# Refactoring Rules

本文件把重构固化为 agent 可执行的判断规则。它吸收《重构》一书中常见坏味道与重构手法的工程化思想，但不复述书本内容；目标是让 agent 在重构、清理、模块化、PR review 和接手旧项目时，先识别明确坏味道，再选择小步、可验证、行为保持的手法。

## 1. 重构定义

重构是**不改变外部可观察行为**的内部结构调整。

不属于重构：

- 顺手加功能、改流程、改权限、改状态机。
- 改 API 契约、改数据含义、改业务规则。
- 大范围格式化、依赖升级、框架迁移和业务修复混在一起。
- 没有测试保护却移动核心逻辑。

如果行为改变不可避免，先退回 Stage 2/3/5：补 spec、ADR 或 implementation plan，再按 feature / migration 处理。

## 2. 进入重构前的 Gate

| Gate | 必须满足 | 不满足时 |
|---|---|---|
| Intent Gate | 说明要消除哪类坏味道 | 不做“看着更干净”的泛清理 |
| Behavior Gate | 明确哪些行为必须保持 | 先补 characterization test / smoke check |
| Scope Gate | 只聚焦一个 topic | 拆 PR，不混 feature / migration / format |
| Safety Gate | 不触 Constitution 红线 | 停下让 owner 决策 |
| Architecture Gate | 边界变化有 ARCHITECTURE / ADR | 不借重构偷偷改架构 |
| Validation Gate | 有可重复验证命令或人工验收步骤 | 先补验证路径 |

## 3. 坏味道到手法映射

| 坏味道 | 识别信号 | 优先手法 | 验证重点 |
|---|---|---|---|
| Long Function | 一个函数同时做解析、判断、IO、副作用 | Extract Function / Split Phase | 覆盖输入输出和副作用顺序 |
| Large Class / God Service | 一个类同时管协议、领域、存储、外部集成 | Extract Class / Move Function | 保持公共方法行为和依赖注入 |
| Duplicated Code | 同一规则多处复制 | Extract Function / Shared Policy | 全部调用点同测例通过 |
| Divergent Change | 一个文件因多类需求频繁修改 | Split Responsibility | 每类变化有唯一 owner |
| Shotgun Surgery | 小改动要跨很多文件同步 | Introduce Owning Layer / Centralize Mapping | 新旧入口都走同一策略 |
| Primitive Obsession | 状态、角色、动作大量裸字符串 | Introduce Enum / Value Object | 非法值、兼容旧数据 |
| Data Clumps | 多个参数/字段总是一起出现 | Introduce Parameter Object | 序列化、API schema、默认值 |
| Feature Envy | 一个函数大量访问别的对象数据 | Move Function | 调用者不感知位置变化 |
| Temporary Field | 字段只在少数流程有意义 | Extract Class / Explicit State | 字段缺失、空值、旧数据 |
| Conditional Complexity | if/switch 持续增长 | Strategy / Dispatch Table / State Machine | 每个分支都有测试 |
| Middle Man | 包装层只转发，没有抽象价值 | Inline Function / Remove Layer | 公共 API 兼容或迁移说明 |
| Inappropriate Intimacy | 模块互相读内部细节 | Hide Delegate / Move Responsibility | 边界和 import 方向 |
| Global Mutable State | 共享可变单例影响测试和并发 | Inject Dependency / Context Object | 并发、测试隔离、初始化顺序 |
| Comment-as-Patch | 注释解释绕路而非表达概念 | Extract Concept / Rename | 代码自解释，注释只留原因 |
| Speculative Generality | 为未来预留抽象但当前无用 | Collapse Abstraction | 当前场景不丢能力 |

## 4. 操作规则

1. **先测试，后移动**：没有保护网时先补 characterization test、fixture、contract test、CLI smoke 或人工验收脚本。
2. **一次只消除一个 smell family**：例如先处理重复规则，不同时做命名、分层、依赖升级。
3. **小步可回滚**：每一步都能独立跑测试；失败时能撤回到上一小步。
4. **先抽概念，再移动边界**：先用命名和函数抽取让意图清楚，再考虑拆类/拆包。
5. **保持公开契约稳定**：公共 API、CLI、schema、配置名默认不变；要改必须走 migration。
6. **边界变化要写文档**：跨 layer、跨 package、truth source、状态机、权限边界变化必须同步 ARCHITECTURE / ADR / folder declaration。
7. **不要用格式化掩盖结构变化**：格式化和重构分开提交或分开 PR。
8. **不要“顺手修 bug”**：发现 bug 时先记录，另起 bug fix 或明确把本任务转为行为变更。

## 5. 测试保护规则

按风险选择最小保护网：

| 改动类型 | 最小验证 |
|---|---|
| 提取函数 / 改命名 | 现有单元测试或新增针对原函数行为的测试 |
| 移动类 / 拆 service | service/API/integration 测试 |
| 合并重复规则 | 对每个旧调用点跑同一组规则测试 |
| 状态/角色 enum 化 | 合法值、非法值、旧数据兼容测试 |
| 分层边界移动 | contract test + import/lint/typecheck |
| 存储访问封装 | migration/smoke + 读写样本 |
| 前端组件重构 | component test 或最小交互 smoke；必要时截图 |
| RPA/OCR/AI pipeline 重构 | fixture/replay/eval，保留样本输出对比 |

没有自动化测试时，先写可重复的 smoke command 或人工验收步骤，并在 PR body 说明覆盖缺口。

## 6. PR 拆分规则

推荐拆分顺序：

1. **测试保护 PR**：补 characterization / regression tests，不改行为。
2. **机械移动 PR**：rename、move、extract，不改逻辑。
3. **结构改善 PR**：拆职责、引入 owning layer、消除重复。
4. **行为变更 PR**：如有功能或 bug 修复，单独处理。
5. **清理 PR**：删除旧入口、旧适配、死代码。

可以放在一个 PR 的条件：

- 文件少、diff 小、单一 smell、验证明确。
- 没有公共契约、数据、权限、状态机或运行时边界变化。

必须拆 PR 的条件：

- 预估 diff 大于 500 行。
- 同时包含 feature / bug fix / refactor / format / dependency upgrade。
- 跨模块、跨 package、跨服务或影响公共 API。
- review 需要不同 owner 批准。

## 7. 不该重构的场景

- 用户只是要快速修线上问题，先恢复服务。
- 需求或目标架构不清楚，先补 spec/ADR。
- 旧项目刚接手，尚未完成 as-is 盘点。
- 测试不可运行，且无法补最小 smoke。
- 当前 checkout 有不明来源脏改动，容易污染 diff。
- 重构收益无法说明，只是风格偏好。

## 8. Agent 输出模板

规划重构时使用：

```text
工程路由: Refactor | <命中坏味道> | Execution/Review
当前阶段: 9 维护
行为保持声明:
命中的坏味道:
不做什么:
前置测试 / smoke:
重构步骤:
影响文件:
验证门禁:
需要同步的文档:
停止条件:
```

PR review 发现重构问题时使用：

```text
Finding: <坏味道 / 风险>
位置:
为什么影响维护:
建议手法:
前置测试:
是否阻塞本 PR:
```

## 9. 与其他 reference 的关系

- `code-review-standards.md`：负责发现坏味道和行为风险；命中重构问题时回到本文件选手法。
- `stage-playbook.md`：负责生命周期路由；Stage 9 读取本文件。
- `execution-pipeline.md`：负责 checkout/worktree、plan、review、validation gate。
- `checklists.md`：负责 PR readiness 和 refactor checklist。
- `inheriting-projects.md`：旧项目未盘点前不进入大重构。
