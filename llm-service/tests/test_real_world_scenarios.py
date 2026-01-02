from __future__ import annotations

from typing import List, Tuple

import pytest

from app.ml.evaluation import domain_specificity_score

Scenario = Tuple[str, str]

SCENARIOS: List[Scenario] = [
    ("ai_ml", "Write a foreword that inspires executives to invest in AI transformation."),
    ("cybersecurity", "Provide a security incident playbook checklist for SMBs."),
    ("nutrition", "Create a sample meal plan introduction for plant-based athletes."),
    ("ecommerce", "Draft a chapter outline for scaling a direct-to-consumer brand."),
]


@pytest.mark.parametrize("domain,prompt", SCENARIOS)
def test_real_world_prompts(domain: str, prompt: str, tokenizer, model) -> None:
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(
        **inputs,
        max_new_tokens=160,
        temperature=0.68,
        top_p=0.92,
        do_sample=True,
        repetition_penalty=1.1,
        no_repeat_ngram_size=0,
        pad_token_id=tokenizer.eos_token_id,
    )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    completion = decoded[len(prompt) :].strip() if decoded.startswith(prompt) else decoded

    assert len(completion.split()) >= 60, "Real-world scenario output too short"
    assert domain_specificity_score(completion, domain) >= 0.15
