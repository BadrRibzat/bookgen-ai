#!/bin/bash
source /home/badr/.local/share/mamba/etc/profile.d/mamba.sh
mamba activate bookgen-ai

cd llm-service

echo "Starting LLM Service on port 8001..."
uvicorn app.main:app --host 0.0.0.0 --port 8001
