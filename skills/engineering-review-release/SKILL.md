---
name: engineering-review-release
description: Use when reviewing code, PRs, merge readiness, CI failures, release risk, rollback plans, or deciding whether a change is safe to ship.
metadata:
  version: 0.19.0
---

# Engineering Review Release / Review 与发布

默认 code-review 立场：问题先行，按严重度列 bugs、行为回归、坏味道、缺测试、安全与发布阻断。摘要永远次要。

本 Skill 采用 **Script-Driven + 2 阶段零等待并发 + 三档 Profile + 动态可配置 + HTML 可视化报告** 强控制链路（`scripts/review_runner.py` + `scripts/review_report_html.py` + `references/review-rules.md` + `references/user-journey.md`）：默认基线聚类为 **2 个执行阶段、6 个正交 Review 维度、50 条原子规则（`RV-*`，含 `RV-BIZ-05` / `RV-UI-05`）**（UI 维度在 `standard/full` 档强制 14 组 70 条 `UX-*` 结构化覆盖），默认按变更规模与信号自动选档（`fast` 17 条 / `standard` / `full`）并用 Pointer-First 瘦身 Prompt、物理隔离无源码盲测与 Delta 增量复审大幅压缩耗时，同时默认产出 **`report.html`** + `report.md`。

## 何时使用

- 用户要求 review、PR、merge、release、发布、CI、是否 ready 或开发后验收。
- Stage 6 实现（`engineering-build-verify`）或 Stage 9 重构收尾后进入独立验证与门禁。
- 团队交付进入 Gate 2“交付前确认做对了”，需要下结论、留证据包或检查发布准备。

## Script-Driven 两阶段 6 维度并发控制流（默认必走）

编排脚本位于源仓库 `scripts/review_runner.py`（软链安装取本目录真实路径向上两级即源仓库；可用 `catalog --target <项目目录>` 查看合并叠加后的完整生效规则目录）。

1. **阶段 0：初始化定界、快返预检与智能定档（`init`）**：
   - 运行 `python3 <源仓库>/scripts/review_runner.py init --target <项目目录> --mode <pr|delivery|release|audit> --level <L0|L1|L2|L3> [--profile auto|fast|standard|full] [--dispatch auto|bundle|parallel] [--project-type auto|web_ui|desktop_app|mobile_app|browser_extension|data_automation|backend_api|ai_agent|cli_sdk_tool|infra_devops]`（团队交付附 `--dri`、`--reviewer`、`--intent-card`；有发布加 `--has-release`；Draft PR 加 `--draft`；截图/原型用 `--mode audit --material screenshot|prototype|runnable`）。
   - **领域技术栈按需挂载（不涉及就不 Review）**：根据仓库清单 + 本次 diff 实际触达范围，自动识别 9 类领域技术栈包（支持多标签组合与 Overlay 自定义扩展），仅激活命中的专项规则（`RV-DESK-01` / `RV-MOB-01` / `RV-DATA-01` / `RV-EXT-01` / `RV-INFRA-01` / `RV-AI-01` / `RV-DX-01`）并向 Prompt 注入对应注意事项；未涉及的领域自动 `AUTO_NA` 零干扰。
   - **快返预检 + 智能定档 + 动态叠加**：自动检测冲突标记（`has_merge_conflicts`）与 `--draft`；按改动行数、文件数与精准信号自动决定 `fast` / `standard` / `full`；合并基线 → 私有层 → 项目层 → CLI `--overlay` 并冻结至 `<run_dir>/effective_config.json`。
2. **阶段 1：核心五维审查（支持单批次合批 `bundle` 与独立并发 `parallel`）**：
   - 跑 `next --run <run_dir> --emit-prompts`（默认 Pointer-First 瘦身 Prompt，需内联全文加 `--full-prompts`）：
     - **`bundle` 模式（`fast` / `standard` 默认，一次输入一次结果）**：脚本自动把当前就绪的静态维度（`t=0` 为 D1+D2+D3+D4）合并成 **1 份 `bundle_batch.md`**，派 **1 个独立只读审查者**读一遍 diff、一次输出全部维度的 JSON 数组并一次 `submit-batch --run <run_dir> --input -` 落盘（仍逐维度跑全部 Python 硬校验）；非 UI PR 全程仅 **1 次 AI 批次**！
     - **`parallel` 模式（`full` / L2+ / release 默认，或 `--dispatch parallel`）**：按「1 维度 = 1 独立只读 Subagent」并发派发，避免超大 PR 上下文过载；维度 1 落盘后立刻再跑 `next` 解锁维度 5。
     - **五大维度职责**：
       - **维度 1 `engineering_baseline`**（`RV-BASE-01`..`05`，不可豁免）：Diff 卫生、变更规模、构建/类型/Lint、后端优先测试、新依赖溯源。
       - **维度 2 `business_acceptance`**（`RV-BIZ-01`..`05`）：业务闭环、AC 一手证据、异常/负向路径、回归对账与旅程反模式 `RV-BIZ-05`。
       - **维度 3 `code_quality`**（`RV-REACT-01..02` + `RV-BUG-01..05` + `RV-TEST-01` + `RV-SMELL-01..10`）：React 增量体检、正确性/边界、测试缺口与 10 条坏味道。
       - **维度 4 `security_architecture`**（`RV-SEC-01..05` + `RV-ARCH-01..04` + `RV-DX-01` + `RV-AI-01`，不可禁用）：安全脱敏（必检）与按子信号精准激活的鉴权/架构/DX/AI 规则。
       - **维度 5 `ui_ux_experience`**（仅依赖维度 1；`RV-UI-05` + `RV-BOMB-01..03` + `RV-UI-01..04` + 14 组 70 条 `UX-*`）：激活 `RV-UI-05` 时无源码盲测（`ui_ux_experience.blind.md`）**永不合批**，必须独立无源码先行；随后做 Bombadil 状态探索与 `engineering-ui-ux-audit` 走查（全通可用 `--ux-all-pass`；`fast` 档免交 14 组矩阵）。
