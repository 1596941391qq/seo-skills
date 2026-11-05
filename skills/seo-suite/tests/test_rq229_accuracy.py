#!/usr/bin/env python3
"""RQ-229 第 3 批「精度和覆盖」回归测试(零网络,全部打桩)。

期望值来源(都不来自读实现):
- 2026-11-05 评分的实测输入:sspai /sitemap.xml 原始响应(200 text/html 页面壳,2709 字节,
  fixtures/rq229-accuracy/sspai-sitemap-xml.html)、sspai 首页 og:url="/"、plausible 首页标题序列
  h3 h3 h3 h1 h2、plausible sitemap 第 160 条之后的 Google 验证文件 URL(302)、everyinfra/plausible
  的 site_crawl 摘要把子域根页写成「loc<50 兜底开着」(实际 2769 / 167 条 loc)。
- 规范原文:llmstxt.org v2(index.html.md 或 index.md)、ogp.me Types 表(URL 须 http(s)://)、
  W3C WAI Headings 教程(h1 前允许 h2 级结构标题,不跳级)、Lighthouse plugins 审计源码
  (core/audits/seo/plugins.js:applet;type 名单;swf/flv/class/xap;param code/movie/source/src)、
  Bing「Robots meta tags and attributes that Bing supports」(name="bingbot" 只对 Bing;
  max-video-preview 整数秒,0=静态图,-1=不限)、Bing 2012 博客与 Google robots.txt 规范
  (子域各自一份 robots.txt,缺失=全放行)、Ahrefs 帮助文(重定向目标只经重定向可达、HTTPS→HTTP
  重定向、HTTP/HTTPS 混链、外链 3xx、Page and SERP titles do not match)。
修前红:同一文件在 origin/main(7732f0e)的脚本上跑,修复类用例全部失败(见提交说明)。
"""
import contextlib
import io
import os
import re
import sys
import unittest
import urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
FIX = os.path.join(BASE, "tests", "fixtures", "rq229-accuracy")
REFS = os.path.join(BASE, "references")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import head_check  # noqa: E402
import llmstxt  # noqa: E402
import redirect_chain  # noqa: E402
import site_audit as sa  # noqa: E402
import site_crawl as sc  # noqa: E402
import sitemap_audit as sma  # noqa: E402
sma._sleep = lambda _s: None   # 逐条检查的礼貌间隔在测试里不真等
from test_site_crawl import FakeWeb, crawl, make_ns, urlset_xml, html_links  # noqa: E402


def fixture(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class _Hdr(dict):
    """sitemap_audit.fetch 返回的 headers 替身:get 大小写不敏感 + get_all。"""

    def get(self, k, default=None):
        for kk, v in self.items():
            if kk.lower() == k.lower():
                return v
        return default

    def get_all(self, k):
        v = self.get(k)
        return [v] if v is not None else []


@contextlib.contextmanager
def sitemap_web(routes):
    """routes={url: (status, headers_dict, body_bytes)};未登记 → 404。"""
    orig = sma.fetch
    sma._ROBOTS_CACHE.clear()

    def fake(url, timeout=10.0, max_bytes=5_000_000):
        st, hdr, body = routes.get(url, (404, {}, b""))
        return st, _Hdr(hdr), body
    sma.fetch = fake
    try:
        yield
    finally:
        sma.fetch = orig
        sma._ROBOTS_CACHE.clear()


def run_sitemap(argv):
    buf, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
        rc = sma.main(argv)
    return rc, buf.getvalue() + err.getvalue()


def urlset(locs):
    return ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join("<url><loc>%s</loc></url>" % u for u in locs) + "</urlset>").encode()


PAGE_OK = (200, {"Content-Type": "text/html"}, b"<html><head><title>x</title></head><body>ok</body></html>")


