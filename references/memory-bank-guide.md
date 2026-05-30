# Memory Bank 指南

为 AI agent 跨会话保留项目上下文。**不是**复制现有文档，而是"指针 + 增量"。

## 设计原则

- **指针优先**：能引用 `README` / `ARCHITECTURE` / `Requirements` 就引用，不复制内容。
- **增量驱动**：只记录在其他文档之外、但 agent 每次都需要的"项目特定模式"和"当前焦点"。
- **新鲜度优先**：active-context.md 必须每次会话结束更新；其他三份按需。
- **小而高密度**：四份文件加起来建议 < 500 行。臃肿 = 失效。
- **AI 友好**：用 markdown 列表、表格、代码块；不写散文。

## 目录约定

```
docs/memory-bank/
├── brief.md            # 项目是什么（指针 + 当下最重要 3 条）
├── tech-context.md     # 技术栈速记（指针 + 当下技术决策快查）
├── patterns.md         # 项目特定模式（新内容，不重复 ARCHITECTURE）
├── active-context.md   # 当前工作焦点（每会话更新）
└── active-context-map.md # 可选；active-context 过长时的关键词索引
```

> 路径 `docs/memory-bank/`（与 `docs/design/`、`docs/governance/` 平级）。
> 在 `AGENTS.md` 中明确"开工前先读 memory-bank/active-context.md"。

## 与现有文档的边界

| 文档 | 谁是真相源 | Memory Bank 怎么处理 |
|---|---|---|
| 项目定位 / 用户 / 核心能力 | `README.md` | brief.md 只放指针 + "当下最重要的 3 件事" |
| 架构决策表 | `ARCHITECTURE.md` 的 Technical Baseline | tech-context.md 只放指针 + "本周需要 agent 关注的技术点" |
| 业务需求 | `docs/requirements/*.md` | brief.md 指针 + 当前活跃需求版本号 |
| 分支/提交规则 | `BRANCHING.md` | tech-context.md 一行指针 |
| 设计系统 | `DESIGN.md` | tech-context.md 一行指针（UI 类） |
| 项目特定写法/惯例 | **无现有真相源** | patterns.md 是真相源 |
| 当前 sprint / 焦点 / 阻塞 | **无现有真相源** | active-context.md 是真相源 |

> 如果 memory-bank 的内容和上述真相源**冲突**，以真相源为准，立刻更新 memory-bank。

## 四份模板

### brief.md

```md
# Project Brief

- Last updated: <date>
- Primary docs: [README](../../README.md) · [Requirements](../requirements/) · [ARCHITECTURE](../../ARCHITECTURE.md)

## 一句话定位
<从 README 复制一句，不超过 30 字>

## 当下最重要的 3 件事
1.
2.
3.

## 项目状态
<pre-dev | prototype | active | uat | production>

## 关键干系人
- Product owner:
- Tech lead:
- Active maintainers:
```

### tech-context.md

```md
# Tech Context

- Last updated: <date>
- Source of truth: [ARCHITECTURE](../../ARCHITECTURE.md) · [BRANCHING](../../BRANCHING.md) · [DESIGN](../../DESIGN.md)

## 技术栈速记

| 维度 | 选定方案 | 备注 |
|---|---|---|
| 语言/运行时 | | |
| 前端框架 | | |
| 后端框架 | | |
| 数据库 | | |
| 部署目标 | | |
| LLM provider（如适用） | | |

> 详细决策与理由见 `ARCHITECTURE.md` Technical Baseline。

## 本周/本 sprint agent 需要关注的技术点

- <例：本周在做 X 迁移，避免在 Y 模块改动>
- <例：新加 feature flag 系统，未来一周内 X 处使用>

## 已知坑（agent 必须先看）

- <例：`packages/auth` 的 token 刷新有种竞态，新代码绕开它>
```

### patterns.md

```md
# Project Patterns

- Last updated: <date>

> 项目特定的写法和惯例。**不重复** ARCHITECTURE 的"应该怎么分层"，这里只放"这个项目实际怎么写"。

## API / 数据契约模式

- <例：所有 API 返回 envelope `{ data, error, meta }`，不直接返回数组>
- <例：错误码统一用 `<MODULE>_<KIND>` 形式，如 `ORDER_NOT_FOUND`>

## 命名 / 文件组织模式

- <例：React 组件文件 `Foo.tsx`，对应 hook 在同目录 `useFoo.ts`>
- <例：Python 模块用 `<domain>/repository.py + use_cases.py + schemas.py` 三件套>

## 测试模式

- <例：fixture 命名 `make_<entity>`，工厂统一在 `tests/factories/`>
- <例：所有 API 测试都走 httpx + 真 DB（test schema），不 mock DB>

## 错误处理模式

- <例：用户态错误抛 `BizError`，框架自动 4xx；意外异常让它冒泡，框架自动 5xx + Sentry>

## 日志 / 可观测模式

- <例：结构化 JSON 日志，固定字段 `request_id / user_id / latency_ms`>

## UI 模式（UI 类项目）

- <例：所有列表页空态走 `<EmptyState variant="first-time">`，不自己写文案>
- <例：表单提交按钮在 loading 时 disabled，不显示 spinner，避免抖动>

## AI / Agent 模式（AI 项目）

- <例：所有 LLM 调用经 `lib/llm/client.ts`，禁止直连 SDK>
- <例：prompt 必须从 `prompts/` 加载，不内联>

## 反模式（曾经踩过、明确不要）

- <例：不要在 `routers/` 里写业务逻辑，已被多次 review 打回>
```

