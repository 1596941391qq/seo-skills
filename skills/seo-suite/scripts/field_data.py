#!/usr/bin/env python3
"""CWV 现场数据(field data)采集器:PSI v5 + CrUX API 双源 REST 客户端(stdlib only)。
注意:PSI 文档写明计划停止在 API 响应里返回 CrUX 现场数据(developers.google.com/speed/docs/insights/v5/get-started,
核对 2026-10-21);现场数据以 CrUX 源为准,PSI 源主要看实验室数据。
现场(field)= CrUX 28 天真实用户 p75;实验(lab)= Lighthouse 合成环境审计数值——
两口径分开解析、分开呈现,输出显式标注"现场 vs 实验"。
数据接入口径(与 references/overview/data-onboarding.md 的 want-cwv/T1 条目一致:
PSI key 免费约 5 分钟,`export PSI_API_KEY=…`(CrUX 用 CRUX_API_KEY),不进 git):
- PSI(PageSpeed Insights v5)`GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
  ?url={u}&strategy={mobile|desktop}[&key={k}]`。无 key 也可低配额调用(共享池,易 429;
  配额纪律:无 key 只做轻量单发,批量/正式使用设 env PSI_API_KEY,有 key 约 25k 次/天·
  240 次/分钟)。loadingExperience 即 CrUX 页级现场数据:键 LARGEST_CONTENTFUL_PAINT_MS /
  INTERACTION_TO_NEXT_PAINT / EXPERIMENT_TIME_TO_FIRST_BYTE / FIRST_CONTENTFUL_PAINT_MS
  单位毫秒,CUMULATIVE_LAYOUT_SHIFT_SCORE 为百分之一表示(5 = CLS 0.05,÷100);
  lighthouseResult.audits 为实验数据(lcp/cls/tbt/fcp/inp 的 numericValue 毫秒/小数 + score)。
- CrUX(Chrome UX Report API,必须 key)`https://chromeuxreport.googleapis.com/v1/
  records:queryRecord?key={k}`——官方口径为 POST + JSON body {origin|url,
  formFactor:PHONE|DESKTOP, metrics:[...]}(gRPC transcoding,developer.chrome.com/docs/crux/api,
  2026-10 核实;网络上的"GET 直查"说法以官方文档为准)。响应 record.metrics.
  {largest_contentful_paint,cumulative_layout_shift,interaction_to_next_paint,
  experimental_time_to_first_byte,first_contentful_paint}.percentiles.p75;其中
  cumulative_layout_shift 的 p75 是 2 位小数字符串("0.23"),其余为 int 毫秒。
  page(url=)与 origin(origin=)两种查询模式(--crux-scope)。无 key 时整源跳过并告警
  (降级:仅 PSI,不算失败)。
  软导航实验指标(2026-10-13 起,CrUX 2026-09 数据集):同一请求另要
  experimental_{largest_contentful_paint,interaction_to_next_paint,cumulative_layout_shift}
  _with_softnavs(类型同稳定版:CLS 为 2 位小数字符串,其余 int 毫秒;CrUX API 文档
  「Metric value types」表,核对 2026-11-05)。有就单列「含软导航(experimental)」,
  没有就不显示、不报错;只作参考,不进退出码、不进 CSV、不覆盖稳定版现场值。
阈值判定(官方 CWV 口径,写死;与 references/technical/cwv-playbook.md 同源):
  LCP good≤2.5s / NI≤4s;INP good≤200ms / NI≤500ms;CLS good≤0.1 / NI≤0.25;
  TTFB 参考 good≤0.8s / NI≤1.8s(web.dev 诊断口径,非核心三项);FCP 参考 1.8s/3s;
  TBT(实验)参考 200ms/600ms。边界含等号:2.5s=good,4s=needs_improvement,200ms=good。
用法: python3 field_data.py --url U [--strategy mobile|desktop|both] [--key K] [--json]
       python3 field_data.py --urls list.txt [--delay 1] [--crux-scope page|origin]
                            [--as-cwv-csv out.csv] [--json]
--as-cwv-csv 产出 traffic_funnel.py --cwv 直接可吃的 CSV(列 URL,LCP,CLS,DCL):
  LCP/CLS 取现场 p75(秒/小数),DCL 无直接 CWV 对应 → 用实验 FCP 近似(秒),无实验
  数据留空(traffic_funnel 将按 N/A 不计入 good_ux);--strategy both 时每 URL 一行,
  取 mobile 值(Search 排名以移动 CWV 为口径),缺 mobile 再取 desktop。
退出码: 0 正常 / 1 任一 URL 现场核心三项(LCP/INP/CLS)有 poor(TTFB/FCP 参考项不触发)/
  2 输入错(参数/文件/URL 校验:非 http(s)、私网、环回等)/ 3 全源失败(所有 URL 现场+
  实验均无数据;无 key 的 crux 跳过不算失败)。SSRF 防御照 monitor.py 惯例:输入 URL 仅
  http(s) 且拒私网/环回/链路本地(本工具不直接抓取目标 URL,仅作入参校验);429/403 给出
  "加 key 或降频"提示。"""
