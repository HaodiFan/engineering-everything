---
name: using-engineering-everything
description: Use when starting, resuming, or switching an Engineering Everything session before selecting the kernel router or a direct engineering sub-skill.
metadata:
  version: 0.17.0
---

<!-- evozeus-harness-entry:v1 -->
**CRITICAL — 进入业务主链路前 MUST 使用 Read 工具读取并执行
[.evozeus-wrapper/skills/using-evozeus-harness/SKILL.md](.evozeus-wrapper/skills/using-evozeus-harness/SKILL.md)。**
<!-- /evozeus-harness-entry -->

路径说明：上面的 `.evozeus-wrapper/...` 相对**源仓库根目录**（本文件 realpath 往上两级），不在已安装的 skill 目录里。

# Using Engineering Everything / 启动器

本文件只管三件事：要不要进 Engineering Everything、会话中断后怎么接上、然后交给主路由。**路由表、规则和输出要求都在 `engineering-everything`，直接读它即可，开工前不需要再读别的文件。**

## 何时使用

- 用户显式使用 `$using-engineering-everything`。
- 复杂工程、组织、自动化、Skill、SOP、项目交付或旧项目接手。
- 用户只给了模糊目标，需要先判断做什么、做到哪一步。

普通小问题、单纯问答不进入。

## 会话接续

- 同一任务继续：先说清楚上次停在哪（路由、阶段、在改的文件、交付关口：想清楚 / 在做 / 验收 / 收尾），从那里继续，不重走已完成的步骤。
- 明显换了任务：重新按主路由判断，不沿用旧路由。
- 上下文被压缩后：先用两三句话重建上面这些状态，再继续。
- 拿不准是不是换任务：先问一句，不直接动手。

## 下一步

进入 `engineering-everything` 主路由。用户纠偏、要求沉淀 lesson 或升级 Skill 时，按主路由里的规则处理。
