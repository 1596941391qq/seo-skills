#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hreflang_cluster.py — hreflang 互指簇矩阵验证 (仅标准库).

用法:
  python3 hreflang_cluster.py https://example.com/en/ https://example.com/ja/ https://example.com/zh/

行为:
  * 每个 URL 拉取 HTML + HTTP 响应头, 提取全部 hreflang 声明:
      载体1: HTML  <head> 里 <link rel="alternate" hreflang=... href=...>
      载体2: HTTP  Link 头  <url>; rel="alternate"; hreflang="xx"
      载体3: XML   /sitemap.xml 里 <xhtml:link rel="alternate" hreflang=... href=...> (递归 1 层)
  * 未作为入参提供的 alternate 页面会自动补抓 (--max-extra 控制上限) 以验证回报
  * 检查列 (行=URL):
      条目数 / 自引用 / 语言码合法 / URL 绝对 / HTTP 200 / 双向回报 (return tag)
      语言码: ISO 639-1(拒绝 eng / jp / en_GB 下划线);可选 ISO 15924 文字码(zh-Hans、zh-Hant)
      和 ISO 3166-1 Alpha-2 区域码(en-GB、zh-Hans-US);x-default 放行。
      Google 不支持 3 位数字 UN 区域码(原文举例 es-419);EU / UN / UK 不起作用。
      值不区分大小写(区域码大写只是惯例,小写不判错)。
  * 回链: A 指向 B 而 B 不指回 A, Google 忽略这一对注解;其余互指的照常处理(不是整簇作废)。
  * 多载体: 同一 (hreflang, href) 同时出现在 HTML / HTTP 头 / sitemap —— 三者等价,同时用没有收益、
    更难维护,只作维护提示,不判错。
  出处: https://developers.google.com/search/docs/specialty/international/localized-versions
       (2026-09-21 更新,2026-10-18 核对)

退出码: 存在硬失败 (语言码非法 / 非绝对 URL / 非 200 / 回报缺失) -> 1, 否则 0.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; SEOSkill-HreflangCluster/1.0)"
CARRIERS = ("html-head", "http-link", "sitemap")
LINK_ITEM_RE = re.compile(r"<(?P<url>[^>]+)>(?P<params>[^<]*)")
RESERVED_REGIONS = frozenset({"EU", "UN", "UK", "EZ"})   # Google: EU、UN、UK 不起作用(UK 不是 ISO 3166-1 码,应为 GB)

# ISO 639-1 全集: 结构合法但不是语言码的常见错误 (jp/kr/cn/sc/ge...) 靠它拒绝
ISO639_1 = frozenset("""
aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr
cs cu cv cy da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu
gv ha he hi ho hr ht hu hy hz ia id ie ig ii ik io is it iu ja jv ka kg ki kj kk
kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms
mt my na nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro
ru rw sa sc sd se sg si sk sl sm sn so sq sr ss st su sv sw ta te tg th ti tk tl
tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi yo za zh zu
""".split())
# 常见误用 -> 正确写法提示
LANG_FIX = {"jp": "ja", "kr": "ko", "cn": "zh", "sc": "es", "ge": "de", "in": "id", "ch": "zh"}


class LinkGrab(HTMLParser):
    """提取 <link rel=alternate hreflang=...>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.entries = []

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        try:
            a = {k.lower(): (v or "") for k, v in attrs}
        except Exception:
            return
        rel = a.get("rel", "").lower().split()
        hreflang = a.get("hreflang", "").strip()
        href = a.get("href", "").strip()
        if "alternate" in rel and hreflang and href:
            self.entries.append((hreflang, href))


def fetch(url, timeout=12.0, max_bytes=3_000_000):
    """跟随重定向的 GET (hreflang 以最终页面为准). 返回 (status, headers, final_url, body)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers, resp.geturl(), resp.read(max_bytes)
    except urllib.error.HTTPError as e:
        try:
            body = e.read(65536)
        except Exception:
            body = b""
        return e.code, getattr(e, "headers", None), url, body


def decode(body, headers):
    charset = None
    ct = (headers.get("Content-Type") or "") if headers else ""
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


def parse_link_headers(headers):
    """解析 HTTP Link 头里的 alternate/hreflang 条目."""
    out = []
    if not headers:
        return out
    try:
        vals = headers.get_all("Link") or []
    except Exception:
        vals = []
    for val in vals:
        for m in LINK_ITEM_RE.finditer(val):
            params = m.group("params")
            if not re.search(r"rel\s*=\s*[\"']?alternate", params, re.I):
                continue
            hm = re.search(r"hreflang\s*=\s*[\"']?([^\"';,]+)", params, re.I)
            if hm:
                out.append((hm.group(1).strip(), m.group("url").strip()))
    return out


