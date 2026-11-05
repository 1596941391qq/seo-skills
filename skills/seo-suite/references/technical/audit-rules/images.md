# 审计规则目录 · Images

> 从 [audit-rule-catalog.md](../audit-rule-catalog.md) 拆出(2026-10-21),正文原样搬运,只改了相对链接路径。来源、计分口径、ID 纪律、执行速查(`AUDIT`/`CRAWL` 等简写与 J1–J8、G1–G7 片段)和扩写进度见索引页。

### Images(14 条,权重 8%)

alt 缺失=fail;alt 泛化("image"/文件名)=warn;alt 长度 **>125 字符 warn、>250 fail,无下限**;宽高属性缺失=warn(防 CLS);below-fold 须 `loading="lazy"`=warn;现代格式(建议 WebP/AVIF)=warn;体积(`images-size`,只按文件名线索或声明的宽高推断「像是过大」,不取文件)=warn;srcset 响应式=warn;图片 404=fail;figure 缺 figcaption=warn;文件名(IMG_001.jpg 坏/red-running-shoes.jpg 好)=warn;**内联 SVG >5KB 应外链**=warn;picture 缺 img 回退=fail;内联 style 的 background-image(`images-background-seo`):**2-5 个 warn、>5 个 fail**,样式表里的背景图看不到。

**解释层(6 条;ID 未公布原文,标 [待核])**

#### images-alt-present
- 源表:`images-alt-present` fail · 权重 20(img 无 alt 属性);`images-alt-length` warn/fail · 权重 6(>125 字符 warn,>250 fail,无下限);泛化 alt 归 `images-alt-quality`。长度是工具约定。建议优先级 high(缺失)/low(长度)。
**依据**: Google 结合 alt、计算机视觉和页面内容理解图片,alt 是最重要的图片元数据,也服务屏幕阅读器;不要往 alt 堆关键词([图片 SEO 文档](https://developers.google.com/search/docs/appearance/google-images))。Google 没有 alt 长度规则。装饰图用空 alt 是 W3C 推荐做法,不是缺失。核对 2026-10-18。
**判据**: 通过=内容图有描述性 alt,装饰图 alt=""。失败=内容图无 alt 属性。长度超 125 只算提示。
**执行**: `AUDIT URL` 出现 `[WARN] images: alt 缺失 N/M`(超过 20% 才报;只算没有 alt 属性的图,`alt=""` 是装饰图的正确写法,不算缺失——2026-11-05 对齐脚本实际行为,旧文写反了);精确查无 alt 属性的图:`curl -s URL | grep -oiE '<img[^>]*>' | grep -viE ' alt='`。
**修复**: 内容图写"图里有什么";装饰图用空 alt;复杂图表用 figcaption 写长描述。
**关联**: images-alt-generic;[semantic-html.md](../semantic-html.md)

#### images-alt-generic
- 名称/类型: 泛化/文件名式 alt —— warning · 优先级 low · 输出 WARN(源表 ID `images-alt-quality`,warn;"image"/文件名)
**这意味(what)**: 内容图的 alt 是泛化词("image"/"photo"/"图片")或直接复述文件名(img001),没有描述图内内容。
**为什么(why)**: Google 把 alt 当作图片最重要的元数据,结合计算机视觉和页面内容理解图意([图片 SEO 文档](https://developers.google.com/search/docs/appearance/google-images),核对 2026-10-21);SR 用户听到 "image" 毫无信息。与 images-alt-present(缺失/长度)同族互补:那条管"没写/写多长",本条管"写了但零信息量"。
**触发(trigger)**: 1) alt 值命中泛化词表(image/photo/picture 等[词表源表未公布,待核])即 warn;2) alt 与 src 文件名(去扩展名)相同即 warn;3) 装饰图空 alt 不判(正确做法)。
**不修的条件(caveat)**: alt 文案质量不(直接)影响网页排名,然而决定图片搜索的匹配面与无障碍信息量,所以一般建议写"图里有什么"。但 logo 类小图的短描述(alt="ExampleCorp 商标")属可接受形态。
**修复(fix)**: 按图内容写名词性描述(对象+动作+语境);别把关键词堆进 alt(那归 content-keyword-stuffing);模板无法自动生成时留空待人工补,也别输出文件名。
**关联(seealso)**: images-alt-present;[semantic-html.md](../semantic-html.md)、[image-search-seo.md](../../content/image-search-seo.md)

#### images-dimensions
- 名称/类型: 宽高属性缺失(尺寸家族) —— warning · 优先级 medium · 输出 WARN(源表 warn;防 CLS)
**这意味(what)**: `<img>` 缺 width/height 属性(也无 aspect-ratio 兜底),浏览器无法预留占位。
**为什么(why)**: 缺宽高时图片到位后布局重排,直接推高 CLS(阈值见 [cwv-playbook.md](../cwv-playbook.md));现代浏览器按属性计算宽高比,加载前就留好空间。本家族其余规则同构(缺信号 warn 档):srcset 响应式缺失=warn、figure 缺 figcaption=warn、文件名无描述性(IMG_001.jpg 坏/red-running-shoes.jpg 好)=warn、内联 SVG >5KB 应外链=warn;picture 缺 img 回退=**fail** 档(不支持环境整图消失);图片 404=**fail** 档(与 links-broken-internal 同构的断链家族)。
**触发(trigger)**: 1) `<img>` 无 width/height 且无 CSS aspect-ratio 即 warn;2) 家族各小条按上列阈值判。
**不修的条件(caveat)**: 宽高不(直接)影响 SEO,然而它是 CLS 的最大可控因子之一,所以一般建议模板全配。但已用 CSS aspect-ratio 或 srcset+sizes 覆盖同需求的场景,属性缺失可视为等价实现。
**修复(fix)**: CMS/构建管道存原始尺寸并输出 width/height;动态尺寸图用 aspect-ratio;响应式配 srcset+sizes;figure 配 figcaption。
**关联(seealso)**: images-modern-formats、perf-dom-size;[cwv-playbook.md](../cwv-playbook.md)

