#!/usr/bin/env python3
"""link_intel.py — 竞品与外链发现(上下游种子站、谁链谁、互换外链、外联候选、竞品 SEO 底账)。stdlib only。

没有 Ahrefs / Semrush 也能跑:入链用 Common Crawl 的域名级链接图(每季度一版,公开免费),页面级证据靠自己抓。
流程和判据见 references/research/link-intelligence.md。

子命令:
  listicles  --input listicles.json|urls.txt [--min 2] [--out seeds.json]
             抓榜单/对比文章,数每个外链域出现在几篇里 → 种子站(≥min 篇)。榜单文章本身也是「求收录」外联对象。
  ccgraph    --targets seeds.txt [--own example.com] [--release cc-main-2026-jul-aug-sep|latest] [--ranks] --out graph.json
             流式读 Common Crawl 域名级链接图(顶点约 1GB、边约 8GB 压缩,不落盘),取出每个目标域的入链域,
             以及目标域之间的互链。要 gzip、grep(-E -f)、awk 在 PATH 上;下载断了按 Range 断点续传。
  crawl      --sites sites.txt [--own example.com] [--max-pages 30] --out crawl.json
             抓每个站的首页、合作/集成/友链/资源类页面和 sitemap 里同类页,记下页面上的外链(含 rel、锚文本)。
             页面级互链(A 的某页链 B、B 的某页链 A)= 疑似互换,两边页面都给出来。
  intersect  --graph graph.json [--crawl crawl.json] [--own example.com] [--min 2] [--ledger contacted.csv] --out cand.csv
             外联候选:链到 ≥min 个种子站、没链我们的域;互换关系表。--ledger 是已联系过的 CSV(要有 domain 列),命中的标出来。
  exchangers --crawl crawl.json [--crawl hop2.json] [--own example.com] [--ledger contacted.csv] [--min-listed 3] --out pool.csv
             互换池:在做互换的站(有合作 / 友链 / 集成页)和这些页上列出的外站,按被几家列出排序。只看「会不会换」,不看主题。
  deadlinks  --input 资源页或榜单页 [--own example.com]
             失效链接替换的候选:页上指向别站、现在 404/410/连不上的链接(死链 + 所在页 + 锚文本)。
  unlinked   --input 搜品牌名得到的网址 --own example.com --brand '正则'
             提到我们却没链我们的页(平台站不算),附上下文,用来请对方补链。
  footprint  --serp serp.json [--competitors a.com,b.com] [--own example.com] [--top 8]
             竞品 SEO 底账:每家排在哪些词上、靠哪类页面(对比页、博客、文档、免费工具、平台落地页…)拿到排名,
             我们缺位的词按赢家页面类型归组 → 该复制什么。

所有子命令 --json 输出机器可读结果到 stdout;--out 写文件。网络抓取:仅 http(s),拒私网(同 site_crawl.py)。
"""
import argparse
import csv
import gzip
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import site_crawl as SC  # noqa: E402

CC_BASE = "https://data.commoncrawl.org/projects/hyperlinkgraph"
# data.commoncrawl.org 限流时(新连接回 503、老连接降到几百 KB/s)换它背后的 CloudFront 地址;2026-11-06 实测后者 4MB/s+。
CC_MIRRORS = ("https://data.commoncrawl.org/", "https://ds5q9oxwqwsfj.cloudfront.net/")
CC_INDEX = "https://commoncrawl.org/web-graphs"
UA = "Mozilla/5.0 (compatible; seo-suite-linkintel/1.0)"

# 到处都链、不算「上下游」的平台域。种子里剔掉;候选里不剔,单列 platform=1。
PLATFORMS = {
    "google.com", "youtube.com", "youtu.be", "facebook.com", "twitter.com", "x.com", "linkedin.com",
    "instagram.com", "tiktok.com", "reddit.com", "github.com", "githubusercontent.com", "medium.com",
    "wikipedia.org", "wikimedia.org", "apple.com", "microsoft.com", "amazon.com", "amazonaws.com",
    "cloudflare.com", "w3.org", "schema.org", "wordpress.org", "wordpress.com", "wp.com", "t.me",
    "telegram.org", "discord.gg", "discord.com", "pinterest.com", "quora.com", "bit.ly", "gstatic.com",
    "googleapis.com", "googletagmanager.com", "google-analytics.com", "doubleclick.net", "gravatar.com",
    "trustpilot.com", "g2.com", "capterra.com", "producthunt.com", "stackoverflow.com", "whatsapp.com",
    "mozilla.org", "creativecommons.org", "gmpg.org", "baidu.com", "weibo.com", "zhihu.com", "bilibili.com",
    "qq.com", "weixin.qq.com", "csdn.net", "jsdelivr.net", "unpkg.com", "cloudfront.net", "vimeo.com",
    "substack.com", "npmjs.com", "pypi.org", "docker.com", "openai.com", "anthropic.com", "yandex.ru",
    "bing.com", "duckduckgo.com", "archive.org", "shopify.com", "hubspot.com", "mailchimp.com", "calendly.com",
    # 文章页「用 AI 总结 / 分享」按钮、聊天链接、状态页、备案号
    "perplexity.ai", "claude.ai", "chatgpt.com", "grok.com", "gemini.google.com", "wa.me", "telegram.me",
    "github.blog", "github.community", "githubstatus.com", "githubuniverse.com", "github.io", "statuspage.io",
    "ycombinator.com", "miit.gov.cn", "beian.gov.cn", "mps.gov.cn", "linktr.ee", "threads.net", "threads.com",
    "disqus.com", "ico.org.uk", "addtoany.com", "sharethis.com", "feedly.com", "flipboard.com", "tumblr.com", "vk.com", "line.me",
    # 正文里的引用和自家按钮:论文、法规、标准、开源库文档、预约 / 表单组件、通用 SaaS
    "arxiv.org", "europa.eu", "ietf.org", "rfc-editor.org", "iso.org", "nist.gov", "crummy.com", "python.org",
    "nodejs.org", "playwright.dev", "pptr.dev", "selenium.dev", "developer.mozilla.org", "cal.com", "hsforms.com",
    "hsforms.net", "typeform.com", "tally.so", "figma.com", "notion.so", "notion.com", "slack.com", "linear.app",
    "claude.com", "huggingface.co", "modelcontextprotocol.io", "stripe.com", "vercel.com", "netlify.com",
}


def is_platform(domain):
    return domain in PLATFORMS or ".gov." in "." + domain + "." or domain.endswith((".gov", ".edu"))

