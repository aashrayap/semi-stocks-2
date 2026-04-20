# Signal Desk End-To-End Explanation: Research Pro Handoff

## Copy-Paste Prompt

Please explain the entire Signal Desk application and workflow at three depths:

1. **Level 1 — Explain like I am five:** what the app is, why it exists, and how a human uses it.
2. **Level 2 — Explain like I am a software engineer:** data flow, file ownership, generator boundaries, web contract, graph/table/profile behavior, and validation.
3. **Level 3 — Explain like I am an expert:** canonical propagation model, human-in-the-loop governance, AI/wiki-skill responsibilities, evidence semantics, graph-edge limitations, Trace blockers, and decision-loop implications.

Cover everything from initial raw source ingestion using the wiki / ingest-semi workflow, through wiki query/output filing, human approval of structured data and thesis proposals, generation of `signal_desk.json`, web-reader surface behavior, graph edge meaning, and final human decision-making. Explicitly separate **human responsibilities**, **AI/agent responsibilities**, **generated/automated responsibilities**, and **parked/future features**.

Important scope: do **not** implement code. Your job is to create and improve the ultra-detailed explanatory/specification layer so Codex can execute follow-up implementation. If you see concrete implementation changes, express them as prioritized spec/tasks, acceptance criteria, or UI requirements.

## Reviewer Context

You are reviewing a repo-side application/workflow. Assume access to the remote Git repository and this Markdown packet only. Use repo-relative paths when opening files. If local/runtime context matters, the important facts are included here.

This is not asking for code implementation. It is asking for a teaching/explanation and spec-improvement output that helps a human understand the entire app and gives Codex a clearer execution plan.

## Goal

- Explain Signal Desk end-to-end from raw source ingestion to reader-driven decisions.
- Show the difference between canonical truth, generated app contract, and web surface.
- Explain where humans make judgment calls versus where AI/agents compile or generate state.
- Explain graph edges honestly: contextual shared evidence, not supplier/customer flow.
- Return the explanation in three levels of depth: beginner, software engineer, expert.
- Improve the remaining implementation spec and UI/UX requirements without writing code.

## Research Pro Role

Research Pro should focus on explanation, critique, and spec improvement.

Expected output:

- a clear three-level explanation
- an improved conceptual model
- prioritized implementation tasks for Codex
- acceptance criteria for graph/profile/table/UX polish
- suggested diagram improvements
- warnings where current app semantics could confuse a human

Not expected:

- code patches
- direct repo edits
- full implementation
- replacing Codex as executor

Codex remains the implementation agent after this handoff.

## Current Direction

1. `semi-stocks-2` remains the source of truth for research content and structured evidence.
2. `canonical/40-engine/engine/site_data.py` compiles canonical state into one generated web contract:
   `canonical/site-data/signal_desk.json`.
3. `canonical/site-reader/` is a web-only large-screen reader that consumes only `signal_desk.json`.
4. First graph is contextual evidence only. Trace/pathfinding is parked until a separate typed `relationship_edges` dataset exists.
5. Mobile-specific behavior is out of MVP scope.

## High-Level Diagram

Use this visual as the starting mental model:

```text
docs/diagrams/signal-desk-human-in-loop-workflows.png
```

Visual improvement request:

- Ash will paste the PNG separately.
- If you can reason about Excalidraw structure, suggest a clearer Excalidraw revision.
- If you cannot use Excalidraw directly, describe a better diagram layout in plain language.
- Focus especially on making human-in-the-loop steps, AI/wiki-skill steps, canonical files, generated contract, and reader decision loop easy to understand.

Editable source path:

```text
docs/diagrams/signal-desk-human-in-loop-workflows.excalidraw
```

The diagram shows five lanes:

- Human
- AI / wiki skill
- Canonical files
- Engine
- Web reader

Core loop:

```text
human adds raw source
  -> AI/wiki skill compiles wiki knowledge
  -> human approves structured evidence / proposals
  -> canonical files update
  -> engine validates signal_desk.json
  -> web reader updates
  -> human filters/inspects/decides
  -> next research question creates new source work
```

## Files To Review

Primary starting points:

- `docs/artifacts/signal-desk-schema/18_current_app_state_readup.md`
- `docs/artifacts/signal-desk-schema/17_final_mvp_spec.md`
- `docs/artifacts/signal-desk-schema/05_tasks.md`
- `docs/diagrams/signal-desk-human-in-loop-workflows.png`
- `canonical/site-data/signal_desk.json`
- `canonical/40-engine/engine/site_data.py`
- `canonical/20-data/company_roles.yaml`
- `canonical/site-reader/src/App.jsx`
- `canonical/site-reader/src/logic.js`
- `canonical/10-wiki/schema.md`
- `.codex/skills/ingest-semi/SKILL.md`

Broader context:

- `README.md`
- `docs/architecture.md`
- `docs/doc-contract.md`
- `canonical/10-wiki/index.md`
- `canonical/30-thesis/thesis.yaml`
- `canonical/20-data/sources/**`
- `canonical/20-data/companies/**`
- `canonical/20-data/thesis-proposals/**`

## Current App State

Current generated artifact:

```text
canonical/site-data/signal_desk.json
```

Current version:

```text
signal-desk-v0.2
```

Current counts:

| Collection | Count |
|---|---:|
| Source documents | 21 |
| Companies | 43 |
| Rows | 177 |
| Graph nodes | 43 |
| Graph edges | 418 |

Rows:

| Row type | Count | Meaning |
|---|---:|---|
| `position` | 45 | Raw Baker / Leopold 13F position legs |
| `signal` | 73 | Company, SemiAnalysis, and thesis-stage evidence observations |
| `claim` | 55 | Forward-looking proof gates / claims |
| `proposal` | 4 | Thesis proposals, table/profile only |

Source channels:

| Source channel | Companies | Rows | Source docs |
|---|---:|---:|---:|
| Baker | 16 | 20 | 1 |
| Leopold | 25 | 25 | 1 |
| SemiAnalysis | 8 | 6 | 1 |
| Company earnings | 13 | 92 | 13 |
| Thesis stage | 12 | 30 | 1 |
| Pending proposals | 14 | 4 | 4 |

Quality:

- UI-ready: `true`
- Trace-ready: `false`
- rows without source document: `0`
- Baker raw positions: `20 source / 20 emitted`
- Leopold raw positions: `25 source / 25 emitted`
- rows without sortable date: `122`
- graph edges contextual only: `true`

## Required Emphasis For Your Explanation

Do not skip these.

### Graph Meaning

Explain graph edges at all three levels. The core message:

```text
An edge means shared evidence under current filters.
It does not mean supplier/customer, money flow, chip flow, ownership, causality, or Trace path.
```

Current emitted edge support families:

- `co_position`
- `shared_signal`

Reserved but not emitted:

- `shared_thesis`
- `explicit_relationship`

Trace needs future typed `relationship_edges`.

### Data Contract

Explain `signal_desk.json` as the main boundary between canonical truth and web surface.

Key collections:

- `source_documents`
- `companies`
- `rows`
- `graph`
- `indexes`
- `tables`
- `facets`

Important explanation:

```text
canonical files optimize for research truth.
signal_desk.json optimizes for web reading.
```

### Source Channels

Explain Source Channel as the user-facing provenance lens.

Current channels:

- Baker
- Leopold
- SemiAnalysis
- Company earnings
- Thesis stage
- Pending proposals

Source Channel answers:

```text
Which source or evidence channel is contributing this context?
```

It is not topic clustering. Topic clustering is parked.

## Canonical Source Model

Canonical flow:

```text
canonical/10-wiki/raw
  -> canonical/10-wiki/sources | concepts | outputs
  -> canonical/20-data/sources | companies | thesis-proposals
  -> canonical/30-thesis/thesis.yaml
  -> canonical/40-engine
  -> canonical/site-data/signal_desk.json
  -> canonical/site-reader
```

Important distinction:

- `10-wiki` is narrative/context.
- `20-data` is structured evidence.
- `30-thesis` is thesis control plane.
- `40-engine` compiles and validates.
- `site-data` is generated app data.
- `site-reader` is a web reader.

The reader does **not** parse canonical markdown or YAML directly.

