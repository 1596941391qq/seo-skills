# Routing Rules

> 用途:一句话请求 → 走哪个能力集合、先跑哪个脚本。SKILL.md 的「能力路由」表是短版,本文是细则和负例;原 SKILL.md 的「常见请求如何路由」表和各能力集合的参考文件清单在文末附节。第三方仓库的阅读笔记在文末,只当设计参考,不是搜索引擎规则。

## 第零步:先定市场

任何任务先确认目标市场/语言(18 市场清单见 multilingual-workflow.md)。市场决定引擎格局与工具栈(如俄语区→Yandex、韩语区→Naver);未确认市场前,下面的能力路由结论可能整体不适用。

## 入口判断

### 走 research
当问题核心是“找什么机会做”或“为什么 SERP 长这样”。

关键词：
- keyword
- search intent
- SERP
- competitor
- competitor alternatives
- vs pages
- content gap
- topic cluster
- content pillars

### 走 content
当问题核心是“写什么”和“怎么把页面内容写得更能排名/更能被引用”。

关键词：
- article
- landing page copy
- content brief
- title tag
- meta description
- GEO content
- AI citation
- EEAT
- content refresh
- refresh strategy
- content decay

### 走 technical
当问题核心是“站点结构 / 页面结构 / 抓取索引 / schema / 内链 / 性能 / CWV / 实体信号 / programmatic SEO 实现”。

关键词：
- technical SEO
- indexing
- crawl
- robots.txt
- sitemap
- schema
- breadcrumb
- internal linking
- site architecture
- performance
- Core Web Vitals
- entity
- programmatic SEO

### 走 monitoring
当问题核心是“持续追踪、报告、告警、权威度、外链、排名变化”。

关键词：
- rankings
- keyword positions
- backlinks
- report
- alert
- authority
- domain trust
- trend

## 多路由规则

| 用户问题 | 路由 |
|---|---|
| 为什么这个页面 CTR 低 | content + technical |
| 为什么排名掉了 | monitoring + research + technical |
| 给我完整 SEO 审计 | overview + technical + content |
| 做 GEO 方案 | overview + content + technical + monitoring |
| 做竞争对手 SEO 拆解 | research + monitoring |
| 展示多、点击少,改标题和首段 | content(`question_align.py` + [question-alignment.md](../content/question-alignment.md)) |
| 英文文案按 ASD-STE100 检查 | content(`ste_lint.py` + [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md)) |
| 接入 GSC / Bing 数据、配 key | overview(`doctor.py --wizard` + [data-onboarding.md](data-onboarding.md)) |
| 把审计发现变成工单并跟进到关闭 | technical(`envelope.py` → `remediation.py`) |
| 评估要不要进新市场 | overview([intake-checklists.md](intake-checklists.md) 目标市场闸门 → [multilingual-workflow.md](multilingual-workflow.md)) |

## 不应误路由的情况

| 需求 | 不要误判为 |
|---|---|
| XML sitemap / crawl / indexing | 单纯的信息架构设计（它们属于 technical 的抓取与索引检查） |
| 页面 CRO 提升转化 | 必须由本 Skill 处理的 SEO 任务 |
| 纯广告投放文案 | content SEO |
| 纯产品分析埋点 | SEO 监控，除非明确与 SEO 归因相关 |

## 检查清单(路由前 30 秒)

