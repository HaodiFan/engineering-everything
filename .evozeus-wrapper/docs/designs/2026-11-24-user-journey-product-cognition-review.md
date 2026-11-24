# Design Doc: User Journey–Driven Product Cognition Review (v0.18.0 Draft)

## Related issue

- Issue: Owner post-v0.17.0 architectural review (Product Cognition & User Journey blind spot)
- What was unsatisfactory:
  - Existing review (L0–L3) excels at catching implementation bugs, code smells, security flaws, and local UI defects, but assumes the product design direction itself is correct.
  - Products organized by internal technical modules instead of user workflows (e.g., tab-hopping broken journeys, missing main task entry, blocking AI waits, premature decisions, cross-step context loss) can pass all unit/E2E/Bombadil/UI checks.
  - `schemas/intent-card.schema.json` lacked an implementation-agnostic `journeys[]` contract, and `scripts/review_runner.py` only validated `RV-UI-03` as a single prose check instead of structured coverage across all 14 UX groups (70 rules).
- Expected behavior:
  - Keep the existing 13 runtime skills, 3 lifecycle gates, 3 execution phases (`1 -> 4 parallel -> 1`), and 6 clustered review dimensions (no 7th dimension or 14th skill).
  - Add an optional implementation-agnostic `journeys[]` contract to `schemas/intent-card.schema.json` and guide `engineering-product-definition` to derive journeys before defining UI modules.
  - Add `references/user-journey.md` defining L0–L5 review hierarchy, strict trigger boundaries, Journey-First anti-anchoring review order, 8 Product Anti-patterns (`AP-01`..`AP-08`), Blind User Walkthrough (7 observations), and anti-over-review guardrails (positive control for good standard admin tools).
  - Add conditional rules `RV-BIZ-05` (`business_acceptance`) and `RV-UI-05` (`ui_ux_experience`) (48 -> 50 `RV-*` rules), physically scrubbed code-free Blind Walkthrough prompts (`ui_ux_experience.blind.md`), 14-group structured 70-rule `meta.ux_coverage` validation, Expected-vs-Actual Journey HTML visualization, and a Negative Product Benchmark eval scenario.

## Optimization goal

Enable Engineering Everything to detect L4/L5 Product Cognition and User Journey defects (zero-bug but wrong product logic) via anti-anchoring Expected-vs-Actual comparison and Blind User Walkthrough, enforce structured 14-group 70-rule UX coverage in `review_runner.py`, and pass well-designed standard admin workbenches without over-review.

## Direction

Embed Journey Review upstream inside existing dimensions (`business_acceptance` + `ui_ux_experience`) and Gate 1 (`engineering-product-definition` + `intent-card.schema.json`) with strict signal gating (`has_journey_surface`) so copy tweaks, CSS polish, and internal backend refactors incur zero extra overhead, while workflow/navigation/workspace/async changes get physically code-free Blind Walkthrough prompts and structured machine validation.

## Implementation plan

- Skill sections to change:
  - `skills/engineering-product-definition/SKILL.md`: derive implementation-agnostic `journeys[]` before defining screens/modules when work affects user workflows.
  - `skills/engineering-review-release/SKILL.md`: integrate `RV-BIZ-05` and `RV-UI-05` into Phase 2 dimensions.
  - `skills/engineering-ui-ux-audit/SKILL.md`: run physically isolated Blind Walkthrough first when `RV-UI-05` activates, and submit 14-group `meta.ux_coverage`.
- Files to update:
  - `references/user-journey.md` (new canonical reference, distributed to `engineering-product-definition`, `engineering-review-release`, `engineering-ui-ux-audit`)
  - `schemas/intent-card.schema.json`
  - `data/review_pipeline.json`, `data/reference_distribution.yaml`, `references/review-rules.md`, `references/review-pipeline.md`, `README.md`
  - `scripts/review_runner.py`, `scripts/review_report_html.py`
  - `evals/scenarios/product-journey-negative-benchmark.md`, `evals/scenarios/review-script-driven-pipeline.md`, `tests/test_review_runner.py`
- Backward compatibility:
  - `intent-card.schema.json` keeps `schema_version: "1"` and makes `journeys` optional; existing Intent Cards remain valid.
  - Copy-only, CSS-only, and non-UI refactors automatically skip `RV-BIZ-05` and `RV-UI-05` (`AUTO_NA`).

## Verification plan

- Source discovery check: `python3 scripts/self_evolve.py doctor --json`
- Manual checks: preview rendered `report.html` in dark/light modes verifying Expected vs Actual Journey comparison (e.g., 7 steps vs 3 steps), 8 anti-pattern chips, Blind Walkthrough 7-observation strip, and 14-group 70-rule UX coverage matrix.
- Regression cases: `python3 -m unittest discover -s tests` covering 50-rule 1:1 parity, trigger precision (copy/CSS tweaks skip journey rules), physically code-free blind prompt verification, 14-group UX coverage validation, journey validators, and HTML rendering.
- Preflight command: `sync_references.py --check`, `eval_scenarios.py validate`, `skill_doctor.py`, `self_evolve.py check --strict-install`, `lesson.py validate`, `py_compile scripts/*.py`.

## Release plan

- Changelog entry: recorded under `## [Unreleased]` pending owner verification before cutting `v0.18.0`.
- Release tag: `v0.18.0` (after owner approval)
- Release description summary: Product Cognition & User Journey–Driven Review (`RV-BIZ-05`, `RV-UI-05`, Blind Walkthrough code-free prompt, 8 Product Anti-patterns, 14-group 70-rule UX coverage validation, Expected vs Actual Journey HTML view, and Negative Product Benchmark).

## Risks and rollback

- Risk: Over-triggering Journey Review on small tweaks or falsely criticizing good standard admin tables; mitigated by strict `has_journey_surface` gating (`--no-journey` override) and explicit positive-control anti-over-review guardrails in `references/user-journey.md` and `evals/scenarios/product-journey-negative-benchmark.md`.
- Rollback plan: revert the commit or pin `v0.17.0` and run `python3 scripts/install.py relink --target all`.
