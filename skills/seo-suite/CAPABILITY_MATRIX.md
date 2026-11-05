# Capability Matrix(能力矩阵)

机器可读版:[data/capability-matrix.json](data/capability-matrix.json)(**129 条 = 91 脚本 + 25 模板 + 13 references 主干**;schema_version 1.0)。本文件是人读版,2026-10-12 从 JSON 全量重刷,2026-11-05 补 ga4_api.py、guard_hook.py、ops.py、source_map.py,2026-10-18 增补 question_align.py、ste_lint.py,两者由 [tests/test_capability_matrix.py](tests/test_capability_matrix.py) 守护一致性(改条目先改 JSON,再同步本文件)。

治理出处:[references/research/niubigeo-deep-read.md](references/research/niubigeo-deep-read.md) N10(CAPABILITY_MATRIX 治理格式)。借用其核心思想「**能力=完成**三条件」并按本套件改写:

1. **真实代码存在**——脚本文件在 `scripts/` 落地(不是"计划中");
2. **测试守护存在**——专属测试文件或 `tests/run_tests.py` 内联用例(脚本存在≠能力完成);
3. **合同对勘入表**——数据来源与降级路径已写入 [references/overview/data-source-contract.md](references/overview/data-source-contract.md) 三列并逐一对勘(2026-10-12 已对齐 85)。

与 niubigeo 原版的差异:它的矩阵映射「借来的五个开源项目→本版要求→owner」,本套件的矩阵映射「自有脚本→数据/降级/测试→status」,同样公开承认口径来源(NOTICE 百仓深扫改写)。

## Status 图例

| status | 判据 | 当前数 |
|---|---|---|
| **stable** | 有测试守护(专属测试文件或 run_tests.py 内联用例),或本身即守护工具(self_check/link_check)被检查链每次消费 | 74(37 脚本+24 模板+13 主干) |
| **beta** | 已实装且已入 data-source-contract,但暂无测试守护 | 50(全部为脚本) |
| **draft** | 新增未对勘 | 1(templates/content/trend-jack-playbook.md,规格已定待实装) |

升级路径:新脚本入矩阵默认 **draft** → 合同对勘补行后升 **beta** → 补测试守护(golden 用例)后升 **stable**。

降级模式(与 data-source-contract 全局守则同口径):**①** 等价替代(标 `[est]`)/ **②** 部分执行(显式声明截断或 N/A)/ **③** 停止并指名缺什么 / **④** 静默跳过可选增强。多模式写法「③+②」= 主模式在前。

