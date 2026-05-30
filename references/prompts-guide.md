# Prompts 目录指南

为项目沉淀**可复用的高频动作模板**，让 agent 在不同会话中以相同方式触发同样的工作流。

> 与宿主无关：本指南只规定**目录约定与模板内容**，不依赖 Claude Code / Cursor / Codex 的斜杠命令机制。任何 agent 都可以"读取 + 应用"这些 prompt 模板。

## 设计原则

- **一个 prompt 一个意图**：拆细，不堆砌。
- **明确输入与产出**：每份 prompt 顶部声明"我需要什么 + 我交付什么"。
- **引用 references**：让 prompt 路由到本 Skill 的 reference，而非复制方法论。
- **对 agent 友好**：用结构化 markdown，避免长段散文。
- **与项目共生**：prompts 可被项目自定义/覆盖；本指南给的是基线模板。

## 目录约定

```
docs/prompts/
├── README.md                 # 索引：列出所有可用 prompt
├── scaffold-new-project.md   # 从 0 启动新项目
├── spike-start.md            # 启动 POC / Spike（轻量模式）
├── handover-audit.md         # 接手项目盘点
├── new-feature.md            # 已有项目加 feature
├── scenario-routing.md       # 命中业务场景时如何路由 scenario-playbooks
├── new-design-doc.md         # 创建 design doc
├── new-adr.md                # 记录架构决策
├── pre-pr.md                 # PR 前自检
├── update-active-context.md  # 会话末更新 memory bank
├── refactor-safely.md        # 行为保持型重构
├── debug-incident.md         # 救火 / 故障排查
├── lifecycle-aliases.md      # /spec /plan /build /test /review /ship /learn 入口映射
├── avatar-aliases.md         # /interview /onboard /org /sop /estimate /artifact 工程化场景入口
├── capture-lesson.md         # 用户纠偏后捕获 L1 lesson
└── promote-pattern.md        # L1 → L2 / L2 → L3 promotion
```

> 路径 `docs/prompts/`，与 `docs/design/`、`docs/governance/`、`docs/memory-bank/` 平级。

## 通用 prompt 结构

每份 prompt 文件用统一结构：

```md
# Prompt: <动作名>

## 何时用
<用户请求满足什么条件时触发>

## 我需要的输入
- <字段 1>
- <字段 2>

## 我会交付
- <产物 1>
- <产物 2>

## 步骤
1.
2.
3.

## 引用的 references
- references/<file>.md
- references/<file>.md

## 输出格式
<工程路由模板 / 自由文本 / 文件 diff / 检查报告 ...>

## 完成判定
- [ ]
- [ ]
```

---

## 基线 prompt 模板

下面是建议默认 ship 的基线模板（v0.9.0 起新增 `avatar-aliases`，把工程化万物场景映射为宿主无关 prompt；v0.7.0 起新增 `lifecycle-aliases`，把常见 slash command 映射为宿主无关 prompt；v0.5.0 起新增 `capture-lesson` 与 `promote-pattern`，支持 skill 自身的 knowhow 沉淀；v0.4.1 已加 `spike-start` 与 `scenario-routing`）。项目可挑用、改写、新增。

### lifecycle-aliases.md

```md
# Prompt: Lifecycle Aliases

## 何时用
- 用户输入类似 `/spec`、`/plan`、`/build`、`/test`、`/review`、`/ship`、`/learn`
- 当前宿主不支持 slash command，但用户想用固定入口触发工作流

## Alias 映射
- `/spec` / `define` → Stage 1-2：澄清需求、创建/检查 spec
- `/plan` → Stage 5：implementation plan、vertical slices、validation gates
- `/build` → Stage 6：按 slice 实现，后端/API/service 自测优先
- `/test` → Stage 7：验证矩阵、最小相关验证、显式触发时 Browser QA
- `/review` → Stage 7-8：code review standards + review pipeline
- `/ship` → Stage 8：PR readiness、release gate、rollback、learn 收口
- `/learn` → Stage 8-9：memory-bank、lessons、patterns promotion

## 引用的 references
- references/stage-playbook.md
- references/execution-pipeline.md
- references/agent-operating-standards.md
- references/checklists.md
- references/code-review-standards.md（review 时）
- references/lessons.md / references/patterns-skill.md（learn 时）

## 完成判定
- [ ] 已把 alias 转成明确阶段
- [ ] 没有绕过需求、source-driven、checkout/worktree、验证 gate
- [ ] 输出符合规划类 工程路由模板或执行类收尾格式
```