# 当品牌词用会撞上普通路径的词(proxies.sx 的 "proxies" 会命中所有代理站的 /proxies/)。
GENERIC_TOKENS = {"proxies", "proxy", "scraper", "scraping", "browser", "captcha", "search", "partners", "data",
                  "cloud", "tools", "agent", "agents", "crawl", "crawler", "api", "apis", "solver", "residential"}

# 合作/互换类页面:路径里出现这些词。
PARTNER_PATH = re.compile(
    r"/(partners?|partnerships?|integrations?|friends?|links?|resources?|affiliates?|ecosystem|"
    r"marketplace|alliances?|technology-partners|tools|recommended|友情链接|合作伙伴|合作)(/|$|-|\.html)", re.I)


def registrable(host_or_url):
    h = host_or_url or ""
    if "://" in h:
        try:
            h = urllib.parse.urlsplit(h).hostname or ""
        except ValueError:      # 页面里写坏的网址,例如 http://[::1 没闭合
            return ""
    h = h.split("/")[0].split(":")[0].lower().strip(".")
    if h.startswith("www."):
        h = h[4:]
    return SC.registrable(h)


def _ere(domain):
    """域名 → grep -E 字面量(域名里只有字母数字、点、连字符)。"""
    return domain.replace(".", "\\.")


def rev(domain):
    return ".".join(reversed(domain.split(".")))


def write_out(path, obj):
    if not path:
        return
    tmp = path + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


# ---------------------------------------------------------------------------
# 页面抓取与外链抽取
# ---------------------------------------------------------------------------

