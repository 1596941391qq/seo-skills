# 中文市场专项(zh)

> 定位:中文市场门户页。引用经济学、平台浓度、CJK 阈值、采样纪律的完整版见 [chinese-ai-search-guide.md](../content/chinese-ai-search-guide.md);格式与 lint 参数见 `scripts/markets.json` 的 `markets.zh`。
> 2026-10-18 全文复核,2026-10-21 逐条重核(StatCounter CSV、百度/腾讯财报原文、CNNIC 报告、广告法与网信办办法原文、百度资源平台页面)。标注:【官】=平台或主管机关原文;【三方】=第三方研究或媒体(写机构与时间);【本套件口径】=本套件约定。断言半衰期 6–12 个月;引用偏好结论全部带测试日期,过期即复测。
> 索引:可引性模板见 [content-patterns.md](../content/content-patterns.md);跨平台 GEO 差异见 [geo-platform-differences.md](../content/geo-platform-differences.md);证据纪律以 [geo-evidence.md](../content/geo-evidence.md) 为准;提问对齐见 [question-alignment.md](../content/question-alignment.md);多语言流程见 [multilingual-workflow.md](../overview/multilingual-workflow.md)。

## 一、引擎与 AI 格局

**搜索引擎份额**(StatCounter,数据月 2026-09,取数 2026-10-18):

