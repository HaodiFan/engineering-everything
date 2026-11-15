# Changelog

All notable changes to engineering-everything are recorded here.

Wrapper harness migrations are recorded under `.evozeus-wrapper/docs/migrations/`. Add them here only when the migration also changes this Skill's release contract.

## [Unreleased]

### Skill changes

- New sub-skill `engineering-ui-ux-audit` (`0.16.0`): rule-based UI/UX review imported from the owner's `ui-ux-audit` skill — 69 numbered rules, each with trigger, boundary, evidence, severity, fix and re-check; findings are 通过 / 不通过 / 不适用 / 未验证, no aesthetic scores, and anything a screenshot cannot prove is marked unverified. References ship as `ui-ux-*.md`. New route `ui-ux-audit` (aliases `/ui-audit`, `/ux-review`), router table row, and the review skill hands "用起来顺吗 / 看起来对吗" to it during delivery gates.
- Added `references/react-doctor.md`: when and how to run the open-source React Doctor CLI (millionco, Modified MIT) in review, build-verify, refactoring and UI audit — changed-scope scans for PRs, `--no-telemetry --no-supply-chain` by default, re-grade findings under EE review rules, never treat the score as a verdict, never run its `install` / `ci install` without the user asking. Listed in `verification-methods.md`.
- Two behavior eval scenarios: `ui-ux-audit-evidence-boundary`, `react-review-uses-react-doctor`.

## [v0.15.1] - 2026-11-16

### Skill changes

