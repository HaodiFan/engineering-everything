#!/usr/bin/env python3
"""Self-contained HTML visual report renderer for Engineering Everything Review Runner.

Produces a scannable, dimension-clustered, action-oriented HTML report explaining:
  1. Executive verdict & headline KPI counts
  2. Overview matrix of every Review Dimension and what needs optimization
  3. Per-dimension optimization action cards (severity, rule_id, location, impact, fix, re-check)
  4. Collapsible sub-grouped rule-by-rule audit table (RV-* / UX-* / custom)
  5. Gate check & chronological process log timeline

Zero external dependencies; compatible with standalone browsers AND T3 Code html_render
(no vh units, no height:100% on html/body, uses theme CSS variables with clean fallbacks).
"""

from __future__ import annotations

import html
from typing import Any

BLOCKING_SEVERITIES = {"P0", "P1", "blocking"}
SEVERITY_ORDER = {"P0": 0, "blocking": 0, "P1": 1, "major": 2, "P2": 2, "minor": 3, "P3": 3, "suggestion": 4}
SEVERITY_META = {
    "P0": ("阻断 P0", "sev-p0", "blocking"),
    "blocking": ("阻断", "sev-p0", "blocking"),
    "P1": ("严重 P1", "sev-p1", "blocking"),
    "P2": ("优化 P2", "sev-p2", "optimize"),
    "major": ("重要", "sev-p2", "optimize"),
    "P3": ("建议 P3", "sev-p3", "suggestion"),
    "minor": ("一般", "sev-p3", "suggestion"),
    "suggestion": ("建议", "sev-p3", "suggestion"),
}
STATUS_META = {
    "PASS": ("通过", "st-pass"),
    "FAIL": ("需修复", "st-fail"),
    "BLOCKED": ("缺证据", "st-blocked"),
    "N/A": ("不适用", "st-na"),
    "AUTO_NA": ("自动跳过", "st-na"),
    "CONFIG_DISABLED": ("配置关闭", "st-na"),
    "PENDING": ("待执行", "st-pending"),
    "RUNNING": ("执行中", "st-pending"),
    "PROMPT_ISSUED": ("进行中", "st-pending"),
}


def esc(val: Any) -> str:
    return html.escape("" if val is None else str(val), quote=True)


def _short_ts(iso: str) -> str:
    return iso[11:19] if len(iso) >= 19 else iso


def _verdict_style(verdict: str) -> tuple[str, str, str]:
    if verdict == "READY":
        return "可以交付", "verdict-ready", "所有必检维度与激活规则已有对应版本证据且无阻断问题。"
    if verdict == "NOT_READY":
        return "还不能交付", "verdict-fail", "存在阻断级问题，请按下方各维度的「必改优化项」修复后运行 recheck 复审。"
    if verdict == "IN_PROGRESS":
        return "质检进行中", "verdict-progress", "当前为实时过程快照，仍有维度正在执行或待解锁。"
    return "缺证据没法判断", "verdict-blocked", "存在未完成检查、仅截图边界或缺少必需审批/独立验收人，请按下方补证项补齐。"


