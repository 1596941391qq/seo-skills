# 审计规则目录 · Social

> 从 [audit-rule-catalog.md](../audit-rule-catalog.md) 拆出(2026-10-21),正文原样搬运,只改了相对链接路径。来源、计分口径、ID 纪律、执行速查(`AUDIT`/`CRAWL` 等简写与 J1–J8、G1–G7 片段)和扩写进度见索引页。

### Social(9 条,权重 3%)

og:title/description/image 缺失或为空=**fail**(用 `name=` 代替 `property=` 或 og:image 非绝对 URL=warn);**og:image 推荐 1200×630**,`og:image:width/height` 缺失或小于 1200×630=warn、小于 200×200 或无 og:image=fail;og:url 缺失=fail;**og:url 与 canonical 不一致=fail**(只有 og:url 或两者都无=warn);twitter:card 缺失=fail、未知类型=warn(已知类型 summary、summary_large_image、app、player);分享按钮(**≥2 平台**)=warn;社交资料链接(**≥3 个**,入 Organization sameAs)=warn。

**解释层(4 条;ID 未公布原文,标 [待核])**

#### social-og-url-canonical
- 源表:warn/fail · 权重 1。比较 og:url 与 canonical(host 小写、去尾斜杠):不一致或有 canonical 无 og:url=fail;只有 og:url 或两者都无=warn。工具约定。建议优先级 medium。
**依据**: Open Graph 协议把 og:url 定义为"The canonical URL of your object that will be used as its permanent ID in the graph"([ogp.me](https://ogp.me/))。og:url 与 canonical 不同,社交平台归并分享计数的 URL 与搜索引擎的规范 URL 就分裂。核对 2026-10-18。
**判据**: 通过=og:url 与 canonical 同值。失败=不同(常见是 og:url 带 utm 参数)。
**执行**: `curl -s URL | grep -oiE '<meta[^>]+property=.?og:url[^>]*>'` 与 G1 比对;site_audit 与 head_check 查 og:url 是否为 http(s):// 绝对 URL(`[WARN] og: og:url 非绝对 URL`,ogp.me URL 类型口径);og:url 与 canonical 是否同一 URL 仍要上面的命令人工比对(只在文档)。
**修复**: og:url 复用 canonical 的同一模板变量。
**关联**: core-canonical-conflicting;[head-elements.md](../head-elements.md) OG 消费矩阵

#### social-og-basic [待核 ID]
- 名称/类型: og 标签家族缺失(源表 ID `social-og-title`、`social-og-description`、`social-og-image`、`social-og-url`、`social-twitter-card`) —— warning · 优先级 low · 输出 CRITICAL/WARN(源表现行:缺失或为空=fail;`name=` 代替 `property=` 或 URL 非绝对=warn;本套件把建议优先级压到 low,因为只影响分享卡片)
**这意味(what)**: 页面缺 og:title/og:description/og:image(og:url 缺失另计 warn,与 canonical 的冲突见 social-og-url-canonical);twitter:card 同构——缺=warn,推荐值 summary_large_image。
**为什么(why)**: Open Graph 协议定义了这些标签,分享平台据此生成卡片([ogp.me](https://ogp.me/));缺了平台自行抓取页面,卡片图文不可控。各平台具体怎么用本次未逐个核对。对搜索排名没有已知影响,纯分享层缺信号,故 low。
**触发(trigger)**: 逐一断言 og:title/og:description/og:image/og:url 存在且非空;twitter:card 为已知类型;任一缺失即原版 fail。site_audit 对缺 og:title/og:description/og:image 记 `[WARN] og`,不查 og:url 与 twitter:card。
**不修的条件(caveat)**: og 标签不影响搜索排名,然而决定分享卡片完整度,所以一般建议核心模板页全配。但法律/结账流等不需要被分享的页面可豁免。
**修复(fix)**: 模板用与 title/description 同源变量输出 og:title/og:description;og:image 用固定比例专图(见 social-og-image-dimensions);twitter:card 配 summary_large_image。
**关联(seealso)**: social-og-url-canonical、social-og-image-dimensions;[head-elements.md](../head-elements.md) OG 消费矩阵

#### social-og-image-dimensions
- 名称/类型: og:image 尺寸(源表 ID `social-og-image-size`) —— warning · 优先级 low · 输出 WARN/CRITICAL(源表现行:缺 width/height 或小于 1200×630=warn;小于 200×200 或无 og:image=fail;推荐 1200×630)
**这意味(what)**: og:image 分辨率明显偏离 1200×630(1.91:1),或未配 og:image:width/og:image:height meta。
**为什么(why)**: 各平台分享卡裁切比例不一,1.91:1 是最大公约数;尺寸离谱时平台裁掉关键内容或弃图。配 width/height meta 让平台免下整图即可算占位,加快卡片渲染。
**触发(trigger)**: 读声明的 og:image:width/height(不下载图片):缺失或小于 1200×630 warn,小于 200×200 fail。宽高比 1.91:1 只作建议。
**不修的条件(caveat)**: 尺寸不影响 SEO,然而影响分享卡展示完整度,所以一般建议 1200×630 专图。但主投放平台明确(如以 X 的 1:1 为主)时可按主平台调优。
**修复(fix)**: 出 1200×630 专图;head 补 og:image:width/og:image:height;每页独立图,别全站一张。
**关联(seealso)**: social-og-basic;[head-elements.md](../head-elements.md)

#### social-engagement [待核 ID]
- 名称/类型: 分享按钮与社交资料链接 —— opportunity · 优先级 insight · 输出 WARN(源表 warn;分享按钮 ≥2 平台、社交资料链接 ≥3 个)
**这意味(what)**: 站点缺社交基建:分享按钮覆盖 <2 平台,或站内社交资料链接 <3 个。
**为什么(why)**: 分享按钮降低分发摩擦;资料链接的作用更大——它们是 Organization schema sameAs 的候补实体证据,帮引擎把站点与官方社交账号绑定为同一实体(见 [entity-signal-checklist.md](../entity-signal-checklist.md))。典型缺信号/机会项,不构成错误。
**触发(trigger)**: 1) 分享按钮平台数 <2 即 warn;2) 页脚/联系页社交资料外链 <3 个即 warn(已入 sameAs 的链接计入)。
**不修的条件(caveat)**: 社交基建不影响排名,然而影响分发与实体确认,所以一般建议按受众补齐。但 B2B 内部系统/无社交属性的站点两项都可合理不修。
**修复(fix)**: 分享按钮接 2+ 主平台;页脚列官方资料并同步写入 Organization sameAs。
**关联(seealso)**: sd-required-fields(Organization sameAs);[entity-signal-checklist.md](../entity-signal-checklist.md)
