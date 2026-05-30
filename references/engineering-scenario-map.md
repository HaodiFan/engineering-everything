# Engineering Scenario Map

本文件是 Skill 的入口地图。它回答：用户一句话进来时，Engineering Everything 先判断什么、走哪条知识路由、读取哪些 reference、产出什么决策。

定位：**用工程思维看待一切创造，不是单纯写代码助手**。先判断问题属于产品、软件、组织、企业、SOP、架构、执行、验证、治理、场景选型还是组织记忆；再决定要不要写代码、补文档、做选型、拆计划、跑验证、搭机制或停下来问 owner。

---

## 1. 四轴路由

每个请求先按四轴归类：

| 轴 | 取值 |
|---|---|
| 生命周期 | P POC/Spike / 0 想法 / 1 需求澄清 / 2 Spec / 3 架构 / 4 脚手架 / 5 Feature 规划 / 6 实现 / 7 验证 / 8 PR/发布 / 9 维护 / I 接手盘点 |
| 项目形态 | Web+Backend / Desktop+Local Agent / Python Agent/CLI / Library/SDK / Full-stack Monorepo / Non-software Project / Organization System / Enterprise System / SOP System / Unknown |
| 业务场景 | RPA/采集 / OCR/文档智能 / CV/视觉质检 / 数据治理/分析报表 / LLM 生产链路 / 浏览器自动化 / 重构治理 / 面试 / 入职培训 / 非工程项目 / 非软件开发 / 通用软件工程 |
| 决策层 | Product / Talent / Onboarding / Architecture / Execution / Validation / Review / Release / Governance / Learn |

如果四轴无法判断，先输出“路由待定 + 候选路由 + 缺什么信息”，不要直接给完整方案。

---

## 2. 指令入口

Skill 支持两类入口：

- **显式入口**：用户输入 `$engineering-everything /xxx ...`，agent 直接按 alias 命中路由。
- **模糊入口**：用户用自然语言描述任务，agent 先按信号词和上下文判断路由，再输出 工程路由模板。

| 显式入口 | 模糊说法 | 工程路由 | 主要读取 |
|---|---|---|---|
| `/spec` `/define` `/prd` | “我有个想法 / 帮我整理需求” | Product | `stage-playbook.md`、`checklists.md`、`spec-templates.md` |
| `/arch` `/scaffold` `/new-project` | “从 0 搭项目 / 技术栈怎么选” | Architecture | `architecture-cases.md`、`project-blueprints.md` |
| `/handover` `/audit` `/inherit` | “接手老项目 / 项目很乱先看一下” | Inherit | `inheriting-projects.md` |
| `/plan` `/split` | “这个功能怎么拆” | Execution Plan | `execution-pipeline.md`、`checklists.md` |
| `/build` `/fix` `/migrate` | “实现 / 修 bug / 迁移” | Build | `stage-playbook.md`、`execution-pipeline.md` |
| `/refactor` `/cleanup` `/modularize` | “重构 / 清理 / 模块化 / 技术债治理” | Refactor | `refactoring-rules.md`、`checklists.md`、`execution-pipeline.md` |
| `/test` `/review` `/ship` | “怎么测 / review / 能不能 merge” | Validation / Review / Release | `checklists.md`、`code-review-standards.md` |
| `/interview` `/hire` `/scorecard` | “面试工程师 / 候选人评估” | Talent | `engineering-scenarios.md` |
| `/onboard` `/training` `/bootcamp` | “入职培训 / 工程化培训” | Onboarding | `engineering-scenarios.md`、`templates-core.md` |
| `/org` `/company` `/sop` | “构建组织 / 构建企业 / 搭 SOP / 设计协同机制” | Organization System | `engineering-scenarios.md`、`templates-core.md` |
| `/estimate` `/wbs` `/project` | “非工程项目拆方案、排期、人天、成本” | Project Ops | `engineering-scenarios.md` |
| `/artifact` `/nonsoftware` `/workspace` | “文件输出 / Skill / 多维表 / 知识库项目” | Non-software Development | `engineering-scenarios.md`、`spec-templates.md` |
| `/learn` `/lesson` `/pattern` | “这次纠偏记住 / 升级成模式” | Learn | `lessons.md`、`patterns-skill.md` |

显式入口只负责加速路由，不跳过需求、合规、worktree、source-driven、验证门禁。

---

## 3. 使用场景地图

