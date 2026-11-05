# 图片 SEO 与视觉搜索(被 AI 看见的图片层)

> 建立于 2026-10-09;2026-10-21 逐条重新核对:官方事实附一手链接;没有出处的行业数字已删除;第三方研究标「第三方」并写年份。与 [视频 GEO 指南](video-geo-guide.md) 互补。「本套件口径」是做法约定,不是 Google 规则。

## 一、视觉搜索的量级与测量(官方)

- **Lens 用量**:Google 在 2024-10-03 写明 Lens 每月「nearly 20 billion」次视觉搜索([blog.google](https://blog.google/products-and-platforms/products/search/google-search-lens-october-2024-updates/));同日广告博客称其中 20% 与购物相关([blog.google/ads-commerce](https://blog.google/products/ads-commerce/google-lens-ai-overviews-ads-marketers/))。2025-04 财报电话会称自 2024-10 起每月又增加 50 亿次([Alphabet 2025 Q1 电话会](https://abc.xyz/investor/events/event-details/2025/2025-Q1-Earnings-Call/),摘要读到)。引用时写年份,不要把 2024 年的数字写成「2026 年现值」。
- **官方测量面**:2026-09-24 起,Search Console 效果报告新增 multimodal 搜索类型筛选,覆盖 Lens、Android 的 Circle to Search、向 Google 搜索上传图片、Chrome 右键「Search this image」,并同步进生成式 AI 报告,全球逐步上线([Search Central 博客 2026-09-24](https://developers.google.com/search/blog/2026/09/web-multimodal-in-sc))。
- **图片搜索 UI 一改,流量会大变(历史案例)**:2013 年 Google 图片搜索改版后,Define Media Group 研究的 87 个域名平均图片搜索引荐降 63%([Search Engine Land 2013-04-15](https://searchengineland.com/study-google-image-search-referrer-traffic-drops-63-since-upgrade-155879),第三方)。含义:图片搜索流量不适合当业务基线。
- **本站占比怎么看**:不用行业平均数。在 Search Console 效果报告里,「搜索类型」分别选「图片」「网页」,比较点击;再选 multimodal 筛选看视觉入口(本套件口径)。
- 带购物意图的图片流量,入口在 Lens 的商品结果和商品轮播,不在传统图片结果页:图要进 Merchant Center feed,并与页面 Product 数据一致(第五节)。

## 二、Lens 排名的第三方证据(Backlinko,2020)

Backlinko 分析了 65,388 次 Google Lens 搜索结果(2020 年发布;第三方、相关性研究,不是 Google 说明;Lens 此后改过多次,只作方向参考)([Backlinko](https://backlinko.com/visual-search-ranking-factors)):

| 观察 | 数字 |
|---|---|
| 结果页面的 Moz 域名权威均值 | DA 64.4(页面权威 PA 35.2) |
| 结果来自移动友好网站 | 90.6% |
| 结果图片位于页面上方 25% | 约三分之一(33.1%) |
| 图片 alt 与搜索图的最佳猜测标签匹配 | 11.4% |
| 文件名匹配 | 22.6% |
| 标题含匹配关键词 | 32.5% |
| 同词同时进自然搜索第一页 | 15% |

- 作者自己的措辞是「potential ranking factors」。这些是共现比例,不能推出因果。
- 本套件口径的做法:图片放在与主题相关、本来就有排名的页面上;重要图放在页面上部;alt 照官方写法写,但不指望靠它排名。

## 三、AI 引擎怎么用图片

- 官方:生成式 AI 搜索功能可以带入相关图片和视频;建议在合适时用高质量图片和视频支撑文字([AI 功能优化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide),2026-07-10 更新)。同一份指南说不需要为 AI 搜索专门改写内容。
- 官方:Google 不索引 CSS 图片;关键图用 `<img>` 或 `<picture>`([图片 SEO 最佳做法](https://developers.google.com/search/docs/appearance/google-images),2026-03-02 更新)。
- **首选图**:官方给了三种元数据来源:`primaryImageOfPage`、挂在主实体上的 `image`、`og:image`;2026-03-02 文档写明 Google 两类来源(schema.org 与 og:image)都用,并建议:图相关且有代表性;不用站点 logo 或带文字的图;避免极端长宽比;尽量高分辨率(同上)。
- **未证实**:图片的视觉内容(不是 alt)是否影响文字页被 AI 引用。没有对照研究。
- 「AI 概览引用的图只来自 `<img src>`」只见于第三方工具厂商的观察,本套件不当规则写(未核)。

## 四、图片 SEO 要素(官方,核对 2026-10-21)

出处:[图片 SEO 最佳做法](https://developers.google.com/search/docs/appearance/google-images)(2026-03-02 更新)、[图片 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps)(2025-12-10 更新)。

1. **alt 文本**:官方称它是图片元数据里最重要的属性。写信息丰富、贴合页面上下文的描述,不堆关键词。图片作链接时,alt 兼作锚文本。内联 SVG 用 `<title>`。
2. **文件名**:只给「very light clues」;短而有描述性,例如 `my-new-black-kitten.jpg` 好于 `IMG00023.JPG`;本地化页面连文件名一起翻译。
3. **页面上下文**:Google 从页面内容、图注和图片标题理解图片;图放在相关文字附近。
4. **结构化数据**:`image` 是图片结果徽章(badge)和富结果的必填字段。要在图片结果里显示创作者、版权、授权信息,用[图片元数据](https://developers.google.com/search/docs/appearance/structured-data/image-license-metadata)(IPTC 或结构化数据)。
5. **格式**:Google 图片搜索收录 BMP、GIF、JPEG、PNG、WebP、SVG、AVIF;文件扩展名与类型一致。`srcset` 或 `<picture>` 要配 `src` 回退。同一张图在站内始终用同一个 URL,方便缓存。
6. **体积**:WebP 有损图比同等质量(SSIM)的 JPEG 小 25–34%([WebP 官方页](https://developers.google.com/speed/webp));首屏大图(LCP 图)不要 `loading="lazy"`([web.dev](https://web.dev/articles/lcp-lazy-loading))。
7. **退出内联展示**:图片请求的 referrer 来自 Google 域名时,返回 200 或 204 且无内容,Google 会用抓取时生成的缩略图,官方说这不算 cloaking、不会触发人工处置。
8. **EXIF/GPS**:本组没有找到 Google 官方文档说明如何使用它们,旧版「官方明确不用」已删除;不要为 SEO 给图片加地理标签,也不要靠它做本地排名(未核)。

**图片 sitemap**

- 只有 `<image:image>` 和 `<image:loc>` 两个标签;`<image:caption>`、`<image:geo_location>`、`<image:title>`、`<image:license>` 已从文档删除。每个 `<url>` 最多 1,000 个 `<image:image>`。
- `<image:loc>` 可指向别的域名(CDN),前提是该域名在 Search Console 验证过,且其 robots.txt 不禁止抓取你要收录的图片。
- 命名空间:`http://www.google.com/schemas/sitemap-image/1.1`。
- 官方没有「图片索引量」报告,本套件不给替代指标。

## 五、电商图片:Merchant Center 与页面一致

出处:[Merchant Center image_link 说明](https://support.google.com/merchants/answer/6324350)。

- 主图用 `image_link`;其他角度和细节图用 `additional_image_link`;场景图可作为附加图。
- 尺寸:官方写明自 2027-01-31 起所有商品图至少 500×500 像素;为了在所有展示形态里表现最好,建议约 1500×1500 或更大;单图不超过 64 兆像素。
- 主图不能含促销文字、行动号召(「Buy」「Shop now」)、促销形容词、「New」之类状态标签、水印和版权符号,不能用 logo 或占位图代替商品图;含这些的图会被拒。
- 本套件口径:feed 的 `image_link` 与页面 Product 结构化数据的 `image` 指向同一 URL;页面有多角度实拍,不只放渲染图。

## 六、版权、来源与抓取

- **AI 抓取控制**:robots.txt 对各 AI 爬虫的规则见 [ai-crawler-policy.md](../technical/ai-crawler-policy.md)。Cloudflare 2025-07-01 推出一键屏蔽 AI 爬虫与 Pay Per Crawl(私测)([Cloudflare 博客](https://blog.cloudflare.com/introducing-pay-per-crawl/))。
- **Getty Images v Stability AI(英国高等法院,2025-11-04 判决)**:Getty 的二次版权侵权主张被驳回;商标主张在有限范围内成立(涉及水印)([Latham & Watkins 2025-11-13](https://www.lw.com/en/insights/getty-images-v-stability-ai-english-high-court-rejects-secondary-copyright-claim),第三方律所摘要;判决原文 [judiciary.uk](https://www.judiciary.uk/wp-content/uploads/2025/11/Getty-Images-v-Stability-AI.pdf))。含义有限:水印是维权证据,不能当防抓取手段(本套件口径)。
- **C2PA / Content Credentials**:
  - TikTok 在 2026-07-27 由普通成员升为 C2PA 指导委员会成员,称已把 30 亿以上内容标为 AI 生成([C2PA 公告](https://c2pa.org/c2pa-welcomes-tiktok-to-steering-committee/))。
  - LinkedIn 在其帮助页说明采用 C2PA 并展示 Content Credentials,功能逐步开放([LinkedIn 帮助](https://www.linkedin.com/help/linkedin/answer/a6282984))。
  - 欧盟 AI 法案第 50 条透明度义务自 2026-08-02 起适用([欧盟委员会](https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations));经 Digital Omnibus,机器可读标记(水印)义务对部分系统的适用日期晚至 2026-12-02([Mayer Brown 2026-07-30](https://www.mayerbrown.com/en/insights/publications/2026/07/eu-ai-act-news-digital-omnibus-on-ai-new-guidance-on-risk-classification-gpai-and-transparency-obligations),第三方律所摘要)。具体义务以法规原文和法律意见为准。
  - Google 没有声明 C2PA 影响排名。把它当合规与信任投入,不当排名手段(本套件口径)。
  - 证明来源不等于证明所有权。

## 七、检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| alt 是否缺失 | `python3 scripts/site_audit.py URL --json`,看 alt 相关 finding | 内容图都有描述性 alt 为通过;内容图缺 alt 为失败 |
| 关键视觉是否是 CSS 背景图 | 浏览器开发者工具 Elements 看首屏主图是 `<img>` 还是 `background-image` | 首屏主图为 `<img>` 或 `<picture>` 为通过 |
| 首选图 | `python3 scripts/head_check.py URL` 第 4 项(og:image 绝对 URL);`curl -s URL \| grep -o '"image"[^,]*'` | og:image 为绝对 URL 且与 schema `image` 指向相关主图,不是 logo 或文字图为通过 |
| 图片 sitemap 合规 | `xmllint --noout sitemap-images.xml`;`grep -c '<image:image>' sitemap-images.xml`;`grep -E 'image:(caption\|geo_location\|title\|license)' sitemap-images.xml` | 语法正确、单个 `<url>` ≤1,000、无已删除标签为通过 |
| CDN 域名可抓 | `curl -s -A "Googlebot-Image" -o /dev/null -w "%{http_code}\n" https://cdn.example.com/img.jpg`;Search Console 确认 CDN 域名已验证 | 返回 200 且域名已验证为通过 |
| robots 没拦图片目录 | `curl -s https://example.com/robots.txt \| grep -i -E 'disallow.*(upload\|image\|media\|assets)'` | 无命中为通过 |
| 同图同 URL | 站内抽查同一张图在不同页面的 `src` | 同图同 URL 为通过;每页各生成一个 URL 为失败 |
| LCP 图未懒加载 | 浏览器 Elements 看首屏主图是否有 `loading="lazy"` | 没有为通过 |
| 电商主图合规 | Merchant Center 商品诊断;对照第五节规则 | 无图片政策问题、尺寸达标为通过 |
| 视觉搜索测量 | Search Console 效果报告选 multimodal 筛选,导出 CSV;`python3 scripts/multimodal_report.py --gsc gsc.csv` | 能导出并按页面聚合为通过 |

## 八、常见误区

- 把 2013 年或 2020 年的研究数字当作 2026 年现状引用。
- 把 Backlinko 的共现比例当成 Lens 排名因素。
- 给图片加 GPS 地理标签以为能提高本地排名(本组没有找到官方依据)。
- 电商主图加促销文字或水印,被 Merchant Center 拒绝。
- 把行业平均的「图片流量占比」直接写进报告,不看本站数据。

## 来源

- 官方:[图片 SEO 最佳做法](https://developers.google.com/search/docs/appearance/google-images)、[图片 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps)、[AI 功能优化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)、[Search Console multimodal 报告博客 2026-09-24](https://developers.google.com/search/blog/2026/09/web-multimodal-in-sc)、[Lens 用量博客 2024-10-03](https://blog.google/products-and-platforms/products/search/google-search-lens-october-2024-updates/)、[Merchant Center image_link](https://support.google.com/merchants/answer/6324350)、[图片元数据](https://developers.google.com/search/docs/appearance/structured-data/image-license-metadata)、[WebP](https://developers.google.com/speed/webp)、[web.dev LCP 懒加载](https://web.dev/articles/lcp-lazy-loading)、C2PA / LinkedIn / 欧盟委员会页面(链接见正文)。
- 第三方:Backlinko Lens 研究(2020)、Define Media Group 经 Search Engine Land(2013)、Latham & Watkins、Mayer Brown。
- 2026-10-21 删除的旧说法(没找到一手或可信出处):Lens 月 200 亿次「2025 Q3 财报」归属与「绝大部分增量」、YouGov「快 5 倍」、seoClarity「实际引荐约 2%」、图片 CTR「约 3%」、Netguru「Lens 40 亿购物」(与 20 亿总量自相矛盾)、某电商「点击 +85.86%」、Pinterest「80B+ 商品库、80% 无品牌词」、「EXIF/GPS 官方明确不用」、拍立淘/Naver Smart Lens 三体系对照表、「AVIF 比 JPEG 省 25–35%」、「Getty 训练数据版权诉败」(实际是二次侵权主张被驳回)、「TikTok 2025-01 加入 C2PA 指导委员会」(实际 2026-07-27)。
