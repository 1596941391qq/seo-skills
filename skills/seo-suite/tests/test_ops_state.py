#!/usr/bin/env python3
"""RQ-229 第 1 批:seo-ops/ 统一工作区的迁移与版本保护。

期望值来自需求卡 RQ-229 例 8(11-05 红队给的验收例子):
- 迁移:旧版 <slug>.seo/ + .seo-monitor/ + 散落文件 → seo-ops/,工单 id 集合完全相同、
  历史快照一个不少;旧位置改名保留,不删。
- 版本:更新版本写的状态,旧版 skill 以退出码 2 拒绝,不静默写坏。
- .gitignore:SQLite 缓存和原始 GSC 行不进 git。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
SITE = "https://stub.example"


def run(args, cwd):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, "project.py"), *args],
                          cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, PYTHONIOENCODING="utf-8"))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def legacy_fixture(root):
    """造一个 0.37.1 形态的旧状态:<slug>.seo/(schema 1,无字段)+ 根目录散落文件。"""
    ws = os.path.join(root, "stub-example.seo")
    write(os.path.join(ws, "project.yaml"),
          "site: %s\nmarket: ja\ntype: SaaS\ncreated: 2026-10-01T00:00:00+00:00\n"
          "history_dir: history\n" % SITE)
    for name in ("20261001-080000", "20261008-080000", "20261015-080000"):
        write(os.path.join(ws, "history", name, "audit.json"), '{"audited": 1, "results": {}}')
        write(os.path.join(ws, "history", name, "triage.json"),
              '{"generated_at": "2026-10-01T00:00:00+00:00"}')
    items = [{"id": "REM-%03d" % i, "rule_id": "r%d" % i, "status": "proposed"} for i in range(1, 8)]
    write(os.path.join(root, "remediations.json"), json.dumps({"items": items}))
    write(os.path.join(root, "panel.json"), '{"prompts": []}')
    mon = os.path.join(root, ".seo-monitor")
    write(os.path.join(mon, "config.json"), '{"site": "%s"}' % SITE)
    for i in (1, 2, 3):
        write(os.path.join(mon, "runs", "run-%05d.json" % i), '{"status": "ok"}')
    write(os.path.join(mon, "monitor.db"), "sqlite-bytes")
    return ws, [it["id"] for it in items]


class MigrateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ops_state_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_migrate_keeps_every_id_and_snapshot(self):
        old_ws, ids = legacy_fixture(self.tmp)
        r = run(["migrate", "--json"], self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dest = os.path.join(self.tmp, "seo-ops")
        with open(os.path.join(dest, "remediations.json"), encoding="utf-8") as f:
            got = sorted(it["id"] for it in json.load(f)["items"])
        self.assertEqual(got, sorted(ids))                                   # 工单 id 集合完全相同
        self.assertEqual(sorted(os.listdir(os.path.join(dest, "history"))),
                         ["20261001-080000", "20261008-080000", "20261015-080000"])  # 快照一个不少
        self.assertEqual(sorted(os.listdir(os.path.join(dest, "monitor", "runs"))),
                         ["run-00001.json", "run-00002.json", "run-00003.json"])
        self.assertTrue(os.path.isfile(os.path.join(dest, "panel.json")))
        with open(os.path.join(dest, "project.yaml"), encoding="utf-8") as f:
            y = f.read()
        self.assertIn("schema_version: 2", y)
        self.assertIn("market: ja", y)                                       # 原有字段保留
        self.assertIn("created: 2026-10-01T00:00:00+00:00", y)
        # 旧位置改名保留,不删;改名后不再被当成工作区
        self.assertFalse(os.path.exists(old_ws))
        self.assertTrue(any(n.startswith("stub-example.seo.migrated-") for n in os.listdir(self.tmp)))
        self.assertTrue(any(n.startswith("remediations.json.migrated-") for n in os.listdir(self.tmp)))
        # 迁移记录落 ledger
        with open(os.path.join(dest, "ledger", "migrations.jsonl"), encoding="utf-8") as f:
            entry = json.loads(f.readline())
        self.assertTrue(entry["ok"])
        # 迁完后 next/status 能直接认新工作区
        self.assertEqual(run(["status"], self.tmp).returncode, 0)

    def test_migrate_refuses_when_state_split_in_two_places(self):
        legacy_fixture(self.tmp)
        write(os.path.join(self.tmp, "stub-example.seo", "remediations.json"), '{"items": []}')
        r = run(["migrate"], self.tmp)
        self.assertEqual(r.returncode, 2)
        self.assertIn("两处都有", r.stdout + r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "seo-ops")))   # 没动手

    def test_init_on_legacy_workspace_points_to_migrate(self):
        legacy_fixture(self.tmp)
        r = run(["init", "--site", SITE, "--dir", "stub-example.seo"], self.tmp)
        self.assertEqual(r.returncode, 2)
        self.assertIn("migrate", r.stdout + r.stderr)


class SchemaGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ops_schema_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_newer_schema_rejected_with_exit_2(self):
        ws = os.path.join(self.tmp, "seo-ops")
        write(os.path.join(ws, "project.yaml"),
              "site: %s\nmarket: en\nschema_version: 99\nhistory_dir: history\n" % SITE)
        before = read(os.path.join(ws, "project.yaml"))
        for cmd in (["status"], ["next"], ["init", "--site", SITE]):
            r = run(cmd, self.tmp)
            self.assertEqual(r.returncode, 2, cmd)
            self.assertIn("升级", r.stdout + r.stderr)
        self.assertEqual(read(os.path.join(ws, "project.yaml")), before)

    def test_init_writes_gitignore_for_cache_and_raw_rows(self):
        r = run(["init", "--site", SITE], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.tmp, "seo-ops", ".gitignore"), encoding="utf-8") as f:
            gi = f.read().split()
        for pat in ("monitor/monitor.db", "cache/", "raw/", "monitor/gsc.csv"):
            self.assertIn(pat, gi)
        self.assertTrue(os.path.isdir(os.path.join(self.tmp, "seo-ops", "ledger")))


class SiteNormalizeTests(unittest.TestCase):
    """回归(2026-11-05 测试站实跑发现):init 曾丢端口、去 www.,预览站和 www 正式域名的站都抓错地址。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ops_site_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def site_after_init(self, site):
        r = run(["init", "--site", site], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        y = read(os.path.join(self.tmp, "seo-ops", "project.yaml"))
        shutil.rmtree(os.path.join(self.tmp, "seo-ops"))
        return [ln.split(": ", 1)[1] for ln in y.splitlines() if ln.startswith("site: ")][0]

    def test_port_and_www_kept(self):
        self.assertEqual(self.site_after_init("http://127.0.0.1:8601/"), "http://127.0.0.1:8601")
        self.assertEqual(self.site_after_init("https://www.example.com"), "https://www.example.com")


if __name__ == "__main__":
    unittest.main()
