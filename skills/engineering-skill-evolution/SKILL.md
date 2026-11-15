---
name: engineering-skill-evolution
description: Use when evolving a skill, capturing lessons, promoting patterns, changing routes, updating references, installing skills, validating skill packages, or publishing skill releases.
metadata:
  version: 0.15.0
---

# Engineering Skill Evolution / Skill 自进化

Skill 升级不是继续堆理念，而是把纠偏分成 lesson、pattern、reference、script/gate 或 install sync，并用验证门禁收口。

## 何时使用

- 用户说“记住”“以后都这样”“自进化”“升级 skill”“拆成子 skill”“发布 skill”。
- 需要改 `SKILL.md`、routes、reference、scripts、plugin manifest 或安装路径。
- 需要比较本地安装、source repo、GitHub release 或同步 Codex/Agents 副本。

## 工作流

1. 先定位 canonical source；安装副本只作为部署目标。
2. 判断变更类型：lesson、pattern、reference、script/gate、route、install、release。
3. 主 `SKILL.md` 只做路由；新知识默认下沉 reference，重复动作进入 scripts。
4. 改结构、版本、路由或安装路径后，必须跑 self-evolve 与 doctor gates。
5. 发布前再检查 GitHub origin、release tag、安装副本和版本一致性。

### 团队交付：交付后看学到了什么

按 `references/delivery-gates.md` 第 6 节：大多数任务不需要沉淀，直接结束。只有可能再发生或代价高的问题才记下来，并先想清楚记到哪里：需求和审美案例记到项目或公司私有库；同类错误第二次出现就变成自动检查；只有通用的 Agent 方法问题才按 issue-first 进本仓库。公司案例和客户信息不进本仓库，也不进公开 issue。

### 发布闭环（EvoZeus-CoEvolve 治理）

行为变更走可追踪的发布闭环：

1. 先创建或关联 Skill Feedback Issue，记录问题、期望、复现场景和证据边界。
2. 在 `.evozeus-wrapper/docs/designs/` 写 design doc，再改 Skill、route、reference 或 script。
3. PR 同步更新 `.evozeus-wrapper/CHANGELOG.md`，并跑本仓库验证门禁。
4. 合并后打 `vMAJOR.MINOR.PATCH` tag 并写 release notes。
5. wrapper harness 版本由 `.evozeus-wrapper/wrapper.json` 管理；migration 只追加，记录在 `.evozeus-wrapper/docs/migrations/`。

业务方法和工程路由由本仓库维护；EvoZeus-CoEvolve 只增加证据、评估、版本和恢复治理。

## 输出模板

```text
工程路由: Learn | Skill 自进化 | Governance
当前阶段: 8 PR/发布 / 9 维护
项目形态: Library/SDK
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

## 验证门禁

- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/lesson.py validate`
- 涉及 GitHub issue、push、release 时加 `python3 scripts/self_evolve.py doctor --json`

## 停止条件

- 只改安装副本，没改 canonical source。
- 新规则适用范围不清，却写入 Skill 级运行逻辑。
- 验证脚本失败，或版本、manifest、README、安装副本不一致。

## References（用到时再读）

- `references/self-evolution-harness.md`：进入本 Skill 就读，自进化流程和 gate。
- `references/lessons.md`：要查重、追加 L1 lesson 时。
- `references/patterns-skill.md`：要 promote 成 L2 pattern 时。
- `references/prompts-guide.md`：要用 capture / promote prompt 工作流时。
- `references/delivery-gates.md`：判断团队交付后哪些值得沉淀、记到哪里时。
- `references/output-contracts.md`：写“交付后”正式输出时。
