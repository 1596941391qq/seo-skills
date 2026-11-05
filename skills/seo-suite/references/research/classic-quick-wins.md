# 经典速效做法清单(改动小、见效快的 SEO 动作,逐条指到本套件)

## 用途

每次接手一个站,或者季度复盘时,按这张表从上往下过一遍:
- 每条先看站点做没做;
- 没做的按「提升 × 速度」排进本周或本月;
- 表里「本套件」一列告诉你用哪个脚本、读哪份文档。

排序是 2026-11-06 在一个 API 产品站(约 2,800 个网址、月展示约 2 万)上实测排出来的。站点体量不同时,提升档会变,但前几条几乎对所有站都成立。

## 一、站内,我们自己就能做(几天见效)

| # | 做法 | 怎么做 | 本套件 |
|---|---|---|---|
| 1 | GSC 第 8–20 名的词改标题、补答案段 | 拉近 28 天 query×page,取加权排名 8–20、展示最高的词;把词放进 title 和 H2,H2 下第一段直接回答 | `gsc_mining.py`(striking distance)、[title-formulas](../content/title-formulas.md) |
| 2 | 排前 10 却没人点的词改标题和描述 | 同一份数据里排名 1–10、CTR 比期望低 >2 个百分点的词;对照 SERP 看别人的标题怎么写 | `gsc_mining.py`(低 CTR,query×page 导出先按词合并)、`question_align.py` |
| 3 | 从高权重页给目标页加内链 | 首页、文档首页、热门文章 → 第 1、2 条的目标页,锚文本写目标词 | `link_graph.py`、`orphan_fix.py` |
| 4 | 新页、改过的页请 Google 收录 | GSC 网址检查里请求编入索引(Google 不收 IndexNow);Bing、Yandex 用 IndexNow | `gsc_api.py inspect`(只能查)、`indexnow.py` |
| 5 | 关键词互抢 | 同一语言里 ≥2 页分展示、次页占 ≥20% 且合计 ≥10 才算;先定主页面,另一页拉开意图并链向主页面 | `gsc_mining.py --mode matrix --brand 品牌词` |
| 6 | 掉量页刷新 | 两期对比掉一半以上的页,补内容、对齐意图 | `gsc_mining.py --decay`、[content-refresh-playbook](../content/content-refresh-playbook.md) |
| 7 | 标题加年份或数字 | 内容真更新了才写年份 | [title-formulas](../content/title-formulas.md) |
| 8 | 抢精选摘要和「其他人还问了」 | 排前 10 且 SERP 有摘要的词,在对应 H2 下写 40–60 字直接答案 | [serp-feature-taxonomy](serp-feature-taxonomy.md) |
| 9 | 自家有外链的 404 改 301 | 外链落点和站内 404 求交集,301 到最相关的现页 | `backlink_import.py`(GSC 外链导出)+ `redirect_chain.py` |
| 10 | 外链落点保持干净直链 | 见下文「外链落点」 | `redirect_chain.py` |

## 二、找外链(要对外发信,几周见效)

| # | 做法 | 怎么找 | 本套件 |
|---|---|---|---|
| 11 | 扒竞品和上下游的合作 / 集成 / 友链页 | 页上列了谁,谁就是潜在合作对象;双向都链的是换过的 | `link_intel.py crawl` → `exchangers`(互换池)、[link-intelligence](link-intelligence.md) |
| 12 | 竞品外链差集 | 链了 ≥2 家竞品、没链我们的域 | `link_intel.py ccgraph` + `intersect`(免费,Common Crawl);有 Ahrefs / Semrush 导出就用 `backlink_import.py` |
| 13 | 榜单文章收录 | 搜「best X / X alternatives / X 推荐」,请作者把我们加进去,给一个具体理由(价格、实测) | `link_intel.py listicles`(榜单 URL 和上面出现的站) |
| 14 | 失效链接替换 | 资源页、榜单页上指向已失效站点的链接,请对方换成我们的同类页 | `link_intel.py deadlinks`;话术 [outreach-templates](../monitoring/outreach-templates.md) |
| 15 | 资源页 | 查询模板见下文 | `link_intel.py deadlinks`(顺便查死链) |
| 16 | 未链接的品牌提及 | 搜品牌名、排除自己的域名,抓每页,找提到我们却没链我们的 | `link_intel.py unlinked` |
| 17 | 图片外链回收 | 原创图(架构图、数据图、OG 图)做反向图片搜索,用了却没署名的,请对方加来源链接 | search MCP `lens` 找页面 → `link_intel.py unlinked --brand 品牌` 核对有没有链 |
| 18 | 客座文章、联合教程 | 和真有合作的伙伴一起写一篇实测,正文链到深页 | [backlink-directory](backlink-directory.md) 第七节 |
| 19 | 记者请求平台(HARO 一类) | 按关键词订阅,只答真懂的问题,换引用和外链 | 平台和做法见下文 |
| 20 | awesome 列表、产品目录、MCP / AI 目录 | GitHub awesome-* 提 PR;AlternativeTo、SaaSHub、G2 等目录;Smithery、Glama、MCP Registry 等 | [directory-submissions](directory-submissions.md)、[backlink-directory](backlink-directory.md)、`directory_tracker.py` |
| 21 | 社区(Reddit、知乎、V2EX、Show HN) | 在真实问题下回答,不硬广 | [community-seo-playbook](../content/community-seo-playbook.md) |
| 22 | Product Hunt 发布 | 一次性流量和品牌提及;发布当天的流程归 gtm-suite 的 launch | [backlink-directory](backlink-directory.md) |

