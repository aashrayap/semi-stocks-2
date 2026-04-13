---
status: approved
feature: daily
---

# Feature Spec: Hourly Market-Hours Intelligence Pipeline via Claude Code Remote Triggers

## Goal

Build an automated intelligence pipeline that runs hourly during US market hours using Claude Code Remote Triggers (Anthropic cloud). The pipeline combines the existing earnings-focused agent sidecar with new source-monitoring agents that track semiconductor intelligence across all sources Ash uses. Each hourly run produces structured findings, commits artifacts, and opens/updates a daily PR with a clean summary.

## Execution Platform

**Claude Code Remote Triggers** — not GitHub Actions, not local launchd.

- Runs on Anthropic's cloud infrastructure (no Mac dependency)
- Clones the repo fresh each run from GitHub
- Can commit, push, and create PRs via `gh` CLI
- Supports `WebSearch`, `WebFetch`, and full network access
- Cron scheduling with 1-hour minimum interval
- Environment variables for API keys/secrets
- Setup script for Python deps (`uv sync` or `pip install`)

### Existing Triggers (Already Running)

| Trigger | Cron | Model | Status | What it does |
|---|---|---|---|---|
| `daily-briefing` | `0 11 * * *` | opus | enabled | General daily briefing |
| `earnings-calendar` | `0 12 * * *` | opus | enabled | Earnings calendar scan |
| `predictor-and-transcript-fetcher` | `15 12 * * *` | opus | enabled | Predictions + transcript fetch |
| `13F Filing Monitor` | `0 23 * * *` | sonnet | disabled | 13F filing checks |

### Target Schedule

Hourly during US market hours: `0 13-20 * * 1-5` UTC (9 AM - 4 PM ET), plus one pre-market run at `0 12 * * 1-5` UTC (8 AM ET). Total: ~9 runs per trading day.

## What Exists Today (Being Transferred / Consolidated)

### Existing Agent Scripts (agents/src/)

| Script | What it does | Current trigger | Outputs |
|---|---|---|---|
| `earnings_calendar.py` | Scans `thesis.yaml` for earnings within N days, maps tickers to bottlenecks, surfaces forward claims coming due | Remote trigger `earnings-calendar` + local `daily_runner.py` | `agents/reports/earnings-alert-YYYY-MM-DD.md`, log |
| `pre_earnings_predictor.py` | Generates deterministic predictions 7 days before earnings using thesis + wiki + data (no LLM) | Remote trigger `predictor-and-transcript-fetcher` + local `daily_runner.py` | `agents/state/predictions/{TICKER}-{QUARTER}.yaml`, log |
| `transcript_fetcher.py` | Fetches earnings call transcripts via 3-tier strategy for deep-dive tickers post-earnings | Remote trigger `predictor-and-transcript-fetcher` + local `daily_runner.py` | `agents/drafts/earnings/`, log |
| `report.py` | Builds consolidated HTML report from all predictions, scorecards, alerts, logs | Local `daily_runner.py` only | `agents/reports/latest.html` |
| `daily_runner.py` | Orchestrator: runs the above 4 in sequence | Local launchd at 06:05 | All of the above |
| `post_earnings_scorer.py` | Scores predictions against actual results | **Manual only** (interactive) — excluded from automation | Updated prediction YAMLs |

### Existing Transcript Fetcher Tiers

| Tier | Method | Tickers | Config ref |
|---|---|---|---|
| Tier 1 | q4cdn PDF (FactSet/CallStreet) | CRWV (`s205.q4cdn.com`), NVDA (`s201.q4cdn.com`) | `agents/config.yaml:80-87` |
| Tier 2 | IR page scrape | TSM (`investor.tsmc.com`), MU (`investors.micron.com`), INTC (`intc.com`) | `agents/config.yaml:89-96` |
| Tier 3 | Motley Fool fallback | All 7 deep-dive tickers | `agents/config.yaml:98-108` |

