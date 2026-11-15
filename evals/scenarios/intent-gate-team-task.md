---
schema_version: 1
id: intent-gate-team-task
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.14.0
min_package_version: 0.14.0
prompt: "创始人只说了一句：企业建模模块要有生命感，能看到人和系统、流程的关系，不要做成传统管理后台。我是这个任务的负责人，帮我开工。"
expected_route_ids:
  - product
required_fields:
  - 原始意图
  - 需求卡
  - 档位
  - 需要拍板的事
must:
  - 原样保留创始人的原话，不用转述覆盖。
  - 先查已有代码、数据模型或案例，再把事实、假设、未知分开写。
  - 验收项写成可观察结果，并为每项给出建议的验证方法。
  - 低风险、可逆的设计选择由负责人自主决定并记录。
  - 需求卡控制在一页内能看完，先给结论。
must_not:
  - 不把一份空白问题清单原样丢回给创始人。
  - 不把推断写成创始人已确认的需求。
  - 不在需求卡完成前直接写代码。
  - 不在正文里堆 L0-L3、DRI、Gate 这类内部代号。
expected_references:
  - skills/engineering-product-definition/references/delivery-gates.md
stop_condition: "命中升级条件时只提交升级单（2-3 个选项 + 推荐），其余部分继续推进。"
---

# Intent Gate Team Task

验证团队交付任务进入 Gate 1：由负责人展开粗粒度意图，产出需求卡，而不是把拆需求的工作退回给创始人。
