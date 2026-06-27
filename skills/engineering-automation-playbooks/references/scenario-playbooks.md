# 场景 Playbooks（本地项目经验版）

本文件用于补齐“项目形态”之外的业务自动化场景。项目形态回答“系统长什么样”，场景回答“这类问题通常怎么落地、先防什么坑、验证什么才算闭环”。

> **与 case 库的分工**（v0.4.1 起明确）：
> - 本文件回答「**业务场景落地**」：最小切片、默认工具、验证门禁、反模式。
> - `architecture-cases.md` / `architecture-cases-ai.md` 回答「**架构选型**」：在哪一层、用什么形态、付什么代价。
> - 命中重叠话题（例如 LLM 生产链路 vs `architecture-cases-ai.md` 的 LLM 调用 / Prompt 管理 / 评估）时，本文件给切片，case 库给选型——**两边内容不复制，只互相指向**。
> - 命中场景但还没选定架构 → 先回 `architecture-cases.md` §0 形态决策，再回本文件。

使用顺序：

1. 先按 `SKILL.md` 判断阶段与项目形态。
2. 如果任务命中下表场景，再读取本文件对应小节。
3. 场景建议只改变技术选型、切片和验证门禁，不替代 requirements / design doc / ADR。

## 场景速查

| 信号 | 场景 | 常见形态 |
|---|---|---|
| 淘宝系/京东/拼多多/抖音等电商平台，公域价格/详情/直播评论，商家后台报表/订单/客服记录，周期抓取 | RPA / 数据采集 | Python Agent/CLI、Web+Backend、Desktop+Local Agent |
| PDF、合同、账单、报告、表格、发票、版面恢复、关键信息提取 | OCR / 文档智能 | Python Agent/CLI、Web+Backend |
| 图片相似度、目标检测、设计查重、质检标注、截图轨迹 | 视觉 / 多媒体质检 | Python Agent/CLI、Web+Backend、Desktop+Local Agent |
| 多平台数据清洗、数据中台、经营报表、自然语言报表 | 数据治理 / 分析报表 | Web+Backend、Full-stack Monorepo |
| prompt 频繁迭代、LLM pipeline、Agent 调 API、批量生成/评估 | LLM 生产链路 | Web+Backend、Python Agent/CLI |
| Playwright/Selenium、页面截图、网站可发现性、WebAgent 数据 | 浏览器自动化 / WebAgent 数据 | Python Agent/CLI、Web+Backend |
| 临时验证想法、算法试验、客户演示、一次性脚本 | POC / Spike | Python Agent/CLI、单页 Web、Notebook |

---

## A. RPA / 数据采集

典型来源：淘宝系、京东、拼多多、抖音/抖店等中国电商平台；公域价格、详情页、搜索/榜单、直播评论；商家管理后台、客服记录、ERP/报表系统、公开企业信息、飞书/外部平台数据。

### 第一原则

- **API 优先**：官方 API / 合规导出 > 浏览器自动化 > 桌面 RPA > 图像/OCR > 抓包。越往后越脆、越要合规确认。
- **原始数据保留**：raw payload / screenshot / HTML / timestamp / source URL 要留存，便于复盘。
- **采集与分析解耦**：collector 只负责稳定拿数；cleaner/normalizer 负责结构化；analysis/report 只读标准化结果。
- **人机兜底**：目标平台变化、验证码、登录失效、反爬升级必须有失败状态、重试策略和人工接管点。

### 中国电商数据入口判断

中国电商数据分析先按平台和数据源类型拆，不先按 dashboard 或指标拆。

第一层：平台。

- 淘宝系：淘宝 / 天猫 / 千牛 / 生意参谋 / 直通车等。
- 京东：京麦 / 京东商智 / 京准通等。
- 拼多多：拼多多商家后台 / 多多进宝等。
- 抖音：抖店 / 巨量千川 / 直播间 / 达人内容等。

第二层：数据源类型。

