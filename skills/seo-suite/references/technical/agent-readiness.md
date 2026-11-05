# Agent-Readiness 操作层(协议时代的站点准备)

> 用途:让站点能被 agent 发现、读懂、调用和识别。协议本体以 [agent-protocols.md](agent-protocols.md) 为准(下文「第 N 卡」);本文只写部署决策和验收。UA 表见 [AI 爬虫政策](ai-crawler-policy.md)。事实核对 2026-10-18。本层是低成本期权,不是已验证的引用杠杆(本套件口径,证据见第七节)。
> **分叉决策(本套件口径)**:英文目标站全开本层;其他语区只保留 llms.txt 类等价物(未见百度、元宝、豆包官方支持这些协议),见 [多语言工作流](../overview/multilingual-workflow.md)。

## 一、ARD 发现链(Agentic Resource Discovery)

- Google 于 2026-06-17 [宣布](https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/),Microsoft、Hugging Face 等参与;数据模型沿用 Linux Foundation 下 AI Catalog 工作组。规范 [v0.91](https://agenticresourcediscovery.org/spec/)(2026-08-26,Proposal)。
- 发现机制(§5.1):`/.well-known/ard.json` 和 `<link rel="ard">`(消费方 MUST 处理);robots.txt `Agentmap: <URL>`;页内 JSON-LD;DNS。
- `/.well-known/ai-catalog.json`、`rel="ai-catalog"` 是前身名字,消费方只是 MAY 查;只放旧路径可能不被发现。Lighthouse 13.6.0(2026-10-27)起按 ARD v0.91 改读 `ard.json`(Link 头、`<link rel="ard">`、`/.well-known/ard.json`),只在旧路径会报警告;Hugging Face 等目录仍只发 `ai-catalog.json`。两条路径发同一份文件(本套件口径)。条目字段见第 2 卡。

## 二、WebMCP(页面级工具注册)

- W3C WebML CG 草案([规范](https://webmachinelearning.github.io/webmcp/));Chrome origin trial M149–M156([chromestatus](https://chromestatus.com/feature/5117755740913664));WebKit oppose([#670](https://github.com/WebKit/standards-positions/issues/670)),Mozilla neutral([#1412](https://github.com/mozilla/standards-positions/issues/1412))。
- 命令式 `document.modelContext.registerTool()`;声明式 `<form toolname tooldescription>`,agent 提交时 `SubmitEvent.agentInvoked` 为 true([Chrome 文档](https://developer.chrome.com/docs/ai/webmcp/declarative-api))。细节见第 5 卡。
- 权限:`tools` Permissions Policy,默认 `self`;跨源 iframe 加 `allow="tools"`;全站禁用发 `Permissions-Policy: tools=()`。
- 消费者:有官方文档的只核到 ChatGPT 桌面应用内置浏览器 [Site tools](https://learn.chatgpt.com/docs/webmcp)。它只认顶层页面的命令式工具,不认声明式表单和 iframe;用户可关闭。关键操作用命令式注册。「token 效率」类营销数字没有可追溯基准,不引用(本套件口径)。

## 三、身份与授权(Web Bot Auth 与 UA 行为)

- [draft-ietf-webbotauth-httpsig-protocol-00](https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/)(2026-09-01):签名方 MUST 发字典形式 `Signature-Agent`,旧字符串形式验签方 MAY 接受。细节见第 14 卡。
- 已核签名方:ChatGPT Work 的 Cloud browser(原 ChatGPT agent),发旧字符串形式 `Signature-Agent: "https://chatgpt.com"`([OpenAI](https://help.openai.com/en/articles/11845367-chatgpt-agent-allowlisting));OpenAI 没说 ChatGPT-User 签名。

| UA | 用途 | robots.txt |
|---|---|---|
| `Google-Agent` | Google 托管的 agent 代用户浏览、操作 | 用户触发抓取器 "generally ignore robots.txt rules"([Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers)) |
| `ChatGPT-User` | 用户提问时取页 | "robots.txt rules may not apply"([OpenAI](https://platform.openai.com/docs/bots)) |
| `ClaudeBot`/`Claude-SearchBot`/`Claude-User` | 训练/搜索索引/用户触发 | 三者都遵守([Anthropic](https://support.claude.com/en/articles/8896518)) |

- Content Signals 见第 1 卡。MCP Server Card:[SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127) 已于 2026-10-06 合入(Extensions Track,Final)。

## 四、Lighthouse Agentic Browsing 类别(7 项审计)

- 版本([releases](https://github.com/GoogleChrome/lighthouse/releases)):13.2.0(2026-05-01)建类别,13.4.1(2026-07-20)经 PSI API 提供,13.5.0(2026-09-18)加 `ard-schema`,13.6.0(2026-10-27)把 `ard-schema` 改到 ARD v0.91、CLI 支持一条命令批量审多个 URL(`--url-file`、`--fail-fast`),官方说一周内进 PSI([发布说明](https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0))。
- 类别 id `agentic-browsing`,只显示通过比例,不出 0–100 分([文档](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring))。PSI API 文档只列 4 个旧类别,viewer 源码发 `category=agentic-browsing`,未实测。

| 审计 id | 判什么(据源码) | 计分 |
|---|---|---|
| `agent-accessibility-tree` | 33 条 axe 规则:可访问名称、表单标签、ARIA 良构等;不含对比度、标题顺序 | 任一失败 = 0 |
| `webmcp-form-coverage` | 列出没有 `toolname`/`tooldescription` 的表单 | 信息型 |
| `webmcp-registered-tools` | 列出已注册工具;超过 40 个警告 | 信息型 |
| `webmcp-schema-validity` | 缺工具名、描述或必填参数名 = 错误;参数缺说明 = 警告 | 错误 0;只有警告 0.5 |
| `cumulative-layout-shift` | 元素位移会让 agent 点错 | 同性能类 |
| `llms-txt` | 有 H1、至少 1 个 Markdown 链接、≥50 字符 | 4xx = n/a;5xx/429 = 0 |
| `ard-schema` | 按 ARD 官方一致性逻辑校验目录 | 有错误 0;只有警告或只在旧路径 0.9 |

- 浏览器不支持 WebMCP 时三项 WebMCP 审计为 n/a,不等于通过。13.5.0 校验 `ai-catalog.json`;13.6.0 起先找 `ard.json`(#17259),旧位置只报 legacy 警告,报告页脚写 ARD 规范版本。用 PSI 时看结果里的 `lighthouseVersion` 判断走的是哪一版。

## 五、语言中立层的多语言部署

协议层与语言无关。每个 locale 各发一份目录,包内交叉链接按语言分目录(本套件口径)。OKF 打包见第 4 卡。

## 六、就绪决策表(本套件口径)

| 站点情形 | 建议 |
|---|---|
| 英文 SaaS/文档站(客群重度用 ChatGPT/Claude) | 全开:`ard.json` + `rel="ard"`、llms.txt、关键操作的命令式 WebMCP 工具、Web Bot Auth 日志 |
| 其他语区站点 | llms.txt + robots 放行引用型 bot;协议层等该语区出现消费者再上 |
| 技术博客/文档 | 每页配 `.md` 双胞胎(第 10 卡),性价比高于全套 |
| 电商 | 先做 Product 结构化数据与价格、库存一致,再加查价工具 |

## 七、未证实项

- ARD/OKF 未查到 AI 搜索或助手宣布消费;Google 称其企业级 Agent Platform 数月内原生支持 ARD。WebMCP 只核到一个有文档的消费者(第二节)。
- 未找到对照研究把可访问性树质量和 agent 任务成功率联系起来。

## 检查清单(在 skill 根目录运行,`site` 换成目标域名)

| 检查什么 | 怎么查 | 通过/失败 |
|---|---|---|
| 引用型 bot 放行 | `python3 scripts/robots_posture.py https://site/robots.txt --json` | 通过:`citation.ok` 为 true 且 `visibility_failures` 为空;封训练层不算失败(本套件口径) |
| llms.txt | `python3 scripts/llmstxt.py check https://site`;下载后 `python3 scripts/llmstxt.py validate llms.txt` | 通过:`/llms.txt` 行为 `200 [PASS]`,validate 退出码 0;失败:`/llms.txt` 行为 `[FAIL] /llms.txt 返回 HTML 页面`(其他文件各自写自己的路径;`/llms-full.txt` 不在规范里,首页 Markdown 版本 `index.html.md`/`index.md` 有一个即可,没有只记 `[NONE]`) |
| ARD 目录 | `curl -s https://site/.well-known/ard.json \| jq '.entries \| length'`;`curl -s https://site/robots.txt \| grep -i '^Agentmap:'`;官方工具 `conformance-test publisher site`(ard-spec 仓) | 通过:200、entries ≥1、工具无 error;失败:只在 `ai-catalog.json` |
| Agentic Browsing 与 ARIA | `lighthouse https://site --only-categories=agentic-browsing --output=json --output-path=./lh.json`(Node 22+,13.5.0+) | 通过:无 0 分审计(`agent-accessibility-tree` 的 33 条规则全过);记下通过比例 |
| WebMCP 工具 | 开 `chrome://flags/#enable-webmcp-testing` 后,控制台跑 `typeof document.modelContext?.registerTool` | 通过:返回 `function`,关键操作有命令式工具,schema 无错误 |
| Markdown 协商 | `curl -sI -H 'Accept: text/markdown' https://site/page/` | 通过:Markdown 或 307 到 `.md`,带 `Vary: Accept`,不同时发 `s-maxage` 和 `stale-while-revalidate` |
| Link 头 | `curl -sI https://site/ \| grep -i '^link:'` | 通过:只用注册 rel(第 9 卡),非 ASCII 路径已编码 |
| 签名 bot 流量 | 日志按 `Signature-Agent` 统计;看 CDN 已验证 bot 报表 | 通过:签名能验;未签名流量不默认拦截 |
| 生成式 AI 控制 | Search Console > 设置 > Search generative AI | 通过:取值等于客户书面决定(默认包含) |
| 价格一致 | Merchant Center 商品「需要处理」筛 "Mismatched product price" | 通过:无此问题 |

## 完全装载:自研 Markdown 协商的实现要点(第三方源码笔记)

协议见第 10 卡。1–6 条据 [nuxt-ai-ready](https://github.com/harlan-zw/nuxt-ai-ready) 源码。

1. 默认只按 `Accept` 协商。可选的 UA 启发式(AI bot 给 Markdown)有三条护栏:预渲染给 HTML;`Sec-Fetch-Dest: document` 不判 bot;`text/markdown`、`text/*`、`*/*` 最先匹配的一组全为 q=0 时尊重拒绝。
2. 不协商:`/.well-known/`、内部取 HTML 的请求、只接受 JSON 或 `text/event-stream` 的 API 请求。
3. 隐式命中 Markdown 时 307 到 `.md` 双胞胎,两种表示各占缓存键,忽略 `Vary` 的 CDN 也不串。`Vary` 默认 `Accept`,开启发式时加 `Sec-Fetch-Dest, User-Agent`,只追加一次。
4. 显式 `.md` 排在站点鉴权中间件之后渲染,防绕过鉴权。
5. ISR 或整页缓存不按全部协商头分变体时,协商自动关闭;自研时关协商,或把协商头加进缓存变体。
6. Link 头:HTML 带 `rel="alternate"; type="text/markdown"`;Markdown 带 `type="text/html"` 的 alternate 和指回 HTML 的 `rel="canonical"`;两者带 llms.txt 的 `rel="describedby"`。非 ASCII 路径先 `encodeURI`:RFC 8288 §3 要 URI-Reference,RFC 9110 §5.5 要新字段限于 US-ASCII;源码注释称 Cloudflare 拒收非 ASCII 头,未在其文档核到。
7. 新鲜度只放 `max-age` 加 `stale-while-revalidate`;`s-maxage` 会禁用 stale-while-revalidate([Cloudflare](https://developers.cloudflare.com/cache/concepts/cache-control/))。Cloudflare Pages/Workers 的 `_headers` 最多 100 条规则,每行 ≤2,000 字符([文档](https://developers.cloudflare.com/pages/configuration/headers/))。

## 官方口径校准与 AI 可见性技术层(digital-marketing-pro 深读 2026-10-09b)

来源:第三方仓库 [digital-marketing-pro](https://github.com/indranilbanerjee/digital-marketing-pro)。测量与审计见 [intake-checklists](../overview/intake-checklists.md) 同日节。

### 1. llms.txt 层的对冲事实(Google 生成式 AI 优化指南)

- [指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) 2026-05-15 新增,2026-06-15 补 llms.txt 说明([更新日志](https://developers.google.com/search/updates))。原文:"You don't need to create new machine readable files, AI text files, markup, or Markdown to appear in Google Search (including its generative AI capabilities), as Google Search itself doesn't use them";"there's no special schema.org markup you need to add"。资格:页面可索引、可显示摘要,且站点在 Search Console 生成式 AI 控制里保持「包含」(默认)。
- OpenAI、Anthropic、Perplexity 的爬虫文档只讲 robots.txt,不要求 llms.txt。
- 结论(本套件口径):llms.txt 和本文协议层按低成本期权对待,客户坚持要时记为低优先级交付物。驱动 AI 引用的是实体一致性、可引用片段和知识图谱对齐。

### 2. AI 退出/训练控制三层(互不可替代)

- Search 内的 AI 功能:robots.txt 管 Googlebot;`nosnippet`、`data-nosnippet`、`max-snippet`、`noindex` 限制展示([文档](https://developers.google.com/search/docs/appearance/ai-features))。没有 AI 专用 robots 或 meta 指令。
- `Google-Extended`(robots.txt 产品 token):管 Gemini 模型训练,以及 Gemini Apps 和 Vertex AI「Grounding with Google Search」的 grounding;不影响 Search 收录和排名([文档](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers))。
- Search Console「Search generative AI」控制:先[宣布](https://blog.google/products-and-platforms/products/search/new-controls-website-owners/)并在英国测试,后全球开放([日期](../overview/facts.md#gsc-genai))。覆盖 AI Overviews、AI Mode、Discover 的生成式 AI 功能;排除后不出链接、不作 grounding 输入;不影响训练;约 1–2 天生效;子属性默认继承父属性。何时考虑排除(本套件口径):AI 呈现直接伤漏斗的内容(付费墙摘要、进行中的声誉事件);先用 GSC 生成式 AI 报告估算会丢的展示。

### 3. 六规范表面与探针计分(本套件口径,取自第三方仓库)

- 6 表面:Google AI Mode、AI Overviews、ChatGPT、Perplexity、Gemini、Copilot。AI Mode 和 AI Overviews 分开探、分开记(Google:两者 "may use different models and techniques")。
- 计分:cited-with-link 10 / mentioned 7 / concept-only 3 / absent 0 / misrepresented −5;逐表面出分,不跨平台平均;单次 10–25 条查询;逐条核对 AI 说的品牌事实。
- 官方背景:[I/O 2026](https://blog.google/products-and-platforms/products/search/search-io-2026/)(2026-05-19):AI Mode 月用户超 10 亿,Gemini 3.5 Flash 为其全球默认模型,AI Overview 可直接追问进入 AI Mode;information agents 后台监控网页、社媒和实时数据,先给 AI Pro/Ultra 订阅户。Shopping Graph 超过 600 亿条商品,每小时更新 20 亿条。第三方转述:2026-09-28 Robby Stein 在 X 称它已对所有用户免费开放。
- 对探针的含义:①价格、库存、营业时间的变化会触发提醒,本地和购物页保持数据新鲜;②Merchant Center、落地页初始 HTML、结构化数据三处价格一致,否则商品可能被拒([帮助](https://support.google.com/merchants/answer/12159029));③提醒带来的访问没有 referrer,用 GSC 生成式 AI 报告对照变更日期;④探针集加「降价时提醒我」类常驻查询。第三方研究:BrightLocal [2026 调查](https://www.brightlocal.com/research/lcrs-ai-trust/)(1,002 名美国成年人)称,用 AI 找本地商家的比例从 6% 升到 45%。

### 4. 实体一致性层(本套件口径:杠杆高于 schema 微调)

- Wikidata 属性核对表:官网 P856 / X P2002 / Instagram P2003 / Facebook P2013 / LinkedIn 公司 ID P4264 / 创立 P571 / 总部 P159 / 行业 P452 / CEO P169 / 创始人 P112 / instance of P31。逐属性记 match/mismatch/outdated/missing。
- 修复优先级:Wikidata > Knowledge Panel 认领与更正 > Wikipedia > 目录 NAP 一致性。
- 通用词品牌名(如 Apple、Slack)做实体消歧:结构化数据写完整官方名加品类限定词。

### 5. Schema 2026 增量两点(停用清单见 [schema-examples](schema-examples.md))

据 Google [文档更新日志](https://developers.google.com/search/updates):2026-09-24 `VideoObject` 加 `creator` 属性(也支持 `author`);2026-07-24 review snippet 新增指南,针对虚假和未披露的激励评论,评论类 schema 审计加合规检查。

### 6. Agentic Booking(I/O 2026,本地服务)

I/O 2026 博客:AI Mode 代订扩展到本地体验和服务,直链到服务商预订;家装维修、美容、宠物护理可让 Google 代打电话;美国夏季上线。接入面是 Actions Center 数据 feed,不是页面 schema。Services feed 必填价格和时长,`bookability_info`、`policy_info` 标为 agentic booking 必需([文档](https://developers.google.com/actions-center/verticals/appointments/redirect/reference/feeds/services-feed))。schema.org 没有 `AvailabilityFeed` 类型。

### 7. Agent 执行门纪律(本套件口径,取自第三方技能)

CMS 写操作先出全量 before/after diff;用户明确回 `yes` 才执行,含糊即取消;失败不自动重试;先存回滚数据。批量 >5 条、建 redirect、改 canonical、删规则按高风险处理;部署后逐条 HTTP 验证。

### 8. 规模化内容与寄生 SEO 的政策执行细节

- **时间线(官方)**:2024-03-05 Google 同批推出 expired domain abuse、scaled content abuse、site reputation abuse 三条垃圾政策,site reputation 2024-05-05 生效([博客](https://developers.google.com/search/blog/2024/03/core-update-spam-policies))。2024-04-26 Google 称 3 月核心更新完成后,低质非原创结果减少 45%(预期 40%)([博客](https://blog.google/products-and-platforms/products/search/google-search-update-march-2024/))。2025-08-26 至 2025-09-22 August 2025 spam update,全球全语言,官方没说明打击点([Status Dashboard](https://status.search.google.com/incidents/a7Aainy6E9rZsmfq82xt))。
- **执行形态**:手动处罚落在 Manual Actions 报告「Major spam problems」,官方示例含 scaled content abuse([帮助](https://support.google.com/webmasters/answer/9044175))。2025 年针对 AI 批量内容的手动处罚只见第三方报道。
- **政策要点**:为操纵排名批量生成、对用户无价值的页面都算,不管用 AI、人工还是混合([政策](https://developers.google.com/search/docs/essentials/spam-policies#scaled-content))。生成式 AI 优化指南明说:为每个 fan-out 查询变体单独建页违反此政策。
- **闸门(本套件口径)**:批次唯一内容 <30% 硬停、30–40% 标记薄内容;standalone value test:「即使没有同类页,这一页也值得发布吗?」;渐进发布 50–100 页/批、观察 2–4 周;500+ 未审页不一次发布。数字真源、页型字数地板和高危页型见 [programmatic-seo-gates](programmatic-seo-gates.md),用 `python3 scripts/pseo_batch_gate.py --records batch.jsonl` 执行。
- **Site reputation 2026-08-30 起按搜索用户所在地分叉**([博客 2026-08-28](https://developers.google.com/search/blog/2026/08/update-site-reputation-policy)):EEA 外,手动处罚只影响受影响板块;EEA 内,手动处罚不生效,受影响板块可能被分离并随时间独立排序。站长仍收到 Search Console 通知。第三方或寄生板块的审计结论按 EEA 内外分开写。
