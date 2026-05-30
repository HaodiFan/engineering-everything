# 架构选型 Case 库（AI / Agent 专项）

用于 AI / Agent 类项目在 Stage 3 的架构决策。与 `architecture-cases.md` 配合使用——**通用工程问题先在通用 case 库决策，AI 特异的部分在本文件解决**。

格式与通用 case 库一致：定位 / 适用 / 反例 / 代价 / 退出成本 / 组合 / 决策信号 / Worked example / 踩坑。

每大类末尾给决策矩阵。

> 推荐度图例：✅ 推荐 / ◯ 可用但有代价 / ⚠️ 谨慎 / ❌ 不推荐
>
> **编号约定**：通用 case 库（`architecture-cases.md`）用数字编号 0–20；本文件用字母编号 A–K，避免跨文件撞号。`## 0. AI 任务目标分流` 是本库的入口分流，不参与字母序。
>
> **与 `scenario-playbooks.md` 的边界**：本文件回答「**架构选型**」——在哪一层、用什么形态、付什么代价、退出多痛；`scenario-playbooks.md` 回答「**业务场景落地**」——这类业务最小切片是什么、先防什么坑、验证什么算闭环。LLM 调用方式 / RAG / 向量库 / Prompt 管理 / 评估这类**架构维度**留在本文件；OCR/RPA/视觉/数据治理/LLM 生产链路这类**业务场景**留在 scenario-playbooks。两边内容不互相复制，只互相指向。

---

## 0. AI 任务目标分流（先于 LLM / Agent）

AI 项目不要默认等于 LLM 项目。Stage 3 先识别任务目标属于哪个经典场景，再结合**成本、时效、效果、流量、私有化要求**选择：

1. 经典算法
2. 经典算法 + LLM/VLM 兜底
3. 纯 LLM/VLM

成本估算要显式写进 design doc。粗估时可先按单次 LLM/VLM 调用 `0.1 RMB / task` 估算，再替换为具体模型价格。比如 `100000 task/day` 约等于 `10000 RMB/day`，通常不适合纯 API LLM 方案，除非业务价值明确覆盖成本。

### 0.1 NLP 经典场景

典型任务：文本分类、意图识别、情感分析、关键信息提取、命名实体识别、规则字段抽取。

#### NLP 分层路线

| Level | 默认方案 | 适用场景 | 升级信号 |
|---|---|---|---|
| Level 1 | 规则 / 正则 / 字典 / 模板 | 格式稳定、字段固定、可解释性强、成本敏感 | 规则爆炸、长尾表达多 |
| Level 2 | PaddleNLP 零样本 NLP 相关能力 | 没有训练集但标签相对固定；希望本地/低成本快速 baseline | 准确率不足、领域语义复杂 |
| Level 3 | BERT / PaddleNLP fine-tune | 长期运行、私有化部署、预算不高、有数据集或可标注 | 工程量不足、标注成本过高、长尾变化快 |
| Level 4 | LLM structured output / prompt | 无数据集、需要快速落地、流量不大、语义复杂 | 日调用量大、成本不可接受、强私有化 |

分类任务默认判断：

- **没有数据集**：先用 LLM prompt / structured output 快速落地，建立可用 baseline 和失败样例。
- **长期运行 + 私有化部署 + 预算不高**：优先验证 BERT / PaddleNLP 能否达到精度；可用 LLM 作为低置信度兜底。
- **快速落地 + 工程量要少 + 流量不大**：推荐 LLM。成本主要是 API token，必须按日调用量估算。
- **高流量（例如 100000/day 量级）**：优先小模型/经典算法；LLM 只做抽样、人审辅助、低置信度兜底或离线复核。

关键信息提取默认混合：

- 固定格式：规则/正则 + schema 校验。
- 半结构化：规则/模板 + PaddleNLP/BERT 抽取 + 字段校验。
- 自由文本/长尾表达：LLM structured output + Pydantic/schema 校验。
- 关键字段：LLM 不直接拍板，必须有规则校验、人审或低置信度队列。

### 0.2 CV / VLM 经典场景

典型任务：图像分类、目标检测、图像理解、OCR 辅助、实体/实例分割、质量检测、相似度检索。

| 场景 | 默认选择 | 说明 |
|---|---|---|
| 固定图像识别 / 检测 | YOLO 系列 | 任务固定、类别明确、需要 bbox/计数/缺陷定位 |
| 精准分割 | YOLO-seg / 专用分割模型 | 精度和线上稳定性优先 |
| 通用分割 / 交互式分割 | SAM | 类别变化大、先做通用 mask 或辅助标注 |
| 图像语义比对 / 粗比 | image embedding + 向量库 | 相似款、重复图、素材语义检索 |
| 随机问题 / 图像理解 | VLM（视觉语言模型） | 开放问答、描述、解释、审核建议；部署时可用厂商 API 或 vLLM 等推理服务 |

默认原则：

