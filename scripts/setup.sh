#!/bin/bash

# ============================================
# BookGen-AI - Automated Setup Script
# ============================================
# This script sets up the entire development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================
# Step 1: Check Prerequisites
# ============================================
print_status "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi
print_success "Node.js is installed ($(node --version))"

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi
print_success "Python 3 is installed ($(python3 --version))"

# ============================================
# Step 2: Create Environment Files
# ============================================
print_status "Setting up environment files..."

# Backend
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    print_success "Created backend/.env"
else
    print_warning "backend/.env already exists, skipping..."
fi

# Frontend
if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    print_success "Created frontend/.env.local"
else
    print_warning "frontend/.env.local already exists, skipping..."
fi

# LLM Service
if [ ! -f llm-service/.env ]; then
    cp llm-service/.env.example llm-service/.env
    print_success "Created llm-service/.env"
else
    print_warning "llm-service/.env already exists, skipping..."
fi

# ============================================
# Step 3: Install Backend Dependencies
# ============================================
print_status "Installing backend dependencies..."

cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Created Python virtual environment"
fi

cd backend && source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Backend dependencies installed"

cd ..

# ============================================
# Step 4: Install Frontend Dependencies
# ============================================
print_status "Installing frontend dependencies..."

cd ../frontend
npm install
print_success "Frontend dependencies installed"
cd ..

# ============================================
# Step 5: Install LLM Service Dependencies
# ============================================
print_status "Installing LLM service dependencies..."

cd llm-service

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Created Python virtual environment for LLM service"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "LLM service dependencies installed"

cd ..

# ============================================
# Step 6: Start Docker Services
# ============================================
print_status "Starting Docker services (MongoDB, Redis)..."

docker-compose up -d mongodb redis

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

print_success "Docker services started"

# ============================================
# Step 7: Run Database Migrations
# ============================================
print_status "Running database migrations..."

cd backend
source venv/bin/activate
python manage.py migrate
print_success "Database migrations completed"

# ============================================
# Step 8: Seed Initial Data
# ============================================
print_status "Seeding initial data..."

python manage.py seed_domains
print_success "Domains, niches, and audiences seeded"

python manage.py create_test_users
print_success "Test users created"

cd ..

# ============================================
# Step 9: Collect Static Files
# ============================================
print_status "Collecting static files..."

cd backend
source venv/bin/activate
python manage.py collectstatic --noinput
print_success "Static files collected"

cd ..

# ============================================
# Setup Complete
# ============================================
echo ""
print_success "=========================================="
print_success "  BookGen-AI Setup Complete! 🎉"
print_success "=========================================="
echo ""

print_status "Test Accounts Created:"
echo "  📧 Admin: admin@bookgen.ai / Admin@12345"
echo "  📧 User:  user@example.com / User@12345"
echo "  📧 New:   newuser@example.com / User@12345"
echo ""

print_status "Next Steps:"
echo "  1. Start all services:"
echo "     ${GREEN}docker-compose up -d${NC}"
echo ""
echo "  2. Access the application:"
echo "     Frontend:    ${BLUE}http://localhost:3000${NC}"
echo "     Backend API: ${BLUE}http://localhost:8000${NC}"
echo "     API Docs:    ${BLUE}http://localhost:8000/api/docs/${NC}"
echo "     LLM Service: ${BLUE}http://localhost:8001${NC}"
echo ""
echo "  3. Run tests:"
echo "     ${GREEN}./scripts/run-tests.sh${NC}"
echo ""

print_status "Useful Commands:"
echo "  View logs:        ${GREEN}docker-compose logs -f [service]${NC}"
echo "  Stop services:    ${GREEN}docker-compose down${NC}"
echo "  Restart services: ${GREEN}docker-compose restart${NC}"
echo "  Access DB shell:  ${GREEN}docker-compose exec backend python manage.py shell${NC}"
echo ""

print_success "Happy coding! 🚀"
