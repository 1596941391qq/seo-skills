#!/usr/bin/env python3
"""纯静态测试站(RQ-229 例 3、例 4;stdlib only)。

三个状态:
  clean   干净站:轻检、深审都应该 0 个问题(判据先验:测试站本身没有杂质)。
  round1  在干净站上预埋 10 个已知问题(清单见 PLANTS,开工前写定)。
  round2  修好其中 4 个、弄坏 1 个(301 → 404,同页同类级别升高)、新增 2 个。

用法:
  python3 static_site.py build --state round1 --out DIR [--base http://127.0.0.1:8601]
  python3 static_site.py serve --dir DIR --port 8601       # 认 _redirects 和 _status,带 Last-Modified
"""
import argparse
import email.utils
import http.server
import json
import os
import sys
import time

PAGES = {
    "/": ("Acme Static — 测试站首页,讲清楚这个站卖什么", "首页"),
    "/about/": ("About Acme Static: who we are and what we build", "关于"),
    "/pricing/": ("Pricing for Acme Static plans and usage limits", "价格"),
    "/blog/": ("Acme Static blog: notes on shipping static sites", "博客"),
    "/blog/a/": ("Blog A: how we cache pages at the edge safely", "文章 A"),
    "/blog/b/": ("Blog B: measuring page weight before every release", "文章 B"),
    "/blog/c/": ("Blog C: writing docs that answer the question first", "文章 C"),
    "/docs/": ("Acme Static docs: install, configure and deploy", "文档"),
    "/docs/start/": ("Getting started with Acme Static in five minutes", "入门"),
    "/docs/api/": ("Acme Static API reference for build hooks", "接口"),
    "/contact/": ("Contact Acme Static support and sales teams", "联系"),
    "/team/": ("The Acme Static team and how to reach each of us", "团队"),
    "/old-page/": ("Old page that moved to the new docs location", "旧页"),
}

# 预埋问题:(编号, URL, 怎么埋, 期望检出的 area)。round2 的处置写在 ROUND2。
PLANTS = [
    ("P1", "/about/", "title_missing", "title"),
    ("P2", "/pricing/", "desc_missing", "description"),
    ("P3", "/blog/a/", "h1_multiple", "h1"),
    ("P4", "/blog/b/", "jsonld_missing", "schema"),
    ("P5", "/blog/c/", "heading_skip", "headings"),
    ("P6", "/docs/start/", "img_alt_missing", "images"),
    ("P7", "/docs/api/", "noindex", "indexability"),
    ("P8", "/contact/", "og_missing", "og"),
    ("P9", "/team/", "status_404", "http"),
    ("P10", "/old-page/", "redirect_301", "http"),
]
ROUND2 = {
    "fixed": ["P1", "P3", "P6", "P8"],
    "worse": {"P10": "status_404"},                    # 301 → 404:同页同类(http),WARN → CRITICAL
    "new": [("N1", "/docs/", "title_too_long", "title"), ("N2", "/blog/", "lang_missing", "a11y")],
}

FILLER = (
    "Acme Static builds plain HTML sites that load fast and stay easy to audit. Every page here answers one question "
    "in its first paragraph, then gives the details a reader needs to act. We keep the markup semantic, the images "
    "described, and the links few and relevant. The team writes each page by hand, checks it against a short list, "
    "and ships it only when the list is green. This paragraph exists so the page has enough real text for a search "
    "engine to understand the topic without guessing. It talks about builds, caching, release checks, documentation, "
    "pricing, support and the people who run the project. Readers who want more can follow the links in the "
    "navigation, read the docs, or contact the team directly through the contact page listed in the footer. "
)


