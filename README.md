# 📚 BookGen-AI

> **AI-Powered SaaS Book Generation Platform**  
> Transform your ideas into professionally formatted books with the power of artificial intelligence.

## 👨‍💻 About the Developer

**Badr Ribzat** - Self-Taught Full-Stack Software Engineer from Morocco

📧 **Contact**: [badrribzat@gmail.com](mailto:badrribzat@gmail.com)  
🌐 **Portfolio**: [https://badr-portfolio.vercel.app](https://badr-portfolio.vercel.app)

### Professional Background
- **Self-taught Full-Stack Software Engineer** available for opportunities and collaborations
- **Experience across multiple domains**: Biomedical, Teaching IT, AI/Chatbot Development
- **Notable Projects**: 
  - Biomedical-AI Human Body Detection System
  - IT-Learning Platform
  - Internationalization Portfolio 
  - Resume Generator SaaS Platform
  - AI-Powered Chatbot Systems

🤝 **Available for**: Opportunities, collaborations, and technical discussions with companies across various industries

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.9+-red.svg)](https://pytorch.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/)

---

## 🌟 Features

### ✅ Current Implementation (Production Ready)

#### 🔐 **Complete Authentication System**
- JWT-based authentication with refresh tokens
- Email verification and password reset workflows
- Secure user registration with validation
- Session management and logout functionality

#### 👤 **Advanced User Management**
- Extended user profiles with subscription tiers
- User analytics and activity tracking
- Profile customization and preferences
- Role-based access control

#### 📖 **Intelligent Book Generation**
- Multi-step book creation wizard with progress tracking
- Real-time form validation with Zod schemas
- Genre-specific content templates
- Professional book metadata management

#### 🤖 **Custom LLM Training Service**
- **Local JSON Storage Infrastructure** - Complete 12-domain data organization
- **Manual Data Collection Workflow** - Quality-controlled training data
- **Subscription-Tier Support** - Basic, Professional, Enterprise content generation
- **MongoDB Atlas Integration** - Production-ready database storage
- **GPT-2 Fine-tuning** - Domain-specific model customization
- **Data Validation Tools** - Comprehensive JSON validation and quality checks
- **Background Training Pipeline** - Async model training with progress tracking

#### 📄 **Professional PDF Generation**
- High-quality book formatting with ReportLab
- Custom templates and styling options
- Automated table of contents and indexing
- Professional typography and layout

#### 🏗️ **Robust Infrastructure**
- Celery async task processing
- Redis message broker and caching
- Comprehensive error handling
- Production-ready logging and monitoring

### 🔄 Coming Soon
- **Manual Data Collection** - Research and collect high-quality training data
- **Rich Book Editing** - Advanced text editor for content refinement
- **AI Cover Generation** - Automated professional book covers  
- **PDF Browser Preview** - In-browser PDF viewing and downloading
- **Payment Integration** - Subscription and billing management
- **Multi-language Support** - Internationalization features

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js Frontend] --> B[TypeScript Components]
        B --> C[Tailwind CSS Styling]
        C --> D[Authentication Context]
    end
    
    subgraph "API Gateway"
        E[Django REST API] --> F[JWT Authentication]
        F --> G[User Management]
        G --> H[Book CRUD Operations]
    end
    
    subgraph "AI Processing Layer"
        I[FastAPI LLM Service] --> J[Local JSON Storage]
        J --> K[Data Validation Tool]
        K --> L[MongoDB Atlas Storage]
        L --> M[GPT-2 Fine-tuning]
        M --> N[Subscription-Tier Generation]
        N --> O[Domain-Specific Models]
    end
    
    subgraph "Data & Infrastructure"
        P[PostgreSQL] --> Q[User Data]
        R[MongoDB Atlas] --> S[Training Data]
        T[Redis] --> U[Caching & Tasks]
        V[Celery] --> W[Async Processing]
    end
    
    A --> E
    E --> I
    I --> R
    E --> P
    E --> T
    T --> V
