# Engineering Everything v0.17.0

## 脚本驱动 6 维度评审链路 + HTML 可视化优化报告

这一版把开发后 Review 升级为**强控制、可并发、可动态叠加、结果一眼可读**的脚本驱动链路，并把 Bombadil 自主状态探索和陌生语言 UI 自解释检查正式纳入统一门禁。

## 新增：脚本驱动 6 维度评审编排（`scripts/review_runner.py`）

- **3 阶段 6 个正交维度（48 条 `RV-*` 原子规则 + 70 条 `UX-*`）**：
  - **Phase 1（前置门闩）**：维度 1 `engineering_baseline`（工程底线 `RV-BASE-01..05`，不可豁免）。
  - **Phase 2（四维并行）**：维度 2 `business_acceptance`（业务闭环）、维度 3 `code_quality`（React Doctor 增量体检 + 正确性与测试 + 10 项坏味道 `RV-SMELL-01..10`）、维度 4 `security_architecture`（安全脱敏硬门禁 + 架构/迁移/DX/AI）、维度 5 `ui_ux_experience`（Bombadil 状态探索 + UI/UX 70 条走查）。
  - **Phase 3（发布收口）**：维度 6 `release_readiness`（业务与技术上线准备、监控与回滚），完成后由 `finalize` 联动 `scripts/gate_check.py` 机检总决。
- **逐条交账与修复复审**：每个维度提交时必须在 `checks[]` 逐条交账，漏条或工具缺失伪装 `N/A` 会被脚本拒收；修复后跑 `recheck` 自动结转未受影响维度并定点复验上轮 Findings。
- **动态四层叠加配置**：支持基线 `data/review_pipeline.json` → `$EE_PRIVATE_ASSETS` → 项目 `.evolution/` → CLI `--overlay` 动态增删阶段/维度/规则（`schemas/review-overlay.schema.json`），硬门禁不可静默关闭。
- **实时过程日志**：所有状态变更原子追加写入 `events.jsonl` 与 `progress.log`，随时可看进度看板与里程碑时间线。

## 新增：HTML 可视化优化报告（`scripts/review_report_html.py`）

- `finalize` 默认同时产出 **`report.html`** 与 `report.md`；审查中途也可运行 `render` 导出实时进度看板。
- 纯静态单文件（零第三方依赖，深浅主题自适应，全量 HTML 转义），按 6 个维度清晰展示裁决结论、待优化动作卡片（严重度 / 规则编号 / 位置 / 影响 / 改法 / 复验条件）、严重度筛选、待补证据/未验证缺口、可折叠逐条规则核验表与过程日志。

## 新增：Bombadil 状态探索与陌生语言自解释（`UX-VIS-09`）

- **Bombadil 显式接入**（`references/bombadil.md`）：复杂可运行 UI（异步加载交错、重复提交、重试恢复、权限切换、多步状态流转）在界面走查前先判并做隔离有界探索；工具缺失或无法隔离必须如实标 `BLOCKED`，不得标 `N/A`。
- **陌生语言 UI 自解释检查（`UX-VIS-09`）**：UI/UX 规则目录扩充至 70 条，通过将可见文字替换为等长陌生语言验证主导航、主操作与反馈是否靠 UI 本身即可辨认，保留既有规则编号稳定。

## 验证

- `scripts/sync_references.py --check --json`、`scripts/eval_scenarios.py validate --json`、`scripts/skill_doctor.py --json`、`scripts/self_evolve.py check --strict-install --json`、`scripts/self_evolve.py doctor --json`、`scripts/lesson.py validate` 全部通过。
- `python3 -m unittest discover -s tests` 全部 53 个单元测试通过；`python3 -m py_compile scripts/*.py` 与 `git diff --check` 通过。

## 升级

```bash
git -C <你的 engineering-everything 目录> pull --ff-only
python3 scripts/install.py relink --target all
```
