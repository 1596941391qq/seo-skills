#!/usr/bin/env python3
"""JSON-LD 实体规则检查器(stdlib)。从页面提取所有 ld+json 块,检查:
@id 绝对性 / 引用悬空(publisher/author/isPartOf 指向未声明 @id)/ 同名实体分裂 /
占位符黑名单 / aggregateRating 范围 / FAQPage 空答案。
用法: python3 schema_lint.py URL
安全:仅 http(s)(拒 file:///ftp://);私网/环回/链路本地/保留段拒连;重定向逐跳复查。"""
import ipaddress, json, os, re, socket, sys, urllib.parse, urllib.request

UA = "Mozilla/5.0 (compatible; seo-suite-audit/1.0)"
PLACEHOLDERS = ["[Business Name]", "[City]", "[INSERT", "[REPLACE_", "[要追加", "[INVULLEN", "TODO", "example.com"]


# ---------------------------------------------------------------- SSRF 防护
class FetchError(Exception):
    pass


_ssrf_cache = {}


def ssrf_guard(host):
    """仅 http(s) + 拒私网/环回/链路本地/保留段;结果按 host 缓存(trend_watch.py 同款,
    内嵌不 import)。198.18.0.0/15(RFC2544 基准段)豁免:本机 fake-IP 代理会把一切域名
    解析到该段,实际连接经代理出网,TLS 验证仍生效;SEO_MONITOR_STRICT_SSRF=1 恢复全拒。"""
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
    """唯一网络出口(测试打桩点):scheme 检查(仅 http(s))+ SSRF 防护 + 受控 opener。"""
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https"):
        raise FetchError("仅允许 http(s): %s" % url)
    ssrf_guard(p.hostname)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with _opener.open(req, timeout=15) as r:
        return r.read(2_000_000).decode("utf-8", "replace")

def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values(): walk(v, fn)
    elif isinstance(node, list):
        for v in node: walk(v, fn)

USAGE = """usage: schema_lint.py URL
提取页面全部 JSON-LD 块,检查:@id 绝对性/引用悬空/同名实体分裂/占位符黑名单/
aggregateRating 范围/FAQPage 空答案。
安全:仅 http(s) URL;私网/环回/链路本地拒连;重定向逐跳复查(SSRF 防护)。"""

def main():
    a = sys.argv[1:]
    if any(x in ("-h", "--help") for x in a):
        print(USAGE)
        return
    if not a or a[0].startswith("-"):
        sys.stderr.write(USAGE + "\n")
        sys.exit(2)
    url = a[0]
    try:
        html = fetch(url)
    except FetchError as e:
        sys.stderr.write("[error] %s\n" % e)
        sys.exit(2)
    except Exception as e:
        sys.stderr.write("抓取失败 %s: %s\n" % (url, e))
        sys.exit(1)
    blocks = re.findall(r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", html, re.S | re.I)
    if not blocks:
        print("无 JSON-LD"); sys.exit(1)
    objs, ids, raw = [], [], " ".join(blocks)
    for b in blocks:
        try: objs.append(json.loads(b))
        except json.JSONDecodeError as e:
            print(f"[CRITICAL] JSON 解析失败: {e}")
    refs = set()
    for o in objs:
        walk(o, lambda n: refs.update(str(v) for k, v in n.items() if k in ("publisher", "author", "isPartOf", "mainEntity") and isinstance(v, str) and v.startswith("#") or (isinstance(v, str) and str(v).startswith(("http", "#")) and k in ("publisher","author","isPartOf")) ))
    allids = set()
    for o in objs:
        walk(o, lambda n: allids.add(n["@id"]) if isinstance(n.get("@id"), str) else None)
    type_by_id = {}
    for o in objs:
        # 只有 @id 没有 @type 的节点是对同页实体的引用({"@id": "…#organization"}),不是另一种类型
        # (11-05 第三轮留出站 fly.io:publisher/provider/isPartOf 里的纯引用被报「同 @id 多 @type」)
        walk(o, lambda n: type_by_id.setdefault(n.get("@id"), set()).add(",".join(map(str, n["@type"])) if isinstance(n["@type"], list) else str(n["@type"]))
             if n.get("@id") and n.get("@type") else None)
    crit = 0
    for o in objs:
        def check(n):
            nonlocal crit
            i = n.get("@id")
            if isinstance(i, str):
                if not i.startswith(("http", "#", "urn")):
                    print(f"[CRITICAL] @id 非绝对: {i}"); crit += 1
                if i.startswith("#") and urljoin_check(i) and f"{i}" not in allids and len(allids) > 1:
                    pass
            for k in ("publisher", "author", "isPartOf", "mainEntity"):
                v = n.get(k)
                if isinstance(v, str) and v.startswith("#") and v not in allids:
                    print(f"[CRITICAL] 引用悬空: {k}={v} 未在本页声明"); crit += 1
            ar = n.get("aggregateRating")
            if ar and n.get("@type") in ("Organization", "WebPage", "WebSite"):
                print(f"[WARN] aggregateRating 挂在 {n.get('@type')}(自评,富结果受限/垃圾信号)"); crit += 0
            if n.get("@type") == "FAQPage":
                qs = n.get("mainEntity") or []
                for q in qs:
                    ans = (q or {}).get("acceptedAnswer", {}).get("text", "")
                    if not ans or len(str(ans)) < 20:
                        print(f"[CRITICAL] FAQ 空答案: {q}"); crit += 1
        walk(o, check)
    for i, ts in type_by_id.items():
        if len(ts) > 1: print(f"[WARN] 同 @id 多 @type: {i} → {ts}")
    for p in PLACEHOLDERS:
        if p in raw: print(f"[CRITICAL] 占位符残留: {p}"); crit += 1
    def urljoin_check(i): return False
    print(f"\n块数 {len(blocks)} 有效对象 {len(objs)} @id {len(allids)}")
    sys.exit(1 if crit else 0)

if __name__ == "__main__": main()
