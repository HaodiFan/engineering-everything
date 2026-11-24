---
schema_version: 1
id: ui-self-explanation-unfamiliar-language
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.17.0
min_package_version: 0.16.0
prompt: "评审这个界面：把所有可见文字换成我不认识的语言后，检查光凭 UI 能否定位主导航、展开详情并返回；不要改生产界面。"
expected_route_ids:
  - ui-ux-audit
required_fields:
  - 交付结论
  - 证据
  - 未运行检查及原因
  - 剩余风险
must:
  - 读取 UX-VIS-09 及陌生语言检查步骤，给任务目标而不提示路径。
  - 仅在隔离预览或副本制作陌生文字版本，覆盖状态和弹层文字并保留布局和控件形态。
  - 先展示陌生版本，不借翻译、DOM 原文、无障碍名称或原页面记忆判为通过；记录观察者熟悉度。
  - 基础导航、主操作或反馈无法辨认时，明确记录 UI 自解释不足及最小修复。
  - 只有截图时仅判断视觉线索；未生成陌生版本时本项未验证；未实际操作不得宣称流程可用。
  - 专业内容理解与基础控件辨识分开检查，保留必要标签和无障碍语义。
must_not:
  - 不把隐藏全部文字、制造排版破坏或只换标题当成陌生语言测试。
  - 不只凭想象打勾，不把所有业务阅读失败都归为视觉失败。
  - 不建议删除所有标签、只留图标或用更长说明掩盖结构问题。
expected_references:
  - skills/engineering-ui-ux-audit/references/ui-ux-rules.md
  - skills/engineering-ui-ux-audit/references/ui-ux-verification.md
stop_condition: "没有陌生版本或实际操作证据时，按材料限制保留未验证，不能声称用户已能独立使用。"
---

# UI self-explanation under unfamiliar language

行为场景定义；格式校验不代表已经进行真实用户或模型实验。
