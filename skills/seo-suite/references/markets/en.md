# 英文市场专项(基线层)

> 英文是基线,本页只收英文区独有的增量。建立于 2026-10-09,2026-10-21 逐条重核:每个数字都回到原始页面或官方文档重读,读不到的删除。
> 基线能力在 [agent-readiness.md](../technical/agent-readiness.md)、[agent-protocols.md](../technical/agent-protocols.md)、[ai-crawler-policy.md](../technical/ai-crawler-policy.md)、[geo-evidence-bank.md](../content/geo-evidence-bank.md)。证据等级以 [geo-evidence.md](../content/geo-evidence.md) 为准;提问对齐见 [question-alignment.md](../content/question-alignment.md);句子写法见 [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md)。
> 标注:【官】=官方页面或文档;【三方】=第三方研究(写机构、样本、时间);【本套件口径】=本套件约定。断言半衰期 3–6 个月(引用份额类 3 个月)。

## 一、引擎与 AI 格局

### 1. 品牌词的 AI Overviews 覆盖在 2026-09 下旬骤增

| 追踪方 | 读数 | 口径 |
|---|---|---|
| DemandSphere【三方】 | 品牌词 AIO 出现率 2026-09-01 为 26.12%;9/1–9/17 在 26–35%;9/18 起波动(57.43%、46.62%、56.97%、55.81%);9/26 69.21%;**9/27 90.48%(月内峰值)**;9/28 80.23%;9/29 82.06% | 每天每词测一次,全市场全设备,出现 AIO 即计(不看是否引用品牌) |
| Ahrefs【三方】 | 2026-09-29 当天美国桌面品牌词 82.91%;月均:7 月 61.3%、8 月 65.1%、9 月 73.3% | 2026-07 至 09 的 2.328 亿条美国桌面 Google 抓取(品牌词 9,250 万条) |
| Chris Long / SerpApi【三方】 | 100 个企业品牌里 93 个出现 AIO | 单次抽测,没有测点击 |

