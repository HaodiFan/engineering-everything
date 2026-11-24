# 明确 Bombadil 的评审执行步骤（未发布）

## Related issue

https://github.com/HaodiFan/engineering-everything/issues/31

Owner 明确要求修改 Skill。问题是工具目录没有连接到评审动作，复杂 UI 可以在没有属性探索决策的情况下结束审查。

## Scope

- Review、UI Audit 在走查前作明确适用性判断；适用时执行 Bombadil。
- 共用 references/bombadil.md 说明隔离、版本核验、属性、动作边界、有界执行、证据及失败处理；命令对照官方手册 v0.7.10，实际运行仍核对已安装版本。
- 方法目录及 UI 验收手册引用该流程；由 reference_distribution 同步分发，技能安装保持 canonical symlink。
- 澄清发现 P0/P1 阻断发布；提前结束审查必须保留未运行项。
- 添加复杂可运行 UI、只有截图、工具不可用三类行为场景，复用现有场景验证器；不把场景格式校验说成模型行为验证。

## Non-goals

不改产品代码、不安装 Bombadil、不自动测试外部应用、不增加全局依赖、不发布、不改通用 evidence schema 或 gate checker。后者仍只检查汇总证据，不自动推断 UI 复杂度。

## Acceptance

只读命中子技能即可知道何时进入 Bombadil；适用则有实际命令和有界结果，不能只写推荐；无法运行必须记录尝试、原因、补证及风险；截图任务不伪造运行。工具默认属性的 smoke 不能冒充业务状态覆盖。

## Verification / rollback

运行参考分发、行为场景格式、skill doctor、自进化、lesson、Python 测试及编译检查；核对 Codex / Agents 安装指向源文件。回滚仅撤销本次命中的文件与分发副本，保留原有未跟踪文件。未做真实应用的 Bombadil 探索和多模型行为实验。
