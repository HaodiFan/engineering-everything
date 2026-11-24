#!/usr/bin/env python3
"""Script-driven post-development review orchestrator for Engineering Everything.

Features:
  - Dynamic config layering: base data/review_pipeline.json + private/project/CLI overlays
  - Declarative phase/lane/rule DAG (no hardcoded review step topology)
  - Itemized rule accounting (RV-*, UX-*, or custom ORG-*/PRJ-* rule IDs)
  - Concurrent-safe per-lane atomic submissions + append-only process logs (events.jsonl & progress.log)
  - Real-time milestone progress board on every transition + `log` / `start` / `catalog` commands

Protocol: references/review-pipeline.md | Rules: references/review-rules.md
Config: data/review_pipeline.json | Overlay schema: schemas/review-overlay.schema.json
Exit codes:
  catalog/init/status/next/prompt/start/submit/log/recheck: 0 ok, 2 validation/usage error
  finalize: 0 READY, 1 NOT_READY or INSUFFICIENT_EVIDENCE, 2 invalid/incomplete run
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = EE_ROOT / "data" / "review_pipeline.json"
REFERENCES_DIR = EE_ROOT / "references"

VALID_MODES = ("pr", "delivery", "release", "audit")
VALID_LEVELS = ("L0", "L1", "L2", "L3")
VALID_MATERIALS = ("auto", "code", "runnable", "prototype", "screenshot", "video")
VALID_LANE_STATUSES = ("PASS", "FAIL", "BLOCKED", "N/A")
VALID_SEVERITIES = ("P0", "P1", "P2", "P3", "blocking", "major", "minor", "suggestion")
BLOCKING_SEVERITIES = {"P0", "P1", "blocking"}
SEVERITY_RANK = {
    "P0": 0, "blocking": 0, "P1": 1, "major": 2, "P2": 2, "minor": 3, "P3": 3, "suggestion": 4,
}
RULE_ID_RE = re.compile(r"^(?:[A-Z][A-Z0-9]{1,7}-[A-Z0-9]+-\d{2,3}|AP-0[1-8])$")

PRODUCT_ANTI_PATTERNS: list[tuple[str, str]] = [
    ("AP-01", "Module-Driven UI（模块驱动界面）"),
    ("AP-02", "Broken Journey（旅程碎片化）"),
    ("AP-03", "Context Loss（上下文丢失）"),
    ("AP-04", "Wrong Sequence（步骤顺序错位）"),
    ("AP-05", "Premature Decision（过早/盲目决策）"),
    ("AP-06", "Missing Next Action（主入口或下一步缺失）"),
    ("AP-07", "Cognitive Overload（内部复杂性转嫁/流程阻塞）"),
    ("AP-08", "Frequency Mismatch（高低频权重错位）"),
]
ANTI_PATTERN_IDS = {ap_id for ap_id, _ in PRODUCT_ANTI_PATTERNS}

UX_GROUPS: list[tuple[str, str, int]] = [
    ("UX-META", "审计纪律", 5),
    ("UX-FLOW", "任务流程", 3),
    ("UX-IA", "导航与位置", 5),
    ("UX-VIS", "视觉层级与布局", 9),
    ("UX-TYPE", "排版文案", 6),
    ("UX-COLOR", "颜色与对比度", 5),
    ("UX-FORM", "表单与组件", 8),
    ("UX-STATE", "状态与数据反馈", 6),
    ("UX-RISK", "风险与权限控制", 5),
    ("UX-MOTION", "动效与反馈", 3),
    ("UX-PERF", "感知性能", 2),
    ("UX-RESP", "响应式适配", 4),
    ("UX-A11Y", "无障碍", 6),
    ("UX-RES", "研究检查", 3),
]
UX_RULE_ID_RE = re.compile(r"^UX-[A-Z0-9]+-\d{2}$")

WALKTHROUGH_OBSERVATION_KEYS: list[tuple[str, str]] = [
    ("entry_clarity", "首次进入是否知道从哪里开始"),
    ("action_discoverability", "能否独立发现正确操作"),
    ("module_burden", "是否被迫理解内部模块划分"),
    ("async_non_blocking", "等待/异步处理期间能否做其他工作"),
    ("context_recovery", "跨页/中断/分析完成后能否找回上下文"),
    ("next_step_clarity", "完成一步后是否知道下一步做什么"),
    ("goal_achieved", "最终是否真正达成用户目标"),
]
VALID_OBSERVATION_STATUSES = ("PASS", "FAIL", "FRICTION", "UNVERIFIED", "N/A")

STYLE_ONLY_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
COPY_ONLY_TOKENS = ("locales/", "i18n/", "/copy.", "copy.ts", "copy.json", "strings.", ".po", ".pot")
UI_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".sass", ".less", ".html", ".astro"}
CODE_EXTENSIONS = UI_EXTENSIONS | {
    ".py", ".ts", ".js", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".swift", ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".sql", ".sh",
}
DEFAULT_SIGNAL_PATTERNS: dict[str, list[str]] = {
    "arch_data": [
        "migration", "alembic", "prisma", "schema", "models", "database", "db/",
        "state_machine", "workflow", "constitution.md", "architecture.md", "docs/decisions/", "adr-",
        "permission", "rbac", "policy",
    ],
    "security": [
        "auth", "login", "oauth", "jwt", "session", "token", "secret", "crypto", "encrypt",
        "payment", "billing", "checkout", "pii", "privacy", "permission", "acl", "rbac",
        ".env", "webhook", "signature", "rpa", "scraper", "crawler",
    ],
    "dx": ["cli", "sdk", "openapi", "swagger", "graphql", "proto", "readme.md", "docs/", "api/", "routes/", "router", "endpoints"],
    "ai_automation": ["prompt", "llm", "agent", "openai", "anthropic", "gemini", "ocr", "paddle", "yolo", "cv/", "vision", "rpa", "selenium", "playwright", "eval", "rag"],
    "release": ["dockerfile", "docker-compose", ".github/workflows", "helm", "k8s", "terraform", "deploy", "changelog", "release", "migration", "alembic", "package.json", "pyproject.toml"],
    "ui_interactive": ["form", "submit", "modal", "dialog", "wizard", "step", "checkout", "approval", "auth", "login", "role", "permission", "retry", "async", "query", "mutation", "store", "state"],
    "journey_surface": [
        "pages/", "views/", "screens/", "routes/", "router", "navigation", "navbar", "sidebar", "layout",
        "workspace", "workbench", "dashboard", "home", "inbox", "feed", "tabs", "wizard", "onboarding",
        "flow", "workflow", "checkout", "approval", "drawer", "modal", "task", "notification", "decision",
    ],
}
SECRET_LINE_REGEXES = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("hardcoded-secret", re.compile(r"(?i)\b(?:api_key|secret_key|access_token|password|private_key)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]")),
]
TOOL_UNAVAILABLE_KEYWORDS = (
    "missing", "not found", "not installed", "unavailable", "no cli", "offline",
    "network", "timeout", "timed out", "cannot isolate", "not isolated", "interrupted",
    "缺失", "不可用", "未安装", "装不上", "无网络", "断网", "超时", "无法隔离", "未隔离", "中断",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def short_ts(iso_str: str | None = None) -> str:
    s = iso_str or now_iso()
    return s[11:19] if len(s) >= 19 else s


def load_base_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_gate_check_module() -> Any:
    path = EE_ROOT / "scripts" / "gate_check.py"
    spec = importlib.util.spec_from_file_location("ee_gate_check", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["ee_gate_check"] = module
    spec.loader.exec_module(module)
    return module


def load_html_renderer_module() -> Any:
    path = EE_ROOT / "scripts" / "review_report_html.py"
    spec = importlib.util.spec_from_file_location("ee_review_report_html", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["ee_review_report_html"] = module
    spec.loader.exec_module(module)
    return module


def lane_validators(lane_obj: dict[str, Any]) -> list[str]:
    vals = list(lane_obj.get("validators") or [])
    if lane_obj.get("validator") and lane_obj["validator"] not in vals:
        vals.append(lane_obj["validator"])
    return vals


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def atomic_append_line(path: Path, line: str) -> None:
    """POSIX O_APPEND single-line write so concurrent subagent logs never interleave."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (line.rstrip("\n") + "\n").encode("utf-8")
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def record_event(run_dir: Path, event_type: str, message: str, *, round_num: int, lane_id: str | None = None, phase_id: str | None = None, status: str | None = None, details: dict[str, Any] | None = None) -> dict[str, Any]:
    evt = {
        "ts": now_iso(),
        "round": round_num,
        "event": event_type,
        "phase_id": phase_id,
        "lane_id": lane_id,
        "status": status,
        "message": message,
        "details": details or {},
    }
    atomic_append_line(run_dir / "events.jsonl", json.dumps(evt, ensure_ascii=False))
    atomic_append_line(run_dir / "progress.log", f"[{short_ts(evt['ts'])}][R{round_num}] {message}")
    return evt


def read_events(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "events.jsonl"
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    return events


def discover_overlay_paths(target: Path | None, explicit_overlays: list[str] | None, no_auto_overlays: bool = False) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    if not no_auto_overlays:
        env_assets = os.environ.get("EE_PRIVATE_ASSETS", "").strip()
        if env_assets:
            priv_root = Path(env_assets).resolve()
            if (priv_root / "review_pipeline.json").is_file():
                found.append(("private", priv_root / "review_pipeline.json"))
            if (priv_root / "review_overlays").is_dir():
                for p in sorted((priv_root / "review_overlays").glob("*.json")):
                    found.append(("private", p))
        if target and target.exists():
            evo = target / ".evolution"
            if (evo / "review_pipeline.json").is_file():
                found.append(("project", evo / "review_pipeline.json"))
            if (evo / "review_overlays").is_dir():
                for p in sorted((evo / "review_overlays").glob("*.json")):
                    found.append(("project", p))
    for raw in explicit_overlays or []:
        p = Path(raw).resolve()
        if not p.is_file():
            raise ValueError(f"overlay file not found: {raw}")
        found.append(("cli", p))
    return found


def merge_effective_config(
    target: Path | None,
    explicit_overlays: list[str] | None = None,
    no_auto_overlays: bool = False,
    enable_lanes: list[str] | None = None,
    disable_lanes_cli: list[str] | None = None,
) -> dict[str, Any]:
    """Compose base pipeline + private/project/CLI overlays with hard-gate protection."""
    cfg = copy.deepcopy(load_base_config())
    for p in cfg["phases"]:
        p.setdefault("source", "base")
    for l in cfg["lanes"]:
        l.setdefault("source", "base")
        for r in l.get("rules", []):
            r.setdefault("source", "base")

    signal_patterns = copy.deepcopy(DEFAULT_SIGNAL_PATTERNS)
    applied_overlays: list[dict[str, str]] = []
    force_require_lanes: set[str] = set()
    disabled_lanes: dict[str, str] = {}
    disabled_rules: dict[str, str] = {}

    phases_by_id = {p["id"]: p for p in cfg["phases"]}
    lanes_by_id = {l["id"]: l for l in cfg["lanes"]}

    def resolve_ref_path(raw: str, overlay_dir: Path) -> str:
        p = Path(raw)
        if p.is_absolute():
            return str(p)
        candidate = (overlay_dir / p).resolve()
        return str(candidate) if candidate.exists() else raw

    for layer, path in discover_overlay_paths(target, explicit_overlays, no_auto_overlays):
        try:
            ov = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid overlay JSON {path}: {exc}") from exc
        if not isinstance(ov, dict) or not str(ov.get("name", "")).strip():
            raise ValueError(f"overlay {path} must be a JSON object with a non-empty 'name'")
        ov_tag = f"{layer}:{ov['name']}"
        applied_overlays.append({"layer": layer, "name": str(ov["name"]), "path": str(path)})

        # 1. signal_patterns
        for bucket, pats in (ov.get("signal_patterns") or {}).items():
            if isinstance(pats, list):
                signal_patterns.setdefault(bucket, [])
                for pat in pats:
                    s = str(pat).strip().lower()
                    if s and s not in signal_patterns[bucket]:
                        signal_patterns[bucket].append(s)

        # 2. add_phases
        for ph in ov.get("add_phases") or []:
            if not isinstance(ph, dict) or not ph.get("id"):
                raise ValueError(f"overlay {ov_tag}: add_phases item missing id")
            pid = str(ph["id"])
            if pid in phases_by_id:
                phases_by_id[pid].update({k: v for k, v in ph.items() if k != "id"})
            else:
                new_ph = {
                    "id": pid,
                    "order": ph.get("order", 2.5),
                    "title": ph.get("title", pid),
                    "goal": ph.get("goal", ""),
                    "allow_parallel": bool(ph.get("allow_parallel", True)),
                    "source": ov_tag,
                }
                cfg["phases"].append(new_ph)
                phases_by_id[pid] = new_ph

        # 3. add_lanes
        for lane in ov.get("add_lanes") or []:
            if not isinstance(lane, dict) or not lane.get("id") or not lane.get("phase") or not lane.get("rules"):
                raise ValueError(f"overlay {ov_tag}: add_lanes item requires id, phase, and non-empty rules[]")
            lid = str(lane["id"])
            if lane["phase"] not in phases_by_id:
                raise ValueError(f"overlay {ov_tag}: lane '{lid}' references unknown phase '{lane['phase']}'")
            if lid in lanes_by_id:
                raise ValueError(f"overlay {ov_tag}: lane '{lid}' already exists; use extend_lanes instead")
            rules_norm: list[dict[str, Any]] = []
            for r in lane["rules"]:
                rid = str(r.get("id", "")).strip()
                if not RULE_ID_RE.match(rid):
                    raise ValueError(f"overlay {ov_tag}: invalid rule id '{rid}' in lane '{lid}'")
                rules_norm.append({
                    "id": rid,
                    "title": str(r.get("title", rid)),
                    "check": str(r.get("check", "")),
                    "allow_na": bool(r.get("allow_na", True)),
                    **({"trigger_signals": r["trigger_signals"]} if r.get("trigger_signals") else {}),
                    **({"na_reason_default": r["na_reason_default"]} if r.get("na_reason_default") else {}),
                    "source": ov_tag,
                })
            new_lane = {
                "id": lid,
                "phase": lane["phase"],
                "title": lane.get("title", lid),
                "owner_skill": lane.get("owner_skill", "engineering-review-release"),
                "gate_steps": list(lane.get("gate_steps", [])),
                "review_roles": list(lane.get("review_roles", [])),
                "depends_on": list(lane.get("depends_on", [])),
                "upstream_notes": dict(lane.get("upstream_notes", {})),
                "can_parallel": bool(lane.get("can_parallel", True)),
                "allow_na": bool(lane.get("allow_na", True)),
                "never_waived": bool(lane.get("never_waived", False)),
                "always_required": bool(lane.get("always_required", False)),
                "requires_code_change": bool(lane.get("requires_code_change", False)),
                "required_in_modes": list(lane.get("required_in_modes", [])),
                "exclude_in_modes": list(lane.get("exclude_in_modes", [])),
                "trigger_signals": list(lane.get("trigger_signals", [])),
                "trigger_path_patterns": [str(x).lower() for x in lane.get("trigger_path_patterns", [])],
                "recheck_policy": lane.get("recheck_policy", "on_file_match"),
                "na_reason_default": lane.get("na_reason_default", f"未命中自定义模块 {lid} 触发条件。"),
                "reference_slices": list(lane.get("reference_slices", [])),
                "reference_files": [resolve_ref_path(str(rf), path.parent) for rf in lane.get("reference_files", [])],
                "anti_rationalizations": list(lane.get("anti_rationalizations", [])),
                "rules": rules_norm,
                "source": ov_tag,
            }
            cfg["lanes"].append(new_lane)
            lanes_by_id[lid] = new_lane

        # 4. extend_lanes
        for lid, ext in (ov.get("extend_lanes") or {}).items():
            if lid not in lanes_by_id:
                raise ValueError(f"overlay {ov_tag}: extend_lanes references unknown lane '{lid}'")
            target_lane = lanes_by_id[lid]
            existing_rids = {r["id"] for r in target_lane.get("rules", [])}
            for r in ext.get("add_rules") or []:
                rid = str(r.get("id", "")).strip()
                if not RULE_ID_RE.match(rid):
                    raise ValueError(f"overlay {ov_tag}: invalid rule id '{rid}' in extend_lanes.{lid}")
                if rid in existing_rids:
                    raise ValueError(f"overlay {ov_tag}: duplicate rule id '{rid}' in lane '{lid}'")
                existing_rids.add(rid)
                target_lane["rules"].append({
                    "id": rid,
                    "title": str(r.get("title", rid)),
                    "check": str(r.get("check", "")),
                    "allow_na": bool(r.get("allow_na", True)),
                    **({"trigger_signals": r["trigger_signals"]} if r.get("trigger_signals") else {}),
                    **({"na_reason_default": r["na_reason_default"]} if r.get("na_reason_default") else {}),
                    "source": ov_tag,
                })
            for dep in ext.get("add_depends_on") or []:
                if dep not in target_lane["depends_on"]:
                    target_lane["depends_on"].append(dep)
            target_lane.setdefault("reference_files", [])
            for rf in ext.get("add_reference_files") or []:
                target_lane["reference_files"].append(resolve_ref_path(str(rf), path.parent))
            for ar in ext.get("add_anti_rationalizations") or []:
                target_lane["anti_rationalizations"].append(str(ar))
            if ext.get("trigger_path_patterns"):
                target_lane.setdefault("trigger_path_patterns", [])
                target_lane["trigger_path_patterns"].extend(str(x).lower() for x in ext["trigger_path_patterns"])

        # 5. force_require_lanes / disable_lanes / disable_rules
        for lid in ov.get("force_require_lanes") or []:
            if lid not in lanes_by_id:
                raise ValueError(f"overlay {ov_tag}: force_require_lanes references unknown lane '{lid}'")
            force_require_lanes.add(lid)
        for lid, reason in (ov.get("disable_lanes") or {}).items():
            if lid not in lanes_by_id:
                raise ValueError(f"overlay {ov_tag}: disable_lanes references unknown lane '{lid}'")
            if lanes_by_id[lid].get("never_waived"):
                raise ValueError(f"overlay {ov_tag}: cannot disable hard gate lane '{lid}' (never_waived=true)")
            if not str(reason).strip():
                raise ValueError(f"overlay {ov_tag}: disable_lanes.{lid} requires a non-empty reason")
            disabled_lanes[lid] = f"[{ov_tag}] {str(reason).strip()}"
        for rid, reason in (ov.get("disable_rules") or {}).items():
            owner = next((l for l in cfg["lanes"] if any(r["id"] == rid for r in l.get("rules", []))), None)
            if owner is None:
                raise ValueError(f"overlay {ov_tag}: disable_rules references unknown rule '{rid}'")
            rule_obj = next(r for r in owner["rules"] if r["id"] == rid)
            if owner.get("never_waived") and not rule_obj.get("allow_na", True):
                raise ValueError(f"overlay {ov_tag}: cannot disable hard rule '{rid}' on never_waived lane '{owner['id']}'")
            if not str(reason).strip():
                raise ValueError(f"overlay {ov_tag}: disable_rules.{rid} requires a non-empty reason")
            disabled_rules[rid] = f"[{ov_tag}] {str(reason).strip()}"

    for lid in enable_lanes or []:
        if lid not in lanes_by_id:
            raise ValueError(f"--enable-lane unknown lane: {lid}")
        disabled_lanes.pop(lid, None)
        force_require_lanes.add(lid)

    for raw in disable_lanes_cli or []:
        lid, _, reason = raw.partition(":")
        lid = lid.strip()
        reason = reason.strip() or "CLI --disable-lane"
        if lid not in lanes_by_id:
            raise ValueError(f"--disable-lane unknown lane: {lid}")
        if lanes_by_id[lid].get("never_waived"):
            raise ValueError(f"--disable-lane cannot disable hard gate lane '{lid}' (never_waived=true)")
        force_require_lanes.discard(lid)
        disabled_lanes[lid] = f"[cli] {reason}"

    cfg["phases"].sort(key=lambda p: p["order"])
    cfg["signal_patterns"] = signal_patterns
    cfg["applied_overlays"] = applied_overlays
    cfg["force_require_lanes"] = sorted(force_require_lanes)
    cfg["disabled_lanes"] = disabled_lanes
    cfg["disabled_rules"] = disabled_rules
    return cfg


def run_git(target: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(target), *args], capture_output=True, text=True, check=False)


