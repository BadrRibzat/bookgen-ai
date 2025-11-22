"""Shared pytest fixtures for LLM service tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import pytest
from transformers import AutoModelForCausalLM, AutoTokenizer

# Ensure the llm-service package root is importable inside tests
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.evaluation import DOMAIN_KEYWORDS, load_metrics  # noqa: E402

DOMAINS: List[str] = list(DOMAIN_KEYWORDS.keys())


@pytest.fixture(scope="session")
def model_dir() -> Path:
    path = PROJECT_ROOT / "models" / "final_model"
    if not path.exists():
        pytest.skip("Fine-tuned model directory not found; ensure models/final_model is available.")
    return path


@pytest.fixture(scope="session")
def metrics(model_dir: Path) -> Dict[str, object]:
    metrics_path = model_dir / "metrics.json"
    if not metrics_path.exists():
        pytest.skip("metrics.json is required for comparison tests.")
    return load_metrics(metrics_path)


@pytest.fixture(scope="session")
def tokenizer(model_dir: Path):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


@pytest.fixture(scope="session")
def model(model_dir: Path):
    model = AutoModelForCausalLM.from_pretrained(model_dir)
    model.eval()
    return model


@pytest.fixture(scope="session")
def domain_prompts() -> Dict[str, str]:
    return {
        "ai_ml": "Outline the future of applied machine learning for 2026.",
        "automation": "Design an automation playbook for scaling operations.",
        "healthtech": "Explain how healthtech startups can navigate compliance.",
        "cybersecurity": "Summarize the top cybersecurity threats for remote teams.",
        "creator_economy": "Create a launch plan for a creator economy membership site.",
        "web3": "Describe the evolution of web3 governance models.",
        "ecommerce": "Draft a book outline on ecommerce conversion strategy.",
        "data_analytics": "List advanced data analytics techniques for product teams.",
        "gaming": "Discuss emerging monetization strategies in gaming.",
        "kids_parenting": "Provide a chapter overview on positive parenting routines.",
        "nutrition": "Explain how to structure a nutrition coaching program.",
        "recipes": "Generate a seasonal recipe collection introduction.",
    }
