#!/usr/bin/env python3
"""Initialize a private Reading Explorer coursepack project from safe templates."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets" / "templates"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_template(name: str) -> dict:
    return json.loads((TEMPLATES / name).read_text(encoding="utf-8"))


def create_project(target: Path, project_id: str, title: str, force: bool) -> list[Path]:
    target = target.resolve()
    if target.exists() and any(target.iterdir()) and not force:
        raise ValueError(f"Target is not empty: {target}. Use --force only for an intentional merge.")
    target.mkdir(parents=True, exist_ok=True)
    for directory in ("artifacts", "qa", "qa/renders", "qa/reviews", "sources-private"):
        (target / directory).mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    project = load_template("project-contract.template.json")
    project["project_id"] = project_id
    project["title"] = title
    project_path = target / "coursepack.json"
    write_json(project_path, project)
    created.append(project_path)

    spec = load_template("coursepack-spec.template.json")
    spec["unit_id"] = project_id.upper().replace("_", "-")
    spec["title"] = title
    spec_path = target / "coursepack-spec.json"
    write_json(spec_path, spec)
    created.append(spec_path)

    for template_name, output_name in (
        ("source-ledger.template.json", "source-ledger.json"),
        ("source-usage.template.json", "source-usage.json"),
        ("pilot-approval.template.json", "qa/pilot-approval.json"),
        ("docx-style-tokens.json", "docx-style-tokens.json"),
    ):
        destination = target / output_name
        shutil.copy2(TEMPLATES / template_name, destination)
        created.append(destination)

    source_index = {
        "schema_version": "re.source-index.v1",
        "project_id": project_id,
        "sources": [],
        "publishing_boundary": "Private source paths and commercial files stay outside the skill repository.",
    }
    source_index_path = target / "source-index.json"
    write_json(source_index_path, source_index)
    created.append(source_index_path)

    manifest = {
        "schema_version": "re.artifact-manifest.v1",
        "project_id": project_id,
        "status": "needs_review",
        "teacher_unit_guide": None,
        "student_practice_book": None,
        "qa": {},
    }
    manifest_path = target / "artifact-manifest.json"
    write_json(manifest_path, manifest)
    created.append(manifest_path)

    private_note = target / "sources-private" / ".gitignore"
    private_note.write_text("*\n!.gitignore\n", encoding="utf-8")
    created.append(private_note)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        created = create_project(args.project_dir, args.project_id, args.title, args.force)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for path in created:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