class LinkParser(HTMLParser):
    """<a href rel>文本</a> + <meta name=robots>。
    chrome=True:链接在 nav / header / footer / aside 里(导航、页脚、侧栏),不是正文推荐。"""

    CHROME_TAGS = {"nav", "header", "footer", "aside"}
    CHROME_ROLES = {"navigation", "banner", "contentinfo", "complementary"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self._cur, self.meta_robots = [], None, ""
        self._chrome = []           # 打开的导航 / 页脚类元素

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.CHROME_TAGS or (a.get("role") or "").lower() in self.CHROME_ROLES:
            self._chrome.append(tag)
        if tag == "a" and a.get("href"):
            self._cur = {"href": a["href"], "rel": (a.get("rel") or "").lower().split(), "text": "",
                         "chrome": bool(self._chrome)}
            self.links.append(self._cur)
        elif tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.meta_robots = (a.get("content") or "").lower()

    def handle_endtag(self, tag):
        if tag == "a":
            self._cur = None
        if tag in self._chrome:     # 标签没闭合的页面:关到最近一个同名的为止
            while self._chrome and self._chrome.pop() != tag:
                pass

    def handle_data(self, data):
        if self._cur is not None and len(self._cur["text"]) < 120:
            self._cur["text"] += data


def fetch(url, timeout=12.0):
    """→ (status, final_url, body);失败 → (0, url, "")。"""
    try:
        r = SC.robust_fetch(url, timeout=timeout)
        return r["status"], r["final_url"], r["body"]
    except Exception:
        return 0, url, ""


def external_links(body, base):
    """页面 → [{domain, url, rel[], anchor}](只留外站链接,同注册域的去掉)。"""
    p = LinkParser()
    try:
        p.feed(body[:800_000])
    except Exception:
        pass
    own = registrable(base)
    page_nofollow = "nofollow" in p.meta_robots
    out, seen = [], set()
    for ln in p.links:
        raw = ln["href"].strip()
        if re.search(r"\s", raw):      # 「http://1. https://…」这类把正文当链接写坏的,不算
            continue
        try:
            href = urllib.parse.urljoin(base, raw)
        except ValueError:
            continue
        if not href.startswith(("http://", "https://")):
            continue
        d = registrable(href)
        if not d or d == own or "." not in d:
            continue
        key = (d, href)
        if key in seen:
            continue
        seen.add(key)
        rel = sorted(set(ln["rel"] + (["nofollow"] if page_nofollow else [])))
        out.append({"domain": d, "url": href, "rel": rel, "anchor": " ".join(ln["text"].split())[:80],
                    "chrome": ln["chrome"]})
    return out


# ---------------------------------------------------------------------------
# listicles:榜单文章 → 种子站
# ---------------------------------------------------------------------------

def load_listicles(path):
    """listicles.json(queries[].results[] 带 is_listicle)或一行一个 URL 的文本 → [(url, category)]。"""
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        out, seen = [], set()
        for q in data.get("queries", []):
            for r in q.get("results", []):
                if r.get("is_listicle") and r.get("url") and r["url"] not in seen:
                    seen.add(r["url"])
                    out.append((r["url"], q.get("category", "")))
        return out
    return [(u, "") for u in read_lines(path)]


def aggregate_listicles(fetched, min_publishers=2):
    """按「被几家不同网站的榜单提到」计数:同一网站发的多篇只算一家,
    免得某家自己博客里一排文章页脚都链着自家各国分站,把分站顶成种子。"""
    per_domain = defaultdict(lambda: {"publishers": set(), "listicles": set(), "categories": set()})
    for f in fetched:
        pub = registrable(f["url"])
        for d in f.get("domains", []):
            if d == pub or is_platform(d) or _sibling(d, pub):
                continue
            rec = per_domain[d]
            rec["publishers"].add(pub)
            rec["listicles"].add(f["url"])
            if f.get("category"):
                rec["categories"].add(f["category"])
    publishers = {registrable(f["url"]) for f in fetched}
    seeds = []
    for d, v in per_domain.items():
        n = len(v["publishers"])
        if n >= min_publishers:
            seeds.append({"domain": d, "publisher_count": n, "listicle_count": len(v["listicles"]),
                          "categories": sorted(v["categories"]), "also_publishes_listicle": d in publishers,
                          "listicles": sorted(v["listicles"])[:20]})
    seeds.sort(key=lambda s: (-s["publisher_count"], -s["listicle_count"], s["domain"]))
    return seeds


def _sibling(a, b):
    """brightdata.de 和 brightdata.com 这类同名不同后缀的站算一家。"""
    return a.split(".")[0] == b.split(".")[0]


def cmd_listicles(ns):
    items = load_listicles(ns.input)
    fetched = []
    for url, cat in items:
        st, final, body = fetch(url)
        links = external_links(body, final) if st == 200 else []
        body_links = [ln for ln in links if not ln["chrome"]]       # 只算正文,导航和页脚不算推荐
        fetched.append({"url": url, "category": cat, "status": st,
                        "domains": sorted({ln["domain"] for ln in body_links}),
                        "nofollow": sorted({ln["domain"] for ln in body_links if "nofollow" in ln["rel"]})})
        if ns.delay:
            time.sleep(ns.delay)
    seeds = aggregate_listicles(fetched, ns.min)
    ok = sum(1 for f in fetched if f["status"] == 200 and f["domains"])
    res = {"listicles_total": len(items), "listicles_parsed": ok, "min": ns.min,
           "seeds": seeds, "fetched": fetched}
    write_out(ns.out, res)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("榜单 %d 篇,能读出外链 %d 篇;被 ≥%d 家网站的榜单提到的域 %d 个" % (len(items), ok, ns.min, len(seeds)))
        for s in seeds[:40]:
            print("  %-28s %2d 家 / %2d 篇  %s" % (s["domain"], s["publisher_count"], s["listicle_count"],
                                                 ",".join(s["categories"])))
    return 0


# ---------------------------------------------------------------------------
# ccgraph:Common Crawl 域名级链接图
# ---------------------------------------------------------------------------

def latest_release():
    req = urllib.request.Request(CC_INDEX, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    names = sorted(set(re.findall(r"cc-main-(20\d\d)-([a-z]{3})-([a-z]{3})-([a-z]{3})", html)))
    if not names:
        raise SystemExit("取不到 Common Crawl 链接图版本列表:%s" % CC_INDEX)
    months = "jan feb mar apr may jun jul aug sep oct nov dec".split()
    best = max(names, key=lambda t: (int(t[0]), months.index(t[3]) + (12 if months.index(t[3]) < months.index(t[1]) else 0)))
    return "cc-main-%s-%s-%s-%s" % best


def cc_url(release, kind):
    return "%s/%s/domain/%s-domain-%s.txt.gz" % (CC_BASE, release, release, kind)


def _feed(url, sink, tries=300, chunk=16 << 20):
    """把 url 的字节流按 16MB 一段的 Range 请求写进 sink(子进程 stdin)。
    Common Crawl 高峰时 S3 回 503 SlowDown:整条长连接几乎拿不到数据,短的分段请求一半以上能成。
    所以按段取,单段失败就换主站 / 镜像重试,连续失败 tries 次才放弃(单线程顺序取,不加并发)。"""
    got, total, fails, last = 0, None, 0, None
    alts = [url] + [url.replace(CC_MIRRORS[0], m, 1) for m in CC_MIRRORS[1:] if url.startswith(CC_MIRRORS[0])]
    while total is None or got < total:
        u = alts[fails % len(alts)]
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA, "Range": "bytes=%d-%d" % (got, got + chunk - 1)})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status != 206:
                    raise SystemExit("服务器不支持分段下载:%s" % u)
                m = re.search(r"/(\d+)$", r.headers.get("Content-Range", ""))
                total = int(m.group(1)) if m else total
                data = r.read()
            sink.write(data)
            got += len(data)
            fails = 0
            if total is None and len(data) < chunk:
                break
        except urllib.error.HTTPError as e:
            if e.code == 416:           # 已经取完
                break
            last, fails = e, fails + 1
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            if isinstance(e, BrokenPipeError):
                raise
            last, fails = e, fails + 1
        if fails:
            if fails >= tries:
                sink.close()
                raise SystemExit("下载失败(连续 %d 段失败,到 %d 字节):%s %s" % (tries, got, u, last))
            time.sleep(min(30, 1 + fails // 5))
    sink.close()
    return got


def _pipeline(url, source, tail_cmd):
    """(本地文件 | 断点续传下载) → gzip -dc → tail_cmd,返回 tail_cmd 的输出行。"""
    import threading
    env = dict(os.environ, LC_ALL="C")
    p2 = subprocess.Popen(["gzip", "-dc"], stdin=subprocess.PIPE if not source else open(source, "rb"),
                          stdout=subprocess.PIPE)
    p3 = subprocess.Popen(tail_cmd, stdin=p2.stdout, stdout=subprocess.PIPE, env=env)
    p2.stdout.close()
    err = []
    if not source:
        def run():
            try:
                _feed(url, p2.stdin)
            except BaseException as e:      # noqa: BLE001 — 线程里的异常带回主线程
                err.append(e)
                try:
                    p2.stdin.close()
                except OSError:
                    pass
        th = threading.Thread(target=run, daemon=True)
        th.start()
    out = p3.communicate()[0].decode("utf-8", "replace").splitlines()
    p2.wait()
    if not source:
        th.join()
    if err:
        raise SystemExit(str(err[0]))
    if p2.returncode not in (0, None):
        raise SystemExit("解压失败(gzip=%s):%s" % (p2.returncode, url or source))
    return out


def stream_grep(url, patterns, source=None):
    """(下载 | 本地文件) | gzip -dc | grep -E -f patterns → 命中行。source 给本地文件(测试用)时不走网络。"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pat", encoding="utf-8") as pf:
        pf.write("\n".join(patterns) + "\n")
        pat = pf.name
    try:
        return _pipeline(url, source, ["grep", "-E", "-f", pat])
    finally:
        os.unlink(pat)


def stream_join(url, keys, col, source=None):
    """(下载 | 本地文件) | gzip -dc | awk 第 col 列在 keys 里的行。键多(几十万)时比 grep 快,一遍读完。"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".keys", encoding="utf-8") as kf:
        kf.write("\n".join(keys) + "\n")
        kpath = kf.name
    try:
        return _pipeline(url, source, ["awk", "-F", "\t", "NR==FNR{k[$1];next} ($%d in k)" % col, kpath, "-"])
    finally:
        os.unlink(kpath)


def ccgraph(targets, own=None, release=None, ranks=False, local=None):
    """targets:注册域列表。local:{'vertices': path, 'edges': path, 'ranks': path}(测试用)。
    返回 {release, found, missing, inlinks{t:[src]}, outlinks{t:[dst]}, mutual[[a,b]], ranks{d:pos}}。"""
    for tool in ("gzip", "grep", "awk"):
        if not shutil.which(tool):
            raise SystemExit("缺少命令 %s" % tool)
    local = local or {}
    names = sorted({t.lower() for t in targets} | ({own.lower()} if own else set()))
    # 1) 顶点:目标域 → id
    vpat = ["\t%s\t" % _ere(rev(d)) for d in names]
    vlines = stream_grep(cc_url(release, "vertices"), vpat, local.get("vertices"))
    id_of = {}
    for ln in vlines:
        parts = ln.split("\t")
        if len(parts) >= 2:
            id_of[rev(parts[1])] = parts[0]
    name_of = {v: k for k, v in id_of.items()}
    # 2) 边:指向目标的(入链)和目标发出的(出链)
    ids = sorted(name_of)
    epat = ["\t%s$" % i for i in ids] + ["^%s\t" % i for i in ids]
    inl, outl = defaultdict(set), defaultdict(set)
    for ln in stream_grep(cc_url(release, "edges"), epat, local.get("edges")) if ids else []:
        a, _, b = ln.partition("\t")
        if b in name_of:
            inl[b].add(a)
        if a in name_of:
            outl[a].add(b)
    # 3) 顶点第二遍:入链/出链 id → 域名
    need = (set().union(*inl.values()) if inl else set()) | (set().union(*outl.values()) if outl else set())
    need -= set(name_of)
    if need:
        for ln in stream_join(cc_url(release, "vertices"), sorted(need), 1, local.get("vertices")):
            parts = ln.split("\t")
            if len(parts) >= 2:
                name_of[parts[0]] = rev(parts[1])
    inlinks = {name_of[t]: sorted(name_of.get(s, "#" + s) for s in srcs) for t, srcs in inl.items()}
    outlinks = {name_of[t]: sorted(name_of.get(s, "#" + s) for s in dsts) for t, dsts in outl.items()}
    tset = set(id_of)
    mutual = sorted({tuple(sorted((a, b))) for a in tset for b in outlinks.get(a, [])
                     if b in tset and a in outlinks.get(b, []) and a != b})
    res = {"release": release, "targets": names, "found": sorted(id_of), "missing": sorted(set(names) - set(id_of)),
           "inlinks": inlinks, "outlinks": outlinks, "mutual": [list(m) for m in mutual], "own": own}
    if ranks:
        doms = set(names) | {d for v in inlinks.values() for d in v}
        res["ranks"] = cc_ranks(release, doms, local.get("ranks"))
    return res


def cc_ranks(release, domains, local=None):
    """harmonic centrality 名次(越小越重要;Common Crawl 自己算的,可当免费的「域名权重」)。"""
    keys = [rev(d) for d in domains if d and not d.startswith("#")]
    out = {}
    for ln in stream_join(cc_url(release, "ranks"), keys, 5, local):
        p = ln.split("\t")
        if len(p) >= 5 and p[0].isdigit():
            out[rev(p[4])] = int(p[0])
    return out


def cmd_ccgraph(ns):
    targets = read_lines(ns.targets)
    targets = [registrable(t) for t in targets]
    release = ns.release if ns.release and ns.release != "latest" else latest_release()
    t0 = time.time()
    res = ccgraph(targets, own=registrable(ns.own) if ns.own else None, release=release, ranks=ns.ranks)
    res["seconds"] = round(time.time() - t0, 1)
    write_out(ns.out, res)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("链接图 %s:目标 %d 个,图里有 %d 个,没有 %d 个;用时 %ss" % (
            release, len(res["targets"]), len(res["found"]), len(res["missing"]), res["seconds"]))
        for t in sorted(res["inlinks"], key=lambda k: -len(res["inlinks"][k]))[:30]:
            print("  %-28s 入链域 %6d" % (t, len(res["inlinks"][t])))
        print("目标之间互链 %d 对" % len(res["mutual"]))
    return 0


# ---------------------------------------------------------------------------
# crawl:页面级外链(合作/集成/友链/资源页)
# ---------------------------------------------------------------------------

def partner_pages(site, home_body, home_url, max_pages, brands=(), first=()):
    """首页里的合作类链接 + sitemap 里路径像合作类的页 + sitemap 里路径带别家品牌词的页
    (评测、合作方介绍、客座文章常以对方命名,例如 /partners/software/everyinfra-review)。
    first:最先抓的品牌词(我们自己的)。一次抓几百个站时,别家品牌词的页会把页数上限占满,
    带我们品牌词的页、合作类页要排在前面。"""
    cands, branded, mine = [], [], []
    p = LinkParser()
    try:
        p.feed(home_body[:800_000])
    except Exception:
        pass
    own = registrable(home_url)
    for ln in p.links:
        u = urllib.parse.urljoin(home_url, ln["href"]).split("#")[0]
        if registrable(u) == own and PARTNER_PATH.search(urllib.parse.urlsplit(u).path or "/"):
            cands.append(u)
    st, final, body = fetch(urllib.parse.urljoin(home_url, "/sitemap.xml"))
    if st == 200 and body:
        try:
            kind, urls, children = SC.parse_sitemap_bytes(body.encode("utf-8"))
            for ch in children[:5]:
                ch = ch.get("loc", "") if isinstance(ch, dict) else ch
                s2, _, b2 = fetch(ch)
                if s2 == 200:
                    try:
                        urls += SC.parse_sitemap_bytes(b2.encode("utf-8"))[1]
                    except ValueError:
                        pass
            for u in urls:
                loc = u.get("loc", "") if isinstance(u, dict) else u
                path = (urllib.parse.urlsplit(loc).path or "/").lower()
                if any(b in path for b in first):
                    mine.append(loc)
                elif any(b in path for b in brands):
                    branded.append(loc)
                elif PARTNER_PATH.search(path):
                    cands.append(loc)
        except ValueError:
            pass
    seen, out = set(), []
    for u in mine + cands + branded:   # 以我们命名的页最可能是给我们的落点,先抓;再是合作页,最后是以别家命名的页
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out[:max_pages]


def brand_token(domain):
    """everyinfra.com → everyinfra;太短(<5 个字符)的不用,免得撞上普通词。"""
    t = domain.split(".")[0].lower()
    return t if len(t) >= 5 and t not in GENERIC_TOKENS else ""


def crawl_site(site, max_pages=30, extra=(), brands=(), first=()):
    home = site if "://" in site else "https://%s/" % site
    st, final, body = fetch(home)
    pages = [{"url": final, "status": st, "kind": "home", "links": external_links(body, final) if st == 200 else []}]
    if st == 200:
        for u in list(extra) + partner_pages(site, body, final, max_pages,
                                                    [b for b in brands if b and b != brand_token(registrable(final))],
                                                    [b for b in first if b and b != brand_token(registrable(final))]):
            s2, f2, b2 = fetch(u)
            pages.append({"url": f2, "status": s2, "kind": "partner",
                          "links": external_links(b2, f2) if s2 == 200 else []})
    return {"site": registrable(final or home), "pages": pages}


def _safe_crawl(site, max_pages, extra, brands, first=()):
    """一个站出意外不拖垮整批:记下错误,页面为空。"""
    try:
        return crawl_site(site, max_pages, extra, brands, first)
    except Exception as e:      # noqa: BLE001
        return {"site": registrable(site), "pages": [], "error": "%s: %s" % (type(e).__name__, e)}


def page_mutual(crawled, own=None):
    """站 A 某页链 B、站 B 某页链 A → 互换对,带两边页面和 rel。"""
    links = defaultdict(list)       # (A,B) → [(page, rel)]
    for s in crawled:
        for pg in s["pages"]:
            for ln in pg["links"]:
                links[(s["site"], ln["domain"])].append({"page": pg["url"], "rel": ln["rel"], "kind": pg["kind"]})
    pairs = []
    sites = {s["site"] for s in crawled}
    for (a, b), ev in links.items():
        if a < b and b in sites and (b, a) in links:
            pairs.append({"a": a, "b": b, "a_links_b": ev[:3], "b_links_a": links[(b, a)][:3],
                          "involves_own": own in (a, b)})
    return sorted(pairs, key=lambda p: (not p["involves_own"], p["a"], p["b"]))


def cmd_crawl(ns):
    sites = [registrable(s) for s in read_lines(ns.sites)]
    own = registrable(ns.own) if ns.own else None
    extra = {}
    if ns.own_pages:
        extra[own] = read_lines(ns.own_pages)
    if own and own not in sites:
        sites.append(own)
    brands = sorted({brand_token(s) for s in sites} - {""})
    from concurrent.futures import ThreadPoolExecutor    # 按站并行;同一个站内仍是顺序抓
    with ThreadPoolExecutor(max_workers=max(1, ns.workers)) as ex:
        first = [brand_token(own)] if own else []
        crawled = list(ex.map(lambda s: _safe_crawl(s, ns.max_pages, extra.get(s, ()), brands, first), sites))
    res = {"own": own, "sites": crawled, "mutual": page_mutual(crawled, own)}
    write_out(ns.out, res)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("抓了 %d 个站,页面级互链 %d 对" % (len(crawled), len(res["mutual"])))
        for m in res["mutual"][:30]:
            print("  %s ↔ %s   %s | %s" % (m["a"], m["b"], m["a_links_b"][0]["page"], m["b_links_a"][0]["page"]))
    return 0


# ---------------------------------------------------------------------------
# intersect:外联候选 + 互换关系
# ---------------------------------------------------------------------------

def load_ledger(path):
    if not path:
        return set()
    with open(path, encoding="utf-8") as f:
        return {registrable(r.get("domain", "")) for r in csv.DictReader(f) if r.get("domain")}


def intersect(graph, crawl=None, own=None, min_seeds=2, ledger=(), seeds=None):
    """seeds:只把这些目标域当种子(链接图里可以多查一些域,算候选时只用确定的种子)。"""
    own = own or graph.get("own")
    seeds = {d for d in (set(seeds) if seeds else set(graph["inlinks"])) if not is_platform(d)} - {own}
    links_to = defaultdict(set)            # 来源域 → 它链到的种子
    followed = defaultdict(set)            # 来源域 → 至少有一条不带 nofollow / sponsored / ugc 的种子
    evidence = defaultdict(set)            # 来源域 → 页面级证据(哪几页链了种子)
    page_best = defaultdict(int)           # 来源域 → 单页最多链了几家种子(同名不同后缀算一家)
    graph_only = set()
    for t, srcs in graph["inlinks"].items():
        if t not in seeds:
            continue
        for s in srcs:
            links_to[s].add(t)
            followed[s].add(t)             # 链接图只到域名级,不知道 rel
            graph_only.add(s)
    own_linkers = set(graph["inlinks"].get(own, []))
    if crawl:   # 页面级证据补进来(链接图之后才出现的链接)
        for s in crawl["sites"]:
            for pg in s["pages"]:
                on_page = {ln["domain"] for ln in pg["links"] if ln["domain"] in seeds and not ln.get("chrome")}
                page_best[s["site"]] = max(page_best[s["site"]], len(_brands(on_page - {s["site"]})))
                for ln in pg["links"]:
                    if ln["domain"] in seeds and not ln.get("chrome"):   # 导航、页脚里的不算推荐
                        links_to[s["site"]].add(ln["domain"])
                        if not {"nofollow", "sponsored", "ugc"} & set(ln.get("rel", ())):
                            followed[s["site"]].add(ln["domain"])
                        evidence[s["site"]].add((pg.get("kind", ""), pg["url"]))
                    if ln["domain"] == own:
                        own_linkers.add(s["site"])
    ranks = graph.get("ranks", {})
    rows = []
    for d, ts in links_to.items():
        ts = ts - {d}
        if d.startswith("#") or d == own or len(_brands(ts)) < min_seeds or d in own_linkers:
            continue
        # 页面证据要求「同一页」链了 ≥min_seeds 家:四页各链一家的站,没有一页是在推荐同行
        if d not in graph_only and page_best[d] < min_seeds:
            continue
        rows.append({"domain": d, "seeds_linked": len(_brands(ts)), "best_page": page_best.get(d, ""),
                     "followed": len(_brands(followed[d] & ts)),
                     "seeds": ";".join(sorted(ts)),
                     "is_seed": int(d in seeds), "platform": int(is_platform(d)),
                     "cc_rank": ranks.get(d, ""), "contacted": int(d in ledger),
                     "evidence": ";".join(u for _, u in sorted(evidence.get(d, ()))[:6]),
                     "evidence_kind": ",".join(sorted({k for k, _ in evidence.get(d, ())})) or "commoncrawl"})
    rows.sort(key=lambda r: (r["platform"], -r["seeds_linked"], r["cc_rank"] if r["cc_rank"] != "" else 10**12))
    mutual = [{"a": a, "b": b, "source": "commoncrawl"} for a, b in graph.get("mutual", [])]
    if crawl:
        mutual += [{"a": m["a"], "b": m["b"], "source": "page",
                    "a_page": m["a_links_b"][0]["page"], "b_page": m["b_links_a"][0]["page"]}
                   for m in crawl.get("mutual", [])]
    return rows, mutual


# 互换池只认这几类路径:合作伙伴、友链、集成、联盟页。tools / resources / blog 太杂(博客里的「工具推荐」不是互换)。
EXCHANGE_PATH = re.compile(
    r"/(partners?|partnerships?|friends?|links|friend-?links|integrations?|affiliates?|alliances?|ecosystem|"
    r"technology-partners|友情链接|合作伙伴|合作)(/|$|\.html)", re.I)


def exchangers(crawl, own=None, ledger=(), min_listed=3):
    """互换池:① 自己有合作 / 友链 / 集成页、上面列了 ≥min_listed 个外站的站(在做互换的站);
    ② 这些页上列出的外站,按被几家列出排序(被代理、指纹浏览器、验证码站同时列着的,最可能也愿意和我们换)。
    跟 intersect 的区别:intersect 找「推荐同行的榜单 / 资源页」,看主题对不对口;这里只看「会不会换」,不看主题。"""
    own_linkers = set()
    hosts, listed = {}, defaultdict(lambda: {"by": set(), "nofollow": 0, "n": 0, "pages": []})
    for s in crawl["sites"]:
        for pg in s["pages"]:
            for ln in pg["links"]:
                if own and ln["domain"] == own:
                    own_linkers.add(s["site"])
            if s["site"] == own or is_platform(s["site"]):   # 我们自己的合作页、平台站的生态页不算
                continue
            try:
                path = urllib.parse.urlsplit(pg["url"]).path or "/"
            except ValueError:          # 坏网址(没闭合的 IPv6 等)
                continue
            if pg.get("kind") == "home" or not EXCHANGE_PATH.search(path):
                continue
            ext = {}
            for ln in pg["links"]:
                d = ln["domain"]
                if d == s["site"] or _sibling(d, s["site"]) or is_platform(d):
                    continue
                ext.setdefault(d, ln)
            if len(ext) < min_listed:
                continue
            h = hosts.setdefault(s["site"], {"pages": [], "listed": 0})
            h["pages"].append(pg["url"])
            h["listed"] = max(h["listed"], len(ext))
            for d, ln in ext.items():
                rec = listed[d]
                if s["site"] not in rec["by"]:
                    rec["by"].add(s["site"])
                    rec["pages"].append(pg["url"])
                    rec["n"] += 1
                    rec["nofollow"] += int(bool({"nofollow", "sponsored", "ugc"} & set(ln.get("rel", ()))))
    rows = []
    for d, h in hosts.items():
        if d == own:
            continue
        rows.append({"domain": d, "role": "host", "count": h["listed"], "by": "", "nofollow": "",
                     "links_us": int(d in own_linkers), "contacted": int(d in ledger),
                     "pages": ";".join(h["pages"][:3])})
    for d, r in listed.items():
        if d == own or d in hosts:
            continue
        rows.append({"domain": d, "role": "listed", "count": r["n"], "by": ";".join(sorted(r["by"])),
                     "nofollow": r["nofollow"], "links_us": int(d in own_linkers), "contacted": int(d in ledger),
                     "pages": ";".join(r["pages"][:3])})
    rows.sort(key=lambda r: (r["role"] != "host", r["contacted"], r["links_us"], -r["count"], r["domain"]))
    return rows


def _brands(domains):
    """firecrawl.dev 和 firecrawl.link、brightdata.com 和 brightdata.de 算一家。"""
    return {d.split(".")[0] for d in domains}


def listicles_as_crawl(listicle_res):
    """listicles 的抓取结果(每篇的外链域)当成页面级证据:发榜单的站 = 链了这些种子的站。"""
    sites = defaultdict(list)
    for f in listicle_res.get("fetched", []):
        if f.get("status") == 200 and f.get("domains"):
            nf = set(f.get("nofollow", ()))
            sites[registrable(f["url"])].append({"url": f["url"], "kind": "listicle",
                                                 "links": [{"domain": d, "rel": ["nofollow"] if d in nf else []}
                                                           for d in f["domains"]]})
    return [{"site": k, "pages": v} for k, v in sites.items()]


def cmd_intersect(ns):
    graph = {"inlinks": {}, "mutual": []}
    if ns.graph:
        with open(ns.graph, encoding="utf-8") as f:
            graph = json.load(f)
    crawl = None
    if ns.crawl:
        with open(ns.crawl, encoding="utf-8") as f:
            crawl = json.load(f)
    if ns.listicles:
        with open(ns.listicles, encoding="utf-8") as f:
            extra = listicles_as_crawl(json.load(f))
        crawl = crawl or {"sites": [], "mutual": []}
        crawl = {"sites": crawl["sites"] + extra, "mutual": crawl.get("mutual", [])}
    own = registrable(ns.own) if ns.own else graph.get("own")
    seeds = [registrable(x) for x in read_lines(ns.seeds)] if ns.seeds else None
    rows, mutual = intersect(graph, crawl, own, ns.min, load_ledger(ns.ledger), seeds)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["domain", "seeds_linked", "best_page", "followed", "seeds", "is_seed", "platform", "cc_rank",
                                              "contacted", "evidence_kind", "evidence"])
            w.writeheader()
            w.writerows(rows)
    res = {"own": own, "candidates": rows, "mutual": mutual}
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("外联候选(链到 ≥%d 个种子、没链 %s)%d 个;互换关系 %d 对" % (ns.min, own, len(rows), len(mutual)))
        for r in rows[:30]:
            print("  %-28s 链了 %2d 个种子  rank=%s%s" % (r["domain"], r["seeds_linked"], r["cc_rank"],
                                                   "  已联系" if r["contacted"] else ""))
    return 0


# ---------------------------------------------------------------------------
# deadlinks:失效链接替换(broken link building)的候选
# ---------------------------------------------------------------------------

DEAD_STATUS = {404, 410}


def link_status(url, timeout=10.0):
    """→ (status, 说明)。0 = 连不上(域名过期、DNS 失败、拒绝连接)。HEAD 不被支持时退 GET。"""
    try:
        r = SC.robust_fetch(url, timeout=timeout, method="HEAD", retries=1)
        if r["status"] in (403, 405, 501):
            r = SC.robust_fetch(url, timeout=timeout, retries=1)
        return r["status"], r["final_url"]
    except Exception as e:
        return 0, str(e)[:120]


def deadlinks(pages, own=None, per_page=80, fetcher=None, checker=None):
    """pages:资源页、榜单页网址 → 页上指向别站、现在 404/410/连不上的链接。
    同一个目标网址只查一次;我们自己的链接不查。"""
    fetcher = fetcher or fetch
    checker = checker or link_status
    cache, out = {}, []
    for page in pages:
        st, final, body = fetcher(page)
        if st != 200:
            continue
        for ln in external_links(body, final)[:per_page]:
            if ln["domain"] == own or is_platform(ln["domain"]):
                continue
            if ln["url"] not in cache:
                cache[ln["url"]] = checker(ln["url"])
            code, note = cache[ln["url"]]
            if code in DEAD_STATUS or code == 0:
                out.append({"page": final, "dead_url": ln["url"], "status": code, "note": note,
                            "anchor": ln["anchor"], "rel": ln["rel"]})
    return {"pages": len(pages), "links_checked": len(cache), "dead": out}


def cmd_exchangers(ns):
    crawl = {"sites": []}
    for path in ns.crawl:           # 可以给多份:第一轮种子站 + 第二轮(第一轮合作页上列出的站)
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        seen = {s["site"] for s in crawl["sites"]}
        crawl["sites"] += [s for s in c["sites"] if s["site"] not in seen]
        crawl.setdefault("own", c.get("own"))
    own = registrable(ns.own) if ns.own else crawl.get("own")
    rows = exchangers(crawl, own, load_ledger(ns.ledger), ns.min_listed)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["domain", "role", "count", "by", "nofollow", "links_us", "contacted", "pages"])
            w.writeheader()
            w.writerows(rows)
    if ns.json:
        print(json.dumps(rows, ensure_ascii=False))
        return 0
    hosts = [r for r in rows if r["role"] == "host"]
    lst = [r for r in rows if r["role"] == "listed"]
    fresh = lambda rs: [r for r in rs if not r["contacted"] and not r["links_us"]]   # noqa: E731
    print("在做互换的站(有合作 / 友链 / 集成页,列了 ≥%d 个外站)%d 个,没联系过、没链我们的 %d 个"
          % (ns.min_listed, len(hosts), len(fresh(hosts))))
    print("这些页上列出的外站 %d 个;被 ≥2 家列出、没联系过的 %d 个"
          % (len(lst), len([r for r in fresh(lst) if r["count"] >= 2])))
    for r in fresh(hosts)[:15]:
        print("  [站] %-28s 列了 %3d 个  %s" % (r["domain"], r["count"], r["pages"].split(";")[0]))
    for r in fresh(lst)[:15]:
        print("  [被列] %-26s %d 家列出:%s" % (r["domain"], r["count"], r["by"][:80]))
    return 0