import csv
import ipaddress
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCHEMA_VERSION = 1          # --json 顶层 schema 版本(输出契约)
UA = "Mozilla/5.0 (compatible; seo-suite-field/1.0)"
PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CRUX_ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
DEFAULT_TIMEOUT = 60        # PSI 会现场跑一次 Lighthouse,可达 20-60s
FETCH_LIMIT = 4_000_000     # PSI 响应可到数 MB

# 官方 CWV 阈值(写死,单位:时间毫秒/CLS 无量纲;(good, needs_improvement 上界])
THRESHOLDS = {"LCP": (2500.0, 4000.0), "INP": (200.0, 500.0), "CLS": (0.1, 0.25),
              "TTFB": (800.0, 1800.0), "FCP": (1800.0, 3000.0), "TBT": (200.0, 600.0)}
CORE_FIELD = ("LCP", "INP", "CLS")          # 核心三项:唯一触发退出码 1 的现场指标
FIELD_ORDER = ("LCP", "INP", "CLS", "TTFB", "FCP")
LAB_ORDER = ("LCP", "CLS", "TBT", "INP", "FCP")
# PSI loadingExperience.metrics 键 → 统一指标名(CLS 为百分之一表示,解析时 ÷100)
PSI_FIELD_KEYS = {"LARGEST_CONTENTFUL_PAINT_MS": "LCP",
                  "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
                  "INTERACTION_TO_NEXT_PAINT": "INP",
                  "EXPERIMENT_TIME_TO_FIRST_BYTE": "TTFB",
                  "FIRST_CONTENTFUL_PAINT_MS": "FCP"}
# Lighthouse 审计 id → 统一指标名(INP 审计为实验性,两个候选 id 都认)
PSI_LAB_AUDITS = {"largest-contentful-paint": "LCP", "cumulative-layout-shift": "CLS",
                  "total-blocking-time": "TBT", "first-contentful-paint": "FCP",
                  "experimental-interaction-to-next-paint": "INP",
                  "interaction-to-next-paint": "INP"}
# CrUX record.metrics 键 → 统一指标名
CRUX_METRICS = {"largest_contentful_paint": "LCP", "cumulative_layout_shift": "CLS",
                "interaction_to_next_paint": "INP", "experimental_time_to_first_byte": "TTFB",
                "first_contentful_paint": "FCP"}
# CrUX 软导航实验指标(SPA 路由切换计入;web.dev/blog/crux-experimental-soft-navs,
# 预计 2027-05 转正,转正前标 experimental、只作参考,见 references/overview/facts.md#crux-softnav)
CRUX_SOFTNAV_METRICS = {"experimental_largest_contentful_paint_with_softnavs": "LCP",
                        "experimental_interaction_to_next_paint_with_softnavs": "INP",
                        "experimental_cumulative_layout_shift_with_softnavs": "CLS"}
FORM_FACTOR = {"mobile": "PHONE", "desktop": "DESKTOP"}

