#!/usr/bin/env python3
"""AI 引用流量日志分析(下界口径)。stdlib-only。

读 apache/nginx combined 日志(stdin 或文件),按 AI referrer 域归因请求:
  chatgpt.com / perplexity.ai / gemini.google.com / copilot.microsoft.com /
  claude.ai / grok.com(含子域)。

输出:
  - 每域请求数 + 独立路径数
  - 全站热门路径 top20(按命中)
  - 无 referrer 请求数 → 提示:App 内打开常不带 referrer,测得的是下界
  - --bot-ua:同时统计 AI 爬虫 UA(GPTBot / OAI-SearchBot / ChatGPT-User /
    ClaudeBot / Claude-SearchBot / PerplexityBot)的到访(先行指标:先爬后引)
  - --classify:bot 四桶分类(Profound/Otterly/Peec 三家口径合并)——
    on_demand_fetcher / search_index / training / agent_visits(宽匹配)/
    unclassified(未知 UA 单列);KPI 扩展:failure_rate(4xx+5xx 占比,按 bot 与
    按桶两级;先剔除漏洞扫描探测路径 /.env、/.git/、id_rsa、../ 等——冒充 AI UA 的
    扫描器 404 不算可见性失败;UA 未验证,按官方 IP 段/反查核实)+ 每桶访问数 Top URL + bot×status 矩阵 + llms.txt 双基线
    (Otterly 90 天实验参考值)+ retrieval vs training 分层结论
  - --attribution:归因工具箱输出——GA4 custom channel 正则(锚定官方域名)+
    三条纪律注记 + "自报归因"问卷模板两问
  - --as-panel-import:分析输出之外,追加 citation_panel 导入 JSON(R6 竞品 Ryze
    一方数据线对齐:GA4/GSC 式真实 AI-referral 流量即可见性证据,比 prompt 采样
    便宜且真实)——referrer 域→引擎映射(chatgpt.com→chatgpt 等,对齐面板六引擎),
    每引擎 sessions=请求命中数(未做会话化)、cited_urls=目标路径聚合(按命中数降序)。
    诚实口径注释:这是下界证据(real)——App 内打开常不带 referrer,真实 AI 引流
    ≥ 此数;与 prompt 采样(est)分轨,导入面板时标 source:referral,由
    `citation_panel.py record --from-referral file.json` 消费(两轨分开列,不加权混合)

日志格式:combined(CLF)或每行一个 JSON 对象
  (path/uri/url、status/status_code、user_agent/ua、referer/referrer 等常见键名)。
  源站在 CDN/隧道后时,combined 行尾可追加真实客户端 IP 字段 cip= / client_ip= / real_ip=(如 nginx
  log_format 末尾 'cip=$某个只取可信 CF-Connecting-IP 的变量');值是合法 IP 时取代第一列的上一跳地址,
  "-" 或不是 IP 时仍用第一列。没有这个字段的旧行照常解析。

用法:
  cat access.log | python3 ai_referral_log.py
  python3 ai_referral_log.py access.log [--top 20] [--bot-ua] [--classify] [--attribution]
                                        [--as-panel-import]
  python3 ai_referral_log.py access.log --as-panel-import > referral.json
                                        # 重定向整文件给 citation_panel record --from-referral
  python3 ai_referral_log.py --attribution          # 只输出归因工具箱,无需日志
  python3 ai_referral_log.py --self-test
"""
import argparse
import ipaddress
import json
import re
import sys
import traceback
from collections import Counter
from datetime import datetime

AI_REFERRER_DOMAINS = ("chatgpt.com", "perplexity.ai", "gemini.google.com",
                       "copilot.microsoft.com", "claude.ai", "grok.com")
BOT_UAS = ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
           "Claude-SearchBot", "PerplexityBot")

# ---- R6 referral 桥(referrer 域 → citation_panel 面板引擎,对齐六引擎) ----
DOMAIN_TO_ENGINE = {
    "chatgpt.com": "chatgpt",
    "perplexity.ai": "perplexity",
    "gemini.google.com": "gemini",
    "copilot.microsoft.com": "copilot",
    "claude.ai": "claude",
    "grok.com": "grok",
}
PANEL_IMPORT_MARKER = "-- referral panel import (source=referral; citation_panel record --from-referral) --"
PANEL_IMPORT_SCOPE = ("下界证据(real): App 内打开常不带 referrer,真实 AI 引流 ≥ 此数;"
                      "sessions=请求命中数(未做会话化);与 prompt 采样(est)分轨,"
                      "导入面板标 source:referral,两轨分开列不加权混合")

LOG_RE = re.compile(
    r'^(\S+)\s+\S+\s+\S+\s+\[([^\]]+)\]\s+"([^"]*)"\s+(\d{3})\s+(\S+)'
    r'(?:\s+"([^"]*)"\s+"([^"]*)")?')
# combined 之后行尾的真实客户端 IP 字段(源站在 CDN/隧道后,第一列只是上一跳)
CLIENT_IP_FIELD_RE = re.compile(r'(?:^|\s)(?:cip|client_ip|real_ip)=(\S+)')

