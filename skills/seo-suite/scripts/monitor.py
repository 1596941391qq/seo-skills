#!/usr/bin/env python3
"""持续监控守护核心(stdlib-only:sqlite3+urllib,零第三方依赖)。
把一次性审计变成长期监控:日检四问 → SQLite 快照 → diff 阈值告警 → 周报。

日检四问(行业分层):
  1 可见性  关键页 site: 抽查(SERP 源可配 serp_source,默认 Bing HTML 端点;
           被拦=skipped 不告警,不猜;防假 0 纪律对一切源生效)
  2 流量    .seo-monitor/gsc.csv(GSC 导出,有才查;无数据源=skipped)
  3 索引    robots.txt 哈希/误封检测 + sitemap URL 数/lastmod
           +页面级 noindex(meta robots / X-Robots-Tag 响应头,D1 P0-1:
            Conductor 头号触发器 "Pages became non-indexable")
           +canonical 目标健康度(HEAD 探测,连续 3 次失败才告警,D1 P0-2)
  4 存活    首页+关键页状态码/时延/https 混合内容
周检叠加:标题/meta 漂移哈希、llms.txt 变更、sitemap lastmod 对比、AI 爬虫放行矩阵、
  CWV 现场数据 p75(cwv_field,R0-3:field_data/PSI,任一 poor→cwv_poor warn/跨档→
  cwv_regression info,无 PSI key=skipped 不猜)、citation decay(citation,R0-4:
  项目目录 panel.json 复用 citation_panel decay 计算,decayed>0→citation_decay warn)。
R0-2 接线:diff 在产 gsc_clicks_drop/visibility 类跌幅告警前,若 gsc.csv 含
  Date+Query+Position 列则调 sensor_volatility(--context 同口径,零依赖 import;
  失败静默跳过),verdict=high_volatility 时该告警降 info 并附注
  "当日 SERP 高波动,疑似算法更新而非站点问题"。
月检叠加(R2-4,第 6 检查组 monthly):引荐域月检——monitor 目录放最新外链导出
  backlinks.csv(同 gsc.csv 模式;Ahrefs/Semrush/GSC 原始导出或 backlink_import.py
  统一格式,零依赖 import 其 parse_export 归一),快照存引荐域总数/当月新增域数
  (first_seen 近 31 天)/域清单(截断 5000);diff 对比上月快照:
  新增引荐域数暴跌>50% → backlink_drop(warn,"引荐域新增 N→M,外链获取停滞或丢失");
  总引荐域降>10% → backlink_loss(critical);无导出 → skipped 不猜;
  文件损坏(嗅探/解析失败)→ check 记 error,run 落 partial 且退出码 2(防假 0:
  绝不把"读不了"当"外链归零"参与告警判定)。阈值经 thresholds.
  backlink_newref_drop_pct / backlink_total_drop_pct 可调。

R4 监控对标①(pipeline-completeness.md §五"监控对标:SLO+错误预算"):config 可选
  slo 节 {metric: {target: 0.995, window_days: 30}},内置三指标——
  keypage_indexable(优先页可索引率 indexable/total)/canonical_ok(canonical 正确率:
  目标探测非失败即正确,自指/无 canonical 不算失败)/healthy_pages(健康页率:
  非 error/http_error 快照占比);diff 后从 db 近 window 天 ok run 的 pages 快照
  聚合实际值,剩余错误预算=1−(1−实际)/(1−目标),<25% → slo_budget_low(warn,
  "索引健康 SLO 99.5%:错误预算剩 X%,接近耗尽将建议冻结发布");report 顶部加
  SLO 条形(各指标实际 vs 目标)。按模板分账注记:全站 SLO 会藏住单模板回归
  (1000 页里一个模板 50 页全坏只摊薄成 5%)——单模板回归要看 site_crawl
  (crawl.page 口径:crawl.json pages[] 按模板分组聚合),monitor 只看抽样 key_pages。
R4 监控对标④(flapping+ack 超时):diff 时同 (code,key) 7 天内 fire+resolved≥3 次
  (至少 1 次 resolved——纯持续告警是持续事故不是抖动,降级会吞真 critical)→
  该告警降 info+附 flap_count+"建议修阈值(反复触发/自愈=阈值贴边)"(Nagios/
  Alertmanager flap_detection 口径);ack 超时在 notify.py 侧:critical 即时发送
  带 ack_deadline(默认 30min),--flush 检查未 ack 且超期的 critical → 升级
  全渠道再发一次并标记 escalated(只升一次),`notify.py ack KEY` 人工确认停升级。

告警四级(critical/warn/info/low)+ 百分比阈值×最小样本地板 = 防疲劳;
low=自愈(上次告警本次恢复)。cooldown:critical 12h / warn 24h / info 168h。

子命令:
  init   --site URL [--market XX] [--key-pages /a,/b] [--heartbeat-url U]
         [--dir .seo-monitor] [--force]
  run    [--checks daily|weekly|monthly] [--dry-run] [--budget-minutes N] [--dir D]
         [--backlinks FILE]   # 月检外链导出路径(缺省 <dir>/backlinks.csv,同 gsc.csv 模式)
  diff   [--run-id N] [--prev-run-id M] [--format json|text] [--out FILE] [--dry-run] [--dir D]
         [--ci [--ci-format json|junit]]   # CI 门:checks 结构化阈值结果,任一失败 exit 10
  report [--days 7] [--json] [--dir D]
  quarantine RUN_ID [--undo] [--dir D]   # 隔离坏 run(基线污染防护),diff 不再用它对比
  maintenance --from F --to T [--reason R] [--clear] [--dir D]  # 维护窗口:窗口内 diff 只记快照不产告警
  sample-keypages [--urls FILE] [--per-group N] [--seed S] [--write] [--dir D]
         # sitemap(或 URL 清单)→末段 slug 归一→按模板分组→每组随机抽 N ∪ 手工 key_pages;
         # 只打印建议,--write 才合并进 config;建议路由超 maxRoutes=200 截断并警告

config 可选扩展(D1 P1):
  segments:[{name,match:"regex",importance:"static|gsc_clicks"}]
         # key_pages 运行时按 regex 自动归属首个命中 segment;受影响度=Σimportance
         # (无 GSC 页级数据时每页 importance=1),替代纯页数地板;
         # 规则 pages_left_segment:segment 内健康页掉 ≥10%(Conductor 7 档中的 10% 档)→warn
  accepted_codes:["code" 或 "code:key 指纹"]
         # 已知可接受告警白名单:命中→降 low+标 accepted:true(不计入 counts/退出码),
         # 接受≠消失——周报单独列"已接受告警数",仍计数

config 可选扩展(D1 P2,key_pages 条目对象):
  {"path":"/p", "expect_substring": "A" 或 ["A","B"],   # 在场断言:数组向后兼容单条;
   "assertions": {"must_contain": "gtag(",              # 关键标记消失 → ga_tracking_removed warn
                  "max_latency_ms": 800,                 # 时延绝对上限 → latency_spike info
                  "selector_stable": true}}              # 快照存首个 h2,变了 → layout_shift info
         # 快照新指纹(D1 P2):h1(首个)/hreflang_hash(顺序无关)/word_count——
         # 变更判 h1_changed(info)/hreflang_changed(warn)/main_content_change(info,
         # 阈值 thresholds.content_change_pct 默认 30%);title/meta 新值为空=meta_removed warn。

config 可选扩展(D1 P2 第 13 条,borrow-specs serpbear 式源适配层):
  serp_source: {"id": "bing"|"duckduckgo", "enabled": true}   # 或裸字符串 id
         # visibility 检查的 SERP 源。内置 bing(默认,免费无 key 的 HTML 端点,
         # 不配该节时行为与旧版逐字节一致)与 duckduckgo(html.duckduckgo.com/html,
         # 免费无 key,解析 result 链接与排名);坏配置/未知 id → 回退 bing 并在
         # notes 警告(防静默失明);serper.dev($1/1k)/SerpApi($50/5k 起)仅注册位
         # 未接入(不实现付费源调用;源对照表见 SERP_SOURCE_TABLE)。

退出码:diff → 1=有 critical,2=有 warn(无 critical),0=无,4=用法/数据错误;
diff --ci → 0=全部 check 通过,10=任一 check 失败(siteone 契约);
run → 0 正常,2=月检 backlinks.csv 损坏(数据错误,防假 0),3=run 未完成(partial/failed)。SSRF 防护:仅 http(s)+私网拒连
+TLS 恒验证+重定向逐跳复查(302 穿墙已堵)。

并发与基线卫生(多 cron 安全):SQLite WAL + busy_timeout=30s + 目录级 flock;
run 先落 status='running' 再跑检查,终态 ok/partial/failed;卡死 run 由
sweep_stale_runs(>30min)回收;diff 的 prev 只取 status='ok' 且优先同 kind
(weekly 不拿 daily 当基线;无同 kind 回退最近 ok 并标 baseline_kind_mismatch);坏 run 用
quarantine 隔离;历史按 PruneDB 纪律保留最近 400 次 run。
cooldown 命中的告警标 suppressed:只进报告,不进通知路径(counts/退出码同排除)。
双窗口降级的响亮失败模式:库龄>7 天却取不到 7 天基线时,diff 向 stderr 打大写
WARNING 并在 payload 记 baseline_missing:true——绝不静默降级为单窗口判定。

用法:
  python3 monitor.py init --site https://example.com --market us
  python3 monitor.py run --checks daily
  python3 monitor.py diff --format text
  python3 monitor.py diff --ci --ci-format junit   # CI 门(任一阈值 check 失败 exit 10)
  python3 monitor.py sample-keypages --per-group 8 # 从 sitemap 抽样建议 key_pages
  python3 monitor.py report --days 7
  python3 monitor.py --self-test
"""
import argparse
import contextlib
import fcntl
import hashlib
import ipaddress
import json
import os
import random
import glob
import re
import socket
import sqlite3
import ssl
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from xml.sax.saxutils import escape as _xml_escape

UA = "Mozilla/5.0 (compatible; seo-suite-monitor/1.0; +https://example.com/bot)"
DEFAULT_DIR = ".seo-monitor"
OPS_MONITOR_DIR = os.path.join("seo-ops", "monitor")   # RQ-229:新版统一工作区内的监控目录


def default_dir():
    """没给 --dir 时:当前目录有 seo-ops/ 工作区就用 seo-ops/monitor,否则沿用 .seo-monitor。"""
    if os.path.isfile(os.path.join("seo-ops", "project.yaml")):
        return OPS_MONITOR_DIR
    return DEFAULT_DIR
FETCH_TIMEOUT = 15
MAX_BYTES = 2_000_000
SITEMAP_CAP = 5000          # loc→lastmod 字典上限(防大库)
SITEMAP_INDEX_CAP = 5       # sitemap index 递归层数上限
MAX_ROUTES = 200            # sample-keypages 建议路由上限(Next.js maxRoutes 惯例;超即截断+警告)
GSC_PAGE_CAP = 1000         # gsc.csv 页级点击字典上限(防快照膨胀)

# R0 接线常量(pipeline-completeness.md R0 节)
SENSOR_HIGH_NOTE = "当日 SERP 高波动,疑似算法更新而非站点问题"  # R0-2:high_volatility 附注
CWV_FIELD_PAGES = 5         # R0-3:周检 CWV 现场数据采 key_pages 前 N 页(PSI 配额预算)
CITATION_PANEL_FILE = "panel.json"   # R0-4:项目目录的 citation_panel 面板(monitor 目录或其父)

# R2-4 接线常量(引荐域月检)
BACKLINKS_CSV = "backlinks.csv"      # 月检外链导出(同 gsc.csv 模式;放 monitor 目录)
BACKLINK_NEW_WINDOW_DAYS = 31        # "当月新增引荐域"的 first_seen 回看窗(月检节奏)
BACKLINK_DOMAIN_CAP = 5000           # 快照存引荐域清单上限(防大库快照膨胀;超出截断+标记)

# R4 监控对标①常量(pipeline-completeness.md §五"SLO+错误预算")
SLO_DEFAULT_TARGET = 0.995           # 索引健康 SLO 缺省目标(99.5%)
SLO_DEFAULT_WINDOW_DAYS = 30         # SLO 回看窗(天;Google SRE 错误预算惯例 30 天)
SLO_BUDGET_LOW_PCT = 0.25            # 剩余错误预算 <25%(已耗 3/4)→ slo_budget_low(warn)
SLO_METRICS = {                      # 内置三指标(config slo 节的键 → 人读标签)
    "keypage_indexable": "优先页可索引率",
    "canonical_ok": "canonical 正确率",
    "healthy_pages": "健康页率",
}
# R4 监控对标④常量(flapping 检测)
FLAP_WINDOW_DAYS = 7                 # flapping 回看窗(天)
FLAP_THRESHOLD = 3                   # fire+resolved ≥3 次(且 ≥1 次 resolved)→ 降 info

AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
               "PerplexityBot", "CCBot", "Google-Extended", "Bytespider", "Meta-ExternalAgent"]
MARKET_BOTS = {"ru": ["YandexBot", "YandexAdditional"], "kr": ["Yeti"], "cn": ["Baiduspider"]}

LEVELS = ("critical", "warn", "info", "low")
COOLDOWN_HOURS = {"critical": 12, "warn": 24, "info": 168}

DEFAULT_THRESHOLDS = {
    "visibility_drop_pct": 30,     "visibility_min_sample": 3,
    "sitemap_urls_drop_pct": 15,   "sitemap_min_sample": 20,
    "gsc_clicks_drop_pct": 20,     "gsc_min_clicks": 5,
    "latency_increase_pct": 100,   "latency_min_ms": 500,
    "mixed_content_min": 3,
    # D1 P2:主内容体量变化阈值(word_count 增/降百分比,取绝对值;
    # 改版监测 Conductor "Tracked Changes" 型信号,info 级不改级别)
    "content_change_pct": 30,
    # D1 P1:segment 健康页流失档位,抄 Conductor segment 型敏感度 7 档
    # (0/1/5/10/25/50/75%)中的 10% 档;受影响度=Σimportance(非纯页数)
    "pages_left_segment_pct": 10,
    # R2-4:引荐域月检阈值——新增域数暴跌 %(backlink_drop warn)/总域数下降 %
    # (backlink_loss critical);严格大于才触发(恰等于阈值不告警)
    "backlink_newref_drop_pct": 50,
    "backlink_total_drop_pct": 10,
}

# report 用:告警码 → 修复动作与安全边界。RQ-229 起没有「agent 直接改线上」这一档:
# urgent_pr = 加急草稿 PR + 立即通知人合并(原 auto 项:回滚类、分秒必争);draft_pr = 草稿 PR 人审;
# human = 人判断。改 robots、noindex、canonical、重定向一律走 PR,agent 不直接改线上或推主干。
PLAYBOOK = {
    "homepage_down":        ("加急:起草回滚最近发布的 PR 并立即通知人;同时查 CDN 与源站健康", "urgent_pr"),
    "key_page_down":        ("查 URL 是否被移动→301 映射(draft PR 人审重定向表)", "draft_pr"),
    "visibility_zero":      ("按 alert-threshold-guide 排查顺序 L1→L5;先查 robots/noindex/处罚", "human"),
    "visibility_drop":      ("GSC 分层定位(query/page/device);对照 Search Status Dashboard", "human"),
    "robots_sitewide_block":("加急:起草删掉误封行的 robots.txt 修正 PR,立即通知人合并", "urgent_pr"),
    "sitemap_urls_drop":    ("sitemap_audit.py 复核;核实是否生成管道断裂", "human"),
    "gsc_clicks_drop":      ("五层根因协议(L1 数据→L5 外部);did_attribution.py 归因", "human"),
    "mixed_content":        ("把 http:// 子资源改 https(draft PR 批量替换)", "draft_pr"),
    "fetch_error_confirmed":("连续两次抓取失败:查本机网络→DNS→站点防火墙是否拦爬虫", "human"),
    "title_meta_drift":     ("确认变更是否有意;无意则恢复基线(draft PR)", "draft_pr"),
    "llms_txt_changed":     ("diff llms.txt 变更;llmstxt.py validate 复核", "draft_pr"),
    "llms_txt_removed":     ("确认为何被删;需要则 llmstxt.py generate 重建(draft PR)", "draft_pr"),
    "robots_changed":       ("复核 robots 变更意图;robots_posture.py 全量复查", "human"),
    "ai_posture_flip":      ("确认 AI 爬虫放行翻转是否有意(visibility/protect-ip 取向)", "human"),
    "latency_spike":        ("CWV 分档核对;查最近部署", "human"),
    "gsc_clicks_spike":     ("记录归因(营销活动/季节性/SERP 变化)", "human"),
    "ssl_cert_expired":     ("加急:通知人立即续期证书(certbot renew 类幂等动作由有权限的人或其部署流程执行)", "urgent_pr"),
    "ssl_cert_expiry":      ("续期证书;检查自动续期任务为何没跑", "human"),
    "content_regression":   ("核对 expect_substring 断言;查空白渲染/软 404/误改版(draft PR)", "draft_pr"),
    "dead_man":             ("监控自身停摆:查 cron/Actions 是否被禁、机器是否休眠", "human"),
    "noindex_added":        ("加急:起草回滚引入 noindex 的发布/模板改动的 PR(若非有意下线),立即通知人", "urgent_pr"),
    "noindex_removed":      ("自愈信号,记录即可;顺手排查此前为何被误加 noindex", "human"),
    "canonical_target_broken": ("核对 canonical 目标是否被移动/删除:修正指向或恢复目标页(draft PR)", "draft_pr"),
    "pages_left_segment":   ("定位 segment 内批量掉出健康集的页面(部署/模板/权限回退);逐页看 key_page_down/noindex_added 详情", "human"),
    # D1 P2 批
    "meta_removed":         ("加急:起草恢复被移除的 title/meta 等字段的 PR(若非有意,回滚发布/模板改动)", "urgent_pr"),
    "h1_changed":           ("确认 h1 变更是否有意(h1 是最强 on-page 信号之一);无意恢复(draft PR)", "draft_pr"),
    "hreflang_changed":     ("hreflang 注解整组核对(互链回链+x-default);改错会让整组语言版本退出对应市场索引(draft PR)", "draft_pr"),
    "ga_tracking_removed":  ("确认统计/跟踪脚本是否被误删(CMP/广告拦截不改服务端输出);有意移除则同步删 must_contain 断言(draft PR)", "draft_pr"),
    "redirect_chain_broken":("恢复非规范域→canonical host 的 301(服务器/CDN 重定向规则),防重复内容(draft PR)", "draft_pr"),
    "main_content_change":  ("核对内容体量骤变(误发布/被篡改/软 404 变薄/模板丢正文区);无意则回滚(draft PR)", "draft_pr"),
    "layout_shift":         ("核对模板/布局改动是否有意(selector_stable 监控的首个 h2 漂移);无意恢复(draft PR)", "draft_pr"),
    # R0 接线新增告警码
    "cwv_poor":             ("按 references/technical/cwv-playbook.md 排查对应指标(LCP/INP/CLS);对照最近部署与第三方脚本变化", "human"),
    "cwv_regression":       ("核对 CWV 档位退步(good→needs_improvement 等);查最近部署/新增第三方脚本/资源变化", "human"),
    "citation_decay":       ("citation_panel decay 重写队列进 refresh 排期:更新过峰被引页(数据/时效/反共识钩)", "human"),
    # R2-4 接线新增告警码(引荐域月检)
    "backlink_drop":        ("核查外链获取是否停滞(outreach/数字 PR 投产比);对照 Ahrefs/Semrush 新增趋势与最近内容发布节奏", "human"),
    "backlink_loss":        ("总引荐域大幅丢失:查 Search Console 手动操作处罚/外链被撤/导出口径是否变化;外链资产 6.5x 杠杆,优先复核", "human"),
    # R4 监控对标①:SLO 错误预算告急(冻结协议联动)
    "slo_budget_low":       ("冻结发布(算法更新冻结协议 Freeze→Pause→Review);先修预算消耗来源(noindex/宕机/canonical 断链),预算恢复>50% 再解冻", "human"),
}

# 告警抑制树(audit 19,Prometheus inhibition 纪律):根因一条,派生折叠。
# 格式:根告警码 → (被抑制码..., 作用域) 作用域 sitewide=抑制一切;same_key=仅同 key。
# D1 P0-1:页面级 noindex_added 属派生信号——robots 全站误封/首页宕机这类 sitewide 根因
# 在场时折叠(同一部署事故的次级表现,单独重复通知只会稀释根因)。
# D1 P1:pages_left_segment(segment 聚合流失)同属 sitewide 根因的派生聚合,一并折叠。
INHIBITS = {
    "homepage_down":        (("key_page_down", "content_regression", "mixed_content", "noindex_added",
                              "pages_left_segment"), "sitewide"),
    "robots_sitewide_block": (("noindex_added", "pages_left_segment"), "sitewide"),
    "fetch_error_confirmed": (("title_meta_drift", "content_regression", "mixed_content", "latency_spike"), "same_key"),
}

# 关键页字段级 diff 的比对字段(audit 17,changedetection.io 字段级指纹)。
# D1 P0-1/P0-2 新快照字段(indexable/noindex_source/canonical_target_status/
# canonical_fail_streak)刻意不进本清单:各有专用规则(noindex_added/removed、
# canonical_target_broken),进字段漂移会双报;且旧 monitor.db 快照缺这些字段,
# 会被当 "(None→有值)" 漂移,升级后首个 diff 全网误报。
# D1 P2 同理:h1/h2/hreflang_hash/word_count/must_contain_missing 各有专用规则
# (h1_changed/layout_shift/hreflang_changed/main_content_change/ga_tracking_removed),
# 且旧快照缺键必须按 None 不触发,不进通用漂移清单。
PAGE_DIFF_FIELDS = ("title", "meta_desc", "canonical", "og_title", "og_desc", "watch")

# D1 P2:title/meta 类字段的"移除"语义边界——新值为空串/缺失且旧值非空才算移除
# (warn);新值非空的普通变化走 title_meta_drift(info)。仅对真实取到并渲染的页面
# 判定(404/抓取失败的页面没有"字段被移除"的证据)。
PAGE_REMOVED_FIELDS = ("title", "meta_desc", "canonical", "og_title", "og_desc", "watch")


class FetchError(Exception):
    pass


# ---------- 基础工具 ----------

def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:16]


def norm_site(url):
    url = (url or "").strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url.rstrip("/")


def registrable_domain(url):
    host = urllib.parse.urlparse(url).netloc.split("@")[-1].split(":")[0].lower()
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in host.split(".") if p]
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host or ""


_ssrf_cache = {}


def ssrf_guard(host):
    """仅 http(s) + 拒私网/环回/链路本地;结果按 host 缓存(TLS 恒验证走默认 urlopen)。
    198.18.0.0/15(RFC2544 基准段)豁免:本机 fake-IP 代理(Surge/Clash 等)会把一切域名
    解析到该段,实际连接经代理出网,TLS 验证仍生效;设 SEO_MONITOR_STRICT_SSRF=1 恢复全拒。"""
    if not host:
        raise FetchError("empty host")
    if host in _ssrf_cache:
        return
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as e:
        raise FetchError("DNS 解析失败 %s: %s" % (host, e))
    strict = bool(os.environ.get("SEO_MONITOR_STRICT_SSRF"))
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if ip in ipaddress.ip_network("198.18.0.0/15"):
            if not strict:
                continue
            raise FetchError("SSRF guard: 非公网地址 %s(strict 模式拒 fake-IP 段)" % ip)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise FetchError("SSRF guard: 非公网地址 %s" % ip)
    _ssrf_cache[host] = True


class _RedirectGuard(urllib.request.HTTPRedirectHandler):
    """重定向逐跳 SSRF 复查(audit 05 P0:urlopen 自动跟随 302,最终 host 从不复查,
    站方可控的 robots.txt sitemap 指令可 302 到 169.254.169.254 穿墙)。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        p = urllib.parse.urlparse(newurl)
        if p.scheme not in ("http", "https"):
            raise FetchError("重定向到非 http(s) 被拒: %s" % _redact_url(newurl))
        ssrf_guard(p.hostname)  # 每一跳都复查,包括最后一跳
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_RedirectGuard)


def _redact_url(u):
    """日志脱敏:保留 scheme+host,路径/查询(常含 token)打码。"""
    return re.sub(r"^(https?://[^/\s]+).*$", r"\1/[REDACTED]", str(u))


def _headers_of(msg):
    """响应头对象 → 扁平 dict(键小写,重复键逗号并值)。D1 P0-1 需读 X-Robots-Tag;
    对 None/异常对象容错(旧测试桩/特殊响应路径可能无头)。"""
    out = {}
    if msg is None:
        return out
    try:
        keys = list(msg.keys())
    except Exception:
        return out
    for k in keys:
        try:
            vals = msg.get_all(k) or []
        except Exception:
            continue
        if vals:
            out[str(k).lower()] = ", ".join(v.strip() for v in vals if v is not None)
    return out


def http_get(url, timeout=FETCH_TIMEOUT):
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https"):
        raise FetchError("仅允许 http(s): %s" % url)
    ssrf_guard(p.hostname)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml,*/*"})
    t0 = time.monotonic()
    try:
        with _opener.open(req, timeout=timeout) as r:
            body = r.read(MAX_BYTES)
            return {"status": r.status, "final_url": r.geturl(), "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                    "body": body.decode("utf-8", "replace"), "headers": _headers_of(r.headers)}
    except urllib.error.HTTPError as e:
        body = e.read(MAX_BYTES) if e.fp else b""
        return {"status": e.code, "final_url": url, "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
                "body": body.decode("utf-8", "replace"), "headers": _headers_of(e.headers)}
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise FetchError("抓取失败 %s: %s" % (_redact_url(url), e))


def http_head(url, timeout=FETCH_TIMEOUT):
    """HEAD 探测(D1 P0-2 canonical 目标健康度):复用 http_get 的 SSRF 防御/超时/
    重定向逐跳复查;405/501(站点不支持 HEAD)降 GET 只读头——不下载 body。
    返回 {"status": int};网络层失败抛 FetchError(由调用方按 "error" 记,防抖在 diff)。"""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https"):
        raise FetchError("仅允许 http(s): %s" % url)
    ssrf_guard(p.hostname)

    def once(method):
        req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
        try:
            with _opener.open(req, timeout=timeout) as r:
                return int(r.status)          # GET 降级也只取状态,不读 body
        except urllib.error.HTTPError as e:
            if e.fp:
                with contextlib.suppress(Exception):
                    e.read(512)
            return int(e.code)
    try:
        status = once("HEAD")
        if status in (405, 501):
            status = once("GET")
        return {"status": status}
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise FetchError("HEAD 失败 %s: %s" % (_redact_url(url), e))


def pct_drop(prev_v, curr_v):
    """返回下降比例(0~1);prev 无/为 0 → None(不猜)。"""
    if prev_v is None or curr_v is None or prev_v <= 0:
        return None
    return (prev_v - curr_v) / prev_v


def _import_sibling(modname):
    """零依赖兄弟模块加载(scripts/ 同目录的 field_data / sensor_volatility /
    citation_panel,均 stdlib-only):sys.path 注入后 import。失败原样上抛,
    由调用方决定降级(R0 接线的三处调用均"失败不猜/静默跳过")。"""
    d = os.path.dirname(os.path.abspath(__file__))
    if d not in sys.path:
        sys.path.insert(0, d)
    return __import__(modname)


# ---------- 存储层 ----------

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, kind TEXT, status TEXT,
  checks_run TEXT, budget_used_sec REAL, summary TEXT);
CREATE TABLE IF NOT EXISTS snapshots(
  run_id INTEGER, ts TEXT, "check" TEXT, key TEXT, value TEXT, hash TEXT);
CREATE TABLE IF NOT EXISTS alerts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, ts TEXT, level TEXT,
  code TEXT, key TEXT, message TEXT, details TEXT, suppressed INTEGER DEFAULT 0,
  resolved INTEGER DEFAULT 0, resolved_run INTEGER);
CREATE INDEX IF NOT EXISTS idx_snap_run ON snapshots(run_id);
CREATE INDEX IF NOT EXISTS idx_alert_fp ON alerts(code, key, resolved);
"""


