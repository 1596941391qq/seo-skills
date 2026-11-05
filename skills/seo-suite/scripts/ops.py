#!/usr/bin/env python3
"""ops.py — 长期运营的周 / 月运营单(RQ-229 第 2 批;stdlib only)。

一条命令串起每周该看的事,产出一屏能读完的运营单 `seo-ops/runs/<日期>/agenda.md`:
  1. 硬告警:站点不可达、robots 全站封、首页或关键页 noindex / 非 200、sitemap 失效、证书快到期、
     搜索爬虫被源站拒、监控库里没解决的 critical;没有就写「无」。
  2. 问题五态:和上一轮比,已解决 / 好转 / 仍在 / 变差 / 新增,每条带 URL;这轮没复查到的 URL 记「未复查」,
     不当成已解决。
  3. 到期复验:变更台账(ledger/changes.jsonl)里上线满 14、28 天的改动,用 GSC 逐页逐日数比前后。
  4. GEO:AI 引用周检的出现率变化、AI 爬虫访问量、AI 引荐(GA4)。
  5. 只推荐一件事,带证据;给了 --repo 时附源码候选路径。
  6. 覆盖率:sitemap 全量轻检多少页、按点击前 N 页深审多少页、没跑的检查和原因;覆盖不够不出分。
  7. 每个数写数据源(skill 自己拉的 GSC,还是外部数据包里的网关库)。

数据从哪来(都可缺,缺了在「覆盖」节写明):
  - 站点本身:sitemap、robots.txt、页面(轻检只读 <head>,深审走 site_audit.py)。
  - 外部数据包 `seo-ops/raw/external-*.json`(格式 seo-ops.external.v1,见 references/monitoring/ops-agenda.md):
    GSC / Bing 逐日总数、页面和查询两个窗口、逐页逐日、AI 抓取、GEO 引用周检。站点已有自己的数据管道时用它,
    skill 不重复拉。
  - skill 自己拉:GSC(gsc_api.py,服务账号)、GA4(ga4_api.py)。配了凭据才拉;两边都有 GSC 时抽 3 天对账。
  - 监控库 `seo-ops/monitor/`(monitor.py)。

安全边界:只读站点、只写 seo-ops/;不改站点代码,不推送,不部署。

用法:
  python3 ops.py weekly  [--ws seo-ops] [--site URL] [--external FILE] [--top-n 50] [--workers 8]
                         [--repo PATH] [--no-net] [--date YYYY-MM-DD] [--json]
  python3 ops.py monthly ...           # 周单 + 内容退役候选 + 30 条事实断言重抽提醒
  python3 ops.py change add --urls U1,U2 --summary "…" --rollback "git revert abc123" \
                 --expect clicks:up [--annotation "≤120 字"] [--at YYYY-MM-DD]
  python3 ops.py change list
  python3 ops.py ack [YYYY-MM-DD]      # 有人看过这一期运营单
  python3 ops.py notify [--dry-run]    # 有硬告警、或连续 2 期没人看,推 Telegram

退出码:0 正常;1 有硬告警;2 用法 / 工作区错误。
"""
import argparse
import concurrent.futures
import datetime as dt
import glob
import hashlib
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.robotparser

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import sitemap_audit as SM  # noqa: E402

PY = sys.executable or "python3"
EXTERNAL_SCHEMA = "seo-ops.external.v1"
SEV_RANK = {"CRITICAL": 3, "WARN": 2, "INFO": 1}
STATES = ("resolved", "improved", "persisting", "worse", "new")
STATE_ZH = {"resolved": "已解决", "improved": "好转", "persisting": "仍在", "worse": "变差", "new": "新增",
            "unchecked": "未复查"}
VERIFY_DAYS = (14, 28)
# 覆盖率门槛:轻检覆盖 sitemap ≥95%,深审 ≥ min(20, 有点击页数) 页且 ≥80% 的目标页 → 才出分
LIGHT_MIN, DEEP_MIN_PAGES, DEEP_MIN_RATIO = 0.95, 20, 0.8
SEARCH_BOTS = ("Googlebot", "bingbot", "Applebot", "YandexBot", "Baiduspider")
CERT_WARN_DAYS = 14
ANNOTATION_MAX = 120
RETRY_PAUSES = (15, 45)          # 秒:两轮重试前各停多久


class UsageError(Exception):
    pass


# ---------- 小工具 ----------

def today_str():
    return dt.date.today().isoformat()


def iso_now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def read_jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        continue
    except OSError:
        pass
    return out


def append_jsonl(path, row):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_yaml_flat(path):
    """project.yaml 是扁平 key: value(project.py 写的),这里只读顶层标量。"""
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
                if m and not line.startswith(" "):
                    out[m.group(1)] = m.group(2).strip("'\"")
    except OSError:
        pass
    return out


def host_of(url):
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def same_site(url, site_host):
    h = host_of(url)
    bare = site_host[4:] if site_host.startswith("www.") else site_host
    return h == site_host or h == bare or h == "www." + bare


def norm(url):
    return SM.norm_url(url)


def pct(a, b):
    return (a / b) if b else 0.0


def fmt_delta(cur, prev):
    if prev == 0:
        return "%s(上期 0)" % cur
    return "%s(%+.0f%%)" % (cur, (cur - prev) * 100.0 / prev)


def template_of(message):
    return re.sub(r"\d+(?:\.\d+)?", "N", message or "").strip()


def fingerprint(area, url, message):
    raw = "%s|%s|%s" % (area, norm(url), template_of(message))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


# ---------- 工作区 ----------

def resolve_ws(ws):
    if ws:
        if not os.path.isfile(os.path.join(ws, "project.yaml")):
            raise UsageError("%s 里没有 project.yaml;先跑 project.py init --site URL" % ws)
        return ws
    if os.path.isfile(os.path.join("seo-ops", "project.yaml")):
        return "seo-ops"
    raise UsageError("当前目录没有 seo-ops/;先跑 project.py init --site URL(旧版状态用 project.py migrate)")


def latest_external(ws, explicit=None):
    if explicit:
        data = read_json(explicit)
        if not data or data.get("schema") != EXTERNAL_SCHEMA:
            raise UsageError("%s 不是 %s 格式的外部数据包" % (explicit, EXTERNAL_SCHEMA))
        return explicit, data
    files = sorted(glob.glob(os.path.join(ws, "raw", "external-*.json")))
    for path in reversed(files):
        data = read_json(path)
        if data and data.get("schema") == EXTERNAL_SCHEMA:
            return path, data
    return None, None


def previous_run(ws, date):
    runs = sorted(d for d in glob.glob(os.path.join(ws, "runs", "*", "issues.json"))
                  if os.path.basename(os.path.dirname(d)) < date)
    return os.path.dirname(runs[-1]) if runs else None


# ---------- 1. 轻检:sitemap 全量 + 有点击的页 ----------

