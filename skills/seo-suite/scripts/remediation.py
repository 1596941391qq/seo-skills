#!/usr/bin/env python3
"""修复项生命周期管理(remediation ticket lifecycle;stdlib only)。
链路:envelope.py 的 audit-data.json → init 生成工单(remediations.json)→
update 状态机推进 → verify 对照两次 site_audit --json 自动核销(新增/已修复
按 URL+rule 认定,与 audit_compare.py 同口径——只读借鉴,不 import)→
report 生命周期汇总与 SLA。

数据文件 remediations.json(默认当前目录,--file 可指定):{items:[...]},每项:
  {id:"REM-001", rule_id, area(envelope 类别名), action(recommendation 或 phase
   item 的 action), phase:"now|month|ongoing"(对应 立即(本周)/短期(月内)/持续),
   severity, affected_urls[], status:"proposed|accepted|in_progress|implemented|
   verified|wontfix", created, deadline(now=+7d/month=+30d/ongoing=+90d),
   closed:null, verify_hint:"该 finding 在新体检中消失即自动核销", note:""}

状态机:proposed→accepted→in_progress→implemented 逐级前进(跳级/回退/同态拒绝);
verified 只能由 verify 自动设置(终态);wontfix 可从任意态进入且必须带 note
(接受≠消失,report 单独计数——照 monitor.py accepted_codes 语义)。超期 =
deadline 已过且未关闭(status ∈ proposed/accepted/in_progress/implemented;
verified/wontfix 已关闭不超期)。

verify 核销口径:非 wontfix/verified 单,其命中的 finding——rule_id 直接命中
(规则级,不限 URL)或 area+URL 交集兜底(审计 area 经类别映射落到工单 area 且
URL 在工单清单内)——在 old 有而 new 无 → verified + closed=今天 +
auto{verified_by:"audit diff", old_audit, new_audit};部分 URL 仍命中 →
保持 implemented 并附 partial 明细(非 implemented 单保持原状态仅附明细)。
同时新审计出现不属于任何现有工单的新 finding((url,rule) 在 new 不在 old,
rule 级无对应工单)→ 列"建议 init 增补"清单。

用法: python3 remediation.py <init|list|update|verify|report> [选项]
退出码: 0 正常 / 1 有超期(list/report)或 verify 发现增补建议 / 2 输入或参数错误。

并发口径(R5):save_data 原子写(tempfile + os.replace,读者只见旧版或新版,不落
半截文件)+ 数据文件级 flock(data_lock,照 monitor.py monitor_lock 惯例:lockfile
落在数据文件所在目录,LOCK_EX|LOCK_NB 轮询,超时 → 警告并跳过本次写)。
init/update/verify 的 load→改→save 全程持锁——两进程交替写也不覆盖丢单。"""
import contextlib
import fcntl
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

SCHEMA_VERSION = 1
DEFAULT_FILE = "remediations.json"
STATUSES = ("proposed", "accepted", "in_progress", "implemented", "verified", "wontfix")
OPEN_STATUSES = ("proposed", "accepted", "in_progress", "implemented")   # 未关闭 → 可超期
UPDATE_TARGETS = ("accepted", "in_progress", "implemented", "wontfix")
TRANSITIONS = {("proposed", "accepted"), ("accepted", "in_progress"),
               ("in_progress", "implemented")}
PHASES = ("now", "month", "ongoing")
PHASE_OF_NAME = {"立即(本周)": "now", "短期(月内)": "month", "持续": "ongoing"}
DEADLINE_DAYS = {"now": 7, "month": 30, "ongoing": 90}
SEVS = ("CRITICAL", "WARN", "INFO")
SEV_ORDER = {"CRITICAL": 0, "WARN": 1, "INFO": 2}
VERIFY_HINT = "该 finding 在新体检中消失即自动核销"
ID_RE = re.compile(r"^REM-(\d+)$")

