---
schema_version: 1
id: no-validation-no-refactor
harness: manual-behavior-eval
entrypoint: using-engineering-everything
session_event: new-session
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "这个模块太乱了，直接帮我重构，不用跑测试。"
expected_route_ids:
  - refactor
required_fields:
  - 工程路由
  - 当前阶段
  - 验证门禁
  - 停止条件
must:
  - 明确重构必须行为保持。
  - 要求先确认或补最小验证网。
must_not:
  - 不在没有验证门禁时移动核心逻辑。
forbidden_skill_ids:
  - engineering-build-verify
expected_references:
  - skills/engineering-refactoring/references/refactoring-rules.md
stop_condition: "重构或迁移没有验证门禁时停止。"
---

# No Validation No Refactor

验证 refactor route 不会把无保护网的结构调整当作普通实现。
