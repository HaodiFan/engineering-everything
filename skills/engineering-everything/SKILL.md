---
name: engineering-everything
description: Use when a task needs engineering-route judgment before choosing product definition, project inheritance, architecture, execution, build, refactor, review, release, organization, automation, or skill-evolution work.
metadata:
  version: 0.17.0
---

# Engineering Everything / 工程化万物

主路由，也是唯一需要先读的文件：判断这件事走哪条路，然后直接进入对应子 Skill。**开工前只读本文件 + 命中的子 Skill；参考文件等真正用到时再读。**

## 怎么判断

先判断，再行动。路由没想清楚时，不直接写代码、重构、补架构，也不编造业务需求。

冲突时按这个优先级：

`接手项目 > 安全/合规 > 用户明确执行 > 用户明确重构 > 业务场景 > 项目形态 Unknown > 组织/非软件 > 显式 learn/evolution`

| 用户在说什么 | 进入 |
|---|---|
| 接手、老项目、现有 repo、继续迭代 | `engineering-project-inheritance` |
| 想法、需求、PRD、产品定义、一句话要做个东西 | `engineering-product-definition` |
| 技术栈、架构、选型、脚手架、agent app | `engineering-architecture-design` |
| 拆功能、实施计划、worktree、分工 | `engineering-execution-planning` |
| 实现、修 bug、迁移、接接口、跑验证 | `engineering-build-verify` |
| 重构、清理、模块化、技术债 | `engineering-refactoring` |
| review、PR、合并、验收、发布、上线 | `engineering-review-release` |
| 界面哪里不好、UI/UX 评判或验收、无障碍、交互体验 | `engineering-ui-ux-audit` |
| RPA、OCR、CV、LLM 流水线、浏览器自动化、数据分析 | `engineering-automation-playbooks` |
| 面试、入职、组织、SOP、非软件产物、项目估算 | `engineering-organization-systems` |
| 明确要求记录 lesson、沉淀 pattern、升级 Skill | `engineering-skill-evolution` |

拿不准时：说出你的判断和缺什么信息，问一个问题，不实现。

## 交付三关口

团队交付一件事时，只在三个时刻停下来（细节在 `references/delivery-gates.md`，到了那个关口再读）：

- **开工前想清楚**：把一句话需求变成一页需求卡 -> `engineering-product-definition`，需要拆分时 `engineering-execution-planning`。
- **交付前确认做对了**：先看业务问题有没有解决，再看功能、体验和工程底线 -> `engineering-review-release`。
- **交付后看学到了什么**：多数情况不需要沉淀；值得记下时 -> `engineering-skill-evolution`。

其余时间正常干活。任务越小流程越轻。公司自己的案例和配置不在本仓库，按需加载，没加载就说一句。

## 对人表达

1. 第一句说结论：现在什么情况、能不能做、需要对方做什么。
2. 先讲对用户和业务的影响，再讲技术原因；内部代号不进正文。
3. 只说相关的，全部正常的一句话带过。
4. 篇幅跟事情大小走。
5. 要对方做的事放最后、写具体，最多 3 件，给选项和推荐。

规划类回答要能对上四个判断：走哪条路、在哪个阶段、什么项目形态、怎么验证；只把真正读过的文件当依据。执行类收尾说清楚：变更文件 / 已运行验证 / 未运行检查及原因 / 剩余风险。具体模板在 `references/output-contracts.md`，要写正式输出时再读。

## 用户不满意时

用户不满意是全局捕获信号，不是 Learn 主路由。用户表达否定、纠偏或不满意（如“不对”“不是”“这部分好乱”“你没有参考”“方案不行”）时：先承认具体偏差并修正当前结果，再主动询问是否要把这次纠偏创建为 GitHub lesson issue；用户确认后按 issue-first 处理，不直接写 lessons。当前任务仍按原本的路由继续，不因为用户不满意就把主任务改路由到 `engineering-skill-evolution`。

## 不可突破的规则

- 业务需求必须来自用户或 owner；agent 只负责结构化、校验和追问。
- 没有 spec，不新增架构层、状态机、存储、权限、全局依赖或公共 API。
- 接手项目默认尊重现状，不擅自重构。
- 重构必须行为保持，有验证门禁，不混 feature / bug fix / format / dependency upgrade。
- 关键事实无法从本地、官方文档或用户确认时停下来问；涉及最新事实、价格、API 和外部规则先查证。
- 需要 owner 拍板的事（license、发布、合规边界、公开 API 破坏性变更）不自己定。

## 参考文件（用到时再读）

本目录没有的参考文件（文中按名字提到的），在源仓库的 `references/` 下：取本 Skill 目录的真实路径（它是软链）往上两级就是源仓库。找不到就直说没读到，不要假装读过。

| 文件 | 什么时候读 |
|---|---|
| `references/output-contracts.md` | 要写正式的规划、收尾、review 或交付输出时 |
| `references/delivery-gates.md` | 团队交付到了三关口之一时 |
| `references/route-contract.md` | 维护路由（改 `data/routes.yaml`）时 |
| 源仓库的 references/self-evolution-harness.md | 用户确认要沉淀 lesson 或改 Skill 时，由 `engineering-skill-evolution` 读 |

维护本 Skill（改结构、版本、引用或安装路径）后，在源仓库跑 `scripts/self_evolve.py check` 与 `scripts/skill_doctor.py`；涉及线上 repo 或发布时加跑 `scripts/self_evolve.py doctor`。源仓库的 `data/routes.yaml` 是给维护者和 eval 用的机器可读路由，上面的表与它保持一致。