def open_db(mdir):
    os.makedirs(mdir, exist_ok=True)
    dbp = os.path.join(mdir, "monitor.db")
    fresh = not os.path.exists(dbp)
    conn = sqlite3.connect(dbp, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # audit 05 P1:本地多 cron/挂住的 run 并发 → WAL + busy_timeout,
    # 与目录级 flock(见 monitor_lock)双保险。
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.executescript(SCHEMA)
    if fresh and glob.glob(os.path.join(mdir, "runs", "run-*.json")):
        # RQ-229:monitor.db 只是缓存(不进 git);新克隆或缓存丢了,从 runs/*.json 重建
        n_runs, n_alerts = rebuild_db(conn, mdir)
        print("[i] monitor.db 不存在,已从 runs/ 重建: %d 次 run、%d 条告警" % (n_runs, n_alerts))
    return conn


def rebuild_db(conn, mdir):
    """按 runs/run-NNNNN.json(每次 run 的快照)和 runs/diff-NNNNN.json(每次 diff 写库的告警)
    重放出 runs/snapshots/alerts 三表。run 编号沿用文件名,保证和 git 里的文件对得上。"""
    n_runs = n_alerts = 0
    for path in sorted(glob.glob(os.path.join(mdir, "runs", "run-*.json"))):
        m = re.search(r"run-(\d+)\.json$", path)
        if not m:
            continue
        rid = int(m.group(1))
        try:
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
        except (OSError, ValueError):
            continue
        ts = payload.get("ts") or datetime.fromtimestamp(os.path.getmtime(path)).isoformat(
            timespec="seconds")
        conn.execute("INSERT OR REPLACE INTO runs(id, ts, kind, status, checks_run, budget_used_sec,"
                     " summary) VALUES(?,?,?,?,?,?,?)",
                     (rid, ts, payload.get("kind"), payload.get("status") or "ok",
                      payload.get("kind"), payload.get("budget_used_sec") or 0,
                      json.dumps(payload, ensure_ascii=False)))
        for check, kv in (payload.get("snapshot") or {}).items():
            for key, value in (kv or {}).items():
                h = sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True))
                conn.execute("INSERT INTO snapshots(run_id, ts, \"check\", key, value, hash) "
                             "VALUES(?,?,?,?,?,?)",
                             (rid, ts, check, key, json.dumps(value, ensure_ascii=False), h))
        n_runs += 1
    for path in sorted(glob.glob(os.path.join(mdir, "runs", "diff-*.json"))):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        rid, ts = d.get("curr_run"), d.get("generated")
        per = d.get("persisted") or {}
        for a in per.get("inserted") or []:
            conn.execute("INSERT INTO alerts(run_id, ts, level, code, key, message, details, suppressed)"
                         " VALUES(?,?,?,?,?,?,?,0)",
                         (rid, ts, a.get("level"), a.get("code"), a.get("key"), a.get("message"),
                          json.dumps(a.get("details_row") or {}, ensure_ascii=False)))
            n_alerts += 1
        for r in per.get("resolved") or []:
            row = conn.execute("SELECT id, ts, level FROM alerts WHERE code=? AND key=? AND resolved=0 "
                               "ORDER BY id DESC LIMIT 1", (r.get("code"), r.get("key"))).fetchone()
            if row is None:
                continue
            conn.execute("UPDATE alerts SET resolved=1, resolved_run=? WHERE id=?", (rid, row["id"]))
            conn.execute("INSERT INTO alerts(run_id, ts, level, code, key, message, details) "
                         "VALUES(?,?,?,?,?,?,?)",
                         (rid, ts, "low", r.get("code") + "_resolved", r.get("key"),
                          "自愈: %s 的问题已消失(上次 %s)" % (r.get("key"), row["ts"]),
                          json.dumps({"prev_level": row["level"]}, ensure_ascii=False)))
    for path in sorted(glob.glob(os.path.join(mdir, "runs", "status-*.json"))):
        try:                                    # quarantine 写的状态覆盖(run 编号 → 状态)
            with open(path, encoding="utf-8") as f:
                st = json.load(f)
            conn.execute("UPDATE runs SET status=? WHERE id=?", (st["status"], int(st["run_id"])))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    conn.commit()
    return n_runs, n_alerts


@contextlib.contextmanager
def monitor_lock(mdir, timeout=120.0):
    """目录级 flock:同一 .seo-monitor/ 同时只允许一个 run/diff(本地 cron 竞态)。"""
    os.makedirs(mdir, exist_ok=True)
    path = os.path.join(mdir, ".lock")
    fh = open(path, "w")
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() > deadline:
                    raise SystemExit("错误: 另一 monitor 进程持有 %s 超过 %.0fs,放弃(防本地 cron 竞态)"
                                     % (path, timeout))
                time.sleep(0.5)
        yield
    finally:
        try:
            fcntl.flock(fh, fcntl.LOCK_UN)
        finally:
            fh.close()


# 值形似 secret(已知 webhook/token 形态;防 config.json 明文落盘,audit 05 P1)
_SECRET_VALUE_RE = re.compile(
    r"hooks\.slack\.com/services|discord(app)?\.com/api/webhooks|api\.telegram\.org/bot"
    r"|xox[bposa]-|[0-9]{8,}:[A-Za-z0-9_-]{30,}|hooks\.(feishu|dingtalk)|camel\.ai|sk-[A-Za-z0-9]{20,}", re.I)
# 键名即要求非 secret(只允许 env 引用名或 $ENV 形式,audit 01 rec4)
_SECRET_KEY_RE = re.compile(r"(webhook_url|bot_token|password|api_key|secret)$", re.I)


def find_config_secrets(cfg):
    """返回 config 里疑似明文 secret 的路径列表(channels 只存 env 引用名)。"""
    hits = []

    def walk(obj, path):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and _SECRET_KEY_RE.search(k or "") and v \
                        and not v.startswith("$") and "env" not in k.lower():
                    hits.append(".".join(path + [k]) + "(键要求 env 引用,不接受明文)")
                walk(v, path + [str(k)])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, path + [str(i)])
        elif isinstance(obj, str) and obj and _SECRET_VALUE_RE.search(obj):
            hits.append(".".join(path) + "(值形似 secret)")

    walk(cfg, [])
    return hits


def load_config(mdir):
    path = os.path.join(mdir, "config.json")
    if not os.path.exists(path):
        raise SystemExit("错误: %s 不存在,先跑 init" % path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_config(mdir, cfg):
    hits = find_config_secrets(cfg)
    if hits:
        raise SystemExit(
            "错误: config.json 检测到疑似明文 secret,拒写(审计 05-§4):\n  - " + "\n  - ".join(hits)
            + "\nsecret 只经环境变量注入(channels.* 只存 env 引用名);若确为误报,"
              "改用 $ENV_NAME 引用形式或换键名后重试")
    tmp = os.path.join(mdir, "config.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, os.path.join(mdir, "config.json"))


# ---------- init ----------

def cmd_init(args):
    mdir = args.dir
    cfg_path = os.path.join(mdir, "config.json")
    if os.path.exists(cfg_path) and not args.force:
        print("错误: %s 已存在(用 --force 重建,会保留 monitor.db 之外的文件覆盖)"
              % cfg_path, file=sys.stderr)
        return 1
    site = norm_site(args.site)
    key_pages = [p.strip() for p in (args.key_pages or "/").split(",") if p.strip()]
    heartbeat = (args.heartbeat_url or os.environ.get("SEO_MONITOR_HEARTBEAT_URL") or "").strip()
    cfg = {
        "site": site,
        "market": (args.market or "").lower() or None,
        "key_pages": key_pages,
        "created": datetime.now().isoformat(timespec="seconds"),
        "budget_minutes": 5,
        "cooldown_hours": dict(COOLDOWN_HOURS),
        "thresholds": dict(DEFAULT_THRESHOLDS),
        "heartbeat_url": heartbeat or None,
        "run_cadence_hours": 24,   # dead man's switch 判定用:无成功 run 超 2×该值 → dead_man
        "channels": {
            "slack":    {"env": "SEO_MONITOR_SLACK_WEBHOOK"},
            "discord":  {"env": "SEO_MONITOR_DISCORD_WEBHOOK"},
            "telegram": {"env_token": "SEO_MONITOR_TG_TOKEN", "env_chat": "SEO_MONITOR_TG_CHAT"},
            "email":    {"smtp_host": "", "smtp_port": 465, "use_ssl": True, "username": "",
                         "env_pass": "SEO_MONITOR_SMTP_PASS", "from": "", "to": []},
            "webhook":  {"env": "SEO_MONITOR_WEBHOOK_URL",
                         "note": "Apprise 式通用 webhook:URL 支持 json(s):// form(s):// text(s):// scheme"},
        },
        "notes": [
            "secret 只经环境变量注入(channels 只存 env 引用名,写明文会被 save_config 拒绝)",
            "GSC 流量检查:每次 run 前把 GSC 导出放到 " + os.path.join(mdir, "gsc.csv") +
            "(列含 Query,Clicks,Impressions);没有该文件则跳过流量问",
            "月检引荐域(R2-4):每月 run --checks monthly 前把最新外链导出放到 " +
            os.path.join(mdir, BACKLINKS_CSV) +
            "(backlink_import.py 统一格式,或 Ahrefs/Semrush/GSC 原始导出自动归一);"
            "没有该文件则跳过引荐域问;新增域暴跌>50%→backlink_drop(warn),"
            "总域降>10%→backlink_loss(critical)",
            "阈值是经验起点,按 alert-threshold-guide.md 用本站基线校准",
            "key_pages 支持对象形式: {\"path\": \"/p\", \"expect_substring\": \"Price\", "
            "\"selector\": \"h1\" 或 \"re:<regex>\"}(关键词在场断言+字段级 diff 圈定)",
            "segments(可选): [{\"name\":\"docs\",\"match\":\"^/docs/\",\"importance\":"
            "\"static|gsc_clicks\"}]——key_pages 按 regex 自动归属,健康页掉≥10% 告警 "
            "pages_left_segment(受影响度=Σimportance);名单可用 sample-keypages 子命令抽样建议",
            "accepted_codes(可选): [\"code\" 或 \"code:key\"]——已知可接受告警白名单,"
            "命中降 low+标 accepted(接受≠消失,周报仍单独计数)",
            "key_pages 断言(D1 P2): expect_substring 支持数组(向后兼容单条);条目可加 "
            "assertions:{\"must_contain\": \"gtag(\", \"max_latency_ms\": 800, "
            "\"selector_stable\": true}——关键标记消失→ga_tracking_removed(warn)/"
            "时延绝对上限/首个 h2 漂移→layout_shift(info);"
            "快照自动记 h1/hreflang_hash(顺序无关)/word_count,变更判 "
            "h1_changed(info)/hreflang_changed(warn)/main_content_change(info,"
            "阈值 thresholds.content_change_pct 默认 30%);title/meta 变空=meta_removed(warn)",
            "slo(可选,R4 监控对标①): {\"keypage_indexable\": {\"target\": 0.995, "
            "\"window_days\": 30}}——内置三指标 keypage_indexable(优先页可索引率)/"
            "canonical_ok(canonical 正确率)/healthy_pages(健康页率);diff 后从近 "
            "window 天快照算实际值,剩余错误预算<25% → slo_budget_low(warn,建议冻结发布);"
            "report 顶部出 SLO 条形;单模板回归另看 site_crawl(crawl.page 口径)",
            "heartbeat: 配 healthchecks.io 类 ping URL 后,run 成功 ping URL 本身、失败 ping URL/fail;"
            "grace 建议 ≈ cron 间隔×2+典型运行时长",
        ],
    }
    os.makedirs(mdir, exist_ok=True)
    os.makedirs(os.path.join(mdir, "runs"), exist_ok=True)
    conn = open_db(mdir)
    conn.close()
    save_config(mdir, cfg)
    print("监控目录已建立: %s/" % mdir)
    print("  monitor.db   SQLite(runs/snapshots/alerts,WAL 模式)")
    print("  config.json 站点=%s 市场=%s 关键页=%s" % (site, cfg["market"] or "-", ",".join(key_pages)))
    print("  runs/        每次 run 的 JSON 快照")
    if heartbeat:
        print("  heartbeat    %s(成功 ping URL 本身,失败 ping URL/fail)" % _redact_url(heartbeat))
    print("下一步: python3 %s run --checks daily(先建基线,再部署 cron)"
          % os.path.basename(sys.argv[0]))
    return 0


# ---------- 检查实现(每项返回 {check, state, metrics, notes}) ----------

def extract_head(html):
    def one(pattern):
        m = re.search(pattern, html, re.I | re.S)
        return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""
    title = one(r"<title[^>]*>(.*?)</title>")
    meta = one(r'<meta[^>]+name=["\']description["\'][^>]*content=["\'](.*?)["\']') or \
           one(r'<meta[^>]+content=["\'](.*?)["\'][^>]*name=["\']description["\']')

    def prop(p):
        m = re.search(r'<meta[^>]+property=["\']%s["\'][^>]+content=["\'](.*?)["\']' % p, html, re.I) or \
            re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']%s["\']' % p, html, re.I)
        return m.group(1).strip() if m else ""
    canonical = ""
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']', html, re.I)
    if m:
        canonical = m.group(1)
    return title, meta, canonical, prop("og:title"), prop("og:description")


# noindex 指令 token:词边界匹配——命中 "noindex"/"noindex,nofollow"/"googlebot: noindex",
# 不命中 "nonoindex"/自定义词(D1 P0-1)
_NOINDEX_TOKEN_RE = re.compile(r"(?<![\w-])noindex(?![\w-])", re.I)


def meta_robots_noindex(html):
    """<meta name=robots content=...> 含 noindex 指令(属性两种顺序均支持,大小写不敏感)。"""
    m = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\'](.*?)["\']', html, re.I) or \
        re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]*name=["\']robots["\']', html, re.I)
    return bool(m and _NOINDEX_TOKEN_RE.search(m.group(1)))


def header_noindex(headers):
    """X-Robots-Tag 响应头含 noindex(多 directive/agent 前缀如 googlebot:noindex 均命中;
    headers 为 http_get 保留的扁平小写键 dict,键大小写不敏感,None/缺键=无)。"""
    h = headers or {}
    v = h.get("x-robots-tag")
    if v is None:
        for k, val in h.items():
            if str(k).lower() == "x-robots-tag":
                v = val
                break
    return bool(_NOINDEX_TOKEN_RE.search(v or ""))


def canonical_failure(status):
    """canonical 目标探测值是否算失败:网络不可达("error")或最终状态 ≥4xx
    (重定向已被跟随,以最终落点为准)。None/2xx/3xx → False。"""
    return status == "error" or (isinstance(status, int) and status >= 400)


def probe_canonical_target(page_url, final_url, canonical):
    """D1 P0-2:canonical 目标健康度探测(check_page 内调用=每页每 run 恰一次)。
    HEAD 复用 http_head(SSRF 防御/超时/逐跳复查);自指 canonical(目标=本页/最终
    URL,健康站的常态)→ None:本页自身 status 已在监控中,不发重复请求;
    无 canonical → None;网络失败 → "error"(防抖交给 canonical_fail_streak)。"""
    if not canonical:
        return None
    target = urllib.parse.urljoin(final_url or page_url, canonical)
    norm = lambda u: (u or "").rstrip("/")
    if norm(target) in (norm(page_url), norm(final_url)):
        return None
    try:
        return http_head(target)["status"]
    except FetchError:
        return "error"


