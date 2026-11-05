#!/usr/bin/env python3
"""2026-11-05 三站实战(everyinfra.com、plausible.io、sspai.com)查出的问题回归。

输入是站点当天的真实 robots.txt,存在 tests/fixtures/field-20261105/。修前红、修后绿;零网络。
- site_crawl / robots_posture 不认 RFC 9309 的 `*`、`$`,还忽略大小写:sspai 的 `Disallow: /tag/*` 被当成放行,爬虫抓了对方禁止的路径。
- site_crawl 的 normalize_url 不转码中文路径,http_fetch 抛 UnicodeEncodeError,整次爬取作废。
- robots_posture 把「没有任何规则组」的 robots.txt 判成引用 bot 不可见(RFC 9309:没有匹配组 = 全放行)。
- hreflang_cluster 对没有 hreflang 的单语页报「缺自引用」。
- sitemap_audit 在 `python3 -I` 下 import 不到同目录的 hreflang_cluster。
"""
import os
import subprocess
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
FIX = os.path.join(BASE, "tests", "fixtures", "field-20261105")
sys.path.insert(0, SCRIPTS)

import hreflang_cluster  # noqa: E402
import robots_posture  # noqa: E402
import site_crawl  # noqa: E402


def text(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class SiteCrawlRobots(unittest.TestCase):
    def setUp(self):
        self.doc = site_crawl.parse_robots(text("sspai-robots.txt"))

    def test_wildcard_disallow_blocks(self):
        for path in ("/tag/设计", "/tag/x", "/a/123", "/search/post?q=1", "/link"):
            self.assertFalse(site_crawl.robots_allows(self.doc, "https://sspai.com" + path), path)

    def test_unblocked_paths_allowed(self):
        for path in ("/", "/post/12345", "/series"):
            self.assertTrue(site_crawl.robots_allows(self.doc, "https://sspai.com" + path), path)

    def test_paths_are_case_sensitive(self):
        self.assertTrue(site_crawl.robots_allows(self.doc, "https://sspai.com/TAG/x"))

    def test_dollar_anchor(self):
        doc = site_crawl.parse_robots("User-agent: *\nDisallow: /*.pdf$\n")
        self.assertFalse(site_crawl.robots_allows(doc, "https://e.com/x/a.pdf"))
        self.assertTrue(site_crawl.robots_allows(doc, "https://e.com/x/a.pdf?dl=1"))


class SiteCrawlUnicodePath(unittest.TestCase):
    def test_normalize_url_percent_encodes(self):
        u = site_crawl.normalize_url("/tag/设计", base="https://sspai.com/")
        self.assertEqual(u, "https://sspai.com/tag/%E8%AE%BE%E8%AE%A1")
        u.encode("ascii")

    def test_existing_escapes_kept(self):
        u = site_crawl.normalize_url("https://e.com/a%20b/c?q=%E4%B8%AD")
        self.assertEqual(u, "https://e.com/a%20b/c?q=%E4%B8%AD")


class RobotsPosture(unittest.TestCase):
    def test_wildcard_rule(self):
        g = {"allow": [], "disallow": ["/a/*"]}
        self.assertEqual(robots_posture.effective_rule(g, "/a/1")[0], "disallow")
        self.assertEqual(robots_posture.effective_rule(g, "/b/1")[0], "allow")

    def test_no_groups_means_visible(self):
        doc = robots_posture.parse_robots(text("plausible-robots.txt"))
        c = robots_posture.citation_report(doc)
        self.assertTrue(c["ok"])
        self.assertEqual(c["allowed_count"], 5)
        self.assertFalse(c["explicit"])  # 没有专属规则,拿不到满分
        rep = robots_posture.analyze(text("plausible-robots.txt"))
        self.assertEqual(rep["visibility_failures"], [])


class HreflangSingleLanguage(unittest.TestCase):
    def test_no_entries_is_not_applicable(self):
        self.assertIsNone(hreflang_cluster.self_ref_state({}, "https://plausible.io/"))

    def test_missing_self_still_fails(self):
        d = {("en", "https://e.com/en"): {}}
        self.assertFalse(hreflang_cluster.self_ref_state(d, "https://e.com/de"))
        self.assertTrue(hreflang_cluster.self_ref_state(d, "https://e.com/en"))


class IsolatedImport(unittest.TestCase):
    def test_sitemap_audit_runs_under_python_I(self):
        r = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "sitemap_audit.py"), "--help"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr[-400:])


if __name__ == "__main__":
    unittest.main(verbosity=1)
