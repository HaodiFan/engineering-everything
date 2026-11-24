---
schema_version: 1
id: bombadil-runnable-ui-review
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.17.0
min_package_version: 0.16.0
prompt: "这个本地可运行的工作流有异步加载、重复提交、失败重试和退回验收。帮我 review；已有隔离测试账号，工具可用。"
expected_route_ids:
  - review-release
required_fields:
  - 交付结论
  - 证据
  - 未运行检查及原因
  - 剩余风险
must:
  - 先固定版本、角色、隔离数据和允许操作，识别为 Bombadil 适用。
  - 在主路径走查前读取共用执行说明，复用项目 CLI 和规格；核对实际版本与帮助。
  - 从验收项提炼业务属性及可达目标的动作，实际执行带预算与输出路径的探索；记录命令、结果和证据。
  - 只运行默认异常检查不得声称覆盖提交和验收流转；固定路径 Playwright 不冒充属性探索。
  - 先发现 P1 可阻断发布，但提前结束时必须保留未执行的检查。
must_not:
  - 不只建议以后再跑 Bombadil；工具可用且已授权隔离时要实际执行。
  - 不把无违规、退出成功或门禁机检成功等同所有状态正确。
expected_references:
  - skills/engineering-review-release/references/bombadil.md
stop_condition: "适用性、执行结果或受阻原因不清时，不得宣称状态探索完成。"
---

# bombadil-runnable-ui-review

本场景为行为评估定义；格式验证通过不代表已进行模型或真实浏览器验证。
