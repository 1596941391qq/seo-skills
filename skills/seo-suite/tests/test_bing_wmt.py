#!/usr/bin/env python3
"""bing_wmt.py 测试(R2-5 之二:Bing WMT JSON/REST API 薄客户端)。零网络:
_http_json 打桩(唯一网络出口);无 key 指路路径用 CLI(不发请求,构造上先于网络)。
覆盖:
  ① 凭证:--key > env BING_WMT_KEY;都缺 → doctor 式指路(exit 1,含获取路径与
     doctor.py --keys 校验提示,绝不猜、绝不发请求)
  ② SSRF 白名单:ssl.bing.com/www.bing.com/bing.com 及 bing.com 子域放行;
     https 缺失、bing.com.evil.com 后缀伪装、无关域拒
  ③ API 形态:URL=…/api.svc/json/<方法>?apikey=…&参数;响应解包 "d"(dict/单元素
     list 两形态);HTTP 200 也可能带 {"ErrorCode","Message"}(WCF 怪癖)——必须
     判为失败;apikey 不出现在任何输出(redact)
  ④ WCF 日期 "/Date(ms±zzzz)/" → YYYY-MM-DD;脏值→""(不猜)
  ⑤ urlstatus:GetUrlInfo 逐 URL(发现/最后抓取/HTTP/文档大小)+配额(GetUrlSubmissionQuota);
     d=null → 无抓取记录(known=false),不当 0
  ⑥ submit:1 URL→SubmitUrl;≥2→SubmitUrlBatch 按 500/调用分批;空清单 exit 2
     不触网;超过今日配额→WARNING 但仍提交
  ⑦ stats CSV 契约:Date,Query,Clicks,Impressions,CTR,Position(CTR 小数;
     Position=AvgImpressionPosition,-1 点击哨兵值不用)——产出直接喂 gsc_mining
     --mode query 跑通(round-trip 验证列对齐);空列表=还没有(stderr 注记,exit 0);
     --url 的 GetUrlInfo 块走 stderr,stdout 保持纯 CSV 可管道
用法: python3 tests/test_bing_wmt.py(tests/run_tests.py 自动发现本文件)"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import bing_wmt as BW    # noqa: E402 (需先入 SCRIPTS 路径)

KEY = "TESTKEY0123456789abcdef"
SITE = "https://example.com"


def run_cli(*args, env_extra=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.pop("BING_WMT_KEY", None)                     # 默认屏蔽外部 env,显式给 key
    env.update(env_extra or {})
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, "bing_wmt.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)


def run_main(argv):
    """in-process main():捕获 stdout/stderr,返回 (rc, out, err)。"""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = BW.main(argv)
    return rc, out.getvalue(), err.getvalue()


class _StubApi:
    """_http_json 打桩:按方法名回 canned 响应;记录 (url, data) 供断言。"""

    def __init__(self, responses=None, default=None):
        self.responses = dict(responses or {})        # 方法名 → 响应 dict/list
        self.default = default if default is not None else {}
        self.calls = []                               # (url, data)

    def __call__(self, url, data=None, headers=None, timeout=BW.DEFAULT_TIMEOUT):
        method = url.split("/api.svc/json/", 1)[1].split("?", 1)[0]
        self.calls.append((url, data))
        return self.responses.get(method, self.default)


def stubbed(responses=None, default=None):
    """装饰器助手:测试期间打桩 BW._http_json。"""
    stub = _StubApi(responses, default)
    return stub, mock.patch.object(BW, "_http_json", stub)


class CredentialTests(unittest.TestCase):
    """① 凭证寻径与 doctor 式指路。"""

    def test_missing_key_doctor_guidance_no_network(self):
        # in-process:_http_json 打桩为"不应触网",无 key 必须在触网前指路
        stub, patcher = stubbed(default={"__boom__": True})
        with patcher:
            rc, _out, err = run_main(["urlstatus", "--site", "example.com",
                                      "--url", "https://example.com/"])
        self.assertEqual(rc, 1)
        self.assertIn("BING_WMT_KEY", err)
        self.assertIn("API access", err)               # 获取路径(WMT 设置页)
        self.assertIn("doctor.py --keys", err)         # 校验工具指路
        self.assertEqual(stub.calls, [])               # 未发任何请求
        # CLI 同路径(exit 1,不猜)
        r = run_cli("urlstatus", "--site", "example.com", "--url", "https://example.com/")
        self.assertEqual(r.returncode, 1)
        self.assertIn("未找到 Bing WMT API key", r.stderr)

    def test_key_priority_and_env(self):
        # --key > env
        ap = BW.build_parser()
        self.assertEqual(BW.resolve_key(ap.parse_args(["urlstatus", "--site", "s",
                                                       "--key", "K1", "--url", "u"]),
                                        env={"BING_WMT_KEY": "K2"}), "K1")
        self.assertEqual(BW.resolve_key(ap.parse_args(["urlstatus", "--site", "s",
                                                       "--url", "u"]),
                                        env={"BING_WMT_KEY": " K2 "}), "K2")   # 去空白
        with self.assertRaises(BW.CredentialError):
            BW.resolve_key(ap.parse_args(["urlstatus", "--site", "s", "--url", "u"]), env={})


class GuardTests(unittest.TestCase):
    """② SSRF bing.com 域白名单(零网络,纯 URL 判定)。"""

    def test_bing_hosts_allowed(self):
        for url in ("https://ssl.bing.com/webmaster/api.svc/json/GetQueryStats",
                    "https://www.bing.com/x", "https://bing.com/x",
                    "https://api.bing.com/x"):          # bing.com 任意子域
            self.assertTrue(BW.guard_bing(url), url)

    def test_evil_hosts_rejected(self):
        for evil in ("http://ssl.bing.com/x",           # 非 https
                     "https://ssl.bing.com.evil.com/x", # 白名单域做后缀伪装
                     "https://evil.com/webmaster",      # 无关域
                     "file:///etc/passwd", ""):
            with self.assertRaises(BW.GuardError, msg=evil):
                BW.guard_bing(evil)


class ApiShapeTests(unittest.TestCase):
    """③ 端点 URL / "d" 解包 / 200 带 ErrorCode / redact。"""

    def test_api_call_url_and_params(self):
        stub, patcher = stubbed({"GetUrlSubmissionQuota": {"d": {"DailyQuota": 100,
                                                                 "MonthlyQuota": 1300}}})
        with patcher:
            q = BW.get_quota(KEY, SITE)
        self.assertEqual(q, {"daily": 100, "monthly": 1300})
        url = stub.calls[0][0]
        self.assertTrue(url.startswith(
            "https://ssl.bing.com/webmaster/api.svc/json/GetUrlSubmissionQuota?"), url)
        self.assertIn("apikey=" + KEY, url)             # key 进查询串
        self.assertIn("siteUrl=" + SITE.replace(":", "%3A").replace("/", "%2F"), url)

    def test_quota_d_list_form_tolerated(self):
        stub, patcher = stubbed({"GetUrlSubmissionQuota":
                                 {"d": [{"DailyQuota": 7, "MonthlyQuota": 70}]}})
        with patcher:
            self.assertEqual(BW.get_quota(KEY, SITE), {"daily": 7, "monthly": 70})

    def test_error_code_with_http_200_is_failure(self):
        """WMT 怪癖:错误可能随 200 返回(只看状态码会把失败当成功)。"""
        stub, patcher = stubbed(default={"ErrorCode": 3, "Message": "InvalidApiKey"})
        with patcher:
            rc, _out, err = run_main(["submit", "--site", "example.com", "--key", KEY,
                                      "--url", "https://example.com/a"])
        self.assertEqual(rc, 1)
        self.assertIn("InvalidApiKey", err)
        self.assertNotIn(KEY, err)                      # key 不进输出(redact)

    def test_redact_key(self):
        self.assertNotIn(KEY, BW.redact_key("...apikey=%s 失败" % KEY, KEY))
        self.assertIn("<redacted-key>", BW.redact_key("k=%s" % KEY, KEY))

    def test_normalize_site(self):
        self.assertEqual(BW.normalize_site("example.com"), "https://example.com")
        self.assertEqual(BW.normalize_site("https://example.com/"), "https://example.com/")
        with self.assertRaises(BW.UsageError):
            BW.normalize_site("")


class WcfDateTests(unittest.TestCase):
    """④ WCF "/Date(ms±zzzz)/" → YYYY-MM-DD。"""

    def test_wcf_forms(self):
        self.assertEqual(BW.parse_wcf_date("/Date(1316156400000-0700)/"), "2011-09-16")
        self.assertEqual(BW.parse_wcf_date("/Date(1700000000000)/"), "2023-11-14")
        self.assertEqual(BW.parse_wcf_date(1700000000000), "2023-11-14")   # 数字形态
        self.assertEqual(BW.parse_wcf_date("2026-09-01T00:00:00"), "2026-09-01")  # ISO 容错
        self.assertEqual(BW.parse_wcf_date("garbage"), "")
        self.assertEqual(BW.parse_wcf_date(None), "")


class UrlStatusTests(unittest.TestCase):
    """⑤ urlstatus:GetUrlInfo + 配额。"""

    def test_urlstatus_human_and_json(self):
        responses = {
            "GetUrlSubmissionQuota": {"d": {"DailyQuota": 99, "MonthlyQuota": 1250}},
            "GetUrlInfo": {"d": {"Url": "https://example.com/a",
                                 "HttpStatus": 200, "DocumentSize": 12345,
                                 "DiscoveryDate": "/Date(1700000000000)/",
                                 "LastCrawledDate": "/Date(1730000000000)/",
                                 "AnchorCount": 5, "TotalChildUrlCount": 0,
                                 "IsPage": True}},
        }
        stub, patcher = stubbed(responses)
        with patcher:
            rc, out, err = run_main(["urlstatus", "--site", "example.com", "--key", KEY,
                                     "--url", "https://example.com/a"])
        self.assertEqual(rc, 0)
        self.assertIn("今日 99 · 本月 1250", out)        # 配额读数
        self.assertIn("发现 2023-11-14", out)            # WCF 日期转换
        self.assertIn("最后抓取 2024-10-27", out)
        self.assertIn("HTTP 200", out)
        with patcher:
            rc, out, err = run_main(["urlstatus", "--site", "example.com", "--key", KEY,
                                     "--url", "https://example.com/a", "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertTrue(data["urls"][0]["known"])
        self.assertEqual(data["urls"][0]["discovery_date"], "2023-11-14")
        self.assertEqual(data["quota"], {"daily_left": 99, "monthly_left": 1250})

    def test_urlstatus_unknown_url_not_fake_zero(self):
        responses = {"GetUrlSubmissionQuota": {"d": {"DailyQuota": 100, "MonthlyQuota": 1300}},
                     "GetUrlInfo": {"d": None}}          # d=null:无抓取记录
        stub, patcher = stubbed(responses)
        with patcher:
            rc, out, _err = run_main(["urlstatus", "--site", "example.com", "--key", KEY,
                                      "--url", "https://example.com/never-seen"])
        self.assertEqual(rc, 0)
        self.assertIn("无该 URL 的抓取记录", out)        # 未收录 ≠ 0,不猜
        with patcher:
            _rc, out_j, _ = run_main(["urlstatus", "--site", "example.com", "--key", KEY,
                                      "--url", "https://example.com/never-seen", "--json"])
        self.assertFalse(json.loads(out_j)["urls"][0]["known"])

    def test_urlstatus_requires_url(self):
        rc, _out, err = run_main(["urlstatus", "--site", "example.com", "--key", KEY])
        self.assertEqual(rc, 2)
        self.assertIn("至少给一个 --url", err)


class SubmitTests(unittest.TestCase):
    """⑥ submit:SubmitUrl/SubmitUrlBatch/分批/配额告警/空清单。"""

    def test_submit_single_uses_submiturl(self):
        stub, patcher = stubbed({"GetUrlSubmissionQuota": {"d": {"DailyQuota": 100,
                                                                 "MonthlyQuota": 1300}},
                                 "SubmitUrl": {"d": None}})
        with patcher:
            rc, out, _err = run_main(["submit", "--site", "example.com", "--key", KEY,
                                      "--url", "https://example.com/a"])
        self.assertEqual(rc, 0)
        methods = [u.split("/api.svc/json/", 1)[1].split("?")[0] for u, _ in stub.calls]
        self.assertEqual(methods, ["GetUrlSubmissionQuota", "SubmitUrl"])
        body = json.loads(stub.calls[1][1])             # POST body
        self.assertEqual(body, {"siteUrl": SITE, "url": "https://example.com/a"})
        self.assertIn("SubmitUrl: 1 URL 已提交", out)

    def test_submit_batch_chunks_500_and_quota_warn(self):
        urls = ["https://example.com/p%d" % i for i in range(1200)]
        stub, patcher = stubbed({"GetUrlSubmissionQuota": {"d": {"DailyQuota": 100,
                                                                 "MonthlyQuota": 1300}},
                                 "SubmitUrlBatch": {"d": None}})
        with patcher:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                             encoding="utf-8") as f:
                f.write("# 注释行\n" + "\n".join(urls) + "\n")
                path = f.name
            try:
                rc, out, _err = run_main(["submit", "--site", "example.com", "--key", KEY,
                                          "--urls", path])
            finally:
                os.unlink(path)
        self.assertEqual(rc, 0)                          # 超配额=告警不阻断
        self.assertIn("超过今日剩余配额 100", out)
        batches = [(u, json.loads(d)) for u, d in stub.calls
                   if "SubmitUrlBatch" in u]
        self.assertEqual([len(b[1]["urlList"]) for b in batches], [500, 500, 200])
        self.assertTrue(all(b[1]["siteUrl"] == SITE for b in batches))
        self.assertIn("共 1200 URL 提交完成", out)

    def test_submit_dedupes_and_empty_is_usage_error(self):
        stub, patcher = stubbed({"GetUrlSubmissionQuota": {"d": {"DailyQuota": 100,
                                                                 "MonthlyQuota": 1300}},
                                 "SubmitUrlBatch": {"d": None}})
        with patcher:
            rc, out, _err = run_main(["submit", "--site", "example.com", "--key", KEY,
                                      "--url", "https://example.com/a",
                                      "--url", "https://example.com/a"])   # 重复
        self.assertEqual(rc, 0)
        # 去重后仅 1 条 → SubmitUrl 单条路径,且只带 1 个 URL
        submits = [(u, d) for u, d in stub.calls if "SubmitUrl" in u]
        self.assertEqual(len(submits), 1)
        self.assertTrue(submits[0][0].startswith(
            "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrl?"))
        self.assertEqual(json.loads(submits[0][1]),
                         {"siteUrl": SITE, "url": "https://example.com/a"})
        # 空清单:exit 2,且不触网(打桩会炸)
        def boom(*a, **k):
            raise AssertionError("空清单必须在校验期拒绝,不得触网")
        with mock.patch.object(BW, "_http_json", boom):
            rc, _out, err = run_main(["submit", "--site", "example.com", "--key", KEY])
        self.assertEqual(rc, 2)
        self.assertIn("至少给一个", err)


class StatsCsvContractTests(unittest.TestCase):
    """⑦ stats:CSV 契约 + gsc_mining round-trip + 空数据语义 + stdout 纯净。"""

    ROWS = [
        {"Query": "cheap flights", "Clicks": 10, "Impressions": 500,
         "AvgImpressionPosition": 6.25, "AvgClickPosition": 3.5,
         "Date": "/Date(1700000000000)/"},
        {"Query": "zero click term", "Clicks": 0, "Impressions": 100,
         "AvgImpressionPosition": 11.0, "AvgClickPosition": -1,   # Bing 无点击哨兵值
         "Date": "/Date(1700000000000)/"},
    ]

    def _stats(self, extra=()):
        stub, patcher = stubbed({"GetQueryStats": {"d": self.ROWS},
                                 "GetUrlInfo": {"d": None}})
        with patcher:
            result = run_main(["stats", "--site", "example.com", "--key", KEY, *extra])
        return result, stub

    def test_csv_columns_and_values(self):
        (rc, out, _err), _stub = self._stats()
        self.assertEqual(rc, 0)
        lines = out.splitlines()
        self.assertEqual(lines[0], "Date,Query,Clicks,Impressions,CTR,Position")
        self.assertEqual(lines[1], "2023-11-14,cheap flights,10,500,0.02,6.25")
        self.assertEqual(lines[2], "2023-11-14,zero click term,0,100,0.0,11.0")

    def test_csv_feeds_gsc_mining_roundtrip(self):
        """列对齐 gsc_mining 契约:产出 CSV 直接喂 gsc_mining --mode query 可解析。"""
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                         encoding="utf-8") as f:
            csv_path = f.name
        try:
            (rc, _out, _err), _stub = self._stats(["--out", csv_path])
            self.assertEqual(rc, 0)
            env = dict(os.environ, PYTHONIOENCODING="utf-8")
            g = subprocess.run([sys.executable, os.path.join(SCRIPTS, "gsc_mining.py"),
                                csv_path], capture_output=True, text=True,
                               encoding="utf-8", env=env, timeout=60)
            self.assertEqual(g.returncode, 0)
            # 两行均 pos5-20 且曝光≥20 → striking distance 命中 2 词
            self.assertIn("striking distance(pos5-20, 曝光≥20): 2 词", g.stdout)
            self.assertIn("cheap flights", g.stdout)
            # parse_ctr 对小数 CTR 全区间无歧义(契约核心)
            import gsc_mining as gm
            with open(csv_path, newline="", encoding="utf-8") as fh:
                rows = gm.read(csv_path)
            self.assertEqual(rows[0]["query"], "cheap flights")
            self.assertAlmostEqual(gm.parse_ctr(rows[0]["ctr"]), 0.02)
        finally:
            os.unlink(csv_path)

    def test_empty_rows_is_not_zero_not_error(self):
        stub, patcher = stubbed({"GetQueryStats": {"d": []}})
        with patcher:
            rc, out, err = run_main(["stats", "--site", "example.com", "--key", KEY])
        self.assertEqual(rc, 0)                          # 空=还没有,exit 0
        self.assertEqual(out.strip(), "Date,Query,Clicks,Impressions,CTR,Position")
        self.assertIn("数据还没有", err)                  # 语义注记走 stderr
        with patcher:
            rc, out_j, _ = run_main(["stats", "--site", "example.com", "--key", KEY,
                                     "--json"])
        data = json.loads(out_j)
        self.assertEqual(data["rows"], [])
        self.assertIn("不是 0 也不是错", data["note_empty"])

    def test_url_info_block_goes_to_stderr_stdout_stays_csv(self):
        responses = {"GetQueryStats": {"d": self.ROWS},
                     "GetUrlInfo": {"d": {"Url": "https://example.com/a",
                                          "HttpStatus": 200, "DocumentSize": 0,
                                          "DiscoveryDate": "/Date(1700000000000)/",
                                          "LastCrawledDate": None,
                                          "AnchorCount": 1, "IsPage": True}}}
        stub, patcher = stubbed(responses)
        with patcher:
            rc, out, err = run_main(["stats", "--site", "example.com", "--key", KEY,
                                     "--url", "https://example.com/a"])
        self.assertEqual(rc, 0)
        self.assertTrue(out.startswith("Date,Query,"))   # stdout 纯 CSV 可管道
        self.assertNotIn("单页状态", out)
        self.assertIn("单页状态(GetUrlInfo)", err)       # 状态块走 stderr
        self.assertIn("发现 2023-11-14", err)
        # stats --json 附 url_info 节
        with patcher:
            rc, out_j, _ = run_main(["stats", "--site", "example.com", "--key", KEY,
                                     "--url", "https://example.com/a", "--json"])
        data = json.loads(out_j)
        self.assertEqual(data["url_info"]["url"], "https://example.com/a")
        self.assertEqual(data["url_info"]["discovery_date"], "2023-11-14")



class FeedsTests(unittest.TestCase):
    """feeds:GetFeeds 列 sitemap 状态,--submit 先 SubmitFeed。
    响应取自 2026-11-06 everyinfra.com 的真实 GetFeeds(两张日语 sitemap 读不到)。"""

    REAL_20261106 = {"d": [
        {"__type": "Feed:#Microsoft.Bing.Webmaster.Api", "Compressed": False, "FileSize": 0,
         "LastCrawled": "/Date(1793912346000)/", "Status": "The page is not accessible",
         "Submitted": "/Date(1793900000000)/", "Type": "NA",
         "Url": "https://everyinfra.com/sitemap/ja-platform.xml", "UrlCount": 0},
        {"__type": "Feed:#Microsoft.Bing.Webmaster.Api", "Compressed": False, "FileSize": 0,
         "LastCrawled": "/Date(1793912335000)/", "Status": "Success",
         "Submitted": "/Date(1793900000000)/", "Type": "NA",
         "Url": "https://everyinfra.com/sitemap/ja-content.xml", "UrlCount": 161},
        {"__type": "Feed:#Microsoft.Bing.Webmaster.Api", "Compressed": False, "FileSize": 0,
         "LastCrawled": "/Date(1793912334000)/", "Status": "Pending",
         "Submitted": "/Date(1793945452221)/", "Type": "NA",
         "Url": "https://everyinfra.com/sitemap/ja-captcha.xml", "UrlCount": 0},
    ]}

    def test_not_accessible_feed_exits_3_and_is_named(self):
        _stub, patcher = stubbed({"GetFeeds": self.REAL_20261106})
        with patcher:
            rc, out, _err = run_main(["feeds", "--site", "everyinfra.com", "--key", KEY])
        self.assertEqual(rc, 3)
        self.assertIn("读不到", out)
        self.assertIn("ja-platform.xml  [The page is not accessible]", out)
        self.assertIn("1 张 sitemap Bing 读不到", out)

    def test_json_lists_only_unreadable_pending_counts_as_ok(self):
        _stub, patcher = stubbed({"GetFeeds": self.REAL_20261106})
        with patcher:
            rc, out, _err = run_main(["feeds", "--site", "everyinfra.com", "--key", KEY,
                                      "--json"])
        self.assertEqual(rc, 3)
        d = json.loads(out)
        self.assertEqual(d["not_readable"], ["https://everyinfra.com/sitemap/ja-platform.xml"])
        self.assertEqual([f["url_count"] for f in d["feeds"]], [0, 161, 0])
        self.assertEqual(d["feeds"][0]["last_crawled"], "2026-11-05")

    def test_submit_posts_feed_before_listing(self):
        stub, patcher = stubbed({"SubmitFeed": {"d": None},
                                 "GetFeeds": {"d": [self.REAL_20261106["d"][1]]}})
        sm = "https://everyinfra.com/sitemap/ja-platform.xml"
        with patcher:
            rc, out, _err = run_main(["feeds", "--site", "everyinfra.com", "--key", KEY,
                                      "--submit", sm])
        self.assertEqual(rc, 0)
        methods = [u.split("/api.svc/json/", 1)[1].split("?")[0] for u, _ in stub.calls]
        self.assertEqual(methods, ["SubmitFeed", "GetFeeds"])
        self.assertEqual(json.loads(stub.calls[0][1]),
                         {"siteUrl": "https://everyinfra.com", "feedUrl": sm})
        self.assertIn("已提交: " + sm, out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
