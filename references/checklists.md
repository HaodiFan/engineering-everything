# Checklists

用于验证、PR readiness 和反模式检查。

## 通用验证

优先运行最小相关验证。

```bash
git diff --check
```

前端：

```bash
pnpm typecheck
pnpm build
pnpm test
```

Python 后端：

```bash
ruff check .
pytest
alembic upgrade head
```

桌面端：

```bash
pnpm --dir apps/desktop typecheck
pnpm --dir apps/desktop build
```

Python Agent / CLI：

```bash
ruff check .
pytest
python -m <package> --help
```

Library / SDK：

```bash
pytest
npm test
npm run build
```

如果命令不可用，报告：

- 尝试或跳过的命令
- 为什么无法运行
- 不运行造成的风险
- 建议后续动作

### Source-driven 验证

命中新依赖、外部 API、平台规则、框架升级、鉴权/支付/合规时，验证结果必须包含：

- [ ] 项目内锁定版本、ADR、README、官方 SDK 类型或官方文档来源。
- [ ] 版本 / 日期 / 适用范围。
- [ ] 哪些结论来自来源，哪些是 agent 推断。

---

## 需求文档完备性 Checklist（Stage 1 用）

> Agent 收到用户给的需求文档后，按这套清单校验。**全过才进 Stage 2**。

### 必须项（任何一项缺失 → 退回用户补）

- [ ] 业务背景：能解释"为什么做"
- [ ] 目标用户：至少 1 类用户的场景与痛点
- [ ] PSPS：Persona / Scenario / Pain / Solution Surface 已能解释系统闭环
- [ ] 业务目标：1 句话目标 + 至少 1 个可量化成功指标
- [ ] P0 功能列表：每条带验收标准
- [ ] 非目标：明确这一版不做什么
- [ ] 关键约束：合规 / 性能 / 时间 / 预算 至少一项明确
- [ ] Owner：可对接的负责人

### 应有项（缺失但可推迟）

- [ ] P1 / Later 列表
- [ ] 已知风险
- [ ] 与现有系统的关系

### 危险信号（命中任一 → 立即提问，不要往下做）

- [ ] 出现"差不多就行 / 你看着办 / 行业标准"等模糊词，且不肯具体化
- [ ] 验收标准全是主观词（好用、流畅、漂亮）
- [ ] P0 列表超过 10 条且无优先级
- [ ] 非目标为空
- [ ] 成功指标不可量化或无截止时间
- [ ] 性能/合规约束与所选架构明显冲突
- [ ] 只有功能愿望，没有 Persona / Scenario / Pain 的证据

### Agent 输出格式

```text
需求文档完备性: <PASS | NEEDS-USER-INPUT | BLOCKED>
缺失必须项: <逐条列出>
建议补充项: <逐条列出>
需用户回答的问题: <编号列表>
可继续推进的部分: <如可先做架构选型部分>
```

---

## 新项目 Checklist（Stage 4 完成判定）

### 必备（任何项目）

- [ ] 已写项目一句话定义。
- [ ] 已选择项目形态。
- [ ] `README.md` 存在。
- [ ] `ARCHITECTURE.md` 存在，记录所有关键架构决策（交叉引用 ADR）。
- [ ] `DEVELOPMENT.md` 存在。
- [ ] `BRANCHING.md` 存在并已生效（团队已知）。
- [ ] `BRANCHING.md` 已写明 checkout/worktree 策略：何时必须 worktree、何时可直接开发、脏工作区如何处理。
- [ ] `CONSTITUTION.md` 存在（红线 v0.1）。
- [ ] `AGENTS.md` 存在（明示先读 active-context + Constitution）。
- [ ] `docs/requirements/requirements-v0.0.1.md` 存在（来自用户）。
- [ ] `docs/design/active/design_doc-v0.0.1-bootstrap.md` 存在；`backlog/` 与 `done/` 目录已建立（可空）。
- [ ] `docs/decisions/ADR-0001-record-architecture-decisions.md` 存在。
- [ ] `docs/governance/folder-declaration-v0.md` 存在。
- [ ] `docs/governance/changelog.md` 存在。
- [ ] `.env.example` 存在，真实 secret 已 ignore。
- [ ] bootstrap script 存在。
- [ ] 最小 app/service/CLI 可以运行。

### UI 类项目额外

- [ ] `DESIGN.md` 存在（design tokens + 组件清单 + 交互模式）。
- [ ] `docs/design/layout-spec-<page>.md` 存在（首页或核心页）。

