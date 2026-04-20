---
status: final-mvp-spec
feature: signal-desk-schema
updated: 2026-04-19
supersedes: 14_final_spec_v0_2.md
---

# Final MVP Spec: Signal Desk

## Visual

![Signal Desk readiness shifts](../../diagrams/signal-desk-readiness-shifts.png)

## Architecture Verdict

Signal Desk MVP is a web-only, data-contract-first evidence reader over `semi-stocks-2`.

It is not a clone of Justin Wang's directed deal semantics. Justin's site is a directed transaction graph. Signal Desk MVP is a contextual evidence graph over semi-stocks source channels, evidence rows, source documents, company roles, thesis themes, and profile context.

Implementation sequence:

1. Generate and validate `canonical/site-data/signal_desk.json`.
2. Build a web reader that consumes only that artifact.

Do not scaffold the reader until the data artifact passes validation.

## MVP Scope

Web target:

```text
large-screen browser viewport, roughly 1280px+ wide
```

MVP surface:

- header/title area
- search
- visible Source Channel filter
- visible Company Role filter
- secondary Filters popover for Thesis Theme, Timeline, Include undated
- contextual company graph
- tabbed evidence table
- right-side profile panel

Graph, table, and profile must be usable at the same time in the large-screen web layout.

## Non-Goals

Do not implement in MVP:

- mobile bottom sheets
- mobile toolbar/chip rows
- mobile-first layout behavior
- enabled Trace
- relationship pathfinding
- inferred supplier/customer edges from prose
- `shared_thesis` graph edges
- `explicit_relationship` graph edges
- topic clustering
- agent prediction import
- human review workflow
- wiki-reader behavior in the UI
- direct reader parsing of canonical markdown or YAML

Trace is absent from the MVP toolbar. It may exist only in the artifact as `features.trace.status: parked`.

## Generated Artifact

Path:

```text
canonical/site-data/signal_desk.json
```

All top-level keys are required:

```yaml
version: signal-desk-v0.2

build:
  generated_at: ...
  generator: site-data-v0.2
  source_hash: ...
  collection_hashes:
    facets: ...
    source_documents: ...
    companies: ...
    rows: ...
    graph: ...
    indexes: ...
    tables: ...

features:
  search: true
  timeline: true
  trace:
    status: parked
    visible: false
    reason: requires a separate typed relationship_edges dataset

defaults:
  filters:
    search: ""
    source_channel_ids: []
    company_role_ids: []
    thesis_theme_ids: []
    timeline:
      from: null
      to: null
    include_undated: true

quality:
  ui_ready: true
  trace_ready: false
  rows_without_source_document: 0
  rows_without_sort_date: 0
  rows_with_label_only_timeline: 0
  graph_edges_contextual_only: true
  position_leg_counts:
    baker:
      source: 20
      emitted: 20
    leopold:
      source: 25
      emitted: 25
  trace_blockers:
    - no relationship_edges dataset
    - no typed directional value-chain edges
    - graph is contextual evidence only

facets:
  source_channels: [...]
  company_roles: [...]
  thesis_themes: [...]
  row_types: [position, signal, claim, proposal]
  graph_support_families: [co_position, shared_signal]

source_documents: [...]
companies: [...]
rows: [...]

graph:
  mode: contextual_evidence
  default_enabled_support_families: [co_position, shared_signal]
  nodes: [...]
  edges: [...]

indexes:
  row_ids_by_type: {...}
  row_ids_by_company: {...}
  row_ids_by_source_channel: {...}
  row_ids_by_thesis_theme: {...}
  company_ids_by_role: {...}
  company_ids_by_thesis_theme: {...}
  source_document_ids_by_source_channel: {...}

tables:
  default_view_id: signals
  view_order: [signals, claims, positions, proposals, sources]
  views: {...}
```

Top-level rules:

- `version` is fixed: `signal-desk-v0.2`
- `features.trace.visible` must be `false`
- `quality.trace_ready` must be `false`
- `graph.mode` must be `contextual_evidence`
- `facets.graph_support_families` contains only `co_position` and `shared_signal`
- every collection list is deterministically ordered before write
- every ID is stable across builds when source identities are stable

Nullability:

- top-level keys are never nullable
- optional URLs may be null
- machine dates may be null when date precision is absent
- optional arrays use empty arrays rather than null
- `primary_company_id` may be null for multi-company rows
- timeline defaults `from` and `to` are null
- unused `period` subfields are null

