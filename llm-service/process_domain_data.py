#!/usr/bin/env python3
"""Generic processor for BookGen domain datasets.

This utility converts heterogeneous raw sources (CSV/JSON/JSONL) into the
BookGen normalized training format for multiple domains beyond AI/ML. It
focuses on non-text assets (tabular data, structured corpora) and writes
processed outputs to the corresponding `data/training_sets/<domain>/processed`
directory.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set

try:  # Optional heavy dependency for tabular handling.
    import pandas as pd
except ImportError:  # pragma: no cover - handled at runtime
    pd = None  # type: ignore


LOGGER = logging.getLogger("process_domain_data")
ISO_NOW = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
SCRIPT_DIR = Path(__file__).resolve().parent
RAW_ROOT = SCRIPT_DIR / "data" / "raw_sources"
TRAINING_ROOT = SCRIPT_DIR / "data" / "training_sets"
SUPPORTED_JSON_EXTS = {".json", ".jsonl"}
SUPPORTED_CSV_EXTS = {".csv"}
SUPPORTED_PARQUET_EXTS = {".parquet"}
SUPPORTED_TEXT_EXTS = {".txt"}


@dataclass
class Example:
    """Normalized training example for BookGen domains."""

    id: str
    input: str
    output: str
    context: str
    difficulty_level: int
    subscription_tier: str
    tags: List[str]
    quality_score: float
    metadata: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "input": self.input,
            "output": self.output,
            "context": self.context,
            "difficulty_level": self.difficulty_level,
            "subscription_tier": self.subscription_tier,
            "tags": self.tags,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
        }


@dataclass
class SourceStats:
    produced: int = 0
    skipped: int = 0

    def register(self, created: int, skipped: int = 0) -> None:
        self.produced += created
        self.skipped += skipped


@dataclass
class DomainConfig:
    """Configuration describing how to process a domain."""

    raw_dirs: Sequence[str]
    description: str
    prompt_subject: str
    base_tags: Sequence[str]
    tier_thresholds: Sequence[int] = (3, 7)


DOMAIN_CONFIG: Dict[str, DomainConfig] = {
    "automation": DomainConfig(
        raw_dirs=["Automation-Workflows"],
        description="Automation workflows, business process orchestration, and operational playbooks",
        prompt_subject="automation workflow",
        base_tags=("automation", "workflow", "operations"),
    ),
    "creator_economy": DomainConfig(
        raw_dirs=["Creator-Economy_Digital-Content"],
        description="Creator economy growth tactics, monetization strategies, and digital audience insights",
        prompt_subject="creator economy insight",
        base_tags=("creator_economy", "digital_content", "growth"),
    ),
    "cybersecurity": DomainConfig(
        raw_dirs=["Cyber-Security/malware_intelligence_corpora", "Cyber-Security/phishing_url_detection", "Cyber-Security/threat_detection_instruction_tuning", "Cyber-Security/threat_intelligence_feeds"],
        description="Cybersecurity intelligence, threat detection, and vulnerability response guidance",
        prompt_subject="cybersecurity intelligence report",
        base_tags=("cybersecurity", "threat_intel", "security_ops"),
    ),
    "data_analytics": DomainConfig(
        raw_dirs=["Data-Analytics_Business-Intelligence"],
        description="Data analytics playbooks, business intelligence workflows, and statistical insights",
        prompt_subject="data analytics scenario",
        base_tags=("data_analytics", "business_intelligence", "analytics"),
    ),
    "ecommerce": DomainConfig(
        raw_dirs=["E-commerce_Retail-Tech"],
        description="E-commerce operations, retail technology modernization, and omnichannel strategies",
        prompt_subject="e-commerce strategy brief",
        base_tags=("ecommerce", "retail", "commerce"),
    ),
    "gaming": DomainConfig(
        raw_dirs=["Gaming-Interactive_Entertainment"],
        description="Gaming industry analyses, product design insights, and interactive entertainment trends",
        prompt_subject="gaming industry insight",
        base_tags=("gaming", "interactive", "product_design"),
    ),
    "healthtech": DomainConfig(
        raw_dirs=["Health-Wellness-Technology"],
        description="Digital health product insights, healthtech market intelligence, and clinical operations",
        prompt_subject="healthtech briefing",
        base_tags=("healthtech", "digital_health", "wellness"),
    ),
    "kids_parenting": DomainConfig(
        raw_dirs=["Kids-Parenting"],
        description="Parenting support plans, educational content, and child development resources",
        prompt_subject="parenting program insight",
        base_tags=("parenting", "education", "family"),
    ),
    "nutrition": DomainConfig(
        raw_dirs=["Nutrition-Meditation"],
        description="Nutrition science, wellness data, and mindful living routines",
        prompt_subject="nutrition and wellness data insight",
        base_tags=("nutrition", "wellness", "health"),
    ),
    "recipes": DomainConfig(
        raw_dirs=["Recipes-Cooking"],
        description="Culinary recipes, ingredient breakdowns, and cooking techniques",
        prompt_subject="culinary recipe brief",
        base_tags=("recipes", "cooking", "culinary"),
    ),
    "ai_ml": DomainConfig(
        raw_dirs=["AI-ML-Innovation", "Artificial-Intelligence_Machine-Learning"],
        description="Artificial intelligence product strategy, machine learning research, and generative AI market trends",
        prompt_subject="AI and machine learning insight",
        base_tags=("ai_ml", "machine_learning", "artificial_intelligence"),
        tier_thresholds=(4, 8),
    ),
    "web3": DomainConfig(
        raw_dirs=["Web3-Blockchain"],
        description="Web3 startup intelligence, blockchain product analyses, and decentralized tech roadmaps",
        prompt_subject="web3 strategy memo",
        base_tags=("web3", "blockchain", "decentralization"),
    ),
}


class DomainDataProcessor:
    def __init__(self, max_per_source: int = 400, seed: int = 42) -> None:
        self.max_per_source = max_per_source
        random.seed(seed)
        self.stats: Dict[str, Dict[str, SourceStats]] = {}
        LOGGER.debug("Initialized with max_per_source=%s", max_per_source)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process(self, domains: Sequence[str]) -> None:
        for domain in domains:
            if domain not in DOMAIN_CONFIG:
                LOGGER.warning("Domain '%s' not in configuration; skipping", domain)
                continue
            LOGGER.info("Processing domain: %s", domain)
            self._process_domain(domain, DOMAIN_CONFIG[domain])

    # ------------------------------------------------------------------
    # Domain processing
    # ------------------------------------------------------------------
    def _process_domain(self, domain: str, config: DomainConfig) -> None:
        subscription_tiers = self._load_subscription_tiers(domain)
        domain_stats: Dict[str, SourceStats] = {}
        output_dir = (TRAINING_ROOT / domain / "processed").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        example_counter = 0

        for raw_dir in config.raw_dirs:
            base_path = (RAW_ROOT / raw_dir).resolve()
            if not base_path.exists():
                LOGGER.warning("Raw directory missing for %s: %s", domain, base_path)
                continue
            for file_path in sorted(base_path.rglob("*")):
                if not file_path.is_file():
                    continue
                suffix = file_path.suffix.lower()
                if suffix in SUPPORTED_CSV_EXTS:
                    examples = self._process_csv(file_path, domain, config)
                elif suffix in SUPPORTED_JSON_EXTS:
                    examples = self._process_json(file_path, domain, config)
                elif suffix in SUPPORTED_PARQUET_EXTS:
                    examples = self._process_parquet(file_path, domain, config)
                elif suffix in SUPPORTED_TEXT_EXTS:
                    examples = self._process_text(file_path, domain, config)
                else:
                    LOGGER.debug("Skipping unsupported file type for %s: %s", domain, file_path)
                    continue

                if not examples:
                    continue
                example_counter += len(examples)
                rel_name = self._relative_source_slug(file_path, base_path)
                out_file = output_dir / f"{domain}_{rel_name}.json"
                self._write_training_file(
                    out_file,
                    domain=domain,
                    description=f"{config.description} derived from {rel_name.replace('_', ' ')}",
                    subscription_tiers=subscription_tiers,
                    examples=examples,
                )
                domain_stats.setdefault(rel_name, SourceStats()).register(len(examples))

        if domain_stats:
            self._write_domain_summary(domain, output_dir, domain_stats)
            self.stats[domain] = domain_stats
            LOGGER.info("Finished domain %s with %s examples", domain, example_counter)
        else:
            LOGGER.warning("No examples produced for domain %s", domain)

    # ------------------------------------------------------------------
    # CSV handling
    # ------------------------------------------------------------------
    def _process_csv(self, file_path: Path, domain: str, config: DomainConfig) -> List[Example]:
        if pd is None:
            LOGGER.warning("pandas not available; skipping CSV %s", file_path)
            return []
        df = self._read_csv_with_fallback(file_path)
        if df is None:
            return []
        if df.empty:
            return []
        sample_size = min(len(df), self.max_per_source)
        sample_df = df.head(sample_size).fillna("")
        examples: List[Example] = []
        base_tags = list(config.base_tags) + ["tabular"]
        for index, row in sample_df.iterrows():
            row_dict = {str(k): str(v).strip() for k, v in row.to_dict().items() if str(v).strip()}
            if not row_dict:
                continue
            prompt = self._build_tabular_prompt(domain, config.prompt_subject, row_dict)
            response = self._build_tabular_response(row_dict)
            difficulty = self._estimate_difficulty(prompt, response, "")
            tier = self._tier_for_difficulty(difficulty, config.tier_thresholds)
            metadata = {
                "source": file_path.name,
                "raw_source_reference": str(file_path.relative_to(RAW_ROOT)),
                "created_at": ISO_NOW,
                "validated": False,
                "token_count": self._estimate_token_count(prompt, response, ""),
                "row_index": int(index),
            }
            example_id = f"{domain}_csv_{self._safe_id(file_path.stem)}_{index:05d}"
            examples.append(
                Example(
                    id=example_id,
                    input=prompt,
                    output=response,
                    context=f"{config.prompt_subject.title()} dataset summary",
                    difficulty_level=difficulty,
                    subscription_tier=tier,
                    tags=base_tags,
                    quality_score=self._estimate_quality(prompt, response),
                    metadata=metadata,
                )
            )
        return examples

    # ------------------------------------------------------------------
    # JSON / JSONL handling
    # ------------------------------------------------------------------
    def _process_json(self, file_path: Path, domain: str, config: DomainConfig) -> List[Example]:
        try:
            records = self._load_json_records(file_path)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning("Failed to parse JSON %s (%s)", file_path, exc)
            return []

        if not records:
            return []

        examples: List[Example] = []
        base_tags = list(config.base_tags) + ["structured"]
        for idx, record in enumerate(records[: self.max_per_source]):
            prompt, response, context_addendum, extra_tags = self._extract_prompt_response(record)
            if not prompt or not response:
                continue
            combined_tags = base_tags + extra_tags
            context = self._build_json_context(config.prompt_subject, context_addendum)
            difficulty = self._estimate_difficulty(prompt, response, context)
            tier = self._tier_for_difficulty(difficulty, config.tier_thresholds)
            metadata = {
                "source": file_path.name,
                "raw_source_reference": str(file_path.relative_to(RAW_ROOT)),
                "created_at": ISO_NOW,
                "validated": False,
                "token_count": self._estimate_token_count(prompt, response, context),
                "record_index": idx,
            }
            example_id = f"{domain}_json_{self._safe_id(file_path.stem)}_{idx:05d}"
            examples.append(
                Example(
                    id=example_id,
                    input=prompt,
                    output=response,
                    context=context,
                    difficulty_level=difficulty,
                    subscription_tier=tier,
                    tags=combined_tags,
                    quality_score=self._estimate_quality(prompt, response),
                    metadata=metadata,
                )
            )
        return examples

    def _process_parquet(self, file_path: Path, domain: str, config: DomainConfig) -> List[Example]:
        if pd is None:
            LOGGER.warning("pandas not available; skipping parquet %s", file_path)
            return []
        try:
            df = pd.read_parquet(file_path)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning("Failed to parse parquet %s (%s)", file_path, exc)
            return []
        if df.empty:
            return []

        records = df.to_dict(orient="records")
        examples: List[Example] = []
        base_tags = list(config.base_tags) + ["structured"]
        for idx, record in enumerate(records[: self.max_per_source]):
            prompt, response, context_addendum, extra_tags = self._extract_prompt_response(record)
            if not prompt or not response:
                continue
            combined_tags = base_tags + extra_tags
            context = self._build_json_context(config.prompt_subject, context_addendum)
            difficulty = self._estimate_difficulty(prompt, response, context)
            tier = self._tier_for_difficulty(difficulty, config.tier_thresholds)
            metadata = {
                "source": file_path.name,
                "raw_source_reference": str(file_path.relative_to(RAW_ROOT)),
                "created_at": ISO_NOW,
                "validated": False,
                "token_count": self._estimate_token_count(prompt, response, context),
                "record_index": idx,
            }
            example_id = f"{domain}_parquet_{self._safe_id(file_path.stem)}_{idx:05d}"
            examples.append(
                Example(
                    id=example_id,
                    input=prompt,
                    output=response,
                    context=context,
                    difficulty_level=difficulty,
                    subscription_tier=tier,
                    tags=combined_tags,
                    quality_score=self._estimate_quality(prompt, response),
                    metadata=metadata,
                )
            )
        return examples

    def _process_text(self, file_path: Path, domain: str, config: DomainConfig) -> List[Example]:
        text = self._read_text_with_fallback(file_path)
        if text is None:
            return []
        paragraphs = self._split_paragraphs(text)
        if not paragraphs:
            return []

        examples: List[Example] = []
        base_tags = list(config.base_tags) + ["narrative"]
        for idx, paragraph in enumerate(paragraphs[: self.max_per_source]):
            snippet = paragraph.strip()
            if not snippet:
                continue
            prompt = self._build_text_prompt(domain, config.prompt_subject, snippet)
            response = self._summarize_text(snippet)
            context = f"Insight distilled from {file_path.name}"
            difficulty = self._estimate_difficulty(prompt, response, context)
            tier = self._tier_for_difficulty(difficulty, config.tier_thresholds)
            metadata = {
                "source": file_path.name,
                "raw_source_reference": str(file_path.relative_to(RAW_ROOT)),
                "created_at": ISO_NOW,
                "validated": False,
                "token_count": self._estimate_token_count(prompt, response, context),
                "paragraph_index": idx,
            }
            example_id = f"{domain}_text_{self._safe_id(file_path.stem)}_{idx:05d}"
            examples.append(
                Example(
                    id=example_id,
                    input=prompt,
                    output=response,
                    context=context,
                    difficulty_level=difficulty,
                    subscription_tier=tier,
                    tags=base_tags,
                    quality_score=self._estimate_quality(prompt, response),
                    metadata=metadata,
                )
            )
        return examples

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _read_csv_with_fallback(self, file_path: Path):
        if pd is None:  # pragma: no cover - guarded higher up
            return None
        encodings = (None, "utf-8", "utf-8-sig", "latin-1", "iso-8859-1", "cp1252")
        fallback_errors: List[str] = []
        for encoding in encodings:
            read_kwargs = {"on_bad_lines": "skip", "engine": "python"}
            if encoding:
                read_kwargs["encoding"] = encoding
            try:
                df = pd.read_csv(file_path, **read_kwargs)
                if encoding:
                    LOGGER.debug("Parsed %s using encoding fallback %s", file_path, encoding)
                return df
            except UnicodeDecodeError as exc:
                fallback_errors.append(f"{encoding or 'default'}: {exc}")
                continue
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Failed to parse CSV %s (%s)", file_path, exc)
                return None
        LOGGER.warning(
            "Failed to parse CSV %s (encodings tried: %s)",
            file_path,
            "; ".join(fallback_errors) or "unknown error",
        )
        return None

    def _load_json_records(self, file_path: Path) -> List[Dict[str, object]]:
        suffix = file_path.suffix.lower()
        if suffix == ".jsonl":
            return self._read_json_lines(file_path)
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            LOGGER.debug("Standard JSON parse failed for %s; attempting JSONL fallback", file_path)
            return self._read_json_lines(file_path)

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            payload = data.get("data")
            if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
                return payload
            return [data]
        return []

    def _read_json_lines(self, file_path: Path) -> List[Dict[str, object]]:
        records: List[Dict[str, object]] = []
        encodings_to_try = ("utf-8", "utf-8-sig", "latin-1")
        for encoding in encodings_to_try:
            try:
                with file_path.open(encoding=encoding) as handle:
                    for line_no, line in enumerate(handle, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                        except json.JSONDecodeError:
                            LOGGER.debug(
                                "Skipping malformed JSON line %s:%s during JSONL fallback", file_path, line_no
                            )
                            continue
                        if isinstance(payload, dict):
                            records.append(payload)
                if records:
                    if encoding != "utf-8":
                        LOGGER.debug("Parsed %s using JSONL encoding fallback %s", file_path, encoding)
                    return records
            except UnicodeDecodeError:
                continue
        return records
    def _extract_prompt_response(self, record: Dict[str, object]) -> (Optional[str], Optional[str], List[str], List[str]):
        if self._has_keys(record, {"article", "text"}) and self._has_keys(record, {"highlights", "summary"}):
            article = str(record.get("article") or record.get("text") or "").strip()
            summary = str(record.get("highlights") or record.get("summary") or "").strip()
            language = str(record.get("language") or "").strip().lower()
            if language and language not in {"en", "english"}:
                return None, None, [], []
            if not language and article and not self._is_likely_english(article):
                return None, None, [], []
            if article and summary:
                prompt = "Summarize the following report into concise executive bullet points.\n\n" + article[:2000]
                bullets = [line.strip() for line in summary.replace("\r", "\n").split("\n") if line.strip()]
                if not bullets:
                    bullets = [segment.strip() for segment in summary.split(".") if segment.strip()]
                response = "\n".join(f"• {bullet}" for bullet in bullets[:6])
                context_bits = []
                if language:
                    context_bits.append(f"language: {language}")
                return prompt, response, context_bits, ["summarization"]

        if self._has_keys(record, {"docstring", "canonical_solution", "prompt"}):
            doc = str(record.get("docstring") or "").strip()
            prompt_body = str(record.get("prompt") or "").strip()
            solution = str(record.get("canonical_solution") or "").strip()
            if doc and prompt_body and solution:
                prompt = f"{doc}\n\nComplete the following function:\n\n{prompt_body}"
                context_bits = ["task: code_generation"]
                return prompt, solution, context_bits, ["code_generation", "python"]

        if self._has_keys(record, {"question", "best_answer"}):
            question = str(record.get("question") or "").strip()
            answer = str(record.get("best_answer") or "").strip()
            if question and answer:
                context_bits = []
                wrong = record.get("wrong_answers")
                if isinstance(wrong, (list, tuple)):
                    preview = ", ".join(str(item).strip() for item in wrong if str(item).strip())
                    if preview:
                        context_bits.append(f"avoid: {preview[:250]}")
                return question, answer, context_bits, ["truthfulness", "reasoning"]

        if self._has_keys(record, {"prompt", "response"}):
            prompt = str(record.get("prompt") or "").strip()
            response = str(record.get("response") or "").strip()
            if prompt and response:
                tag_bits: List[str] = []
                category = record.get("category")
                if isinstance(category, str) and category.strip():
                    tag_bits.append(category.strip().lower().replace(" ", "_"))
                return prompt, response, [], tag_bits

        prompt_fields = ["prompt", "instruction", "question", "input", "title", "task", "query"]
        response_fields = [
            "answer",
            "response",
            "output",
            "completion",
            "text",
            "body",
            "content",
            "best_answer",
            "canonical_solution",
            "highlights",
            "summary",
        ]
        prompt = self._first_non_empty(record, prompt_fields)
        response = self._first_non_empty(record, response_fields)
        if not prompt and isinstance(record.get("prompt"), dict):
            prompt = json.dumps(record["prompt"])
        if not response and isinstance(record.get("response"), dict):
            response = json.dumps(record["response"])

        context_bits: List[str] = []
        tag_bits: List[str] = []
        for key in ("category", "topic", "tags", "industry", "segment"):
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                context_bits.append(f"{key}: {value.strip()}")
                tag_bits.append(value.strip().lower().replace(" ", "_"))
            elif isinstance(value, list):
                joined = ", ".join(str(item) for item in value if str(item).strip())
                if joined:
                    context_bits.append(f"{key}: {joined}")
                    tag_bits.extend(str(item).lower().replace(" ", "_") for item in value if str(item).strip())

        return prompt, response, context_bits, tag_bits

    def _first_non_empty(self, record: Dict[str, object], fields: Sequence[str]) -> Optional[str]:
        for field in fields:
            value = record.get(field)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (int, float)) and not (isinstance(value, float) and math.isnan(value)):
                return str(value)
        return None

    def _read_text_with_fallback(self, file_path: Path) -> Optional[str]:
        encodings = ("utf-8", "utf-8-sig", "latin-1", "iso-8859-1")
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Failed to read text %s (%s)", file_path, exc)
                return None
        LOGGER.warning("Failed to read text %s (encoding fallback exhausted)", file_path)
        return None

    def _build_text_prompt(self, domain: str, subject: str, paragraph: str) -> str:
        trimmed = paragraph[:1500]
        return (
            f"You are preparing a {subject.lower()} briefing for the {domain.replace('_', ' ')} domain. "
            f"Review the following excerpt and produce actionable insights.\n\n{trimmed}"
        )

    def _summarize_text(self, text: str, max_sentences: int = 3) -> str:
        sentences = [segment.strip() for segment in text.replace("\n", " ").split(".") if segment.strip()]
        selected = sentences[:max_sentences] or [text.strip()[:240]]
        return " ".join(selected)

    def _split_paragraphs(self, text: str) -> List[str]:
        return [segment.strip() for segment in text.split("\n\n") if segment.strip()]

    def _has_keys(self, record: Dict[str, object], keys: Set[str]) -> bool:
        return any(key in record for key in keys)

    def _is_likely_english(self, text: str) -> bool:
        if not text:
            return False
        ascii_chars = sum(1 for char in text if ord(char) < 128)
        return ascii_chars / max(len(text), 1) >= 0.6

    def _build_tabular_prompt(self, domain: str, subject: str, row: Dict[str, str]) -> str:
        preview = "\n".join(f"- {key}: {value}" for key, value in list(row.items())[:12])
        return (
            f"You are preparing a {subject} briefing for the {domain.replace('_', ' ')} domain. "
            f"Analyze the following dataset row and craft actionable insights.\n\n{preview}"
        )

    def _build_tabular_response(self, row: Dict[str, str]) -> str:
        keys = list(row.keys())[:5]
        bullets = [f"• {key.title()}: {row[key]}" for key in keys]
        return "\n".join(bullets)

    def _build_json_context(self, subject: str, context_bits: List[str]) -> str:
        if not context_bits:
            return f"Structured {subject} example"
        return f"Structured {subject} example\n" + "\n".join(context_bits)

    def _write_training_file(
        self,
        output_path: Path,
        *,
        domain: str,
        description: str,
        subscription_tiers: Dict[str, object],
        examples: Iterable[Example],
    ) -> None:
        examples_list = [example.to_dict() for example in examples]
        if not examples_list:
            return
        tier_counts = self._count_tiers(examples_list)
        payload = {
            "domain": domain,
            "description": description,
            "version": "2.0.0",
            "total_examples": len(examples_list),
            "tier_distribution": tier_counts,
            "subscription_tiers": subscription_tiers,
            "training_examples": examples_list,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        LOGGER.info("Wrote %s examples to %s", len(examples_list), output_path)

    def _write_domain_summary(self, domain: str, output_dir: Path, stats: Dict[str, SourceStats]) -> None:
        summary_path = output_dir / "SUMMARY.json"
        payload = {
            "generated_at": ISO_NOW,
            "max_per_source": self.max_per_source,
            "sources": {name: {"produced": stat.produced, "skipped": stat.skipped} for name, stat in stats.items()},
        }
        with summary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        LOGGER.info("Summary for %s written to %s", domain, summary_path)

    def _load_subscription_tiers(self, domain: str) -> Dict[str, object]:
        template_path = TRAINING_ROOT / domain / "template.json"
        if not template_path.exists():
            LOGGER.warning("Template missing for %s; using default tiers", domain)
            return {
                "basic": {"system_prompt": "You are a helpful assistant.", "max_complexity": 3},
                "professional": {"system_prompt": "You are an expert consultant.", "max_complexity": 7},
                "enterprise": {"system_prompt": "You advise executive stakeholders.", "max_complexity": 10},
            }
        with template_path.open(encoding="utf-8") as handle:
            template = json.load(handle)
        tiers = template.get("subscription_tiers")
        if isinstance(tiers, dict):
            return tiers
        LOGGER.warning("subscription_tiers not found in template for %s; using default", domain)
        return {
            "basic": {"system_prompt": "You are a helpful assistant.", "max_complexity": 3},
            "professional": {"system_prompt": "You are an expert consultant.", "max_complexity": 7},
            "enterprise": {"system_prompt": "You advise executive stakeholders.", "max_complexity": 10},
        }

    def _estimate_difficulty(self, prompt: str, response: str, context: str) -> int:
        length = len(prompt.split()) + len(response.split()) + len(context.split())
        if "analysis" in prompt.lower() or "strategy" in prompt.lower():
            length += 25
        if "architecture" in response.lower() or "framework" in response.lower():
            length += 20
        if length < 120:
            return 3
        if length < 250:
            return 6
        return min(10, max(7, round(length / 80)))

    def _tier_for_difficulty(self, difficulty: int, thresholds: Sequence[int]) -> str:
        low, mid = thresholds
        if difficulty <= low:
            return "basic"
        if difficulty <= mid:
            return "professional"
        return "enterprise"

    def _estimate_quality(self, prompt: str, response: str) -> float:
        signal = len(response.split())
        noise = prompt.lower().count("???")
        score = max(0.0, min(10.0, 7.5 + math.log1p(signal) - noise))
        return round(score, 2)

    def _estimate_token_count(self, prompt: str, response: str, context: str) -> int:
        total_chars = len(prompt) + len(response) + len(context)
        return int(total_chars * 0.75 / 4)

    def _count_tiers(self, examples: Sequence[Dict[str, object]]) -> Dict[str, int]:
        counts = {"basic": 0, "professional": 0, "enterprise": 0}
        for example in examples:
            tier = str(example.get("subscription_tier", "basic"))
            counts[tier] = counts.get(tier, 0) + 1
        return counts

    def _relative_source_slug(self, file_path: Path, base_path: Path) -> str:
        relative = file_path.relative_to(base_path)
        slug_parts: List[str] = []
        for part in relative.parts:
            if part.endswith(file_path.suffix):
                slug_parts.append(self._safe_id(Path(part).stem))
            else:
                slug_parts.append(self._safe_id(part))
        return "_".join(slug_parts)

    def _safe_id(self, text: str) -> str:
        filtered = [char.lower() if char.isalnum() else "_" for char in text]
        return "".join(filtered).strip("_") or "source"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process BookGen domain datasets")
    parser.add_argument(
        "--domains",
        nargs="*",
        help="Subset of domains to process. Defaults to all configured domains.",
    )
    parser.add_argument(
        "--max-per-source",
        type=int,
        default=400,
        help="Maximum number of examples per source file",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s %(message)s",
    )
    domains = args.domains or sorted(DOMAIN_CONFIG.keys())
    processor = DomainDataProcessor(max_per_source=args.max_per_source, seed=args.seed)
    processor.process(domains)


if __name__ == "__main__":
    main()
