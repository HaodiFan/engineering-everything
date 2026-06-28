# Changelog

All notable changes to engineering-everything are recorded here.

Wrapper harness migrations are recorded under `docs/wrapper-migrations/`. Add them here only when the migration also changes this Skill's release contract.

## [Unreleased]

### Skill changes

- Demoted root `SKILL.md`: runtime entrypoints now live only under `skills/*/SKILL.md`.
- Updated package, self-evolution, and wrapper preflight gates to use `.codex-plugin/plugin.json` plus the plugin skill library as the package contract.
- Updated wrapper/dashboard docs to describe plugin-first source governance.

### Version Plan

- Recommended next release: `v0.13.0`.
- Rationale: package structure changes while runtime behavior remains routed through existing library skills.

## [v0.12.0] - 2026-06-28

### Skill changes

- Added `using-engineering-everything` as a bootloader skill for new sessions, resume handling, and task-switch rerouting.
- Added canonical output contracts, route contract notes, and Codex tool boundary references.
- Added `data/reference_distribution.yaml` plus `scripts/sync_references.py` to prevent reference drift and orphan runtime copies.
- Added behavior-eval scenario schemas under `evals/scenarios/` plus `scripts/eval_scenarios.py`.
- Extended `data/routes.yaml` with route contract fields: priority, conflicts, fallback, handoff, direct-call permission, and eval coverage.
- Hardened `scripts/install.py` with list/relink/uninstall lifecycle actions and symlink-safe removal.
- Extended `scripts/skill_doctor.py` to validate bootloader structure, route contracts, reference distribution, and eval scenario schemas.

### Feedback / Issues

- User request: learn from `obra/superpowers` plugin/skill structure and refactor Engineering Everything into a clearer AgentOS bootloader + router + subskill system.

### Verification

- `python3 scripts/sync_references.py --check --json`
- `python3 scripts/eval_scenarios.py validate --json`
- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/lesson.py validate`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py`

### Release notes

- Non-breaking minor release: `$engineering-everything` remains valid, while `$using-engineering-everything` becomes the recommended bootloader entry.
- SessionStart hook remains deferred.
- License remains `UNLICENSED`; public distribution positioning still requires owner decision.

## [v0.11.0] - 2026-06-27

### Skill changes

- Upgraded EvoZeus-wrapper harness from `v0.2.0` to `v0.3.0`.
- Added `EvoZeus-wrapper 状态检查` as the first visible section after root `SKILL.md` frontmatter.
- Kept the Engineering Everything routing and subskill behavior unchanged.

### Feedback / Issues

- User request: target Skills wrapped by EvoZeus-wrapper must check current Skill release, wrapper harness version, source contract, and remediation path before entering the main Skill flow.

### Verification

- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/self_evolve.py doctor --json`
- `python3 scripts/evozeus_wrapper_preflight.py structure`
- `python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- `python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything --current-tag v0.11.0`
- `python3 scripts/evozeus_wrapper_preflight.py release --tag v0.11.0 --release-notes /tmp/engineering-everything-v0.11.0-release-notes.md --skip-gh`

## [v0.10.0] - 2026-06-27

### Skill changes

- Adopted EvoZeus-wrapper `v0.2.0` as the GitHub-backed self-evolution harness.
- Added wrapper-managed feedback Issue, PR template, design docs, migration log, dashboard docs, and preflight checker.
- Preserved the existing Engineering Everything routing behavior while adding append-only wrapper migration rules.

### Feedback / Issues

- User request: use the current EvoZeus-wrapper to make engineering-everything self-evolving.

### Verification

- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/self_evolve.py doctor --json`
- `python3 scripts/evozeus_wrapper_preflight.py structure`
- `python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- `python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything --current-tag v0.10.0`
- `python3 scripts/evozeus_wrapper_preflight.py release --tag v0.10.0 --release-notes release-notes.md --skip-gh`

## [v0.9.10] - 2026-06-27

### Skill changes

- Split Engineering Everything into the current router-plus-subskills library shape.

### Verification

- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/self_evolve.py doctor --json`

## Release Notes Policy

Every release must include:

- The Skill behavior or harness contract that changed.
- The related feedback Issue or design doc.
- The verification performed.
- Known limitations or rollback notes.

Release tags must use `vMAJOR.MINOR.PATCH`:

- `MAJOR`: incompatible Skill behavior or output contract change.
- `MINOR`: new capability, new required evidence rule, or new harness behavior.
- `PATCH`: wording, examples, bug fixes, validation fixes, or non-breaking clarifications.
