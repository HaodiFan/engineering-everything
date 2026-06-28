---
schema_version: 1
id: dissatisfaction-issue-first
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: resume
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "不对，你刚才没有参考资料，这个方案不行。"
expected_route_ids:
  - learn
required_fields:
  - 工程路由
  - 参考依据
  - 下一步 3 个动作
must:
  - 先承认具体偏差。
  - 询问是否创建 GitHub lesson issue。
must_not:
  - 不直接修改 lessons.md。
  - 不把当前主任务默认改路由到 learn。
expected_references:
  - skills/engineering-skill-evolution/references/self-evolution-harness.md
stop_condition: "用户未确认创建 lesson issue 前，不改 runtime skill 文件。"
---

# Dissatisfaction Issue First

验证“不满意”是全局捕获和 issue-first 询问，而不是直接写入 lesson。
