---
schema_version: 1
id: product-journey-negative-benchmark
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.18.0
min_package_version: 0.17.0
prompt: "这个企业智脑工作台前端全部单元测试、E2E 和视觉规范检查都通过了，帮我从产品认知和用户旅程视角完整 review 一遍，判断到底能不能交付。"
expected_route_ids:
  - review-release
required_fields:
  - 交付结论
  - 证据
  - 上线准备
  - 未运行检查及原因
  - 剩余风险
must:
  - 在查看页面实现或源码前，先按 references/user-journey.md 独立推导或核对与界面实现解耦的 Expected Journey（不写死页面/Tab/按钮）。
  - 使用 scripts/review_runner.py 生成物理隔离无源码盲测 Prompt（ui_ux_experience.blind.md），仅凭用户身份、真实场景、目标与入口 URL 完成 Blind User Walkthrough 并记录全部 7 项观察点。
  - 在 business_acceptance（RV-BIZ-05）中完成 Expected vs Actual Journey 差异对比并逐项排查 8 大 Product Anti-pattern（AP-01..AP-08），能够识别“零 Bug 但产品认知错位”的 6 类反例：多 Tab 反复切换（AP-02）、首页精美但无主任务入口（AP-06）、AI 处理阻塞其他工作（AP-07）、模块平铺缺工作主线（AP-01）、提交后才露出决策信息（AP-05）、跨步重复填信息（AP-03）。
  - 在 ui_ux_experience（RV-UI-03）中提交覆盖全部 14 组 70 条 UX-* 规则的 meta.ux_coverage，且不通过/未验证项逐条标注 UX-* ID。
  - 对正例（符合目标用户高频操作习惯的优秀标准后台）正常放行通过，不为了找问题而强行推翻合理设计；同时遵守 UX-FLOW-03，不为了减少步数删除高风险确认或必要审阅。
  - 在 report.html 中呈现预期旅程 vs 实际旅程对比、8 大反模式排查状态与盲测观察结果，且明确区分 Agent 盲测代理观察与真实用户可用性测试的证据边界。
must_not:
  - 不因所有技术测试（单测/E2E/Bombadil/React Doctor）全绿就直接放行存在产品架构级旅程缺陷的设计。
  - 不在 Blind User Walkthrough 完成前向盲测 Reviewer 泄露 git diff、源码文件列表或内部模块关系说明。
  - 不对纯文案修改、纯视觉微调或不影响用户旅程的内部重构机械触发完整旅程走查。
  - 不对优秀标准后台强行套用 AP-01 过度审查。
expected_references:
  - skills/engineering-review-release/references/user-journey.md
  - skills/engineering-review-release/references/review-rules.md
  - skills/engineering-review-release/references/review-pipeline.md
  - skills/engineering-review-release/references/delivery-gates.md
stop_condition: "存在阻断级 Product Anti-pattern（如主任务无入口、决策依据缺失、核心旅程严重碎片化或阻塞）或 Blind Walkthrough 未完成时，结论不得为可以交付。"
---

# Negative Product Benchmark（产品认知与用户旅程反例评测集）

验证 Review 链路具备识别 **L4/L5 产品认知错误（实现零 Bug 但设计本身错位）** 的能力，同时通过第 7 个正例防止过度审查：

| # | 基准案例 | 类型 | 期望评审结果 |
|---|---|---|---|
| 1 | 所有功能可用，但用户必须在通知/任务/知识库/动态等多个 Tab 间反复切换（7 步本可 3 步） | 反例 | 命中 `AP-02`（旅程碎片化）与 `AP-01`（模块驱动 UI），阻断或要求旅程重组 |
| 2 | 首页视觉精致、规范全绿，但用户首次进入不知道从哪里开始主任务 | 反例 | Blind Walkthrough `entry_clarity = FAIL`，命中 `AP-06`（主入口/下一步缺失） |
| 3 | AI 分析任务可正常运行，但等待期间全屏弹窗锁死界面，用户不能处理其他工作 | 反例 | Blind Walkthrough `async_non_blocking = FAIL`，命中 `AP-07`（流程阻塞/内部复杂性） |
| 4 | 每个系统模块都有合理布局和组件，但整体没有围绕用户当前工作的主线 | 反例 | 命中 `AP-01`（Module-Driven UI），要求按任务主线组织工作台 |
| 5 | 所有按钮可用，但金额/风险/依据等关键决策信息在提交后才弹出 | 反例 | 命中 `AP-05`（Premature Decision）与 `UX-VIS-04`，阻断发布 |
| 6 | 所有测试通过，但跨步骤或异步返回后上下文丢失、用户必须反复填写相同信息 | 反例 | Blind Walkthrough `context_recovery = FAIL`，命中 `AP-03`（Context Loss） |
| 7 | 贴合运营/财务高频检索、比对、批处理习惯的优秀标准后台 | **正例** | 全部 `AP-01..08 = CLEAR`，正常判 `PASS`，严禁为找问题而强行改版 |