```

---

## 📁 Project Structure

```
bookgen-ai/
├── 🎨 frontend/                    # Next.js Application
│   ├── app/                        # App Router pages
│   │   ├── auth/                   # Authentication flows
│   │   ├── dashboard/              # User dashboard
│   │   └── api/                    # API routes
│   ├── components/                 # Reusable UI components
│   │   ├── auth/                   # Auth-specific components
│   │   ├── ui/                     # Base UI components
│   │   └── layout/                 # Layout components
│   ├── lib/                        # Utilities and configurations
│   │   ├── api/                    # API client functions
│   │   ├── contexts/               # React contexts
│   │   ├── hooks/                  # Custom React hooks
│   │   └── validation/             # Zod schemas
│   └── shared/types/               # TypeScript type definitions
│
├── 🔧 backend/                     # Django REST API
│   ├── apps/                       # Django applications
│   │   ├── users/                  # User management
│   │   ├── core/                   # Core functionality
│   │   └── books/                  # Book management
│   ├── config/                     # Django configuration
│   ├── tests/                      # Backend test suites
│   └── templates/                  # Email templates
│
├── 🤖 llm-service/                 # FastAPI AI Service
│   ├── app/                        # FastAPI application
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── ml/                     # Machine learning modules
│   │   │   ├── data_schema.py      # MongoDB schemas
│   │   │   ├── data_importer.py    # Local JSON import & validation
│   │   │   └── llm_trainer.py      # GPT-2 fine-tuning
│   │   ├── models/                 # Pydantic models
│   │   └── api/                    # API route handlers
│   ├── data/training_sets/         # Local JSON storage (12 domains)
│   │   ├── README.md               # Complete data collection guide
│   │   ├── template.json           # Universal data format template
│   │   ├── cybersecurity/          # Cybersecurity training data
│   │   │   └── template.json       # Domain-specific template
│   │   ├── ai_ml/                  # AI/ML training data
│   │   │   └── template.json       # Domain-specific template
│   │   ├── automation/             # Automation training data
│   │   ├── healthtech/             # HealthTech training data
│   │   ├── creator_economy/        # Creator Economy training data
│   │   ├── web3/                   # Web3 training data
│   │   ├── ecommerce/              # E-commerce training data
│   │   ├── data_analytics/         # Data Analytics training data
│   │   ├── gaming/                 # Gaming training data
│   │   ├── kids_parenting/         # Kids/Parenting training data
│   │   ├── nutrition/              # Nutrition training data
│   │   └── recipes/                # Recipes training data
│   ├── tests/                      # LLM service tests
│   ├── demo_manual_import.py       # CLI import tool for local JSON
│   ├── validate_data.py            # JSON validation and quality check tool
│   ├── requirements.txt            # Python dependencies
│   ├── README_CUSTOM_TRAINING.md   # Complete documentation
│   └── IMPLEMENTATION_COMPLETE.md  # Implementation summary
│
├── 📋 shared/                      # Shared resources
│   └── types/                      # Common TypeScript types
│
├── 🛠️ scripts/                     # Automation scripts
│   ├── setup.sh                   # Development setup
│   ├── run-tests.sh               # Test runner
│   └── seed-db.sh                 # Database seeding
│
├── 📋 docs/                        # Documentation
│   ├── LLM_SERVICE_COMPLETE.md    # LLM service documentation
│   └── IMPLEMENTATION_CHECKLIST.md # Implementation tracking
│
└── 🐳 docker-compose.yml           # Development environment
```

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended for full setup)
- **Node.js 18+** and npm/yarn
- **Python 3.11+** with pip
- **Git** for version control

### 🐳 Automated Docker Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/BadrRibzat/bookgen-ai.git
cd bookgen-ai

# Make setup script executable and run
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 🔧 Manual Development Setup

#### 1. Backend (Django) Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

#### 2. Frontend (Next.js) Setup
```bash
cd frontend
npm install
npm run dev
```

#### 3. LLM Service (FastAPI) Setup
```bash
cd llm-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify local JSON storage infrastructure
ls data/training_sets/

