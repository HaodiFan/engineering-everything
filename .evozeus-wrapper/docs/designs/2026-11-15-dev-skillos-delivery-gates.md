# Design Doc: Dev SkillOS — three delivery gates

## Related issue

- Issue: not yet filed (creating a GitHub issue is an external action awaiting owner approval).
- What was unsatisfactory: Engineering Everything routes a single agent well, but team delivery still depends on the founder to expand requirements and to accept results. Basic gates and product taste are not transferred; corrections are rarely reused (3 lessons, 1 pattern as of `df92e70`).
- Expected behavior: a DRI and their agent expand a coarse intent into an intent card, pass a fixed, evidence-based quality flow judged by an independent reviewer, and only escalate genuinely non-delegable decisions; useful corrections become reusable assets.

## Optimization goal

Lower founder minutes per accepted feature without lowering quality, by making Intent, Quality and Evolution explicit lifecycle checkpoints with machine-checkable evidence. Source: the internal "Evolution-Driven Development" handoff (2026-11-15) and owner decisions: first scenario = coarse intent to team delivery; users = the team, owner accepts; private content stays outside this repo; hosts = Codex, Claude Code, Agents.

## Direction

Reuse existing members instead of adding skills (SkillOS member boundaries unchanged):

- Gate 1 -> `engineering-product-definition` + `engineering-execution-planning`
- Gate 2 -> `engineering-review-release` (fixed flow) with `engineering-build-verify` collecting evidence and `engineering-architecture-design` running design verification (D)
- Gate 3 -> `engineering-skill-evolution`

Protocol and method knowledge live in two new root references; runtime skills only point to them. Deterministic checks (gate_check) replace prose where the rule is mechanical. No hooks: gates trigger on task lifecycle so all hosts behave the same.

## Implementation plan

- Skill sections to change: router (three gates section), bootloader (resume restores gate), product-definition, execution-planning, build-verify, architecture-design, review-release, skill-evolution.
- Files to update: `references/delivery-gates.md`, `references/verification-methods.md`, `references/output-contracts.md`, `data/reference_distribution.yaml`, `data/routes.yaml`, `schemas/*.schema.json`, `scripts/gate_check.py`, `scripts/install.py`, tests, eval scenarios, README, versions.
- Backward compatibility: single-agent flows unchanged; gate behavior applies to team delivery tasks. `--target both` keeps its meaning.

## Verification plan

- Source discovery check: `python3 scripts/skill_doctor.py --json`, `python3 scripts/sync_references.py --check --json`.
- Manual checks: run the three new eval scenarios in Codex and Claude Code.
- Regression cases: existing 7 eval scenarios; `python3 -m unittest discover -s tests`.
- Preflight command: `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py structure`.

## Release plan

- Changelog entry: `[Unreleased]` in `.evozeus-wrapper/CHANGELOG.md`.
- Release tag: `v0.14.0` after merge and a manual pilot on one real project.
- Release description summary: Dev SkillOS three gates, verification method catalog, evidence package checker, Claude install target.

## Risks and rollback

- Risk: protocol overhead on small tasks (mitigated by the L0 light path); thresholds and L0-L3 boundaries are unvalidated drafts until the pilot; behavior evals are manual.
- Rollback plan: revert the PR; installed skills are symlinks, so reverting the source restores 0.13.0 behavior immediately.
