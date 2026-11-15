from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("update_check", ROOT / "scripts/update_check.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["update_check"] = module
    spec.loader.exec_module(module)
    return module


class UpdateCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.uc = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.uc.CACHE_PATH = Path(self.temp.name) / "cache.json"
        self.ee = {"version": "0.14.0", "repository": "https://github.com/o/ee", "repo_path": "/r", "branch": "main", "dirty": False}
        self.evo = {"installed": True, "home": "/h", "version": "v0.5.5", "channel": "uat", "manifest_source": "https://x/uat.json"}
        patches = [
            mock.patch.object(self.uc, "local_ee", return_value=self.ee),
            mock.patch.object(self.uc, "local_evozeus", return_value=self.evo),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def fake_fetch(self, ee_version: str, evo_version: str):
        def fetch(url: str) -> dict:
            if url.endswith("plugin.json"):
                return {"version": ee_version}
            return {"product_version": evo_version}
        return mock.patch.object(self.uc, "fetch_json", side_effect=fetch)

    def test_version_compare(self) -> None:
        self.assertTrue(self.uc.is_newer("v0.5.10", "v0.5.9"))
        self.assertFalse(self.uc.is_newer("0.13.0", "0.14.0"))
        self.assertFalse(self.uc.is_newer(None, "0.14.0"))

    def test_raw_url(self) -> None:
        self.assertEqual(
            "https://raw.githubusercontent.com/HaodiFan/engineering-everything/main/.codex-plugin/plugin.json",
            self.uc.raw_url("https://github.com/HaodiFan/engineering-everything", "main", ".codex-plugin/plugin.json"),
        )

    def test_reports_both_updates(self) -> None:
        with self.fake_fetch("0.15.0", "v0.5.6"):
            report = self.uc.build_report(force=True)
        self.assertTrue(report["engineering_everything"]["update_available"])
        self.assertTrue(report["evozeus"]["update_available"])
        self.assertEqual(2, len(self.uc.summary_lines(report)))
        self.assertIn("pull --ff-only", report["engineering_everything"]["how_to_update"])

    def test_feature_branch_hint(self) -> None:
        self.ee["branch"] = "feat/x"
        with self.fake_fetch("0.15.0", "v0.5.5"):
            report = self.uc.build_report(force=True)
        self.assertIn("feat/x", report["engineering_everything"]["how_to_update"])
        self.assertFalse(report["evozeus"]["update_available"])

    def test_throttle_reuses_cache(self) -> None:
        with self.fake_fetch("0.14.0", "v0.5.5") as fetch:
            self.uc.build_report()
            self.uc.build_report()
        self.assertEqual(2, fetch.call_count)  # one round of two fetches

    def test_network_error_is_silent_in_hook(self) -> None:
        with mock.patch.object(self.uc, "fetch_json", side_effect=OSError("offline")), \
                mock.patch.object(sys, "stdin", io.StringIO('{"source":"startup"}')):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(0, self.uc.run_hook("claude"))
        self.assertEqual("", out.getvalue())

    def test_hook_emits_context_when_outdated(self) -> None:
        with self.fake_fetch("0.15.0", "v0.5.5"), mock.patch.object(sys, "stdin", io.StringIO("{}")):
            out = io.StringIO()
            with redirect_stdout(out):
                self.uc.run_hook("codex")
        payload = json.loads(out.getvalue())
        self.assertEqual("SessionStart", payload["hookSpecificOutput"]["hookEventName"])
        self.assertIn("0.15.0", payload["hookSpecificOutput"]["additionalContext"])

    def test_hook_can_be_disabled(self) -> None:
        with mock.patch.dict(os.environ, {"EE_UPDATE_CHECK": "0"}), mock.patch.object(self.uc, "build_report") as build:
            self.assertEqual(0, self.uc.run_hook("claude"))
        build.assert_not_called()

    def test_install_hook_is_idempotent_and_keeps_others(self) -> None:
        home = Path(self.temp.name)
        (home / ".claude").mkdir()
        settings = home / ".claude/settings.json"
        other = {"matcher": "startup", "hooks": [{"type": "command", "command": "other.py"}]}
        settings.write_text(json.dumps({"hooks": {"SessionStart": [other]}, "model": "x"}), encoding="utf-8")
        with mock.patch.object(Path, "home", return_value=home):
            self.uc.update_hook_config("claude", install=True, dry_run=False)
            self.uc.update_hook_config("claude", install=True, dry_run=False)
            data = json.loads(settings.read_text(encoding="utf-8"))
            self.assertEqual("x", data["model"])
            self.assertEqual(2, len(data["hooks"]["SessionStart"]))
            self.assertEqual(1, sum(self.uc.is_ours(e) for e in data["hooks"]["SessionStart"]))
            self.uc.update_hook_config("claude", install=False, dry_run=False)
            data = json.loads(settings.read_text(encoding="utf-8"))
            self.assertEqual([other], data["hooks"]["SessionStart"])
            self.assertIn("skip codex", self.uc.update_hook_config("codex", install=True, dry_run=False))


if __name__ == "__main__":
    unittest.main()