def render_html_report(
    manifest: dict[str, Any],
    plan: dict[str, Any],
    results: dict[str, dict[str, Any]],
    events: list[dict[str, Any]],
    *,
    verdict: str,
    verdict_zh: str = "",
    gate_result: dict[str, Any] | None = None,
    early_stop_reason: str | None = None,
) -> str:
    verdict_label, verdict_cls, verdict_hint = _verdict_style(verdict)
    headline = verdict_zh or verdict_label

    # Aggregate findings & stats per dimension
    all_findings: list[dict[str, Any]] = []
    total_active_rules = 0
    total_passed_rules = 0
    total_failed_rules = 0
    total_blocked_rules = 0
    total_gaps = 0

    dimensions_data: list[dict[str, Any]] = []
    for lp in plan.get("lanes", []):
        lid = lp["id"]
        required = bool(lp.get("required"))
        active_rules = lp.get("active_rules", [])
        auto_na_rules = lp.get("auto_na_rules", [])
        res = results.get(lid)
        if not required:
            st = str(lp.get("initial_status") or "AUTO_NA")
        elif res is not None:
            st = str(res.get("status", "PENDING"))
        else:
            st = "PENDING"

        findings = sorted(
            [{**f, "lane_id": lid, "lane_title": lp["title"]} for f in (res.get("findings", []) if res else [])],
            key=lambda x: SEVERITY_ORDER.get(str(x.get("severity")), 9),
        )
        all_findings.extend(findings)

        blocking_cnt = sum(1 for f in findings if f.get("severity") in BLOCKING_SEVERITIES)
        opt_cnt = len(findings) - blocking_cnt
        checks = res.get("checks", []) if res else []
        checks_by_id = {c["id"]: c for c in checks if isinstance(c, dict) and c.get("id")}

        if required:
            total_active_rules += len(active_rules)
            total_passed_rules += sum(1 for c in checks if c.get("status") == "PASS")
            total_failed_rules += sum(1 for c in checks if c.get("status") == "FAIL")
            total_blocked_rules += sum(1 for c in checks if c.get("status") == "BLOCKED")

        gaps: list[str] = []
        if res:
            for uc in res.get("unrun_checks", []):
                if isinstance(uc, dict) and uc.get("check"):
                    rem = f" → 补证：{uc['remediation']}" if uc.get("remediation") else ""
                    gaps.append(f"{uc['check']}（{uc.get('reason', '')}）{rem}")
            for uv in res.get("unverified_items", []):
                if str(uv).strip():
                    gaps.append(f"未验证：{uv}")
            for tg in res.get("test_gaps", []):
                if str(tg).strip():
                    gaps.append(f"测试缺口：{tg}")
        elif required:
            gaps.append("该维度尚未执行（提前阻断或仍在等待）")
        total_gaps += len(gaps)

        dimensions_data.append({
            "lane": lp,
            "result": res,
            "status": st,
            "findings": findings,
            "blocking_cnt": blocking_cnt,
            "opt_cnt": opt_cnt,
            "checks_by_id": checks_by_id,
            "active_rules": active_rules,
            "auto_na_rules": auto_na_rules,
            "gaps": gaps,
        })

    total_blocking = sum(1 for f in all_findings if f.get("severity") in BLOCKING_SEVERITIES)
    total_optimize = len(all_findings) - total_blocking

    # Build Dimension Overview Cards
    overview_cards: list[str] = []
    for dim in dimensions_data:
        lp = dim["lane"]
        lid = lp["id"]
        st = dim["status"]
        st_label, st_cls = STATUS_META.get(st, (st, "st-pending"))
        res = dim["result"]
        if not lp["required"]:
            action_text = f"跳过：{lp.get('auto_na_reason', '本次不涉及')}"
            pill_html = '<span class="pill pill-muted">无需处理</span>'
        else:
            pills: list[str] = []
            if dim["blocking_cnt"]:
                pills.append(f'<span class="pill pill-danger">{dim["blocking_cnt"]} 项必改</span>')
            if dim["opt_cnt"]:
                pills.append(f'<span class="pill pill-warn">{dim["opt_cnt"]} 项建议优化</span>')
            if dim["gaps"]:
                pills.append(f'<span class="pill pill-amber">{len(dim["gaps"])} 项缺口/未验</span>')
            if not pills:
                pills.append('<span class="pill pill-ok">无待优化项</span>' if st == "PASS" else f'<span class="pill pill-muted">{esc(st_label)}</span>')
            pill_html = "".join(pills)
            action_text = (res.get("summary") if res else "") or lp.get("dimension_question", "")

        passed_in_dim = sum(1 for c in (res.get("checks", []) if res else []) if c.get("status") == "PASS")
        active_cnt = len(dim["active_rules"])
        pct = int(round(100 * passed_in_dim / active_cnt)) if active_cnt else (100 if not lp["required"] else 0)
        q_text = lp.get("dimension_question", "")

        overview_cards.append(f"""
        <a class="dim-card {st_cls}-border" href="#dim-{esc(lid)}">
          <div class="dim-card-top">
            <span class="dim-title">{esc(lp['title'])}</span>
            <span class="badge {st_cls}">{esc(st_label)}</span>
          </div>
          {f'<div class="dim-question">{esc(q_text)}</div>' if q_text else ''}
          <div class="dim-summary">{esc(action_text)}</div>
          <div class="dim-meta">
            <div class="dim-pills">{pill_html}</div>
            {f'<span class="dim-ratio">{passed_in_dim}/{active_cnt} 通过</span>' if lp['required'] else ''}
          </div>
          {f'<div class="bar"><div class="bar-fill {st_cls}-bg" style="width:{pct}%"></div></div>' if lp['required'] else ''}
        </a>
        """)

    # Build Detailed Per-Dimension Optimization Sections
    detail_sections: list[str] = []
    for dim in dimensions_data:
        lp = dim["lane"]
        lid = lp["id"]
        st = dim["status"]
        st_label, st_cls = STATUS_META.get(st, (st, "st-pending"))
        res = dim["result"]

        if not lp["required"]:
            detail_sections.append(f"""
            <section class="dim-section dim-skipped" id="dim-{esc(lid)}" data-dim="{esc(lid)}" data-has-issues="false">
              <div class="dim-head">
                <div>
                  <h3>{esc(lp['title'])}</h3>
                  <div class="muted">{esc(lp.get('auto_na_reason', '本次未触发'))}</div>
                </div>
                <span class="badge {st_cls}">{esc(st_label)}</span>
              </div>
            </section>
            """)
            continue

        # Optimization cards (findings)
        findings_html_parts: list[str] = []
        for f in dim["findings"]:
            sev = str(f.get("severity", "P2"))
            sev_label, sev_cls, sev_bucket = SEVERITY_META.get(sev, (sev, "sev-p2", "optimize"))
            rid = str(f.get("rule_id", "-"))
            verif = str(f.get("verification", "")).strip()
            findings_html_parts.append(f"""
            <article class="finding-card {sev_cls}-border" data-sev="{sev_bucket}" data-dim="{esc(lid)}">
              <div class="finding-head">
                <span class="badge {sev_cls}">{esc(sev_label)}</span>
                <code class="rule-tag">{esc(rid)}</code>
                <code class="loc-tag">{esc(f.get('location', ''))}</code>
              </div>
              <div class="finding-problem">{esc(f.get('problem', ''))}</div>
              <div class="finding-grid">
                <div class="fg-item"><span class="fg-label">为什么影响</span><span>{esc(f.get('impact', ''))}</span></div>
                <div class="fg-item"><span class="fg-label">怎么优化</span><span class="fg-fix">{esc(f.get('fix', ''))}</span></div>
                {f'<div class="fg-item"><span class="fg-label">怎么复验</span><span>{esc(verif)}</span></div>' if verif else ''}
              </div>
            </article>
            """)

        if findings_html_parts:
            opt_block = f'<div class="opt-list"><div class="sub-label">本维度要优化什么（{len(findings_html_parts)} 项）</div>{"".join(findings_html_parts)}</div>'
        elif st == "PASS" and not dim["gaps"]:
            opt_block = '<div class="ok-banner">✓ 本维度已核验通过，无必须优化项。</div>'
        elif st in ("PENDING", "RUNNING", "PROMPT_ISSUED"):
            opt_block = '<div class="info-banner">→ 本维度尚未提交结论，正在等待审查完成。</div>'
        else:
            opt_block = '<div class="info-banner">本维度暂无代码缺陷发现，请关注下方待补证据或说明。</div>'

        gaps_block = ""
        if dim["gaps"]:
            items = "".join(f"<li>{esc(g)}</li>" for g in dim["gaps"])
            gaps_block = f'<div class="gap-box"><div class="sub-label">待补证据 / 未验证 / 测试缺口</div><ul>{items}</ul></div>'

        # Group rules cleanly by rule["group"]
        grouped_rules: dict[str, list[dict[str, Any]]] = {}
        for r in dim["active_rules"]:
            grp = str(r.get("group") or "检查项")
            grouped_rules.setdefault(grp, []).append(r)

        rule_tables: list[str] = []
        for grp_name, rules in grouped_rules.items():
            rows: list[str] = []
            for r in rules:
                chk = dim["checks_by_id"].get(r["id"])
                rst = str(chk["status"]) if chk else ("PENDING" if res is None else "PENDING")
                r_label, r_cls = STATUS_META.get(rst, (rst, "st-pending"))
                rnote = chk.get("note", "") if chk else "尚未核验"
                rows.append(f"""
                <tr data-rule-status="{esc(rst)}">
                  <td><code class="rule-tag">{esc(r['id'])}</code></td>
                  <td><strong>{esc(r['title'])}</strong><div class="muted small">{esc(r.get('check', ''))}</div></td>
                  <td><span class="badge {r_cls}">{esc(r_label)}</span></td>
                  <td>{esc(rnote)}</td>
                </tr>
                """)
            grp_label = grp_name if ("项" in grp_name or "条" in grp_name) else f"{grp_name}（{len(rules)} 条）"
            rule_tables.append(f"""
            <div class="rule-group">
              <div class="rule-group-title">{esc(grp_label)}</div>
              <table class="rule-table">
                <thead><tr><th style="width:112px">规则编号</th><th>检查点</th><th style="width:76px">结论</th><th style="width:168px">核查记录 / 证据</th></tr></thead>
                <tbody>{"".join(rows)}</tbody>
              </table>
            </div>
            """)

        if dim["auto_na_rules"]:
            na_items = "".join(f'<li><code>{esc(r["id"])}</code> {esc(r["title"])} — {esc(r.get("auto_na_reason", ""))}</li>' for r in dim["auto_na_rules"])
            rule_tables.append(f'<div class="auto-na-note"><div class="muted small">自动跳过子规则（{len(dim["auto_na_rules"])} 条）：</div><ul>{na_items}</ul></div>')

        open_attr = ""
        has_issues = "true" if (dim["findings"] or dim["gaps"] or st in ("FAIL", "BLOCKED")) else "false"
        summary_line = res.get("summary", "") if res else lp.get("dimension_question", "")
        reviewer_line = f"审查者：{res['reviewer']}" if (res and res.get("reviewer")) else ""

        detail_sections.append(f"""
        <section class="dim-section" id="dim-{esc(lid)}" data-dim="{esc(lid)}" data-has-issues="{has_issues}">
          <div class="dim-head">
            <div>
              <h3>{esc(lp['title'])}</h3>
              <div class="muted">{esc(summary_line)}{f' · {esc(reviewer_line)}' if reviewer_line else ''}</div>
            </div>
            <span class="badge {st_cls}">{esc(st_label)}</span>
          </div>
          {opt_block}
          {gaps_block}
          <details class="rules-details"{open_attr}>
            <summary>展开逐条规则核验明细（{len(dim['active_rules'])} 条激活{f' / {len(dim["auto_na_rules"])} 条自动跳过' if dim['auto_na_rules'] else ''}）</summary>
            {"".join(rule_tables)}
          </details>
        </section>
        """)

    # Gate check & timeline sections
    gate_block = ""
    if gate_result and gate_result.get("problems"):
        g_items = "".join(f"<li>{esc(p)}</li>" for p in gate_result["problems"])
        gate_block = f'<section class="dim-section"><div class="gap-box"><div class="sub-label">交付门禁机检阻塞项（gate_check.py）</div><ul>{g_items}</ul></div></section>'

    timeline_rows = "".join(
        f'<li><code class="ts-tag">{esc(_short_ts(ev.get("ts", "")))}</code> <span class="round-tag">R{esc(ev.get("round", 1))}</span> {esc(ev.get("message", ""))}</li>'
        for ev in events[-30:]
    )
    timeline_block = f"""
    <details class="timeline-details">
      <summary>查看质检过程日志（共 {len(events)} 条里程碑事件）</summary>
      <ul class="timeline-list">{timeline_rows or '<li>暂无过程日志。</li>'}</ul>
    </details>
    """

    overlays = manifest.get("applied_overlays") or []
    overlay_badge = f" · 叠加配置：{', '.join(o['name'] for o in overlays)}" if overlays else ""
    ds = manifest.get("diff_stats") or {}
    scope_desc = f"{manifest.get('base_ref', 'N/A')} → {manifest.get('head_sha', 'N/A')} · {ds.get('files_changed', 0)} 文件 (+{ds.get('added', 0)}/-{ds.get('deleted', 0)})"
    early_banner = f'<div class="early-banner">提前阻断说明：{esc(early_stop_reason)}（未执行维度已在报告中明确单列）</div>' if early_stop_reason else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Review Report — {esc(manifest.get('run_id', 'review'))}</title>
