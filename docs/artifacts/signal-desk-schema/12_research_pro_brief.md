---
status: research-pro-handoff
feature: signal-desk-schema
updated: 2026-04-19
---

# Signal Desk Research Pro Brief

## How To Use This Document

This is a single self-contained handoff for ChatGPT Research Pro. It combines:

- project context
- current repo state
- Justin Wang reference-site state
- current Signal Desk spec
- readiness challenge
- implementation gates
- source paths and source facts
- questions Research Pro should answer before implementation

Primary request for Research Pro:

> Challenge this plan before implementation. Verify whether the semi-stocks repo data and wiki structure are ready to support a Justin-style Signal Desk surface. Identify schema mistakes, graph/Trace risks, source/provenance gaps, UI/data mismatches, and a better implementation sequence if needed.

The desired output from Research Pro is not generic encouragement. It should return concrete changes to the schema/spec, risks, missing fields, implementation order, and tests.

## External Links To Open First

Research Pro should inspect these public URLs directly. The pinned commits are the versions used for this planning pass.

### Justin Wang live surface

```text
Live site:
https://compute.jstwng.com/
```

### Justin UI repo

```text
Repo:
https://github.com/jstwng/compute-site

Pinned tree:
https://github.com/jstwng/compute-site/tree/1f90a873c44ceea03240ccb5658e115dbc40e6c6

Commit:
https://github.com/jstwng/compute-site/commit/1f90a873c44ceea03240ccb5658e115dbc40e6c6

License metadata:
MIT in package.json
```

Key files to inspect in the pinned UI repo:

```text
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/App.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/styles.css
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/app.css
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/Toolbar.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/Dropdown.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/MobileFilterSheet.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/Graph.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/DealTable.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/FilterBar.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/ProfilePanel.jsx
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/logic.js
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/src/components/ComputeDealMap/styles.module.css
https://github.com/jstwng/compute-site/blob/1f90a873c44ceea03240ccb5658e115dbc40e6c6/scripts/vite-plugin-deal-data.mjs
```

### Justin data repo

```text
Repo:
https://github.com/jstwng/compute-deal-map-data

Pinned tree:
https://github.com/jstwng/compute-deal-map-data/tree/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d

Commit:
https://github.com/jstwng/compute-deal-map-data/commit/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d

Release inspected during planning:
2026.04.17-1

Latest release page:
https://github.com/jstwng/compute-deal-map-data/releases/latest

Data license:
CC BY 4.0 for data; MIT for scripts/schemas per README/LICENSE notes.
```

Key files to inspect in the pinned data repo:

```text
https://github.com/jstwng/compute-deal-map-data/blob/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/README.md
https://github.com/jstwng/compute-deal-map-data/blob/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/companies.yml
https://github.com/jstwng/compute-deal-map-data/tree/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/deals
https://github.com/jstwng/compute-deal-map-data/blob/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/schema/company.schema.json
https://github.com/jstwng/compute-deal-map-data/blob/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/schema/deal.schema.json
https://github.com/jstwng/compute-deal-map-data/blob/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/scripts/build.js
https://github.com/jstwng/compute-deal-map-data/blob/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d/scripts/validate.js
```

Latest release artifact URLs, useful for comparing current public output shape:

```text
https://github.com/jstwng/compute-deal-map-data/releases/latest/download/companies.json
https://github.com/jstwng/compute-deal-map-data/releases/latest/download/deals.json
https://github.com/jstwng/compute-deal-map-data/releases/latest/download/schema.json
```

Important: this Signal Desk plan should copy Justin's visual and interaction lessons, not Justin's data semantics. Justin's source edge is a directed deal edge; semi-stocks source edges are evidence/provenance unless explicitly projected.

## Executive Summary

Ash wants a Signal Desk reader for `semi-stocks-2`.

The target look and interaction model should be close to Justin Wang's compute map:

- dense graph-first surface
- Inter font
- 12px base density
- dark-mode-first feel
- rectangular company nodes
- thin muted borders and edges
- compact toolbar
- graph block
- dense table below
- profile panel / bottom sheet

But the data must come from `semi-stocks-2`, not Justin's deal dataset.

Current locked decision:

- Do **not** build UI first.
- Build and validate `canonical/site-data/signal_desk.json` first.
- Only then scaffold `canonical/site-reader/`.
- Keep Trace disabled until graph edges are value-chain-safe.

Reason:

Justin has a clean directed deal graph. Semi-stocks currently has a canonical evidence system: wiki pages, fund positions, company packets, source signals, claims, thesis stages, proposals, and broad provenance edges. That can support a similar reader, but only after a generated view model normalizes source clusters, positions, timelines, categories, graph projection, and table rows.

## Current Repo Purpose

Repo path:

```text
/Users/ash/Documents/2026/semi-stocks-2
```

`semi-stocks-2` is a canonical propagation repo for semiconductor / AI infrastructure investment research.

