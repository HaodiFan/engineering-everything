# Script-Driven Post-Dev Review Pipeline（脚本驱动的动态可配置评审链路）

本文件定义开发后 Review（Stage 7–8 与团队交付 Gate 2）的控制链路。核心原则：**默认基线聚类为 6 个正交、业务一眼可读的 Review 维度（覆盖 50 条稳定编号原子规则 `RV-*`——含 L4/L5 产品认知与用户旅程规则 `RV-BIZ-05` / `RV-UI-05`——以及 14 组 70 条 `UX-*` 结构化覆盖，见 `references/review-rules.md` 与 `user-journey.md`），采用 2 阶段零等待并发 DAG + 三档智能 Profile（`fast` / `standard` / `full`）+ Pointer-First 瘦身 Prompt + Delta 增量复审，支持按公司/项目/任务动态叠加或裁剪配置（不写死步骤）；执行全程记录可观测的过程日志与实时进度看板，默认产出含预期 vs 实际旅程对比的 HTML 可视化报告（`report.html`）+ Markdown 汇总（`report.md`），缺任一必检规则即拒收。**

- 编排脚本：`scripts/review_runner.py`（位于源仓库；软链安装的 Skill 取本目录真实路径向上两级）。
- HTML 渲染器：`scripts/review_report_html.py`（零第三方依赖，内联 CSS/JS 与主题变量，按维度讲清优化点）。
- 基线与叠加配置：`data/review_pipeline.json`（默认基线，含 `profiles` 与 2 阶段 DAG）+ `schemas/review-overlay.schema.json`（动态叠加契约）。
- 证据机检联动：`finalize` 自动生成兼容 `schemas/evidence-package.schema.json` 的证据包并调用 `scripts/gate_check.py` 校验。

---

## 1. 默认基线：两阶段零等待 DAG + 单批次合批（Bundle）+ 三档 Profile

**提速核心（减少大模型 API 往返 + 杜绝重复读 diff）**：
- **默认单批次合批（`--dispatch auto|bundle|parallel`）**：
  - **`fast` / `standard` 档默认启用 `bundle`（一次输入、一次结果）**：`next --emit-prompts` 将当前就绪的全部非盲测静态维度（`t=0` 时为 **D1+D2+D3+D4**）浓缩为 **1 份 `bundle_batch.md`**（公共上下文与变更文件只注入一次，去重参考索引），AI **只读一遍 diff、一次推理输出全部维度的 JSON 数组**，经 `submit-batch` 一次性落盘并逐维度执行全部 Python 硬门禁校验。
    - **纯后端/非 UI PR**：全程只需 **1 次 AI 批次**即可收口全部 4 维度！
    - **小 UI PR（`fast`）**：只需 **2 次 AI 批次**（批次 1：静态 4 维合批 → 批次 2：轻量 UI 维度 D5）。
    - **复杂旅程 UI PR（`standard`）**：**3 次 AI 批次**（批次 1：静态 4 维合批 → 批次 2：物理隔离无源码盲测 `.blind.md` → 批次 3：D5 界面体验）。
  - **`full` 档（`release` / `L2+`）默认启用 `parallel`**：按「1 维度 = 1 独立只读 Subagent」并发执行（确保超大改动拥有独立上下文窗口；需要提速时亦可手工传 `--dispatch bundle`）。
  - **防锚定红线永不合批**：激活 `RV-UI-05` 时生成的无源码盲测 Prompt（`ui_ux_experience.blind.md`）**严禁**与读源码/diff 的维度合批，始终物理隔离独立执行。
- **依赖精准解锁**：**维度 5（`ui_ux_experience`）同属 Phase 1，仅依赖 `engineering_baseline`**；**维度 6（`release_readiness`）** 属 Phase 2 等前置维度落盘后收口。
- **逐条交账铁律**：无论合批或并发，提交时每个维度都必须对旗下全部激活规则逐条在 `checks[]` 交账，漏一条即拒收。

