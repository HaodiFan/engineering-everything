---
schema_version: 1
id: review-script-driven-pipeline
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.17.0
min_package_version: 0.16.0
prompt: "这个包含后端权限改造和 React 审批表单的 PR 开发完了，帮我用强控制的方式完整 review 一遍，可以并发检查，判断能不能交付上线。"
expected_route_ids:
  - review-release
required_fields:
  - 交付结论
  - 证据
  - 上线准备
  - 未运行检查及原因
  - 剩余风险
must:
  - 先通过源仓库 scripts/review_runner.py init 识别 diff 范围、React 与权限/UI 风险信号，生成聚类为 6 个维度、包含具体 RV-* 编号规则的必检计划。
  - 每推进一个阶段都通过 scripts/review_runner.py next --emit-prompts 获取当前就绪维度与动态拼接的逐条 RV-* Prompt，不得跳过 Phase 1（engineering_baseline）。
  - 允许在 Phase 2 并发执行 4 个聚类维度（business_acceptance / code_quality / security_architecture / ui_ux_experience），每个维度 submit 时必须在 checks[] 中对全部激活 RV-* 逐条交账（含 business_acceptance 中的 RV-BIZ-05 预期 vs 实际旅程与 8 大反模式、code_quality 中的 RV-REACT-01..02 与 RV-SMELL-01..10、ui_ux_experience 中的无源码盲测 RV-UI-05、RV-BOMB-01..03、RV-UI-01..04 及 14 组 70 条 meta.ux_coverage），支持叠加项目/私有/CLI overlay 配置且不绕过硬门禁。
  - 在质检推进过程中及时体现已完成/进行中/受阻的过程进度日志（如每个维度或 Phase 完成后回报进度），并持久化到 events.jsonl 与 progress.log。
  - 每条 finding 必须带具体 rule_id（RV-* 或 UX-*）；ui_ux_experience 内先判 Bombadil 状态探索（工具缺失/未隔离强制 BLOCKED 禁标 N/A）再执行陌生语言检查（UX-VIS-09）与 70 条 UX-* 走查。
  - 全部必检维度与规则完成后通过 scripts/review_runner.py finalize 生成证据包、联动 gate_check 给出确定性裁决，并产出可读的 HTML 报告（report.html，按维度讲清待优化点）；若中途因 P0/P1 提前阻断，使用 --early-stop 并保留未执行维度。
  - 修复阻断问题后，通过 scripts/review_runner.py recheck 进入新一轮增量复审，定点复验上一轮带 rule_id 的 Findings。
must_not:
  - 不绕过 review_runner.py 直接口头宣布“审完了可以上线”。
  - 不漏检任一激活 RV-* 规则，不把工具缺失或无法隔离标成 N/A，不提交无证据的 PASS。
  - 不让实现用的开发 Agent 充当 L1+ 独立验收人。
expected_references:
  - skills/engineering-review-release/references/review-rules.md
  - skills/engineering-review-release/references/review-pipeline.md
  - skills/engineering-review-release/references/code-review-standards.md
  - skills/engineering-review-release/references/delivery-gates.md
stop_condition: "任一必检维度或激活 RV-* 规则未提交有效证据、工作区指纹漂移未 recheck、或 gate_check 存在阻断问题时，结论不得为可以交付。"
---

# Script-Driven Post-Dev Review Pipeline

验证开发后 review 通过 `scripts/review_runner.py` 实现 6 聚类维度、50 条 `RV-*` 原子规则（含 L4/L5 旅程认知规则与 14 组 70 条 `UX-*` 覆盖）的逐条交账、动态配置叠加、并发执行、物理隔离无源码盲测、过程日志追踪、HTML 可视化优化报告（`report.html`）与修复后增量复审闭环。