### Agent 协作项目额外

- [ ] `docs/memory-bank/brief.md` / `tech-context.md` / `patterns.md` / `active-context.md` 四件套存在（参考 `memory-bank-guide.md`）。
- [ ] `docs/prompts/README.md` 存在，至少含基线 prompt（参考 `prompts-guide.md`）。

### AI / LLM 项目额外

- [ ] LLM 调用统一 client 已就位（红线 §6 项可勾）。
- [ ] `prompts/` 目录已建立（与 `docs/prompts/` 区分：`prompts/` 是运行时 prompt 文件，`docs/prompts/` 是 agent 操作手册）。
- [ ] eval baseline 计划已写（即使未实施）。

---

## POC / Spike Checklist

适用于生命周期短、单人验证、未进生产的临时验证。命中任一升级触发条件，停止 POC 模式，切回正式项目流程。

### POC 最小必备

- [ ] `README.md` 写清要验证的问题、运行方式、结论位置。
- [ ] `.gitignore` 覆盖 `output/`、`runtime/`、`logs/`、`uploads/`、`temp_*`、真实数据目录。
- [ ] 有依赖声明（`requirements.txt` / `pyproject.toml` / `package.json`）。
- [ ] 有 `docs/spike-note.md` 或等价文档，记录假设、样本、方法、结果、是否升级。
- [ ] 样本数据脱敏；真实 token/cookie/客户数据不入仓。
- [ ] 有一个可重复运行的 smoke command。

### 升级触发

> 升级触发条件的真相源在 `scenario-playbooks.md` §G「POC / Spike 轻量模式 → 升级触发」。本处只列检查项，避免双份维护。

- [ ] 已对照 `scenario-playbooks.md` §G 的升级触发条件全部检查（任一命中 → 立即停止 POC 模式，切回正式项目流程）。

## 场景 Checklist

命中具体业务场景时，读取 `scenario-playbooks.md` 后做最小自检。

### RPA / 数据采集

- [ ] 中国电商场景已先确定平台：淘宝系 / 京东 / 拼多多 / 抖音。
- [ ] 已区分数据源类型：公域数据 / 商家管理后台 / 客户自有系统。
- [ ] 公域数据已记录合法性、授权边界、平台 ToS 风险；逆向/抓包默认不作为推荐路径。
- [ ] 商家后台数据已优先评估官方 API、后台导出、异步报表下载能力。
- [ ] 商家后台浏览器自动化已评估 `undetected-chromedriver` + Selenium，不默认使用 plain Chromium。
- [ ] 浏览器自动化 selector 有集中维护策略；中国电商后台优先 XPath + 文本/层级锚点。
- [ ] 动作频率有 bounded random sleep、任务级 rate limit、明确等待条件和失败重试上限。
- [ ] 手机 RPA 方案已说明设备/账号授权、节流、截图/录屏证据、失败状态和人工接管。
- [ ] 手机 RPA 默认使用 Appium + ADB/iOS automation，并说明设备池和账号状态管理。
- [ ] 数据来源、授权边界、平台 ToS 风险已记录。
- [ ] API / 自动化 / OCR / 抓包等方式的选择理由已写清。
- [ ] raw 证据、标准化结果、分析结果分层。
- [ ] 登录失效、限流、页面变更、空数据有失败态。
- [ ] 不提交 cookie、客户数据、导出的敏感原始数据。

### OCR / 文档智能

- [ ] 输出 schema 先于模型实现。
- [ ] 已判断 OCR 是后台基础能力还是核心能力。
- [ ] 已记录服务器规格和并发预算；2C2G/2C4G 低配后台优先轻量 OCR，不默认引入 PaddleOCR。
- [ ] 如选择 PaddleOCR，已有理由：准确度要求高、中文复杂版面、表格/版面恢复或 OCR 是核心能力。
- [ ] page image / OCR blocks / extracted fields / reviewed result 分层。
- [ ] 关键字段有置信度、来源页码/bbox、校验或人审。
- [ ] 至少 3 个真实样本 fixture 或脱敏样本。

### 视觉 / 多媒体质检

- [ ] 标注 schema 是真相源，先于模型实现。
- [ ] 媒体资源不入 repo（图片/视频/截图全在仓外或 LFS / 对象存储）。
- [ ] resourceId → fileUrl 映射独立存储，模型输出与人审结果分层。
- [ ] 标注坐标系（归一化 vs 显示）双向一致并有测试。
- [ ] 大图、缺失资源、错误 MIME、跨域、视频截帧失败均有错误态。
- [ ] 模型输出按 candidate 处理，人审决定是否落库。
- [ ] 至少 1 套版本/快照机制可回滚。

