from __future__ import annotations

import pytest

from app.ml.evaluation import (
    DOMAIN_KEYWORDS,
    domain_specificity_score,
    measure_latency,
)
from .conftest import DOMAINS


@pytest.mark.parametrize("domain", DOMAINS)
def test_finetuned_model_generates_domain_content(domain: str, tokenizer, model, domain_prompts) -> None:
    prompt = domain_prompts[domain]
    latency, generated = measure_latency(tokenizer, model, prompt, max_new_tokens=96)

    assert generated, "Generated text should not be empty"
    assert latency < 1.5, f"Inference latency too high for {domain}: {latency:.2f}s"

    score = domain_specificity_score(generated, domain)
    assert score >= 0.2, (
        f"Generated text for {domain} lacks domain context (score={score:.2f})"
    )


@pytest.mark.parametrize("domain", DOMAINS)
def test_domain_keyword_coverage(domain: str, tokenizer, model, domain_prompts) -> None:
    prompt = domain_prompts[domain]
    _, generated = measure_latency(tokenizer, model, prompt, max_new_tokens=80)

    keywords = DOMAIN_KEYWORDS[domain]
    lower = generated.lower()
    hits = [kw for kw in keywords if kw in lower]
    assert hits, f"Expected at least one domain keyword in output for {domain}"
