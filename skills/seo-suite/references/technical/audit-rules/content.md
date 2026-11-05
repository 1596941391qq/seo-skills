# 审计规则目录 · Content

> 从 [audit-rule-catalog.md](../audit-rule-catalog.md) 拆出(2026-10-21),正文原样搬运,只改了相对链接路径。来源、计分口径、ID 纪律、执行速查(`AUDIT`/`CRAWL` 等简写与 J1–J8、G1–G7 片段)和扩写进度见索引页。

### Content(27 条,权重 5%)

词数 **≥300 过/100-299 警/<100 败**(原版建议标准页 500+、文章 1000+,Google 没有字数要求);Flesch-Kincaid **60-70** 最优(源表说法,`content-reading-level`);关键词堆砌=warn;标题层级不跳(H1→H3=invalid,warn/fail);**标题 <10 字符或 >70 字符=warn**(`content-heading-length`;旧快照写 3/100,已作废);页内标题重复=warn;text/HTML 比=warn/fail;title 与 H1 相同=warn;**title 像素宽 ≤~580px、description ≤~920px**(工具约定;Google 无固定上限,按设备宽度截断);title=description 全同=warn;meta 在 body 里=fail;MIME=warn/fail;**crawl 专属**:duplicate-description/duplicate-exact(=fail)/duplicate-near/duplicate-h1(跨页同 H1)/thin-vs-site(**<同类页中位词数一半=警**,需 ≥4 个同类页)/title-pattern(标题未带全站 ≥60% 使用的后缀=警);`content-mojibake`(UTF-8 被按 Latin-1/Windows-1252 解码,如 `â€™`=fail);`content-unrendered-markup`(code/pre 外的字面 Markdown `**bold**`=warn);`content-placeholder-text`(**`{{ }}`/`{% %}`/`<% %>`/`[object Object]`=fail;TODO:/FIXME:=warn**;`content-stale-copyright`(页脚版权年落后当年=warn,区间取末年);`content-date-agreement`(datePublished/time datetime//20xx/ 路径三年份不一致=warn,dateModified 不比);`content-hidden-text`(**≥80 字符**被内联样式隐藏(display:none/visibility:hidden/font-size:0/大负 text-indent/opacity:0)=warn,nav/对话框/sr-only 豁免,仅样式表隐藏不判);`content-broken-html`/`content-meta-in-body`。

**解释层(15 条;ID 未公布原文,标 [待核])**

#### content-duplicate-exact ⛏
- 源表:fail · 权重 8 · 需 `--crawl`。另一已爬页的可见文本与本页完全相同。工具约定。建议优先级 high。
**依据**: 站内重复内容"not a violation of our spam policies",也不会招致人工处置;代价是体验差、浪费抓取,Google 会自行聚类并选规范页([SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide);[规范化文档](https://developers.google.com/search/docs/crawling-indexing/canonicalization))。"数千页触发质量算法"无出处,已删。核对 2026-10-18。
**判据**: 通过=无可见文本完全相同的可索引页对。失败=存在(联合发布、合法转载用伙伴侧 noindex 处理)。
**执行**: site_audit 不跨页;套件里 `traffic_funnel.py --audit audit.json` 只按 title+description 的 Simhash 聚类,不比正文。正文完全重复手工查:`while read u; do echo "$(curl -s "$u" | sed 's/<[^>]*>/ /g' | tr -s '[:space:]' ' ' | shasum | cut -c1-12) $u"; done < urls.txt | sort | awk '{n[$1]++; l[$1]=l[$1]" "$2} END{for(k in n) if(n[k]>1) print k":"l[k]}'`。
**修复**: 真重复用 canonical 或 301 合并;打印版加 canonical;采集页重写或下线。
**关联**: core-canonical-conflicting、content-duplicate-near;[scoring-rubric.md](../scoring-rubric.md)

#### content-duplicate-near ⛏
- 源表:warn/fail · 权重 7 · 需 `--crawl`。主内容高度相似;相似度算法与阈值源表未公布。工具约定。建议优先级 medium。
**依据**: 同上:Google 会把主内容相似的页聚类,只选一个作规范页,重复页抓取频率降低([规范化文档](https://developers.google.com/search/docs/crawling-indexing/canonicalization))。真正的风险在规模化零增量模板,那属于"规模化内容滥用"的审查范围([垃圾政策](https://developers.google.com/search/docs/essentials/spam-policies))。核对 2026-10-18。
**判据**: 通过=同类页各有实质差异(本地数据、案例、评价)。失败=只换城市名/型号的模板页成批出现。
**执行**: 无现成正文相似度脚本。先用上条命令排除完全重复,再人工抽样对比同模板页;程序化页过 [programmatic-seo-gates.md](../programmatic-seo-gates.md) 的门槛。
**修复**: 增量本地化;或合并为强页加 canonical。
**关联**: content-duplicate-exact;[programmatic-seo-gates.md](../programmatic-seo-gates.md)

#### content-duplicate-description ⛏
- 源表:warn/fail · 权重 5。重复或不足 50 字符的 description=warn(需 `--crawl`);缺失=fail(任何审计;site_audit 对缺 description 记 WARN,因为 Google 不要求必须有)。工具约定。建议优先级 low。
**依据**: 全站相同或相似的 description 对用户没有帮助;无暇逐页写时先保核心页,大站可程序化生成([snippet 文档](https://developers.google.com/search/docs/appearance/snippet))。description 不是排名因素。核对 2026-10-18。
**判据**: 通过=可索引页 description 各不相同。失败=模板级重复(零星几页可排后)。
**执行**: `while read u; do curl -s "$u" | grep -oiE '<meta[^>]+name=.?description[^>]*>'; done < urls.txt | sort | uniq -c | sort -rn | awk '$1>1'`。
**修复**: 模板用真实字段变量拼装;无字段的页宁可不写,让 Google 从正文取摘要。
**关联**: core-title-unique、core-description-present

#### content-duplicate-h1 ⛏
- 源表:warn · 权重 5 · 需 `--crawl`。本页 h1 与另一已爬页完全相同;无 h1 报 not measured。工具约定。建议优先级 low。
**依据**: 无搜索引擎专门规定;Google 会参考 h1 生成 title link([title link 文档](https://developers.google.com/search/docs/appearance/title-link)),h1 重复常与 title 重复、近似内容同时出现,是模板失控的症状。核对 2026-10-18。
**判据**: 通过=可索引页 h1 各不相同(分页序列共享 h1 属预期)。失败=不同主题页用同一 h1。
**执行**: `while read u; do curl -s "$u" | grep -oiE '<h1[^>]*>[^<]*' | sed -E 's/<h1[^>]*>//'; done < urls.txt | sort | uniq -c | awk '$1>1'`。
**修复**: h1 带页面级变量;真重复页合并。
**关联**: core-h1-present、content-duplicate-exact

#### content-word-count
- 名称/类型: 词数 —— warning · 优先级 low · 输出 WARN(100-299)/CRITICAL(<100)(源表:≥300 过/100-299 警/<100 败;文章建议 500+,长文 1000+)
**这意味(what)**: 页面主内容词数不足:100-299 词 warn,<100 词 fail 档(文章类建议 500+、长文 1000+ 为参考线不扣分[待核])。
**为什么(why)**: Google 说它没有偏好的字数("Are you writing to a particular word count because you've heard or read that Google has a preferred word count? (No, we don't.)",[有用内容文档](https://developers.google.com/search/docs/fundamentals/creating-helpful-content),核对 2026-10-21)。词数只是"页面有没有内容"的粗代理:<100 词几乎必然是空壳/占位/极薄页,才配 fail 档;site_audit 的词数线是 <200 记 `[WARN] content`(本套件口径,另按 CJK/泰文/天城文感知计数)。质量口径见 [scoring-rubric.md](../scoring-rubric.md) "不作为扣分依据"——**不要机械灌字数到 300**。
**触发(trigger)**: 主内容区(剥导航/页脚/广告)文本词数:<100 → fail 档;100-299 → warn;≥300 过。站内实跑用 `AUDIT URL`(<200 词 warn,不剥导航,仅剥 script/style)。
**不修的条件(caveat)**: 词数不(直接)影响 SEO,然而它是薄内容检测的第一道症状指标,所以一般建议主内容 ≥300 词。但联系页/工具页/表单页天然短,按页面类型豁免。
**修复(fix)**: 薄页补实质内容(回答/示例/数据)或并入父页;程序化薄页过 [programmatic-seo-gates.md](../programmatic-seo-gates.md) 门槛;别注水。
**关联(seealso)**: content-keyword-stuffing、content-duplicate-near;[scoring-rubric.md](../scoring-rubric.md)

#### content-keyword-stuffing
- 名称/类型: 关键词堆砌 —— issue · 优先级 high · 输出 WARN(源表现行 warn、权重 5;密度阈值源表未公布)
**这意味(what)**: 页面文本/alt/meta 里同一关键词的密度与重复超出自然语言频率。
**为什么(why)**: 关键词堆砌违反 Google 垃圾政策,例子包括罗列要排名的城市和地区、不自然地重复同一词组([垃圾政策](https://developers.google.com/search/docs/essentials/spam-policies),核对 2026-10-21)。工具判定的密度阈值未公布,命中只作人工复查线索。
**触发(trigger)**: 主文本关键词密度+n-gram 不自然重复检测(密度阈值[待核]);meta/alt 内同词根堆叠另计。
**不修的条件(caveat)**: 没有公认的安全密度魔法数,机器判堆砌误报不低,所以一般建议命中后人工复查再动文案。但主题集中的专题页关键词命中率高是自然结果,别一见重复就删。
**修复(fix)**: 用同义词/实体变体分散表达;每段回答一个问题;alt/title 里的堆叠优先清。
**关联(seealso)**: content-hidden-text、content-word-count;[scoring-rubric.md](../scoring-rubric.md)

#### content-heading-family [待核 ID]
- 名称/类型: 标题结构家族(源表 ID `content-heading-hierarchy`、`content-heading-length`、`content-heading-unique`) —— warning · 优先级 low · 输出 WARN(源表现行:层级跳级 H1→H3=invalid;标题 <10 字符或 >70 字符=warn;页内标题重复=warn)
**这意味(what)**: 页内标题树有问题:层级跳级(H1 直接 H3)、标题过短(<10 字符)或过长(>70 字符)、同页重复标题文本。
**为什么(why)**: Google 说标题的数量与顺序对搜索没有影响("Number and order of headings",[SEO 入门指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide),核对 2026-10-21);层级对屏幕阅读器导航有用,Bing 另要求层级有逻辑。这一族是无障碍与内容结构项,不是 Google 排名规则。site_audit 的对应项:`[WARN] headings: 跳级 hN→hM`;第一个 h1 之前就出现 h3–h6(前面没有上一级)报 `[WARN] headings: hN 出现在第一个 h1 之前`(W3C WAI Headings 教程允许 h1 前有 h2 级结构标题,所以 h2 起头不报)。标题长度 <10/>70 字符、同页重复标题是 SEOmator 工具约定,site_audit 不跑(只在文档)。
**触发(trigger)**: 1) 相邻标题级别差 >1 即 invalid;2) 标题文本 <10 或 >70 字符即警(源表现行);3) 同页两标题文本相同即 warn。
**不修的条件(caveat)**: 标题结构不(直接)影响排名,然而影响无障碍与 AI 摘要的章节切分,所以一般建议树形规范。但设计系统组件自带级别(卡片 H3 出现在 H1 区)造成的"跳级"是工程取舍,可按组件规则豁免。
**修复(fix)**: 模板按语义排 H1→H2→H3;标题写"这节说什么";组件标题级别参数化。
**关联(seealso)**: core-h1-present、content-agreement;[semantic-html.md](../semantic-html.md)

#### content-agreement [待核 ID]
- 名称/类型: 元素一致性家族(源表 ID `content-title-same-as-h1`、`content-title-same-as-description`、`content-date-agreement`,像素宽度线 `content-title-pixel-width`/`content-description-pixel-width`) —— warning · 优先级 low · 输出 WARN(源表:title 与 H1 相同=warn;title=description 全同=warn;content-date-agreement 三年份不一致=warn,dateModified 不比)
**这意味(what)**: 本该各司其职的信号互相雷同或矛盾:title 与 H1 完全相同;title 与 description 全同;页面三处年份(datePublished/`<time>` datetime/路径 /20xx/)互不一致。
**为什么(why)**: title 是 SERP 行、H1 是页内主题、description 是摘要候选——雷同等于放弃两层独立表达;年份不一致则对引擎发出矛盾的新鲜度信号。dateModified 不参与比对(更新时间晚于发布是常态)。均为轻档:单页雷同无实质影响,批量模板雷同才是病。
**触发(trigger)**: 1) 归一化后 title==H1 即 warn;2) title==description 即 warn;3) 三处年份取值 ≥2 个不同即 warn。
**不修的条件(caveat)**: 一致性家族不影响排名,然而各自放弃一层表达面,所以一般建议差异化:title 带品牌与意图、H1 是主题、description 是行动点。但品牌极简页(title=H1=品牌名)可豁免。
**修复(fix)**: 三字段分模板变量;日期单一来源(CMS updated_at)注入全部位置;像素口径(title ≤~580px/description ≤~920px)见本节表。
**关联(seealso)**: core-title-present、core-h1-present、content-heading-family;[head-elements.md](../head-elements.md)

#### content-hidden-text
- 名称/类型: 隐藏文本 —— issue · 优先级 high · 输出 WARN(源表 warn;≥80 字符被内联样式隐藏)
**这意味(what)**: ≥80 字符的文本被**内联样式**隐藏(display:none/visibility:hidden/font-size:0/大负 text-indent/opacity:0)。
**为什么(why)**: 为操纵排名而隐藏文本违反 Google 垃圾政策(字号或透明度设 0、移出屏幕等);折叠、选项卡等动态显示内容不违规([垃圾政策](https://developers.google.com/search/docs/essentials/spam-policies))。源表三个精准边界:只判内联样式(样式表隐藏可能是响应式规则,不判);≥80 字符(短文本隐藏多为 UI 状态);nav/对话框/sr-only 豁免(sr-only 是无障碍正确做法)。
**触发(trigger)**: 1) 元素内联样式含隐藏属性;2) 文本 ≥80 字符;3) 非豁免区即 warn。
**不修的条件(caveat)**: 隐藏本身不是罪(SR-only 文本、折叠 UI 都正当),然而"隐藏+长文本+关键词"的组合接近操纵形态,所以一般建议命中后人工判意图。但 A/B 测试的隐藏变体属实验基建,标注豁免。
**修复(fix)**: 该给用户看的就显示;折叠交互用 details/dialog 语义元素;sr-only 保留(豁免)。
**关联(seealso)**: content-keyword-stuffing;[semantic-html.md](../semantic-html.md)

#### content-deploy-hygiene [待核 ID]
- 名称/类型: 部署卫生家族(源表 ID `content-placeholder-text`、`content-mojibake`、`content-unrendered-markup`、`content-stale-copyright`) —— issue · 优先级 high · 输出 CRITICAL/WARN(源表:占位符 {{ }}/{% %}/<% %>/[object Object]=fail,TODO:/FIXME:=warn;mojibake=fail;code/pre 外字面 Markdown=warn;页脚版权年落后=warn,区间取末年)
**这意味(what)**: 渲染管道事故漏进生产:未渲染占位符(fail 档)、TODO:/FIXME: 残留(warn)、乱码 mojibake——UTF-8 被按 Latin-1/Windows-1252 解码,如 `â€™`(fail 档)、code/pre 外的字面 Markdown `**bold**`(warn)、页脚版权年落后当年(warn,年份区间取末年)。
**为什么(why)**: 每项都是"管道坏了"的直接证据:占位符=模板引擎没跑或变量没注入;乱码=编码声明与实际字节不符;字面 Markdown=静态生成器漏处理。对用户是可见破损(信任度),对引擎是无意义文本;fail 档两项意味着页面实质坏死。
**触发(trigger)**: 正则扫主内容:占位符模式 → fail 档;TODO:/FIXME: → warn;mojibake 特征序列(â€™/Ã© 族)→ fail;code/pre 外 `**…**`/行首 # → warn;版权年 < 当年 → warn。
**不修的条件(caveat)**: 家族命中基本无豁免(生产页不该有模板残渣);唯一注意是展示模板语法的教程/文档页命中属误报,按白名单排除。
**修复(fix)**: CI 加渲染产物断言(无占位符/无 mojibake);charset 声明与实际编码统一为 UTF-8;版权年由服务器时间动态输出。
**关联(seealso)**: content-word-count、sd-json-syntax(同为"静默失效"家族);[validation-guide.md](../validation-guide.md)

#### content-text-html-ratio
- 名称/类型: 文本/HTML 比 —— warning · 优先级 low · 输出 WARN/CRITICAL(源表现行 warn/fail、权重 7;阈值源表未公布)
**这意味(what)**: 页面可见文本量与 HTML 标记量的比值过低。
**为什么(why)**: 低比值是"标记-heavy"的粗代理:内联样式/深层嵌套容器/隐藏 DOM 把标记撑大,正文被稀释——引擎要剥壳取肉,移动端要为壳付流量。它从来不是排名因素,是内容密度的症状指标;真正的病(多余嵌套/内联属性)由它暴露。
**触发(trigger)**: 渲染后可见文本字符数 ÷ HTML 总字符数,低于阈值即 warn(具体比值[待核:源表未公布])。
**不修的条件(caveat)**: 比值不(直接)影响 SEO(代码展示页文本密集、应用页标记密集,天然波动),然而它是标记债的症状,所以一般建议命中后查嵌套与内联属性而非灌字。但 SPA 壳页低比值是形态属性,配 SSR 后再看。
**修复(fix)**: 内联样式剥离到样式表;组件嵌套扁平化;隐藏 DOM 按需挂载;SSR 输出真实内容。
**关联(seealso)**: perf-dom-size、content-word-count;[scoring-rubric.md](../scoring-rubric.md)

#### content-readability
- 名称/类型: 可读性(源表 ID `content-reading-level`) —— warning · 优先级 low · 输出 WARN(源表 warn;Flesch-Kincaid **60-70** 最优)
**这意味(what)**: 正文可读性得分偏离 60-70 建议区(Flesch-Kincaid 口径)。
**为什么(why)**: 60-70 是源表给的最优区间(工具约定);可读性不是 Google 排名因素。英文公式不适用于中文,得分只作同类页横向对比。
**触发(trigger)**: 主内容文本计算 Flesch-Kincaid 读易分;<60 或 >70 即 warn(中文近似的口径[待核])。
**不修的条件(caveat)**: 可读性不是排名因素,然而它影响真实阅读完成率,所以一般建议向 60-70 靠拢。但学术/法律/技术文档天然低分是受众属性,别为得分把术语稀释成水文。
**修复(fix)**: 长句拆短(一句一个意思);术语首次出现给解释;段落 ≤4 行;中英混排统一标点口径。
**关联(seealso)**: content-word-count、content-heading-family;[scoring-rubric.md](../scoring-rubric.md)

#### content-thin-vs-site
- 名称/类型: 相对站内同类过薄 —— warning · 优先级 medium · 输出 WARN(源表 warn;crawl 模式;**<同类页中位词数一半=警,需 ≥4 个同类页**)
**这意味(what)**: crawl 全站后,该页词数不足同模板/同类页面中位数的一半(同类页 ≥4 个才可判)。
**为什么(why)**: 绝对词数阈值(content-word-count)对工具页/长文页一刀切失真;相对口径按同类校准——同是产品详情页,别家中位 800 词你 200 词,薄就是同维度可比的薄。≥4 个同类页的门槛保证中位数有统计意义,不足则不判(缺数据不等于缺内容)。
**触发(trigger)**: 1) 按模板/类型聚合同类页;2) 组内 ≥4 页才启用;3) 页词数 < 组中位数 ÷2 即 warn。
**不修的条件(caveat)**: 相对薄不(直接)影响排名(词数不是排名因素),然而同模板下显著偏薄多为空字段/抓取失败/未完成页,所以一般建议补实质内容。但新品待充实、UGC 早期短评是真实生命周期状态,排期充实而非硬灌字。
**修复(fix)**: 查模板空字段(无描述的产品页);补齐结构化内容模块;确实无话可说的页并入父级或 410。
**关联(seealso)**: content-word-count、content-duplicate-near;[programmatic-seo-gates.md](../programmatic-seo-gates.md)

#### content-title-pattern
- 名称/类型: 标题模式偏离(源表 ID `content-title-pattern`) —— warning · 优先级 low · 输出 WARN(源表 warn;crawl 模式,≥4 页;标题未以至少 60% 标题所用的后缀结尾=警,标题恰为品牌名则通过)
**这意味(what)**: crawl 全站后,该页 title 不带全站 ≥60% 页面都在用的标题后缀(品牌后缀/站名)。
**为什么(why)**: 品牌后缀一致性是模板健康与品牌 SERP 露出的双信号:多数页"| Brand"而个别页裸标题,几乎总是模板分支漏拼——SERP 里品牌词忽有忽无,同一站在结果页的视觉一致性碎掉。60% 是"主流模式"判定线:达到它,偏离者才算异常。
**触发(trigger)**: 1) 全站 title 提取公共后缀(分词对齐);2) 某后缀覆盖率 ≥60%;3) 不带该后缀的页即 warn。
**不修的条件(caveat)**: 后缀缺失不(直接)影响排名(title 长度哲学同 core-title-present),然而它是模板分支失控的症状,所以一般建议统一。但刻意区分的落地页组(广告着陆页不带品牌测 CTR)是实验设计,标注豁免。
**修复(fix)**: title 模板统一 `主题 | 品牌` 单一出口;超长页可程序化裁后缀保主题(像素口径见 content-agreement);实验页白名单。
**关联(seealso)**: core-title-present、content-agreement、core-title-unique;[scoring-rubric.md](../scoring-rubric.md)

#### content-mime-broken [待核 ID]
- 名称/类型: MIME 与文档破损家族(源表 ID `content-mime-type`、`content-meta-in-body`、`content-broken-html`) —— issue/warning · 优先级 high(fail 档)/medium · 输出 CRITICAL/WARN(源表:MIME=warn/fail;meta 在 body 里=fail;content-broken-html)
**这意味(what)**: 文档级破损三型:页面 MIME 声明与实际不符(warn/fail 分型[待核]);meta 标签出现在 body 里(fail);HTML 结构破损(关键标签未闭合/非法嵌套)。
**为什么(why)**: MIME 错让引擎选错解析器(technical-content-type 的内容侧镜像);meta 出现在 body 时解析器容错重组,description/robots/canonical 可能全部失位——与 core-canonical-outside-head 同构的"声明不在有效位置"家族;结构性破损让 DOM 树与源码意图错位,内容提取随之漂移。三型叠加是"同一页面在不同工具里长得不一样"的根因。
**触发(trigger)**: 1) 响应 Content-Type 与文档实际形态(HTML/XML/文本)不符即 warn/fail;2) meta robots/description/charset 出现在 body 区即 fail;3) 关键标签未闭合/非法嵌套造成解析器重组即破损档。
**不修的条件(caveat)**: 破损判定依赖解析器口径,容错重组后多数用户无感,然而引擎提取的内容树已偏,所以一般建议 CI 过 HTML 校验器。但第三方组件注入的合法容错结构(微前端壳/遗留嵌入)命中属误报面,白名单处理。
**修复(fix)**: 模板过 W3C 类校验器零 error 再发;meta 全部收敛 head 单一出口;MIME 与内容对齐(见 technical-content-type);组件注入走规范插槽。
**关联(seealso)**: technical-content-type、htmlval-document-structure、core-canonical-outside-head;[semantic-html.md](../semantic-html.md)
