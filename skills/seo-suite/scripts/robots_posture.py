#!/usr/bin/env python3
"""robots.txt AI 爬虫姿势分析器(stdlib)。读取 robots.txt,按 RFC 9309(连续 UA 合并/
最长匹配/Allow 平局胜出)对 37 个 AI bot 四层名单(training/search/user/other)做四态判定
(allowed/blocked/partial/missing),检测 Cloudflare 注入块,输出两级引用评分
(citation_bots_ok / citation_bots_explicit)、分层统计、Content-Signal 建议与警告,
可选 --fix-robots 打印修复建议块(只打印不写盘)。判定算法沿用 geo-optimizer 源码口径(borrow-specs C3);
名单与分层以 references/technical/ai-crawler-policy.md 和各家官方页为准。
用法: python3 robots_posture.py https://example.com/robots.txt [--signal visibility|protect-ip] [--json] [--fix-robots]"""
import ipaddress, json, os, re, socket, sys, urllib.parse, urllib.request

UA = "Mozilla/5.0 (compatible; seo-suite-audit/1.0)"
MAX_BYTES = 500_000  # RFC 9309: 超过 500KiB 的 robots.txt 至少按前 500KiB 处理

# ---------------------------------------------------------------------------
# 37 bot 四层名单(模块级常量)。分类以 references/technical/ai-crawler-policy.md 第一节表格
# 与第七节「已知偏差」及其链接的各家官方页为准(2026-10-21 按第七节改,B42/B46):
#   training: 基础模型训练——封禁是授权决策,不影响搜索/AI 答案可见性
#   search:   搜索/答案索引——决定 AI 引用,封禁=逐出 AI 答案
#   user:     按用户请求抓取(对话里用户点名某个 URL 时去取)——封禁=用户实测不可达
#   other:    站长委托 / 广告审核 / 官方称目前不训练——不影响搜索可见性,也不是训练授权
# verified=False:运营方没有可读的官方 bot 文档,只有第三方目录(第七节),结论仅供参考。
# 修前(27 bot,geo-optimizer 口径)的偏差:Amazonbot 记搜索(官方训练/产品)、PetalBot 记训练
# (官方搜索)、Google-CloudVertexBot 记训练(官方站长委托)、cohere-ai 记训练(Cohere 官方:目前
# 不用 bot 训练基础模型);缺 Baiduspider、Amzn-SearchBot、Amzn-User、MistralAI-*、
# meta-webindexer、Google-Agent、OAI-AdsBot、YandexAdditional。
# ---------------------------------------------------------------------------
def _bot(token, desc, tier, verified=True):
    return {"token": token, "desc": desc, "tier": tier, "verified": verified}