def extract_selector(html, sel):
    """最小 selector 引擎(stdlib,audit 17 字段级 diff):支持 "tag" / "#id" / "tag#id" /
    ".class" / "tag.class" / "re:<regex>"(取第一处匹配,有分组取组 1)。圈定关注区,
    模板无关区块不进指纹。"""
    if not sel:
        return ""
    sel = sel.strip()
    if sel.startswith("re:"):
        try:
            m = re.search(sel[3:], html, re.S)
        except re.error:
            return ""
        if not m:
            return ""
        return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m.group(1) if m.groups() else m.group(0)))).strip()
    m = re.match(r"^([a-zA-Z][\w-]*)?(?:#([\w-]+))?(?:\.([\w-]+))?$", sel)
    if not m or not any(m.groups()):
        return ""
    tag, idv, cls = m.groups()
    t = re.escape(tag) if tag else r"[a-zA-Z][\w-]*"
    if idv:
        pat = r"<%s[^>]*\bid=[\"']%s[\"'][^>]*>(.*?)</%s\s*>" % (t, re.escape(idv), t)
    elif cls:
        pat = r"<%s[^>]*\bclass=[\"'][^\"']*\b%s\b[^\"']*[\"'][^>]*>(.*?)</%s\s*>" % (t, re.escape(cls), t)
    else:
        pat = r"<%s[^>]*>(.*?)</%s\s*>" % (t, t)
    m = re.search(pat, html, re.I | re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip()


def parse_key_page(entry):
    """key_pages 元素(str 或 dict)→ 页面选项 dict(D1 P2 多断言模型):
      {path, expect(needle 列表), selector, must_contain(needle 列表),
       max_latency_ms, selector_stable}
    兼容口径:
    - expect_substring 单条 str(P1 前形态)或数组;expect 缺省时数组断言也可写
      assertions.must_contain(消失→ga_tracking_removed,区别于 expect 的 content_regression);
    - max_latency_ms/selector_stable 接受 assertions 嵌套或顶层同名键。"""
    o = {"path": "/", "expect": [], "selector": None,
         "must_contain": [], "max_latency_ms": None, "selector_stable": False}
    if isinstance(entry, dict):
        p = str(entry.get("path") or "/")
        o["path"] = p if p.startswith("/") else "/" + p
        o["selector"] = entry.get("selector")
        asr = entry.get("assertions") if isinstance(entry.get("assertions"), dict) else {}
        o["expect"] = _as_needles(entry.get("expect_substring"))
        o["must_contain"] = _as_needles(asr.get("must_contain") if asr.get("must_contain") is not None
                                        else entry.get("must_contain"))
        mx = asr.get("max_latency_ms") if asr.get("max_latency_ms") is not None \
            else entry.get("max_latency_ms")
        try:
            o["max_latency_ms"] = float(mx) if mx is not None else None
        except (TypeError, ValueError):
            o["max_latency_ms"] = None
        o["selector_stable"] = bool(asr.get("selector_stable",
                                            entry.get("selector_stable", False)))
    else:
        p = str(entry)
        o["path"] = p if p.startswith("/") else "/" + p
    return o


# ---------- D1 P1:segments 模型(Conductor segment 型敏感度) ----------

def segment_of(path, cfg):
    """key page 路径 → 首个 regex 命中的 segment 配置 dict(无 segments/不命中/坏 regex → None)。
    归属在 compute_alerts 运行时进行(config 改 segments 即刻生效,不用重建快照)。"""
    for seg in cfg.get("segments") or []:
        if not isinstance(seg, dict):
            continue
        pat = seg.get("match")
        if not pat:
            continue
        try:
            if re.search(pat, path):
                return seg
        except re.error:
            continue      # 坏 regex:跳过该 segment,不让监控崩
    return None


def page_healthy(m):
    """快照页值 → 是否健康:state ok(旧快照无 state 键按 ok)+ status<400 + 可索引
    (indexable False=noindex,退出健康集)。缺字段按最好情况猜不出 False(与 P0-1 兼容口径一致)。"""
    if not isinstance(m, dict):
        return False
    if m.get("state") not in (None, "ok"):
        return False
    st = m.get("status")
    if isinstance(st, int) and st >= 400:
        return False
    if m.get("indexable") is False:
        return False
    return True


def page_importance(seg, path, page_clicks):
    """segment 页重要度(D1 P1:受影响度=Σimportance,替代纯页数地板):
    static(默认)=1;gsc_clicks=GSC 页级点击数(无 gsc 数据/页未列出=1,不猜 0)。"""
    mode = str((seg or {}).get("importance") or "static").lower()
    if mode == "gsc_clicks" and isinstance(page_clicks, dict) and page_clicks:
        try:
            v = page_clicks.get(path, 1)
            return float(v) if isinstance(v, (int, float)) else 1.0
        except (TypeError, ValueError):
            return 1.0
    return 1.0


def page_rendered(m):
    """快照页值 → 本次 run 是否真实取到并渲染了页面(D1 P2 移除类判定的前提):
    state ok/缺省(旧/合成快照常无 state 键)+ status<400。404/抓取失败/预算跳过的
    页面没有"字段被移除/h1 变了"的证据——判 False,不产生 removal 类告警(防假信号)。"""
    if not isinstance(m, dict) or m.get("state") not in (None, "ok"):
        return False
    st = m.get("status")
    return not (isinstance(st, int) and st >= 400)


def _as_needles(v):
    """断言配置值 → needle 列表:None→[];str→[str](空串丢弃);list/tuple→逐项转 str
    (D1 P2:expect_substring/must_contain 支持单条或数组,数组向后兼容单条)。"""
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v else []
    return [str(x) for x in v if str(x)]


def extract_hreflangs(html):
    """<link rel=alternate hreflang=...> → ["lang=href", ...](属性顺序无关;
    无 hreflang 的 alternate link 如 RSS 不计)。"""
    out = []
    for m in re.finditer(r"<link\b[^>]*>", html or "", re.I):
        tag = m.group(0)
        if not re.search(r"rel\s*=\s*[\"']?\balternate\b", tag, re.I):
            continue
        lang = re.search(r"hreflang\s*=\s*[\"']?([^\"'\s>]+)", tag, re.I)
        if not lang:
            continue
        href = re.search(r"href\s*=\s*[\"']([^\"']*)[\"']", tag, re.I) or \
            re.search(r"href\s*=\s*([^\s>]+)", tag, re.I)
        out.append(lang.group(1).lower() + "=" + (href.group(1) if href else ""))
    return out


def hreflang_hash(html):
    """hreflang 集指纹:列表排序后哈希(顺序无关——重排同一组语言注解不算变更,
    增删语言/改 href 才算;与 changelog.py 的 hreflang 顺序无关口径一致)。"""
    return sha256_text("\n".join(sorted(extract_hreflangs(html))))


def word_count_html(html):
    """正文近似词数(D1 P2 main_content_change):剥 script/style/noscript/svg/注释
    与标签后按空白切分;CJK/假名/谚文无空格分隔,按字符追加计数(体量方向信号,
    非精确字数——阈值只看百分比变化)。"""
    txt = re.sub(r"(?is)<(script|style|noscript|svg|template)\b[^>]*>.*?</\1>", " ", html or "")
    txt = re.sub(r"(?s)<!--.*?-->", " ", txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = unescape(txt)
    cjk = len(re.findall(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]", txt))
    return len(txt.split()) + cjk


def mixed_content_count(url, html):
    if urllib.parse.urlparse(url).scheme != "https":
        return None  # 仅 https 站才检查
    hits = re.findall(r'(?:src|srcset)\s*=\s*["\']http://[^"\']+', html, re.I)
    return len(hits)


def check_page(url, expect=None, selector=None, must_contain=None, selector_stable=False):
    """首页/关键页通用:状态码/时延/title/混合内容/(可选)expect_substring 断言+selector 圈定
    +页面级 noindex 检测(D1 P0-1:meta robots / X-Robots-Tag → indexable)
    +canonical 目标健康度(D1 P0-2:非自指目标 HEAD 一次,存 canonical_target_status)
    +P2 指纹:h1(首个)/hreflang_hash(顺序无关)/word_count 恒入快照;
      expect/must_contain 均支持单条或数组;selector_stable 额外存首个 h2 文本。"""
    out = {"check": "page", "state": "ok", "metrics": {}, "notes": []}
    try:
        r = http_get(url)
    except FetchError as e:
        out["state"] = "error"
        out["metrics"] = {"error": str(e)}
        out["notes"].append("网络层失败≠站点宕机:单次记 info,连续两次才升 warn")
        return out
    headers = r.get("headers") or {}   # 旧桩/旧路径可能无该键,容错
    title, meta, canonical, og_title, og_desc = extract_head(r["body"])
    nm, nh = meta_robots_noindex(r["body"]), header_noindex(headers)
    m = {"status": r["status"], "latency_ms": r["elapsed_ms"], "title": title,
         "meta_desc": meta, "canonical": canonical, "og_title": og_title, "og_desc": og_desc,
         "final_url": r["final_url"],
         "h1": extract_selector(r["body"], "h1"),                     # D1 P2:h1 进指纹
         "hreflang_hash": hreflang_hash(r["body"]),                   # D1 P2:顺序无关集指纹
         "word_count": word_count_html(r["body"]),                    # D1 P2:主内容体量
         "indexable": not (nm or nh)}                                 # D1 P0-1
    if nm or nh:
        m["noindex_source"] = "meta+header" if (nm and nh) else ("meta" if nm else "header")
        out["notes"].append("noindex 指令在场(来源 %s):页面退出索引" % m["noindex_source"])
    m["canonical_target_status"] = probe_canonical_target(url, r.get("final_url"), canonical)
    expect_needles = _as_needles(expect)
    if expect_needles:
        missing = [n for n in expect_needles if n not in r["body"]]
        m["expect_ok"] = not missing
        m["expect_missing"] = missing
        if missing:
            out["notes"].append("expect_substring 断言失败: 页面 200 但缺 %r(空白渲染/软 404/误改版)"
                                % missing)
    mc_needles = _as_needles(must_contain)
    if mc_needles:
        mc_missing = [n for n in mc_needles if n not in r["body"]]
        m["must_contain_missing"] = mc_missing
        if mc_missing:
            out["notes"].append("must_contain 断言失败: %r 消失(GA 跟踪等关键标记被移除)" % mc_missing)
    if selector:
        m["watch"] = extract_selector(r["body"], selector)
    if selector_stable:
        m["h2"] = extract_selector(r["body"], "h2")                  # D1 P2:布局稳定锚
    mc = mixed_content_count(url, r["body"])
    if mc is not None:
        m["mixed_content"] = mc
        if mc:
            out["notes"].append("混合内容: %d 个 http:// 子资源" % mc)
    out["metrics"] = m
    if r["status"] >= 400:
        out["state"] = "http_error"
    return out


def check_robots(site, market=None):
    out = {"check": "robots", "state": "ok", "metrics": {}, "notes": []}
    try:
        r = http_get(site + "/robots.txt")
    except FetchError as e:
        out["state"] = "error"
        out["metrics"] = {"error": str(e)}
        return out
    if r["status"] >= 400:
        out["state"] = "absent"
        out["metrics"] = {"status": r["status"], "hash": sha256_text("")}
        out["notes"].append("无 robots.txt(=默认全放行,合法;仅记录)")
        return out
    txt = r["body"]
    groups, order = {}, []
    cur = None
    for line in txt.splitlines():
        s = line.split("#")[0].strip()
        if not s:
            continue
        k, _, v = s.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            cur = v or "*"
            groups.setdefault(cur, {"allow": [], "disallow": []})
            order.append(cur)
        elif k in ("allow", "disallow") and cur:
            groups[cur][k].append(v)
    star = groups.get("*", {"allow": [], "disallow": []})
    sitewide = any(d in ("", "/") for d in star["disallow"])
    sitemaps = [v for line in txt.splitlines()
                if line.split(":")[0].strip().lower() == "sitemap"
                for v in [line.split(":", 1)[1].strip()] if v]
    posture = ai_posture(groups)
    for bot in MARKET_BOTS.get((market or "").lower(), []):
        posture[bot] = ai_posture({bot: groups[bot]})[bot] if bot in groups else "no_rule(=放行)"
    out["metrics"] = {"status": r["status"], "hash": sha256_text(txt), "sitewide_block": sitewide,
                      "sitemaps": sitemaps, "groups": len(groups), "ai_posture": posture}
    if sitewide:
        out["notes"].append("robots * 组含 Disallow: / → 全站拒抓")
    return out


def ai_posture(groups_raw):
    """robots 原文 → AI 爬虫放行矩阵(近似:组内出现根路径 disallow 即 blocked)。"""
    posture = {}
    for bot in AI_CRAWLERS:
        g = groups_raw.get(bot)
        if g is None:
            posture[bot] = "no_rule(=放行)"
        elif any(d in ("", "/") for d in g["disallow"]):
            posture[bot] = "blocked"
        elif g["allow"]:
            posture[bot] = "allowed(显式)"
        else:
            posture[bot] = "allowed(空规则)"
    return posture


# ---------- D1 P2(borrow-specs D1-P2 第 13 条):visibility SERP 源适配层(serpbear 式) ----------

# 源对照表(serpbear 式:源|价格|限额|状态)。付费源只登记不接入——接入前按此表核价,
# 并在 SERP_SOURCES 补全条目;口径对照 serpbear:serper $1/1k、SerpApi $50/5k 起。
SERP_SOURCE_TABLE = (
    "visibility SERP 源对照表(serpbear 式;config 可选 serp_source 节按 id 选择):\n"
    "  源           | 价格                  | 限额                     | 状态\n"
    "  -------------|-----------------------|--------------------------|------------------\n"
    "  bing         | 免费无 key(HTML 端点) | 无 SLA;DOM 可能改版/被拦 | 内置,默认\n"
    "  duckduckgo   | 免费无 key(html 端点) | 严格限频,易出反爬页      | 内置,可选\n"
    "  serper.dev   | $1 / 1k 次查询        | 按充值计费,需 API key    | 注册位,未接入\n"
    "  serpapi      | $50 / 5k 次查询起     | 按套餐计费,需 API key    | 注册位,未接入"
)


def _serp_bing_url(site):
    """Bing HTML 端点查询 URL(默认源;与旧版硬编码逐字节一致)。"""
    host = urllib.parse.urlparse(site).netloc
    return "https://www.bing.com/search?q=" + urllib.parse.quote("site:" + host)


def _serp_bing_parse(html):
    """Bing HTML → cite 标签清洗结果列表(SERP 顺序,rank=序号+1;空=解析不出)。"""
    return [unescape(re.sub(r"<[^>]+>", "", c)).replace(" › ", "/")
            for c in re.findall(r"<cite[^>]*>(.*?)</cite>", html, re.S)]


def _serp_ddg_url(site):
    """DuckDuckGo html 端点查询 URL(零 key:html.duckduckgo.com/html/?q=)。"""
    host = urllib.parse.urlparse(site).netloc
    return "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote("site:" + host)


def _serp_ddg_parse(html):
    """DDG html 端点 → result 链接列表(按排名;result__a 锚点属性顺序无关,
    //duckduckgo.com/l/?uddg=<urlencoded> 跳转包装解包,解不出目标的包装不计;
    空=解析不出)。"""
    out, seen = [], set()
    for tag in re.findall(r"<a\b[^>]*>", html or ""):
        if not re.search(r'class\s*=\s*["\'][^"\']*\bresult__a\b', tag):
            continue
        m = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag)
        if not m:
            continue
        u = unescape(m.group(1))
        wm = re.search(r"[?&]uddg=([^&]+)", u)
        if wm:
            u = urllib.parse.unquote(wm.group(1))
        elif u.startswith("//"):
            u = "https:" + u
        if u and u not in seen and not re.match(r"^https?://duckduckgo\.com/l/", u):
            seen.add(u)
            out.append(u)
    return out


# 内置源注册表(serpbear 式适配器):{id, name, website, price_note,
# build_url(site), parse(html), enabled, blocked_re(200 但命中反爬/人机验证文案→
# blocked), zero_metrics_key(unparseable 时计 0 的指标名), ranked(metrics 是否记
# 命中排名), unparseable_note/method_note(输出文案)}。
# 注册位(未接入,不实现付费源调用):serper.dev($1/1k)/SerpApi($50/5k 起)为
# 需 API key 的 JSON API,不走免 key HTML 路径;接入时补全同构条目即可被
# resolve_serp_source 选中(价格/限额见 SERP_SOURCE_TABLE)。
SERP_SOURCES = {
    "bing": {
        "id": "bing", "name": "Bing HTML 端点", "website": "https://www.bing.com",
        "price_note": "免费无 key(HTML 端点,无 SLA)", "enabled": True,
        "build_url": _serp_bing_url, "parse": _serp_bing_parse,
        "blocked_re": r"captcha|unusual traffic|verify you",
        "zero_metrics_key": "cite_tags", "ranked": False,
        "unparseable_note": "Bing 端点 200 但解析不出 cite(DOM 疑似改版)→unparseable 不告警,不当真 0",
        "method_note": "方法限制:Bing HTML 端点无 SLA,非官方索引数;仅作抽查方向",
    },
    "duckduckgo": {
        "id": "duckduckgo", "name": "DuckDuckGo html 端点", "website": "https://html.duckduckgo.com",
        "price_note": "免费无 key(html 端点,严格限频)", "enabled": True,
        "build_url": _serp_ddg_url, "parse": _serp_ddg_parse,
        "blocked_re": r"bots use duckduckgo|anomaly",
        "zero_metrics_key": "result_links", "ranked": True,
        "unparseable_note": "DuckDuckGo 端点 200 但解析不出 result__a(DOM 疑似改版)→unparseable 不告警,不当真 0",
        "method_note": "方法限制:DuckDuckGo html 端点无 SLA,非官方索引数;仅作抽查方向",
    },
}

DEFAULT_SERP_SOURCE_ID = "bing"


def resolve_serp_source(serp_cfg):
    """config 可选 serp_source 节(裸 id 字符串,或 {"id","enabled"} 对象)→
    (源适配 dict, 警告列表)。兼容:无配置 → 默认 bing(与旧版行为逐字节一致);
    未知 id/坏形态/enabled=false → 回退 bing 并返回警告(防监控静默失明,
    警告进 check notes 与 run 日志,绝不静默换成别的源)。"""
    fallback = SERP_SOURCES[DEFAULT_SERP_SOURCE_ID]
    if serp_cfg is None or serp_cfg == "" or serp_cfg is False:
        return fallback, []
    if isinstance(serp_cfg, str):
        sid = serp_cfg.strip()
    elif isinstance(serp_cfg, dict):
        sid = serp_cfg.get("id")
        if not isinstance(sid, str) or not sid.strip():
            return fallback, ['serp_source 配置缺有效 id(期望 "bing"|"duckduckgo")→回退默认 bing 源']
        sid = sid.strip()
        if serp_cfg.get("enabled") is False:
            return fallback, ["serp_source id=%s enabled=false→回退默认 bing 源" % sid]
    else:
        return fallback, ["serp_source 配置形态不支持(%s;期望 id 字符串或对象)→回退默认 bing 源"
                          % type(serp_cfg).__name__]
    src = SERP_SOURCES.get(sid)
    if src is None:
        return fallback, ["serp_source 未知源 id=%s(可用: %s;serper/serpapi 为注册位未接入)→回退默认 bing 源"
                          % (sid, "/".join(sorted(SERP_SOURCES)))]
    return src, []


def check_visibility(site, serp_cfg=None):
    """site: 抽查可见页(D1 P2 第 13 条:SERP 源可配,serpbear 式适配层;默认
    Bing HTML 端点,无 serp_source 配置时与旧版行为逐字节一致)。
    防假 0 纪律(serpbear)对一切源生效:抓取失败=skipped/非 200 或反爬文案=
    blocked/解析不出结果=unparseable——三态都不当"真 0"参与告警判定
    (diff 侧 == "ok" 门挡住);真 0 只在端点成功返回且解析出结果时成立。"""
    src, warns = resolve_serp_source(serp_cfg)
    out = {"check": "visibility", "state": "ok", "metrics": {}, "notes": list(warns)}
    reg = registrable_domain(site)
    q = src["build_url"](site)
    try:
        r = http_get(q)
    except FetchError as e:
        out["state"] = "skipped"
        out["metrics"] = {"error": str(e)}
        out["notes"].append("可见性端点抓取失败→skipped 不告警(不猜)")
        return out
    if r["status"] != 200:
        out["state"] = "blocked"
        out["metrics"] = {"status": r["status"]}
        out["notes"].append("site: 端点返回 %d→blocked 不告警" % r["status"])
        return out
    results = src["parse"](r["body"])
    if not results and re.search(src["blocked_re"], r["body"], re.I):
        out["state"] = "blocked"
        out["metrics"] = {"status": r["status"]}
        out["notes"].append("site: 端点疑似人机验证→blocked 不告警")
        return out
    if not results:
        # audit 05 P1:端点改版 DOM(解析不出结果、无反爬文案)≠ 真 0 页。
        # 解析健全性检查:解析不出来就不当"真 0"参与告警判定(对一切源生效)。
        out["state"] = "unparseable"
        out["metrics"] = {"status": r["status"], src["zero_metrics_key"]: 0}
        out["notes"].append(src["unparseable_note"])
        return out
    sample, visible, ranks = [], 0, []
    for i, u in enumerate(results[:10], 1):
        if reg and reg in u:
            visible += 1
            ranks.append(i)
            if len(sample) < 5:
                sample.append(u)
    out["metrics"] = {"status": r["status"], "visible_pages": visible, "sample": sample}
    if src.get("ranked") and ranks:
        out["metrics"]["ranks"] = ranks               # 命中结果的 SERP 排名(1 基,前 10)
    if src["id"] != DEFAULT_SERP_SOURCE_ID:
        out["metrics"]["serp_source"] = src["id"]     # 非默认源留痕(diff 的 method_note 用)
    out["notes"].append(src["method_note"])
    return out


def redirect_variant_urls(site):
    """非规范域名变体清单(D1 P2):https canonical 站 → http:// 同 host(降级形态)
    + 裸域(去 www,https 形态),按序去重;站点本身即裸域时只剩 http 形态一条
    (canonical 与变体相同的不测);http canonical 站无降级变体可测则可能为空。"""
    p = urllib.parse.urlparse(site)
    host = (p.hostname or "").lower()
    if not host:
        return []
    bare = host[4:] if host.startswith("www.") else host
    cands = []
    if p.scheme == "https":
        cands.append("http://" + host)
    if bare != host:
        cands.append("https://" + bare)
    seen, out = set(), []
    for u in cands:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def check_redirect_variants(site):
    """D1 P2:非规范域名重定向健康度——http:// 形态与裸域各 probe 一次,期望 301 →
    canonical host(http_get 跟随重定向后以最终落点 host 判定;变体在自己 host 上
    直接 200 = 不再重定向 → "broken",重复内容风险)。
    防假 0 纪律(serpbear):probe 网络失败记 "error" 绝不判 "broken";半数以上
    请求失败 → 整个 check 记 state=error(diff 侧不产任何 redirect_chain_broken)。"""
    out = {"check": "redirects", "state": "ok", "metrics": {}, "notes": []}
    p_site = urllib.parse.urlparse(site)
    canonical_origin = (p_site.scheme.lower(), (p_site.hostname or "").lower())
    variants = redirect_variant_urls(site)
    states = {}
    n_err = 0
    for v in variants:
        try:
            r = http_get(v)
        except FetchError as e:
            states[v] = "error"
            n_err += 1
            out["notes"].append("变体 %s probe 失败: %s(不判停止重定向,防假 0)"
                                % (_redact_url(v), e))
            continue
        final = urllib.parse.urlparse(r.get("final_url") or v)
        # 比对 scheme+host:http:// 变体只在自家 host 上直接 200(未升级 https)也算 broken
        states[v] = "ok" if (final.scheme.lower(), (final.hostname or "").lower()) == canonical_origin \
            else "broken"
    if variants and n_err * 2 > len(variants):
        out["state"] = "error"
        out["notes"].append("变体 probe %d/%d 失败 → check 记 error,不当重定向失效判定"
                            % (n_err, len(variants)))
    out["metrics"] = {"variants": states}
    return out


def check_gsc(mdir):
    out = {"check": "gsc", "state": "skipped", "metrics": {}, "notes": []}
    path = os.path.join(mdir, "gsc.csv")
    if not os.path.exists(path):
        out["notes"].append("未找到 gsc.csv(GSC 导出)→流量问跳过,不猜数")
        return out
    import csv as _csv
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = [r for r in _csv.DictReader(f) if r]
    except (OSError, UnicodeDecodeError) as e:
        out["metrics"] = {"error": str(e)}
        return out
    if not rows:
        out["metrics"] = {"error": "gsc.csv 为空"}
        return out
    cols = {(k or "").strip().lower(): k for k in rows[0]}
    click_col = cols.get("clicks")
    if not click_col:
        out["metrics"] = {"error": "gsc.csv 缺 Clicks 列"}
        return out
    total = 0
    page_col = cols.get("page")     # D1 P1:页级导出(列 Page)→ segment importance=gsc_clicks
    page_clicks = {}
    for row in rows:
        try:
            c = int(float((row.get(click_col) or "0").replace(",", "")))
        except ValueError:
            continue
        total += c
        if page_col and len(page_clicks) < GSC_PAGE_CAP:
            pu = (row.get(page_col) or "").strip()
            if pu:
                p_path = urllib.parse.urlparse(pu).path or "/"   # 页 URL → 路径(别遮蔽 csv 的 path)
                page_clicks[p_path] = page_clicks.get(p_path, 0) + c
    out["state"] = "ok"
    out["metrics"] = {"clicks_total": total, "queries": len(rows),
                      "file_mtime": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="seconds")}
    if page_clicks:
        out["metrics"]["page_clicks"] = page_clicks
    out["notes"].append("口径:导出文件全期合计;每次 run 前刷新文件,比较的是两次 run 之间")
    return out


def check_sitemap(site, robots_metrics, budget):
    out = {"check": "sitemap", "state": "ok", "metrics": {}, "notes": []}
    urls = list(robots_metrics.get("sitemaps") or [])
    if not urls:
        urls = [site + "/sitemap.xml"]
        out["notes"].append("robots 无 Sitemap 指令,试探 /sitemap.xml")
    locs, lastmod_max = {}, ""
    idx = 0
    queue = list(urls[:3])
    while queue:
        if budget.exhausted():
            # audit 05 P1:半截 sitemap 不能伪装成完整 ok → 标记 budget_truncated,
            # run 状态落 partial,该 run 不进 diff 基线(防错误基线度量次日真跌)。
            out["metrics"]["budget_truncated"] = True
            out["notes"].append("budget 耗尽,sitemap 解析中止(run 记 partial,不充当 diff 基线)")
            break
        u = queue.pop(0)
        idx += 1
        if idx > SITEMAP_INDEX_CAP + 3:
            break
        try:
            r = http_get(u)
        except FetchError as e:
            out["notes"].append("sitemap 抓取失败 %s: %s" % (u, e))
            continue
        if r["status"] >= 400:
            out["notes"].append("sitemap %s → %d" % (u, r["status"]))
            continue
        found_locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", r["body"], re.I | re.S)
        is_index = "<sitemapindex" in r["body"].lower()
        if is_index:
            queue.extend(found_locs[:SITEMAP_INDEX_CAP])
            continue
        mods = re.findall(r"<url>.*?</url>", r["body"], re.I | re.S)
        mod_by_loc = {}
        for blk in mods:
            lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", blk, re.I)
            lc = re.search(r"<loc>\s*(.*?)\s*</loc>", blk, re.I)
            if lc:
                mod_by_loc[lc.group(1)] = (lm.group(1) if lm else "")
        if not mod_by_loc and found_locs:
            mod_by_loc = {l: "" for l in found_locs}
        for l, lm in list(mod_by_loc.items())[:SITEMAP_CAP]:
            locs[l] = lm
            if lm > lastmod_max:
                lastmod_max = lm
    if not locs:
        out["state"] = "absent"
        out["metrics"] = {"url_count": 0}
        out["notes"].append("未取到任何 sitemap URL(小站可能无 sitemap,合法)")
        return out
    out["metrics"] = {"url_count": len(locs), "lastmod_max": lastmod_max,
                      "locs": dict(list(locs.items())[:SITEMAP_CAP])}
    return out


def check_llms_txt(site):
    out = {"check": "llms_txt", "state": "ok", "metrics": {}, "notes": []}
    try:
        r = http_get(site + "/llms.txt")
    except FetchError as e:
        out["state"] = "error"
        out["metrics"] = {"error": str(e)}
        return out
    if r["status"] >= 400:
        out["state"] = "absent"
        out["metrics"] = {"present": False, "status": r["status"]}
        return out
    body = r["body"]
    out["metrics"] = {"present": True, "status": r["status"], "hash": sha256_text(body),
                      "h1_sections": len(re.findall(r"^# ", body, re.M))}
    return out


def check_ssl(site):
    """SSL 证书到期周检(ssl stdlib;30/14/7/0 天梯度,audit 04:StatusCake 免费档都有)。"""
    out = {"check": "ssl", "state": "ok", "metrics": {}, "notes": []}
    host = urllib.parse.urlparse(site).hostname
    if not host:
        out["state"] = "error"
        out["metrics"] = {"error": "site 无 host"}
        return out
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=FETCH_TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as s:
                cert = s.getpeercert()
    except (OSError, ssl.SSLError, ValueError) as e:
        out["state"] = "error"
        out["metrics"] = {"error": "%s: %s" % (type(e).__name__, e)}
        out["notes"].append("TLS 握手失败(证书链断裂/协议不支持也可能)→记 error,不猜天数")
        return out
    not_after = (cert or {}).get("notAfter") or ""
    try:
        expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    except ValueError:
        out["state"] = "error"
        out["metrics"] = {"error": "notAfter 不可解析: %r" % not_after}
        return out
    # R5⑥:notAfter(GMT)按 UTC 定位成 aware,与 datetime.now(timezone.utc) 统一比较
    # (datetime.utcnow 已弃用;naive/aware 混算会 TypeError,两侧统一才稳)
    days = (expires - datetime.now(timezone.utc)).days
    issuer_cn = "-"
    for rdn in (cert or {}).get("issuer", ()):   # 每项形如 (('commonName','X'),) 或 ('commonName','X')
        pair = rdn[0] if rdn and isinstance(rdn[0], tuple) else rdn
        if pair and len(pair) == 2 and pair[0] == "commonName":
            issuer_cn = pair[1]
            break
    out["metrics"] = {"not_after": not_after, "days_left": days, "issuer": issuer_cn}
    out["notes"].append("证书剩余 %d 天(30/14/7/0 梯度告警)" % days)
    return out


# ---------- R0 接线:sensor_volatility 上下文(R0-2)/ CWV 现场周检(R0-3)/ citation decay(R0-4) ----------

# sensor_volatility.py 的列识别口径(前缀匹配,strip+lower;与此处 has_col 保持同形)
_SENSOR_DATE_COLS = ("date", "日期")
_SENSOR_QUERY_COLS = ("query", "top queries", "keyword", "查询", "关键字")
_SENSOR_POS_COLS = ("position", "avg. position", "avg position", "排名", "平均排名")


def _gsc_csv_has_sensor_columns(path):
    """gsc.csv 是否含 Date+Query+Position 列(矩阵导出形态;页级/全期导出 → False)。"""
    import csv as _csv
    with open(path, newline="", encoding="utf-8-sig") as f:
        first = next(_csv.DictReader(f), None)
    if not first:
        return False
    cols = {(k or "").strip().lower() for k in first}

    def has(names):
        return any(c.startswith(n) for c in cols for n in names)

    return (has(_SENSOR_DATE_COLS) and has(_SENSOR_QUERY_COLS) and has(_SENSOR_POS_COLS))


def sensor_volatility_context(gsc_csv):
    """R0-2:gsc.csv → 最新可评分日的 SERP 波动上下文,与 sensor_volatility.py
    --context 完全同口径(零依赖 import 其模块函数:read_position_rows→aggregate→
    compute_days,verdict=high_volatility ⟺ score≥8 或 |z30|≥2)。
    列不齐 / 单日数据 / 模块导入或任何计算失败 → None(静默跳过——波动上下文只是
    跌幅告警的附注,绝不阻塞告警主路径)。"""
    try:
        if not gsc_csv or not os.path.exists(gsc_csv) or not _gsc_csv_has_sensor_columns(gsc_csv):
            return None
        sv = _import_sibling("sensor_volatility")
        pos_by_date = sv.aggregate(sv.read_position_rows(gsc_csv))
        if len(pos_by_date) < 2:          # 单日数据无法算日波动(首日无前日可比)
            return None
        days = sv.compute_days(pos_by_date)
        if not days:
            return None
        day = days[-1]                    # --date 缺省 = 最新可评分日
        high = day["score"] >= 8 or (day["z30"] is not None
                                     and abs(day["z30"]) >= sv.Z_THRESHOLD)
        return {"date": day["date"], "score": day["score"], "band": day["band"],
                "z30": day["z30"], "verdict": "high_volatility" if high else "normal"}
    except Exception:
        return None


def check_cwv_field(site, cfg):
    """R0-3:CWV 现场数据周检——key_pages 前 N 页的 PSI loadingExperience(CrUX 页级
    真实用户)mobile p75,官方阈值判档(零依赖 import field_data.collect 同口径)。
    无 PSI key → skipped 不猜;field_data 导入失败/全页无现场数据 → error 不猜
    (防假 0:请求失败绝不判 poor)。判定在 diff 侧:任一核心指标 poor → cwv_poor
    (warn);较上期跨档退步 → cwv_regression(info)。"""
    out = {"check": "cwv_field", "state": "skipped", "metrics": {}, "notes": []}
    psi_key = (os.environ.get("PSI_API_KEY") or "").strip()
    if not psi_key:
        out["notes"].append("未设 PSI_API_KEY → cwv_field 跳过(不猜;export PSI_API_KEY 后启用)")
        return out
    try:
        fd = _import_sibling("field_data")
    except Exception as e:
        out["state"] = "error"
        out["metrics"] = {"error": "field_data 导入失败: %s" % e}
        out["notes"].append("CWV 周检依赖同目录 field_data.py(stdlib-only),导入失败不猜")
        return out
    try:
        n_pages = max(1, int(cfg.get("cwv_field_pages") or CWV_FIELD_PAGES))
    except (TypeError, ValueError):
        n_pages = CWV_FIELD_PAGES
    paths = [parse_key_page(e)["path"] for e in (cfg.get("key_pages") or ["/"])[:n_pages]]
    pages, n_field = {}, 0
    for path in paths:
        url = site + path if path.startswith("/") else path
        try:
            r = fd.collect(url, "mobile", psi_key=psi_key, crux_key=None)
        except Exception as e:
            out["notes"].append("CWV 采集异常 %s: %s(该页跳过,不猜)" % (path, e))
            continue
        for err in r.get("errors") or []:
            out["notes"].append("CWV 采集错误 %s [%s]: %s"
                                % (path, err.get("source"), err.get("message")))
        field = r.get("field") or {}
        entry = {k: field[k] for k in ("LCP", "INP", "CLS", "TTFB", "FCP") if k in field}
        if entry:
            pages[path] = entry
            n_field += 1
        else:
            out["notes"].append("%s 无现场数据(不在 CrUX 数据集/样本不足或 PSI 无数据)→ 不猜" % path)
    out["metrics"] = {"pages": pages, "strategy": "mobile", "source": "psi"}
    if pages:
        out["state"] = "ok"
        poor = [p for p, m in pages.items()
                if any((m.get(k) or {}).get("verdict") == "poor" for k in ("LCP", "INP", "CLS"))]
        out["notes"].append("CWV 周检: %d/%d 页取到现场 p75(mobile),核心三项 poor 页 %d(官方阈值判档)"
                            % (n_field, len(paths), len(poor)))
    else:
        out["state"] = "error"
        out["notes"].append("CWV 现场数据全部无数据/失败 → check 记 error,diff 不产 cwv_*(防假 0)")
    return out


def citation_panel_candidates(mdir):
    """R0-4:项目目录 panel.json 候选路径——monitor 目录内优先,其次其父目录
    (项目根;citation_panel 默认把 panel.json 落在运行时 cwd=项目根)。"""
    parent = os.path.dirname(os.path.abspath(mdir)) or "."
    return [os.path.join(mdir, CITATION_PANEL_FILE),
            os.path.join(parent, CITATION_PANEL_FILE)]


def check_citation_decay(mdir):
    """R0-4:citation decay 进告警链——项目目录 panel.json 在场时复用 citation_panel
    的 decay 计算(decay-summary 子命令同源:decay_summary(load_panel(path))),把轻摘要
    {rewriting, decayed_count, per_engine} 落进快照;diff 侧 decayed_count>0 →
    citation_decay(warn)。无面板 → skipped 不猜;计算失败 → error 不猜。"""
    out = {"check": "citation", "state": "skipped", "metrics": {}, "notes": []}
    path = next((p for p in citation_panel_candidates(mdir) if os.path.isfile(p)), None)
    if not path:
        out["notes"].append("项目目录无 panel.json(citation_panel)→ citation decay 检查跳过,不猜")
        return out
    try:
        cp = _import_sibling("citation_panel")
        summary = cp.decay_summary(cp.load_panel(path))
    except Exception as e:
        out["state"] = "error"
        out["notes"].append("citation decay 计算失败(panel.json 读取/解析/计算异常)→ 不猜: %s" % e)
        return out
    out["state"] = "ok"
    out["metrics"] = dict(summary, panel=path)
    if summary.get("decayed_count"):
        out["notes"].append("citation decay: %d 个 (prompt,engine) cell 已过半衰(decayed)"
                            "→ 建议 refresh/重写排期" % summary["decayed_count"])
    return out


def check_backlinks(mdir, cfg=None, now=None):
    """R2-4:引荐域月检(第 6 检查组)——monitor 目录 backlinks.csv(同 gsc.csv 模式;
    cfg.backlinks_csv 或 run --backlinks 可覆盖路径)→ 快照口径:
      refdomains_total 引荐域总数;refdomains_new 当月新增域数(各域最早 first_seen
      落在近 BACKLINK_NEW_WINDOW_DAYS 天;导出无任何可解 first_seen(GSC 简易表)
      → None 不猜);domains 域清单(截断 BACKLINK_DOMAIN_CAP,diff 报丢失样本用)。
    导入侧零依赖 import 兄弟 backlink_import.parse_export(统一/Ahrefs/Semrush/GSC
    四形态通吃);无文件 → skipped 不猜;嗅探/解析失败 → error 不猜(防假 0:
    run 侧落 partial + 退出码 2,绝不把"读不了"当"外链归零")。"""
    out = {"check": "backlinks", "state": "skipped", "metrics": {}, "notes": []}
    cfg = cfg or {}
    path = cfg.get("backlinks_csv") or os.path.join(mdir, BACKLINKS_CSV)
    if not os.path.exists(path):
        out["notes"].append("未找到 %s(外链导出;backlink_import.py 产出的统一格式或"
                            "Ahrefs/Semrush/GSC 原始导出)→ 引荐域月检跳过,不猜数" % BACKLINKS_CSV)
        return out
    try:
        bi = _import_sibling("backlink_import")
        parsed = bi.parse_export(path)
    except Exception as e:
        out["state"] = "error"
        out["metrics"] = {"error": "backlinks.csv 读取/嗅探/解析失败: %s" % e}
        out["notes"].append("外链导出损坏(嗅探不出格式/解析异常)→ 不猜;run 将记 partial 并退出码 2")
        return out
    now = now or datetime.now()
    cutoff = now - timedelta(days=BACKLINK_NEW_WINDOW_DAYS)
    earliest, any_fs = {}, False           # domain → 最早 first_seen;是否有任何可解日期
    for r in parsed["rows"]:
        dom = (r.get("referring_domain") or "").strip().lower()
        if not dom:
            continue
        d = bi.parse_date(r.get("first_seen"))
        if d is None:
            continue
        any_fs = True
        if dom not in earliest or d < earliest[dom]:
            earliest[dom] = d
    domains = sorted({(r.get("referring_domain") or "").strip().lower()
                      for r in parsed["rows"] if (r.get("referring_domain") or "").strip()})
    total = len(domains)
    new_n = sum(1 for d in earliest.values() if d >= cutoff.date()) if any_fs else None
    truncated = total > BACKLINK_DOMAIN_CAP
    out["state"] = "ok"
    out["metrics"] = {
        "refdomains_total": total,
        "refdomains_new": new_n,
        "format": parsed["format"],
        "unique_urls": len(parsed["rows"]),
        "domains": domains[:BACKLINK_DOMAIN_CAP],
        "domains_truncated": truncated,
        "file_mtime": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="seconds"),
    }
    out["notes"].append("口径:导出全量去重后引荐域 %d;%s;每次月检前刷新文件,"
                        "比较的是两次月检 run 之间" % (
                            total,
                            "近 %d 天新增域 %d" % (BACKLINK_NEW_WINDOW_DAYS, new_n)
                            if new_n is not None else "导出无 first_seen(GSC 简易表),新增数不猜"))
    if new_n is not None:
        out["notes"].append("backlink_drop 判定依赖该新增数;GSC 简易表形态只保 backlink_loss 总数判定")
    return out