# ---------------------------------------------------------------- A1 sitemap 返回 HTML
class SitemapSoft404(unittest.TestCase):
    def test_sspai_html_sitemap_is_finding_not_fatal(self):
        body = fixture("sspai-sitemap-xml.html").encode()
        with sitemap_web({"https://sspai.com/sitemap.xml": (200, {"Content-Type": "text/html"}, body)}):
            rc, out = run_sitemap(["https://sspai.com"])
        self.assertEqual(rc, 1, out)                       # 站点问题,不是输入错误(修前 2 + FATAL)
        self.assertIn("不是 sitemap", out)
        self.assertIn("软 404", out)
        self.assertNotIn("[FATAL]", out)

    def test_redirect_to_homepage_is_soft404(self):
        home = b"<!DOCTYPE html><html><head><title>Home</title></head><body>hi</body></html>"
        with sitemap_web({
            "https://e.com/sitemap.xml": (301, {"Location": "https://e.com/"}, b""),
            "https://e.com/": (200, {"Content-Type": "text/html; charset=utf-8"}, home),
        }):
            rc, out = run_sitemap(["https://e.com/sitemap.xml"])
        self.assertEqual(rc, 1, out)
        self.assertIn("1 次重定向到 https://e.com/", out)

    def test_html_child_sitemap_counted(self):
        index = (b'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                 b"<sitemap><loc>https://e.com/a.xml</loc></sitemap><sitemap><loc>https://e.com/b.xml</loc></sitemap>"
                 b"</sitemapindex>")
        with sitemap_web({
            "https://e.com/sitemap.xml": (200, {"Content-Type": "application/xml"}, index),
            "https://e.com/a.xml": (200, {"Content-Type": "application/xml"}, urlset(["https://e.com/p"])),
            "https://e.com/b.xml": (200, {"Content-Type": "text/html"}, b"<html><body>404</body></html>"),
            "https://e.com/p": PAGE_OK,
        }):
            rc, out = run_sitemap(["https://e.com/sitemap.xml"])
        self.assertEqual(rc, 1, out)
        self.assertIn("https://e.com/b.xml", out)

    def test_real_xml_still_passes(self):
        with sitemap_web({"https://e.com/sitemap.xml": (200, {"Content-Type": "application/xml"},
                                                        urlset(["https://e.com/p"])),
                          "https://e.com/p": PAGE_OK}):
            rc, out = run_sitemap(["https://e.com/sitemap.xml"])
        self.assertEqual(rc, 0, out)


# ---------------------------------------------------------------- A7 sitemap 覆盖率
class SitemapCoverage(unittest.TestCase):
    def _site(self, n, redirect_at):
        locs = ["https://e.com/p%d" % i for i in range(n)]
        routes = {"https://e.com/sitemap.xml": (200, {"Content-Type": "application/xml"}, urlset(locs))}
        for i, u in enumerate(locs):
            routes[u] = PAGE_OK
        routes[locs[redirect_at]] = (302, {"Location": "https://www.google.com/"}, b"")
        return routes, locs

    def test_plausible_shape_late_redirect_is_found(self):
        # plausible 2026-11-05:167 条 loc,Google 验证文件排在第 160 条之后、会 302;修前只查前 50 条漏报
        routes, locs = self._site(167, 165)
        with sitemap_web(routes):
            rc, out = run_sitemap(["https://e.com/sitemap.xml"])
        self.assertEqual(rc, 1, out)
        self.assertIn(locs[165], out)
        self.assertIn("逐条检查 167/167 个 loc(全量", out)

    def test_large_sitemap_samples_and_says_so(self):
        routes, locs = self._site(600, 599)                 # 末条一定在样本里(含首尾)
        with sitemap_web(routes):
            rc, out = run_sitemap(["https://e.com/sitemap.xml"])
        self.assertIn("逐条检查 500/600 个 loc(按位置均匀抽样,含首尾", out)
        self.assertIn(locs[599], out)
        self.assertEqual(rc, 1)

    def test_check_limit_zero_means_all(self):
        routes, _ = self._site(60, 0)
        with sitemap_web(routes):
            _rc, out = run_sitemap(["https://e.com/sitemap.xml", "--check-limit", "0"])
        self.assertIn("逐条检查 60/60 个 loc(全量;--check-limit 0)", out)


