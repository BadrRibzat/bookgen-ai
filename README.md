# 📚 BookGen-AI

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
- ✅ **Secure Authentication** - JWT-based auth with email verification and password reset
- ✅ **User Profiles** - Extended profiles with subscription tiers and analytics
- ✅ **Multi-step Book Generation** - Intuitive wizard for creating books
- ✅ **Mock AI Content** - FastAPI service with comprehensive content mapping
- ✅ **Professional PDF Output** - Production-ready book generation
- ✅ **Real-time Validation** - Immediate feedback with Zod schemas

### Coming Soon
- 🔄 **Book Editing** - Rich text editor for content refinement
- 🤖 **Custom LLM Training** - Fine-tuned models for quality content
- 🎨 **AI Cover Generation** - Automated professional book covers
- 📄 **PDF Browser Preview** - In-browser PDF viewing and downloading
- 💳 **Payment Integration** - Subscription management and billing

---

## 🏗️ Technical Architecture

### Tech Stack

#### Backend
- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: MongoDB Atlas (primary), SQLite (LLM mappings)
- **Authentication**: JWT tokens with refresh mechanism
- **File Storage**: Cloudinary for PDFs and images
- **Async Tasks**: Celery with Redis broker
- **API Documentation**: DRF Spectacular (OpenAPI 3.0)

#### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form + Zod validation
- **State Management**: React Context API
- **HTTP Client**: Axios with interceptors

#### AI Service
- **Framework**: FastAPI
- **Database**: SQLite (content mappings)
- **Content Generation**: Mock LLM with extensible architecture

#### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Development**: Monorepo architecture
- **Testing**: pytest (backend), Jest + Playwright (frontend)
- **CI/CD**: GitHub Actions

---

## 📁 Project Structure

```
bookgen-ai/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── users/             # User management & auth
│   │   ├── books/             # Book generation logic
│   │   └── core/              # Shared utilities
│   ├── config/                # Django settings
│   ├── tests/                 # Backend tests
│   └── requirements.txt
│
├── frontend/                   # Next.js application
│   ├── app/                   # App router pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities & API clients
│   ├── __tests__/             # Frontend tests
│   └── package.json
│
├── llm-service/               # FastAPI AI service
│   ├── app/                   # API endpoints
│   ├── services/              # Content generation
│   ├── tests/                 # LLM service tests
│   └── requirements.txt
│
├── shared/                    # Shared TypeScript types
│   └── types/
│
├── scripts/                   # Automation scripts
│   ├── setup.sh              # Initial project setup
│   ├── seed-db.sh            # Database seeding
│   └── run-tests.sh          # Run all tests
│
├── docker-compose.yml         # Development environment
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 24.0+ and **Docker Compose** 2.0+
- **Node.js** 18+ and **npm** 9+
- **Python** 3.11+
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bookgen-ai.git
   cd bookgen-ai
   ```

2. **Run automated setup**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

   This script will:
   - Copy environment example files
   - Install dependencies
   - Set up Docker containers
   - Run database migrations
   - Seed initial data

3. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - LLM Service: http://localhost:8001

### Manual Setup (Alternative)

If you prefer manual setup or the automated script fails:

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_domains
   python manage.py create_test_users
   python manage.py runserver
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **LLM Service Setup**
   ```bash
   cd llm-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8001
   ```

---

## 🧪 Testing

### Run All Tests
```bash
./scripts/run-tests.sh
```

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=apps --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test                    # Unit & integration tests
npm run test:e2e           # E2E tests with Playwright
npm run test:coverage      # Generate coverage report
```

### LLM Service Tests
```bash
cd llm-service
pytest tests/ -v --cov=app
```

---

## 📊 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
Follow the coding standards:
- Backend: PEP 8, type hints, docstrings
- Frontend: ESLint, Prettier, strict TypeScript
- Tests: Maintain 85%+ coverage

### 3. Run Tests
```bash
./scripts/run-tests.sh
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mongodb://localhost:27017/bookgen
REDIS_URL=redis://localhost:6379/0
CLOUDINARY_URL=cloudinary://key:secret@cloud
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

See `.env.example` files in each directory for complete configuration.

---

## 📖 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

### Key Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/password-reset/` - Request password reset
- `GET /api/auth/verify-email/{token}/` - Verify email

#### User Profile
- `GET /api/users/profile/` - Get user profile
- `PATCH /api/users/profile/` - Update profile
- `GET /api/users/analytics/` - Get user analytics
- `GET /api/users/books-history/` - Get books history

#### Book Generation
- `GET /api/domains/` - List available domains
- `GET /api/domains/{id}/niches/` - List niches for domain
- `POST /api/books/generate/` - Generate new book

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Commit Convention
We use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Django REST Framework for excellent API tools
- Next.js team for the amazing React framework
- FastAPI for the high-performance API framework
- The open-source community for inspiration and support

---

## 📞 Support

For support, email support@bookgen-ai.com or open an issue in the GitHub repository.

---

## 🗺️ Roadmap

### Q1 2024
- ✅ Core authentication system
- ✅ Basic book generation
- ✅ User profiles and analytics

### Q2 2024
- 🔄 Advanced book editing
- 🔄 Custom LLM training
- 🔄 AI cover generation

### Q3 2024
- 📅 PDF browser preview
- 📅 Payment integration
- 📅 Team collaboration features

### Q4 2024
- 📅 Mobile app (React Native)
- 📅 Advanced analytics dashboard
- 📅 Multi-language support

---

**Made with ❤️ by the BookGen-AI Team**
