---
name: engineering-architecture-design
description: Use when choosing technical architecture, project shape, stack, data source, boundaries, deployment model, AI/Agent architecture, or scaffold strategy.
metadata:
  version: 0.15.1
---

# Engineering Architecture Design / 架构设计

先判断项目形态和真相源，再选技术栈。架构不是偏好清单，而是对运行位置、数据来源、团队能力、退出成本和验证门禁的取舍。

## 何时使用

- 用户问技术栈、架构、选型、脚手架、从 0 搭项目、agent app。
- 项目形态不清楚：Web+Backend、Desktop+Local Agent、Python CLI、Library、Full-stack Monorepo 等。
- 涉及 AI/Agent、RAG、LLM 网关、工具调用、权限、审计、成本和延迟。

## 工作流

1. 先定项目形态：用户在哪里运行、真相源在哪里、是否跨 app 共享、是否需要本地 runtime。
2. 再定边界：前后端关系、后端形态、数据架构、协议、鉴权、异步、部署、可观测性。
3. AI 项目先做任务类型分流，不默认等于 LLM 项目。
4. 对关键决策写清推荐、反例、代价、退出成本和最小验证。
5. 触及长期边界时，要求 ADR 或 design doc 记录。
6. 重要改动涉及并发、多步骤状态、重试或权限流转时，写代码前先验证设计本身（从简单的状态表评审起步，复杂时再用 TLA+/TLC 或 P，见 `references/verification-methods.md`）；发现的反例要变成测试。

## 输出模板

```text
工程路由: Architecture | 架构设计 | Architecture
当前阶段: 3 架构 / 4 脚手架
项目形态:
参考依据:
- 路由规则:
- 已读 reference:
- 外部/历史依据:
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

## 停止条件

- 业务需求、数据源、权限或部署约束不清楚，却准备新增架构层。
- 只凭流行技术选型，无法解释代价和退出成本。
- 没有 spec，却要新增状态机、存储、权限或公共 API。

## References（用到时再读）

本目录没有的参考文件（文中按名字提到的），在源仓库的 `references/` 下：取本 Skill 目录的真实路径（它是软链）往上两级就是源仓库。找不到就直说没读到，不要假装读过。

- `references/architecture-cases.md`：要做通用架构选型、比较方案时。
- `references/architecture-cases-ai.md`：涉及 AI / Agent 架构时。
- `references/app-for-agent-design-paradigm.md`：要设计给 agent 操作的 app 时。
- `references/project-blueprints.md`：要按项目形态起脚手架时。
- `references/templates-governance.md`：要写 ADR / CONSTITUTION 时。
- `references/prompts-guide.md`：要初始化项目的 `docs/prompts/` 时。
- `references/checklists.md`：架构定稿或发布前自查时。
- `references/verification-methods.md`：重要改动涉及并发、状态机、权限流转，考虑做设计验证时。