- 固定识别、检测、分割任务不要优先 VLM；先用 YOLO / YOLO-seg / SAM / embedding 等专用栈。
- VLM 适合开放图像理解和兜底解释，不作为高精度 bbox/mask 真相源。
- CV 可以多技术栈组合：`YOLO 检测 → SAM/YOLO-seg 分割 → embedding 粗比 → VLM 理解/解释`。
- 流量是关键决策项：高频任务优先专用模型；VLM 用于低频、长尾、抽样审核或兜底。

### 0.3 统计建模 / 时序分析

典型任务：销量预测、库存预警、价格趋势、异常检测、留存/转化分析、周期性指标分析。

默认路线：

- 表格/经营预测优先 XGBoost / LightGBM baseline。
- 每类具体场景再查对应 SOTA 或领域常用模型；不要凭“AI”泛化选型。
- 时序必须做时间切分验证、滚动回测和业务解释，不用随机切分假装准确。
- LLM 不直接作为数值预测核心；它只做解释报告、洞察草稿，或通过 Agent 调用统计/预测工具实现 chat analysis。

### 0.4 选型矩阵

| 场景 | Level 1 规则/正则 | Level 2 PaddleNLP 零样本 | Level 3 BERT/PaddleNLP | Level 4 LLM/VLM 兜底 | 纯 LLM/VLM |
|---|---|---|---|---|---|
| NLP 固定分类 | ✅ | ✅ | ✅ | ◯ | ◯（低流量/快落地） |
| NLP 关键信息提取 | ✅ | ◯ | ◯ | ✅ | ◯（长尾自由文本） |
| 高流量文本任务 | ✅ | ◯ | ✅ | ◯（低置信度） | ❌ |
| 固定图像检测 | ❌ | ❌ | ✅（YOLO 等专用模型） | ◯（解释） | ❌ |
| 图像分割 | ❌ | ❌ | ✅（YOLO-seg/SAM） | ◯（解释） | ❌ |
| 图像开放理解 | ❌ | ❌ | ◯ | ✅ | ✅ |
| 时序预测 | ✅（统计 baseline） | ❌ | ✅（XGBoost/领域模型） | ◯（解释） | ❌ |
| chat 分析 / 报告生成 | ◯ | ❌ | ◯ | ✅ | ✅ |

---

## A. LLM 调用方式

### A.1 直连厂商 API（OpenAI / Anthropic / Google / 云厂商托管）

- **一句话定位**：应用直接 SDK 调用模型 API。
- **适用场景**：原型、单一模型、流量不大、无统一治理需求。
- **反例**：多模型切换；成本/限流/审计要集中管；多团队共用。
- **主要代价**：每个应用各自管 key、限流、重试、缓存；模型替换要改代码。
- **退出成本**：低-中（依赖具体 SDK 时偏中）。
- **常见组合**：官方 SDK + 简单 retry + Sentry。
- **决策信号**：
  - 选它：单应用、单模型、< 1k QPM。
  - 换掉：多应用复用同一 LLM 能力；要做成本归因；要 A/B 模型。
- **Worked example**：单 SaaS 接入 OpenAI，封装 `llm_client.py` 统一 retry/timeout。
- **常见踩坑**：API key 散落多个仓；没有 rate limit 处理，被限速时全站 503。

### A.2 内部 LLM 网关（自建或开源 LiteLLM/Portkey）

- **一句话定位**：所有 LLM 流量统一过自家网关，做路由、重试、缓存、审计、成本归因。
- **适用场景**：多应用 / 多模型 / 多团队；要统一治理；要切换模型；要做精细成本核算。
- **反例**：一个应用一个模型一个团队（杀鸡用牛刀）。
- **主要代价**：网关自身的可用性与延迟；运维与监控；上下游协议适配。
- **退出成本**：低（恢复直连即可，但所有应用要一起改）。
- **常见组合**：LiteLLM / Portkey / Helicone（观测）/ 自建（FastAPI + Redis 缓存）；前置 OpenAI 兼容协议。
- **决策信号**：
  - 选它：≥ 2 应用使用 LLM；要 A/B 不同模型；财务追问"哪个产品用了多少 token"。
  - 换掉：组织收敛回单团队单应用（少见）。
- **Worked example**：内部网关暴露 OpenAI 兼容 endpoint，按 header 路由到 GPT-4o / Claude / 本地 vLLM；命中 prompt cache 直接返回；导出每 app 的 token 使用率。
- **常见踩坑**：网关阻塞流式响应；流式必须 first-byte 透传，不能整体缓冲。

### A.3 自部署模型（vLLM / TGI / Ollama / SGLang）