## Facets

### Source Channels

Required fields:

```yaml
id: source-channel:baker
label: Baker
channel_kind: fund_positioning
aliases: [atreides, gavin-baker]
description: Baker / Atreides fund-positioning evidence.
counts:
  companies: 0
  rows: 0
  source_documents: 0
search_text: baker atreides gavin-baker fund positioning
```

All fields are required. `aliases` may be empty. `description` may be empty. `counts.*` are required integers.

MVP source channels:

- `source-channel:leopold`
- `source-channel:baker`
- `source-channel:semianalysis`
- `source-channel:company-earnings`
- `source-channel:thesis-stage`
- `source-channel:pending-proposals`

### Company Roles

Required fields:

```yaml
id: company-role:chip-designer
label: Chip designers
rank: 2
aliases: []
description: Companies primarily designing semiconductors or accelerators.
counts:
  companies: 0
  rows: 0
search_text: chip designer semiconductor design accelerator fabless
```

MVP role set:

- `company-role:equipment`
- `company-role:foundry`
- `company-role:memory`
- `company-role:packaging`
- `company-role:chip-designer`
- `company-role:networking`
- `company-role:optics`
- `company-role:server-oem`
- `company-role:power-infrastructure`
- `company-role:gpu-cloud`
- `company-role:hyperscaler`
- `company-role:ai-lab`

Source-fidelity roles added during implementation:

- `company-role:software-services`
- `company-role:market-basket`

These preserve raw 13F rows that are part of Baker/Leopold source documents, such as INFY and QQQ. They are not thesis/value-chain roles and should be visually de-emphasized if the web UI needs to keep the core semi-stack cleaner.

Role mapping:

- add explicit mapping file: `canonical/20-data/company_roles.yaml`
- every visible company must have one `primary_role_id`
- optional `secondary_role_ids`
- optional `display_tags`
- `neocloud` and `data_center` may be `display_tags`, not primary roles in MVP
- no fallback from bottleneck slugs
- no fallback from thesis themes
- unknown role mappings fail validation

### Thesis Themes

Required fields:

```yaml
id: thesis-theme:n3-logic
slug: n3_logic
label: N3 logic wafers
status: active
period: {...}
parent_bucket: null
cycle_phase: mid_shortage
counts:
  companies: 0
  rows: 0
search_text: n3 logic wafers
```

Rules:

- source primarily from `canonical/30-thesis/thesis.yaml`
- `parent_bucket` nullable
- `cycle_phase` nullable
- `status` enum: `active`, `watch`, `inactive`
- rows may have empty `thesis_theme_ids` when reliable assignment does not exist
- theme assignment is not forced when uncertain

## Period And Timeline

### Period Object

Used by rows, source documents, and thesis themes.

```yaml
period:
  system: none | calendar_quarter | fiscal_quarter | date_range | label
  start_date: null
  end_date: null
  year: null
  quarter: null
  fiscal_year: null
  fiscal_quarter: null
  label: null
```

Rules:

- object is required everywhere it appears
- unused fields remain null
- `calendar_quarter` requires `year`, `quarter`, `end_date`
- `fiscal_quarter` requires `fiscal_year`, `fiscal_quarter`, and preferably `end_date` when known
- `date_range` requires at least one of `start_date` or `end_date`
- `label` requires `label`
- `none` requires all other fields null

### Timeline Object

Used by rows and source documents.

```yaml
timeline:
  sort_date: null
  end_date: null
  precision: day | month | quarter | year | label
  label: Filed Feb 17 2026
  kind: filed_date | published_date | period_end | verify_window | thesis_updated | proposal_updated | label
  include_in_range: true
```

Rules:

- object is always required
- `label` is always required
- `sort_date` drives filtering and default sorting
- label-only rows use `sort_date: null`, `precision: label`
- `include_in_range` defaults to true when `sort_date` exists
- `include_in_range` defaults to false when `sort_date` is null
- UI-level `include_undated` controls whether null sort-date rows survive active timeline filters

## Source Documents

`source_documents` are authoritative provenance objects.

MVP rule: one source-document record per authoritative canonical input file. Companion wiki source pages are metadata, not separate source documents.

Required fields:

