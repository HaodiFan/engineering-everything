# 修复：代码评审读不到坏味道规则库（0.15.1）

## Related issue

Owner 在使用中发现了这个问题，要求立即修复，认为很重要。没有单独开 issue。

## 问题与优化目标

`code-review-standards.md` 规定代码评审时，要以 `refactoring-rules.md` 的坏味道规则库为第一优先级。但 `refactoring-rules.md` 只分发给了 `engineering-refactoring`。`engineering-review-release` 以及另外 7 个带评审规范的 Skill 都没有这份文件，评审时 Agent 读不到它，只能跳过或者自己去找。

全面扫描还发现，共享参考文件之间按名字互相提到时，约有 150 处指向本 Skill 目录里没有的文件。绝大多数是“命中某场景时再读”的交叉引用。

**优化目标：**
- 代码评审一定能读到坏味道规则库。
- 其余按名字提到、但本 Skill 没带的参考文件，Agent 有确定的办法找到，找不到会明说。
- 同类问题以后会被检查拦下来。

## 优化方向与实现

- **硬依赖随 Skill 一起分发。** 在 `data/reference_distribution.yaml` 里新增 `requires:` 字段，`code-review-standards.md` 声明依赖 `refactoring-rules.md`。`sync_references.py` 会检查：凡是发了评审规范的 Skill，必须同时发坏味道规则库。`refactoring-rules.md` 因此分发到 9 个 Skill，约 1,100 行。`engineering-review-release` 的参考文件列表里也明确写上它。
- **按场景才读的文件，用统一规则去找，不再复制。** 每个子 Skill 的参考文件小节开头加一句：本目录没有的文件在源仓库 `references/` 下，即 Skill 真实路径往上两级；找不到就直说没读到。软链安装和插件安装这个路径都成立。
- **加检查。** `skill_doctor.py` 要求每个子 Skill 都写有这条规则；如果文件里出现带 `references/` 前缀、但在本 Skill 和源仓库都不存在的引用，直接报错。

## 验证

- `tests/test_sync_references.py`：缺少依赖时报错，补齐后通过；评审 Skill 确实带了坏味道规则库。
- `tests/test_entry_depth.py`：每个子 Skill 都有找文件的规则；不存在的引用会被报出来。
- 七项门禁全部通过。

## 发布

版本号 `0.15.1`（补丁）。合并后打 tag，发布 GitHub release。回滚只需要 revert 这个 PR。

## 不做

- 不把所有按名字提到的文件都复制到每个 Skill。那样会重新带回约 1 万行重复内容，抵消 0.15.0 的扁平化。
