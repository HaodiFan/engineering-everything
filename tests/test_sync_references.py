from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_references", ROOT / "scripts/sync_references.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_references"] = module
    spec.loader.exec_module(module)
    return module


def write_valid_fixture(root: Path) -> None:
    (root / "data").mkdir()
    (root / "references").mkdir()
    (root / "skills/example/references").mkdir(parents=True)
    (root / "references/foo.md").write_text("same\n", encoding="utf-8")
    (root / "skills/example/references/foo.md").write_text("same\n", encoding="utf-8")
    (root / "data/routes.yaml").write_text("routes:\n", encoding="utf-8")
    (root / "data/reference_distribution.yaml").write_text(
        """canonical_root: references
entries:
  - source: foo.md
    mode: exact-copy
    targets:
      - example
""",
        encoding="utf-8",
    )


class SyncReferencesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sync = load_sync_module()

    def test_valid_distribution_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_valid_fixture(root)

            self.assertEqual([], self.sync.check_distribution(root))

    def test_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_valid_fixture(root)
            (root / "skills/example/references/foo.md").write_text("changed\n", encoding="utf-8")

            errors = self.sync.check_distribution(root)

            self.assertTrue(any("reference drift" in error for error in errors))

    def test_undeclared_runtime_copy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_valid_fixture(root)
            (root / "skills/example/references/extra.md").write_text("extra\n", encoding="utf-8")

            errors = self.sync.check_distribution(root)

            self.assertTrue(any("undeclared runtime reference copy" in error for error in errors))

    def test_required_reference_must_ship_with_dependent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_valid_fixture(root)
            (root / "references/rules.md").write_text("rules\n", encoding="utf-8")
            manifest = """canonical_root: references
entries:
  - source: foo.md
    mode: exact-copy
    requires:
      - rules.md
    targets:
      - example
  - source: rules.md
    mode: exact-copy
    targets: []
"""
            (root / "data/reference_distribution.yaml").write_text(manifest.replace("    targets: []\n", "    status: canonical\n    targets: []\n"), encoding="utf-8")
            errors = self.sync.check_distribution(root)
            self.assertTrue(any("requires rules.md, but skill example does not ship it" in e for e in errors), errors)

            (root / "data/reference_distribution.yaml").write_text(manifest.replace("    targets: []\n", "    targets:\n      - example\n"), encoding="utf-8")
            (root / "skills/example/references/rules.md").write_text("rules\n", encoding="utf-8")
            self.assertEqual([], self.sync.check_distribution(root))

    def test_review_skill_ships_smell_catalog(self) -> None:
        self.assertTrue((ROOT / "skills/engineering-review-release/references/refactoring-rules.md").exists())
        self.assertEqual([], self.sync.check_distribution(ROOT))


if __name__ == "__main__":
    unittest.main()
