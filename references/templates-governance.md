# 治理模板

用于创建 `CONSTITUTION.md`、ADR、Folder Declaration、changelog / glossary 等治理文档。只在创建或更新这些文件时读取。

## CONSTITUTION.md

Constitution 只记录红线。一般偏好和代码风格放 `DEVELOPMENT.md`、lint 配置或 `docs/memory-bank/patterns.md`。

判断标准：违反会导致安全问题、数据丢失、合规违反、架构腐烂、无法回滚或交接失败，才是红线。

```md
# Project Constitution

- Status: active
- Last updated: <date>
- Owner: <tech lead / team>

## 0. 修改本文件的规则

- 新增/修改条款必须开 PR，至少 2 名维护者批准。
- 删除条款必须写明原因，并入 changelog。
- 临时豁免必须有明确截止时间和 owner。

## 1. 安全与合规

- [必须] 任何 secret 不入 repo。
- [必须] 用户数据访问必须有审计日志。
- [禁止] 在日志/异常/前端 console 打印 PII / 凭证 / token。
- [禁止] 绕过鉴权层直连数据库或外部数据源。

## 2. 架构边界

- [必须] router/controller 只做协议适配，不承载领域逻辑。
- [必须] 全局真相源唯一：`ARCHITECTURE.md` / `BRANCHING.md` / `DESIGN.md` / `folder-declaration-v0.md`。
- [禁止] 跳过 service/repository 层，从 UI 直连存储。
- [禁止] 在契约层写业务逻辑。

## 3. 数据与状态

- [必须] runtime data（output / logs / uploads / runtime）放 repo 外。
- [必须] schema 变更走 migration，不直接改库。
- [禁止] 把外部平台当产品真相源，除非 `ARCHITECTURE.md` 明确声明。

## 4. 代码与变更

- [必须] 一个分支一个意图。
- [必须] 涉及架构 / 状态机 / 存储 / 权限 / 公共 API / UI 模式的改动，先更新 spec 再写代码。
- [禁止] 直接 push 到 protected 分支。
- [禁止] 提交未验证的 AI 生成代码。

## 5. UI（UI 类项目）

- [必须] 新组件先入 `DESIGN.md` 再写代码。
- [必须] loading / empty / error / success 按 `DESIGN.md` 模式实现。
- [禁止] 局部发明 design token 或组件样式。

## 6. AI / Agent（AI 类项目）

- [必须] LLM 调用走统一 client。
- [必须] prompt 从 `prompts/` 或 prompt registry 加载，不内联硬编码。
- [必须] LLM 调用有 trace（provider / model / prompt_version / cost / latency / token）。
- [禁止] 把模型/provider 名硬编码到业务逻辑里。
- [禁止] 没有 eval baseline 就上生产。

## 7. 可观测性

- [必须] 关键路径有结构化日志（request_id / user_id / latency）。
- [必须] 错误必须上报到错误追踪系统。
- [禁止] 用 `print` / `console.log` 作为生产日志。

## 8. 红线触发处理

1. 立即停下，不要绕路实现。
2. 明示触发红线 §X.Y。
3. 给出三种路径：改方案规避 / 提议放宽红线 / 申请临时豁免。
4. 由 owner 决策。
```

## ADR

路径：`docs/decisions/ADR-<NNNN>-<kebab-title>.md`，编号连续。

何时写 ADR：选了某个有后果、未来要回溯的技术方向，例如选库、改边界、引入新模式、放弃某条路。决策结论写在 `ARCHITECTURE.md`，为什么这么选写在 ADR。

```md
# ADR-<NNNN>: <一句话决策标题>

- Status: <proposed | accepted | superseded by ADR-MMMM | deprecated>
- Date: <YYYY-MM-DD>
- Deciders: <names / roles>
- Linked Design Doc: <docs/design/active/...>
- Linked ARCHITECTURE 行: <Technical Baseline 中的对应维度>

## Context

<决策时面临什么问题？什么约束？什么不能改？>

## Options Considered

### 选项 A：<方案名>
- 优点：
- 缺点：
- 代价：
- 退出成本：

### 选项 B：<方案名>
- 优点：
- 缺点：
- 代价：
- 退出成本：

## Decision

选择 **<方案 X>**。

## Rationale

<为什么是 X，不是 A/B？关键 trade-off 是什么？>

## Consequences

正面：

负面：

中性：

## Validation

- <多久后重看？看什么指标？>
- <什么信号触发 ADR 重审？>

## References
```

旧 ADR 不删除。被替代时标记 `Status: superseded by ADR-MMMM`。

## Folder Declaration

```md
# Folder Declaration v0

## 顶层目录职责

- `apps/`: 用户可运行的应用
- `services/`: 后端服务
- `packages/`: 共享代码
- `agent/`: 默认 agent runtime，如适用
- `skills/`: 可复用 agent skills，如适用
- `docs/`: 文档
- `scripts/`: 开发和运维脚本
- `configs/`: 仅存配置模板

## 运行时目录：禁止提交

- `output/`
- `_reference_repo/`
- `node_modules/`
- `.venv/`
- `dist/`
- `build/`
- `runtime/`
- `logs/`
- `uploads/`

## 用户级目录

- `~/.<product>/data/`
- `~/.<product>/runtime/`
- `~/.<product>/logs/`

## 变更规则

- 新增顶层目录必须更新本文件。
- 重命名顶层目录必须先写 design doc。
```

## terminology-glossary.md

```md
# Terminology Glossary

| Term | Meaning | Source of Truth | Notes |
|---|---|---|---|
```

## changelog.md

```md
# Changelog

## <YYYY-MM-DD>

- <变更摘要>
- Docs updated:
- Validation:
```