def cmd_deadlinks(ns):
    pages = [u for u, _ in load_listicles(ns.input)]
    res = deadlinks(pages[: ns.max_pages], registrable(ns.own) if ns.own else None, ns.per_page)
    write_out(ns.out, res)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("查了 %d 页、%d 个外链;失效 %d 个" % (res["pages"], res["links_checked"], len(res["dead"])))
        for d in res["dead"][:40]:
            print("  [%s] %s\n        在 %s(锚文本:%s)" % (d["status"] or "连不上", d["dead_url"], d["page"], d["anchor"]))
    return 0


# ---------------------------------------------------------------------------
# unlinked:提到我们却没链我们的页
# ---------------------------------------------------------------------------

def page_text(body):
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    return " ".join(re.sub(r"(?s)<[^>]+>", " ", t).split())


def unlinked(pages, own, brand_rx, fetcher=None):
    """pages:搜品牌名得到的网址 → 提到品牌、却没有任何指向 own 的链接的页(平台站和我们自己的不算)。"""
    fetcher = fetcher or fetch
    rx = re.compile(brand_rx, re.I)
    out = []
    for page in pages:
        d = registrable(page)
        if d == own or is_platform(d):
            continue
        st, final, body = fetcher(page)
        if st != 200:
            continue
        text = page_text(body)
        m = rx.search(text)
        if not m:
            continue
        links = [ln for ln in external_links(body, final) if ln["domain"] == own]
        if links:
            continue
        a = max(0, m.start() - 80)
        out.append({"page": final, "domain": d, "context": text[a:m.end() + 80]})
    return out


