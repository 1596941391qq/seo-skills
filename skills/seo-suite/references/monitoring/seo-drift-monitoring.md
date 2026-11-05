# SEO 漂移监控（基线 / 对比 / 历史）

> 建立于 2026-10-09。架构与规则参考 [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)（MIT）`skills/seo-drift/`。按本套件证据约束改写。
> 定位："SEO 的 Git"——先存基线，再定期对比，把静默劣化变成可归因事件。
> 人工操作与排名下滑的处置（人工操作类型 / reconsideration 流程 / 负面 SEO 防御 / 恢复期策略）见 [penalty-recovery](penalty-recovery.md)——归因到 L5「人工操作」分支后转该文件。
> 本套件里没有名为 `baseline` / `compare` / `history` 的脚本（那是 claude-seo 的命令模型）。等价物:`monitor.py run`（存快照 = 基线）、`monitor.py diff`（对比）、`changelog.py --db .seo-monitor/monitor.db`（字段级变更历史）。

## 一、三命令模型

| 命令 | 作用 |
|---|---|
| baseline | 抓取页面并存 13 元素快照 |
| compare | 当前页 vs 最近基线，跑 17 规则 |
| history | 同 URL 全部基线/对比的时间线 |

存储：本地 SQLite（单库，URL 归一化后哈希索引）。

## 二、13 个捕获元素

页面层：title / meta description / canonical / robots 指令 / H1 数组 / H2 数组 / H3 数组 / JSON-LD 数组 / Open Graph 字典（九项来自 HTML 解析）；性能：Core Web Vitals 字典；传输：HTTP 状态码；完整性：html_hash 与 schema_hash（**SHA-256**，分别对正文与 schema 内容）。

URL 归一化：scheme/host 小写、去默认端口 80/443、query 参数排序、去 UTM、去尾斜杠。

## 三、17 条对比规则

> 规则与阈值（相似度 <0.5、CWV 退步 >20%、Lighthouse 分掉 10+）是 claude-seo 的默认值，**本套件口径，不是 Google 的规定**；按本站基线调整。

**CRITICAL（1–8，立即行动）**
1. JSON-LD/Schema 完全消失
2. Canonical URL 变更
3. Canonical 被移除
4. 新增 noindex 指令
5. H1 全部消失
6. H1 文本大改（相似度 <0.5）
7. Title 标签消失
8. 状态码 2xx → 4xx/5xx

**WARNING（9–14）**
9. Title 文本变化
10. Meta description 变化
11. CWV 指标退步 **>20%**（p75 LCP/INP/CLS）
12. Lighthouse 性能分掉 **10+**
13. OG 标签被移除
14. Schema 内容修改（schema_hash 变但 schema 仍在）

**INFO（15–17）**
15. 新增 Schema
16. H2 结构变化
17. 内容哈希变化（html_hash，兜底）

## 四、实施要点

- 4xx/5xx 页仍要捕获（状态码本身是被跟踪的漂移信号），不是跳过
- CWV 抓取失败存 null 并跳过 CWV 规则——**不猜数**
- 抓取走 SSRF 防护（只允许 http(s)、禁内网地址、TLS 恒验证）
- 适用节奏：每次发版后 compare；每周全站 compare；改版前先 baseline

## 五、算法更新归因层(2026-10-09 并入)

**数据源**:Google 官方 [Search Status Dashboard](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history) 的 Ranking 历史是官方来源，只报 Google 确认的事件。第三方传感器（Semrush Sensor、MozCast、Algoroo）做旁证；下面几条来自行业媒体，本次未核一手，仅作线索（未核）:Semrush Sensor 在 2026-09-18 重算过波动基线，历史分不可直接比；RankRanger 已不再独立销售。勿依赖单一传感器，固定面板会漏事件。

