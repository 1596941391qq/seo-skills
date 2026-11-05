#!/usr/bin/env python3
"""gsc_mining:关键词互抢和低 CTR 的两处误报(2026-11-06 在 everyinfra.com 29 天 query×page 数据上发现)。

期望值来自一个没看过脚本的子代理在跑数据之前写定的判定规则(品牌词不算、只差 #锚点是同一页、
/en/x 与 /es/x 是语言版本、同一语言里次页占 ≥20% 且合计 ≥10 才算互抢)。它按这个规则在真实数据里
数出 5 个真互抢;改前脚本报 11 组,其中品牌词一组有 93 页。真实数据不进公开仓库,这里按真实行的形状
缩成小样本,每类各留一条。
"""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(BASE, "scripts", "gsc_mining.py")

ROWS = [
    # 品牌词:几十条站点链接,--brand 排除
    ("acme", "https://acme.dev/en", 187, 276, 1.2),
    ("acme", "https://acme.dev/en/pricing", 0, 40, 1.3),
    ("acme", "https://acme.dev/en/docs", 0, 35, 1.2),
    # 真互抢:同一语言两页,次页 15/38 ≥20%,合计 ≥10
    ("widget free api endpoints", "https://acme.dev/en/widget-api/competitors", 0, 23, 14.9),
    ("widget free api endpoints", "https://acme.dev/en/widget-api", 0, 15, 19.7),
    # 只差 #锚点:同一页
    ("小部件api", "https://acme.dev/widget-api", 0, 16, 12.6),
    ("小部件api", "https://acme.dev/widget-api#capabilities", 0, 4, 9.5),
    ("小部件api", "https://acme.dev/widget-api#faq", 0, 4, 9.5),
    # 语言版本:/partners/x 与 /es/partners/x、/en/partners/x 按国家分流
    ("gizmo", "https://acme.dev/partners/gizmo", 1, 34, 6.7),
    ("gizmo", "https://acme.dev/es/partners/gizmo", 0, 17, 8.7),
    ("gizmo", "https://acme.dev/en/partners/gizmo", 0, 17, 10.3),
    # 一页占主导:次页 1/61 <20%
    ("thing api", "https://acme.dev/en/thing-api", 0, 59, 6.7),
    ("thing api", "https://acme.dev/en/thing-api/search", 0, 2, 20.0),
    # 量小:两页各半但合计 <10
    ("tiny api", "https://acme.dev/en/tiny-api", 0, 4, 9.0),
    ("tiny api", "https://acme.dev/en/tiny-api/list", 0, 4, 8.0),
]


def run(*args):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Query", "Page", "Clicks", "Impressions", "CTR", "Position"])
        for q, p, c, i, pos in ROWS:
            w.writerow([q, p, c, i, round(c / i, 6), pos])
        path = f.name
    try:
        out = subprocess.run([sys.executable, "-I", SCRIPT, path, *args, "--json"],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    finally:
        os.unlink(path)


class CannibalizationTests(unittest.TestCase):
    def test_only_true_conflicts(self):
        res = run("--mode", "matrix", "--brand", "acme")
        self.assertEqual([c["query"] for c in res["cannibalization"]], ["widget free api endpoints"])
        self.assertEqual(res["cannibalization"][0]["lang"], "en")

    def test_without_brand_flag(self):
        """不传 --brand:品牌词的首页占 79% 展示,按「一页占主导」本来就不报;锚点、语言版本照样不算。"""
        qs = [c["query"] for c in run("--mode", "matrix")["cannibalization"]]
        self.assertEqual(qs, ["widget free api endpoints"])


class LowCtrMergeTests(unittest.TestCase):
    def test_query_page_export_merged_by_query(self):
        """改前:品牌词每条站点链接各算一条低 CTR(真实数据里 everyinfra 列了 7 次)。"""
        res = run()
        qs = [x["query"] for x in res["low_ctr"]]
        self.assertEqual(len(qs), len(set(qs)))
        sd = {x["query"]: x for x in res["striking_distance"]}
        # widget free api endpoints 合并后 38 展示、加权排名 (23*14.9+15*19.7)/38 = 16.8
        self.assertEqual(sd["widget free api endpoints"]["impressions"], 38)
        self.assertAlmostEqual(sd["widget free api endpoints"]["pos"], 16.8, places=1)


if __name__ == "__main__":
    unittest.main()