Canonical flow:

```text
canonical/10-wiki/raw
  -> canonical/10-wiki/sources | concepts | outputs
  -> canonical/20-data/sources | companies | thesis-proposals
  -> canonical/30-thesis/thesis.yaml
  -> canonical/40-engine
  -> canonical/50-reports
```

Generated integration surfaces:

```text
canonical/wiki-site/   # old/generated Wikiwise export bundle
canonical/site-data/   # newer generated reader contract
```

Important boundary:

- `canonical/wiki-site/` is not a canonical stage.
- `canonical/site-data/` is generated app data, not source authority.
- UI must not parse canonical markdown/YAML directly.
- UI should consume generated `canonical/site-data/signal_desk.json` for the first Signal Desk slice.

Runtime:

```bash
uv run python canonical/40-engine/site_data.py --validate
```

## Current Repo State

`canonical/site-data/build.json` current state:

```yaml
generated_at: 2026-04-19T09:28:33Z
generator: site-data-v0.1
source_counts:
  data_yaml: 13
  reports: 2
  wiki_markdown: 36
artifact_counts:
  claims: 43
  companies: 40
  edges: 678
  entities: 93
  pages: 34
  reports: 1
  signals: 67
  thesis_stages: 7
warnings: []
```

Current `canonical/site-data/` artifacts:

```text
build.json
schema.json
pages.json
companies.json
signals.json
claims.json
entities.json
edges.json
thesis.json
reports.json
search.json
graph.json
```

Important absence:

```text
canonical/site-data/signal_desk.json  # does not exist yet
```

Current `pages.json`:

```yaml
pages: 34
types:
  concept: 8
  meta: 3
  output: 3
  raw: 8
  source: 12
with_created: 23
with_sources: 23
```

Current `signals.json`:

```yaml
total: 67
kinds:
  company_thesis_signal: 25
  semianalysis_signal: 6
  thesis_proposal_signal: 3
  thesis_stage_signal: 33
with_date: 9
with_source: 9
with_source_page: 25
with_source_path: 67
```

Current `claims.json`:

```yaml
total: 43
with_source_path: 0
with_source_page: 43
with_parseable_verify_date: 0
```

Current `companies.json`:

```yaml
companies: 40
with_positions: 37
generated_position_rows:
  baker: 16
  leopold: 25
with_bottleneck: 18
```

Important position-source gap:

```yaml
canonical/20-data/sources/baker/q4_2025.yaml:
  positions: 20
  period: 2025-12-31
  filed: 2026-02-17
  aum: 8183000000

canonical/20-data/sources/leopold/q4_2025.yaml:
  positions: 25
  period: 2025-12-31
  filed: 2026-02-11
  aum: 5517000000
```

Baker has 20 source positions but only 16 generated company position rows because multi-leg positions are collapsed in `companies.json`. Signal Desk needs first-class position rows built directly from fund YAML.

Current `graph.json`:

```yaml
nodes: 127
links: 398
node_types:
  bottleneck: 17
  company: 40
  concept: 8
  output: 3
  page:concept: 8
  page:meta: 3
  page:output: 3
  page:raw: 8
  page:source: 12
  report: 1
  source: 16
  thesis: 1
  thesis_stage: 7
link_types:
  belongs_to_bottleneck: 7
  derived_from_source: 7
  exposes_company_to: 18
  links_to: 172
  mentions_ticker: 153
  published_in_report: 41
```

This graph is a broad knowledge/provenance graph. It is not ready to serve as a Justin-style company relationship graph or Trace graph.

## Current Wiki State

Wiki path:

```text
canonical/10-wiki/
```

Wiki schema:

```text
canonical/10-wiki/schema.md
```

Wiki structure:

```text
canonical/10-wiki/index.md
canonical/10-wiki/_index.json
canonical/10-wiki/_backlinks.json
canonical/10-wiki/_lint.json
canonical/10-wiki/log.md
canonical/10-wiki/schema.md
canonical/10-wiki/raw/
canonical/10-wiki/concepts/
canonical/10-wiki/sources/
canonical/10-wiki/outputs/
```

Current wiki lint:

```yaml
dead_links: 0
orphan_pages: 0
```

Important source pages:

```text
canonical/10-wiki/sources/leopold-q4-2025.md
canonical/10-wiki/sources/baker-q4-2025.md
canonical/10-wiki/sources/semianalysis-signals.md
canonical/10-wiki/sources/nvda-q4-fy2026.md
canonical/10-wiki/sources/tsm-q4-2025.md
canonical/10-wiki/sources/mu-q2-fy2026.md
canonical/10-wiki/sources/cohr-q2-fy2026.md
canonical/10-wiki/sources/lite-q2-fy2026.md
canonical/10-wiki/sources/crwv-q4-2025.md
canonical/10-wiki/sources/intc-q4-2025.md
canonical/10-wiki/sources/jstwng-nvidia-margin-illusion.md
canonical/10-wiki/sources/dwarkesh-dylan-ai-infrastructure-bottlenecks.md
canonical/10-wiki/sources/creative-strategies-neoclouds-three-business-models.md
```

