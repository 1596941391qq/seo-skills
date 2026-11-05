#!/usr/bin/env python3
"""ga4_api.py — GA4 Data API 只读拉数(RQ-229 第 2 批;stdlib only,凭证复用 gsc_api 的服务账号签名)。

做什么:
  channels  按默认渠道分组(sessionDefaultChannelGroup)列会话;GA4 自带「AI Assistant」渠道时它会单独出现。
  ai        AI 引荐:先取「AI Assistant」渠道的会话,再按来源(sessionSource)拆到引擎;没有这个渠道的媒体资源,
            退回按来源域名白名单认(chatgpt.com、perplexity.ai、gemini.google.com、copilot.microsoft.com、claude.ai 等)。
            --compare 同时给上一个同长窗口。

凭证:服务账号 JSON(--sa 或 env GSC_SA_FILE / GA4_SA_FILE),要在 GA4 媒体资源里加成「查看者」;
      Google Cloud 项目要开 Google Analytics Data API。scope 只用 analytics.readonly。
媒体资源 ID:--property 或 env GA4_PROPERTY_ID(数字,不是 G- 开头的衡量 ID)。

用法:
  python3 ga4_api.py channels --property 123456789 [--days 28] [--json]
  python3 ga4_api.py ai --property 123456789 --days 7 --compare --json
退出码:0 正常;1 API 错误;2 用法 / 凭证错误。
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import gsc_api as G  # noqa: E402

SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
API = "https://analyticsdata.googleapis.com/v1beta/properties/%s:runReport"
AI_CHANNEL = "AI Assistant"
# 退回口径:来源域名 → 引擎名。只收公开可核的 AI 助手域名;新引擎在这里加。
AI_SOURCES = {
    "chatgpt.com": "ChatGPT", "chat.openai.com": "ChatGPT", "openai.com": "ChatGPT",
    "perplexity.ai": "Perplexity", "www.perplexity.ai": "Perplexity",
    "gemini.google.com": "Gemini", "bard.google.com": "Gemini",
    "copilot.microsoft.com": "Copilot", "edgeservices.bing.com": "Copilot",
    "claude.ai": "Claude", "chat.deepseek.com": "DeepSeek", "deepseek.com": "DeepSeek",
    "grok.com": "Grok", "x.ai": "Grok", "meta.ai": "Meta AI", "you.com": "You.com",
    "poe.com": "Poe", "kimi.moonshot.cn": "Kimi", "kimi.com": "Kimi", "doubao.com": "Doubao",
    "chat.mistral.ai": "Mistral", "duckduckgo.com/aichat": "Duck.ai",
}

_cache = {}


def token(sa):
    key = sa.get("client_email")
    hit = _cache.get(key)
    if hit and time.time() < hit[1]:
        return hit[0]
    G.guard_googleapis(sa["token_uri"])
    iat = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {"iss": sa["client_email"], "scope": SCOPE, "aud": sa["token_uri"], "exp": iat + 3600, "iat": iat}
    h = G.b64url(json.dumps(header, separators=(",", ":")).encode())
    c = G.b64url(json.dumps(claims, separators=(",", ":")).encode())
    sig = G.rsa_sign(hashlib.sha256(("%s.%s" % (h, c)).encode("ascii")).digest(), sa["private_key"])
    body = urllib.parse.urlencode({"grant_type": G.GRANT_TYPE, "assertion": "%s.%s.%s" % (h, c, G.b64url(sig))})
    resp = G._http_json(sa["token_uri"], data=body.encode("ascii"),
                        headers={"User-Agent": G.UA, "Content-Type": "application/x-www-form-urlencoded"})
    _cache[key] = (resp["access_token"], time.time() + 3000)
    return resp["access_token"]


def run_report(sa, prop, body):
    url = API % prop
    G.guard_googleapis(url)
    data = json.dumps(body).encode("utf-8")
    resp = G._http_json(url, data=data, headers={"User-Agent": G.UA, "Authorization": "Bearer " + token(sa),
                                                 "Content-Type": "application/json"})
    out = []
    for r in resp.get("rows") or []:
        dims = [d.get("value") for d in r.get("dimensionValues") or []]
        mets = [float(m.get("value") or 0) for m in r.get("metricValues") or []]
        out.append((dims, mets))
    return out


def window(days, end=None, offset=0):
    end = end or (dt.date.today() - dt.timedelta(days=1))
    last = end - dt.timedelta(days=offset * days)
    first = last - dt.timedelta(days=days - 1)
    return first.isoformat(), last.isoformat()


def channels(sa, prop, first, last):
    rows = run_report(sa, prop, {"dateRanges": [{"startDate": first, "endDate": last}],
                                 "dimensions": [{"name": "sessionDefaultChannelGroup"}],
                                 "metrics": [{"name": "sessions"}], "limit": 50})
    return {d[0]: int(m[0]) for d, m in rows}


def engine_of(source):
    s = (source or "").lower()
    for dom, name in AI_SOURCES.items():
        if s == dom or s.endswith("." + dom) or s.startswith(dom):
            return name
    return None


def ai_breakdown(sa, prop, first, last):
    rows = run_report(sa, prop, {"dateRanges": [{"startDate": first, "endDate": last}],
                                 "dimensions": [{"name": "sessionDefaultChannelGroup"}, {"name": "sessionSource"}],
                                 "metrics": [{"name": "sessions"}], "limit": 2000})
    has_channel = any(d[0] == AI_CHANNEL for d, _ in rows)
    total, by = 0, {}
    for (chan, src), m in rows:
        n = int(m[0])
        if has_channel:
            if chan != AI_CHANNEL:
                continue
            name = engine_of(src) or src
        else:
            name = engine_of(src)
            if not name:
                continue
        total += n
        by[name] = by.get(name, 0) + n
    return {"ai_sessions": total, "by_engine": dict(sorted(by.items(), key=lambda kv: -kv[1])),
            "basis": "GA4 渠道「%s」" % AI_CHANNEL if has_channel else "来源域名白名单(这个媒体资源没有 AI Assistant 渠道)"}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ga4_api.py", description="GA4 Data API 只读拉数")
    ap.add_argument("cmd", choices=("channels", "ai"))
    ap.add_argument("--property", default=os.environ.get("GA4_PROPERTY_ID"))
    ap.add_argument("--sa", default=os.environ.get("GA4_SA_FILE") or os.environ.get("GSC_SA_FILE"))
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--compare", action="store_true", help="同时给上一个同长窗口")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    if not ns.property or not ns.sa:
        sys.stderr.write("ga4_api.py: 要 --property(或 GA4_PROPERTY_ID)和 --sa(或 GSC_SA_FILE)\n")
        return 2
    try:
        sa = G.load_sa(ns.sa)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("ga4_api.py: 服务账号读不了:%s\n" % e)
        return 2
    cur = window(ns.days)
    prev = window(ns.days, offset=1)
    try:
        if ns.cmd == "channels":
            out = {"property": ns.property, "window": cur, "channels": channels(sa, ns.property, *cur)}
            if ns.compare:
                out["previous"] = {"window": prev, "channels": channels(sa, ns.property, *prev)}
        else:
            out = dict(ai_breakdown(sa, ns.property, *cur), property=ns.property, window=cur)
            if ns.compare:
                p = ai_breakdown(sa, ns.property, *prev)
                out["ai_sessions_prev"] = p["ai_sessions"]
                out["by_engine_prev"] = p["by_engine"]
                out["window_prev"] = prev
    except urllib.error.HTTPError as e:
        sys.stderr.write("ga4_api.py: %s\n" % G.describe_http_error(e))
        return 1
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("ga4_api.py: %s\n" % e)
        return 1
    if ns.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for k, v in out.items():
            print("%s: %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