### 数据治理 / 分析报表

- [ ] 中国电商场景已先确定平台（淘宝系 / 京东 / 拼多多 / 抖音）与数据源类型（公域 / 商家后台 / 客户自有）。
- [ ] OLTP 与分析存储分离：报表/分析走只读副本、数仓或物化表，不直查业务库。
- [ ] 来源系统未声明为真相源前不写入 dashboard；source priority、冲突规则、更新频率已记录。
- [ ] 数据分层 raw / staging / mart / dashboard 清晰，每层有 owner。
- [ ] 每个指标都有口径、过滤条件、更新时间、owner，先定义后做页面。
- [ ] 增量同步、重跑、补数策略已写进 design doc。
- [ ] 数据新鲜度和失败状态对消费方可见（不是只在 ETL 内部报错）。

### 浏览器自动化 / WebAgent 数据

- [ ] 浏览器状态可复现：viewport、device scale、cookie、headers、UA、时间戳全记录。
- [ ] 截图、DOM、网络证据分开存储，不只留截图。
- [ ] selector / 布局 / 滚动 / 懒加载有失败探测；selector 集中维护。
- [ ] 同一 URL 重跑结果差异可解释；不可访问 / 超时 / 重定向 / 反爬有状态区分。
- [ ] 长页面截图、懒加载、登录态切换有用例覆盖。
- [ ] 临时截图、缓存、下载目录已在 `.gitignore`，不污染 repo。
- [ ] robots / llms.txt / sitemap 等可发现性数据有结构化输出。

### LLM 生产链路

- [ ] AI 任务已先按目标分流到经典场景：NLP 分类/抽取、CV 检测/分割/理解、统计/时序、LLM/Agent 混合。
- [ ] 已按成本、时效、效果、流量、私有化要求选择经典算法 / 经典算法 + LLM/VLM 兜底 / 纯 LLM/VLM。
- [ ] LLM/VLM 成本已按单次调用估算；高流量任务（如 100000/day 量级）已避免默认纯 API LLM。
- [ ] NLP 分类/抽取已评估 Level 1 规则/正则、Level 2 PaddleNLP 零样本、Level 3 BERT/PaddleNLP、Level 4 LLM 兜底。
- [ ] 没有数据集但要快速落地的 NLP 任务，可用 LLM prompt baseline；长期/私有化/低预算任务需验证 BERT/PaddleNLP。
- [ ] CV 固定识别/检测优先 YOLO；精准分割优先 YOLO-seg；通用分割/辅助标注可用 SAM；图像理解用 VLM。
- [ ] 图像语义比对已评估 image embedding + 向量库；VLM 只做开放理解/兜底解释，不替代高精度检测/分割。
- [ ] 统计/时序任务已建立 XGBoost/LightGBM 或领域 SOTA baseline；LLM 只做解释报告或 Agent 调工具做 chat analysis。
- [ ] 分类/抽取任务有标签集、schema、字段校验和字段级评估；CV 有标注 schema 与 accuracy/mAP/IoU/recall；时序有 backtest 与 MAE/MAPE/RMSE。
- [ ] prompt 有 ID、版本、默认指针和回滚路径。
- [ ] 每次调用记录 provider/model/prompt_version/token/latency/error。
- [ ] 结构化输出有 schema 校验和失败重试策略。
- [ ] 失败样例进入 eval 或 replay 用例库。
- [ ] streaming 场景定义 first chunk、chunk idle、total timeout。

---

## Feature Checklist

- [ ] 已有关联 design doc，并位于 `docs/design/active/`（开工前从 `backlog/` 移过来）。
- [ ] design doc 关联了 requirements doc 和（如有）相关 ADR。
- [ ] 已有关联 requirements doc。
- [ ] Scope 和 non-goals 明确。
- [ ] 已识别影响目录。
- [ ] 数据、状态、API、UI 变化已写清。
- [ ] **不触 `CONSTITUTION.md` 红线**；触红线则已走豁免/修改流程。
- [ ] 触动架构维度的决策已开 ADR（或更新现有 ADR）。
- [ ] UI 改动：layout spec 已更新或新增。
- [ ] UI 改动：所选组件全部在 `DESIGN.md` 内；新组件已先入 `DESIGN.md`。
- [ ] 有测试或验证计划。
- [ ] 新依赖、外部 API、框架升级、平台规则、鉴权/支付/合规等已按 `agent-operating-standards.md` 走 source-driven gate。
- [ ] 已判断是否需要 changelog。
- [ ] 实现已拆成 vertical slices。
- [ ] 多步 feature 已按 `execution-pipeline.md` 输出 implementation plan。
- [ ] 已按 `execution-pipeline.md` 判断 checkout/worktree；多 agent / 多任务并行已使用独立 worktree 和 disjoint write set。
- [ ] 每个 slice 已标 validation gate 和命中的 review roles。
- [ ] `docs/memory-bank/active-context.md` 已写当前焦点（agent 协作项目）。

