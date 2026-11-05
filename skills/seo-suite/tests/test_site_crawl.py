#!/usr/bin/env python3
"""site_crawl.py golden 用例(stdlib unittest,合成数据,零网络)。
口径钉死 references/monitoring/ci-gates.md §四 URL discovery 优先级链:
  发现链四模式切换(urls / robots+sitemap / sitemap / crawl)/ sitemap index 递归 /
  ≥50 loc 关闭爬虫兜底 / 子域 DNS 探测收否与 crt.sh / 礼貌 delay 与 robots 遵守 /
  归一化去重 / 孤儿检测 / edges 与计数 / 退出码 / --max 截断警告 / SSRF 拒绝 /
  输出契约(crawl.json·urls.txt·--json)。
fetch/DNS/延时全部打桩(FakeWeb + dns 白名单 + Sleeper);SSRF 用例走 IP 字面量
本地解析(同 test_traffic_funnel 手法),零网络。
独立可运行:python3 tests/test_site_crawl.py;也被 tests/run_tests.py 自动发现。"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import site_crawl as sc  # noqa: E402


def run_script(args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, "site_crawl.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env)


def tmp_file(content, suffix=".txt"):
    f = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# 打桩设施:http_fetch / dns_resolve / _sleep
# ---------------------------------------------------------------------------

class FakeWeb:
    """http_fetch 桩:精确路由 + 默认状态;raise_urls 模拟传输层失败(触发重试)。"""

    def __init__(self, default_status=404, default_body=""):
        self.routes = {}
        self.calls = []                      # (url, method)
        self.default_status = default_status
        self.default_body = default_body
        self.fail_all = False

    def add(self, url, status=200, body="", chain=None, final_url=None):
        self.routes[url] = (status, body, chain or [], final_url)

    @staticmethod
    def _resp(url, status, body, chain, final):
        return {"status": status, "final_url": final or url, "chain": chain,
                "headers": {}, "body": body, "body_bytes": body.encode("utf-8", "replace")}

    def __call__(self, url, timeout=10.0, method="GET"):
        self.calls.append((url, method))
        if self.fail_all:
            raise urllib.error.URLError("connection refused")
        h = self.routes.get(url)
        if h is None:
            return self._resp(url, self.default_status, self.default_body, [], None)
        status, body, chain, final = h
        return self._resp(url, status, body, chain, final)

    def urls(self):
        return [u for u, _m in self.calls]


class Sleeper:
    def __init__(self):
        self.vals = []

    def __call__(self, t):
        self.vals.append(t)


@contextlib.contextmanager
def patched(web=None, dns_hosts=()):
    """打桩 http_fetch/dns_resolve/_sleep 并清 SSRF 缓存;DNS 默认全拒(探测零出网)。"""
    orig_fetch, orig_dns, orig_sleep = sc.http_fetch, sc.dns_resolve, sc._sleep
    sleeper = Sleeper()
    if web is not None:
        sc.http_fetch = web
    allow = set(dns_hosts or ())

    def fake_dns(host):
        if host in allow:
            return ["93.184.216.34"]
        raise OSError("NXDOMAIN %s" % host)

    sc.dns_resolve = fake_dns
    sc._sleep = sleeper
    sc._ssrf_cache.clear()
    try:
        yield sleeper
    finally:
        sc.http_fetch, sc.dns_resolve, sc._sleep = orig_fetch, orig_dns, orig_sleep
        sc._ssrf_cache.clear()


def make_ns(**kw):
    d = dict(site="https://example.com", urls=None, max_pages=500, delay=0.0,
             ignore_robots=False, strip_params=False, same_host=False,
             include_subdomains=True, subs="dns", check_external=False,
             timeout=5.0, out="crawl.json", urls_out=None, json=False)
    d.update(kw)
    return argparse.Namespace(**d)


def crawl(ns, web, dns_hosts=()):
    with patched(web, dns_hosts):
        report, rc = sc.Crawler(ns).run()
    return report, rc


# ---------------------------------------------------------------------------
# 合成 fixture
# ---------------------------------------------------------------------------

HOME = "https://example.com/"
ABOUT = "https://example.com/about"


def robots_txt(disallow=(), sitemap=None, crawl_delay=None):
    lines = ["User-agent: *"]
    lines += ["Disallow: %s" % d for d in disallow]
    if crawl_delay is not None:
        lines.append("Crawl-delay: %s" % crawl_delay)
    if sitemap:
        lines.append("Sitemap: %s" % sitemap)
    return "\n".join(lines) + "\n"


def urlset_xml(locs):
    return ('<?xml version="1.0" encoding="UTF-8"?><urlset>'
            + "".join("<url><loc>%s</loc></url>" % u for u in locs) + "</urlset>")


def index_xml(children):
    return ('<?xml version="1.0" encoding="UTF-8"?><sitemapindex>'
            + "".join("<sitemap><loc>%s</loc></sitemap>" % c for c in children)
            + "</sitemapindex>")


def html_links(title, hrefs, canonical=None):
    c = '<link rel="canonical" href="%s">' % canonical if canonical else ""
    body = "".join('<a href="%s">x</a>' % h for h in hrefs)
    return "<html><head><title>%s</title>%s</head><body>%s</body></html>" % (title, c, body)


# ---------------------------------------------------------------------------
# 发现链四模式
# ---------------------------------------------------------------------------

class DiscoveryChainTests(unittest.TestCase):

    def test_urls_mode_closes_discovery(self):
        """链①:--urls 给出即关闭 ②③④——sitemap.xml 不被抓;robots 仍抓(礼貌规则)。"""
        p = tmp_file("# 手工清单\nhttps://example.com/u1\nhttps://example.com/u2\n")
        web = FakeWeb()
        web.add(HOME + "robots.txt", body=robots_txt(sitemap="https://example.com/sitemap.xml"))
        web.add("https://example.com/sitemap.xml", body=urlset_xml(["https://example.com/x"]))
        web.add("https://example.com/u1", body=html_links("U1", []))
        web.add("https://example.com/u2", body=html_links("U2", []))
        rep, rc = crawl(make_ns(urls=p), web)
        os.unlink(p)
        self.assertEqual(rc, 0)
        self.assertEqual(rep["discovery"]["mode"], "urls")
        self.assertEqual(rep["discovery"]["counts"], {"robots": 0, "sitemap": 0, "crawl": 0})
        self.assertEqual([pg["url"] for pg in rep["pages"]],
                         ["https://example.com/u1", "https://example.com/u2"])
        self.assertNotIn("https://example.com/sitemap.xml", web.urls())   # ③ 被关闭
        self.assertIn(HOME + "robots.txt", web.urls())                    # 礼貌规则仍在

    def test_robots_sitemap_mode_and_disallow_exclusion(self):
        """链②→③:robots Sitemap 指令入队;Disallow 路径被排除(不抓、进 robots_skipped)。"""
        web = FakeWeb()
        web.add(HOME + "robots.txt", body=robots_txt(
            disallow=["/private"], sitemap="https://example.com/sitemap.xml"))
        web.add("https://example.com/sitemap.xml",
                body=urlset_xml([HOME, ABOUT, "https://example.com/private"]))
        web.add(HOME, body=html_links("Home", ["/about"]))
        web.add(ABOUT, body=html_links("About", []))
        web.add("https://example.com/private", body=html_links("Private", []))
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep["discovery"]["mode"], "robots+sitemap")
        self.assertEqual(rep["discovery"]["counts"]["robots"], 1)
        self.assertEqual(rep["discovery"]["counts"]["sitemap"], 3)
        self.assertEqual({pg["url"] for pg in rep["pages"]}, {HOME, ABOUT})
        self.assertNotIn("https://example.com/private", web.urls())       # 排除 = 根本不抓
        self.assertEqual(rep["robots_skipped"], ["https://example.com/private"])
        self.assertTrue(any("Disallow" in w for w in rep["warnings"]), rep["warnings"])
        self.assertEqual(rc, 0)

    def test_direct_sitemap_mode_when_no_robots_directive(self):
        """链③:robots 无 Sitemap 指令(404)→ 直接 /sitemap.xml;孤儿/深度/外链聚合。"""
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml",
                body=urlset_xml([HOME, "https://example.com/p1", "https://example.com/orphan"]))
        web.add(HOME, body=html_links("Home", ["/p1"]))
        web.add("https://example.com/p1",
                body=html_links("P1", ["/", "https://twitter.com/x", "https://github.com/y"]))
        web.add("https://example.com/orphan", body=html_links("Orphan", []))
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep["discovery"]["mode"], "sitemap")
        by = {pg["url"]: pg for pg in rep["pages"]}
        self.assertEqual(rep["orphans"], ["https://example.com/orphan"])  # 0 入链且非首页
        self.assertEqual(by[HOME]["depth"], 0)
        self.assertEqual(by["https://example.com/p1"]["depth"], 1)
        self.assertIsNone(by["https://example.com/orphan"]["depth"])      # 图上不可达
        self.assertEqual(by["https://example.com/p1"]["inlinks"], 1)
        self.assertEqual(by["https://example.com/p1"]["out_external"], 2)
        self.assertEqual(rep["external_domains"], {"twitter.com": 1, "github.com": 1})
        self.assertIn({"src": "https://example.com/p1", "dst": HOME}, rep["edges"])
        self.assertEqual(rc, 0)

    def test_crawl_mode_bfs_depths_and_edges(self):
        """链④:无 robots/sitemap → 从首页 BFS;/ 与 /a 互链不重复计边,深度按层。"""
        web = FakeWeb()
        web.add(HOME, body=html_links("Home", ["/a", "/b"]))
        web.add("https://example.com/a", body=html_links("A", ["/c"]))
        web.add("https://example.com/b", body=html_links("B", ["/a"]))
        web.add("https://example.com/c", body=html_links("C", []))
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep["discovery"]["mode"], "crawl")
        self.assertEqual(rep["discovery"]["counts"]["crawl"], 3)
        self.assertEqual([pg["url"] for pg in rep["pages"]],
                         [HOME, "https://example.com/a", "https://example.com/b",
                          "https://example.com/c"])
        by = {pg["url"]: pg for pg in rep["pages"]}
        self.assertEqual([by[HOME]["depth"], by["https://example.com/a"]["depth"],
                          by["https://example.com/b"]["depth"],
                          by["https://example.com/c"]["depth"]], [0, 1, 1, 2])
        self.assertEqual(by["https://example.com/a"]["inlinks"], 2)      # / 与 /b 都指它
        self.assertEqual(len(rep["edges"]), 4)
        self.assertEqual(rep["stats"]["total_outlinks"], 4)              # 2+1+1+0
        self.assertEqual(rep["stats"]["total_inlinks"], 4)               # /a×2+/b+/c
        self.assertEqual(rep["stats"]["redirects"], 0)
        self.assertEqual(rc, 0)

    def test_sitemap_index_recursion_nested(self):
        """sitemapindex 递归:index → urlset + 嵌套 index → urlset,三层 loc 全收。"""
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=index_xml(
            ["https://example.com/sm-a.xml", "https://example.com/sm-b.xml"]))
        web.add("https://example.com/sm-a.xml",
                body=urlset_xml(["https://example.com/p1", "https://example.com/p2"]))
        web.add("https://example.com/sm-b.xml", body=index_xml(["https://example.com/sm-c.xml"]))
        web.add("https://example.com/sm-c.xml", body=urlset_xml(["https://example.com/p3"]))
        for u in ("p1", "p2", "p3"):
            web.add("https://example.com/" + u, body=html_links(u, []))
        web.add("https://example.com/", body=html_links("Home", []))
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep["discovery"]["mode"], "sitemap")
        self.assertEqual(rep["discovery"]["counts"]["sitemap"], 3)
        self.assertEqual({pg["url"] for pg in rep["pages"]}
                         - {"https://example.com/p1", "https://example.com/p2",
                            "https://example.com/p3", "https://example.com/"}, set())
        # sitemap 模式也先抓首页(2026-10-24 asahi 实测:不抓首页时孤儿判定全是假阳性)
        self.assertEqual(rc, 0)

    def test_50_sitemap_locs_close_crawl_fallback(self):
        """≥50 条 loc 关闭爬虫兜底:链接只进图(边保留),不进抓取队列。"""
        locs = ["https://example.com/p%02d" % i for i in range(1, 51)]
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml(locs))
        web.add("https://example.com/p01", body=html_links("P1", ["/hidden"]))
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep["discovery"]["counts"]["sitemap"], 50)
        self.assertEqual(rep["discovery"]["counts"]["crawl"], 0)
        self.assertNotIn("https://example.com/hidden", {pg["url"] for pg in rep["pages"]})
        self.assertIn({"src": "https://example.com/p01", "dst": "https://example.com/hidden"},
                      rep["edges"])                                        # 图仍记边
        self.assertEqual(len(rep["pages"]), 51)                          # 50 条 loc + 首页

    def test_under_50_locs_crawl_supplement(self):
        """<50 条 loc:爬虫兜底开着,sitemap 页上的新内链被补抓(source=crawl)。"""
        locs = ["https://example.com/p%02d" % i for i in range(1, 50)]    # 49 条
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml(locs))
        web.add("https://example.com/p01", body=html_links("P1", ["/hidden"]))
        web.add("https://example.com/hidden", body=html_links("H", []))
        rep, _rc = crawl(make_ns(), web)
        self.assertEqual(rep["discovery"]["counts"]["crawl"], 1)
        hidden = [pg for pg in rep["pages"] if pg["url"] == "https://example.com/hidden"]
        self.assertEqual(len(hidden), 1)
        self.assertEqual(hidden[0]["source"], "crawl")


# ---------------------------------------------------------------------------
# 子域发现
# ---------------------------------------------------------------------------

class SubdomainTests(unittest.TestCase):

    def test_dns_probe_accept_and_reject(self):
        """(b) DNS 探测:解析成功且 HTTP 200 才收;解析成功但非 200 / 解析失败都不收。"""
        web = FakeWeb()
        web.add(HOME, body=html_links("Home", []))
        web.add("https://blog.example.com/", body=html_links("Blog", []))
        # staging.example.com:DNS 白名单内但根路径默认 404 → 拒
        # shop.example.com:不在 DNS 白名单 → 连 HTTP 都不发
        rep, rc = crawl(make_ns(), web,
                        dns_hosts={"blog.example.com", "staging.example.com"})
        self.assertEqual(rep["subdomains"], ["blog.example.com"])
        self.assertIn("https://blog.example.com/", {pg["url"] for pg in rep["pages"]})
        self.assertEqual(web.urls().count("https://staging.example.com/"), 1)   # 试了一次
        self.assertNotIn("https://shop.example.com/", web.urls())               # DNS 即拒
        self.assertEqual(rc, 0)

    def test_same_host_tightens_and_counts_subdomain_link_external(self):
        """--same-host:不做子域探测,跨子域链接按外链记(聚合键=完整主机)。"""
        web = FakeWeb()
        web.add(HOME, body=html_links("Home", ["/a", "https://blog.example.com/x"]))
        web.add("https://example.com/a", body=html_links("A", []))
        rep, rc = crawl(make_ns(same_host=True), web)
        self.assertEqual(rep["subdomains"], [])
        self.assertNotIn("https://blog.example.com/x", web.urls())       # 不抓跨子域
        by = {pg["url"]: pg for pg in rep["pages"]}
        self.assertEqual(by[HOME]["out_external"], 1)
        self.assertEqual(by[HOME]["out_internal"], 1)
        self.assertEqual(rep["external_domains"], {"blog.example.com": 1})  # 非裸 registrable
        self.assertEqual(rc, 0)

    def test_crtsh_discovery_and_graceful_failure(self):
        """(c) --subs ct:crt.sh JSON 候选经 DNS+200 验收;crt.sh 不可达优雅跳过。"""
        crt_url = "https://crt.sh/?q=%25.example.com&output=json"
        body = json.dumps([{"name_value": "news.example.com\n*.example.com"},
                           {"name_value": "example.com"}])
        web = FakeWeb()
        web.add(HOME, body=html_links("Home", []))
        web.add(crt_url, body=body)
        web.add("https://news.example.com/", body=html_links("News", []))
        rep, rc = crawl(make_ns(subs="ct"), web, dns_hosts={"news.example.com"})
        self.assertIn("news.example.com", rep["subdomains"])
        self.assertIn("https://news.example.com/", {pg["url"] for pg in rep["pages"]})
        self.assertEqual(rc, 0)
        # 失败路径:crt.sh 404 → 警告 + 运行继续
        web2 = FakeWeb()
        web2.add(HOME, body=html_links("Home", []))
        rep2, rc2 = crawl(make_ns(subs="ct"), web2)
        self.assertTrue(any("crt.sh" in w for w in rep2["warnings"]), rep2["warnings"])
        self.assertEqual(rc2, 0)


# ---------------------------------------------------------------------------
# 礼貌:delay 与 robots 遵守
# ---------------------------------------------------------------------------

class PolitenessTests(unittest.TestCase):

    def test_crawl_delay_from_robots_star_group(self):
        """crawl-delay 取 * 组,与 --delay 取大者;首个请求不延时。"""
        web = FakeWeb()
        web.add(HOME + "robots.txt", body=robots_txt(crawl_delay=3))
        web.add(HOME, body=html_links("Home", ["/a", "/b"]))
        web.add("https://example.com/a", body=html_links("A", []))
        web.add("https://example.com/b", body=html_links("B", []))
        # robots + sitemap.xml(404) + / + /a + /b = 5 个请求 → 4 次延时,全部 3.0s
        sleeper = None
        with patched(web) as s:
            sleeper = s
            sc.Crawler(make_ns(delay=0.0)).run()
        self.assertEqual(sleeper.vals, [3.0, 3.0, 3.0, 3.0])

    def test_ignore_robots_skips_compliance(self):
        """--ignore-robots:robots.txt 不抓、Disallow 不排除、crawl-delay 不采用。"""
        robots = robots_txt(disallow=["/private"], crawl_delay=9)
        web = FakeWeb()
        web.add(HOME + "robots.txt", body=robots)
        web.add(HOME, body=html_links("Home", ["/a", "/private"]))
        web.add("https://example.com/a", body=html_links("A", []))
        web.add("https://example.com/private", body=html_links("P", []))
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep.get("robots_skipped"), ["https://example.com/private"])
        self.assertNotIn("https://example.com/private", {pg["url"] for pg in rep["pages"]})
        self.assertEqual(rc, 0)
        web2 = FakeWeb()
        web2.add(HOME + "robots.txt", body=robots)
        web2.add(HOME, body=html_links("Home", ["/a", "/private"]))
        web2.add("https://example.com/a", body=html_links("A", []))
        web2.add("https://example.com/private", body=html_links("P", []))
        with patched(web2) as sleeper:
            rep2, rc2 = sc.Crawler(make_ns(ignore_robots=True, delay=0.5)).run()
        self.assertNotIn(HOME + "robots.txt", web2.urls())               # robots 根本不抓
        self.assertIn("https://example.com/private", {pg["url"] for pg in rep2["pages"]})
        self.assertTrue(set(sleeper.vals) == {0.5}, sleeper.vals)        # 用 --delay 非 9
        self.assertEqual(rc2, 0)

    def test_parse_robots_and_matching(self):
        """RFC 9309 简化解析:连续 UA 合并/Sitemap 提取/crawl-delay/空 Disallow 无操作/
        最长前缀 + Allow 平局胜。"""
        doc = sc.parse_robots(
            "User-agent: *\nDisallow:\nDisallow: /x\nCrawl-delay: 2\n"
            "Sitemap: https://e.com/s.xml\n\nUser-agent: seo-suite-crawl\nAllow: /x/y\n")
        self.assertEqual(doc["sitemaps"], ["https://e.com/s.xml"])
        self.assertEqual(doc["crawl_delay"], 2.0)
        # 专属组整体优先(RFC 9309 不与 * 组合并):/x/y 由 Allow /x/y 放行
        self.assertTrue(sc.robots_allows(doc, "https://e.com/x/y/z"))
        self.assertTrue(sc.robots_allows(doc, "https://e.com/x1"))        # 专属组无匹配 → 放行
        star_only = sc.parse_robots("User-agent: *\nDisallow: /x\n")
        self.assertFalse(sc.robots_allows(star_only, "https://e.com/x1"))  # * 组 /x 前缀禁
        self.assertTrue(sc.robots_allows(star_only, "https://e.com/other"))
        only_empty = sc.parse_robots("User-agent: *\nDisallow:\n")
        self.assertTrue(sc.robots_allows(only_empty, "https://e.com/anything"))  # 空 Disallow


# ---------------------------------------------------------------------------
# 归一化与去重
# ---------------------------------------------------------------------------

class NormalizationTests(unittest.TestCase):

    def test_normalize_url_rules(self):
        """去 fragment/尾斜杠保留(/a 和 /a/ 是两个 URL)/参数保留/大小写不合并/端口与 host 小写。"""
        self.assertEqual(sc.normalize_url("https://Example.COM:443/a/#frag"),
                         "https://example.com/a/")
        self.assertEqual(sc.normalize_url("https://x.com/"), "https://x.com/")
        self.assertEqual(sc.normalize_url("https://x.com/blog/"), "https://x.com/blog/")
        self.assertEqual(sc.normalize_url("/p?q=1", base="https://x.com/"),
                         "https://x.com/p?q=1")
        self.assertEqual(sc.normalize_url("/p?q=1", base="https://x.com/", strip_params=True),
                         "https://x.com/p")
        self.assertNotEqual(sc.normalize_url("https://x.com/A"), sc.normalize_url("https://x.com/a"))
        self.assertIsNone(sc.normalize_url("ftp://x.com/y"))
        self.assertIsNone(sc.normalize_url("not a url"))

    def test_dedupe_trailing_slash_fragment_params_and_case(self):
        """已见集合去重:/a、/a#f、:443/a 合并;/a/、/A 与 /a?x=1 各自独立。"""
        web = FakeWeb()
        web.add(HOME, body=html_links("Home",
                                      ["/a/", "/a#top", "/a", "https://example.com:443/a",
                                       "https://example.com/A", "/a?x=1"]))
        rep, _rc = crawl(make_ns(), web)
        by = {pg["url"]: pg for pg in rep["pages"]}
        self.assertEqual(set(by), {HOME, "https://example.com/a", "https://example.com/a/", "https://example.com/A",
                                   "https://example.com/a?x=1"})
        self.assertEqual(by[HOME]["out_internal"], 4)
        web2 = FakeWeb()
        web2.add(HOME, body=html_links("Home",
                                       ["/a/", "/a#top", "/a?x=1", "https://example.com/A"]))
        rep2, _rc2 = crawl(make_ns(strip_params=True), web2)
        self.assertEqual(set(pg["url"] for pg in rep2["pages"]),
                         {HOME, "https://example.com/a", "https://example.com/a/",
                          "https://example.com/A"})  # ?x=1 并入 /a