| 数据源类型 | 示例 | 默认策略 | 风险 |
|---|---|---|---|
| 公域数据 | 价格、详情页、搜索结果、榜单、评价、直播评论 | 官方公开能力 > 浏览器/手机 RPA > 人工抽样 | 难度高，风控强，频繁变更 |
| 商家管理后台 | 订单、商品、库存、客服、经营报表、广告数据 | 官方 API / 后台导出 > 浏览器自动化 > 手机 RPA | 登录态、权限、账号安全 |
| 客户自有系统 | ERP、WMS、CRM、财务表 | API / DB readonly / 导出任务 | 字段口径不一致 |

公域数据获取必须先判断合法性和授权边界。逆向、抓包、绕过风控属于高风险方案，默认不作为推荐路径；只有在明确授权、测试环境或合规确认后才能进入候选，并必须写入 design doc 的风险与替代方案。

商家管理后台数据优先走平台自己的管理系统能力：官方开放平台、报表导出、异步下载任务、后台页面导出。自动化只作为补位，不把后台页面当稳定 API。

手机 RPA 适用于移动端 App-only、Web 风控过强、或必须保留“接近人工操作路径”的公域采集。它仍然需要账号授权、设备池治理、截图/录屏证据、节流、失败状态和人工接管，不等于规避合规。

### RPA 工具实战偏好

以下偏好只适用于已授权账号、商家后台或客户允许的采集场景；不能替代平台 ToS、客户授权和合规确认。

| 场景 | 默认选择 | 说明 |
|---|---|---|
| 中国电商商家管理后台 | `undetected-chromedriver` + Selenium | 比普通 Chromium 更贴近真实浏览器环境；适合千牛/京麦/抖店/拼多多后台这类强登录态后台 |
| 常规 Web 自动化 / 新项目框架 | Playwright 或 Selenium | Playwright 是更现代的浏览器自动化框架；Selenium 生态更老、更容易接 `undetected-chromedriver` |
| 手机 RPA | Appium + ADB / iOS automation | App-only、公域移动端、直播/短视频等优先用移动设备自动化 |
| 元素定位 | XPath 优先，配合文本锚点和层级锚点 | 商家后台 DOM 经常动态化；避免只依赖第 N 个 div 或易变 class |
| 动作节奏 | bounded random sleep + rate limiter | 点击、滚动、翻页、导出不要高频；sleep 要有上下限和任务级节流 |

实现约束：

- 商家后台默认不要从 plain Chromium 起步；先评估 `undetected-chromedriver` 是否更稳。
- 每个动作前检查页面状态，动作后等待明确状态变化，不只靠固定 sleep。
- random sleep 是稳定性与节流手段，不是合规替代；频率、账号、设备和失败重试都要写进 design doc。
- selector 维护要集中管理，按平台/页面分组，页面改版时能快速定位影响范围。

### 电商数据分析开工问题

1. 目标平台是哪几个：淘宝系 / 京东 / 拼多多 / 抖音？
2. 数据源是公域数据，还是商家管理后台，还是客户自有系统？
3. 需要的数据类型是什么：价格 / 详情页 / 评价 / 直播评论 / 订单 / 商品 / 库存 / 广告 / 客服？
4. 是否有账号、店铺、客户授权和平台允许的获取方式？
5. 采集频率和延迟要求是什么：一次性、日级、小时级、近实时？
6. 是否要保留原始证据：screenshot、HTML、导出文件、raw API payload、录屏？

### 技术选型默认

