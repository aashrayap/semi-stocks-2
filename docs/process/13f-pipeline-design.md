 # 13F Pipeline Upgrade — Design Research

Date: 2026-04-03
 
## Problem

Current ingestion is manual: human reads 13F filing, cross-checks against 5-6 aggregators,
hand-writes YAML. Slow, error-prone, doesn't scale to tracking more funds.

## Approaches Evaluated

### 1. Shkreli's 13F repo (github.com/martinshkreli/13F)

**Architecture:** Four standalone Python scripts, no abstraction.

- `retrieve.py` — Hits SEC EDGAR full-text search API (`efts.sec.gov/LATEST/search-index`)
  directly with POST requests. Downloads raw 13F-HR filings for a date range. Uses the
  internal EDGAR Elasticsearch endpoint (not the public EDGAR API).
- `downloadidx.py` — Downloads EDGAR daily index files (master list of all filings).
- `download.py` — Parses `.idx` files (fixed-width format), ranks by date, outputs CSV by quarter.
- `13f.py` — **Key tool.** Parses a single 13F XML file using `xml.etree.ElementTree`.
  Strips out put/call options to show true equity exposure. Only dependency: `pandas`.

**Key insight:** 13F reports notional value for options. A $1.2B call position (like Leopold's
CRWV) may only represent $100-200M in premium. Shkreli's tool strips this distortion.

**Strengths:**
- Zero dependencies beyond pandas
- Direct EDGAR XML parsing — no middlemen
- Options stripping for true equity exposure
- Bulk filing download (ALL 13F-HRs in a date range)

**Weaknesses:**
- No QoQ diffing
- No cross-checking
- No structured output (just prints to console)
- No bottleneck/thesis mapping
- Hardcoded dates in retrieve.py

### 2. edgartools (PyPI package)

**Architecture:** Full-featured Python library wrapping SEC EDGAR APIs.

- No API key needed, no rate limits
- Parses 13F into Python objects and DataFrames
- Supports all SEC form types (10-K, 10-Q, 8-K, etc.)
- Handles CIK lookup, company search

**Strengths:**
- Most complete free option
- Clean Python API
- Active maintenance

**Weaknesses:**
- Heavier dependency
- Doesn't strip options automatically
- No thesis/bottleneck mapping

### 3. Other options evaluated

- `sec-edgar-downloader` — Simple download-only, good for bulk pulls
- `sec-api.io` — Paid API, real-time streaming, good for production
- `hedge-fund-tracker` (GitHub) — AI-powered 13F insights
- `13F-Network` (GitHub) — Graph visualization of 13F holdings

## Recommended Hybrid Pipeline

```
SEC EDGAR XML (raw source of truth)
     |
     v
edgartools or Shkreli-style XML parser
(parse 13F, separate equity vs options)
     |
     v
Auto-generate draft YAML
(positions, values, share counts, option type)
     |
     v
Cross-check step (flag discrepancies only)
     |
     v
Human review + bottleneck tagging (the value-add)
     |
     v
Commit to canonical/20-data/sources/<fund>/q<N>_<year>.yaml
```

### New capability: "Who else is buying?" scanner

```
Download all 13F-HR filings for a quarter
     |
     v
Filter for positions in thesis tickers (COHR, LITE, CIEN, CRWV, MU, etc.)
     |
     v
Output: "These 47 funds added COHR this quarter"
(institutional momentum signal)
```

## Implementation Plan

1. EDGAR fetcher using edgartools for tracked funds (Leopold CIK 0002045724, Baker CIK 0001777813)
2. Shkreli-style options stripping — separate equity value from notional option value
3. Auto-diff against prior quarter YAML (change_vs_prior field)
4. Bulk scanner for thesis tickers across all 13F filers
5. Integrate into the sidecar ingest path under `agents/src/` — for example `fund_13f.py` with a `fetch_from_edgar()` method

## Shkreli's Models Repo (Separate Reference)

His `models` repo (1,686 stars) contains 500+ hand-built Excel financial models.
Each ticker gets a spreadsheet with quarterly P&L, balance sheet, cash flow,
and forward estimates. CRWV.xlsx model analyzed separately — see CRWV analysis notes.

This is a different paradigm: fundamental valuation vs. our thematic/bottleneck approach.
Both answer different questions:
- Shkreli: "What is the stock worth?"
- Our system: "Where does it sit in the AI supply chain and who's positioned?"