- **一句话定位**：在自家 GPU 上跑开源/微调模型。
- **适用场景**：数据主权强；高频调用成本反超托管；要微调；离线/边缘。
- **反例**：流量小（GPU 吃灰）；团队无 ML/Infra 能力；模型更新频率跟不上 SOTA。
- **主要代价**：GPU 成本（即使闲置）；运维；模型质量天花板；版本升级风险。
- **退出成本**：高（推理栈、监控、prompt 都按本地模型调过）。
- **常见组合**：vLLM/SGLang + K8s GPU 调度 + Triton（多模型）+ 监控 GPU util。
- **决策信号**：
  - 选它：合规要求自托管；月 token 量足以打平 GPU 成本；有 ML 团队。
  - 换掉：质量差距持续扩大；流量下来 GPU 闲置。
- **Worked example**：政企客户专属部署 Llama-3-70B-Instruct + LoRA 微调，vLLM 起 4×A100 集群。
- **常见踩坑**：上线后用户体验远不如 GPT；先做盲测对齐基线再决策。

### A.4 混合（默认托管 + 部分自部署）

- **一句话定位**：通用任务走托管，敏感/高频/微调任务走自部署。
- **适用场景**：合规分级；成本与质量两头要。
- **代价**：双栈复杂度；路由策略治理。
- **常见踩坑**：路由规则散落代码各处；统一在网关做。

#### 决策矩阵 — LLM 调用方式

| 场景 | 直连 | 网关 | 自部署 | 混合 |
|---|---|---|---|---|
| 原型 / 单应用 | ✅ | ⚠️ | ❌ | ❌ |
| 多应用 / 多模型 | ⚠️ | ✅ | ◯ | ✅ |
| 强合规 / 数据主权 | ❌ | ◯ | ✅ | ✅ |
| 月 token 极大 | ❌ | ✅ | ✅ | ✅ |
| 团队无 ML/Infra | ✅ | ✅ | ❌ | ◯ |

---

## B. Agent Runtime 形态

### B.1 In-process（与主应用同进程）

- **一句话定位**：Agent 逻辑作为函数/库直接在 web/桌面进程里跑。
- **适用场景**：单步/短链工具调用；无需独立伸缩；强状态共享。
- **反例**：长任务（阻塞主进程）；多并发 Agent 需要隔离；故障传播会拖垮主应用。
- **主要代价**：耦合主应用部署节奏；GIL/事件循环阻塞。
- **退出成本**：低（抽接口拆出去即可）。
- **常见组合**：FastAPI/Next.js route 直接调 Agent 模块。
- **决策信号**：单次调用 < 数秒；并发不高；不需要崩溃隔离。
- **Worked example**：聊天机器人后端 Next.js route 内直接编排 LLM + 工具，SSE 流式返回。
- **常见踩坑**：长链 Agent 把 web worker 全占；改异步 + 拆 sidecar/remote。

### B.2 Sidecar（伴随主应用的本地 Agent 进程）

- **一句话定位**：Agent 单独进程，通过 IPC/HTTP/gRPC 与主应用交互；通常同机部署。
- **适用场景**：桌面应用（本地 Agent 处理本地数据）；后端伴生 Agent 需要独立伸缩。
- **反例**：完全无状态、可水平扩展（用 Remote）；超轻 Agent（用 In-process）。
- **主要代价**：进程生命周期管理；IPC 协议；崩溃恢复。
- **退出成本**：中。
- **常见组合**：桌面 Tauri 启动子进程 Agent（Python/Rust）；后端用 systemd 伴生 worker。
- **决策信号**：本地数据/工具访问；崩溃需隔离；语言异构（前端 TS + Agent Python）。
- **Worked example**：桌面知识库应用，Tauri 主进程 + Python Agent sidecar，通过本地 HTTP 通信，启停同生命周期。
- **常见踩坑**：sidecar 没正确退出，遗留僵尸进程；用 PID 文件 + 启动时清理。

### B.3 Remote（独立服务/集群）

- **一句话定位**：Agent 作为独立服务，HTTP/gRPC/MQ 通信，独立部署伸缩。
- **适用场景**：高并发；多客户端共用；需要 GPU/特殊资源；强故障隔离。
- **反例**：低频简单任务（额外网络成本）；本地数据访问需求。
- **主要代价**：网络延迟；契约维护；独立 CI/CD。
- **退出成本**：中。
- **常见组合**：FastAPI + worker pool；K8s 部署；前置 LLM 网关。
- **决策信号**：QPS 高；需要 GPU；多客户端复用。
- **Worked example**：B 端 SaaS 把 Agent 抽成 `agent-service`，多个产品共用，K8s HPA 按 LLM 调用排队长度扩缩。
- **常见踩坑**：长任务用同步 HTTP，超时各种翻车；用 WebSocket/SSE 或异步 job。

### B.4 多 Agent 编排（Worker pool / Orchestrator）

- **一句话定位**：多个 agent 实例由调度层协调，处理任务队列。
- **适用场景**：批量处理；多步骤工作流；研究型多 agent 协作。
- **反例**：单步对话场景；过早抽象。
- **主要代价**：任务状态、失败补偿、可观测性复杂。
- **常见组合**：Temporal/Inngest/Trigger.dev + 一组 agent worker；或自建队列 + worker。
- **常见踩坑**：用普通队列做长事务，状态飘；用工作流引擎。