def collect_locs(site, timeout, notes):
    """robots.txt 声明的 sitemap(没有就 /sitemap.xml),index 展开两层,全量不抽样。"""
    parts = urllib.parse.urlsplit(site)
    origin = "%s://%s" % (parts.scheme, parts.netloc)
    declared = SM.robots_sitemaps(origin, timeout)
    queue = list(declared) or [origin + "/sitemap.xml"]
    locs, seen, errors = [], set(), []
    depth = {u: 0 for u in queue}
    while queue:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        try:
            kind, urls, children, _ = SM.fetch_sitemap(sm, timeout)
        except Exception as e:  # noqa: BLE001 — 失败原样记下,算硬告警的证据
            errors.append("%s: %s" % (sm, e))
            continue
        if kind == "urlset":
            locs.extend(u["loc"] if isinstance(u, dict) else u for u in urls)
        elif kind == "sitemapindex":
            if depth[sm] >= 2:
                notes.append("sitemap 嵌套超过两层,没再展开:%s" % sm)
                continue
            for c in children:
                depth.setdefault(c, depth[sm] + 1)
                queue.append(c)
        else:
            errors.append("%s: 不是 sitemap(%s)" % (sm, kind))
    return locs, errors, len(seen)


def check_one(url, timeout):
    row = {"url": url}
    try:
        status, headers, body = SM.fetch(url, timeout=timeout, max_bytes=262144)
    except Exception as e:  # noqa: BLE001
        row.update(status=0, error=str(e)[:200])
        return row
    row["status"] = status
    if 300 <= status < 400 and headers is not None:
        row["location"] = urllib.parse.urljoin(url, headers.get("Location") or "")
    if status == 200:
        xr = (headers.get("X-Robots-Tag") or "") if headers is not None else ""
        hp = SM.HeadParser()
        try:
            hp.feed(SM.decode(body, headers))
        except Exception:  # noqa: BLE001
            pass
        robots = " ".join(hp.meta_robots + [xr]).lower()
        row["noindex"] = "noindex" in robots
        if hp.canonical:
            canon = urllib.parse.urljoin(url, hp.canonical)
            row["canonical"] = canon
            row["canonical_self"] = norm(canon) == norm(url)
    return row


def light_check(site, extra_urls, workers, timeout, limit=0):
    t0 = time.time()
    notes = []
    locs, sm_errors, sm_files = collect_locs(site, timeout, notes)
    site_host = host_of(site)
    targets, seen, offsite = [], set(), 0
    for u in list(locs) + list(extra_urls):
        if not same_site(u, site_host):
            offsite += 1
            continue
        n = norm(u)
        if n not in seen:
            seen.add(n)
            targets.append(u)
    if limit and len(targets) > limit:
        notes.append("轻检限到前 %d 个 URL(共 %d)" % (limit, len(targets)))
        targets = targets[:limit]
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        for row in ex.map(lambda u: check_one(u, timeout), targets):
            rows.append(row)
    # 并发下没缓存的动态页会被源站拖慢:失败的先停一会儿,再逐个、加倍超时重试两轮;
    # 后面某轮成功的记 slow_under_load(抓取高峰时超时),都失败才算抓取失败
    failed = [i for i, r in enumerate(rows) if r.get("status") == 0 or r.get("status", 0) >= 500]
    for pause in (RETRY_PAUSES if failed else ()):
        if not failed:
            break
        time.sleep(pause)
        still = []
        for i in failed:
            row = check_one(rows[i]["url"], timeout * 2)
            if row.get("status") == 0 or row.get("status", 0) >= 500:
                still.append(i)
            else:
                row["slow_under_load"] = True
            rows[i] = dict(row, retried=True)
        failed = still
    retried = sum(1 for r in rows if r.get("retried"))
    if retried:
        notes.append("%d 个 URL 第一遍失败(超时或 5xx),停顿后重试仍失败 %d 个" % (retried, len(failed)))
    if offsite:
        notes.append("跳过 %d 个不在本站的 URL" % offsite)
    return {"sitemap_files": sm_files, "sitemap_errors": sm_errors, "locs_total": len(locs),
            "extra_urls": len(extra_urls), "targets": len(targets), "checked": len(rows),
            "seconds": round(time.time() - t0, 1), "notes": notes,
            "in_sitemap": sorted({norm(u) for u in locs}), "rows": rows}


def light_issues(light):
    out = []
    in_sm = set(light.get("in_sitemap") or [])
    for r in light["rows"]:
        url, st = r["url"], r.get("status", 0)
        listed = norm(url) in in_sm
        if st == 0:
            out.append(("http", url, "CRITICAL", "抓取失败:%s" % (r.get("error") or "")[:80]))
        elif r.get("slow_under_load"):
            out.append(("http", url, "INFO", "批量抓取时超时或 5xx,停顿后重试正常"))
        elif st >= 500:
            out.append(("http", url, "CRITICAL", "HTTP 5xx"))
        elif st == 403:
            out.append(("http", url, "CRITICAL", "HTTP 403"))
        elif st >= 400:
            out.append(("http", url, "CRITICAL" if listed else "WARN", "HTTP 4xx"))
        elif st >= 300 and listed:
            out.append(("http", url, "WARN", "sitemap 里的 URL 重定向"))
        if r.get("noindex"):
            out.append(("indexability", url, "WARN" if not listed else "CRITICAL",
                        "noindex" + ("(在 sitemap 里)" if listed else "")))
        if r.get("canonical") and not r.get("canonical_self") and listed:
            out.append(("canonical", url, "WARN", "canonical 指向别处(在 sitemap 里)"))
    return out


# ---------- 2. 深审:按点击前 N 页 ----------

def deep_audit(urls, market, run_dir):
    if not urls:
        return None, "没有要深审的页"
    cmd = [PY, "-I", os.path.join(BASE, "site_audit.py"), *urls, "--json"]
    if market:
        cmd += ["--market", market]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=1800)
    text = p.stdout
    start = text.find("{")
    try:
        audit = json.loads(text[start:]) if start >= 0 else None
    except ValueError:
        audit = None
    if not audit:
        return None, "site_audit 没给出 JSON(退出码 %s):%s" % (p.returncode, (p.stderr or "")[-200:])
    audit["seconds"] = round(time.time() - t0, 1)
    write_json(os.path.join(run_dir, "audit.json"), audit)
    return audit, None


def deep_issues(audit):
    out = []
    for url, res in (audit or {}).get("results", {}).items():
        for f in res.get("findings") or []:
            sev = (f.get("severity") or "").upper()
            if sev in SEV_RANK:
                out.append((f.get("area") or "?", url, sev, f.get("message") or ""))
    return out


