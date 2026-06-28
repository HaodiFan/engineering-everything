---
schema_version: 1
id: no-spec-no-architecture
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "我只有一个想法：做企业知识库，你直接选技术栈并设计数据库。"
expected_route_ids:
  - product
  - architecture
required_fields:
  - 工程路由
  - 当前阶段
  - 缺失内容
  - 停止条件
must:
  - 说明 spec 缺失会阻塞架构和数据库设计。
  - 给出下一步 3 个需求澄清动作。
must_not:
  - 不新增状态机、存储、权限或公共 API。
forbidden_skill_ids:
  - engineering-build-verify
stop_condition: "没有 spec，不进入架构层、存储和权限设计。"
---

# No Spec No Architecture

验证主路由仍保持无 spec 不进架构的硬门禁。