### B.5 流式任务 Watchdog（first chunk / chunk idle / total timeout）

- **一句话定位**：对 LLM/Agent 长任务的流式输出建立可观测的超时语义。
- **适用场景**：SSE/WebSocket 流式返回、CrewAI/LangChain event bus、长链 Agent、用户等待可见进度。
- **反例**：纯同步短调用，直接 request timeout 足够。
- **主要代价**：需要统一 request_id / call_id / step_run_id；要区分“请求活跃心跳”和“真实输出 chunk”。
- **常见组合**：
  - `first_chunk_timeout`：调用开始后一直没有首个 chunk。
  - `chunk_idle_timeout`：首个 chunk 后长时间没有新 chunk。
  - `total_timeout`：整个 step 的最大耗时。
  - `cancel/abandoned` 状态：外层已超时但底层 provider 后续仍返回。
- **决策信号**：用户能看到“开始了但一直没字”；线上排障需要知道卡在首包还是中途静默。
- **常见踩坑**：把 `llm_start` 或最终 `llm.call()` 返回当作输出活动，导致 watchdog 误判；流式活跃性应以 chunk 事件为主信号。

#### 决策矩阵 — Agent Runtime

| 场景 | In-process | Sidecar | Remote | Orchestrator |
|---|---|---|---|---|
| 单步聊天 | ✅ | ◯ | ◯ | ❌ |
| 桌面 + 本地数据 | ⚠️ | ✅ | ❌ | ◯ |
| 多客户端共用 | ❌ | ◯ | ✅ | ◯ |
| 长链 / 多 agent | ❌ | ◯ | ✅ | ✅ |
| 高并发批处理 | ❌ | ❌ | ◯ | ✅ |
| 流式用户等待 | ⚠️ | ◯ | ✅ | ◯ |

---

## C. 工具调用与协议

### C.1 厂商原生 Function Calling / Tool Use

- **一句话定位**：用 OpenAI/Anthropic 等模型自带的工具调用接口。
- **适用场景**：上线快；工具数量有限；模型对工具的训练优化已经足够。
- **反例**：跨厂商切模型频繁；工具集要被多个 Agent/客户端复用。
- **主要代价**：与厂商协议绑定；切模型时要适配差异。
- **常见踩坑**：工具描述写得太啰嗦或太抽象，模型乱调或不调。

### C.2 MCP（Model Context Protocol）

- **一句话定位**：把"工具/资源/prompt"标准化为 MCP server，任何兼容客户端可接。
- **适用场景**：工具要跨多个 agent / 客户端复用；想要工具生态可插拔；桌面 IDE/编辑器场景。
- **反例**：仅一个应用一组工具，没有复用必要。
- **主要代价**：协议学习；MCP server 自身的运维；权限/安全模型要重新想。
- **退出成本**：低-中（可降级为厂商原生 function calling）。
- **常见组合**：本地 MCP server（stdio）+ 桌面客户端；远程 MCP server（HTTP/SSE）+ 多端共用。
- **决策信号**：工具被 ≥ 2 个客户端使用；想接入 Claude Desktop / Cursor 等已支持 MCP 的宿主。
- **Worked example**：研发内部工具集封成 MCP server（git、内部 API、文档检索），员工在 Claude Desktop 里直接用。
- **常见踩坑**：未做权限/审计，MCP server 暴露过多能力。

### C.3 自定义工具协议

- **一句话定位**：自家定义 JSON schema 描述工具，自家代码 dispatch。
- **适用场景**：闭环可控；需要 fine-grained 权限/审计；不依赖厂商或 MCP。
- **反例**：标准协议已够用；想要外部生态贡献。
- **代价**：自家维护描述/dispatch/权限/版本。
- **常见踩坑**：工具描述与实现漂移；用 schema 校验 + 单元测试。

### C.4 工具沙箱与权限

- **沙箱**：Code interpreter / Docker / E2B / Cloudflare Sandbox / WASM。
- **决策**：执行用户/Agent 生成的代码必须沙箱；只调白名单 API 可以不上沙箱。
- **常见踩坑**：把 shell 工具直接给 Agent，没有沙箱 → 灾难。

#### 决策矩阵 — 工具调用

| 场景 | 厂商原生 | MCP | 自定义 | 沙箱 |
|---|---|---|---|---|
| 单应用快速上 | ✅ | ◯ | ◯ | 视工具而定 |
| 跨客户端复用 | ⚠️ | ✅ | ◯ | 视工具而定 |
| 强合规 + 审计 | ◯ | ◯ | ✅ | 必备 |
| 执行用户代码 | — | — | — | ✅ 必备 |

---

## D. 记忆与状态

### D.1 无状态（Pure Stateless）

- **一句话定位**：每次请求独立，上下文全靠客户端传。
- **适用**：FAQ / 单轮问答 / API 形式 LLM。
- **反例**：连续对话、长期偏好。

