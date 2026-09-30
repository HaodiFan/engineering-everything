---
name: engineering-product-definition
description: Use when clarifying or reviewing a product idea, PRD, requirements, PSPS, user scenario, scope, non-goals, or success criteria, finding gaps and recommending decisions for user confirmation before architecture or implementation.
metadata:
  version: 0.13.0
---

# Engineering Product Definition / 产品定义

把模糊想法变成可构建、可验证、可拒绝扩张的需求边界。业务意图必须来自用户或 owner；agent 负责查证、结构化、审查和建议，业务取舍由用户确认。

## 何时使用

- 用户说“我有个想法”“帮我写 PRD”“需求怎么定义”“审需求”“需求评审”“检查 PRD”“PSPS”“用户场景不清楚”。
- 当前还没有可执行 spec、成功指标、非目标或验收标准。
- 架构、实现、排期依赖业务边界先清楚。

## 工作流

1. 先读取用户材料和相关已有文档，查清可查证的事实，提取一句话定义与 PSPS；已有内容直接引用，缺失项标明，避免交给用户一份空白清单。
2. 按 `references/checklists.md` 的需求审查流程检查业务闭环、范围、规则与异常、约束和验收。区分事实、假设、建议与待决事项，不把推测写成已确认需求。
3. 分级说明缺口及影响。涉及业务取舍时给出可选方案、代价和推荐理由；提出 P0/P1/P2 范围建议，P0 必须保住最小业务闭环。
4. 输出需求理解、关键缺口、建议和需用户确认的事项，等待用户明确确认审查结论及取舍。完备性检查通过本身不构成推进授权；用户只回答部分问题时，继续标明未决项。
5. 用户确认后，将已确认内容更新到需求文档，再进入约定的下一步。已确认决策直接沿用，只有新增关键假设或范围变化才重新确认。

## 输出模板

需求审查结果使用 `references/checklists.md` 的 Agent 输出格式；规划 / 路由输出继续使用以下字段。

```text
工程路由: Product | 产品定义 | Product
当前阶段: 0 想法 / 1 需求澄清 / 2 Spec
项目形态: <候选形态，不超过 3 个>
参考依据:
- 路由规则:
- 已读 reference:
- 外部/历史依据:
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

## 停止条件

- 缺少业务 owner、目标用户、核心流程或成功指标，且错误假设代价高。
- 用户要求 agent 编造业务需求，而不是结构化已知事实。
- P0 范围无法形成可验收闭环。
- 审查结论或业务取舍尚未得到用户明确确认；此时可继续查证和完善建议，保持在需求审查阶段。

## References

- `references/psps-framework.md`：PSPS 构建洞察框架。
- `references/spec-templates.md`：需求、Design Doc 和模板路由。
- `references/templates-specs.md`：Requirements / Design Doc 具体模板。
- `references/checklists.md`：需求完备性与验证 checklist。
- `references/stage-playbook.md`：Stage 0-2 阶段判断。