| 阶段 | 聚类维度（Lane ID） | 核心问题 | 子分组与规则编号（默认条数） | 前置依赖 | 触发条件 | 复审策略（Recheck） |
|---|---|---|---|---|---|---|
| **Stage 0** | `init`（脚本自动） | 范围、档位与快返风险？ | 合并四层叠加配置 + 精准信号分流 + 自动定档（`fast`/`standard`/`full`）+ 冲突/Draft 快返告警 | — | 每次必先运行 | — |
| **Phase 1** | `engineering_baseline` | 工程底线稳吗？ | 工程底线 `RV-BASE-01`..`05`（5 条） | 无（`t=0` 并发） | 有代码变更（不可 N/A / 禁用 / 豁免） | `always` |
| **Phase 1** | `business_acceptance` | 业务问题和产品旅程方向对吗？ | 业务与端到端验收 `RV-BIZ-01`..`04` + 产品认知与 8 大反模式 `RV-BIZ-05`（5 条） | 无（`t=0` 并发） | `pr`/`delivery`/`release` 或交付（`RV-BIZ-05` 需命中真实旅程面且 diff > 120 行或 `delivery/release` 或需求卡声明 `journeys[]`） | `on_failure_only` |
| **Phase 1** | `code_quality` | 代码正确、干净且有测试保护吗？ | React 扫描 `RV-REACT-01..02` + 正确性与测试 `RV-BUG-01..05`/`RV-TEST-01` + 坏味道 `RV-SMELL-01..10`（18 条） | 无（`t=0` 并发） | 有代码变更（不可 N/A；`RV-REACT-*` 仅 React 激活） | `on_file_match`（`code_files`） |
| **Phase 1** | `security_architecture` | 安全合规与架构边界稳吗？ | 安全脱敏 `RV-SEC-01..05` + 架构迁移 `RV-ARCH-01..04` + 接口 DX `RV-DX-01` + AI 链路 `RV-AI-01`（11 条） | 无（`t=0` 并发） | 有代码变更（不可禁用 / 豁免；剥离 `apps/<name>/` 前缀且忽略测试文件后按子信号激活） | `on_file_match`（`security_arch_files`） |
| **Phase 1** | `ui_ux_experience` | 盲测能走通、交互稳、70 条体验达标吗？ | 无源码盲测走查 `RV-UI-05` + Bombadil 状态探索 `RV-BOMB-01..03` + UI/UX 审计 `RV-UI-01..04` + 14 组 70 条 `UX-*`（8 条门禁） | 仅 `engineering_baseline` | 涉及 UI 或 `audit` 模式（`fast` 档免交 14 组 UX 矩阵；`RV-UI-05` 生成物理隔离 `ui_ux_experience.blind.md`） | `on_file_match`（`ui_files`） |
| **Phase 2** | `release_readiness` | 能不能放心发布与回滚？ | 上线与发布准备 `RV-REL-01`..`03`（3 条） | 前置全部维度 | `delivery`/`release`、L2+ 或涉发布 | `on_file_match`（`release_files`） |
| **Stage 3 裁决** | `finalize`（脚本自动） | 最终能不能交付？ | 全量规则汇总 + `gate_check.py` + `report.html` / `report.md` | 全必检维度落盘 | 全必检维度落盘后 | — |

### 三档智能 Profile（`--profile auto|fast|standard|full`）

`init` 默认按 `--profile auto` 自动选档，也可手工覆盖：