def health(run_dir):
    path = os.path.join(run_dir, "audit.json")
    if not os.path.isfile(path):
        return None
    p = subprocess.run([PY, "-I", os.path.join(BASE, "health_score.py"), "--input", path, "--json"],
                       capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads(p.stdout)
    except ValueError:
        return None


# ---------- 3. 问题五态 ----------

def build_issues(raw, source):
    items = {}
    for area, url, sev, msg in raw:
        fp = fingerprint(area, url, msg)
        cur = items.get(fp)
        if cur is None or SEV_RANK[sev] > SEV_RANK[cur["severity"]]:
            items[fp] = {"fp": fp, "area": area, "url": url, "severity": sev, "message": msg,
                         "source": source}
    return items


def classify(prev, cur, prev_checked, cur_checked, ever_resolved):
    """prev / cur:{fp: item};*_checked:这一轮实际看过的 URL(归一后)。返回 [(state, item, prev_item)]。"""
    out = []
    for fp, item in cur.items():
        old = prev.get(fp)
        if old is None:
            state = "worse" if fp in ever_resolved else "new"      # 修好过又回来 = 变差(回归)
        elif SEV_RANK[item["severity"]] > SEV_RANK[old["severity"]]:
            state = "worse"
        elif SEV_RANK[item["severity"]] < SEV_RANK[old["severity"]]:
            state = "improved"
        else:
            state = "persisting"
        out.append((state, item, old))
    for fp, old in prev.items():
        if fp in cur:
            continue
        if norm(old["url"]) in cur_checked:
            out.append(("resolved", old, old))
        else:
            out.append(("unchecked", old, old))
    return out


# ---------- 4. 硬告警 ----------

def cert_days(host, timeout=10):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as s:
            cert = s.getpeercert()
    end = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
    return (end - dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)).days


def robots_blocks_home(site, timeout):
    parts = urllib.parse.urlsplit(site)
    rp = urllib.robotparser.RobotFileParser()
    try:
        st, headers, body = SM.fetch("%s://%s/robots.txt" % (parts.scheme, parts.netloc), timeout=timeout)
    except Exception:  # noqa: BLE001
        return None
    if st != 200:
        return False
    rp.parse(SM.decode(body, headers).splitlines())
    return not rp.can_fetch("Googlebot", "%s://%s/" % (parts.scheme, parts.netloc))


def monitor_criticals(ws):
    db = os.path.join(ws, "monitor", "monitor.db")
    if not os.path.isfile(db):
        return None
    import sqlite3
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute("SELECT code, key, message, ts FROM alerts WHERE resolved=0 AND level='critical' "
                            "ORDER BY id DESC LIMIT 20").fetchall()
    except sqlite3.Error:
        rows = []
    conn.close()
    return [{"code": r[0], "key": r[1], "message": r[2], "ts": r[3]} for r in rows]


def edge_blocking(ext):
    rows = ((ext or {}).get("sources", {}).get("ai_crawl") or {}).get("rows") or []
    if not rows:
        return None
    last7 = rows[-7:]
    out = []
    for bot in SEARCH_BOTS:
        tot = bad = 0
        for r in last7:
            for k, v in (r.get("status_by_bot") or {}).get(bot, {}).items():
                tot += v
                if k.startswith("4") or k.startswith("5"):
                    bad += v
        if tot >= 50 and bad / tot > 0.05:
            out.append({"bot": bot, "requests": tot, "errors": bad})
    return out


# ---------- 5. 数据:GSC、GA4、GEO ----------

def sum_days(rows, first, last, key):
    return sum(r.get(key, 0) for r in rows if first <= r["date"] <= last)


def gsc_summary(ext):
    src = (ext or {}).get("sources", {})
    tot = (src.get("gsc_totals") or {}).get("rows") or []
    if not tot:
        return None
    last = tot[-1]["date"]
    d = dt.date.fromisoformat(last)
    w = lambda a, b: ((d - dt.timedelta(days=a)).isoformat(), (d - dt.timedelta(days=b)).isoformat())  # noqa: E731
    cur7, prev7 = w(6, 0), w(13, 7)
    out = {"last_day": last, "source": (src.get("gsc_totals") or {}).get("source"),
           "clicks7": sum_days(tot, *cur7, "clicks"), "clicks7_prev": sum_days(tot, *prev7, "clicks"),
           "impr7": sum_days(tot, *cur7, "impressions"), "impr7_prev": sum_days(tot, *prev7, "impressions")}
    bing = (src.get("bing_totals") or {}).get("rows") or []
    if bing:
        bl = dt.date.fromisoformat(bing[-1]["date"])
        bw = lambda a, b: ((bl - dt.timedelta(days=a)).isoformat(), (bl - dt.timedelta(days=b)).isoformat())  # noqa: E731
        out["bing"] = {"last_day": bing[-1]["date"], "clicks7": sum_days(bing, *bw(6, 0), "clicks"),
                       "clicks7_prev": sum_days(bing, *bw(13, 7), "clicks"),
                       "source": (src.get("bing_totals") or {}).get("source")}
    return out


def market_of(url, prefixes):
    path = urllib.parse.urlsplit(url).path
    seg = path.strip("/").split("/", 1)[0].lower()
    return seg if seg in prefixes else None


def detect_prefixes(urls):
    segs = {}
    for u in urls:
        seg = urllib.parse.urlsplit(u).path.strip("/").split("/", 1)[0].lower()
        if re.fullmatch(r"[a-z]{2}(?:-[a-z0-9]{2,4})?", seg or ""):
            segs[seg] = segs.get(seg, 0) + 1
    return {s for s, n in segs.items() if n >= 3}


def default_sa(explicit=None):
    """--gsc-sa > env GSC_SA_FILE > ~/.config/seo-suite/gsc.json(和 gsc_api.py 同一顺序)。"""
    if explicit:
        return explicit
    if os.environ.get("GSC_SA_FILE"):
        return os.environ["GSC_SA_FILE"]
    cand = os.path.join(os.path.expanduser("~"), ".config", "seo-suite", "gsc.json")
    return cand if os.path.isfile(cand) else None


def gsc_crosscheck(ext, sa_path, site):
    """skill 自己用服务账号拉 3 天总数,和外部数据包里的总数比。"""
    tot = ((ext or {}).get("sources", {}).get("gsc_totals") or {}).get("rows") or []
    if not tot or not sa_path:
        return None, ("缺外部 GSC 总数" if not tot else "没配 GSC 服务账号(--gsc-sa、GSC_SA_FILE 或 ~/.config/seo-suite/gsc.json)")
    import gsc_api
    try:
        sa = gsc_api.load_sa(sa_path)
    except Exception as e:  # noqa: BLE001
        return None, "GSC 服务账号读不了:%s" % e
    by_day = {r["date"]: r for r in tot}
    last = dt.date.fromisoformat(tot[-1]["date"])
    days = [(last - dt.timedelta(days=k)).isoformat() for k in (0, 7, 14)]
    prop = site if site.endswith("/") else site + "/"
    out, err = [], ""
    for prop_try in ("sc-domain:" + host_of(site).removeprefix("www."), prop):
        try:
            rows = gsc_api.searchanalytics_query(sa, prop_try, min(days), max(days), ["date"])
            got = {r["keys"][0]: r for r in rows}
            for day in days:
                a, b = by_day.get(day, {}), got.get(day, {})
                out.append({"date": day, "property": prop_try,
                            "external_clicks": a.get("clicks"), "skill_clicks": int(b.get("clicks", 0)),
                            "external_impr": a.get("impressions"), "skill_impr": int(b.get("impressions", 0))})
            return out, None
        except Exception as e:  # noqa: BLE001
            err = str(e)
            continue
    return None, "GSC 实拉失败:%s" % err[:160]


