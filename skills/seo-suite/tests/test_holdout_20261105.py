#!/usr/bin/env python3
"""留出站(RQ-229 例 6,2026-11-05:ruanyifeng.com、buttondown.com、zenn.dev)测出的误报,逐条修前红、修后绿。

期望值来自独立核验子代理对照站点原始响应的判定(curl 原始 HTML、响应头、robots.txt、sitemap),
夹具按原始响应的结构缩写,不是读实现推的:
- zenn:sitemap 里的中日文网址按 UTF-8 编码后 curl 全是 200;sitemap 在 robots.txt 声明的 /sitemaps/_index.xml;
  index 汇总 31 万条,但要看的是单个文件;?locale=en 是译文(正文不同、canonical 指自己)。
- buttondown:lastmod 写成「2017-12-26T00:00:00.000Z」;两页原始 HTML 有 4,809 / 4,098 字正文但不用 main/article;
  twitter:title 和 og:title 不同。
- 第二轮 qiita(21:11 换的留出站):sitemap_audit 不留间隔连抓 500 条把站打到限流,同时跑的 site_crawl 第 9–90 页
  连着 403,按 1 秒间隔重抓 81 个是 200;sitemap_audit 列出的 10 条「非 200」全是 200。
- 阮一峰:中文首页可见文本不到 600 字,带 Cloudflare JS Detections 脚本(每页都注入),不是挑战页。
"""
import os
import sys
import unittest
import urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_check  # noqa: E402
import site_audit as sa  # noqa: E402
import sitemap_audit as sma  # noqa: E402
from test_rq229_accuracy import PAGE_OK, run_sitemap, sitemap_web, urlset  # noqa: E402
from test_site_crawl import HOME, FakeWeb, crawl, html_links, make_ns, urlset_xml  # noqa: E402

JSD = ("<script>(function(){var u='/cdn-cgi/challenge-platform/scripts/jsd/main.js?ray=x';"
       "var a=document.createElement('script');a.src=u;document.head.appendChild(a);})();</script>")


def run_audit(url, html, extra=None):
    root = "https://%s" % url.split("/")[2]
    table = {url: (200, {"Content-Type": "text/html"}, html),
             root + "/robots.txt": (200, {}, "User-agent: *\nAllow: /\n"),
             root + "/sitemap.xml": (200, {}, "<urlset/>"),
             root + "/llms.txt": (200, {}, "# l\n")}
    table.update(extra or {})
    table = {k: v for k, v in table.items() if v is not None}     # None = 这个地址 404

    def fake(u, timeout=15):
        if u in table:
            return table[u]
        raise urllib.error.HTTPError(u, 404, "Not Found", {}, None)
    orig = sa.fetch
    sa.fetch = fake
    try:
        return sa.audit(url, "en")
    finally:
        sa.fetch = orig


class Ruanyifeng(unittest.TestCase):
    def test_short_cjk_page_with_jsd_script_is_not_a_challenge(self):
        html = ("<html><head><title>阮一峰的网络日志</title>" + JSD + "</head><body>"
                "<h1>阮一峰的网络日志</h1><p>" + "科技爱好者周刊" * 30 + "</p></body></html>")
        self.assertFalse(sa.looks_like_challenge(html))

    def test_real_challenge_still_detected(self):
        html = "<html><head><title>Just a moment...</title></head><body>Checking your browser</body></html>"
        self.assertTrue(sa.looks_like_challenge(html))


class Buttondown(unittest.TestCase):
    def test_lastmod_with_milliseconds(self):
        self.assertIsNotNone(sma.parse_lastmod("2017-12-26T00:00:00.000Z"))

    def test_server_rendered_text_without_semantic_tags(self):
        html = ('<!doctype html><html lang="en"><head><title>Buttondown pricing and plans for newsletters</title>'
                '<meta name="description" content="Plans and pricing for a newsletter tool, from free to '
                'enterprise, with what each one includes."></head><body><div id="app"><h1>Pricing</h1>'
                "<h2>Free</h2><h2>Paid</h2><div>" + "Plain server rendered words here. " * 150
                + "</div></div></body></html>")
        F, _m, _a = run_audit("https://buttondown.example/pricing", html)
        msgs = [m for _s, _a2, m in F]
        self.assertFalse([m for m in msgs if "服务端内容弱" in m or "无 JS 客户端拿到空页" in m], msgs)

    def test_twitter_title_differs_from_og_not_redundant(self):
        head = ('<html><head><title>T</title><meta property="og:title" content="Buttondown">'
                '<meta name="twitter:title" content="Buttondown: the newsletter tool"></head><body></body></html>')
        got = []
        head_check.check(head.encode(), head, "utf-8", "", lambda s, m: got.append((s, m)))
        self.assertFalse([m for _s, m in got if "与 OG 重复" in m], got)

    def test_twitter_title_same_as_og_is_redundant(self):
        head = ('<html><head><title>T</title><meta property="og:title" content="Same">'
                '<meta name="twitter:title" content="Same"></head><body></body></html>')
        got = []
        head_check.check(head.encode(), head, "utf-8", "", lambda s, m: got.append((s, m)))
        self.assertTrue([m for _s, m in got if "与 OG 重复" in m], got)


