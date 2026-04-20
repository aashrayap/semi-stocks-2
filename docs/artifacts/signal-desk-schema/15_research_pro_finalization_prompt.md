---
status: research-pro-finalization-request
feature: signal-desk-schema
updated: 2026-04-19
---

# Research Pro Finalization Prompt

## Copy-Paste Opener

Continuing from the prior Signal Desk brief and your readiness review in this same chat: please revise and finalize the actual implementable MVP spec. New constraint: mobile is out of scope for the MVP. Treat this as a web-only Signal Desk, similar to Justin's web app, optimized for a large-screen browser viewport. Use the accepted v0.2 direction below, challenge any remaining ambiguity, and return a final spec that Codex can implement without further product interpretation.

## What Changed Since The Prior Brief

The previous Research Pro review was accepted in substance. It changed the implementation target from the older "Signal Cluster / Company Category" spec to a v0.2 data-contract-first spec.

Accepted v0.2 decisions:

- `Signal Cluster` is now `Source Channel`.
- `Company Category` is now `Company Role`.
- `source_documents` are first-class.
- evidence uses one unified `rows` collection with row variants:
  - `position`
  - `signal`
  - `claim`
  - `proposal`
- table views should contain row IDs and column config, not duplicated row payloads.
- graph mode is `contextual_evidence`.
- first graph is undirected, company-node-only, no arrows, no supplier/customer implication.
- Trace remains parked until a separate typed `relationship_edges` dataset exists.
- pending proposals can appear in table/profile but do not create graph edges.
- Timeline ships in the data contract, but not as a top-level toolbar control in MVP.

New decision for this follow-up:

- **Mobile is not required for this MVP.**
- Do not spend implementation scope on mobile bottom sheets, mobile toolbar behavior, or mobile-specific layout.
- The web MVP may still be reasonably responsive to avoid broken layout, but success criteria should target a large-screen browser viewport.

## Current Implementation Target

The implementation target currently lives in:

```text
docs/artifacts/signal-desk-schema/14_final_spec_v0_2.md
```

The task plan currently lives in:

```text
docs/artifacts/signal-desk-schema/05_tasks.md
```

The prior Research Pro decisions are captured in:

```text
docs/artifacts/signal-desk-schema/13_research_pro_decisions.md
```

Please revise/finalize those conceptually. You do not need to preserve document filenames; return a final spec structure and implementation plan.

## Web MVP Scope

The MVP should be web-only, similar to Justin's web app.

Target viewport:

```text
large-screen browser viewport, roughly 1280px+ wide
```

MVP UI shape:

```text
Header / title
Search
Source Channel filter
Company Role filter
Filters popover or side control for Thesis Theme and Timeline
Contextual company graph
Evidence table
Profile panel
```

Out of scope for MVP:

- mobile bottom sheets
- mobile chip rows
- mobile-first layout logic
- `MobileFilterSheet.jsx` adaptation
- enabled Trace
- relationship pathfinding
- inferred supplier/customer edges
- proposal-generated graph edges
- topic clustering
- agent prediction import
- full wiki reader
- human review workflow

Web UX expectation:

- graph and table should both be usable without route switching
- profile panel should be the truth surface for selected company/edge context
- filters should be explicit and inspectable
- Source Channel and Company Role should be first-class visible controls
- Thesis Theme and Timeline can be grouped in secondary Filters
- Trace should be absent or visibly parked, not a normal disabled filter that implies readiness

## Data Contract To Finalize

The proposed top-level contract is:

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
  trace_blockers: [...]
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
    signals: { row_ids: [...], columns: [...] }
    claims: { row_ids: [...], columns: [...] }
    positions: { row_ids: [...], columns: [...] }
    proposals: { row_ids: [...], columns: [...] }
    sources: { source_document_ids: [...], columns: [...] }