```yaml
id: source-doc:baker:q4-2025
source_channel_id: source-channel:baker
document_kind: 13f_filing
title: Atreides Management LP Q4 2025 13F
canonical_path: canonical/20-data/sources/baker/q4_2025.yaml
related_paths:
  - canonical/10-wiki/sources/baker-q4-2025.md
wiki_page_slug: baker-q4-2025
external_url: null
company_ids: [...]
thesis_theme_ids: [...]
period: {...}
timeline: {...}
search_text: ...
```

Required keys:

- `id`
- `source_channel_id`
- `document_kind`
- `title`
- `canonical_path`
- `company_ids`
- `thesis_theme_ids`
- `period`
- `timeline`
- `search_text`
- `related_paths`
- `wiki_page_slug`
- `external_url`

Nullable:

- `external_url`
- `wiki_page_slug`

Rules:

- `related_paths` may be empty
- `company_ids` may be empty only for thesis-control documents with no direct company scope
- `canonical_path` points to the authoritative canonical source file, not generated output

MVP `document_kind` enum:

- `13f_filing`
- `supply_chain_research`
- `company_packet`
- `thesis_control`
- `thesis_proposal`

Do not emit `wiki_source_page` as a standalone document kind in MVP.

## Companies

Required fields:

```yaml
id: company:NVDA
ticker: NVDA
name: NVIDIA Corporation
primary_role_id: company-role:chip-designer
secondary_role_ids: []
display_tags: [neocloud]
thesis_theme_ids: [...]
source_channel_ids: [...]
source_document_ids: [...]
counts:
  positions: 0
  signals: 0
  claims: 0
  proposals: 0
  source_documents: 0
search_text: nvda nvidia corporation
```

Rules:

- all fields above are required
- `ticker` may be null only if the company truly has no ticker
- arrays may be empty except `source_channel_ids` for visible companies
- `source_document_ids` are deduplicated and stable
- `counts.*` are required integers

## Unified Rows

All evidence appears in `rows`.

MVP row types:

- `position`
- `signal`
- `claim`
- `proposal`

### Base Row Fields

Required on every row:

```yaml
id: row:signal:semianalysis:2026-04-02:01
row_type: signal
title: The Great GPU Shortage - Rental Capacity
summary: Short normalized summary for table and panel context.
company_ids: [...]
primary_company_id: null
source_channel_id: source-channel:semianalysis
source_document_ids: [...]
source_paths: [...]
thesis_theme_ids: [...]
search_text: ...
period: {...}
timeline: {...}
graph_eligibility:
  eligible: true
  family: shared_signal
  reason: multi-company signal row approved for contextual graph support
lifecycle_state: curated
ui_badges: [SemiAnalysis]
```

Rules:

- `company_ids` non-empty
- `source_document_ids` non-empty
- `source_paths` non-empty
- `primary_company_id` may be null
- if `primary_company_id` is not null, it must appear in `company_ids`
- `thesis_theme_ids` may be empty
- `ui_badges` may be empty
- `graph_eligibility.family` may be null only when `eligible` is false

### Position Row Extra Fields

```yaml
fund_id: baker
position_leg_id: baker:NVDA:q4-2025:call:01
position_type: call
filed_date: 2026-02-17
shares: 3500000
value: 653000000
pct_portfolio: 0.08
change_vs_prior: new
underlier_ticker: NVDA
```

Rules:

- generated directly from raw fund YAML
- one filing leg equals one row
- `period.system` is `calendar_quarter`
- `timeline.kind` is `filed_date`
- `timeline.sort_date` equals `filed_date`
- `graph_eligibility.eligible` true
- `graph_eligibility.family` is `co_position`

`position_type` enum:

- `equity`
- `call`
- `put`
- `other`

`change_vs_prior` enum:

- `new`
- `increased`
- `decreased`
- `unchanged`
- `unknown`

Nullable:

- `underlier_ticker`

### Signal Row Extra Fields

```yaml
signal_kind: company_thesis_signal | semianalysis_signal | thesis_stage_signal
impact_direction: supports | contradicts | mixed | signal | proposed
excerpt_locator: null
```

Rules:

- `signal_kind` required
- `impact_direction` required
- `excerpt_locator` required but nullable
- can contribute graph support only as `shared_signal`
- can be graph eligible only when it touches at least two companies and source channel is graph-approved

### Claim Row Extra Fields

```yaml
claim_type: earnings_claim | readthrough_claim | proof_gate | thesis_claim
claim_text: ...
verification_target: null
verification_window_label: null
rationale: ...
staleness_policy: stale after next earnings cycle if unresolved
```

Rules:

