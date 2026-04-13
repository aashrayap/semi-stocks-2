---
status: approved
feature: daily
---

# Design: Hourly Market-Hours Intelligence Pipeline

## Relevant Principles

From `CLAUDE.md` and `agents/CLAUDE.md`:
- **Agents write only to `agents/`** — no writes to canonical lanes unless promoting reviewed changes
- **Agents read canonical freely** — thesis.yaml, company data, wiki, engine
- **Drafts are proposals** — human reviews before promotion to canonical
- **Agent reports run parallel** to canonical reports, never replace them
- **Always log runs** under `agents/logs/`
- **Use `uv run python ...`** for execution
- **Bottleneck slug is the join key** across all data layers

From research:
- Fresh clone each trigger run — no persistent state between runs, must read committed state
- Claude Code Remote Triggers: min 1hr cron, `claude/`-prefixed branches by default, env vars for secrets
- Only 3 Python deps declared — new deps need adding to `pyproject.toml`
- Two logging styles coexist — standardize for new code

---

## Decisions

### D1 — Single unified trigger replaces all 4

**Finding:** 4 separate triggers exist with staggered crons. No artifact dependency between them. User requested merge.

**Options:**
1. Keep 4 separate triggers, add new source monitors as additional triggers
2. Merge into 1 unified trigger that runs hourly during market hours

**Decision:** Option 2 — one trigger, hourly cron `0 13-20 * * 1-5` (UTC, = 8 AM - 3 PM ET) plus `0 21 * * 1-5` (4 PM ET close). The trigger prompt orchestrates all work.

**Principle:** Simplicity. One trigger means one cron, one prompt, one branch, one PR pattern. No coordination overhead.

**Scope:** Trigger configuration (web UI / `/schedule`), trigger prompt text, retirement of 3 other triggers.

---

### D2 — Trigger prompt orchestrates directly, not via daily_runner.py

**Finding:** `daily_runner.py` is a subprocess orchestrator designed for local execution. Remote triggers run in a fresh clone with full Claude capabilities (WebSearch, WebFetch, Bash, file tools). Having Claude call `daily_runner.py` via subprocess wastes the agent's intelligence.

**Options:**
1. Trigger runs `uv run python agents/src/daily_runner.py` via Bash
2. Trigger prompt directly orchestrates: run Python scripts for earnings pipeline, then use WebSearch/WebFetch for source monitoring, then commit/PR

**Decision:** Option 2 — the trigger prompt is the orchestrator. It runs the existing Python scripts for the earnings pipeline (they work, no reason to rewrite), then uses its native tools (WebSearch, WebFetch) for source monitoring. This avoids building new Python scripts for every source when Claude already has web access.

**Principle:** Leverage the agent. The trigger IS a Claude session with web tools — use them directly for search/fetch work instead of wrapping everything in Python scripts.

**Scope:** Trigger prompt design. `daily_runner.py` stays for local use but is not invoked by the trigger.

---

### D3 — Earnings pipeline: first run of day only

**Finding:** Earnings calendar, predictions, and transcript fetch are daily-cadence work. Running them hourly is wasteful (same results each hour within a day).

**Decision:** The trigger prompt checks if `agents/logs/daily-runner-YYYY-MM.log` has an entry for today. If yes, skip the earnings pipeline steps. If no, run them first.

**Scope:** Trigger prompt logic (conditional execution).

---

### D4 — Source monitoring: Claude uses WebSearch + WebFetch directly

**Finding:** No source monitoring scripts exist. Building Python scrapers for each source is high effort and fragile (sites change, block scrapers). Claude's WebSearch returns titles + URLs; WebFetch gets page content. This covers web search, RSS, and public web pages.

**Decision:** The trigger prompt monitors sources by:
1. **Per-ticker web search** — `WebSearch("{ticker} semiconductor earnings news")` for each watchlist ticker
2. **SemiAnalysis RSS** — `WebFetch("https://newsletter.semianalysis.com/feed")` and parse titles/dates
3. **Analyst tweets** — `WebSearch("Gavin Baker @GavinSBaker semiconductor site:x.com OR site:twitter.com")` and similar for Leopold, Dylan Patel
4. **SEC EDGAR 13F** — `WebFetch("https://efts.sec.gov/LATEST/search-index?q=...&forms=13F-HR")` for Leopold/Baker CIKs
5. **General financial news** — `WebSearch("{ticker} site:seekingalpha.com OR site:finance.yahoo.com OR site:wsj.com")` per ticker
6. **Finviz** — `WebSearch("{ticker} finviz")` for screening snapshots