Important concept pages:

```text
canonical/10-wiki/concepts/bottleneck-cascade.md
canonical/10-wiki/concepts/memory-supercycle.md
canonical/10-wiki/concepts/n3-wafer-crunch.md
canonical/10-wiki/concepts/pluggable-optics.md
canonical/10-wiki/concepts/co-packaged-optics.md
canonical/10-wiki/concepts/euv-tool-bottleneck.md
canonical/10-wiki/concepts/nvda-margin-residual.md
canonical/10-wiki/concepts/token-economics.md
canonical/10-wiki/concepts/neocloud-business-models.md
```

Conclusion:

The wiki is ready as source/profile substrate. It is not the UI runtime. Generator may read wiki and page metadata; reader should not.

## Current Canonical Data Sources

Fund positioning:

```text
canonical/20-data/sources/leopold/q4_2025.yaml
canonical/20-data/sources/baker/q4_2025.yaml
```

SemiAnalysis source signals:

```text
canonical/20-data/sources/semianalysis/signals.yaml
```

Company packets:

```text
canonical/20-data/companies/COHR/q2_fy2026.yaml
canonical/20-data/companies/CRWV/q4_2025.yaml
canonical/20-data/companies/INTC/q4_2025.yaml
canonical/20-data/companies/LITE/q2_fy2026.yaml
canonical/20-data/companies/MU/q2_fy2026.yaml
canonical/20-data/companies/NVDA/q4_fy2026.yaml
canonical/20-data/companies/TSM/q4_2025.yaml
canonical/20-data/companies/CIFR/q1_2026_neocloud.yaml
canonical/20-data/companies/CORZ/q1_2026_neocloud.yaml
canonical/20-data/companies/GLXY/q1_2026_neocloud.yaml
canonical/20-data/companies/IREN/q1_2026_neocloud.yaml
canonical/20-data/companies/NBIS/q1_2026_neocloud.yaml
canonical/20-data/companies/WULF/q1_2026_neocloud.yaml
```

Thesis control:

```text
canonical/30-thesis/thesis.yaml
```

Thesis proposals:

```text
canonical/20-data/thesis-proposals/hbm-contracting-structure-shift.yaml
canonical/20-data/thesis-proposals/nvda-margin-compression.yaml
canonical/20-data/thesis-proposals/neocloud-business-model-reclassification.yaml
canonical/20-data/thesis-proposals/tsm-pricing-power-reclassification.yaml
```

## Project Goal

Build a Signal Desk reader that helps Ash inspect semi-stocks evidence like a dense map, not like a generic dashboard.

The desk should answer:

- Which thesis cluster is active?
- Which economic role does each company play?
- Which source/channel is contributing evidence?
- Which companies are touched by Leopold, Baker, SemiAnalysis, company earnings, thesis stage signals, or pending proposals?
- What evidence row explains why a node or edge is highlighted?
- What claims/proof gates need to be verified later?
- Which relationships are real enough to show in graph form?

The desk should not pretend that semi-stocks data is a directed transaction graph when it is actually an evidence and provenance system.

## Justin Wang Reference State

Reference live site:

```text
https://compute.jstwng.com/
```

Reference UI repo:

```text
https://github.com/jstwng/compute-site
pinned tree: https://github.com/jstwng/compute-site/tree/1f90a873c44ceea03240ccb5658e115dbc40e6c6
inspected commit: 1f90a873c44ceea03240ccb5658e115dbc40e6c6
local scratch clone: /tmp/compute-site-signal-desk
license metadata: MIT in package.json
source file count under src: 24
```

Reference data repo:

```text
https://github.com/jstwng/compute-deal-map-data
pinned tree: https://github.com/jstwng/compute-deal-map-data/tree/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d
inspected commit: e5c0e740b2f34ee56b6073e2e237b2dddc0c564d
local scratch clone: /tmp/compute-deal-map-data-signal-desk
data license: CC BY 4.0
scripts/schemas license: MIT
latest release inspected in planning: 2026.04.17-1
```

Justin data shape:

```yaml
companies: 81
deals: 257
company_categories:
  - ai_lab
  - chip_designer
  - data_center
  - equipment
  - foundry
  - hyperscaler
  - investor
  - memory
  - neocloud
  - networking
  - packaging
  - power
  - server_oem
deal_types:
  - cloud_capacity
  - custom_asic
  - equipment_supply
  - equity_investment
  - funding_round
  - gpu_purchase
  - m_and_a
  - power_ppa
all_deals_have_dates: true
all_deals_have_source_urls: true
```

Justin data model:

```yaml
company:
  required:
    - slug
    - name
    - category
  optional:
    - ticker
    - subline
    - acquired

deal:
  required:
    - id
    - source_slug
    - source_name
    - target_slug
    - target_name
    - deal_type
    - date
    - date_display
    - description
    - source_url
  optional:
    - value_billions
    - value_display
```

Justin UI files worth studying:

```text
/tmp/compute-site-signal-desk/src/App.jsx
/tmp/compute-site-signal-desk/src/styles.css
/tmp/compute-site-signal-desk/src/app.css
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/Toolbar.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/Dropdown.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/MobileFilterSheet.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/Graph.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/DealTable.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/ProfilePanel.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/FilterBar.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/logic.js
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/styles.module.css
```

Justin mechanics to copy/adapt:

- Inter font
- 12px base density
- light/dark CSS variable palette
- rectangular nodes
- muted graph styling
- top toolbar
- one open dropdown panel at a time
- active filters independent/composable
- mobile filter bottom sheets
- d3 graph simulation
- node width measurement
- overlap removal
- ResizeObserver handling
- hover/focus dimming
- edge clipping
- profile panel
- dense table

Justin Trace logic:

- `logic.js` defines category layout and Trace ranking.
- Trace pathfinding uses strict value-chain ranks.
- It rejects paths that move upstream.
- It caps tier jumps with `MAX_TIER_JUMP = 2`.
- It caps path search.
- It groups paths by category shape.

Important difference:

Justin's Trace is trustworthy because deal edges are directed source-to-target relationships with source/target categories. Semi-stocks does not yet have equivalent value-chain-safe edges.

## Current Signal Desk Decisions

Locked decisions from existing artifact set:

1. Signal Desk is a generated reader surface over canonical data, not a new canonical stage.
2. UI reads `canonical/site-data/signal_desk.json` only.
3. `Signal Cluster` means source/channel clustering, not topic clustering.
4. Topic clusters are future subordinate features.
5. Baker and Leopold require positions as first-class UI rows.
6. Trace remains visible only as a disabled/off control until graph projection is safe.
7. Reviews are not a first-class entity.
8. Canonical claims/proof gates are not the same as agent predictions.
9. Agent predictions remain sidecar until explicitly imported.

Current corrected meaning of `Signal Cluster`:

```text
Leopold
Baker
SemiAnalysis
Company earnings
Thesis stage
Pending proposals
Future agent signals
```

Future topic subclusters:

```text
Rubin capacity
HBM pricing
optics backlog
CPO roadmap
power deliverability
```

Do not ship topic clusters in first slice.

## Proposed Signal Desk Surface

Desktop toolbar:

```text
Trace | Timeline | Thesis Cluster | Company Category | Signal Cluster | Search
```

Mobile toolbar:

```text
row 1: Search
row 2: compact chips for Trace, Timeline, Thesis Cluster, Company Category, Signal Cluster
```

Graph:

- company nodes only in first slice
- rectangular nodes
- muted edges
- company category centroids
- selected/focused neighborhood dimming
- edge click opens evidence context
- empty graph click resets focus

Table:

```text
Signals
Claims / proof gates
Positions
Sources
```

Profile panel:

- company identity
- company category
- thesis clusters
- selected signal-cluster context
- positions by source
- signals by source
- claims/proof gates
- source links

## Control Semantics

Filter state:

```yaml
controls:
  search: ""
  trace:
    enabled: false
    origin_company_id: null
    destination_company_id: null
    path_index: 0
    hop_count: null
  timeline:
    from: null
    to: null
    mode: evidence_date
  thesis_cluster:
    selected_ids: []
  company_category:
    selected_ids: []
  signal_cluster:
    selected_ids: []
```

Filter composition:

- Within one control, multi-select uses union semantics.
- Across controls, filters compose by intersection.
- No selected value means "all" for that control.

Example:

```text
Signal Cluster = Baker + Leopold
Company Category = optics
Result = companies/rows touched by Baker OR Leopold AND classified as optics
```

## Required `signal_desk.json`

Create:

```text
canonical/site-data/signal_desk.json
```

Top-level shape:

```yaml
version: signal-desk-v0.1
source_build:
  generator: site-data-v0.1
  source_hash: ...
  generated_at: ...
summary_counts:
  companies: ...
  thesis_clusters: ...
  company_categories: ...
  signal_clusters: ...
  signals: ...
  claims: ...
  positions: ...
controls:
  search: true
  timeline: true
  thesis_cluster: true
  company_category: true
  signal_cluster: true
  trace:
    enabled: false
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
facets:
  directions: [...]
  statuses: [...]
  source_kinds: [...]
  table_kinds: [...]
```

## Required Normalized Fields

Every visible evidence row must carry:

```yaml
source_cluster_id: ...
source_kind: ...
source_label: ...
source_paths: [...]
source_refs: [...]
search_text: ...
timeline:
  date: null | YYYY-MM-DD | YYYY-MM | YYYY
  precision: day | month | quarter | year | label
  label: ...
  kind: source_date | earnings_date | filing_date | verify_at | thesis_updated | label
```

