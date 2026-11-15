# 来源地图与核验边界

> 本文件保留原文 100 项索引、九类映射与独立核验边界。
> 本技能已改为审计优先的界面评判；规则目录见 [rules.md](ui-ux-rules.md)。此处来源组织未改写为新规范。


核验日期：2026-11-14。

起点是 Eian 的文章 [《100 个提升审美的设计网站大赏》](https://x.com/EianLu/status/2121219503988113557?s=46)。已在浏览器读到全文，并核对原文全部 100 项的名称、编号和链接。本文是资源索引及方法归纳，不转载原文。

## 1. 如何读这份地图

- **原文事实**：九类名称、数量、资源收录关系和文章提出的练习方法。已核对全文。
- **原站核验**：仅对下文“独立核验”列表中的具体页面读取了当前内容。不能据此声称测试了该网站的全部产品、付费内容或交互。
- **我们的衍生规则**：为了页面优化而建立的选择顺序、任务类型、检查点和验收方式。这些是本 skill 的综合方法，不是 Eian 或任何资源作者的原话。
- **资源索引**：100 项中的“用于”是简短用途归纳。链接保留文章列出的地址，未逐站验证可用性、跳转、价格、功能数量或商业授权。

## 2. 原文九类如何转化为页面优化决策

类别、数量属于原文；适用决策、产出及边界是我们的衍生映射。

| 原文类别 | 数量与编号 | 页面优化时何时使用 | 应提取的决策或产出 | 不应据此推断 |
|---|---|---|---|---|
| 大赛与奖项 | 12；1–12 | 品牌表达缺少方向，或需要建立视觉质量基准 | 版式、视觉叙事、交互创意的候选方向 | 获奖、评委喜爱等于更高转化率或更好任务完成率 |
| 动态设计与视频 | 14；13–26 | 产品演示、首屏影片、转场或节奏需要优化 | 起承转合、重点停留、运动方向、时序与视觉连续性 | 影视节奏可不加调整地用于高频软件操作 |
| 3D 与渲染 | 9；27–35 | 产品需要材质、空间、三维模型或英雄视觉 | 视觉对象、照明、材质、视角、静态替代方案 | 使用 WebGL/3D 必然提升体验，或素材一定可商用 |
| 电影画面与镜头参考 | 7；36–42 | 图片、视频和滚动叙事缺少构图与焦点 | 主体、景别、视线方向、色温、前后景与取景规则 | 电影截图可直接当生产素材，或电影感等于可读性 |
| UI 设计 | 16；43–58 | 设计产品流程、表单、后台、导航、状态和反馈 | 真实任务路径、组件选择、信息层级、完整状态与恢复路径 | 展示截图证明用户体验有效，或心理学定律可替代测试 |
| 网页灵感 | 10；59–68 | 首页、定价页、活动页、作品集需要结构方向 | 同类站点的内容顺序、区块职责、差异化策略 | 不同业务的页面外观可以整套照搬 |
| 前端与交互 | 16；69–84 | 已确定交互目的，需要实现与打磨 | 最小实现、运动逻辑、输入响应、性能与可访问性策略 | 演示能运行等于生产可靠；示例代码可不查许可直接使用 |
| 字体与配色 | 10；85–94 | 页面缺乏秩序、品牌辨识或跨屏一致性 | 字体角色、字号/间距尺度、颜色语义、状态与主题映射 | 某种字体、配色或比例是通用标准，或色卡本身保证对比度 |
| 日常收集灵感 | 6；95–100 | 长期积累参考和复盘设计 | 带适用条件、来源和解释的参考库 | 收藏数量等于设计能力，或流行度等于设计有效性 |

## 3. 文章自己的练习法

以下是对文章末尾的简要概括：固定少量时间专注一个资源；说明一个具体设计优点；拆解并仿做；积累能准确描述设计的词汇。文章也强调参考真实上线的产品，并优先把字体、配色与交互细节说清楚。

## 4. 我们把练习法转成 skill 的方式

本节是综合推导，不是原文逐条规范。

1. **带着问题找参考**：先定义页面用户、主要任务和约束，再挑相似业务、设备、复杂度的少量参考。
2. **把喜欢转成可验证假设**：记录“观察到了什么 → 为什么可能有用 → 对当前页面是否适用 → 如何验证”，避免只记录“高级”“现代”。
3. **提取机制，不照搬品牌**：可提取层级、间距关系、内容顺序和反馈模式；不能直接挪用品牌资产、受限字体或无授权素材。
4. **建立可复用约束**：把已经确认的选择转成设计 token、组件状态、内容规则和验收条件，不把整个参考站生硬变成模板。
5. **用实现检验理解**：先完成一个关键组件或流程的小样，比较前后，再扩展到其他页面。
6. **区分视觉质量和使用效果**：好看只能说明表达更清楚或风格更一致的可能性；任务成功率、错误率、耗时和转化需要独立验证。
7. **生产规范优先**：品牌指南、现有设计系统、平台规范、可访问性要求和真实用户数据优先于灵感库和个人偏好。
8. **参数有适用条件**：字号、目标大小、动画时间、断点和密度应注明单位、平台和场景；建议起点不能写成所有项目必须照抄的定律。

## 5. 独立核验的重点页面

以下内容除原文收录外，还直接读取了对应原站。

### Vercel：界面实施与验收

[Web Interface Guidelines](https://vercel.com/design/guidelines)。核验了键盘和焦点、点击热区、加载与错误反馈、URL 状态、手势替代、布局、动画及完整状态等条目。适合转换成实现验收清单，而非视觉风格模板。其移动输入字号、动效时间等建议应保留场景条件；尤其不能采用禁止用户缩放的做法。

### Radix：颜色角色与状态

[Understanding the scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)。原站将 12 级色阶分配给背景、组件状态、边框、实色填充和文字等职责。已实际查看页面和状态色示例。用于建立语义颜色系统；对比度结论只在原站指定组合及条件内成立，不能推广成所有叠加、透明度与背景都自动合格。

### Emil Kowalski：动效目的与控制

[Great Animations](https://emilkowal.ski/ui/great-animations)。读取了目的、节奏、性能、可中断性和减弱动态效果等章节。实际操作了卡片展开及 Escape 收回。作者通常建议交互动画短于 300ms，这是情境性建议，不是统一强制值。部分嵌入视频显示无法播放，没有验证全部视频和帧率，也没有做性能测量。

### Rauno Freiberg：意图和容错

[Invisible Details of Interaction Design](https://rauno.me/craft/interaction-design)。读取了手势隐喻、物理连续性、触发时机和意图表达的讨论。作者明确将文章定位为观察与反思，而非规范集合。可用于设计“何时触发、何时提交、是否可以反悔”的问题框架。

### Utopia：响应式尺度

[Fluid Responsive Design](https://utopia.fyi/)。核验了为小屏与大屏定义字号、间距尺度并由视口插值的思路。适合整理响应式 token。它不是无需布局断点的承诺；导航、表格、列数与内容重排仍需按内容决定。

### Butterick：正文排版

[Typography in ten minutes](https://practicaltypography.com/typography-in-ten-minutes.html)。核验了优先处理正文、字号、行距、行长及字体选择的建议。文中的字符数和行距示例主要服务其文字排版语境，不应机械套用到中文、混排、数据表格和小尺寸控件。正文可读性比只换展示字体更值得优先检查。

### Mobbin：真实产品参考

[Mobbin 官网](https://mobbin.com/)。官网目前列出 Screens、Flows、Animations、UI Elements。原文把它与 Page Flows 简化成“静态截图对录屏”，这个二分不适合写入 skill；应按实际可访问内容选择。未登录、未购买，也未核验完整付费流程库。

### Impeccable：从笼统审美反馈转向具体诊断

[Impeccable](https://impeccable.style/)。官网展示了层级、文案、表单和装饰处理的前后对照，并将工具定位为帮助代理遵守设计系统、从头构建或改善界面。适合借鉴“诊断具体问题再选择动作”的思路；未安装或测试其工具。不要把示例中批评的某种颜色、衬线字或卡片样式转成全局禁令。

### The Component Gallery：按职责比较组件

[The Component Gallery](https://component.gallery/)。官网按组件类型和设计系统组织例子，提供各系统的代码、使用指南与可访问性等来源入口。用于比较组件职责、状态和交互约定；收录不等于每项都经过可访问性认证。实际采用时回到原设计系统规范。

### awesome-design-md：第三方设计分析

[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)。仓库明确把自身描述为从网站提取、分析设计模式、token 和规则的 DESIGN.md 集合。它不是所涉品牌发布的官方设计规范。可借鉴文档结构，把参考改写为自己项目的约束；不能假设放入根目录就被所有工具自动加载，更不能把品牌相似度当成正确性证明。未安装、运行或批量导入仓库。

### Refero Styles：可读设计参考

[Refero Styles](https://styles.refero.design/)。公开页列有颜色、字体、间距、组件及 DESIGN.md 参考。与上一项一样，这属于第三方整理的可读资料，不是各品牌官方授权的规则或素材许可。适合比较和提取模式，不应以替换现有设计系统为默认动作。未核验整个图库及导出功能。

## 6. 核验限制与不应固化的内容

- 原文所有 100 项均完成“确实收录及链接是什么”的核对，不等于 100 个站点均已实测。
- Page Flows 的直接网页抓取返回 403；未把这次抓取失败说成网站失效，也未核验其付费内容。
- 文章中的资源数量、收费状态、免费范围、重命名、作者任职、插件许可与素材许可可能变化。使用时查相应原站，不写成永久事实。
- 原文的“最强”“最好”“没有一帧卡顿”等表达属于作者评价，不能转写成测量结果。
- “反 AI 味”应作为识别无目的装饰和同质化的检查方向，不能把某种颜色、字体、卡片布局一概列为禁用。
- 本地图的网页优化映射是综合方法，不代表这篇资源导航本身包含全部可访问性、性能、用户研究或工程规范。

## 7. 原文全部资源索引

索引的编号、名称及 URL 已核对原文。每项的简短用途是我们的归纳；独立原站核验范围以上节为准。

### 大赛与奖项

1. [Pwnisher 3D 渲染挑战赛](https://www.youtube.com/@pwnisher)：比较相同约束下的视觉创意。
2. [Awwwards](https://www.awwwards.com/)：网页创意与表现参考。
3. [CSS Design Awards](https://www.cssdesignawards.com/)：网页设计多维评审参考。
4. [The FWA](https://thefwa.com/)：实验性交互与数字体验参考。
5. [The Motion Awards](https://motionawards.com/)：动态作品参考。
6. [Apple Design Awards](https://developer.apple.com/design/awards/)：平台应用体验与获奖评语。
7. [D&AD](https://www.dandad.org/)：品牌与广告创意参考。
8. [The One Show & ADC](https://www.oneclub.org/)：广告创意与视觉工艺参考。
9. [Runway AI Film Festival](https://aif.runwayml.com/)：AI影像叙事参考。
10. [Tokyo TDC](https://tokyotypedirectorsclub.org/)：字体与实验视觉参考。
11. [Annecy 安纳西国际动画节](https://www.annecyfestival.com/)：动画美术与叙事参考。
12. [Ciclope Festival](https://www.ciclopefestival.com/)：分工种研究影视工艺。

### 动态设计与视频

13. [Motionographer](https://motionographer.com/)：动态项目与制作思路。
14. [STASH](https://www.stashmedia.tv/)：商业动效案例与幕后。
15. [Art of the Title](https://www.artofthetitle.com/)：片头排版与视觉叙事。
16. [Vimeo Staff Picks](https://vimeo.com/channels/staffpicks)：短片节奏与表现。
17. [Behance 动态设计专区](https://www.behance.net/galleries/motion)：风格帧到成片的过程。
18. [Short of the Week](https://www.shortoftheweek.com/)：短篇故事结构。
19. [Directors Notes](https://directorsnotes.com/)：制作条件与创作取舍。
20. [Sakugabooru](https://www.sakugabooru.com/)：动作时序与表现力。
21. [Promonews](https://www.promonews.tv/)：MV视觉与剪辑节奏。
22. [BUCK](https://buck.co/)：多媒介品牌动效。
23. [ManvsMachine](https://mvsm.com/)：产品材质与三维视觉。
24. [Oddfellows](https://oddfellows.tv/)：插画、角色与转场。
25. [Golden Wolf](https://www.goldenwolf.tv/)：高能量视觉节奏。
26. [Ordinary Folk](https://www.ordinaryfolk.co/)：几何图形与运动曲线。

### 3D 与渲染

27. [ArtStation](https://www.artstation.com/)：概念美术与三维参考。
28. [The Rookies](https://www.therookies.co/)：新锐作品与技能基准。
29. [80 Level](https://80.lv/)：场景制作拆解。
30. [Sketchfab](https://sketchfab.com/)：可旋转模型与结构研究。
31. [befores & afters](https://beforesandafters.com/)：视效前后对照。
32. [fxguide](https://www.fxguide.com/)：渲染与制作技术。
33. [Blender Studio](https://studio.blender.org/)：工程资产与制作流程。
34. [Poly Haven](https://polyhaven.com/)：三维场景素材。
35. [Beeple Everydays](https://beeple-crap.com/everydays)：持续练习与风格演变。

### 电影画面与镜头参考

36. [ShotDeck](https://shotdeck.com/)：按镜头特征找参考。
37. [FILMGRAB](https://film-grab.com/)：电影构图与色彩。
38. [StillsLab](https://stillslab.com/)：影视画面检索。
39. [Flim](https://flim.ai/)：语义检索影视画面。
40. [EyeCannndy](https://eyecannndy.com/)：镜头与转场术语。
41. [StudioBinder 镜头语言指南](https://www.studiobinder.com/blog/ultimate-guide-to-camera-shots/)：镜头语言系统学习。
42. [American Cinematographer](https://theasc.com/)：摄影决策与用光思路。

### UI 设计

43. [Mobbin](https://mobbin.com/)：真实产品屏幕、流程和动画参考。
44. [Page Flows](https://pageflows.com/)：端到端操作流程参考。
45. [Refero](https://refero.design/)：按页面和组件类型找参考。
46. [Nicelydone](https://nicelydone.club/)：SaaS后台与复杂界面。
47. [SaaSFrame](https://www.saasframe.io/)：SaaS官网及产品页面参考。
48. [Figma Community](https://www.figma.com/community)：研究组件、变量与自动布局。
49. [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)：苹果平台组件及交互规范。
50. [Material Design 3](https://m3.material.io/)：设计系统结构与状态规则。
51. [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines)：界面实施与验收检查。
52. [Impeccable](https://impeccable.style/)：AI界面诊断及设计打磨。
53. [The Component Gallery](https://component.gallery/)：比较不同设计系统的同类组件。
54. [60fps](https://60fps.design/)：真实产品动效片段。
55. [Spotted in Prod](https://www.spottedinprod.com/)：已上线产品的微交互。
56. [Growth.Design](https://growth.design/)：用户旅程案例拆解。
57. [Laws of UX](https://lawsofux.com/)：交互心理学启发式。
58. [Game UI Database](https://www.gameuidatabase.com/)：高密度信息与游戏界面。

### 网页灵感

59. [Recent（原 Godly）](https://recent.design/)：网页及品牌视觉灵感。
60. [Siteinspire](https://www.siteinspire.com/)：按行业与风格匹配页面。
61. [Land-book](https://land-book.com/)：商业页面版式参考。
62. [Landingfolio](https://www.landingfolio.com/)：按页面区块选参考。
63. [awesome-design-md](https://github.com/VoltAgent/awesome-design-md)：把参考转为机器可读设计约束。
64. [One Page Love](https://onepagelove.com/)：单页叙事节奏。
65. [Minimal Gallery](https://minimal.gallery/)：留白与极简层级。
66. [Dark Mode Design](https://www.darkmodedesign.com/)：深色界面视觉层级。
67. [Hoverstat.es](https://www.hoverstat.es/)：实验性视觉与交互探索。
68. [Web Design Museum](https://www.webdesignmuseum.org/)：历史风格与网页演变。

### 前端与交互

69. [Codrops](https://tympanus.net/codrops/)：创意前端实现与示例。
70. [CodePen Spark](https://codepen.io/spark)：小型交互实验与代码研究。
71. [GSAP 官方 Demo 库](https://demos.gsap.com/)：动画实现模式。
72. [Three.js 官方示例](https://threejs.org/examples/)：Web 3D技术示例。
73. [Shadertoy](https://www.shadertoy.com/)：着色器视觉实验。
74. [The Book of Shaders](https://thebookofshaders.com/)：着色器基础与互动教学。
75. [Bruno Simon](https://bruno-simon.com/)：空间化作品集体验。
76. [Lusion](https://lusion.co/)：沉浸式网页表现。
77. [Active Theory](https://activetheory.net/)：品牌数字互动体验。
78. [Framer Gallery](https://www.framer.com/gallery/)：响应式商业网站参考。
79. [Motion 官方示例](https://motion.dev/examples)：常见UI动效实现。
80. [React Bits](https://reactbits.dev/)：可配置动画组件。
81. [coss ui](https://coss.com/ui)：产品型基础组件和模块。
82. [Josh W. Comeau](https://www.joshwcomeau.com/)：布局与动画原理。
83. [Rauno Freiberg](https://rauno.me/)：意图、手势和容错细节。
84. [Emil Kowalski](https://emilkowal.ski/)：动效目的、节奏与可中断性。

### 字体与配色

85. [Typewolf](https://www.typewolf.com/)：字体搭配和实站案例。
86. [Fonts In Use](https://fontsinuse.com/)：字体的真实应用。
87. [Google Fonts](https://fonts.google.com/)：字体选择及语言覆盖。
88. [Fontshare](https://www.fontshare.com/)：字体选择与搭配。
89. [Butterick's Practical Typography](https://practicaltypography.com/)：正文排版基本功。
90. [Utopia](https://utopia.fyi/)：流式字号与间距系统。
91. [Coolors](https://coolors.co/)：配色探索。
92. [Realtime Colors](https://www.realtimecolors.com/)：在界面中预览颜色角色。
93. [Radix Colors](https://www.radix-ui.com/colors)：语义化色阶与组件状态。
94. [tweakcn](https://tweakcn.com/)：组件主题可视化调校。

### 日常收集灵感

95. [Pinterest](https://www.pinterest.com/)：主题视觉收集。
96. [Are.na](https://www.are.na/)：研究资料关联与归档。
97. [Cosmos](https://www.cosmos.so/)：创意参考收集。
98. [Savee](https://savee.com/)：视觉参考浏览与收藏。
99. [It's Nice That](https://www.itsnicethat.com/)：创意项目背景和思路。
100. [Brand New](https://www.underconsideration.com/brandnew/)：品牌改版对比。

