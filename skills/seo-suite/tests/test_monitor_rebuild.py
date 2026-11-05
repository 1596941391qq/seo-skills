#!/usr/bin/env python3
"""RQ-229 第 1 批:monitor.db 降为缓存,可从进 git 的 runs/*.json 重建。

判据(需求卡 RQ-229 第 3 节「状态统一」,11-05 红队意见):SQLite 二进制不进 git;
新克隆没有 monitor.db 时,从 runs/run-*.json、diff-*.json、status-*.json 重放出的
runs / snapshots / alerts 三表,要和原库逐行一致(告警的已解决状态、隔离状态也一致)。
"""
import contextlib
import io
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
import monitor as M  # noqa: E402


def page(status):
    return {"state": "ok", "notes": [],
            "metrics": {"status": status, "title": "Acme", "meta_desc": "d", "canonical": "/",
                        "latency_ms": 100}}


def results_for(status):
    return {"robots": {"state": "ok", "notes": [], "metrics": {"hash": "h1", "sitewide_block": False}},
            "home": page(status), "redirects": {"state": "ok", "notes": [], "metrics": {}},
            "key_pages": {"/": page(status)}}


def dump(mdir):
    conn = sqlite3.connect(os.path.join(mdir, "monitor.db"))
    runs = conn.execute("SELECT id, kind, status FROM runs ORDER BY id").fetchall()
    snaps = conn.execute('SELECT run_id, "check", key, hash FROM snapshots '
                         'ORDER BY run_id, "check", key').fetchall()
    alerts = conn.execute("SELECT run_id, level, code, key, resolved, resolved_run FROM alerts "
                          "ORDER BY run_id, code, key").fetchall()
    conn.close()
    return runs, snaps, alerts


class RebuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="mon_rebuild_")
        self.mdir = os.path.join(self.tmp, "monitor")
        self._orig = M.run_checks
        self.queue = []
        M.run_checks = lambda mdir, cfg, kind, budget: self.queue.pop(0)

    def tearDown(self):
        M.run_checks = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def m(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return M.main(list(argv))

    def test_rebuild_matches_original_tables(self):
        self.assertEqual(self.m("init", "--site", "https://example.com", "--market", "us",
                                "--dir", self.mdir), 0)
        for status in (200, 503, 200, 200):          # 正常 → 首页挂 → 恢复 → 正常
            self.queue.append(results_for(status))
            self.m("run", "--dir", self.mdir)
            self.m("diff", "--dir", self.mdir)
        self.m("quarantine", "4", "--dir", self.mdir)
        before = dump(self.mdir)
        self.assertTrue(any(a[2] == "homepage_down" for a in before[2]),
                        "样例没触发首页告警,判据失效")
        self.assertTrue(any(a[2] == "homepage_down" and a[4] == 1 for a in before[2]))
        for suf in ("", "-wal", "-shm"):             # 模拟新克隆:缓存库不在
            p = os.path.join(self.mdir, "monitor.db" + suf)
            if os.path.exists(p):
                os.unlink(p)
        self.assertEqual(self.m("rebuild", "--dir", self.mdir), 0)
        after = dump(self.mdir)
        self.assertEqual(after[0], before[0])        # runs:编号、种类、状态(含隔离)
        self.assertEqual(after[1], before[1])        # snapshots 逐行哈希
        self.assertEqual(after[2], before[2])        # alerts:级别、指纹、已解决

    def test_default_dir_follows_seo_ops(self):
        cwd = os.getcwd()
        try:
            os.chdir(self.tmp)
            self.assertEqual(M.default_dir(), ".seo-monitor")
            os.makedirs("seo-ops")
            with open(os.path.join("seo-ops", "project.yaml"), "w", encoding="utf-8") as f:
                f.write("site: https://example.com\nschema_version: 2\n")
            self.assertEqual(M.default_dir(), os.path.join("seo-ops", "monitor"))
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
