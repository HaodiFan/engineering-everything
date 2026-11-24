# Review 逐条方法论规则目录（6 大维度 / 50 条 RV-*）

本文件把开发后 Review 聚类为 **3 个执行阶段、6 个业务可读的核心维度（MECE）、50 条带稳定编号的原子规则（`RV-*`）**（含 L4/L5 产品认知与用户旅程规则 `RV-BIZ-05` / `RV-UI-05`，详见 `user-journey.md`；UI 细则另接 `ui-ux-rules.md` 的 14 组 70 条 `UX-*` 结构化覆盖）。与 `data/review_pipeline.json` 保持同一编号，由 `scripts/review_runner.py` 逐条强制核验，并在 `finalize` 时自动输出按维度展示优化项与旅程对比的 **HTML 可视化报告（`report.html`）**。

随时查看生效目录（含私有/项目/CLI 叠加配置）：

```bash
python3 <源仓库>/scripts/review_runner.py catalog --target <项目目录>
```

---

## Phase 1：工程底线与基线门禁

### 维度 1：`engineering_baseline` — 工程底线与验证基线（5 条，有代码必跑，不可禁用）

1. **`RV-BASE-01` Diff 与工作区卫生**（不可 N/A）— 跑 `git diff --check`；无冲突标记、无无关格式化噪音、无构建/runtime 产物入仓、未擅自改动用户脏文件。
2. **`RV-BASE-02` 变更规模与单一主题（Change Size）**（不可 N/A）— 核对 diff 档位（300–500 解释凝聚性；500–1000 默认拆分或写明理由；>1000 须拆分除非批准的机械迁移），未混入无关重构/格式化/升级。
3. **`RV-BASE-03` 构建、类型检查与 Lint**（不可 N/A）— 跑受影响范围的 build / typecheck / lint，保留真实命令与退出码（不以“CI 绿”代替本次实证）。
4. **`RV-BASE-04` 后端优先自动化测试**（不可 N/A）— 按后端/API/service/unit/integration/contract/migration 优先顺序跑受影响测试集，记录通过/失败/跳过数；无自动化时记缺口与人工验收步骤。
5. **`RV-BASE-05` 新依赖与外部事实溯源（Source-Driven）**（未涉及可 N/A）— 新增/升级库、外部 API、框架或平台规则有锁定版本、官方文档或 ADR 依据，不凭记忆编造。

---

## Phase 2：四大核心维度并发审查（4 个维度全部可并发）

### 维度 2：`business_acceptance` — 业务闭环与产品认知验收（5 条，G4 + G1 + Journey）

1. **`RV-BIZ-01` 业务问题解决度（G4）**（不可 N/A）— 对照需求卡/spec 的“帮谁、什么场景、做成了是什么样子”，确认核心业务闭环已达成、范围与非目标未漂移。
2. **`RV-BIZ-02` 验收标准逐条对应一手证据（G1）**（不可 N/A）— 每条 AC 映射到本次 commit 的实测测试、数据核对、fixture/replay 或真实演示，不用假数据/截图/开发自述冒充。
3. **`RV-BIZ-03` 异常态、负向路径与恢复能力**（不可 N/A）— 核查空数据、非法输入、无权限、超时/部分失败、重复请求幂等与失败恢复路径。
4. **`RV-BIZ-04` 回归测试与业务数据对账**（不涉及可 N/A）— Bug fix 补回归测试；涉金额/库存/统计/报表做脱敏真实样本前后对账。
5. **`RV-BIZ-05` 预期旅程 vs 实际旅程与 8 大产品反模式审查（Product Cognition）**（命中旅程/信息架构/新功能/跨角色/异步工作流时激活）— 先独立于界面实现确认或推导 Expected Journey（不写页面/Tab/按钮），再对比实际产品路径与步骤，逐项排查 `user-journey.md` 的 8 类 Product Anti-pattern（`AP-01`..`AP-08`）；对符合高频习惯的优秀标准后台正常放行，不过度审查。

### 维度 3：`code_quality` — 代码质量：正确性 + 坏味道 + React 体检（18 条，按信号自动激活 React 子组）

#### 子组 A：React 增量体检（2 条，仅 React 项目激活）
1. **`RV-REACT-01` 增量范围与隐私合规扫描（React Doctor）**（不可 N/A）— 仅扫 `--scope changed --base <base>`，默认带 `--no-telemetry --no-supply-chain --json`；未运行 `install`/`ci install`；失败或 `skipped_files` 必标 `BLOCKED`。
2. **`RV-REACT-02` React 新增问题定级与存量剥离**（不可 N/A）— 工具输出仅作线索按 EE 口径重定级（安全/状态错乱/无限渲染/丢数据→阻断），存量问题单列技术债不阻断本次 PR，不刷分。

