"""Validated private snapshots and deterministic planning; stdlib only."""

from __future__ import annotations

import contextlib
import copy
import datetime as dt
import decimal
import json
import os
from pathlib import Path
import re
import tempfile

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
    import msvcrt

decimal.getcontext().prec = 40
D = decimal.Decimal
ZERO = D("0")
REPO_ROOT = Path(__file__).resolve().parents[2]
FILES = ("ledger.json", "transactions.json", "lots.json", "facts.json", "rules.json", "decisions.json")
ACCOUNT_TYPES = {"bank", "brokerage", "retirement", "hsa", "pension", "education", "crypto", "other"}
RESTRICTED_TYPES = {"retirement", "hsa", "pension", "education"}


class FinanceError(ValueError):
    """An unsafe, invalid, or incomplete request."""


def fail(message):
    raise FinanceError(message)


def number(value, label="amount", *, nullable=False, signed=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"-?\d+(?:\.\d+)?", value) or len(value) > 80:
        fail(f"{label} must be a finite decimal string" + (" or null" if nullable else ""))
    result = D(value)
    if not result.is_finite() or abs(result) > D("1e25") or (not signed and result < 0):
        fail(f"{label} is out of range")
    return result


def fmt(value):
    return None if value is None else format(value, "f")


def date(value, label="date"):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        fail(f"{label} must be YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        fail(f"{label} is not a calendar date")


def today():
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def string(value, label, pattern=None):
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        fail(f"{label} must be nonempty text")
    if pattern and not re.fullmatch(pattern, value):
        fail(f"Invalid {label}")
    return value


def currency(value):
    return string(value, "currency", r"[A-Z]{3}")


def identifier(value, label="id"):
    return string(value, label, r"[a-zA-Z][a-zA-Z0-9_.:-]{0,127}")


def symbol(value):
    return string(value, "symbol", r"[A-Z0-9][A-Z0-9.\-:/^]{0,39}")


def obj(value, label):
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def items(value, label):
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def required(record, keys, label):
    obj(record, label)
    missing = set(keys) - record.keys()
    if missing:
        fail(f"{label} missing: {', '.join(sorted(missing))}")


def boolean(record, field):
    if type(record.get(field)) is not bool:
        fail(f"{field} must be true or false")


def no_duplicates(records, label):
    seen = set()
    for record in records:
        key = record["id"]
        if key in seen:
            fail(f"Duplicate {label} id: {key}")
        seen.add(key)


def workspace_path(raw=None):
    path = Path(raw or os.environ.get("FINANCE_WORKSPACE") or Path.home() / ".local/share/personal-finance-skills").expanduser().resolve()
    for ancestor in (path, *path.parents):
        manifest = ancestor / ".codex-plugin/plugin.json"
        project = ancestor / "pyproject.toml"
        # Identify the public boundary even when invoked from an installed wheel.
        if ancestor == REPO_ROOT and (ancestor / "src/finance_core/core.py").exists():
            fail("Private workspaces must be outside the public checkout")
        if project.is_file():
            import tomllib
            try:
                name = tomllib.loads(project.read_text(encoding="utf-8")).get("project", {}).get("name")
            except (OSError, ValueError):
                name = None
            if name == "personal-finance-skills":
                fail("Private workspaces must be outside the public checkout")
        if manifest.is_file():
            try:
                name = json.loads(manifest.read_text(encoding="utf-8")).get("name")
            except (OSError, ValueError, AttributeError):
                name = None
            if name == "personal-finance-skills":
                fail("Private workspaces must be outside the public checkout")
    return path


def check_file(path):
    if path.is_symlink():
        fail(f"Refusing symlink data file: {path.name}")
    if path.exists() and not path.is_file():
        fail(f"Expected regular data file: {path.name}")


@contextlib.contextmanager
def locked(raw=None, *, create=False):
    path = workspace_path(raw)
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir():
        fail("Workspace does not exist; run init first")
    if os.name != "nt" and path.stat().st_mode & 0o077:
        fail("Existing private workspace must have mode 0700; choose a dedicated private directory or restrict its permissions")
    for name in FILES + (".finance.lock",):
        check_file(path / name)
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path / ".finance.lock", flags, 0o600)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        else:
            if os.fstat(fd).st_size == 0:
                os.write(fd, b"\0")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        for name in FILES:
            check_file(path / name)
        yield path
    finally:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_UN)
        else:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        os.close(fd)


