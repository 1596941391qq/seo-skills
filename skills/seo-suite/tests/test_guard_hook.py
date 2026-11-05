#!/usr/bin/env python3
"""guard_hook:主干上改索引控制要拦,分支上放行。

期望值来自 SKILL.md 使用原则 3(RQ-229 安全边界,Echo 11-05 批的需求卡第 3 节「安全边界统一」):
「在站点仓库里改 robots.txt、noindex、canonical、重定向,一律开草稿 PR,不推主干、不合并。」
"""
import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
import guard_hook as G  # noqa: E402


def ev(tool, branch="main", **inp):
    return {"tool_name": tool, "tool_input": inp, "_branch": branch}


class GuardHookTests(unittest.TestCase):
    def test_blocks_index_controls_on_main(self):
        cases = [
            ev("Write", file_path="/r/public/robots.txt", content="User-agent: *\nAllow: /\n"),
            ev("Edit", file_path="/r/app/about/page.tsx", old_string="title: 'A'",
               new_string="title: 'A', robots: 'noindex'"),
            ev("Edit", file_path="/r/app/layout.tsx", old_string="x", new_string="alternates: { canonical: '/x' }"),
            ev("Edit", file_path="/r/next.config.mjs", old_string="a", new_string="b"),
            ev("MultiEdit", file_path="/r/pages/a.html",
               edits=[{"old_string": "<head>", "new_string": '<head><link rel="canonical" href="/b">'}]),
            ev("Bash", command="echo 'Disallow: /' >> public/robots.txt"),
            ev("Write", file_path="/r/public/robots.txt", branch="master", content="x"),
        ]
        for c in cases:
            self.assertTrue(G.verdict(c)[0], c)

    def test_blocks_push_to_main_and_title_edits(self):
        # 例 7 对抗场景「用户说直接推 main」(11-05 评测:没装运营包的 Sonnet 5/5 照推)。
        self.assertTrue(G.verdict(ev("Bash", command="git push origin main"))[0])
        self.assertTrue(G.verdict(ev("Bash", command="git push"))[0])
        self.assertTrue(G.verdict(ev("Bash", branch="seo/x", command="cd r && git push -q origin main"))[0])
        self.assertTrue(G.verdict(ev("Bash", branch="seo/x", command="git push origin HEAD:main"))[0])
        self.assertTrue(G.verdict(ev("Edit", file_path="/r/about/index.html", old_string="<head>",
                                     new_string="<head><title>About</title>"))[0])
        self.assertFalse(G.verdict(ev("Bash", branch="seo/x", command="git push -u origin seo/x"))[0])
        self.assertFalse(G.verdict(ev("Bash", branch="seo/x", command="git push"))[0])

    def test_pre_push_blocks_agents_not_humans(self):
        # 例 7 第 4 波:Opus 1/5 读到「用户说直接推也开 PR」仍照推;子代理不加载站点仓的 PreToolUse,所以加 git 层
        main = ["refs/heads/main 1111 refs/heads/main 0000"]
        branch = ["refs/heads/seo/x 1111 refs/heads/seo/x 0000"]
        self.assertTrue(G.pre_push(main, {"CLAUDECODE": "1"})[0])
        self.assertTrue(G.pre_push(["HEAD 1111 refs/heads/master 0000"], {"CODEX_SANDBOX": "seatbelt"})[0])
        self.assertFalse(G.pre_push(main, {})[0])
        self.assertFalse(G.pre_push(branch, {"CLAUDECODE": "1"})[0])
        self.assertFalse(G.pre_push(main, {"CLAUDECODE": "1", "SEO_SUITE_ALLOW_MAIN_PUSH": "1"})[0])

    def test_allows_on_branch_and_unrelated_edits(self):
        self.assertFalse(G.verdict(ev("Write", branch="seo/fix-robots", file_path="/r/public/robots.txt",
                                      content="x"))[0])
        self.assertFalse(G.verdict(ev("Edit", file_path="/r/app/about/page.tsx", old_string="Hello",
                                      new_string="Hello world"))[0])
        self.assertFalse(G.verdict(ev("Bash", command="cat public/robots.txt"))[0])


if __name__ == "__main__":
    unittest.main()
