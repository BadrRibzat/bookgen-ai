"""
LLM Training Service
Handles model training, fine-tuning, and inference using Hugging Face Transformers
"""

import json
import logging
import os
import asyncio
import torch
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import psutil
import time

from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    pipeline
)
from datasets import Dataset
import numpy as np
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from .data_schema import (
    TrainingJob, 
    ModelArtifact, 
    TrainingJobRequest,
    TextGenerationRequest,
    TextGenerationResponse
)
from .data_importer import TrainingDataImporter

logger = logging.getLogger(__name__)

DOMAIN_DISPLAY_NAMES: Dict[str, str] = {
    "ai_ml": "AI & Machine Learning",
    "automation": "Automation",
    "healthtech": "HealthTech",
    "cybersecurity": "Cybersecurity",
    "creator_economy": "Creator Economy",
    "web3": "Web3",
    "ecommerce": "E-commerce",
    "data_analytics": "Data Analytics",
    "gaming": "Gaming",
    "kids_parenting": "Kids & Parenting",
    "nutrition": "Nutrition",
    "recipes": "Recipes",
}


class ModelTrainingMetrics:
    """Track and calculate training metrics"""
    
    def __init__(self):
        self.start_time = None
        self.epoch_times = []
        self.train_losses = []
        self.eval_losses = []
        self.learning_rates = []
        self.memory_usage = []
        
    def start_training(self):
        """Mark training start"""
        self.start_time = time.time()
        
    def log_epoch(self, epoch: int, train_loss: float, eval_loss: float = None, lr: float = None):
        """Log metrics for an epoch"""
        epoch_time = time.time() - self.start_time if self.start_time else 0
        self.epoch_times.append(epoch_time)
        self.train_losses.append(train_loss)
        
        if eval_loss is not None:
            self.eval_losses.append(eval_loss)
        if lr is not None:
            self.learning_rates.append(lr)
            
        # Log memory usage
        memory_info = psutil.virtual_memory()
        self.memory_usage.append({
            'total_gb': memory_info.total / (1024**3),
            'used_gb': memory_info.used / (1024**3),
            'percent': memory_info.percent
        })
        
    def get_summary(self) -> Dict[str, Any]:
        """Get training summary"""
        if not self.train_losses:
            return {}
            
        total_time = self.epoch_times[-1] if self.epoch_times else 0
        
        return {
            'total_training_time': total_time,
            'avg_epoch_time': np.mean(self.epoch_times) if self.epoch_times else 0,
            'final_train_loss': self.train_losses[-1],
            'best_train_loss': min(self.train_losses),
            'final_eval_loss': self.eval_losses[-1] if self.eval_losses else None,
            'best_eval_loss': min(self.eval_losses) if self.eval_losses else None,
            'loss_improvement': self.train_losses[0] - self.train_losses[-1] if len(self.train_losses) > 1 else 0,
            'peak_memory_gb': max(m['used_gb'] for m in self.memory_usage) if self.memory_usage else 0,
            'avg_memory_percent': np.mean([m['percent'] for m in self.memory_usage]) if self.memory_usage else 0
        }


