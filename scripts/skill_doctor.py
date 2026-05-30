#!/usr/bin/env python3
"""Validate the Engineering Everything package before install or release."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SKILL_NAME = "engineering-everything"
OLD_SKILL_NAMES = ["software-dev-workflow", "cto-copilot-skill"]
MAX_SKILL_LINES = 200


@dataclass
class Finding:
    level: str
    message: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def skill_dir(root: Path) -> Path:
    return root / SKILL_NAME


def is_installed_layout(root: Path, package: Path) -> bool:
    return (
        package.parent == root
        and root.name == "skills"
        and root.parent.name in {".agents", ".codex"}
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def parse_yaml_scalar(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip().strip('"')


def add(findings: list[Finding], level: str, message: str) -> None:
    findings.append(Finding(level, message))


def check_required_files(root: Path, package: Path, findings: list[Finding]) -> None:
    required = [
        package / "SKILL.md",
        package / "agents/openai.yaml",
        package / "scripts/install.py",
        package / "scripts/skill_doctor.py",
        package / "scripts/lesson.py",
        package / "schemas/lesson.schema.json",
        package / "schemas/pattern.schema.json",
        package / "data/routes.yaml",
        package / "data/review_roles.yaml",
        package / "data/validation_commands.yaml",
        package / "references/engineering-scenarios.md",
        package / "references/engineering-scenario-map.md",
        package / "references/psps-framework.md",
        package / "references/refactoring-rules.md",
    ]
    if not is_installed_layout(root, package):
        required.insert(0, root / "README.md")
    for path in required:
        if not path.exists():
            add(findings, "error", f"missing required file: {path.relative_to(root)}")


def check_skill_metadata(root: Path, package: Path, findings: list[Finding]) -> str | None:
    path = package / "SKILL.md"
    if not path.exists():
        return None
    text = read_text(path)
    frontmatter = parse_frontmatter(text)
    version = frontmatter.get("version")
    if frontmatter.get("name") != SKILL_NAME:
        add(findings, "error", f"SKILL.md name must be {SKILL_NAME}")
    if not version or not re.match(r"^\d+\.\d+\.\d+$", version):
        add(findings, "error", "SKILL.md version must be semver-like, for example 0.9.0")
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        add(findings, "error", f"SKILL.md has {line_count} lines; soft limit is {MAX_SKILL_LINES}")
    if "工程路由:" not in text:
        add(findings, "error", "SKILL.md must include the engineering route output field")
    return version


def check_agent_manifest(package: Path, version: str | None, findings: list[Finding]) -> None:
    path = package / "agents/openai.yaml"
    if not path.exists():
        return
    text = read_text(path)
    if parse_yaml_scalar(text, "skill") != SKILL_NAME:
        add(findings, "error", f"agents/openai.yaml skill must be {SKILL_NAME}")
    manifest_version = parse_yaml_scalar(text, "version")
    if version and manifest_version != version:
        add(findings, "error", f"agents/openai.yaml version {manifest_version} != SKILL.md {version}")
    if f"${SKILL_NAME}" not in text:
        add(findings, "error", "agents/openai.yaml default_prompt must use the current trigger")


def check_readme(root: Path, version: str | None, findings: list[Finding]) -> None:
    path = root / "README.md"
    if not path.exists():
        return
    text = read_text(path)
    required = [
        f"${SKILL_NAME}",
        f"~/.codex/skills/{SKILL_NAME}",
        f"~/.agents/skills/{SKILL_NAME}",
        f"python3 {SKILL_NAME}/scripts/install.py",
        "references/psps-framework.md",
        "references/refactoring-rules.md",
    ]
    for needle in required:
        if needle not in text:
            add(findings, "error", f"README.md missing {needle}")
    if version and f"`{version}`" not in text:
        add(findings, "warning", f"README.md does not mention current version {version}")
    for old_name in OLD_SKILL_NAMES:
        forbidden = [
            f"${old_name}",
            f"~/.codex/skills/{old_name}",
            f"~/.agents/skills/{old_name}",
        ]
        for needle in forbidden:
            if needle in text:
                add(findings, "error", f"README.md still contains old install/trigger string {needle}")


def check_markdown(package: Path, findings: list[Finding]) -> None:
    for path in [package / "SKILL.md", *sorted((package / "references").glob("*.md"))]:
        if not path.exists():
            continue
        text = read_text(path)
        if text.count("```") % 2:
            add(findings, "error", f"unbalanced fenced code block: {path.relative_to(package.parent)}")


def check_reference_links(package: Path, findings: list[Finding]) -> None:
    for path in [package / "SKILL.md", *sorted((package / "references").glob("*.md"))]:
        if not path.exists():
            continue
        text = read_text(path)
        for match in re.finditer(r"`(references/[^`]+?\.md)`", text):
            target = package / match.group(1)
            if not target.exists():
                add(
                    findings,
                    "error",
                    f"missing referenced file {match.group(1)} from {path.relative_to(package.parent)}",
                )


def parse_route_blocks(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^  - id:\s*([a-z0-9-]+)\s*$", text, re.MULTILINE))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1)] = text[match.start() : end]
    return blocks


def parse_aliases(block: str) -> list[str]:
    match = re.search(r"^\s+aliases:\s*\[(.*?)\]\s*$", block, re.MULTILINE)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def check_route_seeds(package: Path, findings: list[Finding]) -> None:
    path = package / "data/routes.yaml"
    if not path.exists():
        return
    text = read_text(path)
    blocks = parse_route_blocks(text)
    required_routes = {
        "product",
        "architecture",
        "inherit",
        "execution-plan",
        "build",
        "refactor",
        "review-release",
        "learn",
        "talent",
        "onboarding",
        "organization-system",
        "project-ops",
        "non-software-development",
    }
    required_aliases = {
        "talent": {"/interview", "/hire", "/scorecard"},
        "refactor": {"/refactor", "/cleanup", "/modularize"},
        "onboarding": {"/onboard", "/training", "/bootcamp"},
        "organization-system": {"/org", "/company", "/sop"},
        "project-ops": {"/estimate", "/wbs", "/project"},
        "non-software-development": {"/artifact", "/nonsoftware", "/workspace"},
    }
    for route_id in sorted(required_routes - set(blocks)):
        add(findings, "error", f"data/routes.yaml missing required route: {route_id}")

    alias_owner: dict[str, str] = {}
    for route_id, block in blocks.items():
        aliases = parse_aliases(block)
        if not aliases:
            add(findings, "error", f"route {route_id} must define slash aliases")
        if "fuzzy_examples:" not in block:
            add(findings, "error", f"route {route_id} must define fuzzy_examples")
        if "signals:" not in block:
            add(findings, "error", f"route {route_id} must define signals")
        for alias in aliases:
            if not alias.startswith("/"):
                add(findings, "error", f"route {route_id} alias must start with /: {alias}")
            if alias in alias_owner:
                add(findings, "error", f"alias {alias} duplicated in routes {alias_owner[alias]} and {route_id}")
            alias_owner[alias] = route_id
        missing_aliases = required_aliases.get(route_id, set()) - set(aliases)
        if missing_aliases:
            add(findings, "error", f"route {route_id} missing aliases: {', '.join(sorted(missing_aliases))}")
        for reference in re.findall(r"^\s+-\s+(references/[^\s#]+\.md)\s*$", block, re.MULTILINE):
            if not (package / reference).exists():
                add(findings, "error", f"route {route_id} references missing file: {reference}")


def check_old_names(root: Path, package: Path, findings: list[Finding]) -> None:
    allow = {
        root / ".git",
    }
    del allow
    for path in [root / "README.md", package / "SKILL.md", package / "agents/openai.yaml"]:
        if not path.exists():
            continue
        text = read_text(path)
        for old_name in OLD_SKILL_NAMES:
            if old_name in text:
                add(findings, "error", f"old skill name {old_name} remains in {path.relative_to(root)}")


def check_json_schemas(package: Path, findings: list[Finding]) -> None:
    for path in sorted((package / "schemas").glob("*.json")):
        try:
            json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            add(findings, "error", f"invalid JSON schema {path.relative_to(package.parent)}: {exc}")


def run() -> tuple[list[Finding], Path, Path]:
    root = repo_root()
    package = skill_dir(root)
    findings: list[Finding] = []
    if not package.exists():
        add(findings, "error", f"missing package directory: {SKILL_NAME}/")
        return findings, root, package
    check_required_files(root, package, findings)
    version = check_skill_metadata(root, package, findings)
    check_agent_manifest(package, version, findings)
    check_readme(root, version, findings)
    check_markdown(package, findings)
    check_reference_links(package, findings)
    check_route_seeds(package, findings)
    check_old_names(root, package, findings)
    check_json_schemas(package, findings)
    return findings, root, package


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Engineering Everything package.")
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    args = parser.parse_args()

    findings, root, package = run()
    errors = [item for item in findings if item.level == "error"]
    warnings = [item for item in findings if item.level == "warning"]

    if args.json:
        print(
            json.dumps(
                {
                    "repo_root": str(root),
                    "skill_dir": str(package),
                    "errors": [item.message for item in errors],
                    "warnings": [item.message for item in warnings],
                    "ok": not errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if not findings:
            print("skill_doctor: ok")
        else:
            for item in findings:
                print(f"{item.level}: {item.message}")
            print(f"skill_doctor: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
