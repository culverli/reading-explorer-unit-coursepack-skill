#!/usr/bin/env python3
"""Validate the portable Skill and its public/private repository boundary."""

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
except ImportError:  # pragma: no cover
    yaml = None


SKILL_DIR_NAME = "reading-explorer-unit-coursepack-skill"
ALLOWED_ROOT_FILES = {".gitignore", "LICENSE", "README.md"}
FORBIDDEN_SUFFIXES = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".mp3", ".m4a", ".wav", ".mp4", ".mov",
    ".png", ".jpg", ".jpeg",
}
FORBIDDEN_DIRS = {"sources", "source-materials", "artifacts", "qa", "projects", "__pycache__"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".txt"}
PRIVATE_PATH_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[^\\]+\\"),
)
OBSOLETE_CONTRACT_PATTERNS = (
    "teacher_unit_" + "guide\": true",
    "re.coursepack-" + "spec.v2",
    "re.coursepack-" + "project.v2",
    "init_coursepack_" + "project.py",
    "validate_coursepack_" + "spec.py",
    "approved-practice-book-" + "standard.md",
    "teacher-guide-" + "standard.md",
)
REQUIRED_SKILL_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/intake-and-reading-modes.md",
    "references/practice-book-standard.md",
    "references/teacher-edited-layout-delta.md",
    "references/answer-key-standard.md",
    "references/teaching-outline-standard.md",
    "references/source-and-qa.md",
    "references/provenance.md",
    "assets/templates/article-project-brief.template.json",
    "assets/templates/source-inventory.template.json",
    "assets/templates/exercise-source-map.template.json",
    "assets/templates/docx-style-tokens.json",
    "assets/samples/article-project-brief.synthetic.json",
    "scripts/init_article_project.py",
    "scripts/validate_article_brief.py",
    "scripts/validate_skill_repo.py",
)


def publication_candidates(root: Path) -> list[Path]:
    """Return files Git would publish, excluding deleted paths still in the index."""
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        candidates = [root / raw.decode("utf-8") for raw in completed.stdout.split(b"\0") if raw]
        return sorted(path for path in candidates if path.is_file())
    except (OSError, subprocess.CalledProcessError):
        skill = root / SKILL_DIR_NAME
        result = [path for path in skill.rglob("*") if path.is_file()]
        result.extend(path for path in (root / name for name in ALLOWED_ROOT_FILES) if path.is_file())
        return sorted(result)


def validate_yaml(path: Path, errors: list[str], relative: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            errors.append(f"Invalid YAML in {relative}: {exc}")
            return
        interface = data.get("interface", {}) if isinstance(data, dict) else {}
        for key in ("display_name", "short_description", "default_prompt"):
            if not isinstance(interface.get(key), str) or not interface[key].strip():
                errors.append(f"Missing YAML interface key '{key}' in {relative}")
        prompt = interface.get("default_prompt", "")
    else:
        if "\t" in text or not re.search(r"(?m)^interface:\s*$", text):
            errors.append(f"YAML structure check failed in {relative}")
        for key in ("display_name", "short_description", "default_prompt"):
            if not re.search(rf"(?m)^  {key}:\s*\".+\"\s*$", text):
                errors.append(f"Missing or unquoted YAML interface key '{key}' in {relative}")
        match = re.search(r'(?m)^  default_prompt:\s*"(.+)"\s*$', text)
        prompt = match.group(1) if match else ""
    if "$reading-explorer-unit-coursepack-skill" not in prompt:
        errors.append("agents/openai.yaml default_prompt must mention the Skill explicitly")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    skill = root / SKILL_DIR_NAME
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
        if len(parts) == 1 and relative.as_posix() not in ALLOWED_ROOT_FILES:
            errors.append(f"Unexpected root publication file: {relative}")
        if len(parts) > 1 and parts[0] != SKILL_DIR_NAME:
            errors.append(f"Unexpected publication path outside Skill: {relative}")
        if any(part in FORBIDDEN_DIRS for part in parts):
            errors.append(f"Forbidden runtime/source directory in publication boundary: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden binary/source artifact: {relative}")
        if "assets/samples" in relative.as_posix() and path.suffix == ".json" and "synthetic" not in path.name:
            errors.append(f"Sample JSON must be explicitly synthetic: {relative}")

        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"Text file is not valid UTF-8: {relative}")
                continue
            if any(pattern.search(text) for pattern in PRIVATE_PATH_PATTERNS):
                errors.append(f"Local/private absolute path found in: {relative}")
            for pattern in OBSOLETE_CONTRACT_PATTERNS:
                if pattern in text:
                    errors.append(f"Obsolete contract reference '{pattern}' found in: {relative}")

        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"Invalid JSON in {relative}: {exc}")
        elif path.suffix in {".yaml", ".yml"}:
            validate_yaml(path, errors, relative)
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
    print(f"PASS: Skill repository gate passed ({len(candidates)} publication candidates).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
