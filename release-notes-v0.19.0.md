# Engineering Everything v0.19.0

## 高吞吐 Review 引擎：单批次合批 + 三档 Profile + 9 大领域技术栈按需隔离 + Delta 复审

这一版针对真实 PR 评审中的核心耗时与误触发瓶颈（中位 ~20.9 分钟、98 KB 冗余 Prompt、单轮 `carry=0` 全量重跑、monorepo 目录误触发重度旅程审查）进行了全面提速与精准化重构，在不放松任何一条硬门禁机检的前提下，大幅压缩大模型 API 往返次数与上下文体积。

## 核心升级

### 1. 两阶段零等待并发 DAG + 单批次合批（`--dispatch auto|bundle|parallel`）
- **两阶段精准依赖**（`data/review_pipeline.json` schema v5）：合并为 `core_parallel_review` + `release_gate`；维度 1–4（`engineering_baseline`、`business_acceptance`、`code_quality`、`security_architecture`）在 `t=0` 零等待解锁，维度 5（`ui_ux_experience`）仅依赖 `engineering_baseline` 落盘即解锁。
- **单批次合批（`bundle`，一次输入一次输出）**：`fast` / `standard` 档默认将所有就绪的非盲测静态维度浓缩为 1 份去重 `bundle_batch.md`——AI 只读一遍 diff、一次输出全部维度 JSON 数组并经 `submit-batch` 一次性落盘（仍对每个维度执行 100% 完整 Python 硬校验）：
  - **纯后端 / 脚本 / CLI / 采集 PR**：全程仅需 **1 次 AI 批次**即可直达 `finalize`。
  - **小 UI PR（`fast`）**：仅需 **2 次 AI 批次**（静态 4 维合批 + 轻量 UI）。
  - **复杂旅程 UI PR（`standard`）**：**3 次**（无源码盲测 `.blind.md` 强制物理隔离，永不合批）。
  - **大版本发布 / L2+（`full`）**：默认保持 `parallel` 多 Subagent 独立深审，也可按需 `--dispatch bundle` 合批。

### 2. 三档智能 Profile 与 Pointer-First 瘦身 Prompt（`-54% ~ -77%`）
- **三档自动定档（`--profile auto|fast|standard|full`）**：小体量干净 PR（`<= 250` 行、`<= 8` 文件、无安全/架构/旅程/发布面）自动启用 `fast`（高信号核心规则 + 命中的技术栈专项，免填 14 组 UX 矩阵）；常规 PR 走 `standard`；团队交付/发布/L2+/声明 `journeys[]` 自动走 `full`。
- **Pointer-First 瘦身 Prompt + 快捷提交**：默认仅注入规范路径索引与紧凑提交契约（总 Prompt 体积下降 54%–77%，保留 `--full-prompts` 兼容全文内联）；新增 `submit --ux-all-pass` / `meta.ux_coverage_preset="all_pass"` 一键展开 14 组 70 条 UX 矩阵。

### 3. 9 大领域技术栈按需挂载（不涉及就不 Review）
- 新增 `project_types` 声明式领域包与 `--project-type`（支持多标签组合与 Overlay JSON 自定义扩展），按「仓库清单 + 本次 diff 实际触达范围」精准激活，无关技术栈保持 `AUTO_NA` 零干扰：
  - `web_ui`、`desktop_app`（`RV-DESK-01`）、`mobile_app`（`RV-MOB-01`）、`browser_extension`（`RV-EXT-01`）、`data_automation`（`RV-DATA-01`）、`backend_api`、`ai_agent`（`RV-AI-01`）、`cli_sdk_tool`（`RV-DX-01`）、`infra_devops`（`RV-INFRA-01`）。
- 规则目录扩展至 **55 条稳定编号 `RV-*`**（50 条通用核心 + 5 条按领域按需激活专项），并在 Prompt 中自动注入命中技术栈的专属注意事项。

### 4. 精准信号去噪、Stage 0 快返预检与 Delta 增量复审
- **去噪**：信号匹配自动剥离 `apps/<name>/` 等 monorepo 前缀并排除测试文件；`has_journey_surface` 需满足 `diff > 120` 行或 `delivery`/`release` 或需求卡声明 `journeys[]`，彻底消除小改动误触发重度旅程审查。
- **Stage 0 Fast-Fail**：自动检测合并冲突标记（`has_merge_conflicts`）与 `--draft`，置顶 `fast_fail_advisories` 避免浪费全量算力。
- **Delta `recheck`**：使用 `git log --no-merges` 过滤合并上游带来的无关文件噪音；按精确文件桶重开受影响维度（`business_acceptance` 仅失败重开），并对重开维度自动继承上轮 `PASS` 规则，只需复验失败/变动项（强制全量加 `--full-recheck`）。

## 验证

- `scripts/sync_references.py --check --json`、`scripts/eval_scenarios.py validate --json`、`scripts/skill_doctor.py --json`、`scripts/self_evolve.py check --strict-install --json`、`scripts/self_evolve.py doctor --json` 全部通过。
- `python3 -m unittest discover -s tests` 全部 60 个单元测试通过；`python3 -m py_compile scripts/*.py` 与 `git diff --check` 全部通过。

## 升级

```bash
git -C <你的 engineering-everything 目录> pull --ff-only
python3 scripts/install.py relink --target all
```
