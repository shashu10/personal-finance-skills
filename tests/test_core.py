import copy
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from finance_core import core


DAY = "2026-01-20"


def account(alias="main-bank", **kwargs):
    result = {"id": alias, "institution": "Example Institution", "type": "bank", "currency": "USD",
              "as_of": DAY, "source": "synthetic fixture", "status": "verified", "include_in_totals": True,
              "restricted": False, "positions": [], "cash": "1000", "liabilities": "0", "reported_total": "1000"}
    result.update(kwargs)
    return result


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name) / "private"
        core.init_workspace(self.workspace)

    def tearDown(self):
        self.temp.cleanup()

    def import_account(self, value, **kwargs):
        return core.import_snapshot(self.workspace, {"account": value, **kwargs})

    def alter_rules(self, **updates):
        filename = self.workspace / "rules.json"
        data = core.load_json(filename)
        data.update(updates)
        core.commit(self.workspace, {"rules.json": data})

    def test_empty_is_unknown_not_zero_and_init_never_overwrites(self):
        before = (self.workspace / "rules.json").read_bytes()
        self.assertFalse(core.summary(self.workspace, DAY)["ready"])
        self.assertIsNone(core.summary(self.workspace, DAY)["net_worth"])
        self.assertEqual(core.init_workspace(self.workspace)["created"], [])
        self.assertEqual(before, (self.workspace / "rules.json").read_bytes())
        with self.assertRaises(core.FinanceError):
            core.init_workspace(self.workspace, use_demo=True)

    def test_repeat_import_dedupes_transactions_and_lots(self):
        payload = {"account": account(), "transactions": [{"id": "transfer-1", "account_id": "main-bank", "date": DAY,
                    "type": "transfer", "amount": "100", "currency": "USD"}],
                   "lots": [{"id": "lot-1", "account_id": "main-bank", "symbol": "EXAMPLE", "acquired_on": DAY,
                            "quantity": "2", "cost_basis": "200", "currency": "USD"}]}
        first = core.import_snapshot(self.workspace, payload)
        second = core.import_snapshot(self.workspace, payload)
        self.assertEqual(first["added"], {"transactions": 1, "lots": 1})
        self.assertEqual(second["added"], {"transactions": 0, "lots": 0})
        self.assertEqual(core.summary(self.workspace, DAY)["net_worth"], "1000")

    def test_failed_import_leaves_all_files_unchanged(self):
        self.import_account(account())
        before = {name: (self.workspace / name).read_bytes() for name in core.FILES}
        payload = {"account": account(as_of="2026-01-21", cash="2000", reported_total="2000"),
                   "transactions": [{"id": "broken", "account_id": "no-account", "date": DAY, "type": "income", "amount": "100", "currency": "USD"}]}
        with self.assertRaises(core.FinanceError):
            core.import_snapshot(self.workspace, payload)
        self.assertEqual(before, {name: (self.workspace / name).read_bytes() for name in core.FILES})

    def test_reconciliation_and_same_date_changes_require_attention(self):
        with self.assertRaisesRegex(core.FinanceError, "reconcile"):
            self.import_account(account(reported_total="1001"))
        self.import_account(account())
        with self.assertRaisesRegex(core.FinanceError, "same date"):
            self.import_account(account(cash="2000", reported_total="2000"))
        core.import_snapshot(self.workspace, {"account": account(cash="2000", reported_total="2000")}, replace_same_date=True)
        with self.assertRaisesRegex(core.FinanceError, "newer"):
            self.import_account(account(as_of="2026-01-01"))

    def test_fx_and_parent_exclusion(self):
        self.import_account(account(currency="EUR"))
        self.assertIsNone(core.summary(self.workspace, DAY)["net_worth"])
        self.import_account(account(currency="EUR"), fx_rates={"EUR": {"rate": "1.2", "as_of": DAY, "source": "synthetic FX"}})
        self.import_account(account("wrapper", include_in_totals=False, cash="99999", reported_total="99999"))
        self.assertEqual(core.summary(self.workspace, DAY)["net_worth"], "1200.0")
        self.assertFalse(core.summary(self.workspace, "2026-02-20")["ready"])

    def test_missing_stale_future_unverified_cannot_pass_review(self):
        proposal = {"account_id": "main-bank", "symbol": "EXAMPLE", "side": "buy", "quantity": "1", "price": "10", "as_of": DAY}
        for variant in (account(cash=None, reported_total=None), account(as_of="2026-01-01"),
                        account(as_of="2026-01-25"), account(status="unverified"), account(status="estimated")):
            with self.subTest(variant=variant):
                core.commit(self.workspace, {"ledger.json": {"schema_version": 1, "base_currency": "USD", "accounts": [variant], "fx_rates": {}}})
                self.assertEqual(core.review(self.workspace, proposal, DAY)["status"], "needs_data")

    def test_runway_excludes_retirement_and_restricted_cash(self):
        self.import_account(account())
        self.import_account(account("retirement", type="retirement", cash="100000", reported_total="100000"))
        self.import_account(account("restricted-bank", restricted=True, cash="100000", reported_total="100000"))
        result = core.plan(self.workspace, "200", "100", "100", DAY)
        self.assertEqual(result["runway_months"], "9")
        self.assertEqual(result["cash_after_one_time_cost"], "900")
        self.assertIsNone(core.plan(self.workspace, "100", "200", "0", DAY)["runway_months"])

    def test_projected_trade_concentration_and_funding(self):
        self.import_account(account(type="brokerage", positions=[{"symbol": "EXAMPLE", "quantity": "10", "market_value": "1000"}], reported_total="2000"))
        self.alter_rules(limits={"max_position_fraction": "0.6", "max_debt_to_assets": None})
        proposal = {"account_id": "main-bank", "symbol": "EXAMPLE", "side": "buy", "quantity": "5", "price": "100", "as_of": DAY}
        result = core.review(self.workspace, proposal, DAY)
        self.assertEqual(result["status"], "breaches_limits")
        self.assertEqual(result["projected"]["position_fractions"]["EXAMPLE"], "0.75")
        self.assertEqual(core.summary(self.workspace, DAY)["position_fractions"]["EXAMPLE"], "0.5")
        proposal["quantity"] = "11"
        self.assertEqual(core.review(self.workspace, proposal, DAY)["status"], "invalid_proposal")
        proposal.update(side="sell", quantity="20")
        self.assertEqual(core.review(self.workspace, proposal, DAY)["status"], "invalid_proposal")
        proposal.update(quantity="5", price="120")
        result = core.review(self.workspace, proposal, DAY)
        self.assertEqual(result["status"], "within_limits")
        self.assertEqual(result["projected"]["assets"], "2100")

    def test_null_limits_are_report_only(self):
        self.import_account(account())
        proposal = {"account_id": "main-bank", "symbol": "EXAMPLE", "side": "buy", "quantity": "1", "price": "10", "as_of": DAY}
        self.assertEqual(core.review(self.workspace, proposal, DAY)["status"], "report_only")

    def test_all_positions_and_debt_limit_checked(self):
        self.import_account(account(type="brokerage", liabilities="500", reported_total="1500",
                                    positions=[{"symbol": "OTHER", "quantity": "10", "market_value": "1000"}]))
        self.alter_rules(limits={"max_position_fraction": "0.4", "max_debt_to_assets": "0.2"})
        proposal = {"account_id": "main-bank", "symbol": "EXAMPLE", "side": "buy", "quantity": "1", "price": "10", "as_of": DAY}
        result = core.review(self.workspace, proposal, DAY)
        self.assertEqual({b["limit"] for b in result["breaches"]}, {"max_position_fraction", "max_debt_to_assets"})

    def test_memory_confirmation_dedupe_and_conflicts(self):
        entry = {"id": "decision-1", "date": DAY, "status": "confirmed", "text": "Keep emergency cash", "source": "user message", "user_confirmed": True}
        self.assertEqual(core.memory(self.workspace, {"decisions": [entry]})["added"]["decisions"], 1)
        self.assertEqual(core.memory(self.workspace, {"decisions": [entry]})["added"]["decisions"], 0)
        with self.assertRaises(core.FinanceError):
            core.memory(self.workspace, {"decisions": [{**entry, "text": "different"}]})
        with self.assertRaises(core.FinanceError):
            core.memory(self.workspace, {"facts": [{**entry, "id": "fact-1", "user_confirmed": False}]})
        with self.assertRaises(core.FinanceError):
            core.memory(self.workspace, {"decisions": [{**entry, "id": "decision-2", "status": "executed", "user_confirmed": False}]})

    def test_context_sharing_requires_explicit_flags(self):
        self.import_account(account())
        with self.assertRaises(core.FinanceError):
            core.context(self.workspace, "EXAMPLE", as_of=DAY)
        self.alter_rules(sharing={"relative_context": True, "tradingagents_amounts": False})
        result = core.context(self.workspace, "EXAMPLE", as_of=DAY)
        self.assertFalse(result["held"])
        self.assertNotIn("main-bank", json.dumps(result))
        self.assertNotIn("1000", json.dumps(result))
        with self.assertRaises(core.FinanceError):
            core.context(self.workspace, "EXAMPLE", "tradingagents", DAY)

    def test_upstream_context_exact_shape_and_no_assumed_broker_cash(self):
        self.import_account(account(type="brokerage", positions=[{"symbol": "EXAMPLE", "quantity": "10", "market_value": "1000", "cost_basis": "800"}], reported_total="2000"))
        self.alter_rules(sharing={"relative_context": True, "tradingagents_amounts": True})
        result = core.context(self.workspace, "EXAMPLE", "tradingagents", DAY)
        self.assertEqual(result, {"cash": None, "currency": "USD", "positions": [{"ticker": "EXAMPLE", "quantity": 10.0, "average_price": 80.0}]})
        self.import_account(account("foreign", currency="EUR", cash="0", positions=[{"symbol": "EXAMPLE", "quantity": "2", "market_value": "200", "cost_basis": "150"}], reported_total="200"), fx_rates={"EUR": {"rate": "1.2", "as_of": DAY, "source": "synthetic"}})
        result = core.context(self.workspace, "EXAMPLE", "tradingagents", DAY)
        self.assertEqual(result["positions"], [{"ticker": "EXAMPLE", "quantity": 12.0}])

    def test_installed_package_still_rejects_checkout_workspace(self):
        checkout = Path(self.temp.name) / "public"
        checkout.mkdir()
        (checkout / "pyproject.toml").write_text('[project]\nname = "personal-finance-skills"\n')
        with patch.object(core, "REPO_ROOT", Path(self.temp.name) / "site-packages"):
            with self.assertRaises(core.FinanceError):
                core.init_workspace(checkout / "private")

    def test_private_boundary_symlinks_and_permissions(self):
        with self.assertRaises(core.FinanceError):
            core.init_workspace(core.REPO_ROOT / "forbidden-private-data")
        link = Path(self.temp.name) / "source-link"
        link.symlink_to(core.REPO_ROOT, target_is_directory=True)
        with self.assertRaises(core.FinanceError):
            core.init_workspace(link / "private")
        original = self.workspace / "ledger.json"
        original.unlink()
        original.symlink_to(Path(self.temp.name) / "elsewhere")
        with self.assertRaises(core.FinanceError):
            core.validate_workspace(self.workspace)
        self.assertEqual(stat.S_IMODE((self.workspace / "rules.json").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.workspace.stat().st_mode), 0o700)

    @unittest.skipIf(os.name == "nt", "POSIX permission check")
    def test_existing_shared_directory_is_not_silently_repurposed(self):
        shared = Path(self.temp.name) / "existing"
        shared.mkdir(mode=0o755)
        shared.chmod(0o755)
        with self.assertRaisesRegex(core.FinanceError, "0700"):
            core.init_workspace(shared)
        self.assertEqual(stat.S_IMODE(shared.stat().st_mode), 0o755)
        self.assertEqual(list(shared.iterdir()), [])

    def test_io_failure_rolls_back_previously_replaced_files(self):
        before = {name: (self.workspace / name).read_bytes() for name in core.FILES}
        real_replace = core.os.replace
        calls = 0

        def interrupted_replace(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("synthetic disk failure")
            return real_replace(source, target)

        with patch.object(core.os, "replace", side_effect=interrupted_replace):
            with self.assertRaises(OSError):
                core.import_snapshot(self.workspace, {"account": account()})
        self.assertEqual(before, {name: (self.workspace / name).read_bytes() for name in core.FILES})
        self.assertFalse(any(p.name.startswith(".ledger.json.") for p in self.workspace.iterdir()))

    def test_invalid_numeric_and_duplicate_json_fields(self):
        for value in ("NaN", "Infinity", "-1", 10, True, "1e5", "1" * 81):
            with self.subTest(value=value), self.assertRaises(core.FinanceError):
                self.import_account(account(cash=value))
        source = Path(self.temp.name) / "duplicate.json"
        source.write_text('{"cash":"1","cash":"2"}')
        with self.assertRaises(core.FinanceError):
            core.load_json(source)


if __name__ == "__main__":
    unittest.main()