#### 子组 B：行为正确性与测试（6 条）
3. **`RV-BUG-01` 逻辑与边界条件**（不可 N/A）— 排查空值/None/undefined、空集合、0/负数/极值、编码/时区/精度、分页排序边界与 off-by-one。
4. **`RV-BUG-02` 状态机、并发与幂等竞态**（无相关逻辑可 N/A）— 排查状态允许/禁止迁移、并发写竞争、重复点击/回调、锁与事务边界、部分成功补偿或回滚。
5. **`RV-BUG-03` 错误处理、资源释放与外部超时**（不可 N/A）— 排查静默吞错、未知/失败伪装成功、文件/连接/子进程泄漏、外部 IO 缺超时或无限重试。
6. **`RV-BUG-04` 契约与向后兼容**（不可 N/A）— 排查前后端 schema 字段缺失、旧数据反序列化兼容、枚举新增、公共签名破坏性变更。
7. **`RV-BUG-05` 半成品隔离与入口门禁**（不可 N/A）— 确认未完成功能未直接接入生产主路径，具备 feature flag、配置开关或明确验收边界。
8. **`RV-TEST-01` 测试覆盖与断言强度（Test Gaps）**（不可 N/A）— 识别弱断言、漏测失败态、mock 过度失真，并明确列出 `Test Gaps`。

#### 子组 C：代码坏味道（10 条，命中时按 `refactoring-rules.md` 写明手法、前置测试与是否阻塞）
9. **`RV-SMELL-01` 过长函数（Long Function）** — 单函数混做解析、判断、IO 与副作用 → `Extract Function / Split Phase`。
10. **`RV-SMELL-02` 过大类 / 上帝服务（Large Class / God Service）** — 单类/模块混管协议、领域、存储、外部集成与后台任务 → `Extract Class / Move Function`。
11. **`RV-SMELL-03` 重复代码与重复规则（Duplicated Code / Rules）** — 同一限制、状态、角色或字段映射在多处复制 → `Extract Function / Shared Policy`。
12. **`RV-SMELL-04` 发散式变化 / 霰弹式修改（Divergent Change / Shotgun Surgery）** — 单文件因多类需求高频改动，或小改需跨多层多文件同步 → `Split Responsibility / Introduce Owning Layer`。
13. **`RV-SMELL-05` 基本类型偏执与魔法值（Primitive Obsession）** — 裸字符串/魔法数字表示状态、角色、action、错误码 → `Introduce Enum / Value Object`。
14. **`RV-SMELL-06` 过度耦合与越界依赖（Over-Coupling / Feature Envy / Inappropriate Intimacy）** — 业务用例直连外部 API/文件系统/线程细节，或 router 堆领域逻辑 → `Move Function / Hide Delegate`。
15. **`RV-SMELL-07` 条件分支爆炸（Conditional Complexity）** — 多层嵌套 if/switch 持续膨胀难以穷举测试 → `Strategy / Dispatch Table / State Machine`。
16. **`RV-SMELL-08` 临时字段、参数团与神秘命名（Temporary Field / Data Clumps / Naming）** — 无 schema 的隐式局部字段、成组重复传递的裸参数、晦涩命名 → `Introduce Parameter Object / Explicit State / Rename`。
17. **`RV-SMELL-09` 全局可变状态与无价值抽象（Global Mutable State / Middle Man / Speculative Generality）** — 共享可变单例破坏测试/并发隔离，或仅转发/过度预留抽象 → `Inject Dependency / Inline / Collapse Abstraction`。
18. **`RV-SMELL-10` 注释补丁味（Comment-as-Patch）** — 用注释解释晦涩绕路而非提炼概念 → `Extract Concept / Rename`（注释只留 why）。

### 维度 4：`security_architecture` — 安全合规与架构边界（11 条，密钥/日志必查，其余按子信号精准激活）

#### 子组 A：安全与脱敏（5 条）
1. **`RV-SEC-01` 密钥、凭据与硬编码检查**（有代码必查，不可 N/A）— 禁真实 secret/token/密码/私钥入仓；`.env.example` 仅留空/假值；开发 mock 默认关闭；区分配置化权限列表与禁止的生产硬编码凭据。
2. **`RV-SEC-02` 鉴权、授权默认拒绝与租户隔离**（命中安全面或 L2+ 激活）— 核查未登录/普通用户/管理员/跨租户默认拒绝；不把前端隐藏控件当安全边界。
3. **`RV-SEC-03` 输入校验、注入与签名防重放**（命中安全/DX 或 L2+ 激活）— 核查 SQL/命令/路径穿越/SSRF/XSS/反序列化边界及 webhook 签名防重放。
4. **`RV-SEC-04` 日志、报错与 URL 敏感信息脱敏**（有代码必查，不可 N/A）— 日志、报错、URL、遥测不得落 Authorization、cookie、token、signature、password、secret、PII 或敏感回调 payload。
5. **`RV-SEC-05` 合规与自动化/平台 ToS 授权边界**（命中安全或 AI/自动化激活）— 核查支付、PII、第三方抓取/RPA 的授权边界、ToS 风险、限流与失败态。

