---
status: draft
feature: signal-desk-schema
---

# Justin Compute Map -> Signal Desk Mapping

## Justin's Tracked Dimensions

### Source data model

Justin's data repo has two core entities:

| Entity | Fields | Meaning |
|---|---|---|
| Company node | `slug`, `name`, `ticker`, `category`, `subline`, `acquired` | Stable company/entity node |
| Deal edge | `id`, `source_slug/name`, `target_slug/name`, `deal_type`, `value_billions`, `value_display`, `date`, `date_display`, `description`, `source_url` | Directed transaction edge; direction is money/chips/equity flow |

Current observed shape from the repo clone:

- 81 companies
- 257 deals
- 13 company categories
- 8 deal types

### UI dimensions

| UI surface | State/dimensions | What it does |
|---|---|---|
| Search | free text over company names, deal type, description | Global narrowing |
| Trace | origin company, destination company, path index, hop count, path shape | Finds value-chain paths between companies |
| Timeline | `from` year, `to` year | Highlights nodes/edges active in date range |
| Cluster | multi-selected company categories | Highlights companies in selected categories |
| Graph | company nodes, aggregated source-target edges, category centroids | Visual relationship map |
| Table | deal type, category, sort, date, value, source | Evidence/detail list |
| Profile panel | selected company or selected edge | Context + counterparty/deal detail |

Important implementation detail: Trace is not just generic graph traversal. It uses a value-chain rank so paths move downstream: equipment/foundry/memory/packaging -> chip designer -> server/power/networking -> operator -> AI lab.

## Semi-Stocks Current Dimensions

| Entity | Current source | Key fields |
|---|---|---|
| Company | `canonical/site-data/companies.json` | `ticker`, `name`, `bottleneck`, `status`, `also`, `next_earnings`, `positions`, `metrics`, `thesis`, counts |
| Category / thesis stage | `canonical/site-data/thesis.json` | `name`, `status`, `period`, `cycle_phase`, `tickers`, `signals` |
| Signal | `canonical/site-data/signals.json` | `kind`, `ticker/company_id/stage_id/proposal_id`, `bottleneck`, `direction`, `evidence`, source trace |
| Claim / proof gate | `canonical/site-data/claims.json` | `ticker`, `claim`, `status`, `verify_at`, `verify_window`, source trace |
| Position | inside company records | `source`, `value`, `pct_portfolio`, `type`, `change_vs_prior`, `notes` |
| Page/source | `canonical/site-data/pages.json` | `slug`, `title`, `type`, `summary`, `body_markdown`, links |
| Relationship edge | `canonical/site-data/edges.json` | `type`, `source`, `target`, optional ticker/source metadata |

## Mapping

| Justin dimension | Semi-stocks equivalent | Recommendation |
|---|---|---|
| Company node | Company/ticker record | Keep as primary node type |
| Company category | Bottleneck/category/thesis stage | Normalize into `category_id`; expose as first-class cluster |
| Deal edge | Signal/claim/position/source relationship | Do not copy deal semantics; define typed evidence edges |
| Deal type | Signal kind / claim type / relationship type | Use as edge/filter facet |
| Date/timeline | source date, signal date, earnings date, claim `verify_at`, 13F filing date | Add timeline facet across evidence and events |
| Value | position value, revenue metric, exposure, claim value where parseable | Keep optional; do not force all rows into dollar-value schema |
| Source URL | source page/path/ref | Keep source trace mandatory for every signal/claim |
| Trace origin/destination | company/category/source path through value chain | Add later after category ranks are stable |
| Cluster | category multi-select | Make primary surface |
| Signal source cluster | not present in Justin; user-requested | Source/channel lens: Leopold, Baker, SemiAnalysis, earnings, thesis, proposals |

## Proposed Signal Desk Surfaces

### 1. Top controls

Use Justin's visual rhythm exactly:

- Search
- Trace
- Timeline
- Thesis Cluster
- Company Category
- Signal Cluster

Start with Search, Timeline, Thesis Cluster, Company Category, and Signal Cluster. Add Trace once value-chain ranks/edges are stable enough to avoid misleading paths.

### Top-control meanings

