# BookGen-AI DistilGPT2 Fine-Tuned Model

This directory contains the production-ready BookGen-AI language model fine-tuned on 12 publishing domains. Training was executed on Kaggle GPUs using the `kaggle_train.py` pipeline.

## Training Snapshot (November 2025)
- **Base checkpoint**: `distilgpt2`
- **Domains covered**: ai_ml, automation, healthtech, cybersecurity, creator_economy, web3, ecommerce, data_analytics, gaming, kids_parenting, nutrition, recipes
- **Training examples**: 144,699
- **Epochs**: 3 (12,210 optimizer steps)
- **Hardware**: NVIDIA T4 (Kaggle P100 tier) with mixed precision (fp16)
- **Training duration**: 6 hours 2 minutes (down from ~2 year CPU estimate)
- **Final training loss**: 1.47
- **Evaluation loss**: 1.92
- **Validation perplexity**: 6.83 (baseline distilgpt2 perplexity: 14.71)

## Saved Artifacts
- `model.safetensors` – consolidated model weights (~300 MB)
- `config.json` – Hugging Face configuration
- `generation_config.json` – default inference settings
- `tokenizer.json`, `tokenizer_config.json`, `vocab.json`, `merges.txt`, `special_tokens_map.json`
- `training_args.bin` – Hugging Face Trainer metadata
- `metrics.json` – fine-tuning and evaluation metrics (see below)

## Usage
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "llm-service/models/final_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

output = model.generate(
    **tokenizer("Outline the key trends in AI for 2026", return_tensors="pt"),
    max_new_tokens=220,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

## Integration Notes
- Docker images mount this directory read-only at `/app/models/final_model`.
- `LLM_MODEL_PATH` defaults to this location when not supplied explicitly.
- Update instructions are documented in `README.md` (root) under **Fine-Tuned Model Setup**.

## Reproducing Training
1. Upload `llm-service/kaggle_train.py` and the curated dataset to your Kaggle notebook.
2. Set `BOOKGEN_RUN_FULL=1` environment variable to enable full training.
3. After training, download `/kaggle/working/final_model` and replace the contents of this directory.
4. Run `python scripts/model/register_finetuned_model.py` to refresh local metadata (see deployment scripts).

For detailed metrics and comparisons with the base `distilgpt2`, refer to `metrics.json`.
