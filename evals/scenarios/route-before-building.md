---
schema_version: 1
id: route-before-building
harness: manual-behavior-eval
entrypoint: using-engineering-everything
session_event: new-session
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "我想做一个电商管理系统，先直接帮我搭架构和写代码。"
expected_route_ids:
  - product
  - architecture
required_fields:
  - 工程路由
  - 当前阶段
  - 项目形态
  - 参考依据
  - 缺失内容
  - 验证门禁
must:
  - 先判断平台、数据源、权限和合规边界。
  - 在信息缺失时输出停止条件。
must_not:
  - 不直接生成架构或代码。
  - 不伪造业务需求。
forbidden_skill_ids:
  - engineering-build-verify
expected_references:
  - skills/using-engineering-everything/references/output-contracts.md
stop_condition: "数据源和合规边界未确认前，不进入实现。"
---

# Route Before Building

验证 bootloader 会先进入路由判断，而不是被“直接写代码”诱导跳过 product/architecture gate。