| Profile | 自动命中条件 | 规则规模 | UX 矩阵与 Prompt 策略 | 适用场景 |
|---|---|---|---|---|
| **`fast`** | `mode=pr` + `L0/L1` + 总改行 `<= 250` 且变更文件 `<= 8` + 未命中安全/架构/数据迁移/发布/AI 信号 + 未声明需求卡 `journeys[]` | 17 条高信噪比核心规则（必保底线、安全脱敏、Bug/Test、React 扫描与 UI 关键项） | 免填 14 组 70 条 `ux_coverage` 矩阵；Pointer-First 瘦身 Prompt | 小 PR、样式/面板精修、局部 bugfix（如 3 文件 94 行改动） |
| **`standard`** | 默认档位（中等 PR、命中安全/架构/旅程面或 >250 行） | 约 30–45 条（按精准信号动态激活） | 完整 14 组 `ux_coverage`（支持 `--ux-all-pass` 一键展开）；Pointer-First 瘦身 Prompt | 日常功能 PR、接口改动、交互流修改 |
| **`full`** | `mode=release` 或 `level=L2/L3` 或 `--profile full` | 全量 50 条规则（含全部坏味道、旅程盲测与发布准备） | 完整 14 组 `ux_coverage` + 全量约束；可加 `--full-prompts` 展开内联手册 | 重要版本发布、高风险架构重构、上线前 Gate 2 终审 |

**快返预检（Stage 0 Fast-Fail）**：`init` 自动检测冲突标记（`has_merge_conflicts`）与 `--draft` 标志；命中时在输出与进度看板置顶 `fast_fail_advisories`，提示直接阻断或暂缓全量审查，避免浪费算力。

### 按项目类型与技术栈自动分类（`--project-type auto|...`，支持多选）

`init` 根据仓库清单（`package.json` / `pyproject.toml` / `Cargo.toml` / `src-tauri/` / `AndroidManifest.xml` / `skills/*/SKILL.md` 等）**叠加本次 diff 实际触达范围**，自动识别活跃项目类型（支持多标签组合，如 `desktop_app + web_ui + ai_agent`），按技术栈精准注入审查重点并激活对应专项规则（无关技术栈保持 `AUTO_NA`，零冗余 Token）：

| 项目类型（`project_type`） | 典型技术栈 | 自动激活专项规则与工具 | 默认跳过/减负 |
|---|---|---|---|
| **`web_ui`** | React / Next.js / Vue / Svelte / Tailwind | `React Doctor`、`Bombadil`、`UX-VIS-09`、70 条 `UX-*`、自动加载 `DESIGN.md` | 不涉后端/桌面/移动端专项 |
| **`desktop_app`** | Electron / Tauri / SwiftUI / PyQt / Wails | **`RV-DESK-01`**（IPC/preload 隔离、系统托盘/快捷键/深浅色、本地持久化与签名更新）+ UI/UX | 无关后端迁移/采集专项 |
| **`mobile_app`** | iOS / Android / React Native / Expo / Flutter / 小程序 | **`RV-MOB-01`**（弱网恢复、权限拒绝兜底、安全区/键盘遮挡、旧版本兼容）+ UI/UX | 无关桌面/采集专项 |
| **`data_automation`** | Playwright / Puppeteer / Selenium / Scrapy / DrissionPage / RPA / ETL | **`RV-DATA-01`**（解析漂移显式告警禁静默吐空、限流退避、幂等去重、断点续传、资源释放）+ `RV-SEC-05` | 纯采集脚本自动跳过 UI/UX |
| **`backend_api`** | FastAPI / Django / Express / NestJS / Go / Prisma / Alembic | 后端优先测试、`RV-SEC-02/03`、`RV-ARCH-03` 迁移与并发幂等 | 纯后端自动跳过整个 UI/UX 维度（1 批次完结） |
| **`ai_agent`** | OpenAI / Anthropic / Gemini / MCP / RAG / OCR / CV / Skills | **`RV-AI-01`**（Prompt 版本回滚、Schema 校验、防注入、工具最小权限、观测与 Eval） | 无 UI 时 1 批次完结 |
| **`cli_sdk_tool`** | CLI / SDK / Library / Engineering Skills | **`RV-DX-01`**（首次路径、退出码、向后兼容、文档示例同步） | 自动跳过整个 UI/UX 维度（1 批次完结） |
| **`browser_extension`** | Chrome/Edge/Firefox Extension（MV3） | **`RV-EXT-01`**（最小 permissions、MV3 Service Worker 休眠无状态、content script 隔离、消息校验） | 仅涉插件才激活，其他项目 0 干扰 |
| **`infra_devops`** | Docker / Compose / GitHub Actions / K8s / Terraform | **`RV-INFRA-01`**（非 root 锁定镜像、CI 最小权限/Secret 掩码、健康检查/优雅停机、IaC 防误删） | 仅涉容器/CI/IaC 才激活，自动跳过 UI |