# audit area → envelope 类别(envelope.AREA_CATEGORY 同源本地拷贝;保持 standalone
# 不 import 兄弟脚本——verify 的 area+URL 交集兜底匹配依赖此映射)。
AREA_CATEGORY = {
    "fetch": "availability",
    "staging": "indexability", "robots": "indexability", "ai-bots": "indexability",
    "canonical": "indexability",
    "duplicate_title": "uniqueness",
    "links": "discoverability", "sitemap": "discoverability",
    "llms.txt": "discoverability", "a11y": "discoverability",
    "title": "rankability", "description": "rankability", "h1": "rankability",
    "headings": "rankability", "content": "rankability", "images": "rankability",
    "schema": "rankability", "og": "rankability", "rendering": "rankability",
    "semantic-html": "rankability", "bluf": "rankability", "freshness": "rankability",
}

USAGE = """usage: remediation.py <init|list|update|verify|report> [选项]
修复项生命周期管理:envelope(audit-data.json)→ init 工单(remediations.json)→
update 状态机 → verify audit diff 自动核销 → report 汇总与 SLA。

数据文件 remediations.json(默认当前目录,--file 可指定):{items:[{id:"REM-001",
  rule_id, area, action, phase, severity, affected_urls[], status, created,
  deadline, closed, verify_hint, note}]}
  phase: now=立即(本周, deadline +7d) / month=短期(月内, +30d) / ongoing=持续(+90d)
  status: proposed → accepted → in_progress → implemented → verified(verify 自动);
          wontfix 可从任意态进入(必须带 note,接受≠消失,report 单独计数)

子命令:
  init --envelope audit-data.json [--file F]
      从 envelope 生成工单:每条 categories[].findings 一张(action 优先取
      action_plan 对应 item 的 action,缺省取 finding.recommendation;area=所在
      类别名);同 rule_id+phase 并单(affected_urls 合并去重);幂等——已存在同
      rule_id+phase 的单跳过,不重复建单。
  list [--status X] [--overdue] [--file F] [--json]
      表格(id/rule/phase/severity/status/deadline/URLs 数);超期行 deadline 后
      标 [!];--status 按状态过滤;--overdue 只看超期单。
  update REM-001 --status accepted|in_progress|implemented|wontfix [--note "..."] [--file F]
      状态机推进:逐级前进 proposed→accepted→in_progress→implemented,跳级/回退/
      同态拒绝;verified 只能由 verify 自动设置;wontfix 必须带 --note(closed=今天)。
  verify --old old_audit.json --new new_audit.json [--file F] [--json]
      自动核销(--old/--new 为两份 site_audit --json,与 audit_compare.py 同口径):
      非 wontfix/verified 单,其命中(rule_id 直接命中,或 area+URL 交集兜底)在
      old 有而 new 无 → status=verified、closed=今天、附
      auto{verified_by:"audit diff", old_audit, new_audit};部分 URL 仍命中 →
      保持 implemented 并附 partial 明细;新审计出现不属于任何现有工单的新
      finding → 列"建议 init 增补"清单(退出码 1)。
  report [--file F] [--json]
      生命周期汇总(Markdown):open/in_progress/overdue/verified/wontfix 计数 +
      SLA 达成率(verified 且 closed≤deadline ÷ 总 verified;无 verified 时 N/A)。

并发(R5):save_data 原子写(tempfile+os.replace)+ 数据文件级 flock(data_lock,
照 monitor.py 惯例);init/update/verify 的 load→改→save 全程持锁,两进程交替写
不覆盖丢单;等锁超时(默认 120s)→ 警告并跳过本次写。

退出码: 0 正常 / 1 有超期(list/report)或 verify 发现增补建议 / 2 输入或参数错误。"""


def die(msg, with_usage=False):
    """输入/参数错误 → stderr + 退出码 2。"""
    sys.stderr.write(msg + ("\n" + USAGE if with_usage else "") + "\n")
    sys.exit(2)


def now_utc():
    """当前 UTC 时间(秒级;套件统一 timezone.utc 口径)。"""
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_dt(s):
    """ISO 时间戳 → aware datetime;无法解析 → None;naive 视作 UTC。"""
    if not isinstance(s, str) or not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def load_json_tolerant(path, what):
    """容错读 JSON(文件前部混有逐 URL 文本行时从每个 '{' 起点试解,与
    health_score/audit_compare 同法);读不了/解析不出 → 退出码 2。"""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        die("读不了 %s: %s" % (what, e))
    cands = []
    try:
        cands.append(json.loads(text))
    except json.JSONDecodeError:
        pass
    for i, ch in enumerate(text):
        if ch == "{":
            try:
                cands.append(json.loads(text[i:]))
            except json.JSONDecodeError:
                continue
    for cand in cands:
        if isinstance(cand, dict):
            return cand
    die("无法从 %s 解析出 JSON: %s" % (what, path))


