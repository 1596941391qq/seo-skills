# Türkiye Pazarı 土耳其语市场专项(Google 为主 + Trendyol 站内搜索)

> 适用圈:土耳其(tr-TR)。数据锚点 2026-10-21;断言半衰期 6–12 个月。
> 配套:`overview/multilingual-workflow.md` 土语区段、`scripts/markets.json` 的 `tr` 键。
> 来源标注:【官方】=Google/监管机构/StatCounter 原始表/平台官方页;【第三方研究】=写明样本和日期;【从业者说法】=博客或论坛转述,未核到一手,只作线索;【本套件口径】=套件设计约定。

## 一、引擎格局:StatCounter 的 Yandex 数字波动极大,不能当预算依据

### 1.1 原始数据(StatCounter TR,2026-10-21 读 CSV)

| 月份(全设备) | Google | Yandex |
|---|---|---|
| 2025-09 | 59.97% | 33.17% |
| 2025-11 | 45.78% | **50.51%**(Yandex 高于 Google) |
| 2026-02 | 81.58% | 15.80% |
| 2026-03 | 84.21% | 13.44% |
| 2026-06 | 86.67% | 10.88% |
| 2026-08 | 80.86% | 17.47% |
| 2026-09 | 73.08% | **25.53%** |
| 2026-10 | 74.79% | **23.74%**(2026-11-05 读 CSV) |

- 2026-09 另有一次读到 25.19%(取数时间不同);两个数都落在 25% 附近。StatCounter 会回溯修订。
- 2026-09 按设备:Yandex 桌面 19.54% / 手机 28.55% / 平板 33.09%。旧稿写「Yandex 集中在桌面,手机被压制」,现值相反。
- 13 个月 Yandex 范围 10.88%–50.51%,均值 25.04%。旧稿「26% 是 12 个月窗口均值」不准确:25.53% 是 2026-09 单月值。
- 旧稿的「2025-09 Yandex 49.79%」「2026-08 单月 15.98%」在今天的表里读不到(2025-09 为 33.17%,2026-08 为 17.47%),按未复现处理。StatCounter 可能回溯修订历史月份。

### 1.2 怎么解读

- StatCounter 官方方法说明(`gs.statcounter.com/faq`):搜索引擎份额统计的是「从搜索引擎点击进入其会员站点的 referral」,不是搜索次数;样本是装了它代码的 100 万+ 站点;它会剔除 bot 流量。
- 同一国家一个月内能从 13% 跳到 50%,不可能是真实用户行为的变化。本套件推断:会员站点样本构成或某类流量在小样本国家里波动。这是推断,不是 StatCounter 的声明。
- 「点击侧 3–5%」来自本地机构说法,没有一手来源,标【从业者说法】。
- **本套件做法**:引擎份额一律写「StatCounter 某月值 + 12 个月区间」,不写单一数字。预算按客户自己的分析面板里 Yandex 的 referral 占比定;占比 <3% 时不做 Yandex 专项。Yandex Webmaster 提交是低成本动作,可以做。
- 旧稿「Yandex 自报 2025 年用户与查询 +75%」找不到原文,已删。

### 1.3 AI Overviews、AI Mode 与 Yazeka

- **AI Overviews 和 AI Mode 在土耳其语的上线日是 2026-02-18**:Google 土耳其博客《Türkiye'de AI Modu ve AI Bakışı Dönemi Başlıyor》,两者同日,由 Gemini 3 驱动,Android/iOS Google 应用和搜索结果页逐步推出(`blog.google/intl/tr-tr/urun-duyurulari/turkiyede-ai-modu-ve-ai-bakisi-donemi-basliyor/`)。2024-11 的 Google AIO 国家名单里没有土耳其(Wayback 快照核对)。
- 因此任何 2026-02-18 之前的「土耳其 AIO 覆盖率」都不是土耳其语 AIO 数据。
- Seobaz《Türkiye AI Overview Araştırması 2026》(2026-08 发布,公司自发):20 个行业、8,282 条土语移动搜索,其中 1,933 条出现 AIO,7,696 条来源链接,**75.3% 的来源位于自然结果前 10**【第三方研究,来自 Seobaz 自家 Facebook/LinkedIn/网站摘要】。解读:AIO 来源与经典排名高度重叠,先进自然前 10 再谈 AI 引用。
- 旧稿对比的「美国 76% → 37–38%」「Originality.ai 52%」找不到原文,已删。
- **Yazeka**:Yandex 土耳其专属 AI 搜索,2024-12-17 上线,先 Android 和桌面,iOS 稍后(t24.com.tr 报道,核对 2026-10-21)。输入方式、推理模式、金融/旅行垂直等细节旧稿无一手来源,已删。体量未知,列监测项,品牌词季度抽查。

