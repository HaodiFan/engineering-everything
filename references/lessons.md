# Lessons（Skill 级纠偏日志，L1）

> **本文件是 skill 自身的「纠偏沉淀」追加日志**。每次用户纠正 agent 的方案，agent 主动把这条纠偏写进本文件。**只追加，不删除**。被推翻或废弃的 lesson 标 `Status: deprecated` 并写明替代项。
>
> 与项目级 `docs/memory-bank/patterns.md` 的区别：本文件记录的是**跨项目可复用的 skill 级 knowhow**；项目特定写法仍写在该项目自己的 patterns.md。

## 三层 knowhow 模型回顾

```
L1 Lessons（本文件）         单条纠偏，立即生效，agent 自己加
   ↓ ≥ 2 次命中或用户确认
L2 Patterns（patterns-skill.md）   验证过的模式，合并卡片
   ↓ 影响某个 reference 的核心结论
L3 Reference 升级           owner 开 PR 改对应 reference
```

---

## 触发信号（agent 必须主动捕获 lesson）

用户回复包含以下信号时，**agent 必须**在该轮回复末尾追加一段「📌 是否捕获 lesson」的提议，并在用户确认后写入本文件：

- 否定/纠偏：「不对」「不是」「应该是」「这个方案有问题」「这里不行」「错了」
- 经验补充：「这种情况下要…」「你忘了…」「实际上…」「我们这边…」「我之前是…」
- 反例提供：「我之前踩过这个坑」「上次就是这样挂了」「这条路走不通」
- 选型推翻：「不要用 X，要用 Y，因为…」「换成 Y」
- 流程纠偏：「这一步不该现在做」「先做 X 再做 Y」

> 信号弱 / 用户只是聊天 / 单纯澄清不要硬捕获——硬捕获会污染 lessons.md。

---

## Lesson 卡片模板

每条 lesson 一段 markdown，**必须**包含全部字段：

```md
### L-NNNN: <一句话标题>

- Date: <YYYY-MM-DD>
- Status: <active | pending-review | superseded by L-MMMM | deprecated>
- Captured-from: <对话场景一句话，如「Stage 3 给电商商家后台采集方案时」>
- Tags: <stage-3 | scenario-rpa | arch-llm | ...>（多标签用逗号；从下面 Tag 词表挑）

**❌ 之前的错误方案 / 默认建议**：

<一两句话写清当时 agent 的方案或推断>

**✅ 正确方案 / 用户给的纠偏**：

<一两句话写清正确做法或反例>

**🧠 原因 / 适用条件**：

<什么场景下这条成立？什么场景下不成立？最关键的限制条件是什么？>

**🔁 是否可泛化**：

- [ ] 跨项目可复用（→ 候选 promote 到 patterns-skill.md）
- [ ] 仅特定项目（→ 应该写到该项目自己的 patterns.md，不是这里）
- [ ] 仅特定场景：<场景名>

**🔗 相关**：

- 影响 reference: `<file>.md` §<x>（如有）
- 关联 lesson: L-<NNNN>（如是同主题）
```

### 字段说明

- **L-NNNN 编号**：连续编号，从 L-0001 开始。被 superseded 不释放编号。
- **Status**：active 是默认；与 reference 冲突待 owner 决策 → pending-review；被新 lesson 推翻 → superseded by L-MMMM；明确不再适用 → deprecated。
- **Captured-from**：让未来的 agent 知道"这条是在什么对话里被纠偏的"，不写客户名/秘密。
- **Tags 词表**（保持有限，超出时先在本文件顶部加新 tag）：
  - 阶段：`stage-0`–`stage-9`、`stage-p`、`stage-i`
  - 形态：`form-web-backend` `form-desktop-local` `form-python-cli` `form-library` `form-monorepo`
  - 场景：`scenario-rpa` `scenario-ocr` `scenario-vision` `scenario-data-gov` `scenario-llm` `scenario-browser-auto` `scenario-poc`
  - 架构维度：`arch-repo` `arch-render` `arch-backend` `arch-data` `arch-protocol` `arch-auth` `arch-deploy` `arch-async` `arch-observability` `arch-llm` `arch-rag` `arch-eval` `arch-prompt` `arch-vector`
  - 工程实践：`practice-spec` `practice-doc` `practice-branch` `practice-ci` `practice-test` `practice-pr` `practice-refactor` `practice-incident`
  - 治理：`gov-constitution` `gov-adr` `gov-memory-bank` `gov-prompts` `gov-design-lifecycle`
- **是否可泛化**：这是 promotion 入口。打勾「跨项目可复用」+ 同主题 ≥ 2 条 → 提议写 pattern。
- **相关**：留下回溯链。

---

## 反模式（agent 不要写进 lessons.md）

- ❌ 个人偏好：「我喜欢用 X」「X 看起来更优雅」——不是被验证的纠偏。
- ❌ 与现有 reference 重复：reference 已经写过的结论，不复述成 lesson。
- ❌ 项目特定细节：「我们公司用 Y 做 Z」——这是项目级 patterns.md 的内容。
- ❌ 秘密 / 客户名 / 内部链接 / token / 真实数据。
- ❌ 一条 lesson 包含多个意图——拆成多条。
- ❌ 没有「原因 / 适用条件」的 lesson：只写"用 Y 不要用 X"没说为什么 → 无法被未来 agent 复用。
- ❌ 散文化的 lesson：超过 15 行通常说明该写成 design doc / ADR 或 reference 升级。
- ❌ 把临时纠偏当 lesson：用户只是这一次想这么做，不是普遍真理。