> **自定义领域包**：公司或项目可在 Overlay JSON 中通过 `project_types` 新增或扩展自有领域包（如量化交易、嵌入式、清结算），未涉及时同样保持 `AUTO_NA` 零干扰。

---

## 2. 动态叠加与配置化（不写死步骤）

`review_runner.py` 按四层顺序自动合并配置，并在 `init` 时将最终合并结果冻结保存到 `<run_dir>/effective_config.json`（保证本轮可复现）：

1. **基线层**：源仓库 `data/review_pipeline.json`
2. **公司私有层**（自动发现，可用 `--no-auto-overlays` 关闭）：`$EE_PRIVATE_ASSETS/review_pipeline.json` 与 `$EE_PRIVATE_ASSETS/review_overlays/*.json`
3. **项目层**（自动发现）：`<target>/.evolution/review_pipeline.json` 与 `<target>/.evolution/review_overlays/*.json`
4. **命令行临时叠加层**（可多次传入，按序生效）：`--overlay <overlay.json>`、`--enable-lane <id>`、`--disable-lane <id>:<理由>`

单个 Overlay JSON（结构见 `schemas/review-overlay.schema.json`）支持：
- `add_phases`：插入自定义阶段（通过 `order` 控制前后顺序，例如 `2.5` 插在 Phase 2 与 Phase 3 之间）；
- `add_lanes`：新增自定义审查维度（含 `rules[]`、`depends_on`、`trigger_signals`、`trigger_path_patterns`、`reference_files`、`recheck_policy`），自定义规则编号支持任意 `<PREFIX>-<GROUP>-<NN>`（如 `FIN-PAY-01`、`ORG-DB-01`、`PRJ-SEC-01`）；
- `extend_lanes`：给已有维度追加规则（`add_rules`）、追加参考文档（`add_reference_files`）、追加依赖或反跳步红线；
- `signal_patterns`：为项目特有目录补充信号匹配模式；
- `force_require_lanes` / `disable_lanes` / `disable_rules`：强制开启或带理由关闭**非硬门禁**维度/规则（`never_waived=true` 的硬门禁如 `engineering_baseline`、`security_architecture` 及其必检规则禁止被配置静默关闭）。

**优秀 UI 设计理念 / 审美基准配置（零配置自动发现 + 规则化模板）**：
- **免写 JSON 自动注入**：将团队或项目的设计理念 `.md` 放到 `$EE_PRIVATE_ASSETS/design-principles/*.md`、`$EE_PRIVATE_ASSETS/taste/*.md`、`$EE_PRIVATE_ASSETS/DESIGN.md` 或项目 `<target>/.evolution/design-principles/*.md`、`<target>/.evolution/taste/*.md`、`<target>/DESIGN.md`，`review_runner.py` 会自动发现并把全文注入 `ui_ux_experience`（以及激活 `RV-BIZ-05` 时的 `business_acceptance`），同时保持 `ui_ux_experience.blind.md` 物理隔离无泄露；提交 `ui_ux_experience` 时强制校验 `meta.company_cases_loaded = true` 并在 `report.html` 中标注已载入基准。
- **升级为逐条强制规则**：直接复用或改写源仓库预设模板 `data/review_overlays/ui-design-philosophy.example.json`（与配套 `ui-design-philosophy.example.md`，含 `DES-PHI-01..06`），放入 `.evolution/review_overlays/` 或传入 `--overlay` 即可逐条交账。

查看叠加后的生效目录：

```bash
python3 <源仓库>/scripts/review_runner.py catalog --target . --overlay ./custom.json
```

---

## 3. 实时过程日志与进度看板（质检过程可见）