def cmd_unlinked(ns):
    pages = [u for u, _ in load_listicles(ns.input)]
    res = {"own": registrable(ns.own), "brand": ns.brand,
           "unlinked": unlinked(pages, registrable(ns.own), ns.brand)}
    write_out(ns.out, res)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("提到 %s 却没链 %s 的页 %d 个" % (ns.brand, res["own"], len(res["unlinked"])))
        for u in res["unlinked"][:40]:
            print("  %s\n        …%s…" % (u["page"], u["context"]))
    return 0


# ---------------------------------------------------------------------------
# footprint:竞品 SEO 底账(SERP 抽样)
# ---------------------------------------------------------------------------

PAGE_TYPES = [
    ("comparison", re.compile(r"alternative|(^|[/_-])vs([/_.-]|$)|versus|compare|comparison|-or-", re.I)),
    ("glossary", re.compile(r"/glossary/|/wiki/|/what-is|/definitions?/|/terms?/", re.I)),
    ("free_tool", re.compile(r"/tools?/|/free-|checker|generator|tester|calculator|validator", re.I)),
    ("docs", re.compile(r"/docs?/|/documentation/|/api-reference|/reference/|/sdk/|^docs\.|^developers?\.", re.I)),
    ("blog", re.compile(r"/blog/|/guides?/|/learn/|/articles?/|/resources?/|/academy/|/tutorials?/|/insights?/|/posts?/", re.I)),
    ("integration", re.compile(r"/integrations?/", re.I)),
    ("pricing", re.compile(r"/pricing", re.I)),
    ("marketplace", re.compile(r"/store/|/actors?/|/marketplace/|/templates?/", re.I)),
    ("product", re.compile(r"/products?/|/solutions?/|scraper|-api(/|$)|/api/|/apis?/|/proxies/|/proxy/|unlocker|crawler", re.I)),
]


