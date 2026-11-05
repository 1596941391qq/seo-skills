# AI 爬虫政策参考（robots.txt 决策）

> 用途：回答「robots.txt 里该放行或禁止哪些 AI 爬虫」。
> 口径：bot 名、用途、是否遵守 robots.txt、IP 表，一律以运营方官方页为准。2026-10-18 逐个打开核对，复核于 2026-11-05（补 OpenAI 训练信号、Cloudflare 2026-09-15 新默认）。没有官方页的 bot 标「第三方观察」。「决策」类内容是本套件口径。
> 分工：agent 协议（Content Signals、ARD、WebMCP、Web Bot Auth 等）的规范出处与状态见 [agent-protocols.md](agent-protocols.md)；Lighthouse 与站点准备见 [agent-readiness.md](agent-readiness.md)；Naver 细则见 [naver-searchadvisor.md](naver-searchadvisor.md)。

## 一、先分清三类 bot（最常见错误在这里）

三类：**训练**（内容可能进模型训练）、**搜索/索引**（决定能否出现在 AI 答案里）、**用户触发**（用户在对话里让 AI 去取某个页面）。同一家公司的三类 bot 用不同 token，规则互相独立。

| token | 运营方（官方页） | 类别 | 官方用途要点 | 遵守 robots.txt | 官方 IP 表 / 验证 |
|---|---|---|---|---|---|
| `OAI-SearchBot` | [OpenAI](https://developers.openai.com/api/docs/bots) | 搜索 | ChatGPT 搜索结果；禁止后不出现在 ChatGPT 搜索答案，但仍可能作为导航链接出现 | 是 | `openai.com/searchbot.json` |
| `GPTBot` | OpenAI | 训练 | 抓取可能用于训练基础模型的内容 | 是 | `openai.com/gptbot.json` |
| `ChatGPT-User` | OpenAI | 用户触发 | 不做自动抓取；不决定搜索收录 | 官方：robots 规则「may not apply」 | `openai.com/chatgpt-user.json` |
| `OAI-AdsBot` | OpenAI | 广告审核 | 只访问作为 ChatGPT 广告提交的落地页；数据不用于训练 | 官方未说明 | `openai.com/adsbot.json` |
| `ClaudeBot` | [Anthropic](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) | 训练 | 收集可能用于训练的内容 | 是；支持 Crawl-delay；2026-10-30 起另认 `__usage_ai-training`，点名 `ClaudeBot` 的规则优先（见第二节） | `claude.com/crawling/bots.json` |
| `Claude-SearchBot` | Anthropic | 搜索 | 为搜索结果建索引 | 是 | 同上 |
| `Claude-User` | Anthropic | 用户触发 | 禁止后，Claude 不再按用户请求取回该站内容 | 是 | 同上 |
| `PerplexityBot` | [Perplexity](https://docs.perplexity.ai/guides/bots) | 搜索 | 在搜索结果中展示和链接网站；不用于训练基础模型 | 是 | `perplexity.com/perplexitybot.json` |
| `Perplexity-User` | Perplexity | 用户触发 | 用户提问时访问页面 | 官方：「generally ignores robots.txt」 | `perplexity.com/perplexity-user.json` |
| `Googlebot` | [Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) | 搜索 | Google 搜索，含 Discover 和全部搜索功能（AI Overviews、AI Mode 在内） | 自动抓取时总遵守 | `common-crawlers.json`；反向 DNS `*.googlebot.com` |
| `Google-Extended` | Google | 控制 token | 不单独抓取。控制 Gemini 模型训练，以及 Gemini Apps 与 Vertex AI「Grounding with Google Search」的 grounding；不影响搜索收录与排名 | 只作 robots token | — |
| `Google-CloudVertexBot` | Google | 站长委托 | 站点所有者为建 Vertex AI Agents 请求的抓取；不影响 Google 搜索 | 是 | `common-crawlers.json` |
| `Google-Agent` | [Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers) | 用户触发 | Google 基础设施上的 agent 按用户请求浏览网页、执行操作 | 用户触发类「generally ignore robots.txt」 | `user-triggered-agents.json`；部分请求带 Web Bot Auth 签名（实验，身份 `https://agent.bot.goog`，[Google](https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth)） |
| `Applebot` | [Apple](https://support.apple.com/en-us/119829) | 搜索 | Spotlight、Siri、Safari 搜索；数据也可能用于训练和生成 AI 回答 | 是；没有 Applebot 组时跟随 Googlebot 组；不支持 crawl-delay | `applebot.json`；反向 DNS `*.applebot.apple.com` |
| `Applebot-Extended` | Apple | 控制 token | 不抓取；只决定 Applebot 抓到的数据能否用于训练 | 只作 robots token | — |
| `Bingbot` | [Microsoft](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a) | 搜索 | Bing 与 Copilot 共用同一套抓取、索引、排名基础 | 是 | `bing.com/toolbox/bingbot.json`（实测可取） |
| `CCBot` | [Common Crawl](https://commoncrawl.org/ccbot) | 开放语料 | 建公开网页数据集；第三方研究称它是生成式 AI 最重要的训练数据源之一（[Mozilla 2024-02](https://www.mozillafoundation.org/en/research/library/generative-ai-training-data/common-crawl/)） | 是；支持 Crawl-delay | `index.commoncrawl.org/ccbot.json`；反向 DNS `*.crawl.commoncrawl.org` |
| `meta-externalagent` | [Meta](https://developers.facebook.com/docs/sharing/webmasters/web-crawlers) | 训练/产品 | 训练基础模型，或直接索引内容改进产品 | 按 robots.txt（官方给出写法） | 官方页 |
| `meta-webindexer` | Meta | 搜索 | 提升 Meta AI 搜索质量；放行有助于在 Meta AI 回答中被引用和链接 | 按 robots.txt | 官方页 |
| `meta-externalfetcher` | Meta | 用户触发 | 按用户请求取单个链接 | 官方：可能绕过 | 官方页 |
| `facebookexternalhit` | Meta | 链接预览 | 抓取分享链接的标题、描述、缩略图 | 做安全检查时可能绕过 | 官方页 |
| `Amazonbot` | [Amazon](https://developer.amazon.com/amazonbot) | 训练/产品 | 改进产品与服务，可能用于训练 Amazon AI 模型 | 是；robots 缓存最长 30 天；不支持 crawl-delay | `developer.amazon.com/amazonbot/ip-addresses/` |
| `Amzn-SearchBot` | Amazon | 搜索 | Alexa 等搜索体验；不用于训练 | 是；没有专属组时跟随其他搜索 bot 的规则 | `…/amazonbot/searchbot-ip-addresses/` |
| `Amzn-User` | Amazon | 用户触发 | 例如为 Alexa 实时取信息 | 官方：「may not follow all robots.txt directives」 | `…/amazonbot/live-ip-addresses/` |
| `DuckAssistBot` | [DuckDuckGo](https://duckduckgo.com/duckduckgo-help-pages/results/duckassistbot) | 搜索 | 为 AI 辅助答案实时抓取；不用于训练 | 是；禁止后 72 小时生效 | `duckduckgo.com/duckassistbot.json` |
| `MistralAI-User` | [Mistral](https://docs.mistral.ai/robots) | 用户触发 | Vibe 回答用户问题时访问页面 | 用 robots 控制用户请求能访问哪些站 | `mistral.ai/mistralai-user-ips.json` |
| `MistralAI-Index` | Mistral | 搜索 | 为 Mistral 搜索建索引；不用于训练 | 按 robots.txt | `mistral.ai/mistralai-index-ips.json` |
| `MistralAI-Training` | Mistral | 训练 | 构建训练数据集 | 可 Disallow | 官方未给 |
| `YandexAdditional` | [Yandex](https://yandex.com/support/webmaster/en/robot-workings/check-yandex-robots) | 控制 token | 处理 robots.txt，阻止内容出现在 Search with Yandex AI 回答中；不发索引请求 | 不认 `User-agent: *` 通用规则，必须点名 | 反向 DNS `yandex.ru/.net/.com` |
| `PetalBot` | [Huawei](https://aspiegel.com/petalbot) | 搜索 | Petal 搜索索引，以及 Huawei Assistant、AI Search | 是 | 反向 DNS |
| `AI2Bot` | [Allen AI](https://allenai.org/crawler) | 训练 | 抓取内容训练开放语言模型 | 官方页未说明 | — |
| `Bytespider` | 字节跳动（无官方页） | 第三方观察 | 第三方称用于训练与搜索 | 第三方观察称常不遵守 | — |

**关键事实**（官方，核对 2026-10-18）：
1. **禁 `GPTBot` 不影响 ChatGPT 搜索。** OpenAI 写明各 token 设置互相独立；引用走 `OAI-SearchBot`。
2. **Copilot 没有单独的 bot。** Bing Webmaster Guidelines 写明 Bing 与 Copilot 共用抓取和索引。控制 Copilot 用页面 meta：`NOARCHIVE` 让内容不进 Copilot 回答和 grounding；`NOCACHE` 只允许用 URL、标题、摘要（[Bing 文档](https://www.bing.com/webmasters/help/robots-meta-tags-and-attributes-that-bing-supports-5198d240)）。
3. **`Google-Extended` 不是 AI Overviews 开关。** 它不影响搜索收录。退出 AI Overviews/AI Mode 的做法见第二节第 3 条。
4. **用户触发类 bot 的 robots 行为各家不同。** OpenAI（may not apply）、Perplexity（generally ignores）、Google（generally ignore）、Meta（may bypass）、Amazon（may not follow all）声明可能不遵守；Anthropic 声明 `Claude-User` 遵守。
5. **日志按 token 子串匹配，不写死版本号。** OpenAI 示例 UA 为 `OAI-SearchBot/1.4`、`GPTBot/1.4`，官方注明版本会变；抓 robots.txt 时 UA 可能多一个 `robots.txt;` 标记。Google 的 `Chrome/W.X.Y.Z` 也会变。
6. **robots 改动的生效时间各家不同。** OpenAI 搜索约 24 小时；Perplexity 最多 24 小时；Meta 最多缓存 24 小时；Google 一般缓存不超过 24 小时；DuckAssistBot 72 小时；Amazon 可能用最近 30 天内的缓存。RFC 9309 规定缓存一般不超过 24 小时（[RFC 9309 §2.4](https://www.rfc-editor.org/rfc/rfc9309)）。

## 二、四种典型诉求的配置

### 1. 全开放（本套件默认推荐）

```
User-agent: *
Allow: /
```

不写任何 AI 专属规则。

### 2. 保留 AI 搜索引用、退出模型训练

```
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: MistralAI-Training
Disallow: /
```

- 搜索类和用户触发类 bot 不动。
- `Google-Extended` 要单独决定。禁它会同时停止 Gemini Apps 和 Vertex AI grounding 使用你的内容（官方），不只是训练。想保留 Gemini App 里的引用，就不要禁。
- **跨厂商训练偏好 token `__usage_ai-training`（草案，2026-10-30 起）。** Anthropic 2026-10-30 起开始逐步在全部服务上遵守这个「不要 AI 训练」信号；robots.txt 里点名 `ClaudeBot` 的规则比它更具体，优先执行（[Anthropic 帮助页](https://privacy.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)「How Anthropic honors website preferences for AI training」一节）。Google 宣布计划 2027 年和其他 AI 厂商一起支持：站点用这个 policy token 表示退出训练、且没有单独写 `Google-Extended` 时，Google 按「禁了 `Google-Extended`」处理；单独写的 `Google-Extended` 规则照旧生效，并且优先（[Google 博客 2026-10-30](https://developers.google.com/search/blog/2026/10/ai-training-control)）。语法来自 IETF 个人草案 [draft-kelley-aipref-training-preference-signal-00](https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/)（作者单位 Anthropic，2027-05-03 过期）：写成普通 robots.txt 组，`User-Agent: __usage_ai-training` 加 `Disallow`/`Allow`，可按路径；`User-Agent: *` **不算**对它表态；文件里没有这一组 = 没有表态；它只表达用途偏好，不管抓取，抓取仍看各家 bot 自己的组（草案 §4.2–4.4）。OpenAI 同日宣布会遵守这个共享信号，原文是「aim to implement the signal in the coming months」，实现时另发说明；现有按 bot 的 robots.txt 控制（`GPTBot` 等）照旧生效（[OpenAI 公告](https://openai.com/index/helping-websites-express-ai-training-preferences/)，页面正文没写日期，链接指向上面这份草案；核对 2026-11-05）。状态：**OpenAI 已宣布、未实现**。本套件口径：想禁训练的站现在就加这一组（不认识它的解析器会当成未知 bot 跳过，没有副作用）；但目前只有 Anthropic 在铺开、OpenAI 和 Google 都还没实现（Google 定在 2027 年），上面按 bot 写的组一条都不能删。

  ```
  User-Agent: __usage_ai-training
  Disallow: /
  Allow: /press-kit/
  ```
- `Amazonbot`、`meta-externalagent` 的官方用途是「训练或改进产品」。禁它们不只影响训练，按业务决定（本套件口径）。

### 3. 退出特定引擎的 AI 答案

| 引擎 | 做法 | 官方说明（核对 2026-10-18） |
|---|---|---|
| ChatGPT 搜索 | `Disallow` `OAI-SearchBot` | 不出现在搜索答案；仍可能作为导航链接；约 24 小时生效 |
| Google AI Overviews / AI Mode / Discover 生成式功能 | Search Console → 设置 → Search generative AI，选 Exclude；或页面级 `nosnippet`、`data-nosnippet`、`max-snippet` | 已对所有网站开放（[日期](../overview/facts.md#gsc-genai)）；一般 1–2 天生效；不影响训练（训练用 `Google-Extended`）；不作为其他搜索排名信号（[帮助页](https://support.google.com/webmasters/answer/16908024)、[AI 功能文档](https://developers.google.com/search/docs/appearance/ai-features)） |
| Perplexity | `Disallow` `PerplexityBot` | `Perplexity-User` 仍可能按用户请求抓取 |
| Claude | `Disallow` `Claude-SearchBot`（索引）与 `Claude-User`（用户触发） | 两者都声明遵守 robots.txt |
| Copilot | 页面 meta `NOARCHIVE`（或 `NOCACHE`，只给 URL/标题/摘要） | robots.txt 只管抓取，不管索引 |
| Apple Siri / 搜索的 AI 回答 | 页面 `nosnippet`；付费墙页标 `isAccessibleForFree: false` | 训练另用 `Applebot-Extended` |
| DuckDuckGo AI 辅助答案 | `Disallow` `DuckAssistBot` | 72 小时生效；不影响自然排名 |
| Yandex AI 回答 | `User-agent: YandexAdditional` + `Disallow: /` | 必须点名，`*` 规则管不到它 |
| Mistral Vibe | `Disallow` `MistralAI-Index` 与 `MistralAI-User` | — |

### 4. 完全退出所有 AI

逐家做第 2、3 条。没有一键全退（本套件口径）。用户触发类 bot 多数声明可能不遵守 robots.txt；要彻底挡住，只能靠 WAF 或登录墙（本套件口径）。Anthropic 提醒：只按 IP 封禁，会让它读不到 robots.txt，不能保证持续退出（官方）。

## 三、市场差异：区域引擎的爬虫与收录

| 市场 | Bot / 机制 | 事实（来源，核对 2026-10-18） | 决策（本套件口径） |
|---|---|---|---|
| 俄语区 | `YandexAdditional` | 见第一节；作用于主爬虫已收录的页面，本身不发索引请求（Yandex 官方） | 想进 Yandex AI 回答就不写 Disallow；与 GPTBot 等分开决策 |
| 俄语区 | YandexBot + IndexNow | Yandex 是 IndexNow 参与方（[indexnow.org](https://www.indexnow.org/)） | 新鲜度策略纳入 IndexNow |
| 土耳其 | Yandex 系 | StatCounter 全平台：Yandex 2026-01 为 42.5%、2026-03 为 13.4%、2026-09 为 25.5%，月度波动大（[StatCounter](https://gs.statcounter.com/search-engine-market-share/all/turkey)，第三方） | 按 Google+Yandex 双引擎做；YandexAdditional 决策同俄语区 |
| 韩语区 | Naver `Yeti` | robots 要点见下；收录与报表见 [naver-searchadvisor.md](naver-searchadvisor.md) | 韩语流量的前提是被 Naver 收录 |
| 日语区 | `Bingbot` | StatCounter 全平台：Bing 2026-01 至 2026-09 月度 24.3%–36.4%，2026-09 为 31.6%（第三方）；Bing 索引同时服务 Copilot（官方） | Bing Webmaster Tools 验证列为必做项 |
| 越南 | Cốc Cốc | StatCounter：2026-09 为 5.96%（第三方）；2023-05-29 推出 AI Chat 与 AI Search（[官方新闻稿](https://press.coccoc.com/bai-viet/coc-coc-chinh-thuc-ra-mat-ai-chat-va-ai-search-toi-uu-hoa-cho-nguoi-viet/)） | 越南向站点把 Cốc Cốc 纳入可达性抽查 |
| 中文 | `Baiduspider` / `Bytespider` | 百度官方：UA 含 `Baiduspider/2.0` 或 `Baiduspider-render/2.0`；不公布 IP 段（动态变化），验证靠双向 DNS——反向解析主机名必须是 `*.baidu.com` 或 `*.baidu.jp`，再正向解析回原 IP（[百度搜索资源平台，2022-02-08，核对 2026-10-21](https://ziyuan.baidu.com/college/articleinfo?id=3378)）。`Bytespider` 没有官方文档（第三方观察）；中文引擎细则见 [chinese-ai-search-guide.md](../content/chinese-ai-search-guide.md) | 中文站先确认 `Baiduspider` 没被禁；日志核真伪用 `host <IP>` 后再 `host <主机名>` |
| 全局 | Mistral 三个爬虫 | User / Index / Training 三分工（Mistral 官方） | 放行 User 与 Index；Training 按战略定 |
| 全局 | 过时 token | Anthropic 官方页只列三个 bot，OpenAI 只列四个；`anthropic-ai`、`Claude-Web`、`ChatGPT-Plugins` 不在官方页 | 审计先查死 token（`robots_posture.py` 的 `deprecated_tokens` 字段） |

**Yeti（Naver）的 robots.txt 要点**（[Naver 官方](https://searchadvisor.naver.com/guide/seo-basic-robots)，核对 2026-10-18）：
1. 返回 2xx 但内容是 HTML：可能按「没有 robots.txt、全部允许」处理。文件要用 `text/plain`。
2. 3xx 最多跟 5 次，超过按全部允许；HTML/JS 跳转不解释。
3. 4xx 按全部允许。5xx 按全部不允许；之前成功抓到的规则可能临时沿用。对照：RFC 9309 规定 5xx 必须视为完全禁止；Google 前 12 小时停抓，之后 30 天用最后一份可用副本，没有副本则按无限制处理（[Google robots 规范](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)）。所以 robots.txt 返回 5xx 一律按阻断项处理。
4. 规则只对同一 host、协议、端口生效。`www.example.com/robots.txt` 管不到 `example.com`。
5. 只放行 Yeti 的写法：`User-agent: *` + `Disallow: /`，再写 `User-agent: Yeti` + `Allow: /`（官方示例）。
6. `User-agent : Yeti`（冒号前有空格）符合 RFC 9309 语法（`*WS ":"`）。只用 `grep 'User-agent: Yeti'` 会漏检（本套件口径）。

`nosourceinfo` 是 Naver 的 robots meta 值。官方定义：使用后，Naver 不为该站提供 AI 自动生成的출처설명（出处说明）（[markup-structure](https://searchadvisor.naver.com/guide/markup-structure)，核对 2026-10-18）。

**llms.txt 的证据状态**：Google 官方指南写明 Google 搜索不使用 llms.txt 这类「AI 文本文件」（[指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)，页面更新 2026-07-10）。其他引擎未见公开承诺消费 llms.txt。本套件口径：只作低成本对冲，不承诺引用。写法见 [llms-txt-guide.md](../content/llms-txt-guide.md)。

## 四、暗坑清单

1. **WAF/CDN 拦截**：robots.txt 只表达意愿。CDN 的 WAF 或「你是人吗」验证页可能先拦下真 bot。Google 建议：临时拦截返回 503 或 429；对爬虫的验证页也改回 503；不要返回带 200 的错误页；网络超时会让 URL 被移出索引（[Google 2024-12-24](https://developers.google.com/search/blog/2024/12/crawling-december-cdns)）。
2. **Cloudflare 托管 robots.txt**：官方称为 Bot Preference Sync。你在 Search、Agent、Training 三类策略里至少有一项设为 Block（或 Training 设为 Disallow）时，Cloudflare 生成托管指令。源站 robots.txt 返回 HTTP 200 时，托管段（`# BEGIN Cloudflare Managed content`）被插到源文件前面，合成一份响应；源站没有 robots.txt 时由 Cloudflare 生成。官方示例的托管段含 `Content-signal` 行和对 Amazonbot、Applebot-Extended、Bytespider、CCBot、ClaudeBot、Google-Extended、GPTBot、meta-externalagent 的 Disallow（[官方](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/)，核对 2026-10-21）。这段只在线上响应里。审计必须抓线上响应，不能只看源文件。
3. **把 `Google-Extended` 当 AIO 开关，把 `GPTBot` 当 ChatGPT 引用开关**：两者都错，见第一节。
4. **只按 IP 封 bot 来退出**：Anthropic 称这会妨碍它读 robots.txt，不能保证退出（官方）。
5. **ai.txt 等非标准文件**：未见引擎公开承诺遵守（本套件口径）。有则无害，无则不扣分。
6. **robots 与 llms.txt 矛盾**：llms.txt 列出的页对搜索类 bot 禁抓，等于白做（本套件口径）。
7. **改完马上验收**：各家缓存时长不同（第一节第 6 条）。没等够时间就判「没生效」是误判。

## 五、探测方法（检查清单）

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| robots.txt 姿态 | `python3 scripts/robots_posture.py https://example.com/robots.txt --json`，看 `visibility_failures`、`bots_blocked`、`cloudflare_injected`、`deprecated_tokens` | `visibility_failures` 为空，或每一项都是有意为之 → 通过。脚本名单与官方有偏差，见第七节 |
| 线上 robots.txt 与源文件一致 | `curl -s https://example.com/robots.txt -o live.txt && diff live.txt <仓库里的 robots.txt>` | 没有意外的托管段或注入行 → 通过 |
| robots.txt 状态码与类型 | `curl -sI https://example.com/robots.txt` | 200 且 `content-type: text/plain` → 通过；5xx → 失败（阻断项）；返回 HTML → 失败 |
| UA 活体探测 | `curl -s -o /dev/null -w '%{http_code}\n' -A '<第一节官方页上的完整 UA>' https://example.com/<深层页>`；每个搜索类 bot 测首页和一个深层页 | 200 → 通过；403、429、5xx 或验证页 → 失败。局限：请求来自你的 IP，只能测按 UA 的规则；按 IP 或签名放行的规则看下一项 |
| 日志核真 bot | `python3 scripts/ai_referral_log.py access.log --bot-ua --classify` 看 bot × 状态码矩阵；可疑 IP 用下面的命令比对官方 IP 表；Google、Apple、Common Crawl、Yandex 可用 `host <IP>` 做反向 DNS，再正向复核 | 真 bot（IP 在官方表内）拿到 200 → 通过；真 bot 被 403/429 → 失败；自称 bot 但 IP 不在官方表 → 记为伪装流量 |
| Google 侧 | Search Console 网址检查看渲染截图；设置 → Search generative AI 看当前选项 | 截图是页面而不是验证页，选项与决策一致 → 通过 |
| Copilot / Bing 侧 | 跑下方第一段命令，看 meta robots / bingbot 与 `X-Robots-Tag` | 想被 Copilot 引用的页没有 `noarchive`、`nocache` → 通过 |

```bash
# Copilot / Bing 侧：查页面 meta 与响应头
curl -s https://example.com/page | grep -ioE '<meta[^>]*name="(robots|bingbot)"[^>]*>'
curl -sI https://example.com/page | grep -i '^x-robots-tag'

# 官方 IP 表比对（OpenAI、Anthropic、Perplexity、Google、Bing 的 JSON 都是
# {"prefixes":[{"ipv4Prefix"/"ipv6Prefix"}]} 结构，2026-10-18 实测）
curl -s https://openai.com/gptbot.json -o gptbot.json
python3 -c 'import json,ipaddress,sys; n=[ipaddress.ip_network(p.get("ipv4Prefix") or p.get("ipv6Prefix")) for p in json.load(open(sys.argv[1]))["prefixes"]]; print(any(ipaddress.ip_address(sys.argv[2]) in x for x in n))' gptbot.json <日志里的 IP>
```

输出 `True` 表示 IP 在官方段内。

## 六、三态商业决策：封 / 放 / 收费（Cloudflare AI Crawl Control）

robots.txt 只有封和放两态。Cloudflare AI Crawl Control（原名 AI Audit，所有套餐可用）可以按爬虫设置放行或拦截，并提供第三态「收费」（Pay Per Crawl，私测阶段）（[官方](https://developers.cloudflare.com/ai-crawl-control/)，核对 2026-10-18）。决策单位是每个爬虫，不是整站一刀切。

**三态 × 爬虫类型矩阵**（本套件口径，起步默认值，最终归业务定）：

| 爬虫类型 | 默认态 | 理由 |
|---|---|---|
| 搜索类（OAI-SearchBot、Claude-SearchBot、PerplexityBot 等，见第一节） | **放** | 直接影响 AI 答案可见性；对它们收费或封禁等于退出引用面 |
| 训练类（GPTBot、ClaudeBot、CCBot 等） | **按战略** | 放：模型「认识」你的内容。封或收费：内容变现或防白用。取决于内容有没有许可市场 |
| 未验证抓取、无视 robots 的 scraper | **收费或封** | 没有可见性回报，只有成本；先用 CDN 的爬虫识别定位，再处置 |

**Pay Per Crawl**（官方，核对 2026-10-18）：
- 机制：爬虫在请求头里表示付款意向才拿到 200；否则收到 `402 Payment Required` 和价格。Cloudflare 是记录商户（Merchant of Record）。默认按 zone 统一定价（[说明](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/what-is-pay-per-crawl/)）。
- 按 URI 免费：Rules → Configuration Rules，对 URI 模式设「Disable Pay Per Crawl」。`/robots.txt`、`/sitemap.xml`、`/security.txt`、`/.well-known/security.txt`、`/crawlers.json` 永远免费（[changelog](https://developers.cloudflare.com/ai-crawl-control/changelog/) 2025-12-10）。
- 动态定价：开启 Enable dynamic pricing 后，源站响应头 `crawler-price: USD 3.14` 覆盖 zone 默认价；Cloudflare 给回源请求加 `cf-pay-per-crawl` 头，告诉源站当前计价模式（[高级配置](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/use-pay-per-crawl-as-site-owner/advanced-configuration/)，changelog 2026-06-16）。

**Redirects for AI Training**（[官方](https://developers.cloudflare.com/ai-crawl-control/reference/redirects-for-ai-training/)，changelog 2026-04-17）：
- 作用：对 Cloudflare 归为「AI Crawler」类别的已验证 bot，把页面已有的 `<link rel="canonical">` 强制成 301。只在 canonical 同源、且与当前 URL 不同时触发。浏览器、搜索引擎、AI Assistant / AI Search 类 bot 照常拿到原页。
- 条件：Pro、Business、Enterprise 套餐；只处理 `text/html` 响应；canonical 必须在解压后 HTML 的前 256 KB 内；Single/Bulk Redirects 先于它执行。
- 审计：日志里「AI Crawler 类 bot 请求重复页 → 301 → Location 等于该页 canonical」是这个功能的正常形态，不要当重定向链错误去修。日志字段 `redirects_for_ai_training_target` 记录跳转目标（GraphQL Analytics API 或 Logpush）。没开这个功能却出现同样的 301，要查边缘层是谁做的（见 [edge-seo.md](edge-seo.md) 第三节决策表）。

### Cloudflare 2026-09-15 起的新控制与默认（核对 2026-11-05）

站在 Cloudflare 后面时，robots.txt 之外还有一层边缘拦截。2026-07-01 的预告和 2026-09-15 的上线说法不一样，以上线时的为准：

| 项目 | 2026-07-01 预告（[博客](https://blog.cloudflare.com/content-independence-day-ai-options/)） | 2026-09-15 上线（[新闻稿](https://www.cloudflare.com/press/press-releases/2026/cloudflare-helps-end-the-search-or-ai-training-tradeoff/)、[博客](https://blog.cloudflare.com/accountable-mixed-use-ai-crawlers/)） |
|---|---|---|
| 开关 | 「Block AI Bots」之外加 Search、Agent、Training 三类可分别管理（含免费版） | 「Block AI Bots」被三个独立控制取代；托管 robots.txt 被 Bot Preference Sync 取代 |
| 新域名默认 | 所有新接入域名：广告页上默认拦 Training 和 Agent，Search 放行 | 改成接入时「推荐设置」，按是否靠广告变现给两套，接入时和之后都能改（见下表） |
| 混合用途爬虫（一个爬虫同时做搜索和训练，如 Googlebot、Bingbot、Applebot） | 按最严格的用途处理：选了拦 Training 就连搜索一起拦 | 新增 Training 选项「Disallow AI Training」：在 robots.txt 发布不许训练的偏好，被认定为 Accountable 的混合爬虫照常抓搜索，其他训练爬虫被拦。选「Block」或「Block on pages with ads」才会连 Googlebot、Bingbot、Applebot 的搜索一起拦 |
| 老用户迁移 | — | 旧「Block AI Bots」选了拦截的 → Search 放行、Training = Disallow AI Training、Agent = 广告页拦截；此前在细分控制里把 Training 设为拦截的，迁成 Disallow AI Training |

新域名推荐设置（2026-09-15 博客原表）：

| 设置 | 不靠广告变现 | 靠广告变现 |
|---|---|---|
| Bot Preference Sync | 开 | 开 |
| Search | 放行 | 放行 |
| Training | 放行 | Disallow AI Training |
| Agent | 放行 | 广告页拦截 |

**Accountable（问责）认定**：运营方要满足或承诺在限期内满足四条：robots.txt 或同类标准能退出训练；能退出 AI 摘要；给 URL 级的使用可见性；公开承诺退出训练不影响传统搜索排名。Apple、Google、Microsoft 被认定为 Accountable（部分条件是带期限的承诺）；Amazon、Anthropic、Meta、OpenAI 因为搜索和训练用不同爬虫，相关爬虫也算 Accountable。名单在 [Cloudflare Radar](https://radar.cloudflare.com/ai-insights#ai-bot-transparency)。Cloudflare 博客转述：Bing 目前靠 `NOARCHIVE` 表达不许训练，robots.txt 域级「不许训练」计划 2027 年初支持（这是 Cloudflare 的说法，微软一手页面未核到）。

审计怎么用（本套件口径）：
1. Cloudflare 后面的站先看后台三项设置，再看线上 robots.txt（Bot Preference Sync 会插托管段，见第四节第 2 条）。
2. Training 设成「Block」或「Block on pages with ads」= Googlebot、Bingbot、Applebot 也被拦，搜索可见性会掉。只想禁训练、要保留搜索，选「Disallow AI Training」。
3. 靠广告的站接入时如果接受了推荐设置，Agent 在广告页被拦：ChatGPT-User 这类用户触发的抓取和浏览器 agent 在这些页拿不到内容。想被 AI 助手实时引用的页，要么不放广告，要么把 Agent 改回放行。
4. 「Agent」目前没有 Disallow 选项，只有放行或拦截（Cloudflare：还没有成熟的指令能向 agent 表达偏好）。

**与证据口径的衔接**：禁训练类 bot 不影响 ChatGPT、Claude、Perplexity 的搜索引用，因为引用走搜索类 bot（第一节，官方）。所以三态决策是商业决策（内容许可收入 vs 训练曝光），不是 SEO 手段。例外：`Google-Extended` 还管 Gemini Apps 的 grounding，禁它会影响 Gemini App 里的引用（官方）。审计报告不把「封 GPTBot」写成 SEO 建议，也不把「放行训练 bot」写成 GEO 优化。证据分级见 [geo-evidence.md](../content/geo-evidence.md)。

## 七、来源与已知偏差

**官方来源**：第一节表格的「运营方」列和各节正文里的链接，全部 2026-10-18 打开核对。2026-11-05 补核：OpenAI 训练偏好公告、Cloudflare 2026-07-01 博客、2026-09-15 新闻稿与 Accountable 博客。2026-11-05 补核：Anthropic 爬虫帮助页（2026-10-30 新增训练偏好一节）、Google 共享训练控制博客（2026-10-30）、IETF 草案 draft-kelley-aipref-training-preference-signal-00、[Control what you share](https://developers.google.com/search/docs/crawling-indexing/control-what-you-share)（2026-10-21 更新，列出 Search generative AI control，与第二节第 3 条一致）。另读了 [Google 验证请求文档](https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests)、[Common Crawl FAQ](https://commoncrawl.org/faq)、OpenAI bots 更新 RSS（`/api/docs/bots/rss.xml`，当日没有条目）。

**第三方**：StatCounter 搜索引擎份额（全平台月度 CSV，2026-01 至 2026-09）；[Mozilla Foundation 2024-02](https://www.mozillafoundation.org/en/research/library/generative-ai-training-data/common-crawl/)（Common Crawl 与生成式 AI 训练数据）。

**脚本名单（2026-10-21 已按本文件对齐）**：`scripts/robots_posture.py` 现为 37 个 bot、四层（search 15、training 11、user 8、other 3），每个带官方核实标记；`Amazonbot` 不再记为搜索类，`PetalBot` 记为搜索，`Google-CloudVertexBot`、`cohere-ai` 不再记为训练，补了 `Baiduspider`、`Amzn-SearchBot`、`Amzn-User`、`MistralAI-*` 等。`scripts/ai_referral_log.py` 把 `GoogleOther` 移出训练类，官方页没有的 `Claude-Web`、`AzureAI-SearchBot`、`DeepSeekBot`、`GrokBot`、`Manus-User`、`Gemini-Deep-Research` 标「未核」，补了 `meta-webindexer`、`Google-Agent`、`OAI-AdsBot`、`YandexAdditional`、`Baiduspider`。`YouBot`、`xAI-Bot`、`AI2Bot-Dolma` 仍未找到运营方官方 bot 文档（截至 2026-10-21）。名单变化时以第一节为准，并同步两个脚本。