USAGE = """usage: field_data.py --url U | --urls list.txt [--strategy mobile|desktop|both]
                     [--crux-scope page|origin] [--key K] [--delay 1] [--timeout 60]
                     [--as-cwv-csv out.csv] [--json]
CWV 现场数据(CrUX 28 天真实用户 p75)+ 实验数据(Lighthouse)双源采集,官方阈值判定:
  --url U           单个目标 URL(与 --urls 可并用,合并去重)
  --urls PATH       批量清单(每行一个 URL,空行/# 注释跳过;--url/--urls 至少一项)
  --strategy S      mobile|desktop|both(默认 mobile;both = 每 URL 两次采集)
  --crux-scope S    page|origin(默认 page;origin 查询 CrUX 站点级聚合)
  --key K           Google API key(同时供 PSI/CrUX;或 env PSI_API_KEY / CRUX_API_KEY,
                    crux 缺省回退 PSI_API_KEY——Google Cloud 同一 key 可同时启用两 API)
  --delay SEC       批量时 URL 间隔秒数(默认 1.0,礼貌限速;PSI 无 key 共享配额易 429)
  --timeout SEC     单请求超时(默认 60;PSI 现场跑 Lighthouse 较慢)
  --as-cwv-csv F    写 traffic_funnel.py --cwv 兼容 CSV(列 URL,LCP,CLS,DCL):
                    LCP/CLS=现场 p75(秒/小数);DCL 无直接对应→实验 FCP 近似(秒),
                    无实验数据留空(funnel 按 N/A);both 策略取 mobile 值
  --json            结构化输出(schema_version=1;每 URL {url,strategy,field,lab,source})
配额纪律:PSI 无 key 可低配额调用(轻量单发);批量/正式用 PSI_API_KEY(≈25k 次/天·
240 次/分钟)。CrUX 必须 key,无 key 整源跳过并告警(降级仅 PSI,不算失败);
429/403 时提示加 key 或降频。
判定(写死官方口径):LCP≤2.5s/4s,INP≤200ms/500ms,CLS≤0.1/0.25,
TTFB 参考 0.8s/1.8s,FCP 参考 1.8s/3s,TBT(实验)参考 200ms/600ms;边界含等号。
退出码:0 正常 / 1 现场核心三项(LCP/INP/CLS)任一 poor(TTFB/FCP 参考项不触发)/
2 输入错(含 URL 非 http(s)/私网 SSRF 拒绝)/ 3 全源失败(所有 URL 现场+实验均无数据)。"""


# ---------- SSRF 防御(照 monitor.py 惯例:仅 http(s)+拒私网/环回/链路本地) ----------

class GuardError(Exception):
    pass


_ssrf_cache = {}


def ssrf_guard(host):
    """仅 http(s)+拒私网/环回/链路本地/保留/组播;结果按 host 缓存。
    198.18.0.0/15(RFC2544)豁免本机 fake-IP 代理;SEO_FIELD_STRICT_SSRF=1 恢复全拒。
    本工具不抓取目标 URL(仅作查询参数发给 googleapis),此校验是入参卫生检查。"""
    if not host:
        raise GuardError("empty host")
    if host in _ssrf_cache:
        return
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as e:
        raise GuardError("DNS 解析失败 %s: %s" % (host, e))
    strict = bool(os.environ.get("SEO_FIELD_STRICT_SSRF"))
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if ip in ipaddress.ip_network("198.18.0.0/15"):
            if not strict:
                continue
            raise GuardError("SSRF guard: 非公网地址 %s(strict 模式拒 fake-IP 段)" % ip)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise GuardError("SSRF guard: 非公网地址 %s" % ip)
    _ssrf_cache[host] = True


def validate_url(url):
    """输入 URL 校验:仅 http(s)+SSRF 私网拒连;返回错误串或 None。"""
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        return "仅允许 http(s) URL: %s" % url
    try:
        ssrf_guard(p.hostname)
    except GuardError as e:
        return str(e)
    return None


# ---------- HTTP(测试打桩点:模块级 fetch_json) ----------

def fetch_json(url, payload=None, timeout=DEFAULT_TIMEOUT):
    """GET(payload=None)或 POST JSON;返回解析后的 dict。HTTPError 原样上抛给调用方。"""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read(FETCH_LIMIT).decode("utf-8", "replace"))