| Control | Meaning | Initial data source |
|---|---|---|
| Search | Global text narrowing | company, signal, claim, source text |
| Trace | Company-to-company path through the evidence/value chain | graph projection, later |
| Timeline | Event/evidence date range | signal date, source date, earnings date, claim `verify_at` |
| Thesis Cluster | Ash thesis buckets and canonical bottleneck stages | `thesis.cascade`, notebook buckets |
| Company Category | Company role / value-chain category | normalized company category |
| Signal Cluster | Source/channel group over signals and positions | fund source YAML, SemiAnalysis YAML, company packets, thesis/proposals |

The important separation:

- **Thesis Cluster** answers "which part of my thesis map?"
- **Company Category** answers "what economic role is this company playing?"
- **Signal Cluster** answers "which signal source/channel is selected?"

### 2. Graph

Start with company nodes. Use category cluster centroids for placement.

Possible visible edge types:

- `shares_category`
- `has_signal`
- `has_claim`
- `positioned_by`
- `derived_from_same_source`
- `supplier_customer` only if imported from external deal data or explicitly encoded

Do not render every existing `edges.json` edge. Build a graph-specific projection so the visual remains legible.

### 3. Bottom detail table

Instead of Justin's transaction table, use a switchable evidence table:

- Signals
- Claims / proof gates
- Positions
- Sources

Rows should always carry source trace.

### 4. Profile panel

Selected company panel should show:

- identity: ticker, name, category/status
- thesis summary
- positions/exposure
- active signals
- open claims/proof gates
- related categories and signal clusters
- source links

## Cluster Model

### Manual clusters

These are human/canonical categories:

- current thesis stages from `30-thesis.cascade`
- notebook-level buckets: Energy, Chips, Infrastructure, Models, Applications
- bottleneck slugs: `memory`, `n3_logic`, `pluggable_optics`, `cpo_next`, `euv`, `power`, `gpu_cloud`, etc.

### Company category clusters

These are value-chain roles, closer to Justin's `company.category` field:

- `equipment`
- `foundry`
- `memory`
- `packaging`
- `chip_designer`
- `server_oem`
- `networking`
- `power`
- `data_center`
- `gpu_cloud`
- `hyperscaler`
- `ai_lab`
- `investor`

Semi-stocks can start smaller and add roles only when source data supports them:

- `equipment`
- `foundry`
- `memory`
- `chip_designer`
- `networking`
- `optics`
- `power`
- `gpu_cloud`
- `hyperscaler_ai_lab`
- `investor`

### Signal source clusters

These are source/channel groups:

- Leopold
- Baker
- SemiAnalysis
- Company earnings
- Thesis stage
- Pending proposals
- Future agent signals

Selecting one source cluster should highlight companies it touches and show the
aggregated context below. Deselecting it removes that source's contribution
without removing companies that are still relevant to another selected source
cluster.

### Future topic subclusters

These are generated from signal evidence inside or across source clusters:

- text/topic similarity
- shared source
- shared ticker set
- shared claim/verify window
- shared direction: `confirms`, `contradicts`, `supports`, `proposed`

Recommended starting output:

```yaml
signal_clusters:
  - id: signal-cluster:baker
    label: Baker
    cluster_type: source_channel
    source_kind: fund_positioning
    signal_ids: [...]
    position_ids: [...]
    company_ids: [...]
    category_ids: [...]
    summary: "Baker/Atreides positioning and thesis read-through."
```

Keep `cluster_type` explicit so source/channel clusters are not confused with
future generated topic clusters.

## Minimum Schema Change

Add one generated UI payload later:

```yaml
signal_desk:
  controls:
    search: true
    timeline: true
    thesis_cluster: true
    company_category: true
    signal_cluster: true
    trace: false
  categories: [...]
  company_categories: [...]
  signal_clusters: [...]
  companies: [...]
  graph:
    nodes: [...]
    edges: [...]
  tables:
    signals: [...]
    claims: [...]
    positions: [...]
```

The key design move is to separate:

- canonical category clusters: stable human thesis buckets
- company category clusters: value-chain role / graph layout buckets
- auto signal clusters: generated topical groupings
- company clustering: graph layout and selected-company neighborhood
