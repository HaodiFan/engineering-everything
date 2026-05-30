# 阶段 Playbook

用于诊断当前软件开发阶段，并决定下一步动作。

阶段 I（接手盘点）见 `inheriting-projects.md`（含 §1.0 自动识别 + §1.1–1.5 人工盘点）。本文件覆盖 Stage P 与 Stage 0–9。

> 跨阶段产物索引：`CONSTITUTION.md`（Stage 3 起草、长期维护）；ADR `docs/decisions/ADR-NNNN-*.md`（Stage 3 起步、每个关键决策）；Memory Bank `docs/memory-bank/`（Stage 4 初始化、Stage 6/8 持续更新）；Prompts `docs/prompts/`（Stage 4 初始化）；Design doc lifecycle `docs/design/{backlog,active,done}/`（Stage 4 建立、Stage 5–8 流转）；Implementation Plan（Stage 5，可写入 design doc Milestones 或单独 `docs/plans/`）。详见 `spec-templates.md`、`memory-bank-guide.md`、`prompts-guide.md`、`execution-pipeline.md`。

---

## Stage P：POC / Spike

典型信号：

- 用户说 POC、spike、demo、sandbox、先试试、验证可行性、一次性脚本。
- 生命周期短、单人推进、未承诺生产化。

下一步：

- 读取 `scenario-playbooks.md` 的「POC / Spike 轻量模式」。
- 明确 POC 只回答一个问题：可行性、质量、性能、成本或业务价值。
- 只要求轻量文件集：`README.md`、依赖声明、`.gitignore`、`docs/spike-note.md`。
- 先定义升级触发条件：多人接手、真实客户数据、持续运行、产品化、存储/权限/API/后台任务。

停止条件：

- POC 有结论：可行 / 不可行 / 需二次验证。
- 有证据：样本、指标、截图、失败案例。
- 明确废弃、归档或升级为正式项目。

---

## Stage 0：想法

典型信号：

- 用户只有产品想法，没有 repo、spec 或技术形态。
- 请求类似"我想做 X"、"这个项目怎么开始"。

下一步：

- 写一句话定义：用户、系统类型、核心能力、核心问题、P0 非目标。
- 用 `psps-framework.md` 抽取 Persona / Scenario / Pain / Solution Surface，避免从一句意图直接跳到功能清单。
- 给出形态候选（不超过 3 种），并说明各自代价。**不要立刻拍板**。
- 提示用户：业务需求文档需由用户提供，agent 仅协助结构化。

产物格式：

```text
<Project> 是一个面向 <user> 的 <system type>，
通过 <core capability> 解决 <core problem>，
P0 不做 <non-goal>。
```

停止条件：

- 已选定一个可逆的项目形态候选范围，并明确 P0 非目标。

---

## Stage 1：需求澄清

> 关键约束：业务需求文档由**用户提供**，agent 不替编。

典型信号：

- 用户、权限、流程、数据来源、平台或成功标准不清楚。
- 用户提供了零散材料但没有结构化需求。

下一步：

- **请求用户提供需求文档**（参考 `spec-templates.md` → `templates-specs.md` 的 Requirements Doc 模板）。
- 用户已给材料的，按模板抽取并回填，缺失项标 `TODO（用户补充）`。
- 用户说不清楚时，先按 `psps-framework.md` 主动还原 PSPS 初稿：谁决策/执行/验收、什么场景、卡在哪里、需要什么系统表面。
- 用 `checklists.md` 的「需求文档完备性 checklist」校验是否够开工。
- 把未知点转成 open questions，按"agent 可推断 / 必须用户回答"分类。

最小产物：

- `Background`、`Goals`、`Scope`、`Non-goals`、`Assumptions`、`Open questions`、`Success metrics`

停止条件：

- 需求完备性 checklist 全通过，或缺口已被用户明确认可为"后置"。
- 下一份 design doc 可以在不编造产品意图的前提下写出来。

---

## Stage 2：Spec

典型信号：

- 用户要求 PRD、design doc、spec。
- 功能会改变 workflow、state、data、API、UI pattern 或 integration。

