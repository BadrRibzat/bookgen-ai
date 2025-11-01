#!/bin/bash

# ============================================
# File Creation Script for BookGen-AI
# Creates all remaining necessary files
# ============================================

set -e

echo "Creating remaining project files..."

# Make scripts executable
chmod +x scripts/setup.sh
chmod +x scripts/seed-db.sh
chmod +x scripts/run-tests.sh

# Make manage.py executable
chmod +x backend/manage.py

echo "✓ All files created and permissions set!"
echo ""
echo "Next steps:"
echo "1. Review the files created"
echo "2. Run: chmod +x scripts/setup.sh"
echo "3. Run: ./scripts/setup.sh"
