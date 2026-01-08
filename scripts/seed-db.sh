#!/bin/bash

# ============================================
# BookGen-AI - Database Seeding Script
# ============================================
# Seeds the database with initial data

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==>${NC} Seeding BookGen-AI Database..."

cd backend
source venv/bin/activate

# Seed domains, niches, and audiences
echo -e "${BLUE}==>${NC} Seeding domains, niches, and audiences..."
python manage.py seed_domains

# Create subscription plans
echo -e "${BLUE}==>${NC} Creating subscription plans..."
python manage.py create_subscription_plans

# Create test users
echo -e "${BLUE}==>${NC} Creating test user accounts..."
python manage.py create_test_users

echo -e "${GREEN}✓${NC} Database seeding complete!"
echo ""
echo "Test Accounts:"
echo "  Admin: admin@bookgen.ai / Admin@12345"
echo "  User:  user@example.com / User@12345"
echo "  New:   newuser@example.com / User@12345"