Note: Tier 1/2 frequently 403 in practice; Motley Fool fallback was hardened during migration.

### Existing Config (agents/config.yaml)

- **Deep-dive tickers:** CRWV, NVDA, MU, COHR, INTC, TSM, LITE
- **Full watchlist:** 18 tickers including ASML, ALAB, SMTC, BE, CORZ, IREN, EQT, TSEM
- **Declared but unimplemented:** `thirteenf_monitor` (weekly), `signal_scanner` (daily)

## What's New (Being Added)

### Source Monitoring Agents

New agents that scan external intelligence sources for semiconductor-relevant signals per-ticker and per-source. Each produces structured finding YAML and human-readable summary.

#### Primary Analyst Sources (Already Canonical in Repo)

| Source | Entity | What to track | Repo refs |
|---|---|---|---|
| **Gavin Baker / Atreides Management** | 13F filer, CIK `0001777813`, Twitter `@GavinSBaker` | 13F filings, tweets on semi cycles, fund positioning | `canonical/20-data/sources/baker/`, `config.yaml:12-19` |
| **Leopold Aschenbrenner / Situational Awareness LP** | 13F filer, CIK `0002045724` | 13F filings, AI scaling thesis updates, blog posts | `canonical/20-data/sources/leopold/`, `config.yaml:2-9` |
| **Dylan Patel / SemiAnalysis** | Newsletter at `newsletter.semianalysis.com` | Articles, tweets, fab/memory/EUV data | `canonical/20-data/sources/semianalysis/`, `config.yaml:22-26` |

#### Semiconductor Industry Sources (Already Referenced in Repo)

| Source | What it provides | Repo refs |
|---|---|---|
| **TrendForce** | DRAM contract pricing, optical transceiver shipment data | `thesis.yaml:44`, `semianalysis/signals.yaml:104-113` |
| **SIA (Semiconductor Industry Association)** | Global semiconductor sales data | `agents/reports/daily-2026-04-07.md:51` |
| **WSTS** | Global semi industry cycle data (40+ years) | `baker-cyclicality-thesis.md:237,286` |
| **Susquehanna Financial Group** | Semiconductor lead time tracking (monthly) | `baker-cyclicality-thesis.md:283` |
| **TechInsights** | Automotive semiconductor lead times | `baker-cyclicality-thesis.md:284` |
| **SEMI** | Wafer fab equipment (WFE) spending | `baker-cyclicality-thesis.md:285` |
| **MacroTrends** | Historical revenue, P/E, stock prices | `baker-cyclicality-thesis.md:281` |

#### Financial News & Analysis (Referenced in Repo + Ash's List)

| Source | Category | Already in repo? |
|---|---|---|
| **Seeking Alpha** | Research/analysis | Yes — `daily-2026-04-07.md:27` |
| **Motley Fool** | Transcript fallback + analysis | Yes — transcript Tier 3 + daily report |
| **Bloomberg** | Breaking news, features | Yes — `daily-2026-04-07.md:53` |
| **Yahoo Finance** | Price data, transcripts | Yes — NVDA transcript compilation |
| **Tom's Hardware** | Semiconductor/DC news | Yes — `daily-2026-04-07.md:30` |
| **WCCFTech** | Semiconductor news | Yes — `daily-2026-04-07.md:21` |
| **CNBC** | Market news, earnings | Yes — `semianalysis/signals.yaml:86` |
| **WSJ** | Financial news | New — from Ash's reference list |
| **FT (Financial Times)** | Financial news, deep analysis | New — from Ash's reference list |
| **Axios** | Tech/business news | New — from Ash's reference list |

#### Research Services (From Ash's Reference List)

| Source | What it provides |
|---|---|
| **Morningstar** | Fundamental analysis, fair value estimates |
| **Value Line** | Investment survey, rankings |
| **BCA Research** | Macro strategy |
| **Sellside (Victor Shvet / Macquarie)** | Macro/equity strategy |

