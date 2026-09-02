#!/usr/bin/env python3
"""Validate a live curated layout-exemplar index and its referenced files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ARTIFACT_TYPES = ("student_practice_book", "answer_key", "teaching_outline")
STATUSES = {"primary", "secondary", "deprecated"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(data: dict, index_path: Path, check_files: bool) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "re.approved-layout-exemplars.v1":
        errors.append("schema_version must be re.approved-layout-exemplars.v1")

    policy = data.get("selection_policy", {})
    default_count = policy.get("default_exemplars_per_artifact")
    maximum_count = policy.get("maximum_exemplars_per_artifact")
    if default_count != 1:
        errors.append("selection_policy.default_exemplars_per_artifact must be 1")
    if not isinstance(maximum_count, int) or not 1 <= maximum_count <= 2:
        errors.append("selection_policy.maximum_exemplars_per_artifact must be 1 or 2")
    if policy.get("scan_output_tree") is not False:
        errors.append("selection_policy.scan_output_tree must be false")
    if policy.get("automatic_registration") is not False:
        errors.append("selection_policy.automatic_registration must be false")

    exemplar_groups = data.get("exemplars")
    if not isinstance(exemplar_groups, dict):
        errors.append("exemplars must be an object")
        return errors

    seen_ids: set[str] = set()
    for artifact_type in ARTIFACT_TYPES:
        records = exemplar_groups.get(artifact_type)
        if not isinstance(records, list):
            errors.append(f"exemplars.{artifact_type} must be a list")
            continue
        active_count = sum(record.get("status") != "deprecated" for record in records if isinstance(record, dict))
        if isinstance(maximum_count, int) and active_count > maximum_count:
            errors.append(f"exemplars.{artifact_type} has more than {maximum_count} active exemplars")
        primary_count = sum(record.get("status") == "primary" for record in records if isinstance(record, dict))
        if records and primary_count != 1:
            errors.append(f"exemplars.{artifact_type} must contain exactly one primary exemplar")

        for position, record in enumerate(records):
            prefix = f"exemplars.{artifact_type}[{position}]"
            if not isinstance(record, dict):
                errors.append(f"{prefix} must be an object")
                continue
            exemplar_id = str(record.get("id", "")).strip()
            if not exemplar_id:
                errors.append(f"{prefix}.id is required")
            elif exemplar_id in seen_ids:
                errors.append(f"{prefix}.id is duplicated: {exemplar_id}")
            else:
                seen_ids.add(exemplar_id)
            if record.get("status") not in STATUSES:
                errors.append(f"{prefix}.status must be one of {sorted(STATUSES)}")
            if not isinstance(record.get("priority"), int) or record.get("priority", 0) < 1:
                errors.append(f"{prefix}.priority must be a positive integer")
            scope = record.get("scope")
            if not isinstance(scope, list) or not any(str(item).strip() for item in scope):
                errors.append(f"{prefix}.scope must be a non-empty list")

            raw_path = str(record.get("path", "")).strip()
            relative_path = Path(raw_path)
            if not raw_path or relative_path.is_absolute() or ".." in relative_path.parts:
                errors.append(f"{prefix}.path must be a safe workspace-relative path")
                continue
            expected_hash = str(record.get("sha256", "")).strip()
            if not SHA256_PATTERN.fullmatch(expected_hash):
                errors.append(f"{prefix}.sha256 must be a lowercase SHA-256 value")
                continue
            if check_files:
                artifact_path = index_path.parent / relative_path
                if not artifact_path.is_file():
                    errors.append(f"{prefix}.path does not exist: {relative_path}")
                elif sha256(artifact_path) != expected_hash:
                    errors.append(f"{prefix}.sha256 does not match: {relative_path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    index_path = args.index.expanduser().resolve()
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate(data, index_path, args.check_files)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    suffix = " and referenced files" if args.check_files else ""
    print(f"PASS: {index_path}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