def detect_git_root(target: Path) -> Path | None:
    if not target.exists():
        return None
    proc = run_git(target, ["rev-parse", "--show-toplevel"])
    return Path(proc.stdout.strip()).resolve() if proc.returncode == 0 else None


def detect_git_common_dir(git_root: Path) -> Path | None:
    proc = run_git(git_root, ["rev-parse", "--git-common-dir"])
    if proc.returncode != 0:
        return None
    raw = Path(proc.stdout.strip())
    return raw if raw.is_absolute() else (git_root / raw).resolve()


def resolve_base_ref(git_root: Path, requested_base: str | None) -> str:
    if requested_base:
        return "WORKTREE" if requested_base.upper() == "WORKTREE" else requested_base
    head_sha = run_git(git_root, ["rev-parse", "HEAD"]).stdout.strip()
    for candidate in ("origin/main", "main", "origin/master", "master"):
        check = run_git(git_root, ["rev-parse", "--verify", candidate])
        if check.returncode == 0 and check.stdout.strip() != head_sha:
            return candidate
    if run_git(git_root, ["rev-parse", "--verify", "HEAD~1"]).returncode == 0:
        return "HEAD~1"
    return "WORKTREE"


def compute_workspace_fingerprint(git_root: Path | None, head_sha: str) -> str:
    if git_root is None:
        return f"nogit:{head_sha}"
    diff_proc = run_git(git_root, ["diff", "HEAD", "--binary"])
    digest = hashlib.sha256(diff_proc.stdout.encode("utf-8", errors="replace")).hexdigest()[:12]
    return f"{head_sha}:{digest}"


def parse_git_state(git_root: Path, base_ref: str | None, explicit_files: list[str] | None = None) -> dict[str, Any]:
    head_proc = run_git(git_root, ["rev-parse", "--short=12", "HEAD"])
    head_sha = head_proc.stdout.strip() if head_proc.returncode == 0 else "UNCOMMITTED"
    branch_proc = run_git(git_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "HEAD"
    resolved_base = resolve_base_ref(git_root, base_ref)

    changed_files: list[str] = []
    added_lines = 0
    deleted_lines = 0
    diff_text_for_probe = ""

    if explicit_files:
        changed_files = sorted({f.strip() for f in explicit_files if f.strip()})
    else:
        file_set: set[str] = set()
        if resolved_base != "WORKTREE":
            names = run_git(git_root, ["diff", "--name-only", f"{resolved_base}...HEAD"])
            if names.returncode != 0:
                names = run_git(git_root, ["diff", "--name-only", resolved_base, "HEAD"])
            if names.returncode == 0:
                file_set.update(line.strip() for line in names.stdout.splitlines() if line.strip())
            numstat = run_git(git_root, ["diff", "--numstat", f"{resolved_base}...HEAD"])
            if numstat.returncode != 0:
                numstat = run_git(git_root, ["diff", "--numstat", resolved_base, "HEAD"])
            if numstat.returncode == 0:
                for line in numstat.stdout.splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                        added_lines += int(parts[0])
                        deleted_lines += int(parts[1])
            patch = run_git(git_root, ["diff", "--unified=0", f"{resolved_base}...HEAD"])
            if patch.returncode == 0:
                diff_text_for_probe += patch.stdout

        wt_names = run_git(git_root, ["diff", "--name-only", "HEAD"])
        if wt_names.returncode == 0:
            file_set.update(line.strip() for line in wt_names.stdout.splitlines() if line.strip())
        wt_numstat = run_git(git_root, ["diff", "--numstat", "HEAD"])
        if wt_numstat.returncode == 0 and (resolved_base == "WORKTREE" or added_lines == 0):
            for line in wt_numstat.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    added_lines += int(parts[0])
                    deleted_lines += int(parts[1])
        wt_patch = run_git(git_root, ["diff", "--unified=0", "HEAD"])
        if wt_patch.returncode == 0:
            diff_text_for_probe += "\n" + wt_patch.stdout
        changed_files = sorted(file_set)

    dirty_files = [line for line in run_git(git_root, ["status", "--short"]).stdout.splitlines() if line.strip()]
    diff_check_proc = run_git(git_root, ["diff", "--check"])
    diff_check_issues = [line for line in diff_check_proc.stdout.splitlines() if line.strip()][:20]

    secret_clues: list[dict[str, str]] = []
    current_file = ""
    for line in diff_text_for_probe.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        lower_file = current_file.lower()
        if any(m in lower_file for m in (".example", "test", "fixture", "mock", "spec", ".md")):
            continue
        for kind, regex in SECRET_LINE_REGEXES:
            if regex.search(line[1:]):
                secret_clues.append({"file": current_file or "<diff>", "kind": kind})
                if len(secret_clues) >= 10:
                    break
        if len(secret_clues) >= 10:
            break

    total_diff = added_lines + deleted_lines
    if total_diff > 1000:
        size_tier = ">1000 (split required unless approved mechanical migration)"
    elif total_diff > 500:
        size_tier = "500-1000 (split recommended or justify single topic)"
    elif total_diff > 300:
        size_tier = "300-500 (explain single-topic cohesion in PR body)"
    elif total_diff >= 100:
        size_tier = "100-300 (ideal PR range)"
    else:
        size_tier = "<100 (small change)"

    return {
        "is_git_repo": True,
        "git_root": str(git_root),
        "branch": branch,
        "base_ref": resolved_base,
        "head_sha": head_sha,
        "workspace_fingerprint": compute_workspace_fingerprint(git_root, head_sha),
        "changed_files": changed_files,
        "dirty_files": dirty_files,
        "diff_stats": {"files_changed": len(changed_files), "added": added_lines, "deleted": deleted_lines, "total": total_diff, "size_tier": size_tier},
        "pre_probes": {"git_diff_check_ok": diff_check_proc.returncode == 0, "git_diff_check_issues": diff_check_issues, "secret_clues": secret_clues},
    }


def load_intent_card_context(intent_card: str | None) -> dict[str, Any]:
    """Load optional journeys/goal/scenario from a JSON Intent Card file if present."""
    if not intent_card:
        return {"journeys": [], "goal": "", "user_and_scenario": ""}
    path = Path(intent_card)
    if not path.is_file():
        return {"journeys": [], "goal": "", "user_and_scenario": ""}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"journeys": [], "goal": "", "user_and_scenario": ""}
    if not isinstance(data, dict):
        return {"journeys": [], "goal": "", "user_and_scenario": ""}
    raw_journeys = data.get("journeys")
    journeys = [j for j in raw_journeys if isinstance(j, dict)] if isinstance(raw_journeys, list) else []
    return {
        "journeys": journeys,
        "goal": str(data.get("goal") or "").strip(),
        "user_and_scenario": str(data.get("user_and_scenario") or "").strip(),
    }


def detect_repo_and_signals(
    target: Path,
    git_info: dict[str, Any],
    effective_cfg: dict[str, Any],
    mode: str,
    level: str,
    material: str,
    ui_interactive_override: bool | None,
    has_release_flag: bool,
    intent_card: str | None,
    journey_override: bool | None = None,
) -> dict[str, Any]:
    changed = git_info.get("changed_files", [])
    lower_files = [f.lower() for f in changed]
    sp = effective_cfg["signal_patterns"]
    intent_ctx = load_intent_card_context(intent_card)
    intent_journeys = intent_ctx["journeys"]

    def any_ext(exts: set[str]) -> bool:
        return any(Path(f).suffix.lower() in exts for f in changed)

    def any_pat(bucket: str) -> bool:
        pats = sp.get(bucket, [])
        return any(any(pat in lf for pat in pats) for lf in lower_files)

    is_react_repo = False
    react_packages: list[str] = []
    if target.exists() and target.is_dir():
        pkg_candidates = [target / "package.json"]
        for sub in ("apps", "packages", "web", "frontend", "client"):
            sub_dir = target / sub
            if sub_dir.is_dir():
                pkg_candidates.extend(sorted(sub_dir.glob("*/package.json"))[:8])
                if (sub_dir / "package.json").exists():
                    pkg_candidates.append(sub_dir / "package.json")
        seen: set[Path] = set()
        for pkg_path in pkg_candidates:
            if not pkg_path.exists() or pkg_path in seen:
                continue
            seen.add(pkg_path)
            try:
                pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            deps: dict[str, Any] = {}
            for sec in ("dependencies", "devDependencies", "peerDependencies"):
                if isinstance(pkg_data.get(sec), dict):
                    deps.update(pkg_data[sec])
            if any(k in deps for k in ("react", "react-dom", "next", "react-native", "expo")):
                is_react_repo = True
                try:
                    react_packages.append(str(pkg_path.relative_to(target)))
                except ValueError:
                    react_packages.append(str(pkg_path))

    has_ui_files = any_ext(UI_EXTENSIONS) or any(
        any(tok in lf for tok in ("components/", "pages/", "views/", "screens/", "ui/", "frontend/", "design.md"))
        for lf in lower_files
    )
    has_code_change = bool(changed) and (any_ext(CODE_EXTENSIONS) or mode != "audit")
    if mode == "audit" and not changed:
        has_code_change = False

    has_ui_change = has_ui_files or mode == "audit" or material in ("runnable", "prototype", "screenshot", "video")
    is_react = (
        is_react_repo
        and has_code_change
        and (has_ui_files or any(Path(f).suffix.lower() in {".ts", ".tsx", ".js", ".jsx"} for f in changed))
    ) or any(Path(f).suffix.lower() in {".tsx", ".jsx"} for f in changed)

    resolved_material = ("runnable" if has_ui_change else "code") if material == "auto" else material
    if ui_interactive_override is not None:
        has_complex_ui_flow: bool | str = ui_interactive_override
    elif resolved_material == "screenshot":
        has_complex_ui_flow = False
    elif has_ui_change and any_pat("ui_interactive"):
        has_complex_ui_flow = True
    elif has_ui_change:
        has_complex_ui_flow = "unknown"
    else:
        has_complex_ui_flow = False

    has_security_surface = any_pat("security")
    non_trivial_ui_files = [
        f for f in changed
        if (Path(f).suffix.lower() in UI_EXTENSIONS and Path(f).suffix.lower() not in STYLE_ONLY_EXTENSIONS)
        and not any(tok in f.lower() for tok in COPY_ONLY_TOKENS)
    ]
    if journey_override is not None:
        has_journey_surface = journey_override
    elif intent_journeys:
        has_journey_surface = True
    elif non_trivial_ui_files and (any_pat("journey_surface") or any_pat("ui_interactive")):
        has_journey_surface = True
    else:
        has_journey_surface = False

    effective_level = level
    level_bump_reason = ""
    if has_security_surface and level == "L0":
        effective_level = "L1"
        level_bump_reason = "涉及安全/权限/数据相关改动，按 delivery-gates.md 不得按 L0 处理，自动升至 L1。"

    governance_docs: list[str] = []
    if target.exists() and target.is_dir():
        for doc in ("CONSTITUTION.md", "ARCHITECTURE.md", "DESIGN.md", "BRANCHING.md", "AGENTS.md"):
            if (target / doc).exists():
                governance_docs.append(doc)
        active_design = target / "docs" / "design" / "active"
        if active_design.is_dir():
            governance_docs.extend(str(p.relative_to(target)) for p in sorted(active_design.glob("*.md"))[:5])

    private_assets_sources: list[str] = []
    if target.exists() and (target / ".evolution").exists():
        private_assets_sources.append(str((target / ".evolution").resolve()))
    env_assets = os.environ.get("EE_PRIVATE_ASSETS", "").strip()
    if env_assets and Path(env_assets).exists():
        private_assets_sources.append(str(Path(env_assets).resolve()))

    design_principle_docs: list[dict[str, str]] = []
    seen_design_paths: set[Path] = set()

    def _add_design_doc(layer: str, p: Path) -> None:
        if not p.is_file():
            return
        rp = p.resolve()
        if rp in seen_design_paths:
            return
        seen_design_paths.add(rp)
        design_principle_docs.append({"layer": layer, "name": p.name, "path": str(rp)})

    if env_assets:
        priv_root = Path(env_assets).resolve()
        for sub in ("design-principles", "taste"):
            if (priv_root / sub).is_dir():
                for md in sorted((priv_root / sub).glob("*.md")):
                    _add_design_doc("private", md)
        _add_design_doc("private", priv_root / "DESIGN.md")
    if target.exists() and target.is_dir():
        for sub in (".evolution/design-principles", ".evolution/taste"):
            if (target / sub).is_dir():
                for md in sorted((target / sub).glob("*.md")):
                    _add_design_doc("project", md)
        _add_design_doc("project", target / "DESIGN.md")

    return {
        "effective_level": effective_level,
        "level_bump_reason": level_bump_reason,
        "material": resolved_material,
        "journeys": intent_journeys,
        "intent_context": intent_ctx,
        "signals": {
            "has_code_change": has_code_change,
            "is_react": is_react,
            "has_ui_change": has_ui_change,
            "has_complex_ui_flow": has_complex_ui_flow,
            "has_journey_surface": has_journey_surface,
            "has_arch_or_data_change": any_pat("arch_data"),
            "has_security_surface": has_security_surface,
            "has_dx_surface": any_pat("dx"),
            "has_ai_or_automation": any_pat("ai_automation"),
            "has_release_scope": has_release_flag or mode == "release" or any_pat("release"),
            "is_team_delivery": mode in ("delivery", "release") or bool(intent_card),
            "high_level": effective_level in ("L2", "L3"),
        },
        "repo_context": {
            "is_react_repo": is_react_repo,
            "react_packages": react_packages,
            "governance_docs": governance_docs,
            "private_assets_sources": private_assets_sources,
            "design_principle_docs": design_principle_docs,
            "bombadil_cli_on_path": shutil.which("bombadil"),
        },
        "file_buckets": {
            "react_files": [f for f in changed if Path(f).suffix.lower() in {".tsx", ".jsx", ".ts", ".js"}],
            "ui_files": [f for f in changed if Path(f).suffix.lower() in UI_EXTENSIONS or any(t in f.lower() for t in ("components/", "pages/", "views/", "ui/", "design.md"))],
            "security_files": [f for f in changed if any(p in f.lower() for p in sp.get("security", []))],
            "arch_dx_ai_files": [f for f in changed if any(p in f.lower() for p in sp.get("arch_data", []) + sp.get("dx", []) + sp.get("ai_automation", []))],
            "security_arch_files": [f for f in changed if any(p in f.lower() for p in sp.get("security", []) + sp.get("arch_data", []) + sp.get("dx", []) + sp.get("ai_automation", []))],
            "release_files": [f for f in changed if any(p in f.lower() for p in sp.get("release", []))],
        },
    }


