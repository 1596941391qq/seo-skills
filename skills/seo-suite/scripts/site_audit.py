#!/usr/bin/env python3
"""单页/多页 SEO 审计器(stdlib only)。整合百仓深扫的阈值:
title/desc 限值按 markets.json 市场单位(chars/fullwidth/grapheme)/ H1 唯一 /
词数 CJK·天城文·泰文字素感知 / 链接>100 / alt 覆盖 / canonical·robots·og·lang·JSON-LD /
llms.txt·sitemap / AI 爬虫放行 / staging 子域。
S2 实测修复(2026-10-09):title 收集只在 <title>…</title> 内(script/JSON-LD 不再吞入);
泰文字素计长、天城文按字符计词、拉丁扩展(越南/波兰/土耳其等)词不被 ASCII 正则切碎;
--market 接线 markets.json 阈值(18 市场)。
S3 扩展(2026-10-10,borrow-specs A3/A4):AI Search Health 独立子分(Semrush 8 bot 名单/
llms.txt/Last-Modified>183 天/语义 HTML 比值/词数>15000/BLUF 密度,--json 新增 ai_search_health 节)+
rendering 5 检查(geo-aeo-tracker 源码口径:CSR/noscript/JS 重量/服务端内容/H1-H2)。
S4 扩展(2026-10-11,borrow-specs A2,20 项借鉴清单第 10 条):具名 bulk export(--export-dir DIR——
每 rule 一份受影响 URL 清单 {area}-{规则简名}.txt,一行一 URL,同 slug 冲突自动合并;另写
summary.json:每 rule slug/受影响数/占比/severity)+ findings 汇总受影响面列(N/M 页 XX%,
SF Coverage 口径——分母=已审计页数而非全站页数,表头注明;单 URL 时命中规则即 1/1)。
用法: python3 site_audit.py URL [URL...] [--market ja|en|zh|th|hi|vi|pl|tr|...] [--export-dir DIR]
判定: CRITICAL 存在则退出码 1。
S5 修复(2026-10-12,R5 错漏清单 8 项,references/overview/pipeline-completeness.md):
robots 专属空组不再回落 * 组(RFC 9309,消灭假 CRITICAL)/X-Robots-Tag 取头大小写无关/
fetch 解码 Content-Type charset→BOM→meta charset 嗅探→utf-8 replace(GBK 不再全量乱码)/
Last-Modified 与 now 统一 timezone.utc(消灭时区混 8h)/canonical 外域比较前 netloc 小写+
去默认端口/robots.txt 404 视为全放行不产 finding(不可达消息去双斜杠)/coverage 分母与
summary.audited 剔除拒审([SKIP])页/--market·--export-dir 缺值与未知市场统一 stderr+exit 2。"""
import sys, os, re, json, math, codecs, unicodedata, urllib.error, urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (compatible; seo-suite-audit/1.1)"
SCHEMA_VERSION = 1   # --json 顶层 schema 版本(评分契约,borrow-specs E8);改输出结构必须 bump 并重生成 tests/fixtures/scoring_v1.json
# Semrush 官方 8 bot 检查名单(AI Search Health 口径,查这 8 个而非 27 个全量):
# 4 个搜索引用 + Googlebot + Google-Extended + Perplexity-User + Claude-User。
# Google-Extended 是 robots token 不是爬虫 → 单列(WARN 级);GPTBot/ClaudeBot 训练型
# 不影响搜索可见性 → 不进失败项,被禁只出 notice(INFO)。
SEARCH_BOTS = ["ChatGPT-User", "OAI-SearchBot", "Googlebot", "Google-Extended",
               "Perplexity-User", "PerplexityBot", "Claude-User", "Claude-SearchBot"]
TRAINING_BOTS = ["GPTBot", "ClaudeBot"]          # 训练型:只提示不计失败(borrow-specs A3)
RETRIEVAL_BOTS = SEARCH_BOTS                     # 向后兼容别名(旧 4 bot ⊂ 新 8 bot)
# 语义 HTML 标签集(Semrush 语义比值口径):header/nav/main/article/section/aside/footer/
# h1-h6/figure/time/mark/details
SEMANTIC_TAGS = frozenset(("header", "nav", "main", "article", "section", "aside", "footer",
                           "figure", "time", "mark", "details")) | {f"h{i}" for i in range(1, 7)}
SEMANTIC_MIN_RATIO = 0.10       # 比值<10% 触发——阈值自定[推断],官方未公开
CONTENT_MAX_WORDS = 15000       # 词数>15000 触发内容过长——阈值自定[推断],官方未公开
FRESHNESS_MAX_DAYS = 183        # Last-Modified>183 天(6 个月)→notice【Semrush 官方】
# AI Search Health 子分权重(bots 0.4/llms 0.15/freshness 0.15/semantic 0.15/content 0.15)
# ——通过率加权,权重自定[推断];bluf 进 checks 仅记录不参与计分
AI_HEALTH_WEIGHTS = {"bots": 0.40, "llms_txt": 0.15, "freshness": 0.15,
                     "semantic_html": 0.15, "content_length": 0.15}
# CSR 空挂载点(geo-aeo-tracker 源码口径):#root/#app/#__next/#svelte
MOUNT_IDS = ("root", "app", "__next", "svelte")
# BLUF 直答短语正则(geo-aeo-tracker 源码公式,原样照抄)
BLUF_RE = re.compile(r"in short|tl;dr|summary|key takeaways|bottom line|the answer is|here's (what|how|why)", re.I)
STAGING = ("test.", "staging.", "dev.", "preview.", "beta.", "uat.")
# fetch 质量守卫:被挑战页/WAF 拦截时拒绝审计(输出 [SKIP],不算 CRITICAL)
MIN_BODY_BYTES = 200
# S2a B11(2026-10-21):只认**结构特征**,不按正文关键词拒审——页面谈论 CAPTCHA/"access denied"
# 的正常页(验证码产品页等)必须照常审计。三类结构特征:
# ① 拦截页专用 <title>(Cloudflare 整页挑战 "Just a moment..." 等);
# ② 拦截页专用元素属性(challenge-form / cf-browser-verification / _cf_chl_opt / px-captcha 等);
# ③ 正文极短(可见文本 < CHALLENGE_MAX_TEXT 字)且含拦截措辞或 /cdn-cgi/challenge-platform/ 脚本。
# 注意:Cloudflare JavaScript Detections 会在**每个** HTML 页注入 /cdn-cgi/challenge-platform/ 脚本
# (developers.cloudflare.com/cloudflare-challenges/challenge-types/javascript-detections/,核对 2026-10-21),
# 所以该脚本单独出现不算挑战页,只在正文极短时作佐证。
CHALLENGE_TITLES = ("just a moment", "attention required! | cloudflare", "checking your browser",
                    "ddos-guard", "please wait while we verify", "verifying you are human")
CHALLENGE_ATTRS = re.compile(r"""(?:id|class|action|name)\s*=\s*["'][^"']*(?:challenge-form|"""
                             r"""cf-browser-verification|cf-challenge-running|__cf_chl|cf_chl_|px-captcha|ddos-guard)""",
                             re.I)
CHALLENGE_JS = re.compile(r"_cf_chl_opt|/cdn-cgi/challenge-platform/h/[^\s\"']*/orchestrate/", re.I)
CHALLENGE_PHRASES = ("verify you are human", "checking your browser", "unusual traffic",
                     "access denied", "captcha", "enable javascript and cookies to continue",
                     "challenge-platform", "you don't have permission to access")
CHALLENGE_MAX_TEXT = 600          # 可见文本 <600 字视为"正文极短"(本套件口径)

# ---- 插件内容(Lighthouse「Document uses plugins」源码口径,core/audits/seo/plugins.js v12;
# Ahrefs Site Audit 的同名项在 Usability and performance 类,https://ahrefs.com/blog/seo-issues/ 第 4 节)。
# applet 一律算;embed/object 的 type 命中 MIME 名单,或 src/code/data/<param name=code|movie|source|src>
# 指向 swf/flv/class/xap 文件才算——<object type="image/svg+xml">、<embed src="x.pdf"> 不算。
PLUGIN_TYPES = ("application/x-shockwave-flash", "application/x-java-applet", "application/x-java-bean",
                "application/x-silverlight", "application/x-silverlight-2")
PLUGIN_EXTS = ("swf", "flv", "class", "xap")
PLUGIN_SOURCE_PARAMS = ("code", "movie", "source", "src")

