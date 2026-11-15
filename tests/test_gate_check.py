from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_gate_module():
    spec = importlib.util.spec_from_file_location("gate_check", ROOT / "scripts/gate_check.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["gate_check"] = module
    spec.loader.exec_module(module)
    return module


def passing_package() -> dict:
    return {
        "schema_version": "1",
        "task_id": "T-1",
        "intent_revision": 1,
        "authorization_level": "L1",
        "dri": "alice",
        "reviewer": "bob",
        "commit": "abc123",
        "acceptance": [{"id": "AC1", "evidence": ["ci://run/1#ac1"], "status": "PASS"}],
        "steps": [
            {"id": "G0", "status": "PASS", "evidence": ["ci://run/1"]},
            {"id": "G1", "status": "PASS", "evidence": ["ci://run/1#e2e"]},
            {"id": "G2", "status": "N/A", "reason": "no UI change"},
            {"id": "G4", "status": "PASS", "evidence": ["review://bob/1"]},
            {"id": "CR", "status": "PASS", "evidence": ["pr://12#review"]},
        ],
    }


class GateCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = load_gate_module()

    def evaluate(self, pkg: dict) -> dict:
        self.assertEqual([], self.gate.validate_shape(pkg))
        return self.gate.evaluate(pkg)

    def test_complete_package_is_releasable(self) -> None:
        result = self.evaluate(passing_package())
        self.assertTrue(result["releasable"], result["problems"])

    def test_template_is_never_releasable(self) -> None:
        pkg = self.gate.template()
        pkg["task_id"], pkg["commit"] = "T-0", "abc"
        self.assertFalse(self.evaluate(pkg)["releasable"])

    def test_pass_without_evidence_is_blocked(self) -> None:
        pkg = passing_package()
        pkg["steps"][0]["evidence"] = []
        result = self.evaluate(pkg)
        self.assertEqual("BLOCKED", result["effective_status"]["G0"])
        self.assertFalse(result["releasable"])

    def test_missing_required_step_is_blocked(self) -> None:
        pkg = passing_package()
        pkg["steps"] = [s for s in pkg["steps"] if s["id"] != "CR"]
        result = self.evaluate(pkg)
        self.assertIn("CR: BLOCKED", result["blocking"])

    def test_g0_cannot_be_na(self) -> None:
        pkg = passing_package()
        pkg["steps"][0] = {"id": "G0", "status": "N/A", "reason": "trust me"}
        self.assertFalse(self.evaluate(pkg)["releasable"])

    def test_na_needs_reason(self) -> None:
        pkg = passing_package()
        pkg["steps"][2]["reason"] = ""
        pkg["steps"][2]["required"] = True
        result = self.evaluate(pkg)
        self.assertEqual("BLOCKED", result["effective_status"]["G2"])
        self.assertFalse(result["releasable"])

    def test_evidence_for_other_commit_is_blocked(self) -> None:
        pkg = passing_package()
        pkg["steps"][1]["commit"] = "old999"
        self.assertFalse(self.evaluate(pkg)["releasable"])

    def test_failed_acceptance_fails_g1(self) -> None:
        pkg = passing_package()
        pkg["acceptance"][0]["status"] = "FAIL"
        result = self.evaluate(pkg)
        self.assertEqual("FAIL", result["effective_status"]["G1"])
        self.assertFalse(result["releasable"])

    def test_reviewer_must_not_be_dri(self) -> None:
        pkg = passing_package()
        pkg["reviewer"] = "alice"
        self.assertFalse(self.evaluate(pkg)["releasable"])

    def test_l0_needs_no_reviewer_or_g4(self) -> None:
        pkg = passing_package()
        pkg["authorization_level"] = "L0"
        pkg["reviewer"] = ""
        pkg["steps"] = [s for s in pkg["steps"] if s["id"] != "G4"]
        self.assertTrue(self.evaluate(pkg)["releasable"])

    def test_l2_judgment_needs_named_approver(self) -> None:
        pkg = passing_package()
        pkg["authorization_level"] = "L2"
        self.assertFalse(self.evaluate(pkg)["releasable"])
        pkg["approvals"] = [{"step": "G4", "approver": "sponsor"}]
        self.assertTrue(self.evaluate(pkg)["releasable"])

    def test_l3_needs_sponsor_approval(self) -> None:
        pkg = passing_package()
        pkg["authorization_level"] = "L3"
        pkg["approvals"] = [{"step": "G4", "approver": "sponsor"}]
        self.assertFalse(self.evaluate(pkg)["releasable"])
        pkg["approvals"].append({"step": "L3", "approver": "sponsor"})
        self.assertTrue(self.evaluate(pkg)["releasable"])

    def test_complete_exception_waives_non_hard_gate(self) -> None:
        pkg = passing_package()
        pkg["steps"][4] = {"id": "CR", "status": "BLOCKED"}
        self.assertFalse(self.evaluate(pkg)["releasable"])
        pkg["exceptions"] = [
            {"step": "CR", "approver": "lead", "reason": "hotfix", "expires": "2026-12-01", "remediation": "post-merge review"}
        ]
        result = self.evaluate(pkg)
        self.assertTrue(result["releasable"], result["problems"])
        self.assertEqual(["CR"], result["waived_steps"])

    def test_g0_cannot_be_waived(self) -> None:
        pkg = passing_package()
        pkg["steps"][0] = {"id": "G0", "status": "FAIL", "evidence": ["ci://run/2"]}
        pkg["exceptions"] = [
            {"step": "G0", "approver": "lead", "reason": "x", "expires": "2026-12-01", "remediation": "y"}
        ]
        self.assertFalse(self.evaluate(pkg)["releasable"])

    def test_invalid_shape_is_reported(self) -> None:
        pkg = copy.deepcopy(passing_package())
        pkg["authorization_level"] = "L9"
        pkg["steps"].append({"id": "G0", "status": "PASS"})
        errors = self.gate.validate_shape(pkg)
        self.assertTrue(any("authorization_level" in e for e in errors))
        self.assertTrue(any("duplicate step G0" in e for e in errors))

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            good = Path(temp) / "good.json"
            good.write_text(json.dumps(passing_package()), encoding="utf-8")
            bad = Path(temp) / "bad.json"
            bad.write_text("{}", encoding="utf-8")
            self.assertEqual(0, self.gate.main(["check", str(good), "--json"]))
            self.assertEqual(2, self.gate.main(["check", str(bad), "--json"]))
            blocked = passing_package()
            blocked["steps"][0]["status"] = "BLOCKED"
            good.write_text(json.dumps(blocked), encoding="utf-8")
            self.assertEqual(1, self.gate.main(["check", str(good)]))


if __name__ == "__main__":
    unittest.main()