- Fix (`0.15.1`): code review could not load its smell catalog. `code-review-standards.md` tells the agent to use `refactoring-rules.md`, but only `engineering-refactoring` shipped it, so reviews from `engineering-review-release` and eight other skills silently skipped it. `refactoring-rules.md` now ships wherever the review standards do, and `engineering-review-release` lists it explicitly.
- `data/reference_distribution.yaml` gained `requires:`; `sync_references.py` fails when a reference ships without one it depends on (`code-review-standards.md` requires `refactoring-rules.md`).
- Every sub-skill now says where to find references it mentions by name but does not ship (the source repo `references/`, two levels above the skill's real path) and to say so if not found. `skill_doctor.py` enforces this and errors on `references/X.md` mentions that exist nowhere.

## [v0.15.0] - 2026-11-16

### Skill changes

- Flattened the entry path (`0.15.0`): the bootloader is now a thin hand-off (session resume + go to the router) with no references of its own; the router is the single file to read before work and carries the route table, hard rules and the five "对人表达" rules inline; every sub-skill reference now states when to read it. Before: ~10 required reads across 4 hops; after: router + sub-skill, references on demand.
- Removed ~10k lines of duplicated runtime references: `lessons.md` and `patterns-skill.md` now ship only with `engineering-skill-evolution`, `prompts-guide.md` only where projects get scaffolded, `codex-tools.md` is root-only (folded into the router), `route-contract.md` moved to the router. Shared references point at lessons by name and route lesson capture to issue-first.
- Moved the EvoZeus-CoEvolve release-loop governance from the bootloader into `engineering-skill-evolution`; added a note that the harness activation path is relative to the source repo root (the block itself is harness-owned and unchanged).
- `skill_doctor.py` gained an entry-depth check (no up-front reference reads in the entry files, every listed reference says when to read it, router table matches `data/routes.yaml`), with tests.
- Dev SkillOS (`0.14.0`): added the three-gate delivery lifecycle (Intent / Quality / Evolution) for team tasks in `references/delivery-gates.md`, with L0-L3 authorization, decision escalation, a fixed Gate 2 flow (D / G0-G4 / CR / R) and the public-core vs private-assets boundary.
- Added `references/verification-methods.md`: a trigger-based catalog of mature verification methods (TLA+/TLC and P, property-based testing, Pact, mutation testing, Playwright, Bombadil, axe-core, visual regression, PRR, staged rollout, DORA).
- Added schemas for intent card, evidence package, decision escalation, evolution candidate and project gate profile, plus `scripts/gate_check.py` (conservative releasability check) and tests.
- Wired the gates into the router, bootloader, product-definition, execution-planning, build-verify, architecture-design, review-release and skill-evolution skills; extended `output-contracts.md` with Gate 1/2/3 fields; added three behavior eval scenarios.
- `scripts/install.py` gained `--target claude` and `--target all`.
- Added `scripts/update_check.py`: a session-start check (Claude Code and Codex `SessionStart` hooks via `install-hook`) that compares the local EE version with GitHub `main` and the local EvoZeus version with its channel manifest; silent when current or offline, throttled to one network check per hour, check-only (never pulls or installs).
- Business-first rewrite after owner review ("too technical, too rigid"): gates are now described as 想清楚 / 确认做对了 / 学到了什么 in plain business language; internal codes (G0-G4, L0-L3, PASS/BLOCKED) are confined to evidence files; added the "对人表达" rules (conclusion first, only relevant items, length proportional to the task) that apply to all outputs; Gate output fields renamed to 档位 / 需要拍板的事 / 交付结论 / 证据 / 上线准备 / 沉淀结论; verification catalog gained business validation (demo, user trials, data reconciliation, post-release business metrics) and business-side release readiness.
- Upgraded the managed EvoZeus-CoEvolve Harness from `v0.12.1` to `v0.15.0`.
- Added the canonical Harness Skill, notice policy, migration contract, and wrapper notice renderer.
- Replaced the legacy wrapper prelude with one canonical activation block while preserving the Engineering Everything business flow.
- Upgraded the managed EvoZeus-CoEvolve Harness from `v0.11.4` to `v0.12.1`.
- Added the per-invocation EvoZeus runtime identity header and staged feedback authorization contract to the wrapper-owned bootloader prelude.

### Feedback / Issues

- Owner-authorized batch Harness upgrade following the EvoZeus-CoEvolve `v0.12.1` release.

### Verification

- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py structure`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py runtime`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py structure`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py identity --json`
- `git diff --check`

## [v0.13.0] - 2026-07-25

### Skill changes

- Demoted root `SKILL.md`: runtime entrypoints now live only under `skills/*/SKILL.md`.
- Updated package, self-evolution, and wrapper preflight gates to use `.codex-plugin/plugin.json` plus the plugin skill library as the package contract.
- Updated wrapper/dashboard docs to describe plugin-first source governance.
- Migrated the EvoZeus-CoEvolve harness from scattered layout `v0.3.0` to consolidated layout `v0.11.2`.
- Kept `skills/using-engineering-everything/SKILL.md` as the recommended bootloader and preserved all direct sub-Skill entrypoints.
- Aligned `scripts/install.py --target both` with its documented contract by creating canonical sub-Skill symlinks for Codex and Agents on fresh installs.

### Feedback / Issues

- Owner request: use Engineering Everything as the first non-project Skillware feasibility target for EvoZeus-CoEvolve.
- Related issue: https://github.com/HaodiFan/engineering-everything/issues/17
- Migration recovery: the first structure gate exposed missing legacy policy files and root-only runtime pointer assumptions; CoEvolve v0.11.2 fixed both without weakening validation.

### Verification

- `python3 scripts/sync_references.py --check --json`
- `python3 scripts/eval_scenarios.py validate --json`
- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/self_evolve.py doctor --json`
- `python3 scripts/lesson.py validate`
- `python3 -m unittest discover -s tests`
- `python3 -m py_compile scripts/*.py`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py structure`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything --current-tag v0.13.0`

### Release notes

- Major pre-1.0 package transition: plugin-first runtime entrypoints replace the retired root Skill entry.
- CoEvolve adds lifecycle governance and a recommended-entry preflight; it does not change Engineering Everything routing decisions.
- Fresh plugin-library installs now maintain one canonical source through symlinks instead of copied runtime directories.
- Native per-Skill invocation hooks remain unavailable; the bootloader preflight depends on instruction compliance.
- License remains `UNLICENSED`.

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
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py structure`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything --current-tag v0.11.0`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py release --tag v0.11.0 --release-notes /tmp/engineering-everything-v0.11.0-release-notes.md --skip-gh`

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
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py structure`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything --current-tag v0.10.0`
- `python3 .evozeus-wrapper/scripts/evozeus_wrapper_preflight.py release --tag v0.10.0 --release-notes release-notes.md --skip-gh`

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
