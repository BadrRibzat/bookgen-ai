#!/usr/bin/env python3
"""Validate the packaged fine-tuned BookGen model before deployment."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

# Make app modules available when script executed from repo root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.evaluation import (  # noqa: E402
    DOMAIN_KEYWORDS,
    coherence_score,
    domain_specificity_score,
    load_local_model,
    load_metrics,
)


@dataclass
class DomainValidationResult:
    domain: str
    keyword_hits: int
    keyword_total: int
    specificity: float
    coherence: float
    word_count: int


@dataclass
class ValidationReport:
    model_path: str
    metrics_path: str
    summary: Dict[str, float]
    domains: List[DomainValidationResult]

    def to_dict(self) -> Dict[str, object]:
        payload = {
            "model_path": self.model_path,
            "metrics_path": self.metrics_path,
            "summary": self.summary,
            "domains": [asdict(domain) for domain in self.domains],
        }
        return payload


DEFAULT_PROMPTS: Dict[str, str] = {
    "ai_ml": "Summarize practical AI strategies for enterprise adoption.",
    "automation": "Explain how automation can streamline onboarding workflows.",
    "healthtech": "Describe regulations impacting healthtech platforms in 2026.",
    "cybersecurity": "List mitigation steps for supply chain cybersecurity threats.",
    "creator_economy": "Provide a membership launch framework for creators.",
    "web3": "Explain how DAOs govern community-led projects.",
    "ecommerce": "Outline retention strategies for ecommerce subscriptions.",
    "data_analytics": "Discuss advanced analytics pipelines for product teams.",
    "gaming": "Highlight monetisation tactics for live service games.",
    "kids_parenting": "Create a routine guide for positive parenting mornings.",
    "nutrition": "Present nutrition periodisation advice for athletes.",
    "recipes": "Introduce a seasonal cookbook for beginner chefs.",
}


def run_validation(model_path: Path, max_new_tokens: int = 96) -> ValidationReport:
    tokenizer, model = load_local_model(model_path)
    metrics_path = model_path / "metrics.json"
    metrics = load_metrics(metrics_path)

    domain_results: List[DomainValidationResult] = []
    specificity_scores: List[float] = []
    coherence_scores: List[float] = []

    for domain, prompt in DEFAULT_PROMPTS.items():
        encoded = tokenizer(prompt, return_tensors="pt")
        output = model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token,
        )
        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
        continuation = decoded[len(prompt) :].strip() if decoded.startswith(prompt) else decoded
        lower = continuation.lower()

        keywords = DOMAIN_KEYWORDS[domain]
        hits = sum(1 for keyword in keywords if keyword in lower)
        specificity = domain_specificity_score(continuation, domain)
        coherence = coherence_score(continuation)

        domain_results.append(
            DomainValidationResult(
                domain=domain,
                keyword_hits=hits,
                keyword_total=len(keywords),
                specificity=round(specificity, 3),
                coherence=round(coherence, 3),
                word_count=len(continuation.split()),
            )
        )
        specificity_scores.append(specificity)
        coherence_scores.append(coherence)

    summary = {
        "avg_specificity": round(sum(specificity_scores) / len(specificity_scores), 3),
        "avg_coherence": round(sum(coherence_scores) / len(coherence_scores), 3),
        "training_examples": metrics["training"]["examples"],
        "validation_perplexity": metrics["metrics"]["validation_perplexity"],
        "base_perplexity": metrics["metrics"]["base_model_perplexity"],
    }

    return ValidationReport(
        model_path=str(model_path),
        metrics_path=str(metrics_path),
        summary=summary,
        domains=domain_results,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate fine-tuned BookGen model")
    parser.add_argument(
        "--model-path",
        default=os.environ.get("LLM_MODEL_PATH", PROJECT_ROOT / "models" / "final_model"),
        help="Path to fine-tuned model directory",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=96,
        help="Tokens to sample per validation prompt",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to save JSON report",
    )
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise SystemExit(f"Model directory not found: {model_path}")

    report = run_validation(model_path, args.max_new_tokens)
    payload = report.to_dict()
    print(json.dumps(payload, indent=2))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
