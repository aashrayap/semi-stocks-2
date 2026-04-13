---
status: complete
feature: daily
---

# Research Findings: daily

## Flagged Items

### CRITICAL — No signal output format exists
`agents/drafts/signals/` is empty (`.gitkeep` only). `agents/state/signals/` does not exist. No agent script writes signals. The only structured agent output schema is prediction YAML (`agents/state/predictions/<TICKER>-<QUARTER>.yaml`). The `daily-2026-04-07.md` is **human-authored narrative**, not machine-generated — no schema, no YAML frontmatter, no consistent fields. A signal finding format must be designed from scratch.

### CRITICAL — Trigger configs are cloud-only
No trigger definition files exist in `.claude/` or anywhere in the repo. The 4 existing triggers are configured entirely in the Claude Code web UI. Their prompts, env vars, setup scripts, and branch permissions cannot be verified from the codebase. This means the unified trigger must be configured via `/schedule` or the web UI, not from repo files.

### HIGH — SemiAnalysis RSS feed exists and may expose full content
`newsletter.semianalysis.com/feed` is RSS 2.0 with `<content:encoded>` containing full HTML article content. Whether this includes paywalled articles or truncates them is unconfirmed (Substack typically truncates paid posts in RSS). This is the primary programmatic access point for SemiAnalysis content.

### HIGH — Prediction overwrites without guard
`pre_earnings_predictor.py` has no "already generated" check — re-running overwrites prior predictions including any manually adjusted ones. Only `transcript_fetcher.py` implements true idempotent state tracking via `agents/state/transcripts.yaml`.

### MEDIUM — 13F Filing Monitor trigger is disabled
The only trigger designed for the core 13F data source (which feeds both Leopold and Baker canonical files) is disabled. The 13F pipeline design doc (`docs/process/13f-pipeline-design.md`) is entirely unimplemented — no `fund_13f.py` exists.

### MEDIUM — Python constrained to `>=3.10,<3.11`
`pyproject.toml` pins Python strictly below 3.11. May affect library compatibility for new dependencies.

### LOW — Remote trigger interaction undocumented
`earnings-calendar` (12:00 UTC) runs 15 minutes before `predictor-and-transcript-fetcher` (12:15 UTC), but no artifact dependency or handshake exists between them. Each trigger reads from canonical lanes independently. Fresh clone per run means a trigger only sees what was committed by a previous trigger's push.

---

## Findings

### Q1 — CLI arguments for each agent script

All scripts support `--date` (YYYY-MM-DD override) and `--dry-run` (stdout-only). Key per-script flags:

| Script | Key flags | Evidence |
|---|---|---|
| `daily_runner.py` | `--date` only | `daily_runner.py:103-104` |
| `earnings_calendar.py` | `--days` (int, default 14), `--dry-run`, `--date` | `earnings_calendar.py:538-542` |
| `pre_earnings_predictor.py` | `--ticker`, `--quarter`, `--all-upcoming`, `--days` (int, default 7), `--dry-run`, `--date` | `pre_earnings_predictor.py:1031-1044` |
| `transcript_fetcher.py` | `--ticker` XOR `--all-due` (required), `--quarter`, `--source` (choices: q4cdn/ir_scrape/motley_fool), `--dry-run` | `transcript_fetcher.py:1210-1221` |
| `post_earnings_scorer.py` | `--ticker` (required), `--quarter` (required), `--interactive`, `--dry-run`, `--date` | `post_earnings_scorer.py:556-568` |
| `report.py` | `--date` only | `report.py:631-639` |
| `install_launchd.py` | `--hour` (int, default 6), `--minute` (int, default 5), `--load`, `--run-now` | `install_launchd.py:94-97` |

**Confidence:** High | **Conflicts:** None

### Q2 — daily_runner.py invocation sequence

Hardcoded, ordered list — no dynamic discovery. Sequence:
1. Parse `agents/config.yaml` for `alerts.earnings_days_out` (default 14) and `predictions.auto_generate_days_before` (default 7)
2. `earnings_calendar.py --days <N> [--date]`
3. `pre_earnings_predictor.py --all-upcoming --days <N> [--date]`
4. `transcript_fetcher.py --all-due` (no `--date` — always uses real today)
5. `report.py [--date]` (always runs even if steps 1-3 fail)

Error handling: failures accumulate in a list; all steps still run. Exit 1 if any failed, exit 0 otherwise.

**Evidence:** `daily_runner.py:76-157` | **Confidence:** High

