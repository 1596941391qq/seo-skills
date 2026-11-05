#!/usr/bin/env python3
"""guard_hook.py — 编码 agent 的改动前钩子:主干上不许直接改搜索引擎可见的索引控制(RQ-229;stdlib only)。

规则(SKILL.md 使用原则 3):在站点仓库里改 robots.txt、noindex、canonical、重定向,一律在分支上改、开草稿 PR,
不推主干、不合并。本钩子把这条从「写在文档里」变成「会拦」:当前分支是 main / master(或 --protect 指定的)时,
Edit / Write / MultiEdit 碰到下列任一项就拦下,告诉 agent 先开分支。
  - 文件:robots.txt、robots.ts/js、_redirects、vercel.json、netlify.toml、next.config.*、middleware.*、
    .htaccess、nginx 配置、sitemap 生成文件;
  - 内容:新增或删掉 noindex / nofollow、rel="canonical" / canonical: / alternates、redirect(s)、
    X-Robots-Tag、Disallow:。
Bash 里对 robots.txt / 重定向文件的写操作(重定向符、sed -i、tee、mv、cp)同样拦。

接法(Claude Code,项目 .claude/settings.json;`project.py ops install` 会写):
  {"hooks": {"PreToolUse": [{"matcher": "Edit|Write|MultiEdit|Bash",
     "hooks": [{"type": "command", "command": "python3 \\"$HOME/.claude/skills/seo-suite/scripts/guard_hook.py\\""}]}]}}
钩子从 stdin 读 {"tool_name", "tool_input", "cwd"};退出码 2 = 拦下(理由写 stderr,agent 能看到);0 = 放行。
其他 agent(Codex 等)没有同等钩子时,AGENTS.md 里的同一条规则是唯一约束,运营包会写进去。
"""
import json
import os
import re
import subprocess
import sys

PROTECTED = ("main", "master")
FILE_RE = re.compile(r"(^|/)(robots\.(txt|ts|js|mjs)|_redirects|_headers|vercel\.json|netlify\.toml|"
                     r"next\.config\.(js|mjs|ts|cjs)|middleware\.(ts|js)|\.htaccess|nginx[^/]*\.conf|"
                     r"sitemap[^/]*\.(xml|ts|js))$", re.I)
CONTENT_RE = re.compile(r"noindex|nofollow|rel=[\"']?canonical|\bcanonical\s*[:=]|alternates\s*:|"
                        r"\bredirects?\b|x-robots-tag|^\s*disallow\s*:", re.I | re.M)
BASH_WRITE_RE = re.compile(r"(robots\.txt|_redirects|vercel\.json|netlify\.toml|\.htaccess)", re.I)
BASH_OP_RE = re.compile(r"(>|sed\s+-i|\btee\b|\bmv\b|\bcp\b|\brm\b)")


def branch(cwd):
    try:
        p = subprocess.run(["git", "-C", cwd or ".", "symbolic-ref", "--short", "-q", "HEAD"],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def touched_text(tool, inp):
    if tool == "Write":
        return inp.get("content") or ""
    if tool == "Edit":
        return (inp.get("old_string") or "") + "\n" + (inp.get("new_string") or "")
    if tool == "MultiEdit":
        return "\n".join((e.get("old_string") or "") + "\n" + (e.get("new_string") or "")
                         for e in inp.get("edits") or [])
    return ""


def verdict(event, protected=PROTECTED):
    """→ (拦不拦, 理由)。纯函数,便于测试。"""
    tool = event.get("tool_name") or ""
    inp = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()
    br = event.get("_branch") if "_branch" in event else branch(cwd)
    if br not in protected:
        return False, ""
    if tool in ("Edit", "Write", "MultiEdit"):
        path = inp.get("file_path") or ""
        if FILE_RE.search(path):
            return True, "在 %s 上改 %s(索引控制 / 重定向文件)" % (br, os.path.basename(path))
        m = CONTENT_RE.search(touched_text(tool, inp))
        if m:
            return True, "在 %s 上改动涉及「%s」(索引控制)" % (br, m.group(0).strip())
    elif tool == "Bash":
        cmd = inp.get("command") or ""
        target = BASH_WRITE_RE.search(cmd)
        if target and BASH_OP_RE.search(cmd):
            return True, "在 %s 上用命令改 %s" % (br, target.group(1))
    return False, ""


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0                                    # 读不懂就放行,不卡住 agent
    block, why = verdict(event)
    if block:
        sys.stderr.write("seo-suite 拦下:%s。robots / noindex / canonical / 重定向的改动先开分支"
                         "(git switch -c seo/<描述>),改完开草稿 PR 给人合并;不推主干。\n" % why)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
