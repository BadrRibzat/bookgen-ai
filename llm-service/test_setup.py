#!/usr/bin/env python3
"""
Test script for LLM Service setup
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing LLM Service imports...")
    
    try:
        # Test core dependencies
        import fastapi
        import uvicorn
        import pydantic
        print("✓ FastAPI and core dependencies")
        
        # Test MongoDB
        import motor.motor_asyncio
        import pymongo
        print("✓ MongoDB drivers (Motor, PyMongo)")
        
        # Test ML libraries
        import torch
        import transformers
        import datasets
        import accelerate
        import peft
        print("✓ PyTorch and ML libraries")
        
        # Test text processing
        import nltk
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print("✓ NLTK and spaCy with English model")
        
        # Test data processing
        import pandas
        import numpy
        print("✓ Data processing libraries")
        
        # Test PDF generation
        import reportlab
        print("✓ ReportLab for PDF generation")
        
        print("\n✅ All dependencies successfully imported!")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def check_file_structure():
    """Check if all required files are present"""
    print("\nChecking LLM Service file structure...")
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/ml/__init__.py",
        "app/ml/preprocessing.py",
        "app/ml/service.py",
        "app/ml/model.py",
        "app/ml/pdf_generator.py",
        "requirements.txt"
    ]
    
    all_present = True
    base_path = Path(__file__).parent
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_present = False
    
    return all_present

def check_requirements():
    """Check requirements.txt content"""
    print("\nChecking requirements.txt...")
    
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    with open(req_file, 'r') as f:
        requirements = f.read()
    
    critical_packages = [
        'fastapi', 'uvicorn', 'torch', 'transformers', 
        'peft', 'reportlab', 'nltk', 'spacy', 'motor', 
        'pymongo', 'datasets', 'accelerate'
    ]
    
    missing_packages = []
    for package in critical_packages:
        if package.lower() not in requirements.lower():
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing critical packages: {missing_packages}")
        return False
    else:
        print("✅ All critical packages present in requirements.txt")
        return True

def main():
    """Main test function"""
    print("🔍 BookGen LLM Service - Setup Verification")
    print("=" * 50)
    
    # Check file structure
    structure_ok = check_file_structure()
    
    # Check requirements
    requirements_ok = check_requirements()
    
    # Test imports
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    if structure_ok and requirements_ok and imports_ok:
        print("🎉 LLM Service setup verification PASSED!")
        print("📋 Next steps:")
        print("1. ✅ Dependencies installed successfully")
        print("2. Set MongoDB Atlas connection: export MONGODB_URL='mongodb+srv://...'")
        print("3. Import your manually collected training data")
        print("4. Train custom model with domain-specific data")
        print("5. Generate professional books!")
    else:
        print("❌ LLM Service setup verification FAILED!")
        print("Please fix the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()