# 接手已有项目 Playbook（Stage I：盘点）

> **核心原则**：默认尊重现状，不擅自重构。先分析、再判断、再补齐、最后才动代码。

适用场景：

- 用户接手他人/团队的现有 repo
- 用户问"这个项目怎么继续"、"该不该重构"、"先做什么"
- 用户给出已有 repo URL 或现状描述

本 playbook 的目标：

- 在动任何代码前，先得到一份**项目现状报告**。
- 决定走哪条路：**遵循现状** / **补齐缺失** / **先稳定再演进** / **必须重构**。
- 把对话从"凭直觉重构"扭回"基于证据的最小动作"。

---

## 0. 立场与边界

- 现有 repo 的约定 > 你的偏好。除非证据显示约定带来明确风险，否则**不要改**。
- 没有读完代码与文档前，**不输出"重构建议"**。
- 不存在的文档不要凭空补充内容；先标 `TODO（需用户/原作者确认）`。
- 业务意图永远问用户/原 owner，不臆测。

---

## 1. 盘点 Checklist（按顺序过）

### 1.0 自动识别（先跑一遍机器可判断的，再走人工盘点）

> 目的：在动手读代码前，**用文件信号**快速生成第一版"项目类型 + 工具链"推断，节省后续盘点时间。Agent 应当能在 1–2 分钟内输出本节结果。

**项目语言/运行时识别**：

