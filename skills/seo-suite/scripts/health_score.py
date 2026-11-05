#!/usr/bin/env python3
"""站点健康分:读 site_audit.py --json 输出 → 三家口径合一(stdlib only)。
- 主分【Ahrefs 官方】:(无 CRITICAL 的 URL 数 ÷ 内链 URL 总数)×100;WARN/INFO 完全不扣
  主分,单列 WARN/INFO 子分(同公式按各自严重度统计);分档 Weak 0-30/Fair 31-70/
  Good 71-90/Excellent 91-100。SKIP(fetch guard 拒审)URL 不进分子分母,单列 refused。
- 类别树【Lumar 官方结构】:六大类每类 100 起步,只有负号(negative)检查扣分;
  扣分 = (命中 URL 数 ÷ 总 URL 数) × 权重;合成分 = Σ(类分×类权重)÷Σ类权重,
  类权重 = 类内负号检查权重和【Lumar 官方】;权重→扣分数值映射未公开,
  本脚本自定 CRITICAL=3/WARN=1/INFO=0.25(类分下限 0,归一化封顶)。缺数据源的类
  输出 N/A(data_source_missing)不计入合成分——照抄 Lumar N/A 语义(如 Experience
  无速度/安全/外链数据源时整类 N/A)。
- impact 排序【Ryte 官方】:每检查项 impact = 命中占比 × 严重度平方(严重度数值映射
  自定[推断]:CRITICAL=3/WARN=2/INFO=1);>0 按降序进"立即处理",=0 标
  "opportunity 值得探索"。
- --ignore/--severity【Ahrefs 官方语义】:忽略 = 不进 findings 不进分,报告列 ignored;
  降级(如 robots=warn)后自动退出主分扣分项;--config 持久化
  {"rules":{"<id>":{"enabled":bool,"severity":"..."}}},CLI 优先于配置文件。
- coverage:分数基于爬取样本,恒带 coverage_note(Ryte 官方口径:样本<全站,两次分数不可比)。
用法: python3 health_score.py --input audit.json [--ignore r1,r2] [--severity rule=sev]
                              [--config rules.json] [--json]
退出码: 0 正常 / 1 主分档 Weak(0-30) / 2 输入或参数错误。"""
import sys, os, json

def die(msg):
    """输入/参数错误 → stderr + 退出码 2(正常 0/Weak 档 1,见 USAGE)。"""
    sys.stderr.write(msg + "\n")
    sys.exit(2)


SCHEMA_VERSION = "1.0"
COVERAGE_NOTE = "基于样本,分数不可与全站直接比较"  # Ryte 官方口径,输出恒带
NA_REASON = "data_source_missing"                  # Lumar N/A 语义:缺数据源不计入总分
# 分档【Ahrefs 官方】:Weak 0-30 / Fair 31-70 / Good 71-90 / Excellent 91-100
BANDS = (("Excellent", 91), ("Good", 71), ("Fair", 31), ("Weak", 0))
# 扣分权重:自定——Lumar 权重→扣分数值映射未公开(官方只公开"每类 100 起步/负号才扣/
# 类权重=类内负号检查权重和");INFO 0.25 使纯提示项即便全站命中也最多拖类分几个点。
WEIGHTS = {"CRITICAL": 3.0, "WARN": 1.0, "INFO": 0.25}
SEV_LEVEL = {"CRITICAL": 3, "WARN": 2, "INFO": 1}  # impact 严重度数值映射[推断,Ryte 只说 priority²×占比]
SEV_ORDER = {"CRITICAL": 0, "WARN": 1, "INFO": 2}
SEVS = ("CRITICAL", "WARN", "INFO")

# Lumar 六大类树【官方类别结构】;子组为本套件对 site_audit 数据源的映射裁剪
TREE = {
    "availability": ["server_errors"],
    "indexability": ["non_indexable", "canonicalization", "mobile_indexability"],
    # duplicate_description 已删(B37):site_audit --json 的 meta 只有 desc_len,没有描述原文,无从判重
    "uniqueness": ["duplicate_title", "duplicate_body"],
    "discoverability": ["crawl_budget", "internal_linking", "redirection",
                        "sitemaps", "internationalization"],
    "rankability": ["page_content", "structured_data", "social_tags"],
    "experience": ["page_speed", "security", "external_links"],
}

