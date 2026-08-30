#!/usr/bin/env python3
"""Verify sentence-level source fidelity for Reading Explorer artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


QUOTE_DASH_MAP = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
    }
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Top-level JSON value in {path} must be an object")
    return data


def whitespace_normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def formatting_normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(QUOTE_DASH_MAP)
    return re.sub(r"\s+", " ", text).strip()


def collect_sentences(ledger: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    sentences: list[dict[str, Any]] = []
    errors: list[str] = []
    for component in ledger.get("components", []):
        component_id = component.get("component_id")
        for region in component.get("regions", []):
            for sentence in region.get("sentences", []):
                sentence_id = sentence.get("sentence_id")
                text = sentence.get("text")
                if not sentence_id or not isinstance(text, str):
                    errors.append(f"Invalid sentence record in component {component_id}")
                    continue
                sentences.append(
                    {
                        **sentence,
                        "component_id": component_id,
                        "component_order": component.get("order", 0),
                        "region_id": region.get("region_id"),
                        "region_type": region.get("region_type"),
                        "region_order": region.get("order", 0),
                    }
                )
    return sentences, errors


def add_issue(issues: list[dict[str, Any]], code: str, message: str, **details: Any) -> None:
    issues.append({"severity": "error", "code": code, "message": message, **details})


def detect_boundary_issue(
    source_order: list[str],
    source_by_id: dict[str, dict[str, Any]],
    usage_items: list[dict[str, Any]],
    issues: list[dict[str, Any]],
) -> None:
    for item in usage_items:
        if item.get("mode") != "verbatim" or not isinstance(item.get("text"), str):
            continue
        sentence_id = item.get("sentence_id")
        if sentence_id not in source_by_id or sentence_id not in source_order:
            continue
        used = formatting_normalize(item["text"])
        position = source_order.index(sentence_id)
        for width in (2, 3):
            adjacent = source_order[position : position + width]
            if len(adjacent) != width:
                continue
            joined = formatting_normalize(" ".join(source_by_id[x]["text"] for x in adjacent))
            if used == joined:
                add_issue(
                    issues,
                    "possible_sentence_merge",
                    f"Usage {sentence_id} appears to merge {width} source sentences",
                    sentence_ids=adjacent,
                )

    verbatim = [item for item in usage_items if item.get("mode") == "verbatim"]
    for source_id, source in source_by_id.items():
        fragments = [
            item
            for item in verbatim
            if item.get("sentence_id") == source_id and isinstance(item.get("text"), str)
        ]
        if len(fragments) > 1:
            joined = formatting_normalize(" ".join(item["text"] for item in fragments))
            if joined == formatting_normalize(source["text"]):
                add_issue(
                    issues,
                    "possible_sentence_split",
                    f"Source sentence {source_id} appears to be split across usage items",
                    sentence_id=source_id,
                )


def verify(ledger: dict[str, Any], usage: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    sentences, ledger_errors = collect_sentences(ledger)
    for message in ledger_errors:
        add_issue(issues, "invalid_ledger_record", message)

    source_ids = [record["sentence_id"] for record in sentences]
    duplicate_source_ids = [key for key, count in Counter(source_ids).items() if count > 1]
    for sentence_id in duplicate_source_ids:
        add_issue(issues, "duplicate_source_id", f"Duplicate source sentence ID: {sentence_id}")

    source_by_id = {record["sentence_id"]: record for record in sentences}
    required_components = set(usage.get("required_components", []))
    article_sentences = [
        record
        for record in sentences
        if record.get("region_type") == "article_body"
        and (not required_components or record.get("component_id") in required_components)
    ]
    article_sentences.sort(
        key=lambda item: (
            item.get("component_order", 0),
            item.get("region_order", 0),
            item.get("order", 0),
        )
    )
    expected_ids = [record["sentence_id"] for record in article_sentences]

    usage_items = usage.get("items", [])
    if not isinstance(usage_items, list):
        add_issue(issues, "invalid_usage_items", "Usage items must be a list")
        usage_items = []

    verbatim_items: list[dict[str, Any]] = []
    for item in usage_items:
        sentence_id = item.get("sentence_id")
        mode = item.get("mode")
        if sentence_id not in source_by_id:
            add_issue(issues, "unknown_sentence_id", f"Unknown source sentence ID: {sentence_id}")
            continue
        if mode == "adapted":
            if not item.get("adaptation_note"):
                add_issue(
                    issues,
                    "missing_adaptation_note",
                    f"Adapted item {sentence_id} has no adaptation note",
                )
            continue
        if mode == "reference_only":
            continue
        if mode != "verbatim":
            add_issue(issues, "invalid_mode", f"Invalid usage mode for {sentence_id}: {mode}")
            continue
        verbatim_items.append(item)
        source_text = source_by_id[sentence_id]["text"]
        used_text = item.get("text")
        if not isinstance(used_text, str):
            add_issue(issues, "missing_usage_text", f"Missing text for verbatim item {sentence_id}")
        elif whitespace_normalize(used_text) == whitespace_normalize(source_text):
            pass
        elif formatting_normalize(used_text) == formatting_normalize(source_text):
            warnings.append(
                {
                    "severity": "warning",
                    "code": "formatting_only_difference",
                    "message": f"Typography differs for {sentence_id}",
                    "sentence_id": sentence_id,
                }
            )
        else:
            add_issue(
                issues,
                "modified_verbatim_text",
                f"Verbatim text differs from source for {sentence_id}",
                sentence_id=sentence_id,
                source_text=source_text,
                used_text=used_text,
            )

    coverage_policy = usage.get("coverage_policy")
    used_ids = [item.get("sentence_id") for item in verbatim_items]
    if coverage_policy == "all_article_sentences":
        for record in article_sentences:
            if record.get("review_status") != "verified":
                add_issue(
                    issues,
                    "unreviewed_required_source",
                    f"Required source sentence is not verified: {record['sentence_id']}",
                    review_status=record.get("review_status"),
                )
        missing = [sentence_id for sentence_id in expected_ids if sentence_id not in used_ids]
        for sentence_id in missing:
            add_issue(issues, "missing_required_sentence", f"Missing required sentence: {sentence_id}")
        duplicates = [key for key, count in Counter(used_ids).items() if count > 1]
        for sentence_id in duplicates:
            add_issue(issues, "duplicate_usage", f"Sentence used more than once: {sentence_id}")
        if usage.get("enforce_source_order", True):
            observed = [sentence_id for sentence_id in used_ids if sentence_id in expected_ids]
            expected_observed = [sentence_id for sentence_id in expected_ids if sentence_id in observed]
            if observed != expected_observed:
                add_issue(issues, "source_order_mismatch", "Verbatim sentences are not in source order")
    elif coverage_policy != "selected_excerpts":
        add_issue(issues, "invalid_coverage_policy", f"Invalid coverage policy: {coverage_policy}")

    detect_boundary_issue(expected_ids, source_by_id, verbatim_items, issues)

    return {
        "schema_version": "re.source-report.v1",
        "artifact_id": usage.get("artifact_id"),
        "status": "pass" if not issues else "fail",
        "summary": {
            "source_sentences": len(sentences),
            "required_article_sentences": len(expected_ids),
            "verbatim_usage_items": len(verbatim_items),
            "errors": len(issues),
            "warnings": len(warnings),
        },
        "errors": issues,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--usage", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        report = verify(load_json(args.ledger), load_json(args.usage))
    except ValueError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