## 一、审计与页面质量(22)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| site_audit.py | URL --market 市场码(可选) | json | URL 实时抓取(HTML+HTTP 头);--market 阈值读本地 markets.json | ② | test_ai_search_health.py | stable |
| health_score.py | --input audit.json(site_audit --json) | json | 本地 JSON(site_audit --json 输出);--config 可选 | ② | test_health_score.py | stable |
| traffic_funnel.py | --audit audit.json --gsc gsc.csv(可选) --cwv cwv.csv(可选) --urls 清单(可选) | json | --audit(site_audit JSON)+--gsc(GSC 页面导出 CSV)+--cwv(可选 CSV)+--urls(sitemap 清单) | ② | test_traffic_funnel.py | stable |
| quality_rater.py | FILE(纯文本,首行=title 约定) --keyword/--market(可选) | markdown | 纯文本文件(本地;首行=title 约定) | ② | — | beta |
| above_fold.py | URL | markdown | URL 实时抓取(前 700 字符可见文本) | ③ | — | beta |
| trust_signals.py | URL | markdown | URL 实时抓取 | ③ | — | beta |
| core_eeat.py | FILE(纯文本/Markdown) | markdown | 纯文本/Markdown 文件(本地) | ② | — | beta |
| content_score.py | --draft 文件 --competitors c1,c2,c3 --keyword 主词 | json | --draft 本地文件 + --competitors ≥3 个竞品文件 + --keyword;术语表从竞品正文提取 | ③ | test_content_score.py | stable |
| fix_plan.py | --url 或 --audit audit.json --apply/--estimate(可选) | json | --url(内部跑 site_audit 实时抓取)或 --audit JSON | ③ | test_fix_plan.py | stable |
| grounding_page.py | --facts brand.yaml --check(可选,校验已有页) | markdown | brand.yaml(Brand Records 事实库,用户提供) | ③+② | test_grounding_page.py | stable |
| audit_compare.py | --old a.json --new b.json --baseline-gate N(可选) | json | 两次 site_audit --json(本地文件) | ③+② | test_audit_compare.py | stable |
| ci_format.py | audit.json 或 diff JSON --format sarif\|junit\|github | json | 本地 JSON(site_audit --json 或 audit_compare --json diff) | ③ | — | beta |
| sensor_volatility.py | --gsc gsc.csv 或 --positions 三列 CSV | json | --gsc(GSC 多日导出)或 --positions 三列 CSV | ③+② | test_sensor_volatility.py | stable |
| forecast.py | --kws kws.csv --ctr/--actual(可选) | markdown | --kws 关键词 CSV;--ctr 自有 GSC 曲线、--actual 校准流量均可选 | ② | test_forecast.py | stable |
| prioritize.py | --audit audit.json 或 health_score JSON | json | --audit(site_audit JSON)或 health_score JSON;gsc_clicks/inlinks 等扩展键可选 | ② | test_prioritize.py | stable |
| changelog.py | --db monitor.db 或 --snaps JSON(二选一) | json | --db(monitor.py SQLite,读 snapshots 表)或 --snaps JSON,二选一 | ③+② | test_changelog.py | stable |
| doctor.py | (无必填;--net 可选探测) | json | 无外部数据——本地环境探测(Python 版本/文件/环境变量键名) | ② | test_doctor.py | stable |
| ai_views.py | --url 或 --html --apply(可选) | markdown | URL 实时抓取或 --html 离线 | ③ | test_ai_views.py | stable |
| envelope.py | --audit audit.json(必需) --health/--priority(可选) --resume(可选) | json | audit.json(必需)+health/priority(可选) | ② | test_envelope.py | stable |
| benchmark_report.py | --audits dir\|--monitor-db\|--scores(可组合) | json | 多个 audit json/monitor.db/scores.csv | ③ | test_benchmark_report.py | stable |
| site_crawl.py | --domain 目标域(或 --urls 文件) robots.txt/sitemap/首页 HTML(实时) | json | 目标站实时爬取(礼貌:遵守 robots+crawl-delay,默认 1 req/s) | ①+②+③ | test_site_crawl.py | beta |
| field_data.py | --url\|--urls(实时调 PSI/CrUX API) env PSI_API_KEY/CRUX_API_KEY(可选) | json | Google PSI(无 key 低配额)+CrUX(需 key)真实 API | ②+③ | test_field_data.py | beta |

## 二、技术 SEO(7)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| sitemap_audit.py | URL --check-limit(可选) | markdown | sitemap URL 实时抓取(sitemapindex 递归 1 层;逐 loc 抽查状态码/标签) | ③+② | — | beta |
| hreflang_cluster.py | URL...(多个) --max-extra(可选) | markdown | 多个 URL 实时抓取(HTML link 标签+HTTP Link 头+sitemap XML 三载体) | ② | test_hreflang_cluster.py | stable |
| redirect_chain.py | URL | markdown | URL 实时逐跳 GET(手动跟随不自动重定向) | ③ | — | beta |
| robots_posture.py | URL --fix-robots(可选) | json | robots.txt 实时抓取;37 bot 四层名单(search 15/training 11/user 8/other 3,带官方核实标记)+RFC 9309 解析器内置本地 | ③ | test_robots_posture.py | stable |
| llmstxt.py | validate FILE\|check URL\|generate --sitemap | markdown | validate=本地文件;check=线上 /llms.txt 等 4 路径探测;generate=--sitemap 实时抓取 | ③ | run_tests.py(内联) | stable |
| schema_lint.py | URL | markdown | URL 实时抓取(提取全部 ld+json 块) | ③ | — | beta |
| head_check.py | URL\|FILE --market(可选,zh 门控) | markdown | URL 实时抓取或本地 HTML 文件;--market zh 门控中文项 | ③+④ | run_tests.py(内联) | stable |

