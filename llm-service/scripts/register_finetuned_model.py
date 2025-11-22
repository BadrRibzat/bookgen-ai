#!/usr/bin/env python3
"""Register the fine-tuned BookGen model metadata inside MongoDB."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from pymongo import MongoClient

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.evaluation import DOMAIN_KEYWORDS, load_metrics  # noqa: E402


def load_metadata(model_dir: Path) -> Dict[str, object]:
    metrics_path = model_dir / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"metrics.json not found in {model_dir}")
    return load_metrics(metrics_path)


def register_domains(
    client: MongoClient,
    metadata: Dict[str, object],
    model_dir: Path,
    domains: Iterable[str],
    collection_name: str = "llm_models",
) -> None:
    db = client[os.environ.get("MONGODB_DB_NAME", "bookgen_ai")]
    collection = db[collection_name]

    model_id = metadata["model_id"]
    training = metadata["training"]
    metrics = metadata["metrics"]

    for domain in domains:
        doc = {
            "model_id": f"{model_id}-{domain}",
            "name": f"BookGen DistilGPT2 Fine-Tuned ({domain})",
            "version": "1.0.0",
            "domain_id": domain,
            "domain_name": domain.replace("_", " ").title(),
            "niche_id": None,
            "niche_name": None,
            "base_model": metadata["base_model"],
            "model_size": "small",
            "parameters_count": 82000000,
            "training_job_id": metadata["model_id"],
            "training_examples": training["examples"],
            "training_epochs": training["epochs"],
            "final_loss": metrics["training_loss"],
            "validation_loss": metrics["eval_loss"],
            "perplexity": metrics["validation_perplexity"],
            "bleu_score": None,
            "rouge_scores": None,
            "model_path": str(model_dir),
            "tokenizer_path": str(model_dir),
            "config_path": str(model_dir / "config.json"),
            "generation_count": 0,
            "last_used": None,
            "avg_generation_time": metadata["inference"]["average_latency_ms"] / 1000.0,
            "is_active": True,
            "is_default": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "model_size_mb": metadata["inference"]["peak_memory_mb"],
            "storage_location": "local",
            "metadata": {
                "keyword_seed": DOMAIN_KEYWORDS.get(domain, []),
                "optimizer_steps": training["optimizer_steps"],
                "gradient_accumulation": training["gradient_accumulation"],
            },
        }

        collection.update_one(
            {"model_id": doc["model_id"]},
            {"$set": doc},
            upsert=True,
        )
        print(f"Upserted metadata for domain '{domain}'")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register fine-tuned model metadata")
    parser.add_argument(
        "--model-path",
        default=os.environ.get("LLM_MODEL_PATH", PROJECT_ROOT / "models" / "final_model"),
        help="Path to fine-tuned model directory",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="MongoDB connection string",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        default=None,
        help="Subset of domains to register. Defaults to all supported domains.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.database_url:
        raise SystemExit("DATABASE_URL env var or --database-url argument is required")

    model_dir = Path(args.model_path)
    if not model_dir.exists():
        raise SystemExit(f"Model directory not found: {model_dir}")

    metadata = load_metadata(model_dir)
    domains: List[str]
    if args.domains:
        domains = args.domains
    else:
        domains = metadata.get("domains", list(DOMAIN_KEYWORDS.keys()))

    client = MongoClient(args.database_url)
    try:
        register_domains(client, metadata, model_dir, domains)
    finally:
        client.close()


if __name__ == "__main__":
    main()
