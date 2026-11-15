# 集成 UI/UX 界面评判与 React Doctor（0.16.0）

## Related issue

这是 owner 直接提出的需求，没有单独开 issue：把本地的 UI/UX 评审审计 Skill，以及今天用过的、评审 JS 代码的开源工具集成进 EE。

## 优化目标

EE 的评审要能覆盖两块之前做不好的内容：

- **界面体验**：交付关口里的“用起来顺吗 / 看起来对吗”，之前只有原则，没有可以逐条执行的规则。
- **React 代码质量**：之前只能人工看，没有确定性的检查工具。

## 优化方向与实现

- **UI/UX 评判做成独立子 Skill `engineering-ui-ux-audit`。**
  - 内容来自 owner 下载的 `ui-ux-audit` 技能包：69 条规则、证据边界、严重度和输出格式原样保留。
  - 参考文件以 `ui-ux-` 前缀导入 root `references/`，避免和 EE 已有的 `verification-methods.md` 等文件混淆，文内链接同步改名。
  - 新增 `ui-ux-audit` 路由和主路由表的一行。review Skill 在交付关口遇到界面改动时，交给它，并拿回结论和未验证项。
  - 同包里还有一个 `ui-ux-page-optimizer`（动手优化的版本），这次不集成。
- **React Doctor 不放进仓库，只写一份用法说明 `references/react-doctor.md`。**
  - 写明什么时候用、命令参数、隐私默认值、许可证边界、怎么解读结果，以及它能证明和不能证明什么。
  - 分发给 review、构建验证、重构和 UI 评判四个 Skill，并列入 `verification-methods.md`。
  - 默认带 `--no-telemetry --no-supply-chain`：不上传遥测，也不把依赖清单发给 Socket.dev。
  - 不运行它的 `install` / `ci install`，这两个命令会改用户的 Agent 和 CI 配置。
  - 许可证是 Modified MIT，禁止用于 AI 训练或评估，也禁止当托管服务售卖。本地运行不受影响，相关限制已写进说明。

## 验证

- 新增两个行为评估场景：
  - `ui-ux-audit-evidence-boundary`：只有截图时不能放行上线，不打分，未验证的项明确列出。
  - `react-review-uses-react-doctor`：只扫这次改动新引入的问题，保留隐私默认值，不把工具分数当结论。
- 七项门禁、全部测试，以及 `sync_references` 的依赖检查都通过。
- 本机重新链接后，Claude、Codex、Agents 三处都能找到新 Skill。

## 发布

版本 `0.16.0`（新增能力），合并后按 owner 决定发版。回滚只需 revert 这个 PR，再运行 `install.py relink`。

## 不做

- 不把 React Doctor 的代码打包进本仓库。
- 不集成 `ui-ux-page-optimizer`。
