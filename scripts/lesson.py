#!/usr/bin/env python3
"""Create and validate skill-level lesson cards."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


VALID_STATUSES = {"active", "pending-review", "deprecated"}
REQUIRED_FIELDS = ["Date", "Status", "Captured-from", "Tags"]
START_MARKER = "<!-- 真实 lessons 从这一行下方开始追加 -->"


def package_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def lessons_path() -> Path:
    return package_dir() / "references/lessons.md"


def read_lessons() -> str:
    return lessons_path().read_text(encoding="utf-8")


def body_after_marker(text: str) -> str:
    if START_MARKER not in text:
        return text
    return text.split(START_MARKER, 1)[1]


def existing_ids(text: str) -> list[int]:
    return [int(match.group(1)) for match in re.finditer(r"^### L-(\d{4}):", body_after_marker(text), re.MULTILINE)]


def next_id(text: str) -> str:
    ids = existing_ids(text)
    return f"L-{(max(ids) + 1 if ids else 1):04d}"


def split_cards(text: str) -> list[tuple[str, str]]:
    body = body_after_marker(text)
    matches = list(re.finditer(r"^### (L-\d{4}): .*$", body, re.MULTILINE))
    cards: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        cards.append((match.group(1), body[start:end].strip()))
    return cards


def validate_cards(text: str) -> list[str]:
    errors: list[str] = []
    ids = existing_ids(text)
    if ids != sorted(set(ids)):
        errors.append("lesson ids must be unique and ordered")
    for lesson_id, card in split_cards(text):
        for field in REQUIRED_FIELDS:
            if not re.search(rf"^- {re.escape(field)}:", card, re.MULTILINE):
                errors.append(f"{lesson_id} missing field: {field}")
        status_match = re.search(r"^- Status:\s*(.+)$", card, re.MULTILINE)
        if status_match:
            status = status_match.group(1).strip()
            if not (
                status in VALID_STATUSES
                or re.match(r"^superseded by L-\d{4}$", status)
            ):
                errors.append(f"{lesson_id} invalid Status: {status}")
        if "**❌ 之前的错误方案 / 默认建议**" not in card:
            errors.append(f"{lesson_id} missing wrong-solution section")
        if "**✅ 正确方案 / 用户给的纠偏**" not in card:
            errors.append(f"{lesson_id} missing corrected-solution section")
        if "**🧠 原因 / 适用条件**" not in card:
            errors.append(f"{lesson_id} missing rationale section")
    return errors


def render_card(args: argparse.Namespace, lesson_id: str) -> str:
    today = args.date or date.today().isoformat()
    return f"""### {lesson_id}: {args.title}

- Date: {today}
- Status: active
- Captured-from: {args.captured_from}
- Tags: {args.tags}

**❌ 之前的错误方案 / 默认建议**：

{args.wrong}

**✅ 正确方案 / 用户给的纠偏**：

{args.correct}

**🧠 原因 / 适用条件**：

{args.reason}

**🔁 是否可泛化**：

- [ ] 跨项目可复用（→ 候选 promote 到 patterns-skill.md）
- [ ] 仅特定项目（→ 应该写到该项目自己的 patterns.md，不是这里）
- [ ] 仅特定场景：<场景名>

**🔗 相关**：

- 影响 reference: <file>.md §<x>（如有）
- 关联 lesson: 暂无
"""


def append_card(card: str) -> None:
    path = lessons_path()
    text = path.read_text(encoding="utf-8")
    if START_MARKER not in text:
        raise SystemExit(f"missing lesson insertion marker in {path}")
    separator = "" if text.endswith("\n") else "\n"
    path.write_text(f"{text}{separator}\n{card.rstrip()}\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and validate skill lessons.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("next-id", help="Print the next lesson id.")
    sub.add_parser("validate", help="Validate existing lesson cards.")

    new_parser = sub.add_parser("new", help="Render a new lesson card.")
    new_parser.add_argument("--title", required=True)
    new_parser.add_argument("--captured-from", required=True)
    new_parser.add_argument("--tags", required=True)
    new_parser.add_argument("--wrong", required=True)
    new_parser.add_argument("--correct", required=True)
    new_parser.add_argument("--reason", required=True)
    new_parser.add_argument("--date")
    new_parser.add_argument("--append", action="store_true", help="Append the card to references/lessons.md.")

    args = parser.parse_args()
    text = read_lessons()

    if args.command == "next-id":
        print(next_id(text))
        return 0
    if args.command == "validate":
        errors = validate_cards(text)
        if errors:
            for error in errors:
                print(f"error: {error}")
            return 1
        print("lesson: ok")
        return 0
    if args.command == "new":
        card = render_card(args, next_id(text))
        if args.append:
            append_card(card)
            print(f"appended {card.split(':', 1)[0].replace('### ', '')}")
        else:
            print(card)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
