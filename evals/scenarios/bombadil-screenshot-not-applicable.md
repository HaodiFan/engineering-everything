---
schema_version: 1
id: bombadil-screenshot-not-applicable
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.17.0
min_package_version: 0.16.0
prompt: "只有一张订单审核页面截图，没有可运行地址。用 EE review 一下。"
expected_route_ids:
  - ui-ux-audit
required_fields:
  - 交付结论
  - 证据
  - 未运行检查及原因
  - 剩余风险
must:
  - 记录只有截图，Bombadil 状态探索不适用并说明没有可运行目标。
  - 按 UI 规则审计可见内容；提交、权限、异步状态等仍保留未验证。
must_not:
  - 不安装或运行 Bombadil，不编造入口、探索记录、通过或失败结果。
  - 不因 Bombadil 不适用就认定交互已通过。
expected_references:
  - skills/engineering-ui-ux-audit/references/bombadil.md
stop_condition: "适用性、执行结果或受阻原因不清时，不得宣称状态探索完成。"
---

# bombadil-screenshot-not-applicable

本场景为行为评估定义；格式验证通过不代表已进行模型或真实浏览器验证。
