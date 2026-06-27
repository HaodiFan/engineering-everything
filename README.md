# Engineering Everything（工程化万物）

> 用工程思维看待一切创造：软件是工程，组织是工程，企业是工程，SOP 也是工程。

AI agent 已经能很快写代码，也能很快写文档、做表格、生成方案。真正拖慢创造的，通常不是少写了几行代码或几页材料，而是：

- 需求还没问清楚，就开始搭架构。
- 技术栈看起来能用，但没有考虑数据源、权限、合规和退出成本。
- 老项目还没盘点，就开始重构。
- 组织机制、培训、SOP 和交付项目没有 owner、节奏、验收和复盘。
- PR 通过了测试，却没有人认真看行为风险、发布风险和回滚方案。
- agent 每次都很努力，但下次又忘了上次踩过的坑。

**Engineering Everything** 是一个用工程思维处理创造型任务的 Skill。它把 agent 从“会产出内容的助手”升级成“先判断结构、边界、风险和下一步的工程化分身”：用户一句话进来，先做场景路由，再决定该问需求、做架构、拆计划、写代码、搭组织机制、设计 SOP、跑验证、review、发布，还是沉淀经验。默认交互和文档语言是中文，但差异点是工程判断和场景路由。

这个项目公开名称、安装目录和触发名统一为 `engineering-everything` / `$engineering-everything`。

当前版本：`0.9.10`

## 你为什么需要它

空白 prompt 很快，但真实项目不止是 prompt。

比如你说：

> 我要做一个电商管理系统。

普通 agent 可能直接开始列页面、表结构和接口。Engineering Everything 会先停下来判断：

- 你做的是淘宝系、京东、拼多多、抖音，还是多平台？
- 数据来自公域页面、价格详情页、直播评论，还是商家管理后台？
- 公域数据是否涉及逆向、平台 ToS、风控和合规风险？
- 如果需要 RPA，是浏览器自动化、undetected ChromeDriver，还是手机 Appium？
- 第一版应该先闭环哪个最小业务切片？

这就是它的核心价值：**先把问题问对，再让 agent 写代码。**

## 适合谁

- **创业者 / 技术负责人**：想让 AI 加速创造，但不想牺牲工程判断。
- **独立开发者**：需要从想法、PRD、架构、脚手架一路走到发布。
- **正在引入 AI coding 的团队**：需要统一 planning、review、test、release gate。
- **自动化和数据项目开发者**：常做 RPA、电商数据、OCR、CV、LLM、数据分析。
- **接手旧项目的工程师**：需要先尊重现状，再决定怎么继续迭代。
- **构建组织和企业机制的人**：面试工程师、入职培训、协同机制、开发机制、SOP、非工程项目方案/排期/人天/成本估算。

## 快速开始

安装后，在新会话里这样问：

```text
$engineering-everything

我想做一个电商管理系统。先按 Engineering Everything 的方式判断工程路由，
再告诉我现在应该先问什么、选什么、写什么。
```

一个好的第一步输出应该像这样：

```text
工程路由: Scenario | 中国电商管理系统 | Product/Architecture
当前阶段: 0 想法
项目形态: Web+Backend（场景：电商平台数据 / 商家后台）
缺失内容: 平台范围、数据源类型、公域采集边界、商家后台权限、核心报表
下一步 3 个动作:
1. 先确认淘宝系 / 京东 / 拼多多 / 抖音哪些平台是 P0
2. 判断数据来自公域页面、直播评论、价格详情页，还是商家管理后台
3. 输出最小端到端切片和合规风险清单
验证门禁: 后端/API/service 自测优先；浏览器模拟只在 RPA/页面问题需要时运行
停止条件: 数据源和合规边界未确认前，不进入采集实现
```

重点不是模板本身，而是 agent 被强制先判断：这到底是产品问题、架构问题、执行问题、验证问题，还是合规边界问题。

## PSPS 构建洞察

Engineering Everything 会把模糊意图先转成 PSPS，再进入设计和实现：

| PSPS | 问什么 | 决定什么 |
|---|---|---|
| Persona | 谁决策、谁执行、谁验收 | 权限、入口、统计口径 |
| Scenario | 何时触发、如何流转、何时结束 | 流程、状态机、SOP、时间线 |
| Pain | 卡在哪里、怕什么失败 | 风险、自动化、校验、异常处理 |
| Solution Surface | 系统要暴露什么能力 | 页面、看板、接口、报表、资产库、通知 |

