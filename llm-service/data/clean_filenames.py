#!/usr/bin/env python3
import os
import re
from pathlib import Path
import shutil

def clean_filename(filename):
    """Replace forbidden characters with underscores"""
    # Kaggle forbids: &, %, ?, *, :, |, ", <, >, etc.
    forbidden_chars = r'[&%?*:|"<>]'
    cleaned = re.sub(forbidden_chars, '_', filename)
    return cleaned

def clean_directory_structure(root_dir):
    """Recursively clean all filenames in directory"""
    root_path = Path(root_dir)
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            original_name = file_path.name
            cleaned_name = clean_filename(original_name)
            
            if original_name != cleaned_name:
                new_path = file_path.parent / cleaned_name
                print(f"Renaming: {original_name} -> {cleaned_name}")
                shutil.move(str(file_path), str(new_path))

def create_clean_zip():
    """Create a clean copy of training_sets and zip it"""
    training_sets_dir = "training_sets"
    clean_dir = "training_sets_clean"
    
    # Remove existing clean directory if it exists
    if os.path.exists(clean_dir):
        shutil.rmtree(clean_dir)
    
    # Copy and clean the structure
    print("Copying directory structure...")
    shutil.copytree(training_sets_dir, clean_dir)
    
    # Clean all filenames
    print("Cleaning filenames...")
    clean_directory_structure(clean_dir)
    
    # Create zip file
    print("Creating zip file...")
    shutil.make_archive("bookgen-training-data-clean", 'zip', clean_dir)
    
    print("Done! Upload 'bookgen-training-data-clean.zip' to Kaggle")

if __name__ == "__main__":
    create_clean_zip()
