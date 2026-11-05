#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""head_check.py — HTML <head> 元素检查器(仅标准库).

执行 references/technical/head-elements.md(2026 口径,主体吸收自 joshbuchea/HEAD):
  1. charset: 声明须完整落在文档前 1024 字节内(WHATWG 硬约束);HTTP 头已声明则 meta 可省
  2. title: 必须存在且非空;报告位置
  3. 推荐顺序(charset → viewport → title → 其余 meta)只是风格建议,无 SEO 依据 → 最多 INFO
  4. og:image: 须存在且为绝对 URL(https://…);og:url 有就须是 http(s):// 绝对 URL(ogp.me URL 类型)
  5. geo meta(ICBM / geo.*): Google 支持的 meta 列表里没有,Google 忽略 → 只记 INFO,缺失不告警
  6. 中文浏览器 meta: itemprop 三件套(name / image / description)——显式 --market 优先;
     未传 --market 时按 lang/内容识别中文;日文(假名)/韩文(谚文)/无汉字页跳过
  7. twitter:*: X 先读 twitter:*,缺失时回落 og:title/og:description/og:image(X Cards
     markup 文档)——不是弃用;有 OG 时只记 INFO「可省略」
  8. 可删旧标签(x-ua-compatible / skype_toolbar / msapplication-config / mask-icon /
     apple-mobile-web-app-capable / prerender / x-dns-prefetch-control / EditURI /
     pingback / archives / index / alexaVerifyID / twitter:dnt / Window-Target)只记 INFO;
     fb:app_id、amphtml 不是弃用(见 head-elements.md 第十三节)
  抓取不带 Accept-Language(与 Googlebot 一致);被重定向时报告最终 URL。

用法:
  python3 head_check.py https://example.com [--market zh]
  python3 head_check.py ./page.html        # 本地文件
  python3 head_check.py - < page.html      # stdin

退出码: 0 无严重违规; 1 存在严重违规(charset 缺失或超出前 1024 字节 / title 缺失); 2 致命错误。
"""
from __future__ import annotations

import argparse
import codecs
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urllib_request

UA = "Mozilla/5.0 (compatible; SEOSkill-HeadCheck/1.0)"
CHARSET_LIMIT = 1024          # charset meta 必须在文档前 N 字节内
GEO_META = ("ICBM", "geo.position", "geo.region", "geo.placename")
ITEMPROP_TRIO = ("name", "image", "description")  # 微信/QQ 分享三件套
SEV_ORDER = {"error": 0, "warn": 1, "info": 2, "ok": 3}

# (attr, 值[小写]) → (原因, 替代)
DEPRECATED_META = {
    ("name", "skype_toolbar"): ("Skype 工具栏扩展已消亡", "无"),
    ("name", "msapplication-config"): ("Live Tiles 已从 Win11 移除,Edge 不再渲染", '<link rel="manifest">'),
    ("name", "apple-mobile-web-app-capable"): ("web.dev 列为弃用的 Apple 专有标签", 'mobile-web-app-capable;更推荐 manifest display'),
    ("name", "alexaverifyid"): ("Alexa Internet 2022-05-01 关停", "无"),
    ("name", "twitter:dnt"): ("X 不再实际遵守", "无"),
    ("http_equiv", "x-ua-compatible"): ("IE 已于 2022-06-15 退役", "无需替代"),
    ("http_equiv", "x-dns-prefetch-control"): ("非标准;Chrome/Firefox 支持、Safari 不支持(MDN)", '<link rel="dns-prefetch">'),
    ("http_equiv", "window-target"): ("IE 时代非标准,现代浏览器不支持", "无"),
}
# twitter:* → X 回落读取的 OG 属性(X Cards markup「Tag Reference」表)
TWITTER_OG_FALLBACK = {
    "twitter:title": "og:title",
    "twitter:description": "og:description",
    "twitter:image": "og:image",
    "twitter:image:alt": "og:image:alt",
}
DEPRECATED_REL = {
    "mask-icon": ("Safari 12 起固定标签页可用普通 favicon", '标准 <link rel="icon">'),
    "prerender": ("Chrome 已移除 prerender", 'Speculation Rules API(<script type="speculationrules"> 的 prerender/prefetch 规则)'),
    "edituri": ("XML-RPC 编辑器消亡", "无"),
    "pingback": ("pingback 因 DDoS 放大被默认禁用", "Webmention"),
    "archives": ("已从 HTML Living Standard 与 IANA 注册表移除", "无"),
    "index": ("已从 HTML Living Standard 与 IANA 注册表移除", "无"),
}


def fatal(msg):
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(2)


def fetch(src, timeout, max_bytes):
    """返回 (raw_bytes, http_content_type, 来源标签, 最终 URL)。支持 http(s)/本地文件/stdin。
    不发 Accept-Language:Googlebot 一般不带这个头;带上会被按语言跳转的站带到别的 URL。"""
    if src == "-":
        return sys.stdin.buffer.read(max_bytes), "", "stdin", None
    if "://" not in src:
        p = Path(src)
        if p.is_file():
            return p.read_bytes()[:max_bytes], "", str(p), None
        fatal(f"本地文件不存在: {p}")
    if not src.lower().startswith(("http://", "https://")):
        fatal(f"不支持的 URL 协议: {src}")
    req = urllib_request.Request(src, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    })
    try:
        with urllib_request.urlopen(req, timeout=timeout) as r:
            return r.read(max_bytes), r.headers.get("Content-Type", ""), src, r.geturl()
    except (urlerror.URLError, urlerror.HTTPError, OSError, ValueError) as e:
        fatal(f"抓取失败: {e}")


def detect_encoding(raw, ctype):
    m = re.search(r"charset\s*=\s*([\w.:+-]+)", ctype, re.I)
    if m:
        return m.group(1).strip('"\'')
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8"
    if raw.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        return "utf-32"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    m = re.search(rb'charset\s*=\s*["\']?\s*([\w.:+-]+)', raw[:CHARSET_LIMIT], re.I)
    if m:
        try:
            codecs.lookup(m.group(1).decode("ascii", "ignore"))
            return m.group(1).decode("ascii", "ignore")
        except (LookupError, UnicodeDecodeError):
            pass
    return "utf-8"


class HeadParser(HTMLParser):
    """收集 head 区元素及字符偏移(</head> 或 <body> 之后的元素不计)。"""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.line_starts = [0]
        for i, ch in enumerate(text):
            if ch == "\n":
                self.line_starts.append(i + 1)
        self.active = True
        self.metas, self.links = [], []
        self.title = None          # {"pos": int, "text": str}
        self.title_count = 0

    def _pos(self):
        line, off = self.getpos()
        base = self.line_starts[line - 1] if 0 < line <= len(self.line_starts) else 0
        return base + off

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.active = False
            return
        if not self.active:
            return
        pos = self._pos()
        if tag == "meta":
            d = dict(attrs)
            self.metas.append({
                "pos": pos,
                "charset": (d.get("charset") or "").strip(),
                "name": (d.get("name") or "").strip().lower(),
                "property": (d.get("property") or "").strip().lower(),
                "http_equiv": (d.get("http-equiv") or "").strip().lower(),
                "itemprop": (d.get("itemprop") or "").strip().lower(),
                "content": d.get("content") or "",
            })
        elif tag == "link":
            d = dict(attrs)
            self.links.append({
                "pos": pos, "href": d.get("href") or "",
                "rel": {t.strip().lower() for t in (d.get("rel") or "").split() if t.strip()},
            })
        elif tag == "title":
            self.title_count += 1
            if self.title is None:
                self.title = {"pos": pos, "text": ""}
                self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "head":
            self.active = False

    def handle_data(self, data):
        if getattr(self, "_in_title", False) and self.title is not None:
            self.title["text"] += data


def byte_offset(text, char_pos, enc):
    return len(text[:char_pos].encode(enc, errors="replace"))


def chinese_share_scope(text, market=None):
    """微信/QQ itemprop 检查是否适用:显式 --market 优先(zh/zh-* → 适用,其他 → 不适用);
    未传 --market 时 lang=zh,或文档检出足量汉字且无假名(日文)/谚文(韩文)——日文页满篇
    汉字属 kanji,不是中文内容,不得触发。"""
    if market:
        return market.strip().lower().split("-")[0].split("_")[0] == "zh"
    m = re.search(r"""<html[^>]*\blang\s*=\s*["']?([\w-]+)""", text, re.I)
    if m:
        tag = m.group(1).lower()
        if tag.startswith("zh"):
            return True
        if tag[:2] in ("ja", "ko"):
            return False
    if re.search(r"[\u3040-\u30FF]", text):   # 平假名/片假名 → 日文页
        return False
    if re.search(r"[\uAC00-\uD7A3]", text):   # 谚文 → 韩文页
        return False
    return len(re.findall(r"[\u3400-\u4DBF\u4E00-\u9FFF]", text)) >= 20


def describe_meta(m):
    for attr, label in (("name", "name"), ("property", "property"),
                        ("http_equiv", "http-equiv"), ("itemprop", "itemprop")):
        if m[attr]:
            return f'meta {label}="{m[attr]}"'
    return "meta(匿名)"


def check(raw, text, enc, ctype, out, market=None):
    """执行 8 项检查,out(sev, msg) 收集结果;返回 (metas, links)。"""
    hp = HeadParser(text)
    try:
        hp.feed(text)
        hp.close()
    except Exception as e:  # HTMLParser 对畸形 HTML 也极少抛,兜底
        out("warn", f"HTML 解析中断({e}),以下按已解析部分检查")
    metas, links = hp.metas, hp.links
    title = hp.title

    # --- 1. charset:前 1024 字节 ---
    header_cs = re.search(r"charset\s*=\s*([\w.:+-]+)", ctype or "", re.I)
    cs_meta, cs_kind = None, None
    for m in metas:
        if m["charset"]:
            cs_meta, cs_kind, cs_val = m, "charset 属性", m["charset"]
            break
        if m["http_equiv"] == "content-type" and re.search(r"charset\s*=", m["content"], re.I):
            cs_meta, cs_kind = m, "http-equiv Content-Type"
            mm = re.search(r"charset\s*=\s*([\w.:+-]+)", m["content"], re.I)
            cs_val = mm.group(1) if mm else "?"
            break
    if cs_meta is not None:
        boff = byte_offset(text, cs_meta["pos"], enc)
        if boff > CHARSET_LIMIT:
            out("error", f'charset({cs_val},{cs_kind})位于第 {boff} 字节,超出前 {CHARSET_LIMIT} 字节 '
                         f'→ 建议: 把 <meta charset> 移到 <head> 第一个元素')
        else:
            out("ok", f"charset={cs_val}({cs_kind},第 {boff} 字节,≤{CHARSET_LIMIT})")
    elif header_cs:
        out("info", f'charset 仅由 HTTP 头声明({header_cs.group(1)});浏览器优先读头/BOM,meta 可省')
    else:
        out("error", f"未发现 charset 声明(meta 与 HTTP 头均无)→ 建议: <head> 首元素放 <meta charset=\"utf-8\">")

    # --- 2/3. title 与推荐顺序 ---
    if title is None or not title["text"].strip():
        out("error", "title 缺失或为空 → 建议: 在 charset/viewport 之后立即声明 <title>(标题链接候选来源)")
        title_pos = None
    else:
        title_pos = title["pos"]
        boff = byte_offset(text, title_pos, enc)
        out("ok", f'title 存在: "{title["text"].strip()[:60]}"(第 {boff} 字节)')
        if hp.title_count > 1:
            out("warn", f"检测到 {hp.title_count} 个 <title>,仅第一个生效")
    if title_pos is not None:
        late = []
        if cs_meta is not None and cs_meta["pos"] > title_pos:
            late.append("charset")
        vp_late = [m for m in metas if m["name"] == "viewport" and m["pos"] > title_pos]
        if vp_late:
            late.append("viewport")
        if late:
            out("info", f"推荐顺序(风格建议,无 SEO 影响): {'/'.join(late)} 声明在 <title> 之后 "
                        f"→ 可选: charset → viewport → title → 其余 meta")
        early = [describe_meta(m) for m in metas
                 if m["name"] not in ("charset", "viewport") and not m["charset"]
                 and m["http_equiv"] != "content-type" and m["pos"] < title_pos]
        if early:
            out("info", f'推荐顺序(风格建议,无 SEO 影响): {", ".join(dict.fromkeys(early))} 出现在 <title> 之前 '
                        f"→ 可选: charset → viewport → title → 其余 meta(OG/description 等)")
    if not any(m["name"] == "viewport" for m in metas):
        out("warn", 'viewport 缺失 → 建议: <meta name="viewport" content="width=device-width, initial-scale=1">')

    # --- 4. og:image ---
    ogs = [m["content"].strip() for m in metas if m["property"] == "og:image" and m["content"].strip()]
    if not ogs:
        out("warn", 'og:image 缺失 → 建议: <meta property="og:image" content="https://…">(绝对 URL;分享卡片依赖)')
    elif any(re.match(r"^https?://", u, re.I) for u in ogs):
        out("ok", f"og:image 为绝对 URL: {ogs[0][:80]}")
    else:
        out("warn", f'og:image 非绝对 URL: "{ogs[0][:80]}" → 建议: 改为 https:// 绝对地址(部分抓取器不解析相对路径)')

    # --- 4b. og:url:ogp.me 定义为对象的规范 URL(永久 ID),Types 表里 URL 类型 =「All valid URLs that
    # utilize the http:// or https:// protocols」→ 相对路径("/"、"/about")不合规。sspai 首页 og:url="/" 实测漏报。
    og_urls = [m["content"].strip() for m in metas if m["property"] == "og:url"]
    if og_urls:
        if re.match(r"^https?://", og_urls[0], re.I):
            out("ok", f"og:url 为绝对 URL: {og_urls[0][:80]}")
        else:
            out("warn", f'og:url 非绝对 URL: "{og_urls[0][:80]}" → 建议: 写成 https:// 开头的完整规范 URL'
                        f'(ogp.me:URL 类型须 http(s)://;分享抓取器按它归并同一对象)')

    # --- 5. geo meta:不在 Google 支持的 meta 列表里(special-tags 文档),Google 忽略 → 只记 INFO ---
    names = {m["name"] for m in metas if m["name"]}
    geo_present = [g for g in GEO_META if g.lower() in names]
    if geo_present:
        out("info", f"geo meta 存在: {', '.join(geo_present)}——Google 不使用(不在其支持的 meta 列表),"
                    f"不影响搜索;本地业务用 LocalBusiness 结构化数据表达位置")

    # --- 6. 微信/QQ itemprop 三件套(仅中文场景:zh 市场或检出中文内容)---
    # S2 修复:此前对所有站点无条件 WARN——日/英/阿文站全成跨市场噪音。
    # 判定:--market zh 显式指定,或 lang=zh,或正文检出汉字且非日文(假名)/韩文(谚文)页。
    if chinese_share_scope(text, market):
        props = {m["itemprop"] for m in metas if m["itemprop"]}
        trio_missing = [p for p in ITEMPROP_TRIO if p not in props]
        if not trio_missing:
            out("ok", "中文分享 itemprop 三件套齐全(name / image / description)")
        elif props:
            out("warn", f"微信/QQ 分享 itemprop 不全: 缺 {', '.join(trio_missing)}(现有 {sorted(props)})")
        else:
            out("warn", "微信/QQ 分享 itemprop 三件套缺失(仅中文分享场景需要:微信/QQ 不消费 OG,读 itemprop 微数据;"
                        f'需 <html itemscope itemtype=…> 配合)')
    else:
        out("info", "itemprop 三件套跳过——非中文页面/市场(微信/QQ 分享场景不适用)")

    # --- 7. twitter:*:X 先读 twitter:*,缺失时回落 OG(X Cards markup 文档)——不是弃用 ---
    og_props = {m["property"] for m in metas if m["property"].startswith("og:") and m["content"].strip()}
    og_props |= {m["name"] for m in metas if m["name"].startswith("og:") and m["content"].strip()}
    redundant = []
    for m in metas:
        tw = m["name"] if m["name"].startswith("twitter:") else (
            m["property"] if m["property"].startswith("twitter:") else "")
        og = TWITTER_OG_FALLBACK.get(tw)
        if og and og in og_props and tw not in redundant:
            redundant.append(tw)
    if redundant:
        out("info", f"twitter:* 与 OG 重复: {', '.join(redundant)}——X 缺失时会回落到对应 og:*,"
                    f"可省略(不是弃用;内容不同时保留)")

    # --- 8. 可删旧标签:只记 INFO(head-elements.md 第十三节),不影响退出码 ---
    seen_hits = set()
    for m in metas:
        for attr in ("name", "property", "http_equiv"):
            key = (attr, m[attr])
            if key in DEPRECATED_META and key not in seen_hits:
                seen_hits.add(key)
                why, alt = DEPRECATED_META[key]
                out("info", f'可删旧标签: <{describe_meta(m)}> — {why} → 替代: {alt}')
    for lk in links:
        for tok in sorted(lk["rel"] & set(DEPRECATED_REL)):
            why, alt = DEPRECATED_REL[tok]
            out("info", f'可删旧标签: <link rel="{tok}"> — {why} → 替代: {alt}')

    # --- 附加: meta keywords ---
    if any(m["name"] == "keywords" for m in metas):
        out("info", "meta keywords 存在: Google 不使用,可删")

    return metas, links


def main():
    ap = argparse.ArgumentParser(
        description="HTML <head> 元素检查器(口径: technical/head-elements.md;严重违规退出码 1)")
    ap.add_argument("url", help="页面 URL(http/https;亦支持本地文件路径或 - 读 stdin)")
    ap.add_argument("--market", default=None,
                    help="目标市场码(如 zh/en/es);显式指定时优先,itemprop 中文分享检查只在 zh 市场报;"
                         "缺省按 lang/内容自动识别")
    ap.add_argument("--timeout", type=float, default=15.0, help="抓取超时秒数,默认 15")
    ap.add_argument("--max-bytes", type=int, default=2_000_000, help="最多读取字节数,默认 2MB")
    a = ap.parse_args()

    raw, ctype, label, final_url = fetch(a.url, a.timeout, a.max_bytes)
    if not raw.strip():
        fatal("文档为空")
    enc = detect_encoding(raw, ctype)
    try:
        text = raw.decode(enc, errors="replace")
    except (LookupError, UnicodeDecodeError):
        enc, text = "utf-8", raw.decode("utf-8", errors="replace")

    findings = []

    def out(sev, msg):
        findings.append((sev, msg))

    metas, links = check(raw, text, enc, ctype, out, market=a.market)
    findings.sort(key=lambda f: SEV_ORDER[f[0]])  # 稳定排序: error → warn → info → ok

    W = 76
    print("=" * W)
    print(f"head 元素检查 — {label}")
    if final_url and final_url != label:
        print(f"[!] 请求 URL 被重定向:最终 URL = {final_url}——以下结果是最终 URL 的 head,"
              f"不是 {label} 本身(按语言/地区跳转的站尤其注意)")
    print(f"文档 {len(raw)} 字节 | 解码 {enc} | head 元素: meta {len(metas)} / link {len(links)} / "
          f"title {'有' if any(f[0]=='ok' and f[1].startswith('title') for f in findings) else '无'}")
    print("=" * W)
    for sev, msg in findings:
        print(f"[{sev.upper():<5}] {msg}")
    print("-" * W)
    counts = {s: sum(1 for f in findings if f[0] == s) for s in ("error", "warn", "info", "ok")}
    print(f"汇总: 严重(error)={counts['error']}  警告(warn)={counts['warn']}  "
          f"提示(info)={counts['info']}  通过(ok)={counts['ok']}")
    if counts["error"]:
        print("存在严重违规 → 退出码 1")
        sys.exit(1)
    print("无严重违规 → 退出码 0")
    sys.exit(0)


if __name__ == "__main__":
    main()
