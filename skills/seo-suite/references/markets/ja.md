# 日本語市場专项(ja)

> **定位**:ja 市场的增量情报层。数值型规则(全角 title 32 / desc 120、体裁字数分层、敬语、「AI 臭」指纹词表、nosnippet 等)在 `scripts/markets.json` 的 `markets.ja`。本文件只写增量:**设备口径份额差、MEO 与口コミ規制、AI 引用実測、相場与红旗**。
> 2026-10-21 逐条重核:数字回到原始页面读过;读不到的删除或降级。标注:【官】=官方页面;【三方】=第三方研究或厂商(写机构、时间);【本套件口径】=本套件约定。断言半衰期 6–12 个月。
> 提问对齐见 [question-alignment.md](../content/question-alignment.md);句子写法见 [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md)。

## 一、エンジン格局:按设备拆开报

StatCounter 日本搜索引擎份额(取数 2026-10-21):

| 口径 | 2026-09 | 说明 |
|---|---|---|
| 全デバイス | 2026-10 CSV:Google 59.58% / Bing 32.26% / Yahoo! 6.57%(取数 2026-11-05)。2026-09:Google 59.27% / Bing 31.41% / Yahoo! 7.61%(页面表;CSV 59.08 / 31.63 / 7.58) | 2026-03 至 09 月度:Google 55.4–62.8%,Bing 28.5–36.4% |
| デスクトップ | **Bing 51.83% / Google 42.17%** / Yahoo! 4.67% | 月度摆动大:Google 8 月 54.87%、9 月 41.93%;3 月 47.51% 对 Bing 46.94% |
| モバイル | Google 85.08% / Yahoo! 11.79% / Bing 0.91% | 3–9 月 Google 82.1–85.1%,Yahoo! 11.8–14.2% |