def resolve_lane_rules(
    lane_cfg: dict[str, Any],
    signals: dict[str, Any],
    lane_required: bool,
    disabled_rules: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    active: list[dict[str, Any]] = []
    auto_na: list[dict[str, Any]] = []
    for rule in lane_cfg.get("rules", []):
        rid = rule["id"]
        if rid in disabled_rules:
            auto_na.append({**rule, "auto_na_reason": f"配置禁用: {disabled_rules[rid]}"})
            continue
        if not lane_required:
            auto_na.append({**rule, "auto_na_reason": lane_cfg.get("na_reason_default", "模块未触发")})
            continue
        r_signals = rule.get("trigger_signals")
        if not r_signals or any(signals.get(sig) is True for sig in r_signals):
            active.append(rule)
        else:
            auto_na.append({**rule, "auto_na_reason": rule.get("na_reason_default") or "未命中触发信号"})
    return active, auto_na


def build_plan(effective_cfg: dict[str, Any], mode: str, signals: dict[str, Any], changed_files: list[str]) -> dict[str, Any]:
    """Declaratively build the execution plan from effective_cfg (zero hardcoded lane names)."""
    lower_files = [f.lower() for f in changed_files]
    disabled_lanes = effective_cfg.get("disabled_lanes", {})
    disabled_rules = effective_cfg.get("disabled_rules", {})
    forced_lanes = set(effective_cfg.get("force_require_lanes", []))

    lane_copy_keys = (
        "id", "phase", "title", "dimension_question", "owner_skill", "gate_steps", "review_roles",
        "depends_on", "can_parallel", "allow_na", "never_waived", "validator", "validators",
        "file_bucket", "recheck_policy", "trigger_path_patterns", "source",
    )
    lanes_plan: list[dict[str, Any]] = []
    for lane in effective_cfg["lanes"]:
        lid = lane["id"]
        if lid in disabled_lanes:
            _, auto_na_rules = resolve_lane_rules(lane, signals, False, disabled_rules)
            lanes_plan.append({
                **{k: lane.get(k) for k in lane_copy_keys},
                "required": False,
                "initial_status": "CONFIG_DISABLED",
                "trigger_reasons": [],
                "auto_na_reason": f"配置禁用: {disabled_lanes[lid]}",
                "active_rules": [],
                "auto_na_rules": auto_na_rules,
            })
            continue

        matched_reasons: list[str] = []
        excluded = mode in set(lane.get("exclude_in_modes", []))
        if not excluded:
            if lane.get("always_required") or lid in forced_lanes:
                matched_reasons.append("forced/always_required")
            if mode in set(lane.get("required_in_modes", [])):
                if not lane.get("requires_code_change") or signals.get("has_code_change"):
                    matched_reasons.append(f"mode={mode}")
            for sig in lane.get("trigger_signals", []):
                if signals.get(sig) is True:
                    matched_reasons.append(f"signal:{sig}")
            for pat in lane.get("trigger_path_patterns", []) or []:
                if any(pat in lf for lf in lower_files):
                    matched_reasons.append(f"path:{pat}")

        is_required = bool(matched_reasons)
        active_rules, auto_na_rules = resolve_lane_rules(lane, signals, is_required, disabled_rules)
        if is_required and not active_rules:
            is_required = False

        lanes_plan.append({
            **{k: lane.get(k) for k in lane_copy_keys},
            "required": is_required,
            "initial_status": "PENDING" if is_required else "AUTO_NA",
            "trigger_reasons": matched_reasons,
            "auto_na_reason": "" if is_required else lane.get("na_reason_default", "未命中触发条件"),
            "active_rules": active_rules,
            "auto_na_rules": auto_na_rules,
        })

    return {"phases": effective_cfg["phases"], "lanes": lanes_plan}


def extract_markdown_sections(path: Path, headings: list[str]) -> str:
    if not path.exists():
        return f"_(reference missing: {path})_"
    text = path.read_text(encoding="utf-8")
    if not headings:
        return text.strip()
    lines = text.splitlines()
    selected: list[str] = []
    for target_heading in headings:
        capturing = False
        capture_level = 0
        chunk: list[str] = []
        for line in lines:
            m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if m:
                lvl = len(m.group(1))
                title = m.group(2).strip()
                if capturing and lvl <= capture_level:
                    break
                if not capturing and (title == target_heading or target_heading in title):
                    capturing = True
                    capture_level = lvl
                    chunk.append(line)
                    continue
            if capturing:
                chunk.append(line)
        if chunk:
            selected.append("\n".join(chunk).strip())
    return "\n\n".join(selected) if selected else text[:2500].strip()


def round_dir(run_dir: Path, round_num: int) -> Path:
    return run_dir / "rounds" / f"r{round_num}"


def lane_result_path(run_dir: Path, round_num: int, lane_id: str) -> Path:
    return round_dir(run_dir, round_num) / "lanes" / f"{lane_id}.json"


def lane_prompt_path(run_dir: Path, round_num: int, lane_id: str) -> Path:
    return round_dir(run_dir, round_num) / "prompts" / f"{lane_id}.md"


def lane_blind_prompt_path(run_dir: Path, round_num: int, lane_id: str) -> Path:
    return round_dir(run_dir, round_num) / "prompts" / f"{lane_id}.blind.md"


def lane_prompt_meta_path(run_dir: Path, round_num: int, lane_id: str) -> Path:
    return round_dir(run_dir, round_num) / "prompts" / f"{lane_id}.meta.json"


def lane_started_path(run_dir: Path, round_num: int, lane_id: str) -> Path:
    return round_dir(run_dir, round_num) / "prompts" / f"{lane_id}.started.json"


def load_run_state(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"not a review run directory (missing manifest.json): {run_dir}")
    manifest = read_json(manifest_path)
    cfg_path = run_dir / "effective_config.json"
    effective_cfg = read_json(cfg_path) if cfg_path.exists() else load_base_config()
    rnum = int(manifest["current_round"])
    plan = read_json(round_dir(run_dir, rnum) / "plan.json")
    results: dict[str, dict[str, Any]] = {}
    lanes_dir = round_dir(run_dir, rnum) / "lanes"
    if lanes_dir.exists():
        for path in sorted(lanes_dir.glob("*.json")):
            data = read_json(path)
            results[data["lane_id"]] = data
    return manifest, effective_cfg, plan, results


def current_repo_fingerprint(manifest: dict[str, Any]) -> str:
    if not manifest.get("is_git_repo"):
        return str(manifest.get("workspace_fingerprint"))
    git_root = Path(manifest["git_root"])
    if not git_root.exists():
        return str(manifest.get("workspace_fingerprint"))
    head_proc = run_git(git_root, ["rev-parse", "--short=12", "HEAD"])
    head_sha = head_proc.stdout.strip() if head_proc.returncode == 0 else "UNCOMMITTED"
    return compute_workspace_fingerprint(git_root, head_sha)


def lane_is_settled(state: str) -> bool:
    return state in ("PASS", "FAIL", "BLOCKED", "N/A", "AUTO_NA", "CONFIG_DISABLED")


def lane_effective_state(run_dir: Path, round_num: int, lane_plan: dict[str, Any], results: dict[str, dict[str, Any]]) -> str:
    lid = lane_plan["id"]
    if not lane_plan["required"]:
        return str(lane_plan.get("initial_status") or "AUTO_NA")
    if lid in results:
        return str(results[lid]["status"])
    if lane_started_path(run_dir, round_num, lid).exists():
        return "RUNNING"
    return "PROMPT_ISSUED" if lane_prompt_meta_path(run_dir, round_num, lid).exists() else "PENDING"


def compute_progress(run_dir: Path, manifest: dict[str, Any], plan: dict[str, Any], results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rnum = int(manifest["current_round"])
    live_fp = current_repo_fingerprint(manifest)
    expected_fp = manifest.get("workspace_fingerprint")
    stale_workspace = live_fp != expected_fp

    states = {lp["id"]: lane_effective_state(run_dir, rnum, lp, results) for lp in plan["lanes"]}
    phases_summary: list[dict[str, Any]] = []
    active_phase: dict[str, Any] | None = None
    ready_lanes: list[dict[str, Any]] = []

    for phase in sorted(plan["phases"], key=lambda p: p["order"]):
        p_lanes = [lp for lp in plan["lanes"] if lp["phase"] == phase["id"]]
        req_lanes = [lp for lp in p_lanes if lp["required"]]
        done_lanes = [lp for lp in req_lanes if lane_is_settled(states[lp["id"]])]
        p_complete = len(done_lanes) == len(req_lanes)
        phases_summary.append({
            "id": phase["id"],
            "order": phase["order"],
            "title": phase["title"],
            "allow_parallel": phase["allow_parallel"],
            "complete": p_complete,
            "required_count": len(req_lanes),
            "completed_count": len(done_lanes),
            "lanes": [
                {
                    "id": lp["id"],
                    "title": lp["title"],
                    "source": lp.get("source", "base"),
                    "required": lp["required"],
                    "status": states[lp["id"]],
                    "active_rules_count": len(lp.get("active_rules", [])),
                    "checked_rules_count": len(results.get(lp["id"], {}).get("checks", [])),
                    "can_parallel": lp["can_parallel"],
                    "depends_on": lp["depends_on"],
                    "blocking_findings": sum(
                        1 for f in results.get(lp["id"], {}).get("findings", [])
                        if f.get("severity") in BLOCKING_SEVERITIES
                    ),
                }
                for lp in p_lanes
            ],
        })
        if active_phase is None and not p_complete:
            active_phase = phase
            for lp in req_lanes:
                if not lane_is_settled(states[lp["id"]]) and all(lane_is_settled(states.get(d, "AUTO_NA")) for d in lp["depends_on"]):
                    ready_lanes.append(lp)

    total_required = sum(1 for lp in plan["lanes"] if lp["required"])
    total_completed = sum(1 for lp in plan["lanes"] if lp["required"] and lane_is_settled(states[lp["id"]]))
    total_active_rules = sum(len(lp.get("active_rules", [])) for lp in plan["lanes"] if lp["required"])
    total_checked_rules = sum(len(results[lp["id"]].get("checks", [])) for lp in plan["lanes"] if lp["required"] and lp["id"] in results)
    has_blocking = any(
        res.get("status") == "FAIL" or any(f.get("severity") in BLOCKING_SEVERITIES for f in res.get("findings", []))
        for res in results.values()
    )

    return {
        "run_id": manifest["run_id"],
        "round": rnum,
        "mode": manifest["mode"],
        "level": manifest["level"],
        "head_sha": manifest["head_sha"],
        "workspace_fingerprint": expected_fp,
        "live_fingerprint": live_fp,
        "stale_workspace": stale_workspace,
        "total_required": total_required,
        "total_completed": total_completed,
        "total_active_rules": total_active_rules,
        "total_checked_rules": total_checked_rules,
        "all_complete": total_completed == total_required,
        "has_blocking_findings": has_blocking,
        "active_phase": active_phase,
        "ready_lanes": ready_lanes,
        "phases": phases_summary,
        "states": states,
    }


def render_progress_board(progress: dict[str, Any]) -> str:
    """Compact human-readable live status board showing which steps are done/running/pending."""
    badge = {
        "PASS": "✓ PASS   ",
        "FAIL": "✗ FAIL   ",
        "BLOCKED": "! BLOCKED",
        "N/A": "- N/A    ",
        "RUNNING": "→ RUNNING",
        "PROMPT_ISSUED": "→ READY  ",
        "PENDING": "· PENDING",
        "AUTO_NA": "- AUTO_NA",
        "CONFIG_DISABLED": "- OFF    ",
    }
    lines = [
        f"[R{progress['round']}] Review 进度: {progress['total_completed']}/{progress['total_required']} 模块 · "
        f"{progress['total_checked_rules']}/{progress['total_active_rules']} 规则 "
        f"({progress['mode']}/{progress['level']} @ {progress['head_sha']})"
    ]
    if progress["stale_workspace"]:
        lines.append("  ! WARNING: 工作区代码已变动，旧轮次锁定，请先运行 recheck。")
    for ph in progress["phases"]:
        p_mark = "✓ DONE  " if ph["complete"] else "→ ACTIVE"
        lines.append(f"  [{p_mark}] {ph['title']} ({ph['completed_count']}/{ph['required_count']})")
        for lp in ph["lanes"]:
            st = badge.get(lp["status"], lp["status"])
            rinfo = f" ({lp['checked_rules_count']}/{lp['active_rules_count']})" if lp["required"] else ""
            blk = f" [blocking={lp['blocking_findings']}]" if lp["blocking_findings"] else ""
            src = f" <{lp['source']}>" if lp.get("source") and lp["source"] != "base" else ""
            lines.append(f"      [{st}] {lp['id']:24s}{rinfo}{blk}{src}")
    return "\n".join(lines)


def make_prompt_token(run_id: str, round_num: int, lane_id: str, fp: str) -> str:
    return hashlib.sha256(f"{run_id}|r{round_num}|{lane_id}|{fp}".encode("utf-8")).hexdigest()[:12]


def _lane_meta_example(lane_cfg: dict[str, Any], active_rule_ids: set[str], material: str) -> dict[str, Any]:
    vals = lane_validators(lane_cfg)
    lid = lane_cfg["id"]
    out: dict[str, Any] = {}
    if "bombadil" in vals and any(r.startswith("RV-BOMB-") for r in active_rule_ids):
        out.update({
            "applicability": "applicable | not_applicable",
            "execution_state": "completed_no_violation | violation_found | incomplete | not_applicable",
            "command": "实际运行的 bombadil 命令",
            "budget": "1m",
            "output_path": "./output/bombadil/review-001",
            "exit_code": 0,
        })
    if "react_doctor" in vals and any(r.startswith("RV-REACT-") for r in active_rule_ids):
        out.update({
            "scope": "changed | full | design",
            "no_telemetry": True,
            "no_supply_chain": True,
            "report_path": "path/to/react-doctor.json",
            "new_issues_count": 0,
            "preexisting_debt_count": 0,
            "skipped_files": [],
        })
    if "ui_ux_audit" in vals and any(r.startswith("RV-UI-") for r in active_rule_ids):
        out.update({
            "material_type": material if material in ("runnable", "prototype", "screenshot", "video") else "runnable",
            "unfamiliar_language_check": "PASS | FAIL | N/A | UNVERIFIED",
            "unfamiliar_language_evidence": "原版/陌生语言版及观察者熟悉度说明",
            "company_cases_loaded": False,
            "ux_coverage": {
                prefix: {"passed": total, "failed": 0, "na": 0, "unverified": 0, "failed_ids": [], "unverified_ids": []}
                for prefix, _, total in UX_GROUPS
            },
        })
    if "journey_walkthrough" in vals and "RV-UI-05" in active_rule_ids:
        out["journey_walkthrough"] = {
            "blind_mode": True,
            "actor": "目标用户角色与背景",
            "goal": "用户要完成的真实目标",
            "actual_steps": ["1. 打开入口页...", "2. 找到主操作..."],
            "observations": {
                key: {"status": "PASS | FAIL | FRICTION | UNVERIFIED | N/A", "note": label}
                for key, label in WALKTHROUGH_OBSERVATION_KEYS
            },
            "friction_points": [],
        }
    if lid in ("business_acceptance", "business_functional"):
        out["acceptance"] = [{"id": "AC1", "expected": "预期结果", "actual": "实测结果", "evidence": ["test://..."], "status": "PASS"}]
    if "journey_review" in vals and "RV-BIZ-05" in active_rule_ids:
        out["journey_review"] = {
            "journeys": [{
                "id": "primary-journey",
                "actor": "目标用户角色",
                "goal": "用户想完成的核心目标",
                "expected_stages": ["阶段 1（不含页面/按钮名）", "阶段 2", "阶段 3"],
                "actual_steps": ["实际步骤 1", "实际步骤 2"],
                "gap_summary": "预期旅程与实际路径的对比结论",
                "anti_patterns_checked": {ap_id: "CLEAR | FOUND | N/A" for ap_id, _ in PRODUCT_ANTI_PATTERNS},
                "verdict": "ALIGNED | FRICTION | NEEDS_REDESIGN | UNVERIFIED",
            }]
        }
    if lid == "release_readiness":
        out.update({"rollout": "放量计划", "rollback": "已验证回滚步骤", "monitoring": "业务与技术指标", "business_readiness": "知会对象与兜底"})
    return out


def stitch_blind_walkthrough_prompt(
    run_dir: Path,
    manifest: dict[str, Any],
    lane_id: str,
    token: str,
) -> str:
    """Physically code-free prompt for Blind User Walkthrough (anti-anchoring).

    Deliberately excludes git diff, changed files, source code paths, component names,
    and internal module architecture so the reviewer experiences the product like a real user.
    """
    rnum = int(manifest["current_round"])
    journeys = manifest.get("journeys") or []
    intent_ctx = manifest.get("intent_context") or {}
    lines: list[str] = [
        f"# Blind User Walkthrough Prompt（无源码盲测）— `{lane_id}`",
        "",
        "## 1. 严格防锚定声明（必读）",
        f"- **Run ID**: `{manifest['run_id']}` (Round `{rnum}`) | **Prompt Token**: `{token}`",
        f"- **审查材料**: `{manifest['material']}`" + (f" | **产品入口 URL**: `{manifest['target_url']}`" if manifest.get("target_url") else ""),
        "- **物理隔离红线**：本阶段你是一名**真实的目标用户**。完成走查记录前，**严禁阅读 git diff、源码文件、组件目录、路由表或任何内部模块说明**。",
        "- **不要脑补成功**：找不到入口、需要猜内部模块、等待被阻塞、返回丢上下文，都要如实记为 `FRICTION` 或 `FAIL`；仅截图无法实操的项标 `UNVERIFIED`。",
        "- **证据边界**：你的观察属于自动化认知筛查代理信号，不冒充真实用户可用性测试。",
        "",
        "## 2. 你的角色与要完成的真实任务",
    ]
    if journeys:
        for idx, j in enumerate(journeys, 1):
            lines.append(f"### 任务 {idx}: `{j.get('id', f'journey-{idx}')}`")
            lines.append(f"- **你的身份（Actor）**: {j.get('actor', '目标用户')}")
            lines.append(f"- **触发场景（Trigger）**: {j.get('trigger', '真实业务触发场景')}")
            lines.append(f"- **你想达成的目标（Goal）**: {j.get('goal', '')}")
            constraints = j.get("experience_constraints") or []
            if constraints:
                lines.append("- **体验底线约束**:")
                for c in constraints:
                    lines.append(f"  - {c}")
            lines.append("")
    else:
        scenario = intent_ctx.get("user_and_scenario") or "请先基于产品公开定位明确目标用户身份与真实使用场景（不看代码）。"
        goal = intent_ctx.get("goal") or "请先明确本次面向用户的核心任务目标，再从正常入口尝试独立完成。"
        lines.append(f"- **用户与场景**: {scenario}")
        lines.append(f"- **核心目标**: {goal}")
        lines.append("")

    lines.extend([
        "## 3. 逐项必须记录的 7 项盲测观察点",
        "实际走查后，必须逐一回答以下 7 项（每项给 `PASS` / `FRICTION` / `FAIL` / `UNVERIFIED` / `N/A` 与一手现象笔记）：",
    ])
    for idx, (key, label) in enumerate(WALKTHROUGH_OBSERVATION_KEYS, 1):
        lines.append(f"{idx}. **`{key}`** — {label}")

    lines.extend([
        "",
        "## 4. 盲测产出契约",
        "完成无引导走查并锁定真实步骤 `actual_steps[]`、7 项 `observations` 与 `friction_points[]` 后，再把该结果并入 `ui_ux_experience` 的 `meta.journey_walkthrough` 一同提交（随后才允许阅读主 Prompt 中的源码/Bombadil/70 条细项审计）。",
        "",
        "```json",
        json.dumps({
            "blind_mode": True,
            "actor": journeys[0].get("actor", "目标用户") if journeys else "目标用户",
            "goal": journeys[0].get("goal", "完成核心任务") if journeys else (intent_ctx.get("goal") or "完成核心任务"),
            "actual_steps": ["1. 打开正常入口，观察首屏...", "2. ..."],
            "observations": {
                key: {"status": "PASS | FRICTION | FAIL | UNVERIFIED | N/A", "note": "一手观察现象"}
                for key, _ in WALKTHROUGH_OBSERVATION_KEYS
            },
            "friction_points": ["若存在卡点/迷路/丢上下文，逐条列出"],
        }, ensure_ascii=False, indent=2),
        "```",
    ])
    return "\n".join(lines) + "\n"


def stitch_lane_prompt(
    run_dir: Path,
    manifest: dict[str, Any],
    effective_cfg: dict[str, Any],
    plan: dict[str, Any],
    results: dict[str, dict[str, Any]],
    lane_id: str,
) -> tuple[str, str]:
    lane_cfg = next(item for item in effective_cfg["lanes"] if item["id"] == lane_id)
    lane_plan = next(item for item in plan["lanes"] if item["id"] == lane_id)
    active_rules = lane_plan.get("active_rules", [])
    auto_na_rules = lane_plan.get("auto_na_rules", [])

    rnum = int(manifest["current_round"])
    token = make_prompt_token(manifest["run_id"], rnum, lane_id, manifest["workspace_fingerprint"])
    runner_path = str((EE_ROOT / "scripts" / "review_runner.py").resolve())

    buckets = manifest["file_buckets"]
    changed_files = manifest["changed_files"]
    bucket_name = lane_cfg.get("file_bucket")
    if bucket_name and buckets.get(bucket_name):
        scoped_files = buckets[bucket_name]
    elif lane_cfg.get("trigger_path_patterns"):
        pats = lane_cfg["trigger_path_patterns"]
        matched = [f for f in changed_files if any(p in f.lower() for p in pats)]
        scoped_files = matched or changed_files
    else:
        scoped_files = changed_files

    lines: list[str] = [
        f"# Review Lane Prompt: `{lane_id}` — {lane_cfg['title']}",
        "",
        "## 1. 任务与独立审查声明",
        f"- **Run ID**: `{manifest['run_id']}` (Round `{rnum}`) | **Prompt Token**: `{token}`",
        f"- **Lane ID**: `{lane_id}` | **来源**: `{lane_cfg.get('source', 'base')}` | **本模块必检规则数**: `{len(active_rules)}` 条",
        f"- **Target**: `{manifest['target']}` | **Mode**: `{manifest['mode']}` | **Level**: `{manifest['level']}`",
        f"- **Base / Commit**: `{manifest.get('base_ref', 'N/A')}` -> `{manifest['head_sha']}` (Fingerprint: `{manifest['workspace_fingerprint']}`)",
        f"- **Material**: `{manifest['material']}`" + (f" | **Target URL**: `{manifest['target_url']}`" if manifest.get("target_url") else ""),
        "- **独立性纪律**：你是本模块的**独立只读审查者**。不改目标仓库代码；不信“CI 绿/开发说测过”；必须对下方每一条编号规则逐一给出结论与证据。",
        "",
        "## 2. 本轮范围与前置线索",
    ]
    if manifest.get("intent_card"):
        lines.append(f"- **关联需求卡/Spec**: `{manifest['intent_card']}`")
    if "journey_review" in lane_validators(lane_cfg) and manifest.get("journeys"):
        lines.append(f"- **需求卡声明的预期旅程（Journey Contract，共 {len(manifest['journeys'])} 条，与界面实现解耦）**:")
        for j in manifest["journeys"]:
            stages = " → ".join(str(s) for s in (j.get("stages") or []))
            lines.append(f"  - `{j.get('id', 'journey')}` ({j.get('actor', '')}): 目标={j.get('goal', '')} | 预期阶段: {stages}")
    repo_ctx = manifest["repo_context"]
    if repo_ctx.get("governance_docs"):
        lines.append(f"- **项目治理文档**: {', '.join(f'`{d}`' for d in repo_ctx['governance_docs'])}")
    vals = lane_validators(lane_cfg)
    active_rule_ids = {r["id"] for r in active_rules}
    if repo_ctx.get("private_assets_sources"):
        lines.append(f"- **私有案例/检查配置**: {', '.join(f'`{p}`' for p in repo_ctx['private_assets_sources'])}")
    elif "ui_ux_audit" in vals:
        lines.append("- **私有案例库**: 未检测到 `.evolution/` 或 `EE_PRIVATE_ASSETS`，请在结论注明“没有加载公司案例”。")
    design_docs = repo_ctx.get("design_principle_docs") or []
    if design_docs and ("ui_ux_audit" in vals or ("journey_review" in vals and "RV-BIZ-05" in active_rule_ids)):
        lines.append(
            "- **自动加载的 UI 设计理念 / 审美基准**: "
            + ", ".join(f"`{d['name']}` ({d['layer']})" for d in design_docs)
            + "（全文已自动注入下方第 6 节；评审时须对照核验并设 `meta.company_cases_loaded = true`）"
        )

    ds = manifest.get("diff_stats", {})
    if ds:
        lines.append(f"- **Diff 规模**: {ds.get('files_changed', 0)} 个文件，+{ds.get('added', 0)} / -{ds.get('deleted', 0)} 行（{ds.get('size_tier', 'N/A')}）")
    if scoped_files:
        lines.append(f"- **重点文件（共 {len(scoped_files)} 个）**: " + ", ".join(f"`{f}`" for f in scoped_files[:25]) + (" ..." if len(scoped_files) > 25 else ""))
    else:
        lines.append("- **重点文件**: 无 git 代码 diff（按指定界面材料审查）。")

    pre_probes = manifest.get("pre_probes", {})
    if lane_id in ("engineering_baseline", "baseline_gate") and pre_probes:
        lines.append(f"- **预探针 `git diff --check`**: {'通过' if pre_probes.get('git_diff_check_ok') else '发现问题'}")
        for issue in pre_probes.get("git_diff_check_issues", [])[:5]:
            lines.append(f"  - `{issue}`")
        if manifest.get("dirty_files"):
            lines.append(f"- **未提交工作区条目**: {len(manifest['dirty_files'])} 条，核实无无关改动混入。")
    if lane_id in ("security_architecture", "security_compliance") and pre_probes:
        clues = pre_probes.get("secret_clues", [])
        lines.append(f"- **预探针密钥线索**: {len(clues)} 条" + ("" if not clues else " -> " + ", ".join(f"`{c['file']}`({c['kind']})" for c in clues)))
    if "bombadil" in vals and any(r.startswith("RV-BOMB-") for r in active_rule_ids):
        lines.append(f"- **交互复杂度初步信号**: `{manifest['signals'].get('has_complex_ui_flow')}` | **PATH 上 bombadil**: `{repo_ctx.get('bombadil_cli_on_path') or '未在 PATH 找到（须再核项目本地安装）'}`")
    if "react_doctor" in vals and any(r.startswith("RV-REACT-") for r in active_rule_ids):
        lines.append(f"- **React packages**: {', '.join(repo_ctx.get('react_packages', [])) or '由 .tsx/.jsx 识别'}")
        lines.append(f"- **建议命令**: `npx --yes react-doctor@latest . --yes --scope changed --base {manifest.get('base_ref', 'origin/main')} --no-telemetry --no-supply-chain --json --json-out {round_dir(run_dir, rnum) / 'artifacts' / 'react-doctor.json'}`")

    # Upstream artifact injection (declarative via upstream_notes)
    upstream_notes = lane_cfg.get("upstream_notes") or {}
    upstream_blocks: list[str] = []
    for dep_id in lane_cfg.get("depends_on", []):
        if dep_id in results:
            dep = results[dep_id]
            blk = [f"### 上游模块 `{dep_id}`（状态: `{dep['status']}`）", f"- 摘要: {dep.get('summary', '')}"]
            if dep.get("evidence"):
                blk.append(f"- 证据: {', '.join(dep['evidence'][:6])}")
            if dep.get("findings"):
                blk.append("- Findings:")
                for f in dep["findings"][:8]:
                    blk.append(f"  - [{f.get('severity')}][{f.get('rule_id', '-')}] `{f.get('location')}`: {f.get('problem')}")
            if dep.get("meta"):
                blk.append(f"- 元数据: `{json.dumps(dep['meta'], ensure_ascii=False)}`")
            if dep_id in upstream_notes:
                blk.append(f"- **交接指令**: {upstream_notes[dep_id]}")
            upstream_blocks.append("\n".join(blk))
    if upstream_blocks:
        lines.extend(["", "## 3. 上游阶段交接证据（自动注入）", *upstream_blocks])

    carryover_path = round_dir(run_dir, rnum) / "carryover_findings.json"
    if carryover_path.exists():
        carryover = read_json(carryover_path)
        prev_for_lane = [f for f in carryover.get("findings", []) if f.get("lane_id") == lane_id or lane_cfg.get("recheck_policy") == "always"]
        if prev_for_lane or carryover.get("fix_files"):
            lines.extend(["", f"## 复审指令（Round {rnum} 增量复验）"])
            if carryover.get("fix_files"):
                lines.append(f"- 修复改动文件: {', '.join(f'`{f}`' for f in carryover['fix_files'][:20])}")
            for pf in prev_for_lane:
                lines.append(f"- 必须实测复验 [{pf.get('severity')}][{pf.get('rule_id', '-')}] `{pf.get('location')}` — {pf.get('problem')}（原建议: {pf.get('fix')}）")

    lines.extend(["", f"## 4. 本维度逐条必检规则（共 {len(active_rules)} 条，submit 时 checks[] 必须逐条交账）"])
    last_grp: str | None = None
    for idx, rule in enumerate(active_rules, 1):
        grp = rule.get("group")
        if grp and grp != last_grp:
            lines.append(f"### 子分组：{grp}")
            last_grp = grp
        na_tag = "可 N/A（须写理由）" if rule.get("allow_na", True) else "**不可 N/A**"
        src_tag = f" `[来源: {rule['source']}]`" if rule.get("source") and rule["source"] != "base" else ""
        lines.append(f"{idx}. **`{rule['id']}` {rule['title']}**（{na_tag}）{src_tag}")
        lines.append(f"   - 审查要点: {rule['check']}")
    if auto_na_rules:
        lines.append("")
        lines.append("以下子规则未命中信号或被配置关闭，已标为 `AUTO_NA`（无需在 checks[] 中提交）：")
        for rule in auto_na_rules:
            lines.append(f"- `{rule['id']}` {rule['title']} — {rule.get('auto_na_reason', '')}")

    lines.extend(["", "## 5. 红线与禁止跳步规则"])
    for item in lane_cfg.get("anti_rationalizations", []) or ["无一手证据不得标 PASS；必须逐条核验全部激活规则。"]:
        lines.append(f"- {item}")

    lines.extend(["", "## 6. 动态注入的规范依据"])
    for ref_slice in lane_cfg.get("reference_slices", []):
        cond = ref_slice.get("only_when_signal")
        if cond and not manifest["signals"].get(cond):
            continue
        excerpt = extract_markdown_sections(REFERENCES_DIR / ref_slice["file"], ref_slice.get("sections", []))
        lines.extend([f"### 来源: `references/{ref_slice['file']}`", excerpt, ""])
    for custom_ref in lane_cfg.get("reference_files", []) or []:
        ref_path = Path(custom_ref)
        excerpt = ref_path.read_text(encoding="utf-8").strip() if ref_path.is_file() else f"_(custom reference not found: {custom_ref})_"
        lines.extend([f"### 自定义参考: `{custom_ref}`", excerpt, ""])
    already_injected = {str(Path(r).resolve()) for r in (lane_cfg.get("reference_files") or []) if Path(r).exists()}
    if design_docs and ("ui_ux_audit" in vals or ("journey_review" in vals and "RV-BIZ-05" in active_rule_ids)):
        for doc in design_docs[:6]:
            if doc["path"] in already_injected:
                continue
            dpath = Path(doc["path"])
            if not dpath.is_file():
                continue
            raw_txt = dpath.read_text(encoding="utf-8").strip()
            if len(raw_txt) > 4000:
                raw_txt = raw_txt[:4000].rstrip() + f"\n\n_(已截断前 4000 字符，完整版见 `{doc['path']}`)_"
            lines.extend([f"### 自动加载的设计理念 ({doc['layer']}): `{doc['name']}`", raw_txt, ""])
    if "ui_ux_audit" in vals:
        lines.append(f"- 完整 70 条界面规则目录: `{REFERENCES_DIR / 'ui-ux-rules.md'}`（精简索引: `{REFERENCES_DIR / 'ui-ux-rules-short.md'}`）。")
        lines.append("")

    checks_template = [{"id": r["id"], "status": "PASS", "note": f"{r['title']} 核查证据或说明"} for r in active_rules]
    sample_rule_id = active_rules[0]["id"] if active_rules else "RV-BASE-01"
    sample_payload = {
        "lane_id": lane_id,
        "prompt_token": token,
        "status": "PASS | FAIL | BLOCKED | N/A",
        "reviewer": manifest.get("reviewer") or "independent-reviewer",
        "summary": "一句话结论",
        "checks": checks_template,
        "evidence": ["具体命令/文件/日志/观测证据（PASS 必填）"],
        "commands_run": ["实际执行的命令及退出码"],
        "findings": [{
            "rule_id": sample_rule_id,
            "severity": "P0 | P1 | P2 | P3",
            "location": "path/to/file:line",
            "problem": "具体问题",
            "impact": "业务或维护影响",
            "fix": "最小修复建议",
            "verification": "复验条件",
        }],
        "open_questions": [],
        "test_gaps": [],
        "unverified_items": [],
        "unrun_checks": [{"check": "未运行项", "reason": "原因", "remediation": "最小补证办法"}],
        "residual_risks": [],
        "reason": "当 lane status 为 N/A 或 BLOCKED 时必填",
        "meta": _lane_meta_example(lane_cfg, active_rule_ids, manifest["material"]),
    }
    lines.extend([
        "## 7. 过程日志与提交契约",
        f"- （可选）开工打点：`python3 \"{runner_path}\" start --run \"{run_dir}\" --lane {lane_id}`",
        "- 完成后必须将逐条 `checks[]` 落盘：",
        "```bash",
        f'python3 "{runner_path}" submit --run "{run_dir}" --lane {lane_id} --input -',
        "```",
        "```json",
        json.dumps(sample_payload, ensure_ascii=False, indent=2),
        "```",
    ])
    return "\n".join(lines) + "\n", token


def issue_prompt_for_lane(run_dir: Path, manifest: dict[str, Any], effective_cfg: dict[str, Any], plan: dict[str, Any], results: dict[str, dict[str, Any]], lane_id: str) -> dict[str, Any]:
    rnum = int(manifest["current_round"])
    prompt_text, token = stitch_lane_prompt(run_dir, manifest, effective_cfg, plan, results, lane_id)
    p_path = lane_prompt_path(run_dir, rnum, lane_id)
    m_path = lane_prompt_meta_path(run_dir, rnum, lane_id)
    first_issue = not m_path.exists()

    lp = next(x for x in plan["lanes"] if x["id"] == lane_id)
    active_ids = {r["id"] for r in lp.get("active_rules", [])}
    blind_path_str: str | None = None
    if "journey_walkthrough" in lane_validators(lp) and "RV-UI-05" in active_ids:
        b_path = lane_blind_prompt_path(run_dir, rnum, lane_id)
        blind_text = stitch_blind_walkthrough_prompt(run_dir, manifest, lane_id, token)
        atomic_write_text(b_path, blind_text)
        blind_path_str = str(b_path)
        prompt_text = (
            f"> **防锚定前置步骤（Blind Walkthrough）**：请先派发独立只读 Agent 仅读取无源码盲测 Prompt `{blind_path_str}` 完成真实用户走查并锁定观察结果，再继续执行下方全量审查。\n\n"
            + prompt_text
        )

    atomic_write_text(p_path, prompt_text)
    atomic_write_json(m_path, {
        "lane_id": lane_id,
        "round": rnum,
        "prompt_token": token,
        "issued_at": now_iso(),
        "prompt_path": str(p_path),
        "blind_prompt_path": blind_path_str,
        "workspace_fingerprint": manifest["workspace_fingerprint"],
    })
    if first_issue:
        record_event(
            run_dir, "LANE_DISPATCHED",
            f"→ 已解锁并生成 Prompt: {lane_id} ({len(lp.get('active_rules', []))} 条规则)"
            + (" [含无源码盲测 Prompt]" if blind_path_str else ""),
            round_num=rnum, phase_id=lp["phase"], lane_id=lane_id, status="PROMPT_ISSUED",
            details={"token": token, "rules": [r["id"] for r in lp.get("active_rules", [])], "blind_prompt_path": blind_path_str},
        )
    out = {"lane_id": lane_id, "prompt_token": token, "prompt_path": str(p_path), "prompt_text": prompt_text}
    if blind_path_str:
        out["blind_prompt_path"] = blind_path_str
    return out


def validate_lane_submission(
    run_dir: Path,
    manifest: dict[str, Any],
    plan: dict[str, Any],
    results: dict[str, dict[str, Any]],
    lane_id: str,
    payload: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    lane_plan = next((lp for lp in plan["lanes"] if lp["id"] == lane_id), None)
    if lane_plan is None:
        return [f"unknown lane_id: {lane_id}"]
    if not lane_plan["required"]:
        return [f"lane {lane_id} is {lane_plan.get('initial_status', 'AUTO_NA')} in this run; no submission needed"]

    rnum = int(manifest["current_round"])
    progress = compute_progress(run_dir, manifest, plan, results)
    if progress["stale_workspace"]:
        return [f"workspace changed since round {rnum} init ({manifest['workspace_fingerprint']} != {progress['live_fingerprint']}); run recheck first"]

    unmet = [dep for dep in lane_plan["depends_on"] if not lane_is_settled(progress["states"].get(dep, "AUTO_NA"))]
    if unmet:
        return [f"lane {lane_id} is locked; waiting on dependencies: {', '.join(unmet)}"]

    meta_path = lane_prompt_meta_path(run_dir, rnum, lane_id)
    if not meta_path.exists():
        return [f"prompt for lane {lane_id} has not been issued yet; run `next` or `prompt --lane {lane_id}` first"]
    prompt_meta = read_json(meta_path)
    supplied_token = str(payload.get("prompt_token", "")).strip()
    if supplied_token and supplied_token != prompt_meta["prompt_token"]:
        errors.append(f"prompt_token mismatch for {lane_id}: expected {prompt_meta['prompt_token']}, got {supplied_token}")

    status = payload.get("status")
    if status not in VALID_LANE_STATUSES:
        errors.append(f"status must be one of {', '.join(VALID_LANE_STATUSES)}")
        return errors

    summary = str(payload.get("summary", "")).strip()
    if not summary:
        errors.append("summary must be a non-empty string")

    evidence = [str(e).strip() for e in (payload.get("evidence") or []) if str(e).strip()] if isinstance(payload.get("evidence", []), list) else []
    if not isinstance(payload.get("evidence", []), list):
        errors.append("evidence must be a list of strings")
    commands_run = payload.get("commands_run", [])
    if not isinstance(commands_run, list):
        errors.append("commands_run must be a list")
        commands_run = []
    reason = str(payload.get("reason", "")).strip()
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        errors.append("findings must be a list")
        findings = []
    unrun_checks = payload.get("unrun_checks", [])
    if not isinstance(unrun_checks, list):
        errors.append("unrun_checks must be a list")
        unrun_checks = []
    unverified_items = payload.get("unverified_items", [])
    if not isinstance(unverified_items, list):
        errors.append("unverified_items must be a list")
        unverified_items = []
    meta = payload.get("meta", {})
    if not isinstance(meta, dict):
        errors.append("meta must be an object")
        meta = {}

    active_rules = {r["id"]: r for r in lane_plan.get("active_rules", [])}
    checks = payload.get("checks")
    if not isinstance(checks, list):
        errors.append(f"checks must be a list accounting for every active rule: {', '.join(active_rules)}")
        checks = []
    else:
        seen_ids: set[str] = set()
        check_statuses: list[str] = []
        for idx, item in enumerate(checks):
            if not isinstance(item, dict):
                errors.append(f"checks[{idx}] must be an object with id/status/note")
                continue
            rid = str(item.get("id", "")).strip()
            rstatus = item.get("status")
            rnote = str(item.get("note", "")).strip()
            if rid not in active_rules:
                errors.append(f"checks[{idx}].id '{rid}' is not an active rule for lane {lane_id}")
                continue
            if rid in seen_ids:
                errors.append(f"duplicate rule check: {rid}")
                continue
            seen_ids.add(rid)
            if rstatus not in VALID_LANE_STATUSES:
                errors.append(f"check {rid}: status must be one of {', '.join(VALID_LANE_STATUSES)}")
                continue
            check_statuses.append(rstatus)
            if rstatus == "N/A":
                if not active_rules[rid].get("allow_na", True) and status != "N/A":
                    errors.append(f"rule {rid} does not allow N/A")
                if not rnote:
                    errors.append(f"rule {rid} marked N/A requires a non-empty note")
            if rstatus in ("BLOCKED", "PASS") and not rnote:
                errors.append(f"rule {rid} marked {rstatus} requires a non-empty note")

        missing_rules = [rid for rid in active_rules if rid not in seen_ids]
        if missing_rules:
            errors.append(f"missing required rule checks: {', '.join(missing_rules)}")
        if "FAIL" in check_statuses and status != "FAIL":
            errors.append("lane status must be FAIL when one or more checks[] items are FAIL")
        if "BLOCKED" in check_statuses and status == "PASS":
            errors.append("lane status cannot be PASS when one or more checks[] items are BLOCKED")
        if status == "PASS" and check_statuses and all(s == "N/A" for s in check_statuses):
            errors.append("lane status cannot be PASS when all checks[] items are N/A (use N/A)")

    if status == "PASS" and not evidence:
        errors.append("PASS requires non-empty evidence")
    if status == "PASS" and any(isinstance(f, dict) and f.get("severity") in BLOCKING_SEVERITIES for f in findings):
        errors.append("PASS cannot include P0/P1/blocking findings (use FAIL)")
    if status == "N/A":
        if not lane_plan["allow_na"]:
            errors.append(f"lane {lane_id} does not allow N/A")
        if not reason:
            errors.append("N/A requires a non-empty reason")
    if status == "FAIL" and not findings:
        errors.append("FAIL requires at least one structured finding in findings[]")

    for idx, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"findings[{idx}] must be an object")
            continue
        rid = str(f.get("rule_id", "")).strip()
        if not rid or not RULE_ID_RE.match(rid):
            errors.append(f"findings[{idx}].rule_id must be a valid rule ID (e.g. RV-BUG-01, UX-VIS-09, AP-01, ORG-PAY-01)")
        elif not rid.startswith("UX-") and not rid.startswith("AP-") and rid not in active_rules:
            errors.append(f"findings[{idx}].rule_id '{rid}' is not an active rule in lane {lane_id}")
        elif rid.startswith("AP-") and "RV-BIZ-05" not in active_rules and "RV-UI-05" not in active_rules:
            errors.append(f"findings[{idx}].rule_id '{rid}' requires active journey rule (RV-BIZ-05 or RV-UI-05)")
        if f.get("severity") not in VALID_SEVERITIES:
            errors.append(f"findings[{idx}].severity must be one of {', '.join(VALID_SEVERITIES)}")
        for field in ("location", "problem", "impact", "fix"):
            if not str(f.get(field, "")).strip():
                errors.append(f"findings[{idx}].{field} must be non-empty")

    if status == "BLOCKED":
        if not reason:
            errors.append("BLOCKED requires a non-empty reason")
        if not unrun_checks:
            errors.append("BLOCKED requires at least one item in unrun_checks[] with check/reason/remediation")
        for idx, item in enumerate(unrun_checks):
            if not isinstance(item, dict) or not str(item.get("check", "")).strip() or not str(item.get("reason", "")).strip():
                errors.append(f"unrun_checks[{idx}] requires check and reason")

    vals = lane_validators(lane_plan)
    checks_map = {str(c.get("id", "")).strip(): c for c in checks if isinstance(c, dict)}

    if "bombadil" in vals and any(r.startswith("RV-BOMB-") for r in active_rules):
        applicability = str(meta.get("applicability", "")).strip()
        exec_state = str(meta.get("execution_state", "")).strip()
        if applicability not in ("applicable", "not_applicable"):
            errors.append(f"{lane_id} requires meta.applicability in ('applicable', 'not_applicable') for Bombadil")
        if exec_state not in ("completed_no_violation", "violation_found", "incomplete", "not_applicable"):
            errors.append(f"{lane_id} requires meta.execution_state in ('completed_no_violation', 'violation_found', 'incomplete', 'not_applicable')")
        bomb_checks = [checks_map[r] for r in active_rules if r.startswith("RV-BOMB-") and r in checks_map]
        bomb_na_notes = " ".join([reason, *(str(c.get("note", "")) for c in bomb_checks if c.get("status") == "N/A")]).lower()
        if status == "N/A" or any(c.get("status") == "N/A" for c in bomb_checks):
            if applicability == "applicable":
                errors.append(f"{lane_id}: Bombadil checks cannot be N/A when applicability is 'applicable' (use BLOCKED)")
            if any(kw in bomb_na_notes for kw in TOOL_UNAVAILABLE_KEYWORDS):
                errors.append(f"{lane_id}: Bombadil tool/isolation/timeout failure must be BLOCKED, not N/A")
        if applicability == "applicable" and bomb_checks and all(c.get("status") == "PASS" for c in bomb_checks):
            if exec_state != "completed_no_violation":
                errors.append(f"{lane_id}: passing Bombadil checks require execution_state='completed_no_violation'")
            if not str(meta.get("command", "")).strip() and not commands_run:
                errors.append(f"{lane_id}: passing Bombadil checks require executed command in meta.command or commands_run")
            if not str(meta.get("budget", "")).strip():
                errors.append(f"{lane_id}: passing Bombadil checks require meta.budget (e.g. '1m')")

    if "react_doctor" in vals and "RV-REACT-01" in active_rules and status in ("PASS", "FAIL"):
        if str(meta.get("scope", "")).strip() not in ("changed", "full", "design"):
            errors.append(f"{lane_id}: React Doctor requires meta.scope in ('changed', 'full', 'design')")
        if meta.get("no_telemetry") is False:
            errors.append(f"{lane_id}: React Doctor must keep no_telemetry=true by default")
        if status == "PASS" and meta.get("skipped_files"):
            errors.append(f"{lane_id}: React Doctor with skipped_files must be BLOCKED (incomplete scan), not PASS")

    if "ui_ux_audit" in vals and any(r.startswith("RV-UI-") for r in active_rules):
        mat = str(meta.get("material_type", "")).strip()
        if mat not in ("runnable", "prototype", "screenshot", "video"):
            errors.append(f"{lane_id} requires meta.material_type in ('runnable', 'prototype', 'screenshot', 'video')")
        ulc = str(meta.get("unfamiliar_language_check", "")).strip()
        if ulc not in ("PASS", "FAIL", "N/A", "UNVERIFIED"):
            errors.append(f"{lane_id} requires meta.unfamiliar_language_check in ('PASS', 'FAIL', 'N/A', 'UNVERIFIED')")
        if mat == "screenshot" and status == "PASS" and not unverified_items:
            errors.append(f"{lane_id} on screenshot-only material must list non-provable interactions in unverified_items[]")
        loaded_design_docs = (manifest.get("repo_context") or {}).get("design_principle_docs") or []
        ui04_chk = checks_map.get("RV-UI-04")
        if loaded_design_docs and status in ("PASS", "FAIL") and (ui04_chk is None or ui04_chk.get("status") == "PASS"):
            if meta.get("company_cases_loaded") is not True:
                doc_names = ", ".join(d["name"] for d in loaded_design_docs)
                errors.append(
                    f"{lane_id}: design principle docs were auto-loaded ({doc_names}); "
                    "confirm review against them by setting meta.company_cases_loaded=true"
                )

        # 14-group structured 70-rule UX coverage guard (RV-UI-03)
        if "RV-UI-03" in active_rules and status in ("PASS", "FAIL"):
            ux_cov = meta.get("ux_coverage")
            if not isinstance(ux_cov, dict):
                errors.append(f"{lane_id}: RV-UI-03 requires structured meta.ux_coverage covering all 14 UX groups (70 rules total)")
            else:
                finding_rule_ids = {str(f.get("rule_id", "")).strip() for f in findings if isinstance(f, dict)}
                missing_groups = [prefix for prefix, _, _ in UX_GROUPS if prefix not in ux_cov]
                if missing_groups:
                    errors.append(f"{lane_id}: meta.ux_coverage missing UX groups: {', '.join(missing_groups)}")
                for prefix, _, expected_total in UX_GROUPS:
                    if prefix not in ux_cov:
                        continue
                    g_obj = ux_cov[prefix]
                    if not isinstance(g_obj, dict):
                        errors.append(f"{lane_id}: meta.ux_coverage.{prefix} must be an object with passed/failed/na/unverified counts")
                        continue
                    counts: dict[str, int] = {}
                    bad_cnt = False
                    for k in ("passed", "failed", "na", "unverified"):
                        v = g_obj.get(k, 0)
                        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                            errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.{k} must be a non-negative integer")
                            bad_cnt = True
                        else:
                            counts[k] = v
                    if not bad_cnt and sum(counts.values()) != expected_total:
                        errors.append(
                            f"{lane_id}: meta.ux_coverage.{prefix} counts sum to {sum(counts.values())}, expected {expected_total}"
                        )
                    failed_ids = g_obj.get("failed_ids", [])
                    if not isinstance(failed_ids, list):
                        errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.failed_ids must be a list")
                        failed_ids = []
                    if not bad_cnt and len(failed_ids) != counts["failed"]:
                        errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.failed_ids length ({len(failed_ids)}) must match failed count ({counts['failed']})")
                    for fid in failed_ids:
                        sfid = str(fid).strip()
                        if not UX_RULE_ID_RE.match(sfid) or not sfid.startswith(f"{prefix}-"):
                            errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.failed_ids contains invalid ID '{sfid}'")
                        elif sfid not in finding_rule_ids:
                            errors.append(f"{lane_id}: failed UX rule '{sfid}' in meta.ux_coverage.{prefix} must have a matching entry in findings[]")

                    unverified_ids = g_obj.get("unverified_ids", [])
                    if not isinstance(unverified_ids, list):
                        errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.unverified_ids must be a list")
                        unverified_ids = []
                    if not bad_cnt and len(unverified_ids) != counts["unverified"]:
                        errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.unverified_ids length ({len(unverified_ids)}) must match unverified count ({counts['unverified']})")
                    for uid in unverified_ids:
                        suid = str(uid).strip()
                        if not UX_RULE_ID_RE.match(suid) or not suid.startswith(f"{prefix}-"):
                            errors.append(f"{lane_id}: meta.ux_coverage.{prefix}.unverified_ids contains invalid ID '{suid}'")

    # Journey Review validator (business_acceptance RV-BIZ-05)
    biz05_chk = checks_map.get("RV-BIZ-05")
    if "journey_review" in vals and "RV-BIZ-05" in active_rules and status in ("PASS", "FAIL") and (biz05_chk is None or biz05_chk.get("status") != "N/A"):
        jr = meta.get("journey_review")
        if not isinstance(jr, dict) or not isinstance(jr.get("journeys"), list) or not jr["journeys"]:
            errors.append(f"{lane_id}: RV-BIZ-05 requires meta.journey_review.journeys[] with Expected vs Actual journey gap analysis")
        else:
            finding_rule_ids = {str(f.get("rule_id", "")).strip() for f in findings if isinstance(f, dict)}
            found_aps: set[str] = set()
            for idx, j in enumerate(jr["journeys"]):
                if not isinstance(j, dict):
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}] must be an object")
                    continue
                if not str(j.get("id", "")).strip():
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].id must be non-empty")
                if not isinstance(j.get("expected_stages"), list) or not [s for s in j["expected_stages"] if str(s).strip()]:
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].expected_stages must be a non-empty list")
                if not isinstance(j.get("actual_steps"), list) or not [s for s in j["actual_steps"] if str(s).strip()]:
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].actual_steps must be a non-empty list")
                if not str(j.get("gap_summary", "")).strip():
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].gap_summary must be non-empty")
                if str(j.get("verdict", "")).strip() not in ("ALIGNED", "FRICTION", "NEEDS_REDESIGN", "UNVERIFIED"):
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].verdict must be one of ALIGNED, FRICTION, NEEDS_REDESIGN, UNVERIFIED")
                apc = j.get("anti_patterns_checked")
                if not isinstance(apc, dict):
                    errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].anti_patterns_checked must cover AP-01..AP-08")
                else:
                    missing_aps = [ap_id for ap_id, _ in PRODUCT_ANTI_PATTERNS if ap_id not in apc]
                    if missing_aps:
                        errors.append(f"{lane_id}: meta.journey_review.journeys[{idx}].anti_patterns_checked missing {', '.join(missing_aps)}")
                    for ap_id, _ in PRODUCT_ANTI_PATTERNS:
                        if ap_id in apc:
                            val = str(apc[ap_id]).strip()
                            if val not in ("CLEAR", "FOUND", "N/A"):
                                errors.append(f"{lane_id}: anti_patterns_checked.{ap_id} must be CLEAR, FOUND, or N/A")
                            elif val == "FOUND":
                                found_aps.add(ap_id)
            if found_aps and not (finding_rule_ids & ({"RV-BIZ-05"} | found_aps)):
                errors.append(f"{lane_id}: anti-patterns marked FOUND ({', '.join(sorted(found_aps))}) must be recorded in findings[] with matching AP-* or RV-BIZ-05 rule_id")

    # Blind User Walkthrough validator (ui_ux_experience RV-UI-05)
    ui05_chk = checks_map.get("RV-UI-05")
    if "journey_walkthrough" in vals and "RV-UI-05" in active_rules and status in ("PASS", "FAIL") and (ui05_chk is None or ui05_chk.get("status") != "N/A"):
        jw = meta.get("journey_walkthrough")
        if not isinstance(jw, dict):
            errors.append(f"{lane_id}: RV-UI-05 requires meta.journey_walkthrough with blind_mode, actor, goal, actual_steps, and 7 observations")
        else:
            if not isinstance(jw.get("blind_mode"), bool):
                errors.append(f"{lane_id}: meta.journey_walkthrough.blind_mode must be a boolean")
            if not str(jw.get("actor", "")).strip():
                errors.append(f"{lane_id}: meta.journey_walkthrough.actor must be non-empty")
            if not str(jw.get("goal", "")).strip():
                errors.append(f"{lane_id}: meta.journey_walkthrough.goal must be non-empty")
            if not isinstance(jw.get("actual_steps"), list) or not [s for s in jw["actual_steps"] if str(s).strip()]:
                errors.append(f"{lane_id}: meta.journey_walkthrough.actual_steps must be a non-empty list")
            if not isinstance(jw.get("friction_points", []), list):
                errors.append(f"{lane_id}: meta.journey_walkthrough.friction_points must be a list")
            obs = jw.get("observations")
            if not isinstance(obs, dict):
                errors.append(f"{lane_id}: meta.journey_walkthrough.observations must cover all 7 walkthrough observation keys")
            else:
                missing_obs = [k for k, _ in WALKTHROUGH_OBSERVATION_KEYS if k not in obs]
                if missing_obs:
                    errors.append(f"{lane_id}: meta.journey_walkthrough.observations missing keys: {', '.join(missing_obs)}")
                for k, _ in WALKTHROUGH_OBSERVATION_KEYS:
                    if k not in obs:
                        continue
                    v = obs[k]
                    ost = str(v.get("status", "")).strip() if isinstance(v, dict) else str(v).strip()
                    if ost not in VALID_OBSERVATION_STATUSES:
                        errors.append(f"{lane_id}: meta.journey_walkthrough.observations.{k} status must be one of {', '.join(VALID_OBSERVATION_STATUSES)}")

    return errors