## 二、渠道

### 2.1 Trendyol(站内搜索)

- 官方学习入口:Trendyol Akademi(`akademi.trendyol.com`),含《Satıcı Puanı Nasıl Hesaplanıyor?》。卖家分数怎么算,以 Akademi 和卖家面板为准。
- 「排名九信号」「内容分 80–90+ 目标」「标题上限约 100 字符」「efors 权重积累、换卡清零」都来自第三方 SEO 博客或论坛(例如 seovedijital.com 2026-03),没有 Trendyol 官方公式。全部标【从业者说法】,不当规则写给客户。
- 可执行的做法(本套件口径):标题结构用「品牌 + 产品名 + 型号 + 关键属性」;属性按类目必填项填满;断货前补货;排名变化用卖家面板数据看,不用工具猜。
- 站点审计:Trendyol 首页的原始 HTML 是空壳(2026-10-21 `site_audit.py` 读到 7 词、0 链接、无 H1、noindex 判定),这是抓取方式的假象,不是 SEO 问题。只用它测 robots 和 llms.txt(`/llms.txt` 返回 200)。

### 2.2 外链与赞助稿

- tanıtım yazısı(赞助新闻稿 + 外链)是土耳其常见形态。按 Google 垃圾内容政策原文:为排名买卖链接属链接垃圾;但加 `rel="sponsored"` 或 `rel="nofollow"` 的赞助链接不违规(`developers.google.com/search/docs/essentials/spam-policies#link-spam`,核对 2026-10-21)。
- 做法:赞助稿一律标注 sponsored,台账分「自然」「付费(已标注)」两列。旧稿的 r10.net 价格带(90₺–13,500₺)来自论坛挂单,已删。
- r10.net 只作行情监测,不作采购渠道。

## 三、语言机制

### 3.1 黏着语与关键词

- 土耳其语词根后串接多个后缀,一个词根有多个表面形式。关键词研究先归词干,再看屈折变体的搜索量。
- Zemberek-nlp 是常用的开源土耳其语形态分析库(Java)。GitHub 页面写明项目处于 slow maintenance,最新版 0.17.1(2019-07-23);许可证 GitHub API 返回 NOASSERTION,未核。
- Trendyol 站内搜索是否偏字面匹配,没有官方说明,未核。标题和属性按买家真实查询的屈折形写,这个做法无害。

### 3.2 İ / ı:可复现的大小写陷阱

- 本机实测(Node v26.11.1):`"İ".toLowerCase()` 得到 2 个码点 `i` + U+0307;`"I".toLowerCase()` 得到 `i`;`"I".toLocaleLowerCase("tr")` 得到 `ı`;`"ISPARTA".toLocaleLowerCase("tr")` 得到 `ısparta`。Python `"İSTANBUL".lower()` 长度 9(多一个 U+0307)。
- 规则:土耳其语比较前,先 `replace("İ","i")`,再清 U+0307,再 casefold;需要保留土耳其语大小写时用 `toLocaleLowerCase("tr")`。
- slug:先把 ı、İ→i,ğ→g,ş→s,ç→c,ö→o,ü→u,再小写。Google URL 文档要求链接里的非 ASCII 字符做百分号编码,所以 ASCII slug 更好读(`developers.google.com/search/docs/crawling-indexing/url-structure`)。【转写表是本套件口径】
- 域名用 ASCII,正文和标题保留土耳其语字符。

