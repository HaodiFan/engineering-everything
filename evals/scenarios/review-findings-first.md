---
schema_version: 1
id: review-findings-first
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.12.0
min_package_version: 0.12.0
prompt: "review 一下这个 PR，判断能不能 merge。"
expected_route_ids:
  - review-release
required_fields:
  - Findings
  - Open Questions
  - Test Gaps
  - Change Summary
must:
  - 先列 findings，并按严重度排序。
  - 每个问题要有 file:line 或说明无法定位。
must_not:
  - 不先写泛泛总结。
expected_references:
  - skills/engineering-review-release/references/code-review-standards.md
---

# Review Findings First

验证 review 输出契约保持问题优先。
