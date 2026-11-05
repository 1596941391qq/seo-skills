#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sitemap_audit.py — Sitemap 六坏桶审计 + lastmod 三判定 (仅标准库).

用法:
  python3 sitemap_audit.py https://example.com
  python3 sitemap_audit.py https://example.com/sitemap.xml --check-limit 20
  python3 sitemap_audit.py https://example.com --must-include https://example.com/pricing

规则摘要:
  * 入口 URL 不以 .xml/.gz 结尾时自动请求 {origin}/sitemap.xml; 支持 sitemapindex 递归 1 层
    (子节点若仍是 index, 提示不再下钻)
  * 六坏桶:
      桶1 非200      : loc 返回 4xx/5xx 或抓取失败
      桶2 3xx重定向  : loc 返回 301/302/303/307/308 (sitemap 中不应有重定向)
      桶3 noindex    : meta robots 或 x-robots-tag 含 noindex
      桶4 canonical他指: <link rel=canonical> 规范化后 != 自身 URL
      桶5 robots屏蔽 : robots.txt 按 Googlebot 判定 can_fetch() = False
      桶6 参数重复   : 同一 path 不同 query 的多组 URL
  * lastmod 三判定:
      Coverage     = 有 lastmod 条目占比 (期望 1.0)
      Freshness    = 最新 lastmod 距今 <= 30 天
      Truthfulness = 最大"单日簇"占比 > 50% 且该日 == 今天 -> 疑似构建期伪造
  * 规模提示: 单文件 > 50,000 URL 或 > 50MB 超出 Google 单 sitemap 上限, 建议拆分
  * 逐条抓取检查范围: 默认 loc ≤500 全查, 超过按位置均匀抽 500 个(含首尾); --check-limit N
    按位置均匀抽 N 个, 0=全部; 输出 [范围] 行写明查了几条、共几条、是否抽样.
    参数重复与 lastmod 统计始终基于全量 loc
  * sitemap URL 返回 HTML 页面(被重定向到首页、SPA 页面壳等)报「sitemap 文件不是 sitemap
    (软 404)」并计入坏桶(退出码 1), 不当输入错误退出
  * --hreflang: 全部 loc 的 hreflang 互指检查(口径: Google localized-versions 文档)。
    数据源: sitemap 的 <xhtml:link rel="alternate" hreflang> 优先; sitemap 没有注解时
    改读各 loc 页面 <head> 的 <link rel="alternate" hreflang>(受 --hreflang-limit 限制)。
      [hreflang 语言码非法]  语言码校验复用 hreflang_cluster.check_lang(es-419 等不支持)
      [hreflang 非完整 URL]  href 须含 https:// 的完整 URL
      [hreflang 缺自引用]    每个版本须列出自身
      [hreflang 互指缺失]    A 指 B、B 有注解却没指回 A——只有这一对被忽略
      [hreflang 同码多址]    同一页同一语言码指向不同 URL
      [hreflang 目标不在 sitemap] 无法用 sitemap 核对回指(提示, 不计入退出码)
      [hreflang 缺 x-default] 可选的兜底版本(提示, 不计入退出码)
    前五项任一非空 -> 退出码 1

