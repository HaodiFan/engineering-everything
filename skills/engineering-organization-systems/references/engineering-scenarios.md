# 工程化万物场景 Playbook

本文件定义 Engineering Everything 作为“工程化分身”时承载的高层指导场景。它覆盖软件开发、组织构建、企业机制、人才、培训、SOP、非工程项目和不同类型开发项目；目标是把工程化判断方式产品化，而不是只回答代码问题。

使用原则：

- 先判断场景，再选择产物；不要把软件工程模板硬套到所有问题。
- 能工程化的就工程化：需求、边界、里程碑、人天、成本、风险、验收、复盘。
- 组织、企业和 SOP 也按工程处理：目标、角色、接口、节奏、反馈、指标、异常处理和持续迭代。
- 对不确定信息给区间和假设，不伪装成精确结论。
- 涉及人事、绩效、合规、隐私时只做结构化建议，不替代 owner 的最终判断。

---

## 0. 指令入口与知识储备成熟度

显式 `/指令` 和自然语言都必须先转成 工程路由，再进入下表对应场景。

| 入口 | 模糊触发 | 场景 | 当前支持 | 需要用户补充的动态信息 |
|---|---|---|---|---|
| `/interview` `/hire` `/scorecard` | 面试工程师、候选人、JD、debrief | 面试新的工程师 | 中 | 岗位级别、技术栈、业务阶段、团队文化、评分权重 |
| `/onboard` `/training` `/bootcamp` | 入职培训、工程化培训、企业介绍、协同机制 | 入职培训 | 中 | 公司业务、组织结构、权限系统、研发流程、真实案例 |
| `/org` `/company` `/sop` | 构建组织、构建企业、SOP、协同机制、制度流程 | 组织/企业/SOP 工程化 | 中 | 业务目标、组织规模、角色边界、决策权、现有流程、指标口径 |
| `/estimate` `/wbs` `/project` | 非工程项目方案、排期、人天、成本估算 | 非工程项目工程化 | 中 | 目标、预算、单价、角色配置、依赖方、验收标准 |
| `/new-project` `/scaffold` | 新 repo、从 0 搭项目、技术栈选型 | 新软件项目 | 强 | 业务需求、约束、团队偏好、部署环境 |
| `/handover` `/audit` `/inherit` | 接手旧项目、继续迭代、规范化 | 旧软件项目 | 强 | repo、运行方式、当前目标、owner 可达性 |
| `/artifact` `/nonsoftware` `/workspace` | 文件输出、Skill 开发、多维表、知识库 | 非软件开发项目 | 中 | 目标产物格式、源数据、发布渠道、人工验收口径 |

成熟度定义：

- **强**：已有完整阶段流程、模板、检查清单和验证门禁，可以直接指导落地。
- **中**：已有工程化框架和输出模板，但公司/岗位/成本/业务信息必须由用户补齐。
- **弱**：只能给方法论骨架，需要先补 reference、模板或数据字典再规模化复用。

当前缺口：

- 面试：缺少按岗位/级别拆分的题库、评分样例和 calibrated rubric。
- 入职：缺少公司真实业务、组织结构、权限系统、研发制度的填充模板。
- 组织/企业/SOP：缺少公司级真实组织图、职责矩阵、流程现状、指标口径和治理节奏模板。
- 非工程项目估算：缺少可配置单价表、复杂度系数和估算 worksheet schema。
- 非软件开发项目：缺少文件输出、Skill、多维表、知识库四类产物的独立模板库。

---

## 1. 面试新的工程师

### 触发信号

用户问招聘、面试、候选人、JD、技术面、系统设计面、工程师评估、面试题、debrief、offer 风险。

### 工程路由

```text
工程路由: Talent | 工程师面试 | Product/Review
当前阶段: I/0-2（岗位定义不清时）或 7（候选人评估时）
项目形态: Organization System
```

### 输出产物

- 岗位画像：级别、职责、必须项、加分项、反向信号。
- 面试流程：screen / coding / system design / project deep dive / culture & collaboration / debrief。
- 评分卡：每个维度有证据、等级、风险，不只写主观印象。
- 问题库：按岗位能力映射，不问无关脑筋急转弯。
- debrief 模板：hire / no-hire / hold，写清证据和风险。

### 必问维度