### Q3 — agents/config.yaml structure

8 top-level sections. `polling`, `watchlist`, `paths`, and `output` are **dead config** — no script reads them. Active sections:

| Section | Read by |
|---|---|
| `alerts.earnings_days_out` | `daily_runner.py:45` |
| `predictions.auto_generate_days_before` | `daily_runner.py:46` |
| `deep_dive` (7 tickers) | `earnings_calendar.py`, `report.py`, `transcript_fetcher.py` |
| `transcript_sources` (3 tiers) | `transcript_fetcher.py` |

**Evidence:** `agents/config.yaml:1-108` | **Confidence:** High

### Q4 — report.py HTML output

Reads: prediction YAMLs, thesis.yaml, config.yaml (`deep_dive`), all log files (last 8 entries), drafts directory file counts. Renders 6 sections: Summary → Prediction Overview → Prediction Detail → Upcoming Earnings → Drafts Pipeline → Recent Activity. Writes to `agents/reports/latest.html` only. Dead code: `load_company_data()` defined but never called.

**Evidence:** `report.py:521-640` | **Confidence:** High

### Q5 — Prediction YAML schema

```yaml
ticker: TSM
quarter: "Q1 2026"           # space in value, underscore in filename
predicted_at: "2026-04-10"
earnings_date: "2026-04-17"
bottleneck: n3_logic
bottleneck_status: active
predictions:
  - claim: "..."
    category: capacity        # capacity|pricing|demand|margins|guidance|positioning
    basis:
      - source: "canonical/30-thesis/thesis.yaml"
        detail: "..."
    confidence: low           # high|medium|low
    verify_at: "Q1 2026 earnings"
    status: pending           # pending|confirmed|missed|partial|revised
positioning_context:
  leopold: "..."
  baker: "..."
  implied_signal: "..."
  divergence_detail: "..."    # optional
track_record:
  total_predictions: 0
  confirmed: 0 / missed: 0 / partial: 0 / revised: 0
  accuracy: null
```

**Evidence:** `agents/state/predictions/ASML-Q1_2026.yaml`, `TSM-Q1_2026.yaml` | **Confidence:** High

### Q6 — transcripts.yaml

Does not exist. Inferred schema from `transcript_fetcher.py:1103-1118`: keyed by `TICKER.QUARTER` with `fetched_at`, `source`, `source_url`, `path`, `fidelity`.

**Confidence:** High (absence), Medium (schema)

### Q7 — thesis.yaml structure

- `cascade`: ordered bottleneck stages with `name`, `status` (played_out|active|next), `cycle_phase`, `signals[]`, `cycle_risk_flags[]`
- `ticker_map`: flat dict, each ticker has `bottleneck` (slug), `status`, `next_earnings` (ISO date), optional `also` (secondary bottleneck)
- Forward claims are NOT here — they live in `canonical/20-data/companies/<TICKER>/` YAMLs

**Evidence:** `canonical/30-thesis/thesis.yaml:1-162` | **Confidence:** High

### Q8 — runtime_paths.py

Exports: `repo_root()`, `wiki_root()`, `data_root()`, `thesis_path()`, `engine_stage()`, `reports_root()`. Canonical-first fallback. `pre_earnings_predictor.py` supports `SEMI_STOCKS_READ_ROOT` env override; others don't.

**Evidence:** `agents/src/runtime_paths.py:5-44` | **Confidence:** High

### Q9 — canonical/20-data/ schemas

**Sources:** Leopold + Baker use identical 13F schema (`positions[]`, `exits[]`, `cross_checked[]`). SemiAnalysis uses distinct schema (`signals[]`, `media[]`, `market_data[]`).

**Companies:** Per-ticker quarterly YAMLs with `source_artifacts[]`, `financials`, `guidance`, `forward_claims[]`, `thesis_signals[]`, `positioning`.

**Confidence:** High

### Q10-12 — Trigger configuration

Cannot answer from repo. No trigger definition files in `.claude/`. Must check web UI or `/schedule list`.

**Confidence:** Low

### Q13-15 — Process docs

- Earnings pipeline doc describes 4-lane funnel; agents implement only the mechanical steps, not wiki synthesis
- Agent scheduler doc is accurate for launchd but being superseded
- 13F pipeline design is entirely unimplemented

**Confidence:** High

### Q16 — Logging

Two incompatible styles (Python `logging` vs manual `write_log()`). Report reader handles both via regex. Monthly filename rotation, no size-based rotation.