def check_item(it, where):
    """单张工单的最小结构校验;返回错误文案或 None。"""
    if not isinstance(it, dict):
        return "%s 不是对象" % where
    if not isinstance(it.get("id"), str) or not it["id"]:
        return "%s 缺 id 字符串" % where
    if not isinstance(it.get("rule_id"), str) or not it["rule_id"]:
        return "%s 缺 rule_id 字符串" % where
    if it.get("status") not in STATUSES:
        return "%s 的 status 非法(%r;合法值: %s)" % (where, it.get("status"), "|".join(STATUSES))
    return None


def load_data(path, create=False):
    """读工单数据文件;create=True 且文件不存在 → 空库(供 init 首建);
    文件存在但结构不符 → 退出码 2(不静默降级)。"""
    if not os.path.exists(path):
        if create:
            return {"items": []}
        die("工单数据文件不存在: %s(先运行 init 生成)" % path)
    data = load_json_tolerant(path, "工单数据(--file)")
    items = data.get("items")
    if not isinstance(items, list):
        die("工单数据格式不符: 缺 items 列表(%s)" % path)
    for n, it in enumerate(items, 1):
        err = check_item(it, "items[%d]" % n)
        if err:
            die("工单数据格式不符: %s(%s)" % (err, path))
    return data


def save_data(path, data):
    """原子写(R5):tempfile + os.replace(与 notify.save_state 同法)——中断/并发
    不落半截文件,读者只见旧版或新版;写失败(含 replace 前异常)自动清理临时文件。
    与 data_lock 配合:锁保证 read-modify-write 不交错,原子写保证读端永远可解析。"""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".tmp-", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


@contextlib.contextmanager
def data_lock(path, timeout=120.0):
    """数据文件级 flock(R5,照 monitor.py monitor_lock 惯例):lockfile 落在数据文件
    所在目录(.<文件名>.lock),flock LOCK_EX|LOCK_NB 每 0.5s 轮询;超时 → 警告并
    跳过本次写(SystemExit)——防本地 cron/CI 两进程交替写时 read-modify-write
    覆盖丢单。init/update/verify 的 load→改→save 全程持锁。"""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    lock_path = os.path.join(d, "." + os.path.basename(path) + ".lock")
    fh = open(lock_path, "w")
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() > deadline:
                    raise SystemExit(
                        "警告: 另一 remediation 进程持有 %s 超过 %.0fs,跳过本次写(防并发覆盖丢失)"
                        % (lock_path, timeout))
                time.sleep(0.5)
        yield
    finally:
        try:
            fcntl.flock(fh, fcntl.LOCK_UN)
        finally:
            fh.close()


def next_id(items):
    """顺延编号:现有最大 REM-<N> 的 N+1,零填充三位。"""
    mx = 0
    for it in items:
        m = ID_RE.match(str(it.get("id", "")))
        if m:
            mx = max(mx, int(m.group(1)))
    return "REM-%03d" % (mx + 1)


def sort_key(it):
    """按编号自然排序(REM-2 < REM-10);非标准 id 排最后按字典序。"""
    m = ID_RE.match(str(it.get("id", "")))
    return (0, int(m.group(1)), "") if m else (1, 0, str(it.get("id", "")))


def is_overdue(item, now):
    """超期 = deadline 已过且未关闭(verified/wontfix 已关闭,不再超期)。"""
    if item.get("status") not in OPEN_STATUSES:
        return False
    dl = parse_dt(item.get("deadline"))
    return dl is not None and dl < now


def fallback_phase(sev):
    """action_plan 缺某 rule 时的降级分派(镜像 envelope 口径的粗粒度版):
    CRITICAL→now,WARN→month,其余→ongoing。"""
    return {"CRITICAL": "now", "WARN": "month"}.get(sev, "ongoing")