# ---------------------------------------------------------------- A2 llms.txt 文件名标签
class LlmsTxtLabels(unittest.TestCase):
    def _check(self, routes):
        orig = llmstxt.fetch

        def fake(url):
            v = routes.get(url)
            if v is None:
                raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
            return v
        llmstxt.fetch = fake
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                llmstxt.check("https://sspai.com")
        finally:
            llmstxt.fetch = orig
        return buf.getvalue()

    def test_index_md_html_named_by_its_own_path(self):
        shell = fixture("sspai-sitemap-xml.html")             # sspai 对任意路径回同一个 SPA 壳
        out = self._check({"https://sspai.com" + p: (200, shell)
                           for p in ("/llms.txt", "/llms-full.txt", "/index.md", "/index.html.md")})
        line = [ln for ln in out.splitlines() if ln.startswith("/index.md ")][0]
        self.assertIn("/index.md 返回 HTML", line)
        self.assertNotIn("llms.txt", line)                    # 修前:「llms.txt is HTML not markdown」

    def test_either_markdown_twin_accepted(self):
        out = self._check({"https://sspai.com/llms.txt": (200, "# Site\n> s\n"),
                           "https://sspai.com/index.md": (200, "# Home\n\ntext\n")})
        self.assertIn("/index.md 可用", out)
        self.assertRegex(out, r"/index\.html\.md\s+404\s+\[NONE\]")   # 另一种写法缺失只是没提供
        self.assertRegex(out, r"/llms-full\.txt\s+404\s+\[NONE\]")


# ---------------------------------------------------------------- A3 site_crawl 汇总口径
HOME = "https://example.com/"


class CrawlSummaryWording(unittest.TestCase):
    def test_subdomain_roots_not_called_fallback(self):
        locs = [HOME] + ["https://example.com/p%d" % i for i in range(60)]
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml(locs))
        for u in locs:
            web.add(u, body=html_links("T", []))
        web.add("https://www.example.com/", body=html_links("W", []))
        rep, _rc = crawl(make_ns(), web, dns_hosts=("www.example.com",))
        md = sc.render_markdown(rep)
        line = [ln for ln in md.splitlines() if ln.startswith("- 发现模式")][0]
        self.assertNotIn("兜底开着", line)                      # 修前:「爬虫补量 1(loc<50 兜底开着)」
        self.assertIn("爬虫补量关闭", line)
        self.assertIn("子域根页 1", line)
        self.assertFalse(rep["discovery"]["crawl_fallback"])

    def test_small_sitemap_fallback_on(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["/a"]))
        web.add("https://example.com/a", body=html_links("A", []))
        rep, _rc = crawl(make_ns(), web)
        line = [ln for ln in sc.render_markdown(rep).splitlines() if ln.startswith("- 发现模式")][0]
        self.assertIn("爬虫补量开着", line)
        self.assertTrue(rep["discovery"]["crawl_fallback"])


# ---------------------------------------------------------------- A4 itemprop 与 --market 文档
class HeadCheckMarketDoc(unittest.TestCase):
    def _findings(self, html, market=None):
        got = []
        head_check.check(html.encode(), html, "utf-8", "text/html; charset=utf-8",
                         lambda sev, msg: got.append((sev, msg)), market=market)
        return got

    def test_chinese_page_checked_without_market_flag(self):
        html = ('<html lang="zh-CN"><head><meta charset="utf-8"><title>少数派 - 高效工作,品质生活</title>'
                '</head><body>正文</body></html>')
        msgs = " ".join(m for _s, m in self._findings(html))
        self.assertIn("itemprop 三件套缺失", msgs)

    def test_script_catalog_no_longer_claims_flag_required(self):
        with open(os.path.join(REFS, "overview", "script-catalog.md"), encoding="utf-8") as f:
            cat = f.read()
        self.assertNotIn("显式 `--market zh` 才查", cat)     # 修前文档说要显式加,实际自动识别


# ---------------------------------------------------------------- A5 相对 og:url
SSPAI_HEAD = ('<html lang="zh-CN"><head><meta charset="utf-8"><title>少数派 - 高效工作，品质生活</title>'
              '<meta property="og:title" content="少数派 - 高效工作，品质生活" />'
              '<meta property="og:image" content="https://cdn.sspai.com/x.png" />'
              '<meta property="og:url" content="/" /></head><body></body></html>')


