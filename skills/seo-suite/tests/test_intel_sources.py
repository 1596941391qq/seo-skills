"""intel_check.py 2026-11-05 扩源:关键词过滤 + 12 条漏报知识回放。

期望值来源:
- RSS 片段是 2026-11-05 只读拉取的真实 feed 条目(openai.com/news/rss.xml、
  blog.cloudflare.com/rss/),只截了标题、链接、日期。
- 回放标题是各事件一手原文页面的真实标题(打开原文页取 <title>,核对 2026-11-05)。
"""
import os
import re
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

import intel_check as ic  # noqa: E402

OPENAI_RSS = """<rss version="2.0"><channel>
<item><title><![CDATA[Setting a new standard for responsible AI infrastructure]]></title>
<link>https://openai.com/index/responsible-ai-infrastructure</link><pubDate>Thu, 05 Nov 2026 02:00:00 GMT</pubDate></item>
<item><title><![CDATA[OpenAI to acquire Pierre Computer Company, Inc.]]></title>
<link>https://openai.com/index/openai-to-acquire-pierre</link><pubDate>Wed, 04 Nov 2026 14:30:00 GMT</pubDate></item>
<item><title><![CDATA[Making it easier for websites to express AI training preferences]]></title>
<link>https://openai.com/index/helping-websites-express-ai-training-preferences</link><pubDate>Fri, 30 Oct 2026 00:00:00 GMT</pubDate></item>
</channel></rss>"""

CLOUDFLARE_RSS = """<rss version="2.0"><channel>
<item><title><![CDATA[See the agents, set the terms: new visibility and control for personal agents]]></title>
<link>https://blog.cloudflare.com/personal-agents-visibility-control/</link><pubDate>Wed, 04 Nov 2026 14:00:00 GMT</pubDate></item>
<item><title><![CDATA[Introducing Zero Wire, a hub for investigating critical Internet vulnerabilities]]></title>
<link>https://blog.cloudflare.com/zero-wire/</link><pubDate>Tue, 03 Nov 2026 14:00:00 GMT</pubDate></item>
<item><title><![CDATA[How we halved DNS build delay and cut memory use by 85%]]></title>
<link>https://blog.cloudflare.com/dns-build-delay/</link><pubDate>Mon, 02 Nov 2026 14:00:00 GMT</pubDate></item>
</channel></rss>"""


def matches(source, title, link=""):
    kw = ic.SOURCES[source].get("keywords")
    return True if not kw else bool(re.search(kw, f"{title} {link}", re.I))


class KeywordFilterTests(unittest.TestCase):
    def setUp(self):
        self._orig_fetch = ic.fetch
        self._orig_cache = ic._body_cache
        ic._body_cache = {}

    def tearDown(self):
        ic.fetch = self._orig_fetch
        ic._body_cache = self._orig_cache

    def test_openai_keeps_only_relevant(self):
        raw, items = ic.source_items(ic.SOURCES["openai-news"], OPENAI_RSS)
        self.assertEqual(len(raw), 3)
        self.assertEqual([t for t, _, _ in items],
                         ["Making it easier for websites to express AI training preferences"])

    def test_cloudflare_keeps_only_relevant(self):
        _, items = ic.source_items(ic.SOURCES["cloudflare-blog"], CLOUDFLARE_RSS)
        self.assertEqual([t for t, _, _ in items],
                         ["See the agents, set the terms: new visibility and control for personal agents"])

    def test_irrelevant_new_items_are_not_a_change(self):
        """基线之后只来了无关新文章 → 不报变更,也不动基线。"""
        ic.fetch = lambda url, timeout=20, cache=True: CLOUDFLARE_RSS.replace(
            "See the agents, set the terms: new visibility and control for personal agents",
            "Introducing tsrs: A port of TypeScript to Rust").replace(
            "personal-agents-visibility-control", "typescript-rust-port")
        prev = {"top": "Some older AI crawler post", "seen": ["Some older AI crawler post"]}
        ch, detail, ns = ic.check_source("cloudflare-blog", ic.SOURCES["cloudflare-blog"], prev)
        self.assertEqual((ch, detail, ns), (False, "", None))

    def test_relevant_new_item_is_a_change(self):
        ic.fetch = lambda url, timeout=20, cache=True: OPENAI_RSS
        prev = {"top": "Older relevant post", "seen": ["Older relevant post"]}
        ch, detail, ns = ic.check_source("openai-news", ic.SOURCES["openai-news"], prev)
        self.assertTrue(ch)
        self.assertIn("Making it easier for websites", detail)
        self.assertEqual(ns["top"], "Making it easier for websites to express AI training preferences")

    def test_unfiltered_source_unchanged_behaviour(self):
        """没有 keywords 的源仍只看最近 5 条,行为不变。"""
        rss = "<rss><channel>" + "".join(
            f"<item><title>P{i}</title><link>l{i}</link></item>" for i in range(8)) + "</channel></rss>"
        raw, items = ic.source_items(ic.SOURCES["chrome-blog"], rss)
        self.assertEqual(raw, items)
        self.assertEqual(len(items), 5)

    def test_atom_link_href(self):
        """arXiv / GitHub Atom 的 link 在 href 属性里。"""
        atom = ('<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>T</title>'
                '<link href="http://arxiv.org/abs/2610.15033v1" rel="alternate"/>'
                '<updated>2026-10-10T00:00:00Z</updated></entry></feed>')
        self.assertEqual(ic.get_rss_items(atom)[0][1], "http://arxiv.org/abs/2610.15033v1")


class ReplayTests(unittest.TestCase):
    """12 条漏报知识里,由新源负责的那几条,其一手原文标题必须过各自的关键词过滤。"""

    CASES = [
        ("web-dev-blog", "Experimental soft navigation metrics now available in CrUX"),          # 1
        ("cloudflare-blog", "Your site, your rules: new AI traffic options for all customers"),  # 2
        ("cloudflare-blog", "Have it both ways: stay discoverable in search while disallowing AI training"),  # 2
        ("msads-blog", "Building Toward a Sustainable Content Economy for the Agentic Web"),     # 5 PCM
        ("openai-news", "Making it easier for websites to express AI training preferences"),     # 6
        ("msads-blog", "Conversations that Convert: Copilot Checkout and Brand Agents"),         # 8
        ("bing-search-blog", "Announcing Microsoft Web IQ"),                                     # 8
        ("google-shopping-blog", "AI shopping gets simpler with Universal Commerce Protocol updates"),  # 8
        ("google-maps-blog", "How we’re reimagining Maps with Gemini"),                          # 9
        ("google-maps-blog", "Ask Maps gets more helpful with food ordering and more"),          # 9
        ("chrome-blog", "15 updates from Google I/O 2026: Powering the agentic web with new capabilities, tools, and features in Chrome"),  # 12
        ("bing-search-blog", "Your content, your choice: clearer preferences for training and grounding"),  # 回放时新发现
    ]

    def test_replay_titles_pass_filters(self):
        for src, title in self.CASES:
            with self.subTest(src=src, title=title):
                self.assertTrue(matches(src, title), f"{src} 漏掉: {title}")

    def test_arxiv_query_is_geo_phrase(self):
        self.assertIn("generative%20engine%20optimization", ic.SOURCES["arxiv-geo"]["url"])

    def test_modules_exist(self):
        refs = os.path.join(BASE, "references")
        for name, cfg in ic.SOURCES.items():
            for m in cfg["modules"]:
                with self.subTest(source=name, module=m):
                    self.assertTrue(os.path.isfile(os.path.join(refs, m)), m)


if __name__ == "__main__":
    unittest.main()
