#!/usr/bin/env python3
"""sitemap_audit.py --hreflang 全站互指检查回归测试(B29;合成 sitemap,fetch 打桩,零网络)。

期望值来源:Google「Localized versions of your pages」(developers.google.com/search/docs/
specialty/international/localized-versions,2026-09-21 更新,2026-10-21 读取):
- 「Each language version must list itself as well as all other language versions.」→ 缺自引用。
- 「Alternate URLs must be fully-qualified ... not //example.com/foo or /foo」→ 非完整 URL。
- 「If two pages don't both point to each other, the tags will be ignored」;「Google will still
  process the ones that point to each other」→ 按「对」报互指缺失,不整簇作废。
- sitemap 写法:每个 <url> 的 <xhtml:link rel="alternate" hreflang=…> 列出全部版本含自身。
- 「Consider adding a fallback page for unmatched languages ... x-default」→ 缺 x-default 只是提示。
- 语言码只认 ISO 639-1 + 可选 ISO 3166-1 Alpha-2(es-419 不支持)——校验复用
  hreflang_cluster.check_lang(任务要求不另写一套)。
"""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import hreflang_cluster  # noqa: E402
import sitemap_audit as sa  # noqa: E402
sa._sleep = lambda _s: None   # 逐条检查的礼貌间隔在测试里不真等

S = "https://example.com"


def url_entry(loc, alts):
    links = "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (h, u) for h, u in alts)
    return "<url><loc>%s</loc>%s</url>" % (loc, links)


def sitemap(entries):
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(entries) + "</urlset>").encode()


BAD = sitemap([
    url_entry(S + "/en/a", [("en", S + "/en/a"), ("es", S + "/es/a"), ("zh-Hans", S + "/zh/a"),
                            ("x-default", S + "/en/a")]),
    url_entry(S + "/es/a", [("en", S + "/en/a"), ("es", S + "/es/a"), ("zh-Hans", S + "/zh/a"),
                            ("x-default", S + "/en/a")]),
    url_entry(S + "/zh/a", [("en", S + "/en/a"), ("zh-Hans", S + "/zh/a"), ("x-default", S + "/en/a")]),
    url_entry(S + "/en/b", [("en", S + "/en/b"), ("es-419", S + "/es/b")]),
    url_entry(S + "/en/c", [("es", S + "/es/c")]),
    url_entry(S + "/es/c", [("es", S + "/es/c"), ("en", S + "/en/c"), ("x-default", S + "/es/c")]),
    url_entry(S + "/en/d", [("en", "/en/d"), ("x-default", S + "/en/d")]),
])

GOOD = sitemap([
    url_entry(S + "/en/a", [("en", S + "/en/a"), ("zh-CN", S + "/zh/a"), ("x-default", S + "/en/a")]),
    url_entry(S + "/zh/a", [("en", S + "/en/a"), ("zh-CN", S + "/zh/a"), ("x-default", S + "/en/a")]),
])


def run(xml):
    def fake_fetch(url, timeout=10.0, max_bytes=5_000_000):
        if url.endswith("/sitemap.xml"):
            return 200, None, xml
        if url.endswith("/robots.txt"):
            return 404, None, b""
        return 200, None, b"<html><head><title>t</title></head><body>x</body></html>"
    sa._ROBOTS_CACHE.clear()
    out = io.StringIO()
    with mock.patch.object(sa, "fetch", fake_fetch), contextlib.redirect_stdout(out):
        rc = sa.main([S, "--hreflang", "--check-limit", "0"])
    return rc, out.getvalue()


def section(out, label):
    """取「[label] 命中 N」后到下一个空行的块。"""
    i = out.find("[" + label)
    if i < 0:
        return ""
    j = out.find("\n\n", i)
    return out[i: j if j > 0 else len(out)]


class SitemapHreflangTests(unittest.TestCase):
    def test_reuses_hreflang_cluster_check_lang(self):
        self.assertIs(sa.check_lang, hreflang_cluster.check_lang)

    def test_bad_sitemap_findings(self):
        rc, out = run(BAD)
        self.assertEqual(rc, 1)
        recip = section(out, "hreflang 互指缺失")
        self.assertIn(S + "/es/a", recip)                    # es/a → zh/a,zh/a 没回指 es/a
        self.assertIn(S + "/zh/a", recip)
        self.assertNotIn(S + "/en/a", recip)                 # en↔zh、en↔es 都互指
        self.assertIn("es-419", section(out, "hreflang 语言码非法"))
        self.assertIn(S + "/en/c", section(out, "hreflang 缺自引用"))
        self.assertIn(S + "/es/b", section(out, "hreflang 目标不在 sitemap"))
        self.assertIn(S + "/en/b", section(out, "hreflang 缺 x-default"))
        self.assertIn("/en/d", section(out, "hreflang 非完整 URL"))

    def test_good_sitemap_clean(self):
        rc, out = run(GOOD)
        self.assertEqual(rc, 0, out)
        self.assertIn("hreflang", out)
        for label in ("hreflang 互指缺失", "hreflang 语言码非法", "hreflang 缺自引用",
                      "hreflang 非完整 URL"):
            self.assertIn("[%s] 命中 0" % label, out)

    def test_without_flag_no_hreflang_section(self):
        def fake_fetch(url, timeout=10.0, max_bytes=5_000_000):
            if url.endswith("/sitemap.xml"):
                return 200, None, BAD
            return 404 if url.endswith("robots.txt") else 200, None, b"<html></html>"
        sa._ROBOTS_CACHE.clear()
        out = io.StringIO()
        with mock.patch.object(sa, "fetch", fake_fetch), contextlib.redirect_stdout(out):
            sa.main([S, "--check-limit", "0"])
        self.assertNotIn("hreflang 互指缺失", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