def audit_page(head_extra="", body="", headers=None, serp_titles=None, url="https://example.com/self"):
    html = ('<!doctype html><html lang="en"><head><title>Example Article Page Title Long Enough</title>'
            '<meta name="description" content="A sufficiently long description text that exceeds eighty '
            'characters easily for tests.">' + head_extra + '</head><body><main><article>'
            + (body or "<h1>Main</h1><h2>A</h2><h2>B</h2>")
            + "<p>" + "filler content word " * 120 + "</p></article></main></body></html>")
    table = {url: (200, headers or {}, html),
             "https://example.com/robots.txt": (200, {}, "User-agent: *\nAllow: /\n"),
             "https://example.com/sitemap.xml": (200, {}, "<urlset/>"),
             "https://example.com/llms.txt": (200, {}, "# l\n")}

    def fake(u, timeout=15):
        if u in table:
            return table[u]
        raise urllib.error.HTTPError(u, 404, "Not Found", {}, None)
    orig = sa.fetch
    sa.fetch = fake
    try:
        if serp_titles is None:
            return sa.audit(url, "en")                    # 旧签名也能跑,修前红看的是断言而不是 TypeError
        return sa.audit(url, "en", serp_titles)
    finally:
        sa.fetch = orig


class OgUrlRelative(unittest.TestCase):
    def test_head_check_flags_relative_og_url(self):
        got = []
        head_check.check(SSPAI_HEAD.encode(), SSPAI_HEAD, "utf-8", "", lambda s, m: got.append((s, m)))
        self.assertTrue(any(s == "warn" and "og:url 非绝对" in m for s, m in got), got)

    def test_site_audit_flags_relative_og_url(self):
        F, _m, _a = audit_page('<meta property="og:url" content="/">')
        self.assertIn("og-url-not-absolute", [sa.rule_slug(a, m) for _s, a, m in F])

    def test_absolute_og_url_ok(self):
        F, _m, _a = audit_page('<meta property="og:url" content="https://example.com/self">')
        self.assertNotIn("og-url-not-absolute", [sa.rule_slug(a, m) for _s, a, m in F])


# ---------------------------------------------------------------- A6 h1 前的 h3
class HeadingsBeforeH1(unittest.TestCase):
    def test_plausible_h3_before_h1(self):
        body = ("<header><h3>Who it's for</h3><h3>Compare</h3><h3>Follow Plausible</h3></header>"
                "<h1>Easy to use and privacy-friendly Google Analytics alternative</h1>"
                "<h2>Why use Plausible Analytics?</h2><h2>People love Plausible</h2>")
        F, _m, _a = audit_page(body=body)
        hs = [m for _s, a, m in F if a == "headings"]
        self.assertTrue(any("h3 出现在第一个 h1 之前" in m for m in hs), hs)   # 修前无任何 headings 发现

    def test_h2_nav_before_h1_allowed(self):
        # W3C WAI「Main heading after navigation」:结构标题与正文小标题同为 h2,可以排在 h1 前
        body = "<nav><h2>Menu</h2></nav><h1>Title</h1><h2>A</h2><h2>B</h2>"
        F, _m, _a = audit_page(body=body)
        self.assertFalse([m for _s, a, m in F if a == "headings" and "之前" in m])


# ---------------------------------------------------------------- B 插件 / SERP 标题
class PluginsLighthouse(unittest.TestCase):
    def _slugs(self, body):
        F, _m, _a = audit_page(body="<h1>T</h1><h2>a</h2><h2>b</h2>" + body)
        return [m for _s, a, m in F if sa.rule_slug(a, m) == "rendering-plugins"]

    def test_flash_and_applet_flagged(self):
        self.assertTrue(self._slugs('<object type="application/x-shockwave-flash" data="a"></object>'))
        self.assertTrue(self._slugs('<embed src="/media/intro.swf">'))
        self.assertTrue(self._slugs('<applet code="Game.class"></applet>'))
        self.assertTrue(self._slugs('<object><param name="movie" value="clip.swf"></object>'))

    def test_non_plugin_embeds_ignored(self):
        self.assertFalse(self._slugs('<object type="image/svg+xml" data="logo.svg"></object>'))
        self.assertFalse(self._slugs('<embed src="/docs/manual.pdf" type="application/pdf">'))
        self.assertFalse(self._slugs('<object data="video.mp4"><param name="autoplay" value="x.swf"></object>'))


