#!/usr/bin/env python3
"""Validate the approved Reading Explorer Teacher Guide + Practice Book contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PLACEHOLDER_RE = re.compile(r"\b(?:needs_review|todo|tbd|placeholder)\b", re.I)
EXERCISE_ID_RE = re.compile(r"^PB(\d{2,3})$")
ALL_CAPS_RE = re.compile(r"\b[A-Z]{3,}\b")

REQUIRED_ARTIFACTS = {
    "teacher_unit_guide": True,
    "student_practice_book": True,
    "separate_homework_booklet": False,
    "classroom_display_ppt": False,
    "fixed_activity_kit": False,
}

TASK_FAMILIES = {
    "english_definitions",
    "collocations_chunks",
    "context_use",
    "word_form",
    "error_repair",
    "sentence_combining",
    "sentence_transformation",
    "text_order_function",
    "summary_cloze",
    "mixed_review",
    "evidence_judgment",
    "short_transfer",
    "gist",
    "detail_evidence",
    "inference",
    "retell_preparation",
    "listening_viewing",
    "writing_process",
}

LESSON_TYPES = {
    "meaning_first",
    "close_study",
    "language_consolidation",
    "transfer_reading",
    "video_listening",
    "integrated_output",
    "retrieval_feedback",
}

COMPONENTS = {
    "reading_a",
    "reading_b",
    "video_listening",
    "integrated_output",
    "review_feedback",
}

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
)

ACTIVITY_QUALITY = {
    "right_wrong",
    "scoring",
    "evidence",
    "construction_repair",
    "strategy",
    "time_pressure",
    "competition",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Coursepack specification must be a JSON object")
    return value


def add_issue(items: list[dict[str, Any]], code: str, message: str, **details: Any) -> None:
    items.append({"code": code, "message": message, **details})


def required_text(
    record: dict[str, Any], key: str, path: str, errors: list[dict[str, Any]]
) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        add_issue(errors, "missing_text", f"Missing non-empty {key} at {path}")
        return ""
    return value.strip()


def required_list(
    record: dict[str, Any], key: str, path: str, errors: list[dict[str, Any]]
) -> list[Any]:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        add_issue(errors, "missing_list", f"Missing non-empty {key} at {path}")
        return []
    return value


def find_placeholders(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(find_placeholders(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_placeholders(child, f"{path}[{index}]"))
    elif isinstance(value, str) and PLACEHOLDER_RE.search(value):
        found.append(path)
    return found


def student_text(record: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "title",
        "instruction_en",
        "instruction_cn",
        "example",
        "inline_support",
        "student_visible_text",
    ):
        value = record.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts)


def validate_exercises(
    practice_book: Any,
    answers: Any,
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if not isinstance(practice_book, dict):
        add_issue(errors, "missing_practice_book", "practice_book must be an object")
        return {}
    required_text(practice_book, "title", "$.practice_book", errors)
    required_text(practice_book, "reading_body_private_route", "$.practice_book", errors)
    sections = required_list(practice_book, "sections", "$.practice_book", errors)
    answer_map = answers if isinstance(answers, dict) else {}
    if not isinstance(answers, dict):
        add_issue(errors, "invalid_teacher_answers", "teacher_answers must be an object")

    exercises: list[dict[str, Any]] = []
    for s_index, section in enumerate(sections):
        path = f"$.practice_book.sections[{s_index}]"
        if not isinstance(section, dict):
            add_issue(errors, "invalid_section", f"Section at {path} must be an object")
            continue
        required_text(section, "title", path, errors)
        for exercise in required_list(section, "exercises", path, errors):
            if isinstance(exercise, dict):
                exercises.append(exercise)
            else:
                add_issue(errors, "invalid_exercise", f"Exercise in {path} must be an object")

    by_id: dict[str, dict[str, Any]] = {}
    observed_numbers: list[int] = []
    signatures: list[str] = []
    for index, exercise in enumerate(exercises):
        path = f"$.practice_book.exercise[{index}]"
        exercise_id = required_text(exercise, "exercise_id", path, errors)
        match = EXERCISE_ID_RE.fullmatch(exercise_id)
        if not match:
            add_issue(errors, "exercise_id", f"Invalid Practice Book exercise ID at {path}")
        else:
            observed_numbers.append(int(match.group(1)))
        if exercise_id in by_id:
            add_issue(errors, "duplicate_exercise_id", f"Duplicate exercise ID: {exercise_id}")
        elif exercise_id:
            by_id[exercise_id] = exercise

        title = required_text(exercise, "title", path, errors)
        required_text(exercise, "instruction_en", path, errors)
        required_text(exercise, "response_space", path, errors)
        family = exercise.get("task_family")
        if family not in TASK_FAMILIES:
            add_issue(errors, "task_family", f"Unsupported task_family at {path}: {family}")
        item_count = exercise.get("item_count")
        if not isinstance(item_count, int) or item_count < 1:
            add_issue(errors, "item_count", f"item_count must be a positive integer at {path}")
        answer_type = exercise.get("answer_type")
        if answer_type not in {"closed", "open", "mixed"}:
            add_issue(errors, "answer_type", f"Invalid answer_type at {path}")
        answer_ref = required_text(exercise, "answer_ref", path, errors)
        if answer_ref and (answer_ref not in answer_map or not str(answer_map[answer_ref]).strip()):
            add_issue(errors, "missing_answer", f"Missing teacher answer/judgment for {answer_ref}")
        if exercise.get("intended_use") not in {"classwork", "homework", "flexible"}:
            add_issue(errors, "intended_use", f"Invalid intended_use at {path}")
        required_list(exercise, "target_refs", path, errors)
        signature = required_text(exercise, "surface_signature", path, errors)
        if signature:
            signatures.append(signature.strip().lower())

        visible = student_text(exercise)
        visible_lower = visible.lower()
        for phrase in STUDENT_BANNED:
            if phrase in visible_lower:
                add_issue(
                    errors,
                    "student_metalanguage",
                    f"Student-facing banned phrase '{phrase}' at {path}",
                )
        for token in ALL_CAPS_RE.findall(visible):
            if token not in {"RE", "SYN"}:
                add_issue(errors, "all_caps_student_text", f"All-cap display token '{token}' at {path}")
        if title and title.upper() == title and re.search(r"[A-Z]", title):
            add_issue(errors, "all_caps_title", f"All-cap exercise title at {path}")
        if exercise.get("unfamiliar_format") is True and not str(exercise.get("example", "")).strip():
            add_issue(errors, "missing_example", f"Unfamiliar format lacks an example at {path}")

        word_count = exercise.get("word_bank_count")
        blank_count = exercise.get("blank_count")
        extras = exercise.get("stated_extra_words", 0)
        if word_count is not None or blank_count is not None:
            if not all(isinstance(value, int) and value >= 0 for value in (word_count, blank_count, extras)):
                add_issue(errors, "word_blank_count", f"Invalid word/blank counts at {path}")
            elif word_count != blank_count + extras:
                add_issue(
                    errors,
                    "word_blank_mismatch",
                    f"Word bank and blank counts do not match the stated rule at {path}",
                    words=word_count,
                    blanks=blank_count,
                    stated_extra_words=extras,
                )

    if observed_numbers and observed_numbers != list(range(1, len(observed_numbers) + 1)):
        add_issue(errors, "exercise_sequence", "Practice Book exercise IDs must be sequential from PB01")
    for signature, count in Counter(signatures).items():
        if count > 1:
            add_issue(errors, "duplicate_surface_task", f"Duplicate surface_signature: {signature}")
    if len(exercises) < 6:
        add_issue(warnings, "thin_practice_book", "Practice Book has fewer than six materialized exercises")
    return by_id


def validate_activity(activity: Any, path: str, errors: list[dict[str, Any]]) -> None:
    if not isinstance(activity, dict):
        add_issue(errors, "invalid_activity", f"Activity at {path} must be an object")
        return
    for key in (
        "title",
        "language_purpose",
        "grouping",
        "rules",
        "product",
        "individual_evidence",
        "teacher_adjudication",
        "fallback",
    ):
        required_text(activity, key, path, errors)
    minutes = activity.get("minutes")
    if not isinstance(minutes, (int, float)) or not 3 <= minutes <= 20:
        add_issue(errors, "activity_minutes", f"Activity minutes must be 3–20 at {path}")
    features = set(activity.get("quality_features", []))
    if len(features & ACTIVITY_QUALITY) < 2:
        add_issue(errors, "weak_activity", f"Activity needs at least two quality features at {path}")


def validate_lessons(
    spec: dict[str, Any],
    exercises: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    lessons = spec.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        add_issue(errors, "missing_lessons", "lessons must be a non-empty list")
        return {}

    by_id: dict[str, dict[str, Any]] = {}
    lesson_types: list[str] = []
    components: list[str] = []
    duration = spec.get("lesson_duration_minutes", 40)
    if not isinstance(duration, (int, float)) or duration <= 0:
        add_issue(errors, "lesson_duration", "lesson_duration_minutes must be positive")
        duration = 40

    for index, lesson in enumerate(lessons):
        path = f"$.lessons[{index}]"
        if not isinstance(lesson, dict):
            add_issue(errors, "invalid_lesson", f"Lesson at {path} must be an object")
            continue
        lesson_id = required_text(lesson, "lesson_id", path, errors)
        if lesson_id in by_id:
            add_issue(errors, "duplicate_lesson_id", f"Duplicate lesson_id: {lesson_id}")
        elif lesson_id:
            by_id[lesson_id] = lesson
        required_text(lesson, "title", path, errors)
        lesson_type = lesson.get("lesson_type")
        component = lesson.get("component")
        lesson_types.append(str(lesson_type))
        components.append(str(component))
        if lesson_type not in LESSON_TYPES:
            add_issue(errors, "lesson_type", f"Invalid lesson_type at {path}: {lesson_type}")
        if component not in COMPONENTS:
            add_issue(errors, "component", f"Invalid component at {path}: {component}")
        for key in (
            "purpose",
            "success_evidence",
            "materials",
            "preparation",
            "board_plan",
            "lesson_close",
        ):
            required_text(lesson, key, path, errors)
        required_list(lesson, "source_route", path, errors)
        required_list(lesson, "objectives", path, errors)
        required_list(lesson, "anticipated_errors", path, errors)
        differentiation = lesson.get("differentiation")
        if not isinstance(differentiation, dict):
            add_issue(errors, "differentiation", f"Missing differentiation object at {path}")
        else:
            required_text(differentiation, "access", f"{path}.differentiation", errors)
            required_text(differentiation, "extension", f"{path}.differentiation", errors)

        class_refs = lesson.get("classwork_exercise_refs", [])
        if not isinstance(class_refs, list):
            add_issue(errors, "classwork_refs", f"classwork_exercise_refs must be a list at {path}")
            class_refs = []
        for ref in class_refs:
            if ref not in exercises:
                add_issue(errors, "unknown_exercise_ref", f"Unknown classwork exercise {ref} at {path}")

        stages = required_list(lesson, "stages", path, errors)
        total_minutes = 0.0
        ready_to_say_count = 0
        stage_types: list[str] = []
        for s_index, stage in enumerate(stages):
            s_path = f"{path}.stages[{s_index}]"
            if not isinstance(stage, dict):
                add_issue(errors, "invalid_stage", f"Stage at {s_path} must be an object")
                continue
            for key in (
                "stage_id",
                "stage_type",
                "title",
                "grouping",
                "teacher_move_cn",
                "student_action",
                "product",
                "individual_evidence",
                "check",
                "anticipated_response",
                "likely_error",
                "recovery_move",
                "transition",
                "board_display",
            ):
                required_text(stage, key, s_path, errors)
            minutes = stage.get("minutes")
            if not isinstance(minutes, (int, float)) or minutes <= 0:
                add_issue(errors, "stage_minutes", f"Stage minutes must be positive at {s_path}")
            else:
                total_minutes += float(minutes)
            stage_types.append(str(stage.get("stage_type")))
            if str(stage.get("ready_to_say_en", "")).strip():
                ready_to_say_count += 1
            for ref in stage.get("practice_book_refs", []):
                if ref not in exercises:
                    add_issue(errors, "unknown_exercise_ref", f"Unknown stage exercise {ref} at {s_path}")
            if not isinstance(stage.get("source_refs", []), list):
                add_issue(errors, "source_refs", f"source_refs must be a list at {s_path}")
        if stages and isinstance(stages[0], dict) and stages[0].get("stage_type") != "lead_in":
            add_issue(errors, "missing_lead_in", f"First stage must be lead_in at {path}")
        if "lesson_close" not in stage_types:
            add_issue(errors, "missing_lesson_close", f"Lesson lacks a lesson_close stage at {path}")
        if not float(duration) - 2 <= total_minutes <= float(duration) + 2:
            add_issue(
                errors,
                "lesson_minutes",
                f"Lesson stages must total {float(duration)-2:g}–{float(duration)+2:g} minutes at {path}",
                observed=total_minutes,
            )
        if ready_to_say_count == 0:
            add_issue(errors, "ready_to_say", f"Lesson has no ready-to-say English at {path}")

        activities = lesson.get("activities", [])
        if not isinstance(activities, list):
            add_issue(errors, "activities", f"activities must be a list at {path}")
        else:
            for a_index, activity in enumerate(activities):
                validate_activity(activity, f"{path}.activities[{a_index}]", errors)

        homework = lesson.get("homework")
        if not isinstance(homework, dict):
            add_issue(errors, "missing_homework", f"Every lesson needs a homework route at {path}")
        else:
            required_text(homework, "title", f"{path}.homework", errors)
            required_text(homework, "teacher_verification", f"{path}.homework", errors)
            required_text(homework, "next_lesson_use", f"{path}.homework", errors)
            required_list(homework, "taught_content_refs", f"{path}.homework", errors)
            hw_refs = required_list(homework, "exercise_refs", f"{path}.homework", errors)
            minutes = homework.get("minutes")
            if not isinstance(minutes, (int, float)) or not 15 <= minutes <= 30:
                add_issue(errors, "homework_minutes", f"Homework must be 15–30 minutes at {path}")
            for ref in hw_refs:
                if ref not in exercises:
                    add_issue(errors, "unknown_exercise_ref", f"Unknown homework exercise {ref} at {path}")
            overlap = sorted(set(class_refs) & set(hw_refs))
            if overlap:
                add_issue(
                    errors,
                    "classwork_homework_overlap",
                    f"The same exercise cannot be classwork and homework at {path}",
                    exercise_refs=overlap,
                )
            if homework.get("oral") is True:
                verification = str(homework.get("teacher_verification", "")).lower()
                if not any(token in verification for token in ("teacher", "老师", "recite", "report", "random", "record")):
                    add_issue(errors, "oral_verification", f"Oral homework is not teacher-verifiable at {path}")

    scope = spec.get("scope")
    if scope == "pilot":
        required_pilot = {"meaning_first", "close_study"}
        if not required_pilot.issubset(set(lesson_types)):
            add_issue(errors, "pilot_coverage", "Pilot must include meaning_first and close_study lessons")
        if not ({"language_consolidation", "retrieval_feedback", "integrated_output"} & set(lesson_types)):
            add_issue(errors, "pilot_coverage", "Pilot needs a consolidation, review, or output lesson")
        if len(lessons) < 3:
            add_issue(errors, "pilot_count", "Pilot must contain at least three representative lessons")
    elif scope == "full":
        counts = Counter(components)
        override = str(spec.get("route_override_reason", "")).strip()
        expected_ranges = {
            "reading_a": (7, 8),
            "reading_b": (3, 4),
            "video_listening": (1, 2),
            "integrated_output": (1, 2),
            "review_feedback": (1, 2),
        }
        violations = {
            component: count
            for component, count in counts.items()
            if component in expected_ranges
            and not expected_ranges[component][0] <= count <= expected_ranges[component][1]
        }
        missing = [component for component in expected_ranges if counts[component] == 0]
        if (violations or missing) and not override:
            add_issue(
                errors,
                "full_unit_route",
                "Full Unit lesson allocation is outside the approved ranges without a route_override_reason",
                counts=dict(counts),
                missing=missing,
            )
        reading_a_types = [
            lesson.get("lesson_type") for lesson in lessons if isinstance(lesson, dict) and lesson.get("component") == "reading_a"
        ]
        if len(reading_a_types) >= 2 and reading_a_types[:2] != ["meaning_first", "meaning_first"]:
            add_issue(errors, "meaning_first_route", "The first two Reading A lessons must be meaning_first")
    else:
        add_issue(errors, "scope", "scope must be pilot or full")
    return by_id


def validate_language_coverage(
    coverage: Any,
    lessons: dict[str, dict[str, Any]],
    exercises: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    if not isinstance(coverage, list) or not coverage:
        add_issue(errors, "language_coverage", "language_coverage must be a non-empty list")
        return
    lesson_order = {lesson_id: index for index, lesson_id in enumerate(lessons)}
    sentence_ids: set[str] = set()
    for index, row in enumerate(coverage):
        path = f"$.language_coverage[{index}]"
        if not isinstance(row, dict):
            add_issue(errors, "invalid_coverage_row", f"Coverage row at {path} must be an object")
            continue
        sentence_id = required_text(row, "sentence_id", path, errors)
        if sentence_id in sentence_ids:
            add_issue(errors, "duplicate_sentence_coverage", f"Duplicate coverage for {sentence_id}")
        sentence_ids.add(sentence_id)
        required_text(row, "meaning", path, errors)
        first_lesson = required_text(row, "first_encounter_lesson", path, errors)
        if first_lesson not in lessons:
            add_issue(errors, "unknown_lesson_ref", f"Unknown first encounter lesson at {path}: {first_lesson}")
        required_text(row, "grammar_pattern", path, errors)
        required_text(row, "teacher_notes", path, errors)
        practice_refs = required_list(row, "practice_refs", path, errors)
        retrieval_refs = required_list(row, "retrieval_refs", path, errors)
        for ref in practice_refs + retrieval_refs:
            if ref not in exercises:
                add_issue(errors, "unknown_exercise_ref", f"Unknown coverage exercise {ref} at {path}")
        chunks = row.get("chunks", [])
        if not isinstance(chunks, list):
            add_issue(errors, "chunks", f"chunks must be a list at {path}")
        vocabulary = row.get("vocabulary", [])
        if not isinstance(vocabulary, list):
            add_issue(errors, "vocabulary", f"vocabulary must be a list at {path}")
            vocabulary = []
        for v_index, item in enumerate(vocabulary):
            v_path = f"{path}.vocabulary[{v_index}]"
            if not isinstance(item, dict):
                add_issue(errors, "vocabulary_item", f"Vocabulary at {v_path} must be an object")
                continue
            required_text(item, "item", v_path, errors)
            tier = required_text(item, "tier", v_path, errors)
            if tier not in {"active", "text_essential", "recycled", "recognition"}:
                add_issue(errors, "vocabulary_tier", f"Invalid vocabulary tier at {v_path}")
            if tier != "recognition":
                for key in (
                    "english_definition",
                    "source_context",
                    "chunk_collocation",
                    "new_context_use",
                    "retrieval_lesson",
                ):
                    required_text(item, key, v_path, errors)
                retrieval_lesson = str(item.get("retrieval_lesson", ""))
                if retrieval_lesson and retrieval_lesson not in lessons:
                    add_issue(errors, "unknown_lesson_ref", f"Unknown retrieval lesson at {v_path}")
                elif (
                    first_lesson in lesson_order
                    and retrieval_lesson in lesson_order
                    and lesson_order[retrieval_lesson] <= lesson_order[first_lesson]
                ):
                    add_issue(errors, "retrieval_order", f"Vocabulary retrieval must follow first encounter at {v_path}")


def validate(spec: dict[str, Any], allow_needs_review: bool = False) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if spec.get("schema_version") != "re.coursepack-spec.v2":
        add_issue(errors, "schema_version", "schema_version must be re.coursepack-spec.v2")
    required_text(spec, "unit_id", "$", errors)
    required_text(spec, "title", "$", errors)
    if not allow_needs_review:
        for path in find_placeholders(spec):
            add_issue(errors, "unresolved_placeholder", f"Unresolved placeholder at {path}")

    artifacts = spec.get("artifact_contract")
    if not isinstance(artifacts, dict):
        add_issue(errors, "artifact_contract", "artifact_contract must be an object")
    else:
        for key, expected in REQUIRED_ARTIFACTS.items():
            if artifacts.get(key) is not expected:
                add_issue(errors, "artifact_contract", f"artifact_contract.{key} must be {expected}")

    learner = spec.get("learner")
    if not isinstance(learner, dict):
        add_issue(errors, "learner", "learner must be an object")
    else:
        if learner.get("school_grade") != 6:
            add_issue(warnings, "learner_grade", "This skill authority is calibrated for Grade 6")
        for key in ("book_level", "proficiency_range"):
            required_text(learner, key, "$.learner", errors)
        if learner.get("students_own_textbook") is not False:
            add_issue(warnings, "textbook_ownership", "Approved print route assumes students do not own the textbook")

    exercises = validate_exercises(
        spec.get("practice_book"), spec.get("teacher_answers"), errors, warnings
    )
    lessons = validate_lessons(spec, exercises, errors, warnings)
    validate_language_coverage(spec.get("language_coverage"), lessons, exercises, errors)

    return {
        "schema_version": "re.coursepack-validation.v2",
        "unit_id": spec.get("unit_id"),
        "scope": spec.get("scope"),
        "status": "pass" if not errors else "fail",
        "summary": {
            "lessons": len(lessons),
            "practice_book_exercises": len(exercises),
            "language_coverage_rows": len(spec.get("language_coverage", []))
            if isinstance(spec.get("language_coverage"), list)
            else 0,
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--allow-needs-review", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate(load_json(args.spec), args.allow_needs_review)
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