### active-context.md

```md
# Active Context

- Last updated: <date>
- Branch:
- Linked design doc:
- Linked requirements:

## 当前焦点

<这一周/这个 sprint 在做什么。1–3 句>

## 已完成（最近）

- [x]
- [x]

## 进行中

- [ ]
- [ ]

## 下一步（按顺序）

1.
2.
3.

## 当前阻塞

- <什么在卡，谁能解，为什么>

## 决策待定

- <Open question + 谁来回答 + 截止时间>

## 给下一会话 agent 的留言

<上一个 agent / 上一次会话留给下一次的 hand-off。要具体：在做 X，已完成 Y，下一步 Z。>
```

### active-context-map.md（当 active-context 过长时）

当 `active-context.md` 超过 100 行、30KB，或已经让 agent 开工读上下文明显变慢时，新增同目录 `active-context-map.md`。它不是第二份上下文真相源，只是检索入口。

```md
# Active Context Map

- Source: `docs/memory-bank/active-context.md`
- Last updated: <date>
- Rule: 先选关键词，再用 `rg -n "<search terms>" docs/memory-bank/active-context.md` 找详细段落。

| 关键词 | 什么时候选 | 搜索词 | 详细内容 |
|---|---|---|---|
| <短 keyword> | <用户任务信号> | `<term1>` / `<term2>` | `active-context.md` 中包含这些搜索词的最近段落 |
```

维护规则：

- 只记录可检索的关键词、任务信号和搜索词，不复制长正文。
- 每次往 `active-context.md` 新增长期会反复查询的主题时，同步补一行 map。
- map 与正文冲突时，以 `active-context.md` 为准，并立刻修 map。

## 使用规则

### 谁来更新

| 文件 | 谁更新 | 何时更新 |
|---|---|---|
| brief.md | 维护者 / agent 协助 | 项目状态变化、人员变动、定位调整 |
| tech-context.md | 维护者 / agent 协助 | 架构决策落地后、技术栈调整、出现新坑 |
| patterns.md | 维护者 / agent 协助 | code review 发现新模式、确立反模式时 |
| active-context.md | **每个会话结束时 agent 必须更新** | 每次会话 |

### Agent 行为约束

进入项目时：

1. 如果存在 `active-context-map.md`，先读 map，按用户任务选择 1-3 个关键词。
2. 用 map 里的搜索词定位 `active-context.md` 详细段落；只有 map 缺失、冲突或当前任务跨多个历史主题时，才整读 `active-context.md`。
3. 再读 `patterns.md`（避免犯本项目反模式）。
4. 必要时读 `tech-context.md` 与 `brief.md`。

会话结束时：

1. 更新 `active-context.md` 的"已完成 / 进行中 / 下一步 / 给下一会话留言"
2. 如果发现新模式或反模式，提议更新 `patterns.md`（不擅自改，先建议）
3. 如果 tech-context 与代码现实漂移，提议更新

### 与真相源冲突时

memory-bank 的内容和 `README/ARCHITECTURE/BRANCHING/DESIGN` 真相源冲突时：

- **真相源赢**。
- agent 立刻指出冲突，并提议同步 memory-bank。
- 永远不要反向（用 memory-bank 覆盖真相源）。

### 反模式

- 把 ARCHITECTURE.md 的全部决策表复制到 tech-context.md → 双份维护必漂移。
- patterns.md 写成"通用最佳实践"（如"函数应该短"）→ 那是 lint 的事，patterns 只放本项目特定。
- active-context.md 多会话不更新 → 等于没用，agent 会基于过期信息工作。
- active-context.md 越写越长但没有 map → 每次开工都会整读历史流水账，浪费上下文并放大旧信息干扰。
- 把敏感信息（密钥、客户名单）写进 memory-bank → 它会被 agent 多次读，泄露面大。

## Stage 路由

| 阶段 | Memory Bank 动作 |
|---|---|
| Stage 4 脚手架 | 创建四份模板的最小可用版本（brief / tech-context 填指针，patterns 留空，active-context 写"刚 bootstrap 完成，下一步 X"） |
| Stage 5 Feature 规划 | 更新 active-context（焦点 + 下一步） |
| Stage 6 实现 | 会话开始读 active-context；结束更新 active-context |
| Stage 7 验证 | active-context 标"验证中" + 风险 |
| Stage 8 PR/发布 | active-context 标"PR #N pending review" |
| Stage 9 维护 | 重大变更时同步 patterns / tech-context |
| Stage I 接手 | 第一次会话用现状报告填四份；存量项目可作为 Stage I 输出物之一 |