## 三、关键词与 SERP(8)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| gsc_mining.py | 导出.csv --mode matrix(可选) --decay cur prev(可选) --brand RE(可选) | markdown | GSC 导出 CSV(Query 或 Top queries,Clicks,Impressions,CTR,Position;matrix 模式加 Page) | ③+① | run_tests.py(内联)+test_gsc_mining_fixes.py | stable |
| question_align.py | --gsc 查询×页面 CSV --pages 页面级 CSV(建议) --fetch 或 --html-dir(可选) --page URL(单页导出) | json | GSC 导出 CSV(gsc_api 规范化输出或网页导出);--fetch 实时抓取 title/H1/首段 | ② | test_question_align.py | stable |
| serp_overlap.py | 输入.csv(keyword,top10 URL 分号分隔) | markdown | 输入 CSV(keyword,top10 URL 分号分隔)——SERP 数据须用户提供 | ③ | run_tests.py(内联) | stable |
| keyword_variants.py | stdin 每行一词 | markdown | stdin 每行一词(无输入纯本地归一) | ④ | run_tests.py(内联) | stable |
| payment_intent.py | stdin 每行一个关键词 | markdown | stdin 关键词 + markets.json payment_words 词表(本地) | ④ | run_tests.py(内联) | stable |
| geo_difficulty.py | --kd --ur-median --targeting --position/--client-ur(可选) | markdown | --kd/--ur-median/--targeting 手工输入——KD 来自第三方 SEO 工具导出,UR 来自竞品页审计 | ③+② | — | beta |
| serp_occupancy.py | --market XX 域名列表(argv/stdin) | markdown | --market + 域名列表(argv/stdin);对照 markets.json 内置占位表(tr/th/in/kr/jp/vn/ru) | ③ | — | beta |
| grid_rank.py | rank_data.csv(keyword,grid_point,rank) | json | rank_data.csv(keyword,grid_point,rank)——本地网格排名采集结果 | ② | — | beta |

## 四、多语言实装(8)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| market_lint.py | --market XX FILE | markdown | --market + 本地文本文件;64 条规则读 markets.json(本地) | ③ | run_tests.py(内联) | stable |
| local_format.py | --market de\|fr\|ar\|zh 采样文本(argv/stdin) | markdown | --market + 采样文本(argv/stdin);惯例表读 markets.json | ③ | run_tests.py(内联) | stable |
| ste_lint.py | FILE(文本/Markdown/HTML) --lang 市场码 --glossary 术语表 CSV(可选) | json | 本地文件或 stdin;阈值读 markets.json(sentence_ideal、marketing_words) | ② | test_ste_lint.py | stable |
| text_metrics.py | stdin 文本 --market/--scrub(可选) | markdown | stdin 文本(本地) | ④ | run_tests.py(内联) | stable |
| text_units.py | <market>(en\|zh\|ja\|th\|ko\|ru\|id) stdin 文本 | markdown | <market> + stdin 文本(本地;en/zh/ja/th/ko/ru/id) | ③ | — | beta |
| parity_check.py | --source --target 双语页 | json | 双语对照 QA(长度平价带 markets.json/结构对照/JSON-LD 一致) | ②+③ | test_parity_check.py | beta |
| market_fit.py | --gsc-country GSC 国别导出 CSV(可选,缺省走结构因素) --markets 候选市场 --source-lang 源语言 | json | 市场进入决策(GSC 国别×markets.json→优先级矩阵) | ②+③ | test_market_fit.py | beta |
| market_batch.py | --decl 多市场声明 YAML(site/market/key_pages/domains) --out/--json(可选) | json | 多市场批量编排(声明文件→批量 lint+occupancy→跨市场周报) | ②+③ | test_market_batch.py | beta |

