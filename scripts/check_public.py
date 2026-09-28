#!/usr/bin/env python3
"""Check Git's staged tree for accidental private files and common credentials.

This is a release aid, not a guarantee that a repository contains no personal data.
It prints file names and rule names, never matched values. Review the diff as well.
"""
from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {"AGENTS.md", ".gitignore", "README.md", "LICENSE", "NOTICE.md", "pyproject.toml", "integrations.json"}
DIRECTORIES = {".codex-plugin", ".github", "skills", "src", "schemas", "examples", "tests", "docs", "scripts"}
PATTERNS = {
    "absolute personal home path": re.compile(r"(?:/Users/|/home/)[A-Za-z0-9_.-]+/"),
    "private key material": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub credential": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    "provider credential": re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}\b"),
    "cloud credential": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "private cloud document link": re.compile(r"https://(?:docs\.google\.com/(?:spreadsheets|document|presentation)/d/|drive\.google\.com/file/d/)[A-Za-z0-9_-]{15,}"),
    "wallet address": re.compile(r"\b0x[a-fA-F0-9]{40}\b"),
}


def inspect(path: str, mode: str, data: bytes, denylist: tuple[str, ...] = ()) -> list[str]:
    failures = []
    p = PurePosixPath(path)
    if path not in ROOT_FILES and (len(p.parts) < 2 or p.parts[0] not in DIRECTORIES):
        failures.append("outside public source allowlist")
    if mode not in {"100644", "100755"}:
        failures.append("symlink, submodule, or unsupported Git mode")
    if any(x in p.parts for x in {".env", "private", "exports", "reports", "taxes", "oauth", "__pycache__"}) or p.name.startswith(".env") or p.name.endswith((".env", ".pdf", ".png", ".jpg", ".jpeg", ".zip", ".duckdb", ".sqlite", ".db", ".pem", ".key", ".token")):
        failures.append("private or binary artifact path")
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError:
        return failures + ["non-text artifact"]
    if "\x00" in content:
        failures.append("binary content")
    for name, pattern in PATTERNS.items():
        if pattern.search(content):
            failures.append(name)
    if any(value and value in content for value in denylist):
        failures.append("private denylist match")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--denylist", type=Path, help="Optional private newline-separated literal values; never store this file in the repository")
    args = parser.parse_args()
    denylist = tuple(args.denylist.read_text().splitlines()) if args.denylist else ()
    try:
        top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True).strip()
        if Path(top).resolve() != ROOT:
            raise ValueError("This folder must be its own Git repository")
        index = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=ROOT)
    except (subprocess.CalledProcessError, ValueError) as exc:
        parser.exit(1, f"Cannot inspect public tree: {exc}\n")
    entries = [item for item in index.decode().split("\0") if item]
    if not entries:
        parser.exit(1, "No staged files; stage only the public project first.\n")
    failures = []
    for item in entries:
        meta, path = item.split("\t", 1)
        mode, object_id, stage = meta.split()
        if stage != "0":
            failures.append((path, ["unresolved index conflict"]))
            continue
        blob = subprocess.check_output(["git", "cat-file", "blob", object_id], cwd=ROOT)
        reasons = inspect(path, mode, blob, denylist)
        if reasons:
            failures.append((path, reasons))
    for path, reasons in failures:
        print(f"FAIL {path}: {', '.join(reasons)}")
    print(f"Checked {len(entries)} indexed public files; {len(failures)} flagged.")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
