---
status: superseded-by-final-mvp-spec
feature: signal-desk-schema
updated: 2026-04-19
supersedes: 09_final_spec.md
---

# Final Spec v0.2: Signal Desk

> Superseded for implementation by [17_final_mvp_spec.md](17_final_mvp_spec.md).
> This file remains as historical context for the pre-finalization v0.2 spec.

## Visual

![Signal Desk readiness shifts](../../diagrams/signal-desk-readiness-shifts.png)

## Purpose

Build a Justin-style Signal Desk reader over semi-stocks canonical data.

The surface should borrow Justin Wang's dense graph-first feel, but it must not borrow Justin's data semantics. Justin's compute map is a directed transaction graph. Signal Desk v0.2 is a contextual evidence graph with source-channel filtering, evidence rows, source documents, profile panels, and explicit provenance.

## Final Lock

Implementation starts with a generated data contract:

```text
canonical/site-data/signal_desk.json
```

Do not scaffold `canonical/site-reader/` until `signal_desk.json` exists and validates.

Trace is parked. First-slice graph is contextual, undirected, and not value-chain pathfinding.

## Vocabulary

| Old term | Final term | Reason |
|---|---|---|
| Signal Cluster | Source Channel | Baker/Leopold/SemiAnalysis/etc. are source/evidence channels |
| Company Category | Company Role | intended lens is economic role / value-chain role |
| Category / Thesis Cluster | Thesis Theme | separate from company role and source channel |
| Signal direction | Impact Direction | avoids conflict with graph edge direction |
| Status | Lifecycle State | row types have different lifecycle vocabularies |

## Top-Level Contract

```yaml
version: signal-desk-v0.2
build:
  generated_at: ...
  generator: site-data-v0.2
  source_hash: ...
  collection_hashes:
    companies: ...
    source_documents: ...
    rows: ...
    graph: ...
features:
  search: true
  timeline: true
  trace:
    status: parked
    reason: requires explicit value-chain edges
defaults:
  filters:
    search: ""
    source_channel_ids: []
    thesis_theme_ids: []
    company_role_ids: []
    include_undated: true
quality:
  ui_ready: true
  trace_ready: false
  rows_without_source_document: 0
  rows_without_sort_date: ...
  rows_with_label_only_timeline: ...
  graph_edges_contextual_only: true
  trace_blockers:
    - no explicit relationship_edges dataset
    - current graph is evidence/provenance, not value-chain
facets:
  source_channels: [...]
  thesis_themes: [...]
  company_roles: [...]
source_documents: [...]
companies: [...]
rows: [...]
graph:
  mode: contextual_evidence
  nodes: [...]
  edges: [...]
indexes:
  row_ids_by_type: {...}
  row_ids_by_company: {...}
  row_ids_by_source_channel: {...}
  company_ids_by_thesis_theme: {...}
tables:
  default: signals
  views:
    signals:
      row_ids: [...]
      columns: [...]
    claims:
      row_ids: [...]
      columns: [...]
    positions:
      row_ids: [...]
      columns: [...]
    proposals:
      row_ids: [...]
      columns: [...]
    sources:
      source_document_ids: [...]
      columns: [...]
```

## Source Documents

`source_documents` are first-class. They normalize provenance for UI joins while preserving raw repo paths for traceability.

Example:

```yaml
id: source-doc:baker:q4-2025
channel_id: source-channel:baker
document_kind: 13f_filing
title: Atreides Management LP Q4 2025 13F
canonical_path: canonical/20-data/sources/baker/q4_2025.yaml
wiki_page_slug: baker-q4-2025
external_url: null
source_date: 2026-02-17
period:
  system: calendar_quarter
  year: 2025
  quarter: 4
  end_date: 2025-12-31
search_text: ...
```

Initial document kinds:

- `13f_filing`
- `supply_chain_research`
- `company_packet`
- `thesis_control`
- `thesis_proposal`
- `wiki_source_page`

## Source Channels

Source channels replace the old `Signal Cluster` model.

Initial channels:

```yaml
source_channels:
  - id: source-channel:leopold
    label: Leopold
    channel_kind: fund_positioning
    aliases: [situational-awareness, situational awareness]
  - id: source-channel:baker
    label: Baker
    channel_kind: fund_positioning
    aliases: [atreides, gavin-baker]
  - id: source-channel:semianalysis
    label: SemiAnalysis
    channel_kind: supply_chain_research
    aliases: [sem, semi-analysis, sa, dylan-patel]
  - id: source-channel:company-earnings
    label: Company earnings
    channel_kind: company_reported
  - id: source-channel:thesis-stage
    label: Thesis stage
    channel_kind: thesis_control
  - id: source-channel:pending-proposals
    label: Pending proposals
    channel_kind: thesis_proposal
```

Future topic clusters are subordinate to source channels and are not part of the first slice.

## Company Roles

Company roles replace the old `Company Category` model.

First primary role set:

```yaml
company_roles:
  - id: company-role:equipment
    label: Equipment
    rank: 0
  - id: company-role:foundry
    label: Foundry
    rank: 1
  - id: company-role:memory
    label: Memory
    rank: 1
  - id: company-role:packaging
    label: Packaging
    rank: 1
  - id: company-role:chip-designer
    label: Chip designers
    rank: 2
  - id: company-role:networking
    label: Networking
    rank: 3
  - id: company-role:optics
    label: Optics
    rank: 3
  - id: company-role:server-oem
    label: Server OEMs
    rank: 3
  - id: company-role:power-infrastructure
    label: Power infrastructure
    rank: 3
  - id: company-role:gpu-cloud
    label: GPU cloud
    rank: 4
  - id: company-role:hyperscaler
    label: Hyperscalers
    rank: 5
  - id: company-role:ai-lab
    label: AI labs
    rank: 6
```

Rules:

- `optics` remains separate from `networking`.
- `gpu_cloud` remains separate from `hyperscaler`.
- `neocloud` is a secondary label/tag in first slice.
- `data_center` is secondary until pure colocation/landlord data warrants primary role.
- `investor` is not a company role in first slice.
- no `company_role_id` may contain a thesis bottleneck slug.

Company row:

```yaml
id: company:NVDA
ticker: NVDA
name: NVIDIA Corporation
primary_role_id: company-role:chip-designer
secondary_role_ids: []
thesis_theme_ids: [...]
source_channel_ids: [...]
source_document_ids: [...]
counts:
  positions: ...
  signals: ...
  claims: ...
  proposals: ...
search_text: ...
```

## Thesis Themes

Thesis themes replace "Thesis Cluster" in implementation language.

Initial thesis themes come from `canonical/30-thesis/thesis.yaml` cascade stages, with optional parent buckets later.

Example:

```yaml
id: thesis-theme:n3-logic
label: N3 logic wafers
slug: n3_logic
status: active
period:
  system: label
  label: 2025-2027
cycle_phase: mid_shortage
company_ids: [...]
row_ids: [...]
```

## Unified Rows

All evidence rows live in one `rows` collection.

Allowed row types:

- `position`
- `signal`
- `claim`
- `proposal`

Every row has:

```yaml
id: ...
row_type: position | signal | claim | proposal
title: ...
summary: ...
company_ids: [...]
primary_company_id: ...
source_channel_id: ...
source_document_ids: [...]
source_paths: [...]
thesis_theme_ids: [...]
search_text: ...
period:
  system: calendar_quarter | fiscal_quarter | event_window | label | none
  year: ...
  quarter: ...
  fiscal_year: ...
  fiscal_quarter: ...
  end_date: ...
timeline:
  sort_date: null
  end_date: null
  precision: day | month | quarter | year | label
  label: ...
  kind: filed_date | published_date | period_end | verify_window | thesis_updated | proposal_updated | label
  include_in_range: true
graph_eligibility:
  eligible: true
  family: co_position | shared_signal | shared_thesis | explicit_relationship | null
  reason: ...
lifecycle_state: ...
ui_badges: [...]
```

### Position Rows

Generate position rows directly from fund YAML, not from flattened `companies.json`.

One raw filing leg equals one row.

Required extras:

```yaml
fund_id: baker
period:
  system: calendar_quarter
  year: 2025
  quarter: 4
  end_date: 2025-12-31
filed_date: 2026-02-17
position_leg_id: position:baker:NVDA:q4-2025:call:01
position_type: call
shares: 3500000
value: 653000000
pct_portfolio: 0.08
change_vs_prior: new
underlier_ticker: NVDA
lifecycle_state: reported
```

Acceptance:

- Baker source has 20 position rows and generated output preserves 20 raw position rows.
- Leopold source has 25 position rows and generated output preserves 25 raw position rows.
- no multi-leg collapse unless a separate summary row uses `collapsed_from_ids`.

### Signal Rows

Required extras:

```yaml
signal_kind: company_thesis_signal | semianalysis_signal | thesis_stage_signal
impact_direction: confirms | contradicts | supports | signal | proposed
excerpt_locator: ...
lifecycle_state: observed | curated
```

Do not use `direction` for signal implication; reserve direction language for graph/value-chain semantics.

### Claim Rows

Required extras:

```yaml
claim_type: earnings_claim | readthrough_claim | proof_gate | thesis_claim
verification_state: pending_verification | verified | disconfirmed | stale
verification_target: ...
verification_window_label: ...
claim_text: ...
rationale: ...
staleness_policy: ...
```

Claims must gain `source_document_ids` and `source_paths`.

### Proposal Rows

Pending thesis proposals are their own row type, not signals or claims.

Required extras:

```yaml
proposal_type: thesis_patch
decision_state: pending | accepted | rejected | superseded
affected_company_ids: [...]
affected_thesis_theme_ids: [...]
graph_eligibility:
  eligible: false
  family: null
  reason: pending proposals do not create graph edges in first slice
```

