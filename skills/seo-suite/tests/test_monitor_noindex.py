#!/usr/bin/env python3
"""monitor.py D1 P0-1/P0-2 扩展测试(standalone,合成快照/打桩 fetch,零网络;
tests/run_tests.py 自动发现本文件)。覆盖:
meta noindex 检出 / header(X-Robots-Tag)noindex 检出 / 两者都无→indexable /
noindex_added 规则触发+抑制树关系(sitewide 根因折叠)/ noindex_removed 自愈 /
canonical 目标 404→broken / 连续 3 次失败才告警(防抖+run 落库连击计数)/
旧格式 monitor.db 快照兼容(缺新字段按 None,不崩不误报)/
http_get 保留响应头 + http_head 405 降 GET。"""
import email.message
import json
import os
import socket
import sys
import tempfile
import unittest
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import monitor as M  # noqa: E402

CFG = {"site": "https://example.com", "thresholds": dict(M.DEFAULT_THRESHOLDS)}

CLEAN_HTML = ("<html><head><title>Pricing</title>"
              "<meta name='description' content='d'>"
              "<link rel='canonical' href='https://example.com/pricing'>"
              "</head><body>ok</body></html>")


class _FakeResp:
    """最小 urllib 响应桩:状态/头/上下文管理器,body 不落地。"""

    def __init__(self, status, headers=None, body=b"<html></html>"):
        self.status = status
        self.headers = headers
        self._body = body

    def read(self, n=-1):
        return self._body

    def geturl(self):
        return "https://example.com/x"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _FakeOpener:
    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def open(self, req, timeout=None):
        method = req.get_method()
        self.calls.append(method)
        return self.handler(method)


class NoindexDetectionTests(unittest.TestCase):
    """P0-1 检出层:meta robots / X-Robots-Tag → check_page 的 indexable 判定。"""

    def setUp(self):
        self._orig_get, self._orig_head = M.http_get, M.http_head
        self.head_calls = []

        def fake_head(url, timeout=M.FETCH_TIMEOUT):
            self.head_calls.append(url)
            return {"status": 200}

        M.http_head = fake_head

    def tearDown(self):
        M.http_get, M.http_head = self._orig_get, self._orig_head

    def _check(self, body, headers=None):
        M.http_get = lambda url, timeout=M.FETCH_TIMEOUT: {
            "status": 200, "final_url": url, "elapsed_ms": 5.0, "body": body,
            "headers": headers or {}}
        return M.check_page("https://example.com/pricing")["metrics"]

    def test_meta_noindex_detected(self):
        m = self._check("<html><head><title>t</title>"
                        "<meta name='robots' content='noindex, nofollow'></head></html>")
        self.assertIs(m["indexable"], False)
        self.assertEqual(m["noindex_source"], "meta")
        # 属性反序 + 大小写不敏感
        m2 = self._check("<html><head><meta CONTENT='NOINDEX' NAME='Robots'></head></html>")
        self.assertIs(m2["indexable"], False)
        self.assertEqual(m2["noindex_source"], "meta")
        # index,follow 不是 noindex
        m3 = self._check("<html><head><meta name='robots' content='index, follow'></head></html>")
        self.assertIs(m3["indexable"], True)

    def test_header_noindex_detected(self):
        m = self._check(CLEAN_HTML, {"x-robots-tag": "noindex, noarchive"})
        self.assertIs(m["indexable"], False)
        self.assertEqual(m["noindex_source"], "header")
        # agent 前缀形态 + 键大小写不敏感
        m2 = self._check(CLEAN_HTML, {"X-Robots-Tag": "googlebot: noindex"})
        self.assertIs(m2["indexable"], False)
        self.assertEqual(m2["noindex_source"], "header")
        # 无 noindex 指令的头不算
        m3 = self._check(CLEAN_HTML, {"x-robots-tag": "max-snippet:-1"})
        self.assertIs(m3["indexable"], True)

    def test_both_absent_indexable_true(self):
        m = self._check(CLEAN_HTML)
        self.assertIs(m["indexable"], True)
        self.assertNotIn("noindex_source", m)
        # 双来源同时在场 → meta+header
        m2 = self._check("<meta name='robots' content='noindex'>",
                         {"x-robots-tag": "noindex"})
        self.assertIs(m2["indexable"], False)
        self.assertEqual(m2["noindex_source"], "meta+header")

    def test_self_canonical_skips_head_probe(self):
        """频率控制:自指 canonical(=本页)不发额外 HEAD——每页每 run 恰一次请求。"""
        self._check(CLEAN_HTML)     # canonical 指向本页
        self.assertEqual(self.head_calls, [])