## Company Deep Dive Template

For `canonical/20-data/companies/<TICKER>.yaml`. Designed to be lean and maintainable.

```yaml
ticker: COHR
company: Coherent Corp
sector: optical_interconnect
bottleneck: optical
updated: "2026-04-03"

# 1. What do they actually make?
business:
  summary: "" # 2-3 sentences max
  segments: []  # revenue breakdown by segment
  key_products: []  # the specific things that matter for the thesis
  customers: []  # which hyperscalers / OEMs

# 2. Why does the thesis care?
thesis_relevance:
  bottleneck_role: "" # what specific part of CPO/optical do they supply?
  moat: "" # why them and not someone else?
  risks: [] # what could make this wrong?

# 3. Who's positioned and how?
positioning:
  leopold: { value: null, type: null, trend: "" }
  baker: { value: null, type: null, trend: "" }
  semianalysis_signal: "" # any direct mention

# 4. Financials — just enough to sanity-check valuation
financials:
  market_cap: null
  revenue_ttm: null
  revenue_growth_yoy: null
  gross_margin: null
  pe_ratio: null
  ev_ebitda: null

# 5. Catalysts & timeline
catalysts:
  near_term: []  # next 1-2 quarters
  medium_term: []  # 2026-2027
  long_term: []  # 2028+

# 6. Open questions — things we don't know yet
open_questions: []
```

Design rationale:
- **Business** — what they make, plain english, segment revenue so you know what drives the number
- **Thesis relevance** — maps back to canonical/30-thesis/thesis.yaml. Why THIS company for this bottleneck? Moat vs competitors?
- **Positioning** — pulls from Leopold/Baker data into one place per company
- **Financials** — minimal. Just enough to know if market has priced in the thesis
- **Catalysts** — what events move conviction up or down
- **Open questions** — most important section for ongoing research

Could optionally add a Shkreli-style financial model section (quarterly P&L, balance sheet,
cash flow) but that's heavier to maintain. Start lean, add if needed.

### Suggested first deep dive: COHR (Coherent Corp)

COHR is the ONLY full agreement zone across all 3 sources (Leopold, Baker, SemiAnalysis).
Both funds are long. SemiAnalysis calls CPO required for next-gen multi-rack AI.
Starting here gives highest signal-to-noise for validating the template.

### Shkreli's CRWV Model — Key Takeaways

Summary of his Excel model (CRWV.xlsx from martinshkreli/models):

**Snapshot (as of Q3 2025):**
- Price: $77, Shares: 498M, MC: $38.3B, Debt: $14.0B, EV: $49.4B
- Revenue backlog: $55.6B (contracted)
- PP&E: $20.7B (GPU assets, growing ~$2.4B/quarter in capex)

**Revenue trajectory:**
- FY2024: $1.9B → FY2025: $5.1B → FY2026E: $11.6B → FY2027E: $17.3B → FY2028E: $22.5B

**The critical assumption — gross margins:**
- Actual Q3 2025: ~18% (ex-D&A) / ~64% (with D&A added back)
- His 2026-2027 estimate: 64% gross margin
- His 2028 estimate: reverts to 24% (GPU depreciation + competition)
- At 64% margins → stock trades at 7x 2026 earnings (cheap)
- At 30% margins → roughly breakeven (fairly valued / overvalued given debt)
- At 20% margins → can't service $14B debt (existential bear case)

**Debt structure:**
- $14B total: term loans ($7.5B) + high-yield bonds ($3.75B at 9-9.25%) + other
- Bonds trading at $0.93-$0.95 (some credit risk priced in, not distressed)
- He assumes debt fully paid off by 2028 from cash flows

**Cash flow reality:**
- Q3 2025 CFFO: +$1.7B (first meaningful positive quarter)
- CapEx: -$2.4B/quarter (the treadmill — must keep buying next-gen GPUs)
- Net: still cash flow negative on a free cash flow basis

**His model's core message:**
"The trade is entirely about margins. Revenue is de-risked by $55.6B backlog.
If 64% gross margins materialize, stock is absurdly cheap at 7x earnings.
If margins stay at 30%, it's fairly valued. If supply catches up and margins
compress to 20%, the debt load becomes existential."