| 维度 | 看什么 |
|---|---|
| Problem solving | 能否拆问题、识别约束、解释 tradeoff |
| System design | 边界、数据模型、扩展性、故障和观测性 |
| Code quality | 可读性、测试意识、错误处理、维护成本 |
| Product sense | 是否理解业务目标和用户价值 |
| Collaboration | 需求澄清、review 方式、沟通密度 |
| Ownership | 是否能推进不确定任务并收口 |

### 红线

- 不问与岗位无关的隐私、家庭、年龄、婚育、健康、政治、宗教等问题。
- 不把单次 coding 表现当唯一结论；必须结合证据链。
- 不用“感觉聪明 / 气场不错”替代评分卡。

---

## 2. 入职培训与工程化培训

### 触发信号

用户问新人 onboarding、入职培训、工程培训、企业介绍、协同机制、开发机制、如何日常使用本 Skill。

### 工程路由

```text
工程路由: Onboarding | 工程化培训 | Governance/Learn
当前阶段: 0-2（设计培训）或 6-8（执行培训）
项目形态: Organization System
```

### 输出产物

- 公司 / 团队介绍：业务、组织、产品线、技术栈、决策机制。
- 工程化培训路径：开发环境、代码规范、分支策略、review、测试、发布、事故处理。
- 协同机制：需求入口、设计评审、异步沟通、会议节奏、owner 责任。
- 日常使用本 Skill：什么时候 `$engineering-everything`，如何写 prompt，如何更新 memory / lessons。
- 30/60/90 天计划：阶段目标、任务、导师、验收标准。

### 推荐结构

| 阶段 | 目标 | 交付 |
|---|---|---|
| Day 1-3 | 能跑起来 | 环境、权限、仓库、第一条 docs PR |
| Week 1 | 理解团队工作方式 | 读架构、跑测试、参与 review、完成小修 |
| Week 2-4 | 独立交付小功能 | design doc、implementation plan、最小切片 |
| Day 30-90 | 承担模块 owner | 主导 feature、改进流程、沉淀 pattern |

### Skill 日常用法

- 新需求：让 Skill 先判断工程路由和缺失内容。
- 开发前：让 Skill 检查 spec、worktree、source gate、implementation plan。
- 提 PR 前：让 Skill 跑 PR readiness 和 review roles。
- 会话结束：让 Skill 更新 active-context 或捕获 lesson。

---

## 3. 非工程项目，用工程视角解决

### 触发信号

用户问运营项目、交付项目、咨询方案、活动、调研、文档、培训、销售支持、预算、排期、人天、成本估算。

### 工程路由

```text
工程路由: Project Ops | 非工程项目工程化 | Product/Execution
当前阶段: 0-8
项目形态: Non-software Project
```

### 默认输出

- 需求澄清：目标、范围、非目标、约束、成功指标。
- 方案选项：至少 2-3 个方案，说明成本、速度、质量、风险。
- WBS：工作分解、依赖、owner、验收物。
- 排期：里程碑、关键路径、缓冲。
- 人天估算：按角色、任务、复杂度给区间。
- 成本估算：人力成本、工具成本、外包/采购、风险缓冲。
- 风险与回滚：什么情况下停、降级、延期或换方案。

### 估算规则

- 估算必须写假设：输入质量、决策速度、依赖可用性、返工比例。
- 默认给区间，不给伪精确数字。
- 人天 = 任务拆分 × 角色 × 复杂度 × 风险系数。
- 成本 = 人天 × 单价 + 工具/服务/采购 + buffer。
- 不知道单价时，先输出公式和需要用户补的变量。

### 输出模板

```text
目标:
范围 / 非目标:
关键假设:
方案选项:
WBS:
里程碑:
人天估算:
成本估算:
风险:
下一步 3 个动作:
```

---

## 4. 构建组织、企业和 SOP

### 触发信号

用户问构建组织、构建企业、搭 SOP、协同机制、制度流程、部门职责、会议节奏、决策机制、运营体系、交付体系。

### 工程路由

```text
工程路由: Organization System | 组织/企业/SOP 工程化 | Governance/Execution
当前阶段: 0-8
项目形态: Organization System / Enterprise System / SOP System
```

### 默认输出

