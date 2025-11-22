"""Utility helpers for evaluating BookGen LLM generations."""

from __future__ import annotations

import json
import math
import statistics
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from transformers import AutoModelForCausalLM, AutoTokenizer

DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "ai_ml": ["machine learning", "neural", "training", "model", "inference"],
    "automation": ["workflow", "automation", "robotic", "RPA", "orchestration"],
    "healthtech": ["clinical", "patient", "telehealth", "medical", "diagnostics"],
    "cybersecurity": ["threat", "vulnerability", "encryption", "zero trust", "incident"],
    "creator_economy": ["monetization", "audience", "platform", "content", "sponsorship"],
    "web3": ["blockchain", "token", "smart contract", "wallet", "decentralized"],
    "ecommerce": ["conversion", "checkout", "catalog", "fulfillment", "merchandising"],
    "data_analytics": ["dashboard", "insights", "visualization", "ETL", "analytics"],
    "gaming": ["gameplay", "player", "studio", "monetization", "esports"],
    "kids_parenting": ["parent", "child", "development", "education", "milestones"],
    "nutrition": ["macronutrient", "diet", "wellness", "meal plan", "supplement"],
    "recipes": ["ingredients", "cooking", "preheat", "serve", "instructions"],
}


def load_local_model(model_path: Path):
    """Load the fine-tuned model and tokenizer from disk."""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model.eval()
    return tokenizer, model


def domain_specificity_score(text: str, domain: str) -> float:
    """Score a generated sample for domain specificity using keyword coverage."""
    keywords = DOMAIN_KEYWORDS.get(domain, [])
    if not keywords:
        return 0.0

    text_lower = text.lower()
    hits = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return hits / len(keywords)


def coherence_score(text: str) -> float:
    """Simple coherence proxy using average sentence length variance."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    if len(sentences) < 2:
        return 0.0
    lengths = [len(sentence.split()) for sentence in sentences]
    mean = statistics.mean(lengths)
    if math.isclose(mean, 0.0):
        return 0.0
    variance = statistics.pvariance(lengths)
    # Lower variance -> higher coherence; normalise to 0-1
    return max(0.0, min(1.0, 1 - (variance / (variance + mean))))


def measure_latency(tokenizer, model, prompt: str, max_new_tokens: int = 64) -> Tuple[float, str]:
    """Measure generation latency (seconds) and return generated text."""
    encoded = tokenizer(prompt, return_tensors="pt")
    start = time.perf_counter()
    output = model.generate(
        **encoded,
        max_new_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    latency = time.perf_counter() - start
    generated = tokenizer.decode(output[0], skip_special_tokens=True)
    return latency, generated[len(prompt) :].strip() if generated.startswith(prompt) else generated


def load_metrics(metrics_path: Path) -> Dict[str, object]:
    """Load fine-tuning metrics captured during Kaggle training."""
    with metrics_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summarise_scores(scores: Iterable[float]) -> Dict[str, float]:
    """Compute summary statistics for iterable of floats."""
    values = list(scores)
    if not values:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
    }
