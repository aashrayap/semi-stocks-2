# Hourly Market Intelligence — Remote Trigger Prompt

> You are running as an automated hourly trigger. Do not ask questions — execute the full pipeline.
>
> All writes go under `agents/` only. Never modify files under `canonical/`.
>
> Use `python` (not `uv run python`) — deps are installed via setup script.
>
> If a step fails, log the error and continue to the next step.
>
> Prioritize deep-dive tickers (CRWV, NVDA, MU, COHR, INTC, TSM, LITE) for detailed searches.

Working directory: `/Users/ash/Documents/2026/semi-stocks-2`

---

## PART A — EARNINGS PIPELINE (first run of day only)

1. Get today's date and store it. Use the format `YYYY-MM-DD` for the date and `YYYY-MM` for the month.

2. Check whether the daily earnings pipeline has already run today:

   ```bash
   grep "$(date +%Y-%m-%d)" agents/logs/daily-runner-$(date +%Y-%m).log 2>/dev/null
   ```

3. **If no entry exists for today** (the grep above returns nothing or the file does not exist):

   a. Install dependencies that may not be present in the trigger environment:
   ```bash
   pip install pyyaml beautifulsoup4 pdfplumber
   ```

   b. Run the earnings pipeline steps sequentially. Each step must finish before the next starts:
   ```bash
   cd /Users/ash/Documents/2026/semi-stocks-2 && python agents/src/earnings_calendar.py --days 14
   ```
   ```bash
   cd /Users/ash/Documents/2026/semi-stocks-2 && python agents/src/pre_earnings_predictor.py --all-upcoming --days 7
   ```
   ```bash
   cd /Users/ash/Documents/2026/semi-stocks-2 && python agents/src/transcript_fetcher.py --all-due
   ```
   ```bash
   cd /Users/ash/Documents/2026/semi-stocks-2 && python agents/src/report.py
   ```

   c. Record: `EARNINGS_STATUS="ran"`. Log "Earnings pipeline completed".

4. **If an entry already exists for today**: Record: `EARNINGS_STATUS="skipped"`. Log "Earnings pipeline already ran today, skipping".

---

## PART B — SOURCE MONITORING (every run)

### B.1 — Load context

1. Read `canonical/30-thesis/thesis.yaml` to get the full `ticker_map`. The 18 tracked tickers are:

   | Ticker | Bottleneck | Status | Next Earnings |
   |--------|-----------|--------|---------------|
   | COHR | pluggable_optics | active | 2026-05-07 |
   | LITE | pluggable_optics | active | 2026-05-06 |
   | CIEN | pluggable_optics | active | 2026-06-04 |
   | ALAB | copper_signal_integrity | active | 2026-05-06 |
   | SMTC | copper_signal_integrity | active | 2026-06-04 |
   | MU | memory | active | 2026-06-25 |
   | SNDK | memory | active | 2026-05-01 |
   | TSM | n3_logic | active | 2026-04-17 |
   | NVDA | n3_logic | active | 2026-05-28 |
   | AVGO | n3_logic | active | 2026-06-12 |
   | INTC | n3_logic | active | 2026-04-24 |
   | ASML | euv | next | 2026-04-16 |
   | CRWV | gpu_cloud | active | 2026-05-12 |
   | BE | power | played_out | 2026-05-08 |
   | CORZ | power | played_out | 2026-05-08 |
   | IREN | power | played_out | 2026-05-15 |
   | EQT | power | played_out | 2026-04-23 |
   | TSEM | foundry | active | 2026-05-14 |

2. Read `agents/config.yaml` to get the `deep_dive` list and `sources` config.

   Deep-dive tickers: **CRWV, NVDA, MU, COHR, INTC, TSM, LITE**

