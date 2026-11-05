# 信源监控体系(如何持续领先)

> 建立于 2026-10-10;2026-10-21 逐个打开链接重核;复核于 2026-11-05(注册表扩到 29 个源,第五节写回放结果)。用途:回答「要持续更新本套件,该盯哪些信源」。分四层:官方 → 研究数据 → 社区与本地 → 竞品前沿,各带频率与抓取方式。
> 类型标签:**官方** = 搜索引擎、标准组织或平台的一手页面;**论文** = arXiv/SSRN 原文;**第三方** = 行业媒体、厂商研究、社区、GitHub 项目(只当线索,采纳前回到官方文档核对)。
> 注册表(`scripts/intel_check.py` 的 `SOURCES`)当前登记 **29 个源**(2026-11-05 加 9 个,见第五节「2026-11-05 扩源」);本文表格里写「注册」的行就是其中之一。

## 一、必盯官方层(信号价值最高,变动 = 套件规则要改)

| # | 源 | 类型 | 频率 | 方式 | 变了影响什么 |
|---|---|---|---|---|---|
| 1 | [Search Central Blog](https://developers.google.com/search/blog)(RSS: /blog/feed.xml)注册 `google-blog` | 官方 | 周 | RSS | 核心更新、新功能 → 全部模块 |
| 2 | [Search 文档更新记录](https://developers.google.com/search/updates)注册 `google-updates` | 官方 | 周 | 页面 diff | 文档级变更 → 技术审计规则 |
| 3 | 旧 `support.google.com/webmasters/announcements` 页面返回 404(核对 2026-10-21),改看第 1 行 Blog RSS(注册 `gsc-announce` 与 `google-blog` 共用同一个 feed) | 官方 | 月 | RSS | Search Console 新功能(如生成式 AI 报告)→ 监控层 |
| 4 | [Search Status Dashboard · Ranking](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history)注册 `status-dashboard` | 官方 | 事件 | 页面 hash | 算法与事故时间线 → 算法归因 |
| 5 | [Lighthouse releases](https://github.com/googlechrome/lighthouse/releases)注册 `lighthouse` | 官方 | 月 | GitHub Atom | 新审计类别(如 Agentic Browsing,见 v13.x 更新说明)→ agent-readiness |
| 6 | [Bing Webmaster Blog](https://blogs.bing.com/webmaster)(RSS)注册 `bing-wm` | 官方 | 月 | RSS | Bing 新报告(2026-02-10 公测的 [AI Performance](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/))→ 测量层 |
| 7 | [OpenAI bots 文档](https://developers.openai.com/api/docs/bots)注册 `openai-bots`;[RSS](https://developers.openai.com/api/docs/bots/rss.xml)注册 `openai-bots-rss` | 官方 | 不定期 | hash + RSS | UA / IP 段 / robots 规则 → 爬虫政策 |
| 8 | [ARD 规范](https://github.com/ards-project/ard-spec)(Agentic Resource Discovery,规范 v0.91)注册 `ard-spec` | 官方(规范仓库) | 活跃 | GitHub Atom | agent 资源发现协议 → agent-protocols |
| 9 | [WebMCP](https://webmachinelearning.github.io/webmcp)(W3C Web Machine Learning 社区组草案,不是 W3C 标准) | 官方(草案) | 月 | 页面 diff | 页面工具协议 → agent-readiness |
| 10 | [Anthropic 爬虫说明](https://privacy.claude.com/en/articles/8896518)注册 `anthropic-crawl` | 官方 | 不定期 | hash | Claude bot 行为 → 爬虫政策 |
| 11 | [Schema.org releases](https://schema.org/docs/releases.html)注册 `schema-org`(最新 V30.1,发布日 2026-09-16) | 官方 | 半年 | hash | 词汇变更 → schema 模块 |
| 12 | [CrUX 发布说明](https://developer.chrome.com/docs/crux/release-notes)注册 `crux`(BigQuery 数据集每月第二个周二更新,页面原文) | 官方 | 月 | hash | CWV 口径 → cwv-playbook |
| 13 | [Cloudflare Radar · AI Insights](https://radar.cloudflare.com/ai-insights) | 第三方(平台数据) | 周 | API / 页面 | AI bot 流量趋势 → 日志分析;脚本直接请求返回 403,用浏览器或官方 API |
| 14–15 | [StatCounter 搜索引擎份额](https://gs.statcounter.com/search-engine-market-share)注册 `statcounter-search`、[AI chatbot 份额](https://gs.statcounter.com/ai-chatbot-market-share)注册 `statcounter-ai` | 第三方 | 日 | 页面 hash | 份额数字 → 各市场门户 |
| 16–18 | [Yandex Webmaster 新功能](https://yandex.com/support/webmaster/ru/new-features)注册 `yandex-wm`(访问时跳转到英文帮助首页)、[Naver Search Advisor](https://searchadvisor.naver.com/)注册 `naver-wm`、[百度搜索资源平台](https://ziyuan.baidu.com/)注册 `baidu-ziyuan` | 官方 | 月 | hash | 三个引擎的生态 → 对应市场 |
| 19 | StatCounter 国家页 × 5(RU / KR / CN / JP / US) | 第三方 | 周 | 抓取 | 市场门户数字 |
| 20 | [robots.txt 标准 RFC 9309](https://www.rfc-editor.org/rfc/rfc9309) | 官方(IETF) | 年 | 手工 | 爬虫政策底层 |
| 21 | [Search 文档更新 RSS](https://developers.google.com/search/updates/search_docs_updates.rss)注册 `google-docs-rss`(与第 2 行同源,逐条给标题,比整页 hash 少误报) | 官方 | 周 | RSS | 同第 2 行 |
| 22 | [Search Engine Roundtable RSS](https://www.seroundtable.com/index.xml)注册 `seroundtable` | 第三方 | 日 | RSS | 论坛震荡、算法异常、GSC bug 的最早信号 |

注:
- 旧「ranking updates history」页已下线,改看第 1 行 Blog 与第 4 行 Dashboard。
- StatCounter 图表页由 JavaScript 渲染,服务端 HTML 每次拉取都在抖;`intel_check` 对 hash 源做**二次拉取确认**(两次一致才算变更,抖动按噪音跳过)。StatCounter 的 CSV 端点(`chart.php?csv=1`)实测返回空数据,不可依赖。
- Reddit 的 `top.json` 对无登录脚本返回 403(核对 2026-10-21)。r/TSEO 这类社区信号改用网页浏览或授权 API。

## 二、研究与数据层

**论文**(arXiv 周扫):检索式 `cat:cs.IR AND (all:"generative engine optimization" OR all:"answer engine optimization" OR abs:"LLM citation" OR abs:"visibility in AI search")`。已核对的脉络(核对 2026-10-21):

| 论文 | 类型 | 链接 |
|---|---|---|
| GEO: Generative Engine Optimization(2023-11-16) | 论文 | [arXiv:2311.09735](https://arxiv.org/abs/2311.09735) |
| E-GEO: A Testbed for Generative Engine Optimization in E-Commerce(2025-11-25) | 论文 | [arXiv:2511.20867](https://arxiv.org/abs/2511.20867) |
| Optimizing Visibility in Generative Engines: A Critical Survey of GEO (2023-2026)(2026-07-15) | 论文 | [arXiv:2607.14035](https://arxiv.org/abs/2607.14035) |
| Measuring Entity Citation in Generative Engines(BRGEO-1 协议) | 论文(SSRN 预印本) | [SSRN 7446519](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7446519) |

排行榜 [generative-engines.com](https://generative-engines.com/)(第三方)。会议(SIGIR / WWW / WSDM / ACL)每年 5–7 月会后扫一次。

**数据研究团队**(都是第三方研究:样本和口径各家不同,采纳数字前读方法节,并写明样本与日期):

| 源 | 系列 | 类型 | 频率 | 抓什么 |
|---|---|---|---|---|
| [Ahrefs](https://ahrefs.com/blog) | Data Studies | 第三方 | 2–4 月/篇 | AI Overviews 对点击的影响:2025-04 研究为 −34.5%(30 万词),2026-02 更新为 −58%([更新文章](https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/)) |
| [Semrush](https://www.semrush.com/blog) + [Sensor](https://www.semrush.com/sensor/) | 研究 / 日更波动 | 第三方 | 月 / 日 | AIO 触发因素;SERP 波动分(0–10,[说明](https://www.semrush.com/kb/652-sensor)) |
| [Sistrix](https://www.sistrix.com/blog) | 博客研究 | 第三方 | 1–2 月 | 德语区搜索与 AI 搜索研究 |
| [Conductor](https://www.conductor.com/academy) | AI 引用研究 | 第三方 | 季 | 引用对流量的影响 |
| [BrightEdge](https://www.brightedge.com/resources/research-reports) | 报告 | 第三方 | 月 | AI 引荐趋势 |
| [Profound](https://www.tryprofound.com/blog/the-half-life-of-an-ai-citation-is-11-days) | 厂商研究 | 第三方 | 不定期 | 引用半衰期:12 个月、88.3 万页,中位 11 天(2026-09-30 博文) |

## 三、社区与 18 市场本地层

**英文社区**(第三方):r/bigseo(月,网页)、Hacker News(`hn.algolia.com/api/v1/search?query=...`,关键词 "AI Overviews"、"llms.txt"、"Perplexity",周)。三家媒体分工不重叠:[Search Engine Land](https://searchengineland.com/feed)(官方公告解读,日 RSS)/ [SEJ](https://www.searchenginejournal.com/feed/)(方法论长文,日 RSS)/ Search Engine Roundtable(论坛震荡、算法异常、GSC bug,日 RSS,注册为 `seroundtable`)。

**中文圈**(第三方):[SEO每天一贴 · Zac 昝辉](https://www.seozac.com/)(旧文写成 zaccode.com,该域名无法连接,已改)、[站长之家新闻](https://www.chinaz.com/news)(日,常转载 AI 搜索报告)、[5118 博客](https://www.5118.com/);官方最重要的是 [百度搜索资源平台](https://ziyuan.baidu.com/)。

**18 市场本地信源**(每市场至少 1 个;兜底 = Google Search Central Blog 对应语言版 RSS):

| 市场 | 信源(类型) | 市场 | 信源(类型) |
|---|---|---|---|
| ja | [suzukikenichi.com](https://www.suzukikenichi.com/blog/feed/)(第三方)、[Web担当者Forum](https://webtan.impress.co.jp/)(第三方) | fr | [Abondance](https://www.abondance.com/)(第三方) |
| ko | [Naver Search Advisor](https://searchadvisor.naver.com/)(官方) | it | [GT Giorgio Taverniti](https://www.giorgiotave.it/)(第三方) |
| ru | [Searchengines.guru](https://searchengines.guru/ru/articles)(第三方) | nl | [Frankwatching](https://www.frankwatching.com/)(第三方) |
| de | [Sistrix 博客](https://www.sistrix.com/blog)德区研究(第三方) | es | Google Search Central 西语版 + Sistrix 西班牙研究(官方 + 第三方) |
| 其余 | Google Search Central Blog 对应语言(RSS)+ 周扫该语种 `site:` 报道 | | |

旧文提到的 brunch「검색엔진 최적화」页没有可核对的链接,已删。以上链接 2026-10-21 打开:`webtan.impress.co.jp` 和 `frankwatching.com` 对脚本请求返回 403,用搜索 MCP 的 `read` 能读到正文,链接有效。

## 四、竞品与前沿层(套件进化方向的风向标)

**GitHub 观察名单**(第三方;★ 与最近 push 来自 `gh api repos/<owner>/<repo>`,核对 2026-10-21。数字每天在变,采用时重查):

| 仓 | ★ | 最近 push | 信号 | 频率 |
|---|---|---|---|---|
| coreyhaines31/marketingskills | 55.6k | 2026-10-19 | 功能最全的对标 | 周 |
| every-app/open-seo | 24.3k | 2026-10-20 | 商业化路径;issue 即路线图 | 周 |
| Albert-Weasker/niubigeo | 8.4k | 2026-10-10 | 2026-09-03 创建,增速最快;AI 品牌可见性报告 | 周 |
| zubair-trabzada/geo-seo-claude | 11.1k | 2026-10-20 | GEO 方向 | 月 |
| AgriciDaniel/claude-seo | 19.5k | 2026-10-04 | 子技能扩张 | 双周 |
| jianruntech/geo-score | 0.3k | 2026-10-19 | 评分学演进 | 双周 |
| TheCraigHewitt/seomachine | 7.5k | 2026-10-15 | 内容工作流 | 季 |

新仓扫描(双周):GitHub 搜索 `q=seo+claude+skill+created:>YYYY-MM-DD&sort=stars`、`q=geo|aeo|ai-visibility in:name,description created:>`、topics `generative-engine-optimization` / `chatgpt-seo`。Awesome 清单订阅 `commits.atom`:[bmpi-dev/awesome-seo](https://github.com/bmpi-dev/awesome-seo)、[amplifying-ai/awesome-generative-engine-optimization](https://github.com/amplifying-ai/awesome-generative-engine-optimization)、[DavidHuji/Awesome-GEO](https://github.com/DavidHuji/Awesome-GEO)(旧文写 "amplifying-ai/bmpi-dev awesome-seo",仓库名不对,已改)。codex-seo 已改名为 [AgriciDaniel/chatgpt-seo](https://github.com/AgriciDaniel/chatgpt-seo)。

**商业产品风向标**(官方公告 + 第三方):
- Search Console 生成式 AI 效果报告:先给部分站点,后对全部站点开放([日期](facts.md#gsc-genai));Search 报告含 AI Overviews 与 AI Mode,Discover 另有独立报告;默认只给展示数(impressions),维度有页面、国家、日期、设备([Search Central 博文](https://developers.google.com/search/blog),[帮助页](https://support.google.com/webmasters/answer/16984139))。
- 2026-09-24 起,效果报告新增「Web: multimodal」搜索类型(Lens、Circle to Search、上传图片、Chrome 右键搜图)([博文](https://developers.google.com/search/blog/2026/09/web-multimodal-in-sc))。
- Google 官方页面写明正在测试 AI Mode 里的广告([Ads in AI Mode](https://business.google.com/us/accelerate/announcements/ads-in-ai-mode/));这会改变 AI Mode 的点击构成,数据层面要关注。
- 厂商 MCP 化:Profound 在 2025-10-15 发布 MCP 服务器([博文](https://www.tryprofound.com/blog/bring-profound-data-directly-into-your-ai-workflow-with-mcp));竞品重心从 SEO 审计转向 AI 可见性监测加 MCP,是第三方观察。

**风险信号(防套件建议过时)**:
- Google 垃圾内容更新 2026 年共 4 次:03-24、06-24、08-18、09-24(Status Dashboard 的 Ranking 历史页)。核心更新 2026-03-27、2026-05-21。
- 垃圾内容政策页现在写明:试图操纵 Google 搜索里的生成式 AI 回答也属于 spam([spam policies](https://developers.google.com/search/docs/essentials/spam-policies),页面日期 2026-08-28)。文档更新记录 2026-05-15 有单列条目「Clarifying that spam policies apply to generative AI responses in Google Search」(旧版写「没有单列、不写日期」是错的,2026-11-05 更正)。2026-04-14 起垃圾举报可能直接触发人工操作(04-23 补充),见 [penalty-recovery.md](../monitoring/penalty-recovery.md) 1.1。
- 2026-08-28 站点声誉政策更新,内容是调整欧洲经济区内的执法方式([文档更新记录](https://developers.google.com/search/updates))。
- AI 内容检测的进展会影响「人类化改写」类建议的有效期,每季复核一次(本套件口径)。

**跨行业泛信号**(第三方观察,3–5 个):AI 浏览器与浏览器内 agent(Comet、Dia;Chrome 里的 Gemini 和 auto browse,见 [agent-growth-loop.md](../monitoring/agent-growth-loop.md) 第八节)、操作系统级 agent、搜索入口变化。ChatGPT Atlas 已停服:OpenAI 2026-07-09 在 ChatGPT 发布说明里宣布弃用,浏览器类 agent 能力并入 ChatGPT 和 Codex,2026-08-09 停止工作;帮助页「ChatGPT Atlas retirement」写明已退役、不再更新([发布说明](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)、[退役说明](https://help.openai.com/en/articles/20001371-chatgpt-atlas-retirement),核对 2026-11-05)。日志里还看到 Atlas 的 UA 属于残留安装,不再作为 AI 浏览器流量的代表样本。

## 五、信源 → 套件模块映射(哪个信源变了改哪个文件)

下表与 `scripts/intel_check.py` 的 `SOURCES[...]["modules"]` 一致(核对 2026-11-05;`tests/test_intel_sources.py` 检查每个模块文件都存在)。路径都在 `references/` 下。

| 注册名 | 更新模块 |
|---|---|
| google-blog | content/geo-evidence.md、technical/validation-guide.md、content/llms-txt-guide.md |
| google-updates、google-docs-rss | technical/validation-guide.md、technical/audit-rule-catalog.md |
| gsc-announce | overview/intake-checklists.md、monitoring/kpi-definitions.md |
| status-dashboard、semrush-sensor | monitoring/seo-drift-monitoring.md |
| lighthouse、ard-spec | technical/agent-readiness.md、technical/agent-protocols.md |
| openai-bots、openai-bots-rss、anthropic-crawl | technical/ai-crawler-policy.md |
| bing-wm、statcounter-ai | content/geo-platform-differences.md |
| schema-org | technical/schema-templates.md、technical/schema-examples.md |
| crux | technical/cwv-playbook.md |
| yandex-wm | markets/ru.md |
| naver-wm | markets/ko.md、technical/naver-searchadvisor.md |
| baidu-ziyuan | markets/zh.md、content/chinese-ai-search-guide.md |
| statcounter-search | overview/multilingual-workflow.md |
| seroundtable | monitoring/penalty-recovery.md、technical/rendering-seo.md |
| chrome-blog | technical/cwv-playbook.md、technical/agent-readiness.md、technical/agent-protocols.md、monitoring/agent-growth-loop.md |
| web-dev-blog | technical/cwv-playbook.md、technical/rendering-seo.md |
| cloudflare-blog(关键词) | technical/ai-crawler-policy.md、technical/agent-protocols.md |
| openai-news(关键词) | technical/ai-crawler-policy.md、content/geo-platform-differences.md、content/ecommerce-geo-ladder.md、overview/intel-sources.md |
| bing-search-blog | technical/ai-crawler-policy.md、content/geo-platform-differences.md、content/ecommerce-geo-ladder.md |
| msads-blog(关键词) | content/ecommerce-geo-ladder.md、technical/agent-protocols.md |
| google-maps-blog(关键词) | monitoring/local-grid-ranking.md、overview/site-type-playbooks.md |
| google-shopping-blog(关键词) | content/ecommerce-geo-ladder.md |
| arxiv-geo | content/geo-evidence-bank.md、content/citability-scoring.md |

**2026-11-05 扩源。** 起因:RQ-229 补的 12 条 2026 年知识,原来的 20 个源只盯住了 5 条(CrUX 软导航、Google 垃圾政策、平台属性、Google 文档小更新、OpenAI 训练信号经 Google 博客)。新加 9 个源,地址:[Chrome 开发者博客](https://developer.chrome.com/static/blog/feed.xml)、[web.dev 博客](https://web.dev/static/blog/feed.xml)、[Cloudflare 博客](https://blog.cloudflare.com/rss/)、[OpenAI 新闻](https://openai.com/news/rss.xml)、[Bing 搜索博客](https://blogs.bing.com/search/feed)(和 bing-wm 的站长博客不是一个 feed)、[Microsoft Advertising 博客](https://about.ads.microsoft.com/en/blog/rss)、[Google Maps 博客](https://blog.google/products/maps/rss/)、[Google Shopping 博客](https://blog.google/products/shopping/rss/)、arXiv API 按短语 "generative engine optimization" 按提交时间倒序。Search Central 更新记录页原来就在(google-updates 页面 hash + google-docs-rss),没有重复加。
- **关键词过滤**:标「关键词」的源发文多、大半和搜索无关(OpenAI 新闻一天几篇),脚本先看最近 50 条,只留标题或链接命中关键词的条目,最多 5 条;只来了无关文章不算变更。关键词在 `SOURCES[...]["keywords"]`。
- **回放结果(2026-11-05,只读拉取,没写基线)**:12 条里 11 条能被注册表接住(原有源 5 条 + 新源 6 条:Cloudflare 9 月新默认、微软 PCM(第 5 条里的一项)、Copilot Checkout 与 Web IQ、Ask Maps、两篇 GEO 论文、Chrome I/O 工具)。**接不住的 1 条是 ChatGPT Atlas 停服**:只发在 help.openai.com 的发布说明里,该站对脚本请求回 403,OpenAI 新闻 feed 里没有这条;只能靠第三方媒体或人工看发布说明。第 5 条里的 RSL 和 IAB CoMP 也没有可订阅的 feed,只命中了微软 PCM 那一项。
- 回放当场在新源里多看到两条此前没收录的一手公告,已核对原文写进 ai-crawler-policy.md:微软 2026-10-30 训练与 grounding 新偏好(Bing 搜索博客)、Cloudflare 2026-11-04 按单个个人 agent 设访问策略。

注册表之外的信源(论文、竞品仓、行业研究)变动时,改 content/geo-evidence-bank.md、content/geo-platform-differences.md,以及对应能力文件和脚本。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败判据 |
|---|---|---|
| 注册表与本文一致 | `python3 -c "import sys; sys.path.insert(0,'scripts'); import intel_check as i; print(len(i.SOURCES))"`(在 `skills/seo-suite/` 下跑) | 数字等于本文第一段写的 29。不等就同步改本文和 [script-catalog.md](script-catalog.md) |
| 链接没死 | `curl -sIL -m 20 -o /dev/null -w '%{http_code} %{url_effective}\n' <URL>` | 200 通过。403 先换浏览器或 `search MCP read` 复核;404 或连不上就删除或换源 |
| 基线可用 | 首次用 `python3 scripts/intel_check.py init` 建基线;之后连续跑两次 `check` | 第二次无 `[CHANGED]`,退出码 0(1 = 有变更,2 = 错误) |
| 观察名单没改名 | `gh api repos/<owner>/<repo> --jq '[.full_name,.pushed_at]'` | `full_name` 与表一致;不一致就更新表 |
| 数字有日期 | 本文所有 ★、份额、百分比旁边有核对日期或来源链接 | 缺日期的数字删掉或补日期 |

## 来源

2026-10-10 三路调研;2026-10-21 重核:逐个打开本文链接,核对 intel_check 注册表、Status Dashboard 历史页、schema.org 发布页、CrUX 发布说明、arXiv 摘要、GitHub API。
