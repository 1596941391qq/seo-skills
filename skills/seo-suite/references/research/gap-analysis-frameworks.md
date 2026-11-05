# 内容缺口分析

## 用途与何时读

回答「下一步该写什么、该补什么」时读：找出目标用户在搜、竞争页面在满足、而你的站点还没满足好的需求，并排出先后。缺口的最终判断标准是**用户需求没被满足**，不是「竞品有、我没有」。

## 先准备数据

| 数据 | 用途 | 说明 |
|---|---|---|
| 你站点的查询与页面表现 | 知道自己已经覆盖什么、表现如何 | Search Console 效果报告导出，需要你自己的账号 |
| 站内内容清单 | 知道有哪些页面、各自对准什么 | 爬虫工具导出或站点地图，逐页标主题和意图 |
| 搜索竞争对手的查询概况 | 找对方覆盖而你没有的查询 | 商业 SEO 工具导出（例如 Ahrefs、Semrush，需要你自己的账号）；数据为估算值，只作相对比较 |
| 目标查询的 SERP 快照 | 判断意图、形式和 SERP 功能 | 你自有或自选的数据源，记录日期、地域、设备；供给缺口的取数和分类见下文「SERP 供给缺口检查」 |

**竞争对手按 SERP 选**：在你的目标查询上反复出现的站点，才是搜索意义上的对手，可能是媒体、社区或工具站，不一定是业务竞品。

## 五类缺口怎么找

1. **关键词缺口**：把你的查询集合和几个对手的集合对比，分出三块：只有对手覆盖的、双方都覆盖但你明显靠后的、谁都没做好但确有需求的（来自客服问题、站内搜索、社区提问）。第一块是补内容，第二块是改内容，第三块是抢先机会。
2. **主题缺口**：按主题而不是单个词看。常见情况有：整个子主题没写；只有一篇浅文，对手有成体系的总览页和深入页；角度或受众不同（对手写企业，你的用户是小团队）；内容已经过时。整理成主题集群的方法见 [topic-cluster-templates.md](topic-cluster-templates.md)。
3. **形式缺口**：SERP 前列要的是工具、模板、对比表、视频或步骤教程，你只有一篇文字文章。判断依据是 SERP 本身，不是对手各类内容的数量。
4. **漏斗缺口**：按认知、考虑、决策、使用几个阶段盘点页面，找出空缺的阶段；再用 GA4（需要你自己的账号）看各阶段页面之后用户去了哪里，找到在哪里流失。流失阈值按站点自己的历史数据定。阶段划分见 [keyword-intent-taxonomy.md](keyword-intent-taxonomy.md)。
5. **SERP 功能缺口**：目标查询上出现的视频、图片、精选摘要、购物或本地结果，你是否具备资格。只把 Google 当前仍在展示的功能算作缺口；FAQ 和 HowTo 富结果已停止展示，不计入。各功能的条件见 [serp-feature-taxonomy.md](serp-feature-taxonomy.md)。

## SERP 供给缺口检查（可执行）

用途：判断一批候选（平台、能力、工具、主题页）里，哪些在搜索结果上**没有人在专门满足**。它回答「值不值得建页」，不回答「有多少人搜」。适用于任务型查询（要调用、要转换、要计算、要抓取）。评测、口碑、「值不值得买」类查询上，论坛占位是意图本身，不算缺口，见 [keyword-intent-taxonomy.md](keyword-intent-taxonomy.md) 的 Discussions and forums 一节。

### 步骤

