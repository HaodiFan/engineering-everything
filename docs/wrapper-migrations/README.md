# Wrapper Migrations

本目录记录 EvoZeus-wrapper harness version 迁移。这里只记录 wrapper-managed 结构、脚本和治理逻辑的迁移，不记录目标 Skill 的业务内容。

## 迁移原则

- `.evozeus/wrapper.json` 是 wrapper harness version 的事实源。
- `SKILL.md` 只能追加 EvoZeus-wrapper 区域或 migration note，不重写目标 Skill 的业务规则。
- wrapper-managed files 可以按迁移方案复制或合并；如果已有本地修改，必须先做 merge review。
- Skill release version 和 wrapper harness version 是两条版本轴，不能互相覆盖。

## 每次迁移必须记录

- From wrapper version。
- To wrapper version。
- 迁移原因。
- Planned files / changed files。
- `SKILL.md` 的 append-only 处理结果。
- 验证命令和结果。
- 回滚方案。