| 信号文件 | 推断 |
|---|---|
| `package.json` + `pnpm-workspace.yaml` | Node.js monorepo，pnpm |
| `package.json` + `lerna.json` / `nx.json` / `turbo.json` | Node.js monorepo（Lerna / Nx / Turborepo） |
| `package.json` 单一 + `next.config.*` | Next.js Web 项目 |
| `package.json` + `vite.config.*` | Vite 前端 |
| `package.json` + `tauri.conf.json` | Tauri 桌面端 |
| `package.json` + `electron-builder.yml` | Electron 桌面端 |
| `pyproject.toml` + `[tool.poetry]` | Python（Poetry） |
| `pyproject.toml` + `[tool.uv]` 或 `uv.lock` | Python（uv） |
| `requirements.txt` 无 `pyproject.toml` | Python（pip 旧式） |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml` / `build.gradle*` | Java/Kotlin |
| 多语言混合 | Polyglot monorepo（标记 hybrid） |

**项目形态推断**：

| 信号 | 推断形态 |
|---|---|
| 有 `apps/desktop` + Tauri/Electron 配置 | Desktop + Local Agent（候选） |
| 有 `apps/web` + 后端服务目录（`services/` / `backend/` / `api/`） | Web + Backend |
| 仅 `src/` + `cli/` 子目录 + `pyproject.toml` 有 entry point | Python Agent / CLI |
| 有 `package.json` 的 `"main"` / `"exports"` + `examples/` + 无运行入口 | Library / SDK |
| 多 app + `packages/` + workspace 配置 | Full-stack Monorepo |
| 信号冲突或不足 | Unknown（继续走 §1.1–1.5） |

**框架/工具栈识别**：

| 维度 | 信号文件 |
|---|---|
| 前端框架 | `next.config.*` / `nuxt.config.*` / `vite.config.*` / `angular.json` / `svelte.config.*` |
| UI 库 | `tailwind.config.*` / `theme.ts` / 包依赖里的 `@mui/*` `antd` `chakra-ui` `shadcn` |
| 后端框架 | 依赖 `fastapi` `flask` `django` `express` `nestjs` `gin` `actix-web` `spring-boot` |
| ORM / DB | 依赖 `sqlalchemy` `prisma` `drizzle` `typeorm` `mongoose` |
| Migration | `alembic/` / `prisma/migrations/` / `migrations/` |
| 测试框架 | `pytest.ini` / `jest.config.*` / `vitest.config.*` / `playwright.config.*` |
| Lint / Format | `.eslintrc*` / `ruff.toml` / `.prettierrc*` / `biome.json` |
| CI 平台 | `.github/workflows/` / `.gitlab-ci.yml` / `.circleci/` / `Jenkinsfile` |
| 容器化 | `Dockerfile` / `docker-compose.*` / `Containerfile` |
| 部署 | `vercel.json` / `netlify.toml` / `railway.toml` / `fly.toml` / `serverless.yml` / `wrangler.toml` |
| Monorepo 工具 | `pnpm-workspace.yaml` / `nx.json` / `turbo.json` / `lerna.json` / `rush.json` |
| 包管理器锁 | `pnpm-lock.yaml` / `package-lock.json` / `yarn.lock` / `uv.lock` / `poetry.lock` / `Cargo.lock` / `go.sum` |

**AI / Agent 痕迹（加分项）**：

| 信号 | 推断 |
|---|---|
| `prompts/` 顶层目录 / `**/*.prompt.md` | 有 prompt 管理 |
| `agent/` / `agents/` / `skills/` 顶层 | Agent runtime |
| 依赖 `langchain` `langgraph` `llamaindex` `openai` `anthropic` `litellm` | LLM SDK |
| 依赖 `chromadb` `qdrant-client` `pinecone-client` `weaviate-client` | 向量库 |
| `langfuse` / `langsmith` / `helicone` | LLM 可观测性 |
| `evals/` / `eval/` + `*.eval.*` | 有 eval 体系 |

**Legacy / pre-vibecoding 文档痕迹**：

| 信号 | 推断 |
|---|---|
| `PRD.md` / `prd.md` / `PRD/` | 旧式需求入口，先映射到 requirements，不强制移动 |
| `docs/refact_plans/` | 旧式重构/修复设计记录，可能要抽取 ADR 或维护记录 |
| `docs/*design*.md` / `design_doc-v*.md` | 旧式 design doc，按实际状态映射 backlog/active/done |
| `docs/architecture/` 多份架构文档 | 可能存在多个架构真相源，需要先判定 as-is canonical |
| `prompts/` 或 `docs/prompts/` 零散 prompt | 可能需要 prompt registry 或 prompt 操作手册 |
| `output/`、`sandbox/`、`temp_*` 入仓 | POC / 实验遗留或运行时目录污染 |

**业务场景痕迹（用于决定是否读 `scenario-playbooks.md`）**：

| 信号 | 场景 |
|---|---|
| `selenium` / `playwright` / `spider` / `crawler` / `robots` | 浏览器自动化 / 数据采集 |
| `ocr` / `paddleocr` / `pdf` / `layout` / `invoice` | OCR / 文档智能 |
| `opencv` / `ffmpeg` / `fabric` / `reactflow` / `annotation` | 视觉 / 多媒体质检 |
| `prompt_versions` / `prompt_variant` / `llm_calls` / `trace` | LLM 生产链路 |
| `sandbox/` / `POC` / `spike` | POC / Spike |

**git 历史快速画像（在 repo 内跑）**：

```bash
# 项目活跃度
git log --since="6 months ago" --oneline | wc -l           # 近 6 个月 commit 数
git log --since="6 months ago" --format="%an" | sort -u    # 近 6 个月作者
git log --format="%H" | wc -l                              # 总 commit 数
git log -1 --format="%ai"                                  # 最后一次提交时间

# 分支策略推断
git branch -a                                              # 长期分支
git log --all --oneline --merges -20                       # 近期 merge 风格
git log --format="%s" -50                                  # commit message 风格（conventional? "fix"满天飞?）
```

**自动识别输出格式**：

```text
## 自动识别报告（机器推断，待人工确认）

- 主要语言/运行时: <Node.js 18+ / Python 3.11 / 多语言>
- 包管理器: <pnpm / npm / uv / poetry / cargo>
- 项目形态推断: <Web+Backend / Desktop+Local Agent / ...> （置信度: <高 | 中 | 低>）
- Repo 组织: <单 repo / monorepo（pnpm workspaces）/ polyglot monorepo>
- 前端栈: <Next.js / Vite + React / 无前端>
- 后端栈: <FastAPI / Express / 无独立后端>
- 数据层: <Postgres + SQLAlchemy + Alembic / 无 / 不明>
- CI: <GitHub Actions / 不存在>
- 部署: <Vercel / Docker + 自托管 / 不明>
- AI/Agent 痕迹: <无 / langchain + Pinecone / 自研 agent runtime>
- 业务场景推断: <RPA/数据采集 / OCR/文档智能 / LLM生产链路 / POC / 无明显场景>
- Legacy 文档痕迹: <无 / PRD.md + refact_plans / 多份 design_doc / 运行时目录入仓>
- 活跃度: <近 6 个月 N commits / M 名作者 / 最后提交 X 天前>
- 分支模型推断: <trunk-based / git-flow / 仅 main / 不明>
- Commit 风格: <conventional / 自由式 / 混合>

需要人工确认的疑点:
- <例：发现 prompts/ 但没有 LLM 依赖，可能是文档目录而非真 prompt 管理>
- <例：有 Dockerfile 但 CI 不构建镜像，可能未使用>
```

> §1.0 完成后，§1.1–1.5 的人工盘点可以**只关注机器看不到的**：业务真相源、真实分支用法、code review 严格度、暗坑等。

---

### 1.1 文档结构盘点

逐项标记 `存在 / 缺失 / 过期`：

- [ ] `README.md`（能解释项目是什么、给谁用、怎么跑？）
- [ ] `ARCHITECTURE.md` 或等价架构文档
- [ ] `DEVELOPMENT.md` 或等价开发规则
- [ ] `BRANCHING.md` 或在 `CONTRIBUTING.md` / `DEVELOPMENT.md` 内的分支与提交规范
- [ ] `DESIGN.md` 或等价设计系统文档（UI 类项目）
- [ ] `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`（AI agent 项目级约束）
- [ ] `docs/requirements/` 或等价业务需求文档目录
- [ ] `docs/design/` 设计文档目录（含 design docs / layout specs）
- [ ] 旧式 `PRD.md` / `docs/refact_plans/` / `design_doc-v*.md` 是否存在，当前状态是否可判断
- [ ] `docs/governance/` 治理文档（folder declaration / changelog / glossary）
- [ ] `CHANGELOG.md` 或等价变更记录
- [ ] `LICENSE`
- [ ] `.env.example` 或等价配置示例
- [ ] `.gitignore` 是否覆盖运行时目录

### 1.2 代码结构盘点

- [ ] 顶层目录用途是否一目了然？是否有 folder declaration？
- [ ] 是否有 `apps/ services/ packages/` 等清晰边界？或单体结构？
- [ ] 是否能找到主入口（`main.py` / `index.ts` / `App.tsx` / `cmd/`）？
- [ ] 测试目录是否存在？测试运行命令是否文档化？
- [ ] 配置/密钥管理方式（.env / secrets manager / config service）？
- [ ] 是否有运行时数据（output/ runtime/ logs/）误入 repo？
- [ ] 是否存在 POC/sandbox/temp 目录需要 ignore、归档或清理？

### 1.3 工程基础设施

- [ ] 包管理器锁文件存在且最新（`pnpm-lock.yaml` / `package-lock.json` / `uv.lock` / `poetry.lock`）
- [ ] CI 配置存在（`.github/workflows/` / `.gitlab-ci.yml` 等）
- [ ] CI 通过状态如何（main 是绿是红？最近 10 次 PR 通过率）
- [ ] 部署方式可见（Dockerfile / Procfile / serverless config / 部署脚本）
- [ ] 本地一键启动是否可行（`make dev` / `pnpm dev` / `bootstrap.sh`）

### 1.4 业务与运行时

- [ ] 业务真相源在哪里（DB / 外部平台 / 文件系统）？
- [ ] 当前在生产/UAT 跑吗？流量级别？
- [ ] 当前用户是谁？业务负责人是谁？
- [ ] 上一次大改动是什么？（git log + commit 频率分布）
- [ ] 是否有可见的"暗坑"：TODO/FIXME/HACK 数量、注释里的"don't touch"

### 1.5 团队与协作

- [ ] 当前活跃维护者数量与最后活跃时间
- [ ] 分支模型实际怎么用（看最近 30 天 PR）
- [ ] commit 信息风格（conventional? 自由式? 全 "fix"?）
- [ ] code review 实际严格度

### 1.6 AI / Agent 痕迹（如适用）

- [ ] 是否有 `prompts/`、`skills/`、`agent/`、`integrations/llm` 等目录
- [ ] 模型/provider 是否硬编码
- [ ] 是否有 LLM 调用观测（traces / langfuse / langsmith）
- [ ] 是否有 eval 体系

---

## 2. 现状报告输出格式

输出统一这份模板（**先报告，再建议**）：

```text
# 项目现状报告：<repo 名>

## 一句话定性
<这是一个 X 形态的项目，处于 Y 阶段，主要风险在 Z>

## 项目形态
<Web+Backend | Desktop+Local Agent | Python Agent/CLI | Library/SDK | Full-stack Monorepo | Hybrid | Unknown>

## 文档完备度
- 完备：<列出存在且新鲜的文档>
- 缺失：<列出缺失的文档>
- 过期：<最后更新时间 > 6 个月 或与代码不符>
- Legacy 文档：<PRD/refact_plans/design_doc 等旧式文档的映射建议>

## 代码结构判断
- 结构清晰度：<清晰 | 部分模糊 | 混乱>
- 模块边界：<是否存在 / 是否被尊重>
- 真相源：<是否唯一明确>
- 主要异味：<TODO 数量 / 循环依赖 / 巨型文件 / runtime 数据入仓 ...>

## 工程基础设施
- 本地一键运行：<能 / 不能 / 部分>
- CI 状态：<绿 | 红 | 不存在>
- 部署可见性：<清晰 | 模糊 | 不存在>
- 测试覆盖与可执行性：<能跑 / 跑不动 / 无测试>

## 业务与运行时
- 业务真相源：<DB / 外部平台 / 文件 / 不明>
- 当前生产状态：<生产 / UAT / 仅本地 / 不明>
- 业务负责人可达：<是 / 否>

## 关键风险（按严重性排序）
1.
2.
3.

## 建议路径（二选一）
- [ ] 路径 A：遵循现状，仅补关键缺口（推荐当结构尚可）
- [ ] 路径 B：稳定 + 治理优先（推荐当结构混乱但生产在跑）
- [ ] 路径 C：先建文档骨架，再有限演进（推荐当文档极度匮乏）
- [ ] 路径 D：必须重构（仅当现状阻碍业务推进，且有用户授权）

## 下一步 3 个动作
1.
2.
3.

## 用户需要回答的问题
- [ ] Q1:
- [ ] Q2:
```

---

## 3. 路径选择决策

按现状报告的判断，选一条路径走，**一次只走一条**。

### 路径 A：遵循现状，仅补关键缺口

**适用条件**（同时满足）：

- 文档至少存在 README + 架构信息
- 代码结构有明确模块边界
- 本地能跑、CI 基本绿
- 业务在生产稳定运行

**只补这些（不动代码）**：

1. 缺失的核心文档（按 `spec-templates.md` 索引选择 `templates-core.md` / `templates-governance.md` / `templates-specs.md` 补）
2. `BRANCHING.md`（如缺失，**先观察现状再写**，反映现状不要拍脑袋）
3. `AGENTS.md`（如团队会用 AI agent 协作）
4. 把已有约定明文化（不要发明新约定）

**不做**：重命名顶层目录、改架构、重构模块边界、升级主框架。

### 路径 B：稳定 + 治理优先

**适用条件**：

- 生产在跑但代码结构混乱 / 文档极少 / 修改风险高
- 业务负责人存在但工程基础薄弱

**顺序**：

1. **冻结架构变更**：宣布"接下来 N 周不动架构"。
2. **建立可观测性最小集**：日志结构化 + 关键路径追踪 + 错误上报。
3. **补 smoke 测试**：覆盖核心 happy path，作为后续动作的护栏。
4. **写 ARCHITECTURE.md**：**反映当前状态**，不写"理想状态"。
5. **建立 BRANCHING.md**：基于实际 git log 中的模式描述，而非理想模式。
6. **CHANGELOG.md**：从今天起记录变化。
7. 满足以上后，再考虑路径 A 的局部演进。

### 路径 C：先建文档骨架，再有限演进

**适用条件**：

- 接近"代码考古"状态：文档几乎为零
- 原作者不可达
- 需要逐步重新理解项目

**顺序**：

1. **代码考古**：从入口逆向梳理调用关系，画出当前实际架构（不是理想架构）。
2. **写一份"as-is" ARCHITECTURE.md**，明确标注 `（推断）` 与 `（已确认）`。
3. **找 1 名了解业务的人**做半小时同步，确认推断。
4. 把 TODO/FIXME/HACK 整理成风险列表。
5. 建立最小 CI（lint + 单元，跑得动就行）。
6. 之后参考路径 B。

### 路径 D：必须重构

**门槛极高**。同时满足：

- 现状已阻碍业务推进（明确证据）
- 有用户/owner 显式授权
- 有目标架构文档（`ARCHITECTURE.md` 写明 to-be，不只是吐槽 as-is）
- 有迁移计划（按 vertical slice 推进，不大爆炸）
- 有验证手段（测试或 smoke 覆盖被改动区域）

**否则一律退回路径 A/B/C。**

---

## 4. 文档补齐顺序（路径 A/B/C 共用）

补文档时按这个顺序，**先有最小可读版本，再迭代**：

1. `README.md`（如缺）：项目是什么 + 谁用 + 怎么跑 + 在哪里看下一步。
2. `ARCHITECTURE.md`：当前架构事实 + 真相源 + 主要边界。as-is 优先。
3. `BRANCHING.md`：从 git log 反推现状，不发明新规则；新规则需团队同意。
4. `AGENTS.md`：AI 协作硬约束（先读哪些文档、不能动什么）。
5. `CONSTITUTION.md`：把现状中**已存在的红线**明文化（如"不能直连 prod 库"、"prompt 必须从文件加载"），不发明新红线。
6. `DEVELOPMENT.md`：怎么本地跑 + 怎么测试 + 怎么提交 + DoD。
7. `docs/governance/folder-declaration-v0.md`：顶层目录职责（基于 §1.0 自动识别 + §1.2 人工确认）。
8. `docs/governance/changelog.md`：从今天起记。
9. `docs/decisions/ADR-0001-record-architecture-decisions.md`：宣告"从今天起新决策走 ADR"，并补 1–2 份回溯式 ADR 记录现状中"未来要回溯"的关键决策。
10. `docs/memory-bank/`（agent 协作项目）：把 §1.0 自动识别 + §2 现状报告整理成 `brief.md` / `tech-context.md`；`patterns.md` 留待逐步提炼；`active-context.md` 写"刚接手，下一步：X"。
11. `docs/prompts/`（agent 协作项目）：从基线模板挑 `handover-audit` / `pre-pr` / `update-active-context` 起步。
12. `DESIGN.md`（UI 类）：抽取现有组件 + token 现状。
13. `docs/requirements/`：找业务负责人补一份当前 baseline 需求。
14. `docs/design/active/`、`backlog/`、`done/`：建立 design doc lifecycle 目录；之后每个新 feature 一份 design doc。

### 4.1 Legacy / pre-vibecoding 文档迁移

适用于旧项目已经有 PRD、设计文档或重构计划，但没有统一 `docs/design/{backlog,active,done}`、ADR、Memory Bank 的情况。

迁移原则：

1. **先索引，后移动**：先在 README 或 `docs/README.md` 建文档索引，标注每份文档的当前状态。
2. **先 as-is，后 to-be**：旧文档反映历史，不要直接改成理想状态。
3. **只迁移仍有效的文档**：过期文档保留历史标签，不要混入 active。
4. **抽取，不复制**：架构决策从 refact_plans/design docs 中抽取成 ADR，避免双份维护。
5. **移动要可回溯**：文件移动或重命名必须在 changelog 记录旧路径 → 新路径。

映射表：

| 旧形态 | 处理 |
|---|---|
| `PRD.md` / `PRD/prd.md` | 保留原文件或复制为 `docs/requirements/requirements-v0.0.1.md`；README 指向唯一入口 |
| `docs/refact_plans/*.md` | 仍在执行的移到 `docs/design/active/`；已完成的移到 `done/`；架构选择抽 ADR |
| `design_doc-v*.md` | 按状态进入 backlog/active/done；无法判断状态则留原位并标 `needs owner confirmation` |
| 多份 architecture 文档 | 选一份 `ARCHITECTURE.md` 做 canonical，其余标专题/历史并交叉引用 |
| 零散 prompt 文档 | 操作手册进 `docs/prompts/`；运行时 prompt 进 `prompts/` 或 prompt registry |
| sandbox/output/temp 入仓 | 先更新 `.gitignore`，再判断是否保留脱敏 fixture |

停止条件：

- 新成员知道“当前有效文档”是哪几份。
- active design docs 只包含当前正在做的事项。
- 至少一份 ADR 记录“从今天起如何记录架构决策”。
- 旧文档没有被删除到不可追溯。

---

## 5. 接手第一周的"做与不做"

**做**：

- 跑通本地环境，能 build / start / test。
- 读 README + 入口文件 + 路由表 + 数据模型。
- 列出 git log 最近 50 个 commit 的主题分布。
- 看最近 5 个已合并 PR 的风格。
- 找业务负责人 / 原维护者一次同步（30 分钟）。
- 输出现状报告。

**不做**：

- 不发 PR 改架构。
- 不重命名顶层目录。
- 不升级主框架版本。
- 不"顺手"重构看着不顺眼的代码。
- 不引入新工具（除非补观测性最小集）。

---

## 6. 接手项目场景的 工程路由输出（与 SKILL.md 一致）

接手项目的 review 场景，使用统一 工程路由模板：

```text
工程路由: Inherit | 接手已有项目 | Review/Governance
当前阶段: I 接手盘点
项目形态: <推断结果>
缺失内容: <按 §1 checklist 列>
下一步 3 个动作: <来自 §2 报告或 §3 路径>
要创建/更新的文件: <按 §4 顺序>
验证门禁: <最小 smoke / 现有 CI / 本地启动是否可行>
停止条件: <现状报告完成且路径选定 / 文档骨架就位 / smoke 覆盖核心路径>
```

---

## 7. 常见接手反模式

- **第一周就提"重构 PR"**：用户/团队对你毫无信任，必被打回。
- **照搬偏好**：把上家公司的目录结构/工具链强行套用。
- **盲补文档**：在不理解代码的情况下写 ARCHITECTURE.md，写出来的是错的。
- **批判式 review**：第一份产出是"一长串问题列表"，没有任何建设性路径。
- **跳过业务同步**：仅看代码不找业务负责人，决策建立在错误假设上。
- **删 TODO/FIXME**：那些标注往往是历史伤疤，删除前先理解。
- **修改分支策略**：改 protected branch 规则要先得到团队共识。
- **大版本升级**：第一周升级主框架/Node/Python 大版本。
- **引入新工具**：观测性外的新工具（编辑器、linter、formatter 大改）。
- **把现状当问题**：没看清现状的合理性，把约定当 bug。

---

## 8. 与其他 references 的关系

- 现状报告显示项目处于 **正常开发阶段** → 接回 `stage-playbook.md` 对应阶段。
- 现状报告显示需要**补关键架构决策** → 用 `architecture-cases.md` 校准 as-is，不强制改；关键回溯决策落到 `docs/decisions/` ADR。
- 现状报告显示**文档缺失** → 用 `spec-templates.md` 路由到具体模板补，但内容必须反映现状。
- 现状报告显示**旧式文档很多但状态不清** → 先走 §4.1 legacy 迁移，不要直接套新目录。
- 命中 RPA / OCR / 视觉 / LLM / 浏览器自动化 / POC 场景 → 读取 `scenario-playbooks.md` 校准最小切片和验证门禁。
- 现状报告显示**需要 PR/发布** → 用 `checklists.md` 的 PR Readiness。
- 现状报告显示团队**会用 AI agent 协作** → 用 `memory-bank-guide.md` 与 `prompts-guide.md` 初始化 `docs/memory-bank/` 与 `docs/prompts/`。
- 接手 AI 项目 → 额外用 `architecture-cases-ai.md` 校准 AI 维度现状。