### 3.3 语域与格式

- siz(正式)全站一致;sen 只用于非正式社媒语境。【本套件口径】
- 数字 `1.234,56`,日期 `09.10.2026`,电话 +90。
- hreflang 写 `tr` 或 `tr-TR`,两者合法(ISO 639-1 + ISO 3166-1)。

## 四、SERP 占位与 ORM

- Şikayetvar 的投诉页常出现在品牌词结果里。品牌审计第一步:查品牌词 SERP 的投诉页占位。
- 删除投诉:Şikayetvar 官方博客写明,投诉被解决或客户道谢,不等于投诉会被删除;解决后移除投诉的权利只属于投诉人(`sikayetvar.com/blog/genel/resmi-sikayet-yonetimi-rehberi-sikayetvardan-sikayet-kaldirma-islemi-nasil-yapilir`,核对 2026-10-21)。治本路径是与投诉人解决问题。
- 站方违规举报和律师函路径的细节来自律所文章,未核一手,不写成规则。
- Ekşi Sözlük、DonanımHaber、Technopat、Akakçe 的占位动作是【从业者说法】。品牌词 SERP 抽查它们是否在前 10。

## 五、红旗

1. 用单一 Yandex 数字做预算:见第一节。
2. 引用 2026-02-18 之前的「土耳其 AIO」数据。
3. 对 Trendyol 这类 SPA 站用原始 HTML 工具下结论。
4. 赞助链接不标 sponsored。
5. 刷单刷评(平台处罚):不做、不推荐。
6. 土耳其语文本用英语 locale 小写(İ 变两个码点)。

## 六、工具

| 工具 | 用途 | 备注 |
|---|---|---|
| StatCounter TR(CSV) | 引擎份额月度表 | 见 1.1 |
| Yandex Webmaster | 提交与抓取诊断 | 仅在 Yandex referral ≥3% 时深投 |
| Trendyol Akademi / 卖家面板 | 卖家分数与内容质量 | 官方入口 |
| Zemberek-nlp | 词干、形态分析 | 维护放缓 |
| Şikayetvar | 品牌投诉监测与官方回复 | 官方指南见 4 |

## 七、法规适用范围(只写范围,不构成法律意见)

| 事项 | 适用范围 | 一手来源 |
|---|---|---|
| KVKK 6698 号法 | 2016-03-24 通过,Resmî Gazete 2016-04-07 / 29677;适用于处理个人数据的自然人和法人(第 2 条) | `lexpera.com.tr/mevzuat/kanunlar/kisisel-verilerin-korunmasi-kanunu-6698`;`hukukegitim.com` 记录通过与公报信息 |
| 2024 修订 | 7499 号法(2024-03-12,Resmî Gazete 32487)修改 6698 号法第 6、9、18 条;修订自 2024-06-01 起生效;第 9 条旧第一款适用到 2024-09-01 | KVKK 公告 `kvkk.gov.tr/Icerik/7834/...Kamuoyu-Duyurusu`;`kvkk.gov.tr/Icerik/2053/Yurtdisina-Aktarim` |
| Cookie | KVKK《Çerez Uygulamaları Hakkında Rehber》(KVKK Yayınları No: 69,2025-07),说明 5809 号电子通信法与 6698 号法的关系 | `kvkk.gov.tr/SharedFolderServer/CMSFiles/fb193dbb-b159-4221-8a7b-3addc083d33f.pdf` |

## 八、语言处理事实(影响计数、去重、小写比较)

