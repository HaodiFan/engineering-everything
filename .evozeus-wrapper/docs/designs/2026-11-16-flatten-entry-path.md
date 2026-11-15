# 入口扁平化（0.15.0）

## 问题与优化目标

优化目标：让 Agent 从入口到开始干活只读主路由 + 一个子 Skill，参考文件按需读取，并去掉没人用的重复副本。

现状：
Owner 反馈“SkillOS 嵌套很深”。目录只有 3 层，深的是运行时调用链。一个普通任务开工前大约要读 10 个文件，跨 4 跳：

1. harness 启动块要求读 `.evozeus-wrapper/...`。从已安装的 skill 目录按相对路径找不到这个文件。
2. 启动器再要求预读 `route-contract.md`、`output-contracts.md`、`codex-tools.md`。
3. 主路由再引用 `data/routes.yaml`，但运行时读不到它。
4. 子 Skill 列出 5–7 个参考文件，都没写什么时候读。

另外，`lessons.md`、`patterns-skill.md`、`prompts-guide.md` 被复制进 10–11 个子 Skill，约 1 万行重复内容。原因是共享参考文件里写了它们的路径。

## 优化方向与实现

- **启动器变薄。** 只管要不要进入、会话怎么接上，然后交给主路由。启动器不再自带参考文件。harness 启动块原样保留（归 harness 管），块外加一句说明：路径相对源仓库根目录。
- **主路由是开工前唯一要读的文件。** 路由表、不可突破的规则、5 条对人表达规则都写在正文里。输出模板和交付关口细节等用到时再读。
  - 路由表必须和 `data/routes.yaml` 一致，由 `skill_doctor` 检查。
  - 事实源仍然只有 `data/routes.yaml`。
- **子 Skill 的每个参考文件都写明“什么时候读”。**
- **只把副本放在真正需要的地方：**

| 文件 | 处理 |
|---|---|
| `lessons.md`、`patterns-skill.md` | 只留在 `engineering-skill-evolution` |
| `prompts-guide.md` | 只留在会初始化项目的 Skill |
| `codex-tools.md` | 只留根目录，要点并入主路由 |
| `route-contract.md` | 跟主路由走 |

  共享参考文件改为按名字提 lessons，捕获 lesson 统一走 issue-first。
- **EvoZeus-CoEvolve 发布闭环治理挪到 `engineering-skill-evolution`。** 只有在那里才用得到。

## 验证

- `skill_doctor.py` 新增入口深度检查，配有 `tests/test_entry_depth.py`。检查三件事：
  - 入口文件不预读参考文件；
  - 列出的参考文件都写了读取条件；
  - 路由表与 routes 一致。
- 七项门禁全部通过。
- 行为 eval：`route-before-building`、`session-resume`、`task-switch-reroute`、`no-validation-no-refactor`、`intent-gate-team-task`，对比改动前后。

## 发布

合并后版本为 `0.15.0`，CHANGELOG 已记录；按 owner 决定打 tag 发布。已安装的 skill 是软链，合并即生效；回滚只需 revert 本 PR。

## 不做

- 不改 harness 启动块本身。正确修法是让 EvoZeus 生成的启动块使用 skill 目录内可解析的路径，或给出解析规则，应在 EvoZeus 侧提 issue。
- 不合并子 Skill。按场景拆分的方式保留，只缩短到达路径。