# Start the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### � Service URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **LLM Service**: http://localhost:8002
- **LLM API Docs**: http://localhost:8002/docs

---

## 🧪 Testing & Quality Assurance

### Run All Tests
```bash
# Automated test runner
./scripts/run-tests.sh

# Individual service tests
cd backend && python manage.py test
cd frontend && npm test
cd llm-service && python test_setup.py
```

### Test Coverage
- **Backend**: Django TestCase, pytest, factory-boy
- **Frontend**: Jest, React Testing Library, Playwright E2E
- **LLM Service**: pytest-asyncio, FastAPI TestClient
- **Integration**: End-to-end workflow testing

---

## 🤖 LLM Service Implementation

### Core Features
- **Local JSON Storage Infrastructure**: Complete 12-domain data organization with templates
- **Manual Data Collection**: Quality-controlled training data collection workflow
- **MongoDB Atlas Integration**: Production database for training data storage
- **GPT-2 Fine-tuning**: Lightweight, efficient model customization
- **Subscription-Tier Support**: Basic, Professional, Enterprise content generation
- **Data Validation Tools**: Comprehensive JSON validation and quality checking
- **Background Training Pipeline**: Async model training with progress tracking

### Data Collection Workflow
```bash
# 1. Read the comprehensive data collection guide
cat llm-service/data/training_sets/README.md

# 2. Validate your training data before importing
cd llm-service
python validate_data.py --all

# 3. Import validated training data
python demo_manual_import.py import-dir \
  --directory data/training_sets/cybersecurity \
  --domain-id cybersecurity

# 4. Train custom model
curl -X POST "http://localhost:8002/train" \
  -H "Content-Type: application/json" \
  -d '{"domain_id": "cybersecurity", "job_name": "Cybersecurity Model Training", "epochs": 3}'

# 5. Generate domain-specific content
curl -X POST "http://localhost:8002/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the main cybersecurity threats in 2024?", "domain_id": "cybersecurity"}'
```

### Supported Domains & Templates
All 12 domains have dedicated folder structure with domain-specific JSON templates:

| Domain | Folder | Focus Areas |
|--------|--------|-------------|
| **Cybersecurity** | `cybersecurity/` | Vulnerabilities, threats, security practices |
| **AI & ML** | `ai_ml/` | Machine learning, AI research, implementations |
| **Automation** | `automation/` | RPA, workflow optimization, process improvement |
| **HealthTech** | `healthtech/` | Medical devices, digital health, telemedicine |
| **Creator Economy** | `creator_economy/` | Content monetization, platform strategies |
| **Web3** | `web3/` | Blockchain, cryptocurrency, DeFi, NFTs |
| **E-commerce** | `ecommerce/` | Online retail, marketplaces, conversion optimization |
| **Data Analytics** | `data_analytics/` | Business intelligence, data science, visualization |
| **Gaming** | `gaming/` | Game development, industry trends, monetization |
| **Kids/Parenting** | `kids_parenting/` | Child development, parenting advice, education |
| **Nutrition** | `nutrition/` | Dietary guidance, health optimization, supplements |
| **Recipes** | `recipes/` | Cooking techniques, recipe development, culinary arts |

### Local JSON Storage Format
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
      "difficulty_level": 3,
      "subscription_tier": "basic",
      "quality_score": 9.0
    }
  ]
}
```

### ✅ Implementation Example: Cybersecurity Domain

**Real-world data processing implementation with 5 authoritative sources:**

```bash
# Data Sources Integrated (Nov 2025):
# ✓ NVD CVE Database (97 vulnerability examples)  
# ✓ MITRE ATT&CK Framework (50 threat intelligence examples)
# ✓ Ubuntu Security Notices (10 patch management examples)
# ✓ ArXiv Cryptography Research (28 academic research examples)
# ✓ Microsoft Security Updates (JSON format support)