| 事实 | 可查方式 | 脚本现状(2026-10-21 实测) |
|---|---|---|
| `İ` 小写成 2 个码点 | `node -e 'console.log([..."İ".toLowerCase()].length)'` 得 2 | `site_audit.py` `wc()` 已先替换 İ;`keyword_variants.py` 已先替换 İ 再 casefold,`İstanbul`/`ISTANBUL`/`istanbul` 同组,`ıstanbul` 单独一组 |
| 营销词计数 | 页面放 11 处大写「EN İYİ」,运行 `market_lint.py --market tr` | **漏报**:只计到小写的「En iyi」1 处(`casefold()` 把 `İ` 变成 `i`+U+0307)。`ste_lint.py --lang tr` 同样漏掉大写 `EN İYİ` 和 `DEVRİM NİTELİĞİNDE` |
| 提问对齐的分词 | `question_align.py` 的 `tokens()` 对 `İstanbul'da kargo` | `İ` 丢失,得到 `stanbul`;查询 `istanbul` 对该页的覆盖率判为 0.67 而非 1.0 |
| STE 检查 | `ste_lint.py --lang tr` 对重音密集的土耳其语段落 | 整块被当「非正文」跳过(`is_prose` 用 ASCII 正则,示例 13 词只有 2 个纯 ASCII 词),报 0 句 |

## 九、本地实测(实测记录)

> 脚本口径 2026-10-21 已改:twitter:* 与 OG 重复只记 INFO;缺 H1 / 缺描述为 WARN。旧版 2026-10-09 的「head_check 弃用 twitter:* 全套 ERROR」「site_audit 缺 H1 CRITICAL」不再适用。

- `site_audit.py https://www.sikayetvar.com/ --market tr --json`:title 42 字符、description 149 字符、H1=1、1141 词、245 链接(INFO)、无 WARN/CRITICAL。`head_check.py --market tr`:error=0,4 条 INFO(含 twitter:* 与 OG 重复、可删的 apple-mobile-web-app-capable)。
- `site_audit.py https://www.trendyol.com/ --market tr`:见 2.1(空壳假象)。`llmstxt.py check https://www.trendyol.com`:`/llms.txt` 200。
- 旧版记录的两个缺陷已修:title 解析吞脚本、`--market tr` 不读阈值(现在 tr 用 60/155)。

## 十、上线检查清单

| # | 检查什么 | 怎么查 | 通过 / 失败判据 |
|---|---|---|---|
| 1 | 引擎份额口径 | 下载 StatCounter TR CSV(`chart.php?...&csv=1`) | 报告同时写当月值和 12 个月区间;只写一个 Yandex 数字 = 失败 |
| 2 | Yandex 是否值得投 | 客户分析面板,Yandex referral 占比 | ≥3% 才做专项;<3% 只提交 Yandex Webmaster |
| 3 | title / description | `python3 scripts/site_audit.py URL --market tr` | title ≤60、description 77–155 字符(本套件口径) |
| 4 | head 元素 | `python3 scripts/head_check.py URL --market tr` | error=0 |
| 5 | hreflang | `python3 scripts/hreflang_cluster.py URL_tr [URL_en]` | 自引用、互指、语言码合法 |
| 6 | İ/ı 字符 | `python3 scripts/market_lint.py --market tr page.html` | 无「ASCII 大写 I + 小写」可疑项;正文用 İ/ı 码点 |
| 7 | 营销词 | 人工搜 `en iyi`、`devrim niteliğinde` 的大小写各形 | 全页 ≤3 处;不依赖脚本计数(见 8) |
| 8 | 大小写归一 | `printf 'İstanbul\nISTANBUL\nistanbul\n' \| python3 scripts/keyword_variants.py --json` | 三词同组 |
| 9 | 提问对齐候选 | `python3 scripts/question_align.py --gsc q.csv --pages p.csv --min-impressions 20 --max-position 10` | 含 İ 的查询需人工复核覆盖率(见 8) |
| 10 | 赞助链接 | `curl -s URL \| grep -io 'rel="[^"]*sponsored[^"]*"'` | 每个付费链接带 sponsored 或 nofollow |
| 11 | 品牌词 SERP | 搜「品牌名 şikayet」「品牌名」,记前 10 | 投诉页占位数写进台账;官方页是否在前 3 |
| 12 | AI 爬虫姿态 | `python3 scripts/robots_posture.py https://site/robots.txt` | 搜索类、用户类 bot 无非预期 blocked |
| 13 | 土耳其语 AIO 抽样 | 20 个核心词,2026-02-18 之后采样,记日期、设备 | 报告写样本量和日期 |
