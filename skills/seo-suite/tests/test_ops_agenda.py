#!/usr/bin/env python3
"""RQ-229 第 2 批:运营单的五态、通知规则、变更台账。

期望值来自需求卡 RQ-229(Echo 11-05 确认的例子),不是读实现推的:
- 例 3:预埋 10 个问题,修好 4 个、故意弄坏 1 个、新增 2 个 → 已解决 4 / 仍在 6 / 变差 1 / 新增 2。
  「弄坏」= 原有问题级别升高;没复查到的 URL 不能算已解决(红队意见 11-05)。
- 卡头 Echo 选项「只在出事时推」:有硬告警、或连续 2 期没人看才推 Telegram。
- 例 2:Search Console 标注文本 ≤120 字符。
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
import ops as O  # noqa: E402

SITE = "https://stub.example"


def item(n, sev="WARN", area="title"):
    url = "%s/p%d" % (SITE, n)
    msg = "问题 %d" % n
    return O.fingerprint(area, url, msg), {"fp": O.fingerprint(area, url, msg), "area": area, "url": url,
                                           "severity": sev, "message": msg, "source": "深审"}


class FiveStateTests(unittest.TestCase):
    def test_example_3_counts(self):
        prev = dict(item(n) for n in range(1, 11))                      # 预埋 10 个
        cur = dict(item(n) for n in range(5, 11))                       # 修好 1–4
        fp7, it7 = item(7, sev="CRITICAL")                              # 弄坏第 7 个(级别升高)
        cur[fp7] = it7
        cur.update(dict(item(n) for n in (11, 12)))                     # 新增 2 个
        checked = {O.norm("%s/p%d" % (SITE, n)) for n in range(1, 13)}
        states = O.classify(prev, cur, checked, checked, set())
        counts = {}
        for st, _, _ in states:
            counts[st] = counts.get(st, 0) + 1
        self.assertEqual(counts.get("resolved"), 4)
        self.assertEqual(counts.get("persisting", 0) + counts.get("worse", 0), 6)   # 仍在 6(含变差那 1 个)
        self.assertEqual(counts.get("worse"), 1)
        self.assertEqual(counts.get("new"), 2)

    def test_unchecked_url_is_not_resolved(self):
        prev = dict(item(n) for n in (1, 2))
        checked_now = {O.norm("%s/p2" % SITE)}                          # p1 这轮没抓到
        states = O.classify(prev, {}, set(), checked_now, set())
        got = {it["url"]: st for st, it, _ in states}
        self.assertEqual(got["%s/p1" % SITE], "unchecked")
        self.assertEqual(got["%s/p2" % SITE], "resolved")

    def test_regression_of_fixed_issue_is_worse(self):
        fp, it = item(3)
        states = O.classify({}, {fp: it}, set(), {O.norm(it["url"])}, {fp})
        self.assertEqual(states[0][0], "worse")

    def test_fingerprint_ignores_changing_numbers(self):
        a = O.fingerprint("title", SITE + "/x", "62 chars 超上限 60()")
        b = O.fingerprint("title", SITE + "/x", "71 chars 超上限 60()")
        self.assertEqual(a, b)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ops_ledger_")
        self.ws = os.path.join(self.tmp, "seo-ops")
        os.makedirs(os.path.join(self.ws, "ledger"))
        with open(os.path.join(self.ws, "project.yaml"), "w", encoding="utf-8") as f:
            f.write("site: %s\nschema_version: 2\n" % SITE)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_ops(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = O.main(list(argv) + ["--ws", self.ws])
        return rc, out.getvalue()

    def agenda(self, date, hard=False):
        d = os.path.join(self.ws, "runs", date)
        os.makedirs(d, exist_ok=True)
        O.write_json(os.path.join(d, "agenda.json"),
                     {"hard_alerts": [{"title": "首页 503"}] if hard else []})

    def test_notify_only_on_hard_alert_or_two_unread(self):
        self.agenda("2026-11-02")
        self.assertIsNone(O.notify_decision(self.ws)[1])                 # 一期没人看:不推
        self.agenda("2026-11-09")
        self.assertIn("连续 2 期", O.notify_decision(self.ws)[1])         # 连续两期没人看:推
        self.assertEqual(self.run_ops("ack", "2026-11-09")[0], 0)
        self.assertIsNone(O.notify_decision(self.ws)[1])                 # 看过一期:不推
        self.agenda("2026-11-16", hard=True)
        self.assertIn("硬告警", O.notify_decision(self.ws)[1])            # 有硬告警:推

    def test_change_annotation_limit_and_verify_dates(self):
        rc, _ = self.run_ops("change", "add", "--urls", SITE + "/a", "--summary", "x" * 121, "--rollback", "git revert a")
        self.assertEqual(rc, 2)
        rc, out = self.run_ops("change", "add", "--urls", SITE + "/a", "--summary", "改标题", "--rollback",
                               "git revert abc", "--at", "2026-11-01")
        self.assertEqual(rc, 0)
        row = O.read_jsonl(os.path.join(self.ws, "ledger", "changes.jsonl"))[0]
        self.assertEqual(row["verify_on"], ["2026-11-15", "2026-11-29"])  # 上线满 2 周、4 周

    def test_external_bundle_schema_guard(self):
        bad = os.path.join(self.tmp, "x.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump({"schema": "something-else"}, f)
        with self.assertRaises(O.UsageError):
            O.latest_external(self.ws, bad)


if __name__ == "__main__":
    unittest.main()
