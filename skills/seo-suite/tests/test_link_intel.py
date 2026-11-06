#!/usr/bin/env python3
"""link_intel:竞品与外链发现。

期望值来自手搭的小图:每条边是测试里写死的「谁链谁」,答案按定义数出来(谁链到 ≥2 个种子、谁和谁互链),
不是读实现得来的。Common Crawl 文件格式照 2026-jul-aug-sep 版真实文件的前几行(顶点 id\\t反转域名\\t主机数,
边 from\\tto,名次文件 #harmonicc_pos ... #host_rev #n_hosts)。互换识别的真实对照见
references/research/link-intelligence.md「判据」(运营台已核实在线的回链)。
"""
import gzip
import os
import shutil
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
import link_intel as L  # noqa: E402

# 域名 → id(按反转域名排序后的行号,跟真实文件一样)
DOMAINS = ["brightdata.com", "oxylabs.io", "everyinfra.com", "proxyblog.net", "toolsreview.org",
           "spam-farm.xyz", "ipfoxy.com", "novproxy.com", "google.com"]
EDGES = [
    ("proxyblog.net", "brightdata.com"), ("proxyblog.net", "oxylabs.io"),        # 链 2 个种子、没链我们 → 候选
    ("toolsreview.org", "brightdata.com"), ("toolsreview.org", "oxylabs.io"),
    ("toolsreview.org", "everyinfra.com"),                                         # 链了我们 → 不是候选
    ("spam-farm.xyz", "brightdata.com"),                                           # 只链 1 个 → 不是候选
    ("ipfoxy.com", "novproxy.com"), ("novproxy.com", "ipfoxy.com"),               # 种子之间互链
    ("google.com", "brightdata.com"), ("google.com", "oxylabs.io"),               # 平台,单列
    ("brightdata.com", "proxyblog.net"),
]


def build_cc(tmp):
    rows = sorted((L.rev(d), d) for d in DOMAINS)
    ids = {d: str(i) for i, (_, d) in enumerate(rows)}
    with gzip.open(os.path.join(tmp, "v.gz"), "wt") as f:
        for i, (r, _) in enumerate(rows):
            f.write("%d\t%s\t1\n" % (i, r))
    with gzip.open(os.path.join(tmp, "e.gz"), "wt") as f:
        for a, b in sorted(EDGES, key=lambda e: int(ids[e[0]])):
            f.write("%s\t%s\n" % (ids[a], ids[b]))
    with gzip.open(os.path.join(tmp, "r.gz"), "wt") as f:
        f.write("#harmonicc_pos\t#harmonicc_val\t#pr_pos\t#pr_val\t#host_rev\t#n_hosts\n")
        for pos, d in enumerate(["google.com", "brightdata.com", "toolsreview.org", "proxyblog.net"], 1):
            f.write("%d\t1.0\t%d\t0.1\t%s\t1\n" % (pos, pos, L.rev(d)))
    return {"vertices": os.path.join(tmp, "v.gz"), "edges": os.path.join(tmp, "e.gz"), "ranks": os.path.join(tmp, "r.gz")}


class CCGraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="li_test_")
        self.local = build_cc(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def graph(self):
        return L.ccgraph(["brightdata.com", "oxylabs.io", "ipfoxy.com", "novproxy.com", "missing-site.com"],
                         own="everyinfra.com", release="test", ranks=True, local=self.local)

    def test_inlinks_and_missing(self):
        g = self.graph()
        self.assertEqual(g["inlinks"]["brightdata.com"],
                         ["google.com", "proxyblog.net", "spam-farm.xyz", "toolsreview.org"])
        self.assertEqual(g["inlinks"]["everyinfra.com"], ["toolsreview.org"])
        self.assertEqual(g["missing"], ["missing-site.com"])

    def test_mutual_between_targets(self):
        self.assertEqual(self.graph()["mutual"], [["ipfoxy.com", "novproxy.com"]])

    def test_ranks(self):
        r = self.graph()["ranks"]
        self.assertEqual(r["google.com"], 1)
        self.assertEqual(r["proxyblog.net"], 4)

    def test_intersect_candidates(self):
        rows, mutual = L.intersect(self.graph(), own="everyinfra.com", min_seeds=2, ledger={"proxyblog.net"})
        doms = [r["domain"] for r in rows]
        # proxyblog 链 2 个种子没链我们;toolsreview 链了我们;spam-farm 只链 1 个;google 是平台排最后
        self.assertEqual(doms, ["proxyblog.net", "google.com"])
        self.assertEqual(rows[0]["contacted"], 1)
        self.assertEqual(rows[1]["platform"], 1)
        self.assertEqual([(m["a"], m["b"]) for m in mutual], [("ipfoxy.com", "novproxy.com")])

    def test_crawl_evidence_overrides_snapshot(self):
        """链接图之后对方才放的链接:页面级证据把它从候选里拿掉。"""
        crawl = {"sites": [{"site": "proxyblog.net", "pages": [
            {"url": "https://proxyblog.net/partners/", "kind": "partner",
             "links": [{"domain": "everyinfra.com", "url": "https://everyinfra.com/", "rel": [], "anchor": "EveryInfra"}]}]}],
            "mutual": []}
        rows, _ = L.intersect(self.graph(), crawl, own="everyinfra.com", min_seeds=2)
        self.assertNotIn("proxyblog.net", [r["domain"] for r in rows])


class ListicleEvidenceTests(unittest.TestCase):
    def test_intersect_from_listicles_without_graph(self):
        """链接图拿不到时(Common Crawl 限流),只用榜单页的外链也能出候选:发榜单、列了 ≥2 个种子、没列我们的站。"""
        res = {"fetched": [
            {"url": "https://proxyway.com/best/scraping", "status": 200, "domains": ["brightdata.com", "oxylabs.io"]},
            {"url": "https://listy.io/top", "status": 200, "domains": ["brightdata.com", "oxylabs.io", "everyinfra.com"]},
            {"url": "https://one.io/x", "status": 200, "domains": ["brightdata.com"]},
        ]}
        crawl = {"sites": L.listicles_as_crawl(res), "mutual": []}
        rows, _ = L.intersect({"inlinks": {}, "mutual": []}, crawl, own="everyinfra.com", min_seeds=2,
                              seeds=["brightdata.com", "oxylabs.io"])
        self.assertEqual([(r["domain"], r["evidence_kind"]) for r in rows], [("proxyway.com", "listicle")])


class IndependentCheckTests(unittest.TestCase):
    """2026-11-06 独立核验抽 20 个候选时发现的三类误算。"""

    def test_nav_footer_links_not_counted(self):
        """bright data 页脚链自家姊妹站、厂商页头「预约演示」按钮,不是对同行的推荐。"""
        html = ('<header><a href="https://cal.example/demo">Book</a></header>'
                '<article><a href="https://oxylabs.io/">Oxylabs</a></article>'
                '<footer><div><a href="https://bright-sdk.com/">SDK</a></div></footer>'
                '<div role="navigation"><a href="https://webshare.io/">x</a></div>')
        links = L.external_links(html, "https://brightdata.com/blog/x")
        self.assertEqual([(l["domain"], l["chrome"]) for l in links],
                         [("cal.example", True), ("oxylabs.io", False), ("bright-sdk.com", True), ("webshare.io", True)])
        crawl = {"sites": [{"site": "brightdata.com", "pages": [{"url": "https://brightdata.com/blog/x", "kind": "partner",
                                                                 "links": links}]}], "mutual": []}
        rows, _ = L.intersect({"inlinks": {}, "mutual": []}, crawl, own="everyinfra.com", min_seeds=2,
                              seeds=["oxylabs.io", "bright-sdk.com", "webshare.io"])
        self.assertEqual(rows, [])          # 正文里只链了 1 个种子

    def test_reference_domains_not_seeds(self):
        """论文、法规、预约组件进了种子名单时,不能让一篇引用 arxiv 和 europa.eu 的文章凑够 2 个种子。"""
        crawl = {"sites": [{"site": "decodo.com", "pages": [{"url": "https://decodo.com/blog/a", "kind": "partner", "links": [
            {"domain": "arxiv.org", "rel": []}, {"domain": "europa.eu", "rel": []}, {"domain": "cal.com", "rel": []}]}]}],
            "mutual": []}
        rows, _ = L.intersect({"inlinks": {}, "mutual": []}, crawl, own="everyinfra.com", min_seeds=2,
                              seeds=["arxiv.org", "europa.eu", "cal.com"])
        self.assertEqual(rows, [])

    def test_followed_count(self):
        """榜单里同行链接多是 nofollow:另列一栏「至少一条 follow 的种子数」,外联时先看它。"""
        res = {"fetched": [{"url": "https://scrapingdog.com/blog/best-serp-apis/", "status": 200,
                            "domains": ["apify.com", "dataforseo.com", "hasdata.com"],
                            "nofollow": ["apify.com", "hasdata.com"]}]}
        rows, _ = L.intersect({"inlinks": {}, "mutual": []}, {"sites": L.listicles_as_crawl(res), "mutual": []},
                              own="everyinfra.com", min_seeds=2, seeds=["apify.com", "dataforseo.com", "hasdata.com"])
        self.assertEqual([(r["domain"], r["seeds_linked"], r["followed"]) for r in rows], [("scrapingdog.com", 3, 1)])


class SecondCheckTests(unittest.TestCase):
    """2026-11-06 第二轮独立核验发现的两类误算。"""

    def test_seeds_must_share_a_page(self):
        """proxyway:4 个种子分在 4 篇不同的文章里,每篇只链 1 家,不是在推荐同行。"""
        pages = [{"url": "https://proxyway.com/a%d" % i, "kind": "partner", "links": [{"domain": d, "rel": []}]}
                 for i, d in enumerate(["apify.com", "scrapingbee.com", "parsehub.com", "pixelscan.net"])]
        pages.append({"url": "https://other.io/best", "kind": "listicle", "links": []})
        crawl = {"sites": [{"site": "proxyway.com", "pages": pages[:4]},
                           {"site": "other.io", "pages": [{"url": "https://other.io/best", "kind": "listicle", "links": [
                               {"domain": "apify.com", "rel": []}, {"domain": "scrapingbee.com", "rel": []}]}]}],
                 "mutual": []}
        rows, _ = L.intersect({"inlinks": {}, "mutual": []}, crawl, own="everyinfra.com", min_seeds=2,
                              seeds=["apify.com", "scrapingbee.com", "parsehub.com", "pixelscan.net"])
        self.assertEqual([(r["domain"], r["best_page"]) for r in rows], [("other.io", 2)])

    def test_sibling_domains_count_once(self):
        """mattcollins.net 同时链 firecrawl.dev 和联盟短域 firecrawl.link,算一家。"""
        crawl = {"sites": [{"site": "blog.net", "pages": [{"url": "https://blog.net/x", "kind": "partner", "links": [
            {"domain": "firecrawl.dev", "rel": []}, {"domain": "firecrawl.link", "rel": []}]}]}], "mutual": []}
        rows, _ = L.intersect({"inlinks": {}, "mutual": []}, crawl, own="everyinfra.com", min_seeds=2,
                              seeds=["firecrawl.dev", "firecrawl.link"])
        self.assertEqual(rows, [])


class GraphPrecisionTests(unittest.TestCase):
    """2026-11-06 审查:文档第 5 步的命令同时给 --graph 和 --crawl / --listicles,而链接图里出现过的域原来
    一律跳过「同一页 ≥2 家」,链接图里的每个种子都记成 follow,上面两轮核验修的三条全部失效。
    Common Crawl 的边来自 <a>、<link>、<script>、og:image、跳转、robots.txt Sitemap 行,不看 rel
    (cc-pyspark wat_extract_links.py ExtractHostLinksJob.get_links / process_robotstxt,核对 2026-11-06)。
    期望值按文档对各列的定义写:有页面证据的按页面判;只有链接图的 follow 未知。"""

    GRAPH = {"inlinks": {"a-seed.com": ["x.com"], "b-seed.com": ["x.com"]}, "mutual": []}

    @staticmethod
    def crawl(pages):
        return {"sites": [{"site": "x.com", "pages": pages}], "mutual": []}

    @staticmethod
    def page(url, links):
        return {"url": url, "kind": "partner", "status": 200,
                "links": [{"domain": d, "rel": rel, "chrome": ch} for d, rel, ch in links]}

    def test_graph_does_not_bypass_same_page_rule(self):
        """x.com 两页各链一家(都 nofollow),链接图里也有它:没有一页在推荐同行,不是候选。"""
        crawl = self.crawl([self.page("https://x.com/p1", [("a-seed.com", ["nofollow"], False)]),
                            self.page("https://x.com/p2", [("b-seed.com", ["nofollow"], False)])])
        rows, _ = L.intersect(self.GRAPH, crawl, own="me.com", min_seeds=2)
        self.assertEqual(rows, [])

    def test_graph_does_not_fake_follow(self):
        """同一页链了两家,两条都是 nofollow:followed 是 0,不因为链接图里有这两条边就变成 2。"""
        crawl = self.crawl([self.page("https://x.com/best", [("a-seed.com", ["nofollow"], False),
                                                              ("b-seed.com", ["sponsored"], False)])])
        rows, _ = L.intersect(self.GRAPH, crawl, own="me.com", min_seeds=2)
        self.assertEqual([(r["domain"], r["seeds_linked"], r["followed"]) for r in rows], [("x.com", 2, 0)])
        self.assertEqual(rows[0]["graph_seeds"], 2)              # 链接图里的数另记一列,不参与判断

    def test_graph_does_not_count_footer_links(self):
        """两家都只在页脚:页面证据说它没在正文推荐同行,链接图(不分正文和页脚)不能把它加回来。"""
        crawl = self.crawl([self.page("https://x.com/", [("a-seed.com", [], True), ("b-seed.com", [], True)])])
        rows, _ = L.intersect(self.GRAPH, crawl, own="me.com", min_seeds=2)
        self.assertEqual(rows, [])

    def test_graph_only_rows_follow_unknown_and_ranked_after_page_rows(self):
        """只有链接图证据的 y.com 链了 3 家,有页面证据的 z.com 链了 2 家:z.com 在前;y.com 的 follow 未知。"""
        graph = {"inlinks": {"a-seed.com": ["y.com"], "b-seed.com": ["y.com"], "c-seed.com": ["y.com"]}, "mutual": []}
        crawl = {"sites": [{"site": "z.com", "pages": [self.page("https://z.com/best", [
            ("a-seed.com", [], False), ("b-seed.com", [], False)])]}], "mutual": []}
        rows, _ = L.intersect(graph, crawl, own="me.com", min_seeds=2)
        self.assertEqual([(r["domain"], r["followed"], r["evidence_kind"]) for r in rows],
                         [("z.com", 2, "partner"), ("y.com", "", "commoncrawl")])
        self.assertEqual(rows[1]["seeds_linked"], 3)


class ExchangerTests(unittest.TestCase):
    def test_hosts_and_listed(self):
        """互换池:有 /partners 页列了 ≥3 个外站的站是「在做互换的站」;页上列的外站按被几家列出计数。
        博客里的工具推荐、我们自己的合作页不算。"""
        def page(url, doms, kind="partner"):
            return {"url": url, "kind": kind, "links": [{"domain": d, "rel": []} for d in doms]}
        crawl = {"sites": [
            {"site": "a-proxy.com", "pages": [page("https://a-proxy.com/partners", ["x.io", "y.io", "everyinfra.com"])]},
            {"site": "b-browser.com", "pages": [page("https://b-browser.com/links", ["x.io", "z.io", "w.io"]),
                                                page("https://b-browser.com/blog/tools", ["q.io", "r.io", "s.io"])]},
            {"site": "everyinfra.com", "pages": [page("https://everyinfra.com/partners", ["x.io", "a-proxy.com", "k.io"])]},
        ]}
        rows = L.exchangers(crawl, own="everyinfra.com", ledger={"z.io"})
        got = {(r["domain"], r["role"], r["count"], r["links_us"], r["contacted"]) for r in rows}
        self.assertEqual(got, {("a-proxy.com", "host", 3, 1, 0), ("b-browser.com", "host", 3, 0, 0),
                               ("x.io", "listed", 2, 0, 0), ("y.io", "listed", 1, 0, 0),
                               ("z.io", "listed", 1, 0, 1), ("w.io", "listed", 1, 0, 0)})


class CrawlBudgetTests(unittest.TestCase):
    def test_own_brand_and_partner_pages_first(self):
        """2026-11-06 一次抓 196 个站:proxies.sx、coronium、datacircle 的博客里以别家命名的页有上百篇,
        把 30 页上限占满,给我们的那页没抓到(8 个站单独抓时能找到)。我们的品牌词页、合作页要先抓。"""
        urls = ["https://p.sx/blog/apify-proxy-%d" % i for i in range(40)]
        urls += ["https://p.sx/partners", "https://p.sx/blog/everyinfra-review"]
        sm = "<urlset>" + "".join("<url><loc>%s</loc></url>" % u for u in urls) + "</urlset>"
        orig = L.fetch
        L.fetch = lambda u, timeout=12.0: (200, u, sm) if u.endswith("sitemap.xml") else (404, u, "")
        try:
            got = L.partner_pages("p.sx", "", "https://p.sx/", 5, brands=["apify", "everyinfra"], first=["everyinfra"])
        finally:
            L.fetch = orig
        self.assertEqual(got[:2], ["https://p.sx/blog/everyinfra-review", "https://p.sx/partners"])
        self.assertEqual(len(got), 5)


class PageLevelTests(unittest.TestCase):
    def test_external_links_rel_and_meta(self):
        html = ('<meta name="robots" content="index,nofollow"><a href="/x">in</a>'
                '<a href="https://www.novproxy.com/?ref=a" rel="sponsored">Nov <b>Proxy</b></a>'
                '<a href="https://sub.everyinfra.com/zh/">EI</a>')
        links = L.external_links(html, "https://ipfoxy.com/partners/")
        self.assertEqual([l["domain"] for l in links], ["novproxy.com", "everyinfra.com"])
        self.assertEqual(links[0]["rel"], ["nofollow", "sponsored"])   # 页面级 nofollow 并进来
        self.assertEqual(links[0]["anchor"], "Nov Proxy")

    def test_malformed_href_skipped(self):
        """2026-11-06 跑 195 个站时,某页的 href 是没闭合的 IPv6 网址,urlsplit 抛 ValueError 把整批带崩。"""
        links = L.external_links('<a href="http://[::1/x">bad</a><a href="https://a.com/">ok</a>', "https://b.com/")
        self.assertEqual([l["domain"] for l in links], ["a.com"])
        self.assertEqual(L.registrable("http://[::1/x"), "")

    def test_page_mutual(self):
        crawled = [
            {"site": "everyinfra.com", "pages": [{"url": "https://everyinfra.com/partners/ipfoxy", "kind": "partner",
                                                  "links": [{"domain": "ipfoxy.com", "rel": []}]}]},
            {"site": "ipfoxy.com", "pages": [{"url": "https://www.ipfoxy.com/partners/", "kind": "partner",
                                              "links": [{"domain": "everyinfra.com", "rel": []}]}]},
            {"site": "oxylabs.io", "pages": [{"url": "https://oxylabs.io/", "kind": "home",
                                              "links": [{"domain": "everyinfra.com", "rel": []}]}]},
        ]
        m = L.page_mutual(crawled, "everyinfra.com")
        self.assertEqual([(x["a"], x["b"]) for x in m], [("everyinfra.com", "ipfoxy.com")])
        self.assertTrue(m[0]["involves_own"])

    def test_page_type(self):
        cases = {
            "https://www.scraperapi.com/alternatives/bright-data/": "comparison",
            "https://oxylabs.io/blog/best-proxy": "blog",
            "https://docs.brightdata.com/scraping/": "docs",
            "https://brightdata.com/products/web-scraper/tiktok": "product",
            "https://apify.com/clockworks/tiktok-scraper": "product",
            "https://www.scrapingbee.com/": "home",
            "https://firecrawl.dev/glossary/headless-browser": "glossary",
            "https://brightdata.com/pricing": "pricing",
        }
        for url, want in cases.items():
            self.assertEqual(L.page_type(url), want, url)


class ListicleTests(unittest.TestCase):
    def test_publishers_not_articles(self):
        """2026-11-06 首跑的真实噪音:brightdata 自家 9 篇文章页脚都链 brightdata.de,把分站顶成第 10 名;
        文章页「用 AI 总结」按钮让 perplexity.ai 进了 45 篇。按「几家网站提到」计数后都该出局。"""
        fetched = [
            {"url": "https://brightdata.com/blog/best-proxies-%d" % i, "category": "proxy",
             "domains": ["brightdata.de", "oxylabs.io", "perplexity.ai"]} for i in range(9)
        ] + [
            {"url": "https://proxyway.com/best/residential", "category": "proxy",
             "domains": ["oxylabs.io", "iproyal.com", "brightdata.com", "miit.gov.cn"]},
            {"url": "https://www.techradar.com/best/proxy", "category": "proxy",
             "domains": ["iproyal.com", "brightdata.com", "perplexity.ai"]},
        ]
        seeds = {s["domain"]: s["publisher_count"] for s in L.aggregate_listicles(fetched, 2)}
        self.assertEqual(seeds, {"oxylabs.io": 2, "iproyal.com": 2, "brightdata.com": 2})


class ProspectTests(unittest.TestCase):
    PAGES = {
        "https://toolsreview.org/resources/": (
            '<a href="https://deadproxy.com/pricing">DeadProxy</a>'
            '<a href="https://oxylabs.io/">Oxylabs</a>'
            '<a href="https://gone-scraper.io/">Gone</a>'
            '<a href="https://everyinfra.com/">EI</a>'
            '<a href="https://twitter.com/x">tw</a>'),
        "https://blog.example.net/tools": "<p>We tried Every Infra for TikTok data.</p><a href='https://oxylabs.io'>o</a>",
        "https://linked.example.org/a": "<p>EveryInfra is fine</p><a href='https://www.everyinfra.com/en'>ei</a>",
        "https://x.com/someone/status/1": "<p>EveryInfra</p>",
    }
    STATUS = {"https://deadproxy.com/pricing": (404, ""), "https://oxylabs.io/": (200, ""),
              "https://gone-scraper.io/": (0, "DNS")}

    def fetcher(self, url):
        return (200, url, self.PAGES[url]) if url in self.PAGES else (404, url, "")

    def test_deadlinks(self):
        res = L.deadlinks(["https://toolsreview.org/resources/"], own="everyinfra.com",
                          fetcher=self.fetcher, checker=lambda u: self.STATUS.get(u, (200, "")))
        self.assertEqual([(d["dead_url"], d["status"]) for d in res["dead"]],
                         [("https://deadproxy.com/pricing", 404), ("https://gone-scraper.io/", 0)])

    def test_unlinked(self):
        res = L.unlinked(list(self.PAGES), "everyinfra.com", r"every\s?infra", fetcher=self.fetcher)
        self.assertEqual([r["page"] for r in res], ["https://blog.example.net/tools"])


class FootprintTests(unittest.TestCase):
    def test_gaps_and_counts(self):
        serp = {"keywords": [
            {"keyword": "tiktok scraper api", "results": [
                {"rank": 1, "url": "https://apify.com/clockworks/tiktok-scraper"},
                {"rank": 2, "url": "https://brightdata.com/products/web-scraper/tiktok"}]},
            {"keyword": "apify alternatives", "results": [
                {"rank": 1, "url": "https://www.scraperapi.com/alternatives/apify/"},
                {"rank": 4, "url": "https://everyinfra.com/en/blog/apify-alternatives"}]},
            {"keyword": "serp api", "results": [{"rank": 3, "url": "https://serpapi.com/"}]},
        ]}
        f = L.footprint(serp, ["apify.com", "scraperapi.com", "serpapi.com"], own="everyinfra.com")
        self.assertEqual(f["own_ranked"], {"apify alternatives": 4})
        gaps = f["gaps_by_winning_page_type"]
        self.assertEqual([g["keyword"] for g in gaps["product"]], ["tiktok scraper api"])
        self.assertEqual([g["keyword"] for g in gaps["home"]], ["serp api"])
        apify = f["competitors"][0]
        self.assertEqual((apify["keywords_ranked"], apify["top3"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