### avatar-aliases.md

```md
# Prompt: Avatar Aliases

## 何时用
- 用户输入类似 `/interview`、`/hire`、`/scorecard`、`/onboard`、`/training`、`/org`、`/company`、`/sop`、`/estimate`、`/wbs`、`/artifact`、`/nonsoftware`
- 用户用自然语言描述工程化万物场景：面试工程师、入职培训、组织/企业/SOP、非工程项目估算、文件输出、Skill 开发、多维表或知识库项目
- 当前宿主不支持 slash command，但用户想用固定入口触发工程化工作流

## Alias 映射
- `/interview` / `/hire` / `/scorecard` → Talent：岗位画像、面试流程、评分卡、debrief
- `/onboard` / `/training` / `/bootcamp` → Onboarding：企业介绍、协同机制、开发机制、30/60/90
- `/org` / `/company` / `/sop` → Organization System：目标、角色、接口、流程、指标、异常处理、迭代机制
- `/estimate` / `/wbs` / `/project` → Project Ops：需求、方案、WBS、排期、人天、成本、风险
- `/artifact` / `/nonsoftware` / `/workspace` → Non-software Development：spec、源文件、目标产出物、验证路径分离
- `/new-project` / `/scaffold` → 新软件项目：Stage 0-4、架构选型、脚手架
- `/handover` / `/audit` → 旧软件项目：as-is 盘点、最小文档、低风险工程化适配

## 模糊触发例子
- “我要面试一个后端工程师，帮我设计面试流程和评分卡”
- “给新人做入职培训，包含企业介绍、协同机制和开发机制”
- “我要构建组织/企业/SOP，帮我拆角色、流程、指标和落地计划”
- “帮我把这个非工程项目拆方案、排期、人天和成本”
- “我要做一个多维表/文件输出/Skill 开发项目，按工程方式组织”
- “新项目从 0 搭，告诉我每个阶段下一步”
- “旧项目先理解结构，再按合适规范整理开发方式”

## 引用的 references
- references/engineering-scenarios.md
- references/engineering-scenario-map.md
- references/inheriting-projects.md（旧软件项目）
- references/project-blueprints.md（新软件项目）
- references/spec-templates.md（需要产物模板时）
- references/execution-pipeline.md（需要计划、验证、worktree 策略时）

## 完成判定
- [ ] 已把 alias 或模糊说法转成明确 工程路由
- [ ] 已判断该场景当前知识储备成熟度：强 / 中 / 弱
- [ ] 输出产物与场景匹配，没有把软件工程模板硬套到人事或非工程项目
- [ ] 缺少公司、岗位、预算、单价、业务背景等动态信息时，明确列为待用户补充
```

### scaffold-new-project.md

