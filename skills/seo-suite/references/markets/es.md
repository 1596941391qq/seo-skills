# Mercado Hispanohablante(西语市场:es-ES + 拉美 + es-US)

> 建立于 2026-10-09,2026-10-21 逐条重核:每个数字回到原始页面读过;读不到的删除或降级。数据层见 `scripts/markets.json` 的 `markets.es`(本文件不改 json)。
> 标注:【官】=官方页面或统计机构;【三方】=第三方研究或厂商(写机构、时间);【本套件口径】=本套件约定。断言半衰期 6–12 个月。
> 提问对齐见 [question-alignment.md](../content/question-alignment.md);句子写法见 [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md);多语言流程见 [multilingual-workflow.md](../overview/multilingual-workflow.md)。

## 一、格局:一种语言,两个宏观市场,加一块 es-US

### 1.1 引擎份额

StatCounter 搜索引擎份额,2026-09,全设备(页面表读数;同月 CSV 导出差 0.0x 个百分点,如西班牙 Google 93.78%、墨西哥 88.08%→87.99%):

| 国家 | Google | Bing |
|---|---|---|
| 西班牙 | 93.81% | 3.49% |
| 阿根廷 | 93.82% | 4.71% |
| 哥伦比亚 | 93.30% | 4.74% |
| 秘鲁 | 91.87% | 5.65% |
| 智利 | 90.23% | 7.28% |
| 墨西哥 | 88.08% | 9.43% |

