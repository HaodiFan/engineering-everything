---
name: engineering-review-release
description: Use when reviewing code, PRs, merge readiness, CI failures, release risk, rollback plans, or deciding whether a change is safe to ship.
metadata:
  version: 0.16.0
---

# Engineering Review Release / Review 与发布

默认 code-review 立场：问题先行，按严重度列 bugs、风险、回归、缺测试和发布阻断。摘要永远次要。

## 何时使用

- 用户要求 review、PR、merge、release、发布、CI、是否 ready。
- 需要判断行为风险、测试证据、回滚和发布门禁。
- 需要修 CI 或检查发布流程。

## 工作流

1. 先看 diff、相关上下文、需求卡和测试证据。
2. 按严重度列 findings，必须有文件/行号或明确证据。React 项目先用 react-doctor 扫这次改动新引入的问题（`references/react-doctor.md`），结果当线索，逐条按本 Skill 的口径定级。
3. 区分阻断、建议、开放问题和残余风险。
4. 发布前检查：配置、迁移、回滚、监控、兼容、数据风险。
5. 没有问题就明确说无发现，并说明测试缺口。

### 团队交付：交付前确认做对了

按 `references/delivery-gates.md` 第 4 节，先问“业务问题解决了吗”，再看功能、体验、审美和工程底线（改动涉及界面时，“用起来顺吗 / 看起来对吗”交给 `engineering-ui-ux-audit`，拿回它的结论和未验证项）；只深挖跟这次改动相关的项，无关的一句话带过。方法按事情大小从 `references/verification-methods.md` 里挑，不求全。

- 结论只有三种：可以交付 / 还不能交付（附最小修改建议）/ 缺证据没法判断（说清缺什么、谁补）。
- 没证据不算通过；“CI 绿了”“开发说测过了”只是线索，不是验收结论。开发用的 Agent 不当验收人。
- 有发布时，业务侧（谁要提前知道、上线后看什么业务指标、出事怎么兜底）和技术侧（放量、撤回）一起确认。
- 需要留档时写证据包，用源仓库的 `scripts/gate_check.py check <证据包>` 自动检查。本 skill 是软链安装的：取本目录真实路径向上两级就是源仓库；找不到就说明未机检，不要假装检查过。

## 输出模板

```text
Findings:
Open questions:
Change summary:
Tests / release gates:
Residual risk:
```

团队交付时用 `references/output-contracts.md` 的“交付前”输出，先给结论。

## 停止条件

- 没有 diff、PR、分支或变更范围，无法 review。
- 用户要求“批准”但缺运行时验证，只能做静态 review。
- 发现 P0/P1 行为风险、数据风险或安全风险未处理。

## References（用到时再读）

本目录没有的参考文件（文中按名字提到的），在源仓库的 `references/` 下：取本 Skill 目录的真实路径（它是软链）往上两级就是源仓库。找不到就直说没读到，不要假装读过。

- `references/code-review-standards.md`：做代码评审时。
- `references/refactoring-rules.md`：代码评审时一起读，用它的坏味道规则库识别问题、给出改法和是否阻塞合并。
- `references/react-doctor.md`：评审或验收的是 React 项目时。
- `references/delivery-gates.md`：团队交付，要下“能不能交付”结论或做上线准备时。
- `references/verification-methods.md`：要挑验证方法、判断证据够不够时。
- `references/checklists.md`：PR 合并或发布前自查时。
- `references/execution-pipeline.md`：要安排 review 角色或发布门禁时。
- `references/stage-playbook.md`：拿不准处于 7-8 哪个阶段时。
- `references/output-contracts.md`：要写正式的 review 或“交付前”输出时。
