#!/usr/bin/env python3
"""Check whether Engineering Everything and EvoZeus have newer releases on GitHub.

Check-only: never pulls, installs or edits anything except its own cache and,
for `install-hook`, the host hook config the user asked to change.

Commands:
  check [--json] [--force]          Print the status of both products.
  hook --host claude|codex          SessionStart hook: silent when current or offline.
  install-hook --target claude|codex|both [--dry-run]
  uninstall-hook --target claude|codex|both [--dry-run]

Environment:
  EE_UPDATE_CHECK=0                 Disable the hook.
  EE_UPDATE_CHECK_INTERVAL=<secs>   Remote check throttle (default 3600).
  EVOZEUS_HOME                      EvoZeus home (default ~/.evozeus).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN_JSON = REPO / ".codex-plugin" / "plugin.json"
DEFAULT_BRANCH = "main"
DEFAULT_INTERVAL = 3600
FETCH_TIMEOUT = 4
HOOK_MARKER = "engineering-everything/scripts/update_check.py"
CACHE_PATH = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "engineering-everything" / "update-check.json"


# ---------- helpers ----------

def parse_version(text: str | None) -> tuple[int, ...] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(part) for part in match.groups()) if match else None


def is_newer(remote: str | None, local: str | None) -> bool:
    r, l = parse_version(remote), parse_version(local)
    return bool(r and l and r > l)


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "engineering-everything-update-check"})
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT) as response:  # noqa: S310 - fixed https URLs
        return json.loads(response.read().decode("utf-8"))


def git(*args: str) -> str:
    result = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=5)
    return result.stdout.strip() if result.returncode == 0 else ""


def raw_url(repository: str, branch: str, path: str) -> str | None:
    match = re.match(r"https://github\.com/([^/]+)/([^/.]+)", repository or "")
    if not match:
        return None
    owner, name = match.groups()
    return f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/{path}"


def evozeus_home() -> Path:
    return Path(os.environ.get("EVOZEUS_HOME", Path.home() / ".evozeus"))


# ---------- local state (cheap, always fresh) ----------

def local_ee() -> dict:
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    return {
        "version": plugin.get("version"),
        "repository": plugin.get("repository") or plugin.get("homepage"),
        "repo_path": str(REPO),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
    }


def local_evozeus() -> dict:
    home = evozeus_home()
    cli = home / "bin" / "evozeus"
    info: dict = {"installed": cli.exists(), "home": str(home)}
    if not cli.exists():
        return info
    try:
        result = subprocess.run([str(cli), "channel", "status", "--json"], capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout).get("data", {})
        info.update(
            version=data.get("product_version"),
            channel=data.get("active_channel"),
            manifest_source=data.get("manifest_source"),
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        info["error"] = "evozeus channel status failed"
    return info


# ---------- remote state (throttled) ----------

def remote_versions(ee: dict, evo: dict) -> dict:
    remote: dict = {"checked_at": int(time.time()), "errors": []}
    url = raw_url(ee.get("repository") or "", DEFAULT_BRANCH, ".codex-plugin/plugin.json")
    if url:
        try:
            remote["ee_version"] = fetch_json(url).get("version")
        except Exception as exc:  # network errors must never break a session
            remote["errors"].append(f"ee: {type(exc).__name__}")
    if evo.get("manifest_source"):
        try:
            remote["evozeus_version"] = fetch_json(evo["manifest_source"]).get("product_version")
        except Exception as exc:
            remote["errors"].append(f"evozeus: {type(exc).__name__}")
    return remote


def load_cache() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_cache(data: dict) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def interval() -> int:
    try:
        return max(0, int(os.environ.get("EE_UPDATE_CHECK_INTERVAL", DEFAULT_INTERVAL)))
    except ValueError:
        return DEFAULT_INTERVAL


def get_remote(ee: dict, evo: dict, force: bool) -> dict:
    cache = load_cache()
    fresh = time.time() - cache.get("checked_at", 0) < interval()
    same_source = cache.get("manifest_source") == evo.get("manifest_source")
    if not force and fresh and same_source and not cache.get("errors"):
        return {**cache, "cached": True}
    remote = remote_versions(ee, evo)
    remote["manifest_source"] = evo.get("manifest_source")
    save_cache(remote)
    return {**remote, "cached": False}


# ---------- report ----------

def build_report(force: bool = False) -> dict:
    ee, evo = local_ee(), local_evozeus()
    remote = get_remote(ee, evo, force)
    ee_update = is_newer(remote.get("ee_version"), ee.get("version"))
    evo_update = is_newer(remote.get("evozeus_version"), evo.get("version"))
    return {
        "engineering_everything": {
            **ee,
            "latest": remote.get("ee_version"),
            "update_available": ee_update,
            "how_to_update": ee_update_hint(ee) if ee_update else None,
        },
        "evozeus": {
            **evo,
            "latest": remote.get("evozeus_version"),
            "update_available": evo_update,
            "how_to_update": evozeus_update_hint(evo) if evo_update else None,
        },
        "checked_at": remote.get("checked_at"),
        "cached": remote.get("cached"),
        "errors": remote.get("errors", []),
    }


def ee_update_hint(ee: dict) -> str:
    repo = ee["repo_path"]
    if ee.get("branch") != DEFAULT_BRANCH:
        return f"本地在 {ee.get('branch')} 分支上：先把它合并或收尾，再切回 {DEFAULT_BRANCH} 拉取（git -C \"{repo}\" pull --ff-only）。"
    if ee.get("dirty"):
        return f"本地有未提交改动：先提交或暂存，再运行 git -C \"{repo}\" pull --ff-only。"
    return f"运行 git -C \"{repo}\" pull --ff-only，拉下后立即生效（各 Agent 的 skill 是软链）。"


def evozeus_update_hint(evo: dict) -> str:
    cli = Path(evo["home"]) / "bin" / "evozeus"
    return f"EvoZeus 会在新会话启动时自动升级；如果一直没升，运行 {cli} version --json 触发检查，或用 maintain-evozeus 排查。"


def summary_lines(report: dict) -> list[str]:
    lines = []
    ee, evo = report["engineering_everything"], report["evozeus"]
    if ee["update_available"]:
        lines.append(f"Engineering Everything 有新版本 {ee['latest']}（本地 {ee['version']}）。{ee['how_to_update']}")
    if evo["update_available"]:
        lines.append(f"EvoZeus 有新版本 {evo['latest']}（本地 {evo['version']}）。{evo['how_to_update']}")
    return lines


def print_human(report: dict) -> None:
    ee, evo = report["engineering_everything"], report["evozeus"]
    print(f"Engineering Everything: 本地 {ee['version']}，GitHub {ee.get('latest') or '未知'}"
          f"{' → 有新版本' if ee['update_available'] else ''}（{ee['branch']}{'，有未提交改动' if ee['dirty'] else ''}）")
    if evo.get("installed"):
        print(f"EvoZeus: 本地 {evo.get('version')}，{evo.get('channel')} 通道 {evo.get('latest') or '未知'}"
              f"{' → 有新版本' if evo['update_available'] else ''}")
    else:
        print("EvoZeus: 未安装")
    for line in summary_lines(report):
        print(f"- {line}")
    for error in report["errors"]:
        print(f"! 无法检查 {error}")


# ---------- hook ----------

def run_hook(host: str) -> int:
    if os.environ.get("EE_UPDATE_CHECK", "1") == "0":
        return 0
    try:
        hook_input = json.loads(sys.stdin.read() or "{}") if not sys.stdin.isatty() else {}
    except ValueError:
        hook_input = {}
    if hook_input.get("source") not in (None, "startup", "resume", "clear"):
        return 0
    try:
        lines = summary_lines(build_report())
    except Exception:  # a broken check must never block a session
        return 0
    if not lines:
        return 0
    context = (
        "Engineering Everything update check: " + " ".join(lines)
        + " Mention this to the user once, in one plain sentence, only if relevant to the task; do not update without their OK."
    )
    print(json.dumps({
        "systemMessage": "[EE] " + " ".join(lines),
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
    }, ensure_ascii=False))
    return 0


# ---------- hook install ----------

def hook_command(host: str) -> str:
    return f"/usr/bin/python3 \"{Path(__file__).resolve()}\" hook --host {host}"


def config_path(host: str) -> Path:
    return Path.home() / (".claude/settings.json" if host == "claude" else ".codex/hooks.json")


def is_ours(entry: dict) -> bool:
    return any(HOOK_MARKER in str(h.get("command", "")) for h in entry.get("hooks", []) if isinstance(h, dict))


def update_hook_config(host: str, install: bool, dry_run: bool) -> str:
    path = config_path(host)
    if not path.parent.exists():
        return f"skip {host}: {path.parent} not found"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    hooks = data.setdefault("hooks", {})
    entries = [e for e in hooks.get("SessionStart", []) if isinstance(e, dict) and not is_ours(e)]
    if install:
        entries.append({
            "matcher": "startup|resume",
            "hooks": [{"type": "command", "command": hook_command(host), "timeout": 15,
                       **({"statusMessage": "Checking EE / EvoZeus versions"} if host == "codex" else {})}],
        })
    if entries:
        hooks["SessionStart"] = entries
    else:
        hooks.pop("SessionStart", None)
    action = "install" if install else "uninstall"
    if dry_run:
        return f"would {action} {host} hook in {path}"
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak-ee-update-check"))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return f"{action}ed {host} hook in {path}"


def targets(value: str) -> list[str]:
    return ["claude", "codex"] if value == "both" else [value]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check EE and EvoZeus versions against GitHub.")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--json", action="store_true")
    check.add_argument("--force", action="store_true", help="Ignore the throttle cache.")
    hook = sub.add_parser("hook")
    hook.add_argument("--host", choices=["claude", "codex"], required=True)
    for name in ("install-hook", "uninstall-hook"):
        p = sub.add_parser(name)
        p.add_argument("--target", choices=["claude", "codex", "both"], default="both")
        p.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "hook":
        return run_hook(args.host)
    if args.command in ("install-hook", "uninstall-hook"):
        for host in targets(args.target):
            print(update_hook_config(host, args.command == "install-hook", args.dry_run))
        return 0
    report = build_report(force=args.force)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
