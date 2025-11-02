# 🚀 BookGen-AI - Complete Setup Commands

## Prerequisites Check
```bash
docker --version         # Should be 24.0+
docker-compose --version # Should be 2.0+
node --version          # Should be 18+
python3 --version       # Should be 3.11+
```

---

## Phase 1: Copy All Artifact Files

You've already created the directory structure. Now copy all the artifact contents into these files:

### Backend Files to Create:
```bash
# Config files (already done)
backend/config/settings.py
backend/config/urls.py
backend/config/wsgi.py
backend/config/celery.py
backend/config/__init__.py (update with celery import)

# Management
backend/manage.py

# Apps - Users
backend/apps/users/models.py
backend/apps/users/serializers.py
backend/apps/users/views.py
backend/apps/users/services.py
backend/apps/users/urls/auth_urls.py
backend/apps/users/urls/user_urls.py
backend/apps/users/urls/__init__.py

# Apps - Core
backend/apps/core/exceptions.py
backend/apps/core/urls.py
backend/apps/core/management/commands/seed_domains.py
backend/apps/core/management/commands/create_test_users.py

# Apps - Books
backend/apps/books/urls.py

# Email Templates
backend/templates/emails/verify_email.txt
backend/templates/emails/verify_email.html
backend/templates/emails/password_reset.txt
backend/templates/emails/password_reset.html

# Docker
backend/Dockerfile
backend/requirements.txt
```

### Frontend Files to Create:
```bash
# Shared Types
shared/types/index.ts

# Config
frontend/package.json
frontend/next.config.js
frontend/tsconfig.json
frontend/tailwind.config.ts

# API Layer
frontend/lib/api/client.ts
frontend/lib/api/auth.ts
frontend/lib/api/users.ts

# Validation
frontend/lib/validation/auth.schema.ts

# Context
frontend/lib/contexts/AuthContext.tsx

# Utils
frontend/lib/utils/index.ts

# UI Components
frontend/components/ui/Button.tsx
frontend/components/ui/Input.tsx
frontend/components/ui/Alert.tsx

# Auth Components
frontend/components/auth/LoginForm.tsx
frontend/components/auth/RegisterForm.tsx

# App Pages
frontend/app/layout.tsx
frontend/app/globals.css
frontend/app/page.tsx
frontend/app/auth/login/page.tsx
frontend/app/auth/register/page.tsx
frontend/app/dashboard/page.tsx

# Docker
frontend/Dockerfile
```

### LLM Service Files to Create:
```bash
llm-service/requirements.txt
llm-service/app/main.py
llm-service/Dockerfile
```

---

## Phase 2: Make Scripts Executable

```bash
chmod +x scripts/setup.sh
chmod +x scripts/seed-db.sh
chmod +x scripts/run-tests.sh
chmod +x backend/manage.py
```

---

## Phase 3: Create .env Files

```bash
# Copy environment examples
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
cp llm-service/.env.example llm-service/.env
```

---

## Phase 4: Run Automated Setup

### Option A: Automated Setup (Recommended)
```bash
./scripts/setup.sh
```

This will:
- Check prerequisites
- Install all dependencies
- Start Docker services
- Run migrations
- Seed database
- Create test users

### Option B: Manual Setup

If automated setup fails, follow these steps:

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Seed data
python manage.py seed_domains
python manage.py create_test_users

# Collect static files
python manage.py collectstatic --noinput

cd ..
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Build (optional, for production)
# npm run build

cd ..
```

#### 3. LLM Service Setup
```bash
cd llm-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

cd ..
```

#### 4. Start Docker Services
```bash
# Start MongoDB and Redis
docker-compose up -d mongodb redis

# Wait for services to be ready
sleep 10

# Check if services are running
docker-compose ps
```

---

## Phase 5: Run the Application

### Option A: Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Option B: Run Services Individually

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - LLM Service:**
```bash
cd llm-service
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

**Terminal 4 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
celery -A config worker --loglevel=info
```

---

## Phase 6: Access the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **LLM Service**: http://localhost:8001

### Test Accounts:
- **Admin**: `admin@bookgen.ai` / `Admin@12345`
- **User**: `user@example.com` / `User@12345`
- **New User**: `newuser@example.com` / `User@12345`

---

## Phase 7: Verify Installation

### 1. Check Backend
```bash
curl http://localhost:8000/api/schema/
```

### 2. Check Frontend
```bash
curl http://localhost:3000
```

### 3. Check LLM Service
```bash
curl http://localhost:8001/health
```

### 4. Test Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"User@12345"}'
```

---

## Phase 8: Development Workflow

### Running Tests
```bash
# Run all tests
./scripts/run-tests.sh

# Backend tests only
cd backend
source venv/bin/activate
pytest tests/ -v --cov=apps

# Frontend tests only
cd frontend
npm test

# E2E tests
cd frontend
npm run test:e2e
```

### Database Operations
```bash
cd backend
source venv/bin/activate

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (caution!)
python manage.py flush
python manage.py seed_domains
python manage.py create_test_users
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 apps/
black apps/
isort apps/

# Frontend linting
cd frontend
npm run lint
npm run format
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :27017 # MongoDB

# Kill process
kill -9 <PID>
```

### Docker Issues
```bash
# Stop all containers
docker-compose down

# Remove volumes (caution: deletes data!)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# Start fresh
docker-compose up -d --force-recreate
```

### Python Dependencies
```bash
# Clear pip cache
pip cache purge

# Reinstall
pip install -r requirements.txt --force-reinstall
```

### Node Dependencies
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

---

## Next Steps

1. ✅ Complete Phase 1 (Authentication) - **DONE!**
2. 🔄 Implement Phase 2 (User Profile & Analytics)
3. 📝 Implement Phase 3 (Book Editing)
4. 🤖 Implement Phase 4 (Custom LLM)
5. 🎨 Implement Phase 5 (Cover Generation)
6. 📄 Implement Phase 6 (PDF Construction)
7. 💳 Implement Phase 7 (Payment Integration)

---

## Useful Commands Reference

```bash
# Docker
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose restart            # Restart services
docker-compose logs -f [service]  # View logs
docker-compose exec backend sh    # Access backend container
docker-compose exec mongodb mongosh # Access MongoDB shell

# Django
python manage.py shell            # Django shell
python manage.py dbshell          # Database shell
python manage.py showmigrations   # Show migrations
python manage.py test            # Run Django tests

# Git
git status
git add .
git commit -m "feat: initial implementation"
git push origin main
```

---

## 🎉 You're All Set!

Your BookGen-AI development environment is now ready. Start by testing the authentication flow at http://localhost:3000
