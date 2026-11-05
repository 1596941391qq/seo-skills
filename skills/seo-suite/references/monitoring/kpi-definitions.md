# SEO / GEO 指标口径

> 涉及 AI 可见度的指标，先读 [geo-evidence.md](../content/geo-evidence.md)。

## 用途

写报告、设告警、定目标之前，先把每个指标「怎么算、从哪来、容易被怎么误读」说清楚。本文不给行业基准数字：行业、站点和查询组合差别太大，目标用本站历史基线和同期对比来定。Search Console、GA4 和第三方工具的数据都需要你自己的账号和权限，本 Skill 不附带数据。

报告里每个指标都要写明：公式、数据源、日期范围与时区、筛选条件（国家、设备、搜索类型、品牌 / 非品牌）、聚合方式、数据延迟。

## 一、Search Console（只覆盖 Google 搜索）

核对 2026-10-21（2026-11-05 补平台属性），来源：[效果报告概览](https://support.google.com/webmasters/answer/7576553)、[数据如何计数](https://support.google.com/webmasters/answer/17011364)、[维度与分组](https://support.google.com/webmasters/answer/17011259)、[数据差异排查](https://support.google.com/webmasters/answer/17010575)。

| 指标 | Google 的定义 | 容易误读的地方 |
|---|---|---|
| 点击 | 用户从 Google 搜索结果点进本站的次数 | 不等于 GA4 会话数 |
| 展示 | 本站出现在搜索结果里的次数 | 按网站聚合时，同一页结果里出现两条本站链接只算 1 次展示 |
| CTR | 点击数 ÷ 展示数 | 新增大量靠后的展示会拉低 CTR，不一定是标题的问题 |
| 平均排名 | 本站最靠前那条结果的平均位置（图表是全站最靠前；表格是该行 URL 或维度的平均位置） | 数值变大不一定是排名下降，可能是新增了靠后的长尾展示。官方建议多看展示和点击的趋势，少看位置本身 |

口径要点：

- **按网站 vs 按网页聚合**：图表永远按网站聚合；「网页」「搜索外观」维度的表格按网页聚合。多个页面同时出现时，按网页聚合的点击和展示更多，CTR 和平均排名更低（官方示例：3 个页面同时出现，网站级 CTR 100%、平均排名 1；网页级每页 CTR 33%、平均排名 2）。图表总数与表格总数不等是正常的。
- **匿名查询**：罕见查询出于隐私被省略，不出现在查询表里；没加查询筛选时，它们仍计入图表总数。加了查询筛选后，「匹配」与「不匹配」两部分加起来可能小于不筛选的总数。
- **行数上限**：界面表格最多显示 1,000 行；Search Console 只存储和显示最重要的数据行。要更全的查询列表，用[批量数据导出到 BigQuery](https://support.google.com/webmasters/answer/12917675)。
- **时区与延迟**：日数据按太平洋时间（PT）；通常 2 到 3 天后数据才完整；最新数据可能是初步数据（图上显示虚线）。
- **数据保留**：Search Console 只保留有限的月数（[保留期](../overview/facts.md#gsc-retention)；GA4 里的 Search Console 报告同一上限，见 [GA4 关联说明](https://support.google.com/analytics/answer/10737381)）。要更久的历史，用 Search Analytics API 或批量导出自己存。批量导出从开通起累积，开通前的历史要靠 API 补（[官方](https://support.google.com/webmasters/answer/12917675)）。
- **搜索类型**：网页（文本型 Web: text-based，或多模态 Web: multimodal——图片搜索如 Lens、Circle to Search，2026-09-24 起有这个筛选）、图片、视频、新闻是不同的搜索类型；多模态搜索没有文本查询，选它时查询维度不可用。Discover 和 Google 新闻有单独的报告。
- **AI 功能**：按 Google 的 [AI 功能说明](https://developers.google.com/search/docs/appearance/ai-features)，AI Overviews 和 AI Mode 的数据计入效果报告的「网页」搜索类型。另有[生成式 AI 效果报告](https://support.google.com/webmasters/answer/16984139)：只报展示（按页面、国家、设备、日期），不报点击；先分批开放，后对全球网站开放（[日期](../overview/facts.md#gsc-genai)）；展示太少的站点仍可能看不到该报告。
- **品牌 / 非品牌**：效果报告有官方的品牌 / 非品牌查询筛选，从 2025-03-11 起有数据，历史长度同效果报告保留期（[保留期](../overview/facts.md#gsc-retention)）；展示太少的站点和子资源没有这个筛选；分类可能出错，仅供参考，不影响排名。要在 API 或批量导出里分品牌，自己用查询正则，并把正则写进报告附录，保证每期一致。
- **平台属性（社媒与视频账号）**：Instagram、TikTok、X、YouTube 账号可以作为单独的 Search Console 属性，2026-07-29 起全球开放（[帮助页](https://support.google.com/webmasters/answer/17148418)、[博文](https://developers.google.com/search/blog/2026/07/platform-properties-social-video-guide)，核对 2026-11-05）。KPI「平台内容的 Google 点击」= 每个平台属性效果报告的点击，按平台分列，不和网站属性的点击相加成「搜索点击」（两类属性统计的是不同 URL）。口径：只算 Google 搜索、Discover、Google 新闻里的展示和点击，不含平台站内播放；视频在 Google 播放器里打开也算点击；Insights 顶部总数含图片、视频、新闻搜索，下方明细只算网页搜索。新加的属性只从开始收集那天起有数据，没有回溯，做同比前先确认起始日。分析方法见 [video-geo-guide.md](../content/video-geo-guide.md) 第三节。
- **数据异常期**：Google 在[数据异常页](https://support.google.com/webmasters/answer/6211453)记录过一段展示、CTR、平均排名记录有误的时间（[GSC 数据异常期](../overview/facts.md#gsc-anomaly)），点击不受影响，修复后展示数下降。跨这个期间的展示 / CTR / 排名对比不可信；这段期间只比点击。写报告前先读这个页面，看有没有新的异常。

### API 与导出的限额（核对 2026-10-21）

来源：[Search Console API 用量限制](https://developers.google.com/webmaster-tools/limits)、[获取效果数据](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data)、[帮助中心：用 API 导出](https://support.google.com/webmasters/answer/12919192)。

| 项目 | 官方数值 |
|---|---|
| 每次请求最多行数 | 见[配额表](../overview/facts.md#api-quotas)；用 `startRow` 翻页，直到返回 0 行 |
| 每天可取总行数 | 每个属性、每个搜索类型有每日上限（按点击排序，[配额表](../overview/facts.md#api-quotas)） |
| Search Analytics 查询频率 | 按站点、用户、项目分别限额，见[配额表](../overview/facts.md#api-quotas) |
| URL 检查 | 比 Search Analytics 紧，按站点、项目限额，见[配额表](../overview/facts.md#api-quotas) |
| 其他资源 | 按用户、项目限额，见[配额表](../overview/facts.md#api-quotas) |
| 负载配额 | 另有 10 分钟短期配额和 1 天长期配额；按网页或查询分组、日期范围越长，负载越大；超限时报同一个 quotaExceeded 错误 |

官方建议：每天只取一天的数据，既不容易超配额，也避免丢数据。按「网页」和「查询」一起分组时，系统会丢弃部分数据；要准确总数，就不带这两个维度单独取一次。

- 本套件的 `gsc_api.py query` 默认每页取单次请求上限（`--rows` 设总行数上限），用 `--dimensions` 选维度；匿名查询 API 不返回。

## 二、GA4（站内行为与转化）

核对 2026-10-21，来源：[默认渠道组](https://support.google.com/analytics/answer/9756891)、[Data API 指标定义](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)、[数据保留](https://support.google.com/analytics/answer/7667196)、[Data API 配额](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)。

- **自然搜索会话**：会话默认渠道组为「Organic Search」的会话。官方定义：来自搜索结果里非广告链接的访问，**包括 Google 的 AI Overviews 和 AI Mode**，也包括所有其他搜索引擎，不只 Google。
- **AI 助手渠道**：GA4 默认渠道组有「AI Assistant」渠道：来自 ChatGPT、Gemini、Deepseek、Copilot、Grok 等的访问，**不含** Google AI Overviews 和 AI Mode（后两者落在 Organic Search）。没有 referrer 的 AI 访问仍会落进 Direct。要看全貌，用自定义渠道组加来源正则，再和服务器日志对照。
- **归因范围**：「默认渠道组」（事件级，用属性设置的归因模型）、「会话默认渠道组」和「首次用户默认渠道组」（后两者用付费和自然渠道末次点击）口径各不相同，同一个「自然搜索带来的转化」会得到不同的数。报告里写明用的是哪一种。
- **关键事件率**：API 里有两个指标。`sessionKeyEventRate` 是「触发过任一关键事件的会话占比」；`userKeyEventRate` 是用户占比。报告里写明用哪个，也就是写明分母。
- **和 Search Console 对不上是常态**：点击和会话的定义不同；GA 只统计启用了 JavaScript 的用户；用户拒绝统计或拦截脚本；referrer 丢失会记为直接流量；Search Console 日数据按太平洋时间，GA4 按属性时区；数据延迟也会造成差异。看两边趋势是否同向，不追求数字相等。
- **数据保留**：标准 GA4 属性的用户级和事件级数据保留期只能选 2 个月或 14 个月；这个设置只影响探索和漏斗报告，不影响标准聚合报告。更长的保留期（26、38、50 个月）只有 360 属性才有。要超过 14 个月的探索数据，用 BigQuery 导出。
- **Data API 配额（标准属性）**：Core 每属性每天 200,000 token、每小时 40,000 token、每项目每属性每小时 14,000 token，并发请求 10 个；360 属性是 10 倍（并发 50）。token 消耗随行数、列数、筛选复杂度和日期范围增加；请求里加 `"returnPropertyQuota": true` 可看剩余额度。

## 三、索引、抓取与性能

- **已编入索引页数**：看页面索引报告，可按 sitemap 筛选，对比「已提交」和「已编入」。未编入的原因逐项看，不只看总数。
- **抓取**：抓取统计报告给出请求数、平均响应时间，以及按状态码和抓取用途的分布；服务器日志能看到所有爬虫，更完整。
- **Core Web Vitals**（核对 2026-10-21）：按 web.dev，评估点是页面加载的第 75 百分位，分手机和桌面分别看；良好档见[阈值表](../overview/facts.md#cwv)。Lighthouse 这类实验室数据用来诊断，不能代替字段数据。CrUX 的数据是滚动窗口汇总（[窗口长度](../overview/facts.md#crux-window)），改动上线后要等窗口滚过才能完全反映。

## 四、外链与竞争指标（第三方工具的估算）

- **引用域**：链接到本站的不同域名数。各工具抓取覆盖不同，只能在同一工具内按时间比较。
- **DR、DA、Authority Score 等**：各工具自定义的评分，不是 Google 的指标，也不是排名因素的读数。
- **可见度 / Share of Voice**：基于你自选的关键词集和工具假设的点击率曲线估算。换词集或换工具就不可比。
- **流量价值**：估算点击数 × 广告单价，意思是「买同样的流量要花多少」。它不是收入，不能直接当 ROI。

## 五、AI 可见度（自行观测的抽样指标）

这些不是任何平台提供的官方指标，而是你按固定协议自己采样得到的数：

- **样本**：固定问题集 × 产品或模型 × 语言与地域 × 重复采样次数。每条记录时间、是否联网检索、引用的 URL 和原始回答。
- **提及率**：提到品牌的回答数 ÷ 有效回答数。
- **引用率**：引用本站 URL 的回答数 ÷ 有效回答数。提到品牌不等于引用本站。
- **表述准确率**：回答里关于品牌或产品的事实，有多少是对的。
- 同一问题重复问，结果会变；不同监测工具的数字不可比；和内容改动同时出现的变化只是相关，不能写成因果。

## 六、业务结果

- 自然搜索转化和收入：写明归因模型和时间窗口。
- SEO ROI：写明成本包含哪些、收益按哪种归因、是否扣除了品牌的自然需求；给区间和假设，不给单一数字。

## 常见误读

- 平均排名变差，就说「排名掉了」。
- 拿网上流传的「各位置 CTR 表」判断标题好坏。有效参照是本站同一查询、相近位置的历史 CTR。
- 用工具的 DR 涨跌解释流量变化。
- 凭某一次 AI 回答里有没有本站就下结论。

## 归因与对账（本套件口径，依据官方帮助）

- **GA4 的归因模型**：首次点击、线性、时间衰减、位置加权这四种模型自 2023-11 起不可用；现在是数据驱动归因和「付费和自然渠道末次点击」两种（来源：[GA4 归因入门](https://support.google.com/analytics/answer/10596866)）。
- **数据驱动归因的数据量**：这是 Google Ads 的说法。Google Ads 帮助建议 30 天内至少 200 个转化和 2,000 次广告互动，数据少时模型仍能运行，只是精度较低（来源：[Google Ads 数据驱动归因](https://support.google.com/google-ads/answer/6394265)）。这是建议值，不是开关门槛。
- **三种测量范式**：多点触达归因（用户级路径）、营销组合模型（MMM，汇总层回归，需要足够长的历史和真实的预算波动）、增量实验（如按地区留出对照组）。当两个渠道争同一个转化时，增量实验是最可靠的判据。
- **对账五步（本套件口径）**：①选一个业务真相源（CRM 或后端订单）；②不跨平台求和，同一个转化会被多个平台各认领一次；③只比较方向是否一致；④各平台自报的数只作参考，不用固定倍数换算；⑤把允许的差距预先写成预算。
- **盲区四项**：直接流量（什么都往里放）、品牌词搜索（会吃掉上层渠道的功劳）、暗社交（私信和群里转发）、AI 流量（常经品牌词搜索或直接进入，AI 的触达看不见）。AI 归因只能用 referrer 清单、渠道组正则和服务器日志三个来源做下界估计。

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。

- 思路参考：[aaron-he-zhu/seo-geo-claude-skills · monitor/performance-reporter/references/kpi-definitions.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/v9.9.12/monitor/performance-reporter/references/kpi-definitions.md)（Apache-2.0）
- 一手资料：[Search Console 效果报告](https://support.google.com/webmasters/answer/7576553)、[Search Console API](https://developers.google.com/webmaster-tools)、[AI 功能与网站](https://developers.google.com/search/docs/appearance/ai-features)、[GA4 事件](https://support.google.com/analytics/answer/9322688)、[Web Vitals](https://web.dev/articles/vitals)、[CrUX](https://developer.chrome.com/docs/crux)

## 机会挖掘与变更测量的口径（第三方工具做法与本套件口径）

以下数值来自第三方开源工具的源码默认值（crawlseo、seo-monster、iannuttall、elmo、unifapi，2026-10-09 读源码），**不是 Google 的规定**。读它们是为了看别人怎么入池和排序；阈值请用自己站的历史数据重新标定，并写进报告附录。

### 四类机会的入池条件（crawlseo 默认值，本套件借用为起点）

| 机会 | 入池条件 | 口径要点 |
|---|---|---|
| striking distance | 位置 4–20 且 28 天展示 ≥20 | 按展示排序，估算推进 3 位后的增量 |
| low CTR | 展示 ≥50 且位置 ≤15 | 用「期望 CTR − 实际 CTR」排序，按展示×差距，不按百分比 |
| content decay | 前 28 天点击 ≥10 | 28 天 vs 前 28 天，下降 25% 以上才报；小基数页不入池 |
| cannibalization | 同一查询 ≥2 个落地页，且 top 页展示 ≥20 | 页面位置用展示加权平均，不是简单平均 |

本套件自己的脚本 `python3 scripts/gsc_mining.py gsc.csv --mode matrix --json` 用的是另一组本套件口径阈值:striking distance = 排名 5–20 且展示 ≥20;低 CTR = 排名 1–10、展示 ≥50、比内置期望曲线低 2 个百分点以上(曲线是本套件口径，不是官方数据);蚕食 = 同一查询 ≥2 个页面且最大展示 ≥20;衰退 = 上期点击 ≥10 且本期下降 ≥25%。两组阈值不同，报告里写明用的是哪一组。

「期望 CTR」不要用网上的通用曲线：第三方研究给出的各位置 CTR 差别很大，不是通用基准。做法是用本站同一批查询、各位置的历史 CTR 自己算一条曲线（seo-monster 的做法），只用它给 gap 排序，不用它判断标题好坏。

### 对比与异常

- seo-monster 的 `gsc_compare_periods` 支持按差值排序、设最小变化门槛，以及用 σ 阈值找离群点。本套件对应的脚本是 `sensor_volatility.py`（`--gsc` 读导出 CSV，输出逐日波动分和 z30 异常日）。
- 多站点先看每个属性一行的汇总，再钻进单站。

### 变更前后对比（iannuttall measure-change 的做法，本套件口径）

- 前后两个窗口等长，只用已完成的完整日历日；日界按 Search Console 的太平洋时间（PT）切。
- 若后窗被截断，或某个窗口不足 7 个完整天，把结果标为「初步」，不下方向性结论（本套件口径）。
- 平均排名是按展示加权的平均位置；查询级数据因匿名化会缺行，缺行不等于零流量，报告里注明。
- GA4 交叉读用落地页筛选，并注意 GA4 属性时区与 PT 日界的差异。
- [GSC 数据异常期](../overview/facts.md#gsc-anomaly)里的展示 / CTR / 排名不可比，见上文。

### AI 可见度指标的公式版（elmo / unifapi 的写法）

- visibility = 提及品牌的 run 数 ÷ 总 run 数；share of voice = 本品牌 ÷（本品牌 + 竞品之和），提及单位要一致（如「提及该实体的 run 数」）。
- citation coverage = 各品牌各来源的引用次数之和 ÷ 成功的 cell 数；多个品牌可同时被引用，跨品牌求和可以超过 100%。citation share = 单品牌引用次数 ÷ 全部品牌引用次数之和，分母非空时各品牌之和恒为 100%。带权重的版本不叫 share。分母为空记 N/A，不记 0；有效的「无回答」留在 coverage 的分母里。
- 稳定性 = 用逐日引用份额向量的 Bray–Curtis 距离算波动，再换成 0–100 的分数；它是这些工具的自定义指标，换工具不可比。

页内「内容分」和站点「健康分」这类公式各家工具都不同，权重没有公开依据，也不是 Google 指标。需要时用本套件的 `content_score.py` 与 `health_score.py`，并按脚本帮助里写的口径解读；不要把别家工具的分数当作排名预测。

## AI 可见度指标的行业词汇层：IAB 4P 对齐

核对 2026-10-21，来源：[IAB《Measuring Visibility in the AI Era》指南页](https://www.iab.com/guidelines/measuring-visibility-in-the-ai-era/)与[PDF 全文](https://www.iab.com/wp-content/uploads/2026/07/IAB_Measuring_Visibility_in_the_AI_Era_August_2026-1.pdf)（2026-08 发布）。IAB 指出有 20 多家公司在卖 AI 可见度测量工具，方法不同，同一品牌会得到不同的结果。IAB 只定词汇和披露要求，不给厂商评级。

### 4P 层级（IAB 原文）

| 层 | 该层指标 |
|---|---|
| Presence（在场） | Mention Rate（提及率）、Citation Rate（引用率）、Share of Voice、Visibility Momentum |
| Prominence（突出） | Position（位置）；发布方侧另有 Content Utilization Rate |
| Portrayal（表述） | Sentiment、Framing、Hallucination Rate、Factual Inaccuracy Rate；发布方侧另有 Attribution Clarity |
| Persuasion（说服） | Recommendation Strength、Post-Citation CTR |

IAB 对 Post-Citation CTR 的定义：AI 引用中，把用户带到发布方网站的百分比。

### 方向级与决策级（IAB 原文要点）

- **Directional（方向级）**：看趋势和信号，用于早期发现、内部简报、竞争感知；不够用于预算分配或战略决策。
- **Decision-Grade（决策级）**：用于预算调整、代理商评审和高管决策。IAB 要求在 8 个维度上达标：样本量（每个查询的回答数）、查询量、提示类型覆盖、测试频率、可复现性、数据验证、方法文档、平台覆盖。
- IAB 给出的几个具体数：查询量低于 50 个，按「探索性」处理，连方向级都不算；决策级要求提示类型覆盖全部 4 类意图（信息、比较、推荐、交易）；决策级的可复现性要在 7 天窗口内定义可接受的波动范围。
- 评估第三方工具时，拿这 8 个维度做问卷。答不出的按方向级用，进报告时标「directional」，不进预算页。

### 套件指标 → IAB 词汇映射

| 套件口径（本文第五节与 [agent-readiness](../technical/agent-readiness.md) 探针计分） | IAB 层与指标 | 备注 |
|---|---|---|
| `citation_panel.py report` 的 mention coverage（提及数 ÷ 成功 cell 数；no_answer 计 0 并留在分母） | Presence · Mention Rate | 带 Wilson 区间的 mention_rate 见脚本 JSON |
| `citation_panel.py` 的 source_visibility（引用本站域名的回答占比） | Presence · Citation Rate | 与 brand_visibility 的差距记为 visibility_gap_pp;跨品牌求和可超过 100%，不是 share |
| share of voice | Presence · Share of Voice | 提及单位一致是前提 |
| stability | Presence · Visibility Momentum 的对偶面 | 动量与稳定性同层报告 |
| 探针计分 cited-with-link / mentioned / absent | Presence | 没记位次时只落此层 |
| 表述准确率（本文第五节） | Portrayal · Factual Inaccuracy Rate | 分母 = 已核查的事实条数 |
| 逐条事实核查的 misrepresented 罚分 | Portrayal · Hallucination Rate | 纠错汇报可直接用这个词 |
| `ai_referral_log` 三源下界 | Persuasion · Post-Citation CTR 的近似 | AI 引荐流量是引用后行为的下界 |
| 缺口：回答内位置 | Prominence · Position | Search Console 的 AI 报告只有展示；位次靠探针自采 |
| 缺口：Post-Citation CTR 的直接口径 | Persuasion | 用 referrer 清单、渠道组、日志三源近似，标「下界」 |

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 报告里每个指标都写了公式、数据源、日期与时区、筛选、聚合方式 | 对照本文开头一行；Search Console 日期按 PT | 缺任一项 = 失败 |
| 对比期没有跨数据异常期 | 读[数据异常页](https://support.google.com/webmasters/answer/6211453)；跨[GSC 数据异常期](../overview/facts.md#gsc-anomaly)的展示 / CTR / 排名对比 | 跨了就只比点击，并在报告注明 |
| 取数没有被行数上限截断 | 界面表格 1,000 行；API 单页和每天每类型的行数上限见[配额表](../overview/facts.md#api-quotas)。`python3 scripts/gsc_api.py query --site sc-domain:example.com --start 2026-10-01 --end 2026-10-01 --dimensions query,page --rows 25000 --out gsc.csv` 一天一次 | 行数恰好等于上限 = 可能被截断，改用批量导出 |
| 点击与展示总数核对 | 不带 page / query 维度单独取一次总数，和明细求和比较 | 明细小于总数是匿名查询与截断造成的，报告里写差值占比 |
| GA4 渠道口径一致 | 报告注明用的是默认渠道组、会话默认渠道组还是首次用户渠道组 | 混用 = 失败 |
| AI 流量不只看 AI Assistant 渠道 | 同时看 Organic Search 里的 AI 功能展示（Search Console 生成式 AI 报告）和服务器日志 | 只用一个来源 = 降级为方向级 |
| AI 可见度数据标了级别 | 用上文 IAB 8 个维度问卷；查询量 <50 记为探索性 | 未标级别的数不进预算页 |