class NoindexAlertRuleTests(unittest.TestCase):
    """P0-1 告警层:noindex_added(critical)/noindex_removed(info)/抑制树。"""

    def test_noindex_added_critical_message(self):
        prev = {"pages": {"/pricing": {"status": 200, "indexable": True}}}
        curr = {"pages": {"/pricing": {"status": 200, "indexable": False,
                                       "noindex_source": "meta"}}}
        alerts = M.compute_alerts(prev, curr, CFG)
        hit = [a for a in alerts if a["code"] == "noindex_added"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["level"], "critical")
        self.assertEqual(hit[0]["key"], "/pricing")
        self.assertIn("新增 noindex(来源:meta)", hit[0]["message"])
        self.assertIn("立即回滚", hit[0]["message"])
        self.assertEqual(hit[0]["details"]["source"], "meta")
        self.assertIn("回滚引入 noindex 的发布/模板改动", hit[0]["action"])
        self.assertEqual(hit[0]["boundary"], "urgent_pr")   # RQ-229:回滚类改为加急草稿 PR,agent 不直接改

    def test_noindex_removed_info_heal(self):
        prev = {"pages": {"/pricing": {"status": 200, "indexable": False,
                                       "noindex_source": "header"}}}
        curr = {"pages": {"/pricing": {"status": 200, "indexable": True}}}
        alerts = M.compute_alerts(prev, curr, CFG)
        hit = [a for a in alerts if a["code"] == "noindex_removed"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["level"], "info")
        self.assertIn("自愈", hit[0]["message"])

    def test_noindex_added_inhibited_by_sitewide_roots(self):
        """抑制树:robots 全站误封 / 首页宕机两类 sitewide 根因折叠页面级 noindex。"""
        prev = {"pages": {"/": {"status": 200, "indexable": True},
                          "/a": {"status": 200, "indexable": True}}}
        noindex_page = {"status": 200, "indexable": False, "noindex_source": "meta"}
        # 根因一:robots_sitewide_block
        curr = {"robots": {"robots": {"sitewide_block": True}},
                "pages": {"/a": noindex_page}}
        inhib = []
        alerts = M.compute_alerts(prev, curr, CFG, inhibited_out=inhib)
        self.assertFalse(any(a["code"] == "noindex_added" for a in alerts))
        self.assertTrue(any(i["code"] == "noindex_added"
                            and i["inhibited_by"] == "robots_sitewide_block" for i in inhib))
        # 根因二:homepage_down(站点级,首页宕机时页面级判定不可信)
        curr2 = {"pages": {"/": {"status": 503}, "/a": noindex_page}}
        inhib2 = []
        alerts2 = M.compute_alerts(prev, curr2, CFG, inhibited_out=inhib2)
        self.assertFalse(any(a["code"] == "noindex_added" for a in alerts2))
        self.assertTrue(any(i["code"] == "noindex_added"
                            and i["inhibited_by"] == "homepage_down" for i in inhib2))
        # 无根因时保留(critical 直达)
        curr3 = {"pages": {"/": {"status": 200, "indexable": True}, "/a": noindex_page}}
        alerts3 = M.compute_alerts(prev, curr3, CFG)
        self.assertTrue(any(a["code"] == "noindex_added" and a["level"] == "critical"
                            for a in alerts3))


