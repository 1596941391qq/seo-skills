# 域名与 SEO：选域·历史风险·迁移·国际架构·品牌与 AI 引用

> 建立于 2026-10-09，2026-10-21 全文复核：Google 官方文档逐条重读，第三方说法逐条找原文，找不到的删除。断言半衰期：政策类 12 个月，AI 引用类 6 个月。
> 分工：**多站怎么组织**（ccTLD、子目录、子域，站群光谱）以 [site-networks](site-networks.md) 为准；本文件只管"单个域名本身"。外链画像见 [backlink-profile-analysis](backlink-profile-analysis.md)；301/302 语义见 [http-status-codes](../technical/http-status-codes.md)；hreflang 校验见 [hreflang-validation](../technical/hreflang-validation.md)；PBN 与过期域的黑帽侧见 [backlink-directory](backlink-directory.md) 与 [site-networks](site-networks.md) 第一节。
> **口径**：标"K"的是本套件的做法约定，不是外部事实。

## 用途与何时读

新项目选域名、评估买或回收旧域名、准备换域或迁移、客户问"要不要为每个国家买 ccTLD"、品牌重塑后 AI 引用掉了。

顺序：选域（第一节）→ 旧域或买域过第二节尽调 → 换地址按第三节 → 跨国架构看第四节 → 品牌与 AI 影响看第五节 → 技术层按需查第六节。第八节是检查清单。

## 一、选域：TLD 的真实影响与命名

### 1.1 TLD 对排名

