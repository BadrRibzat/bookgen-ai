#!/usr/bin/env python3
"""
CLI tool for importing training data from Data.gov JSON files
Usage: python demo_manual_import.py --help
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import motor.motor_asyncio
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Load environment variables
load_dotenv()


async def setup_database():
    """Setup database connection"""
    database_url = os.getenv("DATABASE_URL")
    db_name = os.getenv("MONGODB_DB_NAME", "bookgen_ai")
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    client = motor.motor_asyncio.AsyncIOMotorClient(database_url)
    database = client[db_name]
    
    # Test connection
    await client.admin.command('ping')
    print(f"✓ Connected to MongoDB: {db_name}")
    
    return database


async def import_training_data(
    file_path: str,
    domain_id: str,
    domain_name: str,
    niche_id: Optional[str] = None,
    niche_name: Optional[str] = None,
    source: str = "data_gov"
):
    """Import training data from JSON file"""
    from ml.data_importer import TrainingDataImporter
    
    try:
        # Setup database
        database = await setup_database()
        importer = TrainingDataImporter(database)
        
        print(f"📥 Importing training data from: {file_path}")
        print(f"   Domain: {domain_name} ({domain_id})")
        if niche_name:
            print(f"   Niche: {niche_name} ({niche_id})")
        print(f"   Source: {source}")
        
        # Import data
        imported, skipped, errors = await importer.import_from_json_file(
            file_path, domain_id, domain_name, niche_id, niche_name, source
        )
        
        print(f"✓ Import completed:")
        print(f"   Imported: {imported} examples")
        print(f"   Skipped: {skipped} examples")
        if errors:
            print(f"   Errors: {len(errors)}")
            for error in errors[:5]:  # Show first 5 errors
                print(f"     - {error}")
            if len(errors) > 5:
                print(f"     ... and {len(errors) - 5} more errors")
        
        return imported > 0
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


async def import_directory(
    directory_path: str,
    domain_id: str,
    domain_name: str,
    niche_id: Optional[str] = None,
    niche_name: Optional[str] = None,
    source: str = "data_gov"
):
    """Import training data from all JSON files in directory"""
    from ml.data_importer import TrainingDataImporter
    
    try:
        # Setup database
        database = await setup_database()
        importer = TrainingDataImporter(database)
        
        print(f"📁 Importing from directory: {directory_path}")
        print(f"   Domain: {domain_name} ({domain_id})")
        if niche_name:
            print(f"   Niche: {niche_name} ({niche_id})")
        
        # Import data
        results = await importer.import_from_directory(
            directory_path, domain_id, domain_name, niche_id, niche_name, source
        )
        
        total_imported = sum(result[0] for result in results.values())
        total_skipped = sum(result[1] for result in results.values())
        
        print(f"✓ Directory import completed:")
        print(f"   Files processed: {len(results)}")
        print(f"   Total imported: {total_imported} examples")
        print(f"   Total skipped: {total_skipped} examples")
        
        # Show per-file results
        for filename, (imported, skipped, errors) in results.items():
            print(f"   {filename}: {imported} imported, {skipped} skipped")
            if errors:
                print(f"     Errors: {len(errors)}")
        
        return total_imported > 0
        
    except Exception as e:
        print(f"❌ Directory import failed: {e}")
        return False


async def list_datasets():
    """List all available datasets"""
    from ml.data_importer import TrainingDataImporter
    
    try:
        # Setup database
        database = await setup_database()
        importer = TrainingDataImporter(database)
        
        print("📊 Available training datasets:")
        
        domains = await importer.list_domains()
        
        if not domains:
            print("   No training data found")
            return
        
        for domain in domains:
            print(f"\n🔹 {domain['domain_name']} ({domain['domain_id']})")
            print(f"   Examples: {domain['total_examples']}")
            print(f"   Quality: {domain['avg_quality']:.2f}")
            print(f"   Last updated: {domain['last_updated']}")
            
            if domain['niches']:
                print(f"   Niches:")
                for niche in domain['niches']:
                    if niche['niche_id']:
                        print(f"     - {niche['niche_name']} ({niche['niche_id']})")
        
    except Exception as e:
        print(f"❌ Failed to list datasets: {e}")


async def get_stats(domain_id: str, niche_id: Optional[str] = None):
    """Get detailed statistics for a domain/niche"""
    from ml.data_importer import TrainingDataImporter
    
    try:
        # Setup database
        database = await setup_database()
        importer = TrainingDataImporter(database)
        
        print(f"📈 Statistics for domain: {domain_id}")
        if niche_id:
            print(f"   Niche: {niche_id}")
        
        stats = await importer.get_dataset_stats(domain_id, niche_id)
        
        if not stats:
            print("   No data found for this domain/niche")
            return
        
        print(f"\n📊 Dataset Overview:")
        print(f"   Domain: {stats.domain_name}")
        if stats.niche_name:
            print(f"   Niche: {stats.niche_name}")
        print(f"   Total examples: {stats.total_examples}")
        print(f"   Validated examples: {stats.validated_examples}")
        print(f"   Average quality score: {stats.avg_quality_score:.3f}")
        print(f"   Total words: {stats.total_word_count:,}")
        print(f"   Average words per example: {stats.avg_word_count:.1f}")
        
        if stats.content_types:
            print(f"\n📝 Content Types:")
            for content_type, count in stats.content_types.items():
                print(f"   {content_type}: {count}")
        
        if stats.chapter_types:
            print(f"\n📖 Chapter Types:")
            for chapter_type, count in stats.chapter_types.items():
                print(f"   {chapter_type}: {count}")
        
        if stats.target_audiences:
            print(f"\n👥 Target Audiences:")
            for audience, count in stats.target_audiences.items():
                print(f"   {audience}: {count}")
        
        if stats.quality_distribution:
            print(f"\n⭐ Quality Distribution:")
            for quality_range, count in stats.quality_distribution.items():
                print(f"   {quality_range}: {count}")
        
    except Exception as e:
        print(f"❌ Failed to get statistics: {e}")


async def clear_data(domain_id: Optional[str] = None, niche_id: Optional[str] = None):
    """Clear training data"""
    from ml.data_importer import TrainingDataImporter
    
    try:
        # Setup database
        database = await setup_database()
        importer = TrainingDataImporter(database)
        
        scope = "all data"
        if domain_id:
            scope = f"domain '{domain_id}'"
            if niche_id:
                scope += f" niche '{niche_id}'"
        
        print(f"🗑️  Clearing {scope}...")
        
        # Confirm deletion
        response = input(f"Are you sure you want to clear {scope}? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled")
            return
        
        deleted_count = await importer.clear_training_data(domain_id, niche_id)
        
        print(f"✓ Cleared {deleted_count} training examples")
        
    except Exception as e:
        print(f"❌ Failed to clear data: {e}")


def create_example_files():
    """Create example training data files"""
    from ml.data_importer import create_example_template
    
    # Create data directory
    data_dir = Path("data/training_sets")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create template file
    template_file = data_dir / "template.json"
    template_data = [create_example_template()]
    
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created template file: {template_file}")
    
    # Create domain-specific examples
    domains = {
        "ai_ml": "AI & Machine Learning",
        "automation": "Automation & Productivity", 
        "healthtech": "Health Technology",
        "cybersecurity": "Cybersecurity",
        "creator_economy": "Creator Economy",
        "web3": "Web3 & Blockchain",
        "ecommerce": "E-commerce",
        "data_analytics": "Data Analytics",
        "gaming": "Gaming",
        "kids_parenting": "Kids & Parenting",
        "nutrition": "Nutrition & Wellness",
        "recipes": "Recipes & Cooking"
    }
    
    for domain_id, domain_name in domains.items():
        domain_dir = data_dir / domain_id
        domain_dir.mkdir(exist_ok=True)
        
        example_file = domain_dir / "example_data.json"
        if not example_file.exists():
            example_data = [
                {
                    "prompt": f"Write an introduction about {domain_name.lower()} for beginners",
                    "completion": f"This is an example introduction to {domain_name.lower()}. This field should contain comprehensive, high-quality content that serves as a good training example for the AI model. The content should be informative, well-structured, and appropriate for the target audience.",
                    "metadata": {
                        "quality_score": 0.8,
                        "chapter_type": "introduction",
                        "target_audience": "beginner",
                        "tags": [domain_id, "introduction", "beginner"]
                    }
                }
            ]
            
            with open(example_file, 'w', encoding='utf-8') as f:
                json.dump(example_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {len(domains)} domain example files")
    print(f"📁 Data structure created in: {data_dir}")
    
    # Print usage instructions
    print(f"\n📝 Usage Instructions:")
    print(f"1. Edit the JSON files in data/training_sets/[domain]/")
    print(f"2. Add your training examples following the template format")
    print(f"3. Import using: python demo_manual_import.py import --file data/training_sets/ai_ml/example_data.json --domain-id ai_ml")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="CLI tool for importing training data into BookGen AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import single file
  python demo_manual_import.py import --file data.json --domain-id ai_ml --domain-name "AI & ML"
  
  # Import with niche
  python demo_manual_import.py import --file data.json --domain-id ai_ml --domain-name "AI & ML" --niche-id nlp --niche-name "Natural Language Processing"
  
  # Import directory
  python demo_manual_import.py import-dir --directory ./data/ai_ml --domain-id ai_ml --domain-name "AI & ML"
  
  # List all datasets
  python demo_manual_import.py list
  
  # Get statistics
  python demo_manual_import.py stats --domain-id ai_ml
  
  # Clear data
  python demo_manual_import.py clear --domain-id ai_ml
  
  # Create example files
  python demo_manual_import.py create-examples
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import training data from JSON file')
    import_parser.add_argument('--file', required=True, help='Path to JSON file')
    import_parser.add_argument('--domain-id', required=True, help='Domain ID')
    import_parser.add_argument('--domain-name', required=True, help='Domain display name')
    import_parser.add_argument('--niche-id', help='Niche ID (optional)')
    import_parser.add_argument('--niche-name', help='Niche display name (optional)')
    import_parser.add_argument('--source', default='data_gov', help='Data source type')
    
    # Import directory command
    import_dir_parser = subparsers.add_parser('import-dir', help='Import from directory')
    import_dir_parser.add_argument('--directory', required=True, help='Directory path')
    import_dir_parser.add_argument('--domain-id', required=True, help='Domain ID')
    import_dir_parser.add_argument('--domain-name', required=True, help='Domain display name')
    import_dir_parser.add_argument('--niche-id', help='Niche ID (optional)')
    import_dir_parser.add_argument('--niche-name', help='Niche display name (optional)')
    import_dir_parser.add_argument('--source', default='data_gov', help='Data source type')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all training datasets')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get dataset statistics')
    stats_parser.add_argument('--domain-id', required=True, help='Domain ID')
    stats_parser.add_argument('--niche-id', help='Niche ID (optional)')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear training data')
    clear_parser.add_argument('--domain-id', help='Domain ID (optional, clears all if not specified)')
    clear_parser.add_argument('--niche-id', help='Niche ID (optional)')
    
    # Create examples command
    examples_parser = subparsers.add_parser('create-examples', help='Create example training data files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check environment variables
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable is required")
        print("Set it in your .env file or export it:")
        print("export DATABASE_URL='mongodb+srv://user:pass@cluster.mongodb.net/database'")
        return
    
    # Execute commands
    if args.command == 'import':
        asyncio.run(import_training_data(
            args.file, args.domain_id, args.domain_name,
            args.niche_id, args.niche_name, args.source
        ))
    
    elif args.command == 'import-dir':
        asyncio.run(import_directory(
            args.directory, args.domain_id, args.domain_name,
            args.niche_id, args.niche_name, args.source
        ))
    
    elif args.command == 'list':
        asyncio.run(list_datasets())
    
    elif args.command == 'stats':
        asyncio.run(get_stats(args.domain_id, args.niche_id))
    
    elif args.command == 'clear':
        asyncio.run(clear_data(args.domain_id, args.niche_id))
    
    elif args.command == 'create-examples':
        create_example_files()


if __name__ == "__main__":
    main()