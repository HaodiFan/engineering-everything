# Engineering Everything v0.18.0

## Product Cognition Review：用户旅程驱动评审 + 无源码盲测 + UI 设计理念配置化

这一版补上了开发后 Review 的 L4/L5 盲区：**不再只验证“设计有没有被无 Bug 地实现”，而是先独立验证“产品设计和用户旅程方向本身对不对”**，同时把 70 条 UI/UX 规则和团队优秀设计理念纳入脚本强约束。

仍保持现有 **13 个运行时 Skill、3 个执行 Phase（`1 → 4 并行 → 1`）与 6 个 Review 维度**，不膨胀目录结构。

## 新增：User Journey–Driven Review（产品认知与旅程审查）

- **轻量 Journey Contract**（`schemas/intent-card.schema.json` + `engineering-product-definition`）：开工前在需求卡可选 `journeys[]` 中先推导与界面实现解耦的用户旅程（`actor / trigger / goal / stages / success / experience_constraints`），刻意不写页面、Tab、按钮或内部模块名。
- **L4/L5 产品认知规则**（`references/user-journey.md`，规则目录扩至 50 条 `RV-*`）：
  - `RV-BIZ-05`（维度 2 `business_acceptance`）：先独立推导 Expected Journey 再对比实际产品路径，逐项排查 **8 大 Product Anti-pattern（`AP-01`..`AP-08`）**：模块驱动 UI、旅程碎片化、上下文丢失、步骤顺序错位、过早/盲目决策、主入口或下一步缺失、内部复杂性/异步阻塞、高低频权重错位。
  - `RV-UI-05`（维度 5 `ui_ux_experience`）：**Blind User Walkthrough（无引导用户走查）**，由 `scripts/review_runner.py` 物理生成**无源码、无 diff、无模块说明**的独立盲测 Prompt（`ui_ux_experience.blind.md`），仅凭用户身份、真实场景、目标和入口 URL 记录 7 项观察点。
- **严格触发边界与防过度审查**：纯文案、纯 CSS 样式微调或内部重构默认 `AUTO_NA`（支持 `--journey` / `--no-journey` 显式开关）；明确将“贴合高频习惯的优秀标准后台”作为正例放行，避免过度审查。

## 增强：14 组 70 条 UX 结构化机检与 HTML 旅程对比视图

- **`review_runner.py` 14 组 70 条 `UX-*` 机检**：`RV-UI-03` 强制提交覆盖全部 14 组（总计精确等于 70 条）的 `meta.ux_coverage`，所有不通过与未验证项必须逐条标注 `UX-*` ID 并与 `findings[]` 对齐。
- **`report.html` 升级**（`scripts/review_report_html.py`）：新增「预期旅程 vs 实际旅程」双栏对比（含步数冗余标注）、8 大反模式状态标签、Blind Walkthrough 7 项观察卡片与 14 组 70 条 UX 覆盖矩阵。

## 新增：优秀 UI 设计理念零配置注入与预设模板

- **免写 JSON 自动加载**：在项目根目录放 `DESIGN.md`，或在 `.evolution/design-principles/*.md`、`.evolution/taste/*.md`、`$EE_PRIVATE_ASSETS/design-principles/*.md` 放入设计理念文档，脚本自动注入 `ui_ux_experience`（及激活旅程审查时的 `business_acceptance`），同时严格排除在无源码盲测 Prompt 之外；提交时强制校验 `meta.company_cases_loaded = true` 并在 HTML 报告展示已载入基准。
- **可复制预设模板**：新增 `data/review_overlays/ui-design-philosophy.example.json` + `.md`，提供 6 条可验证设计原则（`DES-PHI-01`..`06`：任务主线优先、克制降噪、渐进披露、决策语境自洽、非阻塞即时反馈、设计系统一致性）。

## 新增：Negative Product Benchmark 评测集

- 新增 `evals/scenarios/product-journey-negative-benchmark.md`，包含 6 类“代码零 Bug 但产品认知错位”反例与 1 个“优秀标准后台正常放行”正例。

## 验证

- `scripts/sync_references.py --check --json`、`scripts/eval_scenarios.py validate --json`、`scripts/skill_doctor.py --json`、`scripts/self_evolve.py check --strict-install --json`、`scripts/self_evolve.py doctor --json`、`scripts/lesson.py validate` 全部通过。
- `python3 -m unittest discover -s tests` 全部 56 个单元测试通过；`python3 -m py_compile scripts/*.py`、`git diff --check` 及 EvoZeus Wrapper preflight 全部通过。

## 升级

```bash
git -C <你的 engineering-everything 目录> pull --ff-only
python3 scripts/install.py relink --target all
```