### D.2 短期会话记忆（Conversation buffer）

- **一句话定位**：保留最近 N 轮或 N tokens 的对话。
- **适用**：聊天机器人；编辑器助手。
- **代价**：超出窗口要截断/摘要；会话边界判断。
- **常见踩坑**：硬截断丢系统提示；用滑窗 + 摘要。

### D.3 摘要记忆（Summarization Memory）

- **一句话定位**：定期把旧对话摘要为压缩文本，留窗口给新内容。
- **代价**：摘要质量决定记忆质量；摘要本身耗 token。
- **常见踩坑**：摘要后丢失关键事实（人名、数字）；定向 prompt 强调保留。

### D.4 长期记忆（Profile / Facts / Preferences）

- **一句话定位**：把"关于用户/项目的稳定事实"持久化，每次会话注入。
- **适用**：个性化助手、Coding Agent、客户支持。
- **代价**：写入策略（什么算"事实"）；冲突解决；隐私。
- **常见组合**：结构化（KV/JSON）+ 非结构化（向量库）。
- **常见踩坑**：把所有对话都写长期记忆 → 噪音爆炸；用提取器 + 阈值。

### D.5 向量库语义记忆 / RAG-as-memory

- **一句话定位**：把过去对话/知识切片向量化，按需检索。
- **适用**：大量历史 + 跨会话引用。
- **代价**：检索质量；新鲜度；召回噪音。
- **常见踩坑**：把记忆 = RAG，丢失结构化偏好；混合用。

### D.6 知识图谱记忆（Graph Memory）

- **一句话定位**：把实体关系入图，查询走图查询。
- **适用**：多实体强关系（人物/项目/任务网络）。
- **代价**：抽取与维护；查询语言学习。
- **常见踩坑**：起步就上图，过度工程；先 KV + 向量，必要再升级。

### D.7 Episodic / Semantic / Procedural 三层

- **Episodic（情景）**：发生过什么（对话历史/动作日志）。
- **Semantic（语义）**：稳定事实（偏好、关系）。
- **Procedural（程序）**：怎么做（学到的策略/skill）。
- 完整 Agent 系统三层都要，但起步只做 Episodic + Semantic。

#### 决策矩阵 — 记忆策略

| 场景 | 无状态 | 会话窗 | 摘要 | 长期事实 | 向量记忆 | 图记忆 |
|---|---|---|---|---|---|---|
| 单轮问答 API | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 普通聊天助手 | ❌ | ✅ | ◯ | ◯ | ◯ | ❌ |
| 个性化助手 | ❌ | ✅ | ✅ | ✅ | ✅ | ◯ |
| Coding Agent | ❌ | ✅ | ✅ | ✅ | ✅ | ◯ |
| 强关系网络 | ❌ | ◯ | ◯ | ◯ | ✅ | ✅ |

---

## E. RAG 架构

### E.1 朴素向量 RAG

- **一句话定位**：query → embedding → top-k 检索 → 拼 prompt。
- **适用**：文档问答 MVP；知识量中等。
- **反例**：表格/数字密集；多跳推理；命名实体精确匹配。
- **代价**：召回质量天花板；切片策略影响巨大。
- **常见踩坑**：固定 chunk size 切割破坏语义；用 markdown-aware / 句子边界。

### E.2 混合检索（Vector + BM25 + Reranker）

- **一句话定位**：稀疏（关键词）+ 稠密（语义）召回 + 交叉编码 rerank。
- **适用**：生产级文档问答；命名实体查询；多语言。
- **代价**：多一层服务；rerank 增加延迟。
- **常见组合**：Elasticsearch / OpenSearch + 向量库 + Cohere/bge-reranker。
- **决策信号**：纯向量 RAG 召回明显漏关键词查询。
- **Worked example**：客服文档库 ES（BM25 top 50）+ Qdrant（语义 top 50）→ 合并去重 → bge-reranker top 10 → 拼 prompt。
- **常见踩坑**：rerank 阶段超时不设 fallback；模型挂掉直接全军覆没。

### E.3 多跳 / Agentic RAG

- **一句话定位**：Agent 自己决定何时检索、用什么 query、迭代几次。
- **适用**：复杂问题需要多次检索 + 综合；问题分解。
- **反例**：简单 FAQ（增加延迟与成本）。
- **代价**：延迟高、成本高、可观测难。
- **常见组合**：ReAct + 检索工具 + 中间笔记。
- **常见踩坑**：未限制最大跳数 → 死循环或成本爆炸。

### E.4 GraphRAG / 结构化 RAG

- **一句话定位**：先抽取实体关系建图，再用图查询 + 子图 LLM 总结。
- **适用**：跨文档的实体网络问题；长尾报告分析。
- **反例**：简单文档问答（朴素 RAG 已够）。
- **代价**：建图阶段昂贵；维护复杂。
- **常见踩坑**：忽略增量更新，全量重建拖垮成本。