通用规则：管理者要统计和看板；任务流转要状态和队列；素材/商品/文件要资产库；排期计划要时间线；执行者入口必须简单。

## 指令入口

你可以用自然语言触发，也可以用固定入口加速路由：

| 入口 | 你也可以直接说 | 会进入 |
|---|---|---|
| `/spec` `/define` | “我有个想法，帮我整理需求” | 需求澄清 / Spec |
| `/new-project` `/scaffold` | “从 0 搭一个项目” | 新项目架构和脚手架 |
| `/handover` `/audit` | “我接手了一个旧项目” | 旧项目盘点 |
| `/plan` `/split` | “这个功能怎么拆” | implementation plan |
| `/build` `/fix` | “帮我实现 / 修 bug” | 最小切片实现 |
| `/refactor` `/cleanup` | “帮我重构 / 清理 / 模块化” | 行为保持型重构 |
| `/test` `/review` `/ship` | “怎么测 / 能不能 merge / 准备发布” | 验证、review、发布门禁 |
| `/automation` `/rpa` `/ocr` `/llm` | “我要做 RPA / OCR / LLM 自动化” | 自动化场景选型、POC 和验证门禁 |
| `/self-evolve` | “自进化这个 Skill / 升级 skill” | GitHub lesson issue intake、依赖/source doctor、自进化 harness 与安装副本同步 |
| `/lesson` | “把这条规则记录成 lesson issue” | lesson issue intake；确认后才进入 runtime lesson |
| `/interview` `/hire` | “我要面试一个工程师” | 面试流程和评分卡 |
| `/onboard` `/training` | “给新人做入职培训” | 入职和工程化培训 |
| `/org` `/company` `/sop` | “我要构建组织 / 企业 / SOP” | 机制设计和落地路径 |
| `/estimate` `/wbs` | “帮我拆方案、排期、人天和成本” | 非工程项目估算 |
| `/artifact` `/nonsoftware` | “我要做文件输出 / Skill / 多维表 / 知识库项目” | 非软件开发项目治理 |
| `/learn` | “以后都这样 / 升级成模式” | lessons / patterns / reference 升级判断 |

这些入口只负责让 agent 更快命中路由，不会跳过需求、合规、worktree、source-driven 和验证门禁。

用户说“不对 / 不是 / 这部分好乱 / 你没有参考”时，默认不是 `/learn` 主路由，而是全局不满意捕获：agent 必须先承认偏差，并询问是否创建 GitHub lesson issue。

## 安装

默认安装到 Codex。`scripts/install.py` 会安装 `skills/*` 下的所有子 skill，包括主路由和各场景子 skill：

```bash
git clone https://github.com/HaodiFan/engineering-everything.git
cd engineering-everything
python3 scripts/install.py --target codex
```

安装到本地 Agents skills 目录：

```bash
git clone https://github.com/HaodiFan/engineering-everything.git
cd engineering-everything
python3 scripts/install.py --target agents
```

默认安装结果：

- `~/.codex/skills/engineering-everything`
- `~/.codex/skills/engineering-product-definition`
- `~/.codex/skills/engineering-architecture-design`
- `~/.codex/skills/engineering-execution-planning`
- `~/.codex/skills/engineering-build-verify`
- `~/.codex/skills/engineering-refactoring`
- `~/.codex/skills/engineering-review-release`
- `~/.codex/skills/engineering-automation-playbooks`
- `~/.codex/skills/engineering-organization-systems`
- `~/.codex/skills/engineering-project-inheritance`
- `~/.codex/skills/engineering-skill-evolution`
- `~/.agents/skills/engineering-everything`
- `~/.agents/skills/engineering-product-definition`
- `~/.agents/skills/engineering-architecture-design`
- `~/.agents/skills/engineering-execution-planning`
- `~/.agents/skills/engineering-build-verify`
- `~/.agents/skills/engineering-refactoring`
- `~/.agents/skills/engineering-review-release`
- `~/.agents/skills/engineering-automation-playbooks`
- `~/.agents/skills/engineering-organization-systems`
- `~/.agents/skills/engineering-project-inheritance`
- `~/.agents/skills/engineering-skill-evolution`

