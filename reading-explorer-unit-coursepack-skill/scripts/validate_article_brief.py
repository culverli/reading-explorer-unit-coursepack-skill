#!/usr/bin/env python3
"""Validate the decisions required before article-coursepack production."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SLOTS = [
    "01_textbook",
    "02_worksheet",
    "03_bloom",
    "04_vocabulary",
    "05_pre_post",
    "06_grammar_cloze",
    "07_official_extra",
    "08_teacher_notes",
    "09_layout_authority",
]
STATUSES = {"found", "not_supplied", "not_applicable", "wrong_unit"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "re.article-project-brief.v1":
        errors.append("schema_version must be re.article-project-brief.v1")

    article = data.get("article", {})
    for key in ("level", "unit_code", "title"):
        if not str(article.get(key, "")).strip() or article.get(key) == "needs_review":
            errors.append(f"article.{key} must be confirmed")

    package = data.get("source_package", {})
    for slot in SLOTS:
        record = package.get(slot)
        if not isinstance(record, dict):
            errors.append(f"source_package.{slot} is required")
            continue
        status = record.get("status")
        if status not in STATUSES:
            errors.append(f"source_package.{slot}.status must be one of {sorted(STATUSES)}")
        files = record.get("files")
        if not isinstance(files, list):
            errors.append(f"source_package.{slot}.files must be a list")
        elif status == "found" and not files:
            errors.append(f"source_package.{slot} is found but has no files")
    if package.get("01_textbook", {}).get("status") != "found":
        errors.append("01_textbook must be found before dependent production")

    design = data.get("reading_design", {})
    if design.get("mode") not in {"intensive", "extensive"}:
        errors.append("reading_design.mode must be intensive or extensive")
    if not isinstance(design.get("lesson_count"), int) or design.get("lesson_count", 0) < 1:
        errors.append("reading_design.lesson_count must be a positive integer")
    if not isinstance(design.get("lesson_minutes"), int) or design.get("lesson_minutes", 0) < 1:
        errors.append("reading_design.lesson_minutes must be a positive integer")
    flow = design.get("teacher_flow")
    if not isinstance(flow, list) or not any(str(step).strip() for step in flow):
        errors.append("reading_design.teacher_flow must contain the teacher's intended sequence")
    if design.get("assignment_balance") not in {"majority_homework", "custom"}:
        errors.append("reading_design.assignment_balance must be majority_homework or custom")

    outputs = data.get("outputs", {})
    for key in ("student_practice_book", "answer_key", "teaching_outline"):
        if outputs.get(key) is not True:
            errors.append(f"outputs.{key} must be true for the default three-piece set")

    if data.get("confirmed_by_teacher") is not True:
        errors.append("confirmed_by_teacher must be true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.brief.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {args.brief}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
