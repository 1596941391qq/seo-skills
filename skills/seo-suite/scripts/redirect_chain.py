#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""redirect_chain.py — 逐跳重定向链审计 (仅标准库).

用法:
  python3 redirect_chain.py http://example.com
  python3 redirect_chain.py https://old.example.com/page?id=7 --max 5

行为:
  * 手动发 GET, 不自动跟随 3xx, 逐跳记录 status / Location / 耗时
  * 链长判定: > 2 跳 -> 警告; > 5 跳 (或超过 --max) -> CRITICAL
  * 循环检测: 同一规范化 URL 二次出现即判定为循环
  * 301 vs 302: 永久性变更 (http->https 升级 / 加去 www / 仅尾斜杠差异) 却用
    302/303/307 -> 提示应改 301 (308 为永久保留方法, 视同 301)
  * 每跳检查查询参数保留: 上一跳的全部参数应出现在下一跳 URL 中
  * HTTPS -> HTTP 降级跳转 -> 警告 (Ahrefs「HTTPS to HTTP redirect」)

退出码: 存在 CRITICAL (循环 / >5 跳 / 超过 --max) -> 1; 仅警告 -> 0; 致命错误 -> 2.
"""
from __future__ import annotations

import argparse
import sys
import time
import http.client
from urllib.parse import urlsplit, urljoin, parse_qsl

UA = "Mozilla/5.0 (compatible; SEOSkill-RedirectChain/1.0)"
REDIRECT_STATUSES = (301, 302, 303, 307, 308)
PERMANENT = (301, 308)


def request_once(url, timeout, ua=UA):
    """单次 GET, 不跟随重定向. 返回 (status, location, elapsed_ms)."""
    p = urlsplit(url)
    if p.scheme == "https":
        conn = http.client.HTTPSConnection(p.hostname, p.port or 443, timeout=timeout)
    elif p.scheme == "http":
        conn = http.client.HTTPConnection(p.hostname, p.port or 80, timeout=timeout)
    else:
        raise ValueError("不支持的协议: {0}".format(p.scheme or "(空)"))
    target = (p.path or "/") + (("?" + p.query) if p.query else "")
    t0 = time.monotonic()
    conn.request("GET", target, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Connection": "close",
    })
    resp = conn.getresponse()
    status = resp.status
    location = resp.getheader("Location")
    try:
        resp.read(2048)  # 少量读取以复用连接, 随即关闭
    except Exception:
        pass
    conn.close()
    return status, location, (time.monotonic() - t0) * 1000.0


def norm(url):
    """循环检测用规范化: 小写 scheme/host, 去默认端口, 排序 query, 去 fragment."""
    p = urlsplit(url)
    try:
        netloc = p.netloc.lower()
        if (p.scheme == "https" and p.port == 443) or (p.scheme == "http" and p.port == 80):
            netloc = (p.hostname or p.netloc).lower()
    except ValueError:
        netloc = p.netloc.lower()
    q = "&".join(sorted(p.query.split("&"))) if p.query else ""
    from urllib.parse import urlunsplit
    return urlunsplit((p.scheme.lower(), netloc, p.path or "/", q, ""))


def looks_permanent(a, b):
    """判断 a->b 是否属于"永久性"变更场景; 返回描述或 None."""
    pa, pb = urlsplit(a), urlsplit(b)
    if pa.scheme == "http" and pb.scheme == "https":
        return "http->https 升级"
    ha, hb = pa.netloc.lower(), pb.netloc.lower()
    if ha != hb and ha.lstrip("www.") == hb.lstrip("www."):
        return "www 收敛 ({0}->{1})".format(ha, hb)
    patha = (pa.path or "/").rstrip("/")
    pathb = (pb.path or "/").rstrip("/")
    if ha == hb and patha == pathb and (pa.path or "/") != (pb.path or "/"):
        return "仅尾斜杠差异"
    return None


def truncate(s, n=64):
    s = s or ""
    return s if len(s) <= n else s[: n - 3] + "..."


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="redirect_chain.py",
        description="逐跳重定向链审计: 链长/循环/301 vs 302/查询参数保留 (stdlib only)")
    ap.add_argument("url", help="起始 URL")
    ap.add_argument("--max", type=int, default=5, help="允许的最大跳数, 超过判 CRITICAL (默认 5)")
    ap.add_argument("--timeout", type=float, default=12.0, help="单请求超时秒数 (默认 12)")
    args = ap.parse_args(argv)

    url = args.url.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    chain = []       # (url, status, location, ms)
    issues = []      # (severity, text)
    critical = False
    seen = set()
    current = url

    try:
        seen.add(norm(current))
        while True:
            try:
                status, location, ms = request_once(current, args.timeout)
            except (http.client.HTTPException, OSError, ValueError) as e:
                print("[FATAL] 请求失败 {0}: {1}: {2}".format(current, type(e).__name__, e),
                      file=sys.stderr)
                return 2
            chain.append((current, status, location, ms))

            if status not in REDIRECT_STATUSES or not location:
                break  # 到达终点 (2xx/4xx/5xx 或无 Location 的 3xx)

            if len(chain) - 1 >= args.max:
                issues.append(("CRITICAL", "已跟随 {0} 跳仍未终止, 超过 --max={1}".format(
                    len(chain) - 1, args.max)))
                critical = True
                break

            nxt = urljoin(current, location)

            # 查询参数保留检查
            params_now = parse_qsl(urlsplit(current).query, keep_blank_values=True)
            params_next = parse_qsl(urlsplit(nxt).query, keep_blank_values=True)
            lost_vals = ["{0}={1}".format(k, v) for k, v in params_now if (k, v) not in params_next]
            if lost_vals:
                issues.append(("WARN", "第 {0} 跳丢失查询参数: {1}".format(len(chain), ", ".join(lost_vals[:5]))))

            # 循环检测
            n = norm(nxt)
            if n in seen:
                chain.append((nxt, None, "(循环)", 0.0))
                issues.append(("CRITICAL", "检测到循环: {0} 再次出现".format(truncate(nxt))))
                critical = True
                break
            seen.add(n)

            # HTTPS → HTTP 降级(Ahrefs「HTTPS to HTTP redirect」warning:「It is not recommended to
            # redirect HTTPS URLs to HTTP URLs」https://help.ahrefs.com/en/articles/2442569,2026-11-05 读取)
            if urlsplit(current).scheme.lower() == "https" and urlsplit(nxt).scheme.lower() == "http":
                issues.append(("WARN", "第 {0} 跳 HTTPS→HTTP 降级: {1} -> {2} (跳转目标应保持 HTTPS)".format(
                    len(chain), truncate(current, 48), truncate(nxt, 48))))

            # 301 vs 302 建议
            perm = looks_permanent(current, nxt)
            if perm and status not in PERMANENT:
                issues.append(("WARN", "第 {0} 跳是{1}, 但状态码 {2} 为临时重定向, 建议改 301".format(
                    len(chain), perm, status)))

            current = nxt
    except KeyboardInterrupt:
        print("\n[interrupted]", file=sys.stderr)
        return 130

    hops = len(chain) - 1
    print("=" * 88)
    print("redirect_chain | 起始: {0}".format(url))
    print("{0:<4} {1:<6} {2:>8}  {3}".format("#", "状态", "耗时(ms)", "URL -> Location"))
    print("-" * 88)
    for i, (u, status, location, ms) in enumerate(chain):
        arrow = ""
        if location and location != "(循环)":
            arrow = "-> " + truncate(location)
        elif location == "(循环)":
            arrow = "-> (循环)"
        print("{0:<4} {1:<6} {2:>8.0f}  {3} {4}".format(
            i, status if status is not None else "-", ms, truncate(u, 60), arrow))
    print("-" * 88)
    final = chain[-1]
    print("链长: {0} 跳 | 终态: HTTP {1}".format(hops, final[1] if final[1] is not None else "(循环)"))

    if hops >= 1 and final[1] is not None and final[1] >= 400:   # 11-05 评审:跳到 404 原来判「无问题」
        issues.append(("CRITICAL", "重定向终点返回 HTTP {0}: {1} (跳到坏页, 改指向能打开的页或直接 404/410)".format(
            final[1], truncate(final[0], 60))))
        critical = True
    if hops > 2:
        sev = "CRITICAL" if hops > 5 else "WARN"
        issues.append((sev, "链长 {0} 跳{1} (Google/用户均不友好, 应一跳到底)".format(
            hops, ", 超过 5 跳" if hops > 5 else "")))
        if hops > 5:
            critical = True

    if issues:
        print("\n---- 问题 ----")
        for sev, text in issues:
            print("  [{0}] {1}".format(sev, text))
    else:
        print("\n无问题: 链长 <= 2 跳, 无循环, 无参数丢失, 无 301/302 误用, 无 HTTPS→HTTP 降级.")

    print("==== 结论: {0} ====".format("CRITICAL (退出码 1)" if critical else "PASS/WARN (退出码 0)"))
    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
