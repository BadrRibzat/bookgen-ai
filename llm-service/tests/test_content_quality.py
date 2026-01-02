from __future__ import annotations

import pytest

from app.ml.evaluation import coherence_score, summarise_scores
from .conftest import DOMAINS


@pytest.mark.parametrize("domain", DOMAINS[:6])
def test_generated_content_coherence(domain: str, tokenizer, model, domain_prompts) -> None:
    prompt = domain_prompts[domain]
    output = model.generate(
        **tokenizer(prompt, return_tensors="pt"),
        max_new_tokens=120,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        repetition_penalty=1.1,
        no_repeat_ngram_size=0,
        pad_token_id=tokenizer.eos_token_id,
    )
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    continuation = text[len(prompt) :].strip() if text.startswith(prompt) else text
    score = coherence_score(continuation)
    assert score >= 0.05, f"Coherence score too low for {domain}: {score:.2f}"


@pytest.mark.parametrize("domain", DOMAINS[6:])
def test_generation_length_and_variation(domain: str, tokenizer, model, domain_prompts) -> None:
    prompt = domain_prompts[domain]
    outputs = []
    for _ in range(2):
        sample = model.generate(
            **tokenizer(prompt, return_tensors="pt"),
            max_new_tokens=100,
            temperature=0.75,
            top_p=0.92,
            do_sample=True,
            repetition_penalty=1.05,
            no_repeat_ngram_size=0,
            pad_token_id=tokenizer.eos_token_id,
        )
        text = tokenizer.decode(sample[0], skip_special_tokens=True)
        continuation = text[len(prompt) :].strip() if text.startswith(prompt) else text
        outputs.append(len(continuation.split()))

    stats = summarise_scores(outputs)
    assert stats["mean"] >= 40, f"Generated continuation too short for {domain}"