AI_BOTS = [
    # --- training(11) ---
    _bot("GPTBot",               "OpenAI GPT 模型训练(禁它不影响 ChatGPT 引用,引用走 OAI-SearchBot)", "training"),
    _bot("ClaudeBot",            "Anthropic Claude 模型训练(引用走 Claude-SearchBot)",                "training"),
    _bot("Google-Extended",      "Google 控制 token:Gemini 训练与 grounding(不是 AI Overviews 开关;不单独抓取)", "training"),
    _bot("Applebot-Extended",    "Apple 控制 token:Applebot 数据能否用于训练(不抓取)",                 "training"),
    _bot("Bytespider",           "字节跳动(无官方页;第三方称训练与搜索)",                              "training", False),
    _bot("meta-externalagent",   "Meta 训练基础模型或直接索引改进产品",                                 "training"),
    _bot("Amazonbot",            "Amazon 改进产品与服务,可能用于训练 AI 模型(搜索走 Amzn-SearchBot)",   "training"),
    _bot("AI2Bot",               "Allen AI 训练开放语言模型",                                           "training"),
    _bot("AI2Bot-Dolma",         "Allen AI Dolma 数据集(无官方 bot 文档)",                              "training", False),
    _bot("CCBot",                "Common Crawl 公开语料(第三方研究称是生成式 AI 主要训练源)",           "training"),
    _bot("MistralAI-Training",   "Mistral 训练数据集抓取",                                              "training"),
    # --- search(15,决定 AI 引用) ---
    _bot("OAI-SearchBot",        "OpenAI ChatGPT 搜索索引(AI 引用入口)",                                "search"),
    _bot("Claude-SearchBot",     "Anthropic Claude 搜索索引(AI 引用入口)",                              "search"),
    _bot("PerplexityBot",        "Perplexity 搜索/引用(不训练)",                                         "search"),
    _bot("Googlebot",            "Google 通用收录+AI Overviews",                                        "search"),
    _bot("Applebot",             "Apple Siri/Spotlight 收录",                                           "search"),
    _bot("Bingbot",              "Bing 收录(喂 Copilot,无独立 Copilot bot)",                            "search"),
    _bot("DuckAssistBot",        "DuckDuckGo AI 辅助答案实时抓取(不训练)",                              "search"),
    _bot("YouBot",               "You.com 搜索/AI 答案(无可读官方 bot 文档)",                           "search", False),
    _bot("xAI-Bot",              "xAI Grok 检索索引(官方无爬虫文档)",                                   "search", False),
    _bot("Amzn-SearchBot",       "Amazon Alexa 等搜索体验(不训练)",                                     "search"),
    _bot("PetalBot",             "华为 Petal 搜索索引及 Huawei Assistant、AI Search",                   "search"),
    _bot("Baiduspider",          "百度搜索(中文站主引擎;验证靠双向 DNS *.baidu.com/.jp)",              "search"),
    _bot("MistralAI-Index",      "Mistral 搜索索引(不训练)",                                            "search"),
    _bot("meta-webindexer",      "Meta AI 搜索质量与引用链接",                                          "search"),
    _bot("YandexAdditional",     "Yandex 控制 token:能否进 Search with Yandex AI 回答(不认 * 组,必须点名)", "search"),
    # --- user(8,按用户请求抓取) ---
    _bot("ChatGPT-User",         "OpenAI 按用户请求抓取(ChatGPT;厂商声明可能无视 robots)",              "user"),
    _bot("Claude-User",          "Anthropic 按用户请求抓取(Claude)",                                     "user"),
    _bot("Perplexity-User",      "Perplexity 按用户请求抓取",                                            "user"),
    _bot("Meta-ExternalFetcher", "Meta AI 按用户请求抓取",                                               "user"),
    _bot("facebookexternalhit",  "Meta 链接预览抓取",                                                    "user"),
    _bot("Amzn-User",            "Amazon 按用户请求实时取信息(如 Alexa)",                               "user"),
    _bot("MistralAI-User",       "Mistral Vibe 按用户请求访问页面",                                      "user"),
    _bot("Google-Agent",         "Google 基础设施上的 agent 按用户请求浏览/操作",                        "user"),
    # --- other(3,不影响搜索可见性,也不是训练) ---
    _bot("Google-CloudVertexBot","Google 站长委托的 Vertex AI Agents 抓取(不影响 Google 搜索)",          "other"),
    _bot("cohere-ai",            "Cohere(官方:目前不用 bot 训练生成式基础模型;官方表格未列此 token)",  "other", False),
    _bot("OAI-AdsBot",           "OpenAI 只审核提交为 ChatGPT 广告的落地页(不用于训练)",               "other"),
]

# 只认点名规则、不认 `User-agent: *` 的 token(Yandex 官方机器人页:YandexAdditional 对通用规则
# 填 No)。没有专属组时不受 * 组约束,按 allowed 处理,不因 * 组的 Disallow 判 blocked。
WILDCARD_IGNORED = {"yandexadditional"}

# 引用型 5 bot(刻意排除纯训练的 ClaudeBot:禁 ClaudeBot 不阻止 Claude 引用,引用走 Claude-SearchBot)
CITATION_BOTS = ["OAI-SearchBot", "Claude-SearchBot", "PerplexityBot", "Googlebot", "Applebot"]

