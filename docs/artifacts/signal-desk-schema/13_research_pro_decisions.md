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