# ---- 按爬虫名写的 robots meta(Bing:「you can replace the generic name="robots" with
# name="bingbot" to limit the meta tag to only apply to Bing」;Google 同理认 name="googlebot"):
BOT_META_NAMES = ("googlebot", "googlebot-news", "bingbot", "msnbot")
# robots 指令里自带冒号的指令名——X-Robots-Tag「bingbot: noindex」里冒号前若不是这些,就是爬虫名
DIRECTIVES_WITH_VALUE = ("max-snippet", "max-image-preview", "max-video-preview", "unavailable_after")


def _plugin_url(u):
    """Lighthouse isPluginURL:取 URL 路径最后一个点后的扩展名比对名单(相对 URL 也认)。"""
    try:
        path = urlparse(urljoin("http://example.com/", u.strip())).path
    except ValueError:
        return False
    parts = path.split(".")
    return len(parts) >= 2 and parts[-1].strip().lower() in PLUGIN_EXTS


def _plugin_type(t):
    t = (t or "").strip().lower()
    return t in PLUGIN_TYPES or t.startswith(("application/x-java-applet", "application/x-java-bean"))


def plugin_elements(embeds):
    """命中 Lighthouse plugins 规则的元素 → 简短描述列表。"""
    hits = []
    for it in embeds:
        tag, why = it["tag"], None
        if tag == "applet":
            why = "applet"
        elif it["type"] and _plugin_type(it["type"]):
            why = "type=" + it["type"].strip()
        elif tag == "embed" and (it["src"] or it["code"]) and _plugin_url(it["src"] or it["code"]):
            why = "src=" + (it["src"] or it["code"])
        elif tag == "object" and it["data"] and _plugin_url(it["data"]):
            why = "data=" + it["data"]
        else:
            for name, val in it["params"]:
                if name.strip().lower() in PLUGIN_SOURCE_PARAMS and _plugin_url(val):
                    why = 'param %s=%s' % (name, val)
                    break
        if why:
            hits.append("<%s %s>" % (tag, why[:80]))
    return hits


def robots_tokens(value):
    """robots 指令串 → [(name, value)](小写,逗号分隔;max-video-preview:-1 → ("max-video-preview","-1"))。"""
    out = []
    # 逗号是规范分隔符;实际站点也有用空格分隔的("noindex nofollow"),修前按子串判 noindex 能命中,
    # 这里按逗号与空白都切,冒号两侧的空格先并掉("max-snippet: 20" → "max-snippet:20")
    for part in re.split(r"[,\s]+", re.sub(r"\s*:\s*", ":", value or "")):
        part = part.strip().lower()
        if not part:
            continue
        name, _, val = part.partition(":")
        out.append((name.strip(), val.strip()))
    return out


def split_x_robots(value):
    """X-Robots-Tag 值 → (通用指令串, {爬虫名: 指令串})。「bingbot: noindex」冒号前不是已知
    带值指令名时按爬虫名处理(Google robots meta 文档:X-Robots-Tag 可指定 user agent)。"""
    generic, agents = [], {}
    m = re.match(r"\s*([a-z][\w-]*)\s*:\s*(.+)$", value or "", re.I)
    if m and m.group(1).lower() not in DIRECTIVES_WITH_VALUE:
        agents[m.group(1).lower()] = m.group(2)
    elif value:
        generic.append(value)
    return ",".join(generic), agents


def robots_directive_findings(meta_robots, meta_agents, xrobots):
    """robots 指令的 Bing/Google 分路判定 → findings。
    依据:Bing「Robots meta tags and attributes that Bing supports」
    (https://www.bing.com/webmasters/help/robots-meta-tags-and-attributes-that-bing-supports-5198d240,
    2026-11-05 读取):name="bingbot" 只对 Bing 生效;max-video-preview:[number] 是整数秒,
    0=可能只显示视频静态图,-1=不限长度;每个 meta 都能改写成 X-Robots-Tag 响应头。
    Google 的 noindex 只看通用 robots 与 googlebot(name="bingbot" 不影响 Google)。"""
    F = []
    xr_generic, xr_agents = split_x_robots(xrobots)
    generic = robots_tokens(meta_robots) + robots_tokens(xr_generic)
    agents = {}
    for name, v in list(meta_agents.items()) + list(xr_agents.items()):
        agents.setdefault(name, []).extend(robots_tokens(v))
    google = generic + agents.get("googlebot", [])
    g_names = {n for n, _ in google}
    if "noindex" in g_names or "none" in g_names:
        F.append(("CRITICAL", "robots", "noindex"))
    if "nosnippet" in g_names:
        F.append(("WARN", "robots", "nosnippet(会限制 AI 特性)"))
    bing_only = agents.get("bingbot", []) + agents.get("msnbot", [])
    b_names = {n for n, _ in bing_only}
    if ("noindex" in b_names or "none" in b_names) and "noindex" not in g_names and "none" not in g_names:
        F.append(("WARN", "robots", "bingbot noindex——只对 Bing 生效:该页不进 Bing 索引(Google 照常收录)"))
    if bing_only:
        F.append(("INFO", "robots", "bingbot 专属指令(只对 Bing 生效): %s"
                  % ", ".join(n + (":" + v if v else "") for n, v in bing_only)))
    for name, v in generic + bing_only + agents.get("googlebot", []):
        if name != "max-video-preview":
            continue
        if not re.fullmatch(r"-?\d+", v or ""):
            F.append(("WARN", "robots", "max-video-preview 值 %r 不是整数秒(Bing/Google 只认整数;-1=不限,0=只给静态图)" % v))
        elif int(v) < -1:
            F.append(("WARN", "robots", "max-video-preview:%s 无效(最小 -1=不限)" % v))
        elif int(v) == 0:
            F.append(("INFO", "robots", "max-video-preview:0——搜索结果只显示视频静态图,不放预览片段"))
        break
    return F

USAGE = """usage: site_audit.py URL [URL...] [--market XX] [--json] [--export-dir DIR] [--serp-titles FILE]
单页全项审计:title/desc 限值(市场单位)/H1/词数/链接/alt/canonical/robots/og/JSON-LD/
llms.txt/sitemap/AI 爬虫放行/staging 子域。
  --market XX      markets.json 18 市场阈值(chars/fullwidth/grapheme)
  --json           结构化输出(findings+meta+verdict+ai_search_health,供 agent 消费):
                   stdout 只有一个 JSON 对象(可直接 jq / json.loads),人读行改写到 stderr;
                   顶层含 market 与 limits(本次 title/description 区间,单位随市场)
  --export-dir DIR 具名 bulk export(SF/Sitebulb 口径):按 rule 生成受影响 URL 清单
                   {area}-{规则简名}.txt(如 canonical-missing.txt/title-too-long.txt;
                   area+message 首词生成稳定 slug,同一 slug 冲突时合并),每文件一行一
                   URL;另写 summary.json(每 rule:slug/受影响数/占比/severity)。
                   目录不存在则创建,已存在直接写(输出由调用方隔离,套件惯例)。
                   单 URL 模式同样可用(产出 1 页的清单)。
  --serp-titles FILE  搜索结果里显示的标题(CSV 表头 url,title 或 JSON [{url,title}]/{url:title});
                   给了才比「页面 title 与 SERP 标题不一致」(INFO,Ahrefs 同名项);不给时输出
                   [跳过] 行与 --json 的 skipped 节写明原因(GSC API 不返回标题,不猜)。
多 URL 审计后输出 findings 汇总(markdown 表):规则×级别×受影响面——N/M 页(XX%),
SF Coverage 口径的简化:分母=本次已审计页数(拒审 [SKIP] 页剔除)而非全站页数(表头
注明);单 URL 时每条命中规则即 1/1。--json 模式新增顶层 exports 节列出导出文件名
(仅 --export-dir 时)。
AI Search Health 子分(Semrush 8 bot 名单口径,与主审计并列输出):
  8 bot 放行(ChatGPT-User/OAI-SearchBot/Googlebot/Google-Extended/Perplexity-User/
  PerplexityBot/Claude-User/Claude-SearchBot;GPTBot/ClaudeBot 训练型只提示;
  Google-Extended 是 robots token 非 爬虫单列)/llms.txt 存在/Last-Modified>183 天/
  语义 HTML 比值<10%/词数>15000/BLUF 密度 → --json 每页 ai_search_health 节
  (score 0-100 通过率加权:bot 0.4/llms·freshness·semantic·content 各 0.15[推断])。
rendering 5 检查(geo-aeo-tracker 源码口径,WARN/INFO 级不产生 CRITICAL):
  CSR 空挂载点(#root/#app/#__next/#svelte + 纯文本<200 字或 text/HTML<0.02;
  __NEXT_DATA__/data-reactroot 赦免)/noscript 回退>20 字/JS 重量(外部>15 或内联>100KB)/
  服务端内容(纯文本>500 字且含 article/main/section)/H1==1 且 H2>=2。
判定:CRITICAL 存在则退出码 1;fetch 守卫触发输出 [SKIP] fetch guard: response too small /
likely challenge page 并拒绝审计结论(该 URL 不计失败,退出码不受影响;拒审页不计入
coverage 分母与 summary.audited)。robots.txt 404=全放行(RFC 9309),不产 finding。
退出码 2(stderr 提示):--market/--export-dir 缺值,或 --market 未知市场。
严重度口径(S2a 2026-10-21,依据 Google 文档原文):description 缺失、无 H1、canonical 相对路径
记 WARN(描述可选、标题层级不影响排名、相对 canonical 支持但不建议);>100 链接记 INFO
(工具约定,现行 Google 文档无此数);description 下限=markets.json desc_min(默认上限一半);
zh 标题按显示宽度(fullwidth 单位);已检测到服务端内容时 JS 重量只 INFO 提示体积、不报无 noscript;
挑战页只按结构特征(拦截页标题/拦截元素/正文极短+拦截措辞)拒审,正文谈论 CAPTCHA 不拒审。"""

