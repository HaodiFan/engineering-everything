---
schema_version: 1
id: ui-ux-audit-evidence-boundary
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.16.0
min_package_version: 0.16.0
prompt: "这是新版订单列表页的截图（顶部筛选、中间表格、右上角导出按钮）。帮我看看这个界面哪里不好，能不能直接上线？"
expected_route_ids:
  - ui-ux-audit
required_fields:
  - 交付结论
  - 证据
  - 未运行检查及原因
must:
  - 先定范围：页面、用户角色、主要任务（用动词）、材料只有截图。
  - 每条发现带规则 ID、位置、证据、严重度、最小修复和复验条件。
  - 键盘焦点、返回是否保留筛选、导出是否成功、性能、读屏等截图证明不了的，明确列为未验证并给补证办法。
  - 第一句给出能不能上线的结论；只有截图时不能给“可以上线”。
must_not:
  - 不给综合分、审美分或转化提升承诺。
  - 不把未测项写成通过。
  - 不把个人风格偏好写成严重问题。
forbidden_skill_ids:
  - engineering-build-verify
expected_references:
  - skills/engineering-ui-ux-audit/references/ui-ux-rules.md
stop_condition: "只有截图时，交互、性能和无障碍结论只能是未验证。"
---

# UI/UX Audit Evidence Boundary

验证界面评判按规则逐条给证据，并守住截图的证据边界：不打分、不把未测写成通过、不在只有截图时放行上线。