```md
# Prompt: Scaffold New Project

## 何时用
- 用户从空目录或新 repo 开始
- 用户问"这个项目怎么搭"

## 我需要的输入
- 用户提供的需求文档（或同意我先生成 Requirements Doc 模板让用户填写）
- 项目形态候选（Web+Backend / Desktop+Local Agent / Python Agent/CLI / Library / Monorepo / Unknown）
- 业务场景信号（RPA/采集、OCR、视觉质检、数据治理、LLM 生产链路、POC 等，如有）
- 关键约束（语言、合规、时间、预算）

## 我会交付
- 形态判断（含理由与代价）
- 关键架构决策清单（Stage 3 输出）
- starter 目录树（Stage 4）
- 首次提交文件清单
- BRANCHING.md / Constitution.md / Memory Bank 初始版

## 步骤
1. 校验需求文档完备性（references/checklists.md）
2. 用 psps-framework.md 把模糊意图转成 Persona / Scenario / Pain / Solution Surface
3. 形态判断走 architecture-cases.md §0 的 4 步法
4. 如命中业务自动化场景，先读 scenario-playbooks.md，确定最小切片和验证门禁
5. 走 architecture-cases.md 20 大类 + AI 项目 architecture-cases-ai.md 11 大类，逐项确定方案
6. 落地 BRANCHING.md（决策方向：trunk-based / git-flow / GitHub flow）
7. 落地 Constitution.md（项目红线）
8. 落地 starter tree（references/project-blueprints.md）
9. 初始化 Memory Bank（references/memory-bank-guide.md）
10. 输出首次提交清单 + Stage 4 完成判定

## 引用的 references
- references/stage-playbook.md（Stage 0–4）
- references/psps-framework.md（Persona / Scenario / Pain / Solution Surface）
- references/scenario-playbooks.md（命中场景时）
- references/architecture-cases.md
- references/architecture-cases-ai.md（AI 项目）
- references/project-blueprints.md
- references/spec-templates.md（模板索引）
- references/templates-core.md / templates-governance.md / templates-specs.md（按需）
- references/memory-bank-guide.md
- references/checklists.md（需求完备性 + 新项目 checklist）

## 输出格式
工程路由模板 + 文件清单

## 完成判定
- [ ] 需求完备性 PASS 或用户明确接受 NEEDS-INPUT
- [ ] ARCHITECTURE.md / BRANCHING.md / Constitution.md / DESIGN.md（UI 类）/ AGENTS.md 已就位
- [ ] Memory Bank 四件套有最小可用版本
- [ ] 首次提交清单符合 references/checklists.md「新项目 Checklist」
```

### handover-audit.md

```md
# Prompt: Handover Audit（接手项目盘点）

## 何时用
- 用户接手他人/团队的现有 repo
- 用户问"这项目怎么继续 / 该不该重构 / 先做什么"
- 用户给出已有 repo URL

## 我需要的输入
- repo 访问（路径或 URL）
- 业务负责人是否可达
- 用户的目标（接手后想干什么）

## 我会交付
- 自动识别报告（项目类型 + 工具链推断）
- 项目现状报告（references/inheriting-projects.md §2 模板）
- 路径建议（A 遵循 / B 稳定 / C 建文档 / D 重构）
- 第一周「做与不做」清单
- Memory Bank 四件套初始版（基于盘点结果）

## 步骤
1. 跑「自动识别清单」（references/inheriting-projects.md §1.0）
2. 6 块盘点 checklist 逐项过
3. 输出现状报告（标注「已确认 / 推断」）
4. 推荐路径并说明触发条件
5. 用现状结果初始化 Memory Bank

## 引用的 references
- references/inheriting-projects.md
- references/architecture-cases.md（校准 as-is 决策）
- references/memory-bank-guide.md

## 输出格式
现状报告 + 工程路由模板

## 完成判定
- [ ] 现状报告完成
- [ ] 路径选定（A/B/C/D 之一）
- [ ] Memory Bank 初始化
- [ ] 第一周不做清单已沟通
```

### new-feature.md

