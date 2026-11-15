---
name: engineering-build-verify
description: Use when implementing, fixing bugs, migrating code, wiring APIs, running validation commands, or closing a build/test loop with minimal scoped changes.
metadata:
  version: 0.15.0
---

# Engineering Build Verify / 构建验证

执行用户明确要求的实现、修复或迁移。默认最小改动、最小切片、先读现状、验证闭环，不顺手重构。

## 何时使用

- 用户要求实现、修 bug、迁移、接接口、跑验证命令。
- 已有 repo 或文件需要修改。
- 任务目标足够明确，可以进入代码/配置/脚本变更。

## 工作流

1. 先读相关代码、配置、测试和现有模式。
2. 明确成功标准和验证命令。
3. 只改直接服务目标的文件；不处理无关坏味道。
4. 改完立即跑最接近风险面的验证。
5. 收尾说明变更文件、已运行验证、未运行检查及原因、剩余风险。
6. 团队交付时：对照需求卡里“做成的样子”逐条留证据（对应这次要交付的版本），方便验收人复核；不要用假数据或截图冒充走通了。

## 输出模板

```text
变更文件:
已运行验证:
未运行检查及原因:
剩余风险:
```

## 停止条件

- 目标不明确且错误假设会破坏数据、权限、公共 API 或生产行为。
- 工作树存在相关未知改动，无法判断是否用户改动。
- 验证失败且无法定位到可继续推进的下一步。

## References（用到时再读）

- `references/execution-pipeline.md`：切片不清楚、或要按 source-driven gate 推进时。
- `references/stage-playbook.md`：拿不准当前处于哪个阶段时。
- `references/agent-operating-standards.md`：多 agent 协作或执行纪律有疑问时。
- `references/checklists.md`：收尾、准备 PR 时。
- `references/delivery-gates.md`：团队交付、需要留交付证据时。
- `references/verification-methods.md`：常规测试不够、要挑更合适的验证方法时。