def build_evidence_package(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    results: dict[str, dict[str, Any]],
    approvals: list[dict[str, Any]],
    exceptions: list[dict[str, Any]],
) -> dict[str, Any]:
    step_ids = ("D", "G0", "G1", "G2", "G3", "G4", "CR", "R")
    step_lanes: dict[str, list[dict[str, Any]]] = {sid: [] for sid in step_ids}
    for lp in plan["lanes"]:
        for sid in lp.get("gate_steps") or []:
            if sid in step_lanes:
                step_lanes[sid].append(lp)

    steps_out: list[dict[str, Any]] = []
    unrun_checks: list[dict[str, str]] = []
    residual_risks: list[str] = []
    acceptance: list[dict[str, Any]] = []
    release_info: dict[str, str] = {"rollout": "", "rollback": "", "monitoring": ""}

    for res in results.values():
        for uc in res.get("unrun_checks", []):
            if isinstance(uc, dict) and uc.get("check"):
                unrun_checks.append({"check": str(uc["check"]), "reason": str(uc.get("reason", ""))})
        for uv in res.get("unverified_items", []):
            if str(uv).strip():
                unrun_checks.append({"check": str(uv).strip(), "reason": f"unverified in {res['lane_id']}"})
        for rr in res.get("residual_risks", []):
            if str(rr).strip():
                residual_risks.append(str(rr).strip())
        ac_list = res.get("meta", {}).get("acceptance", [])
        if isinstance(ac_list, list):
            acceptance.extend(i for i in ac_list if isinstance(i, dict) and i.get("id") and i.get("status"))
        rmeta = res.get("meta", {})
        for k in ("rollout", "rollback", "monitoring"):
            if isinstance(rmeta.get(k), str) and rmeta[k].strip():
                release_info[k] = rmeta[k].strip()

    for lp in plan["lanes"]:
        if lp["required"] and lp["id"] not in results:
            unrun_checks.append({"check": f"lane:{lp['id']} ({lp['title']})", "reason": "未执行（提前阻断或尚未完成）"})

    biz_res = results.get("business_acceptance") or results.get("business_functional")
    if not acceptance and biz_res:
        if biz_res["status"] in ("PASS", "FAIL", "BLOCKED"):
            acceptance.append({"id": "AC1", "expected": "主业务闭环与验收标准达成", "actual": biz_res.get("summary", ""), "evidence": biz_res.get("evidence", []), "status": biz_res["status"]})

    for sid in step_ids:
        linked = step_lanes[sid]
        if sid == "D":
            any_required = any(
                lp["required"] and any(r["id"].startswith("RV-ARCH-") for r in lp.get("active_rules", []))
                for lp in linked
            )
        else:
            any_required = any(lp["required"] for lp in linked)
        if not any_required:
            na_reasons = [lp["auto_na_reason"] for lp in linked if lp.get("auto_na_reason")]
            steps_out.append({"id": sid, "required": False, "status": "N/A", "evidence": [], "reason": "; ".join(na_reasons) or "not applicable"})
            continue

        agg_evidence: list[str] = []
        agg_reasons: list[str] = []
        statuses_seen: list[str] = []
        for lp in linked:
            if not lp["required"]:
                continue
            res = results.get(lp["id"])
            if res is None:
                statuses_seen.append("BLOCKED")
                agg_reasons.append(f"{lp['id']} not executed")
                continue
            statuses_seen.append(res["status"])
            agg_evidence.extend(res.get("evidence", []))
            if res.get("reason"):
                agg_reasons.append(f"{lp['id']}: {res['reason']}")

        step_status = "FAIL" if "FAIL" in statuses_seen else ("BLOCKED" if "BLOCKED" in statuses_seen else ("PASS" if "PASS" in statuses_seen else "N/A"))
        ui_res = results.get("ui_ux_experience") or results.get("ui_ux_audit")
        if sid == "G2" and ui_res:
            if ui_res.get("meta", {}).get("material_type") == "screenshot" and step_status == "PASS":
                step_status = "BLOCKED"
                agg_reasons.append("只有静态截图，交互/焦点/提交/性能等未验证")

        steps_out.append({
            "id": sid,
            "required": True,
            "status": step_status,
            "evidence": agg_evidence,
            "commit": manifest["head_sha"],
            "reason": "; ".join(agg_reasons),
            "method": ",".join(lp["id"] for lp in linked if lp["required"]),
        })

    reviewer = str(manifest.get("reviewer") or "").strip()
    if not reviewer:
        reviewers = [str(r.get("reviewer", "")).strip() for r in results.values() if str(r.get("reviewer", "")).strip()]
        reviewer = reviewers[0] if reviewers else ""

    return {
        "schema_version": "1",
        "task_id": manifest.get("task_id") or manifest["run_id"],
        "intent_revision": 1,
        "authorization_level": manifest["level"],
        "dri": manifest.get("dri") or "",
        "reviewer": reviewer,
        "commit": manifest["head_sha"],
        "environment": manifest.get("target_url") or manifest.get("target") or "",
        "acceptance": acceptance,
        "steps": steps_out,
        "unrun_checks": unrun_checks,
        "residual_risks": residual_risks,
        "release": release_info,
        "approvals": approvals,
        "exceptions": exceptions,
    }