```md
# Prompt: New Feature

## 何时用
- 已有项目要加新 feature / 页面 / API / workflow / agent 能力

## 我需要的输入
- feature 名称与一句话目标
- 关联的 requirements 与 design doc（若已有）
- 影响范围预估（前端 / 后端 / 数据 / 集成）

## 我会交付
- design doc（如缺失）
- implementation plan（vertical slices + validation gates + review roles）
- 影响目录与文件清单
- 测试与 docs 计划
- Constitution 与 patterns.md 检查（不违反红线、走项目模式）

## 步骤
1. 校验关联 requirements 是否完备（checklists.md 完备性 checklist）
2. 用 `psps-framework.md` 检查 Persona / Scenario / Pain / Solution Surface 是否足够推导系统表面
3. 若无 design doc，按 `spec-templates.md` → `templates-specs.md` 创建 v0.0.1
4. UI 类：layout spec → 组件选择查 DESIGN.md
5. 读取 `execution-pipeline.md`，输出 implementation plan：PSPS、file map、vertical slices、validation gates、review roles
6. 检查 Constitution 红线 + patterns.md 模式
7. 更新 active-context.md

## 引用的 references
- references/stage-playbook.md（Stage 5）
- references/psps-framework.md（PSPS 构建洞察）
- references/execution-pipeline.md（Implementation Plan + Review Pipeline）
- references/spec-templates.md（模板索引）
- references/templates-specs.md（Design Doc / PR Body）
- references/checklists.md（Feature Checklist）
- references/memory-bank-guide.md（patterns.md / active-context.md）

## 输出格式
工程路由模板 + milestone 列表

## 完成判定
- [ ] 已有 design doc（status: active）
- [ ] vertical slice 切完，每个有 validation gate
- [ ] 命中的 review roles 已标出
- [ ] active-context.md 更新
```

### new-design-doc.md

```md
# Prompt: New Design Doc

## 何时用
- Stage 2，要建 PRD/design doc

## 步骤
1. 套 `spec-templates.md` → `templates-specs.md` 的 Design Doc 模板
2. 按 `psps-framework.md` 补齐 PSPS 与 Solution Surface
3. 关联 requirements 与（UI 类）layout spec
4. 写验收标准 + 回滚点
5. Status 默认 `draft`，归档到 `docs/design/`

## 引用
- references/psps-framework.md（PSPS）
- references/spec-templates.md（模板索引）
- references/templates-specs.md（Design Doc）
- references/stage-playbook.md（Stage 2）

## 完成判定
- [ ] 验收标准可被开发者直接用
- [ ] 没有"大而全总集"
```

### new-adr.md

```md
# Prompt: New ADR

## 何时用
- 做出可追溯的架构/技术决策（选库、改边界、引入新模式）
- 决策有后果，未来要回溯"当时为什么这么选"

## 步骤
1. 找 `docs/decisions/` 下当前最大编号 N
2. 新建 `ADR-<N+1>-<kebab-title>.md`
3. 套 `spec-templates.md` → `templates-governance.md` 的 ADR 模板
4. 链接到 ARCHITECTURE.md Technical Baseline 对应行
5. 提交 PR 走 review

## 引用
- references/spec-templates.md（模板索引）
- references/templates-governance.md（ADR 模板）
- references/architecture-cases.md / architecture-cases-ai.md（决策时查 case）

## 完成判定
- [ ] 文件名有连续编号
- [ ] 状态字段明确（proposed/accepted/superseded/deprecated）
- [ ] 后果（trade-offs）写清
```

### pre-pr.md

```md
# Prompt: Pre-PR Self-check

## 何时用
- 准备开 PR 前
- 用户说"准备提交 / 该开 PR 了 / ship"

## 步骤
1. 跑 PR Readiness checklist
2. 跑 `execution-pipeline.md` 的 Review Gate / Validation Gate / Learn Gate；验证默认后端/API/service 自测优先，浏览器模拟只在显式触发时运行
3. 跑 Constitution 红线检查
4. 同步 design doc / requirements / DESIGN（UI）/ ARCHITECTURE（架构改动）
5. 更新 active-context.md：标 PR 状态
6. 输出 PR body（`spec-templates.md` → `templates-specs.md` 模板）

## 引用
- references/checklists.md（PR Readiness）
- references/execution-pipeline.md（Review Pipeline / 后端优先验证 / Browser QA 触发边界 / Learn）
- references/spec-templates.md（模板索引）
- references/templates-specs.md（PR Body）

## 完成判定
- [ ] PR Readiness 全过
- [ ] Constitution 0 违反
- [ ] PR body 完整
```