def page_type(url):
    sp = urllib.parse.urlsplit(url)
    host = (sp.hostname or "").lower()
    path = sp.path or "/"
    probe = host + path if host.startswith(("docs.", "developer", "developers.")) else path
    for name, rx in PAGE_TYPES:
        if name == "docs" and host.startswith(("docs.", "developer")):
            return "docs"
        if rx.search(probe):
            return name
    return "home" if path in ("", "/") or re.fullmatch(r"/[a-z]{2}(-[a-z]{2})?/?", path) else "other"


def footprint(serp, competitors=None, own=None, top=8):
    kws = serp.get("keywords", [])
    by_dom = defaultdict(lambda: {"keywords": {}, "types": Counter(), "urls": Counter()})
    appear = Counter()
    for k in kws:
        seen = set()
        for r in k.get("results", []):
            d = registrable(r.get("url", ""))
            if not d or d in seen:
                continue
            seen.add(d)
            appear[d] += 1
            rec = by_dom[d]
            rec["keywords"][k["keyword"]] = r.get("rank")
            rec["types"][page_type(r["url"])] += 1
            rec["urls"][r["url"]] += 1
    if competitors:
        comps = [registrable(c) for c in competitors]
    else:
        comps = [d for d, _ in appear.most_common() if not is_platform(d) and d != own][:top]
    out = []
    for d in comps:
        rec = by_dom.get(d)
        if not rec:
            out.append({"domain": d, "keywords_ranked": 0})
            continue
        ranks = [r for r in rec["keywords"].values() if isinstance(r, int)]
        out.append({"domain": d, "keywords_ranked": len(rec["keywords"]),
                    "top3": sum(1 for r in ranks if r <= 3),
                    "avg_rank": round(sum(ranks) / len(ranks), 1) if ranks else None,
                    "page_types": dict(rec["types"].most_common()),
                    "top_urls": [u for u, _ in rec["urls"].most_common(8)],
                    "keywords": dict(sorted(rec["keywords"].items(), key=lambda kv: (kv[1] or 99)))})
    gaps = defaultdict(list)       # 赢家页面类型 → 我们没排上的词
    own_rank = {}
    for k in kws:
        res = k.get("results", [])
        mine = [r.get("rank") for r in res if registrable(r.get("url", "")) == own]
        own_rank[k["keyword"]] = mine[0] if mine else None
        if mine:
            continue
        for r in res:
            d = registrable(r.get("url", ""))
            if d in comps:
                gaps[page_type(r["url"])].append({"keyword": k["keyword"], "winner": d, "url": r["url"],
                                                  "rank": r.get("rank")})
                break
    return {"competitors": out, "serp_regulars": appear.most_common(30),
            "own": own, "own_ranked": {k: v for k, v in own_rank.items() if v},
            "gaps_by_winning_page_type": {t: v for t, v in sorted(gaps.items(), key=lambda kv: -len(kv[1]))},
            "keywords_total": len(kws)}