class SerpTitles(unittest.TestCase):
    URL = "https://example.com/self"

    def test_mismatch_reported(self):
        F, meta, _a = audit_page(serp_titles={sa._url_key(self.URL): "Totally Different Title | Example"})
        self.assertIn("title-serp-mismatch", [sa.rule_slug(a, m) for _s, a, m in F])
        self.assertFalse(meta["serp_title_check"]["match"])

    def test_truncated_serp_title_counts_as_match(self):
        F, meta, _a = audit_page(serp_titles={sa._url_key(self.URL + "/"): "Example Article Page Title ..."})
        self.assertTrue(meta["serp_title_check"]["match"])
        self.assertNotIn("title-serp-mismatch", [sa.rule_slug(a, m) for _s, a, m in F])

    def test_no_data_means_skip_with_reason(self):
        F, meta, _a = audit_page()
        self.assertFalse(meta["serp_title_check"]["checked"])
        self.assertIn("GSC", meta["serp_title_check"]["reason"])
        self.assertNotIn("title-serp-mismatch", [sa.rule_slug(a, m) for _s, a, m in F])

    def test_csv_loader(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("url,title\nhttps://Example.com/self/,Some SERP Title\n")
        try:
            d = sa.load_serp_titles(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(d[sa._url_key(self.URL)], "Some SERP Title")


# ---------------------------------------------------------------- C Bing 专属指令
class BingDirectives(unittest.TestCase):
    def _robots(self, head_extra="", headers=None):
        F, _m, _a = audit_page(head_extra, headers=headers)
        return [(s, m) for s, a, m in F if a == "robots"]

    def test_bingbot_meta_noindex_is_bing_only(self):
        r = self._robots('<meta name="bingbot" content="noindex">')
        self.assertNotIn(("CRITICAL", "noindex"), r)
        self.assertTrue(any(s == "WARN" and "只对 Bing 生效" in m for s, m in r), r)

    def test_bingbot_header_noindex_is_bing_only(self):
        r = self._robots(headers={"X-Robots-Tag": "bingbot: noindex"})
        self.assertNotIn(("CRITICAL", "noindex"), r)          # 修前:子串命中 noindex → CRITICAL
        self.assertTrue(any("bingbot noindex" in m for _s, m in r), r)

    def test_googlebot_meta_noindex_detected(self):
        self.assertIn(("CRITICAL", "noindex"), self._robots('<meta name="googlebot" content="noindex">'))

    def test_none_equals_noindex(self):
        self.assertIn(("CRITICAL", "noindex"), self._robots('<meta name="robots" content="none">'))

    def test_max_video_preview_values(self):
        bad = self._robots('<meta name="bingbot" content="max-video-preview:long">')
        self.assertTrue(any(s == "WARN" and "max-video-preview" in m for s, m in bad), bad)
        zero = self._robots('<meta name="robots" content="max-video-preview:0">')
        self.assertTrue(any(s == "INFO" and "静态图" in m for s, m in zero), zero)
        ok = self._robots('<meta name="robots" content="max-video-preview:-1, max-image-preview:large">')
        self.assertFalse([m for _s, m in ok if "max-video-preview" in m], ok)


# ---------------------------------------------------------------- B/C 跨页:site_crawl
class CrawlLinkIssues(unittest.TestCase):
    def test_redirect_target_only_reached_via_redirect(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["/old"]))
        web.add("https://example.com/old", body=html_links("New", []),
                chain=[{"status": 301, "location": "https://example.com/new"}],
                final_url="https://example.com/new")
        rep, _rc = crawl(make_ns(), web)
        rows = rep["link_issues"]["redirect_target_no_direct_inlinks"]
        self.assertEqual([r["target"] for r in rows], ["https://example.com/new"])
        self.assertEqual(rows[0]["via"], ["https://example.com/old"])

    def test_direct_link_clears_it(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["/old", "/new"]))
        web.add("https://example.com/old", body=html_links("New", []),
                chain=[{"status": 301, "location": "https://example.com/new"}],
                final_url="https://example.com/new")
        web.add("https://example.com/new", body=html_links("New", []))
        rep, _rc = crawl(make_ns(), web)
        self.assertEqual(rep["link_issues"]["redirect_target_no_direct_inlinks"], [])

    def test_trailing_slash_site_no_false_redirect_targets(self):
        # 11-05 独立评分实测 ma.tt(WordPress,链接都带尾斜杠):12 页 11 页误报「只能经重定向到达」。
        # 期望值来自站点行为:首页直接链着 /blog/a/,它不是重定向目标;只有 /new/ 是。
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["/blog/a/", "/old/"]))
        web.add("https://example.com/blog/a/", body=html_links("A", []))
        web.add("https://example.com/blog/a", body=html_links("A", []),          # nginx 习惯:缺斜杠 301 补上
                chain=[{"status": 301, "location": "https://example.com/blog/a/"}],
                final_url="https://example.com/blog/a/")
        web.add("https://example.com/old/", body=html_links("New", []),
                chain=[{"status": 301, "location": "https://example.com/new/"}],
                final_url="https://example.com/new/")
        rep, _rc = crawl(make_ns(), web)
        rows = rep["link_issues"]["redirect_target_no_direct_inlinks"]
        self.assertEqual([r["target"] for r in rows], ["https://example.com/new/"])
        by = {pg["url"]: pg for pg in rep["pages"]}
        self.assertEqual(by["https://example.com/blog/a/"]["status"], 200)

    def test_http_page_links_to_https(self):
        web = FakeWeb()
        web.add("http://example.com/sitemap.xml", body=urlset_xml(["http://example.com/"]))
        web.add("http://example.com/", body=html_links("H", ["https://example.com/a", "/b"]))
        web.add("https://example.com/a", body=html_links("A", ["http://example.com/b"]))
        web.add("http://example.com/b", body=html_links("B", []))
        rep, _rc = crawl(make_ns(site="http://example.com"), web)
        li = rep["link_issues"]
        self.assertEqual([r["page"] for r in li["http_page_links_to_https"]], ["http://example.com/"])
        self.assertEqual([r["page"] for r in li["https_page_links_to_http"]], ["https://example.com/a"])

    def test_https_to_http_redirect(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME, "https://example.com/x"]))
        web.add(HOME, body=html_links("H", []))
        web.add("https://example.com/x", body=html_links("X", []),
                chain=[{"status": 301, "location": "http://example.com/x"}], final_url="http://example.com/x")
        rep, _rc = crawl(make_ns(), web)
        rows = rep["link_issues"]["https_to_http_redirects"]
        self.assertEqual([(r["from"], r["to"]) for r in rows], [("https://example.com/x", "http://example.com/x")])

    def test_external_3xx_sampled(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["https://old-partner.com/guide", "https://ok.org/"]))
        web.add("https://old-partner.com/guide", status=200,
                chain=[{"status": 301, "location": "https://casino.example.net/"}],
                final_url="https://casino.example.net/")
        web.add("https://ok.org/", status=200)
        rep, _rc = crawl(make_ns(check_external=True), web)
        ex = rep["external_redirects"]
        self.assertEqual((ex["checked"], ex["total"]), (2, 2))
        self.assertEqual([r["url"] for r in ex["redirects"]], ["https://old-partner.com/guide"])
        self.assertEqual(ex["redirects"][0]["kind"], "跳到别的站")
        self.assertIn("外链 3xx(抽检 2/2", sc.render_markdown(rep))

    def test_external_404_reported(self):
        # 11-05 独立评分:夹具外链 ext-404 实际 404,脚本不报(Ahrefs「External 4XX」)
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["https://gone.org/page", "https://ok.org/"]))
        web.add("https://gone.org/page", status=404)
        web.add("https://ok.org/", status=200)
        rep, _rc = crawl(make_ns(check_external=True), web)
        ex = rep["external_redirects"]
        self.assertEqual([(r["url"], r["status"]) for r in ex["broken"]], [("https://gone.org/page", 404)])
        self.assertEqual(ex["redirects"], [])
        self.assertIn("外链 4xx(同一批抽检):1 个", sc.render_markdown(rep))

    def test_external_3xx_off_by_default_says_so(self):
        web = FakeWeb()
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME]))
        web.add(HOME, body=html_links("H", ["https://ok.org/"]))
        rep, _rc = crawl(make_ns(), web)
        self.assertNotIn("external_redirects", rep)
        self.assertIn("外链 3xx:未检查", sc.render_markdown(rep))
        self.assertNotIn("https://ok.org/", web.urls())


