"""
Data importer for training data from Data.gov and other sources
Converts JSON data into TrainingExample format and stores in MongoDB
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import BulkWriteError
import aiofiles
from textblob import TextBlob

from .data_schema import (
    TrainingExample, 
    DatasetStats,
    TrainingExampleRequest
)

logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """Analyze and score training data quality"""
    
    @staticmethod
    def calculate_quality_score(prompt: str, completion: str) -> float:
        """Calculate quality score based on various metrics"""
        score = 0.0
        
        # Length checks (25% of score)
        prompt_len = len(prompt.split())
        completion_len = len(completion.split())
        
        if 5 <= prompt_len <= 50:  # Good prompt length
            score += 0.1
        if 50 <= completion_len <= 1000:  # Good completion length
            score += 0.15
        
        # Language quality (25% of score)
        try:
            completion_blob = TextBlob(completion)
            
            # Check for proper sentence structure
            sentences = completion_blob.sentences
            if len(sentences) >= 2:  # Multiple sentences
                score += 0.1
            
            # Basic grammar check (simplified)
            if len(completion_blob.words) > len(completion.split()):  # Proper word detection
                score += 0.05
            
            # Check for coherence (basic punctuation)
            if completion.count('.') >= 1 and completion.count(',') >= 1:
                score += 0.1
                
        except Exception as e:
            logger.warning(f"TextBlob analysis failed: {e}")
        
        # Content structure (25% of score)
        # Check for proper formatting
        if completion.strip().endswith(('.', '!', '?')):  # Proper ending
            score += 0.1
        
        # Check for paragraph structure
        paragraphs = completion.split('\n\n')
        if len(paragraphs) >= 2:
            score += 0.1
        
        # Check for balanced content
        if not completion.startswith(prompt.strip()):  # Not just repeating prompt
            score += 0.05
        
        # Uniqueness check (25% of score)
        # Check for repetitive content
        words = completion.lower().split()
        unique_words = set(words)
        if len(unique_words) / len(words) > 0.6:  # Good vocabulary diversity
            score += 0.15
        
        # Check for common filler words (reduce score if too many)
        filler_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filler_ratio = sum(1 for word in words if word in filler_words) / len(words)
        if filler_ratio < 0.3:  # Not too many filler words
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """Calculate Flesch Reading Ease score"""
        try:
            blob = TextBlob(text)
            sentences = len(blob.sentences)
            words = len(blob.words)
            syllables = sum(DataQualityAnalyzer._count_syllables(str(word)) for word in blob.words)
            
            if sentences == 0 or words == 0:
                return 0.0
            
            # Flesch Reading Ease formula
            score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            return max(0.0, min(100.0, score))  # Clamp between 0-100
            
        except Exception as e:
            logger.warning(f"Readability calculation failed: {e}")
            return 50.0  # Default moderate score
    
    @staticmethod
    def _count_syllables(word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        
        vowels = 'aeiouy'
        syllable_count = 0
        prev_char = ''
        
        for char in word:
            if char in vowels and prev_char not in vowels:
                syllable_count += 1
            prev_char = char
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)


class TrainingDataImporter:
    """Import and manage training data from various sources"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.training_collection: AsyncIOMotorCollection = db.llm_training_data
        self.datasets_collection: AsyncIOMotorCollection = db.llm_datasets
        self.quality_analyzer = DataQualityAnalyzer()
        
        # Create indexes for efficient querying
        asyncio.create_task(self._create_indexes())
    
    async def _create_indexes(self):
        """Create database indexes for efficient queries"""
        try:
            # Training data indexes
            await self.training_collection.create_index([("domain_id", 1), ("niche_id", 1)])
            await self.training_collection.create_index([("content_type", 1)])
            await self.training_collection.create_index([("quality_score", -1)])
            await self.training_collection.create_index([("created_at", -1)])
            await self.training_collection.create_index([("is_validated", 1)])
            
            # Dataset indexes
            await self.datasets_collection.create_index([("domain_id", 1), ("niche_id", 1)])
            await self.datasets_collection.create_index([("is_ready_for_training", 1)])
            
            # Compound indexes for common queries
            await self.training_collection.create_index([
                ("domain_id", 1), ("niche_id", 1), ("quality_score", -1)
            ])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def import_from_json_file(
        self, 
        file_path: str, 
        domain_id: str, 
        domain_name: str,
        niche_id: Optional[str] = None,
        niche_name: Optional[str] = None,
        content_type: str = "data_gov",
        source_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Import training data from JSON file
        
        Args:
            file_path: Path to JSON file
            domain_id: Target domain ID
            domain_name: Domain display name
            niche_id: Optional niche ID
            niche_name: Optional niche display name
            content_type: Type of content source
            source_info: Additional source metadata
            
        Returns:
            Tuple of (imported_count, skipped_count, error_messages)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Starting import from {file_path}")
        
        try:
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of training examples")
            
            return await self._process_json_data(
                data, domain_id, domain_name, niche_id, niche_name, 
                content_type, str(file_path), source_info
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error importing from {file_path}: {e}")
            raise
    
    async def import_from_directory(
        self,
        directory_path: str,
        domain_id: str,
        domain_name: str,
        niche_id: Optional[str] = None,
        niche_name: Optional[str] = None,
        content_type: str = "data_gov",
        file_pattern: str = "*.json"
    ) -> Dict[str, Tuple[int, int, List[str]]]:
        """
        Import training data from all JSON files in a directory
        
        Returns:
            Dictionary mapping file names to import results
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        results = {}
        json_files = list(directory.glob(file_pattern))
        
        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return results
        
        logger.info(f"Found {len(json_files)} JSON files to import")
        
        for json_file in json_files:
            try:
                result = await self.import_from_json_file(
                    str(json_file), domain_id, domain_name, 
                    niche_id, niche_name, content_type
                )
                results[json_file.name] = result
                logger.info(f"Imported {result[0]} examples from {json_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to import {json_file.name}: {e}")
                results[json_file.name] = (0, 0, [str(e)])
        
        return results
    
    async def _process_json_data(
        self,
        data: List[Dict[str, Any]],
        domain_id: str,
        domain_name: str,
        niche_id: Optional[str],
        niche_name: Optional[str],
        content_type: str,
        source_file: str,
        source_info: Optional[Dict[str, Any]]
    ) -> Tuple[int, int, List[str]]:
        """Process and import JSON data"""
        
        imported_count = 0
        skipped_count = 0
        error_messages = []
        
        # Process in batches for better performance
        batch_size = 100
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_examples = []
            
            for item in batch:
                try:
                    example = await self._create_training_example(
                        item, domain_id, domain_name, niche_id, niche_name,
                        content_type, source_file, source_info
                    )
                    
                    if example:
                        batch_examples.append(example.dict(by_alias=True))
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    error_messages.append(f"Error processing item: {e}")
                    skipped_count += 1
            
            # Insert batch to MongoDB
            if batch_examples:
                try:
                    result = await self.training_collection.insert_many(
                        batch_examples, ordered=False
                    )
                    imported_count += len(result.inserted_ids)
                    
                except BulkWriteError as e:
                    # Handle duplicates and other write errors
                    imported_count += e.details.get('nInserted', 0)
                    for error in e.details.get('writeErrors', []):
                        if error.get('code') != 11000:  # Not a duplicate key error
                            error_messages.append(f"Write error: {error.get('errmsg', 'Unknown error')}")
        
        # Update dataset statistics
        await self._update_dataset_stats(domain_id, niche_id)
        
        logger.info(f"Import completed: {imported_count} imported, {skipped_count} skipped")
        return imported_count, skipped_count, error_messages
    
    async def _create_training_example(
        self,
        item: Dict[str, Any],
        domain_id: str,
        domain_name: str,
        niche_id: Optional[str],
        niche_name: Optional[str],
        content_type: str,
        source_file: str,
        source_info: Optional[Dict[str, Any]]
    ) -> Optional[TrainingExample]:
        """Create a TrainingExample from JSON item"""
        
        # Extract required fields
        prompt = item.get('prompt', '').strip()
        completion = item.get('completion', '').strip()
        
        if not prompt or not completion:
            logger.warning("Skipping item with missing prompt or completion")
            return None
        
        # Validate minimum lengths
        if len(prompt) < 10 or len(completion) < 50:
            logger.warning("Skipping item with content too short")
            return None
        
        # Calculate quality metrics
        quality_score = item.get('quality_score')
        if quality_score is None:
            quality_score = self.quality_analyzer.calculate_quality_score(prompt, completion)
        
        readability_score = self.quality_analyzer.calculate_readability_score(completion)
        word_count = len(completion.split())
        
        # Extract metadata
        metadata = item.get('metadata', {})
        if source_info:
            metadata.update(source_info)
        
        # Create unique ID based on content using SHA256 (more secure than MD5)
        content_text = f"{prompt}{completion}"
        content_hash = hashlib.sha256(content_text.encode()).hexdigest()[:16]  # Use first 16 chars
        
        return TrainingExample(
            prompt=prompt,
            completion=completion,
            domain_id=domain_id,
            domain_name=domain_name,
            niche_id=niche_id,
            niche_name=niche_name,
            content_type=content_type,
            chapter_type=item.get('chapter_type'),
            target_audience=item.get('target_audience'),
            language=item.get('language', 'en'),
            quality_score=quality_score,
            word_count=word_count,
            readability_score=readability_score,
            training_weight=item.get('training_weight', 1.0),
            is_validated=item.get('is_validated', False),
            validation_notes=item.get('validation_notes'),
            source_file=source_file,
            source_url=item.get('source_url'),
            data_gov_dataset=item.get('data_gov_dataset'),
            tags=item.get('tags', []),
            metadata=metadata
        )
    
    async def _update_dataset_stats(self, domain_id: str, niche_id: Optional[str] = None):
        """Update dataset statistics after import"""
        
        # Build query filter
        filter_query = {"domain_id": domain_id}
        if niche_id:
            filter_query["niche_id"] = niche_id
        
        # Calculate statistics
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": None,
                "total_examples": {"$sum": 1},
                "validated_examples": {"$sum": {"$cond": ["$is_validated", 1, 0]}},
                "avg_quality_score": {"$avg": "$quality_score"},
                "total_word_count": {"$sum": "$word_count"},
                "content_types": {"$push": "$content_type"},
                "chapter_types": {"$push": "$chapter_type"},
                "target_audiences": {"$push": "$target_audience"}
            }}
        ]
        
        result = await self.training_collection.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            
            # Update or create dataset record
            dataset_filter = {"domain_id": domain_id}
            if niche_id:
                dataset_filter["niche_id"] = niche_id
            
            dataset_update = {
                "$set": {
                    "total_examples": stats["total_examples"],
                    "validated_examples": stats["validated_examples"],
                    "avg_quality_score": stats["avg_quality_score"],
                    "total_word_count": stats["total_word_count"],
                    "updated_at": datetime.utcnow(),
                    "is_ready_for_training": stats["total_examples"] >= 50  # Minimum threshold
                }
            }
            
            await self.datasets_collection.update_one(
                dataset_filter, dataset_update, upsert=True
            )
    
    async def get_dataset_stats(
        self, 
        domain_id: str, 
        niche_id: Optional[str] = None
    ) -> Optional[DatasetStats]:
        """Get comprehensive dataset statistics"""
        
        filter_query = {"domain_id": domain_id}
        if niche_id:
            filter_query["niche_id"] = niche_id
        
        # Aggregation pipeline for detailed stats
        pipeline = [
            {"$match": filter_query},
            {"$facet": {
                "overview": [
                    {"$group": {
                        "_id": None,
                        "total_examples": {"$sum": 1},
                        "validated_examples": {"$sum": {"$cond": ["$is_validated", 1, 0]}},
                        "avg_quality_score": {"$avg": "$quality_score"},
                        "total_word_count": {"$sum": "$word_count"},
                        "avg_word_count": {"$avg": "$word_count"}
                    }}
                ],
                "content_types": [
                    {"$group": {"_id": "$content_type", "count": {"$sum": 1}}}
                ],
                "chapter_types": [
                    {"$group": {"_id": "$chapter_type", "count": {"$sum": 1}}}
                ],
                "target_audiences": [
                    {"$group": {"_id": "$target_audience", "count": {"$sum": 1}}}
                ],
                "quality_distribution": [
                    {"$bucket": {
                        "groupBy": "$quality_score",
                        "boundaries": [0, 0.3, 0.6, 0.8, 1.0],
                        "default": "other",
                        "output": {"count": {"$sum": 1}}
                    }}
                ]
            }}
        ]
        
        result = await self.training_collection.aggregate(pipeline).to_list(1)
        
        if not result or not result[0]["overview"]:
            return None
        
        data = result[0]
        overview = data["overview"][0]
        
        # Get domain name from first example
        example = await self.training_collection.find_one(filter_query, {"domain_name": 1, "niche_name": 1})
        
        return DatasetStats(
            domain_id=domain_id,
            domain_name=example.get("domain_name", domain_id) if example else domain_id,
            niche_id=niche_id,
            niche_name=example.get("niche_name", niche_id) if example and niche_id else niche_id,
            total_examples=overview["total_examples"],
            validated_examples=overview["validated_examples"],
            avg_quality_score=overview["avg_quality_score"],
            total_word_count=overview["total_word_count"],
            avg_word_count=overview["avg_word_count"],
            content_types={item["_id"]: item["count"] for item in data["content_types"]},
            chapter_types={item["_id"]: item["count"] for item in data["chapter_types"] if item["_id"]},
            target_audiences={item["_id"]: item["count"] for item in data["target_audiences"] if item["_id"]},
            quality_distribution={
                "Low (0-0.3)": next((item["count"] for item in data["quality_distribution"] if item["_id"] == 0), 0),
                "Medium (0.3-0.6)": next((item["count"] for item in data["quality_distribution"] if item["_id"] == 0.3), 0),
                "High (0.6-0.8)": next((item["count"] for item in data["quality_distribution"] if item["_id"] == 0.6), 0),
                "Excellent (0.8-1.0)": next((item["count"] for item in data["quality_distribution"] if item["_id"] == 0.8), 0)
            }
        )
    
    async def add_single_example(self, example_request: TrainingExampleRequest) -> str:
        """Add a single training example"""
        
        # Calculate quality metrics if not provided
        quality_score = self.quality_analyzer.calculate_quality_score(
            example_request.prompt, example_request.completion
        )
        readability_score = self.quality_analyzer.calculate_readability_score(
            example_request.completion
        )
        word_count = len(example_request.completion.split())
        
        example = TrainingExample(
            prompt=example_request.prompt,
            completion=example_request.completion,
            domain_id=example_request.domain_id,
            domain_name=example_request.domain_name,
            niche_id=example_request.niche_id,
            niche_name=example_request.niche_name,
            content_type=example_request.content_type,
            chapter_type=example_request.chapter_type,
            target_audience=example_request.target_audience,
            quality_score=quality_score,
            word_count=word_count,
            readability_score=readability_score,
            tags=example_request.tags,
            source_file=example_request.source_file,
            metadata=example_request.metadata
        )
        
        result = await self.training_collection.insert_one(example.dict(by_alias=True))
        
        # Update dataset stats
        await self._update_dataset_stats(example_request.domain_id, example_request.niche_id)
        
        return str(result.inserted_id)
    
    async def list_domains(self) -> List[Dict[str, Any]]:
        """List all available domains with training data"""
        
        pipeline = [
            {"$group": {
                "_id": {
                    "domain_id": "$domain_id",
                    "domain_name": "$domain_name"
                },
                "total_examples": {"$sum": 1},
                "niches": {"$addToSet": {"niche_id": "$niche_id", "niche_name": "$niche_name"}},
                "avg_quality": {"$avg": "$quality_score"},
                "last_updated": {"$max": "$updated_at"}
            }},
            {"$sort": {"_id.domain_name": 1}}
        ]
        
        result = await self.training_collection.aggregate(pipeline).to_list(None)
        
        domains = []
        for item in result:
            domains.append({
                "domain_id": item["_id"]["domain_id"],
                "domain_name": item["_id"]["domain_name"],
                "total_examples": item["total_examples"],
                "niches": [n for n in item["niches"] if n["niche_id"]],
                "avg_quality": item["avg_quality"],
                "last_updated": item["last_updated"]
            })
        
        return domains
    
    async def clear_training_data(
        self, 
        domain_id: Optional[str] = None, 
        niche_id: Optional[str] = None
    ) -> int:
        """Clear training data with optional filtering"""
        
        filter_query = {}
        if domain_id:
            filter_query["domain_id"] = domain_id
        if niche_id:
            filter_query["niche_id"] = niche_id
        
        result = await self.training_collection.delete_many(filter_query)
        
        # Update dataset stats if specific domain/niche was cleared
        if domain_id:
            await self._update_dataset_stats(domain_id, niche_id)
        
        return result.deleted_count


# Utility functions for data preparation
def validate_json_format(data: List[Dict[str, Any]]) -> List[str]:
    """Validate JSON data format and return error messages"""
    errors = []
    
    required_fields = ['prompt', 'completion']
    
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item {i}: Must be a dictionary")
            continue
        
        for field in required_fields:
            if field not in item:
                errors.append(f"Item {i}: Missing required field '{field}'")
            elif not isinstance(item[field], str) or not item[field].strip():
                errors.append(f"Item {i}: Field '{field}' must be a non-empty string")
        
        # Validate optional fields
        if 'quality_score' in item and not (0 <= item['quality_score'] <= 1):
            errors.append(f"Item {i}: quality_score must be between 0 and 1")
        
        if 'training_weight' in item and not (0 <= item['training_weight'] <= 10):
            errors.append(f"Item {i}: training_weight must be between 0 and 10")
    
    return errors


def create_example_template() -> Dict[str, Any]:
    """Create an example training data template"""
    return {
        "prompt": "Write an introduction chapter about AI machine learning for beginners",
        "completion": "Artificial Intelligence and Machine Learning represent a transformative era in technology. At its core, machine learning enables computers to learn and improve from experience without being explicitly programmed for every task. This revolutionary approach has applications spanning from recommendation systems that suggest your next favorite movie to autonomous vehicles navigating complex city streets.\n\nFor beginners, it's helpful to think of machine learning as teaching computers to recognize patterns in data, much like how humans learn to recognize faces or predict weather patterns based on cloud formations. The field encompasses various techniques including supervised learning, where we provide examples with correct answers, and unsupervised learning, where algorithms discover hidden patterns in data without guidance.\n\nThis foundational understanding opens doors to exploring more advanced concepts like neural networks, deep learning, and the ethical considerations that guide responsible AI development.",
        "metadata": {
            "quality_score": 0.95,
            "chapter_type": "introduction", 
            "target_audience": "beginner",
            "word_count": 150,
            "tags": ["AI", "machine learning", "introduction", "beginner"]
        }
    }