### update-active-context.md

```md
# Prompt: Update Active Context

## 何时用
- 每次会话结束前
- 重要进展后

## 步骤
1. 在 active-context.md 写"已完成"
2. 写"进行中" / "下一步"
3. 列阻塞与决策待定
4. 给下一会话 agent 的留言（具体）
5. 仅当发现新/反模式时，提议更新 patterns.md（不擅自改）

## 引用
- references/memory-bank-guide.md

## 完成判定
- [ ] 时间戳更新
- [ ] hand-off 留言具体（不是"继续"这种废话）
```

### refactor-safely.md

```md
# Prompt: Refactor Safely

## 何时用
- 行为保持型重构
- 用户说"清理 / 模块化 / 重命名 / 重构"

## 步骤
1. 明确"不改变行为"
2. 读取 `refactoring-rules.md`，识别具体坏味道并选择对应手法
3. 识别覆盖测试 / smoke check（缺则先补）
4. 校验 Constitution（重构不违反红线）
5. 走小步重构，不混 feature / bug fix / format / dependency upgrade
6. 边界变化时同步 ARCHITECTURE / folder declaration / patterns.md
7. 收尾跑测试

## 引用
- references/refactoring-rules.md（坏味道 → 手法 → 测试保护 → PR 拆分）
- references/checklists.md（Refactor Checklist）
- references/stage-playbook.md（Stage 9）

## 完成判定
- [ ] 行为不变（测试为证）
- [ ] 边界变化已同步文档
```

### debug-incident.md

```md
# Prompt: Debug Incident（救火）

## 何时用
- 生产/UAT 出问题
- 用户说"挂了 / 错了 / 不工作了"

## 步骤
1. 先恢复（回滚 / feature flag / 临时绕过）
2. 复现路径：最小重现
3. 定位 root cause（log + trace + diff 最近变更）
4. 修复 + 加 regression test
5. 写 post-mortem 入 `docs/post-mortems/`（建议而非强制）
6. 更新 patterns.md「反模式」（如果是模式问题）

## 引用
- references/checklists.md（Bug Fix Checklist）
- references/architecture-cases.md §11（可观测性）

## 完成判定
- [ ] 已恢复
- [ ] regression test 已加
- [ ] root cause 已记录
```

### capture-lesson.md