| 用户问题 | 工程路由 | 读取 | 产出 |
|---|---|---|---|
| “我有个想法 / 想做个系统” | Product → Stage 0-2 | `stage-playbook.md`、`checklists.md`、`spec-templates.md` | 需求缺口、非目标、下一步提问 |
| “从 0 搭项目 / 技术栈怎么选” | Architecture → Stage 3-4 | `architecture-cases.md`、AI 项目加 `architecture-cases-ai.md`、`project-blueprints.md` | 形态判断、技术基线、starter tree |
| “接手这个老项目 / 继续迭代” | Inherit → Stage I | `inheriting-projects.md` | 自动识别、现状报告、第一周做与不做 |
| “这个功能怎么拆” | Execution Plan → Stage 5 | `execution-pipeline.md`、`checklists.md` | implementation plan、vertical slices、validation gates |
| “帮我实现 / 修 bug / 迁移” | Build → Stage 6 | `stage-playbook.md`、`execution-pipeline.md`、`agent-operating-standards.md` | 最小切片实现、验证、风险说明 |
| “重构 / 清理 / 模块化 / 技术债治理” | Refactor → Stage 9 | `refactoring-rules.md`、`checklists.md`、`execution-pipeline.md` | 坏味道识别、重构手法、测试保护、PR 拆分 |
| “怎么测 / 是否 ready” | Validation → Stage 7 | `checklists.md`、`execution-pipeline.md` | 最小相关验证、缺口、风险关闭 |
| “review / PR / release” | Review/Release → Stage 7-8 | `code-review-standards.md`、`checklists.md`、`execution-pipeline.md` | findings、PR readiness、rollback |
| “RPA / 电商数据 / OCR / CV / LLM / 数据分析” | Scenario → 场景路线 | `scenario-playbooks.md`，必要时加 `architecture-cases-ai.md` | 默认选型、合规边界、最小切片、场景 checklist |
| “面试工程师 / 入职培训 / 企业协同 / 非工程项目估算” | Engineering Scenarios | `engineering-scenarios.md` | 面试评分卡、培训路径、WBS、人天/成本估算 |
| “构建组织 / 构建企业 / SOP / 协同机制” | Organization System | `engineering-scenarios.md`、`templates-core.md` | 目标、角色、接口、流程、指标、异常处理 |
| “文件输出 / Skill 开发 / 多维表开发 / 知识库” | Non-software Development | `engineering-scenarios.md`、`spec-templates.md` | spec、源文件、目标产物和验证路径分离 |
| “项目规范 / 文档 / agent 协作” | Governance | `templates-core.md`、`templates-governance.md`、`memory-bank-guide.md`、`prompts-guide.md` | 文档骨架、红线、ADR、Memory Bank |
| “这次纠偏记住 / 方法论升级” | Learn | `lessons.md`、`patterns-skill.md` | L1 lesson、L2 pattern、reference 升级建议 |

---

## 4. 路由优先级

多条命中时按这个顺序取主路由：

1. **接手现有项目优先**：先盘点 as-is，不急着重构或套模板。
2. **安全 / 合规 / secret / 平台 ToS 优先**：先划红线和 source-driven gate。
3. **用户明确要执行代码**：进入 Stage 6，但仍先检查 spec、checkout/worktree 和验证门禁。
4. **用户明确要重构**：读 `refactoring-rules.md`，先证明行为保持和测试保护，再决定是否动代码。
5. **业务场景明确**：读 `scenario-playbooks.md`，再回到生命周期阶段。
6. **项目形态 Unknown**：先跑架构形态判断，不输出 starter。
7. **人才 / 培训 / 组织 / 企业 / SOP / 非工程 / 非软件开发**：读 `engineering-scenarios.md`，用工程化结构拆目标、产物、估算和验收。
8. **方法论 / Skill 建设**：只改 reference、脚本或模板，不把大段内容塞回 `SKILL.md`。

---

## 5. 工程路由输出模板

规划类回答顶部使用这个模板：

```text
工程路由: <主路由 | 命中场景 | 决策层>
当前阶段: <P/0-9/I>
项目形态: <形态>（如有场景，追加：场景 <RPA/OCR/LLM/...>）
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

执行类回答不强制完整模板，但收尾必须包含变更文件、已运行验证、未运行检查及原因、剩余风险。

---

## 6. 传播命名

- 对外名称：**Engineering Everything** / **工程化万物 Skill**。
- 推荐 repo name：`engineering-everything`。
- Skill ID / 安装目录 / 触发名统一为 `engineering-everything`，使用 `$engineering-everything` 触发。