Rows without parseable dates are still displayable. Timeline filter may exclude them unless a later "include undated" control is added.

## Proposed Cluster Records

Thesis cluster:

```yaml
id: thesis-cluster:n3-logic
label: N3 logic wafers
slug: n3_logic
parent_bucket: Chips
status: active
period: 2025-2027
cycle_phase: mid_shortage
company_ids: [...]
signal_ids: [...]
claim_ids: [...]
position_ids: [...]
counts:
  companies: ...
  signals: ...
  claims: ...
  positions: ...
```

Company category:

```yaml
id: company-category:chip-designer
label: Chip designers
rank: 2
company_ids: [...]
```

Signal cluster:

```yaml
id: signal-cluster:baker
label: Baker
cluster_type: source_channel
source_kind: fund_positioning
aliases:
  - atreides
  - gavin-baker
source_paths:
  - canonical/20-data/sources/baker/q4_2025.yaml
  - canonical/10-wiki/sources/baker-q4-2025.md
position_ids: [...]
signal_ids: [...]
claim_ids: [...]
company_ids: [...]
summary: Baker/Atreides positioning and thesis read-through.
```

## Proposed Row Models

Company row:

```yaml
id: company:NVDA
ticker: NVDA
name: NVIDIA Corporation
company_category_id: company-category:chip-designer
thesis_cluster_ids: [...]
signal_cluster_ids: [...]
status: active
source_page: nvda-q4-fy2026
metrics: {...}
positions_summary: {...}
counts: {...}
search_text: ...
```

Position row:

```yaml
id: position:baker:NVDA:q4-2025:01
source_cluster_id: signal-cluster:baker
source_kind: fund_positioning
company_id: company:NVDA
ticker: NVDA
fund: baker
quarter: Q4 2025
period: 2025-12-31
filed: 2026-02-17
position_type: call
value: 653000000
shares: 3500000
pct_portfolio: 0.08
change_vs_prior: new
bottleneck: n3_logic
thesis_cluster_ids: [...]
source_paths:
  - canonical/20-data/sources/baker/q4_2025.yaml
timeline:
  date: 2026-02-17
  precision: day
  label: Filed Feb 17 2026
```

Signal row:

```yaml
id: signal:semianalysis:2026-04-02:01
source_cluster_id: signal-cluster:semianalysis
source_kind: supply_chain_research
company_ids:
  - company:NVDA
  - company:CRWV
  - company:TSM
thesis_cluster_ids: [...]
kind: semianalysis_signal
direction: signal
title: The Great GPU Shortage - Rental Capacity
evidence: ...
source_paths:
  - canonical/20-data/sources/semianalysis/signals.yaml
timeline:
  date: 2026-04-02
  precision: day
  label: Apr 2 2026
```

Claim row:

```yaml
id: claim:NVDA:q4-fy2026:01
source_cluster_id: signal-cluster:company-earnings
source_kind: company_reported
company_id: company:NVDA
thesis_cluster_ids: [...]
claim: ...
status: pending
verify_at: Q1 FY2027 earnings (~May 2026)
timeline:
  date: null
  precision: label
  label: verify at Q1 FY2027 earnings
source_page: nvda-q4-fy2026
source_paths:
  - canonical/20-data/companies/NVDA/q4_fy2026.yaml
```

## Proposed Graph Projection

Do not use current `canonical/site-data/graph.json` directly.

First slice:

- graph nodes are companies only
- edges are projection edges
- edge evidence resolves to row IDs in `signal_desk.json`

Allowed first-slice edge sources:

1. Fund co-position edges:
   - companies held by same fund
   - source cluster: Baker or Leopold
   - weight by combined position size or count
2. SemiAnalysis co-signal edges:
   - companies mentioned in the same SemiAnalysis signal
   - source cluster: SemiAnalysis
   - weight by shared signal count
3. Thesis co-cluster edges:
   - companies in same thesis cluster
   - lower default weight
4. Company earnings read-through edges:
   - only if encoded explicitly
   - do not infer broad supplier/customer links from prose

Graph edge:

```yaml
id: graph-edge:semianalysis:NVDA:TSM
source: company:NVDA
target: company:TSM
edge_type: shared_signal_cluster
source_cluster_id: signal-cluster:semianalysis
evidence_ids:
  - signal:semianalysis:2026-03-15:02
weight: 2
```

Trace:

- disabled in first slice
- no generic traversal over provenance edges
- unpark only after value-chain-safe edge eligibility exists

Future rank model:

```yaml
0: equipment
1: foundry | memory | packaging | materials
2: chip_designer
3: server_oem | networking | optics | power
4: gpu_cloud | data_center | hyperscaler
5: ai_lab | application
```

## Company Category Challenge