---

## Implementation Plan Checklist（Stage 5）

- [ ] Goal 是用户可观察行为，不是技术动作。
- [ ] PSPS 已写清：谁用/谁管、什么场景、解决什么痛点、需要什么系统表面。
- [ ] 管理者视角有统计/状态/指标口径；执行者入口只保留必要字段。
- [ ] Source docs 已链接 requirements / design doc / ADR / layout spec（如有）。
- [ ] Source-driven evidence 已列出：新依赖、外部 API、平台规则、框架升级等用到的官方或项目内来源。
- [ ] Checkout / worktree 决策已说明；如并行开发，写明每个 worktree / agent 的写入范围。
- [ ] Scope / Non-goals 明确。
- [ ] File Map 列出新建/修改文件及责任边界。
- [ ] Change size 已评估；预估大于 500 行时有拆分策略或不拆理由。
- [ ] Vertical slices 可单独验证，不只是“后端/前端/测试”分层。
- [ ] 每个 slice 有 validation gate：后端/API/单元/集成/契约测试命令、样本、人工验收或 replay/eval。
- [ ] 每个 slice 标出需要的 review roles（Product / Eng / Design / DX / Code / QA / Security / Release）。
- [ ] Rollback / fallback 已说明。
- [ ] 没有 TODO / TBD / “适当处理边界情况” 这类占位。

---

## Review Pipeline Checklist（Stage 7-8）

- [ ] Product / CEO Review：目标、P0、非目标和范围没有漂移（命中产品/范围变化时）。
- [ ] Eng / Architecture Review：owning layer、ADR、数据流、状态机、权限边界已检查（命中架构变化时）。
- [ ] Design Review：DESIGN.md、layout spec、响应式、可访问性已检查（命中 UI 时）。
- [ ] DX Review：API / CLI / SDK / docs 的首次使用路径和错误信息已检查（命中开发者体验时）。
- [ ] Code Review：已按 `code-review-standards.md` 检查坏味道、行为风险、secret/hardcode。
- [ ] QA Review：优先后端/API/service 自测；端到端用户流、失败态和回归路径有证据。
- [ ] Security / Compliance Review：鉴权、PII、secret、平台 ToS、自动化授权边界已检查（命中高风险时）。
- [ ] Release Review：PR body、CI、changelog、迁移顺序、回滚方式已检查（准备发布时）。

---

## Browser QA Checklist（显式触发）

默认不要用浏览器模拟代替后端自测。只有用户明确要求，或任务本身就是浏览器/RPA/前端交互能力，或问题只能在真实浏览器复现时，才跑本 checklist。

触发前先确认：

- [ ] 已优先运行后端/API/service/contract/fixture/replay 等最小相关验证，或说明为什么无法运行。
- [ ] 浏览器模拟的触发原因已写明：用户要求 / 产品能力本身 / 浏览器特有 bug / release gate。

- [ ] 已记录目标 URL / 本地页面、viewport、登录态、测试账号或脱敏身份。
- [ ] 核心用户流已走通：打开、填写、提交、刷新、错误态、权限态。
- [ ] console error、network failure、loading/empty/error state 已检查。
- [ ] 已保存截图，或说明无法截图的原因。
- [ ] 响应式页面至少检查一个窄屏 viewport。
- [ ] RPA / 电商后台已保留截图、HTML 或 raw payload 证据层。
- [ ] 登录失效、验证码、限流、页面改版有失败态和人工接管说明。

---

## Bug Fix Checklist

- [ ] 已理解复现路径。
- [ ] 已识别 root cause 或明确假设。
- [ ] 可行时已添加 regression test。
- [ ] 修复足够小且局部。
- [ ] 用户可见行为变化已记录。

---

## Refactor Checklist

