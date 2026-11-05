# 可引用性打分（内容能否被 AI 引用）

> 建立于 2026-10-09；2026-10-21 对照各来源仓库原文再次复核（权重、veto 项、抽样规则逐项读到原文）；复核于 2026-11-05（补两篇论文）。
> 打分衡量内容的**形状**是否便于摘取和核实，不衡量引用结果——好分数不保证被引。
> **本文所有权重、档位和阈值都是第三方作者的判断或本套件口径，没有一项经过受控实验验证。** Google 明确说第三方工具拿不到其内部排名数据（[third-party-seo](https://developers.google.com/search/docs/fundamentals/third-party-seo)）。分数只用来排整改顺序。
> 证据仲裁见 [geo-evidence.md](geo-evidence.md)：按域名控制后，通用 Schema、CWV 对 AI 引用没有独立效应，FAQ 段只有很小的正值；提示-内容对齐和域名级权威是主导变量（[geo-evidence-bank.md](geo-evidence-bank.md) 第七节第 1 条、第八节）。2026-10 的第二份独立数据（第七节第 12 条，[arXiv 2610.15033](https://arxiv.org/abs/2610.15033)）同向：同站内比，只有标题和段落对上用户问法与引用相关，FAQ 块、结构化数据、摘要框、页速只在跨站比较时显得有效；「被引擎检索到」解释的差异远大于页面属性。所以本文的块级打分只决定「被检索到之后好不好摘」，管不了「会不会被检索到」。

**用哪套（入口决策）**：

| 场景 | 用哪套 | 工具 | 来源 |
|---|---|---|---|
| 快速评估一个站 | AIV 五支柱（第二节） | 人工读档打分 | [jianruntech/geo-score](https://github.com/jianruntech/geo-score) rubric v1.1 |
| 单页深入体检 | CORE-EEAT 80 项（8 维 × 10 项） | `python3 scripts/core_eeat.py 页面.html`（可加 `--url URL`） | [aaron-he-zhu/seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) v9.9.12 `references/core-eeat-benchmark.md` |
| 域名评级 | CITE 40 项（4 维 × 10 项） | `python3 scripts/cite_domain.py --input answers.json --json out.json`（`--template` 打印输入模板） | 同仓 `references/cite-domain-rating.md` |

- 三套可叠：域名 CITE → 站点 AIV → 单页 CORE-EEAT。
- CORE-EEAT 的 veto 项是 T04（未披露利益关系）、C01（标题承诺与内容不符）、R10（页面数据自相矛盾）；CITE 的 veto 项是 T03、T05、T09。源仓库 `auditor-runbook.md` §2 规定：一项 veto 失败，维度分与总分封顶 **60**；两项以上标 BLOCKED，不出分。本套件 `core_eeat.py` 已按此对齐（2026-10-21）。

## 一、块级五维打分（第三方设计，权重是作者判断）

来源：[zubair-trabzada/geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) `skills/geo-citability/SKILL.md`。

| 维度 | 权重 | 看什么 | 证据强度 |
|---|---|---|---|
| 答案块质量 | 30% | 段落是否直接回答一个能被问出的问题；先结论后展开 | 弱：Bing 指南要求关键信息靠前、陈述不依赖隐含内容；Google 说不需要为 AI 切块 |
| 段落自含性 | 25% | 抽出来单独读，不靠上文代词也成立 | 弱：同上 |
| 结构可读性 | 20% | 标题层级、列表、定义先行 | 观察相关：AirOps 称标题层级连续的页面被引几率 2.8 倍；Google SEO 入门指南说标题的数量和顺序对搜索没有影响 |
| 统计密度 | 15% | 有来源的数字有多密 | 有冲突：GEO 论文在固定上下文里「加统计」等方法 +30–40%；C-SEO Bench 发现多数此类改写无效 |
| 独特与原始数据 | 10% | 自有一手数据、图表、表格 | 方向一致：Google 指南强调「非同质化」内容 |

- 该仓写的「134–167 词是最优被引段落长度」引自它称为「Bortolato 2025」的分析，2026-10-21 再搜仍只找到转引文章、没有原始研究，**不作为阈值使用**。同一文件还写「GEO 优化内容可见性提升 30–115%」，这是把 GEO 论文的 +30–40%（三种方法，位置加权词数）和 +115.1%（原排第 5 的来源用「引用来源」那一格）连成一个区间，论文没有这个结论（[arXiv 2311.09735](https://arxiv.org/abs/2311.09735) Table 2）。段落长短按读者和题目定；Google 写明没有理想页长。
- **整页覆盖度**（本套件口径）：整页分 = 得分 >70 的块的占比。单块高分不够，要看全页能被摘取的密度。
- **FAQ 是条件件不是标配**：只在页面命中问句式搜索、用户有真实疑问、能写出正文没答的问题时才加。2609.35077 里可见 FAQ 段 β=+0.07，作者称效应很小；SE Ranking 的合并数据里带 FAQ Schema 的页面平均引用反而更少（3.6 vs 4.2）。
- JS 注入的 Schema：Google 能读；不执行 JS 的爬虫只读初始 HTML。给 AI 爬虫看的事实与标记要在初始 HTML 里（本套件口径）。

## 二、AI 就绪度分层审核（站点级，geo-score rubric v1.1）

结构（[rubric/v1.1.md](https://github.com/jianruntech/geo-score/blob/main/rubric/v1.1.md)，核对 2026-10-18）：

- **五支柱**：Reachable 15 / Understandable 22 / Content Citability 35 / Brand Credibility 18 / Answer Fit 10。
- **抽样**：恰好 8 个 URL——首页、2 个主要产品/服务页、2 个文档/知识页、3 个近期内容页；不足 8 个就全取并在报告写明。
- **三态**：scored / unobservable / not_applicable；后两者离开分母，报告写「Readiness X / 可观测满分 Y」。
- **gate**：三个 `g.` 检查（robots、可达、SSR）只在得 0 分时把归一化百分比封顶 40%；中间档只扣分不封顶。挑战页不算样本页，全站只有挑战页时不评分，不读作 0 分。
- **bonus**：llms-full.txt、ai.txt、GEO link tags、speakable 四项只加分（上限 +6），不进分母。
- **分档**：Leading 83+ / Solid 66+ / Growing 51+ / Early 31+ / Not started。
- **中文引擎就绪**满 2 分 = 可抓取 + ICP 备案 + 实体信息完整（rubric 作者的判据，非引擎官方规定）。

作者自己公布的证据强度（[evidence-v1.1.md](https://github.com/jianruntech/geo-score/blob/main/rubric/evidence-v1.1.md)，引用时照抄限定）：

- 最重的「自含答案段」（9 分）只有两篇预印本支持，Google 又说不必为 AI 切块；25–120 词窗口来自作者的校准审计。
- 「标题匹配问法」（7 分）没找到一手支持；一篇观察性预印本（3 位独立研究者，602 个提示、21,143 条检索层引用）发现问答格式页面平均影响力 0.0947 对 0.1005，低 5.74%（[arXiv 2604.25707](https://arxiv.org/abs/2604.25707)），作者说问答格式本身作用弱，不证明格式有害。
- 「有源统计」（7 分）是外部证据最强也最有争议的一项：GEO 论文 +30–40%，C-SEO Bench 发现多数改写方法无效。
- llms.txt（5 分）奖励的是采用一个约定，不是可证明的效果；Google Search 不使用它。
- 「知识图谱实体是最强单信号」没有出处。
- ai.txt 是两个不相关提案共用的名字，没有答案引擎声明读取。
- speakable 是 Google 的 Beta 功能，只用于美国、英文、Google Home 设备上的新闻类回答（[Google 文档](https://developers.google.com/search/docs/appearance/structured-data/speakable)）。

分档稳定性（[bands-analysis.md](https://github.com/jianruntech/geo-score/blob/main/rubric/bands-analysis.md)）：2026-09-27 的 317 站旧跑里，Leading 只有 32 站（10.1%）达到；当时重测的测量误差 3.09 分，单次分数 95% 区间约 ±6.1 分；168 站（53%）落在切线 ±6.1 以内；同一版本两次运行有 7.9% 的站换档。作者随后用 geo-score 1.8.0 在 2026-10-12 做同日重测，测量误差降到 1.41 分；324 站里 98 站落在切线 2.8 分以内，Leading 只有 21 站（6%）。**相邻两档的差别仍可能在噪声以内**，报告要写区间，不只写档位。

## 三、方法纪律（本套件强制）

1. **抽样协议**：照 AIV 的 8 个 URL 抽样，保证跨站可比。
2. **三态标注**：每项 scored / unobservable / not_applicable；不可观测不等于 0 分。
3. **测量与整改分开报告**：就绪度分数与实测引用表现是两个数，不合并成一个「AI 可见度」。
4. **引用数据带不确定度**：报告实测引用时附样本量 n 和 95% 区间；一次性观测不可靠，要多次测（[arXiv 2604.07585](https://arxiv.org/abs/2604.07585)）。
5. **确定性脚本与 LLM 判分分开标注**：后者同一 URL 两次运行结果可能不同。
6. 不承诺分数与被引的因果关系。
7. **先诊断失败环节再改**：页面没被引时，先分清是「没被检索到」「检索到了没被选」还是「被选了没署名」，再对症改；通用改写模板可能伤害长尾内容（[arXiv 2603.09296](https://arxiv.org/abs/2603.09296)，预印本，[geo-evidence-bank.md](geo-evidence-bank.md) 第七节第 13 条）。没被检索到时，改块级结构基本没用，先查索引、抓取和标题与问题的对齐。

## 四、作者与可验证信号（E-E-A-T 的可机检子集）

Google 用「Who / How / Why」自查（[有用内容指南](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)）：页面在读者期望处有署名；署名能链到作者背景；AI 辅助过程在读者会关心时说明；内容为人而写。可机检的部分：

- 署名存在且链到身份页（作者页的 sameAs 指向 LinkedIn、ORCID 等）。
- 可见日期与 dateModified 一致；只改日期不改内容是 Google 点名的负面做法。
- 统计带可点击的来源。
- 组织 sameAs 都能打开，无死链。
- 有原始数据产物（表格、图、数据集），不是纯转述。

## 五、市场差异：单位不是通用的

英文的「词」不能直接搬到中、日、韩、泰。中文按字计，日韩按全角字计，泰语先分词（`Intl.Segmenter("th")`）再算密度。各语言的块长、句长阈值都是本套件口径，见 [multilingual-workflow.md](../overview/multilingual-workflow.md) 第四节。评分前剥离导航和页脚（本套件口径）。

「纯问答格式 −5.7%」不是中文实测：它来自海外三平台的观察数据（2604.25707，平均影响力差异，描述性），不能当中文规则，也不能当因果。

## 六、其他第三方评分器（只作设计参考，不作结论）

| 评分器 | 结构 | 来源 |
|---|---|---|
| geo-seo-claude 站点评分 | 六类：Citability 25 / Brand 20 / E-E-A-T 20 / Technical 15 / Schema 10 / Platform 10；分档 90/75/60/40；文档自带三条声明：确定性、权重是观点、诊断不是保证 | [docs/scoring-methodology.md](https://github.com/zubair-trabzada/geo-seo-claude) |
| Auriti geo-optimizer | 默认 rubric v2（v4.19，对齐 Google AI 文档）：google_ai 20 / robots 14 / schema 14 / content 14 / brand_entity 12 / meta 11 / llms 6 / signals 6 / ai_discovery 3；v1 仍可用 `--score-version 1`（robots 18 / llms 18 / schema 16 / meta 14 / content 12 / brand_entity 10 / signals 6 / ai_discovery 6）；分档 86/68/36（源码注释记有下调历史） | [models/config.py](https://github.com/Auriti-Labs/geo-optimizer-skill/blob/main/src/geo_optimizer/models/config.py) |

- 这些评分器给 Schema、llms.txt 的分值是机器可读性卫生分，**不是被引概率**。用它们排整改顺序时，Schema 与 llms.txt 排在提示-内容对齐和站外权威之后；产品页把价格、规格写进 Product/Offer 字段除外。
- 有的仓库把 GPTBot、ClaudeBot 等训练型爬虫算进「关键爬虫」扣分，与厂商文档矛盾；爬虫分层以 [geo-platform-differences.md](geo-platform-differences.md) 第三节为准。

## 七、检查清单

| # | 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|---|
| 1 | 买家原话出现在标题、H1、首段 | `python3 scripts/question_align.py --gsc 查询页面.csv --pages 页面.csv --json`，方法见 [question-alignment.md](question-alignment.md) | 通过：重点页的 title/H1/首段第一句含该页主要查询的原词并直接作答。失败：首段在铺垫 |
| 2 | 句子短、一句一事、术语一致 | `python3 scripts/ste_lint.py 页面.md --lang zh --json`（英文用 `--lang en`），口径见 [asd-ste100-web-writing.md](asd-ste100-web-writing.md) | 通过：无 fail 级问题。失败：长句、术语不统一 |
| 3 | 单页 CORE-EEAT 机检切片 | `python3 scripts/core_eeat.py 页面.html --url URL` | 通过：无 veto 命中，GEO/SEO 两个分数都写进报告。失败：命中 veto（利益未披露、标题与内容不符、数据自相矛盾） |
| 4 | 有源数字 | 人工逐条点开页面上的统计来源 | 通过：每个数字都能打开到原文且数字一致。失败：死链、数字漂移、无来源 |
| 5 | 署名与日期 | 看作者行与作者页；比对可见日期与 JSON-LD 的 dateModified | 通过：署名可解析，两种日期一致。失败：「本站编辑」、日期不一致 |
| 6 | 结构化数据卫生 | `python3 scripts/schema_lint.py URL` | 通过：无报错、无为 AI 新增的 FAQPage。失败：占位符、空答案、悬空 @id |
| 7 | 文本节奏与套话 | `cat 页面.txt \| python3 scripts/text_metrics.py --market zh` | 通过：无大段模板化句式与套话。失败：命中多处 slop 词 |
| 8 | 域名级 | `python3 scripts/cite_domain.py --template` 填好后 `--input answers.json --json out.json` | 通过：无 veto，未观测字段写 unknown。失败：把未观测当 0 |
| 9 | 分数用法 | 读报告 | 通过：写「启发式、非引擎信号」，就绪度与实测引用分开，带区间。失败：把分数写成「被引概率」 |