No new Python scripts needed for source monitoring. Claude reads the search results, filters for relevance against thesis.yaml, and writes structured signal YAMLs.

**Principle:** Agent-native tools over custom scrapers. WebSearch/WebFetch are maintained by Anthropic, handle rate limiting, and work across all sites without per-site scraper maintenance.

**Scope:** Trigger prompt (source monitoring section).

---

### D5 — Signal output format: new schema, not prediction extension

**Finding:** Predictions are verification-oriented (claim → confirm/miss at earnings). Signals are discovery-oriented (source → finding → relevance). Different lifecycle.

**Decision:** New schema at `agents/state/signals/YYYY-MM-DD.yaml` — one file per day, appended across hourly runs.

```yaml
date: "2026-04-10"
signals:
  - id: "sig-20260410-1305-tsm-001"       # deterministic: date-time-ticker-seq
    found_at: "2026-04-10T13:05:00"
    ticker: TSM
    bottleneck: n3_logic
    source: "seekingalpha.com"
    source_url: "https://seekingalpha.com/article/..."
    headline: "TSMC Q1 revenue beats estimates on AI chip demand"
    summary: "Revenue $26.3B vs $25.8B expected. N3 capacity fully utilized. Management raised FY guidance."
    relevance: confirms                     # confirms|challenges|novel|neutral
    thesis_ref: "N3 capacity constraints remain binding through 2026"
    confidence: high                        # high|medium|low
    category: demand                        # capacity|pricing|demand|margins|guidance|positioning|macro|filing
```

**Principle:** Separate lifecycle from predictions. Signals are ephemeral intelligence; predictions are durable verification contracts. Different consumers, different retention.

**Scope:** `agents/state/signals/` directory, signal YAML schema, dedup logic in trigger prompt.

---

### D6 — Deduplication: hash-based signal IDs

**Finding:** Hourly runs will see the same articles/tweets repeatedly. `transcript_fetcher.py` uses YAML state for dedup.

**Decision:** Each signal gets a deterministic ID: `sig-{date}-{hour}{minute}-{ticker}-{seq}`. The trigger reads the existing day's signal file, extracts all `source_url` values, and skips any finding whose URL is already recorded. For sources without unique URLs (tweets found via search), dedup on `headline` substring match.

**Scope:** Trigger prompt logic (dedup check before appending).

---

### D7 — Branch strategy: push to `claude/daily-signals`, auto-PR into main

**Finding:** Default trigger branch permissions are `claude/`-prefixed only. Pushing to main risks conflicts with Ash's local work. Fresh clone means trigger only sees committed state.

**Decision:** Trigger pushes to `claude/daily-signals` branch. Creates or updates a single PR per day titled `[signals] YYYY-MM-DD market intelligence`. PR body is the human-readable summary (not raw files). Subsequent hourly runs force-push to the same branch and update the PR body.

**Principle:** Drafts are proposals. The PR is the review surface. Ash merges when ready.

**Scope:** Trigger prompt (git/PR section), branch permission config.

---

### D8 — PR body format: structured summary, not raw YAML

**Finding:** User said "I don't want to read the files." The PR body must be the readable product.

**Decision:** PR body format:

```markdown
## Market Intelligence — YYYY-MM-DD

### Earnings Pipeline
- [status of today's earnings run: calendar, predictions, transcripts]

### Signals by Ticker
#### TSM (n3_logic, active) — earnings Apr 17
- **[confirms]** TSMC Q1 revenue beats on AI demand (SeekingAlpha, 13:05)
- **[novel]** New packaging partnership rumored (WCCFTech, 14:10)

#### NVDA (gpu_cloud, active) — earnings May 28
- **[neutral]** No new signals today

### Signals by Source
- SemiAnalysis: 1 new article (...)
- Gavin Baker: no new tweets
- SEC EDGAR: no new 13F filings

### Summary
- X new signals across Y tickers
- Z confirms, W challenges, V novel
```

