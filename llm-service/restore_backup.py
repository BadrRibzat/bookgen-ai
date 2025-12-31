#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path

def setup_kaggle_auth():
    """Ensure Kaggle API is set up"""
    kaggle_config_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_config_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print(f"❌ Error: Kaggle API key not found at {kaggle_json}")
        return False
    os.chmod(kaggle_json, 0o600)
    return True

def restore_backup(dataset_slug, project_root):
    """Download and intelligently distribute files"""
    temp_dir = project_root / "temp_restore"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    print(f"⬇️  Downloading {dataset_slug}...")
    
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(dataset_slug, path=temp_dir, unzip=True)
    except ImportError:
        print("❌ Error: 'kaggle' library not installed. Run 'pip install kaggle'")
        return
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return

    print("✅ Download complete. Analyzing structure...")
    
    # Define targets
    model_target = project_root / "models" / "final_model"
    data_target = project_root / "data"
    
    # 1. Restore Model
    model_files = ["pytorch_model.bin", "model.safetensors", "config.json", "vocab.json"]
    restored_model = False
    
    # Check root of temp
    if any((temp_dir / f).exists() for f in model_files):
        print(f"📦 Found model files in root. Moving to {model_target.relative_to(project_root)}...")
        model_target.mkdir(parents=True, exist_ok=True)
        for item in temp_dir.iterdir():
            if item.is_file() and item.name in model_files + ["merges.txt", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]:
                shutil.copy2(item, model_target / item.name)
        restored_model = True
    
    # Check for 'final_model' folder
    elif (temp_dir / "final_model").exists():
        print(f"📦 Found 'final_model' folder. Moving content to {model_target.relative_to(project_root)}...")
        model_target.mkdir(parents=True, exist_ok=True)
        source = temp_dir / "final_model"
        for item in source.iterdir():
            shutil.copy2(item, model_target / item.name)
        restored_model = True

    if restored_model:
        print("✅ Model restored successfully.")
    else:
        print("⚠️  No model files found in backup.")

    # 2. Restore Data
    restored_data = False
    possible_data_dirs = ["data", "training_sets", "processed"]
    
    for d in possible_data_dirs:
        if (temp_dir / d).exists():
            print(f"📂 Found data directory '{d}'. Merging into {data_target.relative_to(project_root)}...")
            # Simple recursive copy
            try:
                shutil.copytree(temp_dir / d, data_target, dirs_exist_ok=True)
                restored_data = True
                print(f"   Merged content from '{d}'")
            except Exception as e:
                print(f"   Failed to merge '{d}': {e}")
    
    if not restored_data:
        # Check for JSON files in root that might be data
        json_files = list(temp_dir.glob("*.json"))
        data_json = [j for j in json_files if j.name not in model_files]
        if data_json:
            print(f"📂 Found {len(data_json)} JSON files in root. Copying to data/import_queue...")
            import_queue = data_target / "import_queue"
            import_queue.mkdir(exist_ok=True)
            for j in data_json:
                shutil.copy2(j, import_queue / j.name)
            restored_data = True

    if restored_data:
        print("✅ Data restored successfully.")
    else:
        print("ℹ️  No specific data directories found to restore.")

    # Cleanup
    shutil.rmtree(temp_dir)
    print("\n✨ Restore operation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore BookGen System from Kaggle")
    parser.add_argument("dataset", help="Kaggle dataset slug (user/dataset)")
    args = parser.parse_args()
    
    root = Path(__file__).parent
    restore_backup(args.dataset, root)
