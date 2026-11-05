#!/usr/bin/env python3
"""信源检查器:拉取 intel-sources.md 的源→与上次状态对比→输出变更报告。
用法:
  intel_check.py init              # 首次建基线(.intel-state.json)
  intel_check.py check             # 拉全部源→diff→报告(变更源列表+受影响模块映射)
  intel_check.py check --source google-blog  # 只查指定源
输出: 变更源+变更摘要+应更新的套件文件列表(基于 source→module 映射)
hash 源二次确认: 检出变更后立即重拉一次,两次一致才算真变更;
动态页(JS渲染,如 statcounter 图表)两次不同 → 按噪音跳过,不动基线。
宽口径 RSS 源(如 OpenAI 新闻、Cloudflare 博客)带 keywords:先取最近 RSS_SCAN 条,
只保留标题或链接命中关键词的条目再比较;新条目都不相关 → 不算变更。
退出码: 0=无变更 / 1=有变更(触发更新流程) / 2=错误"""
import sys, os, json, re, hashlib, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = "Mozilla/5.0 (compatible; seo-suite-intel/1.0)"
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", ".intel-state.json")

# 源注册表:与 references/overview/intel-sources.md 同步维护
SOURCES = {
    "google-blog": {"url": "https://developers.google.com/search/blog/feed.xml", "type": "rss",
        "modules": ["content/geo-evidence.md", "technical/validation-guide.md", "content/llms-txt-guide.md"]},
    "google-updates": {"url": "https://developers.google.com/search/updates", "type": "hash",
        "modules": ["technical/validation-guide.md", "technical/audit-rule-catalog.md"]},
    "gsc-announce": {"url": "https://developers.google.com/search/blog/feed.xml", "type": "rss",
        "modules": ["overview/intake-checklists.md", "monitoring/kpi-definitions.md"]},
    "status-dashboard": {"url": "https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history", "type": "hash",
        "modules": ["monitoring/seo-drift-monitoring.md"]},
    "lighthouse": {"url": "https://github.com/googlechrome/lighthouse/releases.atom", "type": "rss",
        "modules": ["technical/agent-readiness.md", "technical/agent-protocols.md"]},
    "bing-wm": {"url": "https://blogs.bing.com/webmaster/feed", "type": "rss",
        "modules": ["content/geo-platform-differences.md"]},
    "openai-bots": {"url": "https://developers.openai.com/api/docs/bots", "type": "hash",
        "modules": ["technical/ai-crawler-policy.md"]},
    "ard-spec": {"url": "https://github.com/ards-project/ard-spec/commits/main.atom", "type": "rss",
        "modules": ["technical/agent-protocols.md", "technical/agent-readiness.md"]},
    "anthropic-crawl": {"url": "https://privacy.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler", "type": "hash",
        "modules": ["technical/ai-crawler-policy.md"]},
    "schema-org": {"url": "https://schema.org/docs/releases.html", "type": "hash",
        "modules": ["technical/schema-templates.md", "technical/schema-examples.md"]},
    "crux": {"url": "https://developer.chrome.com/docs/crux/release-notes/", "type": "hash",
        "modules": ["technical/cwv-playbook.md"]},
    "yandex-wm": {"url": "https://yandex.com/support/webmaster/ru/new-features", "type": "hash",
        "modules": ["markets/ru.md"]},
    "naver-wm": {"url": "https://searchadvisor.naver.com/", "type": "hash",
        "modules": ["markets/ko.md", "technical/naver-searchadvisor.md"]},
    "baidu-ziyuan": {"url": "https://ziyuan.baidu.com/", "type": "hash",
        "modules": ["markets/zh.md", "content/chinese-ai-search-guide.md"]},
    "statcounter-search": {"url": "https://gs.statcounter.com/search-engine-market-share", "type": "hash",
        "modules": ["overview/multilingual-workflow.md"]},
    "statcounter-ai": {"url": "https://gs.statcounter.com/ai-chatbot-market-share", "type": "hash",
        "modules": ["content/geo-platform-differences.md"]},
    "semrush-sensor": {"url": "https://www.semrush.com/sensor/", "type": "hash",
        "modules": ["monitoring/seo-drift-monitoring.md"]},
    "google-docs-rss": {"url": "https://developers.google.com/search/updates/search_docs_updates.rss", "type": "rss",
        "modules": ["technical/validation-guide.md", "technical/audit-rule-catalog.md"]},
    "openai-bots-rss": {"url": "https://developers.openai.com/api/docs/bots/rss.xml", "type": "rss",
        "modules": ["technical/ai-crawler-policy.md"]},
    "seroundtable": {"url": "https://www.seroundtable.com/index.xml", "type": "rss",
        "modules": ["monitoring/penalty-recovery.md", "technical/rendering-seo.md"]},
    # 2026-11-05 扩源(RQ-229):12 条漏报知识的回放,见 intel-sources.md 第五节
    "chrome-blog": {"url": "https://developer.chrome.com/static/blog/feed.xml", "type": "rss",
        "modules": ["technical/cwv-playbook.md", "technical/agent-readiness.md",
                    "technical/agent-protocols.md", "monitoring/agent-growth-loop.md"]},
    "web-dev-blog": {"url": "https://web.dev/static/blog/feed.xml", "type": "rss",
        "modules": ["technical/cwv-playbook.md", "technical/rendering-seo.md"]},
    "cloudflare-blog": {"url": "https://blog.cloudflare.com/rss/", "type": "rss",
        "keywords": r"\bai\b|crawl|\bbots?\b|robots|agent|content signal|pay per|training|publisher|llms|markdown|grounding",
        "modules": ["technical/ai-crawler-policy.md", "technical/agent-protocols.md"]},
    "openai-news": {"url": "https://openai.com/news/rss.xml", "type": "rss",
        "keywords": r"crawl|\bbots?\b|robots|training pref|publisher|website|\bsearch\b|atlas|browser|shopping|checkout|commerce|merchant|\bads?\b|advertis",
        "modules": ["technical/ai-crawler-policy.md", "content/geo-platform-differences.md",
                    "content/ecommerce-geo-ladder.md", "overview/intel-sources.md"]},
    "bing-search-blog": {"url": "https://blogs.bing.com/search/feed", "type": "rss",
        "modules": ["technical/ai-crawler-policy.md", "content/geo-platform-differences.md",
                    "content/ecommerce-geo-ladder.md"]},
    "msads-blog": {"url": "https://about.ads.microsoft.com/en/blog/rss", "type": "rss",
        "keywords": r"copilot|checkout|agent|merchant|shopping|commerce|publisher|content|grounding|\bai\b|clarity|bing",
        "modules": ["content/ecommerce-geo-ladder.md", "technical/agent-protocols.md"]},
    "google-maps-blog": {"url": "https://blog.google/products/maps/rss/", "type": "rss",
        "keywords": r"ask maps|gemini|\bai\b|business|local|review|merchant|places",
        "modules": ["monitoring/local-grid-ranking.md", "overview/site-type-playbooks.md"]},
    "google-shopping-blog": {"url": "https://blog.google/products/shopping/rss/", "type": "rss",
        "keywords": r"agent|checkout|commerce|\bai\b|merchant|protocol|\bucp\b|ap2|cart|retailer",
        "modules": ["content/ecommerce-geo-ladder.md"]},
    "arxiv-geo": {"url": "https://export.arxiv.org/api/query?search_query=all:%22generative%20engine%20optimization%22&sortBy=submittedDate&sortOrder=descending&max_results=20",
        "type": "rss",
        "modules": ["content/geo-evidence-bank.md", "content/citability-scoring.md"]},
}