| 层 | 结论 | 出处（核对 2026-10-21） |
|---|---|---|
| 新 gTLD（.io、.app、.xyz 等） | Google 按其他 gTLD 同样处理；"TLD 里的关键词不带来优势或劣势"；.london、.bayern 这类地区新 TLD 也按 gTLD 处理 | Google 官方博客 [Google's handling of new top level domains](https://developers.google.com/search/blog/2015/07/googles-handling-of-new-top-level)（2015-07-21；文首注明部分信息可能已过时，当前规则看多地区文档） |
| TLD 一般影响 | TLD "只有在你面向某个国家的用户时才有意义，即便如此也通常是低影响信号"；否则 Google 不在乎你用 .com、.org 还是 .asia | [SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) |
| ccTLD | 是判断目标地区的信号之一，与 hreflang、服务器位置、本地地址电话、语言货币、本地链接并列；`.ad .ai .as .bz .cc .cd .co .dj .fm .io .la .me .ms .nu .sc .sr .su .tv .tk .ws` 被按 gTLD 处理（"名单可能变化"） | [多地区站点文档](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)（更新日 2025-12-10） |
| 间接影响 | 有第三方称部分便宜 TLD（.xyz、.info）更容易被邮件服务商标记为垃圾（SEJ 转述，未找到原始数据）。上一版引用的 Mueller 原话"我不会选超便宜、被垃圾淹没的 TLD"没有找到出处，已删 | 未核 |
| 记忆与直输 | .com 更易记、更易直接输入 | K（行业常识，无统计来源） |

**决策口径**：TLD 是品牌与信任决策，不是排名决策。给客户的理由写"点击信任、直输、邮件送达率"，不写"SEO 加成"。邮件送达自己测：用目标 TLD 的域名向几家主流邮箱发测试邮件，看是否进垃圾箱。

**选 TLD 的快速表**（K）：

| 场景 | 首选 | 次选 | 不选 |
|---|---|---|---|
| 全球通用品牌 | .com | 与品牌匹配的 .io、.ai、.co | 含关键词的杂 gTLD（.best、.shop） |
| 单一国家业务 | 该国 ccTLD | .com 加本地化 URL 与 hreflang | 面向该国的其他 ccTLD |
| 垂直专业信任（法律、医疗） | .com 品牌域 | .law 等受验证 gTLD 作副入口 | 把受验证 gTLD 当唯一主域 |
| 预算受限试验站 | .com 变体 | .dev、.app（强制 HTTPS） | 促销价的 .top、.xyz 层 |

### 1.2 精确匹配域名（EMD）

- Google 起始指南："从排名角度看，域名（或 URL 路径）里的关键词本身几乎没有影响，除了出现在面包屑里"。注意：这里说的"关键词在域名里"，不是"域名等于关键词"，但官方口径是几乎无影响。
- John Mueller 2022-02 也确认关键词域名没有 SEO 加成（[SEJ 转述](https://www.searchenginejournal.com/google-no-seo-bonus-for-keyword-based-domains/438324/)）。
- 上一版的"2012 EMD 更新""131 位 SEO 的调查""长周期受控实验"没有找到一手出处，已删。
- 残余价值（推断，K，无官方证实）：本地服务加城市词的域名可能提升点击信任；别人自然链向你时，域名本身即锚文本。**代价是确定的**：主题天花板、转型困难、转售价值低（见第七节）。

### 1.3 命名规则（K）

| 规则 | 口径 |
|---|---|
| 长度 | 无算法阈值；实操以"口头拼写测试"为准，念一遍对方能拼对 |
| 连字符 | 一个尚可，两个以上显得不专业 |
| 数字 | 有拼写歧义（2/two）时不用，除非品牌本身含数字 |
| 品牌词与关键词 | 默认用可发音的品牌域；关键词域只在 1.2 残余价值成立且客户明确不做品类扩张时选 |
| IDN | 见 4.3 |

### 1.4 域名年龄

- John Mueller 2019 年在回应时说"域名年龄什么用也没有"（"No, domain age helps nothing"，[Search Engine Roundtable 转述 2019-07-08](https://www.seroundtable.com/old-new-domain-names-google-seo-27844.html)）。Google 文档里没有把域名年龄列为排名因素。
- 老域名表现好是**相关不是因果**（K，推断）：它们积累了外链、内容和用户行为。买"只老不干净"的域，比新域更糟。
- 上一版"新域头 1–3 个月信任爬坡"没有来源，已删数字。新站排名需要时间是普遍现象，但没有"年龄因子"。
- 中文市场：百度对新域和空壳备案的处理见 [markets/zh](../markets/zh.md)。

### 1.5 新项目选域工作流（K）

1. 品牌词先行：先定品牌名（可发音、商标可查、社媒 handle 可注册）。
2. 候选池 5–8 个：逐个过口头拼写、商标库初查、社媒一致性。
3. 二手域必须尽调：按 2.3。
4. 注册：多年期、自动续费、注册商锁定、WHOIS 隐私；防御性注册只买品牌错拼或异后缀两个以内。
5. 把"为什么选这个域"写进项目档案。

## 二、域名历史与风险

### 2.1 过期域名抢注：Google 已写成政策

Google 垃圾内容政策的 **Expired domain abuse**：买过期域名，并"主要为操纵搜索排名而重新利用"，放"几乎没有用户价值"的内容。例子：把曾属政府机构的站改成联盟内容；在曾属非营利医疗慈善机构的站上卖医疗产品；在前小学网站上放赌博内容（[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies#expired-domain-abuse)，核对 2026-10-21）。2024-03-05 公告同时说明："用旧域名建一个为人服务的、全新的原创站"没问题（[公告](https://developers.google.com/search/blog/2024/03/core-update-spam-policies)）。

操作含义：

- 买过期域放低价值内容，违反 Google 政策，不做。
- 把过期域 301 进主站以"借旧链接权重"：政策原文示例没有逐字列出这种做法，但它以取得排名为目的，符合 link spam 的意图。本套件不做。
- 品牌回购、并购续营是合法场景；先过 2.3 尽调，再决定 301 还是放置。

### 2.2 历史包袱：Google 没公开的部分，按风险处理

Google 没有公开说明域名易主后人工处置和链接信号如何处理（未核）。尽调时把下面几项当风险：

- 手动处置未撤销、垃圾外链档案、Safe Browsing 标记、邮件黑名单，可能跟着域名走（行业常见说法，无一手来源，K）。
- 买方看不到前任所有者 Search Console 里的手动处置记录；唯一办法是要求卖家提供只读权限（K）。
- 上一版"Google 对过期加易主的域做信号打折""换域后流量跌七成、5 个月才恢复"没有一手来源，已删。

### 2.3 买前尽调七步（顺序执行，任何一步红灯即停；K）

| 步骤 | 怎么查（真实命令或入口） | 红灯 |
|---|---|---|
| 1 Wayback 全史扫描 | `curl -s "http://web.archive.org/cdx/search/cdx?url=域名&output=json&fl=timestamp,statuscode&collapse=timestamp:6&limit=500"` 列出快照月份，再逐年打开 | 药、赌、贷、成人、目录站、PBN 痕迹；主题跳变 ≥2 次 |
| 2 外链档案交叉 | 导出 Ahrefs/Majestic 等外链，`python3 scripts/backlink_import.py <导出.csv> --format auto --brand <品牌词>`，看 [backlink-profile-analysis](backlink-profile-analysis.md) | 锚文本垃圾占比高、买链年代的链入尖峰、热门链接页已不存在 |
| 3 处罚史 | 让卖家提供 Search Console 只读权限，看"安全和人工处置"；`site:域名` 看收录形态 | 有未撤销的人工处置；无权限且拒绝提供 |
| 4 WHOIS 历史 | whois 历史服务（付费，如 DomainTools）；`whois 域名` 看当前状态 | 注册人频繁跳变，长期停放（parked） |
| 5 安全与黑名单 | Google [Safe Browsing 站点状态](https://transparencyreport.google.com/safe-browsing/search)（输入 `?url=域名`）、VirusTotal、Spamhaus 域名查询 | 任一在案 |
| 6 残留品牌 | Wayback 和搜索看旧品牌是否仍有搜索与口碑 | 有旧品牌词需求＝你要承接别人的声誉，通常是负担 |
| 7 价格 | 对比同类无历史新域的价格 | 价格远超档案残值＝卖家卖的是你不知道的历史 |

**尽调结论的四种判定**（K）：

| 判定 | 证据形态 | 处置 |
|---|---|---|
| 干净可用 | Wayback 全史同主题、外链自然、无黑名单 | 可用于品牌回购或并购续营 |
| 档案残值型 | 干净，但外链档案与目标业务无关 | 只做品牌保卫（放置，不 301） |
| 污染可洗 | 有停放史或轻度垃圾链，无人工处置痕迹 | 隔离放置 6 个月以上，不接外链，再复评；不直接 301 进主站（6 个月是本套件保守值，无官方数字） |
| 红灯 | 药赌贷成人史、人工处置未撤销、Safe Browsing 在案 | 放弃 |

### 2.4 重定向：Google 原文要点

核对 2026-10-21（[301 重定向文档](https://developers.google.com/search/docs/crawling-indexing/301-redirects)、[迁移文档](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)）：

| 项 | Google 原文要点 | 本套件动作 |
|---|---|---|
| PageRank | "301 和其他永久重定向不会造成 PageRank 损失"（迁移文档"Don't worry about link credit"） | 用永久重定向，不再引用"传递 90–99%"这类无出处数字 |
| 永久与临时 | 永久重定向：搜索结果显示新目标；临时重定向：搜索结果显示源页 | 永久搬家用 301 或 308 |
| 链长 | Googlebot 最多跟随 10 跳；Google 建议直接指向最终目的地，实在不行"最好不超过 3 跳，少于 5 跳" | `python3 scripts/redirect_chain.py <URL> --max 3` |
| 无关重定向 | 不要把许多旧 URL 重定向到一个不相关的页面（如新站首页），可能被当成 soft 404；合并内容到单页时可以 | URL 一对一映射 |
| 保留时长 | 迁移文档：保留重定向"尽可能长，一般至少 1 年"，从用户角度可考虑无限期 | 见 3.4 |

上一版"DomCop：受罚资产恢复成本 $312–$9,380/站""RealSiteWorth Renew-Forever 规则""HetNeo 链路取证"均无一手来源，已删。关于续费：Google 地址变更文档建议"至少再付一年旧域名费用，以防他人买走并滥用你放弃的域名"（见 3.3）。

## 三、域名迁移

适用：换主域、http→https、子域→子目录、多域收编。原则：**内容不动、URL 一对一、用工具申报、监测拉长**。子域↔子目录的架构权衡见 [site-networks](site-networks.md) 2.2/2.4。

### 3.1 预热期（切流前 4 周以上，K）

1. 冻结内容：迁移窗口内不并发改版。Google 说明迁移同时重构内容和 URL 结构，"很可能出现流量损失"，因为 Google 需要重新评估单页（[Change of Address](https://support.google.com/webmasters/answer/9370220?hl=en)"Best practices"一节）。
2. 新域预热：解析、证书、一页真实内容让其被抓取；查 `site:`、Safe Browsing，并按 2.3 尽调（新买的域也可能是别人的过期域）。
3. URL 映射表：全站爬取加 GSC 导出，生成 `旧URL → 新URL` 1:1 表。命令：`python3 scripts/site_crawl.py https://旧域 --out crawl_old.json --urls-out urls_old.txt`。每条旧 URL 必须有去处。
4. 基准线存档：top 词排名、分段流量、索引量、热门外链页。
5. 清点所有写死旧域名的地方：canonical、hreflang、schema、统计、sitemap、robots。

### 3.2 一次切还是分批

Google 迁移文档的建议：

- **中小站**：同时迁移所有 URL，不要一次一个板块——帮助用户使用新站，也帮助 Google 算法更快识别迁移并更新索引。
- **大站**：可一次迁一个板块，更易监控和修复问题；也可先迁一小块测试，再迁其余部分。
- 迁移期间"搜索可见度可能临时波动，排名会随时间稳定"；中小站"大多数页面搬完要几周，大站更久"。

### 3.2.1 三个特殊方向（K）

| 方向 | 差异 | 增量动作 |
|---|---|---|
| 子域→子目录（同一注册域内） | Google 的地址变更文档把"同一站点内移动部分页面"列为不用该工具的情形，只需加重定向和更新 sitemap | 逐 URL 301、新 sitemap、内链全量改写；内链里的绝对 URL 是最大事故源 |
| 子目录→子域或独立域（拆分） | 信号拆散 | 按 [site-networks](site-networks.md) 2.4 的三种正当情形前置审批，配内容重建和独立外链启动计划 |
| 多域收编 | 涉及他人或历史域名 | 每个待收编域先过 2.3；受罚域不直接 301 进主站 |

### 3.3 切流日动作（按序）

1. 低峰期上线新站，DNS TTL 提前降低（≤300 秒是本套件做法，K）。
2. 旧域全站服务器级 301，页对页按映射表，不是全部指向首页。
3. 在 Search Console 验证新旧域，用**地址变更工具**。Google 文档要点（[Change of Address](https://support.google.com/webmasters/answer/9370220?hl=en)，核对 2026-10-21）：
   - 只能用于域名级属性（如 example.com、m.example.com），不能用于路径级属性；不会自动覆盖子域，所有子域变体（含 www 和非 www）都要各自申报。
   - 2026-06-17 起 Google 的[迁站指南](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)把这条写进了正文：换域时，旧域**所有已验证的变体**（含子域、www 和非 www）都要向新域提交地址变更，**即使这些变体没在用**（原文举例：en.example.com、www.example.com、example.com 都迁到 new-example.net）；这些变体都要先在 Search Console 验证（[更新记录](https://developers.google.com/search/updates) 2026-06-17，核对 2026-11-05）。切流前把旧域的变体清单列全，逐个验证、逐个提交。
   - 工具"把旧站的各种信号转给新站，并让 Google 在选规范页时优先新站"，这些动作"在你于 Search Console 发起迁移后持续 180 天"；Search Console 的迁移通知也显示 180 天。
   - 要"保留重定向至少 180 天，如果仍有来自 Google 搜索的访问则更久"；"建议继续为旧域名付费至少一年，以防他人买走并滥用"。180 天后，Google 不再认为新旧站有关系，旧站若仍可抓取则被当作无关站点。
   - 迁移请求可在 180 天内取消。不要连环迁移（A→B 后不能立刻 B→C）。
   - 不适用：http→https（Google 自行识别）、同域内搬路径、www 与非 www 互换、只换主机或 CDN。
4. 新域提交新 sitemap。
5. Bing：Bing 官方博客 2020 年把 Site Move 工具列为迁移步骤之一（[Website Migration with Bing](https://blogs.bing.com/webmaster/2020/12/Website-Migration-with-Bing/)）；该工具现在的入口是否仍在站长平台里，未核，操作前登录 Bing Webmaster Tools 确认。同时 Bing 准则写明永久变更用 301，302 仅用于不到 2 天的短期变更（[Bing 准则](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)）。
6. 更新 hreflang 组内所有绝对 URL（校验见 [hreflang-validation](../technical/hreflang-validation.md)）。
7. 当天抽查首页和重点模板页：200、canonical 指向、GSC 覆盖率错误。

### 3.4 监测窗口与预期

- Google 说波动"几周或更久"，大站更久；没有"首周跌 10–30%"这类官方数字，上一版的数字已删。预期管理用 Google 原话，不给百分比。
- 第 1 周：索引替换（旧 URL 掉出、新 URL 进入）、爬取错误、覆盖率；不追日级排名。
- 到第 180 天：地址变更窗口结束。**旧域继续付费至少一年，重定向尽量长期保持**（Google 原文：一般至少 1 年）。
- 偏离诊断见 [seo-drift-monitoring](../monitoring/seo-drift-monitoring.md)。AI 引用的迁移见第五节。

### 3.5 常见死法（K）

1. 映射表缺行：部分旧 URL 404，或被批量 301 到首页（可能被当 soft 404）。
2. 切流同时改内容或改版：变量叠加，无法归因。
3. 旧域提前弃费：窗口没走完就掉解析。
4. canonical、内链、sitemap 仍指旧域。
5. 忘了非 Google 引擎：Bing、Naver、Yandex、Baidu 各有迁移入口（[markets/ko](../markets/ko.md)、[naver-searchadvisor](../technical/naver-searchadvisor.md)）。
6. 买来的新域带历史处罚：没做 2.3。

### 3.6 迁移后的沟通话术

- 切流前就给预期：Google 说几周或更久，大站更久；超过这个范围没回填再按 [seo-drift-monitoring](../monitoring/seo-drift-monitoring.md) 排障。
- 把直接流量单独列出：换域后直接流量掉而自然流量稳，多半是书签和缓存未刷新（K）。
- AI 引荐流量单独分列，工具见 [ai_referral_log](../../scripts/ai_referral_log.py)（`--classify`、`--attribution` 等参数见其 `--help`）。

## 四、国际域名架构

### 4.1 三种形态

ccTLD、子目录、子域的优缺点对照和"升级 ccTLD 的三个理由"见 [site-networks](site-networks.md) 2.1–2.3，默认结论：**单域子目录加 hreflang 起步，重点市场才用 ccTLD**。本节补域名层的几点：

- Google 多地区文档列出 ccTLD 的缺点包括"只能定位单个国家"（核对 2026-10-21）。
- **Search Console 的国际定位报告已弃用**：2022-08-24 文档更新日志写"移除了对已弃用的国际定位报告的引用"（[更新日志](https://developers.google.com/search/updates)）。上一版"ccTLD 的地理信号不可被 GSC 覆盖（gTLD 可以）"已过时，已删。gTLD 站点想面向某国，Google 文档给的是：本地化 URL、hreflang 或 sitemap，以及本地地址电话、语言货币、本地链接等信号；Google 忽略 geo.position 等位置 meta 标签。
- 不要承诺客户"在 GSC 里设一下国家"。hreflang 配置见 [hreflang-validation](../technical/hreflang-validation.md)，逐市场工作流见 [multilingual-workflow](../overview/multilingual-workflow.md)。

### 4.2 本地域名：五个市场的注册规则与引擎生态

| 市场 | 可核对的事实 | 说明 |
|---|---|---|
| 巴西（.com.br） | registro.br 规则：.br 下的域名对个人（CPF）和企业（CNPJ）开放；外国企业需有在巴西合法设立的代理人（[规则](https://registro.br/dominio/regras/)、[新域注册](https://registro.br/ajuda/registro-de-novos-dominios/)，核对 2026-10-21） | 无本土主体需走代理；策略层见 [markets/pt](../markets/pt.md) |
| 俄语区（.ru） | Yandex 为主要引擎。个人数据本地化（152-ФЗ）是否使 .ru 成为合规选择，上一版有说法但无来源，未核 | 见 [markets/ru](../markets/ru.md) |
| 韩国（.co.kr） | StatCounter 页面浏览口径 Google 略高于 Naver（[读数](../overview/facts.md#search-share)）；来路构成口径 Naver 领先，两种口径见 [markets/ko](../markets/ko.md) | Naver 收录走 Search Advisor；见 [markets/ko](../markets/ko.md) |
| 日本（.co.jp） | co.jp 是属性型 JP 域名，面向在日本登记的企业（经销商说明，[jpdirect](https://jpdirect.jp/domain/register/cojp/)）；一般 .jp 面向在日本有住所的个人和组织（[JPRS](https://jprs.jp/about/jp-dom/spec/)） | 无本土主体用 .com；见 [markets/ja](../markets/ja.md) |
| 中国（.cn、备案） | 备案是中国大陆主机的合规要求；备案对百度收录的具体影响上一版"优先级明显更低"无来源，已删 | 见 [markets/zh](../markets/zh.md) |

通用规律（K）：ccTLD 的价值来自注册门槛带来的实体性、本地用户的信任偏好、本土引擎生态准入，而不是 Google 给 .de 加分。

### 4.3 IDN（国际化域名）

- Google 多地区文档："在 URL 中使用本地化词汇或使用国际化域名（IDN）都可以"，但要用 UTF-8 编码并正确转义；2015 年博客："Google 把 Punycode 版主机名视为与未编码版本等同，不需要分别重定向或设规范"。
- 所以 Google 对 IDN 域名没有惩罚也没有加成。风险在人机两侧的可靠性（K）：邮件系统兼容性、复制粘贴显示成 `xn--`。品牌词含变音时，转写域是更稳的选择（如 buecher.de 类）。
- 套件内市场共识：德语区主域避免 IDN（[markets/de](../markets/de.md)）；波兰新站不建 IDN 域（[markets/pl](../markets/pl.md)）。

## 五、域名与品牌 SERP、AI 引用、邮件信誉

### 5.1 域名是品牌词排名的锚（K）

- 品牌词查询是导航型，官网守住第一靠域名与品牌名一致加实体信号。
- 换域名后品牌词 SERP 会经历"新旧域混排"。Google 一侧用地址变更工具；AI 引擎一侧没有对应工具（见 5.2）。
- 品牌词 SERP 占位结构（诊断时逐行查）：官网、知识面板、社媒档案、百科评测口碑位。观察周期按 4–12 周（K，无官方数字）。
- 品牌词点击是全站最高的查询簇之一，单独设告警，阈值见 [alert-threshold-guide](../monitoring/alert-threshold-guide.md)。

### 5.2 换域后的 AI 引用

- 现状：没有 AI 引擎提供类似地址变更的官方工具。社区报告"最终会切过去，但不即时"（讨论帖，非一手）。
- 证据（套件内存档，不复述）：[markets/ja](../markets/ja.md) 4.1 和 [ai-citation-patterns](../content/ai-citation-patterns.md)。
- 缓解动作（K，按确定度排序）：①品牌名不变只换后缀；②301 加双域并行，让爬虫看到新旧对应；③更新 Wikidata、社媒档案、目录站里的官网字段；④用 [citation_panel](../../scripts/citation_panel.py) 盯新旧域的引用占比。
- **llms.txt 救不了换域**：SE Ranking 对约 300,000 个域名的研究发现，只有 10.13% 有 llms.txt，统计分析与机器学习都没发现它与 AI 引用频率有关系（[SE Ranking](https://seranking.com/blog/llms-txt/)，核对 2026-10-21；研究方是 SE Ranking，不是 Ahrefs）。Ahrefs 另一项研究分析 137K 个使用 Ahrefs Web Analytics 的域名：28% 发布了 llms.txt，其中 97% 的文件在 2026-05 当月没有收到任何请求（[Ahrefs](https://ahrefs.com/blog/llmstxt-study/)）。两项都是第三方观察，不是平台规则。Google 一侧，Search Central 更新日志 2026-06-15 写明 llms.txt 不是 Google 搜索所需，且不会对可见度或排名有正面或负面影响（[更新日志](https://developers.google.com/search/updates)）。套件口径见 [llms-txt-guide](../content/llms-txt-guide.md)。
- 为 AI 引用多注册转载域是负 ROI（推断，K；证据见 [ai-citation-patterns](../content/ai-citation-patterns.md)）。

### 5.3 邮件域信誉

- 邮件发送信誉跟发信域走：换域等于发件信誉清零，冷启动群发会烧坏送达率，伤外链 outreach。迁移后邮件域渐进 warm-up（少量到放量，数周；K），并做 SPF/DKIM/DMARC 对齐。
- 营销邮件用子域（如 news.example.com）隔离，保护根域（K）。
- 上一版"品牌官方域比第三方被引多 11.1 个百分点"没有出处，已删。

## 六、技术细节

### 6.1 www 与裸域

- 排名中性，Google 只看一致性：选定一个规范 host，另一个 301 过去并让 canonical 对齐。Google 地址变更文档也说 www 与非 www 互换用重定向或 canonical，不用地址变更工具。
- 选 www 的技术理由（非 SEO）：www 是子域，可以挂 CNAME（裸域在 DNS 协议层不能），CDN 接入更顺（技术事实）。
- 已上线站点不改 host。
- 双活事故的修复顺序（K）：先统一 canonical，再上 301，最后在 GSC 里确认收敛。

### 6.2 HTTPS

- Google 页面体验文档的自查问题之一是"页面是否以安全方式提供"（[页面体验](https://developers.google.com/search/docs/appearance/page-experience)，核对 2026-10-21），Search Console 有 HTTPS 报告。新域默认全站 HTTPS。上一版"HTTPS 是轻量排名因子（2014 起确认至今）"本次未找到现行官方原文，已删。
- http→https 按迁移流程走；Google 说这类迁移不用地址变更工具。
- 证书 SAN 覆盖规范 host 与遗留变体。
- HSTS 的 preload：[hstspreload.org](https://hstspreload.org/) 写明可以移除，但"变更要数月才能通过 Chrome 更新到达用户，其他浏览器无法保证"，因此加入前评估域名将来是否换手或出售。开启 includeSubDomains 前盘点所有子域证书。

### 6.3 DNS

- DNS 不影响排名本身，影响可达性：长时间或反复 DNS 故障让抓取失败，可在日志里看（[log-analysis](../technical/log-analysis.md)）。
- TTL 平时设 1 小时以上，变更窗口降到 300 秒（K）；多 NS 冗余；把解析可用性写进监测。

### 6.4 注册商迁移与续费

- 转注册商是行政动作，不改 DNS：NS 不动则零停机。事故多出在"顺手换了 DNS 服务商"，换 NS 按迁移项目对待。
- ICANN 转移政策（[Transfer Policy](https://www.icann.org/resources/pages/transfer-policy-2016-06-01-en)，核对 2026-10-21）：注册后 60 天内、转移后 60 天内的域名可被拒绝转移；变更注册人后默认有 60 天转移锁（可在变更前选择不启用）。
- ICANN 的 [EPP 状态码说明](https://www.icann.org/resources/pages/epp-status-codes-2014-06-16-en)：redemptionPeriod 状态持续 30 天，结束后 5 个日历日域名被清除并可重新注册。（各 TLD 可能不同；.br、.cn 等有本地规则，提前查。）
- 续费纪律：主域和所有仍在 301 的旧域开自动续费、多年期、注册商锁定。
- 域名资产台账：≥3 个域时记注册商、到期日、解析位置、用途（在线/301/停放）、证书（K）。

## 七、常见误区与长期 ROI

| 误区 | 事实 | 一句话反驳 |
|---|---|---|
| "EMD 回来了，买词根域躺赢" | 官方：域名里的关键词几乎无影响 | 官方口径没变 |
| "买老域名＝买排名" | 年龄不是因素；买的是档案，档案可能带毒 | 你买的是别人的历史 |
| "高 DA/DR 过期域交易" | Google 2024-03 公告原话：第三方的"信誉/权威"评分与 Google 自己的任何信号都不对应，也不来自 Google | 卖家晒的分是工具厂商的分，不是 Google 的 |
| "过期域 301 堆权重" | 以排名为目的，落在 expired domain abuse 和 link spam 意图内 | 不是灰区，不做 |
| "关键词域比品牌域划算" | 见下表 | 短期省的广告是长期交的税 |

TBPR（工具栏 PageRank）上一版写"2014 年就死了"，没有核实，已删；它与本节结论无关。

**关键词域与品牌域的长期取舍**（K，决策用）：

| 维度 | 关键词域（best-running-shoes.com） | 品牌域（可发音造词） |
|---|---|---|
| 前 6 个月 | 微弱起点优势（推断：锚文本与点击信任） | 冷启动，靠内容与外链 |
| 1–3 年 | 天花板是词根；转型要再买域再迁移 | 无主题约束，实体资产随品牌复利 |
| 品牌词 SERP | 品牌词＝通用词，守不住导航位 | 品牌词独占 |
| AI 引用 | 套件内数据见 [ai-citation-patterns](../content/ai-citation-patterns.md)：AI 记品牌多于记 URL | 品牌域直接受益 |
| 口碑、邮件、直输 | 连字符加关键词显得不专业，直输低 | 口头可传 |
| 转售 | 低 | 品牌资产可随业务出售 |

默认答案：**品牌域**。关键词域仅限 1.2 的残余价值场景且客户确认不做扩张。

**迷思自查三问**：

1. 三年后业务只做这个词根的事吗？答不上来就选品牌域。
2. 这个域的历史你亲手查过 Wayback 和外链档案吗？没有就回第二节。
3. 如果它明天带不来任何排名，你还会买它吗？这是 [site-networks](site-networks.md) 黄金律在域名层的问法。

## 八、检查清单

| 检查什么 | 怎么查 | 通过/失败 |
|---|---|---|
| 候选域的历史 | 2.3 第 1 步 CDX 命令；`curl -s "https://archive.org/wayback/available?url=域名&timestamp=20100101"` 看最近快照 | 全史同主题＝通过；出现药赌贷成人＝红灯 |
| 候选域的黑名单 | Safe Browsing 站点状态页；`dig +short 域名.dbl.spamhaus.org`（Spamhaus 域名黑名单；必须用自己的解析器，公共解析器会返回 127.255.255.x 拒答，不能当"在列"） | 无记录＝通过 |
| 旧域是否还在 301 | `python3 scripts/redirect_chain.py https://旧域/旧路径` | 单跳 301 到对应新页；链长 ≤3 |
| 映射表完整 | 对每条旧 URL：`curl -sI -o /dev/null -w "%{http_code} %{redirect_url}\n" <旧URL>` | 全部 301 且落到一对一页面；不得大量落首页 |
| 新站 sitemap 与规范域一致 | `python3 scripts/sitemap_audit.py https://新域 --must-include https://新域/重点页` | 无坏桶；重点页在列 |
| 新站 head 与 canonical | `python3 scripts/head_check.py https://新域/页面` | canonical 指向新域本页 |
| hreflang 簇 | `python3 scripts/hreflang_cluster.py <各语言版本 URL…>` | 互指完整；不含旧域 |
| 迁移后监测 | `python3 scripts/monitor.py init`，再按 `monitor.py run`、`diff` 做日检（子命令以其 `--help` 为准） | 无新增 noindex、canonical 错误、重定向链 |
| 地址变更窗口 | 在 Search Console 看迁移通知；记日历第 180 天和旧域到期日 | 旧域到期日晚于迁移日 +1 年 |
| 规范 host | `curl -sI http://example.com`、`https://example.com`、`https://www.example.com` 三个都跳到唯一规范 URL | 只有一个 200，其余 301 |

## 九、来源

Google：[SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)、[新 TLD 博客 2015](https://developers.google.com/search/blog/2015/07/googles-handling-of-new-top-level)、[多地区站点](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)、[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies)、[2024-03 公告](https://developers.google.com/search/blog/2024/03/core-update-spam-policies)、[迁移文档](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)、[301 重定向](https://developers.google.com/search/docs/crawling-indexing/301-redirects)、[Change of Address](https://support.google.com/webmasters/answer/9370220?hl=en)、[更新日志](https://developers.google.com/search/updates)；Bing：[准则](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)、[迁移博客 2020](https://blogs.bing.com/webmaster/2020/12/Website-Migration-with-Bing/)；ICANN：Transfer Policy 与 EPP 状态码；hstspreload.org；registro.br；JPRS；StatCounter；SE Ranking 与 Ahrefs 的 llms.txt 研究；John Mueller 言论经 Search Engine Roundtable 与 SEJ 转述（标"转述"）。