```

Please finalize:

1. exact required top-level keys
2. exact row base fields
3. exact row variant fields
4. exact source-document fields
5. exact company fields
6. exact graph node/edge fields
7. exact index fields
8. exact table-view fields
9. which fields are mandatory vs optional
10. which fields can be nullable

## Current Known Data Constraints

Current generated `site-data` state:

```yaml
companies: 40
signals: 67
claims: 43
edges: 678
entities: 93
pages: 34
thesis_stages: 7
```

Signals:

```yaml
company_thesis_signal: 25
semianalysis_signal: 6
thesis_stage_signal: 33
thesis_proposal_signal: 3
with_date: 9
with_source: 9
with_source_page: 25
with_source_path: 67
```

Claims:

```yaml
total: 43
with_source_page: 43
with_source_path: 0
with_parseable_verify_date: 0
```

Positions:

```yaml
Baker source YAML positions: 20
Baker generated company position rows today: 16
Leopold source YAML positions: 25
Leopold generated company position rows today: 25
```

Graph:

```yaml
current graph.json nodes: 127
current graph.json links: 398
current graph is broad knowledge/provenance graph, not a Signal Desk graph
```

Important data-gate requirement:

- Baker and Leopold raw position leg counts must match source YAML exactly in the new `rows` output.
- Claims need normalized source trace, not only `source_page`.
- Timeline quality must be reported because many rows are label-only or partially dated.

## Company Role Question Still Needs Final Lock

Proposed first primary roles:

```text
equipment
foundry
memory
packaging
chip_designer
networking
optics
server_oem
power_infrastructure
gpu_cloud
hyperscaler
ai_lab
```

Accepted notes:

- `optics` stays separate from generic networking.
- `gpu_cloud` stays separate from hyperscaler.
- `neocloud` is a displayed alias or secondary role/tag, not first primary role.
- `data_center` is secondary unless pure colocation/landlord data warrants primary role.
- `investor` is not a company role in MVP.

Please finalize whether this role set is the right MVP set, and give the exact mapping policy:

- where explicit mapping should live
- fallback order
- whether unknown companies are allowed
- whether secondary roles/tags are required in MVP
- how to prevent bottleneck slugs leaking into company role IDs

## Graph Question Still Needs Final Lock

Current proposed graph:

```yaml
graph:
  mode: contextual_evidence
  nodes:
    - id: company:NVDA
      company_id: company:NVDA
      primary_role_id: company-role:chip-designer
  edges:
    - id: edge:company:NVDA:company:TSM
      source: company:NVDA
      target: company:TSM
      directed: false
      trace_eligible: false
      support:
        - family: co_position
          source_channel_id: source-channel:baker
          score: 0.72
          row_ids: [...]
      visual_weight: 1.72
      semantic_label: shared_evidence
