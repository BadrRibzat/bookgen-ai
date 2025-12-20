#!/bin/bash

echo "Testing LLM Service..."

# 1. Check Health
echo "Checking Health..."
curl -s http://localhost:8001/health | jq .

# 2. Generate Text
echo -e "\nGenerating Text..."
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The future of AI in healthcare is",
    "domain_id": "healthtech",
    "max_length": 100,
    "temperature": 0.7
  }' | jq .