BOT_UA_RE = re.compile("|".join(re.escape(b) for b in BOT_UAS))

# ---- bot 四桶分类(B5:Profound/Otterly/Peec 三家口径合并) ----
# on_demand_fetcher:按用户请求实时抓取(AI 答案直接取材源)
# search_index:AI 搜索/答案的专用索引爬虫(封 = 可见性失败)
# training:基础模型训练(封 = 授权决策,不影响引用)
# agent_visits:其余 AI agent UA 宽匹配;未知 UA 单列 unclassified
BOT_TIERS = {
    "on_demand_fetcher": ("ChatGPT-User", "Claude-User", "Perplexity-User",
                          "MistralAI-User", "Meta-ExternalFetcher", "Google-Agent",
                          "Claude-Agent"),
    "search_index": ("PerplexityBot", "OAI-SearchBot", "Claude-SearchBot",
                     "Amzn-SearchBot", "meta-webindexer", "Baiduspider",
                     "YandexAdditional"),
    "training": ("GPTBot", "ClaudeBot", "CCBot", "Google-Extended", "Bytespider"),
}
# 名单口径(B46,2026-10-21):按 references/technical/ai-crawler-policy.md 第七节与其链接的官方页改。
# - GoogleOther 移出 training:Google 官方说它是产品团队通用抓取器,不影响任何具体产品(如一次性研发
#   抓取)→ 宽匹配 agent_visits。
# - 补 meta-webindexer(Meta AI 搜索)、Google-Agent(用户触发)、Baiduspider(百度搜索)、
#   YandexAdditional(UA `YandexAdditional/1.0`,控制 Yandex AI 回答,归 search_index)、
#   OAI-AdsBot(广告落地页审核,不训练 → agent_visits)。
# - 官方页没有的 token(UNVERIFIED_UA_TOKENS)移出显式三桶,只按宽匹配进 agent_visits 并标「未核」。
# - 补 Claude-Agent(2026-11-05):Anthropic 托管浏览器替用户办事,真实浏览器 UA 里加这个 token,
#   IP 表在 claude.com/.well-known/sail;和 Google-Agent 同归 on_demand_fetcher。
# - 匹配不分大小写:Meta 官方 UA 全小写(`meta-externalagent/1.1`、`meta-webindexer/1.1`)。
TIER_ORDER = ("on_demand_fetcher", "search_index", "training",
              "agent_visits", "unclassified")
# 官方 bot 页上找不到的 token:不进显式三桶,宽匹配记 agent_visits,输出标「未核」
UNVERIFIED_UA_TOKENS = ("Claude-Web", "AzureAI-SearchBot", "DeepSeekBot", "GrokBot",
                        "Manus-User", "Gemini-Deep-Research")
# 其余 AI agent UA token(宽匹配,不在显式三桶名单内)→ agent_visits
AGENT_UA_TOKENS = ("Meta-ExternalAgent", "MistralAI-Index", "MistralAI-Training",
                   "Amazonbot", "Applebot-Extended", "DuckAssistBot", "YouBot",
                   "cohere-ai", "AI2Bot", "Diffbot", "Timpibot", "iaskspider",
                   "omgili", "Google-CloudVertexBot", "Panscient",
                   "VelenPublicWebCrawler", "Awakari", "GoogleOther", "OAI-AdsBot") \
    + UNVERIFIED_UA_TOKENS

_BOT_TIER_OF = {b: t for t, bs in BOT_TIERS.items() for b in bs}
_CANON = {b.lower(): b for b in list(_BOT_TIER_OF) + list(AGENT_UA_TOKENS)}
_BOT_TOKEN_RE = re.compile("|".join(re.escape(b) for b in
                                    sorted(_BOT_TIER_OF, key=len, reverse=True)), re.I)
_AGENT_UA_RE = re.compile("|".join(re.escape(a) for a in
                                   sorted(AGENT_UA_TOKENS, key=len, reverse=True)), re.I)


# ---- 漏洞扫描探测路径(B26):扫描器常冒充 AI 爬虫 UA,这些请求 404 不代表可见性被封 ----
PROBE_PATH_RE = re.compile(
    r"(?:^|/)\.env(?:[./_?-]|$)|/\.git(?:/|$)|/\.svn(?:/|$)|/\.hg(?:/|$)|/\.aws/|/\.ssh/"
    r"|id_[rd]sa|/proc/self/|/etc/passwd|\.\./|%2e%2e|docker-compose\.ya?ml|wp-config"
    r"|/\.DS_Store|/\.htpasswd|phpinfo\.php", re.I)


def is_probe_path(path):
    return bool(PROBE_PATH_RE.search(path or ""))


def _valid_ip(ip):
    try:
        ipaddress.ip_address((ip or "").strip("[]"))
        return True
    except ValueError:
        return False


def _is_public_ip(ip):
    try:
        return ipaddress.ip_address((ip or "").strip("[]")).is_global
    except ValueError:
        return False


