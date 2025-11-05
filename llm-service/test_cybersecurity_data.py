#!/usr/bin/env python3
"""
Simple test to verify cybersecurity data quality and readiness for training
"""

import json
import os
from pathlib import Path

def test_cybersecurity_data():
    """Test the processed cybersecurity data"""
    
    print("🧪 Testing Cybersecurity Training Data")
    print("=====================================\n")
    
    data_dir = Path("data/training_sets/cybersecurity")
    
    if not data_dir.exists():
        print("❌ Error: Cybersecurity data directory not found")
        return False
    
    # Get all JSON files (excluding template)
    json_files = [f for f in data_dir.glob("*.json") if f.name != "template.json"]
    
    if not json_files:
        print("❌ Error: No training data files found")
        return False
    
    total_examples = 0
    tier_stats = {'basic': 0, 'professional': 0, 'enterprise': 0}
    file_stats = {}
    
    print(f"📁 Found {len(json_files)} training data files\n")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            examples = data.get('training_examples', [])
            file_stats[json_file.name] = len(examples)
            total_examples += len(examples)
            
            print(f"📄 {json_file.name}")
            print(f"   ✓ Valid JSON structure")
            print(f"   ✓ {len(examples)} training examples")
            
            # Check subscription tier distribution
            for example in examples:
                tier = example.get('subscription_tier', 'unknown')
                if tier in tier_stats:
                    tier_stats[tier] += 1
            
            # Sample validation
            if examples:
                sample = examples[0]
                required_fields = ['id', 'input', 'output', 'subscription_tier', 'difficulty_level']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if missing_fields:
                    print(f"   ⚠️  Missing fields in sample: {missing_fields}")
                else:
                    print(f"   ✓ All required fields present")
                
                # Check quality score
                quality_score = sample.get('quality_score', 0)
                print(f"   ✓ Quality score: {quality_score}/10")
            
            print()
            
        except json.JSONDecodeError as e:
            print(f"❌ {json_file.name}: Invalid JSON - {e}")
            return False
        except Exception as e:
            print(f"❌ {json_file.name}: Error - {e}")
            return False
    
    # Summary statistics
    print("📊 SUMMARY STATISTICS")
    print("====================")
    print(f"Total training examples: {total_examples}")
    print(f"Files processed: {len(json_files)}")
    print("\n📈 By subscription tier:")
    for tier, count in tier_stats.items():
        percentage = (count / total_examples * 100) if total_examples > 0 else 0
        print(f"   {tier.capitalize()}: {count} ({percentage:.1f}%)")
    
    print(f"\n📋 By file:")
    for filename, count in file_stats.items():
        print(f"   {filename}: {count} examples")
    
    # Quality checks
    print(f"\n🔍 QUALITY ASSESSMENT")
    print("=====================")
    
    if total_examples >= 100:
        print("✅ Sufficient training examples (100+ recommended)")
    else:
        print(f"⚠️  Low training examples count: {total_examples} (100+ recommended)")
    
    if tier_stats['basic'] > 0 and tier_stats['professional'] > 0 and tier_stats['enterprise'] > 0:
        print("✅ Good tier distribution (all tiers represented)")
    else:
        print("⚠️  Uneven tier distribution")
    
    if len(json_files) >= 3:
        print("✅ Good data source diversity (3+ files)")
    else:
        print("⚠️  Limited data source diversity")
    
    # MongoDB connection test (without full import)
    print(f"\n🔗 ENVIRONMENT CHECK")
    print("====================")
    
    db_url = os.getenv('DATABASE_URL')
    if db_url and 'mongodb' in db_url and '<username>' not in db_url:
        print("✅ MongoDB connection string configured")
    else:
        print("⚠️  MongoDB connection string not properly configured")
    
    print(f"\n🎯 TRAINING READINESS")
    print("====================")
    
    if total_examples >= 100 and len(json_files) >= 3:
        print("🚀 READY FOR TRAINING!")
        print("Your cybersecurity data is well-prepared for LLM fine-tuning.")
        print("\nNext steps:")
        print("1. Fix any MongoDB connection issues if present")
        print("2. Run training with: python3 train_model.py --domain cybersecurity")
        print("3. Test the trained model with sample prompts")
        return True
    else:
        print("📈 NEEDS IMPROVEMENT")
        print("Consider adding more training examples or data sources.")
        return False

if __name__ == '__main__':
    success = test_cybersecurity_data()
    exit(0 if success else 1)