为了避免审查变成“最后才给结论的黑盒”，脚本内置并发安全的追加式过程日志与实时进度看板：

- **落盘日志**：每次状态变更以 POSIX `O_APPEND` 原子追加到 `<run_dir>/events.jsonl`（结构化事件）与 `<run_dir>/progress.log`（可读时间线），支持并发 subagent 同时落盘不串行乱码。
- **自动记录的关键里程碑事件**：
  - `RUN_INIT`：初始化完成、叠加层、激活维度/规则总数；
  - `LANE_DISPATCHED`：维度解锁并生成 Prompt；
  - `LANE_STARTED`（可选调用 `start --run <dir> --lane <id> --worker <name>`）：维度标记进入 `RUNNING`；
  - `LANE_DONE`：维度提交完成，记录 `[✓ PASS / ✗ FAIL / ! BLOCKED / - N/A]` 与规则通过数；
  - `PHASE_DONE`：当某个 Phase 最后一个必检维度完成时**自动触发**，提示下一 Phase 已解锁；
  - `RUN_FINALIZED` / `ROUND_RECHECK`：总决与复审轮次切换。
- **实时查看与对人播报**：
  - 随时跑 `python3 <源仓库>/scripts/review_runner.py status --run <run_dir>` 看当前看板，或 `log --run <run_dir>` 看完整时间线；
  - **Agent 执行纪律**：在执行 Review 过程中，每当一个维度或一个 Phase 完成时，向用户输出简短的过程进度日志（例如 `[R1] ✓ engineering_baseline 已完成 (5/5) · ★ Phase 1 完成 -> Phase 2 四维度并行已解锁`），让用户实时看到哪些步骤已经好了、哪些进行中、哪些受阻。

---

## 4. HTML 可视化结果呈现（默认产出）

为了让非纯命令行读者和开发者都能一眼看懂“结论是什么、每个维度要优化什么”：

- **`finalize` 自动双产出**：默认在 `<run_dir>/rounds/r<N>/` 同时生成 **`report.html`**（主要给人阅读）与 `report.md`（适合 PR 评论或存档），可用 `--html-out <path>` 指定额外输出路径。
- **随时渲染实时看板**：审查进行中也可运行 `python3 <源仓库>/scripts/review_runner.py render --run <run_dir> [--out <path>]` 生成当前进度的 HTML 报告。
- **HTML 报告内容结构**（由 `scripts/review_report_html.py` 生成，纯静态单文件，支持深浅主题自动适配）：
  1. **结论横幅与核心指标**：最终裁决（可以交付 / 还不能交付 / 缺证据没法判断 / 评审进行中）、阻断项数、优化建议数、规则覆盖率、未验证/缺口数。
  2. **6 维度总览网格**：每个维度的业务问题、状态标签、待优化条数、规则通过率，点击直达该维度详情。
  3. **按维度拆解的“要优化什么”**：支持按严重度（阻断/重要/一般/建议）与维度筛选；每条优化项以卡片讲清 **严重度 + 规则编号 + 位置 + 现象问题 + 业务/用户影响 + 建议改法 + 复验条件**；无问题的维度明确展示“本维度暂无待优化项”；存在测试缺口或未验证项的维度单独高亮补证方法。
  4. **可折叠逐条规则明细（按子分组）与过程时间线**：默认折叠不喧宾夺主，点开即可核对 48 条 `RV-*` 逐条交账证据与 `progress.log` 执行记录。
- **对话内呈现**：若当前宿主支持内联渲染 HTML（如 T3 Code `html_render`），在给出结论摘要的同时直接把生成的 `report.html` 呈现给用户；否则给出 `report.html` 的本地可点击路径，方便浏览器直接打开。

---

## 5. 标准控制循环

