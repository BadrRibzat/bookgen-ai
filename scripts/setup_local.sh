#!/bin/bash
set -e

# Activate Mamba Environment
source /home/badr/.local/share/mamba/etc/profile.d/mamba.sh
mamba activate bookgen-ai

# Setup LLM Service
echo "Setting up LLM Service..."
cd llm-service
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Setup Backend
echo "Setting up Backend..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "Setup complete."