def norm_url(u, base=None):
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


def check_lang(code):
    """返回该 hreflang 值的问题列表; 空列表 = 合法(大小写不敏感)."""
    problems = []
    c = (code or "").strip()
    if c.lower() == "x-default":
        return []
    if not c:
        return ["空语言码"]
    if "_" in c:
        problems.append("使用下划线 (应为连字符, 如 en_GB -> en-GB)")
        c = c.replace("_", "-")
    parts = c.split("-")
    lang = parts[0].lower()
    if not re.fullmatch(r"[a-z]{2}", lang):
        problems.append("语言码 '{0}' 非 ISO 639-1 双字母 (eng/jp 之类非法)".format(parts[0]))
    elif lang not in ISO639_1:
        hint = LANG_FIX.get(lang, "")
        problems.append("语言码 '{0}' 不是 ISO 639-1 代码{1}".format(
            lang, " (正确写法: {0})".format(hint) if hint else ""))
    rest = parts[1:]
    if rest and re.fullmatch(r"[A-Za-z]{4}", rest[0]):      # ISO 15924 文字码:zh-Hans、sr-Latn
        rest = rest[1:]
    if rest:
        region = rest[0]
        if re.fullmatch(r"\d{3}", region):
            problems.append("区域码 '{0}' 是 UN M.49 数字码, Google 不支持 (原文: such as es-419, aren't supported); "
                            "改用语言码兜底 (es) 加需要的国家码 (es-MX)".format(region))
        elif not re.fullmatch(r"[A-Za-z]{2}", region):
            problems.append("区域码 '{0}' 非法 (须为 ISO 3166-1 Alpha-2 两字母国家码)".format(region))
        elif region.upper() in RESERVED_REGIONS:
            problems.append("区域码 '{0}' 是保留码, 在 Google 搜索里不起作用 (英国用 GB)".format(region))
        if len(rest) > 1:
            problems.append("区域码之后还有多余子标签 '{0}'".format("-".join(rest[1:])))
    return problems


