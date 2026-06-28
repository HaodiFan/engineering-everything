#!/usr/bin/env python3
"""Validate managed reference distribution copies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ALLOWED_ROOT_ONLY_STATUSES = {"canonical", "legacy"}


@dataclass
class Entry:
    source: str
    mode: str | None
    status: str | None
    owner: str | None
    targets: list[str]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_scalar(value: str) -> str | list[str]:
    value = value.strip()
    if value == "[]":
        return []
    return value.strip('"').strip("'")


def load_manifest(path: Path) -> tuple[str, list[Entry]]:
    canonical_root = ""
    entries: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and ":" in raw_line:
            key, value = raw_line.split(":", 1)
            if key == "canonical_root":
                canonical_root = str(parse_scalar(value))
            elif key == "entries":
                continue
            else:
                raise ValueError(f"unknown top-level key: {key}")
            current_list = None
            continue
        if raw_line.startswith("  - "):
            if current:
                entries.append(current)
            current = {}
            current_list = None
            item = raw_line[4:]
            if ":" not in item:
                raise ValueError(f"invalid entry line: {raw_line}")
            key, value = item.split(":", 1)
            current[key.strip()] = parse_scalar(value)
            continue
        if raw_line.startswith("      - ") and current is not None:
            if current_list is None:
                raise ValueError(f"list item without key: {raw_line}")
            current.setdefault(current_list, [])
            assert isinstance(current[current_list], list)
            current[current_list].append(str(parse_scalar(raw_line[8:])))
            continue
        if raw_line.startswith("    ") and current is not None:
            item = raw_line[4:]
            if ":" not in item:
                raise ValueError(f"invalid field line: {raw_line}")
            key, value = item.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                current[key] = []
                current_list = key
            else:
                current[key] = parse_scalar(value)
                current_list = None
            continue
        raise ValueError(f"unsupported manifest indentation: {raw_line}")

    if current:
        entries.append(current)

    parsed_entries = [
        Entry(
            source=str(entry.get("source", "")),
            mode=str(entry["mode"]) if "mode" in entry else None,
            status=str(entry["status"]) if "status" in entry else None,
            owner=str(entry["owner"]) if "owner" in entry else None,
            targets=list(entry.get("targets", [])) if isinstance(entry.get("targets", []), list) else [],
        )
        for entry in entries
    ]
    return canonical_root, parsed_entries


def valid_source(source: str) -> bool:
    path = Path(source)
    return (
        source.endswith(".md")
        and not path.is_absolute()
        and ".." not in path.parts
        and len(path.parts) == 1
    )


def valid_target_name(target: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]+", target))


def declared_target_path(root: Path, entry: Entry, target: str) -> Path:
    return root / "skills" / target / "references" / entry.source


def check_distribution(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "data/reference_distribution.yaml"
    if not manifest_path.exists():
        return ["missing data/reference_distribution.yaml"]

    try:
        canonical_root, entries = load_manifest(manifest_path)
    except ValueError as exc:
        return [f"invalid reference distribution manifest: {exc}"]

    if canonical_root != "references":
        errors.append("canonical_root must be references")

    root_references = {path.name for path in (root / "references").glob("*.md")}
    declared_sources: set[str] = set()
    declared_targets: dict[Path, str] = {}
    root_only_sources: set[str] = set()

    for entry in entries:
        if not valid_source(entry.source):
            errors.append(f"invalid source path: {entry.source}")
            continue
        if entry.source in declared_sources:
            errors.append(f"duplicate source entry: {entry.source}")
        declared_sources.add(entry.source)

        source_path = root / "references" / entry.source
        if not source_path.exists():
            errors.append(f"missing source reference: references/{entry.source}")

        if entry.targets:
            if entry.mode != "exact-copy":
                errors.append(f"source {entry.source} with targets must use mode: exact-copy")
            for target in entry.targets:
                if not valid_target_name(target):
                    errors.append(f"invalid target skill name for {entry.source}: {target}")
                    continue
                target_path = declared_target_path(root, entry, target)
                if target_path in declared_targets:
                    errors.append(
                        f"duplicate target {target_path.relative_to(root)} in {declared_targets[target_path]} and {entry.source}"
                    )
                declared_targets[target_path] = entry.source
                if not target_path.exists():
                    errors.append(f"missing target reference: {target_path.relative_to(root)}")
                    continue
                if source_path.exists() and target_path.read_bytes() != source_path.read_bytes():
                    errors.append(f"reference drift: {target_path.relative_to(root)} != references/{entry.source}")
        else:
            if entry.status not in ALLOWED_ROOT_ONLY_STATUSES:
                errors.append(f"root-only source {entry.source} must declare status canonical or legacy")
            root_only_sources.add(entry.source)

    for root_source in sorted(root_references - declared_sources):
        errors.append(f"unclassified root reference: references/{root_source}")

    for source in sorted(declared_sources - root_references):
        errors.append(f"declared source is not present under references/: {source}")

    runtime_references = sorted((root / "skills").glob("*/references/*.md"))
    runtime_reference_paths = set(runtime_references)
    for path in runtime_references:
        if path not in declared_targets:
            errors.append(f"undeclared runtime reference copy: {path.relative_to(root)}")

    for source in sorted(root_only_sources):
        runtime_copies = [path for path in runtime_references if path.name == source]
        for path in runtime_copies:
            errors.append(f"root-only reference has runtime copy: {path.relative_to(root)}")

    managed_targets = {path.relative_to(root).as_posix() for path in declared_targets}
    route_refs = re.findall(
        r"^\s+-\s+(skills/[a-z0-9-]+/references/[^\s#]+\.md)\s*$",
        (root / "data/routes.yaml").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    for reference in route_refs:
        if not (root / reference).exists():
            errors.append(f"route references missing file: {reference}")
        elif reference not in managed_targets:
            errors.append(f"route references unmanaged file: {reference}")

    for skill_file in sorted((root / "skills").glob("*/SKILL.md")):
        skill_root = skill_file.parent
        text = skill_file.read_text(encoding="utf-8")
        for match in re.finditer(r"`(references/[^`]+?\.md)`", text):
            reference = skill_root / match.group(1)
            if not reference.exists():
                errors.append(f"{skill_file.relative_to(root)} references missing file: {match.group(1)}")
            elif reference.relative_to(root).as_posix() not in managed_targets:
                errors.append(f"{skill_file.relative_to(root)} references unmanaged file: {match.group(1)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Engineering Everything reference distribution.")
    parser.add_argument("--check", action="store_true", help="Validate without modifying files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors = check_distribution(repo_root())
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        for error in errors:
            print(f"error: {error}")
        print(f"sync_references: {len(errors)} error(s)")
    else:
        print("sync_references: ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
