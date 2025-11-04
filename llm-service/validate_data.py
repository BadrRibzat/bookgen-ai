#!/usr/bin/env python3
"""
Data Validation Utilities for LLM Training Data
Validates JSON format, content structure, and quality before training.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import argparse
from datetime import datetime

class DataValidator:
    """Validates training data structure and content."""
    
    def __init__(self):
        self.required_fields = {
            'domain': str,
            'description': str,
            'version': str,
            'total_examples': int,
            'subscription_tiers': dict,
            'training_examples': list
        }
        
        self.required_example_fields = {
            'id': str,
            'input': str, 
            'output': str,
            'context': str,
            'difficulty_level': int,
            'subscription_tier': str,
            'tags': list,
            'quality_score': (int, float),
            'metadata': dict
        }
        
        self.valid_tiers = ['basic', 'professional', 'enterprise']
        self.valid_domains = [
            'cybersecurity', 'ai_ml', 'automation', 'healthtech',
            'creator_economy', 'web3', 'ecommerce', 'data_analytics',
            'gaming', 'kids_parenting', 'nutrition', 'recipes'
        ]
    
    def validate_json_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate a single JSON file."""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON format: {e}"]
        except Exception as e:
            return False, [f"Error reading file: {e}"]
        
        # Validate top-level structure
        errors.extend(self._validate_structure(data))
        
        # Validate training examples
        if 'training_examples' in data:
            errors.extend(self._validate_examples(data['training_examples']))
        
        # Validate domain consistency
        errors.extend(self._validate_domain_consistency(data, file_path))
        
        return len(errors) == 0, errors
    
    def _validate_structure(self, data: Dict[str, Any]) -> List[str]:
        """Validate top-level data structure."""
        errors = []
        
        # Check required fields
        for field, expected_type in self.required_fields.items():
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(data[field], expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
        
        # Validate domain
        if 'domain' in data and data['domain'] not in self.valid_domains:
            errors.append(f"Invalid domain '{data['domain']}'. Must be one of: {self.valid_domains}")
        
        # Validate subscription tiers
        if 'subscription_tiers' in data:
            for tier in data['subscription_tiers'].keys():
                if tier not in self.valid_tiers:
                    errors.append(f"Invalid subscription tier '{tier}'. Must be one of: {self.valid_tiers}")
        
        return errors
    
    def _validate_examples(self, examples: List[Dict[str, Any]]) -> List[str]:
        """Validate training examples."""
        errors = []
        
        if not examples:
            errors.append("No training examples found")
            return errors
        
        example_ids = set()
        
        for i, example in enumerate(examples):
            example_errors = []
            
            # Check required fields
            for field, expected_type in self.required_example_fields.items():
                if field not in example:
                    example_errors.append(f"Missing field: {field}")
                elif isinstance(expected_type, tuple):
                    if not isinstance(example[field], expected_type):
                        example_errors.append(f"Field '{field}' must be of type {[t.__name__ for t in expected_type]}")
                elif not isinstance(example[field], expected_type):
                    example_errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
            
            # Check unique IDs
            if 'id' in example:
                if example['id'] in example_ids:
                    example_errors.append(f"Duplicate example ID: {example['id']}")
                example_ids.add(example['id'])
            
            # Validate subscription tier
            if 'subscription_tier' in example and example['subscription_tier'] not in self.valid_tiers:
                example_errors.append(f"Invalid subscription tier: {example['subscription_tier']}")
            
            # Validate difficulty level
            if 'difficulty_level' in example:
                if not 1 <= example['difficulty_level'] <= 10:
                    example_errors.append("Difficulty level must be between 1 and 10")
            
            # Validate quality score
            if 'quality_score' in example:
                if not 0 <= example['quality_score'] <= 10:
                    example_errors.append("Quality score must be between 0 and 10")
            
            # Validate content length
            if 'input' in example and len(example['input']) < 10:
                example_errors.append("Input text too short (minimum 10 characters)")
            
            if 'output' in example and len(example['output']) < 20:
                example_errors.append("Output text too short (minimum 20 characters)")
            
            # Add example-specific errors
            if example_errors:
                errors.append(f"Example {i+1} errors: {'; '.join(example_errors)}")
        
        return errors
    
    def _validate_domain_consistency(self, data: Dict[str, Any], file_path: Path) -> List[str]:
        """Validate domain consistency with file location."""
        errors = []
        
        if 'domain' in data:
            expected_domain = file_path.parent.name
            if data['domain'] != expected_domain:
                errors.append(f"Domain mismatch: file in '{expected_domain}' folder but domain is '{data['domain']}'")
        
        return errors
    
    def validate_directory(self, directory_path: Path) -> Dict[str, Any]:
        """Validate all JSON files in a directory."""
        results = {
            'valid_files': [],
            'invalid_files': [],
            'total_examples': 0,
            'errors': []
        }
        
        if not directory_path.exists():
            results['errors'].append(f"Directory does not exist: {directory_path}")
            return results
        
        json_files = list(directory_path.glob("*.json"))
        
        if not json_files:
            results['errors'].append(f"No JSON files found in {directory_path}")
            return results
        
        for json_file in json_files:
            if json_file.name == 'template.json':
                continue  # Skip template files
            
            is_valid, errors = self.validate_json_file(json_file)
            
            if is_valid:
                results['valid_files'].append(str(json_file))
                # Count examples
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        if 'training_examples' in data:
                            results['total_examples'] += len(data['training_examples'])
                except:
                    pass
            else:
                results['invalid_files'].append({
                    'file': str(json_file),
                    'errors': errors
                })
        
        return results
    
    def validate_all_domains(self, base_path: Path) -> Dict[str, Any]:
        """Validate all domain directories."""
        overall_results = {
            'domains': {},
            'summary': {
                'total_files': 0,
                'valid_files': 0,
                'invalid_files': 0,
                'total_examples': 0
            }
        }
        
        training_sets_path = base_path / "data" / "training_sets"
        
        if not training_sets_path.exists():
            overall_results['error'] = f"Training sets directory not found: {training_sets_path}"
            return overall_results
        
        for domain in self.valid_domains:
            domain_path = training_sets_path / domain
            if domain_path.exists():
                results = self.validate_directory(domain_path)
                overall_results['domains'][domain] = results
                
                # Update summary
                overall_results['summary']['total_files'] += len(results['valid_files']) + len(results['invalid_files'])
                overall_results['summary']['valid_files'] += len(results['valid_files'])
                overall_results['summary']['invalid_files'] += len(results['invalid_files'])
                overall_results['summary']['total_examples'] += results['total_examples']
        
        return overall_results


def main():
    parser = argparse.ArgumentParser(description="Validate LLM training data")
    parser.add_argument('--path', type=str, default='.', help='Path to validate (file or directory)')
    parser.add_argument('--domain', type=str, help='Validate specific domain only')
    parser.add_argument('--all', action='store_true', help='Validate all domains')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    validator = DataValidator()
    base_path = Path(args.path)
    
    if args.all:
        print("🔍 Validating all domains...")
        results = validator.validate_all_domains(base_path)
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}")
            sys.exit(1)
        
        # Print summary
        summary = results['summary']
        print(f"\n📊 VALIDATION SUMMARY")
        print(f"Total files: {summary['total_files']}")
        print(f"Valid files: {summary['valid_files']} ✅")
        print(f"Invalid files: {summary['invalid_files']} ❌")
        print(f"Total training examples: {summary['total_examples']}")
        
        # Print domain details
        if args.verbose:
            print(f"\n📁 DOMAIN DETAILS")
            for domain, domain_results in results['domains'].items():
                print(f"\n{domain.upper()}:")
                print(f"  Valid files: {len(domain_results['valid_files'])}")
                print(f"  Invalid files: {len(domain_results['invalid_files'])}")
                print(f"  Examples: {domain_results['total_examples']}")
                
                if domain_results['invalid_files']:
                    print(f"  Errors:")
                    for invalid in domain_results['invalid_files']:
                        print(f"    {Path(invalid['file']).name}: {'; '.join(invalid['errors'][:3])}...")
        
        if summary['invalid_files'] > 0:
            sys.exit(1)
    
    elif args.domain:
        print(f"🔍 Validating domain: {args.domain}")
        domain_path = base_path / "data" / "training_sets" / args.domain
        results = validator.validate_directory(domain_path)
        
        print(f"Valid files: {len(results['valid_files'])} ✅")
        print(f"Invalid files: {len(results['invalid_files'])} ❌")
        print(f"Training examples: {results['total_examples']}")
        
        if results['invalid_files']:
            print(f"\n❌ ERRORS:")
            for invalid in results['invalid_files']:
                print(f"\n{Path(invalid['file']).name}:")
                for error in invalid['errors']:
                    print(f"  - {error}")
            sys.exit(1)
    
    else:
        # Validate single file or directory
        path = Path(args.path)
        if path.is_file():
            print(f"🔍 Validating file: {path}")
            is_valid, errors = validator.validate_json_file(path)
            
            if is_valid:
                print("✅ File is valid!")
            else:
                print("❌ File has errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
        else:
            print(f"🔍 Validating directory: {path}")
            results = validator.validate_directory(path)
            
            print(f"Valid files: {len(results['valid_files'])} ✅")
            print(f"Invalid files: {len(results['invalid_files'])} ❌")
            
            if results['invalid_files']:
                for invalid in results['invalid_files']:
                    print(f"\n❌ {Path(invalid['file']).name}:")
                    for error in invalid['errors']:
                        print(f"  - {error}")
                sys.exit(1)
    
    print("\n🎉 All validations passed!")


if __name__ == "__main__":
    main()