TIER_LABELS = {"search": "检索", "user": "按需", "training": "训练", "other": "其他"}
TIER_ORDER = ("search", "user", "training", "other")  # 展示顺序:先可见性攸关层,后授权决策层
SIGNALS = {"visibility": "search=yes, ai-input=yes, ai-train=yes",
           "protect-ip": "search=yes, ai-input=yes, ai-train=no"}


# ---------------------------------------------------------------------------
# SSRF 防护(trend_watch.py 同款,内嵌不 import):仅 http(s)+私网/环回/链路本地/
# 保留段拒连+重定向逐跳复查
# ---------------------------------------------------------------------------
class FetchError(Exception):
    pass


_ssrf_cache = {}


def ssrf_guard(host):
    """仅 http(s) + 拒私网/环回/链路本地/保留段;结果按 host 缓存。
    198.18.0.0/15(RFC2544 基准段)豁免:本机 fake-IP 代理会把一切域名解析到该段,
    实际连接经代理出网,TLS 验证仍生效;SEO_MONITOR_STRICT_SSRF=1 恢复全拒。"""
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
    """重定向逐跳 SSRF 复查(urlopen 自动跟 302,每一跳的新 host 必须复查)。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        p = urllib.parse.urlparse(newurl)
        if p.scheme not in ("http", "https"):
            raise FetchError("重定向到非 http(s) 被拒: %s" % newurl)
        ssrf_guard(p.hostname)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_RedirectGuard)


def fetch(url):
    """唯一网络出口(测试打桩点):scheme 检查(仅 http(s),拒 file:// 等)+ SSRF 防护。"""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https"):
        raise FetchError("仅允许 http(s): %s" % url)
    ssrf_guard(p.hostname)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with _opener.open(req, timeout=15) as r:
        return r.read(MAX_BYTES).decode("utf-8", "replace")

# ---------------------------------------------------------------------------
# 旧版简单解析器(冻结契约:tests/run_tests.py 直接消费,勿改行为)
# ---------------------------------------------------------------------------
def parse_groups(txt):
    groups, cur, order = {}, "*", []
    for line in txt.splitlines():
        s = line.split("#")[0].strip()
        if not s: continue
        k, _, v = s.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            cur = v or "*"
            groups.setdefault(cur, {"allow": [], "disallow": []}); order.append(cur)
        elif k in ("allow", "disallow") and cur:
            groups[cur][k].append(v)
    return groups, order

# ---------------------------------------------------------------------------
# RFC 9309 解析强化:BOM 剥离 / 500KB 截断 / 连续 User-agent 行合并成规则组 /
# 提取 crawl-delay(取 * 组)与 Sitemap 指令
# ---------------------------------------------------------------------------
def parse_robots(txt):
    """返回 {groups, sitemaps, crawl_delay, truncated}。
    groups 键为小写 token(token 匹配大小写不敏感),值为
    {"token": 原样名, "allow": [path], "disallow": [path], "crawl_delay": float|None}。"""
    if txt.startswith("\ufeff"):          # BOM 剥离
        txt = txt[1:]
    truncated = len(txt) > MAX_BYTES  # 500KB 截断守卫
    if truncated:
        txt = txt[:MAX_BYTES]
    groups, sitemaps = {}, []
    cur, last_was_ua = [], False      # 连续 UA 行共享后续规则;规则行之后的新 UA 开新组
    for line in txt.splitlines():
        s = line.split("#", 1)[0].strip()
        if not s: continue
        k, _, v = s.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if not last_was_ua:
                cur = []
            tok = v or "*"
            cur.append(tok)
            groups.setdefault(tok.lower(), {"token": tok, "allow": [], "disallow": [], "crawl_delay": None})
            last_was_ua = True
        elif k in ("allow", "disallow") and cur:
            for t in cur:
                groups.setdefault(t.lower(), {"token": t, "allow": [], "disallow": [], "crawl_delay": None})[k].append(v)
            last_was_ua = False
        elif k == "crawl-delay" and cur:
            for t in cur:
                g = groups.setdefault(t.lower(), {"token": t, "allow": [], "disallow": [], "crawl_delay": None})
                if g["crawl_delay"] is None:
                    try: g["crawl_delay"] = float(v)
                    except ValueError: pass
            last_was_ua = False
        elif k == "sitemap" and v:
            sitemaps.append(v)
            last_was_ua = False
        elif k:
            last_was_ua = False
    return {"groups": groups, "sitemaps": sitemaps,
            "crawl_delay": groups.get("*", {}).get("crawl_delay"), "truncated": truncated}

_ROBOTS_SAFE = "/?=&*$%:@!'()+,;-._~"


def rule_matches(rule, path):
    """RFC 9309 §2.2.2 匹配:空值匹配一切;`*` 匹配任意字符序列,结尾 `$` 锚定路径结尾;
    区分大小写;规则和路径都先做百分号编码(非 ASCII 字符按 UTF-8 转码),两边口径一致。"""
    if rule == "":
        return True
    rule = urllib.parse.quote(rule, safe=_ROBOTS_SAFE)
    path = urllib.parse.quote(path, safe=_ROBOTS_SAFE)
    anchored = rule.endswith("$")
    body = rule[:-1] if anchored else rule
    rx = "".join(".*" if c == "*" else re.escape(c) for c in body) + ("$" if anchored else "")
    return re.match(rx, path) is not None

def effective_rule(group, path="/"):
    """最长规则匹配;同长时 Allow 平局胜出(RFC 9309 最具体的规则赢,平局归 Allow)。
    无任何匹配规则时默认允许。返回 ("allow"|"disallow", 匹配长度),无匹配为 -1。"""
    best_type, best_len = "allow", -1
    for kind in ("allow", "disallow"):
        for rule in group.get(kind, []):
            if not rule_matches(rule, path): continue
            n = len(rule)
            if n > best_len or (n == best_len and kind == "allow"):
                best_type, best_len = kind, n
    return best_type, best_len

def classify(doc, bot):
    """四态判定(站点根 '/' 口径)+ via_wildcard 标记。
    missing  : 既无专属组也无 * 组(robots 对它只字未提)。RFC 9309 §2.2.1:没有匹配组 = 可以抓,
               所以引用评分把它算作放行,只是拿不到「专属规则」满分
    allowed  : 根路径裁定为允许(专属组或 * 组)
    blocked  : 根路径裁定为禁止且无开洞
    partial  : Disallow: / 但有具体 Allow 路径(>1)开洞——只放行部分路径
    via_wildcard: True=结论来自 * 组而非 bot 专属规则(通配符 Allow 也行,但拿不到全分)。"""
    groups = doc["groups"]
    own = groups.get(bot.lower())
    if own is None and bot.lower() in WILDCARD_IGNORED:
        # 不认 * 组的 token:没有点名规则=没有任何限制(Yandex 官方口径),按放行算
        return {"state": "allowed", "via_wildcard": False}
    star = groups.get("*")
    if own is not None:
        g, via = own, False
    elif star is not None:
        g, via = star, True
    else:
        return {"state": "missing", "via_wildcard": False}
    verdict, _ = effective_rule(g, "/")
    if verdict == "allow":
        state = "allowed"
    elif any(len(a) > 1 for a in g.get("allow", [])):
        state = "partial"
    else:
        state = "blocked"
    return {"state": state, "via_wildcard": via}

def citation_report(doc):
    """两级评分(geo-optimizer 口径):
    ok       = 5 个引用 bot 全部 allowed(含靠 * 通配)→ 部分分
    explicit = 5 个都有专属规则(非仅靠 `*` 通配)且 allowed → 满分
    (通配符 Allow 也行,但拿不到全分)"""
    states = {b: classify(doc, b) for b in CITATION_BOTS}
    visible = ("allowed", "missing")  # missing:没有匹配组,按 RFC 9309 默认放行
    ok = all(s["state"] in visible for s in states.values())
    explicit = all(s["state"] == "allowed" and not s["via_wildcard"] for s in states.values())
    return {"ok": ok, "explicit": explicit,
            "allowed_count": sum(1 for s in states.values() if s["state"] in visible),
            "explicit_count": sum(1 for s in states.values() if s["state"] == "allowed" and not s["via_wildcard"]),
            "bots": states}

def analyze(txt, mode="visibility"):
    """全量分析:37 bot 四态矩阵 + 分层统计 + 两级引用评分 + 指令提取。"""
    doc = parse_robots(txt)
    bots = []
    for item in AI_BOTS:
        c = classify(doc, item["token"])
        bots.append({"token": item["token"], "desc": item["desc"], "tier": item["tier"],
                     "verified": item.get("verified", True),
                     "state": c["state"], "via_wildcard": c["via_wildcard"]})
    buckets = {s: [b["token"] for b in bots if b["state"] == s]
               for s in ("allowed", "blocked", "missing", "partial")}
    tiers = {}
    for tier in ("training", "search", "user", "other"):
        sub = [b for b in bots if b["tier"] == tier]
        tiers[tier] = {"total": len(sub)}
        tiers[tier].update({s: sum(1 for b in sub if b["state"] == s)
                            for s in ("allowed", "blocked", "missing", "partial")})
    return {
        "schema_version": "2",
        "cloudflare_injected": "# BEGIN Cloudflare Managed content" in txt,
        "deprecated_tokens": [t for t in ("anthropic-ai", "Claude-Web", "ChatGPT-Plugins") if t in txt],
        "truncated": doc["truncated"],
        "crawl_delay": doc["crawl_delay"],
        "sitemaps": doc["sitemaps"],
        "bots": bots,
        "bots_allowed": buckets["allowed"], "bots_blocked": buckets["blocked"],
        "bots_missing": buckets["missing"], "bots_partial": buckets["partial"],
        "tiers": tiers,
        "citation": citation_report(doc),
        # answers vs training 分层:封 search/user 才是可见性失败;封 training 只是授权决策不扣分
        "visibility_failures": [b["token"] for b in bots
                                if b["tier"] in ("search", "user") and b["state"] in ("blocked", "partial")],
        "content_signal": SIGNALS.get(mode, SIGNALS["visibility"]),
        # 现有的 Content-Signal 行(11-05 第三轮留出站 fly.io:已有同一行,脚本还建议加)
        "content_signal_present": [m.strip() for m in re.findall(r"(?im)^\s*content-signal\s*:\s*(.+)$", txt)],
    }

# ---------------------------------------------------------------------------
# --fix-robots:修复建议块(缺失/被封的 bot 逐个 "# {desc}\nUser-agent: {token}\nAllow: /";
# 同长规则 Allow 平局胜出,故追加 Allow: / 即可翻转既有 Disallow: /;只打印不写盘)
# ---------------------------------------------------------------------------
def fix_robots(report):
    lines = ["== robots.txt 修复建议(追加到现有 robots.txt 末尾;只打印不写盘)==", ""]
    headers = {"search": "# —— 引用层(search):被封/缺失=逐出 AI 答案,建议追加 ——",
               "user":   "# —— 按需层(user):封禁=用户端不可达,建议追加 ——",
               "training": "# —— 训练层(training):封禁是授权决策而非错误,仅在你决定开放时追加 ——",
               "other": "# —— 其他层(other:站长委托/广告审核/用途待核):不影响搜索可见性,按需追加 ——"}
    for tier in TIER_ORDER:
        need = [b for b in report["bots"] if b["tier"] == tier and b["state"] != "allowed"]
        if not need: continue
        lines.append(headers[tier])
        for b in need:
            lines += [f"# {b['desc']}", f"User-agent: {b['token']}", "Allow: /", ""]
    wild = [b for b in report["bots"] if b["token"] in CITATION_BOTS
            and b["state"] == "allowed" and b["via_wildcard"]]
    if wild:  # 通配符放行的引用 bot:补专属规则才拿得到 citation 满分
        lines.append("# —— 专属规则补全:通配符 Allow 也行,但 citation 评分拿不到全分 ——")
        for b in wild:
            lines += [f"# {b['desc']}", f"User-agent: {b['token']}", "Allow: /", ""]
    if len(lines) == 2:
        return "== robots.txt 修复建议:无需修复(引用/按需层全部放行,引用 5 bot 均有专属规则)=="
    return "\n".join(lines).rstrip() + "\n"

STATUS = {
    "search":   {"allowed": "✅", "blocked": "❌ 禁(逐出AI答案)", "partial": "◐ 部分(仅Allow路径)", "missing": "✅ 未提及(默认放行)"},
    "user":     {"allowed": "✅", "blocked": "❌ 禁(用户端不可达)", "partial": "◐ 部分(仅Allow路径)", "missing": "✅ 未提及(默认放行)"},
    "training": {"allowed": "放行", "blocked": "禁(不影响搜索,授权决策)", "partial": "部分(仅Allow路径)", "missing": "未提及(默认放行)"},
    "other":    {"allowed": "放行", "blocked": "禁(不影响搜索)", "partial": "部分(仅Allow路径)", "missing": "未提及(默认放行)"},
}

def render(report):
    out = []
    if report["cloudflare_injected"]:
        out.append("⚠ Cloudflare 边缘注入块存在(站长源文件看不到)——去 Security→Bot traffic 关闭 block training")
    out.append(f"{'bot':<22}{'类别':<8}状态")
    for tier in TIER_ORDER:
        for b in report["bots"]:
            if b["tier"] != tier: continue
            mark = STATUS[tier][b["state"]]
            if b["state"] == "allowed" and b["via_wildcard"] and tier in ("search", "user"):
                mark = "✅(靠 * 通配)"
            if not b.get("verified", True):
                mark += "(未核:无官方 bot 文档)"
            out.append(f"{b['token']:<22}{TIER_LABELS[tier]:<8}{mark}")
    out.append("")
    for s in ("allowed", "blocked", "missing", "partial"):
        lst = report[f"bots_{s}"]
        out.append(f"bots_{s}({len(lst)}): " + (", ".join(lst) if lst else "-"))
    t = report["tiers"]
    out.append(f"\n分层统计: training {t['training']['allowed']}/{t['training']['total']} 放行"
               f" | search {t['search']['allowed']}/{t['search']['total']} 放行"
               f" | user {t['user']['allowed']}/{t['user']['total']} 放行"
               f" | other {t['other']['allowed']}/{t['other']['total']} 放行")
    c = report["citation"]
    out.append(f"citation_bots_ok: {'✅' if c['ok'] else '❌'} {c['allowed_count']}/5 放行"
               + ("(基础分)" if c["ok"] else "(可见性失败:引用 bot 被封/未被放行)"))
    # 专属规则只是本套件的加分项:RFC 9309 下 `*` 组对所有爬虫同样生效,没有外部依据说必须点名,
    # 所以未点名只给提示(ℹ),不报警告(2026-11-05 三站实战判为误报后改)
    out.append(f"citation_bots_explicit: {'✅' if c['explicit'] else 'ℹ'} {c['explicit_count']}/5 专属规则"
               + ("(满分)" if c["explicit"] else "(可选:没点名的 bot 按 `*` 组或默认全放行处理,点名只是便于单独调整)"))
    if report["visibility_failures"]:
        out.append(f"可见性失败: {', '.join(report['visibility_failures'])}(封 search/user 才是可见性失败;"
                   f"封 training 只是授权决策,不扣分)")
    else:
        out.append("可见性结论: ✅ 引用(search)与按需(user)bot 无封禁;training 封禁属授权决策,不扣分")
    out.append("\n过时 token 检查: " + (", ".join(report["deprecated_tokens"]) if report["deprecated_tokens"] else "无"))
    sm = report["sitemaps"]
    out.append("Sitemap 行: " + (f"有({len(sm)} 条)" if sm else "❌ 缺"))
    out.append("Crawl-delay(* 组): " + (str(report["crawl_delay"]) if report["crawl_delay"] is not None else "无"))
    present = report.get("content_signal_present") or []
    if report["content_signal"] in present:
        out.append(f"\nContent-Signal: 已有「{report['content_signal']}」,和建议一致")
    elif present:
        out.append(f"\nContent-Signal: 现有「{'」「'.join(present)}」;按当前取向建议改成(业务决策,Googlebot 不遵守、"
                   f"非排名因素):\n  Content-Signal: {report['content_signal']}")
    else:
        out.append(f"\n建议 Content-Signal(业务决策,Googlebot 不遵守、非排名因素):\n  Content-Signal: {report['content_signal']}")
    return "\n".join(out)

USAGE = """usage: robots_posture.py URL [--signal visibility|protect-ip] [--json] [--fix-robots]
	URL 通常是 https://site/robots.txt(给站点根也行,自动拼 /robots.txt)。
	仅 http(s):file:///ftp:// 等非 http(s) scheme 拒;私网/环回/链路本地拒连;
	重定向逐跳复查(SSRF 防护;本地 fixture 请经 import analyze() 消费)。
读取 robots.txt,输出 37 bot 四层矩阵(training/search/user/other)+四态判定(allowed/blocked/
partial/missing)+两级引用评分(citation_bots_ok/citation_bots_explicit)+分层统计
+bots_allowed/bots_blocked/bots_missing/bots_partial 四列表+Cloudflare 注入检测
+Crawl-delay/Sitemap 提取+Content-Signal 建议。封 training 不扣分(授权决策),
封 search/user 才是可见性失败。
--signal      visibility|protect-ip(Content-Signal 建议)
--json        结构化输出(同上字段,供 agent 消费)
--fix-robots  打印修复建议块(# 描述 + User-agent: {token} + Allow: /,可追加到现有
              robots.txt;只打印不写盘)"""

def main():
    a = sys.argv[1:]
    if any(x in ("-h", "--help") for x in a):
        print(USAGE); return
    url, mode, robots_file = None, None, None
    as_json, fix = "--json" in a, "--fix-robots" in a
    i = 0
    while i < len(a):
        x = a[i]
        if x == "--signal":
            mode = a[i + 1] if i + 1 < len(a) and not a[i + 1].startswith("-") else "visibility"
            i += 2
        elif x == "--robots-file":
            robots_file = a[i + 1] if i + 1 < len(a) and not a[i + 1].startswith("-") else None
            i += 2
        elif x in ("--json", "--fix-robots"):
            i += 1
        elif x.startswith("-") or url is not None:
            sys.stderr.write(USAGE + "\n"); sys.exit(2)
        else:
            url = x; i += 1
    if not url:
        sys.stderr.write(USAGE + "\n"); sys.exit(2)
    if robots_file:
        # 离线模式:robots.txt 本地读(测试/本地分析;线上仍走 fetch+SSRF 守卫)
        try:
            with open(robots_file, encoding="utf-8", errors="replace") as f:
                txt = f.read()
        except OSError as e:
            sys.stderr.write(f"读取失败 {robots_file}: {e}\n"); sys.exit(2)
    else:
        url = url.rstrip("/") + "/robots.txt" if not url.rstrip("/").endswith("robots.txt") else url
        try:
            txt = fetch(url)
        except Exception as e:
            sys.stderr.write(f"抓取失败 {url}: {e}\n"); sys.exit(1)
    report = analyze(txt, mode or "visibility")
    if as_json:
        payload = dict(report)
        if fix:
            payload["fix_robots"] = fix_robots(report)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(render(report))
    if fix:
        print("\n" + fix_robots(report))

if __name__ == "__main__": main()
