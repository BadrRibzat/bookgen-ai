#!/usr/bin/env python3
"""
MongoDB Training Data Import Example
Demonstrates how to manually import training data into MongoDB Atlas
"""

import json
import asyncio
from pathlib import Path
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def demo_manual_import():
    """Demonstrate manual data import workflow"""
    print("🔥 MongoDB Training Data Import Demo")
    print("=" * 50)
    
    # Import the service components
    try:
        from ml.preprocessing import MongoDBTrainingDataManager, ManualDataImporter
        print("✓ Successfully imported MongoDB components")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return
    
    # Create sample training data files
    print("\n📁 Creating sample training data files...")
    
    # Create temp directory
    temp_dir = Path("temp_training_data")
    temp_dir.mkdir(exist_ok=True)
    
    # Sample JSON training data
    ai_data = [
        {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
            "source": "AI Fundamentals Manual",
            "metadata": {"topic": "machine_learning_basics", "difficulty": "beginner"}
        },
        {
            "content": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information by responding to external inputs and relaying information between each node.",
            "source": "Deep Learning Guide",
            "metadata": {"topic": "neural_networks", "difficulty": "intermediate"}
        },
        {
            "content": "Natural language processing (NLP) combines computational linguistics with statistical, machine learning, and deep learning models to enable computers to process and analyze large amounts of natural language data.",
            "source": "NLP Handbook",
            "metadata": {"topic": "nlp", "difficulty": "intermediate"}
        }
    ]
    
    # Sample business data
    business_data = [
        {
            "content": "Strategic planning is the process of defining an organization's direction and making decisions on allocating resources to pursue this strategy. It involves setting goals, determining actions to achieve the goals, and mobilizing resources to execute the actions.",
            "source": "Business Strategy Manual",
            "metadata": {"topic": "strategic_planning", "industry": "general"}
        },
        {
            "content": "Digital transformation is the integration of digital technology into all areas of a business, fundamentally changing how you operate and deliver value to customers. It's also a cultural change that requires organizations to continually challenge the status quo.",
            "source": "Digital Business Guide",
            "metadata": {"topic": "digital_transformation", "industry": "technology"}
        }
    ]
    
    # Save sample files
    ai_file = temp_dir / "ai_training_data.json"
    business_file = temp_dir / "business_training_data.json"
    
    with open(ai_file, 'w', encoding='utf-8') as f:
        json.dump(ai_data, f, indent=2, ensure_ascii=False)
    
    with open(business_file, 'w', encoding='utf-8') as f:
        json.dump(business_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created sample AI training data: {ai_file}")
    print(f"✓ Created sample business training data: {business_file}")
    
    # Sample text file
    text_file = temp_dir / "health_training_data.txt"
    health_content = """
    Preventive healthcare focuses on preventing diseases before they occur. This includes regular check-ups, vaccinations, screenings, and lifestyle modifications. 
    
    The importance of nutrition cannot be overstated in maintaining good health. A balanced diet provides essential nutrients that support bodily functions and help prevent chronic diseases.
    
    Regular physical exercise is crucial for maintaining cardiovascular health, strengthening muscles and bones, and improving mental well-being. The World Health Organization recommends at least 150 minutes of moderate-intensity exercise per week.
    
    Mental health is just as important as physical health. Stress management techniques, adequate sleep, and social connections all contribute to overall well-being.
    """
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(health_content)
    
    print(f"✓ Created sample health training text: {text_file}")
    
    # Create CSV sample
    csv_file = temp_dir / "technology_training_data.csv"
    csv_content = """content,source,category
"Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the Internet.","Cloud Computing Guide","infrastructure"
"Cybersecurity involves protecting systems, networks, and programs from digital attacks. These attacks usually aim to access, change, or destroy sensitive information.","Security Handbook","security"
"Internet of Things (IoT) refers to the network of physical devices, vehicles, home appliances, and other items embedded with electronics, software, sensors, and connectivity.","IoT Overview","connectivity"
"""
    
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print(f"✓ Created sample technology training CSV: {csv_file}")
    
    print("\n🔧 MongoDB Configuration")
    print("To use this with your MongoDB Atlas:")
    print("1. Set your MONGODB_URL environment variable:")
    print("   export MONGODB_URL='mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>'")
    print("2. Or create a .env file with:")
    print("   MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>")
    
    # Check if MongoDB URL is available
    mongodb_url = os.getenv('MONGODB_URL')
    if not mongodb_url:
        print("\n⚠️  MongoDB URL not found in environment variables")
        print("Please set MONGODB_URL to test the import functionality")
        print("\n📂 Sample files created in:", temp_dir.absolute())
        print("\n💡 Manual Import Commands (after setting MONGODB_URL):")
        print(f"   python -m app.ml.service import --file '{ai_file}' --domain 'artificial intelligence' --niche 'machine learning'")
        print(f"   python -m app.ml.service import --file '{business_file}' --domain 'business' --niche 'strategy'")
        print(f"   python -m app.ml.service import --file '{health_file}' --domain 'health' --niche 'preventive care'")
        return
    
    print(f"\n✓ Found MongoDB URL: {mongodb_url[:50]}...")
    
    try:
        # Initialize MongoDB manager
        print("\n🔗 Connecting to MongoDB...")
        mongodb_manager = MongoDBTrainingDataManager(mongodb_url)
        await mongodb_manager.initialize()
        print("✓ Connected to MongoDB successfully")
        
        # Initialize data importer
        data_importer = ManualDataImporter(mongodb_manager)
        
        # Import AI data
        print(f"\n📥 Importing AI training data...")
        success = await data_importer.import_from_file(
            str(ai_file), "artificial intelligence", "machine learning", "manual"
        )
        print(f"✓ AI data import: {'Success' if success else 'Failed'}")
        
        # Import business data
        print(f"\n📥 Importing business training data...")
        success = await data_importer.import_from_file(
            str(business_file), "business", "strategy", "manual"
        )
        print(f"✓ Business data import: {'Success' if success else 'Failed'}")
        
        # Import health data
        print(f"\n📥 Importing health training data...")
        success = await data_importer.import_from_file(
            str(text_file), "health", "preventive care", "manual"
        )
        print(f"✓ Health data import: {'Success' if success else 'Failed'}")
        
        # Import technology data
        print(f"\n📥 Importing technology training data...")
        success = await data_importer.import_from_file(
            str(csv_file), "technology", "infrastructure", "manual"
        )
        print(f"✓ Technology data import: {'Success' if success else 'Failed'}")
        
        # Get statistics
        print(f"\n📊 Getting training data statistics...")
        stats = await mongodb_manager.get_training_stats()
        
        print(f"\n📈 Training Data Summary:")
        print(f"   Total Examples: {stats.get('total_examples', 0)}")
        print(f"   Domain Breakdown:")
        for item in stats.get('domain_breakdown', []):
            domain = item['_id']['domain']
            niche = item['_id']['niche'] or 'general'
            count = item['count']
            avg_words = item.get('avg_words', 0)
            print(f"     - {domain}/{niche}: {count} examples (avg {avg_words:.0f} words)")
        
        print(f"\n🎉 Manual data import demonstration completed!")
        print(f"\n🚀 Next Steps:")
        print(f"   1. Train model: python -m app.ml.service train --domain 'artificial intelligence' --niche 'machine learning'")
        print(f"   2. Generate book: python -m app.ml.service generate --domain 'artificial intelligence' --niche 'machine learning'")
        
    except Exception as e:
        print(f"\n❌ Error during MongoDB operations: {e}")
        print("Please check your MongoDB connection and credentials")
    
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary files...")
        for file in temp_dir.glob("*"):
            file.unlink()
        temp_dir.rmdir()
        print("✓ Cleanup completed")


if __name__ == "__main__":
    asyncio.run(demo_manual_import())