def page_html(path, base, title, label, plants):
    url = base + path
    lang = "" if "lang_missing" in plants else ' lang="en"'
    if "title_missing" in plants:
        title_tag = ""
    elif "title_too_long" in plants:
        title_tag = "<title>%s — and a much longer tail that keeps going well past any sensible limit</title>" % title
    else:
        title_tag = "<title>%s</title>" % title
    desc = "" if "desc_missing" in plants else (
        '<meta name="description" content="%s. Read the details, see examples and find the next step on this page.">'
        % title)
    robots = '<meta name="robots" content="noindex">' if "noindex" in plants else ""
    og = ('<meta property="og:title" content="%s"><meta property="og:description" content="%s page of Acme Static">'
          % (title, label))
    if "og_missing" not in plants:                     # 预埋只缺 og:image 一项,一个预埋 = 一个问题
        og += '<meta property="og:image" content="%s/og.png">' % base
    jsonld = "" if "jsonld_missing" in plants else (
        '<script type="application/ld+json">%s</script>'
        % json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": url}))
    h1 = "<h1>%s</h1>" % title + ("<h1>Second heading one</h1>" if "h1_multiple" in plants else "")
    sub = ("<h2>Details</h2><p>%s</p><h4>Skipped level</h4><p>%s</p><h2>Next steps</h2>" % (FILLER, FILLER)
           if "heading_skip" in plants else
           "<h2>Details</h2><p>%s</p><h3>Background</h3><p>%s</p><h2>Next steps</h2>" % (FILLER, FILLER))
    alt = "" if "img_alt_missing" in plants else ' alt="Diagram of the %s page"' % label
    imgs = "".join('<img src="/img%d.png"%s width="10" height="10">' % (i, alt) for i in range(3))
    nav = "".join('<a href="%s">%s</a> ' % (p, PAGES[p][1]) for p in ("/", "/docs/", "/blog/", "/pricing/", "/contact/"))
    return ("<!doctype html><html%s><head><meta charset=\"utf-8\">%s%s%s"
            "<link rel=\"canonical\" href=\"%s\">%s%s"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"></head><body>"
            "<header><nav>%s</nav></header><main><article>%s<p>%s answers it directly: %s</p>%s"
            "<section><p>%s</p>%s</section></article></main>"
            "<noscript><p>This page works without JavaScript.</p></noscript>"
            "<footer><p>Acme Static, a test site for seo-suite.</p></footer></body></html>"
            % (lang, title_tag, desc, robots, url, og, jsonld, nav, h1, label, FILLER, sub, FILLER, imgs))


def plants_for(state):
    """→ {path: set(kind)} 和状态码表 {path: code}。"""
    by, status = {}, {}
    if state == "clean":
        return by, status
    active = {pid: (path, kind) for pid, path, kind, _ in PLANTS}
    if state == "round2":
        for pid in ROUND2["fixed"]:
            active.pop(pid)
        for pid, kind in ROUND2["worse"].items():
            active[pid] = (active[pid][0], kind)
        for nid, path, kind, _ in ROUND2["new"]:
            active[nid] = (path, kind)
    for path, kind in active.values():
        if kind == "status_404":
            status[path] = 404
        elif kind == "redirect_301":
            status[path] = 301
        else:
            by.setdefault(path, set()).add(kind)
    return by, status


def build(out, state, base):
    by, status = plants_for(state)
    os.makedirs(out, exist_ok=True)
    for path, (title, label) in PAGES.items():
        d = os.path.join(out, path.strip("/"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html(path, base, title, label, by.get(path, set())))
    with open(os.path.join(out, "_status"), "w", encoding="utf-8") as f:
        json.dump({p: c for p, c in status.items()}, f)
    with open(os.path.join(out, "_redirects"), "w", encoding="utf-8") as f:
        json.dump({p: "/docs/" for p, c in status.items() if c == 301}, f)
    with open(os.path.join(out, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % base)
    with open(os.path.join(out, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("# Acme Static\n\n> Test site for seo-suite.\n\n" + "".join("- [%s](%s%s)\n" % (t, base, p)
                                                                           for p, (t, _) in PAGES.items()))
    with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        today = time.strftime("%Y-%m-%d")
        for p in PAGES:
            f.write("<url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n" % (base, p, today))
        f.write("</urlset>\n")
    for name in ("og.png", "img0.png", "img1.png", "img2.png"):
        with open(os.path.join(out, name), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
    return out


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 — 安静,不打访问日志
        pass

    def _maps(self):
        def load(name):
            try:
                with open(os.path.join(self.directory, name), encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError):
                return {}
        return load("_status"), load("_redirects")

    def do_GET(self):
        status, redirects = self._maps()
        path = self.path.split("?", 1)[0]
        if path in redirects:
            self.send_response(301)
            self.send_header("Location", redirects[path])
            self.end_headers()
            return
        if status.get(path) == 404:
            body = b"<!doctype html><title>Not found</title><h1>404</h1>"
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Last-Modified", email.utils.formatdate(time.time(), usegmt=True))
        super().end_headers()


def serve(directory, port):
    handler = lambda *a, **k: Handler(*a, directory=directory, **k)  # noqa: E731
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


def start(state, site_dir, port, base):
    """run_example3 用:按状态重建站点并起服务,返回进程。"""
    import shutil
    import subprocess
    shutil.rmtree(site_dir, ignore_errors=True)
    build(site_dir, state, base)
    return subprocess.Popen([sys.executable, os.path.abspath(__file__), "serve", "--dir", site_dir,
                             "--port", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop(proc):
    proc.terminate()
    proc.wait(timeout=10)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--state", choices=("clean", "round1", "round2"), required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--base", default="http://127.0.0.1:8601")
    s = sub.add_parser("serve")
    s.add_argument("--dir", required=True)
    s.add_argument("--port", type=int, default=8601)
    ns = ap.parse_args(argv)
    if ns.cmd == "build":
        print(build(ns.out, ns.state, ns.base.rstrip("/")))
    else:
        serve(ns.dir, ns.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