#### Data & Charting Platforms (From Ash's Reference List)

| Source | What it provides |
|---|---|
| **Finviz** | Daily screening, heat maps, technicals (Ash's primary daily) |
| **Kifin** | Financial data |
| **Y Charts** | Fundamental charts, economic indicators |
| **Trading Economics** | Macro data, commodities |
| **Think or Swim** | Charting, options data |

#### Real-Time / Breaking News (From Ash's Reference List)

| Source | What it provides |
|---|---|
| **News Squawk / First Squawk** | Real-time market-moving headlines |

#### 13F / Ownership Aggregators (Already in Repo)

| Source | Repo refs |
|---|---|
| **SEC EDGAR** | `config.yaml:8,18`, `13f-pipeline-design.md` |
| **WhaleWisdom** | `config.yaml:7,17` |
| **InsideArbitrage** | `config.yaml:19` |
| **StockZoa** | `leopold/q4_2025.yaml:16`, `baker/q4_2025.yaml:16` |
| **HedgeFollow** | `leopold/q4_2025.yaml:17`, `baker/q4_2025.yaml:17` |
| **13F.info** | `leopold/q4_2025.yaml:18`, `baker/q4_2025.yaml:18` |
| **DanielScrivner.com** | `config.yaml:9` (Leopold-specific) |

#### Other Sources Found in Repo

| Source | Context | Repo ref |
|---|---|---|
| **Invest Like the Best podcast** | Baker interviews EP.385, EP.451 | `baker-cyclicality-thesis.md:275-276` |
| **Dwarkesh Podcast** | Dwarkesh x Dylan Patel on AI infra | `canonical/10-wiki/raw/dwarkesh-dylan-*` |
| **Latent Space Podcast** | Google/Amazon capex, GitHub commit shares | `semianalysis/signals.yaml:97` |
| **TheMarket.ch** | Baker interview | `baker-cyclicality-thesis.md:277` |
| **More Than Moore (Substack)** | SemiAnalysis lawsuit coverage | `daily-2026-04-07.md:59` |
| **SimplyWallSt** | Stock analysis | `daily-2026-04-07.md:9` |
| **QuiverQuant** | Alt data, institutional tracking | `daily-2026-04-07.md:42` |
| **StockTitan** | Press release aggregation | `daily-2026-04-07.md:40` |
| **Bankless Times** | Crypto/tech finance news | `daily-2026-04-07.md:35` |
| **FXLeaders** | Market news | `daily-2026-04-07.md:9` |
| **TimothySykes** | Stock news | `daily-2026-04-07.md:14` |
| **24/7 Wall St** | Market analysis | `semianalysis/signals.yaml:92` |

### Per-Ticker Hourly Scan

For each ticker in the watchlist, every hourly run:
- Searches all monitorable sources for mentions of that ticker
- Cross-references findings against `thesis.yaml` positions and forward claims
- Flags anything that: confirms a thesis position, challenges it, or is novel

### Per-Source Scan

For each source, every hourly run:
- Checks for new content since last run
- Extracts semiconductor-relevant signals
- Tags findings with relevant tickers from the watchlist
- Deduplicates against previously committed findings

## Users and Workflows

**Primary user:** Ash (sole operator)

**Workflow 1 — Passive morning review:**
Given the pipeline ran overnight/pre-market,
When Ash opens GitHub or checks email,
Then there is a daily PR with a structured summary of all findings — no need to read raw files.

**Workflow 2 — Intraday signal during market hours:**
Given a source monitor detects a material signal (Baker tweet about TSM, SemiAnalysis article on NVDA capacity),
When the hourly run completes,
Then the daily PR is updated with the new finding linked to the relevant ticker and thesis position.

**Workflow 3 — Earnings pipeline (transferred):**
Given the existing daily runner logic,
When the first trigger of the day fires,
Then earnings calendar, predictions, transcript fetches, and report rebuild happen as they do today, with artifacts committed back.

## Acceptance Criteria

1. **AC-1:** Claude Code Remote Triggers are configured to run hourly during US market hours (8 AM - 4 PM ET, weekdays).
2. **AC-2:** The existing daily_runner.py pipeline (earnings calendar, pre-earnings predictor, transcript fetcher, report) executes in the first run of the day and commits artifacts back.
3. **AC-3:** Source monitoring covers at minimum: Gavin Baker (tweets/13F), Leopold (13F/blog), Dylan Patel/SemiAnalysis (articles/tweets), Google web search for each watchlist ticker, and Finviz screening data.
4. **AC-4:** Each source monitor produces structured output (YAML finding + human summary) under `agents/state/signals/` or `agents/drafts/signals/`.
5. **AC-5:** A per-ticker scan cross-references all source findings against `thesis.yaml` and flags confirmations, challenges, and novel signals.
6. **AC-6:** Each daily run creates or updates a single PR with a clean summary body (not raw files). Findings are appended across hourly runs within the same day.
7. **AC-7:** Empty runs (no new findings) do not create PRs or noise commits.
8. **AC-8:** Secrets/API keys are stored as trigger environment variables, never committed.
9. **AC-9:** The local launchd job can be decommissioned after remote triggers are verified.
10. **AC-10:** Additional sources from Ash's reference list (WSJ, FT, Seeking Alpha, Morningstar, Finviz, Yahoo Finance, etc.) are integrated as available — web-searchable sources first, paywalled sources as titles/snippets only.

## Boundaries

### In scope
- Claude Code Remote Trigger configuration (cron, env vars, setup scripts, prompts)
- Consolidation of existing 4 triggers into a unified hourly pipeline
- New source monitoring agents for all sources listed above
- Per-ticker cross-referencing against thesis
- Auto-PR creation/update with summarized findings
- Structured signal output format (YAML + summary)

### Out of scope
- `post_earnings_scorer.py` — stays manual/interactive
- Real-time / sub-hourly push-based alerting (webhook, WebSocket)
- Mobile notifications or Slack integration
- Backfilling historical signals
- Full-text scraping of paywalled content (SemiAnalysis articles, FT, WSJ) — titles/snippets only

### Ask first
- Whether to use Claude API (LLM) for relevance filtering and summarization of findings, or keep deterministic
- Budget/rate-limit comfort level for hourly runs (each trigger run uses Claude API credits)
- Which paywalled sources Ash has subscriptions to (affects scraping depth)
- Whether the 4 existing triggers should be merged into 1 unified trigger or kept separate with the new ones added alongside

## Risks and Dependencies

| Risk | Impact | Mitigation |
|---|---|---|
| Twitter/X monitoring for Baker, Leopold, Patel — no official API access | Can't get tweets directly | Use `WebSearch` to search for recent tweets by handle; surface via Google cache/Nitter mirrors |
| SemiAnalysis is paywalled | Can't scrape full articles | Monitor titles/previews via `newsletter.semianalysis.com` RSS or search snippets |
| Trigger run count / API credit cost | 9 runs/day * weekdays = ~180 runs/month | Monitor credit usage; reduce to key hours if needed |
| Fresh clone each run — no persistent state between runs | Must read committed state from repo each time | All state lives in `agents/state/` committed to repo; each run reads from main |
| Commit conflicts if Ash pushes while trigger is running | Push could fail | Triggers push to a `claude/daily-signals` branch, PR into main |
| Source monitoring returns noise | PRs become unreadable | Relevance filtering against thesis.yaml watchlist; confidence scoring; only surface ticker-matched or high-signal items |
| Some sources block automated scraping (Finviz, Bloomberg) | Can't access data | Fall back to `WebSearch` snippets; flag blocked sources |
| 13F filings are quarterly, not hourly | Mostly idle checks | Run 13F monitor once daily or weekly, not hourly |
