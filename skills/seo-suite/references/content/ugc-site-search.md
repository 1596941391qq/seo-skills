# UGC 内容 SEO 与站内搜索优化（双模块）

> 建立于 2026-10-09；2026-10-18 逐条核对一手来源（证据账本 C3），2026-10-21 又重新打开官方文档和第三方来源复核一遍。上篇讲用户生成内容（UGC）怎么排上名；下篇讲站内搜索怎么处理和挖掘。两者在工程上共享同一批 URL（论坛帖、搜索结果页），所以合为一份。
> 规则以 Google Search Central 文档为准。平台排序机制多为公开观察，已逐条标注。「本套件口径」是本套件的做法约定，不是 Google 规则。不承诺排名。
> 分工（只引用不复述）：AI 爬虫放行见 [ai-crawler-policy.md](../technical/ai-crawler-policy.md)；UGC 进 JSON-LD 与 llms.txt 的注入防御见 [meta-tag-formulas.md](meta-tag-formulas.md) 与 [llms-txt-guide.md](llms-txt-guide.md)；rel=ugc 链接审计见 [link-quality-rubric.md](../monitoring/link-quality-rubric.md)；DiscussionForumPosting 字段细则见 [schema-templates.md](../technical/schema-templates.md)；FAQ 停展与 QAPage 存续见 [schema-examples.md](../technical/schema-examples.md)。

## 上篇：UGC 内容 SEO

### 一、UGC 的 SEO 双刃

**收益面**：