## Wiki / Ingest Workflow

Repo-local semi-stocks wiki workflow uses `ingest-semi`, not a random wiki checkout.

Key rules:

- Wiki root: `canonical/10-wiki`
- Raw sources: `canonical/10-wiki/raw`
- Never modify `raw/`
- Read `canonical/10-wiki/schema.md` before wiki writes
- New source summaries go under `canonical/10-wiki/sources/`
- Durable concepts go under `canonical/10-wiki/concepts/`
- Filed query outputs go under `canonical/10-wiki/outputs/`
- After wiki writes:
  - update `canonical/10-wiki/index.md`
  - rebuild `_index.json`, `_backlinks.json`, `_lint.json`
  - append `canonical/10-wiki/log.md`

Human-in-loop ingestion shape:

```text
Human:
  finds source
  saves raw source under canonical/10-wiki/raw/
  decides whether source matters
  reviews AI summary and proposed direction

AI / ingest-semi:
  reads schema
  reads raw source
  drafts or updates source page
  updates related concept pages
  uses wikilinks
  flags contradictions
  proposes structured thesis/data patches when needed

Human:
  accepts/rejects/promotes structured changes
```

## How Sources Become Signal Desk Rows

Signal rows mostly come from `20-data` and `30-thesis`, not directly from wiki prose.

| Input | Output in Signal Desk |
|---|---|
| `canonical/20-data/sources/baker/q4_2025.yaml` | `source_document` + `position` rows |
| `canonical/20-data/sources/leopold/q4_2025.yaml` | `source_document` + `position` rows |
| `canonical/20-data/sources/semianalysis/signals.yaml` | `source_document` + `signal` rows |
| `canonical/20-data/companies/**` | `source_document` + `signal` / `claim` rows |
| `canonical/20-data/thesis-proposals/**` | `source_document` + `proposal` rows |
| `canonical/30-thesis/thesis.yaml` | thesis themes + thesis-stage signal rows |
| `canonical/10-wiki/sources/**` | related path / wiki slug metadata |
| `canonical/10-wiki/concepts/**` | context/search pages, not direct rows |
| `canonical/10-wiki/outputs/**` | context/search pages, not direct rows |
| `canonical/10-wiki/raw/**` | raw source archive, not direct rows |

## Human vs AI vs Automation

Human responsibilities:

- choose sources worth adding
- review AI summaries
- decide whether a source changes the thesis
- approve or reject proposals
- promote evidence into structured data when appropriate
- interpret reader output
- decide next research/trade/ingest action

AI / agent responsibilities:

- compile raw sources into wiki pages
- maintain wikilinks and summaries
- query the wiki
- file useful query outputs
- propose structured changes when source evidence warrants it
- generate reports or predictions only within sidecar boundaries

Automation / engine responsibilities:

- load canonical source files
- normalize rows and source documents
- preserve raw position legs
- validate references
- generate `signal_desk.json`
- generate web-reader data

Reader responsibilities:

- search/filter source-channel evidence
- show graph/table/profile
- explain why a company or edge appears
- never create canonical truth by itself

## Graph Meaning

Graph mode:

```text
contextual_evidence
```

Graph nodes:

```text
companies only
```

Graph edge means:

```text
two companies share evidence under current filters
```

Graph edge does not mean:

```text
supplier/customer relationship
money flow
chip flow
ownership flow
causal relationship
Trace path
```

Current graph support families:

- `co_position`: both companies appear in the same Baker or Leopold filing
- `shared_signal`: both companies appear in the same multi-company signal

Not emitted:

- `shared_thesis`
- `explicit_relationship`
- Trace/pathfinding edges

Trace blocker:

```text
No typed relationship_edges dataset exists.
```

## Web Surface

Current app:

```text
canonical/site-reader/
```

Local URL when dev server is running:

```text
http://127.0.0.1:5173/
```

Surface:

- header
- toolbar
- stats strip
- contextual graph
- evidence table
- right-side profile panel

Toolbar:

- Search
- Source Channel
- Company Role
- Filters

Filters:

- Thesis Theme
- Timeline from/to
- Include undated

Table views:

