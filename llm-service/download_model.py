#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
import json

def setup_kaggle_auth():
    """Ensure Kaggle API is set up"""
    kaggle_config_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_config_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print(f"❌ Error: Kaggle API key not found at {kaggle_json}")
        print("Please download your kaggle.json from your Kaggle account settings")
        print(f"and place it in {kaggle_config_dir}")
        return False
        
    os.chmod(kaggle_json, 0o600)
    return True

def download_model(dataset_slug, output_dir):
    """Download model files from Kaggle dataset"""
    print(f"⬇️  Downloading dataset {dataset_slug} to {output_dir}...")
    
    try:
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Download all files
        api.dataset_download_files(dataset_slug, path=output_dir, unzip=True)
        
        print("✅ Download complete!")
        
        # Verify critical files
        files = list(Path(output_dir).glob("*"))
        print(f"📂 Extracted {len(files)} files:")
        for f in files:
            print(f"  - {f.name}")
            
        required_weights = ["pytorch_model.bin", "model.safetensors"]
        has_weights = any(f.name in required_weights for f in files)
        
        if has_weights:
            print("\n✅ Valid model weights found!")
        else:
            print(f"\n⚠️  WARNING: Could not find {' or '.join(required_weights)}")
            print("Please check if your Kaggle dataset contains the actual model weights.")
            
    except ImportError:
        print("❌ Error: 'kaggle' library not installed.")
        print("Run: pip install kaggle")
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download BookGen model from Kaggle")
    parser.add_argument("dataset", nargs="?", help="Kaggle dataset slug (user/dataset)")
    args = parser.parse_args()
    
    dataset_slug = args.dataset
    if not dataset_slug:
        print("Please enter the Kaggle Dataset Slug containing your model.")
        print("Format: username/dataset-name")
        dataset_slug = input("Dataset Slug: ").strip()
    
    if not dataset_slug:
        print("❌ No dataset specified.")
        sys.exit(1)
        
    if not setup_kaggle_auth():
        sys.exit(1)
        
    # Project specific path
    current_dir = Path(__file__).parent
    models_dir = current_dir / "models" / "final_model"
    
    download_model(dataset_slug, str(models_dir))