def classify_ua(ua):
    """UA → (命中的 token 或 None, 桶名)。显式映射优先,再 AI agent 宽匹配;
    未命中 → unclassified。"""
    if ua and ua != "-":
        m = _BOT_TOKEN_RE.search(ua)
        if m:
            tok = _CANON[m.group(0).lower()]
            return tok, _BOT_TIER_OF[tok]
        m = _AGENT_UA_RE.search(ua)
        if m:
            return _CANON[m.group(0).lower()], "agent_visits"
    return None, "unclassified"


# ---- 归因工具箱(B5:GA4 custom channel 正则锚定官方域名) ----
ATTR_REFERRER_DOMAINS = ("chat.openai.com", "chatgpt.com", "perplexity.ai",
                         "gemini.google.com", "copilot.microsoft.com", "claude.ai",
                         "grok.com", "i.meta.ai")
ATTR_SOURCE_REGEX = "|".join(d.replace(".", r"\.") for d in ATTR_REFERRER_DOMAINS)


def _parse_json_line(line):
    """每行一个 JSON 对象(path/uri/url、status/status_code、user_agent/ua、
    referer/referrer 等常见键名,兼容 request 为字符串或对象)。缺 path/status → None。"""
    s = line.strip()
    if not s.startswith("{"):
        return None
    try:
        obj = json.loads(s)
    except ValueError:
        return None
    if not isinstance(obj, dict):
        return None

    def pick(*keys):
        for k in keys:
            v = obj.get(k)
            if v not in (None, ""):
                return v
        return None

    path = pick("path", "uri", "url")
    req = obj.get("request")
    if isinstance(req, dict):
        path = path or req.get("path") or req.get("uri")
    elif isinstance(req, str) and req.strip():
        parts = req.split(" ")
        path = path or (parts[1] if len(parts) >= 2 else parts[0])
    if path is None:
        return None
    path = str(path)
    if "://" in path:                       # 完整 url 形态 → 取 path 部分
        tail = path.split("://", 1)[1]
        path = "/" + tail.split("/", 1)[1] if "/" in tail else "/"
    status = pick("status", "status_code", "response_status")
    if status is None:
        return None
    return {"ip": str(pick("ip", "client_ip", "remote_addr") or "-"),
            "ts": str(pick("time", "ts", "timestamp", "date") or "-"),
            "path": path, "status": str(status),
            "referer": str(pick("referer", "referrer", "http_referer") or "-"),
            "ua": str(pick("user_agent", "ua", "agent", "http_user_agent") or "-")}


def parse_line(line):
    line = (line or "").strip()
    if line.startswith("{"):
        rec = _parse_json_line(line)
        if rec:
            return rec
    m = LOG_RE.match(line)
    if not m:
        return None
    ip, ts, request, status, _bytes, referer, ua = m.groups()
    real = CLIENT_IP_FIELD_RE.search(line[m.end():])
    if real and _valid_ip(real.group(1)):
        ip = real.group(1).strip("[]")
    parts = (request or "").split(" ")
    path = parts[1] if len(parts) >= 2 else (parts[0] if parts else "-")
    return {"ip": ip, "ts": ts, "path": path, "status": status,
            "referer": referer or "-", "ua": ua or "-"}


def referrer_host(referer):
    if not referer or referer == "-":
        return ""
    host = referer.strip().lower()
    if "://" in host:
        host = host.split("://", 1)[1]
    return host.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]


def match_ai_domain(host):
    """host 命中 AI 引用域(精确或子域)→ 返回该域,否则 None。"""
    if not host:
        return None
    for d in AI_REFERRER_DOMAINS:
        if host == d or host.endswith("." + d):
            return d
    return None


# ---- R6 referral 桥:面板导入导出(--as-panel-import) ----
_CLF_TS_RE = re.compile(r"(\d{1,2})/([A-Za-z]{3})/(\d{4})")
_ISO_TS_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def log_date_of(ts):
    """日志 ts 串 → YYYY-MM-DD。支持 CLF(09/Oct/2026:10:00:00 +0800)与
    ISO(2026-10-09T12:06:00Z)两种形态;无法解析 → None。"""
    if not ts:
        return None
    m = _CLF_TS_RE.search(ts)
    if m:
        mon = _MONTHS.get(m.group(2).lower())
        if mon:
            try:
                return "%s-%02d-%02d" % (m.group(3), mon, int(m.group(1)))
            except ValueError:
                return None
    m = _ISO_TS_RE.search(ts)
    if m:
        return "%s-%s-%s" % m.groups()
    return None