class CanonicalTargetTests(unittest.TestCase):
    """P0-2:canonical 目标健康度探测 + canonical_target_broken(warn)+ 防抖。"""

    def setUp(self):
        self._orig_get, self._orig_head = M.http_get, M.http_head

    def tearDown(self):
        M.http_get, M.http_head = self._orig_get, self._orig_head

    def test_cross_target_head_probed_and_404_recorded(self):
        calls = []

        def fake_get(url, timeout=M.FETCH_TIMEOUT):
            return {"status": 200, "final_url": url, "elapsed_ms": 5.0,
                    "body": CLEAN_HTML.replace("https://example.com/pricing",
                                               "https://example.com/preferred"),
                    "headers": {}}

        def fake_head(url, timeout=M.FETCH_TIMEOUT):
            calls.append(url)
            return {"status": 404}

        M.http_get, M.http_head = fake_get, fake_head
        m = M.check_page("https://example.com/pricing")["metrics"]
        self.assertEqual(m["canonical_target_status"], 404)
        self.assertEqual(calls, ["https://example.com/preferred"])   # 每页每 run 一次
        # 相对路径 canonical 以 final_url 为基解析
        M.http_get = lambda url, timeout=M.FETCH_TIMEOUT: {
            "status": 200, "final_url": "https://example.com/pricing/", "elapsed_ms": 5.0,
            "body": "<link rel='canonical' href='/elsewhere'>", "headers": {}}
        m2 = M.check_page("https://example.com/pricing")["metrics"]
        self.assertEqual(m2["canonical_target_status"], 404)
        self.assertEqual(calls[-1], "https://example.com/elsewhere")
        # 网络层失败 → "error"(不猜具体码)
        M.http_head = lambda url, timeout=M.FETCH_TIMEOUT: (_ for _ in ()).throw(
            M.FetchError("HEAD 失败(测试桩)"))
        m3 = M.check_page("https://example.com/pricing")["metrics"]
        self.assertEqual(m3["canonical_target_status"], "error")

    def test_canonical_target_broken_warn(self):
        prev = {"pages": {"/pricing": {"status": 200, "indexable": True}}}
        base = {"status": 200, "indexable": True, "canonical": "https://example.com/gone",
                "canonical_target_status": 404, "canonical_fail_streak": 3}
        alerts = M.compute_alerts(prev, {"pages": {"/pricing": base}}, CFG)
        hit = [a for a in alerts if a["code"] == "canonical_target_broken"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]["level"], "warn")
        self.assertIn("canonical 指向 404 目标", hit[0]["message"])
        self.assertIn("索引信号自相矛盾", hit[0]["message"])
        self.assertEqual(hit[0]["details"]["fail_streak"], 3)
        # 网络不可达形态同样算 broken
        err = dict(base, canonical_target_status="error")
        hit2 = [a for a in M.compute_alerts(prev, {"pages": {"/pricing": err}}, CFG)
                if a["code"] == "canonical_target_broken"]
        self.assertEqual(len(hit2), 1)
        self.assertIn("不可达", hit2[0]["message"])
        # 2xx/3xx 不算(重定向已被跟随,以最终落点为准)
        ok = dict(base, canonical_target_status=301, canonical_fail_streak=3)
        self.assertFalse(any(a["code"] == "canonical_target_broken"
                             for a in M.compute_alerts(prev, {"pages": {"/pricing": ok}}, CFG)))

    def test_debounce_three_consecutive_failures(self):
        """连续 3 次失败才告警:streak 1/2 不动,streak 3 触发。"""
        prev = {"pages": {"/pricing": {"status": 200, "indexable": True}}}
        for streak in (1, 2):
            curr = {"pages": {"/pricing": {
                "status": 200, "indexable": True, "canonical": "https://example.com/gone",
                "canonical_target_status": 404, "canonical_fail_streak": streak}}}
            self.assertFalse(any(a["code"] == "canonical_target_broken"
                                 for a in M.compute_alerts(prev, curr, CFG)),
                             "streak=%d 不应告警" % streak)

    def test_fail_streak_continuation_and_reset(self):
        """apply_canonical_streaks:失败续数 / 成功清零 / 旧库无 prev 从 1 起。"""
        prev = {"pages": {"/p": {"canonical_target_status": 404, "canonical_fail_streak": 2}}}
        snap = {"pages": {"/p": {"canonical_target_status": 404}}}
        M.apply_canonical_streaks(prev, snap)
        self.assertEqual(snap["pages"]["/p"]["canonical_fail_streak"], 3)
        recovered = {"pages": {"/p": {"canonical_target_status": 200}}}
        M.apply_canonical_streaks(snap, recovered)
        self.assertEqual(recovered["pages"]["/p"]["canonical_fail_streak"], 0)
        first = {"pages": {"/p": {"canonical_target_status": "error"}}}
        M.apply_canonical_streaks(None, first)                     # 旧 monitor.db / 首跑
        self.assertEqual(first["pages"]["/p"]["canonical_fail_streak"], 1)
        legacy_prev = {"pages": {"/p": {"status": 200}}}           # 旧格式 prev(缺新字段)
        legacy_snap = {"pages": {"/p": {"canonical_target_status": 404}}}
        M.apply_canonical_streaks(legacy_prev, legacy_snap)
        self.assertEqual(legacy_snap["pages"]["/p"]["canonical_fail_streak"], 1)


