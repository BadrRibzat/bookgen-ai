# 📚 BookGen-AI

> **AI-Powered SaaS Book Generation Platform**  
> Transform your ideas into professionally formatted books with the power of artificial intelligence.

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

#### 🤖 **Advanced LLM Service**
- **Manual Data Collection Workflow** - Import custom training data
- **MongoDB Atlas Integration** - Production-ready database storage
- **PEFT/LoRA Fine-tuning** - Parameter-efficient model customization
- **Multi-format Data Import** - Support for JSON, CSV, TXT files
- **Custom Model Training** - Domain-specific knowledge fine-tuning
- **Async Processing Pipeline** - High-performance training workflows

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
        I[FastAPI LLM Service] --> J[Manual Data Import]
        J --> K[MongoDB Atlas Storage]
        K --> L[PEFT/LoRA Training]
        L --> M[Custom Model Fine-tuning]
        M --> N[Book Generation Engine]
    end
    
    subgraph "Data & Infrastructure"
        O[PostgreSQL] --> P[User Data]
        Q[MongoDB Atlas] --> R[Training Data]
        S[Redis] --> T[Caching & Tasks]
        U[Celery] --> V[Async Processing]
    end
    
    A --> E
    E --> I
    I --> Q
    E --> O
    E --> S
    S --> U
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
│   │   │   ├── preprocessing.py    # Data preprocessing & import
│   │   │   ├── model.py           # Model definitions
│   │   │   ├── service.py         # ML service orchestrator
│   │   │   └── pdf_generator.py   # PDF generation engine
│   │   ├── models/                 # Pydantic models
│   │   └── api/                    # API route handlers
│   ├── data/                       # Training data storage
│   ├── tests/                      # LLM service tests
│   ├── requirements.txt            # Python dependencies
│   └── test_setup.py              # Setup verification
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
python test_setup.py  # Verify installation
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
- **Manual Data Collection**: Import custom training datasets
- **MongoDB Atlas Integration**: Production database for training data
- **PEFT/LoRA Fine-tuning**: Memory-efficient model customization
- **Multi-format Support**: JSON, CSV, TXT data import
- **Async Processing**: High-performance training pipeline
- **Professional PDF Generation**: ReportLab-based book formatting

### Training Data Workflow
```bash
# 1. Set up MongoDB connection
export MONGODB_URL='mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>'

# 2. Import training data
curl -X POST "http://localhost:8002/training/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_training_data.json" \
  -F "data_type=domain_knowledge"

# 3. Train custom model
curl -X POST "http://localhost:8002/training/start" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "custom-book-generator", "epochs": 3}'

# 4. Generate book content
curl -X POST "http://localhost:8002/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in Education", "style": "academic", "length": "comprehensive"}'
```

### Supported Data Formats
- **JSON**: Structured training data with metadata
- **CSV**: Tabular data with headers
- **TXT**: Plain text for language modeling
- **Custom**: Extensible import system

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
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>
OPENAI_API_KEY=optional-for-fallback
HUGGINGFACE_TOKEN=optional-for-model-access
MODEL_CACHE_DIR=/app/models
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

### Phase 3 (Next Quarter)
- [ ] Rich text editor integration
- [ ] AI-powered cover generation
- [ ] Advanced PDF customization
- [ ] Multi-language support

### Phase 4 (Future)
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

*Last updated: November 3, 2025*
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
