#!/usr/bin/env python3
"""Check the Engineering Everything self-evolution harness."""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SKILL_NAME = "engineering-everything"
MAX_SKILL_LINES = 200
LESSON_MARKER = "<!-- 真实 lessons 从这一行下方开始追加 -->"
PATTERN_MARKER = "<!-- 真实 patterns 从这一行下方开始追加 -->"


@dataclass
class Finding:
    level: str
    message: str


def package_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add(findings: list[Finding], level: str, message: str) -> None:
    findings.append(Finding(level, message))


def run_command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def count_cards(text: str, marker: str, prefix: str) -> int:
    body = text.split(marker, 1)[1] if marker in text else text
    return len(re.findall(rf"^### {re.escape(prefix)}-\d{{4}}:", body, re.MULTILINE))


def declared_count(text: str) -> int | None:
    match = re.search(r"当前条目数：(\d+)", text)
    return int(match.group(1)) if match else None


def check_count_file(
    package: Path,
    findings: list[Finding],
    relative: str,
    marker: str,
    prefix: str,
) -> None:
    path = package / relative
    if not path.exists():
        add(findings, "error", f"missing {relative}")
        return
    text = read_text(path)
    actual = count_cards(text, marker, prefix)
    declared = declared_count(text)
    if declared is not None and declared != actual:
        add(findings, "error", f"{relative} declares {declared} entries but has {actual}")


def check_harness_reference(package: Path, findings: list[Finding]) -> None:
    path = package / "references/self-evolution-harness.md"
    if not path.exists():
        add(findings, "error", "missing references/self-evolution-harness.md")
        return
    text = read_text(path)
    for needle in ["GitHub issue", "lesson` label", "gh issue view"]:
        if needle not in text:
            add(findings, "error", f"self-evolution harness missing issue intake rule: {needle}")


def check_skill_router(package: Path, findings: list[Finding]) -> None:
    root_skill = package / "SKILL.md"
    if root_skill.exists():
        add(findings, "error", "root SKILL.md must not exist; plugin runtime skills live under skills/")

    manifest = package / ".codex-plugin/plugin.json"
    if not manifest.exists():
        add(findings, "error", "missing .codex-plugin/plugin.json")
    else:
        try:
            data = json.loads(read_text(manifest))
        except json.JSONDecodeError as exc:
            add(findings, "error", f"invalid .codex-plugin/plugin.json: {exc}")
        else:
            if data.get("skills") != "./skills/":
                add(findings, "error", ".codex-plugin/plugin.json skills must be ./skills/")

    for relative in [
        "skills/using-engineering-everything/SKILL.md",
        "skills/engineering-everything/SKILL.md",
    ]:
        path = package / relative
        if not path.exists():
            add(findings, "error", f"missing {relative}")
            continue
        text = read_text(path)
        line_count = len(text.splitlines())
        if line_count > MAX_SKILL_LINES:
            add(findings, "error", f"{relative} has {line_count} lines; max is {MAX_SKILL_LINES}")

    router = package / "skills/engineering-everything/SKILL.md"
    router_text = read_text(router) if router.exists() else ""
    for needle in [
        "references/output-contracts.md",
        "references/self-evolution-harness.md",
    ]:
        if needle not in router_text:
            add(findings, "error", f"skills/engineering-everything/SKILL.md missing {needle}")


def check_route(package: Path, findings: list[Finding]) -> None:
    path = package / "data/routes.yaml"
    if not path.exists():
        add(findings, "error", "missing data/routes.yaml")
        return
    text = read_text(path)
    learn_match = re.search(r"^  - id: learn\n(?P<body>.*?)(?=^  - id: |\Z)", text, re.MULTILINE | re.DOTALL)
    learn_body = learn_match.group("body") if learn_match else ""
    for needle in ["/self-evolve", "自进化", "references/self-evolution-harness.md"]:
        if needle not in learn_body:
            add(findings, "error", f"learn route missing {needle}")


