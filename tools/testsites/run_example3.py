#!/usr/bin/env python3
"""RQ-229 例 3:复验闭环在自建测试站上跑三轮运营单,核对五态。

判据(需求卡例 3,开工前写定):
  - clean 轮:0 个问题(测试站本身没有杂质,否则后面的计数不可信)。
  - round1 轮:预埋 10 个,运营单「新增」正好是这 10 个(按 URL + area 对)。
  - round2 轮:已解决 4 / 仍在 6(其中变差 1)/ 新增 2,逐条对上 PLANTS / ROUND2,100% 才算过。

用法:python3 run_example3.py [--site static|next] [--keep DIR]
退出码:0 通过;1 没过。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(ROOT, "skills", "seo-suite", "scripts")
PY = sys.executable or "python3"


def wait_up(url, secs=60):
    import urllib.request
    t = time.time()
    while time.time() - t < secs:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:  # noqa: BLE001
            time.sleep(0.5)
    return False


def ops(ws_root, date):
    p = subprocess.run([PY, "-I", os.path.join(SCRIPTS, "project.py"), "ops", "weekly", "--allow-local",
                        "--date", date, "--json", "--workers", "4"],
                       cwd=ws_root, capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads(p.stdout)
    except ValueError:
        sys.stderr.write(p.stdout[-2000:] + p.stderr[-2000:])
        raise


def key(s, base):
    return (s["url"].replace(base, ""), s["area"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=("static", "next"), default="static")
    ap.add_argument("--keep")
    ns = ap.parse_args(argv)
    sys.path.insert(0, HERE)
    if ns.site == "static":
        import static_site as S
        port = 8601
    else:
        import next_site as S
        port = 8602
    base = "http://127.0.0.1:%d" % port
    tmp = ns.keep or tempfile.mkdtemp(prefix="rq229_ex3_")
    site_dir = os.path.join(tmp, "site")
    ws_root = os.path.join(tmp, "ops")
    os.makedirs(ws_root, exist_ok=True)
    subprocess.run([PY, "-I", os.path.join(SCRIPTS, "project.py"), "init", "--site", base, "--market", "en"],
                   cwd=ws_root, capture_output=True, check=True)
    results, ok = {}, True
    server = None
    try:
        for date, state in (("2026-01-05", "clean"), ("2026-01-12", "round1"), ("2026-01-19", "round2")):
            if server:
                S.stop(server)
            server = S.start(state, site_dir, port, base)
            if not wait_up(base + "/", 120):
                raise SystemExit("测试站没起来")
            agenda = ops(ws_root, date)
            states = {}
            for s in agenda["states"]:
                states.setdefault(s["state"], []).append(key(s, base))
            results[state] = {k: sorted(v) for k, v in states.items()}
            results[state]["hard_alerts"] = [h["title"] for h in agenda["hard_alerts"]]
    finally:
        if server:
            S.stop(server)

    def expect(name, got, want):
        nonlocal ok
        good = sorted(got) == sorted(want)
        ok = ok and good
        print("%s %s:%s" % ("✅" if good else "❌", name, "" if good else "\n   期望 %s\n   实得 %s" % (sorted(want), sorted(got))))

    plants = {pid: (path, area) for pid, path, _, area in S.PLANTS}
    expect("clean 轮 0 个问题", sum((v for k, v in results["clean"].items() if k != "hard_alerts"), []), [])
    expect("round1 新增 = 预埋 10 个", results["round1"].get("new", []), list(plants.values()))
    fixed = [plants[p] for p in S.ROUND2["fixed"]]
    worse = [plants[p] for p in S.ROUND2["worse"]]
    remaining = [v for p, v in plants.items() if p not in S.ROUND2["fixed"] and p not in S.ROUND2["worse"]]
    new = [(path, area) for _, path, _, area in S.ROUND2["new"]]
    r2 = results["round2"]
    expect("round2 已解决 4", r2.get("resolved", []), fixed)
    expect("round2 变差 1", r2.get("worse", []), worse)
    expect("round2 仍在 5(+变差 1 = 6)", r2.get("persisting", []), remaining)
    expect("round2 新增 2", r2.get("new", []), new)
    expect("round2 没有好转、未复查", r2.get("improved", []) + r2.get("unchecked", []), [])
    print(json.dumps(results, ensure_ascii=False, indent=1) if not ok else "例 3 通过(%s)" % ns.site)
    if not ns.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
