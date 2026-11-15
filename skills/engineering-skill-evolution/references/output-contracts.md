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
- 原始意图
- 需求卡
- 档位
- 需要拍板的事
- 交付结论
- 证据
- 上线准备
- 沉淀结论
<!-- output-fields:end -->

## 对人表达（所有输出都适用）

下面的字段是 Agent **必须做的判断**，不是必须逐行填写的表单。对人说话时：

1. **先结论**：第一句话说清楚“现在是什么情况 / 能不能做 / 需要你做什么”。
2. **业务语言**：先讲对用户和业务的影响，再讲技术原因。内部代号（G0、L2、BLOCKED、route ID 等）只出现在证据文件和工具输出里，正文用“工程底线”“重要改动”“缺证据”这样的说法。
3. **只说相关的**：不适用的项不列；全都正常的部分一句话带过。不要输出一整张每格都写“待定”的表。
4. **篇幅跟事情大小走**：小事几句话；大事也先给一屏能看完的摘要，细节放后面或放文件里。
5. **对方要做的事放最后、写具体**：要对方拍板什么、提供什么，最多 3 件，能给选项就给选项和推荐。
6. 字段名可以换成自然的小标题或融进句子，但对应的判断不能缺；评估时检查的是判断有没有做，而不是字面有没有出现。

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

规划类回答不能只说“用了 Engineering Everything”。必须把关键判断和已读取的 reference 对上，至少覆盖路由、阶段、项目形态、验证门禁这 4 类判断；未读取的候选 reference 不要伪装成依据。上面的模板是判断清单：对用户可以用自然段落和小标题表达，依据可以放在末尾一两行。

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

## 开工前：想清楚（Gate 1 Intent）

方法见 `delivery-gates.md` 第 3 节；需要存档时用 `schemas/intent-card.schema.json`。

```text
原始意图: <对方原话>
需求卡:
- 帮谁、什么场景、解决什么问题
- 做成了是什么样子（可演示的结果，每条附怎么确认）
- 这次不做什么
- 确定的 / 我的推测（可撤回）/ 还不知道的
档位: <小改 | 常规 | 重要 | 方向性> + 一句理由
需要拍板的事: <没有 | 冲突、2-3 个选项及代价、推荐、具体要对方决定什么、不等决定能先做什么>
```

目标是一页纸让提需求的人能直接说“对”或“不对”。

## 交付前：确认做对了（Gate 2 Quality）

方法见 `delivery-gates.md` 第 4 节；证据包用 `schemas/evidence-package.schema.json`，可用源仓库 `scripts/gate_check.py` 自动检查。

```text
交付结论: <可以交付 | 还不能交付：原因 + 最小修改建议 | 缺证据没法判断：缺什么、谁来补>
证据: <每条“做成的样子” -> 怎么确认的；只列相关项>
上线准备: <业务侧谁要知道、上线后看什么、出问题怎么撤回；不上线就不写>
未运行检查及原因:
剩余风险:
```

## 交付后：学到了什么（Gate 3 Evolution）

```text
沉淀结论: <不需要沉淀 + 一句理由 | 值得记下：发生了什么、记到哪里（项目 / 公司私有库 / 本仓库）、适用和不适用的场景、怎么验证有效、谁维护>
```

方法论类 lesson 仍按 `self-evolution-harness.md` 先开 issue，不直接写入 runtime 文件。

## 行为评估证据

```text
scenario IDs:
entrypoint:
expected/actual:
pass/fail:
harness/model/date:
```

行为 eval 只记录证据，不替代人工判断。失败场景必须能反向定位到 route、output contract 或 reference 分发问题。
