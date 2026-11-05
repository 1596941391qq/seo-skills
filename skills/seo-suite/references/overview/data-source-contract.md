# 数据源合同表(全脚本)

> **Agent 调用任何脚本前,先查此表确认数据就绪。缺数据时走"降级"列的既定路径,绝不由模型编造数字或观测。**

本表覆盖 `scripts/` 全部 **91** 个实装脚本(2026-10-12 对勘 85 个;2026-10-21 补 question_align、ste_lint 两行,并按官方文档与脚本 `--help` 重核数据接入类、GSC 类行)。沿革:2026-10-10 首版对勘 52 个;2026-10-11 增至 54+ 并登记 ai_views/envelope/trend_watch/benchmark_report 四行(曾出现 trend_watch 与 benchmark_report 行粘连错位,本轮已修复);2026-10-12 收口波把 R0-R4 建设波次新增的 29 个脚本(数据接入 5/内容运营与 pSEO 6/内链 2/外链 PR 2/归因实验 3/垂直 3/多语言 3/工作流 3/审计 2)全部补齐入表并按 ①-④ 降级模式对勘。每行三列:

- **数据**:输入是什么、从哪来(GSC 导出 CSV / HTML 文件 / server log / URL 实时抓取 / 无输入纯本地)。
- **降级**:数据缺失时的既定动作,四种模式之一:
  - **① 等价替代**——换等价数据源或脚本重建同一问题域,输出必须标 `[est]`;
  - **② 部分执行**——继续跑,但截断/降级到有数据支撑的部分,并显式声明截断或 N/A;
  - **③ 停止并指名缺什么**——报错/警告并列出缺失数据,不产出误导性结果;
  - **④ 静默跳过可选增强**——该数据只影响可选项,核心功能照常。
- **反编造**:哪些数字绝不能估;真实数据 `[real]` vs 估算 `[est]` 的标注规则。

本套件不附带任何数据(见 [data-onboarding.md](data-onboarding.md) 末节「你需要自备什么」,原 SKILL.md 第 4 节):GSC/GA4/Ads 导出、排名追踪与外链工具导出、采样回答、server log 一律由用户自备;外部 API 需用户自己的 Key。跑任何吃数据的脚本前,可先跑 `doctor.py` 探测当前环境的数据凭证分层(T0 纯静态 → T3 GA4)。

---

## 一、审计与页面质量(19)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `site_audit.py` | URL 实时抓取(HTML+HTTP 头);`--market` 阈值读本地 markets.json | ② 抓取异常→CRITICAL fetch 错误;WAF/挑战页→`[SKIP]` fetch guard 拒审,不算 CRITICAL、不进分母 | 只断言实际抓到的静态 HTML 证据;不测渲染,JS 注入内容缺失时不得推断"页面无内容";`--json` 时 stdout 只有一个 JSON 对象(人读行走 stderr);缺 description、缺 H1、相对路径 canonical 记 WARN,不记 CRITICAL(依据 Google 文档:描述可选,标题顺序与数量对搜索无影响,相对 canonical 受支持但建议绝对路径) |
| `health_score.py` | 本地 JSON(site_audit `--json` 输出);`--config` 可选 | ② 缺数据源的类→N/A(`data_source_missing`)不计入合成分;refused/SKIP URL 不进分母、单列 | N/A 类绝不给分;恒带 coverage 注记:分数基于爬取样本,两次分数不可直接比 |
| `traffic_funnel.py` | `--audit`(site_audit JSON)+`--gsc`(GSC 页面导出 CSV)+`--cwv`(可选 CSV)+`--urls`(sitemap 清单) | ② 无 GSC→漏斗截断到 uniqueness 并输出截断声明(in_serps/with_clicks/good_ux=null);缺 CWV→good_ux N/A 不计入;仅 `--urls`→只做可达性抽测 | null 阶段绝不算比例;样本<全站时 coverage_ratio 必须显式输出 |
| `quality_rater.py` | 纯文本文件(本地;首行=title 约定);`--keyword`/`--market` 可选 | ② 无 `--keyword`→按词频自动推断主词(输出注明是推断) | 分数只基于给定文本;纯文本近似,不宣称覆盖视觉/渲染质量 |
| `above_fold.py` | URL 实时抓取(前 700 字符可见文本) | ③ 抓取失败→exit 2,不评分 | "首屏文本"是渲染首屏的保守近似(无布局引擎);输出不得宣称真实渲染布局结论 |
| `trust_signals.py` | URL 实时抓取 | ③ 抓取失败→exit 2 | 四维只认文本证据;静态未检出≠页面没有证言(可能在图片/JS 中),报告须注明口径 |
| `core_eeat.py` | 纯文本/Markdown 文件(本地) | ② 不可机判项(如"≥3 查询变体")固定记 na,离开分母 | na 不稀释分母;不把"未检出"当"不存在";1 项 veto 封顶 60、≥2 项标 BLOCKED,只对显式标记 |
| `content_score.py` | `--draft` 本地文件 + `--competitors` ≥3 个竞品文件 + `--keyword`;术语表从竞品正文提取 | ③ 竞品 <3 个不同来源(按内容哈希去重)→拒绝评分 exit 2(Surfer 官方规则) | 无竞品绝不出分;术语与重要度全部来自竞品语料共现,不引入外部臆测词表 |
| `fix_plan.py` | `--url`(内部跑 site_audit 实时抓取)或 `--audit` JSON;`--git-branch` 落分支+draft PR(R1-10) | ③ 审计失败(fetch guard SKIP)→不生成任何修复物 exit 2 | 修复物只基于审计 findings;content 类只出提纲不自动重写;默认 dry-run,`--apply` 只写隔离目录 ./seo-fixes/ |
| `grounding_page.py` | brand.yaml(Brand Records 事实库,用户提供);`--check` 校验已有页 | ③ 无 facts 文件→无法生成;② facts 缺消歧记录→生成占位注释提示人工填 | 只重组 YAML 内的已验证事实,绝不新增/改写事实;FAQPage JSON-LD 不生成(2026-05 富结果退役) |
| `audit_compare.py` | 两次 site_audit `--json`(本地文件) | ③ 缺任一文件→exit 2;② canonical 等字段两侧皆缺→该字段跳过对比 | 两期 URL 样本不同时必须输出 coverage_ratio,不得直接断言"分数升降" |
| `prioritize.py` | `--audit`(site_audit JSON,逐页)或 health_score JSON(摘要);gsc_clicks/inlinks 等扩展键可选 | ② 摘要输入→条件依赖型规则降级;缺 GSC 上下文→未索引按中优先级并降级标注;canonical 缺 PageRank 数据→标"需人工判定" | 缺数据一律标"需人工判定",不给定论;两栏排序只基于命中的真实 finding |
| `changelog.py` | `--db`(monitor.py SQLite,读 snapshots 表)或 `--snaps` JSON,二选一 | ③ 两者皆缺→exit 2;② 仅 2xx 快照参与 diff(4xx/5xx 页字段不可信) | 只报白名单字段的真实 diff;事件流不含推测;与 gsc_mining `--decay` 联动定位衰退起点 |
| `forecast.py` | `--kws` 关键词 CSV(词+search_volume+position[+cpc]);`--ctr` 自有 GSC 曲线、`--actual` 校准流量均可选 | ② 无 `--ctr`→内置行业默认曲线,全输出标 `[est]`;无 cpc 列→acquisition_value/等效付费成本=N/A;>30 位的词不预测 | **Never invent search volumes**——kws.csv 无量不猜;CTR 模型默认是行业默认曲线 `[est]`(seoClarity 方法建议换自有 GSC 90 天非品牌曲线 `[real]`;各家 CTR 基准差别很大,不当通用基准);orders/value 是情景推演非承诺 |
| `site_crawl.py` | 目标站实时爬取(robots/sitemap/BFS 四级发现链取到即止+子域 DNS/CT 日志探测;默认 1 req/s,robots Crawl-delay 更大时以其为准) | ① `--urls` 手工清单替代发现链;② `--max` 默认 500(上限 5000)超预算警告+截断;ct.sh 失败优雅跳过;③ 输入错 exit 2/全部起点失败 exit 3 | 孤儿判定只对实际抓到的 edges;`--strip-params` 开关两种口径的页数不可直接比较;不抓外链目标,`--check-external` 只抽样 HEAD 验活 |
| `field_data.py` | Google PSI(key 可选,频繁调用建议加)+CrUX API(必须 key,150 次/分钟/项目)真实 API;官方阈值判定(LCP/INP/CLS 等)。PSI 文档写明计划停止返回 CrUX 现场数据,现场 p75 长期以 CrUX 源为准 | ② CrUX 无 key 整源跳过并告警(仅 PSI,不算失败);`--as-cwv-csv` 的 DCL 无现场对应→实验 FCP 近似、无数据留空;③ URL 非 http(s)/私网 SSRF 拒 exit 2;全源失败 exit 3 | 现场 p75 与实验数据分列(field/lab);阈值写死官方口径不引入自评;429/403 提示加 key 不硬跑 |
| `ai_views.py` | URL 实时抓取或 `--html` 离线 | ③ fetch 被拒([SKIP])→停止并说明;无 `--apply` 只预览 | 不承诺引用提升;token 统计是 len//4 估算 `[est]` |
| `envelope.py` | audit.json(必需)+health/priority(可选) | ② 可选源缺失→标 source_missing 继续;格式不符→exit 2 不静默 | 只聚合不改写输入数字;phases 分派是规则映射非承诺 |
| `benchmark_report.py` | 多个 audit json/monitor.db/scores.csv(可组合;每源=一站) | ③ 样本<`--min-sites`(默认 5)→拒绝出报告 exit 2 | 只输出聚合数字,绝不含域名(site 读取后即弃,URL 解析即弃);偏差自白照抄 geo-optimizer 纪律 |