#### images-modern-formats
- 名称/类型: 老旧图片格式/传输体积 —— warning · 优先级 low · 输出 WARN(源表 ID `images-modern-format`,warn:建议 WebP/AVIF,原版未给节省比例;与 Performance 节 perf-image-encoding 同一事实的两面)
**这意味(what)**: 页面图片仍是 JPEG/PNG 老格式且未提供 WebP/AVIF(协商或 picture 回退),或单图传输体积过大。
**为什么(why)**: Google 的对比研究:同等 SSIM 下 WebP 比 JPEG 小 25%-34%([WebP 研究](https://developers.google.com/speed/webp/docs/webp_study),核对 2026-10-21;AVIF 无本次回读的一手数字)。省下的字节改善 LCP 与传输量。perf 侧同源规则 perf-image-encoding(渲染专属)判**传输 >100KB=warn、BMP/TIFF=fail**——本条看"格式供给",那条看"实际传输",命中其一就该动手。
**触发(trigger)**: 1) img src 无 .webp/.avif 且响应无格式协商(Accept/Vary)即 warn;2) 渲染口径:单图传输 >100KB=warn、BMP/TIFF=fail。
**不修的条件(caveat)**: 格式不影响图片相关性判定,然而传输体积是 LCP 的一半战场,所以一般建议全站切现代格式。但图片本就 <30KB 且 CMS 无转换能力的场景,收益排序靠后。
**修复(fix)**: 构建/CDN 层自动转 WebP/AVIF+picture 回退;大图压到展示分辨率;截图类 PNG 走有损压缩;验收看单图传输量。
**关联(seealso)**: perf-page-weight、images-lazy;[cwv-playbook.md](../cwv-playbook.md)、[image-search-seo.md](../../content/image-search-seo.md)

#### images-lazy
- 名称/类型: loading="lazy" 家族 —— warning · 优先级 medium · 输出 WARN(源表 ID `images-lazy-loading`,warn;below-fold 须 lazy;首屏图禁 lazy=perf-lazy-above-fold)
**这意味(what)**: 折叠线以下的图没加 loading="lazy",或首屏图(尤其 LCP 图)反而加了 lazy。
**为什么(why)**: 两个方向伤同一指标:下页图不 lazy=全部抢首屏带宽,LCP 被非关键图拖慢;首屏图 lazy=LCP 资源被延迟加载。原生 loading="lazy" 由浏览器实现,不需要脚本库;web.dev 建议 LCP 图用默认的 eager 加载([web.dev](https://web.dev/articles/browser-level-image-lazy-loading),核对 2026-10-21)。
**触发(trigger)**: 1) below-fold 图无 loading="lazy" 即 warn;2) 首屏/LCP 图带 loading="lazy" 即 warn(Performance 侧 perf-lazy-above-fold)。
**不修的条件(caveat)**: lazy 属性不影响图片索引(仍会被抓取),然而它调度首屏带宽,所以一般建议 below-fold 全配。但首屏边缘图(是否在视口随设备变化)宁可不 lazy——误 lazy 的白屏代价大于误加载的带宽代价。
**修复(fix)**: 模板按位置分流:首屏/LCP 图 eager+fetchpriority=high(见 perf-lcp-hints),其余 lazy;首屏判定以常见移动视口为准。
**关联(seealso)**: perf-lcp-hints、perf-page-weight;[cwv-playbook.md](../cwv-playbook.md)

#### images-css-background
- 名称/类型: 内容图用 CSS background —— warning · 优先级 medium · 输出 WARN/CRITICAL(源表 ID `images-background-seo`:数内联 style 里的 background-image(不含 data URL 与渐变),1 个过、2-5 个 warn、>5 个 fail;样式表里的背景图看不到)
**这意味(what)**: 承载内容信息的图(产品图/文章配图/图表)用 CSS background-image 呈现,而非 `<img>`。
**为什么(why)**: Google 说它不索引 CSS 图片("Google doesn't index CSS images"),要被图片搜索收录需用 `<img>` 或 `<picture>`([图片 SEO 文档](https://developers.google.com/search/docs/appearance/google-images),核对 2026-10-21);alt/宽高/srcset/lazy 这套图片优化也都用不上。背景图的合理域是装饰;内容图的合理域是 img(或 picture/svg)。
**触发(trigger)**: 源表:内联 style 的 background-image 数量 2-5 warn、>5 fail。本套件另要求人工判断该图是否承载内容。
**不修的条件(caveat)**: 纯装饰背景(渐变/纹理/氛围图)用 background 是正确做法,不判;只有当图承载内容语义(用户需要"看懂"它)时才构成问题——判定依赖"信息图"识别,命中后建议人工复核再改。
**修复(fix)**: 内容图改 `<img>` 带 alt/宽高/现代格式;装饰保留 background;图表类用 svg+figcaption 或 img+长描述。
**关联(seealso)**: images-alt-generic;[semantic-html.md](../semantic-html.md)
