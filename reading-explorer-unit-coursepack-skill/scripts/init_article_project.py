#!/usr/bin/env python3
"""Initialize a private article-coursepack workspace from the portable template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


SKILL_DIR = Path(__file__).resolve().parents[1]
BRIEF_TEMPLATE = SKILL_DIR / "assets" / "templates" / "article-project-brief.template.json"
INVENTORY_TEMPLATE = SKILL_DIR / "assets" / "templates" / "source-inventory.template.json"
MAP_TEMPLATE = SKILL_DIR / "assets" / "templates" / "exercise-source-map.template.json"


def copy_template(source: Path, target: Path) -> None:
    if target.exists():
        return
    shutil.copyfile(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, help="Private project directory to create")
    parser.add_argument("--project-id", help="Initial project_id written into JSON templates")
    args = parser.parse_args()

    root = args.project_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for name in ("sources", "work", "artifacts", "qa", "qa/renders"):
        (root / name).mkdir(parents=True, exist_ok=True)

    targets = {
        BRIEF_TEMPLATE: root / "article-project-brief.json",
        INVENTORY_TEMPLATE: root / "source-inventory.json",
        MAP_TEMPLATE: root / "exercise-source-map.json",
    }
    for source, target in targets.items():
        copy_template(source, target)

    if args.project_id:
        for target in targets.values():
            data = json.loads(target.read_text(encoding="utf-8"))
            if data.get("project_id") == "needs_review":
                data["project_id"] = args.project_id
                target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
