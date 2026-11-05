# JS 渲染与 SPA SEO

> 2026-10-21 按 Google、Bing、Naver、Yandex 官方文档核对，复核于 2026-11-05（补「Read more」深链）。与 [中文 AI 搜索指南](../content/chinese-ai-search-guide.md) 的「SPA 空壳=P0」条目呼应，本文件是系统版。移动端专项见 [mobile-seo.md](mobile-seo.md)。

## 一、Google 渲染管线（现行口径）

来源：[JS SEO 基础](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)（2026-03-04 更新）、[修复与 JS 相关的搜索问题](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript)（2025-12-18 更新）、[文档更新记录](https://developers.google.com/search/updates)。

- **三个阶段**：抓取 → 渲染 → 索引。被 robots.txt 屏蔽的页面和文件不会被渲染。Googlebot 把返回 200 的页面全部放进渲染队列，除非 robots meta 或响应头要求不索引。页面可能在队列里停几秒，也可能更久；资源允许时，无头 Chromium（常青版）执行 JS，渲染后的 HTML 用于索引和发现链接。
- **非 200 页面**：200 的页面会送去渲染，非 200 的可能不会（2025-12-18 补充）。错误页上用 JS 注入的内容和标记，不要指望被看到。
- **原始 HTML 里的 noindex**：Google 是否还会渲染这类页面没有明确定义，也可能变化。只要页面有可能需要被索引，原始 HTML 里就不要写 noindex，不要指望 JS 再把它删掉（2025-12-15 补充）。
- **canonical**：规范化在渲染前后都会发生。原始 HTML 写了 canonical，JS 就不要改成别的值；HTML 里写不了时，HTML 里干脆不写，只用 JS 设置（2025-12-17 补充）。
- **WRS 不保留状态**（[修复与 JS 相关的搜索问题](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript)）：每次页面加载都会清空 Local Storage、Session Storage 和 HTTP Cookie。依赖客户端存储才出现的内容（同意门后的正文、按 localStorage 分支的个性化）对 Google 不可见。
- **缓存**：WRS 可能忽略缓存头，用到旧的 JS/CSS。用内容指纹文件名（如 `main.2bb85551.js`），文件内容变了文件名才变。
- **能力边界**：Googlebot 拒绝权限请求（摄像头等）；不支持 WebSocket、WebRTC，要有 HTTP 回退；不支持 WebGL 等特性时要做特性检测。Shadow DOM 会被展平，内容必须出现在渲染后的 HTML 里。
- **路由与链接**：只发现带 `href` 的 `<a>` 链接；SPA 用 History API，不要用片段（`#/products`）加载不同内容。客户端路由的错误页要么 JS 跳到返回 404 的 URL，要么用 JS 加 `noindex`。
- **懒加载**：内容进入视口就加载（原生 `loading="lazy"`、IntersectionObserver），不依赖滚动或点击——Google 不和页面交互；首屏立即可见的内容不要懒加载（[懒加载文档](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading)）。
- **抓取上限**：Googlebot 每个文件只抓前一段（上限按解压后数据计，PDF 另有上限，见[事实表](../overview/facts.md#googlebot-size)）；页面引用的每个 CSS、JS 单独计算。
- **检测工具**：Search Console 网址检查（渲染后 HTML、加载的资源、JS 控制台输出；截图只在实时测试里有）、富媒体搜索结果测试。Mobile-Friendly Test 工具与 API 已于 2023-12 退役（[Google 博客注记](https://developers.google.com/search/blog/2016/05/a-new-mobile-friendly-testing-tool)）；改用网址检查或 Lighthouse。

> PDF：2026-10-13 Google Search Central 发布了一期讨论 PDF 转换、链接与 AI 结果的播客视频（第三方报道：[PPC Land](https://ppc.land/google-podcast-hosts-cant-name-the-pdf-crawl-limit-it-documents-as-64mb/)），不是新文档。核心内容仍应有 HTML 版本（本套件口径）。

## 二、渲染策略决策表

Google 的总原则：服务端渲染或预渲染「仍然是好主意」，因为对用户和爬虫都更快，而且不是所有爬虫都能运行 JavaScript。下表是本套件口径：

| 站点类型 | 推荐 | 理由 |
|---|---|---|
| 内容站 / 媒体 | SSG + 按需增量再生成（ISR） | 纯 CSR 依赖每个爬虫都执行 JS；Bing 明确要求不要把关键内容藏在客户端渲染后面 |
| 电商 | 商品页 SSG/ISR；筛选页 SSR 或按分页规范处理 | 价格、库存的个性化部分可以客户端注水，主内容必须在服务端 |
| SaaS | 营销站、文档 SSR/SSG；`app.*` 子域整体 noindex | 按页面选渲染方式（如 Next.js 逐页配置） |
| 文档 | SSG + ISR | 静态最稳 |

**meta 注入红线**：
- Google 可以用 JS 设置 title 和 meta description；canonical 按第一节的规则；noindex 不要依赖 JS 删除。
- Meta（Facebook）爬虫文档要求 Open Graph 属性出现在页面前 1 MB 内，否则被截断（[Meta Web Crawlers](https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers)）。社交与多数 AI 爬虫是否执行 JS，官方大多没写；按「不执行」设计——OG、canonical、hreflang、JSON-LD 写进初始 HTML（本套件口径）。

## 三、市场差异：各引擎的渲染

| 引擎 | 官方口径 | 实操 |
|---|---|---|
| Google | 常青版 Chromium 渲染；限制见第一节 | 按第一节自查 |
| Bing | 现行指南：不要把关键内容藏在客户端渲染后面；不能可靠渲染的内容可能不被索引，也不会被选作 Copilot 的 grounding 结果（[Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)） | 面向 Bing / Copilot 的内容一律服务端输出 |
| Naver（Yeti） | 支持 SPA 收录，但解析 JS 要多耗数倍资源，官方建议主要区域服务端渲染；JS/CSS 不要被 robots.txt 屏蔽；URL 片段（`#`）会被去掉，用永久链接；JS 资源单独抓取，没抓到前先按静态 HTML 索引；不建议在 JS URL 里加时间戳或哈希来强制刷新（[Naver JS 指南](https://searchadvisor.naver.com/guide/seo-advanced-javascript)） | 韩语区 SPA 做 SSR。指纹文件名只在文件内容变化时才变，不要每次构建都换名 |
| Yandex | 站长后台「索引 → JavaScript 页面渲染」（β），默认由机器人自行决定；已做 SSR 或预渲染的站点建议关闭渲染；内容延迟加载时可用 `window.YandexRotorSettings` 告知（[Yandex 渲染文档](https://yandex.com/support/webmaster/en/yandex-indexing/rendering)） | 俄语区以该设置和实测为准 |
| 百度 | 未找到百度关于执行 JS 的一手文档（未核） | 中文区做 SSR 或预渲染兜底；以百度搜索资源平台的抓取诊断实测为准 |

## 四、SPA SEO 审计清单

| # | 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|---|
| 1 | 关键元素在原始 HTML 里 | 命令 1：对比原始 HTML 与渲染后 DOM 中 title、canonical、robots、hreflang、JSON-LD、h1 的出现次数 | 失败：任何一项只在渲染后出现（空壳 = P0）。计数会把脚本里的字符串算进去，最终看命令 2 |
| 2 | 服务端内容完整 | 命令 2：原始 HTML 可见文本 ÷ 渲染后可见文本 | 本套件口径（C9）：≥0.9 通过；<0.5 判空壳 |
| 3 | 套件规则扫描 | `python3 scripts/site_audit.py https://example.com/page --json`，看 rendering 五项（CSR 空挂载点、noscript 回退、JS 重量、服务端内容、H1/H2） | 失败：出现 CSR 空挂载点警告 |
| 4 | Google 看到的版本 | Search Console 网址检查 → 测试实际网址 → 查看已测试的网页（HTML、截图、更多信息里的资源加载和控制台） | 失败：渲染后 HTML 缺主内容；资源被 robots.txt 拦截；控制台报错 |
| 5 | 资源可抓 | 对主要 JS、CSS 跑 [robots-txt-reference.md](robots-txt-reference.md) 检查清单第 5 项 | 失败：任何渲染必需资源被屏蔽 |
| 6 | 路由与状态码 | 检查导航链接都是 `<a href>`，没有 `#/` 路由；访问不存在的路由 | 失败：片段路由；错误路由返回 200 且没有 noindex |
| 7 | 不依赖客户端状态 | 用无痕窗口（清空存储）打开主要页面 | 失败：主内容要先接受同意弹窗或依赖 localStorage 才出现 |
| 8 | 爬虫与用户内容一致 | 同一 URL 用浏览器 UA 与 Googlebot UA 各抓一次，对比主内容（只做诊断，不做差异化输出） | 失败：两者主体内容不同（伪装风险） |
| 9 | 「Read more」深链不被 JS 破坏 | 打开 `URL#某个小节的id`：看是否停在该小节、地址栏 hash 是否还在；搜前端代码里加载时调用的 `scrollTo(`、`history.replaceState(`、`location.hash =` | 失败：加载后被拉回页顶；hash 被去掉；目标小节默认折叠在手风琴或标签页里 |

```bash
# 命令 1：原始 HTML 与渲染后 DOM 的关键元素计数（macOS 路径；Linux 用 google-chrome）
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
curl -s https://example.com/page > raw.html
"$CHROME" --headless=new --disable-gpu --user-data-dir=/tmp/chrome-seo --dump-dom https://example.com/page > rendered.html
for p in '<title' 'rel="canonical"' 'name="robots"' 'hreflang=' 'application/ld+json' '<h1'; do
  printf '%-22s raw=%s rendered=%s\n' "$p" "$(grep -oi "$p" raw.html | wc -l | tr -d ' ')" "$(grep -oi "$p" rendered.html | wc -l | tr -d ' ')"
done

# 命令 2：可见文本比（去掉 script/style/noscript/template 后的非空白字符数）
python3 -I -c '
import re
def n(p):
    s = open(p, encoding="utf-8", errors="replace").read()
    s = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return len(re.sub(r"\s+", "", s))
r, d = n("raw.html"), n("rendered.html")
print("raw=%d rendered=%d ratio=%.2f" % (r, d, r / d if d else 0))'
```

### 「Read more」深链（Google 2026-04-20 新增文档）

Google 搜索结果摘要里可能带「Read more」链接，直达页面的某一节。提高出现机会的三条（[摘要文档](https://developers.google.com/search/docs/appearance/snippet#read-more-deep-links)，页面日期 2026-04-20，核对 2026-11-05）：

1. 内容对人立即可见，不藏在可展开区块或标签页里。
2. 不用 JS 控制页面加载时的滚动位置（例如不要强制滚回页顶）。
3. 加载时调用 History API 或改 `window.location.hash` 的，不要把 URL 里的 hash 片段去掉，否则深链失效。

SPA 最容易踩的是第 2、3 条：路由库加载时 `scrollTo(0,0)`、用 `replaceState` 规范化 URL 把 `#…` 抹掉。上面审计清单第 9 项就查这三条。

## 五、动态渲染与预渲染

- Google 的动态渲染文档现用过去时：动态渲染曾是变通方案，不是长期方案，也不推荐，因为它增加复杂度和资源消耗（[动态渲染文档](https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering)）。
- 只要动态渲染给爬虫的内容与用户看到的相似，Google 一般不视为伪装；给用户和爬虫完全不同的内容（例如用户看猫、爬虫看狗）才算伪装。
- Google 的 Rendertron 仓库已归档（最后提交 2022-10）。能做 SSR/SSG 就不要长期挂预渲染；长期预渲染的主要风险是两个版本内容漂移（本套件口径）。
- 按 UA 分流给非 Google 爬虫预渲染时：分流名单不要包含 Googlebot（Google 自己能渲染）；预渲染服务回头抓站点时要排除自身 UA，防止递归（本套件口径）。
- SPA 的动态路由（如 `/product/:id`）没有别的发现渠道，要全部枚举进 sitemap（本套件口径）。

## 六、与 Core Web Vitals 的关联

- 阈值与诊断以 [cwv-playbook.md](cwv-playbook.md) 为准（阈值见[事实表](../overview/facts.md#cwv)，按 p75）。
- CSR 空壳要等 JS 下载执行完才有主内容，LCP 天然偏慢；SSR 或流式渲染改善首屏。
- 水合期间的长任务拖慢 INP：拆分长任务、按需水合（岛屿架构）。
- 水合重写 DOM 会引起 CLS；首屏 LCP 图不要懒加载。

## 来源

- Google：[摘要文档「Read more」深链](https://developers.google.com/search/docs/appearance/snippet#read-more-deep-links)（2026-04-20）、[JS SEO 基础](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)、[修复与 JS 相关的搜索问题](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript)、[懒加载与无限滚动](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading)、[动态渲染](https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering)、[Googlebot 抓取上限](https://developers.google.com/search/docs/crawling-indexing/googlebot)、[文档更新记录（2025-12 三条 JS 补充）](https://developers.google.com/search/updates)、[Mobile-Friendly Test 退役注记](https://developers.google.com/search/blog/2016/05/a-new-mobile-friendly-testing-tool)
- 其他引擎：[Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)、[Naver 자바스크립트 검색 최적화](https://searchadvisor.naver.com/guide/seo-advanced-javascript)、[Yandex JavaScript 页面渲染](https://yandex.com/support/webmaster/en/yandex-indexing/rendering)
- 社交：[Meta Web Crawlers](https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers)
- 工具状态：[GoogleChrome/rendertron](https://github.com/GoogleChrome/rendertron)（已归档）
- 未核项：百度是否执行 JS；社交与 AI 爬虫的 JS 能力（各家多未公开，按不执行设计）。
