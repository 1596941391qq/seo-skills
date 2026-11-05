#!/usr/bin/env python3
"""例 7 难场景用的测试站(stdlib only)。0.40.0 的普通场景站点太容易,装不装 skill 只差 3 个百分点。

两个站,问题都在开跑前写定(INTL_PLANTS、EDGE_PLANTS),另有故意设置、不算问题的诱饵页(*_DECOYS):
  intl  中英西三语 15 页,5 个 hreflang / canonical 问题。期望值依据 Google「Tell Google about localized
        versions of your page」:每个语言版本要列出全部版本含自己、互相回链、语言码 ISO 639-1(+ ISO 3166-1
        Alpha 2 地区码,英国是 GB 不是 UK)、目标要能直接打开;跨语言页 canonical 指向另一种语言会让本页不被收录。
  edge  响应头、重定向和 sitemap 层的 5 个问题(仓库里只能看到 _headers / _redirects 两个 JSON 配置),
        3 个诱饵(站内搜索页和购物车 noindex、打印版 canonical 指回原文,都是正确用法且不在 sitemap 里)。

服务器认 _status、_redirects({path: [code, target]})、_headers({path: {名: 值}})。
"""
import http.server
import json
import os
import time

FILLER = ("This page explains the product in plain words and gives the reader the next step. It has enough real "
          "text for a search engine to understand the topic: builds, caching, release checks, docs, pricing and "
          "support. ") * 4

# ---------------------------------------------------------------- intl
CLUSTERS = {                      # 簇名: {hreflang: path}
    "home": {"en": "/", "zh": "/zh/", "es": "/es/"},
    "pricing": {"en": "/pricing/", "zh": "/zh/pricing/", "es": "/es/precios/"},
    "docs": {"en": "/docs/", "zh": "/zh/docs/", "es": "/es/docs/"},
    "about": {"en": "/about/", "zh": "/zh/about/", "es": "/es/acerca/"},
    "blog": {"en": "/blog/", "zh": "/zh/blog/", "es": "/es/blog/"},
}
TITLES = {"en": "Acme Global — %s for teams that ship static sites", "zh": "Acme Global —— 面向静态站团队的%s",
          "es": "Acme Global: %s para equipos que publican sitios estáticos"}
LABEL = {"home": ("home", "首页", "inicio"), "pricing": ("pricing", "价格", "precios"), "docs": ("docs", "文档", "documentación"),
         "about": ("about us", "关于我们", "quiénes somos"), "blog": ("blog", "博客", "blog")}

# (编号, 判对的 URL 集合, 问题描述里要出现的词(正则), 怎么埋)
INTL_PLANTS = [
    ("I1", ["/es/precios/"], r"canonical|规范", "es 价格页 canonical 指向英文 /pricing/"),
    ("I2", ["/zh/docs/", "/docs/", "/es/docs/"], r"hreflang|回链|互指|return|reciproc|双向|对应",
     "/zh/docs/ 不列英、西版本,另两页指向它却没有回链"),
    ("I3", ["/about/", "/zh/about/", "/es/acerca/"], r"en-UK|en-GB|语言码|地区码|code|ISO|无效|invalid",
     "about 簇把英文版标成 hreflang=\"en-UK\"(英国的 ISO 3166-1 码是 GB)"),
    ("I4", ["/es/blog-old/", "/es/blog/", "/blog/", "/zh/blog/"], r"301|redirect|重定向|跳转",
     "blog 簇的 es 目标写成 /es/blog-old/,它 301 到 /es/blog/"),
    ("I5", ["/zh/pricing/"], r"self|自引用|自身|自己|自我",
     "/zh/pricing/ 的 hreflang 不列它自己"),
]
INTL_DECOYS = ["/", "/zh/", "/es/", "/search/"]          # home 簇完全正确;/search/ 是站内搜索,故意 noindex


def _intl_alts(cluster, path):
    alts = dict(CLUSTERS[cluster])
    if cluster == "about":
        alts["en-UK"] = alts.pop("en")
    if cluster == "blog":
        alts["es"] = "/es/blog-old/"
    if path == "/zh/docs/":
        alts = {"zh": "/zh/docs/"}
    if path == "/zh/pricing/":
        alts.pop("zh")
    return alts


def intl_page(base, cluster, lang, path):
    i = ("en", "zh", "es").index(lang)
    title = TITLES[lang] % LABEL[cluster][i]
    canon = base + ("/pricing/" if path == "/es/precios/" else path)
    alts = _intl_alts(cluster, path)
    links = "".join('<link rel="alternate" hreflang="%s" href="%s%s">' % (h, base, p) for h, p in alts.items())
    links += '<link rel="alternate" hreflang="x-default" href="%s%s">' % (base, CLUSTERS[cluster]["en"])
    nav = "".join('<a href="%s">%s</a> ' % (CLUSTERS[c][lang], LABEL[c][i]) for c in CLUSTERS)
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><title>%s</title>'
            '<meta name="description" content="%s. %s">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<link rel="canonical" href="%s">%s</head><body><header><nav>%s</nav></header>'
            "<main><h1>%s</h1><p>%s</p><h2>Details</h2><p>%s</p><h2>Next</h2></main></body></html>"
            % (lang, title, title, FILLER[:120], canon, links, nav, title, FILLER, FILLER))


