#!/usr/bin/env python3
"""Link or copy the bundled skills into a host's chosen skill directory, without overwriting."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "finance-setup", "finance-gather", "investment-research",
    "portfolio-review", "finance-plan", "finance-memory", "finance-dashboard",
)


def install(target: Path, mode: str = "link", source: Path | None = None) -> list[str]:
    if mode not in {"link", "copy"}:
        raise ValueError("mode must be link or copy")
    source = (source or ROOT / "skills").resolve()
    target = target.expanduser().resolve()
    if target == source or source in target.parents:
        raise ValueError("The installation target must be outside the source skills directory")
    planned = []
    for name in NAMES:
        src, dst = source / name, target / name
        if not (src / "SKILL.md").is_file():
            raise ValueError(f"Missing skill: {name}")
        if any(p.is_symlink() for p in src.rglob("*")):
            raise ValueError(f"Refusing skill source containing symlinks: {name}")
        if os.path.lexists(dst):
            if mode == "link" and dst.is_symlink() and dst.resolve() == src.resolve():
                continue
            raise ValueError(f"Target already exists; no files were overwritten: {dst}")
        planned.append((src, dst))
    target.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    try:
        for src, dst in planned:
            if mode == "link":
                dst.symlink_to(src, target_is_directory=True)
            else:
                shutil.copytree(src, dst)
            created.append(dst)
    except OSError:
        for dst in reversed(created):
            if dst.is_symlink():
                dst.unlink()
            else:
                shutil.rmtree(dst)
        raise
    return [str(p) for p in created]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True, help="Host skill directory, e.g. /my/project/.agents/skills")
    parser.add_argument("--mode", choices=("link", "copy"), default="link")
    args = parser.parse_args()
    try:
        changed = install(args.target, args.mode)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"Installed {len(changed)} skills; matching existing links were kept.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
