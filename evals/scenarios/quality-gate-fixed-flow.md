---
schema_version: 1
id: quality-gate-fixed-flow
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.14.0
min_package_version: 0.14.0
prompt: "这个功能开发完了，CI 绿了，开发 Agent 说都测过了。帮我验收一下能不能上线。"
expected_route_ids:
  - review-release
required_fields:
  - 交付结论
  - 证据
  - 上线准备
  - 未运行检查及原因
  - 剩余风险
must:
  - 第一句给出三种结论之一：可以交付 / 还不能交付 / 缺证据没法判断。
  - 先看业务问题是否解决，再看功能、体验和工程底线；只展开相关项。
  - 没有证据不算通过，并说清楚缺什么、谁来补。
  - 需要机检时找到源仓库的 scripts/gate_check.py，或如实说明未机检。
must_not:
  - 不把 CI 绿或开发 Agent 的总结当作独立验收结论。
  - 不输出每格都写“待定 / BLOCKED”的整张检查表。
  - 不在正文里堆 G0、L2、BLOCKED 这类内部代号。
expected_references:
  - skills/engineering-review-release/references/delivery-gates.md
  - skills/engineering-review-release/references/verification-methods.md
stop_condition: "必需的检查没通过或缺证据时，结论只能是还不能交付或没法判断。"
---

# Quality Gate Fixed Flow

验证交付前的确认先看业务、先给结论，不以 CI 通过或开发 Agent 自述代替独立验收，也不输出死板的全量检查表。
