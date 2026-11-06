#!/usr/bin/env python3
"""Bing Webmaster Tools API 薄客户端(免费,需 API key;pipeline-completeness.md R2-5;stdlib-only)。

Bing WMT JSON/REST API(官方 learn.microsoft.com/en-us/bingwebmaster;SOAP/POX 协议已于
2026-08-31 退役,仅剩 JSON/HTTP)。端点形态:
  https://ssl.bing.com/webmaster/api.svc/json/<方法>?apikey=<KEY>&<参数>
响应恒包一层 "d"(WCF 约定);错误形态 {"ErrorCode":int,"Message":str}——注意错误可能
随 HTTP 200 返回,只看状态码会把失败当成功。日期为 WCF "/Date(ms±zzzz)/" 毫秒时间戳。

子命令:
  urlstatus --site HOST [--url U ...]           # GetUrlInfo 逐 URL 收录/抓取状态
                                               #   + GetUrlSubmissionQuota 提交配额
  submit    --site HOST (--url U ... | --urls F)  # SubmitUrl(单)/SubmitUrlBatch(批,≤500/调用)
  stats     --site HOST [--url U] [--out F]     # GetQueryStats → CSV(+--url 时附 GetUrlInfo)
  pagequery --site HOST --page U [--out F]      # GetPageQueryStats → 单页的查询 CSV(同 stats 列)
  feeds     --site HOST [--submit SITEMAP ...]  # GetFeeds 列 sitemap 状态;--submit 先 SubmitFeed(重)交
                                               #   有 sitemap 读不到(Status 不是 Success/Pending)时退出码 3

给 Google 交网址或 sitemap 时,同一批也交 Bing:网址用 submit,sitemap 用 feeds --submit,
再跑一次 feeds 看每张是 Success 且 UrlCount 不为 0(Google 没有普通网页的提交 API)。

凭证寻径:--key > env BING_WMT_KEY(doctor.py T4 键,免费)。无 key 不猜——doctor 式指路。

CSV 契约(stats;列序对齐 gsc_api.py / gsc_mining.py,可直接喂 gsc_mining --mode query
与 sensor_volatility 的 Date/Query/Position 契约):
  Date,Query,Clicks,Impressions,CTR,Position
  - CTR=Clicks/Impressions 小数(0.0317;gsc_mining.parse_ctr 对小数形态全区间无歧义);
  - Position=AvgImpressionPosition(2 位小数)。AvgClickPosition 在 Clicks=0 时恒为 -1,
    是 Bing"无点击"哨兵值,不作 Position;
  - Date 由 WCF 时间戳转 UTC YYYY-MM-DD。

诚实边界(不假装能做到的):
  - 提交配额实测约 100/日 + 1300/月(站点间可不同,以 GetUrlSubmissionQuota 读数为准,
    不假设;两桶同批扣减)。SubmitUrlBatch 单调用上限 500,超出自动分批;
  - 流量/查询数据在站点验证后数天才开始有,验证前历史不回填——GetQueryStats 空列表
    不是 0 也不是错,是"还没有";--json 如实给 rows:[];
  - 2026-08-31 API 裁撤后 GetUrlSubmissionStatus 端点已 404——urlstatus 以 GetUrlInfo
    (单页发现/抓取详情,即 URL 在 Bing 侧的状态)+ GetUrlSubmissionQuota 实现;
  - GetUrlInfo 的 HttpStatus=0/DocumentSize=0 是 Bing 自家 API 的老怪癖(官方示例
    2011 年起即如此),DiscoveryDate/LastCrawledDate 才是可靠字段;
  - Google 无对应公开提交 API(GSC 靠手工/sitemap)——本工具只管 Bing;
  - 重复提交同一 URL 不报错也不增加收录机会(引擎记为重复)——别拿提交当重试。

SSRF 防御(套件惯例,照 gsc_api.py 端点固定思路):仅 https + bing.com 域白名单
(ssl.bing.com/www.bing.com 等 bing.com 及子域);端点基址内置,不接受任意 URL。
apikey 只进请求查询串,不进任何输出(异常信息过 redact_key)。

退出码:0 正常;1 运行错(网络/HTTP/API/凭证缺失);2 用法错(参数/SSRF 拒);
3 feeds 发现有 sitemap Bing 读不到。
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SCHEMA_VERSION = 1               # --json 顶层 schema 版本(输出契约)
UA = "seo-suite-bingwmt/1.0"
API_BASE = "https://ssl.bing.com/webmaster/api.svc/json"
ENV_KEY = "BING_WMT_KEY"         # doctor.py T4 键(--keys 可校验存在性)
SUBMIT_BATCH_LIMIT = 500         # SubmitUrlBatch 单调用上限(api-reference 口径)
FETCH_LIMIT = 4_000_000          # 响应体读取上限(与 gsc_api 同量级)
DEFAULT_TIMEOUT = 30
CSV_COLUMNS = ["Date", "Query", "Clicks", "Impressions", "CTR", "Position"]

# Bing 侧 key 获取指引(doctor 式指路;无 key 时打印,不猜不发请求)
KEY_HOWTO = (
    "获取(免费,约 2 分钟):bing.com/webmasters 登录 → 站点 → Settings → API access →\n"
    "  生成 API key(一个用户一把 key,对其全部已验证站点生效;站点需先在 WMT 验证)。\n"
    "  配好后:export %s=\"…\" 或 --key 传参;doctor.py --keys --check 可校验存在性(不读值)"
    % ENV_KEY)


class UsageError(Exception):
    """参数校验失败——用法错(exit 2)。"""


class GuardError(Exception):
    """端点白名单拒(SSRF 防御)——用法级错误(exit 2)。"""


class CredentialError(Exception):
    """API key 缺失——运行错(exit 1,doctor 式指路不猜)。"""


class ApiError(Exception):
    """API 语义错误(ErrorCode/网络/HTTP/响应缺字段)——运行错(exit 1)。"""


# ---------- 凭证 / SSRF / 脱敏 ----------

def resolve_key(args, env=None):
    """--key > env BING_WMT_KEY;都没有 → CredentialError(指路,不发请求)。"""
    env = os.environ if env is None else env
    key = (getattr(args, "key", None) or "").strip() or (env.get(ENV_KEY) or "").strip()
    if not key:
        raise CredentialError(
            "未找到 Bing WMT API key:--key KEY 或 env %s\n%s" % (ENV_KEY, KEY_HOWTO))
    return key


def guard_bing(url):
    """端点守卫:仅 https + bing.com 域(含子域)。端点基址内置本不应有外部输入,
    守卫独立复查作纵深防御(防日后基址被改动引入任意 URL)。"""
    p = urllib.parse.urlsplit(url or "")
    host = (p.hostname or "").lower()
    if p.scheme != "https" or not host:
        raise GuardError("SSRF 守卫:仅允许 https 端点: %s" % url)
    if host != "bing.com" and not host.endswith(".bing.com"):
        raise GuardError("SSRF 守卫:端点域不在 bing.com 白名单: %s" % url)
    return True


def redact_key(s, key):
    """异常/诊断信息里绝不带 key 值(套件 redact 纪律)。"""
    if not key:
        return str(s)
    return str(s).replace(key, "<redacted-key>")


# ---------- WCF 日期 "/Date(ms±zzzz)/" → "YYYY-MM-DD" ----------

_WCF_DATE = re.compile(r"^/Date\((-?\d+)([+-]\d{4})?\)/$")


def parse_wcf_date(v):
    """Bing WCF 日期串("/Date(1316156400000-0700)/")→ UTC YYYY-MM-DD;
    已是数字/ISO 串原样容错;解析不出返回 ""(不猜)。"""
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc).date().isoformat()
    m = _WCF_DATE.match(str(v).strip())
    if m:
        ms = int(m.group(1))
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()
    s = str(v).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", s):        # 已是 ISO 形态,截日期部分
        return s[:10]
    return ""


# ---------- HTTP(唯一网络出口;测试打桩点) ----------

def _http_json(url, data=None, headers=None, timeout=DEFAULT_TIMEOUT):
    """GET(data=None)/POST(JSON body);返回解析后 dict(空响应体→{})。
    HTTPError 读 body 找 {"ErrorCode","Message"} 转 ApiError(WMT 的 4xx 带 JSON 错误体)。"""
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(FETCH_LIMIT)
    except urllib.error.HTTPError as e:
        raw = e.read(FETCH_LIMIT)
        try:
            body = json.loads(raw.decode("utf-8", "replace"))
        except (ValueError, AttributeError):
            body = {}
        msg = body.get("Message") if isinstance(body, dict) else None
        raise ApiError("HTTP %d: %s%s" % (
            e.code, msg or "(无错误详情)",
            "(GetUrlSubmissionStatus 等端点已于 2026-08-31 裁撤;检查方法名)"
            if e.code == 404 else ""))
    if not raw or not raw.strip():
        return {}
    return json.loads(raw.decode("utf-8", "replace"))


def api_call(method, key, params=None, body=None, timeout=DEFAULT_TIMEOUT):
    """单次 API 调用:GET(参数进查询串)/POST(JSON body);解包 "d" 并检查 ErrorCode。
    key 只进查询串;URLError 上抛给 main(网络不可达)。"""
    url = "%s/%s" % (API_BASE, method)
    guard_bing(url)
    q = {"apikey": key}
    q.update({k: v for k, v in (params or {}).items() if v is not None})
    full = url + "?" + urllib.parse.urlencode(q)
    headers = {"User-Agent": UA, "Accept": "application/json",
               "Content-Type": "application/json; charset=utf-8"}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    resp = _http_json(full, data=data, headers=headers, timeout=timeout)
    if isinstance(resp, dict) and "ErrorCode" in resp:      # 200 也可能带错误体(WCF 怪癖)
        raise ApiError("API 错误 ErrorCode=%s: %s" % (resp.get("ErrorCode"),
                                                      resp.get("Message", "")))
    return resp.get("d") if isinstance(resp, dict) else None


# ---------- 端点封装(薄:一次调用一个方法,不做链式魔法) ----------

def normalize_site(site):
    """--site 接受裸域名(补 https:// 前缀)或完整 URL(原样;须与 WMT 已验证形式一致,
    GetUserSites 可列精确值)。"""
    site = (site or "").strip()
    if not site:
        raise UsageError("--site 必填(裸域名即可,如 example.com)")
    if "://" in site:
        return site
    return "https://" + site


def get_quota(key, site, timeout=DEFAULT_TIMEOUT):
    """GetUrlSubmissionQuota → {"daily": int 剩余, "monthly": int 剩余}。
    d 容错 dict / 单元素 list 两形态。"""
    d = api_call("GetUrlSubmissionQuota", key, params={"siteUrl": site}, timeout=timeout)
    if isinstance(d, list):
        d = d[0] if d else {}
    if not isinstance(d, dict):
        raise ApiError("GetUrlSubmissionQuota 响应形态异常: %s" % json.dumps(d)[:200])
    return {"daily": int(d.get("DailyQuota") or 0),
            "monthly": int(d.get("MonthlyQuota") or 0)}


def get_url_info(key, site, url, timeout=DEFAULT_TIMEOUT):
    """GetUrlInfo → 单页收录/抓取状态 dict(UrlInfo:DiscoveryDate/LastCrawledDate/
    HttpStatus/DocumentSize/AnchorCount/IsPage/…);d 为 null/空 → None(无抓取记录)。"""
    d = api_call("GetUrlInfo", key, params={"siteUrl": site, "url": url}, timeout=timeout)
    return d if isinstance(d, dict) and d else None


def submit_urls(key, site, urls, timeout=DEFAULT_TIMEOUT, batch_meta=None):
    """提交 URL:1 个 → POST SubmitUrl;≥2 → SubmitUrlBatch 分批(≤500/调用)。
    返回 [{"method","count","ok"}];batch_meta 收每批原始响应(测试/--json 用)。
    空清单是调用方 bug(空 urlList 引擎返 400)——UsageError 拒绝。"""
    urls = list(urls)
    if not urls:
        raise UsageError("没有可提交的 URL(--url/--urls 至少给一个;空 urlList 引擎返 400)")
    results = []
    if len(urls) == 1:
        resp = api_call("SubmitUrl", key,
                        body={"siteUrl": site, "url": urls[0]}, timeout=timeout)
        if batch_meta is not None:
            batch_meta.append({"method": "SubmitUrl", "count": 1, "resp": resp})
        results.append({"method": "SubmitUrl", "count": 1, "ok": True})
        return results
    for i in range(0, len(urls), SUBMIT_BATCH_LIMIT):
        chunk = urls[i:i + SUBMIT_BATCH_LIMIT]
        resp = api_call("SubmitUrlBatch", key,
                        body={"siteUrl": site, "urlList": chunk}, timeout=timeout)
        if batch_meta is not None:
            batch_meta.append({"method": "SubmitUrlBatch", "count": len(chunk), "resp": resp})
        results.append({"method": "SubmitUrlBatch", "count": len(chunk), "ok": True})
    return results


FEED_OK_STATUSES = ("Success", "Pending")   # Pending=刚(重)交、还没读;其余如
                                            # "The page is not accessible" 都算读不到


def get_feeds(key, site, timeout=DEFAULT_TIMEOUT):
    """GetFeeds → [{"url","status","url_count","last_crawled","submitted"}];d 为 null → []。"""
    d = api_call("GetFeeds", key, params={"siteUrl": site}, timeout=timeout)
    rows = []
    for f in d if isinstance(d, list) else []:
        if not isinstance(f, dict):
            continue
        rows.append({"url": f.get("Url"), "status": f.get("Status") or "",
                     "url_count": int(f.get("UrlCount") or 0),
                     "last_crawled": parse_wcf_date(f.get("LastCrawled")),
                     "submitted": parse_wcf_date(f.get("Submitted"))})
    return rows


def submit_feed(key, site, feed_url, timeout=DEFAULT_TIMEOUT):
    """SubmitFeed(POST);重交已有的 sitemap 也走它,Bing 会把状态改成 Pending 再读。"""
    api_call("SubmitFeed", key, body={"siteUrl": site, "feedUrl": feed_url}, timeout=timeout)


def get_query_stats(key, site, timeout=DEFAULT_TIMEOUT):
    """GetQueryStats → 行列表(每行 Query/Impressions/Clicks/AvgImpressionPosition/
    AvgClickPosition/Date);空列表=数据还没有(不是 0,不是错)。"""
    d = api_call("GetQueryStats", key, params={"siteUrl": site}, timeout=timeout)
    if d is None:
        return []
    if not isinstance(d, list):
        raise ApiError("GetQueryStats 响应形态异常: %s" % json.dumps(d)[:200])
    return d


def get_page_query_stats(key, site, page, timeout=DEFAULT_TIMEOUT):
    """GetPageQueryStats(siteUrl, page)→ 该页的 QueryStats 行(learn.microsoft.com
    IWebmasterApi.GetPageQueryStats;官方 JSON 样例里 page 值是带引号的 JSON 字符串)。
    官方备注「The data will be updated every week」;空列表=还没有数据。"""
    d = api_call("GetPageQueryStats", key,
                 params={"siteUrl": site, "page": json.dumps(page)}, timeout=timeout)
    if d is None:
        return []
    if not isinstance(d, list):
        raise ApiError("GetPageQueryStats 响应形态异常: %s" % json.dumps(d)[:200])
    return d


def querystats_rows_to_csv_rows(rows):
    """QueryStats 行 → 契约行 [{Date,Query,Clicks,Impressions,CTR,Position}]:
    CTR 小数、Position=AvgImpressionPosition 2 位小数(-1/缺席哨兵值不留进 Position,
    空串呈现)。"""
    out = []
    for r in rows:
        try:
            clicks = int(r.get("Clicks") or 0)
            impressions = int(r.get("Impressions") or 0)
        except (TypeError, ValueError):
            clicks, impressions = 0, 0
        ctr = round(clicks / impressions, 4) if impressions > 0 else 0.0
        pos = r.get("AvgImpressionPosition")
        try:
            pos = round(float(pos), 2) if pos is not None else ""
        except (TypeError, ValueError):
            pos = ""
        out.append({"Date": parse_wcf_date(r.get("Date")),
                    "Query": r.get("Query") or "",
                    "Clicks": clicks, "Impressions": impressions,
                    "CTR": ctr, "Position": pos})
    return out


def write_csv(rows, out=None):
    """契约 CSV:列序 Date,Query,Clicks,Impressions,CTR,Position;--out 落盘,
    缺省返回串(stdout,可管道)。"""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    if out:
        with open(out, "w", newline="", encoding="utf-8") as f:
            f.write(buf.getvalue())
        return None
    return buf.getvalue()


def _fmt_urlinfo(u):
    """UrlInfo dict → 人读两行(状态行 + 指标行);None → 无记录行。"""
    if u is None:
        return "  (Bing 无该 URL 的抓取记录——未提交过或尚未被发现)"
    known_quirk = (int(u.get("HttpStatus") or 0) == 0
                   and int(u.get("DocumentSize") or 0) == 0)
    line1 = ("  发现 %s · 最后抓取 %s · HTTP %s · 文档 %s"
             % (parse_wcf_date(u.get("DiscoveryDate")) or "?",
                parse_wcf_date(u.get("LastCrawledDate")) or "?",
                u.get("HttpStatus") if u.get("HttpStatus") is not None else "?",
                _fmt_bytes(u.get("DocumentSize"))))
    line2 = ("  锚文本链接 %s · 子 URL %s · 是页面 %s"
             % (u.get("AnchorCount", "?"), u.get("TotalChildUrlCount", "?"),
                "yes" if u.get("IsPage") else "no"))
    if known_quirk:
        line2 += "\n  (HTTP 0/文档 0 是 Bing 该端点老怪癖;发现/最后抓取日期才可靠)"
    return line1 + "\n" + line2


def _fmt_bytes(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "?"
    if n <= 0:
        return "0(Bing 端点怪癖)" if n == 0 else str(int(n)) + " B"
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return ("%.0f %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024
    return "%.1f MB" % n


def load_urls_file(path):
    """一行一个 URL;# 注释与空行跳过(与 indexnow.py 同规则)。"""
    try:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise UsageError("读不了 --urls 文件 %s: %s" % (path, e))
    out, seen = [], set()
    for ln in lines:
        ln = ln.strip()
        if ln and not ln.startswith("#") and ln not in seen:
            seen.add(ln)
            out.append(ln)
    return out