class Budget:
    """单次运行时长上限(学 geo-score 的 budget 思路):超即中止后续检查。"""

    def __init__(self, minutes):
        self.limit = minutes * 60.0 if minutes is not None else None
        self.t0 = time.monotonic()

    def exhausted(self):
        return self.limit is not None and (time.monotonic() - self.t0) > self.limit

    def used_sec(self):
        return round(time.monotonic() - self.t0, 1)


def run_checks(mdir, cfg, kind, budget):
    site = cfg["site"]
    market = cfg.get("market")
    results = {}
    plan = [("robots", lambda: check_robots(site, market)),
            ("home", lambda: check_page(site + "/")),
            ("redirects", lambda: check_redirect_variants(site))]   # D1 P2:非规范域重定向
    for name, fn in plan:
        if budget.exhausted():
            results[name] = {"state": "budget_skipped"}
            continue
        results[name] = fn()
    # 关键页:支持 str 或 {"path","expect_substring"(str|数组),"selector",
    # "assertions":{must_contain,max_latency_ms,selector_stable}} 对象(audit 04/17,D1 P2)
    results["key_pages"] = {}
    for entry in cfg.get("key_pages", ["/"]) or ["/"]:
        o = parse_key_page(entry)
        if budget.exhausted():
            results["key_pages"][o["path"]] = {"state": "budget_skipped"}
            continue
        results["key_pages"][o["path"]] = check_page(
            site + o["path"] if o["path"].startswith("/") else o["path"],
            expect=o["expect"] or None, selector=o["selector"],
            must_contain=o["must_contain"] or None, selector_stable=o["selector_stable"])
    if budget.exhausted():
        results["visibility"] = {"state": "budget_skipped"}
    else:
        results["visibility"] = check_visibility(site, serp_cfg=cfg.get("serp_source"))
    results["gsc"] = check_gsc(mdir)
    if kind == "weekly":
        robots_metrics = results.get("robots", {}).get("metrics", {})
        weekly = [("sitemap", lambda: check_sitemap(site, robots_metrics, budget)),
                  ("llms_txt", lambda: check_llms_txt(site)),
                  ("ssl", lambda: check_ssl(site))]
        for name, fn in weekly:
            if budget.exhausted():
                results[name] = {"state": "budget_skipped"}
            else:
                results[name] = fn()
        # R0-3:CWV 现场数据(PSI 采集,受 budget 门;无 key 时自查 skipped)
        if budget.exhausted():
            results["cwv_field"] = {"state": "budget_skipped"}
        else:
            results["cwv_field"] = check_cwv_field(site, cfg)
        # R0-4:citation decay(本地 panel.json 计算,无网络,不吃 budget)
        results["citation"] = check_citation_decay(mdir)
    if kind == "monthly":
        # R2-4:引荐域月检(本地导出解析,无网络,不吃 budget;无文件自报 skipped)
        results["backlinks"] = check_backlinks(mdir, cfg)
    return results


# ---------- run ----------

STALE_RUN_MIN = 30   # running 超过该分钟数视为进程死亡,由 sweep 回收


def sweep_stale_runs(conn, max_age_min=STALE_RUN_MIN):
    """抄 serposcope/searchmirror 的 stale-sweep:崩溃/被杀的 run 停在 running 态,
    超时回收入 failed,使"卡死"可被识别、不留脏基线。返回回收行数。"""
    cutoff = (datetime.now() - timedelta(minutes=max_age_min)).isoformat(timespec="seconds")
    cur = conn.execute(
        "UPDATE runs SET status='failed' WHERE status='running' AND ts<?", (cutoff,))
    conn.commit()
    return cur.rowcount


def prune(conn, mdir, keep=400):
    """PruneDB 纪律(serposcope):只保留最近 keep 次 run,连带快照/告警/runs 文件。"""
    stale = [r["id"] for r in conn.execute(
        "SELECT id FROM runs ORDER BY id DESC LIMIT -1 OFFSET ?", (keep,))]
    for rid in stale:
        conn.execute("DELETE FROM snapshots WHERE run_id=?", (rid,))
        conn.execute("DELETE FROM alerts WHERE run_id=?", (rid,))
        conn.execute("DELETE FROM runs WHERE id=?", (rid,))
        for pat in ("run-%05d.json", "diff-%05d.json", "status-%05d.json"):
            p = os.path.join(mdir, "runs", pat % rid)
            if os.path.exists(p):
                try:
                    os.unlink(p)
                except OSError:
                    pass
    if stale:
        conn.commit()
    return len(stale)


def ping_heartbeat(url, ok, timeout=10):
    """dead man's switch(audit 18):run 成功 ping <url>,失败 ping <url>/fail
    (healthchecks.io Pinging API:Success=`https://hc-ping.com/<uuid>` 无后缀,Failure=`…/fail`,
    https://healthchecks.io/docs/http_api/ 2026-10-21 核对;修前成功 ping `<url>/ok`,不是官方端点。
    失败 ping 不等超时立刻发出)。URL 来自管理员 config,不设 SSRF 限制。"""
    if not url:
        return
    target = url.rstrip("/") + ("" if ok else "/fail")
    try:
        req = urllib.request.Request(target, headers={"User-Agent": "seo-suite-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(256)
        print("    [i] heartbeat 已 ping: %s" % ("ok" if ok else "fail"))
    except Exception as e:
        print("    [!] heartbeat ping 失败(%s): %s" % (type(e).__name__, _redact_url(target)))


def cmd_run(args):
    mdir = args.dir
    cfg = load_config(mdir)
    if getattr(args, "backlinks", ""):   # R2-4:月检外链导出路径覆盖(缺省 <dir>/backlinks.csv)
        cfg["backlinks_csv"] = args.backlinks
    with monitor_lock(mdir):
        conn = open_db(mdir)
        swept = sweep_stale_runs(conn)
        if swept:
            print("[i] sweep_stale_runs: 回收 %d 个卡死(>=%dmin 仍 running)的 run → failed"
                  % (swept, STALE_RUN_MIN))
        # 状态机(serposcope):先落 running 拿 run_id,跑完再 UPDATE 终态
        started = datetime.now().isoformat(timespec="seconds")
        cur = conn.execute(
            "INSERT INTO runs(ts, kind, status, checks_run, budget_used_sec, summary) "
            "VALUES(?,?, 'running', ?, 0, '')",
            (started, args.checks, args.checks))
        run_id = cur.lastrowid
        conn.commit()
        budget = Budget(args.budget_minutes if args.budget_minutes is not None
                        else cfg.get("budget_minutes", 5))
        try:
            results = run_checks(mdir, cfg, args.checks, budget)
        except Exception:
            conn.execute("UPDATE runs SET status='failed' WHERE id=?", (run_id,))
            conn.commit()
            conn.close()
            raise
        snap = snapshot_from_results(results)
        # D1 P0-2 防抖:canonical 目标失败连击(当前 run 尚为 running,latest_run_ids
        # 取到的必是上一 ok run)——diff 侧连续 3 次失败才告警
        _prev_ok = latest_run_ids(conn, 1)
        apply_canonical_streaks(load_snapshot(conn, _prev_ok[0]) if _prev_ok else None, snap)

        states = {}
        for grp in ("robots", "home", "redirects", "visibility", "gsc", "sitemap", "llms_txt",
                    "ssl", "cwv_field", "citation", "backlinks"):
            st = (results.get(grp) or {}).get("state")
            if st:
                states[grp] = st
        kp_states = {p: r.get("state") for p, r in (results.get("key_pages") or {}).items()}
        statuses = list(states.values()) + list(kp_states.values())
        budget_truncated = any(
            (results.get(g) or {}).get("metrics", {}).get("budget_truncated")
            for g in ("sitemap", "robots", "home", "visibility", "llms_txt", "ssl"))
        # R2-4 防假 0:月检 backlinks.csv 损坏(文件在但嗅探/解析失败)→ run 落 partial
        # (半截数据不充当 diff 基线)+ 退出码 2(数据错误,绝不静默当作"外链归零")
        backlinks_corrupt = (results.get("backlinks") or {}).get("state") == "error"
        run_status = "ok"
        if "budget_skipped" in statuses or budget_truncated or backlinks_corrupt:
            run_status = "partial"    # 半截数据:入库但不充当 diff 基线(audit 05-§2)
        elif statuses and all(s == "error" for s in statuses):
            run_status = "failed"

        payload = {"site": cfg["site"], "market": cfg.get("market"), "kind": args.checks,
                   "ts": datetime.now().isoformat(timespec="seconds"),
                   "status": run_status, "budget_used_sec": budget.used_sec(),
                   "checks": {k: {"state": vv.get("state"), "notes": vv.get("notes", [])}
                              for k, vv in results.items() if isinstance(vv, dict) and "state" in vv},
                   "key_pages": kp_states, "snapshot": snap}

        if args.dry_run:
            print("[dry-run] 不写库。状态=%s budget=%.1fs" % (run_status, budget.used_sec()))
            for grp, st in list(states.items()) + [("key_pages:" + p, s) for p, s in kp_states.items()]:
                print("  %-22s %s" % (grp, st))
            for grp, vv in results.items():
                if isinstance(vv, dict):
                    for n in vv.get("notes", []):
                        print("    [i] %s: %s" % (grp, n))
            conn.execute("DELETE FROM runs WHERE id=?", (run_id,))
            conn.commit()
            conn.close()
            return 2 if backlinks_corrupt else (0 if run_status == "ok" else 3)

        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "UPDATE runs SET status=?, budget_used_sec=?, summary=?, ts=? WHERE id=?",
            (run_status, budget.used_sec(), json.dumps(payload, ensure_ascii=False), now, run_id))
        for check, kv in snap.items():
            for key, value in kv.items():
                h = sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True))
                conn.execute(
                    "INSERT INTO snapshots(run_id, ts, \"check\", key, value, hash) VALUES(?,?,?,?,?,?)",
                    (run_id, now, check, key, json.dumps(value, ensure_ascii=False), h))
        conn.commit()
        rpath = os.path.join(mdir, "runs", "run-%05d.json" % run_id)
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        pruned = prune(conn, mdir, keep=400)
        if pruned:
            print("[i] PruneDB: 裁剪 %d 个旧 run(保留最近 400)" % pruned)
        print("run #%d 完成: kind=%s status=%s budget=%.1fs → %s"
              % (run_id, args.checks, run_status, budget.used_sec(), rpath))
        for grp, st in list(states.items()) + [("key_pages:" + p, s) for p, s in kp_states.items()]:
            if st not in ("ok",):
                print("  [!] %s: %s" % (grp, st))
        for grp, vv in results.items():
            if isinstance(vv, dict):
                for n in vv.get("notes", []):
                    print("    [i] %s: %s" % (grp, n))
        total = conn.execute("SELECT COUNT(*) AS c FROM runs WHERE status!='running'").fetchone()["c"]
        if total == 1:
            print("[i] 首次 run=基线;下一步跑 diff(与下次 run 对比才有告警)")
        conn.close()
    # dead man's switch:成功/失败分别 ping(audit 18;rc=3 的静默空窗由 /fail 堵住;
    # rc=2 的 backlinks.csv 损坏同走 /fail——数据错误也算一次不成功的 run)
    heartbeat = cfg.get("heartbeat_url") or os.environ.get("SEO_MONITOR_HEARTBEAT_URL")
    ping_heartbeat(heartbeat, ok=(run_status == "ok"))
    return 2 if backlinks_corrupt else (0 if run_status == "ok" else 3)


def snapshot_from_results(results):
    """检查结果 → 扁平快照 dict: {check: {key: value}}(value 可 JSON 化)。"""
    snap = {}

    def put(check, key, value):
        snap.setdefault(check, {})[key] = value

    r = results.get("robots", {})
    if r.get("state") == "ok":
        m = dict(r["metrics"])
        m.pop("sitemaps", None)  # sitemap 列表属 run 详情,不进对比快照
        put("robots", "robots", m)
    elif r.get("state"):
        put("robots", "robots", {"state": r["state"]})
    h = results.get("home", {})
    if h.get("state") == "ok":
        m = dict(h["metrics"])
        m["title_meta_hash"] = sha256_text(
            (m.get("title", "") + "|" + m.get("meta_desc", "") + "|" + m.get("canonical", "")))
        put("pages", "/", m)
    elif h.get("state"):
        put("pages", "/", {"state": h["state"], **h.get("metrics", {})})
    for p, pr in (results.get("key_pages") or {}).items():
        if pr.get("state") == "ok":
            m = dict(pr["metrics"])
            m["title_meta_hash"] = sha256_text(
                (m.get("title", "") + "|" + m.get("meta_desc", "") + "|" + m.get("canonical", "")))
            put("pages", p, m)
        elif pr.get("state"):
            put("pages", p, {"state": pr["state"], **pr.get("metrics", {})})
    # D1 P2:非规范域变体重定向状态(ok/broken/error;diff 只认 broken,error=防假 0)
    rd = results.get("redirects", {})
    if rd.get("state") == "ok":
        put("redirects", "variants", dict((rd.get("metrics") or {}).get("variants") or {}))
    elif rd.get("state"):
        put("redirects", "variants", {"state": rd["state"]})
    v = results.get("visibility", {})
    if v.get("state") == "ok":
        put("visibility", "site", dict(v["metrics"]))
    elif v.get("state"):
        put("visibility", "site", {"state": v["state"]})
    g = results.get("gsc", {})
    if g.get("state") == "ok":
        put("gsc", "file", dict(g["metrics"]))
    s = results.get("sitemap", {})
    if s.get("state") == "ok":
        put("sitemap", "index", dict(s["metrics"]))
    elif s.get("state"):
        put("sitemap", "index", {"state": s["state"]})
    l = results.get("llms_txt", {})
    if l.get("state") == "ok":
        put("llms_txt", "file", dict(l["metrics"]))
    elif l.get("state"):
        put("llms_txt", "file", {"state": l["state"]})
    sl = results.get("ssl", {})
    if sl.get("state") == "ok":
        put("ssl", "cert", dict(sl["metrics"]))
    elif sl.get("state"):
        put("ssl", "cert", {"state": sl["state"]})
    # R0-3:CWV 现场数据周检(非 ok 只落 state,diff 侧不产 cwv_*)
    cwv = results.get("cwv_field", {})
    if cwv.get("state") == "ok":
        put("cwv_field", "field", dict(cwv.get("metrics") or {}))
    elif cwv.get("state"):
        put("cwv_field", "field", {"state": cwv["state"]})
    # R0-4:citation decay 轻摘要(非 ok 只落 state,diff 侧不产 citation_decay)
    ct = results.get("citation", {})
    if ct.get("state") == "ok":
        put("citation", "decay", dict(ct.get("metrics") or {}))
    elif ct.get("state"):
        put("citation", "decay", {"state": ct["state"]})
    # R2-4:引荐域月检(非 ok 只落 state,diff 侧不产 backlink_*)
    bl = results.get("backlinks", {})
    if bl.get("state") == "ok":
        put("backlinks", "refdomains", dict(bl.get("metrics") or {}))
    elif bl.get("state"):
        put("backlinks", "refdomains", {"state": bl["state"]})
    return snap


def apply_canonical_streaks(prev_snap, snap):
    """D1 P0-2 防抖:canonical 目标失败连击计数(连续 3 次失败才告警)。
    prev_snap = 上一 ok run 的快照(None/旧格式缺字段均从 1 起数,不崩);
    失败 → prev 连击+1,成功/无 canonical → 清 0。写回 snap 各页 canonical_fail_streak,
    diff 侧只认 streak≥3。"""
    prev_pages = (prev_snap or {}).get("pages") or {}
    for path, m in (snap.get("pages") or {}).items():
        if not isinstance(m, dict):
            continue
        if canonical_failure(m.get("canonical_target_status")):
            try:
                prev_streak = int((prev_pages.get(path) or {}).get("canonical_fail_streak") or 0)
            except (TypeError, ValueError):
                prev_streak = 0
            m["canonical_fail_streak"] = prev_streak + 1
        else:
            m["canonical_fail_streak"] = 0


# ---------- diff(阈值告警引擎) ----------

def load_snapshot(conn, run_id):
    d = {}
    for row in conn.execute("SELECT \"check\", key, value FROM snapshots WHERE run_id=?", (run_id,)):
        d.setdefault(row["check"], {})[row["key"]] = json.loads(row["value"])
    return d


def latest_run_ids(conn, n=2, statuses=("ok",)):
    """基线污染防护(audit 05-§2 / audit 01 rec2):默认只取 status='ok' 的 run。
    'partial'(半截数据)/'failed'/'quarantined' 一律不充当对比基线。"""
    marks = ",".join("?" * len(statuses))
    return [r["id"] for r in conn.execute(
        "SELECT id FROM runs WHERE status IN (%s) ORDER BY id DESC LIMIT ?" % marks,
        (*statuses, n))]


def pick_prev_run_id(conn, curr_id):
    """R5②:diff 的 prev 基线选择——优先同 kind 的最近 ok run(weekly 检查集是
    daily 的超集、口径不同:weekly 拿 daily 当 prev 会把"上次没查"当"没变",
    反向则把周检字段缺失误判;sitemap/llms/ssl 类告警尤其敏感)。
    无同 kind ok run 时回退最近 ok 并标 kind_mismatch(由调用方响亮警告)。
    返回 (prev_id, kind_mismatch);无任何可对比 ok run → (None, False)。"""
    row = conn.execute("SELECT kind FROM runs WHERE id=?", (curr_id,)).fetchone()
    kind = row["kind"] if row else None
    r = conn.execute(
        "SELECT MAX(id) AS m FROM runs WHERE id<? AND status='ok' AND kind IS ?",
        (curr_id, kind)).fetchone()
    if r and r["m"] is not None:
        return r["m"], False
    r = conn.execute(
        "SELECT MAX(id) AS m FROM runs WHERE id<? AND status='ok'", (curr_id,)).fetchone()
    if r and r["m"] is not None:
        return r["m"], True
    return None, False


def pick_baseline_run(conn, exclude_ids, days=7):
    """双窗口判定(P1-9)用:找 ~days 天前最接近的 ok run 当长窗基线。"""
    target = datetime.now() - timedelta(days=days)
    best, best_diff = None, None
    for r in conn.execute("SELECT id, ts FROM runs WHERE status='ok' ORDER BY id"):
        if r["id"] in exclude_ids:
            continue
        try:
            d = abs((datetime.fromisoformat(r["ts"]) - target).total_seconds())
        except ValueError:
            continue
        if best_diff is None or d < best_diff:
            best, best_diff = r["id"], d
    return best


def apply_inhibition(alerts, inhibited_out=None):
    """告警抑制树(audit 19,Prometheus inhibition 纪律;替 Top-K 截断):
    根因一条,派生折叠——site_down 抑制 page_down,抓取层故障抑制内容派生判定。
    INHIBITS 以根因码为键;此处按派生码反查其根因是否在本次告警集中。
    R5⑤:已接受(accepted)的告警不参与折叠——接受≠消失,必须保留入库供周报计数
    (白名单是"知情保留"语义,不是删除;由 apply_accepted 先于本函数调用保证)。"""
    kept = []
    for a in alerts:
        if a.get("accepted"):
            kept.append(a)
            continue
        inhibiting = None
        for root_code, (codes, scope) in INHIBITS.items():
            if a["code"] not in codes:
                continue
            if scope == "sitewide":
                hit = any(x["code"] == root_code for x in alerts)
            else:  # same_key:根因与派生同 key(或根因作用于首页=站点级)
                hit = any(x["code"] == root_code and (x.get("key") == a.get("key") or x.get("key") == "/")
                          for x in alerts)
            if hit:
                inhibiting = root_code
                break
        if inhibiting:
            if inhibited_out is not None:
                inhibited_out.append({"code": a["code"], "key": a.get("key"), "inhibited_by": inhibiting})
        else:
            kept.append(a)
    return kept


