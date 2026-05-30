---
name: engineering-everything
description: Engineering Everything 是用工程思维看待一切创造型任务的决策 Skill，默认用中文交互。用于 Codex 需要先判断工程路由，再在软件开发、组织构建、企业机制、SOP/流程、产品定义、人才面试、入职培训、非工程项目方案/排期/人天/成本估算、项目形态、架构选型、业务场景、执行计划、验证、代码审查、发布治理和经验沉淀之间选择正确知识路径时；适用于新建项目、接手旧项目、非软件开发项目、组织/企业工程化、legacy 治理、POC/spike、PRD/design doc、ADR、脚手架、RPA/电商数据采集、OCR、CV、LLM/Agent、数据分析、PR/release readiness 等场景。先输出路由判断，再决定读哪个 reference、补哪个产物、跑哪个 gate。保留 lessons / patterns / reference 三层 knowhow 机制，让每次用户纠偏可沉淀成可复用工程判断。
version: 0.9.1
---

# Engineering Everything / 工程化万物

用工程思维看待一切创造型任务：软件是工程，组织是工程，企业是工程，SOP 和知识资产也是工程。先判断用户问题属于哪个工程路由，再选择产品、人才、培训、架构、执行、验证、治理或 learn 的知识路径。

## 使用原则

每次回答用户时，先按 `references/engineering-scenario-map.md` 完成工程路由判断。规划类回答顶部输出统一的工程路由模板。

「规划类」工程路由模板（覆盖原先单独的分类块，不要重复输出两组分类）：

