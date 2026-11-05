#!/usr/bin/env python3
"""field_data.py 读 CrUX 软导航实验指标(2026-11-05)。

期望值来自一手原文,不是读实现写的:
- 指标名与类型:CrUX API 文档「Metric value types」表(developer.chrome.com/docs/crux/api,
  核对 2026-11-05):experimental_cumulative_layout_shift_with_softnavs 为「2 decimal place
  double encoded as string」,experimental_interaction_to_next_paint_with_softnavs、
  experimental_largest_contentful_paint_with_softnavs 为「int milliseconds」,都有 p75。
- 口径:web.dev 2026-10-13 博文(web.dev/blog/crux-experimental-soft-navs)写明稳定版 Core Web
  Vitals 分数不变,实验版并列评估;所以实验值单列、不覆盖稳定版、不触发退出码。
- 没有这些字段的记录(大多数非 SPA 站,或 2026-10 之前的数据)照常输出,不报错。
零网络;被 run_tests.py 发现。
"""
import contextlib
import io
import json
import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

import field_data as fd  # noqa: E402

DOC_NAMES = {  # CrUX API 文档原文里的三个名字
    "experimental_largest_contentful_paint_with_softnavs",
    "experimental_interaction_to_next_paint_with_softnavs",
    "experimental_cumulative_layout_shift_with_softnavs",
}


def record(softnav=True, lcp_sn=1800, inp_sn=650, cls_sn="0.04"):
    """按 CrUX API 文档的类型造一条记录:稳定版 + (可选)软导航实验版。"""
    m = {"largest_contentful_paint": {"percentiles": {"p75": 4200}},
         "interaction_to_next_paint": {"percentiles": {"p75": 260}},
         "cumulative_layout_shift": {"percentiles": {"p75": "0.31"}}}
    if softnav:
        m["experimental_largest_contentful_paint_with_softnavs"] = {"percentiles": {"p75": lcp_sn}}
        m["experimental_interaction_to_next_paint_with_softnavs"] = {"percentiles": {"p75": inp_sn}}
        m["experimental_cumulative_layout_shift_with_softnavs"] = {"percentiles": {"p75": cls_sn}}
    return {"record": {"key": {"url": "https://spa.example/", "formFactor": "PHONE"}, "metrics": m}}


class SoftnavTests(unittest.TestCase):
    def setUp(self):
        self._saved = (fd.fetch_json, fd.ssrf_guard, fd.time)
        fd.ssrf_guard = lambda host: None
        fd._ssrf_cache.clear()

        class T:
            def sleep(self, s):
                pass
        fd.time = T()
        self._env = {k: os.environ.pop(k) for k in ("PSI_API_KEY", "CRUX_API_KEY") if k in os.environ}

    def tearDown(self):
        fd.fetch_json, fd.ssrf_guard, fd.time = self._saved
        os.environ.update(self._env)

    def run_main(self, rec, *extra):
        self.bodies = []

        def fake(url, payload=None, timeout=fd.DEFAULT_TIMEOUT):
            if payload is None:          # PSI:无现场、无实验,逼现场只来自 CrUX
                return {"loadingExperience": {"metrics": {}}, "lighthouseResult": {}}
            self.bodies.append(payload)
            return rec
        fd.fetch_json = fake
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fd.main(["--url", "https://spa.example/", "--key", "K"] + list(extra))
        return code, out.getvalue()

    def test_names_match_crux_api_doc(self):
        self.assertEqual(set(fd.CRUX_SOFTNAV_METRICS), DOC_NAMES)
        body = fd.crux_request_body("https://spa.example/", "page", "PHONE")
        self.assertTrue(DOC_NAMES <= set(body["metrics"]))      # 请求里要了这三项

    def test_types_parsed_per_doc(self):
        got = fd.parse_crux(record(), fd.CRUX_SOFTNAV_METRICS)
        self.assertEqual(got, {"LCP": 1800.0, "INP": 650.0, "CLS": 0.04})   # CLS 字符串 → 小数

    def test_shown_separately_and_not_in_exit_code(self):
        code, out = self.run_main(record(), "--json")
        r = json.loads(out)["results"][0]
        # 稳定版:LCP 4.2s、CLS 0.31 都在「差」档 → 退出码 1;实验版 INP 650ms 也差,但不额外影响
        self.assertEqual(code, 1)
        self.assertEqual(r["field"]["LCP"]["p75"], 4200.0)                # 稳定版不被实验值覆盖
        self.assertEqual(sorted(r["field_softnav"]), ["CLS", "INP", "LCP"])
        self.assertTrue(all(e["experimental"] for e in r["field_softnav"].values()))
        self.assertEqual(r["field_softnav"]["CLS"]["p75"], 0.04)

    def test_softnav_poor_alone_does_not_fail(self):
        good = {"record": {"metrics": {
            "largest_contentful_paint": {"percentiles": {"p75": 1500}},
            "interaction_to_next_paint": {"percentiles": {"p75": 120}},
            "cumulative_layout_shift": {"percentiles": {"p75": "0.02"}},
            "experimental_interaction_to_next_paint_with_softnavs": {"percentiles": {"p75": 900}}}}}
        code, out = self.run_main(good, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["results"][0]["field_softnav"]["INP"]["verdict"], "poor")

    def test_absent_fields_no_error(self):
        code, out = self.run_main(record(softnav=False), "--json")
        r = json.loads(out)["results"][0]
        self.assertEqual(r["field_softnav"], {})
        self.assertEqual([e for e in r["errors"] if e["source"] == "crux"], [])
        _, md = self.run_main(record(softnav=False))
        self.assertNotIn("含软导航", md)

    def test_markdown_section_when_present(self):
        _, md = self.run_main(record())
        self.assertIn("含软导航(experimental", md)
        self.assertIn("| LCP | 1.8 s |", md)


class FactsTableAlignment(unittest.TestCase):
    def test_facts_softnav_names_match_script(self):
        """事实表 #crux-softnav 写的三个名字 = 脚本常量(改一边忘另一边就红)。"""
        import re
        with open(os.path.join(BASE, "references", "overview", "facts.md"), encoding="utf-8") as f:
            text = f.read()
        body = re.search(r'<a id="crux-softnav"></a>(.*?)(?=<a id="|\Z)', text, re.S).group(1)
        self.assertEqual(set(re.findall(r"`(experimental_\w+_with_softnavs)`", body)), DOC_NAMES)
        self.assertEqual(set(fd.CRUX_SOFTNAV_METRICS), DOC_NAMES)


if __name__ == "__main__":
    unittest.main()