| 市场 | 全设备 | 桌面 | 移动 |
|---|---|---|---|
| 中国大陆([原图](https://gs.statcounter.com/search-engine-market-share/all/china)) | 百度 46.85%、Bing 21.61%、Yandex 15.01%、好搜 12.22% | Bing 41.21%、百度 28.32% | 百度 60.35%、Yandex 21.97% |
| 台湾([原图](https://gs.statcounter.com/search-engine-market-share/all/taiwan)) | Google 79.41%、Yahoo! 11.38%、Bing 8.29% | Google 66.09%、Bing 17.69% | Google 90.49% |
| 香港([原图](https://gs.statcounter.com/search-engine-market-share/all/hong-kong)) | Google 90.36%、Bing 3.99%、Yahoo! 3.67% | Google 81.78%、Bing 11.04% | Google 94.31% |

- 中国大陆数据单月波动大:2026-08 百度 59.10%,2026-09 46.85%,2026-10 49.08%(CSV,取数 2026-11-05);Yandex 11.42% → 15.01% → 11.58%。只作参考,不作预算依据。预算看自己站点的来源报表。
- Google AI Overviews:可用国家含香港、台湾,不含中国大陆;语言含简体中文、繁体中文(【官】[Google 帮助中心](https://support.google.com/websearch/answer/14901683?hl=en),核对 2026-10-18)。

**平台事实**:

| 平台 | 事实 | 来源 |
|---|---|---|
| 百度 | 2026 Q2「AI-powered Business」收入 125 亿元,占一般性业务收入 50%(Q1 为 52%);百度 App 2026-06 月活 6.44 亿;2026-06 推出 DuMate 企业版 | 【官】[百度 Q2 2026 财报](https://ir.baidu.com/node/14731/pdf) |
| 百度 | 2026-08-20 AI Day:百度 App 升级,方向是「从信息检索向全流程落地交付」 | 【三方】[科技日报 2026-08-20](https://www.stdaily.com/web/gdxw/2026-08/20/content_567190.html) |
| 微信 | 2026-06-30 微信及 WeChat 合并月活 14.39 亿;AI 智能体「小微」(WeLM 驱动)小范围灰度测试 | 【官】[腾讯 2026 Q2 业绩公告](https://www.tencent.com/wp-content/uploads/2026/08/%E8%85%BE%E8%AE%AF%E5%85%AC%E5%B8%83%E4%BA%8C%E9%9B%B6%E4%BA%8C%E5%85%AD%E5%B9%B4%E7%AC%AC%E4%BA%8C%E5%AD%A3%E4%B8%9A%E7%BB%A9.pdf)(2026-08-12;经营数据表 1,439 百万,「小微」段原文) |
| 微信 | 搜一搜 AI 搜索在混元模型之外灰度接入 DeepSeek-R1(2025-02 起) | 【三方】[新华网 2025-02-17](http://www.news.cn/tech/20250217/dde95a45605e4a20bf4798311e390a15/c.html) |
| 微信 | 2026-06-08 发布《关于开发者接入微信 AI 生态的指引》:小程序在「小程序管理后台 → AI 能力」授权接入微信 AI,分自动与开发两种模式 | 【官】[小程序 AI 开发模式接入指南(beta)](https://developers.weixin.qq.com/miniprogram/dev/ai/guide)(官方页只写开发模式);自动/开发两种模式的说法来自【三方】[观察者网 2026-06-08](https://www.guancha.cn/economy/2026_06_08_819794.shtml) |
| 豆包 | 新榜智汇监测:10 个统计行业的豆包引用第一名全部是抖音;豆包引用抖音的权重 2026-05 为 10.79%,2026-08 为 31.8% | 【三方】[新榜 2026-09-10](https://www.newrank.cn/article/detail/34738)、[新榜 2026-10-08](https://www.newrank.cn/article/detail/34775) |
| 网民 | 截至 2025-12:网民 11.25 亿;生成式 AI 用户 6.02 亿(普及率 42.8%);短视频用户 10.74 亿 | 【官】[CNNIC 第 57 次报告](http://www.cnnic.cn/n4/2026/0304/c88-11549.html)(短视频数见报告正文,[新浪转载](https://finance.sina.com.cn/tech/roll/2026-03-17/doc-inhrfshc8397107.shtml)) |

判读(本套件口径):流量入口在向 App 内助手迁移(百度 App、微信小微)。传统 SERP 优化的边际收益下降,平台阵地(第二节)的优先级上升。

## 二、平台阵地(本套件口径,按平台规则执行)

以下打法是本套件的执行约定。没有标来源的经验数字已删除;平台规则以各平台官方规范为准,执行前去平台后台核对。

### 微信(公众号 + 搜一搜)
1. 标题与摘要前置核心词;前 3 行写长尾问句。
2. 原创声明与认证先做完再谈搜索。
3. 问一问/AI 搜索有多个模型可选时,同一问题按模型分开采样、分开记录。
4. 灰度用户与非灰度用户看到的入口不同;采样记录账号状态。
5. 公开内容不堆 UTM;带参 URL 被引用会分散规范 URL。
6. 选题用微信指数做趋势验证。

### 小红书
1. 选题按搜索渠道做:标题写用户会搜的原话。
2. 正文前 3 行放长尾;结尾提问引导评论。
3. 私域导流只走平台官方组件;站外导流话术按《小红书社区规范》自查。
4. 站外 AI 难以引用登录墙内容:按站内搜索考核,不计入「AI 引用渠道」。

### 抖音与头条(豆包通道)
1. 豆包引用高度集中于字节系(见第一节新榜数据):抖音视频与图文、头条号图文是豆包 GEO 的主通道。
2. 同一素材在抖音与头条分开发,标题措辞区分,不发同文。
3. 视频前 3 秒口播核心词;字幕文本进入可检索范围。
4. 选题用巨量算数查词热度与关联词。
5. 企业号认证先做;认证对豆包引用的具体加权未见官方说明。

### 知乎与 B 站
1. 知乎回答用用户原话问句作开头;首段 80–200 字给出直接答案(本套件口径)。
2. 关键结论挂来源链接;不刷赞、不做矩阵互赞。
3. 想被引用的内容写成「定义段 + 有源数字 + 对比表」块。
4. B 站标题与简介写完整搜索问句;上传 CC 字幕,不依赖自动识别(专有名词识别错会丢相关性)。
5. B 站做 8 分钟以上深讲,抖音做 1 分钟结论:两边用户期待不同,不直接搬素材。

### 豆包头条通道(杠杆位,2026-10-11 归拢)
头条号是豆包生态里「图文半边」的通道,与抖音短视频半边配对。判据:平台在引用池内、图文位竞争密度低、字节生态同源。每季复核;本地竞争者填满即失效(主入口见 [multilingual-workflow.md](../overview/multilingual-workflow.md) 十节杠杆位表)。

## 三、语言机制

- **简繁**:简繁不混排。繁体另建独立页。hreflang 可用 `zh-Hans`/`zh-Hant`(ISO 15924 文字码),也可用 `zh-CN`/`zh-TW`(Google 按地区推导文字)。两种写法 Google 都支持;本套件偏好文字码,全站只用一种。来源:【官】[Google 本地化版本文档](https://developers.google.com/search/docs/specialty/international/localized-versions)(2026-09-21 更新)。
- hreflang 值不区分大小写;Google 不用 hreflang 或 `lang` 判定页面语言,用算法判定(同上)。
- **句长**:理想 15–25 字;超过 25 字拆句(本套件口径,lint 用 `sentence_ideal`)。
- **长度平价**:中文比英文短 20–40%;译页长度偏离超过 30% 提示未本地化(本套件口径,`parity_check.py` 读取)。
- **问句母语化**:「XX 好用吗/哪个好/多少钱/怎么选」,不用翻译腔。
- **营销词**:《广告法》第九条第三项规定广告不得使用「国家级」「最高级」「最佳」等用语;违反者由市场监管部门对广告主处 20 万–100 万元罚款(第五十七条第一项)。广告引用数据、统计、调查结果须真实准确并标明出处(第十一条);违反第十一条另按第五十九条处 10 万元以下罚款。适用范围:商品经营者或服务提供者介绍自己所推销商品或服务的商业广告活动(第二条),对象是「广告」,不是所有网页文字。来源:【官】[《广告法》全文(上海市市场监管局)](https://scjgj.sh.gov.cn/903/20250924/7e43b9954ca24b349488e5b464e83ac8.html)。本套件 lint 词表(超过 3 个/页即提示改成具体事实):

| 类别 | 词 |
|---|---|
| 空洞最高级 | 创新、领先、卓越、极致、最佳、顶尖、业内首创 |
| 包装腔 | 全方位、一站式、赋能、深耕、匠心、量身定制、颠覆 |
| 标题党(禁) | 暴涨、封神、必看、颠覆认知、王者、国民级、绝绝子 |

- 数字与日期:1,234.56;2026年10月9日;价格带日期(本套件口径)。数据用阿拉伯数字,成语叙事用汉字,全页统一。

## 四、内容规范(本套件口径)

- **三变体**,不跨渠道同文:官网权威页(最长,带 JSON-LD 与来源表)/公众号版(口语标题、结论先行、短段)/社区版(知乎体、小红书体)。
- **FAQ**:问题用口语问句,每答 80–200 字。官网 FAQ 是「可回答性」的补位手段。
- **长度**:不设字数下限。Google 明确没有偏好字数;百度标题规范只要求「简明扼要」。按问题覆盖完整度判断,不按字数判断。
- **可抽取块**:每个目标页含定义、2–5 个有源数字、对比表、步骤、「不适用边界」。
- **榜单页**:先写评选方法(维度、权重、数据来源、利益披露),再给榜单。没有方法论的榜单读起来就是软文。
- **百度标题**【官】:格式「核心词 + 修饰词」,修饰词建议不多于 3 个;间隔符建议统一用「-」;非首页的站点名放最末(首页格式是「站点名 - 官网」);过度优化的首页标题会被直接改写为站点名或公司名。来源:[百度搜索网页标题规范](https://ziyuan.baidu.com/college/articleinfo?id=2728)(2018-11-15)。markets.json 的 title 30、desc 78 是本套件 lint 阈值,不是百度规定。

## 五、外链与目录生态

- 排行站与品牌官网的引用占比差异见 [chinese-ai-search-guide.md](../content/chinese-ai-search-guide.md)(本文件不复述数字,口径以该文件为准)。
- 申报清单(本套件口径):maigoo、chnapp、cnpp、phb123 至少 3 家;askci、iimedia 按行业补。
- 友链只与正常运营的权威站交换;批量买卖链、自动链轮按垃圾链接处理。
- 国内提交式渠道(独立开发/AI 导航/社区)清单见 guide 第八节。

## 六、AI-GEO(引用偏好与采样)

| 引擎 | 已核事实 | 来源 |
|---|---|---|
| 豆包 | 10 个统计行业引用第一全是抖音;抖音权重 2026-05→08:10.79%→31.8% | 【三方】新榜智汇(见第一节) |
| 元宝/百度 AI/Kimi/千问/DeepSeek | 平台归属与引用偏好只作定性(元宝≈腾讯系,豆包≈字节系);份额数字以 guide 的带日期口径为准 | [chinese-ai-search-guide.md](../content/chinese-ai-search-guide.md)、[geo-evidence-bank.md](../content/geo-evidence-bank.md) |

- 采样纪律(Web/App 分开、环境四档、A–D 证据分级)见 guide 9.3–9.4。豆包 API 联网要在控制台开 web-search 插件;开与关是两个基线。
- 新榜智汇按月发布行业引用数据;跟踪其更新,替代盲测。

## 七、红旗与合规

- **AI 生成内容标识**【官】:《人工智能生成合成内容标识办法》2025-09-01 起施行。用户用平台发布 AI 生成内容时,应主动声明并使用平台的标识功能;任何人不得删除、篡改标识(第十条)。平台对未声明内容可加「疑似生成合成」提示(第六条)。来源:[国家网信办](https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm)。
- **广告法极限词**:见第三节。
- **ICP 备案**:没有找到百度对「备案与收录/排名关系」的官方说明。能查到的唯一官方条款在提交配额:无 ICP 备案的站点,「普通收录 → sitemap」每日提交上限为 1 个文件,已备案站点不受影响(百度资源平台公告 2021-05-14,[工具迭代更新汇总](https://ziyuan.baidu.com/college/articleinfo?id=3019))。是否备案按业务主体与主机位置决定;不要买「老备案壳」(本套件口径)。
- **蜘蛛池、泛目录**:本套件一律禁用。
- **收录提交**【官】:百度资源平台提供「普通收录」工具(API 推送、sitemap、手动提交);官方说明只缩短发现时间,不保证收录。来源:[普通收录](https://ziyuan.baidu.com/linksubmit/index)。
- **假权重**:爱站、站长之家的「百度权重」是第三方模拟值,只作趋势参考,不当事实引用。
- 每条主张可溯源;未验证标「待确认」,不用模型补(guide 证据纪律)。

## 八、工具表

| 工具 | 用途 | 备注 |
|---|---|---|
| 百度搜索资源平台 | 收录提交、抓取诊断、官方规范 | 【官】ziyuan.baidu.com |
| 5118 | 关键词挖掘、行业词库 | 第三方,估算值 |
| 爱站/站长之家 | 百度权重模拟、反链 | 第三方,非官方 |
| 微信指数 | 搜一搜与公众号选题验证 | 腾讯官方工具 |
| 巨量算数 | 抖音系词热度、关联词、画像 | 字节官方工具 |
| 百度指数 | 大盘热度基线 | 与巨量算数、微信指数交叉验证 |
| 新榜智汇 | 平台引用信源跟踪 | 第三方研究 |

> 工具产出的估算值一律标「测量 vs 估算」(it 市场同款纪律)。

## 九、检查清单

| # | 检查什么 | 怎么查 | 通过判据 |
|---|---|---|---|
| 1 | 简繁 hreflang | `python3 scripts/hreflang_cluster.py https://site/zh-hans/x https://site/zh-hant/x https://site/en/x` | 簇内全部互指;全站只用一种写法(文字码或地区码);无 `zh` 简繁同页 |
| 2 | 简繁混排与营销词 | `python3 scripts/market_lint.py --market zh page.html --report` | 简繁混检无命中;营销词 ≤3 个/页;CRITICAL 0 |
| 3 | 广告法极限词 | 在广告和落地页文案里搜「国家级、最高级、最佳」(第九条第三项原文)和同类词「第一、顶级、唯一」(「等用语」的常见对象,本套件口径) | 广告文案零命中;引用数据都标出处(第十一条) |
| 4 | AI 生成内容标识 | 抽查在公众号、小红书、抖音发布的 AI 生成内容 | 发布时已用平台标识功能声明 |
| 5 | 爬虫可达 | `python3 scripts/robots_posture.py https://site/robots.txt --json`;另 `grep -iE "baiduspider|bytespider" robots.txt` | 对 Baiduspider、Bytespider 有明确决策并记录;不误封 |
| 6 | head 分享标签 | `python3 scripts/head_check.py https://site/x --market zh` | 微信/QQ 分享相关 itemprop 在场(对中文站是真信号) |
| 7 | llms.txt 假阳性 | `python3 scripts/llmstxt.py check https://site`,再 `curl -s https://site/llms.txt \| head -3` | 首行是 `# ` 标题,不是 HTML |
| 8 | 百度收录提交 | 资源平台「普通收录」提交 sitemap 与新 URL | 提交成功;抓取诊断无异常 |
| 9 | 平台阵地 | 百科、百家号、知道、公众号逐项检查占位 | 缺项写进待办(markets.json special_checks 第 1 条) |
| 10 | 证据阶梯 | `python3 scripts/citation_panel.py init --brand B --prompts prompts.csv --engines doubao,yuanbao,deepseek,kimi`,每次采样后 `record --engine doubao --file run.csv` | 六级分开记,不合并成「AI 可见性提升」 |

## 十、本地实测(2026-10-09,本套件记录)

- 跑了 zhihu.com 与 taobao.com × `site_audit --market zh` / `llmstxt check` / `head_check`。
- zhihu:title 14 字;desc 217 字,超过本套件百度阈值 78;无 H1、canonical、og、JSON-LD。robots.txt 的 `User-Agent: *` 段为 `Allow: /tardis/jm` + `Disallow: /`,四条 AI 检索爬虫与 Google-Extended 全禁;Googlebot、bingbot、Baiduspider、Sogou 有专属放行段。
- taobao:title「淘宝」2 字;desc 113 字;无 H1;robots 只有一组 `User-agent: *`,AI 检索爬虫放行,没有 Baiduspider 专属段(2026-10-21 复查:该组含 3 条 Allow 和 1 条 `Disallow: /*?*`)。
- `llmstxt check`:两站 `/llms.txt` 等路径都返回 200,内容却是 SPA 的 HTML 回退页。工具只看状态码,属假阳性。
- `head_check`:两站都命中 x-ua-compatible 弃用 ERROR(旧口径);微信/QQ itemprop 缺失 WARN 对中文站是真信号。
- **脚本口径 2026-10-21 已改**:`head_check` 里 twitter:* 与 OG 重复只记 INFO,x-ua-compatible 记「可删旧标签」INFO,元素顺序只记风格 INFO;`site_audit` 缺 H1、缺 description 记 WARN;zh 的 title/description 按显示宽度计(全角 1、半角 0.5,上限 30 / 78),description 下限取 `markets.json` 的 `desc_min`(zh=39),title 无下限。下面「工具盲区」里关于 title 下限 20、desc 下限 80 的说法按旧口径写,已失效。复跑以新口径为准。
- 工具盲区:`Disallow: /?` 旧版会被当整站禁止(已修,见 ru.md 第八节),中文站仍建议复核 robots 原文;百科/百家号/公众号占位、简繁混检、营销词密度不在 site_audit 覆盖内。

## 维护

- 复审周期 **90 天**,下一次 **2027-01-09**;signals 清单与 `scripts/markets.json` 的 `markets.zh.review_cycle` 保持一致,以 json 为准。
- 触发即复审:百度与腾讯季报、百度搜索资源平台公告、微信 AI 入口与开发者指引变化、新榜智汇月度数据、网信办与市场监管总局新规。
- 知乎 AI 爬虫封锁、淘宝 robots 姿态属可逆决策,每季实测复查。