# ---------------------------------------------------------------------------
# init:envelope → 工单
# ---------------------------------------------------------------------------
def cmd_init(rest):
    val = {"--envelope": None, "--file": DEFAULT_FILE}
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in val:
            if i + 1 >= len(rest):
                die("%s 需要一个值" % a, with_usage=True)
            val[a] = rest[i + 1]; i += 2
        else:
            die("未知参数 %r(init 子命令)" % a, with_usage=True)
    if not val["--envelope"]:
        die("缺少 --envelope\n" + USAGE)
    env = load_json_tolerant(val["--envelope"], "--envelope")
    categories = env.get("categories")
    if not isinstance(categories, list):
        die("--envelope 格式不符: 缺 categories 列表(应为 envelope.py 的 audit-data.json 输出)")
    # action_plan:rule_id → (phase, action);未知 phase 名的 item 只供 action 不定 phase
    plan = {}
    for ph in (env.get("action_plan") or {}).get("phases") or []:
        if not isinstance(ph, dict):
            continue
        phase = PHASE_OF_NAME.get(ph.get("name"))
        for it in ph.get("items") or []:
            rid = it.get("rule_id") if isinstance(it, dict) else None
            if isinstance(rid, str) and rid and rid not in plan:
                plan[rid] = (phase, it.get("action"))
    # findings 按 (rule_id, phase) 并单(affected_urls 合并去重,保首见顺序)
    merged, order = {}, []
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        cname = cat.get("name") or "other"
        for f in cat.get("findings") or []:
            if not isinstance(f, dict):
                continue
            rid = f.get("rule_id")
            if not isinstance(rid, str) or not rid:
                continue
            phase = (plan.get(rid) or (None, None))[0] or fallback_phase(f.get("severity"))
            key = (rid, phase)
            if key not in merged:
                merged[key] = {"area": cname,
                               "action": (plan.get(rid) or (None, None))[1]
                                         or f.get("recommendation") or "",
                               "severity": f.get("severity") if f.get("severity") in SEVS else "INFO",
                               "urls": []}
                order.append(key)
            m = merged[key]
            for u in f.get("affected_urls") or []:
                if isinstance(u, str) and u not in m["urls"]:
                    m["urls"].append(u)
            sev = f.get("severity")
            if sev in SEV_ORDER and SEV_ORDER[sev] < SEV_ORDER[m["severity"]]:
                m["severity"] = sev                      # 并单取最重严重度
    data = None
    with data_lock(val["--file"]):                       # R5:load→改→save 全程持锁
        data = load_data(val["--file"], create=True)
        existing = {(it.get("rule_id"), it.get("phase")) for it in data["items"]}
        created = skipped = 0
        for rid, phase in order:
            if (rid, phase) in existing:                 # 幂等:同 rule+phase 不重复建单
                skipped += 1
                continue
            m = merged[(rid, phase)]
            ts = now_utc()
            data["items"].append({
                "id": next_id(data["items"]), "rule_id": rid, "area": m["area"],
                "action": m["action"], "phase": phase, "severity": m["severity"],
                "affected_urls": m["urls"], "status": "proposed",
                "created": ts.isoformat(),
                "deadline": (ts + timedelta(days=DEADLINE_DAYS[phase])).isoformat(),
                "closed": None, "verify_hint": VERIFY_HINT, "note": ""})
            created += 1
        save_data(val["--file"], data)
    print("init: 新建 %d 张工单(跳过 %d 张已存在),共 %d 张 → %s"
          % (created, skipped, len(data["items"]), os.path.abspath(val["--file"])))
    return 0