- [ ] 明确不改变行为。
- [ ] 已按 `refactoring-rules.md` 识别具体坏味道，不做泛清理。
- [ ] 已选择对应重构手法，并说明为什么适用。
- [ ] 已有测试或 smoke checks 覆盖被移动代码。
- [ ] 未混入 feature、bug fix、format、dependency upgrade 或 migration。
- [ ] 大于 500 行、跨模块或影响公共 API 时已拆 PR 或说明不可拆理由。
- [ ] 如果边界变化，已更新 architecture 或 folder declaration。
- [ ] 公共 API 保持兼容；不兼容时写 migration notes。

---

## PR Readiness

- [ ] Diff 聚焦一个 topic。
- [ ] 当前 checkout/worktree 决策符合 `BRANCHING.md`；单 PR follow-up 或小修直接开发时，当前分支就是目标分支。
- [ ] Diff size 符合 `agent-operating-standards.md` 的 change size rules；大 PR 已拆分或解释例外。
- [ ] 没有无关格式化噪音。
- [ ] 没有混入用户未提交改动；如保留无关脏文件，PR body 或收尾说明已列出。
- [ ] 没有提交生成文件或运行时文件。
- [ ] 新依赖、外部 API、平台规则、框架升级、鉴权/支付/合规的 source-driven evidence 已写进 PR body 或关联文档。
- [ ] 已按 `references/code-review-standards.md` 检查代码坏味道、潜在行为风险、密钥/硬编码风险。
- [ ] 已按 `references/execution-pipeline.md` 跑完命中的 Review Pipeline roles。
- [ ] 已优先运行后端/API/service/contract/fixture/replay 等最小相关验证。
- [ ] 浏览器模拟仅在用户要求、产品能力本身、浏览器特有 bug 或 release gate 命中时运行；未命中则无需 Browser QA 证据。
- [ ] **`CONSTITUTION.md` 红线 0 触发**（或已走豁免流程并在 PR body 注明）。
- [ ] Design doc 已关联，状态正确（feature 完成时已从 `active/` 移到 `done/` 并回填 `Validation Results`）。
- [ ] requirements doc、架构文档已同步。
- [ ] 架构维度变更：对应 ADR 已新建/更新。
- [ ] UI 改动：DESIGN.md / layout spec 已同步。
- [ ] 验证命令结果明确。
- [ ] 风险和回滚方式已说明。
- [ ] 分支与提交信息符合 `BRANCHING.md`。
- [ ] `docs/memory-bank/active-context.md` 已更新（agent 协作项目）。

---

## Constitution 红线触发处理 Checklist

agent / 开发者发现自己的实现**会**触线时：

- [ ] **立刻停下**，不要"绕路实现"（绕路通常等于偷偷违反）。
- [ ] 在 PR / 对话中明示触发哪条（例 `Constitution §2 架构边界`）。
- [ ] 给三种路径供用户选择：
  - (a) **改方案规避**：调整实现方式，红线不变。
  - (b) **提议放宽红线**：开 PR 修改 `CONSTITUTION.md`，至少 2 名维护者批准。
  - (c) **临时豁免**：由 owner 批准，明确截止时间和补救计划，记入 changelog。
- [ ] 由 owner 决策，不要 agent 自行选路径。

> 红线之外的"觉得不太好"不是触线，走 `DEVELOPMENT.md` / patterns.md 路线沟通。

---

## Skill Knowhow Hygiene Checklist（每次会话末，agent 自检）

> 让 skill 自我进化：用户每次纠偏都被结构化捕获到 `references/lessons.md`（L1）；多条同主题 lesson 合并到 `references/patterns-skill.md`（L2）；pattern 验证够多后开 PR 升级到对应 reference（L3）。详见 SKILL.md「Knowhow 沉淀规则」。

### 会话开始时

- [ ] 已按本次任务的阶段 / 形态 / 场景 / 架构维度，用 Tag 检索 `lessons.md` 与 `patterns-skill.md` 的 active 条目。
- [ ] 命中的 active lesson / pattern 已写进方案约束，并在回复里显式引用 `L-NNNN` / `P-NNNN`。

### 会话进行中

- [ ] 用户回复包含捕获信号（不对 / 应该是 / 错了 / 我之前是 / 不要 X 要 Y / 这一步不该现在做）→ 在该轮回复末尾追加「📌 是否捕获 lesson」提议。
- [ ] 信号弱 / 单纯澄清 / 闲聊 → 不硬捕获。

### 会话结束时

