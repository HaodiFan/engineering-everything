# App for Agent 设计范式

用于从 0 设计“给 agent 操作的 app”，或给现有 app 补齐 agent operation surface。适用于 AI-native workbench、Desktop + Local Agent、后台管理 app、local-first studio、CLI-first app、MCP/工具协议承载层。

核心判断：**app for agent 不是普通 app 后补一个 CLI，而是 Day 1 就把稳定能力暴露成 Human Surface / Agent Surface / Governance Surface 三条同步操作面。**

## 1. 适用条件

命中以下任一信号时读取本文件：

- 用户说“app for agent”“给 agent 操作的 app”“agent 可操作”“agent-native app”。
- 新 app 需要 Day 1 有 CLI / MCP / tool wrapper / automation surface。
- 桌面或本地应用需要托管外部 agent、CLI、runtime、后台任务。
- 后台管理系统需要同时支持人类 UI 操作和 agent 自动操作。
- 用户希望 Codex/agent 能稳定使用这个 app，而不是靠临时脚本和页面点击。

不适用：

- 纯营销站、内容站、一次性 landing page。
- 单纯内部脚本，无产品状态、权限、审计或长期演进需求。
- 只需要人类 GUI，不需要 agent 发现、调用、写入或执行任务。

## 2. 三层 Surface

| Surface | 作用 | Day 1 必须有 |
|---|---|---|
| Human Surface | 人类操作、审阅、批准、恢复 | GUI/TUI、可见状态、错误、审批/草稿入口 |
| Agent Surface | agent 发现能力、调用能力、订阅变化、启动任务 | manifest、protocol、CLI、JSON envelope、NDJSON stream |
| Governance Surface | 防止匿名越权和不可审计写入 | actor、permission、audit log、approval、tests、rollback |

判定标准：一个能力不能只存在于 GUI 或只存在于 CLI。稳定能力必须能在 manifest、CLI、GUI、docs、tests 中找到同一套语义。

## 3. Day 1 最小架构

```text
apps/
  desktop-or-web/
packages/
  <app>-protocol/
  <app>-cli/
  <app>-sdk/                 optional
backend/
  capability-registry/
  policy/
  audit/
docs/
  engineering/specs/
skills/
  <app>-cli/references/
```

### 3.1 Protocol Package

先建 `packages/<app>-protocol`，再让 CLI / GUI / SDK 使用它。

必须包含：

- protocol constants
- default backend URL
- request envelope builders
- response envelope types
- manifest types
- NDJSON stream decoder
- shared error shape

最小形态：

```ts
export const APP_EXT_PROTOCOL = 'app-ext';
export const APP_EXT_PROTOCOL_VERSION = 'v1';
export const DEFAULT_APP_BACKEND_URL = 'http://127.0.0.1:18616';

export function createExtCallEnvelope(operation, input = {}, context = {}) {
  return {
    protocol: APP_EXT_PROTOCOL,
    version: APP_EXT_PROTOCOL_VERSION,
    operation,
    input,
    context,
  };
}
```

### 3.2 Backend Capability Registry

`describe` 的真相源不是 README，也不是 CLI help，而是 backend capability registry。

每个 operation 至少包含：

- `name`
- `domain`
- `summary`
- `inputSchema`
- `outputSchema`
- `requiredContext`
- `requiredPermissions`
- `writeMode`
- `riskLevel`
- `examples`

命名规则：

```text
<domain>.<verb>
```

推荐：

- `projects.list`
- `projects.get`
- `projects.updateDraft`
- `tasks.create`
- `tasks.updateStatus`
- `memory.search`
- `deploy.preflight`
- `deploy.run`

避免：

- `postgres.queryProjects`
- `reactPageSave`
- `buttonClickDeploy`

### 3.3 Thin CLI

CLI 是 transport，不是产品模型。业务逻辑放在 backend operation layer，CLI 只做参数解析、envelope、HTTP/NDJSON 转发、输出格式。

Day 1 必须有：