def panel_import_payload(res, fallback_date=None):
    """分析结果 → citation_panel 导入 payload(source=referral,下界 real 证据)。
    records 只含命中的 referrer 域;engine 经 DOMAIN_TO_ENGINE 映射;
    sessions=该域请求命中数(未做会话化的下界);cited_urls=该域目标路径聚合
    (按命中数降序、同数按字典序)。date=日志内可解析的最新日期(证据自带),
    无可解析日期时用 fallback_date/今天。诚实口径进 scope 字段——与 prompt
    采样(est)分轨,由 citation_panel record --from-referral 消费。"""
    dates = sorted(res.get("log_dates") or ())
    date = dates[-1] if dates else (fallback_date
                                    or datetime.now().strftime("%Y-%m-%d"))
    records = []
    for dom in AI_REFERRER_DOMAINS:
        s = res["stats"][dom]
        if not s["hits"]:
            continue
        urls = [p for p, _c in sorted(s["paths"].items(),
                                      key=lambda kv: (-kv[1], kv[0]))]
        records.append({"date": date, "engine": DOMAIN_TO_ENGINE[dom],
                        "sessions": s["hits"], "cited_urls": urls})
    return {"tool": "ai_referral_log", "source": "referral",
            "scope": PANEL_IMPORT_SCOPE, "date": date, "records": records}


def analyze(lines, with_bots=False):
    stats = {d: {"hits": 0, "paths": Counter()} for d in AI_REFERRER_DOMAINS}
    all_paths = Counter()
    total = parsed = no_ref = 0
    # 显式名单全集(含旧 6 个,旧 --bot-ua 视图键恒在,向后兼容)
    bots = {b: {"hits": 0, "ips": set(), "first": None, "last": None}
            for bs in BOT_TIERS.values() for b in bs}
    tiers = {t: {"hits": 0, "fail": 0, "paths": Counter()} for t in TIER_ORDER}
    bot_rows = {}                      # token → 桶级行(hits/fail/statuses 矩阵)
    llms = {"hits": 0, "bot_hits": 0}  # /llms.txt 请求(总/AI bot)
    ai_bot_total = 0
    probes = {"total": 0, "bot": 0, "paths": Counter()}   # 剔除的漏洞扫描探测请求
    bot_ips = set()                      # AI bot UA 请求的客户端 IP(判断能否验证 UA)
    log_dates = set()                    # R6: 可解析的日志日期(面板导入 date 用)
    for line in lines:
        line = (line or "").rstrip("\n")
        if not line.strip():
            continue
        total += 1
        rec = parse_line(line)
        if rec is None:
            continue
        parsed += 1
        d = log_date_of(rec["ts"])
        if d:
            log_dates.add(d)
        all_paths[rec["path"]] += 1
        host = referrer_host(rec["referer"])
        if not host:
            no_ref += 1
        dom = match_ai_domain(host)
        if dom:
            stats[dom]["hits"] += 1
            stats[dom]["paths"][rec["path"]] += 1
        token, tier = classify_ua(rec["ua"])
        code = rec["status"]
        is_fail = code[:1] in ("4", "5")
        if is_probe_path(rec["path"]):     # 扫描器探测:不进 bot 桶、不进失败率
            probes["total"] += 1
            probes["paths"][rec["path"]] += 1
            if tier != "unclassified":
                probes["bot"] += 1
            continue
        if tier != "unclassified":
            bot_ips.add(rec["ip"])
        tiers[tier]["hits"] += 1
        tiers[tier]["paths"][rec["path"]] += 1
        if is_fail:
            tiers[tier]["fail"] += 1
        if tier != "unclassified":
            ai_bot_total += 1
            row = bot_rows.setdefault(
                token, {"tier": tier, "hits": 0, "fail": 0, "ips": set(),
                        "first": None, "last": None, "statuses": Counter()})
            row["hits"] += 1
            row["statuses"][code] += 1
            row["ips"].add(rec["ip"])
            row["first"] = row["first"] or rec["ts"]
            row["last"] = rec["ts"]
            if is_fail:
                row["fail"] += 1
            if with_bots and token in bots:   # 旧 --bot-ua 视图数据
                bots[token]["hits"] += 1
                bots[token]["ips"].add(rec["ip"])
                bots[token]["first"] = bots[token]["first"] or rec["ts"]
                bots[token]["last"] = rec["ts"]
        if rec["path"].split("?", 1)[0] == "/llms.txt":
            llms["hits"] += 1
            if tier != "unclassified":
                llms["bot_hits"] += 1
    return {"total": total, "parsed": parsed, "no_ref": no_ref,
            "stats": stats, "all_paths": all_paths, "bots": bots,
            "ai_total": sum(s["hits"] for s in stats.values()),
            "tiers": tiers, "bot_rows": bot_rows, "llms": llms,
            "ai_bot_total": ai_bot_total, "log_dates": log_dates,
            "probes": probes, "bot_ips": bot_ips,
            "site_avg_per_page": (parsed / len(all_paths)) if all_paths else 0.0}


def _rate(fail, hits):
    return (100.0 * fail / hits) if hits else 0.0