> [核对 2026-10-21] 时间线:**Google 2026 年 9 月垃圾内容更新**,官方 Dashboard 记录为 2026-09-24 09:15 开始、2026-10-08 01:00 结束（美国太平洋时间；[事件页](https://status.search.google.com/incidents/XhUDXP7A67iHCD2kmbVu)，发布时说明可能最长两周）。同年还有 2026-06-24（[事件页](https://status.search.google.com/incidents/YUX1peHev5a4fkxLDiUQ)）和 2026-08-18（[事件页](https://status.search.google.com/incidents/LEubPCm2octf2uMqCFKE)）两次垃圾内容更新。2026 年 3 月核心更新的官方起止为 2026-03-27 至 2026-04-08（[事件页](https://status.search.google.com/incidents/7eTbAa2jWdToLkraZj5y)，2026-11-05 用 Dashboard 的 incidents.json 直接核对）。同一来源补全此前漏记的官方事件（美国太平洋时间）：2025 年 12 月核心更新 2025-12-11 至 2025-12-29（[事件页](https://status.search.google.com/incidents/DsirqJ1gpPRgVQeccPRv)）；2026 年 2 月 Discover 更新 2026-02-05 至 2026-02-27（[事件页](https://status.search.google.com/incidents/mYbNTqV1ytDc2fA8hUz4)，只影响 Discover）；2026 年 3 月垃圾内容更新 2026-03-24 至 2026-03-25（[事件页](https://status.search.google.com/incidents/VbnSXAH4SmEcxPtx4YSD)）；2026 年 5 月核心更新 2026-05-21 至 2026-06-02（[事件页](https://status.search.google.com/incidents/wdAXJk6LRRihEjpzEeWE)）。截至 2026-11-05，9 月垃圾内容更新之后没有新的官方事件。**2026-10-15~16 未确认波动**:行业媒体称社区大量反馈流量骤降（[SER 2026-10-16](https://www.seroundtable.com/google-search-ranking-volatility-chatter-42317.html)，第三方，未核）——Dashboard 上没有对应的官方事件时，归因记为 `unconfirmed_volatility`，并先用 Search Console 一方数据交叉。**2026-10-31~11-03 Search Console 点击虚高（第三方报告，Google 未确认）**：部分站点效果报告点击突增到平日数倍、展示持平，API 和网页界面读数不一致，11-04 起陆续回落；从业者推测是 AI 代理或机器人点击（[SER 2026-11-03](https://www.seroundtable.com/google-performance-reports-spike-clicks-42448.html)）。截至 2026-11-05 [数据异常页](https://support.google.com/webmasters/answer/6211453)没有这一条。做环比时把这几天标出来或剔除，不当成真实增长。

**第 0 步:算法更新 rollout 期间变更冻结(Freeze→Pause→Review;行业从业者做法，本套件口径，不是 Google 的要求)**——归因流程启动前先过这一关。确认更新在 rollout 中(Status Dashboard 标 `rolling_out`,或传感器 z30 异常且窗口对齐)时:
- **Freeze**:冻结一切对站点的变更——代码发布、title/meta 改写、批量内容上下线全部暂停。rollout 期间改站=污染归因:事后无法区分波动来自算法还是自家改动,也毁掉 DiD 对照组的事后纯净性;
- **Pause 期间只做带日期快照**:GSC 逐日导出存档(标日期,供窗口对齐),monitor.py 照常 run/diff——监控是存证不是变更。critical 级事故响应(站点 down、robots 误封)**不受冻结约束**:那是救火不是变更,走 [continuous-operations](continuous-operations.md) 告警 playbook(第三节);
- **Review 定损时点**:Google 的官方建议是更新结束后**至少等满一周**再在 Search Console 里分析，并拿这一周与更新开始前一周比较（[核心更新说明](https://developers.google.com/search/updates/core-updates)）。本套件口径取 **10–14 天**，更稳;被冻结的变更解冻后按 [program-management](program-management.md) 的 PRD/ticket 排期执行,不抢跑;
- **对领导层的话术**:"天气预报不是复盘"——day5≠day14。rollout 中与刚结束的读数只能当天气预报汇报("正在波动,窗口关闭后 10–14 天给定损");把中间读数当复盘交结论=宣布一个还没发生的因果。

**归因流程([官方《Debugging drops》](https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops)核对 2026-10-21 + 行业实践)**:
1. 先排除数据假象(GSC data anomalies 页;clicks-only 还是 clicks+impressions 同降);
2. 下降形态:断崖全站→算法/spam/安全;逐年重复波形→季节性（官方做法:Performance 报告日期选最长范围（[保留期](../overview/facts.md#gsc-retention)），并用 Google Trends 对比查询需求）;单页/单模板→技术;缓慢下滑→内容相关性（后两条是本套件经验）;
3. 时间对齐:下降首日 vs 官方更新窗口,**同时对照自家发布日历**——区分技术事故最硬的信号;
4. 类目级传感器旁证;
5. GSC 分层(query/page/device/国家);**impressions 平+clicks 降→不是算法,是 SERP 特性/竞品截流(如 AIO)**;
6. **结论时点**:官方至少 1 周，本套件口径 1–2 周;2026 年 6、8、9 月连续有垃圾内容更新，须先排除上一次更新的余波与更新重叠。

**时间线要点**(完整清单见 status.search.google.com，不预设每年次数):行业媒体称 2026-03-24 至 03-25 有一次不到 20 小时的垃圾内容更新，随后 03-27 开始核心更新（SEJ，第三方）；**2024-08-15 17:15 至 08-20 04:30（太平洋时间）官方记录了一次排名问题（[事件页](https://status.search.google.com/incidents/42XCLGtpuCZkzqe4dc6S)），与 8 月核心更新同期。技术事故和算法更新出现在同一个官方面板——归因必须能区分。**官方[排名系统指南](https://developers.google.com/search/docs/appearance/ranking-systems-guide)把 reviews system 列为现行系统；Dashboard 上不再看到独立的 reviews update，是本套件的观察，不是官方声明。

**algorithm-updates 数据文件最小字段集**(漂移监控自动比对用):
```json
{"id":"2026-03-core","engine":"google","type":"core|spam|reviews|discover|bug_incident|unconfirmed_volatility","start_date":"2026-03-27","end_date":"2026-04-08","status":"complete|rolling_out","official_url":"…","source_tier":"official|vendor|community","scope":"global","impact_notes":"一句话","last_verified":"2026-10-09"}
```
**联动规则**:告警窗口 ∩ 更新窗口非空 → 打「疑似算法」标签而非直接升级;end_date 必填(归因窗口 = end + 7 天，对应官方「至少等满一周」);last_verified 驱动月度复核。**跨市场**（未核，下面是行业说法，使用前对 Yandex、Naver、Bing 各自官方渠道核一遍）:Yandex 有时在官方博客公告更新;Naver 没有官方看板;Bing 没有算法更新公告流。

## 五、与其他参考的联动

漂移规则命中的项直接路由：Schema 变更 → schema 校验参考；CWV 退步 → 性能参考；noindex 新增 → 索引审计；title/meta 变化 → 内容规范。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 有页面级基线 | `python3 scripts/monitor.py init --site https://example.com --key-pages /,/pricing` 后 `monitor.py run --checks weekly`；关键页 title / meta / canonical / og 会存快照 | `.seo-monitor/` 里有 ≥1 次 `status=ok` 的 run |
| 发版后对比 | `monitor.py run` 后 `monitor.py diff --format text` | 无 critical；canonical 变更、noindex 新增、H1 消失、title 消失、状态码 2xx→4xx/5xx 一律升 critical 处理 |
| 查「那天页面改了什么」 | `python3 scripts/changelog.py --db .seo-monitor/monitor.db --from 2026-10-01 --to 2026-10-15 --summary` | 下降日前后有字段变更 = 先查发版；没有 = 转外部因素 |
| 下降是否对齐更新 | 在 [Search Status Dashboard](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history) 记更新起止；更新结束后至少等满一周（官方），本套件取 10–14 天 | 下降首日在窗口内 = 疑似算法；窗口外且有发版 = 先查技术 |
| 「已抓取 - 尚未编入索引」怎么读 | Google 2026-11 改了帮助页：Google 不索引所有网页，这是很多站都会有的常见状态，不一定说明有问题；重要页落在这里才用网址检查工具排查（例如是否误封了爬虫），确认是全站性索引故障再走[索引问题表单](https://support.google.com/webmasters/contact/indexing_issue_form)（[网页索引报告帮助](https://support.google.com/webmasters/answer/7440203)，2026-11-05 核对原文） | 通过：只对重要页排查；失败：把这个状态的总数当成问题数直接报警 |
| 数据是否可比 | 对照[数据异常页](https://support.google.com/webmasters/answer/6211453)；跨[GSC 数据异常期](../overview/facts.md#gsc-anomaly)的展示 / CTR / 排名只比点击 | 跨期未处理 = 结论不可信 |
| 页面改动是否有效 | `python3 scripts/did_attribution.py --help` 看参数；处理组与对照组各自满足最小点击地板（本套件口径：处理组 pre ≥5、对照页 ≥3 个且各 pre ≥5） | 数据不足时 verdict 写 insufficient，不给方向 |
| 第三方排名数据可信 | 与 Search Console 一方数据交叉；Nozzle 等报告的异常期内不单独引用第三方排名 | 只有第三方读数异常 = 标「可能受数据污染」，不下结论 |

## 六、来源

- 13 元素/SQLite DDL/17 规则/归一化规则：[AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) `skills/seo-drift/SKILL.md`、`references/comparison-rules.md`、`scripts/drift_baseline.py`
- 变更冻结协议(Freeze→Pause→Review、rollout 完成后 10–14 天定损、"天气预报不是复盘"话术):SEJ 2026-10(算法更新期 SEO 变更冻结方法论);20 视角调研 R6"运营体系"登记项,调研摘要见 [pipeline-completeness](../overview/pipeline-completeness.md) 第五节,改动治理配套(解冻后排期走 PRD/ticket)见 [program-management](program-management.md)

## 增量:对照组归因与发布回归(百仓扫描批 2/4)

- **对照组归因**(seo-monster rank_attribution):改动页 vs 匹配对照组的前后对比+置信区间——比单纯前后对比强一档;
- **发布回归清单**(notfair seo-drift):基线快照→diff——**redeploy 覆盖了标题/元描述、canonical 或 noindex 翻转、schema 消失、索引页数下降**——每次发版后自动比对(与 13 元素基线互补:那个防漂移,这个防"改版踩坏")。

## 流量诊断五层协议 + DiD 参数(rampstack/seo-monster 精读,百仓深扫)

**五层根因顺序**:L1 确认变化真实(tracking 断档/bot/口径/季节性,**要 YoY 不要 MoM**;GSC clicks 与 analytics sessions 同向波动 within 10-20%,显著背离=tracking 问题)→ L2 定位(国家/设备/区块/品牌 vs 非品牌/落地页)→ L3 页面级 → L4 技术(**"Recent deploys are the prime suspect"**)→ L5 外部(算法/竞品/需求/处罚)。
**L2 模式表**:单国跌=本地算法或 hreflang;仅移动跌=移动可用性;品牌词跌=品牌级问题(宕机/声誉/处罚);非品牌跌=算法;单页跌=页面级;全站跌=惩罚/技术/迁移/算法。
**L3 判读**:位置跌+SERP 不变=质量/新鲜度;**位置稳+CTR 跌=SERP 特性变化(AIO/广告)——页面可以不掉排名而掉流量**;去索引=技术;同日 deploy+drop=强相关非证明,要找机制。
**九条失败模式**(照抄要点):跳到算法归因是懒惰答案;无正常基线则一切波动皆警报;**品牌 vs 非品牌由不同团队负责**;四源并用(GSC+Ahrefs+analytics+日志)单源诊断禁止;不许提前安抚"算法会恢复"。
**假设单句模板**:"[Property] lost [magnitude] starting [date] because [cause], evidenced by [data], recovery requires [actions], timeline [duration]"。
**DiD 对照参数**(seo-monster):pre=56 天(≥2× post)/post=28/gap=7 天 washout;闸门=控制页≥3、treated pre 点击≥5、控制页 pre 点击≥5;lift CI(±1.96 SE)三态判定;**第三方排名追踪不可靠期(第三方报告，Google 未在本次检索中官方确认)**:排名追踪公司 Nozzle 的研究（[Poisoned Google SERPs](https://nozzle.io/research/poisoned-google-serps/)，2026-10-10 发布、10-19 更新）称，2026-09-13 之后的 2,700 万个已判定 SERP 中平均 8.4% 是「被调包」的页面（页面正常，但结果换了），9-29 达到峰值 28.6%，10-14 后降到每天 3% 至 7%；多数在三天内恢复。[SER 2026-10-12](https://www.seroundtable.com/third-party-google-rank-tracking-broken-42272.html) 转述了同样的三类现象（大范围封 IP、验证码增多、可疑 SERP 数据异常）。**归因纪律:第三方排名工具的异常读数在排除自家问题前,先怀疑数据被污染(交叉 GSC 一方数据核对);本套件 monitor 的 SERP 源(bing/ddg)不受直接影响,但引用任何第三方排名数据时须标注 [est·可能受 poisoned SERPs 影响]**;GSC 断代检测:Google 官方记录过一段展示 / CTR / 平均排名记录有误的时间（[GSC 数据异常期](../overview/facts.md#gsc-anomaly)），点击不受影响;窗口重叠时 clicks 为唯一可信指标。Google 在 2025 年移除 `num=100` 参数一事来自行业媒体报道（[SER](https://www.seroundtable.com/google-search-drops-100-results-parameter-40097.html)），不是 Google 官方公告，日期本次未核。**报告延迟事件:行业媒体称 2026-10-11 Search Console 效果报告延迟超 64 小时（[SER](https://www.seroundtable.com/google-search-console-performance-report-delayed-42271.html)，第三方，未核）——监控告警归因前先查报告新鲜度（报告页的「最后更新」日期），延迟期内不要把数据缺口当流量下跌**;**"server-side page-level split test 是唯一真因果检验"**。
**告警矩阵默认值**(crawlseo 的源码默认值，**本套件口径，不是 Google 规定**):TRAFFIC_DROP 7 天点击 ≤−20%(当期≥5);POSITION_CHANGE 28 天均位恶化 ≥2 位;CRAWL_ISSUES 健康分 <70;VITALS 最近 5 份报告 ≥2 份 LCP 或 CLS 超出 web.dev「良好」档（[阈值表](../overview/facts.md#cwv)）;健康分=100−8×CRITICAL−3×WARNING−1×INFO（crawlseo 自定义公式）。

## 诊断清单细化 + 回归四件套 + DiD 实现细节(rampstack/iannuttall/seo-monster 源码深读,2026-10-09)

### 五层协议的 checklist 级细化(rampstack seo-traffic-diagnosis/references/diagnosis-checklist.md)

**L1 拉动清单**（以下症状表和阈值是 rampstack 的从业者清单，本套件口径；「同向 ±10–20%」同属经验阈值）:GSC clicks 与 impressions(近 90 天逐日)+analytics 同窗 organic sessions+YoY 同期+可过滤时的 bot 流量。校验项:日期口径对齐;窗口内无 analytics 停摆;**窗口内无 tag manager 发布**;GSC clicks 与 sessions 同向(±10–20% 内);YoY 同形态→季节性而非异常;无节假日/行业事件解释。

**L4 技术回归症状表**(症状→可能原因):

| 症状 | 可能原因 |
|---|---|
| 部署后全站骤降 | robots.txt 全封 / 误加 sitewide noindex / 路由断裂 |
| 页面 404/410 | URL 结构变更、缺重定向 |
| 页面 5xx | 服务器/托管故障,可能 CDN 配错 |
| Render mismatch | JS 渲染对爬虫失效(框架升级后高发) |
| hreflang 断裂 | 跨国流量掉但其他市场位移 |
| 批量 canonical 变更 | 改版后 canonical 指向错误 URL |

L4 校验项补:重定向须 1 跳且 301;受影响 URL 无 4xx/5xx 尖峰;sitemap 含受影响 URL 且新鲜;hreflang 互指且指向活 URL;Googlebot 抓取率正常(服务器日志);**逐条比对 deploy 日期与流量下降日期**。

**L5 三判读**(L1–L4 全净时):下降落在已知更新日→大概率算法性,审计内容质量与 E-E-A-T,恢复常需等下一个更新周期;掉位且有新强势域名进 SERP→竞争位移,审计对方内容并更新自己;全行业搜索需求下滑→非己方问题,管理预期。

**诊断不清时的 4 步**(不强行下结论):列 top 2 假设各附证据→推荐对两者都有效的最低风险动作→指出能区分两个假设的数据→提出采集该数据的监控计划。"Stakeholders prefer honest uncertainty to confident-but-wrong."

**交付模板**:What happened 1 句 / Why 1 句 / What we're doing 3–5 条 / When to expect recovery+置信度 / What to watch for(恢复或恶化的前导指标)。诊断正文 7 段:Summary、Symptom、逐层发现、根因假设、行动计划、恢复预期、监控计划;4–10 页。

### 回归四件套(iannuttall/seo technical-watch 源码,一次编排并行跑)

| 组件 | 口径 |
|---|---|
| crawl-diff | BFS 抓取→与上一 run 快照 diff,**7 字段**:status/title/meta_description/canonical/h1/indexable/contentHash;变更分 added/changed/removed 三类;**newErrors=after≥400 且 before<200**;indexabilityFlips 单列;快照入库供下次对比 |
| index-watch | URL Inspection 逐 URL:单次 ≤100 个（iannuttall 工具设定）、dailyLimit 设为官方每站点每日上限（[配额表](../overview/facts.md#api-quotas)）;每 URL 保留最近 20 次尝试(拿到成功后修剪);**quota 被限或属性错误后,剩余 URL 全部标 deferred、不再发请求**;产出 changed/regressions/recoveries/alerts 四分类 |
| index-monitor | sitemap 驱动的同能力(有 sitemap 时替代逐 URL) |
| link-recover | 找有搜索价值(点击/展示下限可配)的可恢复 URL |

**编排纪律**:findingCount = crawl 高优先建议 + index currentIssues + recovery high/medium;failed+quotaBlocked+deferred 计为「未完成检查」而**不算缺陷**——"Do not treat incomplete checks as SEO defects"。index-watch 固定四条 caveats:URL Inspection API 报的是 Google 已索引版本、不能测 live URL（[官方](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)）;PASS / NEUTRAL / FAIL 官方对应 Search Console 里的 Valid / Excluded / Error;excluded 或 canonical 差异可能是有意的(复核而非默认缺陷);本地配额账本(保守 UTC 日上限)看不到其他机器/客户端对 URL Inspection 的调用。

### DiD 实现细节(seo-monster rank_attribution + iannuttall measure-change 互补)

- **控制组构造**:默认 section(URL 首路径段)池;section 池 <3 页自动回退 site-wide 并注记;控制页 pre 点击 ≥5 才入池。
- **公式**:peer_trend_ratio = mean(各控制页 post/pre 点击比);counterfactual = treated_pre × ratio;lift = treated_post − counterfactual;CI 由 ratio 的 ±1.96 SE 推出 lift_lo/lift_hi。
- **判定五态**:lift_lo>0→likely_positive;lift_hi<0→likely_negative;跨零→inconclusive;**treated pre<5→insufficient_data;控制页<3→insufficient_control——数据不足本身就是一种 verdict,不许硬给方向**。
- **confounders 块**(每次必返):data_regime_breaks(GSC 展示记录错误（官方，[GSC 数据异常期](../overview/facts.md#gsc-anomaly)）、num=100 参数移除（行业媒体报道，日期未核）,窗口重叠即检出)→position_reliable 标志;parallel_trends_assumption;algo_update_note——"查 Search Status Dashboard change_date 前后 ~2 周的 core/spam 更新;DiD 经控制组吸收全站性更新,吸收不了页面类型特定的更新"。
- **iannuttall 变体**(equal-finalized-calendar-windows-v1):前后等长 finalized 日历窗(GSC 日数据按太平洋时间 PT，[官方](https://support.google.com/webmasters/answer/17011259)),可选 controlScope/controlTarget;adjusted delta = control-ratio counterfactual;**置信度纪律:GSC 证据 partial→confidence 降一档;每窗 finalized 天 <7 或 after 窗被截→verdict=not-enough-data,不给方向**;caveats:position 是 impression-weighted;query 匿名化缺行≠零流量。

## 操作参数与规则边界增量(claude-seo 深读 2026-10-09b)

- **Rule 1 的弃用类型豁免**:schema 全消失时,仍受支持的类型(Product/Review/LocalBusiness 等)按"富结果将快速掉出 SERP"处理;**已停展类型(FAQ/HowTo 等)的消失不算富结果损失**,降级记录——避免把清理死标记误报成 CRITICAL。
- **操作参数集**:baseline 可 `--skip-cwv`(无 API key 场景);compare 可 `--baseline-id N` 指定历史基线,**默认取最近一条**;history 支持 `--limit`;compare 完成后可把 JSON 结果喂报告器生成 HTML 漂移报告(人读交付物)。
- **错误路径纪律**:无基线→提示先跑 baseline,不硬比;URL 不可达→报 fetch 错误,**不猜页面状态**;SSRF 拦截(私网 IP)→绝不绕过;SQLite 库不存在→首次使用自动建库(非错误);存储层查询一律参数化占位符,不做字符串拼接。
- **交叉路由补全**(在现有四条之外):canonical 变更/移除→索引与规范化审计;状态码 2xx→4xx/5xx→技术诊断;OG 标签移除→社交分享分析;H1 结构变化→内容与 E-E-A-T 复核。
- **CWV 采集失败的处理**:CWV 字段存 null 且比较时跳过 CWV 规则——缺数据跳过规则,而不是拿旧值顶替。
