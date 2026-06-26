#!/usr/bin/env python3
"""Install or update Engineering Everything in local agent skill directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SKILL_NAME = "engineering-everything"


def package_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def default_skill_roots(target: str) -> list[Path]:
    home = Path.home()
    destinations: list[Path] = []
    if target in {"codex", "both"}:
        destinations.append(home / ".codex/skills")
    if target in {"agents", "both"}:
        destinations.append(home / ".agents/skills")
    return destinations


def default_legacy_destinations(target: str) -> list[Path]:
    return [root / SKILL_NAME for root in default_skill_roots(target)]


def discover_skill_packages(source: Path) -> list[Path]:
    skills_dir = source / "skills"
    if not skills_dir.exists():
        return [source]
    packages = [path for path in sorted(skills_dir.iterdir()) if (path / "SKILL.md").exists()]
    return packages or [source]


def copy_tree(source: Path, dest: Path, delete: bool, dry_run: bool) -> str:
    source = source.resolve()
    dest = dest.expanduser().resolve()
    if source == dest:
        return f"skip {dest} (source and destination are the same)"
    if dry_run:
        action = "replace" if dest.exists() and delete else "copy"
        return f"would {action} {source} -> {dest}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and delete:
        shutil.rmtree(dest)
    shutil.copytree(
        source,
        dest,
        dirs_exist_ok=not delete,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store"),
    )
    return f"installed {dest}"


def install_library(source: Path, dest_root: Path, delete: bool, dry_run: bool) -> list[str]:
    results: list[str] = []
    for skill_package in discover_skill_packages(source):
        results.append(copy_tree(skill_package, dest_root / skill_package.name, delete, dry_run))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Engineering Everything.")
    parser.add_argument(
        "--target",
        choices=["codex", "agents", "both"],
        default="both",
        help="Destination skill directory group.",
    )
    parser.add_argument(
        "--layout",
        choices=["library", "legacy"],
        default="library",
        help="Install skills/* as separate skills, or install the whole repo as the legacy single skill.",
    )
    parser.add_argument(
        "--dest",
        action="append",
        type=Path,
        help="Explicit destination. In library layout this is a skills root; in legacy layout this is the package destination.",
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Do not delete the existing destination before copying.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying files.")
    args = parser.parse_args()

    source = package_dir()
    destinations = args.dest or (
        default_skill_roots(args.target)
        if args.layout == "library"
        else default_legacy_destinations(args.target)
    )
    if not destinations:
        print("install: no destinations selected", file=sys.stderr)
        return 1
    for dest in destinations:
        if args.layout == "library":
            for result in install_library(source, dest, delete=not args.no_delete, dry_run=args.dry_run):
                print(result)
        else:
            print(copy_tree(source, dest, delete=not args.no_delete, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