def render_classify(res, top=3):
    """四桶 + failure_rate 两级 + 每桶 Top URL + bot×status 矩阵。"""
    L = ["-- bot 四桶(Profound/Otterly/Peec 三家口径合并) --"]
    for t in TIER_ORDER:
        s = res["tiers"][t]
        tops = " ".join("%s(%d)" % (p, c) for p, c in s["paths"].most_common(top))
        L.append("  %-18s hits=%-6d fail(4xx+5xx)=%-5d failure=%5.1f%%  top: %s"
                 % (t, s["hits"], s["fail"], _rate(s["fail"], s["hits"]),
                    tops or "-"))
    L.append("-- 按 bot 的 failure rate(4xx+5xx 占比) --")
    rows = sorted(res["bot_rows"].items(), key=lambda kv: (-kv[1]["hits"], kv[0]))
    for token, row in rows:
        L.append("  %-22s [%s] hits=%-6d fail=%-5d failure=%5.1f%%%s"
                 % (token, row["tier"], row["hits"], row["fail"],
                    _rate(row["fail"], row["hits"]),
                    "  (未核:官方 bot 页无此 token)" if token in UNVERIFIED_UA_TOKENS else ""))
    if not rows:
        L.append("  [i] 未检出已知 AI bot UA(全部请求计入 unclassified)")
    L.append("-- bot×status 矩阵 --")
    if rows:
        codes = sorted({c for r in res["bot_rows"].values() for c in r["statuses"]})
        L.append("  %-22s %s  %5s"
                 % ("bot", "  ".join("%5s" % c for c in codes), "total"))
        for token, row in rows:
            L.append("  %-22s %s  %5d"
                     % (token,
                        "  ".join("%5d" % row["statuses"].get(c, 0) for c in codes),
                        row["hits"]))
    else:
        L.append("  [i] 无 AI bot 请求,矩阵为空")
    return L


def render_llms_baseline(res):
    """llms.txt 双基线(Otterly 90 天实验口径);无 /llms.txt 请求时不输出。"""
    if not res["llms"]["hits"]:
        return []
    pct = (100.0 * res["llms"]["bot_hits"] / res["ai_bot_total"]) \
        if res["ai_bot_total"] else 0.0
    return [
        "-- llms.txt 双基线(Otterly 90 天实验口径) --",
        "  /llms.txt 请求 %d(其中 AI bot %d;AI bot 请求合计 %d)"
        % (res["llms"]["hits"], res["llms"]["bot_hits"], res["ai_bot_total"]),
        "  基线 1: 占总 AI bot 请求 %.2f%%(实测参考值 0.1%%)" % pct,
        "  基线 2: llms.txt %d 次 vs 站均页面访问 %.1f 次/页(参考值: 84 vs 265)"
        % (res["llms"]["hits"], res["site_avg_per_page"]),
        "  结论: llms.txt 是编程 agent 基础设施非可见性杠杆",
    ]


def render_policy(res):
    """retrieval vs training 分层结论:封 training=授权决策([i] 只提示);
    封 on_demand/search=可见性失败([!] WARN);显式分开。"""
    t_tr = res["tiers"]["training"]
    ret_hits = (res["tiers"]["on_demand_fetcher"]["hits"]
                + res["tiers"]["search_index"]["hits"])
    ret_fail = (res["tiers"]["on_demand_fetcher"]["fail"]
                + res["tiers"]["search_index"]["fail"])
    L = ["-- retrieval vs training: 封禁立场分层(显式分开) --",
         "  [i] training 桶(" + "/".join(BOT_TIERS["training"]) + "): 封=授权决策,只提示不告警"
         "(当前 failure rate %.1f%%)" % _rate(t_tr["fail"], t_tr["hits"]),
         "  [!] on_demand_fetcher + search_index 桶(AI 答案/引用直接取材源): "
         "封=可见性失败 WARN",
         "  [i] 封 GPTBot ≠ 封 ChatGPT 引用——引用走 OAI-SearchBot"]
    pr = res.get("probes") or {"total": 0, "bot": 0, "paths": Counter()}
    if pr["total"]:
        L.append("  [i] 已剔除漏洞扫描探测请求 %d 条(其中冒充 AI bot UA %d 条;如 %s)——"
                 "不计入失败率" % (pr["total"], pr["bot"],
                                  ", ".join(p for p, _ in pr["paths"].most_common(3))))
    if ret_fail:
        L.append("  [!] WARN 实测: retrieval 层(on_demand+search)failure rate "
                 "%.1f%%(%d/%d,已剔除探测路径)——UA 未验证:先确认这些请求来自真 bot,"
                 "再排查 WAF/robots 是否误拦" % (_rate(ret_fail, ret_hits), ret_fail, ret_hits))
    else:
        L.append("  [i] retrieval 层 bot 当前干净(剔除探测路径后未观测到 4xx/5xx)")
    ips = res.get("bot_ips") or set()
    public = sorted(ip for ip in ips if _is_public_ip(ip))
    if public:
        L.append("  [i] UA 未验证:日志含 %d 个公网客户端 IP——按各家公布的官方 IP 段"
                 "(如 OpenAI 的 gptbot.json/searchbot.json/chatgpt-user.json)或反向 DNS 核实后再下结论"
                 % len(public))
    elif ips:
        L.append("  [i] UA 未验证且无法验证:bot 请求的 IP 只有 %s(环回/内网/缺失)——"
                 "源站在 CDN/隧道后时让边缘回传真实客户端 IP(如 CF-Connecting-IP),记在行尾 cip= 字段再核"
                 % ", ".join(sorted(ips)[:3]))
    L.append("  [i] 源站在 CDN 后时,边缘缓存命中的请求不进源站日志——bot 量以 CDN 的 bot 分析为准")
    return L


