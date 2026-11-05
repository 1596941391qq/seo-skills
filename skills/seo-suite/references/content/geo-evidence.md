# GEO 的证据基础与实施边界

> 建立于 2026-08-29；一手来源全量复核于 **2026-10-21**（上一轮 2026-10-18；2026-11-05 加「GEO 手法风险线」，复核于 2026-11-05）：官方页面、论文和第三方研究都重新打开读过原句。
> 本文件是本套件 GEO 结论的**仲裁**：其他参考文件里的数字、阈值或「AI 偏好」说法与本文件冲突时，以本文件为准。
> 目标是让真实内容更容易被发现、理解和核实；不把 HTML 形状、Schema、域名后缀或自发转载包装成 AI 排名公式。
> 数字、论文与第三方研究的样本和局限见 [geo-evidence-bank.md](geo-evidence-bank.md)。

## 一、先区分证据范围

| 证据类型 | 能支持什么 | 不能支持什么 |
|---|---|---|
| 产品官方说明 | 该产品的公开规则 | 其他引擎的内部算法 |
| 论文/可复现实验 | 实验设定内的结论；要写明模型、任务、数据、时间、指标、对照 | 某个站点的收益承诺 |
| 观察/相关研究 | 现象和方向 | 因果权重 |
| 厂商/营销转述 | 「有人报告了这个结果」 | 实施验收和预算收益 |

### 官方事实（核对 2026-10-21）