### E.5 SQL / 结构化数据 RAG（Text-to-SQL）

- **一句话定位**：用户自然语言 → SQL → DB → 答案。
- **适用**：报表/统计问答；结构化数据为主。
- **代价**：SQL 正确性与安全（注入/破坏）；权限隔离。
- **常见组合**：schema 检索 + few-shot examples + SQL 校验 + 只读连接。
- **常见踩坑**：直接执行 LLM 生成 SQL 写库；只允许只读 + 白名单语句。

### E.6 切片策略（Chunking）

- 固定大小（兜底但破坏语义）/ 语义切（更好）/ markdown 结构 / 父子（小块检索 + 大块给上下文）。
- 起步：父子 + markdown 结构。

### E.7 评估

- 检索：Recall@K / MRR / nDCG。
- 生成：Faithfulness / Answer relevance / Context precision（Ragas / TruLens）。
- **常见踩坑**：只看生成质量不看检索召回，问题难定位。

#### 决策矩阵 — RAG 架构

| 场景 | 朴素向量 | 混合+rerank | Agentic | GraphRAG | Text-to-SQL |
|---|---|---|---|---|---|
| 文档问答 MVP | ✅ | ◯ | ❌ | ❌ | ❌ |
| 生产文档问答 | ◯ | ✅ | ◯ | ◯ | ❌ |
| 复杂多跳分析 | ❌ | ◯ | ✅ | ✅ | ◯ |
| 报表/数据问答 | ❌ | ❌ | ◯ | ❌ | ✅ |
| 实体网络分析 | ❌ | ◯ | ◯ | ✅ | ◯ |

---

## F. 向量库

### F.1 pgvector

- **定位**：Postgres 扩展，向量与业务数据同库。
- **适用**：< 1000 万向量；想要事务一致；运维简单。
- **反例**：极大规模 / 极致延迟 / 复杂过滤。
- **代价**：高维大规模性能不及专用库。
- **退出成本**：低（数据迁移到专用库容易）。
- **常见踩坑**：未建 IVFFlat/HNSW 索引，全表扫描慢。

### F.2 Qdrant

- **定位**：开源、Rust、过滤强、生产成熟。
- **适用**：中大规模；需要 metadata 过滤；自托管。
- **常见踩坑**：单机内存不够时未配磁盘 mmap。

### F.3 Weaviate

- **定位**：开源 + 商用云；schema 化 + 模块（vectorizer 内置）。
- **适用**：希望开箱多模态、内置混合检索。

### F.4 Pinecone

- **定位**：纯托管、零运维。
- **适用**：不想运维；快速上线。
- **代价**：vendor lock-in；成本随规模上去。

### F.5 LanceDB / Chroma

- **定位**：嵌入式 / 文件即库。
- **适用**：本地、桌面、个人助手、边缘设备。
- **反例**：多租户大规模。

### F.6 Milvus

- **定位**：超大规模分布式；GPU 索引。
- **适用**：亿级向量；需要 GPU 加速。
- **代价**：运维复杂。

#### 决策矩阵 — 向量库

| 场景 | pgvector | Qdrant | Weaviate | Pinecone | LanceDB/Chroma | Milvus |
|---|---|---|---|---|---|---|
| MVP / 与业务同库 | ✅ | ◯ | ◯ | ◯ | ❌ | ❌ |
| 中大规模自托管 | ◯ | ✅ | ✅ | ❌ | ❌ | ◯ |
| 零运维快上线 | ◯ | ◯ | ◯ | ✅ | ❌ | ❌ |
| 桌面 / 边缘 | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| 亿级 + GPU | ❌ | ◯ | ◯ | ◯ | ❌ | ✅ |

---

## G. Prompt 管理

### G.1 内联在代码

- **适用**：MVP；prompt 不会被产品/运营改。
- **反例**：prompt 频繁迭代；非工程师参与。

### G.2 仓内集中目录（`prompts/`）

- **适用**：版本控制；和代码一起 review；多人协作。
- **常见组合**：Jinja/Mustache 模板 + 单元测试 prompt 渲染。
- **常见踩坑**：把 prompt 散落各处；强制全部从 `prompts/` 加载。

生产链路建议采用 prompt registry，而不是把大 prompt 内联在 YAML 或代码中：

```text
prompts/
└── <task_name>/
    ├── manifest.yaml        # default_version, aliases, status
    ├── vYYYY_MM_DD.yaml     # system/user template/schema
    └── eval_cases.jsonl
```

`manifest.yaml` 至少包含：

- `default_version`
- `aliases`（如 `current`、`original`）
- `versions`
- 每个版本的 `status`、`summary`、`based_on`

运行时记录 `requested_prompt_variant` 和 `resolved_prompt_version`。版本不存在必须快速失败，不静默回退。

### G.3 平台托管（PromptLayer / Langfuse / LangSmith / Helicone）

