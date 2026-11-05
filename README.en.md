# EveryInfra SEO Skills

<!-- rq223-banner -->
<p align="center"><img alt="EveryInfra SEO Skills — Free global SEO and GEO skills for Claude Code, Codex and 10 agent hosts" src="assets/banner-en.jpg" width="100%"></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
    <img alt="Eighteen language-market tiles light up while the skill audits example.com for the Korean market and lists the real findings." src="assets/hero-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.37.0-brightgreen" alt="version 0.37.0">
  <img src="https://img.shields.io/badge/license-Apache--2.0-brightgreen" alt="Apache-2.0">
  <img src="https://img.shields.io/badge/markets-18-brightgreen" alt="18 language markets">
  <img src="https://img.shields.io/badge/dependencies-Python_stdlib_only-brightgreen" alt="Python standard library only">
</p>

<p align="center"><a href="README.md">简体中文</a> · <b>English</b> · <a href="README.es.md">Español</a></p>

**Free to download. Use your own AI tool and model.**

**Install in one line** (detects <img src="assets/icons/claude.svg" width="16" height="16" alt=""> Claude Code, <img src="assets/icons/codex.svg" width="16" height="16" alt=""> Codex, <img src="assets/icons/cursor.svg" width="16" height="16" alt=""> Cursor and other hosts on your machine):

```bash
curl -fsSL https://raw.githubusercontent.com/everyinfra/seo-skills/main/install.sh | bash
```

> Maintained by [EveryInfra](https://everyinfra.com/en). When a task needs live data, EveryInfra offers a [web search API](https://everyinfra.com/en/products/search) (17 tools) and [data APIs for 90 platforms](https://everyinfra.com/en/market); this Skill does not depend on them.

EveryInfra SEO Skills is version `0.37.0`, licensed under Apache-2.0. One SEO / GEO workbench Skill: `seo-suite` — instructions, reference notes and output templates. No model calls, no bundled provider, no API key, no runtime dependency. The model and its quota are whatever AI tool you already use.

**The differentiator: global SEO/GEO in one pass.** Teams shipping worldwide don't want a dozen single-market tools. This suite puts **18 language markets** in one workbench, scored market-by-market: Chinese, English, Russian (Yandex/Alice), Korean (<img src="assets/icons/naver.svg" width="16" height="16" alt=""> Naver/AI Briefing), Japanese (Yahoo! Japan + Bing + AI Overviews), Spanish (es-419 LatAm splits), Portuguese (Brazil = <img src="assets/icons/codex.svg" width="16" height="16" alt=""> ChatGPT's strongest market), Arabic (RTL + MSA vs dialects), French (Bill 96), German (DACH Sie/du), Indonesian (baku vs gaul), Hindi (Hinglish three-script reality), Italian (it-CH as its own locale), Turkish (a second Yandex market, ~26%), Vietnamese (diacritic variants + Coc Cốc), Thai (spaceless script segmentation), Polish (diacritic canonicalization), Dutch (Flemish nl-BE). Global capability is **woven into every capability set**, not a separate module — the spine is `overview/multilingual-workflow.md`.

## What only this suite ships

- **18 market portals.** `references/markets/` holds one portal per language market (zh, en, ru, ko, ja, es, pt, ar, fr, de, id, hi, it, tr, vi, th, pl, nl), each written from native-language research in October 2026: engine landscape, local tool stack, community intel, compliance notes.
- **Wikipedia-grade evidence discipline.** Claims carry source types and assertion half-lives; the skill never reports a signal that is not on the page and never promises ranking, traffic or AI-citation gains. GEO advice is bounded by an evidence-constraint file (`references/content/geo-evidence.md`); every Why-now number below has a registered source.
- **A self-updating intel loop.** `intel_check.py` monitors 18 data sources (engine blogs, robots and AI-crawler policies, agent specs, market-share trackers), re-pulls hash changes to confirm them, maps each real change to the affected reference files, and grades the required update P0–P3 under a written self-update protocol — the skill's facts are engineered to decay slower than the market's.
- **A monitoring daemon, not one-shot audits.** `monitor.py` runs daily four-question checks and weekly drift, keeps SQLite snapshots, and raises four-tier alerts with cooldown and anti-fatigue rules (plus SSRF and secret guards); `notify.py` fans notifications out across four channels by severity; GitHub Actions deployment templates are included.
- **CI gates for SEO.** A composite action at the repo root (`action.yml`) audits on every pull request, fails the build below a `min-score` threshold, and emits SARIF / JUnit / GitHub PR annotations via `ci_format.py` — SEO regressions surface like test failures.
- **A pipeline orchestrator.** `project.py` gives each site a workspace and a five-stage state machine (audit → prioritize → fix → verify → monitor): `run triage` chains crawl → audit → health score → priorities in one command, `next` prints the exact command to paste next, `status` shows the score trend. It orchestrates the other scripts as subprocesses and never reimplements them.