# ---------------------------------------------------------------------------
# list:表格 + 超期标记
# ---------------------------------------------------------------------------
def cmd_list(rest):
    val = {"--status": None, "--file": DEFAULT_FILE}
    flag = {"--overdue": False, "--json": False}
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in val:
            if i + 1 >= len(rest):
                die("%s 需要一个值" % a, with_usage=True)
            val[a] = rest[i + 1]; i += 2
        elif a in flag:
            flag[a] = True; i += 1
        else:
            die("未知参数 %r(list 子命令)" % a, with_usage=True)
    if val["--status"] is not None and val["--status"] not in STATUSES:
        die("--status 非法 %r;合法值: %s" % (val["--status"], "|".join(STATUSES)))
    data = load_data(val["--file"])
    now = now_utc()
    rows = []
    for it in sorted(data["items"], key=sort_key):
        od = is_overdue(it, now)
        if val["--status"] is not None and it["status"] != val["--status"]:
            continue
        if flag["--overdue"] and not od:
            continue
        rows.append((it, od))
    overdue_n = sum(1 for _, od in rows if od)
    if flag["--json"]:
        payload = {"schema_version": SCHEMA_VERSION, "file": os.path.abspath(val["--file"]),
                   "count": len(rows), "overdue": overdue_n,
                   "items": [dict(it, overdue=od) for it, od in rows]}
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        cols = ("ID", "RULE", "PHASE", "SEVERITY", "STATUS", "DEADLINE", "URLS")
        table = [["%s" % it["id"], it["rule_id"], it["phase"], it["severity"], it["status"],
                  str(it.get("deadline") or "")[:10] + (" [!]" if od else ""),
                  str(len(it.get("affected_urls") or []))] for it, od in rows]
        widths = [len(c) for c in cols]
        for r in table:
            for n, v in enumerate(r):
                widths[n] = max(widths[n], len(v))
        L = [" ".join(c.ljust(widths[n]) for n, c in enumerate(cols)).rstrip(),
             " ".join("-" * w for w in widths)]
        for r in table:
            L.append(" ".join(v.ljust(widths[n]) for n, v in enumerate(r)).rstrip())
        print("\n".join(L))
        print("共 %d 张(超期 %d)%s" % (len(rows), overdue_n,
                                       " → %s" % val["--file"] if val["--file"] != DEFAULT_FILE else ""))
    return 1 if overdue_n else 0


# ---------------------------------------------------------------------------
# update:状态机推进
# ---------------------------------------------------------------------------
def cmd_update(rest):
    tid = None
    val = {"--status": None, "--note": None, "--file": DEFAULT_FILE}
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in val:
            if i + 1 >= len(rest):
                die("%s 需要一个值" % a, with_usage=True)
            val[a] = rest[i + 1]; i += 2
        elif a.startswith("-"):
            die("未知参数 %r(update 子命令)" % a, with_usage=True)
        elif tid is None:
            tid = a; i += 1
        else:
            die("多余的定位参数 %r(update 只接受一个工单 id)" % a, with_usage=True)
    if tid is None:
        die("缺少工单 id\n" + USAGE)
    if val["--status"] is None:
        die("缺少 --status\n" + USAGE)
    new = val["--status"]
    if new == "verified":
        die("verified 只能由 verify 子命令自动设置(audit diff 核销),不可手工指定")
    if new not in UPDATE_TARGETS:
        die("--status 非法 %r;update 只接受 %s" % (new, "|".join(UPDATE_TARGETS)))
    data = None
    with data_lock(val["--file"]):                       # R5:load→改→save 全程持锁
        data = load_data(val["--file"])
        item = next((it for it in data["items"] if it.get("id") == tid), None)
        if item is None:
            die("找不到工单 %r(%s 中共 %d 张)" % (tid, val["--file"], len(data["items"])))
        cur = item["status"]
        if new == "wontfix":
            if cur == "wontfix":
                die("wontfix 是终态,不可再次转换")
            if not (val["--note"] or "").strip():
                die("wontfix 必须带 --note 说明不修理由(接受≠消失,report 仍单独计数)")
        elif (cur, new) not in TRANSITIONS:
            die("非法状态转换 %s → %s;合法链 proposed→accepted→in_progress→implemented"
                "(逐级前进);wontfix 可从任意态进入(需 note);verified 仅由 verify 设置" % (cur, new))
        item["status"] = new
        if val["--note"] is not None:
            item["note"] = val["--note"]
        if new == "wontfix":
            item["closed"] = now_utc().isoformat()       # wontfix 即关闭
        if new == "implemented":
            # project.py 阶段判定用它和体检时间比先后;不用文件修改时间(新克隆后全部重置)
            item["implemented_at"] = now_utc().isoformat()
        save_data(val["--file"], data)
    print("update: %s %s → %s%s" % (tid, cur, new, "(closed=%s)" % item["closed"]
                                    if new == "wontfix" else ""))
    return 0