```md
# Prompt: Capture Lesson（捕获用户纠偏到 L1）

## 何时用
本轮对话出现以下捕获信号（详见 SKILL.md「Knowhow 沉淀规则」）：
- 用户否定 / 纠偏：「不对」「应该是」「错了」
- 经验补充：「这种情况要…」「你忘了…」「我之前是…」
- 反例提供：「踩过这个坑」「上次就是这样挂了」
- 选型推翻：「不要 X 要 Y，因为…」
- 流程纠偏：「这一步不该现在做」「先 X 再 Y」

## 我需要的输入
- 当前对话场景（一句话脱敏描述，如「Stage 3 给电商商家后台采集方案」）
- agent 之前的方案 / 推断（错的）
- 用户给的正确方案 / 反例
- 用户提示的原因或限制条件
- 是否跨项目可复用

## 我会交付
- 一条 lesson 卡片，按 `lessons.md` 模板格式
- 编号 L-NNNN（在 `lessons.md` 现有最大编号 +1）
- 多标签 Tag（从 `lessons.md` Tag 词表挑）
- 是否触发 promotion 提议（同主题 lesson ≥ 2 条 → 建议走 promote-pattern）

## 步骤
1. 抽取「之前的错误方案」「正确方案」「原因 / 适用条件」三段，每段不超过 2 句话。
2. 按 `lessons.md` Tag 词表打标签——多标签用逗号，标签必须在词表里。
3. 判断「是否可泛化」三选一：跨项目 / 仅特定项目 / 仅特定场景。
   - 仅特定项目 → **不写到 lessons.md**，建议写到该项目自己的 `docs/memory-bank/patterns.md`。
4. 检查反模式：个人偏好 / 与 reference 重复 / 项目特定 / 含敏感数据 / 多意图 / 无原因 → 任一命中拒绝写入。
5. 在 `lessons.md` 最末尾追加新条目，编号连续。
6. 检查同 Tag + 同主题的 active lesson 是否已有 ≥ 1 条 → 触发 promote-pattern 提议。

## 引用的 references
- references/lessons.md（模板、Tag 词表、反模式）
- SKILL.md「Knowhow 沉淀规则」一节

## 输出格式
- 单条 lesson 的完整 markdown（直接可追加到 lessons.md）
- 末尾附一行：`Promotion 候选: <是 / 否> + 理由`

## 完成判定
- [ ] 用户已确认这条 lesson 措辞准确
- [ ] 编号 L-NNNN 连续，无跳号
- [ ] Tag 全部在词表内
- [ ] 「适用条件」字段非空
- [ ] 已写到 lessons.md（agent 输出 diff 给用户审）
```

### promote-pattern.md

```md
# Prompt: Promote Pattern（L1 → L2 → L3 升级）

## 何时用
- L1 → L2：同主题 lesson ≥ 2 条 / 用户说「这是通用模式」/ lesson 在新会话被复用 ≥ 2 次。
- L2 → L3：pattern 与某 reference 核心结论冲突 / pattern 在多项目验证 / pattern 累计被引用 ≥ 3 次且无反例。

## 我需要的输入
- 升级方向：L1→L2 还是 L2→L3
- 源条目：lesson IDs（L-NNNN, ...）或 pattern ID（P-NNNN）
- 升级理由（命中哪条触发条件）
- 反例排查结果（有没有反例推翻？）

## 我会交付

### L1 → L2 时
- 一条 pattern 卡片，按 `patterns-skill.md` 模板格式
- 编号 P-NNNN（连续）
- Source lessons 字段填全部源 L-NNNN
- 决策矩阵（如果多条 lesson 描述同一选型在不同场景下不同推荐）
- 反例 / 不适用 字段必填
- 在每条源 lesson 卡片末尾的「🔗 相关」加 `Promoted to: P-NNNN`

### L2 → L3 时
- PR 草稿：要修改的 reference 文件 + 具体段落 + 新文案
- PR 描述里链接 P-NNNN 与全部源 L-NNNN
- pattern 卡片更新 `Status: promoted-to-reference`，写明 reference 段落
- 新会话的默认行为切换：reference 优先 > pattern

## 步骤

### L1 → L2
1. 列出所有候选源 lesson（同 Tag + 同主题）。
2. 抽取共同规律（不是简单合并文字，而是抽 "什么场景 / 什么信号 / 什么推荐 / 什么反例"）。
3. 写「适用条件」「反例 / 不适用」「模式描述」「决策矩阵」。
4. 反模式自查：是否只是 lesson 复制粘贴 / 缺反例 / 缺适用条件 / 与 reference 冲突未标。
5. 在 `patterns-skill.md` 末尾追加，编号连续。
6. 回到每条源 lesson 加 `Promoted to: P-NNNN`。

### L2 → L3
1. 定位要修改的 reference 文件 + 段落（pattern 影响的就是这里）。
2. 反例排查：在所有 active lesson / pattern 中检索是否有反例 → 有反例则不升级。
3. 起草 PR：reference 修改 + 关联 P-NNNN + 关联 L-NNNN。
4. PR 合并后回写 pattern 卡片状态为 `promoted-to-reference`。
5. **不删 lesson / pattern**（保留考古回溯）。

## 引用的 references
- references/patterns-skill.md（pattern 模板、promotion 流程）
- references/lessons.md（promotion 触发条件、L1 → L2 流程）
- SKILL.md「Knowhow 沉淀规则」

## 输出格式
- L1 → L2：完整 pattern 卡片 + 源 lesson 更新 diff
- L2 → L3：PR 草稿（标题、描述、reference 修改 diff）

## 完成判定
- [ ] 升级触发条件已显式列出（命中哪条）
- [ ] 反例排查已做
- [ ] 源条目状态已更新（lesson 加 Promoted to / pattern 加 promoted-to-reference）
- [ ] 编号连续
- [ ] 不删除任何源条目
```

