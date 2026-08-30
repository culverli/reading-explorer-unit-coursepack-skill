#!/usr/bin/env python3
"""Audit generated Practice Book or Teacher Guide DOCX against a v2 coursepack spec."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
PLACEHOLDER_RE = re.compile(r"\b(?:needs_review|todo|tbd|placeholder)\b", re.I)
CAPS_RE = re.compile(r"\b[A-Z]{3,}\b")
CAPS_ALLOW = {"RE", "SYN", "ANS", "DOCX", "PDF", "PPT", "PPTX", "QR"}

STUDENT_BANNED = (
    "productive",
    "recognition",
    "core active",
    "today i will learn",
    "now i can",
    "self-check",
    "self check",
    "before you finish",
    "assign after",
    "next class use",
    "next lesson use",
    "checkpoint",
    "source id",
    "teacher will score",
    "teacher awards",
    "team score",
    "self-score",
    "pair check",
    "random check",
    "class example",
    "classroom display ppt",
    "production stage",
    "pilot purpose",
    "answer key",
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Top-level JSON in {path} must be an object")
    return value


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def qn(local: str) -> str:
    return f"{{{W_NS}}}{local}"


def read_docx(path: Path) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"Corrupt ZIP member: {bad}")
            names = set(archive.namelist())
            xml = archive.read("word/document.xml")
    except (OSError, zipfile.BadZipFile, KeyError) as exc:
        raise ValueError(f"Cannot read DOCX {path}: {exc}") from exc

    root = ET.fromstring(xml)
    paragraphs: list[dict[str, str]] = []
    for paragraph in root.findall(".//w:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))
        p_style = paragraph.find("./w:pPr/w:pStyle", NS)
        style = p_style.get(qn("val"), "") if p_style is not None else ""
        if text.strip():
            paragraphs.append({"text": text.strip(), "style": style})
    full_text = "\n".join(row["text"] for row in paragraphs)

    section = root.find(".//w:sectPr", NS)
    margins: dict[str, float] = {}
    if section is not None:
        pg_mar = section.find("w:pgMar", NS)
        if pg_mar is not None:
            for edge in ("top", "bottom", "left", "right"):
                raw = pg_mar.get(qn(edge))
                if raw and raw.lstrip("-").isdigit():
                    margins[edge] = int(raw) / 1440.0

    tracked = len(root.findall(".//w:ins", NS)) + len(root.findall(".//w:del", NS))
    comment_parts = sorted(name for name in names if "comment" in name.lower())
    return {
        "paragraphs": paragraphs,
        "text": full_text,
        "normalized": normalize(full_text),
        "margins": margins,
        "tracked_changes": tracked,
        "comment_parts": comment_parts,
    }


def add_issue(items: list[dict[str, Any]], severity: str, code: str, message: str, **details: Any) -> None:
    items.append({"severity": severity, "code": code, "message": message, **details})


def ordered_positions(haystack: str, needles: list[str]) -> tuple[bool, list[int]]:
    positions: list[int] = []
    cursor = 0
    for needle in needles:
        found = haystack.find(normalize(needle), cursor)
        positions.append(found)
        if found < 0:
            continue
        cursor = found + len(normalize(needle))
    present = all(position >= 0 for position in positions)
    ordered = present and positions == sorted(positions)
    return ordered, positions


def all_exercises(spec: dict[str, Any]) -> list[dict[str, Any]]:
    exercises: list[dict[str, Any]] = []
    for section in spec.get("practice_book", {}).get("sections", []):
        if isinstance(section, dict):
            exercises.extend(item for item in section.get("exercises", []) if isinstance(item, dict))
    return exercises


def common_audit(doc: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    if doc["tracked_changes"]:
        add_issue(issues, "error", "tracked_changes", "DOCX contains tracked changes")
    if doc["comment_parts"]:
        add_issue(issues, "error", "comments", "DOCX contains comment parts", parts=doc["comment_parts"])
    if PLACEHOLDER_RE.search(doc["text"]):
        add_issue(issues, "error", "placeholder", "DOCX contains unresolved placeholder text")
    for paragraph in doc["paragraphs"]:
        text = paragraph["text"]
        if len(text) <= 100:
            for token in CAPS_RE.findall(text):
                if token not in CAPS_ALLOW:
                    add_issue(
                        issues,
                        "error",
                        "all_caps_display",
                        f"All-cap display token found: {token}",
                        paragraph=text,
                    )


def audit_practice_book(
    doc: dict[str, Any], spec: dict[str, Any], issues: list[dict[str, Any]]
) -> None:
    text = doc["normalized"]
    title = str(spec.get("title", ""))
    if title and (normalize(title) not in text or "practice book" not in text):
        add_issue(issues, "error", "practice_book_title", "Approved Practice Book title is missing")

    expected = all_exercises(spec)
    headings = [f"Exercise {index} · {item.get('title', '')}" for index, item in enumerate(expected, 1)]
    ordered, positions = ordered_positions(text, headings)
    if not ordered:
        add_issue(
            issues,
            "error",
            "exercise_sequence",
            "Practice Book exercise headings are missing or out of order",
            expected=headings,
            positions=positions,
        )
    for exercise in expected:
        instruction = str(exercise.get("instruction_en", ""))
        if instruction and normalize(instruction) not in text:
            add_issue(
                issues,
                "error",
                "missing_instruction",
                f"Missing student instruction for {exercise.get('exercise_id')}",
            )

    for phrase in STUDENT_BANNED:
        if phrase in text:
            add_issue(issues, "error", "student_metalanguage", f"Banned student phrase found: {phrase}")
    if re.search(r"\b(?:lesson|stage|checkpoint)[ -]?\d+\b", text):
        add_issue(issues, "error", "internal_route", "Student book exposes lesson/stage/checkpoint numbering")

    target_margins = {"left": 0.62, "right": 0.62, "top": 0.55, "bottom": 0.55}
    for edge, expected_value in target_margins.items():
        observed = doc["margins"].get(edge)
        if observed is None or abs(observed - expected_value) > 0.05:
            add_issue(
                issues,
                "error",
                "practice_book_geometry",
                f"{edge} margin must be {expected_value:.2f} ± 0.05 inches",
                observed=observed,
            )


def audit_teacher_guide(
    doc: dict[str, Any], spec: dict[str, Any], issues: list[dict[str, Any]]
) -> None:
    text = doc["normalized"]
    lessons = [item for item in spec.get("lessons", []) if isinstance(item, dict)]
    lesson_titles = [str(item.get("title", "")) for item in lessons]
    ordered, positions = ordered_positions(text, lesson_titles)
    if not ordered:
        add_issue(
            issues,
            "error",
            "lesson_sequence",
            "Teacher Guide lesson titles are missing or out of order",
            expected=lesson_titles,
            positions=positions,
        )

    for index, lesson in enumerate(lessons):
        title = str(lesson.get("title", ""))
        next_title = lesson_titles[index + 1] if index + 1 < len(lesson_titles) else ""
        start = text.find(normalize(title))
        end = text.find(normalize(next_title), start + 1) if next_title else len(text)
        segment = text[start:end] if start >= 0 and end >= 0 else ""
        if len(segment) < 900:
            add_issue(
                issues,
                "error",
                "thin_lesson_design",
                f"Lesson section is too thin to be a complete design: {title}",
                normalized_characters=len(segment),
            )
        for phrase in (lesson.get("materials"), lesson.get("preparation"), lesson.get("board_plan")):
            if isinstance(phrase, str) and phrase.strip() and normalize(phrase) not in segment:
                add_issue(
                    issues,
                    "error",
                    "missing_teacher_detail",
                    f"Teacher Guide omits a required lesson detail for {title}",
                    detail=phrase,
                )
        stages = [stage for stage in lesson.get("stages", []) if isinstance(stage, dict)]
        if not stages or stages[0].get("stage_type") != "lead_in":
            add_issue(issues, "error", "lead_in_spec", f"Spec lacks lead-in for {title}")
        for stage in stages:
            stage_title = str(stage.get("title", ""))
            if stage_title and normalize(stage_title) not in segment:
                add_issue(
                    issues,
                    "error",
                    "missing_stage",
                    f"Teacher Guide omits stage '{stage_title}' in {title}",
                )
            teacher_move = str(stage.get("teacher_move_cn", ""))
            if teacher_move and normalize(teacher_move) not in segment:
                add_issue(
                    issues,
                    "error",
                    "missing_teacher_move",
                    f"Teacher move is missing for stage '{stage_title}'",
                )
        homework = lesson.get("homework", {})
        for key in ("title", "teacher_verification", "next_lesson_use"):
            phrase = homework.get(key) if isinstance(homework, dict) else ""
            if isinstance(phrase, str) and phrase.strip() and normalize(phrase) not in segment:
                add_issue(
                    issues,
                    "error",
                    "missing_homework_route",
                    f"Teacher Guide omits homework {key} for {title}",
                )

    if "answer key" not in text and "答案" not in text:
        add_issue(issues, "error", "missing_answer_key", "Teacher Guide lacks an answer/judgment section")
    for answer_ref in spec.get("teacher_answers", {}):
        if normalize(answer_ref) not in text:
            add_issue(issues, "error", "missing_answer_ref", f"Teacher Guide omits {answer_ref}")


def audit(path: Path, role: str, spec: dict[str, Any]) -> dict[str, Any]:
    doc = read_docx(path)
    issues: list[dict[str, Any]] = []
    common_audit(doc, issues)
    if role == "practice-book":
        audit_practice_book(doc, spec, issues)
    else:
        audit_teacher_guide(doc, spec, issues)
    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    return {
        "schema_version": "re.docx-audit.v1",
        "file": str(path),
        "role": role,
        "status": "pass" if not errors else "fail",
        "summary": {"errors": len(errors), "warnings": len(warnings)},
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--role", required=True, choices=("practice-book", "teacher-guide"))
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(args.docx, args.role, load_json(args.spec))
    except ValueError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['status'].upper()}: {report['role']} | {report['file']}")
        for item in report["issues"]:
            print(f"{item['severity'].upper()} {item['code']}: {item['message']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
