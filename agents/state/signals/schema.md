# Signal YAML Schema

Hourly market intelligence signals are stored as YAML files in this directory.

## File convention

- **One file per day**, named `YYYY-MM-DD.yaml`.
- Each hourly run appends new signals to the day's file.
- If the file does not yet exist for the current date, the runner creates it.

## Record format

```yaml
date: "YYYY-MM-DD"
signals:
  - id: "sig-YYYYMMDD-HHMM-TICKER-NNN"   # deterministic ID
    found_at: "YYYY-MM-DDTHH:MM:SS"
    ticker: TICKER
    bottleneck: slug                        # from thesis.yaml ticker_map
    source: "domain.com"
    source_url: "https://..."
    headline: "..."
    summary: "1-2 sentence finding"
    relevance: confirms|challenges|novel|neutral
    thesis_ref: "relevant thesis position"
    confidence: high|medium|low
    category: capacity|pricing|demand|margins|guidance|positioning|macro|filing
```

## Field definitions

| Field | Type | Description |
|---|---|---|
| `id` | string | Deterministic ID built from date, time, ticker, and a zero-padded sequence number (e.g. `sig-20260410-0930-NVDA-001`). |
| `found_at` | ISO 8601 | Timestamp when the signal was discovered. |
| `ticker` | string | Stock ticker symbol. |
| `bottleneck` | string | Bottleneck slug from `canonical/30-thesis/thesis.yaml` `ticker_map`. |
| `source` | string | Domain of the originating source. |
| `source_url` | string | Full URL of the source article or filing. |
| `headline` | string | Original or summarized headline. |
| `summary` | string | 1-2 sentence description of the finding. |
| `relevance` | enum | Cross-references against `thesis.yaml` positions. One of: `confirms` (supports an existing thesis position), `challenges` (contradicts a position), `novel` (new information not covered by current thesis), `neutral` (informational, no direct thesis impact). |
| `thesis_ref` | string | The specific thesis position this signal relates to. |
| `confidence` | enum | `high`, `medium`, or `low`. |
| `category` | enum | Aligns with existing prediction categories plus two additions. One of: `capacity`, `pricing`, `demand`, `margins`, `guidance`, `positioning`, `macro`, `filing`. |

## Deduplication rules

1. **Primary dedup key: `source_url`.** Before appending a signal, check whether a record with the same `source_url` already exists in the day's file. If it does, skip the signal.
2. **Fallback for sources without unique URLs:** When a source does not provide a stable unique URL (e.g. aggregated feeds, paywalled redirects), dedup on a **headline substring match** against existing signals in the file. If a substring of the new headline (or vice-versa) matches an existing record, treat it as a duplicate and skip.

## Category alignment

The `category` values reuse the prediction categories already defined in the engine (`capacity`, `pricing`, `demand`, `margins`, `guidance`, `positioning`) and add two new ones:

- **`macro`** -- macroeconomic signals that affect the semiconductor supply chain broadly (e.g. tariffs, trade policy, interest rates).
- **`filing`** -- SEC filings, 8-Ks, proxy statements, and other regulatory documents.

## Relevance cross-referencing

The `relevance` field is determined by comparing the signal content against the positions declared in `canonical/30-thesis/thesis.yaml`. The runner should:

1. Load the current thesis positions.
2. Match the signal's ticker and category to the relevant position.
3. Assign `confirms` if the signal supports the position, `challenges` if it contradicts, `novel` if no matching position exists, or `neutral` if the signal is informational only.