def render_attribution():
    """归因工具箱:GA4 custom channel 正则 + 三条纪律注记 + 自报归因问卷两问。"""
    return [
        "-- AI 归因工具箱(GA4 custom channel,可直接粘贴) --",
        "  规则 1 referrer 匹配正则:",
        "    " + ATTR_SOURCE_REGEX,
        "  规则 2 source 匹配正则(utm_source 同名匹配,同域名单):",
        "    " + ATTR_SOURCE_REGEX,
        "  [纪律] AIO 点击 referrer=google.com 无法与自然结果区分,"
        "用 Search Console 看侧影(AIO 曝光/点击)",
        "  [纪律] 一切 AI referrer 数字当下限(App 内打开常不带 referrer)",
        "  [纪律] 不要给入站 AI 链接发明 UTM(只认真实 utm/自报数据)",
        "  [自报归因问卷] 首选补充,放注册/结账表单:",
        "    Q1 从哪听说我们?(选项: ChatGPT/Claude/Perplexity/Gemini/Copilot/"
        "Grok/搜索引擎/口碑推荐/其他)",
        "    Q2 你问了 AI 什么?(自由文本,记录用户原 prompt)",
    ]


def render(res, top=20, with_bots=False, classify=False):
    L = ["== AI 引用流量日志分析 =="]
    L.append("日志行 %d | 可解析 %d | 无 referrer %d"
             % (res["total"], res["parsed"], res["no_ref"]))
    L.append("-- AI referrer 域(请求数 / 独立路径数)--")
    any_hit = False
    for d in AI_REFERRER_DOMAINS:
        s = res["stats"][d]
        if s["hits"]:
            any_hit = True
        L.append("  %-26.26s %6d  %6d" % (d, s["hits"], len(s["paths"])))
    L.append("  合计 AI referrer 请求: %d" % res["ai_total"])
    L.append("-- 热门路径 top%d(全站,含非 AI)--" % top)
    for path, cnt in res["all_paths"].most_common(top):
        L.append("  %-50.50s %d" % (path, cnt))
    if not any_hit:
        L.append("  [i] 未检出任何 AI referrer 命中")
    L.append("[!] App 内打开常不带 referrer——测得的是下界;"
             "AI 实际引流 >= 此处数字")
    if with_bots:
        L.append("-- AI 爬虫到访(先行指标:先爬后引) --")
        any_bot = False
        for b in BOT_UAS:
            s = res["bots"][b]
            if s["hits"]:
                any_bot = True
                L.append("  %-18.18s hits=%-5d ip=%-4d first=%s last=%s"
                         % (b, s["hits"], len(s["ips"]),
                            (s["first"] or "")[:11], (s["last"] or "")[:11]))
        if not any_bot:
            L.append("  [i] 未检出已知 AI 爬虫 UA")
        L.append("  [i] 爬虫到访 ≠ 已被引用;引用看 referrer,到访看 UA")
    if classify:
        L.extend(render_classify(res))
        L.extend(render_llms_baseline(res))
        L.extend(render_policy(res))
    return "\n".join(L)


SAMPLE_LOG = "\n".join([
    '1.2.3.4 - - [09/Oct/2026:10:00:00 +0800] "GET /pricing HTTP/1.1" 200 512 "https://chatgpt.com/" "Mozilla/5.0"',
    '5.6.7.8 - - [09/Oct/2026:10:05:00 +0800] "GET /blog/geo HTTP/1.1" 200 1024 "https://www.perplexity.ai/search?q=crm" "Mozilla/5.0"',
    '9.9.9.9 - - [09/Oct/2026:10:06:00 +0800] "GET /pricing HTTP/1.1" 200 256 "https://gemini.google.com/app" "Mozilla/5.0"',
    '1.2.3.4 - - [09/Oct/2026:10:07:00 +0800] "GET / HTTP/1.1" 200 128 "https://claude.ai/chat/abc" "Mozilla/5.0"',
    '2.2.2.2 - - [09/Oct/2026:10:08:00 +0800] "GET /x HTTP/1.1" 200 64 "-" "Mozilla/5.0"',
    '3.3.3.3 - - [09/Oct/2026:11:00:00 +0800] "GET /api/data HTTP/1.1" 200 32 "-" "Mozilla/5.0 (compatible; GPTBot/1.0; +https://openai.com/gptbot)"',
    '4.4.4.4 - - [09/Oct/2026:11:01:00 +0800] "GET /api/data HTTP/1.1" 200 32 "-" "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexity-bot)"',
    'garbage line that does not parse',
])