下一步：

- 创建或更新一份聚焦的 design doc。
- Design doc 必须包含 PSPS 推导出的系统表面：数据模型、页面/视图、流程/SOP、自动化、指标/报表、权限/审计。
- 必须包含验收标准和回滚点。
- 不写"大而全总集"，除非用户明确要项目 baseline。
- UI 类 design doc 必须关联或先建 `DESIGN.md` 与 layout spec。

停止条件：

- 开发者能实现最小切片，不需要猜行为。

---

## Stage 3：架构

> 这是 Stage 0–4 真实顺序里最关键的一环。先选架构，再脚手架。

典型信号：

- 需要选择技术栈、repo 形态、runtime 边界、数据归属、模块边界或集成模式。
- 用户问"怎么拆"、"放哪里"、"选什么结构"。

下一步（建议顺序）：

1. **形态决策**：用 `architecture-cases.md` 的 4 步法确定项目形态。
2. **关键架构决策清单**：直接读 master checklist，**不要再跳两个文件拼装**：
   - 通用 21 项：`architecture-cases.md` 文末「综合决策清单（Stage 3 落地用）」。
   - AI 增补 15 项（仅 AI / Agent 项目）：`architecture-cases-ai.md` 文末「AI Stage 3 决策清单」。
   - 两份清单的结论统一写进 `ARCHITECTURE.md` 的 Technical Baseline 表。每项落地见对应章节（§0–§20 / §A–§K）。
3. **真相源声明**：每个领域唯一 owning layer。外部平台默认是 integration，不是真相源，除非文档明确说明。
4. **分支规范前置**：在脚手架之前，先定 `BRANCHING.md`（见 `spec-templates.md` → `templates-core.md`）。这是 trunk-based / git-flow / GitHub flow 的明确选择，不留模糊。
5. **红线声明**：起草 `CONSTITUTION.md` v0.1（见 `spec-templates.md` → `templates-governance.md`），把"绝不能违反"的规则明文化（鉴权边界、真相源、runtime data、AI 调用统一 client 等）。**只放红线，不放偏好**。
6. **关键决策走 ADR**：每个有后果、未来要回溯的决策（选库、选数据库、选 LLM provider 调用模式、选 monorepo vs polyrepo），写一份 `docs/decisions/ADR-NNNN-*.md`（见 `spec-templates.md` → `templates-governance.md`）。决策结论同步进 `ARCHITECTURE.md` Technical Baseline。
7. **更新 `ARCHITECTURE.md`** 或等价全局真相源，记录所有决策与代价，并交叉引用 ADR。

规则：

- router/controller 只做协议适配，不承载核心领域逻辑。
- runtime data 放 repo 外。
- 每个架构决策必须写明：选了什么、为什么、付出什么代价、退出成本多高。**详细 trade-off 写 ADR，结论写 ARCHITECTURE.md**。

停止条件：

- 每个主要职责都有唯一 owning layer 或目录。
- `ARCHITECTURE.md` + `BRANCHING.md` + `CONSTITUTION.md` + 关键 ADR 可独立解释整套技术决策。

---

## Stage 4：脚手架

典型信号：

- 空 repo、新模块、首次提交。
- 用户要求 starter structure 或 bootstrap plan。

真实推进顺序（与一句话需求 → 上线之间最易出错的一段）：