| 步 | 做什么 | 具体写法 |
|---|---|---|
| 1 候选来源 | 列出候选，再减去已覆盖的 | 来源可选：同类产品的公开目录和分类页、竞争对手站点地图、客服或销售的原话、站内搜索无结果的词、自家 GSC / Bing Webmaster 里已出现但没有专页的查询。减去自家站点地图里已有的页面。写成 `candidates.csv`：`candidate,source,covered`。虚构例子：目录里有 FooVideo、BarShop、BazJobs，自家已上线 BarShop，则候选 = FooVideo、BazJobs |
| 2 每个候选查什么 | 每个候选查 1–2 条查询 | 英文 `<候选> api`；需要时加 `<候选> scraper`。目标市场不是英语时，加该语言的同义词，并设对应的语言和地区参数（例如 `hl=zh-cn`、`gl=cn`）。同一候选的两条查询用同一引擎、同一地区 |
| 3 记录每次取数 | 每次取 SERP 都记下引擎、时间、地区 | 字段：`engine`（引擎或接口名）、`fetched_at`（ISO 时间和时区）、`gl`、`hl`、`device`、`degraded`（是否从主引擎降级到备用引擎）。任一字段缺失，这批 SERP 不进结论 |
| 4 前 10 条逐条分类 | 每条 URL 归入下表七类之一 | 只看前 10 条自然结果，广告和 SERP 功能块不计。分类规则见下表 |
| 5 算供给分 | 供给分 = vendor 条数 + marketplace 条数（0–10） | 用下面的脚本算，输入是第 4 步的分类表 |
| 6 判缺口 | 供给分 ≤ 2，且 official 不能直接满足 | official 能否满足要读它的官方文档确认：有没有公开 API，公开 API 给不给你要的这类数据。记文档 URL 和阅读日期 |
| 7 需求代理，只排序 | 缺口候选之间排先后用 | 搜索框联想词条数、相关搜索里含 `api` / `接口` / `scraper` 的条数、自家 GSC 和 Bing 里该候选相关查询的展示。这些是代理指标，不是搜索量，不跨来源相加，不写进「月搜索量」列 |

### 七类分类规则

| 类别 | 判定 | 例子（虚构） |
|---|---|---|
| official | 候选平台自己的开发者文档或开放平台 | `dev.foovideo.example/docs` |
| vendor | 第三方 API、爬虫或数据服务的产品页，页面主体是「调用 / 购买」 | `scrapers.example/foovideo-api` |
| marketplace | API 或爬虫的市场、商店里的商品页 | `market.example/apis/foovideo` |
| code | 代码托管和包仓库：GitHub、PyPI、npm 等 | `github.com/x/foovideo-client` |
| forum | 论坛、问答、讨论串 | `forum.example/t/123` |
| article | 博客、清单文、新闻、教程文章 | `blog.example/foovideo-data` |
| unrelated | 与该候选的 API 任务无关（同名歧义、泛词结果） | 另一家同名公司的官网 |

拿不准的 URL 打开读首屏再分，不凭域名猜。unrelated 达到 5 条以上，说明查询有歧义，换更具体的查询重查，不直接下结论。

### 供给分和缺口判据（本套件口径）

- 「供给分 ≤ 2」是本套件的起始阈值，没有外部校准。第一批候选跑完后，看供给分的分布，必要时按分布调整，并把调整理由写进报告。
- article 多而 vendor 少，说明有人在教怎么自己做。这是需求旁证，不算供给。
- code 条数不计入供给分；单列一列，作为「开源方案已有」的提示。
- 得分为 `check-official` 的候选，必须读完官方文档再判，不能默认算缺口。

### 可信度

- 每条 SERP 的可信度由取数方式决定：主引擎、地区和时间齐全 = 高；地区或设备缺一项 = 中；`degraded=yes`（搜索接口自动降到备用引擎）= 降一级；两项以上缺失或降级且缺字段 = 低。
- 低可信度的结果不单独支撑「缺口」结论：换主引擎重查，或人工在无痕窗口复查前 10 条。
- 结论里写明「第 N 位（第 1 页）」，不写「排名第一」；决定头号结论的那一条查询，成稿前重跑一次，两次不一致写后者并在括号里记前值。

### 计算脚本