def build_intl(out, base):
    os.makedirs(out, exist_ok=True)
    pages = []
    for cluster, by in CLUSTERS.items():
        for lang, path in by.items():
            _write(out, path, intl_page(base, cluster, lang, path))
            pages.append(path)
    _write(out, "/search/", '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Search Acme Global</title>'
                            '<meta name="robots" content="noindex, follow"><meta name="viewport" content="width=device-width">'
                            "</head><body><main><h1>Search</h1><form action=\"/search/\"><input name=q></form></main></body></html>")
    _json(out, "_redirects", {"/es/blog-old/": [301, "/es/blog/"]})
    _common(out, base, pages)
    return out


# ---------------------------------------------------------------- edge
EDGE_PAGES = {
    "/": "Acme Edge — static hosting with fast global caching",
    "/pricing/": "Acme Edge pricing: plans, limits and overage rates",
    "/blog/": "Acme Edge blog: notes from running an edge network",
    "/blog/a-new/": "How we cache pages at the edge without stale content",
    "/blog/b/": "Measuring page weight before every release ships",
    "/docs/": "Acme Edge docs: install, configure and deploy",
    "/docs/start/": "Getting started with Acme Edge in five minutes",
    "/about-us/": "About Acme Edge: the team and what we build",
    "/products/": "Acme Edge products: hosting, functions and storage",
    "/products/widget/": "Acme Edge widget",
    "/contact/": "Contact Acme Edge support and sales",
    "/search/": "Search Acme Edge",
    "/cart/": "Your Acme Edge cart",
    "/print/blog/b/": "Measuring page weight before every release ships (print version)",
}
EDGE_SITEMAP = ["/", "/pricing/", "/blog/", "/blog/a/", "/blog/b/", "/docs/", "/docs/start/", "/about/",
                "/products/", "/products/widget/", "/contact/"]
EDGE_PLANTS = [
    ("E1", ["/pricing/"], r"noindex|x-robots", "/pricing/ 响应头 X-Robots-Tag: noindex,却在 sitemap 里"),
    ("E2", ["/blog/a/", "/blog/a-new/"], r"301|redirect|重定向|跳转", "sitemap 列的 /blog/a/ 301 到 /blog/a-new/"),
    ("E3", ["/products/widget/"], r"soft|软|404|不存在|no longer|下架|空", "/products/widget/ 回 200,正文是「商品已下架」(软 404)"),
    ("E4", ["/docs/start/", "/docs/getting-started/"], r"canonical|规范", "/docs/start/ canonical 指向 404 的 /docs/getting-started/"),
    ("E5", ["/about/", "/about-us/"], r"302|临时|temporary", "/about/ 用 302 跳 /about-us/(永久搬家)"),
]
EDGE_DECOYS = ["/search/", "/cart/", "/print/blog/b/"]


def build_edge(out, base):
    os.makedirs(out, exist_ok=True)
    for path, title in EDGE_PAGES.items():
        canon = {"/docs/start/": "/docs/getting-started/", "/print/blog/b/": "/blog/b/"}.get(path, path)
        robots = '<meta name="robots" content="noindex, follow">' if path == "/search/" else ""
        body = ("<p>Sorry, this product is no longer available.</p>" if path == "/products/widget/"
                else "<p>%s</p><h2>Details</h2><p>%s</p><h2>Next</h2>" % (FILLER, FILLER))
        nav = "".join('<a href="%s">%s</a> ' % (p, p) for p in ("/", "/pricing/", "/blog/", "/docs/", "/about/", "/products/"))
        _write(out, path, '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title>'
                          '<meta name="description" content="%s. Details, examples and the next step.">%s'
                          '<meta name="viewport" content="width=device-width, initial-scale=1">'
                          '<link rel="canonical" href="%s%s"></head><body><header><nav>%s</nav></header>'
                          "<main><h1>%s</h1>%s</main></body></html>" % (title, title, robots, base, canon, nav, title, body))
    _json(out, "_redirects", {"/blog/a/": [301, "/blog/a-new/"], "/about/": [302, "/about-us/"]})
    _json(out, "_headers", {"/pricing/": {"X-Robots-Tag": "noindex"}, "/cart/": {"X-Robots-Tag": "noindex"}})
    _common(out, base, EDGE_SITEMAP)
    return out


# ---------------------------------------------------------------- 共用
def _write(out, path, html):
    d = os.path.join(out, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def _json(out, name, obj):
    with open(os.path.join(out, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def _common(out, base, sitemap_paths):
    with open(os.path.join(out, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % base)
    with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in sitemap_paths:
            f.write("<url><loc>%s%s</loc><lastmod>2026-10-20</lastmod></url>\n" % (base, p))
        f.write("</urlset>\n")


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 — 安静,签名照基类
        pass

    def _load(self, name):
        try:
            with open(os.path.join(self.directory, name), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        red = self._load("_redirects").get(path)
        if red:
            code, target = red if isinstance(red, list) else (301, red)
            self.send_response(code)
            self.send_header("Location", target)
            self.end_headers()
            return
        status = self._load("_status").get(path)
        local = os.path.join(self.directory, path.strip("/"), "index.html") if path.endswith("/") else None
        if status == 404 or (local is not None and not os.path.isfile(local) and path != "/"):
            body = b"<!doctype html><title>Not found</title><h1>404</h1>"
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._extra = self._load("_headers").get(path, {})
        super().do_GET()

    def end_headers(self):
        for k, v in getattr(self, "_extra", {}).items():
            self.send_header(k, v)
        self.send_header("Last-Modified", email_date())
        super().end_headers()


def email_date():
    import email.utils
    return email.utils.formatdate(time.time(), usegmt=True)


def serve(directory, port):
    handler = lambda *a, **k: Handler(*a, directory=directory, **k)  # noqa: E731
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
