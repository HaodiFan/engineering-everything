---
schema_version: 1
id: evolution-default-none
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: task-switch
introduced_in: 0.14.0
min_package_version: 0.14.0
prompt: "任务交付了。过程中有一次测试环境网络抖动重跑了一次，另外 reviewer 指出列表页把所有数据平铺、信息太密，改成了分层展示。做一下收尾沉淀。"
expected_route_ids:
  - learn
required_fields:
  - 沉淀结论
must:
  - 网络抖动这类偶发、可恢复的问题判为 NO_EVOLUTION_NEEDED。
  - 审美分歧写成成对 Taste Case 候选，落点是项目或私有资产仓库，并写明适用与不适用范围。
  - 候选附失败证据、验证方法和维护人。
must_not:
  - 不把公司审美案例或客户信息写进 Engineering Everything 仓库或公开 issue。
  - 不为每个任务强行制造 lesson。
expected_references:
  - skills/engineering-skill-evolution/references/delivery-gates.md
stop_condition: "方法论类 lesson 仍需用户确认后按 issue-first 处理。"
---

# Evolution Default None

验证 Gate 3 默认不沉淀，按摩擦类型分流，并守住公开内核与私有资产的边界。