```bash
app health
app ext describe
app ext call <operation> [--input-json '{...}'] [--context-json '{...}']
app ext stream <subscription> [--input-json '{...}'] [--context-json '{...}']
app exec profiles
app exec run <executor-ref> [--command "..."] [--args-json '[]'] [--attach]
app exec attach <execution-session-id>
app exec inspect <execution-session-id>
app exec stop <execution-session-id>
```

`ext call` 是 Day 1 逃生口；语义化命令可以后加：

```bash
app ext call projects.list --input-json '{"limit":20}'
app projects list --limit 20
```

后者只是前者的 ergonomic alias，不应变成另一套业务模型。

### 3.4 Human Review Surface

agent 能写入，就必须有人类可见的审阅面：

- pending drafts
- approval requests
- audit log
- failed operations
- permission denials
- generated plans
- rollback candidates

最小命令：

```bash
app audit list
app approvals list
app approvals respond --input-json '{"approvalId":"...","decision":"approved"}'
```

## 4. 协议规则

### 4.1 Describe First

agent 第一次操作前先读取：

```bash
app ext describe
```

manifest 必须告诉 agent：

- 有哪些 operation / stream
- 每个 operation 的 input/output schema
- 需要哪个 actor context
- 需要什么 permission
- 是 read-only、draft-writing、direct-writing 还是 high-risk
- 示例调用方式

### 4.2 JSON-only Boundary

边界统一用结构化数据：

- `--input-json`
- `--context-json`
- JSON response envelope
- NDJSON stream
- structured error object

不要把自然语言 stdout 当主协议。

### 4.3 Actor Mandatory

非公开 discovery operation 不允许匿名修改状态。

request:

```json
{
  "protocol": "app-ext",
  "version": "v1",
  "operation": "projects.updateDraft",
  "context": {
    "workspaceId": "workspace-dev",
    "actorId": "agent-codex"
  },
  "input": {
    "projectId": "p1",
    "patch": {}
  }
}
```

response:

```json
{
  "ok": true,
  "operation": "projects.updateDraft",
  "actor": {
    "type": "agent",
    "actorId": "agent-codex"
  },
  "data": {}
}
```

### 4.4 Draft Before Direct Write

高影响写入默认走 draft / approval-required。

direct write 只在以下条件都满足时允许：

- permission 明确允许
- operation risk level 允许
- input schema 通过
- affected state 可审计
- 有 rollback / repair path

## 5. Ext / Exec 分层

不要把资源操作和进程执行混在一起。

| Surface | 负责 | 不负责 |
|---|---|---|
| `ext` | 产品资源、业务状态、manifest、call、stream | 启停受管进程 |
| `exec` | managed execution lifecycle、attach、stop、inspect | 业务资源读写 |

最小 execution session：

| Field | Meaning |
|---|---|
| `executionSessionId` | stable id |
| `executorRef` | selected executor |
| `actorId` | who requested it |
| `state` | `starting/running/waiting_input/stopping/stopped/failed` |
| `bridgeMode` | `stdio/pty/sdk/structured_cli/none` |
| `cwd` | working directory |
| `startedAt` / `stoppedAt` | lifecycle timestamps |
| `exitCode` | process result |

## 6. Capability Completion Matrix

一个能力不因为有 backend route 就算完成。

| Layer | 完成要求 |
|---|---|
| Backend | operation 存在并校验 input |
| Manifest | `ext describe` 暴露 schema / permission / examples |
| CLI | generic call 可用；关键操作有语义化 alias |
| GUI | 人能看到状态、错误、恢复路径 |
| Policy | actor 和 permission 被执行 |
| Audit | 写入尝试被记录 |
| Tests | mock-server CLI test + backend policy test |
| Docs | human workflow + agent workflow |

状态命名：

- `not-started`
- `backend-only`
- `agent-readable`
- `agent-draft-write`
- `agent-direct-write`
- `dual-track-complete`

## 7. Permission Baseline

从粗粒度 domain permission 起步，但高风险动作必须拆开。