# ---------------------------------------------------------------------------
# 链接图:重定向 / canonical / 外链抽检
# ---------------------------------------------------------------------------

class GraphTests(unittest.TestCase):

    def test_redirect_chain_recorded_and_link_base(self):
        """重定向跟随记链:final_url 记档,相对链接按最终 URL 解析。"""
        p = tmp_file("https://example.com/r\n")
        web = FakeWeb()
        web.add("https://example.com/r", status=200, body=html_links("R", ["about"]),
                chain=[{"status": 301, "location": "https://example.com/final/"}],
                final_url="https://example.com/final/")
        rep, rc = crawl(make_ns(urls=p), web)
        os.unlink(p)
        pg = rep["pages"][0]
        self.assertEqual(pg["status"], 200)
        self.assertEqual(pg["final_url"], "https://example.com/final/")
        self.assertEqual(rep["stats"]["redirects"], 1)
        self.assertIn({"src": "https://example.com/r", "dst": "https://example.com/final/about"},
                      rep["edges"])                          # about 挂在最终 URL 之下
        self.assertEqual(rc, 0)

    def test_canonical_and_title_extracted(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("  Example   Home ", [], canonical="https://example.com/"))
        rep, _rc = crawl(make_ns(), web)
        pg = rep["pages"][0]
        self.assertEqual(pg["title"], "Example Home")
        self.assertEqual(pg["canonical"], "https://example.com/")

    def test_check_external_head_sampling(self):
        """--check-external:Top 外链域抽样 HEAD(只记状态);默认关。"""
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("Home", ["https://twitter.com/x", "https://github.com/y"]))
        web.add("https://twitter.com/", status=200)
        web.add("https://github.com/", status=301)
        rep, rc = crawl(make_ns(check_external=True), web)
        # 平局按域名字典序(确定性输出,不受进程 hash 随机影响)
        self.assertEqual(rep["external_check"],
                         [{"domain": "github.com", "status": 301},
                          {"domain": "twitter.com", "status": 200}])
        self.assertIn(("https://twitter.com/", "HEAD"), web.calls)
        self.assertEqual(rc, 0)
        web2 = FakeWeb()
        web2.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web2.add(HOME, body=html_links("Home", ["https://twitter.com/x"]))
        rep2, _rc2 = crawl(make_ns(), web2)
        self.assertNotIn("external_check", rep2)                         # 默认关
        self.assertNotIn("https://twitter.com/", web2.urls())