def ga4_ai(run_dir, sa_path, prop):
    if not (sa_path and prop):
        return None, "没配 GA4(GA4_PROPERTY_ID + 服务账号)"
    p = subprocess.run([PY, "-I", os.path.join(BASE, "ga4_api.py"), "ai", "--property", prop,
                        "--sa", sa_path, "--days", "7", "--compare", "--json"],
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    try:
        data = json.loads(p.stdout)
    except ValueError:
        return None, "GA4 拉取失败:%s" % (p.stderr or p.stdout)[-200:]
    write_json(os.path.join(run_dir, "ga4.json"), data)
    return data, None


def geo_summary(ext):
    src = (ext or {}).get("sources", {})
    reps = (src.get("geo_citations") or {}).get("reports") or []
    crawl = (src.get("ai_crawl") or {}).get("rows") or []
    out = {"reports": [], "crawl": None}
    for r in reps:
        cur, prev = (r.get("metrics") or {}), ((r.get("previous") or {}).get("metrics") or {})
        out["reports"].append({"query_set": r.get("query_set"), "date": r.get("date"),
                               "hit_rate": cur.get("hit_rate"), "hits": cur.get("hits"), "queries": cur.get("queries"),
                               "prev_date": (r.get("previous") or {}).get("date"),
                               "prev_hit_rate": prev.get("hit_rate")})
    if crawl:
        cur, prev = crawl[-7:], crawl[-14:-7]
        bots = {}
        for r in cur:
            for k, v in (r.get("by_bot") or {}).items():
                bots[k] = bots.get(k, 0) + v
        out["crawl"] = {"last_day": crawl[-1]["date"], "total7": sum(r["total"] for r in cur),
                        "total7_prev": sum(r["total"] for r in prev),
                        "top": sorted(bots.items(), key=lambda kv: -kv[1])[:6],
                        "source": (src.get("ai_crawl") or {}).get("source")}
    return out


# ---------- 6. 到期复验 ----------

def due_verifications(ws, ext, today):
    changes = read_jsonl(os.path.join(ws, "ledger", "changes.jsonl"))
    done = {(v["change"], v["day"]) for v in read_jsonl(os.path.join(ws, "ledger", "verifications.jsonl"))}
    daily = ((ext or {}).get("sources", {}).get("gsc_page_daily") or {}).get("rows") or []
    out = []
    for ch in changes:
        at = dt.date.fromisoformat(ch["at"])
        for d in VERIFY_DAYS:
            if (ch["id"], d) in done or today < at + dt.timedelta(days=d):
                continue
            urls = {norm(u) for u in ch.get("urls") or []}
            before = (at - dt.timedelta(days=d)).isoformat(), (at - dt.timedelta(days=1)).isoformat()
            after = (at + dt.timedelta(days=1)).isoformat(), (at + dt.timedelta(days=d)).isoformat()
            rows = [r for r in daily if norm(r["page"]) in urls]
            have_days = {r["date"] for r in rows}
            if not rows or not any(before[0] <= x <= before[1] for x in have_days) \
                    or max(have_days) < after[1]:
                res = {"change": ch["id"], "day": d, "result": "数据不足",
                       "why": "外部数据包里没有这些页的前后逐日数(或 GSC 还没到 %s)" % after[1]}
            else:
                b = {k: sum_days(rows, *before, k) for k in ("clicks", "impressions")}
                a = {k: sum_days(rows, *after, k) for k in ("clicks", "impressions")}
                metric, _, direction = (ch.get("expect") or "clicks:up").partition(":")
                metric = "impressions" if metric.startswith("imp") else "clicks"
                moved = a[metric] - b[metric]
                ok = moved > 0 if direction != "down" else moved < 0
                res = {"change": ch["id"], "day": d, "before": b, "after": a, "metric": metric,
                       "result": "达到预期" if ok else "没达到预期", "window": {"before": before, "after": after}}
            res["summary"] = ch.get("summary")
            res["rollback"] = ch.get("rollback")
            out.append(res)
    return out


# ---------- 7. 交叉清单(例 5)与推荐 ----------

def five_lists(ext, light):
    pages = ((ext or {}).get("sources", {}).get("gsc_pages") or {}).get("rows") or []
    if not pages:
        return None
    by_url = {norm(r["url"]): r for r in light["rows"]} if light else {}
    lists = {"noindex": [], "4xx": [], "403": [], "3xx": [], "non_canonical": []}
    for p in pages:
        if p.get("clicks", 0) <= 0:
            continue
        r = by_url.get(norm(p["page"]))
        if not r:
            continue
        st = r.get("status", 0)
        row = {"url": p["page"], "clicks28": p["clicks"], "status": st}
        if st == 403:
            lists["403"].append(row)
        elif 400 <= st < 500:
            lists["4xx"].append(row)
        elif 300 <= st < 400:
            lists["3xx"].append(dict(row, location=r.get("location")))
        if r.get("noindex"):
            lists["noindex"].append(row)
        if r.get("canonical") and not r.get("canonical_self"):
            lists["non_canonical"].append(dict(row, canonical=r.get("canonical")))
    for v in lists.values():
        v.sort(key=lambda x: -x["clicks28"])
    return lists


def ctr_opportunity(ext):
    pages = ((ext or {}).get("sources", {}).get("gsc_pages") or {}).get("rows") or []
    cands = [p for p in pages if p.get("impressions", 0) >= 200 and pct(p.get("clicks", 0), p["impressions"]) < 0.01]
    cands.sort(key=lambda p: -p["impressions"])
    return cands[:5]


def source_hint(repo, url, rev=None):
    if not repo:
        return None
    mapper = os.path.join(BASE, "source_map.py")
    if not os.path.isfile(mapper):
        return None
    cmd = [PY, "-I", mapper, "--repo", repo, "--json", url] + (["--rev", rev] if rev else [])
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)
    try:
        return (json.loads(p.stdout) or {}).get("results", [{}])[0]
    except (ValueError, IndexError):
        return None


def recommend(hard, states, lists, ctr, geo, clicks_by_url, repo):
    """只挑一件:硬告警 > 有点击页上的变差/新增 CRITICAL > 交叉清单里点击最多的 > 高展示低点击 > GEO 掉。"""
    if hard:
        h = hard[0]
        return {"what": "先处理硬告警:%s" % h["title"], "why": h["evidence"], "url": h.get("url"),
                "source": h.get("source")}
    bad = [(clicks_by_url.get(norm(it["url"]), 0), st, it) for st, it, _ in states
           if st in ("worse", "new") and it["severity"] == "CRITICAL"]
    bad.sort(key=lambda x: -x[0])
    if bad and bad[0][0] > 0:
        c, st, it = bad[0]
        return {"what": "修 %s 的「%s」(%s)" % (it["url"], it["message"], STATE_ZH[st]),
                "why": "这页近 28 天 %d 次点击;问题级别 CRITICAL" % c, "url": it["url"], "source": it["source"]}
    if lists:
        flat = [(r["clicks28"], name, r) for name, rows in lists.items() for r in rows]
        flat.sort(key=lambda x: -x[0])
        if flat:
            c, name, r = flat[0]
            return {"what": "处理有点击的 %s 页:%s" % (name, r["url"]),
                    "why": "近 28 天 %d 次点击,抓取状态 %s" % (c, r["status"]), "url": r["url"],
                    "source": "GSC 页面 × 本周轻检"}
    if ctr:
        p = ctr[0]
        return {"what": "改写 %s 的标题和描述(展示多、点击少)" % p["page"],
                "why": "近 28 天展示 %d、点击 %d(CTR %.2f%%)" % (p["impressions"], p["clicks"],
                                                                 100 * pct(p["clicks"], p["impressions"])),
                "url": p["page"], "source": "GSC 页面窗口"}
    for r in (geo or {}).get("reports") or []:
        if r.get("prev_hit_rate") is not None and (r.get("hit_rate") or 0) < r["prev_hit_rate"]:
            return {"what": "查 AI 引用出现率下降(%s)" % r["query_set"],
                    "why": "%s → %s" % (r["prev_hit_rate"], r["hit_rate"]), "url": None, "source": "GEO 周检"}
    return {"what": "本周没有必须做的事;按内容计划推进", "why": "无硬告警、无变差问题、交叉清单为空", "url": None,
            "source": None}


