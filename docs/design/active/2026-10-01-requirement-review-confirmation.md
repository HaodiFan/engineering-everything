# 对内-已确认：需求审查与用户确认流程设计

## Related issue

- https://github.com/HaodiFan/engineering-everything/issues/21
- 状态：优化方案与修改范围已确认；合并状态以关联 PR 为准。

## Optimization goal / 优化目标

AI 从已有材料查证需求，审查业务闭环与规则缺口，提出有依据的建议；用户明确确认结论、取舍和下一步后，再更新需求并推进。

## Direction / 优化方向

沿用产品定义 Skill、需求完备性检查与需求模板，补足审查到推进的交接。保持事实、假设、建议和用户决策可区分。审查报告由 Checklist 定义，Skill 只引用该格式。

## Implementation plan / 实现范围

1. `skills/engineering-product-definition/SKILL.md` 增加审需求入口，先查证已有材料，再分级审查、提出建议并等待确认；实际确认的决策直接沿用。
2. `references/checklists.md` 增加审查顺序、必须先解决与可后置的缺口分级，以及关键缺口的证据、影响、候选方案、代价与推荐理由。`PASS` 仅表示覆盖充分，确认状态单独记录。
3. `references/templates-specs.md` 补充材料来源、待确认假设、业务流程与规则对应的验收样例，以及实际用户确认记录。权限、审批和集成字段按场景适用。
4. 按 `data/reference_distribution.yaml` 同步十个 runtime reference copies。

## Verification plan / 验证

执行 `docs/testing.md` 所列仓库检查，并检查本次三个合成场景的规则覆盖：

| 场景 | 预期处理 | 手工走查依据 |
|---|---|---|
| 驳回后可重新提交，未明确审批路径 | 说明关键缺口及影响，比较候选路径，建议保持待确认 | Checklist 审查顺序 2–4；Requirements 的规则与验收、待决事项 |
| 需求已完整，用户要求先审查，尚未同意下一步 | 完备性可为 PASS，确认状态仍为待确认，保持审查阶段 | Checklist 对 PASS 的定义与确认状态；Skill 工作流 4 |
| 用户只回答一个问题，随后确认剩余取舍及下一步 | 部分答复只关闭对应问题；确认后更新需求，已有决策不反复索取 | Skill 工作流 4–5；Checklist 审查顺序 5、确认记录 |

以上为规则手工走查，未运行独立模型行为评估，不将结构检查作为模型遵循效果的证据。

验证结果：reference distribution、eval scenario schema、Skill doctor、自进化检查、lesson 校验、脚本语法检查与 diff 检查均通过；现有十项单元测试全部通过。结构、canonical source 和显式指定本设计的 PR preflight 均通过。

## Release plan / 发布计划

Issue → focused branch → PR → 检查通过后合并到 main。此次只合并已确认的需求审查改进，不创建版本 tag 或 GitHub Release。变更说明与验收依据记录在本设计及 PR 中；Harness 配置和维护文件保持现状。

## Risks and rollback / 风险与回退

- 确认要求仅在产品定义和需求审查路径生效，已有明确确认直接沿用；新增关键假设或范围变化才重新确认。
- 自然语言规则的真实模型遵循效果仍需独立行为评估。
- 合并前可撤回本 PR；合并后可通过 revert 合并提交恢复本次修改。

## Evidence boundary / 证据边界

仅包含公开仓库相对路径、合成案例、改进范围、Issue 链接与验证依据。
