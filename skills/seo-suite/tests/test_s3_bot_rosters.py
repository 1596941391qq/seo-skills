#!/usr/bin/env python3
"""B42 / B46 bot 名单回归(robots_posture.py 与 ai_referral_log.py;stdlib unittest,零网络)。

期望值来源:references/technical/ai-crawler-policy.md 第一节表格与第七节「已知偏差」,以及它链接的
官方页(2026-10-21 打开核对):
- Amazon(developer.amazon.com/amazonbot):Amazonbot 训练/产品;Amzn-SearchBot 搜索;Amzn-User 用户触发。
- Huawei(aspiegel.com/petalbot):PetalBot 是 Petal 搜索。
- Google 通用爬虫页:Google-CloudVertexBot 是站长委托的 Vertex AI Agents 抓取;GoogleOther 是
  产品团队通用抓取器,「don't affect any specific product」,不是训练类。
- Google 用户触发页:Google-Agent,UA 含 `compatible; Google-Agent;`。
- Cohere(docs.cohere.com/docs/cohere-web-crawlers):目前不用 bot 训练生成式基础模型。
- Mistral(docs.mistral.ai/robots):MistralAI-User 用户触发 / MistralAI-Index 搜索 / MistralAI-Training 训练。
- Meta(web-crawlers 页):meta-webindexer 搜索,UA 为小写 `meta-webindexer/1.1`;meta-externalagent
  UA 同为小写 `meta-externalagent/1.1`。
- OpenAI bots 页:OAI-AdsBot 只做广告落地页审核,UA `OAI-AdsBot/1.0`。
- Yandex 机器人页:`YandexAdditional/1.0`,控制 Yandex AI 回答;不认 `User-agent: *` 通用规则。
- 百度搜索资源平台:UA 含 `Baiduspider/2.0`。
- 官方页没有的 token(Claude-Web、AzureAI-SearchBot、DeepSeekBot、GrokBot、Manus-User、
  Gemini-Deep-Research)不得进显式桶,只能标「未核」。
用法: python3 tests/test_s3_bot_rosters.py(tests/run_tests.py 自动发现本文件)"""
import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
sys.path.insert(0, SCRIPTS)

import ai_referral_log as ar   # noqa: E402
import robots_posture as rp    # noqa: E402


def tier_of(token):
    hits = [b["tier"] for b in rp.AI_BOTS if b["token"] == token]
    return hits[0] if hits else None


class RobotsPostureRosterTests(unittest.TestCase):
    def test_added_bots_and_tiers(self):
        want = {"Baiduspider": "search", "Amzn-SearchBot": "search", "Amzn-User": "user",
                "MistralAI-User": "user", "MistralAI-Index": "search",
                "MistralAI-Training": "training", "meta-webindexer": "search",
                "Google-Agent": "user", "YandexAdditional": "search"}
        for tok, tier in want.items():
            self.assertEqual(tier_of(tok), tier, tok)

    def test_reclassified_per_official_pages(self):
        self.assertEqual(tier_of("Amazonbot"), "training")       # 训练/产品,不是搜索
        self.assertEqual(tier_of("PetalBot"), "search")          # Petal 搜索
        self.assertNotIn(tier_of("Google-CloudVertexBot"), ("training", "search", "user"))
        self.assertNotIn(tier_of("cohere-ai"), ("training",))    # 官方:目前不训练
        self.assertIsNotNone(tier_of("OAI-AdsBot"))
        self.assertNotIn(tier_of("OAI-AdsBot"), ("training", "search"))

    def test_unverified_tokens_marked(self):
        flags = {b["token"]: b.get("verified") for b in rp.AI_BOTS}
        for tok in ("YouBot", "xAI-Bot", "AI2Bot-Dolma", "Bytespider"):
            self.assertIs(flags[tok], False, tok)
        for tok in ("GPTBot", "OAI-SearchBot", "Amzn-SearchBot", "Baiduspider"):
            self.assertIs(flags[tok], True, tok)

    def test_yandexadditional_ignores_wildcard_group(self):
        rep = rp.analyze("User-agent: *\nDisallow: /\n")
        state = {b["token"]: b["state"] for b in rep["bots"]}
        self.assertNotEqual(state["YandexAdditional"], "blocked")   # 只认点名规则
        self.assertEqual(state["Baiduspider"], "blocked")
        self.assertNotIn("YandexAdditional", rep["visibility_failures"])
        rep2 = rp.analyze("User-agent: YandexAdditional\nDisallow: /\n")
        self.assertIn("YandexAdditional", rep2["bots_blocked"])
        self.assertIn("YandexAdditional", rep2["visibility_failures"])

    def test_amazonbot_block_is_not_visibility_failure(self):
        rep = rp.analyze("User-agent: Amazonbot\nDisallow: /\n\nUser-agent: Amzn-SearchBot\nDisallow: /\n")
        self.assertNotIn("Amazonbot", rep["visibility_failures"])
        self.assertIn("Amzn-SearchBot", rep["visibility_failures"])