TIER_SAMPLE = "\n".join([
    '1.1.1.1 - - [09/Oct/2026:12:00:00 +0800] "GET /a HTTP/1.1" 200 64 "-" "Mozilla/5.0 (compatible; GPTBot/1.0)"',
    '1.1.1.1 - - [09/Oct/2026:12:01:00 +0800] "GET /a HTTP/1.1" 404 64 "-" "Mozilla/5.0 (compatible; GPTBot/1.0)"',
    '2.2.2.2 - - [09/Oct/2026:12:02:00 +0800] "GET /b HTTP/1.1" 403 64 "-" "Mozilla/5.0 ChatGPT-User/1.0"',
    '3.3.3.3 - - [09/Oct/2026:12:03:00 +0800] "GET /c HTTP/1.1" 200 64 "-" "Mozilla/5.0 (compatible; Meta-ExternalAgent/1.0)"',
    '4.4.4.4 - - [09/Oct/2026:12:04:00 +0800] "GET /d HTTP/1.1" 200 64 "-" "Mozilla/5.0"',
    '5.5.5.5 - - [09/Oct/2026:12:05:00 +0800] "GET /llms.txt HTTP/1.1" 200 64 "-" "Mozilla/5.0 PerplexityBot/1.0"',
    '{"path": "/j", "status": 200, "user_agent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)", "referer": "-", "ip": "6.6.6.6", "time": "2026-10-09T12:06:00Z"}',
])


def _self_test():
    lines = SAMPLE_LOG.splitlines()
    res = analyze(lines, with_bots=True)
    assert res["total"] == 8 and res["parsed"] == 7      # 1 行垃圾
    assert res["stats"]["chatgpt.com"]["hits"] == 1
    assert res["stats"]["perplexity.ai"]["hits"] == 1    # www 子域命中
    assert res["stats"]["gemini.google.com"]["hits"] == 1
    assert res["stats"]["claude.ai"]["hits"] == 1
    assert res["stats"]["copilot.microsoft.com"]["hits"] == 0
    assert res["stats"]["grok.com"]["hits"] == 0
    assert res["ai_total"] == 4
    assert res["no_ref"] == 3
    assert res["all_paths"]["/pricing"] == 2 and res["all_paths"]["/api/data"] == 2
    assert res["stats"]["perplexity.ai"]["paths"]["/blog/geo"] == 1
    assert res["bots"]["GPTBot"]["hits"] == 1 and res["bots"]["PerplexityBot"]["hits"] == 1
    assert len(res["bots"]["GPTBot"]["ips"]) == 1
    assert res["bots"]["GPTBot"]["last"].startswith("09/Oct/2026:11:00")
    # referrer 提取
    assert referrer_host("https://www.perplexity.ai/search?q=crm") == "www.perplexity.ai"
    assert referrer_host("-") == "" and referrer_host("") == ""
    assert match_ai_domain("www.perplexity.ai") == "perplexity.ai"
    assert match_ai_domain("perplexity.ai") == "perplexity.ai"
    assert match_ai_domain("evil-perplexity.ai.example.com") is None
    assert match_ai_domain("notai.com") is None
    out = render(res, top=20, with_bots=True)
    assert "下界" in out and "GPTBot" in out and "chatgpt.com" in out
    assert "未检出" not in out.split("AI 爬虫到访")[1].split("[i]")[0]
    # B5 扩展: 四桶(含未知)/failure_rate 两级/llms.txt 双基线/归因工具箱/JSON 行
    res2 = analyze(TIER_SAMPLE.splitlines())
    t2 = res2["tiers"]
    assert t2["training"]["hits"] == 3 and t2["training"]["fail"] == 1  # GPTBot×2+ClaudeBot(JSON)
    assert t2["on_demand_fetcher"]["hits"] == 1 and t2["on_demand_fetcher"]["fail"] == 1
    assert t2["search_index"]["hits"] == 1                              # PerplexityBot
    assert t2["agent_visits"]["hits"] == 1                              # Meta-ExternalAgent
    assert t2["unclassified"]["hits"] == 1
    assert res2["ai_bot_total"] == 6 and res2["llms"] == {"hits": 1, "bot_hits": 1}
    assert res2["bot_rows"]["GPTBot"]["statuses"] == {"200": 1, "404": 1}
    assert classify_ua("x ChatGPT-User/1.0") == ("ChatGPT-User", "on_demand_fetcher")
    assert classify_ua("x GrokBot/1.0") == ("GrokBot", "agent_visits")   # 官方页无此 token → 未核
    assert classify_ua("x Meta-ExternalFetcher/1.0") == ("Meta-ExternalFetcher", "on_demand_fetcher")
    assert classify_ua("x Meta-ExternalAgent/1.0") == ("Meta-ExternalAgent", "agent_visits")
    assert classify_ua("Mozilla/5.0") == (None, "unclassified")
    assert classify_ua("-") == (None, "unclassified")
    out2 = render(res2, classify=True)
    for frag in ("bot 四桶", "50.0%", "33.3%", "bot×status 矩阵", "84 vs 265",
                 "0.1%", "llms.txt 是编程 agent 基础设施非可见性杠杆",
                 "授权决策", "可见性失败", "WARN 实测", "UA 未验证", "CDN"):
        assert frag in out2, frag
    att = "\n".join(render_attribution())
    assert "chat\\.openai\\.com" in att and "i\\.meta\\.ai" in att
    assert "utm_source" in att and "从哪听说我们" in att and "你问了 AI 什么" in att
    rec_j = parse_line('{"path":"/j","status":404,"user_agent":"x","referer":"-"}')
    assert rec_j and rec_j["path"] == "/j" and rec_j["status"] == "404"
    # R6 referral 桥(Ryze 一方数据线对齐): 面板导入导出(下界 real,与采样 est 分轨)
    imp = panel_import_payload(res)
    assert imp["source"] == "referral" and imp["tool"] == "ai_referral_log"
    assert imp["date"] == "2026-10-09"                    # 从日志 ts 推导(CLF)
    assert "下界" in imp["scope"] and "(real)" in imp["scope"] and "est" in imp["scope"]
    got = {r["engine"]: (r["sessions"], r["cited_urls"]) for r in imp["records"]}
    assert got == {"chatgpt": (1, ["/pricing"]), "perplexity": (1, ["/blog/geo"]),
                   "gemini": (1, ["/pricing"]), "claude": (1, ["/"])}, got
    assert set(DOMAIN_TO_ENGINE) == set(AI_REFERRER_DOMAINS)
    assert set(DOMAIN_TO_ENGINE.values()) == {"chatgpt", "perplexity", "gemini",
                                              "copilot", "claude", "grok"}
    assert DOMAIN_TO_ENGINE[match_ai_domain("www.grok.com")] == "grok"
    assert log_date_of("09/Oct/2026:10:00:00 +0800") == "2026-10-09"
    assert log_date_of("2026-10-09T12:06:00Z") == "2026-10-09"
    assert log_date_of("-") is None and log_date_of("garbage") is None \
        and log_date_of("") is None
    empty = panel_import_payload({"stats": {d: {"hits": 0, "paths": Counter()}
                                            for d in AI_REFERRER_DOMAINS},
                                  "log_dates": set()})
    assert empty["records"] == [] and empty["source"] == "referral"  # 零命中也诚实导出
    assert PANEL_IMPORT_MARKER.startswith("-- referral panel import")
    print("[self-test] PASS ai_referral_log(7 行解析,4 域命中,无 referrer=3,"
          "bot UA 先行指标,子域匹配,anti 误匹配;"
          "B5: 四桶分类/failure 两级/llms.txt 双基线/归因工具箱/JSON 行;"
          "R6: --as-panel-import 导出(域→引擎/下界口径/date 推导))")


