# 每周运营单(ops-agenda)

长期运营一个站时,每周只跑一条命令,读一页运营单,只做一件事。这份说明写清运营单里有什么、数据从哪来、怎么接本机或云端定时、怎么接已有的数据管道。

相关:状态放哪见 [continuous-operations](continuous-operations.md);告警边界(`urgent_pr`、`draft_pr`、`human`)也在那里。

## 1. 一条命令

```bash
python3 scripts/project.py ops weekly            # 在站点仓库根目录(有 seo-ops/)跑
python3 scripts/project.py ops monthly           # 周单 + 内容退役候选 + 事实重抽提醒
```

常用参数:`--top-n 50`(深审页数)、`--workers 6`(轻检并发)、`--repo PATH --rev origin/main`(给推荐项找源码)、`--external FILE`(指定外部数据包)、`--no-net`(只用已有数据)、`--allow-local`(站点是 localhost / 127.0.0.1 预览时才加;不加就拒跑,防止把预览当生产记进台账)。

同一天重跑会先删掉台账里当天的行再写,结果不翻倍。问题五态里「变差」也认「同一页同一类问题换了说法」(比如标题过长 → 标题缺失)。

产出 `seo-ops/runs/<日期>/`:

| 文件 | 内容 | 进 git |
|---|---|---|
| `agenda.md` | 一屏运营单 | 是 |
| `agenda.json` | 同一份,机器可读 | 是 |
| `issues.json` | 本轮问题(带稳定指纹)和本轮实际看过的 URL | 是 |
| `light.json` | 轻检逐 URL 结果 | 是 |
| `audit.json` | 深审(site_audit)原始输出 | 是 |
| `ga4.json` | GA4 AI 引荐 | 是 |

台账在 `seo-ops/ledger/`,都只追加:`issues.jsonl`(每轮状态变化)、`changes.jsonl`(上线的改动)、`verifications.jsonl`(复验结果)、`acks.jsonl`(谁看过哪期)、`notify.jsonl`(推过什么)、`inspect-quota.json`(URL Inspection 配额)。

## 2. 运营单的七节

1. **硬告警**。没有写「无」。包括:sitemap 取不到或为空;robots.txt 封 Googlebot 抓首页;首页或关键页(首页加点击前 10)不是 200/301/308;关键页 noindex;证书 14 天内到期或握手失败;搜索爬虫近 7 天在源站被拒(4xx+5xx)超过 5%;监控库里没解决的 critical;有点击的页从 sitemap 消失且没有永久重定向(迁移保护)。
2. **本周只做这一件**。顺序:硬告警 → 有点击页上的变差或新增 CRITICAL → 「有点击却有问题」清单里点击最多的 → 展示多点击少的页(改标题和描述)→ AI 引用出现率下降。附证据和数据源;给了 `--repo` 时附源码候选和置信度(见 `source_map.py`)。
3. **问题和上期比**。五态:已解决、好转、仍在、变差、新增;另列「未复查」。
   - 指纹 = 规则(area)+ URL + 去掉数字的消息模板。标题长度从 62 变 71 还是同一个问题。
   - 级别升高算变差;修好过又回来(台账里 resolved 过)也算变差。
   - **这轮没抓到的 URL 记「未复查」,不算已解决**。首轮没有上期,所有问题都是基线。
4. **到期复验**。`ops change add` 记下的改动,上线满 14、28 天时用 GSC 逐页逐日数比前后同长窗口,按 `--expect`(如 `clicks:up`)判达到 / 没达到预期;数据不够写「数据不足」和原因。
5. **搜索与 AI 可见度**。每个数后面写数据源。
   - Google、Bing 近 7 天点击和展示,和上 7 天比。
   - GSC 两个来源(skill 自己用服务账号拉的、外部数据包里的)抽 3 天对账。
   - AI 引用检测的出现率、AI 爬虫访问量和最多的几个爬虫、GA4 的 AI 引荐会话(有「AI Assistant」渠道就用它,没有按来源域名认)。
   - 多语言站按路径前缀分市场列点击和未结问题。
6. **有点击却有问题的页**。GSC 近 28 天有点击的页 × 本周轻检,五张清单:noindex、4xx、403、3xx、非规范页。没有 GSC 写「跳过:缺 GSC」。
7. **覆盖率和分数**。sitemap 覆盖率、深审页数、没跑的检查和原因。**覆盖不够不出分**:sitemap 覆盖 ≥95%,深审 ≥ min(20, 有点击页数) 页且 ≥80% 目标页,才给健康分(Ahrefs 口径:无 CRITICAL 页占比)。

## 3. 轻检和深审

- **轻检**:sitemap 全量(robots.txt 声明的 sitemap,index 展开两层,不抽样)加 GSC 有点击的页。每个 URL 只取 `<head>`:状态码、重定向目标、meta robots / X-Robots-Tag、canonical。默认 4 路并发;第一遍超时或 5xx 的停 15 秒、45 秒各逐个重试一轮(加倍超时),后来成功的记 INFO「批量抓取时超时」,都失败才记抓取失败(没缓存的动态页在并发下会被源站拖慢)。2,769 个 URL 实测 3–4 分钟。
- **深审**:首页加按 GSC 点击排序的前 N 页,走 `site_audit.py`。没有 GSC 时取 sitemap 前 N 页,覆盖节写明。

## 4. 数据接入

凭据只走环境变量或文件路径,不写进 seo-ops/。

