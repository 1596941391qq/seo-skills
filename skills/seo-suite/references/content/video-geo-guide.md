# 视频 SEO/GEO(被 AI 引用的视频层)

> 建立于 2026-10-09;2026-10-21 逐条重新核对(2026-11-05 补 VideoObject `creator` 和 Search Console 平台属性,复核于 2026-11-05):Google、YouTube、Gemini API、Spotify 官方文档逐句读过;第三方研究标注来源、样本和时间。YouTube 站内算法、变现和各平台排序的数字没有一手来源,已删除(见文末)。「本套件口径」是做法约定,不是平台规则。

## 一、AI 怎么用视频

**官方机制**

- **Gemini API 读视频**:默认静态处理,以 1 FPS 抽帧,并取音频;可以把公开的 YouTube URL 直接传给 Gemini API(预览功能);只能上传公开视频,不能上传私有或不公开视频([Gemini API 视频理解](https://ai.google.dev/gemini-api/docs/video-understanding),核对 2026-10-21)。含义:帧画面和音频转写是两条信息通道。
- **官方 transcript 取不到别人的视频**:YouTube Data API 的 `captions.download` 要求调用者有编辑该视频的权限([文档](https://developers.google.com/youtube/v3/docs/captions/download))。主动上传并校对过的字幕,是你唯一能控制的文本层。

**第三方研究(带样本;引用时必须写样本和时间)**

| 研究 | 样本与时间 | 结论 |
|---|---|---|
| BrightEdge([链接](https://www.brightedge.com/resources/weekly-ai-search-insights/youtube-presence-ai-search)) | AI Catalyst 数据,2024-05 至 2025-09 | YouTube 在各 AI 平台平均占 20% 引用份额;在 Google AI 概览里 29.5%、排第 1 的域名;AI Mode 16.6%;Perplexity 9.7%;ChatGPT 0.2% |
| OtterlyAI([链接](https://otterly.ai/blog/youtube-ai-citation-study-2026/)) | 超过 1 亿次 AI 引用,30 天,2026 年发表 | 94% 的 YouTube 引用指向长视频;播放、点赞、订阅数与引用频率几乎不相关(r ≈ −0.03);40.83% 的被引视频播放量不足 1,000;带时间戳的引用只出现在 Google AI 概览(73%)和 AI Mode(27%) |

- 两项都是厂商研究,方法细节以原文为准。含义:不要用播放量判断一条视频能不能被 AI 引用;文本可及性(字幕、章节、描述、页面)更值得先做。
- 「ChatGPT 只读视频附着的文字、不读像素」没有一手来源,已删除。

## 二、Google 视频索引与富结果要求(官方)

出处:[视频 SEO 最佳做法](https://developers.google.com/search/docs/appearance/video)(2025-12-18 更新)、[VideoObject 结构化数据](https://developers.google.com/search/docs/appearance/structured-data/video)(2026-09-24 更新)、[视频 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/video-sitemaps)(2026-05-20 更新)。

- **索引条件**:watch page 必须被索引,且在搜索里表现良好,其视频才可能被考虑索引;视频必须嵌在 watch page 上且不被其他元素遮挡;有付费墙时要加付费内容结构化数据;缩略图必须有效且 URL 稳定。
- **缩略图**:至少 60×30 像素,越大越好。CDN 的过期 URL 会让视频无法索引。
- **文件类型**:Google 能处理 3GP、3G2、ASF、AVI、DivX、M2V、M3U、M3U8、M4V、MKV、MOV、MP4、MPEG、OGV、QVT、RAM、RM、VOB、WebM、WMV、XAP;不支持 data URL。要进入 key moments、视频预览,视频文件也要有稳定 URL。
- **元数据**:Google 支持结构化数据、视频 sitemap 和 Open Graph。为每个视频建独立 watch page(只有一个视频是页面主旨)。
- **创作者 `creator`(2026-09-24 加入文档)**:VideoObject 的推荐属性,值是 `Person` 或 `Organization`(也认 `author`);写了 `creator` 就要有 `name` 或 `alternateName`,`url` 指向能唯一识别创作者的页面(个人主页或机构首页)。同次更新列出 `interactionStatistic` 支持的四种 `interactionType`:`WatchAction`(观看数)、`LikeAction`(点赞)、`CommentAction`(评论数)、`ShareAction`(转发)([VideoObject 文档](https://developers.google.com/search/docs/appearance/structured-data/video)、[更新记录](https://developers.google.com/search/updates) 2026-09-24,核对 2026-11-05)。本套件口径:`creator.url` 指向站内作者页,和 Article 的作者实体用同一个 `@id`。
- **Key moments 两种做法**:`Clip` 结构化数据(精确起止时间和标签,所有 Google 搜索支持的语言);`SeekToAction`(告诉 Google 时间戳在 URL 里怎么写,仅限英、西、葡、意、中、法、日、德、土、韩、荷、俄语);YouTube 托管的视频,在 YouTube 描述里写时间戳。你设定的 key moments 优先于 Google 自动识别的。
- **视频 sitemap**:sitemap 里引用的所有 URL 必须允许 Googlebot 抓取(不被 robots.txt 禁止、不需要登录、不被防火墙拦);不要列与宿主页内容无关的视频;`<video:content_loc>` 等价于 `VideoObject.contentUrl`,`<video:player_loc>` 用于 YouTube、Vimeo 等 iframe 嵌入,对应 `embedUrl`(官方 sitemap 文档标明等价关系);官方推荐优先提供 `content_loc`;单个 sitemap 文件受通用 [sitemap 上限](../overview/facts.md#sitemap-limits)约束。同一信息写在 sitemap 里或结构化数据里都行,不会因为写两份而叠加权重(本套件口径)。
- **地域限制**:用 `<video:restriction>`(sitemap)或 `regionsAllowed`(结构化数据)。没有国家限制的视频不要写,误写会让视频在其他地区消失。
- **决策口诀(本套件口径)**:只嵌 YouTube → 做 VideoObject(`embedUrl`);自托管视频 → VideoObject(`contentUrl`)加视频 sitemap;视频在 JS 弹层或无限滚动里 → sitemap 是更可靠的发现通道。

**视频 sitemap 验收命令(自托管视频站)**

```bash
# 1) 条目数(单文件 ≤50,000)
curl -s https://example.com/video-sitemap.xml | grep -c '<url>'
# 2) 缩略图、标题、描述标签数应与视频条数一致
for t in video:thumbnail_loc video:title video:description; do curl -s https://example.com/video-sitemap.xml | grep -c "<$t>"; done
# 3) 视频文件能被 Googlebot UA 取到前 1KB(不被 robots/WAF 拦)
curl -s -A "Googlebot" -o /dev/null -w "%{http_code} %{content_type}\n" -r 0-1024 "https://cdn.example.com/v/123.mp4"
# 4) 页面 VideoObject 的 contentUrl 与 sitemap 一致
curl -s https://example.com/watch/123 | grep -o '"contentUrl":\s*"[^"]*"'
# 5) 全球内容上不应出现国家限制
curl -s https://example.com/video-sitemap.xml | grep -c 'video:restriction'
```

## 三、视频 GEO 实操清单

1. 上传人工校对的字幕(本套件口径;官方 transcript 拿不到别人的,见第一节)。
2. 章节:YouTube 描述里写时间戳,自托管页面用 `Clip` 标记。
3. 描述前几行写事实句和可引用的结论;标题带目标查询词(本套件口径)。
4. 自建 watch page:VideoObject、`contentUrl` 可抓取、视频 sitemap。
5. 口播里自然说出关键词,屏幕文字开头出现关键词(本套件口径;平台对口播和屏幕文字的索引没有一手文档)。
6. **多语言音轨**:YouTube 的 Multi-language audio 让一个视频(含 Shorts)带多条音轨,长视频还可上传各语言缩略图;官方帮助页说,视频有翻译后的标题和描述后,搜索系统会按这些翻译文本匹配用户语言;该功能面向有「Advanced features」权限的创作者([YouTube 帮助](https://support.google.com/youtube/answer/13338784))。单频道多音轨与分语言频道哪个更好,没有官方结论。
7. **hreflang**:Google 的视频文档里没有视频专用的 hreflang 说明(本组读到的版本),视频集合页沿用页面级 hreflang。YouTube 托管的视频无法加 hreflang;自建 watch page 每种语言一个 URL 并各自带本地化的 VideoObject(本套件口径)。
8. 监测:用 `citation_panel.py record`(口径见 [kpi-definitions.md](../monitoring/kpi-definitions.md))对目标问题定期采样,看自己的视频是否被 AI 面引用;引用不等于播放。

**Search Console 平台属性(社媒与视频账号在 Google 上的表现)**:2026-07-07 公布,2026-07-29 全球开放,同日发布分析指南([公布博文](https://developers.google.com/search/blog/2026/07/search-console-social-video-platforms)、[全球开放博文](https://developers.google.com/search/blog/2026/07/platform-properties-social-video-guide)、[帮助页](https://support.google.com/webmasters/answer/17148418)、[分析指南](https://developers.google.com/search/docs/monitor-debug/analyze-social-video-content),核对 2026-11-05)。
- 支持 Instagram、TikTok、X、YouTube 四个平台,每个账号或频道单独加一个属性,按平台提示授权验证;已认领 Google 搜索资料(Search profile)的,已验证账号会自动出现在 Search Console。验证后要几天才有数据;登录授权过期会暂停访问,重新验证后历史数据还在。
- 报告:效果报告(点击、展示、CTR、平均排名,可按帖子、查询、国家、设备筛,覆盖 Google 搜索、Discover、Google 新闻,后两者有流量才出现)、Insights(趋势、热门内容、查询分组)、Achievements(点击里程碑)。只统计 Google 上的表现,不统计平台站内的播放和曝光。
- 计数口径:Instagram 快拍出现在 Google 搜索里算展示、被点算点击;视频在 Google 结果里被点、即使在 Google 自己的播放器里打开,也算点击。Insights 顶部总数含网页、图片、视频、新闻搜索的点击,下方明细只算网页搜索,所以明细合计会小于总数。
- 用法(指南):看查询分组(上升、下降)定下一个选题和标签;用 24 小时筛选抓刚起量的帖子,到别的平台跟进;把几个平台的属性导出到同一张表并排比;用页面筛选比较播放列表、Shorts 和长视频;改 YouTube 标题或 TikTok caption 后用 Search Console 注释记一笔,看搜索表现有没有变。指标口径见 [kpi-definitions.md](../monitoring/kpi-definitions.md) 第一节「平台属性」。

**短视频平台(TikTok、Reels、Shorts)**:这三个平台站内搜索的索引规则没有找到一手文档,不给平台专属数字。通用做法(本套件口径):标题或 caption、口播、屏幕文字围绕同一个问题,各层说法一致。

**转录**:开源 OpenAI Whisper 起草,人工校对数字、专名、术语,再上传为字幕,并把全文放进自建 watch page(本套件口径)。

## 四、市场差异

- **韩国**:Naver TV 于 2026-09-30 15:00 关停,内容迁移到 Clip([Herald 2026-07-31](https://mbiz.heraldcorp.com/article/10826754)、[Chosun 2026-07-30](https://biz.chosun.com/en/en-it/2026/07/30/W7NSHITITFC5JCYJPQRYHVREQY/),第三方新闻)。
- 其他市场的用户数、平台份额旧版有数字,没有找到一手来源,已删除;做客户方案前按目标市场查最新的统计机构或平台数据。
- 地域控制见第二节(`regionsAllowed`)。

## 五、播客(发现机制与转录层)

- **Spotify(官方)**:Spotify for Creators 文章称,Spotify 现在为每个符合条件的单集自动生成 transcript、章节、嘉宾和主题标签;transcript 给 Spotify 的系统提供单集的全文版本用于索引,让内容可以在主题和关键词层被发现([Spotify for Creators](https://creators.spotify.com/resources/podcast-seo))。
- **Apple Podcasts**:2024-03 起提供 transcripts([Apple Newsroom 2024-03-05](https://www.apple.com/newsroom/2024/03/apple-introduces-transcripts-for-apple-podcasts/)、[Apple 帮助](https://podcasters.apple.com/support/5316-transcripts-on-apple-podcasts))。transcript 是否进 Apple 站内搜索,本组没有找到一手说法(未核)。
- **本套件口径的做法**:
  1. 每集有 transcript;自建 episode 页放全文(Google 搜索流量主要靠页面文字,不靠音频文件)。
  2. episode 标题写搜索意图,节目名写品牌。
  3. RSS 填完整的 iTunes 标签;节目名称和描述在各平台一致。
  4. 章节化 show notes(时间戳加要点)。
  5. 视频化复用(YouTube 或 Shorts 切片)。
- 旧版引用的「加 transcript 后站内入站流量 +4.36%」(3Play Media 自述)和「PodcastEpisode 富结果 2023 年弃用」没有找到一手来源,已删除。

## 六、YouTube 站内算法:证据边界

YouTube 站内分发(CTR 基准、留存阈值、Shorts 信号层级、RPM、会员与联盟门槛、A/B 测试细节)的旧版数字大多来自第三方仓库和单一厂商博客,没有 YouTube 官方文档支持,已全部删除。处理客户的 YouTube 频道时:

- 用该频道自己的 YouTube Studio 数据,不套行业基准。
- 找「包装吃到流量」的假设:导出频道视频清单 CSV(列 `title,duration_s,views[,is_short][,channel]`),跑 `python3 scripts/yt_outlier.py videos.csv`。它按频道和形态(≤60 秒算 Short)分组,播放量超过组均值 2 倍的视频列为离群(本套件口径)。离群只是假设来源,不是结论。
- 变现、政策和披露要求以 YouTube 帮助中心和 FTC 原文为准,本套件不转述数字。

## 七、检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| watch page 已索引 | Search Console 网址检查 watch page URL | 显示已编入索引为通过 |
| 缩略图稳定且够大 | `curl -sI 缩略图URL`;`sips -g pixelWidth -g pixelHeight 图片`(macOS) | 返回 200、尺寸 ≥60×30、多次抓取 URL 不变为通过;URL 带过期签名为失败 |
| 视频文件可被 Googlebot 取到 | 第二节命令 3 | 200 且 content-type 为视频为通过 |
| VideoObject 必填字段 | Rich Results Test;`curl -s watch页 \| grep -o '"contentUrl"[^,]*'` | 无 error 为通过 |
| sitemap 与标记一致 | 第二节命令 1、2、4 | 条数 ≤50,000、标签数一致、contentUrl 一致为通过 |
| 不误用地域限制 | 第二节命令 5 | 全球内容输出 0 为通过 |
| key moments | 页面有 `Clip` 标记,或 YouTube 描述含时间戳(0:00 起) | 有为通过 |
| 字幕与全文 | YouTube Studio 字幕栏是人工上传版;watch 页有 transcript 全文 | 有为通过 |
| 平台属性已接入 | Search Console 属性下拉里有各平台账号 | 每个在运营的 Instagram、TikTok、X、YouTube 账号各有一个属性、能看到效果报告为通过 |
| 视觉与视频搜索测量 | Search Console 效果报告的 multimodal 筛选(见 [image-search-seo.md](image-search-seo.md));`python3 scripts/multimodal_report.py --gsc gsc.csv --videos videos.csv` | 能导出并与视频清单 join 为通过 |

## 来源

- 官方:[Gemini API 视频理解](https://ai.google.dev/gemini-api/docs/video-understanding)、[YouTube captions.download](https://developers.google.com/youtube/v3/docs/captions/download)、[视频 SEO 最佳做法](https://developers.google.com/search/docs/appearance/video)、[VideoObject](https://developers.google.com/search/docs/appearance/structured-data/video)、[视频 sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/video-sitemaps)、[YouTube Multi-language audio](https://support.google.com/youtube/answer/13338784)、[Spotify for Creators](https://creators.spotify.com/resources/podcast-seo)、Apple Newsroom。
- 第三方:BrightEdge、OtterlyAI(研究);Herald、Chosun(Naver TV 关停)。
- 2026-10-21 删除的旧说法(没找到一手或可信出处):「播放量被引相关性 52%」「41% 被引视频播放不足 1,000」归属 Gumshoe(实际是 OtterlyAI)、Gemini「按付费层取帧」、ChatGPT「读词不读像素」、CTR 诊断线 4%/留存 80% 等算法数字、各市场视频平台用户数与份额、转录服务排名、短视频三平台文本层表、YouTube 站内算法与变现全部数字、播客 +4.36% 与 PodcastEpisode 弃用说法。
