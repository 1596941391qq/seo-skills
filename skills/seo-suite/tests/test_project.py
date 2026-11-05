#!/usr/bin/env python3
"""project.py 回归(stdlib unittest,standalone——助手照抄 run_tests.py 顶部,不 import
run_tests,被其 test_*.py 自动发现加载;零网络)。口径钉死脚本自身契约:

- init 工作区结构(project.yaml 受限 YAML 子集字段/history//references 6 处旧状态;
  幂等刷新保留 created;site 不同拒;未知市场 exit 2——markets.json 恒读真实脚本目录)
- adopt 只列不迁(6 处散落状态命中/未命中两态)
- run triage 编排:步骤次序 crawl(--max 50 --delay 1.0)→ audit(前 5 个 2xx/3xx
  URL,--market 取 project.yaml)→ health → prioritize → envelope;全部经
  SEO_PROJECT_SCRIPTS_DIR 打桩(子进程级,零网络);失败容错(crawl 挂 → 下游
  skipped 续汇总;health 挂 → envelope 照跑且不带 --health;envelope 挂 → 三件事
  退回 audit 严重度聚合);退出码 0 全成 / 1 有失败
- history 快照落盘:history/<YYYYMMDD-HHMMSS>/{crawl,audit,health,priority}.json
  + envelope/audit-data.json + triage.json(逐步完整命令)
- next 五阶段状态机:体检(无 envelope)/优先级(remediation init --envelope <path>)/
  修复(update <首张开单> <下一状态>)/验证(verify --old/--new 按工单 mtime 选体检;
  无新体检 → 复跑 triage + verify 提示)/监控(monitor init|run)
- status 聚合:五阶段各自最近产物 + 主分趋势 "72(Good) → 68(Fair)" + 工单开/闭
- --help 冒烟(根命令与全部子命令)"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

SITE = "https://stub.example"
WS_NAME = "seo-ops"   # RQ-229:默认工作区改为 seo-ops/

AUDIT_BLOB = json.dumps({
    "schema_version": 1, "audited": 2, "critical": 1,
    "results": {
        "https://stub.example/a": {"verdict": "fail", "meta": {}, "findings": [
            {"severity": "CRITICAL", "area": "robots", "message": "noindex"}]},
        "https://stub.example/b": {"verdict": "pass", "meta": {}, "findings": []}},
}, ensure_ascii=False)

ENVELOPE_BLOB = json.dumps({
    "schema_version": 1,
    "summary": {"main_score": 72, "band": "Good", "top_findings": [], "quick_wins": []},
    "categories": [{"name": "indexability", "findings": [{
        "rule_id": "robots", "title": "robots 屏蔽", "severity": "CRITICAL", "description": "d",
        "recommendation": "检查 noindex 是否误设",
        "affected_urls": ["https://stub.example/a"], "affected": 1}]}],
    "action_plan": {"phases": []},
}, ensure_ascii=False)


def run_project(args, cwd, extra_env=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, "project.py"), *args],
                          cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)


def mk_ws(cwd, site=SITE, market="en", type_=""):
    r = run_project(["init", "--site", site, "--market", market] + (["--type", type_] if type_ else []), cwd)
    assert r.returncode == 0, r.stderr
    return os.path.join(cwd, "seo-ops")


def fabricate_run(ws, name, audit=True, envelope=True, health=None):
    d = os.path.join(ws, "history", name)
    os.makedirs(d, exist_ok=True)
    if audit:
        with open(os.path.join(d, "audit.json"), "w", encoding="utf-8") as f:
            f.write(AUDIT_BLOB)
    if envelope:
        os.makedirs(os.path.join(d, "envelope"), exist_ok=True)
        with open(os.path.join(d, "envelope", "audit-data.json"), "w", encoding="utf-8") as f:
            f.write(ENVELOPE_BLOB)
    if health:
        with open(os.path.join(d, "health.json"), "w", encoding="utf-8") as f:
            json.dump(health, f)
    return d


def local_iso(y, mo, d, h, mi):
    """本机时间 → 带时区的 ISO 串(体检目录名按本机时间命名,两边口径一致)。"""
    import datetime as _dt
    return _dt.datetime(y, mo, d, h, mi).astimezone().isoformat()


def write_rem(ws, items):
    path = os.path.join(ws, "remediations.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False)
    return path


def rem_item(rid, status, closed=None):
    return {"id": rid, "rule_id": "robots", "area": "indexability", "phase": "now",
            "severity": "CRITICAL", "status": status, "affected_urls": ["https://stub.example/a"],
            "created": "2026-10-01T00:00:00+00:00", "closed": closed}


# ---------------------------------------------------------------- 打桩脚本目录

STUB_CRAWL = '''\
import json, os, sys
def val(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None
out = val("--out")
pages = [{"url": "https://stub.example" + p, "status": 200, "source": "sitemap"}
         for p in ("/pricing", "/features", "/pricing/integrations", "/features/x",
                   "/blog/launch", "/docs/api", "/shop", "/")]
json.dump({"schema_version": 1, "domain": "stub.example", "pages": pages, "edges": [],
           "stats": {"pages": len(pages), "errors": 0}}, open(out, "w"))
uo = val("--urls-out")
if uo:
    open(uo, "w").write("\\n".join(p["url"] for p in pages))
sys.exit(int(os.environ.get("STUB_CRAWL_RC", "0")))
'''

STUB_AUDIT = '''\
import json, os, sys
res = {}
for u in [a for a in sys.argv[1:] if a.startswith("http")]:
    res[u] = {"verdict": "fail", "meta": {}, "findings": [
        {"severity": "CRITICAL", "area": "robots", "message": "noindex meta"},
        {"severity": "WARN", "area": "title", "message": "title too long"}]}
print("== stub audit(逐 URL 人读行,同 site_audit --json stdout 形态) ==")
print(json.dumps({"schema_version": 1, "audited": len(res), "critical": len(res),
                  "results": res}))
sys.exit(int(os.environ.get("STUB_AUDIT_RC", "0")))
'''

STUB_HEALTH = '''\
import json, os, sys
print(json.dumps({"schema_version": "1.0", "main_score": 72, "band": "Good", "urls_total": 5, "urls_clean": 3}))
sys.exit(int(os.environ.get("STUB_HEALTH_RC", "0")))
'''

STUB_PRIORITIZE = '''\
import json, os, sys
print(json.dumps({"schema_version": "1.0", "impacts": [{"rule": "robots", "severity": "CRITICAL", "impact": 3.0}]}))
sys.exit(int(os.environ.get("STUB_PRIORITIZE_RC", "0")))
'''

STUB_ENVELOPE = '''\
import json, os, sys
def val(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None
out_dir = val("--out-dir")
os.makedirs(out_dir, exist_ok=True)
env = {"schema_version": 1,
       "summary": {"main_score": 72, "band": "Good", "top_findings": [], "quick_wins": []},
       "categories": [
         {"name": "indexability", "findings": [
            {"rule_id": "robots", "title": "robots 屏蔽", "severity": "CRITICAL",
             "description": "d", "recommendation": "检查 noindex 是否误设",
             "affected_urls": ["https://stub.example/pricing",
                               "https://stub.example/features"], "affected": 2}]},
         {"name": "rankability", "findings": [
            {"rule_id": "title", "title": "title 过长", "severity": "WARN",
             "description": "d", "recommendation": "压缩 title",
             "affected_urls": ["https://stub.example/docs/api"], "affected": 1},
            {"rule_id": "og", "title": "og 缺失", "severity": "INFO",
             "description": "d", "recommendation": "补 og 标签",
             "affected_urls": ["https://stub.example/shop"], "affected": 1}]}],
       "action_plan": {"phases": []},
       "stub_argv": sys.argv[1:]}
json.dump(env, open(os.path.join(out_dir, "audit-data.json"), "w"))
sys.exit(int(os.environ.get("STUB_ENVELOPE_RC", "0")))
'''


def stub_scripts_dir(tmp):
    d = os.path.join(tmp, "stub_scripts")
    os.makedirs(d, exist_ok=True)
    for name, body in (("site_crawl.py", STUB_CRAWL), ("site_audit.py", STUB_AUDIT),
                       ("health_score.py", STUB_HEALTH), ("prioritize.py", STUB_PRIORITIZE),
                       ("envelope.py", STUB_ENVELOPE)):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(body)
    return d


class ProjectTestCase(unittest.TestCase):
    """共用:每用例独立 tmp cwd,结束后清理。"""

    def setUp(self):
        # realpath:macOS 上 subprocess 的 getcwd() 把 /var/folders 解析成
        # /private/var/folders,统一到解析后路径,断言的绝对路径才可比
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="proj_test_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def run_triage(self, env=None):
        e = {"SEO_PROJECT_SCRIPTS_DIR": stub_scripts_dir(self.tmp)}
        e.update(env or {})
        return run_project(["run", "triage"], self.tmp, e)


class ProjectInitTests(ProjectTestCase):
    """init:工作区结构 / 幂等刷新 / 非法输入 exit 2"""

    def test_init_creates_workspace_structure(self):
        ws = mk_ws(self.tmp, type_="SaaS / 软件营销站")
        ypath = os.path.join(ws, "project.yaml")
        self.assertTrue(os.path.isfile(ypath))
        self.assertTrue(os.path.isdir(os.path.join(ws, "history")))
        import project as P
        data = P.parse_project_yaml(ypath)
        self.assertEqual(data["site"], SITE)
        self.assertEqual(data["market"], "en")
        self.assertEqual(data["type"], "SaaS / 软件营销站")
        self.assertRegex(data["created"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertEqual(data["history_dir"], "history")
        self.assertEqual(len(data["references"]), 6)      # R1-2:6 处散落状态指回
        for name, _desc in P.SCATTERED_STATE:
            self.assertIn(name, data["references"])

    def test_init_idempotent_refresh_keeps_created(self):
        ws = mk_ws(self.tmp, market="en")
        import project as P
        created1 = P.parse_project_yaml(os.path.join(ws, "project.yaml"))["created"]
        r = run_project(["init", "--site", SITE, "--market", "ja"], self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        data = P.parse_project_yaml(os.path.join(ws, "project.yaml"))
        self.assertEqual(data["created"], created1)       # 幂等刷新不重置 created
        self.assertEqual(data["market"], "ja")

    def test_init_rejects_unparseable_site(self):
        r = run_project(["init", "--site", "http://"], self.tmp)
        self.assertEqual(r.returncode, 2)

    def test_init_unknown_market_rejected(self):
        r = run_project(["init", "--site", SITE, "--market", "xx"], self.tmp)
        self.assertEqual(r.returncode, 2)
        self.assertIn("未知市场", r.stdout + r.stderr)

    def test_init_site_mismatch_rejected(self):
        run_project(["init", "--site", SITE, "--dir", os.path.join(self.tmp, "w.seo")], self.tmp)
        r = run_project(["init", "--site", "https://other.example",
                         "--dir", os.path.join(self.tmp, "w.seo")], self.tmp)
        self.assertEqual(r.returncode, 2)
        self.assertIn("site 不同", r.stdout + r.stderr)


class ProjectYamlTests(ProjectTestCase):
    """受限 YAML 子集解析(照 oracle_check 风格自实现,不依赖 PyYAML)"""

    def test_parse_subset_scalars_and_list(self):
        import project as P
        p = os.path.join(self.tmp, "p.yaml")
        with open(p, "w", encoding="utf-8") as f:
            f.write("# 注释行忽略\n"
                    "site: https://example.com\n"
                    "market: 'en'\n"                       # 引号剥离
                    "type:\n"                              # 空值 → 占位(None → 0 项)
                    "created: 2026-10-12T00:00:00+00:00\n"
                    "references:\n"
                    "  - .seo-monitor/\n"
                    "  - \"panel.json\"\n"
                    "  # 列表内注释\n"
                    "  - seo-fixes/\n")
        d = P.parse_project_yaml(p)
        self.assertEqual(d["site"], "https://example.com")
        self.assertEqual(d["market"], "en")
        self.assertEqual(d["references"], [".seo-monitor/", "panel.json", "seo-fixes/"])

    def test_site_type_value_with_slash_survives(self):
        ws = mk_ws(self.tmp, type_="媒体 / 新闻 / 内容站")
        import project as P
        self.assertEqual(P.parse_project_yaml(os.path.join(ws, "project.yaml"))["type"],
                         "媒体 / 新闻 / 内容站")            # 值取首个冒号后整段


class AdoptTests(ProjectTestCase):
    """adopt 只列不迁(6 处散落状态扫描)"""

    def test_adopt_lists_found_state(self):
        os.makedirs(os.path.join(self.tmp, ".seo-monitor"))
        for name in ("remediations.json", "panel.json"):
            with open(os.path.join(self.tmp, name), "w", encoding="utf-8") as f:
                f.write("{}")
        r = run_project(["adopt"], self.tmp)
        self.assertEqual(r.returncode, 0)
        for hit in (".seo-monitor/", "remediations.json", "panel.json"):
            self.assertIn(hit, r.stdout)
        self.assertNotIn(".trend-state.json", r.stdout.replace("trend_watch", ""))

    def test_adopt_none_found(self):
        r = run_project(["adopt"], self.tmp)
        self.assertEqual(r.returncode, 0)
        self.assertIn("未发现", r.stdout)


class TriageTests(ProjectTestCase):
    """run triage:编排序 / 失败续跑 / 快照落盘 / 首答三件事"""

    def _ws(self):
        return mk_ws(self.tmp)

    def _triage_json(self):
        ws = os.path.join(self.tmp, WS_NAME)
        runs = sorted(os.listdir(os.path.join(ws, "history")))
        self.assertEqual(len(runs), 1)
        with open(os.path.join(ws, "history", runs[0], "triage.json"), encoding="utf-8") as f:
            return runs[0], json.load(f)

    def test_triage_success_order_artifacts_and_verdict(self):
        self._ws()
        r = self.run_triage({"STUB_AUDIT_RC": "1"})     # audit 发现 CRITICAL 仍算成功
        self.assertEqual(r.returncode, 0, r.stderr)
        run_name, tj = self._triage_json()
        self.assertRegex(run_name, r"^\d{8}-\d{6}$")    # history/<YYYYMMDD-HHMMSS>/
        self.assertEqual([s["name"] for s in tj["steps"]],
                         ["crawl", "audit", "health", "prioritize", "envelope"])
        self.assertTrue(all(s["ok"] for s in tj["steps"]), tj["steps"])
        ws = os.path.join(self.tmp, WS_NAME)
        hist = os.path.join(ws, "history", run_name)
        for rel in ("crawl.json", "urls.txt", "audit.json", "health.json",
                    "priority.json", "envelope/audit-data.json"):
            self.assertTrue(os.path.isfile(os.path.join(hist, rel)), rel)
        # 首答:站型建议(SaaS 信号 4/8 页)+ 三件事(envelope 严重度聚合)
        self.assertIn("站型建议: SaaS / 软件营销站", r.stdout)
        self.assertIn("该做的三件事", r.stdout)
        acts = tj["verdict"]["top_actions"]
        self.assertEqual([a["rule_id"] for a in acts], ["robots", "title", "og"])
        self.assertEqual(acts[0]["severity"], "CRITICAL")
        self.assertIn("检查 noindex 是否误设", r.stdout)

    def test_triage_audit_uses_first_five_live_urls(self):
        self._ws()
        self.run_triage()
        _run, tj = self._triage_json()
        audit_cmd = [s for s in tj["steps"] if s["name"] == "audit"][0]["cmd"]
        urls = [a for a in audit_cmd if a.startswith("http")]
        self.assertEqual(len(urls), 5)
        self.assertEqual(urls[0], "https://stub.example/pricing")
        self.assertIn("--market", audit_cmd) and self.assertEqual(
            audit_cmd[audit_cmd.index("--market") + 1], "en")
        crawl_cmd = [s for s in tj["steps"] if s["name"] == "crawl"][0]["cmd"]
        i = crawl_cmd.index("--max")
        self.assertEqual(crawl_cmd[i + 1], "50")        # R1-7:--max 50 限速预算
        self.assertEqual(crawl_cmd[crawl_cmd.index("--delay") + 1], "1.0")

    def test_triage_crawl_failure_skips_downstream(self):
        self._ws()
        r = self.run_triage({"STUB_CRAWL_RC": "3"})     # 3=全部起点失败
        self.assertEqual(r.returncode, 1)
        _run, tj = self._triage_json()
        by = {s["name"]: s for s in tj["steps"]}
        self.assertFalse(by["crawl"]["ok"])
        for name in ("audit", "health", "prioritize", "envelope"):
            self.assertIsNotNone(by[name]["skipped"], name)   # 依赖缺失 → skipped 续汇总
            self.assertIn("上游未成功", by[name]["skipped"])

    def test_triage_health_failure_envelope_continues_without_health(self):
        self._ws()
        r = self.run_triage({"STUB_HEALTH_RC": "2"})
        self.assertEqual(r.returncode, 1)               # health 失败 → 整轮 1
        _run, tj = self._triage_json()
        by = {s["name"]: s for s in tj["steps"]}
        self.assertFalse(by["health"]["ok"])
        self.assertTrue(by["prioritize"]["ok"])         # 其余照跑
        self.assertTrue(by["envelope"]["ok"])
        ws = os.path.join(self.tmp, WS_NAME)
        hist = os.path.join(ws, "history", sorted(os.listdir(os.path.join(ws, "history")))[0])
        with open(os.path.join(hist, "envelope", "audit-data.json"), encoding="utf-8") as f:
            env = json.load(f)
        self.assertNotIn("--health", env["stub_argv"])  # 缺源不喂(envelope 容忍缺输入)
        self.assertIn("--priority", env["stub_argv"])
        self.assertIn("该做的三件事", r.stdout)          # 首答仍产出

    def test_triage_envelope_failure_falls_back_to_audit_aggregation(self):
        self._ws()
        r = self.run_triage({"STUB_ENVELOPE_RC": "2"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("audit 严重度聚合", r.stdout)      # 三件事退回 audit-rule-catalog 口径
        self.assertIn("robots", r.stdout)


class NextTests(ProjectTestCase):
    """next 五阶段状态机 → 下一条精确命令行"""

    def test_next_without_workspace_rc2(self):
        r = run_project(["next"], self.tmp)
        self.assertEqual(r.returncode, 2)
        self.assertIn("init --site", r.stdout + r.stderr)

    def test_next_stage_checkup_when_history_empty(self):
        ws = mk_ws(self.tmp)
        r = run_project(["next"], self.tmp)
        self.assertEqual(r.returncode, 0)
        self.assertIn("当前阶段: 1/5 体检", r.stdout)
        self.assertIn("run triage", r.stdout)

    def test_next_stage_priority_after_envelope(self):
        ws = mk_ws(self.tmp)
        run = fabricate_run(ws, "20261012-080000")
        r = run_project(["next"], self.tmp)
        self.assertEqual(r.returncode, 0)
        self.assertIn("当前阶段: 2/5 优先级", r.stdout)
        self.assertIn("remediation.py init --envelope", r.stdout)
        self.assertIn(os.path.join(run, "envelope", "audit-data.json"), r.stdout)

    def test_next_stage_fix_first_open_ticket(self):
        ws = mk_ws(self.tmp)
        fabricate_run(ws, "20261012-080000")
        rem = write_rem(ws, [rem_item("REM-001", "accepted"),
                             rem_item("REM-002", "proposed")])
        r = run_project(["next"], self.tmp)
        self.assertIn("当前阶段: 3/5 修复", r.stdout)
        self.assertIn("update REM-001 in_progress", r.stdout)   # 首张开单按 id 取下一状态
        self.assertIn(rem, r.stdout)

    def _implemented(self, rid, when):
        it = rem_item(rid, "implemented")
        it["implemented_at"] = when                          # remediation.py update 写入
        return it

    def test_next_stage_verify_with_newer_audit(self):
        # RQ-229:先后按记录里的时间判(体检目录名 / implemented_at),不看文件修改时间
        ws = mk_ws(self.tmp)
        run1 = fabricate_run(ws, "20261012-080000")              # 修复前体检
        rem = write_rem(ws, [self._implemented("REM-001", local_iso(2026, 10, 12, 8, 30))])
        run2 = fabricate_run(ws, "20261012-090000", envelope=False)  # 修复后复体检
        old = os.path.join(run1, "audit.json")
        new = os.path.join(run2, "audit.json")
        for path in (old, rem, new):                             # 模拟 git clone:修改时间全一样
            os.utime(path, (5000, 5000))
        r = run_project(["next"], self.tmp)
        self.assertIn("当前阶段: 4/5 验证", r.stdout)
        self.assertIn("verify", r.stdout)
        self.assertIn("--old %s" % old, r.stdout)
        self.assertIn("--new %s" % new, r.stdout)
        self.assertIn("--file %s" % rem, r.stdout)

    def test_next_stage_verify_without_newer_audit(self):
        ws = mk_ws(self.tmp)
        fabricate_run(ws, "20261012-080000")
        rem = write_rem(ws, [self._implemented("REM-001", local_iso(2026, 10, 12, 8, 30))])
        os.utime(os.path.join(ws, "history", "20261012-080000", "audit.json"), (9000, 9000))
        os.utime(rem, (1000, 1000))                              # 修改时间反着来也不影响判定
        r = run_project(["next"], self.tmp)
        self.assertIn("当前阶段: 4/5 验证", r.stdout)
        self.assertIn("run triage", r.stdout)                    # 先复体检
        self.assertIn("verify", r.stdout)                        # 附 verify 提示

    def test_next_stage_monitor_init_or_run(self):
        ws = mk_ws(self.tmp)
        fabricate_run(ws, "20261012-080000")
        write_rem(ws, [rem_item("REM-001", "verified", closed="2026-10-11T00:00:00+00:00")])
        r = run_project(["next"], self.tmp)
        self.assertIn("当前阶段: 5/5 监控", r.stdout)
        self.assertIn("monitor.py init --site %s" % SITE, r.stdout)   # 未建立 → init 收敛进工作区
        self.assertIn(os.path.join(ws, "monitor"), r.stdout)        # 新版工作区:seo-ops/monitor
        os.makedirs(os.path.join(ws, "monitor"))
        r2 = run_project(["next"], self.tmp)
        self.assertIn("monitor.py run", r2.stdout)                     # 已建立 → run


class StatusTests(ProjectTestCase):
    """status 一屏聚合:五阶段产物 + 主分趋势 + 工单开闭"""

    def test_status_aggregates(self):
        ws = mk_ws(self.tmp, type_="SaaS / 软件营销站")
        fabricate_run(ws, "20261012-080000", health={"main_score": 72, "band": "Good"})
        fabricate_run(ws, "20261012-090000", health={"main_score": 68, "band": "Fair"})
        write_rem(ws, [rem_item("REM-001", "proposed"),
                       rem_item("REM-002", "implemented"),
                       rem_item("REM-003", "verified", closed="2026-10-05T00:00:00+00:00")])
        r = run_project(["status"], self.tmp)
        self.assertEqual(r.returncode, 0)
        for stage in ("① 体检", "② 优先级", "③ 修复", "④ 验证", "⑤ 监控"):
            self.assertIn(stage, r.stdout)
        self.assertIn("audit.json(2 URL)", r.stdout)
        self.assertIn("envelope/audit-data.json", r.stdout)
        self.assertIn("开 1 / 闭 1", r.stdout)
        self.assertIn("待核销 1 / 已核销 1", r.stdout)
        self.assertIn("72(Good) → 68(Fair)", r.stdout)           # 主分趋势按 history 轮序
        self.assertIn("monitor/ 未建立", r.stdout)

    def test_status_json_shape(self):
        ws = mk_ws(self.tmp)
        fabricate_run(ws, "20261012-080000", health={"main_score": 72, "band": "Good"})
        r = run_project(["status", "--json"], self.tmp)
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertEqual(d["site"], SITE)
        self.assertEqual(d["stages"]["体检"], "history/20261012-080000/audit.json(2 URL)")
        self.assertEqual(d["score_trend"], ["72(Good)"])


class HelpSmokeTests(ProjectTestCase):
    """--help 冒烟(根命令 + 全部子命令)"""

    def test_help_exits_zero(self):
        for args in (["--help"], ["init", "--help"], ["adopt", "--help"],
                     ["run", "--help"], ["next", "--help"], ["status", "--help"]):
            r = run_project(args, self.tmp)
            self.assertEqual(r.returncode, 0, args)
            self.assertIn("usage: project.py", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
