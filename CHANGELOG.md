# Changelog

以后内容或结构有变更时,提升版本号并增加一条带日期的记录。
Future content or structure changes must bump the version and add a dated entry.

## 未发版 / Unreleased

- **测试站和复验闭环验收(RQ-229 第 3 批)**:`tools/testsites/` 加纯静态和 Next.js App Router 两个测试站,各埋 10 个已知问题;`run_example3.py` 跑三轮运营单(干净 0 个 / 埋 10 个 / 修 4 坏 1 新 2),两站五态逐条对上(例 3 通过)。测出并修了 `project.py` 站点地址规范化会丢端口和 `www.` 的 bug(回归测试修前红、修后绿)。
- **运营单精度**:同页同类问题换了说法(标题过长 → 缺失)算「变差」不算「一解决一新增」;同一天重跑不翻倍;深审跳过轻检已判非 200 的页、不重复报 noindex;`--allow-local` 才跑本地预览;站点不是 HTTPS 时报硬告警。
- **装进站点仓库**:`project.py ops install` 写 CLAUDE.md / AGENTS.md 规则段、`.claude/settings.json` 改动前钩子、定时模板,记 skill 版本(新文件 `skills/seo-suite/VERSION`,发版门核对);公开仓给警告。新脚本 `guard_hook.py`:在 main / master 上改 robots、noindex、canonical、重定向就拦下,分支上放行。
- **URL → 源码改成先看页面原文(例 4)**:`source_map.py` 默认抓页面的 title、描述、H1、正文首段,切成片段在仓库里反查(越少见越可信,import 链加分,语言目录对不上减分;模板拼的标题拿 import 链里的模板去套;只由 URL 实体词撞上的片段封顶 0.6)。20 条人工标注(测试站 10 + everyinfra 盲标 10):第一名正确 19/20,指错还敢动手 0 条;改前 everyinfra 那 10 条是 0/10,而且条条都敢动手。顺手修了按子串跳目录把 `content/en/build/` 整个漏掉、中文路径被 git 转义、超过 5MB 的内容文件被跳过三个 bug(`tests/test_source_map.py`)。
  Test sites with planted issues and three-round acceptance for the ops loop; `ops install` (rules block, pre-edit guard hook, schedule templates, pinned skill version); URL-to-source mapping now matches live page text first (19/20 on hand-labelled URLs, zero confidently-wrong picks).

## 0.39.1 - 2026-11-05

- **运营产物瘦身**:`seo-ops/runs/<日期>/light.json` 只存有问题的行(非 200、noindex、canonical 指别处、重试过),全 OK 的只记个数;`issues.json` 里已查 URL 存 10 位短哈希。2,769 个 URL 的站一期从约 900 KB 降到约 150 KB,一年进 git 的量从约 50 MB 降到约 8 MB。
  Ops run artifacts slimmed: light-check rows keep only problem URLs; checked URLs stored as short hashes.

## 0.39.0 - 2026-11-05

- **每周运营单(RQ-229 第 2 批)**:`project.py ops weekly|monthly`(新脚本 `ops.py`)一条命令出一屏运营单:硬告警、只推荐一件事、问题五态(没复查到的 URL 不算已解决)、到期复验(`ops change add` 记改动,+14/+28 天用 GSC 逐页逐日数比前后)、搜索与 AI 可见度(每个数写数据源;GSC 两个来源抽 3 天对账)、有点击却有问题的页五张清单(noindex / 4xx / 403 / 3xx / 非规范)、覆盖率(sitemap 全量轻检 + 按点击前 N 页深审,不够不出分)。`ops notify` 只在有硬告警或连续 2 期没人看时推 Telegram。
- **数据接入**:新增 `ga4_api.py`(GA4 Data API,AI Assistant 渠道和按引擎拆的 AI 引荐)、`gsc_api.py inspect`(URL Inspection,按每站每天配额记台账)、外部数据包格式 `seo-ops.external.v1`(站点已有数据管道时读它,不重复拉),说明见 `references/monitoring/ops-agenda.md`。
- **URL → 源码**:新增 `source_map.py`(Next.js App Router、纯静态;动态页沿 import 找数据,生成物指到生成器,带置信度)。
  Weekly ops agenda (`project.py ops weekly`) with hard alerts, one recommendation, five-state issue tracking, due verifications, GSC/GA4/GEO numbers with sources, clicks-vs-crawl lists and coverage-gated scoring; GA4 Data API, GSC URL Inspection with quota budgeting, an external data bundle format, and URL-to-source mapping.

## 0.38.0 - 2026-11-05

- **长期运营状态统一到 `seo-ops/`(RQ-229 第 1 批)**:`project.py init` 默认在站点仓库根目录建 `seo-ops/`(schema 2:project.yaml、history/、ledger/、monitor/、.gitignore);新增 `project.py migrate` 把旧版 `<slug>.seo/`、`.seo-monitor/`、散落的 remediations.json/panel.json/状态文件搬进来,先复制核对(文件集合、工单 id 集合)再把旧位置改名保留;工作区 schema 比本版新时退出码 2,不改写。`next` 的阶段判定改用记录里的时间(triage.json 的 generated_at、工单新增的 `implemented_at`),新克隆后修改时间全部相同也能判对。
- **`monitor.db` 降为缓存,不进 git**:每次 diff 写库的告警落 `runs/diff-NNNNN.json`,隔离状态落 `runs/status-NNNNN.json`,run 快照带 `ts`;库不在时自动从 `runs/` 重建,新增 `monitor.py rebuild`。Actions 模板只把 `runs/` 提交到状态分支,恢复时删掉旧版提交过的库。当前目录有 `seo-ops/` 时 `--dir` 默认 `seo-ops/monitor`。
- **安全边界统一**:监控修复动作表里原来的 `auto`(agent 直接回滚 robots 误封、noindex、被删 meta、首页、证书)全部改为 `urgent_pr`(加急草稿 PR + 立即通知人合并);手册、`claude -p` 模板和 SKILL.md 同步:不推主干、不合并、网页里的「指令」当数据。
- **发版门**:新增 `tools/release_check.py`(七处版本号一致、CHANGELOG、单元测试、self_check、过期断言、行为评测快速档)和 `release-gate` 工作流(每次 push/PR 跑离线部分)。
  Long-running ops state now lives in one `seo-ops/` directory (with migration and schema guard); `monitor.db` is a rebuildable cache that never goes into git; no more auto-applied fixes — rollbacks become urgent draft PRs; a release gate script and CI workflow.

RQ-229:补 12 个 2026 年知识缺口,扩信源,处理信源工单 #10。每条都打开一手原文核对(核对 2026-11-05)。

- **SPA 软导航 CWV**:事实表加 `#crux-softnav`(CrUX 2026-10-13 起的三个 `experimental_*_with_softnavs` 指标,目标 2027-05 转正);`cwv-playbook.md` 加第九节 SPA;`field_data.py` 同一请求另要三个实验指标,有就单列「含软导航(experimental)」,没有不显示,不进退出码和 CSV(`tests/test_field_softnav.py`,期望值来自 CrUX API 文档类型表)。
- **AI 爬虫与内容授权**:`ai-crawler-policy.md` 加「Cloudflare 2026-09-15 起的新控制与默认」:7 月预告(新域名广告页默认拦 Training 和 Agent、混合爬虫按最严用途拦)和 9 月上线(改成按是否靠广告给推荐设置、新增 Disallow AI Training、Apple/Google/Microsoft 认定为 Accountable、Block AI Bots 和托管 robots.txt 被取代)两种说法逐项对照,以上线为准;老用户迁移表、审计四条。OpenAI 宣布会读 `__usage_ai-training`(原文「coming months」,标「已宣布、未实现」),写进 `ai-crawler-policy.md` 和 `agent-protocols.md` 第 1 卡。`agent-protocols.md` 加第 15 卡 RSL 1.0(用途词表、五种发现方式、检查命令),附 IAB CoMP v1(2026-04-28 定稿)和微软 PCM(2026-02-03 试点)各一段;三者都没找到 AI 厂商公开承诺读取。
- **Google 政策与文档小更新**:`penalty-recovery.md` 补 2026-04-14 起垃圾举报可能直接触发人工操作(举报原文会发给被举报站)、2026-05-15 起垃圾政策适用于生成式 AI 回答、第三方 SEO/AEO/GEO 服务评估指引;`geo-evidence.md` 加「GEO 手法风险线」表(安全 / 越线 / 灰);`report-templates.md` 检查清单加「工具或服务声称 Google 认可」;`intel-sources.md` 更正「生成式 AI 垃圾条款没有单列日期」的旧说法(更新记录 2026-05-15 有单列)。`rendering-seo.md` 加「Read more」深链三条和审计第 9 项;`video-geo-guide.md`、`schema-examples.md` 加 VideoObject `creator`(2026-09-24)和 `interactionStatistic` 四种类型;`domain-strategy.md` 补迁站指南 2026-06-17「旧域所有已验证变体都要提交地址变更」。评价摘要新准则(2026-07-24)已在 `schema-examples.md`,补了原文两例。
- **Search Console 平台属性**:`video-geo-guide.md` 加平台属性一段(四个平台、报告、计数口径、指南里的五种分析)和检查项;`kpi-definitions.md` 加 KPI「平台内容的 Google 点击」口径。
- **电商 agent**:`ecommerce-geo-ladder.md` 第四节加微软 Copilot Checkout(2026-01-08,美国,商家仍是记录商户;2026-04-21 Microsoft Merchant Center 支持 UCP-ready feeds)、Web IQ(2026-06-02,建在 Bing 索引上的 grounding API)、Google AP2(2026-04-28 捐给 FIDO Alliance、v0.2 加 Human Not Present 支付);第五节和检查清单各加一行。
- **本地**:`local-grid-ranking.md` 加「Ask Maps」一节(2026-03-12 美印上线、2026-08-06 扩到 150 多个国家和地区;对本地 SEO 的四条含义,网格测不到),盲区清单加 Q&A API 2025-11-03 停用;`site-type-playbooks.md`、`gap-analysis-frameworks.md` 同步。`local_audit.py` 本来没有 Q&A 检查项,不用改。
- **GEO 证据库**:`geo-evidence-bank.md` 第七节入库两篇预印本(B 级):arXiv 2610.15033(多伦多大学,2026-10-10)和 2603.09296(2026-03-10),第 11 条的冲突说明随之更新;`citability-scoring.md` 加对应注记和方法纪律第 7 条。
- **AI 浏览器与 agent 工具**:`intel-sources.md` 更正 ChatGPT Atlas 已停服(2026-07-09 宣布、08-09 停止工作);`agent-growth-loop.md` 加第八节 Chrome 给 agent 的工具(DevTools for agents 1.0、Modern Web Guidance、Gemini in Chrome auto browse),写清各自在每周循环里怎么用、auto-connect 只用测试账号。
- **信源扩到 29 个**:`intel_check.py` 加 Chrome 开发者博客、web.dev 博客、Cloudflare 博客、OpenAI 新闻、Bing 搜索博客、Microsoft Advertising 博客、Google Maps 博客、Google Shopping 博客、arXiv「generative engine optimization」检索;发文多的源按关键词过滤(先看 50 条,只来无关文章不算变更);Atom 链接改读 `href`。用 12 条回放:11 条能接住,Atlas 停服只发在对脚本回 403 的帮助中心,接不住(`tests/test_intel_sources.py`,RSS 片段和回放标题来自真实 feed 和原文页)。`intel-sources.md` 第五节、`self-update-protocol.md` 映射表、`script-catalog.md`、workflow 注释同步。
- **回放顺带发现的两条一手公告**:微软 2026-10-30 宣布训练和 grounding 偏好分开设,2027-02-01 起随抓取认 `__usage_ai-training`,grounding 只能页面级设 `ai-grounding:disallow` / `disallowextended`,2027-03-01 后 `NOARCHIVE`/`NOCACHE` 不再算数;Cloudflare 2026-11-04 起能按单个个人 agent 设访问策略。写进 `ai-crawler-policy.md` 和 `agent-protocols.md` 第 1 卡,原来「微软一手页面未核到」的说法改为已证实。
- **信源工单 #10(2026-11-05 一轮,9 个源)**:Anthropic 爬虫帮助页页首新增托管浏览器说明,`ai-crawler-policy.md` 第一节表格加 `Claude-Agent`(真实浏览器 UA 加 token,IP 表在 `claude.com/.well-known/sail`,和三个 bot 的设置独立),`ai_referral_log.py` 把它归入 on_demand_fetcher(回归测试在 `test_s3_bot_rosters.py`);`penalty-recovery.md` 补 2026-11-04 Google 补发「站点声誉处罚不影响 EEA」邮件(第三方报道)。其余判为噪声:Search Central Live 苏黎世活动、OpenAI bots(仍是四个 bot、UA 1.4)、schema.org(仍是 30.1)、StatCounter 两页(当月数据滚动,2026-10 已入库)、Semrush Sensor(动态页)、Google Ads 搜索词匹配类型(广告,不在本套件范围)、Search Console 效果报告设备多选(界面便利,不改口径)。

## 0.37.1 - 2026-11-05

