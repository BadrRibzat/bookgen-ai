#!/usr/bin/env python3
"""Kaggle-optimized training script for BookGen - REAL TRAINING"""

import os
import json
import logging
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List

import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    set_seed,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("bookgen_kaggle")

@dataclass
class TrainingExample:
    text: str
    domain: str

def load_kaggle_data():
    """Load ALL data from Kaggle dataset"""
    examples = []
    data_path = Path("/kaggle/input/bookgen-training-data")
    
    domains = [d for d in data_path.iterdir() if d.is_dir()]
    logger.info(f"Found domains: {[d.name for d in domains]}")
    
    for domain in domains:
        processed_dir = domain / "processed"
        if not processed_dir.exists():
            logger.warning(f"No processed dir for {domain.name}")
            continue
            
        for json_file in processed_dir.glob("*.json"):
            if json_file.name.upper() == "SUMMARY.json":
                continue
                
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for example in data.get('training_examples', []):
                    prompt = example.get('input', '').strip()
                    completion = example.get('output', '').strip()
                    context = example.get('context', '').strip()
                    
                    if prompt and completion:
                        # Build formatted text (same as your original)
                        segments = []
                        if context:
                            segments.append(f"[CONTEXT]\n{context}")
                        segments.append(f"[PROMPT]\n{prompt}")
                        segments.append(f"[RESPONSE]\n{completion}")
                        text = "\n\n".join(segments)
                        
                        examples.append(TrainingExample(text=text, domain=domain.name))
                        
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
                continue
    
    logger.info(f"Loaded {len(examples)} total examples")
    return examples

def main():
    set_seed(42)
    
    # Load ALL data
    logger.info("Loading ALL training data...")
    examples = load_kaggle_data()
    
    if not examples:
        raise ValueError("No training examples found!")
    
    # Split train/eval (90/10)
    random.shuffle(examples)
    split_idx = int(0.9 * len(examples))
    train_examples = examples[:split_idx]
    eval_examples = examples[split_idx:]
    
    logger.info(f"Train examples: {len(train_examples)}, Eval examples: {len(eval_examples)}")
    
    # Prepare datasets
    train_dataset = Dataset.from_list([{"text": ex.text} for ex in train_examples])
    eval_dataset = Dataset.from_list([{"text": ex.text} for ex in eval_examples])
    
    # Load model and tokenizer
    logger.info("Loading model and tokenizer...")
    model_name = "distilgpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Tokenize datasets
    def tokenize_function(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=512,  # Same as your original
            padding="max_length",
        )
    
    train_dataset = train_dataset.map(tokenize_function, batched=True, num_proc=4)
    eval_dataset = eval_dataset.map(tokenize_function, batched=True, num_proc=4)
    
    train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
    eval_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
    
    # REAL TRAINING ARGUMENTS - optimized for Kaggle GPU
    training_args = TrainingArguments(
        output_dir="/kaggle/working/output",
        overwrite_output_dir=True,
        num_train_epochs=3,  # Your original setting
        per_device_train_batch_size=8,  # Increased for GPU
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=4,  # Effective batch size = 8 * 4 = 32
        learning_rate=5e-5,  # Your original setting
        warmup_ratio=0.03,   # Your original setting
        logging_steps=25,    # Your original setting
        eval_steps=200,      # Your original setting
        save_steps=500,      # Your original setting
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,  # CRITICAL for GPU speed
        dataloader_num_workers=4,
        report_to="none",
        save_total_limit=3,  # Your original setting
    )
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )
    
    # Start REAL training
    logger.info("Starting REAL training with ALL data...")
    logger.info(f"Total training steps: {len(train_dataset) // (8 * 4) * 3}")  # approx calculation
    
    trainer.train()
    
    # Save final model
    trainer.save_model("/kaggle/working/final_model")
    tokenizer.save_pretrained("/kaggle/working/final_model")
    
    logger.info("REAL Training completed successfully!")
    logger.info("Model saved to: /kaggle/working/final_model")

if __name__ == "__main__":
    main()