# ---------------------------------------------------------------------------
# verify:audit diff 自动核销 + 增补建议
# ---------------------------------------------------------------------------
def load_audit(path):
    """读 site_audit --json 输出(缺 results 字典 → 退出码 2)。"""
    d = load_json_tolerant(path, "审计文件")
    if not isinstance(d.get("results"), dict):
        die("--old/--new 格式不符: 缺 results 字典(应为 site_audit.py --json 输出): %s" % path)
    return d


def issue_index(audit):
    """(url, rule) → 最高严重度(SKIP/无 area 的 finding 不入索引;audit_compare 口径)。"""
    idx = {}
    for url, rec in audit["results"].items():
        if not isinstance(rec, dict):
            continue
        for f in rec.get("findings") or []:
            if not isinstance(f, dict):
                continue
            sev, area = f.get("severity"), f.get("area")
            if sev not in SEV_ORDER or not isinstance(area, str) or not area:
                continue
            key = (url, area)
            cur = idx.get(key)
            if cur is None or SEV_ORDER[sev] < SEV_ORDER[cur]:
                idx[key] = sev
    return idx


def item_hits(item, idx):
    """工单在审计索引中的命中 (url, rule) 集合:rule_id 直接命中(规则级,不限 URL),
    或 area+URL 交集兜底(审计 area 经类别映射落到工单 area 且 URL 在工单清单内)。"""
    rid, area = item.get("rule_id"), item.get("area")
    urls = set(item.get("affected_urls") or [])
    return {(u, a) for (u, a) in idx
            if a == rid or (AREA_CATEGORY.get(a, "other") == area and u in urls)}


def cmd_verify(rest):
    val = {"--old": None, "--new": None, "--file": DEFAULT_FILE}
    flag = {"--json": False}
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in val:
            if i + 1 >= len(rest):
                die("%s 需要一个值" % a, with_usage=True)
            val[a] = rest[i + 1]; i += 2
        elif a in flag:
            flag[a] = True; i += 1
        else:
            die("未知参数 %r(verify 子命令)" % a, with_usage=True)
    if not val["--old"] or not val["--new"]:
        die("缺少 --old 或 --new\n" + USAGE)
    data = None
    # R5:audit 文件只读可先解析;工单 load→核销→save 全程持锁(与 update 并发不覆盖)
    old_idx, new_idx = issue_index(load_audit(val["--old"])), issue_index(load_audit(val["--new"]))
    now = now_utc()
    verified_ids, partial_ids, untouched = [], [], 0
    with data_lock(val["--file"]):
        data = load_data(val["--file"])
        for it in data["items"]:
            if it["status"] in ("wontfix", "verified"):     # 终态不参与核销
                untouched += 1
                continue
            old_hits, new_hits = item_hits(it, old_idx), item_hits(it, new_idx)
            if not old_hits:
                untouched += 1                               # old 审计无此发现,无从判定
                continue
            if not new_hits:                                 # old 有 new 无 → 自动核销
                it["status"] = "verified"
                it["closed"] = now.isoformat()
                it["auto"] = {"verified_by": "audit diff",
                              "old_audit": val["--old"], "new_audit": val["--new"]}
                verified_ids.append(it["id"])
            else:                                            # 部分 URL 仍命中 → 保持现状+partial 明细
                it["auto"] = {"partial": [{"url": u, "rule": a} for u, a in
                                          sorted(new_hits, key=lambda p: (p[1], p[0]))],
                              "old_audit": val["--old"], "new_audit": val["--new"]}
                partial_ids.append(it["id"])
        save_data(val["--file"], data)
    # 增补建议:新 finding((url,rule) 在 new 不在 old,audit_compare 新增口径)
    # 且 rule 级不属于任何现有工单(含 wontfix/verified——工单按 rule 归并覆盖)。
    covered = {it.get("rule_id") for it in data["items"]}
    sugg = {}
    for (u, a) in set(new_idx) - set(old_idx):
        if a in covered:
            continue
        sugg.setdefault(a, []).append(u)
    suggested = [{"rule": r, "urls": sorted(sugg[r])} for r in sorted(sugg)]
    if flag["--json"]:
        payload = {"schema_version": SCHEMA_VERSION, "file": os.path.abspath(val["--file"]),
                   "verified": verified_ids, "partial": partial_ids,
                   "untouched": untouched, "suggested_init": suggested}
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        print("verify: 核销 %d 张(%s)/ 部分 %d 张(%s)/ 其余 %d 张未动"
              % (len(verified_ids), ", ".join(verified_ids) or "-",
                 len(partial_ids), ", ".join(partial_ids) or "-", untouched))
        if suggested:
            print("建议 init 增补(%d 个新规则无对应工单):" % len(suggested))
            for s in suggested:
                print("  - %s: %s" % (s["rule"], ", ".join(s["urls"])))
        else:
            print("无增补建议(新审计的新 finding 均有对应工单)")
    return 1 if suggested else 0