# ---------------------------------------------------------------------------
# 预算、退出码、CLI
# ---------------------------------------------------------------------------

class BudgetAndExitTests(unittest.TestCase):

    def test_max_truncation_warning(self):
        """--max 截断:页数封顶 + 截断警告(建议采样)。"""
        locs = ["https://example.com/p%d" % i for i in range(6)]
        web = FakeWeb(default_status=200, default_body=html_links("P", []))
        web.add("https://example.com/sitemap.xml", body=urlset_xml(locs))
        rep, rc = crawl(make_ns(max_pages=3), web)
        self.assertEqual(len(rep["pages"]), 3)
        self.assertEqual(rep["stats"]["pages"], 3)
        self.assertTrue(any("--max 3" in w for w in rep["warnings"]), rep["warnings"])
        self.assertEqual(rc, 0)

    def test_max_hard_cap_clamp(self):
        """--max 超过 5000 上限:警告 + 截断到 5000。"""
        web = FakeWeb(default_status=200, default_body=html_links("P", []))
        with patched(web):
            c = sc.Crawler(make_ns(max_pages=6000))
            rep, _rc = c.run()
        self.assertEqual(c.max_pages, 5000)
        self.assertTrue(any("5000" in w and "采样" in w for w in rep["warnings"]),
                        rep["warnings"])

    def test_exit_1_with_error_pages(self):
        """4xx 页 → 退出码 1(错误计数含 4xx/5xx)。"""
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME, "https://example.com/missing"]))
        web.add(HOME, body=html_links("Home", []))
        # /missing 默认 404
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rc, 1)
        self.assertEqual(rep["stats"]["errors"], 1)
        by = {pg["url"]: pg for pg in rep["pages"]}
        self.assertEqual(by["https://example.com/missing"]["status"], 404)

    def test_exit_3_all_starts_dead_with_retries(self):
        """全部起点传输层失败 → 重试 2 次(共 3 次尝试)后记 error,退出码 3。"""
        web = FakeWeb()
        web.fail_all = True
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rc, 3)
        self.assertEqual(web.urls().count(HOME), 3)                      # 1+2 重试
        self.assertIsNone(rep["pages"][0]["status"])
        self.assertEqual(rep["stats"]["errors"], 1)

    def test_exit_2_input_errors_cli(self):
        """输入/用法错 → 退出码 2(不触网,校验先于爬取)。"""
        r = run_script(["--urls", "/nonexistent/urls.txt", "https://example.com"])
        self.assertEqual(r.returncode, 2)
        self.assertEqual(run_script(["--max", "0", "https://example.com"]).returncode, 2)
        self.assertEqual(run_script(["--subs", "bogus", "https://example.com"]).returncode, 2)
        self.assertEqual(run_script([]).returncode, 2)
        r5 = run_script(["--delay", "-1", "https://example.com"])
        self.assertEqual(r5.returncode, 2)

    def test_help(self):
        r = run_script(["--help"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("usage:", r.stdout)
        self.assertIn("退出码", r.stdout)


# ---------------------------------------------------------------------------
# 输出契约:crawl.json / --urls-out / --json / markdown
# ---------------------------------------------------------------------------

class OutputContractTests(unittest.TestCase):

    def _run_main(self, web, argv):
        with patched(web):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sc.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_outputs_crawl_json_urls_out_and_json_stdout(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME, ABOUT]))
        web.add(HOME, body=html_links("Home", ["/about"]))
        web.add(ABOUT, body=html_links("About", [], canonical=ABOUT))
        jpath = os.path.join(tempfile.mkdtemp(prefix="sc_out_"), "crawl.json")
        upath = jpath.replace("crawl.json", "urls.txt")
        rc, out, _err = self._run_main(web, ["https://example.com", "--out", jpath,
                                             "--urls-out", upath, "--json"])
        self.assertEqual(rc, 0)
        with open(jpath, encoding="utf-8") as f:
            rep = json.load(f)
        self.assertEqual(list(rep.keys())[:9],
                         ["schema_version", "domain", "subdomains", "discovery", "pages",
                          "edges", "orphans", "external_domains", "stats"])
        self.assertEqual(rep["schema_version"], 1)
        self.assertEqual(rep["domain"], "example.com")
        self.assertEqual(rep["discovery"]["mode"], "sitemap")
        self.assertEqual(list(rep["pages"][0].keys())[:9],
                         ["url", "status", "title", "canonical", "depth", "inlinks",
                          "out_internal", "out_external", "source"])
        # B27/B28(2026-10-21 加键):内链/外链出链分列、重定向页计数(不计孤儿);原键语义不变
        self.assertEqual(set(rep["stats"].keys()),
                         {"pages", "total_inlinks", "total_outlinks", "total_out_internal",
                          "total_out_external", "redirected_pages", "errors",
                          "redirects", "duration_s"})
        self.assertTrue(out.lstrip().startswith("{"))                    # --json → stdout
        with open(upath, encoding="utf-8") as f:
            self.assertEqual(f.read().splitlines(), [HOME, ABOUT])       # 纯 URL 清单
        # markdown 摘要形态
        rc2, out2, _ = self._run_main(web, ["https://example.com", "--out", jpath])
        self.assertEqual(rc2, 0)
        self.assertIn("发现模式: sitemap", out2)
        self.assertIn("孤儿页", out2)
        self.assertIn("子域", out2)

    def test_urls_out_excludes_error_pages(self):
        """--urls-out 只收 2xx/3xx 页(4xx 喂下游只会再失败一次)。"""
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml",
                body=urlset_xml([HOME, "https://example.com/gone"]))
        web.add(HOME, body=html_links("Home", []))
        upath = os.path.join(tempfile.mkdtemp(prefix="sc_uo_"), "urls.txt")
        jpath = upath.replace("urls.txt", "crawl.json")
        rc, _out, _err = self._run_main(
            web, ["https://example.com", "--out", jpath, "--urls-out", upath])
        self.assertEqual(rc, 1)                                           # /gone 404
        with open(upath, encoding="utf-8") as f:
            self.assertEqual(f.read().splitlines(), [HOME])


