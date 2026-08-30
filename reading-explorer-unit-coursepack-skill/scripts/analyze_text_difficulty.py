#!/usr/bin/env python3
"""Create a descriptive Reading A/B difficulty profile from a verified ledger."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Any


WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
CLAUSE_MARKERS = {
    "although",
    "as",
    "because",
    "before",
    "but",
    "if",
    "once",
    "since",
    "so",
    "than",
    "that",
    "though",
    "unless",
    "until",
    "when",
    "where",
    "whereas",
    "whether",
    "which",
    "while",
    "who",
    "whom",
    "whose",
    "why",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Ledger must be a JSON object")
    return value


def words(text: str) -> list[str]:
    return [token.lower().replace("’", "'") for token in WORD_RE.findall(text)]


def upper_quartile(values: list[int]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(0.75 * len(ordered)) - 1)
    return float(ordered[index])


def load_known_words(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    try:
        return set(words(path.read_text(encoding="utf-8")))
    except OSError as exc:
        raise ValueError(f"Cannot read cohort lexicon {path}: {exc}") from exc


def collect_article_sentences(ledger: dict[str, Any], component_id: str) -> list[dict[str, Any]]:
    for component in ledger.get("components", []):
        if component.get("component_id") != component_id:
            continue
        records: list[dict[str, Any]] = []
        regions = sorted(component.get("regions", []), key=lambda item: item.get("order", 0))
        for region in regions:
            if region.get("region_type") != "article_body":
                continue
            records.extend(sorted(region.get("sentences", []), key=lambda item: item.get("order", 0)))
        return records
    raise ValueError(f"Component not found: {component_id}")


def analyze(
    ledger: dict[str, Any], component_id: str, known_words: set[str] | None
) -> dict[str, Any]:
    sentences = collect_article_sentences(ledger, component_id)
    if not sentences:
        raise ValueError(f"No article_body sentences found for {component_id}")

    sentence_rows: list[dict[str, Any]] = []
    all_words: list[str] = []
    for sentence in sentences:
        sentence_words = words(sentence.get("text", ""))
        all_words.extend(sentence_words)
        markers = [token for token in sentence_words if token in CLAUSE_MARKERS]
        reasons: list[str] = []
        if len(sentence_words) > 20:
            reasons.append("over_20_words")
        elif len(sentence_words) > 15:
            reasons.append("over_15_words")
        if len(markers) >= 2:
            reasons.append("multiple_clause_markers")
        sentence_rows.append(
            {
                "sentence_id": sentence.get("sentence_id"),
                "word_count": len(sentence_words),
                "clause_markers": markers,
                "reasons": reasons,
            }
        )

    lengths = [row["word_count"] for row in sentence_rows]
    unique_words = set(all_words)
    marker_count = sum(len(row["clause_markers"]) for row in sentence_rows)
    demanding = [row for row in sentence_rows if row["reasons"]]
    demanding.sort(
        key=lambda row: (row["word_count"] + 4 * len(row["clause_markers"])), reverse=True
    )

    coverage = None
    unknown_words: list[str] = []
    if known_words is not None and all_words:
        known_count = sum(1 for token in all_words if token in known_words)
        coverage = round(known_count / len(all_words), 4)
        unknown_words = sorted(unique_words - known_words)

    return {
        "schema_version": "re.difficulty-profile.v1",
        "unit_id": ledger.get("unit_id"),
        "component_id": component_id,
        "status": "quantitative_complete_human_review_required",
        "quantitative": {
            "sentence_count": len(sentence_rows),
            "word_count": len(all_words),
            "unique_word_count": len(unique_words),
            "mean_sentence_words": round(statistics.mean(lengths), 2),
            "median_sentence_words": round(statistics.median(lengths), 2),
            "upper_quartile_sentence_words": upper_quartile(lengths),
            "max_sentence_words": max(lengths),
            "sentences_over_15_words": sum(length > 15 for length in lengths),
            "sentences_over_20_words": sum(length > 20 for length in lengths),
            "type_token_ratio": round(len(unique_words) / len(all_words), 4),
            "long_word_ratio": round(
                sum(len(token.replace("'", "")) >= 7 for token in all_words) / len(all_words), 4
            ),
            "clause_markers_per_sentence": round(marker_count / len(sentence_rows), 3),
            "cohort_lexicon_coverage": coverage,
            "possible_unknown_words": unknown_words,
            "demanding_sentences": demanding[:5],
        },
        "human_review": {
            "discourse_pattern": "needs_review",
            "background_knowledge_load": "needs_review",
            "visual_load": "needs_review",
            "task_demand": "needs_review",
            "teaching_implications": [],
        },
        "interpretation_boundary": (
            "Descriptive metrics only. Do not infer learner grade, CEFR level, or teaching time "
            "without source-page and cohort review."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--known-words", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        report = analyze(
            load_json(args.ledger), args.component, load_known_words(args.known_words)
        )
    except ValueError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