def render_final_report(
    run_dir: Path,
    manifest: dict[str, Any],
    plan: dict[str, Any],
    results: dict[str, dict[str, Any]],
    verdict: str,
    verdict_zh: str,
    gate_result: dict[str, Any] | None,
    early_stop_reason: str | None,
) -> str:
    all_findings: list[dict[str, Any]] = []
    all_questions: list[str] = []
    all_test_gaps: list[str] = []
    all_unrun: list[str] = []
    all_risks: list[str] = []

    for lp in plan["lanes"]:
        lid = lp["id"]
        if lid in results:
            res = results[lid]
            for f in res.get("findings", []):
                all_findings.append({**f, "lane_id": lid})
            all_questions.extend(str(q).strip() for q in res.get("open_questions", []) if str(q).strip())
            all_test_gaps.extend(str(g).strip() for g in res.get("test_gaps", []) if str(g).strip())
            for uv in res.get("unverified_items", []):
                if str(uv).strip():
                    all_unrun.append(f"[{lid}] 未验证: {uv}")
            for uc in res.get("unrun_checks", []):
                if isinstance(uc, dict) and uc.get("check"):
                    rem = f"（补证: {uc['remediation']}）" if uc.get("remediation") else ""
                    all_unrun.append(f"[{lid}] {uc['check']}: {uc.get('reason', '')}{rem}")
            all_risks.extend(str(r).strip() for r in res.get("residual_risks", []) if str(r).strip())
        elif lp["required"]:
            all_unrun.append(f"[{lid}] {lp['title']}: 尚未执行（提前阻断）")

    all_findings.sort(key=lambda item: SEVERITY_RANK.get(str(item.get("severity")), 9))

    def format_rule_coverage() -> list[str]:
        out: list[str] = []
        for lp in plan["lanes"]:
            lid = lp["id"]
            if not lp["required"]:
                out.append(f"- {lp['title']} (`{lid}`): {lp.get('initial_status', 'AUTO_NA')}（{lp['auto_na_reason']}）")
                continue
            if lid not in results:
                out.append(f"- {lp['title']} (`{lid}`): 未执行")
                continue
            res = results[lid]
            out.append(f"- {lp['title']} (`{lid}`): **{res['status']}** — {res.get('summary', '')}")
            for chk in res.get("checks", []):
                out.append(f"  - `{chk['id']}` [{chk['status']}] {chk.get('note', '')}")
            for na_r in lp.get("auto_na_rules", []):
                out.append(f"  - `{na_r['id']}` [AUTO_NA] {na_r.get('auto_na_reason', '')}")
        return out

    mode = manifest["mode"]
    lines: list[str] = []
    if mode in ("delivery", "release", "audit"):
        lines.append(f"交付结论: {verdict_zh}")
        if early_stop_reason:
            lines.append(f"提前阻断说明: {early_stop_reason}（未执行的计划检查已在下方单列，不宣称全量验证完成）")
        lines.extend(["", "Findings:"])
        lines.extend([f"- [{f['severity']}][{f.get('rule_id', '-')}] {f['location']} ({f['lane_id']}) - {f['problem']} | 影响: {f['impact']} | 建议: {f['fix']}" for f in all_findings] or ["- 无阻断或显著发现。"])
        lines.extend(["", "证据（逐条规则核验记录）:", *format_rule_coverage(), "", "上线准备:"])
        if "release_readiness" in results:
            rr = results["release_readiness"]
            lines.append(f"- {rr.get('summary', '')}")
            rmeta = rr.get("meta", {})
            for label, key in (("放量", "rollout"), ("回滚", "rollback"), ("监控", "monitoring"), ("业务就绪", "business_readiness")):
                if rmeta.get(key):
                    lines.append(f"- {label}: {rmeta[key]}")
        else:
            lines.append("- 本次未进入生产发布准备或已提前阻断。")
        lines.extend(["", "未运行检查及原因:", *([f"- {i}" for i in all_unrun] or ["- 无。"])])
        lines.extend(["", "剩余风险:", *([f"- {i}" for i in all_risks] or ["- 无额外未覆盖风险（仍受各测试方法固有边界限制）。"])])
    else:
        lines.append(f"结论: {verdict_zh} ({verdict})")
        if early_stop_reason:
            lines.append(f"提前阻断说明: {early_stop_reason}（以下已单列尚未执行的计划检查）")
        lines.extend(["", "Findings:"])
        lines.extend([f"- [{f['severity']}][{f.get('rule_id', '-')}] {f['location']} ({f['lane_id']}) - {f['problem']} | 影响: {f['impact']} | 建议: {f['fix']}" for f in all_findings] or ["- 无发现阻塞问题。"])
        lines.extend(["", "Open Questions:", *([f"- {q}" for q in all_questions] or ["- 无。"])])
        lines.extend(["", "Test Gaps:", *([f"- {g}" for g in (all_test_gaps + all_unrun)] or ["- 无显著未覆盖缺口。"])])
        ds = manifest.get("diff_stats", {})
        lines.extend([
            "",
            "Change Summary:",
            f"- Scope: `{manifest.get('base_ref', 'N/A')}..{manifest['head_sha']}`，{ds.get('files_changed', 0)} 个文件 (+{ds.get('added', 0)}/-{ds.get('deleted', 0)}，{ds.get('size_tier', 'N/A')})。",
            *format_rule_coverage(),
            "",
            "Residual risk:",
            *([f"- {r}" for r in all_risks] or ["- 无额外记录；受所选验证方法边界限制。"]),
        ])

    if gate_result and gate_result.get("problems"):
        lines.extend(["", "门禁机检问题（gate_check）:", *[f"- {p}" for p in gate_result["problems"]]])

    events = read_events(run_dir)
    if events:
        lines.extend(["", "过程日志（Timeline）:"])
        for ev in events[-20:]:
            lines.append(f"- [{short_ts(ev['ts'])}][R{ev['round']}] {ev['message']}")
    return "\n".join(lines) + "\n"