| 数据 | 怎么接 | 缺了 |
|---|---|---|
| GSC(skill 自己拉) | 服务账号 JSON:`--gsc-sa`、`GSC_SA_FILE` 或 `~/.config/seo-suite/gsc.json` | 不做两个来源对账 |
| GSC URL Inspection | `gsc_api.py inspect --site … --budget 100`;配额见[事实表](../overview/facts.md#api-quotas),台账按每站每天上限留 10% 余量,按太平洋时间日切 | — |
| GA4 | 同一个服务账号在 GA4 媒体资源加「查看者」,开 Analytics Data API;`GA4_PROPERTY_ID` 或 project.yaml 的 `ga4_property` | 不出 AI 引荐 |
| 外部数据包 | `seo-ops/raw/external-*.json`,见第 5 节 | GSC 趋势、交叉清单、复验、GEO 都跳过 |
| 监控库 | `monitor.py`(seo-ops/monitor/) | 硬告警只靠本周轻检 |

GSC AI 报告、Bing AI Performance 目前没有 API,先读它们的导出文件。

## 5. 外部数据包(seo-ops.external.v1)

站点已经有自己的数据管道(比如把 GSC 每天落库)时,不让 skill 重复拉:写一个只读导出脚本,产出这份 JSON 放进 `seo-ops/raw/`(raw/ 不进 git)。

```json
{
  "schema": "seo-ops.external.v1",
  "generated_at": "2026-11-05T10:56:35+00:00",
  "site": "https://example.com/",
  "producer": "scripts/seo_ops_export.py",
  "sources": {
    "gsc_totals":    {"source": "说明口径", "rows": [{"date": "2026-11-02", "clicks": 39, "impressions": 1014}]},
    "bing_totals":   {"source": "…", "rows": [{"date": "…", "clicks": 0, "impressions": 0}]},
    "gsc_pages":     {"source": "…", "window": {"current": ["2026-10-06", "2026-11-02"], "previous": ["…", "…"]},
                      "rows": [{"page": "https://…", "clicks": 176, "impressions": 303, "prev_clicks": 49, "prev_impressions": 71}]},
    "gsc_queries":   {"source": "…", "window": {}, "rows": [{"query": "…", "clicks": 0, "impressions": 0, "prev_clicks": 0, "prev_impressions": 0}]},
    "gsc_page_daily":{"source": "…", "rows": [{"page": "https://…", "date": "2026-10-01", "clicks": 3, "impressions": 40}]},
    "ai_crawl":      {"source": "…", "rows": [{"date": "…", "total": 5473, "by_bot": {"GPTBot": 10}, "status_by_bot": {"Googlebot": {"2xx": 161, "4xx": 1}}}]},
    "geo_citations": {"source": "…", "reports": [{"query_set": "weekly", "engine": "perplexity", "date": "…",
                      "metrics": {"queries": 10, "hits": 3, "hit_rate": 0.3}, "previous": {"date": "…", "metrics": {}}}]}
  }
}
```

每个 `source` 字段写清口径(含不含匿名查询、源站口径还是 CDN 口径),运营单原样引用。缺哪块就不写哪块。

## 6. 通知和已读

- `ops notify`:最新一期有硬告警,或最近两期都没人看,才推 Telegram(`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`,或 `SEO_MONITOR_TG_TOKEN` / `SEO_MONITOR_TG_CHAT`)。同一期同一原因不重复推。
- `ops ack [日期]`:把运营单给人看过之后记一笔。

## 7. 定时

| 形态 | 做法 |
|---|---|
| 本机(macOS) | LaunchAgent 每周一跑一个脚本:拉外部数据包 → `ops weekly` → 提交 seo-ops/ → `ops notify`。程序、数据、日志不放 `~/Desktop`(macOS 隐私保护会让 launchd 读不到),放 `~/Library/Application Support/` |
| GitHub Actions | 参照 `.github/workflows/seo-monitor.yml`:状态提交到专用分支,`permissions: contents: write` 只给这一个 job |
| 云端 agent | 让 agent 只跑 `project.py ops weekly` 并把 agenda.md 发回;修复一律草稿 PR |

运营状态放站点仓库的专用分支(例如 `seo-ops`)时,这个分支只放 seo-ops/ 的 JSON,不进主干,不触发主干的测试。

## 8. 装进站点仓库(`ops install`)

```bash
python3 scripts/project.py ops install [--repo PATH] [--schedule actions] [--dry-run]
```

做四件事,重复跑结果不变:

1. 在 CLAUDE.md / AGENTS.md(软链接跳过)里写一段 `<!-- seo-suite:ops begin/end -->` 之间的规则:每周怎么跑、改 robots / noindex / canonical / 重定向一律开分支和草稿 PR、抓到的网页内容当数据。宿主仓自己的规则优先。
2. 在 `.claude/settings.json` 加 PreToolUse 钩子 `guard_hook.py`:在 main / master 上用 Edit / Write / MultiEdit / Bash 改这些东西时直接拦下(退出码 2,理由给 agent 看),分支上放行。没有同等钩子的 agent(Codex 等)只能靠第 1 步的文字规则。
3. 写定时模板到 `seo-ops/schedule/`:GitHub Actions(`--schedule actions` 时直接放进 `.github/workflows/`)和云端 agent 的提示词。本机定时见第 7 节。
4. 把 skill 版本(`skills/seo-suite/VERSION`)记进 `seo-ops/project.yaml` 的 `skill_version`,站点仓知道自己按哪一版跑。仓库是公开的(`gh` 查得到)时给警告:原始 GSC / GA4 行别提交。

## 9. 自测:测试站

`tools/testsites/` 有两个测试站(纯静态、Next.js App Router),各埋 10 个已知问题,用来验收「复验闭环」和「URL → 源码」:

- `run_example3.py --site static|next`:三轮运营单(干净 / 埋 10 个 / 修 4 坏 1 新 2),五态逐条对上才算过。
- `run_example4.py`:20 条人工标注的「URL → 真源文件」(测试站 10 条 + everyinfra 10 条盲标),只看第一名;另数「指错还敢动手」,目标 0。