## 五、AI/GEO 测量(6)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| citation_panel.py | init\|record\|report\|diff\|decay\|score panel.json --prompts-file/--stage-mix/--persona-fanout(可选) | json | init 建 prompt 面板(本地);record 录入人工采样的真实引擎回答;report/diff/decay 基于累积 panel.json | ② | test_citation_decay.py | stable |
| fanout_analysis.py | 输入.csv(prompt,web_query) | markdown | 输入 CSV(prompt,web_query)——来自 AI 平台 referral 查询或 fan-out 采集导出 | ③ | — | beta |
| ai_referral_log.py | access.log(stdin/文件) --bot-ua/--attribution(可选) | markdown | server access log(apache/nginx combined 或 JSON 行,stdin/文件) | ③+②+④ | test_ai_referral_tiers.py | stable |
| citation_gaps.py | --panel panel.json --brand-domains a.com | json | --panel(citation_panel 的 panel.json)+--brand-domains | ② | test_citation_gaps.py | stable |
| oracle_check.py | --facts brand.yaml --responses responses.json | json | --facts brand.yaml(已验证品牌事实)+--responses responses.json(真实采样回答) | ③ | test_oracle_check.py | stable |
| cite_domain.py | --input answers.json | markdown | --input answers.json(referring_domains/DR 分布/锚文本等结构化观测,来自外链工具导出+人工观测) | ② | — | beta |

## 六、归因与管道(6)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| did_attribution.py | --pre pre.csv --post post.csv treated/control 页分组 | json | GSC 页面级两期 CSV(--pre/--post:Page,Clicks[,Date])+ treated/control 页分组 | ②+③ | — | beta |
| seo_vs_ads.py | --gsc gsc.csv --ads ads.csv(可选) --competitors(可选) | markdown | --gsc(GSC queries 导出)+--ads(Google Ads search terms 导出,可选)+--competitors 列表(可选) | ② | — | beta |
| yt_outlier.py | videos.csv(title,duration_s,views) | markdown | videos.csv(title,duration_s,views[,is_short][,channel])——YouTube 导出/采集 | ③ | — | beta |
| trend_scout.py | --vertical(可选) | markdown | HN topstories API + Reddit 6 sub hot(免 key 实时抓取);X/Twitter 需 key | ④+②+③ | — | beta |
| freshness.py | DIR(默认 references/) --fail-stale(可选) | markdown | 本地 *.md 头部日期标记(默认 references/) | ④ | — | beta |
| report_build.py | --findings json --out html | markdown | findings.json(前置脚本产出或 agent 组装) | ② | — | beta |

## 七、持续监控守护(3)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| monitor.py | init\|run\|diff\|report --site URL --dir/--dry-run/--budget-minutes(可选) | json | --site URL 实时探测(robots/sitemap/状态码/site: 抽查)+ .seo-monitor/gsc.csv(GSC 导出,有才查)+ SQLite 本地快照 | ④ | test_monitor_noindex.py | stable |
| log_session.py | --log access.log(CLF/combined,- 读 stdin) --ua/--window/--top/--json(可选) | json | 服务器访问日志 access.log(apache/nginx combined 或 CLF;按需工具非常驻) | ③ | test_log_session.py | beta |
| notify.py | run --dir --alerts alerts.json config.json 渠道定义 | markdown | monitor diff 的告警 JSON + config.json 渠道定义(secret 只经环境变量注入) | ④ | test_notify_routing.py | stable |

## 八、工作流与编排(6)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| trend_watch.py | Google News/Reddit rising/HN/微博/百度热搜(实时拉取) --topics 站点主题词表 gate: --angle 观点清单 --exclusive data\|quote\|access(403 源整源跳过;全源失败退出 2) | json | 六信号源实时拉取(Google News/Reddit rising/HN/微博/百度热搜;403 源整源跳过告警;--state 可指工作区) | ②+③ | test_trend_watch.py | beta |
| remediation.py | envelope 的 audit-data.json(init) 两份 site_audit --json(verify) | json | 前置脚本产出(工单不自带数据) | ③ | test_remediation.py | beta |
| project.py | --site URL(init) 子进程调既有脚本(run triage/next/status;编排不重实现) | json | 编排器只编排不重实现;任何步失败续跑其余 | ② | test_project.py | beta |
| ops.py | seo-ops/ 工作区; 外部数据包 seo-ops/raw/external-*.json(可缺); GSC / GA4 服务账号(可缺) | json | 站点 sitemap 与页面(轻检/深审)+ 外部数据包 + GSC/GA4 API + monitor.db | ② | test_ops_agenda.py | beta |
| source_map.py | 站点仓库路径(可指定 --rev); URL 列表; 线上页面(默认抓 title/描述/H1/首段;--no-fetch 关) | json | 线上页面原文 + 站点仓库文件树与 import 关系(只读) | ② | test_source_map.py | stable |
| guard_hook.py | Claude Code PreToolUse 事件(stdin JSON) | json | 当前 git 分支名 + 待改文件路径与内容(只读) | ④ | test_guard_hook.py | stable |