- **Google AI 功能**（[AI features](https://developers.google.com/search/docs/appearance/ai-features)）：页面要作为 AI Overviews / AI Mode 的链接出现，只需已被索引、且可以带摘要展示；没有额外技术要求。控制入口是 Googlebot 的 robots.txt，以及 `nosnippet`、`data-nosnippet`、`max-snippet`、`noindex`。这些流量计入 Search Console 效果报告的「网页」类型。
- **Google 生成式 AI 优化指南**（[ai-optimization-guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)，2026-05-15 发布，2026-07-10 更新）：Google Search 不使用 llms.txt、AI 文本文件或特殊标记；不要求切块；没有理想页长；不需要为 AI 改写；追逐不真实的提及作用有限；结构化数据不是必需项，也没有专用 schema。为每个 fan-out 变体批量建页、以操纵排名或 AI 回答，违反规模化内容滥用政策。站点还必须在 Search Console 中处于「纳入生成式 AI 功能」状态。
- **Google 政策**：2026-05-15 起，垃圾内容政策明确适用于生成式 AI 回答；2026-06-15 起，指南补充 llms.txt 不会正面或负面影响 Google 可见性（[文档更新记录](https://developers.google.com/search/updates)）。
- **Search Console**：[Search generative AI 控制](https://support.google.com/webmasters/answer/16908024)（全球开放日期见[事实表](../overview/facts.md#gsc-genai)，路径「设置 → Search generative AI」）可纳入或排除 AI Overviews、AI Mode 和 Discover 的生成式功能。排除通常 1–2 天生效。它不管训练；训练控制用 Google-Extended。[生成式 AI 效果报告](https://support.google.com/webmasters/answer/16984139)（先对部分站点开放，后对全球开放，[日期](../overview/facts.md#gsc-genai)）只有展示次数，维度是页面、国家、日期、设备；这些数据同时计入总体效果报告，AI 功能带来的点击仍拆不出来。
- **Bing / Copilot**（[Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)）：Bing 与 Copilot 共用抓取、索引、排名基础。指南原话：GEO「does not guarantee grounding or citations」。`NOARCHIVE` 让内容不进 Copilot 回答和 grounding；`NOCACHE` 只允许使用网址、标题和摘要。结构化数据不保证可见性。面向语言模型的 prompt injection 会被降权或移除。
- **第三方工具**（[Google 指南](https://developers.google.com/search/docs/fundamentals/third-party-seo)，2026-06-05）：第三方工具拿不到 Google 内部排名数据；Google 不评估第三方服务；用工具不保证排名。本套件的评分器一律标注为「启发式」。
- **内容自查**：Google [有用内容指南](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) 用「Who / How / Why」自查：署名能否链到作者背景；AI 辅助过程是否该披露；内容是否为人而写。指南明确：Google 没有偏好的字数（原文「No, we don't.」）；自查问题里把「改页面日期装作新鲜」列为不该做的事。

**用法**：官方说明只约束该产品。Google 的结论不外推到 ChatGPT、Perplexity 或中文引擎。

## 一·补 GEO 手法风险线（核对 2026-11-05）

Google 2026-05-15 起写明：垃圾内容政策适用于 Google 搜索里的生成式 AI 回答，政策对 spam 的定义包括「试图操纵 Google 搜索里的生成式 AI 回答」（[spam policies](https://developers.google.com/search/docs/essentials/spam-policies)）；2026-04 起垃圾举报可能直接触发人工操作（[举报页](https://developers.google.com/search/help/report-quality-issues)）。所以 GEO 手法要按「会不会被当成操纵」分线。下表的「依据」列是官方原文，「线」是本套件口径。

| 手法 | 线 | 依据 |
|---|---|---|
| 把真实问题的答案写清楚、标题对齐用户问法、事实和定义写明 | 安全 | Google 指南、Bing 指南（本节上文） |
| 页面上真实可见的内容配结构化数据 | 安全 | 结构化数据标看不见的内容是人工操作类型之一（[penalty-recovery](../monitoring/penalty-recovery.md) 1.2 第 3 条） |
| 为每个 fan-out 查询变体批量建页 | **越线** | 指南写明违反规模化内容滥用政策（本节上文「生成式 AI 优化指南」） |
| 页面里给模型藏指令（白字、`display:none`、注释里的 prompt injection） | **越线** | 隐藏文本是垃圾政策条目；Bing 指南：面向语言模型的 prompt injection 会被降权或移除；论文实验见 [geo-evidence-bank](geo-evidence-bank.md)「对抗与安全」 |
| 给用户和爬虫（含 AI 爬虫）看不同内容 | **越线** | cloaking 是垃圾政策条目 |
| 买评价、未披露的激励评价、刷第三方平台提及 | **越线** | 评价摘要指南 2026-07-24 新增：不许虚假或未披露激励的评价（[review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)）；Google 优化指南：追逐不真实的提及作用有限 |
| 在别人的高权重站发「榜单」「推荐」软文借排名 | **越线**（EEA 内处理方式不同） | 站点声誉政策（[penalty-recovery](../monitoring/penalty-recovery.md) 1.3） |
| 自家站写「最佳 X」对比页并把自己排第一 | 灰（看内容是否真比较、是否披露利益关系） | 无专门条文；按有用内容自查「为人而写」判断（本套件口径） |

外包的 GEO 服务做了越线手法，后果落在你的站上。Google 不评估第三方服务，自称「Google 认可」的要警惕（[third-party-seo](https://developers.google.com/search/docs/fundamentals/third-party-seo)）。

## 二、四条流行建议的取舍

### 1. 每段必须变成问题—答案并用 section/div 包裹？

**采用可读性，不采用强制格式或优先抽取保证。** 用户真在问「怎么设置」「这个值是什么意思」时，用清楚的问题标题、紧邻答案、稳定锚点。说明要交代对象、适用范围、条件与例外。定义列表、步骤、代码和真实比较表各有用途，不把每段都塞进 FAQ。

Google 指南不要求切块；它建议语义 HTML 的理由是帮助读者和读屏器。Bing 指南要求事实和定义写明、关键陈述不依赖隐含内容、关键信息靠前。这是 Bing/Copilot 的官方写法依据，不是排名公式。
**证据：两家官方指导 + 工程判断；引用是否提升要另测。**

### 2. FAQ Schema 铺满页面、放 head 就会优先引用？

**不采用。** 有真实 FAQ 时，可保留一份与可见正文一致的声明。不扩成隐藏答案库，不把参数、促销语或段落标成 Question。schema.org 词汇存在，不等于搜索产品支持。

- FAQ 富结果已不再展示，文档已下线（[日期与来源](../overview/facts.md#rich-results)）。旧的「仅医疗/政府站可展示」已不是现行规则。
- [FAQPage 词汇](https://schema.org/FAQPage)仍可描述真实问答；它不带来 AI 优先读取资格。
- [JSON-LD 说明](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)：script 可放 head 或 body；Google 也能读 JS 注入的 JSON-LD。不渲染 JS 的爬虫只读初始 HTML。位置不是权重开关。
- 生产引用研究三条，设计不同，结论同向（明细见 [geo-evidence-bank.md](geo-evidence-bank.md) 第七节第 1 条与第八节）：
  - arXiv 2609.35077：约 200 万条引用、B2B SaaS、四引擎、观察性。按域名控制后，Schema 无显著独立效应；可见 FAQ 段 β=+0.07，作者称效应很小。
  - Ahrefs（2026-05）：1,885 个新加 JSON-LD 的页面对比约 4,000 个对照页，双重差分。AI Mode +2.4%、ChatGPT +2.2%，都不显著；AIO −4.6%，两组加标记前已同步下滑。
  - SSRN 6284518：按查询聚类后，Schema 有无不显著；唯一例外是填了价格、评分、规格的 Product/Review Schema（小样本）。
- 实时抓取阶段：searchVIU 2025-10-30 测试 5 个 AI 系统，没有一个读出只存在于 JSON-LD 里的价格。关键事实必须写在可见正文里。
- 验收：渲染出的问答与 JSON-LD 逐条对应；无重复、无虚构评分、无不可见的独家答案。用 Schema Markup Validator 查词汇合法性，用当前搜索文档查支持范围；解析成功不等于有富结果资格。

**证据：一手产品文档 + 三条生产研究，2026-10-21 复核。** 「Schema 抽取 16%→54%」之类数字只有二手转述，没有一手方法，不作通用实证。

### 3. .edu/.org 高 30%，.co/.io/.tech/.expert 更受 AI 青睐？

**不作为选域或迁站依据。** 这组固定增益找不到一手实验、引擎、样本与对照。某类站点常被引用，不能排除内容、机构信誉与历史积累等混杂因素。

Google [关于新顶级域名的说明](https://developers.google.com/search/blog/2015/07/googles-handling-of-new-top-level)（2015-07-21）：新通用 TLD 与 .com/.org 同样处理，后缀里的关键词不带来优势。这是 2015 年的 Google 声明，不覆盖所有 AI 引擎。国家/地区域名的地理定位信号与「权威加权」不是一回事。
**证据：范围明确的官方说明 + 数字无出处。** 保持现有品牌域名；迁站要有别的业务理由，由站点负责人决定。

### 4. 同一信息在三个独立域名出现，引用权重翻倍？

**不采用固定阈值，不把自发转载当独立验证。** 官网、品牌自己的 LinkedIn/Medium 文章即使域名不同，仍是同一发布者、同一事实来源。真实用户案例、独立测试和行业报道才是不同的证据。

跨渠道发布要服务各自读者，标明作者、时间、原始来源和关联关系；错误事实要同步纠正。Google 指南明确：追逐不真实的提及作用有限。
**证据：Google 官方指导 + 来源独立性的工程判断；「三域名翻倍」无出处。** 对外发布前由站点负责人确认。

## 三、论文能说明什么，不能说明什么

- **GEO 原始论文**（[arXiv 2311.09735](https://arxiv.org/abs/2311.09735)，Aggarwal 等，KDD 2024）：GEO-bench 有 1 万条查询。生成引擎是 gpt-3.5-turbo，输入固定为 Google 前 5 条结果。指标是回答内的可见度（位置加权词数、主观印象），不是检索、排名或流量。最佳方法相对基线分别 +41%、+28%；「引用来源 / 加引语 / 加统计」三种方法在位置加权词数上 +30–40%。原排第 5 的来源用「引用来源」后 +115.1%，排第 1 的来源平均 −30.3%。关键词堆砌几乎无效。在 Perplexity.ai 上复测（200 条测试样本，来源文本以文件上传，不是让它自己搜索），「加引语」+22%。
- **C-SEO Bench**（[arXiv 2506.11097](https://arxiv.org/abs/2506.11097)，Puerto 等，NeurIPS 2025 Datasets & Benchmarks，代码和数据公开）：两类任务（问答、商品推荐）各三个领域，并比较不同采纳率。多数受测内容优化方法基本无效，常常压低排名；提高来源在上下文中排序的传统 SEO 更有效；采纳者越多，总收益越低。
- **批判综述**（[arXiv 2607.14035](https://arxiv.org/abs/2607.14035)，2026-07，单作者预印本，45 篇研究）：原始论文的增益在其设定内成立，但前提是来源已在固定上下文里；它不证明自然可发现性，也不证明持续流量。最可复现的杠杆是主题相关性与上下文位置。已被检索的内容可以因果地改变自己被引用的方式，但没有一项技术显示稳定、纵向、跨平台的因果效应。

这些结果是对泛化增益承诺的警示，**不是「所有 GEO 无效」的证明**。论文结论冲突时，先比较检索/生成阶段、模型、指标、基线和多参与者设置。写清楚能改善读者理解；不要把这一工程价值说成论文证明的排名提升。

## 四、API 文档与多产品参考页的实施要求（本套件口径）

逐产品、逐接口读取实际契约，不批量替换产品名来生成解释。渲染器与自动检查可以复用；**产品事实与术语审查不能用模板代替**。每个展示的参数至少核：

1. 名称、必填/可选、具体对象；不同接口里同名的 keyword / id / url / sort 不假定同义。
2. 输入格式与原生术语；账号名、内部 ID、商品编号、地点标识要分清。
3. 适用接口、默认值、单位、范围、允许值；自由文本不捏造枚举。
4. 参数影响什么、未开放什么；文档与实际行为冲突时先登记。
5. 示例绑定具体产品和接口；格式示例标明不是成功样本；不伪造响应。
6. 返回字段含义及空值边界；不遗漏产品独有能力。

页面用 heading + 紧邻说明、dt/dd、稳定锚点；同页不同接口的同名参数不串链。FAQ 如保留，可见问答与 JSON-LD 从同一份内容生成。新增主题页必须有独立用户价值；低重复率不是垃圾内容政策的安全线。验收分开记录：源码已核 → 生成物同步 → SSR/浏览器可读 → 允许环境中实测 → 上线复核。多语言版本逐语言审校。

## 五、发现与衡量

- 先核访问、索引指令、canonical、内链、正文与字段事实，再讨论 AI 引用。
- llms.txt 可服务确实读它的工具（多为编码 agent）；Google Search 不使用它。不为「AI 加权」默认增加 `.well-known/ai.txt` 或另一份 FAQ JSON，避免多份事实漂移。见 [llms-txt-guide.md](llms-txt-guide.md)。
- 搜索型、训练型、用户触发型爬虫分开定策略（见 [geo-platform-differences.md](geo-platform-differences.md) 第三节）；不为 SEO 擅自放开所有爬虫。
- 官方测量面：Google「生成式 AI 效果报告」（只有展示）；Bing Webmaster Tools「AI Performance」（引用数、被引页面、grounding queries，2026-02 公测）；Yandex Webmaster「Видимость сайта в Алисе AI」（SoV）；Naver「AI 브리핑 인용수」。各家口径不同，不合并。
- 自己的抽样记录查询、语言/地域、产品/模型、时间、是否联网、引用 URL 与原始回答。提到品牌不等于引用；多条搜索链重合不等于多份独立证据。
- 固定问题集与取样协议；区分抓取、索引、展示、引用、点击、转化。用重复观测和对照/分批发布减少混杂。改完本地 HTML 只能叫工程验收。
- 外部监测失败、缺链、旧快照单独标明；一次缺失不等于长期不可见。

## 六、维护规则

每条新增断言登记原始链接、日期、产品范围、证据类型及局限；无方法的百分比不进入实施要求。官方文档变了就地改旧建议，不在尾部追加冲突规则。吸收可核实的方法；不把某个项目的运行快照（数据、截图、内部结论）复制进共享 Skill。

## 七、GEO 检查清单

阈值未注明出处的，都是本套件口径。

| # | 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|---|
| 1 | 检索型爬虫能进站 | `python3 scripts/robots_posture.py https://站点/robots.txt --json`；再用真实 UA 抽测 3 个重点页的状态码 | 通过：search/user 层无 Disallow，`citation_bots_ok` 为真，抽测都是 200。失败：任一检索型爬虫被禁或被 WAF 拦 |
| 2 | Google 资格 | Search Console → 网址检查，看「已编入索引」和抓取到的 HTML | 通过：已索引，关键段落无 `nosnippet`/`data-nosnippet`。失败：未索引或关键段落被屏蔽 |
| 3 | 生成式 AI 控制是有意设置的 | Search Console → 设置 → Search generative AI | 通过：状态与业务决定一致。失败：没人知道当前是纳入还是排除 |
| 4 | Copilot 可用全文 | `curl -sI URL` 与页面 `<meta name="robots">`，查 `noarchive`、`nocache` | 通过：要给 Copilot 用的页面没有这两个指令。失败：有 |
| 5 | 关键事实在初始 HTML 的可见正文里 | `curl -s URL` 后搜价格、规格、定义原句；`python3 scripts/ai_views.py --url URL --json` 看去噪后正文 | 通过：事实出现在可见文本。失败：只在 JSON-LD、图片或 JS 渲染后才出现 |
| 6 | 结构化数据与正文一致 | `python3 scripts/schema_lint.py URL` | 通过：无报错，FAQPage 只标真实问答。失败：悬空 @id、占位符、空答案、为 AI 新增的 FAQPage |
| 7 | llms.txt 不被当成杠杆 | `python3 scripts/llmstxt.py check https://站点` | 通过：没有文件，或文件有效（H1 + 链接）且方案里不写「提升引用」。失败：把它写进 GEO 收益 |
| 8 | 引用基线可复现 | `python3 scripts/citation_panel.py init --brand X --prompts-file 问题库.md --domain 站点`；每个引擎 `record`；`report` | 通过：≥10 个 prompt，每个 prompt ≥3 次采样，报告带 Wilson 区间并标出 unstable。失败：单次采样就下结论 |
| 9 | 真实引荐的下界 | `python3 scripts/ai_referral_log.py access.log --bot-ua --classify` | 通过：检索型爬虫抓取成功率高，AI 引荐按引擎分列。失败：把 App 内无 referrer 的访问算成 0 |
| 10 | 改动效果有对照 | `python3 scripts/split_test.py plan / assign / analyze`；参考 [Ahrefs 自测步骤](https://ahrefs.com/blog/schema-ai-citations/)（5–10 个处理页 + 5–10 个引用水平相近的对照页，改完比较 30 天或更久；样本小，只能当探针，统计功效见 `split_test.py plan`） | 通过：效应 95% CI 不含 0 才说有效；否则报告「未检出」。失败：只有改前改后对比 |
| 11 | 官方测量面已接通 | GSC 生成式 AI 效果报告；Bing Webmaster Tools → AI Performance；Yandex / Naver 对应报告（有该市场时） | 通过：每月记一次，按平台分列。失败：跨平台相加成一个「AI 可见度」 |

## 八、证据保鲜机制与证据治理（本套件口径）

方法来源：[joeseesun/qiaomu-seo](https://github.com/joeseesun/qiaomu-seo) 的 ai-search、knowledge-freshness、performance-measurement 等参考文件，按本套件口径改写。

- **证据阶梯六级**：`eligible`（按平台文档可访问）→ `retrieved`（确实被检索或呈现）→ `cited`（带链接引用）→ `mentioned`（被点名）→ `recommended`（进入推荐短名单）→ `converted`（可测的下游行为）。任何一级都不坍缩成「AI 可见性提升」。
- **知识五类**：稳定原理 / 现行平台规则（必须带来源和复核日期）/ 观察到的市场状态 / 估算值（第三方工具的搜索量、流量、外链、难度，必须带厂商、方法、日期）/ 假设。
- **保鲜**：现行平台规则与市场数字每条带 `review_after_days`；快变事实（AI 产品行为、厂商数字）60 天内重查；过期来源在报告里显式列出。
- **变更验证四里程碑**：已实现（源码与测试）→ 已部署可观测（线上 HTML 已变）→ 平台已处理（抓取、索引、canonical 已反映）→ 结果已观测（合格窗口后的数据）。只有第四步支持效果声明。
- **SEO 实验七要素**：可证伪假设；防交叉污染的处理单元；看结果前定好人群、分配和基线窗；主指标 + 护栏 + 最小实用效应 + 观测窗 + 停止规则；不同时改模板、内链、内容、埋点；监控实现与重抓进度；正、负、零、不定结果都报告。
- 评分器的标定方法（预注册、留出集、重算规则）见 [scoring-calibration.md](../research/scoring-calibration.md)。
