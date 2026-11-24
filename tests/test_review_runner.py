from __future__ import annotations

import concurrent.futures
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    spec = importlib.util.spec_from_file_location("review_runner", ROOT / "scripts/review_runner.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["review_runner"] = module
    spec.loader.exec_module(module)
    return module


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def make_sample_repo(base_dir: Path, *, with_react_ui: bool = True, with_auth: bool = True, with_dx: bool = False) -> Path:
    repo = base_dir / "sample_repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "dev@example.com")
    git(repo, "config", "user.name", "Dev")

    if with_react_ui:
        (repo / "package.json").write_text(
            json.dumps({"name": "demo", "dependencies": {"react": "^19.0.0", "next": "^15.0.0"}}),
            encoding="utf-8",
        )
    (repo / "app.py").write_text("def hello():\n    return 'v1'\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")

    git(repo, "checkout", "-b", "feat/review-demo")
    (repo / "app.py").write_text("def hello():\n    return 'v2'\n", encoding="utf-8")
    if with_react_ui:
        ui_dir = repo / "src" / "components"
        ui_dir.mkdir(parents=True, exist_ok=True)
        (ui_dir / "ApprovalForm.tsx").write_text(
            "export function ApprovalForm() { return <form><button>Submit</button></form>; }\n",
            encoding="utf-8",
        )
    if with_auth:
        (repo / "auth_policy.py").write_text(
            "def can_approve(role: str) -> bool:\n    return role == 'admin'\n",
            encoding="utf-8",
        )
    if with_dx:
        (repo / "README.md").write_text("# Demo CLI\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "feat: add changes")
    return repo


def pass_checks(rule_ids: list[str], note: str = "verified") -> list[dict[str, str]]:
    return [{"id": rid, "status": "PASS", "note": note} for rid in rule_ids]


class ReviewRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_runner()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp_path = Path(self.temp.name)

    def run_cli(self, argv: list[str], stdin_data: str | None = None) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        old_stdin = sys.stdin
        if stdin_data is not None:
            sys.stdin = io.StringIO(stdin_data)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = self.runner.main(argv)
        finally:
            sys.stdin = old_stdin
        return code, out.getvalue(), err.getvalue()

    def submit_json(self, run_dir: Path, lane: str, payload: dict) -> tuple[int, dict]:
        code, out, err = self.run_cli(
            ["submit", "--run", str(run_dir), "--lane", lane, "--input", "-", "--json"],
            stdin_data=json.dumps(payload, ensure_ascii=False),
        )
        return code, (json.loads(out) if out.strip() else {"err": err})

    def test_catalog_matches_review_rules_doc_one_to_one(self) -> None:
        code, out, _ = self.run_cli(["catalog", "--json"])
        self.assertEqual(0, code)
        cat = json.loads(out)
        self.assertEqual(6, cat["total_lanes"])
        self.assertEqual(48, cat["total_rules"])
        self.assertEqual(
            [
                "engineering_baseline",
                "business_acceptance",
                "code_quality",
                "security_architecture",
                "ui_ux_experience",
                "release_readiness",
            ],
            [l["id"] for l in cat["lanes"]],
        )
        json_ids = [r["id"] for l in cat["lanes"] for r in l["rules"]]
        self.assertEqual(len(json_ids), len(set(json_ids)))

        doc_text = (ROOT / "references/review-rules.md").read_text(encoding="utf-8")
        doc_ids = sorted(set(re.findall(r"\*\*`(RV-[A-Z]+-\d{2})`", doc_text)))
        self.assertEqual(sorted(json_ids), doc_ids)

    def test_per_rule_signal_activation_avoids_noise(self) -> None:
        # Pure non-auth Python PR with README DX change:
        # - code_quality has NO RV-REACT-*, only RV-BUG-01..05, RV-TEST-01, RV-SMELL-01..10 (16 rules)
        # - security_architecture activates RV-SEC-01, RV-SEC-03, RV-SEC-04, RV-DX-01
        repo = make_sample_repo(self.tmp_path, with_react_ui=False, with_auth=False, with_dx=True)
        state_dir = self.tmp_path / "signal_state"
        code, out, _ = self.run_cli([
            "init", "--target", str(repo), "--base", "main",
            "--mode", "pr", "--level", "L1", "--state-dir", str(state_dir), "--json",
        ])
        self.assertEqual(0, code, out)
        res = json.loads(out)
        self.assertNotIn("ui_ux_experience", res["required_lanes"])
        self.assertEqual(
            ["RV-SEC-01", "RV-SEC-03", "RV-SEC-04", "RV-DX-01"],
            res["active_rule_ids"]["security_architecture"],
        )
        cq_rules = res["active_rule_ids"]["code_quality"]
        self.assertEqual(16, len(cq_rules))
        self.assertNotIn("RV-REACT-01", cq_rules)
        self.assertIn("RV-BUG-01", cq_rules)
        self.assertIn("RV-SMELL-01", cq_rules)
        self.assertIn("RV-SMELL-10", cq_rules)

    def test_full_react_ui_delivery_pipeline_concurrent_html_and_recheck(self) -> None:
        repo = make_sample_repo(self.tmp_path, with_react_ui=True, with_auth=True)
        state_dir = self.tmp_path / "run_state"

        # 1. Init with L0 + auth -> bumped to L1, all 6 clustered dimensions active
        code, out, _ = self.run_cli([
            "init", "--target", str(repo), "--base", "main",
            "--mode", "delivery", "--level", "L0",
            "--dri", "alice", "--reviewer", "bob",
            "--state-dir", str(state_dir), "--json",
        ])
        self.assertEqual(0, code, out)
        init_res = json.loads(out)
        self.assertEqual("L1", init_res["level"])
        self.assertEqual(
            {
                "engineering_baseline",
                "business_acceptance",
                "code_quality",
                "security_architecture",
                "ui_ux_experience",
                "release_readiness",
            },
            set(init_res["required_lanes"]),
        )
        self.assertEqual("", git(repo, "status", "--short"))

        # 2. Phase 1 next -> unlocks engineering_baseline
        code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
        self.assertEqual(0, code)
        p1 = json.loads(out)
        p1_map = {item["lane_id"]: item for item in p1["ready_lanes"]}
        self.assertEqual({"engineering_baseline"}, set(p1_map))

        self.assertEqual(0, self.submit_json(state_dir, "engineering_baseline", {
            "prompt_token": p1_map["engineering_baseline"]["prompt_token"],
            "status": "PASS",
            "summary": "build & tests green",
            "checks": pass_checks(p1_map["engineering_baseline"]["active_rule_ids"], "ran cmd ok"),
            "evidence": ["pytest: 5 passed", "git diff --check: exit 0"],
            "commands_run": ["git diff --check", "pytest"],
        })[0])

        # Mid-run `render` command produces a live IN_PROGRESS HTML report
        live_html_path = self.tmp_path / "live_report.html"
        code, out, _ = self.run_cli(["render", "--run", str(state_dir), "--out", str(live_html_path), "--json"])
        self.assertEqual(0, code, out)
        self.assertTrue(live_html_path.is_file())
        live_html = live_html_path.read_text(encoding="utf-8")
        self.assertIn("质检进行中", live_html)
        self.assertIn("engineering_baseline", live_html)

        # 3. Phase 2 next -> unlocks all 4 parallel clustered dimensions!
        code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
        self.assertEqual(0, code)
        p2 = json.loads(out)
        self.assertTrue(p2["can_run_concurrently"])
        p2_map = {item["lane_id"]: item for item in p2["ready_lanes"]}
        self.assertEqual(
            {"business_acceptance", "code_quality", "security_architecture", "ui_ux_experience"},
            set(p2_map),
        )
        # Verify React Doctor + 10 itemized smells appear in code_quality prompt, Bombadil + UX appear in ui_ux_experience
        cq_prompt = Path(p2_map["code_quality"]["prompt_path"]).read_text(encoding="utf-8")
        self.assertIn("RV-REACT-01", cq_prompt)
        self.assertIn("RV-SMELL-01", cq_prompt)
        self.assertIn("RV-SMELL-10", cq_prompt)
        ui_prompt = Path(p2_map["ui_ux_experience"]["prompt_path"]).read_text(encoding="utf-8")
        self.assertIn("RV-BOMB-01", ui_prompt)
        self.assertIn("RV-UI-02", ui_prompt)

        # Submit all 4 Phase 2 dimensions concurrently, with ONE blocking FAIL (including HTML chars for XSS escaping test)
        bug_checks = pass_checks(p2_map["code_quality"]["active_rule_ids"], "checked")
        for c in bug_checks:
            if c["id"] == "RV-BUG-01":
                c["status"] = "FAIL"
                c["note"] = "empty payload crashes app.py:2"

        p2_payloads = {
            "business_acceptance": {
                "prompt_token": p2_map["business_acceptance"]["prompt_token"],
                "status": "PASS",
                "summary": "business acceptance verified",
                "checks": pass_checks(p2_map["business_acceptance"]["active_rule_ids"], "checked"),
                "evidence": ["pytest#ac1 passed"],
                "meta": {"acceptance": [{"id": "AC1", "expected": "ok", "actual": "ok", "evidence": ["pytest#ac1"], "status": "PASS"}]},
            },
            "code_quality": {
                "prompt_token": p2_map["code_quality"]["prompt_token"],
                "status": "FAIL",
                "summary": "P1 boundary bug in app.py",
                "checks": bug_checks,
                "evidence": ["app.py:2 inspection", "react-doctor.json: 0 new issues"],
                "commands_run": ["npx --yes react-doctor@latest . --yes --scope changed --base main --no-telemetry --no-supply-chain --json"],
                "meta": {"scope": "changed", "no_telemetry": True, "no_supply_chain": True, "skipped_files": []},
                "findings": [
                    {
                        "rule_id": "RV-BUG-01",
                        "severity": "P1",
                        "location": "app.py:2",
                        "problem": "Missing validation on <script>alert(1)</script> empty payload",
                        "impact": "500 error on approval submit",
                        "fix": "Validate payload before access",
                        "verification": "Add negative unit test",
                    },
                    {
                        "rule_id": "RV-SMELL-01",
                        "severity": "P2",
                        "location": "app.py:1",
                        "problem": "Helper function mixes parsing and formatting",
                        "impact": "Harder to maintain",
                        "fix": "Split into parse_input and format_response",
                        "verification": "Unit tests still pass",
                    },
                ],
            },
            "security_architecture": {
                "prompt_token": p2_map["security_architecture"]["prompt_token"],
                "status": "PASS",
                "summary": "auth & arch verified",
                "checks": pass_checks(p2_map["security_architecture"]["active_rule_ids"], "checked"),
                "evidence": ["auth_policy.py inspected"],
            },
            "ui_ux_experience": {
                "prompt_token": p2_map["ui_ux_experience"]["prompt_token"],
                "status": "PASS",
                "summary": "1m Bombadil exploration & UI/UX audit passed",
                "checks": pass_checks(p2_map["ui_ux_experience"]["active_rule_ids"], "verified"),
                "evidence": ["./output/bombadil/r1/trace.json", "ApprovalForm live walkthrough"],
                "commands_run": ["bombadil browser test --headless --time-limit 1m --exit-on-violation --output-path ./output/bombadil/r1 http://127.0.0.1:3000 ./bombadil/review.spec.ts"],
                "meta": {
                    "applicability": "applicable",
                    "execution_state": "completed_no_violation",
                    "command": "bombadil browser test --headless --time-limit 1m ...",
                    "budget": "1m",
                    "output_path": "./output/bombadil/r1",
                    "exit_code": 0,
                    "material_type": "runnable",
                    "unfamiliar_language_check": "PASS",
                },
            },
        }

        def _submit_worker(item: tuple[str, dict]) -> tuple[str, int, str]:
            lid, pl = item
            tmp_file = self.tmp_path / f"{lid}.json"
            tmp_file.write_text(json.dumps(pl), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/review_runner.py"), "submit",
                 "--run", str(state_dir), "--lane", lid, "--input", str(tmp_file), "--json"],
                capture_output=True, text=True, check=False,
            )
            return lid, proc.returncode, proc.stdout + proc.stderr

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            worker_results = list(pool.map(_submit_worker, p2_payloads.items()))
        for lid, rc, msg in worker_results:
            self.assertEqual(0, rc, f"{lid} failed: {msg}")

        # 4. Early stop on P1 -> NOT_READY, release_readiness listed as unrun, report.html generated & XSS-safe
        code, out, _ = self.run_cli([
            "finalize", "--run", str(state_dir),
            "--early-stop", "--reason", "P1 RV-BUG-01 blocks release", "--json",
        ])
        self.assertEqual(1, code)
        fin1 = json.loads(out)
        self.assertEqual("NOT_READY", fin1["verdict"])
        self.assertEqual(["release_readiness"], fin1["missing_lanes"])
        self.assertIn("[P1][RV-BUG-01]", fin1["report"])
        html_path1 = Path(fin1["report_html_path"])
        self.assertTrue(html_path1.is_file())
        html1 = html_path1.read_text(encoding="utf-8")
        self.assertIn("还不能交付", html1)
        self.assertIn("RV-BUG-01", html1)
        self.assertIn("RV-SMELL-01", html1)
        self.assertIn("Validate payload before access", html1)
        self.assertNotIn("<script>alert(1)</script>", html1)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html1)

        # 5. Fix app.py -> recheck Round 2 carries forward untouched ui_ux_experience and injects RV-BUG-01!
        (repo / "app.py").write_text("def hello(name: str = 'world'):\n    return f'v3-{name}'\n", encoding="utf-8")
        git(repo, "add", "app.py")
        git(repo, "commit", "-m", "fix: validate payload in app.py")

        code, out, _ = self.run_cli(["recheck", "--run", str(state_dir), "--json"])
        self.assertEqual(0, code)
        r2 = json.loads(out)
        self.assertEqual(2, r2["round"])
        self.assertIn("ui_ux_experience", r2["carried_forward_lanes"])
        self.assertIn("code_quality", r2["reopened_lanes"])
        self.assertIn("release_readiness", r2["reopened_lanes"])

        # Walk Round 2 to READY
        for _ in range(4):
            code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
            self.assertEqual(0, code)
            step = json.loads(out)
            if step["action"] == "finalize":
                break
            for item in step["ready_lanes"]:
                lid = item["lane_id"]
                if lid == "code_quality":
                    self.assertIn("RV-BUG-01", Path(item["prompt_path"]).read_text(encoding="utf-8"))
                pl = {
                    "prompt_token": item["prompt_token"],
                    "status": "PASS",
                    "summary": f"{lid} round 2 ok",
                    "checks": pass_checks(item["active_rule_ids"], "re-verified"),
                    "evidence": [f"{lid} r2 evidence"],
                    "commands_run": ["pytest"],
                }
                if lid == "business_acceptance":
                    pl["meta"] = {"acceptance": [{"id": "AC1", "expected": "ok", "actual": "ok", "evidence": ["pytest#ac1"], "status": "PASS"}]}
                if lid == "code_quality":
                    pl["meta"] = {"scope": "changed", "no_telemetry": True, "no_supply_chain": True, "skipped_files": []}
                if lid == "release_readiness":
                    pl["meta"] = {"rollout": "canary", "rollback": "git revert", "monitoring": "error rate"}
                self.assertEqual(0, self.submit_json(state_dir, lid, pl)[0], lid)

        code, out, _ = self.run_cli(["finalize", "--run", str(state_dir), "--json"])
        self.assertEqual(0, code, out)
        fin2 = json.loads(out)
        self.assertEqual("READY", fin2["verdict"])
        self.assertTrue(fin2["gate_check"]["releasable"])
        self.assertIn("RV-SMELL-01", fin2["report"])
        html2 = Path(fin2["report_html_path"]).read_text(encoding="utf-8")
        self.assertIn("可以交付", html2)
        self.assertIn("过程日志", html2)

    def test_itemized_validation_guards_reject_missing_or_inconsistent_rules(self) -> None:
        repo = make_sample_repo(self.tmp_path, with_react_ui=True, with_auth=False)
        state_dir = self.tmp_path / "guard_state"
        self.assertEqual(0, self.run_cli([
            "init", "--target", str(repo), "--base", "main",
            "--mode", "pr", "--level", "L1", "--state-dir", str(state_dir), "--json",
        ])[0])
        code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
        p1_map = {i["lane_id"]: i for i in json.loads(out)["ready_lanes"]}

        # 1. Missing rule IDs in checks[] is REJECTED
        code, res = self.submit_json(state_dir, "engineering_baseline", {
            "prompt_token": p1_map["engineering_baseline"]["prompt_token"],
            "status": "PASS",
            "summary": "partial",
            "checks": [{"id": "RV-BASE-01", "status": "PASS", "note": "ok"}],
            "evidence": ["git diff --check"],
        })
        self.assertEqual(2, code)
        self.assertTrue(any("missing required rule checks" in e for e in res["errors"]))

        # 2. Marking never-NA rule RV-BASE-01 as N/A is REJECTED
        bad_na = pass_checks(p1_map["engineering_baseline"]["active_rule_ids"], "ok")
        bad_na[0] = {"id": "RV-BASE-01", "status": "N/A", "note": "skip"}
        code, res = self.submit_json(state_dir, "engineering_baseline", {
            "prompt_token": p1_map["engineering_baseline"]["prompt_token"],
            "status": "PASS",
            "summary": "tried skipping RV-BASE-01",
            "checks": bad_na,
            "evidence": ["pytest"],
        })
        self.assertEqual(2, code)
        self.assertTrue(any("RV-BASE-01 does not allow N/A" in e for e in res["errors"]))

        # 3. checks[] has FAIL while lane status is PASS is REJECTED
        bad_cons = pass_checks(p1_map["engineering_baseline"]["active_rule_ids"], "ok")
        bad_cons[2] = {"id": "RV-BASE-03", "status": "FAIL", "note": "lint failed"}
        code, res = self.submit_json(state_dir, "engineering_baseline", {
            "prompt_token": p1_map["engineering_baseline"]["prompt_token"],
            "status": "PASS",
            "summary": "mostly ok",
            "checks": bad_cons,
            "evidence": ["lint output"],
        })
        self.assertEqual(2, code)
        self.assertTrue(any("lane status must be FAIL" in e for e in res["errors"]))

        # 4. Finding without valid rule_id is REJECTED
        code, res = self.submit_json(state_dir, "engineering_baseline", {
            "prompt_token": p1_map["engineering_baseline"]["prompt_token"],
            "status": "FAIL",
            "summary": "lint failed",
            "checks": bad_cons,
            "evidence": ["lint output"],
            "findings": [{"severity": "P1", "location": "a.py:1", "problem": "bad", "impact": "fail", "fix": "fix"}],
        })
        self.assertEqual(2, code)
        self.assertTrue(any("rule_id must be a valid" in e for e in res["errors"]))

        # Pass Phase 1 to unlock Phase 2 and test React Doctor + Bombadil guards inside clustered dimensions
        self.assertEqual(0, self.submit_json(state_dir, "engineering_baseline", {
            "prompt_token": p1_map["engineering_baseline"]["prompt_token"],
            "status": "PASS",
            "summary": "baseline ok",
            "checks": pass_checks(p1_map["engineering_baseline"]["active_rule_ids"], "ok"),
            "evidence": ["pytest"],
        })[0])
        code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
        p2_map = {i["lane_id"]: i for i in json.loads(out)["ready_lanes"]}

        # 5. Bombadil tool missing marked as N/A inside ui_ux_experience is REJECTED
        ui_checks_bad = []
        for r in p2_map["ui_ux_experience"]["active_rule_ids"]:
            if r.startswith("RV-BOMB-"):
                ui_checks_bad.append({"id": r, "status": "N/A", "note": "bombadil CLI missing and offline"})
            else:
                ui_checks_bad.append({"id": r, "status": "PASS", "note": "ui checked"})
        code, res = self.submit_json(state_dir, "ui_ux_experience", {
            "prompt_token": p2_map["ui_ux_experience"]["prompt_token"],
            "status": "PASS",
            "summary": "ui ok, skipped bombadil",
            "checks": ui_checks_bad,
            "evidence": ["live walkthrough"],
            "meta": {
                "applicability": "not_applicable",
                "execution_state": "not_applicable",
                "material_type": "runnable",
                "unfamiliar_language_check": "PASS",
            },
        })
        self.assertEqual(2, code)
        self.assertTrue(any("must be BLOCKED, not N/A" in e for e in res["errors"]))

        # 6. React Doctor with skipped_files marked PASS inside code_quality is REJECTED
        code, res = self.submit_json(state_dir, "code_quality", {
            "prompt_token": p2_map["code_quality"]["prompt_token"],
            "status": "PASS",
            "summary": "code quality ok",
            "checks": pass_checks(p2_map["code_quality"]["active_rule_ids"], "checked"),
            "evidence": ["react-doctor.json"],
            "meta": {"scope": "changed", "no_telemetry": True, "skipped_files": ["src/components/ApprovalForm.tsx"]},
        })
        self.assertEqual(2, code)
        self.assertTrue(any("skipped_files must be BLOCKED" in e for e in res["errors"]))

    def test_screenshot_audit_enforces_evidence_boundary_without_git(self) -> None:
        non_git = self.tmp_path / "screenshots"
        non_git.mkdir()
        state_dir = self.tmp_path / "audit_state"

        code, out, _ = self.run_cli([
            "init", "--target", str(non_git), "--mode", "audit", "--material", "screenshot",
            "--commit", "order-list-v2", "--state-dir", str(state_dir), "--json",
        ])
        self.assertEqual(0, code, out)
        init_res = json.loads(out)
        self.assertEqual({"ui_ux_experience"}, set(init_res["required_lanes"]))

        code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
        u_item = json.loads(out)["ready_lanes"][0]
        checks_screenshot = [
            {"id": r, "status": "N/A", "note": "仅静态截图，无可运行前端入口"}
            if r.startswith("RV-BOMB-")
            else {"id": r, "status": "PASS", "note": "observed within screenshot boundary"}
            for r in u_item["active_rule_ids"]
        ]

        # Screenshot without unverified_items rejected
        code, res = self.submit_json(state_dir, "ui_ux_experience", {
            "prompt_token": u_item["prompt_token"],
            "status": "PASS",
            "summary": "视觉正常",
            "checks": checks_screenshot,
            "evidence": ["screenshot observation"],
            "meta": {
                "applicability": "not_applicable",
                "execution_state": "not_applicable",
                "material_type": "screenshot",
                "unfamiliar_language_check": "UNVERIFIED",
            },
        })
        self.assertEqual(2, code)
        self.assertTrue(any("unverified_items" in e for e in res["errors"]))

        # Proper submission -> finalize MUST return INSUFFICIENT_EVIDENCE (never READY) and generate report.html
        self.assertEqual(0, self.submit_json(state_dir, "ui_ux_experience", {
            "prompt_token": u_item["prompt_token"],
            "status": "PASS",
            "summary": "可见排版无阻断问题，交互项均未验证",
            "checks": checks_screenshot,
            "evidence": ["screenshot layout observation"],
            "unverified_items": ["键盘焦点通路", "返回后筛选保留", "提交幂等", "读屏与性能"],
            "meta": {
                "applicability": "not_applicable",
                "execution_state": "not_applicable",
                "material_type": "screenshot",
                "unfamiliar_language_check": "UNVERIFIED",
            },
        })[0])

        code, out, _ = self.run_cli(["finalize", "--run", str(state_dir), "--json"])
        self.assertEqual(1, code)
        fin = json.loads(out)
        self.assertEqual("INSUFFICIENT_EVIDENCE", fin["verdict"])
        html_text = Path(fin["report_html_path"]).read_text(encoding="utf-8")
        self.assertIn("缺证据没法判断", html_text)
        self.assertIn("键盘焦点通路", html_text)

    def test_delivery_independent_reviewer_enforced_via_gate_check(self) -> None:
        repo = make_sample_repo(self.tmp_path, with_react_ui=False, with_auth=False)
        state_dir = self.tmp_path / "indep_state"
        self.assertEqual(0, self.run_cli([
            "init", "--target", str(repo), "--base", "main",
            "--mode", "delivery", "--level", "L1",
            "--dri", "alice", "--reviewer", "alice",
            "--state-dir", str(state_dir), "--json",
        ])[0])
        for _ in range(4):
            code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
            self.assertEqual(0, code)
            step = json.loads(out)
            if step["action"] == "finalize":
                break
            for item in step["ready_lanes"]:
                lid = item["lane_id"]
                pl = {
                    "prompt_token": item["prompt_token"],
                    "status": "PASS",
                    "summary": f"{lid} ok",
                    "checks": pass_checks(item["active_rule_ids"], "checked"),
                    "evidence": [f"{lid} evidence"],
                    "commands_run": ["pytest"],
                }
                if lid == "business_acceptance":
                    pl["meta"] = {"acceptance": [{"id": "AC1", "expected": "v2", "actual": "v2", "evidence": ["pytest"], "status": "PASS"}]}
                self.assertEqual(0, self.submit_json(state_dir, lid, pl)[0], lid)

        code, out, _ = self.run_cli(["finalize", "--run", str(state_dir), "--json"])
        self.assertEqual(1, code)
        fin = json.loads(out)
        self.assertEqual("INSUFFICIENT_EVIDENCE", fin["verdict"])
        self.assertFalse(fin["gate_check"]["releasable"])
        self.assertTrue(any("must not be the DRI" in p for p in fin["gate_check"]["problems"]))

    def test_dynamic_overlay_composition_and_process_logs(self) -> None:
        repo = make_sample_repo(self.tmp_path, with_react_ui=False, with_auth=False)
        (repo / "billing_ledger.py").write_text("def settle(cents: int) -> int:\n    return cents\n", encoding="utf-8")
        git(repo, "add", "billing_ledger.py")
        git(repo, "commit", "-m", "feat: add billing ledger")

        custom_ref = self.tmp_path / "fintech-guide.md"
        custom_ref.write_text("# Fintech Guide\nAll ledger writes must be idempotent and use integer cents.\n", encoding="utf-8")

        # 1. Project auto-discovered overlay under <repo>/.evolution/review_pipeline.json
        evo_dir = repo / ".evolution"
        evo_dir.mkdir()
        (evo_dir / "review_pipeline.json").write_text(json.dumps({
            "schema_version": "1",
            "name": "project-fintech",
            "add_phases": [
                {"id": "domain_compliance", "order": 2.5, "title": "Phase 2.5: 资金对账专项审查", "allow_parallel": True}
            ],
            "add_lanes": [{
                "id": "fintech_ledger",
                "phase": "domain_compliance",
                "title": "资金与账务核对（自定义维度）",
                "depends_on": ["engineering_baseline"],
                "trigger_path_patterns": ["billing_"],
                "reference_files": [str(custom_ref)],
                "rules": [
                    {"id": "FIN-PAY-01", "title": "整数分存储与幂等记账", "check": "确认金额用整数分且写入具备幂等键。", "allow_na": False}
                ],
            }],
            "extend_lanes": {
                "code_quality": {
                    "add_rules": [
                        {"id": "ORG-SMELL-11", "group": "公司代码规范", "title": "浮点数金额计算", "check": "禁止用 float 算金额。", "allow_na": False}
                    ]
                }
            },
            "disable_lanes": {
                "business_acceptance": "本内部底层库重构无终端业务流程改动"
            },
        }, ensure_ascii=False), encoding="utf-8")

        # 2. Hard gate disable attempt via CLI overlay MUST be rejected!
        bad_overlay = self.tmp_path / "bad_overlay.json"
        bad_overlay.write_text(json.dumps({
            "schema_version": "1",
            "name": "bad-disable",
            "disable_lanes": {"engineering_baseline": "want to skip"},
        }), encoding="utf-8")
        code, out, _ = self.run_cli([
            "init", "--target", str(repo), "--base", "main",
            "--overlay", str(bad_overlay), "--state-dir", str(self.tmp_path / "bad_state"), "--json",
        ])
        self.assertEqual(2, code)
        self.assertIn("cannot disable hard gate lane 'engineering_baseline'", out)

        # 3. Catalog with --target auto-discovers project overlay!
        code, out, _ = self.run_cli(["catalog", "--target", str(repo), "--json"])
        self.assertEqual(0, code)
        cat = json.loads(out)
        self.assertEqual(7, cat["total_lanes"])   # 6 base + fintech_ledger
        self.assertEqual(50, cat["total_rules"])  # 48 base + FIN-PAY-01 + ORG-SMELL-11
        self.assertEqual("project-fintech", cat["applied_overlays"][0]["name"])

        # 4. Run full lifecycle with custom phase/lane/rule and verify process logs + HTML!
        state_dir = self.tmp_path / "overlay_state"
        code, out, _ = self.run_cli([
            "init", "--target", str(repo), "--base", "main",
            "--mode", "pr", "--level", "L1", "--state-dir", str(state_dir), "--json",
        ])
        self.assertEqual(0, code, out)
        init_res = json.loads(out)
        self.assertIn("fintech_ledger", init_res["required_lanes"])
        self.assertNotIn("business_acceptance", init_res["required_lanes"])
        self.assertIn("ORG-SMELL-11", init_res["active_rule_ids"]["code_quality"])
        self.assertEqual(["FIN-PAY-01"], init_res["active_rule_ids"]["fintech_ledger"])

        phase_done_seen = []
        for _ in range(5):
            code, out, _ = self.run_cli(["next", "--run", str(state_dir), "--emit-prompts", "--json"])
            self.assertEqual(0, code)
            step = json.loads(out)
            if step["action"] == "finalize":
                break
            for item in step["ready_lanes"]:
                lid = item["lane_id"]
                if lid == "fintech_ledger":
                    prompt_text = Path(item["prompt_path"]).read_text(encoding="utf-8")
                    self.assertIn("FIN-PAY-01", prompt_text)
                    self.assertIn("All ledger writes must be idempotent", prompt_text)
                self.assertEqual(0, self.run_cli(["start", "--run", str(state_dir), "--lane", lid, "--worker", f"agent-{lid}", "--json"])[0])
                code, sub_res = self.submit_json(state_dir, lid, {
                    "prompt_token": item["prompt_token"],
                    "status": "PASS",
                    "summary": f"{lid} passed",
                    "checks": pass_checks(item["active_rule_ids"], "verified"),
                    "evidence": [f"{lid} evidence"],
                    "commands_run": ["pytest"],
                })
                self.assertEqual(0, code, sub_res)
                phase_done_seen.extend(m for m in sub_res["milestone_logs"] if "阶段已完成" in m)

        self.assertGreaterEqual(len(phase_done_seen), 3, phase_done_seen)

        # Finalize -> READY, report.md + report.html include custom rules & Timeline process logs
        code, out, _ = self.run_cli(["finalize", "--run", str(state_dir), "--json"])
        self.assertEqual(0, code, out)
        fin = json.loads(out)
        self.assertEqual("READY", fin["verdict"])
        self.assertIn("FIN-PAY-01", fin["report"])
        self.assertIn("ORG-SMELL-11", fin["report"])
        self.assertIn("过程日志（Timeline）", fin["report"])
        html_text = Path(fin["report_html_path"]).read_text(encoding="utf-8")
        self.assertIn("FIN-PAY-01", html_text)
        self.assertIn("ORG-SMELL-11", html_text)
        self.assertIn("fintech_ledger", html_text)

        # Verify `log` command + progress.log file on disk
        code, log_out, _ = self.run_cli(["log", "--run", str(state_dir)])
        self.assertEqual(0, code)
        self.assertIn("✓ 模块已完成: fintech_ledger [PASS]", log_out)
        self.assertIn("★ 阶段已完成: Phase 2.5: 资金对账专项审查", log_out)
        self.assertIn("★ 总决完成: READY", log_out)
        self.assertTrue((state_dir / "events.jsonl").is_file())
        self.assertTrue((state_dir / "progress.log").is_file())


if __name__ == "__main__":
    unittest.main()
