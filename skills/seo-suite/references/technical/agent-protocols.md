# Agent 协议速查卡(14 协议一页对照)

> 核对 2026-10-18。事实以各卡「规范」链接的原文为准;[specification.website](https://github.com/jdevalk/specification.website) 只作二手索引(它的 ARD 路径与字段、NLWeb 响应、DNS-AID 标签、Web Bot Auth 签名厂商、RFC 8288 章节号与原文不符,已按原文改)。部署取舍见 [agent-readiness.md](agent-readiness.md);robots.txt UA 表见 [ai-crawler-policy.md](ai-crawler-policy.md)。
> 状态标签:**stable**=冻结的正式版(RFC、W3C CG 定稿报告、开放治理项目的 1.x);**draft**=还在改的草案(IETF WG/个人草案、W3C CG 草案、多方 0.x 提案、社区约定);**vendor**=一家公司或一个项目自定版本的规范;**none**=单站约定,未成标准。

## 1. Content Signals(robots.txt 使用偏好声明)— vendor(IETF 对应物为 WG 草案)

- **规范**:Cloudflare [Content Signals Policy](https://contentsignals.org/)(2025-09-24,CC0;原文自述是 Cloudflare 的实现;旧版写的「IAB Tech Lab 平行规范」无出处,已删)。IETF aipref 的 WG 草案:[vocab-08](https://datatracker.ietf.org/doc/draft-ietf-aipref-vocab/)(2026-09-14)、[attach-05](https://datatracker.ietf.org/doc/draft-ietf-aipref-attach/)(2026-08-19)。
- **规则**:Cloudflare 写 `Content-Signal: search=yes, ai-input=yes, ai-train=no`。IETF 写 `Content-Usage: train-ai=n`(标签 `train-ai`/`ai-use`/`search`,值 `y`/`n`,robots.txt 规则与 HTTP 头同名)。两套不混写。指令名单数;放在 `User-agent:` 组内;可带路径前缀;不写某项=不表态;被 `Disallow` 的路径不带偏好(attach §3.1)。它是偏好声明,不是技术拦截。
- **谁支持**:Cloudflare 托管 robots.txt 写 `Content-signal: search=yes, ai-train=no, use=reference`(`use=` 是测试中的第四字段,[文档](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/));Markdown for Agents 也在响应头发。未找到 AI 厂商承诺读取它的一手文档。
- **第三种写法(2026-10-30 出现)**:IETF 个人草案 [draft-kelley-aipref-training-preference-signal-00](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/) 不加新指令,用 policy token `__usage_ai-training` 当 `User-Agent:` 写普通组(`Disallow` = 反对训练,`Allow` = 同意;`*` 组不算表态)。Anthropic 2026-10-30 起开始逐步遵守(点名 `ClaudeBot` 的规则优先,[帮助页](https://privacy.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler));Google 宣布计划 2027 年支持,并把它的退出解读为禁 `Google-Extended`([博客](https://developers.google.com/search/blog/2026/10/ai-training-control))。这是目前唯一有 AI 厂商公开承诺读取的训练偏好写法,上面 Cloudflare 和 `Content-Usage` 两种仍没有;用法和决策见 [ai-crawler-policy.md](ai-crawler-policy.md) 第二节。

## 2. ARD / AI Catalog(域级能力目录)— draft

- **规范**:[AI Catalog](https://github.com/Agent-Card/ai-catalog)(Linux Foundation 维护的工作仓)定义目录格式;[ARD v0.91](https://github.com/ards-project/ard-spec/blob/main/spec/ard.md)(Proposal,2026-08-26,Apache 2.0)加检索与联邦。ARD 由 Google 于 2026-06-17 [宣布](https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/),Microsoft、Hugging Face、GoDaddy 等参与;ARD 不是 LF 项目,LF 托管的是 AI Catalog。
- **规则**:路径已分叉:AI Catalog 用 `/.well-known/ai-catalog.json` + `rel="ai-catalog"`;ARD v0.91 用 `/.well-known/ard.json` + `rel="ard"`,读旧路径只是可选兼容。目录 = `specVersion` + `entries`。条目必填 `identifier`(`urn:air:<域名>:…`)、`type`(媒体类型,如 `application/mcp-server-card+json`、`application/a2a-agent-card+json`、`application/agent-skills+zip`)、`url`/`data` 二选一;ARD 另要求 `displayName`,建议 `representativeQueries` 2–5 条。两份规范都没有 `mediaType` 字段。ARD 另有 robots.txt `Agentmap:` 和 DNS `_entries._agents`/`_search._agents`。
- **签名**:AI Catalog 的 Trust Manifest 用 JCS(RFC 8785)+ detached JWS,签名覆盖条目 identifier、type 和内容 digest;目录级签名没有授权签名者时不算真实性证明。ARD v0.91 不定义签名流程。
- **谁支持**:Hugging Face 在线目录与检索服务(实测只发 `ai-catalog.json`);Google Cloud Agent Registry 宣布将支持。两条路径发同一份文件(本套件口径)。

## 3. NLWeb(对话式站点问答)— vendor

- **规范**:[nlweb-ai/NLWeb](https://github.com/nlweb-ai/NLWeb)(MIT;原 `microsoft/NLWeb`,现 301 到此)+ [REST API 文档](https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-rest-api.md)。
- **规则**:端点 `/ask` 与 `/mcp`,参数相同。`query` 必填;可选 `site`、`prev`、`decontextualized_query`、`streaming`(默认 true)、`mode`(`list`/`summarize`/`generate`)。返回 JSON:`query_id` + 结果数组(`url`、`name`、`site`、`score`、`description`、`schema_object`)。MCP 核心方法叫 `ask`。旧版的 `answer`+`sources` 结构和 `ask_site` 工具名不是官方写法。
- **发现**:`<link rel="nlweb">` 只是社区约定(官方仓未定义,IANA 未注册)。未找到 AI 引擎消费 `/ask` 的一手声明。

## 4. OKF bundle(整库 Markdown 打包)— vendor

- **规范**:Google Cloud [OKF SPEC v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)(2026-07-24 提交;正本已迁到此仓,knowledge-catalog 仓的 `okf/` 副本已冻结)。
- **规则**:概念 = YAML frontmatter + 正文,唯一硬字段是非空 `type`。`okf_version` 只放根 `index.md`;其他 `index.md` 不带 frontmatter。v0.2 两处断裂:`timestamp`→`generated.at`;正文 `# Citations`→frontmatter `sources`(消费方可回退读旧字段)。`log.md` 新的在前;`status` 只取 `draft`/`stable`/`deprecated`。规范不定义媒体类型和发现方式;旧版的 `application/okf-bundle+gzip` 和「唯一落地是付费 Knowledge Catalog」无出处,已删。打包后另挂 ARD 条目或 llms.txt(本套件口径)。
- **常见错误**:手写第二份导致漂移;非根 `index.md` 带 frontmatter;声明 0.2 却发 0.1 字段。

## 5. WebMCP(浏览器内工具注册)— draft

- **规范**:W3C WebML CG [WebMCP](https://webmachinelearning.github.io/webmcp/)(CG 草案,2026-10-16;编辑来自 Microsoft、Google)。
- **规则**:API 在 `document.modelContext`(安全上下文);2026-05-27 前的草案挂在 `navigator.modelContext`([#184](https://github.com/webmachinelearning/webmcp/pull/184)),Chrome origin trial 文档只用前者。`registerTool({name, title?, description, inputSchema?, execute, annotations?}, {signal?, exposedTo?})`,另有 `getTools()`、`executeTool()`。注解是四个布尔值:`readOnlyHint`、`untrustedContentHint`、`consequentialHint`、`debugging`;没有 `destructiveHint`。`consequentialHint: true` 提示 agent 和浏览器在执行前要求用户确认。跨源 iframe 要 `allow="tools"`。
- **谁支持**:Chrome origin trial M149–M156([Chrome Status](https://chromestatus.com/feature/5117755740913664)),本地测试开 `chrome://flags/#enable-webmcp-testing`;Edge 也有 origin trial;Lighthouse Agentic Browsing 类别审计工具注册。Mozilla 立场 neutral([#1412](https://github.com/mozilla/standards-positions/issues/1412)),WebKit 立场 oppose([#670](https://github.com/WebKit/standards-positions/issues/670))。
- **本套件口径**:先 feature-detect(兼容旧构建可两个都检测)再加载工具脚本;与站点的 HTTP MCP 服务器同名同 schema;服务端照常鉴权。

## 6. Schemamap(逐页 JSON-LD 端点索引)— none

- 单站提案:specification.website [自述](https://specification.website/spec/agent-readiness/schemamap/)无外部标准、无 IANA rel、无第二实现者。不部署。指向逐页 JSON-LD 用已注册的 `rel="alternate" type="application/ld+json"`。

## 7. TDMRep(TDM 权利保留)— stable

- **规范**:W3C [TDMRep CG 定稿报告](https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240202/)(2024-02-02,不在标准轨),对应 EU 指令 2019/790 第 4 条。
- **规则**:`tdm-reservation` 只取整数 `1`/`0`;其他值按未设置处理。`tdm-policy` 可选,设 1 不强制配。载体:`/.well-known/tdmrep.json`(数组,每条 `location` + `tdm-reservation`)、HTTP 头、HTML `<meta>`、EPUB 元数据;后读的覆盖先读的:meta/EPUB > HTTP 头 > well-known;规范建议只用一种(SHOULD)。它是权利声明,不是拦截器。
- **谁支持**:第三方论文统计,2024-01 只有 45 个主机发布 tdmrep.json([arXiv 2404.02309](https://arxiv.org/abs/2404.02309));未找到主要 AI 爬虫声明读取。设 1 却写 `ai-train=yes` 属口径矛盾(本套件口径)。

## 8. A2A agent cards(agent 互发现)— stable

- **规范**:[A2A 1.0](https://a2a-protocol.org/latest/specification/)(v1.0.0 于 2026-03-12 发布,v1.0.1 于 2026-05-28 发布,GitHub releases 核对 2026-10-21);Google 2025-04 发起,2025-06-23 转入 Linux Foundation。
- **规则**:卡片在 `/.well-known/agent-card.json`。必填 `name`、`description`、`version`、`supportedInterfaces`(各含 `url`、`protocolBinding`=`JSONRPC`/`GRPC`/`HTTP+JSON`、`protocolVersion`)、`capabilities`、`defaultInputModes`、`defaultOutputModes`、`skills`(各含 `id`、`name`、`description`、`tags`)。1.0 的 JSON-RPC 方法是 `SendMessage`、`GetTask` 等(0.3 的 `message/send` 已改);REST 为 `POST /message:send`。核心操作都要实现;未声明 streaming 时,流式调用回 `UnsupportedOperationError`。可选 JWS `signatures`。
- **常见错误**:卡片指向 404 端点;声称未实现的 streaming;沿用 0.3 方法名。

## 9. HTTP Link 头(HTML-free 发现)— stable

- **规范**:[RFC 8288](https://www.rfc-editor.org/rfc/rfc8288)、[RFC 9727](https://www.rfc-editor.org/rfc/rfc9727)(`/.well-known/api-catalog`,内容必须是 `application/linkset+json`)、[RFC 9264](https://www.rfc-editor.org/rfc/rfc9264)、[IANA 注册表](https://www.iana.org/assignments/link-relations/link-relations.xhtml)。
- **规则**:只用注册 rel。已注册(核对 2026-10-18):`describedby`、`alternate`、`api-catalog`、`linkset`、`service-desc`/`service-doc`/`service-meta`、`author`、`license`。**未注册**:`sitemap`、`security`、`nlweb`、`ai-catalog`、`ard`、`agent-skills`、`schemamap`;要用就写成 URI 形(RFC 8288 §2.1.2)。llmstxt.org 建议 `describedby` 指 llms.txt,`alternate` + `type="text/markdown"` 指 .md。多条用逗号分隔;URL 放在 `<>` 里。在 CDN 或反代层加,非 HTML 响应也能带(本套件口径)。

## 10. Markdown 源端点(逐页 .md + 内容协商)— draft

- **规范**:无正式标准。[llmstxt.org](https://llmstxt.org/) v2 提议同 URL 加 `.md`(无文件名的 URL 用 `index.md`);协商按 RFC 9110 §12。
- **规则**:`.md` 孪生页回 `Content-Type: text/markdown`。做 `Accept: text/markdown` 协商时,Markdown 与 HTML 两种响应都带 `Vary: Accept`(RFC 9110 §12.5.5),否则缓存会串表示;`Content-Location` 可选。HTML 或 Link 头加 `rel="alternate" type="text/markdown"`。.md 与 HTML 的访问策略一致(本套件口径)。
- **谁支持**:实测 2026-10-18:Anthropic(platform.claude.com/docs)与 Stripe 文档的 `.md` 和协商都回 `text/markdown`;Cloudflare Markdown for Agents 在边缘转换。Cloudflare 自测一篇博文 16,180→3,150 token([厂商自测](https://blog.cloudflare.com/markdown-for-agents/));旧版「小 5–20 倍」无出处,已删。实测有大型文档站的 HTML 响应漏带 `Vary: Accept`。

## 11. Agent Skills 发现(SKILL.md 发布面)— vendor

- **规范**:Cloudflare [Agent Skills Discovery RFC v0.2.0](https://github.com/cloudflare/agent-skills-discovery-rfc)(Draft,2026-03-12 更新)+ [agentskills.io 规范](https://agentskills.io/specification)。
- **规则**:索引在 `/.well-known/agent-skills/index.json`(v0.1 的 `/.well-known/skills/` 已改名)。必须有 `"$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json"`;缺了,客户端按 v0.1 处理。条目必填 `name`、`type`(`skill-md`/`archive`)、`description`、`url`、`digest`(`sha256:` + 原始字节哈希);digest 不符时客户端必须拒用。`name` 1–64 字符(小写字母、数字、连字符);`description` 1–1024 字符。index 用 `application/json`,SKILL.md 用 `text/markdown` 或 `text/plain`;给浏览器客户端用时加 CORS(SHOULD)。规范没有 `rel="agent-skills"`。
- **谁支持**:实测:isitagentready.com 和 developers.cloudflare.com 发 v0.2 索引;Stripe 文档仍在旧路径。

## 12. DNS-AID(DNS 层 agent 服务发现)— draft

- **规范**:[draft-mozleywilliams-dnsop-dnsaid-02](https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/)(2026-05-27,IETF 个人草案)+ [RFC 9460](https://www.rfc-editor.org/rfc/rfc9460)(SVCB/HTTPS)。
- **规则**:已知 agent 时,查 agent 名上的 SVCB;`alpn` 带 agent 协议(`alpn=mcp,h2,h3`),一种协议一条记录。组织索引在 `_index._agents.<域>`:ServiceMode(优先级 ≥1),TargetName 不含下划线;AliasMode(0)只给指向主记录的别名入口。DNSSEC 是 SHOULD(用 TLSA 时 MUST)。消费方必须理解的参数写进 `mandatory=`(SHOULD);未注册参数写成 `keyNNNNN`。旧版的 `_mcp._agents`、`_a2a._agents` 不在 -02 里。
- **谁支持**:Cloudflare 扫描器有 `dnsAid` 检查(实测查 SVCB 与 HTTPS 两类)。

## 13. auth.md(agent 注册说明书)— vendor

- **规范**:WorkOS [auth.md 文档](https://workos.com/auth-md/docs/auth-md) + [参考实现](https://github.com/workos/auth.md)。OAuth 部分是标准(RFC 9728、8414、7523、7009);`agent_auth` 块与 claim grant(`urn:workos:agent-auth:grant-type:claim`)是私有扩展。
- **规则**:放在服务根 `/auth.md`。顺序:发现 → 选方式(`identity_assertion`/`service_auth`/`anonymous`)→ `POST /agent/identity` → claim 仪式(沿用 RFC 8628 词汇,私有 grant)→ JWT-bearer 换 token → 调 API → 吊销。与 PRM(`/.well-known/oauth-protected-resource`)冲突时以 PRM 为准。只有 email 时必须走 claim;`user_code` 会过期。文件不授予权限。不要与 Web Bot Auth(验流量身份)混淆。

## 14. Web Bot Auth(可验证 bot 身份)— draft

- **规范**:[RFC 9421](https://www.rfc-editor.org/rfc/rfc9421) + [draft-ietf-webbotauth-httpsig-protocol-00](https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/)(2026-09-01,WG 文档;作者来自 Cloudflare、Google;目录草案已并入)。
- **规则**:禁止共享 HMAC。`Signature-Agent` 用字典形 `sig1="https://bot.example"`;默认 `type=directory`,值必须是 origin,目录在 `/.well-known/http-message-signatures-directory`(`application/http-message-signatures-directory+json`);另有 `type=jwks_uri`、`type=cimd`。签名覆盖 `@authority` 或 `@target-uri`,外加 `"signature-agent";key="sig1"`;必带 `created`、`expires`、`keyid`(JWK thumbprint)、`tag="web-bot-auth"`。未解析的 Signature-Agent 不能用来定策略。
- **兼容性坑**:Cloudflare 现行验证只认旧的字符串形,收到字典形会验证失败([文档](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/))。
- **谁签名**:OpenAI 的 ChatGPT Cloud browser(`"https://chatgpt.com"`,旧形,[帮助中心](https://help.openai.com/en/articles/11845367-chatgpt-works-cloud-browser-allowlisting));Google-Agent 的部分请求(`g="https://agent.bot.goog"`,实验阶段,[文档](https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth))。旧版写的 Anthropic、Perplexity 无文档,主域名下也无目录(实测 404),已删。不要拦未签名流量:Google 说明并非所有请求都签名。

## 否决记录(specification.website `considered/`)

- AGENTS.md:`out-of-scope`(2026-09-12)。它是仓库文件,网站侧没有可检查的 URL;由 LF AAIF 托管,6 万+ 项目采用([LF](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation))。另六条 `too-early`:Cache-Status(RFC 9211)、DPP 发现、HTTP Cache Groups(RFC 9875)、增量转发(RFC 10036)、`<meta name="text-scale">`、419 Purpose Declined。

## 检查清单

先设 `D=https://example.com`。`iar` 调 Cloudflare 的免费扫描器 isitagentready.com 的 MCP 接口;第二个参数是检查名;输出 PASS/FAIL/OK(OK=仅提示):

    iar() { curl -s -X POST https://isitagentready.com/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"scan_site\",\"arguments\":{\"url\":\"$1\",\"enabledChecks\":[\"$2\"]}}}" | grep -o -E "(PASS|FAIL|OK) $2"; }

1. **Content Signals** → `curl -s $D/robots.txt | grep -n -i -B3 '^content-signal'`;`iar $D contentSignals` → 通过:行在 `User-agent:` 组内,键只有 search/ai-input/ai-train(可加 `use=`),值是 yes/no;失败:复数、组外、IETF 标签、FAIL。
2. **AI bot 放行** → `python3 scripts/robots_posture.py $D/robots.txt --json --signal protect-ip` → 通过:`visibility_failures` 为空;失败:列出被封的 search/user 层 bot。
3. **ARD / AI Catalog** → `curl -s $D/.well-known/ard.json | jq -e '.entries | all(has("identifier") and has("type") and (has("url") != has("data")))'`,再换 `ai-catalog.json`;`iar $D ard` → 通过:true,各 `url` 返回 200;失败:false、解析错误、`url` 404。
4. **NLWeb** → `curl -s "$D/ask?query=test&streaming=false" | jq -e '.query_id and (.results|type=="array")'` → 通过:true,抽 3 条 `url` 返回 200 且内容相符;失败:HTML 或空数组。
5. **OKF** → `grep -L '^type: .' $(find bundle -name '*.md' ! -name index.md ! -name log.md)`;`find bundle -mindepth 2 -name index.md -exec grep -l -m1 '^---$' {} +` → 通过:两条都无输出;失败:列出的文件。
6. **WebMCP** → Chrome 149+ 控制台执行 `await document.modelContext.getTools()`;`iar $D webMcp` → 通过:工具齐全,注解与行为一致,不支持的浏览器网络面板里没有工具脚本;失败:写操作标 `readOnlyHint`,付款类缺 `consequentialHint`。
7. **TDMRep** → `curl -sI $D/ | grep -i '^tdm-'`;`curl -s $D/.well-known/tdmrep.json | jq -e 'all(.[]; has("location") and (.["tdm-reservation"]==0 or .["tdm-reservation"]==1))'` → 通过:整数 0/1,非 HTML 资产的头一致;失败:false、`yes`、与 Content-Signal 矛盾。
8. **A2A** → `curl -s $D/.well-known/agent-card.json | jq -e '["name","description","version","supportedInterfaces","capabilities","defaultInputModes","defaultOutputModes","skills"] - keys == []'`;向 JSONRPC 接口 POST `{"jsonrpc":"2.0","id":1,"method":"SendMessage","params":{"message":{"role":"ROLE_USER","parts":[{"text":"ping"}],"messageId":"t1"}}}` → 通过:true,返回 JSON-RPC `result` 或 `error`;失败:404、HTML。
9. **Link 头** → `curl -sI $D/ | grep -i '^link:'`;每个裸名 rel 跑 `curl -s https://www.iana.org/assignments/link-relations/link-relations-1.csv | cut -d, -f1 | grep -x -i '<rel>'`;`iar $D linkHeaders` → 通过:rel 都查得到,非 HTML 响应也带;失败:查不到的 rel。
10. **Markdown** → `python3 scripts/llmstxt.py check $D`(只探测根目录的 /llms.txt、/llms-full.txt、/index.md、/index.html.md);内页跑 `curl -sI -H 'Accept: text/markdown' $D/<页>/ | grep -i -E '^(content-type|vary)'`,再不带 Accept 对比 → 通过:`text/markdown`,两种响应都有 `Vary: Accept`;失败:`[FAIL]`、缺 Vary。
11. **Agent Skills** → `curl -s $D/.well-known/agent-skills/index.json | jq -r '."$schema"'`;逐条 `curl -s <url> | shasum -a 256` 比对 `digest`;`jq '.skills[] | select((.name|test("^[a-z0-9]+(-[a-z0-9]+)*$")|not) or (.name|length)>64 or (.description|length)>1024) | .name'` → 通过:0.2.0 URI、哈希全对、最后一条无输出;失败:任一不符。
12. **DNS-AID** → `curl -s -H 'accept: application/dns-json' "https://cloudflare-dns.com/dns-query?name=_index._agents.example.com&type=SVCB"`,再查 `type=HTTPS`;`iar $D dnsAid` → 通过:有 Answer、优先级 ≥1、`"AD":true`;失败:无记录、优先级 0、AD 为 false。DoH 不受本地代理改写 DNS 影响。
13. **auth.md** → `curl -s -o /dev/null -w '%{http_code} %{content_type}\n' $D/auth.md`;`curl -s $D/.well-known/oauth-protected-resource | jq .authorization_servers`;`iar $D authMd` → 通过:无凭证返回 200,文中端点与元数据一致;失败:登录墙、端点不一致。
14. **Web Bot Auth(bot 运营方)** → `curl -sI https://<bot域>/.well-known/http-message-signatures-directory`;抓一条出站请求 → 通过:200 + 目录媒体类型,`Signature-Input` 含 `@authority`、`"signature-agent"`、`created`、`expires`、`keyid`、`tag="web-bot-auth"`,形式匹配目标验证方;改动任一被签组件后验证失败。

## 状态一览(核对 2026-10-18)

| 协议 | 标签 | 实际状态 |
|---|---|---|
| Link 头 | stable | RFC 8288 / 9727 / 9264;只用注册 rel |
| TDMRep | stable | W3C CG 定稿报告(2024-02-02) |
| A2A | stable | LF 项目 1.0(2026-03-12) |
| WebMCP | draft | W3C CG 草案;Chrome M149–M156 与 Edge origin trial |
| Web Bot Auth | draft | IETF WG 草案 -00 + RFC 9421 |
| DNS-AID | draft | IETF 个人草案 -02 |
| ARD / AI Catalog | draft | ARD v0.91 Proposal;AI Catalog 工作仓 |
| Markdown 源端点 | draft | 社区约定(llmstxt.org) |
| Content Signals | vendor | Cloudflare 规范;IETF `Content-Usage` 是 WG 草案 |
| Agent Skills 发现 | vendor | Cloudflare 草案 v0.2.0 |
| NLWeb | vendor | 项目参考实现 + REST 文档 |
| OKF bundle | vendor | Google Cloud v0.2 |
| auth.md | vendor | WorkOS 规范 |
| Schemamap | none | 单站提案,不部署 |
