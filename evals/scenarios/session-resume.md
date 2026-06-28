---
schema_version: 1
id: session-resume
harness: manual-behavior-eval
entrypoint: using-engineering-everything
session_event: resume
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "继续刚才的重构任务，先说我们做到哪一步。"
expected_route_ids:
  - refactor
required_fields:
  - 工程路由
  - 当前阶段
  - 参考依据
  - 验证门禁
must:
  - 先恢复 route summary。
  - 说明最近 route、阶段、打开文件和验证状态。
must_not:
  - 不重新当作全新需求设计。
expected_references:
  - skills/using-engineering-everything/references/route-contract.md
---

# Session Resume

验证 resume 时 bootloader 会恢复上下文，而不是丢失路由状态。