## How it got here (0.5 → 0.34)

One arc, compressed: the 0.5 series introduced the **market × capability dual-dimension architecture** — every task picks its market first, then routes by capability — with per-market deep-dives for all 18 markets and 23 cross-region fusion principles; 0.9 re-mined the 17 non-English markets in their own languages (a local community & information-source index, fusion principles grown to 27); 0.16–0.23 turned rules into code — stdlib-only scripts, the `markets.json` 18-market rule layer with dynamic `market_lint.py` checks, golden tests, the specialist modules and the 18 market portals; 0.24–0.30 added the monitoring daemon and the self-update loop; since 0.31 the executable layer has grown to **87 scripts and 1,787 tests** (self_check runs them all on every pass), plus the CI gates and the `project.py` orchestrator. Full history: [CHANGELOG.md](CHANGELOG.md).

## Why now

> Figures come from public studies, vendor studies or forecasts; scope is in brackets. Sources and check results are registered in `skills/seo-suite/references/content/geo-platform-differences.md` section 5 (checked 2026-10-21). Correlation is not causation.

| Metric | Value (scope) |
|---|---|
| GEO services market | $886M (2024) → $7.318B by 2031 (Valuates estimate; estimates vary widely) |
| AI-referred sessions | +527% (Previsible, 19 GA4 sites, Jan–May 2025 vs 2024); update: 166 sites, monthly sessions 9.9x from Nov 2024 to May 2026 |
| Value of AI traffic vs organic, by conversion rate | 4.4x (Semrush, Jun 2025, 500+ SEO topics, vendor study) |
| Brands' organic search traffic by 2028 | −50% or more (Gartner forecast, Dec 2023; not a measurement) |
| Web brand mentions vs backlinks, correlation with AIO brand mentions | Spearman 0.664 vs 0.218, ~3x (Ahrefs, 75K brands) |
| Visibility gain of the three GEO rewrite methods | +30–40% (KDD 2024; gpt-3.5-turbo, fixed top-5 results) |

Global markets (checked 2026-10-21; unverified rows removed):

| Metric | Value | Source |
|---|---|---|
| Yandex share of Russian search | 70.33% (Sep 2026) | StatCounter |
| <img src="assets/icons/naver.svg" width="16" height="16" alt=""> Naver share in Korea | 62.6% on the domestic panel (Apr 2026); StatCounter Sep 2026: Google 47.97%, <img src="assets/icons/naver.svg" width="16" height="16" alt=""> Naver 43.06% | InternetTrend / StatCounter |
| Korean AI Briefing citation pool | almost exclusively Naver-owned properties | Andgentic (vendor blog) |
| AI Overviews appearing on Japanese queries | 76.9% (1,459 queries measured) | Itera (industry) |
| Japan AI-search usage | 21.3% (May 2025) → 37.0% (Feb 2026); 52.3% including AI Mode (Aug 2026) | CyberAgent |
| Brazil <img src="assets/icons/codex.svg" width="16" height="16" alt=""> ChatGPT app | ~54M monthly active users (Jul 2025) | Atlantico (as reported) |
| Language-bound AI citations for Spanish queries | 83-84% Spanish-language sources (Google AIO and <img src="assets/icons/copilot.svg" width="16" height="16" alt=""> Copilot only; Grok 55%+) | Temso (industry study) |
| Yandex share in Turkey | 25.19% (Sep 2026) — a second Yandex market | StatCounter |
| India <img src="assets/icons/codex.svg" width="16" height="16" alt=""> ChatGPT adoption | ~100M weekly active users | Sam Altman (as reported by TechCrunch, Feb 2026) |

## What it does