| Permission | Meaning |
|---|---|
| `<domain>.read` | list/get/search |
| `<domain>.writeDraft` | create or update draft only |
| `<domain>.write` | direct write |
| `<domain>.delete` | destructive action |
| `<domain>.approve` | approve pending operation |
| `exec.run` | start managed execution |
| `exec.attach` | attach to execution stream |
| `exec.stop` | stop execution |
| `deploy.plan` | produce deployment plan |
| `deploy.run` | execute deployment |
| `settings.write` | update app-level settings |
| `secrets.writeRef` | save secret reference, never echo raw secret |

高风险权限不能被 generic write 隐含：

- delete
- install / uninstall
- deploy
- provider / settings write
- secret update
- external publishing
- irreversible migration

## 8. Agent Manual Contract

Day 1 写 agent-readable command reference。

推荐路径：

```text
skills/<app>-cli/references/cli-commands.md
```

最小章节：

1. Base URL and transport
2. Top-level commands
3. Command-to-backend mapping
4. Recommended operator flows
5. Selection rules
6. Known unsupported operations

这不是营销文档，是 agent 和维护者的操作契约。

## 9. Test Gate

### 9.1 CLI Unit Tests

覆盖：

- argument parsing
- JSON flag parsing
- backend URL resolution
- no secret echo
- help output does not crash

### 9.2 CLI Integration Tests

用 mock server，不依赖真实 backend。断言：

- method
- path
- request body
- response printing
- NDJSON stream handling
- non-2xx error behavior

### 9.3 Backend Policy Tests

覆盖：

- missing actor
- invalid actor
- missing permission
- approval-required path
- schema invalid
- audit record written

### 9.4 E2E Smoke

至少保留：

```bash
pnpm app ext describe
pnpm app ext call health.read
pnpm app exec profiles
```

## 10. Day 1 Checklist

- [ ] `packages/<app>-protocol` exists.
- [ ] `packages/<app>-cli` exists.
- [ ] Root `package.json` exposes `pnpm app`.
- [ ] Backend exposes `GET /api/ext/describe`.
- [ ] Backend exposes `POST /api/ext/call`.
- [ ] Backend exposes `POST /api/ext/stream/:subscription` if streams are needed.
- [ ] CLI supports `ext describe`, `ext call`, and `ext stream`.
- [ ] CLI has mock-server integration tests.
- [ ] Manifest includes schemas, permissions, examples, and context requirements.
- [ ] Actor context is required for non-public operations.
- [ ] High-risk writes go through draft or approval.
- [ ] Audit log records write attempts.
- [ ] `skills/<app>-cli/references/cli-commands.md` exists.
- [ ] GUI has one human-visible place for agent drafts, approvals, or audit records.

## 11. Anti-patterns

- GUI-only capability with no operation contract.
- CLI command that bypasses backend policy.
- Agent write path with no actor.
- `curl` snippets as the only agent interface.
- Unstructured stdout as success contract.
- Manifest that omits permissions.
- Tests that only verify happy-path UI.
- Secret values printed in CLI output.
- Domain commands added before generic `ext call`.
- Backend routes named after frontend pages.

## 12. 最小可复制 Scaffold

```text
package.json
scripts/
  dev.sh
packages/
  app-protocol/
    package.json
    src/index.js
    src/index.d.ts
    tests/index.test.mjs
  app-cli/
    package.json
    bin/app.mjs
    src/cli.mjs
    tests/cli.test.mjs
    tests/integration.test.mjs
backend/
  ext/
    manifest.ts
    call.ts
    stream.ts
  policy/
    actor.ts
    permissions.ts
  audit/
    audit-log.ts
skills/
  app-cli/
    SKILL.md
    references/cli-commands.md
docs/
  engineering/specs/
    app-for-agent-design-paradigm.md
```

## 13. Final Rule

设计 app 时假设 agent 会在 GUI 完成前先操作它。

这会强迫系统拥有：

- explicit capabilities
- explicit state transitions
- explicit permissions
- explicit errors
- explicit tests
- explicit recovery paths

这些不是 agent 专用要求；它们也会让人类 app 更可靠。