1. **初始化项目文件夹体系**（按 `project-blueprints.md` 的 starter tree）。
2. **落地分支规范**：`BRANCHING.md` 必须在第一个非 README commit 之前生效。
3. **落地架构 + 红线 + 关键 ADR**：`ARCHITECTURE.md` 反映 Stage 3 全部决策；`CONSTITUTION.md` v0.1 落地（红线）；起步 ADR（至少 `ADR-0001` 宣告用 ADR 记录决策）。
4. **业务目标对齐**：把用户提供的需求文档归档到 `docs/requirements/`，并交叉引用 design doc。建立 `docs/design/{backlog,active,done}/` 三个生命周期目录，把 bootstrap design doc 放到 `active/`。
5. **页面布局先行**（UI 类项目）：根据需求文档 + `DESIGN.md` 写 layout spec（md 形式，见 `spec-templates.md` → `templates-specs.md`），**先于代码与 Figma**。
6. **组件选择**：对照 `DESIGN.md` 的组件清单与交互模式选定每个区域用什么组件。新组件必须先进 `DESIGN.md`。
7. **AI 协作骨架（agent 协作项目）**：初始化 `docs/memory-bank/` 四件套（`brief.md` / `tech-context.md` / `patterns.md` / `active-context.md`，见 `memory-bank-guide.md`）；`docs/prompts/` 至少落地基线 `scaffold-new-project` / `pre-pr` / `update-active-context`（见 `prompts-guide.md`）。
8. **AGENTS.md 更新**：明示 agent 开工先读 `memory-bank/active-context.md` + `CONSTITUTION.md`，会话末更新 `active-context.md`。

首次提交规则：

- 首次提交只放 skeleton、docs、config templates、最小可运行 hello path。
- 不把正式 feature 实现混进 bootstrap commit，除非不可避免。

停止条件：

- 新成员可以 clone、install、run，并找到下一份 design doc。
- `BRANCHING.md`、`ARCHITECTURE.md`、`CONSTITUTION.md`、`DESIGN.md`（UI 类）、`AGENTS.md` 全部存在。
- agent 协作项目：`docs/memory-bank/` 四件套与 `docs/prompts/README.md` 已就位。
- `docs/decisions/ADR-0001-*.md` 存在，作为后续 ADR 编号锚点。

---

## Stage 5：Feature 规划

典型信号：

- 功能目标明确，但不知道怎么拆。
- 用户要求拆解、估算、多人/多 agent 并行。

下一步：

- 确认关联 design doc。
- 确认 design doc 中的 PSPS 已能解释本 feature 的用户、场景、痛点和 Solution Surface；缺失则退回 Stage 1/2。
- 读取 `execution-pipeline.md` §2 判断 checkout/worktree；读取 `agent-operating-standards.md` 检查 source-driven、change size 和常见 rationalization；读取 §3 输出 implementation plan。
- 拆成能产生可观察行为的 vertical slices，并标出每个 slice 的 validation gate。
- 标出影响目录、数据模型变化、API 变化、UI 变化、测试、文档和 review roles。
- 多步 feature 没有 plan 不进入 Stage 6；单点小改、POC、事故救火可走例外，但要说明原因。

产物格式：

```text
Milestone 1: schema/API skeleton
Milestone 2: core use case
Milestone 3: UI or CLI path
Milestone 4: tests and docs
```

停止条件：

- 每个 milestone 都有清晰 validation gate。
- 命中的 Review Pipeline roles 已标出（Product / Eng / Design / DX / Code / QA / Security / Release）。

---

## Stage 6：实现

典型信号：

- 用户要求 build、fix、add、wire、migrate、implement。

下一步：

- 编辑前先检查 repo，并按 `execution-pipeline.md` §2 判断是在当前 checkout 直接开发，还是新建 worktree；不得擅自 stash/revert 用户改动。
- 命中新依赖、外部 API、平台规则、框架升级、鉴权/支付/合规时，先按 `agent-operating-standards.md` 做 source-driven check。
- 读取 canonical docs（含 `CONSTITUTION.md`、`docs/memory-bank/active-context.md`、`docs/memory-bank/patterns.md`）和现有实现模式。
- 多步 feature 先读取 implementation plan；没有 plan 时退回 Stage 5。
- 按 `execution-pipeline.md` 的 slice 执行，完成一个可观察行为再进入下一个。
- 保持在已声明架构边界内 + 不触 `CONSTITUTION.md` 红线。
- 如需偏离 spec，先更新 spec。
- 触发红线 → 立刻停下，提示用户三种路径（改方案规避 / 提议放宽红线 / 申请临时豁免），由 owner 决策。

收尾必须包含：

