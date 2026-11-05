# 本地网格排名(geo-grid rank tracking)

> 复核于 2026-11-05(补第五节之二 Ask Maps、第六节 Q&A API 停用)。三指标(ARP/ATRP/SoLV)源码级口径 + 网格参数公式 + 5 层审计法 + GBP 信号(官方三因素与从业者观察分开写) + API 盲区。本地业务站点结构、六行业速查与 GBP 深读见 [site-type-templates.md](../technical/site-type-templates.md);通用指标口径规范见 [kpi-definitions.md](kpi-definitions.md)。

## 用途

- 用户问「本地排名」「网格排名」「geo-grid」「ARP/ATRP/SoLV」「本地包(local pack)监控」「竞品为什么在我附近排我前面」时读本文。
- 单点排名会随搜索者位置剧烈波动,一次查询说明不了可见度。网格排名把「一个位置的排名」换成「一片区域内 N×N 个采样点的统计量」,是本地 SEO 监控的正确单位。
- 实现口径对齐 cablate/mcp-google-map 的 `localRankTracker`(Places API(新)Text Search);API 密钥与调用费用自备。ARP / ATRP / SoLV 是第三方本地排名工具的行业通用指标，不是 Google 的指标；Google 不提供「网格排名」数据。
- **官方口径（Google 商家资料帮助[《提升本地排名》](https://support.google.com/business/answer/7091)，核对 2026-10-21）**:本地结果主要取决于**相关性（relevance）、距离（distance）和知名度（prominence，帮助页正文也称 popularity）**。相关性指商家资料与搜索的匹配程度；距离指商家到搜索者的远近，搜索者不分享位置时 Google 用它所知的位置；知名度指商家有多出名，也基于有多少网站链接到你和评论数量，更多评论和好评有帮助。官方还写明:**不能申请或付费获得更好的本地排名**。

## 一、单格点排名怎么产生

每个格点独立跑一次 Text Search,再在结果里定位目标商家:

```
textQuery   = 关键词
locationBias = { lat: 格点纬度, lng: 格点经度, radius: spacing/2 }
pageSize = 20                       // maxResultCount 已被官方标为弃用，改用 pageSize（1–20）
rank = 结果数组中 findIndex(place_id === 目标place_id) + 1   // 找不到记 null
top3 = 结果前 3 名的商家名                                    // 无论目标是否命中都记录
```

- 匹配键是 **place_id**(ChIJ 开头的标识),不是商家名——同名连锁只有靠 place_id 才不串店。可以缓存复用,但官方建议超过 12 个月的 place_id 要刷新(Place Details 只请求 `id` 字段,免费);商家关闭、搬迁或地图数据库更新会让旧 ID 返回 NOT_FOUND([Place IDs](https://developers.google.com/maps/documentation/places/web-service/place-id),核对 2026-10-21)。
- `locationBias` 是**偏置不是硬过滤**:官方原话是结果可以包含指定区域之外的地点；要硬限制用 `locationRestriction`，两者不能同时用；圆形半径范围 0–50,000 m。因此格点排名≈该位置真实 Maps 搜索的近似,不是精确复刻。官方还说明:相同请求返回的列表**不保证一致**——同一格点要重复采样几次，取中位数（本套件口径）。（[Text Search (New)](https://developers.google.com/maps/documentation/places/web-service/text-search)，核对 2026-10-21）
- 每页最多 20 条:本文口径只取第一页，排在 20 名开外与根本不在结果里在格点层面无法区分，统一记 null——这是三指标里「21 惩罚」的来源。官方说 Text Search (New) 跨所有页最多返回 60 条（可能调整），需要更深的排名可用 `nextPageToken` 翻页，每多一页多一次调用费用。
- 格点坐标截断到小数点后 6 位(约 0.1 m),报告照抄,不要手动截短。

## 二、三指标公式(源码级口径)

设总格点数 `N = gridSize²`,命中点集 `H = {r : r.rank ≠ null}`,`|H|` 为命中点数:

| 指标 | 公式 | 分母 | 未命中处理 | 空值行为 |
|---|---|---|---|---|
| **ARP**(Average Rank Position) | `Σ rank(H) ÷ \|H\|`,四舍五入 1 位小数 | 仅命中点 | 排除在分子分母外 | `\|H\|=0` 时返回 null |
| **ATRP**(Average Traditional Rank Position) | `Σ (rank ?? 21) ÷ N`,1 位小数 | 全部 N 点 | **按 rank=21 计入分子** | 永不 null(除非整格报错) |
| **SoLV**(Share of Local Voice) | `count(rank ≤ 3) ÷ N × 100`,1 位小数 | 全部 N 点 | 不计入分子(拉低百分比) | 恒为 0–100 |
| found_in(辅助) | `\|H\|/N` 字符串,如 `6/9` | — | — | — |

**联合解读规则:**

- ARP 与 ATRP **必须同时报**。只报 ARP 会把「排名不错但大片区域根本找不到」美化成正常;`ATRP − ARP` 差值就是盲区面积的代理指标。
- SoLV 回答的是「进本地包(前三)的地理覆盖率」,与 ARP(进榜时排多好)是两个维度:SoLV 高 + ARP 大 = 到处能进包但排在第 3;SoLV 低 + found_in 高 = 经常上榜但守不住前三。
- 三指标全部对「排名 >20 = 缺失」不敏感:一个被挤出前 20 的点和一个被挤出前 10 的点惩罚相同,细粒度只看格点明细。
- 报告口径对齐 [kpi-definitions.md](kpi-definitions.md):每期写明公式、数据源、网格参数、关键词表、日期与地区,保证期与期可比。

**算例**(3×3=9 点, ranks = `[1,2,4,null,1,3,null,null,2]`):

- ARP = (1+2+4+1+3+2) ÷ 6 = **2.2**(只算 6 个命中点)
- ATRP = (13 + 21×3) ÷ 9 = **8.4**(3 个未命中点各按 21)
- SoLV = 5 ÷ 9 × 100 = **55.6**(rank≤3 的点:1,2,1,3,2)
- found_in = `6/9`;ATRP−ARP = 6.2 → 右下象限存在明显盲区,去格点明细定位被谁占据。

## 三、网格参数与生成公式

**默认与合法值**:gridSize 默认 3(3×3=9 点),常用 3/5/7(9/25/49 点);gridSpacing 默认 1000 m,常用区间 100–10000 m。

**格点生成**(以中心点 + 间距向四周展开):

```
half            = floor(gridSize / 2)
metersPerDegreeLat = 111320                        // 纬度度长全球近似恒定
metersPerDegreeLng = 111320 × cos(中心纬度 × π/180) // 经度度长随纬度收缩
lat(r, c) = 中心lat + (r − half) × spacing ÷ metersPerDegreeLat
lng(r, c) = 中心lng + (c − half) × spacing ÷ metersPerDegreeLng
每点搜索半径     = spacing ÷ 2                      // 相邻搜索圈恰好相接,无缝隙无重叠
```

- 经度的 cos 校正内置于公式:东京(约 35°N)附近 1° 经度 ≈ 91 km、45°N 附近（如米兰）≈ 79 km、奥斯陆(约 60°N)≈ 56 km,公式在高纬度自动收缩,网格仍是正方形(米意义上)。
- **gridSize 用奇数**:奇数保证中心点落在网格正中;偶数会因 `floor` 向一侧偏半格。
- 覆盖跨度 = `(gridSize − 1) × spacing`:3×3@1000m 覆盖 2×2 km;5×5@2000m 覆盖 8×8 km;7×7@3000m 覆盖 18×18 km。
- 每点 `radius = spacing/2` 的设计含义:每个格点「负责」一块 spacing×spacing 的方形市场,九块拼起来恰好等于网格覆盖,不重不漏。

**参数选择**(按业务的服务半径,本套件经验建议,非官方规定):

| 业务形态 | 建议 |
|---|---|
| 步行到店(餐饮/咖啡/美容) | 3×3 或 5×5,间距 500–1000 m |
| 社区服务(诊所/律所/教培) | 5×5,间距 1000–2000 m |
| 上门服务/SAB(水管工/搬家) | 5×5 或 7×7,间距 2000–5000 m |
| 都会级品牌(多中心分测) | 每个商圈中心各跑一次 5×5,不要一次 7×7@10km 糊弄 |

**成本与并发**:调用次数 = `gridSize² × 关键词数`(源码并发 5 批处理)。25 点 × 10 词 = 250 次 Text Search,计费与限流按此预估;关键词多时先筛后扫。

**复测可比性铁律**:期与期之间中心、gridSize、spacing、关键词表、语言/地区参数任一变化都不可比。把网格参数写进每期报告头;对比默认「年同比优先于环比」(本地搜索季节性强)。

## 四、5 层分析法(审计全流程)

排名三因子:**距离(固定)+ 相关性 + 知名度**。距离改不了,审计的只是后两者。

### Layer 1 — 关键词版图
搜 `{关键词} {区域}` 看谁在排、品类大词与长尾各是什么生态:
- 主词、次词、`{品类} near {地址}`(近邻竞品)、英文/其他语言词各扫一遍。
- 产出:带 place_id 的竞品清单,供下层深挖。

### Layer 2 — 竞品深挖
对 top 竞品逐个比对信号:评分+评论数(知名度)、主/次类目(相关性)、网站/电话/营业时间(完整度)、照片数、评论正文关键词。
- **从业者观察**（非官方）:主类目决定露出词面——「日式餐厅」与泛「餐厅」排名面不同;次类目加广度。官方只说类目要准确（"What kind of business you are"）。
- 全新客户完整审计约 8–10 次调用:L1 三搜 → compare/details 1–2 次 → 区域分析 1–2 次 → 静态地图 1 次。

### Layer 3 — 缺口分析
目标 vs 头部竞品逐信号对表:

| 信号 | 检查 | 未达标的修法 |
|---|---|---|
| 主类目 | 对准最高流量词? | 换更准的主类目(从业者观察认为影响很大;官方只要求准确) |
| 评论数 | ≥ 头部竞品的 80%?（本套件经验阈值） | 评论征集活动(注意合规红线,见六行业速查) |
| 评分 | ≥ 4.2?（本套件经验阈值） | 处理负评根因 |
| 照片 | ≥ 10 张?含门面/内景/菜单?（本套件经验阈值） | 补传 |
| 网站 | 有链接? | 补 |
| 营业时间 | 准确+特别时段? | 更正 |
| 菜单/服务项 | 命名可被搜索匹配? | 用搜索词命名 |

- **从业者洞察**:菜单/服务名必须用顾客搜的词。卖「半熟蛋」却写成「大太阳」,算法无法把查询匹配到你。

### Layer 4 — 区域密度与机会
对候选区域按类型数商户密度+平均分:
- 高密度 + 低均分 = 机会(竞品都弱);低密度 = 蓝海;高密度 + 高均分 = 红海(差异化或放弃)。
- 选址侦察 4 次调用:explore_area → nearby 2km 明细 → distance_matrix 通勤可达性 → static_map 密度图。

### Layer 5 — 监控快照
记录当前排位作基线(本文网格三指标即为此层的数据化),**按月复测**同口径,跟踪移动。
- 老客户快检 2 次调用:一次搜索定位 + 一次 details 信号快照。

**已知边界**:`search_nearby` 的 keyword 不支持中文类目名(如「日式餐廳」)——用英文 type(`japanese_restaurant`)或改走 `search_places`/`explore_area`,它们能正确处理中文查询。

## 五、GBP 信号表

**官方说法**（[提升本地排名](https://support.google.com/business/answer/7091)，核对 2026-10-21）:验证商家；保持信息完整准确（地址、营业时间含特别营业时间、商家类型、停车和 Wi-Fi 等属性）；回复评论；添加照片和视频；零售商家可添加店内商品。Google 不公布各因素的权重。下表的「权重」是**从业者测试的观察级判断，不是官方排序**，只用于排查优先级:

| 信号 | 权重 | API 查法 |
|---|---|---|
| 主类目 | 高 | `place_details` → types |
| 评论数 | 高 | `place_details` → user_ratings_total |
| 平均评分 | 高 | `place_details` → rating |
| 评论正文关键词 | 高 | `place_details` → reviews 文本 |
| 照片数与质量 | 中 | `place_details` → photo_count |
| 资料完整度(网站/电话/时间) | 中 | `place_details` 对应字段 |
| 菜单/服务项 | 中(行业相关) | `place_details` → 是否存在 |
| 评价回复率 | 中 | API 不可直接见 |
| 外部引用(博客/新闻) | 中 | Maps API 不可见 |
| NAP 一致性 | 中 | `place_details` 跨源核对 |
| Google Posts 活跃度 | 低 | API 不可见 |

AI 检索补充:各 AI 平台怎么选本地商家，官方没有逐平台的说明，本套件不写成规则；证据分级见 [geo-evidence](../content/geo-evidence.md)。Google 的 AI 功能与整体搜索共用商家资料，官方建议保持 Merchant Center 与商家资料信息最新（[AI 功能说明](https://developers.google.com/search/docs/appearance/ai-features)）。Bing Places、Apple Maps 是各自独立的商家资料，需要分别认领。

## 五之二、Ask Maps:地图里的对话式答案(核对 2026-11-05)

- **是什么**:Google 地图里的「Ask Maps」按钮,用 Gemini 模型回答复杂的地点问题(例如「现在哪能充电、不用排长队」「今晚哪有开灯的公共网球场」),给出定制地图、路线和来自贡献者的「insider tips」,能直接订位、存列表、分享。2026-03-12 先在美国和印度的 Android、iOS 推出,桌面版随后;官方说它分析 3 亿多个地点和 5 亿多贡献者的评价,并按用户在地图里搜索、保存过的地点做个性化([blog.google 2026-03-12](https://blog.google/products-and-platforms/products/maps/ask-maps-immersive-navigation/))。
- **2026-08-06 扩展**:澳大利亚、巴西、加拿大、印度尼西亚、日本、墨西哥,外加 150 多个国家和地区的英语版;美国先上线代点外卖(合作方 Square、Toast,Uber Eats 随后,并和伙伴共建 UCP for Food)、酒店比价、活动发现,以及用对话提交地点修改(拍招牌识别新营业时间,用户确认后提交)([blog.google 2026-08-06](https://blog.google/products-and-platforms/products/maps/order-food-in-ask-maps/))。
- **对本地 SEO 的含义**(本套件口径,官方没有说 Ask Maps 怎么选商家):
  1. 回答依赖评价正文、贡献者提示和商家资料属性里的细节(「安静」「有灯」「后面有停车位」)。资料属性填全、鼓励顾客在评价里写具体场景,比堆关键词有用。
  2. 回答是个性化的,网格排名(第一至三节)测不到 Ask Maps 的推荐;报告里把它列为盲区,不拿网格 SoLV 代替。
  3. 餐饮商家:代点外卖走 Square、Toast 等合作方,没接入的店在 Ask Maps 里只能被推荐、不能被直接下单。
  4. 营业时间可能被用户拍照修改并提交,商家要定期看资料里的「Google 更新」并确认。
- **怎么观察**:没有官方报表。用目标城市的真实问题在 Ask Maps 里手工抽样,记录是否被推荐、引用了哪条评价或属性;样本纪律同 [ai-citation-patterns.md](../content/ai-citation-patterns.md)。

## 六、数据盲区清单

**Places API / Maps API 拿不到**的数据，报告里明说「不可测」，不要拿代理指标冒充:

1. 搜索关键词的展示量、商家资料浏览量分解;
2. 直接搜索 vs 发现式搜索的比例;
3. 本地 3-Pack 出现率（只能用网格 SoLV 近似）;
4. 评价回复率、外部引用、Google Posts 活跃度（上表已标）;
5. Ask Maps 的对话式推荐(见五之二):个性化,网格测不到;
6. 商家资料的问答(Q&A):My Business Q&A API 2025-11-03 已停用,不能再用 API 读写问答,相关的 `NEW_QUESTION` 等通知类型也一并废弃;官方说正在更新问答的功能和体验([Q&A API 变更日志](https://developers.google.com/my-business/content/qanda/change-log),核对 2026-11-05)。审计不再取 Q&A 数据,常见问题写进网站和商家描述;
7. 网格工具自身盲区:`locationBias` 是偏置非过滤;排名 >20 与未收录不可区分（可翻页到 60）;单次扫描只覆盖一种语言 / 设备 / 个性化条件;`search_nearby` 的 keyword 对中文类目名不支持（cablate 工具的行为，不是 Google 规定）。

**商家自己能拿到**的数据:用商家的 OAuth（scope `business.manage`）调 [Business Profile Performance API](https://developers.google.com/my-business/reference/performance/rest/v1/DailyMetric)（核对 2026-10-21），可以按日取 Google 搜索和地图 × 桌面 / 移动的商家展示（同一用户一天内多次只算一次）、通话点击、网站点击、路线请求、消息点击、预订和订餐，另有按月的搜索关键词展示。这类数据只有商家资料的所有者或管理者能取，不在 Places API 里。

## 七、反模式 7 条

| # | 反模式 | 症状 | 修法 |
|---|---|---|---|
| 1 | 商家名堆关键词 | 「台北最好吃牛肉麵-王記牛肉麵」 | 用真实商家名;关键词放评论/菜单 |
| 2 | 忽略次类目 | 只设一个类目 | 补相关次类目 |
| 3 | 菜单用创意命名 | 名字没人搜 | 用与查询匹配的可搜索命名 |
| 4 | 照片荒漠 | 0–3 张照片 | 传 10+(门面/内景/菜品/团队) |
| 5 | 不回评价 | 大量评价零回复 | 全部回复(影响活跃分) |
| 6 | 主类目选错 | 该「日式餐廳」选了泛「餐廳」(或反之) | 对准最高价值关键词定位 |
| 7 | 对错口径 | 拿夏季比冬季数据 | 年同比同口径对比 |

## 八、审计输出模板

```markdown
# 本地网格排名审计 — {商家名}({place_id})
- 日期:{YYYY-MM-DD} | 中心:{lat,lng} | 网格:{gridSize}×{gridSize} @ {spacing}m
- 关键词:{n} 个(列表附后) | 调用:{gridSize²×n} 次 Text Search | 上一期:{日期}

## 1. 指标总表
| 关键词 | ARP | ATRP | ATRP−ARP | SoLV % | found_in | 环比 |
|---|---|---|---|---|---|---|
| {kw} | 2.2 | 8.4 | 6.2 | 55.6 | 6/9 | ↑/↓/— |

## 2. 盲区定位
(ATRP−ARP 最大或 found_in 最低的词;指向格点象限/街区,列该象限 top3 占据者)

## 3. 竞品对照(top3 占据者)
| 竞品 | 主类目 | 评分 | 评论数 | 照片数 | 网站/电话/时间齐全 | 对目标差距 |

## 4. 信号缺口清单(Layer 3 checklist)
| 信号 | 阈值 | 目标现状 | 命中? | 行动 |

## 5. 行动项(按杠杆排序:主类目 > 评论 > 照片 > 完整度)
1. {行动 / 负责人 / 预期影响的指标与格点区域}

## 6. 复测口径
同中心/同网格/同间距/同词表/同语言,未命中按 21 计;年同比优先。
```
## 检查清单

| 检查什么 | 怎么查 | 通过 / 失败 |
|---|---|---|
| 三指标算对 | 准备 CSV，列为 `keyword,grid_point,rank`（未找到留空），运行 `python3 scripts/grid_rank.py rank_data.csv --detail`；加 `--json` 得结构化输出 | 与第二节算例一致：9 点 `[1,2,4,空,1,3,空,空,2]` 得 ARP 2.2、ATRP 8.4、SoLV 55.6、found_in 6/9 |
| 同一格点采样稳定 | 同一格点、同一词重复查询 3 次（官方说结果不保证一致） | 三次中位数相同或相差 ≤1 名才入表（本套件口径）；否则记为不稳定点 |
| 期与期可比 | 中心点、gridSize、spacing、词表、语言 / 地区参数写进报告头 | 任一项变化 = 不可比，重建基线 |
| 网格间距与覆盖匹配服务范围 | 覆盖跨度 = (gridSize − 1) × spacing；对照业务服务半径 | 覆盖不到主要客户来源区 = 加大间距或增加中心点 |
| place_id 有效 | Place Details 只请求 `id` 字段（免费）；超过 12 个月的重刷 | 返回 NOT_FOUND = 商家已变化，重新搜索 |
| 官方三因素对账 | 对照商家资料帮助页的「验证 / 信息完整 / 评论 / 照片」逐项 | 未验证、信息缺项优先补；其余权重无官方依据，只作排查线索 |
| 商家自有指标 | 用 Performance API 取展示 / 通话 / 网站 / 路线，与网格 SoLV 趋势对照 | 两者同向才下结论；背离先查采样条件 |

## 来源

本文由 EveryInfra 改写吸收,保留口径与结构,未复制原文。

- 一手实现:[cablate/mcp-google-map · src/services/PlacesSearcher.ts](https://github.com/cablate/mcp-google-map)(`localRankTracker`/`scanKeywordGrid`:网格生成、并发、三指标)
- 同仓:`skills/google-maps-local-seo/references/local-seo.md`(5 层分析法、GBP 信号权重、反模式、行业笔记)
- 同仓:`.agents/skills/project-docs/references/geo-domain-knowledge.md`(坐标系、经度随纬度收缩、place_id 稳定性、精度表)
