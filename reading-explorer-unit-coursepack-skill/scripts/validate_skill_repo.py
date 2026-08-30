#!/usr/bin/env python3
"""Validate the public boundary and internal consistency of this skill repository."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - quick_validate also checks this file
    yaml = None


SKILL_DIR = "reading-explorer-unit-coursepack-skill"
ALLOWED_ROOT_FILES = {".gitignore", "LICENSE", "README.md"}
FORBIDDEN_SUFFIXES = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".mp3",
    ".m4a",
    ".wav",
    ".mp4",
    ".mov",
    ".png",
    ".jpg",
    ".jpeg",
}
FORBIDDEN_DIRS = {"sources", "source-materials", "artifacts", "qa", "projects", "__pycache__"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".csv", ".js"}
PRIVATE_PATH_MARKERS = ("/" + "Users/", "/" + "home/", "C:\\" + "Users\\")
STALE_PATTERNS = (
    "validate_" + "unit_spec.py",
    "references/" + "artifact-design.md",
    "references/" + "homework-system.md",
    "references/" + "unit-contract.md",
    "references/" + "unit-design.md",
    "Produce exactly " + "twelve",
    "HW01" + "–HW12",
    "Generate all " + "three",
)
REQUIRED_SKILL_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/approved-practice-book-standard.md",
    "references/teacher-guide-standard.md",
    "references/practice-book-standard.md",
    "references/instructional-system.md",
    "references/qa-and-approval.md",
    "references/source-fidelity.md",
    "references/provenance.md",
    "assets/templates/coursepack-spec.template.json",
    "assets/templates/project-contract.template.json",
    "assets/templates/source-ledger.template.json",
    "assets/templates/source-usage.template.json",
    "assets/templates/pilot-approval.template.json",
    "assets/templates/docx-style-tokens.json",
    "assets/samples/coursepack-spec.synthetic.json",
    "assets/samples/source-ledger.synthetic.json",
    "assets/samples/source-usage.synthetic.json",
    "scripts/validate_coursepack_spec.py",
    "scripts/audit_coursepack_docx.py",
    "scripts/build_synthetic_reference.py",
    "scripts/init_coursepack_project.py",
    "scripts/verify_source_fidelity.py",
    "scripts/analyze_text_difficulty.py",
)


def publication_candidates(root: Path) -> list[Path]:
    """Return exactly what Git would publish, including untracked non-ignored files."""
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        result = [path for path in (root / SKILL_DIR).rglob("*") if path.is_file()]
        result.extend(path for path in (root / "LICENSE", root / ".gitignore") if path.is_file())
        return sorted(result)
    return sorted(root / raw.decode("utf-8") for raw in completed.stdout.split(b"\0") if raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    skill = root / SKILL_DIR
    errors: list[str] = []

    for required in (root / "LICENSE", *(skill / relative for relative in REQUIRED_SKILL_FILES)):
        if not required.is_file():
            errors.append(f"Missing required file: {required.relative_to(root)}")

    candidates = publication_candidates(root)
    for path in candidates:
        try:
            relative = path.relative_to(root)
        except ValueError:
            errors.append(f"Publication candidate is outside repository: {path}")
            continue
        parts = relative.parts
        if not parts:
            continue
        if len(parts) == 1 and relative.as_posix() not in ALLOWED_ROOT_FILES:
            errors.append(f"Unexpected root publication file: {relative}")
        if len(parts) > 1 and parts[0] != SKILL_DIR:
            errors.append(f"Unexpected publication path outside skill: {relative}")
        if any(part in FORBIDDEN_DIRS for part in parts):
            errors.append(f"Forbidden runtime/source directory in publication boundary: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden binary/source artifact: {relative}")
        if path.name in {"source-ledger.json", "source-usage.json", "source-report.json"}:
            errors.append(f"Forbidden runtime record: {relative}")
        if "assets/samples" in relative.as_posix() and path.suffix == ".json" and "synthetic" not in path.name:
            errors.append(f"Sample JSON must be explicitly synthetic: {relative}")

        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"Text file is not valid UTF-8: {relative}")
                continue
            if any(marker in text for marker in PRIVATE_PATH_MARKERS):
                errors.append(f"Local/private absolute path found in: {relative}")
            for pattern in STALE_PATTERNS:
                if pattern in text:
                    errors.append(f"Obsolete contract reference '{pattern}' found in: {relative}")

        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"Invalid JSON in {relative}: {exc}")
        elif path.suffix in {".yaml", ".yml"}:
            if yaml is None:
                text = path.read_text(encoding="utf-8")
                if "\t" in text or not re.search(r"(?m)^interface:\s*$", text):
                    errors.append(f"YAML structure check failed in {relative}")
                for key in ("display_name", "short_description", "default_prompt"):
                    if not re.search(rf"(?m)^  {key}:\s*.+$", text):
                        errors.append(f"Missing YAML interface key '{key}' in {relative}")
            else:
                try:
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                except (UnicodeDecodeError, yaml.YAMLError) as exc:
                    errors.append(f"Invalid YAML in {relative}: {exc}")
        elif path.suffix == ".py":
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failure in {relative}: {exc.msg}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(f"Skill repository gate passed ({len(candidates)} publication candidates).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