- 长尾覆盖：用户的提问就是真实查询的措辞，编辑部内容很难覆盖这种口语长尾（本套件口径）。
- 第一手经验：Google 2023-05-10 宣布 helpful content 系统会多展示论坛、博客等处的 "hidden gems"（[blog.google](https://blog.google/products-and-platforms/products/search/google-search-perspectives/)）。
- Discussions and forums 特性（第三方）：Ahrefs 分析 1.45 亿条美国 Google 结果，该特性出现在 1,693 万条（11.7%）里。出现时含 Reddit 的比例：美国 87.8%，全球 83.9%。单个帖子的外链数与它出现的频次没有相关性。来源：[Ahrefs 2026-08-27](https://ahrefs.com/blog/discussions-and-forums-serps/)。
- 新鲜度：活跃社区的帖子持续有新回复，适合时效敏感的查询（本套件口径）。

**风险面：为什么 Reddit 排得上，你的论坛可能排不上**——差距不在「有没有 UGC」，在四层机制：

1. **质量过滤层**：Reddit 的上下票、Quora 的答案竞争、知乎的赞同与反对，都把垃圾沉底、把好内容顶起。多数自建论坛没有这层，垃圾帖和好帖一起进索引（[site-type-playbooks.md](../overview/site-type-playbooks.md) 把「UGC 无质量门槛」列为失败模式）。
2. **数据供给层**：2024-02-22 Google 宣布接入 Reddit Data API，获得「实时、结构化」的内容和增强信号，用于展示和训练；Google 同时说明这不改变它对公开可抓取内容的索引方式（[blog.google](https://blog.google/company-news/inside-google/company-announcements/expanded-reddit-partnership/)）。Reuters 援引一位知情人士称合同约每年 6,000 万美元（[Reuters 2024-02-22](https://www.reuters.com/technology/reddit-ai-content-licensing-deal-with-google-sources-say-2024-02-22/)，第三方）。2026-10-08 Google 推出 [UGC Fresh Data Program](https://developers.google.com/search/docs/appearance/ugc-fresh-data-program)：获批平台可通过专用通道推送内容和互动信号。门槛是以 UGC 为主、内容量大、用户多、公开可抓、作者有公开主页、能做 OAuth 2.0 和严格校验的 JSON-LD、页面已有 `DiscussionForumPosting` 或 `SocialMediaPosting` 标记、有审核和举报机制、内容几分钟内推送、互动计数 72 小时内更新。Google 6 到 8 周内答复申请。
3. **规模层**：浏览、停留、回复速度等行为信号要到平台量级才稳定。新社区冷启动期信号稀疏（本套件口径）。
4. **工程层**：排序和翻页参数不归一、薄页进 sitemap、没有结构化数据、依赖 JS 渲染（本套件口径）。

**结论（本套件口径）**：UGC 不是免费内容，是要靠运营机制才能变现的资产。第三方借你的域名权威发内容抬排名，属于 Site Reputation Abuse 打击面（时间线见 [agent-readiness.md](../technical/agent-readiness.md) 第 8 节）。

### 二、UGC 技术治理

**审核模式（本套件口径）**：

| 站点状态 | 推荐模式 | 理由 |
|---|---|---|
| 新社区或高风险话题（健康、金融、法律） | 先审后发 | 冷启动期垃圾进索引的代价最大 |
| 有规模的活跃社区 | 后审加举报 | 发布延迟会压低参与度 |
| 任何阶段 | 新用户首帖必审，限制发帖频率 | Google 建议对可疑互动人工审核（见下） |

**官方反垃圾建议**（[Prevent user-generated spam](https://developers.google.com/search/docs/monitor-debug/prevent-abuse)，核对 2026-10-21；2026-10-26 官方增补「只索引给搜索用的内容」和「监控滥用」两节，2026-11-05 补核）：

- **只索引给搜索用的内容（2026-10-26 新增）。** 用户能生成可分享页面、生成结果或小工具的平台，先判断这类页面是给搜索找的，还是只给拿到链接的人看的；只为直接分享、协作或工具用途生成的页面，默认加 `noindex`（meta 或 `X-Robots-Tag`）或用 robots.txt 不让抓。
- **监控滥用（2026-10-26 新增）。** 在 Search Console 验证站点或子域名，收人工操作和安全问题邮件；定期看网页索引报告和效果报告，找和平台用途不符的已索引页、展示或查询突增；平台自己统计新公开页数和可索引 URL 数，新页突增或少数用户产生大部分可索引 URL 时报警。

- 对没有信誉的新用户帖子加 `noindex`；用户积累信誉后再放开索引。
- 给不可信内容里的所有链接加 `rel="ugc"` 或 `rel="nofollow"`。Google 建议评论和论坛帖的链接用 `ugc`；对长期高质量的贡献者可以去掉该属性（[链接属性文档](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)）。
- 对可疑互动人工审核；用表单填写时间、IP、UA 等信号建立用户信誉；屏蔽已知垃圾来源；用验证工具阻止自动注册。
- 违规后果：人工处置 "User-generated spam" 和 "Site abused with third-party spam"。后者点名论坛、留言簿、文件上传和**站内搜索页**是常见受害位置（[人工处置报告帮助](https://support.google.com/webmasters/answer/9044175)）。

**noindex 分级（本套件口径，依据上面的官方建议）**：

| 内容状态 | 索引策略 |
|---|---|
| 已验证（过审且有回复、投票或加精） | index，进 sitemap |
| 新内容或新用户内容（零互动、作者无信誉） | 不进 sitemap；可先 noindex，达到升格条件再放开 |
| 垃圾、重复、零价值薄页 | 永久删除的页面返回 404 或 410（Google 抓取预算文档建议） |
| 排序和翻页变体 | canonical 到默认排序版本，或用 robots.txt 阻止抓取（见第六节） |

- 升格条件写成可量化口径，例如：至少 3 条真实回复，或至少 N 票，或管理员加精。降格条件同样要写：举报成立、被合并、长期零流量。
- 404 或 410 依据：抓取预算文档说，永久删除的页面返回 404 或 410；被 robots.txt 屏蔽的 URL 会更久留在抓取队列里（[Optimize your crawl budget](https://developers.google.com/crawling/docs/crawl-budget)，2026-07-22 更新）。
- 与 [chinese-ai-search-guide.md](chinese-ai-search-guide.md) 的纪律一致：sitemap 只装值得被引用的规范页。

**指令交付注意**：`noindex` 用 meta 或 `X-Robots-Tag` 都可以。但爬虫必须能抓到页面才能读到指令（[robots meta 规范](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)）。robots.txt 屏蔽加 noindex 并存是经典自锁（修复见 [meta-tag-formulas.md](meta-tag-formulas.md) robots 行）。

**冷启动（本套件口径）**：机制跑起来之前，靠运营补内容密度。编辑以真实身份发起问题并邀请回答；每周固定选题帖；把客服和销售的真实问题（来源见 [gap-analysis-frameworks.md](../research/gap-analysis-frameworks.md)）转成第一批问题。有 3 到 5 个稳定活跃作者后再放开注册发帖。100 个有互动的帖子好过 10,000 个零回复帖。

### 三、社区内容排名机制（平台怎么排，自建社区抄什么）

> 平台大多没有公开当前算法。以下是公开资料与观察口径。

- **Reddit**：旧版开源代码里的 hot 排序函数 `hot(ups, downs, date)` 用票数和发帖时间计算热度（[reddit-archive/reddit](https://github.com/reddit-archive/reddit/blob/master/r2/r2/lib/db/_sorts.pyx)，仓库 2017-11-09 归档；现行算法未公开）。
- **Quora**：同义问题会被合并到同一个问题页，官方帮助有撤销合并的说明（[Quora Help](https://help.quora.com/hc/en-us/articles/360001043426-How-do-I-unmerge-my-question)；本次抓取返回 403，未能重新核对）。一个 URL 对应一个问题，查询与页面对齐度高。
- **知乎**：盐值按「基础信用、内容创作、友善互动、遵守规范、社区建设」五个维度计算（[知乎盐值说明](https://www.zhihu.com/term/credit)）。知乎说明盐值会作用于内容推荐系统和赋权系统，具体权重未公开。
- **百科类 UGC（Wikipedia 模式）**：中立立场、引用门槛、敏感页编辑复核、讨论页解决争议。内容是「达标才留」（观察口径）。

**机制到自建实现的翻译表（本套件口径）**：

| 平台机制 | 自建社区的等价实现 |
|---|---|
| 上下票质量过滤 | 投票或点赞加举报队列；帖子质量分 = 互动加权和 |
| 热度时间衰减 | 「最近回复顶起」加热帖位；页面 `dateModified` 随回复更新 |
| 一个 URL 一个问题（Quora 合并） | 近似重复的提问合并到规范问题页，旧 URL 301 |
| 引用门槛（百科） | 健康、金融、法律板块要求引用和资质，复用 content-patterns 高风险条款 |
| 作者信誉 | 等级、徽章、声望权限，接第四节 ProfilePage |

**不要抄的**：无门槛匿名即时发帖；「发帖即进 sitemap」的默认设置（回到第二节分级）。

### 四、UGC 结构化数据

| 内容形态 | 用什么 | 关键点（官方） |
|---|---|---|
| 用户可以提交答案的单问题页 | `QAPage`（`mainEntity` 为 `Question`） | 有富结果资格。`Question` 必须有 `answerCount`，以及至少一个 `acceptedAnswer` 或 `suggestedAnswer`；`Answer` 必须有 `text`。站方自写、用户不能补答的 FAQ 页不能用（[QAPage 文档](https://developers.google.com/search/docs/appearance/structured-data/qapage)）。2026-03-24 文档新增评论线程属性 |
| 一般论坛帖和讨论串 | `DiscussionForumPosting`（主帖）+ `Comment`（回复，可嵌套） | 必填 `author`（含 `author.name`）、`datePublished`，以及 `text`、`image`、`video` 三选一。用于 Discussions and forums 等特性。问答型论坛改用 QAPage（[文档](https://developers.google.com/search/docs/appearance/structured-data/discussion-forum)） |
| 作者主页 | `ProfilePage`（必填 `mainEntity`） | 可带 `interactionStatistic` 与 `agentInteractionStatistic`（[文档](https://developers.google.com/search/docs/appearance/structured-data/profile-page)） |
| 评论挂在商品上 | `Review` 或 `AggregateRating` 挂在 `Product` 上 | 被评对象自己控制评价时，用 `LocalBusiness` 或其他 `Organization` 类型的页面没有星级资格（[评价摘要文档](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)；电商细则见 [ecommerce-geo-ladder.md](ecommerce-geo-ladder.md) L2） |

- ProfilePage 与 DiscussionForumPosting 于 2023-11-27 同时发布，并配有 Search Console 报告（[Search Central 博客](https://developers.google.com/search/blog/2023/11/discussion-and-profile-markup)）。
- 论坛帖骨架（字段规整按 schema-templates 执行）：

```json
{"@context":"https://schema.org","@type":"DiscussionForumPosting",
 "headline":"<帖标题>","text":"<主帖正文>",
 "author":{"@type":"Person","name":"<用户名>","url":"<作者主页>"},
 "datePublished":"2026-10-01T08:00:00+08:00",
 "comment":[{"@type":"Comment","author":{"@type":"Person","name":"<回帖人>"},
             "text":"<回复正文>","datePublished":"2026-10-02T10:00:00+08:00"}]}
```

**反面清单**：

- UGC 问答不用 FAQPage。FAQ 富结果已不再展示（[日期与来源](../overview/facts.md#rich-results)）；真实用户提交的问答用 QAPage（分界见 [geo-evidence.md](geo-evidence.md)）。
- 2026-07-24 起评价摘要指南禁止虚假评价和未披露的激励评价（换取金钱、折扣、代金券、免费产品而未醒目披露）。审计评论类结构化数据时加这条检查。
- 结构化数据只描述页面上可见的内容（[结构化数据通用指南](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)）。投票数、回复数要与页面展示一致。
- Google 能处理渲染后 DOM 里的 JS 生成结构化数据（[文档](https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript)），但多数 AI 爬虫不执行 JS。本套件口径：结构化数据放在初始 HTML（降权规则见 [citability-scoring.md](citability-scoring.md)）。

### 五、AI 引用与 UGC

**AI 答案常引 UGC 的原因（本套件推断，非官方机制）**：第一人称经验在语料里密度高；一问一答结构便于抽取；票数和回复数是可见的质量代理。

**市场差异大**：各市场的引用分布见 [ai-citation-patterns.md](ai-citation-patterns.md) 与 [geo-platform-differences.md](geo-platform-differences.md)。先查目标市场的引用偏好，再决定是否押 UGC。

**让自站 UGC 被 AI 引用的六件事（本套件口径）**：

1. 答案自足、可抽取（块级写法见 [content-patterns.md](content-patterns.md)）。
2. 结构化数据语义完整（第四节）。
3. 无登录墙；AI 爬虫可达，且不被 WAF 拦截（见 [ai-crawler-policy.md](../technical/ai-crawler-policy.md)）。
4. 真实署名加作者页（ProfilePage）。
5. 带更新时间。
6. 数字与结论有出处。

**引用观测**：固定查询集，按 [ai-citation-patterns.md](ai-citation-patterns.md) 的采样纪律记录引擎、查询、日期、地域四要素，30、60、90 天对比自站 UGC 页的出现率。第三方 UGC 平台的占位审计见 [serp-feature-taxonomy.md](../research/serp-feature-taxonomy.md)。

## 下篇：站内搜索 SEO

### 六、站内搜索结果页的 SEO 处理（noindex 还是索引）

**默认答案：不让站内搜索结果页进索引。** 官方依据：

- 抓取预算文档：用 robots.txt 阻止抓取「无限滚动重复页、同一页面的不同排序版本」这类页面；为节省抓取不要用 noindex，因为 Google 仍会请求页面再丢弃（[Optimize your crawl budget](https://developers.google.com/crawling/docs/crawl-budget)）。
- 分面导航文档：URL 参数式分面会产生无限 URL 空间；不需要索引时用 robots.txt 阻止或改用 URL 片段（`#`）；canonical 和 nofollow 长期效果较弱（[Managing crawling of faceted navigation URLs](https://developers.google.com/crawling/docs/faceted-navigation)）。
- Google 2025-03 的 robots.txt 博客用 `disallow: /search` 作示例（[博客](https://developers.google.com/search/blog/2025/03/robotstxt-flexible-way-to-control)）。
- 人工处置 "Site abused with third-party spam" 把站内搜索页列为常见受害位置：用户的查询词可能被用来推广第三方。
- 历史依据：Google 旧版质量指南曾写「用 robots.txt 阻止抓取搜索结果页」（[SEL 2007 转述](https://searchengineland.com/google-warning-against-letting-your-search-results-get-indexed-10709)）。现行文档没有这句原话。
- URL 参数工具已于 2022 年下线（2022-03-28 宣布一个月后停用）。Google 说爬虫会自动学会处理参数；要更多控制就用 robots.txt（[博客](https://developers.google.com/search/blog/2022/03/url-parameters-tool-deprecated)）。

**三种手段对比**：

| 手段 | 效果 | 适用 | 陷阱 |
|---|---|---|---|
| robots.txt `Disallow: /search` | 不抓取，最省抓取预算 | 纯功能性搜索 | 被外链指向时 URL 仍可能进索引，但没有摘要（[robots.txt 介绍](https://developers.google.com/search/docs/crawling-indexing/robots/intro)） |
| meta noindex | 抓取但不进索引 | 想让爬虫顺着结果页发现新内容 | 必须可抓才生效；Google 仍会请求这些页面，量大时浪费抓取 |
| canonical 归一 | 变体逐渐并入规范页 | 分面组合与排序翻页 | 官方称长期效果弱于 robots.txt；只在同一内容的变体之间用 |

**何时可以索引（本套件口径，四条全满足才放开）**：

1. 该查询组合有**独立搜索需求**（关键词工具或 GSC 有量）。
2. 结果集**稳定**（同一查询长期返回同一批核心结果）。
3. 页面有**超出结果列表的增量内容**（导购文案、聚合评价、筛选说明）。
4. URL **规范化可控**：参数用 `&` 分隔；分面顺序固定；不出现重复筛选（分面导航文档的最佳实践）。

可索引的「搜索页」本质是程序化落地页。例：Class Central 2022 年的报告记录 Coursera 约有 146 万个关键词定向的搜索结果页（经 [seo.to 案例](https://seo.to/case-studies/coursera-course-catalog) 转引，第三方）。选题与闸门走 [programmatic-seo-playbook.md](../technical/programmatic-seo-playbook.md) 与 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md)，不要拿「搜索页可索引」当免审理由。

**robots.txt 参考块（按自家路径改）**：

```
User-agent: *
# 前缀匹配：/search 已覆盖 /search?q=...
Disallow: /search
# 参数在任意位置都匹配（写法同 Google 分面导航文档示例）
Disallow: /*?*sort=
Disallow: /*?*filter=
```

采用可索引搜索页模式时，把可索引查询页放到独立路径（如 `/q/` 或类目化 slug），与功能搜索 `/search` 分开，规则互不干扰。

**何时必须禁（本套件口径）**：会话和跟踪参数、排序翻页、任意拼接的多维分面、零结果页。中文区纪律见 [chinese-ai-search-guide.md](chinese-ai-search-guide.md)。

**决策流程（本套件口径）**：新的搜索或分面 URL 出现 → 有没有独立需求？没有 → robots.txt 阻止。有 → 结果稳定且有增量内容？没有 → noindex。都有 → 按 pSEO 闸门放量进索引，并持续监控该 URL 组的流量与蚕食（复诊见 [content-decay-signals.md](content-decay-signals.md)）。

### 七、站内搜索数据挖掘（GSC 之外的意图源）

站内搜索日志记录的是用户已经在你站内表达的需求，比外部关键词工具更贴近真实意图（本套件口径）。

- **采集**：GA4 增强型衡量的「站内搜索」事件 `view_search_results` 带 `search_term` 参数；默认识别 URL 参数 `q`、`s`、`search`、`query`、`keyword`，可在高级设置里加其他参数（[GA4 帮助](https://support.google.com/analytics/answer/9216061)）。埋点细则见 [ga4-implementation.md](../technical/ga4-implementation.md)。没有 GA4 的站，从服务器日志的 `/search?q=` 抽取（[log-analysis.md](../technical/log-analysis.md)）。
- **零结果查询 = 内容缺口**：导出零结果查询 → 清洗（先过第八节纠错重查）→ 聚类 → 三类动作：建新页、并入现有簇（补同义词与标题）、忽略。与 [gap-analysis-frameworks.md](../research/gap-analysis-frameworks.md) 的三方缺口法衔接。
- **热门内部查询**：直接进选题管道（[topic-cluster-templates.md](../research/topic-cluster-templates.md)）。头部查询对应的页面排不动时，先查内链与信息架构。
- **意图分层**：

| 意图 | 典型表现 | 动作 |
|---|---|---|
| 导航型 | 搜自家页面名或栏目名 | 查信息架构与内链：用户为什么找不到入口 |
| 信息型 | how、what、对比类 | 内容缺口，进选题管道 |
| 交易型 | 型号、属性、在售筛选 | 查品类命名与筛选项覆盖 |

- **清洗最小规则**：小写归一、去标点、去停用词、同义词折叠；中日韩查询先分词再聚类。

**月度循环**：

| 步 | 动作 | 产出 |
|---|---|---|
| 1 | 导出上月零结果查询，过纠错重查 | 清洗后的缺口清单 |
| 2 | 聚类并对照现有页面 | 三类：建、并入、忽略 |
| 3 | 高频查询对照现有排名 | 内链与信息架构修正单 |
| 4 | 交易型查询对照品类 | 命名与筛选项修正单 |
| 5 | 联想词日志归档 | 私有词库增量 |

### 八、搜索体验（分面、纠错、空结果页）

搜索体验不是直接的排名因素，但它决定站内搜索这条意图通道能不能用（本套件口径）。

- **分面导航**：单一维度且有独立需求（品牌、品类、价格段）可考虑索引（过第六节四条件）；多维组合默认不索引；参数顺序固定（同一筛选组合只产生一个 URL）。架构分工见 [navigation-patterns.md](../technical/navigation-patterns.md) 与 [link-architecture-patterns.md](../technical/link-architecture-patterns.md)。
- **纠错**：did-you-mean 与容错匹配（编辑距离、音近、分词变体）。只提示，不自动跳转，否则真实的新词查询永远查不到。纠错命中也记日志。
- **空结果页三件套**：给最接近的结果或热门内容；给相邻类目或放宽筛选的入口；把查询记入零结果报表。空结果页始终 noindex。
- **联想词**：搜索框联想降低空结果率；联想日志并入私有词库。
- **度量三件**：站内搜索使用率（搜索会话占比）、零结果率（应持续下降）、搜索后退出率（结果质量的代理）。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| UGC 外链带 ugc 或 nofollow | 抽 20 个帖子页：`curl -s URL \| grep -o '<a [^>]*href="http[^"]*"[^>]*>' \| grep -v 'example.com' \| grep -Evc 'rel="[^"]*(ugc\|nofollow)'`（`example.com` 换成自家域名，排除站内绝对链接） | 每页输出 0 为通过（白名单作者的链接除外） |
| 新用户内容不进索引 | 新注册账号发一帖，`curl -s 帖子URL \| grep -io '<meta[^>]*noindex[^>]*>'` | 输出 noindex 为通过 |
| 稀释程度 | GSC「网页」报告导出 UGC 目录的已索引 URL，对照 Search 效果报告 6 个月展示量 | 零展示页占比 ≤60% 为通过（本套件口径阈值） |
| 抓取预算流向 | 访问日志按目录统计 Googlebot 请求（[log-analysis.md](../technical/log-analysis.md)） | UGC 薄页与搜索页的抓取占比持续下降为通过 |
| 结构化数据必填项 | Rich Results Test 测帖子页；`python3 scripts/schema_lint.py URL` 查 JSON-LD 引用与占位符 | 论坛帖有 `author.name`、`datePublished`、正文；无 error 为通过 |
| 无 UGC 类人工处置 | GSC「人工处置」报告 | 无 "User-generated spam" 与 "Site abused with third-party spam" 为通过 |
| 站内搜索页不被抓取 | `python3 scripts/robots_posture.py https://example.com/robots.txt --json` 看规则；`curl -s https://example.com/robots.txt \| grep -i 'disallow: /search'` | 命中 `/search` 规则为通过 |
| 已索引的搜索页 | `site:example.com inurl:search` 抽查；GSC「网页」报告筛 `/search` | 只有按第六节四条件放开的页面被索引为通过 |
| robots 与 noindex 不自锁 | 对同一 URL 同时查 robots.txt 规则和页面 noindex | 想移出索引的页面可抓且带 noindex 为通过；两者并存为失败 |
| 站内搜索事件在采集 | GA4「报告 > 互动 > 事件」里有 `view_search_results`，且「搜索字词」维度有值 | 有数据为通过 |
| 空结果页 | 搜一个必然无结果的词，`curl -s 结果页 \| grep -io '<meta[^>]*noindex[^>]*>'` | 输出 noindex 且页面给出替代入口为通过 |

## 来源

- Google 官方：[UGC Fresh Data Program](https://developers.google.com/search/docs/appearance/ugc-fresh-data-program)；[Prevent user-generated spam](https://developers.google.com/search/docs/monitor-debug/prevent-abuse)；[链接属性 rel=ugc](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)；[人工处置报告](https://support.google.com/webmasters/answer/9044175)；[抓取预算](https://developers.google.com/crawling/docs/crawl-budget)；[分面导航](https://developers.google.com/crawling/docs/faceted-navigation)；[robots.txt 介绍](https://developers.google.com/search/docs/crawling-indexing/robots/intro)；[robots meta 规范](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)；[robots.txt 博客 2025-03](https://developers.google.com/search/blog/2025/03/robotstxt-flexible-way-to-control)；[URL 参数工具下线](https://developers.google.com/search/blog/2022/03/url-parameters-tool-deprecated)；[QAPage](https://developers.google.com/search/docs/appearance/structured-data/qapage)；[DiscussionForumPosting](https://developers.google.com/search/docs/appearance/structured-data/discussion-forum)；[ProfilePage](https://developers.google.com/search/docs/appearance/structured-data/profile-page)；[论坛与主页标记发布 2023-11-27](https://developers.google.com/search/blog/2023/11/discussion-and-profile-markup)；[评价摘要](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)；[结构化数据通用指南](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)；[文档更新日志](https://developers.google.com/search/updates)；[Reddit 合作公告](https://blog.google/company-news/inside-google/company-announcements/expanded-reddit-partnership/)；[hidden gems 公告](https://blog.google/products-and-platforms/products/search/google-search-perspectives/)；[GA4 增强型衡量](https://support.google.com/analytics/answer/9216061)。
- 平台：[Reddit 旧版开源代码](https://github.com/reddit-archive/reddit/blob/master/r2/r2/lib/db/_sorts.pyx)；[Quora 撤销合并](https://help.quora.com/hc/en-us/articles/360001043426-How-do-I-unmerge-my-question)；[知乎盐值](https://www.zhihu.com/term/credit)。
- 第三方：[Ahrefs Discussions and forums 分析](https://ahrefs.com/blog/discussions-and-forums-serps/)；[Reuters 2024-02-22](https://www.reuters.com/technology/reddit-ai-content-licensing-deal-with-google-sources-say-2024-02-22/)；[Inflow：站内搜索页是否索引](https://www.goinflow.com/blog/should-internal-search-urls-be-indexed/)；[seo.to Coursera 案例](https://seo.to/case-studies/coursera-course-catalog)。
- 2026-10-18 删除或改写的旧说法见证据账本 C3：「Data API 是自建论坛拿不到的通道」（已有申请制计划）、「Google 发言人 2026-08 否认偏好」（未找到原始报道）、「agentInteractionStatistic 是 AEO 新字段」（2023 年起已受支持）、「UGC 商品页转化显著更高」（无来源）等。
