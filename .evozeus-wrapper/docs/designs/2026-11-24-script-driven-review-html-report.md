# Design Doc: Script-Driven Clustered Review Pipeline & HTML Visual Report

## Related issue

- Issue: Owner iterative review workflow feedback (post-v0.16.0)
- What was unsatisfactory:
  - Post-development review relied on prompt-only discipline, making it easy for agents to skip checks, forget numbered rules, or give an unstructured wall of Markdown that humans struggle to scan for per-dimension action items.
  - Review steps were static and fragmented across 10 overlapping labels without real-time process logs or project/company-level overlay customization.
- Expected behavior:
  - Provide a deterministic script-driven review orchestrator (`scripts/review_runner.py`) with 3 execution phases, 6 MECE business-readable dimensions, and 48 itemized atomic rules (`RV-BASE-01`..`RV-REL-03`, plus 70 `UX-*` rules in UI review).
  - Support 4-layer dynamic overlay composition (`data/review_pipeline.json` → `$EE_PRIVATE_ASSETS` → `<repo>/.evolution/` → CLI `--overlay`) without allowing hard gates (`engineering_baseline`, `security_architecture`) to be silently waived.
  - Persist concurrent-safe append-only process logs (`events.jsonl` / `progress.log`) and live progress boards during review execution.
  - Automatically generate a zero-dependency interactive HTML visual report (`report.html` via `scripts/review_report_html.py`) on `finalize` (plus live `render`) that clearly presents per-dimension optimization cards, gaps/unverified items, collapsible rule audit tables, and process timeline.

## Optimization goal

Every post-development review run orchestrated by `engineering-review-release` or `engineering-ui-ux-audit` enforces itemized rule accounting across the 6 clustered dimensions, blocks missing/inconsistent rule evidence mechanically, emits live progress milestones, and outputs a human-readable `report.html` alongside `report.md` and `evidence-package.json`.

## Direction

Move review state, phase gating, prompt stitching, rule validation, process logging, and HTML report generation from prose instructions into pure Python stdlib scripts (`scripts/review_runner.py` + `scripts/review_report_html.py`) backed by declarative JSON (`data/review_pipeline.json`) and an overlay schema (`schemas/review-overlay.schema.json`). Cluster the 10 granular checks into 6 MECE dimensions arranged as `1 (preflight baseline) -> 4 concurrent (business / code quality / security & architecture / UI & UX) -> 1 (release readiness)` so concurrent subagents maximize speed without sacrificing strict gating.

## Implementation plan

- Skill sections to change:
  - `skills/engineering-review-release/SKILL.md`: adopt 3-phase 6-dimension script-driven review loop, live progress reporting, and `report.html` presentation.
  - `skills/engineering-ui-ux-audit/SKILL.md`: integrate as `ui_ux_experience` dimension with Bombadil (`RV-BOMB-01..03`) + UI/UX 70 rules (`UX-VIS-09`).
- Files to update:
  - `data/review_pipeline.json`, `schemas/review-overlay.schema.json`
  - `scripts/review_runner.py`, `scripts/review_report_html.py`
  - `references/review-rules.md`, `references/review-pipeline.md`, `data/reference_distribution.yaml` and synced runtime copies
  - `evals/scenarios/review-script-driven-pipeline.md`, `tests/test_review_runner.py`, `README.md`
- Backward compatibility:
  - Existing routes, `scripts/gate_check.py`, `schemas/evidence-package.schema.json`, and non-script fallback guidance remain compatible.

## Verification plan

- Source discovery check: `python3 scripts/self_evolve.py doctor --json` and `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- Manual checks: inspect rendered dark/light `report.html` layout and filter interactions across all 6 dimensions.
- Regression cases: `python3 -m unittest discover -s tests` (53 unit tests covering 1:1 rule parity, signal activation, concurrent submissions, Bombadil/React Doctor/screenshot boundary guards, overlay composition, recheck, and XSS-safe HTML generation).
- Preflight command: `python3 scripts/sync_references.py --check --json`, `python3 scripts/eval_scenarios.py validate --json`, `python3 scripts/skill_doctor.py --json`, `python3 scripts/self_evolve.py check --strict-install --json`, `python3 scripts/lesson.py validate`, `python3 -m py_compile scripts/*.py`.

## Release plan

- Changelog entry: promote Bombadil explicit review, `UX-VIS-09` unfamiliar-language self-explanation, and the script-driven 6-dimension review pipeline + HTML visual report under `## [v0.17.0] - 2026-11-24`.
- Release tag: `v0.17.0`
- Release description summary: Script-driven 6-dimension review pipeline with 48 numbered `RV-*` rules, dynamic overlays, live process logs, interactive `report.html` optimization report, explicit Bombadil UI exploration, and `UX-VIS-09` unfamiliar-language self-explanation check.

## Risks and rollback

- Risk: Host environments without Python/Shell cannot execute `scripts/review_runner.py`; mitigated by explicit fallback instructions in `SKILL.md` and `references/review-pipeline.md`.
- Rollback plan: `git revert` the v0.17.0 release commit (or checkout `v0.16.0`) and run `python3 scripts/install.py relink --target all`.