```bash
RUNNER="<源仓库>/scripts/review_runner.py"

# 1. Stage 0：自动合并私有/项目/CLI 配置、定界、快返预检并自动选档（fast / standard / full）
python3 "$RUNNER" init --target . --base origin/main --mode pr --level L1 [--profile auto|fast|standard|full] [--draft] [--overlay ./extra.json]

# 2. 解锁当前就绪维度并生成 Pointer-First 瘦身 Prompt（Phase 1：t=0 维度 1–4 立即 4 路并发；维度 1 落盘后再跑 next 即时解锁维度 5）
python3 "$RUNNER" next --run "<run_dir>" --emit-prompts

# 3. （可选）开工打点，看板显示 [→ RUNNING]
python3 "$RUNNER" start --run "<run_dir>" --lane <lane_id> --worker subagent-1

# 4. 并发执行并逐条 checks[] 落盘（单维度用 submit；UI 全通可加 --ux-all-pass；多维度并行结束可一次 submit-batch）
python3 "$RUNNER" submit --run "<run_dir>" --lane <lane_id> [--ux-all-pass] --input -
# 或批量提交多个维度结果（JSON 数组）：
python3 "$RUNNER" submit-batch --run "<run_dir>" --input -

# 5. 查看完整过程时间线，或中途生成 HTML 看板（随时）
python3 "$RUNNER" log --run "<run_dir>"
python3 "$RUNNER" render --run "<run_dir>"

# 6. 确定性总决（联动 gate_check.py，自动产出 report.html + report.md）
python3 "$RUNNER" finalize --run "<run_dir>"

# 7. 阻断修复后：Delta 增量复审 Round N+1（自动剔除 merge commit 噪音，继承上轮已 PASS 规则；强制全量加 --full-recheck）
python3 "$RUNNER" recheck --run "<run_dir>"
```

---

## 6. 脚本硬校验清单与边界

1. **逐条规则交账**：`checks[]` 必须覆盖本维度全部激活规则编号；缺条、重复、不可 `N/A` 标 `N/A`、`checks[]` 有 `FAIL` 却报维度 `PASS` 均拒收（Delta 复审轮次由脚本自动补齐上轮已继承的 `PASS` 规则）。
2. **Finding 溯源**：每条 finding 必须带合法 `rule_id`（`RV-*` / `UX-*` / `AP-01..08` / 自定义 `<PREFIX>-<GROUP>-<NN>`）、`severity`、`location`、`problem`、`impact`、`fix`。
3. **专项底线**：
   - `business_acceptance` 激活 `RV-BIZ-05` 时必须提交 `meta.journey_review.journeys[]`（预期阶段、实际步骤、差异结论与全部 `AP-01..08` 排查状态；命中 `FOUND` 须有对应 Finding）；
   - `code_quality` 命中 React 时必须带合法 React Doctor `meta`（`scope` / `no_telemetry`），跳文件禁标 `PASS`；
   - `ui_ux_experience` 内 `RV-UI-03` 在 `standard/full` 档必须在 `meta.ux_coverage` 交齐全部 14 组（总计 70 条）结构化统计（支持 `--ux-all-pass` 或 `meta.ux_coverage_preset="all_pass"` 一键展开），`fast` 档免交 14 组矩阵；激活 `RV-UI-05` 时脚本自动生成物理无源码盲测 Prompt `ui_ux_experience.blind.md` 并强制校验 `meta.journey_walkthrough` 7 项观察点；`RV-BOMB-01..03` 工具缺失/未隔离强制 `BLOCKED` 禁标 `N/A`；仅截图必须列 `unverified_items` 且 `finalize` 不判 `READY`；
   - 浏览器测试遵守非 UI 后端优先、复杂可运行 UI 前置 Bombadil 的统一边界。
4. **有范围提前阻断**：存在 `FAIL` 或 `P0/P1` 时允许 `finalize --early-stop --reason "..."`，强制单列未执行维度并产出 HTML 报告。
5. **无脚本兜底**：宿主无法运行 Python/Shell 时先说明“未运行 `scripts/review_runner.py` 及原因”，再按 `references/review-rules.md` 6 维度逐条手工核验，并在回复过程中汇报阶段完成进度。