---

## Promotion 流程

### L1 → L2（lesson → pattern）

触发条件（任一）：
- 同 Tag + 同主题的 lesson ≥ 2 条
- 用户明确说「这是通用模式」「以后都这样」「记一下规律」
- agent 在新会话发现 lesson 已被引用解决相同问题 ≥ 2 次

动作：
1. 在 `patterns-skill.md` 写一份 pattern 卡片（合并多条 lesson 为一条规律）。
2. 在原 lessons 卡片的 `🔗 相关` 加 `Promoted to: P-NNNN`。
3. 不删 lesson（保留考古）。

### L2 → L3（pattern → reference 升级）

触发条件（任一）：
- pattern 与某个 reference 的核心结论冲突。
- pattern 在多个项目都验证过，且方法学层面可补强 reference。
- pattern 累计 ≥ 3 次被引用且无反例。

动作：
1. owner 开 PR 修改对应 reference（如 `architecture-cases.md` / `stage-playbook.md` / `scenario-playbooks.md`）。
2. PR 描述里链接 pattern P-NNNN 与全部源 lesson L-NNNN。
3. pattern 卡片加 `Promoted to: <reference>.md §<x>` 并标 `Status: promoted-to-reference`。
4. 不删 pattern（保留回溯）。

> Promotion 是**严格单向**的：reference 修改后再次发现错 → 走新 lesson 而不是改 pattern；这样保证 reference 永远是当前真相源。

---

## 如何使用本文件（agent 自查）

**会话开始时**：
- 如果当前任务命中某个 Tag（阶段 / 场景 / 架构维度），用 `grep` 或全文搜把对应 Tag 的 active lesson 拉出来，作为方案约束。
- 如果发现某条 active lesson 的「✅ 正确方案」与本次方案冲突 → 优先采纳 lesson，并在回复里引用 L-NNNN。

**会话结束时**：
- 检查本次对话是否触发任一捕获信号；触发就提议捕获。
- 用户确认后追加到下方「Lessons 列表」末尾，编号连续。
- 同时检查是否触发 Promotion，触发就走 L1 → L2 流程。

**冲突处理**：
- 多条 lesson 互相冲突 → 写新 lesson 并把旧的标 superseded by L-新编号，给出"什么情况下用旧、什么情况下用新"。
- lesson 与 reference 的明确陈述冲突 → 默认 reference 优先，把 lesson 标为 `Status: pending-review`，由 owner 决定 reference 是否要改（L3）。

---

## Lessons 列表

> 新条目追加到本节末尾，**保持时间顺序**。第一条用 L-0001 开始。
>
> 当前条目数：1。

<!-- 示例（不删，是 agent 仿写的样本）：

### L-0001: Stage 3 不要默认推 RAG 给所有 LLM 项目（示例条目）

- Date: 2025-01-01
- Status: active
- Captured-from: Stage 3 架构方案对话中默认推 RAG，被用户指出该项目数据量小且更新频繁，RAG 不划算
- Tags: stage-3, arch-llm, arch-rag, scenario-llm

**❌ 之前的错误方案 / 默认建议**：

LLM 项目默认配 RAG（向量库 + embedding pipeline + 检索路由）。

**✅ 正确方案 / 用户给的纠偏**：

数据量 < 10 万条 + 更新频繁 + 内容能塞 context window 时，优先 prompt-stuffing 或工具调用查 DB；RAG 只在数据量大、更新慢、需要语义检索时才有 ROI。

**🧠 原因 / 适用条件**：

RAG 的运维成本（embedding 重建、向量库一致性、检索召回 tuning）只有在数据规模和更新频次过了某个阈值才划算。小数据 + 高频更新场景下 RAG 反而是负担。

**🔁 是否可泛化**：

- [x] 跨项目可复用（→ 候选 promote 到 patterns-skill.md）
- [ ] 仅特定项目
- [ ] 仅特定场景

**🔗 相关**：

- 影响 reference: `architecture-cases-ai.md` §E（RAG 架构）的「适用场景」段落可补强
- 关联 lesson: 暂无
-->

<!-- 真实 lessons 从这一行下方开始追加 -->

### L-0001: 长 active-context 先读关键词 map 再读正文

- Date: 2026-05-13
- Status: active
- Captured-from: 复盘一次 fast_build/Excel bug 排查链路时，用户指出 Skill 造成整读长上下文和历史流水账干扰，需要优化链路
- Tags: gov-memory-bank, practice-doc, practice-incident

**❌ 之前的错误方案 / 默认建议**：

开工强制读取完整 `docs/memory-bank/active-context.md`，即使它已经变成数百行记录性文档。

**✅ 正确方案 / 用户给的纠偏**：

当记录性且频繁读取的上下文文档过长时，先维护同目录关键词 mapping 文件；agent 先选关键词，再用搜索词定位正文细节。

**🧠 原因 / 适用条件**：

适用于 active context、incident log、handover log 这类持续追加、需要频繁读取但每次只命中部分主题的文档。不适用于短 spec、ADR 或需要完整顺序阅读的协议文档。

**🔁 是否可泛化**：

- [x] 跨项目可复用（→ 候选 promote 到 patterns-skill.md）
- [ ] 仅特定项目
- [ ] 仅特定场景

**🔗 相关**：

- 影响 reference: `memory-bank-guide.md` 的 active-context 使用规则
