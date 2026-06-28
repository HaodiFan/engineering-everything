# Route Contract（路由契约）

`data/routes.yaml` 是路由事实源。本文件只定义字段契约和读取方式，不复制 route 表。

## 必填字段

每个 route 必须包含：

- `id`: 稳定路由 ID。
- `skill`: 命中的子 Skill 目录名。
- `priority`: 冲突时的排序依据，数值越小越优先。
- `aliases`: 显式 slash 入口。
- `signals`: 自然语言触发信号。
- `fuzzy_examples`: 模糊输入样例。
- `stages`: 工程阶段。
- `references`: route 命中后可读的 self-contained reference。
- `conflicts`: 已知容易混淆的 route ID。
- `fallback`: 无法确认时退回的 route ID。
- `handoff_to`: 常见后续交接 route ID。
- `direct_call_allowed`: 是否允许用户显式直达该 route。
- `eval_cases`: 覆盖该 route 的 eval scenario ID。

## 读取顺序

1. 先处理显式 alias。
2. 再用 signals 和 fuzzy_examples 判断自然语言意图。
3. 多 route 命中时按 priority、缺失信息和停止条件裁决。
4. route 不明时不要实现，输出缺失内容和下一步问题。
5. 命中 route 后再读取对应子 Skill 和 references。

## 禁止事项

- 不在 bootloader 或 README 复制 route 表。
- 不把用户不满意默认改路由为 learn。
- 不在 legacy scenario map 文档里维护第二套路由事实源。