# ---------- 运营单 ----------

def run_ops(args, kind):
    ws = resolve_ws(args.ws)
    proj = load_yaml_flat(os.path.join(ws, "project.yaml"))
    site = args.site or proj.get("site")
    if not site:
        raise UsageError("project.yaml 没有 site,也没给 --site")
    market = args.market or proj.get("market") or None
    date = args.date or today_str()
    run_dir = os.path.join(ws, "runs", date)
    os.makedirs(run_dir, exist_ok=True)
    t0 = time.time()
    cov = {"ran": [], "skipped": []}

    ext_path, ext = latest_external(ws, args.external)
    if ext:
        cov["ran"].append("外部数据包 %s(生成于 %s,来自 %s)" % (os.path.basename(ext_path), ext.get("generated_at"),
                                                           ext.get("producer", "?")))
    else:
        cov["skipped"].append("外部数据包:seo-ops/raw/ 下没有 %s 文件" % EXTERNAL_SCHEMA)

    gsc_pages = ((ext or {}).get("sources", {}).get("gsc_pages") or {}).get("rows") or []
    site_host = host_of(site)
    clicked = [p for p in gsc_pages if p.get("clicks", 0) > 0 and same_site(p["page"], site_host)]
    clicks_by_url = {norm(p["page"]): p.get("clicks", 0) for p in gsc_pages}

    light = None
    hard = []
    if args.no_net:
        cov["skipped"].append("轻检、深审、证书、robots:--no-net")
    else:
        light = light_check(site, [p["page"] for p in clicked], args.workers, args.timeout, args.light_limit)
        write_json(os.path.join(run_dir, "light.json"), light)
        cov["ran"].append("轻检 %d 个 URL(sitemap %d 条 + GSC 有点击的页,%d 个 sitemap 文件,%.0f 秒)"
                          % (light["checked"], light["locs_total"], light["sitemap_files"], light["seconds"]))
        if light["sitemap_errors"]:
            hard.append({"title": "sitemap 取不到或解析失败", "evidence": "; ".join(light["sitemap_errors"][:3]),
                         "source": "本周轻检"})
        elif light["locs_total"] == 0:
            hard.append({"title": "sitemap 是空的", "evidence": "0 条 loc", "source": "本周轻检"})
        try:
            if robots_blocks_home(site, args.timeout):
                hard.append({"title": "robots.txt 封了 Googlebot 抓首页", "evidence": "robotparser 判定 / 不可抓",
                             "source": "本周 robots.txt"})
        except Exception as e:  # noqa: BLE001
            cov["skipped"].append("robots 检查:%s" % e)
        try:
            days = cert_days(site_host, args.timeout)
            if days < CERT_WARN_DAYS:
                hard.append({"title": "证书 %d 天后到期" % days, "evidence": site_host, "source": "TLS 握手"})
        except Exception as e:  # noqa: BLE001
            hard.append({"title": "TLS 握手失败", "evidence": str(e)[:160], "source": "TLS 握手"})

    # 深审目标:首页 + 按点击前 N;没有 GSC 就取 sitemap 前 N(覆盖节写明)
    home = "%s://%s/" % (urllib.parse.urlsplit(site).scheme, urllib.parse.urlsplit(site).netloc)
    if clicked:
        deep_targets = [home] + [p["page"] for p in sorted(clicked, key=lambda p: -p["clicks"])]
        deep_basis = "按 GSC 点击前 %d 页" % args.top_n
    else:
        deep_targets = [home] + ([r["url"] for r in light["rows"]] if light else [])
        deep_basis = "没有 GSC 页面数据,取 sitemap 前 %d 页" % args.top_n
    seen, uniq = set(), []
    for u in deep_targets:
        if norm(u) not in seen:
            seen.add(norm(u))
            uniq.append(u)
    deep_targets = uniq[:args.top_n]
    audit = None
    if not args.no_net:
        audit, err = deep_audit(deep_targets, market, run_dir)
        if err:
            cov["skipped"].append("深审:%s" % err)
        else:
            cov["ran"].append("深审 %d 页(%s,%.0f 秒)" % (audit.get("audited", 0), deep_basis, audit["seconds"]))

    # 关键页:首页 + 点击前 10
    key_pages = {norm(u) for u in deep_targets[:11]}
    if light:
        for r in light["rows"]:
            n = norm(r["url"])
            if n in key_pages and r.get("status") not in (200, 301, 308):
                hard.append({"title": "关键页 %s 返回 %s" % (r["url"], r.get("status") or r.get("error")),
                             "evidence": "近 28 天点击 %d" % clicks_by_url.get(n, 0), "url": r["url"],
                             "source": "本周轻检"})
            if n in key_pages and r.get("noindex"):
                hard.append({"title": "关键页 %s 是 noindex" % r["url"], "evidence": "meta robots / X-Robots-Tag",
                             "url": r["url"], "source": "本周轻检"})
    blocked = edge_blocking(ext)
    if blocked is None:
        cov["skipped"].append("搜索爬虫被拒检查:外部数据包里没有 ai_crawl 状态码")
    for b in blocked or []:
        hard.append({"title": "%s 在源站被拒 %d/%d 次(近 7 天)" % (b["bot"], b["errors"], b["requests"]),
                     "evidence": "4xx+5xx 占比 %.0f%%" % (100 * b["errors"] / b["requests"]),
                     "source": "外部数据包 ai_crawl"})
    mon = monitor_criticals(ws)
    if mon is None:
        cov["skipped"].append("监控库:seo-ops/monitor/ 没有 monitor.db(没配 monitor.py,或新克隆尚未重建)")
    for a in mon or []:
        hard.append({"title": "监控 critical:%s" % a["code"], "evidence": "%s %s" % (a["key"], a["message"]),
                     "source": "monitor.db"})

    # 迁移保护:上一轮 sitemap 里有、这轮没了的 URL,有点击却不是 301/308 到 200
    prev_dir = previous_run(ws, date)
    if light and prev_dir:
        prev_light = read_json(os.path.join(prev_dir, "light.json")) or {}
        gone = set(prev_light.get("in_sitemap") or []) - set(light["in_sitemap"])
        by = {norm(r["url"]): r for r in light["rows"]}
        for n in sorted(gone):
            c = clicks_by_url.get(n, 0)
            r = by.get(n)
            if c > 0 and (not r or r.get("status") not in (301, 308)):
                hard.append({"title": "有点击的页从 sitemap 消失且没有永久重定向:%s" % n,
                             "evidence": "近 28 天 %d 次点击,现在 %s" % (c, (r or {}).get("status", "没复查")),
                             "url": n, "source": "sitemap 前后两轮对比"})

    # 问题五态
    cur_items = {}
    if light:
        cur_items.update(build_issues(light_issues(light), "轻检"))
    if audit:
        cur_items.update(build_issues(deep_issues(audit), "深审"))
    checked = set()
    if light:
        checked |= {norm(r["url"]) for r in light["rows"]}
    if audit:
        checked |= {norm(u) for u in audit.get("results", {})}
    prev_issues = read_json(os.path.join(prev_dir, "issues.json")) if prev_dir else None
    ledger_path = os.path.join(ws, "ledger", "issues.jsonl")
    ever_resolved = {e["fp"] for e in read_jsonl(ledger_path) if e.get("state") == "resolved"}
    if prev_issues:
        states = classify(prev_issues["items"], cur_items, set(prev_issues.get("checked") or []), checked,
                          ever_resolved)
    else:
        states = [("new", it, None) for it in cur_items.values()]
    if light or audit:
        write_json(os.path.join(run_dir, "issues.json"),
                   {"date": date, "checked": sorted(checked), "items": cur_items})
        for st, it, _ in states:
            if st != "persisting":
                append_jsonl(ledger_path, {"run": date, "fp": it["fp"], "state": st, "severity": it["severity"],
                                           "area": it["area"], "url": it["url"], "message": it["message"]})

    # 数据
    gsc = gsc_summary(ext)
    sa = default_sa(args.gsc_sa)
    cross, cross_err = (None, "--no-net") if args.no_net else gsc_crosscheck(ext, sa, site)
    if cross_err:
        cov["skipped"].append("GSC 两个来源对账:%s" % cross_err)
    ga4, ga4_err = (None, "--no-net") if args.no_net else ga4_ai(
        run_dir, args.ga4_sa or sa, args.ga4_property or os.environ.get("GA4_PROPERTY_ID") or proj.get("ga4_property"))
    if ga4_err:
        cov["skipped"].append("AI 引荐(GA4):%s" % ga4_err)
    geo = geo_summary(ext)
    if not geo["reports"]:
        cov["skipped"].append("AI 引用周检:外部数据包里没有 geo_citations")
    lists = five_lists(ext, light)
    if lists is None:
        cov["skipped"].append("流量 × 抓取交叉:缺 GSC 页面数据")
    ctr = ctr_opportunity(ext)
    verifs = due_verifications(ws, ext, dt.date.fromisoformat(date))
    for v in verifs:
        if v["result"] != "数据不足":
            append_jsonl(os.path.join(ws, "ledger", "verifications.jsonl"), dict(v, run=date))

    # 覆盖率门槛
    score = health(run_dir) if audit else None
    light_cov = pct(light["checked"], light["targets"]) if light else 0.0
    sm_cov = pct(len({norm(r["url"]) for r in light["rows"]} & set(light["in_sitemap"])),
                 len(light["in_sitemap"])) if light else 0.0
    deep_n = (audit or {}).get("audited", 0)
    deep_need = min(DEEP_MIN_PAGES, max(1, len(clicked))) if clicked else DEEP_MIN_PAGES
    deep_ratio = pct(deep_n, len(deep_targets))
    gate_ok = bool(light) and sm_cov >= LIGHT_MIN and deep_n >= deep_need and deep_ratio >= DEEP_MIN_RATIO
    gate = {"sitemap_coverage": round(sm_cov, 3), "light_coverage": round(light_cov, 3), "deep_pages": deep_n,
            "deep_needed": deep_need, "deep_ratio": round(deep_ratio, 3), "ok": gate_ok}

    # 市场切分
    prefixes = detect_prefixes([p["page"] for p in gsc_pages]) if gsc_pages else set()
    markets = {}
    root_market = market or "根路径"
    for p in gsc_pages:
        if not same_site(p["page"], site_host):
            continue
        m = markets.setdefault(market_of(p["page"], prefixes) or root_market, {"clicks": 0, "prev_clicks": 0,
                                                                  "impressions": 0, "prev_impressions": 0})
        for k in m:
            m[k] += p.get(k, 0)
    for st, it, _ in states:
        if st in ("new", "worse", "persisting"):
            m = markets.setdefault(market_of(it["url"], prefixes) or root_market, {"clicks": 0, "prev_clicks": 0,
                                                                     "impressions": 0, "prev_impressions": 0})
            m["open_issues"] = m.get("open_issues", 0) + 1

    rec = recommend(hard, states, lists, ctr, geo, clicks_by_url, args.repo)
    if rec.get("url"):
        hint = source_hint(args.repo, rec["url"], args.rev)
        if hint:
            rec["source_files"] = hint
    monthly = monthly_extras(ext) if kind == "monthly" else None

    elapsed = round(time.time() - t0, 1)
    agenda = {"kind": kind, "date": date, "site": site, "generated_at": iso_now(), "seconds": elapsed,
              "hard_alerts": hard, "states": [{"state": st, **it} for st, it, _ in states],
              "verifications": verifs, "gsc": gsc, "gsc_crosscheck": cross, "ga4": ga4, "geo": geo,
              "five_lists": lists, "ctr_opportunity": ctr, "recommendation": rec, "coverage": cov,
              "score_gate": gate, "score": (score or {}).get("main_score") if gate_ok else None,
              "markets": markets, "monthly": monthly, "external": ext_path, "first_run": not prev_issues}
    write_json(os.path.join(run_dir, "agenda.json"), agenda)
    md = render(agenda, score)
    with open(os.path.join(run_dir, "agenda.md"), "w", encoding="utf-8") as f:
        f.write(md)
    if args.json:
        print(json.dumps(agenda, ensure_ascii=False, indent=1))
    else:
        print(md)
        print("\n写到 %s" % os.path.join(run_dir, "agenda.md"))
    return 1 if hard else 0


