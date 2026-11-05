# 审计规则目录 · Core SEO

> 从 [audit-rule-catalog.md](../audit-rule-catalog.md) 拆出(2026-10-21),正文原样搬运,只改了相对链接路径。来源、计分口径、ID 纪律、执行速查(`AUDIT`/`CRAWL` 等简写与 J1–J8、G1–G7 片段)和扩写进度见索引页。

### Core SEO(24 条,权重 11%)

源表现行(132d2384):`core-title-present` 缺失=fail;`core-title-length` **30-60 字符**=warn/fail;`core-description-present` 缺失=fail;`core-description-length` **120-160 字符**=warn;`core-canonical-present` 缺失=fail;`core-canonical-valid` 非绝对 http(s)=warn/fail(不请求目标);`core-viewport-present` 缺失=fail;`core-favicon-present` 缺失=fail;`core-h1-present` 缺失=fail、`core-h1-single` 多于 1 个=warn/fail;`core-canonical-header`(HTML canonical 与 HTTP Link 头不一致=warn);`core-nosnippet`(nosnippet/max-snippet:0=warn);`core-robots-meta`(noindex/nofollow/noarchive/noimageindex/none=warn);`core-title-unique`(跨页重复 title=warn,无 title=fail,crawl);**canonical 家族 8 条**:conflicting(HTML 与 Link 头不一致=fail)/to-homepage(深页指向首页=fail)/http-mismatch(协议不一致=fail)/loop(指向他页即 warn,不抓目标)/to-noindex(本页 noindex 且 canonical 指他页=warn)/outside-head(在 body 里=fail)/attributes(带 hreflang/lang/media/type=fail,其他多余属性=warn)/multiple(多条且不一致=fail,一致=warn);`core-robots-directive-mismatch`(meta 与 X-Robots-Tag 一方 index 一方 noindex=fail,多处声明 noindex=warn);`core-canonical-external`(指向外域,pass only)。长度阈值都是工具约定。

**解释层(20 条:18 条第一波 P0/P1 + 第三批 viewport/favicon)**