#### 子组 B：架构与数据迁移（4 条，按架构/数据或 L2+ 信号激活）
6. **`RV-ARCH-01` 真相源与分层归属（Owning Layer）** — 核心职责有唯一 owning layer；router 不承载领域逻辑；外部平台不擅自当产品真相源。
7. **`RV-ARCH-02` CONSTITUTION 红线与 ADR/架构文档同步** — 红线 0 触发（触线立刻停下给 owner 三路径）；架构变化同步 `ARCHITECTURE.md` 与 `ADR-*`。
8. **`RV-ARCH-03` 数据迁移与运行时存储边界** — 空库升级、存量升级、downgrade 或前向修复预案；runtime data 不入仓。
9. **`RV-ARCH-04` 复杂设计验证复核（D）**（L2+）— 涉并发/分布式/多步状态机/权限时，确认 TLA+/P/状态表结论仍成立且反例已转回归测试。

#### 子组 C：公开契约与 AI 链路（2 条，按 DX / AI 信号激活）
10. **`RV-DX-01` 公开 API / CLI / SDK 与文档体验（DX）** — 首次使用路径清晰、错误信息可行动、向后兼容、README 与示例同步。
11. **`RV-AI-01` AI / OCR / CV / RPA 生产链路检查** — prompt 版本与回滚、结构化输出 schema 校验、调用观测、超时降级与 eval/replay 证据。

### 维度 5：`ui_ux_experience` — 界面体验与旅程走查（8 条门禁 + 14 组 70 条 `UX-*`，仅涉及 UI 时触发）

#### 子组 A：无引导用户旅程走查（Blind Walkthrough，命中旅程变更时优先执行）
1. **`RV-UI-05` 无引导用户走查与 7 项旅程观察（Blind User Walkthrough）**（命中旅程/IA/工作流时激活）— 使用脚本生成的物理隔离无源码 blind prompt（仅含用户身份、场景、目标与入口 URL，不含 diff/源码/按钮路径/内部模块说明）实际操作完成任务，逐项记录 7 项观察点（首屏起步、自主发现、模块认知负担、异步非阻塞、上下文恢复、下一步清晰度、目标达成）与真实摩擦；仅截图标未验证边界，且不冒充真实用户可用性测试。

#### 子组 B：前置交互状态探索（Bombadil，走查前必执行）
2. **`RV-BOMB-01` 适用性与隔离动作边界判定** — 可运行 UI 且涉异步交错/重复提交/重试恢复/权限切换/多步状态流转→适用并固定版本/URL/角色/隔离数据与动作边界（同源≠隔离）；仅截图/静态才允许 `N/A`；工具缺失/断网/未隔离强制 `BLOCKED`。
3. **`RV-BOMB-02` 业务属性规格与有界执行** — 核验 CLI `--version` 与 `--help`，从验收项提炼业务属性与可达动作，执行有界探索（默认 1m）并留命令、退出码与 trace（默认 smoke / 固定 Playwright 不得冒充）。
4. **`RV-BOMB-03` 违规复现与探索结论边界** — 违规留重放命令与前置状态；无违规仅声明“在该版本/范围/预算内未发现违规”；中断/目标不可达标 `BLOCKED` 并给补证办法。

#### 子组 C：界面自解释与 14 组 70 条体验规则（UI/UX Audit）
5. **`RV-UI-01` 复核前置状态探索证据**（不可 N/A）— 直接继承本维度 Bombadil 适用性结论与证据，不重复跑已完成探索。
6. **`RV-UI-02` 陌生语言 UI 自解释检查（`UX-VIS-09`）**（不可 N/A）— 隔离副本替换全部可见文字并保留版式后验基础辨识；未做转换或仅截图如实标未验证边界。
7. **`RV-UI-03` 70 条界面规则逐条审验（`UX-*`）**（不可 N/A）— 按 `ui-ux-rules.md` 14 组 70 条规则逐条审验，并在 `meta.ux_coverage` 交齐全部 14 组结构化统计（通过/不通过/不适用/未验证总计=70）及全部不通过/未验证 `UX-*` ID；不打审美分。
8. **`RV-UI-04` 材料证据边界与视觉对标（G3）**（不可 N/A）— 截图须将焦点/路由/提交/权限/性能/读屏列为 `unverified_items` 且不放行上线；G3 对标 `.evolution/` 或 `EE_PRIVATE_ASSETS`（未加载须声明），L2+ 由校准过的人拍板。

---

## Phase 3：上线准备与确定性总决

### 维度 6：`release_readiness` — 上线准备与发布门禁（3 条，R / Release）

1. **`RV-REL-01` 业务侧上线就绪**（无用户可见变化可 N/A）— 明确提前知会对象（客户/客服/销售/运营）、说明培训、指标口径变化与业务兜底方案。
2. **`RV-REL-02` 技术侧放量、监控与已验证回滚**（不可 N/A）— 配置/环境变量、迁移顺序、分批放量或 feature flag、业务指标优先监控及已验证回滚步骤。
3. **`RV-REL-03` PR 与治理文档生命周期收口**（不可 N/A）— PR body 6 要素完整、必要 changelog、design doc 从 `active/` 迁至 `done/` 并回填验证结果、`active-context.md` 已更新。
