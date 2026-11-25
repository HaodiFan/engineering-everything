---
name: engineering-product-definition
description: Use when clarifying or reviewing a product idea, PRD, requirements, PSPS, user scenario, scope, non-goals, or success criteria, finding gaps and recommending decisions for user confirmation before architecture or implementation.
metadata:
  version: 0.19.0
---

# Engineering Product Definition / 产品定义

把模糊想法变成可构建、可验证、可拒绝扩张的需求边界。业务意图必须来自用户或 owner；agent 负责查证、结构化、审查和建议，业务取舍由用户确认。

## 何时使用

- 用户说“我有个想法”“帮我写 PRD”“需求怎么定义”“审需求”“需求评审”“检查 PRD”“PSPS”“用户场景不清楚”。
- 当前还没有可执行 spec、成功指标、非目标或验收标准。
- 架构、实现、排期依赖业务边界先清楚。

## 工作流

1. 先读取用户材料和相关已有文档，查清可查证的事实，提取一句话定义与 PSPS；已有内容直接引用，缺失项标明，避免交给用户一份空白清单。
2. 涉及面向用户的工作流、导航/信息架构、工作台、跨角色协作或异步/AI 任务时，先按 `references/user-journey.md` 推导**与界面实现解耦的核心用户旅程**（`actor / trigger / goal / stages / success / experience_constraints`，不写死页面/Tab/按钮），写入需求卡 `journeys[]`，再确定功能组合与界面方案。
3. 按 `references/checklists.md` 的需求审查流程检查业务闭环、范围、规则与异常、约束和验收。区分事实、假设、建议与待决事项，不把推测写成已确认需求。
4. 分级说明缺口及影响。涉及业务取舍时给出可选方案、代价和推荐理由；提出 P0/P1/P2 范围建议，P0 必须保住最小业务闭环。
5. 输出需求理解、关键缺口、建议和需用户确认的事项，等待用户明确确认审查结论及取舍。完备性检查通过本身不构成推进授权；用户只回答部分问题时，继续标明未决项。
6. 用户确认后，将已确认内容更新到需求文档，再进入约定的下一步。已确认决策直接沿用，只有新增关键假设或范围变化才重新确认。

### 团队交付：开工前想清楚

需求来自创始人或业务方、由负责人来做时，按 `references/delivery-gates.md` 第 3 节写一页需求卡：帮谁解决什么问题、做成了是什么样子（能演示）、不做什么、哪些是推测、改动有多大。目标是让提需求的人看一眼就能说“对”或“不对”，而不是把问题清单丢回去。能自己定、可撤回的事自己定并记一句理由；只有真要取舍时才带着选项和推荐去问。

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

## References（用到时再读）

本目录没有的参考文件（文中按名字提到的），在源仓库的 `references/` 下：取本 Skill 目录的真实路径（它是软链）往上两级就是源仓库。找不到就直说没读到，不要假装读过。

- `references/delivery-gates.md`：团队任务，要写需求卡、定档位、判断要不要找人拍板时。
- `references/user-journey.md`：涉及用户工作流、工作台、导航、跨角色或异步任务，要在定功能前先推导 Journey Contract 时就读。
- `references/psps-framework.md`：需求模糊，要用 PSPS 挖洞察时。
- `references/spec-templates.md`：要选需求 / Design Doc 模板时。
- `references/templates-specs.md`：要按模板写正式文档时。
- `references/stage-playbook.md`：拿不准处于 0-2 哪个阶段时。
- `references/checklists.md`：需求定稿前自查完备性时。
- `references/output-contracts.md`：要写正式的“开工前”输出时。
