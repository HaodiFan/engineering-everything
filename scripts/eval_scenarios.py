#!/usr/bin/env python3
"""Validate Engineering Everything behavior-eval scenario files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_KEYS = {
    "schema_version",
    "id",
    "harness",
    "entrypoint",
    "session_event",
    "introduced_in",
    "min_package_version",
    "prompt",
    "expected_route_ids",
    "required_fields",
    "must",
    "must_not",
}
LIST_KEYS = {
    "expected_route_ids",
    "required_fields",
    "must",
    "must_not",
    "forbidden_skill_ids",
    "expected_references",
}
ENTRYPOINTS = {"using-engineering-everything", "engineering-everything", "direct-subskill"}
SESSION_EVENTS = {"new-session", "resume", "task-switch"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_scalar(value: str) -> str | list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    return value.strip('"').strip("'")


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    data: dict[str, object] = {}
    current_list: str | None = None
    for raw_line in text[4:end].splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - "):
            if current_list is None:
                raise ValueError(f"list item without key: {raw_line}")
            data.setdefault(current_list, [])
            assert isinstance(data[current_list], list)
            data[current_list].append(str(parse_scalar(raw_line[4:])))
            continue
        if ":" not in raw_line:
            raise ValueError(f"invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_list = key
        else:
            data[key] = parse_scalar(value)
            current_list = None
    return data


def route_ids(root: Path) -> set[str]:
    path = root / "data/routes.yaml"
    if not path.exists():
        return set()
    return set(re.findall(r"^  - id:\s*([a-z0-9-]+)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE))


def skill_ids(root: Path) -> set[str]:
    return {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}


def output_fields(root: Path) -> set[str]:
    path = root / "references/output-contracts.md"
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    start = text.find("<!-- output-fields:start -->")
    end = text.find("<!-- output-fields:end -->")
    if start == -1 or end == -1 or end < start:
        return set()
    block = text[start:end]
    return {
        match.group(1).strip()
        for match in re.finditer(r"^\-\s+(.+?)\s*$", block, re.MULTILINE)
    }


def as_list(data: dict[str, object], key: str) -> list[str]:
    value = data.get(key, [])
    return value if isinstance(value, list) else []


def validate_scenarios(root: Path) -> list[str]:
    errors: list[str] = []
    scenarios_dir = root / "evals/scenarios"
    if not scenarios_dir.exists():
        return ["missing evals/scenarios"]

    known_routes = route_ids(root)
    known_skills = skill_ids(root)
    known_fields = output_fields(root)
    seen_ids: set[str] = set()

    for path in sorted(scenarios_dir.glob("*.md")):
        rel = path.relative_to(root)
        try:
            data = parse_frontmatter(path)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
            continue

        missing = sorted(REQUIRED_KEYS - set(data))
        if missing:
            errors.append(f"{rel}: missing required keys: {', '.join(missing)}")

        scenario_id = str(data.get("id", ""))
        if scenario_id != path.stem:
            errors.append(f"{rel}: id must match filename stem")
        if scenario_id in seen_ids:
            errors.append(f"{rel}: duplicate scenario id {scenario_id}")
        seen_ids.add(scenario_id)

        for key in sorted(LIST_KEYS & set(data)):
            if not isinstance(data[key], list):
                errors.append(f"{rel}: {key} must be a list")

        entrypoint = str(data.get("entrypoint", ""))
        if entrypoint and entrypoint not in ENTRYPOINTS:
            errors.append(f"{rel}: invalid entrypoint {entrypoint}")

        session_event = str(data.get("session_event", ""))
        if session_event and session_event not in SESSION_EVENTS:
            errors.append(f"{rel}: invalid session_event {session_event}")

        for key in ["introduced_in", "min_package_version"]:
            value = str(data.get(key, ""))
            if value and not SEMVER_RE.match(value):
                errors.append(f"{rel}: {key} must be semver, got {value}")

        for route_id in as_list(data, "expected_route_ids"):
            if route_id not in known_routes:
                errors.append(f"{rel}: unknown expected_route_id {route_id}")

        for field in as_list(data, "required_fields"):
            if field not in known_fields:
                errors.append(f"{rel}: unknown output field {field}")

        for skill_id in as_list(data, "forbidden_skill_ids"):
            if skill_id not in known_skills:
                errors.append(f"{rel}: unknown forbidden_skill_id {skill_id}")

        for reference in as_list(data, "expected_references"):
            if not (root / reference).exists():
                errors.append(f"{rel}: missing expected_reference {reference}")

    if not seen_ids:
        errors.append("evals/scenarios must contain at least one scenario")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Engineering Everything eval scenarios.")
    parser.add_argument("action", choices=["validate"], nargs="?", default="validate")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors = validate_scenarios(repo_root())
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        for error in errors:
            print(f"error: {error}")
        print(f"eval_scenarios: {len(errors)} error(s)")
    else:
        print("eval_scenarios: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