def walk_relative_files(root: Path) -> list[Path]:
    ignored = {"__pycache__", ".DS_Store"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            files.append(path.relative_to(root))
    return sorted(files)


def compare_install(package: Path, findings: list[Finding], strict: bool) -> None:
    home = Path.home()
    codex = home / ".codex/skills" / SKILL_NAME
    agents = home / ".agents/skills" / SKILL_NAME
    install_roots = {codex.resolve(), agents.resolve()}
    if package.resolve() not in install_roots or not codex.exists() or not agents.exists():
        return
    codex_files = walk_relative_files(codex)
    agents_files = walk_relative_files(agents)
    level = "error" if strict else "warning"
    if codex_files != agents_files:
        add(findings, level, ".codex and .agents install file lists differ")
        return
    for rel_path in codex_files:
        if not filecmp.cmp(codex / rel_path, agents / rel_path, shallow=False):
            add(findings, level, f".agents copy differs: {rel_path}")


def parse_github_repo(remote_url: str) -> str | None:
    remote_url = remote_url.strip()
    match = re.match(r"^https://github\.com/([^/]+/[^/.]+)(?:\.git)?$", remote_url)
    if match:
        return match.group(1)
    match = re.match(r"^git@github\.com:([^/]+/[^/.]+)(?:\.git)?$", remote_url)
    if match:
        return match.group(1)
    return None


def gh_current_login() -> str | None:
    result = run_command(["gh", "api", "user", "--jq", ".login"])
    return result.stdout.strip() if result.returncode == 0 else None


def gh_orgs() -> list[str]:
    result = run_command(["gh", "api", "user/orgs", "--jq", ".[].login"])
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def gh_search_repos(query: str) -> list[str]:
    result = run_command(["gh", "search", "repos", query, "--json", "fullName", "--limit", "10"])
    if result.returncode != 0:
        return []
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return [row["fullName"] for row in rows if row.get("fullName")]


def discover_github_sources() -> list[str]:
    if shutil.which("gh") is None:
        return []
    candidates: list[str] = []
    login = gh_current_login()
    if login:
        for repo in gh_search_repos(f"{SKILL_NAME} user:{login}"):
            if repo not in candidates:
                candidates.append(repo)
    for org in gh_orgs():
        for repo in gh_search_repos(f"{SKILL_NAME} org:{org}"):
            if repo not in candidates:
                candidates.append(repo)
    if candidates:
        return candidates
    for query in [SKILL_NAME]:
        for repo in gh_search_repos(query):
            if repo not in candidates:
                candidates.append(repo)
    return candidates


def check_dependencies(findings: list[Finding]) -> None:
    for command in ["git", "gh"]:
        if shutil.which(command) is None:
            add(findings, "error", f"missing required dependency: {command}")
    if shutil.which("gh") is None:
        return
    auth = run_command(["gh", "auth", "status"])
    if auth.returncode != 0:
        add(findings, "error", "gh is installed but not authenticated; run gh auth login")


def check_canonical_source(package: Path, findings: list[Finding]) -> None:
    if shutil.which("git") is None:
        return
    root_result = run_command(["git", "-C", str(package), "rev-parse", "--show-toplevel"])
    if root_result.returncode != 0:
        candidates = discover_github_sources()
        if candidates:
            add(
                findings,
                "warning",
                "package is not inside a git repository; discovered possible canonical source: "
                + ", ".join(candidates[:3]),
            )
        else:
            add(findings, "error", "canonical source not verified: package is not inside a git repository")
        return
    git_root = Path(root_result.stdout.strip())
    if git_root != package:
        add(findings, "warning", f"git root is {git_root}, not package root {package}")
    remote_result = run_command(["git", "-C", str(git_root), "remote", "get-url", "origin"])
    if remote_result.returncode != 0:
        candidates = discover_github_sources()
        if candidates:
            add(findings, "warning", "missing origin remote; discovered possible canonical source: " + candidates[0])
        else:
            add(findings, "error", "canonical source not verified: missing origin remote")
        return
    repo = parse_github_repo(remote_result.stdout)
    if not repo:
        candidates = discover_github_sources()
        if candidates:
            add(
                findings,
                "warning",
                f"origin remote is not a GitHub repo: {remote_result.stdout.strip()}; discovered {candidates[0]}",
            )
        else:
            add(findings, "error", f"origin remote is not a GitHub repo: {remote_result.stdout.strip()}")
        return
    if shutil.which("gh") is None:
        return
    view_result = run_command(["gh", "repo", "view", repo, "--json", "nameWithOwner,url,defaultBranchRef"])
    if view_result.returncode != 0:
        add(findings, "error", f"cannot access GitHub repo with gh: {repo}")


def run(strict_install: bool, include_runtime: bool) -> tuple[list[Finding], Path]:
    package = package_dir()
    findings: list[Finding] = []
    check_skill_router(package, findings)
    check_route(package, findings)
    check_harness_reference(package, findings)
    check_count_file(package, findings, "references/lessons.md", LESSON_MARKER, "L")
    check_count_file(package, findings, "references/patterns-skill.md", PATTERN_MARKER, "P")
    compare_install(package, findings, strict_install)
    if include_runtime:
        check_dependencies(findings)
        check_canonical_source(package, findings)
    return findings, package


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Engineering Everything self-evolution wiring.")
    parser.add_argument("command", choices=["check", "doctor"])
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--strict-install", action="store_true", help="Treat .agents drift as an error.")
    args = parser.parse_args()

    findings, package = run(args.strict_install, include_runtime=args.command == "doctor")
    errors = [item for item in findings if item.level == "error"]
    warnings = [item for item in findings if item.level == "warning"]
    if args.json:
        print(
            json.dumps(
                {
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
        for item in findings:
            print(f"{item.level}: {item.message}")
        if not findings:
            print("self_evolve: ok")
        else:
            print(f"self_evolve: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