def cmd_catalog(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve() if args.target else None
    try:
        cfg = merge_effective_config(target, args.overlay, args.no_auto_overlays, args.enable_lane, args.disable_lane)
    except ValueError as exc:
        print(f"review_runner catalog: {exc}", file=sys.stderr)
        return 2

    phases = sorted(cfg["phases"], key=lambda p: p["order"])
    lanes = cfg["lanes"]
    if args.phase:
        phases = [p for p in phases if p["id"] == args.phase]
    if args.lane:
        lanes = [l for l in lanes if l["id"] == args.lane]

    if args.json:
        print(json.dumps({
            "schema_version": cfg["schema_version"],
            "applied_overlays": cfg["applied_overlays"],
            "disabled_lanes": cfg["disabled_lanes"],
            "disabled_rules": cfg["disabled_rules"],
            "phases": phases,
            "lanes": [{"id": l["id"], "phase": l["phase"], "title": l["title"], "source": l.get("source", "base"), "rules": l.get("rules", [])} for l in lanes],
            "total_lanes": len(lanes),
            "total_rules": sum(len(l.get("rules", [])) for l in lanes),
        }, ensure_ascii=False, indent=2))
        return 0

    total_rules = sum(len(l.get("rules", [])) for l in lanes)
    ov_note = f" (叠加 {len(cfg['applied_overlays'])} 个配置层)" if cfg["applied_overlays"] else ""
    print(f"Engineering Everything Review Catalog — {len(lanes)} 模块, {total_rules} 条原子规则{ov_note}\n")
    for ov in cfg["applied_overlays"]:
        print(f"  + Overlay [{ov['layer']}] {ov['name']} ({ov['path']})")
    if cfg["applied_overlays"]:
        print()
    for p in phases:
        p_lanes = [l for l in lanes if l["phase"] == p["id"]]
        if not p_lanes:
            continue
        print(f"=== {p['title']} ({'可并发' if p['allow_parallel'] else '串行门禁'}) ===")
        for l in p_lanes:
            dis = f" [DISABLED: {cfg['disabled_lanes'][l['id']]}]" if l["id"] in cfg["disabled_lanes"] else ""
            src = f" <{l['source']}>" if l.get("source") and l["source"] != "base" else ""
            print(f"\n[{l['id']}] {l['title']} ({len(l.get('rules', []))} 条){src}{dis}")
            for idx, r in enumerate(l.get("rules", []), 1):
                na = "可N/A" if r.get("allow_na", True) else "必检"
                rsrc = f" <{r['source']}>" if r.get("source") and r["source"] != "base" else ""
                rdis = f" [OFF: {cfg['disabled_rules'][r['id']]}]" if r["id"] in cfg["disabled_rules"] else ""
                print(f"  {idx:2d}. {r['id']} {r['title']} [{na}]{rsrc}{rdis} — {r['check']}")
        print()
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    git_root = detect_git_root(target)
    try:
        effective_cfg = merge_effective_config(git_root or target, args.overlay, args.no_auto_overlays, args.enable_lane, args.disable_lane)
    except ValueError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"review_runner init: {exc}", file=sys.stderr)
        return 2

    explicit_files = [f.strip() for f in args.files.split(",") if f.strip()] if args.files else None
    if git_root is not None:
        git_info = parse_git_state(git_root, args.base, explicit_files)
    else:
        commit_label = args.commit or "SNAPSHOT"
        git_info = {
            "is_git_repo": False,
            "git_root": None,
            "branch": None,
            "base_ref": args.base or "NONE",
            "head_sha": commit_label,
            "workspace_fingerprint": f"nogit:{commit_label}",
            "changed_files": explicit_files or [],
            "dirty_files": [],
            "diff_stats": {"files_changed": len(explicit_files or []), "added": 0, "deleted": 0, "total": 0, "size_tier": "non-git"},
            "pre_probes": {},
        }

    ui_override: bool | None = True if args.ui_interactive else (False if args.no_ui_interactive else None)
    journey_override: bool | None = True if args.journey else (False if args.no_journey else None)
    detected = detect_repo_and_signals(
        target=git_root or target,
        git_info=git_info,
        effective_cfg=effective_cfg,
        mode=args.mode,
        level=args.level,
        material=args.material,
        ui_interactive_override=ui_override,
        has_release_flag=args.has_release,
        intent_card=args.intent_card,
        journey_override=journey_override,
    )
    plan = build_plan(effective_cfg, args.mode, detected["signals"], git_info["changed_files"])

    if args.mode in ("pr", "delivery", "release") and not git_info["changed_files"] and detected["material"] == "code":
        msg = "no diff, changed files, or UI material detected; pass --base, --files, or --material"
        if args.json:
            print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"review_runner init: {msg}", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    short_hash = hashlib.sha256(f"{target}|{git_info['workspace_fingerprint']}|{stamp}".encode()).hexdigest()[:6]
    run_id = args.run_id or f"rev-{stamp}-{short_hash}"

    if args.state_dir:
        run_dir = Path(args.state_dir).resolve()
    elif git_root is not None:
        common = detect_git_common_dir(git_root)
        run_dir = (common / "ee-review" / run_id) if common else (Path(tempfile.gettempdir()) / "ee-review" / run_id)
    else:
        run_dir = Path(tempfile.gettempdir()) / "ee-review" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "2",
        "run_id": run_id,
        "created_at": now_iso(),
        "current_round": 1,
        "target": str(target),
        "mode": args.mode,
        "level": detected["effective_level"],
        "level_bump_reason": detected["level_bump_reason"],
        "material": detected["material"],
        "task_id": args.task_id or run_id,
        "dri": args.dri or "",
        "reviewer": args.reviewer or "",
        "intent_card": args.intent_card or "",
        "journeys": detected["journeys"],
        "intent_context": detected["intent_context"],
        "target_url": args.target_url or "",
        "applied_overlays": effective_cfg["applied_overlays"],
        **git_info,
        "signals": detected["signals"],
        "repo_context": detected["repo_context"],
        "file_buckets": detected["file_buckets"],
    }
    atomic_write_json(run_dir / "manifest.json", manifest)
    atomic_write_json(run_dir / "effective_config.json", effective_cfg)
    atomic_write_json(round_dir(run_dir, 1) / "plan.json", plan)

    required_lanes = [lp["id"] for lp in plan["lanes"] if lp["required"]]
    active_rule_ids = {lp["id"]: [r["id"] for r in lp["active_rules"]] for lp in plan["lanes"] if lp["required"]}
    total_active = sum(len(v) for v in active_rule_ids.values())
    ov_names = [o["name"] for o in effective_cfg["applied_overlays"]]
    record_event(
        run_dir, "RUN_INIT",
        f"✓ 初始化完成: {manifest['mode']}/{manifest['level']} @ {manifest['head_sha']} — 激活 {len(required_lanes)} 模块 / {total_active} 条规则"
        + (f"（叠加配置: {', '.join(ov_names)}）" if ov_names else ""),
        round_num=1, status="INIT",
        details={"required_lanes": required_lanes, "total_active_rules": total_active, "overlays": ov_names},
    )

    progress = compute_progress(run_dir, manifest, plan, {})
    auto_na_lanes = {lp["id"]: lp["auto_na_reason"] for lp in plan["lanes"] if not lp["required"]}
    runner_path = str((EE_ROOT / "scripts" / "review_runner.py").resolve())
    next_cmd = f'python3 "{runner_path}" next --run "{run_dir}" --emit-prompts'

    result = {
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "round": 1,
        "mode": manifest["mode"],
        "level": manifest["level"],
        "level_bump_reason": manifest["level_bump_reason"],
        "applied_overlays": effective_cfg["applied_overlays"],
        "head_sha": manifest["head_sha"],
        "base_ref": manifest["base_ref"],
        "workspace_fingerprint": manifest["workspace_fingerprint"],
        "diff_stats": manifest["diff_stats"],
        "signals": manifest["signals"],
        "required_lanes": required_lanes,
        "active_rule_ids": active_rule_ids,
        "total_active_rules": total_active,
        "auto_na_lanes": auto_na_lanes,
        "progress_log_path": str(run_dir / "progress.log"),
        "next_command": next_cmd,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[LOG {short_ts()}][R1] ✓ Stage 0 初始化完成: {run_id}")
        if ov_names:
            print(f"  Overlays:  {', '.join(ov_names)}")
        if manifest["level_bump_reason"]:
            print(f"  LevelBump: {manifest['level_bump_reason']}")
        print(f"  Run dir:   {run_dir}")
        print(f"  Log file:  {run_dir / 'progress.log'}")
        print()
        print(render_progress_board(progress))
        print(f"\nNext step:\n  {next_cmd}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, _, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner status: {exc}", file=sys.stderr)
        return 2
    progress = compute_progress(run_dir, manifest, plan, results)
    if args.json:
        print(json.dumps(progress, ensure_ascii=False, indent=2))
    else:
        print(render_progress_board(progress))
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, _, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner log: {exc}", file=sys.stderr)
        return 2
    events = read_events(run_dir)
    if args.tail and args.tail > 0:
        events = events[-args.tail:]
    progress = compute_progress(run_dir, manifest, plan, results)
    if args.json:
        print(json.dumps({"run_id": manifest["run_id"], "round": manifest["current_round"], "events": events, "progress": progress}, ensure_ascii=False, indent=2))
    else:
        print(render_progress_board(progress))
        print("\n过程日志 (events.jsonl):")
        for ev in events:
            print(f"  [{short_ts(ev['ts'])}][R{ev['round']}] {ev['message']}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, _, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner start: {exc}", file=sys.stderr)
        return 2
    rnum = int(manifest["current_round"])
    lp = next((x for x in plan["lanes"] if x["id"] == args.lane), None)
    if lp is None or not lp["required"]:
        print(f"review_runner start: lane '{args.lane}' is not a required lane", file=sys.stderr)
        return 2
    if not lane_prompt_meta_path(run_dir, rnum, args.lane).exists():
        print(f"review_runner start: prompt not issued for '{args.lane}'; run next first", file=sys.stderr)
        return 2
    started = {"lane_id": args.lane, "round": rnum, "started_at": now_iso(), "worker": args.worker or ""}
    atomic_write_json(lane_started_path(run_dir, rnum, args.lane), started)
    evt = record_event(
        run_dir, "LANE_STARTED",
        f"→ 开始执行: {args.lane}" + (f" (worker={args.worker})" if args.worker else ""),
        round_num=rnum, phase_id=lp["phase"], lane_id=args.lane, status="RUNNING",
    )
    if args.json:
        print(json.dumps({"ok": True, "event": evt}, ensure_ascii=False, indent=2))
    else:
        print(f"[LOG {short_ts(evt['ts'])}][R{rnum}] {evt['message']}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, effective_cfg, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner next: {exc}", file=sys.stderr)
        return 2
    progress = compute_progress(run_dir, manifest, plan, results)
    runner_path = str((EE_ROOT / "scripts" / "review_runner.py").resolve())

    if progress["stale_workspace"]:
        msg = f"Workspace changed since Round {progress['round']} init ({progress['workspace_fingerprint']} -> {progress['live_fingerprint']}). Run `python3 \"{runner_path}\" recheck --run \"{run_dir}\"`."
        if args.json:
            print(json.dumps({"ok": False, "stale_workspace": True, "message": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"review_runner next: {msg}", file=sys.stderr)
        return 2

    if progress["all_complete"]:
        finalize_cmd = f'python3 "{runner_path}" finalize --run "{run_dir}"'
        payload = {"ok": True, "action": "finalize", "progress": f"{progress['total_completed']}/{progress['total_required']}", "finalize_command": finalize_cmd}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(render_progress_board(progress))
            print(f"\n[LOG {short_ts()}][R{progress['round']}] ★ 全部必检模块与规则已完成，可执行最终裁决：\n  {finalize_cmd}")
        return 0

    ready = progress["ready_lanes"]
    if args.lane:
        ready = [lp for lp in ready if lp["id"] == args.lane]
        if not ready:
            print(f"review_runner next: lane '{args.lane}' is not currently ready/unlocked", file=sys.stderr)
            return 2

    dispatched: list[dict[str, Any]] = []
    for lp in ready:
        info = issue_prompt_for_lane(run_dir, manifest, effective_cfg, plan, results, lp["id"])
        item = {
            "lane_id": lp["id"],
            "title": lp["title"],
            "owner_skill": lp["owner_skill"],
            "can_parallel": lp["can_parallel"],
            "active_rule_ids": [r["id"] for r in lp.get("active_rules", [])],
            "prompt_token": info["prompt_token"],
            "prompt_path": info["prompt_path"],
            "submit_command": f'python3 "{runner_path}" submit --run "{run_dir}" --lane {lp["id"]} --input -',
            "prompt_text": info["prompt_text"] if args.inline else None,
        }
        if info.get("blind_prompt_path"):
            item["blind_prompt_path"] = info["blind_prompt_path"]
        dispatched.append(item)

    progress = compute_progress(run_dir, manifest, plan, results)
    active_phase = progress["active_phase"]
    can_run_concurrently = len(dispatched) > 1 and all(d["can_parallel"] for d in dispatched)
    out = {
        "ok": True,
        "action": "execute_lanes",
        "run_id": progress["run_id"],
        "round": progress["round"],
        "progress": f"{progress['total_completed']}/{progress['total_required']}",
        "rules_progress": f"{progress['total_checked_rules']}/{progress['total_active_rules']}",
        "active_phase": active_phase,
        "can_run_concurrently": can_run_concurrently,
        "early_stop_available": progress["has_blocking_findings"],
        "ready_lanes": [{k: v for k, v in d.items() if k != "prompt_text" or args.inline} for d in dispatched],
    }

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(render_progress_board(progress))
        print(f"\n[LOG {short_ts()}][R{progress['round']}] → 当前阶段: {active_phase['title']} ({'可并发派发' if can_run_concurrently else '执行就绪模块'})")
        if progress["has_blocking_findings"]:
            print(f'  Early-stop: python3 "{runner_path}" finalize --run "{run_dir}" --early-stop --reason "..."')
        for d in dispatched:
            print(f"  - {d['lane_id']} ({d['title']}) [token={d['prompt_token']}]")
            print(f"    Rules:  {', '.join(d['active_rule_ids'])}")
            print(f"    Prompt: {d['prompt_path']}")
            print(f"    Submit: {d['submit_command']}")
        if args.inline or (len(dispatched) == 1 and not args.emit_prompts):
            for d in dispatched:
                print("\n" + "=" * 72)
                print(d["prompt_text"] or Path(d["prompt_path"]).read_text(encoding="utf-8"))
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    args.inline = True
    args.emit_prompts = False
    args.json = False
    return cmd_next(args)


def cmd_submit(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, _, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner submit: {exc}", file=sys.stderr)
        return 2

    if args.input:
        try:
            raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"review_runner submit: invalid JSON input: {exc}", file=sys.stderr)
            return 2
        if not isinstance(parsed, dict):
            print("review_runner submit: input JSON must be an object", file=sys.stderr)
            return 2
        payload = parsed
    else:
        payload = {
            "lane_id": args.lane,
            "prompt_token": args.token or "",
            "status": args.status,
            "reviewer": args.reviewer or manifest.get("reviewer") or "",
            "summary": args.summary or "",
            "checks": [json.loads(c) for c in (args.check_json or [])],
            "evidence": list(args.evidence or []),
            "commands_run": list(args.cmd_run or []),
            "reason": args.reason or "",
            "findings": [json.loads(f) for f in (args.finding_json or [])],
            "unrun_checks": [json.loads(u) for u in (args.unrun_json or [])],
            "unverified_items": list(args.unverified or []),
            "test_gaps": list(args.test_gap or []),
            "open_questions": list(args.question or []),
            "residual_risks": list(args.risk or []),
            "meta": json.loads(args.meta_json) if args.meta_json else {},
        }

    payload["lane_id"] = args.lane
    errors = validate_lane_submission(run_dir, manifest, plan, results, args.lane, payload)
    if errors:
        if args.json:
            print(json.dumps({"ok": False, "lane_id": args.lane, "errors": errors}, ensure_ascii=False, indent=2))
        else:
            print(f"review_runner submit: rejected submission for '{args.lane}':", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
        return 2

    rnum = int(manifest["current_round"])
    prev_progress = compute_progress(run_dir, manifest, plan, results)
    prev_phase_done = {p["id"]: p["complete"] for p in prev_progress["phases"]}

    record = {
        "lane_id": args.lane,
        "round": rnum,
        "head_sha": manifest["head_sha"],
        "workspace_fingerprint": manifest["workspace_fingerprint"],
        "prompt_token": payload.get("prompt_token") or read_json(lane_prompt_meta_path(run_dir, rnum, args.lane))["prompt_token"],
        "status": payload["status"],
        "reviewer": str(payload.get("reviewer", "")).strip(),
        "summary": str(payload.get("summary", "")).strip(),
        "checks": payload["checks"],
        "evidence": [str(e).strip() for e in payload.get("evidence", []) if str(e).strip()],
        "commands_run": [str(c).strip() for c in payload.get("commands_run", []) if str(c).strip()],
        "findings": payload.get("findings", []),
        "open_questions": [str(q).strip() for q in payload.get("open_questions", []) if str(q).strip()],
        "test_gaps": [str(g).strip() for g in payload.get("test_gaps", []) if str(g).strip()],
        "unverified_items": [str(u).strip() for u in payload.get("unverified_items", []) if str(u).strip()],
        "unrun_checks": payload.get("unrun_checks", []),
        "residual_risks": [str(r).strip() for r in payload.get("residual_risks", []) if str(r).strip()],
        "reason": str(payload.get("reason", "")).strip(),
        "meta": payload.get("meta", {}),
        "recorded_at": now_iso(),
    }
    atomic_write_json(lane_result_path(run_dir, rnum, args.lane), record)

    results[args.lane] = record
    progress = compute_progress(run_dir, manifest, plan, results)
    lp = next(x for x in plan["lanes"] if x["id"] == args.lane)

    sym = {"PASS": "✓", "FAIL": "✗", "BLOCKED": "!", "N/A": "-"}[record["status"]]
    pass_cnt = sum(1 for c in record["checks"] if c["status"] == "PASS")
    done_evt = record_event(
        run_dir, "LANE_DONE",
        f"{sym} 模块已完成: {args.lane} [{record['status']}] ({pass_cnt}/{len(record['checks'])} 规则通过, findings={len(record['findings'])}) — {record['summary']}",
        round_num=rnum, phase_id=lp["phase"], lane_id=args.lane, status=record["status"],
        details={"rules_checked": len(record["checks"]), "findings_count": len(record["findings"])},
    )

    milestone_logs = [f"[LOG {short_ts(done_evt['ts'])}][R{rnum}] {done_evt['message']}"]
    for ph in progress["phases"]:
        if ph["id"] == lp["phase"] and ph["complete"] and not prev_phase_done.get(ph["id"], False):
            nxt_hint = f"下一步解锁: {progress['active_phase']['title']}" if progress["active_phase"] else "所有阶段完成，可执行 finalize"
            ph_evt = record_event(
                run_dir, "PHASE_DONE",
                f"★ 阶段已完成: {ph['title']} ({ph['completed_count']}/{ph['required_count']}) -> {nxt_hint}",
                round_num=rnum, phase_id=ph["id"], status="DONE",
            )
            milestone_logs.append(f"[LOG {short_ts(ph_evt['ts'])}][R{rnum}] {ph_evt['message']}")

    runner_path = str((EE_ROOT / "scripts" / "review_runner.py").resolve())
    next_action = "finalize" if progress["all_complete"] else "next"
    next_cmd = f'python3 "{runner_path}" {next_action} --run "{run_dir}"'

    resp = {
        "ok": True,
        "lane_id": args.lane,
        "status": record["status"],
        "rules_checked": len(record["checks"]),
        "progress": f"{progress['total_completed']}/{progress['total_required']}",
        "rules_progress": f"{progress['total_checked_rules']}/{progress['total_active_rules']}",
        "all_complete": progress["all_complete"],
        "milestone_logs": milestone_logs,
        "next_action": next_action,
        "next_command": next_cmd,
    }
    if args.json:
        print(json.dumps(resp, ensure_ascii=False, indent=2))
    else:
        for line in milestone_logs:
            print(line)
        print()
        print(render_progress_board(progress))
        print(f"\nNext step: {next_cmd}")
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, _, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner finalize: {exc}", file=sys.stderr)
        return 2

    progress = compute_progress(run_dir, manifest, plan, results)
    if progress["stale_workspace"]:
        msg = "workspace changed since round init; run `recheck` before finalizing"
        if args.json:
            print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False, indent=2))
        else:
            print(f"review_runner finalize: {msg}", file=sys.stderr)
        return 2

    missing_lanes = [lp["id"] for lp in plan["lanes"] if lp["required"] and lp["id"] not in results]
    if missing_lanes:
        if not args.early_stop:
            msg = f"cannot finalize: required lanes incomplete: {', '.join(missing_lanes)}"
            if args.json:
                print(json.dumps({"ok": False, "error": msg, "missing_lanes": missing_lanes}, ensure_ascii=False, indent=2))
            else:
                print(f"review_runner finalize: {msg}", file=sys.stderr)
            return 2
        if not progress["has_blocking_findings"]:
            msg = "--early-stop is only allowed after recording a FAIL lane or P0/P1/blocking finding"
            if args.json:
                print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False, indent=2))
            else:
                print(f"review_runner finalize: {msg}", file=sys.stderr)
            return 2
        if not str(args.reason or "").strip():
            msg = "--early-stop requires --reason"
            if args.json:
                print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False, indent=2))
            else:
                print(f"review_runner finalize: {msg}", file=sys.stderr)
            return 2

    approvals = json.loads(Path(args.approvals).read_text(encoding="utf-8")) if args.approvals else []
    exceptions = json.loads(Path(args.exceptions).read_text(encoding="utf-8")) if args.exceptions else []

    evidence_pkg = build_evidence_package(manifest, plan, results, approvals, exceptions)
    gate_mod = load_gate_check_module()
    shape_errors = gate_mod.validate_shape(evidence_pkg)
    if shape_errors:
        print(f"review_runner finalize: internal evidence package invalid: {shape_errors}", file=sys.stderr)
        return 2
    gate_result = gate_mod.evaluate(evidence_pkg)

    has_fail = any(
        res["status"] == "FAIL" or any(f.get("severity") in BLOCKING_SEVERITIES for f in res.get("findings", []))
        for res in results.values()
    )
    has_blocked = any(res["status"] == "BLOCKED" for res in results.values())
    screenshot_only = any(res.get("meta", {}).get("material_type") == "screenshot" for res in results.values())
    enforce_gate = manifest["mode"] in ("delivery", "release")

    if has_fail or args.early_stop:
        verdict, verdict_zh, exit_code = "NOT_READY", "还不能交付（存在阻断问题，请按各维度优化建议修复）", 1
    elif has_blocked or screenshot_only or (enforce_gate and not gate_result["releasable"]):
        verdict, verdict_zh, exit_code = "INSUFFICIENT_EVIDENCE", "缺证据没法判断（存在未完成检查或缺少必需审批/独立验收人）", 1
    else:
        verdict, verdict_zh, exit_code = "READY", "可以交付（所有必检维度与逐条规则已有对应版本证据且无阻断问题）", 0

    rnum = int(manifest["current_round"])
    record_event(
        run_dir, "RUN_FINALIZED",
        f"★ 总决完成: {verdict} ({progress['total_completed']}/{progress['total_required']} 维度, {progress['total_checked_rules']}/{progress['total_active_rules']} 规则)"
        + (f" [early-stop: {args.reason}]" if args.early_stop else ""),
        round_num=rnum, status=verdict,
    )

    pkg_path = round_dir(run_dir, rnum) / "evidence-package.json"
    report_path = round_dir(run_dir, rnum) / "report.md"
    html_path = Path(args.html_out).resolve() if getattr(args, "html_out", None) else (round_dir(run_dir, rnum) / "report.html")
    atomic_write_json(pkg_path, evidence_pkg)
    report_text = render_final_report(run_dir, manifest, plan, results, verdict, verdict_zh, gate_result if enforce_gate else None, args.reason if args.early_stop else None)
    atomic_write_text(report_path, report_text)

    html_mod = load_html_renderer_module()
    html_text = html_mod.render_html_report(
        manifest, plan, results, read_events(run_dir),
        verdict=verdict,
        verdict_zh=verdict_zh,
        gate_result=gate_result if enforce_gate else None,
        early_stop_reason=args.reason if args.early_stop else None,
    )
    atomic_write_text(html_path, html_text)

    if args.json:
        print(json.dumps({
            "ok": True,
            "run_id": manifest["run_id"],
            "round": rnum,
            "verdict": verdict,
            "verdict_zh": verdict_zh,
            "early_stop": bool(args.early_stop),
            "missing_lanes": missing_lanes,
            "rules_checked": progress["total_checked_rules"],
            "rules_active": progress["total_active_rules"],
            "evidence_package_path": str(pkg_path),
            "report_path": str(report_path),
            "report_html_path": str(html_path),
            "progress_log_path": str(run_dir / "progress.log"),
            "gate_check": gate_result,
            "report": report_text,
        }, ensure_ascii=False, indent=2))
    else:
        print(report_text)
        print(f"Artifacts saved:\n  HTML:     {html_path}\n  Markdown: {report_path}\n  Evidence: {pkg_path}\n  Log:      {run_dir / 'progress.log'}")
    return exit_code


