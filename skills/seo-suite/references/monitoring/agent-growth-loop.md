# 增长周循环:让 AI agent 每周只推一个「赚钱页」

> 建立于 2026-10-17，2026-10-21 重核，复核于 2026-11-05（加第八节 Chrome 给 agent 的工具）。来源:X @EXM7777 长文《How to automate SEO with Opus 5.5 (Full Course)》(2026-09-23，正文经 fxtwitter 全文读取)。原文由一款 Slack 内 AI 员工产品赞助,文中「托管自动驾驶」那条路线是广告位,本文件不收。**这是一位从业者的工作方式，没有对照数据，本文件全部按「本套件口径的实践方法」使用，不当作 Google 或行业规定。**
> 以下是与本套件已有内容查重后**只留新增、可操作的部分**,用本套件口径改写。
>
> 分工:[continuous-operations](continuous-operations.md) 管「站点今天有没有出事」(监控、告警、自动安全项);
> [program-management](program-management.md) 管「改动怎么立项和审批」;本文件管**「这周该把力气花在哪一页、改哪一处、怎么判输赢」**,
> 并且默认由 AI agent 执行、人只做批准。GSC 数据口径、实验七要素与四里程碑仍以 [kpi-definitions](kpi-definitions.md) 和
> [geo-evidence](../content/geo-evidence.md) 为准,这里不重复。

## 一、前提:先让页面能转化,再要流量

- 动手前写下「一次转化是什么」(注册、预约、下单、付费调用),并确认它在分析工具里是**单独命名的事件**,不是工具自动猜的。
  没有命名事件,后面所有判输赢都无从谈起。
- 页面上没有清晰下一步(注册、预约、结账)时,先补下一步,再做任何 SEO。排名和曝光涨了而转化不动,一律记为没赢。

## 二、零站起步:只建两页

还没有站或没有任何自然流量时,第一个月只做两页,不铺量:

1. **一页落地页**:围绕一个「准备付钱前才会搜」的问题(行动型意图,不是好奇型意图),写清卖什么、给谁,
   首屏就有那个唯一的下一步。
2. **一页支撑页**:回答买前紧挨着的一个问题,正文里链到落地页。

这样周循环一开始只有两个候选页,判定简单。选词判据沿用 [keyword-intent-taxonomy](../research/keyword-intent-taxonomy.md) 的意图分类。

## 三、agent 的工作目录:三个文件每次都读

| 文件 | 内容 | 纪律 |
|---|---|---|
| `brief` | 业务、卖什么、谁买、什么算一次转化、品牌绝不会说的话 | 改得最多;agent 对页面的判断只会和它对 brief 的理解一样好 |
| `state` | 每个在跟进页面的基线数字(按天拉取的 GSC 页面/查询数据、每页转化数) | 按**天**增量拉 GSC 存进来。官方建议每天只取一天的数据，既不容易超配额，也避免按页面和查询分组时丢数据（[Search Console API](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data)，核对 2026-10-21）;不要每次拉一大段覆盖 |
| `log` | 每次运行追加一条:看了什么、建议了什么、哪天上线了什么改动 | **只追加不删改**;三周后判效果时要知道每个改动上线多久了 |

接入与安全(写进第一周,先于第一次真实运行):