- Signals
- Claims
- Positions
- Proposals
- Sources

Profile:

- empty state
- selected company state
- selected shared-evidence edge state

## Validation Already Run

These commands passed earlier in this workstream:

```bash
uv run python canonical/40-engine/site_data.py --validate
uv run python canonical/40-engine/tests/test_signal_desk_contract.py
cd canonical/site-reader && npm test
cd canonical/site-reader && npm run build
```

Current local server has also responded at:

```text
http://127.0.0.1:5173/
```

## Known Out Of Scope

Out of current MVP:

- mobile-specific behavior
- Trace
- relationship pathfinding
- inferred supplier/customer edges
- topic clustering
- agent prediction import
- human review workflow UI
- full wiki reader

Unrelated dirty repo state exists in `agents/`, generated wiki-site files, and other canonical artifacts. Do not assume every dirty file belongs to Signal Desk.

## What Is Left In Implementation

Current implementation has the data contract and first web reader scaffold. Remaining work is mostly explanation clarity, UX polish, and graph readability.

Already implemented:

- `canonical/20-data/company_roles.yaml`
- `canonical/site-data/signal_desk.json`
- source channels
- source documents
- unified rows
- contextual graph data
- validation and contract tests
- web reader scaffold
- search/source-channel/company-role/filter logic
- graph/table/profile first pass

Still left:

1. **Graph readability**
   - Reduce 418 edge clutter through thresholds, toggles, top-N support, or another spec-level approach.
   - Consider edge thresholds, top-N support, or toggles by support family.
   - Make clear that the graph shows shared evidence, not relationship flow.

2. **Profile depth**
   - Improve company profiles with grouped source channels.
   - Improve edge profiles with clearer support rows and source-document links.
   - Show "why visible under current filters" more explicitly.

3. **Table polish**
   - Improve per-tab column formatting.
   - Better values for positions, claims, proposals, and source documents.
   - Add clearer sorting / null-date handling.

4. **Reader UX**
   - Improve filter state display.
   - Add legend/help copy for graph semantics.
   - Add empty states for filtered-out views.

5. **Browser QA**
   - Run screenshot review.
   - Check large-screen layout.
   - Check graph/table/profile interaction.

6. **Future data work**
   - Add typed `relationship_edges` only if Trace becomes a future feature.
   - Keep Trace parked until then.
   - Do not infer supplier/customer edges from prose.

Research Pro should explain these remaining items in human terms too: what is complete enough for understanding now, what is rough, and what future work would make the reader more decision-grade.

Research Pro should also turn these items into a concise "next implementation spec" for Codex, with:

- priority order
- concrete expected behavior
- acceptance tests / visual checks
- what to cut if scope grows

## Review / Explanation Tasks

Please produce a three-level explanation.

### Level 1 — Complete Beginner

Explain:

- what Signal Desk is
- what problem it solves
- what "source", "row", "company", "graph edge", and "profile" mean in plain language
- how a human gets from new source to decision
- why Trace is not available yet

### Level 2 — Software Engineer

Explain:

- file/data pipeline
- `10-wiki`, `20-data`, `30-thesis`, `40-engine`, `site-data`, `site-reader`
- how `signal_desk.json` is generated
- how source documents, rows, companies, indexes, tables, and graph relate
- how filters compose
- why the reader consumes one artifact
- validation gates

### Level 3 — Expert

Explain:

- canonical propagation model and authority boundaries
- human-in-loop governance
- AI/wiki skill as compiler, not authority
- provenance model and source-document design
- graph semantics and why edges are contextual evidence only
- why co-position/shared-signal are allowed but Trace is parked
- how this design avoids false certainty
- what future data would be needed for relationship edges and Trace

## Desired Output Format

Return one cohesive explanation with:

1. Executive summary
2. Level 1 explanation
3. Level 2 explanation
4. Level 3 explanation
5. Human vs AI vs automation responsibility table
6. End-to-end workflow table
7. Graph edge explanation
8. Reader decision-loop explanation
9. Glossary of key terms
10. What is ready now vs what is parked

Prefer clarity over brevity. The goal is to help Ash understand the whole application and operating workflow.
