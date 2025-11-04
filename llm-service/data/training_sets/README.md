# 📊 LLM Training Data Collection Guide

> **Complete guide for collecting and organizing training data for all 12 domains**

## 🎯 **Overview**

This guide provides everything you need to collect, format, and organize training data for BookGen AI's custom LLM training system. The system supports **12 specialized domains** with **3 subscription tiers** each.

## 📁 **Directory Structure**

```
llm-service/data/training_sets/
├── cybersecurity/
│   ├── template.json          # Domain template (DO NOT EDIT)
│   ├── vulnerabilities_1.json # Your training data files
│   ├── attack_patterns_2.json
│   └── security_tools_3.json
├── ai_ml/
│   ├── template.json
│   ├── algorithms_1.json      
│   ├── deep_learning_2.json
│   └── nlp_research_3.json
├── automation/
├── healthtech/
├── creator_economy/
├── web3/
├── ecommerce/
├── data_analytics/
├── gaming/
├── kids_parenting/
├── nutrition/
└── recipes/
```

## 🎯 **Supported Domains**

| Domain | Focus Areas | Target Audience |
|--------|-------------|-----------------|
| **cybersecurity** | Vulnerabilities, threats, security practices | Security professionals, beginners |
| **ai_ml** | Machine learning, AI research, implementations | Data scientists, developers |
| **automation** | RPA, workflow optimization, process improvement | Business analysts, engineers |
| **healthtech** | Medical devices, digital health, telemedicine | Healthcare professionals, patients |
| **creator_economy** | Content monetization, platform strategies | Content creators, influencers |
| **web3** | Blockchain, cryptocurrency, DeFi, NFTs | Crypto enthusiasts, developers |
| **ecommerce** | Online retail, marketplaces, conversion optimization | E-commerce businesses |
| **data_analytics** | Business intelligence, data science, visualization | Data analysts, business users |
| **gaming** | Game development, industry trends, monetization | Game developers, industry professionals |
| **kids_parenting** | Child development, parenting advice, education | Parents, childcare professionals |
| **nutrition** | Dietary guidance, health optimization, supplements | Health enthusiasts, professionals |
| **recipes** | Cooking techniques, recipe development, culinary arts | Home cooks, professional chefs |

## 📋 **JSON File Format**

### **Required Structure**
Every training data file must follow this structure:

```json
{
  "domain": "DOMAIN_NAME",
  "description": "Description of this training data file",
  "version": "1.0.0",
  "total_examples": 100,
  "subscription_tiers": {
    "basic": {
      "system_prompt": "You are a DOMAIN assistant for beginners...",
      "max_complexity": 3,
      "target_audience": "beginners"
    },
    "professional": {
      "system_prompt": "You are a DOMAIN expert...",
      "max_complexity": 7,
      "target_audience": "professionals"
    },
    "enterprise": {
      "system_prompt": "You are a senior DOMAIN consultant...",
      "max_complexity": 10,
      "target_audience": "enterprise_leaders"
    }
  },
  "training_examples": [
    {
      "id": "unique_example_001",
      "input": "Question or prompt for the AI",
      "output": "Expected response from the AI",
      "context": "Background context for this example",
      "difficulty_level": 3,
      "subscription_tier": "basic",
      "tags": ["tag1", "tag2", "tag3"],
      "quality_score": 8.5,
      "metadata": {
        "source": "manual_creation",
        "created_at": "2024-01-01T00:00:00Z",
        "validated": true,
        "token_count": 150,
        "category": "specific_category"
      }
    }
  ]
}
```

### **Field Descriptions**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | ✅ | Must match folder name exactly |
| `description` | string | ✅ | What this training data contains |
| `version` | string | ✅ | Version number (e.g., "1.0.0") |
| `total_examples` | number | ✅ | Count of training examples |
| `subscription_tiers` | object | ✅ | Configuration for basic/professional/enterprise |
| `training_examples` | array | ✅ | Array of training examples |

### **Training Example Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier (e.g., "cyber_001") |
| `input` | string | ✅ | Question/prompt (min 10 chars) |
| `output` | string | ✅ | Expected response (min 20 chars) |
| `context` | string | ✅ | Background context |
| `difficulty_level` | number | ✅ | 1-10 (1=beginner, 10=expert) |
| `subscription_tier` | string | ✅ | "basic", "professional", or "enterprise" |
| `tags` | array | ✅ | Relevant tags for categorization |
| `quality_score` | number | ✅ | 0-10 quality rating |
| `metadata` | object | ✅ | Additional information |

## 🎯 **Subscription Tier Guidelines**

### **Basic Tier (Difficulty 1-3)**
- **Target**: Beginners, general public
- **Content**: Simple explanations, basic concepts
- **Style**: Clear, jargon-free, with analogies
- **Examples**: "What is...", "How to start...", "Basic guide to..."

### **Professional Tier (Difficulty 4-7)**
- **Target**: Industry professionals, practitioners
- **Content**: Technical details, implementation guides
- **Style**: Professional terminology, step-by-step processes
- **Examples**: "How to implement...", "Best practices for...", "Advanced techniques..."

### **Enterprise Tier (Difficulty 8-10)**
- **Target**: Executive decision-makers, strategists
- **Content**: Strategic guidance, compliance, governance
- **Style**: Executive-level insights, ROI considerations
- **Examples**: "Strategic approach to...", "Enterprise governance for...", "C-level guide to..."

## 📊 **Data Collection Sources**

### **High-Quality Sources by Domain**

#### 🔒 **Cybersecurity**
- CVE Database (cve.mitre.org)
- MITRE ATT&CK Framework
- NIST Cybersecurity Framework
- OWASP Documentation
- Security research papers
- Incident response case studies