### spike-start.md

```md
# Prompt: Spike Start（启动 POC / Spike）

## 何时用
- 用户说 POC / spike / demo / sandbox / 试一下 / 一次性脚本
- 生命周期 < 1 周、单人开发、不进生产、不接真实敏感数据
- 目标是回答一个明确的可行性问题

## 我需要的输入
- 要验证的具体问题（一句话）
- 验收信号：什么结果算 "可行"，什么结果算 "不可行"
- 数据来源（脱敏样本 / mock / 公开数据）
- 时间盒（建议 ≤ 5 个工作日）

## 我会交付
- `README.md`（POC 问题、运行方式、结论位置）
- `.gitignore`（output / runtime / data / secret 全 ignore）
- 依赖声明（requirements.txt / pyproject.toml / package.json）
- `docs/spike-note.md`（假设、方案、样本、结论、是否升级）
- 可重复运行的 smoke command
- 升级判断：是否命中升级触发条件

## 步骤
1. 确认时间盒与升级触发条件已对齐用户。
2. 落地 4 份最小文件（README / .gitignore / 依赖 / spike-note）。
3. 写 smoke command，先确保能跑通最小路径。
4. 实施验证，把假设、方法、样本、结果填回 spike-note。
5. 收尾：给结论（可行 / 不可行 / 需二次验证）+ 证据 + 下一步（废弃 / 归档 / 升级）。
6. 任一升级触发条件命中 → 立即停止 POC 模式，切回 `scaffold-new-project`。

## 引用的 references
- references/scenario-playbooks.md §G（POC / Spike 轻量模式 + 升级触发）
- references/stage-playbook.md Stage P
- references/checklists.md（POC / Spike Checklist）

## 输出格式
工程路由模板，`工程路由` 或 `项目形态` 注明 `POC/Spike`，`停止条件` 必须包含升级触发条件。

## 完成判定
- [ ] 4 份最小文件已落地
- [ ] smoke command 可重复运行
- [ ] spike-note 有结论和证据
- [ ] 升级判断已显式给出（是 / 否 + 命中哪条）
```

### scenario-routing.md

