# 项目形态 Starter Blueprints

用于新建项目（Stage 4 脚手架）落地目录结构与首次提交清单。

> **关系说明**：
> - 形态决策与判断流程见 `architecture-cases.md` §0。
> - 20 大类通用架构决策见 `architecture-cases.md`。
> - AI 项目额外的 11 大类架构决策见 `architecture-cases-ai.md`。
> - 本文件**只管 starter 目录结构与首次提交清单**，不重复架构决策内容。

## 形态速查（详细决策见 architecture-cases.md §0）

| 项目特征 | 推荐形态 |
|---|---|
| 管理台 UI、外部平台集成、后端 DB 是产品真相源 | Web + Backend |
| 本地数据、本地进程、离线能力、桌面分发、Agent runtime | Desktop + Local Agent |
| CLI、SDK、自动化、后台任务、Agent runtime | Python Agent / CLI |
| 可复用 API package、公共类型、示例、兼容性承诺 | Library / SDK |
| 多 app、共享协议、共享 UI、长期平台化演进 | Full-stack Monorepo |

> 形态判断为 Unknown 时**不要**选 starter，先到 `architecture-cases.md` §0 完成 4 步判断。

## 所有形态共享的根级文件

每种形态至少包含：

```text
README.md                    # 项目定位、Start Here、本地启动
ARCHITECTURE.md              # 架构结论、边界、技术选型、P0 非目标（含 Technical Baseline 决策表）
DEVELOPMENT.md               # spec-driven、测试、完成定义（分支规范引用 BRANCHING.md）
BRANCHING.md                 # 分支与提交规范（独立真相源，Stage 3 落地）
DESIGN.md                    # 设计系统真相源（UI 类项目必备）
AGENTS.md                    # 给 AI agent 的项目级约束
CONSTITUTION.md              # 项目红线
LICENSE
.gitignore                   # 必须 ignore 运行时目录（output/ runtime/ logs/ 等）
.editorconfig
.env.example                 # 环境变量模板，禁止提交真实 secret
docs/
├── requirements/
│   └── requirements-v0.0.1.md   # 用户提供的业务需求文档
├── design/
│   ├── active/
│   │   └── design_doc-v0.0.1-bootstrap.md
│   ├── backlog/
│   ├── done/
│   └── layout-spec-<page>.md    # 页面布局 md（UI 类项目）
├── decisions/
│   └── ADR-0001-record-architecture-decisions.md
├── memory-bank/
│   ├── brief.md
│   ├── tech-context.md
│   ├── patterns.md
│   └── active-context.md
├── prompts/
│   └── README.md
└── governance/
    ├── folder-declaration-v0.md
    ├── terminology-glossary.md
    └── changelog.md
configs/
└── config.yaml.demo
scripts/
└── bootstrap_dev_env.sh
```

> Stage 4 完成判定见 `checklists.md` 的「新项目 Checklist」。

## Web + Backend

适用于 Web 管理台、后端拥有产品状态、外部平台集成的项目。

```text
<project>/
├── package.json
├── pnpm-workspace.yaml
├── apps/
│   └── studio-web/
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       ├── index.html
│       ├── public/
│       └── src/
│           ├── main.tsx
│           ├── App.tsx
│           ├── routes.tsx
│           ├── pages/
│           ├── components/
│           │   ├── ui/
│           │   └── blocks/
│           ├── services/
│           ├── hooks/
│           ├── types/
│           ├── lib/
│           └── styles/
├── services/
│   └── backend-api/
│       ├── pyproject.toml
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   ├── modules/
│       │   │   └── <domain>/
│       │   │       ├── domain.py
│       │   │       ├── schemas.py
│       │   │       ├── repository.py
│       │   │       └── use_cases.py
│       │   ├── models/
│       │   ├── core/
│       │   ├── integrations/
│       │   └── workers/
│       ├── migrations/
│       └── tests/
├── packages/
│   └── protocol/
└── tests/
    └── e2e/
```

目录职责：

- `apps/studio-web/`：只做 UI 与用户交互，不承载后端业务编排。
- `components/ui/`：无业务语义的原子组件。
- `components/blocks/`：带业务语义的页面组合块。
- `services/backend-api/app/routers/`：HTTP 适配、鉴权、校验、事务边界。
- `modules/<domain>/`：领域逻辑、schema、repository、use cases 内聚。
- `integrations/`：第三方 SDK 封装。外部平台不是产品真相源。
- `packages/protocol/`：前后端共享契约和类型。

