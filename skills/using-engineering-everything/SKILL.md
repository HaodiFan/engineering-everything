---
name: using-engineering-everything
description: Use when starting, resuming, or switching an Engineering Everything session before selecting the kernel router or a direct engineering sub-skill.
metadata:
  version: 0.12.0
---

# Using Engineering Everything / 启动器

这是 Engineering Everything 的 bootloader。它只负责决定是否进入工程化路由、恢复会话上下文、加载主路由和约束输出，不承载具体 route 表。

## 何时使用

- 用户显式使用 `$using-engineering-everything`。
- 任务是复杂工程、组织、自动化、Skill、SOP、项目交付或旧项目接手。
- 会话 resume 后需要判断是继续原 route，还是任务已经切换。
- 用户先给了模糊目标，需要先判断阶段、形态、边界、验证门禁。

## 加载顺序

1. 读取本文件，确认是否进入 Engineering Everything。
2. 读取 `references/route-contract.md`，理解 route 字段和裁决方式。
3. 读取 `references/output-contracts.md`，确定本次输出字段。
4. 读取 `references/codex-tools.md`，确认工具和收尾边界。
5. 进入 `engineering-everything` 主路由；主路由再按 `data/routes.yaml` 命中子 Skill。

## Session / Resume

- 如果用户继续同一任务，先恢复最近一次工程路由、阶段、项目形态、验证门禁和打开的文件。
- 如果用户明显换任务，重新进入主路由，不沿用旧 route。
- context compaction 后，先重建 route summary，再继续执行。
- 不确定是否切换任务时，先问一个澄清问题，不直接实现。

## 停止条件

- route 不明，且缺少足够信息判断下一步。
- 需求、合规、数据源、权限或 owner 决策缺失，却准备进入实现。
- 重构或迁移没有验证门禁。
- 用户不满意时，先 issue-first 询问是否沉淀 lesson，不把主任务默认改路由到 learn。

## Self-Evolution Handoff

只有用户明确要求 `/learn`、`/lesson`、`/pattern`、`/self-evolve`、升级 Skill，或确认要把纠偏沉淀为 lesson issue 时，才交给 `engineering-skill-evolution`。

## References

- `references/route-contract.md`：route 字段契约和裁决顺序。
- `references/output-contracts.md`：规划、执行、review、eval 输出契约。
- `references/codex-tools.md`：Codex 工具使用和收尾边界。