## 九、套件自维护(3)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| self_check.py | (无;扫本地 skill 文件) | markdown | 本地 skill 文件(frontmatter/模板七段式/死链/golden 测试) | ③ | 本身即守护(CI 每次消费) | stable |
| link_check.py | (无;扫本地 markdown 文件树) | markdown | 本地 markdown 文件树 | ③ | 由 self_check 每次消费 | stable |
| intel_check.py | init\|check --source 名(可选) | markdown | intel-sources.md 注册的 18 源实时拉取(RSS/hash)+ .intel-state.json 基线 | ③+② | run_tests.py(内联) | stable |

## 十、数据接入(6)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| gsc_api.py | 服务账号 JSON(--sa/env GSC_SA_FILE/~/.config/seo-suite/gsc.json) | csv | GSC Search Analytics API(真实 OAuth RS256,纯 stdlib RSA) | ③ | test_gsc_api.py | beta |
| backlink_import.py | Ahrefs/Semrush/GSC 外链导出 CSV | csv | BYO 三格式嗅探归一(统一 schema 直喂 cite_domain) | ③ | test_backlink_import.py | beta |
| indexnow.py | --host --key --urls(Bing/Yandex/Naver 端点) | json | IndexNow 协议提交(零 key;Google 不支持) | ②+③ | test_indexnow.py | beta |
| bing_wmt.py | env BING_WMT_KEY(免费,需站点验证) | csv | Bing Webmaster API 薄客户端(状态/提交/QueryStats→gsc 契约 CSV) | ③ | test_bing_wmt.py | beta |
| byo_import.py | Screaming Frog/SERP/关键词表导出 | csv | 第三方导出归一入口(三 kind 自动嗅探) | ③ | test_byo_import.py | beta |
| ga4_api.py | 服务账号 JSON(--sa/env GA4_SA_FILE/GSC_SA_FILE); GA4 媒体资源 ID | json | GA4 Data API runReport(analytics.readonly) | ③ | — | beta |

## 十一、内容运营与 pSEO(6)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| content_queue.py | collect/plan/track/report 三源: trend-state+gsc 导出+serp_overlap 输出(任组合) | json | trend_watch backlog+gsc_mining striking/衰退+serp_overlap 缺口三源合并→contentops.json(ContentOps 六态+遥测) | ②+③ | test_content_queue.py | beta |
| pseo_pattern_mining.py | --gsc GSC queries 导出 CSV(必需) --sitemap/--urls 现有 URL 覆盖度(可选) | json | pSEO 模式挖掘(16 正则+CJK 表/gates §8 打分/GO·WATCH·白空间) | ②+③ | test_pseo_pattern.py | beta |
| pseo_batch_gate.py | --records 批次 JSONL(必需) --rendered 渲染产物目录(可选,词数以此为准) | json | pSEO 批次闸(数据闸/爆炸预警/Simhash 唯一度/样板比/页型地板/STOP·WARN) | ②+③ | test_pseo_batch.py | beta |
| pseo_cohort.py | init 登记并冻结判读标准 ingest --gsc GSC 页面导出(周喂) prune 90 天零展示处置(--backlinks 红线可选) | json | pSEO cohort 索引率追踪(预注册判读冻结+90 天 prune 三选一+as-remediation) | ②+③ | test_pseo_cohort.py | beta |
| prune_gate.py | --funnel traffic_funnel JSON 或 --urls+--gsc(候选源) --crawl crawl.json(入链) --backlinks 外链导出(红线) | json | 退役/合并决策(三查红线:外链/排名词 NO-GO;prune·merge·watch 三态) | ②+③ | test_prune_inventory.py | beta |
| content_inventory.py | --crawl --gsc(必需) --panel --backlinks --keep --words(可选四轴补全) | json | 站点级四轴库存治理(流量/外链/AI 引用/战略→四桶+redirect map;被引页绝不入 remove) | ②+③ | test_prune_inventory.py | beta |