# ---------- 子命令 ----------

def cmd_urlstatus(args):
    key = resolve_key(args)
    site = normalize_site(args.site)
    urls = args.url or []
    if not urls:
        raise UsageError("urlstatus 至少给一个 --url(查多个可重复传)")
    quota = get_quota(key, site, timeout=args.timeout)
    infos = [(u, get_url_info(key, site, u, timeout=args.timeout)) for u in urls]
    if args.json:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "site": site,
            "quota": {"daily_left": quota["daily"], "monthly_left": quota["monthly"]},
            "urls": [{"url": u, "known": info is not None,
                      "discovery_date": parse_wcf_date((info or {}).get("DiscoveryDate")) or None,
                      "last_crawled_date": parse_wcf_date((info or {}).get("LastCrawledDate")) or None,
                      "http_status": (info or {}).get("HttpStatus"),
                      "document_size_bytes": (info or {}).get("DocumentSize"),
                      "anchor_count": (info or {}).get("AnchorCount"),
                      "total_child_url_count": (info or {}).get("TotalChildUrlCount"),
                      "is_page": (info or {}).get("IsPage")} for u, info in infos],
        }, ensure_ascii=False, indent=1))
        return 0
    print("== URL 提交/收录状态(Bing WMT)==")
    print("site: %s" % site)
    print("提交配额剩余: 今日 %d · 本月 %d(GetUrlSubmissionQuota,读数为准不假设)"
          % (quota["daily"], quota["monthly"]))
    for u, info in infos:
        print(u)
        print(_fmt_urlinfo(info))
    return 0


