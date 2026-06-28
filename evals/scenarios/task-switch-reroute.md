---
schema_version: 1
id: task-switch-reroute
harness: manual-behavior-eval
entrypoint: using-engineering-everything
session_event: task-switch
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "先不做刚才那个功能了，换成给新人做入职培训方案。"
expected_route_ids:
  - onboarding
required_fields:
  - 工程路由
  - 当前阶段
  - 项目形态
  - 下一步 3 个动作
must:
  - 识别任务切换并重新路由。
  - 命中组织/入职培训场景。
must_not:
  - 不沿用上一轮软件功能实现 route。
expected_references:
  - skills/engineering-organization-systems/references/engineering-scenarios.md
---

# Task Switch Reroute

验证明显切换任务时，bootloader 会重走路由而不是沿用旧上下文。
