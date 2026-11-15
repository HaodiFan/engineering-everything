---
name: engineering-execution-planning
description: Use when splitting a feature, writing an implementation plan, choosing worktree strategy, defining vertical slices, validation gates, or review roles before coding.
metadata:
  version: 0.14.0
---

# Engineering Execution Planning / 执行规划

把已定义的需求或设计拆成可交付的 vertical slices。计划不是任务堆砌，必须包含边界、顺序、验证和停止条件。

## 何时使用

- 用户问“怎么拆”“implementation plan”“这个功能怎么做”“worktree”“review roles”。
- 已有需求或设计，但还没有执行切片。
- 改动跨文件、跨模块、跨团队，直接实现风险高。

## 工作流

1. 确认输入真相源：requirements、design doc、issue、PRD 或用户明确指令。
2. 定 checkout/worktree 策略：当前分支、小修、并行任务或高风险改动。
3. 拆 vertical slices：每片都能产生可观察行为。
4. 为每片定义验证：单元、集成、E2E、静态检查、人工验收。
5. 指定 review roles：产品、架构、实现、测试、发布风险。
6. 团队交付时：每块工作只有一个负责人；多人并行前先约定好交接的接口；每条“做成的样子”想好怎么确认（方法参考 `references/verification-methods.md`，按事情大小选，不求全）；同时进行的事别太多，避免验收全堆到一个人身上。

## 输出模板

```text
工程路由: Execution Plan | Feature 拆解 | Planning
当前阶段: 5 Feature 规划
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

- 没有输入真相源，计划只能靠猜。
- 每个切片都无法独立验证。
- 计划混入无关重构、格式化、依赖升级或额外 feature。

## References

- `references/execution-pipeline.md`：implementation plan、worktree、review roles。
- `references/checklists.md`：计划和 PR readiness checklist。
- `references/stage-playbook.md`：Stage 5 及相邻阶段判断。
- `references/delivery-gates.md`：负责人、验收人分工与交付前检查。
- `references/verification-methods.md`：按事情大小选验证方法。
- `references/output-contracts.md`：对人表达规则与“开工前”输出。