def monthly_extras(ext):
    pages = ((ext or {}).get("sources", {}).get("gsc_pages") or {}).get("rows") or []
    win = ((ext or {}).get("sources", {}).get("gsc_pages") or {}).get("window") or {}
    zero = [p for p in pages if p.get("impressions", 0) > 0 and p.get("clicks", 0) == 0
            and p.get("prev_clicks", 0) == 0]
    zero.sort(key=lambda p: -p["impressions"])
    return {"prune_candidates": zero[:20], "prune_window": win,
            "prune_note": "候选 = 两个窗口都 0 点击但有展示;动手前跑 prune_gate.py 三查(入链、外链、排名词),"
                          "外链 > 0 或有排名词的不动",
            "fact_resample": "本月重抽 30 条事实断言(freshness.py --sample 30),错 ≤1 才算达标"}


# ---------- 渲染 ----------

def render(a, score):
    L = []
    L.append("# %s 运营单 · %s · %s" % ("月度" if a["kind"] == "monthly" else "每周", a["site"], a["date"]))
    L.append("")
    L.append("生成 %s,用时 %.0f 秒。只读站点、只写 seo-ops/;没有改代码、没有推送、没有部署。" % (a["generated_at"], a["seconds"]))
    L.append("")
    L.append("## 1. 硬告警")
    if a["hard_alerts"]:
        for h in a["hard_alerts"]:
            L.append("- **%s** — %s(来源:%s)" % (h["title"], h["evidence"], h["source"]))
    else:
        L.append("- 无")
    L.append("")
    rec = a["recommendation"]
    L.append("## 2. 本周只做这一件")
    L.append("- **%s**" % rec["what"])
    L.append("- 证据:%s(来源:%s)" % (rec["why"], rec.get("source") or "—"))
    sf = rec.get("source_files")
    if sf:
        cands = sf.get("candidates") or []
        L.append("- 源码:%s" % ("; ".join("%s(置信度 %.2f)" % (c["file"], c["confidence"]) for c in cands[:3])
                               or "没找到"))
    L.append("")
    L.append("## 3. 问题和上期比")
    if a.get("first_run"):
        L.append("- 首轮:没有上期可比,下面的「新增」就是基线(共 %d 条),下周起才有五态" % len(a["states"]))
    counts = {}
    for s in a["states"]:
        counts[s["state"]] = counts.get(s["state"], 0) + 1
    L.append("- " + " / ".join("%s %d" % (STATE_ZH[k], counts.get(k, 0))
                               for k in ("resolved", "improved", "persisting", "worse", "new", "unchecked")))
    for k in ("worse", "new", "improved", "resolved"):
        rows = [s for s in a["states"] if s["state"] == k and (k != "new" or s["severity"] == "CRITICAL")]
        rows.sort(key=lambda s: -SEV_RANK[s["severity"]])
        if not rows:
            continue
        extra = "(只列 CRITICAL)" if k == "new" else ""
        L.append("- %s%s:" % (STATE_ZH[k], extra))
        for s in rows[:8]:
            L.append("  - [%s] %s — %s" % (s["severity"], s["url"], s["message"]))
        if len(rows) > 8:
            L.append("  - …共 %d 条,见 issues.json" % len(rows))
    L.append("")
    L.append("## 4. 到期复验")
    if a["verifications"]:
        for v in a["verifications"]:
            if v["result"] == "数据不足":
                L.append("- %s 第 %d 天:数据不足 — %s" % (v["change"], v["day"], v["why"]))
            else:
                L.append("- %s 第 %d 天:**%s** — %s %s → %s(%s;回滚:`%s`)" % (
                    v["change"], v["day"], v["result"], v["metric"], v["before"][v["metric"]],
                    v["after"][v["metric"]], v.get("summary") or "", v.get("rollback") or "—"))
    else:
        L.append("- 无到期项")
    L.append("")
    L.append("## 5. 搜索与 AI 可见度")
    g = a.get("gsc")
    if g:
        L.append("- Google 近 7 天(到 %s):点击 %s,展示 %s。来源:%s" % (
            g["last_day"], fmt_delta(g["clicks7"], g["clicks7_prev"]), fmt_delta(g["impr7"], g["impr7_prev"]),
            g["source"]))
        if g.get("bing"):
            b = g["bing"]
            L.append("- Bing 近 7 天(到 %s):点击 %s。来源:%s" % (b["last_day"], fmt_delta(b["clicks7"], b["clicks7_prev"]),
                                                          b["source"]))
    if a.get("gsc_crosscheck"):
        diffs = ["%s 外部 %s / skill %s" % (r["date"], r["external_clicks"], r["skill_clicks"])
                 for r in a["gsc_crosscheck"]]
        L.append("- GSC 两个来源抽 3 天对账(点击):%s。属性 %s" % ("; ".join(diffs), a["gsc_crosscheck"][0]["property"]))
    geo = a.get("geo") or {}
    for r in geo.get("reports") or []:
        prev = ("上次 %s(%s)" % (r["prev_hit_rate"], r["prev_date"])) if r.get("prev_date") else "没有上期"
        L.append("- AI 引用(%s,%s):出现率 %s(%s/%s),%s。来源:外部数据包 GEO 引用检测(Perplexity)" % (
            r["query_set"], r["date"], r["hit_rate"], r["hits"], r["queries"], prev))
    c = geo.get("crawl")
    if c:
        L.append("- AI 爬虫近 7 天(到 %s):%s;最多:%s。来源:%s" % (
            c["last_day"], fmt_delta(c["total7"], c["total7_prev"]),
            "、".join("%s %d" % kv for kv in c["top"]), c["source"]))
    ga = a.get("ga4")
    if ga:
        L.append("- AI 引荐会话近 7 天:%s;按引擎:%s。来源:GA4 %s" % (
            fmt_delta(ga.get("ai_sessions", 0), ga.get("ai_sessions_prev", 0)),
            "、".join("%s %d" % (k, v) for k, v in (ga.get("by_engine") or {}).items()) or "无",
            ga.get("property")))
    if a.get("markets") and len(a["markets"]) > 1:
        L.append("- 按市场(近 28 天,GSC 页面行加总,不含匿名查询):" + ";".join(
            "%s 点击 %s、未结问题 %d" % (m, fmt_delta(v["clicks"], v["prev_clicks"]), v.get("open_issues", 0))
            for m, v in sorted(a["markets"].items())))
    L.append("")
    L.append("## 6. 有点击却有问题的页(流量 × 抓取)")
    fl = a.get("five_lists")
    if fl is None:
        L.append("- 跳过:缺 GSC")
    else:
        names = {"noindex": "noindex", "4xx": "4xx", "403": "403", "3xx": "3xx", "non_canonical": "非规范页"}
        L.append("- " + " / ".join("%s %d" % (names[k], len(v)) for k, v in fl.items()))
        for k, v in fl.items():
            for r in v[:3]:
                L.append("  - %s:%s(近 28 天 %d 次点击,抓取 %s)" % (names[k], r["url"], r["clicks28"], r["status"]))
    L.append("")
    if a.get("monthly"):
        mo = a["monthly"]
        L.append("## 月度")
        L.append("- 内容退役候选 %d 个(%s)" % (len(mo["prune_candidates"]), mo["prune_note"]))
        for p in mo["prune_candidates"][:5]:
            L.append("  - %s(展示 %d)" % (p["page"], p["impressions"]))
        L.append("- %s" % mo["fact_resample"])
        L.append("")
    L.append("## 7. 覆盖率和分数")
    gt = a["score_gate"]
    L.append("- sitemap 覆盖 %.0f%%,深审 %d 页(至少要 %d 页、≥%.0f%% 目标页)" % (
        100 * gt["sitemap_coverage"], gt["deep_pages"], gt["deep_needed"], 100 * DEEP_MIN_RATIO))
    if gt["ok"] and score:
        L.append("- 健康分 %s(%s,Ahrefs 口径:无 CRITICAL 的页占比;基于深审样本)" % (score.get("main_score"),
                                                                       score.get("band")))
    else:
        L.append("- **不出分**:覆盖率没过门槛")
    for x in a["coverage"]["ran"]:
        L.append("- 跑了:%s" % x)
    for x in a["coverage"]["skipped"]:
        L.append("- 没跑:%s" % x)
    L.append("")
    return "\n".join(L)


