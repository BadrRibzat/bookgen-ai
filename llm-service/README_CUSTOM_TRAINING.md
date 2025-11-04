# 🎯 BookGen AI Custom LLM Training Service

A comprehensive custom LLM training service for fine-tuning GPT-2 models on **manually collected, domain-specific training data**. This service uses a **local JSON storage approach** for maximum control over data quality and enables domain-specific book generation with high-quality, trained language models.

## 🏗️ Architecture Overview

```
📦 llm-service/
├── 🔧 app/
│   ├── main.py                    # FastAPI service with training & inference endpoints
│   └── ml/
│       ├── data_schema.py         # MongoDB schemas for training data
│       ├── data_importer.py       # Local JSON import & quality analysis
│       └── llm_trainer.py         # GPT-2 fine-tuning & inference
├── 📊 data/training_sets/         # LOCAL JSON STORAGE (12 domains)
│   ├── README.md                  # Complete data collection guide
│   ├── template.json              # Universal data format template
│   ├── cybersecurity/
│   │   └── template.json          # Cybersecurity-specific template
│   ├── ai_ml/                     # AI & Machine Learning
│   │   └── template.json          # AI/ML-specific template
│   ├── automation/                # Automation & Productivity
│   │   └── template.json          # Automation-specific template
│   ├── healthtech/                # Health Technology
│   │   └── template.json          # HealthTech-specific template
│   ├── creator_economy/           # Creator Economy
│   │   └── template.json          # Creator Economy-specific template
│   ├── web3/                      # Web3 & Blockchain
│   │   └── template.json          # Web3-specific template
│   ├── ecommerce/                 # E-commerce
│   │   └── template.json          # E-commerce-specific template
│   ├── data_analytics/            # Data Analytics
│   │   └── template.json          # Data Analytics-specific template
│   ├── gaming/                    # Gaming
│   │   └── template.json          # Gaming-specific template
│   ├── kids_parenting/            # Kids & Parenting
│   │   └── template.json          # Kids/Parenting-specific template
│   ├── nutrition/                 # Nutrition & Wellness
│   │   └── template.json          # Nutrition-specific template
│   └── recipes/                   # Recipes & Cooking
│       └── template.json          # Recipes-specific template
├── 🤖 models/                     # Trained model storage
├── 📄 output/                     # Generated content output
├── 🛠️ demo_manual_import.py       # CLI tool for importing local JSON files
├── 🔍 validate_data.py            # JSON validation and quality check tool
├── ⚙️ .env                        # Environment configuration
└── 📋 requirements.txt            # Python dependencies
```

## 🚀 Key Features

### 🎓 Custom LLM Training
- **Fine-tuned GPT-2**: Lightweight, fast inference
- **Domain-specific models**: Trained for each of 12 business domains
- **Quality-scored training data**: Automatic quality assessment
- **Subscription-tier support**: Basic, Professional, Enterprise content generation

### 📥 Local JSON Data Management
- **Manual data collection**: Complete control over training data quality
- **12 domain structure**: Organized folders with domain-specific templates
- **Subscription tiers**: Basic (1-3), Professional (4-7), Enterprise (8-10) difficulty levels
- **Quality validation**: Comprehensive JSON validation and content scoring

### 🔄 Training Pipeline
- **Background training**: Non-blocking model training
- **Progress tracking**: Real-time training progress
- **Checkpoint management**: Automatic model saving
- **Performance metrics**: Loss tracking and model evaluation

### 🎨 Text Generation
- **Domain-aware generation**: Use trained models for specific domains
- **Subscription-tier generation**: Content complexity based on user tier
- **Configurable parameters**: Temperature, top-p, top-k controls
- **Quality filtering**: Repetition penalty and length controls

## 🔧 Setup Instructions

### 1. Environment Configuration

The service uses the same MongoDB connection as the backend:

```bash
# Configure in your .env file (DO NOT commit actual credentials)
DATABASE_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=<app-name>
MONGODB_DB_NAME=app_name
```

> **⚠️ SECURITY NOTE**: Never commit actual MongoDB credentials to your repository. Always use environment variables and keep your `.env` file in `.gitignore`.

### 2. Install Dependencies

```bash
cd llm-service
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Validate and Prepare Training Data

```bash
# Follow the comprehensive data collection guide
cat data/training_sets/README.md

# Validate your collected data before importing
python validate_data.py --all

# Validate specific domain
python validate_data.py --domain cybersecurity

