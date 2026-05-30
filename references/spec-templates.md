# Spec 模板索引

本文件只做模板导航，避免一次性加载所有模板。需要创建或更新具体文档时，按目标文件读取对应 reference。

## 典型文档结构

```text
README.md
ARCHITECTURE.md
DEVELOPMENT.md
BRANCHING.md
DESIGN.md
AGENTS.md
CONSTITUTION.md
docs/
├── requirements/
│   └── requirements-v0.0.1.md
├── design/
│   ├── active/
│   │   └── design_doc-v0.0.1-bootstrap.md
│   ├── backlog/
│   ├── done/
│   └── layout-spec-<page>.md
├── decisions/
│   └── ADR-0001-record-architecture-decisions.md
├── memory-bank/
│   ├── brief.md
│   ├── tech-context.md
│   ├── patterns.md
│   └── active-context.md
├── prompts/
│   └── README.md
├── plans/
│   └── implementation-plan-<topic>.md
└── governance/
    ├── folder-declaration-v0.md
    ├── terminology-glossary.md
    └── changelog.md
```

## 读取路由

| 要创建/更新 | 读取 |
|---|---|
| 工程场景地图 / 使用路由 | `engineering-scenario-map.md` |
| PSPS / 需求洞察 / 构建闭环 | `psps-framework.md` |
| `README.md` | `templates-core.md` |
| `ARCHITECTURE.md` | `templates-core.md` |
| `DEVELOPMENT.md` | `templates-core.md` |
| `BRANCHING.md` | `templates-core.md` |
| `DESIGN.md` | `templates-core.md` |
| `AGENTS.md` | `templates-core.md` |
| `CONSTITUTION.md` | `templates-governance.md` |
| ADR | `templates-governance.md` |
| Folder Declaration | `templates-governance.md` |
| glossary / changelog | `templates-governance.md` |
| Requirements Doc | `templates-specs.md` |
| Design Doc | `templates-specs.md` |
| Layout Spec | `templates-specs.md` |
| PR Body | `templates-specs.md` |
| Checkout / Worktree / Implementation Plan / Review Pipeline | `execution-pipeline.md` |
| Refactor Plan / 行为保持型重构 | `refactoring-rules.md`、`checklists.md` |
| Agent 执行纪律 / Source-driven gate / Change size | `agent-operating-standards.md` |
| Memory Bank | `memory-bank-guide.md` |
| Prompts 操作手册 | `prompts-guide.md` |
| Skill 级 L1 纠偏日志 | `lessons.md` |
| Skill 级 L2 验证模式 | `patterns-skill.md` |

## 使用原则

- 业务需求文档由用户/owner 提供；agent 只负责结构化、校验和提问。
- `ARCHITECTURE.md` 写结论和边界，ADR 写为什么这么选。
- `CONSTITUTION.md` 只放红线，不放偏好。
- `docs/design/{backlog,active,done}/` 用目录表达生命周期。
- POC / Spike 项目先读 `scenario-playbooks.md` 的轻量模式，达到升级触发条件后再补全本索引里的治理骨架。

## Legacy 迁移提示

接手旧项目时，不要强行改目录。先在现有 `docs/` 下建立映射：

| 旧文档形态 | 新治理位置 |
|---|---|
| `PRD.md` / `prd.md` | `docs/requirements/requirements-v0.0.1.md`（或保留原文件并在 README 指向它） |
| `docs/*design*.md` | `docs/design/backlog|active|done/`，按实际状态迁移 |
| `docs/refact_plans/*.md` | 行为保持类进入维护记录；架构决策抽取成 ADR |
| `docs/architecture/*.md` | 与 `ARCHITECTURE.md` 对齐，旧文件标历史/专题 |
| 零散 prompt 文档 | `docs/prompts/` 操作手册或运行时 `prompts/` |

迁移原则：先加索引和交叉引用，再移动文件；文件移动必须有验证或 owner 确认。