- **适用**：产品/运营改 prompt；需要 A/B；要观测每条 prompt 表现。
- **代价**：依赖外部服务；故障兜底；数据外送合规。
- **决策信号**：非工程师要直接改 prompt；要做 prompt A/B + 指标对齐。

### G.4 Prompt 版本与 A/B

- 每条 prompt 必须有 ID + 版本；线上引用版本而非"最新"。
- A/B 关注点：质量（人评/eval）+ 成本（token）+ 延迟。
- 回滚优先改 manifest 的默认指针，不改业务代码。
- 单请求回放允许显式指定版本号，保证历史问题可复现。

#### 决策矩阵 — Prompt 管理

| 场景 | 内联 | 仓内目录 | 平台托管 |
|---|---|---|---|
| MVP / 工程团队 | ✅ | ✅ | ❌ |
| 多人迭代 + 测试 | ⚠️ | ✅ | ◯ |
| 非工程师参与 | ❌ | ⚠️ | ✅ |
| 在线 A/B + 指标 | ❌ | ◯ | ✅ |

---

## H. 评估与回归（Evaluation）

### H.1 离线 Eval（Offline Evaluation）

- **一句话定位**：固定测试集 + 自动评分（rule / LLM-as-judge / 人评）跑回归。
- **适用**：模型/prompt 升级前；回归门禁。
- **常见组合**：Promptfoo / Ragas / DeepEval / 自建。
- **常见踩坑**：测试集与生产分布偏差大；定期从生产采样补充。

### H.2 在线 A/B 与影子流量

- **适用**：生产对比新旧版本；金丝雀发布。
- **代价**：流量切分基础设施；指标采集。
- **常见踩坑**：用户感知度量（满意度）和 LLM 自评相关性差；二者并行。

### H.3 LLM-as-Judge

- **适用**：开放式生成评估（摘要、回答质量）。
- **代价**：判官模型偏好（位置偏置、长度偏置）；需要校准与 sanity check。
- **常见踩坑**：用同款模型自评自家输出；用更强或不同家族判官。

### H.4 人工评估

- **适用**：上线前核心质量基线；判官校准。
- **代价**：成本与速度。
- **常见组合**：抽样 + 标注平台（Label Studio / 自建）。

### H.5 Trace / 观测

- 单次调用全链路（prompt + tool calls + 结果）入 Langfuse/LangSmith/Helicone。
- 一定要采样保存 prompt 与输出，否则线上故障无法复盘。
- 每次调用至少记录：
  - `request_id` / `call_id` / `step_run_id`
  - provider / model / route / retry / timeout
  - prompt id / prompt version / input hash
  - token usage / latency / first chunk latency / finish reason
  - structured output 校验结果
  - error / cancel / abandoned 状态

### H.6 Replay / 失败用例库

- **一句话定位**：把线上失败调用转成可重复执行的回归样例。
- **适用场景**：prompt/model/路由频繁变更；客户反馈需要复盘；强质量要求。
- **常见组合**：trace payload → 脱敏 → eval case → 修复后纳入 CI 或手动 pre-release gate。
- **常见踩坑**：只保留最终错误文案，不保留 prompt version 和输入上下文，导致无法复现。

#### 决策矩阵 — 评估

| 场景 | 离线 eval | 在线 A/B | LLM judge | 人评 | Trace 观测 |
|---|---|---|---|---|---|
| MVP | ◯ | ❌ | ◯ | ◯ | ✅ |
| 生产产品 | ✅ | ◯ | ◯ | ◯ | ✅ |
| 强依赖质量 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 开放生成 | ◯ | ◯ | ✅ | ✅ | ✅ |
| prompt 频繁迭代 | ✅ | ◯ | ◯ | ◯ | ✅ |

---

## I. 安全与责任 AI

### I.1 Prompt Injection 防护

- **基本认识**：LLM 无法 100% 防 injection；纵深防御。
- **手段**：
  - 不让 LLM 输出直接执行（人/规则把关）。
  - 工具调用强权限边界，不靠 prompt 限制。
  - 用 system prompt 隔离 + 输入标记 + 提取式输出（structured output）。
  - 检测器（开源 prompt-injection 分类器、规则）。
- **常见踩坑**：把"请忽略后续指令"当万能护栏。

### I.2 输出审核（Moderation）

- 厂商 moderation API + 自定义规则；必要时人审。
- 关注：违法、隐私、虚假承诺、PII 回流。
- 常见踩坑：仅审用户输入不审模型输出。

### I.3 数据安全 / PII

- 训练/微调数据 PII 脱敏。
- 调用上行做 PII 检测/脱敏（Presidio 等）。
- 日志脱敏；审计可追溯。

### I.4 越权与凭证管理

- Agent 凭证最小权限；动态短期凭证（STS）。
- 工具调用每次校验调用者上下文，不靠 LLM 自觉。
- 常见踩坑：Agent 拿到 admin token 长期持有。

### I.5 输出可控性 / Structured Output

