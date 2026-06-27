# Agent Operating Standards

用于约束 agent 在软件开发任务中的默认执行纪律。它补足 `execution-pipeline.md`：前者管 Stage 5-8 的 gate 和验证，本文管 agent 容易偷懒、过度自信、过度实现或引用不可靠来源的问题。

本文适用于所有正式软件任务；POC / Spike 可轻量执行，但仍不能跳过安全、合规、secret 和验证证据。

---

## 1. Skill / Reference 编写标准

新增或重写 Skill 内容时，优先使用这个结构；内容太长时下沉到 `references/`，`SKILL.md` 只保留路由。

| Section | 目的 |
|---|---|
| Overview | 说明这个流程解决什么问题 |
| When to Use | 明确触发条件和不适用场景 |
| Process | 可执行步骤，不写空泛原则 |
| Common Rationalizations | agent 常见跳步理由与反驳 |
| Red Flags | 执行中出现哪些信号说明流程走偏 |
| Verification | 完成判定和证据要求 |

写法要求：

- **Process over prose**：写动作、输入、输出、停止条件，不写长篇理念。
- **Evidence over assumption**：每个完成判定要能用命令、diff、截图、样本、日志或 review 结论证明。
- **Progressive disclosure**：正文只放路由和高频规则，长 checklist / case / 模板放 reference。
- **No duplicated truth**：同一规则只能有一个真相源，其他文件只引用。

---

## 2. Common Rationalizations

| Rationalization | Reality |
|---|---|
| “这个很小，不需要看 spec。” | 小改可以跳过完整计划，但仍要知道验收标准和不改什么。 |
| “我先实现完，最后一起测。” | 多个未验证 slice 会叠加错误；每个可观察 slice 完成后先跑最小相关验证。 |
| “我顺手把旁边代码整理一下。” | 无关清理会污染 diff，增加 review 和回滚成本；记录为后续任务，不混进本 PR。 |
| “浏览器点一遍就算测过。” | 默认后端/API/service/contract/fixture/replay 优先；浏览器模拟只在显式触发或产品能力本身需要时运行。 |
| “这个库我知道怎么用，不用查。” | 新依赖、外部 API、框架升级、平台规则、鉴权/支付/合规等必须看官方来源或项目内已锁定版本。 |
| “先把大 PR 做出来，后面再拆。” | 大 diff 让 review 失效；先在 plan 阶段拆 slice 和 PR 边界。 |
| “测试失败应该是环境问题。” | 先记录失败命令、错误和假设；只有证据支持时才归因为环境。 |
| “生成文件应该一起提交。” | 只有项目约定要求的 lockfile、migration、schema snapshot 等可提交；build output、runtime data、secret 不入仓。 |
| “我可以自己 stash / reset 处理脏工作区。” | 用户未提交改动受保护；没有授权不得 stash、reset、clean 或 revert。 |

---

## 3. Red Flags

- 需求、scope、验收标准还不清楚就开始写代码。
- 计划按“后端 / 前端 / 测试”横向分层，缺少可观察 vertical slice。
- implementation plan 没有 validation gate、source docs、rollback 或 review roles。
- 一次改动同时包含 feature、refactor、格式化、依赖升级和文档重写。
- diff 很大但没有拆分理由，或没有说明哪些文件只是机械生成 / 删除。
- 新增依赖、外部平台接入、框架 API 用法没有官方来源或本项目锁定版本依据。
- 用浏览器模拟替代后端/API/service 自测。
- 发现死代码、旧逻辑、旁路配置后直接删除，没有 owner 确认。
- 多 agent / 多任务并行但没有独立 worktree 或 disjoint write set。
- 收尾只说“已完成”，没有验证命令、未跑项和剩余风险。

---

## 4. Source-Driven Gate

当技术事实可能变化，或错误代价较高时，必须走 source-driven check。

### 必须查官方或一手来源