# Processing Results:
# - 185 total training examples across all subscription tiers
# - Quality scores: 8.8-9.7/10 across all sources
# - Tier distribution: 5 basic, 125 professional, 55 enterprise

# Implementation Files:
llm-service/
├── data/
│   ├── raw_sources/cybersecurity/          # Original data files (gitignored)
│   │   ├── nvd_cve_2025.json              # NVD vulnerability data
│   │   ├── mitre_attack_enterprise.json    # MITRE ATT&CK techniques
│   │   ├── ubuntu_security_notices.xml     # Ubuntu security advisories  
│   │   ├── arxiv_crypto_papers.xml         # Academic research papers
│   │   └── microsoft_security_updates.json # Microsoft security updates
│   └── training_sets/cybersecurity/        # Processed training data
│       ├── vulnerabilities_cve_1.json      # 97 CVE examples
│       ├── threat_intelligence_mitre_1.json # 50 MITRE examples
│       ├── patch_management_ubuntu_1.json   # 10 Ubuntu examples
│       └── security_research_arxiv_1.json   # 28 research examples
├── process_cyber_data_fixed.py             # Data processor script
├── test_cybersecurity_data.py              # Quality validation
└── Cyber-Security.sh                       # Integration automation

# Validation & Quality Check:
python3 test_cybersecurity_data.py
# ✅ 185 training examples ready
# ✅ All subscription tiers represented  
# ✅ High quality scores (8.8-9.7/10)
# ✅ Multiple authoritative data sources
```

**Key Implementation Features:**
- **Multi-format Processing**: Handles JSON (CVE, MITRE), XML (Ubuntu, ArXiv), RSS feeds
- **Intelligent Tier Assignment**: Automatic difficulty scoring based on CVSS, complexity
- **Quality Validation**: Comprehensive data structure and content validation
- **Production Ready**: Fully processed and validated for LLM training

---

## 🔐 Environment Configuration

### Backend Environment (.env)
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/bookgen
REDIS_URL=redis://localhost:6379
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
```

### LLM Service Environment (.env)
```bash
# MongoDB Atlas (shared with backend) - DO NOT commit real credentials
DATABASE_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=<app-name>
MONGODB_DB_NAME=bookgen_ai

# Training Configuration
DEFAULT_BATCH_SIZE=4
DEFAULT_LEARNING_RATE=5e-5
DEFAULT_EPOCHS=3
MAX_SEQUENCE_LENGTH=512

# Hardware Settings
DEVICE=auto  # auto, cpu, cuda
USE_FP16=true

# Supported Domains
SUPPORTED_DOMAINS=cybersecurity,ai_ml,automation,healthtech,creator_economy,web3,ecommerce,data_analytics,gaming,kids_parenting,nutrition,recipes
```