- **三站实战修复(everyinfra.com、plausible.io、sspai.com,8 个只读审计脚本,逐条对照原始响应)**:每处都有用真实 robots.txt 做 fixture 的回归测试(`tests/test_field_20261105.py`,修前红、修后绿)。
  - `site_crawl.py`、`robots_posture.py`:robots.txt 规则按 RFC 9309 匹配 `*` 和结尾 `$`,区分大小写。修前把 `Disallow: /tag/*` 当成放行,爬虫抓了站点禁止的路径。
  - `site_crawl.py`:非 ASCII 路径(如 `/tag/设计`)规范化时按 UTF-8 百分号编码。修前抛 `UnicodeEncodeError`,整次爬取作废。
  - `robots_posture.py`:没有任何匹配组时按 RFC 9309 默认放行,不再判「引用 bot 不可见」;「没给引用 bot 单独写规则」从警告降为提示(`*` 组对它们同样生效)。
  - `hreflang_cluster.py`:页面没有 hreflang 声明时,自引用一栏标「不适用」,不再报失败。
  - `sitemap_audit.py`:在 `python3 -I` 下也能导入同目录的 `hreflang_cluster`。
- **抽样核对修正 4 条断言**:Nozzle 排名追踪研究按 11-01 新版数据重写;去掉原文没有的「历史数据不补」「AIES 论文集」;13,184 条 AI 引用研究的作者改为 Bill Widmer。
  Field fixes from a three-site run: RFC 9309 wildcard and `$` matching in site_crawl and robots_posture (the crawler used to fetch disallowed paths), percent-encoding of non-ASCII paths, no-group robots.txt treated as allow, hreflang self-reference marked not-applicable on single-language pages, `python3 -I` import fix in sitemap_audit; four reference claims corrected after a random 30-claim source check.

## 0.37.0 - 2026-11-05

- **信源工单 #5 积压清理(2026-10-18 至 11-04,17 轮报告、17 个信源)**:逐个打开一手原文,改了 15 个参考文件;确认无影响的也记下来。
  - **AI 训练偏好新写法**:IETF 草案 `draft-kelley-aipref-training-preference-signal-00` 定义 robots.txt 里的 policy token `__usage_ai-training`(`User-Agent: *` 不算表态,只表达用途、不管抓取)。Anthropic 2026-10-30 起开始逐步遵守,点名 `ClaudeBot` 的规则优先;Google 宣布 2027 年支持,并把它的退出当作禁 `Google-Extended`。写进 `ai-crawler-policy.md`(第一节表、第二节禁训练配置)和 `agent-protocols.md` 第 1 卡。
  - **Lighthouse 13.6.0(2026-10-27)**:`ard-schema` 改按 ARD v0.91 读 `ard.json`,旧 `ai-catalog` 位置报 legacy 警告;CLI 支持 `--url-file` 批量审。改 `agent-readiness.md`。
  - **Google 文档**:防 UGC 垃圾指南 10-26 增补「只索引给搜索用的内容」和「监控滥用」(`ugc-site-search.md`);生成式 AI 内容指南补质量评估员指南 4.6.5/4.6.6 和 IPTC `TrainedAlgorithmicMedia`(`ai-writing-detection.md`);网页索引报告「已抓取 - 尚未编入索引」的新官方写法(`seo-drift-monitoring.md`)。URL 结构、Indexing API 配额、Control what you share 三条已和现有写法一致。
  - **Search Status Dashboard**:用 incidents.json 补齐此前漏记的 2025-12 核心更新、2026-02 Discover 更新、2026-03 垃圾内容更新、2026-05 核心更新;记下 2026-10-31~11-03 Search Console 点击虚高(第三方报告,Google 未确认)。
  - **市场数据**:StatCounter 搜索份额事实表换成 2026-10(俄、韩、日、中、土),各市场文件保留 2026-09 读数;Yandex 改用 2026 Q3 财报(Алиса AI 回答覆盖 44% 查询、搜索框下回答月受众 5,480 万);Naver 三条官方公告(10-15 起 HowTo 停显和摘要化、FAQ 卡片 07-09 停显、10 月起报表口径迁移)。
  - **GEO**:ChatGPT 12 亿周活、联网搜索量约为 Google 五分之一,按厂商自述入库并注明口径。
  - **确认无影响**:OpenAI bots(四个 bot、UA 1.4 未变)、schema.org(仍是 30.1)、CrUX(最新仍是 2026-09 数据集)、ARD 规范(只加了非规范性的可观测性说明)、Yandex 新功能页(页面改成前端渲染外壳,2026-04-07 之后无新条目)、Semrush Sensor(动态页)。StatCounter AI 聊天份额 2026-10 单月 ChatGPT 从 80% 掉到 51%,疑似口径变动,本版不入库。
  Cleared intel backlog #5 (17 sources, 2026-10-18 to 11-04): the shared `__usage_ai-training` robots.txt token (Anthropic honoring it since 2026-10-30, Google planned for 2027), Lighthouse 13.6.0 ARD v0.91, Google UGC-spam and gen-AI guidance updates, Search Status Dashboard backfill, StatCounter 2026-10 shares, Yandex Q3 and Naver notices.

## 0.36.0 - 2026-10-24

- **事实单一来源(2026-10-24)**:新增 `references/overview/facts.md`,收 11 类在多个文件里反复出现的外部事实(CWV 阈值、CrUX 窗口、Search Console 数据异常期、FAQ / HowTo 富结果退役日期、生成式 AI 效果报告日期、Search Console 保留期、sitemap 上限、Googlebot 抓取上限、API 配额、IndexNow 单批上限、搜索引擎份额),每条写值、一手来源和核对日期(2026-10-24 逐条重读原文)。74 个文件里 204 处硬写改成链接事实表。新看门 `tests/test_fact_single_source.py`:有人在别处重新硬写这些值就红(修前在改动前的树上实测 204 处 + 2 条一致性失败);事实表的值与脚本常量(`field_data`、`did_attribution`、`sitemap_audit`、`indexnow`、`gsc_api`)和市场文件份额自动核对。顺带修:`split_test.py` 写的 GSC 异常期结束日 2026-04-30 → 2026-04-27。记录在仓根 `deployments/2026-10-24-k2/`。
  Single source of truth for 11 repeated external facts (`references/overview/facts.md`); 204 hardcoded copies in 74 files now link to it; a new guard test fails when a value is hardcoded again and checks the table against script constants.
- **三个非中英西市场实战(2026-10-24)**:10 个 beta 脚本在日本 asahi.com、韩国 yna.co.kr、德国 spiegel.de 各跑一次(30 次),逐条对照站点原始响应判定;修了 14 处误报(另有 3 处真问题、field_data 因无 key 跑不了),每个带用真实响应做 fixture 的回归测试(`tests/test_k2_field_fixes.py`,修前红、修后绿):
  - `site_crawl.py`:sitemap 模式也先抓首页;带 `?iref=` 等跟踪参数的内链计入干净 URL 的入链(修前 asahi 40 篇首页直链文章全被判孤儿);`co.jp`、`co.kr` 等国家码二级后缀按三段算可注册域(修前 `www.yna.co.kr` 被归成 `co.kr`,默认模式会把别家 .co.kr 站当自家子域);sitemap 按 50MB 上限读取(修前 2MB 截断,spiegel 2.25MB 的 index 解析失败);子 sitemap 超上限时按位置均匀抽样(修前只取最前面的 1947 年起归档);被 `--max` 截断时孤儿标为「只在样本内判定」(`orphans_partial`),`orphan_fix`、`link_graph` 同步提示。
  - `link_graph.py`:带参数的内链边对到干净 URL(修前 asahi「内链边 0」,PageRank 全是 10.00)。
  - `sitemap_audit.py`:给站点 URL 时先读 robots.txt 的 Sitemap 声明(修前 yna /sitemap.xml 404 直接 FATAL),声明里的 index 照常展开;子 sitemap 超 `--max-child` 时均匀抽样(修前 spiegel 判「最新 lastmod 1978 年,过期」)。
  - `above_fold.py`:不把「跳到正文」链接(asahi、yna、spiegel 三站都有)和 `x-cloak` / `display:none` 的隐藏块当首屏文本。
  - `news_sitemap_check.py`:robots.txt 只声明 sitemap index、index 里列着本 sitemap 时不再报「未声明」;news:title ≥100 字符只提示(Google 文档没有长度上限)。
  Field run on Japanese, Korean and German news sites: 14 false positives fixed in site_crawl, link_graph, sitemap_audit, above_fold and news_sitemap_check, each with a regression test built from the real responses.

- **seo-suite 瘦身(2026-10-21)**:SKILL.md 从 47KB 压到 9.3KB,只留 intake、能力路由表和输出结构;87 个脚本的说明搬到 `references/overview/script-catalog.md`,原路由正文搬到 `routing-rules.md` 附节;`audit-rule-catalog.md`(307KB)按 20 个规则类别拆到 `references/technical/audit-rules/`,原文件改为索引页;使用原则 0 改为按任务大小决定是否先跑全站体检。内容只搬不改,搬运前后逐行核对无丢失。
  Slimmed seo-suite: SKILL.md cut from 47KB to 9.3KB as a pure router, script docs moved to `script-catalog.md`, and the 307KB audit rule catalog split into 20 per-category files with an index page; content moved verbatim.
- **site_audit alt 判定(2026-10-21,真实站点重跑发现)**:`alt=""`(装饰图的正确写法,W3C WAI)不再算 alt 缺失,只有没有 alt 属性才算;回归测试 `tests/test_b63_alt_empty.py`。`gsc_api.py` 帮助里的配额说明改为每站点/每用户 1,200 QPM。
- **深挖第二批完成(2026-10-21)**:129 份参考文件和 25 份模板全部逐条核一手来源,证据账本 5,499 条(V 3,164 / F 801 / D 557 / K 736 / 未核 241),每份文件都有检查清单;独立抽查 V 30/30、F/D 20/20 通过;文件里 905 处脚本参数全部在 `--help` 查到。核对记录在仓根 `audits/2026-10-21-reference-check/`(不随 skill 安装)。要点:hreflang 改按 Google 原文(es-419 不支持、zh-Hans 合法、缺回链只影响那一对);删掉全部买链价格表(Google 链接垃圾政策);GSC 生成式 AI 报告 2026-08-31 全球开放、只报展示,multimodal 筛选 2026-09-24 起;README「为什么是现在」两表按原文改口径或删除。
- **脚本 bug 第三批(2026-10-21)**:`robots_posture.py` bot 名单扩到 37 个四层、带官方核实标记,`ai_referral_log.py` 名单按官方页修正;越南、泰、土耳其、印地语的分词、大小写与词数(`ste_lint`、`question_align`、`keyword_variants`、`text_units`、`market_lint`、`site_audit`、`content_score`、`text_metrics`、`pseo_batch_gate`);`llmstxt.py validate` 报相对链接、接受 BOM;`core_eeat.py` 1 项 veto 封顶 60、≥2 项 BLOCKED;`monitor.py` heartbeat 按 healthchecks.io 官方端点;`citation_panel.py --prompts-file` 只收模板列;`directory_tracker.py verify` 认 sponsored/ugc;`head_check`、`field_data`、`forecast`、`multimodal_report` 的说明按核对结果改;`test_canonical_facts.py` 新增 6 条已退役功能检查。`markets.json` 18 个市场的文字按核对结果更新。
  Deep-review batch 2 complete: all 129 references and 25 templates checked claim by claim (5,499-row evidence ledger, independent spot-check passed, every script flag mentioned exists); script bug batch 3 (bot rosters, non-Latin tokenization, llms.txt validation, and more).

- **脚本 bug 第二批(2026-10-21,真实站点实测发现)**:每条先写修前红的回归测试(`tests/test_s2a_*.py`、`tests/test_s2c_*.py`、`tests/test_content_queue_help.py`)。
  - `site_audit.py`:只在结构性挑战页特征时拒审(页面谈论 captcha 不再被跳过);`--json` 的 stdout 只出 JSON(人读文字走 stderr,顶层加 `market`、`limits`);缺 description、缺 H1、相对 canonical 降为 WARN;>100 链接降 INFO(工具约定);有服务端内容时不报「无 JS 空页」;去掉「Botify 官方阈值」说法。
  - `markets.json`:18 个市场加 `desc_min`(上限的一半,修中文下限 > 上限);中文标题和描述按显示宽度计(全角 1、半角 0.5);es 删 es-419(Google 不支持);zh-CN 与 zh-Hans 都合法;支柱字数改标「本套件口径,不是排名要求」(Google 原文:没有偏好字数)。
  - `project.py`/`prioritize.py`/`envelope.py`:API/开发者站不再被认成电商,自报站型优先;建议按 `--market` 阈值。
  - `head_check.py`:不发 Accept-Language,被重定向时打印最终 URL;与 OG 重复的 twitter:* 只记 INFO(不是弃用);geo.* 不报缺失;显式 `--market` 优先;元素顺序降 INFO(charset 前 1024 字节仍 ERROR)。
  - `gsc_api.py`:`--dimensions` 支持 country、device、hour、searchAppearance。`market_lint.py`:zh-CN 合法、es-419 判不支持、外币标价改 INFO。`ai_referral_log.py`:失败率先剔除漏洞扫描探测路径,标「UA 未验证」。`site_crawl.py`/`orphan_fix.py`:内链外链分开计数,被重定向的页不算孤儿。`sitemap_audit.py --hreflang`:全站互指检查。`bing_wmt.py pagequery`:按页面看查询。`above_fold.py`:首屏取样跳过导航和 Cookie 横幅。`trust_signals.py`:认「失败不扣费/按成功计费/退款」,不再建议写不真实的承诺。`did_attribution.py`:断代期结束日改为 2026-04-27(GSC 数据异常页)。`health_score.py`:删掉未实现的 duplicate_description。`content_queue.py`:子命令 `--help` 列出该子命令参数。
  Script bug batch 2: 27 bugs found on a real site fixed with red-before/green-after regression tests (site_audit severity and JSON output, market thresholds, head_check, gsc_api dimensions, hreflang site-wide check, log probe filtering, and more).

