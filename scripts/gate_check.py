#!/usr/bin/env python3
"""Check an Evidence Package against the Delivery Gates protocol.

The check is deterministic and conservative: missing evidence never becomes PASS.
Protocol: references/delivery-gates.md. Shape: schemas/evidence-package.schema.json.

Exit codes: 0 releasable, 1 not releasable, 2 invalid package or usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


STEP_IDS = ("D", "G0", "G1", "G2", "G3", "G4", "CR", "R")
STATUSES = {"PASS", "FAIL", "BLOCKED", "N/A"}
LEVELS = ("L0", "L1", "L2", "L3")
# Steps that are always required at a given authorization level.
BASE_REQUIRED = {
    "L0": {"G0", "G1", "CR"},
    "L1": {"G0", "G1", "G4", "CR"},
    "L2": {"G0", "G1", "G4", "CR"},
    "L3": {"G0", "G1", "G4", "CR"},
}
NEVER_NA = {"G0"}
NEVER_WAIVED = {"G0"}
HUMAN_JUDGMENT_STEPS = {"G3", "G4"}


def template() -> dict:
    return {
        "schema_version": "1",
        "task_id": "",
        "intent_revision": 1,
        "authorization_level": "L1",
        "dri": "",
        "reviewer": "",
        "commit": "",
        "environment": "",
        "acceptance": [
            {"id": "AC1", "expected": "", "actual": "", "evidence": [], "status": "BLOCKED"}
        ],
        "steps": [
            {"id": step, "required": step in BASE_REQUIRED["L1"], "status": "BLOCKED", "evidence": [], "reason": ""}
            for step in STEP_IDS
        ],
        "unrun_checks": [],
        "residual_risks": [],
        "release": {"rollout": "", "rollback": ""},
        "approvals": [],
        "exceptions": [],
    }


def _nonempty_str(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _evidence_list(item: dict) -> list:
    evidence = item.get("evidence", [])
    return evidence if isinstance(evidence, list) else []


def validate_shape(pkg: object) -> list[str]:
    """Structural errors that make the package unusable (exit 2)."""
    if not isinstance(pkg, dict):
        return ["package must be a JSON object"]
    errors: list[str] = []
    for key in ("task_id", "commit"):
        if not _nonempty_str(pkg.get(key)):
            errors.append(f"missing {key}")
    if pkg.get("authorization_level") not in LEVELS:
        errors.append(f"authorization_level must be one of {', '.join(LEVELS)}")
    steps = pkg.get("steps")
    if not isinstance(steps, list):
        errors.append("steps must be a list")
    else:
        seen: set[str] = set()
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"steps[{index}] must be an object")
                continue
            step_id = step.get("id")
            if step_id not in STEP_IDS:
                errors.append(f"steps[{index}].id must be one of {', '.join(STEP_IDS)}")
            elif step_id in seen:
                errors.append(f"duplicate step {step_id}")
            else:
                seen.add(step_id)
            if step.get("status") not in STATUSES:
                errors.append(f"step {step_id}: status must be one of {', '.join(sorted(STATUSES))}")
    acceptance = pkg.get("acceptance", [])
    if not isinstance(acceptance, list):
        errors.append("acceptance must be a list")
    else:
        for index, item in enumerate(acceptance):
            if not isinstance(item, dict) or not _nonempty_str(item.get("id")):
                errors.append(f"acceptance[{index}] needs an id")
            elif item.get("status") not in STATUSES:
                errors.append(f"acceptance {item.get('id')}: invalid status")
    return errors


def evaluate(pkg: dict) -> dict:
    """Return effective step statuses, blocking problems and the release verdict."""
    level = pkg["authorization_level"]
    commit = pkg["commit"]
    problems: list[str] = []
    approvals = [a for a in pkg.get("approvals", []) if isinstance(a, dict)]
    exceptions = [e for e in pkg.get("exceptions", []) if isinstance(e, dict)]

    def approved(step_id: str) -> bool:
        return any(a.get("step") == step_id and _nonempty_str(a.get("approver")) for a in approvals)

    steps = {s["id"]: s for s in pkg["steps"]}
    required = set(BASE_REQUIRED[level]) | {sid for sid, s in steps.items() if s.get("required") is True}
    effective: dict[str, str] = {}

    for step_id in STEP_IDS:
        step = steps.get(step_id)
        if step is None:
            if step_id in required:
                effective[step_id] = "BLOCKED"
                problems.append(f"{step_id}: required step missing from package")
            continue
        status = step["status"]
        if status == "PASS":
            if not _evidence_list(step):
                status = "BLOCKED"
                problems.append(f"{step_id}: PASS without evidence")
            elif _nonempty_str(step.get("commit")) and step["commit"] != commit:
                status = "BLOCKED"
                problems.append(f"{step_id}: evidence is for commit {step['commit']}, package is {commit}")
            elif step_id in HUMAN_JUDGMENT_STEPS and level in ("L2", "L3") and not approved(step_id):
                status = "BLOCKED"
                problems.append(f"{step_id}: L2+ judgment needs a named approver in approvals")
        elif status == "N/A":
            if step_id in NEVER_NA:
                status = "BLOCKED"
                problems.append(f"{step_id}: cannot be N/A")
            elif not _nonempty_str(step.get("reason")):
                status = "BLOCKED"
                problems.append(f"{step_id}: N/A needs a reason")
        effective[step_id] = status

    # Acceptance criteria feed G1.
    acceptance = pkg.get("acceptance", [])
    if not acceptance and level != "L0":
        problems.append("G1: no acceptance criteria for an L1+ task")
        if effective.get("G1") == "PASS":
            effective["G1"] = "BLOCKED"
    for item in acceptance:
        ac_status = item["status"]
        if ac_status == "PASS" and not _evidence_list(item):
            ac_status = "BLOCKED"
            problems.append(f"{item['id']}: PASS without evidence")
        if ac_status in ("FAIL", "BLOCKED") and effective.get("G1") == "PASS":
            effective["G1"] = ac_status
            problems.append(f"G1: acceptance {item['id']} is {ac_status}")

    # Independence and authorization.
    if level != "L0":
        reviewer, dri = pkg.get("reviewer"), pkg.get("dri")
        if not _nonempty_str(reviewer):
            problems.append("reviewer: L1+ needs an independent reviewer")
        elif _nonempty_str(dri) and reviewer.strip() == dri.strip():
            problems.append("reviewer: must not be the DRI")
    if level == "L3" and not approved("L3"):
        problems.append("L3: needs a Sponsor or authorized approval with step 'L3'")

    # Exceptions may waive a required FAIL/BLOCKED step, except hard gates.
    waived: list[str] = []
    for step_id in sorted(required):
        if effective.get(step_id) not in ("FAIL", "BLOCKED"):
            continue
        match = next((e for e in exceptions if e.get("step") == step_id), None)
        if match is None:
            continue
        if step_id in NEVER_WAIVED:
            problems.append(f"{step_id}: hard gate cannot be waived")
            continue
        if all(_nonempty_str(match.get(k)) for k in ("approver", "reason", "expires", "remediation")):
            waived.append(step_id)
        else:
            problems.append(f"{step_id}: exception needs approver, reason, expires and remediation")

    blocking = [
        f"{step_id}: {effective.get(step_id, 'BLOCKED')}"
        for step_id in sorted(required)
        if effective.get(step_id) in ("FAIL", "BLOCKED") and step_id not in waived
    ]
    gate_problems = [p for p in problems if p.startswith(("reviewer", "L3", "G1: no acceptance"))]
    releasable = not blocking and not gate_problems
    return {
        "task_id": pkg["task_id"],
        "commit": commit,
        "authorization_level": level,
        "required_steps": sorted(required),
        "effective_status": effective,
        "waived_steps": waived,
        "blocking": blocking,
        "problems": problems,
        "releasable": releasable,
    }


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check an Evidence Package against Delivery Gates.")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Evaluate an evidence package JSON file.")
    check.add_argument("path", type=Path)
    check.add_argument("--json", action="store_true", help="Emit JSON result.")
    sub.add_parser("template", help="Print an empty evidence package (all BLOCKED).")
    args = parser.parse_args(argv)

    if args.command == "template":
        print(json.dumps(template(), ensure_ascii=False, indent=2))
        return 0

    try:
        pkg = load(args.path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"gate_check: cannot read {args.path}: {exc}", file=sys.stderr)
        return 2
    shape_errors = validate_shape(pkg)
    if shape_errors:
        if args.json:
            print(json.dumps({"valid": False, "errors": shape_errors, "releasable": False}, ensure_ascii=False, indent=2))
        else:
            for error in shape_errors:
                print(f"invalid: {error}")
        return 2

    result = evaluate(pkg)  # type: ignore[arg-type]
    if args.json:
        print(json.dumps({"valid": True, **result}, ensure_ascii=False, indent=2))
    else:
        verdict = "RELEASABLE" if result["releasable"] else "NOT RELEASABLE"
        print(f"{result['task_id']} @ {result['commit']} [{result['authorization_level']}]: {verdict}")
        for step_id, status in result["effective_status"].items():
            marker = "*" if step_id in result["required_steps"] else " "
            print(f"  {marker} {step_id}: {status}")
        for problem in result["problems"]:
            print(f"  - {problem}")
    return 0 if result["releasable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
