"""
Data preprocessing and text processing utilities for custom LLM training
Manual data import and MongoDB integration for production training data
"""

import re
import nltk
import spacy
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import json
from datetime import datetime
import os

# Download required NLTK data (run once)
def download_nltk_data():
    """Download necessary NLTK data"""
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except Exception as e:
        logging.error(f"Error downloading NLTK data: {e}")


class TextPreprocessor:
    """Advanced text preprocessing for LLM training data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Download NLTK data
        download_nltk_data()
        
        # Initialize spaCy (will need to install model: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except IOError:
            self.logger.warning("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Fix common issues
        text = re.sub(r'\.{2,}', '.', text)  # Multiple periods
        text = re.sub(r'\s+([\.,:;!?])', r'\1', text)  # Space before punctuation
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text using NLTK"""
        clean_text = self.clean_text(text)
        
        try:
            sentences = nltk.sent_tokenize(clean_text)
            # Filter out very short sentences
            return [s.strip() for s in sentences if len(s.strip()) > 10]
        except Exception as e:
            self.logger.error(f"Error extracting sentences: {e}")
            return [clean_text]
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            
            # Extract entities and important terms
            key_terms = []
            
            # Named entities
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'GPE', 'PRODUCT', 'EVENT']:
                    key_terms.append(ent.text)
            
            # Important nouns and noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 3:
                    key_terms.append(chunk.text)
            
            return list(set(key_terms))
        
        except Exception as e:
            self.logger.error(f"Error extracting key terms: {e}")
            return []
    
    def create_training_segments(self, text: str, max_length: int = 512) -> List[str]:
        """Create training segments of appropriate length"""
        sentences = self.extract_sentences(text)
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed max length
            if len(current_segment) + len(sentence) + 1 <= max_length:
                current_segment += " " + sentence if current_segment else sentence
            else:
                # Save current segment and start new one
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        # Add final segment
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments


class MongoDBTrainingDataManager:
    """Manage training data in MongoDB Atlas for production use"""
    
    def __init__(self, connection_string: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Get MongoDB connection from environment or parameter
        self.connection_string = connection_string or os.getenv('MONGODB_URL')
        if not self.connection_string:
            raise ValueError("MongoDB connection string required. Set MONGODB_URL environment variable.")
        
        self.client = None
        self.async_client = None
        self.db = None
        self.training_collection = None
        
    async def initialize(self):
        """Initialize MongoDB connections"""
        try:
            # Async client for async operations
            self.async_client = AsyncIOMotorClient(self.connection_string)
            
            # Sync client for sync operations
            self.client = MongoClient(self.connection_string)
            
            # Database and collection
            self.db = self.async_client.bookgen_ai
            self.training_collection = self.db.training_data
            
            # Create indexes for better performance
            await self.training_collection.create_index([("domain", 1), ("niche", 1)])
            await self.training_collection.create_index([("created_at", -1)])
            await self.training_collection.create_index([("content_type", 1)])
            
            self.logger.info("MongoDB training data manager initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing MongoDB: {e}")
            raise
    
    async def store_training_data(self, training_data: List[Dict[str, Any]], 
                                domain: str, niche: str = None) -> bool:
        """Store training data in MongoDB"""
        try:
            if not self.training_collection:
                await self.initialize()
            
            # Add metadata to each training example
            timestamp = datetime.utcnow()
            processed_data = []
            
            for item in training_data:
                item_with_meta = {
                    **item,
                    'domain': domain,
                    'niche': niche,
                    'created_at': timestamp,
                    'status': 'active',
                    'word_count': len(item.get('content', '').split()) if item.get('content') else 0
                }
                processed_data.append(item_with_meta)
            
            # Insert data
            result = await self.training_collection.insert_many(processed_data)
            
            self.logger.info(f"Stored {len(result.inserted_ids)} training examples for {domain}/{niche}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing training data: {e}")
            return False
    
    async def get_training_data(self, domain: str = None, niche: str = None, 
                              limit: int = None) -> List[Dict[str, Any]]:
        """Retrieve training data from MongoDB"""
        try:
            if not self.training_collection:
                await self.initialize()
            
            # Build query
            query = {'status': 'active'}
            if domain:
                query['domain'] = domain
            if niche:
                query['niche'] = niche
            
            # Execute query
            cursor = self.training_collection.find(query).sort('created_at', -1)
            if limit:
                cursor = cursor.limit(limit)
            
            training_data = await cursor.to_list(length=None)
            
            self.logger.info(f"Retrieved {len(training_data)} training examples")
            return training_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving training data: {e}")
            return []
    
    async def get_training_stats(self) -> Dict[str, Any]:
        """Get training data statistics"""
        try:
            if not self.training_collection:
                await self.initialize()
            
            # Aggregate statistics
            pipeline = [
                {'$match': {'status': 'active'}},
                {'$group': {
                    '_id': {'domain': '$domain', 'niche': '$niche'},
                    'count': {'$sum': 1},
                    'total_words': {'$sum': '$word_count'},
                    'avg_words': {'$avg': '$word_count'}
                }},
                {'$sort': {'count': -1}}
            ]
            
            stats_cursor = self.training_collection.aggregate(pipeline)
            domain_stats = await stats_cursor.to_list(length=None)
            
            total_examples = await self.training_collection.count_documents({'status': 'active'})
            
            return {
                'total_examples': total_examples,
                'domain_breakdown': domain_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting training stats: {e}")
            return {}
    
    async def clear_training_data(self, domain: str = None, niche: str = None) -> bool:
        """Clear training data (mark as inactive)"""
        try:
            if not self.training_collection:
                await self.initialize()
            
            # Build query
            query = {'status': 'active'}
            if domain:
                query['domain'] = domain
            if niche:
                query['niche'] = niche
            
            # Mark as inactive instead of deleting
            result = await self.training_collection.update_many(
                query, 
                {'$set': {'status': 'inactive', 'deleted_at': datetime.utcnow()}}
            )
            
            self.logger.info(f"Marked {result.modified_count} training examples as inactive")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing training data: {e}")
            return False


class ManualDataImporter:
    """Import manually collected training data into the system"""
    
    def __init__(self, mongodb_manager: MongoDBTrainingDataManager):
        self.logger = logging.getLogger(__name__)
        self.preprocessor = TextPreprocessor()
        self.mongodb_manager = mongodb_manager
    
    async def import_from_file(self, file_path: str, domain: str, niche: str = None,
                             content_type: str = "manual") -> bool:
        """Import training data from various file formats"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False
            
            # Process based on file type
            if file_path.suffix.lower() == '.json':
                training_data = await self._process_json_file(file_path, domain, niche, content_type)
            elif file_path.suffix.lower() == '.csv':
                training_data = await self._process_csv_file(file_path, domain, niche, content_type)
            elif file_path.suffix.lower() == '.txt':
                training_data = await self._process_text_file(file_path, domain, niche, content_type)
            else:
                self.logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            # Store in MongoDB
            if training_data:
                success = await self.mongodb_manager.store_training_data(training_data, domain, niche)
                return success
            else:
                self.logger.warning("No training data extracted from file")
                return False
            
        except Exception as e:
            self.logger.error(f"Error importing data from file: {e}")
            return False
    
    async def _process_json_file(self, file_path: Path, domain: str, niche: str, 
                               content_type: str) -> List[Dict[str, Any]]:
        """Process JSON file containing training data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        training_examples = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'content' in item:
                    training_examples.append({
                        'content': item['content'],
                        'source': item.get('source', file_path.name),
                        'content_type': content_type,
                        'metadata': item.get('metadata', {})
                    })
                elif isinstance(item, str):
                    segments = self.preprocessor.create_training_segments(item)
                    for segment in segments:
                        training_examples.append({
                            'content': segment,
                            'source': file_path.name,
                            'content_type': content_type
                        })
        
        return training_examples
    
    async def _process_csv_file(self, file_path: Path, domain: str, niche: str,
                              content_type: str) -> List[Dict[str, Any]]:
        """Process CSV file containing training data"""
        df = pd.read_csv(file_path)
        training_examples = []
        
        # Look for common column names
        content_column = None
        for col in ['content', 'text', 'description', 'body', 'message']:
            if col in df.columns:
                content_column = col
                break
        
        if not content_column:
            self.logger.error("No recognizable content column found in CSV")
            return []
        
        for _, row in df.iterrows():
            content = str(row[content_column])
            if len(content.strip()) > 50:  # Minimum content length
                segments = self.preprocessor.create_training_segments(content)
                for segment in segments:
                    training_examples.append({
                        'content': segment,
                        'source': file_path.name,
                        'content_type': content_type,
                        'metadata': {col: str(row[col]) for col in df.columns if col != content_column}
                    })
        
        return training_examples
    
    async def _process_text_file(self, file_path: Path, domain: str, niche: str,
                               content_type: str) -> List[Dict[str, Any]]:
        """Process plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        segments = self.preprocessor.create_training_segments(content)
        training_examples = []
        
        for segment in segments:
            training_examples.append({
                'content': segment,
                'source': file_path.name,
                'content_type': content_type
            })
        
        return training_examples
    
    async def import_from_directory(self, directory_path: str, domain: str, 
                                  niche: str = None) -> bool:
        """Import all supported files from a directory"""
        try:
            directory = Path(directory_path)
            if not directory.exists():
                self.logger.error(f"Directory not found: {directory}")
                return False
            
            success_count = 0
            total_files = 0
            
            # Process all supported files
            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.json', '.csv', '.txt']:
                    total_files += 1
                    success = await self.import_from_file(str(file_path), domain, niche)
                    if success:
                        success_count += 1
            
            self.logger.info(f"Successfully imported {success_count}/{total_files} files")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error importing from directory: {e}")
            return False


class TrainingDataGenerator:
    """Generate training data for domain-specific LLM fine-tuning"""
    
    def __init__(self, mongodb_manager: MongoDBTrainingDataManager):
        self.logger = logging.getLogger(__name__)
        self.preprocessor = TextPreprocessor()
        self.mongodb_manager = mongodb_manager
    
    async def prepare_training_dataset(self, domain: str, niche: str = None) -> List[Dict[str, Any]]:
        """Prepare training dataset from MongoDB for model training"""
        try:
            # Get training data from MongoDB
            raw_data = await self.mongodb_manager.get_training_data(domain, niche)
            
            if not raw_data:
                self.logger.warning(f"No training data found for {domain}/{niche}")
                return []
            
            # Format for training
            training_examples = []
            for item in raw_data:
                content = item.get('content', '')
                if len(content.strip()) < 50:
                    continue
                
                # Create instruction-following format
                training_example = {
                    'instruction': f"Generate informative content about {domain}" + 
                                 (f" focusing on {niche}" if niche else ""),
                    'input': self._create_context_prompt(item, domain, niche),
                    'output': content,
                    'domain': domain,
                    'niche': niche,
                    'source': item.get('source', 'Unknown'),
                    'metadata': item.get('metadata', {})
                }
                
                training_examples.append(training_example)
            
            self.logger.info(f"Prepared {len(training_examples)} training examples for {domain}/{niche}")
            return training_examples
            
        except Exception as e:
            self.logger.error(f"Error preparing training dataset: {e}")
            return []
    
    def _create_context_prompt(self, item: Dict[str, Any], domain: str, niche: str = None) -> str:
        """Create a context prompt for training"""
        content_type = item.get('content_type', 'general')
        
        prompt = f"Write informative content about {domain}"
        if niche:
            prompt += f" specifically focusing on {niche}"
        prompt += f". The content should be educational, well-structured, and based on {content_type} information."
        
        return prompt

import re
import nltk
import spacy
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
import logging

# Download required NLTK data (run once)
def download_nltk_data():
    """Download necessary NLTK data"""
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except Exception as e:
        logging.warning(f"Could not download NLTK data: {e}")

class TextPreprocessor:
    """Advanced text preprocessing for domain-specific content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Try to load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        else:
            # Fallback to NLTK
            from nltk.tokenize import sent_tokenize
            return [sent.strip() for sent in sent_tokenize(text) if len(sent.strip()) > 10]
    
    def preprocess_domain_data(self, raw_text: str, domain: str, niche: str) -> Dict[str, Any]:
        """Preprocess text data for specific domain and niche"""
        
        # Clean the text
        clean_text = self.clean_text(raw_text)
        
        # Extract sentences
        sentences = self.extract_sentences(clean_text)
        
        # Extract metadata if using spaCy
        entities = []
        if self.nlp and clean_text:
            doc = self.nlp(clean_text)
            entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        
        return {
            "raw_text": raw_text,
            "clean_text": clean_text,
            "sentences": sentences,
            "sentence_count": len(sentences),
            "word_count": len(clean_text.split()),
            "domain": domain,
            "niche": niche,
            "entities": entities,
            "metadata": {
                "processed_at": pd.Timestamp.now().isoformat(),
                "char_count": len(clean_text)
            }
        }

class DataGovProcessor:
    """Processor for Data.gov datasets specific to our domains"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.preprocessor = TextPreprocessor()
    
    def process_dataset(self, dataset_path: Path, domain: str, niche: str) -> List[Dict[str, Any]]:
        """Process a Data.gov dataset for training"""
        
        processed_data = []
        
        try:
            # Determine file type and read accordingly
            if dataset_path.suffix.lower() == '.csv':
                df = pd.read_csv(dataset_path)
            elif dataset_path.suffix.lower() in ['.json', '.jsonl']:
                df = pd.read_json(dataset_path, lines=dataset_path.suffix == '.jsonl')
            else:
                self.logger.error(f"Unsupported file format: {dataset_path.suffix}")
                return []
            
            # Process each row
            for _, row in df.iterrows():
                # Try to find text columns
                text_content = self._extract_text_from_row(row)
                
                if text_content:
                    processed_item = self.preprocessor.preprocess_domain_data(
                        text_content, domain, niche
                    )
                    processed_data.append(processed_item)
            
            self.logger.info(f"Processed {len(processed_data)} items from {dataset_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing dataset {dataset_path}: {e}")
        
        return processed_data
    
    def _extract_text_from_row(self, row: pd.Series) -> str:
        """Extract text content from a dataset row"""
        
        # Common text column names to look for
        text_columns = [
            'description', 'content', 'text', 'body', 'summary', 
            'abstract', 'title', 'name', 'notes', 'details'
        ]
        
        text_parts = []
        
        for col in text_columns:
            if col in row.index and pd.notna(row[col]):
                text_parts.append(str(row[col]))
        
        # If no standard text columns found, combine all string columns
        if not text_parts:
            for col, value in row.items():
                if isinstance(value, str) and len(value) > 20:  # Only meaningful text
                    text_parts.append(value)
        
        return " ".join(text_parts)


class TrainingDataGenerator:
    """Generate training data in the format needed for our custom LLM"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_book_generation_examples(self, processed_data: List[Dict], 
                                      domain: str, niche: str) -> List[Dict[str, str]]:
        """Create training examples for book generation"""
        
        training_examples = []
        
        for item in processed_data:
            # Create input-output pairs for training
            sentences = item["sentences"]
            
            if len(sentences) >= 3:
                # Create chapter-like structures
                for i in range(0, len(sentences), 3):
                    chapter_sentences = sentences[i:i+3]
                    
                    if len(chapter_sentences) >= 2:
                        # Input: domain, niche, and first sentence as prompt
                        input_text = f"Domain: {domain}\nNiche: {niche}\nChapter topic: {chapter_sentences[0]}"
                        
                        # Output: the following sentences as content
                        output_text = " ".join(chapter_sentences[1:])
                        
                        training_examples.append({
                            "input": input_text,
                            "output": output_text,
                            "domain": domain,
                            "niche": niche,
                            "metadata": item["metadata"]
                        })
        
        return training_examples
    
    def save_training_data(self, training_examples: List[Dict], output_path: Path):
        """Save training data in JSON format"""
        
        try:
            import json
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(training_examples, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(training_examples)} training examples to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving training data: {e}")


# Initialize the module
if __name__ == "__main__":
    download_nltk_data()