升级已有安装：

```bash
cd engineering-everything
git pull --ff-only
python3 scripts/install.py --target both
```

旧式整包安装仍保留，用于需要单目录兼容的场景：

```bash
python3 scripts/install.py --target both --layout legacy
```

## 看它怎么工作

### 做 OCR 方案

```text
你: 我要做 OCR 能力，先出方案。

Agent:
工程路由: Scenario | OCR / 文档智能 | Architecture
当前阶段: 3 架构
判断:
- 如果 OCR 只是后台基础能力，服务器只有 2C2G/4G，优先 Tesseract 或轻量 OCR 组件
- 如果 OCR 是核心能力，准确率和版面恢复是 P0，选 PaddleOCR
- 先确认输入样本、输出 schema、置信度阈值、人审规则
```

### 拆一个新功能

```text
你: 这个项目要加一个会员续费提醒。

Agent:
工程路由: Execution Plan | 会员续费提醒 | Product/Execution
当前阶段: 5 Feature 规划
下一步:
- 查现有 design doc 和会员模型
- 确认提醒渠道、触发时机、幂等规则、退订规则
- 写 implementation plan，再按最小切片实现
```

### 判断 PR 能不能合并

```text
你: review 一下这个 PR，能不能 merge。

Agent:
工程路由: Review/Release | PR readiness | Review/Release
检查:
- 行为风险
- 测试缺口
- secret / hardcode
- 架构边界
- release 和 rollback
```

### 做非工程项目方案和估算

```text
你: 我要做一个客户培训项目，帮我拆方案、排期、人天和成本。

Agent:
工程路由: Project Ops | 非工程项目工程化 | Product/Execution
输出:
- 目标、范围、非目标、成功指标
- 2-3 个方案选项和 tradeoff
- WBS、里程碑、owner、验收物
- 人天区间、成本公式、关键假设和风险缓冲
```

### 面试和入职培训

```text
你: 我要面试一个后端工程师，帮我设计面试流程和评分卡。

Agent:
工程路由: Talent | 工程师面试 | Product/Review
输出:
- 岗位画像和反向信号
- coding / system design / project deep dive 问题
- 评分卡、证据要求、debrief 模板
```

## 工程路由

规划类回答会先输出这组字段：