## 十二、内链架构(2)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| link_graph.py | --crawl site_crawl 的 crawl.json --top/--exact-threshold(可选) | json | crawl edges→PageRank/深度直方图/入链清单/锚文本审计(过度优化警告) | ②+③ | test_link_tools.py | beta |
| orphan_fix.py | --crawl site_crawl 的 crawl.json --max 处理上限(默认 50) | json | 孤儿×同目录候选源页→修复清单(hub-spoke 规划输入) | ②+③ | test_link_tools.py | beta |

## 十三、外链与数字 PR(2)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| outreach_tracker.py | add/list/update/due/report(outreach.json) add --source 可吃 citation_gaps --json 候选域 | json | 外展状态库(add 吃 gaps 导入/due 复查提醒/转化漏斗;与 citation_gaps 闭环) | ③ | test_outreach_tracker.py | beta |
| directory_tracker.py | init/add/list/verify/quarterly/export/import(14 列 CSV) verify --entry --target 现场核验 | json | 目录提交执行器(14 列 CSV/现场核验 dofollow/季度复检队列) | ③ | test_directory_tracker.py | beta |

## 十四、归因实验(3)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| split_test.py | plan --pages --baseline-clicks --weeks assign --urls --seed --crossover analyze --treated --control --plan | json | 页面级增量实验(plan 功效计算+预注册冻结/分层随机+crossover/Welch 分析) | ② | test_split_test.py | beta |
| synthetic_control.py | --treated 处理组 CSV --donors donor pool CSV --intervention 干预日 | json | 合成控制 DiD 升级(donor 加权反事实+placebo 检验) | ② | test_synthetic_control.py | beta |
| geo_experiment.py | assign 分国别分组+平衡检查 analyze DiD+分国别异质性 | json | GeoX 薄封装(分国别分组+平衡检查+2×2 交互 OLS;索引级 holdout 诚实边界) | ② | test_geo_experiment.py | beta |

## 十五、垂直场景(3)

| 脚本 | 输入 | 输出 | 数据源 | 降级 | 测试 | status |
|---|---|---|---|---|---|---|
| local_audit.py | --url GBP 页或官网 URL(必需) --name 店名(必需) --addr 地址(必需) --city/--phone(可选) | json | 本地 SEO 体检(NAP/GBP/LocalBusiness schema/本地信号四节) | ② | test_local_audit.py | beta |
| news_sitemap_check.py | --url news sitemap XML 的 URL(具体文件勿传 index) --pub-name 站名(可选,缺省只查站内一致性) --sample noindex 抽查条数(默认 3,0=关闭) | json | news sitemap XML 实时抓取(48h 红线/必填三件套/noindex 抽查/publication name/时间戳精度/robots 声明) | ② | test_news_sitemap_check.py | beta |
| multimodal_report.py | --gsc GSC Performance 导出 CSV(必需) --videos 可选视频清单 CSV(url/video 列) --top/--min-impr/--ctr(可选阈值) | json | GSC Performance 导出 CSV(含 Search Appearance 列则精确口径,否则落地页目录特征代理 [est]) | ② | test_multimodal_report.py | beta |

## 模板层(25;七段式结构由 self_check 守护)

| 目录 | 模板 |
|---|---|
| templates/audit(5) | entity-audit / full-seo-audit / on-page-audit / report-modes / technical-audit |
| templates/research(7) | competitor-analysis-output / competitor-pages-plan / content-gap-output / content-strategy-plan / keyword-research-output / prompt-bank / serp-analysis-output |
| templates/content(4) | ai-use-policy / content-brief / pre-publish-checklist / trend-jack-playbook(draft,规格已定待实装) |
| templates/monitor(9) | ai-visibility-monthly / ai-visibility-weekly / alert-playbook / backlink-report / citation-outreach-brief / forecast-report / performance-report / postmortem / rank-report |

模板不自带数据(data-source-contract 全局守则同样适用):inputs 列写明各自消费的前置脚本产出,逐条见 JSON 的 template 条目。

## references 主干(13)