## Timeline Policy

Timeline ships in the data contract immediately. It is not a top-level UI control in the first reader pass.

Rows with `timeline.sort_date: null`:

- remain visible in table, search, graph counts, and profile context
- are included by default because `include_undated: true`
- are excluded only when the user explicitly applies date-bounded filtering that excludes undated rows

Required date validation:

- every row has a `timeline` object
- machine date strings must be validated as real dates
- if using Python `jsonschema`, format validation must be explicitly enabled with a format checker

## Graph Contract

First graph mode:

```yaml
graph:
  mode: contextual_evidence
```

Graph rules:

- company nodes only
- edges are undirected
- no arrows
- no supplier/customer implication
- no pending-proposal edges
- no inferred relationship from prose
- no direct reuse of `canonical/site-data/graph.json`

Allowed edge families:

- `co_position`
- `shared_signal`
- `shared_thesis`
- `explicit_relationship`

`explicit_relationship` requires typed canonical relationship data. Prose read-through is not enough.

Edge shape:

```yaml
id: edge:company:NVDA:company:TSM
source: company:NVDA
target: company:TSM
directed: false
trace_eligible: false
support:
  - family: co_position
    source_channel_id: source-channel:baker
    score: 0.72
    row_ids: [...]
  - family: shared_signal
    source_channel_id: source-channel:semianalysis
    score: 1
    row_ids: [...]
visual_weight: 1.72
semantic_label: shared_evidence
```

Weight guidance:

- `co_position`: normalized support such as `sqrt(pct_a * pct_b)` per fund, not raw market value
- `shared_signal`: count of shared curated signals
- `shared_thesis`: small contextual bonus
- `explicit_relationship`: strongest weight, only when typed

## Trace Policy

Trace is parked.

First UI:

- desktop: hidden or clearly parked; if visible, it must not look like a normal active control
- mobile: omitted

Trace unblocks only with a separate relationship dataset:

```yaml
relationship_edges:
  - id: relationship-edge:...
    source_company_id: ...
    target_company_id: ...
    relationship_type: supplier_customer | capacity_contract | component_dependency | ...
    direction: upstream_to_downstream
    trace_eligible: true
    value_chain_rank_from: ...
    value_chain_rank_to: ...
    evidence_ids: [...]
    effective_dates: {...}
    confidence: ...
```

A source-channel evidence graph does not support Trace by itself.

## UI Model

Borrow Justin's surface discipline, not the full first-day control budget.

Desktop first slice:

```text
Search | Source Channel | Company Role | Filters
```

Filters popover:

- Thesis Theme
- Timeline

Trace:

- hidden or parked on desktop
- omitted on mobile

Mobile first slice:

```text
Search
Filters
```

Bottom sheet sections:

- Source Channel
- Company Role
- Thesis Theme
- Timeline

Copy or closely adapt from Justin:

- density tokens
- dropdown shell behavior
- one-open-panel-at-a-time behavior
- mobile bottom sheet pattern
- graph node rectangle measurement shell
- hover/focus dimming shell
- profile panel / bottom-sheet shell

Rewrite:

- data loading
- directed-deal logic
- table model
- profile renderers
- edge click semantics
- graph support aggregation
- all Trace/pathfinding logic

## Validation Gate

Before UI scaffolding, validator must prove:

- every company has a stable ID and valid `primary_role_id`
- every row has `row_type`, `search_text`, `source_channel_id`, and `source_document_ids`
- every `source_document_id` resolves
- every company ID in every row resolves
- every graph node resolves to a company
- every graph edge `support[].row_ids[]` resolves to rows
- every graph support row touches both companies or is explicitly allowed by the support family
- proposals are never graph-eligible in first slice
- Baker/Leopold output raw position counts match source YAML row counts exactly
- no multi-leg collapse unless `collapsed_from_ids` is emitted
- no `company_role_id` contains a bottleneck value
- every row has a `timeline` object
- all machine dates pass real format validation
- `quality.trace_ready` is false
- `graph.mode` is `contextual_evidence`

## Implementation Order

1. Normalize source documents.
2. Promote raw fund positions directly from YAML.
3. Normalize row base and row variants.
4. Define company roles and thesis themes.
5. Build source channels.
6. Generate company summaries.
7. Generate graph support arrays.
8. Write validators and fixture tests.
9. Emit `signal_desk.json`.
10. Scaffold reader.

## First-Slice Cuts

Cut from first slice:

- top-toolbar Timeline
- graph edges from pending proposals
- enabled Trace
- inferred supplier/customer edges from prose
- duplicated row payloads under `tables.*`
- Sources tab without `source_documents`
- any merge of bottlenecks and company roles
- user-facing label `Signal Cluster`

## Verification Commands

Data contract:

```bash
uv run python canonical/40-engine/site_data.py --validate
python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null
```

Reader only after data gate:

```bash
cd canonical/site-reader
npm install
npm run build
npm run test
```
