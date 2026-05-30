# 核心项目文档模板

用于创建根级项目文档：`README.md`、`ARCHITECTURE.md`、`DEVELOPMENT.md`、`BRANCHING.md`、`DESIGN.md`、`AGENTS.md`。

只在需要生成对应文件时读取本文件。模板里的占位符保留给 agent 按项目事实填写；不知道的内容标 `TODO（需用户/owner 确认）`。

## README.md

````md
# <Project>

<一句话项目定义：面向谁、解决什么、当前核心能力。>

## Status

<pre-dev | prototype | active | uat | production>

## Start Here

- [Architecture](./ARCHITECTURE.md)
- [Constitution](./CONSTITUTION.md)
- [Development Rules](./DEVELOPMENT.md)
- [Branching](./BRANCHING.md)
- [Design System](./DESIGN.md)
- [Requirements](./docs/requirements/)
- [Design Docs](./docs/design/) · [Decisions (ADR)](./docs/decisions/)
- [Memory Bank](./docs/memory-bank/) · [Prompts](./docs/prompts/)
- [Folder Declaration](./docs/governance/folder-declaration-v0.md)
- [Changelog](./docs/governance/changelog.md)

## Current Structure

| Directory | Purpose |
|---|---|
| `apps/` | 用户可运行的应用 |
| `services/` | 后端服务 |
| `packages/` | 共享代码 |
| `docs/` | 项目文档 |
| `scripts/` | 开发和运维脚本 |
| `configs/` | 配置模板 |

## Local Run

```bash
<install command>
<dev command>
```
````

## ARCHITECTURE.md

```md
# Architecture

- Status: active
- Last updated: <date>

## 一句话架构结论

<P0 架构决策和核心非目标。>

## Goals

## Non-goals

## System Boundaries

### <Frontend/App>
负责：
不负责：

### <Backend/Runtime>
负责：
不负责：

### <External Platform>
负责：
不负责：

## Technical Baseline

| 维度 | 选定方案 | 主要理由 | 主要代价 | 退出成本 | ADR |
|---|---|---|---|---|---|
| 项目形态 | | | | | |
| Repo 组织 | | | | | |
| 客户端形态 | | | | | |
| 前端渲染 | | | | | |
| 前后端关系 | | | | | |
| 后端架构 | | | | | |
| 数据架构 | | | | | |
| 通信协议 | | | | | |
| 鉴权与身份 | | | | | |
| 部署环境 | | | | | |
| 异步任务 | | | | | |
| 可观测性 | | | | | |
| 测试策略 | | | | | |
| CI/CD | | | | | |
| 配置与密钥 | | | | | |

## Data Truth Source

| 数据/状态 | 真相源 | 写入者 | 读取者 |
|---|---|---|---|

## Key Flows

## Risks and Future Phases
```

## DEVELOPMENT.md

````md
# Development Rules

## Spec-driven Development

- 业务需求由用户/owner 提供，agent 不编造。
- 改动影响架构、状态机、存储、权限、公共 API 或 UI 模式时，先更新 design doc / ADR。
- 每个任务只做一个 topic。

## Local Setup

```bash
<bootstrap command>
```

## Testing Rules

- 最小相关验证优先。
- 无法运行检查时，说明原因、风险和后续动作。

## Definition of Done

- 关联 requirements / design doc。
- 文档、测试、changelog 按影响范围同步。
- `CONSTITUTION.md` 红线 0 触发，或已走豁免流程。
````

## BRANCHING.md

```md
# Branching & Commit Rules

## 策略

<GitHub flow | trunk-based | git-flow>

## 长期分支

- `main`: production baseline
- `uat`: acceptance / release verification（如适用）
- `dev`: daily integration（如适用）

## 短期分支命名

- `feature/<topic>`
- `fix/<topic>`
- `docs/<topic>`
- `refactor/<topic>`
- `codex/<type>/<topic>`（AI agent 分支）

## 一个分支一个意图

不要混合 feature、refactor、docs、依赖升级和格式化。

## Checkout / Worktree Rules

编辑前先运行 `git status --short --branch`，判断当前 checkout 是否适合承载本任务。

必须使用独立 worktree：

- 从 `main` / `dev` / `release` 等共享分支开始新 feature、bug fix、refactor、迁移或 spike。
- 当前 checkout 有未提交改动，且与本任务可能重叠、来源不明或会污染 PR diff。
- 多 agent / 多任务并行，每个任务或 agent 使用独立 worktree，并声明不重叠的写入范围。
- 高风险改动：跨模块重构、数据迁移、权限/支付/状态机/公共 API/构建系统/依赖升级。
- 需要保留当前现场用于复现、对比或 review。

允许当前 checkout 直接开发：

- 当前分支已经是目标任务或目标 PR 分支。
- 工作区干净，或只有与本任务明确相关的未提交改动。
- 小修、文档、注释、配置小改、单 PR review follow-up，且没有并行任务。

脏工作区规则：

- 不得擅自 `reset` / `checkout --` / `clean` / `stash` 用户改动。
- 无关且不重叠的改动可以保留，但收尾说明未触碰。
- 重叠、来源不清或影响 diff 时，先停下，让 owner 选择提交、手动 stash、新建 worktree 或授权 agent stash。

## Commit Rules

优先 Conventional Commits：

- `feat:`
- `fix:`
- `docs:`
- `refactor:`
- `test:`
- `chore:`

## PR 规则

- PR body 必须包含 why / what / validation / risk。
- 触发架构维度变更时关联 ADR。
```

## DESIGN.md

```md
# Design System

- Status: active
- Last updated: <date>

## 设计原则

## Design Tokens

### Color

### Typography

### Spacing

### Radius / Shadow / Motion

## 组件清单

| Component | Variants | Usage | Notes |
|---|---|---|---|

## 交互模式

### Loading
### Empty
### Error
### Success / Confirmation
### Navigation
### Form
### Accessibility

## 命名与文件

## 变更规则

- 新组件先进本文件再写代码。
- token 变更必须列影响范围。
- 弃用组件标 `@deprecated` + 替代项 + 期限。
```

## AGENTS.md

```md
# Agent Rules

- 大改前先读 `README.md`、`ARCHITECTURE.md`、`DEVELOPMENT.md`、`BRANCHING.md`、`CONSTITUTION.md`。
- 开工先读 `docs/memory-bank/active-context.md` + `docs/memory-bank/patterns.md`。
- UI 任务还必须读 `DESIGN.md` 与对应 layout spec。
- 每个正式任务必须关联 `docs/design/active/*` 与 `docs/requirements/*`。
- 按 `BRANCHING.md` 判断 checkout/worktree；不得擅自 stash/revert/reset 用户改动。
- 业务需求由用户提供，agent 不编造业务意图。
- 没有 spec，不新增架构层、状态机、存储、权限、全局依赖或公共 API。
- 新依赖、外部 API、平台规则、框架升级、鉴权/支付/合规必须优先查项目内锁定版本或官方来源。
- 大 diff 先拆 vertical slice；混合 feature/refactor/格式化/依赖升级时先拆 PR。
- 如果实现必须偏离 spec，先更新 spec，再改代码。
- 触动 `CONSTITUTION.md` 红线的改动 → 立刻停下，提示用户而非自行突破。
- 默认后端/API/service 自测优先；浏览器模拟只在用户要求、产品能力本身或浏览器特有 bug 时运行。
- 会话结束更新 `docs/memory-bank/active-context.md`。
- 收尾必须说明变更文件、已运行验证、剩余风险。
```