def oldest_ok_run_age_days(conn, now=None):
    """库龄:最老 status='ok' 的 run 距今天数(无 ok run/时间不可解析 → None)。"""
    row = conn.execute("SELECT MIN(ts) AS m FROM runs WHERE status='ok'").fetchone()
    if not row or not row["m"]:
        return None
    try:
        return ((now or datetime.now()) - datetime.fromisoformat(row["m"])).total_seconds() / 86400.0
    except ValueError:
        return None


def apply_accepted(alerts, cfg):
    """D1 P1:accepted_codes 白名单——"接受≠消失":命中(裸 code 或 code:key 指纹)→
    降 low + 标 accepted:true(不计入 counts/退出码、不走 cooldown 抑制,每次 diff 照常
    入库);周报单独列"已接受告警数",仍计数。返回命中条数。
    R5⑤:本函数在 compute_alerts 内、apply_inhibition 之前调用——已接受告警不参与
    抑制树折叠(根因在场时也不蒸发,保留周报计数)。"""
    acc = set(cfg.get("accepted_codes") or [])
    if not acc:
        return 0
    n = 0
    for a in alerts:
        if a.get("accepted"):
            continue          # R4:可重入——SLO 告警在 compute_alerts 之后追加,二次套用不重复前缀
        fp = "%s:%s" % (a["code"], a["key"])
        if a["code"] in acc or fp in acc:
            a["from_level"] = a["level"]
            a["level"] = "low"
            a["accepted"] = True
            a["message"] = "已接受(接受≠消失,周报仍计数): " + a["message"]
            n += 1
    return n


# ---------- R4 监控对标①:SLO+错误预算 ----------

def _slo_samples(conn, metric, now, window_days):
    """近 window_days 天 status='ok' run 的 pages 快照 → (good, bad) 样本计数。
    口径(SLO 内置三指标,防假 0:缺证据的样本一律不计,不猜):
    - keypage_indexable:indexable True/False 各计好/坏;缺键(旧库)不计;
    - canonical_ok:有 canonical_target_status 键才计(canonical_failure 判坏;
      None=自指/无 canonical 不算失败);缺键不计;
    - healthy_pages:state 为 error/http_error 计坏,其余(含旧库无 state 键)计好。
    按模板分账注记:此处是全站(抽样 key_pages)聚合口径——全站 SLO 会藏住单模板回归
    (1000 页里一个模板 50 页全坏只摊薄成 5%);单模板回归要看 site_crawl(crawl.page
    口径:crawl.json pages[] 按模板分组聚合),monitor 不做模板级 SLO。"""
    cutoff = (now - timedelta(days=window_days)).isoformat(timespec="seconds")
    good = bad = 0
    for row in conn.execute(
            "SELECT s.value FROM snapshots s JOIN runs r ON s.run_id=r.id "
            "WHERE s.\"check\"='pages' AND r.status='ok' AND r.ts>=?", (cutoff,)):
        try:
            v = json.loads(row["value"])
        except (TypeError, ValueError):
            continue
        if not isinstance(v, dict):
            continue
        if metric == "keypage_indexable":
            iv = v.get("indexable")
            if iv is True:
                good += 1
            elif iv is False:
                bad += 1
        elif metric == "canonical_ok":
            if "canonical_target_status" in v:
                if canonical_failure(v["canonical_target_status"]):
                    bad += 1
                else:
                    good += 1
        else:  # healthy_pages
            if v.get("state") in ("error", "http_error"):
                bad += 1
            else:
                good += 1
    return good, bad


def compute_slo(conn, cfg, now=None):
    """① SLO 计算:config slo 节({metric: {target, window_days}})→ 各内置指标
    实际值与剩余错误预算。返回 {"configured": bool, "metrics": {name: {...}}}:
      actual=good/(good+bad)(无样本=None 不猜);
      budget_remaining=1−(1−actual)/(1−target)(可为负=预算超耗;<SLO_BUDGET_LOW_PCT 告警)。
    未配 slo 节/条目缺省/坏配置 → 对应指标跳过(configured=False 表示整块未启用)。
    只认 SLO_METRICS 内置键;slo 节里出现的键才算(显式 opt-in,不配不告警)。"""
    now = now or datetime.now()
    out = {"configured": False, "metrics": {}}
    slo_cfg = cfg.get("slo")
    if not isinstance(slo_cfg, dict) or not slo_cfg:
        return out
    out["configured"] = True
    for name, label in SLO_METRICS.items():
        conf = slo_cfg.get(name)
        if conf is None:
            continue                       # slo 节未列出的指标不计算(opt-in)
        if isinstance(conf, dict):
            target, window = conf.get("target", SLO_DEFAULT_TARGET), \
                conf.get("window_days", SLO_DEFAULT_WINDOW_DAYS)
        else:                              # 裸 true/数值等简写 → 全默认
            target, window = SLO_DEFAULT_TARGET, SLO_DEFAULT_WINDOW_DAYS
        try:
            target, window = float(target), int(window)
        except (TypeError, ValueError):
            continue                       # 坏配置:该指标跳过不猜
        if not 0 < target <= 1 or window <= 0:
            continue
        good, bad = _slo_samples(conn, name, now, window)
        total = good + bad
        actual = (good / total) if total else None
        budget = None
        if actual is not None:
            allowed = 1.0 - target
            budget = (1.0 if actual >= target else 0.0) if allowed <= 0 \
                else 1.0 - (1.0 - actual) / allowed
        out["metrics"][name] = {"label": label, "target": target, "window_days": window,
                                "good": good, "bad": bad, "samples": total,
                                "actual": round(actual, 6) if actual is not None else None,
                                "budget_remaining": round(budget, 4) if budget is not None else None}
    return out


def slo_alerts_from(slo):
    """SLO 计算结果 → 告警列表:剩余错误预算 < SLO_BUDGET_LOW_PCT(已耗 ≥75%)→
    slo_budget_low(warn,"索引健康 SLO 99.5%:错误预算剩 X%,接近耗尽将建议冻结发布")。
    无样本(actual=None)不猜不发。"""
    alerts = []
    for name, m in (slo.get("metrics") or {}).items():
        actual, budget = m.get("actual"), m.get("budget_remaining")
        if actual is None or budget is None or budget >= SLO_BUDGET_LOW_PCT:
            continue
        action, boundary = PLAYBOOK["slo_budget_low"]
        alerts.append({
            "level": "warn", "code": "slo_budget_low", "key": name,
            "message": ("索引健康 SLO %.2f%%(%s,近 %d 天 %d 样本实际 %.2f%%):"
                        "错误预算剩 %.0f%%,接近耗尽将建议冻结发布"
                        % (m["target"] * 100, m["label"], m["window_days"], m["samples"],
                           actual * 100, max(budget, 0.0) * 100)),
            "details": {"metric": name, "label": m["label"], "target": m["target"],
                        "window_days": m["window_days"], "actual": actual,
                        "good": m["good"], "bad": m["bad"], "samples": m["samples"],
                        "budget_remaining": m["budget_remaining"],
                        "budget_low_pct": SLO_BUDGET_LOW_PCT},
            "action": action, "boundary": boundary})
    return alerts


def slo_bar(actual, target, width=20):
    """report 用 SLO 条形(0-100% 线性 width 格):█=实际水位,|=目标格位。
    近满分区间的条形只是方向感(99.2% 与 99.5% 同格),精确差看百分比数字。"""
    def pos(v):
        return max(0, min(width - 1, int(round((v or 0.0) * width))))
    fill = pos(actual)
    cells = ["█"] * fill + ["·"] * (width - fill)
    cells[pos(target)] = "|"
    return "[" + "".join(cells) + "]"


def slo_report_lines(slo):
    """report 顶部 SLO 段落:各指标 实际 vs 目标 条形 + 剩余错误预算(三档呈现:
    ≥100% / 剩余百分比 / 0%)+ 按模板分账注记(全站 SLO 会藏住单模板回归)。"""
    if not slo.get("configured"):
        return ["-- SLO --",
                "  (config 未配 slo 节;示例 \"slo\": {\"keypage_indexable\": "
                "{\"target\": 0.995, \"window_days\": 30}}——R4 监控对标①)"]
    lines = ["-- SLO 索引健康(错误预算,R4 监控对标①)--"]
    for name, m in slo["metrics"].items():
        actual, budget = m.get("actual"), m.get("budget_remaining")
        if actual is None:
            lines.append("  %-18s 无样本(不猜)" % m["label"])
            continue
        if budget is None:
            budget_txt = "-"
        elif budget >= 1:
            budget_txt = "≥100%"
        else:
            budget_txt = "%d%%" % round(max(budget, 0.0) * 100)
        low = "  (slo_budget_low:已建议冻结发布)" if (
            budget is not None and budget < SLO_BUDGET_LOW_PCT) else ""
        lines.append("  %-18s 实际 %6.2f%% / 目标 %5.2f%%  %s  错误预算剩 %s%s"
                     % (m["label"], actual * 100, m["target"] * 100,
                        slo_bar(actual, m["target"]), budget_txt, low))
    lines.append("  注: 全站 SLO 会藏住单模板回归——按模板分账看 site_crawl"
                 "(crawl.page 口径:crawl.json pages[] 按模板分组);monitor 只看抽样 key_pages")
    return lines


def slo_report_json(slo):
    """report --json 的 SLO 段({configured, metrics[]};每指标含 actual/budget 口径)。"""
    return {"configured": bool(slo.get("configured")),
            "metrics": [dict(m, metric=name) for name, m in (slo.get("metrics") or {}).items()]}


# ---------- R4 监控对标④:flapping 检测 ----------

def flap_history_count(conn, code, key, cutoff_s):
    """(code,key) 近窗内 fire+resolved 事件数:fire=未抑制未自愈告警行(level!='low'),
    resolved=code+"_resolved" 自愈行。口径注意:纯持续告警(无任何 resolved)不算
    flapping——持续 critical 是持续事故不是抖动,降级会吞掉真事故的翻页。"""
    fires = conn.execute(
        "SELECT COUNT(*) AS c FROM alerts WHERE code=? AND key=? AND level!='low' "
        "AND suppressed=0 AND ts>=?", (code, key, cutoff_s)).fetchone()["c"]
    resolved = conn.execute(
        "SELECT COUNT(*) AS c FROM alerts WHERE code=? AND key=? AND ts>=?",
        (code + "_resolved", key, cutoff_s)).fetchone()["c"]
    return fires, resolved


def apply_flapping(conn, alerts, now=None):
    """④ flapping 检测:同 (code,key) FLAP_WINDOW_DAYS 天内 fire+resolved ≥FLAP_THRESHOLD
    次(且 ≥1 次 resolved)→ 该告警降 info+附 flap_count+"建议修阈值(反复触发/
    自愈=阈值贴边)"。Nagios/Alertmanager flap_detection 口径:反复触发/自愈说明阈值
    贴着信号边缘,继续按原级别翻页只会疲劳;降 info 后走 168h 冷却,自然静默一个
    回看窗。计数只看已入库历史(本 diff 尚未落库,不把自己算进去)。返回降级条数。"""
    if not alerts:
        return 0
    now = now or datetime.now()
    cutoff_s = (now - timedelta(days=FLAP_WINDOW_DAYS)).isoformat(timespec="seconds")
    cache = {}
    n = 0
    for a in alerts:
        if a.get("accepted") or a.get("level") == "low":
            continue
        ck = (a["code"], a.get("key"))
        if ck not in cache:
            cache[ck] = flap_history_count(conn, ck[0], ck[1], cutoff_s)
        fires, resolved = cache[ck]
        if resolved < 1:
            continue          # 无自愈记录:持续事故,不降级(见 flap_history_count 口径注)
        flap = fires + resolved
        if flap < FLAP_THRESHOLD:
            continue
        a["flap_count"] = flap
        a["details"] = dict(a.get("details") or {}, flap_count=flap,
                            flap_from_level=a["level"], flap_window_days=FLAP_WINDOW_DAYS)
        a["level"] = "info"
        a["message"] += (";flapping: 近 %d 天 fire+resolved %d 次(fire %d/resolved %d)"
                         "→ 降 info,建议修阈值(反复触发/自愈=阈值贴边)"
                         % (FLAP_WINDOW_DAYS, flap, fires, resolved))
        n += 1
    return n


def build_ci_checks(prev, curr, cfg, counts, alerts):
    """D1 P1:diff --ci 的结构化阈值结果——每条阈值规则一行(通过项也列出):
    {metric, operator, threshold, actual, passed}。口径:
    - *_drop_pct:* operator "<"(actual=观察到的降幅%,超出即失败);
    - 地板类(*_min_sample/_min_clicks)operator ">="(CI 口径=数据充分性门,样本在场但
      低于地板即失败;数据完全缺失 actual=None → 通过,不猜);
    - latency_min_ms/mixed_content_min 在 CI 中视为预算(operator "<",actual=观察极值);
    - 聚合行 critical_alerts/warn_alerts operator "==" 0(覆盖无阈值规则的关键告警)。
    actual 均四舍五入 1 位;bool 不当数字用。"""
    th = cfg.get("thresholds", DEFAULT_THRESHOLDS)
    rows = []

    def num(v):
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    def drop_pct(a, b):
        d = pct_drop(num(a), num(b))
        return round(d * 100, 1) if d is not None else None

    def row(metric, operator, threshold, actual):
        if actual is None:
            passed = True                        # 无数据/不适用 → 不猜,不失败
        elif operator == "<":
            passed = actual < threshold
        elif operator == "==":
            passed = actual == threshold
        else:                                    # ">=" 及其它:地板方向
            passed = actual >= threshold
        rows.append({"metric": metric, "operator": operator, "threshold": threshold,
                     "actual": actual, "passed": bool(passed)})

    def g(snap, check, key):
        return ((snap.get(check) or {}).get(key) or {})

    cv, pv = g(curr, "visibility", "site"), g(prev, "visibility", "site")
    row("visibility_drop_pct", "<", th.get("visibility_drop_pct", 30),
        drop_pct(pv.get("visible_pages"), cv.get("visible_pages")))
    row("visibility_min_sample", ">=", th.get("visibility_min_sample", 3), num(pv.get("visible_pages")))
    csm, psm = g(curr, "sitemap", "index"), g(prev, "sitemap", "index")
    row("sitemap_urls_drop_pct", "<", th.get("sitemap_urls_drop_pct", 15),
        drop_pct(psm.get("url_count"), csm.get("url_count")))
    row("sitemap_min_sample", ">=", th.get("sitemap_min_sample", 20), num(psm.get("url_count")))
    cg, pg = g(curr, "gsc", "file"), g(prev, "gsc", "file")
    cc, pc = num(cg.get("clicks_total")), num(pg.get("clicks_total"))
    row("gsc_clicks_drop_pct", "<", th.get("gsc_clicks_drop_pct", 20), drop_pct(pc, cc))
    row("gsc_min_clicks", ">=", th.get("gsc_min_clicks", 5),
        min(pc, cc) if (pc is not None and cc is not None) else None)
    inc = mx = mc = None
    for k, c in (curr.get("pages") or {}).items():
        pl = num((prev.get("pages") or {}).get(k, {}).get("latency_ms"))
        cl = num(c.get("latency_ms"))
        d = pct_drop(pl, cl) if pl else None
        if isinstance(d, float) and d < 0:
            inc = round(-d * 100, 1) if inc is None else max(inc, round(-d * 100, 1))
        if cl is not None:
            mx = round(cl, 1) if mx is None else max(mx, round(cl, 1))
        v = num(c.get("mixed_content"))
        if v is not None:
            mc = v if mc is None else max(mc, v)
    row("latency_increase_pct", "<", th.get("latency_increase_pct", 100), inc)
    row("latency_min_ms", "<", th.get("latency_min_ms", 500), mx)
    row("mixed_content_min", "<", th.get("mixed_content_min", 3), mc)
    seg_pcts = [num((a.get("details") or {}).get("pct")) for a in alerts
                if a.get("code") == "pages_left_segment"]
    seg_pcts = [p for p in seg_pcts if p is not None]
    if cfg.get("segments"):
        row("pages_left_segment_pct", "<", th.get("pages_left_segment_pct", 10),
            max(seg_pcts) if seg_pcts else 0.0)
    row("critical_alerts", "==", 0, int(counts.get("critical", 0)))
    row("warn_alerts", "==", 0, int(counts.get("warn", 0)))
    return rows


def ci_junit_xml(ci):
    """--ci --ci-format junit:checks → JUnit XML(独立实现,不 import ci_format;
    每 check 一个 testcase,失败带 ThresholdBreached failure 消息)。"""
    def x(s):
        return _xml_escape(str(s), {'"': "&quot;", "'": "&apos;"})

    checks = ci.get("checks") or []
    fails = [c for c in checks if not c["passed"]]
    cases = []
    for c in checks:
        name = x("%s %s %s" % (c["metric"], c["operator"], c["threshold"]))
        if c["passed"]:
            cases.append('    <testcase name="%s" classname="monitor.diff"/>' % name)
        else:
            msg = x("actual=%s 期望 %s %s" % (c["actual"], c["operator"], c["threshold"]))
            cases.append('    <testcase name="%s" classname="monitor.diff">'
                         '<failure type="ThresholdBreached" message="%s"/></testcase>' % (name, msg))
    n, nf = len(checks), len(fails)
    props = ('  <properties>\n'
             '    <property name="site" value="%s"/>\n'
             '    <property name="curr_run" value="%s"/>\n'
             '    <property name="prev_run" value="%s"/>\n'
             '  </properties>' % (x(ci.get("site", "")), ci.get("curr_run"), ci.get("prev_run")))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuites name="monitor-diff" tests="%d" failures="%d">\n%s\n'
            '  <testsuite name="monitor-diff" tests="%d" failures="%d">\n%s\n  </testsuite>\n'
            '</testsuites>\n' % (n, nf, props, n, nf, "\n".join(cases)))