- [ ] 触发了捕获信号且用户确认 → 按 `lessons.md` 模板追加 L-NNNN（连续编号）。
- [ ] Tag 全部在 `lessons.md` Tag 词表内。
- [ ] 「适用条件」「是否可泛化」字段非空。
- [ ] 同 Tag + 同主题 active lesson ≥ 2 条 → 提议 L1 → L2 promotion。
- [ ] 单条 lesson 是「仅特定项目」→ **不**写到 `lessons.md`，引导用户写到该项目自己的 `docs/memory-bank/patterns.md`。

### 反模式（agent 不要写进 lessons / patterns）

- [ ] 不把个人偏好当 lesson。
- [ ] 不把 reference 已有结论复述成 lesson。
- [ ] 不把项目特定写法写到 skill 级 lessons.md。
- [ ] 不写秘密 / 客户名 / token / 真实数据。
- [ ] 一条 lesson 一个意图（多意图拆条）。
- [ ] 没有「原因 / 适用条件」的 lesson 拒绝写入。
- [ ] pattern 没有「反例 / 不适用」字段拒绝合并。

---

## Memory Bank Hygiene Checklist（agent 协作项目）

每次会话结束前，agent 自检：

- [ ] `active-context.md` `Last updated` 已刷。
- [ ] 已完成 / 进行中 / 下一步 / 给下一会话留言 全部更新（"留言"必须具体，不写"继续"）。
- [ ] 阻塞与决策待定已列。
- [ ] 发现新 pattern / 反模式 → **提议**更新 `patterns.md`（不擅自改）。
- [ ] 发现 `tech-context.md` 与代码现实漂移 → 提议更新。
- [ ] 没把密钥 / 客户名单 / 内部链接（含 token 的）写进 memory-bank。

---

## 常见反模式

- 行为不明确时先写代码、后补 spec。
- 把“我觉得这个很小”当成跳过验收标准、验证和 source check 的理由。
- 多份互相竞争的真相源文档。
- agent 替用户编造业务需求，没有 Requirements Doc 就直接做 design doc。
- 跳过架构决策直接搭脚手架，导致后续选型被既成事实绑架。
- 分支规范延后到第一次 PR 才讨论，已有 commit 不符合规范。
- 写代码再补 layout，组件各自发明而不查 DESIGN.md。
- router/controller 堆核心业务逻辑。
- 前端页面各自发明局部设计系统。
- 前后端重复定义不兼容类型。
- 未明确决策就把外部平台当产品数据库。
- 把 runtime data 提交进 repo。
- 一个分支混合 feature、refactor、docs、依赖升级、格式化。
- 在脏工作区直接开写，或擅自 stash/revert 用户改动。
- 多 agent / 多任务共写一个 checkout，导致 diff 互相覆盖。
- 大 diff 不拆分，也不说明为什么必须保持一个 PR。
- 新依赖、外部 API 或平台规则只凭记忆实现，没有官方来源或项目内锁定版本依据。
- AI 生成代码后不验证。
- PR 不写风险和验证方式。
- 接手项目立刻"重构整理"，破坏现有约定。
- `CONSTITUTION.md` 写成"代码风格 / 一般最佳实践"大杂烩，触线变成"风格不统一"，红线失效。
- design doc 全堆在 `docs/design/` 一层，没有 lifecycle，agent 看不出哪份还有效。
- ADR 写成"我们决定用 X"一句话，没有 Options Considered 与 Consequences，未来无法回溯。
- Memory Bank 把 `ARCHITECTURE.md` 全文复制进 `tech-context.md` → 双份维护必漂移。
- `active-context.md` 多会话不更新 → agent 基于过期信息工作。
- 把密钥 / 客户名单 / 内部链接写进 memory-bank → 它会被 agent 多次读到。
- prompts 写成长篇散文，agent 难解析；或一个 prompt 包含多个意图。
- 用户给出明确纠偏后 agent 不捕获到 `lessons.md`，下次同类问题再犯同样错。
- 把项目特定写法写进 skill 级 `lessons.md`，污染跨项目知识库（应进项目自己的 `docs/memory-bank/patterns.md`）。
- 把"个人偏好 / 未验证假设"当 lesson 写进 `lessons.md`，让未来 agent 误信。
- pattern 与 reference 冲突但不标 promotion 状态，形成双份真相源。

---

## "下一步做什么"输出 Checklist

当用户问下一步时，输出 工程路由模板（与 SKILL.md 统一）：

```text
工程路由:
当前阶段:
项目形态:
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```