```

Allowed support families:

```text
co_position
shared_signal
shared_thesis
explicit_relationship
```

Please finalize:

- exact support-family semantics
- whether `explicit_relationship` should be excluded entirely until typed relationship data exists
- edge ID format
- whether edge endpoints should use `source`/`target` despite undirected semantics, or `company_ids: [a, b]`
- weight formula for each family
- whether graph should initially include `shared_thesis` or only source-backed evidence families
- what edge copy should say in the profile panel so it does not imply supplier/customer relationship

## Timeline Question Still Needs Final Lock

Timeline is in the data contract, but not a top-level MVP toolbar control.

Please finalize:

- whether Timeline appears inside secondary Filters in MVP
- exact `period` object schema
- exact `timeline` object schema
- how `include_undated` should behave
- how label-only rows appear in table/profile
- whether fiscal quarters and calendar quarters need different object fields

## Web UI To Finalize

MVP web controls:

```text
Search | Source Channel | Company Role | Filters
```

Filters contains:

```text
Thesis Theme
Timeline
include undated
```

MVP layout:

```text
top header
toolbar
large graph block
evidence table below or beside graph
profile panel on right
```

Please finalize:

- graph/table/profile layout
- whether table is below graph or split-pane beside graph
- whether profile panel is fixed right drawer or inline right panel
- default selected state
- default table view
- default graph edge families enabled
- how Source Channel filter affects graph/table/profile
- how Company Role filter affects graph/table/profile
- how Thesis Theme filter affects graph/table/profile
- how Search intersects with filters
- what is copied/adapted from Justin vs rewritten

Remember: mobile is not required for this MVP.

## Validation And Tests To Finalize

Current required validator ideas:

- every company has valid `primary_role_id`
- every row has `row_type`, `search_text`, `source_channel_id`, `source_document_ids`, and `timeline`
- every `source_document_id` resolves
- every row company ID resolves
- every graph node resolves to a company
- every graph edge support row ID resolves
- proposals are not graph-eligible
- Baker/Leopold raw position counts match source YAML
- no `company_role_id` contains a bottleneck value
- every row has a timeline object
- machine dates pass real format validation
- `graph.mode == contextual_evidence`
- `quality.trace_ready == false`

Please finalize:

- required validator rules
- fixture test cases
- any snapshot/golden fixture strategy
- where validation should fail hard vs warn through `quality`
- whether JSON Schema should be generated and how much should be enforced in Python

## Implementation Order To Finalize

Current proposed order:

1. Normalize source documents.
2. Promote raw fund positions directly from YAML.
3. Normalize row base and row variants.
4. Define company roles and thesis themes.
5. Build source channels.
6. Generate company summaries.
7. Generate graph support arrays.
8. Write validators and fixture tests.
9. Emit `signal_desk.json`.
10. Scaffold web reader.

Please revise this if needed and return exact implementation phases with acceptance criteria and verify commands.

## Requested Output From Research Pro

Return a final implementable spec with these sections:

1. Architecture verdict.
2. Final MVP scope.
3. Final non-goals and parked features.
4. Final `signal_desk.json` schema.
5. Final row model.
6. Final source-document model.
7. Final company-role and thesis-theme model.
8. Final graph model.
9. Final web UI model.
10. Final filter semantics.
11. Final validation/test checklist.
12. Final implementation sequence.
13. Open questions only if truly blocking.

Important: optimize for implementation. Do not give high-level advice only. Return field names, shapes, default behavior, cut lines, and pass/fail gates.
## Embedded Local Reference Documents

The sections below inline the local documents referenced above so Research Pro can read this as a single self-contained prompt without filesystem access.

Important: these embedded documents preserve prior planning history, including some mobile-related recommendations. The current instruction supersedes those lines: mobile is out of scope for the MVP, and Research Pro should revise the final spec/task plan accordingly.

## Appendix A - Full Current Final Spec v0.2

Source path in repo: `docs/artifacts/signal-desk-schema/14_final_spec_v0_2.md`

---
status: final-spec-v0.2
feature: signal-desk-schema
updated: 2026-04-19
supersedes: 09_final_spec.md
---

# Final Spec v0.2: Signal Desk

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

## Appendix B - Accepted Research Pro Decisions

Source path in repo: `docs/artifacts/signal-desk-schema/13_research_pro_decisions.md`

---
status: accepted
feature: signal-desk-schema
updated: 2026-04-19
---

# Research Pro Decisions

## Verdict

Research Pro confirmed the main direction but changed the lock:

- keep generated contract first, UI second
- do not start reader scaffolding yet
- treat first graph as contextual evidence, not value-chain relationship graph
- park Trace harder: do not let a disabled control imply the data can support it
- rename the key user-facing schema terms before implementation

## Accepted Changes

### 1. Rename `Signal Cluster` to `Source Channel`

Accepted.

Reason: Baker, Leopold, SemiAnalysis, company earnings, thesis-stage control, and pending proposals are source/evidence channels. They are not all signal clusters.

Implementation implication:

- contract term: `source_channels`
- filter state: `source_channel_ids`
- UI label: `Source Channel`
- old `signal_clusters` name is allowed only as historical artifact language

### 2. Rename `Company Category` to `Company Role`

Accepted.

Reason: the intended lens is economic role / value-chain role, not arbitrary category and not thesis bottleneck.

Implementation implication:

- contract term: `company_roles`
- row field: `primary_role_id`
- optional field: `secondary_role_ids`
- old `company_category` name is superseded

### 3. Add first-class `source_documents`

Accepted.

Reason: provenance should not be a flat set of string paths. Rows need normalized source-document IDs for UI joins and raw paths for repo trace/debug.

Implementation implication:

- add top-level `source_documents`
- every row has `source_document_ids`
- keep `source_paths` as trace/debug fields

### 4. Collapse evidence into a unified `rows` collection

Accepted.

Reason: separate duplicated `signals`, `claims`, `positions`, `tables.*` payloads create drift. The first slice should use one row collection plus indexes/table views.

Implementation implication:

- top-level `rows`
- row variants: `position`, `signal`, `claim`, `proposal`
- `tables.views.*` contain `row_ids` and column config, not duplicated rows

### 5. Split `features`, `defaults`, and `quality`

Accepted.

Reason: `trace.enabled: false` mixes capability state and filter state. The payload should self-report readiness and blockers.

Implementation implication:

- `features.trace.status: parked`
- `quality.trace_ready: false`
- `quality.trace_blockers: [...]`

### 6. Add structured period and stronger timeline

Accepted.

Reason: fund period end, filing date, fiscal quarter, verify window, and proposal update are different facts.

Implementation implication:

- row-level `period`
- row-level `timeline.sort_date`
- row-level `timeline.end_date`
- row-level `timeline.include_in_range`
- nullable sort dates allowed

### 7. Make graph contextual and undirected

Accepted.

Reason: current semi-stocks edges are not directed deal/value-chain relationships.

Implementation implication:

- `graph.mode: contextual_evidence`
- graph edges are undirected
- edge `support[]` carries evidence families and row IDs
- no arrows
- no supplier/customer implication
- no Trace pathfinding

### 8. Tighten first company-role taxonomy

Accepted with one open detail: exact role mapping should be encoded in generator data/constant and validated.

First primary roles:

- `equipment`
- `foundry`
- `memory`
- `packaging`
- `chip_designer`
- `networking`
- `optics`
- `server_oem`
- `power_infrastructure`
- `gpu_cloud`
- `hyperscaler`
- `ai_lab`

Notes:

- `optics` stays separate from generic networking.
- `gpu_cloud` stays separate from hyperscaler.
- `neocloud` becomes a displayed alias or secondary role/tag, not a first primary role.
- `data_center` is secondary until pure colocation/landlord data warrants primary role.
- `investor` is not a company role in first slice; Baker/Leopold are source channels.

### 9. Reduce first UI control load

Accepted.

Desktop target:

- Search
- Source Channel
- Company Role
- Filters popover: Thesis Theme + Timeline
- Trace hidden or parked, not normal active control

Mobile target:

- Search full width
- one Filters button
- bottom sheet sections for Source Channel, Company Role, Thesis Theme, Timeline
- no visible Trace control

## Rejected Or Deferred

### Keep `signal_desk.json` split into multiple files

Rejected for first slice.

Reason: corpus is small enough for one bundle; multi-file loading adds avoidable contract complexity.

### Top-level Timeline toolbar

Deferred.

Timeline should ship in the data contract now. It should not be a first top-level UI power control until date quality is proven.

### Pending proposals in graph

Rejected for first slice.

Proposals may appear in table/profile. They must not create graph edges until accepted or explicitly promoted.

### Any inferred supplier/customer edges from prose

Rejected.

Only typed canonical relationships can become `explicit_relationship`.

## New Contract Direction

The implementation target is now [14_final_spec_v0_2.md](14_final_spec_v0_2.md).

Old final spec [09_final_spec.md](09_final_spec.md) remains useful history but is superseded for implementation.

## Appendix C - Current Implementation Task Plan

Source path in repo: `docs/artifacts/signal-desk-schema/05_tasks.md`

---
status: locked-after-research-pro
feature: signal-desk-schema
updated: 2026-04-19
---

# Tasks: Signal Desk Schema

Implementation remains unstarted. This task list is now locked by
[13_research_pro_decisions.md](13_research_pro_decisions.md) and
[14_final_spec_v0_2.md](14_final_spec_v0_2.md).

## SD-V2-1 - Normalize source documents

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add top-level `source_documents`.
- Build source documents for:
  - Baker 13F
  - Leopold 13F
  - SemiAnalysis signals
  - company packets
  - thesis control
  - thesis proposals
  - linked wiki source pages when available
- Acceptance:
  - every evidence row can point to at least one `source_document_id`
  - source documents preserve `canonical_path`, optional `wiki_page_slug`, source date, period, and search text
- Verify: source-document IDs are unique and all row references resolve.
- Estimate: 2-4h.

## SD-V2-2 - Promote raw fund positions to row variants

- Modify: `canonical/40-engine/engine/site_data.py`.
- Read directly from:
  - `canonical/20-data/sources/leopold/q4_2025.yaml`
  - `canonical/20-data/sources/baker/q4_2025.yaml`
- Emit one `row_type: position` per source filing leg.
- Acceptance:
  - Baker emits 20 raw position rows
  - Leopold emits 25 raw position rows
  - multi-leg tickers preserve leg detail
  - no collapse unless a separate summary row uses `collapsed_from_ids`
- Verify: validator compares generated counts to source YAML counts.
- Estimate: 2-3h.

## SD-V2-3 - Normalize unified row base and variants

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add top-level `rows`.
- Row types:
  - `position`
  - `signal`
  - `claim`
  - `proposal`
- Add base row fields:
  - `id`
  - `row_type`
  - `title`
  - `summary`
  - `company_ids`
  - `primary_company_id`
  - `source_channel_id`
  - `source_document_ids`
  - `source_paths`
  - `thesis_theme_ids`
  - `search_text`
  - `period`
  - `timeline`
  - `graph_eligibility`
  - `lifecycle_state`
  - `ui_badges`
- Acceptance:
  - old duplicated top-level `signals`, `claims`, and `positions` are not duplicated inside tables
  - table views reference row IDs
- Estimate: 4-6h.

## SD-V2-4 - Add timeline and search projections

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add helpers:
  - `_timeline_for_row(row) -> dict`
  - `_search_text(*values) -> str`
- Timeline fields:
  - `sort_date`
  - `end_date`
  - `precision`
  - `label`
  - `kind`
  - `include_in_range`
- Acceptance:
  - every row has `search_text`
  - every row has a display-safe `timeline`
  - null sort dates are allowed but counted under `quality`
- Boundary: Timeline ships in data contract but not as first top-level toolbar control.
- Estimate: 1.5-3h.

## SD-V2-5 - Define company roles and thesis themes

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add helpers:
  - `_build_thesis_themes(...)`
  - `_build_company_roles(...)`
  - `_company_role_for(company_or_ticker) -> str`
- Acceptance:
  - thesis themes remain separate from company roles
  - no `company_role_id` contains a bottleneck value
  - `optics` and `gpu_cloud` are first-slice roles
  - `neocloud` is secondary label/tag, not first primary role
- Boundary: role mapping must be explicit and tested.
- Estimate: 2-3h.

## SD-V2-6 - Build source channels

- Modify: `canonical/40-engine/engine/site_data.py`.
- Build top-level `facets.source_channels`.
- Required channels:
  - `source-channel:leopold`
  - `source-channel:baker`
  - `source-channel:semianalysis`
  - `source-channel:company-earnings`
  - `source-channel:thesis-stage`
  - `source-channel:pending-proposals`
- Acceptance:
  - rows reference source channels
  - source documents reference source channels
  - old `Signal Cluster` language is not used in new contract fields
- Estimate: 1-2h.

## SD-V2-7 - Generate company summaries and indexes

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add:
  - `companies`
  - `indexes.row_ids_by_type`
  - `indexes.row_ids_by_company`
  - `indexes.row_ids_by_source_channel`
  - `indexes.company_ids_by_thesis_theme`
- Acceptance:
  - company summaries derive counts from rows
  - indexes do not duplicate row payloads
- Estimate: 2-3h.

## SD-V2-8 - Build contextual evidence graph

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add helper: `_build_signal_desk_graph(...)`.
- Graph mode: `contextual_evidence`.
- First-slice graph nodes: company nodes only.
- Edges:
  - undirected
  - no arrows
  - support arrays with `family`, `source_channel_id`, `score`, and `row_ids`
- Allowed support families:
  - `co_position`
  - `shared_signal`
  - `shared_thesis`
  - `explicit_relationship`
- Acceptance:
  - do not dump current `edges.json`
  - pending proposals are never graph-eligible
  - edge support row IDs resolve and touch both companies or are explicitly allowed by support family
- Estimate: 2-4h.

## SD-V2-9 - Add quality/readiness diagnostics

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add top-level `quality`.
- Required fields:
  - `ui_ready`
  - `trace_ready`
  - `rows_without_source_document`
  - `rows_without_sort_date`
  - `rows_with_label_only_timeline`
  - `graph_edges_contextual_only`
  - `trace_blockers`
- Acceptance:
  - `trace_ready` is false
  - `graph_edges_contextual_only` is true
  - quality counters match generated data
- Estimate: 1-2h.

## SD-V2-10 - Extend schema and validation

- Modify: `canonical/40-engine/engine/site_data.py`.
- Modify generated: `canonical/site-data/schema.json`.
- Validator checks:
  - `signal_desk` exists
  - every company has valid `primary_role_id`
  - row IDs unique
  - every row has `row_type`, `search_text`, `source_channel_id`, `source_document_ids`, `timeline`
  - all source documents resolve
  - all row company IDs resolve
  - graph nodes resolve to companies
  - graph edge support row IDs resolve
  - proposals are not graph-eligible
  - Baker/Leopold raw position counts match source YAML
  - all machine dates pass real format validation
  - `graph.mode == contextual_evidence`
  - `quality.trace_ready == false`
- Boundary: if using Python `jsonschema`, enable format checking explicitly.
- Estimate: 2-4h.

## SD-V2-11 - Add fixture tests

- Create/update tests in the repo's existing test location if one exists; otherwise add focused tests near the generator.
- Must cover:
  - OR within one control, AND across controls
  - search intersection
  - `include_undated: true` default
  - source channel toggles update row sets and graph support
  - Baker position-leg fidelity
  - graph support row resolution
  - pending proposals table/profile only, no graph edges
  - desktop/mobile filter state parity at data-logic level
- Estimate: 2-4h.

## SD-V2-12 - Emit `signal_desk.json`

- Modify: `canonical/40-engine/engine/site_data.py`.
- Modify if output text changes: `canonical/40-engine/site_data.py`.
- Create generated: `canonical/site-data/signal_desk.json`.
- Add artifact to write list, manifest, and validation.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`
  - `python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null`