class CustomTrainer(Trainer):
    """Custom trainer with progress tracking"""
    
    def __init__(self, metrics_tracker: ModelTrainingMetrics, progress_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics_tracker = metrics_tracker
        self.progress_callback = progress_callback
        self.current_epoch = 0
        
    def on_epoch_begin(self, args, state, control, **kwargs):
        """Called at the beginning of each epoch"""
        self.current_epoch = state.epoch
        if self.progress_callback:
            self.progress_callback(
                epoch=self.current_epoch,
                total_epochs=args.num_train_epochs,
                status="training"
            )
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        """Called when logging training metrics"""
        if logs and 'train_loss' in logs:
            eval_loss = logs.get('eval_loss')
            lr = logs.get('learning_rate')
            
            self.metrics_tracker.log_epoch(
                epoch=self.current_epoch,
                train_loss=logs['train_loss'],
                eval_loss=eval_loss,
                lr=lr
            )
            
            if self.progress_callback:
                self.progress_callback(
                    epoch=self.current_epoch,
                    total_epochs=args.num_train_epochs,
                    train_loss=logs['train_loss'],
                    eval_loss=eval_loss,
                    status="training"
                )


class LLMTrainer:
    """Main LLM training service"""
    
    def __init__(self, db: AsyncIOMotorDatabase, models_dir: str = "./models"):
        self.db = db
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Collections
        self.training_jobs_collection: AsyncIOMotorCollection = db.llm_training_jobs
        self.models_collection: AsyncIOMotorCollection = db.llm_models
        self.training_data_collection: AsyncIOMotorCollection = db.llm_training_data
        
        # Training state
        self.current_job: Optional[TrainingJob] = None
        self.is_training = False
        
        # Data importer for dataset preparation
        self.data_importer = TrainingDataImporter(db)
        
        # Device configuration
        self.device = self._configure_device()
        logger.info(f"Using device: {self.device}")

        # Fine-tuned model defaults
        self.default_model_path = Path(
            os.getenv("LLM_MODEL_PATH", self.models_dir / "final_model")
        ).resolve()
        self.default_model_metadata = self._load_default_model_metadata()
        self._default_artifact_cache: Dict[str, ModelArtifact] = {}
        self._model_cache: Dict[str, GPT2LMHeadModel] = {}
        self._tokenizer_cache: Dict[str, GPT2Tokenizer] = {}
        self._background_tasks: List[asyncio.Task] = []
        
    def _configure_device(self) -> str:
        """Configure training device (CPU/CUDA)"""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"CUDA available with {torch.cuda.device_count()} GPU(s)")
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("Using CPU for training")
        
        return device

    def _track_task(self, task: asyncio.Task) -> None:
        """Track background tasks to avoid premature garbage collection."""

        self._background_tasks.append(task)

        def _cleanup(finished: asyncio.Task) -> None:
            if finished in self._background_tasks:
                self._background_tasks.remove(finished)

        task.add_done_callback(_cleanup)
    
    async def start_training_job(
        self, 
        request: TrainingJobRequest,
        progress_callback: Optional[callable] = None
    ) -> str:
        """Start a new training job"""
        
        if self.is_training:
            raise RuntimeError("Another training job is already running")
        
        # Create job record
        job = TrainingJob(
            job_id=f"train_{request.domain_id}_{int(datetime.now(timezone.utc).timestamp())}",
            name=request.job_name or f"Training for {request.domain_id}",
            domain_id=request.domain_id,
            domain_name=await self._get_domain_name(request.domain_id),
            niche_id=request.niche_id,
            niche_name=await self._get_niche_name(request.niche_id) if request.niche_id else None,
            model_name=request.model_name,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
            epochs=request.epochs,
            max_length=request.max_length,
            status="pending"
        )
        
        # Save job to database
        result = await self.training_jobs_collection.insert_one(job.dict(by_alias=True))
        job_id = str(result.inserted_id)
        
        # Start training in background
        self._track_task(asyncio.create_task(self._run_training_job(job, progress_callback)))
        
        return job_id
    
    async def _run_training_job(
        self, 
        job: TrainingJob, 
        progress_callback: Optional[callable] = None
    ):
        """Run the actual training job"""
        
        self.is_training = True
        self.current_job = job
        
        try:
            # Update job status
            await self._update_job_status(job.job_id, "running", "Preparing training data...")
            job.started_at = datetime.now(timezone.utc)
            
            # Prepare training data
            train_dataset, eval_dataset = await self._prepare_training_data(
                job.domain_id, job.niche_id
            )
            
            if not train_dataset:
                raise ValueError("No training data available for this domain/niche")
            
            job.total_examples = len(train_dataset)
            job.training_examples = len(train_dataset)
            job.validation_examples = len(eval_dataset) if eval_dataset else 0
            
            # Initialize model and tokenizer
            await self._update_job_status(job.job_id, "running", "Loading model and tokenizer...")
            
            model, tokenizer = self._load_model_and_tokenizer(job.model_name)
            
            # Prepare datasets for training
            tokenized_train = self._tokenize_dataset(train_dataset, tokenizer, job.max_length)
            tokenized_eval = self._tokenize_dataset(eval_dataset, tokenizer, job.max_length) if eval_dataset else None
            
            # Setup training
            await self._update_job_status(job.job_id, "running", "Starting model training...")
            
            model_path = self.models_dir / f"{job.job_id}_model"
            model_path.mkdir(exist_ok=True)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(model_path),
                num_train_epochs=job.epochs,
                per_device_train_batch_size=job.batch_size,
                per_device_eval_batch_size=job.batch_size,
                learning_rate=job.learning_rate,
                warmup_steps=100,
                logging_steps=50,
                save_steps=500,
                eval_steps=500 if tokenized_eval else None,
                evaluation_strategy="steps" if tokenized_eval else "no",
                save_strategy="steps",
                load_best_model_at_end=True if tokenized_eval else False,
                metric_for_best_model="eval_loss" if tokenized_eval else None,
                greater_is_better=False,
                dataloader_num_workers=0,  # Avoid multiprocessing issues
                fp16=self.device == "cuda",  # Use mixed precision on GPU
                gradient_accumulation_steps=2,
                remove_unused_columns=False,
                report_to=[]  # Disable wandb/tensorboard
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False  # GPT-2 is causal LM, not masked LM
            )
            
            # Progress tracking
            metrics_tracker = ModelTrainingMetrics()
            metrics_tracker.start_training()
            
            def training_progress_callback(epoch, total_epochs, status="training", **kwargs):
                if progress_callback:
                    progress_callback(job.job_id, epoch, total_epochs, status, **kwargs)
                
                # Update job in database
                job.current_epoch = epoch
                job.progress = (epoch / total_epochs) * 100
                self._track_task(asyncio.create_task(self._update_job_in_db(job)))
            
            # Create trainer
            trainer = CustomTrainer(
                metrics_tracker=metrics_tracker,
                progress_callback=training_progress_callback,
                model=model,
                args=training_args,
                train_dataset=tokenized_train,
                eval_dataset=tokenized_eval,
                data_collator=data_collator,
                tokenizer=tokenizer
            )
            
            # Train the model
            trainer.train()
            
            # Save model artifacts
            await self._update_job_status(job.job_id, "running", "Saving model artifacts...")
            
            trainer.save_model()
            tokenizer.save_pretrained(str(model_path))
            
            # Calculate final metrics
            training_summary = metrics_tracker.get_summary()
            
            job.final_loss = training_summary.get('final_train_loss')
            job.validation_loss = training_summary.get('final_eval_loss')
            job.model_path = str(model_path)
            job.tokenizer_path = str(model_path)
            job.completed_at = datetime.now(timezone.utc)
            job.total_duration_seconds = int((job.completed_at - job.started_at).total_seconds())
            job.status = "completed"
            job.progress = 100
            
            # Create model artifact record
            model_artifact = ModelArtifact(
                model_id=f"model_{job.domain_id}_{int(datetime.now(timezone.utc).timestamp())}",
                name=f"Fine-tuned {job.model_name} for {job.domain_name}",
                version="1.0",
                domain_id=job.domain_id,
                domain_name=job.domain_name,
                niche_id=job.niche_id,
                niche_name=job.niche_name,
                base_model=job.model_name,
                model_size="small",
                training_job_id=job.job_id,
                training_examples=job.training_examples,
                training_epochs=job.epochs,
                final_loss=job.final_loss,
                validation_loss=job.validation_loss,
                model_path=job.model_path,
                tokenizer_path=job.tokenizer_path,
                config_path=str(model_path / "config.json"),
                is_active=True,
                is_default=True,  # Mark as default model for this domain
                model_size_mb=self._calculate_model_size(model_path)
            )
            
            await self.models_collection.insert_one(model_artifact.dict(by_alias=True))
            
            await self._update_job_status(
                job.job_id, "completed", 
                f"Training completed successfully in {job.total_duration_seconds}s"
            )
            
            logger.info(f"Training job {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            
            await self._update_job_status(job.job_id, "failed", f"Training failed: {str(e)}")
            
            logger.error(f"Training job {job.job_id} failed: {e}")
            
        finally:
            self.is_training = False
            self.current_job = None
            await self._update_job_in_db(job)
    
    async def _prepare_training_data(
        self, 
        domain_id: str, 
        niche_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, str]], Optional[List[Dict[str, str]]]]:
        """Prepare training and validation datasets"""
        
        # Query training data
        filter_query = {"domain_id": domain_id}
        if niche_id:
            filter_query["niche_id"] = niche_id
        
        # Get all examples sorted by quality score (highest first)
        cursor = self.training_data_collection.find(filter_query).sort("quality_score", -1)
        examples = await cursor.to_list(length=None)
        
        if not examples:
            return [], None
        
        # Convert to training format
        training_data = []
        for example in examples:
            training_data.append({
                "text": f"{example['prompt']}\n\n{example['completion']}"
            })
        
        # Split into train/validation (80/20)
        split_idx = int(len(training_data) * 0.8)
        train_data = training_data[:split_idx]
        eval_data = training_data[split_idx:] if split_idx < len(training_data) else None
        
        logger.info(f"Prepared {len(train_data)} training examples, {len(eval_data) if eval_data else 0} validation examples")
        
        return train_data, eval_data
    
    def _load_model_and_tokenizer(self, model_name: str) -> Tuple[GPT2LMHeadModel, GPT2Tokenizer]:
        """Load model and tokenizer"""
        
        logger.info(f"Loading model: {model_name}")
        
        # Load tokenizer
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        
        # Add padding token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model
        model = GPT2LMHeadModel.from_pretrained(model_name)
        model.to(self.device)
        
        return model, tokenizer
    
    def _tokenize_dataset(
        self, 
        dataset: List[Dict[str, str]], 
        tokenizer: GPT2Tokenizer, 
        max_length: int
    ) -> Dataset:
        """Tokenize dataset for training"""
        
        def tokenize_function(examples):
            # Tokenize the text
            tokens = tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt"
            )
            
            # For causal language modeling, labels are the same as input_ids
            tokens["labels"] = tokens["input_ids"].clone()
            
            return tokens
        
        # Convert to Hugging Face Dataset
        hf_dataset = Dataset.from_list(dataset)
        
        # Apply tokenization
        tokenized_dataset = hf_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=hf_dataset.column_names
        )
        
        return tokenized_dataset
    
    def _calculate_model_size(self, model_path: Path) -> float:
        """Calculate model size in MB"""
        total_size = 0
        for file_path in model_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def _get_domain_name(self, domain_id: str) -> str:
        """Get domain name from database"""
        example = await self.training_data_collection.find_one(
            {"domain_id": domain_id}, {"domain_name": 1}
        )
        return example.get("domain_name", domain_id) if example else domain_id
    
    async def _get_niche_name(self, niche_id: str) -> str:
        """Get niche name from database"""
        example = await self.training_data_collection.find_one(
            {"niche_id": niche_id}, {"niche_name": 1}
        )
        return example.get("niche_name", niche_id) if example else niche_id
    
    async def _update_job_status(self, job_id: str, status: str, message: str):
        """Update job status in database"""
        await self.training_jobs_collection.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now(timezone.utc),
                    "progress": 100 if status == "completed" else None
                },
                "$push": {
                    "metadata.status_history": {
                        "status": status,
                        "message": message,
                        "timestamp": datetime.now(timezone.utc)
                    }
                }
            }
        )
    
    async def _update_job_in_db(self, job: TrainingJob):
        """Update complete job record in database"""
        await self.training_jobs_collection.update_one(
            {"job_id": job.job_id},
            {"$set": job.dict(by_alias=True, exclude={"id"})}
        )
    
    async def get_training_status(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job status"""
        job_data = await self.training_jobs_collection.find_one({"job_id": job_id})
        return TrainingJob(**job_data) if job_data else None
    
    async def list_training_jobs(
        self, 
        domain_id: Optional[str] = None,
        limit: int = 50
    ) -> List[TrainingJob]:
        """List training jobs"""
        filter_query = {}
        if domain_id:
            filter_query["domain_id"] = domain_id
        
        cursor = self.training_jobs_collection.find(filter_query).sort("created_at", -1).limit(limit)
        jobs = await cursor.to_list(length=None)
        
        return [TrainingJob(**job) for job in jobs]
    
    async def get_available_models(
        self, 
        domain_id: Optional[str] = None
    ) -> List[ModelArtifact]:
        """Get available trained models"""
        filter_query = {"is_active": True}
        if domain_id:
            filter_query["domain_id"] = domain_id
        
        cursor = self.models_collection.find(filter_query).sort("created_at", -1)
        models = await cursor.to_list(length=None)
        
        return [ModelArtifact(**model) for model in models]
    
    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """Generate text using trained model"""
        
        # Find the best model for this domain/niche
        model_artifact = await self._find_best_model(request.domain_id, request.niche_id)
        
        if not model_artifact:
            raise ValueError(f"No trained model found for domain: {request.domain_id}")
        
        # Load model and tokenizer
        start_time = time.time()
        
        try:
            cache_key = model_artifact.model_id
            if cache_key not in self._model_cache:
                tokenizer = GPT2Tokenizer.from_pretrained(model_artifact.tokenizer_path)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                model = GPT2LMHeadModel.from_pretrained(model_artifact.model_path)
                model.to(self.device)
                model.eval()
                self._tokenizer_cache[cache_key] = tokenizer
                self._model_cache[cache_key] = model
            tokenizer = self._tokenizer_cache[cache_key]
            model = self._model_cache[cache_key]
            
            # Create text generation pipeline
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            # Generate text
            generated = generator(
                request.prompt,
                max_length=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                repetition_penalty=request.repetition_penalty,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                pad_token_id=tokenizer.eos_token_id
            )
            
            # Extract generated text (remove prompt)
            generated_texts = []
            for result in generated:
                full_text = result['generated_text']
                # Remove the original prompt from the generated text
                if full_text.startswith(request.prompt):
                    generated_text = full_text[len(request.prompt):].strip()
                else:
                    generated_text = full_text
                generated_texts.append(generated_text)
            
            generation_time = time.time() - start_time
            
            # Update model usage statistics
            await self._update_model_usage(model_artifact.model_id, generation_time)
            
            return TextGenerationResponse(
                generated_text=generated_texts,
                prompt=request.prompt,
                domain_id=request.domain_id,
                niche_id=request.niche_id,
                model_used=model_artifact.model_id,
                generation_time=generation_time,
                metadata={
                    "model_name": model_artifact.name,
                    "model_version": model_artifact.version,
                    "parameters_used": {
                        "temperature": request.temperature,
                        "top_p": request.top_p,
                        "top_k": request.top_k,
                        "max_length": request.max_length
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise RuntimeError(f"Text generation failed: {str(e)}")
    
    async def _find_best_model(
        self, 
        domain_id: str, 
        niche_id: Optional[str] = None
    ) -> Optional[ModelArtifact]:
        """Find the best model for given domain/niche"""
        
        # Try to find exact match first (domain + niche)
        if niche_id:
            model_data = await self.models_collection.find_one({
                "domain_id": domain_id,
                "niche_id": niche_id,
                "is_active": True
            }, sort=[("final_loss", 1)])  # Best loss first
            
            if model_data:
                return ModelArtifact(**model_data)
        
        # Fall back to domain-only model
        model_data = await self.models_collection.find_one({
            "domain_id": domain_id,
            "is_active": True
        }, sort=[("final_loss", 1)])
        
        if model_data:
            return ModelArtifact(**model_data)
        
        default_artifact = self._build_default_artifact(domain_id, niche_id)
        if default_artifact:
            return default_artifact

        return None
    
    async def _update_model_usage(self, model_id: str, generation_time: float):
        """Update model usage statistics"""
        update_result = await self.models_collection.update_one(
            {"model_id": model_id},
            {
                "$inc": {"generation_count": 1},
                "$set": {"last_used": datetime.now(timezone.utc)},
                "$push": {
                    "metadata.generation_times": {
                        "$each": [generation_time],
                        "$slice": -100
                    }
                }
            }
        )

        if update_result.matched_count == 0:
            return

        pipeline = [
            {"$match": {"model_id": model_id}},
            {"$project": {
                "avg_time": {"$avg": "$metadata.generation_times"}
            }}
        ]

        result = await self.models_collection.aggregate(pipeline).to_list(1)
        if result:
            avg_time = result[0].get("avg_time", generation_time)
            await self.models_collection.update_one(
                {"model_id": model_id},
                {"$set": {"avg_generation_time": avg_time}}
            )

    def _load_default_model_metadata(self) -> Optional[Dict[str, Any]]:
        if not self.default_model_path.exists():
            return None
        metrics_path = self.default_model_path / "metrics.json"
        if not metrics_path.exists():
            logger.warning("Fine-tuned model found without metrics.json")
            return None
        try:
            with metrics_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse metrics.json: {exc}")
            return None

    def _build_default_artifact(self, domain_id: str, niche_id: Optional[str]) -> Optional[ModelArtifact]:
        if not self.default_model_path.exists():
            return None

        cache_key = f"{domain_id}:{niche_id or 'general'}"
        if cache_key in self._default_artifact_cache:
            return self._default_artifact_cache[cache_key]

        metadata = self.default_model_metadata or {}
        training = metadata.get("training", {})
        metrics = metadata.get("metrics", {})
        inference = metadata.get("inference", {})

        model_identifier = metadata.get("model_id", "bookgen-distilgpt2-v1")
        model_path_str = str(self.default_model_path)

        artifact = ModelArtifact(
            model_id=f"{model_identifier}-{domain_id}",
            name=f"BookGen DistilGPT2 Fine-Tuned ({DOMAIN_DISPLAY_NAMES.get(domain_id, domain_id)})",
            version="1.0.0",
            domain_id=domain_id,
            domain_name=DOMAIN_DISPLAY_NAMES.get(domain_id, domain_id.replace("_", " ").title()),
            niche_id=niche_id,
            niche_name=None,
            base_model=metadata.get("base_model", "distilgpt2"),
            model_size="small",
            parameters_count=82000000,
            training_job_id=model_identifier,
            training_examples=training.get("examples", 0),
            training_epochs=training.get("epochs", 0),
            final_loss=metrics.get("training_loss"),
            validation_loss=metrics.get("eval_loss"),
            model_path=model_path_str,
            tokenizer_path=model_path_str,
            config_path=str(self.default_model_path / "config.json"),
            perplexity=metrics.get("validation_perplexity"),
            bleu_score=None,
            rouge_scores=None,
            generation_count=0,
            last_used=None,
            avg_generation_time=inference.get("average_latency_ms", 380) / 1000.0,
            is_active=True,
            is_default=True,
            model_size_mb=self._calculate_model_size(self.default_model_path),
            storage_location="local",
        )

        self._default_artifact_cache[cache_key] = artifact
        return artifact