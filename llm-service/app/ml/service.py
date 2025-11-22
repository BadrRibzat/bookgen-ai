"""
LLM Service - Main training and inference orchestrator
MongoDB integration for production training data management
"""

import logging
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .model import BookGenModel
from .preprocessing import (
    TextPreprocessor, MongoDBTrainingDataManager, 
    ManualDataImporter, TrainingDataGenerator
)
from .pdf_generator import BookPDFGenerator, BookFormatter


class LLMService:
    """Main service for managing LLM training and book generation with MongoDB"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.model = None
        self.preprocessor = TextPreprocessor()
        self.mongodb_manager = MongoDBTrainingDataManager(
            self.config.get('mongodb_url')
        )
        self.data_importer = ManualDataImporter(self.mongodb_manager)
        self.training_generator = TrainingDataGenerator(self.mongodb_manager)
        self.pdf_generator = BookPDFGenerator()
        self.formatter = BookFormatter()
        
        # Paths
        self.model_dir = Path(self.config['model_dir'])
        self.temp_dir = Path(self.config['temp_dir'])
        self.output_dir = Path(self.config['output_dir'])
        
        # Ensure directories exist
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("LLM Service initialized with MongoDB")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        import os
        return {
            'model_dir': '/app/models',
            'temp_dir': '/app/temp',
            'output_dir': '/app/output',
            'mongodb_url': os.getenv('MONGODB_URL', 'mongodb://localhost:27017'),
            'max_length': 512,
            'batch_size': 4,
            'learning_rate': 2e-5,
            'num_epochs': 3,
            'lora_r': 16,
            'lora_alpha': 32,
            'lora_dropout': 0.1,
            'device': 'cpu',  # CPU-only for now
            'save_steps': 500,
            'logging_steps': 100
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def initialize_model(self) -> bool:
        """Initialize the BookGen model and MongoDB"""
        try:
            # Initialize MongoDB
            await self.mongodb_manager.initialize()
            
            # Initialize model
            model_path = "models/final_model"
            self.model = BookGenModel(
                model_name=model_path,
                lora_r=self.config['lora_r'],
                lora_alpha=self.config['lora_alpha'], 
                lora_dropout=self.config['lora_dropout']
            )
            
            # Load existing model if available
            model_path = self.model_dir / "bookgen_model"
            if model_path.exists():
                success = await self.model.load_model(str(model_path))
                if success:
                    self.logger.info("Loaded existing model")
                else:
                    self.logger.warning("Failed to load existing model, using fresh model")
            
            self.logger.info("Model and MongoDB initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing model: {e}")
            return False
    
    async def import_training_data(self, file_path: str, domain: str, 
                                 niche: str = None, content_type: str = "manual") -> bool:
        """Import manually collected training data"""
        try:
            self.logger.info(f"Importing training data from: {file_path}")
            
            success = await self.data_importer.import_from_file(
                file_path, domain, niche, content_type
            )
            
            if success:
                self.logger.info(f"Successfully imported training data for {domain}/{niche}")
                return True
            else:
                self.logger.error("Failed to import training data")
                return False
            
        except Exception as e:
            self.logger.error(f"Error importing training data: {e}")
            return False
    
    async def import_training_directory(self, directory_path: str, domain: str, 
                                      niche: str = None) -> bool:
        """Import all training data files from a directory"""
        try:
            self.logger.info(f"Importing training data from directory: {directory_path}")
            
            success = await self.data_importer.import_from_directory(
                directory_path, domain, niche
            )
            
            if success:
                self.logger.info(f"Successfully imported training data from directory")
                return True
            else:
                self.logger.error("Failed to import training data from directory")
                return False
            
        except Exception as e:
            self.logger.error(f"Error importing training directory: {e}")
            return False
    
    async def prepare_training_data(self, domain: str, niche: str = None) -> bool:
        """Prepare training data from MongoDB for model training"""
        try:
            self.logger.info("Preparing training data from MongoDB")
            
            training_data = await self.training_generator.prepare_training_dataset(domain, niche)
            
            if not training_data:
                self.logger.error("No training data available in MongoDB")
                return False
            
            # Save to temporary file for model training
            training_file = self.temp_dir / f"training_data_{domain}_{niche or 'all'}.json"
            with open(training_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Prepared {len(training_data)} training examples")
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return False
    
    async def train_model(self, domain: str, niche: str = None) -> bool:
        """Train the model with prepared data from MongoDB"""
        try:
            if not self.model:
                await self.initialize_model()
            
            # Prepare training data
            success = await self.prepare_training_data(domain, niche)
            if not success:
                return False
            
            # Find the training data file
            training_file = self.temp_dir / f"training_data_{domain}_{niche or 'all'}.json"
            
            if not training_file.exists():
                self.logger.error(f"Training data file not found: {training_file}")
                return False
            
            self.logger.info("Starting model training")
            
            # Load training data
            with open(training_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # Train model
            success = await self.model.train(
                training_data=training_data,
                output_dir=str(self.model_dir / "bookgen_model"),
                num_epochs=self.config['num_epochs'],
                batch_size=self.config['batch_size'],
                learning_rate=self.config['learning_rate']
            )
            
            if success:
                self.logger.info("Model training completed successfully")
                # Clean up temporary training file
                training_file.unlink(missing_ok=True)
                return True
            else:
                self.logger.error("Model training failed")
                return False
            
        except Exception as e:
            self.logger.error(f"Error during training: {e}")
            return False
    
    async def generate_book(self, 
                          domain: str, 
                          niche: str, 
                          purpose: str,
                          target_length: int = 5000,
                          output_format: str = 'pdf') -> Optional[str]:
        """Generate a complete book"""
        try:
            if not self.model:
                await self.initialize_model()
            
            self.logger.info(f"Generating book for {domain}/{niche}/{purpose}")
            
            # Create generation prompt
            prompt = f"""
            Domain: {domain}
            Niche: {niche}
            Purpose: {purpose}
            
            Generate a comprehensive book covering the essential aspects of {niche} within the {domain} field.
            The book should be suitable for {purpose} and provide practical, actionable insights.
            
            Book Content:
            """
            
            # Generate content
            generated_content = await self.model.generate_content(
                prompt=prompt,
                max_length=target_length,
                temperature=0.7,
                top_p=0.9
            )
            
            if not generated_content:
                self.logger.error("Failed to generate content")
                return None
            
            # Format content into book structure
            book_data = self.formatter.format_generated_content(
                generated_content, domain, niche
            )
            
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{domain}_{niche}_{purpose}_{timestamp}".replace(' ', '_').lower()
            
            # Generate output based on format
            if output_format.lower() == 'pdf':
                output_path = self.output_dir / f"{base_filename}.pdf"
                success = self.pdf_generator.generate_book_pdf(book_data, str(output_path))
                
                if success:
                    self.logger.info(f"Book PDF generated: {output_path}")
                    return str(output_path)
                else:
                    self.logger.error("Failed to generate PDF")
                    return None
            
            elif output_format.lower() == 'json':
                output_path = self.output_dir / f"{base_filename}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Book JSON generated: {output_path}")
                return str(output_path)
            
            else:
                self.logger.error(f"Unsupported output format: {output_format}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error generating book: {e}")
            return None
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and MongoDB statistics"""
        try:
            # Get MongoDB stats
            training_stats = await self.mongodb_manager.get_training_stats()
            
            status = {
                'initialized': self.model is not None,
                'model_exists': (self.model_dir / "bookgen_model").exists(),
                'mongodb_connected': self.mongodb_manager.training_collection is not None,
                'training_examples': training_stats.get('total_examples', 0),
                'available_domains': [
                    f"{item['_id']['domain']}/{item['_id']['niche'] or 'general'}" 
                    for item in training_stats.get('domain_breakdown', [])
                ],
                'model_size': 0,
                'last_training': None,
                'mongodb_stats': training_stats
            }
            
            # Check model size
            model_path = self.model_dir / "bookgen_model"
            if model_path.exists():
                status['model_size'] = sum(
                    f.stat().st_size for f in model_path.rglob('*') if f.is_file()
                )
                status['last_training'] = datetime.fromtimestamp(
                    model_path.stat().st_mtime
                ).isoformat()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return {'error': str(e)}
    
    async def clear_training_data(self, domain: str = None, niche: str = None) -> bool:
        """Clear training data from MongoDB"""
        try:
            success = await self.mongodb_manager.clear_training_data(domain, niche)
            if success:
                self.logger.info(f"Cleared training data for {domain}/{niche}")
            return success
        except Exception as e:
            self.logger.error(f"Error clearing training data: {e}")
            return False
    
    async def list_training_domains(self) -> List[str]:
        """List available training domains"""
        try:
            stats = await self.mongodb_manager.get_training_stats()
            domains = [
                f"{item['_id']['domain']}/{item['_id']['niche'] or 'general'}" 
                for item in stats.get('domain_breakdown', [])
            ]
            return domains
        except Exception as e:
            self.logger.error(f"Error listing domains: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.model:
                # Any model cleanup if needed
                pass
            
            # Clean up temporary files
            for temp_file in self.temp_dir.glob("*.json"):
                temp_file.unlink(missing_ok=True)
            
            self.logger.info("LLM Service cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Async context manager for service lifecycle
class LLMServiceManager:
    """Context manager for LLM Service lifecycle"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config
        self.service = None
    
    async def __aenter__(self):
        self.service = LLMService(self.config)
        await self.service.initialize_model()
        return self.service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.service:
            await self.service.cleanup()


# CLI interface for testing
async def main():
    """Main function for CLI testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BookGen LLM Service with MongoDB')
    parser.add_argument('command', choices=['status', 'import', 'train', 'generate', 'clear'])
    parser.add_argument('--file', help='File path for import command')
    parser.add_argument('--directory', help='Directory path for import command')
    parser.add_argument('--domain', default='artificial intelligence')
    parser.add_argument('--niche', default='machine learning')
    parser.add_argument('--purpose', default='educational guide')
    parser.add_argument('--content-type', default='manual')
    
    args = parser.parse_args()
    
    async with LLMServiceManager() as service:
        if args.command == 'status':
            status = await service.get_model_status()
            print(json.dumps(status, indent=2))
        
        elif args.command == 'import':
            if args.file:
                success = await service.import_training_data(
                    args.file, args.domain, args.niche, args.content_type
                )
            elif args.directory:
                success = await service.import_training_directory(
                    args.directory, args.domain, args.niche
                )
            else:
                print("Please specify --file or --directory for import")
                return
            
            print(f"Data import {'succeeded' if success else 'failed'}")
        
        elif args.command == 'train':
            success = await service.train_model(args.domain, args.niche)
            print(f"Training {'succeeded' if success else 'failed'}")
        
        elif args.command == 'generate':
            output_path = await service.generate_book(
                args.domain, args.niche, args.purpose
            )
            if output_path:
                print(f"Book generated: {output_path}")
            else:
                print("Book generation failed")
        
        elif args.command == 'clear':
            success = await service.clear_training_data(args.domain, args.niche)
            print(f"Data clearing {'succeeded' if success else 'failed'}")


if __name__ == "__main__":
    asyncio.run(main())