# 映射表(模块级常量):site_audit 的 area(=rule id)→(类, 子组, 默认严重度, 说明)。
# 默认严重度 = 该 area 能触发的最高档(0 命中时按此计类权重);实际计分取
# "配置降级 > 批内最高触发档 > 默认档"。说明列注明个别归组的裁量:
#   staging/ai-bots → non_indexable(环境泄漏与 bot 屏蔽都是"不可索引"控制问题);
#   llms.txt → sitemaps(AI 发现层,归站点级发现文件组);
#   a11y(html 无 lang)→ internationalization(lang 是 i18n 基础标记);
#   images(alt)→ page_content(替代文本属内容质量)。
# 未出现在表中的子组(mobile_indexability/duplicate_body/
# crawl_budget/redirection/page_speed/security/external_links)= site_audit 无该数据源
# → N/A(data_source_missing)。
MAPPING = {
    "fetch":           ("availability", "server_errors", "CRITICAL", "抓取失败(HTTP 错误/网络异常)"),
    "injection":       ("indexability", "non_indexable", "CRITICAL", "隐藏元素或注释里对 AI 下指令(Google 隐藏文字政策)"),
    "staging":         ("indexability", "non_indexable", "CRITICAL", "staging 子域公开可访问"),
    "robots":          ("indexability", "non_indexable", "CRITICAL", "noindex/nosnippet/robots.txt 不可达"),
    "ai-bots":         ("indexability", "non_indexable", "CRITICAL", "AI 检索 bot 被 robots 禁"),
    "canonical":       ("indexability", "canonicalization", "CRITICAL", "canonical 缺失/相对 URL/指向外域"),
    "title":           ("rankability", "page_content", "CRITICAL", "title 缺失/过短/过长"),
    "description":     ("rankability", "page_content", "CRITICAL", "description 缺失/过短/过长"),
    "h1":              ("rankability", "page_content", "CRITICAL", "H1 缺失/多个"),
    "headings":        ("rankability", "page_content", "WARN", "标题层级跳级"),
    "content":         ("rankability", "page_content", "WARN", "词数<200(soft-thin)"),
    "images":          ("rankability", "page_content", "WARN", "alt 缺失>20%"),
    "schema":          ("rankability", "structured_data", "WARN", "无 JSON-LD"),
    "og":              ("rankability", "social_tags", "WARN", "og 标签缺失/og:image 非绝对 URL"),
    "links":           ("discoverability", "internal_linking", "WARN", "页内链接>100"),
    "sitemap":         ("discoverability", "sitemaps", "INFO", "/sitemap.xml 不可达"),
    "llms.txt":        ("discoverability", "sitemaps", "INFO", "/llms.txt 不可达(AI 发现层,归站点发现文件组)"),
    "a11y":            ("discoverability", "internationalization", "WARN", "html 无 lang(i18n 基础标记)"),
    # S3 扩展(2026-10-10 site_audit 新增检查,均归 page_content——内容对爬虫/AI 的
    # 可解析性与可引用性;Lumar 无对应官方子组,此归组为我们的裁量)
    "rendering":       ("rankability", "page_content", "WARN", "CSR 疑似/JS 重量/noscript 缺失/服务端内容弱"),
    "semantic-html":   ("rankability", "page_content", "INFO", "语义标签比值<10%"),
    "bluf":            ("rankability", "page_content", "INFO", "BLUF 密度不足(答案未前置)"),
    "freshness":       ("rankability", "page_content", "INFO", "Last-Modified>183 天"),
    # 派生规则(非 site_audit area):批内 meta.title 相同的 URL≥2 → 各记一次命中
    "duplicate_title": ("uniqueness", "duplicate_title", "WARN", "批内 title 重复(≥2 URL 同 title)"),
}

