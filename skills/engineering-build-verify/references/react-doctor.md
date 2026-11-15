# React Doctor（React 代码体检工具）

[React Doctor](https://github.com/millionco/react-doctor) 是 Million 出品的开源命令行工具，对 React 代码跑确定性检查，报告六类问题：状态与 effect、性能、架构、安全、无障碍和可维护性。它支持 Next.js、Vite、Astro、TanStack、React Native 和 Expo。

在 EE 里，它是**代码评审和交付前验证的证据来源之一**，不是验收结论本身。

## 什么时候用

- 评审或交付的是 React 项目：`package.json` 依赖里有 `react`。
- 合并 PR 前，想知道这次改动**新引入**了哪些 React 问题。
- 重构 React 代码前后，想对比问题有没有变多。
- 做界面评判时，想补一份代码层面的 UI 证据：用 `design` 子命令。

不是 React 项目就不用它。

## 怎么跑

在项目根目录运行。第一次会通过 `npx` 从 npm 下载，需要联网。

```bash
# 只看这次改动新引入的问题（PR 评审首选）
npx --yes react-doctor@latest . --yes --scope changed --base origin/main \
  --no-telemetry --no-supply-chain --json --json-out <报告路径>.json

# 全量体检（接手项目、重构前打底）
npx --yes react-doctor@latest . --yes --scope full \
  --no-telemetry --no-supply-chain --json --json-out <报告路径>.json

# 只跑 UI 设计相关诊断
npx --yes react-doctor@latest design .
```

- **monorepo**：用 `--project <名字或目录>` 只扫要看的子项目。
- **只看错误**：加 `--no-warnings`。
- **想知道某条规则为什么触发**：用 `react-doctor why <位置>`。
- **运行时性能**：`react-doctor scan http://localhost:3000` 会在 Chrome 里录制一段交互的性能 trace。这一步需要用户在场操作。

## 隐私和许可

- **默认关掉两个对外发送**：
  - `--no-telemetry`：不上传崩溃报告和匿名使用数据。
  - `--no-supply-chain`：不把依赖清单发给 Socket.dev 做供应链体检。
  
  用户明确同意后，才打开供应链检查。
- **许可证**：Modified MIT。未经版权方书面许可，不得把它本身、源码或衍生作品用于训练或评估 AI 模型，也不得把它包装成付费托管服务出售。在项目里本地运行它没有问题，但不要把它的代码或输出批量喂给训练流程。
- **不安装它自带的 skill**：`react-doctor install` 和 `ci install` 会往 Agent 或 CI 里写配置。EE 只需要上面的命令，用户明确要求时才运行这两个。

## 怎么解读结果

1. **先看这次改动新增的问题**（`--scope changed` 或 `lines`）。全量里存量的问题，单独列为技术债，不算这次 PR 的阻断项。
2. **按 EE 的严重度重新定级**：工具报 `error` 不等于一定阻断。按实际影响判断：
   - 安全问题，以及会导致状态错乱、无限渲染、数据丢失的问题，判为阻断；
   - 性能和可维护性问题，按影响范围判断；
   - 风格类问题只算建议。
3. **每条转成 EE 评审的格式**：文件:行号、问题、影响、建议、要补的测试。规则名可以附在后面，正文用大白话。
4. **不刷分**：总分只作参考，不当验收结论，也不为了提分改业务上没问题的代码。
5. **修复要验证**：改完后用同样的参数再跑一次，确认问题消失、没有冒出新问题，并跑项目自己的测试。

## 能证明什么，不能证明什么

- **能**：代码里存在它规则库覆盖的已知坏模式；某次改动引入或消除了这些模式。
- **不能**：
  - 功能对不对、业务问题有没有解决；
  - 界面在真实使用中顺不顺手；
  - 规则库没覆盖的问题。
  
  这些仍要靠测试、演示和人工走查。
- **扫描失败时**：比如缺依赖、超时、被跳过的文件或项目（JSON 报告里会列出来），如实写成“未完成扫描”，不当作通过。