3. **阶段 2：上线发布准备与确定性总决（Phase 2 + `finalize`）**：
   - 命中发布/交付/L2+ 时完成 **维度 6 `release_readiness`**（`RV-REL-01`..`03`：业务侧就绪、技术侧放量/监控/已验证回滚、PR/文档生命周期）。
   - 运行 `finalize --run <run_dir>`：核验全维度全规则无漏检、指纹未漂移、L1+ 独立验收人（`reviewer != dri`），自动调用 `scripts/gate_check.py` 机检并产出 **`report.html` + `report.md`**。已有 P0/P1 阻断可跑 `finalize --early-stop --reason "..."`。
4. **修复后 Delta 增量复审（`recheck`）**：
   - 修复后跑 `recheck --run <run_dir>` 进入 Round N+1：自动用 `git log --no-merges` 剔除合并上游带来的无关文件噪音，精准结转未受影响维度（`business_acceptance` 仅失败重开，`code_quality` / `security_architecture` / `ui_ux_experience` 按实际改到的桶重开）；对重开的非 `always` 维度自动启用 **Delta 模式**——继承上轮已 `PASS` 的规则，只需复验上轮失败/受阻/命中 Finding 的规则（强制全量重审加 `--full-recheck`）。

## 过程日志与 HTML 结果呈现（必做）

- **实时过程播报**：脚本自动落盘 `<run_dir>/events.jsonl` 与 `<run_dir>/progress.log`。每完成一个维度或解锁一个 Phase，向用户输出一行简洁的过程进度日志（例如 `[R1] ✓ engineering_baseline 已完成 (5/5) · ★ Phase 1 完成 -> Phase 2 四维度并行已解锁`），让用户实时看到进度。
- **HTML 结果呈现**：`finalize` 默认生成 `<run_dir>/rounds/r<N>/report.html`（按 6 个维度清晰列出结论、待优化卡片、影响、改法、复验条件与缺口）。若当前对话宿主支持内联 HTML 渲染工具（如 `html_render`），直接把 `report.html` 渲染给用户查看；否则在结论下方提供 `report.html` 的可点击文件路径，让用户一键在浏览器打开。

> **无脚本环境兜底**：仅当宿主完全无法运行 Python/Shell 时，写明“未运行 `scripts/review_runner.py` 及原因”，再按 `references/review-rules.md` 6 维度逐条手动核验并在推进过程中汇报阶段完成进度，不假装完成机检。

## 团队交付（Gate 2）铁律

按 `references/delivery-gates.md` 第 4 节：先问“业务问题解决了吗”，再看功能、体验、审美和工程底线；只深挖相关项。

- 结论只有三种：**可以交付** / **还不能交付（附最小修改建议）** / **缺证据没法判断（说清缺什么、谁补）**。
- 没证据不算通过；“CI 绿了”“开发说测过了”只是线索，不是验收结论。**开发用的 Agent 不当验收人**。
- 有发布时，业务侧与技术侧准备必须一起确认。

## 输出模板（与 `references/output-contracts.md` 对齐）

默认给出简明结论与 `report.html` 呈现/链接；文本摘要遵循 PR / 代码评审结构：

```text
Findings:
- [Severity][rule_id] file:line - 问题、影响、建议
Open Questions:
Test Gaps:
Change Summary:
Tests / release gates:
Residual risk:
```

团队交付使用 `references/output-contracts.md` 的“交付前（Gate 2）”模板，第一句先给结论，正文不堆内部代号；列明 Bombadil 适用性/命令/结果或未完成原因。无问题时明说无阻塞发现并列测试缺口。

## 停止条件

- 没有 diff、PR、分支或审查材料范围，无法 review。
- 缺运行时验证或仅有静态截图，结论不得为可以交付。
- 发现 P0/P1 行为、数据或安全风险未处理时，停止合并/发布；提前结束须用 `--early-stop` 保留未执行项。

## References（用到时再读）

本目录没有的参考文件（文中按名字提到的），在源仓库的 `references/` 下：取本 Skill 目录的真实路径（它是软链）往上两级就是源仓库。找不到就直说没读到，不要假装读过。

- `references/review-rules.md`：查看 6 个聚类维度、50 条编号规则（`RV-*`）完整清单时就读。
- `references/review-pipeline.md`：执行脚本驱动的两阶段并发评审、三档 Profile、配置叠加（overlay）、过程日志、HTML 报告渲染或 Delta 增量复审时就读。
- `references/user-journey.md`：涉及新功能、信息架构、工作台、跨角色或异步工作流，要做 Expected vs Actual Journey、8 大产品反模式或 Blind Walkthrough 时就读。
- `references/code-review-standards.md`：做代码评审口径核对时。
- `references/refactoring-rules.md`：命中 `RV-SMELL-*` 坏味道需要手法、前置测试和阻塞判断时。
- `references/react-doctor.md`：评审或验收 React 项目时。
- `references/bombadil.md`：评审可运行 UI 且涉异步、重复操作、恢复、权限或状态流转时，走查前就读并执行。
- `references/delivery-gates.md`：团队交付要下“能不能交付”结论或做上线准备时。
- `references/verification-methods.md`：要挑验证方法、判断证据够不够时。
- `references/checklists.md`：PR 合并或发布前自查时。
- `references/execution-pipeline.md`：要核对 review 角色映射或测试顺序边界时。
- `references/stage-playbook.md`：拿不准处于 7–8 哪个阶段时。
- `references/output-contracts.md`：要写正式 review 或“交付前”输出时。
