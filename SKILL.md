---
name: engineering-everything
description: Use when a task needs engineering-route judgment before choosing product definition, project inheritance, architecture, execution, build, refactor, review, release, organization, automation, or skill-evolution work.
metadata:
  version: 0.11.0
---

## EvoZeus-wrapper 状态检查

执行本 Skill 主链路前，先完成状态检查；只有检查结果为 OK，才继续进入下方原 Skill 流程。

1. Skill release 状态
   - 当前记录版本：`v0.11.0`
   - 检查命令：`python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything`
   - 如果 GitHub latest release 更新：先更新 canonical repo，并确认 runtime install 仍指向 canonical repo。
   - 如果本地版本领先 GitHub release：先完成 changelog、验证和 `vMAJOR.MINOR.PATCH` release，再把它当作稳定运行版本。
2. Wrapper harness 状态
   - 当前 wrapper 版本：`v0.3.0`
   - 事实源：`.evozeus/wrapper.json`
   - 检查命令：在 EvoZeus-wrapper repo 运行 `python3 scripts/evozeus_wrapper.py harness upgrade-check --target <this-skill-repo> --latest-version <wrapper-version> --json`
   - 如果 wrapper 落后：先运行 `harness upgrade --dry-run` 生成迁移方案，再按状态检查前置、其他 wrapper 内容 append-only 的规则迁移。
3. Source contract 状态
   - 检查命令：`python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`
   - 如果 `.evozeus/.projects`、git origin 或 runtime install 不一致：先修复为同一个 canonical repo，再继续。

解决顺序：先修 source contract，再修 wrapper harness，最后处理 Skill release。全部 OK 后，再进入主链路。

# Engineering Everything / 工程化万物

Engineering Everything 是主路由 Skill。它不承载所有场景细节，只负责先判断任务属于哪条工程路径，再加载对应子 skill 或 reference。

## 使用原则

先判断，再行动。不要在路由未明时直接写代码、重构、补架构或编造业务需求。

用户不满意是全局捕获信号，不是 Learn 主路由。只要用户在使用 Engineering Everything 时表达否定、纠偏或不满意（如“不对”“不是”“这部分好乱”“你没有参考”“方案不行”），agent 必须先承认具体偏差，并主动询问是否要把这次纠偏创建为 GitHub lesson issue；用户确认后再按 issue-first 流程处理，不能默认直接写 `lessons.md`。当前任务仍按原本命中的工程路由继续，不因为用户不满意就把主任务改路由到 `engineering-skill-evolution`。

规划类回答使用统一模板：