- Acceptance: data gate passes before UI work starts.
- Estimate: 1-2h after prior tasks.

## SD-V2-13 - Scaffold Justin-style reader only after data gate

- Create after SD-V2-1 through SD-V2-12 pass:
  - `canonical/site-reader/package.json`
  - `canonical/site-reader/index.html`
  - `canonical/site-reader/src/**`
  - `canonical/site-reader/THIRD_PARTY_NOTICES.md`
- Copy/adapt Justin visual system with attribution.
- Boundary: no UI reads from canonical markdown/YAML; only `canonical/site-data/signal_desk.json`.
- Initial desktop controls:
  - Search
  - Source Channel
  - Company Role
  - Filters popover for Thesis Theme and Timeline
- Initial mobile controls:
  - Search
  - Filters bottom sheet
- Trace omitted on mobile and hidden/parked on desktop.
- Verify:
  - `cd canonical/site-reader && npm install`
  - `npm run build`
  - `npm run test`
- Estimate: 6-10h after data gate.

## SD-V2-14 - Keep Trace parked

- Do not implement enabled Trace in first reader slice.
- Acceptance:
  - no pathfinding over raw evidence/provenance edges
  - no user-facing control implies Trace is available
  - unpark only after a separate `relationship_edges` dataset exists
- Estimate if later approved: 3-5h.