## 二、技术 SEO(7)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `sitemap_audit.py` | sitemap URL 实时抓取(sitemapindex 递归 1 层;逐 loc 抽查状态码/标签) | ③ 入口不可达→报错指名;② `--check-limit` 限定抽查数,结论只覆盖抽查样本 | 六坏桶只报实测状态码/标签;不推测未抽查 URL 的健康;lastmod 伪造只按三判定的显式证据 |
| `hreflang_cluster.py` | 多个 URL 实时抓取(HTML link 标签+HTTP Link 头+sitemap XML 三载体) | ② 未作为入参的 alternate 自动补抓(`--max-extra` 上限,超限标"未验证") | 只判实际抓到的声明;A 指向 B 而 B 不指回 A,Google 忽略这一对,其余互指的照常处理——不是整簇作废([Google 文档](https://developers.google.com/search/docs/specialty/international/localized-versions),页面日期 2026-09-21);语言码按 ISO 639-1(可加 ISO 15924 文字码、ISO 3166-1 区域码),es-419 这类码 Google 不支持 |
| `redirect_chain.py` | URL 实时逐跳 GET(手动跟随不自动重定向) | ③ 网络错误→exit 2 | 只报实测跳数/状态码/参数保留;301 建议来自规则映射,不虚构"权重损失数值" |
| `robots_posture.py` | robots.txt 实时抓取;37 bot 四层名单(search 15/training 11/user 8/other 3,带官方核实标记)+RFC 9309 解析器内置本地 | ③ robots.txt 不可达→报错不判 posture | 四态判定只基于文件内容;通配符 Allow 只拿部分分(两级评分),不夸大为"已放行";`--fix-robots` 只打印不写盘 |
| `llmstxt.py` | validate=本地文件;check=线上 /llms.txt 等 4 路径探测;generate=--sitemap 实时抓取 | ③ check 探测不到→逐路径打 ✗ 与异常名(不猜"平台不支持");generate 抓取失败→exit 非 0 | 生成骨架只含 sitemap 实际 URL,不发明条目;check 发现返回 HTML 而非 Markdown 判 FAIL |
| `schema_lint.py` | URL 实时抓取(提取全部 ld+json 块) | ③ 抓取失败→exit 非 0 | 只对静态 HTML 内的 JSON-LD 断言(@id/悬空引用/占位符);静态未检出≠页面无 schema——渲染后可能注入,需渲染证据复核(SKILL.md 特别约束) |
| `head_check.py` | URL 实时抓取或本地 HTML 文件;`--market zh` 门控中文项 | ③ 抓取失败→exit 2;④ 非 zh 市场且页面无汉字→微信/QQ itemprop 检查跳过(消跨市场噪音) | charset>1024B([WHATWG HTML 标准](https://html.spec.whatwg.org/multipage/semantics.html):字符编码声明元素必须完整出现在文档前 1024 字节内)/弃用 meta 命中只按文档口径断言;微信/QQ 读 itemprop 是平台文档行为,不虚构浏览器实测 |

## 三、关键词与 SERP(8)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `gsc_mining.py` | GSC 导出 CSV(Query,Clicks,Impressions,CTR,Position;matrix 模式加 Page;`--decay` 需当前+前一期两文件) | ③ 脚本侧:无导出文件不可跑;**agent 层等价替代①**:无 GSC 时改用 `serp_overlap.py` 对 SERP 抓取样(逐词 top10 URL)做蚕食/同源判断,结论标 `[est]` | **Never invent search volumes**——clicks/impressions/position 全部来自 CSV,脚本不代查 GSC;期望 CTR 曲线是行业锚点(与 forecast DEFAULT_CTR 同源),低 CTR 判定基于该模型 `[est]`;列名宽容匹配、缺值按 0,调用前自查列齐全(见文末差异) |
| `serp_overlap.py` | 输入 CSV(keyword,top10 URL 分号分隔)——SERP 数据须用户提供(自抓取样或 rank tracker 导出) | ③ 无 CSV→exit 2 | Jaccard 只对给定 URL 集合计算,不虚构 SERP 结果;四档判据(7-10/4-6/2-3/0-1)是解读层,数据必须真实 |
| `keyword_variants.py` | stdin 每行一词(无输入纯本地归一) | ④ 无输入→空输出 | 归组=Unicode 归一链结果;越南有调/无调归组时显式提示"意图不同,排名当独立词跟踪",不合并了事 |
| `payment_intent.py` | stdin 关键词 + markets.json payment_words 词表(本地) | ④ 词未命中→无标签(不是"零商业意图") | 只标词表显式命中(OXXO/cuotas/Pix/COD…);不臆测未命中词的支付意图 |
| `geo_difficulty.py` | `--kd`/`--ur-median`/`--targeting` 手工输入——KD 来自第三方 SEO 工具导出,UR 来自竞品页审计 | ③ 缺必填参数→exit 2;② 无 `--position`/`--client-ur`→只出绝对难度分,不出客户三档 | KD/UR 必须来自真实工具导出,脚本不代查;分数公式透明,输入值须标注来源工具 |
| `serp_occupancy.py` | `--market` + 域名列表(argv/stdin,来自用户 SERP 观测);对照 markets.json 内置占位表(tr/th/in/kr/jp/vn/ru) | ③ 未知市场→exit 并列出可用市场 | 只对提供的域名计数;内置占位表是市场层知识(哪些平台通常霸位),不虚构"某域当前占位"的事实 |
| `grid_rank.py` | rank_data.csv(keyword,grid_point,rank)——本地网格排名采集结果(如 Text Search API 手工导出) | ② rank 留空/null→该格未找到;rank>20→视同未找到并告警(21 惩罚);全未命中→ARP=null 而 ATRP 永不 null;盲区=ATRP−ARP 必同报 | 只算采集到的格点,不补测不外推;复测须同网格同词表同半径,否则不比 |
| `question_align.py` | `--gsc` 查询×页面 CSV(`gsc_api.py query --dimensions query,page` 的规范化输出,或网页导出的 Top queries / Top pages 写法);`--pages` 页面级 CSV(建议给);`--fetch` 实时抓页面 title / H1 / description / 首段,或 `--html-dir` 离线 HTML | ② 无 `--pages`→按查询行估页面展示并提示(查询×页面导出不含匿名查询);无 `--fetch` / `--html-dir`→标 `no_fetch`,只给数据不给词覆盖率;可见查询展示不足页面展示 20%→标 `anonymized`,不判标题缺口;③ 缺 `--gsc` / 列名不认识→exit 2 | 展示、点击、位置只来自 CSV;期望点击按**本站**同排名段 CTR 算,不引用行业 CTR 曲线;词覆盖率是本套件口径,只排序提示,不是 Google 算法;脚本只找页、量差距,不生成文案 |

## 四、多语言(8)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `market_lint.py` | `--market` + 本地文本文件;64 条规则读 markets.json(本地) | ③ 未知市场→exit 并列出 18 个可用市场 | 机检三态 [AUTO-OK]/[AUTO-FAIL]/[MANUAL] 分明;不可机检项以 [MANUAL] 前缀列人工清单,绝不把 MANUAL 当 PASS |
| `local_format.py` | `--market` + 采样文本(argv/stdin);惯例表读 markets.json | ③ 缺 `--market`→exit 2 | 只对给定文本逐条 ✓/✗;电话前缀错配仅提示 ⚠ 不判错 |
| `text_metrics.py` | stdin 文本(本地) | ④ 无输入→空;`--scrub` 输出净化版到 stdout | 水印/slop/AI 节奏是**特征密度**检测,"检出"≠"AI 生成"结论;CJK 词数口径显式声明 |
| `text_units.py` | `<market>` + stdin 文本(本地;en/zh/ja/th/ko/ru/id) | ③ 未知 market→exit 2 | 换算是确定性计算;全角=1/半角=0.5、泰文按字素的口径在输出中显式 |
| `parity_check.py` | 源/目标双语页 HTML(本地文件);长度平价带读 markets.json 语言膨胀口径 | ③ 参数/文件/市场错→exit 2;② 无口径市场→通用带 ±30% 并标 [推断];canonical 离线只比互指 | 长度口径=可见文本非空白字符数(显式声明);跨语言不可逐字比对、按位置对齐列差;hreflang 对存在性仅提示不计退出码 |
| `market_fit.py` | GSC 按 Country 维度导出 CSV(可选)×markets.json 结构因素(引擎格局/文字系/合规注记) | ② 无 GSC 国别数据→全候选等权 0.5 并显著标注"缺数据按结构因素"(不编数字);③ 输入/用法错→exit 2 | 决策支持启发式各因子证据全部打印,不当真值;有数据但国别无记录→0.1 另挂机会注(零足迹≠零机会);合规事实留在 markets.json、脚本只持模式 |
| `market_batch.py` | 多市场声明 YAML(受限子集:site/market/key_pages/domains);URL 由 market_lint 子进程自抓(本脚本零网络) | ② 单市场步骤失败记原因续跑、不拖垮周报(汇总 exit 1);占位表外市场/无 domains→skipped 记原因;③ 声明坏→exit 2 | lint FAIL(critical>0)是有效结果不是执行失败;只聚合子进程真实输出,不代抓不代查 |
| `ste_lint.py` | 文本 / Markdown / HTML 文件或 stdin;`--glossary` 术语表 CSV(可选);阈值读 markets.json(`sentence_ideal`、`marketing_words`) | ④ 无术语表→只做同词多写法的启发式提示;`--lang` 非英语→句长走 STE-LEN-X,单位同 markets.json `sentence_ideal`;③ 输入或参数错→exit 2 | 只做 ASD-STE100 近似检查:STE 批准词典受版权保护,脚本不内置、ASD 也不认证任何工具,报告不写"符合 STE";多词名词和批准词不机检,列 MANUAL;FAIL 才让退出码为 1 |

## 五、GEO 可见性(6)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `citation_panel.py` | init 建 prompt 面板(本地);record 录入**人工采样的真实引擎回答**;report/diff/decay 基于累积 panel.json | ② prompts<10→"样本太小,结论只能当方向";单 prompt 采样 <3 次→不下结论(CI 跨 0.5→unstable);空分母→N/A;decay 观察窗不足→半衰期用 Profound 研究的中位 11 天作参照(厂商研究,不是官方规则;[原文](https://www.tryprofound.com/blog/the-half-life-of-an-ai-citation-is-11-days))并标 `[est]` | **绝不生成"模拟引擎回答"**——面板里的每条回答必须真实采样粘贴;五状态边界分明(failed≠brand_absent:采集失败不是内容缺口);diff 报告 \|Δ\|≥5pp 且配对 n≥10 才下结论 |
| `fanout_analysis.py` | 输入 CSV(prompt,web_query)——来自 AI 平台 referral 查询或 fan-out 采集导出 | ③ 无 CSV→exit 2 | 三桶(added/dropped/preserved)只对给定查询对分词;不虚构 fan-out 序列 |
| `ai_referral_log.py` | server access log(apache/nginx combined 或 JSON 行,stdin/文件) | ③ 无日志→无法运行;② 日志缺 referrer→计入无 referrer 桶并声明;④ `--bot-ua` 先行指标可选 | **下界口径**:App 内打开常不带 referrer,测得值是下界,绝不表述为 AI 引流总量;failure_rate 只按日志内状态码计算 |
| `citation_gaps.py` | `--panel`(citation_panel 的 panel.json)+`--brand-domains` | ② panel 无竞品名单→以"同 cell 共同被引的其他非自有域"代理竞品并标 [推断];failed/no_answer 不入缺口 | 采集失败≠内容缺口;竞品判定是代理推断,报告必须注明;has_competitor_run 是唯一高优先判据 |
| `oracle_check.py` | `--facts` brand.yaml(已验证品牌事实)+`--responses` responses.json(真实采样回答) | ③ 已验证 facts<25 条→警告"样本不足,结论置信低"并继续(置信降级,报告必须带警告);responses 空→警告无可核查;语义级矛盾不由脚本判,交 agent 复核 | 只判显式数字/日期/布尔冲突(正则近似);possible sources 一律留空由 agent 调查后填——不臆造错误来源归因 |
| `cite_domain.py` | `--input` answers.json(referring_domains/DR 分布/锚文本等结构化观测,来自外链工具导出+人工观测) | ② 未观测字段=unknown 不计组内均值;某组全 unknown→该组权重按比例重分配到已知组 | unknown 绝不当 0 分(没观测≠零分);veto BLOCK 只对显式命中(manual_penalty 等) |

## 六、监控与 CI(6)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `monitor.py` | `--site` URL 实时探测(robots/sitemap/状态码/site: 抽查)+ `.seo-monitor/gsc.csv`(GSC 导出,有才查)+ SQLite 本地快照;周检另接 CWV p75(R0-3,field_data)/citation decay(R0-4)/sensor_volatility --context(R0-2)/引荐域月检 | ④ 无 gsc.csv→流量问 skipped 不告警、不猜数;无 PSI key→cwv skipped 不猜;site: 被拦/人机验证→blocked 不告警;DOM 改版解析失败→unparseable 不当真 0;canonical HEAD 失败→连续 3 次才告警;`--budget-minutes` 耗尽→budget_skipped | skipped/blocked 状态绝不转成数字进快照;prev 无数据→下降比例返回 None(不猜);low=自愈只进报告;读不了外链导出不判"外链归零" |
| `notify.py` | monitor diff 的告警 JSON + config.json 渠道定义(secret 只经环境变量注入) | ④ 渠道未配置→跳过并报告;low 级静默只进报告;冷却期重复指纹→suppressed 只进报告;未知/过期 key→提示跳过不判错 | 不投递不存在的告警;明文 secret 被 monitor 拒写,绝不回显值 |
| `sensor_volatility.py` | `--gsc`(GSC 多日导出,列含 Date/Query/Position)或 `--positions` 三列 CSV | ③ 单日数据→exit 2(无法算波动);缺列→exit 2;② 基线 <2 天或 std=0→z30=null;GSC 缺日→与最近可用日比(标 [推断]) | 波动分只来自真实排名序列;公式是自研口径对齐 Semrush 分档(源码注释声明),不冒充官方公式;z30 null 时不标"异常日" |
| `ci_format.py` | 本地 JSON(site_audit `--json` 或 audit_compare `--json` diff) | ③ 输入错误→exit 2 | 格式化不判成败(门禁交给 min-score/baseline-gate);分数透传不重算;helpUri 只在有真实文档 URL 时加;github 注解每 URL 至多 10 行防刷屏 |
| `doctor.py` | 无外部数据——本地环境探测(Python 版本/文件/环境变量**键名**;`--net` 可选 HEAD 探测;`--keys` keys manifest 校验 R2-9) | ② 无任何凭证→T0 纯静态审计可用,missing 列出"配置 X 可解锁 Y";网络探测失败只警告不影响 ready(exit 0=ready/3=需处理) | 只探键名**不读值**,全输出过 redact;报告按 tier 自动声明数据覆盖范围——T0 时绝不暗示能出 GSC/GA4 结论 |
| `log_session.py` | 服务器访问日志(CLF/combined;`--log` 文件或 `-` 读 stdin;按 IP+UA 前缀+时间窗拼会话;`--ua` 默认 Googlebot) | ③ 缺 `--log`/读失败/`--window` 不可解析→exit 4 指名;未捕获异常兜底 exit 3 | 会话指标(入口/深度/命中率)只来自日志内真实行;陷阱特征(param_loop>10/deep_crawl>8/volume>500)按显式阈值断言,不推测爬取意图 |

## 七、工作流与编排(12)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `project.py` | project.yaml 站点实体(站点+市场+站型)+ `<slug>.seo/` history/ 快照;重活全部子进程调既有脚本(site_crawl/site_audit/health_score/prioritize/envelope/remediation/monitor) | ② 单步失败续跑其余并汇总(triage exit 1);③ 输入/用法错 exit 2 | 编排器只编排不重实现;next/status 只报告五阶段状态机的真实产物位置,不虚构阶段完成 |
| `trend_watch.py` | 六信号源实时拉取(Google News/Reddit rising/HN/微博/百度热搜;`--config` vertical_tokens 配**产品垂直**三层词表:品类+品牌+竞品;gate 另需 `--angle`/`--exclusive`) | ② 403 源整源跳过告警;③ 全源失败→exit 2;GO 级信号→exit 1(cron 接 notify) | 判定只报闸门分数不预测流量;时效窗口是 24-72h 经验带;`--state` 可指工作区(R0-7 口径) |
| `remediation.py` | envelope audit-data.json(init)/两份 site_audit `--json`(verify);工单库 remediations.json(原子写+flock) | ③ 输入/结构不符→exit 2;verify 发现新 finding→列"建议 init 增补"清单 exit 1 | verify 只按 audit diff 白名单核销;部分 URL 仍命中→保持 implemented 附 partial 明细;wontfix 必须带 note(接受≠消失,report 单独计数) |
| `did_attribution.py` | GSC 页面级两期 CSV(`--pre`/`--post`:Page,Clicks[,Date])+ treated/control 页分组 | ② 控制页 <3 或控制组 pre 点击 <5→自动回退 site 级对照并注明;③ treated pre 点击 <5→exit 2"基线流量不足以归因";controlBefore≤0→结果 null | DiD 是**观测估计不是因果**——server-side A/B 才是真因果检验,报告必须声明;窗口与[GSC 数据异常期](facts.md#gsc-anomaly)(只影响展示/CTR/位置,点击不受影响)重叠→impressions 不可靠警告 |
| `seo_vs_ads.py` | `--gsc`(GSC queries 导出)+ `--ads`(Google Ads search terms 导出,可选)+ `--competitors` 列表(可选) | ② 缺 Ads 侧→明确列出缺什么,只输出 GSC 侧概览,organic_only 桶不定义、不猜;defensible 桶无 `--competitors`→明说跳过 | 自己的 search terms 报告**看不到竞对竞价**——double_paying 判 HIGH 时注明需 auction insights 复核;省额是 50%~70% 保留率**估算区间**非实测 |
| `yt_outlier.py` | videos.csv(title,duration_s,views[,is_short][,channel])——YouTube 导出/采集 | ③ 文件/格式错误→exit 2 | 离群=组内均值 2×(频道×形态分基线,长短分开);只统计 CSV 内真实播放量,标题词频只对离群标题计算 |
| `trend_scout.py` | HN topstories API + Reddit 6 sub hot(免 key 实时抓取);X/Twitter 需 key | ④ X/Twitter 无 key→明说跳过不猜;② 单源失败→warn 明说;③ 全源失败/无数据→exit 2 | 白名单门槛:HN+Reddit 相关条目合计 ≥15 才建议立项;相关性分只对 `--vertical` 词命中,不硬凑 |
| `freshness.py` | 本地 *.md 头部日期标记(默认 references/) | ④ 文件无日期标记→按新鲜处理,不计 stale | 只读显式日期标记(Updated/verified_at/建于/复核于);不推测文件实际年龄;未来日期=error |
| `report_build.py` | findings.json(前置脚本产出或 agent 组装) | ② summary>2500 字符→截断并警告;findings>20 条→警告"失败报告"并截断到 20 | 只渲染输入 findings,不补写结论;禁 script/外部资源;数字同时印在文字里,不靠图形暗示 |
| `self_check.py` | 本地 skill 文件(frontmatter/模板七段式/死链/golden 测试) | ③ 任一项失败→exit 1 | 工具脚本,无外部数据 |
| `link_check.py` | 本地 markdown 文件树 | ③ 断链→exit 1 | 工具脚本,无外部数据 |
| `intel_check.py` | `SOURCES` 注册的 20 源(见 intel-sources.md)实时拉取(RSS/hash)+ `.intel-state.json` 基线 | ③ 无基线→先 init;② hash 源二次确认:两次拉取不一致(动态页噪音)→按噪音跳过、不动基线;单源失败→明说 | 变更判定需两次拉取一致才算真变更;噪音不报变更;只输出"源变了→该更新哪些文件",不自动改 |

## 八、数据接入(5)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `gsc_api.py` | GSC Search Analytics API 真实拉取(服务账号 RS256 JWT,纯 stdlib 手写 RSA 签名;凭证寻径 `--sa`>`--key`>`GSC_SA_FILE`>`~/.config/seo-suite/gsc.json`;服务账号邮箱要先加为该属性的用户;`--dimensions` 可选 date/hour/query/page/country/device/searchAppearance) | ③ 凭证缺失/坏 PEM/auth 失败/网络/HTTP→exit 1 指名;参数/维度/日期/SSRF 拒→exit 2 | 规范化 CSV 列契约固定(CTR 小数);token 只进内存 50 分钟缓存不落盘;匿名查询 API 不返回(与导出同口径,不补数);限额以官方为准,见[配额表](facts.md#api-quotas)(另有 10 分钟/1 天负载配额) |
| `ga4_api.py` | GA4 Data API runReport(服务账号 RS256 JWT,复用 gsc_api 签名;scope `analytics.readonly`;服务账号要在媒体资源里加「查看者」,项目要开 Analytics Data API;`--property` 或 `GA4_PROPERTY_ID`) | ③ 凭证缺失/读不了→exit 2;API/网络错→exit 1 指名 | AI 引荐优先用 GA4 自带的「AI Assistant」渠道,没有才按来源域名白名单认,输出写明用的哪种口径;不补数、不推断 |
| `ops.py` | seo-ops/ 工作区;站点 sitemap 全量轻检 + 按 GSC 点击前 N 页深审(site_audit);外部数据包 `seo-ops/raw/external-*.json`(seo-ops.external.v1);GSC / GA4 服务账号;monitor.db | ② 每块数据缺了就跳过那一节,在「覆盖」节写明原因;覆盖率不够不出分;③ 工作区缺失、外部数据包格式不对→exit 2;有硬告警 exit 1 | 只读站点、只写 seo-ops/;不改代码、不推送、不部署;没复查到的 URL 不算已解决;每个数写数据源 |
| `source_map.py` | 线上页面的 title / 描述 / H1 / og:title / 正文首段(默认抓,`--no-fetch` 关,`--fetch-base` 换成本地预览);站点仓库文件树(工作树或 `--rev` 指定提交,用 git 读不检出);Next.js App Router 路由文件和 import 闭包;纯静态 html | ② 页面抓不到或原文一条都搜不到→退回路由 + 动态段办法;框架不认识→`unsupported`,不猜;置信度低于门槛→`actionable=false` 只列候选 | 生成物(头部写着自动生成)不当真源,顺着头部注释找生成器;只由 URL 实体词撞上的片段置信度封顶 0.6;只读仓库 |
| `guard_hook.py` | Claude Code PreToolUse 事件(stdin JSON:tool_name / tool_input / cwd);`git symbolic-ref` 取当前分支 | ④ 读不懂事件就放行(退出码 0),不卡住 agent | 只在 main / master 上拦:robots、noindex、canonical、重定向文件或内容的改动 → 退出码 2 + 理由;分支上一律放行 |
| `backlink_import.py` | Ahrefs/Semrush/GSC Links 三格式外链导出 CSV(列头特征自动嗅探;`--format` 显式指定) | ③ 嗅探不出格式/读不了/无有效行→exit 2(数据错误,不猜) | dofollow 列缺失→unknown 不猜(GSC "Text" 只能反推 nofollow);解不出日期的行不计新链;`anchor_exact_ratio` 需 `--brand` 才计,缺省 null |
| `indexnow.py` | IndexNow 协议 POST(Bing/Yandex/Naver 端点;key 文件自部署 `{host}/{key}.txt`;Google 不支持) | ② 单批 >10000 自动分批(IndexNow 每次 POST 至多 10,000 个 URL,[文档](https://www.indexnow.org/documentation));429→提示退避降频;③ 有批次失败→exit 1;用法/SSRF 拒→exit 2 | 只按引擎真实响应码判读(200/202=ok,422=key 未部署或 URL 不属 host,403=key 无效);提交≠收录,不承诺索引时点 |
| `bing_wmt.py` | Bing Webmaster Tools API(免费;key 取法:Bing Webmaster Tools → Settings → API Access → Generate API Key,每用户一个、不分站点,[Microsoft Learn](https://learn.microsoft.com/en-us/bingwebmaster/getting-access);需先验证站点;子命令 urlstatus/submit/stats/pagequery,对应 GetUrlInfo/SubmitUrl/GetQueryStats/GetPageQueryStats) | ③ 凭证缺失/网络/HTTP/API 错→exit 1;用法/SSRF 拒→exit 2;空查询列表≠0≠错(历史不回填,输出声明) | QueryStats CSV 对齐 gsc_mining 契约(CTR 小数;-1 点击哨兵值不用);配额以 GetUrlSubmissionQuota 实读为准不硬编 |
| `byo_import.py` | Screaming Frog internal.csv / SERP top10 表 / kws.csv 三 kind(省略时按表头特征自动嗅探) | ③ 嗅探失败/必需列缺失/未知 kind→exit 2 指名 | 列头容错(NFKC/数字后缀/同义词)只做归一不改值;`--urls-only` 清单原样透传供 site_audit 批量,不发明 URL |

## 九、内容运营与 pSEO(6)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `content_queue.py` | trend_watch backlog(`--trend-state`)/gsc_mining striking·衰退导出/serp_overlap 输出,三源任组合→contentops.json 统一 idea 库 | ② 缺源跳过告警不猜;③ 三源全缺→exit 1(没东西可收);文件在但解析不了→exit 2 不静默降级 | trend/serp 源无量级数据取中性 5(不猜);评分公式(流量潜力×意图系数×时效加成)透明打印;六态状态机跳级/回退拒绝 |
| `pseo_pattern_mining.py` | GSC queries 导出 CSV(必需)+ 现有 URL 清单/sitemap(覆盖度;SSRF 防护) | ③ 缺 `--gsc`→usage 不可跑;② sitemap 抓取失败→覆盖度降级标注 | addressable 量只按 16 正则+CJK 变体表真实聚类;30/25/20/15/10 打分口径=gates §八固定;GO/WATCH/白空间三态有判据 |
| `pseo_batch_gate.py` | 批次 JSONL(每行一条记录)+ 可选渲染产物目录(按 key.html 逐个读) | ② 缺 `--rendered`→按记录 body 计词数并声明;③ 任一 STOP/警告≥100/唯一度 30-40%→exit 1 阻断发布;用法错→exit 2 | 数据闸只剔除记录列清单非 fatal;爆炸预警只算组合空间与记录数差异;Simhash 唯一度/样板比/页型地板阈值写死可配 |
| `pseo_cohort.py` | cohort 登记(init 冻结判读标准)+ 周喂 GSC 页面导出(Page/Clicks/Impressions/Position)+ 可选外链导出(prune 红线) | ② 索引口径=有曝光=已索引 `[est]`(非 URL Inspection,一律带标);③ GSC 缺列→exit 2;FAIL 判定/有处置工单→exit 1 | 预注册纪律:判读标准 init 写死入档、之后冻结(看完数据再挑标准=移动球门禁止);有外链/展示史的页 NO-GO 只标注;410 恒需人工确认 |
| `prune_gate.py` | traffic_funnel JSON 或 URL 清单+GSC 导出(query 级供排名词红线)+crawl.json(入链)+外链导出,四源可组合 | ② 红线证据不全(外链或排名词不可查)/入链缺失→watch(缺证据不下刀);③ 漏斗截断(前置漏斗脚本未带 --gsc)→exit 2 | 外链>0 或排名词(Position≤20)>0→NO-GO 红线绝不退役;page 级 GSC 排名词不可查→watch 不猜;`--window-days` 只注明口径不参与计算 |
| `content_inventory.py` | crawl.json(清点范围)+GSC 导出(流量轴)+panel.json(AI 引用轴)+外链导出(外链轴)+战略页清单,轴数据皆可选 | ② 轴数据缺失→该轴不可用逐条注明,不猜;③ 输入/参数错→exit 2 | 被引页绝不入 remove 桶(硬护栏,输出命中数恒 0);remove 桶恒为候选需人工复核;四轴证据逐页打印 |

## 十、内链架构(2)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `link_graph.py` | site_crawl 的 crawl.json edges[](旧版无 anchor 键按 0 带锚处理) | ② 零入链清单默认排除首页与 sitemap-only 页(大站 sitemap 模式边欠采样防假孤儿);③ 输入坏→exit 2;锚过度优化→exit 1 警告 | PageRank 20 轮/阻尼 0.85/dangling 均摊口径显式;锚审计只对真实锚文本(精确匹配域名>60% 告警) |
| `orphan_fix.py` | crawl.json orphans × 同目录候选源页(与孤儿路径首段相同的已链出活页) | ② 无同目录候选→空缺提示(需导航/hub 级入口),不跨主题硬配;`--max` 默认 50 限处理量;③ 输入坏→exit 2 | 建议锚文本=孤儿 title 品牌分隔符前首段(缺 title 回退路径末段人类化);规划工具,发现孤儿不算失败 |

## 十一、外链与数字 PR(2)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `outreach_tracker.py` | outreach.json 状态库;add 吃 citation_gaps `--json` 候选域(原样取 priority 与 outreach_tip) | ③ 输入/结构不符/同域重复→exit 2;due 复查日到期→exit 1(cron 接 notify) | 无 `--source` 手工登记 priority=Standard 不臆测;转化漏斗只按库内真实状态迁移计算;平均回复天数无样本=N/A |
| `directory_tracker.py` | 目录追踪 CSV(14 列 schema 吃 directory-submissions.md);verify 现场核验(HEAD liveness+GET 查 rel=nofollow;SSRF 拒私网) | ③ init 不覆写既有数据(exit 2);verify 404/410→removed、nofollow/找不到指向目标链接/不可达→exit 1 行不乱动;quarterly 队列非空→exit 1 接 notify | `--dofollow` 缺省 "?"(未知待 verify);DR 用户记账不代查;dofollow 结论只认现场核验的 rel 属性 |

## 十二、归因实验(3)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `split_test.py` | URL 清单(assign 分层随机)+两期 GSC CSV(analyze);基线点击/页数/周数手工输入(plan 功效计算) | ③ 参数/输入错→exit 2;② crossover 两期表按 `--crossover` 自动生成 | 功效=z 法近似、判读=Welch t(口径打印);预注册 plan 写档核验,看完数据换标准禁止;样本=页×周、泊松 var=φ·mean 口径显式 |
| `synthetic_control.py` | 处理组 CSV(Date,Metric)+donor pool CSV(逗号分隔)+干预日 YYYY-MM-DD | ③ 输入缺/读不了→报错;`--self-test` 离线冒烟 | donor 加权反事实+placebo 检验输出置信口径;坐标下降轮数显式;观测估计非因果,不写承诺性增量 |
| `geo_experiment.py` | 分国别流量 CSV(assign 分组+平衡检查;analyze 手写 OLS 2×2 交互 DiD+分国别异质性) | ③ 输入错→exit 2;`--self-test` 冒烟 | 索引级 holdout 诚实边界(Meridian GeoX 思路薄封装不冒充全量 GeoX);异质性只对提供的国别计算 |

## 十三、垂直场景(3)

| 脚本 | 数据 | 降级 | 反编造 |
|---|---|---|---|
| `local_audit.py` | `--url` GBP 页或官网实时抓取+NAP 基准三件(`--name`/`--addr` 必填人工提供;`--phone` 可选) | ③ 页面不可达/输入错→exit 2;② `--city` 缺省从地址形态推断并注明;`--phone` 缺省只报告页内检出 | NAP 一致性只比"用户提供基准 vs 页内检出";套房号变体归一口径显式;LocalBusiness schema 只断言页内实际 JSON-LD |
| `news_sitemap_check.py` | news sitemap XML 实时抓取(具体文件,勿传 index)+引用页 noindex 抽查 | ③ 非 200/不可达/不可解析/传了 index→exit 2;② `--sample` 默认 3 条抽查(0=关闭),结论只覆盖抽查样本 | 48h 窗口红线(Google:news sitemap 只放最近两天发布的文章、单个文件至多 1,000 个 news:news 标签,[文档](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap),页面日期 2025-12-10)只按条目真实时间戳;`--pub-name` 缺省只查站内一致性不猜;publication name/时间戳精度只按 XML 实测 |
| `multimodal_report.py` | GSC Performance 导出 CSV(Page+Clicks+Impressions;含 Search Appearance 列则精确口径)+可选视频清单 CSV(找孤儿视频) | ③ 文件缺/列缺→exit 2;② 无 Search Appearance 列→按落地页目录特征代理,全部数字标 `[est]` | GSC 效果报告有搜索类型过滤器(Web 文本 / Web multimodal / 图片 / 视频 / 新闻;multimodal 自 2026-09-24 起,[帮助页](https://support.google.com/webmasters/answer/7576553));本脚本不读搜索类型维度,只能用目录特征代理,代理口径数字均 `[est]` 明示,有按搜索类型导出的 CSV 时应优先用实测;候选阈值(曝光≥100/CTR≤3%)显式打印;只报接线建议不承诺流量 |

## 全局守则(四条,一切脚本与报告通用)

1. **真实数据优先于估算。** 凡能拿到站点自有数据(GSC 导出、server log、真实采样回答、工具导出),一律先用;行业默认曲线/官方参照常数只在自有数据缺席时顶位,且不覆盖、不冒充实测。
2. **估算必须打 `[est]` 标。** 一切非实测数字——内置 CTR 曲线、半衰期参照值、省额区间、代理竞品口径、pSEO 索引率代理、multimodal 目录代理——在输出中逐个带 `[est]`;关键结论数字可用 `[real]` 明示为实测来源。混标或漏标即违规。
3. **Tool availability can vary;每个脚本声明了自己的 fallback。** 外部工具、导出文件、API 凭据的可用性因环境而异——缺什么看本表"降级列"按 ①②③④ 四模式处理,而不是换个数字继续算。
4. **不拿第三方估算冒充站点自有数据。** 行业基准 KD、默认 CTR、市场占位表、工具 DR 分布是第三方口径;报告里必须与站点实测分列并标注来源,绝不混写为"我们的数据"。

## 发现的差异(文档 vs 实现,以实现为准)

1. **(2026-10-12 重生成;2026-10-21 更新)** trend_watch 与 benchmark_report 行粘连错位已在 10-12 拆开;10-21 补 question_align、ste_lint 两行,头部计数更新为 87,与 `scripts/` 文件系统、data/capability-matrix.json 的 `summary.script` 以及 SKILL.md 第 3 节标题一致。
2. **SKILL.md 第 3 节标题已写 87**(2026-10-21 核对,与本表一致)。仍待改的两处在本表之外:`data/capability-matrix.json` 的 `governance.source_of_truth.scripts` 文字还写"59 落后于 85";SKILL.md 的 intel_check 条目还写"18 源"(现为 20)。
3. **gsc_mining.py 没有"缺列报错"路径**:列名按前缀+大小写宽容匹配,缺值按 0 参与计算——若 CSV 缺 Clicks/Position 列,脚本会静默跑完而非显式失败。调用前须人工确认列齐全(本表数据列已注明必需列)。
4. 任务口径中的"gsc_mining 无 GSC→serp_overlap 替代标 `[est]`"是 **agent 层等价替代策略**(模式①);gsc_mining 脚本本身无内建降级(无文件即 usage error exit 2)。本表按"脚本侧 ③ + agent 层 ①"双写。
5. **oracle_check.py 的 25 条 facts 门槛是"警告置信低并继续输出"**,并非硬停止——按实现写为模式 ③ 的警告变体(执行继续、置信降级、报告必须携带警告原文)。
6. **(2026-10-12 抽查记录)本轮对 11 个新脚本做了源码级降级行为复核**(project/content_queue/pseo_cohort/prune_gate/market_fit/backlink_import/bing_wmt/gsc_api/indexnow/content_inventory/outreach_tracker),退出码语义与"缺数据→跳过/watch/拒绝,不猜"路径与 --help 及专属测试一致,未发现文档与实现不符。

## 外部数据源的官方限额与接入条件(速查,核对 2026-10-21)

| 数据源 | 接入条件 | 限额或口径 | 官方来源(页面日期) |
|---|---|---|---|
| Search Console API · Search Analytics | 服务账号邮箱加为属性用户;启用 Search Console API | 按站点、用户、项目限 QPM/QPD;另有 10 分钟与 1 天的负载配额 | [配额表](facts.md#api-quotas) |
| Search Console API · URL Inspection | 同上 | 按站点、项目限 QPM/QPD,比 Search Analytics 紧 | 同上 |
| CrUX API | Google Cloud API key(为 Chrome UX Report API 开通) | 按项目限速,免费 | [配额表](facts.md#api-quotas) |
| CrUX History API | 同一个 key | 每周一更新;保留 40 周;默认返回 25 个采集期 | [History API](https://developer.chrome.com/docs/crux/history-api)(2025-04-11) |
| PageSpeed Insights API | key 可选;频繁调用建议加 | 文档写明计划停止返回 CrUX 现场数据;限额看 Cloud 控制台配额页 | [PSI 入门](https://developers.google.com/speed/docs/insights/v5/get-started)(2025-08-28) |
| GA4 Data API | GA4 属性 + 授权 | 标准属性:核心 200,000 token/天、40,000 token/小时;Analytics 360:2,000,000 / 400,000;太平洋时间午夜刷新 | [Data API 配额](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)(2026-10-13) |
| Bing Webmaster API | 验证站点;Settings → API Access 生成 key(每用户一个);Microsoft 推荐 OAuth 2.0 | 提交配额以 `GetUrlSubmissionQuota` 实读为准 | [Getting access](https://learn.microsoft.com/en-us/bingwebmaster/getting-access)(2022-10-13) |
| IndexNow | 站点自部署 key 文件 | 单次 POST 上限见[事实表](facts.md#indexnow-batch);各引擎自定每日阈值;参与引擎不含 Google | [文档](https://www.indexnow.org/documentation)、[FAQ](https://www.indexnow.org/faq) |

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败判据 |
|---|---|---|
| 表行数等于脚本数 | 用本节末尾的命令数表行;`ls scripts/*.py \| wc -l`;`python3 tests/test_capability_matrix.py` | 三者一致(当前 91),测试 OK。少一行就补 |
| 表里写的参数真实存在 | `python3 scripts/<名>.py --help`;子命令再跑 `<名>.py <子命令> --help` | 表里每个 `--参数` 都在 help 里。找不到就改表(不改脚本) |
| 降级行为与表一致 | 不给数据直接跑:`python3 scripts/<名>.py`(无参数) | 按表中模式 ③ 打 usage 并以 exit 2 结束,没有 traceback;模式 ② 的脚本给了部分数据后输出里带截断或 N/A 声明 |
| 估算与实测分开标 | 跑 `forecast.py`、`gsc_mining.py` 样例,看输出 | 内置曲线、半衰期参照、省额区间等估算数逐个带 `[est]`;实测数不带 |
| 外部限额没写错 | 对照上一节表里的官方链接重新打开页面 | 数字与页面一致;页面日期比表里新 → 更新表 |
| 官方说法改了 | `python3 scripts/intel_check.py check` | 无 `[CHANGED]`;有就按 [self-update-protocol.md](self-update-protocol.md) 处理 |

数表行的命令(在 `skills/seo-suite/` 下跑):

```sh
python3 -c "import re; print(len(re.findall(r'^[|] .[a-z_0-9]+[.]py', open('references/overview/data-source-contract.md').read(), re.M)))"
```
