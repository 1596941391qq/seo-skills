# AI 搜索平台差异事实库

> 建立于 2026-10-09；2026-10-21 按一手来源再次全量重核（上一轮 2026-10-18）。厂商官方事实与第三方观察分开写；没有官方说明的一律标「第三方观察」。
> 这些是各平台的**公开行为差异**，不是排名公式。优化建议由此推导，但不承诺引用结果。证据仲裁见 [geo-evidence.md](geo-evidence.md)。

## 一、厂商文档级事实（核对 2026-10-21）

| 平台 | 官方事实 | 出处 |
|---|---|---|
| ChatGPT | `OAI-SearchBot` 用于搜索；禁它的站不会出现在 ChatGPT 搜索答案里，但仍可能作为导航链接出现。改 robots.txt 后约 24 小时生效。两个机器人都放行时，OpenAI 可能只用一次抓取结果满足两种用途 | [OpenAI bots](https://platform.openai.com/docs/bots) |
| ChatGPT | `GPTBot` 只管训练；各设置互相独立，禁 GPTBot 不影响搜索 | 同上 |
| ChatGPT | `ChatGPT-User` 是用户触发的访问，官方原话「robots.txt rules may not apply」；它不决定搜索收录 | 同上 |
| ChatGPT | 搜索使用「第三方搜索提供商」和合作方直接提供的内容；官方没有写明是哪家索引 | [OpenAI 2024-10-31](https://openai.com/index/introducing-chatgpt-search/) |
| Perplexity | `PerplexityBot` 用于在搜索结果中展示和链接网站，不用于训练基础模型；`Perplexity-User` 由用户请求触发，「generally ignores robots.txt rules」；变更最长 24 小时生效 | [Perplexity bots](https://docs.perplexity.ai/guides/bots) |
| Claude | `ClaudeBot` 用于训练；`Claude-SearchBot` 用于搜索索引；`Claude-User` 是用户触发的访问。三者都遵守 robots.txt；封 IP 可能让爬虫读不到 robots.txt；IP 清单在 claude.com/crawling/bots.json | [Anthropic 帮助](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) |
| Google | AI Overviews / AI Mode 的资格 = 已索引且可带摘要展示；控制入口是 Googlebot 的 robots.txt 与 `nosnippet` 等指令；Search Console 有「Search generative AI」纳入/排除开关（[全球开放日期](../overview/facts.md#gsc-genai)） | [AI features](https://developers.google.com/search/docs/appearance/ai-features)、[SC 帮助](https://support.google.com/webmasters/answer/16908024) |
| Google | `Google-Extended` 是控制 token，不单独抓取：管未来 Gemini 模型（Gemini Apps、Vertex AI API）的训练，以及 Gemini Apps 和 Vertex AI 的 grounding；不影响 Google 搜索收录与排名。SC 帮助页另写明：它也限制「搜索生成式 AI 功能所用模型」的训练 | [Google 常见爬虫](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)、[SC 帮助](https://support.google.com/webmasters/answer/16908024) |
| Google | `Google-Agent` 是 Google 托管的 agent 按用户请求访问网页时用的 UA；用户触发类抓取「generally ignore robots.txt rules」 | [Google 用户触发抓取](https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers) |
| Copilot | Bing 与 Copilot 共用抓取、索引、排名基础；指南要求放行 Bingbot，没有列出单独的 Copilot 爬虫。用 IndexNow 通知增删改；`NOARCHIVE` 不进 Copilot 回答与 grounding；`NOCACHE` 只用网址、标题、摘要；GEO「does not guarantee grounding or citations」 | [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a) |
| Apple | `Applebot` 用于 Spotlight、Siri、Safari 搜索，抓到的内容也可能作为生成答案的上下文；`Applebot-Extended` 只管训练退出，自己不抓取；退出「广域知识答案」用 `nosnippet`；robots.txt 没写 Applebot 但写了 Googlebot 时，Applebot 照 Googlebot 的规则执行 | [About Applebot](https://support.apple.com/en-us/119829)（2026-09-04） |
| Meta | `Meta-WebIndexer` 改善 Meta AI 搜索，放行它有助于 Meta AI 引用并链接；`Meta-ExternalAgent` 用于训练或直接索引；`Meta-ExternalFetcher` 按用户请求抓取，可能绕过 robots.txt；Meta 只认 robots.txt，不认 NoAI 一类非标准标签 | [Meta Web Crawlers](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers) |
| Amazon | `Amazonbot` 的数据可能用于训练；`Amzn-SearchBot` 用于 Alexa 等搜索，不用于训练，没被点名时照其他搜索爬虫的规则执行；`Amzn-User` 由用户触发，可能不遵守全部 robots 指令 | [About AmazonBot](https://developer.amazon.com/amazonbot) |
| Mistral | `MistralAI-User`（Vibe 用户请求，不训练）、`MistralAI-Index`（Mistral 搜索索引，不训练）、`MistralAI-Training`（训练） | [Mistral crawlers](https://docs.mistral.ai/robots) |
| Yandex | Алиса AI 的答案出现在传统搜索结果之内，由搜索算法判定「有用才显示」，并列出作为依据的来源；选源看专业性、有用性、原创性、内容充实。退出：robots.txt 对 `YandexAdditional` 或 `YandexAdditionalBot` 写 `Disallow`，2–14 天生效 | [如何形成答案](https://yandex.ru/support/webmaster/ru/alice)、[可见度报告](https://yandex.ru/support/webmaster/ru/service/alice-answers)、[禁止索引（含 Алиса AI 退出）](https://yandex.ru/support/webmaster/ru/adding-site/indexing-prohibition)、[官方博客 2024-04](https://webmaster.yandex.ru/blog/yandeks-zapustil-neyro-kak-on-rabotaet) |

**近期官方变化**：
- 2026-10-15，Google 宣布 AI Mode / AI Overviews 增加内联链接并更靠前；测试在回答顶部单列「一两个完成该任务的官方页面」；时效新闻轮播扩到更多国家和语言，并突出用户的 Preferred Sources（官方称使用人数年初至今增长 7 倍以上）；回答末尾相关文章改为带缩略图的链接；AI Mode 视频结果的创作者名可点到 Search profile（[Google 博客](https://blog.google/products-and-platforms/products/search/updates-ai-mode-overviews-explore-web/)）。
- 2026-10 中旬，Bing Webmaster Tools 的 AI Performance 报告新增 Topics Portfolio（Beta），按主题聚合 grounding queries（[Bing 博客](https://blogs.bing.com/webmaster/2026/10/introducing-topics-portfolio-beta-in-ai-performance/)）。

## 二、第三方观察（不外推为算法）

| 平台 | 观察 | 来源与口径 |
|---|---|---|
| ChatGPT | 被引最多的 10 个来源内部，Wikipedia 占 47.9%、Reddit 11.3%；Wikipedia 占全部引用 7.8% | Profound，6.8 亿条引用，2024-08~2025-06（[原文](https://www.tryprofound.com/blog/ai-platform-citation-patterns)） |
| ChatGPT | 44.2% 的引用来自页面前 30% | Kevin Indig，120 万条回答（[SEL 报道](https://searchengineland.com/chatgpt-citations-content-study-469483)，2026-02） |
| ChatGPT | 品牌自有与竞品页占被引 URL 39.3%（Gemini 13.8%） | arXiv 2609.35077，B2B SaaS（见 [geo-evidence-bank.md](geo-evidence-bank.md) 第七节第 1 条） |
| Perplexity | 前 10 来源内部 Reddit 占 46.7%（占全部引用 6.6%） | Profound，同上 |
| Google AIO | 前 10 来源内部 Reddit 21.0%、YouTube 18.8% | Profound，同上 |
| 新鲜度 | Ahrefs：AI 助手被引 URL 比自然结果新 25.7%，ChatGPT 最偏好新内容，AIO 最接近自然结果。Seer：AIO 约 85%、Perplexity 约 80%、ChatGPT 约 71% 的引用发布于 2023–2025（Peec.ai 引用数据，5,000+ 个被引 URL，2025）。两家在「谁最偏好新内容」上结论相反：Ahrefs 说 AIO 最旧，Seer 说 AIO 最偏爱近期内容 | [Ahrefs](https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/)（1,697.5 万 URL，2025-07-28）；[Seer](https://www.seerinteractive.com/insights/study-ai-brand-visibility-and-content-recency)（2025） |
| 跨引擎 | 被引内容中位年龄 Claude 5.1 个月、ChatGPT 8.0 个月；23,908 条第三方 LinkedIn 引用中 96.6% 来自 AIO，Gemini 为 0 | arXiv 2609.35077 |
| 跨引擎 | 引用半衰期：峰值后中位 11 天减半；一个页面在不同引擎上的寿命相关性只有 0.03–0.09 | Profound，88.3 万页、7 个引擎（[原文](https://www.tryprofound.com/blog/the-half-life-of-an-ai-citation-is-11-days)） |

## 三、爬虫分类（决策用）

| 类别 | 例子 | 封掉的后果 |
|---|---|---|
| 搜索/索引爬虫 | OAI-SearchBot、Claude-SearchBot、PerplexityBot、Googlebot、Bingbot、Applebot、Amzn-SearchBot、Meta-WebIndexer、MistralAI-Index | 失去该产品的搜索引用 |
| 用户触发访问 | ChatGPT-User、Claude-User、Perplexity-User、Google-Agent、Meta-ExternalFetcher、Amzn-User、MistralAI-User | 用户点名你的页面时取不到；其中多家声明可能不受 robots 约束 |
| 训练爬虫 | GPTBot、ClaudeBot、CCBot、Amazonbot（可能用于训练）、Meta-ExternalAgent、MistralAI-Training | 不影响搜索引用；是授权决策 |
| 控制 token（不发请求） | Google-Extended、Applebot-Extended | 只声明「其他爬虫抓到的内容能否这样用」 |

- **禁 `GPTBot` 不阻止 ChatGPT 搜索引用你**：OpenAI 写明各设置独立，搜索看 OAI-SearchBot。
- **没有「一键全引擎退出」**：ChatGPT 禁 OAI-SearchBot；Google 用 Search Console 的生成式 AI 开关（不是 Google-Extended）；Perplexity 禁 PerplexityBot，但 Perplexity-User 可能不受约束；Apple 用 `nosnippet`。
- **组选择规则**（[RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html) 2.2.1）：爬虫只执行匹配自己名字的组；有点名组时，`*` 组对它不生效。只写在 `*` 组里的指令（如 Cloudflare 的 `Content-Signal`）不会自动带到点名组。
- **robots.txt 拿不到时**（RFC 9309 2.3.1）：4xx 视为没有限制；5xx 视为全站禁止，持续约 30 天后可改按 4xx 处理或用缓存。
- **不要用封 IP 代替 robots.txt**：Anthropic 写明封 IP 会让爬虫读不到 robots.txt，退出不一定生效。
- 更多爬虫与组合策略见 [ai-crawler-policy.md](../technical/ai-crawler-policy.md)。

## 四、按平台的检查重点（由第一节推导，不是保证）

| 平台 | 先做到 | 再观察 |
|---|---|---|
| Google AIO / AI Mode | 已索引、可带摘要；生成式 AI 开关处于「纳入」；关键事实写在可见正文 | GSC 生成式 AI 效果报告（只有展示） |
| ChatGPT | 放行 OAI-SearchBot（及 WAF 白名单其 IP 段）；页面能被主流搜索引擎收录 | 抽样面板 + chatgpt.com 引荐 |
| Perplexity | 放行 PerplexityBot 并按官方 IP 段放行 WAF | 抽样面板 + perplexity.ai 引荐 |
| Copilot | Bing 收录；IndexNow；不加 `NOARCHIVE`/`NOCACHE` | Bing Webmaster Tools → AI Performance |
| Claude | 放行 Claude-SearchBot 与 Claude-User | 抽样面板 |
| Apple | 放行 Applebot；`nosnippet` 只用在确实要退出 AI 答案的内容 | 无官方报告 |
| Yandex | 先在 Yandex 自然结果里排进前列 | Webmaster「Видимость сайта в Алисе AI」SoV |
| Naver | 在 Naver 自有生态（博客、카페、지식iN）里有内容 | 服务资料页的「AI 브리핑 인용수」 |

## 五、可引用的统计（第三方，引用时带口径）

- **GEO 原始论文**（KDD 2024）：「引用来源 / 加引语 / 加统计」在位置加权词数上 +30–40%；原排第 5 的来源用「引用来源」+115.1%。条件：gpt-3.5-turbo + 固定前 5 条结果，详见 [geo-evidence.md](geo-evidence.md) 第三节。
- **SE Ranking**（[原文](https://seranking.com/blog/how-to-optimize-for-chatgpt/)，2025-11-24 发布、2026-03-27 更新；12.9 万个域、216,524 个页面、20 个行业）：2,900 词以上的文章平均 5.1 次 ChatGPT 引用，800 词以下 3.2 次；标题间段落 120–180 词的页面平均 4.6 次，不足 50 词的 2.7 次（约多 70%）；3 个月内更新的 6.0 次 vs 3.6 次；带 FAQ Schema 的页面 3.6 次，不带的 4.2 次。全是合并相关，未按域名控制。
- **AirOps**（[原文](https://www.airops.com/report/structuring-content-for-llms)，2025-07-18，分析 1.2 万+ 个 URL，只看页面自身结构、不含外链和权威）：标题层级连续（H2>H3>H4）的页面被引几率 2.8 倍；同报告称富 Schema 页面被引可能性高 13%——这是合并相关，生产研究按域名控制后 Schema 无独立效应（[geo-evidence-bank.md](geo-evidence-bank.md) 第八节）。
- **Conductor**（2025-05~09）：ChatGPT 占 AI 引荐流量 87.4%。

### 仓库根 README「为什么是现在」表的来源登记（核对 2026-10-21）

README 里的数字以本表为准。结论列：V＝原文读到；F＝原文说法不同，README 要改；D＝找不到可信出处，README 要删；未核＝没打开原文。

| README 条目 | 结论 | 原文与口径 |
|---|---|---|
| GEO 服务市场 8.5 亿 → 2031 年 73 亿美元 | F | [Valuates 新闻稿](https://www.prnewswire.com/news-releases/generative-engine-optimization-geo-services-market-to-hit-7-3b-by-2031--growing-at-34-cagr--valuates-reports-302505741.html)（2025-07-15）：2024 年 8.86 亿、2031 年 73.18 亿，年复合增速 34%。起点是 8.86 亿。市场研究厂商的估算，各家差得远（Dimension Research 写 2026 年 10.9 亿），写「估算」和厂商名 |
| AI 引荐流量年增速 +527% | V | [Previsible 2025](https://searchengineland.com/ai-traffic-up-seo-rewritten-459954)：19 个 GA4 站点，2025-01~05 对比 2024 同期，会话 17,076 → 107,100。样本是 19 个站。更新值：[Previsible 2026-07](https://previsible.com/seo-strategy/ai-traffic-report-july-2026/)，166 个站，2024-11~2026-05 月会话 9.9 倍 |
| AI 流量转化率是自然搜索 4.4 倍 | V | [Semrush](https://www.semrush.com/blog/ai-search-seo-traffic-study/)（2025-06）：以转化率计的「价值」，样本是 500 多个 SEO 相关话题；Semrush 卖 AI 可见度工具。不是通用倍数 |
| Gartner：传统搜索流量到 2028 年 −50% | F | [Gartner 新闻稿](https://www.gartner.com/en/newsroom/press-releases/2023-12-14-gartner-predicts-fifty-percent-of-consumers-will-significantly-limit-their-interactions-with-social-media-by-2025)（2023-12-14）：预测，对象是「品牌的自然搜索流量」，下降「50% 或更多」；不是实测，不是传统搜索流量 |
| 品牌提及对外链的相关性约 3 倍 | V | [Ahrefs](https://ahrefs.com/blog/ai-overview-brand-correlation/)（2025-05-26，7.5 万品牌）：与 AIO 品牌提及次数的 Spearman 相关，全网提及 0.664，外链数 0.218，比值 3.05。对象是「AIO 里被提及的次数」，不是「AI 排名」；相关不等于因果。[2025-12 后续研究](https://ahrefs.com/blog/ai-brand-visibility-correlations/)加入 ChatGPT 和 AI Mode：YouTube 提及最强（约 0.737），全网提及 0.66–0.71 |
| GEO 优化内容可见性 +30–115% | F | [GEO 论文](https://arxiv.org/abs/2311.09735)：三种方法在位置加权词数上 +30–40%（gpt-3.5-turbo，固定前 5 条）。+115.1% 只是「原排第 5 的来源用引用来源」一格；同表排第 1 的来源平均 −30.3% |
| 投入 GEO 的营销者仅 23% | D | 只追到 Incremys（法国 SEO/GEO 厂商博客）和转引它的博客，原句是「做提示词追踪和 GEO 测量」，没有原始调查、样本和日期。README 删 |

第二张表（全球市场）：

| 条目 | 结论 | 原文与口径 |
|---|---|---|
| Yandex 是俄罗斯第一搜索引擎 | V | StatCounter 读数见[事实表](../overview/facts.md#search-share)，三套口径见 [ru.md](../markets/ru.md) |
| 俄语信息查询 68% 有 AI 答案（applabx） | 未核 | 只找到 AppLabx 的统计汇编帖，找不到 68% 的原句 |
| Naver 在韩国的份额 | V | 口径不同读数不同：InternetTrend 来路构成里 Naver 领先，StatCounter 页面浏览里 Google 略高（[事实表](../overview/facts.md#search-share)）。两种口径都写，见 [ko.md](../markets/ko.md) |
| 韩国 AI 브리핑引用几乎全是 Naver 自有生态 | V | [Andgentic](https://andgentic.com/insights/what-is-naver-ai-briefing/)（2026-07-24，厂商博客）原句 "almost exclusively" |
| 日本 AIO 出现率 76.9% | V | 见第六节 Itera 行 |
| 日本 AI 搜索使用率 21.3% → 37.0% | V | [CyberAgent](https://www.cyberagent.co.jp/news/detail/id=33041)（2026-03-05）；更新值：[2026-08 调查](https://www.cyberagent.co.jp/news/detail/id=33787)含 AI Mode 为 52.3% |
| 巴西 ChatGPT 25.5%、约 5,000 万月用户 | F | 数字出自 Atlantico（2025-07，约 5,400 万月活 App 用户，经 LinkedIn 帖转述），不是 StatCounter/OpenAI，来源标注要改 |
| 西语查询 83–84% 引西语源（Temso） | V | [Temso](https://www.temso.ai/data/-Lost-in-Translation-How-AI-Models-Handle-Local-Language-Sources)（2026-04，700 万条引用，4 个模型）：83–84% 只是 Google AIO 和 Copilot 的数；Grok 为 55% 以上；ChatGPT 本语言源 70.2%、英语源 23.7% |
| Yandex 在土耳其的份额 | F | StatCounter 读数见[事实表](../overview/facts.md#search-share)，月间波动大，见 [tr.md](../markets/tr.md)；「3 月约 13%」未核 |
| 印度 ChatGPT 约 1 亿周活 | V | [TechCrunch](https://techcrunch.com/2026/02/15/india-has-100m-weekly-active-chatgpt-users-sam-altman-says/)（2026-02-15）转述 Altman |
| ChatGPT 全球 12 亿周活、联网搜索类查询约为 Google 的五分之一 | 厂商自述 | OpenAI 消费产品负责人 Adam Fry 接受 Big Technology 采访（2026-11-03，[SER 转述](https://www.seroundtable.com/chatgpt-20-percent-google-42451.html)）；「搜索」按 ChatGPT 每次联网检索计，不是 Google 的查询口径，不能直接拿来和搜索引擎份额比 |
| 非英语 SEO skill top 仓库 1–5 星 | 未核 | GitHub API 实测值，本轮没有重跑 |

## 六、市场差异：区域 AI 搜索平台

Google 系之外的 AI 搜索入口行为不同，不套用同一套 GEO 假设。只列已核到出处的条目。

| 平台（市场） | 已核行为 | 来源类型 | 实操含义 |
|---|---|---|---|
| **Алиса AI**（俄） | 答案按当前 Yandex 搜索结果生成；Webmaster「Видимость сайта в Алисе AI」报告 SoV（近 3 个月、每周更新、只统计你已排得较高的查询、不提供点击和展示）；退出用 `YandexAdditional` | Yandex 官方 | 先做 Yandex 排名；用 SoV 作官方计量口径 |
| **Yazeka**（土） | Yandex 土耳其的 AI 搜索，2024-12 发布，给出基于来源的答案 | Yandex 官方页 + 当地报道 | 土耳其市场单独测，不套俄罗斯结论 |
| **Naver AI 브리핑**（韩） | 官方引用基准五项：전문성·경험 / 주제 일관성 / 진정성·투명성 / 가독성 / 활동성·최신성；「AI 브리핑 인용수」自 2026-01 累计，显示在博客、지식iN、카페、프리미엄内容的资料页；入选 Naver 메이트的人数据公开 | Naver 官方帮助 | 韩语 GEO 先做 Naver 生态内容；用 인용수 作可查基准 |
| **Naver AI 브리핑**（韩） | Naver 表示被引内容约 70% 是其自有 UGC | 第三方报道（[Nasmedia](https://blog.nasmedia.co.kr/entry/2606naspick)，2026-06-16，转述 Naver 的说法；Naver 官方原话未找到） | 同上 |
| **Mistral Vibe**（法） | 三个爬虫：`MistralAI-User` / `MistralAI-Index` / `MistralAI-Training` | Mistral 官方 | 可只禁训练、保留索引 |
| **Google AIO（日）** | 30 个领域 1,459 个查询中 76.9% 出现 AIO | 第三方调查（Itera，AI 可见度监测厂商自测，[PR TIMES](https://prtimes.jp/main/html/rd/p/000000030.000177930.html) 新闻稿 2026-08-05，报告期 2026-07） | 日语区 AIO 覆盖面大，单独监测 |
| **提问语言（日）** | 用日语提问时 26% 的被引来源在 .jp 域，用英语约 1% | 第三方（Weglot，2026-09） | AI 引用审计必须用目标语言提问 |
| **ChatGPT 子检索语言** | 非英语 prompt 的子检索 43% 用英语 | 第三方遥测（Peec AI，2026-02） | 非英语市场也要有英文权威来源 |
| **阿拉伯语内容** | 阿拉伯语只占已知内容语言网站的 0.6% | [W3Techs](https://w3techs.com/technologies/details/cl-ar-) | 阿语结构化内容竞争少（方向判断，非引用承诺） |

中文引擎见 [chinese-ai-search-guide.md](chinese-ai-search-guide.md)。

## 七、测量口径（防误读）

- **GSC 生成式 AI 效果报告**（先对部分站点开放，后对全球开放，[日期](../overview/facts.md#gsc-genai)）只有展示，没有点击、CTR、查询维度；维度只有页面、国家、日期、设备。这些数据同时计入总体效果报告，所以 AI 功能带来的点击仍然拆不出来。
- **Bing AI Performance**：Total Citations、Average Cited Pages、Grounding queries（抽样）、页面级引用数；2026-02 公测（[Bing 博客](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/)）。
- **引荐流量是下界**：Ahrefs 测试发现 Copilot、Mistral、Jasper 的访问在分析工具里显示为「Direct」（[Ahrefs](https://ahrefs.com/blog/ai-traffic-study/)）。用 referrer 清单 + 服务器日志 + 分析工具三源对账，按平台分列。
- **抽样面板的五状态**（本套件口径，实现见 `scripts/citation_panel.py`）：no_answer / failed / brand_absent / name_only_mention / cited_brand。采集失败不等于内容缺口；提及不等于引用。
- **query fan-out 三桶**：`python3 scripts/fanout_analysis.py fanout.csv`（列：prompt,web_query）把子查询分成 added / dropped / preserved，用来看引擎改写了哪些词。

## 八、品牌纠错（Negative GEO，本套件口径）

各家都没有公开的「品牌事实更正」工单通道；产品内反馈是单向上报。不要向客户承诺「提交后会被更正」。现行闭环：

1. **基准问题集**：客户口吻问价格、功能、政策；跨引擎、新会话、跨日重复；存截图和时间戳。
2. **分类**：过时事实 / 实体混淆 / 复读第三方错误 / 信息缺失 / 纯幻觉。
3. **追来源**：有引用列表的引擎（Perplexity、AIO）直接看来源；无引用时用错误断言反查最匹配的网页。
4. **改源**：先改自有页面；第三方走发布者更正、目录/评测站修正；Wikipedia 走讨论页，不直接编辑。
5. **反馈**：用各产品回答下方的反馈入口（赞/踩、Google 的「Report a problem」）。Search Console 的生成式 AI 开关是退出，不是更正。
6. **复测**：修复后按同一问题集复跑，报告修复前后快照。诽谤性内容走法务。

## 九、检查清单

| # | 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|---|
| 1 | 搜索/索引爬虫与用户触发访问都放行 | `python3 scripts/robots_posture.py https://站点/robots.txt --json` | 通过：search 与 user 层无禁止。失败：任一层被禁（training 层被禁不算失败） |
| 2 | 点名组没有丢掉 `*` 组里的关键行 | 人工读 robots.txt，对每个点名组核对 Disallow / Content-Signal | 通过：点名组里重复了需要的行。失败：只写在 `*` 组 |
| 3 | WAF 不拦官方爬虫 | 服务器日志按 UA 统计状态码：`python3 scripts/ai_referral_log.py access.log --bot-ua --classify`；可疑 UA 用官方 IP 清单核 | 通过：检索型爬虫多为 200。失败：403/429/挑战页 |
| 4 | Copilot 能用全文 | 查重点页的 `<meta name="robots">` 与 `X-Robots-Tag` | 通过：没有 noarchive / nocache。失败：有 |
| 5 | Google 生成式 AI 开关是有意设置 | Search Console → 设置 → Search generative AI | 通过：与业务决定一致。失败：无人知道当前状态 |
| 6 | 按平台分列监测 | `python3 scripts/citation_panel.py report`；GSC、Bing、Yandex、Naver 各自报告 | 通过：每个平台单独一列。失败：合并成一个分数 |
| 7 | 统计引用时带口径 | 对照本文第二、五节 | 通过：写明来源、样本、时间、相关/因果。失败：只写一个百分比 |