- claims do not create graph edges in MVP
- `graph_eligibility.eligible` false
- `graph_eligibility.family` null

`lifecycle_state` enum:

- `pending_verification`
- `verified`
- `disconfirmed`
- `stale`

Nullable:

- `verification_target`
- `verification_window_label`

### Proposal Row Extra Fields

```yaml
proposal_type: thesis_patch
affected_company_ids: [...]
affected_thesis_theme_ids: [...]
```

Rules:

- proposals do not create graph edges in MVP
- `graph_eligibility.eligible` false
- `graph_eligibility.family` null

`lifecycle_state` enum:

- `pending`
- `accepted`
- `rejected`
- `superseded`

`affected_company_ids` and `affected_thesis_theme_ids` may be empty, but should be populated when clear.

## Graph

Required graph shape:

```yaml
graph:
  mode: contextual_evidence
  default_enabled_support_families:
    - co_position
    - shared_signal
  nodes:
    - id: company:NVDA
      company_id: company:NVDA
      primary_role_id: company-role:chip-designer
      thesis_theme_ids: [...]
      source_channel_ids: [...]
  edges:
    - id: edge:company:NVDA__company:TSM
      company_ids:
        - company:NVDA
        - company:TSM
      trace_eligible: false
      semantic_label: shared_evidence
      support:
        - family: co_position
          source_channel_id: source-channel:baker
          score: 0.63
          row_ids: [...]
        - family: shared_signal
          source_channel_id: source-channel:semianalysis
          score: 0.67
          row_ids: [...]
      visual_weight: 1.3
```

Node rules:

- company nodes only
- node `id` equals `company_id`
- no thesis/source/page/report/provenance nodes

Edge rules:

- undirected
- use `company_ids`, not `source` / `target`
- `company_ids` contains exactly two IDs
- pair is lexicographically sorted
- edge ID format: `edge:<company-id-a>__<company-id-b>`
- `trace_eligible` false
- `semantic_label` is `shared_evidence`

### Support Families

Only emitted MVP support families:

- `co_position`
- `shared_signal`

Reserved but not emitted in MVP:

- `shared_thesis`
- `explicit_relationship`

#### `co_position`

A `co_position` support exists when both companies appear in the same fund filing.

Rules:

- one support object per `(family, source_channel_id, company pair)`
- Baker and Leopold remain separate support entries
- `row_ids` contains the specific position-leg rows for the pair in that fund/channel

Score:

```text
score = min(1.0, sqrt(pct_a * pct_b) / 0.10)
```

Rules:

- `pct_a` and `pct_b` are decimal portfolio weights
- if either weight is missing, validation fails
- score rounded consistently, e.g. 6 decimal places

#### `shared_signal`

A `shared_signal` support exists when a graph-eligible signal row touches both companies.

Rules:

- one support object per `(family, source_channel_id, company pair)`
- `row_ids` contains all graph-eligible multi-company signal rows that touch the pair

Score:

```text
score = min(1.0, shared_signal_row_count / 3)
```

### Visual Weight

```text
visual_weight = round(sum(support.score for support in edge.support), 6)
```

Renderer-oriented only. It is not financial or causal.

### Edge Copy

Edge profile title:

```text
Shared evidence: NVDA <-> TSM
```

Required subtext:

```text
This edge reflects shared evidence under the current filters. It does not imply a directional supplier/customer relationship.
```

## Filter Semantics

All multi-select controls use OR semantics within one control and AND semantics across controls.

### Search

Case-insensitive substring match against normalized `search_text`.

A row survives search if:

- its own `search_text` matches, or
- any linked company matches, or
- any linked source document matches

A company survives search if:

- its own `search_text` matches, or
- at least one surviving row still touches it

No advanced boolean syntax in MVP.

### Source Channel

Visible top-level control.

Rules:

- rows survive if `row.source_channel_id` is selected, unless no channels selected
- source documents survive if their `source_channel_id` is selected, unless none selected
- graph support survives only if `support.source_channel_id` is selected
- graph nodes survive if they still have surviving row/document context

### Company Role

Visible top-level control.

Rules:

- company survives if selected role matches `primary_role_id` or `secondary_role_ids`, unless no roles selected
- graph edges survive only if both endpoint companies survive
- row survives role filtering if it touches at least one surviving company
- profile counts update to filtered context

### Thesis Theme

Secondary control inside Filters.

Rules:

- row survives if `row.thesis_theme_ids` intersects selected themes, unless none selected
- company survives if its own theme IDs intersect or at least one surviving row touches it
- graph recomputed from surviving rows only
- Thesis Theme does not generate graph edges

### Timeline And Include Undated

Secondary control inside Filters.

Filter fields:

```yaml
timeline:
  from: null
  to: null
include_undated: true
```

Rules:

- inactive when `from` and `to` are null
- when active, rows/source documents with `timeline.sort_date` inside range survive
- rows/source documents with null `sort_date` survive only if `include_undated` true
- label-only rows remain fully visible when they survive filtering
- table sorting places null sort-date rows last by default

## Web UI

Layout:

```text
header
toolbar
main content:
  left main column:
    graph
    table
  right side panel:
    profile
```

Recommended dimensions:

- profile panel width: 360-420px
- graph height: 460-560px

Toolbar:

```text
Search | Source Channel | Company Role | Filters
```

Filters:

- Thesis Theme
- Timeline from
- Timeline to
- Include undated
- Clear secondary filters

Default state:

- no selected company
- no selected edge
- no active filters
- no search query
- no timeline bounds
- `include_undated = true`
- default table view: `signals`
- default graph support families: `co_position`, `shared_signal`

Profile empty state:

```text
Select a company or shared-evidence edge
```

Selection:

- company click selects company, opens company profile, highlights node, dims unrelated graph
- edge click selects edge, opens edge profile, groups support by family/channel
- empty graph click clears selection
- if filters remove selected node/edge, selection clears automatically

## Tables

Required table root:

```yaml
tables:
  default_view_id: signals
  view_order: [signals, claims, positions, proposals, sources]
  views: {...}
```

Required view shape:

```yaml
id: signals
label: Signals
entity_type: row | source_document
row_type: signal | claim | position | proposal | null
row_ids: [...]
source_document_ids: [...]
columns:
  - key: timeline
    label: Date
    sortable: true
    visible_by_default: true
default_sort:
  key: timeline.sort_date
  direction: desc
  nulls: last
```

Rules:

- row-based views include `row_type` and `row_ids`
- source view uses `row_type: null` and `source_document_ids`
- columns are config only; no duplicated entity payloads

Default columns:

Signals:

- Date
- Signal
- Companies
- Source Channel
- Thesis Themes
- Impact

Claims:

- Date/Window
- Claim
- Company
- Source Channel
- Lifecycle State

Positions:

- Filed
- Fund
- Company
- Position Type
- Value
- % Portfolio
- Change

Proposals:

- Updated
- Proposal
- Companies
- Thesis Themes
- Lifecycle State

Sources:

- Date
- Source
- Source Channel
- Kind
- Canonical Path

## Justin Reuse Policy

Copy or closely adapt:

- Inter font usage
- compact density tokens
- dark-mode-first feel
- rectangular node styling
- muted borders and edges
- web dropdown shell behavior
- one-open-filter-at-a-time behavior
- graph rectangle measurement shell
- hover/focus dimming shell
- graph block density and page discipline

Rewrite completely:

- data loading
- graph semantics
- edge support aggregation
- table row model
- profile panel content
- selection/state logic around evidence rows
- directed-deal assumptions
- Trace/pathfinding code
- mobile behavior

If Justin code/CSS is copied directly, add attribution in:

```text
canonical/site-reader/THIRD_PARTY_NOTICES.md
```

## Validation

Use two layers:

1. JSON Schema for structure.
2. Python semantic validation for cross-object rules.

Add a dedicated `signal_desk` schema entry under `canonical/site-data/schema.json`.

Hard-fail rules:

- `signal_desk.json` missing
- incomplete top-level keys
- duplicate IDs anywhere
- any company lacks valid `primary_role_id`
- any `primary_role_id` absent from `facets.company_roles`
- any role mapping uses bottleneck slug or non-role ID
- `canonical/20-data/company_roles.yaml` missing or incomplete for visible companies
- any row lacks required base field
- any row has empty `company_ids`
- any row has empty `source_document_ids`
- any row has empty `source_paths`
- non-null `primary_company_id` not in `company_ids`
- unresolved `source_document_id`
- unresolved row company ID
- unresolved source-document company ID
- graph node not resolving to a company
- graph edge company pair not resolving
- graph contains support family other than `co_position` or `shared_signal`
- graph support row ID unresolved
- support row does not touch both edge endpoint companies
- proposal row graph eligible
- claim row graph eligible
- non-null machine date fails real date validation
- Baker source-leg count != emitted Baker position rows
- Leopold source-leg count != emitted Leopold position rows
- `graph.mode != contextual_evidence`
- `quality.trace_ready != false`
- `features.trace.visible != false`

