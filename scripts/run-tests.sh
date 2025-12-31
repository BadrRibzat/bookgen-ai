#!/bin/bash

# ============================================
# BookGen-AI - Test Runner Script
# ============================================
# Runs all tests across backend, frontend, and LLM service

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED=0

echo -e "${BLUE}=========================================="
echo -e "  BookGen-AI Test Suite"
echo -e "==========================================${NC}"
echo ""

# ============================================
# Backend Tests
# ============================================
echo -e "${BLUE}==>${NC} Running Backend Tests (pytest)..."
cd backend
source ../venv/bin/activate

if pytest tests/ -v --cov=apps --cov-report=html --cov-report=term; then
    echo -e "${GREEN}✓${NC} Backend tests passed"
else
    echo -e "${RED}✗${NC} Backend tests failed"
    FAILED=1
fi

echo ""
echo -e "${BLUE}Coverage report:${NC} backend/htmlcov/index.html"
echo ""

cd ..

# ============================================
# Frontend Tests
# ============================================
echo -e "${BLUE}==>${NC} Running Frontend Tests (Jest)..."
cd frontend

if npm test -- --coverage --watchAll=false; then
    echo -e "${GREEN}✓${NC} Frontend tests passed"
else
    echo -e "${RED}✗${NC} Frontend tests failed"
    FAILED=1
fi

echo ""
echo -e "${BLUE}Coverage report:${NC} frontend/coverage/index.html"
echo ""

cd ..

# ============================================
# LLM Service Tests
# ============================================
echo -e "${BLUE}==>${NC} Running LLM Service Tests (pytest)..."
cd llm-service
source ../venv/bin/activate

if pytest tests/ -v --cov=app --cov-report=html --cov-report=term; then
    echo -e "${GREEN}✓${NC} LLM service tests passed"
else
    echo -e "${RED}✗${NC} LLM service tests failed"
    FAILED=1
fi

echo ""
echo -e "${BLUE}Coverage report:${NC} llm-service/htmlcov/index.html"
echo ""

cd ..

# ============================================
# Summary
# ============================================
echo -e "${BLUE}=========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}  All Tests Passed! ✓${NC}"
else
    echo -e "${RED}  Some Tests Failed ✗${NC}"
fi
echo -e "==========================================${NC}"
echo ""

exit $FAILED
