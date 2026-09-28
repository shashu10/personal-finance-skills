"""Small JSON-output command line interface."""

import argparse
import json
import sys

from . import core


def parser():
    result = argparse.ArgumentParser(description="Private, deterministic personal finance workspace; no network calls.")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("init", "validate", "import", "summary", "plan", "review", "context", "memory"):
        command = commands.add_parser(name)
        command.add_argument("--workspace", help="Private directory outside this checkout; defaults to FINANCE_WORKSPACE or ~/.local/share/personal-finance-skills")
        if name == "init":
            command.add_argument("--base-currency", default="USD")
            command.add_argument("--demo", action="store_true", help="Explicitly initialize synthetic sample accounts")
        if name in {"import", "memory"}:
            command.add_argument("--input", required=True)
        if name == "import":
            command.add_argument("--replace-same-date", action="store_true")
        if name in {"summary", "plan", "review", "context"}:
            command.add_argument("--as-of", help="Assessment date YYYY-MM-DD; defaults to today")
        if name == "plan":
            command.add_argument("--monthly-expenses", required=True)
            command.add_argument("--monthly-income", default="0")
            command.add_argument("--one-time-cost", default="0")
        if name == "review":
            command.add_argument("--proposal", required=True)
        if name == "context":
            command.add_argument("--ticker", required=True)
            command.add_argument("--format", choices=("relative", "tradingagents"), default="relative")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            value = core.init_workspace(args.workspace, base_currency=args.base_currency, use_demo=args.demo)
        elif args.command == "validate":
            value = core.validate_workspace(args.workspace)
        elif args.command == "import":
            value = core.import_snapshot(args.workspace, core.load_json(args.input), replace_same_date=args.replace_same_date)
        elif args.command == "summary":
            value = core.summary(args.workspace, args.as_of)
        elif args.command == "plan":
            value = core.plan(args.workspace, args.monthly_expenses, args.monthly_income, args.one_time_cost, args.as_of)
        elif args.command == "review":
            value = core.review(args.workspace, core.load_json(args.proposal), args.as_of)
        elif args.command == "context":
            value = core.context(args.workspace, args.ticker, args.format, args.as_of)
        else:
            value = core.memory(args.workspace, core.load_json(args.input))
        print(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))
        if args.command == "context" and value.get("status") == "needs_data":
            return 2
        return 0
    except (core.FinanceError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
