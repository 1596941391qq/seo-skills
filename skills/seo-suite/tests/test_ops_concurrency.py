#!/usr/bin/env python3
"""例 8 并发:两个进程同时跑 `ops weekly`,只产出一份本周目录、台账无重复、谁也不崩。

期望值来自需求卡 RQ-229 例 8(Echo 11-05 确认):「两个进程同时跑 ops weekly:只产出一份本周目录、台账无重复、
git 无冲突文件」。11-05 实测修前:一个进程 FileNotFoundError(两边共用 light.json.tmp,一边 replace 走了另一边的)。
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPS = os.path.join(BASE, "scripts", "ops.py")

PAGE = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s page of the concurrency fixture</title>'
        '<meta name="description" content="Fixture page %s used to check that two weekly runs do not collide.">'
        '<link rel="canonical" href="%s"></head><body><h1>%s</h1><p>Body text for %s.</p></body></html>')


class ConcurrentWeeklyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ops_conc_")
        site = os.path.join(self.tmp, "site")
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k):
                super().__init__(*a, directory=site, **k)

            def log_message(self, format, *args):  # noqa: A002 — 签名照基类
                pass

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
        base = "http://127.0.0.1:%d" % self.httpd.server_address[1]
        paths = ["/", "/a/", "/b/", "/c/"]
        for p in paths:
            os.makedirs(os.path.join(site, p.strip("/")), exist_ok=True)
            name = p.strip("/") or "home"
            with open(os.path.join(site, p.strip("/"), "index.html"), "w", encoding="utf-8") as f:
                f.write(PAGE % (name, name, base + p, name, name))
        with open(os.path.join(site, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>'
                    % "".join("<url><loc>%s%s</loc></url>" % (base, p) for p in paths))
        with open(os.path.join(site, "robots.txt"), "w", encoding="utf-8") as f:
            f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % base)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.ws = os.path.join(self.tmp, "seo-ops")
        os.makedirs(os.path.join(self.ws, "ledger"))
        with open(os.path.join(self.ws, "project.yaml"), "w", encoding="utf-8") as f:
            f.write("site: %s\nmarket: en\nschema_version: 2\n" % base)

    def tearDown(self):
        self.httpd.shutdown()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_two_weekly_runs_at_once(self):
        cmd = [sys.executable, "-I", OPS, "weekly", "--ws", self.ws, "--allow-local", "--date", "2026-11-09"]
        procs = [subprocess.Popen(cmd, cwd=self.tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for _ in range(2)]
        outs = [p.communicate(timeout=180) for p in procs]
        for p, (_, err) in zip(procs, outs):
            self.assertNotIn("Traceback", err, err[-2000:])
            self.assertIn(p.returncode, (0, 1), err[-2000:])          # 1 = 有硬告警(本地 http 站没有证书)
        self.assertEqual(os.listdir(os.path.join(self.ws, "runs")), ["2026-11-09"])
        rows = []
        with open(os.path.join(self.ws, "ledger", "issues.jsonl"), encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        keys = [json.dumps(r, sort_keys=True) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        leftovers = [n for n in os.listdir(os.path.join(self.ws, "runs", "2026-11-09")) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
