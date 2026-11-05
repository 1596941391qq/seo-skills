# 人工操作与排名下滑：识别、恢复与负面 SEO 防御(类型学·鉴别诊断·恢复流程·防御)

> 建立于 2026-10-09，2026-10-21 逐条对 Google 官方文档重核，复核于 2026-11-05（补垃圾举报可触发人工操作、生成式 AI 回答适用垃圾政策、第三方 SEO 服务评估）。定位:**人工操作(manual action)与排名下滑的全生命周期处置**——识别(哪类人工操作)→鉴别(人工操作还是算法变化)→恢复(reconsideration / 内容工程)→防御(负面 SEO)。用词按 Google 原话：人工评审给出的叫「人工操作」(manual action)；核心更新、垃圾内容更新和自动系统造成的排名变化叫「算法变化」或「自动降级」，**不叫惩罚，也没有申诉通道**。
> 分工(引用不重复):**时间线对齐与算法归因方法论**见 [seo-drift-monitoring](seo-drift-monitoring.md) 第五节(归因流程)与五层协议 L5;**站群/PBN 案例模式、传染性与 SRA 时间线**见 [site-networks](../research/site-networks.md) 第四节;**disavow 判定门槛**见 [外链画像分析](../research/backlink-profile-analysis.md) 第四节;**规模化内容政策闸门**见 [agent-readiness](../technical/agent-readiness.md) 第 8 节。本文件只写上述文件未覆盖的:手动动作类型全清单、reconsideration 全流程、负面 SEO 防御、恢复期策略与时长汇总。

## 一、人工操作类型学:官方清单

### 1.1 清单口径

