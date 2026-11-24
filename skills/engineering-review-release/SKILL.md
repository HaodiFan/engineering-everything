---
name: engineering-review-release
description: Use when reviewing code, PRs, merge readiness, CI failures, release risk, rollback plans, or deciding whether a change is safe to ship.
metadata:
  version: 0.18.0
---

# Engineering Review Release / Review 与发布

默认 code-review 立场：问题先行，按严重度列 bugs、行为回归、坏味道、缺测试、安全与发布阻断。摘要永远次要。

本 Skill 采用 **Script-Driven + 动态可配置 + 产品认知/用户旅程 + HTML 可视化报告** 强控制链路（`scripts/review_runner.py` + `scripts/review_report_html.py` + `references/review-rules.md` + `references/user-journey.md`）：默认基线聚类为 **3 个执行阶段、6 个正交 Review 维度、50 条原子规则（`RV-*`，含 L4/L5 产品认知与旅程规则 `RV-BIZ-05` / `RV-UI-05`）**（UI 维度另强制 14 组 70 条 `UX-*` 结构化覆盖），支持按公司/项目/CLI **动态叠加或裁剪配置**。脚本掌控进度、并发解锁、物理无源码盲测 Prompt、逐条 `checks[]` 交账、全程过程日志，并默认产出含“预期 vs 实际旅程对比”的 **`report.html`** + `report.md`。

## 何时使用

- 用户要求 review、PR、merge、release、发布、CI、是否 ready 或开发后验收。
- Stage 6 实现（`engineering-build-verify`）或 Stage 9 重构收尾后进入独立验证与门禁。
- 团队交付进入 Gate 2“交付前确认做对了”，需要下结论、留证据包或检查发布准备。

## Script-Driven 三阶段 6 维度控制流（默认必走）

编排脚本位于源仓库 `scripts/review_runner.py`（软链安装取本目录真实路径向上两级即源仓库；可用 `catalog --target <项目目录>` 查看合并叠加后的完整生效规则目录）。

1. **阶段 0：初始化定界与配置叠加（`init`）**：
   - 运行 `python3 <源仓库>/scripts/review_runner.py init --target <项目目录> --mode <pr|delivery|release|audit> --level <L0|L1|L2|L3>`（团队交付附 `--dri`、`--reviewer`、`--intent-card`；有发布加 `--has-release`；截图/原型用 `--mode audit --material screenshot|prototype|runnable`）。
   - **动态配置叠加**：自动合并基线 `data/review_pipeline.json` → `$EE_PRIVATE_ASSETS/review_pipeline.json`（及 `review_overlays/*.json`）→ `<项目>/.evolution/review_pipeline.json`（及 `review_overlays/*.json`）→ CLI `--overlay <path.json>` / `--enable-lane` / `--disable-lane <id>:<理由>`（`never_waived` 硬门禁不可禁用），并冻结至 `<run_dir>/effective_config.json`。
   - 自动扫描 diff（含未提交改动）、Change Size 与风险信号，锁定 `workspace_fingerprint`，精准激活必检维度与子规则。
2. **阶段 1：前置工程底线门禁（Phase 1）**：
   - 跑 `next --run <run_dir> --emit-prompts` 解锁 **维度 1 `engineering_baseline`**（`RV-BASE-01`..`05`：Diff 卫生、构建/类型、Lint/静态扫描、测试真实通过、反跳步核对；不可豁免）。
   - 完成后在 `checks[]` 逐条交账并跑 `submit --run <run_dir> --lane engineering_baseline --input -` 落盘。**Phase 1 落盘前，Phase 2 锁死。**
3. **阶段 2：四大核心维度并发深度评审（Phase 2，4 维度全部可并发）**：
   - 跑 `next --run <run_dir> --emit-prompts` 解锁并自动注入 Phase 1 证据，推荐派发独立只读 subagent 并发执行：
     - **维度 2 `business_acceptance`**（`RV-BIZ-01`..`05`）：业务闭环、需求卡 AC 一手证据、负向路径，以及命中旅程/信息架构/新功能/异步工作流时激活的 `RV-BIZ-05`（先独立推导 Expected Journey 再对比实际路径，排查 `AP-01..08` 八大产品反模式；符合高频习惯的标准后台正常放行）。
     - **维度 3 `code_quality`**（`RV-REACT-01..02`[React 激活] + `RV-BUG-01..05` + `RV-TEST-01` + `RV-SMELL-01..10`）：React Doctor 变更扫描、正确性/边界/并发、测试防护与 10 条坏味道（联动 `references/refactoring-rules.md`）。
     - **维度 4 `security_architecture`**（`RV-SEC-01..05` + `RV-ARCH-01..04` + `RV-DX-01` + `RV-AI-01`）：安全脱敏与权限（不可豁免）、架构/红线/迁移、接口 DX 与 AI/自动化链路（按信号精准激活子规则）。
     - **维度 5 `ui_ux_experience`**（`RV-UI-05`[旅程激活] + `RV-BOMB-01..03` + `RV-UI-01..04` + 14 组 70 条 `UX-*`）：命中旅程变更时先用脚本生成的物理隔离无源码盲测 Prompt（`ui_ux_experience.blind.md`）做 Blind User Walkthrough 记录 7 项观察点；再按 `references/bombadil.md` 做状态探索（工具缺失/未隔离强制 `BLOCKED` 禁标 `N/A`），并委托 `engineering-ui-ux-audit` 完成 `UX-VIS-09` 与 14 组 70 条 `UX-*` 结构化覆盖。
   - 以及叠加层注入的自定义维度或阶段（如 Phase 2.5 行业合规）。
4. **阶段 3：上线发布准备与确定性总决（Phase 3 + `finalize`）**：
   - 命中发布/交付/L2+ 时先完成 **维度 6 `release_readiness`**（`RV-REL-01`..`03`：业务侧就绪、技术侧放量/监控/已验证回滚、PR/文档生命周期）。
   - 运行 `finalize --run <run_dir>`：核验全维度全规则无漏检、指纹未漂移、L1+ 独立验收人（`reviewer != dri`），自动生成 `evidence-package.json` 并调用 `scripts/gate_check.py` 机检，**同时产出 `report.html`（可视化交互报告，按维度讲清待优化项）与 `report.md`**。
   - 已有 P0/P1 阻断需提前结束时跑 `finalize --early-stop --reason "..."`；审查中途也可跑 `render --run <run_dir>` 生成实时进度 HTML。
5. **修复后增量复审（`recheck`）**：
   - 修复后跑 `recheck --run <run_dir>` 进入 Round N+1：自动结转未受影响维度，重开受影响与失败/受阻维度并把上轮带 `rule_id` 的 Findings 注入新 Prompt 定点复验。

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
- `references/review-pipeline.md`：执行脚本驱动的三阶段评审、配置叠加（overlay）、过程日志、HTML 报告渲染或增量复审时就读。
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