def cmd_submit(args):
    key = resolve_key(args)
    site = normalize_site(args.site)
    urls = list(args.url or [])
    if args.urls:
        urls.extend(load_urls_file(args.urls))
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    if not uniq:
        raise UsageError("没有可提交的 URL(--url/--urls 至少给一个;空 urlList 引擎返 400)")
    quota = get_quota(key, site, timeout=args.timeout)      # 提交前读配额(读数为准)
    warn = ""
    if len(uniq) > quota["daily"]:
        warn = ("本批 %d URL 超过今日剩余配额 %d——Bing 可能只受理一部分;"
                "把余量留到明天再跑(状态文件记已提交的,别每天重发同一批)"
                % (len(uniq), quota["daily"]))
    batch_meta = []
    submit_urls(key, site, uniq, timeout=args.timeout, batch_meta=batch_meta)
    if args.json:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "ok": True, "site": site,
            "submitted": len(uniq), "quota_before": {"daily_left": quota["daily"],
                                                     "monthly_left": quota["monthly"]},
            "batches": [{"method": b["method"], "count": b["count"]} for b in batch_meta],
            "quota_warning": warn or None,
            "note": "重复提交不报错也不加速收录;配额实测约 100/日+1300/月,以读数为准",
        }, ensure_ascii=False, indent=1))
        return 0
    print("== Bing URL 提交 ==")
    print("site: %s" % site)
    print("提交配额剩余: 今日 %d · 本月 %d" % (quota["daily"], quota["monthly"]))
    if warn:
        print("[!] %s" % warn)
    for b in batch_meta:
        print("%s: %d URL 已提交" % (b["method"], b["count"]))
    print("共 %d URL 提交完成(受理≠已收录;收录看 urlstatus 的发现/抓取日期)"
          % len(uniq))
    return 0


