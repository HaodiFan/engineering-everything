---
title: "engineering-everything 自进化驾驶舱"
---

# engineering-everything 自进化驾驶舱

这是 engineering-everything 的最小自进化驾驶舱。它用于公开当前 Skill 状态、收集使用反馈、追踪设计决策和发布记录。

## 当前状态

| 项目 | 内容 |
| --- | --- |
| Skill | [`SKILL.md`](https://github.com/HaodiFan/engineering-everything/blob/main/SKILL.md) |
| EvoZeus 项目指针 | `~/.evozeus/.projects/HaodiFan/engineering-everything` |
| Repo | `HaodiFan/engineering-everything` |
| Visibility | `public` |
| 当前 Skill 版本 | `v0.10.0` |
| Wrapper harness 版本 | `v0.2.0` |
| Wrapper manifest | `.evozeus/wrapper.json` |
| Wrapper migrations | [`docs/wrapper-migrations/`](wrapper-migrations/) |
| Changelog | [`CHANGELOG.md`](https://github.com/HaodiFan/engineering-everything/blob/main/CHANGELOG.md) |
| Design docs | [`docs/designs/`](designs/) |

## 反馈入口

如果使用中遇到 Skill 输出不满意，请提交 Skill Feedback Issue。Issue 需要包含：

- 不满意的 Skill 结果。
- 期望结果。
- 复现输入或场景。
- 证据边界。
- 影响程度。

## 进化规则

Wrapper-managed Skill 的源头发现顺序固定：

1. 读取 `.evozeus/wrapper.json`。
2. 检查 `~/.evozeus/.projects/HaodiFan/engineering-everything` 是否指向 canonical repo。
3. 验证 canonical repo 的 git origin / GitHub repo。
4. 检查 `~/.codex/skills/<skill-name>` 和 `~/.agents/skills/<skill-name>`，它们只能是 runtime pointer。
5. 只有 wrapper 状态无法确认时，才进入 GitHub user/org/public search。

每次运行 Skill 前，先检查 GitHub latest release 是否有新版本：

```bash
python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything
python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything
```

每次 Skill 更新必须先写 design doc，再开 PR。根目录 `SKILL.md` 是 repo 化后的可运行入口；`~/.evozeus/.projects/HaodiFan/engineering-everything` 和 runtime 安装路径应指向同一个 canonical repo，不保留 copied install 作为第二事实源，也不要直接修改 `.codex/skills/...` 或 `.agents/skills/...`。

EvoZeus-wrapper harness 升级时，不能重写目标 Skill 业务段落。先在 EvoZeus-wrapper repo 里生成迁移方案：

```bash
python3 scripts/evozeus_wrapper.py harness upgrade-check --target /absolute/path/to/this-skill --latest-version <wrapper-version> --json
python3 scripts/evozeus_wrapper.py harness upgrade --target /absolute/path/to/this-skill --latest-version <wrapper-version> --dry-run --json
```

迁移记录写入 `docs/wrapper-migrations/`，并记录 from/to wrapper version、planned files、`SKILL.md` append-only 处理、验证命令和回滚方案。wrapper harness version 的事实源是 `.evozeus/wrapper.json`；Skill release 仍以 GitHub release 和 `CHANGELOG.md` 为准。

Design doc 至少回答：

- 修复的 Issue 是什么。
- 优化目标是什么。
- 优化方向是什么。
- 怎么优化。
- 怎么验证。
- release 如何说明。

## Release 版本标准

使用 `vMAJOR.MINOR.PATCH`：

- `MAJOR`：不兼容的 Skill 行为或输出格式变化。
- `MINOR`：新增能力、必需证据规则或 harness 行为。
- `PATCH`：文案、示例、bug fix、校验修复或不破坏兼容性的澄清。

## 上传前检查

```bash
python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything
python3 scripts/evozeus_wrapper_preflight.py structure
python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything
python3 scripts/evozeus_wrapper_preflight.py pr --design-doc docs/designs/<design-doc>.md
python3 scripts/evozeus_wrapper_preflight.py release --tag v0.10.0 --release-notes release-notes.md
```
