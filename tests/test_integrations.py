"""Offline boundary and handoff tests. No broker, model, or installer network calls."""

from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_script("install_optional")
runner = load_script("run_tradingagents")


class IntegrationInstallerTests(unittest.TestCase):
    def test_dry_run_uses_pinned_revision_and_per_environment_interpreter_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "optional"
            with patch.object(installer.sys, "version_info", (3, 12)), patch.object(installer.subprocess, "run") as run:
                plan = installer.build_plan("tradingagents", target)
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(installer.main(["--tool", "tradingagents", "--venv", str(target), "--dry-run"]), 0)
            run.assert_not_called()
            self.assertFalse(target.exists())
            self.assertEqual(plan["commands"][1][0], str(installer.environment_python(target.resolve())))
            self.assertIn("@" + installer.manifest()["tools"]["tradingagents"]["revision"], plan["commands"][1][-1])
            self.assertEqual(plan["commands"][2][-2:], ["pip", "check"])

    def test_public_checkout_and_symlink_destinations_refused(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            installer.external_path(ROOT / "private-looking-env")
        with tempfile.TemporaryDirectory() as temporary:
            link = Path(temporary) / "alias"
            link.symlink_to(ROOT, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "outside"):
                installer.external_path(link / "new-env")

    def test_existing_unmanaged_directory_and_wrong_tool_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            with self.assertRaisesRegex(ValueError, "not a managed"):
                installer.validate_target(target, "tradingagents")
            (target / installer.MARKER).write_text(json.dumps({"managed_by": "personal-finance-skills", "tool": "vibe-trading"}))
            with self.assertRaisesRegex(ValueError, "own managed"):
                installer.validate_target(target, "tradingagents")

    def test_install_checks_pip_and_revision_before_ready_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "managed"
            with patch.object(installer.sys, "version_info", (3, 12)):
                plan = installer.build_plan("tradingagents", target)
            calls = []

            def fake_run(command, **kwargs):
                calls.append((command, kwargs))
                self.assertNotIn("shell", kwargs)
                if command[1:3] == ["-m", "venv"]:
                    target.mkdir()
                return subprocess.CompletedProcess(command, 0, json.dumps({"version": "test", "revision": plan["revision"]}))

            with patch.object(installer.subprocess, "run", side_effect=fake_run):
                installer.install(plan)
            receipt = json.loads((target / installer.MARKER).read_text())
            self.assertEqual(receipt["status"], "ready")
            self.assertEqual(calls[2][0][-2:], ["pip", "check"])
            self.assertIn("direct_url.json", calls[-1][0][-1])

    def test_bad_installed_revision_does_not_mark_ready(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "managed"
            with patch.object(installer.sys, "version_info", (3, 12)):
                plan = installer.build_plan("vibe-trading", target)

            def fake_run(command, **kwargs):
                if command[1:3] == ["-m", "venv"]:
                    target.mkdir()
                return subprocess.CompletedProcess(command, 0, '{"version":"test","revision":"wrong"}')

            with patch.object(installer.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(ValueError, "differs"):
                    installer.install(plan)
            self.assertNotEqual(json.loads((target / installer.MARKER).read_text())["status"], "ready")


class TradingAgentsRunnerTests(unittest.TestCase):
    def test_real_core_dry_run_requires_both_permissions_then_exports_only_portfolio(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "synthetic-private"
            init = subprocess.run(
                [sys.executable, "-m", "finance_core", "init", "--workspace", str(workspace), "--demo"],
                capture_output=True, text=True, env=environment,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            command = [sys.executable, str(ROOT / "scripts/run_tradingagents.py"),
                       "--workspace", str(workspace), "--ticker", "EXAMPLE", "--dry-run"]
            disabled = subprocess.run(command, capture_output=True, text=True, env=environment)
            self.assertNotEqual(disabled.returncode, 0)
            rules_path = workspace / "rules.json"
            rules = json.loads(rules_path.read_text())
            rules["sharing"]["relative_context"] = True
            rules_path.write_text(json.dumps(rules))
            relative_only = subprocess.run(command, capture_output=True, text=True, env=environment)
            self.assertNotEqual(relative_only.returncode, 0)
            self.assertIn("tradingagents_amounts", relative_only.stderr)
            rules["sharing"]["tradingagents_amounts"] = True
            rules_path.write_text(json.dumps(rules))
            before = {p.name: p.read_bytes() for p in workspace.iterdir() if p.is_file()}
            enabled = subprocess.run(command, capture_output=True, text=True, env=environment)
            self.assertEqual(enabled.returncode, 0, enabled.stderr)
            payload = json.loads(enabled.stdout)
            self.assertLessEqual(set(payload), {"cash", "currency", "positions"})
            self.assertIsNone(payload["cash"])
            self.assertEqual(payload["currency"], "USD")
            self.assertEqual(payload["positions"][0]["ticker"], "EXAMPLE")
            self.assertEqual(float(payload["positions"][0]["quantity"]), 20)
            self.assertNotIn("sample-brokerage", enabled.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in workspace.iterdir() if p.is_file()})
            self.assertFalse((workspace / "research").exists())

    def test_core_rejection_prevents_dry_run_and_model_execution(self):
        result = subprocess.CompletedProcess([], 2, "", "sharing.tradingagents_amounts must be true")
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(runner.subprocess, "run", return_value=result), patch.object(runner, "execute") as execute:
                with redirect_stderr(io.StringIO()) as errors:
                    status = runner.main(["--workspace", temporary, "--ticker", "AAPL", "--dry-run"])
            self.assertEqual(status, 2)
            self.assertIn("sharing.tradingagents_amounts", errors.getvalue())
            execute.assert_not_called()
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_dry_run_prints_exact_core_payload_and_no_files(self):
        payload = {"cash": None, "currency": "USD", "positions": [{"ticker": "AAPL", "quantity": 2}]}
        result = subprocess.CompletedProcess([], 0, json.dumps(payload), "")
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(runner.subprocess, "run", return_value=result) as run, patch.object(runner, "execute") as execute:
                with redirect_stdout(io.StringIO()) as output:
                    status = runner.main(["--workspace", temporary, "--ticker", "AAPL", "--dry-run"])
            self.assertEqual(status, 0)
            self.assertEqual(json.loads(output.getvalue()), payload)
            execute.assert_not_called()
            self.assertEqual(run.call_args.args[0][0], sys.executable)
            self.assertNotIn("--as-of", run.call_args.args[0])
            self.assertEqual(run.call_args.kwargs["env"]["PYTHONPATH"], str(ROOT / "src"))
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_extra_context_fields_fail_closed(self):
        result = subprocess.CompletedProcess([], 0, '{"positions":[],"profile":{"name":"Synthetic"}}', "")
        with tempfile.TemporaryDirectory() as temporary, patch.object(runner.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "unexpected context"):
                runner.read_context(Path(temporary), "AAPL")

    def test_explicit_provider_and_both_models_required(self):
        args = types.SimpleNamespace(provider=None, deep_model=None, quick_model=None)
        with patch.dict(runner.os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "no model defaults"):
                runner.explicit_models(args)
        args.provider, args.deep_model, args.quick_model = "synthetic", "model-a", "model-b"
        self.assertEqual(runner.explicit_models(args)["quick_think_llm"], "model-b")

    def test_output_symlink_to_checkout_refused_before_context_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "research").symlink_to(ROOT, target_is_directory=True)
            with patch.object(runner, "read_context") as read, redirect_stderr(io.StringIO()):
                self.assertEqual(runner.main(["--workspace", temporary, "--ticker", "AAPL", "--dry-run"]), 2)
            read.assert_not_called()

    def test_historical_date_does_not_misrepresent_current_holdings(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(runner, "read_context") as read, redirect_stderr(io.StringIO()) as errors:
                status = runner.main(["--workspace", temporary, "--ticker", "AAPL", "--date", "2000-01-01", "--dry-run"])
            self.assertEqual(status, 2)
            self.assertIn("Historical portfolio runs", errors.getvalue())
            read.assert_not_called()

    def test_analysis_date_matches_upstream_local_calendar_on_both_sides_of_utc(self):
        payload = {"cash": None, "currency": "USD", "positions": []}
        cases = (
            (date(2026, 1, 1), datetime(2026, 1, 2, 0, 15, tzinfo=timezone.utc)),
            (date(2026, 1, 2), datetime(2026, 1, 1, 23, 45, tzinfo=timezone.utc)),
        )
        for local_day, utc_instant in cases:
            class LocalDate(date):
                @classmethod
                def today(cls):
                    return local_day

            with self.subTest(local=local_day, utc=utc_instant.date()), tempfile.TemporaryDirectory() as temporary:
                with patch.object(runner, "date", LocalDate), patch.object(runner, "datetime") as clock, \
                        patch.object(runner, "read_context", return_value=payload) as read, \
                        patch.object(runner, "execute") as execute, \
                        redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    clock.now.return_value = utc_instant
                    arguments = ["--workspace", temporary, "--ticker", "AAPL", "--provider", "synthetic",
                                 "--deep-model", "test-deep", "--quick-model", "test-quick"]
                    for explicit_date in ([], ["--date", local_day.isoformat()]):
                        self.assertEqual(runner.main(arguments + explicit_date), 0)
                        self.assertEqual(execute.call_args.args[4], local_day.isoformat())
                        self.assertTrue(execute.call_args.args[2].name.startswith("AAPL-" + utc_instant.strftime("%Y%m%dT")))
                    read.reset_mock()
                    execute.reset_mock()
                    self.assertEqual(runner.main(arguments + ["--date", utc_instant.date().isoformat()]), 2)
                    read.assert_not_called()
                    execute.assert_not_called()

    def test_supported_api_receives_validated_payload_and_private_paths(self):
        payload = {"currency": "USD", "positions": [{"ticker": "AAPL", "quantity": 2}]}
        validated = object()
        seen = {}

        class PortfolioContext:
            @staticmethod
            def model_validate(value):
                seen["payload"] = value
                return validated

        class Graph:
            def __init__(self, *, debug, config):
                seen["config"] = config

            def propagate(self, ticker, day, *, portfolio):
                seen["portfolio"] = portfolio
                return {"report": "synthetic"}, "REVIEW"

            def save_reports(self, state, ticker, *, save_path):
                seen["reports"] = save_path

        modules = {
            "tradingagents": types.ModuleType("tradingagents"),
            "tradingagents.portfolio": types.SimpleNamespace(PortfolioContext=PortfolioContext),
            "tradingagents.default_config": types.SimpleNamespace(DEFAULT_CONFIG={}),
            "tradingagents.graph": types.ModuleType("tradingagents.graph"),
            "tradingagents.graph.trading_graph": types.SimpleNamespace(TradingAgentsGraph=Graph),
        }
        with tempfile.TemporaryDirectory() as temporary:
            workspace, output = Path(temporary), Path(temporary) / "run"
            with patch.dict(sys.modules, modules), patch.object(runner, "verify_environment", return_value="synthetic-revision"):
                receipt = runner.execute(payload, workspace, output, "AAPL", date.today().isoformat(), {"llm_provider": "synthetic"})
            self.assertIs(seen["portfolio"], validated)
            self.assertEqual(seen["payload"], payload)
            self.assertEqual(seen["config"]["results_dir"], str(output / "logs"))
            self.assertEqual(seen["reports"], output / "reports")
            self.assertEqual(receipt["signal"], "REVIEW")
            self.assertTrue((output / "run.json").is_file())
            if os.name != "nt":
                self.assertEqual(output.stat().st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
