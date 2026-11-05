#!/usr/bin/env python3
"""2026-10-24 三市场实战(日本 asahi.com、韩国 yna.co.kr、德国 spiegel.de)发现的误报回归。

每条用例的输入是站点当天的真实响应,存在 tests/fixtures/k2/<市场-站点>/(只截取判定
用得到的部分,文件头注明截取范围)。修前红、修后绿;零网络(http_fetch / 抓取函数打桩)。
判据与结果表见仓根 deployments/2026-10-24-k2/。
"""
import contextlib
import io
import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
FIX = os.path.join(BASE, "tests", "fixtures", "k2")
sys.path.insert(0, SCRIPTS)
import sitemap_audit as _sma  # noqa: E402
_sma._sleep = lambda _s: None  # 逐条检查的礼貌间隔在测试里不真等


def fixture(*parts):
    with open(os.path.join(FIX, *parts), "rb") as f:
        return f.read()


def run_main(mod, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = mod.main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


class NewsSitemapRobotsIndexTests(unittest.TestCase):
    """asahi.com:robots.txt 只声明 sitemap index,index 里列着 sitemap_national.xml。
    修前:报 WARN「robots.txt 的 1 条 Sitemap 声明均不含本 sitemap」——但经 index 可发现。"""

    def setUp(self):
        import news_sitemap_check as ns
        self.ns = ns
        news = "https://www.asahi.com/sitemap/sitemap_national.xml"
        mapping = {
            news: fixture("ja-asahi", "sitemap_national.xml"),
            "https://www.asahi.com/robots.txt": fixture("ja-asahi", "robots.txt"),
            "https://www.asahi.com/sitemap.xml": fixture("ja-asahi", "sitemap.xml"),
        }
        orig = ns.http_fetch

        def fake(url, timeout=ns.FETCH_TIMEOUT, max_bytes=10 ** 9):
            if url in mapping:
                return 200, {}, mapping[url]
            return 200, {}, b"<html><head><title>a</title></head><body>x</body></html>"

        ns.http_fetch = fake
        self.addCleanup(setattr, ns, "http_fetch", orig)
        self.news = news

    def test_declared_via_sitemap_index_is_not_warned(self):
        rc, out, _ = run_main(self.ns, ["--url", self.news, "--sample", "0"])
        self.assertNotIn("均不含本 sitemap", out)
        self.assertIn("sitemap index", out)


class AboveFoldSkipLinkTests(unittest.TestCase):
    """三站首页都以「跳到正文」链接开头(asahi「メインメニューをとばして…」、yna「본문 바로가기」、
    spiegel title="Zum Inhalt springen" 的 1px 隐藏链接)。这类链接平时不可见,修前被当成首屏文本
    和首个链接(CTA 判「仅存在链接: メインメニューをとばして…」)。"""

    SKIP_TEXT = {"ja-asahi": "メインメニューをとばして", "ko-yna": "본문 바로가기",
                 "de-spiegel": "Zum Inhalt springen"}

    def parse(self, site):
        import above_fold as af
        p = af.FoldParser()
        p.feed(fixture(site, "home-top.html").decode("utf-8"))
        p.flush()
        return "".join(p.text_parts), p.links

    def test_skip_links_not_in_fold_text_or_links(self):
        for site, txt in self.SKIP_TEXT.items():
            fold, links = self.parse(site)
            self.assertNotIn(txt, fold[:700], site)
            self.assertFalse(any(txt in l for l in links[:3]), "%s: %r" % (site, links[:3]))


class SitemapAuditRobotsDiscoveryTests(unittest.TestCase):
    """yna.co.kr:/sitemap.xml 返回 404,robots.txt 声明了 7 个 sitemap。修前:给站点 URL 只试
    /sitemap.xml,直接 [FATAL] 退出 2——站点其实有 sitemap。"""

    def test_site_url_uses_robots_sitemaps_when_default_missing(self):
        import sitemap_audit as sa
        robots = fixture("ko-yna", "robots.txt")
        news3 = fixture("ko-yna", "news-sitemap3.xml")
        orig_fetch, orig_robots = sa.fetch, sa.robots_for

        def fake(url, timeout=10.0, max_bytes=5_000_000):
            if url == "https://www.yna.co.kr/robots.txt":
                return 200, {}, robots
            if url.startswith("https://www.yna.co.kr/news-sitemap"):
                return 200, {}, news3
            if url.endswith(".xml"):
                return 404, {}, b"not found"
            return 200, {}, b"<html><head><title>a</title></head><body>x</body></html>"

        sa.fetch = fake
        class AllowAll:
            def can_fetch(self, ua, url):
                return True

        sa.robots_for = lambda url, timeout=10.0: AllowAll()
        self.addCleanup(setattr, sa, "fetch", orig_fetch)
        self.addCleanup(setattr, sa, "robots_for", orig_robots)
        rc, out, err = run_main(sa, ["https://www.yna.co.kr/", "--check-limit", "0", "--max-child", "2"])
        self.assertNotEqual(rc, 2, err)
        self.assertIn("robots.txt 声明的 7 个 sitemap", out)
        self.assertIn("loc 总数: 3", out)


class SiteCrawlCcSldTests(unittest.TestCase):
    """yna.co.kr 首页链到 yhitf.co.kr、egypt.dothome.co.kr 等别家站。修前 registrable() 取末两段,
    www.yna.co.kr → "co.kr",默认模式下把整个 .co.kr 当自家子域;asahi 的外链域聚合成 "co.jp"。"""

    def test_registrable_keeps_cc_second_level(self):
        import site_crawl as sc
        self.assertEqual(sc.registrable("www.yna.co.kr"), "yna.co.kr")
        self.assertEqual(sc.registrable("yhitf.co.kr"), "yhitf.co.kr")
        self.assertEqual(sc.registrable("www.cnn.co.jp"), "cnn.co.jp")
        self.assertEqual(sc.registrable("www.spiegel.de"), "spiegel.de")
        self.assertEqual(sc.registrable("www.example.co.uk"), "example.co.uk")

    def test_other_co_kr_sites_are_external(self):
        import site_crawl as sc
        import argparse
        html = fixture("ko-yna", "home-top.html").decode("utf-8")
        self.assertIn("https://yhitf.co.kr/", html)
        ns = argparse.Namespace(site="https://www.yna.co.kr/", urls=None, max_pages=5, delay=0.0,
                                ignore_robots=False, strip_params=False, same_host=False,
                                include_subdomains=True, subs="dns", check_external=False,
                                timeout=5.0, out=None, urls_out=None, json=False)
        c = sc.Crawler(ns)
        self.assertFalse(c.is_internal("yhitf.co.kr"))
        self.assertFalse(c.is_internal("egypt.dothome.co.kr"))
        self.assertTrue(c.is_internal("en.yna.co.kr"))


class SiteCrawlOrphanTests(unittest.TestCase):
    """asahi.com:sitemap 模式下修前从不抓首页,首页上指向文章的链接没进图;站内链接还都带
    ?iref= 跟踪参数,和 sitemap 里的干净 URL 对不上。结果 40 篇首页直链的文章全被判孤儿,
    orphan_fix 建议「新建 hub」。真实首页里每篇都有 4–8 处链接。"""

    def test_homepage_links_count_as_inlinks(self):
        import site_crawl as sc
        import argparse
        robots = fixture("ja-asahi", "robots.txt").decode("utf-8")
        index = fixture("ja-asahi", "sitemap.xml").decode("utf-8")
        national = fixture("ja-asahi", "sitemap_national.xml").decode("utf-8")
        home = fixture("ja-asahi", "home-links.html").decode("utf-8")
        routes = {"https://www.asahi.com/robots.txt": robots,
                  "https://www.asahi.com/sitemap.xml": index,
                  "https://www.asahi.com/sitemap/sitemap_national.xml": national,
                  "https://www.asahi.com/": home}

        def fake(url, timeout=10.0, method="GET"):
            body = routes.get(url)
            if body is None:
                status = 404 if url.endswith(".xml") else 200
                body = "" if status == 404 else "<html><head><title>a</title></head><body></body></html>"
            else:
                status = 200
            return {"status": status, "final_url": url, "chain": [], "headers": {},
                    "body": body, "body_bytes": body.encode("utf-8")}

        orig = (sc.http_fetch, sc.dns_resolve, sc._sleep)
        sc.http_fetch = fake
        def fake_dns(host):
            if host == "www.asahi.com":
                return ["93.184.216.34"]
            raise OSError("NXDOMAIN %s" % host)

        sc.dns_resolve = fake_dns
        sc._sleep = lambda t: None
        sc._ssrf_cache.clear()
        self.addCleanup(lambda: (setattr(sc, "http_fetch", orig[0]), setattr(sc, "dns_resolve", orig[1]),
                                 setattr(sc, "_sleep", orig[2]), sc._ssrf_cache.clear()))
        ns = argparse.Namespace(site="https://www.asahi.com/", urls=None, max_pages=10, delay=0.0,
                                ignore_robots=False, strip_params=False, same_host=True,
                                include_subdomains=True, subs="dns", check_external=False,
                                timeout=5.0, out=None, urls_out=None, json=False)
        report, _rc = sc.Crawler(ns).run()
        clean = {u for u in (p["url"] for p in report["pages"])
                 if "/articles/" in u and "?" not in u}
        self.assertEqual(len(clean), 3, [p["url"] for p in report["pages"]])
        self.assertEqual([u for u in report["orphans"] if u in clean], [])


class LinkGraphParamVariantTests(unittest.TestCase):
    """asahi.com:首页链接都带 ?iref= 参数,crawl.json 里的页面是 sitemap 的干净 URL。修前
    link_graph 只认两端完全相同的边:「内链边 0(带锚 15326)」,PageRank 40 页全是 10.00。"""

    def test_param_variant_edges_reach_clean_pages(self):
        import site_crawl as sc
        import link_graph as lg
        home = "https://www.asahi.com/"
        _t, _c, hrefs, _a = sc.extract_links(fixture("ja-asahi", "home-links.html").decode("utf-8"), home)
        dsts = [sc.normalize_url(h, home) for h in hrefs]
        self.assertTrue(all("?iref=" in d for d in dsts), dsts)
        clean = [d.split("?", 1)[0] for d in dsts]
        report = {"pages": [{"url": home, "status": 200, "source": "seed"}]
                  + [{"url": u, "status": 200, "source": "sitemap"} for u in clean],
                  "edges": [{"src": home, "dst": d} for d in dsts]}
        _pages, _urls, edges = lg.build_graph(report)
        self.assertEqual(sorted(d for _s, d in edges), sorted(clean))


class AboveFoldHiddenNoticeTests(unittest.TestCase):
    """spiegel.de 首页 body 开头有一段 404 提示(Alpine.js:x-show + x-cloak,只在 ?from=404 时显示)。
    修前被当成首屏文本:「Leider gibt es die von Ihnen gesuchte Seite nicht oder nicht mehr…」。"""

    def test_x_cloak_block_not_in_fold(self):
        import above_fold as af
        p = af.FoldParser()
        p.feed(fixture("de-spiegel", "home-top.html").decode("utf-8"))
        p.flush()
        fold = "".join(p.text_parts)
        self.assertIn("Leider gibt es die von Ihnen gesuchte Seite",
                      fixture("de-spiegel", "home-top.html").decode("utf-8"))
        self.assertNotIn("Leider gibt es die von Ihnen gesuchte Seite", fold)


class SitemapAuditIndexSamplingTests(unittest.TestCase):
    """spiegel.de 的 sitemap index 有 23,707 个子 sitemap,按年月升序、无 <lastmod>。修前
    --max-child 只展开前 N 个(1957、1961……年的归档),据此判「最新 lastmod 1978-05-29,过期」。"""

    def test_truncated_index_sample_includes_newest_end(self):
        import sitemap_audit as sa
        index = fixture("de-spiegel", "sitemap.xml")
        child = fixture("de-spiegel", "sitemap-2026-10_44.xml")
        fetched = []
        orig_fetch, orig_robots = sa.fetch, sa.robots_for

        class AllowAll:
            def can_fetch(self, ua, url):
                return True

        def fake(url, timeout=10.0, max_bytes=5_000_000):
            fetched.append(url)
            if url == "https://www.spiegel.de/sitemap.xml":
                return 200, {}, index
            if "/sitemaps/article/" in url:
                return 200, {}, child
            return 200, {}, b"<html><head><title>a</title></head><body>x</body></html>"

        sa.fetch = fake
        sa.robots_for = lambda url, timeout=10.0: AllowAll()
        self.addCleanup(setattr, sa, "fetch", orig_fetch)
        self.addCleanup(setattr, sa, "robots_for", orig_robots)
        rc, out, err = run_main(sa, ["https://www.spiegel.de/sitemap.xml", "--check-limit", "0",
                                     "--max-child", "3"])
        kids = [u for u in fetched if "/sitemaps/article/" in u]
        self.assertEqual(len(kids), 3, kids)
        self.assertIn("https://www.spiegel.de/sitemaps/article/sitemap-2026-10_44.xml", kids)


class NewsSitemapLongTitleTests(unittest.TestCase):
    """spiegel.de news sitemap 有 4 条 news:title ≥100 字符(都是页面上的真实文章标题)。修前报 WARN;
    Google news sitemap 文档对 <news:title> 只写「The title of the news article」,没有长度上限。"""

    def test_long_real_titles_not_warned(self):
        import re
        import news_sitemap_check as ns
        news = "https://www.spiegel.de/sitemaps/news-de.xml"
        body = fixture("de-spiegel", "news-de.xml")
        robots = fixture("de-spiegel", "robots.txt")
        orig = ns.http_fetch

        def fake(url, timeout=ns.FETCH_TIMEOUT, max_bytes=10 ** 9):
            if url == news:
                return 200, {}, body
            if url.endswith("/robots.txt"):
                return 200, {}, robots
            return 200, {}, b"<html><head><title>a</title></head><body>x</body></html>"

        ns.http_fetch = fake
        self.addCleanup(setattr, ns, "http_fetch", orig)
        rc, out, _ = run_main(ns, ["--url", news, "--sample", "0"])
        self.assertIn("4 条 title ≥100 字符", out)
        self.assertIsNone(re.search(r"⚠\s+ext\s+title", out), out)


class SiteCrawlIndexSamplingTests(unittest.TestCase):
    """spiegel.de:site_crawl 解析 sitemap index 时只展开前 SITEMAP_CHILD_CAP 个子表——按年月升序的
    index 里全是 1947 年起的归档,抓到的样本全是几十年前的旧文章。与 sitemap_audit 同类问题。"""

    def test_child_cap_sample_includes_newest(self):
        import site_crawl as sc
        import argparse
        index = fixture("de-spiegel", "sitemap.xml").decode("utf-8")
        child = fixture("de-spiegel", "sitemap-2026-10_44.xml").decode("utf-8")
        fetched = []

        def fake(url, timeout=10.0, method="GET"):
            fetched.append(url)
            if url == "https://www.spiegel.de/robots.txt":
                body = "User-agent: *\nSitemap: https://www.spiegel.de/sitemap.xml\n"
            elif url == "https://www.spiegel.de/sitemap.xml":
                body = index
            elif "/sitemaps/article/" in url:
                body = child
            else:
                body = "<html><head><title>a</title></head><body></body></html>"
            return {"status": 200, "final_url": url, "chain": [], "headers": {},
                    "body": body, "body_bytes": body.encode("utf-8")}

        orig = (sc.http_fetch, sc.dns_resolve, sc._sleep, sc.SITEMAP_CHILD_CAP)

        def fake_dns(host):
            if host == "www.spiegel.de":
                return ["93.184.216.34"]
            raise OSError("NXDOMAIN %s" % host)

        sc.http_fetch, sc.dns_resolve, sc._sleep, sc.SITEMAP_CHILD_CAP = fake, fake_dns, (lambda t: None), 3
        sc._ssrf_cache.clear()
        self.addCleanup(lambda: (setattr(sc, "http_fetch", orig[0]), setattr(sc, "dns_resolve", orig[1]),
                                 setattr(sc, "_sleep", orig[2]), setattr(sc, "SITEMAP_CHILD_CAP", orig[3]),
                                 sc._ssrf_cache.clear()))
        ns = argparse.Namespace(site="https://www.spiegel.de/", urls=None, max_pages=1, delay=0.0,
                                ignore_robots=False, strip_params=False, same_host=True,
                                include_subdomains=True, subs="dns", check_external=False,
                                timeout=5.0, out=None, urls_out=None, json=False)
        sc.Crawler(ns).run()
        kids = [u for u in fetched if "/sitemaps/article/" in u]
        self.assertEqual(len(kids), 3, kids)
        self.assertIn("https://www.spiegel.de/sitemaps/article/sitemap-2026-10_44.xml", kids)


class SiteCrawlSitemapByteCapTests(unittest.TestCase):
    """spiegel.de/sitemap.xml 是 2,249,195 字节的 index(23,707 个子 sitemap)。修前 site_crawl 对所有
    响应只读前 2,000,000 字节,XML 被截断,报「sitemap XML 解析失败: unclosed token」,整份文章 index
    被丢掉。Google 对单个 sitemap 的上限是 50MB(未压缩)。fixture 是完整原文的 gzip。"""

    def test_large_sitemap_not_truncated(self):
        import gzip
        import site_crawl as sc
        raw = gzip.decompress(fixture("de-spiegel", "sitemap-index-full.xml.gz"))
        self.assertGreater(len(raw), 2_000_000)

        class Resp:
            status = 200
            headers = {}

            def __init__(self, data):
                self.data = data

            def read(self, n=-1):
                return self.data if n is None or n < 0 else self.data[:n]

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        class Opener:
            def open(self, req, timeout=None):
                return Resp(raw)

        orig = (sc._OPENER, sc.ssrf_guard)
        sc._OPENER, sc.ssrf_guard = Opener(), (lambda host: None)
        self.addCleanup(lambda: (setattr(sc, "_OPENER", orig[0]), setattr(sc, "ssrf_guard", orig[1])))
        status, _h, body = sc._single("https://www.spiegel.de/sitemap.xml", "GET", 5.0)
        self.assertEqual(len(body), len(raw))
        kind, _urls, children = sc.parse_sitemap_bytes(body)
        self.assertEqual((kind, len(children)), ("sitemapindex", 23707))


class SiteCrawlTruncatedOrphanTests(unittest.TestCase):
    """asahi.com 修首页抓取后复跑:40 页样本里仍有 22 页「0 入链」——它们挂在没抓到的栏目页下
    (sitemap 218 条,只抓 40 页)。截断时样本内 0 入链不等于站内孤儿;修前 site_crawl 照常写
    「孤儿页」,orphan_fix 照常给内链修复清单,不提截断。"""

    def test_truncated_crawl_marks_orphans_partial(self):
        import site_crawl as sc
        import orphan_fix as of
        import argparse
        routes = {"https://www.asahi.com/robots.txt": fixture("ja-asahi", "robots.txt").decode("utf-8"),
                  "https://www.asahi.com/sitemap.xml": fixture("ja-asahi", "sitemap.xml").decode("utf-8"),
                  "https://www.asahi.com/sitemap/sitemap_national.xml":
                      fixture("ja-asahi", "sitemap_national.xml").decode("utf-8")}

        def fake(url, timeout=10.0, method="GET"):
            body = routes.get(url)
            status = 200 if body is not None or not url.endswith(".xml") else 404
            body = body if body is not None else ("" if status == 404 else
                                                  "<html><head><title>a</title></head><body></body></html>")
            return {"status": status, "final_url": url, "chain": [], "headers": {},
                    "body": body, "body_bytes": body.encode("utf-8")}

        def fake_dns(host):
            if host == "www.asahi.com":
                return ["93.184.216.34"]
            raise OSError("NXDOMAIN %s" % host)

        orig = (sc.http_fetch, sc.dns_resolve, sc._sleep)
        sc.http_fetch, sc.dns_resolve, sc._sleep = fake, fake_dns, (lambda t: None)
        sc._ssrf_cache.clear()
        self.addCleanup(lambda: (setattr(sc, "http_fetch", orig[0]), setattr(sc, "dns_resolve", orig[1]),
                                 setattr(sc, "_sleep", orig[2]), sc._ssrf_cache.clear()))
        ns = argparse.Namespace(site="https://www.asahi.com/", urls=None, max_pages=2, delay=0.0,
                                ignore_robots=False, strip_params=False, same_host=True,
                                include_subdomains=True, subs="dns", check_external=False,
                                timeout=5.0, out=None, urls_out=None, json=False)
        report, _rc = sc.Crawler(ns).run()
        self.assertTrue(report.get("orphans_partial"), report.get("stats"))
        self.assertIn("截断", sc.render_markdown(report))
        plans, _n = of.build_plan(report)
        payload_md = of.render_markdown({"site": "asahi.com", "orphans_total": len(report["orphans"]),
                                         "processed": len(plans), "max": 50, "max_candidates": 3,
                                         "plans": plans, "orphans_partial": report.get("orphans_partial")})
        self.assertIn("截断", payload_md)


class SitemapAuditRobotsNestedIndexTests(unittest.TestCase):
    """spiegel.de 给站点 URL:robots.txt 声明 4 个 sitemap,其中 sitemap.xml 本身是 23,707 个子表的
    index。按 robots 声明展开后,这个 index 成了第二层;修前第二层不展开,文章 sitemap 全没审到。"""

    def test_declared_index_children_are_sampled(self):
        import sitemap_audit as sa
        robots = fixture("de-spiegel", "robots.txt")
        index = fixture("de-spiegel", "sitemap.xml")
        child = fixture("de-spiegel", "sitemap-2026-10_44.xml")
        fetched = []
        orig_fetch, orig_robots = sa.fetch, sa.robots_for

        class AllowAll:
            def can_fetch(self, ua, url):
                return True

        def fake(url, timeout=10.0, max_bytes=5_000_000):
            fetched.append(url)
            if url == "https://www.spiegel.de/robots.txt":
                return 200, {}, robots
            if url == "https://www.spiegel.de/sitemap.xml":
                return 200, {}, index
            if "/sitemaps/article/" in url:
                return 200, {}, child
            if url.endswith(".xml"):
                return 404, {}, b"not found"
            return 200, {}, b"<html><head><title>a</title></head><body>x</body></html>"

        sa.fetch = fake
        sa.robots_for = lambda url, timeout=10.0: AllowAll()
        self.addCleanup(setattr, sa, "fetch", orig_fetch)
        self.addCleanup(setattr, sa, "robots_for", orig_robots)
        rc, out, err = run_main(sa, ["https://www.spiegel.de/", "--check-limit", "0", "--max-child", "3"])
        self.assertIn("https://www.spiegel.de/sitemaps/article/sitemap-2026-10_44.xml", fetched)


if __name__ == "__main__":
    unittest.main(verbosity=1)
