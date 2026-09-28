#!/usr/bin/env python3
"""Send explicitly permitted ledger context to a pinned TradingAgents installation."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from install_optional import MARKER, external_path, manifest


def read_context(workspace: Path, ticker: str) -> dict:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "finance_core", "context", "--workspace", str(workspace),
         "--ticker", ticker, "--format", "tradingagents"],
        capture_output=True, text=True, cwd=workspace, env=environment, check=False,
    )
    if result.returncode:
        raise ValueError("finance-core refused portfolio context: " + (result.stderr.strip() or result.stdout.strip()))
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict) or not isinstance(payload.get("positions"), list):
        raise ValueError("finance-core returned an invalid TradingAgents context")
    if set(payload) - {"cash", "currency", "positions"}:
        raise ValueError("finance-core returned unexpected context fields; nothing was shared")
    return payload


def explicit_models(args: argparse.Namespace) -> dict:
    fields = (("provider", "TRADINGAGENTS_LLM_PROVIDER", "llm_provider"),
              ("deep_model", "TRADINGAGENTS_DEEP_THINK_LLM", "deep_think_llm"),
              ("quick_model", "TRADINGAGENTS_QUICK_THINK_LLM", "quick_think_llm"))
    config = {}
    for flag, variable, key in fields:
        value = getattr(args, flag, None) or os.environ.get(variable)
        if not value or not value.strip():
            raise ValueError(f"Choose --{flag.replace('_', '-')} or set {variable}; no model defaults are selected")
        config[key] = value.strip()
    return config


def verify_environment() -> str:
    path = external_path(Path(sys.prefix), "TradingAgents environment")
    try:
        receipt = json.loads((path / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ValueError("Use the Python interpreter from the external managed TradingAgents environment") from None
    expected = manifest()["tools"]["tradingagents"]
    if (receipt.get("managed_by") != "personal-finance-skills" or receipt.get("tool") != "tradingagents"
            or receipt.get("status") != "ready" or receipt.get("revision") != expected["revision"]):
        raise ValueError("Managed TradingAgents environment does not match integrations.json; run the installer")
    distribution = importlib.metadata.distribution("tradingagents")
    origin = json.loads(distribution.read_text("direct_url.json") or "{}")
    if origin.get("vcs_info", {}).get("commit_id") != expected["revision"]:
        raise ValueError("Installed TradingAgents source revision is not the pinned revision")
    return expected["revision"]


def execute(payload: dict, workspace: Path, output: Path, ticker: str, day: str, models: dict) -> dict:
    revision = verify_environment()
    # Import only after local validation; cwd and every configured output are private.
    previous = Path.cwd()
    try:
        os.chdir(workspace)
        from tradingagents.portfolio import PortfolioContext
        portfolio = PortfolioContext.model_validate(payload)
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        output.mkdir(mode=0o700, parents=True, exist_ok=False)
        config = deepcopy(DEFAULT_CONFIG)
        config.update(models)
        config.update(results_dir=str(output / "logs"), data_cache_dir=str(output / "cache"),
                      memory_log_path=str(output / "memory" / "decisions.md"), checkpoint_enabled=False)
        graph = TradingAgentsGraph(debug=False, config=config)
        final_state, signal = graph.propagate(ticker, day, portfolio=portfolio)
        graph.save_reports(final_state, ticker, save_path=output / "reports")
        receipt = {"ticker": ticker, "analysis_date": day, "upstream_revision": revision,
                   "models": models, "signal": signal, "purpose": "research; no order execution"}
        (output / "run.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return receipt
    finally:
        os.chdir(previous)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--ticker", required=True)
    # Upstream validates its analysis date against the host's local calendar.
    # finance-core independently checks ledger freshness using today's UTC date.
    today = date.today()
    parser.add_argument("--date", default=today.isoformat(), help="Analysis date; defaults to today in the host's local timezone")
    parser.add_argument("--dry-run", action="store_true", help="Print exact shared portfolio JSON; no model calls or writes")
    parser.add_argument("--output", help="New external directory for this run's reports, memory, and cache")
    parser.add_argument("--provider")
    parser.add_argument("--deep-model")
    parser.add_argument("--quick-model")
    args = parser.parse_args(argv)
    try:
        workspace = external_path(args.workspace, "Workspace")
        if not workspace.is_dir():
            raise ValueError("Workspace must already exist; initialize it using finance-core")
        ticker = args.ticker.strip().upper()
        if not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=-]{0,39}", ticker):
            raise ValueError("Ticker must be a symbol, not a path or natural-language instruction")
        day = date.fromisoformat(args.date)
        if day.isoformat() != args.date or day > today:
            raise ValueError("Date must be YYYY-MM-DD and cannot be in the future")
        # The core ledger represents its current accepted snapshot, not a historical book.
        if day != today:
            raise ValueError("Historical portfolio runs need a dated holdings snapshot; this runner supports today's book only")
        proposed_output = args.output or workspace / "research" / (
            ticker.replace("^", "index-") + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
        output = external_path(proposed_output, "Output")
        if output.exists():
            raise ValueError("Output directory already exists; choose a new directory to preserve earlier reports")
        payload = read_context(workspace, ticker)
        if args.dry_run:
            print(json.dumps(payload, indent=2, allow_nan=False))
            return 0
        models = explicit_models(args)
        print("Running research with the explicitly permitted portfolio context. Model/data providers may charge.", file=sys.stderr)
        execute(payload, workspace, output, ticker, args.date, models)
        print(json.dumps({"status": "complete", "output": str(output), "trading": False}))
        return 0
    except (ValueError, OSError, KeyError, ImportError, subprocess.CalledProcessError) as exc:
        print(f"Research stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
