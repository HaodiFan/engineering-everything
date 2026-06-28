# Output Contracts（输出契约）

本文件是 Engineering Everything 输出字段的唯一事实源。Skill 文件、README 和 eval 只能引用本文件，不复制完整模板。

<!-- output-fields:start -->
- 工程路由
- 当前阶段
- 项目形态
- 参考依据
- 缺失内容
- 下一步 3 个动作
- 要创建/更新的文件
- 验证门禁
- 停止条件
- 变更文件
- 已运行验证
- 未运行检查及原因
- 剩余风险
- Findings
- Open Questions
- Test Gaps
- Change Summary
- scenario IDs
- entrypoint
- expected/actual
- pass/fail
- harness/model/date
<!-- output-fields:end -->

## 规划 / 路由输出

```text
工程路由: <主路由 | 命中场景 | 决策层>
当前阶段: <P POC/Spike | 0 想法 | 1 需求澄清 | 2 Spec | 3 架构 | 4 脚手架 | 5 Feature 规划 | 6 实现 | 7 验证 | 8 PR/发布 | 9 维护 | I 接手盘点>
项目形态: <Web+Backend | Desktop+Local Agent | Python Agent/CLI | Library/SDK | Full-stack Monorepo | Non-software Project | Organization System | Unknown>
参考依据:
- 路由规则: <命中的 SKILL.md 子 Skill 路由或不可突破规则>
- 已读 reference: <path -> 具体用于哪个判断>
- 外部/历史依据: <如使用 web / memory / repo 文件，说明来源和用途；未使用则写未使用>
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

规划类回答不能只说“用了 Engineering Everything”。必须把关键判断和已读取的 reference 对上，至少覆盖路由、阶段、项目形态、验证门禁这 4 类判断；未读取的候选 reference 不要伪装成依据。

## 执行收尾

```text
变更文件:
已运行验证:
未运行检查及原因:
剩余风险:
```

如果验证命令不可用，必须写明尝试过什么、为什么不能运行、风险是什么。

## Review 输出

Review 默认问题优先：

```text
Findings:
- [Severity] file:line - 问题、影响、建议

Open Questions:
Test Gaps:
Change Summary:
```

只有没有发现问题时，才先说没有发现阻塞问题；仍需说明测试缺口或剩余风险。

## 行为评估证据

```text
scenario IDs:
entrypoint:
expected/actual:
pass/fail:
harness/model/date:
```

行为 eval 只记录证据，不替代人工判断。失败场景必须能反向定位到 route、output contract 或 reference 分发问题。