def http_error(source, e):
    """HTTPError → 统一错误条目;429/403 附"加 key 或降频"提示(配额纪律)。"""
    try:
        body = e.read()[:500].decode("utf-8", "replace")
    except Exception:
        body = ""
    ent = {"source": source, "code": e.code, "message": "HTTP %s %s%s" % (
        e.code, body.strip()[:200], "" if body else getattr(e, "reason", ""))}
    if e.code in (403, 429):
        ent["hint"] = ("配额/权限受限:加 key(PSI_API_KEY / CRUX_API_KEY,Google Cloud "
                       "同一 key 可同时启用两 API)或降频(--delay 调大)")
    return ent


def psi_request_url(url, strategy, key=None):
    q = {"url": url, "strategy": strategy}
    if key:
        q["key"] = key
    return PSI_ENDPOINT + "?" + urllib.parse.urlencode(q)


def crux_request_body(target, scope, form_factor):
    body = {"formFactor": form_factor, "metrics": list(CRUX_METRICS) + list(CRUX_SOFTNAV_METRICS)}
    if scope == "origin":                          # origin 查询:剥路径,只留 scheme://netloc
        body["origin"] = "%s://%s" % urllib.parse.urlsplit(target)[:2]
    else:
        body["url"] = target
    return body


def query_psi(url, strategy, key=None, timeout=DEFAULT_TIMEOUT):
    try:
        return fetch_json(psi_request_url(url, strategy, key), None, timeout), None
    except urllib.error.HTTPError as e:
        return None, http_error("psi", e)
    except Exception as e:
        return None, {"source": "psi", "message": "%s" % e}


def query_crux(url, strategy, key, scope="page", timeout=DEFAULT_TIMEOUT):
    body = crux_request_body(url, scope, FORM_FACTOR[strategy])
    try:
        return fetch_json(CRUX_ENDPOINT + "?key=" + key, body, timeout), None
    except urllib.error.HTTPError as e:
        return None, http_error("crux", e)
    except Exception as e:
        return None, {"source": "crux", "message": "%s" % e}


# ---------- 解析(纯函数,零网络) ----------

def parse_psi_field(le):
    """PSI loadingExperience → {指标: (p75 规范值, category)};规范值:毫秒/CLS 小数。
    CUMULATIVE_LAYOUT_SHIFT_SCORE 为百分之一表示(官方),÷100 归一。"""
    out = {}
    for key, name in PSI_FIELD_KEYS.items():
        m = (le.get("metrics") or {}).get(key) or {}
        if m.get("percentile") is None:
            continue
        p = float(m["percentile"])
        out[name] = (p / 100.0 if name == "CLS" else p, m.get("category"))
    return out


def parse_psi_lab(lh):
    """PSI lighthouseResult.audits → {指标: {value,unit,verdict,score,numeric}};
    numericValue 毫秒(LCP/FCP/TBT/INP)或 CLS 小数。"""
    audits = lh.get("audits") or {}
    out = {}
    for aid, name in PSI_LAB_AUDITS.items():
        a = audits.get(aid) or {}
        if a.get("numericValue") is None or name in out:
            continue
        canon = float(a["numericValue"])
        value, unit = display_value(name, canon)
        ent = {"value": value, "unit": unit, "verdict": cwv_verdict(name, canon),
               "numeric": canon}
        if a.get("score") is not None:
            ent["score"] = a["score"]
        out[name] = ent
    return out


def parse_crux(record, keys=None):
    """CrUX 响应 → {指标: p75 规范值};cumulative_layout_shift 的 p75 官方为
    2 位小数字符串("0.23"),其余 int 毫秒;percentiles 兼容 dict 与 list 两种形态。
    keys 缺省为稳定版 CRUX_METRICS;传 CRUX_SOFTNAV_METRICS 取软导航实验指标。"""
    metrics = (record.get("record") or {}).get("metrics") or {}
    out = {}
    for key, name in (CRUX_METRICS if keys is None else keys).items():
        pc = (metrics.get(key) or {}).get("percentiles")
        p75 = None
        if isinstance(pc, dict):
            p75 = pc.get("p75")
        elif isinstance(pc, list) and pc:
            p75 = pc[0].get("p75")
        if p75 is not None:
            out[name] = float(str(p75))
    return out


# ---------- 阈值判定与展示 ----------

def cwv_verdict(metric, value):
    """官方 CWV 口径(边界含等号):≤good 阈值=good;≤NI 阈值=needs_improvement;否则 poor。"""
    good, ni = THRESHOLDS[metric]
    if value <= good:
        return "good"
    if value <= ni:
        return "needs_improvement"
    return "poor"