退出码: 六坏桶任一非空、sitemap 返回 HTML、--must-include 有缺失或 --hreflang 硬问题非空 -> 1;
sitemap 不可达(4xx/5xx/网络)/XML 不可解析 -> 2; 正常 0.
"""
from __future__ import annotations

import argparse
import time
import re
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I 不把脚本目录放进 sys.path
from hreflang_cluster import check_lang  # 语言码校验唯一实现(Google localized-versions 口径)

UA = "Mozilla/5.0 (compatible; SEOSkill-SitemapAudit/1.0)"
FIFTY_MB = 50 * 1024 * 1024
FIFTY_K = 50000
DEFAULT_CHECK_CAP = 500   # 默认逐条检查上限:≤500 条全查,超过按位置均匀抽 500 条(本套件口径,写进输出)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """禁用自动跟随重定向, 以便把 3xx 本身当作审计结果."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def iri_to_uri(url):
    """非 ASCII 路径/参数(如 zenn 的 /topics/日本語)按 UTF-8 百分号编码,已有的 %XX 保留。
    不转码时 urllib 抛 UnicodeEncodeError,11-05 留出站把 10 条 200 的页记成「抓取失败」(同 site_crawl 的修法)。"""
    try:
        p = urllib.parse.urlsplit(url)
        host = p.netloc.encode("idna").decode("ascii") if not p.netloc.isascii() else p.netloc
    except (ValueError, UnicodeError):
        return url
    path = urllib.parse.quote(p.path, safe="/%:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(p.query, safe="=&%:@!$'()*+,;/?-._~")
    return urllib.parse.urlunsplit((p.scheme, host, path, query, ""))


def fetch(url, timeout=10.0, max_bytes=5_000_000):
    """GET 且不跟随重定向. 返回 (status, headers, body_bytes); 网络层异常向上抛."""
    req = urllib.request.Request(iri_to_uri(url), headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return resp.status, resp.headers, resp.read(max_bytes)
    except urllib.error.HTTPError as e:
        try:
            body = e.read(65536)
        except Exception:
            body = b""
        return e.code, getattr(e, "headers", None), body


def decode(body, headers):
    """按 Content-Type / meta charset / 常见兜底顺序解码字节流."""
    charset = None
    ct = ""
    try:
        ct = headers.get("Content-Type") or "" if headers else ""
    except Exception:
        ct = ""
    if ct:
        m = re.search(r"charset=([\w\-]+)", ct, re.I)
        if m:
            charset = m.group(1)
    if not charset and body:
        m = re.search(rb'charset=["\']?([\w\-]+)', body[:4096], re.I)
        if m:
            charset = m.group(1).decode("ascii", "replace")
    for enc in (charset, "utf-8", "gb18030", "latin-1"):
        if not enc:
            continue
        try:
            return body.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", "replace")


class HeadParser(HTMLParser):
    """仅提取 meta robots 与 link rel=canonical."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta_robots = []
        self.canonical = None
        self.alternates = []       # [(hreflang, href)]:<link rel=alternate hreflang>

    def handle_starttag(self, tag, attrs):
        try:
            a = {k.lower(): (v or "") for k, v in attrs}
            if tag == "meta" and a.get("name", "").lower() == "robots":
                self.meta_robots.append(a.get("content", ""))
            elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
                if a.get("href") and not self.canonical:
                    self.canonical = a["href"]
            elif (tag == "link" and "alternate" in a.get("rel", "").lower().split()
                  and a.get("hreflang")):
                self.alternates.append((a["hreflang"].strip(), a.get("href", "").strip()))
        except Exception:
            pass


def norm_url(u, base=None):
    """规范化 URL: 补 base, 小写 scheme/host, 去默认端口/fragment, 排序 query."""
    try:
        if base and not urllib.parse.urlsplit(u).scheme:
            u = urllib.parse.urljoin(base, u)
        p = urllib.parse.urlsplit(u)
        netloc = p.netloc.lower()
        try:
            if (p.scheme == "https" and p.port == 443) or (p.scheme == "http" and p.port == 80):
                netloc = (p.hostname or p.netloc).lower()
        except ValueError:
            pass
        q = "&".join(sorted(p.query.split("&"))) if p.query else ""
        return urllib.parse.urlunsplit((p.scheme.lower(), netloc, p.path or "/", q, ""))
    except ValueError:
        return u


def parse_lastmod(value):
    """解析 W3C/Dublin Core 常见 lastmod 格式, 失败返回 None."""
    if not value:
        return None
    v = value.strip()
    v = re.sub(r"[Zz]$", "+0000", v)
    v = re.sub(r"\.(\d{1,6})\d*", lambda m: "." + m.group(1), v)
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M%z"):   # 带毫秒(buttondown「…T00:00:00.000Z」)、W3C 只到分钟
        try:
            return datetime.strptime(v, fmt)
        except ValueError:
            continue
    return None


LANG_PARAMS = {"locale", "lang", "hl", "language", "lng", "lc"}


def _drop_lang_params(query):
    return "&".join(sorted(kv for kv in query.split("&") if kv and kv.split("=", 1)[0].lower() not in LANG_PARAMS))


_ROBOTS_CACHE = {}
_sleep = time.sleep          # 模块级可打桩(测试零真实延时)


def robots_for(url, timeout=10.0):
    """按 origin 缓存 robots.txt 判定器; 拉不到视为无限制(全放行)."""
    p = urllib.parse.urlsplit(url)
    origin = "{0}://{1}".format(p.scheme, p.netloc)
    if origin in _ROBOTS_CACHE:
        return _ROBOTS_CACHE[origin]
    rp = urllib.robotparser.RobotFileParser()
    lines = []
    try:
        status, headers, body = fetch(origin + "/robots.txt", timeout=timeout, max_bytes=1_000_000)
        if status == 200:
            lines = decode(body, headers).splitlines()
    except Exception:
        lines = []
    try:
        rp.parse(lines)
    except Exception:
        rp.parse([])
    _ROBOTS_CACHE[origin] = rp
    return rp


def robots_sitemaps(origin, timeout=10.0):
    """读 {origin}/robots.txt 的 Sitemap: 行,返回绝对 URL 列表(保序去重);拉不到返回 []。"""
    try:
        status, headers, body = fetch(origin + "/robots.txt", timeout=timeout, max_bytes=1_000_000)
    except Exception:
        return []
    if status != 200:
        return []
    out = []
    for line in decode(body, headers).splitlines():
        m = re.match(r"\s*sitemap\s*:\s*(\S+)", line, re.I)
        if m:
            u = urllib.parse.urljoin(origin + "/", m.group(1).strip())
            if u not in out:
                out.append(u)
    return out


def sample_children(children, k):
    """子 sitemap 超过 k 个时按位置均匀抽 k 个,首尾都在。index 常按时间排序(spiegel.de 从
    1947 年的归档排到当月),只取前 k 个会全是最旧的文件,Freshness 判成「过期」。"""
    n = len(children)
    if k <= 0:
        return []
    if n <= k:
        return list(children)
    if k == 1:
        return [children[-1]]
    idx = sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})
    return [children[i] for i in idx]


def ln(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def parse_text_sitemap(blob):
    """文本 sitemap:一行一个完整 URL(sitemaps.org「Text file」一节;Google 也收 .txt sitemap)。
    11-05 第三轮留出站 oschina:robots 声明的 sitemap.txt 被当成坏 XML。
    以 < 开头的(坏 XML)不算;非空行过半是 http(s) URL 才认,返回 URL 列表,否则 None。"""
    try:
        text = blob.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None
    if text.lstrip().startswith("<"):
        return None
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    urls = [x for x in lines if re.match(r"^https?://\S+$", x, re.I)]
    if not urls or len(urls) * 2 < len(lines):
        return None
    return urls


def parse_sitemap_bytes(blob):
    """解析 sitemap 字节流 -> (kind, [{loc,lastmod}], [child_sitemap_url])."""
    try:
        root = ET.fromstring(blob)
    except ET.ParseError as e:
        urls = parse_text_sitemap(blob)
        if urls is None:
            raise ValueError("XML 解析失败: {0}".format(e))
        return "urlset", [{"loc": u, "lastmod": "", "src": "text", "alts": []} for u in urls], []
    kind = ln(root.tag)
    if kind not in ("urlset", "sitemapindex"):
        return "unknown", [], []
    urls, children = [], []
    for node in root.iter():
        t = ln(node.tag)
        if t == "url":
            entry = {"loc": "", "lastmod": "", "src": kind, "alts": []}
            for c in node:
                ct = ln(c.tag)
                if ct == "loc" and c.text:
                    entry["loc"] = c.text.strip()
                elif ct == "lastmod" and c.text:
                    entry["lastmod"] = c.text.strip()
                elif (ct == "link" and "alternate" in (c.get("rel") or "").lower().split()
                      and c.get("hreflang")):
                    entry["alts"].append((c.get("hreflang").strip(), (c.get("href") or "").strip()))
            if entry["loc"]:
                urls.append(entry)
        elif t == "sitemap":
            for c in node:
                if ln(c.tag) == "loc" and c.text and c.text.strip():
                    children.append(c.text.strip())
    return kind, urls, children


class NotSitemap(Exception):
    """sitemap URL 返回的是 HTML 页面(常见:被重定向到首页,或 SPA 对任意路径都回 200 + 页面壳)。
    口径:sitemaps.org 协议要求 sitemap 是 XML(根元素 urlset/sitemapindex);Search Console
    Sitemaps 报告把这类文件记为 Unsupported format / Parsing error
    (https://support.google.com/webmasters/answer/7451001,2026-11-05 读取)。
    这是站点问题(软 404:URL 回 200 却没有 sitemap 内容),作为发现报告,不当输入错误退出。"""

    def __init__(self, url, final_url, status, ctype, nbytes, hops):
        self.url, self.final_url, self.status = url, final_url, status
        self.ctype, self.nbytes, self.hops = ctype, nbytes, hops
        super().__init__(self.describe())

    def describe(self):
        via = ""
        if self.hops:
            via = "经 {0} 次重定向到 {1},".format(len(self.hops), self.final_url)
        return ("{0} {1}返回 HTTP {2} 的 HTML 页面(Content-Type: {3},{4} 字节),不是 sitemap"
                "(软 404:搜索引擎读不到任何 URL)").format(
                    self.url, via, self.status, self.ctype or "未声明", self.nbytes)


_HTML_HEAD_RE = re.compile(rb"^\s*(?:\xef\xbb\xbf)?\s*(?:<!doctype\s+html|<html[\s>]|<head[\s>]|<body[\s>])", re.I)


def looks_like_html(body, ctype):
    """Content-Type 是 text/html,或正文开头就是 <!doctype html>/<html>/<head>/<body>。
    XML sitemap 开头是 <?xml 或 <urlset/<sitemapindex,两条都不会命中。"""
    if (ctype or "").split(";")[0].strip().lower() in ("text/html", "application/xhtml+xml"):
        return True
    return bool(_HTML_HEAD_RE.match(body[:2048] or b""))


def fetch_sitemap(url, timeout, max_hops=5):
    """抓 sitemap:跟随 ≤max_hops 次重定向(记录在 hops 里供备注);返回 HTML 页面时抛 NotSitemap。"""
    hops, cur = [], url
    for _ in range(max_hops + 1):
        status, headers, body = fetch(cur, timeout=timeout, max_bytes=FIFTY_MB + 1)
        loc = ""
        if 300 <= status < 400:
            try:
                loc = headers.get("Location") or "" if headers else ""
            except Exception:
                loc = ""
        if not loc:
            break
        nxt = urllib.parse.urljoin(cur, loc)
        hops.append((status, nxt))
        cur = nxt
    if status != 200:
        raise SitemapHTTPError(status)
    try:
        ctype = headers.get("Content-Type") or "" if headers else ""
    except Exception:
        ctype = ""
    if body[:2] == b"\x1f\x8b":
        import gzip
        body = gzip.decompress(body)
    elif looks_like_html(body, ctype):
        raise NotSitemap(url, cur, status, ctype, len(body), hops)
    kind, urls, children = parse_sitemap_bytes(body)
    if hops:
        _REDIRECT_NOTES.append("{0} 经 {1} 次重定向到 {2}".format(url, len(hops), cur))
    return kind, urls, children, len(body)


class SitemapHTTPError(IOError):
    """sitemap 文件本身回非 200。404/410 是站点问题(Search Console 记 Couldn't fetch),计入坏桶;
    403/429/5xx 可能是限流或临时故障,只记过程备注。"""

    def __init__(self, status):
        self.status = status
        super().__init__("HTTP {0}".format(status))


_REDIRECT_NOTES = []   # fetch_sitemap 记下的 sitemap 自身重定向(main 收进过程备注)


def hreflang_audit(alts_by_loc, sitemap_norms):
    """全站 hreflang 互指检查。alts_by_loc: {loc 原文: [(hreflang, href)]}(只含有注解的页)。
    返回 {标签: [行]};口径见模块 docstring 的 --hreflang 段。"""
    out = {k: [] for k in ("语言码非法", "非完整 URL", "缺自引用", "互指缺失", "同码多址",
                           "目标不在 sitemap", "缺 x-default")}
    targets = {}                       # norm(loc) → {norm(href)}
    locs_by_norm = {}
    for loc, alts in alts_by_loc.items():
        n = norm_url(loc)
        locs_by_norm[n] = loc
        tset, by_code, has_xd = set(), {}, False
        for code, href in alts:
            probs = check_lang(code)
            if probs:
                out["语言码非法"].append("{0}  hreflang=\"{1}\": {2}".format(loc, code, "; ".join(probs)))
            if code.strip().lower() == "x-default":
                has_xd = True
            sp = urllib.parse.urlsplit(href)
            if sp.scheme.lower() not in ("http", "https") or not sp.netloc:
                out["非完整 URL"].append("{0}  hreflang={1} href=\"{2}\"".format(loc, code, href))
                continue
            hn = norm_url(href)
            tset.add(hn)
            prev = by_code.setdefault(code.lower(), hn)
            if prev != hn:
                out["同码多址"].append("{0}  hreflang={1}: {2} / {3}".format(loc, code, prev, hn))
        targets[n] = tset
        if n not in tset:
            out["缺自引用"].append(loc)
        if not has_xd:
            out["缺 x-default"].append(loc)
    missing_targets = set()
    for n, tset in targets.items():
        for t in sorted(tset):
            if t == n:
                continue
            if t in targets:
                if n not in targets[t]:
                    out["互指缺失"].append("{0} -> {1}: 后者没有指回前者(只有这一对被 Google 忽略)".format(
                        locs_by_norm[n], locs_by_norm.get(t, t)))
            elif t not in missing_targets:
                missing_targets.add(t)
                out["目标不在 sitemap"].append("{0}  (被 {1} 引用;{2})".format(
                    t, locs_by_norm[n],
                    "在 sitemap 里但没有注解" if t in sitemap_norms else "无法用 sitemap 核对回指"))
    return out


HREFLANG_HARD = ("语言码非法", "非完整 URL", "缺自引用", "互指缺失", "同码多址")
HREFLANG_SOFT = ("目标不在 sitemap", "缺 x-default")


def print_bucket(no, name, items):
    print("\n[桶{0} {1}] 命中 {2}".format(no, name, len(items)))
    for s in items[:10]:
        print("   - {0}".format(s))
    if len(items) > 10:
        print("   ... 共 {0} 条, 仅示前 10".format(len(items)))


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="sitemap_audit.py",
        description="Sitemap 六坏桶审计 + lastmod 三判定 (stdlib only)")
    ap.add_argument("url", help="站点或 sitemap URL, 如 https://example.com")
    ap.add_argument("--check-limit", type=int, default=None, metavar="N",
                    help="逐条抓取检查的 loc 数: 默认 loc ≤{0} 时全查、超过时按位置均匀抽 {0} 个(含首尾); "
                         "N>0 按位置均匀抽 N 个; 0=全部. 输出里写明查了几条、共几条".format(DEFAULT_CHECK_CAP))
    ap.add_argument("--timeout", type=float, default=10.0, help="单请求超时秒数 (默认 10)")
    ap.add_argument("--delay", type=float, default=0.5,
                    help="逐条检查时两次请求的间隔秒数 (默认 0.5;robots.txt 的 crawl-delay 更大时用它)")
    ap.add_argument("--max-child", type=int, default=100,
                    help="sitemapindex 展开的子 sitemap 上限 (默认 100)")
    ap.add_argument("--must-include", action="append", default=[], metavar="URL",
                    help="必须出现在 sitemap 中的 URL, 可重复传入")
    ap.add_argument("--hreflang", action="store_true",
                    help="对全部 loc 做 hreflang 互指检查: 自引用/互指/x-default/目标是否在 sitemap/"
                         "语言码合法(复用 hreflang_cluster.check_lang)/完整 URL; 数据源优先 sitemap "
                         "xhtml:link, 没有则读页面 <head>")
    ap.add_argument("--hreflang-limit", type=int, default=0, metavar="N",
                    help="sitemap 无 hreflang 注解、改读页面时最多抓取的 loc 数 (默认 0=全部)")
    args = ap.parse_args(argv)
    del _REDIRECT_NOTES[:]

    target = args.url.strip()
    if not target.lower().startswith(("http://", "https://")):
        target = "https://" + target
    try:
        parts = urllib.parse.urlsplit(target)
        if not parts.netloc:
            raise ValueError("缺少主机名")
    except ValueError as e:
        print("[FATAL] URL 无法解析: {0}".format(e), file=sys.stderr)
        return 2
    origin = "{0}://{1}".format(parts.scheme, parts.netloc)
    path_l = (parts.path or "").lower()
    notes = []
    sitemap_bad = []          # sitemap 文件本身的问题(返回 HTML 等),计入坏桶总数
    entries = []
    total_bytes = 0
    oversize_files = 0
    over50k_files = 0

    if path_l.endswith(".xml") or path_l.endswith(".gz"):
        sitemap_url = target
        declared = []
    else:
        # 给的是站点:先读 robots.txt 的 Sitemap: 行(搜索引擎发现 sitemap 的标准入口),
        # 没有声明才回退 /sitemap.xml。多条声明按一个虚拟 index 展开。
        declared = robots_sitemaps(origin, args.timeout)
        sitemap_url = declared[0] if len(declared) == 1 else origin + "/sitemap.xml"
    if len(declared) > 1:
        kind, urls, children, nbytes = "sitemapindex", [], declared, 0
        sitemap_url = "{0}/robots.txt 声明的 {1} 个 sitemap".format(origin, len(declared))
        notes.append("入口来自 robots.txt 的 {0} 条 Sitemap 声明(按 index 展开)".format(len(declared)))
    else:
        if declared:
            notes.append("入口来自 robots.txt 的 Sitemap 声明: {0}".format(sitemap_url))
        try:
            kind, urls, children, nbytes = fetch_sitemap(sitemap_url, args.timeout)
        except NotSitemap as e:
            sitemap_bad.append(e.describe())
            kind, urls, children, nbytes = "html", [], [], e.nbytes
        except SitemapHTTPError as e:
            if not (declared and e.status in (404, 410)):
                print("[FATAL] 无法获取/解析 {0}: {1}".format(sitemap_url, e), file=sys.stderr)
                return 2
            # robots 声明的唯一 sitemap 打不开:是站点问题,记坏桶并退回 /sitemap.xml
            kind, urls, children, nbytes = "dead", [], [], 0
            dead_root = "{0} 返回 HTTP {1}".format(sitemap_url, e.status)
        except Exception as e:
            print("[FATAL] 无法获取/解析 {0}: {1}".format(sitemap_url, e), file=sys.stderr)
            return 2
    total_bytes += nbytes
    if nbytes > FIFTY_MB:
        oversize_files += 1
    sitemap_dead = []         # sitemap 文件回 404/410(Search Console 记 Couldn't fetch),计入坏桶总数
    if kind == "dead":
        sitemap_dead.append(dead_root)

    def take(url):
        """抓一个子 sitemap;成功返回 (kind, urls, children),失败记账后返回 None。"""
        nonlocal total_bytes, oversize_files
        try:
            k, u, c, n = fetch_sitemap(url, args.timeout)
        except NotSitemap as e:
            sitemap_bad.append(e.describe())
            return None
        except SitemapHTTPError as e:
            if e.status in (404, 410):
                sitemap_dead.append("{0} 返回 HTTP {1}".format(url, e.status))
            else:
                notes.append("子 sitemap 获取失败: {0}: {1}".format(url, e))
            return None
        except Exception as e:
            notes.append("子 sitemap 获取失败: {0}: {1}".format(url, e))
            return None
        total_bytes += n
        if n > FIFTY_MB:
            oversize_files += 1
        return k, u, c

    def add_urlset(u):
        nonlocal over50k_files
        entries.extend(u)
        if len(u) > FIFTY_K:                    # 上限按单个文件算,index 汇总数超 5 万是正常拆分
            over50k_files += 1

    def expand_index(children, label, nested):
        """展开一个 index 的子表;nested=True 时子表里的 index 再展开一层(入口是 robots 多条声明的虚拟 index)。"""
        picked = sample_children(children, args.max_child)
        if len(children) > args.max_child:
            notes.append("{0}含 {1} 个子 sitemap, 超过 --max-child={2}, 按位置均匀抽 {3} 个(含首尾;"
                         "lastmod 与 Freshness 只代表样本)".format(label, len(children), args.max_child, len(picked)))
        for child in picked:
            got = take(child)
            if not got:
                continue
            k2, u2, c2 = got
            if k2 == "urlset":
                add_urlset(u2)
            elif k2 == "sitemapindex" and nested:
                # 入口是 robots.txt 的多条声明(虚拟 index):声明里的 index 是真正的第一层,照常展开
                # (2026-10-24 spiegel.de:robots 声明的 sitemap.xml 是 23,707 个子表的 index)
                expand_index(c2, child + " ", False)
            elif k2 == "sitemapindex":
                notes.append("嵌套 sitemapindex 超过 1 层, 未继续下钻: {0} ({1} 个子)".format(child, len(c2)))

    if kind == "urlset":
        add_urlset(urls)
    elif kind == "sitemapindex":
        expand_index(children, "sitemapindex ", len(declared) > 1)
    fallback = origin + "/sitemap.xml"
    if declared and not entries and fallback not in declared:
        # 11-05 第三轮留出站 oschina:robots 声明 1,134 条几乎全 404,检查了 0 条却判 PASS;
        # 站点另有能打开的 /sitemap.xml。声明的全取不到条目时退回它,坏的声明照样计入坏桶。
        notes.append("robots.txt 声明的 sitemap 没取到任何条目, 退回检查 {0}".format(fallback))
        got = take(fallback)
        if got:
            k0, u0, c0 = got
            if k0 == "urlset":
                add_urlset(u0)
            elif k0 == "sitemapindex":
                expand_index(c0, fallback + " ", False)
    if kind not in ("urlset", "sitemapindex", "html", "dead"):
        print("[FATAL] 根元素不是 urlset/sitemapindex: {0}".format(sitemap_url), file=sys.stderr)
        return 2
    notes.extend(_REDIRECT_NOTES)

    # 去重 (保序)
    locs = []
    seen_norm = set()
    for e in entries:
        n = norm_url(e["loc"])
        if n in seen_norm:
            continue
        seen_norm.add(n)
        e["norm"] = n
        locs.append(e)
    total = len(locs)

    print("=" * 62)
    print("sitemap_audit | 入口: {0}".format(sitemap_url))
    print("sitemap 类型: {0} | 累计抓取 {1} 字节 | loc 总数: {2} (去重后)".format(
        kind, total_bytes, total))
    if over50k_files:
        print("[提示] {0} 个 sitemap 文件各超 50,000 条: 超出 Google 单个 sitemap 上限, 拆成更小的文件挂在 index 下".format(
            over50k_files))
    if oversize_files:
        print("[提示] 存在 > 50MB 的 sitemap 文件: 超出 Google 上限, 建议拆分")

    # ---------- lastmod 三判定 ----------
    now = datetime.now(timezone.utc)

    def to_utc(d):
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

    dated = []
    for e in locs:
        d = parse_lastmod(e.get("lastmod"))
        if d:
            dated.append(to_utc(d))
    coverage = (len(dated) / total) if total else 0.0
    latest = max(dated) if dated else None
    fresh_days = (now - latest).days if latest else None
    day_counter = Counter(d.date() for d in dated)
    top_day, top_count = (day_counter.most_common(1)[0] if day_counter else (None, 0))
    share = (top_count / total) if total else 0.0
    fabricated = total > 0 and share > 0.5 and top_day == now.date()

    print("\n---- lastmod 三判定 ----")
    print("Coverage     : {0:.3f}  (有 lastmod 条目占比, 期望 1.0)".format(coverage))
    if latest:
        print("Freshness    : 最新 lastmod {0} 距今 {1} 天 {2}".format(
            latest.isoformat()[:19], fresh_days, "(<=30 天, OK)" if fresh_days <= 30 else "(>30 天, 过期)"))
    else:
        print("Freshness    : 无任何可解析的 lastmod, 无法判定")
    print("Truthfulness : 最大单日簇 {0} 占 {1:.1%} {2}".format(
        top_day or "-", share,
        "-> 疑似构建期伪造(大量条目 lastmod=今天)" if fabricated else "(未触发伪造特征)"))

    # ---------- 六坏桶 ----------
    b_non200, b_redir, b_noindex, b_canonical, b_robots, b_dup = [], [], [], [], [], []
    b_limited = []      # 疑似被限流、未判定(不进问题桶,不影响退出码)

    # 逐条检查的范围:默认 ≤DEFAULT_CHECK_CAP 全查,超过按位置均匀抽样(含首尾);
    # 修前默认只查前 50 条——plausible 的 Google 验证文件 URL(302)排在第 160 条之后,漏报。
    if args.check_limit is None:
        cap, rule = DEFAULT_CHECK_CAP, "默认"
    elif args.check_limit <= 0:
        cap, rule = total, "--check-limit 0"
    else:
        cap, rule = args.check_limit, "--check-limit {0}".format(args.check_limit)
    to_check = sample_children(locs, cap) if cap < total else list(locs)
    sampled = len(to_check) < total
    checked = 0
    page_alts = {}                      # 六坏桶抓过的页:loc → <head> hreflang(--hreflang 复用)
    ok_seen, limited_run = False, 0
    for i, e in enumerate(to_check):
        u = e["loc"]
        if limited_run >= 5:                    # 连续 5 条退避后仍像限流:停下,剩下的不判
            b_limited.extend(x["loc"] for x in to_check[i:])
            notes.append("连续 5 条疑似被限流, 剩余 {0} 条未检查".format(len(to_check) - i))
            break
        if i:
            _sleep(args.delay)
        try:
            rp = robots_for(u, args.timeout)
            if not rp.can_fetch("Googlebot", u):
                b_robots.append(u)
                continue
        except Exception as err:
            notes.append("robots.txt 判定失败 {0}: {1}".format(u, err))
        try:
            status, headers, body = fetch(u, timeout=args.timeout)
            if status == 429 or (status in (403, 503) and ok_seen):
                # 11-05 第二轮留出站 qiita:原来不留间隔连抓 500 条,被限流后 403 全算「非 200」(列出的 10 条重抓全是 200)
                _sleep(max(10.0, args.delay * 10))
                status, headers, body = fetch(u, timeout=args.timeout)
                if status == 429 or (status in (403, 503) and ok_seen):
                    b_limited.append(u)
                    limited_run += 1
                    continue
        except Exception as err:
            b_non200.append("{0}  (抓取失败: {1})".format(u, type(err).__name__))
            continue
        limited_run = 0
        if 200 <= status < 300:
            ok_seen = True
        checked += 1
        if 300 <= status < 400:
            loc_hdr = ""
            try:
                loc_hdr = headers.get("Location") or "" if headers else ""
            except Exception:
                loc_hdr = ""
            b_redir.append("{0} -> {1} (HTTP {2})".format(u, loc_hdr, status))
            continue
        if status != 200:
            b_non200.append("{0}  (HTTP {1})".format(u, status))
            continue
        try:
            text = decode(body, headers)
            hp = HeadParser()
            hp.feed(text[:200000])
        except Exception as err:
            notes.append("HTML 解析失败 {0}: {1}".format(u, err))
            continue
        page_alts[u] = hp.alternates
        xr = []
        try:
            xr = headers.get_all("X-Robots-Tag") or [] if headers else []
        except Exception:
            xr = []
        noindex = any("noindex" in v.lower() for v in hp.meta_robots) or \
            any("noindex" in v.lower() for v in xr)
        if noindex:
            b_noindex.append(u)
            continue
        if hp.canonical:
            cnorm = norm_url(hp.canonical, base=u)
            if cnorm and cnorm != norm_url(u):
                b_canonical.append("{0} -> {1}".format(u, hp.canonical))
                continue

    # 桶6: 参数重复 (基于全量 loc)
    groups = {}
    for e in locs:
        try:
            sp = urllib.parse.urlsplit(e["loc"])
        except ValueError:
            continue
        key = (sp.scheme.lower(), sp.netloc.lower(), sp.path or "/")
        groups.setdefault(key, []).append(e["loc"])
    for _key, us in groups.items():
        # 只差语言参数(?locale=en、?hl=ja)的是译文,不是重复(11-05 留出站 zenn 抽 4 对:正文不同、canonical 指自己)
        qs = set(_drop_lang_params(urllib.parse.urlsplit(x).query) for x in us)
        if len(us) > 1 and len(qs) > 1:
            b_dup.extend(sorted(us))

    how = "按位置均匀抽样,含首尾" if sampled else "全量"
    if rule == "默认":
        how += ";默认 ≤{0} 条全查、超过抽 {0} 条,--check-limit 可调".format(DEFAULT_CHECK_CAP)
    else:
        how += ";" + rule
    if total or not (sitemap_bad or sitemap_dead):
        print("\n[范围] 逐条检查 {0}/{1} 个 loc({2});实际抓到 {3} 个,robots 屏蔽 {4} 个"
              "(参数重复与 lastmod 统计按全部 {1} 个)".format(len(to_check), total, how, checked, len(b_robots)))
    if sitemap_bad:
        print("\n[sitemap 文件不是 sitemap(软 404)] 命中 {0}".format(len(sitemap_bad)))
        for line in sitemap_bad[:10]:
            print("   - {0}".format(line))
    if sitemap_dead:
        print("\n[sitemap 文件打不开(404/410)] 命中 {0}".format(len(sitemap_dead)))
        for line in sitemap_dead[:10]:
            print("   - {0}".format(line))
        if len(sitemap_dead) > 10:
            print("   ... 共 {0} 条, 仅示前 10".format(len(sitemap_dead)))

    print("\n---- 六坏桶 ----")
    print_bucket(1, "非 200 / 抓取失败", b_non200)
    print_bucket(2, "3xx 重定向", b_redir)
    print_bucket(3, "noindex 页", b_noindex)
    print_bucket(4, "canonical 指向他址", b_canonical)
    print_bucket(5, "robots.txt 屏蔽 (Googlebot)", b_robots)
    print_bucket(6, "参数重复 URL (同 path 不同 query)", b_dup)
    if b_limited:
        print("\n[未判定:疑似被站点限流] {0} 条(429,或先 200 后 403/503,退避重试后仍是);加大 --delay 或错开同时跑的脚本再查".format(len(b_limited)))

    # ---------- 反向检查 ----------
    missing = []
    if args.must_include:
        print("\n---- --must-include 反向检查 ----")
        loc_norms = set(e["norm"] for e in locs)
        for m in args.must_include:
            ok = norm_url(m) in loc_norms
            print("   {0} {1}".format("OK  " if ok else "MISS", m))
            if not ok:
                missing.append(m)

    # ---------- hreflang 全站互指 ----------
    hl_hard = 0
    if args.hreflang:
        sm_alts = {e["loc"]: e["alts"] for e in locs if e.get("alts")}
        if sm_alts:
            src, alts_by_loc = "sitemap xhtml:link", sm_alts
        else:
            src = "页面 <head> link rel=alternate"
            alts_by_loc = {}
            cap = args.hreflang_limit if args.hreflang_limit > 0 else total
            for e in locs[:cap]:
                u = e["loc"]
                if u not in page_alts:
                    try:
                        status, headers, body = fetch(u, timeout=args.timeout)
                    except Exception as err:
                        notes.append("hreflang 抓取失败 {0}: {1}".format(u, type(err).__name__))
                        continue
                    if status != 200:
                        continue
                    hp = HeadParser()
                    try:
                        hp.feed(decode(body, headers)[:200000])
                    except Exception:
                        continue
                    page_alts[u] = hp.alternates
                if page_alts.get(u):
                    alts_by_loc[u] = page_alts[u]
            if cap < total:
                notes.append("hreflang 只读了前 {0}/{1} 个 loc 的页面 (--hreflang-limit)".format(cap, total))
        hres = hreflang_audit(alts_by_loc, set(e["norm"] for e in locs))
        print("\n---- hreflang 全站互指 (数据源: {0}; 有注解的 loc {1}/{2}) ----".format(
            src, len(alts_by_loc), total))
        for label in HREFLANG_HARD + HREFLANG_SOFT:
            items = hres[label]
            tag = "" if label in HREFLANG_HARD else " (提示, 不计入退出码)"
            print("\n[hreflang {0}] 命中 {1}{2}".format(label, len(items), tag))
            for line in items[:10]:
                print("   - {0}".format(line))
            if len(items) > 10:
                print("   ... 共 {0} 条, 仅示前 10".format(len(items)))
        hl_hard = sum(len(hres[k]) for k in HREFLANG_HARD)
        print("")

    if notes:
        print("\n---- 过程备注 ----")
        for n in notes[:20]:
            print("   * {0}".format(n))
        if len(notes) > 20:
            print("   ... 共 {0} 条".format(len(notes)))

    bad_total = sum(len(x) for x in (b_non200, b_redir, b_noindex, b_canonical, b_robots, b_dup,
                                     sitemap_bad, sitemap_dead))
    fail = bool(bad_total or missing or hl_hard)
    print("\n==== 结论: 坏桶命中 {0} 条, must-include 缺失 {1} 个{2} => {3} ====".format(
        bad_total, len(missing),
        ", hreflang 硬问题 {0} 条".format(hl_hard) if args.hreflang else "",
        "FAIL (退出码 1)" if fail else "PASS"))
    return 1 if fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[interrupted]", file=sys.stderr)
        sys.exit(130)
