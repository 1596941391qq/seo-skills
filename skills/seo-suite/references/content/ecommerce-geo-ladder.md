# 电商 GEO 阶梯(五级)与市场分叉

> 建立于 2026-10-09;2026-10-21 逐条重新核对:Google 商家与结构化数据文档、Merchant Center 帮助、blog.google、[ucp.dev](https://ucp.dev)(UCP 官方,Apache-2.0)、[agentic-commerce-protocol](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol)(ACP,OpenAI 与 Stripe 维护,Apache-2.0,仓库标注 beta)、[Shopify/ucp-cli](https://github.com/Shopify/ucp-cli)(MIT)。没有一手出处的市场份额和平台算法数字已删除。「本套件口径」是做法约定,不是 Google 规则。UCP 与 AI 面里的 free listings 仍在分阶段推出,不承诺排名与转化。2026-11-05 补微软 Copilot Checkout、Web IQ 和 Google AP2,复核于 2026-11-05。

## 一、五级阶梯(从基础到 agent 交互,逐级验收)

| 级 | 层 | 动作 | 验收 |
|---|---|---|---|
| **L1** | 产品数据 | 全 SKU 部署 Product + Offer(name、image、price、priceCurrency 必填;availability、gtin、sku、brand 推荐);接入 Merchant Center free listings;feed 与页面价格一致 | Rich Results Test 无 error;Search Console「商家信息」报告有效项;feed 与页面价差为 0(抽检) |
| **L2** | 评价信号 | `aggregateRating`、`review` 挂在 Product 上;官网评分数据与平台上的真实评价一致 | 星级富结果展示;`reviewCount` 与平台一致 |
| **L3** | 内容层 | 比较页、选购指南覆盖 best、vs、alternatives 类查询 | 目标查询手工月检,记录 AI 面引用的域名 |
| **L4** | marketplace 分工 | 交易型宽词让给 marketplace;官网争品牌词、长尾词、内容词、售后查询(本套件口径) | 品牌词官网排第一;交易词由 marketplace 承接 |
| **L5** | agent 交互 | 价格与库存对 AI 可读;UCP 接入(GMC UCP 集成中心或 `/.well-known/ucp`);Merchant Center conversational attributes | UCP profile 可解析;GMC 里能看到 AI performance insights |

### L1–L5 实操细节

**L1(产品数据)**

- 官方对 merchant listing 的要求(核对 2026-10-21,[merchant listing 文档](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing),2026-09-08 更新):必填 `name`、`image`、`offers`;`offers` 里必填 `price`(或 `priceSpecification.price`,且大于 0)和 `priceCurrency`(ISO 4217 三字母)。`availability` 是**推荐**属性,不是必填。merchant listing 要求 `Offer`;`AggregateOffer` 只适用于商品摘要(product snippet),且要符合「价格下降」增强必须用 `Offer`。
- `image`:官方建议提供多张高分辨率图(宽×高至少 5 万像素),比例 16:9、4:3、1:1;图片 URL 必须可抓取、可索引。本套件口径:主图 URL 与 Merchant Center feed 的 `image_link` 相同。
- 价格:页面可见价、结构化数据价、feed 价三处一致(本套件口径);促销价用 `priceSpecification` 并带有效期(官方文档有示例)。
- 停产商品页保留并标 `availability` 为 `OutOfStock` 或 `Discontinued`,避免整页删除丢失积累(本套件口径)。

**L2(评价信号)**

- 评价属于 Product。官方的 review snippet 文档对 Organization、LocalBusiness 上的「自我评价」有单独限制([review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet),2026-09-08 更新)。
- Product snippet 要求 `review`、`aggregateRating`、`offers` 三者至少有一个;只有 `offers` 时 Rich Results Test 可能给 warning([product snippet](https://developers.google.com/search/docs/appearance/structured-data/product-snippet))。
- 不要为了消 warning 编造评分(本套件口径)。

**L3(内容层)**:页型 best、vs、alternatives、how-to-choose;每页有可抽取的参数表或评分维度(本套件口径)。

**L4(marketplace 分工)**:验证方法:搜核心交易词,看前 10 名里 marketplace 占几个;占多数就把预算转向内容层和品牌词(本套件口径,阈值自定)。

**L5(agent 交互)**:见下节。

### L5:Google agentic commerce 与 UCP(核对 2026-10-21)

- **UCP 结账功能的范围**:Merchant Center 帮助页写明,该结账功能只适用于在美国、加拿大、澳大利亚有资格的商品,面向选定商家的早期访问,商家仍是 seller of record,买家用 Google Pay 在 AI Mode 和 Gemini 里结账([Merchant Center 帮助](https://support.google.com/merchants/answer/16837055))。
- **UCP 集成中心(Merchant Center)**:2026-09-16 的官方博客说,用集成中心做 UCP 结账的商家可以开启「购物车回传商家网站」和增强的结账流测试;新能力在美国逐步推出,澳大利亚和加拿大「early next year」;博客称 UCP 已支撑数十万品牌和零售商的直接结账;Tapestry(Coach、Kate Spade)是案例([blog.google 2026-09-16](https://blog.google/products-and-platforms/products/shopping/google-shopping-updates-holiday-shopping/))。
- **Universal Cart**:2026-10-15 在美国上线(此前已预告)。跨零售商存入同一购物车,提示降价和补货,识别相关优惠码并显示,用 Google Pay 结账或转到商家购物车完成;建立在 Shopping Graph 的 600 亿以上持续刷新的商品条目上;列出的商家含 Nike、Sephora、Target、Ulta Beauty、Walmart、Wayfair 和许多 Shopify 商家([blog.google 2026-10-15](https://blog.google/products-and-platforms/products/shopping/universal-cart-launch/))。含义:购物车会追踪降价,所以页面价、结构化数据价、feed 价必须一致。
- **conversational attributes(2026-09-16 起列入产品数据规范)**:6 个可选字段:`question_and_answer`、`document_link`、`related_product`、`item_group_title`、`variant_option`、`popularity_rank`。建议用补充数据源(supplemental data source)提交,也可用 Merchant API;不影响商品审批状态([Merchant Center 帮助](https://support.google.com/merchants/answer/17085370))。Google 在 2026-01-11 预告将有「dozens」的新属性([blog.google](https://blog.google/products/ads-commerce/agentic-commerce-ai-tools-protocol-retailers-platforms/))。官方称与 lululemon 的测试中,品牌提交的 conversational attributes 在相关 AI Mode 商品推荐里被采用 50%;采用核心 feed 最佳实践的商家,次月转化平均增加 5%(均为 Google 自述,见 2026-09-16 博客)。
- **Business Agent**:2026-01 起在美国 Search 上线;2026-09-16 开放 YouTube 广告内嵌 Business Agent 的 beta,仅美国([blog.google](https://blog.google/products-and-platforms/products/shopping/google-shopping-updates-holiday-shopping/))。
- **AI performance insights**:2026-09-16 起对澳大利亚、加拿大、印度、新西兰、美国的 Merchant Center 账户正式可用,仅限英语查询。指标是 share of voice(你的 AI 展示 ÷ 你与你自定竞品集的 AI 展示之和)、竞品平均份额、热门搜索词和属性的频率、你有多少商品在这些词下出现;按购物阶段(discovery、evaluation 等)筛选([帮助页](https://support.google.com/merchants/answer/17200695))。报告页没有点击、转化指标,基准取决于你自配的竞品集,只覆盖 Google 的 AI 面,不覆盖 ChatGPT、Perplexity。品牌主要经零售商销售时,商品数据多由零售商 feed 持有,逐账号确认覆盖范围。
- **双轨 SoV**:电商客户的 AI 面可见度报告并列两轨:自采探针(跨引擎,按 [kpi-definitions.md](../monitoring/kpi-definitions.md) 的分级标注)和 AI performance insights(官方、仅 Google 面);两轨数字不互相对账,各带口径说明(本套件口径)。
- UCP 不影响 Google 排名;Google 没有这样表述,不要写进客户材料。

**L5 验收命令**

```bash
# UCP profile 可解析(已接入 UCP 的站点)
curl -s https://shop.example.com/.well-known/ucp | python3 -m json.tool
# 价格页对 AI 爬虫可达(应返回 200)
curl -s -A "GPTBot" -o /dev/null -w "%{http_code}\n" https://shop.example.com/p/123
# robots 对各 AI 爬虫的放行情况
python3 scripts/robots_posture.py https://shop.example.com/robots.txt --json
```

## 二、Product schema 实操清单

出处:[merchant listing](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing)、[product snippet](https://developers.google.com/search/docs/appearance/structured-data/product-snippet)(均 2026-09-08 更新)。

**高频错误**(前三项来自官方必填要求;其余为本套件口径的失败模式):

1. `price` 不是纯数字(例:`$1,299.99` 应写 `1299.99`)——官方示例用数字,并要求遵循 schema.org 的用法。
2. 缺 `priceCurrency`——必填。
3. 价格为 0 或缺 `offers`——merchant listing 要求价格大于 0。
4. 页面可见价、结构化数据价、feed 价不一致(含舍入差)。
5. 单品页使用 `AggregateOffer`——merchant listing 要求 `Offer`。
6. 缺 `availability`、`gtin`、`sku`、`brand`——推荐属性,缺了不一定失去资格,但商品匹配和展示信息变少。
7. 缺 `aggregateRating`/`review`——没有星级富结果;不要为此造假评分。
8. `image` 指向被 robots 屏蔽的 CDN,或带会过期签名的 URL——官方要求图片 URL 可抓取、可索引。
9. 主题或插件更新后 schema 失效——用下面的检查清单定期抽查。

**排查入口**:Search Console「商家信息」报告(按 SKU 列错误)、Rich Results Test(单 URL)、Merchant Center Diagnostics(feed 侧)。三者交叉:Search Console 报页面侧,Merchant Center 报 feed 侧,只看一边会漏。

**最小可用 Product JSON-LD**

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Example 3-Seat Sofa (Red Leather)",
  "image": ["https://cdn.example.com/img/sofa-red-main.webp",
            "https://cdn.example.com/img/sofa-red-side.webp"],
  "sku": "SOFA-RED-3S",
  "gtin13": "0123456789012",
  "brand": { "@type": "Brand", "name": "ExampleHome" },
  "aggregateRating": { "@type": "AggregateRating", "ratingValue": "4.6", "reviewCount": "812" },
  "offers": {
    "@type": "Offer",
    "url": "https://shop.example.com/p/sofa-red-3s",
    "priceCurrency": "USD",
    "price": "1299.99",
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2026-12-31"
  }
}
```

(示例数据为虚构。price 用纯数字、priceCurrency 用 ISO 4217、availability 用完整 URL。)

Merchant Center 帮助页写明 free listings 可以出现在 Google 搜索、地图、Gemini、YouTube、购物标签、Google 图片和 Google Lens([Free listings 帮助](https://support.google.com/merchants/answer/9826670));需要 feed 与页面中的商品信息都准确(帮助页要求提供高质量商品数据)。

## 三、市场分叉(定性;份额数字未核,已删)

旧版的各市场份额、平台算法清单和增长数字没有找到可核对的一手来源,已删除。做某个市场的客户方案前,先查该市场最新的一手数据(平台官方卖家中心、统计机构),再写入方案。

| 市场 | marketplace 主导方(定性) | 官网策略(本套件口径) |
|---|---|---|
| 美/英 | Amazon | DTC 争品牌词、对比词;交易词让 marketplace |
| 印度 | Flipkart、Amazon | 官网做品牌词和内容层 |
| 东南亚 | Shopee、Lazada、Tokopedia | 官网做内容层和 schema |
| 日本 | Amazon JP、楽天 | 楽天店内搜索与 Google 搜索是两套规则 |
| 韩国 | Coupang、Naver Shopping | 重点在 Naver 生态 |
| 土耳其 | Trendyol | 官网争品牌词和内容层 |
| 拉美 | Mercado Libre | 标题、属性、问答在平台内优化 |
| 中东 | Noon、Amazon | 阿拉伯语 RTL 站点,本地支付方式 |
| 俄罗斯 | Ozon、Wildberries | 低优先级,先评估合规与履约风险 |

## 四、AI 购物现状(核对 2026-10-21)

- **Google**:AI Mode、Gemini、Search 里的购物功能依赖 Merchant Center 与 Shopping Graph;UCP 结账见上节。
- **OpenAI**:ChatGPT Instant Checkout 于 2025-09-29 推出(Forbes 2026-03-10)。OpenAI 在 2026-03-24 的官方文章里说,初版 Instant Checkout 灵活性不够,改为允许商家使用自己的结账流程,自己专注产品发现;商家通过 ACP 共享商品 feed 和促销信息;想要更深整合的商家可以开发 ChatGPT apps(Walmart 是首个例子)([OpenAI](https://openai.com/index/powering-product-discovery-in-chatgpt/))。CNBC 2026-03-20 报道 OpenAI 确认结束 Instant Checkout([CNBC](https://www.cnbc.com/2026/03/20/open-ai-agentic-shopping-etsy-shopify-walmart-amazon.html),第三方)。
- **微软 Copilot**(核对 2026-11-05):
  - **Copilot Checkout**:2026-01-08 公布,先在美国 Copilot.com 推出,商家仍是记录商户(merchant of record),交易、客户数据和关系归商家;接入走 PayPal、Shopify、Stripe:PayPal 和 Stripe 商家申请,Shopify 商家在退出窗口期后自动加入;首批有 Urban Outfitters、Anthropologie、Ashley Furniture 和 Etsy 卖家;微软称会随 Copilot 扩到 Bing、MSN、Edge 等入口。同时发布 Brand Agents(装在商家自己站上的购物助手)([Microsoft Advertising 2026-01-08](https://about.ads.microsoft.com/en/blog/post/january-2026/conversations-that-convert-copilot-checkout-and-brand-agents))。2026-04-21 起 Microsoft Merchant Center 在美国对所有人支持「UCP-ready feeds」,Copilot Checkout 设置只给 beta 参与者;Shopify Catalog 经微软 commerce API 接入 Copilot,商家不必单独建 feed([2026-04-21 博客](https://about.ads.microsoft.com/en/blog/post/april-2026/win-across-all-three-eras-of-the-web))。博客里的转化提升数字(53%、194%、2 倍)是微软自述,不入证据库。
  - **Web IQ**:2026-06-02 发布,一组给 AI 系统和 agent 用的 grounding API,建在 Bing 全球索引上,返回段落和结构化证据而不是整页;微软称它遵守 robots 排除协议和出版方的访问偏好([Bing 博客 2026-06-02](https://blogs.bing.com/search/2026/6/Announcing-Microsoft-Web-IQ/))。对电商的含义(本套件口径):用 Web IQ 的第三方 agent 看到的商品信息来自 Bing 索引,所以商品页要能被 Bing 抓取和索引,`NOARCHIVE`/`NOCACHE` 会限制 Copilot 对内容的使用(见 [geo-evidence.md](geo-evidence.md) 官方事实)。
- **Google AP2(Agent Payments Protocol)**:agent 支付协议,2025-09-16 由 Google Cloud 公布([公告](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol));2026-04-28 捐给 FIDO Alliance,同日发布 v0.2,加入「Human Not Present」支付(按用户事先授权,agent 自主下单,例如开售瞬间抢票),并配合与 Mastercard 共同开发、也捐给 FIDO 的 Verifiable Intent(用户授权 agent 动作的防篡改记录)([blog.google 2026-04-28](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/)、[GitHub](https://github.com/google-agentic-commerce/AP2))。它管「agent 怎么安全付款」,和 UCP(商品、购物车、结账接口)、ACP 不是一层;对 SEO 没有直接作用,商家只在接 agent 结账时碰到。
- 本套件口径的判断:AI 管发现,结算多回到商家网站。把 L5 当期货,把 L1–L4 当现货。公开的商家采用率和转化数据仍然缺失,对客户写「基建预备」,不写「流量渠道」。

## 五、UCP 与 ACP

| | UCP | ACP |
|---|---|---|
| 发起 | Google 主导;ucp.dev 的「Co-developed」列表含 Shopify、Etsy、Wayfair、Target、Walmart 等;「Endorsed across the ecosystem」列表含 Adyen、Best Buy、Flipkart、Klarna、Mastercard、PayPal、Shopee、Stripe、Visa、Zalando 等 | OpenAI 与 Stripe 维护(仓库称 beta) |
| 机制 | 商家在 `/.well-known/ucp` 发布 profile;传输层 REST、MCP、A2A、Embedded;商家保持 Merchant of Record | 连接买家、AI agent 与商家;2026-03 扩展到产品发现(商家共享 feed 和促销) |
| 状态 | 规格按日期版本,当前最新 2026-08-25;垂直扩展:Lodging 草案、Food 即将推出;Google 侧结账见上节 | Instant Checkout 已改为允许商家自有结账 |
| 实操入口 | [ucp.dev](https://ucp.dev)、[Shopify/ucp-cli](https://github.com/Shopify/ucp-cli) | [ACP 规范仓库](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol) |
| 微软侧 | Microsoft Merchant Center 2026-04-21 起在美国支持 UCP-ready feeds,供 Copilot 购物使用 | — |

支付层另有 Google 发起、现归 FIDO Alliance 的 AP2(见第四节),它不替代 UCP 或 ACP。

## 六、检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| Product 必填项 | `curl -s URL \| grep -o '"price":[^,}]*'`;`python3 scripts/schema_lint.py URL` 检查 JSON-LD 的 `@id`、悬空引用、aggregateRating 范围 | `price` 是纯数字且大于 0,`priceCurrency` 存在,为通过 |
| 价格三处一致 | 抽 20 个 SKU:页面可见价、JSON-LD 价、feed 价逐个对 | 价差为 0 为通过;任一不一致为失败 |
| 富结果资格 | Rich Results Test(单页);Search Console「商家信息」报告 | 无 error 为通过 |
| feed 侧问题 | Merchant Center Diagnostics | 无 critical 问题为通过 |
| 单品页没有 AggregateOffer | `curl -s URL \| grep -c AggregateOffer` | 输出 0 为通过 |
| 评价与平台一致 | 官网 `reviewCount` 对照平台店铺页 | 一致为通过;官网数大于平台实有评价数为失败 |
| AI 爬虫可达价格页 | `curl -s -A "GPTBot" -o /dev/null -w "%{http_code}\n" URL`;`python3 scripts/robots_posture.py URL/robots.txt --json` | 返回 200,且 robots 立场与客户的决策一致为通过 |
| UCP profile(已接入时) | `curl -s https://shop.example.com/.well-known/ucp \| python3 -m json.tool` | 能解析为 JSON 为通过 |
| Bing 侧可索引(Copilot、Web IQ) | Bing Webmaster Tools 网址检查抽 10 个商品页;`curl -s URL \| grep -ioE '<meta[^>]*(noarchive\|nocache)[^>]*>'` | 已索引且无 `noarchive`/`nocache` 为通过(除非客户决定退出 Copilot) |
| 官方 AI 面份额 | Merchant Center → Analytics → AI performance(仅在可用国家,英语查询) | 能看到 share of voice 并记录口径为通过 |
| 内容层引用 | 20 个 best、vs 查询,手工在目标 AI 面检查,记录引用的域名 | 有记录为通过(采样纪律见 [ai-citation-patterns.md](ai-citation-patterns.md)) |

## 七、未证实项

- AI 面里 free listings 的触发条件与覆盖面。
- UCP 到转化的案例数据;商家采用率。
- Merchant Center UCP 功能在澳大利亚、加拿大的上线时间:官方只说「early next year」。
- 各市场 marketplace 的份额与站内排名因素(旧版数字已删)。

## 来源

- 官方(2026-11-05 补):Microsoft Advertising 博客 2026-01-08、2026-04-21;Bing 博客 2026-06-02(Web IQ);Google Cloud AP2 公告、blog.google 2026-04-28(AP2 捐给 FIDO)。
- 官方:[merchant listing 结构化数据](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing)、[product snippet](https://developers.google.com/search/docs/appearance/structured-data/product-snippet)、[review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)、Merchant Center 帮助([free listings](https://support.google.com/merchants/answer/9826670)、[UCP 结账](https://support.google.com/merchants/answer/16837055)、[conversational attributes](https://support.google.com/merchants/answer/17085370)、[AI performance insights](https://support.google.com/merchants/answer/17200695))、blog.google(2026-01-11、2026-09-16、2026-10-15 三篇)、[ucp.dev](https://ucp.dev)、[OpenAI 2026-03-24](https://openai.com/index/powering-product-discovery-in-chatgpt/)。
- 第三方:CNBC、Forbes(Instant Checkout 时间线)。
