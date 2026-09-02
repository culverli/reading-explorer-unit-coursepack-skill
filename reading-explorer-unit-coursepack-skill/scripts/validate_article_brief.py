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
]
STATUSES = {"found", "not_supplied", "not_applicable", "wrong_unit"}
LAYOUT_SELECTION_STATUSES = {"resolved", "portable_standard_only", "teacher_supplied"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "re.article-project-brief.v2":
        errors.append("schema_version must be re.article-project-brief.v2")

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

    layout = data.get("layout_exemplars", {})
    if not isinstance(layout, dict):
        errors.append("layout_exemplars is required")
    else:
        if not str(layout.get("index_path", "")).strip():
            errors.append("layout_exemplars.index_path must be recorded")
        if layout.get("path_base") != "workspace_root":
            errors.append("layout_exemplars.path_base must be workspace_root")
        status = layout.get("selection_status")
        if status not in LAYOUT_SELECTION_STATUSES:
            errors.append(
                "layout_exemplars.selection_status must be one of "
                f"{sorted(LAYOUT_SELECTION_STATUSES)}"
            )
        selected_ids = layout.get("selected_ids")
        if not isinstance(selected_ids, dict):
            errors.append("layout_exemplars.selected_ids must be an object grouped by artifact type")
        else:
            for artifact_type in ("student_practice_book", "answer_key", "teaching_outline"):
                ids = selected_ids.get(artifact_type)
                if not isinstance(ids, list):
                    errors.append(f"layout_exemplars.selected_ids.{artifact_type} must be a list")
                elif len(ids) > 2:
                    errors.append(f"layout_exemplars.selected_ids.{artifact_type} may contain at most two IDs")
                elif status in {"resolved", "teacher_supplied"} and outputs.get(artifact_type) is True and not ids:
                    errors.append(
                        f"layout_exemplars.selected_ids.{artifact_type} is required for the selected layout status"
                    )

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
