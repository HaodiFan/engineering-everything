# Changelog

All notable changes to engineering-everything are recorded here.

Wrapper harness migrations are recorded under `docs/wrapper-migrations/`. Add them here only when the migration also changes this Skill's release contract.

## [Unreleased]

### Skill changes

- None yet.

### Feedback / Issues

- None yet.

### Verification

- None yet.

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
