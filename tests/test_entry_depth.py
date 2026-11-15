from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_doctor():
    spec = importlib.util.spec_from_file_location("skill_doctor", ROOT / "scripts/skill_doctor.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["skill_doctor"] = module
    spec.loader.exec_module(module)
    return module


OLD_BOOTLOADER = """# Using
<!-- evozeus-harness-entry:v1 -->
**MUST 使用 Read 工具读取 [x](.evozeus-wrapper/skills/using-evozeus-harness/SKILL.md)**
<!-- /evozeus-harness-entry -->
## 加载顺序
1. 读取本文件。
2. 先读取 `references/route-contract.md`，理解 route 字段。
## References
- `references/route-contract.md`：route 字段契约。
"""


class EntryDepthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doctor = load_doctor()

    def test_old_eager_bootloader_is_rejected(self) -> None:
        problems = self.doctor.entry_depth_problems("using-engineering-everything", OLD_BOOTLOADER)
        self.assertTrue(any("up front" in p for p in problems), problems)
        self.assertTrue(any("without loading references" in p for p in problems), problems)
        self.assertTrue(any("when to read" in p for p in problems), problems)

    def test_harness_block_is_ignored(self) -> None:
        text = OLD_BOOTLOADER.split("## 加载顺序")[0] + "\n进入 `engineering-everything`。\n"
        self.assertEqual([], self.doctor.entry_depth_problems("using-engineering-everything", text))

    def test_sub_skill_reference_needs_condition(self) -> None:
        text = "## References（用到时再读）\n\n- `references/a.md`：做评审时。\n- `references/b.md`：评审口径。\n"
        problems = self.doctor.entry_depth_problems("engineering-review-release", text)
        self.assertEqual(1, len(problems))
        self.assertIn("b.md", problems[0])

    def test_repository_entry_is_flat(self) -> None:
        for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill.parent.name):
                self.assertEqual([], self.doctor.entry_depth_problems(skill.parent.name, skill.read_text(encoding="utf-8")))

    def test_bootloader_reaches_router_in_one_hop(self) -> None:
        text = (ROOT / "skills/using-engineering-everything/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`engineering-everything`", text)
        self.assertFalse((ROOT / "skills/using-engineering-everything/references").exists())

    def test_router_table_matches_routes(self) -> None:
        import re
        listed = set(re.findall(r"\| `(engineering-[a-z-]+)` \|", (ROOT / "skills/engineering-everything/SKILL.md").read_text(encoding="utf-8")))
        self.assertEqual(self.doctor.route_skill_names(ROOT) - {"engineering-everything"}, listed)

    def test_every_sub_skill_says_where_unshipped_references_live(self) -> None:
        findings = []
        self.doctor.check_reference_resolution(ROOT, findings)
        self.assertEqual([], [f.message for f in findings])

    def test_unresolvable_reference_is_reported(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "engineering-x"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text("读取 `references/gone.md`。\n", encoding="utf-8")
            (skill / "references/a.md").write_text("见 `references/b.md`\n", encoding="utf-8")
            missing = self.doctor.unresolved_reference_names(skill, {"b.md"})
            self.assertEqual(["SKILL.md -> gone.md"], missing)


if __name__ == "__main__":
    unittest.main()
