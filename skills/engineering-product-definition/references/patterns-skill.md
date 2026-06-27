# Patterns（Skill 级验证过的模式库，L2）

> **本文件是 skill 自身的「已验证模式」库**。来自 `lessons.md` 中被多次命中或用户确认的纠偏。每条 pattern 是一张可独立引用的卡片，**不再追加日志，而是合并成规律**。
>
> 与项目级 `docs/memory-bank/patterns.md` 的区别：本文件是**跨项目可复用**的 skill 知识；项目特定写法仍在该项目自己的 patterns.md。

## 三层 knowhow 模型回顾

```
L1 lessons.md         单条纠偏，立即生效
   ↓ ≥ 2 次或用户确认
L2 patterns-skill.md（本文件）   验证过的模式
   ↓ 影响某个 reference 的核心结论
L3 Reference 升级    owner 开 PR 修改对应 reference
```

---

## Pattern 卡片模板

每条 pattern 一张卡片，**必须**包含全部字段：

```md
### P-NNNN: <一句话标题>

- Created: <YYYY-MM-DD>
- Status: <active | pending-review | promoted-to-reference | superseded by P-MMMM | deprecated>
- Tags: <从 lessons.md 顶部 Tag 词表挑>
- Source lessons: L-<NNNN>, L-<NNNN>（合并的源 lesson）
- Confirmation count: <被多少次会话验证过>

## 适用条件

<什么情况下应当套用本 pattern？最关键的判断信号是什么？>

## 反例 / 不适用

<什么情况下绝对不要套用？反例是什么？>

## 模式描述

<一段或一段半的描述。如果有"先 A 再 B 不要 C"这样的步骤，写成有序列表。>

## 决策矩阵（可选）

<场景 vs 推荐做法的小表，复用 architecture-cases.md 风格>

| 场景 | 推荐做法 | 不推荐 | 退出成本 |
|---|---|---|---|

## 验证证据

- 项目 / 会话场景脱敏描述：<不写客户名>
- 反例命中：<是否被反例推翻过？>

## Promotion 状态

- [ ] 候选 promote 到 reference: <reference>.md §<x>
- [ ] 已 promote（写明 PR 链接和 reference 段落）
- [ ] 暂不 promote（理由：尚未在足够多项目验证 / 与现有 reference 冲突待 owner 决策）
```

### 字段说明

- **P-NNNN**：连续编号，从 P-0001 开始。
- **Status**：active 是可直接引用的模式；pending-review 表示与 reference 冲突，owner 决策前只能作为待审证据；promoted-to-reference 表示已进入 reference，reference 成为真相源。
- **Source lessons**：必须列出所有源 lesson；保证回溯链。
- **Confirmation count**：每次会话引用 pattern 解决新问题就 +1（agent 应当主动维护，但允许漂移，不是核心字段）。
- **Promotion 状态**：跟踪 L2 → L3 流程。

---

## 反模式（pattern 不该长这样）

- ❌ pattern 是 lesson 的复制粘贴，没有"合并多条 lesson 为规律"的动作。
- ❌ pattern 没有"反例 / 不适用"——只说什么时候用，不说什么时候不用 → 会被滥用。
- ❌ pattern 没有「适用条件」——结论性陈述但没说在什么信号下成立。
- ❌ pattern 与 reference 冲突但没标 promotion 状态 → 会形成双份真相源。
- ❌ pattern 累计被反例推翻 ≥ 1 次仍标 active → 应当 superseded 或 deprecated。

---

## 与 reference 的边界

- pattern 是 **"reference 的候选补强"**。一旦 promote 进 reference，pattern 标 `Status: promoted-to-reference` 并指向具体 reference 段落。
- pattern 不能与 reference 同时是 active 真相源。新的 reference PR 合并后，对应 pattern 必须更新状态。
- 如果 pattern 与 reference 冲突，**reference 优先**，pattern 标 `Status: pending-review`，等 owner 决策是否升级。

---

## Patterns 列表

> 新条目追加到本节末尾，编号连续。
>
> 当前条目数：0（v0.5.0 初始化，等待 promotion 注入）。

<!-- 示例（不删，是仿写样本）：

### P-0001: LLM 项目默认不配 RAG，先验证数据规模与更新频次（示例条目）

- Created: 2025-01-15
- Status: active
- Tags: stage-3, arch-llm, arch-rag, scenario-llm
- Source lessons: L-0001, L-0007
- Confirmation count: 3

## 适用条件

任何 Stage 3 给 LLM 项目做架构选型，且涉及"是否要 RAG"决策时。

## 反例 / 不适用

- 数据量 > 100 万条且语义检索是核心需求 → RAG 划算，本 pattern 不适用。
- 数据更新慢（< 1 次/周） + 检索频次高 → RAG 划算。

## 模式描述

LLM 项目 Stage 3 默认**不**配 RAG，先用以下决策树判断：

1. 数据量能否塞 context window（含 prompt + 历史）？能 → prompt-stuffing。
2. 数据有结构化入口（DB / API）？有 → 工具调用查询。
3. 数据规模 > 10 万 + 语义检索强需求 + 更新频率 < 1 次/天 → RAG 候选。
4. 上述三条都不满足 → 重新审视任务，多半不是 RAG 问题。

## 决策矩阵

| 数据规模 | 更新频次 | 检索类型 | 推荐 | 不推荐 | 退出成本 |
|---|---|---|---|---|---|
| < 10 万 | 任意 | 任意 | prompt-stuffing | RAG | 低 |
| 10–100 万 | 高频 | 关键词 | DB 工具调用 | RAG | 中 |
| 10–100 万 | 低频 | 语义 | RAG 候选 | prompt-stuffing | 中 |
| > 100 万 | 任意 | 语义 | RAG | 仅工具调用 | 高 |

## 验证证据

- 项目 A（脱敏：客服知识库）：100 条 FAQ，prompt-stuffing 已满足，砍掉 RAG 后维护成本下降 70%。
- 项目 B（脱敏：合规问答）：50 万条法规，RAG 必要，验证 pattern 不适用条件。
- 项目 C（脱敏：内部 Q&A）：5 千条文档但每天更新，RAG 维护成本超过收益，回退到 prompt-stuffing + 工具调用。

## Promotion 状态

- [x] 候选 promote 到 reference: `architecture-cases-ai.md` §E（RAG 架构）「适用场景」段落
- [ ] 已 promote
- [ ] 暂不 promote
-->

<!-- 真实 patterns 从这一行下方开始追加 -->
