# 韩语市场专项(ko)

> **定位**:ko 市场的增量情报层。数值型规则(title/desc 全角阈值 30/80、敬语统一、연관채널 sameAs 域名清单、PIPA 等)在 `scripts/markets.json` 的 `markets.ko`;技术收录规范全文在 [technical/naver-searchadvisor.md](../technical/naver-searchadvisor.md)。本文件只写:**多口径份额、Naver 独家渠道、2026 年新变量(AI 브리핑 / 메이트 / 별점 부활)**。
> 2026-10-21 逐条重核:数字回到原始页面或官方公告读过;读不到的删除或降级。标注:【官】=官方公告或帮助页;【三方】=第三方研究或媒体(写机构、时间);【本套件口径】=本套件约定。断言半衰期 6–12 个月。
> 提问对齐见 [question-alignment.md](../content/question-alignment.md);句子写法见 [asd-ste100-web-writing.md](../content/asd-ste100-web-writing.md)。

## 一、引擎格局:四个口径,不能互换

| 口径 | 读数 | 它到底量什么 |
|---|---|---|
| 인터넷트렌드(BizSpring)搜索**来路构成** | 2025 年 Naver 均值 62.86%(2024 年 58.14%);2026-04 Naver 62.6% / Google 30.0%;2026 上半年 Naver 64.39% / Google 28.27%;2026-09 Naver 66.8% / Google 27.6% | 装了其分析代码的站点,收到的搜索来路比例(【三方】[Yonhap 2026-01-02](https://www.yna.co.kr/view/AKR20260102129700017)、[2026-04 页](https://internettrend.co.kr/insights/2026-04-search-engine)、[月度汇总](https://internettrend.co.kr/insights/topic/search-engine)、[引用案例](https://internettrend.co.kr/citations)) |
| StatCounter 页面浏览 | 2026-10 全设备 Google 48.64% / Naver 42.10%(CSV,取数 2026-11-05);2026-09 全设备 Google 47.97% / Naver 43.06%(CSV 导出 47.97 / 43.05,取数 2026-10-24);桌面 Google 62.5% / Naver 23.31%;移动 Naver 59.56% / Google 35.77% | 样本里的搜索引擎页面浏览(【三方】[StatCounter 韩国](https://gs.statcounter.com/search-engine-market-share/all/south-korea),取数 2026-10-21) |
| 应用 MAU(IGAWorks Mobile Index) | 2026-07 应用 MAU:Google 4,702 万、Naver 4,684 万,Google 首次超过 Naver | 手机应用的月活,不是搜索次数(【三方】经 Chosun 报道,转引自 [wiztheplanning](https://wiztheplanning.com/guide/naver-google-share),原报道未读) |
| 使用率调查(Nasmedia 类) | 「最近 3 个月使用 Naver」85.3% → 81.6%(调查期 2025 年内)| 受访者自报使用过,不是份额(【三方】[aimatters 2026-01-27](https://aimatters.co.kr/news-report/ai-report/37299/)) |

- 为什么差这么多:来路构成偏向有分析代码的商业站点,页面浏览偏向桌面与 Google 强势的场景,MAU 看应用。**不要把任何一个当「韩国搜索份额」**。预算看自己站点的来源报表(Naver 与 Google 分开)。
- 原先写的「2026-08 Google MAU 首超 Naver」改为 2026-07 的 MAU(2026-08 见报);「搜索行为份额(인터넷트렌드 实测面板)」改为「搜索来路构成」,这个口径本来就不是搜索行为份额。
- Google AI Overviews 在韩国可用,语言含韩语(【官】[Google 帮助中心](https://support.google.com/websearch/answer/14901683?hl=en),核对 2026-10-21)。
- **AI 브리핑**:2025-03-24 Naver 官方博客宣布开放,2025-03-27 上线(【官】[Naver 검색 블로그](https://blog.naver.com/naver_search/223807628464))。原先写的「2024-10 上线」不对。月独立用户 3,000 万(【官】[Naver 광고주센터 2026-06-15](https://ads.naver.com/notice/31888))。覆盖:Naver 称到 2025-12 约占全部搜索结果的 20%(【三方】[KB Think 2026-04-16](https://kbthink.com/news-list/view.html?newsId=20260416075553646) 引 Naver);「1% 扩到 20%」的起点数字没有来源,已删。2026 年已更新 9 次(截至 2026-03,【三方】[머니투데이 2026-03-26](https://www.mt.co.kr/tech/2026/03/26/2026032609121170661))。
- **AI 광고**:Naver 광고주센터 2026-06-15 公告:광고주센터 2026-07-15 开放,노출 2026-07-21 开放;对象是통합검색的 AI 브리핑独立区域(【官】[公告](https://ads.naver.com/notice/31888))。含义:自然引用和广告同屏。
- AI탭「单月一度冲 80%」找不到来源,已删。
- 통합검색结构 = 서비스 영역(VIEW/블로그/카페/플레이스/쇼핑/지식iN 等)+ 웹문서;Search Advisor 报表只计웹문서(本套件口径,以 Search Advisor 报表说明为准)。外部自建域名走웹문서;블로그/카페/플레이스/스마트스토어走서비스 영역。同一关键词两类宿主同屏竞争,常需双宿主布局(本套件口径)。
- Daum:原先写「Daum 搜索 = Google 索引」,只找到 Kakao 的旧稿「Daum 与 Google 合作」,现状未核,已删。StatCounter 桌面 Daum 1.61%。

**사업 유형별 주력 채널**(本套件口径,进入顺序):

| 사업 유형 | 1순위 | 2순위 |
|---|---|---|
| 이커머스(제품) | 스마트스토어 | 블로그 리뷰형 콘텐츠 |
| 로컬(매장) | 플레이스(저장·방문자 리뷰) | 블로그 지도 삽입 |
| 콘텐츠/미디어 | 블로그 + 자사 도메인 웹문서 | 카페 |
| B2B/SaaS | 자사 도메인 웹문서 + 연관채널 markup | 지식iN |

## 二、独家渠道

### 2.1 네이버 블로그(业界经验,非官方)

下列都是业界说法,Naver 官方没有披露算法。数字类的精确值(发布时刻、图片张数、字数)找不到来源,已删,保留方向:

- **「C-Rank」「NS-Rank」是业界用语**,Naver 官方文档不收录,引用必须标「비공식」。官方能查的是 Search Advisor 的诊断报告。
- 内容充实度比字数重要;堆字数、盗图、重复发布会拉低质量(业界说法)。
- 自动互邻、评论宏、反复编辑后重发,属于 Naver 垃圾内容类型(见 6 节)。
- 第一段放重搜关键词和结论,有助于摘要和 AI 브리핑 取用(本套件口径)。
- 本地关键词文章里插入地图/플레이스 链接,把블로그与플레이스信号连起来(本套件口径)。
- 周流程(本套件口径):关键词双形(带空格/不带)→ 看前 20 篇的结构 → 写 → 24 小时内查排名 → 没效果改标题或首段,不频繁改正文。

### 2.2 스마트스토어

- 노출 순위由 **적합도 / 인기도 / 신뢰도** 三个维度构成,每个维度下有若干细项(【三方】[아이템스쿨](https://school.itemscout.io/article/seo-strategy-1),转引 Naver 쇼핑图表)。原先写的「2022-06 发布 / 2022-09 适用」「旧 조회수·리뷰수·판매량直接排名废止」找不到原始公告,已删日期。
- 「9 信号」是业界拆法(本套件口径):상품명 키워드 적합도、카테고리 정확도、상세정보 충실도、판매가 경쟁력、최근 판매·추세、리뷰·평점·최신성、찜·재구매、재고·배송 조건、판매자 신뢰도。
- 2026-08-05 起 굿서비스 점수被计入「몰 신뢰도」(【三方】[i-boss 2026-08-04](https://www.i-boss.co.kr/ab-6141-71441),原文被拦未读,仅搜索摘要)。
- 상품명写法:핵심 키워드 → 속성;避免「최저가」「100%」这类不可证实的表述(本套件口径)。

### 2.3 플레이스

- 리뷰·저장·정보 완성도是常见经验因素(业界说法);Naver 没公布公式。「필요 저장량按 월검색량 역산」的公式是业界说法,不要对客户当事实。
- **별점 부활**:2026-04-06 起新的 방문 내역可以打별점;2026-07-09 起公开업체 평균 별점(之前 3 个月内部观察期);리뷰 内容与별점只能在写后 **3 个月内**修改(【官】[Naver Corp 新闻稿 2026-06-01](https://www.navercorp.com/media/pressReleasesDetail?seq=10034317)、[Naver 帮助](https://help.naver.com/service/30026/contents/20497?lang=ko)、[Yonhap](https://www.yna.co.kr/view/AKR20260601074700017))。2026-04-06 之前生成的方문 내역写的评价没有별점。
- 별점条款双刃(【官】新闻稿):개정된 이용정책禁止「부가적 또는 합리적인 설명 없이 무분별하게 3점 미만의 별점을 부여」与损害 리뷰 公正性的行为。运营端别诱导全员好评,差评留客观证据(本套件口径)。

### 2.4 카페·지식iN·VIEW

- 카페:公开게시판内容可被통합검색收录;登记数量与转化是另一件事(本套件口径)。
- 지식iN:질문형 쿼리强;专家回答可用연관채널 markup 连到自家域名(本套件口径)。
- VIEW:个性化(스마트블록)介入,账号间结果不同,排名报告用无登录/无痕窗口测(本套件口径)。
- 치지직:在연관채널 sameAs 官方域名清单内(`markets.json` entity_sources)。

### 2.5 Tistory 外域半边(杠杆位,2026-10-11,本套件口径)

- Tistory 在 Naver 연관채널 官方识别域名清单内(见 [technical/naver-searchadvisor.md](../technical/naver-searchadvisor.md))。外域自有域的博客半边可以落 Tistory。
- 分工:Naver Blog 养生态内信号(서비스 영역);Tistory 做外域웹문서半边。
- 「AI 引用 ~70% 来自博客/카페 UGC」:Nasmedia 2026-06-16 的文章标题写「AI 브리핑 引用内容 70% 是 UGC」(【三方】[Nasmedia](https://blog.nasmedia.co.kr/entry/2606naspick)),方法未读,只作方向。判据:平台在引用池内 + 竞争密度低 + 官方图谱承认,每季复核。

## 三、语言机制:敬语与语域(本套件口径)

- **文体分层**:`합니다体`(B2B/金融/公式)> `해요体`(购物·亲切)> `하십시오体`(公文)> `반말`(社区)。全站统一,混用是 lint 红旗(market_lint 敬语混用检查)。
- 검색 키워드是名词型、无敬语;标题关键词与正文语域分离。
- 어휘层:汉字语 / 固有语 / 外来语检索量不同("구매" ↔ "사기"),两形都查。
- 띄어쓰기:"자동차보험" ↔ "자동차 보험"两形都有量,关键词工具双查。
- 지역 키워드:"홍대 맛집""강남 피부과"——地区 + 业种是本地搜索主流形态。
- 外来语표기법(국립국어원)、「서비스/소개」等规范化:公共·金融文档遵守。
- 句长:`sentence_ideal` 15–25 단어;韩文句子过长(50 字以上)时一句一信息(本套件口径)。

## 四、AI 인용수 公开侦察(메이트)

- **AI 브리핑 인용수**:内容被 AI 브리핑 作为出处引用的次数,自 2026-01 起累计;2026-06-04 起在各服务频道主页的 프로필 显示(默认仅本人可见)(【官】[Naver 블로그 메이트 公告 2026-06-04](https://m.blog.naver.com/blogpeople/224306111510))。
- **네이버 메이트**(1기 2026-06 起):按 AI 브리핑 인용수为中心选拔;入选者的内容在검색 결과与 AI 브리핑中展示엠블럼与인용수(【官】[메이트 고객센터](https://help.naver.com/service/30056/contents/25217?lang=ko));报道称入选者有奖励金(【三方】[Daum 报道 2026-06-25](https://v.daum.net/v/Bgn6c6LxHF),金额与条件未核)。
- 公开基准点(【三方】[커넥터스 2026-06-04](https://contents.premium.naver.com/connectx/us/contents/260604142449283sm)):커넥터스 累计 435 万、2026-04 单月 103 万,是프리미엄콘텐츠里인용수第一;第一名订阅频道的累计只有 41 万。用作量级上界参照。
- 公开竞调(本套件口径):① 找 메이트 엠블럼频道;② 用上面的基准点校准量级;③ 自家频道프로필直查,月度记录(`citation_panel.py`);④ 对齐 Naver 创作指南,「先赢 SERP 再赢引用」。
- 测量注意:인용수是频道累计,页面级不可拆;他人 비공개 数不可爬;AI 광고 2026-07-21 上线后出处栏构成会变,基线要断代。

| 주기 | 액션 | 도구 |
|---|---|---|
| 주간 | 自家频道프로필인용수记录;메이트频道扫描 | `citation_panel.py record` |
| 월간 | 인용수 diff + SERP 前 30 变动交叉 | `citation_panel.py diff` / `report` |
| 분기 | AI 브리핑 출처 도메인构成重查(광고 후变曲点) | 手工面板 + `fanout_analysis.py` |

## 五、Yeti 收录细节(规范全文见 technical/naver-searchadvisor.md)

下面几条回到 Naver 官方页面核过:

- **IndexNow**:一次 POST 的 URL 数上限同协议([事实表](../overview/facts.md#indexnow-batch);【官】[페이지 갱신 요청하기](https://searchadvisor.naver.com/guide/indexnow-request));总请求数无限制,短时间大量请求时会限流(【官】[IndexNow FAQ](https://searchadvisor.naver.com/guide/indexnow-faq))。
- **수집요청 API(제휴)**:合作方式提交的 URL,在全网抓取队列中优先级「相对更高」(【官】[수집요청 API](https://searchadvisor.naver.com/guide/crawl-request-api))。「单次 ≤1,000 URL」本次未在页面读到,以官方页为准。
- **robots 元标签 `nosourceinfo`**:官方原文只写「使用 nosourceinfo 时,该站点不提供 AI 自动生成的**출처설명**」(【官】[선호 URL 및 로봇 메타 태그](https://searchadvisor.naver.com/guide/markup-structure))。它能不能让页面退出 AI 브리핑 引用,文档没写。原先写的「全球唯一官方 AI 引用退出 meta」不成立(Google 有 nosnippet、Google-Extended 等),已改;要退出引用先小范围测。
- **垃圾内容**(【官】[웹 콘텐츠 스팸사례](https://searchadvisor.naver.com/guide/content-abusing)):「低质量内容大量生成」指为占据结果,用相同或相似模板大量发布(改几个句子的页面数十个以上);页面写明 AI 或自动化程序可能涉及,但「不以是否使用某项技术本身为判断」。被判垃圾的站点或文档可能被排除或降权。
- Yeti 真伪验证用 rDNS + 正查;不要按 IP 封禁(本套件口径,详见规范文件)。其余项(robots 5xx、sitemap 与 RSS 分工、채용정보/동영상 제휴)以 technical/naver-searchadvisor.md 为准,本次未重读。

**외부 도메인 수용 6단계**(本套件口径):① Search Advisor 가입 + 소유확인(host 单位);② robots.txt 确认没挡 Yeti,监控 5xx;③ sitemap + RSS 提交;④ 웹문서 수집요청投代表 URL;⑤ IndexNow key 发行后推增量(≤10,000/次);⑥ `site:` 检查索引 + 사이트 진단 리포트(约 1 周后有数据)。

## 六、红旗

- **体验团/리뷰 이벤트与「뒷광고」**:공정위《추천·보증 등에 관한 표시·광고 심사지침》要求推荐者有经济利益时标示经济利益(【官】[공정위 2026-05-29](https://www.ftc.go.kr/www/selectBbsNttView.do?bordCd=3&key=12&nttSn=47547&pageIndex=1&pageUnit=10&searchCnd=all&searchCtgry=01%2C02))。该指南 2026-06-01 起修订施行:AI 生成的虚拟人物推荐须标示「虚拟人物」;블로그·카페等文字媒体要在标题或开头标示(例「AI를 기반으로 생성된 가상인물이 포함된 게시물입니다.」)。未标示可能构成不当表示广告。原先写的「스텔스 마케팅规制 2023 年强化」没有找到对应官方文件,已删。
- **플레이스 리뷰 조작**:用图片编辑或 AI 工具伪造收据、伪造预约来发评价,属于조작;Naver 对此「사전탐지·사후모니터링」后不显示该评价(【官】[공지 714](https://new.smartplace.naver.com/notices/714)、[업체 단위 페널티](https://help.naver.com/service/30026/contents/25089?lang=ko))。2026-01 起,确认异常行为时,包括已有评价在内的**所有评价一周内不显示**,重复则更久(【三方】[Yonhap 2026-01-28](https://www.yna.co.kr/view/AKR20260128137600017))。原先写的「1 次即不可逆制裁」「리뷰 탭 폐쇄」找不到来源,已改。
- **GPS 방문 인증**:방문 인증有 GPS、收据、卡片三条路径(本套件口径,以 Naver 帮助为准);伪造位置属同类滥用。
- **매크로·조작**:自动互邻/评论交换是垃圾内容;AI 参与本身不单独判定,按模板化大量发布判(见第五节)。
- **리뷰 3 개월 수정제한**:负面评价要在窗口内响应(사장님 답글 / 신고),过窗后内容与별점锁定。
- 클로킹·링크 스팸·关键词重复等通用类型 Naver 同样处理,整改后可申请重新审核(本套件口径)。

**三级红线速查**(本套件口径):

| 등급 | 항목 | 처리 |
|---|---|---|
| 완전 금지 | 伪造收据/GPS/评论宏/付费或实物换评论 | 拒绝 |
| 조건부 | 블로그 체험단·서포터즈(经济利益明示)/저장 유도 QR | 표기 문구·계약서 검수 후 진행 |
| 허용 | 지도 삽입/자연 공감·이웃/정보 완성도/공식 출처 링크 | 권장 |

## 七、工具

| 도구 | 용도 | 비고 |
|---|---|---|
| 네이버 데이터랩 | 검색량 트렌드、쇼핑인사이트 | 官方,免费+登录 |
| 네이버 광고 키워드 도구 | 월 검색량 | 광고 계정免费开 |
| 블랙키위 / 아이템스카우트 / 셀러마스터 / 판다랭크 | 关键词、发布量、스마트스토어分析 | 第三方,功能以各自官网为准,未逐一核 |
| Search Advisor | 웹문서 수집·노출 리포트、robots、sitemap、IndexNow | 见规范文件 |
| GSC + Bing WMT | Google / Bing 口径 | Naver 无法替代外部域名诊断 |

「pazarus」本次也没能独立核实,已从工具表删除。

## 八、检查清单

| # | 检查什么 | 怎么查 | 通过判据 |
|---|---|---|---|
| 1 | Yeti 可抓 | `curl -sI https://site/robots.txt`;`python3 scripts/robots_posture.py https://site/robots.txt --json`;Search Advisor 的 robots.txt 检查与抓取诊断 | robots.txt 返回 200(5xx 会被视为整站禁抓,见规范文件);没有对 Yeti 的 Disallow;apex 与 www 各自检查 |
| 2 | 收录提交 | Search Advisor 提交 sitemap + 웹문서 수집요청;IndexNow:`python3 scripts/indexnow.py key --out DIR`,`python3 scripts/indexnow.py submit --host site --key K --urls urls.txt --endpoint naver` | 提交成功(200/202);每批 ≤10,000 URL;`site:` 能查到 |
| 3 | 연관채널 markup | `curl -s URL \| grep -i "sameAs"`;`python3 scripts/schema_lint.py URL` | sameAs 里是官方域名清单内的频道 |
| 4 | nosourceinfo 决策 | `grep -i "nosourceinfo" page.html` | 有没有设都有记录;设了之后抽测是否仍被 AI 브리핑 引用 |
| 5 | 文案机检 | `python3 scripts/market_lint.py --market ko page.html --report` | CRITICAL 0;합니다体统一;과/와 助词搭配正确 |
| 6 | 标题与描述宽度 | `python3 scripts/site_audit.py URL --market ko` | title ≤30 全角、description ≤80 全角(本套件阈值);缺描述为 WARN |
| 7 | 리뷰 流程 | 看 QR/POP、回复话术、激励 | 没有付费或实物换评论;体验团有经济利益标示,文字媒体在标题或开头 |
| 8 | AI 인용수 台账 | `python3 scripts/citation_panel.py init --brand B --prompts prompts.csv --engines naver,google`;每月 `record` | 同一问句、同一环境逐月可比;광고 上线前后分段 |
| 9 | 双宿主 | 同一关键词在웹문서与서비스 영역各查一次 | 记录各自占位,别混口径 |

## 九、本地実測(2026-10-09,本套件记录;2026-10-21 抽查)

- 跑了 www.naver.com 与 www.tistory.com × `site_audit --market ko` / `llmstxt check` / `head_check`。
- naver.com:title「NAVER」3 全角;robots.txt 全文只有 `User-agent: *`、`Disallow: /`、`Allow : /$`、`Allow : /.well-known/privacy-sandbox-attestations.json`(2026-10-21 复查一致):首页以外对所有爬虫整站关门,含 Googlebot 和 Yeti。Naver 的索引靠 Search Advisor 提交,门户自身不做被爬对象。四条 AI 检索爬虫的 CRITICAL 是真的。
- tistory.com:title「티스토리」4 全角;`/robots.txt` 返回 404(2026-10-21);head_check 旧口径报了 twitter:* 弃用。
- **脚本口径 2026-10-21 已改**:twitter:*(含 OG 重复)只记 INFO,不是弃用;x-ua-compatible 记「可删旧标签」INFO;元素顺序只记风格 INFO;`site_audit` 缺 H1、缺 description 记 WARN;description 下限取 `markets.json` 的 `desc_min`(ko=40 全角),旧记录里「desc 29 全角 <80 下限 WARN」「下限 20/80 过严」已失效。`Disallow: /?` 误判已修(见 ru.md 第八节),真禁(naver 的整站 Disallow)与误判现在能区分。
- 盲区:nosourceinfo、연관채널 markup、AI 브리핑 标签-值网格等 ko 专属项不在工具覆盖内;coupang.com 对 stdlib UA 返回 403,韩国电商审计需浏览器口径。

## 維護

- 复审周期 **90 天**,下一次 **2027-01-09**;signals 清单与 `scripts/markets.json` 的 `markets.ko.review_cycle` 保持一致,以 json 为准。
- 触发即复审:Naver 公式블로그/공지(검색·콘텐츠 정책)、Search Advisor 공지(수집/색인/IndexNow)、AI 브리핑 인용 조건·별점·메이트 인용수 公告、공정위 심사지침、naver.com robots 政策变化、인터넷트렌드 月度与 StatCounter 韩国月度(口径分开记)。
