from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_eval_module():
    spec = importlib.util.spec_from_file_location("eval_scenarios", ROOT / "scripts/eval_scenarios.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_eval_fixture(root: Path, scenario_id: str = "sample") -> Path:
    (root / "data").mkdir()
    (root / "references").mkdir()
    (root / "evals/scenarios").mkdir(parents=True)
    (root / "skills/engineering-product-definition").mkdir(parents=True)
    (root / "skills/engineering-product-definition/SKILL.md").write_text("---\nname: engineering-product-definition\n---\n")
    (root / "data/routes.yaml").write_text("routes:\n  - id: product\n    skill: engineering-product-definition\n")
    (root / "references/output-contracts.md").write_text(
        """<!-- output-fields:start -->
- 工程路由
- 当前阶段
- 验证门禁
<!-- output-fields:end -->
""",
        encoding="utf-8",
    )
    scenario = root / "evals/scenarios/sample.md"
    scenario.write_text(
        f"""---
schema_version: 1
id: {scenario_id}
harness: manual
entrypoint: using-engineering-everything
session_event: new-session
introduced_in: 0.12.0
min_package_version: 0.11.0
prompt: "sample"
expected_route_ids:
  - product
required_fields:
  - 工程路由
must:
  - route first
must_not:
  - build first
---

# Sample
""",
        encoding="utf-8",
    )
    return scenario


class EvalScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.eval_scenarios = load_eval_module()

    def test_valid_scenario_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_eval_fixture(root)

            self.assertEqual([], self.eval_scenarios.validate_scenarios(root))

    def test_id_must_match_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_eval_fixture(root, scenario_id="other")

            errors = self.eval_scenarios.validate_scenarios(root)

            self.assertTrue(any("id must match filename stem" in error for error in errors))

    def test_unknown_output_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            scenario = write_eval_fixture(root)
            scenario.write_text(
                scenario.read_text(encoding="utf-8").replace("  - 工程路由", "  - 不存在字段"),
                encoding="utf-8",
            )

            errors = self.eval_scenarios.validate_scenarios(root)

            self.assertTrue(any("unknown output field" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
