---
status: locked-after-challenge
feature: signal-desk-schema
updated: 2026-04-19
---

# Readiness Challenge: Signal Desk

## Visual

![Signal Desk readiness shifts](../../diagrams/signal-desk-readiness-shifts.png)

## Lock

The Justin-style surface is still the right look and interaction target, but the current repo is **not ready for UI-first implementation**.

The repo is ready for a **data-contract-first implementation**:

1. generate `canonical/site-data/signal_desk.json`
2. validate source/channel joins, positions, categories, timelines, and graph endpoints
3. scaffold the Justin-style reader only after that payload passes
4. keep Trace disabled until graph edges are value-chain-safe

## Merged History Findings

Sidecar history scan confirmed the prior decision trail:

- `Signal Cluster` was corrected on 2026-04-19 from topic clustering to source/channel clustering.
- The locked source/channel clusters are `Leopold`, `Baker`, `SemiAnalysis`, company earnings, thesis stage, pending proposals, and later agent signals.
- Topic clusters such as Rubin capacity, HBM pricing, and optics backlog are subordinate future features.
- `canonical/site-data/` is the intended reader boundary.
- `canonical/site-data/signal_desk.json` does not exist yet.
- Trace belongs in the UI contract but should stay disabled until value-chain ranks and edges are trustworthy.

## Evidence Snapshot

Current generated data:

| Artifact | Current state | Readiness |
|---|---:|---|
| `canonical/site-data/build.json` | generated 2026-04-19, `site-data-v0.1` | usable boundary |
| `companies.json` | 40 companies | usable, but category roles need normalization |
| `signals.json` | 67 signals | usable, but source/date shapes differ |
| `claims.json` | 43 claims | usable, but no `source_path` and no normalized timeline date |
| `edges.json` | 678 broad evidence/wiki/report edges | not safe as graph surface |
| `graph.json` | 127 nodes, 398 links | too broad for Justin-style company map |
| `signal_desk.json` | absent | blocker |

Current wiki structure:

| Wiki surface | Current state | Readiness |
|---|---:|---|
| pages emitted to `pages.json` | 34 | good source/profile substrate |
| source pages | 12 | enough for initial source-channel labels |
| concept pages | 8 | enough for thesis context |
| output pages | 3 | useful but not first-slice table rows |
| `_lint.json` dead links | 0 | healthy |
| `_lint.json` orphan pages | 0 | healthy |

Current source-channel evidence:

| Channel | Current source | Current count | Challenge |
|---|---|---:|---|
| Leopold | `canonical/20-data/sources/leopold/q4_2025.yaml` | 25 source positions | positions are embedded/flattened in `companies.json` |
| Baker | `canonical/20-data/sources/baker/q4_2025.yaml` | 20 source positions, 16 generated company position rows | multi-leg positions are collapsed in `companies.json` |
| SemiAnalysis | `canonical/20-data/sources/semianalysis/signals.yaml` | 6 generated signal rows | good source cluster seed |
| Company earnings | `canonical/20-data/companies/**` | 25 signal rows, 43 claim rows | claims lack `source_path`; timeline is textual |
| Thesis stage | `canonical/30-thesis/thesis.yaml` | 33 signal rows | source is one control file, not an authored source page |
| Pending proposals | `canonical/20-data/thesis-proposals/**` | 3 signal rows | good pending channel seed |

## Readiness Gate

| Surface | Verdict | Reason | Lock |
|---|---|---|---|
| Justin visual style | Ready | CSS, toolbar, graph, table, and profile patterns are source-pinned | copy/adapt after data gate |
| Search | Mostly ready | text exists across pages, companies, signals, claims | add `search_text` to row projections |
| Timeline | Partial | only 9 of 67 signals have exact `date`; claims have text `verify_at` only | normalize `timeline.date`, `precision`, `label`, `kind` |
| Thesis Cluster | Ready enough | 7 thesis stages exist with IDs, tickers, signals | generate cluster rows and joins |
| Company Category | Partial | current values are thesis bottlenecks, not value-chain roles | add explicit mapping table and ranks |
| Signal Cluster | Partial | source channels exist, but rows are scattered | build clusters from signals, claims, and first-class positions |
| Evidence table | Partial | signals/claims exist; positions are not first-class | create table projections |
| Profile panel | Partial | data exists but is scattered | compose in `signal_desk.json` |
| Graph | Partial | company nodes exist; current graph is broad knowledge graph | build graph-specific company projection |
| Trace | Not ready | current edges are provenance/evidence, not directed value-chain deals | keep disabled |

