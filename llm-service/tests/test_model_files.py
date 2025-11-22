from __future__ import annotations

from pathlib import Path

import pytest

REQUIRED_FILES = {
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "special_tokens_map.json",
    "metrics.json",
}


@pytest.mark.parametrize("filename", sorted(REQUIRED_FILES))
def test_model_artifacts_present(model_dir: Path, filename: str) -> None:
    """Ensure all critical model artifacts are packaged with the fine-tuned model."""
    assert (model_dir / filename).exists(), f"Missing artifact: {filename}"


def test_model_directory_readable(model_dir: Path) -> None:
    """Model directory should contain more than one file and be readable."""
    files = [p for p in model_dir.iterdir() if p.is_file()]
    assert len(files) >= len(REQUIRED_FILES), "Model directory appears incomplete"