| 问题 | 默认选择 | 换方案信号 |
|---|---|---|
| Web 页面采集 | 商家后台优先 `undetected-chromedriver` + Selenium；常规 Web 用 Playwright/Selenium | 普通 Chromium 不稳定、后台登录态复杂、需要更贴近真实浏览器时用 `undetected-chromedriver` |
| 移动端采集 | Appium / ADB / iOS automation + OCR fallback | 公域数据风控强、App-only、需要接近人工路径 |
| 桌面客户端操作 | pywinauto / AppleScript / accessibility API / OCR fallback | 客户端频繁改版或无稳定控件树 |
| 周期任务 | cron + job table 起步；复杂重试用 RQ/Celery/Temporal | 任务跨天、需补偿、状态多步骤 |
| 数据存储 | raw bucket + normalized tables | raw 数据量大到影响 OLTP，分到对象存储/数仓 |
| 反爬与合规 | 先写约束和 owner 确认 | 采集涉及登录、个人数据、平台 ToS 风险 |

### 最小切片

1. 单来源、单账号、单页面/接口采集成功。
2. 原始证据落盘：raw + screenshot/HTML + run metadata。
3. 标准化出一张最小表或 JSON schema。
4. 失败路径可见：登录失败、页面变更、限流、空数据。
5. 一个 smoke command 可重复运行。

### Design Doc 必写

- 数据来源与授权边界。
- 登录态、cookie、secret 存储方式。
- 采集频率、限流、失败重试、人工接管。
- raw / normalized / derived 三层数据位置。
- 平台结构变化时如何发现与回滚。

### 验证门禁

- 对 3–5 个真实样本运行。
- 采集结果可追溯到原始证据。
- 断网、登录失效、空页面、字段缺失至少覆盖 smoke。
- 不把 cookie、客户数据、导出原始敏感文件提交进 repo。

### 反模式

- 把采集、清洗、分析写在一个脚本里。
- 只保存最终 CSV，不留 raw 和证据。
- 依赖页面第 N 个 div，没有稳定 selector 和变更探测。
- 用“图像识别没有法律风险”替代合规确认。

---

## B. OCR / 文档智能

典型来源：合同解析、债券/评级报告、PDF 差异对比、发票/表格、检测报告、账单归档、版面恢复。

### 第一原则

- **先定义输出 schema，再选 OCR/LLM**。没有 schema 的文档智能会退化成摘要工具。
- **版面与文本分层**：page image / layout blocks / OCR lines / extracted fields / reviewed result 分开存。
- **资源规格决定 OCR 引擎**：OCR 只是后台基础能力且服务器只有 2C2G/2C4G 时，优先轻量方案；PaddleOCR 安装和运行都重，不默认放进低配后台。
- **置信度与人工复核是产品功能**，不是后处理。
- **LLM 不直接决定关键字段**：金额、日期、责任条款、合规字段必须有规则校验或人审。

### 轻量后台 vs 核心 OCR

| 场景 | 默认建议 | 说明 |
|---|---|---|
| OCR 只是后台基础能力 | Tesseract 或 LangChain/Unstructured 类 document loader 的 OCR 集成 | 适合低频、低并发、只抽基础文本；更容易部署到 2C2G/2C4G |
| 低配服务器（2C2G/2C4G） | 轻量 OCR + 异步 job + 队列限流 | 不把 OCR 放在 request path；必要时把图片预处理降级 |
| OCR 是核心能力 | PaddleOCR / PPStructure | 适合中文、表格、版面、bbox、质量要求高的项目 |
| 必须版面恢复 | PaddleOCR + layout/table pipeline | 需要保留 blocks、bbox、table structure 和人工复核 |
| 准确率要求极高 | PaddleOCR / 云 OCR + 人审 + 字段级评估 | 引擎选择必须通过样本集 benchmark，不凭默认偏好 |

### 技术选型默认

| 子问题 | 默认选择 | 换方案信号 |
|---|---|---|
| PDF 转图 | pypdfium2 / pymupdf | 系统依赖固定且已有 poppler 时可用 pdf2image |
| OCR | 基础能力/低配后台用 Tesseract 或轻量 document loader OCR；核心能力用 PaddleOCR | 需要高准确率、中文复杂版面、表格、版面恢复时升级 PaddleOCR；云 OCR 在合规允许且质量明显更高时使用 |
| 表格/版面 | PPStructure / layout parser | 版面极复杂时引入专门 document AI 服务 |
| 字段抽取 | 规则 + LLM structured output + Pydantic 校验 | 字段强规则时优先正则/解析器 |
| 差异对比 | 行级/块级对齐 + 可视化框选 | 法务/审计场景必须留 before/after 证据 |