def display_value(metric, canon):
    """规范值(毫秒/CLS 小数)→(展示值, 单位):LCP/FCP/TTFB 秒,INP/TBT 毫秒,CLS 无量纲。"""
    if metric == "CLS":
        return round(canon, 3), ""
    if metric in ("INP", "TBT"):
        return int(round(canon)), "ms"
    return round(canon / 1000.0, 3), "s"


def field_entry(name, canon, category=None, src=None):
    value, unit = display_value(name, canon)
    ent = {"value": value, "unit": unit, "verdict": cwv_verdict(name, canon), "p75": canon}
    if category:
        ent["category"] = category
    if src:
        ent["source"] = src
    return ent


# ---------- 采集 ----------

def collect(url, strategy, psi_key=None, crux_key=None, scope="page", timeout=DEFAULT_TIMEOUT):
    """单 URL×单策略:PSI(现场+实验)+ CrUX(现场);现场两源合并(PSI 页级优先,CrUX 补缺)。"""
    res = {"url": url, "strategy": strategy, "field": {}, "lab": {}, "field_softnav": {},
           "field_category": None, "performance_score": None,
           "source": "", "errors": [], "notes": []}
    srcs = []
    psi_field = {}
    data, err = query_psi(url, strategy, psi_key, timeout)
    if err:
        res["errors"].append(err)
    elif data:
        psi_field = parse_psi_field(data.get("loadingExperience") or {})
        lab = parse_psi_lab(data.get("lighthouseResult") or {})
        if psi_field or lab:
            srcs.append("psi")
        else:
            res["errors"].append({"source": "psi",
                                  "message": "响应 200 但 loadingExperience/lighthouseResult 均无数据"})
        for name in LAB_ORDER:                      # 固定列序
            if name in lab:
                res["lab"][name] = lab[name]
        res["performance_score"] = ((data.get("lighthouseResult") or {})
                                    .get("categories", {}).get("performance", {}) or {}).get("score")
        res["field_category"] = (data.get("loadingExperience") or {}).get("overall_category")
    crux_field = {}
    if crux_key:
        cdata, cerr = query_crux(url, strategy, crux_key, scope, timeout)
        if cerr:
            if cerr.get("code") == 404:             # CrUX 404 = 无数据(样本不足),非故障
                res["notes"].append("crux: 无数据(404,该 %s 样本不足不在 CrUX 数据集)" % scope)
            else:
                res["errors"].append(cerr)
        else:
            crux_field = parse_crux(cdata)
            if crux_field:
                srcs.append("crux")
            softnav = parse_crux(cdata, CRUX_SOFTNAV_METRICS)
            for name in CORE_FIELD:                 # 实验指标:单列,不并入 field
                if name in softnav:
                    ent = field_entry(name, softnav[name], None, "crux")
                    ent["experimental"] = True
                    res["field_softnav"][name] = ent
    for name in FIELD_ORDER:                        # 现场:PSI 优先,CrUX 补缺
        if name in psi_field:
            canon, cat = psi_field[name]
            res["field"][name] = field_entry(name, canon, cat, "psi")
        elif name in crux_field:
            res["field"][name] = field_entry(name, crux_field[name], None, "crux")
    res["source"] = "+".join(srcs)
    if not res["field"]:
        res["notes"].append("现场无数据:URL 不在 CrUX 数据集(流量/样本不足)或该 formFactor 无记录")
    return res


# ---------- 输出 ----------

