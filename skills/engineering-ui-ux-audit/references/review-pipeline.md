# Script-Driven Post-Dev Review Pipeline（脚本驱动的动态可配置评审链路）

本文件定义开发后 Review（Stage 7–8 与团队交付 Gate 2）的控制链路。核心原则：**默认基线聚类为 6 个正交、业务一眼可读的 Review 维度（覆盖 48 条稳定编号原子规则 `RV-*` 与 70 条 `UX-*`，见 `references/review-rules.md`），支持按公司/项目/任务动态叠加或裁剪配置（不写死步骤）；执行全程记录可观测的过程日志与实时进度看板，默认产出可读的 HTML 可视化报告（`report.html`）+ Markdown 汇总（`report.md`），缺任一必检规则即拒收。**

- 编排脚本：`scripts/review_runner.py`（位于源仓库；软链安装的 Skill 取本目录真实路径向上两级）。
- HTML 渲染器：`scripts/review_report_html.py`（零第三方依赖，内联 CSS/JS 与主题变量，按维度讲清优化点）。
- 基线与叠加配置：`data/review_pipeline.json`（默认基线）+ `schemas/review-overlay.schema.json`（动态叠加契约）。
- 证据机检联动：`finalize` 自动生成兼容 `schemas/evidence-package.schema.json` 的证据包并调用 `scripts/gate_check.py` 校验。

---

## 1. 默认基线：三阶段硬门闩 + 6 个聚类维度（48 条 `RV-*` + 70 条 `UX-*`）

同一 Phase 内就绪维度**允许并发执行**（推荐派发独立只读 subagent），但下一 Phase 必须等前置依赖落盘后解锁；**每个维度提交时必须对旗下全部激活规则逐条在 `checks[]` 交账，漏一条即拒收。**

| 阶段 | 聚类维度（Lane ID） | 核心问题 | 子分组与规则编号（默认条数） | 对应 Gate / 角色 | 触发条件 | 并发 |
|---|---|---|---|---|---|---|
| **Stage 0** | `init`（脚本自动） | 范围与配置是什么？ | 合并四层叠加配置 + 信号分流 | — | 每次必先运行 | — |
| **Phase 1** | `engineering_baseline` | 工程底线稳吗？ | 工程底线 `RV-BASE-01`..`05`（5 条） | G0 / QA | 有代码变更（不可 N/A / 禁用 / 豁免） | 否（前置门闩） |
| **Phase 2** | `business_acceptance` | 业务问题解决了吗？ | 业务与端到端验收 `RV-BIZ-01`..`04`（4 条） | G4 + G1 / Product + QA | `pr`/`delivery`/`release` 或交付 | 是 |
| **Phase 2** | `code_quality` | 代码正确、干净且有测试保护吗？ | React 扫描 `RV-REACT-01..02` + 正确性与测试 `RV-BUG-01..05`/`RV-TEST-01` + 坏味道 `RV-SMELL-01..10`（18 条） | G0 + CR / Code | 有代码变更（不可 N/A；`RV-REACT-*` 仅 React 激活） | 是 |
| **Phase 2** | `security_architecture` | 安全合规与架构边界稳吗？ | 安全脱敏 `RV-SEC-01..05` + 架构迁移 `RV-ARCH-01..04` + 接口 DX `RV-DX-01` + AI 链路 `RV-AI-01`（11 条） | G0 + D / Security + Arch + DX | 有代码变更（不可禁用 / 豁免；子规则按信号激活） | 是 |
| **Phase 2** | `ui_ux_experience` | 界面用起来顺、状态不炸且看起来对吗？ | Bombadil 状态探索 `RV-BOMB-01..03` + UI/UX 审计 `RV-UI-01..04` + 70 条 `UX-*`（7 条门禁） | G2 + G3 / QA + Design | 涉及 UI 或 `audit` 模式（先判 Bombadil 再做走查） | 是 |
| **Phase 3** | `release_readiness` | 能不能放心发布与回滚？ | 上线与发布准备 `RV-REL-01`..`03`（3 条） | R / Release | `delivery`/`release`、L2+ 或涉发布 | 否（汇总门闩） |
| **Stage 3 裁决** | `finalize`（脚本自动） | 最终能不能交付？ | 全量规则汇总 + `gate_check.py` + `report.html` / `report.md` | 最终门禁 | 全必检维度落盘后 | — |

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

# 1. Stage 0：自动合并私有/项目/CLI 配置并定界
python3 "$RUNNER" init --target . --base origin/main --mode pr --level L1 [--overlay ./extra.json]

# 2. 解锁当前 Phase 就绪维度并动态拼接专属 Prompt（Phase 1 -> Phase 2 四维并发 -> Phase 3）
python3 "$RUNNER" next --run "<run_dir>" --emit-prompts

# 3. （可选）开工打点，看板显示 [→ RUNNING]
python3 "$RUNNER" start --run "<run_dir>" --lane <lane_id> --worker subagent-1

# 4. 并发或顺序执行并逐条 checks[] 落盘（自动打印里程碑日志与进度看板）
python3 "$RUNNER" submit --run "<run_dir>" --lane <lane_id> --input -

# 5. 查看完整过程时间线，或中途生成 HTML 看板（随时）
python3 "$RUNNER" log --run "<run_dir>"
python3 "$RUNNER" render --run "<run_dir>"

# 6. 确定性总决（联动 gate_check.py，自动产出 report.html + report.md）
python3 "$RUNNER" finalize --run "<run_dir>"

# 7. 阻断修复后：增量复审 Round N+1
python3 "$RUNNER" recheck --run "<run_dir>"
```

---

## 6. 脚本硬校验清单与边界

1. **逐条规则交账**：`checks[]` 必须覆盖本维度全部激活规则编号；缺条、重复、不可 `N/A` 标 `N/A`、`checks[]` 有 `FAIL` 却报维度 `PASS` 均拒收。
2. **Finding 溯源**：每条 finding 必须带合法 `rule_id`（`RV-*` / `UX-*` / 自定义 `<PREFIX>-<GROUP>-<NN>`）、`severity`、`location`、`problem`、`impact`、`fix`。
3. **专项底线**：
   - `code_quality` 命中 React 时必须带合法 React Doctor `meta`（`scope` / `no_telemetry`），跳文件禁标 `PASS`；
   - `ui_ux_experience` 内 `RV-BOMB-01..03` 工具缺失/未隔离强制 `BLOCKED` 禁标 `N/A`；仅截图必须列 `unverified_items` 且 `finalize` 不判 `READY`；
   - 浏览器测试遵守非 UI 后端优先、复杂可运行 UI 前置 Bombadil 的统一边界。
4. **有范围提前阻断**：存在 `FAIL` 或 `P0/P1` 时允许 `finalize --early-stop --reason "..."`，强制单列未执行维度并产出 HTML 报告。
5. **无脚本兜底**：宿主无法运行 Python/Shell 时先说明“未运行 `scripts/review_runner.py` 及原因”，再按 `references/review-rules.md` 6 维度逐条手工核验，并在回复过程中汇报阶段完成进度。