首次提交最小清单：

```text
README.md ARCHITECTURE.md DEVELOPMENT.md BRANCHING.md AGENTS.md CONSTITUTION.md
.gitignore .env.example
docs/design/active/design_doc-v0.0.1-bootstrap.md
docs/design/backlog/.gitkeep
docs/design/done/.gitkeep
docs/decisions/ADR-0001-record-architecture-decisions.md
docs/governance/folder-declaration-v0.md
docs/governance/terminology-glossary.md
docs/governance/changelog.md
docs/memory-bank/brief.md
docs/memory-bank/tech-context.md
docs/memory-bank/patterns.md
docs/memory-bank/active-context.md
docs/prompts/README.md
configs/config.yaml.demo
package.json pnpm-workspace.yaml
apps/studio-web/package.json
apps/studio-web/tsconfig.json
apps/studio-web/vite.config.ts
apps/studio-web/index.html
apps/studio-web/src/main.tsx
apps/studio-web/src/App.tsx
apps/studio-web/src/routes.tsx
services/backend-api/pyproject.toml
services/backend-api/app/main.py
services/backend-api/app/core/config.py
services/backend-api/migrations/.gitkeep
services/backend-api/tests/.gitkeep
```

## Desktop + Local Agent

适用于本地数据、本地进程、Agent runtime、离线流程或桌面分发项目。

适用经验：本地 agent shell、local-first studio、资源注册表、托管外部 CLI、MCP/CLI/exec 接口。默认不要把桌面壳写成“只有 UI 的 WebView”；桌面项目的核心难点通常是本地 runtime 生命周期、用户数据目录、权限、进程编排和可观测性。

```text
<project>/
├── package.json
├── pnpm-workspace.yaml
├── apps/
│   └── desktop/
│       ├── package.json
│       ├── src-tauri/
│       │   ├── tauri.conf.json
│       │   ├── Cargo.toml
│       │   └── src/
│       │       ├── main.rs
│       │       ├── commands/
│       │       ├── lifecycle/
│       │       └── local_backend/
│       └── src/
│           ├── main.tsx
│           ├── pages/
│           ├── components/
│           ├── services/
│           └── hooks/
├── agent/
│   ├── pyproject.toml
│   ├── core/
│   ├── runtimes/
│   ├── tools/
│   └── tests/
├── local-services/
│   ├── resource-registry/
│   ├── executor-host/
│   └── mcp-server/
├── packages/
│   ├── protocol/
│   ├── ui/
│   └── cli/
├── skills/
├── distribution/
└── config/
    └── default.yaml
```

目录职责：

- `apps/desktop/`：UI、桌面壳、本地 backend 生命周期、IPC。
- `agent/`：默认 AgentCore 实现，可替换，不是产品真相源。
- `local-services/resource-registry/`：本地资源真相源，统一管理 provider、skills、extensions、memory、history、profiles、layouts 等资源。
- `local-services/executor-host/`：受管执行宿主，负责启动/停止/观察外部 CLI 或 agent runtime。
- `local-services/mcp-server/`：把本地资源暴露给 MCP-capable agent；如暂不做 MCP，可留 `.gitkeep`。
- `packages/protocol/`：IPC、CLI、runtime、agent 消息契约。
- `packages/ui/`：跨 app 复用的无业务组件。
- `packages/cli/`：本地命令面；可承载 `ext` / `exec` 风格接口。
- `skills/`：可加载 agent skills。
- `distribution/`：签名、打包、安装器、release notes。
- `config/`：只存模板；运行时配置在用户目录。

进阶边界：

- **connected mode**：外部 agent 自己运行，通过 MCP / CLI extension 访问本地资源。
- **managed mode**：桌面 app 启动外部 agent/CLI，持有 execution session、terminal bridge、stop/retry 状态。
- **resource registry** 是本地资源真相源；UI、MCP、CLI、内置 agent 都只通过同一套 schema 读写。
- **executor binding** 是声明式配置，不是 UI 里拼命令字符串。
- **layout / whiteboard / memory** 等 agent 可写资源必须受限 schema + 审计日志，禁止任意脚本注入。

本地数据约定：

```text
~/.<product>/data/         # 用户数据和数据库
~/.<product>/runtime/      # pid、socket、临时运行态
~/.<product>/logs/         # 日志
~/.<product>/config.yaml   # 用户级配置
```