### 最小切片

1. 选 5 份代表性文档，建立 fixture。
2. 跑出 page image + OCR line/block JSON。
3. 抽取 P0 字段并通过 schema 校验。
4. 输出一份可读报告：字段值、置信度、来源页/框、错误列表。
5. 人工修正结果能回写或单独保存 review record。

### Design Doc 必写

- 文档类型、页数范围、语言、扫描质量假设。
- 输出 schema 与字段验收标准。
- OCR、layout、LLM 的职责边界。
- 部署规格、并发、任务耗时预算，以及是否允许 PaddleOCR 这类重依赖。
- 置信度阈值和人审规则。
- 原件、图片、OCR 中间结果、最终结果的存储和保留策略。

### 验证门禁

- 每类文档至少 3 个真实样本。
- 对关键字段计算字段级准确率，不只看整体“看起来对”。
- 可视化证据能定位到页码和 bbox。
- OCR/LLM 失败时不会静默产出“成功”结果。

---

## C. 视觉 / 多媒体质检

典型来源：鞋类设计图相似度、安全帽/车道线/目标检测、WebAgent 截图质检、图片/视频标注、JSON + 媒体资源 QC。

### 第一原则

- **标注 schema 是真相源**：框、点、mask、标签、时间戳、资源 ID 必须结构化。
- **媒体文件不直接进 repo**：repo 保存 fixtures 或小样本，主数据在对象存储/用户目录。
- **模型输出只是候选**：质检产品必须有人工确认、回滚、快照或审计。

### 技术选型默认

| 子问题 | 默认选择 |
|---|---|
| 标注 UI | canvas/fabric.js 或专用标注组件 |
| 流程/JSON 可视化 | ReactFlow + 结构化表单双视图 |
| 图像预处理 | OpenCV |
| 目标检测/分割 | YOLO/SAM/专用模型，先离线评估 |
| 视频帧 | ffmpeg / browser capture，明确时间戳与帧 ID |

### 最小切片

1. 载入一组资源，建立 resourceId -> fileUrl 映射。
2. 能创建/编辑/删除一种标注类型。
3. 标注结果可导出为 schema。
4. 快照或版本记录能回滚。
5. 对一条 QC 任务显示状态、失败原因、结果定位。

### 验证门禁

- 大图、缺失资源、错误 MIME、跨域资源、视频截帧失败都有错误态。
- 标注坐标归一化和显示坐标双向一致。
- 资源路径、上传缓存、导出文件不会污染 repo。

---

## D. 数据治理 / 分析报表

典型来源：ERP 数据孤岛、经营参谋/数据银行、自然语言报表、ESG 数据采集、企业/监管数据分析。

### 第一原则

- **中国电商先拆平台与源类型**：淘宝系 / 京东 / 拼多多 / 抖音；公域数据 / 商家后台 / 客户自有系统。平台与源类型未定，不进入指标和 dashboard 设计。
- **OLTP 与分析分开**：业务库承载事务，报表/分析用只读副本、数仓或物化表。
- **来源系统不是自动真相源**：明确 source priority、冲突规则和更新频率。
- **指标先定义再做页面**：每个指标要有口径、过滤条件、更新时间、owner。

### 最小切片

1. 单来源 ingestion。
2. 标准化表 + 数据字典。
3. 一个指标口径落地。
4. 一个报表或 API 可查询。
5. 数据新鲜度和失败状态可见。

### Design Doc 必写

- 来源系统清单、字段映射、冲突处理。
- 数据层次：raw / staging / mart / dashboard。
- 指标口径和 owner。
- 增量同步、重跑、补数策略。