3. Read `agents/state/signals/YYYY-MM-DD.yaml` (using today's date) if it exists. Collect all existing `source_url` values into a dedup set. If the file does not exist, the dedup set is empty.

### B.2 — Per-ticker web search (all 18 tickers)

For each ticker in the ticker_map:

- Run: `WebSearch("{ticker} semiconductor news today")`
- Review each result. **Keep only** results that are relevant to:
  - The ticker's bottleneck category (from the table above)
  - Upcoming earnings
  - Capacity, pricing, demand, margins, guidance, or positioning
- **Skip** any result whose URL is already in the dedup set.
- For each kept result, create a signal entry (see signal format in B.6).

### B.3 — SemiAnalysis RSS feed

- Run: `WebFetch("https://newsletter.semianalysis.com/feed")`
- Parse the returned RSS XML. Extract `<title>`, `<link>`, and `<pubDate>` from each `<item>`.
- Flag items published within the last 24 hours that mention any watchlist ticker or bottleneck keywords: `memory`, `EUV`, `fab`, `N3`, `optics`, `HBM`, `DRAM`, `CoWoS`, `wafer`, `packaging`, `GPU`, `accelerator`, `foundry`, `CPO`, `transceiver`, `pluggable`.
- Skip any item whose URL is already in the dedup set.
- Create a signal entry for each flagged item.

### B.4 — Analyst social/web search

Run these three searches:

```
WebSearch("Gavin Baker @GavinSBaker semiconductor OR AI OR chip 2026")
```
```
WebSearch("Leopold Aschenbrenner situational awareness semiconductor OR AI 2026")
```
```
WebSearch("Dylan Patel SemiAnalysis semiconductor OR fab OR memory 2026")
```

For each search:
- Filter for recency: only keep results from the last 7 days.
- Filter for relevance: must mention a watchlist ticker, bottleneck keyword, or thesis-relevant topic (capacity, pricing, demand, margins, positioning, cycle phase).
- Skip URLs already in the dedup set.
- Create a signal entry for each relevant result.

### B.5 — SEC EDGAR 13F (Mondays only)

Check if today is Monday:
```bash
date +%u
```

If today is Monday (output is `1`):

- Calculate the date 7 days ago: `7_DAYS_AGO=$(date -v-7d +%Y-%m-%d)` and `TODAY=$(date +%Y-%m-%d)`.
- Run:
  ```
  WebFetch("https://efts.sec.gov/LATEST/search-index?q=%22situational+awareness%22&forms=13F-HR&dateRange=custom&startdt={7_DAYS_AGO}&enddt={TODAY}")
  ```
- Run:
  ```
  WebFetch("https://efts.sec.gov/LATEST/search-index?q=%22atreides+management%22&forms=13F-HR&dateRange=custom&startdt={7_DAYS_AGO}&enddt={TODAY}")
  ```
- Flag any new filings. Create signal entries with `category: filing`.

If today is not Monday, skip this step entirely.

### B.6 — Financial news (deep-dive tickers only)

For each deep-dive ticker (**CRWV, NVDA, MU, COHR, INTC, TSM, LITE**):

```
WebSearch("{TICKER} earnings OR revenue OR guidance site:seekingalpha.com OR site:finance.yahoo.com OR site:wsj.com")
```

- Filter for recency: results from the last 7 days.
- Filter for relevance: must relate to earnings, revenue, guidance, margins, demand, or capacity.
- Skip URLs already in the dedup set.
- Create a signal entry for each relevant result.

### B.7 — Signal entry format

For every finding from B.2 through B.6, create a YAML signal entry following this exact schema:

```yaml
- id: "sig-YYYYMMDD-HHMM-TICKER-NNN"
  found_at: "YYYY-MM-DDTHH:MM:SS"
  ticker: TICKER
  bottleneck: slug_from_ticker_map
  source: "domain.com"
  source_url: "https://..."
  headline: "Original or summarized headline"
  summary: "1-2 sentence description of the finding"
  relevance: confirms|challenges|novel|neutral
  thesis_ref: "The specific thesis position this relates to"
  confidence: high|medium|low
  category: capacity|pricing|demand|margins|guidance|positioning|macro|filing
```

Field rules:
- **id**: Deterministic. Format is `sig-YYYYMMDD-HHMM-TICKER-NNN` where `HHMM` is the current hour/minute and `NNN` is a zero-padded sequence number starting at 001 for each ticker within this run.
- **found_at**: Current ISO 8601 timestamp.
- **ticker**: The stock ticker symbol.
- **bottleneck**: From the `ticker_map` in thesis.yaml (e.g., `pluggable_optics`, `memory`, `n3_logic`, `euv`, `gpu_cloud`, `power`, `foundry`, `copper_signal_integrity`).
- **source**: The domain name of the source (e.g., `seekingalpha.com`, `newsletter.semianalysis.com`).
- **source_url**: The full URL. This is the primary dedup key.
- **headline**: The article/post title or a concise summary if no title is available.
- **summary**: 1-2 sentences explaining the finding and why it matters.
- **relevance**: Compare against `canonical/30-thesis/thesis.yaml` positions:
  - `confirms` — supports an existing thesis position
  - `challenges` — contradicts a thesis position
  - `novel` — new information not covered by current thesis
  - `neutral` — informational, no direct thesis impact
- **thesis_ref**: The specific thesis position from thesis.yaml that this signal relates to (e.g., "Memory supercycle — peak_shortage", "N3 logic wafers — mid_shortage").
- **confidence**: `high` (primary source, specific data), `medium` (credible source, general claim), `low` (secondary source, speculative).
- **category**: One of `capacity`, `pricing`, `demand`, `margins`, `guidance`, `positioning`, `macro`, `filing`.

### B.8 — Write signals to file

After collecting all new signals:

1. Check if `agents/state/signals/YYYY-MM-DD.yaml` exists.
2. If it exists, read the existing content.
3. Append all new signals to the `signals:` list. Do not duplicate any `source_url` that already exists.
4. If the file does not exist, create it:

```yaml
date: "YYYY-MM-DD"
signals:
  - id: ...
    ...
```

5. Write the file back to `agents/state/signals/YYYY-MM-DD.yaml`.

Track the count of new signals added (`SIGNALS_COUNT`) and the number of distinct tickers that have at least one new signal (`TICKERS_WITH_SIGNALS`).

---

## PART C — LOGGING

Append the following lines to `agents/logs/hourly-intel-YYYY-MM.log` (create the file if it does not exist). Use the current timestamp for each line:

```
[YYYY-MM-DD HH:MM:SS] INFO hourly-market-intel run
[YYYY-MM-DD HH:MM:SS] INFO Earnings pipeline: {EARNINGS_STATUS}
[YYYY-MM-DD HH:MM:SS] INFO Signals found: {SIGNALS_COUNT} new across {TICKERS_WITH_SIGNALS} tickers
[YYYY-MM-DD HH:MM:SS] INFO Sources checked: per-ticker search, SemiAnalysis RSS, analyst social, SEC EDGAR 13F, financial news
```

Replace `{EARNINGS_STATUS}` with `ran` or `skipped`. Replace `{SIGNALS_COUNT}` and `{TICKERS_WITH_SIGNALS}` with the actual counts from Part B. For the sources list, include only the sources that were actually checked (e.g., omit "SEC EDGAR 13F" if today is not Monday).

---

## PART D — COMMIT AND PR

### D.1 — Stage changes

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && git add agents/state/signals/ agents/logs/ agents/reports/ agents/state/predictions/ agents/drafts/
```

### D.2 — Check for staged changes

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && git diff --cached --stat
```

If there are no staged changes, log "No new findings, skipping commit" to `agents/logs/hourly-intel-YYYY-MM.log` and stop here. Do not commit or push.

### D.3 — Commit

Use today's date and current time in the commit message:

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && git commit -m "[signals] YYYY-MM-DD HH:MM market intelligence"
```

Replace `YYYY-MM-DD HH:MM` with the actual current date and time.

### D.4 — Push

Force-push to overwrite previous hourly pushes on the same branch:

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && git push origin HEAD:claude/daily-signals --force
```

### D.5 — Check for existing PR

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && gh pr list --head claude/daily-signals --state open --json number
```

### D.6 — Create or update PR

**If no PR exists** (the list is empty), create one:

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && gh pr create --base main --head claude/daily-signals --title "[signals] YYYY-MM-DD market intelligence" --body "$(cat <<'PRBODY'
## Market Intelligence — YYYY-MM-DD

### Earnings Pipeline
- Status: {ran|skipped}
- {details of what was generated or why it was skipped}

### Signals by Ticker

{For each ticker that has signals today, generate a section like:}

#### {TICKER} ({bottleneck}, {status}) — earnings {next_earnings}
- **[{relevance}]** {headline} ({source}, {found_at time})

{For tickers with no signals, list them together:}

**No new signals:** {comma-separated list of tickers}

### Signals by Source
- SemiAnalysis RSS: {count} articles
- Gavin Baker: {found/nothing new}
- Leopold Aschenbrenner: {found/nothing new}
- Dylan Patel: {found/nothing new}
- SEC EDGAR 13F: {status — checked/skipped (not Monday)}
- Per-ticker web search: {count} findings
- Financial news (deep-dive): {count} findings

### Summary
- {SIGNALS_COUNT} new signals across {TICKERS_WITH_SIGNALS} tickers
- {confirms_count} confirms, {challenges_count} challenges, {novel_count} novel, {neutral_count} neutral
PRBODY
)"
```

Replace all `{...}` placeholders with actual values derived from the signals written in Part B. Use today's actual date for `YYYY-MM-DD`.

**If a PR already exists**, update the body. Read ALL signals from today's `agents/state/signals/YYYY-MM-DD.yaml` file (not just new ones) and regenerate the full PR body so it always reflects the complete day:

```bash
cd /Users/ash/Documents/2026/semi-stocks-2 && gh pr edit {NUMBER} --body "$(cat <<'PRBODY'
{same body format as above, but generated from ALL signals in today's file}
PRBODY
)"
```

Replace `{NUMBER}` with the PR number from the list output.

---

## Error handling

- If any individual step fails, log the error message and continue to the next step.
- If the earnings pipeline fails on a specific script, still run subsequent scripts.
- If a WebSearch or WebFetch call fails, log the failure and move to the next source.
- Always execute Part C (logging) and Part D (commit/PR) even if some source monitoring steps failed.
- Never exit early unless there is a fundamental environment failure (e.g., git is not available).