# Validate single file
python validate_data.py --path data/training_sets/cybersecurity/vulnerabilities_1.json
```

## 📊 Supported Domains

| Domain ID | Display Name | Description |
|-----------|--------------|-------------|
| `ai_ml` | AI & Machine Learning | Artificial intelligence, neural networks, deep learning |
| `automation` | Automation & Productivity | Business automation, workflow optimization |
| `healthtech` | Health Technology | Digital health, medical devices, telemedicine |
| `cybersecurity` | Cybersecurity | Information security, threat protection |
| `creator_economy` | Creator Economy | Content creation, digital entrepreneurship |
| `web3` | Web3 & Blockchain | Cryptocurrency, NFTs, decentralized applications |
| `ecommerce` | E-commerce | Online retail, digital commerce |
| `data_analytics` | Data Analytics | Business intelligence, data science |
| `gaming` | Gaming | Video game development, gaming industry |
| `kids_parenting` | Kids & Parenting | Child development, parenting advice |
| `nutrition` | Nutrition & Wellness | Healthy eating, nutritional science |
| `recipes` | Recipes & Cooking | Culinary arts, recipe development |

## 🛠️ Usage Guide

### 1. Start the LLM Service

```bash
# Start the FastAPI service
uvicorn app.main:app --reload --port 8001
```

### 2. Import Training Data

#### Prerequisites: Data Collection
First, you need to manually collect and create training data files following the format in `data/training_sets/README.md`. Place your JSON files in the appropriate domain folders.

#### Using CLI Tool (Recommended)

```bash
# Import single file
python demo_manual_import.py import \
  --file data/training_sets/cybersecurity/vulnerabilities_1.json \
  --domain-id cybersecurity \
  --domain-name "Cybersecurity"

# Import entire directory (after you've added your data files)
python demo_manual_import.py import-dir \
  --directory data/training_sets/cybersecurity \
  --domain-id cybersecurity \
  --domain-name "Cybersecurity"

# List all datasets
python demo_manual_import.py list

# Get statistics
python demo_manual_import.py stats --domain-id cybersecurity
```

#### Using API Endpoints

```bash
# Import file via API
curl -X POST http://localhost:8001/data/import/file \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "data/training_sets/cybersecurity/vulnerabilities_1.json",
    "domain_id": "cybersecurity",
    "domain_name": "Cybersecurity",
    "content_type": "manual_collection"
  }'
```

### 3. Train Custom Models

```bash
# Start training via API
curl -X POST http://localhost:8001/train \
  -H "Content-Type: application/json" \
  -d '{
    "domain_id": "cybersecurity",
    "job_name": "Cybersecurity Model Training",
    "epochs": 3,
    "batch_size": 4,
    "learning_rate": 5e-5
  }'

# Check training status
curl http://localhost:8001/train/status/{job_id}
```

### 4. Generate Content

```bash
# Generate text using trained model
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the main cybersecurity threats in 2024?",
    "domain_id": "cybersecurity",
    "max_length": 500,
    "temperature": 0.8
  }'
