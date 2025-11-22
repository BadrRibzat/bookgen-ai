#!/usr/bin/env python3
"""Benchmark inference speed and quality against the base distilgpt2 model."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.evaluation import (  # noqa: E402
    DOMAIN_KEYWORDS,
    domain_specificity_score,
    measure_latency,
)

PROMPTS: Dict[str, str] = {
    "ai_ml": "Explain how to productionize machine learning models with MLOps.",
    "cybersecurity": "Create an executive summary on zero trust security.",
    "nutrition": "Draft an introduction for a holistic nutrition guide.",
    "ecommerce": "List growth levers for scaling a DTC ecommerce brand.",
}


def _load(model_name_or_path: str) -> Optional[tuple]:
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
        model.eval()
        return tokenizer, model
    except OSError:
        return None


def benchmark_model(tokenizer, model, prompts: Dict[str, str], max_new_tokens: int = 96):
    results = {}
    for domain, prompt in prompts.items():
        latency, generated = measure_latency(tokenizer, model, prompt, max_new_tokens=max_new_tokens)
        word_count = len(generated.split())
        specificity = domain_specificity_score(generated, domain)
        results[domain] = {
            "latency_seconds": latency,
            "word_count": word_count,
            "specificity": specificity,
        }
    return results


def summarise(results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    per_domain = list(results.values())
    latencies = [item["latency_seconds"] for item in per_domain]
    specificity_scores = [item["specificity"] for item in per_domain]
    return {
        "avg_latency": statistics.mean(latencies),
        "p95_latency": statistics.quantiles(latencies, n=100)[94] if len(latencies) > 1 else latencies[0],
        "avg_specificity": statistics.mean(specificity_scores),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark fine-tuned vs base distilgpt2")
    parser.add_argument(
        "--model-path",
        default=os.environ.get("LLM_MODEL_PATH", PROJECT_ROOT / "models" / "final_model"),
        help="Path to fine-tuned model directory",
    )
    parser.add_argument(
        "--base-model",
        default=os.environ.get("BASE_MODEL_ID", "distilgpt2"),
        help="Base model identifier for comparison",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=96,
        help="Tokens generated per prompt",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Force device for benchmarking",
    )
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise SystemExit(f"Fine-tuned model directory not found: {model_path}")

    finetuned = _load(str(model_path))
    if finetuned is None:
        raise SystemExit("Unable to load fine-tuned model")

    base = _load(args.base_model)
    if base is None:
        print(
            json.dumps(
                {
                    "warning": "Base model not available offline; skipping baseline comparison",
                    "base_model": args.base_model,
                }
            )
        )

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    finetuned[1].to(device)
    if base:
        base[1].to(device)

    finetuned_results = benchmark_model(
        tokenizer=finetuned[0],
        model=finetuned[1],
        prompts=PROMPTS,
        max_new_tokens=args.max_new_tokens,
    )

    payload: Dict[str, object] = {
        "model_path": str(model_path),
        "device": str(device),
        "fine_tuned": {
            "per_domain": finetuned_results,
            "summary": summarise(finetuned_results),
        },
    }

    if base:
        base_results = benchmark_model(
            tokenizer=base[0],
            model=base[1],
            prompts=PROMPTS,
            max_new_tokens=args.max_new_tokens,
        )
        payload["base"] = {
            "model": args.base_model,
            "per_domain": base_results,
            "summary": summarise(base_results),
        }
        delta = {
            domain: {
                "latency_improvement": base_results[domain]["latency_seconds"] - finetuned_results[domain]["latency_seconds"],
                "specificity_gain": finetuned_results[domain]["specificity"] - base_results[domain]["specificity"],
            }
            for domain in PROMPTS
        }
        payload["comparison"] = delta

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
