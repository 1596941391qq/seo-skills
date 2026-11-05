# 单页 SEO 审计评分

## 用途

对单个页面（或同一模板的一批页面）做 on-page 审计、需要给出可比较的分数和修复优先级时读。结果填进 [on-page-audit.md](../../templates/audit/on-page-audit.md)。

**分数只是内部排序工具**：用来比较页面、跟踪修复进度，不是 Google 的指标，也不能预测排名。

## 一、先过门槛，再打分

以下任何一项不通过，先列为最高优先级问题，不急着算总分：

- 返回 200，没有被重定向到别处（见 [http-status-codes.md](http-status-codes.md)）。
- 没有被 robots.txt 屏蔽，也没有 noindex（见 [robots-txt-reference.md](robots-txt-reference.md)）。
- canonical 指向自身，或指向一个合理的规范版本。
- 渲染后的主内容可见：JavaScript 渲染的页面，要看渲染后的 DOM，不能只看源码。

## 二、评分维度与默认权重

默认权重是**可调的经验起点**。按页面类型调整（例如商品页提高图片和页面体验的权重，长文指南提高内容的权重），并在报告里写明用了哪套权重。

| 维度 | 权重 | 检查什么 |
|---|---|---|
| 意图匹配与内容 | 30 | 是否直接满足目标查询的意图；有没有原创的信息、经验或数据；事实准确，注明出处；作者或负责主体清楚（对照 Google 的[有用内容自评问题](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)；自评问题也提醒不要为了显得新而改日期） |
| 标题与描述 | 15 | `<title>` 准确、独特，并写明页面主题；meta description 准确概括本页、不与其他页重复（见[标题链接](https://developers.google.com/search/docs/appearance/title-link)、[摘要](https://developers.google.com/search/docs/appearance/snippet)） |
| 链接 | 15 | 内链用可抓取的 `<a href>`，锚文本描述目标页；指向相关页面；没有失效链接；出站链接指向可靠来源，rel 使用正确 |
| 页面体验 | 15 | 有 CrUX 字段数据时看 Core Web Vitals，没有时用实验室数据诊断并注明；HTTPS；移动端内容与桌面端一致；没有遮挡主内容的弹窗 |
| 结构与可读性 | 10 | 标题层级能反映内容结构；段落、列表、表格用得合适；语义 HTML（见 [semantic-html.md](semantic-html.md)） |
| 结构化数据 | 10 | 类型合适，与可见内容一致，能通过验证（见 [validation-guide.md](validation-guide.md)）；没有标记本身不扣光这一项，只在该页类型确有合适的 Google 支持类型时提出建议 |
| 图片与媒体 | 5 | alt 描述图片内容；尺寸与显示尺寸相称；首屏主图不懒加载 |

## 三、打分方法

1. 每个维度拆成若干检查项，每项记为「通过 / 部分 / 未通过 / 无法验证」，分别按 1、0.5、0 计分。
2. 「无法验证」（例如没有字段数据、拿不到渲染后页面）不计入分母，并在报告里单列，不能猜。
3. 维度得分 = 得分 ÷ 可验证项数 × 权重；总分为各维度之和，满分 100。
4. **每个扣分项都附证据**：URL、检查时间、设备或 User-Agent，加上渲染后 DOM 片段、截图或工具导出（例如 Lighthouse 报告、Search Console 网址检查结果（需要该站点的权限）、爬虫导出）之一。
5. 修复优先级按「影响 × 修复成本」排，不按扣分多少排；门槛问题永远排第一。

## 四、评分纪律

- 各维度独立打分，不要因为标题写得好，就给内容也打高分。
- 对照检查项打分，不对照竞品打分；和竞品比较是另一项分析。
- 同一模板的页面放在一起评，模板问题只记一次，并注明影响的页面数。
- 两次评分（或两个人）结果差距大的检查项，把判定标准写得更具体。

## 五、不要作为扣分依据

以下说法没有 Google 一手依据，或与 Google 的说明相反（见 [SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)里「不必关注」的部分，核对 2026-10-21），不作为扣分项：

- 固定的字数目标、关键词密度。入门指南原文：没有神奇的字数目标，无论下限还是上限。堆砌关键词本身违反[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies)。
- 「只能有一个 H1」「标题层级不能跳级」。入门指南原文：标题顺序对读屏软件很好，但从 Google 搜索角度看，乱序没有影响，也没有理想的标题数量。层级清楚有助于读者和辅助技术，可以作为可读性建议，但不作为排名问题扣分。Bing 的指南要求有逻辑的标题层级，面向 Bing 的站点可以单独提。
- `<title>` 或 meta description 的固定字符数。Google 按设备宽度截断，并可能改写标题；只有在真实结果里被截断、影响理解时才提出。
- URL 里必须含关键词。入门指南原文：域名或 URL 路径里的关键词除了出现在面包屑里，几乎没有排名影响。URL 里放对用户有用的词仍是好习惯。
- 填写 meta keywords：Google 不使用该标签。
- 把 E-E-A-T 当成排名因子打分。入门指南原文：它不是。第一维度里的作者、出处检查是内容质量的自评项，不是 Google 的评分项。
- 为了富结果加 FAQPage。FAQ 富结果已停止展示，FAQPage 只用于页面上真实存在的问答（见 [geo-evidence.md](../content/geo-evidence.md)）。

## 检查清单

| # | 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|---|
| 1 | 门槛：状态码与重定向 | `python3 scripts/redirect_chain.py <URL> --max 3` | 通过：200 或一跳 301 到 200。失败：多跳、循环、终点非 200 |
| 2 | 门槛：可抓取、可索引 | `curl -sI <URL>` 看 `X-Robots-Tag`；`python3 scripts/head_check.py <URL>` 看 robots meta 与 canonical；robots.txt 见 [robots-txt-reference.md](robots-txt-reference.md) 检查清单 | 失败：noindex、被 robots.txt 屏蔽、canonical 指向无关页 |
| 3 | 门槛：渲染后主内容可见 | [rendering-seo.md](rendering-seo.md) 检查清单第 1、2 项 | 失败：主内容只在渲染后出现 |
| 4 | 页面体验用字段数据 | `python3 scripts/field_data.py --url <URL> --strategy both` | 失败：移动端 p75 任一核心指标为 poor。无字段数据时记"无法验证"，不猜 |
| 5 | 每个扣分项有证据 | 看报告里每个扣分项是否带 URL、时间、设备或 UA、截图或导出 | 失败：只有结论没有证据 |
| 6 | 没有用第五节的说法扣分 | 报告全文搜索"字数""H1""字符""关键词密度" | 失败：这些词出现在扣分理由里 |

## 交付时给出

总分和各维度得分、所用权重、门槛检查结果、「无法验证」清单、按优先级排列的问题表（问题、证据、影响、建议、验证方法）。

## 市场差异:审计阈值换算(拉平轮;英文默认值需按语言调)

> 本表所有数字都是**本套件的提示阈值**，用来发现可能有问题的页面。它们不是 Google 规则：Google 对 title 和 description 没有固定字符数（按设备宽度截断），对正文也没有字数要求（见第五节）。表中的字数行只作薄内容预警。

| 检查项 | 英文基线 | 市场换算 |
|---|---|---|
| title 长度 | ~60 字符 | 日 32 全角/泰按字素/德 55–65/越 45–65(词进前 30)——完整表见 title-formulas 市场差异节 |
| 薄内容预警线（不是字数要求） | ~300 词 | 日 300 全角字(体裁分层)/中 pillar ≥1,500 字/印尼 EYD V |
| 句长 | 15–20 词 | 中 15–25 字(>35 难解析)/泰 ≤25 词(>30 罚)/日 ≤25 词 |
| 营销词密度 | hype 克制 | 中 ≤3/页(创新领先/极致类)+标题党禁 |
| 内链数 | 按内容比例 | 日 1 見出し 1–2 本/3,000 字 4–8 本/单页 45 本上限 |
| 可访问文本 | 英文 alt | 阿语图内核心信息必须文本化(Naver AI Briefing 同款规则) |
| 锚文本/UA | — | 韩区 description=og:description;robots 检查含 Yeti 语义陷阱 |

**评分输出**:多语言站逐语言各出一份评分(架构纪律);阈值冲突时以目标市场口径为准。

## 完全装载:三个成品评分器(seomachine/SEOmator/gtm,百仓深扫)

> 本节是三个第三方评分器的权重与扣分规则，本套件没有逐条复核其源码，也不是 Google 规则。引用时写"某工具判定"。其中"词数<2000 扣 30"这类字数规则与 Google 的说明相反，**不要照搬**；"publishing_ready≥80"之类的线只对该工具有意义。

**seomachine 质量评分器**:六维权重 content 0.20/keywords 0.25/meta 0.15/structure 0.15/links 0.15/readability 0.10;**publishing_ready=总分≥80 且 0 个 critical**;扣分制:词数<2000 扣 30/标题缺关键词扣 20/前 100 词缺扣 15/密度>max×1.5 判 stuffing 扣 20/meta title 缺失扣 40/多 H1 扣 20/**>20% 句子超 37.5 词扣 10**/全文零列表扣 5。
**首屏 700 字符"5 秒测试"**(above_fold_analyzer):四元素加权 headline 0.35/value_prop 0.25/cta 0.25/trust 0.15,≥70 过;弱标题正则黑名单(`^Welcome to`/`^The (best|ultimate)`/`^Introducing`/`^We (help|offer)`)各扣 30;CTA 首现 <300 字符 +20;标题健康区 20-80 字符。
**信任信号计分**(trust_signal_analyzer):证言≤35(≥3 条 25 分+具体数字署名再+10)/社会证明≤30/风险反转≤25(**4 类中 3 类=strong 拿满**:free trial/no credit card/cancel anytime/guarantee)/权威≤10。
**SEOmator 373 规则权重表**(20 类):Core SEO 11%/Performance 10%/Links 8%/Images 8%/Security 8%/Technical 7%/Crawlability 5%/Structured Data 5%/Content 5%/JS Rendering 5%/Accessibility 7%/Social 3%/E-E-A-T 3%/URL 3%/Redirects 3%/Mobile 2%/i18n 2%/HTML 验证 2%/**AI-GEO 2%**/Legal 1%;Pass=100/Warn=50/Fail=0;档位 90=A/70=B/50=C。
**gtm 16 检查 142 分表**(audit-website-aeo):title 10(≥10 字符)/meta-description 10(≥50)/canonical 8/h1 8(恰好 1)/schema 8(≥1 JSON-LD)/og 8/内链 10(≥5)/image-alt 8(≥80%)/text-depth 12(≥250 词)/indexability 10/**ai-meta-tags 6(无 nosnippet/noai)**/heading-hierarchy 6/llms-txt 10(标题+链接+≥100 字符)/**ai-bot-access 12**/rss-feed 8;站点级通过=**80%+ 爬取页通过**;Foundational 50%(脚本)+Intelligence 50%(模型 6 维)。

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。核对 2026-10-21。

- 思路参考：[aaron-he-zhu/seo-geo-claude-skills · optimize/on-page-seo-auditor/references/scoring-rubric.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/v9.9.12/optimize/on-page-seo-auditor/references/scoring-rubric.md)（Apache-2.0）
- 一手资料：[SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)、[有用、可靠、以人为本的内容](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)、[标题链接](https://developers.google.com/search/docs/appearance/title-link)、[摘要与 meta description](https://developers.google.com/search/docs/appearance/snippet)、[可抓取链接与锚文本](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)、[Core Web Vitals 与 Google 搜索](https://developers.google.com/search/docs/appearance/core-web-vitals)、[优化 LCP](https://web.dev/articles/optimize-lcp)、[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies)