- 来源:[StatCounter](https://gs.statcounter.com/search-engine-market-share/all/mexico)(各国同路径,取数 2026-10-21)。结论:Google 88–94%,无本地引擎。
- 墨西哥的 Bing 份额是西班牙的 2.7 倍。Bing 喂 Copilot,墨西哥站的 AI 引用抽检要单列 Bing / Copilot。
- 西语不是「独立引擎学科」市场:差异在语言变体与渠道结构,不在引擎。
- Google AI Overviews 在西班牙、墨西哥等拉美国家可用,语言含西语(【官】[Google 帮助中心可用国家与语言清单](https://support.google.com/websearch/answer/14901683?hl=en),核对 2026-10-21)。

### 1.2 市场切分

- 西班牙 es-ES:49,801,559 人(【官】[INE 2026-07-01](https://www.ine.es/dyngs/Prensa/ECP2T26.htm));欧元区。
- 墨西哥:130,911,314 人(【官】[INEGI 2025](https://www.inegi.org.mx/temas/estructura/)),是最大的西语国家。
- 美国 es-US:5 岁以上家中说非英语的人 7,410 万(2024),其中西语占一半以上,即 3,700 万以上(【官】ACS 2024,经 [USAFacts](https://usafacts.org/answers/how-many-people-speak-a-language-other-than-english-at-home/country/united-states/) 汇总)。
- 已删:「阿根廷/智利高客单,哥伦比亚/秘鲁增长带」(无来源)。

### 1.3 hreflang 决策

- Google 只支持 ISO 639-1 语言码加可选 ISO 3166-1 Alpha-2 区域码。原文:「other codes that aren't listed in those standards, such as es-419, aren't supported」(【官】[Google localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions),页面标注更新 2026-09-21,核对 2026-10-21)。
- 所以:`es-419` 不能当 hreflang 值。拉美写 `es` 兜底;需要按国家分页时加 `es-MX`、`es-AR`、`es-CO` 等国家码。`es-419` 只作内容层的「拉美西语」写法。
- 最小正确集(本套件口径):`es`(兜底) + `es-ES` + 你有独立内容的拉美国家码。与 `markets.json` 的 `hreflang_codes` 一致(es、es-ES、es-MX、es-AR)。
- 值不区分大小写;Google 不用 hreflang 或 `lang` 判定页面语言,用算法判定;两页没有互相指向时,这对标注会被忽略,其余照常处理(同一份文档)。

### 1.4 支付词即购买意图

- 墨西哥:OXXO 是便利店连锁,顾客可到店用现金支付线上订单(【官】[Stripe 文档](https://docs.stripe.com/payments/oxxo)),「efectivo」「OXXO」是现金偏好词。
- 阿根廷 `cuotas`(分期)、哥伦比亚/秘鲁 `contra entrega`(货到付款)、通用 `envío gratis`:本套件口径,入意图分类(`markets.json` 的 `payment_words`),没有逐条取到一手来源。

### 1.5 es-US 的「代看」视角

- 原先写的「81% 受托搜索」两次检索都找不到原研究(2026-10-09、2026-10-21),已删这个数字。
- 保留的是方法(本套件口径):搜的人不一定是用的人,品牌词和品类词 SERP 要用「代看」视角审计。步骤见第九节案例。

### 1.6 墨西哥 2026 动态

已删:「GBP 拥挤」「E-E-A-T 2.0」「微意图」「语音/多模态上升」四条,原文只有二手总结,没有可核来源。本地 SEO 的检查看第八节。

## 二、渠道:Mercado Libre、外链、WhatsApp

### 2.1 Mercado Libre 的排序

- 【官】Mercado Libre 学习中心写的是「竞争中的 listing」规则:同一商品的 listing 会被分组,**条件最好的**(价格、listing 类型、免息分期)显示为最醒目的一个,其余折叠成「Review More Options」;声誉黄色及以上的卖家更容易胜出;listing 质量(标题、描述、照片、属性)要完整准确。重复 listing 只保留一个,类目错误会被调整或下架,模糊或带水印的图片会让 listing 被立即暂停(【官】[Winning Strategies for Competing Listings](https://sellers.mercadolibre.com/learning-center/news/guide-to-your-listings-in-competition))。
- 【官】声誉由订单取消、延误、投诉等指标构成(【官】[Seller reputation](https://sellers.mercadolibre.com/learning-center/news/seller-reputation-learn-how-it-works))。
- 【三方】卖家工具厂商 Base.com(2026-04-24)归纳了「五支柱」模型:声誉、历史转化率、价格竞争力、listing 质量(标题、照片、ficha técnica)、物流(Full / Flex / 时效);标题 60 字符、品牌加型号加关键属性(【三方】[Base.com](https://base.com/es-AR/blog/algoritmo-posicionamiento-mercado-libre-2026/))。这是厂商的归纳,Mercado Libre 没有发布过这样的排序公式,也没有「投诉率 <1% 门槛」的官方说法(已删)。
- 做法(本套件口径):先把 listing 的属性/ficha técnica 填全,再看价格、声誉、物流三项;Flex 与 Full 的权重高低以自己店铺的数据为准。

### 2.2 外链价带

- 买卖带排名意图的链接违反 Google 链接 spam 政策(【官】[Spam policies](https://developers.google.com/search/docs/essentials/spam-policies):「Buying or selling links for ranking purposes」)。下面的价带只用来识别竞品档案里的付费层。
- 【三方】链接平台 Publisuites 自报(2026-06-16):利基博客约 50 €;专题博客 50–300 €;地区报纸 150–800 €;有影响力的数字媒体 400–1,500 €;顶级媒体 1,500 € 以上,个别 5,000 €(【三方】[Publisuites](https://www.publisuites.com/blog/precio-linkbuilding/))。平台自报价,不是成交价。
- 已删:「12–20 €/链」平台起步价表、按 DR 分档的价带、Dinorank「361 $」、「comprarenlaces.net 5,000+ 域名」、「新闻稿 7 €」(找不到可核来源)。

### 2.3 WhatsApp 与 Facebook

- 【三方·厂商博客】watsi(2026-03-22)称:WhatsApp 对话对合格线索的转化率 45–60%,网站 2–4%。两者的分母不同(合格线索 vs 全部访客),不能当基准;已不用「十倍差」的说法。
- 落地页检查(本套件口径):`wa.me` 深链在场;预填消息(`wa.me/<号码>?text=`);写明响应时效。
- Meta 计费(【官】[Meta 开发者文档](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages)):自 2026-10-01 起,所有服务消息按条计费。Business Agent 回复自 2026-08-01 起按 token 计费(【三方】[Omnichat](https://blog.omnichat.ai/meta-business-agent-platform-explained-features-pricing-and-what-the-2026-whatsapp-changes-mean-for-your-business/))。商务 WhatsApp 的成本要重算。巴西本币结算那一条没找到来源,已删。
- 已删:「Facebook 本地页是事实店面」「邮件在拉美消费场景近缺席」(无来源)。

## 三、语言机制:变体分流是本体

### 3.1 词汇

- `coche`(西班牙)、`carro`(墨西哥、哥伦比亚等)、`auto`(阿根廷、智利、乌拉圭等):常见高频词分裂。同类:ordenador / computadora,móvil / celular。
- 关键词研究按变体组分开做;仲裁用 Google Trends 按 es-ES / es-MX / es-AR 分区比量级(本套件口径)。
- 已删:「autobús / camión」「patata / papa」「zumo / jugo」的国别归属(未逐条核)。

### 3.2 vosotros 与 ustedes,tú 与 vos

- 【官】RAE《泛西班牙语疑难词典》:`vosotros` 是西班牙大部分地区的非正式复数称呼;在美洲没有使用,在加那利群岛和安达卢西亚西部也用 `ustedes` 代替(【官】[DPD: vosotros](https://www.rae.es/dpd/vosotros))。动词变位 `-áis/-éis` 同样不用于美洲。
- 单数层:美洲很多地区用 voseo(`vos` 代替 `tú`),阿根廷是典型(【官】[DPD: voseo](https://www.rae.es/dpd/voseo) 的例句来自阿根廷等国)。原先写的「阿根廷 tú 渗透最深」不对,已改。文案要不要用 voseo,按目标国的品牌调性定(本套件口径),至少不要在阿根廷页混用西班牙的 `vosotros`。
- 正式 B2B 用 `usted`(本套件口径)。

### 3.3 倒问号

- 【官】RAE:疑问句和感叹句的开头符号 `¿` `¡` 必须写,省略是错误;开头符号放在问句真正开始的位置,不一定在整句开头(【官】[RAE 正字法](https://www.rae.es/espanol-al-dia/ortografia-de-los-signos-de-interrogacion-y-exclamacion))。
- 疑问式 H2(`¿Cuánto cuesta…?`、`¿Cómo elegir…?`)与用户提问同构,方法见 [question-alignment.md](../content/question-alignment.md)。缺 `¿` 的标题是机翻或外包信号(本套件口径)。

### 3.4 数字与日期

- 【官】Unicode CLDR 48:`es`(西班牙)小数用逗号、千分位用点,且最小分组位数为 2,即 1234,56 不加点,12.345,67 才加点;`es-MX` 与 `es-419` 小数点用点、千分位用逗号(1,234.56)(【官】[CLDR es numbers](https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-numbers-full/main/es/numbers.json) 及 es-MX、es-419 同路径)。
- 同一站内混用两种写法,是未本地化的信号。日期按日/月/年(09/10/2026);货币 € 与 MXN/ARS/COP 分开写,通胀国价格带更新日期(本套件口径)。

### 3.5 中性西语

- `es neutral` 只用于 UI 骨架和产品文案,不用于关键词层和转化文案(本套件口径)。分层:关键词按变体组;转化文案按目标国;UI 与法务用中性层。

## 四、AI-GEO

### 4.1 西班牙的引用格局

- 【三方】Media and Journalism Research Center《AI Information Map: Spain》(2026-07-10):10 个 AI 助手、2 种语言、同一组问题。El País 是被引最多的来源,占 4.9%;前三名合计 10.2%;其余 77.6% 分散在 1,924 个来源(【三方】[原文](https://journalismresearch.org/ai-information-map-spain/))。含义:没有一个西班牙媒体主导 AI 信息层,长尾来源有机会。
- AIO 引用与自然 top-10 的重合,各家读数不同:Limón Publicidad 写 15%(代理商博客 2025-10,无方法说明);Forbes 的 4 百万条研究经 Mintec 转述为 38%;Isma Jiménez 写 47.7%(【三方】[Limón](https://limonpublicidad.com/blog/ai-overviews-en-espana-como-la-ia-de-google-revoluciona-los-resultados-organicos/)、[Mintec](https://mintec.co/es/blog/organic-ranking-vs-ai-citations/)、[Isma Jiménez](https://ismajimenez.com/google-ai-overviews-como-impactan-el-ctr-organico-y-el-trafico-en-espana/);后两条未读原文)。结论:区间 15%–48%,差距来自方法。做法:自然排名是前提但不是全部,指南页、数据页、垂直媒体页单独做可引性检查。
- AIO 覆盖:SE Ranking 在 100,000 个西班牙关键词里,33.23% 出现 AIO(【三方】[SE Ranking 2025-06-18](https://seranking.com/es/blog/ai-overviews-en-espana/),15 个月前的读数);Laboratorio de Periodismo / Clara Soteras 与 M.J. Cachón 的研究:媒体类搜索中 29.8% 出现 AIO,桌面与移动无明显差异(【三方】[Laboratorio de Periodismo](https://laboratoriodeperiodismo.org/impacto-de-ai-overviews-en-espana-google-activa-resumenes-generativos-en-el-298-de-busquedas-sobre-medios/))。
- ThinkEPI(Díaz-Noci,2026)分析了 Google 从搜索到生成内容后西班牙媒体流量的下降(【三方】[ThinkEPI](https://thinkepi.scimagoepi.com/index.php/ThinkEPI/es/article/view/91722));媒体类客户的预期管理用这个方向。
- 【第三方研究】西语查询的 AI 引用多指向西语源:Google AI Overviews 和 Copilot 约 83–84%,Grok 55% 以上([Temso 2026-04](https://www.temso.ai/data/-Lost-in-Translation-How-AI-Models-Handle-Local-Language-Sources),700 万条引用、4 个模型;厂商研究,核对 2026-10-21)。不能推广到全部 AI 引擎。
- 已删:「Clabe.org 43.6%」「mjcachon:经典排名是最佳预测因子」(找不到可核原文)。
- 半岛偏置(AI 对拉美查询倾向引 es-ES 源):没有找到量化研究。做法保留为本套件口径:拉美查询用拉美出口测 SERP,不用西班牙代理数据代替;拉美站点常托管在欧洲,检查 CDN 与延迟。

### 4.2 测量

- 【官】Search Console 的「Generative AI performance」报告(公布与全球开放日期见[事实表](../overview/facts.md#gsc-genai))只给**展示**,涵盖 AI Overviews 和 AI Mode,按页面、国家、日期、设备拆分,没有点击(【官】[帮助页](https://support.google.com/webmasters/answer/16984139?hl=en))。原先写的「曝光/点击」不对,已改。
- 站点没有足够展示时看不到这份报告。西语站的 AI 可见性以它为第一数据源,第三方 AIO 抽样只作补充。

### 4.3 西语 LLM 偏见

- SESGO(Robles 等,arXiv 2509.03329,2025):评估指令微调 LLM 在西语语境里的区域性社会偏见(【三方】[arXiv](https://arxiv.org/abs/2509.03329))。含义:品牌在西语 AI 答案中的呈现,要单独抽检,不能沿用英语结果。

## 五、信息源(圈内常被引用,未逐一核其方法)

| 区域 | 源 | 用途 |
|---|---|---|
| 西班牙 | SEOPLUS 年度大会(2026-07-25 场,见 [Convictorius 活动表](https://convictorius.com/eventos-seo/)) | 西班牙 SEO 圈动向 |
| 西班牙 | ThinkEPI | 学术侧(AIO 与媒体) |
| 拉美 | Nubimetrics(Mercado Libre Centro de Partners 在列:[页面](https://centrodepartners.mercadolibre.com.ar/apps/nubimetrics)) | Mercado Libre 卖家数据 |
| 其他 | Campamento Web、Human Level、Punto Rojo、Alan Quezada | 未核其近况,按需使用 |

## 六、红旗

1. **「一份中性西语通吃」**:coche / carro / auto 与 vosotros / ustedes 不能互换(第三节)。
2. **「拉美 = 低竞争」**:没有一手来源支持这句话,不要写进方案。
3. **买链和 PBN**:违反 Google 链接 spam 政策(2.2)。竞品档案里 DR 20–40 的单链密集、锚文本过度优化的站群,按付费链接怀疑,采购不跟。
4. **半岛数据代替拉美实测**:用西班牙 SERP 工具口径汇报「西语排名」,会掩盖国家差异。
5. **机翻漏 `¿`、数字格式混用**:低成本可检的未本地化信号(3.3、3.4)。
6. **把厂商模型当平台规则**:Mercado Libre「五支柱」是厂商归纳(2.1)。

## 七、工具

| 工具 | 用途 | 备注 |
|---|---|---|
| Search Console Generative AI performance | AIO / AI Mode 展示 | 【官】只有展示 |
| Google Trends(es-ES / es-MX / es-AR 分区) | 词汇变体量级 | 本套件口径 |
| Nubimetrics | Mercado Libre 供需与价格带 | 【三方】官方 Partner 列表在列 |
| 国别 SERP 采样(MX / AR / CO 独立出口) | 半岛偏置对抗 | 本套件口径 |
| 链接档案审计 | 识别竞品付费层 | 用 `scripts/link_check.py` 与 monitoring/link-quality-rubric.md |

## 八、检查清单

| # | 检查什么 | 怎么查 | 通过判据 |
|---|---|---|---|
| 1 | hreflang 簇 | `python3 scripts/hreflang_cluster.py https://site/es/x https://site/es-es/x https://site/es-mx/x https://site/en/x` | 簇内互指;没有 `es-419`;`es` 兜底在场;含 `x-default` |
| 2 | 全站 hreflang | `python3 scripts/sitemap_audit.py https://site --hreflang` | 无自引用缺失、无互指缺失、无非法语言码 |
| 3 | 西语文案机检 | `python3 scripts/market_lint.py --market es page.html --report` | CRITICAL 0;`--report` 里「¿ H2」「coche/carro/auto 词汇分流」两项为 AUTO-OK(这两项脚本会机检;数字格式脚本不检,见第 5 项) |
| 4 | 变体词汇 | `grep -ciE "coche\|carro\|auto" page.html`,按国别页分别统计 | es-ES 页无 carro/auto;es-MX 页无 coche |
| 5 | 数字格式(脚本不检,人工) | `grep -nE "[0-9]{1,3}(\.[0-9]{3})+,[0-9]\|[0-9]{1,3}(,[0-9]{3})+\.[0-9]" page.html` 分别抓欧式与美式写法;对照 CLDR:es-ES 4 位数不加分隔符(1234,56),5 位起加点(12.345,67);es-MX 用逗号千分位 | 同一站点同一页面只用一种;es-ES 页无 1,234.56 |
| 6 | AI 展示基线 | Search Console「Generative AI performance」按国家拆分 | 西班牙与墨西哥分别有展示数据;每月记录,不与旧版报表混比 |
| 7 | AI 检索爬虫 | `python3 scripts/robots_posture.py https://site/robots.txt --json` | `visibility_failures` 为空,或封禁是记录在案的决定 |
| 8 | 墨西哥 Bing | Bing Webmaster Tools;`python3 scripts/bing_wmt.py stats`(需 API key) | Bing 有数据;抽检 Copilot 引用 |
| 9 | WhatsApp 深链 | 浏览器看 CTA 的 href | `wa.me` 深链在场;消息预填;页面写响应时效 |
| 10 | Mercado Libre listing | 卖家后台 listing 质量与属性完整度 | 必填属性全填;标题含品牌、型号、关键属性;无重复 listing |
| 11 | 代看视角 | 见第九节案例 | 前 10 中目录/评测/佣金站占比有记录 |

## 九、本地实测(2026-10-09,本套件记录;2026-10-21 抽查)

- 跑了 elmundo.es 与 eluniversal.com.mx × `site_audit --market es` / `llmstxt check` / `head_check`。
- 2026-10-21 复查 robots(`robots_posture.py --json`):elmundo 对 OAI-SearchBot、PerplexityBot、ChatGPT-User 构成可见性失败,Claude-SearchBot 没有;eluniversal 对 11 个检索/用户类机器人构成可见性失败。与 10-09 记录一致。elmundo 的 `/llms.txt` 现在 301 到 CDN 域名后返回 404;eluniversal 返回 404。
- **脚本口径 2026-10-21 已改**:`head_check` 里 twitter:* 与 OG 重复只记 INFO(不是弃用),x-ua-compatible、fb:app_id 等旧标签记「可删旧标签」INFO;微信/QQ itemprop 提示只在显式或自动判定为 zh 时出现;`site_audit` 缺 H1、缺 description 记 WARN。上面 10-09 的「弃用」「CRITICAL」表述按旧口径。
- 其他记录(10-09):两站 `>100 链接` 与 alt 缺失;eluniversal 首页 2 MB、og:image 相对 URL;elmundo 老的 iso-8859-15 charset 声明;title 解析把 head 内脚本并入 title 的问题已知(解析器问题,非站方)。
- 工具盲区:`market_lint --market es` 对 `¿` H2、coche/carro/auto 混用、支付词层有机检(2026-10-21 夹具实测),但「该用哪个变体」要人按国别判断;数字格式混用、`vosotros` / `ustedes` 混用、voseo 脚本都不检。

### es-US 代看案例(本套件方法)

案例设定:迈阿密一家西语保险品牌,品牌词 SERP 被第三方代理页占据,转化率偏低。

1. **代看 SERP 快照**:品牌词与代搜品类词(如 "seguro médico para mi mamá")分别在美国西语 locale 拉 SERP;统计前 10 里目录、评测、佣金站的占比。占比 >30% 判为污染(本套件口径阈值)。
2. **意图分离**:词表分「自用」(para mí)与「代搜」(para mi mamá / papá / abuela)两列,分别落地;代搜列的文案按「帮家人选」写。
3. **问句层**:H2 用完整问句(`¿Cuál es el mejor seguro para padres mayores?`)。
4. **结构化数据**:FAQ 文本写代搜口语全句;产品页写适用人群。只写页面上可见的内容。
5. **归因**:GA4 按特征切「代理会话」视图(晚间、移动、复访间隔长、直跳联系页),代理转化单列,避免 CPA 被稀释。

## 维护

- 复审周期 **90 天**,下一次 **2027-01-09**;signals 清单与 `scripts/markets.json` 的 `markets.es.review_cycle` 保持一致,以 json 为准。
- 触发即复审:StatCounter 分国月度份额(墨西哥 Bing 波动单记);Search Console Generative AI 报告口径变化;Mercado Libre 学习中心与卖家政策公告;Meta WhatsApp 计费与 Business Agent 政策;AI Information Map Spain 年更。