Current semi-stocks `company.bottleneck` values are thesis bottlenecks:

```text
n3_logic
pluggable_optics
cpo_next
copper_signal_integrity
memory
power
gpu_cloud
euv
foundry
```

Justin categories are economic roles:

```text
equipment
foundry
memory
packaging
chip_designer
server_oem
networking
power
data_center
neocloud
hyperscaler
ai_lab
investor
```

Signal Desk should not confuse these.

Needed mapping examples:

```yaml
NVDA: chip-designer
TSM: foundry
MU: memory
COHR: optics
LITE: optics
CIEN: networking or optics
CRWV: gpu-cloud
NBIS: gpu-cloud
BE: power
CORZ: power or data-center/power-landlord
IREN: gpu-cloud or power-landlord, depending model
ASML: equipment
AMAT: equipment
KLAC: equipment
LRCX: equipment
```

Research Pro should challenge whether `optics` should be a first-class company category or fit under `networking`, and whether `gpu_cloud`, `neocloud`, and `data_center` need separate categories.

## Timeline Challenge

Justin deals all have normalized dates. Semi-stocks evidence does not.

Current state:

- only 9 of 67 signals have exact `date`
- 25 signals have `quarter`
- 33 thesis-stage signals come from `thesis.yaml`
- claims have textual `verify_at`
- fund positions have filing dates in source YAML, but generated company positions lose those fields

Needed:

- keep timeline nullable but display-safe
- distinguish `date`, `precision`, `label`, `kind`
- timeline filter should not silently drop important undated rows without UX affordance

Research Pro should challenge whether first slice should ship Timeline at all, or ship it with an "undated included" policy.

## Source Cluster Challenge

Signal cluster must be source/channel, not topic.

Why:

- Ash explicitly corrected this meaning.
- Selecting `Leopold` should show Leopold-positioned companies and context.
- Selecting `Baker` should show Baker-positioned companies and context.
- Selecting `SemiAnalysis` should show companies touched by SemiAnalysis signals.
- Topic clusters should come later under or across source clusters.

Implication:

- `signal_clusters` must include `position_ids`, not only `signal_ids`.
- `positions` must be first-class.
- Each profile panel needs to explain why selected source clusters touch a company.

## Review And Prediction Vocabulary

Do not create first-class `reviews` table yet.

Current evidence:

- no `reviews.json`
- no stored review object in current generator
- likely "reviews" is a derived count over curated signals

Do not call canonical claims "predictions" in the first slice.

Current evidence:

- canonical `claims.json` has 43 source-backed forward claims/proof gates
- sidecar `agents/state/predictions/*.yaml` is a separate agent prediction lifecycle
- agent predictions should not be imported unless explicitly approved

Preferred UI terms:

```text
Claims
Proof gates
Reviewed signals, if a count is needed
```

## Implementation Plan

Phase 1: data contract

1. Add `signal_desk` artifact to `canonical/40-engine/engine/site_data.py`.
2. Build first-class fund positions from source YAML.
3. Build thesis clusters.
4. Build company categories and ranks.
5. Build source-channel signal clusters.
6. Build table projections.
7. Build graph projection.
8. Extend validation.
9. Write `canonical/site-data/signal_desk.json`.

Phase 1 verify:

```bash
uv run python canonical/40-engine/site_data.py --validate
python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null
```

Phase 2: reader shell

1. Scaffold Vite/React reader in `canonical/site-reader/`.
2. Copy/adapt Justin theme and controls with attribution.
3. Load `../site-data/signal_desk.json`.
4. Render graph.
5. Render evidence table.
6. Render profile panel.

Phase 2 verify:

```bash
cd canonical/site-reader
npm install
npm run build
npm run test
```

Phase 3: filters and interaction

1. Search.
2. Timeline.
3. Thesis Cluster.
4. Company Category.
5. Signal Cluster.
6. Edge/company click panels.

Phase 4: Trace

Only after graph projection is trustworthy:

1. Add ranks.
2. Add edge eligibility.
3. Add pathfinding.
4. Add hop chips and path groups.
5. Verify examples manually.

## Current Locked Tasks

Task list lives at:

```text
docs/artifacts/signal-desk-schema/05_tasks.md
```

Locked task IDs:

```text
SD-L1 Add signal_desk.json collection
SD-L2 Promote fund positions to first-class rows
SD-L3 Normalize source-channel clusters
SD-L4 Add timeline and search projections
SD-L5 Add thesis and company category projections
SD-L6 Build Signal Desk graph projection
SD-L7 Extend schema and validation
SD-L8 Scaffold Justin-style reader only after data gate
SD-L9 Park Trace
```

## Acceptance Criteria

Data:

- `signal_desk.json` generated from canonical source data.
- No UI reads canonical markdown/YAML directly.
- Source clusters include Baker, Leopold, SemiAnalysis, company earnings, thesis stage, pending proposals.
- Baker/Leopold source clusters include position rows.
- SemiAnalysis source cluster includes SemiAnalysis signal rows.
- Company earnings source cluster includes company thesis signals and claims.
- Every displayed row has source trace.
- Every displayed row has `search_text`.
- Every evidence row has `timeline`.
- Graph edge evidence IDs resolve to table rows.
- Trace is disabled.

UI:

- visual feel close to Justin's site
- toolbar density and interaction pattern match Justin where practical
- company rectangles with muted edges
- evidence table replaces transaction table
- profile panel explains selected company/edge context
- selecting/deselecting source clusters changes graph/table/profile context

Non-goals:

- no enabled Trace in first slice
- no embeddings
- no topic clustering
- no agent prediction import
- no human review workflow
- no full wiki reader
- no direct UI parsing of canonical source files

## Known Risks

1. Source metadata mismatch:
   - signals have `source_path`
   - claims do not
   - positions lose source metadata after flattening

2. Timeline mismatch:
   - mixed exact dates, quarters, fiscal periods, filing dates, and labels

3. Graph certainty mismatch:
   - current edges are evidence/provenance/wiki/report edges
   - Justin edges are directed transaction edges

4. Category mismatch:
   - thesis bottlenecks are not company role categories

5. Position fidelity mismatch:
   - Baker multi-leg positions collapse from 20 source rows to 16 generated company rows

6. UI complexity:
   - toolbar has Trace, Timeline, Thesis Cluster, Company Category, Signal Cluster, Search
   - may need to collapse cluster controls later, but first spec keeps them explicit

7. Licensing/attribution:
   - Justin UI repo license metadata says MIT
   - Justin data repo says data CC BY 4.0, scripts/schemas MIT
   - If CSS/components are copied, preserve notices in `canonical/site-reader/THIRD_PARTY_NOTICES.md`

## Research Pro Questions

Please answer these directly.

### Data Readiness

1. Is `signal_desk.json` the right boundary, or should it be split into several contract files?
2. Are `positions`, `signals`, and `claims` the right first-class evidence rows?
3. Should fund positions be generated directly from source YAML instead of `companies.json`?
4. What minimum fields are missing from current `site-data` to support source-channel filtering?
5. Should claims gain `source_path`, or should source trace be represented as `source_refs` only?

### Source Clusters

6. Is source/channel clustering the right primary Signal Cluster model?
7. Should `company earnings` and `thesis stage` be separate source clusters, or should thesis-stage signals be a thesis cluster facet only?
8. How should pending thesis proposals appear in graph/table/profile without implying they are accepted?

### Categories

9. What is the best first category taxonomy for semi-stocks company roles?
10. Should `optics` be separate from `networking`?
11. Should `gpu_cloud`, `neocloud`, and `data_center` be separate in first slice?
12. Should `investor` exist as a company category if Baker/Leopold are source clusters, not company nodes?

### Timeline

13. Should Timeline ship in first UI slice given the mixed date precision?
14. What should happen to rows with `timeline.date: null`?
15. Is `precision: day|month|quarter|year|label` enough?

### Graph

16. Are co-position, co-signal, thesis co-cluster, and explicit read-through enough for first graph edges?
17. How should edge weights be computed?
18. Should graph edges be directed or undirected before Trace?
19. What graph projection would avoid misleading supplier/customer implication?

### Trace

20. Should Trace be visible disabled, hidden, or omitted until graph is ready?
21. What exact data fields would be required to safely enable Trace?
22. Could a source-channel evidence graph ever support Trace, or does Trace require a separate value-chain relationship dataset?

### UI

23. Is the six-control toolbar too dense?
24. Should three cluster controls remain separate or be one Cluster dropdown with tabs?
25. Which Justin components should be copied nearly verbatim, and which should be rewritten?
26. What mobile compromises are needed?

### Validation And Implementation

27. What validator rules are mandatory before UI scaffolding?
28. What tests should be written for filter semantics?
29. What implementation order would reduce rework?
30. What should be cut from the first slice?

## Source Pack

The repo-local paths below are included so Research Pro can understand what local evidence generated this brief. If Research Pro cannot read local files, use the External Links section for Justin source and use the summaries/counts above for semi-stocks state.

Semi-stocks docs:

```text
README.md
AGENTS.md
docs/architecture.md
docs/doc-contract.md
docs/artifacts/canonical-propagation-model/07_implementation-spec.md
docs/artifacts/lightweight-visual-layer/03_research.md
docs/artifacts/lightweight-visual-layer/04_design.md
docs/artifacts/lightweight-visual-layer/site-data-contract.md
```

Signal Desk artifacts:

```text
docs/artifacts/signal-desk-schema/00_summary.md
docs/artifacts/signal-desk-schema/01_spec.md
docs/artifacts/signal-desk-schema/02_questions.md
docs/artifacts/signal-desk-schema/03_research.md
docs/artifacts/signal-desk-schema/04_design.md
docs/artifacts/signal-desk-schema/05_tasks.md
docs/artifacts/signal-desk-schema/06_justin_mapping.md
docs/artifacts/signal-desk-schema/07_ui_replication_notes.md
docs/artifacts/signal-desk-schema/08_top_controls_iteration.md
docs/artifacts/signal-desk-schema/09_final_spec.md
docs/artifacts/signal-desk-schema/10_readiness_challenge.md
docs/artifacts/signal-desk-schema/11_justin_surface_compare.md
docs/artifacts/signal-desk-schema/12_research_pro_brief.md
docs/artifacts/signal-desk-schema/relevant_sources.md
```

Signal Desk diagrams:

```text
docs/diagrams/signal-desk-readiness-shifts.png
docs/diagrams/signal-desk-final-spec-flow.png
docs/diagrams/signal-desk-schema-minimum.png
```

Generator files:

```text
canonical/40-engine/site_data.py
canonical/40-engine/engine/site_data.py
canonical/40-engine/engine/synthesis.py
canonical/40-engine/engine/company_data.py
canonical/40-engine/engine/paths.py
canonical/40-engine/engine/sources/fund_13f.py
canonical/40-engine/engine/sources/semianalysis.py
```

Current generated data:

```text
canonical/site-data/build.json
canonical/site-data/schema.json
canonical/site-data/pages.json
canonical/site-data/companies.json
canonical/site-data/signals.json
canonical/site-data/claims.json
canonical/site-data/entities.json
canonical/site-data/edges.json
canonical/site-data/thesis.json
canonical/site-data/reports.json
canonical/site-data/search.json
canonical/site-data/graph.json
```

Core canonical data:

```text
canonical/20-data/sources/leopold/q4_2025.yaml
canonical/20-data/sources/baker/q4_2025.yaml
canonical/20-data/sources/semianalysis/signals.yaml
canonical/20-data/companies/**
canonical/20-data/thesis-proposals/**
canonical/30-thesis/thesis.yaml
```

Wiki:

```text
canonical/10-wiki/schema.md
canonical/10-wiki/index.md
canonical/10-wiki/_lint.json
canonical/10-wiki/concepts/**
canonical/10-wiki/sources/**
canonical/10-wiki/outputs/**
```

Justin UI reference:

```text
GitHub repo: https://github.com/jstwng/compute-site
Pinned tree: https://github.com/jstwng/compute-site/tree/1f90a873c44ceea03240ccb5658e115dbc40e6c6
/tmp/compute-site-signal-desk/src/App.jsx
/tmp/compute-site-signal-desk/src/styles.css
/tmp/compute-site-signal-desk/src/app.css
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/Toolbar.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/Dropdown.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/MobileFilterSheet.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/Graph.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/DealTable.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/ProfilePanel.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/FilterBar.jsx
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/logic.js
/tmp/compute-site-signal-desk/src/components/ComputeDealMap/styles.module.css
/tmp/compute-site-signal-desk/scripts/vite-plugin-deal-data.mjs
```

Justin data reference:

```text
GitHub repo: https://github.com/jstwng/compute-deal-map-data
Pinned tree: https://github.com/jstwng/compute-deal-map-data/tree/e5c0e740b2f34ee56b6073e2e237b2dddc0c564d
Latest release artifacts:
https://github.com/jstwng/compute-deal-map-data/releases/latest/download/companies.json
https://github.com/jstwng/compute-deal-map-data/releases/latest/download/deals.json
https://github.com/jstwng/compute-deal-map-data/releases/latest/download/schema.json
/tmp/compute-deal-map-data-signal-desk/README.md
/tmp/compute-deal-map-data-signal-desk/companies.yml
/tmp/compute-deal-map-data-signal-desk/deals/*.yml
/tmp/compute-deal-map-data-signal-desk/schema/company.schema.json
/tmp/compute-deal-map-data-signal-desk/schema/deal.schema.json
/tmp/compute-deal-map-data-signal-desk/scripts/build.js
/tmp/compute-deal-map-data-signal-desk/scripts/validate.js
```

Sidecar prediction references, relevant only to avoid confusing claims with predictions:

```text
agents/autoagent/program.md
agents/state/predictions/*.yaml
```

## Recommended Research Pro Output Shape

Ask Research Pro to return:

1. Revised architecture verdict.
2. Revised `signal_desk.json` schema.
3. Field-level changes by row type.
4. Graph projection recommendation.
5. Trace gating recommendation.
6. Category taxonomy recommendation.
7. Timeline policy.
8. UI control recommendation.
9. Implementation sequence.
10. Validator/test checklist.
11. Anything to cut from first slice.

The key bar:

Do not let the final spec drift into a polished UI plan that overstates current data certainty. The data contract must make provenance, confidence, and graph semantics explicit before UI work starts.