def cmd_render(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, _, plan, results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner render: {exc}", file=sys.stderr)
        return 2
    rnum = int(manifest["current_round"])
    progress = compute_progress(run_dir, manifest, plan, results)
    has_fail = any(
        res["status"] == "FAIL" or any(f.get("severity") in BLOCKING_SEVERITIES for f in res.get("findings", []))
        for res in results.values()
    )
    has_blocked = any(res["status"] == "BLOCKED" for res in results.values())
    screenshot_only = any(res.get("meta", {}).get("material_type") == "screenshot" for res in results.values())
    if not progress["all_complete"]:
        verdict, verdict_zh = "IN_PROGRESS", f"质检进行中（已完成 {progress['total_completed']}/{progress['total_required']} 维度）"
    elif has_fail:
        verdict, verdict_zh = "NOT_READY", "还不能交付（存在阻断问题）"
    elif has_blocked or screenshot_only:
        verdict, verdict_zh = "INSUFFICIENT_EVIDENCE", "缺证据没法判断"
    else:
        verdict, verdict_zh = "READY", "可以交付"

    html_path = Path(args.out).resolve() if args.out else (round_dir(run_dir, rnum) / "report.html")
    html_mod = load_html_renderer_module()
    html_text = html_mod.render_html_report(manifest, plan, results, read_events(run_dir), verdict=verdict, verdict_zh=verdict_zh)
    atomic_write_text(html_path, html_text)
    if args.json:
        print(json.dumps({"ok": True, "run_id": manifest["run_id"], "round": rnum, "verdict": verdict, "report_html_path": str(html_path)}, ensure_ascii=False, indent=2))
    else:
        print(f"HTML report rendered: {html_path} ({verdict})")
    return 0


def _lane_touched_by_files(lane_plan: dict[str, Any], effective_cfg: dict[str, Any], files: list[str]) -> bool:
    """Declarative recheck invalidation based on lane.recheck_policy + file_bucket/patterns."""
    policy = lane_plan.get("recheck_policy") or "on_file_match"
    if policy == "always":
        return True
    if not files:
        return False
    if policy == "on_any_fix":
        return True
    if policy == "on_failure_only":
        return False

    lower = [f.lower() for f in files]
    sp = effective_cfg.get("signal_patterns", DEFAULT_SIGNAL_PATTERNS)
    bucket = lane_plan.get("file_bucket")
    if bucket == "react_files":
        return any(Path(f).suffix.lower() in {".tsx", ".jsx", ".ts", ".js"} for f in files)
    if bucket == "ui_files":
        return any(Path(f).suffix.lower() in UI_EXTENSIONS or any(t in lf for t in ("components/", "pages/", "views/", "ui/", "design.md")) for f, lf in zip(files, lower))
    if bucket == "security_files":
        return any(any(p in lf for p in sp.get("security", [])) for lf in lower)
    if bucket == "arch_dx_ai_files":
        return any(any(p in lf for p in sp.get("arch_data", []) + sp.get("dx", []) + sp.get("ai_automation", [])) for lf in lower)
    if bucket == "security_arch_files":
        return any(any(p in lf for p in sp.get("security", []) + sp.get("arch_data", []) + sp.get("dx", []) + sp.get("ai_automation", [])) for lf in lower)
    if bucket == "release_files":
        return any(any(p in lf for p in sp.get("release", [])) for lf in lower)
    pats = lane_plan.get("trigger_path_patterns") or []
    if pats:
        return any(any(p in lf for p in pats) for lf in lower)
    return True


def cmd_recheck(args: argparse.Namespace) -> int:
    run_dir = Path(args.run).resolve()
    try:
        manifest, effective_cfg, prev_plan, prev_results = load_run_state(run_dir)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"review_runner recheck: {exc}", file=sys.stderr)
        return 2

    prev_round = int(manifest["current_round"])
    new_round = prev_round + 1
    prev_head = manifest["head_sha"]

    fix_files: list[str] = []
    if manifest.get("is_git_repo"):
        git_root = Path(manifest["git_root"])
        new_git = parse_git_state(git_root, manifest.get("base_ref"))
        if prev_head and prev_head != "UNCOMMITTED":
            delta = run_git(git_root, ["diff", "--name-only", prev_head, "HEAD"])
            if delta.returncode == 0:
                fix_files.extend(line.strip() for line in delta.stdout.splitlines() if line.strip())
        wt = run_git(git_root, ["diff", "--name-only", "HEAD"])
        if wt.returncode == 0:
            fix_files.extend(line.strip() for line in wt.stdout.splitlines() if line.strip())
        fix_files = sorted(set(fix_files))
        manifest.update({k: new_git[k] for k in ("head_sha", "workspace_fingerprint", "changed_files", "dirty_files", "diff_stats", "pre_probes")})
    else:
        new_label = args.commit or f"{prev_head}-r{new_round}"
        manifest["head_sha"] = new_label
        manifest["workspace_fingerprint"] = f"nogit:{new_label}"

    force_lanes = {s.strip() for s in (args.force_lanes or "").split(",") if s.strip()}
    carryover_findings = [{**f, "lane_id": lid} for lid, res in prev_results.items() for f in res.get("findings", [])]

    carried_forward: list[str] = []
    reopened: list[str] = []
    new_results: dict[str, dict[str, Any]] = {}
    for lp in prev_plan["lanes"]:
        lid = lp["id"]
        if not lp["required"]:
            continue
        prev = prev_results.get(lid)
        if lid in force_lanes or prev is None or prev["status"] in ("FAIL", "BLOCKED") or _lane_touched_by_files(lp, effective_cfg, fix_files):
            reopened.append(lid)
        else:
            carried = {**prev, "round": new_round, "carried_from_round": prev_round, "head_sha": manifest["head_sha"], "workspace_fingerprint": manifest["workspace_fingerprint"]}
            atomic_write_json(lane_result_path(run_dir, new_round, lid), carried)
            carried_forward.append(lid)
            new_results[lid] = carried

    manifest["current_round"] = new_round
    atomic_write_json(run_dir / "manifest.json", manifest)
    atomic_write_json(round_dir(run_dir, new_round) / "plan.json", prev_plan)
    atomic_write_json(round_dir(run_dir, new_round) / "carryover_findings.json", {"from_round": prev_round, "fix_files": fix_files, "findings": carryover_findings})

    record_event(
        run_dir, "ROUND_RECHECK",
        f"↻ 启动复审 Round {new_round} @ {manifest['head_sha']} — 重开 {len(reopened)} 模块 ({', '.join(reopened)}), 结转 {len(carried_forward)} 模块",
        round_num=new_round, status="RECHECK",
        details={"reopened": reopened, "carried_forward": carried_forward, "fix_files": fix_files},
    )

    progress = compute_progress(run_dir, manifest, prev_plan, new_results)
    runner_path = str((EE_ROOT / "scripts" / "review_runner.py").resolve())
    next_cmd = f'python3 "{runner_path}" next --run "{run_dir}" --emit-prompts'
    out = {
        "ok": True,
        "run_id": manifest["run_id"],
        "round": new_round,
        "head_sha": manifest["head_sha"],
        "workspace_fingerprint": manifest["workspace_fingerprint"],
        "fix_files": fix_files,
        "reopened_lanes": reopened,
        "carried_forward_lanes": carried_forward,
        "carryover_findings_count": len(carryover_findings),
        "next_command": next_cmd,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"[LOG {short_ts()}][R{new_round}] ↻ 增量复审已启动: 重开 {reopened}, 结转 {carried_forward}")
        print()
        print(render_progress_board(progress))
        print(f"\nNext step:\n  {next_cmd}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Script-driven composable post-development review runner.")
    sub = parser.add_subparsers(dest="action", required=True)

    p_cat = sub.add_parser("catalog", help="List effective phases, modules, and numbered rules (with optional overlays).")
    p_cat.add_argument("--target", default=None, help="Optional project path to auto-discover .evolution overlays.")
    p_cat.add_argument("--overlay", action="append", help="Overlay JSON path (repeatable).")
    p_cat.add_argument("--no-auto-overlays", action="store_true")
    p_cat.add_argument("--enable-lane", action="append")
    p_cat.add_argument("--disable-lane", action="append")
    p_cat.add_argument("--phase", default=None)
    p_cat.add_argument("--lane", default=None)
    p_cat.add_argument("--json", action="store_true")

    p_init = sub.add_parser("init", help="Inspect target repo/diff, compose overlays, and initialize a review run.")
    p_init.add_argument("--target", default=".")
    p_init.add_argument("--base", default=None)
    p_init.add_argument("--mode", choices=VALID_MODES, default="pr")
    p_init.add_argument("--level", choices=VALID_LEVELS, default="L1")
    p_init.add_argument("--material", choices=VALID_MATERIALS, default="auto")
    p_init.add_argument("--overlay", action="append", help="Dynamic review overlay JSON path (repeatable).")
    p_init.add_argument("--no-auto-overlays", action="store_true", help="Ignore .evolution/ and EE_PRIVATE_ASSETS overlays.")
    p_init.add_argument("--enable-lane", action="append", help="Force-enable a lane ID for this run.")
    p_init.add_argument("--disable-lane", action="append", help="Disable an optional lane: <lane_id>:<reason>.")
    p_init.add_argument("--ui-interactive", action="store_true")
    p_init.add_argument("--no-ui-interactive", action="store_true")
    p_init.add_argument("--journey", action="store_true", help="Force-enable User Journey / Product Cognition review (RV-BIZ-05 & RV-UI-05).")
    p_init.add_argument("--no-journey", action="store_true", help="Explicitly disable User Journey review for pure copy/visual tweaks.")
    p_init.add_argument("--has-release", action="store_true")
    p_init.add_argument("--task-id", default=None)
    p_init.add_argument("--dri", default=None)
    p_init.add_argument("--reviewer", default=None)
    p_init.add_argument("--intent-card", default=None)
    p_init.add_argument("--target-url", default=None)
    p_init.add_argument("--files", default=None)
    p_init.add_argument("--commit", default=None)
    p_init.add_argument("--run-id", default=None)
    p_init.add_argument("--state-dir", default=None)
    p_init.add_argument("--json", action="store_true")

    p_status = sub.add_parser("status", help="Show live visual progress board for phases, modules, and rules.")
    p_status.add_argument("--run", required=True)
    p_status.add_argument("--json", action="store_true")

    p_log = sub.add_parser("log", help="Show chronological process log timeline and current progress board.")
    p_log.add_argument("--run", required=True)
    p_log.add_argument("--tail", type=int, default=0, help="Show last N events (0 = all).")
    p_log.add_argument("--json", action="store_true")

    p_start = sub.add_parser("start", help="Mark a dispatched lane as RUNNING in the process log.")
    p_start.add_argument("--run", required=True)
    p_start.add_argument("--lane", required=True)
    p_start.add_argument("--worker", default=None, help="Optional worker/subagent identifier.")
    p_start.add_argument("--json", action="store_true")

    p_next = sub.add_parser("next", help="Unlock ready lanes and dynamically stitch itemized prompts.")
    p_next.add_argument("--run", required=True)
    p_next.add_argument("--lane", default=None)
    p_next.add_argument("--emit-prompts", action="store_true")
    p_next.add_argument("--inline", action="store_true")
    p_next.add_argument("--json", action="store_true")

    p_prompt = sub.add_parser("prompt", help="Print the dynamically stitched prompt for one ready lane.")
    p_prompt.add_argument("--run", required=True)
    p_prompt.add_argument("--lane", required=True)

    p_submit = sub.add_parser("submit", help="Validate per-rule checks[], record lane result, and emit milestone logs.")
    p_submit.add_argument("--run", required=True)
    p_submit.add_argument("--lane", required=True)
    p_submit.add_argument("--input", default=None)
    p_submit.add_argument("--token", default=None)
    p_submit.add_argument("--status", choices=VALID_LANE_STATUSES, default=None)
    p_submit.add_argument("--reviewer", default=None)
    p_submit.add_argument("--summary", default=None)
    p_submit.add_argument("--reason", default=None)
    p_submit.add_argument("--check-json", action="append")
    p_submit.add_argument("--evidence", action="append")
    p_submit.add_argument("--command", dest="cmd_run", action="append")
    p_submit.add_argument("--finding-json", action="append")
    p_submit.add_argument("--unrun-json", action="append")
    p_submit.add_argument("--unverified", action="append")
    p_submit.add_argument("--test-gap", action="append")
    p_submit.add_argument("--question", action="append")
    p_submit.add_argument("--risk", action="append")
    p_submit.add_argument("--meta-json", default=None)
    p_submit.add_argument("--json", action="store_true")

    p_fin = sub.add_parser("finalize", help="Verify all lanes/rules, run gate_check, and emit HTML + Markdown report.")
    p_fin.add_argument("--run", required=True)
    p_fin.add_argument("--early-stop", action="store_true")
    p_fin.add_argument("--reason", default=None)
    p_fin.add_argument("--approvals", default=None)
    p_fin.add_argument("--exceptions", default=None)
    p_fin.add_argument("--html-out", default=None, help="Optional custom output path for report.html.")
    p_fin.add_argument("--json", action="store_true")

    p_ren = sub.add_parser("render", help="Render HTML visual report (supports in-progress live snapshot or final).")
    p_ren.add_argument("--run", required=True)
    p_ren.add_argument("--out", default=None, help="Optional custom output path for report.html.")
    p_ren.add_argument("--json", action="store_true")

    p_re = sub.add_parser("recheck", help="Start next incremental review round after fixes.")
    p_re.add_argument("--run", required=True)
    p_re.add_argument("--force-lanes", default=None)
    p_re.add_argument("--commit", default=None)
    p_re.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "catalog": cmd_catalog,
        "init": cmd_init,
        "status": cmd_status,
        "log": cmd_log,
        "start": cmd_start,
        "next": cmd_next,
        "prompt": cmd_prompt,
        "submit": cmd_submit,
        "finalize": cmd_finalize,
        "render": cmd_render,
        "recheck": cmd_recheck,
    }
    return dispatch[args.action](args)


if __name__ == "__main__":
    raise SystemExit(main())