**Scope:** Trigger prompt (PR body generation section).

---

### D9 — Python dependency additions

**Finding:** Only `beautifulsoup4`, `pdfplumber`, `pyyaml` declared. Trigger uses WebSearch/WebFetch (no Python HTTP library needed for source monitoring). But `feedparser` would help parse RSS in Python if needed.

**Decision:** No new Python dependencies required for the trigger itself. Claude parses RSS directly from WebFetch output. If a future Python-based source monitor is added, `feedparser` and `requests` can be added then.

**Principle:** Don't add dependencies for hypothetical future needs. The trigger's source monitoring uses Claude's native tools, not Python libraries.

**Scope:** No changes to `pyproject.toml`.

---

### D10 — Trigger setup script

**Finding:** Remote triggers support a setup script that runs before each session (e.g., dependency install).

**Decision:** Setup script: `pip install pyyaml beautifulsoup4 pdfplumber` (covers the earnings pipeline Python scripts). `uv` may not be available in the trigger environment, so use pip directly.

**Scope:** Trigger configuration (setup script field).

---

### D11 — Existing launchd job: keep as local backup

**Finding:** `install_launchd.py` and `com.ash.semi-stocks-agents.daily.plist` are installed and working.

**Decision:** Keep the launchd job as-is for local backup/testing. Document that the remote trigger is the primary execution path. No code changes needed.

**Scope:** `docs/process/agent-scheduler.md` update only.

---

### D12 — Logging: trigger writes its own log entries

**Finding:** Existing scripts log to `agents/logs/<name>-YYYY-MM.log`. Trigger runs via subprocess for the Python scripts (which log themselves) but does source monitoring natively.

**Decision:** The trigger appends to `agents/logs/hourly-intel-YYYY-MM.log` for its own source monitoring activity. Python scripts continue logging to their own files when invoked.

**Scope:** Trigger prompt (logging section).

---

## Open Risks

| Risk | Severity | Status |
|---|---|---|
| Trigger credit cost — ~180 runs/month, plan limits undocumented | Medium | Monitor after deployment; reduce to key hours if costly |
| WebSearch may not find very recent tweets (<1hr old) | Low | Acceptable — hourly cadence means next run catches it |
| SemiAnalysis RSS paywall behavior unconfirmed | Low | Try it; fall back to title+preview only |
| Force-push to `claude/daily-signals` loses git history for that branch | Low | Acceptable — PR is the review surface, not branch history |
| Trigger prompt is long — may hit context limits on complex days | Medium | Keep prompt focused; let Claude decide which sources to prioritize |

---

## File Map

### New files
| Path | Purpose |
|---|---|
| `agents/state/signals/YYYY-MM-DD.yaml` | Daily signal findings (created by trigger) |
| `agents/logs/hourly-intel-YYYY-MM.log` | Trigger's own activity log |
| `docs/process/agent-scheduler.md` | Updated to document remote trigger as primary |

### Modified files
| Path | Change |
|---|---|
| `agents/config.yaml` | Add `sources` section with source definitions, remove dead sections |
| `agents/README.md` | Document trigger-based execution |

### Trigger configuration (web UI / `/schedule`)
| Setting | Value |
|---|---|
| Name | `hourly-market-intel` |
| Cron | `0 13-21 * * 1-5` (UTC = 8 AM - 4 PM ET, weekdays) |
| Model | opus |
| Repo | `aashrayap/semi-stocks-2` |
| Branch permissions | Allow `claude/daily-signals` |
| Setup script | `pip install pyyaml beautifulsoup4 pdfplumber` |
| Env vars | (none needed — all sources are public) |
| Tools | Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch |

### Unchanged files
| Path | Why unchanged |
|---|---|
| `agents/src/daily_runner.py` | Stays for local use |
| `agents/src/earnings_calendar.py` | Called by trigger via Bash |
| `agents/src/pre_earnings_predictor.py` | Called by trigger via Bash |
| `agents/src/transcript_fetcher.py` | Called by trigger via Bash |
| `agents/src/report.py` | Called by trigger via Bash |
| `agents/src/post_earnings_scorer.py` | Stays manual |
| `canonical/**` | Read-only for agents |