RSS_SCAN = 50  # 带 keywords 的源先看这么多条再过滤

_body_cache = {}

def fetch(url, timeout=20, cache=True):
    # 同一轮里同 URL 只拉一次(google-blog/gsc-announce 共用一个 feed);
    # 二次确认场景传 cache=False 强制真拉
    if cache and url in _body_cache:
        return _body_cache[url]
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read(2_000_000).decode("utf-8", "replace")
    _body_cache[url] = body
    return body

def get_rss_items(xml_text, limit=5):
    """提取 RSS/Atom 最近 N 条: (title, link, date)"""
    items = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom", "rss": "http://purl.org/rss/1.0/"}
        # RSS 2.0
        for item in root.iter("item"):
            t = (item.findtext("title") or "").strip()
            l = (item.findtext("link") or "").strip()
            d = (item.findtext("pubDate") or "").strip()
            items.append((t, l, d))
        # Atom
        if not items:
            for e in root.iter("{http://www.w3.org/2005/Atom}entry"):
                t = (e.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
                le = e.find("{http://www.w3.org/2005/Atom}link")
                l = ((le.text or le.get("href") or "") if le is not None else "").strip()
                d = (e.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
                items.append((t, l, d))
    except ET.ParseError:
        pass
    return items[:limit]

def source_items(cfg, body):
    """返回 (原始条目, 相关条目)。没有 keywords 的源两者相同(最近 5 条);
    有 keywords 的源先取 RSS_SCAN 条,标题或链接命中才算相关,最多 5 条。"""
    kw = cfg.get("keywords")
    raw = get_rss_items(body, limit=RSS_SCAN if kw else 5)
    if not kw:
        return raw, raw
    rx = re.compile(kw, re.I)
    return raw, [it for it in raw if rx.search(f"{it[0]} {it[1]}")][:5]

def content_hash(text):
    # 去时间戳/nonce/随机段 + HTML canonical 化(属性排序/去 script·style·注释)后哈希,减假阳性
    text = re.sub(r"\d{4}-\d{2}-\d{2}T[\d:.+Z-]+", "", text)
    text = re.sub(r"""csrf[\w-]*|nonce(-[\w/=+]+|\s*=\s*("[^"]*"|[\w/=+-]+))?|_token|cache[-_]?bust\w*""", "", text, flags=re.I)
    return hashlib.sha256(canonicalize(text).encode()).hexdigest()[:32]

def canonicalize(text):
    """HTML canonical 化(防 hash 误报):
    1) 删 script/style/注释;2) 标签名小写、属性名排序去重、挥发性属性值遮蔽
       (nonce/integrity/随机 token 形态的值只留属性名);3) 标签多重集排序(元素顺序
       洗牌不触发假变更)+ 可见文本压空白。
    CDN 属性顺序漂移/内联脚本轮换/每请求随机 id/等价 link 元素重排不再触发假变更;
    真实内容变更(文本变/新增链接或元素)仍改变哈希。非 HTML 内容原样返回。"""
    if not re.search(r"<(script|style|!|html|body|div|meta|a\b|head)", text, re.I):
        return text
    text = re.sub(r"(?is)<script\b[^>]*>.*?</script>", " ", text)
    text = re.sub(r"(?is)<script\b[^>]*>", " ", text)          # 未闭合残段
    text = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    VOLATILE_ATTRS = {"nonce", "integrity", "csrf"}
    RAND_TOKEN = re.compile(r"[A-Za-z0-9_-]{16,}")          # 每请求轮换的随机 token
    COUNTER_ID = re.compile(r"[A-Za-z0-9_-]*\d{4,}[A-Za-z0-9_-]*")  # 会话计数器 id(dc-86127/input-186042212)
    ATTR_RE = re.compile(r"""([^\s=/>]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?""")
    def _clean_attr(name, val):
        n = name.lower()
        if not val:
            return n
        v = val.strip("\"'")
        if n in ("href", "src"):
            v = re.sub(r"#.*", "", v)  # 去锚点/混淆哈希(cdn-cgi/l/email-protection#…)
        if n in VOLATILE_ATTRS or RAND_TOKEN.fullmatch(v) or COUNTER_ID.fullmatch(v):
            return n  # 挥发性属性/随机 token/会话计数器值只留属性名
        return n + "=" + v
    def _norm_tag(m):
        name = m.group(1).lower()
        attrs = sorted(set(_clean_attr(n, v) for n, v in ATTR_RE.findall(m.group(2) or "")), key=str.lower)
        return "<%s %s>" % (name, " ".join(attrs)) if attrs else "<%s>" % name
    text = re.sub(r"(?is)<([a-zA-Z][a-zA-Z0-9:-]*)((?:\s+[^\s=>]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?)*)\s*/?>",
                  _norm_tag, text)
    tags = sorted(re.findall(r"<[a-zA-Z][^>]*>", text))
    visible = re.sub(r"<[^>]+>", " ", text)
    return "TAGS: " + " ".join(tags) + " TEXT: " + re.sub(r"\s+", " ", visible).strip()

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {"checked_at": None, "sources": {}}

def save_state(state):
    state["checked_at"] = datetime.now(timezone.utc).isoformat()
    json.dump(state, open(STATE_FILE, "w"), indent=1)

def check_source(name, cfg, prev):
    """返回 (changed:bool, detail:str, new_state)。new_state 用本次同一 body 建,
    不二次 fetch——两次 check 之间页面微抖不再让基线与对比体错位。"""
    try:
        body = fetch(cfg["url"])
    except Exception as e:
        return False, f"fetch_error: {type(e).__name__}", None
    h = content_hash(body)
    now = datetime.now(timezone.utc).isoformat()
    if cfg["type"] == "hash":
        if prev and prev.get("hash") == h:
            if prev.get("unstable_streak"):
                return False, "", {**prev, "unstable_streak": 0, "ts": now}
            return False, "", None
        # 与基线不同 → 立即二次拉取确认:两次一致才是真变更(动态页每次渲染
        # 都在抖,如 statcounter 的 JS 图表页),两次不一致按噪音跳过且不动基线
        try:
            h2 = content_hash(fetch(cfg["url"], cache=False))
        except Exception:
            h2 = h  # 二次拉取失败时退回单次结果
        if h2 != h:
            streak = (prev or {}).get("unstable_streak", 0) + 1
            note = "连续抖动,疑似JS渲染/动态页,按P3处理,偶尔人工复核即可" if streak >= 3 else "页面抖动,本次跳过"
            return False, f"unstable(连续{streak}次): {note}", {**(prev or {}), "unstable_streak": streak, "ts": now}
        return (prev is not None), f"hash:{h[:12]}", {"hash": h, "ts": now}
    # rss
    raw, items = source_items(cfg, body)
    if raw and not items:
        return False, "", None  # 有条目,但都和本套件无关(keywords 过滤后为空)
    if not items:
        # fallback: hash comparison if rss parsing failed
        if prev and prev.get("hash") == h:
            return False, "", None
        return (prev is not None and "top" not in (prev or {})), f"hash:{h[:12]}", {"hash": h, "ts": now}
    top = items[0][0]
    if prev and prev.get("top") == top:
        return False, "", None
    old_seen = (prev or {}).get("seen", [])
    seen = old_seen + [t for t, _, _ in items if t not in old_seen]
    new_items = [t for t, _, _ in items if not (prev and t in old_seen)]
    detail = " | ".join(t[:60] for t in new_items[:3]) or f"top: {top[:60]}"
    return True, detail, {"top": top, "seen": seen[-50:], "ts": now}

def usage():
    print(__doc__.strip())

def main():
    argv = sys.argv[1:]
    if any(a in ("-h", "--help") for a in argv):
        usage()
        return
    args = [a for a in argv if not a.startswith("--")]
    only = None
    if "--source" in argv:
        only = argv[argv.index("--source") + 1]
    state = load_state()
    if args and args[0] == "init":
        sources = state["sources"]
        for name, cfg in SOURCES.items():
            if only and name != only: continue
            try:
                body = fetch(cfg["url"])
                if cfg["type"] == "rss":
                    items = source_items(cfg, body)[1]
                    sources[name] = {"top": items[0][0] if items else content_hash(body),
                                     "seen": [t for t, _, _ in items], "ts": datetime.now(timezone.utc).isoformat()}
                else:
                    sources[name] = {"hash": content_hash(body), "ts": datetime.now(timezone.utc).isoformat()}
                print(f"  init {name}: ok")
            except Exception as e:
                print(f"  init {name}: {type(e).__name__} (skip)")
        save_state(state)
        print("基线已建;下次 check 检测变更")
        return
    if args and args[0] != "check":
        usage()
        sys.exit(2)
    # check mode
    changed_sources = []
    errors = []
    for name, cfg in SOURCES.items():
        if only and name != only: continue
        prev = state["sources"].get(name)
        try:
            ch, detail, new_state = check_source(name, cfg, prev)
            if ch:
                changed_sources.append((name, detail, cfg["modules"]))
            if new_state:
                state["sources"][name] = new_state
            if detail.startswith("fetch_error") or detail.startswith("unstable"):
                errors.append((name, detail))
        except Exception as e:
            errors.append((name, str(e)))
    save_state(state)
    if changed_sources:
        print(f"=== {len(changed_sources)} 个信源变更 ===")
        affected = set()
        for name, detail, mods in changed_sources:
            print(f"[CHANGED] {name}: {detail}")
            for m in mods:
                affected.add(m)
                print(f"  → 应更新: references/{m}")
        print(f"\n受影响文件共 {len(affected)} 个")
        print("\n下一步: 按 self-update-protocol.md 逐个更新 → self_check → commit")
        sys.exit(1)
    else:
        print(f"无变更(已查 {len([n for n in SOURCES if not only or n == only])} 源;{len(errors)} 错误/抖动)")
        for n, e in errors[:5]: print(f"  skip {n}: {e}")
        sys.exit(0)

if __name__ == "__main__": main()