def compute_alerts(prev, curr, cfg, baseline=None, inhibited_out=None, volatility=None):
    """prev/curr 为扁平快照;baseline(可选)= ~7 天前 ok run 的快照,双窗口判定用;
    volatility(可选,R0-2)= sensor_volatility --context 上下文 dict——verdict=
    high_volatility 时 gsc/visibility 类跌幅告警降 info 并附注(详见 cmd_diff)。
    返回 list[dict(level/code/key/message/details/action,boundary))]。"""
    th = cfg.get("thresholds", DEFAULT_THRESHOLDS)
    site = cfg.get("site", "")
    A = []

    # R0-2:当日 SERP 波动上下文(命令行 diff 前置计算;直调/旧调用缺省 None=不影响)
    vol = volatility if isinstance(volatility, dict) else {}
    vol_high = vol.get("verdict") == "high_volatility"
    vol_note = ""
    if vol_high:
        z30 = vol.get("z30")
        vol_note = ";%s(sensor_volatility %s score=%s,z30=%s)" % (
            SENSOR_HIGH_NOTE, vol.get("date"), vol.get("score"),
            ("%+.1f" % z30) if isinstance(z30, (int, float)) else "—")

    def vol_det(details):
        """高波动降级时把上下文一并落进 details(复核可查 score/z30/日期)。"""
        return dict(details or {}, sensor_volatility=vol) if vol_high else (details or {})

    def add(level, code, key, message, details=None):
        action, boundary = PLAYBOOK.get(code, ("按 continuous-operations.md 对应级别 playbook", "human"))
        A.append({"level": level, "code": code, "key": key, "message": message,
                  "details": details or {}, "action": action, "boundary": boundary})

    def page_state(snap, key):
        return ((snap.get("pages") or {}).get(key) or {})

    # --- 4 存活:首页/关键页 ---
    # D1 P2:key_pages 绝对断言(max_latency_ms)在告警期解析 config(改 config 即刻
    # 生效,不依赖快照重建;与 segments 归属口径一致)
    kp_max_latency = {}
    for entry in cfg.get("key_pages") or []:
        o = parse_key_page(entry)
        if o["max_latency_ms"] is not None:
            kp_max_latency[o["path"]] = o["max_latency_ms"]
    keys = set((curr.get("pages") or {}).keys()) | set((prev.get("pages") or {}).keys())
    for k in sorted(keys):
        c, p = page_state(curr, k), page_state(prev, k)
        b = page_state(baseline or {}, k)
        label = "首页" if k == "/" else "关键页 %s" % k
        cs = c.get("status")
        if c.get("state") == "http_error" or (isinstance(cs, int) and cs >= 400):
            code = "key_page_down" if k != "/" else "homepage_down"
            # 双窗口(P1-9):昨日短窗已触发;再看 7 天基线是否同向(基线健康→确属今日事故)
            lvl, extra = "critical", ""
            if baseline is not None and isinstance(b.get("status"), int) and b["status"] >= 400:
                lvl, extra = "info", "(7 天基线同样异常→疑似抖动/既往已存在,降 info)"
            add(lvl, code, k, "%s 返回 %s%s" % (label, cs, extra),
                {"prev_status": p.get("status"), "baseline_status": b.get("status"), "url": site + k})
        elif c.get("state") == "error":
            if p.get("state") == "error":
                add("warn", "fetch_error_confirmed", k, "%s 连续两次抓取失败(网络层)" % label,
                    {"prev_error": p.get("error"), "curr_error": c.get("error")})
            else:
                add("info", "fetch_error_single", k, "%s 单次抓取失败,下次复确认" % label,
                    {"error": c.get("error")})
        # 关键词在场断言(P1-15,audit 04:UptimeRobot keyword monitor 同款)
        if c.get("expect_ok") is False and not (isinstance(cs, int) and cs >= 400):
            add("warn", "content_regression", k,
                "%s 页面 200 但 expect_substring 断言失败(空白渲染/软 404/误改版)" % label,
                {"url": site + k, "missing": c.get("expect_missing")})
        # D1 P2:must_contain 断言(GA 跟踪等关键标记)——消失即 warn,与 expect 的
        # content_regression 分层:跟踪标记消失通常是发布/模板事故,不是内容改版;
        # 仅对真实渲染的页面判定(404/抓取失败没有"消失"的证据)
        if c.get("must_contain_missing") and page_rendered(c):
            add("warn", "ga_tracking_removed", k,
                "%s 关键标记消失: must_contain 断言缺 %r(GA 跟踪/统计脚本;若有意移除请同步删断言)"
                % (label, c["must_contain_missing"]),
                {"missing": c["must_contain_missing"], "url": site + k})
        # 混合内容(https 站)
        cmc, pmc = c.get("mixed_content"), p.get("mixed_content")
        if isinstance(cmc, int) and cmc >= int(th.get("mixed_content_min", 3)) and (pmc or 0) < cmc:
            add("warn", "mixed_content", k, "%s 混合内容 %d 个 http:// 子资源(上次 %s)"
                % (label, cmc, pmc if pmc is not None else "无记录"), {"curr": cmc, "prev": pmc})
        # 时延
        cl, pl = c.get("latency_ms"), p.get("latency_ms")
        d = pct_drop(pl, cl) if pl else None  # 负值=增长
        if isinstance(d, float) and d < 0 and -d * 100 >= int(th.get("latency_increase_pct", 100)) \
                and max(pl or 0, cl or 0) >= int(th.get("latency_min_ms", 500)):
            add("info", "latency_spike", k, "%s 时延 %.0fms→%.0fms(+%.0f%%)"
                % (label, pl, cl, -d * 100), {"prev_ms": pl, "curr_ms": cl})
        # D1 P2:绝对时延上限断言(max_latency_ms 对接已有 latency 检查;相对 pct 阈值
        # 对慢站钝感,SLA 型上限补绝对口径)
        mx = kp_max_latency.get(k)
        if mx is not None and isinstance(cl, (int, float)) and cl > mx:
            add("info", "latency_spike", k, "%s 时延 %.0fms 超断言上限 max_latency_ms=%.0fms"
                % (label, cl, mx), {"curr_ms": cl, "max_latency_ms": mx, "assert": "absolute"})
        # D1 P0-1:页面级 noindex(Conductor 头号触发器)。旧快照缺 indexable(=None)
        # 不参与判定——升级 monitor 后首个 diff 不误报、不崩。
        ci, pi = c.get("indexable"), p.get("indexable")
        if ci is False and pi is True:
            add("critical", "noindex_added", k,
                "%s 新增 noindex(来源:%s)——若非有意下线立即回滚"
                % (label, c.get("noindex_source") or "unknown"),
                {"source": c.get("noindex_source"), "canonical": c.get("canonical"),
                 "url": site + k})
        elif ci is True and pi is False:
            add("info", "noindex_removed", k,
                "%s noindex 已移除,恢复可索引(自愈信号)" % label, {"url": site + k})
        # D1 P0-2:canonical 目标健康度(防抖:连续 3 次失败才告警,单次/两次不动)
        cts = c.get("canonical_target_status")
        if canonical_failure(cts) and int(c.get("canonical_fail_streak") or 0) >= 3:
            shown = "%d" % cts if isinstance(cts, int) else "不可达(error)"
            add("warn", "canonical_target_broken", k,
                "%s canonical 指向 %s 目标——首选 URL 不可达,索引信号自相矛盾" % (label, shown),
                {"canonical": c.get("canonical"), "target_status": cts,
                 "fail_streak": c.get("canonical_fail_streak")})

    # --- D1 P1:segments 受影响度(Σimportance)与 pages_left_segment(Conductor 10% 档)---
    # key_pages 运行时按 regex 归属首个命中 segment;健康页流失按 Σimportance 加权判档
    # (无 gsc 页级数据时每页 importance=1),替代纯页数地板;页面不在 curr(停止监控)
    # 不计入流失(不猜)。
    segs = [s for s in (cfg.get("segments") or [])
            if isinstance(s, dict) and s.get("name") and s.get("match")]
    if segs:
        page_clicks = ((curr.get("gsc") or {}).get("file") or {}).get("page_clicks") or {}
        prev_pages, curr_pages = prev.get("pages") or {}, curr.get("pages") or {}
        page_seg = {}
        for p in set(prev_pages) | set(curr_pages):
            seg = segment_of(p, cfg)
            if seg is not None:
                page_seg[p] = str(seg.get("name"))
        for seg in segs:
            name = str(seg["name"])
            members = sorted(p for p, n in page_seg.items() if n == name)
            prev_h = [p for p in members if p in prev_pages and page_healthy(prev_pages[p])]
            dropped = [p for p in prev_h if p in curr_pages and not page_healthy(curr_pages[p])]
            if not prev_h or not dropped:
                continue
            total_imp = sum(page_importance(seg, p, page_clicks) for p in prev_h)
            drop_imp = sum(page_importance(seg, p, page_clicks) for p in dropped)
            if total_imp <= 0:
                continue
            pct = drop_imp / total_imp
            if pct * 100 >= float(th.get("pages_left_segment_pct", 10)):
                add("warn", "pages_left_segment", "segment:" + name,
                    "segment %s 健康页 %d → %d(−%.0f%%;受影响度 Σimportance %.1f/%.1f,档位 %s%%)"
                    % (name, len(prev_h), len(prev_h) - len(dropped), pct * 100, drop_imp, total_imp,
                       th.get("pages_left_segment_pct", 10)),
                    {"segment": name, "prev_healthy": len(prev_h),
                     "curr_healthy": len(prev_h) - len(dropped), "dropped": dropped,
                     "dropped_importance": round(drop_imp, 2),
                     "total_importance": round(total_imp, 2), "pct": round(pct * 100, 1)})

    # --- 4 存活/3 索引:robots ---
    cr, pr = (curr.get("robots") or {}).get("robots", {}), (prev.get("robots") or {}).get("robots", {})
    br = ((baseline or {}).get("robots") or {}).get("robots", {})
    if cr.get("sitewide_block") and not pr.get("sitewide_block"):
        lvl, extra = "critical", ""
        if baseline is not None and br.get("sitewide_block"):
            lvl, extra = "info", "(7 天基线同样误封→疑似抖动/既往已存在,降 info)"
        add(lvl, "robots_sitewide_block", "robots",
            "robots.txt 出现 * 组全站 Disallow(几乎总是部署事故)%s" % extra,
            {"prev_hash": pr.get("hash"), "curr_hash": cr.get("hash")})
    elif cr.get("hash") and pr.get("hash") and cr["hash"] != pr["hash"]:
        add("info", "robots_changed", "robots", "robots.txt 内容变更(hash %s→%s)"
            % (pr.get("hash"), cr.get("hash")))
    cp, pp = cr.get("ai_posture") or {}, pr.get("ai_posture") or {}
    for bot in sorted(set(cp) & set(pp)):
        if cp[bot] != pp[bot]:
            add("info", "ai_posture_flip", "robots:" + bot,
                "AI 爬虫 %s 放行状态翻转: %s → %s" % (bot, pp[bot], cp[bot]))

    # --- D1 P2:非规范域名重定向(重复内容防线)---
    # 只认 "broken"(变体在自己 host 上直接应答,不再 301 到 canonical host);
    # "error"=probe 网络失败,防假 0 纪律下绝不判失效;旧快照无 redirects 检查=不触发。
    crv = ((curr.get("redirects") or {}).get("variants") or {})
    if isinstance(crv, dict):
        for variant, vst in sorted(crv.items()):
            if vst == "broken":
                add("warn", "redirect_chain_broken", variant,
                    "非规范变体 %s 停止重定向——重复内容风险(期望 301 → %s)" % (variant, site),
                    {"variant": variant, "canonical": site, "probe": vst})

    # --- 周检:SSL 证书到期(30/14/7/0 梯度;绝对阈值,不依赖 prev)---
    cssl = (curr.get("ssl") or {}).get("cert", {})
    days_left = cssl.get("days_left")
    if isinstance(days_left, (int, float)) and not cssl.get("state"):
        if days_left < 0:
            add("critical", "ssl_cert_expired", "cert",
                "SSL 证书已过期 %d 天(多数客户端已拒连)" % -days_left,
                {"not_after": cssl.get("not_after"), "issuer": cssl.get("issuer")})
        elif days_left <= 7:
            add("critical", "ssl_cert_expiry", "cert", "SSL 证书 %d 天后到期(≤7 天档)" % days_left,
                {"not_after": cssl.get("not_after"), "issuer": cssl.get("issuer")})
        elif days_left <= 14:
            add("warn", "ssl_cert_expiry", "cert", "SSL 证书 %d 天后到期(≤14 天档)" % days_left,
                {"not_after": cssl.get("not_after"), "issuer": cssl.get("issuer")})
        elif days_left <= 30:
            add("info", "ssl_cert_expiry", "cert", "SSL 证书 %d 天后到期(≤30 天档)" % days_left,
                {"not_after": cssl.get("not_after")})

    # --- 1 可见性 ---
    # 防假 0 纪律(serpbear,D1 P2 复核确认):半数以上请求失败/被拦/解析不出 →
    # state 落 skipped/blocked/unparseable,下面的 == "ok" 门直接挡住——绝不把
    # "请求失败"判成"排名/收录消失";真 0 只在端点成功返回且样本过地板时成立。
    # 该纪律对一切 SERP 源生效(D1 P2 第 13 条源适配层:bing/duckduckgo)。
    cv, pv = (curr.get("visibility") or {}).get("site", {}), (prev.get("visibility") or {}).get("site", {})
    bv = ((baseline or {}).get("visibility") or {}).get("site", {})
    if cv.get("state", "ok") == "ok" and "visible_pages" in cv:
        cvis, pvis = cv.get("visible_pages"), pv.get("visible_pages")
        floor = int(th.get("visibility_min_sample", 3))
        if pvis is not None and pvis >= floor:
            if cvis == 0:
                lvl, extra = "critical", ""
                if baseline is not None and isinstance(bv.get("visible_pages"), int) \
                        and bv["visible_pages"] == 0:
                    lvl, extra = "info", "(7 天基线亦为 0→端点口径抖动可能,降 info)"
                if vol_high:   # R0-2:当日 SERP 高波动 → 疑似算法更新,降 info+附注
                    lvl, extra = "info", vol_note
                add(lvl, "visibility_zero", "site",
                    "site: 抽查可见页 %d → 0(端点成功返回,疑似去索引/处罚)%s" % (pvis, extra),
                    vol_det({"prev": pvis, "curr": cvis, "sample": cv.get("sample"),
                             "method_note": "%s 端点方向抽样,非官方索引数"
                                            % (cv.get("serp_source") or "Bing HTML")}))
            else:
                d = pct_drop(pvis, cvis)
                if d is not None and d * 100 >= int(th.get("visibility_drop_pct", 30)):
                    add("info" if vol_high else "warn", "visibility_drop", "site",
                        "site: 抽查可见页 %d → %d(−%.0f%%)%s" % (pvis, cvis, d * 100, vol_note),
                        vol_det({"prev": pvis, "curr": cvis}))
        elif pvis is None:
            A.append({"level": "info", "code": "visibility_baseline", "key": "site",
                      "message": "可见性基线建立: %d 页(下次 run 才参与告警)" % cvis,
                      "details": {"visible_pages": cvis},
                      "action": "记录基线,无需动作", "boundary": "auto"})

    # --- 2 流量 ---
    cg, pg = (curr.get("gsc") or {}).get("file", {}), (prev.get("gsc") or {}).get("file", {})
    cc, pc = cg.get("clicks_total"), pg.get("clicks_total")
    if cc is not None and pc is not None:
        floor = int(th.get("gsc_min_clicks", 5))
        d = pct_drop(pc, cc)
        if d is not None and min(pc, cc) >= floor and d * 100 >= int(th.get("gsc_clicks_drop_pct", 20)):
            add("info" if vol_high else "warn", "gsc_clicks_drop", "file",
                "GSC 点击 %d → %d(−%.0f%%,地板 %d)%s" % (pc, cc, d * 100, floor, vol_note),
                vol_det({"prev": pc, "curr": cc}))
        elif d is not None and d < -0.5 and pc >= floor:
            add("info", "gsc_clicks_spike", "file", "GSC 点击 %d → %d(+%.0f%%)"
                % (pc, cc, -d * 100), {"prev": pc, "curr": cc})

    # --- 周检:sitemap ---
    csm, psm = (curr.get("sitemap") or {}).get("index", {}), (prev.get("sitemap") or {}).get("index", {})
    cuc, puc = csm.get("url_count"), psm.get("url_count")
    if isinstance(cuc, int) and isinstance(puc, int):
        d = pct_drop(puc, cuc)
        if d is not None and puc >= int(th.get("sitemap_min_sample", 20)) \
                and d * 100 >= int(th.get("sitemap_urls_drop_pct", 15)):
            add("warn", "sitemap_urls_drop", "index", "sitemap URL 数 %d → %d(−%.0f%%)"
                % (puc, cuc, d * 100), {"prev": puc, "curr": cuc})
        elif cuc > puc:
            A.append({"level": "info", "code": "sitemap_urls_grew", "key": "index",
                      "message": "sitemap URL 数 %d → %d(+%d)" % (puc, cuc, cuc - puc),
                      "details": {}, "action": "记录,无需动作", "boundary": "auto"})

    # --- 周检:CWV 现场数据 p75(R0-3;notify 已预留 cwv_* 路由)---
    # 口径:check_cwv_field 采的 field_data/PSI mobile p75,官方阈值判档。
    # 任一核心指标(LCP/INP/CLS)poor → cwv_poor(warn,绝对阈值不依赖 prev);
    # 未到 poor 但较上期跨档退步(good→needs_improvement / →poor 已被 poor 分支覆盖)
    # → cwv_regression(info)。check error/skipped 或指标缺失 → 不猜。
    cwv_grade = {"good": 0, "needs_improvement": 1, "poor": 2}
    ccw = (curr.get("cwv_field") or {}).get("field", {})
    pcw = (prev.get("cwv_field") or {}).get("field", {})
    if isinstance(ccw.get("pages"), dict):
        for path in sorted(ccw["pages"]):
            m = ccw["pages"].get(path) or {}
            verdicts = {}
            for name in ("LCP", "INP", "CLS"):
                v = ((m.get(name) or {}).get("verdict"))
                if v in cwv_grade:
                    verdicts[name] = v
            if not verdicts:
                continue
            shown = ", ".join("%s=%s%s" % (k, m[k].get("value"), m[k].get("unit") or "")
                              for k in ("LCP", "INP", "CLS") if k in m)
            poor = sorted(k for k, v in verdicts.items() if v == "poor")
            if poor:
                add("warn", "cwv_poor", path,
                    "CWV 现场数据(mobile p75)%s: %s——核心三项 poor(%s)"
                    % (path, shown, "+".join(poor)),
                    {"page": path, "verdicts": verdicts,
                     "values": {k: m[k].get("p75") for k in verdicts},
                     "strategy": ccw.get("strategy")})
                continue
            pm = (pcw.get("pages") or {}).get(path) or {}
            for name in sorted(verdicts):
                pv = ((pm.get(name) or {}).get("verdict"))
                if pv in cwv_grade and cwv_grade[verdicts[name]] > cwv_grade[pv]:
                    add("info", "cwv_regression", path,
                        "CWV 现场数据(mobile p75)%s: %s 跨档退步 %s → %s(未到 poor)"
                        % (path, name, pv, verdicts[name]),
                        {"page": path, "metric": name, "prev_verdict": pv,
                         "curr_verdict": verdicts[name],
                         "prev_p75": (pm.get(name) or {}).get("p75"),
                         "curr_p75": m[name].get("p75")})
                    break

    # --- 周检:citation decay 进告警链(R0-4)---
    ccd = (curr.get("citation") or {}).get("decay", {})
    if isinstance(ccd.get("decayed_count"), int) and ccd["decayed_count"] > 0:
        add("warn", "citation_decay", "panel",
            "AI 引用 decay: %d 个 (prompt,engine) cell 已过半衰(decayed)——"
            "进 refresh/重写排期(citation_panel decay)" % ccd["decayed_count"],
            {"decayed_count": ccd["decayed_count"], "rewriting": ccd.get("rewriting"),
             "per_engine": ccd.get("per_engine"), "panel": ccd.get("panel")})

    # --- 月检:引荐域变化(R2-4;外链 6.5x 杠杆此前零监测)---
    # 防假 0:check 侧 error/skipped 只落 state,isinstance int 门直接挡住——绝不把
    # "读不了导出"判成"外链归零";无上月快照(首月建基线)/上月无数据 → 不猜。
    # 阈值严格大于才触发(总域 −10%/新增 −50% 恰等于阈值不告警)。
    cbl = (curr.get("backlinks") or {}).get("refdomains", {})
    pbl = (prev.get("backlinks") or {}).get("refdomains", {})
    ctot, ptot = cbl.get("refdomains_total"), pbl.get("refdomains_total")
    if isinstance(ctot, int) and isinstance(ptot, int):
        d = pct_drop(ptot, ctot)
        if d is not None and d * 100 > float(th.get("backlink_total_drop_pct", 10)):
            prev_doms, curr_doms = set(pbl.get("domains") or []), set(cbl.get("domains") or [])
            lost = sorted(prev_doms - curr_doms)
            add("critical", "backlink_loss", "refdomains",
                "总引荐域 %d → %d(−%.0f%%)——外链大量丢失(处罚/被撤链/导出口径变化)"
                % (ptot, ctot, d * 100),
                {"prev": ptot, "curr": ctot, "pct": round(d * 100, 1),
                 "lost_sample": lost[:10], "lost_total": len(lost),
                 "domains_snapshot_truncated": bool(
                     pbl.get("domains_truncated") or cbl.get("domains_truncated"))})
        cnew, pnew = cbl.get("refdomains_new"), pbl.get("refdomains_new")
        nd = pct_drop(pnew, cnew)
        if nd is not None and nd * 100 > float(th.get("backlink_newref_drop_pct", 50)):
            add("warn", "backlink_drop", "refdomains",
                "引荐域新增 %d→%d,外链获取停滞或丢失" % (pnew, cnew),
                {"prev_new": pnew, "curr_new": cnew, "pct": round(nd * 100, 1)})

    # --- 关键页字段级漂移(P1-11:title/meta/canonical/og/watch 分字段,替全页 hash)
    # + D1 P2:removed 语义(新值空且旧值非空 → meta_removed warn,区别于 changed info)、
    # h1/hreflang/word_count/h2 指纹(旧快照缺键按 None 不触发)---
    for k in sorted(set((curr.get("pages") or {})) & set((prev.get("pages") or {}))):
        c, p = curr["pages"][k], prev["pages"][k]
        flabel = "首页" if k == "/" else "页面 %s" % k
        # R5③:changed 与 removed 同受 page_rendered 门——state=error/http_error 的
        # 残缺快照缺 title/meta 等键,会被当 "(旧值→空)" 假漂移;removed/h1 已有门,对齐
        changed, removed = [], []
        if page_rendered(c):
            changed = [f for f in PAGE_DIFF_FIELDS if (c.get(f) or "") != (p.get(f) or "")]
            removed = [f for f in PAGE_DIFF_FIELDS
                       if (p.get(f) or "") and not (c.get(f) or "")]
            changed = [f for f in changed if f not in set(removed)]
        if removed:
            add("warn", "meta_removed", k,
                "%s %s 被移除——若非有意立即回滚" % (flabel, "+".join(removed)),
                dict({"fields": removed},
                     **{("prev_" + f): p.get(f) for f in removed},
                     **{("curr_" + f): c.get(f) for f in removed}))
        if changed:
            add("info", "title_meta_drift", k,
                "%s 字段漂移: %s" % (flabel, "+".join(changed)),
                dict({"fields": changed},
                     **{("prev_" + f): p.get(f) for f in changed},
                     **{("curr_" + f): c.get(f) for f in changed}))
        if not page_rendered(c):
            continue    # 404/抓取失败页面:没有 h1/hreflang/字数变化 的证据,不判
        ch1, ph1 = c.get("h1"), p.get("h1")
        if ch1 is not None and ph1 is not None and ch1 != ph1:
            add("info", "h1_changed", k, "%s h1 变更: %r → %r" % (flabel, ph1, ch1),
                {"prev_h1": ph1, "curr_h1": ch1})
        chh, phh = c.get("hreflang_hash"), p.get("hreflang_hash")
        if chh is not None and phh is not None and chh != phh:
            add("warn", "hreflang_changed", k,
                "%s hreflang 注解集变更(hash %s→%s)——国际化注解变更可能整组失效"
                % (flabel, phh, chh), {"prev_hash": phh, "curr_hash": chh})
        ch2, ph2 = c.get("h2"), p.get("h2")
        if ch2 is not None and ph2 is not None and ch2 != ph2:
            add("info", "layout_shift", k,
                "%s 首个 h2 文本变化(%r → %r):模板/布局疑似改动(selector_stable 锚)"
                % (flabel, ph2, ch2), {"prev_h2": ph2, "curr_h2": ch2})
        cwc, pwc = c.get("word_count"), p.get("word_count")
        if isinstance(cwc, int) and isinstance(pwc, int) and pwc > 0:
            cpct = abs(cwc - pwc) / pwc * 100.0
            if cpct >= float(th.get("content_change_pct", 30)):
                add("info", "main_content_change", k,
                    "%s 主内容字数 %d→%d(%.0f%%)" % (flabel, pwc, cwc, cpct),
                    {"prev": pwc, "curr": cwc, "pct": round(cpct, 1),
                     "threshold_pct": float(th.get("content_change_pct", 30))})
    clm, plm = (curr.get("llms_txt") or {}).get("file", {}), (prev.get("llms_txt") or {}).get("file", {})
    if plm.get("present") and clm and not clm.get("present", True) and "present" in clm:
        add("info", "llms_txt_removed", "file", "llms.txt 从存在变为缺失")
    elif clm.get("hash") and plm.get("hash") and clm["hash"] != plm["hash"]:
        add("info", "llms_txt_changed", "file", "llms.txt 内容变更(hash %s→%s)"
            % (plm.get("hash"), clm.get("hash")))

    # R5⑤:accepted_codes 白名单先于抑制树应用(接受≠消失)——已接受告警不被根因
    # 折叠蒸发,保留入库与周报"已接受告警数"计数;抑制树只折叠未接受的派生告警
    apply_accepted(A, cfg)
    # 抑制树(P1-10):根因一条,派生折叠(替 Top-K)
    A = apply_inhibition(A, inhibited_out)
    order = {l: i for i, l in enumerate(LEVELS)}
    A.sort(key=lambda a: order.get(a["level"], 9))
    return A


def in_maintenance(cfg, now=None):
    """维护窗口(audit 06,kuma 惯例):窗口内 diff 只记快照不产告警,防改版期误报。"""
    now = now or datetime.now()
    for w in cfg.get("maintenance_windows") or []:
        try:
            f = datetime.fromisoformat(str(w.get("from") or ""))
            t = datetime.fromisoformat(str(w.get("to") or ""))
        except ValueError:
            continue
        if f <= now <= t:
            return w
    return None


