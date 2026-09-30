# 需求、设计与交付模板

用于创建 Requirements Doc、Design Doc、Layout Spec 和 PR Body。业务意图由用户/owner 提供；agent 从已有材料提取、查证、结构化并提出建议，未确认的内容须标明。

## Requirements Doc（基于用户材料）

已有文档直接补充缺失内容，避免重复填表。按场景保留适用字段；建议和假设先作为审查结果给用户确认，确认后再更新需求正文。`reviewed` / `locked` 须对应用户实际确认，审查通过不能自动改变状态。

```md
# Requirements: <Product/Feature> v0.0.1

- Status: <draft | reviewed | locked>
- Owner: <用户名>
- Last updated: <date>

## 业务背景

<从用户材料提取为什么做、当前问题、机会；注明来源，缺失项附建议请用户确认。>

## 目标用户与场景

| 用户类型 | 核心场景 | 频率 | 关键痛点 |
|---|---|---|---|

## PSPS

| Persona | Scenario | Pain | Solution Surface |
|---|---|---|---|
| 管理者 / owner | | | 统计、状态、指标、异常 |
| 执行者 | | | 最少必填、默认值、下一步动作 |
| 协作者 / 外部角色 | | | 权限、通知、交接、验收 |

## 资料来源与待确认假设

- 来源：<材料 / 文档位置及版本>
- 待确认假设：<内容、依据、影响；确认后更新对应正文>

## 业务目标

- 一句话目标：
- 可量化的成功指标：
  - <指标 1：当前值 → 目标值 → 截止时间>

## P0 功能列表

1. **<功能名>**
   - 用户价值：
   - 验收标准：<前置条件 / 用户动作 / 可观察结果；关联下方规则或异常>

## 核心流程、规则与验收

- 主流程：<触发 → 处理 → 交接 → 完成条件>

| 场景 / 异常 | 业务规则 | 预期结果 / 验收样例 |
|---|---|---|

<涉及跨角色或审批时补充谁可执行什么操作、可见哪些数据、如何流转；涉及数据或集成时补充来源、口径、依赖与失败处理。只保留适用内容，未确认规则保持待决。>

## P1 / Later

## 非目标

## 约束

- 合规：
- 性能：
- 预算：
- 时间：
- 技术约束：

## 已知风险

## Open Questions（待决事项）

- [ ] Q1: <问题 / 影响 / 可选方案及代价 / 推荐理由 / 决策人>

## 用户确认记录

- 确认的需求版本与事项：<关联用户实际答复>
- 已确认后置项：<影响边界 / 关闭时点>
- 约定的下一步：
```

## Design Doc

生命周期用目录表达：

| Status | 文件位置 | 含义 |
|---|---|---|
| draft | `docs/design/backlog/` | 起草中，未启动 |
| active | `docs/design/active/` | 当前在做 |
| done | `docs/design/done/` | 已完成、已上线 |
| archived | `docs/design/done/` | 放弃或历史保留 |

`AGENTS.md` 默认只读 `active/`；查 backlog/done 需要用户明确要求。

```md
# Design Doc: <Topic> v0.0.1

- Status: <draft | active | done | archived | superseded by <design-doc-slug>>
  <!-- design doc 用文件 slug 引用（无连续编号）；ADR 用 ADR-MMMM。两者风格不同是有意为之。 -->
- Owner: <name or team>
- Last updated: <date>
- Started: <YYYY-MM-DD>（active 时填）
- Completion date: <YYYY-MM-DD>（done 时填）
- Linked Requirements: docs/requirements/...
- Linked Layout: docs/design/layout-spec-<page>.md（UI 类）
- Linked ADR(s): docs/decisions/ADR-NNNN-...（如有架构决策）

## Background

## Goal

## Scope

## Non-goals

## User Flow / System Flow

## PSPS-Derived Surface

| 触发 | 必须设计 |
|---|---|
| 管理者 / 老板 | 统计/看板/报表、状态分布、核心指标 |
| 任务分配 / 流转 | 状态机、Kanban/队列、owner、阻塞原因 |
| 图片 / 素材 / 商品 / 文件 / 资产 | 资产库/Gallery、元数据、搜索筛选、生命周期 |
| 排期 / 计划 / 时间线 | Gantt/Calendar/Timeline、起止日期、依赖 |

## Data Model / State Changes

## API / CLI / UI Changes

## Milestones

| Milestone | 行为闭环 | 影响文件 | Validation Gate |
|---|---|---|---|

## Risks and Rollback

## Acceptance Criteria

## Open Questions

## Validation Results（done 时回填）
```

## Layout Spec（页面布局，md 形式）

在写代码和拉 Figma 前先用 md 定布局。ASCII 图给人看，结构化列表给 agent / diff 用。

````md
# Layout Spec: <Page Name>

- Status: draft
- Linked Requirements: docs/requirements/...
- Linked Design: ../../DESIGN.md
- Last updated: <date>

## 页面意图

<一句话：这个页面让什么用户在什么场景完成什么任务。>

## 关键 KPI

## 视觉框图（ASCII，桌面优先）

```text
┌────────────────────────────────────────────────────┐
│ [Logo]   Nav1  Nav2  Nav3              [User] [⚙] │
├──────────┬─────────────────────────────────────────┤
│  Side    │  Breadcrumb > Page Title          [CTA] │
│  Nav     ├─────────────────────────────────────────┤
│          │  Filter  Search              [Refresh]  │
│          ├─────────────────────────────────────────┤
│          │              Main Content               │
└──────────┴─────────────────────────────────────────┘
```

## 区域结构

- Header
- Sidebar
- Main
  - PageHeader
  - Toolbar
  - Content
  - FooterBar

## 区域 → 组件映射

| 区域 | 组件 | 变体 | 备注 |
|---|---|---|---|

## 状态矩阵

| 状态 | 触发 | 主区域表现 | 周边表现 |
|---|---|---|---|
| 初次空 | | | |
| 过滤空 | | | |
| 加载 | | | |
| 错误 | | | |

## 响应式断点

| 断点 | 行为 |
|---|---|
| ≥ 1280 | |
| 768–1279 | |
| < 768 | |

## 交互细节

## 可访问性

## Open Questions
````

## PR Body

```md
## Why

## What Changed

## Linked Spec

- Requirements: docs/requirements/...
- Design Doc: docs/design/...
- Layout Spec: docs/design/layout-spec-...（UI 改动）
- ADR: docs/decisions/...

## Validation

## Risks / Rollback

## Docs Updated
```
