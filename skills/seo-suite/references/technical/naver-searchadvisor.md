# Naver Search Advisor 官方指南蒸馏

> **来源与口径**：事实以 Naver 웹마스터 가이드原文为准（`https://searchadvisor.naver.com/guide/{guid}`）。2026-10-18 逐篇重读了本文引用的全部 guid，修订日取页面的 `postModified`。二手索引：来源仓 [JaceProgramming/naver-searchadvisor-expert](https://github.com/JaceProgramming/naver-searchadvisor-expert)（2026-07 采集 55 篇）。当前菜单仍是 55 篇：`structured-data-howto` 已下线，`faq-branding`（2026-10-16）是新增页，2026-10-12～16 另有 14 篇修订。C-Rank、D.I.A.+、최적화 지수、「저품질 블로그」判定是社区概念，不在官方指南里。

## 用途

韩语区做收录诊断、robots/sitemap/RSS、IndexNow、结构化数据、제휴（合作）API 评估时读。[ai-crawler-policy.md](ai-crawler-policy.md) 第三节是摘要，这里是规范层。韩国搜索份额有两个第三方口径（核对 2026-10-18）：[InternetTrend](https://www.internettrend.co.kr/insights/2026-09-search-engine) 来路构成里 Naver 领先（装了其 Logger 的韩国网站的实际引荐访问，样本统计，不是面板）；StatCounter 页面浏览里 Google 略高（[读数](../overview/facts.md#search-share)）。两套口径的数字见 [ko.md](../markets/ko.md)。

## 一、收录机制：수집요청 与优先级队列（官方文档蒸馏）

- **流水线**：수집 → 정제 → 색인 → 랭킹。抓到不等于索引，索引不等于曝光。`[guid: report-crawl-refine]`
- **抓取优先级**：Yeti 给每个 URL 定「수집 우선순위」。抓取资源有限，先抓算法认为重要的 URL。索引规模也有上限，抓到不保证索引和曝光。`[guid: seo-advanced-javascript]`
- **웹페이지 수집요청**：每个站点有配额。它只把 URL 交给抓取系统，照样排队，需要 1 天到数周。同一 URL 不必每天重交。抓取成功不保证曝光。spam 站的请求会受限。`[guid: request-crawl]`
- **검색 제외**：先删原文 → 确认返回 404 → 在 요청 > 웹 페이지 검색 제외 提交 → 「재색인」后生效，不实时。`[guid: request-crawl]`
- **确认收录**：Yeti 访问后最多 1 周反映。`site:域名` 看当前索引；趋势看 사이트 진단，两者口径不同。`[guid: seo-basic-intro, report-diagnosis]`
- **没有收录登记**：网页搜索只靠 Yeti 自动抓取。注册并完成소유확인只解锁报表。站点按 host 注册，不支持路径级。`[guid: faq-start-register, seo-basic-intro]`

核对 2026-10-18。

## 二、Yeti 爬虫特性（官方文档蒸馏）

- **UA 两种形态**（版本会无预告变更）`[guid: seo-basic-firewall]`（修订 2026-05-11）：

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko; compatible; Yeti/1.1; +https://naver.me/spd) Chrome/W.X.Y.Z Safari/537.36
Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)
```

- **其他机器人**：`Ads-Naver` 为广告主页面采集补充信息；`Blueno` 采集链接预览。这类特殊用途机器人可能不遵守或不完全遵守 robots.txt，敏感内容要靠登录等手段保护。抓 JS 等资源时，Yeti 有时用浏览器 UA 加 `Yeti` 串。`[guid: seo-basic-firewall, seo-basic-robots, seo-advanced-javascript]`
- **真伪验证**：IP 的反向 DNS 须以 `.naver.com` 结尾，再正向解析回原 IP；或比对官方 CIDR 列表 `https://searchadvisor.naver.com/doc/naverbot.json`（会无预告变更）。`[guid: seo-basic-firewall]` 不要按 IP 封 Yeti（IP 段会变）；限制 Yeti 用 robots.txt。`[guid: seo-basic-intro]`
- **robots.txt 状态码** `[guid: seo-basic-robots]`（修订 2025-10-14）：2xx 按规则解析，但返回 HTML 可能被当作「没有 robots.txt＝全部允许」，文件须以 `text/plain` 提供；3xx 最多跟 5 次 HTTP 重定向，超过按全部允许，HTML/JS 重定向不解释；4xx 按全部允许；5xx 按全部不允许，之前抓到的规则可能临时沿用（原文没写时限；RFC 9309 §2.3.1.4 以 30 天为例）。
- **作用范围**：规则只对同一 host、协议、端口生效。`http://www.example.com/robots.txt` 不管 `http://example.com/` 和 `https://example.com/`。`[guid: seo-basic-robots]`
- **组匹配**（[RFC 9309](https://www.rfc-editor.org/rfc/rfc9309) §2.2.1；Naver 页面引用该 RFC）：有 `User-agent: Yeti` 组时，Yeti 只按该组执行，否则用 `*` 组；同名多组合并。冒号前可以有空格。
- **资源与 favicon**：页面允许抓、JS/CSS/favicon 却被 Disallow 时，Yeti 可能照样去抓，也可能解读不完整。规则要与页面一致，或直接放开。`Sitemap:` 行可写进 robots.txt。`[guid: seo-basic-robots, seo-advanced-javascript]`
- **渲染** `[guid: seo-advanced-javascript]`：没抓到 JS 时先按静态 HTML 索引 → JS 另行抓取，存入渲染服务器 → 再访时带 JS 渲染 → 主内容有变才更新索引。不建议给 JS URL 加 timestamp/hash。主要区域建议 SSR。fragment（`#`、`#!`）会被剥掉，独立内容要用 permalink。
- **수집 현황 的 9 类错误** `[guid: report-crawl-refine]`：로봇 비허용、DNS 오류、연결 실패、서버 오류（4xx/5xx）、페이지 오류（404）、콘텐츠 오류、URL 오류、单文档下载 ≥1 分钟、HTML ≥4MB（后两类是「可能」报错）。

核对 2026-10-18（含 RFC 9309 原文）。

## 三、Sitemap 规范（官方文档蒸馏）`[guid: request-feed]`

- 提交的 sitemap 和 RSS 被当作「콘텐츠 피드」，Yeti 定期回访。Yeti 取出 URL 后按算法筛选、排序再抓，不是提交即抓。
- **提交校验**：URL 与소유확인站点同域；超过 10MB 不能提交；不能含 50,000 个及以上 URL（原文「50,000개 이상」）；响应慢时可能限制提交。
- **格式**：sitemaps.org 0.9。`loc` 必填，`lastmod`/`changefreq`/`priority` 选填。量大用 sitemapindex。建议收录全部 URL。相对路径或 host 不一致的链接不抓。`[guid: seo-basic-intro]`
- robots.txt 的 `Sitemap:` 行会被 사이트 상태 报告识别。`[guid: site-summary]` URL 规模交给 sitemap，不交给 RSS。

核对 2026-10-18。

## 四、RSS 规范（官方文档蒸馏）`[guid: request-feed, seo-basic-intro]`

- RSS 2.0。每个 item 的 `<description>` 放全文，不放摘要。
- **提交校验**：同域；至少 1 个 `<item>`；超过 10MB 不能提交；响应慢时可能限制提交。
- RSS 用来主动通知新内容；它带全文，装不下大量 URL。官方「10 项优化方法」第 5 项：在 요청 菜单分别提交 sitemap 和 RSS。

核对 2026-10-18。

## 五、IndexNow（官方文档蒸馏）`[guid: indexnow-about/api-key/request/faq]`

- 端点 `https://searchadvisor.naver.com/indexnow`。变更会共享给其他参与的引擎。IndexNow 只通知，不保证索引。
- **Key**：UTF-8；只用 `a-f A-F 0-9 -`；长 8–128。推荐在根目录放 `{key}.txt`，内容就是 key。放在其他目录时须带 `keyLocation`，且只对该目录下的页面有效。每个域名单独一个 key。
- **提交**：单个 `GET /indexnow?url=...&key=...[&keyLocation=...]`（URL 符合 RFC 3986）；批量 `POST /indexnow`，JSON `{host, key, keyLocation?, urlList[]}`，一次最多 10,000 个 URL。
- **响应码**：200 成功；202 已收到、正在验证 key；400 格式错；403 key 无效；422 URL 与 key 不匹配；429 请求过多；500 服务器错误。
- **FAQ**：总请求数不限，突发会受限。不替代수집요청/RSS/sitemap。改为 404、301、302 也可通知。只提交开始使用后新增的 URL。

核对 2026-10-18（四页均修订于 2023-07-25）。

## 六、수집요청 API（제휴 API，官方文档蒸馏）`[guid: crawl-request-api]`（修订 2025-07-25）

- **前提**：① 经 [네이버 제휴제안](https://www.navercorp.com/naver/proposalRegister) 申请（제휴 구분：웹사이트-수집요청 API）并协商；② 完成소유확인，scheme、www、端口须与 API 中的站点完全一致；③ 目标 URL 允许 Yeti 抓取。
- **认证**：把 도구 설정 页的 accessToken 放进 `Authorization: Bearer ...`。须用 TLS 1.2 及以上。
- **端点**：`POST https://apis.naver.com/searchadvisor/crawl-request/submit.json`；`verify.json` 预检 payload 语法。
- **payload**：`{"urls":[{"url":"...","type":"update|delete"}]}`；一次 ≤1,000 个 URL、≤2MB。`update`＝Yeti 实访；`delete`＝从存储删除，不访问。同一 URL 两种都有时 `delete` 优先。只处理제휴站点的 URL。
- 只提交浏览器里看到的落地页 URL。与浏览器 URL 不同或被重定向时可能失败，计入「업데이트 실패」。重复内容只提交 canonical URL。
- **配额与错误码**：每天按 URL 数扣减；超额返回 1005（HTTP 402），之后的 URL 被丢弃。024 인증 실패、030 须用 HTTPS、064 超过 2MB、1003 未소유확인、1004 非제휴站点。
- **优先级与监控**：제휴 API 提交的 URL 优先级相对较高。大批量提交会让 Yeti 访问瞬时上升，要分散。리포트 > 제휴 API 현황 每 24 小时更新，盯住 업데이트 실패。

核对 2026-10-18。

## 七、结构化数据：类型矩阵与제휴依赖（官方文档蒸馏）

- schema.org 有 Microdata、RDFa、JSON-LD 三种格式；Naver 推荐 Microdata 或 JSON-LD。一页可组合多种类型。用 [validator.schema.org](https://validator.schema.org/) 验证。标记正确也不保证展示；各类型都只作辅助分析。`[guid: structured-data-intro]`

| 类型（guid） | 必填 | 需제휴 |
|---|---|---|
| 연관채널 Person/Organization（structured-data-channel） | name / url / sameAs；只认站点根页面上的标记 | 否。识别域名：네이버TV、블로그、스마트스토어、지식iN、치지직、당근、스레드、인스타그램、유튜브、카카오스토리、카카오톡 채널、티스토리、틱톡、페이스북、X（清单可变） |
| 주소 PostalAddress（structured-data-address） | streetAddress | 否 |
| BreadcrumbList（structured-data-breadcrumb） | name | 否 |
| 캐러셀 ListItem（structured-data-carousel） | image（写 item 时放进 item） | 否 |
| 평점 AggregateRating（structured-data-rating） | ratingValue；ratingCount、reviewCount 至少一个（都有时显示 ratingCount） | 否 |
| 레시피 Recipe（structured-data-recipe） | recipeInstructions | 否 |
| 리뷰 Review（structured-data-review） | reviewBody | 否 |
| 식당 Restaurant（structured-data-restaurant） | name / openingHours | 否 |
| TV 시리즈、영화（structured-data-tvseries、structured-data-movie） | name / actor | 否 |
| SoftwareApplication（structured-data-software） | name / applicationCategory | 否 |
| **JobPosting（structured-data-job，修订 2025-04-09）** | 最小集：title、datePosted、validThrough、employmentType、experienceRequirements、jobLocation、description、hiringOrganization、identifier | **是**：제휴제안（콘텐츠 및 서비스）→ JSON-LD → 수집요청 API → robots 允许 |
| **VideoObject + 频道 Person（structured-data-video，修订 2026-10-12）** | Video：name、description、url、thumbnailUrl、uploadDate（含秒和时区）、duration、cid（Naver 扩展）、creator（Person 的 name、url）。Channel：name、url、cid、description、mainEntityOfPage 的 dateCreated/dateModified | **是**：[제휴제안](https://www.navercorp.com/company/partnerApply)（서비스 콘텐츠 제휴 > 동영상콘텐츠 제휴）→ 用 API Push URL → Yeti Pull |

- **JobPosting**：employmentType 可用韩文或英文枚举；experienceRequirements、workHours、educationRequirements 用韩文枚举。薪资只填数字（韩元），currency 填 KRW。猎头公告加 `"hiringtype":"headhunting"`。常年招聘不写 validThrough。`[guid: structured-data-job]`
- **VideoObject**：每页一个顶层对象，不用 `@graph`。搜索结果 URL、浏览器渲染 URL、结构化数据所在 URL 三者须相同。带 `offers` 的影片按付费处理，**被排除出搜索结果**；免费影片不写 offers（含 0 元）。需登录的影片要事先协商。原文允许只对 Naver 爬虫 UA 返回结构化数据。`[guid: structured-data-video]`
- 表中 job、video 以外的类型页都在 2026-10-15 修订过。HowTo：来源仓 2026-07 快照有 `structured-data-howto`；2026-10-18 该页返回 500、菜单无此篇，不再列入。
- **2026-10-15 起的显示变化（官方公告）**：网页、博客、카페、지식iN、视频结果统一模板。① 파비콘建议尺寸改为 32px（显示变大，小图会糊）；② 사이트 이동경로显示在站点信息第二行；③ 地址、评分、食谱、评论、餐厅、电视剧、电影、软件这几类 schema 只在正文下方显示精简摘要，部分字段不再显示；④ **HowTo 专属结果停止显示**，改按普通结果显示，不影响收录、索引和排名，已有标记不必删，但不再用于显示（[公告](https://blog.naver.com/naver_webmaster/224442540254)）。
- **FAQ 卡片 2026-07-09（KST）起停止显示**：留着 FAQ 标记不影响排名和显示，官方说仍可能辅助文档分析（[公告](https://blog.naver.com/naver_webmaster/224340385532)）。审计时 Naver 的 FAQ、HowTo 都不再算「可拿富结果」。

核对 2026-10-18；三条公告 2026-11-05 补核。

## 八、웹 검색 与서비스 영역：两条通道（官方文档蒸馏）

- **两条通道**：Yeti 抓的自有站点内容进 웹 검색 영역。VIEW、블로그、기업/학교/명소/게임 等콘텐츠 정보 영역另算；채용정보 영역靠제휴。招聘信息可同时出现在 웹 검색 和 통합검색 채용정보 영역（原文标「제공 예정」）。noindex 可把页面排除出 웹 검색；제휴영역是否遵守 noindex 按协议定。`[guid: report-expose-ctr, structured-data-job]`
- **报表只计 웹 검색**：노출/클릭不含 VIEW、블로그 검색、콘텐츠 정보 영역、搜索广告。从 업데이트 기준일（1 周前的数据）往回 90 天；窗口 1/7/30/60/90 天；按点击给出关键词和网页 TOP 30。`[guid: report-expose-ctr]`
- **서브링크**（修订 2026-10-15）：自动生成，不能申请。单条退出用 `<a rel="nosublink">`；全站退出用 `<meta name="naver" content="nosublinks">`。`[guid: faq-sublink]`
- **SERP 标题、说明、缩略图**：引擎从 title、description、OG、앵커中自动选，Naver 不接受人工修改。meta 与 OG 不一致时，选更适合搜索的值。`[guid: faq-serpedit]`
- **사이트 브랜드 정보란**（2026-10-16 新增）：URL 旁的品牌名由 Yeti 自动抽取，不能指定；显示错误可找고객센터。`[guid: faq-branding]`

核对 2026-10-18。

## 九、标记层规范速查（官方文档蒸馏）

- **canonical**：用绝对路径。首页优先用 HTTP 重定向。`[guid: markup-structure]`
- **robots meta**（修订 2025-12-11）：`noindex` 排除出搜索结果；`nofollow` 不抓页内链接；`nosourceinfo`＝Naver 不为该站提供「AI로 자동 생성된 출처설명」（AI 自动生成的出处说明）。只做重定向的页面，meta 可能不生效，目标页要同样设置。`[guid: markup-structure]`
- **og:image**（建议检查项）：大于 150×150、≥5,000 字节、宽高比 ≤3:1、每页唯一。多页重复的图、全站 logo、宣传横幅可能不被采用。`[guid: markup-content]`
- **favicon**（修订 2026-10-15）：正方形，最小 16px，建议 ≥32px。支持 ICO/PNG/GIF/动图 GIF/JPEG/APNG/SVG。href 用绝对路径。优先级：shortcut icon > icon > `/favicon.ico` > apple-touch-icon > apple-touch-icon-precomposed。同一 rel 只写一个。不要频繁改 URL。须允许 Yeti 抓取。`[guid: markup-favicon]`
- **title/description**：title 无硬性字数限制，但不要过长。全站同 title、关键词重复 2 次以上、spam 词、无关词都可能受罚。description 用 1–2 句。사이트 간단 체크 建议 title ≤40 字、description ≤80 字。`[guid: markup-content, diagnose-site]`
- **重定向**：永久变更用 301，临时用 302。避免 JS 重定向；meta refresh 可识别，但尽量用 HTTP 重定向。连续重定向建议不超过 5 次，链上每个 URL 都须可抓。临时挡 Yeti 用수집 설정的트래픽 제한，不用 robots.txt（期间已收录的文档可能被移出）。`[guid: seo-basic-redirect]`
- **迁移**：旧 URL 用 301 一对一到新 URL；新站全部页面设 canonical；注册新站并提交 sitemap；新域名被识别可能至少要 2–3 天。迁移完成前，旧站不要先设 robots.txt 屏蔽，也不要先断网或封网。`[guid: seo-basic-migration]`
- **소유확인**：不执行 JS，不跟随 JS、meta refresh、cookie 跳转（要用 HTTP 301/302）。验证 meta 须在 `<head>`；放在 frame 或 body 里不认。`[guid: faq-start-register]`
- **移动端**：推荐响应式。独立 m. 站时，移动页 canonical 一对一指向桌面页，两站都注册；按 UA 跳转用 HTTP 重定向。`[guid: markup-mobile, seo-basic-create]`

核对 2026-10-18。

## 十、官方工具清单（官方文档蒸馏）

| 工具 | 位置 | 要点（guid） |
|---|---|---|
| 사이트 간단 체크 | `/tools/sitecheck`（无需先注册站点） | 实时访问首页：Yeti 能否访问、robots.txt、title/description 40/80 字、noindex、RSS/sitemap `[diagnose-site]` |
| URL 검사 | 검증 > URL 검사 | 색인/Meta/SEO 三张表；排查被黑时看 Yeti 实际抓到的 HTML `[url-inspection, content-abusing]` |
| 사이트 진단 | 리포트 | 색인/수집제한/색인제외/SEO 四类，按天快照，分析近 90 天抓到的页面；明细最多下载 2,000 条；소유확인后至少 1 篇被抓、最少约 1 周才生成 `[report-diagnosis]` |
| 사이트 최적화 | 리포트 | AI 评估算法打分，是排名的间接指标，不保证排名；四类：검색 로봇 수집/콘텐츠 관리/사이트 구조/사이트 활성화 `[report-seo]` |
| 사이트 상태 | 리포트 | 보안 인증서/HTTPS 리다이렉션/사이트맵，1–2 天更新；Yeti 优先抓 HTTPS，HTTP 与 HTTPS 并存且不重定向，会重复抓取并可能受罚 `[site-summary]` |
| 수집 현황、콘텐츠 노출 및 클릭 | 리포트 | 见第二、八节 `[report-crawl-refine, report-expose-ctr]` |

- **2026-10 起报表口径变动**：系统迁移，리포트 里사이트 진단（색인、색인 제외）和콘텐츠 노출/클릭数值从 2026 年 10 月的数据起陆续变化；官方说只是统计显示差异，和收录、显示、排名无关（[公告](https://blog.naver.com/naver_webmaster/224456824688)，2026-10-28）。跨 2026-09/10 做环比要打断点，不当成真实涨跌。
| robots.txt 도구 | 웹마스터도구 | 수집 및 검증（请求重抓、测试规则）、간단 생성 `[seo-basic-robots]` |
| 교육 자료 PDF | `/doc/wmt_guide_ps_websearch.pdf`、`/doc/wmt_guide_ps_quality.pdf` | 웹 검색 기초、웹마스터도구 활용 `[education-basic, education-wmt-advanced]` |

核对 2026-10-18。

## 十一、审计红旗（判 P0/P1 用）

- robots.txt 返回 5xx（Yeti 按全部不允许处理，本套件判 P0）；apex 与 www 的 robots.txt 不一致。`[guid: seo-basic-robots]`
- 页面允许抓，但 JS/CSS/图片被 Disallow 或 IP 被封；`<a href>` 写成 JS 调用；HTTPS 页引用同 host 的 `http://` 资源。`[guid: resource-and-link]`
- 错误页返回 200（soft 404），或只有 JS 跳转的空 HTML → 被当作불용문서排除。应按情况返回 404/403/301/503。`[guid: seo-advanced-indexing]`
- **spam 类型**（修订 2026-07-03，18 类）：클로킹（含按 Referer/UA 区别展示）、부적절한 리다이렉트、링크 스팸、백링크 악용、만료 도메인 악용、매크로 및 조작 행위、해킹된 콘텐츠、악성코드 배포、숨겨진 텍스트、키워드 반복·남용、낚시성、저품질 콘텐츠 대량 생성、스크래핑、유해 콘텐츠、사용자 혼동 및 피해 유발 콘텐츠、유사 공공사이트、피싱、서비스 안정성 저해。저품질 대량 생성＝用相同或相似模板大量发布（如只改几句的页面数十个以上）；不只凭是否用了 AI 或自动化来判断。处罚＝排除出搜索或降低排名。整改后可附事实和整改记录，申请검색 노출 정상화。`[guid: content-abusing]`

核对 2026-10-18。

## 十二、检查清单

`$S`＝本套件根目录（skills/seo-suite）。括号里是阈值出处；「本套件口径」是本套件的判定约定。格式：检查什么 → 怎么查 → 通过/失败。

1. **robots.txt 状态与类型**（seo-basic-robots）→ 对 http/https × apex/www 各跑 `curl -sI https://<host>/robots.txt`；有跳转时跑 `python3 $S/scripts/redirect_chain.py https://<host>/robots.txt --max 5` → 通过：2xx 且 `text/plain`。失败：5xx（P0）、返回 HTML、跳转超过 5 次。
2. **Yeti 组与资源放行**（seo-basic-robots、RFC 9309）→ `curl -s https://<host>/robots.txt | grep -n -i -E '^\s*user-agent\s*:\s*(yeti|\*)'`（容忍冒号前空格）；再用 robots.txt 도구「수집 및 검증」测关键页及其 JS/CSS/favicon → 通过：全部允许。失败：任一被 Disallow。
3. **Yeti UA 能否访问**（seo-basic-firewall）→ `curl -s -o /dev/null -w '%{http_code}\n' -A 'Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)' https://<host>/`，再用浏览器 UA 跑一次 → 通过：两次都是 2xx。失败：只有 Yeti UA 得 403/429/5xx，要查 WAF。WAF 按 IP 验真爬虫时会拦伪造 UA，这时改用 사이트 간단 체크 复核（本套件口径）。
4. **日志里 Yeti 的真伪**（seo-basic-firewall）→ `python3 $S/scripts/log_session.py --log access.log --ua Yeti` 取 IP；`host <IP>`，再 `host <返回的域名>`；或下载 naverbot.json 后跑 `python3 -c "import json,ipaddress,sys;n=[ipaddress.ip_network(p['ipv4Prefix']) for p in json.load(open('naverbot.json'))['prefixes']];print(any(ipaddress.ip_address(sys.argv[1]) in x for x in n))" <IP>` → 通过：域名以 `.naver.com` 结尾且正向解析回原 IP，或输出 True。失败：两项都不符。
5. **sitemap 与 RSS**（request-feed）→ `curl -s -o sm.xml -w '%{size_download}\n' <sitemap URL>`；`grep -o '<loc>' sm.xml | wc -l`；`python3 $S/scripts/sitemap_audit.py <sitemap URL>`；RSS 用 `grep -c '<item>'` 并抽查 `<description>` → 通过：<10MB、条数低于 Naver 上限（见上文「提交校验」）、全部是同域绝对 URL；RSS ≥1 个 item 且是全文。失败：任一不符。
6. **IndexNow**（indexnow-*）→ `python3 $S/scripts/indexnow.py key --out .`，把 `{key}.txt` 放根目录；`python3 $S/scripts/indexnow.py submit --host <host> --key <key> --urls urls.txt --endpoint naver` → 通过：200 或 202。失败：403、422、429。
7. **重定向链**（seo-basic-redirect）→ `python3 $S/scripts/redirect_chain.py <旧 URL> --max 5` → 通过：≤5 次、永久迁移用 301、终点 200 且可抓。失败：超限、循环、链中有 Disallow 的 URL。
8. **noindex 与 nosourceinfo**（markup-structure、faq-serpmissing）→ `curl -sI <URL> | grep -i x-robots-tag`；`curl -s <URL> | grep -i -o '<meta[^>]*name="robots"[^>]*>'` → 通过：要收录的页在响应头和 meta 里都没有 noindex；出现 nosourceinfo 时有书面决策（本套件口径）。失败：要收录的页带 noindex。
9. **og:image**（markup-content）→ `python3 $S/scripts/head_check.py <URL>` 查存在与绝对 URL；`curl -s -o og.img -w '%{size_download}\n' <图片 URL>` 看字节；`file og.img` 看宽高 → 通过：大于 150×150、≥5,000 字节、宽高比 ≤3:1、各页不同。失败：任一不符。
10. **站点总体与收录**（diagnose-site、report-diagnosis）→ 跑 `/tools/sitecheck`；在 Naver 搜 `site:<host>`；리포트 > 사이트 진단 下载明细；单页用 URL 검사 → 通过：简单检查无报警，重要 URL 在 색인。失败：重要 URL 在 수집제한/색인제외，按对应 guid 修，再等 Yeti 回访或用수집요청。