<style>
  :root {{
    color-scheme: light dark;
    --rv-fg: var(--foreground, #111827);
    --rv-muted: var(--muted-foreground, #6b7280);
    --rv-card: var(--card, #ffffff);
    --rv-subtle: var(--secondary, #f3f4f6);
    --rv-border: var(--border, #e5e7eb);
    --rv-primary: var(--primary, #2563eb);
    --rv-danger: var(--destructive, #dc2626);
    --rv-danger-bg: var(--destructive-surface, rgba(220, 38, 38, 0.10));
    --rv-warn: var(--warning, #d97706);
    --rv-warn-bg: var(--warning-surface, rgba(217, 119, 6, 0.12));
    --rv-ok: var(--success, #16a34a);
    --rv-ok-bg: rgba(22, 163, 74, 0.12);
    --rv-info: var(--info, #2563eb);
    --rv-info-bg: rgba(37, 99, 235, 0.10);
    --rv-code-bg: var(--code-background, rgba(127, 127, 127, 0.12));
    --rv-radius: var(--radius, 10px);
    --rv-sans: var(--font-sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", sans-serif);
    --rv-mono: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --rv-fg: var(--foreground, #f3f4f6);
      --rv-muted: var(--muted-foreground, #9ca3af);
      --rv-card: var(--card, #18181b);
      --rv-subtle: var(--secondary, #27272a);
      --rv-border: var(--border, #2e2e34);
      --rv-danger: var(--destructive, #f87171);
      --rv-warn: var(--warning, #fbbf24);
      --rv-ok: var(--success, #4ade80);
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 0;
    font-family: var(--rv-sans);
    color: var(--rv-fg);
    line-height: 1.55;
    font-size: 14px;
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }}
  .hero {{
    background: var(--rv-card);
    border: 1px solid var(--rv-border);
    border-left: 5px solid var(--rv-primary);
    border-radius: var(--rv-radius);
    padding: 16px 18px;
  }}
  .hero.verdict-ready {{ border-left-color: var(--rv-ok); }}
  .hero.verdict-fail {{ border-left-color: var(--rv-danger); }}
  .hero.verdict-blocked {{ border-left-color: var(--rv-warn); }}
  .hero.verdict-progress {{ border-left-color: var(--rv-info); }}
  .hero-top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; }}
  .hero-verdict {{ font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 10px; }}
  .hero-meta {{ font-size: 12px; color: var(--rv-muted); font-family: var(--rv-mono); }}
  .hero-hint {{ margin-top: 6px; color: var(--rv-muted); font-size: 13px; }}
  .early-banner {{
    margin-top: 10px; padding: 8px 12px; border-radius: 8px;
    background: var(--rv-danger-bg); color: var(--rv-danger); font-size: 13px; font-weight: 500;
  }}
  .kpi-row {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-top: 14px; }}
  @media (max-width: 600px) {{ .kpi-row {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  .kpi {{
    background: var(--rv-subtle); border-radius: 8px; padding: 10px 12px;
    border: 1px solid var(--rv-border);
  }}
  .kpi-num {{ font-size: 20px; font-weight: 700; line-height: 1.2; }}
  .kpi-num.danger {{ color: var(--rv-danger); }}
  .kpi-num.warn {{ color: var(--rv-warn); }}
  .kpi-num.ok {{ color: var(--rv-ok); }}
  .kpi-label {{ font-size: 12px; color: var(--rv-muted); margin-top: 2px; }}

  .section-title {{ font-size: 15px; font-weight: 700; margin: 4px 0 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
  .dim-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
  @media (max-width: 640px) {{ .dim-grid {{ grid-template-columns: 1fr; }} }}
  .dim-card {{
    display: flex; flex-direction: column; gap: 6px;
    text-decoration: none; color: inherit;
    background: var(--rv-card); border: 1px solid var(--rv-border);
    border-radius: var(--rv-radius); padding: 14px;
    transition: border-color 0.15s ease;
  }}
  .dim-card:hover {{ border-color: var(--rv-primary); }}
  .dim-card.st-fail-border {{ border-left: 4px solid var(--rv-danger); }}
  .dim-card.st-blocked-border {{ border-left: 4px solid var(--rv-warn); }}
  .dim-card.st-pass-border {{ border-left: 4px solid var(--rv-ok); }}
  .dim-card.st-na-border {{ opacity: 0.78; }}
  .dim-card-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
  .dim-title {{ font-weight: 600; font-size: 14px; }}
  .dim-question {{ font-size: 12px; color: var(--rv-muted); }}
  .dim-summary {{ font-size: 13px; }}
  .dim-meta {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-top: 2px; flex-wrap: wrap; }}
  .dim-pills {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .dim-ratio {{ font-size: 12px; color: var(--rv-muted); font-family: var(--rv-mono); }}
  .bar {{ height: 5px; border-radius: 99px; background: var(--rv-subtle); overflow: hidden; margin-top: 4px; }}
  .bar-fill {{ height: 100%; border-radius: 99px; }}
  .st-pass-bg {{ background: var(--rv-ok); }}
  .st-fail-bg {{ background: var(--rv-danger); }}
  .st-blocked-bg {{ background: var(--rv-warn); }}
  .st-pending-bg {{ background: var(--rv-info); }}

  .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
  .filter-btn {{
    border: 1px solid var(--rv-border); background: var(--rv-card); color: var(--rv-fg);
    border-radius: 999px; padding: 5px 12px; font-size: 12px; cursor: pointer; font-family: inherit;
  }}
  .filter-btn.active {{ background: var(--rv-primary); color: #fff; border-color: var(--rv-primary); }}

  .dim-section {{
    background: var(--rv-card); border: 1px solid var(--rv-border);
    border-radius: var(--rv-radius); padding: 16px;
    display: flex; flex-direction: column; gap: 12px;
  }}
  .dim-section.dim-skipped {{ padding: 12px 16px; opacity: 0.78; }}
  .dim-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }}
  .dim-head h3 {{ margin: 0; font-size: 15px; }}
  .muted {{ color: var(--rv-muted); font-size: 13px; }}
  .small {{ font-size: 12px; }}
  .sub-label {{ font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; color: var(--rv-muted); margin-bottom: 6px; }}

  .badge {{
    display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; white-space: nowrap;
  }}
  .st-pass {{ background: var(--rv-ok-bg); color: var(--rv-ok); }}
  .st-fail {{ background: var(--rv-danger-bg); color: var(--rv-danger); }}
  .st-blocked {{ background: var(--rv-warn-bg); color: var(--rv-warn); }}
  .st-na {{ background: var(--rv-subtle); color: var(--rv-muted); }}
  .st-pending {{ background: var(--rv-info-bg); color: var(--rv-info); }}
  .sev-p0, .sev-p1 {{ background: var(--rv-danger-bg); color: var(--rv-danger); }}
  .sev-p2 {{ background: var(--rv-warn-bg); color: var(--rv-warn); }}
  .sev-p3 {{ background: var(--rv-info-bg); color: var(--rv-info); }}

  .pill {{ display: inline-block; padding: 2px 7px; border-radius: 6px; font-size: 11px; font-weight: 600; }}
  .pill-danger {{ background: var(--rv-danger-bg); color: var(--rv-danger); }}
  .pill-warn {{ background: var(--rv-warn-bg); color: var(--rv-warn); }}
  .pill-amber {{ background: var(--rv-warn-bg); color: var(--rv-warn); }}
  .pill-ok {{ background: var(--rv-ok-bg); color: var(--rv-ok); }}
  .pill-muted {{ background: var(--rv-subtle); color: var(--rv-muted); }}

  .opt-list {{ display: flex; flex-direction: column; gap: 10px; }}
  .finding-card {{
    background: var(--rv-subtle); border: 1px solid var(--rv-border);
    border-left: 4px solid var(--rv-warn); border-radius: 8px; padding: 12px 14px;
  }}
  .finding-card.sev-p0-border, .finding-card.sev-p1-border {{ border-left-color: var(--rv-danger); }}
  .finding-card.sev-p3-border {{ border-left-color: var(--rv-info); }}
  .finding-head {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 6px; }}
  .rule-tag, .loc-tag, .ts-tag {{
    font-family: var(--rv-mono); font-size: 11.5px; background: var(--rv-code-bg);
    padding: 2px 6px; border-radius: 4px;
  }}
  .finding-problem {{ font-weight: 600; font-size: 14px; margin-bottom: 8px; }}
  .finding-grid {{ display: flex; flex-direction: column; gap: 5px; font-size: 13px; }}
  .fg-item {{ display: grid; grid-template-columns: 76px 1fr; gap: 8px; }}
  .fg-label {{ color: var(--rv-muted); font-weight: 600; font-size: 12px; }}
  .fg-fix {{ font-weight: 500; }}

  .ok-banner {{ padding: 9px 12px; border-radius: 8px; background: var(--rv-ok-bg); color: var(--rv-ok); font-size: 13px; font-weight: 500; }}
  .info-banner {{ padding: 9px 12px; border-radius: 8px; background: var(--rv-info-bg); color: var(--rv-info); font-size: 13px; }}
  .gap-box {{
    padding: 10px 14px; border-radius: 8px; background: var(--rv-warn-bg);
    border: 1px solid rgba(217, 119, 6, 0.25); font-size: 13px;
  }}
  .gap-box ul {{ margin: 4px 0 0 18px; padding: 0; }}

  .rules-details, .timeline-details {{
    border-top: 1px solid var(--rv-border); padding-top: 10px;
  }}
  .rules-details summary, .timeline-details summary {{
    cursor: pointer; font-size: 13px; font-weight: 600; color: var(--rv-muted); user-select: none;
  }}
  .rule-group {{ margin-top: 10px; }}
  .rule-group-title {{ font-size: 12px; font-weight: 700; color: var(--rv-muted); margin-bottom: 4px; }}
  .rule-table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  .rule-table th, .rule-table td {{
    text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--rv-border); vertical-align: top;
  }}
  .rule-table th {{ color: var(--rv-muted); font-weight: 600; background: var(--rv-subtle); }}
  .auto-na-note {{ margin-top: 8px; font-size: 12px; color: var(--rv-muted); }}
  .auto-na-note ul {{ margin: 4px 0 0 18px; padding: 0; }}
  .timeline-list {{ list-style: none; padding: 0; margin: 8px 0 0; display: flex; flex-direction: column; gap: 5px; font-size: 12.5px; }}
  .round-tag {{ font-family: var(--rv-mono); font-size: 11px; color: var(--rv-muted); }}
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero {verdict_cls}">
    <div class="hero-top">
      <div class="hero-verdict">
        <span class="badge {'st-pass' if verdict == 'READY' else ('st-fail' if verdict == 'NOT_READY' else ('st-pending' if verdict == 'IN_PROGRESS' else 'st-blocked'))}">{esc(verdict_label)}</span>
        <span>{esc(headline)}</span>
      </div>
      <div class="hero-meta">{esc(manifest.get('run_id', ''))} · Round {esc(manifest.get('current_round', 1))} · {esc(manifest.get('mode', ''))}/{esc(manifest.get('level', ''))}</div>
    </div>
    <div class="hero-hint">{esc(verdict_hint)}</div>
    <div class="hero-meta" style="margin-top:6px;">范围：{esc(scope_desc)}{esc(overlay_badge)}</div>
    {early_banner}
    <div class="kpi-row">
      <div class="kpi"><div class="kpi-num {'danger' if total_blocking else 'ok'}">{total_blocking}</div><div class="kpi-label">阻断必改（P0/P1）</div></div>
      <div class="kpi"><div class="kpi-num {'warn' if total_optimize else ''}">{total_optimize}</div><div class="kpi-label">建议优化（P2/P3）</div></div>
      <div class="kpi"><div class="kpi-num ok">{total_passed_rules}/{total_active_rules}</div><div class="kpi-label">规则已通过</div></div>
      <div class="kpi"><div class="kpi-num {'warn' if total_gaps else ''}">{total_gaps}</div><div class="kpi-label">缺口 / 未验证项</div></div>
    </div>
  </header>

  <div>
    <div class="section-title">
      <span>各维度现状与待优化总览（点击卡片直达详情）</span>
    </div>
    <div class="dim-grid">
      {"".join(overview_cards)}
    </div>
  </div>

  <div>
    <div class="section-title">
      <span>分维度优化建议与逐条核验明细</span>
      <div class="toolbar">
        <button class="filter-btn active" data-filter="all">全部显示</button>
        <button class="filter-btn" data-filter="issues-only">只看有问题/待补证维度</button>
        <button class="filter-btn" data-filter="blocking">只看阻断 P0/P1</button>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:12px;">
      {"".join(detail_sections)}
      {gate_block}
    </div>
  </div>

  <div class="dim-section">
    {timeline_block}
  </div>
</div>

<script>
(function () {{
  const buttons = document.querySelectorAll('.filter-btn');
  const sections = document.querySelectorAll('.dim-section[data-dim]');
  const cards = document.querySelectorAll('.finding-card');
  buttons.forEach(btn => {{
    btn.addEventListener('click', () => {{
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.getAttribute('data-filter');
      sections.forEach(sec => {{
        if (mode === 'all') {{
          sec.classList.remove('hidden');
        }} else if (mode === 'issues-only') {{
          sec.classList.toggle('hidden', sec.getAttribute('data-has-issues') !== 'true');
        }} else if (mode === 'blocking') {{
          const hasBlocking = sec.querySelectorAll('.finding-card[data-sev="blocking"]').length > 0;
          sec.classList.toggle('hidden', !hasBlocking);
        }}
      }});
      cards.forEach(card => {{
        if (mode === 'blocking') {{
          card.classList.toggle('hidden', card.getAttribute('data-sev') !== 'blocking');
        }} else {{
          card.classList.remove('hidden');
        }}
      }});
    }});
  }});
}})();
</script>
</body>
</html>
"""