class SubdomainRobots(unittest.TestCase):
    def _run(self, sub_robots):
        web = FakeWeb()
        web.add(HOME + "robots.txt", body="User-agent: *\nDisallow: /admin\nSitemap: https://example.com/sitemap.xml\n")
        web.add("https://example.com/sitemap.xml", body=urlset_xml([HOME, "https://blog.example.com/post"]))
        web.add(HOME, body=html_links("H", []))
        web.add("https://blog.example.com/post", body=html_links("P", []))
        if sub_robots is not None:
            web.add("https://blog.example.com/robots.txt", status=sub_robots[0], body=sub_robots[1])
        rep, _rc = crawl(make_ns(), web)
        return rep["subdomain_robots"]

    def test_missing_subdomain_robots(self):
        sub = self._run(None)                                  # FakeWeb 默认 404
        self.assertEqual(sub["main_rules"], 1)
        self.assertEqual(sub["hosts"][0]["host"], "blog.example.com")
        self.assertIn("缺失", sub["hosts"][0]["verdict"])

    def test_subdomain_robots_present(self):
        sub = self._run((200, "User-agent: *\nDisallow:\n"))
        self.assertEqual(sub["hosts"][0]["verdict"], "有")

    def test_subdomain_robots_html_shell(self):
        sub = self._run((200, "<!doctype html><html><body>app</body></html>"))
        self.assertIn("返回 HTML", sub["hosts"][0]["verdict"])

    def test_server_error_not_judged(self):
        sub = self._run((503, ""))
        self.assertIn("未判定", sub["hosts"][0]["verdict"])


