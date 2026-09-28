import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_public", ROOT / "scripts/check_public.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class PublicBoundaryTests(unittest.TestCase):
    def test_private_paths_and_symlinks_are_flagged(self):
        self.assertTrue(check.inspect("config/ledger.json", "100644", b"{}"))
        self.assertTrue(check.inspect("docs/statement.pdf", "100644", b"data"))
        self.assertTrue(check.inspect("skills/example/SKILL.md", "120000", b"../private"))

    def test_values_are_detected_without_echoing_them(self):
        private_value = "account-" + "private-example"
        problems = check.inspect("README.md", "100644", private_value.encode(), (private_value,))
        self.assertEqual(problems, ["private denylist match"])
        self.assertNotIn(private_value, str(problems))

    def test_public_text_is_accepted(self):
        self.assertEqual(check.inspect("examples/account.json", "100644", b'{"id":"demo-broker"}'), [])

    def test_private_key_and_binary_are_flagged(self):
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        self.assertIn("private key material", check.inspect("README.md", "100644", marker.encode()))
        self.assertIn("binary content", check.inspect("README.md", "100644", b"a\x00b"))


if __name__ == "__main__":
    unittest.main()