class HttpLayerTests(unittest.TestCase):
    """http_get 保留响应头 / http_head 405 降 GET / scheme 守卫(打桩 opener+DNS)。"""

    def setUp(self):
        self._orig_gai = socket.getaddrinfo
        socket.getaddrinfo = lambda host, *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))]
        M._ssrf_cache.clear()
        self._orig_opener = M._opener

    def tearDown(self):
        socket.getaddrinfo = self._orig_gai
        M._ssrf_cache.clear()
        M._opener = self._orig_opener

    @staticmethod
    def _msg_headers():
        msg = email.message.Message()
        msg["X-Robots-Tag"] = "noindex, noarchive"
        msg["Content-Type"] = "text/html"
        return msg

    def test_http_get_preserves_response_headers(self):
        M._opener = _FakeOpener(lambda method: _FakeResp(200, headers=self._msg_headers()))
        r = M.http_get("https://example.com/x")
        self.assertEqual(r["headers"]["x-robots-tag"], "noindex, noarchive")
        self.assertTrue(M.header_noindex(r["headers"]))
        self.assertEqual(r["headers"]["content-type"], "text/html")

    def test_http_head_falls_back_to_get_on_405(self):
        opener = _FakeOpener(lambda method: _FakeResp(405 if method == "HEAD" else 200))
        M._opener = opener
        r = M.http_head("https://example.com/x")
        self.assertEqual(r["status"], 200)
        self.assertEqual(opener.calls, ["HEAD", "GET"])     # HEAD 405 → 降 GET 只读头
        opener2 = _FakeOpener(lambda method: _FakeResp(404))
        M._opener = opener2
        self.assertEqual(M.http_head("https://example.com/x")["status"], 404)
        self.assertEqual(opener2.calls, ["HEAD"])           # 非 405 不降级

    def test_http_head_scheme_guard(self):
        for bad in ("ftp://example.com/f", "file:///etc/passwd"):
            with self.assertRaises(M.FetchError):
                M.http_head(bad)