UA = {
    "GoogleOther": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GoogleOther) Chrome/120.0.0.0 Safari/537.36",
    "meta-webindexer": "meta-webindexer/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/web-crawlers)",
    "Google-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 "
                     "Safari/537.36 (compatible; Google-Agent; +https://developers.google.com/crawling/docs/"
                     "crawlers-fetchers/google-agent)"),
    "OAI-AdsBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-AdsBot/1.0; +https://openai.com/adsbot",
    "YandexAdditional": "Mozilla/5.0 (compatible; YandexAdditional/1.0; +http://yandex.com/bots)",
    "Baiduspider": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "meta-externalagent": "meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/web-crawlers)",
}


class AiReferralRosterTests(unittest.TestCase):
    def test_googleother_not_training(self):
        tok, tier = ar.classify_ua(UA["GoogleOther"])
        self.assertEqual(tok, "GoogleOther")
        self.assertNotEqual(tier, "training")
        self.assertNotIn("GoogleOther", ar.BOT_TIERS["training"])

    def test_unofficial_tokens_not_in_explicit_tiers(self):
        explicit = {b for bs in ar.BOT_TIERS.values() for b in bs}
        for tok in ("Claude-Web", "AzureAI-SearchBot", "DeepSeekBot", "GrokBot",
                    "Manus-User", "Gemini-Deep-Research"):
            self.assertNotIn(tok, explicit, tok)
            self.assertIn(tok, ar.UNVERIFIED_UA_TOKENS, tok)
            self.assertEqual(ar.classify_ua("x %s/1.0" % tok), (tok, "agent_visits"))

    def test_added_tokens_classified(self):
        self.assertEqual(ar.classify_ua(UA["meta-webindexer"]), ("meta-webindexer", "search_index"))
        self.assertEqual(ar.classify_ua(UA["Google-Agent"]), ("Google-Agent", "on_demand_fetcher"))
        # Anthropic 帮助页 18234133(核对 2026-11-05):真实浏览器 UA + Claude-Agent token
        self.assertEqual(ar.classify_ua("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                        "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Claude-Agent"),
                         ("Claude-Agent", "on_demand_fetcher"))
        self.assertEqual(ar.classify_ua(UA["Baiduspider"]), ("Baiduspider", "search_index"))
        self.assertEqual(ar.classify_ua(UA["YandexAdditional"])[0], "YandexAdditional")
        tok, tier = ar.classify_ua(UA["OAI-AdsBot"])
        self.assertEqual(tok, "OAI-AdsBot")
        self.assertNotEqual(tier, "unclassified")

    def test_official_lowercase_meta_ua_matched(self):
        tok, tier = ar.classify_ua(UA["meta-externalagent"])
        self.assertEqual(tok, "Meta-ExternalAgent")       # 官方 UA 全小写,也要认出
        self.assertNotEqual(tier, "unclassified")

    def test_unverified_marked_in_classify_output(self):
        lines = ['1.1.1.1 - - [09/Oct/2026:10:00:00 +0800] "GET /a HTTP/1.1" 200 1 "-" "x GrokBot/1.0"']
        out = ar.render(ar.analyze(lines), classify=True)
        self.assertIn("GrokBot", out)
        self.assertIn("未核", out)


if __name__ == "__main__":
    unittest.main()