```md
# Prompt: Scenario Routing（业务场景路由）

## 何时用
- 用户描述命中业务自动化场景：RPA / 数据采集、OCR / 文档智能、视觉 / 多媒体质检、数据治理 / 分析报表、LLM 生产链路、浏览器自动化 / WebAgent。
- 信号词：电商后台、千牛 / 京麦 / 抖店、PDF / 发票 / 合同、图像质检、经营报表、prompt 多版本、Playwright / Selenium 等。

## 我需要的输入
- 当前阶段（用 SKILL.md 工程路由模板先判断）
- 项目形态（已选 / 待定）
- 命中的场景（从 scenario-playbooks 表里挑 1 条，或 `Unknown`）
- 是否已有 design doc / ADR

## 我会交付
- 命中场景的最小切片清单（直接来自 scenario-playbooks 对应小节）
- 默认技术选型 + 不推荐反例 + 退出成本
- design doc 必写章节
- 验证门禁与反模式
- 是否需要补 ADR（架构维度变化时）

## 步骤
1. 在 `scenario-playbooks.md` 场景速查表里定位场景小节（A–G）。
2. 把该小节的「最小切片」「Design Doc 必写」「验证门禁」「反模式」抽出来。
3. 如果场景涉及架构维度（LLM 调用方式、RAG、Prompt 管理、向量库等）→ 同步指向 `architecture-cases-ai.md` 对应大类，**不复制内容**。
4. 把场景信息写进 工程路由模板的 `工程路由` 和 `项目形态` 字段，例如：`工程路由: Scenario | OCR / 文档智能 | Architecture`、`Python Agent/CLI（场景：OCR / 文档智能）`。
5. 校对 checklists.md 对应场景 checklist；缺失项进入 `缺失内容`。

## 引用的 references
- references/scenario-playbooks.md（首选）
- references/architecture-cases-ai.md（命中 LLM / Agent 架构维度）
- references/checklists.md（场景 Checklist）
- references/spec-templates.md → templates-specs.md（design doc 模板）

## 输出格式
工程路由模板，`工程路由` 与 `项目形态` 必须带场景标签；`下一步 3 个动作` 至少包含「补齐场景 design doc 必写章节」与「跑场景 checklist」各 1 条。

## 完成判定
- [ ] 场景已定位到 scenario-playbooks 具体小节
- [ ] 最小切片 / 默认选型 / 验证门禁 / 反模式 已抽到回答里
- [ ] 架构维度变化已明确是否需要 ADR
- [ ] 场景 checklist 已跑或已记入 `缺失内容`
```

---

## prompts/README.md（索引）

每个项目的 `docs/prompts/README.md` 应该列出可用 prompt 与触发信号：

```md
# Prompts Index

| Prompt | 触发信号 |
|---|---|
| lifecycle-aliases | `/spec` / `/plan` / `/build` / `/test` / `/review` / `/ship` / `/learn` |
| avatar-aliases | `/interview` / `/onboard` / `/org` / `/sop` / `/estimate` / `/artifact` / 面试 / 入职 / 组织企业 SOP / 非工程估算 / 非软件开发 |
| scaffold-new-project | 新 repo / 空目录 / "怎么搭" |
| spike-start | POC / spike / demo / 一次性脚本 / 试一下 |
| handover-audit | 接手 / 老代码 / "怎么继续" |
| new-feature | 加功能 / 加页面 / 加 API |
| scenario-routing | 命中 RPA / OCR / 视觉 / 数据治理 / LLM 生产链路 / 浏览器自动化 |
| new-design-doc | 要 PRD / design doc |
| new-adr | 选库 / 改边界 / 改模式 |
| pre-pr | 准备提交 / ship |
| update-active-context | 会话结束 / 重要进展后 |
| refactor-safely | 重构 / 清理 / 重命名 |
| debug-incident | 挂了 / 错了 / 救火 |
| capture-lesson | 用户说"不对/应该是/错了/我之前是/不要 X 要 Y" |
| promote-pattern | 同主题 lesson ≥ 2 / 用户说"这是通用模式" / pattern 影响 reference 核心结论 |
```

## 与 SKILL.md 决策树的关系

prompts 是**决策树命中后的"操作手册"**，不替代 SKILL.md 的路由：

```
用户请求
  → SKILL.md 决策树（命中第几条 + 阶段判断）
    → 找到对应 prompt（如 scaffold-new-project）
      → prompt 路由到具体 references
        → 输出 工程路由模板 + 产物
```

> 项目可在自家 `docs/prompts/` 覆盖或新增。本 Skill 提供基线模板。

## 反模式

- prompt 把 references 内容复制进来 → 双份维护必漂移。
- prompt 写成长篇散文 → agent 难解析。
- 一个 prompt 包含多个意图 → 拆成多个。
- 不更新 prompts/README.md 索引 → 写了没人知道。
- 把敏感凭证 / 客户数据写进 prompt → 会被 agent 多次读到。