- **深挖第二批(部分,2026-10-18)**:technical(robots、HTTP 状态码、重定向与 canonical、渲染、移动、日志、hreflang、head、Schema、LCP/CWV、实体与知识图谱、内链与导航、AI 爬虫政策、agent 协议、edge、Naver、pSEO、审计规则目录)、content(GEO 证据与证据银行、平台差异、打分、可引性、AI 写作识别、品牌档案、衰退与刷新、深度研究、Discover、UGC、社区)和 markets(ru、zh)共 42 个文件,已按一手来源改过一部分并补检查清单;这批的核查因额度中止,未全部完成,剩余条目和其余参考文件下一轮继续。自检全绿。
  Deep-review batch 2 (partial): 42 reference files partly rechecked against primary sources with checklists added; review paused for usage limits and continues next round.

- **深挖第一批(2026-10-18)**:每条结论逐条核一手来源(Google Search Central、Bing、schema.org、规范原文、论文),错的改、没依据的删,概念段改成「检查什么→怎么查→通过/失败」的检查清单。本批提交:title-formulas、meta-tag-formulas、content-structure-templates、content-patterns(核 176 条:核实 75、改正 13、删除 37);其余参考文件分批提交。
- **新增方向文件**:`references/content/question-alignment.md`(提问对齐:title、H1、首段用买家原词,首段第一句直接回答;取词来源、选页规则、判据与测量)、`references/content/asd-ste100-web-writing.md`(ASD-STE100 Issue 9 网页借用:程序句 ≤20 词、描述句 ≤25 词、一句一指令、主动语态、术语一致;写明 STE 没有排名或 AI 引用实证)。
- **新增脚本**:`question_align.py`(提问对齐候选页:展示多点击 0、匿名查询占比、title/H1/首段覆盖与缺词、本站分段 CTR 期望点击)、`ste_lint.py`(ASD-STE100 近似检查,不出合规结论)。
- **真实站点实测修的 bug**:`gsc_mining.py` 两期对比遇新查询崩溃、消失的查询不报、低 CTR 规则从不触发(只看排名 11–20)、"0.5%" 被读成 50%、不认 `Top queries` 列,并加 `--brand`;`hreflang_cluster.py` 把 zh-Hans 判非法、放行 es-419(Google 原文写明不支持)、把单条回链缺失说成整簇作废、把多载体同时声明当冲突。均补修前红、修后绿的回归测试。
  Deep-review batch 1: claims checked against primary sources; question-alignment and ASD-STE100 references added; question_align.py and ste_lint.py added; gsc_mining and hreflang_cluster bugs found on a real site fixed with regression tests.

- **intel-update 工单修复**:workflow 此前在生成工单时再跑一次 intel_check,第二次比对的是第一次刚存下的基线,工单头部写"有变更"、正文恒为"无变更"(10-13/10-14/10-15 复现)。现在只跑一次,报告直接写进 `intel-update-pending` issue(新开或追加评论),不再提交仓根 `.intel-update-task.md`;无变更时不再自动关单;异常退出(无 `[CHANGED]` 行)单独记 error,不开 issue。
- **运行态文件移出仓库**:`findings.json`、`crawl.json`、`briefs/`、`.intel-update-task.md` 加入 .gitignore 并从仓库删除;`tests/test_fix_oracle.py` 改为把 findings 写进临时目录(此前每跑一次测试都在 CWD 落一份 findings.json);trend-watch 的 `.github/state/trend/briefs/` 不再被 `briefs/` 规则误吞。
- **自更新协议改写**:`self-update-protocol.md` 按现行方式改为「云端检测 + issue 工单 + 本地处理」,触发模板路径改占位符,提交改精确路径(不用 `git add -A`)。
- CHANGELOG:合并重复的 0.28.0,0.23.1 归位,补写 0.11.0–0.19.0。
  intel-update now reuses a single check run and files the report into the pending issue (no committed task file, no auto-close); runtime outputs ignored and removed from the repo; self-update protocol rewritten for cloud detection + issue tickets + local processing; CHANGELOG duplicates/gaps fixed.

## 0.35.0 - 2026-10-12

- **50-agent 战役(10 波,37→85 脚本/1604 测试)**——从"分析工具集"进化为"完整管线工作台":
  - **R5 正确性**:37 个复现验证的 bug 全修(假 Wilson→真公式/robots 假 CRITICAL/冷却失效/oracle 五市场失明/除零/时区/GBK);SSRF 铲平 17 脚本;一致性 12 处+事实 6 处;SKILL 路由重排;
  - **R0 接线**:sensor 波动上下文/CWV 周检/citation decay 全进 monitor 告警链;remediation verify 云端排期;trend 3h cron;issue 超时;freshness CI;
  - **R1 管线骨架**:project.py 编排器(init/run triage/next/status+工作区)/strategy-fit 决策层+站型识别+intake 4 问/content_queue 选题队列(ContentOps 遥测)/fix_plan --git-branch 发布通道/ai-use-policy(AP 四象限);
  - **R2 数据接入**:gsc_api.py(纯 stdlib RSA,openssl 对拍)/backlink_import 三格式+引荐域月检/IndexNow+BingWMT/byo_import+parity_check/schema_version 推广+doctor --keys;
  - **R3 生产线**:pSEO 三件(pattern_mining/batch_gate/cohort 预注册判读)/link_graph+锚文本采集+orphan_fix/market_fit+market_batch 多市场批量/prune_gate+content_inventory 四轴治理;
  - **R4 末端+监控对标**:outreach/directory tracker/split_test 功效计算/synthetic_control+geo_experiment+triangulate/SLO+错误预算/flapping+ack 超时/postmortem+log_session+owner_team;
  - **R6 知识边界**:证据银行 Q3 学术批次(3 修正+8 全新)/冻结协议+四层节奏+program-management/Search Everywhere+Brand SERP+Community 三新文档/IAB 4P+agentic commerce+付费 AI 面/edge-seo+AI Crawl Control 三态/Job+房产垂直卡/Ryze 一方数据桥(referral↔panel 双轨)/站型卡 48 条命令链/云端状态 commit-back 统一/e2e 回归 57 例零新断裂;
  - README.en 正文完整化;治理矩阵 123 条全刷。



## 0.34.4 - 2026-10-11

- **借鉴清单复盘清零**(用户指出的复盘机制首次执行):
  - 20 项清单状态列全面过期(多数已实现仍标 ❌)——逐条实测核实刷新:**19 ✅ + 1 部分**(第 19 条 Opportunity 落在 prioritize 两栏/规则目录类型轴,site_audit 三态契约冻结,取舍注明);borrow-specs 尾部新增「复盘记录」节+机制(intel-update 月度搭车核对+新能力同 commit 回写状态列);
  - **补齐第 10 条**:site_audit `--export-dir`(每规则具名受影响 URL 清单+summary.json+markdown 受影响面% 列,15 测试);
  - **补齐 D1-P2#13**:monitor SERP 源适配层(SERP_SOURCES 注册表:bing 默认逐字节兼容[42 场景对拍实证]/duckduckgo 零 key/serper·SerpApi 注册位+价格对照表,16 测试);
  - **README 双语加「60 秒体验」段**(一条命令零 key 跑通体检→分层分→修复建议,example.com 实跑验证);
  - 788 测试全绿。



## 0.34.3 - 2026-10-11

- **GEO 内容战略调研全量接入 skill**(5 轮 10 agent 调研 + 4 agent 接线):
  - **新文档**:templates/content/trend-jack-playbook.md(热点选题四问闸门+判定矩阵+48h 管线)/references/content/deep-research-protocol.md(五轮检索+IGS 自检+引用纪律)/references/research/multilingual-geo-evidence.md(fan-out 语言切换/机翻降权/分市场杠杆/小语种红利);
  - **multilingual-workflow.md 接入 9/9 工单**:U1 引用池语言切换/U2 hreflang chatbot 弱信号(每语言 URL 自持权威)/U3 分市场杠杆四格表(Tistory·引用枠·头条·Habr)/U4 机翻降权分界/U5 小语种唯一源原则 28/U6 时效预期管理/U7 半衰期双口径并记/U8 新工作流接线/U9 四门户页+hreflang-validation 联动修正;
  - **geo-evidence-bank.md +14 条**(A 级 4/B 级 5/C 级 2/中文区 3,全部带核查后降级标注;8/14 曾降级:Weglot 厂商口径/peec 78%→43%/中文引擎占比定性化);
  - **pre-publish-checklist 27→32 条**(内联具名引用/统计数字密度/净新观点≥5/反例与不确定性标注/时间戳+答案前置);content-brief 加引用与增益纪律节;
  - **trend_watch.py 实装**(56 号脚本):六信号源 watch/四问 gate/五态 backlog,29 测试零网络;实测可达 Google News/HN/百度,Reddit/微博 403 跳过;
  - 672 测试全绿;本机副本同步。



## 0.34.2 - 2026-10-11

- **第 8 波(10 agent,3+3+4 批)——niubigeo 借鉴落地+治理闭环,613→643 测试**:
  - **citation_panel 四项增强**(URL 掩码提及检测 --answer-file/branded·unbranded 分报切片/意图冻结分母/配对差分跨指纹"不可比"标注);**citation_gaps 来源五分类+gapLabel 七叉决策树**+cite_domain 证据清单(N3 五家字段路径);**content_score 共识词筛+D/K 事实分级**(分数零变化,纯纪律层);**quality_rater UTF-16 证据核验**(同形字/孤立代理检出);
  - **CAPABILITY_MATRIX 治理**:data/capability-matrix.json 89 条+人读版+test_capability_matrix 五检接入 self_check(新增脚本不登记即红);
  - **规则目录第四批 50 条(累计 220)**:E-E-A-T 16 全量+Accessibility 34 全量(双理由)+实体图六查+Legal;
  - **freshness 回填**:9 处补测量月(纠 2 处误归属:ipullrank→Similarweb、Profound 数字误挂 SE Ranking),6 处诚实升级[未证实];
  - **workflow 接入**:seo-monitor 加 envelope-report job(日基线归档+baseline-gate+月度匿名基准)+intel-update 加 capability-drift job;
  - **examples 扩到 5 例**(envelope 全链/AI 视图离线重放/七叉决策演示);**端到端集成测试 30 条**(全链零网络)——并揪出 2 个真实互操作断裂已修:fix_plan 吃不了 raw stdout JSON、citation_gaps 对象化 prompt 崩溃(均修复+回归测试)。



## 0.34.1 - 2026-10-11