## Spec Challenges

### 1. `signals.json` cannot be the source-cluster substrate

`signals.json` has 67 rows, but Baker and Leopold do not appear as signal rows. They live as fund positions. Therefore `Signal Cluster` must join across `positions`, `signals`, and `claims`, not just filter signals.

Lock: generate first-class `positions` rows in `signal_desk.json`.

### 2. Current position projection loses row fidelity

Generated company positions only expose:

```text
source, value, pct_portfolio, type, change_vs_prior, notes
```

That loses `period`, `filed`, `source_path`, ticker-level row IDs, shares, and multi-leg detail. Baker has 20 source positions but only 16 generated company position rows because multi-leg tickers collapse.

Lock: build positions directly from `canonical/20-data/sources/<fund>/q4_2025.yaml`, not from flattened company records.

### 3. Source metadata is not normalized

Signals all have `source_path`, but only 25 have `source_page` and only 9 have `source`. Claims have `source` and `source_page`, but no `source_path`.

Lock: every visible row gets:

```yaml
source_cluster_id
source_kind
source_label
source_paths
source_refs
```

### 4. Timeline cannot be a raw date filter yet

Signals mix exact dates, fiscal quarters, stage rows, and proposal dates. Claims use human labels such as `Q3 FY2026 earnings` and `FY2026-FY2027 quarterly results`.

Lock: every row gets a `timeline` object with nullable `date`, explicit `precision`, and display-safe `label`.

### 5. Current graph is not the reader graph

`graph.json` contains page, source, bottleneck, report, thesis, and company nodes. Justin's surface is a company-node graph over directed relationships.

Lock: `signal_desk.json.graph` is a new projection with company nodes only for the first slice and edges built from co-position, shared source signal, thesis co-cluster, or explicit read-through evidence.

### 6. Company categories need a role mapping, not raw bottlenecks

Current company records mostly carry thesis bottlenecks such as `n3_logic`, `pluggable_optics`, and `power`. Justin categories are economic roles such as `foundry`, `memory`, `chip_designer`, `networking`, `power`, and `neocloud`.

Lock: implement an explicit role mapping with fallback from thesis bottleneck only when documented.

### 7. Wiki is ready as source/profile substrate, not as UI runtime input

The wiki is healthy enough to provide page summaries, body text, source labels, and profile context. It should not be parsed by the UI.

Lock: UI consumes `signal_desk.json`; generator may read wiki/pages.

## Final Data Contract Lock

`canonical/site-data/signal_desk.json` must include:

```yaml
version: signal-desk-v0.1
source_build: {...}
summary_counts: {...}
controls: {...}
thesis_clusters: [...]
company_categories: [...]
signal_clusters: [...]
companies: [...]
positions: [...]
signals: [...]
claims: [...]
timeline_events: [...]
graph:
  nodes: [...]
  edges: [...]
tables:
  default: signals
  signals: [...]
  claims: [...]
  positions: [...]
  sources: [...]
facets: {...}
```

Validation must prove:

- every referenced company, signal, claim, position, cluster, and graph endpoint exists
- every visible row has source trace
- every visible row has `search_text`
- every row has a display-safe `timeline`
- Trace remains disabled unless graph edges pass value-chain-rank rules

## Implementation Gate

Proceed to Phase 1 only:

```bash
uv run python canonical/40-engine/site_data.py --validate
python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null
```

Do not start `canonical/site-reader/` until the Signal Desk payload exists and validates.
