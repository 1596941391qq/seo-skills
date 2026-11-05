# Core Web Vitals 优化手册（2026-10 口径）

> 建立于 2026-10-09，2026-10-18 与 2026-10-21 两次逐条核对（2026-11-05 补第九节 SPA 软导航，复核于 2026-11-05） web.dev、Chrome 文档、CrUX 发布说明和 Google Search Central。本手册是 CWV 总纲：四指标全景、INP/CLS/TTFB 深度、第三方脚本治理、优化优先级。LCP 的四段拆解与诊断顺序见 [LCP.md](LCP.md)；JS 渲染策略见 [rendering-seo.md](rendering-seo.md)；审计扣分规则见 [audit-rule-catalog.md](audit-rule-catalog.md)。

> **CrUX 软导航（实验性）**：2026-10-13 发布的 CrUX 2026-09 数据集新增 LCP/INP/CLS 的软导航实验变体（SPA 路由切换），BigQuery 和 CrUX API 都可查；API 指标名为 `experimental_largest_contentful_paint_with_softnavs` 等（[CrUX 发布说明](https://developer.chrome.com/docs/crux/release-notes)、[CrUX API](https://developer.chrome.com/docs/crux/api)，核对 2026-10-21）。同期全量统计：18,376,044 个 origin；LCP 良好 68.3%、CLS 81.7%、INP 85.4%、三项全过 55.9%；计入软导航后分别为 72.1%、85.1%、87.4%、59.5%。做竞品基准时注明「含/不含软导航」，两种口径不混用。2026-09-08 的发布说明提到 INP 持续回退，官方没有给出原因。引用软导航指标时标 [experimental]。发布日期、指标名和转正时间只写在[事实表](../overview/facts.md#crux-softnav)；SPA 怎么用见第九节。

## 一、四指标全景

| 指标 | 衡量对象 | 良好 | 需改进 | 差 |
|---|---|---|---|---|
| LCP | 最大内容元素完成渲染（加载） | 见[阈值表](../overview/facts.md#cwv) | 同左 | 同左 |
| INP | 交互到下一帧绘制（响应性） | 见[阈值表](../overview/facts.md#cwv) | 同左 | 同左 |
| CLS | 最大一次布局偏移突发（视觉稳定性） | 见[阈值表](../overview/facts.md#cwv) | 同左 | 同左 |
| TTFB | 首字节（诊断指标，不是 Core Web Vital） | ≤0.8s | 0.8–1.8s | >1.8s |

阈值依据：三项 Core Web Vitals 的数值和来源只写在[事实表](../overview/facts.md#cwv)；TTFB 见 [web.dev TTFB](https://web.dev/articles/ttfb)（核对 2026-10-21）。INP 于 2024-03-12 取代 FID 成为 Core Web Vital（[web.dev 公告](https://web.dev/blog/inp-cwv-march-12)）；FID 从 CrUX API 移除、BigQuery 的 2024-08 数据集是最后一份含 FID 的数据（[CrUX 发布说明](https://developer.chrome.com/docs/crux/release-notes)，2024-09-10 公告）。

- **评估口径**：真实用户第 75 百分位，移动端和桌面端分开（[web.dev Web Vitals](https://web.dev/articles/vitals)）。web.dev：三项都达到良好才算页面通过。
- **Search Console 分组规则**：一个 URL 组的状态取三项里最差的那一项（例如 CLS 差、INP 良好 → 整组为「差」）；LCP 和 CLS 都有足够数据的组才会出现在报告里；数值是最近 28 天的 p75（[Search Console 帮助](https://support.google.com/webmasters/answer/9205520)，核对 2026-10-21）。因此只修最差的一项，组的状态就能上升一级；三项都良好才全绿。
- **现场与实验室**：CrUX、Search Console 报告是现场数据（field），反映真实分布但不能归因；Lighthouse、DevTools 是实验室数据（lab），可复现可归因，但受模拟节流影响。顺序：现场定位「哪类页面、哪个指标差」，实验室复现并归因，改完回看现场。
- **CrUX 覆盖范围**：只收桌面版 Chrome（Windows、macOS、ChromeOS、Linux）和 Android 版 Chrome 的数据，且用户要开启使用情况统计和历史同步；iOS 版 Chrome、Android WebView、Edge 等其他 Chromium 浏览器不提供数据；页面和 origin 还要公开可发现、访问量足够（[CrUX 方法论](https://developer.chrome.com/docs/crux/methodology)）。低流量站可能查不到数据，用 web-vitals 自建 RUM 补盲。现场数据与 RUM 矛盾时以 RUM 为准（本套件口径：RUM 覆盖你自己的全部用户）。
- **CrUX 里的 TTFB**：BigQuery 自 2019-06 数据集起有 `experimental.time_to_first_byte`；CrUX API 自 2022-05 起提供 `experimental_time_to_first_byte`，名称至今带 experimental 前缀（[CrUX 发布说明](https://developer.chrome.com/docs/crux/release-notes)、[CrUX API](https://developer.chrome.com/docs/crux/api)）。

数据源选型：

| 数据源 | 类型 | 粒度与归因 | 适用 |
|---|---|---|---|
| Search Console CWV 报告 | 现场（CrUX） | URL 组级，无归因 | 定位哪类页面、哪个指标差 |
| CrUX API / BigQuery | 现场 | origin/URL 级；API 是滚动窗口、每天更新（[窗口与更新时间](../overview/facts.md#crux-window)）；BigQuery 按月 | 竞品对比、改动前后验证 |
| PageSpeed Insights | 实验室（Lighthouse）；页面界面仍显示现场数据，但 PSI API 计划停止返回 CrUX 数据（[PSI API 文档](https://developers.google.com/speed/docs/insights/v5/get-started)） | 单 URL | 单页快速诊断；现场数据改走 CrUX API |
| web-vitals 自建 RUM | 现场（自采） | URL、元素、交互级归因 | 决定修什么、验证修没修好 |
| Lighthouse / DevTools | 实验室 | 单次模拟 | 本地复现与 CI 回归 |

## 二、INP 深度

定义要点（[web.dev INP](https://web.dev/articles/inp)，核对 2026-10-21）：

- INP 观察整个访问期间所有点击、触摸和按键交互；每次交互的耗时 = 输入延迟 + 处理时长 + 呈现延迟，一直算到下一帧绘制。
- 取值：报告最长的一次交互，但每 50 次交互忽略最高的一次（交互很多的页面不会被单次异常拖累）；多数页面交互不到 50 次，所以通常报告的就是最差那一次。
- 悬停、缩放、滚动不计入 INP。
- FID 只测第一次交互的输入延迟；INP 覆盖全部交互的完整链路。

三段归因与对应修法（先用 RUM 拿归因，再对症）：

| 最长段 | 典型原因 | 先修什么 |
|---|---|---|
| 输入延迟 | 主线程被长任务或第三方占用 | 让出主线程、延迟第三方 |
| 处理时长 | 事件处理器本身太重 | 拆任务、减计算、防抖 |
| 呈现延迟 | DOM 更新量大、布局抖动 | 读写分离、减少 DOM 更新、先给即时反馈 |

**1）拆分长任务**

- 主线程上超过 50ms 的任务就是长任务（[web.dev 优化长任务](https://web.dev/articles/optimize-long-tasks)）。
- `scheduler.yield()`：Chrome 129+、Firefox 142+ 支持；Safari 不支持（[MDN 兼容数据](https://github.com/mdn/browser-compat-data) v8.1.6、[Chrome 博客](https://developer.chrome.com/blog/use-scheduler-yield)，核对 2026-10-21）。必须带兜底：

```js
const yieldToMain = ('scheduler' in window && 'yield' in scheduler)
  ? () => scheduler.yield()
  : () => new Promise(r => setTimeout(r, 0));

// 长循环每处理一批就让出主线程
for (const batch of batches) {
  process(batch);
  await yieldToMain();
}
```

- 与 `setTimeout(0)` 的差别：`scheduler.yield()` 的后续部分优先于其他已排队的新任务执行；`setTimeout` 让出后排到队尾，可能被别的任务插队（Chrome 博客）。
- 兜底不能用永不 resolve 的 Promise，否则 `await` 会无报错地永久挂起（工程判断）。

**2）Hydration 积压**（工程判断）

- SPA 常见问题：hydration 期间主线程被注水任务占满，点击落在未注水的节点上没有反应。
- 解法按成本递增：减少 JS（代码分割、删依赖）→ 选择性注水 / 岛屿架构 → 可恢复性框架 → 纯 SSR 加渐进增强。
- 首屏就要交互的组件先注水，其余空闲后注水。

**3）第三方脚本**：详见第六节。

**4）先给反馈**

- INP 只算到下一帧：慢处理器先把界面置为加载中，让下一帧尽快绘制。
- 搜索输入防抖；DOM 读写分离；动画用 `transform`/`opacity`。
- 用 web-vitals `onINP`（attribution 构建）拿到慢交互元素和三段耗时。`attribution` 是对象，不是数组（[web-vitals README](https://github.com/GoogleChrome/web-vitals)，main 6.2.3）：

```js
import { onINP } from 'web-vitals/attribution';

onINP(({ value, rating, attribution: a }) => {
  navigator.sendBeacon('/rum', JSON.stringify({
    url: location.pathname,
    value, rating,
    target: a.interactionTarget,          // 慢交互的元素
    type: a.interactionType,              // pointer | keyboard
    inputDelay: a.inputDelay,
    processingDuration: a.processingDuration,
    presentationDelay: a.presentationDelay,
  }));
});
```

**常见误区**

- 用 FID 判断响应性：老站「FID 全绿、INP 差」很常见。
- 指望实验室工具：web.dev 建议 INP 以真实用户现场数据为准。
- 只看加载后几秒：INP 覆盖整个访问期间。
- 平均用力修所有点击：先修最差的交互，收益最高。

## 三、CLS 深度

口径（[web.dev CLS](https://web.dev/articles/cls)，核对 2026-10-21）：

- 布局偏移按「突发」（session window）累计：相邻两次偏移间隔小于 1 秒，整个窗口最长 5 秒；CLS 取得分最高的那个窗口。
- 只有视口内可见元素改变起始位置才算偏移。新内容追加在下方、不推挤已有内容，不产生偏移。
- 用户点击、触摸、按键后 500ms 内的偏移会被标记 `hadRecentInput`，不计入；滚动、拖拽、缩放不算「近期输入」。
- 用 CSS `transform` 做动画不会触发布局偏移。

按出现频率排查（[web.dev 优化 CLS](https://web.dev/articles/optimize-cls)）：

**1）图片和视频没有尺寸**：所有 `<img>`、`<video>` 写 `width` 和 `height`，或用 CSS `aspect-ratio` 预留空间。

**2）Web 字体替换**：回退字体与 Web 字体度量不一致时，换字体瞬间整段文字重排。用 `size-adjust`、`ascent-override`、`descent-override`、`line-gap-override` 把回退字体调到接近 Web 字体：

```css
@font-face {
  font-family: 'Adjusted Fallback';
  src: local('Arial');
  size-adjust: 104%;
  ascent-override: 92%;
  descent-override: 24%;
  line-gap-override: 0%;
}
body { font-family: 'BrandFont', 'Adjusted Fallback', sans-serif; }
```

度量值用工具按实际字体计算，不要手猜。浏览器支持（[MDN 兼容数据](https://github.com/mdn/browser-compat-data)，核对 2026-10-21）：`size-adjust` Chrome 92+、Firefox 92+、Safari 17+；三个 `*-override` 描述符 Chrome 87+、Firefox 89+，Safari 仍是预览版。Safari 上这几项不一定生效，按渐进增强处理。`font-display: optional` 只在首次布局时字体已就绪才使用 Web 字体，可以避免重排。

**3）动态插入内容**：横幅、提示条插在已有内容上方必然偏移。新内容放在视口下方，或用 `position: fixed` 覆盖层，或用 `transform` 位移；列表懒加载用等高骨架屏占位。

**4）广告位与嵌入**：广告槽用 `min-height` 或 `aspect-ratio` 预留空间；填充失败也保留同尺寸占位。

```html
<div id="ad-top" style="min-height:250px"></div>
```

**5）bfcache**：让页面能进入往返缓存，用户后退时页面原样恢复，不再重复加载期的偏移（web.dev 优化 CLS）。

诊断工具：

- Chrome DevTools → Rendering → **Layout Shift Regions**：偏移区域高亮（[Chrome 文档](https://developer.chrome.com/docs/devtools/rendering/performance)）。
- Performance 面板的 Layout Shift 事件：查看引起偏移的节点。
- web-vitals `onCLS`（attribution 构建）：`attribution.largestShiftTarget`（偏移最大的元素选择器）、`largestShiftValue`、`largestShiftTime`、`largestShiftSource`、`loadState`（web-vitals README）。

**常见误区**

- 以为一切位移都算：只算视口内可见元素的意外位移；`transform` 动画不算。
- 占位高度靠猜：占位与真实渲染不一致照样偏移。
- 修完不做回归：把 CLS 写进 CI 的 Lighthouse 断言防复发。

## 四、TTFB

拆解：重定向 + DNS/TCP/TLS + 服务器处理时间（[web.dev TTFB](https://web.dev/articles/ttfb)）。CDN 能消除前两类和缓存命中时的第三类；源站慢只能修后端。TTFB 不是 Core Web Vital：只要不拖累 FCP 和 LCP，不必强求达到「良好」（web.dev 原话）。

分层修法（按见效排序，工程判断）：

1. **缓存 HTML**：最大杠杆是把 HTML 文档本身放进 CDN 缓存，而不只缓存静态资源；动态页用 stale-while-revalidate。缓存键只按必要的头和 cookie 区分，个性化片段拆成独立请求，否则缓存全部未命中。
2. **清理重定向链**：HTTP→HTTPS→www 每多一跳多一次往返，链接直达规范域名。
3. **缩短 SSR 时间**：流式渲染尽早输出首字节；数据获取并行；热点查询加缓存；数据库治理 N+1、补索引。
4. **边缘渲染**：把渲染放到边缘节点，消除单区域回源的往返时间。注意边缘运行时缺少部分 Node API。旧版本文写的「TTFB 可降 60–80%」没有可靠出处，已删除。
5. **103 Early Hints**：服务器还在生成页面时，先发 preload/preconnect 提示，浏览器提前取关键资源（[Chrome 文档](https://developer.chrome.com/docs/web-platform/early-hints)）。服务器能立即返回 200 时它没有用。

```http
HTTP/1.1 103 Early Hints
Link: </css/main.css>; rel=preload; as=style
Link: </img/hero.webp>; rel=preload; as=image; fetchpriority=high
```

   测量注意：103 响应算作「首字节」，所以 `responseStart`（即 TTFB）会变小；最终文档响应的开始时间看 `finalResponseHeadersStart`。Chrome 115–132 曾把 `responseStart` 改成最终响应，Chrome 133 起改回（web.dev TTFB）。载体：Cloudflare 开启 Early Hints 后，会缓存 HTML 响应里带 preload/preconnect 的 `Link` 头并发出 103（[Cloudflare 文档](https://developers.cloudflare.com/cache/advanced-configuration/early-hints/)）。

测量：实验室看 DevTools Network 的 Waiting（TTFB）；现场用 CrUX API 的 `experimental_time_to_first_byte` 和 RUM（Navigation Timing `responseStart`）。

## 五、LCP 增量

四段拆解、诊断顺序、`fetchpriority` 示例见 [LCP.md](LCP.md)，以下只补增量。

- **fetchpriority 已在主流浏览器支持**：Chrome 101+、Safari 17.2+、Firefox 132+（MDN 兼容数据 v8.1.6），可以直接使用。
- **Speculation Rules 预取/预渲染**：预渲染的下一页在导航时几乎已渲染完成，对下一页 LCP 改善很大（[Chrome 文档](https://developer.chrome.com/docs/web-platform/prerender-pages)，核对 2026-10-21）。
  - 支持：Chrome 109+；Safari 26.2 需开实验开关；Firefox 只在预览版部分支持（MDN 兼容数据）。按渐进增强接入。
  - 默认触发时机：document 规则默认 `conservative`（指针或触摸按下时）；list 规则默认 `immediate`。桌面端 `moderate` = 悬停 200ms 或按下时触发；移动端没有悬停，Chrome 自 2025-08 起改用视口启发式（停止滚动 500ms 后，对靠近上次按下位置的较大链接触发）。`eager` 自 Chrome 143 起不再等同 `immediate`：桌面端悬停 10ms 触发，移动端自 2026-01 起用简单视口启发式（链接进入视口 50ms 后）。
  - Chrome 上限：`immediate` 最多 50 个预取、10 个预渲染；`eager`/`moderate`/`conservative` 各最多 2 个，先进先出。document 规则配 `immediate` 才会大量过取，慎用。
  - 预渲染只对开启「预加载网页」设置的用户生效；内存不足、省流量或节能模式下会关闭。

```html
<script type="speculationrules">
{"prefetch":[{"source":"document","where":{"href_matches":"/*"},"eagerness":"moderate"}]}
</script>
```

- **响应式 LCP 图**：优先 AVIF/WebP；`sizes` 写准。常见错配：图片在 CSS 里实际是半宽，却写 `sizes="100vw"`，下载过大（工程判断）。

## 六、第三方脚本治理

审计法：

1. 清点：Lighthouse 13 起第三方信息放在「3rd parties」洞察里，只作信息展示，总是「通过」（[Chrome 文档](https://developer.chrome.com/docs/performance/insights/third-parties)）；旧版审计「Reduce the impact of third-party code」在第三方代码阻塞主线程 ≥250ms 时报警（[旧审计文档](https://developer.chrome.com/docs/lighthouse/performance/third-party-summary)）。再看 DevTools Network 按域名分组、Performance 面板按脚本归因主线程时间。
2. 三档分级（本套件口径）：
   - **A 关键业务**（分析、支付、A/B）：自托管或换轻量实现，`async`/`defer`，采集时机后移。
   - **B 可延迟**（热图、聊天、营销像素）：空闲时或首屏渲染完成后注入，或等首个交互信号。
   - **C 只在视口内有价值**（视频、地图、社交嵌入）：用 facade（缩略图 + 播放按钮），点击后才加载真组件。

   | 类别 | 例子 | 默认处置 |
   |---|---|---|
   | 分析 | GA4、标签管理器 | 批量上报；能服务端采集就服务端 |
   | A/B 测试 | Optimizely、VWO | 防闪烁设限时卸载；实验结束立刻摘脚本 |
   | 热图/录屏 | Hotjar、Clarity | 首屏后加载，调低采样率 |
   | 客服聊天 | Intercom、Zendesk | 等交互意图再挂载 |
   | 视频/社交嵌入 | YouTube、推文、地图 | facade，点击才注入 iframe |
3. Partytown 等方案把第三方脚本移进 Web Worker，兼容性有限，逐个脚本验证再上（工程判断）。
4. 制度化：设第三方 JS 预算（KB 上限）和标签管理器审批流程；没有闸门，治理后会很快反弹（本套件口径）。

## 七、CWV 与 SEO 的真实关系

- **官方口径**（[Google 页面体验](https://developers.google.com/search/docs/appearance/page-experience)，2026-09-22 更新，核对 2026-10-21）：Core Web Vitals 被 Google 的排名系统使用；Search Console 或第三方工具里的好成绩不保证排在前面；为了 SEO 追求满分不一定值得。Google 总是优先展示最相关的内容，即使页面体验欠佳；但很多查询有大量有用内容，这时好的页面体验有助于成功。**CWV 不是主排名杠杆，是同等相关时的加分项和负资产防线。**
- 页面体验自 2021-06 中旬起逐步纳入排名系统（[Google 2021-04 博客](https://developers.google.com/search/blog/2021/04/more-details-page-experience)，原文 Gradual rollout starting in mid-June）。
- 报告侧：Search Console 的「页面体验」报告 2024-11 中旬移除；它只是 CWV 和 HTTPS 两个报告的汇总页，这两个报告照常保留。官方说法见 Google Search Central 的 LinkedIn 帖（[原帖](https://www.linkedin.com/posts/googlesearchcentral_were-removing-the-page-experience-report-activity-7264284084145713152-rWCg)需登录，2026-10-21 未能直接读取；全文由 [Search Engine Roundtable 2024-11-19 报道](https://www.seroundtable.com/google-search-console-page-experience-report-gone-38436.html)引用）。
- 速度与营收（第三方研究）：Deloitte 受 Google 委托的《Milliseconds Make Millions》（2020）分析欧美零售、旅游、奢侈品、线索类品牌 4 周的移动端数据（核对 2026-10-21，数字与 [Deloitte 页面](https://www2.deloitte.com/ie/en/pages/consulting/articles/milliseconds-make-millions.html)一致）：4 项速度指标都提升 0.1 秒后，零售转化率 +8.4%、客单价 +9.2%（[Deloitte](https://www.deloitte.com/ie/en/services/consulting/research/milliseconds-make-millions.html)、[web.dev 摘要](https://web.dev/case-studies/milliseconds-make-millions)）。这是相关性观察，不是因果实验；所用指标（如 First Meaningful Paint）已过时。
- 结论：向业务要预算时用转化和体验论证；CWV 的 SEO 价值是防御性的。

## 八、优化优先级决策树

第 0 步：`python3 scripts/field_data.py --urls 清单文件 --strategy both` 或 Search Console CWV 报告确认哪个指标、哪类页面组差；没有现场数据先接 RUM。

按「影响 × 成本」的默认顺序（本套件口径）：

1. CLS 差 → 图片补尺寸、容器预留高度：纯标记改动，风险低。
2. LCP 差且 TTFB 段最长 → HTML 进 CDN 缓存、清理重定向。
3. LCP 差且加载延迟段最长 → LCP 图 preload + `fetchpriority="high"` + 去掉懒加载。
4. INP 差 → 先测第三方占主线程的比例：延迟或 facade 第三方往往比改自家代码便宜。
5. INP 差且是自家代码 → 拆长任务（yield 带兜底）+ 交互即时反馈。
6. TTFB 源站慢 → 数据库、缓存、流式 SSR：后端工程，周期最长。
7. 全部良好后 → Speculation Rules 预取/预渲染 + 跨文档 View Transitions。

   两项都按渐进增强接入，不做业务依赖：
   - Speculation Rules：见第五节。
   - **跨文档 View Transitions**：Chrome 126+、Safari 18.2+ 支持 `@view-transition`，Firefox 尚不支持（MDN 兼容数据 v8.1.6；[Chrome 文档](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)）。只用于同源导航，两个页面都要写 `@view-transition { navigation: auto; }`。过渡有超时，超时会直接跳过（具体时长未在 Chrome 文档核到）；不要把关键内容的展示押在过渡动画上。图片尺寸、字体度量、容器预留这些 CLS 基础一项不能省。

文字版决策树：

```text
哪个指标差？
├─ CLS  → 按频率排查：图片尺寸？广告/嵌入容器？字体替换？
├─ LCP  → 按 LCP.md 四段表，先修超出参考占比最多的一段
└─ INP  → 第三方占主线程比例高，先治理第三方；否则拆长任务、查注水
三项都是「需改进」→ 先修成本最低的一项；三项都良好才算整组良好
```

纪律：一次只改一类；改完等 CrUX 窗口（[长度](../overview/facts.md#crux-window)）滚动满再评估，不被单日波动带偏。

## 九、SPA 与软导航（2026-11-05）

SPA（单页应用）点链接时不重载整页，只用 JS 换内容并改 URL，这叫软导航。以前 CrUX 只记首次硬加载：后续路由切换不单独计，整个会话的交互和布局偏移都算在落地页头上。现在有了含软导航的实验指标（[日期、名称、转正时间](../overview/facts.md#crux-softnav)）。

- **先判断你是不是受影响的站**：多页站（每次点击都从服务器拿新 HTML）数字不会变。变化集中在「SPA + 后续导航多」的站（官方统计见事实表）。查法：CrUX API 返回里有没有 `*_with_softnavs`，再和稳定版比。
- **三项各怎么变**（[web.dev 2026-10-13](https://web.dev/blog/crux-experimental-soft-navs)，核对 2026-11-05）：
  - LCP：后续软导航复用已下载的代码和资源，通常变好。这是「后续点击本来就快」，不是 SPA 比多页站快。
  - INP：按每次页面浏览算，不再取整个会话里最慢的一次，通常变好；但路由切换时主线程上的重 JS 仍会让 INP 差。
  - CLS：按每次页面浏览分段，不再累计整个会话，通常变好。
- **怎么用**：
  1. SPA 站的基线表并列两列：稳定版和含软导航版。改动前后两列都记，不拿一列和另一列比。
  2. 实验版转正前，Search Console 的 CWV 报告和排名系统仍按稳定版（官方原话：稳定版 Core Web Vitals 分数不变）。达标判定、退出码、告警都只看稳定版；实验版只作诊断参考。
  3. 实验版的 INP 仍差 → 查路由切换时的长任务（第二节），不要指望「换口径」自动变好。
  4. 软导航的数据记在用户导航到的那个 URL 下，按页定位问题比以前容易：先按 URL 查实验版，找出哪个路由差。
  5. 自建 RUM：按 Chrome 的[测量软导航文档](https://developer.chrome.com/docs/web-platform/soft-navigations)接入，口径和 CrUX 对齐。
- **脚本**：`python3 scripts/field_data.py --url URL --key KEY` 有软导航数据时单列「含软导航（experimental）」一节，没有就不显示；实验值不进退出码、不进 `--as-cwv-csv`。
- **会变的地方**：官方说转正前每月都可能调整测量方法；11 月的发布预计加导航类型和 FCP 的软导航版。按月复核事实表。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 三项现场值 | `python3 scripts/field_data.py --url URL --strategy both --json` | 退出码 0 且三项 p75 都在良好区间 → 通过；退出码 1 → 有一项为差 |
| SPA 软导航口径 | 同上加 `--key KEY`，看 JSON 的 `field_softnav` | 有值 → 基线表并列两列；空 → 该 URL/origin 没有软导航实验数据，按多页站处理 |
| origin 级基线 | `python3 scripts/field_data.py --url https://example.com/ --crux-scope origin` | 用作改动前基线，记录日期 |
| CrUX 原始数据 | `curl -s -X POST "https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=KEY" -H 'Content-Type: application/json' -d '{"origin":"https://example.com","formFactor":"PHONE"}'`，读 `record.metrics.<名称>.percentiles.p75` 和 `record.collectionPeriod` | 记录 p75 和数据窗口；SPA 另查 `*_with_softnavs` 变体 |
| Search Console 分组 | Search Console → 体验 → Core Web Vitals → 移动设备/桌面设备 | 组状态 = 最差一项；「差」的组排第一优先 |
| INP 归因 | RUM 里 `onINP` 的 `interactionTarget` 与三段耗时 | 能指出最差交互元素和最长一段 → 可修 |
| CLS 来源 | DevTools Rendering → Layout Shift Regions；RUM 里 `largestShiftTarget` | 能定位偏移元素 → 可修 |
| TTFB | DevTools Network 看文档请求 Waiting；CrUX `experimental_time_to_first_byte` | ≤0.8s 良好；用了 103 时另看 `finalResponseHeadersStart` |
| 第三方占比 | Lighthouse「3rd parties」洞察 + Performance 面板按域名看主线程时间 | 记录每个第三方的主线程毫秒数，按第六节分级处置 |
| Speculation Rules 生效 | Chrome DevTools 的推测加载调试功能（步骤见 Chrome 文档「Debug speculation rules」，面板路径以当前 Chrome 版本为准）；页面里 `document.prerendering` 在预渲染期间为 `true` | 目标链接显示 prerender/prefetch 成功 → 通过；因「Preload pages」关闭、省电或内存限制被取消属正常，不算失败 |

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。官方口径优先，第三方数字均已标注。

- 一手（核对 2026-11-05）：web.dev [CrUX 软导航实验指标博文](https://web.dev/blog/crux-experimental-soft-navs)、Chrome [测量软导航](https://developer.chrome.com/docs/web-platform/soft-navigations)、[CrUX 指标方法论](https://developer.chrome.com/docs/crux/methodology/metrics)。
- 一手（核对 2026-10-21）：web.dev [Web Vitals](https://web.dev/articles/vitals)、[LCP](https://web.dev/articles/lcp)、[INP](https://web.dev/articles/inp)、[优化 INP](https://web.dev/articles/optimize-inp)、[CLS](https://web.dev/articles/cls)、[优化 CLS](https://web.dev/articles/optimize-cls)、[TTFB](https://web.dev/articles/ttfb)、[优化长任务](https://web.dev/articles/optimize-long-tasks)、[INP 公告](https://web.dev/blog/inp-cwv-march-12)；Chrome [CrUX 方法论](https://developer.chrome.com/docs/crux/methodology)、[CrUX API](https://developer.chrome.com/docs/crux/api)、[CrUX 发布说明](https://developer.chrome.com/docs/crux/release-notes)、[scheduler.yield](https://developer.chrome.com/blog/use-scheduler-yield)、[预渲染与 Speculation Rules](https://developer.chrome.com/docs/web-platform/prerender-pages)、[Early Hints](https://developer.chrome.com/docs/web-platform/early-hints)、[跨文档 View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/cross-document)；Google Search Central [页面体验](https://developers.google.com/search/docs/appearance/page-experience)、[Search Console CWV 报告帮助](https://support.google.com/webmasters/answer/9205520)；[web-vitals README](https://github.com/GoogleChrome/web-vitals)；[MDN browser-compat-data](https://github.com/mdn/browser-compat-data) v8.1.6。
- 第三方：[Deloitte《Milliseconds Make Millions》](https://www.deloitte.com/ie/en/services/consulting/research/milliseconds-make-millions.html)（2020）；[Cloudflare Early Hints 文档](https://developers.cloudflare.com/cache/advanced-configuration/early-hints/)。
