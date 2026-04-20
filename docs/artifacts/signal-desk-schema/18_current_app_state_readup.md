---
status: current-state-readup
feature: signal-desk-schema
updated: 2026-04-20
---

# Signal Desk Current State Readup

## Short Version

Signal Desk now has a working generated data contract and an initial web-only reader.

Open the app locally:

```text
http://127.0.0.1:5173/
```

The app is not a polished product yet. It is a validated first pass that proves the key architecture:

```text
canonical source data -> canonical/site-data/signal_desk.json -> web reader
```

The reader consumes only:

```text
canonical/site-data/signal_desk.json
```

It does not parse canonical markdown or YAML directly.

## Current Data State

Generated artifact:

```text
canonical/site-data/signal_desk.json
```

Current artifact version:

```text
signal-desk-v0.2
```

Last generated:

```text
2026-04-20T12:33:10Z
```

Current counts:

| Collection | Count |
|---|---:|
| Source documents | 14 |
| Companies | 40 |
| Rows | 152 |
| Graph nodes | 40 |
| Graph edges | 418 |

Rows by type:

| Row type | Count | Meaning |
|---|---:|---|
| `position` | 45 | Raw Baker / Leopold 13F position legs |
| `signal` | 61 | Company, SemiAnalysis, and thesis-stage evidence observations |
| `claim` | 43 | Forward-looking proof gates / claims |
| `proposal` | 3 | Thesis proposals, shown as evidence context but not graph edges |

Source channels:

| Source channel | Companies | Rows | Source docs |
|---|---:|---:|---:|
| Baker | 16 | 20 | 1 |
| Leopold | 25 | 25 | 1 |
| SemiAnalysis | 8 | 6 | 1 |
| Company earnings | 7 | 68 | 7 |
| Thesis stage | 12 | 30 | 1 |
| Pending proposals | 6 | 3 | 3 |

Quality checks:

| Check | State |
|---|---|
| UI-ready flag | `true` |
| Trace-ready flag | `false` |
| Rows without source document | `0` |
| Baker raw positions | `20 source / 20 emitted` |
| Leopold raw positions | `25 source / 25 emitted` |
| Label-only timeline rows | `98` |
| Rows without sortable date | `98` |

The high number of label-only rows is expected right now. Many thesis-stage signals and proof gates use fiscal or text windows rather than exact dates.

## Current Surface State

Implemented web reader:

```text
canonical/site-reader/
```

Current app shape:

- web-only large-screen layout
- header
- toolbar
- stats strip
- contextual graph
- graph legend and support controls
- tabbed evidence table
- right-side profile panel

Toolbar controls:

- Search
- Source Channel
- Company Role
- Filters

Filters contains:

- Thesis Theme
- Timeline from / to
- Include undated

Table views:

- Signals
- Claims
- Positions
- Proposals
- Sources

Profile panel:

- empty state when nothing is selected
- company profile when a company node is clicked
- edge profile when a graph edge is clicked
- edge profile explains that the edge is shared evidence, not a supplier/customer relationship
- company evidence grouped by source channel and row type
- edge support grouped by support family and source channel

## What The Graph Means

The graph is a contextual evidence graph.

It means:

```text
these companies share evidence under the current filters
```

It does not mean:

```text
supplier/customer relationship
money flow
chip flow
ownership flow
value-chain path
```

Current graph support families:

| Family | Meaning |
|---|---|
| `co_position` | two companies appear in the same Baker or Leopold filing |
| `shared_signal` | two companies appear in the same graph-eligible multi-company signal |

Not emitted in MVP:

- `shared_thesis`
- `explicit_relationship`
- Trace/pathfinding relationships

Trace is intentionally absent from the toolbar.

Current graph controls:

- support-family toggles for `co_position` and `shared_signal`
- minimum edge-weight threshold
- top-edge limit

These controls reduce clutter without changing the underlying contract semantics.

## Current Role Model

Company roles live in:

```text
canonical/20-data/company_roles.yaml
```

This file is explicit mapping data for the web reader. It is deliberately separate from thesis bottlenecks.

Core roles include:

- Equipment
- Foundry
- Memory
- Packaging
- Chip designers
- Networking
- Optics
- Server OEMs
- Power infrastructure
- GPU cloud
- Hyperscalers
- AI labs

Two source-fidelity roles were added during implementation:

- Software services
- Market basket

Reason: the raw 13F filings include non-core exposures such as INFY and QQQ. Those rows are preserved exactly rather than silently dropped or mislabeled.

## What Is Validated

Validation currently checks:

- `signal_desk.json` exists and has expected top-level shape
- Trace is parked and hidden
- graph mode is `contextual_evidence`
- graph support families are only `co_position` and `shared_signal`
- every source document / company / row has stable IDs
- row references resolve to source documents and companies
- graph endpoints resolve to companies
- graph support rows resolve
- Baker emits 20 raw position rows
- Leopold emits 25 raw position rows
- claims and proposals are not graph-eligible

Contract tests:

```text
canonical/40-engine/tests/test_signal_desk_contract.py
```

Web filter tests:

```text
canonical/site-reader/src/logic.test.js
```

## Commands That Currently Pass

Data generation and validation:

```bash
uv run python canonical/40-engine/site_data.py --validate
```

Signal Desk contract tests:

```bash
uv run python canonical/40-engine/tests/test_signal_desk_contract.py
```

Web reader tests:

```bash
cd canonical/site-reader
npm test
```

Web reader build:

```bash
cd canonical/site-reader
npm run build
```

Local dev server:

```bash
cd canonical/site-reader
npm run dev -- --port 5173
```

Current local URL:

```text
http://127.0.0.1:5173/
```

## What Is Still Rough

The current app is useful for inspecting the contract and has received a first
polish pass after Research Pro review. It is still not final product UI.

Known rough areas:

- graph is still dense because co-position edges create many pairs
- graph layout is deterministic but simple
- table columns are improved but still not final
- profile panel now groups evidence but could still use stronger narrative copy
- source-document view is basic
- no production deploy path exists yet
- no mobile behavior is planned for MVP

Browser screenshot QA now exists for:

- default state
- Baker source-channel edge selection
- empty timeline-filtered state

Screenshot artifacts:

- `docs/artifacts/signal-desk-schema/browser-qa/default.png`
- `docs/artifacts/signal-desk-schema/browser-qa/baker-edge.png`
- `docs/artifacts/signal-desk-schema/browser-qa/empty-state.png`

The main product risk now is graph readability, not data correctness.

## Next Work

Recommended next pass:

1. Review screenshot artifacts and tune spacing/copy.
2. Improve graph layout beyond deterministic role columns.
3. Add stronger narrative copy for company and edge profiles.
4. Add more table-specific formatting and sorting controls.
5. Decide whether edge clutter needs a better default threshold.

Do not start Trace until a separate typed `relationship_edges` dataset exists.

## Important Files

Data contract:

```text
canonical/site-data/signal_desk.json
```

Generator:

```text
canonical/40-engine/engine/site_data.py
```

Role mapping:

```text
canonical/20-data/company_roles.yaml
```

Web reader:

```text
canonical/site-reader/
```

Current final spec:

```text
docs/artifacts/signal-desk-schema/17_final_mvp_spec.md
```

Current task plan:

```text
docs/artifacts/signal-desk-schema/05_tasks.md
```
