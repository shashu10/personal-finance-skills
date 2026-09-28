#!/usr/bin/env python3
"""Install one pinned optional tool into its own external, managed virtualenv."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = ".personal-finance-skills-managed.json"


def manifest() -> dict:
    return json.loads((ROOT / "integrations.json").read_text(encoding="utf-8"))


def external_path(value: str | Path, label: str = "path") -> Path:
    path = Path(value).expanduser().resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError(f"{label} must be outside the public checkout")
    return path


def environment_python(path: Path) -> Path:
    return path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def validate_target(value: str | Path, tool: str) -> tuple[Path, bool]:
    path = external_path(value, "Virtual environment")
    if not path.exists():
        return path, False
    try:
        receipt = json.loads((path / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ValueError("Existing target is not a managed environment; choose a new external directory") from None
    if receipt.get("managed_by") != "personal-finance-skills" or receipt.get("tool") != tool:
        raise ValueError("Each optional tool requires its own managed environment")
    if not (path / "pyvenv.cfg").is_file() or not environment_python(path).is_file():
        raise ValueError("Managed environment is incomplete; choose a new external directory")
    return path, True


def build_plan(tool: str, target: str | Path) -> dict:
    if sys.version_info < (3, 12):
        raise ValueError("Run this installer with Python 3.12 or newer")
    path, exists = validate_target(target, tool)
    spec = manifest()["tools"][tool]
    if not re.fullmatch(r"[0-9a-f]{40}", spec["revision"]):
        raise ValueError("Integration revision must be a full Git commit SHA")
    python = str(environment_python(path))
    requirement = f"{spec['distribution']} @ git+{spec['repository']}.git@{spec['revision']}"
    commands = [] if exists else [[sys.executable, "-m", "venv", str(path)]]
    commands.extend([
        [python, "-m", "pip", "install", "--disable-pip-version-check", requirement],
        [python, "-m", "pip", "check"],
    ])
    return {"tool": tool, "environment": str(path), "existing": exists,
            "revision": spec["revision"], "license": spec["license"], "commands": commands}


def verification_command(python: Path, distribution: str) -> list[str]:
    # Package metadata inspection imports no upstream runtime and makes no API calls.
    program = (
        "import importlib.metadata as m,json; "
        f"d=m.distribution({distribution!r}); "
        "u=json.loads(d.read_text('direct_url.json') or '{}'); "
        "print(json.dumps({'version':d.version,'revision':u.get('vcs_info',{}).get('commit_id')}))"
    )
    return [str(python), "-c", program]


def install(plan: dict) -> None:
    path = Path(plan["environment"])
    receipt = {"managed_by": "personal-finance-skills", "tool": plan["tool"],
               "revision": plan["revision"], "status": "installing"}
    commands = list(plan["commands"])
    if not plan["existing"]:
        subprocess.run(commands.pop(0), check=True)
    (path / MARKER).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for command in commands:
        subprocess.run(command, check=True, cwd=path)
    spec = manifest()["tools"][plan["tool"]]
    result = subprocess.run(verification_command(environment_python(path), spec["distribution"]),
                            check=True, capture_output=True, text=True, cwd=path)
    installed = json.loads(result.stdout)
    if installed.get("revision") != plan["revision"]:
        raise ValueError("Installed source revision differs from the manifest; environment is not ready")
    receipt.update(status="ready", version=installed["version"])
    (path / MARKER).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", choices=("tradingagents", "vibe-trading"), required=True)
    parser.add_argument("--venv", required=True, help="New external directory, distinct for each tool")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without writes, installs, or network")
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.tool, args.venv)
        print(f"Optional tool: {args.tool}; license: {plan['license']}; pinned commit: {plan['revision']}")
        print("Installation downloads source/dependencies. Later model/data calls may incur provider charges.")
        print("No broker login or model call is performed by this installer. Keep credentials outside this checkout.")
        print("Source is pinned; transitive dependencies are resolved by pip and are not fully locked.")
        for command in plan["commands"]:
            print(shlex.join(command))
        if not args.dry_run:
            install(plan)
            print(f"Ready: {environment_python(Path(plan['environment']))}")
        return 0
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Installation stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