class Zenn(unittest.TestCase):
    def test_non_ascii_urls_are_encoded_before_fetch(self):
        self.assertEqual(sma.iri_to_uri("https://zenn.dev/topics/日本語"),
                         "https://zenn.dev/topics/%E6%97%A5%E6%9C%AC%E8%AA%9E")
        self.assertEqual(sma.iri_to_uri("https://zenn.dev/a%20b"), "https://zenn.dev/a%20b")

    def test_sitemap_declared_in_robots_is_used(self):
        robots = "User-agent: *\nAllow: /\nSitemap: https://zenn.example/sitemaps/_index.xml\n"
        html = ('<!doctype html><html lang="ja"><head><title>Zenn topics page title long enough</title></head>'
                "<body><main><h1>Zenn</h1><h2>a</h2><h2>b</h2><p>" + "本文 " * 300 + "</p></main></body></html>")
        F, _m, _a = run_audit("https://zenn.example/topics", html, {
            "https://zenn.example/robots.txt": (200, {}, robots),
            "https://zenn.example/sitemap.xml": None,
            "https://zenn.example/sitemaps/_index.xml": (200, {}, "<sitemapindex/>")})
        self.assertFalse([m for _s, a, m in F if a == "sitemap"], F)

    def test_index_total_over_50k_is_not_a_finding(self):
        idx = ('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               + "".join("<sitemap><loc>https://z.example/s%d.xml</loc></sitemap>" % i for i in range(3))
               + "</sitemapindex>").encode()
        routes = {"https://z.example/sitemap.xml": (200, {}, idx)}
        for i in range(3):
            routes["https://z.example/s%d.xml" % i] = (
                200, {}, urlset(["https://z.example/p/%d/%d" % (i, j) for j in range(20000)]))
        routes.update({"https://z.example/p/%d/%d" % (i, j): PAGE_OK for i in range(3) for j in range(20000)})
        with sitemap_web(routes):
            _rc, out = run_sitemap(["https://z.example/sitemap.xml", "--check-limit", "5"])
        self.assertNotIn("50,000", out)

    def test_locale_param_variants_are_translations_not_duplicates(self):
        locs = ["https://z.example/articles/x", "https://z.example/articles/x?locale=en"]
        routes = {"https://z.example/sitemap.xml": (200, {}, urlset(locs))}
        routes.update({u: PAGE_OK for u in locs})
        with sitemap_web(routes):
            _rc, out = run_sitemap(["https://z.example/sitemap.xml"])
        self.assertIn("参数重复 URL (同 path 不同 query)] 命中 0", out)


class QiitaRateLimit(unittest.TestCase):
    def test_crawl_retries_403_after_200_and_recovers(self):
        web = FakeWeb()
        pages = ["https://example.com/p%d" % i for i in range(3)]
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME] + pages))
        web.add(HOME, body=html_links("H", []))
        for u in pages:
            web.add(u, body=html_links("P", []))
        hits = {}
        inner = web.__call__

        def flaky(url, timeout=10.0, method="GET"):        # 每页第一次 403(限流中),退避后 200
            hits[url] = hits.get(url, 0) + 1
            if url in pages and hits[url] == 1:
                return FakeWeb._resp(url, 403, "", [], None)
            return inner(url, timeout, method)
        rep, rc = crawl(make_ns(), flaky)
        self.assertEqual(rc, 0, rep["warnings"])
        self.assertEqual(rep["stats"]["errors"], 0)
        self.assertEqual({p["url"]: p["status"] for p in rep["pages"]}[pages[0]], 200)

    def test_crawl_persistent_403_after_200_is_unjudged_not_error(self):
        web = FakeWeb()
        pages = ["https://example.com/p%d" % i for i in range(3)]
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME] + pages))
        web.add(HOME, body=html_links("H", []))
        for u in pages:
            web.add(u, status=403)
        rep, rc = crawl(make_ns(), web)
        self.assertEqual(rep["stats"]["errors"], 0)
        self.assertEqual(rep["rate_limited_pages"], 3)
        self.assertEqual(rc, 0)

    def test_crawl_403_without_any_200_is_still_an_error(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, status=403)
        rep, _rc = crawl(make_ns(), web)
        self.assertEqual(rep["stats"]["errors"], 1)

    def test_sitemap_audit_403_after_200_is_unjudged(self):
        locs = ["https://q.example/a/%d" % i for i in range(8)]
        routes = {"https://q.example/sitemap.xml": (200, {}, urlset(locs)), locs[0]: PAGE_OK}
        routes.update({u: (403, {}, b"") for u in locs[1:]})
        with sitemap_web(routes):
            _rc, out = run_sitemap(["https://q.example/sitemap.xml"])
        self.assertIn("[桶1 非 200 / 抓取失败] 命中 0", out)
        self.assertIn("未判定:疑似被站点限流", out)


if __name__ == "__main__":
    unittest.main()
