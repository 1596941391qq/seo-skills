# 编辑质量检查：空话、套话与机械写法

> 复核于 2026-10-21（首轮 2026-10-18）：Google 官方立场逐条对照原文；AI 检测器的准确率只保留有原始研究的数字。

## 用途与何时读

内容发布前做编辑审稿，或者改一篇「读起来很顺但什么都没说」的稿子时读。

这份清单**不是用来判断作者是人还是 AI**。下面这些毛病，人和模型都会写出来；靠几个词判定作者身份既不可靠，也不是 SEO 要解决的问题。要解决的是：这段文字有没有给读者提供信息。写法规则（句长、语态、术语）见 [asd-ste100-web-writing.md](asd-ste100-web-writing.md)。

## Google 的立场：看质量，不看生产方式

核对 2026-10-21：

- **重点是质量。** Google 关注内容质量，而不是内容怎么生产；合理使用 AI 或自动化不违反其指南（[Search Central 博客 2023-02-08](https://developers.google.com/search/blog/2023/02/google-search-and-ai-content)）。
- **红线是操纵排名。** 用自动化（包括 AI）生成内容，主要目的是操纵排名，违反垃圾内容政策；SpamBrain 等系统按模式和信号识别垃圾内容，不论它怎么生产（同上）。
- **大规模滥用内容。** 为操纵排名、而不是帮助用户，大量生成页面，属于「大规模滥用内容」；例子之一是用生成式 AI 工具生成大量页面却不给用户增加价值（[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies#scaled-content)）。
- **发布前人工核对。** 生成式模型会出错，发布前要人工核对全部 AI 生成内容的准确性，包括 `<title>`、meta description、结构化数据和图片替代文字（[生成式 AI 内容指南](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)，2026-10-01 更新）。Merchant Center 另有规定：AI 生成的商品标题和描述要单独标注，AI 生成的图片要带 IPTC `DigitalSourceType` = `TrainedAlgorithmicMedia` 元数据（同上）。2026-10-01 这次更新还指向质量评估员指南的两节：4.6.5 大规模滥用内容、4.6.6 几乎没有投入、原创和附加价值的主体内容；官方同时说明评估员打分不直接影响排名（同上，2026-11-05 补核）。
- **Who、How、Why。** 读者可能想问「这是怎么做出来的」时，说明自动化或 AI 怎么参与；不要编造作者资料，例如 AI 生成的头像、假名字、假资历。质量评估员的「投入」一项把「用生成式 AI 产出大量文本、没有人工把关」视为几乎没有投入（[有用内容](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)）。
- **不要把 AI 写成署名作者。** 博客 FAQ：给 AI 署名「probably not the best way」让读者知道 AI 参与了创作；应在读者会问「怎么做出来的」时另写说明。

所以编辑检查的目标是信息密度、准确和可信，而不是「去 AI 味」本身。

## 检测器分数不是 Google 的判定

- Google 的公开文档说的是按质量判断、按垃圾内容模式识别，没有说用第三方 AI 检测器的分数判定内容。第三方检测器给出的「AI 概率」不代表 Google 的判定，本套件不把它当发布门槛。
- 已发表的评估显示检测器不可靠（都是原始研究；检测器版本之后有更新，数字只代表当时）：
  - OpenAI 自己的分类器：在英文挑战集上只认出 26% 的 AI 文本，把 9% 的人写文本误判为 AI；2023-07-20 因准确率低下线（[OpenAI](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/)）。
  - Liang 等（Patterns，2023）：7 个检测器测 91 篇非英语母语者写的 TOEFL 作文，平均误报率 61.22%；18 篇（19.78%）被 7 个检测器一致判为 AI；美国八年级学生作文几乎全部判对（[arXiv 2304.02819](https://arxiv.org/abs/2304.02819)）。
  - Weber-Wulff 等（2023）：12 个公开工具和 2 个商业系统，结论是既不准确也不可靠，倾向于把 AI 文本判成人写；改写混淆后表现更差（[arXiv 2306.15666](https://arxiv.org/abs/2306.15666)）。
  - RAID 基准（Dugan 等，ACL 2024）：600 多万条生成文本、12 个检测器；对抗攻击、采样方式、重复惩罚和没见过的模型都能让检测器失效；许多检测器自称 99% 以上准确率，却很少在共享基准上评估（[arXiv 2405.07940](https://arxiv.org/abs/2405.07940)）。
- 词频研究只能说明总体趋势。Kobak 等分析 1,500 多万篇 PubMed 摘要，发现 2024 年 delves、underscores、showcasing 等词的使用突然增多，推算至少 13.5% 的 2024 年摘要经过大模型处理；作者明确说这个方法不能识别单篇摘要（[arXiv 2406.07016](https://arxiv.org/abs/2406.07016)）。所以词表只能提示「这里可能写空了」，不能证明作者是谁。

## 检查项

| 问题 | 怎么识别 | 改法 |
|---|---|---|
| 背景铺垫式开头 | 头一两句在谈时代、趋势、行业变化，删掉后读者没有损失 | 直接给出答案、结论或读者的问题 |
| 无信息的过渡和总结 | 「值得一提的是」「综上所述」之类的连接语，每节末尾复述一遍前文 | 删掉，确认意思没丢；需要总结就只放在全文结尾，并写出新的判断 |
| 机械排比 | 总是三项并列，「不仅……更……」反复出现，各项之间没有实质区别 | 按实际条目数写，合并重复项，每项写出具体差异 |
| 空洞形容词和夸大 | 「强大」「全方位」「极致」「颠覆性」，却没有对应的事实 | 换成可核实的事实：参数、条件、对比结果；数字附来源；做不到就删 |
| 模糊来源 | 「研究表明」「专家认为」「数据显示」，却没说是谁、何时、在哪 | 写明来源并加链接；找不到来源就删掉这句 |
| 措辞与证据不匹配 | 句句「可能」「在一定程度上」，或者毫无依据地说「一定」「必然」 | 证据强就直说，证据弱就写明条件和局限 |
| 格式滥用 | 满篇加粗，所有内容都拆成列表，连续感叹号或破折号，标题里堆表情符号 | 格式只用来帮读者扫读；需要论证的内容保留成段落 |
| 千篇一律的结构 | 每节都是「定义、重要性、技巧、总结」四段 | 按读者的问题组织，结构跟着内容走 |
| 缺少一手信息 | 没有例子、截图、数据、亲自操作的细节，换成任何一家的网站都成立 | 补上只有你能提供的内容：实测结果、真实案例、踩过的坑 |

## 改写示例（自拟）

- 改前：在数字化转型不断深入的今天，网站速度的重要性不言而喻。
- 改后：页面加载慢，最直接的后果是用户还没看到内容就离开。下面先说怎么测，再说怎么改。

- 改前：这款工具功能强大、体验极佳，能全方位满足你的需求。
- 改后：这款工具支持批量导出和定时任务，但不支持离线使用；如果你需要离线工作，要另选工具。

## 五步自查

1. 删掉第一段再读：读者损失了什么？没有损失就删。
2. 只读每段第一句：能不能串起全文的要点？不能，就调整段落顺序或主题句。
3. 圈出所有形容词和副词：能换成事实的换掉，换不了又不影响意思的删掉。
4. 圈出所有数字和「研究表明」：逐条补来源，补不了就删。
5. 问自己：这段话能不能原样搬到竞品的网站上？能，就说明它还缺少你自己的信息。

## 检查清单

1. **事实已人工核对** → 逐条核对正文、title、meta description、结构化数据、图片替代文字里的事实 → 通过：每个事实有来源或实测记录；失败：有 AI 生成而未核对的事实（Google 生成式 AI 内容指南的要求）。
2. **空话和营销词** → `python3 scripts/text_metrics.py --market zh < page.txt`（`--market` 可取 zh、en、ja）：报中英 slop 词、无指涉声明、破折号 ≥3 次；`python3 scripts/market_lint.py --market zh page.txt`：`markets.json` 营销词 >3 处告警 → 通过：每个命中都换成事实或删除；失败：保留无法核对的夸张说法。
3. **句长节奏** → `text_metrics.py` 在句长标准差小于均值 25% 时报 metronomic；`market_lint.py` 的「句长 CV」一项同口径（本套件口径）→ 通过：没有告警，或告警句已改；失败：整篇句长一样且内容空。节奏只是提示，不是判定作者的依据。
4. **来源完整** → 五步自查第 4 步 → 通过：没有「研究表明」类无主语句；失败：有。
5. **AI 参与的说明** → 对照 Who、How、Why → 通过：读者会问「怎么做出来的」的页面有说明，作者信息真实；失败：编造作者，或把 AI 写成署名作者。
6. **不用检测器分数** → 审稿记录 → 通过：交付物里没有「AI 概率」；失败：用检测器分数决定能否发布。

## 交付时给出

一份修改清单，每条包括：原句位置、问题类型（对应上表）、建议改法；需要作者补充的一手信息单独列出。不给「AI 概率」之类的分数。

## 常见误区

- 用 AI 检测工具的分数决定稿子能否发布。
- 只做同义词替换，信息量没有变化。
- 为了「像人写的」故意加口语和错别字。
- 把所有长句都拆碎，导致论证断裂。
- 把零宽字符当成 AI 生成的证据。

## 各语言的标记表

原理（本套件口径）：问题通常不在某个词用错，而在**同一种写法反复出现**。所以按密度检查，不按单个词定罪。日语写作规范仓库 hana652/tech-writing-pack 从 5 篇样本里归纳了这一点；样本太少，它给出的倍数本文不采用。

每个语种的表要由母语者维护，并写上日期。下表的出处是第三方写作规范仓库，不是研究，命中只作提示：

| 语言 | 示例标记 | 出处 |
|---|---|---|
| 中文 | 营销词（创新领先、卓越、极致类）、标题党（暴涨、封神、必看） | 本套件 `scripts/markets.json` 的 zh 营销词表，`market_lint.py` 执行 |
| 英文 | 自动三连排比、每句 12–18 词的匀速节奏、总结式破折号从句、段落长度一样、空洞强化词、没有指代的「行业领先」 | [Yuzzyuk/marketing-os slop-patterns](https://github.com/Yuzzyuk/marketing-os/blob/main/skills/marketing-os/references/slop-patterns.md)（MIT）；本套件词表在 `text_metrics.py` 的 `EN_SLOP` |
| 印尼语 | 「hiruk pikuk」：该仓库列为最高优先级的禁用词，称经母语者验证 | [alvinindra/bahasa-skills · frasa-terlarang](https://github.com/alvinindra/bahasa-skills/blob/main/skills/bahasa-inti/references/frasa-terlarang.md) |
| 日语 | 对比句式「AではなくB」等技法的出现密度 | [hana652/tech-writing-pack · 07-ai-buntai-laws](https://github.com/hana652/tech-writing-pack/blob/main/guides/07-ai-buntai-laws.md) |

marketing-os 的判据可以借用：正式语域本身不是问题，问题是空；好文案至少有一个能被核对、也可能被证伪的事实（本套件转述）。旧版表中的葡萄牙语、波兰语、荷兰语、越南语行没能核到出处中的对应内容，已删除。

## 不可见字符

- `python3 scripts/text_metrics.py --scrub < page.txt > clean.txt` 扫描并删除这些字符：U+200B、U+FEFF、U+200C、U+200D、U+2060–U+2064、U+180E、U+202F。它们会引起渲染和复制问题，发布前值得清理。
- 不要把它们当成 AI 生成的证据。本组没有找到模型厂商说明自己用这些字符做文本水印的一手声明（2026-10-18）。
- **法语页不要删 U+202F。** 法语排版在 `: ; ! ?` 前要求窄不换行空格，`market_lint.py --market fr` 会检查 U+202F 或 U+00A0 是否在场；`--scrub` 会把 U+202F 一起删掉。

## 来源

本文由 EveryInfra 自行编写，只保留要点，未复制原文。核对日期均为 2026-10-21。

- 思路参考：[coreyhaines31/marketingskills · skills/seo-audit/references/ai-writing-detection.md](https://github.com/coreyhaines31/marketingskills/blob/v1.10.0/skills/seo-audit/references/ai-writing-detection.md)（MIT）
- Google 一手资料：[Google 关于 AI 生成内容（2023-02-08）](https://developers.google.com/search/blog/2023/02/google-search-and-ai-content)、[生成式 AI 内容指南](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)、[有用、可靠、以人为本的内容](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)、[垃圾内容政策](https://developers.google.com/search/docs/essentials/spam-policies)
- 检测器研究：[OpenAI 分类器公告与下线说明](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/)、[Liang 等 2023](https://arxiv.org/abs/2304.02819)、[Weber-Wulff 等 2023](https://arxiv.org/abs/2306.15666)、[Dugan 等 2024（RAID）](https://arxiv.org/abs/2405.07940)、[Kobak 等（Science Advances 2025）](https://arxiv.org/abs/2406.07016)