| 检查什么 | 怎么查 | 通过 / 失败判据 |
|---|---|---|
| 市场已定 | 请求里有市场或语言;没有就问,单语言站按站点语言推断 | 有明确市场码(18 个之一)。没有就不往下路由 |
| 数据源已知 | `python3 scripts/doctor.py --wizard`(只看键名,不读值) | 报告写明当前 tier(T0–T3)。缺数据走合同表降级列,不编数 |
| 路由对应的脚本真实存在 | `python3 scripts/<名>.py --help` | help 能打开,文中写的参数都在 help 里 |
| 症状先分层 | 点击降/展示降/位置降/收录降/分析工具降,见下文「事故问题按症状形态路由」 | 每个症状只进一条先查的路径,不五个集合同时展开 |
| 日期口径 | GSC 展示数据涉及[GSC 数据异常期](facts.md#gsc-anomaly)时,两期对比不跨这个期间 | 对比期不跨异常期,或报告里注明展示不可比 |

## 输出优先级规则

1. 先回答用户最直接的问题。
2. 再补充影响最大的相邻问题。
3. 不要一次把五个集合都展开，除非用户明确要整站路线图。

## 诊断管道、症状路由与决策闸门(qiaomu-seo 深读 2026-10-09b)

> 性质:第三方仓库(MIT,2026-08-03 创建)的阅读笔记,不是搜索引擎规则。本节「不能证明」表与闸门是本套件采用的工作口径;其中有 Google 原文可对的句子,已在句内附链接。

来源:[joeseesun/qiaomu-seo](https://github.com/joeseesun/qiaomu-seo) `references/{technical-seo,content-quality,keyword-content,international-commerce}.md` + `scripts/validate_skill.py`。核心工作模式:**按管道阶段路由技术问题,按症状形态路由事故问题,按决策台账路由内容问题,按闸门放行规模化动作**。

### 技术问题先定位管道阶段(七段,不得跨段推断)

`known`(URL 已被发现)→ `allowed to fetch`(robots/基础设施放行具名爬虫)→ `fetched`(HTTP 响应实际取回)→ `rendered`(JS 对具名渲染器执行充分)→ `index eligible`(响应/指令/内容/政策允许收录)→ `canonical selected`(平台聚类重复后选出代表 URL)→ `served`(该查询/市场/设备/时段实际展出)。一段失败不证明后段全败,一段通过不保证下段——**"收录了"和"排上了"是第 6 段和第 7 段,分开核**。

控制语义"不能证明"表(选工具时防越权结论):robots.txt 只管爬虫访问,不证明去索引/canonical/排名;robots meta/X-Robots-Tag 在抓取时才被发现;页面被 robots.txt 禁抓,其中的索引与展示规则会被忽略([Google robots meta 文档](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag),核对 2026-10-21 页面日期 2026-03-24);sitemap 只是发现与变更提示;IndexNow 只是通知,IndexNow FAQ 列出的提交端点是 Amazon、Bing、Naver、Seznam、Yandex、Yep,没有 Google([indexnow.org/faq](https://www.indexnow.org/faq),核对 2026-10-21);canonical 是你对 Google 表达的偏好(Google 称 rel=canonical 是强信号,最终仍由它选定)([Google canonical 文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls),页面日期 2026-07-10);redirect 不证明相关性等价(尤其批量重定向到首页,本套件口径);Google 抓取器默认最多跟 10 跳重定向([Google HTTP 状态码文档](https://developers.google.com/crawling/docs/troubleshooting/http-status-codes),页面日期 2026-02-04)。迁移双闸:上线前(旧 URL 清单+新旧映射分类、重定向/状态码/canonical/hreflang/内链/sitemap/埋点/robots 全测、高价值页与度量连续性保留、DNS 容量与回滚就绪),上线后(新旧主机+日志+索引报告+重要模板复核、重定向保够久、把预期内重抓波动与映射故障分开)。抓取配额工作只对超大/高频变更/已有容量问题的站点先做日志取证;**不承诺"封锁低价值 URL 会把配额转给优选 URL"**——Google 原文:除非已达抓取容量上限,不会把省下的配额转给其它页面;永久删除的页返回 404 或 410([管理抓取预算](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget),页面日期 2026-07-22)。

### 事故问题按症状形态路由(performance-measurement.md)

| 症状 | 先查 |
|---|---|
| 点击降、展示稳 | CTR、结果呈现、意图/SERP 变化、品牌需求、设备/市场结构 |
| 展示点击双降、位置稳 | 需求、季节性、查询组合、统计口径/范围 |
| 位置与展示双降 | 受影响模板/查询、内容与竞争、技术变更、政策与算法更新 |
| 收录量/爬取信号变化 | robots、noindex、canonical、重定向、渲染、宕机、安全、迁移、sitemap/feed |
| 分析工具降、SC 稳 | 埋点本身、同意机制、归因、落地页行为、转化代码 |

同比可比期+季节性+先分段再平均+保留发布时间线;证据淘汰前**多假设并存**。

### 内容问题走决策台账,清理走反保护条款(content-quality.md)

五决策(页级或模板级):`keep`(有用/有战略必要)/`improve`(意图对但缺、旧、弱)/`consolidate`(多页同任务,需查询/页面或 SERP 重叠证据+重定向方案)/`reposition`(页型/意图错配机会)/`remove`(无用户价值/法务安全/过期无替代,需清单+依赖+内链+流量+替代决策)。**反保护条款:不得仅因近期零点击批量删页**——新页、季节页、小众页、导航页、支持/法务页、低量高价值页都可能是必要的;破坏性操作保留决策清单与回滚路径。程序化 SEO 七道闸门全过才放行:①重复用户任务真实存在(非关键词排列组合);②每个可收录页有超越变量替换的页级价值;③数据出处/许可/准确性/新鲜度/缺值行为已定义;④模板暴露可爬 URL、有用导航、正确状态/canonical、稳定渲染;⑤空/重复/不可能/低价值组合被预防或有意排除;⑥分阶段上线+holdout 抽查先于全量曝光;⑦监控覆盖收录/质量/参与/转化/爬取/政策风险。**程序化系统的强度在数据与交互的可辩护性,不在 URL 数量**。AI 辅助不是质量判词:Google 的说法是,用生成式 AI 批量产出没有增加用户价值的页面,可能违反「规模化内容滥用」垃圾内容政策;AI 稿要人工核对事实([Google 生成式 AI 内容指南](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content),页面日期 2026-10-01;[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies#scaled-content));本套件口径:人写与 AI 辅助同一 usefulness/原创性/事实审查/披露/维护责任标准;拒绝项——竞品摘要改写冒充专业、逐 fan-out 铺页、伪造经验/评论/作者/日期/引用、翻译页无本地审查、自动发布无抽样无回滚。

### 关键词方法的三条排序规则(keyword-content.md)

①聚类证据优先级:同市场/设备/日期的**排名 URL 重叠** > 共同意图与预期页型 > 语义相似——不为每个变体建页;②意图从实际 SERP 判读(信息/导航/商业/交易/本地五类映射到 guide/首页/对比/产品页/地点页),混合 SERP 可能需要多页型或刻意选择最佳拟合意图;③优先级输入显式标签:业务相关与转化价值、需求证据、差异化能力、现实竞争、内容/工程成本、现有页匹配与蚕食风险、依赖(产品/数据/法务/专家审查)——**量/难度缺失时定性排序,字段留 `unknown`,不编数**。国际内容**在目标市场重跑发现与意图分析**,翻译源语言词表不叫研究。

### 国际/电商的结构路由(international-commerce.md)

语言/地区版本用稳定可爬 URL(非 cookie/浏览器切换切换);hreflang 每个版本都要列出自己和全部对应版本,互指缺失只让那一对被忽略,不是整簇作废;x-default 用于「没有匹配语言时的回退页」,常见于语言选择页或自动跳转的首页([Google 多语言文档](https://developers.google.com/search/docs/specialty/international/localized-versions),页面日期 2026-09-21);本地化页通常 canonical 自指而非机械指向原文;不按访客国家或语言自动改内容或跳转——Google 原文:按访客国家或语言返回不同内容的站点,Google 可能不抓取、不索引、不排名全部语区内容([locale-adaptive 文档](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages),页面日期 2025-12-10)。分页/加载更多:每页稳定 URL+顺序 `<a href>`(爬虫不点交互控件),**不要把分页序列的第一页当成所有分页的 canonical**([Google 分页文档](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading),页面日期 2025-12-10),过滤器组合防 URL 无限增生。变体是否独立 URL 由用户意图/可得性/内容/内链/运营定,变体选中态/URL/canonical/价格/库存/图/结构化数据保持一致。**五证据系统分离**:站点 HTML、Product 结构化数据、Merchant feed、自然搜索表现、免费列表/购物表面——feed 过审不证明自然收录,Product 标记不保证富结果,各系统间价格/库存/标识/URL 应一致。缺货/停产/换代决策:留 live+准确库存与替代 / 仅重定向到真等价替代 / 有持久价值留归档页 / 无替代 404 或 410——**不把停产品批量重定向到类目或首页**。

### 包契约与触发路由治理(validate_skill.py;技能工程层)

REQUIRED_FILES 硬契约(22 个必在文件,含 evals/trigger_cases.json、schemas、registry、scripts);**禁止嵌套 SKILL.md**(会破坏可发现性路由);frontmatter description 必须含 seo/audit/keyword/exclude 路由词(缺则警告);SKILL.md 内引用的 references/*.md 链接必须实际存在(悬空即 fail);触发评估三桶:`should_trigger` / `should_not_trigger` / **`near_neighbor`(近邻负例,专防误触发)**——本套件设计触发用例时照此三桶补齐。

## 子代理路由与 TOML 定义模式（codex-seo 深读 2026-10-09b,快照）

> 性质:第三方仓库快照笔记。核对 2026-10-21:该仓库已改名为 [AgriciDaniel/chatgpt-seo](https://github.com/AgriciDaniel/chatgpt-seo)(简介「Turn a page, draft, or SEO export into a sourced fix plan inside ChatGPT」),根目录已无 `agents/` 目录;下文的代理数量和文件结构是 2026-10-09 读到的旧版,**未能在现仓重核**,只当设计参考,不作为该仓现状的描述。

来源(旧版):`agents/*.toml` + `skills/seo/SKILL.md`(编排器)。它把路由拆成「自然语言触发(TOML agent)+ 能力探测加派(编排器)」两层,模式可移植。

**TOML 定义骨架。** 每个代理仅 4 字段:`name`、`description`(同时是触发文本,塞满关键词)、`nickname_candidates`(固定三件套:`seo-x` / `seo x` 带空格变体 / `x` 裸词)、`developer_instructions`(多行字符串即完整 system prompt)。description 写坏代理就路由不到:路由文本与代理一体存放时,要有校验防字段损坏(本套件口径:`self_check.py` 和 `link_check.py` 就是这类校验)。

**指令模板的收敛结构。** 老代理(technical/content/schema/local/performance 等)遵循同一骨架:角色句 → 编号工作流步骤 → 领域参考表(CWV 阈值、E-E-A-T 权重 20/25/25/30、Local 六维权重 25/20/20/15/10/10)→ Cross-Skill Delegation 段 → Output Format 契约(0-100 分、表格、Critical>High>Medium>Low、必须标注数据来源如 "DataForSEO (live)" / "On-page analysis (static)")→ Error Handling 表。新代理(hreflang/images/programmatic/plan)改用紧凑的「Prioritization Logic」段直接定义四级严重度映射,省去重复输出格式——两种粒度按代理复杂度选。

**条件加派靠能力探测,不靠用户口供。** 编排器固定派 8 个常驻代理(technical/content/schema/sitemap/performance/visual/geo/sxo),其余按环境探测加派:`google_auth.py --check` 有凭据 → seo-google;首页检测到本地业务信号 → seo-local;再叠加 DataForSEO MCP 可用 → seo-maps;外链 API key → seo-backlinks;内容策略信号 → seo-cluster;电商信号 → seo-ecommerce;存在 drift 基线 → seo-drift。行业判定(SaaS/本地/电商/出版/代理)来自首页信号词,判定含糊时列前两名候选让用户确认,不硬猜。

**分层降级与配额纪律。** seo-google 分 Tier 0/1/2(API key → +service account → +GA4),每层列出可执行的具体命令;seo-maps 分 Tier 0/1(免费 Nominatim/Overpass vs DataForSEO),Tier 0 时把缺失的 geo-grid 维度权重 25% 重分配(+10 GBP/+10 评论/+5 跨平台),评分体系不因数据缺失而空转。付费调用前必须过 `dataforseo_costs.py check`(approved/needs_approval/blocked 三态,needs_approval 要上报编排器);image-gen 永不自动生成图片,只输出计划(成本控制)。

**防重复路由与代理间总线。** 每个代理写明「不做什么」:seo-maps 明确不重复 seo-local 的页面分析、不重复 seo-geo 的 AI 可见性,改推荐 `/seo local <url>` 交还给对应代理;seo-technical 把 hreflang 细查 defer 给子技能。代理间用 `.seo-cache/` 共享缓存传递上下文(site-meta.json 的 business_type 会影响 schema 分析结论、audit-scores.json、pages/{slug}/*.json),读取三态:找到则引用并注明日期 / 缺失或损坏则当不存在 / 用户说 refresh 则整体忽略——与上文 qiaomu 的闸门思路互补:一个管「放行」,一个管「复用与去重」。

## 技术审计代理的标准作业程序(josstei/maestro-orchestrate 深读 2026-10-09d)

来源:[josstei/maestro-orchestrate](https://github.com/josstei/maestro-orchestrate) `src/agents/seo-specialist.md`(`src/agents/` 下共 40 个代理定义,核对 2026-10-21;该文件现 102 行,frontmatter 有 `max_turns: 20`,旧笔记写的 temperature 与超时设置已不在文件里,删除)。该代理是**只读+shell 跑审计工具**的定位(Lighthouse/结构化数据校验器;不修改代码只出报告);产出按下游分叉:coder 要可直接插入的 JSON-LD 片段+精确文件位置,copywriter 要内容级发现(薄内容/缺 alt/标题结构)。Handoff 契约分 Task Report(状态/文件/决策/验证)与 Downstream Context(接口/模式/假设/警告)两段。其三套决策框架可直接作为本套件技术审计的路由附件。

**可抓性审计五步(先验证"能被抓",再看内容质量——顺序即规则)**:①robots.txt 审查:按全部 user-agent 解析规则,标记封掉关键内容的过宽 Disallow;②sitemap 校验:存在性、XML 合法性、URL 数 vs 实际页面数、lastmod 准确性;③canonical 链分析:逐页追链,标记超过 1 跳的链、指向非 200 页的自指 canonical、冲突信号;④重定向审计:超过 2 跳的 301/302 链、循环、软 404;⑤渲染检查:识别无 JS 执行就不被索引的 JS 依赖内容(与 meta-tag-formulas 的"渲染态审计警告"同源)。**路由含义:请求落在①–⑤任一步的验证上 → 技术审计,不进内容/文案集合。**

**严重度三级(与上文的 H/M/L 不同粒度,审计报告用这级)**:**Critical**=页面完全无法索引(robots disallow、关键页 noindex、canonical 链断裂);**Major**=可索引但信号劣化(缺 canonical、重定向链、结构化数据不完整);**Minor**=优化机会(缺可选 meta、标题层级欠优)。排序铁律:按**实际搜索影响**排,不按理论最佳实践;依据现行引擎指南,不用过时 SEO 迷信。

**schema 选型矩阵(按页面主内容用途选型;必填列已按 Google 文档重写,核对 2026-10-21)**。maestro 原表的「必填」列和 Google 文档不一致:Article 在 Google 文档里没有必填属性;LocalBusiness 必填是 name 和 address,telephone 只是推荐;Event 必填是 name、startDate、location(含 location.name 和 location.address);Product 必填 name,另须 review、aggregateRating、offers 三者之一。FAQPage 和 HowTo 的富结果已不再展示。

| 页面类型 | 主 schema | Google 文档的必填 | 来源(页面日期) |
|---|---|---|---|
| 产品页 | `Product` | name + (review \| aggregateRating \| offers) 三选一 | [Product snippet](https://developers.google.com/search/docs/appearance/structured-data/product-snippet)(2026-09-08) |
| 文章/博客 | `Article` | 无必填;推荐 headline、image、datePublished、dateModified、author | [Article](https://developers.google.com/search/docs/appearance/structured-data/article)(2026-09-08) |
| FAQ 页 | `FAQPage` | Google 已不再展示 FAQ 富结果,文档已移除;只在别的系统需要时保留 | [事实表](facts.md#rich-results) |
| 指南/教程 | `HowTo` | Google 已不展示 How-to 富结果,结构化数据文档已移除 | [事实表](facts.md#rich-results) |
| 组织 | `Organization` | 无必填 | [Organization](https://developers.google.com/search/docs/appearance/structured-data/organization)(2026-09-08) |
| 本地商家 | `LocalBusiness` | name、address | [Local business](https://developers.google.com/search/docs/appearance/structured-data/local-business)(2026-09-08) |
| 活动 | `Event` | name、startDate、location | [Event](https://developers.google.com/search/docs/appearance/structured-data/event)(2026-09-08) |

校验以 **Google Rich Results Test 要求**为准——schema.org 允许的属性多于 Google 实际用于富结果的范围。反模式清单(路由到"拒答/纠偏"而非执行):关键词堆砌或精确密度目标(现代引擎用语义理解)、报缺 meta keywords(Google 不用 keywords meta 标签,[2009 年博客](https://developers.google.com/search/blog/2009/09/google-does-not-use-keywords-meta-tag)页首注明至今如此,核对 2026-10-21)、schema 与页面实际内容不符、所有页等权对待(按业务价值排序)、任何损害用户体验的 SEO 手法(隐藏文本/堆砌标题/桥页)。

---

## 附:原 SKILL.md 路由正文(2026-10-21 搬入)

> SKILL.md 瘦身后只留短版路由表。下面是原 SKILL.md 的单入口、路由表、五个能力集合的参考文件清单、输出模板、示例库与特别约束,原样搬入;标题降一级,链接改成从本文件出发的路径。

#### 1. 单入口
- SEO / GEO / AI 搜索可见度 / SERP / Schema / 技术 SEO / 排名追踪 / 外链 / Programmatic SEO / 竞品页 / 内容策略 / 内容刷新等需求，都从这里进入，再按下面的规则路由。

### 路由规则

#### 常见请求如何路由

高频请求速查;分诊细则、多路由规则与不应误路由的负例见 [routing-rules.md](routing-rules.md)。

| 请求类型 | 路由 |
|---|---|
| 「给我做关键词研究」 | research |
| 「为什么这个词排不上去」 | monitoring + research + technical |
| 「流量/排名下滑了，帮我查根因」 | monitoring + research + technical:monitor diff → sensor_volatility --context → changelog(下跌日页面变更)→ gsc_mining --decay;完整链见 [capability-map.md](capability-map.md) 任务链#9 |
| 「掉量是不是算法更新造成的」 | monitoring:Google Search Status Dashboard 官方时间戳对齐 + sensor_volatility z30 异常日佐证;只按 Dashboard 所列确认事件归因 |
| 「写一篇能排名的文章」 | content |
| 「展示多、点击 0,改标题和首段」「对齐买家提问」 | content:[question-alignment.md](../content/question-alignment.md) + `question_align.py` |
| 「英文文案按 ASD-STE100 检查」 | content:[asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md) + `ste_lint.py` |
| 「优化这篇文章让 AI 更容易准确引用」 | content |
| 「做 competitor alternative / vs 页面规划」 | research + content + technical |
| 「做 content pillars / topic clusters」 | research + content |
| 「这篇旧文章掉量了，帮我 refresh」 | content + monitoring + technical |
| 「做 technical SEO 审计」 | technical |
| 「把审计发现变成工单，跟进到修复关闭」 | technical:envelope 封套 → remediation init(phase 定 SLA)→ 修复 → verify 对比新旧体检自动核销 → report 出达成率 |
| 「加 Product / Breadcrumb / Organization schema」 | technical |
| 「重构网站结构和内链」 | technical |
| 「做 programmatic SEO 方案」 | technical |
| 「看排名变化和告警」 | monitoring |
| 「持续盯竞品排名变化」 | monitoring + research(明示降级:内置仅 citation_gaps 被引对照 / serp_overlap SERP 重叠近似;连续排名监控需自备外部排名追踪导出) |
| 「本地起个守护,长期监控我的站并自动完善」 | monitoring(monitor.py+notify.py,continuous-operations.md) |
| 「用 agent 自动化 SEO,每周帮我挑一页改」 | monitoring(agent-growth-loop.md:GSC×转化选赚钱页 → 一次一改 → 人批准上线 → 搜索+业务联合判定) |
| 「分析外链和权威度」 | monitoring |
| 「评估要不要进多语言/新市场」 | overview:先过 [intake-checklists.md](intake-checklists.md) 目标市场闸门,再按 [multilingual-workflow.md](multilingual-workflow.md) 逐市场分开评分 |
| 「不知道先做什么，帮我整体判断」 | overview |

#### overview
适用于：
- 用户说「做 SEO」「给我做 SEO 方案」「统一看下 SEO」
- 需要先判断该走哪一类
- 需要整站级优先级排序

参考：
- [references/overview/capability-map.md](capability-map.md)
- [references/overview/routing-rules.md](routing-rules.md)
- [事实表](facts.md):跨文件反复引用的外部事实(CWV 阈值、GSC 异常期、富结果退役日期、API 配额、sitemap 与 Googlebot 上限、搜索引擎份额)的唯一出处
- [站型打法手册](site-type-playbooks.md):八张站型卡(SaaS/电商/媒体/本地/文档/工具/Marketplace/YMYL)——开局先认站型再取 KPI/渠道/防死清单

#### research
适用于：
- keyword research
- SERP analysis
- content gap
- competitor analysis
- competitor alternative / vs page planning
- topic cluster / pillar strategy / intent mapping

优先参考：
- `references/research/keyword-intent-taxonomy.md`
- `references/research/topic-cluster-templates.md`
- `references/research/serp-feature-taxonomy.md`
- `references/research/gap-analysis-frameworks.md`
- `references/research/battlecard-template.md`
- `references/research/positioning-frameworks.md`
- `references/research/competitor-page-patterns.md`
- `references/research/competitor-content-architecture.md`
- `references/research/competitor-section-templates.md`
- `references/research/content-strategy-framework.md`
- [references/research/domain-strategy.md](../research/domain-strategy.md):选域·历史风险与过期域尽调·迁移 checklist·国际域名架构·"AI 记品牌不记 URL"
- [references/research/scoring-calibration.md](../research/scoring-calibration.md):评分器校准方法论——新建评分/调权重/改阈值曲线先过预注册闸门(权重不许手调)
- [references/research/serp-data-models.md](../research/serp-data-models.md):Google Trends / Google Scholar 抓取数据模型(字段级:主键/合并/去重规则)

输出模板：
- `templates/research/keyword-research-output.md`
- `templates/research/serp-analysis-output.md`
- `templates/research/content-gap-output.md`
- `templates/research/competitor-analysis-output.md`
- `templates/research/competitor-pages-plan.md`
- `templates/research/content-strategy-plan.md`
- 黄金样例:[examples/gold-standard-keyword-research.md](../../examples/gold-standard-keyword-research.md)——关键词研究的达标产出长什么样,先看再写


##### 多语言 / 多市场站点(全球 SEO/GEO 一把做)
- **markets/ 语区门户(18 个)**:references/markets/ 每语区一份专项参考(渠道/语言机制/AI-GEO/信息源/红旗/工具,2026-10-09 定向研究)——目标市场命中时先读对应门户页:
  - [references/markets/zh.md](../markets/zh.md):中文区——百度/微信搜一搜格局、公众号引用经济学、百家号/知乎生态、ICP 与可爬性
  - [references/markets/en.md](../markets/en.md):英文区(基线层)——Reddit 引用塌陷与 YouTube 被引、AIO 品牌词波动、段落级可引性
  - [references/markets/ru.md](../markets/ru.md):俄语区——Yandex 生态为主战场(Alice/Neuro)、76 条商业因子、erid/152-ФЗ 透明层
  - [references/markets/ko.md](../markets/ko.md):韩语区——Naver Blog/Cafe/지식iN 三入口、AI Briefing 引用条件、nosourceinfo 退出
  - [references/markets/ja.md](../markets/ja.md):日语区——Yahoo! Japan+Google 索引依赖、AIO 76.9%、全角规范、ステマ規制
  - [references/markets/es.md](../markets/es.md):西语区——es-ES 与 es-419 拉美分裂、方言归组、词汇分流与 ¿H2 惯例
  - [references/markets/pt.md](../markets/pt.md):巴西葡语区——ChatGPT 最强采用市场、Reclame Aqui 投诉站、PIX/CNPJ 骗局词
  - [references/markets/ar.md](../markets/ar.md):阿语区——RTL 全链路、MSA/方言分层、阿印 vs 欧洲数字统一、双向文本隔离
  - [references/markets/fr.md](../markets/fr.md):法语区——Bill 96 合规、courriel 术语表、:;!? 前窄空格、AIO 晚德一年红利窗
  - [references/markets/de.md](../markets/de.md):德语区(DACH)——Sie/du 语域、Impressum、Abmahnung 法律风险、1.000,00 数字格式
  - [references/markets/id.md](../markets/id.md):印尼语区——baku/gaul 语域分流、EYD V 规范、低价机型/slow-4G 性能基线
  - [references/markets/hi.md](../markets/hi.md):印地语区(印度)——Hinglish 三种书写现实、罗马化文本 AI 处理损耗、语音查询、lakh 分组
  - [references/markets/it.md](../markets/it.md):意大利语区——it-CH 独立 locale、P.IVA/估算声明、it 市场工具栈
  - [references/markets/tr.md](../markets/tr.md):土耳其语区——第二个 Yandex 市场(份额双口径必并记:StatCounter 读数([事实表](facts.md#search-share))远高于本地点击实测,交付以 Google 为主战场、Yandex 仅桌面重度受众作次级审计)、İ/ı 大小写陷阱、tanıtım yazısı 披露、Trendyol 站内搜索
  - [references/markets/vi.md](../markets/vi.md):越南语区——有调/无调变体跟踪、标题词前 30 字符规则、Coc Cốc 本土引擎
  - [references/markets/th.md](../markets/th.md):泰语区——无空格分词(Intl.Segmenter 定论)、字素计长、佛历日期、ครับ/ค่ะ 语体
  - [references/markets/pl.md](../markets/pl.md):波兰语区——变音符规范化归组、sierotki 行首禁则、本地论坛生态
  - [references/markets/nl.md](../markets/nl.md):荷兰语区——nl-NL/nl-BE 弗拉芒分叉、je/u 语域、KvK 与占位符红线
- [信源监控体系](intel-sources.md):**持续完善本套件该盯什么**——四层信源(官方引擎 top20/研究数据/18 市场本地/竞品观察名单)+信源→模块映射表+新仓扫描检索式;
- [多语言工作流](multilingual-workflow.md):**全球主干**——市场总表(中/英/俄/韩/日/西/葡/阿/法/德/印尼)、逐市场工具栈映射、语言与内容规范(阈值不可互套)、检查顺序、合规速查、常见坑
- 区域知识已融入五类能力文件,按需读取:[多语言工作流](multilingual-workflow.md)(引擎格局/工具栈/合规)、[AI 平台差异事实库](../content/geo-platform-differences.md)第六节(Yandex Alice/Neuro、Naver AI Briefing、日语 AIO、引用语言绑定)、[AI 爬虫政策](../technical/ai-crawler-policy.md)第三节(YandexAdditional、Naver 收录、Bing 日本)、[hreflang 校验](../technical/hreflang-validation.md)(es-419 例外、RTL、市场码组合)、[关键词意图分类](../research/keyword-intent-taxonomy.md)(Wordstat/DataLab/ラッコ 工具链与方言归组)、[intake 清单](intake-checklists.md)(目标市场 intake 闸门)、[中文 AI 搜索指南](../content/chinese-ai-search-guide.md)
- 多区域站点逐市场分开评分,不合并总分

##### 外链（backlinks）
- [外链画像分析](../research/backlink-profile-analysis.md)：七段式框架、数据源置信度级联、健康分与数据闸门、disavow 决策
- [外链渠道目录](../research/backlink-directory.md)：分级渠道清单（含核验日期）、提交纪律与反虚荣 KPI
- [站群与多站点策略](../research/site-networks.md)：多站光谱（合法多站→卫星站/PBN→泛站群）、多站架构决策树（ccTLD/子目录/子域、聚合 vs 隔离）、各市场站群实况、风险量化（SRA/传染性）、白帽等效对照、存量站群四层指纹审计清单
##### 目录提交引擎（directory submissions）
- [目录提交引擎](../research/directory-submissions.md)：九问就绪闸门、13 层目录结构、追踪 CSV、反虚荣 KPI
##### 竞品全景（landscape）
- [竞品全景](../research/competitive-landscape.md)：五类形态(企业闭源/主流 SaaS/内容工作台/GEO 创业/开源)的功能设计与打分口径速查、2025-2026 行业共识数据(AIO 点击影响/llms.txt 裁决/AI 归因)、20 项借鉴清单(含现状对照)——做方案对比、选型建议、向管理层论证时引用
- [借鉴实施规格库](../research/borrow-specs.md)：竞品深读后的**施工图**——health_score/content_score/fix_plan/forecast/prioritize/citation decay 的公式与字段、SF/Sitebulb 文案结构、27 bot 名单、Conductor 告警模型、monitor 缺口清单;开发新脚本或扩展现有脚本前先查此库


#### content
适用于：
- SEO content brief
- SEO / GEO content writing
- title / meta 优化
- content quality / E-E-A-T
- AI citation / quotable content 优化
- content refresh / decay recovery / refresh vs rewrite

优先参考：
- **[references/content/geo-evidence.md](../content/geo-evidence.md)**：凡涉及 GEO / AI 引用的任务，先读这一份。
  它按产品范围区分官方规则、实验、相关性与营销转述；不把 C-SEO Bench 的有限实验外推为「所有 GEO 无效」或「收益必然归零」。
  按其记录（2026-09-04 核对 Google 文档），FAQ 富结果已停止展示，也没有专门的 AI Schema；强制问答切块、TLD 固定加权、「多域名转载引用翻倍」都不能当作实施依据。
  其他参考文件与它冲突时，以它为准。
- [references/content/question-alignment.md](../content/question-alignment.md)：title、H1、首段和 description 用买家提问的原词，首段第一句直接回答。改标题、改 meta、写 brief、做 refresh 前先读；候选页用 `question_align.py` 找。
- [references/content/asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md)：短句、一句一事、主动语态、术语一致（ASD-STE100 Issue 9 借用原则）；英文用 `ste_lint.py` 做近似检查。STE 没有排名或 AI 引用的实证，价值在读者理解。
- `references/content/title-formulas.md`
- `references/content/content-structure-templates.md`
- `references/content/content-patterns.md`
- `references/content/ai-citation-patterns.md`（描述性，非因果性，见上）
- `references/content/quotable-content-examples.md`
- `references/content/ai-writing-detection.md`
- `references/content/meta-tag-formulas.md`
- `references/content/content-decay-signals.md`
- `references/content/content-refresh-playbook.md`
- [深度研究写作协议](../content/deep-research-protocol.md):五轮检索设计(共识测绘→缺口→核实→反例→自检)+信息增益自检(n-gram 近似 IGS>0.5+独家观点 5-7)+引用纪律(具名+日期/不复述被引源)+反例与不确定性标注——"引擎奖励深度留下的表层特征,不奖励过程"

输出要求：
- 根据 `references/content/` 中的结构、写法要点和 playbook 直接生成 brief、meta、GEO 优化或 refresh 方案。


##### GEO / AI 搜索（llms.txt 与可引用性）
- [llms.txt 指南](../content/llms-txt-guide.md)：格式规范、校验严重度、生成规则
- [AI 平台差异事实库](../content/geo-platform-differences.md)：五引擎引用行为、爬虫分类、优化侧重
- [图片与视觉搜索 SEO](../content/image-search-seo.md):Lens 月约 200 亿次视觉搜索(Google 2024-10 博客);Search Console 2026-09-24 起有 multimodal 筛选;Google 不索引 CSS 背景图,关键图用 `<img>`/`<picture>`;Lens 排名因素只有第三方相关性研究(Backlinko 2020,alt 匹配 11.4%);Merchant Center 主图要求;版权、C2PA 与抓取
- [Discover 与新闻 SEO](../content/discover-news-seo.md):Discover 官方定位"补充渠道";**2026-02 首个专属核心更新=本地化+反标题党**;大图 1280×720/16:9+max-image-preview:large;Publisher Center 已关(算法化收录);48h news sitemap;**日本新闻域名跌出 AI 引用总榜(百科压制)+Cloudflare Pay-Per-Crawl 杠杆反转**
- [视频 SEO/GEO](../content/video-geo-guide.md):AI 怎么用视频(厂商研究:播放量与被引几乎不相关,文本可及性更值得先做)、Google 视频索引与富结果官方要求、人工校对字幕是唯一可控的文本层、key moments、播客转录层、YouTube 站内算法的证据边界
- [电商 GEO 阶梯](../content/ecommerce-geo-ladder.md):五级阶梯(产品数据→评价→内容→marketplace 分工→agent 交互)、Product schema 七个高频错误、七市场分叉表、AI 购物现状、UCP/ACP 双协议
- [可引用性打分](../content/citability-scoring.md)：五维块级打分、AI 就绪度分层、方法纪律
- [GEO 证据银行](../content/geo-evidence-bank.md):可引用的案例数字/行业研究/论文——每条带链接与日期,按证据分级决定用法
- [UGC 与站内搜索](../content/ugc-site-search.md):UGC 内容怎么排上名+站内搜索怎么处理与挖掘(同一批 URL 的双模块)
##### 中文 AI 搜索（独有能力）
- [中文 AI 搜索指南](../content/chinese-ai-search-guide.md)：引用经济学（品牌官网仅 1.37%）、各引擎护城河、CJK 阈值、15 项就绪清单


#### technical
适用于：
- technical SEO audit
- on-page audit
- schema markup
- internal linking
- site architecture
- entity / knowledge graph
- Core Web Vitals / performance
- programmatic SEO
- analytics 中与 SEO 归因相关的实现部分

优先参考：
- `references/technical/robots-txt-reference.md`
- `references/technical/http-status-codes.md`
- `references/technical/scoring-rubric.md`
- `references/technical/schema-examples.md`
- `references/technical/schema-templates.md`
- `references/technical/validation-guide.md`
- [references/technical/semantic-html.md](../technical/semantic-html.md)：需要核页面语义结构时读取。
- `references/technical/link-architecture-patterns.md`
- `references/technical/entity-signal-checklist.md`
- `references/technical/knowledge-graph-guide.md`
- `references/technical/playbooks.md`
- `references/technical/navigation-patterns.md`
- `references/technical/site-type-templates.md`
- `references/technical/mermaid-templates.md`
- `references/technical/LCP.md`
- `references/technical/cwv-playbook.md`
- [审计工具输出解读](../technical/audit-tool-output.md)：用户提供 Screaming Frog / Lighthouse / Sitebulb / Ahrefs / GSC 导出时先读——各工具字段对照、脚本化审计器 JSON 信封、跨工具字段映射与 findings 合并七步、严重度重映射(P0-P3)
- [head 元素完整参考](../technical/head-elements.md):HTML head 全元素 2026 口径(joshbuchea/HEAD 重组;含弃用清单与平台私有 meta)
- [重定向与 Canonicalization](../technical/redirects-canonical.md):重定向全类型+canonical 六场景深度指南(信号合并/迁移/跨域)
- [Agent 协议速查卡](../technical/agent-protocols.md):15 协议一页对照(Content Signals/WebMCP/ARD/RSL…每卡:规则数字/验证命令/状态)
- [审计规则全目录](../technical/audit-rule-catalog.md):SEOmator 373 规则深读(三态计分/20 类权重/档位);P0/P1 79 条已扩 Sitebulb 式解释层(what/why/trigger/caveat/fix/export 九字段)
- [Brand Records 品牌事实档案](../content/brand-records.md):六记录(含批准术语/never-do)+YAML 格式+缺口协议+Grounding Page 11 条——内容起草前必读,oracle_check.py 的输入
- [多语言 GEO 证据与更新清单](../research/multilingual-geo-evidence.md):fan-out 语言切换与引用池本地化/翻译有效但机翻政策级降权/独立语言 URL 自持权威/分市场杠杆表(Tistory·头条·Habr·知恵袋空置)/小语种唯一源红利——含 multilingual-workflow.md 的 9 项接入清单
- [AI 回答五维打分卡](../content/geo-scoring-rubric.md):回答质量闸(refusal/echo-only)+五维加权+硬 cap+绝对排名+情感校准+反通胀——对 citation_panel 采样回答做 agent 语义打分的标准
- [niubigeo 深读](../research/niubigeo-deep-read.md):6,848★ 五周爆发竞品(2026-09 创建)的架构深读与 Top 10 借鉴(提及检测 URL 掩码/gapLabel 七叉决策树/意图冻结分母/配对差分指纹/observed-consensus 词筛/D·K 纪律)——做 GEO 可见性功能前先查
- [管线完备性地图](pipeline-completeness.md):10 视角审计的缺口登记簿(R0 修复接线/R1 project 编排器+strategy-fit/R2 数据接入/R3 pSEO·内链·多市场生产线/R4 执行末端)——**规划任何新能力前先查此表**,避免加重散珠
- [数据接入指南](data-onboarding.md):用户视角的「我想做 X 分析→需要什么数据/怎么获取/没有时降级成什么」——12 行目标矩阵+T0-T4 凭证阶梯+安全纪律+intake 三问模板;接 doctor --wizard
- [数据源合同表](data-source-contract.md):全部脚本的数据来源/降级路径/反编造守则——**调用任何脚本前先查此表**,缺数据走降级列而不是编造([real]/[est] 标注规则)
- [CI 质量门手册](../monitoring/ci-gates.md):三件套命令地图(site_audit→audit_compare→ci_format→action.yml)/siteone 阈值全表/LHCI 断言 schema/采样协议/防假 0 三律/三部署配方——进 CI 或定时审计前读
- [过时信号看门表](../technical/deprecated-signals.md):官方已停用/勿再推荐清单(带时间戳与一手来源)——**涉及 schema/富结果/CWV/GSC 口径的建议前必查**;tests/test_canonical_facts.py 用 16 条正则钉死已知错误陈述(套件内文档命中即测试失败)
- [Naver Search Advisor 蒸馏](../technical/naver-searchadvisor.md):55 篇官方指南全量蒸馏(每节 guid 可对勘原文)
- `references/technical/event-library.md`
- `references/technical/ga4-implementation.md`
- `references/technical/gtm-implementation.md`

输出模板：
- `templates/audit/full-seo-audit.md`
- `templates/audit/on-page-audit.md`
- `templates/audit/technical-audit.md`
- `templates/audit/entity-audit.md`

Schema 实现和 programmatic SEO 方案直接依据 `references/technical/` 生成。


##### AI 爬虫与国际化
- [AI 爬虫政策](../technical/ai-crawler-policy.md)：引用型 vs 训练型 bot、四种典型 robots 配置、暗坑清单
- [JS 渲染与 SPA SEO](../technical/rendering-seo.md):两波索引已死的新口径、渲染策略决策表、**meta 注入红线(社交/AI 爬虫不执行 JS)**、五引擎渲染差异(Naver 官方建议 SSR/百度以抓取诊断实测)、SPA 审计 7 项与 cloaking 红线
- [移动 SEO 专项](../technical/mobile-seo.md):移动优先索引切换后现状(2024-07 起只抓 smartphone UA/**桌面独有内容=不存在**)、内容平价检查法与破裂诊断表、移动体验阈值速查(viewport/48px 触摸目标/16px 字体/插页惩罚豁免清单)、AMP 遗产与迁移 7 步、slow-4G/慢 3G 测试矩阵(引 markets 印尼基线)、移动 SERP 与 app 深度链接 2026 现实(Firebase 已死/官方"不改展示"口径)、审计 15 项
- [服务器日志分析](../technical/log-analysis.md):日志是 AI 到访的唯一可靠测量层(GA 看不见不执行 JS 的爬虫)、DNS 双重验证、**Bytespider 无视 robots 只能边缘封锁**、a11y×SEO 三分法(SEO 重叠/纯人类/agent 项)
- [Agent-Readiness 操作层](../technical/agent-readiness.md)：协议时代站点准备(ARD 三级发现链/WebMCP 页面工具/Web Bot Auth 签名/Lighthouse AGENTIC_BROWSING 七审计/语言中立层多语言部署/就绪决策表)
- [hreflang 校验](../technical/hreflang-validation.md)：八检框架、实现方式选择、内容平价
##### 程序化与规模化
- [程序化 SEO 闸门](../technical/programmatic-seo-gates.md)：100/500 页闸门、页型地板、安全 vs 风险页型、索引膨胀控制
- [程序化 SEO 作战手册](../technical/programmatic-seo-playbook.md)：全生命周期九章（选词模式挖掘/数据层护城河/URL 与 sitemap 分片/模板工程防 doorway/内链规模化/索引与抓取预算/cohort 测量与 90 天淘汰/Wise·Zapier·Nextdoor·Webflow 四案例实测）


#### monitoring
适用于：
- rank tracking
- backlink analysis
- performance / stakeholder reporting
- alert thresholds
- 域名权威度评估
- SEO KPI monitoring

优先参考：
- `scripts/monitor.py`(持续监控守护入口:init 建库 → run 日检/周检 → diff 告警 → report 周报;通知走 `scripts/notify.py`)
- [references/monitoring/continuous-operations.md](../monitoring/continuous-operations.md)：持续运营手册——日四问/周趋势/月校准分层、告警四级×playbook、防疲劳三律、自动安全项 vs draft PR 人审边界、三种部署形态(GH Actions/本地 cron/claude -p headless 含 prompt 模板)
- [references/monitoring/agent-growth-loop.md](../monitoring/agent-growth-loop.md):增长周循环——GSC×转化联合选「赚钱页」、流量陷阱标记、agent 三文件(brief/state/log)与对外动作批准门、一次一改的周循环与搜索+业务联合判定、前四周排期
- `references/monitoring/tracking-setup-guide.md`
- `references/monitoring/link-quality-rubric.md`
- `references/monitoring/outreach-templates.md`
- `references/monitoring/kpi-definitions.md`
- `references/monitoring/report-templates.md`
- `references/monitoring/alert-threshold-guide.md`
- [本地网格排名](../monitoring/local-grid-ranking.md):geo-grid 三指标 ARP/ATRP/SoLV 源码级口径+网格参数公式+GBP 信号权重
- [惩罚识别与恢复](../monitoring/penalty-recovery.md):手动动作类型学全清单/鉴别诊断/reconsideration 全流程/负面 SEO 防御

输出模板：
- `templates/monitor/rank-report.md`
- `templates/monitor/backlink-report.md`
- `templates/monitor/performance-report.md`
- `templates/monitor/alert-playbook.md`(值班告警处置剧本:按 L1-L3 三步排查,先排季节性与算法更新再查发布/页面变更)
- `templates/monitor/ai-visibility-weekly.md`(Scrunch 六段周报:>5pp 才点名/恰好一条动作/全平则 stable no action needed)
- `templates/monitor/ai-visibility-monthly.md`(月报五节:Executive Summary/Visibility/Competitive/Content Health 三分/Recommendations 恰好 3 动作)
- `templates/monitor/citation-outreach-brief.md`(引用缺口外联简报)
- `templates/research/prompt-bank.md`(GEO 采样 prompt 库:20 条漏斗×视角矩阵+persona 前缀+fanout 六类型+5+3+2 配方)
- `templates/content/content-brief.md`(三段式简报:证据头/执行摘要/大纲六件套+9 内容类型变体)
- `templates/content/pre-publish-checklist.md`(发布前 27 条闸:meta/结构/内容/AI 可引性四组,机检条目挂真实脚本)
- `templates/content/trend-jack-playbook.md`(热点选题决策件:四问闸门[相关/净新观点≥5/时效窗口/独家三选一]+GO·PIVOT·WATCH·DROP 判定矩阵+wire 硬新闻否决+48h 发布管线+scaled-content-abuse 红线;配 trend_watch.py 规格待实装)
- `templates/audit/report-modes.md`(报告三模式:exec/dev/prospect 一表三裁+Today's priorities+建议四字段)
- `templates/monitor/forecast-report.md`(管理层提案:五级漏斗+三档 scenario+省钱/赚钱双结构+ROI 五法)

#### 5. 示例库(examples/)
带日期目录的真实/合成示例(REPORT.md verdict-first+evidence/ 编号回溯+快照免责声明):site-audit-chain-example.com(真实站审计→健康分→修复计划全链)/citation-panel-demo(合成面板);新增示例的规范见 examples/CONVENTIONS.md

### 特别约束


##### 品牌与 AI 可见性
- [品牌提及监控](../monitoring/brand-mention-monitoring.md)：五平台加权、买家提示词集、实体建设清单
##### 漂移监控（drift）
- [SEO 漂移监控](../monitoring/seo-drift-monitoring.md)：13 元素基线、17 条对比规则、SQLite 存储模型


#### Schema 检查
- FAQPage 词汇是否合法、Google 当前是否支持富结果、对 AI 引用是否有效，三件事分别判断，不混为一个「通过」。
- 不要仅凭 `curl` 或静态抓取说「没有 schema」；优先使用浏览器渲染、富媒体搜索结果测试，或用户提供的渲染后证据。

#### API 文档与多产品参考页
- 逐项核对参数名、必填与否、类型、允许值、适用范围和真实示例；可以复用排版和自动检查，但不要用模板批量替换产品名来生成事实。

#### 对外动作
- 外联邮件、提交表单、发布内容、改线上配置等动作，本 Skill 只负责起草和给出方案，执行前由用户本人确认。

### 默认工作流

1. 识别任务目标
2. 走统一 intake
3. 路由到一个或多个能力集合
4. 给出结构化结果
5. 明确验证方式与下一步

### Related

- 本 Skill 覆盖 SEO 的完整范围，其他 SEO 类 Skill 不是运行前提。
- 若需求明显属于 CRO、广告、销售或内容营销，且不以 SEO 为核心，可以转交你环境中的其他 Skill 处理。

### 补充链接(2026-10-21 新增)

上面清单里写成代码路径、没有链接的文件,以及原 SKILL.md 没列的文件:
- 内容:[quotable-content-examples.md](../content/quotable-content-examples.md)、[community-seo-playbook.md](../content/community-seo-playbook.md)(社区 SEO 操作手册)
- 研究:[search-everywhere-optimization.md](../research/search-everywhere-optimization.md)(全平台搜索优化)
- 技术:[gtm-implementation.md](../technical/gtm-implementation.md)
- 监控:[tracking-setup-guide.md](../monitoring/tracking-setup-guide.md)、[link-quality-rubric.md](../monitoring/link-quality-rubric.md)、[outreach-templates.md](../monitoring/outreach-templates.md)
- 历史记录,不作现行依据:[freshness-log-20261011.md](freshness-log-20261011.md)
