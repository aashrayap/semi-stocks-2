---
status: draft
feature: signal-desk-schema
---

# Top Controls Iteration

## Goal

Define the top controls for a Justin-style Signal Desk reader before finalizing the schema.

The controls should feel like Justin's site:

`Trace` `Timeline` `Cluster` + search

But semi-stocks needs three cluster lenses, so current proposed toolbar is:

`Trace` `Timeline` `Thesis Cluster` `Company Category` `Signal Cluster` + search

Control panels should be visually and behaviorally copied from Justin: compact rectangular triggers, one open dropdown at a time, independent active filter states, mobile chips/bottom sheets, dense dark-mode-first theme.

## Control State Model

Filter states are independent and composable. Opening dropdown panels is mutually exclusive, but active filters can stack.

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

## Search

### Purpose

Fast global narrowing across visible graph and table rows.

### Backing fields

- company `ticker`, `name`, `category`, `thesis_summary`
- signal `evidence`, `kind`, `direction`, source fields
- claim `claim`, `status`, `verify_at`
- position `source`, `notes`
- source/page `title`, `summary`

### UI behavior

- Same position as Justin: right side of toolbar on desktop, first full row on mobile.
- Placeholder: `Search companies, signals, claims`.
- Search narrows graph nodes and detail table.
- Search should not change selected cluster state.

### Schema needs

Add `search_text` to UI projections, not canonical records.

## Timeline

### Purpose

Time-slice evidence and claims.

### Backing dates

- source/page `created` or source event date when available
- signal `date` where present
- company `next_earnings`
- claim `verify_at` and `verify_window`
- position filing date
- prediction `predicted_at` only if agent predictions are later imported

### UI behavior

- Same as Justin: year range first.
- Later iteration can add month/quarter mode.
- Active timeline dims graph nodes/edges not active in selected range.
- Table rows filter to active range.

### Open issue

Semi-stocks has mixed date precision: exact dates, months, quarters, fiscal periods, and text labels like `FY2026-FY2027 quarterly results`. Need normalized `timeline_date` plus `timeline_label`.

## Thesis Cluster

### Purpose

Answer: "Which part of my thesis map is selected?"

This is Ash's human/canonical lens.

### Sources

- `canonical/30-thesis/thesis.yaml` cascade stages
- notebook buckets from Ash notes:
  - Energy
  - Chips
  - Infrastructure
  - Models
  - Applications
- existing bottleneck slugs:
  - `memory`
  - `n3_logic`
  - `pluggable_optics`
  - `cpo_next`
  - `euv`
  - `power`
  - `gpu_cloud`
  - `foundry`
  - `copper_signal_integrity`

### UI behavior

- Multi-select checklist like Justin's Cluster dropdown.
- Selecting a thesis cluster highlights related companies and evidence.
- Graph placement can use thesis cluster as outer grouping.
- Table rows filter to signals/claims/positions tied to selected cluster.

### Schema fields

```yaml
thesis_clusters:
  - id: thesis-cluster:n3-logic
    label: N3 logic wafers
    status: active
    period: 2025-2027
    source: canonical/30-thesis/thesis.yaml
    company_ids: [...]
    signal_ids: [...]
    claim_ids: [...]
```

## Company Category

### Purpose

Answer: "What economic role is this company playing?"

This mirrors Justin's company category cluster.

### Initial category set

Start smaller than Justin:

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

Keep open for later:

- `packaging`
- `server_oem`
- `data_center`
- `application`
- `software`
- `materials`

### UI behavior

- Multi-select checklist.
- Drives graph centroid/layout.
- Selecting `Company Category` should highlight company nodes by economic role, not by thesis bucket.
- Useful example: `power` category can contain companies in a played-out thesis cluster but still be visually present as infrastructure supply.

### Schema fields

```yaml
company_categories:
  - id: company-category:chip-designer
    label: Chip designers
    rank: 2
    company_ids: [...]
```

Rank should later feed Trace.

## Signal Cluster

### Purpose

Answer: "Which signal source or channel is selected?"

This is the provenance/channel lens. It surfaces phased data from the pipeline:
Leopold, Baker, SemiAnalysis, company earnings, thesis-stage signals, pending
proposals, and later agent signals/predictions.

The previous topic-cluster idea is still useful, but it should be subordinate
to source/channel clustering, not the top-level meaning of `Signal Cluster`.

### Sources

- fund positioning sources: Leopold, Baker
- structured supply-chain source: SemiAnalysis
- company earnings packets
- thesis-stage signals
- thesis proposal signals
- future daily agent signals
- future imported deal/source feeds