repo 禁止提交 `data/`、`runtime/`、`logs/`、`uploads/`、`output/`、`_reference_repo/` 等运行时目录。

首次提交最小清单：

```text
root shared files
package.json pnpm-workspace.yaml
apps/desktop/package.json
apps/desktop/src/main.tsx
apps/desktop/src-tauri/tauri.conf.json
apps/desktop/src-tauri/Cargo.toml
apps/desktop/src-tauri/src/main.rs
agent/pyproject.toml
agent/core/__init__.py
local-services/resource-registry/.gitkeep
local-services/executor-host/.gitkeep
local-services/mcp-server/.gitkeep
packages/protocol/package.json
packages/protocol/src/index.ts
packages/ui/package.json
packages/ui/src/index.ts
packages/cli/package.json
packages/cli/src/index.ts
skills/.gitkeep
config/default.yaml
distribution/.gitkeep
```

进阶项目首次提交额外建议：

```text
docs/decisions/ADR-0002-local-first-data-boundary.md
docs/decisions/ADR-0003-managed-vs-connected-agent-mode.md
docs/decisions/ADR-0004-resource-registry-schema.md
docs/design/active/design_doc-v0.0.1-runtime-lifecycle.md
```

## Python Agent / CLI

适用于 CLI 工具、SDK 式自动化、Agent runtime 或后台工作流。

```text
<project>/
├── pyproject.toml
├── uv.lock
├── src/
│   └── <package>/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       │   └── commands/
│       ├── core/
│       │   ├── agent.py
│       │   ├── planner.py
│       │   └── executor.py
│       ├── tools/
│       ├── integrations/
│       ├── prompts/
│       ├── config.py
│       └── logging.py
├── skills/
├── tools/
│   └── dev/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── config/
    └── default.yaml
```

目录职责：

- `cli/`：参数解析和命令路由，不写核心业务。
- `core/`：agent 状态机、规划、执行循环、领域规则。
- `tools/`：agent/runtime 可调用工具。
- `integrations/`：第三方 API 封装，业务逻辑不直接 import SDK。
- `prompts/`：prompt 模板集中管理。
- `skills/`：声明式可加载能力包。
- `tools/dev/`：项目开发脚本，区别于 agent tools。

首次提交最小清单：

```text
root shared files
pyproject.toml
src/<package>/__init__.py
src/<package>/__main__.py
src/<package>/config.py
src/<package>/cli/__init__.py
src/<package>/core/__init__.py
src/<package>/tools/__init__.py
src/<package>/integrations/__init__.py
src/<package>/prompts/.gitkeep
skills/.gitkeep
tests/unit/.gitkeep
tests/integration/.gitkeep
tests/fixtures/.gitkeep
config/default.yaml
```

## Library / SDK

适用于被其他应用消费的可复用包。

```text
<project>/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── package.json or pyproject.toml
├── src/
│   └── <package>/
├── tests/
├── examples/
├── docs/
│   ├── api/
│   └── guides/
└── scripts/
```

目录职责：

- `src/`：公共 API 和内部实现。
- `tests/`：兼容性和行为保证。
- `examples/`：可运行示例。
- `docs/api/`：API contract。
- `docs/guides/`：任务型指南。

规则：

- 公共 API 变化必须有 changelog 和 migration notes。
- examples 尽量纳入 CI。
- 明确支持的 runtime 版本。

## Full-stack Monorepo

适用于未来形态不确定，或多个 app/service 需要共享契约的长期项目。

```text
<project>/
├── DESIGN.md
├── package.json
├── pnpm-workspace.yaml
├── pyproject.toml
├── apps/
│   ├── web/
│   └── desktop/
├── services/
│   └── backend-api/
├── packages/
│   ├── protocol/
│   ├── ui/
│   └── cli/
├── docs/
│   ├── README.md
│   ├── design/
│   ├── architecture/
│   ├── governance/
│   ├── operations/
│   └── user-manual/
├── scripts/
├── tests/
└── output/
```

演进规则：

- 起步只开当前需要的目录。
- 至少两个消费者需要共享契约时，才开 `packages/protocol`。
- 真实出现本地 runtime 或桌面分发需求时，才开 `apps/desktop`。
- 每新增顶层目录，必须更新 `docs/governance/folder-declaration-v0.md`。
