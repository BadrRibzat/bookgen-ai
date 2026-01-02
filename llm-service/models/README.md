# Model Management

## Current Models
- **final_model/** - Active model for production/testing
- **archive/** - Archived model versions
- **checkpoints/** - Training checkpoints

## Archive Contents
- `bookgen_final_model.zip` (v1.0, 291MB)
  - Trained on: Kaggle
  - Date: January 2024
  - Dataset: bookgen-training-data-clean
  - Contains: model.safetensors + configs

## Git LFS
Large model files are tracked with Git LFS. To clone properly:
```bash
git lfs install
git clone your-repo-url
git lfs pull
Restoring from Archive
bash
# Extract archive to final_model
unzip archive/bookgen_final_model.zip -d final_model/
