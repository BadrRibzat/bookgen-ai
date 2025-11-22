FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies with build cache
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage fine-tuned model early for better layer caching
ARG MODEL_DIR=models/final_model
COPY ${MODEL_DIR} /opt/bookgen/models/final_model

# Copy application source (model directory excluded by .dockerignore)
COPY . .

# Link staged model into runtime path and ensure directories exist
RUN rm -rf models/final_model && \
    ln -s /opt/bookgen/models/final_model models/final_model && \
    mkdir -p data output logs temp .cache/huggingface

ENV LLM_MODEL_PATH=/app/models/final_model \
    LLM_MODEL_METADATA=/app/models/final_model/metrics.json \
    BASE_MODEL_ID=distilgpt2 \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