def read_lines(args_input):
    if args_input and args_input != "-":
        with open(args_input, encoding="utf-8", errors="replace") as f:
            return f.readlines()
    return sys.stdin.readlines()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?", default=None,
                    help="日志文件(缺省读 stdin)")
    ap.add_argument("--top", type=int, default=20, help="热门路径 top N(默认 20)")
    ap.add_argument("--bot-ua", dest="bot_ua", action="store_true",
                    help="同时统计 AI 爬虫 UA 到访(先行指标)")
    ap.add_argument("--classify", dest="classify", action="store_true",
                    help="bot 四桶分类 + failure rate(按 bot/按桶)+ 每桶 Top URL + "
                         "bot×status 矩阵 + llms.txt 双基线 + retrieval/training 分层结论")
    ap.add_argument("--attribution", dest="attribution", action="store_true",
                    help="输出 AI 归因工具箱(GA4 custom channel 正则 + 纪律注记 + "
                         "自报归因问卷;无日志也可单独使用)")
    ap.add_argument("--as-panel-import", dest="as_panel_import", action="store_true",
                    help="分析输出之外追加 citation_panel 导入 JSON(source=referral,"
                         "下界 real 证据,与 prompt 采样 est 分轨;referrer 域→引擎映射,"
                         "sessions=请求命中数,cited_urls=目标路径聚合;由 "
                         "citation_panel record --from-referral 消费)")
    ap.add_argument("--self-test", action="store_true", help="冒烟自测(不联网)")
    args = ap.parse_args(argv)
    if args.self_test:
        try:
            _self_test()
            return 0
        except Exception:
            traceback.print_exc()
            print("[self-test] FAIL ai_referral_log")
            return 1
    if args.input is None and sys.stdin.isatty():
        if args.attribution:              # 工具箱可独立使用,无需日志
            print("\n".join(render_attribution()))
            return 0
        ap.error("需要日志文件参数,或通过管道传入(如 cat access.log | %s)"
                 % sys.argv[0])
    res = analyze(read_lines(args.input), with_bots=args.bot_ua)
    out = render(res, top=args.top, with_bots=args.bot_ua, classify=args.classify)
    if args.attribution:
        out += "\n" + "\n".join(render_attribution())
    print(out)
    if args.as_panel_import:
        # R6 referral 桥: marker 行之后是纯 JSON——整文件重定向后
        # `citation_panel record --from-referral file.json` 按 marker 定位切取
        print(PANEL_IMPORT_MARKER)
        print(json.dumps(panel_import_payload(res), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