- 来源:[DemandSphere 2026-10-01](https://www.demandsphere.com/blog/branded-ai-overviews-september-2026)、[Search Engine Land](https://searchengineland.com/google-ai-overviews-jump-branded-queries-september-492962)(2026-10)、[Ahrefs](https://ahrefs.com/blog/ai-overviews-on-branded-searches/)。核对 2026-10-21。
- Google 没有公布相关变更。两家追踪器同向,但都不解释品牌词怎么定义,不当成 Google 官方数字。
- 这是**品牌词**口径。全查询口径另有读数:Comscore 报告美国桌面搜索带 AIO 的比例 2025-07 为 25.8%,2026-06 为 39.4%(【三方】[Comscore Q2 2026 AI Intelligence Report](https://www.comscore.com/Insights/Press-Releases/2026/9/Comscores-Q2-2026-AI-Intelligence-Report))。引用任何 AIO 比例,都要写追踪器、月份和查询集。
- 零点击:SparkToro 用 Similarweb 点击流面板,测得美国 Google 零点击搜索 2024 年为 60.45%,两年增加 7.5 个百分点,即约 68%(【三方】[SparkToro 2026-06](https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/))。这不是 Comscore 的数字。
- 做法(本套件口径):品牌词 SERP 审计从季度改月度;品牌词承载页(关于、定价、对比、评价汇总)逐页写清主体、数字、日期和方法;品牌词里出现负面或竞品内容时,只能靠内容和实体信号处理,没有「申诉删除 AIO」的官方通道。

### 2. AI 格局的其他读数

- ChatGPT 每周 12 亿用户(OpenAI DevDay,2026-09-29;【官】[DevDay 2026 recap](https://openai.com/index/devday-2026-recap/))。
- 爬虫构成:Cloudflare Radar 的 2026 Q3 读数经 TechnologyChecker 转引:GPTBot 占 AI 爬虫请求的 8.05%(一年前 12.21%),OAI-SearchBot 翻倍到 2.81%(【三方】[TechnologyChecker](https://technologychecker.io/blog/chatgpt-statistics),未读到 Radar 原始页)。含义:日志里不要用 GPTBot 体积推断引用机会;封训练爬虫时别连带封检索爬虫。
- AIO 与 AI Mode 的社媒链接差:SE Ranking 10 万关键词研究,社媒平台链接出现在 67.66% 的 AIO 回答和 32.39% 的 AI Mode 回答里(【三方】[Social Media Today 2026-10-07](https://www.socialmediatoday.com/news/ai-favors-brands-with-an-active-social-media-presence/832450/) 转述;SE Ranking 原文未读)。

### 3. Google 2026-09 spam 更新

- 【官】[Search Status Dashboard](https://status.search.google.com/incidents/XhUDXP7A67iHCD2kmbVu):2026-09-24 09:15 PDT 发布,2026-10-08 01:00 PDT 结束,全球、全语言。
- 时长 13 天 16 小时,是 2025-08 以来最长(【三方】[PPC Land](https://ppc.land/googles-september-spam-update-ends-after-13-days-as-manual-actions-rise/))。2026 年已有 4 轮 spam 更新:3 月 24–25 日、6 月 24–26 日、8 月 18–21 日、9 月 24 日–10 月 8 日;[Search Engine Roundtable](https://www.seroundtable.com/google-september-2026-spam-update-done-42235.html) 列出的 2025 年只有 8 月 26 日–9 月 22 日一轮。
- 工具侦测到的波动窗口:9/25–27、9/30、10/4–6(Search Engine Roundtable 汇总 14 个工具)。人工处罚增多是 SEO 从业者的反馈,不是 Google 数据。
- 做法:用 Status Dashboard 的时间戳对齐,不用工具波动单方面定性。

## 二、协议层进展(ARD / WebMCP)

基线见 [agent-readiness.md](../technical/agent-readiness.md)。这里只记 2026-10 核到的事实。

- ARD(Agentic Resource Discovery):Google 于 2026-06-17 发布规范(【官】[Google Developers Blog](https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/));Microsoft 的页面写明与 GoDaddy、Google、Hugging Face 等合作开发(【官】[Microsoft](https://commandline.microsoft.com/agentic-resource-discovery-specification-ard/))。机制是站点在 well-known 路径放 `ai-catalog.json`,客户端运行时发现并调用。之前写的「11 厂商共同署名」「NVIDIA」「anti-MCP 联盟」找不到来源,已删。
- WebMCP:Chrome 149 起开放 origin trial(【官】[Chrome 博客 2026-06-09](https://developer.chrome.com/blog/ai-webmcp-origin-trial))。落地样本很少:一个团队在 2026-07 给 4 个生产站点加了只读工具、人工确认表单和机器可读内容索引(【三方】[nz365guy 2026-07-13](https://nz365guy.com/blog/four-websites-agent-ready-webmcp))。「M149–M156」「Edge 平行 trial」「唯一实证消费者是 ChatGPT 桌面浏览器」未找到来源,已删。
- Lighthouse 有 Agentic Browsing 类别(【官】[Chrome 文档 2026-05-05](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring)),可作技术验收。
- 本套件口径:协议层是低成本期权;交付物不能当 KPI 或效果承诺;汇报时写采用现状,验收不承诺引用收益。

## 三、引用份额:先看分母

同一个「Reddit 份额」,三家的分母不同,数字差 20 倍以上。引用前先写分母。

| 来源 | 读数 | 分母 |
|---|---|---|
| Ahrefs Brand Radar,2026-09【三方】 | Reddit 16.8%、Wikipedia 7.0%、Consumer Reports 3.7%、Forbes 3.1% | 美国全主题,ChatGPT 的**头部来源**引用总和([Ahrefs](https://ahrefs.com/blog/most-cited-domains-in-chatgpt/));2026-07 读数 Reddit 16.7% |
| Surfer AI Search Analytics,2026-09-01–28【三方】 | Reddit 占全部 ChatGPT 引用的 0.74%(占 top-50 的 8.82%);50 个头部域名合计只占 8.4% | 约 573 万条 ChatGPT 引用([Surfer](https://surferseo.com/blog/most-cited-domains-chatgpt/)) |
| Promptwatch,2026-08【三方】 | Reddit 在 ChatGPT Search 引用中的份额 2026-07-18–08-07 为 3.83%,08-14–17 降到 0.52%(降 86%);OpenAI 称没有改过选源方式 | ChatGPT Search 全部引用([Search Engine Land 2026-08-19](https://searchengineland.com/reddit-chatgpt-search-citations-fall-report-485473)、[Semrush 转述](https://www.semrush.com/blog/reddits-citations-in-chatgpt-fall/)) |
| 5WPR,2025【三方】 | ChatGPT 的 Reddit 引用份额约 60%→10%(2025-08 至 09 中旬) | 5WPR 报告口径,方法见原文([5WPR](https://www.5wpr.com/research/state-of-ai-citations-2026/)) |

- 结论:Reddit 的 ChatGPT 引用在 2026-08 确有下降(Promptwatch),但「塌陷到 0.5%」「YouTube 取代 Reddit」不能和 Ahrefs 的 16.8% 放在一张表里比。早先文件里「Strivelabs 六研究汇总:YouTube 26.47% / Reddit 17.39%」找不到来源,已删;「Ahrefs 降 86%」是 Promptwatch 的数字,已更正。
- Perplexity:Profound 报告 Reddit 占 Perplexity top-10 来源引用的 46.7%(2025-06 发布,数据区间 2024-08 至 2025-06)(【三方】[Profound](https://www.tryprofound.com/blog/ai-platform-citation-patterns))。这是一年多前的读数,不能写成「仍成立」。
- Google AI Mode:Surfer 2026-09 约 479 万条引用里,google.com 占 13.82%、youtube.com 6.77%、reddit.com 3.17%、facebook.com 0.69%;Google 自有站点占前 50 域名引用的 67.8%(【三方】[Surfer](https://surferseo.com/blog/most-cited-domains-ai-mode/))。
- 引用衰减:GreenFlag 追踪 2025-10 被 ChatGPT 引用最多的 215 个金融类页面,一年后 107 个(50%)零引用,整体只保留约 14% 的引用量(【三方】[GreenFlag 2026-09-21](https://greenflagdigital.com/chatgpt-citation-study/))。Cloro 的 735 条提示篮子里,ChatGPT 引用页面的年龄中位数约 150 天,67% 发布于近 12 个月内(【三方】[Cloro](https://cloro.dev/research/state-of-ai-search))。做法(本套件口径):新鲜度是持续供给,给支柱页排月度增量(新数据加新日期),不做一次性大改。
- 已删:Reddit 高引格式「300–600 词、50+ 赞」(原文是 LinkedIn 文章,读不到方法)、「YouTube+Reddit 占社媒引用 86%」(Slate)、「57% 被引域不会再被引」(digitalapplied)、「发布 <3 个月被引概率 3×」(来源是一篇厂商博客,方法未读到)。

## 四、外链与引用集中度

- 各引擎 top-10 域名集中度(Cloro,735 条提示篮子,【三方】[Cloro](https://cloro.dev/research/state-of-ai-search)):Google AI Mode 25.4%、Perplexity 18.9%、ChatGPT 17.5%、Copilot 14.3%、Gemini 13.8%。Cloro 页面说明这版比早先偏商业的快照更分散,旧文件里的 57.8% / 27.3% / 25.1% / 18.3% / 17.3% 已被取代。
- 大型 UGC 平台(固定 17 个平台名单)在各引擎引用里的占比:AI Mode 19.0%、Perplexity 11.8%、Gemini 5.0%、Copilot 2.4%、ChatGPT 1.7%(同上)。含义:Reddit 帖子、YouTube 视频对 AI Mode 和 Perplexity 有用,对 ChatGPT 几乎是死路。
- 引擎间被引域名重合很低:Bill Widmer 追踪 13,184 条 AI 引用、4 个 LLM(Orbit Media 的 Andy Crestodina 在 LinkedIn 转载),ChatGPT 与 Perplexity 在两个查询集上分别共享 7.6% 和 5.4% 的被引域名(【三方】[LinkedIn](https://www.linkedin.com/pulse/we-tracked-13184-ai-citations-across-4-llms-heres-what-crestodina-ivluc))。做法:每个引擎单独建问题集,单独汇报。
- 数字 PR(本套件口径):先查目标域在目标引擎的在场率,再决定投放,不按传统域名权重(DR)投。
- 已删:Resocial「Wikipedia 32% / Reddit 21%」加权、Posirank/Parse 的「Reddit 代运营机构榜」(两者都读不到方法或原文)。

## 五、AI-GEO 测量

- GA4 在 2026-05-13 公告把「AI Assistant」加进默认渠道组(【官】[What's new in Google Analytics](https://support.google.com/analytics/answer/9164320?hl=en);[SEJ 2026-05-14](https://www.searchenginejournal.com/google-analytics-adds-ai-assistant-as-default-channel-group/574974/))。第三方实测它认得 ChatGPT、Gemini、Claude,认不全 Perplexity 和无 referrer 的访问(【三方】[digitalapplied](https://www.digitalapplied.com/blog/ga4-ai-assistant-channel-2026-measure-ai-traffic-playbook))。做法(本套件口径):先看内置渠道,再和旧自定义渠道组对账,不并行混报两套口径。
- 归因漏损:没有 referrer 的 AI 访问可能记成 Direct(TapClicks 指南原文),所以 AI 流量是下界。「~70% 记成 Direct」这个数字在 TapClicks 页面里读不到,已删。
- ChatGPT 外链常带 `utm_source=chatgpt.com`(【三方】[Seer Interactive](https://www.seerinteractive.com/insights/are-ai-sites-like-chatgpt-sending-your-website-traffic));Perplexity、Gemini 没有对等行为的证据,不要假设对称。
- 品牌词和品类词的 fan-out 分开建问题组(本套件口径)。四级阶梯(retrieved → cited → mentioned → recommended)不变,见 [geo-platform-differences.md](../content/geo-platform-differences.md)。
- 已删:SearchScore「102,873 域指数」(来源页读不到)。

## 六、红旗

- **买「提及」**:Google 的生成式 AI 优化指南写明,寻求「不真实的提及」没有看上去那么有用:核心排名系统看高质量内容,其他系统拦 spam,AI 功能依赖这两者(【官】[AI 优化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide),核对 2026-10-21)。原文没有用「spam 风险」这个词;「买赞、代发评论」属于本套件的风险判断。
- **单平台押注**:5WPR 报告 ChatGPT 的 Reddit 引用份额在 2025-08 至 09 中旬约 6 周内从约 60% 降到约 10%;Promptwatch 报告 2026-08 又有一次下降。份额会在几周内变,押单一被引平台有风险,含 YouTube。
- **llms.txt**:同一份指南写明 Google 不需要 llms.txt;可以为别的系统建,对 Google 可见性既无害也无益。ARD、WebMCP 同理,不当 KPI 卖。
- **数字冲突纪律**:同一指标出现多套读数,客户材料引用任一数字都要带引擎名、月份、分母和来源。
- **AIO 骤增的话术**:承诺能「删除」品牌词 AIO 的供应商,不采用。

## 七、工具

| 工具 | 用途 | 口径备注 |
|---|---|---|
| DemandSphere / Ahrefs | 品牌词 AIO 出现率 | 两家并记,月度重跑 |
| Surfer AI Search Analytics / Cloro / Ahrefs Brand Radar | 各引擎被引域名 | 厂商研究,先看分母 |
| GA4 AI Assistant 渠道 | AI 引荐 | 下界口径 |
| Lighthouse Agentic Browsing | ARD、WebMCP、llms.txt 技术验收 | 免费 |
| Google Search Status Dashboard | spam 与 core 更新时间戳 | 官方 |
| `scripts/citation_panel.py` | 人工采样台账 | 见检查清单 |

## 八、检查清单

| # | 检查什么 | 怎么查 | 通过判据 |
|---|---|---|---|
| 1 | 品牌词 AIO | 列 20–50 个品牌词(品牌名、品牌+定价、品牌+对比、品牌+评价),每月同一天用美国英语无痕窗口查;`python3 scripts/citation_panel.py init --brand B --prompts brand_prompts.csv --engines chatgpt,perplexity,gemini`,每次采样后 `record --engine chatgpt --file run.csv`,`report --brand B` | 每词记 AIO 有无、引用域名、正负面;连续两月同口径可比;负面或竞品内容有处置工单 |
| 2 | AI 检索爬虫放行 | `python3 scripts/robots_posture.py https://site/robots.txt --json` | `visibility_failures` 为空;训练爬虫封不封是授权决策,单独记 |
| 3 | AI 引荐归因 | GA4「报告 → 获客 → 流量获取」,按默认渠道组看是否有 AI Assistant 行;日志侧 `python3 scripts/ai_referral_log.py access.log --classify` | AI Assistant 行存在;日志里 AI 引荐 UA 的失败率先剔除探测路径再算 |
| 4 | 更新对齐 | 对照 Status Dashboard 的开始与结束时间,GSC 比较开始前 14 天与结束后 14 天 | 变化落在窗口内才归因更新;GSC 展示数据在[GSC 数据异常期](../overview/facts.md#gsc-anomaly)里不可比,不跨这段比较 |
| 5 | 引用衰减 | `python3 scripts/citation_panel.py decay --metric cited --engine chatgpt` 每月一次,每个引擎单独判定 | 顶引页面季度流失 ≥30%(本套件口径)时,检查内容更新管线 |
| 6 | 协议层交付 | `python3 scripts/llmstxt.py check https://site`;Lighthouse Agentic Browsing | 交付文档写「已部署」,不写「会带来引用」 |
| 7 | 英文变体 | `python3 scripts/hreflang_cluster.py https://site/en-us/x https://site/en-gb/x`;`python3 scripts/site_audit.py URL --market en` | 簇内互指;`en` 兜底加需要的国家码 |
| 8 | Bing / Copilot 侧 | `python3 scripts/bing_wmt.py stats`(需 API key)与 `pagequery` | 品牌词在 Bing 有数据;GSC 之外的查询有补充 |

## 九、本地实测(2026-10-09,本套件记录)

- 跑了 en.wikipedia.org 与 www.craigslist.org × `site_audit --market en` / `llmstxt check` / `head_check`;ebay.com、etsy.com 主页对审计 UA 返回 403。
- wikipedia:首页无 meta description、2 个 H1、alt 缺 5/23;四条 AI 检索爬虫放行;`/llms.txt` 404。craigslist:title 83 字符超出 60、2 个 H1、h1→h4 跳级、html 无 lang;AI 爬虫放行;`/llms.txt` 404。etsy:`/llms.txt` 返回 200 且首行是「# Etsy: official reference for AI assistants」(2026-10-09 读到;每季抽查)。
- **脚本口径 2026-10-21 已改**:缺 H1、缺 description 记 WARN(不再是 CRITICAL);`head_check` 里 twitter:* 与 OG 重复只记 INFO(不是弃用),`edituri` 等旧标签记「可删旧标签」INFO;`desc` 下限取 `markets.json` 的 `desc_min`。上面两个站的 CRITICAL/ERROR 按旧口径,复跑以新口径为准。
- 盲区:ebay、etsy(以及 ko 市场的 coupang)对 stdlib UA 返回 403,`site_audit` 与 `head_check` 失效,大站审计需要浏览器口径,报告标注「未穿透」;GA/AI 归因类不在本地工具覆盖内,维持月度手工口径。

## 维护

- 复审周期 **90 天**,下一次 **2027-01-09**;signals 清单与 `scripts/markets.json` 的 `markets.en.review_cycle` 保持一致,以 json 为准。
- 触发即复审:Google Search Status Dashboard(spam 与 core)、DemandSphere / Ahrefs 品牌词 AIO 月度读数、Chrome WebMCP 与 ARD 采用进展、GA4 渠道口径变化、Ahrefs / Surfer / Cloro 月度引用研究(先核分母是否变)。