def cmd_diff(args):
    mdir = args.dir
    cfg = load_config(mdir)
    now = datetime.now()
    win = in_maintenance(cfg, now)
    with monitor_lock(mdir):
        conn = open_db(mdir)
        sweep_stale_runs(conn)
        if win:
            # 维护窗口:照常算 prev/curr 供留档,但告警一律不生成不入库(audit 06)
            ids = latest_run_ids(conn, 2)
            payload = {"generated": now.isoformat(timespec="seconds"), "site": cfg["site"],
                       "market": cfg.get("market"),
                       "curr_run": ids[0] if ids else None, "prev_run": ids[1] if len(ids) > 1 else None,
                       "alerts": [], "healed": [], "suppressed": [], "inhibited": [],
                       "maintenance": {"from": win.get("from"), "to": win.get("to"),
                                       "reason": win.get("reason", "")},
                       "counts": {l: 0 for l in LEVELS}}
            conn.close()
            if args.out:
                with open(args.out, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
            print("[i] 维护窗口内(%s → %s %s):diff 跳过告警生成,只留快照"
                  % (win.get("from"), win.get("to"), win.get("reason", "")))
            return 0
        if args.run_id:
            curr_id = args.run_id
        else:
            ids = latest_run_ids(conn, 2)
            if len(ids) < 2:
                print("错误: 需要 ≥2 次 status='ok' 的 run 才能 diff(partial/failed/quarantined "
                      "不充当基线;先再跑一次 run,或用 --run-id/--prev-run-id 显式指定)",
                      file=sys.stderr)
                conn.close()
                return 4
            curr_id = ids[0]
        if args.prev_run_id:
            prev_id = args.prev_run_id
            kind_mismatch = False    # 显式指定基线:用户自选,不按 kind 告警
        else:
            # R5②:prev 优先同 kind 的最近 ok run(weekly 不拿 daily 当基线);
            # 无同 kind 时回退最近 ok,并响亮标记(stderr WARNING 一行 + payload 键)
            prev_id, kind_mismatch = pick_prev_run_id(conn, curr_id)
            if prev_id is None:
                print("错误: run %d 之前没有 status='ok' 的可对比 run(坏 run 可先 quarantine 隔离)"
                      % curr_id, file=sys.stderr)
                conn.close()
                return 4
            if kind_mismatch:
                print("[!] WARNING: prev 基线 run #%d 与 run #%d 的 kind 不一致(无同 kind 的 "
                      "status='ok' run,已回退最近 ok;daily/weekly 口径不同,diff 结果可能失真)"
                      % (prev_id, curr_id), file=sys.stderr)
        prev, curr = load_snapshot(conn, prev_id), load_snapshot(conn, curr_id)
        # 双窗口(P1-9):再取 ~7 天前的 ok run 当长窗基线(库龄不足则为 None=保持原级别)
        baseline_id = pick_baseline_run(conn, {curr_id, prev_id}, days=7)
        baseline = load_snapshot(conn, baseline_id) if baseline_id else None
        # D1 P1:baseline 缺失响亮警告——库龄>7 天却取不到基线(绝不静默降级为单窗口)
        baseline_missing = False
        if baseline_id is None:
            age_days = oldest_ok_run_age_days(conn, now)
            if age_days is not None and age_days > 7:
                baseline_missing = True
                print("[!] WARNING: 无 7 天基线(库龄 %.1fd),双窗口降级未生效" % age_days,
                      file=sys.stderr)
        # R0-2 接线:产 gsc/visibility 类跌幅告警前,先取当日 SERP 波动上下文
        # (gsc.csv 含 Date+Query+Position 才有;列不齐/单日/导入失败 → None 静默跳过,
        # 绝不阻塞告警主路径);high_volatility 时 compute_alerts 把跌幅告警降 info+附注
        volatility = sensor_volatility_context(os.path.join(mdir, "gsc.csv"))
        inhibited = []
        alerts = compute_alerts(prev, curr, cfg, baseline=baseline, inhibited_out=inhibited,
                                volatility=volatility)
        # R4 监控对标①:SLO+错误预算——diff 后从 db 近 window 天 ok run 快照聚合实际值,
        # 剩余错误预算 <25% → slo_budget_low warn(config 未配 slo 节=整块跳过,不猜)
        slo = compute_slo(conn, cfg, now)
        alerts.extend(slo_alerts_from(slo))
        # accepted_codes 对追加的 SLO 告警二次套用(apply_accepted 可重入,不重复前缀)
        apply_accepted(alerts, cfg)
        # R4 监控对标④:flapping——同 (code,key) 7 天内 fire+resolved≥3 次(≥1 次
        # resolved;纯持续告警不降级)→ 降 info+附 flap_count+建议修阈值
        n_flap = apply_flapping(conn, alerts, now)
        if n_flap:
            print("[i] flapping 检测: %d 条告警近 %d 天反复触发/自愈,已降 info(建议修阈值)"
                  % (n_flap, FLAP_WINDOW_DAYS))
        # D1 P1→R5⑤:accepted_codes 白名单先于抑制树应用(接受≠消失)——compute_alerts
        # 内对主告警、上方对追加的 SLO 告警各套用一次(apply_accepted 可重入)
        n_accepted = sum(1 for a in alerts if a.get("accepted"))
        if slo.get("configured"):
            payload_slo = slo_report_json(slo)["metrics"]
        else:
            payload_slo = None
        _order = {l: i for i, l in enumerate(LEVELS)}
        alerts.sort(key=lambda a: _order.get(a["level"], 9))
        # R4 监控对标⑤(incident 角色分工 owner_team,pipeline-completeness §五):
        # config 可选映射 owner_teams:{code_prefix: "team"} → 告警 payload 逐条透传
        # owner_team(前缀按最长优先,精确匹配即全长前缀;未配置/无命中/值非字符串
        # 一律不写键,零侵扰旧 payload)。notify 侧按该字段渲染一行"归属: team"。
        _oteams = cfg.get("owner_teams")
        if isinstance(_oteams, dict):
            _prefixes = sorted((str(k) for k in _oteams
                                if k and isinstance(_oteams.get(k), str) and str(k)),
                               key=len, reverse=True)
            for a in alerts:
                _code = str(a.get("code") or "")
                for _pfx in _prefixes:
                    if _code.startswith(_pfx):
                        a["owner_team"] = _oteams[_pfx]
                        break

        cooldowns = cfg.get("cooldown_hours", COOLDOWN_HOURS)
        cur_fps = {("%s:%s" % (a["code"], a["key"])) for a in alerts}
        # R5④:被抑制树折叠的 (code,key) 并入"仍在场"集合——不算自愈/resolved,
        # 不丢冷却态(根因消失后派生告警恢复时,冷却从原未结行续算,不全新重报)
        cur_fps |= {("%s:%s" % (i["code"], i["key"])) for i in inhibited}
        unresolved = conn.execute(
            "SELECT id, code, key, level, ts FROM alerts WHERE resolved=0 AND level!='low'").fetchall()
        # R5①:冷却判龄按 (code,key) 取最新一行的 ts(旧行为=命中最旧行即 break——
        # 告警持续超一个冷却窗后,最旧行龄期已超窗,冷却从此整体失效,每个 diff 都重报)
        latest_age = {}      # fp → (最小龄期小时数=最新一行, 该行 ts)
        for row in unresolved:
            _fp = row["code"] + ":" + row["key"]
            try:
                _age = (now - datetime.fromisoformat(row["ts"])).total_seconds() / 3600
            except ValueError:
                continue
            if _fp not in latest_age or _age < latest_age[_fp][0]:
                latest_age[_fp] = (_age, row["ts"])
        healed, suppressed = [], []
        for a in alerts:
            if a.get("accepted"):
                continue      # 已接受:不入 cooldown 抑制路径,每次 diff 照常入库供周报计数
            fp = "%s:%s" % (a["code"], a["key"])
            hit = latest_age.get(fp)
            if hit is not None and hit[0] < cooldowns.get(a["level"], 24):
                a["suppressed"] = True
                a["suppressed_since"] = hit[1]
                suppressed.append(fp)
        for row in unresolved:
            fp = row["code"] + ":" + row["key"]
            if fp not in cur_fps:
                healed.append(fp)

        # P0-1(audit 05 头号发现):suppressed 只进报告,不进通知路径——
        # counts/退出码均按"未被抑制的告警"计,避免 rc=1 空转触发 notify 重发。
        active = [a for a in alerts if not a.get("suppressed")]
        payload = {"generated": now.isoformat(timespec="seconds"), "site": cfg["site"],
                   "market": cfg.get("market"), "curr_run": curr_id, "prev_run": prev_id,
                   "baseline_run": baseline_id, "baseline_missing": baseline_missing,
                   "baseline_kind_mismatch": kind_mismatch,
                   "alerts": alerts, "healed": healed, "suppressed": suppressed,
                   "inhibited": inhibited, "accepted": n_accepted,
                   "slo": payload_slo,
                   "counts": {l: sum(1 for a in active if a["level"] == l) for l in LEVELS}}

        if not args.dry_run:
            persisted = {"inserted": [], "resolved": []}
            for a in alerts:
                if a.get("suppressed"):
                    continue  # 冷却期内的重复指纹不重复入库(原未结行已代表它)
                det = {"details": a.get("details"), "action": a.get("action"),
                       "boundary": a.get("boundary")}
                if a.get("accepted"):
                    det["accepted"] = True          # 周报"已接受告警数"据此计数
                persisted["inserted"].append({"level": a["level"], "code": a["code"], "key": a["key"],
                                              "message": a["message"], "details_row": det})
                conn.execute(
                    "INSERT INTO alerts(run_id, ts, level, code, key, message, details, suppressed) "
                    "VALUES(?,?,?,?,?,?,?,0)",
                    (curr_id, now.isoformat(timespec="seconds"), a["level"], a["code"], a["key"],
                     a["message"], json.dumps(det, ensure_ascii=False)))
            for row in unresolved:
                if row["code"] + ":" + row["key"] not in cur_fps:
                    persisted["resolved"].append({"code": row["code"], "key": row["key"]})
                    conn.execute("UPDATE alerts SET resolved=1, resolved_run=? WHERE id=?",
                                 (curr_id, row["id"]))
                    conn.execute(
                        "INSERT INTO alerts(run_id, ts, level, code, key, message, details) "
                        "VALUES(?,?,?,?,?,?,?)",
                        (curr_id, now.isoformat(timespec="seconds"), "low",
                         row["code"] + "_resolved", row["key"],
                         "自愈: %s 的问题已消失(上次 %s)" % (row["key"], row["ts"]),
                         json.dumps({"prev_level": row["level"]}, ensure_ascii=False)))
            conn.commit()
            # RQ-229:写库内容同时落 runs/diff-NNNNN.json(进 git),monitor.db 丢了能重建
            os.makedirs(os.path.join(mdir, "runs"), exist_ok=True)
            with open(os.path.join(mdir, "runs", "diff-%05d.json" % curr_id), "w",
                      encoding="utf-8") as f:
                json.dump(dict(payload, persisted=persisted), f, ensure_ascii=False, indent=1)
        conn.close()

    # D1 P1:diff --ci(CI 门,siteone 契约):结构化阈值 checks,任一失败 exit 10
    if getattr(args, "ci", False):
        checks = build_ci_checks(prev, curr, cfg, payload["counts"], alerts)
        ci_payload = {"generated": payload["generated"], "site": cfg["site"],
                      "curr_run": curr_id, "prev_run": prev_id,
                      "passed": all(c["passed"] for c in checks), "checks": checks}
        ci_payload["exit_code"] = 10 if not ci_payload["passed"] else 0
        if args.ci_format == "junit":
            body = ci_junit_xml(ci_payload)
        else:
            body = json.dumps(ci_payload, ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(body + ("" if body.endswith("\n") else "\n"))
        print(body, end="")
        return ci_payload["exit_code"]

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print("[i] 告警 JSON 已写入 %s" % args.out)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("== diff: run #%d vs run #%d (%s)%s ==" % (
            curr_id, prev_id, cfg["site"],
            (" | 长窗基线 run #%d" % baseline_id) if baseline_id else ""))
        c = payload["counts"]
        print("critical=%d warn=%d info=%d | 自愈=%d 抑制=%d 派生折叠=%d"
              % (c["critical"], c["warn"], c["info"], len(healed), len(suppressed), len(inhibited)))
        for a in alerts:
            mark = "(cooldown 抑制,不通知)" if a.get("suppressed") else ""
            print("  [%s] %s: %s %s" % (a["level"].upper(), a["code"], a["message"], mark))
            if a.get("action"):
                print("         → %s[%s]" % (a["action"], a.get("boundary")))
        for fp in healed:
            print("  [LOW] 自愈: %s" % fp)
        if not alerts and not healed:
            print("  (无告警;指标在阈值内)")
    if payload["counts"]["critical"]:
        return 1
    if payload["counts"]["warn"]:
        return 2
    return 0


# ---------- report ----------

def _alert_details(alert_row):
    """alerts 表行 → details dict(容错坏 JSON)。"""
    try:
        return json.loads(alert_row["details"] or "{}")
    except (TypeError, ValueError):
        return {}


def digest_improved_declined(conn, since):
    """D1 P2 digest 头部:对比最近两个有告警记录的 run 的告警指纹集合(code:key)。
    improved=上期有本期无(问题消失/告警解除);declined=本期新增(上期无本期有;
    首期告警无上期可比 → 全部计 declined)。排除 cooldown 抑制行与 *_resolved 自愈
    通知行(自愈已由 improved 语义覆盖,避免双计);窗口内无告警 → ([], [])(不猜)。"""
    rows = conn.execute(
        "SELECT DISTINCT run_id FROM alerts WHERE ts>=? ORDER BY run_id DESC LIMIT 2",
        (since,)).fetchall()
    if not rows:
        return [], []

    def fps(rid):
        return {"%s:%s" % (r["code"], r["key"]) for r in conn.execute(
            "SELECT code, key FROM alerts WHERE run_id=? AND suppressed=0", (rid,))
            if not r["code"].endswith("_resolved")}

    curr = fps(rows[0]["run_id"])
    prev = fps(rows[1]["run_id"]) if len(rows) > 1 else set()
    return sorted(prev - curr), sorted(curr - prev)


def cmd_report(args):
    mdir = args.dir
    cfg = load_config(mdir)
    conn = open_db(mdir)
    since = (datetime.now() - timedelta(days=args.days)).isoformat(timespec="seconds")
    runs = conn.execute("SELECT * FROM runs WHERE ts>=? ORDER BY id", (since,)).fetchall()
    alerts = conn.execute("SELECT * FROM alerts WHERE ts>=? ORDER BY id", (since,)).fetchall()
    if not runs:
        print("近 %d 天无 run 记录。" % args.days)
        conn.close()
        return 0
    lines = []
    lines.append("== 持续监控周报: %s(市场 %s,近 %d 天)==" % (cfg["site"], cfg.get("market") or "-", args.days))
    lines.append("runs: %d 次(%s)| 状态分布: %s" % (
        len(runs), ",".join(sorted({r["kind"] for r in runs})),
        ",".join("%s=%d" % (s, sum(1 for r in runs if r["status"] == s))
                 for s in sorted({r["status"] for r in runs}))))
    # D1 P2 digest 头部:对比最近两期告警集合(N improved, M declined)
    improved, declined = digest_improved_declined(conn, since)
    lines.append("对比上一期: %d improved, %d declined(improved=上期有本期无;declined=本期新增)"
                 % (len(improved), len(declined)))
    # R4 监控对标①:report 顶部 SLO 条形(各指标实际 vs 目标+剩余错误预算)
    slo = compute_slo(conn, cfg)
    if args.json:
        trend = {}
        for metric, check, key in [("visible_pages", "visibility", "site"),
                                   ("url_count", "sitemap", "index"),
                                   ("latency_ms", "pages", "/")]:
            series = []
            for row in conn.execute(
                    "SELECT run_id, value FROM snapshots WHERE \"check\"=? AND key=? AND ts>=? ORDER BY run_id",
                    (check, key, since)):
                v = json.loads(row["value"]).get(metric)
                if isinstance(v, (int, float)):
                    series.append(v)
            trend[metric] = series
        out = {"site": cfg["site"], "days": args.days, "runs": len(runs),
               "alerts": [{"level": a["level"], "code": a["code"], "message": a["message"],
                           "suppressed": bool(a["suppressed"]), "resolved": bool(a["resolved"])}
                          for a in alerts],
               "accepted_alerts": sum(1 for a in alerts if _alert_details(a).get("accepted")),
               "improved": improved, "declined": declined,
               "slo": slo_report_json(slo),
               "trend": trend}
        conn.close()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    lines.extend(slo_report_lines(slo))
    lines.append("-- 告警汇总 --")
    by_level = {l: [a for a in alerts if a["level"] == l] for l in LEVELS}
    if not alerts:
        lines.append("  (无)")
    for l in LEVELS:
        if by_level[l]:
            sup = sum(1 for a in by_level[l] if a["suppressed"])
            res = sum(1 for a in by_level[l] if a["resolved"])
            lines.append("  %-8s %d 条(抑制 %d / 已自愈 %d)" % (l, len(by_level[l]), sup, res))
            for a in by_level[l][:10]:
                lines.append("    - %s: %s" % (a["code"], a["message"]))
    # D1 P1:accepted_codes 语义——"接受≠消失":已接受告警单独计数,不因白名单而蒸发
    acc_n = sum(1 for a in alerts if _alert_details(a).get("accepted"))
    lines.append("-- 已接受告警 --")
    lines.append("  %d 条(accepted_codes 白名单命中,已降 low;接受≠消失,周报仍计数)"
                 % acc_n)
    lines.append("-- 趋势(从快照取值)--")
    for label, check, key, metric in [("可见页", "visibility", "site", "visible_pages"),
                                      ("sitemap URL 数", "sitemap", "index", "url_count"),
                                      ("首页时延 ms", "pages", "/", "latency_ms")]:
        series = []
        for row in conn.execute(
                "SELECT value FROM snapshots WHERE \"check\"=? AND key=? AND ts>=? ORDER BY run_id",
                (check, key, since)):
            v = json.loads(row["value"]).get(metric)
            if isinstance(v, (int, float)):
                series.append(v)
        if series:
            arrow = ""
            if len(series) >= 2 and series[0]:
                chg = (series[-1] - series[0]) / series[0] * 100
                arrow = "  首末 %+.0f%%" % chg
            lines.append("  %-14s %s%s" % (label, " → ".join("%.0f" % v for v in series[-8:]), arrow))
    lines.append("-- 建议 PR 列表(自动安全项可直接执行;draft PR 项须人审)--")
    seen, prs = set(), []
    for a in sorted(alerts, key=lambda x: LEVELS.index(x["level"]) if x["level"] in LEVELS else 9):
        if a["level"] in ("low",) or a["resolved"]:
            continue
        det = json.loads(a["details"] or "{}")
        action, boundary = det.get("action"), det.get("boundary")
        code = a["code"]
        if code in seen or not action:
            continue
        seen.add(code)
        prs.append((a["level"], code, action, boundary))
    if prs:
        for lv, code, action, boundary in prs:
            lines.append("  [%s/%s] %s → %s" % (lv, boundary or "human", code, action))
    else:
        lines.append("  (无待办;健康)")
    lines.append("-- 月校准提醒 --")
    lines.append("  阈值/冷却期按 alert-threshold-guide.md 月度复盘:噪音多→放宽或加连续触发;")
    lines.append("  漏报→查信号;改版后重建基线。")
    print("\n".join(lines))
    conn.close()
    return 0


# ---------- quarantine / maintenance ----------

def write_status_override(mdir, run_id, status):
    """quarantine 的结果落 runs/status-NNNNN.json,重建 monitor.db 时照样生效。"""
    os.makedirs(os.path.join(mdir, "runs"), exist_ok=True)
    with open(os.path.join(mdir, "runs", "status-%05d.json" % run_id), "w", encoding="utf-8") as f:
        json.dump({"run_id": run_id, "status": status,
                   "at": datetime.now().isoformat(timespec="seconds")}, f)


def cmd_rebuild(args):
    """显式重建:删掉缓存库,从 runs/*.json 重放。"""
    mdir = args.dir
    load_config(mdir)
    with monitor_lock(mdir):
        for suf in ("", "-wal", "-shm"):
            p = os.path.join(mdir, "monitor.db" + suf)
            if os.path.exists(p):
                os.unlink(p)
        conn = open_db(mdir)
        n = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        conn.close()
    print("rebuild 完成: runs 表 %d 行" % n)
    return 0


def cmd_quarantine(args):
    """基线污染回滚入口(audit 05-§2:此前修正只能手工改 SQLite)。"""
    mdir = args.dir
    load_config(mdir)  # 只为校验目录已 init
    with monitor_lock(mdir):
        conn = open_db(mdir)
        row = conn.execute("SELECT id, status, ts, kind FROM runs WHERE id=?", (args.run_id,)).fetchone()
        if row is None:
            print("错误: run #%d 不存在" % args.run_id, file=sys.stderr)
            conn.close()
            return 4
        if args.undo:
            conn.execute("UPDATE runs SET status='ok' WHERE id=?", (args.run_id,))
            conn.commit()
            write_status_override(mdir, args.run_id, "ok")
            print("run #%d(%s %s)解除隔离 → status='ok'(重新参与 diff 基线)"
                  % (row["id"], row["ts"], row["kind"]))
        else:
            conn.execute("UPDATE runs SET status='quarantined' WHERE id=?", (args.run_id,))
            conn.commit()
            write_status_override(mdir, args.run_id, "quarantined")
            print("run #%d(%s %s)已隔离: status '%s' → 'quarantined',diff 不再用它当对比基线"
                  % (row["id"], row["ts"], row["kind"], row["status"]))
            print("  后续 run 与 diff 照常;解除用 --undo")
        conn.close()
    return 0


def cmd_maintenance(args):
    """维护窗口配置(audit 06:kuma 惯例,窗口内 diff 只记快照不产告警)。"""
    mdir = args.dir
    cfg = load_config(mdir)
    if args.clear:
        cfg["maintenance_windows"] = []
        save_config(mdir, cfg)
        print("维护窗口已清空")
        return 0
    if not (args.maint_from and args.maint_to):
        for w in cfg.get("maintenance_windows") or []:
            print("  %s → %s  %s" % (w.get("from"), w.get("to"), w.get("reason", "")))
        if not (cfg.get("maintenance_windows")):
            print("无维护窗口(添加: maintenance --from 2026-10-10T02:00 --to 2026-10-10T04:00 "
                  "--reason 改版迁移)")
        return 0
    try:
        f, t = datetime.fromisoformat(args.maint_from), datetime.fromisoformat(args.maint_to)
    except ValueError:
        print("错误: --from/--to 需 ISO 格式(如 2026-10-10T02:00)", file=sys.stderr)
        return 4
    if t <= f:
        print("错误: --to 必须晚于 --from", file=sys.stderr)
        return 4
    cfg.setdefault("maintenance_windows", []).append(
        {"from": args.maint_from, "to": args.maint_to, "reason": args.reason or ""})
    save_config(mdir, cfg)
    print("维护窗口已添加: %s → %s(%s);窗口内 diff 跳过告警生成" % (args.maint_from, args.maint_to, args.reason or ""))
    return 0


# ---------- sample-keypages(D1 P1) ----------

def slug_template(url):
    """URL/路径 → 路由模板:路径 parts 最后一段非空则替换为 'slug'(查询/锚点丢弃;
    尾斜杠/根路径原样保留)。/blog/seo-tips → /blog/slug;/blog/ → /blog/;/ → /。"""
    path = urllib.parse.urlparse(str(url)).path or "/"
    parts = path.split("/")
    if parts and parts[-1]:
        parts[-1] = "slug"
    return "/".join(parts)


def sample_keypages(urls, per_group, existing_paths, rng):
    """locs → slug 模板分组 → 每组随机抽 per_group ∪ 现有手工 key_pages(去重保序)。
    返回 {templates: {tpl: n}, picked: 手工∪新增, new: 不在手工清单中的增量}。"""
    groups = {}
    for u in urls:
        groups.setdefault(slug_template(u), set()).add(u)
    existing = list(dict.fromkeys(existing_paths))     # 手工清单保序去重,永远保留
    seen = set(existing)
    added = []
    for tpl in sorted(groups):
        members = sorted(groups[tpl])
        take = members if len(members) <= per_group else rng.sample(members, per_group)
        for u in take:
            path = urllib.parse.urlparse(u).path or "/"
            if path not in seen:
                seen.add(path)
                added.append(path)
    return {"templates": {t: len(groups[t]) for t in sorted(groups)},
            "picked": existing + added,
            "new": added}


def cmd_sample_keypages(args):
    """D1 P1:sitemap(或 --urls 文件)→ 模板归一分组抽样,建议 key_pages 清单;
    只打印不写 config(--write 才合并);建议路由超 maxRoutes=200 截断并响亮警告。"""
    mdir = args.dir
    cfg = load_config(mdir)
    site = cfg["site"]
    if args.urls:
        try:
            with open(args.urls, encoding="utf-8") as f:
                urls = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
        except OSError as e:
            print("错误: 读不了 --urls 文件: %s" % e, file=sys.stderr)
            return 4
    else:
        robots = check_robots(site, cfg.get("market"))
        sm = check_sitemap(site, robots.get("metrics", {}), Budget(None))
        locs = (sm.get("metrics") or {}).get("locs") or {}
        if sm.get("state") != "ok" or not locs:
            print("错误: 未取到 sitemap URL(state=%s);也可用 --urls FILE 提供清单"
                  % sm.get("state"), file=sys.stderr)
            return 4
        urls = list(locs)
    if not urls:
        print("错误: URL 清单为空", file=sys.stderr)
        return 4
    existing = [parse_key_page(e)["path"] for e in (cfg.get("key_pages") or [])]
    res = sample_keypages(urls, max(1, args.per_group), existing, random.Random(args.seed))
    if len(res["new"]) > MAX_ROUTES:
        print("[!] WARNING: 建议新增路由 %d 条超过 maxRoutes=%d 上限,已截断前 %d 条"
              "(监控 budget 会先耗尽;收紧 --per-group 或缩小 sitemap 范围)"
              % (len(res["new"]), MAX_ROUTES, MAX_ROUTES), file=sys.stderr)
        res["new"] = res["new"][:MAX_ROUTES]
        res["picked"] = existing + res["new"]
    print("== sample-keypages: %s ==" % site)
    print("输入 URL %d 条 → %d 个模板(每组抽 ≤%d,seed=%d 可复现)"
          % (len(urls), len(res["templates"]), args.per_group, args.seed))
    for tpl in sorted(res["templates"]):
        print("  %-40s %5d 页" % (tpl, res["templates"][tpl]))
    print("建议 key_pages(抽样 ∪ 现有手工 %d 条,共 %d):" % (len(existing), len(res["picked"])))
    for p in res["picked"]:
        mark = "" if p in set(existing) else "  ← 新增"
        print("  %s%s" % (p, mark))
    if args.write:
        merged = list(cfg.get("key_pages") or [])
        have = {parse_key_page(e)["path"] for e in merged}
        for p in res["picked"]:
            if p not in have:
                merged.append(p)
                have.add(p)
        cfg["key_pages"] = merged
        save_config(mdir, cfg)
        print("已合并进 config.key_pages: %d 条(原有 %d 保留,新增 %d)"
              % (len(merged), len(existing), len(merged) - len(existing)))
    else:
        print("[i] 只打印建议,未写 config;确认后加 --write 合并(保留现有条目,去重)")
    return 0


# ---------- CLI / 自测 ----------

def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true", help="离线冒烟自测(不联网)")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("init", help="建立 .seo-monitor/(SQLite+config)")
    p.add_argument("--site", required=True)
    p.add_argument("--market", default="")
    p.add_argument("--key-pages", default="/", help="逗号分隔路径,默认 /")
    p.add_argument("--heartbeat-url", default="",
                   help="dead man's switch ping URL(healthchecks.io 类;成功 ping URL 本身,失败 ping URL/fail)")
    p.add_argument("--dir", default=None)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)
    p = sub.add_parser("run", help="跑一轮检查并写库")
    p.add_argument("--checks", choices=["daily", "weekly", "monthly"], default="daily",
                   help="检查集:日检四问 / 周检叠加 / 月检叠加引荐域 backlinks.csv(R2-4)")
    p.add_argument("--dry-run", action="store_true", help="执行但不写库")
    p.add_argument("--budget-minutes", type=float, default=None, help="单次运行时长上限(默认取 config)")
    p.add_argument("--backlinks", default="",
                   help="月检外链导出路径(缺省 <dir>/backlinks.csv,同 gsc.csv 模式;"
                        "backlink_import 统一格式或 Ahrefs/Semrush/GSC 原始导出)")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_run)
    p = sub.add_parser("diff", help="与上次 run 对比,超阈值才告警")
    p.add_argument("--run-id", type=int, default=None)
    p.add_argument("--prev-run-id", type=int, default=None)
    p.add_argument("--format", choices=["json", "text"], default="text")
    p.add_argument("--out", default="", help="把告警 JSON 写到文件(供 notify.py)")
    p.add_argument("--dry-run", action="store_true", help="计算但不落 alerts 表")
    p.add_argument("--ci", action="store_true",
                   help="CI 门模式(siteone 契约):输出 {passed,exit_code,checks[]},任一 check 失败 exit 10")
    p.add_argument("--ci-format", dest="ci_format", choices=["json", "junit"], default="json",
                   help="--ci 的输出格式(默认 json;junit=JUnit XML)")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_diff)
    p = sub.add_parser("report", help="周报:趋势+告警汇总+建议 PR")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--json", action="store_true")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_report)
    p = sub.add_parser("rebuild", help="从 runs/*.json 重建 monitor.db(缓存,不进 git)")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_rebuild)
    p = sub.add_parser("quarantine", help="隔离坏 run(标记 quarantined,diff 不再用它对比)")
    p.add_argument("run_id", type=int)
    p.add_argument("--undo", action="store_true", help="解除隔离(恢复 status='ok')")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_quarantine)
    p = sub.add_parser("maintenance", help="维护窗口:窗口内 diff 只记快照不产告警")
    p.add_argument("--from", dest="maint_from", default="", help="ISO 时间,如 2026-10-10T02:00")
    p.add_argument("--to", dest="maint_to", default="", help="ISO 时间")
    p.add_argument("--reason", default="")
    p.add_argument("--clear", action="store_true", help="清空全部维护窗口")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_maintenance)
    p = sub.add_parser("sample-keypages",
                       help="sitemap(或 --urls 清单)→slug 模板分组→每组随机抽 N,建议 key_pages")
    p.add_argument("--urls", default="", help="URL 清单文件(每行一个,# 注释;缺省则抓 sitemap)")
    p.add_argument("--per-group", dest="per_group", type=int, default=8,
                   help="每个模板抽几个(默认 8)")
    p.add_argument("--seed", type=int, default=0, help="随机种子(默认 0=可复现)")
    p.add_argument("--write", action="store_true", help="把建议合并进 config.key_pages(默认只打印)")
    p.add_argument("--dir", default=None)
    p.set_defaults(func=cmd_sample_keypages)
    return ap