**Confidence:** High

### Q17 — daily-2026-04-07.md format

Human-authored narrative. No machine-parseable schema. Loosely structured by bottleneck sections with bold tickers, descriptions, URLs, and "Significance:" bullets.

**Confidence:** High

### Q18 — Network failure handling

Tiered fallback, no retry. Motley Fool Tier 3 URL guesser can take >1 minute per ticker (21-day × 3 patterns × 1-sec delay = 63+ requests).

**Confidence:** High

### Q19 — State tracking

Only `transcript_fetcher.py` has idempotent state. Everything else regenerates on every run. Predictions overwrite without guard.

**Confidence:** High

### Q20 — Claude Code Remote Trigger API

Cron (min 1hr), env vars, setup script, tools, model, branch permissions (default `claude/`-prefixed). Fresh clone each run. `/schedule` CLI or web UI. Session-scoped cron separate (CronCreate, 7-day expiry, max 50).

**Confidence:** High

### Q21 — SemiAnalysis RSS

RSS 2.0 at `newsletter.semianalysis.com/feed`. Has `content:encoded` (full HTML). `/archive` for listing. Paywall truncation behavior unconfirmed.

**Confidence:** High (exists), Medium (paywall)

### Q22 — SEC EDGAR EFTS

Undocumented Elasticsearch at `efts.sec.gov/LATEST/search-index`. Params: `q`, `forms`, `dateRange`, `startdt`/`enddt`, `from`. 10 req/sec, User-Agent required. Not officially supported.

**Confidence:** Medium

### Q23 — 13F aggregators

Only WhaleWisdom has API (HMAC auth, 20 req/min, last 8 quarters free). Others are web-only.

**Confidence:** High

### Q24 — Finviz

Screener at `finviz.com/screener.ashx` with URL params. Free: delayed, no export. Elite ($25-40/mo): real-time, CSV, API. Unofficial Python wrapper on PyPI.

**Confidence:** High

### Q25 — WebSearch tool

Returns `url` + `title` per result (~8 results). Content requires separate WebFetch. $10/1000 searches.

**Confidence:** High (features), Medium (result count)

### Q26-30 — Cross-ref findings

- No signal format exists — prediction YAML is closest but different lifecycle
- Triggers don't depend on each other's artifacts
- Daily report cites 12+ sources not in canonical data
- Only 3 Python deps declared (`beautifulsoup4`, `pdfplumber`, `pyyaml`)
- Engine reads exclusively from `canonical/20-data/`, never `agents/`

**Confidence:** High

---

## Patterns Found

1. **Canonical funnel strictly enforced**: Engine reads only `canonical/20-data/`. Agents write only to `agents/`. No cross-contamination.
2. **Bottleneck slug is the join key**: Same slugs across thesis, company data, source positions, and predictions.
3. **YAML everywhere**: All structured data. Reports are HTML/MD.
4. **`--dry-run` + `--date` universal**: Testing pattern on all scripts.
5. **`source_ref` traceability**: Company YAMLs link claims back to source documents.
6. **Two logging styles coexist**: Python `logging` vs manual `write_log()`. Report handles both.
7. **Dead config sections**: `polling`, `watchlist`, `paths`, `output` in config.yaml unused.

---

## Core Docs Summary

| Doc | Key content | Status vs reality |
|---|---|---|
| `docs/process/earnings-pipeline.md` | 4-lane funnel from raw → thesis | Partially implemented |
| `docs/process/agent-scheduler.md` | launchd at 06:05, runtime conditions | Accurate, being superseded |
| `docs/process/13f-pipeline-design.md` | edgartools + hybrid pipeline for 13F | Entirely unimplemented |
| `agents/README.md` | Agent usage, commands, paths | Accurate |
| `agents/config.yaml` | 8 sections, 4 dead | Partially dead |

---

## Open Questions

1. **What are the actual trigger prompts?** Cannot verify from repo — must check web UI or `/schedule list`.
2. **Does SemiAnalysis RSS expose paywalled content?** Needs a paid-article test.
3. **What is the trigger credit cost?** ~180 runs/month. Plan-tier limits undocumented.
4. **Should signal format extend prediction YAML or be its own schema?** Predictions are verification-oriented (claim → confirm/miss). Signals are discovery-oriented (source → finding → relevance). Different lifecycle.
5. **How should trigger-committed artifacts avoid conflicts with Ash's local work?** Triggers push to repo; local pull could conflict.