#### 🤖 **AI/ML**
- ArXiv AI/ML papers
- Hugging Face documentation
- TensorFlow/PyTorch tutorials
- Kaggle competitions and datasets
- University ML course materials
- AI research blogs (OpenAI, DeepMind)

#### ⚡ **Automation**
- RPA vendor documentation
- Workflow automation platforms
- DevOps best practices
- Business process optimization guides
- Integration platform documentation
- Automation case studies

#### 🏥 **HealthTech**
- FDA medical device guidelines
- HIPAA compliance resources
- Healthcare interoperability standards
- Medical AI research papers
- Telemedicine platform documentation
- Clinical trial technology

#### 💰 **Creator Economy**
- Platform creator guidelines
- Monetization strategy studies
- Creator economy reports
- Platform analytics documentation
- Brand partnership case studies
- Creator tool documentation

#### 🌐 **Web3**
- Blockchain whitepapers
- DeFi protocol documentation
- Smart contract tutorials
- Cryptocurrency exchange guides
- Web3 development frameworks
- Regulatory compliance guides

#### 🛒 **E-commerce**
- E-commerce platform documentation
- Conversion optimization studies
- Payment processor guides
- Marketplace seller resources
- Digital marketing case studies
- Customer experience research

#### 📈 **Data Analytics**
- BI tool documentation
- Statistical analysis guides
- Data visualization best practices
- SQL tutorial resources
- Analytics platform guides
- Data science competition solutions

#### 🎮 **Gaming**
- Game development documentation
- Gaming industry reports
- Game engine tutorials
- Monetization strategy guides
- Esports industry analysis
- Game design principles

#### 👶 **Kids/Parenting**
- Child development research
- Pediatric guidelines
- Educational resource materials
- Parenting strategy studies
- Child psychology research
- Family wellness guides

#### 🥗 **Nutrition**
- USDA nutrition guidelines
- Scientific nutrition research
- Dietary pattern studies
- Sports nutrition resources
- Medical nutrition therapy guides
- Food safety documentation

#### 🍳 **Recipes**
- Culinary technique guides
- Professional cooking resources
- Food science principles
- Recipe development methodologies
- Culinary school curricula
- Professional chef techniques

## 📝 **File Naming Convention**

Use descriptive names that indicate content:

```
domain_topic_number.json

Examples:
- cybersecurity_vulnerabilities_1.json
- cybersecurity_penetration_testing_2.json
- ai_ml_deep_learning_1.json
- ai_ml_nlp_transformers_2.json
- automation_rpa_implementation_1.json
- healthtech_telemedicine_platforms_1.json
```

## ✅ **Quality Guidelines**

### **Content Quality**
- ✅ Accurate and up-to-date information
- ✅ Clear, well-structured responses
- ✅ Appropriate for target subscription tier
- ✅ Diverse range of topics within domain
- ✅ Natural question-answer flow

### **Technical Quality**
- ✅ Valid JSON format
- ✅ All required fields present
- ✅ Unique example IDs
- ✅ Appropriate difficulty levels
- ✅ Relevant tags and metadata

### **Avoid**
- ❌ Outdated information
- ❌ Overly promotional content
- ❌ Duplicate examples
- ❌ Inappropriate difficulty assignment
- ❌ Missing required fields

## 🔧 **Validation Tools**

### **Before Training - Validate Your Data**

```bash
# Validate all domains
python validate_data.py --all

# Validate specific domain
python validate_data.py --domain cybersecurity

# Validate single file
python validate_data.py --path data/training_sets/cybersecurity/vulnerabilities_1.json

# Verbose validation
python validate_data.py --all --verbose
```

### **Validation Checks**
- ✅ JSON syntax validation
- ✅ Required field validation
- ✅ Data type validation
- ✅ Domain consistency
- ✅ Unique ID validation
- ✅ Content length validation
- ✅ Quality score ranges

## 🎯 **Target Metrics**

### **Per Domain Goals**
- **Minimum**: 100 training examples
- **Good**: 500 training examples
- **Excellent**: 1000+ training examples

### **Subscription Tier Distribution**
- **Basic**: 40% of examples (difficulty 1-3)
- **Professional**: 40% of examples (difficulty 4-7)
- **Enterprise**: 20% of examples (difficulty 8-10)

### **Quality Targets**
- **Average quality score**: 8.0+
- **Minimum quality score**: 6.0
- **Content diversity**: Cover all major subtopics

## 📋 **Progress Tracking**

### **Checklist Template**
```
□ Domain: [DOMAIN_NAME]
□ Topic areas identified
□ Source materials collected
□ Template file reviewed
□ Training examples created
□ JSON format validated
□ Quality scores assigned
□ Difficulty levels distributed
□ Subscription tiers balanced
□ Final validation passed
```

## 🚀 **Ready for Training**

Once you've collected data for all desired domains:

1. **Validate everything**: `python validate_data.py --all`
2. **Check metrics**: Ensure you have sufficient examples per domain
3. **Notify for review**: Let the development team know data is ready
4. **Begin training**: Run the training pipeline

## 📞 **Need Help?**

If you encounter issues:

1. **Validation errors**: Check the error messages and fix JSON format
2. **Content questions**: Refer to domain-specific template files
3. **Technical issues**: Use the validation tools to diagnose problems
4. **Quality concerns**: Aim for clarity, accuracy, and appropriate complexity

## 🎉 **Success Criteria**

Your data collection is ready when:
- ✅ All JSON files pass validation
- ✅ Each domain has 100+ examples
- ✅ Subscription tiers are properly distributed
- ✅ Quality scores average 8.0+
- ✅ Content covers diverse subtopics
- ✅ All domains you want to train are complete

**Happy data collecting! 🚀**