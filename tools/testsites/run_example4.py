#!/usr/bin/env python3
"""RQ-229 例 4:URL → 源码映射,20 条人工标注(labels_example4.json)。

判据写在 labels_example4.json 的 criterion(开工前写定):best 恰好等于标注才算对;另数「指错还敢动手」
(actionable 但 best 不对),目标 0。通过线 ≥90%。
测试站起在本机(干净状态);everyinfra 读线上页面 + 本机 origin/main。
用法:python3 run_example4.py [--skip-live] [--skip-next]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "skills", "seo-suite", "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, HERE)
import source_map as SM  # noqa: E402
from run_example3 import wait_up  # noqa: E402


def score(name, repo, labels, base=None, fetch_base=None):
    def anchors_for(u):
        if fetch_base:
            u = fetch_base + SM.urllib.parse.urlsplit(u).path
        return SM.fetch_anchors(u)
    urls = [(base or "") + u for u, _ in labels]
    res = SM.map_urls(repo, urls, 0.7, anchors_for)
    rows = []
    for r, (_, want) in zip(res, labels):
        rows.append({"site": name, "url": r["url"], "want": want, "best": r["best"],
                     "confidence": r["confidence"], "actionable": r["actionable"], "ok": r["best"] == want})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-live", action="store_true")
    ap.add_argument("--skip-next", action="store_true")
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    L = json.load(open(os.path.join(HERE, "labels_example4.json"), encoding="utf-8"))
    rows = []

    import static_site
    tmp = tempfile.mkdtemp(prefix="rq229_ex4_")
    base = "http://127.0.0.1:8611"
    site = os.path.join(tmp, "static")
    proc = static_site.start("clean", site, 8611, base)
    try:
        wait_up(base + "/", 30)
        rows += score("static", SM.Repo(site), L["static"]["labels"], base)
    finally:
        static_site.stop(proc)

    if not ns.skip_next:
        import next_site
        base = "http://127.0.0.1:8612"
        proc = next_site.start("clean", None, 8612, base)
        try:
            wait_up(base + "/", 120)
            rows += score("next", SM.Repo(next_site.SITE), L["next"]["labels"], base)
        finally:
            next_site.stop(proc)

    if not ns.skip_live:
        ei = L["everyinfra"]
        repo = SM.Repo(os.path.expanduser(ei["repo"]), ei["rev"])
        subprocess.run(["git", "-C", repo.path, "fetch", "-q", "origin", "main"], check=False)
        rows += score("everyinfra", repo, ei["labels"])

    ok = sum(r["ok"] for r in rows)
    bad_act = [r for r in rows if r["actionable"] and not r["ok"]]
    for r in rows:
        print("%s %-10s %-60s %.2f%s %s" % ("✅" if r["ok"] else "❌", r["site"], r["url"][-60:], r["confidence"],
                                          " 动手" if r["actionable"] else " 只列候选",
                                          "" if r["ok"] else "→ %s(应为 %s)" % (r["best"], r["want"])))
    rate = ok / len(rows) if rows else 0
    print("正确 %d/%d = %.0f%%;指错还敢动手 %d 条" % (ok, len(rows), rate * 100, len(bad_act)))
    if ns.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    return 0 if rate >= 0.9 and not bad_act else 1


if __name__ == "__main__":
    sys.exit(main())
