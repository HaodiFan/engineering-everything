# Self-Evolution Harness（Skill 自进化门禁）

本文件定义 `engineering-everything` 自我升级的最小闭环。目标不是让 Skill 越写越大，而是让每次纠偏、升级和同步都有证据、有边界、可验证。

## 何时使用

- 用户明确说“自进化 / 升级 skill / 记住这个规律 / 以后都这样”。
- 用户纠偏后，需要判断创建 GitHub lesson issue、写入 `lessons.md`、升级到 `patterns-skill.md`，还是修改某个 reference。
- 修改了 `SKILL.md`、reference 文件、`scripts/`、`data/`、`agents/openai.yaml` 或安装路径。
- `.codex` 与 `.agents` 两份安装副本可能漂移。
- 需要把本地自进化结果更新到 GitHub 线上版本。

## 核心原则

- **先分类，再修改**：纠偏、通用规律、reference 缺陷、脚本缺陷是四种不同问题。
- **Issue first**：新 lesson 候选先进入 GitHub issue，用 `lesson` label 审阅和去重；只有确认要进入 runtime skill 时，才写入 `lessons.md` 或 `patterns-skill.md`。
- **Issue 不是 PR**：提交 lesson issue 只做 intake、查重和审阅，不改 `SKILL.md`、reference、scripts 或安装副本；任何改 runtime skill 的动作都属于 PR/commit 级变更。
- **SKILL.md 只做路由**：新知识默认进入 `references/`；重复动作进入 `scripts/`；不要把理念继续塞进主文件。
- **可验证才算进化**：每次升级必须有至少一个机器可跑 gate，或一个明确的人审 gate。
- **先找源头**：先用 GitHub repo / git remote / 安装副本三方关系确认 canonical source；不能只改 `.codex` 或 `.agents` 安装目录。
- **依赖先行**：需要 GitHub issue、线上 repo 或发布时，先检查 `git`、`gh`、`gh auth status` 和 origin remote。

## 决策矩阵

| 输入信号 | 写入位置 | 必跑验证 |
|---|---|---|
| 新 lesson 候选 | GitHub issue（label: `lesson`），不改 runtime 文件 | `gh issue view <number>` |
| issue 已确认要进入 runtime skill | `references/lessons.md` | `scripts/lesson.py validate` |
| 同主题 lesson >= 2 或用户确认是通用规律 | `references/patterns-skill.md` | `scripts/self_evolve.py check` |
| pattern 改变 reference 的核心判断 | 对应 reference 文件 | `scripts/skill_doctor.py` |
| 重复、脆弱或易错操作 | `scripts/*.py` | `python3 -m py_compile scripts/*.py` + 代表性运行 |
| 触发词、路由或安装 manifest 变化 | `SKILL.md` / `data/routes.yaml` / `agents/openai.yaml` | `scripts/skill_doctor.py --json` |
| GitHub issue / 线上 repo / 发布动作 | GitHub repo | `scripts/self_evolve.py doctor` |

## Source Discovery 顺序

1. 如果当前目录在 git repo 内，先读 `origin` remote，并用 `gh repo view` 验证可访问。
2. 如果当前目录只是安装副本（例如 `.codex/skills/...` 或 `.agents/skills/...`），先用 `gh auth status` 确认账号，再查当前用户 repo：`gh search repos "<skill-name> user:<login>"`。
3. 当前用户 repo 查不到时，再查当前用户所属 org：`gh search repos "<skill-name> org:<org>"`。
4. 用户和 org 都查不到时，最后才做公开 repo / Web 搜索。
5. 找到 repo 后，把 repo clone 视为 canonical source；安装副本只作为部署目标。

## 流程

1. **Intake**：把用户输入归类为 lesson candidate、pattern、reference、script/gate 或 install sync。
2. **Preflight**：运行 `python3 scripts/self_evolve.py doctor`，确认 `git`、`gh`、`gh auth`、GitHub origin 和 canonical source。
3. **Issue**：lesson candidate 先在 GitHub repo 里查重；无重复则创建 issue，打 `lesson` label，body 写背景、错误默认动作、正确动作、适用条件、验收标准和来源。到此为止不改 `SKILL.md`、reference、scripts 或安装副本。
4. **Scope**：只有用户确认要把 issue 进入 runtime skill，或明确要求改 skill 时，才列出 PR/commit 需要改的文件；如果要改 `SKILL.md`，先检查能否放到 reference。
5. **Patch**：只改已确认的 canonical source；不手写复制安装目录。
6. **Verify**：至少运行：
   - `python3 scripts/lesson.py validate`
   - `python3 scripts/self_evolve.py check`
   - `python3 scripts/self_evolve.py doctor`（涉及 GitHub issue / 线上 repo / 发布时）
   - `python3 scripts/skill_doctor.py --json`
   - `python3 -m py_compile scripts/*.py`
7. **Sync**：验证通过后，用 `python3 scripts/install.py --target agents` 同步 `.agents` 副本。
8. **Publish**：用户要求线上版本更新时，commit 并 push 到 GitHub；如果不是 owner 直推场景，开 draft PR。
9. **Report**：收尾说明 GitHub issue、GitHub commit/PR、变更文件、验证命令、未验证项和剩余风险。

## 停止条件

- 纠偏只适用于单个项目，却准备写入 Skill 级 `lessons.md`。
- 用户要求 lesson 进 GitHub issue，却直接改 `SKILL.md`、reference、scripts、安装副本或本地 `lessons.md`。
- 未运行 `self_evolve.py doctor`，却准备创建 issue、推送 GitHub 或声称线上已更新。
- `gh` 未安装或未登录，却继续假设可以访问用户自己的 repo。
- origin remote 不是 GitHub repo，或无法用 `gh repo view` 访问。
- 新规则与现有 reference 冲突，但没有标记 pending-review 或升级 reference。
- `SKILL.md` 超过 200 行，或新增内容无法解释为什么必须进入主文件。
- `.agents` 副本有未合并差异，且差异不是源头滞后。
- 验证脚本失败，或只能靠口头判断“应该没问题”。

## 反模式

- 把“自进化”理解成自动扩写原则，导致 Skill 越来越难触发、难阅读、难验证。
- 把创建 lesson issue 当成 PR，顺手修改 runtime skill 文件。
- 只更新 `.codex`，忘记 `.agents`，下一次不同宿主读到旧版本。
- 只记录 lesson，不检查是否已经满足 promotion 条件。
- 为了通过 doctor 放宽 gate，而不是修正真实结构问题。