def cmd_footprint(ns):
    with open(ns.serp, encoding="utf-8") as f:
        serp = json.load(f)
    comps = [c.strip() for c in ns.competitors.split(",")] if ns.competitors else None
    res = footprint(serp, comps, registrable(ns.own) if ns.own else None, ns.top)
    write_out(ns.out, res)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False))
        return 0
    print("SERP 样本 %d 个词;我们(%s)排上 %d 个" % (res["keywords_total"], res["own"], len(res["own_ranked"])))
    for c in res["competitors"]:
        if not c.get("keywords_ranked"):
            print("  %-22s 0 个词" % c["domain"])
            continue
        types = ", ".join("%s %d" % kv for kv in list(c["page_types"].items())[:4])
        print("  %-22s %3d 个词(前三 %d,均名次 %s)  页面类型:%s" % (
            c["domain"], c["keywords_ranked"], c["top3"], c["avg_rank"], types))
    print("我们缺位的词,按赢家页面类型:")
    for t, v in res["gaps_by_winning_page_type"].items():
        print("  %-12s %3d 个  例:%s" % (t, len(v), "; ".join(x["keyword"] for x in v[:4])))
    return 0


def build_parser():
    ap = argparse.ArgumentParser(description="竞品与外链发现(种子站、谁链谁、互换、外联候选、竞品 SEO 底账)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("listicles")
    a.add_argument("--input", required=True)
    a.add_argument("--min", type=int, default=2)
    a.add_argument("--delay", type=float, default=0.3)
    a.add_argument("--out")
    a.add_argument("--json", action="store_true")
    b = sub.add_parser("ccgraph")
    b.add_argument("--targets", required=True, help="一行一个域名")
    b.add_argument("--own")
    b.add_argument("--release", default="latest")
    b.add_argument("--ranks", action="store_true", help="另读 harmonic 名次文件(再下 2.3GB)")
    b.add_argument("--out")
    b.add_argument("--json", action="store_true")
    c = sub.add_parser("crawl")
    c.add_argument("--sites", required=True)
    c.add_argument("--own")
    c.add_argument("--own-pages", help="我们这边放了对方链接的页面,一行一个(例如 /partners/<slug>)")
    c.add_argument("--max-pages", type=int, default=30)
    c.add_argument("--workers", type=int, default=6, help="同时抓几个站(每个站内顺序抓)")
    c.add_argument("--out")
    c.add_argument("--json", action="store_true")
    d = sub.add_parser("intersect")
    d.add_argument("--graph", help="ccgraph 的输出;没有时只用页面级证据(--crawl / --listicles)")
    d.add_argument("--listicles", help="listicles 的输出,发榜单的站也算页面级证据")
    d.add_argument("--crawl")
    d.add_argument("--own")
    d.add_argument("--min", type=int, default=2)
    d.add_argument("--ledger")
    d.add_argument("--seeds", help="只把这些域当种子,一行一个(默认链接图里的全部目标)")
    d.add_argument("--out")
    d.add_argument("--json", action="store_true")
    e = sub.add_parser("footprint")
    e.add_argument("--serp", required=True)
    e.add_argument("--competitors")
    e.add_argument("--own")
    e.add_argument("--top", type=int, default=8)
    e.add_argument("--out")
    e.add_argument("--json", action="store_true")
    x = sub.add_parser("exchangers")
    x.add_argument("--crawl", required=True, action="append", help="crawl 的输出;可重复给多份(滚雪球的第二轮)")
    x.add_argument("--own")
    x.add_argument("--ledger")
    x.add_argument("--min-listed", type=int, default=3, help="一页列了至少几个外站才算合作 / 友链页")
    x.add_argument("--out")
    x.add_argument("--json", action="store_true")
    f = sub.add_parser("deadlinks")
    f.add_argument("--input", required=True, help="资源页/榜单页:listicles.json 或一行一个网址")
    f.add_argument("--own")
    f.add_argument("--max-pages", type=int, default=100)
    f.add_argument("--per-page", type=int, default=80)
    f.add_argument("--out")
    f.add_argument("--json", action="store_true")
    g = sub.add_parser("unlinked")
    g.add_argument("--input", required=True, help="搜品牌名得到的网址,一行一个(或 listicles.json 格式)")
    g.add_argument("--own", required=True)
    g.add_argument("--brand", required=True, help="品牌名正则,例如 'every\\s?infra'")
    g.add_argument("--out")
    g.add_argument("--json", action="store_true")
    return ap


def main(argv=None):
    ns = build_parser().parse_args(argv)
    return {"listicles": cmd_listicles, "ccgraph": cmd_ccgraph, "crawl": cmd_crawl,
            "intersect": cmd_intersect, "footprint": cmd_footprint, "exchangers": cmd_exchangers,
            "deadlinks": cmd_deadlinks, "unlinked": cmd_unlinked}[ns.cmd](ns)


if __name__ == "__main__":
    sys.exit(main())