# ---------------------------------------------------------------------------
# report:生命周期汇总 + SLA
# ---------------------------------------------------------------------------
def _sla_met(item):
    closed, dl = parse_dt(item.get("closed")), parse_dt(item.get("deadline"))
    return closed is not None and dl is not None and closed <= dl


def cmd_report(rest):
    val = {"--file": DEFAULT_FILE}
    flag = {"--json": False}
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in val:
            if i + 1 >= len(rest):
                die("%s 需要一个值" % a, with_usage=True)
            val[a] = rest[i + 1]; i += 2
        elif a in flag:
            flag[a] = True; i += 1
        else:
            die("未知参数 %r(report 子命令)" % a, with_usage=True)
    data = load_data(val["--file"])
    items = data["items"]
    now = now_utc()
    counts = {s: 0 for s in STATUSES}
    for it in items:
        counts[it["status"]] += 1
    open_n = sum(counts[s] for s in OPEN_STATUSES)
    overdue = [it for it in items if is_overdue(it, now)]
    verified = [it for it in items if it["status"] == "verified"]
    met = sum(1 for it in verified if _sla_met(it))
    rate = round(met / len(verified), 3) if verified else None
    if flag["--json"]:
        payload = {"schema_version": SCHEMA_VERSION, "file": os.path.abspath(val["--file"]),
                   "total": len(items), "counts": counts, "open": open_n,
                   "overdue": [it["id"] for it in overdue],
                   "verified": len(verified), "wontfix": counts["wontfix"],
                   "sla": {"met": met, "total": len(verified), "rate": rate}}
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        L = ["# 修复项生命周期报告", "",
             "- 工单: %d 张(数据文件 %s)" % (len(items), os.path.abspath(val["--file"])),
             "- 状态分布: proposed %d / accepted %d / in_progress %d / implemented %d /"
             " verified %d / wontfix %d" % (counts["proposed"], counts["accepted"],
                                            counts["in_progress"], counts["implemented"],
                                            counts["verified"], counts["wontfix"]),
             "- 未关闭(open): %d;超期: %d(deadline 已过且未关闭)" % (open_n, len(overdue)),
             "- verified(本期核销): %d —— 本期=工单库当前生命周期内已核销(closed 非空)"
             % len(verified),
             "- wontfix: %d(接受≠消失,单独计数——monitor accepted_codes 同语义)"
             % counts["wontfix"],
             "- SLA 达成率: %s(verified 且 closed≤deadline ÷ 总 verified)"
             % ("%.0f%%" % (rate * 100) if rate is not None else "N/A")]
        if overdue:
            L += ["", "## 超期清单(%d)" % len(overdue)]
            L += ["- %s [%s] %s deadline %s" % (it["id"], it["severity"], it["rule_id"],
                                                str(it.get("deadline") or "")[:10])
                  for it in overdue[:10]]
            if len(overdue) > 10:
                L.append("- ...(其余 %d 张)" % (len(overdue) - 10))
        print("\n".join(L))
    return 1 if overdue else 0


COMMANDS = {"init": cmd_init, "list": cmd_list, "update": cmd_update,
            "verify": cmd_verify, "report": cmd_report}


def main():
    argv = sys.argv[1:]
    if any(a in ("-h", "--help") for a in argv):
        print(USAGE)
        return 0
    if not argv:
        sys.stderr.write("缺少子命令\n" + USAGE + "\n")
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd not in COMMANDS:
        die("未知子命令 %r;合法值: %s" % (cmd, "|".join(COMMANDS)), with_usage=True)
    return COMMANDS[cmd](rest)


if __name__ == "__main__":
    sys.exit(main())