Quality counters/warnings:

- `rows_without_sort_date`
- `rows_with_label_only_timeline`
- `rows_without_source_document`
- `position_leg_counts`

`quality.ui_ready` is true only when hard-fail rules pass.

## Tests

Add deterministic fixture tests with:

- 4-6 companies
- one Baker filing with at least one multi-leg name
- one Leopold filing
- two multi-company signal rows
- one company packet yielding a claim
- one thesis proposal
- one theme covering only part of the data
- one label-only timeline row

Golden snapshots:

- `facets`
- `companies`
- `rows`
- `graph`
- `indexes`
- `tables`
- `quality`

Sort all collections by stable ID before snapshotting.

Behavior tests:

- OR within one filter, AND across filters
- search + source-channel intersection
- search + company-role intersection
- thesis-theme + search intersection
- timeline with `include_undated = true`
- timeline with `include_undated = false`
- Baker raw position fidelity
- Leopold raw position fidelity
- graph support resolution
- graph edges only from surviving filtered rows
- proposal rows visible in table/profile but absent from graph
- selection clears when filters remove selected node/edge
- table views contain IDs/configs only, not duplicated payloads

## Implementation Sequence

### Phase 1 - Data Normalization

1. Add `canonical/20-data/company_roles.yaml`.
2. Define explicit role mappings for all current visible companies.
3. Build `facets.source_channels`.
4. Build `source_documents`.
5. Ensure one authoritative source-document per canonical source file.

Acceptance:

- every row can reference at least one source document
- every visible company has explicit primary role
- wiki source page linkage is metadata, not separate source-document object

### Phase 2 - Row Generation

1. Emit position rows from Baker/Leopold YAML.
2. Emit signal rows.
3. Emit claim rows.
4. Emit proposal rows.
5. Add shared period/timeline/graph_eligibility/search_text.

Acceptance:

- Baker emits exactly 20 raw position rows
- Leopold emits exactly 25 raw position rows
- claims gain source-document IDs and source paths
- every row has base fields and timeline

### Phase 3 - Derived Collections

1. Build companies.
2. Build company role facets.
3. Build thesis theme facets.
4. Build indexes.
5. Build table views.

Acceptance:

- company counts derive from rows/source documents
- table views contain IDs plus column config only
- default table view is `signals`
- indexes resolve correctly

### Phase 4 - Graph And Quality

1. Build graph nodes.
2. Build graph edges.
3. Build quality diagnostics.

Acceptance:

- graph contains only company nodes
- graph emits only `co_position` and `shared_signal`
- graph is undirected and uses `company_ids`
- `quality.trace_ready = false`
- `quality.graph_edges_contextual_only = true`

### Phase 5 - Validation And Tests

1. Add JSON Schema additions.
2. Add Python semantic validator.
3. Add deterministic fixture.
4. Add golden snapshots.

Acceptance:

- hard-fail and quality rules implemented
- fixture tests pass
- snapshots stable
- machine-date format validation is real

### Phase 6 - Artifact Emission

1. Emit `canonical/site-data/signal_desk.json`.
2. Wire artifact into generator flow.
3. Include it in validation.

Verify:

```bash
uv run python canonical/40-engine/site_data.py --validate
python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null
```

Acceptance:

- artifact generated
- schema validation passes
- semantic validation passes
- counts and quality diagnostics present

### Phase 7 - Web Reader

Only after data gate:

1. Scaffold `canonical/site-reader/`.
2. Load only `../site-data/signal_desk.json`.
3. Implement web toolbar.
4. Implement graph.
5. Implement table.
6. Implement right profile panel.
7. Omit mobile-specific behavior.

Verify:

```bash
cd canonical/site-reader
npm install
npm run build
npm run test
```

Acceptance:

- toolbar matches MVP controls
- graph, table, profile visible together in the large-screen web layout
- filters intersect correctly
- reader does not parse canonical markdown/YAML
- Trace absent from toolbar

## Blocking Questions

No product-level blocking questions remain.

Remaining implementation choices:

- exact file/module organization under `canonical/site-reader/src/`
- whether role-map parsing lives in `site_data.py` or helper module
- how much Justin styling is copied versus reauthored from tokens

These do not block implementation.