# ---------------------------------------------------------------------------
# SSRF(真实函数,IP 字面量本地解析,零网络——同 test_traffic_funnel 手法)
# ---------------------------------------------------------------------------

class SsrfTests(unittest.TestCase):

    def setUp(self):
        sc._ssrf_cache.clear()
        self._strict = os.environ.pop("SEO_CRAWL_STRICT_SSRF", None)

    def tearDown(self):
        sc._ssrf_cache.clear()
        if self._strict is not None:
            os.environ["SEO_CRAWL_STRICT_SSRF"] = self._strict

    def test_guard_rejects_non_public_ips(self):
        for host in ("127.0.0.1", "10.0.0.5", "192.168.1.2", "169.254.169.254", "::1"):
            with self.assertRaises(sc.GuardError, msg=host):
                sc.ssrf_guard(host)
        sc.ssrf_guard("93.184.216.34")                                    # 公网字面量放行

    def test_redirect_hop_guard_and_scheme(self):
        """重定向逐跳复查:302 → 元数据端点/环回/非 http(s) 必须被拒。"""
        for evil in ("http://169.254.169.254/latest/meta-data", "http://127.0.0.1:8080/x",
                     "http://10.0.0.5/internal", "ftp://evil.com/f"):
            with self.assertRaises(sc.GuardError, msg=evil):
                sc.check_redirect("http://example.com/", evil)
        with self.assertRaises(sc.GuardError):
            sc.http_fetch("ftp://example.com/data", timeout=1)           # scheme 先拒,不出网


if __name__ == "__main__":
    unittest.main(verbosity=1)