- JSON Schema / function calling / Pydantic 校验失败重试。
- 关键决策不靠自由文本解析。

### I.6 Hallucination 缓解

- RAG 引用强制（无引用拒答）+ 不知道就说不知道（prompt + eval 强化）+ 关键事实结构化校验。
- 常见踩坑：UI 不展示引用；用户无法判断真假。

#### 决策矩阵 — 安全最小集合

| 场景 | Injection 防 | 输出审核 | PII 脱敏 | 最小权限 | 结构化输出 | 引用强制 |
|---|---|---|---|---|---|---|
| 内部工具 | ◯ | ◯ | ◯ | ✅ | ✅ | ◯ |
| C 端产品 | ✅ | ✅ | ✅ | ✅ | ✅ | ◯ |
| 强合规（医疗/金融）| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Agent 执行写操作 | ✅ | ✅ | ◯ | ✅ | ✅ | ◯ |

---

## J. 成本与延迟优化

### J.1 模型路由 / 分级

- 简单任务用小模型，复杂用大模型；Router 决定。
- 常见组合：自家网关 + heuristic / classifier。

### J.2 Prompt Caching（厂商原生）

- 长系统提示 + RAG 文档前缀缓存（OpenAI / Anthropic / Gemini）。
- 节省重复部分的 input 成本与延迟。
- 常见踩坑：每次都改前缀几个字，缓存命中率 0。

### J.3 Output 截断与流式

- max_tokens 设上限；用户感知用流式 first-byte。
- 流式链路必须定义 first chunk timeout、chunk idle timeout 和 total timeout，阈值走配置，不在业务代码里 hardcode。

### J.4 Embedding 缓存

- 同样文本不要重复 embed；按 hash 落库。

### J.5 Batch / Async API

- 离线任务用 batch API（OpenAI batch / Anthropic batch）成本减半。

### J.6 蒸馏 / 微调

- 高频固定任务用小模型微调替代大模型 prompt。
- 代价：训练数据、运维；评估必须建立。

#### 决策矩阵 — 成本/延迟

| 症状 | 第一动作 | 第二动作 |
|---|---|---|
| token 成本高 | Prompt cache + 模型分级 | Embedding 缓存 + batch |
| 首字慢 | 流式 + 减小 system prompt | 边缘部署 / 区域选择 |
| 长尾延迟大 | 超时 + 重试 + fallback 模型 | rerank 异步 / 跳过 |
| 高频固定任务 | 蒸馏 / 微调 | 规则前置不调 LLM |
| 流式中途卡死 | chunk idle timeout + cancel 标记 | fallback / retry / 用户可见恢复 |

---

## K. 数据飞轮 / 反馈闭环

### K.1 Trace + 用户反馈采集

- 拇指/标签 + 自由文本 + 操作信号（重试、放弃）。
- 关键：把反馈关联到具体 trace（prompt+context+output）。

### K.2 失败用例库

- 用户负反馈 → 加入回归测试集 → 修复后变成 eval 用例。
- 常见踩坑：负反馈无人看；定期 review 流程化。

### K.3 自动标注 + 人审

- LLM 初标 + 人复核；标注成本下降。

### K.4 微调数据生产

- 高质量 trace → 蒸馏数据 → 微调小模型。

#### 决策矩阵 — 反馈闭环投入

| 阶段 | 反馈采集 | 失败用例库 | 自动标注 | 微调数据 |
|---|---|---|---|---|
| MVP | ✅ | ◯ | ❌ | ❌ |
| 产品化 | ✅ | ✅ | ◯ | ◯ |
| 规模化 | ✅ | ✅ | ✅ | ✅ |

---

## AI Stage 3 决策清单（在通用清单后增补）

> AI 项目专用的 master checklist。`stage-playbook.md` Stage 3 直接指向本清单——通用 21 项跑完再跑这 15 项 AI 维度。

完成 `architecture-cases.md` 的综合决策清单后，AI 项目还需在 `ARCHITECTURE.md` 的 Technical Baseline 下增补 AI 维度：

| AI 维度 | 选定方案 | 主要理由 | 主要代价 | 退出成本 |
|---|---|---|---|---|
| AI 任务类型分流（0） | | | | |
| LLM 调用方式（A） | | | | |
| Agent runtime 形态（B） | | | | |
| 工具调用协议（C） | | | | |
| 沙箱与权限（C.4） | | | | |
| 记忆策略（D） | | | | |
| RAG 架构（E） | | | | |
| 向量库（F） | | | | |
| Prompt 管理（G） | | | | |
| 评估方案（H） | | | | |
| Trace / replay（H） | | | | |
| 安全与审核（I） | | | | |
| 成本与延迟优化（J） | | | | |
| 流式 timeout 语义（B/J） | | | | |
| 反馈闭环（K） | | | | |

> 没有 AI 能力的项目跳过本文件。Agentic 关键的项目（Coding Agent、Research Agent、客服 Agent、桌面 Agent）通常 A–I 全部要决策。