```text
工程路由: <主路由 | 命中场景 | 决策层>
当前阶段: <P POC/Spike | 0 想法 | 1 需求澄清 | 2 Spec | 3 架构 | 4 脚手架 | 5 Feature 规划 | 6 实现 | 7 验证 | 8 PR/发布 | 9 维护 | I 接手盘点>
项目形态: <Web+Backend | Desktop+Local Agent | Python Agent/CLI | Library/SDK | Full-stack Monorepo | Non-software Project | Organization System | Unknown>
参考依据:
- 路由规则: <命中的 SKILL.md 子 Skill 路由或不可突破规则>
- 已读 reference: <path -> 具体用于哪个判断>
- 外部/历史依据: <如使用 web / memory / repo 文件，说明来源和用途；未使用则写未使用>
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

规划类回答不能只说“用了 Engineering Everything”。必须把关键判断和已读取的 reference 对上，至少覆盖路由、阶段、项目形态、验证门禁这 4 类判断；未读取的候选 reference 不要伪装成依据。

执行类回答收尾必须包含：变更文件 / 已运行验证 / 未运行检查及原因 / 剩余风险。

## 子 Skill 路由

先按优先级判断，再选择目标路线：

`接手项目 > 安全/合规 > 用户明确执行 > 用户明确重构 > 业务场景 > 项目形态 Unknown > 组织/非软件 > 显式 learn/evolution`

### 已拆出的场景子 Skill

- `engineering-project-inheritance`：接手、老项目、现有 repo、继续迭代。
- `engineering-product-definition`：需求、PRD、产品定义、PSPS、想法澄清。
- `engineering-architecture-design`：技术栈、架构、选型、脚手架、agent app。
- `engineering-execution-planning`：feature 拆解、implementation plan、worktree、review roles。
- `engineering-build-verify`：实现、修 bug、迁移、接接口、验证命令。
- `engineering-refactoring`：重构、清理、模块化、技术债。
- `engineering-review-release`：review、PR、merge、release、发布。
- `engineering-automation-playbooks`：RPA、OCR、CV、LLM、浏览器自动化、数据分析。
- `engineering-organization-systems`：面试、入职、组织、企业、SOP、非工程项目估算、非软件产物。
- `engineering-skill-evolution`：用户明确要求记录 lesson、创建 lesson issue、沉淀 pattern、自进化或升级 skill。

## 不可突破的规则

- 业务需求必须来自用户或 owner；agent 只负责结构化、校验和追问。
- 没有 spec，不新增架构层、状态机、存储、权限、全局依赖或公共 API。
- 接手项目默认尊重现状，不擅自重构。
- 重构必须行为保持，有验证门禁，不混 feature / bug fix / format / dependency upgrade。
- 改 Skill 结构、版本、引用或安装路径后必须跑 `scripts/self_evolve.py check` 与 `scripts/skill_doctor.py`；涉及线上 repo 或发布时加跑 `scripts/self_evolve.py doctor`。

## References

- `docs/design/active/2026-06-27-split-skill-library.md`：多 Skill 拆分设计。
- `data/routes.yaml`：机器可读路由 seed。
- `references/engineering-scenario-map.md`：legacy/source 路由地图；运行时 route seed 已指向子 skill。
- `references/lessons.md`：Skill 级 L1 纠偏日志。
- `references/patterns-skill.md`：Skill 级 L2 可复用模式。
- `references/self-evolution-harness.md`：Skill 自进化门禁。

## 自进化方法

本 Skill 已由 EvoZeus-wrapper 接入自进化闭环。后续任何行为改动都必须先留下可追踪证据，再进入实现。

源头发现顺序：

1. 先读取本 repo 的 `.evozeus/wrapper.json`，以 `canonical_repo` 作为目标 repo。
2. 再检查 `~/.evozeus/.projects/HaodiFan/engineering-everything` 是否存在并指向 canonical repo。
3. 验证 canonical repo 的 git origin / GitHub repo 可访问。
4. 再检查 runtime install：`~/.codex/skills/<skill-name>`、`~/.agents/skills/<skill-name>`；它们只能是指向 canonical repo 的安装指针。
5. 只有 wrapper manifest 和 project pointer 都无法确认时，才进入 GitHub user/org/public search。

进化流程：

1. 使用中出现不满意结果时，先提交 Skill Feedback Issue，写清不满意结果、期望结果、复现场景、证据边界和影响程度。
2. 每次运行本 Skill 前，先执行 `python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`，确认 wrapper source contract 成立。
3. 再执行 `python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything`，确认 GitHub latest release 没有新版本。
4. 开始修改前，在 `docs/designs/` 新建设计文档，明确 Related issue、优化目标、实现计划、验证计划和 release plan。
5. PR 必须同步更新 `SKILL.md` 与 `CHANGELOG.md`，并通过 `python3 scripts/evozeus_wrapper_preflight.py structure` 和 PR 检查。
6. 合并后用 `vMAJOR.MINOR.PATCH` release tag 和 release notes 固化本次进化，保留可回滚记录。

边界：不要把 raw private session、客户资料、secret、未脱敏商业上下文写入公开 Issue、docs 或 release notes；`~/.evozeus/.projects/HaodiFan/engineering-everything/` 应指向 canonical repo，runtime install 不能作为 copied install 或第二事实源直接修改。

Target repo: `HaodiFan/engineering-everything`
Visibility: `public`
Current Skill version: `v0.11.0`
Wrapper harness version: `v0.3.0`

## EvoZeus-wrapper

本区由 EvoZeus-wrapper 追加，用来说明本 Skill 的 wrapper harness 路由、版本记录和迁移规则。它不覆盖原 Skill 的业务规则；涉及业务行为变化时，仍必须走 Issue、design doc、PR、CHANGELOG 和 release。

调用 wrapper 的场景：

1. 本 Skill 需要 repo 化、adopt/repair wrapper harness、或确认 canonical source。
2. `.evozeus/wrapper.json` 中的 wrapper harness version 落后于 EvoZeus-wrapper 最新版本。
3. `~/.evozeus/.projects/HaodiFan/engineering-everything`、`.codex` 或 `.agents` runtime install 疑似不是同一个 source of truth。
4. 使用反馈需要从 Skill Feedback Issue 进入 design doc、PR、CHANGELOG、release 的自进化闭环。
5. 目标 GitHub repo、release tag、GitHub Pages 或 preflight check 需要创建、诊断或修复。

路由规则：

- 目标 Skill 行为问题：先提交 Skill Feedback Issue，不直接改 runtime install。
- 源头/安装问题：先运行 `python3 scripts/evozeus_wrapper_preflight.py doctor --repo HaodiFan/engineering-everything`。
- 结构问题：运行 `python3 scripts/evozeus_wrapper_preflight.py structure`。
- Skill release 问题：运行 `python3 scripts/evozeus_wrapper_preflight.py version --repo HaodiFan/engineering-everything`。
- wrapper harness 升级：回到 EvoZeus-wrapper repo，运行 `python3 scripts/evozeus_wrapper.py harness upgrade-check --target <this-skill-repo> --latest-version <wrapper-version> --json`，再用 `harness upgrade --dry-run` 生成迁移方案。

Append-only 迁移规则：

- wrapper 升级必须保留 frontmatter 后的状态检查；其他 `SKILL.md` wrapper 内容只能追加本区缺失内容或 migration note，不要重写原 Skill 业务段落。
- 如果本区已存在，升级时追加 migration note，不改写旧文本。
- 每次 wrapper 升级必须记录 from/to wrapper version、planned files、验证命令、回滚方案和是否需要人工 merge review。
- wrapper version 事实源是 `.evozeus/wrapper.json` 的 `wrapper_version`；Skill release 仍以 GitHub release / `CHANGELOG.md` 为准。

Wrapper harness version: `v0.3.0`
Wrapper manifest: `.evozeus/wrapper.json`
Wrapper migration log: `docs/wrapper-migrations/`

### Wrapper migration note - 2026-06-27

- From wrapper version: `v0.2.0`
- To wrapper version: `v0.3.0`
- `SKILL.md` handling: added `EvoZeus-wrapper 状态检查` immediately after frontmatter, refreshed wrapper-owned version records, and kept Engineering Everything business routing rules unchanged.
- Migration record: `docs/wrapper-migrations/2026-06-27-v0.2.0-to-v0.3.0.md`