```text
工程路由: <主路由 | 命中场景 | 决策层>
当前阶段: <P POC/Spike | 0 想法 | 1 需求澄清 | 2 Spec | 3 架构 | 4 脚手架 | 5 Feature 规划 | 6 实现 | 7 验证 | 8 PR/发布 | 9 维护 | I 接手盘点>
项目形态: <Web+Backend | Desktop+Local Agent | Python Agent/CLI | Library/SDK | Full-stack Monorepo | Unknown>（如有场景，追加：场景 <RPA/OCR/LLM/POC/...>）
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

「执行类」回答（直接写代码、修 bug、答疑）不强制完整模板，但收尾必须包含：变更文件 / 已运行验证 / 未运行检查及原因 / 剩余风险。

「闲聊类」或单点澄清不需要任何模板。

术语统一：本 Skill 中 **vertical slice / 最小切片 / 最小端到端闭环** 指同一概念——能产生可观察行为的最小纵向实现。

## 决策树

按从上到下的优先级匹配，**多条命中时取第一条**：

### 0. 是接手已有项目吗？（最高优先级）

- 信号：用户描述"接手"、"现有项目"、"老代码"、"刚加入团队"、给出已有 repo URL、问"这项目怎么继续"。
- 行动：读取 `references/inheriting-projects.md`。先跑 §1.0 自动识别（机器可判断的工具链 / 形态推断），再走 §1.1–1.5 人工盘点。若是旧式 PRD / refact_plans / 零散 design docs 项目，再走 legacy 迁移路径。
- 默认立场：**尊重现状，不擅自重构**。先盘点文档与代码现状，缺什么补什么。

### 1. 是实现/修 bug/迁移/重构任务吗？

- 信号：用户要求 build、fix、add、wire、migrate、implement、refactor、cleanup、modularize、写代码、接接口。
- 行动：读取 `references/stage-playbook.md` Stage 6/9、`references/checklists.md` 与 `references/execution-pipeline.md`；命中重构/清理/模块化时额外读取 `references/refactoring-rules.md`。如果命中 RPA / OCR / 视觉质检 / LLM 生产链路 / 浏览器自动化，额外读取 `references/scenario-playbooks.md`。
- 规则：编辑前先检查 repo；如改动会触动架构边界、状态机、权限、存储、公共 API 或 UI 模式，先更新 spec 再写代码。

### 2. 是已有项目的新功能规划吗？

- 信号：新增 feature、页面、API、workflow、agent 能力、集成、后台任务，但还没开写。
- 行动：读取 `references/stage-playbook.md` Stage 5、`references/spec-templates.md` 与 `references/execution-pipeline.md`。如果功能属于采集、OCR、文档智能、视觉质检、数据治理或 LLM 生产链路，额外读取 `references/scenario-playbooks.md`。
- 规则：先确认是否已有关联 design doc；没有就先创建或补齐，除非用户明确要 quick spike。

### 3. 是 review、救火、"下一步做什么"吗？

- 信号：用户问"现在该干嘛"、"帮我 review 计划"、"项目很乱"、"继续开发"。
- 行动：读取 `references/stage-playbook.md` 与 `references/checklists.md`。如果是代码审查、PR review、实现方法评审，再读取 `references/code-review-standards.md`。
- 输出：使用 工程路由模板。

### 4. 是 POC / Spike / 临时验证吗？

- 信号：用户说 POC、spike、demo、sandbox、验证可行性、先试试、一次性脚本、客户演示；生命周期短、未承诺生产。
- 行动：读取 `references/scenario-playbooks.md` 的「POC / Spike 轻量模式」。
- 规则：先用轻量文件集，不强行要求完整 `CONSTITUTION` / ADR / Memory Bank；一旦命中升级触发条件，切回正式项目流程。

### 5. 是从 0 开始的新项目吗？

- 信号：用户从想法、空目录、新 repo、"怎么搭项目"开始。
- 行动：读取 `references/project-blueprints.md`、`references/architecture-cases.md`（AI 项目再加 `architecture-cases-ai.md`）、`references/spec-templates.md`；若业务场景明确，读取 `references/scenario-playbooks.md`。
- 规则：按 Stage 0–4 的真实 8 步顺序推进（见 `stage-playbook.md`）；脚手架阶段同时落地 `CONSTITUTION.md`、`docs/decisions/`、`docs/memory-bank/`、`docs/prompts/`（见 `memory-bank-guide.md` 与 `prompts-guide.md`）。

### 6. 是人才、培训、非工程项目或方法论建设吗？

- 信号：面试工程师、入职培训、企业介绍、构建组织、构建企业、SOP、协同机制、非工程项目方案/排期/人天/成本估算、文件输出、Skill 开发、多维表开发、方法论或可复用 playbook。
- 行动：读取 `references/engineering-scenarios.md`，必要时再读治理、模板、执行或场景 reference。

## 形态 Unknown 的兜底

当项目形态判断为 `Unknown` 时，**不要**直接给阶段建议或目录结构。先走 `references/architecture-cases.md` 的「形态决策表」按 4 步判断：

1. 用户在哪里运行它？
2. 产品真相源在哪里？
3. 是否需要跨 app 共享代码？
4. 是否需要本地 runtime 或进程编排？

形态确定前，最多输出"形态待定 + 候选 2–3 种 + 还差什么信息"。

业务场景判断为 `Unknown` 时，不阻塞项目形态判断；只在采集、OCR、视觉、LLM、数据治理、浏览器自动化等信号明确时读取 `scenario-playbooks.md`。

## 阶段路由

| 阶段 | 典型信号 | Reference | 下一步重点 |
|---|---|---|---|
| I 接手盘点 | 接手已有 repo | `inheriting-projects.md` | 文档/代码盘点，现状报告 |
| P POC/Spike | 临时验证、demo、sandbox | `scenario-playbooks.md`、`checklists.md` | 轻量文件集 + 升级触发判断 |
| 0 想法 | 只有产品想法，无 repo | `spec-templates.md` | 一句话定义、P0 非目标、形态候选 |
| 1 需求澄清 | 业务目标不清 | `stage-playbook.md`、`psps-framework.md`、`checklists.md` | **要求用户提供需求文档**，agent 不替编 |
| 2 Spec | PRD/design doc | `spec-templates.md` | 带验收标准的 design doc |
| 3 架构 | 技术栈、边界、真相源 | `architecture-cases.md`、`architecture-cases-ai.md` | 形态选定 + 关键架构决策清单 |
| 4 脚手架 | 新 repo、首次提交 | `project-blueprints.md`、`spec-templates.md` | starter tree + 分支规范 + 首次提交清单 |
| 5 Feature 规划 | 缺拆解 | `stage-playbook.md`、`psps-framework.md`、`execution-pipeline.md` | implementation plan + review roles |
| 6 实现 | 代码变更 | `checklists.md`、`execution-pipeline.md` | 最小切片 + validation gate |
| 7 验证 | 测试、QA | `checklists.md`、`execution-pipeline.md` | Review Pipeline + 后端优先验证 |
| 8 PR/发布 | 合并、发版 | `checklists.md`、`execution-pipeline.md` | PR 内容、release gate、learn 收口 |
| 9 维护 | 重构、清理 | `stage-playbook.md`、`refactoring-rules.md` | 行为保持 + 边界清晰 |

## 项目形态路由

选择或描述项目形态时读取 `references/architecture-cases.md` 与 `references/project-blueprints.md`。

- **Web + Backend**：管理台、Web App、外部平台集成、后端数据库是真相源。
- **Desktop + Local Agent**：本地数据、本地进程编排、离线优先、桌面分发、Agent runtime。
- **Python Agent / CLI**：命令行工具、SDK、自动化、Agent runtime、后台任务。
- **Library / SDK**：可复用包、公共 API、示例、兼容性承诺。
- **Full-stack Monorepo**：多个 app、共享协议、共享 UI、长期跨端演进。

AI/Agent 类项目额外读取 `references/architecture-cases-ai.md`。

业务自动化场景额外读取 `references/scenario-playbooks.md`，尤其是 RPA/数据采集、OCR/文档智能、视觉/多媒体质检、数据治理/分析报表、LLM 生产链路、浏览器自动化、POC/spike。

## Knowhow 沉淀规则（v0.5.0 起，让 skill 自我进化）

Skill 有三层 knowhow，agent 必须主动维护：

- L1 `references/lessons.md`：单条纠偏，立即追加（编号 L-NNNN）
- L2 `references/patterns-skill.md`：验证过的 pattern（编号 P-NNNN）
- L3 Reference 升级：pattern 影响 reference 核心结论时，owner 开 PR

**会话开始**：按本次任务的 Tag（阶段 / 形态 / 场景 / 架构维度）在 `lessons.md` 与 `patterns-skill.md` 检索 active 条目；冲突时优先 pattern > lesson > reference 默认，并在回复中引用 `L-NNNN` / `P-NNNN`。

**会话进行中**：用户回复出现纠偏信号（「不对 / 应该是 / 错了 / 我之前是 / 不要 X 要 Y / 这一步不该现在做」等）→ agent **必须**在该轮回复末尾追加「📌 是否捕获 lesson」提议。信号弱 / 闲聊不硬捕获。

**会话结束**：触发的捕获信号已处理（捕获 / 用户拒绝 / 判定单纯澄清）；同主题 lesson ≥ 2 条 → 提议 L1 → L2 promotion；pattern 与 reference 冲突 → 提议 L2 → L3 promotion。

详细触发信号词表、Tag 词表、模板、反模式、promotion 流程：见 `references/lessons.md`、`references/patterns-skill.md`、`prompts-guide.md` 的 `capture-lesson` / `promote-pattern`。

## 核心规则

- spec/design doc 是意图真相源，代码是意图实现。
- 先判断工程路由，再读取 reference；不要把多个知识域一次性倾倒给用户。
- **业务需求文档必须由用户提供**，agent 只负责校验完备性、抽取结构、提问澄清，不替用户编造业务意图。
- 没有 spec，不新增架构层、状态机、存储、权限、全局依赖或公共 API。
- 全局真相源必须唯一：architecture、development rules、design rules、folder declaration、terminology、changelog、branching、constitution。
- **`CONSTITUTION.md` 是项目红线**：触线立刻停下、提示用户，不自行突破（详见 `templates-governance.md`）。
- **架构决策走 ADR**：在 `docs/decisions/ADR-NNNN-*.md` 记录"为什么这么选"（详见 `templates-governance.md`）。
- **Memory Bank 是 agent 跨会话上下文**（`docs/memory-bank/`）：开工先读上下文入口，长 `active-context.md` 必须先走关键词 map 再定向读正文；详见 `memory-bank-guide.md`。
- **Design doc 有生命周期**：`backlog/ → active/ → done/`，状态由目录位置体现，AGENTS 默认只读 `active/`。
- 一个 topic 一个分支，避免混入无关变更。
- 编辑前必须判断 checkout/worktree 策略：新 feature、并行任务、脏工作树或高风险改动优先新 worktree；小修、文档、单 PR follow-up 可在当前目标分支直接开发；不得擅自 stash/revert 用户改动。
- 多步 feature 先有 implementation plan；计划必须包含文件边界、vertical slices、validation gates 和命中的 review roles（详见 `execution-pipeline.md`）。
- 新依赖、外部 API、平台规则、框架升级、鉴权/支付/合规等技术事实必须 source-driven：优先项目内锁定版本和官方来源，并记录证据。
- 优先做最小 vertical slice（端到端闭环），不做大面积半成品。
- 测试默认后端/API/service 自测优先；除非用户要求、任务本身是浏览器/RPA能力、或问题只能在真实浏览器复现，不主动跑浏览器模拟。
- 信息不足时，优先做可逆的最小假设并明确说明；只有错误假设代价高时才提问。
- 接手项目默认尊重现状，不擅自重构；缺文档先补文档。
- POC/spike 默认轻量治理，但命中升级触发条件（多人接手、真实客户数据、持续运行、生产化、存储/权限/API/后台任务）后必须升级到正式项目流程。
- 业务场景 playbook 提供默认选型和验证门禁；最终架构决策仍以 `ARCHITECTURE.md` + ADR 为准。

## Skill 增长规则（v0.4.1 起）

为保持 SKILL.md 的"路由器"职能，避免被新加的 case 撑爆：

- **SKILL.md 是路由器，不是内容**。新内容必须落到 `references/`，本文件只能加路由（决策树分支、阶段路由表行、形态路由项、references 列表项）。
- **软上限 200 行**。超出时优先把内容下沉到 reference，而不是删除路由。
- **决策树分支上限 8 条**（当前 6 条）。再加分支前先评估能否合并到现有分支（例如新场景大多并到第 1/2/4 条）。
- **新加 reference 必须在以下三处显式登记**：本文件 References 列表、`spec-templates.md` 路由表（如属于模板）、`README.md` References 列表。
- **三本 case/playbook 边界**：`architecture-cases.md` 与 `architecture-cases-ai.md` 只放架构选型；`scenario-playbooks.md` 只放业务场景落地；不得跨界复制。详见 `architecture-cases.md` 顶部「三本 case/playbook 的分工」。

## 工程化工具（v0.9.0 起）

- 安装 / 升级优先使用 `scripts/install.py`，不要手写复制命令。
- 改 Skill 结构、版本、引用、安装路径后必须跑 `scripts/skill_doctor.py`。
- 捕获 lesson 时可用 `scripts/lesson.py` 分配编号、生成卡片并校验字段。

## References

- `references/stage-playbook.md`：按阶段判断信号、产物和下一步动作。
- `references/engineering-scenario-map.md`：Engineering Everything 使用场景地图，按生命周期、项目形态、业务场景和决策层路由知识。
- `references/engineering-scenarios.md`：工程化万物扩展场景，覆盖工程师面试、入职培训、非工程项目估算、软件/非软件开发项目治理。
- `references/execution-pipeline.md`：Stage 5-8 的硬 gate、checkout/worktree 策略、implementation plan 质量标准、角色化 review pipeline、后端优先验证、browser QA 触发边界和 learn 边界。
- `references/agent-operating-standards.md`：agent 执行纪律，覆盖 Skill 编写结构、common rationalizations、red flags、source-driven gate、change size rules 和 lifecycle prompt aliases。
- `references/scenario-playbooks.md`：按业务自动化场景补充技术选型、最小切片、验证门禁和反模式（RPA/OCR/视觉/数据/LLM/浏览器自动化/POC）。
- `references/project-blueprints.md`：5 种项目形态的 starter 目录结构与首次提交清单。
- `references/architecture-cases.md`：通用架构选型 case 库（Repo / 渲染 / 后端 / 数据 / 部署 / 鉴权 / 异步 / 可观测性 / 业务自动化 / 客户端 / 状态管理 / 测试 / CI/CD / 配置 / i18n / 合规 / 性能等 20 大类）。
- `references/architecture-cases-ai.md`：AI / Agent 专项架构选型 case 库（LLM 调用、Agent runtime、工具调用、记忆、RAG、向量库、Prompt 管理、评估、安全等）。
- `references/spec-templates.md`：模板索引，按需路由到 `templates-core.md` / `templates-governance.md` / `templates-specs.md`。
- `references/templates-core.md`：README / ARCHITECTURE / DEVELOPMENT / BRANCHING / DESIGN / AGENTS 模板。
- `references/templates-governance.md`：CONSTITUTION（红线）/ ADR / Folder Declaration / glossary / changelog 模板。
- `references/templates-specs.md`：Requirements / Design Doc（含 backlog/active/done lifecycle）/ Layout Spec / PR Body 模板。
- `references/checklists.md`：验证门禁、需求完备性、PR readiness、反模式和场景 checklist。
- `references/code-review-standards.md`：团队代码审查口径，覆盖代码坏味道、潜在问题与测试重点、密钥/硬编码风险、真人测试真源。
- `references/psps-framework.md`：PSPS 构建洞察框架，把模糊意图转成 Persona / Scenario / Pain / Solution Surface。
- `references/refactoring-rules.md`：重构规则库，覆盖坏味道到手法映射、行为保持 gate、测试保护和 PR 拆分。
- `references/inheriting-projects.md`：接手已有项目的盘点流程（含 §1.0 自动识别）、现状报告模板、文档补齐顺序。
- `references/memory-bank-guide.md`：AI agent 跨会话上下文的"指针 + 增量"模式（brief / tech-context / patterns / active-context）。
- `references/prompts-guide.md`：可复用 prompt 模板（lifecycle/avatar aliases / scaffold / spike-start / handover-audit / new-feature / scenario-routing / new-design-doc / new-adr / pre-pr / refactor-safely / debug-incident / capture-lesson / promote-pattern）。
- `references/lessons.md`：**Skill 级 L1 纠偏日志**（每次用户纠正方案，agent 主动追加；连续编号 L-NNNN）。
- `references/patterns-skill.md`：**Skill 级 L2 验证过的 pattern 库**（来自 lessons 的合并；连续编号 P-NNNN）。