- **第 7 波(9 agent,小批量重跑)——52→55 脚本,523→545 测试**:
  - ai_views.py(AI 视图层:语义净化 HTML+MD+token 缩减统计,默认 dry-run 人审边界)/monitor **P2 七项**(meta removed 语义/h1·hreflang 指纹/GA 跟踪消失/非规范域 probe/字数漂移/improved-declined 汇总/expect 数组+selector_stable+防假 0)/规则目录**第三批 47 条(累计 170)**;
  - citation_panel **score 子命令**(五维打分写回+校验器硬 cap 机检+top_pick 佐证降级+反通胀聚合)/envelope.py(三源统一封套+**部分落盘契约**+--resume)/评分契约测试(权重守恒断言+冻结 fixture+schema_version 补齐);
  - benchmark_report.py(匿名基准聚合+偏差自白+域名绝不入输出)/全仓 freshness 扫描(修 21 处:数字一致性/日期口径/过时信号)/**niubigeo 深读入库**(Albert-Weasker/niubigeo 6,848★ 五周爆发,Top 10 借鉴规格);
  - 事故处理:首跑 9 agent 并发触发账户速率限制全取消→小批量(3/批)重跑成功;回退取消波的半成品注释。



## 0.34.0 - 2026-10-10

- **33 agent 六波实施(施工图 borrow-specs.md 全面落地)**——38→**52 脚本**、14→**22 模板**、75→**426 测试**,全部纯 stdlib:
  - **wave1 审计与健康分**:health_score.py(Ahrefs 主分+Lumar 六大类树+Ryte impact 两栏+--ignore/--severity)/traffic_funnel.py(六阶段漏斗+Simhash+DeepRank)/site_audit AI Search Health 子分(Semrush 8 bot+183 天+BLUF+rendering 5 检查)/规则目录 79 条 Sitebulb 式解释层/deprecated-signals 看门表+16 正则 canonical facts 回归/robots_posture 27bot+CITATION_BOTS 两级评分/AI 可见性周月报模板;
  - **wave2 GEO 可见性**:citation_panel decay 子命令(Profound 半衰期协议:4 道闸门/重写队列)+signals 化 diff(5pp+n≥10/fingerprint)+SoV 指标族+prompts 对象化/citation_gaps.py 引用缺口+外联简报/oracle_check.py 品牌事实核查(Athena 口径)/ai_referral_log 四桶+归因工具箱/prompt-bank/brand-records/五维打分卡;
  - **wave3 内容**:content_score.py(MarketMuse 公式+Surfer 双轨+意图系数,竞品<3 拒评)/fix_plan.py(6 类修复物+dry-run 默认+隔离目录+收益预估)/grounding_page.py(Rankscale 11 条)/content-brief+pre-publish-checklist+report-modes 模板;
  - **wave4 监控与 CI**:monitor P0(页面级 noindex[Conductor 头号触发器]+canonical 目标健康度连击防抖)/notify 按类型路由+incident 生命周期+redact/sensor_volatility.py 波动分/audit_compare.py+ci_format.py(SARIF/JUnit/github)+action.yml PR 门禁/ci-gates 手册;
  - **wave5 工作流**:forecast.py(seoClarity 六步+三 scenario+校准持久化)/prioritize.py(18 条条件规则+放大器+segment 重算)/changelog.py(5 枚举事件+周折叠)/doctor.py(凭证分层 T0-T3+全输出 redact)/monitor P1(segments/accepted_codes/diff --ci/sample-keypages/baseline 警告);
  - **wave6 文档产品化**:data-source-contract.md(52 脚本数据/降级/反编造合同表)/examples/ 规范化(真实 example.com 审计全链+合成面板演示)/规则目录第二批 44 条(累计 123)/capability-map 重写(52 脚本+6 子系统闭环+10 条任务路由);
  - 测试框架升级:run_tests.py 自动发现 tests/test_*.py(各 agent 零冲突并行);self_check 22 模板七段式全过。


## 0.33.0 - 2026-10-10

- **13 agent 竞品深读 + 多宿主适配**:
  - **多宿主适配(用户点名)**:SKILL.md 本体零适配(Agent Skills 开放标准);install.sh 重写为**多宿主安装器**(真源 ~/.agents/skills + 向检测到的宿主建 symlink;--all/--agent/--uninstall;每宿主打印验证方式);新建 **HOSTS.md**(10 宿主适配矩阵:目录/调用/验证/注意事项);`.zcode-plugin/plugin.json` 薄清单(ZCode 原生插件形态);SKILL.md 加标准 `metadata.adapted-hosts`(全宿主安全的自定义位);README 安装节重写;
  - **新 references/research/borrow-specs.md(实施规格库)**:13 agent 深读的施工图——Lumar 六大类树+Ahrefs 主分公式+Ryte impact 排序(health_score)/SF 320 条 issue 矩阵+Sitebulb 九节文案结构(规则解释层)/Semrush 8 bot+183 天阈值(AI Search Health)/Profound citation decay 官方方法论(半衰期 11 天/四道闸门/重写队列)/citation_gaps 算法/prompt 库三维框架+fanout 六类型/五维打分+硬 cap/Peec SoV·win rate 公式/Athena Oracle/MarketMuse 计分公式+意图系数表/content-brief 三段式字段/fix_plan 6 类 FixItem+27 bot 模板/seoClarity 六步 forecast/Botify 条件规则/Conductor 告警 5 参数模型+monitor 14 条缺口清单/LHCI 断言 schema/凭证分层+doctor+redact/可证伪 4 字段/过时信号全表+test_canonical_facts 机制/数据源标注五段合同/Brand Records 六记录/Rankscale grounding page 11 条;
  - 修正:claude-seo 实测 35 命令(文档 34)/seranking 161★(agent 初报夸大)/本机 ~/.agents 安装副本为无脚本旧版(待刷新);
  - install.sh 修 bash3.2 local 展开序 bug;bash -n+--dry-run 实测通过。

## 0.32.0 - 2026-10-10

- **竞品全景调研(6 agent 并行) + Plugin/Marketplace 打包 + intel_check 抖动抑制**:
  - **新 references/research/competitive-landscape.md**:五类形态全景(企业闭源 7 家/主流 SaaS 6 家打分口径速查/内容工作台 6 家/GEO 创业赛道 13 家含融资事件/开源 10 项,stars 经 GitHub API 复核)+ 2025-2026 行业共识数据(AIO 点击 -58%、llms.txt 三份实证裁决、AI 归因方法)+ 20 项借鉴清单(逐条标注现有/缺失);
  - **Plugin/Marketplace 打包**:新增 `.claude-plugin/plugin.json`+`marketplace.json`(2 个 JSON,一条命令安装/更新/版本钉扎),README 双语加 Plugin 安装节,仓库根新增 **PACKAGING.md**(Skill/Plugin/MCP/CLI/GH Action 五形态对比矩阵与结论:Skill 是内容、Plugin 是包装、MCP 是数据接口——不自研 MCP server,声明式接第三方);
  - **intel_check hash 源二次拉取确认**:检出变更后立即重拉,两次一致才算真变更;JS 渲染动态页(StatCounter 图表)自动按噪音跳过且不动基线(streak 计数);同轮同 URL 去重;self-update-protocol 与 intel-sources 同步说明;
  - **4 个金标测试新增**(intel_check 首次有覆盖:抖动抑制/真变更检出/属性洗牌稳定/RSS 新条目),71→**75 tests**;
  - 赛道信号:同类 claude-seo 8 个月 18,626★(GitHub API 复核)验证 Plugin 形态流量。

## 0.31.0 - 2026-10-10

- **10 agent 体检+全面修复**:4 个测试团队(真实用户场景/脚本工具链/知识准确性/架构债)找问题 → 修复团队执行(12 项 P0+4 项 P1 全完成):
  - **P0**:site_audit **fetch 质量守卫**(403/挑战页/<200 bytes→SKIP 拒绝假 CRITICAL)/intel_check **hash canonical 化**(属性排序+去 script 再哈希——永久误报修复)/install.sh **--help/--dry-run/--force**(不再 --help 触发真装)/11 个脚本补 **--help**(gsc_mining 等不再 traceback)/SKILL.md **补 19 处 markets 路由**(31 个缺失文件挂入)/capability-map **重写**(195→精简,4 个深读笔记拆至 appendix)/intel-sources 死链修/Reddit 塌陷更新(→0.5% 2026-08)/llmstxt HTML **PASS/FAIL** 判定;
  - **P1**:gsc_mining+site_audit+market_lint **--json** 结构化输出/citability-scoring 加"用哪套"入口行/README 系列段时序+数字统一/multilingual 第十二节去代号;
  - **知识准确性**:26 条声明抽查 24 准确/92.3%;18 URL 17 有效(死链修);
  - 25 文件改动+446/-224 行;71 tests 全绿。
  10-agent health check + full fix: 12 P0 + 4 P1 all resolved; 92.3% fact accuracy on spot-check.

## 0.30.1 - 2026-10-10

- **全面体检+修复(逐文件扫描)**:
  - intel_check.py 403 修复:GSC 公告页 404→改用 Search Blog RSS;Yandex en/new-features 404→改用 ru/new-features(200);**18/18 源全部可用**;
  - 全套件体检:12 个文件修复——残留空文件删除/SKILL.md 脚本数 37→38+补 intel_check 路由+标题序号/geo-evidence-bank 的 AIO CTR 口径统一(34.5% 2025-04→58% 2026-02 标注测量日期)/**14 处 zubair-trzada→zubair-trabzada 拼写修正**(原拼写 404)/NOTICE 补登 10 个漏记仓库/README 双语数字更新(38 脚本/71 测试/18 市场/0.24-0.30 系列);
  - 38 脚本全编译零第三方;71 tests 全绿;markets.json 与门户页数字一致;市场总表 11+7=18=门户数;
  - 未修的结构性发现:capability-map/playbooks 追加式组织债/多时间戳倒挂/README 系列段排序——记录待重构。
  Full health check: 12 files fixed (URL 404s, spelling 404s, version counts, date annotations), 18/18 intel sources functional, all 38 scripts compile, 71 tests green.

## 0.30.0 - 2026-10-10

- **自更新循环落地(信源→直接更新 skill,不只是知识)**:
  - **intel_check.py(18 源注册表)**:init/check 两命令——RSS 源取 top 条目+seen 列表,hash 源取去时间戳指纹;变更检测后输出**受影响的套件文件列表**(基于源→模块映射);退出码 1=有变更(可触发 cron 后续动作);16/18 源 init 成功(GSC/Yandex 页面被 403,已记 fetch_error 跳过);
  - **self-update-protocol.md**:自更新 SOP——四步流程(确认变更性质→按映射改文件→self_check 验证→commit);**P0 规则级/P1 事实级/P2 事件级/P3 噪声四档分级**;安全边界(陈述性自动改/行为性须人审/脚本逻辑不改);cron 触发指令模板;频率建议(全量周检/Sensor 日检/freshness 月扫/竞品双周);
  - 状态文件 .intel-state.json(已 gitignore);首次 check 报"10 个受影响文件"是因为 3 个 init 失败源的首检差异——第二次 check 趋稳;
  - **闭环**:用户开定时任务(周一次)→发指令→agent 跑 intel_check→按 protocol 更新规则/阈值/脚本→self_check→push。
  Self-update loop: intel_check.py (18-source registry with change detection + module mapping) + self-update-protocol.md (4-step SOP with P0-P3 grading, safety boundary between auto-safe and human-review).

## 0.29.0 - 2026-10-10

- **新增 [信源监控体系](skills/seo-suite/references/overview/intel-sources.md)**(回答"要持续领先该重点监控搜索哪些信源",三路 agent 深度调研):
  - **四层清单**:①官方引擎 top20(Search Central Blog/文档 changelog/GSC/Status Dashboard/Lighthouse/ARD/WebMCP/Schema.org/CrUX/StatCounter 国家页/Yandex·Naver·Baidu——各带频率与 RSS/哈希/API 抓取方式);②研究数据层(arXiv 周扫检索式+五家数据团队系列名+已知 GEO 论文脉络);③社区与 18 市场本地信源(每市场至少 1 个+Google Blog 语言版兜底);④竞品观察名单(7 仓活跃度+**黑马 niubigeo 5 周 6,140★**+新仓双周扫描检索式);
  - **信源→模块映射表**(哪个信源变了改哪个文件——把监控变成维护 SOP);
  - **风险信号**:2026 spam 已 4 轮+6 月起明文覆盖操纵 AI 回答+8/28 壙站声誉修订→内容模块合规边界需跟;
  - **风向标**:竞品重心从 SEO 审计转向 AI 可见性监测+MCP 化;GSC 官方 AI 报告=数据层最大变量。
  Intel sources system: 4-tier monitoring list (top-20 official / research / 18-market local / competitor watchlist) with source→module mapping — the answer to "what to monitor to keep improving."

## 0.28.0 - 2026-10-09

- **模板深化 + 孤儿文件清零 + market_lint v3(完善度清单第 1-3 项)——special_checks 机检映射 24→52 条 + v3 常开机检 12 项(检查函数注册表共 64),golden 测试 62→71**:
  - **templates 层全面深化(第 1 项)**:12 个骨架模板全文重写到标杆水准(60-84 行/个)——每模板加 Key numbers 区/核心结构表/What could change;代表:serp 九特征矩阵/competitor 每家竞品卡+对位表/pages-plan 内链图+发布顺序/strategy 支柱集群+90 天日历/on-page 九元素市场阈值表/technical 五层栈/entity 实体矩阵/alert 四级 playbook+升级链/backlink 价带三层/performance AI 引荐趋势/rank 五桶×市场×引擎分列;
  - **孤儿修复**:audit-tool-output.md(56→140 行已深化)SKILL.md 裸路径升级为带描述链接行;basename 全量反查再发现两个真孤儿并全部入链——grid_rank.py 与 head_check.py(S7 可执行层漏排,37 脚本清单补齐)+ examples/gold-standard-keyword-research.md(research 路由挂黄金样例);复检孤儿=0;
  - **⑨ special_checks 第二批映射 +28 条**(可机检未实现项,覆盖 30 条 special_checks 条目):ko nosourceinfo(全球唯一官方 AI 引用退出 meta)/标签-值网格/연관채널 sameAs、ja 星5つ QR 王道违法话术、en 段落级可引性四要素(专名+数字+as-of+方法学)、es coche/carro 词汇分流+支付词层、pt CNPJ·OAB 凭证/仅收 PIX·boleto 骗局信号/publieditorial rel 披露、de Werbung 标签+rel 双披露(OLG Köln 口径)、fr courriel/balado 术语表(fr-CA 硬判)、id desc 120 字符安全区/baku-gaul 正文词典化/EYD V 新旧拼法并存、hi 语音助词、it it-CH(.ch+CHF 分裂)/P.IVA/估算声明降级、tr tanıtım 披露、vi 标题词前 30 字符(t0mmy)、th 佛历年(泰月名配公历年即 FAIL)/词中截断余量、pl 剥变音残留/sierotki 行尾孤字、nl je-u 混用/[INVULLEN] 占位/KvK 号;
  - **⑩ v3 常开机检 12 项(全市场注册表,输出数值供阈值判定)**:内容类 营销词密度(per 千词/千字)/句长 CV(<0.25=AI 均匀签名)/FAQ 问句密度/有源数字密度(同句来源线索占比<30% 且数字≥5=无源堆砌);结构类 H2 疑问式占比(¿/什么/怎么/why/how/wie/wat… 12 语)/列表密度 li/(li+p)/标题关键词位次(高频词代理);格式类 日期格式按市场(de 见 10/9/2026 即 WARN)/电话前缀(+7/+82/+86/+91/+55…)/货币符号(€ vs 元、R$ vs $);语言类 ru 西里尔/ko 谚文/th 泰文字符占比;robots 类 页面级 noai/noimageai/nosnippet AI 退出 meta;
  - **--report 尾部新增 AUTO 比例行**;18 市场全量跑通无崩溃;zh/de/ja 真实样文冒烟:special_checks AUTO 比例 zh 2/10=20%(剩余 8 条均为平台级 offpage,不可页内机检)+12 项常开机检(营销词密度 11.4/千字、标题关键词位次命中)、de 2/9=22%→3/9=33%(+Werbung 双披露)、ja 6/10=60%→7/10=70%(+星5つ);
  - 测试 62→71(+9:电话前缀/日期格式/AI 退出 meta/货币符号/句长 CV/AUTO 比例行/ko nosourceinfo/de Werbung 披露/H2 疑问式占比),零网络全绿。
  12 templates rewritten to benchmark depth; orphan files zeroed (audit-tool-output descriptive link; grid_rank+head_check wired into S7; gold-standard example linked); market_lint v3: +28 special_checks mappers (24→52) + 12 always-on checks (64-function registry), AUTO-ratio line in --report; tests 62→71.

## 0.27.0 - 2026-10-09

- **20 路深度审计+全面融入(用户指令:先审计评测,再融入)**——8 个 agent 并行审计(常驻平台/GH Actions 生态/agent 运行时/商业平台基准/自家红队/五细分/五开源深入/五周边反面),产出 8 份审计报告(归档 monitor-audit/),提炼 40+ 条建议,全部实施:
  - **P0 修复 7/7(红队发现)**:cooldown 通知层失效(suppressed 剔除双保险)/陈旧 alerts.json 重发(--max-age 拒发)/SQLite WAL+flock 防本地并发/基线污染(status 守卫+quarantine 命令+partial 标记)/**SSRF 302 穿墙(重定向逐跳复查)**/config secret 防泄漏/Bing cites 空值误判;
  - **P1 增强 8/8(最佳实践抄入)**:**dead man's switch**(heartbeat ping+2×周期检测)/双窗口判定(critical 需 7 天基线同向)/告警抑制树(site_down 抑制 page_down)/字段级 diff(selector 级)/run 状态机+PruneDB/workflow commit-back+matrix+issue 自动开关/if:failure() 兜底/**Apprise 式通用 webhook**/SSL 到期梯度+expect_substring+维护窗口;
  - **测试 46→62(+16)**;E2E 真实跑通:critical→cooldown 不重发→陈旧拒发→quarantine→自愈→report 全周期+SSL 实测 77 天+坏渠道隔离。
  20-path deep audit then full integration: 7 P0 fixes (cooldown leak, SSRF redirect, baseline quarantine) + 8 P1 best-practices (dead man's switch, inhibition tree, dual-window, Apprise webhooks); tests 46→62.

## 0.26.0 - 2026-10-09

- **持续监控守护层(用户核心诉求:从一次性审计→本地长期监控+自动完善)**:
  - **monitor.py(1148 行)**:init/run/diff/report 四命令——日检四问(可见性/流量/索引/存活)+周检叠加(漂移/llms.txt/AI 爬虫矩阵);SQLite 三表(run 快照/snapshots/alerts);**四级告警×百分比阈值×cooldown 抑制**;--dry-run/--budget-minutes;SSRF 防护;
  - **notify.py(377 行)**:slack/discord/telegram/SMTP 四渠道路由;critical 即时/warn 日批/info 周批/low 静默;
  - **.github/workflows/seo-monitor.yml**:日/周 cron+cache 持久化+告警触发通知;注释含本地 cron/launchd/**claude -p 无头调 skill**(prompt 带成功标准)三条替代部署路径;
  - **continuous-operations.md(145 行)**:分层监控表/四级×playbook×SLA/防疲劳三律/安全边界表(自动安全项 vs draft PR 人审项)/三部署形态对照;
  - example.com 真实跑通全流程:init→run→diff(零告警)→注入 404 关键页→CRITICAL 触发(rc=1)→cooldown→修复→LOW 自愈→report 出趋势。
  Continuous monitoring daemon: the suite is no longer one-shot — monitor.py + notify.py + GH Actions cron turn it into an always-on local platform with SQLite state, tiered alerts, and safe-auto/human-review boundaries.

## 0.25.0 - 2026-10-09

- **薄文件深化轮(逐文件行数审计驱动,11 个 <70 行文件→全部 120+)**——3 个 agent 并行:
  - **content 域**:discover-news(54→164:**Follow 功能 2025-11 已被移除**——原文件当现行功能写已修正;Chartbeat:Discover 占出版商 14.9% pageviews/AIO 首位 CTR −58%/突发新闻 +103%)/image-search(55→159:图搜流量案例/Lens 购物联动/C2PA 现状)/ecommerce-ladder(64→181:每级验收命令/印度 Flipkart 主场/UCP Integration Hub 上线·Universal Cart 证实/Noon 合并)/video(120→206:三平台可索引文本层/**Podcast SEO 新节**);
  - **technical 域**:hreflang(44→150:三载体对比 75% 错误率/x-default 六用法/CMS 陷阱三件)/log-analysis(53→156:三源日志正则/实战三案例/抓取预算闭环)/semantic-html(42→121:可访问性树与 agent/框架陷阱)/navigation(48→130:faceted 2025-12 官方细则/mega menu 预算);
  - **research+杂**:competitor-page-patterns(61→151:页型逆向完整工作流)/audit-tool-output(56→140:四工具字段映射+统一 schema)/event-library(49→130:逐事件字典+同意降级)/serp-feature(82→161:九特征触发×优化对照表+波动指数)。
  Thin-file deepening: 11 files under 70 lines all expanded to 120+, with 2026-10 verified facts (Discover Follow removed, UCP Hub live, AIO CTR -58%).

## 0.24.0 - 2026-10-09

- **多语言 9.5 冲刺轮(6 agent:S1 深挖+S2 实测+S3 节奏+S5 工具修复)**:
  - **S1 薄市场深挖(9 市场)**:vi/th/pl/nl/it/tr/id/hi/es 门户页各扩 30-50 行+关键数字一手源双核(更正:泰国原 54/38/7 份额系误引印尼列;印度 Bain 80/60 实为美国样本;土耳其 Yandex 26%=12 月均值含伪影→**实操判决:预算按 3-5%,终裁下放客户引荐数据**;hi 补泰米尔/泰卢固六段展开);
  - **S2 真实站验证(18 市场×2 站×3 工具=108 次实测)**:全部门户页新增「本地实测(2026-10-09)」节。结构性发现:**欧陆大报 3/4 封 AI 爬虫 vs 巴西/埃及头部开放**;知乎全禁 AI 检索 vs 淘宝全放行;Naver robots 整站禁一切爬虫只 Allow /$;youm7 是八站唯一真 llms.txt;Etsy 403 墙后仍有真 llms.txt;kompas 封全部 AI 爬虫 vs detik 不封;
  - **S3 复核节奏**:18 市场 markets.json 全部加 review_cycle(90 天/各自信号源/next 2027-01-09);门户页尾部维护节;
  - **S5 工具盲区修复(7 项)**:title 吞 JSON-LD(50 万字符假 title)/泰文字素/天城文词数恒 0/越南波兰变音切碎/土耳其 İ/--market 接线 markets.json 阈值(18 市场按单位判定)/微信 itemprop 仅 zh——**golden tests 32→46 全绿**;
  - RU 实测发现的 stdlib robotparser 误报(Disallow:/? 被当整站禁)已记录为已知边界。
  Multilingual 9.5 push: 9 thin markets deepened with dual-source verification, 18 markets × 2 real sites × 3 tools = 108 live audits written back into portals, review cycles for all 18, 7 tool blind-spots fixed (tests 32→46).

## 0.23.1 - 2026-10-09

- **S2 实测工具盲区修复轮(9.5 冲刺自动化提升)**——7 项,site_audit.py 重写 + head_check.py 中文场景门控,golden 测试 32→46 全绿:
  - **site_audit title 解析吞 head 内 script/JSON-LD(最高优先)**:HTMLParser 的 title 收集改为只在 `<title>…</title>` 内——此前 title 开启后 head 内全部裸文本(含 JS/JSON-LD)被拼进 title,6+ 站触发 2-75 万字符假 title;连带修复 title 内空白被丢导致的词粘连;
  - **泰文字素计长 + 泰文词数**:wc() 与 title/desc 长度接入 grapheme 近似(unicodedata.combining==0 且非 Mn/Cf,同 markets.json units 口径)——码点计长高估 30-50%、词数恒 0 双修复(实测 20 码点→14 字素);
  - **天城文(印地)词数计 0**:wc() 对 Devanagari 块(0x0900-0x097F)按字符计(同 CJK 口径);
  - **越南/波兰变音词被 ASCII 正则切碎**:wc() 词字符从 `[A-Za-z0-9']` 泛化为一切 Unicode 字母的连续段——拉丁扩展(0x00C0-0x024F 波兰/土耳其 + 0x1E00-0x1EFF 越南)之外连带修复阿文/俄文/希腊/希伯来整段记 0(youm7 实测 141→2204 词,假 soft-thin WARN 消失);
  - **土耳其 İ 双码点**:wc() 先 replace('İ','i') 再清洗 U+0307(casefold 前替换口径,同 keyword_variants canon 链),分解形 I+U+0307 不再把一个词劈成两个;
  - **--market 接线 markets.json**:title/desc 阈值不再硬编码(ja 32/120 全角),按市场单位(chars/fullwidth/grapheme)判定,18 市场全量可用,未知市场列出可用值退出;
  - **微信/QQ itemprop WARN 跨市场噪音(head_check)**:仅 zh 市场(新增 --market 参数)或检出中文内容时报——日文页满篇 kanji 但有假名即判日文跳过(note.com 实测 INFO 跳过;--market zh 仍可强制);
  - golden 测试新增 SiteAuditTests(9)+ HeadCheckChineseScopeTests(4)+ 全字母文字(1),零网络;
  - 真实验证:note.com(--market ja)title「note ――つくる、つながる、とどける。」18/32 全角、desc 109/120;youm7.com(--market ar)title「اليوم السابع」12/60、desc 120/155、JSON-LD 1、词数 2204。
  S2 field-test blind-spot fixes: title no longer swallows head scripts/JSON-LD; Thai grapheme length + word count; Devanagari per-char words; Unicode-letter word runs (vi/pl/ar/ru); Turkish İ fold-before-casefold; --market wired to markets.json thresholds; WeChat/QQ itemprop WARN gated to zh/Chinese content.

## 0.23.0 - 2026-10-09

- **六缺口补全轮(审计驱动)**——5 个新模块:
  - **[cwv-playbook.md](skills/seo-suite/references/technical/cwv-playbook.md)(264 行)**:四指标全景(五数据源选型)/INP 三段归因修法+scheduler.yield 兼容性红线/CLS 动态注入预留/第三方 ABC 三档治理/**GSC Page Experience 报告 2024-11 已移除**/优化优先级决策树;
  - **[mobile-seo.md](skills/seo-suite/references/technical/mobile-seo.md)(228 行)**:移动优先 2024-07 起 Google 只抓 smartphone UA(桌面独有内容=不存在)/平价四法/Mobile Usability 报告已退役/AMP 迁移 7 步/slow-4G 基线/15 项审计清单;
  - **[penalty-recovery.md](skills/seo-suite/references/monitoring/penalty-recovery.md)(262 行)**:**11 类手动动作全表**(含 SRA/scaled content)×触发×识别/三证据轴鉴别法/reconsideration 六要件+文书骨架/**disavow 2026 收紧至两情形**/负面 SEO 威胁重估(被黑>链攻)/九场景恢复周期数据;
  - **[redirects-canonical.md](skills/seo-suite/references/technical/redirects-canonical.md)(246 行)**:五类型重定向边界+链式形态修法表/**canonical 六场景**(分页 2026 共识=自引用)/冲突矩阵 11 行(canonical+noindex 官方禁用)/facet 四层决策树+参数白名单;
  - **[ugc-site-search.md](skills/seo-suite/references/content/ugc-site-search.md)(222 行)**:UGC 双刃四层差距(Reddit 赢在机制非偏好)/技术治理(验证才索引)/Reddit·Quora·知乎排名机制翻译表/内部 SERP 默认禁+四条件放行/零结果查询=内容缺口挖掘。
  Six-gap completion: CWV playbook, mobile SEO, penalty recovery (11 manual-action types), redirects & canonicalization (6 scenarios + conflict matrix), UGC + site-search dual module.

## 0.22.0 - 2026-10-09

- **新增 [域名策略](skills/seo-suite/references/research/domain-strategy.md)(279 行,用户指出缺口)**:七节——选域(TLD 官方口径:ccTLD 锁国/.com=新 gTLD 中性;EMD 三处残值;五步选域工作流)/域名历史与风险(**2024-03 Google 把过期域滥用写成显性垃圾政策**;七步尽调+四档判定;301 衰减数据表 90-99%)/域名迁移完整 checklist(预热/映射/一次 vs 分批/切流日动作/180 天窗口/六大死法)/国际域名架构(五国本地域名特殊要求+IDN punycode 陷阱)/品牌与 AI 引用(**AI 记品牌不记 URL:引用品牌名重叠 14% > 域名 4.4%——换域策略直接改写**;邮件域 warm-up)/技术细节(www 一致性/DNS/注册商迁移)/误区对照(品牌域 vs 关键词域 ROI 六维)。
  Domain strategy module: selection/history-risk/migration checklist/international/brand-AI-citation continuity/technical/myths.

## 0.21.0 - 2026-10-09

- **三个维度补全(用户指出的缺口)**:
  - **[站型打法手册](skills/seo-suite/references/overview/site-type-playbooks.md)(新,345 行)**:8 种站型(SaaS/电商 DTC/媒体/本地/文档/工具/Marketplace/YMYL)各一张打法卡——页面清单/Schema 组合/核心 KPI/获取重点/典型死法/pSEO 机会,带 2026 基准(SaaS trial 转化中位 1.5-3%/Discover 占出版商 30-50%/YMYL 匿名作者无权重 2026-08 确认);
  - **[pSEO 完整作战手册](skills/seo-suite/references/technical/programmatic-seo-playbook.md)(新,254 行)**:九章生命周期——模式发现正则表/数据层三级合规/URL·facet 架构/模板防 doorway 工程/内链规模化/索引与抓取预算(500 页探测期应对)/质量风险/ cohort 测量与 90 天处置阶梯/**四案例当日 sitemap 实测**(Wise 13×50K/Zapier 三层漏斗/Nextdoor 四级/Webflow 10 万 UGC);
  - **[站群与多站策略](skills/seo-suite/references/research/site-networks.md)(新,259 行,教育·防御视角)**:五级光谱(合法多站→卫星→寄生→PBN→泛站群)×SpamBrain 三层检测/多站架构决策树(默认子目录)/四市场站群实况(中泛站群+清风·俄 Минусинск·日终结论·英 PBN)/风险量化(恢复 3 月-1 年+网络联坐)/**六目标灰帽→白帽等效对照表**/存量站群四层指纹审计清单。
  Three dimension fills: site-type playbooks (8 cards), full pSEO playbook (9-stage lifecycle + 4 case studies), site-networks module (spectrum/decision tree/per-market/white-hat alternatives).

## 0.20.0 - 2026-10-09

- **新增 [站群与多站点策略](skills/seo-suite/references/research/site-networks.md)**(教育性/防御性,不提供规避检测指南):**六级光谱**(合法 ccTLD 网络/加盟多地点/品牌矩阵→卫星站→寄生→PBN→泛站群/doorway/链接轮,每级特征×动机×SpamBrain 三层检测)+伪装话术识别;**多站架构决策树**——权重聚合 vs 风险隔离权衡表、ccTLD/子目录/子域对照、反向拆分仅三种正当情形、四种误判;**四市场站群实况**(百度泛站群+清风/AI 低质专项、Yandex сателлиты+Минусинск 滤镜口径未换代、日语区卫星站终结论引用、英文区 PBN 市场化+忽略/降值为主);**风险量化**——恢复期 3 个月–1 年/Yandex 滤镜 6-12 月/传染性网络联坐/**SRA 2026-08-30 EEA 分叉核实**(EEA 内板块独立排序替代降权)+处罚模式速查表;**白帽等效对照**(6 目标×灰帽×白帽)+时间维度财务对照;**存量站群审计**——前置三问+四层指纹(WHOIS/基础设施/内容/链接)+A-D 分级处置+六件交付物。与既有卫星站定论/寄生分层/换城测试只引用不复述;backlink-directory 头部已加链接,SKILL.md 外链节已注册。

## 0.19.0 - 2026-10-09

> 0.11.0–0.19.0 发版时没写条目,以下 9 条于 2026-10-15 按各 tag 的提交说明补写。

- **大规模并行轮**:33 个仓库 agent 新增 agent-protocols、audit-rule-catalog、naver-searchadvisor、head-elements、serp-data-models、geo-evidence-bank、local-grid-ranking、scoring-calibration 等模块,并深化 37 个既有文件;18 个语言 agent 各写一个市场门户页(母语一手调研);markets.json 合并到 130 条 special checks。
  Massive parallel round: new modules (agent-protocols, audit-rule-catalog, naver-searchadvisor, head-elements, serp-data-models, geo-evidence-bank, local-grid-ranking, scoring-calibration), 37 files deepened, one portal page per market (18), markets.json at 130 special checks.

## 0.18.0 - 2026-10-09

- **深度吸收轮**:5 个 agent 小组读开源仓内部实现(不止 README)后写入套件——三套站点级评分体系并列对照、seo-ops 30 项检查、next-seo 15 个组件字段级说明、react-snap 预渲染流程、nuxt 内容协商状态机、NEO 测量协议、Grokipedia 字段级打法、Impact×Confidence 公式;18 个语言的定向分析(渠道/机制/信源/红旗),markets.json 为 18 个市场补 special_checks。
  Deep-absorption round: repo-internal reads written into the suite; 18 per-language analyses and special_checks for all 18 markets.

## 0.17.0 - 2026-10-09

- **可执行层扩到 33 个内置脚本**(4 个 agent 小组并行):审计组(sitemap 六桶 + lastmod 取证、hreflang 集群矩阵、首屏 5 秒测试、质量评估)、GEO 测量组(citation panel 带 Wilson 置信区间采样纪律、fan-out 三桶、CORE-EEAT 机检、CITE 域评级)、多语言实现组(markets.json 18 市场数据层 + 全角/字素校验、关键词变体归一、支付意图标注、SERP 占位、本地格式)、归因管线组(DiD、SEO 与 Ads 四桶对照、YouTube 离群、趋势侦察、freshness、报告生成);SKILL.md 第 7 节改为 33 个脚本的完整路由。
  Executable layer expanded to 33 built-in scripts across audit, GEO measurement, multilingual and attribution groups; SKILL.md section 7 routes all 33.

## 0.16.0 - 2026-10-09

- **归档层换成内置可执行脚本**:移除 0.15.0 的 mining-archive 层,新增 7 个纯 stdlib 工具(site_audit 全套阈值、robots_posture 三级矩阵 + Cloudflare 注入检测、text_metrics 节拍/slop/水印检测、gsc_mining 读 CSV 导出、schema_lint 实体规则、llmstxt v2 校验/检查/生成、serp_overlap 四分位);SKILL.md 第 7 节改为脚本路由,全部冒烟通过。
  Archive layer replaced by 7 stdlib-only scripts; SKILL.md section 7 rewritten as script routing.

## 0.15.0 - 2026-10-09

- **mining-archive 层(已在 0.16.0 移除)**:100 仓深扫的逐仓提取笔记归档进套件(索引 + 6 个批次文件)并接入 SKILL.md。
  Mining-archive layer for the 100-repo deep scan (index + 6 batch files); removed in 0.16.0.

## 0.14.0 - 2026-10-09

- **满载轮**:100 仓深扫剩余的高价值条目并入 12 个文件——渲染三件套细节、Indexing API 状态机、三个生产级评分器、14 个少见 JSON-LD 字段、内容协商实现、审计 JSON schema + 预注册校准 + 文件治理、AI 引用五层面 + 提示词分类、归因模型表 + 报告工程约束、GEO 难度公式、寄生 SEO 分层、中国获客渠道、邮件认证信任信号。
  Full-load round: remaining high-value items from the 100-repo deep scan merged into 12 files.

## 0.13.0 - 2026-10-09

- **100 仓深扫重做**:20 个 agent 各读 5 个仓的完整文件,带行级阈值;并入 10 个文件——YouTube CTR/AVD 基准、ARP/ATRP/SoLV 网格定义、fan-out 三桶 + SOV LVCF + Bray-Curtis、英文 slop 特征全表、CORE-EEAT 80、seonaut 70 项阈值表 + head 白名单 + C26 移除顺序、五层流量诊断 + DiD 参数、SERP 重叠四分位 + CTR 曲线、llms.txt 语料证据 + Google 反证链、欧盟 AI 法案第 50 条速查卡。
  100-repo deep scan redone (20 agents × 5 repos, full-file reads); merged into 10 files.

## 0.12.0 - 2026-10-09

- **100 仓扫描**:分四批逐个阅读 100 个最热门的 SEO/GEO 开源仓(53.8k–397 星),要点并入 8 个文件(llms.txt v2、AIV 评分 v1.1 带 Wilson 置信区间采样纪律、seo-ops 少见判断方法、证据新鲜度登记、度量定义层、Unicode 水印清除清单、对照组归因 + 部署回归检查、SEO 与 Ads 四桶合并);登记 6 个新能力缺口。
  100-repo scan: the 100 most popular SEO/GEO repos read in four batches; top items merged into 8 files; 6 capability gaps registered.

## 0.11.0 - 2026-10-09

- **合规 + 可执行层起步**:SKILL.md description 压到 918/1024 字符并加 Not-for 条款;新增 scripts/(self_check 评测、link_check、text_units 市场单位换算);新增 examples/ 关键词研究黄金样例。
  Compliance + executable layer: description at 918/1024 with a Not-for clause; scripts/ (self_check, link_check, text_units); gold-standard keyword-research example.

## 0.10.0 - 2026-10-09

- **新增 [图片与视觉搜索 SEO](skills/seo-suite/references/content/image-search-seo.md)**(补图片层空白):Lens 月 ~200 亿(官方)+SC multimodal 过滤器(2026-09-24);**Backlinko 65,388 次 Lens 实证:alt 匹配仅 11.4%、与文字前 10 重叠仅 15%——视觉搜索是页面级 SEO 不是元数据游戏**;AIO 引用图只认已索引页的 `<img src>`(CSS 背景图永不索引)与首选图三信号;EXIF 官方明确不用;中国拍立淘/韩国 Naver 购物 Lens;Getty 商标索赔存活+TDMRep/Cloudflare 控制层。
- **新增 [Discover 与新闻 SEO](skills/seo-suite/references/content/discover-news-seo.md)**:官方定位"补充渠道不作为基线";**2026-02 首个 Discover 专属核心更新(本地化+反标题党)对跨境出版商的冲击**;Follow/RSS 依赖;大图规范;Publisher Center 关闭后算法化收录;48h news sitemap;**日本新闻域名 2026-09 跌出 AI 引用总榜(百科/辞书压制)+79% 大新闻站屏蔽 AI 训练爬虫+Cloudflare Pay-Per-Crawl——新闻 GEO 从开放索引转向商业授权**;8 项实操清单。
- **输出模板全面升级(14/14)**:七段式交付结构(借鉴 tronghieu insight-report/TerryFYL 学术三段/AgriciDaniel 数据新鲜度注记)——**标题=答案本身**、The answer 一段独立成立("只读这段的人不会错")、关键数字区带阈值、Evidence/Confidence 列、量化选项表(选择权在 owner)、**"What could change this conclusion" 节**(数据缺口/相关非因果附定案实验)、方法附注(数据源+抓取时间+已知坑);两个示范模板(keyword-research/full-seo-audit)全文重写,其余 12 个追加通用三节;[要追加]/[INVULLEN] 占位协议贯穿。
  Image/visual-search SEO + Discover/news SEO + all 14 templates upgraded to answer-first deliverable structure.

## 0.9.1 - 2026-10-09

- **基线拉平轮(baseline parity)**:审计发现 12 个能力文件仍是英文默认(title/meta 公式、可引用性打分、引用模式、审计评分、实体信号、知识图谱、GA4、内链架构、链接质量、外联、内容模式)——全部补上「市场差异」节:
  - title-formulas:各语言标题长度单位表(日 32 全角/泰字素/德 55–65/越词进前 30/阿 +20% RTL);
  - meta-tag-formulas:各语言 meta 长度+本地格式(法 U+202F/德数字/印尼前 120 字符安全区);
  - citability-scoring:**134–167 词是英文衍生值**——按等价信息量给中/日/泰/俄/印尼/韩换算表;
  - ai-citation-patterns:各市场引用模式(日 9,891 引数据集/土 75.3% 绑定/印尼意图分流/意 Wikipedia 48.67%/韩 70% UGC);
  - scoring-rubric:审计阈值换算表(句长/内链量/营销词/全角);entity-signal:实体源按市场(韩 연관채널/俄 ИНН/意 P.IVA/巴 CNPJ/荷 KvK);knowledge-graph:各引擎实体层;ga4:测量栈市场表(Metrica/Matomo/Piano+判例);link-architecture:日本流 noindex 惯例;link-quality:八市场红旗;outreach:渠道与语域;content-patterns:结构惯例。
  至此全部能力文件与英文基线对齐——英文仍是默认层,但每个文件都知道自己的规则在哪個市场要换。
  Baseline parity: all 12 English-default files gain market-difference sections — every capability file now knows where its rules change by market.

## 0.9.0 - 2026-10-09

- **本地社区深挖轮(17 市场逐一,本地语言检索圈源:searchengines.guru/habr/r10.net/Pantip/Connect.gt/ABAKUS/brunch/站长圈/cmlabs/Frankwatching 等)**:主干新增「本地社区与信息源索引」——每市场的圈内信息源、本地独有共识(带数值与日期)、国际圈误解纠偏。要点:俄 76 条商业因子六块清单/区域 lr 码(位差 40 位)/AI 直接流量仅 0.02-0.25%;韩发帖时刻表/保存付费市场/GPS 实访 리뷰 政策;日内链数值惯例(3000 字 4-8 本/45 本上限)/GBP 投稿日历/MEO 与 SEO 十倍价差/民间 9,891 引用数据集(4 引擎域名重复仅 ~10%);中百度收录现役三通道/5118 MCP/假权重红旗/公众号入池;西外链商品化价目/拉美 WhatsApp 转化按钮;巴 ML 五支柱/IG DM 自动化;德月租链接+Abmahnung/横幅判例;法 AIO 晚德一年=红利窗口/Piano Analytics;印尼廉价服务真相;印三层外包/Discover>Search;意 guest post 价带;土 tanıtım yazısı 市场/UGC 五霸;越 backlink báo 产业/Cốc Cốc 双口径;泰 Pantip 双角色/หลังบ้าน 红线;波 Allegro 参数月更;荷 .nl 权威链原则。
- **backlink-directory 新增 14 市场本地外链价带与风险表**(越南 1,500 VND/条→西语大媒体 5,000€;每市场的红旗与合规买法);**ecommerce-geo-ladder 新增七大 marketplace 站内 SEO 分叉表**(ML/Trendyol/Allegro/bol/Shopee/Tokopedia/Salla);**serp-feature-taxonomy 新增各市场 AIO 覆盖时间线与 SERP 占位层/声誉层通用模式**;中文指南补收录加速三通道+5118 MCP+入池机制;intake 加外包价格锚与廉价服务红旗;**融合原则扩至 27 条**(新增:本地链接市场价/投诉平台声誉层/marketplace 独立学科/AIO 上线窗口)。
- README 双语能力表全面刷新至 0.9 全貌(视频/渲染/日志/电商/算法归因/persona 全部入表)。
  Local-community deep-dive round: 17 markets re-mined in native languages; community index, link-price bands, marketplace in-store SEO forks, AIO timelines, SERP occupancy layers.

## 0.8.0 - 2026-10-09

- **新增 [视频 SEO/GEO 指南](skills/seo-suite/references/content/video-geo-guide.md)**(补最大缺口——YouTube 是多市场 AI 引用第一源):AI 读视频的双通道机制(Gemini 进片内时间戳引用/ChatGPT 整片选择/关键帧+transcript);**播放量不是被引门槛,文本可及性才是**(被引视频 41% 播放<1,000);人工校对字幕是唯一可控层(captions API 官方仅所有者可取);key moments 两法;8 项视频 GEO 清单;五市场平台格局(**韩国 Naver TV 已关停只剩 YouTube;俄 VK Video/RuTube 日活反超 YouTube**);MLA 多音轨。
- **新增 [JS 渲染与 SPA SEO](skills/seo-suite/references/technical/rendering-seo.md)**:两波索引已死的新口径(官方已删);渲染队列实际行为(JS 站 9 倍抓取预算);渲染策略决策表;**meta 注入红线(社交与多数 AI 爬虫不执行 JS,69% 主流爬虫不渲染)**;五引擎渲染差异(**Naver 官方确认 Yeti 解析 JS 但建议 SSR;百度以站长平台抓取诊断实测为准**);SPA 审计 7 项+cloaking 红线+预渲染内容漂移风险。
- **新增 [服务器日志分析](skills/seo-suite/references/technical/log-analysis.md)**:日志是 AI 到访的唯一可靠测量层;DNS 双重验证法;AI UA 过滤+IP 段对照;**Bytespider 无视 robots 且伪装移动 UA,只能边缘封锁**;GEO 基线用法(到访≠引用);**a11y×SEO 三分法**(SEO 重叠项/纯人类项/agent 项——与 agent-readiness 呼应)。
  Video SEO/GEO + rendering/SPA SEO + log analysis: three gap-filling references.

## 0.7.0 - 2026-10-09

- **schema 富结果状态速查**(全量核对官方 changelog):已停展清单(FAQ/HowTo/Sitelinks searchbox/Practice Problems/2025-06 七类)+展示中清单(Product 字段演进至 2026-07、Review 收紧三连、JobPosting 未受限);三处澄清——LocalBusiness 无传统富结果、无 AI 专用 schema、**"Person 新增 alternateName"是误传**(官方 releases 页核实);申诉走 Spammy structured markup(只罚富结果不罚排名)。
- **算法更新归因层**并入漂移监控:官方六步归因流程(数据假象→形态→时间对齐→传感器→GSC 分层→等 1–2 周);2024–2026 时间线要点(reviews 更新 2024-01 后零次;2026 出现 Discover update 与 19.5 小时超短 spam;**2024-08 官方 ranking bug 证明事故与算法同流**);传感器现状(RankRanger 死亡/Semrush 2026-09 基线重算);**algorithm-updates 数据文件最小字段集**(含 bug_incident 类型与 source_tier 降权)+漂移联动规则(窗口交集→"疑似算法"标签);跨市场可观测性(Yandex 官方公告/Naver 无看板/Bing 无公告流)。
- **SXO/persona 层**(深读 claude-seo seo-sxo + marketingskills customer-research 还原):意图×persona 映射(SERP 五信号推导 4–7 persona;页面 4 维×25 打分;证据面扩展含**信号源按市场替换**——中文=知乎/小红书、韩=카페、日=知恵袋);persona 卡加 locale 字段(本地信任偏好);IST/SOLL 对比骨架+超具体占位符纪律+"页面可以是错页型"判定;intake 加 persona 证据闸门。
  Schema rich-result status audit + algorithm-update attribution layer + SXO/persona layer (market-neutralized).

## 0.6.2 - 2026-10-09

- **AI 味检测的市场差异层**:ai-writing-detection 新增各语言 AI 味标记表(日 28 动词×14 构文/巴西 35 型/印尼 hiruk pikuk 禁用/波兰 humanizer/越南句长方差/中文营销词)——"检测密度而非误用"原理落地,原则 #12 的实体化;跨语言通用信号(句长方差/结构平行)与母语者标注维护纪律。
  Per-language AI-flavor marker tables — principle #12 made concrete.

## 0.6.1 - 2026-10-09

- **新增 [电商 GEO 阶梯](skills/seo-suite/references/content/ecommerce-geo-ladder.md)**:五级阶梯(L1 产品数据→L5 agent 交互,逐级验收)、Product schema 七个高频错误(price 带货币符号即非法等)、七市场分叉表(印尼 AIO 直接引 marketplace 页/土耳其 marketplace 仅占 AIO 引用 2.5%/俄罗斯低优先级)、AI 购物现状(ChatGPT Instant Checkout 已 2026-03 退役;"AI 管发现、商家管结算")、**UCP(Google 主导,~50 家背书)与 ACP(OpenAI+Stripe)双协议对照**与 L5 实操入口(Shopify/ucp-cli)。
- **本地 SEO 六行业速查表**并入 site-type-templates(餐饮/医疗/法律/家居/教育/汽车×平台要点/评价合规红线/schema 正解/常见错误;`DrivingSchool` 在 schema.org 不存在已验证;三深例:日本医疗广告禁止项/韩国 리뷰 政策/德国 Handwerkskammer)+评价生态第二平台按市场(俄=Google 停发评→Yandex 系)。
- **中文指南二轮核验(11 处修订)**:发现并接入新持续数据源 [ZhiMaHang/chinese-ai-engine-sources](https://github.com/ZhiMaHang/chinese-ai-engine-sources)(45 题×12 引擎按月快照,issue-11=13,203 引用);"知乎修正"改判"引擎分化"(文心 #3/DeepSeek #4 实引);豆包 7 月信源池改版(第三方 32%→7%,抖音绝对主导);百度"三件套"改"双前提"(知道降级,无独立 App→文心助手 2.0);元宝新 #2 信源 ima.qq.com;搜一搜 2026 新口径(8 亿 MAU/15 亿日均);DeepSeek 2026-05-29 修改/重生成新限制;Kimi 三方分歧带日期引用。
  Ecommerce GEO ladder + local six-vertical table + Chinese guide second-pass verification (new monthly dataset wired in).

## 0.6.0 - 2026-10-08

- **模板市场化(架构落到输出)**:全部 14 个输出模板(research 6/audit 4/monitor 4)加目标市场字段或市场专属行——引擎面提醒(俄/土=Yandex、韩=Yeti、日=Bing 必查、越=Cốc Cốc)、市场阈值(日语全角/泰语字素)、逐市场分列纪律;多市场站逐市场各出一份报告。
- **新增 [Agent-Readiness 操作层](skills/seo-suite/references/technical/agent-readiness.md)**(吸收英文区 seo-agentic 五件+specification.website):ARD 三级发现链实操(Agentmap/ai-catalog.json 写法)、WebMCP registerTool 模式与表单声明式写法、Web Bot Auth 签名(ChatGPT-User)、Lighthouse AGENTIC_BROWSING 七审计解读、语言中立层的多语言部署(每 locale 一份目录)、就绪决策表(英文站全开/其他语区 llms.txt 等价物的分叉立场)。证据约束:协议层无引擎宣布消费,定位为低成本期权。
  Templates gain the market dimension; new agent-readiness reference absorbs the English protocol layer.

## 0.5.3 - 2026-10-08

- **跨区迁移矩阵**:11 组"源方法→可迁移市场+迁移条件"(生态内搜索打法/投诉平台引用源/AI 臭 lint/快照缺口诊断/音译聚类/超级 App OG/官方注册竞品链/提问式 H2+质量门/SoV 计量/主权助手/目录引用源)——迁移后必须本地实测。
- README 双语更新至 0.5 系列全貌(双维度架构+独到方法索引+融合 23 条);仓库描述同步。
  Cross-region migration matrix (11 method-transfer pairs) + README sync; the v0.5 long chain is complete.

## 0.5.2 - 2026-10-08

- **第三波长链路深挖(长尾七市场,每市场单独 agent 母语挖掘)——十八市场全覆盖完成**:
  - **印地/印度**:GSC regex 快照缺口修复法(英文页在 Hinglish 查询排首页但 CTR 0.16% 的零成本机会);JioHotstar×OpenAI 超 App 内 ChatGPT;JustDial/IndiaMART 目录=GEO 引用源;语音助词词库;拼写漂移聚类;Sarvam MCP;
  - **意大利**:P.IVA→Registro Imprese 竞品链(增值税号→ATECO→真实竞品,公开 API 独有);意语 AI 引用=Wikipedia 48.67%+个人专家站第三(Aranzulla 模式);4 星>5 星信任悖论;
  - **土耳其**:**Yazeka**(土语专属 AI 答案,非 YandexGPT);**AIO 引用 75.3% 绑定自然前 10**(vs 美国 37%——美式结论不可平移);Wordstat TR 上线;Zemberek 黏着语工作流;**份额口径冲突并记**(StatCounter 26% vs 本地机构 3–5%);
  - **越南**:t0mmy 99 条规则(提问式 H2≥50%、密度上限 1/150、nonce 双层质量门);Coc Cốc 官方偏好越南语+.vn;句长方差检测;
  - **泰国**:`Intl.Segmenter("th")` 分词定论(**全球主流 SEO 工具栏在泰文站全部错误**);grapheme 字素计数;泰调可读性公式;Wongnai/Pantip 本地信号;PDPA;
  - **波兰**:Bing 桌面 ~13.3%(全球 3 倍)必做;品牌引用按引擎分列(ChatGPT PKO vs Gemini mBank);URL 转写六机构共识;
  - **荷兰/弗拉芒**:je/u tone 双轨;>60% 网民用 AI(欧洲最高档);[INVULLEN] 占位制;KvK 一致性;垂直行业本地页模板模式。
- 独到方法索引十八市场全部填实;**跨区融合原则扩至 23 条**(新增:官方注册竞品链/分词字素基建/质量门防自评篡改/快照缺口诊断法/**口径冲突并记纪律**)。
  Wave 3 completes 18-market coverage: HI/IT/TR/VI/TH/PL/NL, each with its own native-language agent.

## 0.5.1 - 2026-10-08

- **第二波长链路深挖(方言/文字机制六市场,每市场单独 agent 母语挖掘)**:
  - **西语**:审计报告翻译层(四段式+行业类比库,731 审计校准);GEO 五维评分带西语 NLP 特征(¿...? 疑问式 h2、information gain ≥3 数据点);es-US 集体代搜(81%);支付即意图词层(OXXO/cuotas/contra entrega);半岛偏置对抗;**es-419 口径冲突并记**(Google 官方文档列为支持值 vs 从业者报告解析器不认→双保险写法);
  - **葡语(巴西)**:Reclame Aqui 三重角色(22.3% ChatGPT 品牌回答被引/关键词语料/信任信号→SAC 成为 GEO 手段);WhatsApp 官方发现层(Status 广告+Canals);E-E-A-T 巴西化(OAB/CRM 注册号);pt-BR 反 AI 35 型;AO90 正字法;季节日历;
  - **阿拉伯**:品类×语域矩阵;文化日历闸门(Ramadan 发布窗口);50 查询×14 天重测协议;RTL 审计深化(bidi 隔离/数字方向/镜像例外/字体 preload 陷阱与 CLS);内容鸿沟 0.6% vs 5.2%(W3Techs,禁用无出处的"3%");合规预审(GAMR/TDRA);
  - **德语区**:Ansprache/Tonalität 拆两字段;Sistrix 锚点(AIO 覆盖 20%/Pos.1 CTR −59%/月损 2.65 亿点击)与 Bitkom AI 使用数据;GSC 免 consent 基准+consent rate 并列的报表结构;德国官方机构作为 GEO 引用源优先级;
  - **法语**:**Vibe(ex-Le Chat)单独优化**(MistralAI 三爬虫分工+AFP 通稿信源+22.9% unique 推荐);Bill 96 实操(无规模豁免/等效可见性/罚则);魁北克 vs 法国官方术语库词汇表;非洲法语区(塞内加尔桌面 Bing 9.2%);法国 9 层目录+实体简介逐字重复;AIO 法国 2026-07-22 上线口径修正;
  - **印尼语**:AIO 触发率 37.2% 全球第一;引用格局实测(YouTube 12.7%/社交视频 30.7%/电商平台被引/品牌词官网 72.2% 出现率);"关键词跟手指、正文跟词典"三区操作律+五档 ragam;"hiruk pikuk"slop 禁用;slow-4G 测试基线;双雄+TikTok 分流。
- 独到方法索引补六行;**跨区融合原则扩至 18 条**(新增:Reclame Aqui 等价物/反 AI 文案本地化桥/正字法改革分裂/主权助手模式/语域双轨模板/职业注册号/支付即意图/本地引擎 watch 列表);MistralAI 三爬虫与过时 token 表进爬虫政策;hreflang es-419 冲突并记;六市场目录渠道;intake 六市场闸门。
  Wave 2: six dialect/script-mechanism markets, each with its own native-language agent (ES/PT-BR/AR/DE/FR/ID).

## 0.5.0 - 2026-10-08

- **架构重构:市场成为一等维度(市场 × 能力双维度)**。SKILL.md:intake 市场先行(18 市场第一必答字段)、统一输出首行注市场、新增「市场维度」运行方式;capability-map 双维度结构+市场分层表(独立学科/ChatGPT 超强/方言分裂/合规驱动/基线);routing-rules 新增「第零步:先定市场」;统一各能力文件「市场差异」小节命名约定。
- **第一波长链路深挖(独立学科五市场,每市场单独 agent 母语挖掘)**:
  - **中文**:新增「生态内搜索速查」(搜一搜 Peoplerank/小红书 CES 互动分/抖音四因子/知乎引证与 2026-08"知乎修正"/豆包信源金字塔与 2–4 周验收窗/采样风控 ≤20 问);排行站免费申报通道(maigoo/CNPP 官方口径);新库:geo-book(一手实测)、AIGEOTOOLS(175★)、deepseek-geo(118★)、douyin-seo-playbook;
  - **英文**:协议层 agent-readiness(ARD 三级发现链/WebMCP/Web Bot Auth/Lighthouse AGENTIC_BROWSING);引用四级阶梯+recommended-against 暗级;ChatGPT 5.6 格式降权(listicle −50.5%);AIO 与 AI Mode 86% 引用不同源;Cloudflare 托管 robots 坑;fan-out 逆向;新库:marketingskills(53.7k★)、open-seo(22.7k★)、jdevalk/specification.website(874★)等 12 库;
  - **俄语区**:Telegram 公开镜像 SEO(t.me/s/ 被 Yandex 抓取,~90% 曝光来自 Yandex);Webmaster SoV 官方报告;Alisa RAG 五步+ЭПОС;商业透明层 6 类法定页;9 项官方违规+накрутка ПФ 红线;目录生态(Бизнес/2ГИС/Zoon/Flamp/Отзовик+TGStat);VK 群可排名;Horosheff 深读(行为代理 7 分制等 8 项新检查);
  - **韩语区**:`nosourceinfo`(全球唯一官方 AI 引用退出 meta);Yeti robots 语义四陷阱(5xx=全站封禁/host 隔离);연관채널 sameAs 实体图谱;AI 인용수 公开可侦察(메이트);웹문서/서비스内双通道;블로그 투트랙;官方 5 项引用标准+反模式;leopard627(707★)与 55 份官方文档蒸馏库深读;
  - **日语区**:全角阈值体系(title 32/desc 120/正文 300);「AI 臭」密度 lint(28 动词×14 构文);MEO 三因素×投稿週 1 回;2026-06 引用生态(note 第 2/新闻跌出/PR TIMES 特例/垂类>综合榜);卫星站终结论;業界ポータル NAP 一致;kseo/utsushi/seo-operator/hana652 深读([要追加]/[要確認] 占位符协议升为全区规范)。
- **主干新增「十八市场独到方法索引」**(第一波五行填实)+**跨区融合十原则**(封闭生态入口/SoV 计量观/断言半衰期/免费申报先行/行为代理审计/免责声明即 GEO 内容/密度检测/占位符协议/垂类媒体子表/互动分公式化)。
- monitoring/brand-mention 新增市场差异节(四级阶梯+各市场监控通道);backlink-directory 新增区域渠道节(中/俄/日+卫星站风险+链接红线);intake-checklists 四市场深化。
  Architecture: market becomes a first-class dimension (market × capability); Wave 1 deep-dives for the five independent-discipline markets (ZH/EN/RU/KR/JP), each with its own native-language agent.

## 0.4.1 - 2026-10-08

- **结构反馈落地:区域知识融入套件本体**。移除 0.4.0 的 `references/regions/` 独立专区(4 份指南),把内容并入五类能力文件——全球能力不再是一个模块,而是每个能力集合自带:
  - `overview/multilingual-workflow.md` 重写为**全球主干**:11 市场总表(格局/决定性事实/就绪闸门)、逐市场工具栈映射(俄/韩/日)、语言与内容规范(文字数按体裁、Sie/du、MSA/方言、baku/gaul、RTL、排版)、合规速查(152-ФЗ/erid、GDPR、LGPD、Bill 96、PIPA、ステマ規制);
  - `content/geo-platform-differences.md` 新增第六节**区域 AI 平台**(Alice/Neuro 取源规则、GigaChat 仅 App 内引用、Naver AI Briefing 只引自有生态、日语 AIO 76.9%、引用语言绑定 83–84%);
  - `technical/ai-crawler-policy.md` 新增第三节**区域引擎爬虫与收录**(YandexAdditional 唯一退出控制、Naver robots 收录、Bing 日本必做);
  - `technical/hreflang-validation.md` 修正规则五(**es-419 是 Google 接受的唯一 UN M.49 例外**)+ 新增 RTL 必检与常见市场码组合;
  - `research/keyword-intent-taxonomy.md` 新增**区域关键词研究差异**(Wordstat 算子、DataLab、ラッコ→Planner 管线、方言/语域/变体归组);
  - `overview/intake-checklists.md` 新增**目标市场 intake 闸门**(逐市场必答问题)。
- SKILL.md 路由改指向融入后的文件;README 双语同步("全球能力融在每个能力集合里")。
- **第二轮语区并入(18 市场全覆盖)**:印地(India,ChatGPT 第二大市场 ~1 亿周活;Hinglish 三种书写;hi-IN/en-IN 分开)、意大利(it-CH 独立 locale)、**土耳其(Yandex ~26%——俄语区之外第二个 Yandex 市场**,黏着语关键词形式)、越南(有调/无调变体+Coc Cốc ~6%)、泰国(无空格分词,密度工具失效)、波兰(变音符规范化)、荷兰(nl-NL/nl-BE 弗拉芒)——折入多语言工作流长尾市场表、爬虫政策(Yandex 土耳其/Coc Cốc)、hreflang 市场码组合、关键词区域表、intake 速查。
  Structural feedback: regional knowledge merged into the five capability files (regions/ section removed); multilingual-workflow rewritten as the global backbone; second round adds 7 more markets (18 total, incl. Turkish Yandex and Hindi/India).

## 0.4.0 - 2026-10-08

- **全球市场专区(regions/)**:新增 4 个区域指南,把套件从"中英双语"扩展为"全球 SEO/GEO 一把做,逐市场分开评分"——
  - **俄语区(Yandex 生态)**:平行工具栈映射(Webmaster/ИКС/Metrica/Wordstat/Business)、行为与商业排名因素、Королёв/Вега 算法、Alice AI 从自然 SERP 取源(经典 top-10 是引用前提)、YandexAdditional 唯一退出控制、llms.txt 在俄无消费证据、GigaChat 引用仅 App 内、152-ФЗ 与 ORD/erid 合规、15 项就绪清单;
  - **韩语区(Naver 生态)**:份额双口径(StatCounter 并列 vs 本土面板 63–64%)、Search Advisor 要点、C-Rank/D.I.A. 创作者排名、SERP 自有垂直主导、AI Briefing 几乎只引 Naver 生态(韩语 GEO=Naver 生态优先)、Coupang 商品搜索、Wrtn/ChatGPT 格局、14 项就绪清单;
  - **日语区**:Yahoo! Japan=Google 索引、Bing 在日 28–33%(喂 Copilot)、AIO 覆盖 76.9% 日语查询、LLMOチェキ >95% AI 证据来自第三方站、文字数按体裁分层(MEO 500–1,200/一般 1,500–3,500/支柱 7,000–12,000)、ステマ規制、Yahoo!プレイス 2027-03 EOL、14 项就绪清单;
  - **全球六市场(西·葡·阿·法·德·印尼)**:对照表(引擎份额/最大坑/hreflang)、es-419、pt-BR、RTL+MSA/方言分层(arXiv 同行评审:方言退化)、Bill 96、DACH Sie/du、baku/gaul 双轨、AI 引用语言绑定(西语 83–84%)、合规速查(GDPR/LGPD/Bill 96)。
  Four regional guides adding global market-by-market SEO/GEO in one pass: Russian (Yandex ecosystem), Korean (Naver ecosystem), Japanese, and a six-market comparative guide (Spanish/Portuguese/Arabic/French/German/Indonesian).
- **接线**:SKILL.md 新增「区域市场专区」路由与全球市场英文触发词(Yandex/Naver/MEO/es-419/pt-BR/RTL/Bill 96/Sie-du/baku-gaul 等);多语言工作流升级为全球市场路由表(九语区)+ 逐区可达性/es-419/逐引擎盲区;README 双语更新至 0.4.0 并新增全球市场数据表(均注明来源类型)。
- **修复**:消除 SKILL.md 中历史遗留的重复块(frontmatter/头部/整套路由规则各重复一次,475→260 行)。
- 所有事实按套件证据纪律标注来源类型(官方/行业/社区),未证实项在各文件末尾集中声明。

## 0.3.1 - 2026-10-09

- **多语言结构化**:SKILL.md 增加语言约定(输出随用户语言、多语言站逐版本评分)与英文触发词;新增《多语言工作流》参考(按市场路由、双语检查顺序、一套事实多种变体、中英阈值差异对照);README.en.md 更新至 v0.3 能力并加安装命令;README.md 同步。
  Multilingual structuring: language conventions in SKILL.md, new multilingual-workflow reference, EN README updated.
## 0.3.0 - 2026-10-09

- 第二轮新增 4 个参考资料:**中文 AI 搜索指南**(187,818 条引用实测:品牌官网仅占 1.37%、28 个排行站吃 9.1%、各引擎护城河、CJK 阈值、15 项就绪清单)、**程序化 SEO 闸门**(100/500 页硬闸、页型地板)、**SEO 漂移监控**(13 元素基线+17 规则)、**目录提交引擎**(九问闸门+13 层目录)。
  Round-2 additions: Chinese AI-search guide (measured citation economics from a 187,818-citation dataset), programmatic SEO gates, SEO drift monitoring, directory-submissions engine.
- 修复 0.2.0 中 SKILL.md 的 8 条死链;新增一行安装脚本 install.sh。
- 来源登记更新见 NOTICE。

## 0.2.0 - 2026-10-09

- 新增 8 个参考资料:外链画像分析(七段式框架+数据闸门)、外链渠道目录(分级+核验日期)、llms.txt 指南(格式+校验严重度)、AI 平台差异事实库(五引擎+爬虫分类)、可引用性打分(五维块级+就绪度分层)、AI 爬虫政策(引用型 vs 训练型 bot)、hreflang 八检、品牌提及监控(五平台加权+买家提示词集)。
  Eight new reference files: backlink profile analysis (7-section framework with a data-sufficiency gate), graded backlink directory with verification dates, llms.txt guide, AI platform differences fact base, citability scoring, AI crawler policy (citation vs training bots), hreflang 8-check validation, and brand-mention monitoring.
- 框架要点参考 AgriciDaniel/claude-seo、zubair-trabzada/geo-seo-claude、jianruntech/geo-score、Auriti-Labs/geo-optimizer-skill、flaqai/backlink_skills、alvinunreal/awesome-submitlist、indie-hacking/Awesome-SEO-Backlinks、OranAi/orangeo(均在各文件末尾附来源)。借要点摘要与原文链接,见 NOTICE。
  Framework points borrowed (summary + link only, see NOTICE) from the repos above.

## 0.1.0 - 2026-09-29

首个公开版本 / Initial public release.

- 一个 Skill:`seo-suite`(SEO / GEO 统一工作台),含 overview、research、content、technical、monitoring 五类参考资料和 14 个输出模板。
  One Skill, `seo-suite` (SEO / GEO workbench), with reference notes for five capability sets and 14 output templates.
- 参考资料为 EveryInfra 自行编写;涉及第三方来源的文件只给要点摘要和原文链接,见 NOTICE。
  Reference notes are written by EveryInfra; where a third-party source is involved, only our summary and a link is given. See NOTICE.
