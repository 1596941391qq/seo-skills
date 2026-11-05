# GEO 证据银行：可引用的案例数字、行业研究与论文

> 用途：给方案、报告和其他参考文件提供**带出处、带口径**的 GEO 数字。使用前提：先读 [geo-evidence.md](geo-evidence.md)（仲裁）；本银行与它冲突时，以它为准。
> 2026-10-21 全量复核（上一轮 2026-10-18；2026-11-05 第七节新入库第 12、13 条，复核于 2026-11-05）：每条都重新打开原文核对；找不到原文或数字对不上的已删除或改写。原始来源池为 [amplifying-ai/awesome-generative-engine-optimization](https://github.com/amplifying-ai/awesome-generative-engine-optimization)（CC0）与后续调研批次。
> 引用时保留口径（样本、平台、时间、方法）。数字冲突时并列呈现，不择优选边。

## 一、证据分级与引用规则

| 级别 | 类型 | 允许的用法 |
|---|---|---|
| A | 同行评议论文（会议、期刊） | 引用其实验设定内的结论；写明模型、任务、指标与局限 |
| B | 预印本（arXiv/SSRN，未评审）；有方法说明的第三方大样本研究（Ahrefs、Semrush、Conductor 等） | 作为观察或初步证据；写明样本、时间窗、作者身份 |
| C | 综述性报告、媒体报道、小样本测试、厂商综合统计 | 作为现象证据；写明一手出处 |
| D | 厂商/代理商自报案例 | 只写「有厂商报告了此结果」；不进实施验收与预算预测 |

### 引用前检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 级别与用法匹配 | 对照上表 | 通过：D 级只作「厂商报告」。失败：把 B/C/D 级写成因果 |
| 时效 | 看条目日期；快变数字超过 60 天先重开原文 | 通过：原文仍在、数字未变。失败：原文 404 或已改版 |
| 口径完整 | 引用句里有样本、平台、时间 | 通过：三项齐全。失败：只剩一个百分比 |
| 冲突并列 | 查第五节 | 通过：有冲突的结论同时写出另一方。失败：只引对自己有利的一方 |

## 二、案例数字库（D 级：厂商/代理商自报）

| 案例 | 数字 | 方法（自报） | 链接 | 日期 |
|---|---|---|---|---|
| 制造业站点（Matt Diggity） | 月度 AI 流量 +2,300% | E-E-A-T 与内容优化 | [diggitymarketing.com](https://diggitymarketing.com/ai-overviews-seo-case-study/) | 2025-06-18 |
| Hedges & Company 案例 #2（先作对照、后优化） | 优化后 AI 流量 +200%；作者自述加 llms.txt「效果极小、很少被抓取」 | Schema、自有方法、llms.txt | [hedgescompany.com](https://hedgescompany.com/blog/2025/04/ai-search-optimization-case-studies/) | 2025-04（页面标注 2025-12-19 更新） |
| Go Fish Digital | 自述影响了 ChatGPT 搜索结果（无数字） | 实时优化实验 | [gofishdigital.com](https://gofishdigital.com/blog/seo-case-study-how-we-influenced-the-chatgpt-search-results/) | 2025-07-25 |

**使用警示**：以上都是单一案例、无对照、由利益相关方发布。写进方案只能表述为「厂商报告的案例数字」，不换算成客户预期。页面级手段的合并正效应在域名固定效应下会反转或归零（[arXiv 2609.35077](https://arxiv.org/abs/2609.35077)，见第七节第 1 条），这类条目一律降权。

## 三、行业研究库（B/C 级：规模化观察）

> 统一约束：提示词集与权重共同定义各追踪器的「答案市场」，不必代表真实用户需求（[arXiv 2609.06811](https://arxiv.org/abs/2609.06811)，第七节第 3 条）。跨追踪器数字不直接比较或合并；引用必须带厂商名、查询集口径、时间窗。

### 引用模式与平台差异

- **Conductor 2026 AEO/GEO Benchmarks**（[原文](https://www.conductor.com/academy/aeo-geo-benchmarks-report/)）：13,770 个域、350 万 prompt、1,700 万条 AI 回答、1 亿+ 引用（2025-05~09，美国）。ChatGPT 占 AI 引荐流量 87.4%；AI 引荐占全部流量 1.08%（两个数都是 10 个行业的平均值，来自 Conductor 的分析数据）。「LLM 引荐转化率约 2 倍」是报告里引用的 Knotch 客户数据，不是 Conductor 自己的测量。
- **Profound 引用模式**（[原文](https://www.tryprofound.com/blog/ai-platform-citation-patterns)，6.8 亿条引用，2024-08~2025-06）：在 ChatGPT 被引最多的 10 个来源内部，Wikipedia 占 47.9%（占全部引用 7.8%）；在 Perplexity 前 10 来源内部，Reddit 占 46.7%（占全部引用 6.6%）。「前 10 内部份额」与「全部份额」不能混写。
- **Kevin Indig**（[SEL 报道](https://searchengineland.com/chatgpt-citations-content-study-469483)，原文 [Growth Memo 2026-02-16](https://www.growth-memo.com/p/the-science-of-how-ai-pays-attention) 付费，未核原文）：18,012 条核验引用；SEL 写 44.2% 来自页面前 30%，31.1% 来自 30–70% 的中段，24.7% 来自最后部分。SEL 报道同时写了「120 万条回答」和「300 万条回答、3,000 万条引用」，两处口径不一致；引用时只带 SEL 的百分比，并注明二手转述。
- **Seomator**（[原文](https://seomator.com/blog/ai-search-optimization-insights)）：转述 Profound 的 Josh Blyskal 在 BrightonSEO（2025-04）展示的 4,100 万条 AI 搜索结果分析；原文提醒各结论样本不同。

### AI Overviews 覆盖率（不同面板并列，不合并）

- **Semrush**（[原文](https://www.semrush.com/blog/semrush-ai-overviews-study/)，1,000 万+ 关键词，美国）：2025-01 6.49% → 2025-07 24.61% → 2025-11 15.69%。导航类查询触发 AIO 从 0.74%（1 月）升到 10.33%（10 月）。Search Engine Land 的同类报道（[2025-12](https://searchengineland.com/google-ai-overviews-surge-pullback-data-466314)）用的是同一份 Semrush 数据（SEL 归 Semrush 所有），不是独立来源；该报道还给出 AIO 旁出现广告从约 3% 升到约 40%。
- **Conductor**（同上报告）：2025-09-15~10-12，2,190 万次搜索中 25.11% 触发 AIO。
- **Ahrefs**（[原文](https://ahrefs.com/blog/ai-overview-growth/)，2,500 万个 AIO）：触发 AIO 的美国关键词占比从 7.6%（2025-03-13）升到 16.48%（2025-05 初）。

### 点击、流量与品牌

- **Ahrefs 点击研究**：有 AIO 的关键词，第 1 位平均 CTR 比无 AIO 的同类信息型关键词低 34.5%（[2025-04-17](https://ahrefs.com/blog/ai-overviews-reduce-clicks/)，30 万关键词各 15 万，聚合 GSC 数据，桌面端，2024-03 vs 2025-03）；同方法复测低 58%（[2026-02-04](https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/)，2023-12 vs 2025-12）。这是相关，不是因果。只引新值时要写明旧值。
- **Ahrefs AI 流量**（[原文](https://ahrefs.com/blog/ai-traffic-study/)，3,000 个站，2025-02-06）：63% 的站至少有一次 AI 引荐；平均 0.17% 的访客来自 AI（只含分析工具里能追踪到来源的访问，是下界）；作者实测 Copilot、Mistral、Jasper 的访问显示为「Direct」。
- **Ahrefs 品牌研究**（[原文](https://ahrefs.com/blog/ai-overview-brand-correlation/)，2025-05-26，7.5 万个品牌，Spearman 相关）：与 AIO 品牌提及次数相关最强的是全网品牌提及（0.664），外链数只有 0.218（域名评级 0.326、引用域名数 0.295）；约 26% 的品牌在 AIO 中零提及。作者强调相关不等于因果。 同一团队的[后续研究](https://ahrefs.com/blog/ai-brand-visibility-correlations/)（2025-12-12，同样 7.5 万品牌，加入 ChatGPT 和 AI Mode）：YouTube 提及相关最强（约 0.737），全网品牌提及 0.66–0.71，页面数量几乎无关（约 0.194）。引用时用后一份，并写明相关不等于因果。
- **联网比例**：在约 1.4 万条 LMArena 对话里，24% 的 GPT-4o 回答、34% 的 Gemini 回答没有抓取网页（[arXiv 2508.00838](https://arxiv.org/abs/2508.00838)，期刊版 Data & Policy，2026-04-28）。

### 引用失败与信任

- **Tow Center**（[Nieman Lab 报道](https://www.niemanlab.org/2025/03/ai-search-engines-fail-to-produce-accurate-citations-in-over-60-of-tests-according-to-new-tow-center-study/)，2025-03）：8 个 AI 搜索引擎、每个 200 次查询（共 1,600 次），让它们按文章引文给出标题、日期、媒体名和链接，超过 60% 答错；Gemini 与 Grok 3 给出的捏造链接多于正确链接。

### llms.txt 采用与效果

- **Rankability**（[原文](https://www.rankability.com/data/llms-txt-adoption/)，2026-09-18，Tranco 列表）：前 1,000 个域中 9.3% 有 llms.txt 或 llms-full.txt；前 1 万个域为 8.3%。2025-06 的首次测量是 0.3%，2026-06 为 8.7%；各次扫描方法不同，不是连续序列。分母含无法确认的域（前 1,000 个域里有 474 个结果未知），所以百分比偏低。
- **HTTP Archive Web Almanac 2025**（[SEO 章](https://almanac.httparchive.org/en/2025/seo)）：有效 llms.txt 出现在 2.13% 的桌面站、2.10% 的移动站。
- **SE Ranking**（[原文](https://seranking.com/blog/llms-txt/)，约 30 万个域）：10.13% 有 llms.txt；统计和机器学习都没发现它与 AI 引用频率相关。
- 与 [geo-evidence.md](geo-evidence.md) 第五节一致：Google Search 不使用 llms.txt；它不是 GEO 必做项。

### 爬虫与基础设施

- **Vercel**（[原文](https://vercel.com/blog/the-rise-of-the-ai-crawler)，2024-12-17，Vercel 网络内一个月的数据）：GPTBot、Claude、AppleBot、PerplexityBot 合计近 13 亿次抓取，约为 Googlebot 的 28%。同一文章实测：OpenAI、Anthropic、Meta、ByteDance、Perplexity 的爬虫会下载 JS 文件但不执行，读不到纯客户端渲染的内容；Gemini 借用 Googlebot 的渲染，Applebot 能渲染。这是 2024-12 的结果，现状要重测。
- **Prerender**（[原文](https://prerender.io/blog/how-to-optimize-your-website-for-ai-crawlers/)，厂商观点）：多数 AI 爬虫难以执行 JavaScript。Prerender 出售预渲染服务；要引这个结论，用上一条 Vercel 的实测。
- **robots.txt 受控实验**：10 个带联网检索的 AI 助手 × 4 种 robots 条件，共 200 次试验；部分助手未请求 robots.txt 就访问受限资源，或用通用 UA（[arXiv 2607.14447](https://arxiv.org/abs/2607.14447)，第七节第 4 条）。

### 市场快照（带日期，过期即弃）

- Google 2025-12 核心更新：2025-12-11 开始，12-29 完成（[Search Status Dashboard](https://status.search.google.com/incidents/DsirqJ1gpPRgVQeccPRv)；另见 [gsqi.com 分析](https://www.gsqi.com/marketing-blog/google-december-2025-broad-core-update-analysis-findings/)）。
- OpenAI 广告原则（[openai.com](https://openai.com/index/our-approach-to-advertising-and-expanding-access/)，2026-01-16）：广告不影响回答；广告与回答分开并标注；不出现在健康、心理健康、政治等敏感话题旁。

## 四、论文库

### 奠基与基准

| 论文 | 一行结论 | 级别 | 链接 |
|---|---|---|---|
| GEO（Aggarwal 等，Princeton / IIT Delhi，KDD 2024） | 在 gpt-3.5-turbo + 固定前 5 条结果的设定里，最佳方法使回答内可见度最高 +40%（位置加权词数 +41%）；GEO 概念的原始出处 | A | [arXiv 2311.09735](https://arxiv.org/abs/2311.09735) / [ACM](https://dl.acm.org/doi/10.1145/3637528.3671900) |
| C-SEO Bench（Puerto 等，NeurIPS 2025 D&B） | 多数现行内容优化方法基本无效甚至有害；提高来源排序的传统 SEO 更有效；采纳者越多收益越低 | A | [arXiv 2506.11097](https://arxiv.org/abs/2506.11097) |

### 知识冲突与检索

| 论文 | 一行结论 | 级别 | 链接 |
|---|---|---|---|
| ConflictBank | 约 745 万条「主张-证据」对与 55 万条问答，评估知识冲突 | B | [arXiv 2408.12076](https://arxiv.org/abs/2408.12076) |
| What Evidence Do LMs Find Convincing?（ConflictingQA，ACL 2024） | 模型主要看网页与问题的相关度，基本忽略有无科学引用、语气是否中立等人类看重的风格特征 | A | [arXiv 2402.11782](https://arxiv.org/abs/2402.11782) |
| When Search Engine Services meet LLMs | Search4LLM 与 LLM4Search 综述 | B | [arXiv 2407.00128](https://arxiv.org/abs/2407.00128) |

### 对抗与安全（只作风险警示，不作操作手册）

| 论文 | 一行结论 | 级别 | 链接 |
|---|---|---|---|
| GASLITE（ACM CCS 2025） | 针对特定概念的查询，投毒率低至 0.0001%（论文举例值）即可让恶意段落进入多数查询的前排结果 | A | [arXiv 2412.20953](https://arxiv.org/abs/2412.20953) |
| Adversarial SEO for LLMs | 页面里藏 prompt injection（如白色小字）可让 Bing 推荐目标商品的概率达到对照的 2.5 倍（论文用虚构相机页面做实验） | B | [arXiv 2406.18382](https://arxiv.org/abs/2406.18382) |
| Dynamics of Adversarial Attacks（ICML 2026 workshop） | 用无限重复囚徒困境模拟排序操纵攻防 | B | [arXiv 2501.00745](https://arxiv.org/abs/2501.00745) |
| Ranking Manipulation for Conversational Search（EMNLP 2024） | prompt injection 能稳定抬升低排名商品，并可迁移到 perplexity.ai | A | [arXiv 2406.03589](https://arxiv.org/abs/2406.03589) |
| Persistent Pre-Training Poisoning | 投毒 0.1% 的预训练数据，4 种攻击中有 3 种在后训练后仍可测 | B | [arXiv 2410.13722](https://arxiv.org/abs/2410.13722) |

## 五、已知冲突与引用纪律

1. **GEO 40% vs C-SEO Bench 无效**：引用任一方都要提示另一方及条件差异（检索/生成阶段、模型、指标、多采纳者）。批判综述（[arXiv 2607.14035](https://arxiv.org/abs/2607.14035)）判定：原文增益以「来源已在固定上下文中」为前提，不证明自然可发现性和持续流量（第七节第 2 条）。
2. **AIO 覆盖率**：Semrush（6.49% → 24.61% → 15.69%）、Conductor（25.11%）、Ahrefs（16.48%）是不同面板、不同月份；SEL 报道与 Semrush 是同一数据。只带口径引用，不取最大值制造紧迫感。
3. **厂商案例 vs 评审研究**：Diggity +2,300% 与 C-SEO Bench「多数方法无效」并存；方案里两者都写，分别标级别。
4. **llms.txt**：采用率 2%–10%（口径不同）+ Google 官方不使用 + SE Ranking 无相关 = 不作为实施必选项。
5. 行业数字 60 天内复查，见 [geo-evidence.md](geo-evidence.md)「八、证据保鲜机制」。
6. **引用半衰期双口径**：SSRN 7344201 综合多家厂商数据给出中位 4.5 周；Profound 自有数据给出中位 11 天。样本与「半衰期」定义不同，不择一写成通用值（第六节第 7 条）。
7. **arXiv 2609.35077 的常见误读**：①「最佳匹配段中位深度 0.36」是作者按语义相似度算出的段落位置；作者据此推断引擎偏好页面上部三分之一，但论文没有测量引擎「从顶部读、读到某处停下」。②把「FAQ 段 β=+0.07」读成「停止写 FAQ」——它是很小的正值。③把 domain fixed effects（按网站域名控制）译成「控制领域深度」。④把转述者自报的「结论挪到第一段，两周后引用约 2.4 倍」当成研究结论——那是无对照的自述。引用该研究一律回原文，并带上「B2B SaaS、四引擎、只含被引页、观察性」四个限定。

---

## 六、2026-10-11 调研批次（2026-10-18 复核后口径）

1. **检索漏斗：读了不一定引**（A）：约 1.4 万条 LMArena 对话；Perplexity Sonar 每次查询约访问 10 个相关页面、只引用 3–4 个；Gemini 92% 的回答没有可点击引用；24% 的 GPT-4o 与 34% 的 Gemini 回答没有抓取网页。来源：[arXiv 2508.00838](https://arxiv.org/abs/2508.00838)，期刊版 Data & Policy（剑桥，2026-04-28）。数据是 2025 年的引擎快照，不外推为现值。
2. **GEO 原始论文的 +30–40%**（A）：「引用来源 / 加引语 / 加统计」在位置加权词数上 +30–40%，在主观印象上 +15–30%。生成引擎是 gpt-3.5-turbo，输入固定为 Google 前 5 条结果；测的是回答内可见度，不是检索或流量。来源：[arXiv 2311.09735](https://arxiv.org/abs/2311.09735)，KDD 2024。外推时与第五节第 1 条并读。
3. **约 16% 的被引来源有 AI 生成痕迹**（B）：ChatGPT、Copilot、Gemini、Perplexity × 712 条真实人类查询（政治、健康、环境）。来源：[arXiv 2605.23684](https://arxiv.org/abs/2605.23684)，2026-05。口径是「检出 AI 生成证据」，不是「全部由 AI 写成」。
4. **多语言 RAG**（A）：BordIRLines 数据集（领土争议 × 49 种语言，ACL 2025 Findings）。多语检索比只用本语言文档更一致、地缘偏见更小；用低资源语言提问时，回答引用的语言分布方差大得多。来源：[arXiv 2410.01171](https://arxiv.org/abs/2410.01171)。任务是文化敏感事实问答，不是商业查询。
5. **AI 引用的内容更新**（B）：Ahrefs 用 1,697.5 万个被引 URL 比较 ChatGPT、Perplexity、Gemini、Copilot、AIO 与自然结果。AI 助手（ChatGPT、Perplexity、Copilot、Gemini）被引 URL 平均发布后 1,064 天，自然结果 1,432 天，新 25.7%。ChatGPT 最偏好新内容（引用平均 958 天）；AIO 最接近自然结果、偏旧（1,432 天）；四个 AI 助手里 Perplexity 最偏旧（1,166 天）。来源：[Ahrefs](https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/)（2025-07-28）。平均值掩盖引擎差异。
6. **新闻源约占 AI 引用 9%，头部通吃**（B）：AI Search Arena 数据，2.4 万场对话、36.6 万条引用；新闻源占 9%；在 OpenAI 模型的新闻引用中，reuters.com 22.8%、apnews.com 12.2%。来源：[arXiv 2507.05301](https://arxiv.org/abs/2507.05301)（单作者预印本）。这两个比例是新闻引用内部的份额。
7. **引用半衰期**（C / B）：SSRN 7344201（Tandeep Sangra，2026-08-20）综合 Scrunch、Digital Authority Partners 等数据，给出中位 4.5 周、ChatGPT 3.4 周、Perplexity 5.8 周；它是二手综合，不是一手测量（[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7344201)）。Profound 用 88.3 万个页面、7 个引擎、2025-09-08~2026-09-08 的数据，给出峰值后中位 11 天减半（[Profound](https://www.tryprofound.com/blog/the-half-life-of-an-ai-citation-is-11-days)）。两说并记。
8. **ChatGPT 非英语会话会用英语子检索**（B，工具商遥测）：1,000 万+ prompt、2,000 万+ fan-out；非英语 prompt 的子检索 43% 用英语；约 78% 的非英语会话至少有一次英语子检索。来源：[Peec AI](https://peec.ai/blog/chatgpt-searches-in-english-even-when-you-don-t)，2026-02。样本是工具商客户面板。
9. **提问语言改变引用池**（C，翻译服务商研究）：用日语提问时 26% 的被引来源在 .jp 域，用英语提问约 1%（计入全球平台上的日语页面则是 35% 对 1.3%）。来源：[Weglot](https://www.weglot.com/blog/ai-search-citations-language-country)，2026-09-08 更新。
10. **翻译版本与 AIO 可见度**（C，翻译服务商研究）：130 万条引用；对「原站没有的那种语言」的查询，翻译过的站 AIO 可见度比未翻译站高（最多）327%。来源：[Weglot](https://www.weglot.com/blog/multilingual-seo-ai-visibility)，2026-08-10 更新。只能写成「翻译商报告的相关性」。机器翻译的政策风险看 Google 规模化内容滥用政策；LLM 引擎对机翻是否降权，暂无一手证据。
11. **中文区黑产警示**：2026 年央视 3·15 晚会曝光「AI 投毒」；违规机构承诺「4 小时被头部大模型检索」、批量发布数千至数万篇内容（[新华网转北京商报](https://www.news.cn/digital/20260408/c1ef4fac451c456f934fd97e333723fd/c.html)，2026-04-08）。这是风险警示，不是 GEO 功效证据。
12. **国内 GEO 团体标准已立项**：《生成式引擎优化（GEO）可信信息传播与信息生态治理规范》2026-04-10 通过立项评审，由中国新闻技术工作者联合会主持，重点防范「语料投毒」（[转载新华网](https://www.sohu.com/a/1015501700_122526825)，2026-04-28）。立项不等于发布。
13. **中文引擎信源只作数据观察**：CN-GEO 数据集 v2.0.1（2026-07-14）里，腾讯元宝网页版第一信源是 qq.com（20.5%），豆包手机版第一信源是 iesdouyin.com（28.1%）（2026-10-21 用公开的 `source_visibility` 表复算）。这是公开数据集的观察，不是平台官方说明；细节见 [chinese-ai-search-guide.md](chinese-ai-search-guide.md)。

---

## 七、2026-Q3 学术修正批次（论文全部在 arXiv 核读，2026-10-18 复核）

### 修正条目

1. **页面级 AEO 手段的「正效应」在域名固定效应下反转或归零**（B，预印本）：[arXiv 2609.35077](https://arxiv.org/abs/2609.35077)（Ben Moore、Liam Dunne，2026-09-28；数据来自 AEO 代理商 Discovered Labs 的监测平台）。约 200 万条引用，来自 ChatGPT、Claude、Google AI Overviews、Gemini，历时约 6 个月；19 个 B2B SaaS 工作区；60+ 特征；九方法共识框架。主导变量是提示-内容对齐（Jaccard，β=+0.37，95% CI [0.33, 0.41]）；域名级 AI 权威的平均绝对 SHAP 约为最强非对齐页面特征的 6 倍（作者注明这是上界：域名是跨页共享的特征，天然吸收更多方差，不是同口径的效应比较）。
   全文要点（[HTML v1](https://arxiv.org/html/2609.35077v1)）：
   - 样本只含被引 ≥2 次的 URL（10,042 页），因变量 log₂(1+引用次数)。研究「被引多少」，回答不了「会不会被引」。主模型只含品牌自有页与竞品页（N=4,015 页 / 297 个域）。
   - 清单类信号只在第三方页面上测得：FAQ 段 β=+0.07、TLDR/BLUF +0.05、作者简介 +0.02（加内容深度控制后消失）；作者原话是效应「一致地很小」。Schema 结论只覆盖第三方页面（品牌页 JSON-LD 抽取失败）。真实用户 CWV 与 Lighthouse 分数加域名控制后不显著；页速在合并数据里是负相关（大品牌页面偏慢、被引又多）。
   - 页面级可动空间有限：只放域名 R²=0.320，全部特征 R²=0.450，ΔR²=0.130（正文数；附录表 6 把全特征写成 0.388，论文内部不一致）；扣除域名后页面级方差约占 14%。作者自己认为 ΔR² 对营销科学并不小，引用时两面都写。
   - 跨期预测不可迁移：用 2026-04-01 前的数据训练、预测 4 月，样本外 r²=0.018；对齐系数 +0.61 → +0.34，同号；页龄系数 +0.323 → −0.136，翻号。
   - 其他系数（正文数）：定价页 +0.39（附录表 1 写 +0.423）；页长 +0.13、标题-提示相似度 +0.09（作者称这类相似度是上界；附录表 1 写 +0.036 与 +0.114，论文内部不一致，引用时写明）；榜单类页面（listicle +0.048、listicle review +0.026）不显著；对齐系数在五种子集定义下，从竞品页 +0.31 到自有品牌页 +0.77。
   - 引擎差异：被引内容中位年龄从 Claude 5.1 个月到 ChatGPT 8.0 个月；品牌自有与竞品页的 URL 份额 Gemini 13.8%、ChatGPT 39.3%；23,908 条第三方 LinkedIn 引用中 96.6% 来自 Google AI Overviews，Gemini 为 0。
   - 边界：Perplexity 因样本量小被排除；提示词由该公司分析师手写；数据集不公开，只公开分析管线。该公司研究摘要页（[discoveredlabs.com](https://discoveredlabs.com/research/what-drives-ai-citations)）把清单类信号写成「real, measurable gains」，与论文摘要的「reverse or collapse to zero」不一致；引用以论文为准。
2. **GEO 原文增益只在固定上下文内成立**（B，单作者预印本）：45 篇研究的批判综述（2023-11~2026-07 发表窗）。最可复现的杠杆是主题相关性与上下文位置；通用启发式跨平台迁移性差；竞争会侵蚀个体收益；面向引用的改写可能损害检索。总判定：已被检索的内容可以因果地改变自己被引用的方式，但没有一项技术显示对自然可发现性或下游行为的稳定、纵向、跨平台因果效应。来源：[arXiv 2607.14035](https://arxiv.org/abs/2607.14035)，2026-07-15。
3. **提示词集与权重定义「答案市场」**（B，方法论预印本）：可见性分数由提示词集和权重共同决定，不必代表真实需求；提示措辞会改变检索与答案；用 LLM 判分时，判分指令本身会改变同一答案的得分。框架五要素：情境标注、提示表述、执行条件、权重、判分规则；权重未知时报告「可容许分数集」。作者自述没有新实验；与第 2 条综述同一位作者（Olivier Martinez）。来源：[arXiv 2609.06811](https://arxiv.org/abs/2609.06811)，2026-09-06。本套件的 citation_panel 采样同样受此约束：先冻结问题集、带口径、不跨面板比较。

### 新入库

4. **部分 AI 助手不读 robots.txt 或用通用 UA**（B）：10 个带联网检索的 AI 助手；先找出真正产生抓取的配置并记录 UA，再跨 4 种 robots 条件做 200 次试验，用服务端日志和页内密钥区分「真实抓取」与「答案内容」。部分助手按规则执行；另一些未请求 robots.txt 就访问受限资源，或用通用 UA；抓取与答案可以背离。来源：[arXiv 2607.14447](https://arxiv.org/abs/2607.14447)，2026-07-16（v2 07-19）。结论只支撑「robots.txt 不是 AI 抓取的可靠执行边界，敏感内容要用认证或服务端控制」。
5. **agent-ready 改版让浏览器 agent 成功率 49.3% → 89.3%**（B，初步证据）：同一电商原型站的两个版本；GPT-4.1、Gemini-2.5 Flash、Grok-4 Fast × 5 个任务，共 300 次运行；严格成功 134/150 vs 74/150；PARTIAL 43 → 3；平均步数 9.31 → 6.49。来源：[arXiv 2607.12056](https://arxiv.org/abs/2607.12056)，2026-07-13。这是「同一站改版前后」，不是任意站可达水平。
6. **对话内引用捕获（理论）**（A，HAI '26）：多轮对话里早被引用的来源更可能再被引用；用 Pólya 罐过程证明单轮评估下反馈项为零；模型推演中 10 轮内复利比超过 2，单轮与轨迹排序只弱一致（Kendall τ=0.4）。来源：[arXiv 2609.40069](https://arxiv.org/abs/2609.40069)，2026-09-30。>2 是推演值，不是实测。
7. **GEO 痕迹检测**（B）：GEOFlagBench 有 3,200 条内容 × 400 个查询 × 4 个领域 × 8 类优化器；最强基线 F1 0.880；IPT 训练让 ModernBERT 的 F1 从 0.862 升到 0.944、最差组准确率从 0.725 升到 0.883。在 1,000 条真实查询的 Google Search 与 Gemini 接地结果（10,095 页）上，GEO 痕迹占比估计 8.90%，2026 年改过的页面里 16.36%。来源：[arXiv 2608.16824](https://arxiv.org/abs/2608.16824)，2026-08-17（v2 08-20）。
8. **只以排序为目标会降低内容质量对齐**（A，COLM 2026 接收；仿真）：rank-citation AUC 0.853±0.093（六个领域）；20 轮改写后，六个领域的质量-排序对齐度都下降（Spearman ρ 变化 −0.107 ~ −0.018，均值 −0.068）；随机目标对照显示原因是向排序激励适应。来源：[arXiv 2608.30466](https://arxiv.org/abs/2608.30466)，2026-08-31。
9. **记录越薄，引擎幻觉越多**（B）：28 场冲突 × 5 个答案引擎，5,460 个回答对照证据评分；可检索记录越薄，引擎越常编造、错记归属和数字；对 1,048 个被引来源站的分析显示 GEO 来源优化已经出现。来源：[arXiv 2607.14197](https://arxiv.org/abs/2607.14197)，2026-07-15（v2 2026-10-02）。领域是冲突议题，幻觉率不外推。

12. **同站内比，只有「标题和段落对上用户问法」和引用相关；FAQ 块、结构化数据、摘要框、页速只在跨站比较时显得有效**（B，预印本）：[arXiv 2610.15033](https://arxiv.org/abs/2610.15033)（Mahe Chen、Nick Koudas，多伦多大学，2026-10-10；公开数据和代码）。两个 90 天的商业问题答案集，共 158,099 个答案、468,037 条引用：美国家庭宽带（大品牌主导；651 个问题、143,249 个答案）和小型 B2B 软件细分市场（55 个问题、14,850 个答案）。
   - 同站固定效应：标题匹配问题每 1 个标准差 +14.1%（B2B 市场 +26.4%），最佳段落匹配 +15.5%（+12.9%）；FAQ 块跨站 +18.1%、同站 −3.4%（B2B：+22.5% / −1.9%）。站内页面属性能解释的差异很少。
   - 把问题重放给引擎 API：ChatGPT 引用的每一页都是它自己那次搜索取回的；它每次都改写子查询，和 Google、Bing 的结果很少重合；「被检索到」解释的差异远大于页面属性（32% 对 2.8%）。内容主要通过「在语义上对上引擎改写的查询」起作用。
   - 模型先验：ChatGPT 会把它认识的品牌写进搜索词、偏好它认识的网站、在没有支撑页面时也点名品牌；受控实验里，事实完全相同的商品换个品牌名，排序就变。原文一句话：页面被搜到才被引，品牌被记住也会被点名。
   - 局限（作者自述）：都是相关性；页面在收集结束后只下载一次，约三分之一被引 URL 没法分析；重放用的是 API，不一定等于消费者产品；Perplexity 没能重放；只有两个英文商业市场。
   - 与本库的关系：和第 1 条（[arXiv 2609.35077](https://arxiv.org/abs/2609.35077)，域名固定效应下清单类信号归零）同向，是第二条独立数据；和第八节「通用 Schema 无独立效应」同向。和第 11 条（GEO-SFE 结构工程 +17.3%）冲突，引用第 11 条时并读本条。
13. **先诊断「为什么没被引」再定向修改，比通用改写有效；通用优化可能伤害长尾内容**（B，预印本）：[arXiv 2603.09296](https://arxiv.org/abs/2603.09296)（Zhihua Tian 等，2026-03-10）。提出第一份按引用流水线各阶段划分的「引用失败模式」分类；AgentGEO 按分类诊断、从工具库选修复、迭代到被引为止；另建以文档为中心、在留出查询上检验泛化的基准。结果：只改 5% 内容，引用率相对提升 40% 以上，基线方法约 25%；部分文档的问题不是改内容能解决的。局限：实验环境里的引擎和查询集，不是生产引擎的长期观测；「相对提升」不能换算成真实流量。用法：支持本套件「先查失败原因（没被检索到 / 被检索到没被选中 / 被选中没署名）再改」的做法，不支持「批量套用改写模板」。

### 回声补录

10. **「best-of」清单页约占全部引用 21%**（B，厂商数据）：Ranqo 平台 10 万+ 条回答 × 100+ 品牌（2026-03~05）；引用约 78% 落在公司官网；非公司来源中 YouTube 领先；首次可见度三级：知名品牌 73% / 中坚 44% / 长尾 11%；情感正负翻转频率是「是否被提及」的 6.7 倍。来源：[arXiv 2606.20065](https://arxiv.org/abs/2606.20065)（Pratyush Kumar，2026-06-18）。引用必须带厂商名与样本框。
11. **结构特征工程自称引用率 +17.3%**（B）：GEO-SFE 把结构拆成宏观、中观、微观三层，在六个引擎上实验，引用率 +17.3%、主观质量 +18.5%。来源：[arXiv 2603.29979](https://arxiv.org/abs/2603.29979)，2026-03-31。它与第 1 条（生产数据 + 域名固定效应）和第 12 条（同站比较下 FAQ、摘要框等无效应）直接冲突；引用 +17.3% 时必须并读第 1、12 条。

---

## 八、Schema/FAQ 对 AI 引用的独立效应（三条独立证据）

> 三条证据设计不同（域名固定效应观测 / 匹配双重差分 / 按查询聚类的 GEE），结论同向：**通用 Schema 对 AI 引用没有可测的独立效应**。

1. **（B）新加 JSON-LD 的页面，AI 引用没有可测提升**：Ahrefs 从爬虫 HTML 历史里找出 2025-08~2026-03 新加 JSON-LD 的 1,885 个页面；每页配 3 个不同域、此前引用水平相近、从未加过 JSON-LD 的对照页（约 4,000 页）；比较加标记前后各 30 天。匹配双重差分：AI Overviews −4.6%（显著，但两组加标记前已同步下滑）、AI Mode +2.4%（不显著）、ChatGPT +2.2%（不显著）；另做 t 检验、事件研究、换窗口 DiD，方向一致。600 万 URL 的合并观察里，被引页带 JSON-LD 的比例约为未被引页的 3 倍——这正是混杂相关。来源：[Ahrefs](https://ahrefs.com/blog/schema-ai-citations/)（2026-05）。局限：样本是 2025-02 已有 100+ 次 AIO 引用的页面，回答不了「未被引的页面加 Schema 有没有用」；所有 Schema 类型合并估计；观察窗 30 天；加 Schema 的页面常同时改了别的东西。
2. **（B，单作者小样本）通用 Schema 无效应，填了具体属性的 Product/Review Schema 是唯一例外**：ChatGPT（GPT-4o 联网）与 Gemini（1.5 Pro 接地）× 75 个商业查询，730 条引用、1,006 个页面（同查询 Google 前 10 作对照）。合并分析得出 Schema 与被引显著负相关（OR=0.546），作者查明是对照组构造的伪影；按查询聚类的 GEE 中，Schema 有无（OR=0.678，p=.296）、实体丰富度、Schema-查询对齐都不显著。最强预测项是 Google 自然排名：第 1 位 43% → 第 7 位 5%，每降一位被引几率约 −24%。填了价格、评分、规格的 Product/Review Schema 页被引率 61.7%，通用类型 41.6%（p=.012），DR≤60 的域更明显。来源：[SSRN 6284518](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6284518)（Kurt Fischman，2026-02-20，Zenodo 预印本）。只支持「产品页把价格、规格写进 Product/Offer 字段值得做」。
3. **（C）实时抓取阶段，主流 AI 助手只读可见内容**：searchVIU 建了一个测试页，把 8 个价格分别放在可见 HTML、JS 渲染、纯 JSON-LD、隐藏 Microdata/RDFa 等位置；2025-10-30 测 ChatGPT、Claude、Gemini、Perplexity、Google AI Mode。没有一个系统读出只在 JSON-LD 或隐藏标记里的价格。实时抓取时只有 Gemini 读出 JS 渲染的价格；Perplexity 与 AI Mode 走索引，入索引后也读出了这个价格；Claude 8 个价格都没读出。来源：[searchVIU](https://www.searchviu.com/en/schema-markup-and-ai-in-2025-what-chatgpt-claude-perplexity-gemini-really-see/)。局限：单页、厂商自测；作者写明走搜索索引的产品（AIO、Copilot）可能在索引阶段用到 Schema。

**合并口径**：

- 不为 AI 引用新增或扩写 Schema（含 FAQPage）。已有的、与可见正文同源的保留：它还服务知识图谱、语音、实体识别等消费者（处置同 [deprecated-signals.md](../technical/deprecated-signals.md) FAQPage 行）。
- 可见的 FAQ 段落可以写，前提是回答真实问题，见 [citability-scoring.md](citability-scoring.md)「FAQ 是条件件不是标配」。
- 页面级投入顺序：提示-内容对齐（买家原话进标题、首段、小标题）→ 页面类型（定价页、对比页）→ 清单类信号。站外的域名权威排在所有页面级动作之前。
- 产品页例外：价格、规格、评分写进 Product/Offer 字段，同时在正文可见。证据只有第 2 条一项小样本。
- 第 2 条是预印本，60 天内复查有无正式发表版本。