| 路径 | 角色 | 守护 |
|---|---|---|
| references/content/geo-evidence.md | GEO 证据分级:其他参考文件与它冲突时以它为准 | — |
| references/monitoring/ci-gates.md | CI 质量门手册:site_audit→audit_compare→ci_format→action.yml 三件套命令地图 | — |
| references/monitoring/continuous-operations.md | 持续运营手册:日四问/周趋势/月校准、四级 playbook、防疲劳三律 | — |
| references/overview/capability-map.md | 能力地图(本矩阵人读姊妹篇):市场×能力双维度+六个子系统+10 条任务链 | — |
| references/overview/data-onboarding.md | 静态文档(目标→数据源矩阵+T0-T4 阶梯) | self_check.py |
| references/overview/data-source-contract.md | 数据源合同表:全脚本 数据/降级/反编造 三列——本矩阵 data_source/fallback_mode 的对勘源 | test_capability_matrix.py |
| references/overview/intake-checklists.md | 统一 intake 清单(市场先行+逐市场闸门) | — |
| references/overview/intel-sources.md | 信源监控体系:四层信源+源→模块映射表(与 intel_check.py 同步维护) | — |
| references/overview/multilingual-workflow.md | 18 市场主干(市场总表/工具栈映射/语言规范/检查顺序) | — |
| references/overview/routing-rules.md | 分诊细则(常见请求→能力集合映射) | — |
| references/overview/site-type-playbooks.md | 八张站型卡(SaaS/电商/媒体/本地/文档/工具/Marketplace/YMYL) | — |
| references/research/niubigeo-deep-read.md | niubigeo 深读:N10 CAPABILITY_MATRIX 治理格式即本矩阵的出处 | — |
| references/technical/deprecated-signals.md | 过时信号看门表(带时间戳与一手来源) | test_canonical_facts.py |

## 维护规则(强制)

1. **新增脚本必须同步更新矩阵**:references/overview/script-catalog.md(原 SKILL.md 第 3 节,唯一事实来源;其计数文本 59 落后于文件系统 85,已知漂移)+ data-source-contract.md 补行 + 本文件与 data/capability-matrix.json 各加一条(status 从 draft 起步)。漏更即 `test_capability_matrix.py` ① 变红(双向文件覆盖)。
2. **新增模板必须同步更新矩阵**:templates/ 落盘 + 两处矩阵各加一条。漏更即 ⑤ 变红(25 个数量与磁盘集合校验)。
3. **删除/改名同理**:矩阵与文件系统双向对齐,任何一侧漂移都会红。
4. **status 只升不跳**:draft→beta 需合同对勘行;beta→stable 需测试守护;降级(发现 beta 级问题)须在 PR 里说明原因。
5. **人读版从 JSON 重刷**:改条目先改 data/capability-matrix.json(summary 计数同步),再全量重刷本文件;守护链 `python3 tests/test_capability_matrix.py` 五检(①双向文件覆盖 ②tests_file 存在 ③枚举与计数 ④与 data-source-contract 抽查 10 条粗对齐 ⑤模板 25 个);`scripts/self_check.py` 的 `check_capability_matrix` 消费 ①②,矩阵漂移即 self_check FAIL。

## 已知口径备注

- **gsc_mining** 降级为「脚本侧 ③ + agent 层 ①」双写:脚本本身无 GSC 文件即 usage error,等价替代(serp_overlap 采样、标 `[est]`)是 agent 层策略(data-source-contract 差异第 4 条)。
- **grid_rank** 的 run_tests.py 用例钉的是 references/monitoring/local-grid-ranking.md 的 3×3 算例(ARP/ATRP/SoLV 口径),不 import 脚本本体,故 status 记 beta、tests_file 留空。
- **data-source-contract.md** 2026-10-12 已重生成对齐 85(修复 trend_watch/benchmark_report 行粘连并补齐 29 个新脚本行);SKILL.md 第 3 节计数文本仍写 59(非本波可写范围,已知漂移,以文件系统 85 为准)。
- **2026-10-12 波次治理**:JSON 新条目组名去 `scripts/` 前缀并与合同表节名对齐(工作流与编排/数据接入/内容运营与 pSEO/内链架构/外链与数字 PR/归因实验/垂直场景);垂直三脚本(local_audit/news_sitemap_check/multimodal_report)与泛化占位 inputs(前置脚本 JSON/CSV)已按各自 --help 逐条改写;fallback_mode 与重生成后的合同降级列复核对齐。

