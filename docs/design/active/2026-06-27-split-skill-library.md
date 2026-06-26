# Design Doc: Engineering Everything 多 Skill 拆分 v0.1

## TLDR

把 Engineering Everything 从单个超大 Skill 拆成 plugin-style skill library：主 `engineering-everything` 只做路由和协作纪律，场景能力下沉到独立子 skill。第一阶段只迁移 `engineering-project-inheritance` 作为 pilot，并同步安装与 doctor 校验，避免一次性大爆炸。

## 背景

当前根 `SKILL.md` 已到 200 行软上限，同时 `references/architecture-cases.md`、`architecture-cases-ai.md`、`prompts-guide.md` 等 reference 很大。继续把所有场景塞进一个入口，会让 agent 每次加载过多上下文，也让路由、内容、验证、治理混在同一个文件里。

参考 `superpowers` 的方式，正确方向是一个 repo 暴露多个可独立发现的 skill，而不是一个主 skill 内部维护所有流程。

## 目标

- 主 skill 变薄：只负责判断工程路由、选择子 skill、定义输出契约。
- 子 skill 独立触发：每个场景有自己的 `name`、`description`、正文和必要 reference。
- 安装兼容：`scripts/install.py --target both` 默认安装所有 `skills/*` 子 skill。
- 验证可重复：`scripts/skill_doctor.py` 同时检查根兼容入口、plugin manifest、子 skill frontmatter、路由 seed 和 reference 链接。
- 行为保持：`$engineering-everything` 仍然可用，只是变成薄路由器。

## 非目标

- 不在本阶段迁移所有 reference。
- 不在本阶段重写架构、自动化、组织和发布全部场景。
- 不改变 lesson/pattern/self-evolution 的业务规则。
- 不引入 Python 包管理、测试框架或新依赖。

## 目标结构

```text
engineering-everything/
├── .codex-plugin/plugin.json
├── SKILL.md                         # 兼容入口，内容与主路由保持一致
├── skills/
│   ├── engineering-everything/
│   │   └── SKILL.md                 # 主路由 skill
│   └── engineering-project-inheritance/
│       ├── SKILL.md                 # pilot 子 skill
│       └── references/
│           └── inheriting-projects.md
├── references/                      # 旧 reference 库，后续逐步迁移
├── scripts/
└── schemas/
```

## 子 Skill 拆分候选

| 子 skill | 状态 | 内容来源 |
|---|---|---|
| `engineering-project-inheritance` | Phase 1 pilot | `references/inheriting-projects.md` |
| `engineering-product-definition` | 待迁移 | `psps-framework.md`、`spec-templates.md`、Stage 0-2 |
| `engineering-architecture-design` | 待迁移 | `architecture-cases*.md`、`project-blueprints.md` |
| `engineering-execution-planning` | 待迁移 | `execution-pipeline.md`、review roles |
| `engineering-build-verify` | 待迁移 | Stage 6、validation commands、agent standards |
| `engineering-refactoring` | 待迁移 | `refactoring-rules.md` |
| `engineering-review-release` | 待迁移 | `code-review-standards.md`、PR readiness |
| `engineering-automation-playbooks` | 待迁移 | `scenario-playbooks.md` |
| `engineering-organization-systems` | 待迁移 | `engineering-scenarios.md` |
| `engineering-skill-evolution` | 待迁移 | `lessons.md`、`patterns-skill.md`、self-evolution harness |

## Phase 1 方案

1. 新增 plugin manifest，声明 `skills: ./skills/`。
2. 新增薄主路由 skill：`skills/engineering-everything/SKILL.md`。
3. 将根 `SKILL.md` 收缩为同一薄路由，保留旧安装兼容。
4. 新增 pilot 子 skill：`skills/engineering-project-inheritance/SKILL.md`。
5. 复制 `references/inheriting-projects.md` 到 pilot 子 skill 内，使其可独立安装。
6. 更新 `install.py`：默认安装 `skills/*` 到本地 skill 根目录；提供 `--layout legacy` 保留旧整包安装。
7. 更新 `skill_doctor.py`：检查 plugin manifest、子 skill frontmatter、重复 skill 名、重复 aliases、skill reference 链接和 README 说明。

## 验证门禁

- `python3 scripts/skill_doctor.py --json`
- `python3 scripts/self_evolve.py check --json`
- `python3 scripts/self_evolve.py doctor --json`
- `python3 scripts/lesson.py validate`
- `python3 scripts/install.py --target both --dry-run`
- `python3 scripts/install.py --target both --layout legacy --dry-run`

## 风险与处理

| 风险 | 处理 |
|---|---|
| 子 skill 装到本地后找不到根 `references/` | pilot 子 skill 自带必要 reference；后续迁移也遵循自包含原则 |
| 根 `SKILL.md` 与 `skills/engineering-everything/SKILL.md` 漂移 | doctor 检查两者版本和主入口存在；后续可加强文本同步 |
| 一次迁移太多导致行为变化不可控 | Phase 1 只迁移 `inherit` 路由 |
| 旧用户依赖整包安装 | `install.py --layout legacy` 保留旧整包安装 |

## 后续迁移顺序

1. `engineering-refactoring`：边界小，验证逻辑清楚。
2. `engineering-review-release`：可复用度高，内容短。
3. `engineering-product-definition`：承接 PSPS 和 spec。
4. `engineering-execution-planning` / `engineering-build-verify`：拆执行与实现。
5. `engineering-architecture-design` / `engineering-automation-playbooks`：最后迁移最大 reference。