## 三、新页面类型(要业务方定,几周到几个月)

| # | 页面 | 结构要点 |
|---|---|---|
| 23 | 竞品流量页的同类页 | 先跑 `link_intel.py footprint` 看竞品靠哪类页面赢词最多,复制页面类型和结构,不抄内容 |
| 24 | 对比页、替代品页 | [competitor-page-patterns](competitor-page-patterns.md) |
| 25 | 集成单页 | 「产品 + 工具」一页一个:装法、一个能跑的例子、能做什么 |
| 26 | 免费工具页 | 选题看三样:有没有人搜、能不能做成、和付费产品的关系。工具本身是外链对象 |
| 27 | 术语表 | 每个术语一页:定义、例子、相关术语,链到产品页 |
| 28 | 更新日志 | 每条一个网址,带日期,另出 RSS |
| 29 | 模板、示例代码下载页 | 每个模板一页:用途、截图、下载、版本 |
| 30 | 原创数据报告 | 一份别人会引用的数据,按月或按年更新 |
| 31 | 文档 SEO | 每个接口一页可索引的参考文档:独立 title,请求和响应示例是可见文本,错误码,版本号,canonical |
| 32 | 程序化 SEO | [programmatic-seo-gates](../technical/programmatic-seo-gates.md)、`pseo_batch_gate.py` |
| 33 | Wikidata 实体 | 先有独立可靠来源再建,见 [entity-signal-checklist](../technical/entity-signal-checklist.md) |

## 外链落点

- 别人给我们的链接,直接指向相关的深页,不经跳转、不带跟踪参数。
- 用跟踪短链(`/r/<码>` 一类,302 跳到首页再带 UTM)当回链落点,会有三个问题:
  - 302 不传递规范化信号,结果里显示的是短链;
  - Bing 的口径是 302 只用于很短期的变化(见 [redirects-canonical](../technical/redirects-canonical.md) 1.1);
  - 链接落到首页,不落到对方读者真正关心的那一页。
- 要统计来源,用落地页上的 referrer、站点分析里的引荐来源,不要把跳转加在回链上。
- 已经发出去的短链:落点改成 301 到对应深页,或者请对方换成直链。
- 检查:`redirect_chain.py <回链网址>`,看到 302 或者跳到首页就记一条。

## 资源页查询模板

把「主题」换成你的品类词(例如 web scraping、proxy、captcha),每个市场用当地语言各写一套:

- `主题 intitle:resources`
- `主题 "useful resources"` / `主题 "useful tools"` / `主题 "recommended tools"`
- `主题 inurl:links` / `主题 inurl:resources`
- `主题 "best tools" -site:竞品.com`
- 中文:`主题 工具 推荐 汇总`、`主题 资源 导航`、`主题 友情链接`

搜到的页先用 `link_intel.py deadlinks --input 页面清单` 查死链,有死链的先联系。

## 记者请求平台

常用的有 Qwoted、Featured、Source of Sources、Help a B2B Writer。规则和费用各家常变,用之前去官网核对。

- 只订阅和自家产品真相关的关键词。
- 回答写具体数字和亲身做法,署真名。
- 以公司或创始人名义回答属于对外发言,发之前要业务方同意。

## 不要做的

- 批量互链、三角互换、只为互链建的合作页:Google 垃圾内容政策算链接作弊。
- 为显得新而改日期。
- 在别人站上留言、发帖带链接刷量。