### Frontend Environment (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_LLM_SERVICE_URL=http://localhost:8002
```

---

## 📊 Development Workflow

### Git Workflow
1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Implement Changes**: Follow coding standards and add tests
3. **Commit Changes**: Use conventional commits (feat:, fix:, docs:)
4. **Push & PR**: Open pull request with detailed description
5. **Code Review**: Address feedback and merge

### Code Quality Standards
- **Python**: Black formatting, isort imports, flake8 linting
- **TypeScript**: ESLint, Prettier, strict type checking
- **Testing**: Minimum 80% code coverage required
- **Documentation**: Inline comments and README updates

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository and create your feature branch
2. **Follow** the existing code style and conventions
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit** a pull request with a clear description

### Development Guidelines
- Use conventional commit messages
- Write comprehensive tests
- Update documentation for new features
- Follow existing architectural patterns
- Ensure all CI checks pass

---

## 📈 Roadmap

### Phase 3 (Next Phase - Manual Data Collection)
- [ ] Research and collect high-quality training data for target domains
- [ ] Validate and import training data using local JSON storage
- [ ] Train initial domain-specific models
- [ ] Test and refine content generation quality

### Phase 4 (Q1 2025)
- [ ] Rich text editor integration
- [ ] AI-powered cover generation
- [ ] Advanced PDF customization
- [ ] Multi-language support

### Phase 5 (Future)
- [ ] Payment and subscription system
- [ ] Collaboration features
- [ ] Mobile application
- [ ] Enterprise features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for transformer architecture inspiration
- **Hugging Face** for the transformers library
- **MongoDB** for Atlas database services
- **Vercel** for Next.js framework
- **Django Software Foundation** for the web framework

---

**Made with ❤️ by the BookGen-AI Team**

*Last updated: November 4, 2025*
 # � BookGen-AI

 ![BookGen-AI logo](frontend/public/favicon.svg)

 > **AI-Powered SaaS Book Generation Platform**
 > Transform your ideas into professionally formatted books with the power of artificial intelligence.

 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
 [![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
 [![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
 [![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

 ---

 ## 🌟 Features

 ### Current Implementation (Phase 1 & 2)
 - ✅ Secure Authentication (JWT + email verification)
 - ✅ User Profiles with analytics
 - ✅ Multi-step Book Generation wizard
 - ✅ FastAPI LLM service (extensible mock implementation)
 - ✅ Production-ready PDF generation pipeline

 ### Coming Soon
 - 🔄 Rich book editing UI
 - 🤖 Custom LLM fine-tuning
 - 🎨 AI cover design
 - 📄 In-browser PDF preview
 - 💳 Payment/subscription integration

 ---

 ## 🏗️ Technical Architecture

 This repository is a monorepo with three main components:

 - Backend: Django + DRF, Celery, MongoDB
 - Frontend: Next.js (App Router) + TypeScript + Tailwind
 - LLM Service: FastAPI (mock LLM for content generation)

 Other infra: Redis (broker), Cloudinary (assets), Docker Compose for local development.

 ---

 ## 📁 Project Structure (high-level)

 The project tree below is a concise overview for quick orientation — browse the repo for full details.

 ```
 bookgen-ai/
 ├── backend/                    # Django REST API
 ├── frontend/                   # Next.js application
 ├── llm-service/                # FastAPI AI service
 ├── shared/                     # Shared TypeScript types
 ├── scripts/                    # Automation scripts (setup, seeds, tests)
 └── docker-compose.yml          # Development compose file
 ```

 ---

 ## 🚀 Quick Start

 Follow these steps for a fast local development setup (Docker recommended):

 ### Prerequisites
 - Docker & Docker Compose
 - Node 18+ and npm
 - Python 3.11+
 - Git

 ### Automated setup
 ```bash
 git clone https://github.com/yourusername/bookgen-ai.git
 cd bookgen-ai
 chmod +x scripts/setup.sh
 ./scripts/setup.sh
 docker-compose up -d
 ```

 Access:
 - Frontend: http://localhost:3000
 - Backend: http://localhost:8000
 - API docs: http://localhost:8000/api/docs/

 If you prefer manual setup, the original manual steps are preserved in the repository and the `scripts/` folder.

 ---

 ## 🧪 Testing

 Run all tests locally:
 ```bash
 ./scripts/run-tests.sh
 ```

 Backend unit tests (pytest) and frontend tests (Jest/Playwright) are available.

 ---

 ## 📊 Development Workflow

 1. Create a feature branch: `git checkout -b feature/your-feature`
 2. Implement & test
 3. Commit with Conventional Commits
 4. Push and open PR

 ---

 ## 🔐 Environment

 Use `.env.example` files as templates; do not commit secrets. Key env variables are documented in the backend and frontend directories.

 ---

 ## 🤝 Contributing

 We welcome contributions. Please follow the project’s branching and commit conventions. See the CONTRIBUTING.md (if added) for details.

 ---

 ## 📝 License

 MIT — see the `LICENSE` file.

 ---

 **Made with ❤ by the BookGen-AI Team**