### Initial options

- `signal-cluster:leopold`
- `signal-cluster:baker`
- `signal-cluster:semianalysis`
- `signal-cluster:company-earnings`
- `signal-cluster:thesis-stage`
- `signal-cluster:pending-proposals`

Aliases should be explicit. Example: `sem`, `semi-analysis`, and `SemiAnalysis`
all resolve to `signal-cluster:semianalysis`.

### Future subordinate topic clusters

Later, each source/channel cluster can expose topic subclusters:

- Rubin capacity
- HBM pricing
- optics backlog
- CPO roadmap
- power deliverability

These should use deterministic `lexical-v0` first. Do not use embedding
clustering in the first slice; hidden clustering would make the UI hard to
trust.

### UI behavior

- Multi-select checklist.
- Selecting Leopold highlights companies with Leopold positions and shows
  aggregated Leopold context below.
- Selecting Baker highlights companies with Baker positions and shows Baker
  context.
- Selecting SemiAnalysis highlights companies mentioned in SemiAnalysis signals
  and shows those supply-chain signals below.
- Selecting multiple source clusters uses union semantics by default: companies
  with any selected source remain highlighted.
- Deselecting a source removes that source's contribution from the graph,
  table, and profile context.
- Table switches to the relevant evidence rows: positions for fund clusters,
  signals for SemiAnalysis/thesis/company clusters, proposal rows for pending
  proposals.
- Profile panel shows why the selected company belongs to each selected signal
  cluster.

### Schema fields

```yaml
signal_clusters:
  - id: signal-cluster:semianalysis
    label: SemiAnalysis
    cluster_type: source_channel
    source_kind: supply_chain_research
    aliases: [sem, semi-analysis, sa]
    company_ids: [...]
    signal_ids: [...]
    claim_ids: [...]
    position_ids: []
    source_paths:
      - canonical/20-data/sources/semianalysis/signals.yaml
      - canonical/10-wiki/sources/semianalysis-signals.md
    summary: SemiAnalysis supply-chain signals mapped to companies and thesis clusters.
```

## Trace

### Purpose

Answer: "How does this company connect to that company through the value chain?"

Trace should stay off until category ranks and graph edge projection are good. Justin's Trace is clean because it enforces downstream value-chain movement.

### Proposed rank

```yaml
0: equipment
1: foundry | memory | packaging | materials
2: chip_designer
3: server_oem | networking | optics | power
4: gpu_cloud | data_center | hyperscaler
5: ai_lab | application
```

### Edge eligibility

Initial trace edges should not include every `edges.json` relationship. Use only graph-projection edges that make value-chain sense:

- supplier/customer when encoded
- company uses supplier output
- company depends on same bottleneck with direction
- position/read-through only if explicitly marked as thesis relation

### UI behavior to copy from Justin

- From dropdown.
- To dropdown.
- Hop-count chips.
- Path grouping by category shape.
- Selected path highlights graph and filters table.
- Swap button when reverse path may exist.

### Open issue

Current semi-stocks evidence graph is not yet a supplier-customer deal graph. Trace could be misleading if enabled too early.

## Graph And Table Composition

All controls should affect graph and table consistently:

| Control | Graph effect | Table effect |
|---|---|---|
| Search | hide/dim nonmatches | filter rows |
| Timeline | highlight active date window | filter rows by date |
| Thesis Cluster | highlight companies/evidence in thesis bucket | filter rows by category |
| Company Category | highlight companies by role | filter rows tied to companies |
| Signal Cluster | highlight companies/evidence from selected source channels | switch/filter to positions, signals, proposals |
| Trace | highlight selected path | filter rows to path evidence |

## Current Recommendation

Use all five controls explicitly in the first schema, but ship them in phases:

1. `Search`
2. `Timeline`
3. `Thesis Cluster`
4. `Company Category`
5. `Signal Cluster`
6. `Trace`

If the toolbar feels too wide, collapse the three cluster controls into one `Cluster` dropdown with tabs:

- `Thesis`
- `Company`
- `Signals`

Do not collapse them in the schema. They are different dimensions.

## Questions Before Final Spec

- Should the visible toolbar use three separate cluster dropdowns, or one `Cluster` dropdown with internal tabs?
- Should notebook buckets (`Energy`, `Chips`, `Infrastructure`, `Models`, `Applications`) sit above thesis stages or be a parallel lens?
- Should `Company Category` use Justin-like role names, or semi-stocks-specific names like `optics`, `gpu_cloud`, `power_landlord`?
- Should first `Signal Cluster` be deterministic lexical only, or is hidden embedding clustering acceptable later?
