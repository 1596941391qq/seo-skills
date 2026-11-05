# 事实表(单一来源)

在多个参考文件里反复出现的外部事实,只在这一张表里写值。其他文件链接本表的锚点(例如 `facts.md#cwv`),不再各写一份数字。

- 看门:`tests/test_fact_single_source.py`。有人在别的文件里重新硬写这些值,测试就红,并列出文件和行号。
- 改值:先在本表改(值、来源、核对日期),再改各条明细里「脚本常量」写到的脚本。测试会核对两边相等。
- 份额的例外:各市场的明细表留在 `references/markets/<市场>.md`。本表只收跨文件引用的 5 个市场的头条读数,测试核对两边一致。
- 选哪些事实:2026-10-24 在 `SKILL.md`、`references/`、`templates/` 里按出现次数统计,取前 11 类外部事实(本套件自己的口径不进表)。

## 总表

| 锚点 | 事实 | 值 | 一手来源 | 核对 |
|---|---|---|---|---|
| [cwv](#cwv) | Core Web Vitals 阈值 | LCP 良好 ≤2.5s、差 >4s;INP 良好 ≤200ms、差 >500ms;CLS 良好 ≤0.1、差 >0.25;按第 75 百分位,移动和桌面分开看 | web.dev | 2026-10-24 |
| [crux-window](#crux-window) | CrUX 数据窗口 | 28 天滚动聚合,每天约 04:00 UTC 更新 | Chrome for Developers | 2026-10-24 |
| [gsc-anomaly](#gsc-anomaly) | Search Console 展示数据异常期 | 2025-05-13 至 2026-04-27:展示、CTR、平均排名记录有误;点击不受影响 | Search Console 帮助 | 2026-10-24 |
| [rich-results](#rich-results) | FAQ / HowTo 富结果退役 | FAQ:2023-08-08 收窄到知名政府和健康站,2026-05-07 起不再展示,文档 2026-06-15 删除。HowTo:2023-08-08 起只在桌面展示,2023-09-13 起桌面也不展示,2023-09-14 文档删除 | Search Central | 2026-10-24 |
| [gsc-genai](#gsc-genai) | Search Console 生成式 AI 效果报告与控制 | 报告 2026-06-03 公布、先给部分站点;报告和 Search generative AI 控制 2026-08-31 起对全球所有站点开放;报告只给展示,没有点击 | Search Central / 帮助 | 2026-10-24 |
| [gsc-retention](#gsc-retention) | Search Console 效果数据保留期 | 最近 16 个月 | Search Central | 2026-10-24 |
| [sitemap-limits](#sitemap-limits) | sitemap 单文件上限 | 50,000 个 URL 或 50MB(未压缩),先到为准 | Search Central | 2026-10-24 |
| [googlebot-size](#googlebot-size) | Googlebot 抓取文件上限 | 每个受支持文件类型的前 2MB(按解压后计),PDF 前 64MB;CSS、JS 等资源各自单独计 | Search Central | 2026-10-24 |
| [api-quotas](#api-quotas) | API 配额与行数上限 | 见下方分表 | Search Console API / Indexing API / CrUX API | 2026-10-24 |
| [indexnow-batch](#indexnow-batch) | IndexNow 单次 POST 上限 | 10,000 个 URL | indexnow.org | 2026-10-24 |
| [search-share](#search-share) | 搜索引擎份额(StatCounter,2026-10,全设备) | 见下方分表 | StatCounter | 2026-11-05 |

## 机器可读值

测试和脚本常量核对读这一块。改值时和上面的表同批改。

```facts
cwv.lcp.good_ms = 2500
cwv.lcp.poor_ms = 4000
cwv.inp.good_ms = 200
cwv.inp.poor_ms = 500
cwv.cls.good = 0.1
cwv.cls.poor = 0.25
crux.window_days = 28
gsc.anomaly.start = 2025-05-13
gsc.anomaly.end = 2026-04-27
rich.faq.narrowed = 2023-08-08
rich.faq.off = 2026-05-07
rich.faq.docs_removed = 2026-06-15
rich.howto.off = 2023-09-13
rich.howto.docs_removed = 2023-09-14
gsc.genai.announced = 2026-06-03
gsc.genai.global = 2026-08-31
gsc.retention_months = 16
sitemap.max_urls = 50000
sitemap.max_bytes = 52428800   # 50MB = 50 × 1024 × 1024 字节(sitemaps.org 写 52,428,800 bytes)
googlebot.max_mb = 2
googlebot.pdf_max_mb = 64
gsc.api.site_qpm = 1200
gsc.api.user_qpm = 1200
gsc.api.project_qpm = 40000
gsc.api.project_qpd = 30000000
gsc.inspect.site_qpd = 2000
gsc.inspect.site_qpm = 600
gsc.api.rows_per_request = 25000
gsc.api.rows_per_day = 50000
indexing.publish_per_day = 200
crux.api.qpm = 150
indexnow.max_urls_per_post = 10000
share.ru.yandex = 70.15
share.ru.google = 28.43
share.ko.google = 48.64
share.ko.naver = 42.10
share.ja.google = 59.58
share.ja.bing = 32.26
share.ja.yahoo = 6.57
share.zh.baidu = 49.08
share.tr.yandex = 23.74
```

## 各条明细

<a id="cwv"></a>
### Core Web Vitals 阈值

| 指标 | 良好 | 需要改进 | 差 |
|---|---|---|---|
| LCP | ≤2.5s | 2.5–4s | >4s |
| INP | ≤200ms | 200–500ms | >500ms |
| CLS | ≤0.1 | 0.1–0.25 | >0.25 |

- 评估点:页面加载的第 75 百分位,移动和桌面分开。三项都在良好档才算通过。
- 来源:[web.dev Web Vitals](https://web.dev/articles/vitals)(页面日期 2024-10-31)原句 "LCP should occur within 2.5 seconds"、"INP of 200 milliseconds or less"、"CLS of 0.1 or less"、"a good threshold to measure is the 75th percentile";「差」档见 [LCP](https://web.dev/articles/lcp)、[INP](https://web.dev/articles/inp)、[CLS](https://web.dev/articles/cls)。核对 2026-10-24。
- 脚本常量:`scripts/field_data.py` 的 `THRESHOLDS`。

<a id="crux-window"></a>
### CrUX 数据窗口

- CrUX API 和 Search Console 核心网页指标报告的现场数据是 28 天滚动聚合;每天约 04:00 UTC 更新,没有 SLA。改动上线后要等窗口滚过才完整反映。
- 来源:[CrUX API 文档](https://developer.chrome.com/docs/crux/api)「The rolling average」「Daily updates」两节;`collectionPeriod` 始终显示 28 天。核对 2026-10-24。

<a id="gsc-anomaly"></a>
### Search Console 展示数据异常期

- 2025-05-13 至 2026-04-27,一个日志错误让展示、CTR、平均排名记录有误;点击不受影响。已修复,修复后展示数会下降。
- 用法:两期对比的窗口跨过这段时间时,只比点击。
- 来源:[Search Console 数据异常页](https://support.google.com/webmasters/answer/6211453)「April 3」条目原句 "prevented Search Console from accurately reporting impressions from May 13, 2025 until April 27, 2026 … clicks were not affected"。核对 2026-10-24。
- 脚本常量:`scripts/did_attribution.py` 的 `EPOCH_START, EPOCH_END`;其他脚本文字里写到这段时间的,结束日必须一致。

<a id="rich-results"></a>
### FAQ / HowTo 富结果退役

- FAQ:2023-08-08 起只给知名的政府和健康权威站;2026-05-07 起不再出现在 Google 搜索;2026-05-08 文档加弃用说明;2026-06-15 文档删除。Search Console 里 FAQ 的展示数从 2026-05-07 起下降。
- HowTo:2023-08-08 起只在桌面展示;2023-09-13 起桌面也不展示,这类富结果已弃用;2023-09-14 文档删除(更新记录原因:「no longer shown in search results, on both desktop and mobile devices」)。
- 用法:不为 SERP 新增 FAQPage / HowTo 标记;页面上真实存在的问答照常写成可见正文,真用户问答用 QAPage。
- 来源:[Search 文档更新记录](https://developers.google.com/search/updates)(2026-05-08「Deprecating the FAQ rich result feature」、2026-06-15「Removing documentation for the FAQ rich result feature」);[2023-08-08 博客](https://developers.google.com/search/blog/2023/08/howto-faq-changes)(含 "As of September 13, Google Search no longer shows How-to rich results on desktop");[数据异常页](https://support.google.com/webmasters/answer/6211453)「May 7 onwards」。核对 2026-10-24。

<a id="gsc-genai"></a>
### Search Console 生成式 AI 效果报告与控制

- 2026-06-03 公布生成式 AI 效果报告(Search 和 Discover 各一份),先给一部分站点。
- 2026-08-31 起,报告和「设置 → Search generative AI」控制对全球所有站点开放。展示太少的站点可能看不到报告。
- 报告只给展示(按页面、国家、设备、日期),没有点击;AI 功能的点击仍计在效果报告的「网页」搜索类型里,拆不出来。
- 来源:[Search Central 博客 2026-06-03](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports);[报告帮助页](https://support.google.com/webmasters/answer/16984139)("As of August 31, 2026, we've rolled out these insights to all websites worldwide");[控制帮助页](https://support.google.com/webmasters/answer/16908024)(同日全球开放)。核对 2026-10-24。

<a id="gsc-retention"></a>
### Search Console 效果数据保留期

- 效果报告的日期范围最长「最近 16 个月」;更早的数据要自己用 API 或批量导出存。
- 来源:[排查搜索流量下降](https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops)「Change the date range to include 16 months」;[数据异常页](https://support.google.com/webmasters/answer/6211453)只记录 3–16 个月内的问题。核对 2026-10-24。

<a id="sitemap-limits"></a>
### sitemap 单文件上限

- 单个 sitemap 不超过 50,000 个 URL 或 50MB(未压缩)。超了就拆成多个文件,用 sitemap index 提交。gzip 只省带宽,不放宽上限。
- 来源:[Google 构建 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)原句 "All formats limit a single sitemap to 50MB (uncompressed) or 50,000 URLs";[sitemaps.org 协议](https://www.sitemaps.org/protocol.html)。核对 2026-10-24。
- Naver、Yandex 各自文档写的上限按各自文档(见 [naver-searchadvisor.md](../technical/naver-searchadvisor.md)、[ru.md](../markets/ru.md))。
- 脚本常量:`scripts/sitemap_audit.py` 的 `FIFTY_K`、`FIFTY_MB`。

<a id="googlebot-size"></a>
### Googlebot 抓取文件上限

- Googlebot 为 Google 搜索抓取时,只取每个受支持文件类型的前 2MB、PDF 的前 64MB;按解压后的数据计;HTML 引用的每个 CSS、JS 单独抓,各自受同一上限。到上限后只把已下载部分送去索引。Googlebot Image、Video 等其他抓取器的上限可能不同。
- 来源:[Googlebot 文档](https://developers.google.com/search/docs/crawling-indexing/googlebot)(页面日期 2026-02-03)。核对 2026-10-24。

<a id="api-quotas"></a>
### API 配额与行数上限

| API | 配额 | 来源 |
|---|---|---|
| Search Console · Search Analytics | 每站点 1,200 QPM;每用户 1,200 QPM;每项目 40,000 QPM、30,000,000 QPD;另有短期(10 分钟)和长期(1 天)负载配额 | [Usage Limits](https://developers.google.com/webmaster-tools/limits)(页面日期 2025-08-28) |
| Search Console · URL Inspection | 每站点 2,000 QPD、600 QPM;每项目 10,000,000 QPD、15,000 QPM | 同上 |
| Search Console · 其他资源 | 每用户 20 QPS、200 QPM;每项目 100,000,000 QPD | 同上 |
| Search Analytics 行数 | 每次请求最多 25,000 行(`rowLimit` 1–25,000,默认 1,000),用 `startRow` 翻页;每个属性每天每个搜索类型最多 50,000 行(按点击排序) | [query 参考](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)、[获取全部数据](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data) |
| Indexing API | 默认每项目每天 200 次 `publish`(含 URL_UPDATED 和 URL_DELETED),太平洋时间午夜重置;`getMetadata` 每分钟 180 次;全部端点每分钟 380 次;免费。只用于 JobPosting 和 BroadcastEvent 页面 | [配额页](https://developers.google.com/search/apis/indexing-api/v3/quota-pricing)(页面日期 2026-10-16) |
| CrUX API | 每个 Google Cloud 项目每分钟 150 次,免费 | [CrUX API 文档](https://developer.chrome.com/docs/crux/api)「Rate limits」 |

核对 2026-10-24。脚本常量:`scripts/gsc_api.py` 的 `ROW_LIMIT_MAX`。

<a id="indexnow-batch"></a>
### IndexNow 单次 POST 上限

- 一次 POST 最多 10,000 个 URL,可混用 http 和 https。各引擎自定每日阈值。参与引擎不含 Google。
- 来源:[IndexNow 文档](https://www.indexnow.org/documentation)原句 "You can submit up to 10,000 URLs per post"。核对 2026-10-24。
- 脚本常量:`scripts/indexnow.py` 的 `BATCH_LIMIT`。

<a id="search-share"></a>
### 搜索引擎份额(StatCounter,2026-10,全设备)

| 市场 | 读数 | 明细 |
|---|---|---|
| 俄罗斯 | Yandex 70.15%、Google 28.43% | [ru.md](../markets/ru.md) 第 1 节(另有 Яндекс Радар、LiveInternet 两套口径) |
| 韩国 | Google 48.64%、Naver 42.10% | [ko.md](../markets/ko.md)(来路构成口径 Naver 更高,四套口径不能互换) |
| 日本 | Google 59.58%、Bing 32.26%、Yahoo! 6.57% | [ja.md](../markets/ja.md)(桌面单月 Bing 高于 Google) |
| 中国大陆 | 百度 49.08% | [zh.md](../markets/zh.md)(单月波动大) |
| 土耳其 | Yandex 23.74% | [tr.md](../markets/tr.md)(本地点击实测比例低得多) |

- 读数是 StatCounter CSV 导出(页面浏览样本,不是搜索次数)。页面上的表和 CSV 可能差 0.02–0.03 个百分点;StatCounter 会回溯修订历史月份。
- 其他市场 Google 主导(多在 88–99%),份额看各市场文件第 1 节。
- 来源:[StatCounter 搜索引擎份额](https://gs.statcounter.com/search-engine-market-share),各国页面的 CSV 导出(`chart.php?…&csv=1`,2026-10 单月;上一版 2026-09 的读数留在各市场文件)。核对 2026-11-05。
