"""
Custom LLM model definition and training utilities
"""

import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import Dataset
from typing import Dict, List
import logging
from pathlib import Path


class BookGenModel:
    """Custom LLM for book generation based on domain-specific data"""
    
    def __init__(self, model_name: str = "models/final_model", use_peft: bool = False):
        """
        Initialize the model
        
        Args:
            model_name: Base model to use (distilgpt2, google/bert2bert_L-24_wmt_en_de, etc.)
            use_peft: Whether to use Parameter Efficient Fine-Tuning
        """
        self.model_name = model_name
        self.use_peft = use_peft
        self.logger = logging.getLogger(__name__)
        
        # Initialize tokenizer and model
        self.tokenizer = None
        self.model = None
        self.peft_model = None
        
        self._load_base_model()
    
    def _load_base_model(self):
        """Load the base model and tokenizer"""
        try:
            self.logger.info(f"Loading base model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Use float32 for CPU training
                device_map="auto"
            )
            
            # Setup PEFT if requested
            if self.use_peft:
                self._setup_peft()
            
            self.logger.info("Base model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading base model: {e}")
            raise
    
    def _setup_peft(self):
        """Setup Parameter Efficient Fine-Tuning"""
        try:
            # Configure LoRA (Low-Rank Adaptation)
            peft_config = LoraConfig(
                r=16,  # Rank of adaptation
                lora_alpha=32,  # LoRA scaling parameter
                target_modules=["c_attn", "c_proj"],  # Target modules for DistilGPT2
                lora_dropout=0.1,
                bias="none",
                task_type="CAUSAL_LM"
            )
            
            # Apply PEFT to model
            self.peft_model = get_peft_model(self.model, peft_config)
            
            # Print trainable parameters
            self.peft_model.print_trainable_parameters()
            
            self.logger.info("PEFT configuration applied successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up PEFT: {e}")
            self.use_peft = False
    
    def prepare_training_data(self, training_examples: List[Dict], max_length: int = 512):
        """Prepare training data for the model"""
        
        def tokenize_function(examples):
            # Combine input and output for causal language modeling
            texts = []
            for i in range(len(examples["input"])):
                text = f"Input: {examples['input'][i]}\nOutput: {examples['output'][i]}"
                texts.append(text)
            
            # Tokenize
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt"
            )
            
            # For causal LM, labels are the same as input_ids
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        # Convert to HuggingFace Dataset
        dataset_dict = {
            "input": [ex["input"] for ex in training_examples],
            "output": [ex["output"] for ex in training_examples],
            "domain": [ex["domain"] for ex in training_examples],
            "niche": [ex["niche"] for ex in training_examples]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def train(self, training_dataset, output_dir: str, num_epochs: int = 3):
        """Train the model"""
        
        # Training arguments optimized for CPU
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=2,  # Small batch size for CPU
            gradient_accumulation_steps=4,   # Effective batch size = 2 * 4 = 8
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="no",  # No validation set for now
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_num_workers=0,  # Important for CPU training
            fp16=False,  # Disable mixed precision for CPU
            optim="adamw_torch",  # Use PyTorch optimizer
            learning_rate=5e-5,
            weight_decay=0.01,
            lr_scheduler_type="linear",
            report_to=None,  # Disable wandb for now
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal language modeling
        )
        
        # Use PEFT model if available, otherwise base model
        model_to_train = self.peft_model if self.use_peft else self.model
        
        # Initialize trainer
        trainer = Trainer(
            model=model_to_train,
            args=training_args,
            train_dataset=training_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        self.logger.info("Starting training...")
        trainer.train()
        
        # Save the model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        self.logger.info(f"Training completed. Model saved to {output_dir}")
    
    def generate_content(self, prompt: str, max_length: int = 256, 
                        temperature: float = 0.7, top_p: float = 0.9) -> str:
        """Generate content using the trained model"""
        
        if not self.model:
            raise ValueError("Model not loaded")
        
        # Use PEFT model if available
        model_to_use = self.peft_model if self.use_peft else self.model
        
        # Tokenize input
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = model_to_use.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )
        
        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the input prompt from output
        generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
    
    def save_model(self, save_path: str):
        """Save the trained model"""
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        if self.use_peft and self.peft_model:
            self.peft_model.save_pretrained(save_path)
        else:
            self.model.save_pretrained(save_path)
        
        self.tokenizer.save_pretrained(save_path)
        
        self.logger.info(f"Model saved to {save_path}")
    
    def load_model(self, model_path: str):
        """Load a trained model"""
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            if self.use_peft:
                # Load base model first
                base_model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32
                )
                
                # Load PEFT model
                self.peft_model = PeftModel.from_pretrained(base_model, model_path)
                self.model = base_model
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float32
                )
            
            self.logger.info(f"Model loaded from {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise


class ModelEvaluator:
    """Evaluate model performance and quality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def evaluate_generation_quality(self, model: BookGenModel, test_prompts: List[str]) -> Dict[str, float]:
        """Evaluate the quality of generated content"""
        
        metrics = {
            "avg_length": 0,
            "coherence_score": 0,
            "diversity_score": 0
        }
        
        generated_texts = []
        
        for prompt in test_prompts:
            try:
                generated = model.generate_content(prompt)
                generated_texts.append(generated)
            except Exception as e:
                self.logger.error(f"Error generating for prompt '{prompt}': {e}")
                continue
        
        if generated_texts:
            # Calculate metrics
            metrics["avg_length"] = sum(len(text.split()) for text in generated_texts) / len(generated_texts)
            
            # Simple diversity score (unique words ratio)
            all_words = []
            for text in generated_texts:
                all_words.extend(text.lower().split())
            
            if all_words:
                metrics["diversity_score"] = len(set(all_words)) / len(all_words)
        
        return metrics