- 来源:[StatCounter 日本](https://gs.statcounter.com/search-engine-market-share/all/japan)(三个设备页同路径),页面表读数与 CSV 导出差 0.0x–0.2 个百分点。
- 结论:桌面上 Bing 领先是**单月**读数,8 月 Google 还领先 15 个百分点,不当作结构性反超。提案里写「Google 份额」必须带设备与月份。
- Google AI Overviews 在日本可用,语言含日语(【官】[Google 帮助中心](https://support.google.com/websearch/answer/14901683?hl=en),核对 2026-10-21)。
- **Yahoo! JAPAN 搜索用 Google 的搜索引擎**:2010-07 Yahoo! JAPAN 宣布采用 Google 的搜索引擎和搜索联动广告系统(【三方】[国立国会図書館 カレントアウェアネス 2010-07-27](https://current.ndl.go.jp/car/16564));2025–2026 年的二手解读称现在仍是 Google 结果、显示与功能由 Yahoo! 自己做(【三方】[seohacks 2025-09](https://www.seohacks.net/column/29236/)、[seopack 2026-10](https://seopack.jp/seo_faq/yahoo_google_search_ranking.php))。做法(本套件口径):Yahoo! 不单独做自然搜索优化;知恵袋、ニュース等自有服务另算。
- 测量盲区:Search Console 不含 Bing 流量,桌面 B2B 站要并行接入 Bing Webmaster Tools(`scripts/bing_wmt.py`)。

**業種別主戦チャネル**(本套件口径,进入顺序):

| 業種 | 1順位 | 2順位 |
|---|---|---|
| ローカル(飲食/美容/医療) | Google ビジネスプロフィール + 食べログ等垂直平台 | 垂直媒体;名称・住所・电话三处对表 |
| Eコマース | 自社ドメイン SEO + Google ショッピング | 比較メディア |
| コンテンツ/メディア | 自社ドメイン + note | 知恵袋、Qiita 补位 |
| B2B/SaaS | 自社ドメイン(事例/資料) | Qiita / Zenn(开发者向)、PR TIMES |

## 二、MEO、口コミ規制、UGC 平台

### 2.1 本地排名:Google 官方三要素

- 【官】Google 本地搜索结果「主要基于关联性、距离和知名度」(原文 relevance, distance, prominence);店铺信息越完整准确,越可能出现(【官】[Google ビジネスプロフィール ヘルプ](https://support.google.com/business/answer/7091?hl=ja))。
- 日本业界常说的「MEO 三要素」(店舗情報、口コミ、投稿)是业界口径,不是 Google 的排名定义。帮助页没有把发帖频率列为排名因素。「每周 1–2 次发帖」「口コミ 25 件」是业界经验值(本套件口径),先用自己店铺数据验证。
- 做法(本套件口径):信息填满 → 口コミ回复(含差评)→ 照片持续追加 → 月度数据复盘。

### 2.2 口コミ与ステマ規制

- 【官】消費者庁 景品表示法 ステマ規制自 2023-10-01 起施行(告示:令和 5 年内閣府告示第 19 号)。
- 【官】消費者庁 Q&A(Q6):为打折而要求顾客在预约网站发口コミ,**未指示内容**时,该口コミ通常不算「事業者の表示」,不违反告示;若条件是打「星5」(或要求写推荐性评语),则事业者决定了表示内容,算「事業者の表示」,不明示即违反告示(【官】[ステルスマーケティングに関するQ&A](https://www.caa.go.jp/policies/policy/representation/fair_labeling/faq/stealth_marketing/))。
- 【官/三方】首例:2024-06-07 消費者庁对东京一家内科诊所发措置命令,理由是以折扣为条件要求顾客在 Google 地图发 4–5 星口コミ(【三方】[ネットショップ担当者フォーラム](https://netshop.impress.co.jp/node/12404))。
- 【官】Google 地图政策**另外**禁止:以付款、折扣、赠品等换取发布任何评价,以及劝阻或禁止差评、有选择地征集好评(review gating)(【官】[Maps UGC policy](https://support.google.com/contributionpolicy/answer/7400114?hl=en))。
- 所以分两层(本套件口径):景表法层 —「打折换评价」本身未必违法,「指定星级」违法;Google 层 — 任何激励换评价、只导流满意顾客都违反政策,评价会被删。
- QR 码请客人写口コミ、全件回复(含差评)是安全做法;前提是不筛选、不指定星级、不给激励。

**口コミ三级速查**(本套件口径):

| 等级 | 项目 | 处理 |
|---|---|---|
| 完全禁止 | 指定「星5つ」/ 激励换评价(Google 层)/ 自作自演 / 假レシート / review gating | 拒绝 |
| 灰色(条件付) | 体験談掲載、有偿提供商品的评测 | 明示利害关系,法务检收 |
| 推荐 | QR 常設、全件返信、照片自然积累 | 执行 |

### 2.3 UGC / 专业平台(Ahrefs 2026-09 版,见 4.2)

| 平台 | 在日本 AI 引用榜的位置 |
|---|---|
| note | 总榜第 3(6 月版第 2) |
| Yahoo!知恵袋 | 总榜第 4(6 月版第 5) |
| Qiita / Zenn | 技术类查询的 UGC 来源(本套件口径,榜单未单列) |
| 食べログ | 餐饮名称・住所・电话锚点(本套件口径) |

## 三、言語機制:全角阈值、体裁、AI 臭

- **全角阈值**(本套件口径):title 32 全角 / desc 120 全角,半角按 0.5 折算(`visible_length` 口径)。Google 对 title 与 description 没有字符上限,按设备宽度截断。
- **体裁字数**(本套件口径):MEO 页 500–1,200 字,一般記事 1,500–3,500 字,支柱頁 7,000–12,000 字。Google 明说没有偏好字数(【官】[Helpful content 指南](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)),所以这些只是体裁参考,不凑字数。`markets.json` 的 `pillar_min` 7,000 同样按此理解。
- **敬语**:です/ます 全站一致;だ/である 仅限学术栏。搜索关键词是名词终止形,标题关键词与正文语域分离(与 ko 同构)。
- **全角英数字混在**(ＳＥＯ / SEO)与 charset / lang 声明:老 CMS 默认全角字符,是日本特有的 lint 点。
- **AI 臭六法則**(本套件口径;原先写的「humanizer-ja / meiseki / yomiyasu 开源工具共识」未逐个核,不再引用):
  1. 箇条書き依存:「以下の3つ」开场加全文列表化 → 保留段落叙述比例;
  2. 定型前置き/締め:「まとめると」「ぜひお試しください」直接删;
  3. 誇張語:「革命的」「ゲームチェンジャー」「究極/圧倒的/革新的」(`marketing_words`)零容忍;
  4. 絵文字箇条書き、「太字+コロン」リスト定型;
  5. 「AではなくB」対比構文 ≤2–3 次/篇;
  6. 句长方差过小(均质ですます)→ 穿插体言止め。
- 已删:「ヒルクプイクク」条目(2026-10-21 检索不到原始报道;原文自己也标「業界通説」,不再作为 lint 依据)。

## 四、AI 引用実測

### 4.1 四引擎引用重叠(life-from2020 自社研究)

- 【三方·小样本】LIFE 公司自测:2026-02-27 至 03-29,37 个关键词(美容、HR SaaS、金融、转职、教育等多业种),9,891 条域名引用,ChatGPT / Gemini / Perplexity / AIO。结果:1,843 个被引域名里只有 81 个(4.4%)被 4 个引擎全部引用;同一查询同一天 4 引擎全引用的比例平均 1.2%、中位数 0%;两两 Jaccard 最高是 Perplexity × AIO 18.9%,ChatGPT 与其余三个引擎 6.0–6.9%;品牌名重叠约 14%(【三方】[原文 2026-04-05](https://life-from2020.com/blog/ai-engine-citation-overlap/))。
- 同机构:ChatGPT 引用域名里,Google 搜索上位的比率为 19.9%,其余三引擎为 45.7–49.4%(2026-07-20 文,[blog](https://life-from2020.com/blog/));AI 推荐第 1 位的下周保持率 50.3%,引擎间 23%–64%(2026-05-06 文);同一问题换问法,AI 给出的引用 URL 数量差 2–11 倍,但 URL 重复率只有 8–12%(2026-03-20 文)。
- SEO 与 AI 推荐的相关:Spearman ρ=0.28,TOP3 一致率约 35%,AI 推荐第 1 位约 45% 在 SEO 圈外(2026-06-25 文)。**限制**:用的是「某一业种的地域检索」数据,不是全行业;原先写的「2026-05 追试」日期不对。
- 做法(本套件口径):SEO 与 GEO 分开考核;同一问句多种问法并测;每周定点,不用单次快照下结论。

### 4.2 Ahrefs 日本 AI 引用域名榜 2026-09 版

- 【三方】Ahrefs(Brand Radar + Letaido),调查时点 2026-09-29–30,分析对象 Google AI Mode / AI Overviews / ChatGPT / Perplexity / Copilot,业种不限的日本语问题;7–8 月问题数从约 1,400 万扩到约 3,000 万,所以与 6 月版只比名次,不比次数(【三方】[Web担当者Forum / Yahoo!ニュース 2026-10-08](https://news.yahoo.co.jp/articles/22ebb14009e03672d98ad10fd0bf2de1fd445932)、[jinrai 2026-10-14](https://jinrai.co.jp/blog/2026/10/14/ai-cited-domains-japan-2026-09/))。
- 总榜:Wikipedia 日本語版 1 位(6 月版 3 位)、google.com 2 位(原圈外)、note 3 位(原 2 位)、Yahoo!知恵袋 4 位(原 5 位)、YouTube 5 位(原 1 位)、PR TIMES 7 位(原 6 位)、my-best 8 位(不变)、weblio 9 位与コトバンク 10 位(新进)。词典/百科类占 top10 三席。
- 6 月版 ChatGPT 引用第 1 位的 Reddit,9 月版在 5 个 AI 的 top10 里都没有。YouTube 在 AI Overviews 里仍是第 1、AI Mode 第 2:不同 AI 差异大,按引擎看。
- 对照的 6 月版:YouTube 首位、note 从 5 位升到 2 位、Reddit / 知恵袋 / my-best 新进前十(【三方】[Ahrefs 新闻稿](https://prtimes.jp/main/html/rd/p/000000058.000157671.html)、[Advertimes 2026-07-22](https://www.advertimes.com/20260722/article551247/))。两个版本的名次不同,引用时写版本和调查时点。
- Stacker × Scrunch 共同调查(2026-03,美国内容分发平台,厂商研究):经第三方媒体分发,AI 引用中位数提升 239%(【三方】经 [life-from2020 2026-04-12](https://life-from2020.com/blog/geo-media-acquisition/) 转述)。这不是日语数据,不能写成「日语 GEO 最高杠杆」。
- 已删:「Copilot 引用 note 65,023 回」「新闻域名跌出 top10」(读不到原始数据)。

### 4.3 测量节奏(本套件口径)

| 周期 | 动作 | 产出 |
|---|---|---|
| 周 | 自社关键词在 4 个引擎的引用有无与推荐位(同问句 2–3 种问法) | `citation_panel.py` 台账 |
| 月 | 引用域名构成对 Ahrefs 月榜 | 月度定点报告 |
| 季 | 4.1 全量重跑;ChatGPT 单独复核 | 基线更新 |

### 4.4 引用枠空置位(杠杆位,2026-10-11 立,本套件口径)

对目标查询集采样,按引擎和查询语言分桶记录「无引用源答案」的份额;份额高说明位置还空,收敛说明竞争者已填满。选题:问句型长尾(「~とは」「~どっち」)加知恵袋、Qiita 补位。入口见 [multilingual-workflow.md](../overview/multilingual-workflow.md) 十节杠杆位表。

## 五、情報源

| 媒体 | 定位 | 节奏 |
|---|---|---|
| 海外SEO情報ブログ(suzukikenichi.com) | Google 官方动向日语化 | 日更至周更,RSS |
| Web担当者Forum(webtan.impress.co.jp) | 企业 Web 担当者社区;转载 Ahrefs 日本榜 | 周更 |
| life-from2020(LLMO・AIO・GEO リサーチ) | 日语 AI 引用実測(小样本自社研究) | 月更 |
| Ahrefs ブランドレーダー 日本榜 | 日语 AI 引用域名榜 | 不定期(已见 6 月版、9 月版) |

GIG INC.「giglab」「LLM Insight」未核其近况,已从定点三件套里去掉。

## 六、相場(日本业界厂商自报,2026-10-21 抽查)

| 项 | 相場 | 来源 |
|---|---|---|
| SEO 外注(コンサル型) | 月 10–50 万円为主;公开报价 7 家平均约 32.1 万円/月 | 【三方】[shwat.jp](https://shwat.jp/ultra/seo-price/) |
| MEO 代行 | 月 3–5 万円;成果报酬型有「按日计费」 | 【三方】[ローカルミエルカ 2025-12-25](https://local-mieruca.com/blog/meo_market-price_cost/) |

- 已删:コンテンツ SEO「1 記事 5–10 万円」「月 5–30 万円」、MEO「月 1–5 万円/店」「1 キーワード 日额 300–500 円」(与来源给的区间不符,或读不到)。ローカルミエルカ写的成果报酬例子是日额 1,200–1,500 円(月 3.6–4.5 万円)。
- 厂商自报价,只用来识别报价是否离谱;报价时把「投稿 / 返信 / 分析」三件拆开逐项验。

## 七、红旗

- **はてなブログ等免费博客做卫星站**:用来给主站发自作自演链接,属于 Google 链接 spam 政策列举的买卖链接、过度交换链接、用自动化程序造链(【官】[Spam policies](https://developers.google.com/search/docs/essentials/spam-policies))。做法(本套件口径):用自有域名内的博客,不用卫星站方案。已删「はてなブログ SEO 势力 7 年连续走弱」(来源读不到)。
- **名称・住所・电话(NAP)不一致**:GBP、官网、食べログ三处对表,按月检查;改名搬迁先改 GBP 再同步其他(本套件口径)。
- **口コミ操作**:见 2.2。
- **AI 量産記事**:AI 臭六法則超标的批量文章,最先被摘要替代。「〇〇とは」类查询受影响的说法见 glad-cube(2026-04-01)的定性分析;其标题里的「クリック 42% 减」是 AIO 下的整体点击变化,不是「〇〇とは」类的数字,已更正(【三方】[glad-cube](https://www.glad-cube.com/insightcube/archives/904))。
- **nosnippet 误设**:会把页面退出 AIO / AI Mode 的输入;要进 AI 的页不要设(【官】[Google AI features](https://developers.google.com/search/docs/appearance/ai-features))。

## 八、ツール

| ツール | 用途 | 备注 |
|---|---|---|
| ラッコキーワード | 日语关键词扩展(サジェスト) | 免费主力 |
| パスカル | 検索ボリューム・顺位・AIO 配套 | 日本国内系 |
| GSC / Bing WMT | Google / Bing 数据 | Bing 要单独接 |
| Google キーワードプランナー | 月次検索ボリューム | 广告账号免费开 |
| GEO AIO Tracker(life-from2020,2026-05-12 公开) | 4 引擎引用定点观测 | 厂商工具,【三方】[发布稿](https://life-from2020.com/blog/geo-aio-tracker-release/) |

## 九、检查清单

| # | 检查什么 | 怎么查 | 通过判据 |
|---|---|---|---|
| 1 | 文案机检 | `python3 scripts/market_lint.py --market ja page.html --report` | CRITICAL 0;です/ます 不混;「AではなくB」≤3;营销词零命中;全角英数字不混 |
| 2 | 标题与描述长度 | `python3 scripts/site_audit.py URL --market ja` | title ≤32 全角、description ≤120 全角(本套件阈值);缺描述为 WARN |
| 3 | hreflang | `python3 scripts/hreflang_cluster.py https://site/ja/x https://site/en/x` | 簇内互指;`ja` 一个码即可 |
| 4 | AI 检索爬虫 | `python3 scripts/robots_posture.py https://site/robots.txt --json` | `visibility_failures` 为空,或封禁是记录在案的决定 |
| 5 | nosnippet | `curl -sI URL \| grep -i x-robots-tag`;`grep -i nosnippet page.html` | 想进 AIO / AI Mode 的页没有 nosnippet |
| 6 | Bing 流量 | Bing WMT;`python3 scripts/bing_wmt.py stats`(需 API key) | 桌面站有 Bing 数据;和 GSC 分开记 |
| 7 | 口コミ流程 | 看 QR/POP 文案、回复话术、激励机制 | 没有指定星级、没有激励、没有筛选导流 |
| 8 | NAP 对表 | 手工比对 GBP / 官网 / 食べログ | 三处名称、住所、电话完全一致 |
| 9 | AI 引用台账 | `python3 scripts/citation_panel.py init --brand B --prompts prompts.csv --engines chatgpt,gemini,perplexity`;每周 `record --engine chatgpt --file run.csv` | 同问句 2–3 种问法;连续 4 周才下结论 |
| 10 | llms.txt 假阳性 | `python3 scripts/llmstxt.py check https://site`,再 `curl -s https://site/llms.txt \| head -3` | 首行是 `# ` 标题,不是 HTML |

## 十、本地実測(2026-10-09,本套件记录)

- 跑了 note.com 与 www.yahoo.co.jp × `site_audit --market ja` / `llmstxt check` / `head_check`。
- note.com:title 18 全角;词数 164(列表壳页);四条 AI 检索爬虫全放行;`/llms.txt` 404;head_check 对 twitter:app: 系列报了 8 项弃用。yahoo.co.jp:title「Yahoo! JAPAN」6 全角;desc 73 全角;17 个 H1(门户首页现状);AI 检索爬虫放行;`llms.txt` 4 个路径都返回 200 但内容是 HTML 回退页(假阳性,靠人工看首行)。
- **脚本口径 2026-10-21 已改**:twitter:*(含 twitter:app:)与 OG 重复只记 INFO,不是弃用;缺 H1、缺 description 记 WARN;description 下限取 `markets.json` 的 `desc_min`(ja=60 全角),旧输出里「desc 73 全角 <80 下限 WARN」按旧下限写,已失效。全角阈值的**超限分支**至今没有在真实站上验证到正例,下次补。
- 盲区:です/ます 混检、「AではなくB」≤3、AI 臭指纹词、全角英数字有 `market_lint` 机检;「句子是否像 AI 写的」要人读。

## 維護

- 复审周期 **90 天**,下一次 **2027-01-09**;signals 清单与 `scripts/markets.json` 的 `markets.ja.review_cycle` 保持一致,以 json 为准。
- 触发即复审:Ahrefs 日本榜月更、life-from2020 新研究、消費者庁 ステマ規制执法、Google 本地搜索帮助页、StatCounter 日本月度(桌面 Bing / Google 反复)。