- 变更文件
- 已运行验证
- 未运行检查及原因
- 剩余风险
- **更新 `docs/memory-bank/active-context.md`**（agent 协作项目）：写已完成 / 进行中 / 下一步 / 给下一会话留言。
- **检查是否要 capture lesson**：本轮对话有没有触发捕获信号（用户说"不对/应该是/错了/我之前是/不要 X 要 Y"）？有 → 用 `prompts-guide.md` 的 capture-lesson 流程追加到 `references/lessons.md`。详见 SKILL.md「Knowhow 沉淀规则」。

停止条件：

- 代码已实现，并至少完成最小验证，或明确说明验证被什么阻塞。
- `active-context.md` 已更新（agent 协作项目）。
- 触发的捕获信号已经处理（捕获 / 用户拒绝 / 判定为单纯澄清）。

---

## Stage 7：验证

典型信号：

- 用户要求 tests、QA、hardening、e2e、prelaunch、smoke test、"是否 ready"。

下一步：

- 把变更映射到检查：typecheck、unit、integration、migration、e2e、visual、smoke。
- 先跑最窄可靠检查。
- 按 `execution-pipeline.md` §4 选择 Review Pipeline roles；测试默认优先后端/API/service 自测。除非用户要求、任务本身是浏览器/RPA能力、或问题只能在真实浏览器复现，不主动跑浏览器模拟。
- bug fix 优先补 regression test。
- 记录验证缺口。

停止条件：

- 风险列表已关闭，或清楚记录在 PR/文档里。

---

## Stage 8：PR / 发布

典型信号：

- 用户要求 commit、push、open PR、ship、release、deploy。

下一步：

- 确保 design doc 已关联（位于 `docs/design/active/`）。
- 对照 `execution-pipeline.md` 的 Review Gate、Validation Gate、Learn Gate 收口。
- 重要变更已更新 docs/changelog。
- `git diff --check` 通过。
- `CONSTITUTION.md` 红线 0 触发（或已走豁免流程）。
- 触发架构维度变更 → 同步 `docs/decisions/` 增加或更新 ADR。
- feature 完成 → 把 design doc 从 `active/` 移到 `done/`，回填 `Validation Results`。
- 更新 `docs/memory-bank/active-context.md`（agent 协作项目）：标 PR 状态。
- 总结 why、what、risk、validation。
- **PR 前最后一道 knowhow 检查**：本次开发周期内累计的 lesson 候选是否都已写入 `references/lessons.md`？同主题 lesson ≥ 2 条的是否要走 promote-pattern？详见 SKILL.md「Knowhow 沉淀规则」与 `prompts-guide.md` 的 promote-pattern。

PR body：

```md
## Why
## What Changed
## Linked Spec
## Validation
## Risks / Rollback
## Docs Updated
```

停止条件：

- Reviewer 不需要重建上下文，就能理解意图、行为变化和风险。

---

## Stage 9：维护 / 重构

典型信号：

- 用户要求 cleanup、modularize、rename、reduce debt、improve structure、refactor。

下一步：

- 区分行为保持型 refactor 和功能变更。
- 读取 `refactoring-rules.md`，先识别明确坏味道，再选择对应重构手法。
- 移动代码前先识别或补充测试。
- 若边界变化，更新 folder declaration 或 architecture docs；架构方向调整需补 ADR。
- 重构不得绕开 `CONSTITUTION.md` 红线（不能借"清理"之名移除 audit、绕鉴权、合并 truth source 等）。
- 重构发现"项目特定写法"或"已多次踩的坑" → 沉淀到 `docs/memory-bank/patterns.md`（见 `memory-bank-guide.md`）。
- 重构发现的"跨项目可复用纠偏"（不是项目特定的） → 沉淀到 skill 级 `references/lessons.md`（L1），多次命中后 promote 到 `references/patterns-skill.md`（L2）。
- 没有目标架构文档时，避免大范围重写。

停止条件：

- 行为保持，边界更清晰，并有验证证明 touched slice 没有回归。
- 涉及边界 / 架构 / 红线变化时，对应 ADR / ARCHITECTURE / CONSTITUTION 已更新。
