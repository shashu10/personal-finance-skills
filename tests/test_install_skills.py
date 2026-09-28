import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("install_skills", ROOT / "scripts/install_skills.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallSkillsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        for name in installer.NAMES:
            p = self.source / name
            p.mkdir(parents=True)
            (p / "SKILL.md").write_text(name)

    def test_link_is_idempotent_and_edits_stay_visible(self):
        target = self.root / "target"
        self.assertEqual(len(installer.install(target, source=self.source)), len(installer.NAMES))
        self.assertEqual(installer.install(target, source=self.source), [])
        (self.source / installer.NAMES[0] / "SKILL.md").write_text("changed")
        self.assertEqual((target / installer.NAMES[0] / "SKILL.md").read_text(), "changed")

    def test_conflict_leaves_all_targets_unchanged(self):
        target = self.root / "target"
        (target / installer.NAMES[-1]).mkdir(parents=True)
        with self.assertRaises(ValueError):
            installer.install(target, source=self.source)
        self.assertEqual(len(list(target.iterdir())), 1)

    def test_copy_is_self_contained(self):
        target = self.root / "target"
        installer.install(target, mode="copy", source=self.source)
        self.assertFalse((target / installer.NAMES[0]).is_symlink())
        self.assertEqual((target / installer.NAMES[0] / "SKILL.md").read_text(), installer.NAMES[0])

    def test_broken_link_is_not_overwritten(self):
        target = self.root / "target"
        target.mkdir()
        (target / installer.NAMES[-1]).symlink_to(self.root / "missing")
        with self.assertRaises(ValueError):
            installer.install(target, source=self.source)
        self.assertTrue((target / installer.NAMES[-1]).is_symlink())

    def test_existing_six_links_gain_dashboard_without_replacement(self):
        target = self.root / "target"
        target.mkdir()
        previous = (
            "finance-setup", "finance-gather", "investment-research",
            "portfolio-review", "finance-plan", "finance-memory",
        )
        for name in previous:
            (target / name).symlink_to(self.source / name, target_is_directory=True)
        original_links = {name: (target / name).lstat().st_ino for name in previous}

        self.assertEqual(installer.install(target, source=self.source),
                         [str(target.resolve() / "finance-dashboard")])
        self.assertEqual({name: (target / name).lstat().st_ino for name in previous}, original_links)
        self.assertEqual(installer.install(target, source=self.source), [])
        self.assertEqual({p.name for p in target.iterdir()}, set(installer.NAMES))


if __name__ == "__main__":
    unittest.main()
