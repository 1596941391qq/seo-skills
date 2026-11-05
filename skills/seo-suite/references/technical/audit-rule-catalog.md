# 审计规则全目录(SEOmator 373 规则,源码深读)

> 来源:SEOmator 开源审计器 [seo-skills/seo-audit-skill](https://github.com/seo-skills/seo-audit-skill) 的 `docs/SEO-AUDIT-RULES.md`。2026-10-09 吸收的是 e047a5e2(2026-09-22)快照。SEOmator 原仓库 2026-10-15 在 132d2384 按代码重写了该文档,多条规则的语义与严重度变了。**第一波 P0/P1 的 79 条已按 132d2384 复核(核对 2026-10-18),2026-10-21 又逐条回读 Google 文档原文并对齐 site_audit 现行行为;其余表格与条目仍是 09-22 快照,与现行版冲突时以现行版为准。**
> 三态计分:Pass=100 / Warn=50 / Fail=0;总分=类别加权平均。现行档位 **90-100=A / 80-89=B / 70-79=C / 50-69=D / <50=F**;单页审计另有封顶(noindex 或 robots.txt 屏蔽封 20,无 title 封 69 等)。
> **20 类权重表已吸收于 [scoring-rubric.md](scoring-rubric.md)「完全装载」节,不重抄**(Core 11%/Perf 10%/Links·Images·Security 各 8%/Tech·A11y 各 7%/Crawl·SD·Content·JS 各 5%/Social·E-E-A-T·URL·Redirects 各 3%/Mobile·i18n·HTMLval·AI-GEO 各 2%/Legal 1%)。
> **严重度与阈值是 SEOmator 的工具约定,不是搜索引擎规则。** 搜索引擎的一手说法写在各条「依据」里;没有官方出处的写"无官方出处"。
> 三类横切机制先记住,后面表格反复引用:
> - **crawl 模式专属**(`--crawl`):依赖多页爬取的跨页状态;单页审计时报 not measured(权重 0 不计分)。现行 17 条,表内标 ⛏。
> - **渲染专属**(`--no-cwv` 时跳过):带"requires render"标记的 per-asset 规则,数据来自 Playwright 渲染。
> - **TOML 开关**:`[rules] disable=["core-*"]` 按前缀禁类;`enable=["core-*","perf-*"]+disable=["*"]` 只留指定类。

## 用途与读法(2026-10-21 拆分后新增)

- 用途:审计规则的总入口。规则正文按类别拆到 [audit-rules/](audit-rules/) 下 20 个文件,本页只留来源、计分口径、〇节执行速查和第五、六节。
- 读法:先看下表,按类别打开对应文件;要跑命令时回本页〇节查 `AUDIT`、`CRAWL` 等简写和 J1–J8、G1–G7 片段。
- 「对应 site_audit 检查」列是 `site_audit.py` 输出里的 area 名,只表示这一类里有部分规则能被单页审计覆盖,不表示整类都测。
- 规则数和权重照抄各类标题与上面的权重行。拆分只搬不改;条目里的相对链接已改成从 `audit-rules/` 出发的路径。

| 类别 | 文件 | 规则数 | 权重 | 对应 site_audit 检查 |
|---|---|---|---|---|
| Crawlability | [audit-rules/crawlability.md](audit-rules/crawlability.md) | 38 | 5% | `robots`、`canonical`;⛏ 跨页条目单页不测,用 `CRAWL`/`SITEMAP` |
| E-E-A-T | [audit-rules/eeat.md](audit-rules/eeat.md) | 16 | 3% | 无(site_audit 不查) |
| Internationalization | [audit-rules/i18n.md](audit-rules/i18n.md) | 13 | 2% | `a11y`(html 无 lang);其余用 `HREFLANG` |
| Core SEO | [audit-rules/core-seo.md](audit-rules/core-seo.md) | 24 | 11% | `title`、`description`、`h1`、`canonical`、`robots`、`staging` |
| Performance | [audit-rules/performance.md](audit-rules/performance.md) | 28 | 10% | 无;现场数据用 `field_data.py` |
| Links | [audit-rules/links.md](audit-rules/links.md) | 27 | 8% | `links`(只计数) |
| Images | [audit-rules/images.md](audit-rules/images.md) | 14 | 8% | `images` |
| Security | [audit-rules/security.md](audit-rules/security.md) | 26 | 8% | 无 |
| Technical SEO | [audit-rules/technical-seo.md](audit-rules/technical-seo.md) | 18 | 7% | `fetch`;`robots`/`sitemap` 不可达(INFO) |
| Structured Data | [audit-rules/structured-data.md](audit-rules/structured-data.md) | 19 | 5% | `schema` |
| Content | [audit-rules/content.md](audit-rules/content.md) | 27 | 5% | `content`(词数 <200 / >15000)、`headings`(跳级、h1 前低级标题、H2 少)、`bluf` |
| JavaScript Rendering | [audit-rules/javascript-rendering.md](audit-rules/javascript-rendering.md) | 16 | 5% | `rendering` |
| Accessibility | [audit-rules/accessibility.md](audit-rules/accessibility.md) | 36 | 7% | `a11y` |
| Social | [audit-rules/social.md](audit-rules/social.md) | 9 | 3% | `og`(title/description/image 缺失、og:image/og:url 非绝对) |
| URL Structure | [audit-rules/url-structure.md](audit-rules/url-structure.md) | 14 | 3% | 无 |
| Redirects | [audit-rules/redirects.md](audit-rules/redirects.md) | 11 | 3% | 无;用 `REDIR` |
| Mobile | [audit-rules/mobile.md](audit-rules/mobile.md) | 12 | 2% | `rendering`(插件内容,Lighthouse plugins 口径;源表无此条,见第七节) |
| HTML Validation | [audit-rules/html-validation.md](audit-rules/html-validation.md) | 11 | 2% | 无 |
| AI/GEO Readiness | [audit-rules/ai-geo-readiness.md](audit-rules/ai-geo-readiness.md) | 13 | 2% | `ai-bots`、`llms.txt`、`freshness`、`semantic-html`、`robots`(bingbot 专属指令、max-video-preview) |
| Legal Compliance | [audit-rules/legal-compliance.md](audit-rules/legal-compliance.md) | 1 | 1% | 无 |

---

## 〇、解释层规范与执行速查

> 结构与文案纪律来自 [borrow-specs.md](../research/borrow-specs.md) A2 节。**各节表格仍是全量索引,永不删行**。解释层覆盖 220 条,分批见文末第六节。

- **P0/P1 执行版(第一波 79 条)**:规则 ID 标题 + 「源表」行(现行严重度·权重·判定;工具约定;建议优先级)+ 依据 / 判据 / 执行 / 修复 / 关联 五段。依据只写一手来源并附链接;判据写通过/失败;执行写 site_audit 对应的输出行或替代命令。
- **其余条目(八段式)**:what/why/trigger/caveat/fix/seealso。原「导出(export)」字段的 `Reports > …` 路径在 SEOmator 文档中不存在,本套件也无法执行,已全部删除。
- **两轴哲学**:类型(issue|warning|opportunity)× 优先级(critical|high|medium|low|insight)独立打分。Opportunity 永不给 critical;"坏信号>缺信号":主动矛盾排 critical-high,单纯缺失排 medium-low。个别"缺信号但源表 fail"的规则(canonical 缺失、title 缺失)输出 CRITICAL、建议优先级降档,条目内注明。
- **ID 纪律**:第一波条目标题用源表现行 ID。第四节其余标 [待核 ID] 的是本套件按家族起的名字,不是源表 ID。阈值照抄源表,源表未公布的写"未公布",不发明新阈值。
- **caveat 常驻样本**:title 长度高度主观(Google 无上限,按设备宽度截断,且常自行改写 title link);站内重复内容不违反 Google 垃圾政策,影响在规范页选择与抓取效率;缺 alt 只是错失描述,**装饰图空 alt 是正确做法**。

**执行速查**(在 skill 根目录运行;`URL`、`站点` 换成实际值):

| 简写 | 命令 | 用途与限制 |
|---|---|---|
| `AUDIT` | `python3 scripts/site_audit.py URL [--market xx] [--json] [--export-dir DIR]` | 单页;输出 `[级别] area: 消息`;有 CRITICAL 退出码 1。CRITICAL 只有:缺 title、noindex、staging 子域、搜索类 AI bot 被禁(Google-Extended 为 WARN)、抓取失败。缺 description、缺 H1/多个 H1、缺 canonical、相对 canonical 是 WARN;>100 链接是 INFO(工具约定,Google 无此上限)。title/description 区间取 `scripts/markets.json`(`desc_min` 为 description 下限;zh/ja/ko 按显示宽度)。挑战页只按结构特征判,命中输出 `[SKIP]` 拒审。不跨页、不渲染;meta robots 取最后一个 `name=robots`,与 `name=googlebot`、X-Robots-Tag 合并判 noindex(认 `none`);`name=bingbot` 与 `X-Robots-Tag: bingbot:` 只对 Bing 生效,单独报;`--serp-titles FILE` 给了才比 title 与搜索结果标题(没给时 `meta.serp_title_check` 写跳过原因)。全部检查与目录的对应见第七节 |
| `SITEMAP` | `python3 scripts/sitemap_audit.py 站点 --check-limit 0` | 六坏桶:1 非200/2 3xx/3 noindex/4 canonical 他指/5 robots 屏蔽/6 参数重复 + lastmod 三判定;逐条检查默认 ≤500 条全查、超过按位置均匀抽 500 条(含首尾),输出 [范围] 行写明查了几条、共几条;sitemap 本身返回 HTML 报「不是 sitemap(软 404)」并计入失败;加 `--hreflang` 另查 sitemap 载体的 hreflang(自引用、互指、码值、完整 URL) |
| `HREFLANG` | `python3 scripts/hreflang_cluster.py URL1 URL2 …` | 簇矩阵:自引用/语言码/绝对URL/HTTP200/双向回报 + 三载体冲突;跟随重定向;语言码按 Google 口径判(拒 es-419、认 zh-Hans、大小写不敏感、UK/EU 报保留码) |
| `REDIR` | `python3 scripts/redirect_chain.py URL [--max N]` | 逐跳;>2 跳 WARN,>5 跳或环 CRITICAL;临时码用于永久变化 WARN;HTTPS→HTTP 降级 WARN;打印「终态: HTTP」 |
| `CRAWL` | `python3 scripts/site_crawl.py 站点 --max N --out crawl.json [--check-external]` | `pages[]` 含 url/status/final_url/canonical/depth/inlinks/source,另有 `edges`、`orphans`、`link_issues`(重定向目标页无直接内链、HTTP↔HTTPS 混链、HTTPS→HTTP 重定向)、`subdomain_robots`;`--check-external` 另出 `external_redirects`(外链 URL 3xx 抽检);N 要覆盖全站,截断时入链偏少 |
| `GRAPH` | `python3 scripts/link_graph.py --crawl crawl.json` | 深度直方图(>3 层占比)、入链 0/1 清单、锚文本审计 |
| `ROBOTS` | `python3 scripts/robots_posture.py 站点/robots.txt --json` | 含 `crawl_delay`(`*` 组)与 `sitemaps` 字段 |
| `GSC 网址检查` | Search Console → 网址检查 | 「是否允许抓取 / 是否允许编入索引 / 用户声明与 Google 选择的规范网址」;「查看已抓取的网页 → 更多信息」列出资源 |

jq/grep 片段(`crawl.json` 来自 `CRAWL`;已用样例数据实测):
- **J1 canonical 链**:`jq -r '(.pages|map({(.url):.canonical})|add) as $c | .pages[] | select(.canonical and .canonical!=.url) | select($c[.canonical] and $c[.canonical]!=.canonical and $c[.canonical]!=.url) | "\(.url) -> \(.canonical) -> \($c[.canonical])"' crawl.json`
- **J2 canonical 环**:`jq -r '(.pages|map({(.url):.canonical})|add) as $c | .pages[] | select(.canonical and .canonical!=.url and $c[.canonical]==.url) | "\(.url) <-> \(.canonical)"' crawl.json`
- **J3 canonical 目标非 200 或重定向**:`jq -r '(.pages|map({(.url):.})|add) as $p | .pages[] | select(.canonical and .canonical!=.url and $p[.canonical]) | $p[.canonical] as $t | select($t.status!=200 or $t.final_url) | "\(.url) -> \(.canonical) status=\($t.status) final=\($t.final_url)"' crawl.json`
- **J4 sitemap 孤儿**:`jq -r '.pages[] | select(.source=="sitemap" and .inlinks==0) | .url' crawl.json`
- **J5 深度 >3**:`jq -r '.pages[] | select(.depth != null and .depth > 3) | "\(.depth)\t\(.url)"' crawl.json`
- **J6 死内链来源**:`jq -r '(.pages|map(select(.status==null or .status>=400)|.url)) as $bad | .edges[] | select(.dst as $d | $bad|index($d)) | "\(.src) -> \(.dst)"' crawl.json`
- **J7 内链指向重定向**:`jq -r '(.pages|map(select(.final_url)|{(.url):.final_url})|add // {}) as $r | .edges[] | select($r[.dst]) | "\(.src) -> \(.dst) => \($r[.dst])"' crawl.json`
- **J8 重复 title**:`jq -r '.pages[] | .title // empty | ascii_downcase | gsub("^\\s+|\\s+$";"")' crawl.json | sort | uniq -c | awk '$1>1'`
- **G1 canonical 标签**:`curl -s URL | grep -oiE '<link[^>]+rel=.?canonical[^>]*>'`(加 `| wc -l` 计数)
- **G2 head 外的 canonical**:`curl -s URL | tr -d '\n' | grep -oiE '</head>.*' | grep -oiE '<link[^>]+rel=.?canonical[^>]*>'`
- **G3 Link 头 canonical**:`curl -sI URL | grep -i '^link:.*canonical'`
- **G4 相对 hreflang**:`curl -s URL | grep -oiE '<link[^>]+hreflang=[^>]*>' | grep -ivE 'href=.?https?://'`
- **G5 开发环境链接**:`curl -s URL | grep -oiE 'href=.?(https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)|file:)[^ >]*'`
- **G6 索引指令**:`curl -s URL | grep -oiE '<meta[^>]+name=.?(robots|googlebot)[^>]*>'; curl -sI URL | grep -i '^x-robots-tag'`
- **G7 hreflang 清单**:`curl -s URL | grep -oiE '<link[^>]+hreflang=[^>]*>'`

---

## 四、其余 17 类规则目录(浓缩表,保留全部数字阈值)

17 类的浓缩表和解释层已拆到 [audit-rules/](audit-rules/) 下对应文件,见上面的类别表。

---

## 五、吸收备注(去重边界)

- CWV 五阈值/权重表/档位 → [LCP.md](LCP.md)、[scoring-rubric.md](scoring-rubric.md)。
- raw-vs-rendered 双抓实现 → [rendering-seo.md](rendering-seo.md)。
- AI/GEO 13 条 + 实体图六查 → [validation-guide.md](validation-guide.md)、[ai-crawler-policy.md](ai-crawler-policy.md)、[entity-signal-checklist.md](entity-signal-checklist.md)。
- 本文新增独有:Crawlability 38 条全目、E-E-A-T 16 条全目、i18n 13 条全目(含入向校验/x-default 洞察两维度)、Links 入链族 8 条、Content 跨页族、Mobile parity 五条、全类别数字阈值。

---

## 六、未覆盖规则(扩写边界与进度)

- 解释层本版覆盖 **220 条**:第一波 79 条 P0/P1(Crawlability 34/i18n 13/Core SEO 18/Links 4/Redirects 4/Content 重复族 4/Images alt 1/Social og:url 1,聚焦 canonical·noindex·重复内容·断链·重定向·sitemap·hreflang·title/H1 结构家族)+ 第二波 44 条 medium/low 高价值(Crawlability 分页 2/Links 6/Content 6/Images 5/Social 3/Performance 8/Structured Data 5/URL 5/JS Rendering 4)+ 第三批 47 条(Technical SEO 10:5xx·超时·空 HTML·soft-404·非 404 4xx·自定义 404·robots.txt·sitemap 存在性·Content-Type·URL 一致性·埋点卫生;Security 6:HTTPS/混合内容·安全头族·TLS/证书·Cookie·链接引用安全·内容危险信号;Mobile 6:字号·viewport 配置·横向滚动·插页·image maps·parity 五条;Links 6:无内链·外链可达·畸形 href 家族·断锚点·onclick·外链 nofollow;HTML Validation 5:文档结构·多 title/description·head 非法元素·base·体积与 lorem;Content 5:文本比·可读性·相对薄·标题模式·MIME 破损;Redirects 3:静态资源·大小写规范化·资源链;Core SEO 2:viewport/favicon;Crawlability 2:pdf-size/crawl-delay 收口 38 条全量;i18n 1:lang 一致性;Performance 1:preconnect)+ 第四批 50 条(E-E-A-T 14:byline·资历·日期/更新机制·引用·about·contact·隐私+ToS·地址+geo meta·联盟披露·免责·编辑政策·信任信号·YMYL 检测器·NAP,16 条全量;Accessibility 32:对比度·触控目标·可访问名·按钮名·名含可见文本·焦点·tabindex·skip 链·accesskey·表单 label·一控件一 label·autocomplete token·landmark·恰一 main·标题跳级·空标题·链接文本·同链同的·表格 th+scope·caption·字幕文稿·iframe title·SVG 名·alt 复读·ARIA 拼错·aria-hidden 聚焦·根级 aria-hidden·widget 父子角色·列表结构·role 反证·input image alt·重复 ID,34 条规则全量[alt 归 Images、语言码归 i18n、禁缩放归 mobile];Structured Data 3:实体引用·实体一致性·评分作用域,六查全量;Legal 1:cookie consent 收口 20 类全覆盖)。
- **其余约 150 条仍以表格/浓缩表形式维护,是唯一事实来源**:阈值以表格为准,条目与表格冲突时改条目不改表。AI/GEO 13 条(细则已吸收于 [validation-guide.md](validation-guide.md) 与 [ai-crawler-policy.md](ai-crawler-policy.md),仅存目)与各节表内剩余同构细分条(Performance minify 子项、Mobile parity 子项、Links 入链族切面等)的判定阈值都在第四节浓缩表与被吸收的专项文档(LCP.md/validation-guide.md/ai-crawler-policy.md 等)里。
- 后续扩写按同规范增量进行:第四批后 20 类主要规则均有解释层覆盖,剩余为 AI/GEO 13 条(细则在专项文档,存目即可)与各节同构细分条(逐条单列的扩写价值低);后续批次以源目录变动核对、[待核] 阈值复核与新增规则补录为主——每扩一批,更新本节数字。
- 新增条目必须照抄源表阈值并遵守〇节 ID 纪律与两轴哲学;来源变动的核对入口是 intel_check.py 的 google-updates 源(映射到本文)。

---

## 七、site_audit 实际检查与目录对齐(2026-11-05,RQ-229 第 3 批)

`site_audit.py` 的每条检查都在下表登记(`tests/test_rq229_accuracy.py` 逐条核对 `RULE_SLUGS`,脚本新增检查而本表没写会红)。「依据」写一手出处;没有出处的写「本套件口径」。

| 导出 slug | 级别 | 对应目录规则 | 依据 |
|---|---|---|---|
| `staging-subdomain` | CRITICAL | 〇节 AUDIT | 本套件口径 |
| `title-missing` / `title-too-long` / `title-too-short` | CRITICAL / WARN / WARN | core-title-present | 上限按 markets.json;Google 无字数上限 |
| `title-serp-mismatch` | INFO | 源表无;Ahrefs「Page and SERP titles do not match」 | [Ahrefs 站点审计研究](https://ahrefs.com/blog/site-audit-study/);只在给了 `--serp-titles` 时比 |
| `description-missing` / `description-too-long` / `description-too-short` | WARN | core-description-present | 本套件口径(下限 desc_min) |
| `h1-missing` / `h1-multiple` | WARN | core-h1-present | SEO 入门指南 |
| `headings-skip-level` / `headings-before-h1` | WARN | content-heading-family、a11y-heading-hierarchy | [W3C WAI Headings](https://www.w3.org/WAI/tutorials/page-structure/headings/) |
| `headings-h2-few` | INFO | javascript-rendering(rendering 五项之 H1/H2) | geo-aeo-tracker 源码口径 |
| `canonical-missing` / `canonical-relative` / `canonical-external` | WARN / WARN / INFO | core-canonical-present、core-canonical-external | Google canonical 文档 |
| `robots-noindex` / `robots-nosnippet` | CRITICAL / WARN | core-robots-meta、core-nosnippet | Google robots meta 文档 |
| `robots-bingbot-noindex` / `robots-bingbot-only` / `robots-max-video-preview` | WARN / INFO / WARN·INFO | core-robots-meta(GEO 补项) | [Bing robots meta 文档](https://www.bing.com/webmasters/help/robots-meta-tags-and-attributes-that-bing-supports-5198d240) |
| `og-title-missing` / `og-description-missing` / `og-image-missing` | WARN | social 类 | ogp.me |
| `og-image-not-absolute` / `og-url-not-absolute` | WARN | social-og-url-canonical | [ogp.me](https://ogp.me/) Types 表:URL 须 http(s):// |
| `a11y-no-lang` | WARN | i18n-lang-attribute、a11y 类 | HTML 标准 lang |
| `content-thin` / `content-too-long` | WARN | content-word-count(源表阈值 300/100 只在文档;脚本用 <200)/ AI-GEO 存目 | 本套件口径 |
| `links-too-many` | INFO | links 类 | 工具约定,Google 无上限 |
| `images-alt-missing` | WARN | images-alt-present | W3C WAI Decorative Images(`alt=""` 不算缺失) |
| `schema-jsonld-missing` | WARN | structured-data 类 | 本套件口径 |
| `rendering-csr` / `rendering-no-noscript` / `rendering-js-heavy` / `rendering-weak-server-content` | WARN·INFO | javascript-rendering | geo-aeo-tracker 源码口径 |
| `rendering-plugins` | WARN | 源表无;Lighthouse「Document uses plugins」、Ahrefs 同名项 | [Lighthouse plugins](https://developer.chrome.com/docs/lighthouse/seo/plugins) |
| `bluf-low` | INFO | AI-GEO 存目 | geo-aeo-tracker 源码公式 |
| `injection`(隐藏元素或注释里对 AI 下指令的文字,原文照录,最多 3 条) | CRITICAL | 源表无;RQ-229 例 7 对抗场景 | [Google 垃圾内容政策:隐藏文字](https://developers.google.com/search/docs/essentials/spam-policies#hidden-text-and-links);OWASP LLM01 提示注入 |
| `robots-unreachable` / `sitemap-unreachable` / `llms-txt-unreachable` | INFO | technical-seo、AI-GEO | RFC 9309(robots 404=全放行,不报) |
| `ai-bots-blocked` / `ai-bots-training-blocked` | CRITICAL·WARN / INFO | AI-GEO 存目、[ai-crawler-policy.md](ai-crawler-policy.md) | 各家 bot 官方页 |
| `freshness-stale` | INFO | AI-GEO 存目 | Semrush AI Search Health(183 天) |
| `semantic-html-low` | INFO | AI-GEO 存目 | 阈值本套件口径 |
| `fetch`(无导出 slug,按 area 兜底) | CRITICAL | technical-seo 5xx/超时 | — |

**目录里有、脚本没跑(或目录写错)——本批处理结果:**

| 条目 | 原状 | 处理 |
|---|---|---|
| images-alt-present | 目录写「alt="" 也算缺失」,脚本只算没有 alt 属性 | 改目录(脚本对) |
| core-robots-meta | 目录写「不识别 none 与 googlebot meta」 | 脚本补上 none、googlebot、bingbot 分路;目录改写;nofollow、noimageindex 仍只在文档 |
| social-og-url-canonical | 目录写「site_audit 不查 og:url」 | 脚本补绝对 URL 检查;与 canonical 是否一致仍只在文档 |
| content-heading-family | 目录列标题长度 <10/>70、同页重复标题 | 工具约定、无搜索引擎依据,不补,标「只在文档」 |
| content-word-count | 源表 300/100 阈值 | 脚本用 <200(本套件口径),源表阈值标「只在文档」 |
| AI/GEO 类别表 `semantic_html` | area 名写错 | 改成脚本实际输出的 `semantic-html` |
| core-canonical-conflicting、core-canonical-multiple、core-robots-directive-mismatch | 目录已写明 site_audit 不查 | 维持「只在文档」(G1/G3/G6 手工) |

**脚本跑了、目录没写(本批之前已有)**:`content-too-long`、`bluf-low`、`freshness-stale`、`ai-bots-training-blocked`、`headings-h2-few`、`robots/sitemap/llms-txt-unreachable`——上表已登记。

**本批新增(Ahrefs 6 项与 GEO 3 项的落点)**:

| 项 | 落在 | 判据出处 |
|---|---|---|
| 重定向目标页没有直接内链 | `CRAWL` 的 `link_issues.redirect_target_no_direct_inlinks` | [Ahrefs 帮助](https://help.ahrefs.com/en/articles/2754350):「pages that are only linked via a redirect」 |
| HTTP 页链到 HTTPS(及反向) | `CRAWL` 的 `link_issues.http_page_links_to_https` / `https_page_links_to_http` | 反向项 [Ahrefs 帮助](https://help.ahrefs.com/en/articles/2614035);正向项官方无单篇帮助文,出现在 Ahrefs 问题清单(Patrick Stox,SERP Conf 2024 演讲) |
| HTTPS 跳到 HTTP | `CRAWL` 的 `link_issues.https_to_http_redirects`;`REDIR` 的 WARN | [Ahrefs 帮助](https://help.ahrefs.com/en/articles/2442569) |
| 页面 title 与搜索结果标题不一致 | `AUDIT --serp-titles FILE` | [Ahrefs 研究](https://ahrefs.com/blog/site-audit-study/);无 SERP 数据时跳过并写原因 |
| 页面用了插件 | `AUDIT` 的 `rendering-plugins` | [Lighthouse plugins](https://developer.chrome.com/docs/lighthouse/seo/plugins)、[Ahrefs SEO issues](https://ahrefs.com/blog/seo-issues/) |
| 外链 3xx | `CRAWL --check-external` 的 `external_redirects`(按引用页数抽前 50 个外链 URL,写明查了几个/共几个) | [Ahrefs 帮助](https://help.ahrefs.com/en/articles/2724308)、[Ahrefs 301 文第 9 节](https://ahrefs.com/blog/301-redirects/) |
| 各子域各自的 robots.txt | `CRAWL` 的 `subdomain_robots`(抓得到才判) | [Bing 博客 2012](https://blogs.bing.com/webmaster/2012/5/To-crawl-or-not-to-crawl,-that-is-BingBot-s-questi/)、[Google robots.txt 规范](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec) |
| Bing 的 max-video-preview | `AUDIT` 的 `robots-max-video-preview` | [Bing robots meta 文档](https://www.bing.com/webmasters/help/robots-meta-tags-and-attributes-that-bing-supports-5198d240) |
| 只对 Bing 生效的 `name="bingbot"` | `AUDIT` 的 `robots-bingbot-noindex` / `robots-bingbot-only` | 同上 |

