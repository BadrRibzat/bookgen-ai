from __future__ import annotations

from typing import Dict


def test_training_speedup(metrics: Dict[str, object]) -> None:
    duration_hours = metrics["training"]["duration_hours"]
    assert duration_hours <= 6.1, "Training duration regression detected"
    cpu_estimate_hours = 24 * 365 * 2  # original 2-year CPU estimate
    speedup = cpu_estimate_hours / duration_hours
    assert speedup >= 2500, "GPU speedup should remain above 2500x"


def test_global_perplexity_improvement(metrics: Dict[str, object]) -> None:
    baseline = metrics["metrics"]["base_model_perplexity"]
    finetuned = metrics["metrics"]["validation_perplexity"]
    assert finetuned < baseline, "Fine-tuned perplexity must beat baseline"
    assert baseline - finetuned >= 5, "Minimum perplexity delta not met"


def test_domain_performance_vs_baseline(metrics: Dict[str, object]) -> None:
    for domain_metrics in metrics["domain_benchmarks"]:
        assert domain_metrics["perplexity"] < domain_metrics["base_perplexity"], (
            f"Domain {domain_metrics['domain']} failed to beat baseline perplexity"
        )
        assert domain_metrics["keyword_overlap"] >= 0.75, (
            f"Domain {domain_metrics['domain']} keyword overlap regression"
        )


def test_inference_latency(metrics: Dict[str, object]) -> None:
    latency = metrics["inference"]["average_latency_ms"]
    assert latency <= 420, "Average inference latency should stay under 420 ms"