def write_cwv_csv(results, path):
    """traffic_funnel --cwv 兼容 CSV(URL,LCP,CLS,DCL 表头,空格=指标缺失):
    LCP/CLS=现场 p75(秒/小数);DCL 无直接 CWV 指标→实验 FCP 近似(秒),缺实验留空。
    同 URL 多策略行:mobile 优先(Search 排名以移动 CWV 为口径)。"""
    rows, seen = [], {}
    for r in results:
        if r["url"] in seen:
            if r["strategy"] == "mobile":
                rows[seen[r["url"]]] = csv_row(r)
            continue
        seen[r["url"]] = len(rows)
        rows.append(csv_row(r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["URL", "LCP", "CLS", "DCL"])
        w.writerows(rows)


def csv_row(r):
    f, lab = r["field"], r["lab"]
    lcp = "%.3f" % (f["LCP"]["p75"] / 1000.0) if "LCP" in f else ""
    cls = "%.3f" % f["CLS"]["p75"] if "CLS" in f else ""
    dcl = "%.3f" % (lab["FCP"]["numeric"] / 1000.0) if "FCP" in lab else ""
    return [r["url"], lcp, cls, dcl]


VERDICT_MARK = {"good": "✓ good", "needs_improvement": "~ needs_improvement", "poor": "✗ poor"}


def render_markdown(results, notes):
    L = ["# CWV 现场数据(field:CrUX 28 天真实用户 p75)× 实验数据(lab:Lighthouse)", ""]
    for n in notes:
        L.append("> %s" % n)
    if notes:
        L.append("")
    for r in results:
        L.append("## %s [%s] — 源: %s" % (r["url"], r["strategy"], r["source"] or "none"))
        L.append("")
        L.append("### 现场 field(真实用户 p75,CrUX 口径)%s" %
                 ("overall: %s" % r["field_category"] if r["field_category"] else ""))
        L.append("")
        L.append("| 指标 | p75 | 判定 | 站内类别 | 来源 |")
        L.append("|---|---|---|---|---|")
        if r["field"]:
            for name, e in r["field"].items():
                L.append("| %s | %s %s | %s | %s | %s |" % (
                    name, e["value"], e["unit"], VERDICT_MARK[e["verdict"]],
                    e.get("category") or "-", e.get("source") or "-"))
        else:
            L.append("| (无现场数据) | - | - | - | - |")
        L.append("")
        if r.get("field_softnav"):
            L.append("### 现场 field·含软导航(experimental,CrUX;SPA 路由切换计入,只作参考,不进退出码)")
            L.append("")
            L.append("| 指标 | p75 | 判定(参考) | 稳定版 p75 |")
            L.append("|---|---|---|---|")
            for name, e in r["field_softnav"].items():
                st = r["field"].get(name)
                L.append("| %s | %s %s | %s | %s |" % (
                    name, e["value"], e["unit"], VERDICT_MARK[e["verdict"]],
                    "%s %s" % (st["value"], st["unit"]) if st else "-"))
            L.append("")
        L.append("### 实验 lab(Lighthouse 单次合成环境,非真实用户)")
        L.append("")
        L.append("| 指标 | 数值 | 评分 | 判定(参考) |")
        L.append("|---|---|---|---|")
        if r["lab"]:
            for name in LAB_ORDER:
                e = r["lab"].get(name)
                if e:
                    L.append("| %s | %s %s | %s | %s |" % (
                        name, e["value"], e["unit"],
                        "%d" % round(e["score"] * 100) if e.get("score") is not None else "-",
                        VERDICT_MARK[e["verdict"]]))
        else:
            L.append("| (无实验数据) | - | - | - |")
        perf = r.get("performance_score")
        if perf is not None:
            L.append("")
            L.append("性能评分(实验): %d/100" % round(perf * 100))
        for err in r["errors"]:
            L.append("")
            L.append("- [error:%s] %s%s" % (err["source"], err["message"],
                                            "(%s)" % err["hint"] if err.get("hint") else ""))
        for n in r["notes"]:
            L.append("- note: %s" % n)
        L.append("")
    return "\n".join(L)


def compute_exit(results):
    """3=全源失败(所有 URL 现场+实验均无数据)/1=现场核心三项任一 poor/0=正常。"""
    if results and all(not r["field"] and not r["lab"] for r in results):
        return 3
    for r in results:
        for name in CORE_FIELD:
            e = r["field"].get(name)
            if e and e["verdict"] == "poor":
                return 1
    return 0


# ---------- main ----------

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help") for a in args):
        print(USAGE)
        return 0
    opts = {"--url": None, "--urls": None, "--strategy": "mobile", "--key": None,
            "--crux-scope": "page", "--as-cwv-csv": None, "--delay": "1.0", "--timeout": "60"}
    as_json = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--json":
            as_json = True
        elif a in opts:
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                sys.stderr.write("参数错误:%s 需要一个值参数(见 --help)\n" % a)
                return 2
            opts[a] = args[i + 1]
            i += 1
        else:
            sys.stderr.write("未知参数 %s\n\n%s\n" % (a, USAGE))
            return 2
        i += 1
    strategy, scope = opts["--strategy"], opts["--crux-scope"]
    if strategy not in ("mobile", "desktop", "both"):
        sys.stderr.write("无效 --strategy %s(mobile|desktop|both)\n" % strategy)
        return 2
    if scope not in ("page", "origin"):
        sys.stderr.write("无效 --crux-scope %s(page|origin)\n" % scope)
        return 2
    try:
        delay, timeout = float(opts["--delay"]), float(opts["--timeout"])
    except ValueError:
        sys.stderr.write("--delay/--timeout 须为数值\n")
        return 2
    if delay < 0 or timeout <= 0:
        sys.stderr.write("--delay 须≥0 且 --timeout 须>0\n")
        return 2
    urls = []
    if opts["--url"]:
        urls.append(opts["--url"].strip())
    if opts["--urls"]:
        try:
            with open(opts["--urls"], encoding="utf-8") as f:
                urls.extend(ln.strip() for ln in f
                            if ln.strip() and not ln.strip().startswith("#"))
        except OSError as e:
            sys.stderr.write("无法读取 --urls 文件:%s\n" % e)
            return 2
    deduped = list(dict.fromkeys(urls))
    if not deduped:
        sys.stderr.write("需要 --url 或 --urls 至少一项(见 --help)\n")
        return 2
    bad = [(u, validate_url(u)) for u in deduped]
    bad = [(u, e) for u, e in bad if e]
    if bad:
        for u, e in bad:
            sys.stderr.write("URL 校验失败(SSRF/scheme):%s — %s\n" % (u, e))
        return 2
    psi_key = opts["--key"] or os.environ.get("PSI_API_KEY") or None
    # crux 回退 PSI key:Google Cloud 同一 key 常同时启用两 API(见 --help)
    crux_key = opts["--key"] or os.environ.get("CRUX_API_KEY") \
        or os.environ.get("PSI_API_KEY") or None
    notes = []
    if not psi_key:
        notes.append("PSI 无 key 低配额模式(共享池,易 429;批量/正式使用设 PSI_API_KEY)")
    if not crux_key:
        warn = ("crux 源跳过:未提供 API key(--key 或 CRUX_API_KEY/PSI_API_KEY)——"
                "CrUX API 必须 key,本次降级仅 PSI(跳过不算失败)")
        notes.append(warn)
        sys.stderr.write("[warn] %s\n" % warn)
    strategies = ["mobile", "desktop"] if strategy == "both" else [strategy]
    results = []
    for idx, u in enumerate(deduped):
        for s in strategies:
            results.append(collect(u, s, psi_key, crux_key, scope, timeout))
        if delay > 0 and idx < len(deduped) - 1:    # 批量礼貌间隔(末个 URL 不睡)
            time.sleep(delay)
    if opts["--as-cwv-csv"]:
        write_cwv_csv(results, opts["--as-cwv-csv"])
        sys.stderr.write("[ok] CWV CSV 已写 %s(URL,LCP,CLS,DCL;DCL=实验 FCP 近似,缺实验留空→"
                         "traffic_funnel 按 N/A)\n" % opts["--as-cwv-csv"])
    code = compute_exit(results)
    dataless = sum(1 for r in results if not r["field"] and not r["lab"])
    if code == 3:
        sys.stderr.write("[fail] 全源失败:%d/%d 个 URL×策略 现场+实验均无数据\n"
                         % (dataless, len(results)))
    elif dataless:
        sys.stderr.write("[warn] %d/%d 个 URL×策略 全源无数据(其余正常)\n" % (dataless, len(results)))
    for h in sorted({e.get("hint") for r in results for e in r["errors"] if e.get("hint")}):
        sys.stderr.write("[hint] %s\n" % h)        # 429/403 配额提示落到 stderr(配额纪律)
    if as_json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "tool": "field_data",
                          "results": results, "notes": notes, "exit_code": code},
                         ensure_ascii=False, indent=1))
    else:
        print(render_markdown(results, notes))
    return code


if __name__ == "__main__":
    sys.exit(main())
