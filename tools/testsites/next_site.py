#!/usr/bin/env python3
"""Next.js App Router 测试站(RQ-229 例 3、例 4)的驱动:按状态写 plants.json → next build → next start。

站点源码在 next-site/(App Router;路由组、动态段、捕获段、内容 JSON、生成物和生成器都有)。
预埋问题与静态站同一套口径,只是路径不带尾斜杠、问题埋在 Next 的 metadata 和组件里。
依赖:next-site/ 下先 `pnpm install`(node_modules 不进 git)。
"""
import json
import os
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "next-site")

PLANTS = [
    ("P1", "/about", "title_missing", "title"),
    ("P2", "/pricing", "desc_missing", "description"),
    ("P3", "/blog/a", "h1_multiple", "h1"),
    ("P4", "/blog/b", "jsonld_missing", "schema"),
    ("P5", "/blog/c", "heading_skip", "headings"),
    ("P6", "/docs/start", "img_alt_missing", "images"),
    ("P7", "/docs/api", "noindex", "indexability"),
    ("P8", "/contact", "og_missing", "og"),
    ("P9", "/team", "status_404", "http"),
    ("P10", "/old-page", "redirect_301", "http"),
]
ROUND2 = {
    "fixed": ["P1", "P3", "P6", "P8"],
    "worse": {"P10": "status_404"},
    "new": [("N1", "/docs", "title_too_long", "title"), ("N2", "/blog", "desc_missing", "description")],
}


def plants_json(state):
    if state == "clean":
        return {}
    active = {pid: (path, kind) for pid, path, kind, _ in PLANTS}
    if state == "round2":
        for pid in ROUND2["fixed"]:
            active.pop(pid)
        for pid, kind in ROUND2["worse"].items():
            active[pid] = (active[pid][0], kind)
        for nid, path, kind, _ in ROUND2["new"]:
            active[nid] = (path, kind)
    return {path: kind for path, kind in active.values()}


def start(state, site_dir, port, base):
    with open(os.path.join(SITE, "plants.json"), "w", encoding="utf-8") as f:
        json.dump(plants_json(state), f)
    env = dict(os.environ, SITE_BASE=base, NEXT_TELEMETRY_DISABLED="1")
    nxt = os.path.join(SITE, "node_modules", ".bin", "next")
    b = subprocess.run([nxt, "build"], cwd=SITE, env=env, capture_output=True, text=True)
    if b.returncode != 0:
        raise SystemExit("next build 失败:\n" + (b.stdout + b.stderr)[-3000:])
    return subprocess.Popen([nxt, "start", "-p", str(port), "-H", "127.0.0.1"], cwd=SITE, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def stop(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    proc.wait(timeout=20)


if __name__ == "__main__":
    print(json.dumps(plants_json(sys.argv[1] if len(sys.argv) > 1 else "round1"), indent=1))
