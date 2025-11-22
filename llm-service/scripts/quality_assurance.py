#!/usr/bin/env python3
"""Quality assurance checks for generated book content."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.evaluation import (  # noqa: E402
    DOMAIN_KEYWORDS,
    coherence_score,
    domain_specificity_score,
    load_local_model,
)

QUALITATIVE_PROMPTS: Dict[str, List[str]] = {
    "ai_ml": [
        "Produce a detailed chapter on responsible AI deployment.",
        "Draft a case study for scaling ML pipelines in production.",
    ],
    "cybersecurity": [
        "List proactive defenses against phishing for enterprises.",
        "Create a policy section on incident triage workflows.",
    ],
    "nutrition": [
        "Compile a weekly nutrition plan for endurance athletes.",
        "Explain the science of macronutrient timing for recovery.",
    ],
}


def analyse_domain(model_dir: Path, domain: str, prompts: List[str], max_new_tokens: int = 220):
    tokenizer, model = load_local_model(model_dir)
    results = []
    for prompt in prompts:
        encoded = tokenizer(prompt, return_tensors="pt")
        output = model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            temperature=0.68,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token,
        )
        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
        completion = decoded[len(prompt) :].strip() if decoded.startswith(prompt) else decoded

        specificity = domain_specificity_score(completion, domain)
        coherence = coherence_score(completion)
        keywords = DOMAIN_KEYWORDS[domain]
        hits = [kw for kw in keywords if kw in completion.lower()]

        results.append(
            {
                "prompt": prompt,
                "word_count": len(completion.split()),
                "specificity": round(specificity, 3),
                "coherence": round(coherence, 3),
                "keywords_matched": hits,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run qualitative QA checks on generated content")
    parser.add_argument(
        "--model-path",
        default=os.environ.get("LLM_MODEL_PATH", PROJECT_ROOT / "models" / "final_model"),
        help="Fine-tuned model directory",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=220,
        help="Tokens per QA sample",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output file",
    )
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        raise SystemExit(f"Model directory not found: {model_path}")

    payload = {
        domain: analyse_domain(model_path, domain, prompts, args.max_new_tokens)
        for domain, prompts in QUALITATIVE_PROMPTS.items()
    }

    print(json.dumps(payload, indent=2))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