- 唯一权威入口:Search Console「Security & Manual Actions → Manual actions」报告，官方说明见[手动操作报告](https://support.google.com/webmasters/answer/9044175)(核对 2026-10-21)。官方定义:人工评审员判定站点页面不符合 Google 垃圾内容政策时，发出人工操作；有人工操作时，站点的部分或全部内容不会出现在搜索结果里。
- 人工操作有邮件通知和 Search Console 消息中心记录;**报告里没有任何条目 = 没有人工操作**(哪怕流量腰斩——那是算法变化或技术问题，见二)。
- **2026 年两条范围变化**（[文档更新记录](https://developers.google.com/search/updates)，核对 2026-11-05）：
  - 2026-05-15 起，垃圾内容政策写明适用于 Google 搜索里的**生成式 AI 回答**：政策开头对 spam 的定义原文包括「attempting to manipulate generative AI responses in Google Search」（[spam policies](https://developers.google.com/search/docs/essentials/spam-policies)，页面日期 2026-08-28）。所以为了让 AI Overviews / AI Mode 提到你而做的操纵（隐藏文本、批量 fan-out 页面、伪造评价等）按同一套政策处理，可能收到同样的人工操作。
  - 2026-04-14 起，Google **可能用垃圾举报直接采取人工操作**；04-23 补充说明。举报页原文：「Google may use your report to take manual action against violations」；发出人工操作时，举报正文会发给被举报站点的所有者，所以含个人身份信息的举报不处理（[举报质量问题](https://developers.google.com/search/help/report-quality-issues)，页面日期 2026-04-23）。含义：竞争对手的举报现在可能直接变成你的人工操作，见 4.1。
- 类型清单会变。截至 2026-10-21 官方清单增补过 **Back button hijacking**(2026-04-13 公告，2026-06-15 起执行，见[公告](https://developers.google.com/search/blog/2026/04/back-button-hijacking))，原「Site reputation abuse」现名 **Site reputation policy**，原「Pure spam」现名 **Major spam problems**。以报告当时的原文为准，不要凭本表判断类型。

### 1.2 官方类型表(截至 2026-10-21)× 识别信号

| # | 报告里的名称 | 官方描述(要点) | 站长侧识别信号 |
|---|---|---|---|
| 1 | **Major spam problems** | 站点似乎使用激进的垃圾手段，如规模化内容滥用(scaled content abuse)、cloaking，或其他反复、严重违反垃圾内容政策的做法 | 报告标 site-wide;`site:` 结果大幅缩水(本套件经验信号，非官方) |
| 2 | **Hidden text and/or keyword stuffing** | 页面含隐藏文本或关键词堆砌 | 全选页面文字或看渲染后的 CSS 才见隐藏内容;词频异常 |
| 3 | **Structured data issue** | 标记了用户看不见的内容、无关或误导内容，或其他操纵行为 | 富结果消失;比对渲染内容与 JSON-LD 字段 |
| 4 | **Unnatural links to your site** | 指向本站的链接呈现不自然、人为、欺骗或操纵的模式(买链、链接方案) | 报告条目;[外链画像分析](../research/backlink-profile-analysis.md) 七因子低分 |
| 5 | **Unnatural links from your site** | 本站的出站链接呈现不自然、人为、操纵的模式 | 出站链接清单里的付费链接、过量互换链接 |
| 6 | **User-generated spam** / **Site abused with third-party spam** | 访客或第三方在论坛、留言簿、个人资料等处提交的垃圾内容；后者只影响含垃圾内容的页面 | 报告通常是 partial;UGC 区段出现大量垃圾文本和外链 |
| 7 | **Spammy free host** | 免费托管服务上有相当比例的站点是垃圾站，可能对整个服务采取人工操作 | 仅托管服务商会遇到 |
| 8 | **Cloaking and/or sneaky redirects**、**Image cloaking**、**Sneaky mobile redirects** | 给用户和 Google 展示不同内容;把用户重定向到与 Google 所见不同的页面;图片对 Google 与访客不同;只对移动用户的欺骗性重定向(常因第三方广告脚本或被黑) | 用 URL Inspection 的「查看抓取页面」对比真实浏览器渲染 |
| 9 | **Thin content with little or no added value** | 低质或浅层页面，官方举例:薄联盟页(thin affiliate)、采集内容或低质量客座文章、doorway 页面 | 整组页面同时掉出索引;内容与源站高度雷同 |
| 10 | **AMP content mismatch** | AMP 页面与对应规范页面内容不一致 | 受影响的 AMP 页不显示，改显示规范页 |
| 11 | **Site reputation policy** | 站点一部分内容与网站声誉政策不一致(第三方内容主要借宿主站已有排名信号发布);EEA 内的处理不同(见 1.3) | 受影响板块流量归零、编辑部内容正常 |
| 12 | **Back button hijacking** | 站点干扰浏览器历史，用户无法用后退键立即回到上一页 | 前端脚本检查 history 操作;第三方广告脚本也会引起 |
| 13 | **Discover / Google News 政策类** | 违反 Discover 与 News 内容政策(如误导内容、危险内容、骚扰等)的人工操作 | 仅影响 Discover / News 的展示 |
| — | **被黑(hacked)** | 不在人工操作报告;在**安全问题(Security issues)**报告里。官方说明:人工操作报告列出人工发现的问题，安全问题报告列出恶意软件和被黑内容 | 浏览器与搜索结果里的警示标签;日志里有异常新增 URL。走安全事件流程，不走本手册第三节的流量路径 |

- **口径纪律**:这张表是识别用速查，不是判定器。判定只认 Search Console 报告原文;「识别信号」列里标「本套件经验信号」的内容用于报告之外的预诊。
- **政策里有、人工操作报告里没有单独条目的**:规模化内容滥用(scaled content abuse)、过期域名滥用(expired domain abuse)。两者 2024-03-05 随 3 月核心更新一起宣布([公告](https://developers.google.com/search/blog/2024/03/core-update-spam-policies))，这两条的说明是:规模化内容滥用「无论内容怎么产生」(自动化、人工或混合)，只要主要目的是操纵排名；过期域名滥用指买下过期域名、主要为操纵排名而改作低价值内容(旧域名做新的、为用户设计的原创站点没问题)。它们可能通过 Major spam problems 或 Thin content 等条目体现。

### 1.3 影响范围:受影响页面模式与 EEA 例外

- 报告展开每条人工操作后，会列出「受影响页面的模式」，例如 `https://example.com/real-estate/*`，或 **Affects all pages**(影响整站)。官方注明:匹配模式的页面不一定全部受影响([来源](https://support.google.com/webmasters/answer/9044175))。范围越窄，要修的面越小。
- **Site reputation policy 的 EEA 例外**(2026-08-28 公告，2026-08-30 起生效，[公告原文](https://developers.google.com/search/blog/2026/08/update-site-reputation-policy)):EEA 以外，该人工操作直接影响受影响板块的搜索结果，站点其余部分不受影响。EEA 以内，人工操作的影响不适用，受影响板块可能被系统单独划出，随时间推移独立排名。站点所有者仍会在 Search Console 收到通知，并可提交 reconsideration；符合条件的站点可在复审后申请调解。

### 1.4 人工操作报告的读取五字段

打开一条记录，按序读五件事，直接决定第三节的处置路径:

| 字段 | 读什么 | 决定什么 |
|---|---|---|
| 类型(Issue type) | 报告里的名称(对照 1.2 表) | 修复动作族(内容类 / 链接类 / 结构化数据类) |
| 受影响页面模式 | 路径模式或 Affects all pages | 修复面 = 全站还是板块 |
| 示例 URL | 官方给的样例 | 只是**样例**:要按「同类页全量」扩展修复面 |
| 通知时间 | 邮件和消息中心的时间 | 与流量下降日交叉验证(2.1) |
| 复审状态 | 「Request review」入口是否可点、是否已有进行中的复审 | 接手存量站时常见「已提交未处理」 |

- **接手存量站的第一课**:先看报告里的**人工操作历史**(官方说明报告会显示历史)。官方在 back button hijacking 与 site reputation 两条里写明:反复违反可能引发进一步的人工操作、影响整站排名。有历史记录的站，把「再犯」当成最高风险项。
- **刚买下的站**:官方说明，如果站点在你接手前违反过政策，先修复，再在复审请求里说明你刚收购了它、现已不再违规。

## 二、算法变化 vs 人工操作:鉴别诊断

> 本节只讲判别框架;时间线对齐五步法、传感器面板、五层协议 L1-L5 **全部沿用** [seo-drift-monitoring](seo-drift-monitoring.md) 第五节与「流量诊断五层协议」,不在此重复。

### 2.1 三证据轴判别

| 证据轴 | 指向人工操作 | 指向算法变化(核心更新、垃圾内容更新、自动降级) |
|---|---|---|
| **Search Console 通知** | Manual actions 报告有条目，邮件和消息中心有通知 | 报告干净(算法变化不发通知) |
| **时间线对齐** | 下降日与 Search Status Dashboard 上的更新窗口不一定对齐；以报告里的通知时间为准 | 下降首日落在更新 rollout 窗口内或紧邻。Google 建议更新结束后至少等满一周再分析，然后拿这一周与更新开始前一周比（[官方](https://developers.google.com/search/updates/core-updates)） |
| **下降形态** | 与违规面同构:影响范围是路径模式就只砸该板块，Affects all pages 就是整站 | 全站或整类页面滑落;同期很多站点一起波动(传感器旁证，见 drift-monitoring) |

### 2.2 两条铁律

1. **先开 GSC 再谈归因**:五层协议 L5 里「人工操作」分支的第一动作就是查人工操作报告——空报告直接把诊断推向算法/技术/竞品三向。
2. **人工操作可以与算法变化叠加**:撤销人工操作 ≠ 排名回归。若同站还有被自动系统降级的质量问题，恢复取决于系统重新评估（见 3.4）。这是「撤销了还不涨」的第一解释，不是「复审失败」。

### 2.3 判别决策树(把三轴串起来)

```
流量/排名显著下滑
├─ 先跑 L1-L4(数据真实性→定位→页面级→技术)——全部净了才进人工操作 / 算法变化分支
├─ GSC Manual actions 报告有条目?
│   ├─ 有 → 人工操作:按类型进三·3.1;叠加检查算法时间线(2.2 铁律 2)
│   └─ 无 → 算法变化 / 竞品 / 需求三分:
│       ├─ 下降首日落在更新窗口(或 end+7 天宽限)→ 算法变化:进三·3.4
│       ├─ impressions 平+clicks 降 → 不是人工操作也不是降级,是 SERP 特性/竞品截流(drift-monitoring 五第 5 步)
│       └─ 无更新对齐、无报告条目、全站滑落 → 未确认波动:按 drift-monitoring 五"结论时点"等 1-2 周,不强行归因
```

- 树的每一层出口都有数据动作,没有"感觉像被罚了"这类出口;诊断不清时执行 drift-monitoring「诊断清单细化」节的 4 步协议(列假设→两利动作→区分性数据→采集计划)。

### 2.4 易混淆情形

- **垃圾内容更新(spam update)vs 人工操作**:垃圾内容更新由自动系统执行，无通知，按更新窗口对齐；人工操作有 Search Console 条目。2026 年的垃圾内容更新有 2026-06-24、2026-08-18、2026-09-24 三次（[Search Status Dashboard](https://status.search.google.com/incidents/XhUDXP7A67iHCD2kmbVu)，时间为太平洋时间）。两类同期出现时，用报告区分。Google 的说法:改正后，自动系统要「数月」才会学到站点已合规；链接垃圾更新（link spam update）之后，被消除的垃圾链接带来的排名收益不会回来（[垃圾内容更新说明](https://developers.google.com/search/updates/spam-updates)）。
- **技术事故**:Search Status Dashboard 记录过一次排名问题：2024-08-15 17:15 至 2024-08-20 04:30（太平洋时间），与 8 月核心更新同期（[事件页](https://status.search.google.com/incidents/42XCLGtpuCZkzqe4dc6S)）。Google 自己的故障也会与更新混淆；对齐自家发布日历(drift-monitoring 五第 3 步)和这个面板后，再下结论。
- **Yandex/百度口径**:Yandex 滤镜(Минусинск 类)与百度低质屏蔽是各自生态的算法性过滤,各市场实况见 [site-networks](../research/site-networks.md) 第三节;滤镜时长没有一手出处,不写数字。

## 三、恢复手册

### 3.1 人工操作:修复 → Reconsideration 全流程

官方步骤见[手动操作报告](https://support.google.com/webmasters/answer/9044175)(核对 2026-10-21)。

1. **定位范围**:读报告里的类型、受影响页面模式、示例 URL，点「Learn more」读该类型的官方修复说明。
2. **修好所有受影响页面**:官方原话意思是，只修一部分页面不会换来部分恢复；有多条人工操作就全部修。链接类先请对方删链或加 nofollow / sponsored，删不掉的再 disavow（门槛见 [外链画像分析](../research/backlink-profile-analysis.md) 第四节）；UGC 类清存量并装治理机制；被黑类先走安全问题流程。
3. **确认 Google 能访问**:受影响页面不能要求登录、不能在付费墙后、不能被 robots.txt 或 noindex 挡住；用 URL Inspection 测试。
4. **防复发**:修复里要含机制（审核队列、noindex、sponsored / ugc 属性、CI 校验）。官方对 back button 与 site reputation 写明:反复违反可能引发进一步的人工操作。
5. **提交**:在报告里点「Request review」。**没修完不提交**。提交后会收到确认邮件；官方要求:出结果前**不要重复提交**。
6. **等待**:官方口径是「通常几天到几周；链接类请求可能比平时更久」。不给更细的数字。结果通过邮件通知。
7. **读结果**:条目消失 = 已撤销；仍有条目、或带新示例 URL = 没通过，回到第 2 步。

**disavow 的官方规则**(来源:[Disavow links](https://support.google.com/webmasters/answer/2648487)，核对 2026-10-21):
- 只有同时满足这两条才用:有相当数量的垃圾、人为或低质量链接指向你，**并且**这些链接已经造成或可能造成人工操作。大多数站点用不到。
- 文件是 UTF-8 或 7 位 ASCII 的 `.txt`;每行一个 URL 或 `domain:` 前缀的域名;不能 disavow 子路径;`#` 开头为注释;单 URL 最长 2,048 字符;最多 100,000 行（含空行和注释行）、2MB。
- 每个属性只有一份名单，新上传会替换旧名单；必须是属性所有者；名单只适用于上传时的那个属性及其子属性；被 disavow 的链接仍显示在 Links 报告里。
- **disavow 工具不支持域名属性（Domain property）**。用域名属性验证的站点要先建一个网址前缀属性。
- 针对「Unnatural links to your site」的复审，官方明说:要真诚尝试先让对方删除；把全部反向链接不加区分地丢进 disavow 文件，不算真诚尝试，可能导致复审被拒。

### 3.2 Reconsideration 文书写什么

官方说一份好的请求做三件事:①说明站点上确切的质量问题；②描述你为修复采取的步骤；③记录修复的结果。链接类还要附上已删除链接的证明，以及无法删除的链接的说明；薄内容类要给出你删除的坏内容和新增的好内容的例子。在此基础上，本套件建议的文书要件（本套件口径）:

1. 违规事实:直接写做了什么（买链就写买链），不甩锅;
2. 修复清单:做了什么、何时做的、覆盖哪些 URL 或板块（全量，不只是样例）;
3. 证据:删除前后对比、disavow 文件和行数、联系站长的记录、截图;
4. 删不掉的:如实说明，已列入 disavow;
5. 防复发机制:审核规则、sponsored 标注流程、监控告警;
6. 结尾:请求重新评审。

**文书骨架(结构参考,内容必须是站点事实)**:

```text
[站点] 关于 [人工操作类型] 的重新审核请求
1. 问题确认:我们在 [范围] 上存在 [违规事实,直陈]
2. 已完成的修复(截至 [日期]):
   - [动作 1]:覆盖 [N 个 URL/板块],证据 [截图/导出附件]
   - [动作 2]:disavow 文件已提交,含 [N] 个域,行级清单见附件
3. 无法完全移除的遗留:[哪些链接删不掉→已 disavow;哪些历史页→已 noindex]
4. 防复发:审核流程/出链标注规范/自动监控已上线([具体机制])
5. 请求重新审核。[联系人]
```

- 长度:两屏内讲完；附件放证据，不把全量清单贴进正文；所写必须属实。

### 3.3 复审没通过之后

- 报告里新出现的示例 URL 就是补修清单:把新样例并进修复面，修完后再提交。
- 提交之前先等上一次的结果，不要重复提交（官方）。
- 多次没通过，且类型是 Major spam problems 或 Thin content:评估「重建还是继续修」（本套件口径，见 6.2）。

### 3.4 算法变化:没有申诉通道

- 核心更新、垃圾内容更新和其他自动系统造成的排名变化，**没有 reconsideration 路径**。Google 对核心更新的说法（[原文](https://developers.google.com/search/updates/core-updates)）:核心更新范围广，「不针对特定站点或单个网页」；掉到后面的页面「不一定不好」，只是有别的页面更适合。
- 改进之后:「有些改变几天内生效，但系统要几个月才能学习并确认站点整体长期提供有用、可靠、以人为本的内容。如果几个月后仍无效果，可能意味着要等下一次核心更新」；同时 Google 一直在做不公布的小型核心更新，也可能让内容的排名回升。
- 官方提醒:不要做「quick fix」式改动（比如因为听说某个页面元素对 SEO 不好就删掉）；只在内容无法挽救时才考虑删除。
- 2024-03 起，Google 把有用性的判断并入核心排名系统（不再是单一信号或系统，[公告](https://developers.google.com/search/blog/2024/03/core-update-spam-policies)）。
- 更新历史看 [Search Status Dashboard](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history)，不要靠印象估次数。
- 没有「加速恢复」的手段;承诺加速的服务都不可信。

### 3.5 内容质量工程(算法变化后的实质工作)

1. **量裁**:按 Search Console 的 query / page 分层，找出跌得最多的页面族（方法沿用 drift-monitoring 五第 5 步）。
2. **逐页处置**:改（补第一手经验、数据、作者信息；刷新方法见 [content-refresh-playbook](../content/content-refresh-playbook.md)）→ 并（301 进更强的同类页）→ 删（noindex 或 410）。官方态度:删除是最后手段。
3. **闸门**:批量产出的页面族过 [agent-readiness](../technical/agent-readiness.md) 第 8 节的闸门（本套件口径）。
4. **可信信号载体**:作者页、审稿说明、可验证的一手证据。
5. **完成度**:看删并改之后剩余页面族的质量，不看「改了多少页」；用 [kpi-definitions](kpi-definitions.md) 的分层口径盯前导指标（展示通常先于点击回暖，本套件经验）。

## 四、负面 SEO 防御

### 4.1 威胁面重估(官方口径)

- Google 在 disavow 说明里写:「Google 努力确保第三方站点上的行为不会对网站产生负面影响」「大多数情况下，Google 能判断哪些链接可信，所以大多数站点不需要用这个工具」（[Disavow links](https://support.google.com/webmasters/answer/2648487)）。人工操作报告页也写:「我们的算法很擅长发现垃圾内容，多数情况下会自动发现并从结果中移除」。
- 所以纯外链攻击先**监控，不先动手**。真正需要防的是:被黑（走 Security issues 报告）、持续的外链攻击（已出现 Unnatural links 人工操作才用 disavow）、内容剽窃、表单与评论垃圾。
- disavow 判据见 [外链画像分析](../research/backlink-profile-analysis.md) 第四节;官方两条门槛见 3.1。本节只讲防御动作。
- **举报风险（2026-04 起）**:垃圾举报可能直接触发人工操作（见 1.1）。别人举报不需要你的同意,也不需要证明自己是竞争对手。防线只有一条:站内没有真违规。逐项自查 1.2 的类型,尤其是自己能控制的（隐藏文本、结构化数据标记看不见的内容、付费链接、UGC 垃圾、后退键劫持、给 AI 回答做的操纵）。收到人工操作后,报告里附的举报原文能帮你定位问题,按 3.1 修复后复审,不要和举报方纠缠。
- **第三方 SEO / AEO / GEO 服务**:Google 2026-06-05 发布评估指引([third-party-seo](https://developers.google.com/search/docs/fundamentals/third-party-seo),核对 2026-11-05):Google 不评估第三方服务,对自称做法被 Google「接受」或「认可」的说法要警惕;第三方工具拿不到 Google 内部排名数据,不能保证效果,预测是工具自己的。外包方做出违规手法,人工操作落在你的站上。签约前和交付时按 [report-templates.md](report-templates.md) 检查清单「工具或服务声称 Google 认可」一项核对。

### 4.2 外链攻击识别与响应

- **识别**:外链档案突增（周环比异常）+ 锚文本集中在敏感词或精确匹配;用 [link-quality-rubric](link-quality-rubric.md) 走待复核流程，**先记录观察，不急批量 disavow**（阈值由你自己的历史基线定，本套件口径）。
- **响应梯度**:被动出现 → 只监控；持续攻击且排名有可见影响 → 导出人工核实 → 能删先删 → 删不掉才 disavow，并写台账；收到「Unnatural links to your site」人工操作 → 按 3.1，disavow 此时是流程的一部分。
- **自伤风险**:误杀真实链接的 disavow 比攻击本身更伤排名——写 `domain:` 前先确认该域没有正常链接。disavow 不支持域名属性（见 3.1）。

### 4.3 内容剽窃

- 预防:发布后尽快让 Google 抓到——sitemap（`lastmod` 如实填）加 Search Console 的网址检查。IndexNow 只对参与的搜索引擎有效，官方参与列表里有 Bing、Yandex、Naver、Seznam、Amazon、Yep，**没有 Google**（[IndexNow FAQ](https://www.indexnow.org/faq)，核对 2026-10-21）。页面自引用 canonical。
- 处置:采集站排名超过原站时，用 Google 的[法律移除表单](https://support.google.com/legal/answer/3110420)（版权投诉）；表单要求填具体 URL，并说明哪部分内容、为什么违规;Google 只能限制自家产品里的访问，内容仍可能在别处存在，所以也要联系站长。

### 4.4 伪造爬虫与爬虫攻击

- 伪装 Googlebot 的恶意爬虫:按官方方法验证（[Verify Google requests](https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests)，核对 2026-10-21）:①对日志里的 IP 做反向 DNS（`host <ip>`）；②确认域名是 `googlebot.com`、`google.com` 或 `googleusercontent.com`；③对该域名做正向 DNS；④确认解析回原 IP。大批量用官方发布的 IP 范围 JSON 比对（common-crawlers.json 等）。假 bot 在 CDN 或 WAF 层限速或拦截。
- 恶意高并发打爆服务器造成 5xx → 索引受损:这是技术事件，走 drift-monitoring L4，不是人工操作或算法降级。

### 4.5 垃圾提交与评论(UGC 防线)

按官方[防止用户生成垃圾](https://developers.google.com/search/docs/monitor-debug/prevent-abuse)（核对 2026-10-21）:
- 发布并告知清晰的滥用政策，允许可信用户举报垃圾内容；
- 记录注册行为，找垃圾模式（填表耗时、同一 IP 段的请求数、注册时的 user agent、用户名模式）；
- 对没有信誉的新用户的帖子加 `noindex`，有信誉后再放开索引；
- 不可信内容里的链接加 `rel="ugc"` 或 `nofollow`（[官方说明](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)：UGC 链接推荐用 ugc）；
- 可疑互动走人工审核；用封禁名单；注册表单加 reCAPTCHA 一类验证；
- 监控重定向、大量广告区块、垃圾关键词、大段编码 JS，用 `site:` 搜索和日志中的流量尖峰找问题。
- 商家档案的虚假评论轰炸属平台侧攻击（GBP 口径），与搜索处置分开；**本地排名监控**用 [local-grid-ranking](local-grid-ranking.md) 的格点基线做前后对照。

### 4.6 防御基线(季度例行)

1. GSC 手动动作+安全报告巡检(零成本,最高优先);
2. 外链档案增量 diff(攻击尖峰的前导观测);
3. 反向 DNS 的 bot 日志抽查;4. 核心页面 `site:`/索引数抽测。基线快照先行的整套机制见 [seo-drift-monitoring](seo-drift-monitoring.md)(baseline/compare)。

### 4.7 攻击事件响应台账

确认或疑似攻击时,建一张台账(挂外链审计附录,载体同 [site-networks](../research/site-networks.md) 6.4 交付物口径):

| 字段 | 说明 |
|---|---|
| 检测日/首见日 | 攻击尖峰的最早观测(回溯增量 diff) |
| 攻击形态 | 外链突增/锚文本轰炸/采集站克隆/假 bot/表单灌水 |
| 规模与源 | 新增 referring domains 数、锚文本分布、源站/网段指纹 |
| 排名影响 | 攻击窗口前后 GSC 分层对比(impressions/position,不是 clicks) |
| 处置与日期 | 记录观察/takedown 发函/disavow 提交(何日、哪些域) |
| 复查日 | disavow 半衰期纪律:提交后按月回看,引用前复核 |

- 台账的两个用途:给 3.2 的 reconsideration 文书供证据(受攻击+已处置的完整链);给客户演示"记录和观察"不是不作为,是避免误杀的正确动作。

## 五、恢复期 SEO 策略(受影响期间做什么/不做什么)

### 5.1 该做

- **假设先行**:先写单句假设模板("[Property] lost [X] starting [date] because [cause]…",模板沿用 drift-monitoring「五层协议」节),所有动作挂在假设下;
- **修复期内照常发布质量合格的内容**（本套件建议；Google 没有说停更会被扣分）;
- **技术面维持满分**:索引健康/CWV/结构化数据照常监控(恢复期最容易因疏忽引入二次技术损失);
- **渠道对冲**:邮件/社交/付费补搜索流量缺口,按 6.1 的预期区间给预算(恢复期 = 搜索获客受限期;Google 不公布恢复时长,按本站数据估,本套件口径);
- **全量留痕**:每一步修复的 before/after——既是 reconsideration 材料(3.2)也是复盘资产;
- **盯前导指标**:impressions 回暖早于 clicks(kpi 分层口径),别用单一 clicks 曲线判生死。

### 5.2 不该做

- **不慌着换域名**:只有 Major spam problems 级、多轮复审仍无法撤销时才考虑（本套件口径）(且受罚域严禁 301 进新域,传染口径见 [site-networks](../research/site-networks.md) 6.3-D);
- **不批量删内容「表决心」**:官方称删除是最后手段（见 3.4）;改并删走 3.5 的逐页处置;
- **不买链接救排名**:收到链接类人工操作后再买链=给下一轮复审递证据;
- **不空提/重复提交 reconsideration**(3.3);
- **不无差别 disavow**(4.2);
- **不轻信「加速恢复」服务**——算法变化没有申诉和催办通道(3.4)。

### 5.3 沟通与预期管理

- 对内交付用 drift-monitoring「诊断清单细化」节的七段模板(What happened/Why/做什么/何时恢复+置信度/盯什么);恢复时长按 6.1 给官方区间，不给点值;
- 明确一句:**人工操作撤销、算法重新评估与排名回归是三个不同的事件**。撤销后，自动系统的评估仍要时间，这是客户预期错位的高发点(2.2 铁律 2)。

### 5.4 恢复期节奏表(30/60/90 天，本套件口径，不是 Google 的时间表)

| 阶段 | 动作重心 | 里程碑判据 |
|---|---|---|
| 第 1-30 天 | 定性(二)+全量修复启动(手动类)/内容量裁(算法类);建立基线快照与分层监控 | 假设单句定稿;修复面清单冻结;(手动类)修复完成≥50% |
| 第 31-60 天 | 修复收尾+机制上线;(手动类)提交 reconsideration;算法类持续删并改 | 申诉在途/内容工程主要批次完成;前导指标止跌 |
| 第 61-90 天 | 等待期运营:按 5.1 维持发布与技术面;渠道对冲满负荷 | (手动类)收到 Revoked 或新样例;(算法类)主要修复完成，开始观察 |

- 表以「定性完成日」为 T0。官方说算法变化的效果可能要几个月（3.4），90 天没回暖不等于失败；对照 6.1 的场景行，不对照日历。

## 六、场景 × 处置 × 预期时长

### 6.1 场景汇总表

下表时长列只写**官方原话**；官方没给数的，标「无官方数字」，不写没有出处的周数。

| 场景 | 主处置路径 | 官方说法 | 备注 |
|---|---|---|---|
| 被黑注入垃圾页 | 清理并修复漏洞 → 安全问题报告里申请复审 | 走 Security issues 流程，不在人工操作报告 | 见[被黑站点说明](https://web.dev/explore/secure#help!-i've-been-hacked) |
| 用户生成垃圾 / 第三方垃圾 | 清存量 + 治理机制 + Request review | 复审「通常几天到几周」 | 受影响的通常只是含垃圾的页面 |
| Unnatural links to your site | 请对方删链 → 删不掉的 disavow → 附文档 Request review | 链接类请求「可能比平时更久」；无官方数字 | 站群 / PBN 联坐的处置见 [site-networks](../research/site-networks.md) 第四节 |
| Major spam problems / 规模化内容滥用 | 更新站点使其符合垃圾内容政策 → Request review | 复审「通常几天到几周」；无官方数字 | 本套件闸门见 agent-readiness 第 8 节 |
| Site reputation policy | 把内容迁到新域名并 nofollow 链接、noindex、改成第一方内容或移除 | 官方警告:迁到子域名 / 子目录可能被视为规避政策 | EEA 内不适用人工操作影响，见 1.3 |
| Thin content | 提升价值，附删除的坏内容与新增的好内容示例 | 同上 | |
| 核心更新后的下滑 | 内容质量工程（3.5）；没有申诉 | 「可能要几个月」「可能要等下一次核心更新」 | [官方](https://developers.google.com/search/updates/core-updates) |
| 垃圾内容更新后的下滑 | 修复违规面；没有申诉 | 自动系统「要几个月」才学到站点已合规；链接垃圾更新后被消除的链接收益不会回来 | [官方](https://developers.google.com/search/updates/spam-updates) |

- 本表不是 SLA，是预期管理工具；所有时长从「修复完成」起算。

### 6.2 模式规律(本套件经验，用于决策)

1. **修复面决定难度**:影响范围窄（路径模式、partial）的比整站的好处理，因为要验证的修复面小。
2. **叠加是常态**:人工操作撤销加自动降级遗留，是最长的恢复线。
3. **算法变化后的杠杆是修复本身**:掉出核心更新后，先量裁再改，不去猜下一次更新的日期。看 [seo-drift-monitoring](seo-drift-monitoring.md) 五的更新数据文件。
4. **Yandex / 百度不在本表**:各自生态的说明见 [site-networks](../research/site-networks.md) 第三节。

### 6.3 时长数据的使用纪律

- 引用时标明档位:官方原话、第三方转述、行业经验值三档，不混写。本文只用官方档。
- 幸存者偏差:能写成案例的多是修好了的站；对客户沟通时给区间，不给点值。
- 两个站的恢复周期只有在修复完成度、影响范围、是否叠加自动降级三项一致时才可比。

## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 有没有人工操作 | Search Console → Security & Manual Actions → Manual actions；读五字段（1.4） | 报告显示绿色对勾 = 无;有条目 = 按类型进 3.1 |
| 有没有安全问题 | 同菜单 → Security issues | 有条目 = 走安全事件流程，先清理再申请复审 |
| 下降是否对齐更新 | 在 [Search Status Dashboard](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history) 记下更新的开始 / 结束日；等结束后满一周，对比这一周与更新开始前一周 | 下降首日落在窗口内 = 按算法变化处理（3.4）;不对齐且无条目 = 先排查技术与需求 |
| 修复面是否覆盖所有受影响页面 | 用示例 URL 外推同类页，抽样检查；`python3 scripts/site_crawl.py --help` 先确认爬取参数 | 样例之外仍有同类问题 = 未修完，不提交 |
| 链接类：名单格式 | disavow 文件逐项核对 3.1 的格式规则（`.txt`、UTF-8 / ASCII、`domain:`、≤100,000 行、≤2MB）；确认属性类型不是域名属性 | 全部满足才上传 |
| Googlebot 真伪 | `host <ip>` → 域名是否为 googlebot.com / google.com / googleusercontent.com → 再 `host <域名>` 回到同一 IP | 回不到原 IP = 伪造 |
| 复审材料 | 对照 3.2 的三件事与链接类附加项 | 缺任一项不提交 |
| 被举报风险（2026-04 起） | 按 1.2 类型表自查自己能控制的项；为 AI 回答做的手法按 [geo-evidence.md](../content/geo-evidence.md)「GEO 手法风险线」逐项过 | 任一项落在「越线」= 先改，不等举报 |

## 附:核验口径

- 2026-10-21 起逐条对 Google 官方文档重核:[手动操作报告](https://support.google.com/webmasters/answer/9044175)、[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies)（页面更新日 2026-08-28）、[核心更新](https://developers.google.com/search/updates/core-updates)、[垃圾内容更新](https://developers.google.com/search/updates/spam-updates)、[Disavow links](https://support.google.com/webmasters/answer/2648487)、[2024-03 公告](https://developers.google.com/search/blog/2024/03/core-update-spam-policies)、[2026-08 站点声誉政策更新](https://developers.google.com/search/blog/2026/08/update-site-reputation-policy)、[2026-04 back button hijacking](https://developers.google.com/search/blog/2026/04/back-button-hijacking)。2026-11-05 补核:[举报质量问题](https://developers.google.com/search/help/report-quality-issues)、[第三方 SEO 指引](https://developers.google.com/search/docs/fundamentals/third-party-seo)、[文档更新记录](https://developers.google.com/search/updates) 的 2026-04-14、04-23、05-15、06-05 条目。
- 上一版里来自第三方机构（SEJ、PPC Land、seoinbounds、SISL、Bruce Clay、Coalition 等）的时长、周数和「行业经验值」没有一手出处，已删除，不再作为口径。
- 站群、PBN、EEA 之外的站点声誉细节、disavow 的两条官方适用条件等沿用各源文件的核验结论（[site-networks](../research/site-networks.md)、[外链画像分析](../research/backlink-profile-analysis.md)），本文件未重复核。
- 官方政策每季度可能变化，引用前复查「核对日期」。