class CompatAndWiringTests(unittest.TestCase):
    """旧格式快照兼容(compute_alerts + 真库 cmd_diff 端到端)/ cmd_run 连击落库。"""

    @staticmethod
    def _fresh_dir(key_pages="/"):
        tmp = tempfile.mkdtemp(prefix="mon_noidx_")
        mdir = os.path.join(tmp, ".seo-monitor")
        rc = M.cmd_init(M.build_parser().parse_args(
            ["init", "--site", "https://example.com", "--market", "us",
             "--key-pages", key_pages, "--dir", mdir]))
        assert rc == 0
        return mdir

    @staticmethod
    def _insert_run(mdir, pages, ts_offset_days=0):
        from datetime import timedelta
        conn = M.open_db(mdir)
        ts = (datetime.now() - timedelta(days=ts_offset_days)).isoformat(timespec="seconds")
        cur = conn.execute(
            "INSERT INTO runs(ts,kind,status,checks_run,budget_used_sec,summary) "
            "VALUES(?,?, 'ok','daily',0,'')", (ts, "daily"))
        rid = cur.lastrowid
        for path, value in pages.items():
            conn.execute(
                "INSERT INTO snapshots(run_id,ts,\"check\",key,value,hash) VALUES(?,?,?,?,?,?)",
                (rid, ts, "pages", path, json.dumps(value), "h%d%s" % (rid, path)))
        conn.commit()
        conn.close()
        return rid

    def test_old_format_prev_snapshot_compat(self):
        """旧 monitor.db 快照(无 indexable/canonical_* 字段)作 prev:不崩、不误报;
        curr 新字段照常产 canonical_target_broken。"""
        mdir = self._fresh_dir()
        self._insert_run(mdir, {"/": {"status": 200, "latency_ms": 100.0,
                                      "title": "T", "title_meta_hash": "a"}})   # 旧格式 prev
        self._insert_run(mdir, {"/": {"status": 200, "latency_ms": 110.0,
                                      "title": "T", "indexable": False,
                                      "noindex_source": "meta",
                                      "canonical": "https://example.com/gone",
                                      "canonical_target_status": 404,
                                      "canonical_fail_streak": 3}})
        rc = M.cmd_diff(M.build_parser().parse_args(["diff", "--dir", mdir, "--format", "json"]))
        self.assertEqual(rc, 2)                                    # warn(canonical),无 critical
        # 反向:prev 是新格式(indexable True)→ noindex_added critical,rc=1
        mdir2 = self._fresh_dir()
        self._insert_run(mdir2, {"/": {"status": 200, "indexable": True, "title": "T"}})
        self._insert_run(mdir2, {"/": {"status": 200, "indexable": False,
                                       "noindex_source": "meta", "title": "T"}})
        rc2 = M.cmd_diff(M.build_parser().parse_args(["diff", "--dir", mdir2, "--format", "json"]))
        self.assertEqual(rc2, 1)
        # curr 缺新字段(fetch error 形态)也不崩不误报
        mdir3 = self._fresh_dir()
        self._insert_run(mdir3, {"/": {"status": 200, "indexable": True}})
        self._insert_run(mdir3, {"/": {"state": "error", "error": "x"}})
        rc3 = M.cmd_diff(M.build_parser().parse_args(["diff", "--dir", mdir3, "--format", "json"]))
        self.assertEqual(rc3, 0)

    def test_cmd_run_writes_fail_streak_then_diff_alerts(self):
        """cmd_run 接线:canonical 目标连续失败第 3 个 run 落 streak=3,diff 才 warn。"""
        mdir = self._fresh_dir(key_pages="/pricing")
        # run#1:目标 404,streak=2(模拟此前已连败两次)
        self._insert_run(mdir, {"/pricing": {
            "status": 200, "indexable": True, "title": "P",
            "canonical": "https://example.com/gone",
            "canonical_target_status": 404, "canonical_fail_streak": 2}})
        stub_results = {
            "robots": {"state": "ok", "metrics": {"status": 200, "hash": "h",
                                                  "sitewide_block": False}},
            "home": {"state": "ok", "metrics": {"status": 200, "latency_ms": 1.0,
                                                "title": "H", "indexable": True}},
            "key_pages": {"/pricing": {"state": "ok", "metrics": {
                "status": 200, "latency_ms": 1.0, "title": "P", "indexable": True,
                "canonical": "https://example.com/gone", "canonical_target_status": 404}}},
            "visibility": {"state": "skipped", "metrics": {}},
            "gsc": {"state": "skipped", "metrics": {}},
        }
        orig_run_checks, orig_hb = M.run_checks, os.environ.pop(
            "SEO_MONITOR_HEARTBEAT_URL", None)
        M.run_checks = lambda mdir, cfg, kind, budget: stub_results
        try:
            rc = M.cmd_run(M.build_parser().parse_args(
                ["run", "--checks", "daily", "--dir", mdir]))
        finally:
            M.run_checks = orig_run_checks
            if orig_hb is not None:
                os.environ["SEO_MONITOR_HEARTBEAT_URL"] = orig_hb
        self.assertEqual(rc, 0)
        conn = M.open_db(mdir)
        latest = M.latest_run_ids(conn, 1)[0]
        snap = M.load_snapshot(conn, latest)
        conn.close()
        self.assertEqual(snap["pages"]["/pricing"]["canonical_fail_streak"], 3)
        # run#2(旧库 streak=2,未达阈值)→ run#3(=3)的 diff 才出 canonical_target_broken
        rc = M.cmd_diff(M.build_parser().parse_args(["diff", "--dir", mdir, "--format", "json"]))
        self.assertEqual(rc, 2)
        conn = M.open_db(mdir)
        codes = [r["code"] for r in conn.execute(
            "SELECT code FROM alerts WHERE run_id=?", (latest,))]
        conn.close()
        self.assertIn("canonical_target_broken", codes)


if __name__ == "__main__":
    unittest.main(verbosity=1)