本套件没有现成的取 SERP 脚本，取数用你自己的来源（无痕窗口手查、排名追踪工具导出、有授权的 SERP 接口服务）。不要自己写脚本批量请求 Google 结果页：Google 垃圾政策把「为查排名而抓取结果」列为违规的自动查询（[Machine-generated traffic](https://developers.google.com/search/docs/essentials/spam-policies#machine-generated-traffic)）。分类表保存为 `serp_rows.csv`，列：`candidate,query,rank,url,class,engine,fetched_at,gl,hl,degraded`。

```python
import csv, sys
from collections import defaultdict
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
by = defaultdict(list)                     # (candidate, query) -> 前 10 条
for r in rows:
    if int(r["rank"]) <= 10:
        by[(r["candidate"], r["query"])].append(r)
cands = defaultdict(list)
for (cand, _q), rs in by.items():
    cands[cand].append(rs)
print("candidate,supply,official,unrelated,degraded,flag")
for cand, serps in cands.items():
    n = lambda rs, k: sum(1 for r in rs if r["class"] == k)
    supply = max(n(rs, "vendor") + n(rs, "marketplace") for rs in serps)   # 多条查询取最高，避免假缺口
    official = max(n(rs, "official") for rs in serps)
    unrelated = max(n(rs, "unrelated") for rs in serps)
    degraded = any(r["degraded"] == "yes" for rs in serps for r in rs)
    flag = "gap" if supply <= 2 and official == 0 else ("check-official" if supply <= 2 else "no")
    flag += " (low-confidence)" if degraded else ""
    print(f"{cand},{supply},{official},{unrelated},{'yes' if degraded else 'no'},{flag}")
```

运行：`python3 gap_score.py serp_rows.csv`。同一候选有两条查询时，脚本按查询分别数前 10 条，取供给分最高的一条（宁可漏掉缺口，不制造假缺口）。

两个现有脚本可以配合：`python3 scripts/serp_occupancy.py --market tr "域名1,域名2,…"` 统计某市场 SERP 上论坛、比价、投诉站的占位数（市场码见 `scripts/markets.json`）；`python3 scripts/serp_overlap.py input.csv` 判断两条查询的前 10 条是否重合到应当合并成一页。

### 通过 / 失败

| 检查 | 通过 | 失败 |
|---|---|---|
| 每条 SERP 都有引擎、时间、地区 | 全部齐全 | 缺项的 SERP 不进结论 |
| 前 10 条全部分类，无空白 | 每候选 10 行（结果不足 10 条时按实际条数） | 有未分类行 |
| 缺口候选已读官方文档 | 记了文档 URL 和日期 | 只凭供给分下结论 |
| 低可信度候选 | 已换引擎或人工复查 | 直接列为缺口 |
| 需求代理只用于排序 | 报告里没有「月搜索量」字样引用代理指标 | 把联想词条数当搜索量 |

## 先过滤，再排序

先去掉不值得补的：

- 和你的产品或专长无关。
- 意图你承接不了（例如对方是导航型品牌词）。
- 你拿不出比现有结果更多的价值：没有一手经验、数据或更清楚的解释，只能换个说法重写一遍。
- 需求太小。门槛不设统一搜索量，按细分市场和转化价值校准。

再给剩下的打分。建议从简单的 1–3 分、各因素等权开始，需要偏重时再调权重，并把调整理由写进交付物：

| 因素 | 3 分 | 1 分 |
|---|---|---|
| 需求 | 多个来源都证明有人在找 | 只有工具估算，没有其他佐证 |
| 业务相关 | 直接关联核心产品或服务 | 只是沾边 |
| 可赢性 | SERP 前列里有质量一般的页面 | 前列全是权威站且内容很强 |
| 制作成本 | 现有素材即可完成 | 需要新能力、新数据或外部协作 |
| 转化距离 | 考虑或决策阶段 | 纯认知阶段 |

「快赢」指需求和相关性高、成本和竞争低的缺口，适合先做；分数低但战略上必须覆盖的主题，单独标出理由。

## 交付物

每条缺口至少包含：

| 字段 | 内容 |
|---|---|
| 缺口 | 一句话描述缺什么 |
| 类型 | 关键词 / 主题 / 形式 / 漏斗 / SERP 功能 |
| 证据 | 数据来源、导出日期、对应查询或对手 URL |
| 为什么重要 | 对应的用户需求和业务价值 |
| 建议做法 | 新建、改写现有页或合并，以及建议的页面形式 |
| 优先级 | 分数和理由 |
| 验证方式 | 上线后看什么指标、什么时候复查 |

汇总可用 [content-gap-output.md](../../templates/research/content-gap-output.md)。多个缺口属于同一主题时，合并成一个主题集群来排期，不要逐条各写一篇。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 缺口不是已有页面的蚕食 | 导出 GSC「查询 × 页面」，运行 `python3 scripts/gsc_mining.py matrix.csv --mode matrix`，看同一查询是否已有 ≥2 个页面 | 新建前已排除蚕食；有蚕食的先合并，不新建 |
| 竞争对手按 SERP 选 | 把目标查询前 10 条的 URL 存成列表，`cut -d/ -f3 urls.txt \| sort \| uniq -c \| sort -rn \| head`，反复出现的域才是搜索对手 | 对手名单来自 SERP 频次，不来自业务直觉 |
| 每条缺口有证据和日期 | 交付物「证据」列含数据来源、导出日期、查询或 URL | 缺日期或来源：退回补齐 |
| 打分的权重调整有理由 | 默认 1–3 分等权；改权重时在交付物里写原因 | 无理由改权重：失败 |
| 供给缺口按上节检查 | 跑「SERP 供给缺口检查」的 7 步和通过表 | 通过表全绿才进排期 |

## 上线后验证

依次确认：页面已被编入索引，开始获得目标查询的展示，排名和点击的走势，是否带来了下一步动作。复查时间点按站点自己以往新页面的表现节奏来定，不套固定周数。

## 常见误区

- 把对手覆盖的所有词都当成自己的缺口。
- 把第三方工具的流量和难度估算当成事实。
- 只数页面数量，不看质量和意图是否匹配。
- 照着对手的页面换词重写，没有新增价值。
- 把已停止展示的富结果当作要补的缺口。

## open-seo 缺口工作流深读(open-seo+Ryze 深读,2026-10-09)

> 本节和下一节是来源仓（open-seo、Ryze）的工作流与护栏，2026-10-21 抽查了 open-seo 的 `competitive-landscape`、`seo-audit` 两份 SKILL.md，条目与原文一致。其中的数字（查询集 <10 称 directional、候选 5–10 条、品牌词自然捕获率 50–70% 等）是来源仓的约定，没有外部校准，按「本套件口径」使用。

**市场面 vs 单对手两条线**:多个对手的市场级读法用 competitive-landscape(5-10 条混合意图代表查询→SERP 反复出现的域分组:直品竞品/出版媒体/市场目录/社区论坛/文档资源,**标注域类型,出版者≠产品竞品**→最强 3-5 个域拉概况→缺口表带"谁目前拥有该主题"+少数主题承载大部分需求时配条形图);单对手深钻用 competitor-analysis,其关键词主题六分组可直接当缺口骨架:**产品/品类词、alternatives/comparisons、模板/工具/计算器、教育指南、品牌需求、本地词**;漏洞按"可赢性"排序输出。查询集小(<10)时结论必须自称 directional。

**候选清单纪律(seo-audit 式 opportunities.md)**:排序前写工作清单,5-10 条候选、**至少来自三种不同机会类型**:①现有页低于其所对需求的表现 ②有真实需求无承接页(含产品自己声明里的 feature/framework/use-case 查询)③**要保护的已赢页面**(近顶部排名的页是保护对象不是重写对象)④访问/索引/重定向缺陷在流失访问 ⑤帮现有访客走下一步。每行带:页面|观察到的问题|证据(查询簇+量+位次"第 N 位(第 1 页)"或"前 20 无"+日期)|建议改动|搜索者是谁为何重要|合理收益|工作量|主要不确定。**一条硬规则:如果再做一次查询就能改变某行排序,先做那次查询再排**。每个候选只有两个归宿——进推荐,或进"我们还查了什么"表并带真实理由("等销售要"不是理由;"需求只有头部候选的 1/4 且该页已排第 7"才是);对落选第二名写一句"为什么头名胜它",进报告。

**收益的诚实计法**(seo-audit 第 5 步,防潜力虚报):①点名机制——新排名/现有排名升位/同位更多点击,三者收益完全不同;②**按查询簇计不按精确词计**,变体重叠不加总(变体不是不同的人);③已排名页已吃掉部分量,按总量算情景=高估;④搜索量≠访问量,用明示的点击份额假设,position-one 情景必须标"假设性";⑤当前基线未知时写"总潜在访问"不写"增量访问";⑥绝不发明转化率/收入;无数字时给方向判断及理由("已排第 3,头部空间小")。

**付费词=预算验证过的 SEO 路线图**(Ryze seo-vs-ads,缺口第五数据源):广告搜索词报告×GSC 同窗 join 分四桶——double-paying(自然 ≤3 位仍付费同词,尤其无竞价的品牌词,费用即标题数字)/defensible(自然强但对手在投,付费可能正当)/paid-only winners(广告转化但零自然排名→**内容缺口已被真金白银预验证,最优先补**)/organic-only converters(自然强无广告覆盖→扩量候选)。节省估算=double-paying 花费×保守自然捕获率(品牌词第 1 位取 50-70%,标注为估算)。

**研究与复用纪律**(open-seo 项目上下文模式,适用于任何多轮缺口工作):同主题研究 30 天内做过→复用结果并说明,不重复付费;缺口发现的对手域/关键页**回写项目上下文**(下轮不再重找);竞品品牌词默认不进缺口,除非目标是 vs/alternative 页——那时单列。

## open-seo 深读 2026-10-09b(竞品执行细节/本地缺口/审计取证)

**审计取证四守则(seo-audit 实操层)**:①**先查爬虫是否坏死**——证书错误/5xx/只剩一页时,先查重定向与证书变体并搜公司名;死域名有活后继者时,整份建议翻转成"旧域 301 到新域"。②**页面家族从站点地图定,不从爬虫样本定**(产品/定价/对比/工具模板/指南/品类/服务/地区),每个家族至少读 2 页主内容:表现最好的一页+最差或典型一页;**模板换词检测**:只把名字/地点/关键词填进共享答案的页=家族级缺口信号;对比页与定价页是两个家族、两种购买问题,兄弟页并排读,表现悬殊要查原因,近顶部的兄弟页是保护对象。③**现场核查规范**:SERP 返回的 rank 含所有结果块,要自己数自然结果位次,写"第 N 位(第 1 页)",查前 20;查询失败=未知,不是"前 20 无";**决定头号建议的查询在成稿前重跑一次**,两次不一致写后者、先前值进括号——同日波动不是趋势,一次快照不是基线。④**单项证据一律不独立定案**:单条抽样查询的量、修复容易度、爬虫警告、假设的第一位流量、无实测流失的导航/重定向修理——全进"我们还查了什么"表,不进前三。成稿前给第二审阅者(另一 agent 或全新自审)任务清单:为最强落选行辩护、确认头号建议证据齐全、核对日期/地域/位次写法。

**观察≠因果的表述纪律**(seo-audit 护栏,直接进交付物文案):相似内容+排名不均、爬虫警告、数据源缺行,都证明不了惩罚/排除索引/排名原因;**检索日期≠观测日期**,排名要么写观测时间要么写未知;外链或排名数据缺失="无记录",不是问题;难度和量是输入不是目标(小查询对高价值业务可能重要);报告收尾必须区分"工具报告的"与"自己验证的"。

**单对手分析的执行链(competitor-analysis 增量)**:用户点名的对手先用 SERP 重叠度验证是不是真搜索对手(拿不准时跑关键词集级 overlap 工具,别手工数 SERP);对比自己时**自己的基线用 GSC 第一方数据**(已连接时绝不用第三方估算自己的站);排名关键词行用 maxRank/minSearchVolume/排除品牌词/结果类型四过滤器保持相关;**外链概况只在"权威度看起来解释了排名"时才拉**,拉不到就用 SERP+域名证据继续;页面级/内容形态断言必须有 SERP 或网页证据,**不能只凭关键词行推断**;永远不建议照抄对手内容——建议对同一意图给更强角度或更好答案;拿不到用户自己的域时,明确框定为"仅对手侧"分析。

**市场读法增量(competitive-landscape)**:有关键词集时先跑 overlap 工具再人工数 SERP;自己域名在对比中且 GSC 已连接→用第一方点击/展示/CTR 锚定自己位置;收尾必须是"下一步跑什么"(单对手深钻/聚类/内容简报);**本地市场必须区分自然页赢家与 Maps/本地包赢家**,本地证据用本地工具(商户搜索+本地 SERP),organic SERP 只作补充;外链数据不可用时降级继续,不中断。

**本地缺口框架(local-seo,第六类缺口:本地包/Maps)**:输入=商户名或 cid/placeId(最可靠,**全程用 cid/placeId 匹配,绝用名称匹配**——连锁与同名必撞)+坐标(从商户搜索行推导,歧义才问人)+1-3 条真实顾客词(不是品牌名)。流程:①宽半径一次搜全连锁拿快照(品类/评分/评论数/认领状态/坐标/cid);②目标词在商户坐标附近拉本地 SERP,记下前 3-5 对手与自己那行;③**只和最强 2 家逐项对比**:主品类+附加品类、评论量/新近度/业主回复率、营业时段完整度、照片数、认领状态、**网站链接是否深链到该位置页**(指到首页或旧域=缺陷);④双方拉评论看四指标;⑤**排名网格**:3x3=9 次付费查询,服务区确实宽才 5x5,先花格子钱前确认坐标=实体店面;网格回答"只在店门口排"还是"全服务区都排",每个点的 topResult 点名谁在你不在的地方赢;**某点缺排名要对照该点 resultsCount 读**:满结果集=被挤出局,近空结果集=稀疏 SERP 而非不可见。**优先级铁律:品类与认领问题永远压过发帖节奏**;Q&A 与发帖只在基础项已打平时才查(那时差距是互动不是配置;Q&A 的 API 2025-11-03 已停用,只能在地图上手看,见 [local-grid-ranking.md](../monitoring/local-grid-ranking.md) 第六节)。**多地点经济学**:≤5 家全深钻;>5 家先给全链快照表,让用户挑 1-3 家深钻(默认推荐最密市场里档案最弱的那家)。红线:不建议评论门控/假评论/关键词塞商户名;不从全国性自然指标推断本地包实力。

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。

- 深读来源（R3 组，2026-10-09）：[every-app/open-seo](https://github.com/every-app/open-seo) `.agents/skills/seo-audit/SKILL.md`、`competitive-landscape/SKILL.md`、`competitor-analysis/SKILL.md`、`keyword-research/SKILL.md`（Apache-2.0）；[Ryze-AI-Adgent/open-seo-mcp-skills](https://github.com/Ryze-AI-Adgent/open-seo-mcp-skills) `skills/seo-vs-ads/SKILL.md`、`competitor-gap/SKILL.md`
- 深读来源（2026-10-09b 增补）：[every-app/open-seo](https://github.com/every-app/open-seo) `.agents/skills/seo-audit/SKILL.md`（工作流与护栏全文）、`competitive-landscape/SKILL.md`、`competitor-analysis/SKILL.md`、`local-seo/SKILL.md`（Apache-2.0）
- 思路参考：[aaron-he-zhu/seo-geo-claude-skills · research/content-gap-analysis/references/gap-analysis-frameworks.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/v9.9.12/research/content-gap-analysis/references/gap-analysis-frameworks.md)（Apache-2.0）
- 一手资料：[有用、可靠、以人为本的内容](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)、[Search Console 效果报告](https://support.google.com/webmasters/answer/7576553)、[GA4 事件](https://support.google.com/analytics/answer/9322688)