class RedirectChainHttpsToHttp(unittest.TestCase):
    def test_downgrade_warned(self):
        hops = {"https://e.com/a": (301, "http://e.com/a"), "http://e.com/a": (200, None)}
        orig = redirect_chain.request_once
        redirect_chain.request_once = lambda u, t, ua=None: (hops[u][0], hops[u][1], 1.0)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = redirect_chain.main(["https://e.com/a"])
        finally:
            redirect_chain.request_once = orig
        self.assertEqual(rc, 0)
        self.assertIn("HTTPS→HTTP 降级", buf.getvalue())

    def test_redirect_to_404_is_critical(self):
        # 11-05 独立评分:一跳到 404 的链原来打印「无问题」(Ahrefs「3XX redirect to 4XX」)
        hops = {"https://e.com/old": (301, "https://e.com/gone"), "https://e.com/gone": (404, None)}
        orig = redirect_chain.request_once
        redirect_chain.request_once = lambda u, t, ua=None: (hops[u][0], hops[u][1], 1.0)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = redirect_chain.main(["https://e.com/old"])
        finally:
            redirect_chain.request_once = orig
        self.assertEqual(rc, 1)
        self.assertIn("重定向终点返回 HTTP 404", buf.getvalue())


# ---------------------------------------------------------------- D 目录对齐
class CatalogAlignment(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(REFS, "technical", "audit-rule-catalog.md"), encoding="utf-8") as f:
            self.cat = f.read()
        self.sec7 = self.cat.split("## 七、", 1)[1]

    def test_every_site_audit_rule_listed(self):
        slugs = {slug for _a, _n, slug in sa.RULE_SLUGS}
        missing = sorted(s for s in slugs if "`%s`" % s not in self.sec7)
        self.assertEqual(missing, [], "site_audit 有、目录第七节没登记")

    def test_category_table_areas_exist_in_site_audit(self):
        with open(os.path.join(SCRIPTS, "site_audit.py"), encoding="utf-8") as f:
            src = f.read()
        areas = set(re.findall(r'\("(?:CRITICAL|WARN|INFO)",\s*"([^"]+)"', src)) | {"robots", "sitemap", "llms.txt"}
        table = self.cat.split("## 〇、", 1)[0]
        cited = set(re.findall(r"`([a-z0-9.\-_]+)`", "\n".join(
            ln.rsplit("|", 2)[-2] for ln in table.splitlines() if ln.startswith("| ") and ln.count("|") >= 6)))
        cited = {c for c in cited if not c.endswith(".py")}   # 脚本名(field_data.py 等)不是 area
        self.assertEqual(sorted(cited - areas), [], "目录类别表写了 site_audit 不产出的 area")


if __name__ == "__main__":
    unittest.main()