def ln(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def parse_urlset_hrefs(root):
    """sitemap urlset -> {norm_loc: [(lang, href), ...]}."""
    out = {}
    for node in root.iter():
        if ln(node.tag) != "url":
            continue
        loc = None
        alts = []
        for c in node:
            ct = ln(c.tag)
            if ct == "loc" and c.text:
                loc = c.text.strip()
            elif ct == "link":
                hl = (c.attrib.get("hreflang") or "").strip()
                hr = (c.attrib.get("href") or "").strip()
                if hl and hr:
                    alts.append((hl, hr))
        if loc and alts:
            out.setdefault(norm_url(loc), []).extend(alts)
    return out


SITEMAP_SCAN_BUDGET_S = 60.0   # 子表扫描总时长上限;11-05 第三轮留出站 oschina:50 个 4MB 子表扫了 18 分钟


def scan_sitemap(origin, timeout, wanted=None, budget_s=None):
    """抓 origin/sitemap.xml (index 递归 1 层), 提取 hreflang; 返回 (map, note)。
    wanted:要审的页面(归一后);它们都在已扫的子表里找到了就提前停。子表扫描超过 budget_s 秒也停,note 写明扫了几个。"""
    budget_s = SITEMAP_SCAN_BUDGET_S if budget_s is None else budget_s
    wanted = set(wanted or ())
    t0 = time.monotonic()
    result = {}
    try:
        status, headers, _final, body = fetch(origin + "/sitemap.xml", timeout=timeout, max_bytes=20_000_000)
        if status != 200:
            return result, "HTTP {0}, 跳过 sitemap 载体".format(status)
        if body[:2] == b"\x1f\x8b":
            import gzip
            body = gzip.decompress(body)
        root = ET.fromstring(body)
        if ln(root.tag) == "urlset":
            result.update(parse_urlset_hrefs(root))
        elif ln(root.tag) == "sitemapindex":
            kids = []
            for node in root.iter():
                if ln(node.tag) == "sitemap":
                    for c in node:
                        if ln(c.tag) == "loc" and c.text:
                            kids.append(c.text.strip())
            scanned, stop = 0, ""
            for k in kids[:50]:
                if wanted and wanted <= set(result):
                    stop = "要审的页面都已找到"
                    break
                if time.monotonic() - t0 > budget_s:
                    stop = "超过 {0:.0f} 秒预算".format(budget_s)
                    break
                scanned += 1
                try:
                    st2, _h2, _f2, b2 = fetch(k, timeout=timeout, max_bytes=20_000_000)
                    if st2 != 200:
                        continue
                    if b2[:2] == b"\x1f\x8b":
                        import gzip
                        b2 = gzip.decompress(b2)
                    r2 = ET.fromstring(b2)
                    if ln(r2.tag) == "urlset":
                        result.update(parse_urlset_hrefs(r2))
                except Exception:
                    continue
            if stop:
                return result, "共 {0} 个 loc 含 hreflang 声明(子表扫了 {1}/{2} 个, {3})".format(
                    len(result), scanned, len(kids), stop)
        else:
            return result, "根元素非 urlset/sitemapindex, 跳过"
        return result, "共 {0} 个 loc 含 hreflang 声明".format(len(result))
    except Exception as e:
        return result, "获取/解析失败: {0}, 跳过 sitemap 载体".format(type(e).__name__)


def cell(ok):
    if ok is None:
        return "\u2014 "  # 不适用
    return "\u2705 " if ok else "\u274c "


def self_ref_state(d, page_norm):
    """自引用检查:页面没有任何 hreflang 声明时不适用(单语站本来就不需要),返回 None;
    否则返回是否声明了指向自己的条目。"""
    if not d:
        return None
    return any(hn == page_norm for (_l, hn) in d.keys())


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="hreflang_cluster.py",
        description="hreflang 互指簇矩阵验证 (stdlib only)")
    ap.add_argument("urls", nargs="+", metavar="URL", help="簇内任意成员 URL, 建议传入全部语言版本")
    ap.add_argument("--timeout", type=float, default=12.0, help="单请求超时秒数 (默认 12)")
    ap.add_argument("--max-extra", type=int, default=20,
                    help="自动补抓未提供 alternate 页面的上限 (默认 20)")
    ap.add_argument("--no-sitemap", action="store_true", help="跳过 sitemap 载体检查")
    args = ap.parse_args(argv)
    timeout = args.timeout

    entries = {}   # page_url -> {(lang, norm_href): {"orig": href, "carriers": set}}
    statuses = {}  # url -> HTTP status (None=不可达)
    order = []     # 矩阵行序

    def record(page, lang, href, carrier):
        d = entries.setdefault(page, {})
        key = (lang.strip(), norm_url(href, base=page))
        item = d.setdefault(key, {"orig": href, "carriers": set()})
        item["orig"] = href
        item["carriers"].add(carrier)

    def harvest(url):
        """抓页面并记录两个载体的 hreflang; 返回 (final_url, status) 或抛异常."""
        status, headers, final, body = fetch(url, timeout=timeout)
        text = decode(body, headers)
        lg = LinkGrab()
        try:
            lg.feed(text[:500000])
        except Exception:
            pass
        for lang, href in lg.entries:
            record(final, lang, href, "html-head")
        for lang, href in parse_link_headers(headers):
            record(final, lang, href, "http-link")
        return final, status

    # 1) 入参页面
    for u in args.urls:
        if not u.lower().startswith(("http://", "https://")):
            u = "https://" + u
        try:
            final, status = harvest(u)
            statuses[final] = status
            if final not in order:
                order.append(final)
            if norm_url(final) != norm_url(u):
                statuses[u] = status
                if u not in order:
                    order.append(u)
        except Exception as e:
            statuses[u] = None
            if u not in order:
                order.append(u)
            print("[WARN] 抓取失败 {0}: {1}: {2}".format(u, type(e).__name__, e), file=sys.stderr)

    # 2) 补抓未提供的 alternate (有界)
    budget = args.max_extra
    for _page, d in list(entries.items()):
        if budget <= 0:
            break
        for (_lang, hn), item in list(d.items()):
            if budget <= 0:
                break
            if hn in entries or hn in statuses or not hn.lower().startswith(("http://", "https://")):
                continue
            try:
                final, status = harvest(item["orig"])
                statuses[hn] = status
                statuses[final] = status
                if final not in order:
                    order.append(final)
            except Exception:
                statuses[hn] = None
            budget -= 1

    # 3) sitemap 载体 + 冲突检测素材
    smap = {}
    smap_note = "已跳过 (--no-sitemap)"
    if not args.no_sitemap:
        probe = order[0] if order else args.urls[0]
        p = urllib.parse.urlsplit(probe if probe.startswith("http") else "https://" + probe)
        smap, smap_note = scan_sitemap("{0}://{1}".format(p.scheme, p.netloc), timeout,
                                       wanted=[norm_url(x) for x in entries])
        for page in list(entries.keys()):
            for lang, href in smap.get(norm_url(page), []):
                record(page, lang, href, "sitemap")

    # 4) 逐行验证
    hard_fail = False
    rows = []
    details = []
    for page in order:
        d = entries.get(page, {}) or {}
        page_norm = norm_url(page)
        n_items = len(d)
        self_ok = self_ref_state(d, page_norm)

        lang_bad = []
        abs_bad = []
        for (lang, hn), item in sorted(d.items()):
            for prob in check_lang(lang):
                lang_bad.append("hreflang='{0}' {1}".format(lang, prob))
            if not re.match(r"^https?://", hn or ""):
                abs_bad.append("{0} -> {1} (相对 URL)".format(lang, item["orig"]))

        st = statuses.get(page)
        page_ok = (st == 200)
        alt_bad = []
        alt_unverified = 0
        for (lang, hn) in d.keys():
            st2 = statuses.get(hn)
            if st2 is None and hn not in entries:
                alt_unverified += 1
            elif st2 is not None and st2 != 200:
                alt_bad.append("{0} -> {1} (HTTP {2})".format(lang, hn, st2))
        ok200 = page_ok and not alt_bad

        ret_missing = []
        ret_unverified = 0
        for (lang, hn) in sorted(d.keys()):
            if hn not in entries:
                ret_unverified += 1
                continue
            back = any(hn2 == page_norm for (_l2, hn2) in entries[hn].keys())
            if not back:
                ret_missing.append("{0} -> {1}: 对方未回指本页 —— Google 忽略这一对注解 (只影响这一对, 其余互指照常)".format(lang, hn))
        ret_ok = not ret_missing

        row_hard_fail = bool(lang_bad or abs_bad or alt_bad or ret_missing or not page_ok)
        hard_fail = hard_fail or row_hard_fail
        rows.append((page, n_items, self_ok, not lang_bad, not abs_bad, ok200, ret_ok))
        if row_hard_fail or self_ok is False:
            details.append((page, d, st, lang_bad, abs_bad, alt_bad, ret_missing,
                            ret_unverified, alt_unverified))

    # 5) 输出矩阵
    print("=" * 96)
    print("hreflang_cluster | 簇矩阵  (OK=通过  XX=失败)")
    print("sitemap 载体: {0}".format(smap_note))
    header = "{0:<50} {1:>4} {2:>6} {3:>6} {4:>8} {5:>8} {6:>8}".format(
        "URL", "条目", "自引用", "语言码", "绝对URL", "HTTP200", "双向回报")
    print("-" * 96)
    print(header)
    print("-" * 96)
    for page, n, self_ok, lang_ok, abs_ok, ok200, ret_ok in rows:
        disp = (page[:47] + "...") if len(page) > 50 else page
        print("{0:<50} {1:>4} {2:>6} {3:>6} {4:>8} {5:>8} {6:>8}".format(
            disp, n, cell(self_ok), cell(lang_ok), cell(abs_ok), cell(ok200), cell(ret_ok)))

    # 6) 明细
    for page, d, st, lang_bad, abs_bad, alt_bad, ret_missing, ret_unver, alt_unver in details:
        print("\n-- {0} (HTTP {1})".format(page, st if st is not None else "不可达"))
        if not d:
            print("   * 未提取到任何 hreflang 声明")
        if lang_bad:
            print("   * 语言码非法:")
            for s in lang_bad[:10]:
                print("     - {0}".format(s))
        if abs_bad:
            print("   * 非绝对 URL:")
            for s in abs_bad[:10]:
                print("     - {0}".format(s))
        if alt_bad:
            print("   * alternate 不可达:")
            for s in alt_bad[:10]:
                print("     - {0}".format(s))
        if ret_missing:
            print("   * 回链缺失 (只影响这一对):")
            for s in ret_missing[:10]:
                print("     - {0}".format(s))
        if not any((norm_url(h) == norm_url(page)) for (_l, h) in d.keys()) and d:
            print("   * 缺少自引用 (建议每页声明指向自己的 hreflang)")
        if ret_unver or alt_unver:
            print("   * {0} 个 alternate 因超出 --max-extra 未验证回报".format(ret_unver + alt_unver))

    # 7) 载体冲突
    conflicts = []
    for page, d in entries.items():
        for (_lang, hn), item in d.items():
            if len(item["carriers"]) > 1:
                conflicts.append("{0}: ({1}) 声明于 {2}".format(
                    page, _lang, "+".join(sorted(item["carriers"]))))
    if conflicts:
        print("\n---- 多载体重复声明 (三种载体等价, 同时用没有收益、更难维护; 维护提示, 不判错) ----")
        for c in conflicts[:15]:
            print("   * {0}".format(c))
        if len(conflicts) > 15:
            print("   ... 共 {0} 处".format(len(conflicts)))

    print("\n说明: 两页没有互相指向时, Google 忽略这一对注解; 其余互指的注解照常处理 (Google localized-versions 文档).")
    print("==== 结论: {0} ====".format("存在硬失败 (退出码 1)" if hard_fail else "簇校验通过"))
    return 1 if hard_fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[interrupted]", file=sys.stderr)
        sys.exit(130)
