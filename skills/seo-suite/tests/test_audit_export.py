#!/usr/bin/env python3
"""site_audit.py S4 扩展测试:具名 bulk export + 受影响面(borrow-specs A2,SF/Sitebulb 口径)。
覆盖:slug 表命中与 fallback 稳定/同 slug 冲突合并取最高 severity/导出文件一行一 URL/
summary.json 占比计算/markdown 受影响面列(多 URL N/M 页与单 URL 1/1)/--json exports 节
与向后兼容(不加 --export-dir 时无 exports 键)/SKIP 拒审不算规则但计入分母/退出码不动。
standalone(自带 run_script/stub_fetch 助手,合成 HTML fixture + fetch 打桩,零网络):
python3 tests/test_audit_export.py
亦被 tests/run_tests.py 按 test_*.py 独立测试文件自动发现加载。"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import site_audit as sa  # noqa: E402  (需先入 SCRIPTS 路径)


def run_script(name, args=(), stdin=None):
    """独立助手(与 run_tests.py 同形):子进程跑 scripts/ 下脚本,捕获输出。"""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, name), *args],
                          input=stdin, capture_output=True, text=True,
                          encoding="utf-8", env=env)


def stub_fetch(pages, root="https://example.com"):
    """零网络 fetch 替身:pages={路径: (status, headers, body)};未登记 URL 抛 404。"""
    table = {root + path: v for path, v in pages.items()}

    def _fetch(url, timeout=15):
        if url in table:
            st, hdrs, body = table[url]
            return st, hdrs, body
        import urllib.error
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    return _fetch


ROOT_FILES = {  # 根文件全放行,压缩无关 INFO 噪音
    "/robots.txt": (200, {}, "User-agent: *\nAllow: /\n"),
    "/sitemap.xml": (200, {}, "<urlset/>"),
    "/llms.txt": (200, {}, "# llms\n"),
}


def page_html(canonical=True, desc=True, h1=True):
    """合成页:默认仅触发 INFO links-too-many(101 个链接)与 semantic-html-low(链接压低比值);canonical=False 加 WARN
    canonical 缺失;desc=False 加 WARN description 缺失;h1=False 加 WARN 无 H1。
    S2a 2026-10-21 改:旧版默认 INFO 是 rendering-no-noscript——页面有 main/article 且正文>500 字
    (服务端内容)时 site_audit 不再报「无 JS 空页」(B3);description/H1 缺失按 Google 文档降 WARN
    (B15/B38);默认 INFO 规则改由 >100 链接(B14 已降 INFO)提供。"""
    head = ['<title>Example Article Page Title Long Enough</title>',
            '<meta name="viewport" content="width=device-width, initial-scale=1">']
    if desc:
        head.append('<meta name="description" content="A sufficiently long description '
                    'text that exceeds eighty characters easily for tests.">')
    head.append('<meta property="og:title" content="t"><meta property="og:description" content="d">'
                '<meta property="og:image" content="https://example.com/i.png">')
    if canonical:
        head.append('<link rel="canonical" href="https://example.com/self">')
    head.append('<script type="application/ld+json">{"@context":"https://schema.org"}</script>')
    return ('<!doctype html><html lang="en"><head>' + "".join(head) + '</head><body>'
            '<header><nav>nav links here</nav></header><main><article>'
            + ("<h1>Main Heading of the Page</h1>" if h1 else "")
            + '<p>In short, here is the direct answer with facts. ' + "filler content word " * 120
            + '</p>' + "".join('<a href="/l%d">l</a>' % i for i in range(101))
            + '<h2>Section One</h2><ul><li>alpha</li><li>beta</li><li>gamma</li><li>delta</li></ul>'
              '<h2>Section Two</h2><p>more body content for the test page</p>'
              '</article></main><footer>footer text</footer></body></html>')


def run_main(argv, pages, root="https://example.com"):
    """打桩 fetch 真跑 main();返回 (完整 stdout, 退出码)。"""
    orig_fetch, orig_argv = sa.fetch, sys.argv
    sa.fetch = stub_fetch(pages, root)
    sys.argv = ["site_audit.py", *argv]
    buf, ebuf = io.StringIO(), io.StringIO()
    rc = 0
    try:
        with redirect_stdout(buf), redirect_stderr(ebuf):
            try:
                sa.main()
            except SystemExit as e:
                rc = e.code or 0
    finally:
        sa.fetch, sys.argv = orig_fetch, orig_argv
    LAST_STDERR[0] = ebuf.getvalue()
    return buf.getvalue(), rc


LAST_STDERR = [""]   # S2a B4:--json 时人读行(含 markdown 汇总)改走 stderr


def json_blob_of(stdout):
    """S2a B4 改:--json 时 stdout 只有一个 JSON 对象(--help 契约「供 agent 消费」),整体解析。
    旧版从末位 '\n{' 截取,是在迁就 stdout 混排 markdown 的旧缺陷。"""
    return json.loads(stdout)


# ---------------------------------------------------------------- 纯函数层
class RuleSlugTests(unittest.TestCase):
    """rule_slug:RULE_SLUGS 表命中(任务示例钉死)/fallback(首 ASCII 词素与纯 CJK)/稳定性。"""

    def test_spec_examples_canonical_missing_and_title_too_long(self):
        self.assertEqual(sa.rule_slug("canonical", "缺失"), "canonical-missing")
        self.assertEqual(sa.rule_slug("title", "70 chars 超上限 60(市场注记)"), "title-too-long")
        self.assertEqual(sa.rule_slug("title", "15 chars <20"), "title-too-short")
        self.assertEqual(sa.rule_slug("llms.txt", "/llms.txt 不可达"), "llms-txt-unreachable")

    def test_table_ordering_specific_before_generic(self):
        # ai-bots:训练型(INFO)与被禁(CRITICAL/WARN)分文件;og:image 非绝对先于缺失
        self.assertEqual(sa.rule_slug("ai-bots", "GPTBot 被禁(训练型,不影响搜索可见性,仅提示)"),
                         "ai-bots-training-blocked")
        self.assertEqual(sa.rule_slug("ai-bots", "PerplexityBot 被禁——逐出该 AI 答案"),
                         "ai-bots-blocked")
        self.assertEqual(sa.rule_slug("og", "og:image 非绝对 URL"), "og-image-not-absolute")
        self.assertEqual(sa.rule_slug("og", "og:image 缺失"), "og-image-missing")

    def test_fallback_first_ascii_word_and_cjk_area_only(self):
        self.assertEqual(sa.rule_slug("fetch", "HTTP Error 404: Not Found"), "fetch-http")
        self.assertEqual(sa.rule_slug("zz-future", "完全中文的新规则消息"), "zz-future")
        # 非 ASCII 安全字符折叠为 '-'
        self.assertEqual(sa.rule_slug("zz", "Some/Thing: weird"), "zz-some-thing")

    def test_slug_deterministic_across_calls(self):
        for _ in range(3):
            self.assertEqual(sa.rule_slug("canonical", "缺失"), "canonical-missing")
        r1 = sa.aggregate_rules({"https://a/": [("WARN", "fetch", "HTTP Error 500: x")]})
        r2 = sa.aggregate_rules({"https://a/": [("WARN", "fetch", "HTTP Error 500: x")]})
        self.assertEqual(sorted(r1), sorted(r2))


class AggregateRulesTests(unittest.TestCase):
    """聚合:同 slug 冲突合并/最高 severity/URL 顺序去重/SKIP 拒审不算规则。"""

    def test_same_slug_merges_keeps_highest_severity_and_url_order(self):
        by_url = {
            "https://a/": [("WARN", "fetch", "HTTP Error 500: boom"), ("WARN", "x", "boom one")],
            "https://b/": [("INFO", "fetch", "HTTP Error 404: nope"), ("INFO", "x", "boom two")],
        }
        rules = sa.aggregate_rules(by_url)
        self.assertEqual(rules["fetch-http"]["severity"], "WARN")    # 同 slug 两来源同级别,不升级不降级
        self.assertEqual(rules["fetch-http"]["urls"], ["https://a/", "https://b/"])   # 审计顺序
        self.assertEqual(rules["x-boom"]["severity"], "WARN")        # fallback 撞同一 slug 也合并
        self.assertEqual(rules["x-boom"]["urls"], ["https://a/", "https://b/"])

    def test_severity_promotion_and_same_url_dedup(self):
        # 同一页两条 ai-bots 命中(不同 bot 被禁)→ 同 slug 同 URL 去重,受影响数仍 1;
        # 他页 WARN 命中不降级既有 CRITICAL
        by_url = {"https://a/": [("CRITICAL", "ai-bots", "PerplexityBot 被禁——逐出该 AI 答案"),
                                 ("CRITICAL", "ai-bots", "Claude-User 被禁——逐出该 AI 答案")],
                  "https://b/": [("WARN", "ai-bots", "Google-Extended 被禁——robots token")]}
        rules = sa.aggregate_rules(by_url)
        r = rules["ai-bots-blocked"]
        self.assertEqual(r["urls"], ["https://a/", "https://b/"])
        self.assertEqual(r["severity"], "CRITICAL")
        # 同页两条 fallback 撞同一 slug("boom" 首词)→ URL 不重复
        same = sa.aggregate_rules({"https://a/": [("WARN", "a", "boom 1"), ("INFO", "a", "boom 2")]})
        self.assertEqual(same["a-boom"]["urls"], ["https://a/"])

    def test_skip_refusal_not_a_rule(self):
        rules = sa.aggregate_rules({
            "https://a/": [("SKIP", "fetch guard", "response too small; refusing to audit"),
                           ("WARN", "canonical", "缺失")]})
        self.assertEqual(list(rules), ["canonical-missing"])
        self.assertEqual(rules["canonical-missing"]["urls"], ["https://a/"])


class CoverageFormatTests(unittest.TestCase):
    """fmt_pct/coverage_str:一位小数,整数不带小数点;SF Coverage 口径文本。"""

    def test_fmt_pct_boundaries(self):
        self.assertEqual(sa.fmt_pct(3, 5), "60%")
        self.assertEqual(sa.fmt_pct(2, 3), "66.7%")
        self.assertEqual(sa.fmt_pct(1, 3), "33.3%")
        self.assertEqual(sa.fmt_pct(1, 1), "100%")
        self.assertEqual(sa.fmt_pct(0, 5), "0%")
        self.assertEqual(sa.fmt_pct(1, 0), "0%")      # 分母为 0 防御

    def test_coverage_str_shape(self):
        self.assertEqual(sa.coverage_str(2, 3), "2/3 页(66.7%)")
        self.assertEqual(sa.coverage_str(1, 1), "1/1 页(100%)")


# ---------------------------------------------------------------- 集成层(真实 main())
class ExportDirIntegrationTests(unittest.TestCase):
    """--export-dir 端到端(fetch 打桩):具名文件一行一 URL/summary.json/markdown 列/
    单 URL 模式/--json exports 节/SKIP 分母语义/退出码与向后兼容。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="audit_export_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_named_files_one_url_per_line_and_dir_autocreate(self):
        export_dir = os.path.join(self.tmp, "exports", "nested")     # 不存在 → 自动创建
        pages = dict(ROOT_FILES)
        pages.update({"/a": (200, {}, page_html(canonical=False)),
                      "/b": (200, {}, page_html(canonical=False)),
                      "/c": (200, {}, page_html(canonical=True))})
        out, rc = run_main(["https://example.com/a", "https://example.com/b", "https://example.com/c",
                            "--export-dir", export_dir], pages)
        self.assertEqual(rc, 0)                                     # 仅 WARN/INFO,退出码不动
        path = os.path.join(export_dir, "canonical-missing.txt")
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines, ["https://example.com/a", "https://example.com/b"])   # 一行一 URL,顺序=审计序
        self.assertNotIn("https://example.com/c", lines)            # 未命中页不进清单
        with open(path, encoding="utf-8") as f:
            self.assertTrue(f.read().endswith("\n"))                # 行结尾换行
        # INFO 级规则同样导出:>100 链接(工具约定)3/3 页全命中
        with open(os.path.join(export_dir, "links-too-many.txt"), encoding="utf-8") as f:
            self.assertEqual(len(f.read().splitlines()), 3)
        # stdout:markdown 受影响面列(分母注明)+ 导出摘要行
        self.assertIn("| canonical-missing | WARN | 2/3 页(66.7%) |", out)
        self.assertIn("分母=本次已审计 3 页", out)
        # S2a:默认 INFO 改由 101 个链接提供,链接标签同时把语义 HTML 比值压到 <10% → 3 个规则
        self.assertIn("bulk export: 3 个规则清单 + summary.json", out)

    def test_summary_json_coverage_math_and_rule_fields(self):
        export_dir = os.path.join(self.tmp, "exp")
        pages = dict(ROOT_FILES)
        pages.update({"/p1": (200, {}, page_html(desc=False)),       # 3 页缺 description(WARN,S2a B15)
                      "/p2": (200, {}, page_html(desc=False)),
                      "/p3": (200, {}, page_html(desc=False)),
                      "/ok1": (200, {}, page_html()),
                      "/ok2": (200, {}, page_html())})
        out, rc = run_main(["https://example.com/p1", "https://example.com/p2", "https://example.com/p3",
                            "https://example.com/ok1", "https://example.com/ok2",
                            "--export-dir", export_dir], pages)
        self.assertEqual(rc, 0)                                     # S2a B15:描述缺失降 WARN,无 CRITICAL
        self.assertIn("| description-missing | WARN | 3/5 页(60%) |", out)
        with open(os.path.join(export_dir, "summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["audited"], 5)
        self.assertIn("已审计页数", summary["denominator_note"])     # 分母口径注明
        rules = {r["slug"]: r for r in summary["rules"]}
        d = rules["description-missing"]
        self.assertEqual(d["affected"], 3)
        self.assertAlmostEqual(d["coverage"], 0.6)
        self.assertEqual(d["coverage_pct"], "60%")
        self.assertEqual(d["severity"], "WARN")
        self.assertEqual(d["file"], "description-missing.txt")
        # 排序:severity 降序在前
        self.assertEqual(summary["rules"][0]["slug"], "description-missing")

    def test_single_url_mode_coverage_one_of_one(self):
        export_dir = os.path.join(self.tmp, "single")
        pages = dict(ROOT_FILES)
        pages["/only"] = (200, {}, page_html(canonical=False))
        out, rc = run_main(["https://example.com/only", "--export-dir", export_dir], pages)
        self.assertEqual(rc, 0)
        self.assertIn("| canonical-missing | WARN | 1/1 页(100%) |", out)   # 单 URL 命中即 1/1
        with open(os.path.join(export_dir, "canonical-missing.txt"), encoding="utf-8") as f:
            self.assertEqual(f.read().splitlines(), ["https://example.com/only"])
        with open(os.path.join(export_dir, "summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["audited"], 1)
        d = {r["slug"]: r for r in summary["rules"]}["canonical-missing"]
        self.assertEqual((d["affected"], d["coverage"], d["coverage_pct"]), (1, 1.0, "100%"))

    def test_json_exports_node_and_backward_compatibility(self):
        export_dir = os.path.join(self.tmp, "json_exp")
        pages = dict(ROOT_FILES)
        pages.update({"/a": (200, {}, page_html(canonical=False)),
                      "/b": (200, {}, page_html())})
        out, rc = run_main(["https://example.com/a", "https://example.com/b", "--json",
                            "--export-dir", export_dir], pages)
        payload = json_blob_of(out)
        # 旧顶层键全部保留;exports 仅在 --export-dir 时出现
        for legacy in ("schema_version", "audited", "critical", "results"):
            self.assertIn(legacy, payload)
        self.assertEqual(payload["schema_version"], sa.SCHEMA_VERSION)
        self.assertEqual(payload["exports"]["dir"], export_dir)
        self.assertIn("canonical-missing.txt", payload["exports"]["files"])
        self.assertIn("summary.json", payload["exports"]["files"])
        # 逐页旧字段不删不改
        r = payload["results"]["https://example.com/a"]
        for key in ("verdict", "findings", "meta", "ai_search_health"):
            self.assertIn(key, r)
        self.assertEqual(r["verdict"], "pass")
        # 不加 --export-dir:无 exports 键,JSON blob 仍可从末位提取(完全向后兼容)
        out2, rc2 = run_main(["https://example.com/a", "--json"], pages)
        payload2 = json_blob_of(out2)
        self.assertNotIn("exports", payload2)
        # S2a B2:追加 market/limits 两个顶层键(本次市场阈值,供 prioritize/envelope 写建议)
        self.assertEqual(set(payload2), {"schema_version", "market", "limits", "audited",
                                         "critical", "results"})
        self.assertEqual(rc2, 0)

    def test_skip_refusal_in_denominator_not_in_rules(self):
        export_dir = os.path.join(self.tmp, "skip_exp")
        tiny = "<html><head><title>t</title></head></html>"          # <200B → fetch guard [SKIP]
        pages = dict(ROOT_FILES)
        pages.update({"/tiny": (200, {}, tiny),
                      "/b": (200, {}, page_html(canonical=False))})
        out, rc = run_main(["https://example.com/tiny", "https://example.com/b",
                            "--json", "--export-dir", export_dir], pages)
        self.assertEqual(rc, 0)                                     # SKIP 不算失败,退出码不受影响
        self.assertIn("| canonical-missing | WARN | 1/1 页(100%) |", LAST_STDERR[0])   # R5 修复:拒审页不进分母;--json 时 markdown 在 stderr(S2a B4)
        with open(os.path.join(export_dir, "summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        slugs = {r["slug"] for r in summary["rules"]}
        self.assertIn("canonical-missing", slugs)
        self.assertFalse(any("fetch" in s for s in slugs), slugs)   # 拒审不产生规则清单
        self.assertEqual(summary["audited"], 1)
        payload = json_blob_of(out)
        self.assertEqual(payload["results"]["https://example.com/tiny"]["verdict"], "refused")

    def test_help_documents_export_dir_and_coverage(self):
        r = run_script("site_audit.py", ["--help"])
        self.assertEqual(r.returncode, 0)
        text = r.stdout + r.stderr
        self.assertIn("--export-dir", text)
        self.assertIn("受影响面", text)
        self.assertIn("bulk export", text)
        self.assertIn("canonical-missing.txt", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