USAGE = """usage: health_score.py --input audit.json [--ignore r1,r2] [--severity rule=sev]
                       [--config rules.json] [--json]
site_audit.py --json 输出 → 三家口径健康分:
  主分(Ahrefs 官方): (无 CRITICAL 的 URL 数÷内链 URL 总数)×100,WARN/INFO 不扣主分
    只单列子分;分档 Weak 0-30/Fair 31-70/Good 71-90/Excellent 91-100;
    fetch guard 拒审(verdict=refused/SKIP)的 URL 不进分母,单列 refused。
  类别树(Lumar 官方): 六大类每类 100 起步仅负号检查扣分,扣分=(命中URL数÷总URL数)×权重
    (权重自定 CRITICAL=3/WARN=1/INFO=0.25,官方映射未公开);合成分=Σ(类分×类权重)÷Σ类权重,
    类权重=类内负号检查权重和;无数据源的类输出 N/A(data_source_missing)不计入合成分。
  impact(Ryte 官方): impact=命中占比×严重度²(数值映射自定);>0 降序"立即处理",
    =0 标"opportunity 值得探索"。
选项:
  --input audit.json   site_audit.py --json 的输出文件(必填;容忍文件前部的逐 URL 文本行)
  --ignore r1,r2       规则 id=site_audit area 或 duplicate_title;忽略=不进 findings 不进分,
                       报告列 ignored(Ahrefs 官方语义)
  --severity rule=sev  降级(critical|warn|info,如 robots=warn);降级后自动退出主分扣分项
  --config rules.json  持久化配置 {"rules":{"<id>":{"enabled":bool,"severity":"..."}}},
                       enabled:false=忽略;CLI --ignore/--severity 优先于配置
  --json               结构化输出:{schema_version,main_score,band,category_scores{},
                       warn_score,info_score,impacts[],ignored[],coverage_note}
                       (附加:composite_score/urls_total/urls_clean/urls_refused/unmapped——
                       unmapped=site_audit 新增而 MAPPING 未跟进的 area,计主分子分不计类别分)
可用规则 id: %s
coverage: 分数基于样本,不可与全站直接比较(Ryte 官方口径)。
退出码: 0 正常 / 1 主分档 Weak / 2 输入或参数错误。""" % ", ".join(MAPPING)


def band_of(score):
    """分档映射【Ahrefs 官方】;按四舍五入后的分数取档(30.4→30→Weak,70.6→71→Good)。"""
    score = round(score)   # 先取整再分档:未取整时 70.6<71 会误落 Fair(R5)
    for name, floor in BANDS:
        if score >= floor:
            return name
    return "Weak"


def split_scored_refused(results):
    """拆分可评分/拒审 URL:fetch guard 拒审(verdict=refused 或含 SKIP)不进分母
    【site_audit 官方语义:拒审≠失败】。main 在 compute 前用它拦截空样本(除零)。"""
    scored, refused = [], []
    for url, r in results.items():
        if r.get("verdict") == "refused" or any(
                f.get("severity") == "SKIP" for f in r.get("findings", [])):
            refused.append(url)
        else:
            scored.append(url)
    return scored, refused


def norm_sev(s):
    return str(s).strip().upper()


def load_audit(path):
    """读 site_audit --json 输出;--json 模式下文件前部混有逐 URL 文本行(meta: {...}
    行本身可解析),故从每个 '{' 起点试解并取**含 results 字典**的候选(末位优先);
    无候选则退出码 2。"""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        die("读不了输入文件: %s" % e)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
        for i, ch in enumerate(text):
            if ch != "{":
                continue
            try:
                cand = json.loads(text[i:])
            except json.JSONDecodeError:
                continue
            if isinstance(cand.get("results"), dict):
                data = cand   # 不 break:末位的完整 blob 赢过早位的 meta 行片段
    if not isinstance(data, dict) or not isinstance(data.get("results"), dict):
        die("无法从 %s 解析出含 results 的 JSON(应为 site_audit.py --json 的输出)" % path)
    return data


