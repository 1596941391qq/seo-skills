# 脚本目录(87 个实装脚本)

> 2026-10-21 从 SKILL.md 第 3 节原样搬来。SKILL.md 只留路由表,脚本逐条说明以本文件为准;脚本计数以 `scripts/` 文件系统和 `data/capability-matrix.json` 为准。每个脚本的数据来源与降级见 [data-source-contract.md](data-source-contract.md)。

## 3. 可执行层(87 个实装脚本,AI 直接调用;全部 stdlib 零依赖)
规则已变代码——**对应任务先跑脚本拿事实,再按能力文件解读**。markets.json 是 18 市场规则数据层(多语言脚本共读)。新增脚本必须登记 `data/capability-matrix.json`(`tests/test_capability_matrix.py` 五检守护,self_check 消费其中①②),人读版 CAPABILITY_MATRIX.md 与合同表同步:

**审计与页面质量**
- `field_data.py --url U [--strategy mobile] [--as-cwv-csv out.csv]`:CWV 现场数据真实 API 客户端——PSI(无 key 低配额)现场 p75 vs 实验数据分开呈现+CrUX(需 key)双源;官方阈值判定;--as-cwv-csv 直喂 traffic_funnel 的 good_ux 阶段
- `doctor.py --wizard [--want cwv,rank,...]`:数据接入向导——逐项列需要的数据源/当前已配否/获取方式/降级路径(配 references/overview/data-onboarding.md)
- `site_crawl.py example.com`:**全站发现与爬取(体检第 0 步)**——四级发现链(urls→robots→sitemap[≥50 条关爬虫]→首页 BFS);子域发现(DNS 探测+可选 crt.sh);内外链图(edges/孤儿页/外链域聚合;sitemap 模式也先抓首页,带跟踪参数的内链计入干净 URL 的入链,截断时孤儿只代表已抓样本);遵守 robots+crawl-delay,默认 500 页;--urls-out 直接喂 site_audit/traffic_funnel
- `site_audit.py URL [--market]`:单页全项审计(CRITICAL 退出码 1);--market 接线 markets.json 18 市场阈值(chars/fullwidth/grapheme 单位),词数 CJK·天城文·泰文字素·全字母文字感知;含 **AI Search Health 独立子分**(Semrush 口径 8 bot+Last-Modified 183 天+语义 HTML 比值+llms.txt+BLUF 密度+rendering 5 检查,--json 出 ai_search_health 节;--export-dir 出每规则具名受影响 URL 清单+summary.json+报告受影响面% 列)
- `health_score.py --input audit.json`:分层健康分——Ahrefs 主分(仅 CRITICAL 扣分,Weak/Fair/Good/Excellent 分档)+Lumar 六大类树(缺数据源 N/A 不计入)+Ryte impact 排序(立即处理/值得探索两栏);--ignore/--severity/--config rules.json 规则开关
- `traffic_funnel.py --audit audit.json --gsc gsc.csv`:六阶段页面流失漏斗(available⊃indexable⊃uniqueness[Simhash+DeepRank]⊃in_serps⊃with_clicks⊃good_ux);无 GSC 自动截断+coverage 声明
- `quality_rater.py FILE`:六维内容评分,publishing_ready=≥80 且 0 critical;证据行 UTF-16 偏移核验+同形字/孤立代理风险标注(标注层,不改六维分数)
- `above_fold.py URL`:首屏 700 字符"5 秒测试"(四元素加权 ≥70;跳过导航、Cookie 横幅、「跳到正文」链接和 x-cloak / display:none 的隐藏块;为落地页设计,新闻首页等站型的 CTA / 信任分不适用)
- `trust_signals.py URL`:证言/社会证明/风险反转(6 类中 ≥3 类满分)/权威(为商业落地页设计:新闻、媒体首页里的引语和百分比会被当成证言和社会证明,这类站型不用它打分)
- `core_eeat.py FILE`:CORE-EEAT 机械化(GEO/SEO 双分+1 项 veto 封顶 60,≥2 项标 BLOCKED 不出分)
- `content_score.py --draft 文件 --competitors c1,c2,c3 --keyword 主词`:透明内容评分器——MarketMuse 公式(50 话题×min 提及,2)+Surfer 双轨(SEO 轨+AI 轨前三查)+意图系数;竞品<3 拒评;术语表(重要度/典型区间/缺失清单+observed-consensus 共识词筛:≥2 竞品正文精确定位才入推荐层,落选留排除码);`--facts` D/K 事实分级(行首 D: 点名声明/K: 中性观察,分报不混算)
- `fix_plan.py --url|--audit audit.json`:审计→修复物生成器(6 类 FixItem:robots/llms/schema/meta/ai_discovery/content);默认 dry-run,--apply 只写 ./seo-fixes/;--estimate 收益预估
- `grounding_page.py --facts brand.yaml`:品牌实体事实页生成(Rankscale 11 条:dl 事实/FAQ 含名/volatile 独立/is-NOT 消歧/JSON-LD 镜像);--check 校验已有页
- `audit_compare.py --old a.json --new b.json`:两次审计对比(新增/已修复/delta 三清单+页级 changed);--baseline-gate N 回归门(Lumar Protect 语义)
- `ci_format.py audit.json --format sarif|junit|github`:CI 输出格式化(SARIF 挂 Code Scanning/JUnit 挂测试报告/github 注解);配仓库根 action.yml 一站式 PR 门禁
- `sensor_volatility.py --gsc gsc.csv`:自有词集 SERP 波动分(0-10 四档+z30 异常日);--context 供 monitor 告警附注"疑似算法更新而非站点问题"
- `forecast.py --kws kws.csv`:SEO 商业提案六步(seoClarity 官方):est_traffic→校准系数持久化→三 scenario(rank3/pct10/pos2,>30 位不预测)→orders/value/acquisition_value;省钱+赚钱双结构;配 templates/monitor/forecast-report.md
- `prioritize.py --audit audit.json`:条件优先级引擎(Botify 口径):18 条声明式规则+放大器+条件依赖型(noindex 意图/canonical PageRank)+segment 切换重算;"立即处理/值得探索"两栏
- `changelog.py --db monitor.db`:页面变更审计追踪(Conductor 口径):5 枚举事件+字段白名单+14 天日/更早周粒度;根因诊断"流量下跌那天页面改了什么"
- `doctor.py`:环境自检+凭证分层探测(T0 纯静态→T3 GA4,只探键名不读值)+全输出 redact;退出码 0=ready/3=需处理;报告按 tier 自动声明数据覆盖范围
- `ai_views.py --url|--html`:AI 视图层生成(Scrunch AXP 等价):语义净化版 HTML+Markdown+tokereductions 统计;默认 dry-run,--apply 写 ./ai-views/,人审后自行部署;不承诺引用提升(同 llms.txt 实证口径)
- `envelope.py --audit audit.json [--health] [--priority]`:三源统一封套 audit-data.json(summary/categories/action_plan 三段 phases)+**部分落盘契约**(每 category 即落盘 findings/*.md,--resume 断点续跑)
- `trend_watch.py watch|gate|backlog [--config 垂直配置]`:热点监控与选题闸门——**监控的是产品所在行业的趋势**(vertical_tokens 三层词表:品类+品牌+竞品;reddit_subs 按垂直选版),不是 SEO 元领域;六信号源(403 源跳过)→四问闸门(相关≥25 分/净新观点≥5/窗口 24-72h 分型/独家三选一)→GO·PIVOT·WATCH·DROP+wire 否决;briefs/ 落盘决策件配 trend-jack-playbook.md
- `remediation.py init|list|update|verify|report`:修复项生命周期——从 envelope 封套生成工单(phase→deadline SLA),verify 对比新旧体检**自动核销已修复项**(部分命中标 partial,新 finding 提示增补);wontfix 强制 note(接受≠消失);report 出 SLA 达成率——补全"体检→建议→修复→验证→关闭"闭环的最后一环
- `benchmark_report.py --audits dir|--monitor-db|--scores`:匿名基准聚合(State of GEO 式):P25/50/75 分布+Top 失败规则频次;偏差自白首尾强制;只聚合数字绝不含域名 

**技术 SEO**
- `sitemap_audit.py URL`:六坏桶+lastmod 三判定(伪造检测);给站点 URL 时先读 robots.txt 的 Sitemap 声明;子 sitemap 超过 --max-child 时按位置均匀抽样(含最新的末尾)
- `hreflang_cluster.py URL...`:簇矩阵(ISO 639-1 + 可选 ISO 15924 文字码 + ISO 3166-1 区域码;es-419 这类数字区域码 Google 不支持;回链缺失只影响那一对,不是整簇作废;多载体同时声明只作维护提示)
- `redirect_chain.py URL`:逐跳链/循环/301 检查
- `robots_posture.py URL`:AI 爬虫矩阵——**37 bot 四层名单(search 15/training 11/user 8/other 3,带官方核实标记)**+CITATION_BOTS 5 个**两级评分**(通配符 Allow 只拿部分分,专属规则才满分)+RFC 9309 四态判定+Cloudflare 注入检测+Content-Signal;--fix-robots 打印可追加的修复块
- `llmstxt.py validate|check|generate`:v2 校验/线上探测/生成
- `schema_lint.py URL`:@id/悬空引用/自评评分/占位符黑名单
- `head_check.py URL|FILE`:head 元素检查——charset 须在前 1024 字节(ERROR)/og:image 绝对 URL;与 OG 重复的 twitter:*、可删旧标签(x-ua-compatible 等)、元素顺序只记 INFO;不发 Accept-Language,被重定向时打印最终 URL;显式 `--market zh` 才查微信/QQ itemprop

**关键词与 SERP**
- `gsc_mining.py 导出.csv [--mode matrix] [--decay cur prev] [--brand RE]`:striking distance/低 CTR(排名 1–10,期望曲线是本套件口径)/蚕食/衰退(本期消失的查询按 0 计);接受网页导出的 `Top queries` 列
- `question_align.py --gsc qp.csv --pages pages.csv [--brand RE] [--fetch|--html-dir D] [--page URL]`:提问对齐候选页(展示多、点击 0)——title/H1/首段对查询词的覆盖与缺词、匿名查询占比、按本站分段 CTR 算的期望点击;方法见 [question-alignment.md](../content/question-alignment.md)
- `serp_overlap.py 输入.csv`:四档聚类判据(7-10/4-6/2-3/0-1)
- `keyword_variants.py`:跨语言变体归组(阿正书/越声调/全半角/土 İ/俄 ё)
- `payment_intent.py`:支付即意图标注(OXXO/cuotas/Pix/COD…)
- `geo_difficulty.py`:GEO 难度公式+客户三档
- `serp_occupancy.py --market XX`:市场 SERP 占位审计(UGC 五霸/聚合器/投诉站)
- `grid_rank.py rank_data.csv`:本地网格排名三指标(ARP/ATRP/SoLV;未命中 21 惩罚+盲区=ATRP−ARP 必同报)

**多语言实装(markets.json 数据层)**
- `market_lint.py --market XX FILE`:v3 检查注册表 64 条——special_checks 动态机检 52 条映射(全角可见长度(日 32)/泰文字素/句长/营销词 18 语/格式/敬语混用/简繁混检+ko nosourceinfo/ja 星5つ/en 可引性四要素/pt CNPIX骗局/de Werbung 双披露/id baku-gaul/EYD/th 佛历/pl 变音/sierotki/nl je-u·KvK 等)+ v3 常开机检 12 项(营销词密度/句长CV/FAQ问句密度/有源数字密度/H2 疑问式占比/列表密度/标题关键词位次/日期格式/电话前缀/货币符号/母语字符占比/noai·noimageai·nosnippet AI 退出 meta);--report 尾部打印该市场 AUTO 比例
- `local_format.py --market de|fr|ar|zh`:数字/标点空格/RTL 数字/日期/电话
- `ste_lint.py FILE [--lang en] [--glossary terms.csv] [--json]`:ASD-STE100 近似检查(程序句 ≤20 词、描述句 ≤25 词、段落 ≤6 句、一句一指令、被动、缩写、分号、术语一致);口径见 [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md),不出「合规」结论
- `text_metrics.py`:多文字词数(拉丁/西里尔/天城体按词、CJK 按字)/metronomic 句长 AI 签名/slop/Unicode 水印(--scrub 清除)
- `text_units.py`:按市场计量单位统计

**AI/GEO 测量**
- `citation_panel.py init|record|report|diff|decay|score`:采样面板(五状态/配对分母/Wilson CI);record `--answer-file` 自动提及检测(URL 掩码+实体词表自动填 mentioned/position);init 意图冻结分母(denominator_freeze 档案,分母不随答案漂移);report 按 branded·unbranded 分报(targeting 两栏各出全套指标+交叉错配计数);diff 配对差分(只对同 prompt×engine 且同指纹配对算 Δ,跨指纹强制标注"不可比");**decay 子命令**=Profound citation decay 协议(7 点平滑/4 道闸门/半衰期双口径并记/重写队列——Profound 厂商研究称中位 11 天(2026-09-30 博文,88.3 万页)与调研口径 ~4.5 周并记不选边,复测按短口径 W+2、刷新投入按长口径 8-12 周;两口径出处与分池规则见 multilingual-workflow.md);score=五维打分写回(硬 cap 机检+反通胀聚合);diff 带 signals(|Δ|≥5pp 且 n≥10/fingerprint/贡献排序);report 出 SoV/win_rate/citation_rate+brand vs source visibility;prompts 对象化(--prompts-file 吃 prompt-bank.md/--stage-mix 5+3+2/--persona-fanout)
- `fanout_analysis.py 输入.csv`:query fan-out 三桶(added/dropped/preserved)
- `ai_referral_log.py < access.log`:AI referrer 下界分析(+--bot-ua 先行指标);**bot 四桶分类**(on_demand/search_index/training/agent)+failure_rate 两级+llms.txt 双基线;--attribution 出 GA4 正则+归因纪律+自报问卷
- `citation_gaps.py --panel panel.json --brand-domains a.com`:引用缺口(竞品被引你没被的 URL+外联简报;has_competitor_run 高优先)+来源五分类(Editorial/Corporate/UGC/Reference/Own,逐域定性+行动提示)+gapLabel 七叉决策树(逐 prompt 诊断标签,competitor_owned 最高优先)→ 配 citation-outreach-brief.md 模板,与 cite_domain.py 串联
- `oracle_check.py --facts brand.yaml --responses responses.json`:AI 回答 vs 品牌事实核查(Athena 口径:25 条门槛/finding 状态机/Inaccuracy%/按引擎 model_accuracy)
- `cite_domain.py --input json`:CITE 40 项域名评级(veto BLOCK)+引用证据清单(三类来源分离:仅 provider_citation 计入 engines_cited;5 家引擎原始 JSON 字段路径,报告尾部与 --json citation_evidence 均输出)

**归因与管道**
- `did_attribution.py --pre --post`:DiD 对照归因(56/28/7 参数/三态判定/断代检测)
- `seo_vs_ads.py --gsc --ads`:四桶 join(double-paying 检测+省额区间)
- `yt_outlier.py videos.csv`:YouTube 2× 离群+标题词频(长短分基线)
- `trend_scout.py`:HN+Reddit 趋势雷达(失败源明说不猜)
- `freshness.py [DIR]`:证据保鲜(>90 天 stale/未来日期 error/--fail-stale)
- `report_build.py --findings json --out html`:自包含报告(禁 script/80KB/>20 条=失败报告)

**持续监控守护(从一次性审计到长期监控+自动完善)**
- `project.py init|migrate|adopt|run triage|next|status`:长期运营的工作区与编排器。`init` 在站点仓库根目录建 `seo-ops/`(project.yaml 带 `schema_version: 2`、history/ 体检快照、ledger/ 台账、monitor/ 监控、.gitignore 排除缓存和原始流量行),这是运营状态的唯一位置,可提交进 git;同一仓库多站点用 `--dir seo-ops-<名>`。`migrate` 把旧版 `<slug>.seo/`、`.seo-monitor/` 和散落的 remediations.json/panel.json 等搬进 `seo-ops/`:先复制、逐项核对(文件集合、工单 id 集合),全对上才把旧位置改名为 `*.migrated-<日期>` 保留;两处都有同名状态时拒绝。工作区 schema 比本版新时一律退出码 2,不改写。`next` 的阶段判定用记录里的时间(triage.json 的 generated_at、工单的 implemented_at),新克隆后照样判对
- `monitor.py init|run|diff|report|rebuild|quarantine|maintenance|sample-keypages`:守护核心——日检四问(可见性 site: 抽查/流量 GSC/索引 robots+sitemap/存活状态码+混合内容)+周检趋势(title-meta 漂移/llms.txt/sitemap lastmod/AI 爬虫放行),SQLite 快照入库,diff 按百分比阈值×最小样本地板出四级告警(critical/warn/info/low=自愈);quarantine 隔离坏 run(不再作 diff 基线)、maintenance 维护窗口(只记快照不产告警)、sample-keypages 按 sitemap 模板分组抽样建议 key_pages;visibility 检查支持 serp_source 源适配(bing 默认/duckduckgo 零 key/付费源注册位+对照表,config 可换);全模式 `--dry-run` + `--budget-minutes` 运行上限;`monitor.db` 只是缓存(不进 git),每次 run 的快照写 `runs/run-NNNNN.json`、每次 diff 写库的告警写 `runs/diff-NNNNN.json`、隔离状态写 `runs/status-NNNNN.json`,库不在时自动重建(`rebuild` 可手动);当前目录有 `seo-ops/` 时 `--dir` 默认 `seo-ops/monitor`;部署模板见仓库 `.github/workflows/seo-monitor.yml`(本地 cron/launchd/claude -p 无头路径在注释里)
- `notify.py`:告警分级路由器——slack/discord/telegram/SMTP 四渠道(secrets 走环境变量);critical 即时/warn 日批/info 周批/low 静默进报告
- 方法论:[持续运营手册](../monitoring/continuous-operations.md)(日四问/周趋势/月校准分层、四级 playbook、防疲劳三律、自动安全项 vs draft PR 人审边界)

**套件自维护**
- `self_check.py` / `link_check.py`
- `intel_check.py init|check [--source 名]`:信源变更检测(29 源注册表:RSS top-item(宽口径源按关键词过滤)+页面 hash,与 [信源监控体系](intel-sources.md) 同步维护)——check 拉全部源与 `.intel-state.json` 基线 diff,按 source→module 映射输出应更新的套件文件;退出码 1=有变更,按[自更新协议](self-update-protocol.md)执行更新

来源方法论见 NOTICE(百仓深扫改写,非复制代码)。
