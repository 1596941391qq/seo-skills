# 按站型的 SEO 打法手册(八卡+两垂直扩展卡)

用途:接单/开局先认站型,取对应打法卡定 KPI、渠道、防死清单与 pSEO 方向。
分工:本文管「打法层」;页面类型、URL 层级与各站型深读在 [site-type-templates.md](../technical/site-type-templates.md)(互为表里,不重复);通用打法流程见 [playbooks.md](../technical/playbooks.md);pSEO 上线闸门见 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md)。
基准数据均标注来源级别与日期(官方/报告/观察/共识);报告级数字用于对标,不用作对客承诺。2026-10-21 重核:第三方博客的数字已逐个打开原页面核对,核不到的已删;每卡的 URL 型谱、占比阈值(如 >30%、>60%)是本套件的判型启发式,不是外部统计。
⑨招聘/⑩房产(2026-10-12 增补)是⑦ Marketplace 的**垂直变体卡**:共用⑦的供需底盘与「库存密度先行」纪律,各叠垂直红线——判型命中⑦且供给为职位/房源时,升级取对应扩展卡。

**Schema 提示(各卡通用)**:各卡 Schema 组合里的 FAQPage 与 HowTo——Google 的 FAQ 和 How-to 富结果都已不再展示([日期与来源](facts.md#rich-results));这两种标记只在要给其它系统用时保留,Google 没有专门的 AI Schema,Schema 对 AI 引用没有独立效应的证据见 [geo-evidence.md](../content/geo-evidence.md)。Article 在 Google 文档里没有必填属性,Organization 也没有([Article](https://developers.google.com/search/docs/appearance/structured-data/article)、[Organization](https://developers.google.com/search/docs/appearance/structured-data/organization),页面日期 2026-09-08)。

## 站型识别判别法(R1-4,识别结果喂给 [strategy-fit.md](strategy-fit.md))

输入=site_crawl 的 crawl.json(URL 清单/edges)+ site_audit 的 schema 发现。三步判:
①**URL 型谱**——路径段直方图取前 10,对照各卡"识别信号"的型谱;②**schema 类型分布**——JSON-LD 主类型占比;③**页面构成比例**——各面页面量占比。
**判型纪律**:单一信号不算数,型谱+schema+构成至少两处吻合才判型;**模糊或双信号强(混合站)→列前二站型连同证据让用户确认,不得静默选一**;判型结果写入 project.yaml 的 `site_type` / `site_type_secondary`,混合站主卡按 GSC 流量占比定、副卡只取对应小节。

**开局命令链约定(R1-6)**:各卡末节的「开局命令链」=接单后第一批精确命令,默认在套件根目录运行(`python3 scripts/…`);示例域名/页面路径/GSC 导出与日志文件名均为占位,按实际站点替换。`project.py init` + `project.py run triage`(R1-7,30 分钟首答)可作**任意站型**的前置体检链,各卡不逐条重复,仅①号卡演示完整用法。命令参数以 `--help` 为准;每卡末行给出配套示例(examples/)互引。

## ① SaaS / 软件营销站

**识别信号**

- URL 型谱:`/features/`、`/solutions/`、`/pricing`、`/compare/`·`/vs/`·`/alternatives/`、`/integrations/`、`/templates/`、`/customers/` 合计占比 >30%。
- schema 分布:SoftwareApplication+Organization 高频,FAQPage 散布;无 Product/Offer。
- 页面构成:营销页+博客为主,无购物车/结账流;blog 常占 20-50%。
- 混合判别:docs 子域/路径页 >30% → 记「SaaS+文档」双卡(营销面按①、参考面按⑤)。

**页面清单(必争 URL 集)**

- 核心转化面:`/`、`/features/<功能>`、`/solutions/<行业|角色>`、`/pricing`、`/customers/<案例>`。
- 比价拦截面:`/compare/<竞品>`(vs)、`/alternatives/<竞品>`、`/vs/` 集合页。
- 生态面:`/integrations/<app>`、`/templates/<用例>`、支柱指南 + 集群文(组织法见 [topic-cluster-templates.md](../research/topic-cluster-templates.md))。

**Schema 组合**

- SoftwareApplication(name/applicationCategory/operatingSystem)+ Organization;有真实用户评分才加 aggregateRating,禁止编造。
- pricing/vs/alternatives 页的常见问题写成可见正文;Google 的 FAQ 富结果已不再展示([日期](facts.md#rich-results)),FAQPage 标记没有富结果收益,是否保留看内容理解需要;博客 Article/BlogPosting 带作者(Article 无必填属性,作者为推荐属性)。
- 全站 BreadcrumbList;完整映射见 [schema-templates.md](../technical/schema-templates.md)。

**核心 KPI**

- 非品牌词 demo/trial 注册占比——品牌词占比升高≠SEO 增长,常是品牌广告假象。
- 免费试用/demo 请求的转化率:SaaS/B2B 软件中位 1.5–3%、头部四分位 5%+(Stackmatix 汇总 Wordstream、Unbounce 等行业研究,第三方,[原文](https://www.stackmatix.com/blog/website-conversion-rate-benchmarks),核对 2026-10-21)。
- 渠道 close rate:自然搜索约 14.6%、付费搜索 5.1%、付费社交 0.9%、展示 0.3%(Flighted B2B SaaS 基准,第三方,[原文](https://www.flighted.co/blog/b2b-saas-conversion-rate-benchmarks))——只作内部争取预算的参照,口径随公司而异。
- solution 页 vs feature 页流量结构:解决方案词落在 solution 页才算对位,错配即预警。
- AI 搜索流量质量:AI 来源访客转化率 14.2%,Google 自然流量 2.8%(Authoricy 文章引 Stackmatix 2025、1,200 万次访问,第三方单源,[原文](https://authoricy.com/blog/ai-search-conversion-benchmarks));旧稿把它写成"demo show rate"是错的,它是转化率。

**获取策略重点**

- vs/alternatives 矩阵截获竞品品牌词——SaaS 转化最高的词群,先打头三名竞品。
- 集成页三层结构:app 单页 → pair 页(A × B)→ workflow 页;量级来自 pair/workflow 层。Zapier 的 /apps/ 集成页按搜索意图分层(salt.agency 分析:月访问从 2020-11 的 119 万到 2023-11 的约 480 万,Zapier 称连接 6,000+ 个应用,[原文](https://salt.agency/blog/how-zapier-quadrupled-organic-traffic/));旧稿"5,000 工具生成约 5 万页"原文里没有,已删。
- 支柱内容 + 免费工具引流;G2/Capterra/目录外链垫权威底座。

**ABM 对齐(高客单补充)**

- 把 vs/alternatives/solution 词簇与销售命名账号清单做**关键词↔列名映射**:每个 target account 至少一个对位页(vs 其现有供应商/其行业 solution 页)。
- SEO 侧交付物=映射表+页面覆盖缺口审计;排名与流量按账号分组报,销售可直接消费。
- 如实注:套件无独立 ABM 体系(投放/SDR/意图数据编排不在范围)——本节只做 SEO 资产与销售列名的对齐层。

**典型死法**

- 博客海量发文无支柱集群,权重散在孤儿文,主题权威建不起来。
- 功能页打解决方案词、解决方案页打功能词——意图错配两头不收。
- vs/alternatives 页 find-replace 模板,GSC 整组 "Discovered–currently not indexed"。
- 核心内容全门禁(gated)无 SEO 可见落点,可索引面太小。
- 把品牌词流量增长当 SEO 成果汇报,预算被砍时原形毕露。

**pSEO 机会**

- 集成对 `app1 × app2` 与 `app × 用例` workflow 页。
- `行业 × 角色` 解决方案矩阵(每格要有该行业真实痛点文案与案例)。
- 模板库 `/templates/<场景>`(带下载/复制价值,天然外链资产)。

**开局命令链(R1-6)**

```bash
# 0) 建工作区+30 分钟首答(R1-7;--type 取本卡名,判型后回写 project.yaml)
python3 scripts/project.py init --site https://example.com --type "SaaS / 软件营销站"
python3 scripts/project.py run triage
# 1) URL 型谱判型(vs/alternatives/solutions 占比)+内外链图(孤儿支柱文现形)
python3 scripts/site_crawl.py example.com --max 1000 --out crawl.json --urls-out urls.txt
# 2) 比价拦截面重点页审计(vs/alternatives/pricing 各抽样本;--export-dir 出受影响 URL 清单)
python3 scripts/site_audit.py https://example.com/vs/rival https://example.com/pricing --json --export-dir exports/ > audit.json
# 3) solution/feature 词-页对位错配+蚕食(GSC Query×Page 矩阵导出)
python3 scripts/gsc_mining.py matrix.csv --mode matrix --json
# 4) 集成对 `app×app`/workflow 页与模板库的模式挖掘(30/25/20/15/10 打分)
python3 scripts/pseo_pattern_mining.py --gsc queries.csv --sitemap https://example.com/sitemap.xml --json
```

配套示例:[examples/citation-decision-demo-20261011](../../examples/citation-decision-demo-20261011/REPORT.md)(AI 引用缺口侧,比价/替代词形,合成数据);通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## ② 电商(DTC)

**识别信号**

- URL 型谱:`/c/`·`/collections/`·`/category/`(PLP)与 `/p/`·`/products/`(PDP)并存,cart/checkout 路径存在;`?filter=` 等参数 URL 量大。
- schema 分布:Product+Offer 全站高频(健康站 PDP 覆盖 >80%)+BreadcrumbList;无 SoftwareApplication。
- 页面构成:PDP+PLP 合计常 >60%;被索引的 facet 参数 URL 数是本型特征信号。
- 混合判别:导购/指南内容页 >25% → 「电商+媒体」,内容面按③卡取小节。

**页面清单(必争 URL 集)**

- 类目面:多级类目/PLP(`/c/<类目>/<子类目>`)、品牌页、品牌×类目页。
- 商品面:PDP(`/p/<商品>`)、变体归一后的规范 URL。
- 内容面:导购(best-of/gift guide)、尺码/材质/兼容指南、评论 UGC 页。

**Schema 组合**

- Product + Offer + BreadcrumbList,全站 PDP。Google Product 文档:Product 必填 name,并须有 review、aggregateRating、offers 之一;Offer 必填 price(或 priceSpecification.price),priceCurrency 与 availability 是推荐属性([Product snippet](https://developers.google.com/search/docs/appearance/structured-data/product-snippet),页面日期 2026-09-08);商家列表面的要求更严,以文档为准。
- AggregateRating/Review 仅挂页内真实评论;榜单页 ItemList;指南文 Article + FAQPage。
- Merchant Center 免费清单并行——结构化数据不替代 feed,两条腿都要。

**核心 KPI**

- 品类页 vs SKU 页流量结构:头部品类页应扛主要非品牌流量,SKU 页补长尾——倒挂说明类目词全输给了亚马逊/聚合站。
- 非品牌自然收入占比(报告口径先写进合同)。
- facet 索引泄漏量:被索引的 `?filter=`/`?color=` URL 数;DigitalApplied 2026-01 称 faceted navigation 是最常见的抓取预算杀手(第三方观点);Google 的抓取预算文档建议避免索引筛选与排序 URL(见 [large-site-managing-crawl-budget](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget))。
- 缺货排名品保留率(保留+标 availability 的比例)。
- PDP 评论覆盖率(有评论文本的 PDP 占比,养长尾与富结果)。

**获取策略重点**

- 品类页内链 + 导购内容包抄:品类词 SERP 常被 informational 榜单占据,爬梯打法见 [ecommerce-geo-ladder.md](../content/ecommerce-geo-ladder.md)。
- 数字 PR:新品测评/unboxing/礼物清单植入换外链与联盟分发。
- Google 免费 listing(Merchant Center)+ 图片搜索流量(DTC 图片占比常被低估)。

**ASO 桥(品牌词防御)**

- 有购物 App 的 DTC:品牌词 SERP 的 app pack 是移动端第一屏占地——商店页标题/描述带品牌词守住 pack 位(竞品投品牌词抢屏时尤其要紧)。
- web↔App 互认:商品 deep link 与 web URL 结构化对应(旧 App Indexing 说法,Google 现行做法本次未核),App 内商品页进 Google 索引补移动占位。
- 全量 ASO(商店关键词排名/评分运营)**明示不做**——本桥只管品牌词 SERP 占位与互认,不越界。

**典型死法**

- facet 组合失控,百万近重复 URL 吞掉爬虫预算,真页面反而收录慢。
- 变体各留一 URL,30 个近重复 PDP 互相蚕食。
- 缺货即 404,排名资产清零(正解:保留+标 availability;真死 SKU 301 到类目/替代品)。
- 厂商样板描述全站复制,PDP 千篇一律零增量。
- 类目页无导语文本,纯商品网格排不上;迁平台整站换 URL 无重定向表。

**pSEO 机会**

- `品牌 × 类目` 页与 `礼物场景 × 人群 × 价格`(`gifts for <person> under <price>`)。
- 兼容性页(`fits <型号>`/`for iPhone 17`)——自带真实需求分布。
- 材质/尺寸组合页;全部过 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md) 闸门,无需求组合不生成。

**开局命令链(R1-6)**

```bash
# 1) 判型+facet 泄漏口径(PDP/PLP 型谱;默认保留参数,参数 URL 量=索引泄漏面)
python3 scripts/site_crawl.py example.com --max 2000 --out crawl.json --urls-out urls.txt
# 2) PDP/PLP 样本审计:Product/Offer 三必填、变体 canonical、BreadcrumbList
python3 scripts/site_audit.py https://example.com/p/sample-pdp https://example.com/c/sample-plp --json --export-dir exports/ > audit.json
python3 scripts/health_score.py --input audit.json --json
# 3) 品牌×类目/兼容/礼物场景组合的模式挖掘与闸门打分
python3 scripts/pseo_pattern_mining.py --gsc queries.csv --sitemap https://example.com/sitemap.xml --json
```

品类词爬梯(品类页+导购内容包抄)深读锚:[ecommerce-geo-ladder.md](../content/ecommerce-geo-ladder.md)。
配套示例:暂无电商对位示例;通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## ③ 媒体 / 新闻 / 内容站

**识别信号**

- URL 型谱:日期路径(`/2026/10/…`)、`/news/`·`/articles/`·`/blog/`、作者页 `/author/`·`/writers/`;news sitemap 存在是强信号。
- schema 分布:NewsArticle/Article+NewsMediaOrganization+Person(作者)高频。
- 页面构成:文章页常 >70%,lastmod 高频新鲜;频道/section 页占比小。
- 混合判别:垂直医疗/法律/金融媒体=「③的面+⑧的合规红线」;挂工具计算器多→跨⑥。

**页面清单(必争 URL 集)**

- 频道面:首页、channel/section 页、topic hub(专题支柱聚合页)。
- 内容面:文章(NewsArticle 或常青 Article 分开规划)、作者实体页。
- 机器面:news sitemap、普通 sitemap、RSS;订阅/落地转化页。

**Schema 组合**

- NewsArticle/Article + NewsMediaOrganization + Person(作者,带 sameAs 指向社媒/维基)。
- 时间戳精确到秒,`dateModified` 必须真实(假新鲜度是负信号)。
- 视频报道 VideoObject;全站 BreadcrumbList 可省但频道面包屑建议保留。

**核心 KPI**

- Discover / Top Stories / 经典搜索三源流量构成:DigitalApplied 称 Discover 在不少出版商、新闻站和内容站的自然流量里占 30–50%(第三方文章,2026-02,未给方法)——单源依赖度是风险指标,以自家 GSC Discover 报告为准。
- 新稿首小时索引率与首日 CTR(新闻窗口期价值)。
- 订阅/回访/单 UV 会话深度,替代裸 PV 考核。
- 作者实体页收录率与知识面板命中数。

**获取策略重点**

- Publisher Center 收录 + news sitemap:时效内容必争 Top Stories 位。
- Discover 优化:≥1200px 宽大图、实体清晰、标题克制——2026-02 Discover 更新后,依赖耸动标题的站点流量掉 30–60%(DigitalApplied,第三方;Google 的 2026-02 Discover update 见 Status Dashboard,持续约 21 天)。
- 平台联合分发(Apple News/MSN)+ 社交引用回流;细则见 [discover-news-seo.md](../content/discover-news-seo.md)。

**典型死法**

- 标题党——2026-02 Discover 更新的主罚对象,整站级别的展示量萎缩。
- tag 页海量薄页,抓取预算与权重被稀释。
- 作者匿名无实体,权威度无处累积(News sitemap 也要求可归因)。
- 改版换 URL 不逐条 301,历史外链全断。
- 只追 PV 无订阅漏斗,算法一抖收入归零;通讯社稿原样转载,重复内容不收。

**pSEO 机会**

- 数据新闻库:每年更新的 "State of X 2026" 报告页,天然年更外链磁铁。
- 事件 × 地区报道模板页(重大事件的本地化角度)。
- topic hub 持续聚合旧稿吃实体词与 AI 引用。

**开局命令链(R1-6)**

```bash
# 1) news sitemap 合规(传具体文件勿传 index;--pub-name 比对站名一致性)
python3 scripts/news_sitemap_check.py --url https://example.com/news-sitemap.xml --pub-name "Example News" --json
# 2) 文章样本审计:NewsArticle/时间戳精确到秒/作者实体
python3 scripts/site_audit.py https://example.com/2026/10/sample-story --json > audit.json
# 3) 热点监控+四问闸门(--vertical=品类+品牌+竞品,不是 SEO 元领域;signal-id 取 watch 输出)
python3 scripts/trend_watch.py watch --market en --vertical "品类词 品牌名 竞品A"
python3 scripts/trend_watch.py gate --signal-id <signal-id> --exclusive data
# 4) 标题党/薄 tag 页六维内容抽检(页面正文另存 md 再跑)
python3 scripts/quality_rater.py story.md --market en
```

Discover/Top Stories 细则锚:[discover-news-seo.md](../content/discover-news-seo.md)。
配套示例:examples/trend-gate-geo-survey-20261011/(trend_watch watch→gate 全链;含首跑误用 SEO 元领域话题的更正记录)。

## ④ 本地服务

**识别信号**

- URL 型谱:`/services/<服务>`、`/locations/<城市>`;整站页面量小(常 <100);页面含 NAP 文本与 `tel:` 链接。
- schema 分布:LocalBusiness 精确子类(Plumber/Dentist…)+Service;关联 GBP(intake 确认)。
- 页面构成:服务页+位置页为主,无购物车、无文章矩阵。
- 混合判别:多商家入驻+招商页 → 跨⑦ Marketplace(多商家=⑦,单商家=④)。

**页面清单(必争 URL 集)**

- `/`、`/services/<每项服务一页>`(本地自然排名 #1 因素,Whitespark 2026)、`/locations/<城市>`。
- `城市 × 服务` 页仅在能拿出真实本地证据时做;about/team(信任面)、评价与案例页。
- 六行业(餐饮/医疗/法律/家居/教育/汽车)的合规红线与 schema 正解全表在 [site-type-templates.md](../technical/site-type-templates.md),此处不重复。

**Schema 组合**

- LocalBusiness 精确子类(Plumber/Dentist/LegalService…,主类目选错是第一负面因素)。
- SAB(服务区域业务):areaServed、不展示 streetAddress;多门店页独立 `@id` 经 `branchOf` 归一到 Organization。
- Service + FAQPage + BreadcrumbList;医疗实体禁挂 aggregateRating(富结果受限)。

**核心 KPI**

- 本地包网格排名 ARP/ATRP/SoLV 三口径同报(公式与工具见 [local-grid-ranking.md](../monitoring/local-grid-ranking.md))。
- GBP 行为量:来电、问路、预约。
- 评价节奏与回复:DigitalApplied 2026-03 称近 90 天的评价、店主回复率与本地包位置的相关性更强(第三方观点,未给可复核方法);旧稿的"断档 18 天""10 条基准线""88% 消费者在意"找不到出处,已删。Google 官方只说本地结果主要基于关联性、距离和知名度([GBP 帮助](https://support.google.com/business/answer/7091))。
- 服务页 vs 位置页流量结构;`tel:` 点击与表单提交归因。

**获取策略重点**

- GBP 运营:主类目+最多 4 个次类目、帖子、Q&A 退场后常见问题写进商家描述(Q&A API 2025-11-03 停用,见 [local-grid-ranking.md](../monitoring/local-grid-ranking.md) 第六节)。
- Ask Maps(地图里的 Gemini 对话式答案,2026-03 美印上线、2026-08 扩到 150 多个国家和地区):回答取评价正文、贡献者提示和资料属性里的细节,网格排名测不到;做法见 [local-grid-ranking.md](../monitoring/local-grid-ranking.md) 第五节之二。
- 评价引擎:完工短信征集、不门控(违反 Google 假互动政策与 FTC)、持续回复。
- 本地链接:"best of" 榜单 + 商会/赞助/行业目录(本套件口径);第三方文章称 2026-03 更新后本地包更看重网站与本地实体的关联信号(DigitalApplied,未核方法)。

**典型死法**

- 城市×服务 doorway 页:swap 测试(换城市名仍通顺)不过=整组去索引或合并(本套件判据;Google 垃圾政策把 doorway 页列为垃圾,见 [spam policies](https://developers.google.com/search/docs/essentials/spam-policies));旧稿的"HVAC 案例掉 80%"找不到出处,已删。
- SAB 业务乱展示街道地址(违反指南),或实体店硬藏地址。
- 30+ 位置页模板复制、唯一内容 <60%(50+ 强制停线说明)。
- 评价征集三天打鱼,速度断档。
- GBP 网站链接指到最强页面(有压制自然排名的案例风险)。

**pSEO 机会**

- `服务 × 城市` 页——唯一可行模式但必须过证据闸门:真实案例/本地照片/区域实据,无证据组合不生成(闸门见 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md))。
- 门店定位器 SSR/SSG 可爬,不留 CSR 黑洞。

**开局命令链(R1-6)**

```bash
# 1) 整站页量小(常 <100):全量爬取判型(服务页/位置页型谱+NAP 文本)
python3 scripts/site_crawl.py example.com --same-host --max 100 --out crawl.json --urls-out urls.txt
# 2) 本地四节体检:NAP 一致性/GBP 抓取/LocalBusiness 精确子类/落地页本地信号(--url 也可传 GBP 页)
python3 scripts/local_audit.py --url https://example.com --name "Example Plumbing" --addr "123 Main St, Springfield, IL 62701" --phone "2175550123" --json
# 3) 本地包网格排名三口径同报(ARP/ATRP/SoLV;CSV 列 keyword,grid_point,rank)
python3 scripts/grid_rank.py rank_data.csv --detail
# 4) 服务页样本审计(每项服务一页=本地自然排名 #1 因素)
python3 scripts/site_audit.py https://example.com/services/drain-cleaning --json > audit.json
```

网格排名公式与工具深读锚:[local-grid-ranking.md](../monitoring/local-grid-ranking.md);GBP 行为量(来电/问路/预约)在 GBP 后台取数,套件外。
配套示例:暂无本地对位示例;通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## ⑤ 文档 / 开发者站

**识别信号**

- URL 型谱:`/docs/`、`/api/`·`/reference/`、`/guides/`、`/changelog`,版本路径 `/v1`·`/v2`;常独立子域 docs.*。
- schema 分布:TechArticle+HowTo;可见文本代码块密度高(site_crawl 抓取特征)。
- 页面构成:文档页常 >60%;quickstart/getting-started 页存在。
- 混合判别:与①同域(marketing 根域+docs 子域)最常见——分别取卡不合并。

**页面清单(必争 URL 集)**

- 入门面:`/docs`、quickstart、guides(任务型教程)。
- 参考面:API reference(逐参数+可复制示例)、SDK 语言页、错误码/troubleshooting 页。
- 生态面:changelog、integrations、status 页。

**Schema 组合**

- TechArticle(教程)+ HowTo(步骤型)+ FAQPage + BreadcrumbList + Organization。
- 侧栏目录与 URL 层级一致;版本化时明确规范版本,旧版本 noindex 策略写死。

**核心 KPI**

- AI 引用份额:用 `citation_panel.py` 对编程类提问分引擎采样;"docs 是首选引用源""ChatGPT 占 AI 推荐流量 ~88%"没有可核出处,已删。
- AI 爬虫抓取量与 ChatGPT/Copilot referral 增速(基线看自家 GA4 的 AI Assistant 通道,涨速比绝对值重要;"~1% 是常态基线"没有出处,已删)。
- quickstart 完成率(漏斗顶部质量)。
- 站内搜索零结果率(文档覆盖缺口最直接信号)。
- 旧版本页索引健康:该 noindex 的版本是否还在收录、是否蚕食最新版。

**获取策略重点**

- 对 AI 爬虫明确开放策略(GPTBot 等,见 [ai-crawler-policy.md](../technical/ai-crawler-policy.md))——封锁等于把 AI 答案位让给竞品文档。
- 开发者社区答疑:StackOverflow/Reddit/HN 带文档深链,答案即外链。
- 集成伙伴文档互链 + GitHub README/官网导流。

**典型死法**

- 纯客户端渲染,AI 爬虫与传统爬虫都读不到正文(<500 可见字符判 CSR 兜底)。
- 全版本页可索引,自我蚕食(v1/v2/v3 同关键词)。
- 把 llms.txt 当万能药:500M 事件分析显示 AI 爬虫几乎不抓它(观察级),Google 官方 2026 确认对排名无影响——正解是常规可爬性+清晰结构。
- 没有错误码页——开发者最高频的长尾词群(`<service> error 429`)拱手让人。
- API 重构后旧路径 404,生态外链与教程引用集体断裂。

**pSEO 机会**

- 错误码百科:`<service> error <code>` 每码一页(带成因与修复)。
- `语言 × 功能` SDK 示例页;`集成 × 平台` how-to。
- changelog 条目独立化吃 `<功能> release` 词。

**开局命令链(R1-6)**

```bash
# 1) docs 子域全量爬取:版本路径/错误码页覆盖盘点(--same-host 收紧到 docs 本身)
python3 scripts/site_crawl.py docs.example.com --same-host --max 1000 --out crawl.json --urls-out urls.txt
# 2) AI 爬虫放行矩阵(封引用型 bot=把 AI 答案位让给竞品文档)
python3 scripts/robots_posture.py https://docs.example.com/robots.txt --signal visibility --json
# 3) quickstart 的 CSR 兜底+AI 视图层(dry-run 预览;--apply 才写盘,部署由人完成)
python3 scripts/ai_views.py --url https://docs.example.com/quickstart --json
# 4) AI 引荐流量与 AI 爬虫 UA 到访增速(服务器日志;GA4 归因正则另配 --attribution)
python3 scripts/ai_referral_log.py access.log --classify --bot-ua
```

放行三态决策锚:[ai-crawler-policy.md](../technical/ai-crawler-policy.md)。
配套示例:[ai-views-example.com-20261011](../../examples/ai-views-example.com-20261011/REPORT.md)(ai_views 离线重放全链)。

## ⑥ 工具 / 免费计算器站

**识别信号**

- URL 型谱:`/tools/`·`/calculators/`·`/converters/`·`/generators/`;参数化结果分享 URL(`?input=…`)。
- schema 分布:WebApplication/SoftwareApplication+配套 FAQPage。
- 页面构成:工具页与配套说明文成对出现;「工具页 vs 配套文」流量比是本型特征指标(纯工具无文=信息词全丢)。
- 混合判别:工具嵌在 SaaS 站 → 主卡①、工具只作引流资产;独立多工具矩阵→按⑥。

**页面清单(必争 URL 集)**

- 工具面:`/tools/<工具>`、`/calculators/<主题>`(页面即产品)。
- 内容面:每工具配套「怎么算/公式/结果解读」文;公式页单独可排名。
- 传播面:嵌入代码页(widget 换署名链接)、结果分享页。

**Schema 组合**

- WebApplication/SoftwareApplication + FAQPage(工具常见问题)。
- 配套文 HowTo(步骤)+ Article + BreadcrumbList。

**核心 KPI**

- 每工具页引用域获取速度:免费工具=最自然的 linkable asset(业内说法,未核到一手来源)。
- 工具→注册/付费转化率(免费到付费的漏斗必须能归因)。
- 嵌入 widget 与分享链接带来的回链数。
- 品牌词月增长(工具被口碑传播的滞后指标)。
- 配套文 vs 工具页流量比:纯工具无文=信息词全丢。

**获取策略重点**

- 工具本身即链接磁铁:Reddit/论坛/newsletter 自发推荐——做「省时间/算得清」的工具,不做玩具。
- 配套内容打 "how to calculate X / X formula" 词群并双向内链工具页。
- Product Hunt/工具目录提交 + 提供嵌入 widget 换署名链接(seomatic 式 100+ 免工具矩阵可参考)。

**典型死法**

- 纯 JS 工具零可索引文本:公式、说明、示例输入全不进 HTML。
- 计算结果不生成可分享 URL——无独立落地页可排名、无传播钩子。
- 每个输入变体造一页,doorway 式膨胀。
- 工具与主营业务无关:流量不转化还稀释主题相关性。
- 工具包几 MB JS,CWV 崩掉拖累整站质量信号。

**pSEO 机会**

- 参数化结果 URL:固定输入的分享链接各成一页(结果数据真实唯一,非样板)。
- 单位/货币/进制换算矩阵(每页带换算表静态文本)。
- `行业 × 计算器` 变体页(每页配该行业口径与公式说明)。

**开局命令链(R1-6)**

```bash
# 1) 判型:工具页/配套文成对结构型谱(/tools/·/calculators/·/converters/)
python3 scripts/site_crawl.py example.com --max 500 --out crawl.json --urls-out urls.txt
# 2) 工具页+配套文成对审计(纯 JS 零可索引文本=本型第一死法)
python3 scripts/site_audit.py https://example.com/calculators/roi https://example.com/blog/roi-formula --json > audit.json
# 3) 参数化结果 URL(`?input=` 分享页)与换算矩阵的模式挖掘(--urls 走离线覆盖度口径)
python3 scripts/pseo_pattern_mining.py --gsc queries.csv --urls urls.txt --json
# 4) 引用域基线(Ahrefs/Semrush/GSC 外链导出统一导入,后续按月比增速)
python3 scripts/backlink_import.py ahrefs.csv --format auto --out unified-backlinks.csv
```

配套示例:暂无对位示例;通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## ⑦ Marketplace / 平台型

**识别信号**

- URL 型谱:双侧结构 `/s/<供应者>`+`/c/<类目>`+`/<城市>/<类目>`;站内搜索/facet 页多;best-of 榜单页。
- schema 分布:Service/Product+提供者实体(Person/Organization/LocalBusiness)+AggregateRating+ItemList 混布——**全站 schema 谱最杂**是本型指纹。
- 页面构成:供给详情页占大头;空/薄列表页占比是本型暴雷指标。
- 混合判别:与④易混(多商家=⑦单商家=④);带导购内容矩阵→跨③。

**页面清单(必争 URL 集)**

- 供给侧(SEO 库存):`/s/<商家|服务者>` 详情页、`/c/<类目>` 列表页、入驻招商页。
- 需求侧:`/<城市>/<类目>` 组合页、`/<类目>/<属性>` 页、best-of 榜单页。
- 信任面:如何运作/保障/退款政策页(平台型转化前置)。

**Schema 组合**

- Service/Product + 提供者实体(Person/Organization/LocalBusiness)+ 真实 AggregateRating。
- 榜单页 ItemList;全站 BreadcrumbList;同一商家多入口统一规范 URL。

**核心 KPI**

- 供给侧 vs 需求侧流量比:健康曲线是先供后需——倒挂=空货架在吃流量然后流失。
- 类目供需密度:每页可售条目数,密度达标才推需求词。
- 空/薄列表页索引占比(平台型经典暴雷指标,与 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md) 的 not-indexed 占比同源)。
- `城市×类目` 页与类目搜索页的蚕食监控。
- UGC 质量分:审核前后差值、重复/垃圾条目率。

**获取策略重点**

- 供给侧先行:批量收录商家/商品页做「SEO 库存」(Zapier/Booking 范式),库存密度达标才开需求侧词。
- 富结果军备:价格/评分/库存结构化数据拿 SERP 占位(平台 SERP 竞争即富结果竞争)。
- `品牌 × 城市`、`属性 × 类目` 长尾矩阵截流巨头(thebcms pSEO 案例集范式)。

**典型死法**

- 需求页先于供给上线,大量空类目页被批量去索引,再难翻身。
- 同一商家多入口多 URL 无归一(搜索页/类目页/标签页三个版本)。
- UGC 无质量门槛,整站质量信号被垃圾条目拖垮。
- 列表纯 AJAX 分页不可爬,第 2 页起的库存对引擎不存在。
- 冷启动只买付费流量填需求,SEO 库存始终为零,退出成本越滚越高。

**pSEO 机会**

- `城市 × 类目` 矩阵:每格库存 ≥ 阈值才生成(典型 5-10 条起)。
- 属性长尾:pet-friendly / 24h / open-now / accepts-insurance。
- best-of 榜单页(真实评分与评价摘要,非软文);比价/询价聚合页。

**开局命令链(R1-6)**

```bash
# 1) 双侧结构判型+空/薄列表页盘点(/s/ 供给详情+/c/ 类目列表)
python3 scripts/site_crawl.py example.com --max 2000 --out crawl.json --urls-out urls.txt
python3 scripts/site_audit.py https://example.com/c/sample-cat https://example.com/s/sample-provider --json > audit.json
# 2) 六阶段漏斗:空货架在 availability/indexability 层现形(供给先行纪律的量化口径)
python3 scripts/traffic_funnel.py --audit audit.json --gsc pages.csv --json
# 3) `城市×类目` 批次上线闸门(数据闸/爆炸预警/唯一度/样板比/页型地板)
python3 scripts/pseo_batch_gate.py --records city-cat-batch.jsonl --rendered dist/
# 4) 批次索引率曲线:预注册判读,90 天零展示出 prune 工单
python3 scripts/pseo_cohort.py init --cohort_id city-cat-v1 --template-version v1 --urls urls.txt
python3 scripts/pseo_cohort.py ingest --cohort city-cat-v1 --gsc pages.csv
```

闸门数字锚:[programmatic-seo-gates.md](../technical/programmatic-seo-gates.md)。
配套示例:暂无对位示例;通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## ⑧ YMYL(医疗 / 金融 / 法律)

**识别信号**

- 判型主体是**主题而非 URL**:内容命中医疗/法律/金融主题词(条件/症状/practice-areas/费率/赔偿)。
- URL 型谱:`/conditions/`·`/symptoms/`、`/practice-areas/`、实名作者页 `/author/<实名>`、`/how-we-review` 类方法论页存在。
- schema 分布:Person+hasCredential+MedicalWebPage/LegalService 分型;reviewedBy(医审/法审)署名。
- 混合判别:媒体型 YMYL(③的流量打法+⑧的合规红线)最常见——两卡并用,红线优先。

**页面清单(必争 URL 集)**

- 专业面:`/<条件|业务>` 每题一页(医疗 condition 页/法律 practice area 页/金融产品解读页)。
- 信任面:作者资质页(实名+执照+经历)、编辑政策与方法论页(how we review/test)、医审/法审署名机制。
- 工具面:计算器/自查评估页;免责与隐私页(合规面)。

**Schema 组合**

- Person + hasCredential + reviewedBy(医审/法审实体);Organization。
- Article + 作者署名;FAQPage 谨慎使用(医疗答案断章风险)。
- 医疗:MedicalWebPage;执业类:LegalService/Dentist 等分型;医疗实体禁 aggregateRating(合规红线详见 [site-type-templates.md](../technical/site-type-templates.md) 六行业表)。

**核心 KPI**

- 实名作者实体被知识面板/AI 答案引用数:Sure Oak(第三方文章,2026-08)主张 YMYL 的财经内容需要署名、可核实资质的作者;这是该机构的观点,不是 Google 规则。
- 医审/法审覆盖率与复核日期新鲜度(旧内容无复核=静默下滑)。
- 品牌词 vs 非品牌比:YMYL 转化重度依赖品牌信任,纯非品牌流量转化差。
- AI Overview/聊天引擎引用份额(见 [ai-citation-patterns.md](../content/ai-citation-patterns.md))。
- 合规分四项:署名/来源/引用/利益披露——起查用 [core_eeat.py](../../scripts/core_eeat.py)。

**获取策略重点**

- 资质署名 + 专业审阅制度:是排名前提,不是加分项。
- 权威外链:原创数据/研究做数字 PR,换学术机构与政府类引用(一条 .edu/.gov 级引用>百条目录)。
- 第三方声誉面:Reddit/权威论坛/百科的被动提及——AI 检索与 YMYL 质量评估都重,配品牌词防御页。

**典型死法**

- 匿名或假名作者,整站 YMYL 权重归零。
- 无编辑政策/方法论/复核日期页,E-E-A-T 无处验证。
- 医疗实体强加 aggregateRating 或征集患者评价(HIPAA+富结果双输;日本患者体验谈属医疗广告禁止项)。
- 旧医疗/费率内容断更无复核:利率、法案、指南一变即失准。
- AI 批量生成无审内容,一次质量更新整站清退。

**pSEO 机会**

- `费用 × 地区` 页:`cost of <procedure|case> in <state>`——医疗/法律通用强需求。
- 法条/资格 × 州页(法律);监管 × 产品页(金融)。
- 计算器矩阵(贷款 APR/赔偿金/税费/报销)——嫁接⑥号工具站打法;症状自查工具页(结果页必须带就诊指引与免责)。

**开局命令链(R1-6)**

```bash
# 1) 判型:主题词命中(conditions/practice-areas/费率)+实名作者页型谱
python3 scripts/site_crawl.py example.com --max 500 --out crawl.json --urls-out urls.txt
# 2) CORE-EEAT 机械化(GEO/SEO 双分+veto 封顶;合规四项[署名/来源/引用/披露]起查)
python3 scripts/core_eeat.py --url https://example.com/conditions/sample
# 3) 信任信号四类:证言/社会证明/风险反转/权威(方法论页 how-we-review 一起查)
python3 scripts/trust_signals.py https://example.com/how-we-review
# 4) 六维内容评分:证据行核验/复核新鲜度(页面正文另存 md 再跑)
python3 scripts/quality_rater.py condition-page.md --market en --keyword "<条件|业务主题词>"
```

AI 引用份额口径锚:[ai-citation-patterns.md](../content/ai-citation-patterns.md)。
配套示例:暂无 YMYL 对位示例;AI 引用份额的面板采样形态(通用)见 [citation-panel-demo-20261010](../../examples/citation-panel-demo-20261010/REPORT.md)(合成数据)。

## ⑨ 招聘 / Job 站(⑦的垂直变体:供给=职位,2026-10-12 增补)

**识别信号**

- URL 型谱:`/job/`·`/jobs/`、`/company/<雇主>`、`/salary/`·`/salaries/`、`/jobs-in-<城市>`·`/<职能>` 列表页;apply 外跳或 ATS 内嵌流。
- schema 分布:JobPosting 全站高频(本型指纹)+ hiringOrganization(Organization);公司页可挂 EmployerAggregateRating。
- 页面构成:职位详情页占比大且**平均存活期以周计**(高 churn 是本型独有);职位页:公司页数量比=供需密度。
- 混合判别:多雇主聚合=⑦底盘+本卡;只发自家职位的 ATS/官网招聘页=单侧形态(页面清单仍适用,重复内容边界不适用)。

**页面清单(必争 URL 集)**

- 职位面:`/job/<slug>` 详情页、`<职能> jobs`·`/jobs-in-<城市>`·`remote <职能>` 分类与组合页。
- 公司面:`/company/<雇主>`(雇主品牌词承接+评价聚合+在招职位列表)。
- 薪资面:`/salary/<职称>`(自有或来源可溯的聚合薪资库——强需求常青层)。
- 雇主面:post a job 招商页与定价页(第二受众转化位)。

**Schema 组合(JobPosting 全字段纪律)**

- 必填五件(官方):title/description/hiringOrganization/jobLocation/datePosted;远程岗加 jobLocationType=TELECOMMUTE(+applicantLocationRequirements);推荐 validThrough/baseSalary/employmentType/identifier;schema.org v30.0(2026-03-19)新增 jobDuration(合同期信号)。
- **datePosted 时效红线**:官方**无「90 天自动下线」硬规则**(2026-10-12 核实)——过期职位的官方下线机制三选一:validThrough 置于过去/页面返回 404·410/摘除 JobPosting 标记,并以 **Indexing API** 通知(官方明确推荐优先于 sitemap);「90 天内下线」是行业运营惯例级(多数板 30-90 天自动下架,观察级),可作自家 SLA 默认值。
- 富结果现状:JobPosting 结构化数据仍在 Google 官方文档与职位搜索体验内(2026-10-12 核实);垂直盘点报告口径「招聘版 3.605608 不再富结果」的版本号与出处无法核实(全网检索无果)——**按缺口标注、不采信**,以官方文档为准。
- 同一职位多 URL canonical 归一(官方要求);公司页 Organization+EmployerAggregateRating(评分必须真实,禁编造)。

**双受众词簇(求职者 vs 雇主)**

- 求职者簇:`<job title> jobs`、jobs near me、remote `<role>`——落职位详情/分类页。
- 雇主簇:post a job、job board pricing、how to hire `<role>`——落招商页/雇佣指南;两簇 intent 分层不得互抢(方法见 [keyword-intent-taxonomy.md](../research/keyword-intent-taxonomy.md))。

**IDX 类比:职位聚合 vs 自有 ATS 的重复内容边界**

- 聚合器接入多源 ATS → 同一职位在雇主官网/Indeed/自家多版本共存。边界纪律:每源唯一 slug+来源标识;聚合页必须加自有增量(薪资对比/公司评价/申请转化数据)才值得独立索引;纯转发无增量时 canonical 给源或不另出页——与⑩的 IDX 同构(行业共识)。

**核心 KPI**

- apply 点击率(职位页→申请动作)与申请完成率——本型的 demo/trial 等价物。
- 职位页收录率与「过期仍在索引」占比(过期堆积=质量信号流失,直接对应第一死法)。
- 新职位首收录时延(发布→进索引,Indexing API 生效后的基线)。
- 雇主侧线索:post a job 页转化(第二受众的收入)。

**典型死法**

- **过期职位堆积成垃圾页**(本型第一死法):职位下架后页面不摘、schema 不摘、sitemap 照报——爬虫预算与站点质量双输,新职位收录被拖慢。
- 全站 description 用雇主原文镜像,零增量零排名(同⑩ IDX 镜像病)。
- 求职者词与雇主词塞进同一漏斗,两头转化都低。
- 薪资页无自有数据源编数字——YMYL 边缘内容,口径必须可溯。

**pSEO 机会**

- `<职称> jobs in <城市>`·`remote <职称>` 矩阵——每格在招库存 ≥ 阈值才生成(过 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md) 闸门)。
- 薪资库 `<职称> salary`(数据可溯,常青资产)。
- `职称 × 级别|年限` 变体页;雇佣指南 how to hire `<role>` 吃雇主簇。

**开局命令链(R1-6)**

```bash
# 1) 判型:职位/公司/薪资页型谱+过期职位堆积面(高 churn 详情页)
python3 scripts/site_crawl.py example.com --max 2000 --out crawl.json --urls-out urls.txt
python3 scripts/site_audit.py https://example.com/job/sample-job --json > audit.json
# 2) 新职位收录通知:key 生成+批量提交(IndexNow 覆盖 Bing/Yandex/Naver;Google 侧官方 Indexing API 在套件外,勿混称)
python3 scripts/indexnow.py key --out .
python3 scripts/indexnow.py submit --host example.com --key <KEY> --urls new-jobs.txt
# 3) 过期职位退役三查(入链/外链/排名词)→ NO-GO/prune(410)/merge(301)/watch
python3 scripts/prune_gate.py --urls expired-jobs.txt --gsc queries.csv --crawl crawl.json
# 4) `<职称> jobs in <城市>` 批次闸门(每格在招库存 ≥ 阈值才生成)
python3 scripts/pseo_batch_gate.py --records jobs-batch.jsonl
```

闸门锚:[programmatic-seo-gates.md](../technical/programmatic-seo-gates.md);JobPosting 字段与下线三选一见本卡 Schema 节。
配套示例:暂无对位示例;通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## ⑩ 房产 / Real Estate(⑦的垂直变体:供给=房源,2026-10-12 增补)

**识别信号**

- URL 型谱:`/listings/`·`/homes-for-sale/`·`/property/<id>`、`/<城市>-real-estate`、`/community/`·`/neighborhood/`、`/agent/`·`/realtor/`;MLS/IDX 字段特征(mls id、经纬度)。
- schema 分布:RealEstateListing/Residence+Offer 系、RealEstateAgent(Person)+LocalBusiness;无 Product/SoftwareApplication。
- 页面构成:房源详情页量大且随成交/下架**高频失效**;社区页/经纪页是常青层——「易失效详情+常青地方页」两层结构是本型指纹。
- 混合判别:多经纪/MLS 供给=⑦底盘+本卡;自有楼盘开发商=④侧形态;挂估值计算器→嫁接⑥。

**页面清单(必争 URL 集)**

- 房源面:`/property/<id>` 详情页(IDX/MLS 拉取)、在售/待售/已售状态页。
- 地方面:`/<城市>-real-estate` 市场页、`/<社区>` neighborhood 页(常青:市场数据+学区+通勤)、`<城市> housing market` 报告页。
- 人方面:`/agent/<经纪人>`(品牌词+评价实体页)。
- 卖家面:`/home-valuation`·`/sell-my-house`(转化价值最高的一层)。

**Schema 组合**

- 类型选择:RealEstateListing(schema.org 词汇表类型,描述 lease/sell 类 offers)+ Residence/SingleFamilyResidence 承属性细节,价格走 Offer 的 price 或 priceSpecification 嵌套(均现行有效,2026-10-12 核实)。**注意:Google 无 RealEstateListing 富结果**(官方搜索画廊未收录)——标记只是机器可读的实体描述,Google 不据此给富结果;Schema 对 AI 引用没有独立效应的证据见 geo-evidence.md;度假租赁另有官方 VacationRental 结构化数据,勿混用。
- **IDX 重复内容纪律**:同一 MLS 房源出现在成百上千经纪站——镜像页必须有自有增量(本地市场解说/图集/估价上下文)才值得独立索引;纯镜像 canonical 到 MLS 源页;canonical 策略在 MLS/IDX 协议层约定,不静默处理(行业共识级)。
- 经纪页 RealEstateAgent+LocalBusiness(真实评价);社区页/报告页 Article;全站 BreadcrumbList。

**Fair Housing 合规红线(美国市场必读)**

- FHA 七保护类:种族/肤色/宗教/性别/残障/家庭状况/国籍——房源与社区描述禁任何倾向性暗示。
- 禁词示例(行业词表口径:HUD 1995 广告备忘+NAR/MLS 实操清单):safe/quiet neighborhood、perfect for families、childless/empty nesters、walk to church·Christian home、adults only·no kids、able-bodied、族群/宗教社区名——**铁律:describe the property, not the people(写属性不写人)**。
- pSEO 模板同过此线:任何按人群/宗教/家庭结构定向的组合字段直接禁——合规优先于需求量。

**双受众(买家词 vs 卖家词)**

- 买家簇:homes for sale in `<城市>`、`<社区>` real estate、`<城市>` open houses——落房源/地方页。
- 卖家簇:sell my house、home valuation `<城市>`、how to sell——落估值工具+卖家指南(高转化,嫁接⑥工具站打法)。

**核心 KPI**

- lead 表单提交(看房预约/估值请求)与房源页→lead 转化率。
- 房源页收录率与**失效房源清理时延**(下架→404/摘除的间隔,直接对应第一死法)。
- 社区页/经纪页常青流量占比——房源流量天然随库存波动,常青层是稳定器。
- 卖家线索量(home valuation 提交)。

**典型死法**

- **IDX 全量镜像无增量**(本型第一死法):百万近重复页吞爬虫预算,整站质量信号崩,真房源页收录反而慢。
- 失效房源不摘:已售/下架页长期 200+在索引,用户点了没房,转化与质量双输。
- 描述触发 Fair Housing 禁词——法律风险大于一切 SEO 损失(美国)。
- 社区页 doorway 化(换城市名仍通顺)——同④死法整组去索引。
- 经纪页匿名无实体,信任与品牌词无处累积(同③作者实体逻辑)。

**pSEO 机会**

- `<城市> × <房型|价位>` 房源组合页——每格在售库存 ≥ 阈值才生成(过 [programmatic-seo-gates.md](../technical/programmatic-seo-gates.md) 闸门)。
- `<城市> housing market` 年更数据页——外链磁铁(同③ State of X 范式)。
- 估值/月供计算器(⑥嫁接);学区·通勤 facet 页(带真实数据字段,非样板)。

**开局命令链(R1-6)**

```bash
# 1) 判型:房源/社区/经纪两层结构+失效房源堆积面(易失效详情+常青地方页)
python3 scripts/site_crawl.py example.com --max 2000 --out crawl.json --urls-out urls.txt
python3 scripts/site_audit.py https://example.com/property/123 https://example.com/atlanta-real-estate --json > audit.json
# 2) 失效房源退役(已售/下架仍 200 的页 → 404/摘除决策闸;清理时延=本型 KPI)
python3 scripts/prune_gate.py --urls sold-listings.txt --gsc queries.csv --crawl crawl.json
# 3) 经纪页信任面:LocalBusiness/NAP 四节体检
python3 scripts/local_audit.py --url https://example.com/agent/jane-doe --name "Jane Doe" --addr "456 Oak St, Atlanta, GA 30309" --json
# 4) `<城市>×<房型|价位>` 组合矩阵与 housing market 年更页机会
python3 scripts/pseo_pattern_mining.py --gsc queries.csv --sitemap https://example.com/sitemap.xml --json
```

闸门锚:[programmatic-seo-gates.md](../technical/programmatic-seo-gates.md);Fair Housing 禁词红线见本卡上文(组合字段定向人群直接禁)。
配套示例:暂无对位示例;通用体检链交付物形态见 [site-audit-chain-example.com-20261010](../../examples/site-audit-chain-example.com-20261010/REPORT.md)。

## 来源

本文由 EveryInfra 综合编写,只保留要点与口径,未复制原文。

- 2026 转化基准(报告级,单源慎用):[Stackmatix(2026-09)](https://www.stackmatix.com/blog/website-conversion-rate-benchmarks)、[Flighted B2B SaaS(2026-05)](https://www.flighted.co/blog/b2b-saas-conversion-rate-benchmarks)、[Authoricy AI 搜索转化(2026-06)](https://authoricy.com/blog/ai-search-conversion-benchmarks)
- 电商/Discover/本地:[DigitalApplied 电商(2026-01)](https://www.digitalapplied.com/blog/ecommerce-seo-product-category-page-guide-2026)、[DigitalApplied Discover 更新(2026-02)](https://www.digitalapplied.com/blog/google-discover-core-update-february-2026-seo-guide)、[DigitalApplied 本地核心更新(2026-03)](https://www.digitalapplied.com/blog/local-seo-march-2026-core-update-gbp-optimization-guide)
- YMYL/文档与 AI 爬虫:[Sure Oak 金融 YMYL(2026-08)](https://sureoak.com/insights/ymyl-eeat-financial-services-seo-rules)、[Limy llms.txt 500M 事件分析(2026-05)](https://limy.ai/blog/llms-txt-in-2026-the-full-guide)、[Google AI 优化指南(官方)](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- pSEO 范式:[Zapier 案例(salt.agency)](https://salt.agency/blog/how-zapier-quadrupled-organic-traffic/)、[pSEO 案例集(thebcms)](https://www.thebcms.com/blog/programmatic-seo-examples/)
- ⑨⑩ 官方核实(2026-10-12):[Google JobPosting 结构化数据文档](https://developers.google.com/search/docs/appearance/structured-data/job-posting)(必填字段/移除机制三选一/Indexing API 优先于 sitemap/canonical 要求;**无 90 天自动过期规则**)、[schema.org v30.0 发布说明](https://schema.org/docs/releases.html)(jobDuration 新增)、[Google 富结果画廊](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)(无 RealEstateListing 富结果;VacationRental 在列)
- Fair Housing(行业):[GBREB 房源描述禁用词 15 条](https://www.gbreb.com/GBAR/Sites/GBAR/News/Agent_Insider/2022/Dont_Violate_Fair_Housing_15_Words_to_Ban_From_Property_Descriptions.aspx)、[SmartMLS Fair Housing 词表(2024-12)](https://compliance.smartmls.com/hc/en-us/articles/13116678459803-Fair-Housing-words-and-phrase-list)、[NFHA 负责任广告指南](https://nationalfairhousing.org/responsibleadvertising/);IDX canonical 纪律为行业共识级(无双源,引用时标注)
- 本地六行业/网格排名/权重模型深读来源:见 [site-type-templates.md](../technical/site-type-templates.md) 文末及文内标注

## 检查清单(开局认站型时)

| 检查什么 | 怎么查 | 通过 / 失败判据 |
|---|---|---|
| URL 型谱判型 | `python3 scripts/site_crawl.py example.com --max 1000 --out crawl.json --urls-out urls.txt`,再看路径段前 10 | 至少两处信号吻合(型谱、schema、构成)才判型;只有一处或双信号强 → 列前二让用户确认 |
| schema 分布 | `python3 scripts/site_audit.py <URL...> --json` 看 JSON-LD 类型 | 与卡里"schema 分布"吻合;出现 FAQPage / HowTo 只当内容标记,不记收益 |
| 开局命令的参数真实存在 | 对卡里每条命令跑 `python3 scripts/<名>.py --help` | 参数都在 help 里(`site_crawl.py` 站点是位置参数) |
| 报告里的基准数字有来源 | 每个 KPI 基准旁有链接与日期,且来源页能打开 | 无链接的数字删掉;第三方数字标"第三方",不对客承诺 |
| 招聘 / 房产卡的官方要求 | 对照 [JobPosting 文档](https://developers.google.com/search/docs/appearance/structured-data/job-posting)(必填五件;下线三选一;职位 URL 建议用 Indexing API;无 90 天自动过期规则) | 与卡一致;文档更新日期晚于 2026-09-08 时重读 |
