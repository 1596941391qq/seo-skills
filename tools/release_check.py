#!/usr/bin/env python3
"""release_check.py — seo-skills 发版门(RQ-229 第 1 批;stdlib only)。

发版(打 tag、建 GitHub Release)前必须全绿;CI 在每次 push / PR 上也跑同一套(--no-net)。
任何一步红,退出码 1,不发版。

检查项:
  1. 版本号一致:manifest.json、install.sh、.claude-plugin/plugin.json、
     .claude-plugin/marketplace.json、.zcode-plugin/plugin.json、README(中英西,徽章和正文)
     与 CHANGELOG 最新一个已发版条目同一个号;--tag vX.Y.Z 时还要等于这个 tag。
  2. CHANGELOG:「未发版」段为空或只有「(暂无)」(发版时内容要挪进带号的段);--allow-unreleased 跳过。
  3. 单元测试:skills/seo-suite/tests 全绿。
  4. self_check.py(能力矩阵、文件结构)、freshness.py --fail-stale(过期断言)。
  5. 行为评测的快速档(不调模型、结果固定):tools/evals/fast_checks.py 存在就跑。

用法:
  python3 tools/release_check.py                 # 本机发版前
  python3 tools/release_check.py --tag v0.38.0   # 核对 tag 与版本号
  python3 tools/release_check.py --no-net --allow-unreleased   # CI 每次 push
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "seo-suite")
PY = sys.executable or "python3"


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def collect_versions():
    """每个位置 → 版本号(找不到记 None)。"""
    out = {}
    for rel in ("manifest.json", ".claude-plugin/plugin.json", ".zcode-plugin/plugin.json"):
        try:
            out[rel] = json.loads(read(rel)).get("version")
        except (OSError, ValueError):
            out[rel] = None
    try:
        mk = json.loads(read(".claude-plugin/marketplace.json"))
        out[".claude-plugin/marketplace.json"] = (mk.get("plugins") or [{}])[0].get("version")
    except (OSError, ValueError, IndexError, AttributeError):
        out[".claude-plugin/marketplace.json"] = None
    m = re.search(r'^VERSION="([^"]+)"', read("install.sh"), re.M)
    out["install.sh"] = m.group(1) if m else None
    for rel in ("README.md", "README.en.md", "README.es.md"):
        text = read(rel)
        badge = re.search(r"badge/version-([0-9][0-9.]*)-", text)
        body = re.search(r"`([0-9]+\.[0-9]+\.[0-9]+)`", text)
        out[rel + "(徽章)"] = badge.group(1) if badge else None
        out[rel + "(正文)"] = body.group(1) if body else None
    m = re.search(r"^## ([0-9]+\.[0-9]+\.[0-9]+) - \d{4}-\d{2}-\d{2}", read("CHANGELOG.md"), re.M)
    out["CHANGELOG.md(最新已发版)"] = m.group(1) if m else None
    return out


def unreleased_body():
    text = read("CHANGELOG.md")
    m = re.search(r"^## 未发版[^\n]*\n(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        return ""
    body = m.group(1).strip()
    return "" if body in ("", "(暂无)") else body


def run_step(name, cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    ok = p.returncode == 0
    tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
    return {"step": name, "ok": ok, "rc": p.returncode, "tail": tail}


def main(argv=None):
    ap = argparse.ArgumentParser(description="seo-skills 发版门")
    ap.add_argument("--tag", help="要打的 tag,如 v0.38.0")
    ap.add_argument("--allow-unreleased", action="store_true", help="允许 CHANGELOG 未发版段有内容(CI 用)")
    ap.add_argument("--no-net", action="store_true", help="跳过需要联网的检查(CI 用)")
    ap.add_argument("--skip-tests", action="store_true", help="只核版本与 CHANGELOG(调试用,发版不许用)")
    ns = ap.parse_args(argv)

    results = []
    vers = collect_versions()
    distinct = {v for v in vers.values()}
    ok_ver = len(distinct) == 1 and None not in distinct
    if ns.tag and ok_ver:
        ok_ver = ns.tag.lstrip("v") == next(iter(distinct))
    results.append({"step": "版本号一致", "ok": ok_ver,
                    "tail": ["%s = %s" % (k, v) for k, v in vers.items()] if not ok_ver
                    else ["全部 = %s" % next(iter(distinct))]})
    if not ns.allow_unreleased:
        body = unreleased_body()
        results.append({"step": "CHANGELOG 未发版段已挪进带号的段", "ok": not body,
                        "tail": [body[:200]] if body else []})
    if not ns.skip_tests:
        results.append(run_step("单元测试", [PY, "-I", "-m", "unittest", "discover", "-s", "tests"], SKILL))
        results.append(run_step("self_check", [PY, "-I", "scripts/self_check.py"], SKILL))
        results.append(run_step("freshness --fail-stale",
                                [PY, "-I", "scripts/freshness.py", "references", "--fail-stale"], SKILL))
        fast = os.path.join(ROOT, "tools", "evals", "fast_checks.py")
        if os.path.isfile(fast):
            results.append(run_step("行为评测快速档", [PY, "-I", fast], ROOT))

    bad = [r for r in results if not r["ok"]]
    for r in results:
        print("%s %s" % ("✅" if r["ok"] else "❌", r["step"]))
        if not r["ok"] or r["step"] == "版本号一致":
            for line in r.get("tail") or []:
                print("    " + line)
    print("发版门:%s" % ("通过" if not bad else "没过(%d 项红),不发版" % len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