# ---------- 变更台账、已读、通知 ----------

def cmd_change(args):
    ws = resolve_ws(args.ws)
    path = os.path.join(ws, "ledger", "changes.jsonl")
    if args.action == "list":
        for ch in read_jsonl(path):
            print("%s  %s  %s  回滚:%s" % (ch["id"], ch["at"], ch.get("summary"), ch.get("rollback")))
        return 0
    if not (args.urls and args.summary and args.rollback):
        raise UsageError("change add 要 --urls、--summary、--rollback")
    ann = args.annotation or args.summary
    if len(ann) > ANNOTATION_MAX:
        raise UsageError("Search Console 标注最多 %d 字符,现在 %d" % (ANNOTATION_MAX, len(ann)))
    existing = read_jsonl(path)
    cid = "CHG-%03d" % (len(existing) + 1)
    at = args.at or today_str()
    row = {"id": cid, "at": at, "urls": [u.strip() for u in args.urls.split(",") if u.strip()],
           "summary": args.summary, "rollback": args.rollback, "expect": args.expect,
           "annotation": ann, "verify_on": [(dt.date.fromisoformat(at) + dt.timedelta(days=d)).isoformat()
                                            for d in VERIFY_DAYS], "recorded_at": iso_now()}
    append_jsonl(path, row)
    print("%s 记下了;复验日 %s;Search Console 标注:%s" % (cid, "、".join(row["verify_on"]), ann))
    return 0


