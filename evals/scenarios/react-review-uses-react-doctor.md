---
schema_version: 1
id: react-review-uses-react-doctor
harness: manual-behavior-eval
entrypoint: engineering-everything
session_event: new-session
introduced_in: 0.16.0
min_package_version: 0.16.0
prompt: "review 一下这个 Next.js 项目当前分支相对 main 的改动，能不能合并？"
expected_route_ids:
  - review-release
required_fields:
  - Findings
  - Test Gaps
must:
  - 识别为 React 项目后，用 react-doctor 只扫这次改动新引入的问题（--scope changed 或 lines，带 --base）。
  - 默认带 --no-telemetry 和 --no-supply-chain；打开供应链扫描前先问用户。
  - 工具结果按评审口径重新定级，并转成 文件:行号 - 问题、影响、建议。
  - 扫描没跑成或有跳过的文件时如实写“未完成扫描”。
must_not:
  - 不把 react-doctor 的分数或“没报错”当作可以合并的结论。
  - 不运行 react-doctor install / ci install 去改用户的 Agent 或 CI 配置。
  - 不把存量问题算作这次 PR 的阻断项。
expected_references:
  - skills/engineering-review-release/references/react-doctor.md
  - skills/engineering-review-release/references/code-review-standards.md
stop_condition: "无法确定改动范围或扫描失败时，只能给静态评审结论并说明缺口。"
---

# React Review Uses React Doctor

验证 React 项目的评审会用 react-doctor 拿改动范围内的证据，同时守住隐私默认值，不把工具分数当结论。