- 新增或升级框架、库、SDK、模型 provider、云服务、支付、鉴权、CI/CD、部署平台。
- 使用第三方 API、平台 ToS、浏览器/RPA 自动化规则、爬取/采集边界。
- 安全、隐私、合规、加密、认证、授权、日志脱敏。
- 用户问“最新 / 当前 / 今天 / 现在能不能 / 还支持吗”。
- 项目本地文档与记忆冲突，且代码中没有明确真相源。

### 来源优先级

1. 项目内锁定版本、lockfile、ADR、README、官方 SDK 类型与测试。
2. 官方文档、官方 changelog、官方 migration guide、标准/RFC。
3. 源码、issue、release note。
4. 博客、社区答案、二手教程只能作为参考，不能作为唯一依据。

输出时记录：

- source 名称和链接（或项目内文件路径）。
- 版本 / 日期 / 适用范围。
- 哪些结论是来源明确写的，哪些是 agent 推断。

---

## 5. Change Size Rules

行数只是启发式，不是绝对门禁；真正目标是可 review、可回滚、可验证。

| Diff size | 默认处理 |
|---|---|
| <100 行 | 通常可作为小修或单 slice；仍需验证。 |
| 100-300 行 | 理想 PR 范围；适合一个明确行为变化。 |
| 300-500 行 | 可以接受，但 PR body 要解释为什么仍是一个 topic。 |
| 500-1000 行 | 默认拆分；若不拆，必须说明机械变更、删除、生成文件或强依赖原因。 |
| >1000 行 | 必须拆分，除非是 owner 明确批准的机械迁移、大文件删除或生成快照。 |

拆分优先级：

1. 先拆无行为变化的重构 / 格式化 / 依赖升级。
2. 再按 vertical slice 拆用户可观察行为。
3. 跨端协作时先拆 contract / schema / types。
4. 高风险变更（权限、数据迁移、支付、状态机）单独成 PR。

---

## 6. Lifecycle Prompt Aliases

宿主支持 slash command 时可以映射；不支持时把它们当作可复用 prompt 名称。

| Alias | 对应本 Skill 阶段 | 读取 |
|---|---|---|
| `/spec` or `define` | Stage 1-2 | `stage-playbook.md`、`spec-templates.md` |
| `/plan` | Stage 5 | `execution-pipeline.md`、`checklists.md` |
| `/build` | Stage 6 | `execution-pipeline.md`、`agent-operating-standards.md` |
| `/test` | Stage 7 | `checklists.md`、`execution-pipeline.md` |
| `/review` | Stage 7-8 | `code-review-standards.md`、`execution-pipeline.md` |
| `/ship` | Stage 8 | `checklists.md`、`execution-pipeline.md` |
| `/learn` | Stage 8-9 | `lessons.md`、`patterns-skill.md`、`memory-bank-guide.md` |

别名只负责入口，不改变本 Skill 的阶段判断。命中业务场景时仍要读取 `scenario-playbooks.md`。

---

## 7. Owner 已确认的默认策略

以下作为默认工程策略执行：

- **不自动逐 slice commit**：每个 slice 要验证，但只在用户要求 commit/PR、项目规范要求，或当前任务本身是提交/发 PR 时提交。避免 agent 制造过多低质量 commit。
- **不默认 fan-out 多 agent review**：高风险 PR 必须跑对应 review roles，但多 agent 并行只在用户明确要求、宿主明确授权、或 release/ship gate 写明需要时运行。
- **change size 是启发式 + 大 PR 硬门禁**：500 行以内按 review 启发式处理；500-1000 行默认拆分，不拆必须解释；超过 1000 行必须拆分，除非 owner 明确批准机械迁移、大文件删除或生成快照。
- **不强制每阶段人工确认**：需求不清、高风险、触动架构边界、状态机、权限、存储、公共 API、外部平台规则时必须确认；小修、文档、单 PR follow-up、明确验收标准的任务可直接推进。
