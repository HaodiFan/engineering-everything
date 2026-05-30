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


def default_destinations(target: str) -> list[Path]:
    home = Path.home()
    destinations: list[Path] = []
    if target in {"codex", "both"}:
        destinations.append(home / ".codex/skills" / SKILL_NAME)
    if target in {"agents", "both"}:
        destinations.append(home / ".agents/skills" / SKILL_NAME)
    return destinations


def copy_package(source: Path, dest: Path, delete: bool, dry_run: bool) -> str:
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
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )
    return f"installed {dest}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Engineering Everything.")
    parser.add_argument(
        "--target",
        choices=["codex", "agents", "both"],
        default="both",
        help="Destination skill directory group.",
    )
    parser.add_argument(
        "--dest",
        action="append",
        type=Path,
        help="Explicit destination directory. Can be passed multiple times.",
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Do not delete the existing destination before copying.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying files.")
    args = parser.parse_args()

    source = package_dir()
    destinations = args.dest or default_destinations(args.target)
    if not destinations:
        print("install: no destinations selected", file=sys.stderr)
        return 1
    for dest in destinations:
        print(copy_package(source, dest, delete=not args.no_delete, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