- 每个付费数据源先设花费上限;有沙盒的先用沙盒(例如 DataForSEO 的 sandbox 返回同结构的假数据、不计费（[官方说明](https://docs.dataforseo.com/v3/appendix/sandbox/)，核对 2026-10-21）),
  让 agent 先学会数据形状再碰预算。
- 对外动作一律卡在人工批准:发布、改线上页面、提交 URL 前必须停下来等确认。用宿主的工具前置钩子或「遇到无权限操作就暂停」的权限模式
  实现,不要只写在提示词里。定时任务用会停下等批准的模式;无人值守的云端例行任务只给只读权限,永远不给发布凭据。
  动作分级沿用 [continuous-operations](continuous-operations.md) 第五节的 auto / draft PR / human 三档。
- 每个结论附来源 URL;数据缺了就写「缺数据」,不许猜补。竞品分析必须读竞品**原页全文**再比较,不能凭印象复述对方写了什么。

## 四、选页:找一页「赚钱页」,不做全站审计

全站审计会给一堆小问题,却说不清哪个值钱。第一步只找**一页**:

1. 从 GSC 拉每页近几周的曝光、点击、平均排名;从分析工具拉**每个落地页的转化数**;按页对齐。
2. 候选条件三个同时满足:**已经能把来访者转化**;**已经有搜索曝光**;**排名差一点**(落在 striking distance,口径见
   [kpi-definitions](kpi-definitions.md) 的 striking distance 行),多数搜索者还看不到它。排名一涨就直接变成转化的,就是它。
3. **流量陷阱要单独标出、不推荐**:曝光很多、转化为零的页。
4. 对两三个候选,查它背后的主要查询:搜索量、当前前排是谁;再**打开主查询的实时结果页**看前排是什么类型的页。
   前排全是教程而候选是价格页,说明查询要的东西和你卖的不一样,怎么调都没用(意图错配,判据同
   [site-type-playbooks](../overview/site-type-playbooks.md))。
5. 每个候选给三选一结论:**保留** / **改掉一个条件后保留** / **放弃**,并附查看过的页面链接。竞品赢在外链而不是内容时,
   记为另一项工作(外链),不要硬改正文。
6. 本步产出只有三样:一页、一个主查询、一段写下来的理由。

## 五、单页体检:四遍,最后一遍看转化

前三遍沿用套件已有方法,只列入口:

1. **能不能被抓到**:可抓取、状态码、可索引正文、移动端性能;依赖 JS 的站对比原始 HTML 与渲染后正文
   ([rendering-seo](../technical/rendering-seo.md)、[cwv-playbook](../technical/cwv-playbook.md))。
2. **竞品**:主查询前十名逐页抓全文,与本页并排读,产出「他们覆盖而我们没有的点、他们回答而我们跳过的问题、我们说得更好的地方」,
   每条带来源 URL ([competitor-page-patterns](../research/competitor-page-patterns.md))。
3. **答案引擎**:标题按用户的问法写、每个标题下第一句就回答、每节单独读也成立、各处的业务信息一致;
   第三方讨论(论坛、视频、行业媒体)里的提及与错误信息另列清单。哪些手段有证据、哪些是炒作,以
   [geo-evidence](../content/geo-evidence.md) 为准(例如 schema 不当作 AI 引用捷径)。
4. **转化路径**(本文件新增):像买家一样读页面——是否只有一个明显的下一步、它出现得够不够早、买前最后几个疑虑有没有被回答;
   转化是否记成单独命名的事件;站内已经有流量的页面里,哪些该加一条指向这页的内链。

四遍结束写成一份报告:把修复项排序,**只推荐先做一项**。

## 六、每周循环:六步,一次只改一处

1. 拉新的搜索数据和转化数进 `state`;
2. 和**上一次改动之前**的基线比;
3. 检查这页本周有没有被改坏(可抓取、状态码、关键元素);
4. 带证据和链接**只推荐一个改动**;
5. 等人批准后才起草或发布;起草在 CMS 里完成,发布前由人做最后一读(品牌语气只有人能把关);
6. 把发生了什么、改了什么、哪天上线写进 `log`。

判定纪律:

- **一次只改一处**:同一周改标题、开头和内链,就永远不知道是哪个起作用。
- 两周以内的排名波动不算信号（本套件口径;Google 对核心更新的建议是更新结束后至少等满一周再分析，见 [核心更新说明](https://developers.google.com/search/updates/core-updates)）;表现好的页没有强理由不动（官方也建议避免对已表现好的内容做大改）。
- **搜索和业务一起判**:排名涨了但转化没涨 → 记为没赢;排名没动但转化因更清楚的行动号召变好 → 记为赢,不争论。
- 测试期间**冻结 agent 的指令**:中途改提示词,本周结果就和上周不可比。指令版本号写进 `log`。
- AI 引用数据同样谨慎:平台侧的模型更新会让引用数自己变,不要归功于某次改动。
  (原文称 Bing 明确说过引用趋势不能归因到单个改动——**未核**，Bing 官方指南见 [geo-evidence](../content/geo-evidence.md)。)
- 一个改动给足观察窗再判;判完再选同页下一处,或换下一张赚钱页。

## 七、前四周排期

| 周 | 做什么 | 完成标准 |
|---|---|---|
| 1 | 接入搜索、关键词、抓取、转化数据源,设花费上限与批准规则;写 `brief`;确认转化是命名事件;把几周历史拉进 `state` | 第一次真实运行前,所有对外动作都会停下等批准 |
| 2 | 选出赚钱页,跑四遍体检 | 人逐条追问来源,没有来源的结论被删掉;双方定下先做的一项 |
| 3 | 上线周:agent 起草,人审后亲手发布 | `log` 记下日期和确切改了什么 |
| 4 | 启动每周定时循环并开始计量 | 改动再观察几周才判输赢;之后进入「同页下一处 / 下一张赚钱页」 |

## 八、Chrome 给 agent 的工具(2026-05 I/O 发布,核对 2026-11-05)

循环里「检查这页有没有被改坏」(第六节第 3 步)和四遍体检,可以交给能真开浏览器的 agent。三样东西在 [Chrome at I/O 2026](https://developer.chrome.com/blog/chrome-at-io26)(2026-05-19)里一起发布:

| 工具 | 是什么 | 在本循环里怎么用 |
|---|---|---|
| [Chrome DevTools for agents](https://developer.chrome.com/docs/devtools/agents)(1.0 稳定版,[2026-05-19 博文](https://developer.chrome.com/blog/devtools-for-agents-v1)) | 让编码 agent 用 DevTools 的能力:MCP 服务器、给批量操作用的 CLI、agent skills;能读控制台、网络请求、无障碍树,跑 Lighthouse(含 SEO 和 Agentic Browsing 类别),模拟设备、地点、网速和 CPU,调试 WebMCP 工具,看内存泄漏;可以接管你已登录的浏览器会话(auto-connect) | 每周第 3 步:让 agent 打开赚钱页,跑 Lighthouse 和控制台检查,有回归就停在「推荐一个改动」之前。auto-connect 会把你的登录态交给 agent,只用在测试账号上;对外动作仍要人批准(第六节第 5 步) |
| [Modern Web Guidance](https://developer.chrome.com/docs/modern-web-guidance)(早期预览) | Chrome 团队维护的一组 agent skills,覆盖 100 多个用例,按你选的 Baseline 目标给出能用的新特性和降级写法;`npx modern-web-guidance@latest install` 安装 | agent 起草前端改动时装上,减少它写出过时或不兼容的代码;和 [cwv-playbook.md](../technical/cwv-playbook.md) 一起用:CWV 判据仍以本套件和事实表为准 |
| Gemini in Chrome 的 auto browse | 用户让 Chrome 里的 Gemini 替自己在网页上办事(预约、找有货的商品等);桌面已有,2026-06 起到 Android;桌面端计划和 Gemini Spark 整合 | 这是你网站的**访客**,不是你的工具。赚钱页的表单、结账、预约要能被它走通:按钮是真按钮、表单有 label、关键步骤不靠悬停;WebMCP 在 Chrome 149 起做 origin trial,Gemini in Chrome 将支持(见 [agent-protocols.md](../technical/agent-protocols.md) 第 5 卡) |

本套件口径:这些工具帮 agent「看见」页面,不替代第六节的判定纪律;agent 跑出的 Lighthouse 分数是实验室数据,不是现场数据(见 [cwv-playbook.md](../technical/cwv-playbook.md) 第一节)。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 转化是命名事件 | 在 GA4 的「事件 / 关键事件」里能看到命名事件;API 指标 `sessionKeyEventRate`（见 [kpi-definitions](kpi-definitions.md)） | 事件是工具自动猜的 = 失败，先命名 |
| `state` 按天增量 | `python3 scripts/gsc_api.py query --site sc-domain:example.com --start 2026-10-20 --end 2026-10-20 --dimensions page,query --out state/2026-10-20.csv` | 每个文件只含一天;文件名带日期 |
| 选页三条件同时满足 | `python3 scripts/gsc_mining.py gsc.csv --mode matrix --json` 取 striking distance（排名 5–20、展示 ≥20）;与每页转化数对齐 | 三条件缺一不选;曝光多转化为零的页标「流量陷阱」 |
| 四遍体检的第一遍 | `python3 scripts/site_audit.py URL --json`;`python3 scripts/head_check.py URL` | 无 CRITICAL，head 检查退出码 0 |
| 一次只改一处 | `log` 里每条改动有日期、改动对象、指令版本号 | 同一周有两处以上改动 = 本周结果作废 |
| 判输赢 | 改动前后各取等长窗口（官方至少等满一周的更新窗口之外），点击和转化一起看 | 排名涨转化不涨 = 记没赢 |
| 对外动作卡人工批准 | 检查宿主的权限设置:发布、改线上页面、提交 URL 前必须停下 | 只写在提示词里 = 失败 |

## 来源与证据强度

- 方法来自上述长文全文(读取日期 2026-10-17)。原文是作者自述的工作方式,没有给出任何对照数据,本文件按「实践经验」级别使用;
  其中关于 Google、Ahrefs 的事实性说法在本套件已有一手核实版本,链接见上文各处。
- 与本套件已有内容的查重结论:GSC 口径与数据边界、实验七要素、变更四里程碑、schema 与 llms.txt 的证据、AI 引用平台差异均已存在,
  未重复收录;**新增的是「转化 × 搜索」联合选页、流量陷阱标记、三选一候选结论、agent 三文件与冻结指令纪律、一次一改的周循环判定和四周排期**。
- 第八节来自 Chrome 一手文档,核对 2026-11-05:[Chrome at I/O 2026](https://developer.chrome.com/blog/chrome-at-io26)、[DevTools for agents 1.0](https://developer.chrome.com/blog/devtools-for-agents-v1)、[DevTools for agents 文档](https://developer.chrome.com/docs/devtools/agents)、[Modern Web Guidance](https://developer.chrome.com/docs/modern-web-guidance)。auto browse 的 Android 时间和 Gemini Spark 整合是官方「将要」,未核到上线。