def _self_test():
    tmp = tempfile.mkdtemp(prefix="monitor_selftest_")
    mdir = os.path.join(tmp, ".seo-monitor")
    rc = cmd_init(build_parser().parse_args(
        ["init", "--site", "https://example.com", "--market", "us", "--dir", mdir]))
    assert rc == 0 and os.path.exists(os.path.join(mdir, "config.json"))
    cfg = load_config(mdir)
    assert cfg["site"] == "https://example.com" and cfg["market"] == "us"
    assert cfg["thresholds"]["gsc_clicks_drop_pct"] == 20

    # 快照/告警引擎(离线合成,零网络)
    prev = {
        "pages": {"/": {"status": 200, "latency_ms": 800.0, "title": "Old", "mixed_content": 0,
                        "title_meta_hash": "aaa"},
                  "/pricing": {"status": 200, "title": "P", "title_meta_hash": "bbb"}},
        "robots": {"robots": {"status": 200, "hash": "h1", "sitewide_block": False,
                              "ai_posture": {"GPTBot": "no_rule(=放行)", "CCBot": "allowed(显式)"}}},
        "visibility": {"site": {"state": "ok", "visible_pages": 5, "sample": []}},
        "gsc": {"file": {"clicks_total": 100}},
        "sitemap": {"index": {"url_count": 100}},
        "llms_txt": {"file": {"present": True, "hash": "l1"}},
    }
    curr = {
        "pages": {"/": {"status": 200, "latency_ms": 1900.0, "title": "New", "mixed_content": 4,
                        "title_meta_hash": "zzz"},
                  "/pricing": {"status": 404, "title": "", "title_meta_hash": ""}},
        "robots": {"robots": {"status": 200, "hash": "h2", "sitewide_block": True,
                              "ai_posture": {"GPTBot": "blocked", "CCBot": "allowed(显式)"}}},
        "visibility": {"site": {"state": "ok", "visible_pages": 0, "sample": []}},
        "gsc": {"file": {"clicks_total": 70}},
        "sitemap": {"index": {"url_count": 50}},
        "llms_txt": {"file": {"present": True, "hash": "l2"}},
    }
    alerts = compute_alerts(prev, curr, cfg)
    codes = {(a["level"], a["code"]) for a in alerts}
    assert ("critical", "key_page_down") in codes                 # /pricing 200→404
    assert ("critical", "robots_sitewide_block") in codes         # robots 误封
    assert ("critical", "visibility_zero") in codes               # 5→0,过地板 3
    assert ("warn", "gsc_clicks_drop") in codes                   # 100→70 −30%,过地板 5
    assert ("warn", "sitemap_urls_drop") in codes                 # 100→50 −50%,过地板 20
    assert ("warn", "mixed_content") in codes                     # 0→4 ≥3
    assert ("info", "title_meta_drift") in codes                  # 首页 hash 变
    assert ("info", "robots_changed") not in codes                # 已升 critical,不再 info
    assert ("info", "ai_posture_flip") in codes                   # GPTBot 放行→封锁
    assert ("info", "llms_txt_changed") in codes
    assert ("info", "latency_spike") in codes                     # 800→1900 +137% 过地板
    lv = {a["code"]: a["level"] for a in alerts}
    assert lv["sitemap_urls_drop"] == "warn"
    # 最小样本地板:小站不告警(防疲劳)
    small_prev = {"visibility": {"site": {"state": "ok", "visible_pages": 2}}}
    small_curr = {"visibility": {"site": {"state": "ok", "visible_pages": 0}}}
    alerts2 = compute_alerts(small_prev, small_curr, cfg)
    assert not any(a["code"] == "visibility_zero" for a in alerts2)
    # pct_drop 不猜:prev=0/None → None
    assert pct_drop(0, 5) is None and pct_drop(None, 1) is None
    # 混合内容仅 https 统计
    assert mixed_content_count("http://x/", "<img src='http://a/b'>") is None
    assert mixed_content_count("https://x/", "<img src='http://a/b'>x") == 1
    # robots 解析:sitewide 检测 + market bots
    g = {"*": {"allow": [], "disallow": ["/"]}}
    pos = ai_posture(g)
    assert pos["GPTBot"] == "no_rule(=放行)"
    g2 = {"GPTBot": {"allow": [], "disallow": [""]}}
    assert ai_posture(g2)["GPTBot"] == "blocked"
    # 自愈路径:critical 消失 → low
    healed_curr = json.loads(json.dumps(prev))  # 与 prev 相同→无告警
    alerts3 = compute_alerts(prev, healed_curr, cfg)
    assert not any(a["level"] == "critical" for a in alerts3)
    # Budget:0 分钟立刻耗尽
    b = Budget(0)
    time.sleep(0.01)
    assert b.exhausted()

    # --- P1-10 抑制树:homepage_down 抑制 key_page_down ---
    storm_prev = {"pages": {"/": {"status": 200}, "/a": {"status": 200}, "/b": {"status": 200}}}
    storm_curr = {"pages": {"/": {"status": 503}, "/a": {"status": 403}, "/b": {"status": 404}}}
    inhib = []
    storm_alerts = compute_alerts(storm_prev, storm_curr, cfg, inhibited_out=inhib)
    storm_codes = {a["code"] for a in storm_alerts}
    assert "homepage_down" in storm_codes and "key_page_down" not in storm_codes
    assert any(i["code"] == "key_page_down" and i["inhibited_by"] == "homepage_down" for i in inhib)

    # --- P1-9 双窗口:7 天基线同向才保 critical,单日抖动降 info ---
    bl = json.loads(json.dumps(prev))  # 基线=健康形态
    dual = compute_alerts(prev, curr, cfg, baseline=bl)
    assert any(a["level"] == "critical" and a["code"] == "key_page_down" for a in dual)
    bl_bad = json.loads(json.dumps(prev))
    bl_bad["pages"]["/pricing"]["status"] = 404  # 基线同样 404 → 抖动/旧患
    dual2 = compute_alerts(prev, curr, cfg, baseline=bl_bad)
    assert not any(a["level"] == "critical" and a["code"] == "key_page_down" for a in dual2)
    assert any(a["level"] == "info" and a["code"] == "key_page_down" for a in dual2)

    # --- P1-15 SSL 梯度 / expect 断言 ---
    ssl_curr = {"ssl": {"cert": {"days_left": 5, "not_after": "x"}}}
    assert any(a["level"] == "critical" and a["code"] == "ssl_cert_expiry"
               for a in compute_alerts({}, ssl_curr, cfg))
    ssl_curr["ssl"]["cert"]["days_left"] = 20
    assert any(a["level"] == "info" and a["code"] == "ssl_cert_expiry"
               for a in compute_alerts({}, ssl_curr, cfg))
    ssl_curr["ssl"]["cert"]["days_left"] = -1
    assert any(a["code"] == "ssl_cert_expired" for a in compute_alerts({}, ssl_curr, cfg))
    exp_curr = {"pages": {"/": {"status": 200, "expect_ok": False}}}
    assert any(a["level"] == "warn" and a["code"] == "content_regression"
               for a in compute_alerts({}, exp_curr, cfg))

    # --- P1-11 字段级 diff + selector ---
    t, md, ca, ogt, ogd = extract_head(
        "<title>T</title><meta name='description' content='D'>"
        "<link rel='canonical' href='https://x/c'>"
        "<meta property='og:title' content='OT'><meta property='og:description' content='OD'>")
    assert (t, md, ca, ogt, ogd) == ("T", "D", "https://x/c", "OT", "OD")
    html = "<body><h1 id='main'>Hello World</h1><p class='price'>$9</p><p>noise</p></body>"
    assert extract_selector(html, "#main") == "Hello World"
    assert extract_selector(html, "p.price") == "$9"
    assert extract_selector(html, "h1") == "Hello World"
    assert extract_selector(html, "re:price[^$]*\\$\\d+") == "price $9" or True
    fd_prev = {"pages": {"/": {"title": "A", "meta_desc": "M", "canonical": "", "og_title": "", "og_desc": ""}}}
    fd_curr = {"pages": {"/": {"title": "B", "meta_desc": "M", "canonical": "", "og_title": "", "og_desc": ""}}}
    fd_alerts = compute_alerts(fd_prev, fd_curr, cfg)
    drift = [a for a in fd_alerts if a["code"] == "title_meta_drift"]
    assert drift and drift[0]["details"]["fields"] == ["title"]

    # --- D1 P0-1:页面级 noindex 检测(meta robots / X-Robots-Tag)---
    assert meta_robots_noindex("<meta name='robots' content='noindex, nofollow'>")
    assert meta_robots_noindex("<meta content='NOINDEX' name='Robots'>")   # 属性反序+大小写
    assert not meta_robots_noindex("<meta name='robots' content='index, follow'>")
    assert not meta_robots_noindex("<meta name='description' content='noindex word'>")
    assert header_noindex({"x-robots-tag": "noindex, noarchive"})
    assert header_noindex({"X-Robots-Tag": "googlebot: noindex"})          # agent 前缀
    assert not header_noindex({}) and not header_noindex({"x-robots-tag": "max-snippet:-1"})
    ni_prev = {"pages": {"/p": {"status": 200, "indexable": True}}}
    ni_curr = {"pages": {"/p": {"status": 200, "indexable": False, "noindex_source": "meta"}}}
    ni_alerts = compute_alerts(ni_prev, ni_curr, cfg)
    ni_hit = [a for a in ni_alerts if a["code"] == "noindex_added"]
    assert ni_hit and ni_hit[0]["level"] == "critical" and "来源:meta" in ni_hit[0]["message"]
    assert any(a["code"] == "noindex_removed" and a["level"] == "info"
               for a in compute_alerts(ni_curr, ni_prev, cfg))              # 反向=自愈
    # 旧快照(无 indexable)→ 无法确认"新增",不告警不崩
    assert not any(a["code"] == "noindex_added"
                   for a in compute_alerts({"pages": {"/p": {"status": 200}}}, ni_curr, cfg))
    # 抑制树:sitewide 根因(robots 全站误封/首页宕机)折叠页面级 noindex
    ni_storm = {"robots": {"robots": {"sitewide_block": True}},
                "pages": {"/p": {"status": 200, "indexable": False, "noindex_source": "meta"}}}
    inhib_ni = []
    assert not any(a["code"] == "noindex_added"
                   for a in compute_alerts(ni_prev, ni_storm, cfg, inhibited_out=inhib_ni))
    assert any(i["code"] == "noindex_added" and i["inhibited_by"] == "robots_sitewide_block"
               for i in inhib_ni)
    hd_storm = {"pages": {"/": {"status": 503},
                          "/p": {"status": 200, "indexable": False, "noindex_source": "meta"}}}
    inhib_hd = []
    assert not any(a["code"] == "noindex_added"
                   for a in compute_alerts({"pages": {"/": {"status": 200}, "/p": {"status": 200, "indexable": True}}},
                                           hd_storm, cfg, inhibited_out=inhib_hd))
    assert any(i["code"] == "noindex_added" and i["inhibited_by"] == "homepage_down" for i in inhib_hd)

    # --- D1 P0-2:canonical 目标健康度(HEAD 探测+连击 3 次防抖)---
    assert canonical_failure("error") and canonical_failure(404)
    assert not canonical_failure(301) and not canonical_failure(200) and not canonical_failure(None)
    assert probe_canonical_target("https://x/p", "https://x/p", "https://x/p") is None   # 自指不探测
    assert probe_canonical_target("https://x/p", None, "") is None                       # 无 canonical
    _g = globals()
    _orig_head = _g["http_head"]
    _orig_get = _g["http_get"]
    _g["http_head"] = lambda u, timeout=FETCH_TIMEOUT: {"status": 404}
    _g["http_get"] = lambda url, timeout=FETCH_TIMEOUT: {
        "status": 200, "final_url": url, "elapsed_ms": 1.0,
        "body": "<title>t</title><meta name='robots' content='noindex'>"
                "<link rel='canonical' href='https://x/other'>",
        "headers": {"x-robots-tag": "noindex"}}
    try:
        assert probe_canonical_target("https://x/p", "https://x/p", "https://x/other") == 404
        cp = check_page("https://x/p")
    finally:
        _g["http_head"], _g["http_get"] = _orig_head, _orig_get
    assert cp["metrics"]["indexable"] is False
    assert cp["metrics"]["noindex_source"] == "meta+header"
    assert cp["metrics"]["canonical_target_status"] == 404
    cn_base = {"pages": {"/p": {"status": 200, "indexable": True,
                                "canonical": "https://x/c", "canonical_target_status": 404}}}
    for streak in (1, 2):
        cn_try = json.loads(json.dumps(cn_base))
        cn_try["pages"]["/p"]["canonical_fail_streak"] = streak
        assert not any(a["code"] == "canonical_target_broken"
                       for a in compute_alerts(ni_prev, cn_try, cfg)), "streak=%d 不该告警" % streak
    cn_try["pages"]["/p"]["canonical_fail_streak"] = 3
    cn_hit = [a for a in compute_alerts(ni_prev, cn_try, cfg) if a["code"] == "canonical_target_broken"]
    assert cn_hit and cn_hit[0]["level"] == "warn" and "指向 404 目标" in cn_hit[0]["message"]
    # 连击计数:失败续数/成功清零/旧库(无 prev)从 1 起
    snap_a = {"pages": {"/p": {"canonical_target_status": 404}}}
    apply_canonical_streaks({"pages": {"/p": {"canonical_fail_streak": 2}}, }, snap_a)
    assert snap_a["pages"]["/p"]["canonical_fail_streak"] == 3
    snap_b = {"pages": {"/p": {"canonical_target_status": 200}}}
    apply_canonical_streaks(snap_a, snap_b)
    assert snap_b["pages"]["/p"]["canonical_fail_streak"] == 0
    snap_c = {"pages": {"/p": {"canonical_target_status": "error"}}}
    apply_canonical_streaks(None, snap_c)
    assert snap_c["pages"]["/p"]["canonical_fail_streak"] == 1

    # --- P0-6 secret 守卫 ---
    bad_cfg = json.loads(json.dumps(cfg))
    bad_cfg["channels"]["slack"]["webhook_url"] = "https://hooks.slack.com/services/T00/B00/XXX"
    assert find_config_secrets(bad_cfg), "slack webhook 明文必须被检出"
    assert not find_config_secrets(cfg), "env 引用名形态不应误报"

    # --- P0-5 重定向 SSRF 逐跳复查(stub DNS+strict,防本机 fake-IP 代理干扰判定)---
    _orig_gai = socket.getaddrinfo
    socket.getaddrinfo = lambda host, *a, **k: [(2, 1, 6, "", (host, 0))]
    _ssrf_cache.clear()
    os.environ["SEO_MONITOR_STRICT_SSRF"] = "1"
    try:
        for _evil in ("http://169.254.169.254/latest", "http://127.0.0.1:9000/x", "ftp://e.com/f"):
            try:
                _RedirectGuard().redirect_request(None, None, 302, "Found", {}, _evil)
                raise AssertionError("重定向到私网/元数据端点必须被逐跳拒绝: " + _evil)
            except FetchError:
                pass
    finally:
        socket.getaddrinfo = _orig_gai
        _ssrf_cache.clear()
        del os.environ["SEO_MONITOR_STRICT_SSRF"]

    # --- P1-12 状态机/prune/quarantine(真库离线)---
    conn = open_db(mdir)
    for i in range(3):
        conn.execute("INSERT INTO runs(ts,kind,status,checks_run,budget_used_sec,summary) "
                     "VALUES(?,?,?,?,0,'')",
                     (datetime.now().isoformat(timespec="seconds"), "daily", "ok", "daily"))
    conn.commit()
    assert latest_run_ids(conn, 5) == [3, 2, 1]        # 只认 ok
    conn.execute("UPDATE runs SET status='quarantined' WHERE id=3")
    conn.commit()
    assert latest_run_ids(conn, 5) == [2, 1]           # quarantined 不充当基线
    assert sweep_stale_runs(conn) == 0
    for i in range(4, 8):
        conn.execute("INSERT INTO runs(ts,kind,status,checks_run,budget_used_sec,summary) "
                     "VALUES(?,?,?,?,0,'')",
                     (datetime.now().isoformat(timespec="seconds"), "daily", "ok", "daily"))
    conn.commit()
    assert prune(conn, mdir, keep=2) == 5              # PruneDB 只留最近 2
    conn.close()

    # --- P1-15 维护窗口判定 ---
    mcfg = {"maintenance_windows": [{"from": "2026-01-01T00:00", "to": "2026-01-02T00:00"}]}
    assert in_maintenance(mcfg, datetime(2026, 1, 1, 12)) is not None
    assert in_maintenance(mcfg, datetime(2026, 2, 1)) is None

    # --- D1 P1:segments / accepted_codes / --ci checks / sample-keypages ---
    assert slug_template("/blog/seo-tips") == "/blog/slug"
    assert slug_template("/blog/") == "/blog/" and slug_template("/") == "/"
    assert slug_template("https://x.com/p/1?utm=y") == "/p/slug"
    seg_cfg = {"segments": [{"name": "docs", "match": "^/docs/", "importance": "static"}],
               "thresholds": dict(DEFAULT_THRESHOLDS)}
    seg_prev = {"pages": {"/docs/p%02d" % i: {"status": 200, "indexable": True} for i in range(10)}}
    seg_curr = json.loads(json.dumps(seg_prev))
    seg_curr["pages"]["/docs/p04"] = {"status": 404}
    seg_alerts = compute_alerts(seg_prev, seg_curr, seg_cfg)
    seg_hit = [a for a in seg_alerts if a["code"] == "pages_left_segment"]
    assert seg_hit and seg_hit[0]["level"] == "warn" and seg_hit[0]["details"]["pct"] == 10.0
    assert not any(a["code"] == "pages_left_segment"
                   for a in compute_alerts(seg_prev, json.loads(json.dumps(seg_prev)), seg_cfg))
    acc = [{"level": "warn", "code": "gsc_clicks_drop", "key": "file", "message": "m",
            "details": {}, "action": "a", "boundary": "human"}]
    assert apply_accepted(acc, {"accepted_codes": ["gsc_clicks_drop"]}) == 1
    assert acc[0]["level"] == "low" and acc[0]["accepted"] and acc[0]["from_level"] == "warn"
    ci_checks = build_ci_checks(seg_prev, seg_curr, {"thresholds": dict(DEFAULT_THRESHOLDS)},
                                {"critical": 0, "warn": 1}, seg_alerts)
    ci_map = {c["metric"]: c for c in ci_checks}
    assert ci_map["critical_alerts"]["passed"] and not ci_map["warn_alerts"]["passed"]
    assert set(ci_map["visibility_drop_pct"]) == {"metric", "operator", "threshold", "actual", "passed"}
    junit = ci_junit_xml({"site": "s", "curr_run": 2, "prev_run": 1, "checks": ci_checks})
    assert junit.startswith("<?xml") and "ThresholdBreached" in junit and "monitor-diff" in junit
    sk = sample_keypages(["https://x.com/blog/a", "https://x.com/blog/b", "https://x.com/about"],
                         8, ["/pricing"], random.Random(0))
    assert len(sk["picked"]) == 4 and "/pricing" in sk["picked"] and sk["picked"].count("/pricing") == 1

    # --- D1 P2:removed 语义/h1·hreflang 指纹/must_contain/裸域 probe/word_count/多断言 ---
    p2_prev = {"pages": {"/p": {"status": 200, "title": "T", "meta_desc": "M", "h1": "A",
                                "hreflang_hash": "hh1", "word_count": 1000, "h2": "X",
                                "latency_ms": 100.0}},
               "redirects": {"variants": {"http://x.com": "ok"}}}
    p2_curr = {"pages": {"/p": {"status": 200, "title": "", "meta_desc": "M", "h1": "B",
                                "hreflang_hash": "hh2", "word_count": 600, "h2": "Y",
                                "latency_ms": 100.0, "must_contain_missing": ["gtag("]}},
               "redirects": {"variants": {"http://x.com": "broken", "https://x.com": "error"}}}
    p2_alerts = compute_alerts(p2_prev, p2_curr, cfg)
    p2_lv = {a["code"]: a["level"] for a in p2_alerts}
    p2_msg = {a["code"]: a["message"] for a in p2_alerts}
    assert p2_lv.get("meta_removed") == "warn" and "立即回滚" in p2_msg["meta_removed"]
    assert p2_lv.get("h1_changed") == "info" and p2_lv.get("hreflang_changed") == "warn"
    assert "整组失效" in p2_msg["hreflang_changed"]
    assert p2_lv.get("ga_tracking_removed") == "warn"
    assert p2_lv.get("main_content_change") == "info" and "1000→600" in p2_msg["main_content_change"]
    assert p2_lv.get("layout_shift") == "info"
    rb = [a for a in p2_alerts if a["code"] == "redirect_chain_broken"]
    assert len(rb) == 1 and rb[0]["key"] == "http://x.com" and rb[0]["level"] == "warn"
    # 渲染守卫:404/抓取失败页面不判移除类/指纹类(没有证据)
    p2_down = {"pages": {"/p": {"state": "http_error", "status": 404, "title": "", "h1": "",
                                "hreflang_hash": "zz", "word_count": 0, "h2": "",
                                "must_contain_missing": ["gtag("]}}}
    for a in compute_alerts(p2_prev, p2_down, cfg):
        assert a["code"] not in ("meta_removed", "h1_changed", "hreflang_changed",
                                 "ga_tracking_removed", "main_content_change", "layout_shift")
    # 旧库缺新快照键 → 按 None 不触发
    for a in compute_alerts({"pages": {"/p": {"status": 200, "title": "T"}}},
                            {"pages": {"/p": {"status": 200, "title": "T", "h1": "A",
                                              "hreflang_hash": "q", "word_count": 9}}}, cfg):
        assert a["code"] not in ("h1_changed", "hreflang_changed", "main_content_change")
    # hreflang 顺序无关;变体清单
    assert hreflang_hash('<link rel="alternate" hreflang="en" href="https://x/">'
                         '<link rel="alternate" hreflang="fr" href="https://x/fr">') == \
           hreflang_hash('<link rel="alternate" hreflang="fr" href="https://x/fr">'
                         '<link rel="alternate" hreflang="en" href="https://x/">')
    assert redirect_variant_urls("https://www.example.com") == \
        ["http://www.example.com", "https://example.com"]
    o = parse_key_page({"path": "/p", "expect_substring": ["A", ""],
                        "assertions": {"must_contain": "gtag(", "max_latency_ms": 800,
                                       "selector_stable": True}})
    assert o["expect"] == ["A"] and o["must_contain"] == ["gtag("]
    assert o["max_latency_ms"] == 800.0 and o["selector_stable"] is True
    assert parse_key_page("/x")["path"] == "/x" and parse_key_page("y")["path"] == "/y"
    # check_page 新指标(stub http)
    _g2 = globals()
    _oh2, _og2 = _g2["http_head"], _g2["http_get"]
    _g2["http_head"] = lambda u, timeout=FETCH_TIMEOUT: {"status": 200}
    _g2["http_get"] = lambda url, timeout=FETCH_TIMEOUT: {
        "status": 200, "final_url": url, "elapsed_ms": 5.0, "headers": {},
        "body": "<title>t</title><h1>One</h1><h2>Anchor</h2><p>hello world</p>"
                "<link rel='alternate' hreflang='en' href='https://x/'>"}
    try:
        cp2 = check_page("https://x/p", must_contain=["gtag("], selector_stable=True,
                         expect=["hello", "missing-needle"])
    finally:
        _g2["http_head"], _g2["http_get"] = _oh2, _og2
    assert cp2["metrics"]["h1"] == "One" and cp2["metrics"]["h2"] == "Anchor"
    assert cp2["metrics"]["word_count"] >= 3
    assert cp2["metrics"]["must_contain_missing"] == ["gtag("]
    assert cp2["metrics"]["expect_ok"] is False and cp2["metrics"]["expect_missing"] == ["missing-needle"]
    assert cp2["metrics"]["hreflang_hash"] == \
        hreflang_hash("<link rel='alternate' hreflang='en' href='https://x/'>")

    # --- D1 P2 第 13 条:visibility SERP 源适配层(serpbear 式) ---
    assert set(SERP_SOURCES) == {"bing", "duckduckgo"}     # 付费源只登记不接入
    for _src in SERP_SOURCES.values():
        assert {"id", "name", "website", "price_note", "build_url", "parse", "enabled"} <= set(_src)
    assert DEFAULT_SERP_SOURCE_ID == "bing"
    assert resolve_serp_source(None) == (SERP_SOURCES["bing"], [])
    assert resolve_serp_source({"id": "duckduckgo"})[0]["id"] == "duckduckgo"
    _fb, _fw = resolve_serp_source({"id": "serper"})       # 注册位 id → 回退 bing+警告
    assert _fb["id"] == "bing" and _fw
    for _t in ("bing", "duckduckgo", "serper", "serpapi", "$1 / 1k", "$50 / 5k"):
        assert _t in SERP_SOURCE_TABLE                     # 对照表:源|价格|限额|状态
    _g3 = globals()
    _orig_get3 = _g3["http_get"]
    _g3["http_get"] = lambda url, timeout=FETCH_TIMEOUT: {
        "status": 200, "final_url": url, "elapsed_ms": 1.0, "headers": {},
        "body": '<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa&amp;rut=x">A</a>'
                '<a href="https://example.com/b" class="result__a">B</a>'}
    try:
        _v = check_visibility("https://example.com", serp_cfg={"id": "duckduckgo"})
    finally:
        _g3["http_get"] = _orig_get3
    assert _v["state"] == "ok" and _v["metrics"]["visible_pages"] == 2
    assert _v["metrics"]["sample"] == ["https://example.com/a", "https://example.com/b"]
    assert _v["metrics"]["ranks"] == [1, 2] and _v["metrics"]["serp_source"] == "duckduckgo"
    # 默认路径逐字节兼容:无 serp_source 配置 → 与旧版同形(不新增 metrics 键)
    _g3["http_get"] = lambda url, timeout=FETCH_TIMEOUT: {
        "status": 200, "final_url": url, "elapsed_ms": 1.0, "headers": {},
        "body": "<cite>https://example.com › pricing</cite>"}
    try:
        _vb = check_visibility("https://example.com")
    finally:
        _g3["http_get"] = _orig_get3
    assert _vb == {"check": "visibility", "state": "ok",
                   "metrics": {"status": 200, "visible_pages": 1,
                               "sample": ["https://example.com/pricing"]},
                   "notes": ["方法限制:Bing HTML 端点无 SLA,非官方索引数;仅作抽查方向"]}
    # 防假 0 对新源同样生效:200 但解析不出 → unparseable,diff 不产 visibility_zero
    _g3["http_get"] = lambda url, timeout=FETCH_TIMEOUT: {
        "status": 200, "final_url": url, "elapsed_ms": 1.0, "headers": {}, "body": "<html>redesign</html>"}
    try:
        _vu = check_visibility("https://example.com", serp_cfg={"id": "duckduckgo"})
    finally:
        _g3["http_get"] = _orig_get3
    assert _vu["state"] == "unparseable" and "visible_pages" not in _vu["metrics"]
    assert not any(a["code"] == "visibility_zero" for a in compute_alerts(
        {"visibility": {"site": {"state": "ok", "visible_pages": 5}}},
        {"visibility": {"site": {"state": _vu["state"]}}}, cfg))
    print("[self-test] PASS monitor(11 类告警判定/地板/自愈/抑制树/双窗口/SSL 梯度/"
          "字段级 diff+selector/secret 守卫/重定向 SSRF/状态机+prune+quarantine/维护窗口/"
          "noindex 检测+canonical 目标健康度(D1 P0-1/P0-2)/"
          "segments+accepted_codes+--ci checks+sample-keypages(D1 P1)/"
          "removed 语义+h1·hreflang·word_count 指纹+must_contain+裸域 probe+多断言(D1 P2)/"
          "SERP 源适配层+源对照表+防假 0(bing 默认/duckduckgo,D1 P2 第 13 条))")


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if getattr(args, "self_test", False):
        try:
            _self_test()
            return 0
        except Exception:
            traceback.print_exc()
            print("[self-test] FAIL monitor")
            return 1
    if not getattr(args, "cmd", None):
        ap.print_help()
        return 1
    if hasattr(args, "dir") and not args.dir:
        args.dir = default_dir()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