```text
工程路由: <主路由 | 命中场景 | 决策层>
当前阶段: <P/0-9/I>
项目形态: <Web+Backend | Desktop+Local Agent | Python Agent/CLI | Library/SDK | Full-stack Monorepo | Unknown>
参考依据:
- 路由规则: <命中的 SKILL.md 子 Skill 路由或不可突破规则>
- 已读 reference: <path -> 具体用于哪个判断>
- 外部/历史依据: <如使用 web / memory / repo 文件，说明来源和用途；未使用则写未使用>
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

路由决定 agent 下一步该读取哪个 reference。规划类回答必须把关键判断和已读取 reference 对上，不能只说“用了 Engineering Everything”。

| 用户在问 | 工程路由 | agent 应该做什么 |
|---|---|---|
| “我有个想法” | Product | 澄清需求、非目标、最小产品切片 |
| “技术栈怎么选” | Architecture | 判断项目形态、真相源、关键 tradeoff 和 ADR |
| “接手这个老项目” | Inherit | 先盘点现状，不急着重构 |
| “这个功能怎么拆” | Execution Plan | 写 implementation plan、vertical slices、validation gates |
| “帮我实现 / 修 bug / 迁移” | Build | 最小切片实现，并说明验证和风险 |
| “重构 / 清理 / 模块化” | Refactor | 先识别坏味道，再选重构手法、测试保护和 PR 拆分 |
| “怎么测 / 是否 ready” | Validation | 优先后端/API/service 自测，必要时再做浏览器 QA |
| “review / PR / release” | Review/Release | 查行为风险、测试证据、回滚、发布门禁 |
| “RPA / OCR / CV / LLM / 数据分析” | Scenario | 进入场景 playbook，给默认选型和风险边界 |
| “面试工程师 / 候选人评估” | Talent | 岗位画像、面试流程、评分卡、debrief |
| “入职培训 / 工程化培训” | Onboarding | 培训路径、协同机制、30/60/90 |
| “构建组织 / 企业 / SOP” | Organization System | 目标、角色、接口、流程、指标、异常处理和迭代机制 |
| “非工程项目方案 / 人天 / 成本” | Project Ops | 需求、WBS、排期、人天、成本和风险 |
| “文件输出 / Skill / 多维表 / 知识库” | Non-software Development | spec、源文件、目标产物和验证路径分离 |
| “以后都这样 / 记录成 lesson issue” | Learn | 创建 lesson issue，确认后再进入 runtime lesson / pattern |
| “不对 / 不是 / 这部分好乱 / 你没有参考” | 原工程路由 + 不满意捕获 | 先修正当前任务，再询问是否创建 GitHub lesson issue |

## 工作循环

Engineering Everything 不是提示词合集，而是一套工程工作循环：

```text
Route -> PSPS -> Clarify -> Decide -> Plan -> Build -> Verify -> Ship -> Learn
```

- **Route**：先判断生命周期、项目形态、业务场景和决策层。
- **PSPS**：把模糊意图转成 Persona、Scenario、Pain、Solution Surface。
- **Clarify**：业务需求必须来自用户，agent 只负责结构化和追问。
- **Decide**：架构决策要比较选项、代价、退出成本，并用 ADR 记录。
- **Plan**：多步 feature 先写 implementation plan，再拆 vertical slices。
- **Build**：写代码前检查 checkout/worktree、source-driven gate 和影响边界。
- **Verify**：默认后端/API/service 自测优先，浏览器模拟只在该用时使用。
- **Ship**：PR readiness 包含 review、测试证据、发布风险和 rollback。
- **Learn**：只有用户明确要求记住、建 issue 或升级模式时才进入；用户不满意先走全局 issue 提示，不改变当前工程路由。

## 内置场景 Knowhow

| 场景 | 默认判断 |
|---|---|
| 中国电商数据 / RPA | 先问平台，再问数据源。公域数据、商家后台、手机 RPA 是三类不同问题。 |
| 浏览器自动化 | Selenium / Playwright 都可用；商家后台优先考虑 undetected ChromeDriver；动作要加随机 sleep。 |
| 手机 RPA | 用 Appium；元素检索优先 XPath；注意频率、风控和失败恢复。 |
| OCR | 基础后台能力优先轻量方案；核心能力或版面恢复要求高时用 PaddleOCR。 |
| AI 选型 | 先识别经典任务，再按成本、时效、效果选择规则、传统模型、LLM/VLM 或混合方案。 |
| 数据分析 | 区分解释报告、agent chat 分析、时序预测、生产级数据管线。 |

## 工程化工具

v0.9.0 开始，Skill 把稳定、可判定、可重复的动作下沉到了脚本：

| 脚本 | 作用 |
|---|---|
| `scripts/install.py` | 安装或升级到 Codex / Agents skill 目录，避免复制路径漂移。 |
| `scripts/skill_doctor.py` | 发布前检查包结构、版本一致性、README 安装路径、reference 链接和旧触发名残留。 |
| `scripts/lesson.py` | 为 L1 lesson 分配编号、生成卡片、校验字段和状态。 |
| `scripts/self_evolve.py` | 检查自进化 harness、lesson/pattern 计数、安装副本同步和 GitHub canonical source。 |

运行发布前检查：

```bash
python3 engineering-everything/scripts/skill_doctor.py
```

## 目录结构

```text
engineering-everything/
├── .codex-plugin/
│   └── plugin.json
├── SKILL.md
├── agents/
│   └── openai.yaml
├── data/
│   ├── routes.yaml
│   ├── review_roles.yaml
│   └── validation_commands.yaml
├── docs/
│   └── design/active/
│       └── 2026-06-27-split-skill-library.md
├── skills/
│   ├── engineering-architecture-design/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-automation-playbooks/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-build-verify/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-everything/
│   │   └── SKILL.md
│   ├── engineering-execution-planning/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-organization-systems/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-product-definition/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-project-inheritance/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-refactoring/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── engineering-review-release/
│   │   ├── SKILL.md
│   │   └── references/
│   └── engineering-skill-evolution/
│       ├── SKILL.md
│       └── references/
├── references/                      # legacy/source compatibility copies
│   ├── engineering-scenario-map.md
│   ├── engineering-scenarios.md
│   ├── stage-playbook.md
│   ├── execution-pipeline.md
│   ├── architecture-cases.md
│   ├── architecture-cases-ai.md
│   ├── scenario-playbooks.md
│   ├── checklists.md
│   ├── code-review-standards.md
│   ├── psps-framework.md
│   ├── refactoring-rules.md
│   ├── inheriting-projects.md
│   ├── memory-bank-guide.md
│   ├── prompts-guide.md
│   ├── lessons.md
│   ├── patterns-skill.md
│   └── self-evolution-harness.md
├── schemas/
│   ├── lesson.schema.json
│   └── pattern.schema.json
└── scripts/
    ├── install.py
    ├── lesson.py
    ├── self_evolve.py
    └── skill_doctor.py
