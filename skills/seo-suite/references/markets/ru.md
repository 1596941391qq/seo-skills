# 俄语市场专项(ru)

> 定位:俄语市场的增量层,主战场是 Yandex。数值规则在 `scripts/markets.json` 的 `markets.ru`;全球流程见 [multilingual-workflow.md](../overview/multilingual-workflow.md)。
> 2026-10-18 全文复核,2026-10-21 逐条重核(Yandex 帮助中心与新闻稿、consultant.ru 法条原文、RKN/FAS 函件、StatCounter 页面与 CSV、Unicode CLDR JSON)。标注:【官】=Yandex 官方或法条原文;【三方】=第三方研究(写机构、样本、时间);【本套件口径】=本套件自定约定。断言半衰期 6–12 个月。
> 第九节是「俄语版上线检查清单」,给已有英文/中文/西语版的 SaaS 或 API 文档站直接用。

## 一、引擎格局:三套口径并列

| 口径 | 读数 | 来源 |
|---|---|---|
| StatCounter(页面浏览样本) | 2026-10(CSV,取数 2026-11-05):Yandex 70.15%、Google 28.43%。2026-09:页面表 Yandex 70.33%、Google 28.12%(同月 CSV 导出 70.35% / 28.10%,两个读数差 0.02 个百分点);2025-10 至 2026-09 的 12 个月里 Yandex 在 70.32–73.72% 之间;移动 Yandex 68.90%,桌面 71.55%(CSV) | [StatCounter 俄罗斯](https://gs.statcounter.com/search-engine-market-share/all/russian-federation),取数 2026-10-21 |
| Яндекс Радар(Metrica 聚合) | 2026 Q1:Yandex 份额 69.8% | 【官】[Yandex 2026 Q1 财报](https://yandex.ru/company/news/28-04-2026) 脚注 8「по данным … Яндекс Радар」 |
| LiveInternet(ru 统计组「переходы из поисковых систем」) | 2026-09:Google 55.8%、Яндекс 44.0% | [LiveInternet](https://www.liveinternet.ru/stat/ru/searches.html),取数 2026-10-18 |

- 三套口径的样本不同。StatCounter 数页面浏览;Радар 数 Metrica 站点;LiveInternet 数装其计数器站点的搜索来路。三者方向冲突时,用自己站点的 Metrica 来源报表和 GSC 实测来路比例定预算。
- 俄语用户不只在俄罗斯。StatCounter 2026-09:哈萨克斯坦 Google 68.13%、Yandex 29.73%;白俄罗斯 Google 58.96%、Yandex 38.57%。俄语版要同时做 Google 与 Yandex。
- **Алиса AI 已进入搜索结果页**【官】:2026 Q3 有 44% 的查询出现 Алиса AI 回答;搜索框下回答的月受众 5,480 万,环比 +11%;每周在聊天里用 Алиса AI 的用户 4,500 万。来源:[Yandex 2026 Q3 财报](https://yandex.ru/company/news/29-10-2026-01)(2026-11-05 核对)。上一季:Q2 为 42%(环比 +7 个百分点)、4,950 万([Q2 财报](https://yandex.ru/company/news/29-07-2026))。2025-05-22 起 Алиса 接替 Нейро 进入搜索(官方原话「унаследует и расширит возможности Нейро」,[新闻稿](https://yandex.ru/company/news/01-22-05-2025))。
- 盲测成对评测:被测的 Yandex 自研模型(Alice AI Search)对 Google AI Overviews 胜 56.7%。RG 的报道没有写评测方,按「厂商侧数据」对待,不当独立评测。来源:[RG 2026-07-29](https://rg.ru/2026/07/29/ii-otvety-v-poiske-iandeksa-oboshli-google-po-kachestvu-i-nabrali-495-mln-polzovatelej.html)。
- 【三方】Ашманов и партнёры:2025-08 至 2026-01,Алиса 回答引用的非 top-10 站点占比从 40% 降到 10%;约第 5 位之后入选概率下降。Yandex 方面回应:回答平均基于约 10 个来源,入选看内容的专业性和充实度。来源:[Коммерсантъ 2026-06-10](https://www.kommersant.ru/doc/8728568)。
- 【三方】同一机构的电商查询样本:2026-04 只有千分之一出现 Алиса 快速回答,2026-07 约 15%,且常位于全部结果之上。来源:[CNews 2026-10-06](https://www.cnews.ru/news/line/2026-10-06_alisa_ai_aktivno_vstraivaetsya)。
- 官方统计页「Нейростат」([ya.ru/ai/stat](https://ya.ru/ai/stat))发布生成式 AI 的认知与使用数据。
- Google AI Overviews 在俄罗斯和俄语可用(Google 帮助中心可用国家与语言清单,[核对 2026-10-18](https://support.google.com/websearch/answer/14901683?hl=en))。

## 二、Yandex Webmaster 技术要点(逐条官方)

| 项 | Yandex 规则 | 和 Google 的差别 | 来源 |
|---|---|---|---|
| hreflang | `<head>` 内 `<link rel="alternate" hreflang="…">`;每个版本列出全部版本;语言用 ISO 639-1,地区用 ISO 3166-1 Alpha-2 或 ISO 3166-2:RU;支持 `x-default`;站点结构(子目录、子域、不同域)不影响处理 | **Yandex 不再支持 Sitemap 里的语言版本标注**(locale-pages 页首提示;同站 Sitemap 帮助页仍提到可传,按前者为准),要用 HTML。Google 认 HTML、HTTP 头、Sitemap 三种且等价 | 【官】[Индексирование локализованных страниц](https://yandex.ru/support/webmaster/ru/yandex-indexing/locale-pages) |
| hreflang 语言清单 | 官方清单含 ru、en、es 等;清单里没有 zh | 中文版对 Yandex 无 hreflang 效果,Google 照常 | 同上 |
| canonical | 只是建议。指向别的域名或子域、多个 canonical、canonical 链、目标被禁或跳转时忽略;自指合法 | 跨域 canonical Google 可用,Yandex 不认 | 【官】[Канонический адрес](https://yandex.ru/support/webmaster/ru/robot-workings/canonical) |
| robots.txt | 指令只有 User-agent、Disallow、Allow、Sitemap、Clean-param;文件 ≤500 KB;须返回 200,否则视为全开放;禁止西里尔字符(用 Punycode 或百分号编码);有 `User-agent: Yandex` 组时忽略 `*` 组 | 被 Disallow 的页仍可能出现在 Yandex 结果里,要下线用 noindex | 【官】[robots.txt](https://yandex.ru/support/webmaster/ru/controlling-robot/robots-txt)、[User-agent](https://yandex.ru/support/webmaster/ru/robot-workings/user-agent) |
| Clean-param | `Clean-param: p0[&p1…] [path]`;单条 ≤500 字符;区分大小写;可写在任意位置;Disallow 优先;utm_*、ysclid、yrclid 等会自动忽略 | Google 无此指令 | 【官】[Clean-param](https://yandex.ru/support/webmaster/ru/robot-workings/clean-param) |
| Sitemap | XML 或 TXT;≤50,000 URL、未压缩 ≤50 MB;UTF-8;同域;返回 200;在 robots.txt 或「Индексирование → Файлы Sitemap」提交;一般两周内处理 | 规格同协议 | 【官】[Sitemap](https://yandex.ru/support/webmaster/ru/controlling-robot/sitemap) |
| IndexNow | 单条 `GET https://yandex.com/indexnow`,多条 POST;根目录放 key 文件;只报新增、修改、删除的页;不保证收录 | Google 不支持 IndexNow | 【官】[IndexNow](https://yandex.ru/support/webmaster/ru/indexing-options/index-now) |
| 重新抓取 | 「Индексирование → Переобход страниц」;每日限额;排队 ≤3 天;数据两周内更新;robots.txt 几小时内自动重抓 | — | 【官】[Переобход страниц](https://yandex.ru/support/webmaster/ru/robot-workings/site-reindex) |
| 地区 | 「Представление в поиске → Региональность」;官方原话「как правило」只给一个地区,多分支机构的站可有多个地区;只影响地域相关查询,不排除站点在别的地区出现;通用主题站可选「Нет региона」;人工审核「от нескольких дней до нескольких недель」 | Google 无对应设置 | 【官】[Региональность](https://yandex.ru/support/webmaster/ru/site-geography/site-region) |
| 按 IP 切语言 | 机器人从单一地区 IP 抓取;按 IP 跳转会让部分版本不被收录;官方建议用语言切换器,各版本都返回 200 | — | 【官】[Обработка редиректов](https://yandex.ru/support/webmaster/ru/robot-workings/managing-redirects) |
| JS 渲染 | 「Индексирование → Рендеринг страниц JavaScript」(β);默认由机器人决定;已做 SSR 或预渲染时官方建议关闭 | — | 【官】[Рендеринг](https://yandex.ru/support/webmaster/ru/yandex-indexing/rendering) |
| title / description | 不设字符上限,长度受设备屏宽限制;品牌放 title 开头或结尾;description 每页唯一;「Заголовки и описания」报表查重 | markets.json 的 55/160 是本套件 lint 阈值,不是 Yandex 规定 | 【官】[title](https://yandex.ru/support/webmaster/ru/search-results/title)、[description](https://yandex.ru/support/webmaster/ru/indexing-options/description) |
| 验证 | HTML 文件(推荐)、`<meta name="yandex-verification">`、DNS TXT、YTM/GTM;www 与非 www 算两个站;核验最长 24 小时 | — | 【官】[Подтверждение прав](https://yandex.ru/support/webmaster/ru/service/rights) |
| 机器人真伪 | 反查 DNS 以 yandex.ru / yandex.net / yandex.com 结尾,再正查回同一 IP;AS13238、AS208722、AS212066 | — | 【官】[Проверка робота](https://yandex.ru/support/webmaster/ru/robot-workings/check-yandex-robots) |
| Турбо-страницы | 已停止支持,Webmaster 板块关闭 | — | 【官】[Webmaster 博客 2025-02-07](https://webmaster.yandex.ru/blog/yandex-stops-supporting-turbo-technology) |
| ИКС | Yandex 对站点「有用和便利」的评估;依据受众规模、用户满意度、信任等;定期重算;违规或操纵时可清零;新站进入搜索后一个月内算出 | 无 Google 对应物 | 【官】[ИКС](https://yandex.ru/support/webmaster/ru/site-quality-index) |

## 三、Алиса AI 可见度(GEO)

- **怎么生成**【官】:先拆分查询、补充子问题,再用改写后的查询调用搜索,依靠排名靠前的来源成文;来源链接不排序;同一查询的回答随日期和个性化变化。来源:[Как формируются ответы Алисы AI](https://yandex.ru/support/webmaster/ru/alice)。
- **选源标准**【官】:ЭПОС 四方面:Экспертность、Полезность、Оригинальность、Содержательность。官方原话:生成式回答建立在搜索结果之上,所以「принципиально новых требований не возникает」。来源:[ЭПОС](https://yandex.ru/support/webmaster/ru/epos)。
- **计量**【官】:Webmaster「Видимость сайта в Алисе AI」(2026-04-07 上线,[新闻稿](https://yandex.ru/company/news/07-04-2026-01))。SoV = 出现 Алиса 回答且提到本站的查询数 ÷ 出现 Алиса 回答的查询数;只统计本站已排名靠前的查询;数据覆盖近 3 个月,每周更新;不提供点击和展示;须先验证站点。来源:[Видимость сайта в Алисе AI](https://yandex.ru/support/webmaster/ru/service/alice-answers)。
- **退出**【官】:robots.txt 对 `YandexAdditional` 或 `YandexAdditionalBot` 写 Disallow,2–14 天生效。该 token 不发起抓取,只作用于主机器人已收录的页面。来源:[Запрет показа в ответах Алисы AI](https://yandex.ru/support/webmaster/ru/adding-site/indexing-prohibition)。
- **检查**:每月记 SoV;看「Примеры → Запросы и страницы」里竞争者被引的页;没有数据时,先查自然排名(官方列出的原因包括排名低、正文文本少)。
- 媒体与品牌可参考 Yandex 与 Синхронизация 的免费课程「Писать для людей в эпоху ИИ」([RG 2026-10-05](https://rg.ru/2026/10/05/iandeks-zapustil-kurs-dlia-media-o-popadanii-v-otvety-nejrosetej.html))。
- 详细爬虫分策见 [ai-crawler-policy.md](../technical/ai-crawler-policy.md);证据等级以 [geo-evidence.md](../content/geo-evidence.md) 为准。

## 四、语言与文案

| 项 | 规则 | 来源 |
|---|---|---|
| 复数 | 四类:one(1、21、101…)、few(2–4、22–24…)、many(0、5–20、25–30…)、other(小数,如 1,5)。例:1 запрос、2 запроса、5 запросов、11 запросов、21 запрос | [Unicode CLDR 48 plurals](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-core/supplemental/plurals.json) |
| 引号 | 外层 «…»,内层 „…“ | [CLDR ru delimiters](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-misc-full/main/ru/delimiters.json) |
| 数字与货币 | 小数点用逗号;千分位用不换行空格 U+00A0:1 234,56;货币 1 234,56 ₽ | [CLDR ru numbers](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-numbers-full/main/ru/numbers.json) |
| 日期 | 短格式 09.10.2026;长格式 9 октября 2026 г. | [CLDR ru gregorian](https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-dates-full/main/ru/ca-gregorian.json) |
| вы / Вы | 对单个具体的人(信件、公文)写 Вы;对多人或不定多数写 вы;Лопатин 手册另允许问卷、广告等反复使用的文本写 Вы。本套件口径:网站 UI 用小写 вы,全站一致 | [Грамота.ру](https://gramota.ru/biblioteka/spravochniki/pismovnik/kak-pisat-vy-i-vash-s-propisnoy-ili-so-strochnoy-bukvy) |
| 最高级 | 广告里用 лучший、первый、номер один,必须写明比较标准并有客观依据,否则属不实广告(38-ФЗ 第 5 条第 3 款第 1 项) | [ВАС 全会决议 2012 第 58 号第 29 条](https://arbitr.ru/materials/68264?path=%2Farxiv%2Fpost_plenum%2F) |
| ё / е | 关键词研究把两种写法归一组 | 本套件口径;`keyword_variants.py` 规则 `ru-ё→е` |

- **Wordstat 算子**【官】:`-` 排除;`!` 锁词形;`+` 锁停用词;`" "` 锁词数(不锁词序);`[]` 锁词序;`()` 加 `|` 分组。默认数字是「包含该短语的查询总数」,含全部词形。要窄口径就组合 `" "` 与 `!`。来源:[Операторы](https://yandex.ru/support2/wordstat/ru/content/operators)、[Вордстат](https://yandex.ru/support2/wordstat/ru/interface/new)。
- **地区码**【官】:225=俄罗斯,1=莫斯科与莫斯科州,213=莫斯科市([Yandex Search API 地区树](https://aistudio.yandex.ru/en/docs/search-api/operations/wordstat-getregiontree))。走 API 要 folder ID、带 `search-api.webSearch.user` 角色的服务账号、带 `yc.search-api.execute` 权限的 API key([Search API 文档](https://aistudio.yandex.ru/en/docs/search-api/operations/web-search))。
- 标题与首段直接回答俄语用户的原话提问,方法见 [question-alignment.md](../content/question-alignment.md);句子写法见 [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md)。

## 五、法规(写清适用范围;本节是 SEO 交付检查,不是法律意见)

**个人数据(152-ФЗ)**
- 适用范围:Роскомнадзор 2016 年对 242-ФЗ(本地化条款的前身)的评注,自述「не носит обязательного или рекомендательного характера」,列出判断网站是否「面向俄罗斯」的迹象:与俄罗斯相关的域名(.ru/.рф/.su)和/或站方自建的俄语版;合同可在俄境履行(含数字内容)。机器翻译插件不算。来源:[RKN 评注](https://rppa.pro/npa/rkn_09.11.2016)(原件 pd.rkn.gov.ru)。
- 第 18 条第 5 款(23-ФЗ,2025-07-01 起):收集俄罗斯公民个人数据时,禁止用境外数据库做记录、整理、累积、存储、更新、提取(有例外)。来源:[consultant.ru 第 18 条](https://www.consultant.ru/document/cons_doc_LAW_61801/cbf4e15b7c330f9372e876cdf2bc928bad7950ef/)。
- 统计工具:RKN 2024-06-26 第 08-242780 号函:能识别唯一访客并记录其偏好和行为的统计程序,属于处理个人数据,须告知、取得同意、写入内部规定;用 Google Analytics 属于跨境传输,须向 RKN 提交跨境传输通知(第 12 条第 3 款)。来源:[garant.ru](https://www.garant.ru/products/ipo/prime/doc/409415443/)。
- 同意:须具体、知情、明确,且与其他文件分开(第 9 条第 1 款,156-ФЗ 2025 修订)。来源:[第 9 条](https://www.consultant.ru/document/cons_doc_LAW_61801/6c94959bc017ac80140621762d2ac59f6006b08c/)。
- 政策页:在线收集数据的运营者,须在收集数据的页面上公布处理政策(第 18.1 条第 2 款)。来源:[第 18.1 条](https://www.consultant.ru/document/cons_doc_LAW_61801/eeeebe22bf738fd65bb66b95cc278911ae2525ee/)。
- 罚则(КоАП 第 13.11 条,法人):未做本地化 100–600 万卢布,再犯 600–1,800 万;未公布政策 3–6 万;未提交处理通知 10–30 万。来源:[consultant.ru 第 13.11 条](https://www.consultant.ru/document/cons_doc_LAW_34661/1f421640c6775ff67079ebde06a7d2f6d17b96db/)。

**广告标识(erid)**
- 网络广告须带「реклама」字样、广告主信息,并有广告数据运营商分配的识别码(38-ФЗ 第 18.1 条第 16–17 款)。来源:[第 18.1 条](https://www.consultant.ru/document/cons_doc_LAW_58968/2c4537e4796f6ff8b2736ed1b0d4fef08e14458e/)。
- 无识别码投放:法人罚 20–50 万卢布(КоАП 第 14.3 条第 16 款)。来源:[第 14.3 条](https://www.consultant.ru/document/cons_doc_LAW_34661/2d50fc1c4013ea9ab20b8b2666c1650b1dc4c982/)。
- 不算广告的情形:FAS 2025-04-09 第 АК/32908/25 号函:企业在自有官网、自有社媒页介绍自家商品和服务,属信息性内容,不是广告。每页都固定出现的推广横幅、推介第三方公司的内容,可能被认定为广告。来源:[consultant.ru](https://www.consultant.ru/document/cons_doc_LAW_503349/)。所以:自有站点的 SEO 内容不需要 erid;Yandex Direct、博主付费帖、第三方站付费文章需要。

## 六、红旗

- **Имитация действий пользователей(刷行为因素)**【官】:Yandex 列为搜索垃圾。限制可作用于全站或部分栏目;违规消除且算法确认不再重复后解除。提交复查后 30 天内出结果;未解除须等 30 天才能再交。来源:[官方说明](https://yandex.ru/support/webmaster/ru/threat/user-actions-imitation)、[Безопасность и нарушения](https://yandex.ru/support/webmaster/ru/service/security-threats)(官方共列 9 类违规,含 SEO 文本、隐藏跳转、模仿他站、伪装、低价值内容)。不做、不推荐、不代运营。
- 把 `/ru/` 页的 canonical 指向英文页:按官方说明,带指向别页 canonical 的页算非规范页,会从结果里消失(canonical 只是建议,两页内容差异大时 Yandex 可能忽略它,结果不可预测)。
- 按 IP 或 Accept-Language 自动跳语言版本:见第二节。
- 只在 robots.txt 里 Disallow 想下线的页:Yandex 仍可能展示,改用 noindex。
- 只接 GA、不做同意与跨境通知:见第五节。
- 引用「Yandex 76 条商业因子」这类清单:2026-10-21 在 Yandex 帮助中心没有找到这份清单;各机构的「商业因子」清单是第三方整理。Yandex 公开的是 ЭПОС 与透明度建议(真实地址、реквизиты、联系方式,见 [ЭПОС](https://yandex.ru/support/webmaster/ru/epos) 的 Экспертность 一节)。

## 七、工具

| 工具 | 用途 | 备注 |
|---|---|---|
| Yandex Webmaster | 验证、Sitemap、重抓、地区、SoV、ИКС、违规 | 【官】上线前必须验证 |
| Wordstat(wordstat.yandex.ru) | 查询量、地区分布(含亲和指数)、趋势;可下载 CSV;数据最早到 2018-01 | 【官】见第四节算子 |
| Yandex Metrica | 来源报表;Вебвизор、点击图、滚动图、表单分析(「Настройки → Счетчик」开启) | 【官】[点击图说明](https://yandex.ru/support/metrica/ru/behavior/click-map);开 Вебвизор 属处理个人数据,先取同意 |
| Топвизор、Keys.so、Букварикс、arsenkin、TGStat | 排名、竞品语义、扩词、Telegram 统计 | 第三方工具,本套件未逐一核验 |
| 本套件脚本 | 见第九节 | `robots_posture.py` 的 27 个机器人里没有 Yandex,YandexAdditional 要手查 |

其他渠道(本套件口径,无官方排名效果声明):Дзен、Habr、VK 用作分发与品牌提及;Telegram 频道须公开,`t.me/s/<频道>` 预览页每页 20 条,带 `rel="prev"` 与 `?before=` 翻页链接(2026-10-18 实测),t.me/robots.txt 返回 404。有线下门店的企业用 Яндекс Бизнес;审核可能要求拍摄入口视频(【官】[Подтвердить компанию](https://yandex.ru/support/business-priority/ru/moderation/moderation-address))。

## 八、本地实测(2026-10-09,本套件记录)

- 跑了 yandex.ru 与 habr.com × `site_audit --market ru` / `llmstxt check` / `head_check`。
- yandex.ru 当日 302 到 dzen.ru,工具跟随跳转,审计落在 JS 空壳上:title/desc/H1「缺失」是伪影。审计门户域前先 `curl -I` 看落点。
- yandex.ru 的 robots.txt 对 OAI-SearchBot 只写 `Disallow: /?`(禁带查询串的 URL;2026-10-21 复查,302 到 dzen.ru 与该规则都还在)。旧版工具用 stdlib robotparser,把它当整站禁止(`can_fetch('/')=False`),四条 AI 检索爬虫 CRITICAL 是误报。
- habr.com:缺 meta description、og:image 用相对 URL、alt 缺 40/41;charset 声明位于第 1,074 字节(超过 1,024);AI 检索爬虫放行。
- 两站 `/llms.txt` 等 4 个路径均 404。
- 脚本口径 2026-10-21 已改:`site_audit` 的 robots 判定改为 RFC 9309 最长匹配(实测 `Disallow: /?` 对 `/` 放行、对 `/?x=1` 禁止,`robots_posture.py` 同样放行);缺 H1 与缺 description 记 WARN,不再是 CRITICAL;`head_check` 里 twitter:* 与 OG 重复只记 INFO。上面 2026-10-09 的输出按旧口径,复跑以新口径为准。
- 仍有的盲区:不报告「审计的是跳转目标」;复数变格、引号、вы 一致性等 ru 专属检查要人工做(第九节第 13 项)。

## 九、俄语版上线检查清单(SaaS / API 文档站)

前提:站点已有 en/zh/es 版,新增 `/ru/`。每项写「检查什么 → 怎么查 → 通过判据」。

| # | 检查什么 | 怎么查 | 通过判据 |
|---|---|---|---|
| 1 | URL 结构 | 本套件口径:用现有域名的 `/ru/` 子目录;不按 IP 或 Accept-Language 自动跳转 | 每个俄语页有固定 URL;`curl -sI -H "Accept-Language: ru" https://site/en/x` 不跳转;俄语页返回 200 |
| 2 | hreflang 簇 | `python3 scripts/hreflang_cluster.py https://site/en/x https://site/ru/x https://site/es/x https://site/zh/x`;再 `curl -s https://site/ru/x \| grep -i hreflang` | 矩阵全部互指;每页含自身与 `x-default`;代码用 `ru`(服务多国俄语用户时不加地区);**HTML `<link>` 在场**(Yandex 不读 Sitemap 标注) |
| 3 | canonical | `python3 scripts/site_audit.py https://site/ru/x --market ru --json`;Webmaster「Индексирование → Страницы в поиске → Исключённые」 | 俄语页 canonical 指向自身;没有俄语页被标为非规范页 |
| 4 | robots.txt | `curl -sI https://site/robots.txt`;Webmaster「Анализ robots.txt」;`grep -i yandex robots.txt` | 返回 200;≤500 KB;无西里尔字符;若有 `User-agent: Yandex` 组,规则写全;跟踪参数用 Clean-param;有 `Sitemap:` 行 |
| 5 | Алиса AI 准入 | `grep -iA3 "YandexAdditional" robots.txt` | 想进回答:无针对 `YandexAdditional(Bot)` 的 Disallow;不想进:写明并记录决定 |
| 6 | Webmaster 验证 | 添加与线上完全一致的 host(协议、www);用 HTML 文件或 meta 或 DNS TXT | 显示已验证;子域单独验证 |
| 7 | Sitemap | `python3 scripts/sitemap_audit.py https://site --must-include https://site/ru/`;Webmaster「Файлы Sitemap」提交 | 含全部俄语 URL;≤50,000 条、≤50 MB;状态「Обработан」;「Анализ файлов Sitemap」无错误 |
| 8 | IndexNow | `python3 scripts/indexnow.py key --out DIR`,key 文件放根目录;`python3 scripts/indexnow.py submit --host site --key K --urls ru_urls.txt --endpoint yandex` | 返回 200 或 202;只提交新增和修改的 URL |
| 9 | 首批重抓 | Webmaster「Переобход страниц」提交核心俄语页(每日限额内) | 3 天内状态变为「Заявка обработана」;「Проверка страницы」显示已抓 |
| 10 | 地区 | Webmaster「Региональность」 | API 文档查询通常不分地域(本套件口径):选「Нет региона」或保持未指定;只有站上有覆盖俄罗斯的联系和服务信息时才选「Россия」 |
| 11 | 渲染 | `curl -s https://site/ru/x` 看正文是否在初始 HTML;Webmaster「Рендеринг страниц JavaScript」 | 正文在初始 HTML;已做 SSR 时按官方建议关闭渲染 |
| 12 | 文案机检 | `python3 scripts/market_lint.py --market ru page.html --report` | CRITICAL 0;拉丁混排只剩品牌和代码;日期 `09.10.2026`;货币 ₽ |
| 13 | 复数与格式 | i18n 用 ICU MessageFormat 的 one/few/many/other;单测数值 0、1、2、5、11、12、14、21、22、25、101、111、1,5;期望类别取自 CLDR 48 规则:0→many、1→one、2→few、5→many、11/12/14→many、21→one、22→few、25→many、101→one、111→many、1,5→other | 13 个数值的词形全部对上类别;数字千分位为 U+00A0;无 ASCII 直引号(`grep -n '"' ru.json` 只命中代码) |
| 14 | 法律页 | 人工核对第五节;`market_lint --report` 的法定透明层项 | 数据处理政策页 200,且每个表单旁有链接;同意单独勾选;用 Metrica 或 GA 前有同意;跨境与处理通知已评估并记录;付费推广有 erid |
| 15 | 标题与描述 | Webmaster「Заголовки и описания」报表(webmaster.yandex.ru/site/indexing/double-descriptions);`site_audit.py` 逐页看 title/description | 报表里没有重复项;每页有唯一 description;title 含品牌且不堆关键词(官方不给字符上限,屏宽决定截断) |
| 16 | 隐藏页的写法 | 想下线的页用 `noindex`(meta 或 `X-Robots-Tag`);`curl -sI` 看响应头 | 想下线的页没有被 Disallow 挡住(挡住后机器人读不到 noindex);主页要隐藏时用登录保护 |
| 17 | 计量 | Webmaster「Статистика поисковых запросов」与「Видимость сайта в Алисе AI」;GSC 网址检查 | 上线 4 周后记下首个基线;GSC 选用的 canonical 等于俄语页自身 |

## 维护

- 复审周期 **90 天**,下一次 **2027-01-09**;signals 清单与 `scripts/markets.json` 的 `markets.ru.review_cycle` 保持一致,以 json 为准。
- 触发即复审:Yandex Webmaster 帮助中心与博客(hreflang、Алиса AI、robots)、Yandex 季度财报(份额、Алиса AI 覆盖率)、152-ФЗ 与 38-ФЗ 修订、RKN 与 FAS 新函、yandex.ru→dzen 门户结构变化。
- 复审时用 `Disallow: /?` 夹具抽查 `site_audit` 与 `robots_posture.py`,确认不再误判整站禁止。