def cmd_stats(args):
    key = resolve_key(args)
    site = normalize_site(args.site)
    rows = get_query_stats(key, site, timeout=args.timeout)
    csv_rows = querystats_rows_to_csv_rows(rows)
    url_info = None
    if args.url:
        url_info = get_url_info(key, site, args.url, timeout=args.timeout)
    if args.json:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "site": site,
            "query_stats_rows": len(rows), "csv_columns": CSV_COLUMNS,
            "rows": csv_rows,
            "url_info": ({"url": args.url, "known": url_info is not None,
                          "discovery_date": parse_wcf_date((url_info or {}).get("DiscoveryDate")) or None,
                          "last_crawled_date": parse_wcf_date((url_info or {}).get("LastCrawledDate")) or None,
                          "http_status": (url_info or {}).get("HttpStatus"),
                          "document_size_bytes": (url_info or {}).get("DocumentSize")}
                         if args.url else None),
            "note_empty": ("GetQueryStats 空列表=数据还没有(站点验证后数天才开始有,"
                           "验证前历史不回填),不是 0 也不是错" if not rows else None),
        }, ensure_ascii=False, indent=1))
        return 0
    # CSV 保持 stdout 纯净可管道:--url 的 GetUrlInfo 块走 stderr(或 --out 时走 stdout)
    def _info_block():
        lines = ["== 单页状态(GetUrlInfo)==", args.url]
        lines.append(_fmt_urlinfo(url_info))
        return "\n".join(lines)
    if not rows:
        sys.stderr.write("注: GetQueryStats 空列表=数据还没有(验证后数天起量,历史不回填)"
                         ",不是 0 也不是错;CSV 仍输出表头\n")
    if args.out:
        if args.url:
            print(_info_block())
        write_csv(csv_rows, out=args.out)
        print("已写 %d 行 × %d 列(%s)→ %s;可直接喂 gsc_mining --mode query"
              % (len(csv_rows), len(CSV_COLUMNS), ",".join(CSV_COLUMNS), args.out))
        return 0
    if args.url:
        sys.stderr.write(_info_block() + "\n")
    sys.stdout.write(write_csv(csv_rows))
    return 0


