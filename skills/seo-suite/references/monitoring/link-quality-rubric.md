# 外链质量评估

## 用途

审计外链、评估新增或丢失的链接、做竞品外链差距分析、判断是否需要处理有害链接时读。结果填进 [backlink-report.md](../../templates/monitor/backlink-report.md)。

**数据来源**：你自己的外链工具账号导出（例如 Ahrefs、Semrush、Moz、Majestic），或 Search Console 的「链接」报告。按[官方说明](https://support.google.com/webmasters/answer/9049606)（核对 2026-10-21），链接报告**不是完整列表**，只是内部和外部链接的样本；表格最多 1,000 行；按根域名分组；报告包含 Google 历来发现过的链接，其中可能有已被删除的；**报告不说明某条链接是否带 `nofollow`**。各工具的抓取覆盖也不同，数量只能在同一来源内按时间比较。任何结论都要打开链接页抽样人工核实。

## 一、六个评估维度

| 维度 | 看什么 | 加分 | 减分 |
|---|---|---|---|
| 主题相关性 | 链接页和整站的主题是否与目标页有关 | 同一领域、链接页正在讨论相关问题 | 主题完全无关 |
| 来源站点质量 | 有无真实读者、原创内容、编辑标准、可识别的作者或机构 | 有持续更新的原创内容和明确的编辑责任人 | 大量无关出站链接、明显在卖链接、内容拼凑 |
| 位置与上下文 | 链接在正文、侧栏、页脚还是全站模板里；周围文字是否说明了为什么链接 | 正文中作为引用或推荐出现 | 页脚、全站模板、隐藏或堆砌的链接 |
| 锚文本 | 是否描述了目标页内容 | 品牌名、URL、描述性短语自然混合 | 大量完全匹配商业关键词的锚文本 |
| rel 属性 | 普通链接，或 `nofollow`、`sponsored`、`ugc` | 付费或赞助链接已正确标注 | 明显是付费链接却没有标注 |
| 真实流量 | 链接页是否有读者、能否带来引荐访问 | GA4 引荐报告里能看到来自该页的访问 | 链接页没有任何访问迹象 |

`rel="sponsored"`、`rel="ugc"` 是 Google 在 2019-09-10 公告的新属性；公告同日起，`sponsored`、`ugc`、`nofollow` 三者对排名都按**提示（hint）**处理；对抓取和索引，`nofollow` 从 2020-03-01 起也按提示处理（[Search Central 博客 2019-09-10](https://developers.google.com/search/blog/2019/09/evolving-nofollow-new-ways-to-identify)，核对 2026-10-21）。现行文档的措辞是，带这些属性的链接「通常不会被跟随」（[出站链接 rel 说明](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)）。带 `nofollow` 的链接仍可能带来真实访问和品牌曝光，不等于没有价值。官方用法：付费或广告链接用 `sponsored`；评论、论坛等用户生成内容链接推荐用 `ugc`；其他不想背书的链接用 `nofollow`；可以同时写多个值。

## 二、打分方法

- 每个维度打 0–2 分（0 差、1 一般、2 好），按权重加总成 0–100 分。
- 本节整套打分方法是**本套件口径**，不来自 Google 或任何工具。默认权重是**可调的经验起点**：相关性 30、来源站点质量 25、位置与上下文 20、真实流量 10、锚文本 10、rel 5。站点类型不同就调整，并在报告里写明用的权重。
- 分数只用于排序和分层（重点维护 / 正常 / 待复核），不是 Google 的评分，也不能预测排名。
- **直接进待复核清单、不看总分**的情形：明显付费却没标注、链接农场或站群特征、被黑页面里注入的链接、与内容无关的全站链接。
- 每条打分都附证据：链接页 URL、链接所在位置的截图或页面摘录、锚文本原文、rel 值。

## 三、DR、DA 这类分数

DR、DA、Authority Score 等是各工具基于自己抓到的链接图算出来的，不是 Google 的指标，不同工具之间不可比。可以作为初筛排序的一个输入，但不能代替打开页面看相关性和上下文，也不要用「DR 低于某值就是垃圾」一刀切。

## 四、有害链接与 disavow

- Google [垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies#link-spam)（页面更新日 2026-08-28，核对 2026-10-21）把「链接垃圾」定义为主要为操纵排名而创建指向或来自某站点的链接。官方列出的例子包括:为排名买卖链接（用钱、物品或服务换链接，或寄送产品换取含链接的文章）、过度的互换链接或只为互链而设的合作页、用自动程序创建链接、把「必须带链接」写进服务条款而不让第三方选择标注、不阻断排名积分的文字广告、软文和原生广告里的优化锚文本、低质量目录和书签站链接、跨多站分发的小工具或页脚模板链接、论坛签名里的优化链接。同一页的原话:买卖链接本身不违规，只要用 `rel="nofollow"` 或 `rel="sponsored"` 标注。**所以买链不标注就是违反垃圾内容政策，可能收到「Unnatural links」人工操作，见 [penalty-recovery](penalty-recovery.md)。本套件不提供买链的价格或渠道建议。**
- 大多数低质量链接不需要处理。官方条件（[Disavow links](https://support.google.com/webmasters/answer/2648487)，核对 2026-10-21）:同时满足「有相当数量的垃圾、人为或低质量链接指向你」和「这些链接已经造成、或可能造成人工操作」，才考虑 disavow。**该工具不支持域名属性（Domain property）**；文件格式和上传规则见 [penalty-recovery](penalty-recovery.md) 3.1。
- 处理顺序：导出并人工核实 → 能联系对方删除的先联系 → 删不掉的才写进 disavow 文件 → 每条记录理由和日期，保留旧版本。
- 不要 disavow 权重低但内容真实的站点；用 `domain:` 整域屏蔽前，先确认该域没有正常链接。
- 怀疑有人恶意制造垃圾外链时，先记录和观察，不要急着批量 disavow。
- 你自己的站点放出的付费或赞助链接标 `sponsored`，用户生成内容里的链接标 `ugc`。

## 五、竞品外链差距

1. 用同一个工具导出本站和几个主要竞品的引用域。
2. 找出链接了多个竞品、却没有链接本站的域名。
3. 按相关性和来源站点质量筛选，不按数量排序。
4. 打开对方链接页，看它为什么链接竞品：资源推荐、引用数据、评测、新闻报道……
5. 判断本站有没有同等或更好的资源；有的话再按 [outreach-templates.md](outreach-templates.md) 起草外联，没有就先补内容。

不要追求复制竞品的每一条链接，也不要追求链接数量。

没有付费外链工具时，第 1、2 步用 `scripts/link_intel.py`：Common Crawl 域名级链接图查各家入链域，`intersect` 直接列出「链了 ≥2 个竞品、没链我们」的域；整套流程见 [link-intelligence](../research/link-intelligence.md)。

## 常见误区

- 用 DR 或 DA 阈值一刀切，判定链接好坏。
- 套用网上流传的「理想锚文本比例」「理想 nofollow 比例」。
- 为了让比例「看起来自然」而去制造链接。
- 看到工具标的「有害分数」就批量 disavow。

## 市场差异:本地链接红旗(定性信号，本套件经验)

下表只列**该市场常见的低质量外链信号**，用于初筛。买卖链接用于排名违反 Google 垃圾内容政策（见第四节），所以本表不列任何价格或渠道。各市场的具体做法没有逐条核对一手来源，只作排查线索。

| 市场 | 红旗信号 |
|---|---|
| 印尼 | 「保证第一页」承诺;公开兜售的 PBN;教育域名（.ac.id）上的付费链接 |
| 印度 | 排在「SEO India」类词上的外链机构;打包出售的 PBN 目录层 |
| 越南 | 规模化新闻站侧栏链接 |
| 泰国 | 灰色链接网络（赌博类站点被黑后挂链） |
| 德国 | 不标注广告的赞助文章——法律层面的风险（竞争法警告函）需向当地律师确认，本套件未核法条 |
| 中文 | 靠无人竞价的冷僻词刷出来的「权重」;蜘蛛池类工具（各引擎视为作弊的常见手段，百度官方口径本套件未核） |
| 阿拉伯语 | 新闻版面公开售卖——链接存在不等于编辑认可 |
| 通用 | 保证 dofollow、保证排名的承诺;链接页与你的主题无关 |

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 导出数据统一格式 | `python3 scripts/backlink_import.py export.csv --format auto --out unified.csv`（支持 ahrefs / semrush / gsc / unified） | 嗅探不出格式会退出码 2，不猜；先修数据 |
| 链接页抽样核实 | 每个分层抽 10 条以上，打开链接页，看位置、锚文本、周围文字 | 抽样结论与工具分数方向一致才用工具分数排序 |
| rel 标注 | `curl -sL <链接页URL> \| grep -o '<a [^>]*href="[^"]*你的域名[^"]*"[^>]*>'` 看 `rel` 值 | 明显付费或赞助却没有 `sponsored`/`nofollow` = 进待复核 |
| 自家出站链接标注 | 同样用 curl 抓自己的赞助页和 UGC 页，检查出站 `<a>` 的 `rel` | 付费链接无 `sponsored`/`nofollow`、用户内容链接无 `ugc`/`nofollow` = 修复 |
| 是否真要 disavow | 对照第四节两个条件和 [penalty-recovery](penalty-recovery.md) 3.1 | 两个条件不同时满足 = 不 disavow |
| 竞品差距 | 同一工具导出本站和竞品的引用域，再做差集 | 差集结果按相关性和来源质量筛，不按数量 |
| 外联跟进 | `python3 scripts/outreach_tracker.py list --file outreach.json` | 每条候选域有状态和下次复查日 |

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。

- 思路参考：[aaron-he-zhu/seo-geo-claude-skills · monitor/backlink-analyzer/references/link-quality-rubric.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/v9.9.12/monitor/backlink-analyzer/references/link-quality-rubric.md)（Apache-2.0）
- 一手资料：[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies)、[出站链接的 rel 属性](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)、[可抓取链接与锚文本](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)、[拒绝外链（Search Console 帮助）](https://support.google.com/webmasters/answer/2648487)

## (irinabuht12 深读 2026-10-09c)审计增量：可达性战术层、AI 引用源与结构性外链

> 来源：Ryze 系 49 技能仓库 [irinabuht12-oss/marketing-skills](https://github.com/irinabuht12-oss/marketing-skills)（**第三方开源仓库，不是官方规则**）的方法摘写。承接上文第五节「竞品外链差距」：差距筛出目标域名之后怎么选战术，以及 AI 搜索时代外链审计要多看两件事。该仓库自报的数字没有一手来源，本文已删；机会类型和「努力度」是该仓库的判断，作为本套件口径使用。

### 1. 机会类型 × 努力度（e2e-seo-assistant）

第五节差距分析的输出是一批「链了竞品没链本站」的域名；对每个域名按下表选战术，而不是一律发外联邮件：

| 机会类型 | 怎么找 | 努力度 |
|---|---|---|
| 资源页（resource pages） | 搜「[主题] + resources」 | 低 |
| 未链接的品牌提及 | 品牌监控 | 低 |
| 记者/专家引用（HARO 类） | 记者查询平台 | 低 |
| 失效链接替换（broken link building） | 竞品外链里的 404 页 | 中 |
| 客座发文 | 搜「[行业] + write for us」 | 中 |
| 复制竞品外链 | Ahrefs/Semrush 差集 | 中 |

### 2. AI 引用源可达性评分（citation-source-gap-finder / ai-visibility-audit）

AI 助手的回答只引用一小撮来源——评测平台、对比/listicle 文章、Reddit 帖、官方文档、维基。审计方法：

1. 对品类核心查询，收集 Perplexity / ChatGPT / Google AI Overviews 的回答及其引用 URL。
2. 按来源类型聚类（评测平台 / listicle / 社区 / 编辑内容 / 文档），统计每类的**引用份额**。先看头部集中度（少数 URL 占了多少引用），再谈覆盖面；集中度要用你自己收集的样本算。
3. 对每个聚类打**可达性分**并配一种战术：季度更新的 listicle → 直接投递更新；G2 类目录页 → 用评论量撬动；Reddit 帖 → 社区参与（有平台规则约束，不是发广告）。
4. 竞品引用地图（ai-visibility-audit）：把竞品被引追溯到具体来源页，逐个判断「本站能否进入同一来源」，比泛泛做外链精准。

判定链接价值时新增一问：**这条链接所在的页面/域名，是不是 AI 回答实际引用的那类来源**。同权重的两条外链，在被引来源上的那条溢出价值更高。

### 3. 结构性外链：产品放出的链（programmatic-seo-playbook Play 5）

审计外链组合时区分两类：内容挣来的链 vs **产品本身放出的链**（产品渲染在客户域名上——文档、widget、托管页、徽章——每个实例默认带一条回链）。注意:跨多站分发的小工具链接，如果是关键词锚文本或隐藏链接，属 Google 垃圾内容政策里的链接垃圾；要用 `rel="nofollow"`/`sponsored` 或无优化锚文本（见第四节）。审计自查问题：本站产品能否**默认**在客户站点留一条链？若能，这个杠杆优于任何内容外链；若不能，报告中注明这是组合缺口而非执行问题。

### 4. AI 引用前置条件（对上表「真实流量」维度的补充）

页面想出现在 AI 回答里，各平台的官方条件不同，以 [geo-evidence](../content/geo-evidence.md) 的分级证据为准：Google 的 AI 功能要求页面已被索引并可显示摘要，没有额外技术要求（[官方](https://developers.google.com/search/docs/appearance/ai-features)，核对 2026-10-21）；Bing 与 Copilot 共用抓取和索引。第三方提及对被引用的作用，本套件只作为待验证假设，不写成规则。

### 来源（irinabuht12 深读 2026-10-09c）

- [irinabuht12-oss/marketing-skills](https://github.com/irinabuht12-oss/marketing-skills)（49 个单文件技能，第三方）：`e2e-seo-assistant`（机会类型×努力度表）、`citation-source-gap-finder`（聚类与可达性评分流程）、`ai-visibility-audit`（竞品引用地图）、`programmatic-seo-playbook`（客户回链）。要点摘写，未复制原文。