A single entry point: unified intake (site, market, goals, known issues, available data), then routing across five capability sets — overview / research / content / technical / monitoring — then structured output: conclusions, priorities, and how to validate each one. The target market is the first mandatory intake field, because it decides which engines, toolchains, thresholds and language conventions apply.

| Capability | Typical tasks |
|---|---|
| overview | Site-wide SEO diagnosis, roadmap and prioritization, triage when you don't know where to start, target-market intake gates |
| research | Keyword research and search intent (per-market toolchains + persona × intent SXO layer), SERP analysis (incl. per-market AI-Overview coverage and SERP occupancy), content gaps, competitors, directory-submission engine, backlink profile |
| content | SEO content briefs and drafting, titles and meta descriptions, GEO / AI-search visibility (incl. regional AI platforms), Chinese AI search, video SEO/GEO (<img src="assets/icons/youtube.svg" width="16" height="16" alt=""> YouTube citation mechanics, manual-caption layer), the five-rung ecommerce GEO ladder + on-site SEO for seven marketplaces (incl. MercadoLibre, Trendyol, Allegro, bol, <img src="assets/icons/shopee.svg" width="16" height="16" alt=""> Shopee), content quality, content refresh |
| technical | Technical SEO and single-page audits, robots.txt and AI-crawler policy (incl. regional crawlers, MistralAI, Bytespider), hreflang internationalization, structured data (incl. rich-result status), internal linking and site architecture, entity signals, programmatic SEO, Core Web Vitals, JS rendering and SPA SEO (five-engine rendering differences), Agent-Readiness protocol layer (ARD / WebMCP), server-log analysis (AI-visit measurement, a11y triage), attribution instrumentation |
| monitoring | Rank tracking, backlinks (incl. per-market local directories and Google's link-spam policy boundary; link-price tables removed in Oct 2026), brand mentions (four-tier citation ladder + per-market monitoring channels), algorithm-update attribution (official timelines and data files), SEO drift monitoring, metrics and reporting |
| **Specialist modules** | Domain strategy (selection, expired-domain due diligence, migration checklist, AI-citation inheritance), site-network spectrum and white-hat equivalents, 9-stage programmatic-SEO playbook, site-type playbooks (SaaS / ecommerce / media / local / docs / tools / marketplace / YMYL), CWV four metrics, mobile SEO, penalty recovery, redirects and canonicalization, UGC and site search |
| **Executable layer** | 87 stdlib scripts + the `markets.json` 18-market data layer + 1,787 tests (Oct 2026) — the AI runs the scripts to get facts first, then interprets them per the capability files |

Global capability is **woven into every capability set**, not a separate module: [multilingual-workflow.md](skills/seo-suite/references/overview/multilingual-workflow.md) is the spine (market table, per-market tool stacks, language conventions, compliance), and each capability file carries the regional knowledge relevant to it.

**Bilingual by design.** The skill answers in the user's language and scores each language version of a multilingual site separately. One flagship: the [Chinese AI-search guide](skills/seo-suite/references/content/chinese-ai-search-guide.md), built on a measured 187,818-citation dataset — brand sites take only 1.37% of citations, 28 ranking sites take 9.1% of earliest positions; engine moats for <img src="assets/icons/baidu.svg" width="16" height="16" alt=""> Baidu AI / Tencent Yuanbao / Doubao / <img src="assets/icons/kimi.svg" width="16" height="16" alt=""> Kimi / DeepSeek; CJK thresholds and a 15-item readiness checklist.

Evidence-first: it never reports signals that are not on the page, and never promises ranking, traffic or AI-citation gains. No bundled data — bring your own GSC/GA4 exports; optional free APIs are yours to configure.

## What you bring

- An AI tool that supports Skills, with your own model configured.
- For data-dependent tasks, your own exports: Google Search Console, GA4, Bing Webmaster Tools, or rank-tracker / backlink / crawler exports from tools on your own accounts.
- Optional external APIs (e.g. PageSpeed Insights, Knowledge Graph Search) need your own keys — this repo ships none.
- Outbound actions (outreach email, publishing) are drafted by the skill and executed only after you confirm.

## 60-second taste

Zero dependencies, zero API keys — every script runs on the Python standard library alone. After cloning or unzipping, no install is needed: one command chain takes `example.com` through the minimal loop **audit → layered health score → fix plan**:

```bash
cd seo-skills/skills/seo-suite
python3 scripts/site_audit.py https://example.com --json > /tmp/audit.json
python3 scripts/health_score.py --input /tmp/audit.json
python3 scripts/fix_plan.py --audit /tmp/audit.json --estimate
```

Measured output (2026-10-27): `main score 100.0 → Excellent (no CRITICAL; the missing meta description/H1 on example.com are WARN, listed apart and not deducted from the main score) · Lumar six-category composite 97.2 · AI Search Health 70/100 · fix_plan dry-run previews per-category fix artifacts + benefit estimate (writes nothing by default)`.

<p align="center"><img alt="Real run: terminal output of site_audit, health_score and fix_plan on example.com (2026-10-27)" src="assets/real-run-example-com.png" width="100%"></p>

## Install

**<img src="assets/icons/claude.svg" width="16" height="16" alt=""> Claude Code / <img src="assets/icons/zcode.svg" width="16" height="16" alt=""> ZCode (one line, recommended)** — this repo ships plugin manifests (`.claude-plugin/`, `.zcode-plugin/`):

```bash
claude plugin marketplace add everyinfra/seo-skills
claude plugin install seo-suite@everyinfra-seo-skills
```

**Any Agent Skills host (<img src="assets/icons/codex.svg" width="16" height="16" alt=""> Codex, <img src="assets/icons/cursor.svg" width="16" height="16" alt=""> Cursor, <img src="assets/icons/gemini.svg" width="16" height="16" alt=""> Gemini CLI, <img src="assets/icons/copilot.svg" width="16" height="16" alt=""> Copilot, Windsurf, Goose, Amp, …):** the `install.sh` one-liner above auto-detects installed hosts and adapts to each, or copy `skills/seo-suite` into the tool's skills directory, e.g. `~/.agents/skills/`. Per-host directories and invocation cheat sheet: [HOSTS.md](HOSTS.md). Form-factor analysis: [PACKAGING.md](PACKAGING.md).

## Shipping activity

<!-- readme-stats: charts are regenerated daily, do not edit by hand -->

Commits per day across all EveryInfra repositories, including the private gateway (counts only), and releases per week. The chart is regenerated every day and prints its update time.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme-stats/activity-en-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/readme-stats/activity-en-light.svg">
  <img alt="Commits per day across all EveryInfra repositories and releases per week" src="assets/readme-stats/activity-en-light.svg" width="100%">
</picture>

## Repo layout

```text
seo-skills/
├── README.md / README.en.md / README.es.md   Chinese original, this file, Spanish
├── LICENSE / NOTICE / CHANGELOG.md
├── action.yml                 CI composite action (PR SEO gate)
├── install.sh                 One-command installer
└── skills/seo-suite/
    ├── SKILL.md               Entry point: intake, routing table (script map: references/overview/script-catalog.md)
    ├── scripts/               85 stdlib scripts + markets.json (18-market rule layer)
    ├── tests/                 1,787 tests (self_check runs all)
    ├── examples/              Golden-sample outputs
    ├── references/
    │   ├── overview/          Capability map, routing, intake, multilingual spine
    │   ├── research/ content/ technical/ monitoring/
    │   └── markets/           18 language-market portals
    └── templates/             Research / audit / monitor output templates
```

## Build it with us

No single team knows all 18 markets from the inside. If you know how search works in your market, or spot advice that is out of date, add it: a market portal, a corrected rule, a script or a template. See [CONTRIBUTING.md](CONTRIBUTING.md). Maintainers review every contribution by hand, and contributors are credited in [CONTRIBUTORS.md](CONTRIBUTORS.md). Ideas and questions go to [Discussions](https://github.com/everyinfra/seo-skills/discussions).

## License & attribution

Apache-2.0. Framework points borrowed (summary + link, per NOTICE) from: AgriciDaniel/claude-seo, zubair-trabzada/geo-seo-claude, jianruntech/geo-score, Auriti-Labs/geo-optimizer-skill, coreyhaines31/marketingskills, flaqai/backlink_skills, alvinunreal/awesome-submitlist, indie-hacking/Awesome-SEO-Backlinks, OranAi-Ltd/orangeo-ai-visibility-skill, liangdabiao/GEO-Content-Optimizer-Skill, Ryze-AI-Adgent/open-seo-mcp-skills.