```

## 📝 Data Format

Training data should follow this JSON format (see `data/training_sets/README.md` for complete guide):

```json
{
  "domain": "cybersecurity",
  "description": "Training data for cybersecurity domain",
  "version": "1.0.0",
  "total_examples": 100,
  "subscription_tiers": {
    "basic": {
      "system_prompt": "You are a cybersecurity assistant for beginners...",
      "max_complexity": 3,
      "target_audience": "beginners"
    },
    "professional": {
      "system_prompt": "You are a cybersecurity expert...",
      "max_complexity": 7,
      "target_audience": "professionals"
    },
    "enterprise": {
      "system_prompt": "You are a senior cybersecurity consultant...",
      "max_complexity": 10,
      "target_audience": "enterprise_leaders"
    }
  },
  "training_examples": [
    {
      "id": "cyber_001",
      "input": "What is a SQL injection attack?",
      "output": "SQL injection is a code injection technique...",
      "context": "Web application security fundamentals",
      "difficulty_level": 3,
      "subscription_tier": "basic",
      "tags": ["sql_injection", "web_security"],
      "quality_score": 9.0,
      "metadata": {
        "source": "manual_creation",
        "created_at": "2024-01-01T00:00:00Z",
        "validated": true,
        "token_count": 120
      }
    }
  ]
}
```

### Required Fields
- `domain`: Must match folder name exactly
- `input`: Question/prompt (min 10 characters)
- `output`: Expected response (min 20 characters)
- `difficulty_level`: 1-10 (1=beginner, 10=expert)
- `subscription_tier`: "basic", "professional", or "enterprise"
- `quality_score`: 0-10 quality rating

### Subscription Tier Guidelines
- **Basic (1-3)**: Simple explanations for beginners
- **Professional (4-7)**: Technical details for practitioners  
- **Enterprise (8-10)**: Strategic guidance for decision-makers

## 🔍 API Endpoints

### Training Data Management
- `POST /data/import/file` - Import JSON training data file
- `POST /data/import/directory` - Import all JSON files in directory
- `POST /data/examples` - Add single training example
- `GET /data/stats?domain_id={id}` - Get dataset statistics
- `GET /data/domains` - List all available domains
- `DELETE /data/clear` - Clear training data

### Model Training
- `POST /train` - Start training job
- `GET /train/status/{job_id}` - Get training status
- `GET /train/jobs` - List training jobs
- `GET /models` - List available models

### Text Generation
- `POST /generate` - Generate text using trained model

### Utility
- `GET /health` - Service health check
- `GET /status/system` - Comprehensive system status
- `GET /supported-domains` - List supported domains
- `GET /template/training-data` - Get training data template

## 📈 Training Pipeline

### 1. Data Preparation
- Quality scoring and validation
- Text preprocessing and tokenization
- Train/validation split (80/20)

### 2. Model Training
- GPT-2 base model fine-tuning
- Configurable hyperparameters
- Automatic checkpoint saving
- Progress tracking and logging

### 3. Model Management
- Automatic model versioning
- Performance metrics tracking
- Model artifact storage
- Usage statistics

## 🎯 Next Steps

### For Manual Data Collection:
1. **Read the Data Collection Guide**: `cat data/training_sets/README.md`
2. **Choose Target Domains**: Start with 3-4 domains that align with your business
3. **Research and Collect**: Gather high-quality training data from reliable sources
4. **Follow JSON Format**: Use domain-specific templates as your guide
5. **Validate Data**: Use `python validate_data.py --all` before importing
6. **Import and Train**: Import validated data and start training models

### For Production Deployment:
1. **Scale training infrastructure** (GPU instances)
2. **Implement model serving** with load balancing
3. **Add model evaluation** metrics and A/B testing
4. **Implement caching** for faster inference
5. **Monitor performance** and retrain as needed

## 📊 Data Collection Targets

### Per Domain Goals:
- **Minimum**: 100 training examples
- **Good**: 500 training examples  
- **Excellent**: 1000+ training examples

### Subscription Tier Distribution:
- **Basic**: 40% of examples (difficulty 1-3)
- **Professional**: 40% of examples (difficulty 4-7)
- **Enterprise**: 20% of examples (difficulty 8-10)

### Quality Targets:
- **Average quality score**: 8.0+
- **Minimum quality score**: 6.0
- **Content diversity**: Cover all major subtopics in domain

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Training Configuration
DEFAULT_BATCH_SIZE=4
DEFAULT_LEARNING_RATE=5e-5
DEFAULT_EPOCHS=3
MAX_SEQUENCE_LENGTH=512

# Hardware Settings
DEVICE=auto  # auto, cpu, cuda
USE_FP16=true

# Storage Paths
MODELS_DIR=./models
TRAINING_DATA_DIR=./data
OUTPUT_DIR=./output

# Domain Support
SUPPORTED_DOMAINS=ai_ml,automation,healthtech,cybersecurity,creator_economy,web3,ecommerce,data_analytics,gaming,kids_parenting,nutrition,recipes
```

## 🚨 Important Notes

1. **Data Collection Required**: You need to manually collect training data for each domain
2. **Hardware Requirements**: GPU recommended for training, CPU sufficient for inference
3. **Training Time**: Varies by dataset size (typically 30 minutes to 2 hours)
4. **Model Storage**: Each trained model ~500MB-1GB depending on size
5. **Memory Usage**: 4-8GB RAM recommended during training
6. **Data Quality**: Higher quality training data = better model performance
7. **Validation First**: Always validate JSON files before importing
8. **Git Storage**: Large training data files are excluded from git (.gitignore)

## 🔗 Integration with Backend

This LLM service integrates seamlessly with the BookGen AI backend:

- **Shared MongoDB**: Uses same database connection
- **Domain Alignment**: Matches backend domain structure
- **API Compatibility**: RESTful API design
- **Authentication**: Can be extended with backend auth

The service is designed to work as a microservice in the BookGen AI ecosystem, providing custom LLM capabilities for domain-specific book generation with **manual data collection** ensuring maximum quality control over training content.