def cmd_ack(args):
    ws = resolve_ws(args.ws)
    date = args.date or max((os.path.basename(d) for d in glob.glob(os.path.join(ws, "runs", "*"))
                             if os.path.isfile(os.path.join(d, "agenda.md"))), default=None)
    if not date:
        raise UsageError("还没有运营单")
    append_jsonl(os.path.join(ws, "ledger", "acks.jsonl"), {"run": date, "at": iso_now()})
    print("记下:%s 这一期已看" % date)
    return 0


def notify_decision(ws):
    runs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(ws, "runs", "*"))
                  if os.path.isfile(os.path.join(d, "agenda.json")))
    if not runs:
        return None, None
    acked = {a["run"] for a in read_jsonl(os.path.join(ws, "ledger", "acks.jsonl"))}
    latest = runs[-1]
    agenda = read_json(os.path.join(ws, "runs", latest, "agenda.json")) or {}
    if agenda.get("hard_alerts"):
        return latest, "硬告警 %d 条:%s" % (len(agenda["hard_alerts"]),
                                        ";".join(h["title"] for h in agenda["hard_alerts"][:3]))
    unread = [r for r in runs[-2:] if r not in acked]
    if len(runs) >= 2 and len(unread) == 2:
        return latest, "运营单连续 2 期没人看(%s)" % "、".join(unread)
    return latest, None


def cmd_notify(args):
    ws = resolve_ws(args.ws)
    latest, reason = notify_decision(ws)
    if not reason:
        print("不推:没有硬告警,也没有连续 2 期没人看")
        return 0
    sent_path = os.path.join(ws, "ledger", "notify.jsonl")
    if any(n.get("run") == latest and n.get("reason") == reason for n in read_jsonl(sent_path)):
        print("这一期同样的原因已经推过,不重复")
        return 0
    proj = load_yaml_flat(os.path.join(ws, "project.yaml"))
    msg = "[seo-ops] %s %s\n%s\n运营单:seo-ops/runs/%s/agenda.md" % (proj.get("site", ""), latest, reason, latest)
    if args.dry_run:
        print("(dry-run)会推:\n" + msg)
        return 0
    import notify as N
    ch = N._build_channel("telegram", "telegram", {"env_token": "TELEGRAM_BOT_TOKEN", "env_chat": "TELEGRAM_CHAT_ID"}) \
        or N._build_channel("telegram", "telegram", {})
    if not ch:
        print("没配 Telegram(TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID 或 SEO_MONITOR_TG_TOKEN/SEO_MONITOR_TG_CHAT),不推")
        return 0
    status, _ = ch[1](msg)
    append_jsonl(sent_path, {"run": latest, "reason": reason, "at": iso_now(), "status": status})
    print("推了 Telegram(HTTP %s)" % status)
    return 0


# ---------- CLI ----------

def build_parser():
    p = argparse.ArgumentParser(prog="ops.py", description="长期运营的周 / 月运营单")
    sub = p.add_subparsers(dest="cmd")
    for kind in ("weekly", "monthly"):
        s = sub.add_parser(kind)
        s.add_argument("--ws", help="工作区,默认 ./seo-ops")
        s.add_argument("--site")
        s.add_argument("--market")
        s.add_argument("--external", help="外部数据包路径;默认取 seo-ops/raw/external-*.json 最新一份")
        s.add_argument("--top-n", type=int, default=50, help="深审页数(首页 + 按点击排序)")
        s.add_argument("--workers", type=int, default=4, help="轻检并发(默认 4;失败的停顿后逐个重试)")
        s.add_argument("--timeout", type=float, default=15.0)
        s.add_argument("--light-limit", type=int, default=0, help="轻检最多多少 URL(0 = 全部)")
        s.add_argument("--repo", help="站点源码仓库路径;给了就给推荐项附源码候选")
        s.add_argument("--rev", help="读仓库的哪个提交(如 origin/main;默认工作树)")
        s.add_argument("--gsc-sa", help="GSC 服务账号 JSON(默认 env GSC_SA_FILE)")
        s.add_argument("--ga4-sa", help="GA4 服务账号 JSON(默认同 GSC)")
        s.add_argument("--ga4-property", help="GA4 媒体资源 ID(默认 env GA4_PROPERTY_ID 或 project.yaml ga4_property)")
        s.add_argument("--no-net", action="store_true", help="不访问站点和 Google,只用已有数据")
        s.add_argument("--date", help="运营单日期(默认今天)")
        s.add_argument("--json", action="store_true")
    c = sub.add_parser("change")
    c.add_argument("action", choices=("add", "list"))
    c.add_argument("--ws")
    c.add_argument("--urls")
    c.add_argument("--summary")
    c.add_argument("--rollback")
    c.add_argument("--expect", default="clicks:up", help="metric:direction,如 clicks:up、impressions:up")
    c.add_argument("--annotation", help="Search Console 标注文本(≤120 字符;默认用 summary)")
    c.add_argument("--at", help="上线日期 YYYY-MM-DD(默认今天)")
    a = sub.add_parser("ack")
    a.add_argument("date", nargs="?")
    a.add_argument("--ws")
    n = sub.add_parser("notify")
    n.add_argument("--ws")
    n.add_argument("--dry-run", action="store_true")
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    try:
        if args.cmd in ("weekly", "monthly"):
            return run_ops(args, args.cmd)
        if args.cmd == "change":
            return cmd_change(args)
        if args.cmd == "ack":
            return cmd_ack(args)
        if args.cmd == "notify":
            return cmd_notify(args)
        p.print_help()
        return 2
    except UsageError as e:
        sys.stderr.write("ops.py: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
