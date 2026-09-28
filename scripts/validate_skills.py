#!/usr/bin/env python3
"""Validate bundled skill metadata and local references. Install the dev extra first."""
from pathlib import Path
import re
import sys

import yaml

from install_skills import NAMES

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors = []
    found = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    if found != set(NAMES):
        errors.append(f"Expected exactly the {len(NAMES)} documented skills")
    for name in NAMES:
        folder = ROOT / "skills" / name
        skill = folder / "SKILL.md"
        if not skill.exists():
            errors.append(f"{name}: missing SKILL.md")
            continue
        text = skill.read_text()
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not match:
            errors.append(f"{name}: missing YAML frontmatter")
            continue
        try:
            meta = yaml.safe_load(match[1])
            if meta.get("name") != name or not isinstance(meta.get("description"), str) or not meta["description"].strip():
                errors.append(f"{name}: invalid name or description")
            ui = yaml.safe_load((folder / "agents/openai.yaml").read_text())
            if f"${name}" not in ui["interface"]["default_prompt"]:
                errors.append(f"{name}: UI prompt must invoke its skill")
            if not 25 <= len(ui["interface"]["short_description"]) <= 64:
                errors.append(f"{name}: UI description must be 25-64 characters")
        except (OSError, KeyError, TypeError, AttributeError, yaml.YAMLError):
            errors.append(f"{name}: invalid metadata")
        for document in folder.rglob("*.md"):
            body = document.read_text()
            if "[TODO:" in body:
                errors.append(f"{document.relative_to(ROOT)}: unfinished scaffold")
            for target in re.findall(r"\]\(([^)]+)\)", body):
                if "://" in target or target.startswith("#"):
                    continue
                path = (document.parent / target.split("#", 1)[0]).resolve()
                if not path.is_relative_to(folder.resolve()) or not path.exists():
                    errors.append(f"{document.relative_to(ROOT)}: missing or nonportable local reference")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Validated {len(found)} skills; {len(errors)} errors.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
