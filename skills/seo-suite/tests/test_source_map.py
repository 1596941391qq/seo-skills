#!/usr/bin/env python3
"""source_map:线上 URL → 该改的源文件。

期望值来自 RQ-229 例 4 的盲标(labels_example4.json:没看过 source_map 的子代理读 everyinfra 源码逐条追到
title 所在文件,2026-11-05)。这里把那几类页面缩成最小样本:每条注释写对应的是哪条真实标注、真实踩过的坑。
"""
import os
import shutil
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
import source_map as S  # noqa: E402


def site(files):
    d = tempfile.mkdtemp(prefix="sm_test_")
    for path, text in files.items():
        p = os.path.join(d, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    return d


class SourceMapTests(unittest.TestCase):
    def tearDown(self):
        for d in getattr(self, "_dirs", []):
            shutil.rmtree(d, ignore_errors=True)

    def repo(self, files):
        d = site(files)
        self._dirs = getattr(self, "_dirs", []) + [d]
        return S.Repo(d)

    def map1(self, repo, url, anchors):
        return S.map_urls(repo, [url], 0.7, lambda u: anchors)[0]

    def test_content_dir_named_build_is_not_skipped(self):
        # 标注 #10 /en/build/amazon-review-pipeline → web/content/en/build/articles.ts。
        # 旧代码按子串跳过「build/」,把 content/en/build/ 整个漏掉。
        r = self.repo({
            "web/app/en/build/[slug]/page.tsx": "import { A } from '@/content/en/build/articles';\n",
            "web/content/en/build/articles.ts": 'export const A = [{"slug": "amazon-review-pipeline", '
                                                '"title": "Amazon Review API: From Product Links to Issue Lists"}];\n',
            "web/tsconfig.json": "{}",
        })
        self.assertIn("web/content/en/build/articles.ts", r.files())
        res = self.map1(r, "https://x.com/en/build/amazon-review-pipeline",
                        {"title": "Amazon Review API: From Product Links to Issue Lists · Acme",
                         "h1": "Amazon Review API: From Product Links to Issue Lists"})
        self.assertEqual(res["best"], "web/content/en/build/articles.ts")
        self.assertTrue(res["actionable"])

    def test_site_suffix_template_does_not_win(self):
        # 标注 #2 /es/partners/power-bi → es.md。全站共用的 `${title} · 站名` 模板会套上任何页面,不能抢第一。
        r = self.repo({
            "web/app/es/partners/[slug]/page.tsx": "import { t } from '../../../../content/blog/locale';\n",
            "web/content/blog/locale.ts": "export const t = (x: string) => `${x} · Acme Engine`;\n",
            "web/content/partners/power-bi/es.md": "---\ntitle: Power BI y Acme: datos de redes sociales\n"
                                                   "description: Conecta Power BI con datos limpios de redes sociales.\n---\n",
        })
        res = self.map1(r, "https://x.com/es/partners/power-bi",
                        {"title": "Power BI y Acme: datos de redes sociales · Acme Engine",
                         "description": "Conecta Power BI con datos limpios de redes sociales."})
        self.assertEqual(res["best"], "web/content/partners/power-bi/es.md")

    def test_templated_chinese_title(self):
        # 标注 #3 /xiaohongshu-api → web/content/zh-CN/platform-seo.ts:标题由模板拼出,原文在仓库里搜不到。
        r = self.repo({
            "web/app/(zh)/[slug]/page.tsx": "import { zhTitle } from '@/content/zh-CN/platform-seo';\n",
            "web/content/zh-CN/platform-seo.ts": 'const ITEMS = { xiaohongshu: ["笔记", "评论", "用户"] };\n'
                                                 "export const zhTitle = (name: string, xs: string[]) => "
                                                 "`${name}爬虫 API:${xs.join('、')}数据采集`;\n",
        })
        res = self.map1(r, "https://x.com/xiaohongshu-api",
                        {"title": "小红书爬虫 API:笔记、评论、用户数据采集 · Acme 引擎"})
        self.assertEqual(res["best"], "web/content/zh-CN/platform-seo.ts")

    def test_locale_page_prefers_same_locale_file(self):
        # 标注 #6 /es/blog/... → web/content/es/blog/articles.ts,不是英文版或中文生成物。
        r = self.repo({
            "web/app/es/blog/[slug]/page.tsx": "import { ES } from '@/content/es/blog/articles';\n",
            "web/content/es/blog/articles.ts": 'export const ES = [{"slug": "place-id", '
                                              '"title": "Deduplicación de ubicaciones en Google Maps"}];\n',
            "web/content/en/blog/articles.ts": 'export const EN = [{"slug": "place-id", '
                                              '"note": "Deduplicación de ubicaciones en Google Maps (es)"}];\n',
        })
        res = self.map1(r, "https://x.com/es/blog/place-id",
                        {"title": "Deduplicación de ubicaciones en Google Maps · Acme"})
        self.assertEqual(res["best"], "web/content/es/blog/articles.ts")

    def test_entity_only_match_is_not_actionable(self):
        # 标注 #5 /en/similarweb-api/competitors:标题「SimilarWeb Competitors API」只由 URL 实体词拼成,
        # 另一个文件里恰好出现同名短语。这种证据不够动手,只能列候选。
        r = self.repo({
            "web/app/en/[slug]/[action]/page.tsx": "export default function P() {}\n",
            "web/content/en/capability-guides.ts": 'export const G = "SimilarWeb Competitors guide";\n',
        })
        res = self.map1(r, "https://x.com/en/similarweb-api/competitors",
                        {"title": "SimilarWeb Competitors API · Acme", "h1": "SimilarWeb Competitors API"})
        self.assertFalse(res["actionable"])

    def test_page_anchors_take_main_paragraph_not_consent_banner(self):
        # everyinfra 每页正文前都有一段 Cookie 说明,首段锚点不能取它。
        html = ("<html><head><title>T · Acme</title><meta name='description' content='D'></head><body>"
                "<div class='consent'><p>Our own visit statistics are always on. Analytics is enabled only with "
                "your permission.</p></div><main><h1>Heading</h1><p>List the sites a domain relates to, "
                "with category and rank for each one.</p></main></body></html>")
        a = S.page_anchors(html)
        self.assertEqual(a["title"], "T · Acme")
        self.assertTrue(a["p"].startswith("List the sites"))

    def test_static_route_and_text_agree(self):
        r = self.repo({"about/index.html": "<title>About Acme Static: who we are</title>",
                       "index.html": "<title>Acme Static home page title</title>"})
        res = self.map1(r, "http://127.0.0.1/about/", {"title": "About Acme Static: who we are"})
        self.assertEqual(res["best"], "about/index.html")
        self.assertGreaterEqual(res["confidence"], 0.9)


if __name__ == "__main__":
    unittest.main()