def parse_sev_spec(spec):
    """'rule=warn' → (rule, 'WARN');规则/严重度未知则退出码 2。"""
    rule, _, sev = spec.partition("=")
    rule, sev = rule.strip(), norm_sev(sev)
    if not rule or rule not in MAPPING:
        die("未知规则 %r;可用: %s" % (rule, ", ".join(MAPPING)))
    if sev not in SEVS:
        die("未知严重度 %r;可用: critical|warn|info" % sev)
    return rule, sev


def compute(audit, ignored, sev_overrides):
    """全部口径在此汇算;ignored/sev_overrides 已归一(CLI 优先于 --config)。"""
    results = audit["results"]
    # 拆分:fetch guard 拒审(verdict=refused 或含 SKIP)不进分母【site_audit 官方语义:
    # 拒审≠失败】;其余为可评分 URL(假定样本均为内链 URL——site_audit 不做内外链分类)。
    scored, refused = split_scored_refused(results)
    total = len(scored)
    # findings 三元组 (url, rule, 有效严重度):丢 SKIP、丢 ignored、套降级
    findings = []
    for url in scored:
        for f in results[url].get("findings", []):
            sev, area = f.get("severity"), f.get("area")
            if sev not in SEVS or area in ignored:
                continue
            findings.append((url, area, sev_overrides.get(area, sev)))
    # 派生 duplicate_title:批内非空 title 相同的 URL≥2,各记一次命中(可被降级/忽略)
    titles = {}
    for url in scored:
        t = (results[url].get("meta") or {}).get("title")
        if t:
            titles.setdefault(t, []).append(url)
    has_title_data = sum(len(us) for us in titles.values()) >= 2  # ≥2 个带 title 的 URL 才可判重
    if has_title_data and "duplicate_title" not in ignored:
        for t, us in titles.items():
            if len(us) >= 2:
                for u in us:
                    findings.append((u, "duplicate_title",
                                     sev_overrides.get("duplicate_title", "WARN")))
    # 逐规则聚合命中 URL 集与触发过的严重度档
    hits = {r: set() for r in MAPPING}
    sevs = {}
    for url, rule, sev in findings:
        hits.setdefault(rule, set()).add(url)
        sevs.setdefault(rule, set()).add(sev)
    active = []  # 数据源在场的规则(计入类权重;duplicate_title 需批内≥2 个 title)
    for rule in MAPPING:
        if rule in ignored:
            continue
        if rule == "duplicate_title" and not has_title_data:
            continue
        if rule == "injection" and not hits.get(rule):   # 0.40 新增:只在命中时计入,没命中不改既有类权重(冻结口径)
            continue
        active.append(rule)

    def eff_sev(rule):
        """有效严重度:配置降级 > 批内最高触发档 > MAPPING 默认档。"""
        if rule in sev_overrides:
            return sev_overrides[rule]
        if sevs.get(rule):
            return min(sevs[rule], key=lambda s: SEV_ORDER[s])
        return MAPPING[rule][2]

    # 类分与类权重【Lumar 官方:100 起步/仅负号扣/类权重=类内负号检查权重和】;
    # 无数据源的类 → score:null + reason:data_source_missing,不进合成分。
    cat_scores, cat_exact = {}, {}
    for cat in TREE:
        rules = [r for r in active if MAPPING[r][0] == cat]
        if not rules:
            cat_scores[cat] = {"score": None, "reason": NA_REASON, "weight": 0.0}
            continue
        wsum = ded = 0.0
        for r in rules:
            w = WEIGHTS[eff_sev(r)]
            wsum += w
            ded += len(hits.get(r, ())) / total * w
        cat_scores[cat] = {"score": round(max(0.0, 100 - ded), 1), "reason": None,
                           "weight": round(wsum, 2)}
        cat_exact[cat] = (max(0.0, 100 - ded), wsum)
    composite = (round(sum(s * w for s, w in cat_exact.values()) /
                       sum(w for _, w in cat_exact.values()), 1) if cat_exact else None)

    crit_urls = {u for u, _, s in findings if s == "CRITICAL"}
    warn_urls = {u for u, _, s in findings if s == "WARN"}
    info_urls = {u for u, _, s in findings if s == "INFO"}
    main_score = round((total - len(crit_urls)) / total * 100, 1)
    # 未映射 area(site_audit 新增而 MAPPING 未跟进):计主分/子分(Ahrefs 公式按严重度,
    # 与规则无关)但不进类别树;显式列出防"分数掉了却看不到原因"。
    unmapped = {}
    for u, rule, sev in findings:
        if rule not in MAPPING:
            d = unmapped.setdefault(rule, {"severity": sev, "hit_urls": set()})
            d["severity"] = min((d["severity"], sev), key=lambda s: SEV_ORDER[s])
            d["hit_urls"].add(u)
    # impact【Ryte 官方:命中占比×严重度²;=0 → opportunity】
    impacts = []
    for r in active:
        sev = eff_sev(r)
        n = len(hits.get(r, ()))
        imp = n / total * SEV_LEVEL[sev] ** 2
        impacts.append({"rule": r, "category": MAPPING[r][0], "subgroup": MAPPING[r][1],
                        "severity": sev, "hit_urls": n, "total_urls": total,
                        "impact": round(imp, 4),
                        "action": "立即处理" if imp > 0 else "opportunity 值得探索"})
    impacts.sort(key=lambda d: (-d["impact"], d["rule"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "main_score": main_score,
        "band": band_of(main_score),
        "composite_score": composite,
        "warn_score": round((total - len(warn_urls)) / total * 100, 1),
        "info_score": round((total - len(info_urls)) / total * 100, 1),
        "category_scores": cat_scores,
        "impacts": impacts,
        "ignored": sorted(ignored),
        "unmapped": [{"area": a, "severity": d["severity"], "hit_urls": len(d["hit_urls"])}
                     for a, d in sorted(unmapped.items(),
                                        key=lambda kv: (-len(kv[1]["hit_urls"]), kv[0]))],
        "coverage_note": COVERAGE_NOTE,
        "urls_total": total,
        "urls_clean": total - len(crit_urls),
        "urls_refused": len(refused),
    }


def render(rep):
    """人读 markdown:分数卡 + 类别树 + Top impact 表 + ignored 列表。"""
    L = ["# 站点健康分(site_audit 样本 %d URL,%d 拒审未计入)" % (rep["urls_total"], rep["urls_refused"]),
         "",
         "## 分数卡",
         "- 主分(Ahrefs 口径,无 CRITICAL URL 占比×100): **%s → %s**(%d/%d URL 无 CRITICAL)"
         % (rep["main_score"], rep["band"], rep["urls_clean"], rep["urls_total"]),
         "- WARN 子分: %s / INFO 子分: %s(WARN/INFO 不扣主分,单列)" % (rep["warn_score"], rep["info_score"]),
         "- 合成分(Lumar 六类加权,类权重=类内负号检查权重和): %s" % rep["composite_score"],
         "- coverage: %s" % rep["coverage_note"],
         "",
         "## 类别树(Lumar 六大类,每类 100 起步,仅负号检查扣分)"]
    by_sub = {}
    for d in rep["impacts"]:
        by_sub.setdefault((d["category"], d["subgroup"]), []).append(d)
    for cat, subs in TREE.items():
        cs = rep["category_scores"][cat]
        if cs["score"] is None:
            L.append("%s: N/A(%s)——不计入合成分" % (cat, cs["reason"]))
            continue
        L.append("%s %s(类权重 %s)" % (cat, cs["score"], cs["weight"]))
        for i, sub in enumerate(subs):
            arm = "└─" if i == len(subs) - 1 else "├─"
            rs = by_sub.get((cat, sub))
            if not rs:
                L.append("  %s %s: N/A(%s)" % (arm, sub, NA_REASON))
            else:
                L.append("  %s %s: %s" % (arm, sub,
                         "; ".join("%s %d/%d %s" % (d["rule"], d["hit_urls"], d["total_urls"],
                                                    d["severity"]) for d in rs)))
    L += ["", "## Top impact(Ryte 口径:impact=命中占比×严重度²)",
          "立即处理(impact>0,降序):",
          "| 规则 | 类/子组 | 严重度 | 命中 | impact |", "|---|---|---|---|---|"]
    for d in rep["impacts"]:
        if d["impact"] > 0:
            L.append("| %s | %s/%s | %s | %d/%d | %s |" % (d["rule"], d["category"], d["subgroup"],
                     d["severity"], d["hit_urls"], d["total_urls"], d["impact"]))
    opp = [d for d in rep["impacts"] if d["impact"] == 0]
    if opp:
        L.append("")
        L.append("opportunity 值得探索(impact=0):")
        L += ["- %s(%s/%s %s 0/%d)" % (d["rule"], d["category"], d["subgroup"],
                                        d["severity"], d["total_urls"]) for d in opp]
    if rep["unmapped"]:
        L.append("")
        L.append("## 未映射检查(计主分/子分,不计类别分——MAPPING 待跟进)")
        L += ["- %s %s 命中 %d/%d" % (d["area"], d["severity"], d["hit_urls"], rep["urls_total"])
              for d in rep["unmapped"]]
    L.append("")
    L.append("## Ignored")
    L += ["- %s(不进 findings 不进分)" % r for r in rep["ignored"]] or ["- (无)"]
    return "\n".join(L)


def main():
    argv = sys.argv[1:]
    if any(a in ("-h", "--help") for a in argv):
        print(USAGE)
        return
    inp, ignored, sev_over, as_json, config = None, set(), {}, False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--input" and i + 1 < len(argv):
            inp = argv[i + 1]; i += 2
        elif a == "--ignore" and i + 1 < len(argv):
            for r in argv[i + 1].split(","):
                r = r.strip()
                if not r:
                    continue
                if r not in MAPPING:
                    die("未知规则 %r;可用: %s" % (r, ", ".join(MAPPING)))
                ignored.add(r)
            i += 2
        elif a == "--severity" and i + 1 < len(argv):
            rule, sev = parse_sev_spec(argv[i + 1]); sev_over[rule] = sev; i += 2
        elif a == "--config" and i + 1 < len(argv):
            config = argv[i + 1]; i += 2
        elif a == "--json":
            as_json = True; i += 1
        else:
            sys.stderr.write(USAGE + "\n"); sys.exit(2)
    if not inp:
        sys.stderr.write("缺少 --input\n" + USAGE + "\n")
        sys.exit(2)
    if config:  # 持久化配置(Ahrefs 官方格式);CLI --ignore/--severity 优先
        try:
            with open(config, encoding="utf-8") as f:
                rules = json.load(f).get("rules", {})
        except (OSError, json.JSONDecodeError) as e:
            die("读不了配置 %s: %s" % (config, e))
        for rid, cfg in rules.items():
            if rid not in MAPPING:
                die("配置含未知规则 %r;可用: %s" % (rid, ", ".join(MAPPING)))
            if cfg.get("enabled") is False:
                ignored.add(rid)
            if "severity" in cfg:
                sev = norm_sev(cfg["severity"])
                if sev not in SEVS:
                    die("配置含未知严重度 %r;可用: critical|warn|info" % cfg["severity"])
                sev_over.setdefault(rid, sev)
    # R5:空样本(全部拒审/空 results)在 compute 之前拦截——否则类别树扣分按
    # 命中数÷total 直接除零崩溃;这是输入问题,退出码 2 而非崩溃伪装成 1。
    audit = load_audit(inp)
    scored, _refused = split_scored_refused(audit["results"])
    if not scored:
        die("无可评分 URL(全部拒审或空 results)")
    rep = compute(audit, ignored, sev_over)
    if as_json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
    else:
        print(render(rep))
    sys.exit(1 if rep["band"] == "Weak" else 0)


if __name__ == "__main__":
    main()