# ---- 藏在页面里、对 AI 下指令的文字(提示注入)。读这页的编码 agent 可能照做(改 robots.txt、推主干),
# 所以原文要原样列进运营单,让人看到;同时它也是 Google 垃圾内容政策里的「隐藏文字」。
# 只看隐藏元素(display:none / visibility:hidden / hidden 属性)和 HTML 注释,正文里讲提示注入的文章不算。
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source",
             "track", "wbr"}
HIDDEN_STYLE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.I)
AGENT_DIRECTIVE = re.compile(
    r"ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+instructions|system\s+prompt|"
    r"\bnote\s+to\s+(?:ai|llm|assistant)|"
    r"\b(?:ai|llm|assistant|agent|chatgpt|claude|gpt|copilot)s?\b[^.\n]{0,120}?"
    r"\b(?:ignore|disregard|must|should|instruct\w*|change|edit|modify|update|replace|push|commit|delete|"
    r"disallow|robots\.txt)\b|"
    r"(?:AI|助手|智能体|大模型|模型)[^。\n]{0,40}?(?:忽略|修改|改成|推送|删除|提交|照做)", re.I)


class _Hidden(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.chunks, self.depth = [], [], 0
    def handle_starttag(self, tag, attrs):
        if tag in VOID_TAGS:
            return
        a = dict(attrs)
        # aria-hidden 只对读屏软件隐藏,不对人隐藏:标签页、轮播常这么写(11-05 第三轮留出站 fly.io/sprites/
        # 的功能标签页被误判成隐藏指令),所以不算
        hid = HIDDEN_STYLE.search(a.get("style") or "") is not None or "hidden" in a
        self.stack.append((tag, hid))
        if hid:
            self.depth += 1
            self.chunks.append("")
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _, hid in self.stack[i:]:
                    self.depth -= hid
                del self.stack[i:]
                return
    def handle_data(self, d):
        if self.depth > 0 and self.chunks:
            self.chunks[-1] += d
    def handle_comment(self, d):
        self.chunks.append(d)


def agent_directives(html):
    """→ 隐藏元素 / 注释里对 AI 下指令的原文列表(去空白,每条最多 300 字)。"""
    p = _Hidden()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001 — 坏 HTML 不该让整页审计崩
        pass
    out = []
    for c in p.chunks:
        t = re.sub(r"\s+", " ", c).strip()
        if t and AGENT_DIRECTIVE.search(t) and t[:300] not in out:
            out.append(t[:300])
    return out


def visible_text(html):
    """去 script/style/noscript/注释与标签后的可见文本(空白折叠)。"""
    body = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<noscript[^>]*>.*?</noscript>"
                  r"|<!--.*?-->", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()

def looks_like_challenge(html):
    """挑战页/拦截页判定(S2a B11:结构特征,见 CHALLENGE_* 常量注释)。"""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    title = re.sub(r"\s+", " ", m.group(1)).strip().lower() if m else ""
    if title.startswith(CHALLENGE_TITLES):
        return True
    if CHALLENGE_ATTRS.search(html) or CHALLENGE_JS.search(html):
        return True
    text = visible_text(html)
    if len(text) < CHALLENGE_MAX_TEXT:
        low = (title + " " + text).lower()
        if any(p in low for p in CHALLENGE_PHRASES):   # 只有 challenge-platform 脚本不算:JS Detections 每页都注入,
            return True                                 # 11-05 留出站阮一峰首页、/blog/(中文短页)被误判拒审
    return False

def load_market(market):
    """markets.json 市场规则(与 market_lint.py 同源);未知市场 stderr+exit 2(S5 修复⑧)。"""
    with open(os.path.join(BASE, "markets.json"), encoding="utf-8") as f:
        ms = json.load(f)["markets"]
    if market not in ms:
        sys.stderr.write("未知市场 %s;可用: %s\n" % (market, ", ".join(ms)))
        sys.exit(2)
    return ms[market]

TITLE_MIN = 20   # title 过短下限(市场单位;本套件口径,Google 无字数下限)

def desc_bounds(mk):
    """description 长度区间 (下限, 上限),同 desc_limit 单位(S2a B13)。
    下限取 markets.json desc_min;缺省为上限的一半;强制 0 < 下限 < 上限
    (旧版下限 80 写死:zh 上限 78 时任何长度都过不了)。本套件口径——Google 对描述无长度要求。"""
    hi = mk["desc_limit"]["value"]
    lo = mk.get("desc_min")
    if not isinstance(lo, int) or isinstance(lo, bool) or not 0 < lo < hi:
        lo = max(1, hi // 2)
    return lo, hi

def text_limits(market, mk=None):
    """--json 顶层 limits 节:本次审计实际用的 title/description 区间(prioritize/envelope
    据此写修复文案,不再各写一套 50-60/~155)。"""
    mk = mk or load_market(market)
    tl = mk["title_limit"]
    lo, hi = desc_bounds(mk)
    return {"title": {"unit": tl["unit"], "min": TITLE_MIN, "max": tl["value"],
                      "ideal_min": tl.get("ideal_min")},
            "description": {"unit": mk["desc_limit"]["unit"], "min": lo, "max": hi}}

def unit_len(s, unit):
    """按市场单位计长:chars=len()/fullwidth=EAW W/F 计 1 其余 0.5 向上取整/
    grapheme=combining==0 且非 Mn/Cf(泰文字素近似,组合元音/声调符不独立计数)。"""
    if unit == "fullwidth":
        return math.ceil(sum(1.0 if unicodedata.east_asian_width(c) in ("W", "F") else 0.5 for c in s))
    if unit == "grapheme":
        # SARA AM(U+0E33/U+0EB3)是 SpacingMark,并入前字(与 Intl.Segmenter 一致,B53 同类修)
        return sum(1 for c in s if unicodedata.combining(c) == 0
                   and unicodedata.category(c) not in ("Mn", "Mc", "Me", "Cf")
                   and c not in "\u0e33\u0eb3")
    return len(s)

def is_cjk(ch):
    o = ord(ch)
    return 0x4E00 <= o <= 0x9FFF or 0x3040 <= o <= 0x30FF or 0xAC00 <= o <= 0xD7AF

def is_thai(ch):
    return 0x0E00 <= ord(ch) <= 0x0E7F

def is_devanagari(ch):
    return 0x0900 <= ord(ch) <= 0x097F

def is_grapheme_base(ch):
    """字素近似基字符(markets.json units.grapheme 口径)——泰文组合标记不计。"""
    return unicodedata.combining(ch) == 0 and unicodedata.category(ch) not in ("Mn", "Cf")

def wc_info(text):
    """词数 + 是否近似(B47 修,2026-10-21)→ (count, approx)。
    - CJK(汉字/假名/谚文)逐字计(每字≈一词,本套件口径);
    - 其余文字按 Unicode 词边界近似:字母/数字连续段为一词,组合符号(Mn/Mc/Me)附着在词内,
      空格与标点断词(UAX #29 在空格处断开)。天城体的 matra(Mc)与 virama(Mn)不再断词,
      「बेस्ट लैपटॉप कैसे खरीदें」=4(修前逐码点计 21);拉丁/西里尔/阿拉伯/希腊同此口径;
    - 泰文不用空格分词,stdlib 没有词典分词:按空格分隔的短语计数,approx=True(修前返回字素数,
      量纲不对)。精确分词需 Intl.Segmenter('th') 或 ICU;
    - 土耳其 İ:先 replace('İ','i') 再清洗 U+0307 组合点(避免分解形 I+U+0307 劈词)。"""
    text = text.replace("İ", "i").replace("I\u0307", "i").replace("\u0307", "")
    perchar = words = 0
    approx = False
    prev = False  # 前一字符是否处于词内
    for c in text:
        if is_cjk(c):
            perchar += 1
            prev = False
            continue
        cat = unicodedata.category(c)
        if is_thai(c):
            approx = True
        is_l = cat[0] in ("L", "N")
        if is_l and not prev:
            words += 1
        prev = is_l or ((c in "'’" or cat[0] == "M") and prev)
    return perchar + words, approx


def wc(text):
    """词数(见 wc_info;泰文为空格短语近似数)。"""
    return wc_info(text)[0]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.desc, self.canonical, self.lang = [], None, None, None
        self.h1, self.headings, self.meta_robots = 0, [], None
        self.og, self.links, self.imgs, self.img_noalt = {}, 0, 0, 0
        self.jsonld, self.ld_buf = 0, []
        self.in_head, self.meta_props = True, {}
        self.in_title = self.in_script = self.script_ld = False
        # S3:AI Search Health + rendering 5 检查所需信号
        self.semantic_tags, self.all_tags, self.sem_counts = 0, 0, {}
        self.li_count = 0
        self.ext_scripts, self.inline_js_bytes = 0, 0
        self.script_inline = False
        self.mounts, self.ssr_amnesty = set(), False   # CSR 挂载点 / SSR 赦免(__NEXT_DATA__·data-reactroot)
        self.in_noscript, self.noscript_text = False, []
        self.meta_last_modified = None                 # <meta http-equiv="Last-Modified" content=...>(头缺失时回退)
        self.meta_agents = {}                          # name=googlebot/bingbot/… 的 robots 指令(按爬虫名)
        self.embeds = []                               # <embed>/<object>/<applet>(Lighthouse plugins 口径)
        self._obj = None                               # 当前 <object>,收 <param>
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.all_tags += 1
        if tag in SEMANTIC_TAGS:
            self.semantic_tags += 1
            self.sem_counts[tag] = self.sem_counts.get(tag, 0) + 1
        tid = a.get("id")
        if tid in MOUNT_IDS: self.mounts.add(tid)
        if tid == "__NEXT_DATA__" or "data-reactroot" in a: self.ssr_amnesty = True
        if tag == "li": self.li_count += 1
        if tag == "noscript": self.in_noscript = True
        if tag == "html": self.lang = a.get("lang")
        if tag == "head": self.in_head = True
        if tag == "title" and self.in_head:
            self.title.append("")
            self.in_title = True
        if tag == "script":
            self.in_script = True
            self.script_ld = "ld+json" in (a.get("type") or "")
            self.script_inline = not self.script_ld and not a.get("src")
            if a.get("src"): self.ext_scripts += 1
            if self.script_ld: self.ld_buf = []
        if tag == "meta":
            k = a.get("name") or a.get("property") or ""
            v = a.get("content") or ""
            self.meta_props[k.lower()] = v
            if k.lower() == "description": self.desc = v
            if k.lower() == "robots": self.meta_robots = v
            if k.lower() in BOT_META_NAMES: self.meta_agents[k.lower()] = v
            if k.lower().startswith("og:"): self.og[k.lower()] = v
            if (a.get("http-equiv") or "").lower() == "last-modified":
                self.meta_last_modified = a.get("content")
        if tag == "link" and a.get("rel") == "canonical": self.canonical = a.get("href")
        if tag in ("embed", "object", "applet"):
            item = {"tag": tag, "type": a.get("type") or "", "src": a.get("src") or "",
                    "code": a.get("code") or "", "data": a.get("data") or "", "params": []}
            self.embeds.append(item)
            if tag == "object": self._obj = item
        if tag == "param" and self._obj is not None:
            self._obj["params"].append(((a.get("name") or ""), (a.get("value") or "")))
        if tag in ("h1",): self.h1 += 1
        if re.fullmatch(r"h[1-6]", tag): self.headings.append(int(tag[1]))
        if tag == "a" and a.get("href", "").startswith(("http", "/", "#")): self.links += 1
        if tag == "img":
            self.imgs += 1
            # 只有没有 alt 属性才算缺失;alt="" 是装饰图的正确写法(W3C WAI Decorative Images)
            if "alt" not in a: self.img_noalt += 1
        if tag == "body": self.in_head = self.in_title = False
    def handle_endtag(self, tag):
        if tag == "object": self._obj = None
        if tag == "title": self.in_title = False
        if tag == "script":
            if self.script_ld:
                self.jsonld += 1
                self.script_ld = False
            self.script_inline = False
            self.in_script = False
        if tag == "noscript": self.in_noscript = False
        if tag == "head": self.in_head = self.in_title = False
    def handle_data(self, d):
        # S2 修复:title 只收集 <title>…</title> 内的文本——head 内 script/JSON-LD/
        # style 的数据一律不吞(此前 title 开过后 head 内全部裸文本都被拼进 title,
        # 6+ 站触发 2-75 万字符假 title)。
        if self.in_script:
            if self.script_ld: self.ld_buf.append(d)
            elif self.script_inline: self.inline_js_bytes += len(d)
            return
        if self.in_noscript: self.noscript_text.append(d)
        if self.in_title and self.title:
            self.title[-1] = (self.title[-1] or "") + d

def get_header(hdrs, name):
    """大小写不敏感取响应头(dict(r.headers) 键大小写随服务器)。"""
    for k, v in (hdrs or {}).items():
        if k.lower() == name.lower():
            return v
    return None

def norm_host(u):
    """URL host 归一(S5 修复⑥):netloc 小写 + 去协议默认端口(https→443/http→80)。
    canonical 外域比较口径——https://Example.COM:443/ 与 https://example.com/ 同源,
    不再因大小写/显式默认端口误报"指向外域"。"""
    pu = urlparse(u)
    netloc = (pu.netloc or "").lower()
    host, _, port = netloc.rpartition(":")
    if host and port.isdigit():
        if (pu.scheme == "https" and port == "443") or (pu.scheme == "http" and port == "80"):
            return host
    return netloc

def parse_robots_groups(txt):
    """自写 robots.txt 解析(RFC 9309 简化):BOM 剥离/注释剥离/连续 User-agent 行合并同组/
    规则后出现的 User-agent 开新组/Sitemap·Crawl-delay 等忽略。
    返回 {ua小写: [(前缀长, 是否Allow, 前缀小写), ...]};不支持 * $ 通配(按字面前缀处理)。"""
    groups, uas, seen_rule = {}, [], False
    for raw in txt.lstrip("\ufeff").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if seen_rule:
                uas, seen_rule = [], False
            if v:
                uas.append(v.lower())
                groups.setdefault(v.lower(), [])
        elif k in ("allow", "disallow") and uas:
            seen_rule = True
            for ua in uas:
                groups[ua].append((len(v), k == "allow", v.lower()))
    return groups

def robots_allows(groups, ua, url):
    """最长匹配判定:bot 专属组优先于 *;组内取匹配路径的最长前缀规则(同长 Allow 胜);
    无匹配规则/无组 → 默认放行(urllib.robotparser 首条命中即返回,这里改为 RFC 9309 最长匹配)。
    S5 修复①:专属组存在但为空(仅 User-agent 行、无规则)时该组即生效=不受限——
    用 `key in groups` 判存在性,不再 `or` 回落 * 组(此前空组 falsy 被吞 → 误用通配组
    规则 → 假 CRITICAL,违背 RFC 9309)。"""
    if not groups:
        return True
    key = ua.lower()
    rules = groups[key] if key in groups else groups.get("*", [])
    pu = urlparse(url)
    path = (pu.path or "/") + (("?" + pu.query) if pu.query else "")
    best_len, allowed = -1, True
    for rlen, is_allow, prefix in rules:
        if prefix and path.lower().startswith(prefix):
            if rlen > best_len or (rlen == best_len and is_allow):
                best_len, allowed = rlen, is_allow
    return allowed

def last_modified_days(hdrs, meta_lm):
    """Last-Modified 距今天数:响应头优先,缺失回退 meta http-equiv;都没有/解析失败 → None(跳过)。"""
    v = get_header(hdrs, "last-modified") or meta_lm
    if not v:
        return None
    try:
        dt = parsedate_to_datetime(v)          # RFC 2822:"Wed, 21 Oct 2015 07:28:00 GMT"
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(v.strip())
        except (TypeError, ValueError):
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)          # S5 修复④:naive 值按 UTC 口径补 tz
    return max(0, (datetime.now(timezone.utc) - dt).days)   # 与 now 统一 timezone.utc,不再与本地 naive 混 8h

def semantic_ratio(sem_count, all_count):
    """语义 HTML 比值 = 语义标签数 ÷ 非语义标签数(Semrush 口径;<10% 触发,阈值自定[推断]官方未公开)。
    非语义=0 时:有语义标签→1.0(全语义),否则 0.0。"""
    non = all_count - sem_count
    if non > 0:
        return sem_count / non
    return 1.0 if sem_count > 0 else 0.0

def bluf_score(plain, li_count):
    """BLUF 密度(geo-aeo-tracker 源码公式):first_chunk=前 max(20%×文本长, 400) 字符;
    score=min(1,(直答短语命中 + li数>3 + 首块>100字)/2);pass≥0.5。返回 (score, detail)。"""
    if not plain:
        return 0.0, "无纯文本"
    chunk = plain[:max(int(len(plain) * 0.2), 400)]
    phrase = bool(BLUF_RE.search(chunk))
    lis = li_count > 3
    first_long = len(chunk) > 100
    score = min(1.0, (phrase + lis + first_long) / 2)
    detail = (f"首块 {len(chunk)} 字({'>' if first_long else '≤'}100),"
              f"直答短语{'命中' if phrase else '未见'},li {li_count} 个({'>' if lis else '≤'}3)")
    return score, detail

def detect_csr(page, plain, html_len):
    """CSR 检测(geo-aeo-tracker 源码口径):存在空挂载点 #root/#app/#__next/#svelte 且
    (纯文本<200 字 或 text/HTML 比<0.02);有 __NEXT_DATA__/data-reactroot → SSR 赦免返回 None。"""
    if page.ssr_amnesty or not page.mounts:
        return None
    ratio = (len(plain) / html_len) if html_len else 0.0
    if len(plain) < 200 or ratio < 0.02:
        return {"mounts": sorted(page.mounts), "text_chars": len(plain), "ratio": round(ratio, 4)}
    return None

def ai_health_score(checks):
    """AI Search Health 子分(0-100):通过率加权 Σ(权重×pass);
    bluf 进 checks 仅记录不参与计分(权重表无该项)[推断]。"""
    by_id = {c["id"]: c["pass"] for c in checks}
    return round(100 * sum(w for k, w in AI_HEALTH_WEIGHTS.items() if by_id.get(k)))

# ---- S4:具名 bulk export + 受影响面(borrow-specs A2,SF/Sitebulb 口径) ----
SEV_RANK = {"SKIP": 0, "INFO": 1, "WARN": 2, "CRITICAL": 3}
# 规则简名表:(area, message 子串) → 完整导出 slug(即 {area}-{规则简名});自上而下
# 首个 area 相符且 message 含子串者生效;site_audit 新增检查未登记时走 rule_slug 的
# fallback(area+message 首个 ASCII 词素),同一 slug 冲突自动合并(SF bulk export 口径)。
RULE_SLUGS = [
    ("staging", "staging 子域", "staging-subdomain"),
    ("title", "缺失", "title-missing"),
    ("title", "超上限", "title-too-long"),
    ("title", "<20", "title-too-short"),
    ("title", "搜索结果显示的标题不一致", "title-serp-mismatch"),
    ("description", "缺失", "description-missing"),
    ("description", "超上限", "description-too-long"),
    ("description", "低于下限", "description-too-short"),
    ("description", "<80", "description-too-short"),          # 旧版消息(读旧审计文件时同一 slug)
    ("h1", "无 H1", "h1-missing"),
    ("h1", "个 H1", "h1-multiple"),
    ("headings", "第一个 h1 之前", "headings-before-h1"),
    ("headings", "跳级", "headings-skip-level"),
    ("headings", "H2 仅", "headings-h2-few"),
    ("canonical", "相对 URL", "canonical-relative"),
    ("canonical", "指向外域", "canonical-external"),
    ("canonical", "缺失", "canonical-missing"),
    ("robots", "bingbot noindex", "robots-bingbot-noindex"),
    ("robots", "bingbot 专属", "robots-bingbot-only"),
    ("robots", "max-video-preview", "robots-max-video-preview"),
    ("robots", "noindex", "robots-noindex"),
    ("robots", "nosnippet", "robots-nosnippet"),
    ("og", "og:image 非绝对", "og-image-not-absolute"),
    ("og", "og:url 非绝对", "og-url-not-absolute"),
    ("og", "og:title", "og-title-missing"),
    ("og", "og:description", "og-description-missing"),
    ("og", "og:image", "og-image-missing"),
    ("a11y", "无 lang", "a11y-no-lang"),
    ("viewport", "没有", "viewport-missing"),
    ("viewport", "没写 width", "viewport-no-width"),
    ("content", ">15000", "content-too-long"),
    ("content", "<200", "content-thin"),
    ("links", ">100", "links-too-many"),
    ("images", "alt 缺失", "images-alt-missing"),
    ("schema", "无 JSON-LD", "schema-jsonld-missing"),
    ("rendering", "插件", "rendering-plugins"),
    ("rendering", "CSR", "rendering-csr"),
    ("rendering", "noscript", "rendering-no-noscript"),
    ("rendering", "JS 重量", "rendering-js-heavy"),
    ("rendering", "服务端内容弱", "rendering-weak-server-content"),
    ("bluf", "BLUF", "bluf-low"),
    ("robots", "不可达", "robots-unreachable"),
    ("sitemap", "不可达", "sitemap-unreachable"),
    ("llms.txt", "不可达", "llms-txt-unreachable"),
    ("ai-bots", "训练型", "ai-bots-training-blocked"),
    ("ai-bots", "被禁", "ai-bots-blocked"),
    ("freshness", "天前", "freshness-stale"),
    ("semantic-html", "比值", "semantic-html-low"),
]

def _slugify(s):
    """文件名安全 slug:小写,非 [a-z0-9] 段折叠为 '-',去首尾 '-'。"""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

def rule_slug(area, msg):
    """area+message → 稳定导出 slug(具名 bulk export 文件名,SF 口径):
    RULE_SLUGS 表先匹配(自上而下首中);未登记的新规则 fallback 为
    '{area}-{message 首个 ASCII 词素}';纯 CJK 消息无 ASCII 词素时退为 area 本身。
    同一输入恒得同一 slug;不同来源撞同一 slug 时在聚合层合并。"""
    for a, needle, slug in RULE_SLUGS:
        if a == area and needle in msg:
            return slug
    m = re.match(r"[A-Za-z0-9][A-Za-z0-9_.:/-]*", msg.strip())
    tail = _slugify(m.group(0)) if m else ""
    return _slugify(f"{area}-{tail}") if tail else _slugify(area)

def aggregate_rules(by_url):
    """逐 URL findings → 规则聚合表 {slug: {severity, area, example, urls}}:
    SKIP(fetch guard 拒审)不是规则不进表;受影响 URL 按审计顺序去重;
    同 slug 多来源合并,severity 取最高。"""
    rules = {}
    for url, findings in by_url.items():
        for sev, area, msg in findings:
            if sev == "SKIP":
                continue
            slug = rule_slug(area, msg)
            r = rules.get(slug)
            if r is None:
                rules[slug] = {"severity": sev, "area": area, "example": msg, "urls": [url]}
                continue
            if SEV_RANK.get(sev, 0) > SEV_RANK.get(r["severity"], 0):
                r["severity"] = sev
            if url not in r["urls"]:
                r["urls"].append(url)
    return rules

def sorted_rules(rules):
    """导出与表格统一排序:severity 降序 → 受影响数降序 → slug 字典序(确定性)。"""
    return sorted(rules.items(),
                  key=lambda kv: (-SEV_RANK.get(kv[1]["severity"], 0),
                                  -len(kv[1]["urls"]), kv[0]))

def fmt_pct(n, m):
    """受影响面百分比:N/M → '60%'/'33.3%'(一位小数,整数不带小数点;m<=0 → '0%')。"""
    if m <= 0:
        return "0%"
    s = f"{100.0 * n / m:.1f}".rstrip("0").rstrip(".")
    return (s or "0") + "%"

def coverage_str(n, m):
    """受影响面列文本:'N/M 页(XX%)'(SF Coverage 口径,分母=已审计页数)。"""
    return f"{n}/{m} 页({fmt_pct(n, m)})"

def render_findings_markdown(rules, total):
    """人读报告 findings 汇总(markdown 表):规则×级别×受影响面三列;
    受影响面=SF Coverage 口径的简化——分母用本次已审计页数而非全站页数,表头注明。"""
    lines = [f"## findings 汇总(受影响面;分母=本次已审计 {total} 页,拒审已剔除,非全站)",
             "| 规则 | 级别 | 受影响面 |", "| --- | --- | --- |"]
    for slug, r in sorted_rules(rules):
        lines.append(f"| {slug} | {r['severity']} | {coverage_str(len(r['urls']), total)} |")
    return "\n".join(lines)

def write_exports(export_dir, rules, total):
    """具名 bulk export(SF/Sitebulb 口径):每 rule 一份受影响 URL 清单 '{slug}.txt'
    (一行一 URL,审计顺序去重)+ summary.json(每 rule:slug/受影响数/占比/severity,
    外加 area/coverage_pct/file/example_message 与分母声明)。目录不存在则创建;
    已存在直接覆盖写(输出目录由调用方隔离,套件惯例)。返回已写文件名列表。"""
    os.makedirs(export_dir, exist_ok=True)
    files = []
    ordered = sorted_rules(rules)
    for slug, r in ordered:
        name = slug + ".txt"
        with open(os.path.join(export_dir, name), "w", encoding="utf-8") as f:
            f.write("\n".join(r["urls"]) + "\n")
        files.append(name)
    summary = {
        "denominator_note": "coverage 分母=本次已审计页数(SF Coverage 口径简化:非全站页数;拒审([SKIP])页剔除)",
        "audited": total,
        "rules": [{"slug": slug, "area": r["area"], "severity": r["severity"],
                   "affected": len(r["urls"]),
                   "coverage": round(len(r["urls"]) / total, 4) if total else 0.0,
                   "coverage_pct": fmt_pct(len(r["urls"]), total),
                   "file": slug + ".txt",
                   "example_message": r["example"]} for slug, r in ordered]}
    with open(os.path.join(export_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    files.append("summary.json")
    return files

# ---- 页面 title 与搜索结果标题不一致(Ahrefs「Page and SERP titles do not match」,Content 报告
# notice;https://ahrefs.com/blog/site-audit-study/:Google 显示的标题和页面 title 不同,即标题被改写)。
# 搜索结果里显示的标题只能从 SERP 数据拿:GSC Search Analytics API 只回 query/page/clicks 等,
# 不回标题,所以没有 --serp-titles 文件时不比、写明跳过原因,不猜。
SERP_SKIP_REASON = ("未提供 --serp-titles(搜索结果里显示的标题只能来自 SERP 导出;"
                    "GSC Search Analytics API 不返回标题),title 与 SERP 标题一致性未检查")


def _url_key(u):
    pu = urlparse((u or "").strip())
    path = (pu.path or "/").rstrip("/") or "/"
    return f"{norm_host(u)}{path}{('?' + pu.query) if pu.query else ''}"


def load_serp_titles(path):
    """SERP 标题文件 → {url_key: 标题}。认 CSV(表头含 url/page/link 与 title/serp_title)、
    JSON 列表 [{url,title}] 或 JSON 对象 {url: title}。"""
    import csv
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()
    out = {}
    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    if isinstance(data, dict):
        pairs = list(data.items())
    elif isinstance(data, list):
        pairs = [(d.get("url") or d.get("page") or d.get("link"), d.get("title") or d.get("serp_title"))
                 for d in data if isinstance(d, dict)]
    else:
        rows = list(csv.DictReader(raw.splitlines()))
        pairs = []
        for r in rows:
            low = {(k or "").strip().lower(): v for k, v in r.items()}
            pairs.append((low.get("url") or low.get("page") or low.get("link"),
                          low.get("serp_title") or low.get("title")))
    for u, t in pairs:
        if u and t:
            out[_url_key(u)] = str(t)
    return out


def serp_title_matches(page_title, serp_title):
    """一致判据:空白折叠、大小写不敏感后相等;或 SERP 标题以 ... / … 结尾(显示截断)且页面 title
    以截断前的部分开头。其余算不一致(含 Google 追加站点名、改写措辞)。"""
    norm = lambda x: re.sub(r"\s+", " ", (x or "")).strip().lower()
    a, b = norm(page_title), norm(serp_title)
    if a == b:
        return True
    stem = re.sub(r"\s*(\.\.\.|…)$", "", b)
    return stem != b and bool(stem) and a.startswith(stem)


def audit(url, market="en", serp_titles=None):
    F = []  # (severity, area, msg)
    mk = load_market(market)
    tl, dl = mk["title_limit"], mk["desc_limit"]
    host = urlparse(url).netloc.lower()
    if host.startswith(STAGING): F.append(("CRITICAL", "staging", "staging 子域公开可访问"))
    try:
        st, hdrs, html = fetch(url)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429, 503):
            return [("SKIP", "fetch guard",
                     f"response too small / likely challenge page (HTTP {e.code}); refusing to audit")], {}, None
        return [("CRITICAL", "fetch", f"{e}")], {}, None
    except Exception as e:
        return [("CRITICAL", "fetch", f"{e}")], {}, None
    # fetch 质量守卫:<200 bytes 或挑战页特征 → 拒绝审计结论([SKIP],不报 CRITICAL)
    if len(html.strip()) < MIN_BODY_BYTES:
        return [("SKIP", "fetch guard",
                 f"response too small / likely challenge page ({len(html)} bytes, HTTP {st}); refusing to audit")], {}, None
    if looks_like_challenge(html):
        return [("SKIP", "fetch guard",
                 f"response too small / likely challenge page (challenge markers, HTTP {st}); refusing to audit")], {}, None
    p = Page(); p.feed(html)
    t = re.sub(r"\s+", " ", (p.title[0] if p.title else "")).strip()
    tn = unit_len(t, tl["unit"])
    if not t: F.append(("CRITICAL", "title", "缺失"))
    elif tn < TITLE_MIN: F.append(("WARN", "title", f"{tn} {tl['unit']} <{TITLE_MIN}"))
    elif tn > tl["value"]:
        F.append(("WARN", "title", f"{tn} {tl['unit']} 超上限 {tl['value']}({tl.get('note', '')})"))
    if serp_titles is None:
        serp_check = {"checked": False, "reason": SERP_SKIP_REASON}
    else:
        st_serp = serp_titles.get(_url_key(url))
        serp_check = ({"checked": True, "serp_title": st_serp, "match": serp_title_matches(t, st_serp)}
                      if st_serp is not None else {"checked": False, "reason": "--serp-titles 文件里没有这个 URL"})
    if t and serp_check.get("checked") and not serp_check["match"]:
        F.append(("INFO", "title", f"与搜索结果显示的标题不一致: 页面「{t[:50]}」/ SERP「{serp_check['serp_title'][:50]}」"
                  "(Google 改写了标题;Ahrefs Page and SERP titles do not match)"))
    dn = unit_len(p.desc or "", dl["unit"])
    d_lo, d_hi = desc_bounds(mk)
    # S2a B15:描述可选——Google 主要从正文生成摘要(snippet 文档),缺失记 WARN 不记 CRITICAL
    if p.desc is None: F.append(("WARN", "description", "缺失"))
    elif dn < d_lo: F.append(("WARN", "description", f"{dn} {dl['unit']} 低于下限 {d_lo}(本套件口径)"))
    elif dn > d_hi:
        F.append(("WARN", "description", f"{dn} {dl['unit']} 超上限 {d_hi}"))
    # S2a B38:SEO 起始指南——标题数量与顺序对 Google 搜索无影响;缺 H1 记 WARN
    if p.h1 == 0: F.append(("WARN", "h1", "无 H1"))
    elif p.h1 > 1: F.append(("WARN", "h1", f"{p.h1} 个 H1"))
    # 第一个 h1 之前出现低级标题(h3–h6)且前面没有它的上一级:标题树从中间开始。W3C WAI Headings
    # 教程(https://www.w3.org/WAI/tutorials/page-structure/headings/):「Skipping heading ranks can be
    # confusing and should be avoided」;「Main heading after navigation」写法允许 h1 前出现与正文同级的
    # 结构标题(h2),所以 h1 前只认 h2 起头,h3 起头算跳级。plausible 首页 h3 h3 h3 h1 h2 实测漏报(2026-11-05)。
    first_h1 = p.headings.index(1) if 1 in p.headings else None
    pre = p.headings[:first_h1] if first_h1 else []
    pre_hit = None
    for i, h in enumerate(pre):
        prev = pre[i - 1] if i else 1          # h1 前的结构标题按「h1 之下」起算
        if h - prev > 1:
            pre_hit = h
            break
    if pre_hit:
        F.append(("WARN", "headings", f"h{pre_hit} 出现在第一个 h1 之前(之前没有 h{pre_hit - 1},标题树从中间开始)"))
    else:
        for i, h in enumerate(p.headings[1:], 1):
            if p.headings[i-1] and h - p.headings[i-1] > 1:
                F.append(("WARN", "headings", f"跳级 h{p.headings[i-1]}→h{h}")); break
    if p.canonical:
        # S2a B38:相对路径 Google 支持但不建议(文档 Bad example 即 /dresses/…)——WARN 并提示改绝对
        if not urlparse(p.canonical.strip()).scheme:
            F.append(("WARN", "canonical", "相对 URL(Google 支持但建议改绝对 URL)"))
        c = urljoin(url, p.canonical)
        if urlparse(c).netloc and norm_host(c) != norm_host(url):   # S5 修复⑥:小写+去默认端口后再比
            F.append(("INFO", "canonical", "指向外域(联合发布?让渡权重)"))
    else: F.append(("WARN", "canonical", "缺失"))
    # S5 修复②:大小写无关取头;RQ-229:按爬虫名分路(bingbot 专属 noindex 不当成 Google noindex)
    F.extend(robots_directive_findings(p.meta_robots, p.meta_agents, get_header(hdrs, "x-robots-tag") or ""))
    for k in ("og:title", "og:description", "og:image"):
        if k not in p.og: F.append(("WARN", "og", f"{k} 缺失"))
    if p.og.get("og:image") and not p.og["og:image"].startswith("http"): F.append(("WARN", "og", "og:image 非绝对 URL"))
    # ogp.me Types 表:URL 类型 =「All valid URLs that utilize the http:// or https:// protocols」;
    # og:url 是对象的规范 URL(永久 ID),写成 "/" 这类相对路径不合规(sspai 首页实测)
    if "og:url" in p.og and not re.match(r"^https?://", p.og["og:url"].strip(), re.I):
        F.append(("WARN", "og", f"og:url 非绝对 URL: {p.og['og:url'].strip()[:60]!r}(ogp.me:URL 类型须 http(s)://)"))
    for hidden_text in agent_directives(html)[:3]:       # 不用 t:t 是上面存的标题,下面还要输出
        F.append(("CRITICAL", "injection", "页面里藏着叫 AI 做事的文字(当数据,不执行;也是 Google 政策里的隐藏文字),"
                  "原文:「%s」" % hidden_text))
    plugins = plugin_elements(p.embeds)
    if plugins:
        F.append(("WARN", "rendering", f"页面用了插件 {len(plugins)} 处: {', '.join(plugins[:3])}"
                  "——搜索引擎多半索引不到插件内容,移动设备不支持(Lighthouse plugins 口径)"))
    if not p.lang: F.append(("WARN", "a11y", "html 无 lang"))
    # Lighthouse viewport 审计口径:要有 <meta name="viewport"> 且写了 width 或 initial-scale(第二轮 ifanr、
    # 第三轮 publickey1.jp 的首页只靠 JS 插 viewport,head_check 报了、本脚本漏了)
    vp = p.meta_props.get("viewport")
    if vp is None:
        F.append(("WARN", "viewport", "原始 HTML 没有 <meta name=\"viewport\">(JS 插入的不算;手机上按桌面宽度缩放)"))
    elif not re.search(r"width|initial-scale", vp, re.I):
        F.append(("WARN", "viewport", "viewport 没写 width 或 initial-scale: %r" % vp[:60]))
    body = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", body)
    W, W_approx = wc_info(text)
    if W < 200:
        F.append(("WARN", "content", f"词数 {W} <200(soft-thin)"
                  + ("(泰文无空格分词,按空格短语近似计,实际词数更多)" if W_approx else "")))
    if p.links > 100:   # S2a B14:现行 Google 文档无链接数上限;100 是工具约定,只提示
        F.append(("INFO", "links", f"{p.links} 链接 >100(工具约定,非 Google 要求)"))
    if p.imgs and p.img_noalt / p.imgs > 0.2: F.append(("WARN", "images", f"alt 缺失 {p.img_noalt}/{p.imgs}"))
    if p.jsonld == 0: F.append(("WARN", "schema", "无 JSON-LD"))
    # ---- rendering 5 检查(geo-aeo-tracker 源码口径;全部 WARN/INFO 级,不产生 CRITICAL) ----
    plain = re.sub(r"\s+", " ", text).strip()   # 规范化纯文本(字符类指标用)
    h2n = sum(1 for h in p.headings if h == 2)
    csr = detect_csr(p, plain, len(html))
    if csr:
        F.append(("WARN", "rendering",
                  f"CSR 疑似:空挂载点 {csr['mounts']} 且纯文本 {csr['text_chars']} 字/"
                  f"text-HTML 比 {csr['ratio']}(阈值:文本<200 字或比值<0.02)——AI 爬虫多不执行 JS"))
    nos = re.sub(r"\s+", " ", "".join(p.noscript_text)).strip()
    # S2a B3:已检测到服务端内容 → 无 JS 客户端拿到的不是空页;JS 只提示体积,不给改渲染建议
    # 只看纯文本量:11-05 留出站 buttondown 两页原始 HTML 已有 4,809 / 4,098 字正文,只因没用 article/main/section
    # 就被说成「无 JS 拿到空页」。语义标签是否齐全由上面的结构检查管,不在这里重复判。
    server_content = len(plain) > 500
    if len(nos) <= 20 and not server_content:
        F.append(("INFO", "rendering", "无 noscript 回退(或去标签文本≤20 字)——无 JS 客户端拿到空页"))
    if p.ext_scripts > 15 or p.inline_js_bytes > 100 * 1024:
        js = f"JS 重量:外部 script {p.ext_scripts} 个(>15)/内联 JS {p.inline_js_bytes // 1024}KB(>100KB)"
        if server_content:
            F.append(("INFO", "rendering",
                      js + f"——已检测到服务端内容(纯文本 {len(plain)} 字),只提示体积,无需改渲染方式"))
        else:
            F.append(("WARN", "rendering", js + "——易超 AI 爬虫抓取预算"))
    if not server_content:
        F.append(("INFO", "rendering",
                  f"服务端内容弱:纯文本 {len(plain)} 字(需>500)"))
    if h2n < 2:  # 检查项为 H1==1 且 H2>=2;H1 问题上方既有检查已按自身级别报告,此处只补 H2 缺口
        F.append(("INFO", "headings", f"H2 仅 {h2n} 个(<2)——AI 分块依赖标题层级(H1==1 且 H2>=2)"))
    # ---- BLUF 密度(geo-aeo-tracker 源码公式;失败出 INFO,并进 ai_search_health.checks) ----
    b_score, b_detail = bluf_score(plain, p.li_count)
    if b_score < 0.5:
        F.append(("INFO", "bluf", "BLUF 密度不足,答案前置可提升 AI 引用"))
    # ---- 根文件:robots.txt(8 bot 名单判定)/sitemap/llms.txt ----
    root = f"{urlparse(url).scheme}://{host}"
    robots_groups, llms_ok = {}, False
    declared_sitemaps = []
    for path, name in (("/robots.txt", "robots"), ("/sitemap.xml", "sitemap"), ("/llms.txt", "llms.txt")):
        target = root + path
        if name == "sitemap" and declared_sitemaps:
            # robots.txt 声明了 sitemap 就查声明的那个(Google 认这种发现方式);11-05 留出站 zenn 的 sitemap 在
            # /sitemaps/_index.xml,只找 /sitemap.xml 每页都报「不可达」
            target = path = declared_sitemaps[0]
        try:
            s2, _, body2 = fetch(target)
            if s2 == 200 and name == "robots":
                robots_groups = parse_robots_groups(body2)
                declared_sitemaps = re.findall(r"(?im)^\s*sitemap\s*:\s*(\S+)", body2 or "")
            if s2 == 200 and name == "llms.txt":
                llms_ok = True
        except urllib.error.HTTPError as e:
            if name == "robots" and e.code == 404:
                continue   # S5 修复⑦:RFC 9309——robots.txt 404=不存在=全放行,不产 finding
            F.append(("INFO", name, f"{path} 不可达(HTTP {e.code})"))   # path 自带单斜杠,不再拼出 //
        except Exception:
            F.append(("INFO", name, f"{path} 不可达"))
    allowed, blocked = [], []
    for b in SEARCH_BOTS:
        (allowed if robots_allows(robots_groups, b, url) else blocked).append(b)
    for b in blocked:
        if b == "Google-Extended":
            F.append(("WARN", "ai-bots",
                      "Google-Extended 被禁——robots token 非爬虫(单列),影响 Gemini 训练/落地引用"))
        else:
            F.append(("CRITICAL", "ai-bots", f"{b} 被禁——逐出该 AI 答案"))
    for b in TRAINING_BOTS:  # 训练型:不影响搜索可见性,只 notice 不计失败
        if robots_groups and not robots_allows(robots_groups, b, url):
            F.append(("INFO", "ai-bots", f"{b} 被禁(训练型,不影响搜索可见性,仅提示)"))
    # ---- AI Search Health 独立子分(Semrush 8 bot 名单口径) ----
    lm_days = last_modified_days(hdrs, p.meta_last_modified)
    ratio = semantic_ratio(p.semantic_tags, p.all_tags)
    checks = [
        {"id": "bots", "pass": not blocked,
         "detail": f"被禁: {', '.join(blocked)}" if blocked else
                   (f"8 bot 全放行(Semrush 名单)" if robots_groups else "robots.txt 不可达,默认放行")},
        {"id": "llms_txt", "pass": llms_ok,
         "detail": "llms.txt 存在" if llms_ok else "/llms.txt 缺失/404(notice)"},
        {"id": "freshness", "pass": lm_days is None or lm_days <= FRESHNESS_MAX_DAYS,
         "detail": "无 Last-Modified(头/meta),跳过" if lm_days is None else
                   f"Last-Modified {lm_days} 天前(>183 天=6 个月触发,Semrush 官方)"},
        {"id": "semantic_html", "pass": ratio >= SEMANTIC_MIN_RATIO,
         "detail": f"语义标签比值 {ratio:.1%}(<10% 触发;阈值自定[推断],官方未公开)"},
        {"id": "content_length", "pass": W <= CONTENT_MAX_WORDS,
         "detail": f"词数 {W}(>15000 触发内容过长;阈值自定[推断])"},
        {"id": "bluf", "pass": b_score >= 0.5, "detail": f"score {b_score:.2f}(pass≥0.5);{b_detail}"},
    ]
    ai_health = {"score": ai_health_score(checks),
                 "bots": {"allowed": allowed, "blocked": blocked},
                 "last_modified_days": lm_days,
                 "semantic_ratio": round(ratio, 4),
                 "checks": checks}
    if lm_days is not None and lm_days > FRESHNESS_MAX_DAYS:
        F.append(("INFO", "freshness", f"Last-Modified {lm_days} 天前 >183(6 个月,Semrush 官方)"))
    if p.all_tags and ratio < SEMANTIC_MIN_RATIO:
        F.append(("INFO", "semantic-html", f"语义 HTML 比值 {ratio:.1%} <10%(阈值自定,官方未公开)"))
    if W > CONTENT_MAX_WORDS:
        F.append(("WARN", "content", f"词数 {W} >15000 内容过长(AI 上下文过载,阈值自定[推断])"))
    return F, {"title": t, "title_len": f"{tn} {tl['unit']}/{tl['value']}",
               "desc_len": f"{dn} {dl['unit']}/{dl['value']}",
               "words": W, "h1": p.h1, "jsonld": p.jsonld, "links": p.links,
               "serp_title_check": serp_check}, ai_health

CHARSET_SNIFF_BYTES = 2048   # meta charset 嗅探窗口(head_check.py 同款量级)

def detect_encoding(raw, ctype):
    """响应编码探测(S5 修复③,借鉴 head_check.py 思路自实现、不 import):
    Content-Type charset → BOM(utf-8/16/32)→ 前 2KB 内 meta charset 嗅探(编码名未知则弃用)
    → 兜底 utf-8。只返回编码名,不抛异常;decode 由调用方 errors="replace" 收尾。"""
    if ctype:
        m = re.search(r"charset\s*=\s*([\w.:+-]+)", ctype, re.I)
        if m:
            return m.group(1).strip("\"'")
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8"
    if raw.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        return "utf-32"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    m = re.search(rb"""charset\s*=\s*["']?\s*([\w.:+-]+)""", raw[:CHARSET_SNIFF_BYTES], re.I)
    if m:
        cand = m.group(1).decode("ascii", "ignore")
        try:
            codecs.lookup(cand)
            return cand
        except (LookupError, ValueError):
            pass
    return "utf-8"

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        hdrs = dict(r.headers)
        raw = r.read(2_000_000)
        enc = detect_encoding(raw, get_header(hdrs, "content-type"))
        try:
            return r.status, hdrs, raw.decode(enc, "replace")
        except (LookupError, ValueError):   # ctype 声明的编码名不存在 → utf-8 replace 兜底
            return r.status, hdrs, raw.decode("utf-8", "replace")

def main():
    args = sys.argv[1:]
    if any(a in ("-h", "--help") for a in args):
        print(USAGE)
        return
    market, as_json, export_dir = "en", False, None
    if "--market" in args:
        i = args.index("--market")
        if i + 1 >= len(args) or args[i+1].startswith("-"):   # S5 修复⑧:缺值/误吞下一个 flag → exit 2
            sys.stderr.write("--market 需要一个市场代码参数(如 en/ja/zh)\n"); sys.exit(2)
        market = args[i+1]; del args[i:i+2]
    if "--export-dir" in args:
        i = args.index("--export-dir")
        if i + 1 >= len(args) or args[i+1].startswith("-"):
            sys.stderr.write("--export-dir 需要一个目录参数\n"); sys.exit(2)
        export_dir = args[i+1]; del args[i:i+2]
    serp_titles, serp_path = None, None
    if "--serp-titles" in args:
        i = args.index("--serp-titles")
        if i + 1 >= len(args) or args[i+1].startswith("-"):
            sys.stderr.write("--serp-titles 需要一个文件参数(CSV url,title 或 JSON)\n"); sys.exit(2)
        serp_path = args[i+1]; del args[i:i+2]
        try:
            serp_titles = load_serp_titles(serp_path)
        except OSError as e:
            sys.stderr.write(f"--serp-titles 读不了: {e}\n"); sys.exit(2)
    if "--json" in args: as_json = True; args = [a for a in args if a != "--json"]
    load_market(market)  # 提前校验,未知市场列出可用值
    urls = [a for a in args if not a.startswith("-")]
    if not urls:
        sys.stderr.write(USAGE + "\n")
        sys.exit(2)
    crit = 0
    results = {}
    by_url = {}   # S4:URL → findings 原始元组(供规则聚合/bulk export)
    # S2a B4:--json 时 stdout 只出 JSON(jq/json.loads 整体可解析),人读行改走 stderr
    human = sys.stderr if as_json else sys.stdout

    def say(*a):
        print(*a, file=human)
    for url in urls:
        F, meta, ai_h = audit(url, market, serp_titles)
        by_url[url] = F
        say(f"\n== {url} ==")
        for sev, area, msg in F:
            say(f"[{sev}] {area}: {msg}")
            crit += sev == "CRITICAL"
        if meta: say("meta:", json.dumps(meta, ensure_ascii=False))
        if ai_h:  # AI Search Health 子分:与主审计结果并列展示
            parts = ", ".join(f"{c['id']}:{'✓' if c['pass'] else '✗'}" for c in ai_h["checks"])
            say(f"ai_search_health: {ai_h['score']}/100 [{parts}]")
        if as_json:
            results[url] = {
                "verdict": "refused" if any(s == "SKIP" for s, _, _ in F)
                           else ("fail" if any(s == "CRITICAL" for s, _, _ in F) else "pass"),
                "findings": [{"severity": s, "area": a, "message": m} for s, a, m in F],
                "meta": meta,
                "ai_search_health": ai_h}
    # ---- S4:规则聚合 + findings 汇总受影响面列(SF/Sitebulb 口径;SKIP 拒审不算规则) ----
    rules = aggregate_rules(by_url)
    # S5 修复⑤:coverage 分母与 summary.audited 用已审计页数——拒审([SKIP])页未被审计,剔除
    total = sum(1 for F in by_url.values() if not any(s == "SKIP" for s, _, _ in F))
    if rules:
        say("\n" + render_findings_markdown(rules, total))
    else:
        say(f"\n## findings 汇总:0 规则命中(受影响面分母=已审计 {total} 页,拒审剔除)")
    skipped = []
    if serp_titles is None:
        skipped.append({"check": "title-serp-mismatch", "reason": SERP_SKIP_REASON})
    else:
        miss = [u for u in urls if _url_key(u) not in serp_titles]
        if miss:
            skipped.append({"check": "title-serp-mismatch", "urls": miss,
                            "reason": f"{len(miss)}/{len(urls)} 个 URL 在 {serp_path} 里没有 SERP 标题,未比较"})
    for sk in skipped:
        say(f"[跳过] {sk['check']}: {sk['reason']}")
    export_files = []
    if export_dir is not None:
        export_files = write_exports(export_dir, rules, total)
        say(f"bulk export: {len(rules)} 个规则清单 + summary.json → {export_dir}")
    if as_json:
        # market/limits 为追加键(向后兼容,不改既有键):下游按本次市场阈值写修复文案(S2a B2)
        payload = {"schema_version": SCHEMA_VERSION, "market": market,
                   "limits": text_limits(market),
                   "audited": len(urls), "critical": crit, "results": results}
        if export_dir is not None:   # 仅 --export-dir 时新增 exports 节(向后兼容)
            payload["exports"] = {"dir": export_dir, "files": export_files}
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    sys.exit(1 if crit else 0)

if __name__ == "__main__": main()