def load_json(path):
    path = Path(path)
    check_file(path)
    try:
        # Reject duplicate keys and non-standard NaN/Infinity before interpretation.
        def pairs(rows):
            result = {}
            for key, value in rows:
                if key in result:
                    fail(f"Duplicate JSON key: {key}")
                result[key] = value
            return result
        with path.open(encoding="utf-8") as stream:
            return json.load(stream, object_pairs_hook=pairs, parse_constant=lambda value: fail(f"Invalid JSON constant: {value}"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Cannot read {path.name}: {exc}")


def commit(path, updates):
    """Stage all bytes, atomically replace files, roll back ordinary I/O failures."""
    staged, previous = {}, {}
    try:
        for name, value in updates.items():
            target = path / name
            check_file(target)
            previous[name] = target.read_bytes() if target.exists() else None
            fd, temporary = tempfile.mkstemp(prefix=f".{name}.", dir=path)
            staged[name] = Path(temporary)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
        replaced = []
        try:
            for name, temporary in staged.items():
                check_file(path / name)
                os.replace(temporary, path / name)
                replaced.append(name)
        except OSError:
            for name in reversed(replaced):
                if previous[name] is None:
                    (path / name).unlink()
                else:
                    fd, temporary = tempfile.mkstemp(prefix=".rollback.", dir=path)
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(previous[name])
                    os.replace(temporary, path / name)
            raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def blank(base_currency="USD"):
    currency(base_currency)
    result = {name: {"schema_version": 1, "items": []} for name in FILES}
    result["ledger.json"] = {"schema_version": 1, "base_currency": base_currency, "accounts": [], "fx_rates": {}}
    result["rules.json"] = {"schema_version": 1, "max_age_days": 7,
        "limits": {"max_position_fraction": None, "max_debt_to_assets": None},
        "sharing": {"relative_context": False, "tradingagents_amounts": False}}
    return result


def demo(base_currency="USD"):
    result = blank(base_currency)
    result["ledger.json"]["accounts"] = [
        {"id": "sample-bank", "institution": "Example Bank", "type": "bank", "currency": base_currency,
         "as_of": today(), "source": "synthetic demo", "status": "verified", "include_in_totals": True,
         "restricted": False, "cash": "12000", "liabilities": "0", "reported_total": "12000", "positions": []},
        {"id": "sample-brokerage", "institution": "Example Broker", "type": "brokerage", "currency": base_currency,
         "as_of": today(), "source": "synthetic demo", "status": "verified", "include_in_totals": True,
         "restricted": False, "cash": "1000", "liabilities": "0", "reported_total": "5000",
         "positions": [{"symbol": "EXAMPLE", "quantity": "20", "market_value": "4000", "cost_basis": "3000"}]}]
    return result


def init_workspace(raw=None, *, base_currency="USD", use_demo=False):
    with locked(raw, create=True) as path:
        existing = [name for name in FILES if (path / name).exists()]
        if use_demo and existing:
            fail("Demo initialization requires an empty workspace")
        state = demo(base_currency) if use_demo else blank(base_currency)
        updates = {name: value for name, value in state.items() if name not in existing}
        if existing:
            for name in existing:
                state[name] = load_json(path / name)
        validate_state(state)
        commit(path, updates)
        return {"workspace": str(path), "created": list(updates), "demo": use_demo}


def validate_account(account):
    required(account, ("id", "institution", "type", "currency", "as_of", "source", "status", "include_in_totals", "restricted", "positions", "cash", "liabilities"), "account")
    identifier(account["id"])
    string(account["institution"], "institution")
    if not isinstance(account["type"], str) or account["type"] not in ACCOUNT_TYPES:
        fail("Unsupported account type")
    currency(account["currency"])
    date(account["as_of"])
    string(account["source"], "source")
    if not isinstance(account["status"], str) or account["status"] not in {"verified", "estimated", "unverified"}:
        fail("Unsupported account status")
    boolean(account, "include_in_totals")
    boolean(account, "restricted")
    cash = number(account["cash"], "cash", nullable=True)
    debt = number(account["liabilities"], "liabilities", nullable=True)
    seen, values = set(), []
    for pos in items(account["positions"], "positions"):
        required(pos, ("symbol", "quantity", "market_value"), "position")
        ticker = symbol(pos["symbol"])
        if ticker in seen:
            fail(f"Duplicate position {ticker}; consolidate lots in positions")
        seen.add(ticker)
        quantity = number(pos["quantity"], "quantity", nullable=True)
        value = number(pos["market_value"], "market_value", nullable=True)
        if quantity == 0 and value not in (ZERO, None):
            fail("A zero-quantity position cannot have positive market value")
        values.append(value)
        if "cost_basis" in pos:
            number(pos["cost_basis"], "cost_basis", nullable=True)
    if "reported_total" in account:
        reported = number(account["reported_total"], "reported_total", nullable=True, signed=True)
        if reported is not None and cash is not None and debt is not None and all(v is not None for v in values):
            if abs(cash + sum(values, ZERO) - debt - reported) > D("0.01"):
                fail(f"Account {account['id']} does not reconcile to reported_total")


def validate_state(state):
    for name in FILES:
        required(state.get(name), ("schema_version",), name)
        if type(state[name]["schema_version"]) is not int or state[name]["schema_version"] != 1:
            fail(f"Unsupported schema version: {name}")
    ledger = state["ledger.json"]
    required(ledger, ("base_currency", "accounts", "fx_rates"), "ledger")
    currency(ledger["base_currency"])
    for account in items(ledger["accounts"], "accounts"):
        validate_account(account)
    no_duplicates(ledger["accounts"], "account")
    accounts = {a["id"]: a for a in ledger["accounts"]}
    for curr, rate in obj(ledger["fx_rates"], "fx_rates").items():
        currency(curr)
        required(rate, ("rate", "as_of", "source"), "FX rate")
        if number(rate["rate"], "FX rate") <= 0:
            fail("FX rate must be positive")
        date(rate["as_of"])
        string(rate["source"], "FX source")
        if curr == ledger["base_currency"] and D(rate["rate"]) != 1:
            fail("Base currency FX rate must equal one")
    rules = state["rules.json"]
    required(rules, ("max_age_days", "limits", "sharing"), "rules")
    if type(rules["max_age_days"]) is not int or not 0 <= rules["max_age_days"] <= 3650:
        fail("max_age_days must be an integer from 0 to 3650")
    required(rules["limits"], ("max_position_fraction", "max_debt_to_assets"), "limits")
    if set(rules["limits"]) - {"max_position_fraction", "max_debt_to_assets"}:
        fail("Unknown risk limit; this version cannot evaluate it")
    for name, value in rules["limits"].items():
        limit = number(value, name, nullable=True)
        if limit is not None and limit > 1:
            fail(f"{name} must be a fraction between zero and one")
    required(rules["sharing"], ("relative_context", "tradingagents_amounts"), "sharing")
    for key in ("relative_context", "tradingagents_amounts"):
        boolean(rules["sharing"], key)
    for filename in ("transactions.json", "lots.json", "facts.json", "decisions.json"):
        records = items(state[filename].get("items"), filename)
        for record in records:
            required(record, ("id",), filename)
            identifier(record["id"])
            if filename in ("facts.json", "decisions.json"):
                required(record, ("date", "text", "source", "user_confirmed"), filename)
                date(record["date"])
                string(record["text"], "text")
                string(record["source"], "source")
                boolean(record, "user_confirmed")
                if filename == "facts.json" and not record["user_confirmed"]:
                    fail("Facts require explicit user confirmation")
                if filename == "decisions.json":
                    if not isinstance(record.get("status"), str) or record.get("status") not in {"proposal", "confirmed", "executed"}:
                        fail("Decision status must be proposal, confirmed, or executed")
                    if record["status"] != "proposal" and not record["user_confirmed"]:
                        fail("Confirmed and executed decisions require user confirmation")
                if "supersedes" in record:
                    identifier(record["supersedes"], "supersedes")
                    if record["supersedes"] == record["id"]:
                        fail("An entry cannot supersede itself")
            else:
                required(record, ("account_id", "currency"), filename)
                identifier(record["account_id"], "account_id")
                currency(record["currency"])
                if record["account_id"] not in accounts:
                    fail(f"Unknown account in {filename}")
                if filename == "transactions.json":
                    required(record, ("date", "type", "amount"), "transaction")
                    date(record["date"])
                    if not isinstance(record["type"], str) or record["type"] not in {"transfer", "income", "expense", "buy", "sell", "dividend", "fee", "other"}:
                        fail("Unsupported transaction type")
                    number(record["amount"], "transaction amount", signed=True)
                else:
                    required(record, ("symbol", "acquired_on", "quantity", "cost_basis"), "lot")
                    symbol(record["symbol"])
                    date(record["acquired_on"])
                    if number(record["quantity"], "lot quantity") <= 0:
                        fail("Lot quantity must be positive")
                    number(record["cost_basis"], "lot cost basis", nullable=True)
        no_duplicates(records, filename)
        if filename in ("facts.json", "decisions.json"):
            by_id = {r["id"]: r for r in records}
            for record in records:
                target = record.get("supersedes")
                if target is not None and (target not in by_id or by_id[target]["date"] > record["date"]):
                    fail("supersedes must reference an existing entry at an earlier or equal date")
                seen = {record["id"]}
                while target:
                    if target not in by_id:
                        fail("supersedes references an unknown entry")
                    if target in seen:
                        fail("Cyclic supersedes chain")
                    seen.add(target)
                    target = by_id[target].get("supersedes")
    return {"valid": True, "accounts": len(accounts)}


def read_state(path):
    state = {name: load_json(path / name) for name in FILES}
    validate_state(state)
    return state


def validate_workspace(raw=None):
    with locked(raw) as path:
        return validate_state(read_state(path))


def append_unique(existing, incoming, label):
    by_id = {row["id"]: row for row in existing}
    added = 0
    for row in items(incoming, label):
        required(row, ("id",), label)
        identifier(row["id"])
        if row["id"] in by_id:
            if by_id[row["id"]] != row:
                fail(f"Conflicting {label} id: {row['id']}")
        else:
            existing.append(copy.deepcopy(row))
            by_id[row["id"]] = row
            added += 1
    return added


def import_snapshot(raw, payload, *, replace_same_date=False):
    required(payload, ("account",), "import")
    if set(payload) - {"account", "transactions", "lots", "fx_rates"}:
        fail("Unknown import fields")
    validate_account(payload["account"])
    with locked(raw) as path:
        state = read_state(path)
        ledger = state["ledger.json"]
        incoming = copy.deepcopy(payload["account"])
        prior = next((a for a in ledger["accounts"] if a["id"] == incoming["id"]), None)
        if prior:
            if prior["as_of"] > incoming["as_of"]:
                fail("Refusing to overwrite a newer account snapshot")
            if prior["as_of"] == incoming["as_of"] and prior != incoming and not replace_same_date:
                fail("Different snapshot at same date; review and use --replace-same-date explicitly")
            if prior["currency"] != incoming["currency"]:
                fail("Account currency cannot change; use a new account alias")
            ledger["accounts"][ledger["accounts"].index(prior)] = incoming
        else:
            ledger["accounts"].append(incoming)
        for curr, rate in obj(payload.get("fx_rates", {}), "fx_rates").items():
            required(rate, ("rate", "as_of", "source"), "FX rate")
            date(rate["as_of"])
            old = ledger["fx_rates"].get(curr)
            if old and old["as_of"] > rate["as_of"]:
                fail("Refusing older FX rate")
            if old and old["as_of"] == rate["as_of"] and old != rate and not replace_same_date:
                fail("Different FX rate at same date; use --replace-same-date explicitly")
            ledger["fx_rates"][curr] = copy.deepcopy(rate)
        counts = {}
        for key in ("transactions", "lots"):
            counts[key] = append_unique(state[f"{key}.json"]["items"], payload.get(key, []), key)
        validate_state(state)
        commit(path, {name: state[name] for name in ("ledger.json", "transactions.json", "lots.json")})
        return {"imported_account": incoming["id"], "added": counts, "snapshot_unchanged": prior == incoming}


def memory(raw, payload):
    obj(payload, "memory input")
    if not payload or set(payload) - {"decisions", "facts"}:
        fail("Memory input must contain decisions and/or facts")
    with locked(raw) as path:
        state = read_state(path)
        counts = {}
        for key in ("decisions", "facts"):
            counts[key] = append_unique(state[f"{key}.json"]["items"], payload.get(key, []), key)
        validate_state(state)
        commit(path, {f"{key}.json": state[f"{key}.json"] for key in payload})
        return {"added": counts}


def freshness(value, as_of, max_age):
    age = (date(as_of) - date(value)).days
    return "future-dated" if age < 0 else "stale" if age > max_age else None


def summarize_state(state, as_of=None):
    as_of = as_of or today()
    date(as_of)
    ledger, rules = state["ledger.json"], state["rules.json"]
    issues, assets, debt, cash = [], ZERO, ZERO, ZERO
    complete, included, positions = True, 0, {}
    for account in ledger["accounts"]:
        if not account["include_in_totals"]:
            continue
        included += 1
        label = account["id"]
        when = freshness(account["as_of"], as_of, rules["max_age_days"])
        if when:
            issues.append(f"{label}: {when} account snapshot")
        if account["status"] != "verified":
            issues.append(f"{label}: {account['status']} account snapshot")
        rate = D("1")
        if account["currency"] != ledger["base_currency"]:
            fx = ledger["fx_rates"].get(account["currency"])
            if not fx:
                complete = False
                issues.append(f"{label}: missing {account['currency']} FX rate")
                continue
            rate = D(fx["rate"])
            when = freshness(fx["as_of"], as_of, rules["max_age_days"])
            if when:
                issues.append(f"{label}: {when} FX rate")
        for field in ("cash", "liabilities"):
            value = number(account[field], field, nullable=True)
            if value is None:
                complete = False
                issues.append(f"{label}: unknown {field}")
            elif field == "cash":
                assets += value * rate
                if not account["restricted"] and account["type"] not in RESTRICTED_TYPES:
                    cash += value * rate
            else:
                debt += value * rate
        for pos in account["positions"]:
            value = number(pos["market_value"], nullable=True)
            if value is None:
                complete = False
                issues.append(f"{label}: unknown value for {pos['symbol']}")
            else:
                assets += value * rate
                positions[pos["symbol"]] = positions.get(pos["symbol"], ZERO) + value * rate
            if pos["quantity"] is None:
                issues.append(f"{label}: unknown quantity for {pos['symbol']}")
    if not included:
        complete = False
        issues.append("No included account snapshots")
    ready = complete and not issues
    return {"base_currency": ledger["base_currency"], "as_of": as_of, "accounts_included": included,
        "complete": complete, "ready": ready, "issues": issues,
        "assets": fmt(assets) if complete else None, "liabilities": fmt(debt) if complete else None,
        "net_worth": fmt(assets - debt) if complete else None,
        "unrestricted_liquid_cash": fmt(cash) if complete else None,
        "known_subtotals": {"assets": fmt(assets), "liabilities": fmt(debt), "unrestricted_liquid_cash": fmt(cash)},
        "position_values": {s: fmt(v) for s, v in sorted(positions.items())},
        "position_fractions": {s: fmt(v / assets) if complete and assets > 0 else None for s, v in sorted(positions.items())},
        "debt_to_assets": fmt(debt / assets) if complete and assets > 0 else None}


def summary(raw=None, as_of=None):
    with locked(raw) as path:
        return summarize_state(read_state(path), as_of)


def plan(raw, monthly_expenses, monthly_income="0", one_time_cost="0", as_of=None):
    expenses = number(monthly_expenses, "monthly_expenses")
    income = number(monthly_income, "monthly_income")
    one_time = number(one_time_cost, "one_time_cost")
    result = summary(raw, as_of)
    ready = result["ready"]
    balance = D(result["unrestricted_liquid_cash"]) - one_time if ready else None
    burn = expenses - income
    return {"status": "scenario" if ready else "needs_data", "base_currency": result["base_currency"],
        "monthly_expenses": fmt(expenses), "monthly_income": fmt(income), "one_time_cost": fmt(one_time),
        "monthly_cash_deficit": fmt(burn), "cash_after_one_time_cost": fmt(balance),
        "runway_months": fmt(max(balance, ZERO) / burn) if ready and burn > 0 else None,
        "one_time_cost_funded": balance >= 0 if ready else None,
        "cash_flow_nonnegative": burn <= 0, "issues": result["issues"],
        "assumptions": ["Uses unrestricted cash only; no securities sales", "Income and expenses are explicit scenario inputs in base currency", "No taxes, investment returns, inflation, or additional debt repayments are modeled"]}


def review(raw, proposal, as_of=None):
    required(proposal, ("account_id", "symbol", "side", "quantity", "price", "as_of"), "proposal")
    identifier(proposal["account_id"], "account_id")
    symbol(proposal["symbol"])
    if not isinstance(proposal["side"], str) or proposal["side"] not in {"buy", "sell"}:
        fail("Proposal side must be buy or sell")
    quantity, price = number(proposal["quantity"], "quantity"), number(proposal["price"], "price")
    if quantity <= 0 or price <= 0:
        fail("Proposal quantity and price must be positive")
    date(proposal["as_of"])
    as_of = as_of or today()
    with locked(raw) as path:
        state = read_state(path)
    current = summarize_state(state, as_of)
    issues = current["issues"][:]
    when = freshness(proposal["as_of"], as_of, state["rules.json"]["max_age_days"])
    if when:
        issues.append(f"Proposal price is {when}")
    account = next((a for a in state["ledger.json"]["accounts"] if a["id"] == proposal["account_id"]), None)
    if account is None:
        issues.append("Unknown proposal account")
    elif not account["include_in_totals"]:
        issues.append("Proposal account is excluded from totals")
    if issues:
        return {"status": "needs_data", "issues": issues, "current": current, "projected": None}
    position = next((p for p in account["positions"] if p["symbol"] == proposal["symbol"]), None)
    existing_quantity = D(position["quantity"]) if position else ZERO
    existing_value = D(position["market_value"]) if position else ZERO
    cost, cash = price * quantity, D(account["cash"])
    if proposal["side"] == "buy" and cost > cash:
        return {"status": "invalid_proposal", "issues": ["Insufficient recorded cash; borrowing is not modeled"], "projected": None}
    if proposal["side"] == "sell" and quantity > existing_quantity:
        return {"status": "invalid_proposal", "issues": ["Sell quantity exceeds recorded holdings"], "projected": None}
    if proposal["side"] == "buy":
        new_quantity, new_value, new_cash = existing_quantity + quantity, existing_value + cost, cash - cost
    else:
        new_quantity = existing_quantity - quantity
        new_value = existing_value * new_quantity / existing_quantity
        new_cash = cash + cost
    account["cash"] = fmt(new_cash)
    account.pop("reported_total", None)
    if position:
        position["quantity"], position["market_value"] = fmt(new_quantity), fmt(new_value)
        position.pop("cost_basis", None)
    else:
        account["positions"].append({"symbol": proposal["symbol"], "quantity": fmt(new_quantity), "market_value": fmt(new_value)})
    projected = summarize_state(state, as_of)
    limits = state["rules.json"]["limits"]
    breaches, evaluated = [], []
    for name, value in limits.items():
        if value is None:
            continue
        if name == "max_position_fraction":
            fractions = projected["position_fractions"]
            if projected["assets"] is None or D(projected["assets"]) <= 0:
                issues.append("Cannot evaluate concentration with zero or unknown assets")
            else:
                evaluated.append(name)
                for ticker, fraction in fractions.items():
                    if D(fraction) > D(value):
                        breaches.append({"limit": name, "symbol": ticker, "actual": fraction, "maximum": value})
        elif projected["debt_to_assets"] is None:
            issues.append("Cannot evaluate leverage with zero or unknown assets")
        else:
            evaluated.append(name)
            if D(projected["debt_to_assets"]) > D(value):
                breaches.append({"limit": name, "actual": projected["debt_to_assets"], "maximum": value})
    status = "needs_data" if issues else "breaches_limits" if breaches else "within_limits" if evaluated else "report_only"
    return {"status": status, "issues": issues, "breaches": breaches, "evaluated_limits": evaluated,
        "current": current, "projected": projected, "assumptions": ["Cash-funded long-only scenario", "No fees or taxes", "Existing positions retain recorded marks; sale proceeds use the supplied price"]}


def context(raw, ticker, output_format="relative", as_of=None):
    symbol(ticker)
    if output_format not in {"relative", "tradingagents"}:
        fail("Unsupported context format")
    with locked(raw) as path:
        state = read_state(path)
    sharing = state["rules.json"]["sharing"]
    if not sharing["relative_context"]:
        fail("Set rules.sharing.relative_context to true before generating context")
    if output_format == "tradingagents" and not sharing["tradingagents_amounts"]:
        fail("TradingAgents amount export requires rules.sharing.tradingagents_amounts: true")
    report = summarize_state(state, as_of)
    if not report["ready"] or not report["assets"] or D(report["assets"]) <= 0:
        # Avoid account alias disclosure through detailed source issues.
        return {"status": "needs_data", "ticker": ticker, "message": "Run summary locally and resolve incomplete, stale, or unverified data"}
    selected = []
    for account in state["ledger.json"]["accounts"]:
        if account["include_in_totals"]:
            selected.extend(p for p in account["positions"] if p["symbol"] == ticker)
    result = {"status": "ready", "ticker": ticker, "as_of": report["as_of"], "format": output_format,
        "held": bool(selected), "position_fraction": report["position_fractions"].get(ticker, "0"),
        "debt_to_assets": report["debt_to_assets"], "limits": state["rules.json"]["limits"]}
    if output_format == "tradingagents":
        grouped = {}
        for account in state["ledger.json"]["accounts"]:
            if not account["include_in_totals"]:
                continue
            rate = D("1") if account["currency"] == report["base_currency"] else D(state["ledger.json"]["fx_rates"][account["currency"]]["rate"])
            for position in account["positions"]:
                aggregate = grouped.setdefault(position["symbol"], {"quantity": ZERO, "cost_basis": ZERO, "basis_known": True})
                aggregate["quantity"] += D(position["quantity"])
                if position.get("cost_basis") is None or account["currency"] != report["base_currency"]:
                    aggregate["basis_known"] = False
                else:
                    aggregate["cost_basis"] += D(position["cost_basis"]) * rate
        positions = []
        for ticker_name, aggregate in sorted(grouped.items()):
            if aggregate["quantity"] <= 0:
                continue
            position = {"ticker": ticker_name, "quantity": float(aggregate["quantity"])}
            if aggregate["basis_known"]:
                position["average_price"] = float(aggregate["cost_basis"] / aggregate["quantity"])
            positions.append(position)
        # Household cash is not automatically deployable at a particular broker.
        return {"cash": None, "currency": report["base_currency"], "positions": positions}
    return result