```

核心 reference：

| 文件 | 用途 |
|---|---|
| `.codex-plugin/plugin.json` | Codex plugin-style 多 skill 入口，声明 `skills: ./skills/`。 |
| `skills/engineering-everything/SKILL.md` | 主路由 skill，只判断工程路径并选择子 skill。 |
| `skills/engineering-project-inheritance/SKILL.md` | 接手已有项目子 skill，处理老项目盘点和重构前置判断。 |
| `skills/engineering-*/SKILL.md` | 场景子 skill，分别承接产品定义、架构、执行、构建、重构、review/发布、自动化、组织系统、接手盘点和 skill 自进化。 |
| `skills/engineering-*/references/*.md` | 各子 skill 的自包含 reference；运行时优先使用这里。 |
| `references/engineering-scenario-map.md` | legacy/source 兼容副本；完整迁移后运行时 route 已指向子 skill reference。 |
| `references/engineering-scenarios.md` | 工程化万物扩展场景：面试、入职培训、组织/企业/SOP、非工程项目估算、软件/非软件开发项目治理。 |
| `references/stage-playbook.md` | 从 POC、想法、架构、实现到维护的阶段流程。 |
| `references/execution-pipeline.md` | worktree 策略、source-driven gate、implementation plan、review pipeline、验证门禁。 |
| `references/psps-framework.md` | PSPS 构建洞察框架：Persona、Scenario、Pain、Solution Surface。 |
| `references/refactoring-rules.md` | 重构规则库：坏味道到手法映射、行为保持 gate、测试保护和 PR 拆分。 |
| `references/scenario-playbooks.md` | RPA、OCR、CV、数据、LLM、浏览器自动化、POC 场景。 |
| `references/architecture-cases.md` | 通用架构选型、代价、反例、决策信号。 |
| `references/architecture-cases-ai.md` | AI/Agent 架构、模型选型、RAG、工具调用、记忆、评估、安全。 |
| `references/lessons.md` / `references/patterns-skill.md` | 用户纠偏和可复用模式沉淀。 |
| `references/self-evolution-harness.md` | Skill 自进化流程、GitHub issue intake、验证和安装同步门禁。 |

## FAQ

### 这和直接问 ChatGPT / Codex 有什么区别？

直接问会很快给答案，但不一定先判断“这是什么类型的问题”。这个 Skill 的价值是强制 agent 先做 工程路由，再决定读哪个 playbook、补哪个产物、跑哪个 gate。

### 只适合 Codex 吗？

不是。它按 Skill 目录组织，Codex 使用最自然；但核心是 `SKILL.md` + `references/`，任何支持注入上下文或本地 Skill 的 agent 都可以复用。

### 触发名是什么？

触发名是 `$engineering-everything`。安装目录也使用 `engineering-everything`，和 repo 名保持一致。

### 它会替我写业务需求吗？

不会。业务意图必须由 owner 提供。Skill 负责校验完备性、结构化、追问和判断下一步，不替用户编造业务目标。

### 它什么时候会用浏览器模拟？

默认不会。测试优先后端/API/service 自测。只有用户要求、任务本身是浏览器/RPA、bug 只能在真实浏览器复现，或 release QA 命中时，才使用浏览器模拟。

## 状态

- 当前版本：`0.9.10`
- 公开仓库：`HaodiFan/engineering-everything`
- Skill ID：`engineering-everything`
- License：暂未声明，公开分发前建议补充 LICENSE

## 卸载

删除已安装的 Skill：

```bash
rm -rf ~/.codex/skills/engineering-everything
rm -rf ~/.agents/skills/engineering-everything
```

这不会删除你在项目里用 Skill 创建过的代码或文档。