---

## E. LLM 生产链路

典型来源：话术生成、对话分类、合同解析、需求到表结构、Agent 调 API、报告生成、prompt 多版本。

### 第一原则

- **Prompt 是工程资产**：需要 ID、版本、默认指针、回滚路径、测试样例。
- **Trace 是排障入口**：每次调用至少记录 provider/model/prompt_version/input_hash/token/latency/error。
- **结构化输出优先**：关键业务结果走 JSON schema / Pydantic 校验，失败可重试。
- **Eval 先于规模化**：没有失败用例库，不做大范围 prompt/model 替换。

### 默认结构

```text
prompts/
└── <task_name>/
    ├── manifest.yaml        # default_version, aliases
    ├── vYYYY_MM_DD.yaml     # system/user template/schema
    └── eval_cases.jsonl
```

### 最小切片

1. 一个任务的 prompt registry。
2. 调用时可指定 `current` / `original` / explicit version。
3. 输出通过 schema 校验。
4. 失败样例进入 eval cases。
5. 能回放一次历史调用。

### 验证门禁

- prompt 切换不改业务代码。
- 线上默认版本可回滚。
- trace 能定位到最终 prompt 文本或 prompt hash。
- timeout、first chunk、chunk idle、total timeout 的语义清楚。

---

## F. 浏览器自动化 / WebAgent 数据

典型来源：GEO 可发现性分析、网站截图/DOM 分析、WebAgent 轨迹、网页任务数据质检。

### 第一原则

- **浏览器状态可复现**：viewport、device scale、cookie、headers、user agent、时间戳必须记录。
- **截图/DOM/网络证据分开存**：不要只留截图。
- **页面变化是常态**：selector、布局、滚动高度、懒加载都要有失败探测。

### 最小切片

1. 单 URL 可抓取 robots/llms/sitemap 基础信息。
2. 能渲染截图 + DOM + metadata。
3. 能生成页面摘要或结构评分。
4. 输出 report JSON。
5. 对不可访问、超时、重定向、反爬做状态区分。

### 验证门禁

- 同一 URL 重跑结果可解释。
- 长页面截图和懒加载有测试。
- 临时截图目录已 ignore。

---

## G. POC / Spike 轻量模式

POC 用于验证“技术可行性或业务价值假设”，不默认进入完整治理骨架。

### 适用条件

- 生命周期预计 < 1 周。
- 单人开发或一次性客户演示。
- 不进生产、不接真实敏感数据。
- 目标是回答一个明确问题，而不是建立长期系统。

### 最小文件

```text
README.md              # POC 问题、运行方式、结论位置
.gitignore             # output/runtime/data/secret 全 ignore
requirements.txt / pyproject.toml / package.json
docs/spike-note.md     # 假设、方案、样本、结论、是否升级
```

### 升级触发

任一条件命中，必须从 POC 升级到正式项目流程：

- 要给第二个开发者接手。
- 要接入真实客户数据或生产账号。
- 要持续运行超过 1 周。
- 要作为后续产品或交付项目基础。
- 要新增存储、权限、公共 API 或后台任务。

### POC 收尾

- 结论：可行 / 不可行 / 需二次验证。
- 证据：样本、指标、截图、失败案例。
- 下一步：废弃、归档、升级为正式项目。

---

## 场景化输出补充

如果用户问“下一步做什么”，仍使用 `SKILL.md` 的 工程路由模板。场景信息写在 `工程路由`、`项目形态` 或 `缺失内容` 中，例如：

```text
工程路由: Scenario | OCR / 文档智能 | Architecture
项目形态: Python Agent/CLI（场景：OCR / 文档智能）
缺失内容: 输出 schema、样本 fixture、置信度阈值、人审规则
```

如果用户问“技术选型”，输出时必须同时给：

- 默认推荐。
- 不推荐的反例。
- 退出成本。
- 最小验证方式。
