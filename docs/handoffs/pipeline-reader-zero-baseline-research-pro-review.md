# Pipeline -> Reader Zero-Baseline: Research Pro Review Brief

## Reviewer Context

You are reviewing architecture and workflow direction for `semi-stocks-2` after a full data reset.  
Assume remote repo access plus this packet. This packet is designed to be self-contained if remote file access is limited.

## Review Target And Mode

- Mode: architecture/design critique + migration/risk review
- Remote target: commit `8e60e8815f7191f41e97d530f44e8c4045b706ef` and PR [#7](https://github.com/aashrayap/semi-stocks-2/pull/7)
- Base/comparison: `main` (`7888b5736ff98460babe63608955d1d7ecf62832`)
- Requested scrutiny: first entry starting point and path to success from a zero-data baseline while preserving existing architecture

## Access Protocol

1. Confirm repo access for `aashrayap/semi-stocks-2`.
2. Use this packet's `Inline Evidence` as minimum truth.
3. If repo access is available, use `Primary Raw URLs` (commit-pinned) as primary evidence.
4. Treat PR/branch views as context only.
5. If any primary raw URL fails, cite the exact URL and stop (do not continue from potentially stale state).

## Source And Access Policy

- Primary evidence: repository files at commit `8e60e8815f7191f41e97d530f44e8c4045b706ef` and this packet
- Web/external sources: not needed
- Non-repo/local context: included in this packet under `Non-Repo Context Included`
- Sensitive context check: no secrets/private tokens included

## Primary Raw URLs

- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/README.md>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/docs/architecture.md>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/10-wiki/schema.md>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/40-engine/engine/site_data.py>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/site-reader/src/App.jsx>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/site-reader/src/logic.js>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/site-reader/tests/signal-desk.spec.js>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/30-thesis/thesis.yaml>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/20-data/sources/baker/q4_0000.yaml>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/20-data/sources/semianalysis/signals.yaml>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/site-data/signal_desk.json>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/canonical/site-data/build.json>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/config.yaml>
- <https://raw.githubusercontent.com/aashrayap/semi-stocks-2/8e60e8815f7191f41e97d530f44e8c4045b706ef/agents/config.yaml>

## Goal

- Define the strongest first-entry workflow from raw ingest to reader decisioning after data reset.
- Keep architecture and ownership model intact.
- Produce a practical path to repopulate data and regain a meaningful Signal Desk surface.

## General Direction

1. Preserve canonical propagation architecture (`10-wiki -> 20-data -> 30-thesis -> 40-engine -> site-data -> site-reader`).
2. Start from zero data and reintroduce evidence in one strict path (no side channels).
3. Resolve the "zero baseline vs. non-empty graph" testing contract explicitly.

## Files To Review

Primary starting points (not hard boundaries):

- `README.md`
- `docs/architecture.md`
- `canonical/10-wiki/schema.md`
- `canonical/40-engine/engine/site_data.py`
- `canonical/site-reader/src/App.jsx`
- `canonical/site-reader/src/logic.js`
- `canonical/site-reader/tests/signal-desk.spec.js`
- `canonical/30-thesis/thesis.yaml`
- `canonical/20-data/sources/baker/q4_0000.yaml`
- `canonical/20-data/sources/semianalysis/signals.yaml`
- `canonical/site-data/signal_desk.json`
- `canonical/site-data/build.json`
- `config.yaml`
- `agents/config.yaml`

## Inline Evidence

`README.md` lines `9-16`, `45-49`, `85-87`

```text
Defines active path as canonical truth -> 40-engine -> site-data -> site-reader.
States site-data is generated and site-reader is not source of truth.
States graph edges are contextual evidence only and Trace is parked.
```

Explanation: establishes intended top-level flow and semantic contract for graph interpretation.

`docs/architecture.md` lines `7-9`, `22-24`, `73-79`, `83-89`

```text
Explicit canonical propagation chain is documented.
site-data and site-reader are marked "not canonical stage".
Principles require manual research -> structured evidence -> narrow thesis -> engine/report separation.
```

Explanation: confirms ownership boundaries and that architecture must remain unchanged.

`canonical/10-wiki/schema.md` lines `24-26`, `33-35`, `66-72`, `156-159`

```text
Three-layer model: raw immutable, wiki compiled, schema governance.
Wiki links to thesis/data lanes.
Query traversal documents wiki -> data -> thesis path.
Workflow requires index rebuild + log append after wiki updates.
```

Explanation: defines first-entry ingestion discipline and wiki lifecycle rules.

`canonical/40-engine/engine/site_data.py` lines `51-56`, `58-73`, `136-150`, `172-185`, `247-252`

```text
build_site_data always rewrites canonical/site-data.
validate_site_data expects several collections to be non-empty (including graph nodes/links).
signal_desk generation is derived from thesis/wiki/data packets.
Signal Desk graph mode is enforced as contextual_evidence with trace hidden.
```

Explanation: key engine behavior and current validation constraints that matter for zero-baseline onboarding.

`canonical/site-reader/src/App.jsx` lines `26-33`, `49-53`, `67-69`, `251-259`

```text
Reader fetches /site-data/signal_desk.json directly.
Main interaction is filtered rows + graph + profile.
UI labels graph as "Contextual Evidence Graph".
When edges absent, empty-state explains filter collapse.
```

Explanation: reader is contract-driven and can render empty edge states without code changes.

`canonical/site-reader/src/logic.js` lines `21-29`, `56-72`, `97-117`, `137-158`

```text
Filters drive visibility for docs/rows/companies/edges.
Edges remain only if support rows survive filters.
Graph support families are co_position/shared_signal.
Edge post-filtering uses min weight and edge limit controls.
```

Explanation: behavior depends on data presence; no data means no edge support survives.

`canonical/site-reader/tests/signal-desk.spec.js` lines `13-22`

```text
Second e2e test selects Baker then expects first svg edge to exist and be clickable.
This assumption fails when dataset intentionally has zero edges.
```

Explanation: current test contract assumes non-empty graph, conflicting with intentional zero baseline.

`canonical/30-thesis/thesis.yaml` lines `1-5`

```text
updated present; baker_hedge_ratio empty; cascade empty; ticker_map empty.
```

Explanation: thesis control plane has been reset to zero.

`canonical/20-data/sources/baker/q4_0000.yaml` lines `1-7`

```text
Placeholder filing with valid structure and empty positions/exits.
```

Explanation: minimal scaffold exists to satisfy source document generation paths.

`canonical/20-data/sources/semianalysis/signals.yaml` lines `1-5`

```text
Semianalysis source retained with empty signals/media lists.
```

Explanation: keeps source lane shape while preserving zero-data content.

`canonical/site-data/signal_desk.json` lines `16`, `45-48`, `55-145`, `157-165`, `188-210`, `211-243`

```text
companies=[] and rows=[].
Graph support families remain co_position/shared_signal; graph.nodes=[] and graph.edges=[].
Source channels still present with counts=0 companies/rows.
Quality: trace_ready=false; graph_edges_contextual_only=true.
```

Explanation: generated contract is structurally valid but intentionally empty.

`canonical/site-data/build.json` lines `2-11`, `15-19`

```text
artifact_counts: companies=0, signals=0, claims=0, pages=3, reports=1.
source_counts: data_yaml=4, wiki_markdown=3.
```

Explanation: confirms current generation footprint and zero-state counts.

`config.yaml` lines `1-4`

```text
sources: [] and companies.deep_dive: [].
```

Explanation: main config no longer seeds any active universe.

`agents/config.yaml` lines `16-17`, `19-27`, `42-43`

```text
deep_dive/watchlist are empty.
paths preserved to canonical lanes.
sources and transcript_sources are empty maps.
```

Explanation: sidecar automation is reset while lane references stay intact.

## Review Breadth

Inspect adjacent tests, docs, and generation boundaries as needed to decide whether zero baseline should be first-class behavior or only transitional state.

## Non-Repo Context Included

- User explicitly requested: delete all data and restart from zero while preserving architecture.
- Current branch already has large prior pruning history; this packet targets the latest reset commit.
- Latest local validations after reset:
  - `uv run python canonical/40-engine/site_data.py` passed
  - `npm run sync-data` passed
  - `npm test` passed
  - `npm run test:e2e` failed one case due missing graph edge under zero-data baseline

## Assumptions And Blind Spots

Assumptions to falsify:

1. Zero-data baseline should remain renderable in reader without adding seed data.
   - Evidence: empty arrays in generated contract and reader empty-state handling.
   - Disproof: required product behavior mandates at least one default graph edge.
2. Architecture is stable enough to scale from zero once first data is ingested.
   - Evidence: stage ownership is explicit and unchanged.
   - Disproof: first ingest reveals missing contracts or brittle stage coupling.

Reviewer blind spots:

- You cannot rerun local commands from this packet alone.
- Untracked local directory `canonical/.obsidian/` is intentionally out of scope.

## What Changed

`canonical data lanes`

- Canonical wiki/data/thesis/reports content was removed and replaced by minimal scaffolds/placeholders.
- Generated site-data was rebuilt from this zero state.

`reader and engine architecture`

- Reader/engine codepaths stayed in place; no architecture rewrite.
- Behavioral mismatch now visible: one e2e test expects non-empty graph data.

## Validation Already Run

- `uv run python canonical/40-engine/site_data.py`: passed
- `npm run sync-data` (in `canonical/site-reader`): passed
- `npm test` (in `canonical/site-reader`): passed
- `npm run test:e2e` (in `canonical/site-reader`): failed (1/3), failure in edge-selection test expecting an existing graph edge

## Known Out Of Scope

- Untracked `canonical/.obsidian/`
- Any architecture-level refactor in engine or reader code
- Rehydrating real research data (not started yet)

## Findings Intake Plan

- Fix now: blockers/high findings on first-entry flow, contract brittleness, or misleading semantics.
- Backlog: medium/low refinements as roadmap tasks for phased rehydration.
- Local verification: findings requiring runtime checks will be validated by Codex in follow-up commits.
- Reject with reason: record rejected findings in PR discussion with explicit rationale.

## Review Tasks

Please review for:

1. The best first-entry workflow from raw ingestion to a useful first reader state.
2. The minimum data/thesis seed needed before graph/table/profile become decision-useful.
3. Whether zero-data mode should be a supported product state vs. transitional setup only.
4. How to reconcile test strategy (edge-required e2e) with intentional zero-data reset.
5. A staged path-to-success plan for this repository (phase 0 -> phase 1 -> phase 2) with clear acceptance checks.

## Bonus Scope

If time allows, propose a compact architecture explainer diagram update that clarifies human responsibilities, AI/skill responsibilities, generated boundaries, and decision loop handoff.

## Desired Reviewer Output

Lead with findings. For each finding include:

- severity: blocker, high, medium, low
- file/path
- issue
- why it matters
- suggested fix

If there are no blocking findings, state that clearly, then provide a prioritized phased success plan.