def cmd_pagequery(args):
    key = resolve_key(args)
    site = normalize_site(args.site)
    page = (args.page or "").strip()
    if not page:
        raise UsageError("--page 必填(完整页面 URL)")
    rows = get_page_query_stats(key, site, page, timeout=args.timeout)
    csv_rows = querystats_rows_to_csv_rows(rows)
    note = ("GetPageQueryStats 空列表=该页还没有数据(Bing 每周更新;流量小的页常为空),"
            "不是 0 也不是错" if not rows else None)
    if args.json:
        print(json.dumps({
            "schema_version": SCHEMA_VERSION, "site": site, "page": page,
            "query_stats_rows": len(rows), "csv_columns": CSV_COLUMNS,
            "rows": csv_rows, "note_empty": note,
        }, ensure_ascii=False, indent=1))
        return 0
    if note:
        sys.stderr.write("注: %s;CSV 仍输出表头\n" % note)
    if args.out:
        write_csv(csv_rows, out=args.out)
        print("已写 %d 行 × %d 列(%s)→ %s" % (len(csv_rows), len(CSV_COLUMNS),
                                              ",".join(CSV_COLUMNS), args.out))
        return 0
    sys.stdout.write(write_csv(csv_rows))
    return 0


def cmd_feeds(args):
    key = resolve_key(args)
    site = normalize_site(args.site)
    for u in args.submit:
        submit_feed(key, site, u, timeout=args.timeout)
    rows = get_feeds(key, site, timeout=args.timeout)
    bad = [r for r in rows if r["status"] not in FEED_OK_STATUSES]
    if args.json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "ok": not bad, "site": site,
                          "submitted": list(args.submit), "feeds": rows,
                          "not_readable": [r["url"] for r in bad]},
                         ensure_ascii=False, indent=1))
        return 3 if bad else 0
    print("== Bing sitemap 状态 ==")
    print("site: %s" % site)
    for u in args.submit:
        print("已提交: %s" % u)
    for r in rows:
        print("%-9s %6d 条  最近读取 %s  %s%s" % (
            "OK" if r["status"] in FEED_OK_STATUSES else "读不到", r["url_count"],
            r["last_crawled"] or "-", r["url"],
            "" if r["status"] == "Success" else "  [%s]" % r["status"]))
    if not rows:
        print("(Bing 侧没有登记任何 sitemap;用 --submit 交)")
    if bad:
        print("[!] %d 张 sitemap Bing 读不到:先用 bingbot UA 取一次确认现在能打开,"
              "再用 --submit 重交" % len(bad))
        return 3
    return 0


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--key", help="Bing WMT API key(优先级 --key > env %s)" % ENV_KEY)
    common.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="单请求超时秒数(默认 %d)" % DEFAULT_TIMEOUT)
    common.add_argument("--json", action="store_true", help="结构化输出(schema_version=1)")

    p = argparse.ArgumentParser(
        prog="bing_wmt.py",
        description="Bing Webmaster Tools API 薄客户端(免费需 key;R2-5)——"
                    "urlstatus 查 URL 提交/收录状态 / submit 提交 URL / stats 拉查询统计出 CSV。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="端点: https://ssl.bing.com/webmaster/api.svc/json/<方法>?apikey=…(SOAP/POX 已退役)\n"
               "stats CSV 列: Date,Query,Clicks,Impressions,CTR,Position(对齐 gsc_mining 契约;\n"
               "  CTR 小数;Position=AvgImpressionPosition,-1 点击哨兵值不用)\n"
               "配额: 实测约 100/日+1300/月(读 GetUrlSubmissionQuota 为准);SubmitUrlBatch ≤500/调用\n"
               "诚实边界: 流量数据验证后数天起量、历史不回填(空列表≠0≠错);\n"
               "  GetUrlSubmissionStatus 已于 2026-08-31 裁撤,urlstatus 走 GetUrlInfo+配额端点\n"
               "退出码: 0 正常 / 1 运行错(网络/HTTP/API/凭证缺失) / 2 用法错(参数/SSRF 拒)\n"
               "  / 3 feeds 有 sitemap 读不到")
    sub = p.add_subparsers(dest="cmd", metavar="{urlstatus,submit,stats,pagequery,feeds}")

    pu = sub.add_parser("urlstatus", parents=[common],
                        help="查 URL 提交/收录状态(GetUrlInfo+GetUrlSubmissionQuota)")
    pu.add_argument("--site", required=True, help="站点(裸域名或与 WMT 验证形式一致的 URL)")
    pu.add_argument("--url", action="append", default=[], metavar="U",
                    help="要查的 URL(可重复)")

    ps = sub.add_parser("submit", parents=[common],
                        help="提交 URL(SubmitUrl 单个 / SubmitUrlBatch 批量 ≤500)")
    ps.add_argument("--site", required=True, help="站点(裸域名或与 WMT 验证形式一致的 URL)")
    ps.add_argument("--url", action="append", default=[], metavar="U", help="要提交的 URL(可重复)")
    ps.add_argument("--urls", metavar="FILE", help="URL 清单文件(一行一个;# 注释跳过)")

    pt = sub.add_parser("stats", parents=[common],
                        help="GetQueryStats → CSV(Date,Query,Clicks,Impressions,CTR,Position)")
    pt.add_argument("--site", required=True, help="站点(裸域名或与 WMT 验证形式一致的 URL)")
    pt.add_argument("--url", help="附带查单个 URL 的 GetUrlInfo 状态")
    pt.add_argument("--out", metavar="F", help="CSV 落盘路径(缺省 CSV 走 stdout,可管道)")

    pp = sub.add_parser("pagequery", parents=[common],
                        help="GetPageQueryStats → 单页的查询 CSV(列同 stats;GSC 匿名查询多时的补充来源)")
    pp.add_argument("--site", required=True, help="站点(裸域名或与 WMT 验证形式一致的 URL)")
    pp.add_argument("--page", required=True, help="页面完整 URL")
    pp.add_argument("--out", metavar="F", help="CSV 落盘路径(缺省 CSV 走 stdout,可管道)")

    pf = sub.add_parser("feeds", parents=[common],
                        help="列 sitemap 状态(GetFeeds);--submit 先交或重交(SubmitFeed)")
    pf.add_argument("--site", required=True, help="站点(裸域名或与 WMT 验证形式一致的 URL)")
    pf.add_argument("--submit", action="append", default=[], metavar="SITEMAP",
                    help="要交或重交的 sitemap 完整 URL(可重复)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.cmd:
        build_parser().print_help(sys.stderr)
        return 2
    handlers = {"urlstatus": cmd_urlstatus, "submit": cmd_submit, "stats": cmd_stats,
                "pagequery": cmd_pagequery, "feeds": cmd_feeds}
    try:
        return handlers[args.cmd](args)
    except UsageError as e:
        sys.stderr.write("[用法] %s\n" % e)
        return 2
    except GuardError as e:
        sys.stderr.write("[拒] %s\n" % e)
        return 2
    except CredentialError as e:
        sys.stderr.write("[凭证] %s\n" % e)
        return 1
    except ApiError as e:
        key = (getattr(args, "key", None) or "").strip()
        sys.stderr.write("[API] %s\n" % redact_key(e, key or os.environ.get(ENV_KEY, "")))
        return 1
    except urllib.error.URLError as e:
        sys.stderr.write("[网络] %s(ssl.bing.com 需可直连)\n" % e)
        return 1
    except (ValueError, OSError) as e:
        sys.stderr.write("[错误] %s\n" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
