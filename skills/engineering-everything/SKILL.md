---
name: engineering-everything
description: Use when a task needs engineering-route judgment before choosing product definition, project inheritance, architecture, execution, build, refactor, review, release, organization, automation, or skill-evolution work.
metadata:
  version: 0.9.6
---

# Engineering Everything / 工程化万物

Engineering Everything 是主路由 Skill。它不承载所有场景细节，只负责先判断任务属于哪条工程路径，再加载对应子 skill 或 reference。

## 使用原则

先判断，再行动。不要在路由未明时直接写代码、重构、补架构或编造业务需求。

规划类回答使用统一模板：

```text
工程路由: <主路由 | 命中场景 | 决策层>
当前阶段: <P POC/Spike | 0 想法 | 1 需求澄清 | 2 Spec | 3 架构 | 4 脚手架 | 5 Feature 规划 | 6 实现 | 7 验证 | 8 PR/发布 | 9 维护 | I 接手盘点>
项目形态: <Web+Backend | Desktop+Local Agent | Python Agent/CLI | Library/SDK | Full-stack Monorepo | Non-software Project | Organization System | Unknown>
缺失内容:
下一步 3 个动作:
要创建/更新的文件:
验证门禁:
停止条件:
```

执行类回答收尾必须包含：变更文件 / 已运行验证 / 未运行检查及原因 / 剩余风险。

## 子 Skill 路由

| 命中信号 | 优先使用 |
|---|---|
| 接手、老项目、现有 repo、项目很乱、继续迭代 | `engineering-project-inheritance` |
| 需求、PRD、产品定义、PSPS、想法澄清 | `engineering-product-definition`（待迁移） |
| 技术栈、架构、选型、脚手架、agent app | `engineering-architecture-design`（待迁移） |
| feature 拆解、implementation plan、worktree、review roles | `engineering-execution-planning`（待迁移） |
| 实现、修 bug、迁移、接接口、验证命令 | `engineering-build-verify`（待迁移） |
| 重构、清理、模块化、技术债 | `engineering-refactoring`（待迁移） |
| review、PR、merge、release、发布 | `engineering-review-release`（待迁移） |
| RPA、OCR、CV、LLM、浏览器自动化、数据分析 | `engineering-automation-playbooks`（待迁移） |
| 面试、入职、组织、企业、SOP、非工程项目估算 | `engineering-organization-systems`（待迁移） |
| lesson、pattern、自进化、升级 skill | `engineering-skill-evolution`（待迁移） |

多条命中时优先级：接手项目 > 安全/合规 > 用户明确执行 > 用户明确重构 > 业务场景 > 项目形态 Unknown > 组织/非软件 > learn。

## 不可突破的规则

- 业务需求必须来自用户或 owner；agent 只负责结构化、校验和追问。
- 没有 spec，不新增架构层、状态机、存储、权限、全局依赖或公共 API。
- 接手项目默认尊重现状，不擅自重构。
- 重构必须行为保持，有验证门禁，不混 feature / bug fix / format / dependency upgrade。
- 改 Skill 结构、版本、引用或安装路径后必须跑 `scripts/self_evolve.py check` 与 `scripts/skill_doctor.py`；涉及线上 repo 或发布时加跑 `scripts/self_evolve.py doctor`。

## References

- 源仓库的 `data/routes.yaml` 是机器可读路由 seed。
- 源仓库的旧版 route map 在迁移完成前仍可用于校准主路由。
