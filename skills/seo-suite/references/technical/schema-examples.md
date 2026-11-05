# 结构化数据：按页面类型组合

> 涉及 FAQPage 或 AI 引用的判断，先读 [geo-evidence.md](../content/geo-evidence.md)。

## 用途

一个页面需要同时描述多个实体时读，例如文章页既有文章本身，又有面包屑、作者和发布者。单个类型怎么选、Google 必填属性见 [schema-templates.md](schema-templates.md)；验证见 [validation-guide.md](validation-guide.md)。

## 一、组合原则（本套件口径）

1. **用 `@graph` 放在同一个脚本里。** 同一页面的多个节点放进一个 `@graph` 数组（[JSON-LD 1.1](https://www.w3.org/TR/json-ld11/) 的命名图语法），节点之间用 `{"@id": "…"}` 互相引用，不在多处嵌套重复写同一实体。
2. **一个实体在一个页面里只声明一次。** 多个插件、主题或前端组件各输出一份 Organization 很常见：先列出所有输出结构化数据的来源（CMS 插件、主题、标签管理器、前端组件），指定唯一负责方。
3. **`@id` 全站稳定。** 用规范 URL 加片段命名，例如 `https://example.com/#organization`；不带跟踪参数，与 canonical 一致，改版时不变。
4. **每个页面的数据要能独立成立。** Google 文档没有承诺会跨页面解析 `@id`（工程判断）。站点级实体的完整信息放在首页；其他页面保留同一 `@id`、只含 name、url 等少量字段的精简节点。Google 也建议 Organization 放首页或单个介绍页，不需要每页都放（[Organization](https://developers.google.com/search/docs/appearance/structured-data/organization)，核对 2026-10-18）。
5. **主实体只有一个。** 文章页的主角是文章，商品页的主角是商品；Organization、WebSite 是被引用的配角。

## 二、按页面类型的常见组合

| 页面 | 主实体 | 常见组合 |
|---|---|---|
| 首页 | Organization、WebSite | WebSite 的 `publisher` 指向 Organization |
| 文章页 | Article / BlogPosting | + BreadcrumbList；`author` 指向作者 Person；`publisher` 指向 Organization |
| 作者页 | Person（可放在 ProfilePage 的 `mainEntity` 里） | Person 的 `@id` 供全站文章的 `author` 引用 |
| 商品详情页 | Product + Offer | + BreadcrumbList；`brand` 指向品牌；评分只在页面上有真实评价时才加 |
| 分类 / 列表页 | 可用 CollectionPage 描述页面 | + BreadcrumbList；Google 建议商品标记放商品页，不放列表页 |
| 门店页 | LocalBusiness 的具体子类型 | + BreadcrumbList；`parentOrganization` 指向总公司（`branchOf` 已被 schema.org 标为由 `parentOrganization` 取代） |
| 软件 / SaaS 产品页 | SoftwareApplication 或 Product | 评分要求见 [schema-templates.md](schema-templates.md) |

WebPage 节点（`isPartOf`、`breadcrumb` 等关系）可以表达页面结构，Google 富结果不要求它；加不加按维护成本决定。

## 三、组合示例（自写，文章页）

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "示例品牌",
      "url": "https://example.com/"
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "name": "示例品牌",
      "url": "https://example.com/",
      "publisher": { "@id": "https://example.com/#organization" }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://example.com/guides/robots-check#breadcrumb",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "指南", "item": "https://example.com/guides/" },
        { "@type": "ListItem", "position": 2, "name": "如何核对 robots.txt 规则" }
      ]
    },
    {
      "@type": "BlogPosting",
      "@id": "https://example.com/guides/robots-check#article",
      "headline": "如何核对 robots.txt 规则",
      "datePublished": "2026-03-02T09:00:00+08:00",
      "mainEntityOfPage": "https://example.com/guides/robots-check",
      "isPartOf": { "@id": "https://example.com/#website" },
      "author": { "@id": "https://example.com/authors/zhang-san#person" },
      "publisher": { "@id": "https://example.com/#organization" }
    },
    {
      "@type": "Person",
      "@id": "https://example.com/authors/zhang-san#person",
      "name": "张三",
      "url": "https://example.com/authors/zhang-san"
    }
  ]
}
```

要点：Organization 和 WebSite 是精简节点，完整信息在首页。面包屑至少两项；最后一项可以不写 `item`，Google 会用当前页 URL（[Breadcrumb](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)）。所有值都必须能在页面上看到。

## 四、实施要点

- 可见内容和 JSON-LD 从同一份数据生成，避免漂移。
- 序列化时至少把 `<` 写成 `\u003c`，防止内容里的 `</script>` 截断脚本（依据和第三方实现对照见 [schema-templates.md](schema-templates.md)「完全装载」节）。
- 同一实体不要同时用 microdata 和 JSON-LD 各写一份；确需并存时内容必须一致。评价类标记尤其要避免用多种方式表示「被评价的是什么」（Google 2025-11-12 在评价摘要文档里补充的说明）。
- 验证时除了看报错，还要看节点之间的引用是否都能对上。

## 富结果状态速查（2026-10-21 按 Google 文档更新记录核对）

依据：[文档更新记录](https://developers.google.com/search/updates) 与 [类型库](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)（类型库页面最后更新 2026-10-16）。2026-10-21 逐条重读了更新记录原文，日期按其 What/Why 条目写。

**已停展（存量标记无害，但没有展示收益）**：

| 功能 | 关键日期 |
|---|---|
| FAQ | 先只给权威政府、健康网站，后停展，文档已删（[日期](../overview/facts.md#rich-results)） |
| HowTo | 先移动端停展，后桌面停展（[日期](../overview/facts.md#rich-results)） |
| 站点链接搜索框 | 2024-11-21 起停展；2024-11-29 删文档 |
| Home activities | 2024-06-11 删文档 |
| Course info、Claim review、Estimated salary、Learning video、Special announcement、Vehicle listing | 2025-06-12 公告逐步停用；Special announcement 2025-07-31 起停用；2025-09-09 删除 Course info、Estimated salary、Learning video、Special announcement、Vehicle listing 的文档 |
| Practice problem | 2025-11-05 加弃用通知；2026-01-06 删文档 |

**仍在类型库里**：Article、Breadcrumb（2025-01-22 起只在桌面显示）、Carousel、Course list、Dataset（只用于 Dataset Search）、Discussion forum、Education Q&A、Employer aggregate rating、Event、Image metadata、Job posting、Local business、Math solver、Movie、Organization、Product（含商家信息）、Profile page、Q&A、Recipe、Review snippet、Software app、Speakable、Subscription and paywalled content、Vacation rental、Video。

**近期字段与政策变化**：

- 商家信息：2026-05-20 新增 `hasAdultConsideration`；2026-07-07 新增 `Product.category` 用法和促销价有效期（`validFrom`/`validThrough`/`priceValidUntil`）说明。
- 评价摘要：2025-01-15 新增建议：只接受带评论和作者名的评分（是建议，不是必填）；2025-11-12 说明不要用多种方式表示被评价对象；2026-07-24 新增准则：不得在页面或标记里包含虚假评价或未披露的激励评价。违反准则可能招致人工处置。
- VideoObject：2026-09-24 新增推荐属性 `creator`（Person 或 Organization，也认 `author`），并写明 `interactionStatistic` 支持 WatchAction、LikeAction、CommentAction、ShareAction 四种（[VideoObject](https://developers.google.com/search/docs/appearance/structured-data/video)，核对 2026-11-05）。细节见 [video-geo-guide.md](../content/video-geo-guide.md) 第二节。
- 评价摘要 2026-07-24 那条（虚假或未披露激励评价）复核于 2026-11-05：原文举的两例是「不是基于真实体验的评价」和「为换取好处（钱、折扣、代金券、免费产品）而写、又没有清楚显著披露激励的评价」（[review snippet 准则](https://developers.google.com/search/docs/appearance/structured-data/review-snippet#guidelines)）。GEO 侧的风险线见 [geo-evidence.md](../content/geo-evidence.md)「GEO 手法风险线」。
- Organization：2023-11-29 新的 Organization 文档合并了原 Logo 文档；`name`/`alternateName` 与站点名称一致。
- 垃圾内容政策：2026-05-15 明确同样适用于 Google 搜索里的生成式 AI 回答。

**澄清**：

- LocalBusiness 仍在类型库里：可影响知识面板里的营业时间等商家信息和商家轮播（[本地商家](https://developers.google.com/search/docs/appearance/structured-data/local-business)）。旧版本文写的「无传统富结果、营业时间只限医疗类」没有出处，已删除。
- Google 没有 AI 专用 schema（[生成式 AI 优化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)）。
- 人工处置：结构化数据违规只让页面失去富结果资格，不影响网页排名（[通用指南](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)）。修复后在 Search Console 人工处置报告里申请复审。

## 常见误区

- 每个组件各输出一份 Organization，`@id` 不同或内容互相矛盾。
- `@id` 用了带参数的 URL，或随改版变化。
- 以为 `@id` 引用能跨页面解析，于是单页数据残缺。
- 为了让「图谱更完整」，加入页面上没有的实体或属性。

## 弃用类型替换决策与工具链时间线

与上文「富结果状态速查」互补，回答「被问到停用类型时给什么替代」（与 [deprecated-signals.md](deprecated-signals.md) 替换决策表互为镜像）：

| 用户要 | 替代方案 |
|---|---|
| `ClaimReview` | 搜索结果里没有替代；新闻场景用 `Article`/`NewsArticle`（可带 `dateline`）。Google 文档写明 Fact Check Explorer 仍支持该标记，事实核查出版商可保留 |
| `EstimatedSalary` | `JobPosting` + `baseSalary`（单个职位） |
| `LearningVideo` | `VideoObject` |
| Course info（单课详情） | Course list：Course + ItemList，至少 3 门课 |
| `SpecialAnnouncement` | 有时限且在实体场地举办的用 `Event`；否则 `Article`/`WebPage` |
| `VehicleListing` | `Product` + `Offer`（仅线上在售时） |
| `HowTo`（为搜索展示） | 无；正文用清晰的 `<h2>` 和有序列表写步骤 |
| `FAQPage`（为搜索展示） | 无；真实用户提交问答的页面用 `QAPage` |

- **工具链下线**：Google 2025-09-08 更新说明，Course info、Claim review、Estimated salary、Learning video、Special announcement、Vehicle listing 从 2025-09-09 起移出 Search Console 富结果报告、Rich Results Test 和搜索外观筛选；Search Console API 支持到 2025-12；批量导出里对应字段 2025-10-01 起报 `NULL`（[公告](https://developers.google.com/search/blog/2025/06/simplifying-search-results)）。Practice problem 2026-01 起移出这些工具。不要把用户送去已经不报告这些类型的验证器。
- **仍在用的类型**：Book actions 2025-11-05 撤回了停用横幅（还有功能在用该标记）；Dataset 未停，只给 Dataset Search 用；QAPage 2026-03-24 新增评论线程属性；教育问答（Quiz + `eduQuestionType: "Flashcard"`）仍支持。
- **JS 生成 Product 标记**：动态生成的 Product 标记会让购物抓取更少、更不可靠（价格、库存这类快变数据受影响）；Google 建议放进初始 HTML（2024-10-01 加入文档，[用 JS 生成结构化数据](https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript)）。
- **检测陷阱**（工程判断）：缺 `@context` 或 `@type` 的 JSON-LD 块挂不到实体；报错前先确认是不是合法的 `@graph` 包裹写法。
- **生成侧校验**（本套件口径）：占位文本、相对 URL、非 ISO 8601 日期一律按错误处理；有激励的评价必须在页面上醒目披露，否则不生成 Review 标记（依据：评价摘要 2026-07-24 准则）。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 引用能对上 | `python3 scripts/schema_lint.py URL`（查 @id 绝对性、引用悬空、同名实体分裂） | 退出码 0 → 通过；有 CRITICAL → 失败 |
| 实体只声明一次 | 浏览器 Console 运行 `[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>s.textContent)`，统计 Organization 出现次数和 @id | 同一实体只有一个完整节点 → 通过；多个 @id 或内容矛盾 → 失败 |
| 已停用类型 | 对照上文速查表 | 存量 FAQ/HowTo 等记 Info；不新增 |
| 面包屑 | Rich Results Test 看 BreadcrumbList；对照页面可见面包屑 | 至少 2 项、每项有 name 和 position，与可见面包屑一致 → 通过 |
| 组合主次 | 人工看 `@graph` 里谁是 `mainEntityOfPage` 指向本页的节点 | 只有一个主实体 → 通过 |

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。

- 思路参考：[coreyhaines31/marketingskills · skills/schema-markup/references/schema-examples.md](https://github.com/coreyhaines31/marketingskills/blob/v1.10.0/skills/schema-markup/references/schema-examples.md)（MIT）
- 一手资料（核对 2026-10-18）：[结构化数据简介](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)、[通用指南](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)、[类型库](https://developers.google.com/search/docs/appearance/structured-data/search-gallery)、[文档更新记录](https://developers.google.com/search/updates)、[2025-06 简化公告](https://developers.google.com/search/blog/2025/06/simplifying-search-results)、[2025-11 更新](https://developers.google.com/search/blog/2025/11/update-on-our-efforts)、[2023-08 HowTo/FAQ 变更](https://developers.google.com/search/blog/2023/08/howto-faq-changes)、[Article](https://developers.google.com/search/docs/appearance/structured-data/article)、[Breadcrumb](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)、[Organization](https://developers.google.com/search/docs/appearance/structured-data/organization)、[Q&A](https://developers.google.com/search/docs/appearance/structured-data/qapage)、[Fact check](https://developers.google.com/search/docs/appearance/structured-data/factcheck)、[JSON-LD 1.1（W3C）](https://www.w3.org/TR/json-ld11/)、[schema.org](https://schema.org/)