#### core-canonical-conflicting
- 源表:fail · 权重 8。HTML canonical 与 HTTP Link 头 canonical 指向不同 URL(小写、去尾斜杠后比);只有一处则通过;sitemap 不参与。建议优先级 high。
**依据**: 不要用不同方法为同一页指定不同 canonical;HTML 元素与 HTTP 头二选一,同时用更易出错([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。冲突时 Google 自行挑选。核对 2026-10-18。
**判据**: 通过=只有一处声明,或两处同值。失败=两处不同。
**执行**: G1 与 G3 的 URL 比对;site_audit 只读 HTML canonical,不查 Link 头。
**修复**: 全部信号指同一目标(通常自引用);只保留一种载体。
**关联**: core-canonical-header、core-canonical-multiple;[redirects-canonical.md](../redirects-canonical.md)

#### core-canonical-multiple
- 源表:warn/fail · 权重 6。同一文档有多条 rel=canonical:不一致=fail,一致=warn。建议优先级 high(不一致)/low(一致)。
**依据**: "When more than one is specified, all rel=canonical links will be ignored"([Google 2013 博文](https://developers.google.com/search/blog/2013/04/5-common-mistakes-with-relcanonical));常见原因是 SEO 插件默认再插一条。核对 2026-10-18。
**判据**: 通过=恰好 1 条。失败=≥2 条且目标不同;警告=≥2 条但相同。
**执行**: `G1 | wc -l` 大于 1 即命中;site_audit 只保留最后一条,不报多条。
**修复**: 找到双写来源(框架默认+插件/手写)删掉一处;CI 断言每页 canonical 计数=1。
**关联**: core-canonical-conflicting、core-canonical-outside-head;[head-elements.md](../head-elements.md)

#### core-canonical-outside-head
- 源表:fail · 权重 8。rel=canonical 出现在 `<head>` 之外。建议优先级 high。
**依据**: canonical 元素"only accepted if it appears in the `<head>` section";body 里的会被忽略([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls);[2013 博文](https://developers.google.com/search/blog/2013/04/5-common-mistakes-with-relcanonical))。head 里出现非法元素时,Google 忽略其后的全部元素([valid-page-metadata](https://developers.google.com/search/docs/crawling-indexing/valid-page-metadata))。核对 2026-10-18。
**判据**: 通过=canonical 在 head 内,且之前没有非法元素。失败=在 body 里,或排在 head 内的非法元素(img、iframe 等)之后。
**执行**: G2 有输出即失败;渲染后位置用 GSC 网址检查的已抓取 HTML 复核。
**修复**: 移进 head 并尽量靠前;清除 head 内的非法元素。
**关联**: core-canonical-multiple、htmlval-head-content;[head-elements.md](../head-elements.md)、[rendering-seo.md](../rendering-seo.md)

#### core-canonical-attributes
- 源表:warn/fail · 权重 7。canonical 元素带 hreflang/lang/media/type=fail,带其他多余属性=warn。建议优先级 high/low。
**依据**: 带 hreflang、lang、media、type 的 rel=canonical "are not used for canonicalization"([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。核对 2026-10-18。
**判据**: 通过=只有 rel 与 href。失败=带上述四种属性之一。
**执行**: `G1 | grep -iE ' (hreflang|lang|media|type)='` 有输出即失败。
**修复**: canonical 只留 rel+href;语言与设备变体用独立的 alternate 元素。
**关联**: core-canonical-conflicting;[head-elements.md](../head-elements.md) link 速查

#### core-canonical-loop
- 源表:warn · 权重 7。canonical 指向他页即 warn(可能回指);不抓目标。真环由 crawl-canonical-loop 判。建议优先级 medium。
**依据**: Google 文档无专门说法;规范页本身应自引用([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。核对 2026-10-18。
**判据**: 通过=自引用。警告=指向他页(需确认目标自引用)。失败=目标指回本页(两页环)。
**执行**: G1 读目标;对目标再跑 G1,指回本页即失败;全站用 J2。
**修复**: 确定终点页让它自引用,其余直指它。
**关联**: crawl-canonical-loop;[redirects-canonical.md](../redirects-canonical.md)

#### core-canonical-to-noindex
- 源表:warn · 权重 7。本页带 noindex(robots/googlebot meta 或 X-Robots-Tag),canonical 又指向他页;自引用通过;不抓目标。建议优先级 medium。
**依据**: Google 不建议用 noindex 阻止单站内规范页的选择,推荐只用 rel=canonical([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。目标 noindex 的情形见 crawl-canonical-to-noindex。核对 2026-10-18。
**判据**: 通过=noindex 与"canonical 指他页"不同时出现。失败=同时出现。
**执行**: `AUDIT URL` 出现 `[CRITICAL] robots: noindex`,且 G1 的 href 不是本页。
**修复**: 要合并到他页:删 noindex,保留 canonical;要退出索引:删 canonical,保留 noindex。
**关联**: crawl-canonical-to-noindex;[redirects-canonical.md](../redirects-canonical.md) 第三节冲突矩阵

#### core-canonical-header
- 源表:warn · 权重 7。HTML canonical 与 HTTP Link 头 canonical 不一致;SEOmator 建议 HTML 页只用 HTML 元素,Link 头留给 PDF 等非 HTML 资源(工具建议)。建议优先级 medium。
**依据**: Google 两种方式都支持,建议选一种;Link 头的优势是可用于 PDF 等非 HTML 文件([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。核对 2026-10-18。
**判据**: 通过=只用一种,或两者同值。失败=两者不同(与 conflicting 同源,本条侧重载体选择)。
**执行**: G3 有输出时与 G1 比对。Link 头常由 CDN/网关注入,应用代码里找不到就查网关配置。
**修复**: HTML 页删掉 Link 头版本;PDF/DOCX 用 Link 头。
**关联**: core-canonical-conflicting;[head-elements.md](../head-elements.md)、[http-status-codes.md](../http-status-codes.md)

#### core-canonical-to-homepage
- 源表:fail · 权重 6。非首页的 canonical 指向首页。建议优先级 medium。
**依据**: canonical 表示"这页是那页的重复";Google 举过分类页 canonical 到精选文章的反例,后果是分类页从结果里消失([2013 博文 Mistake 4](https://developers.google.com/search/blog/2013/04/5-common-mistakes-with-relcanonical))。深页与首页几乎不可能重复,多为模板兜底变量为空。核对 2026-10-18。
**判据**: 通过=深页 canonical 不是站点根。失败=路径不是 `/` 的页 canonical 等于首页。
**执行**: G1 的 href 等于 `https://域名/` 而本页路径不是 `/` 即失败。
**修复**: 模板兜底改为自引用;排查变量注入顺序。打印版等真重复页可保留。
**关联**: core-canonical-present;[redirects-canonical.md](../redirects-canonical.md)

#### core-canonical-http-mismatch
- 源表:fail · 权重 7。页面与 canonical 协议不一致(HTTPS 页指 HTTP 或反之)。建议优先级 medium。
**依据**: Google 默认优先 HTTPS 作规范页,但 HTTPS 页 canonical 指向 HTTP 页是让它改选 HTTP 的冲突信号之一([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。"引擎会自动升级、风险低"的说法不成立。核对 2026-10-18。
**判据**: 通过=协议一致(应为 https)。失败=不一致。
**执行**: G1 的 href 协议与页面 URL 协议比对。
**修复**: canonical 输出 https 绝对 URL,全站统一。
**关联**: crawl-canonical-form-drift;[redirects-canonical.md](../redirects-canonical.md)

#### core-canonical-present
- 源表:`core-canonical-present` fail · 权重 10(缺失);`core-canonical-valid` warn/fail · 权重 1(href 不是绝对 http(s) URL;空或相对=fail,缺失=warn;不请求目标)。建议优先级 medium(缺失是缺信号)。
**依据**: 指定 canonical 不是必需,不指定时 Google 自行选择;规范页上加自引用 canonical 是建议做法([规范化文档](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls))。相对路径 Google 支持但不推荐,建议用绝对 URL(同上;2013 博文 Mistake 2 讲相对路径写错的常见事故)。核对 2026-10-21。
**判据**: 通过=有一条绝对 https canonical。警告=缺失(单版本页可接受)或相对路径。失败=空值(源表)。
**执行**: `AUDIT URL`:`[WARN] canonical: 缺失`;`[WARN] canonical: 相对 URL(Google 支持但建议改绝对 URL)`(值不带协议就报,`/path` 与 `//host` 都算)。site_audit 对这两项只给 WARN,不给 CRITICAL。
**修复**: 有参数、分页、打印版等重复形态的页补自引用绝对 canonical。
**关联**: core-canonical-conflicting;[redirects-canonical.md](../redirects-canonical.md) 六场景

#### core-canonical-external
- 源表:pass only · 权重 1。canonical 指向他 host;永远通过,只报出供确认。建议优先级 insight。
**依据**: Google 不建议用 canonical 处理与联合发布伙伴的重复,最有效的做法是伙伴屏蔽索引;攻击者也会插入跨域 canonical 劫持页面([规范化排障](https://developers.google.com/search/docs/crawling-indexing/canonicalization-troubleshooting))。核对 2026-10-18。
**判据**: 不判对错。确认:自有多域合并=保持;供稿伙伴场景=改用伙伴侧 noindex;非预期=按被黑或模板错处理。
**执行**: `AUDIT URL` 出现 `[INFO] canonical: 指向外域`(已按 host 小写、去默认端口比较)。
**修复**: 非预期的改回自引用,并检查是否被注入。
**关联**: core-canonical-conflicting;[redirects-canonical.md](../redirects-canonical.md)

#### core-robots-directive-mismatch
- 源表:warn/fail · 权重 5。meta robots 与 X-Robots-Tag 一方 index/follow、一方 noindex/nofollow=fail;多处重复声明 noindex/nofollow=warn。建议优先级 high/low。
**依据**: 多条规则冲突时,Google 取全部否定规则之和,即限制更严的生效("use the sum of the negative rules",[robots meta 规范](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag))。核对 2026-10-18。
**判据**: 通过=所有载体意图一致且只声明一次。失败=一处 index、一处 noindex(结果按 noindex 处理)。
**执行**: G6 同时列出 meta 与响应头,人工比对;site_audit 把两处合并后只报 noindex。
**修复**: 统一索引意图;只在一处声明(服务器层 X-Robots-Tag 便于统一管理)。
**关联**: core-robots-meta、crawl-indexability-conflict;[head-elements.md](../head-elements.md)

#### core-robots-meta
- 源表:warn · 权重 5。meta robots 或 X-Robots-Tag 含 noindex/nofollow/noarchive/noimageindex/none。这是清点项,不等于有错。建议优先级 medium。
**依据**: noindex=不在结果中显示;nofollow=不跟随本页链接;none=noindex+nofollow;noimageindex=不索引本页图片;noarchive 已不被 Google 使用(缓存链接功能已不存在)([robots meta 规范](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag))。核对 2026-10-18。
**判据**: 通过=指令都是刻意的。失败=误加在本该索引的页上。
**执行**: `AUDIT URL` 报 `[CRITICAL] robots: noindex`(通用 robots、`name="googlebot"`、X-Robots-Tag 不带爬虫名或带 googlebot;`none` 等同 noindex)与 nosnippet;`name="bingbot"` 或 `X-Robots-Tag: bingbot: noindex` 只对 Bing 生效,报 `[WARN] robots: bingbot noindex——只对 Bing 生效…`,其余 bingbot 指令报 INFO;`max-video-preview` 非整数报 WARN、为 0 报 INFO(依据 [Bing robots meta 文档](https://www.bing.com/webmasters/help/robots-meta-tags-and-attributes-that-bing-supports-5198d240))。nofollow、noimageindex 仍用 G6 补查(只在文档)。
**修复**: 误加的删除;刻意的归档,并把页面从审计分母剔除。
**关联**: core-robots-directive-mismatch、crawl-noindex-in-sitemap;[robots-txt-reference.md](../robots-txt-reference.md)

#### core-nosnippet
- 源表:warn · 权重 7。meta 或 X-Robots-Tag 含 nosnippet 或 max-snippet:0。建议优先级 low。
**依据**: nosnippet 对网页、图片、Discover、AI Overviews、AI Mode 全部生效,并阻止内容作为 AI Overviews 与 AI Mode 的直接输入;max-snippet:0 等同 nosnippet([robots meta 规范](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag))。这是 Google 的口径,其他 AI 助手是否遵守各看其文档。核对 2026-10-18。
**判据**: 通过=无该指令,或刻意为之且已登记。失败=非刻意的 nosnippet。
**执行**: `AUDIT URL` 出现 `[WARN] robots: nosnippet(会限制 AI 特性)`;max-snippet:0 用 G6 查。只想隐藏片段时改用 `data-nosnippet`。
**修复**: 需要摘要与 AI 引用就删除;刻意的记录在案。
**关联**: core-robots-meta;[head-elements.md](../head-elements.md) meta 全表

#### core-title-present
- 源表:`core-title-present` fail · 权重 25(无非空 `<title>`;内联 SVG 里的 title 不算);`core-title-length` warn/fail · 权重 1(30-60 字符)。长度是工具约定。建议优先级 high(缺失)/low(长度)。
**依据**: 每个页面都要有 `<title>`;"there's no limit on how long a `<title>` element can be",title link 按需截断以适配设备宽度,Google 还会从 h1、og:title、锚文本等来源自行生成([title link 文档](https://developers.google.com/search/docs/appearance/title-link))。**Google 无固定上限;本套件 site_audit 用 markets.json 的阈值作提示(en 为 <20 或 >60 字符)。** 像素宽度(~580px 一类)是工具约定。核对 2026-10-18。
**判据**: 通过=非空且描述本页。失败=缺失或空白。长度超出提示阈值只算提示。
**执行**: `AUDIT URL [--market xx]`:`[CRITICAL] title: 缺失`;`[WARN] title: N chars <20`;`[WARN] title: N chars 超上限 60`(其他市场按 `scripts/markets.json` 的单位与上限:ja 32、zh 30 按显示宽度,全角计 1、半角计 0.5)。
**修复**: 缺失就补每页唯一、描述性的标题;过长就把限定词挪进 description;避免堆砌与全站同模板标题。
**关联**: core-title-unique;[head-elements.md](../head-elements.md)、[scoring-rubric.md](../scoring-rubric.md) "不作为扣分依据"节

#### core-title-unique ⛏
- 源表:warn/fail · 权重 5 · 需 `--crawl`。不分大小写与多余空白比较;首个通过,其后同 title 的页 warn;无 title 的页 fail。建议优先级 high(模板级)/low(零星)。
**依据**: Google 要求避免重复或模板化的 `<title>`,每页要有区分本页内容的文字([title link 文档](https://developers.google.com/search/docs/appearance/title-link))。"数千页重复才触发质量算法"无官方出处,已删。核对 2026-10-18。
**判据**: 通过=每个可索引页 title 唯一。失败=同一 title 出现在 ≥2 个可索引页(分页、参数变体先按 canonical 处理)。
**执行**: `CRAWL` 后跑 J8,每行一个重复 title 及次数。
**修复**: 模板加页面级变量(分类名/页码/属性);真重复页用 canonical 或 301 合并。
**关联**: content-duplicate-description、content-duplicate-h1;[scoring-rubric.md](../scoring-rubric.md)

#### core-description-present
- 源表:`core-description-present` fail · 权重 15(缺 meta description);`core-description-length` warn · 权重 1(120-160 字符)。长度是工具约定。建议优先级 medium(缺失)/low(长度)。
**依据**: Google 主要用页面内容生成摘要,只在 meta description 更准确时采用;"There's no limit on how long a meta description can be",摘要按需截断;大站可程序化生成([snippet 文档](https://developers.google.com/search/docs/appearance/snippet))。**Google 无固定上限,也不要求必须有 description;本套件用 `scripts/markets.json` 的区间作提示(en 为 <77 或 >155 字符,下限 `desc_min` 默认取上限的一半,本套件口径)。** 核对 2026-10-21。
**判据**: 通过=有且描述本页。失败=缺失(源表 fail;site_audit 与建议优先级都只到 WARN/medium)。长度只算提示。
**执行**: `AUDIT URL [--market xx]`:`[WARN] description: 缺失`;`[WARN] description: N chars 低于下限 77(本套件口径)`;`[WARN] description: N chars 超上限 155`(其他市场的下限和上限见 markets.json;zh 按显示宽度)。
**修复**: 核心页手写(先给答案和行动点);模板页用真实字段拼装,别输出空串或全站同文案。
**关联**: core-title-present、content-duplicate-description;[head-elements.md](../head-elements.md)

#### core-h1-present
- 源表:`core-h1-present` fail · 权重 15(无 h1);`core-h1-single` warn/fail · 权重 1(多于 1 个)。工具约定。建议优先级 medium(缺失)/low(多个)。
**依据**: 标题的数量与顺序对 Google 搜索无所谓,对屏幕阅读器有用([SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide));把主标题放进第一个可见 h1 有助 Google 选 title link([title link 文档](https://developers.google.com/search/docs/appearance/title-link))。"只能有一个 H1"不是 Google 规则。核对 2026-10-18。
**判据**: 通过=有一个描述主题的 h1。警告=缺失或多个(组件卡片各一个 h1 时)。
**执行**: `AUDIT URL`:`[WARN] h1: 无 H1`(源表 fail,site_audit 按 Google 文档降为 WARN);`[WARN] h1: N 个 H1`。
**修复**: 每页一个主题 h1,与 title 呼应但不雷同;卡片标题降为 h2/h3。
**关联**: core-title-present、content-duplicate-h1;[semantic-html.md](../semantic-html.md)

#### core-viewport [待核 ID]
- 名称/类型: viewport 缺失 —— issue · 优先级 high · 输出 CRITICAL(源表 `core-viewport-present` fail)
**这意味(what)**: 页面 head 没有 `<meta name="viewport">`。
**为什么(why)**: 缺 viewport 时多数移动浏览器按约 980px 的虚拟视口渲染再缩放(浏览器行为,不是 Google 规则),字号、点击目标与布局都按桌面算。Google 自 2024-07-05 起只用智能手机版 Googlebot 抓取,"在移动设备上完全无法访问"的内容不再可索引([公告](https://developers.google.com/search/blog/2024/06/mobile-indexing-vlast-final-final.doc));缺 viewport 不等于无法访问,但移动体验与评估全部失真。规范值 `width=device-width, initial-scale=1`([head-elements.md](../head-elements.md))。
**触发(trigger)**: head 内无 viewport meta 即 fail;配置不合规另归 mobile-viewport-config。
**不修的条件(caveat)**: 纯桌面工具页、仅登录后使用的后台可按内部系统豁免。
**修复(fix)**: 全站模板 head 注入 `<meta name="viewport" content="width=device-width, initial-scale=1">`;别用 user-scalable=no。
**关联(seealso)**: mobile-viewport-config、mobile-font-size;[head-elements.md](../head-elements.md)、[mobile-seo.md](../mobile-seo.md)

#### core-favicon [待核 ID]
- 名称/类型: favicon 缺失 —— warning · 优先级 low · 输出 CRITICAL(源表现行 `core-favicon-present` fail,权重 1;旧快照为 warn)
**这意味(what)**: head 无 `<link rel="icon">` 或 `rel="shortcut icon"`(源表:只有 apple-touch-icon 不算)。
**为什么(why)**: Google 自 2019-05 移动结果改版起在结果卡顶部显示网站图标与名称([公告](https://blog.google/products-and-platforms/products/search/new-design-google-search/));缺了只剩占位图标,浏览器标签页与书签同样。纯品牌露出项,与排名无关。
**触发(trigger)**: head 无 rel=icon/shortcut icon 即触发(源表);site_audit 不查,手工另查 `curl -sI 站点/favicon.ico`。
**不修的条件(caveat)**: 内部系统/预发布环境可豁免。
**修复(fix)**: 出多尺寸 ICO 或 PNG/SVG + `<link rel="icon" sizes="…">`;apple-touch-icon 180px 另配;别引用外域图标。
**关联(seealso)**: core-viewport;[head-elements.md](../head-elements.md)