- 目标系统：这个组织/企业/SOP 要稳定产生什么结果。
- 角色与接口：owner、参与者、输入、输出、权限、升级路径。
- 流程与节奏：触发条件、步骤、会议/异步节奏、SLA、例外处理。
- 指标与反馈：领先指标、滞后指标、质量指标、复盘频率。
- 产物与真相源：制度文档、模板、表单、看板、知识库、审批链路。
- 推进计划：试点范围、里程碑、培训、验收、迭代机制。

### 设计规则

- 先定义目标产出，再设计组织结构；不要先画部门。
- 每个流程必须有 owner、输入、输出、停止条件和异常处理。
- SOP 不是静态文档，必须绑定触发场景、角色、模板、检查清单和复盘。
- 企业机制要区分红线、原则、流程、习惯；不要把偏好写成制度。
- 从一个最小闭环试点开始，不一次性铺满全公司。

### 输出模板

```text
系统目标:
当前约束:
角色 / RACI:
输入 / 输出:
流程步骤:
SOP 产物:
指标:
试点计划:
风险与例外:
下一步 3 个动作:
```

---

## 5. 工程开发项目

### 5.1 新软件项目

触发：新 repo、从 0 开始、搭架构、搭脚手架、选技术栈。

走既有 Stage 0-4：

- 需求由 owner 提供，Skill 校验和追问。
- 选项目形态：Web+Backend / Desktop+Local Agent / Python Agent/CLI / Library/SDK / Monorepo。
- 落地 `ARCHITECTURE.md`、ADR、`CONSTITUTION.md`、`BRANCHING.md`、Memory Bank、AGENTS。
- 先做最小端到端切片，不做大面积半成品。

读取：`stage-playbook.md`、`project-blueprints.md`、`architecture-cases.md`、`spec-templates.md`。

### 5.2 旧软件项目

触发：接手旧 repo、继续迭代、项目很乱、想规范化、想微调脚手架。

默认顺序：

1. 先理解当前结构：语言、框架、包管理器、入口、测试、部署、文档、git 画像。
2. 输出 as-is 现状报告，不急着重构。
3. 建立最小文档索引：README、ARCHITECTURE、DEVELOPMENT、active-context。
4. 只做低风险 folder / docs / dev workflow 适配；不擅自改业务结构。
5. 需要移动文件时，先做映射表、验证命令和回滚路径。

读取：`inheriting-projects.md`、`execution-pipeline.md`、`templates-core.md`。

### 5.3 非软件开发的开发项目

触发：文件输出、Skill 开发、多维表开发、知识库、自动化配置、提示词库、报告模板、工作流搭建。

原则：用软件开发规范统筹 spec，但把“目标产出物”和“项目管理骨架”分离。

推荐结构：

```text
project/
├── README.md
├── docs/
│   ├── requirements/
│   ├── design/
│   ├── decisions/
│   ├── memory-bank/
│   └── governance/
├── src/ or workspace/
│   └── <可编辑源文件 / 配置 / skill 包 / 表结构>
├── outputs/
│   └── <最终交付物，必要时 gitignored 或单独版本管理>
└── scripts/
    └── <生成 / 校验 / 导出脚本>
```

拆分原则：

- `docs/` 管目标、约束、决策、验收。
- `src/` / `workspace/` 管可编辑源。
- `outputs/` 管目标产物，不让产物反向污染 spec。
- 任何生成型项目都要有“从源到输出”的可重复步骤。

例子：

| 项目 | 源 | 产物 | 验证 |
|---|---|---|---|
| Skill 开发 | `SKILL.md` / references / scripts | 可安装 skill 包 | `skill_doctor.py` |
| 文件输出 | markdown / docx source / data | PDF / DOCX / PPTX | render / diff / 人审 |
| 多维表开发 | schema / view config / automations | 表结构和视图 | 字段校验 / 样例数据 |
| 知识库 | source notes / taxonomy | 发布版知识库 | 链接检查 / 覆盖检查 |

---

## 6. 路由优先级补充

多场景重叠时：

1. 人事 / 面试 / 培训优先走 Talent / Onboarding，不伪装成代码任务。
2. 非工程项目优先用 Project Ops，把需求、WBS、人天、成本和风险讲清。
3. 非软件开发项目走 Non-software Development，用工程结构管理源和产物。
4. 软件项目再按新项目 / 旧项目 / feature / build / review 路由。
5. 任何涉及合规、安全、平台 ToS、隐私的场景优先进入风险判断。
