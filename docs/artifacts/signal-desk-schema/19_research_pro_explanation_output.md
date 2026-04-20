---
status: research-pro-output
feature: signal-desk-schema
updated: 2026-04-20
source: Research Pro response pasted in chat
---

# Research Pro Explanation Output

## Executive Verdict

Research Pro validated the core architecture:

- Signal Desk is a schema-first evidence reader.
- Canonical files remain the research authority.
- `canonical/site-data/signal_desk.json` is the web-reader contract.
- `canonical/site-reader/` consumes only that generated artifact.
- The first graph is contextual evidence, not relationship flow.
- Trace remains parked until a typed `relationship_edges` dataset exists.

Most important message:

```text
The app does not decide for the human.
It makes judgment more evidence-dense, provenance-aware, and repeatable.
```

## Three-Level Explanation Summary

### Level 1 - Beginner

Signal Desk is an evidence board.

- A source is where evidence came from.
- A row is one piece of structured evidence.
- A company is what the evidence touches.
- A graph edge means two companies share evidence under current filters.
- A profile explains why something is visible.

Human loop:

```text
find source -> ingest/compile -> approve structured evidence -> rebuild reader -> inspect -> decide next question
```

Trace is not available because the current graph has shared evidence, not real typed relationship roads.

### Level 2 - Software Engineer

Pipeline:

```text
canonical/10-wiki       narrative/context
canonical/20-data       structured evidence
canonical/30-thesis     thesis control
canonical/40-engine     compiler/validator
canonical/site-data     generated web contract
canonical/site-reader   web reader
```

Contract:

```text
signal_desk.json = version + build + features + defaults + quality + facets + source_documents + companies + rows + graph + indexes + tables
```

Reader controls:

- Search
- Source Channel
- Company Role
- Filters: Thesis Theme, Timeline, Include undated

Validation already gives real guardrails:

- stable IDs
- source-document references
- row/company references
- graph endpoint and support-row integrity
- exact Baker/Leopold raw position preservation
- Trace hidden and parked

### Level 3 - Expert

Research Pro framed the system as a canonical propagation pipeline with strict authority boundaries:

- AI/wiki skill compiles and proposes.
- Human approves promotion into canonical state.
- Engine normalizes and validates.
- Reader inspects; it does not author truth.

Evidence semantics:

- `source_documents` are provenance envelopes.
- `rows` are typed evidence primitives.
- `companies` are role-tagged profile entities.
- `graph.edges` are contextual shared evidence.

Core graph constraint:

```text
Do not overread contextual co-evidence as relationship flow.
```

Research Pro's main expert risk:

- graph can look too relationship-like
- proposals can look too accepted
- label-only timeline rows can look more precise than they are
- source-channel filters can be mistaken for topic clusters

## Human vs AI vs Automation

| Area | Human | AI / Wiki Skill | Engine / Automation | Reader |
|---|---|---|---|---|
| Raw source intake | choose/save source | none until invoked | none | none |
| Wiki compilation | review summary | summarize/link/propose | none | none |
| Structured promotion | accept/reject/edit | suggest patches | none | none |
| Thesis governance | decide changes | suggest implications | none | none |
| Contract generation | approve rebuild direction | none | normalize/validate/emit | none |
| Evidence exploration | interpret | none | none | search/filter/render |
| Final decision | decide next action | may summarize | none | supports decision |

## Graph Edge Explanation

Required explanation:

```text
Shared evidence: NVDA <-> TSM
This edge reflects shared evidence under the current filters.
It does not imply a directional supplier/customer relationship.
```

Current support families:

- `co_position`
- `shared_signal`

Not emitted:

- `shared_thesis`
- `explicit_relationship`
- Trace/pathfinding

## Ready Now vs Parked

| Area | Ready now | Still rough | Parked |
|---|---|---|---|
| Data contract | generated, versioned, validated | none at boundary level | n/a |
| Evidence model | source docs, rows, companies, facets | proposal/claim presentation | more row types later |
| Graph | contextual company graph | 418 edges too dense | Trace, relationship graph |
| Reader | first web pass | UX/profile/table polish | mobile |
| Provenance | rows have source docs | better why-visible UI | full wiki reader |
| Quality | validation/tests exist | 122 label-only rows need honest UI | timeline enrichment |

## Diagram Improvement Guidance

Research Pro suggested revising the workflow diagram to:

1. Split into two loops:
   - research compilation loop
   - reader decision loop
2. Show `10-wiki`, `20-data`, and `30-thesis` separately.
3. Add a human approval diamond before canonical promotion.
4. Make `signal_desk.json` the strongest visual boundary.
5. Move Trace blocker near the graph lane.
6. Add a reader legend:

```text
Graph = shared evidence, not relationship flow.
```

## Next Implementation Spec

Research Pro prioritized remaining work:

| Priority | Task | Expected behavior | Acceptance checks |
|---|---|---|---|
| Highest | Graph semantics/readability | visible legend, clutter control, clear edge meaning | graph says shared evidence; edge support visible; Trace absent |
| High | Profile depth | company/edge profiles grouped by source channel and row type | profile explains why visible and links evidence/source docs |
| High | Table polish | tab-specific columns, honest timeline labels, null dates last | signals/claims/positions/proposals/sources are readable |
| Medium | Filter state/empty states | active filters and zero states are clear | no broken-looking empty graph/table/profile |
| Medium | Large-screen QA | graph/table/profile stable at target viewport | no overlap or hidden controls |
| Lower | Screenshot browser QA | visual states captured and reviewed | default/filter/company/edge/empty screenshots |

Research Pro's implementation order:

1. graph legend + clutter controls
2. edge/company profile clarity
3. table/date clarity
4. filter-state and empty-state polish
5. browser screenshot QA

Do not expand into:

- Trace
- inferred supplier/customer logic
- topic clustering
- wiki reader UI
- mobile behavior

## Guardrail

Research Pro's final guardrail:

```text
If time is short, keep graph simpler, profiles plainer, and table less fancy.
Do not ship a state where shared evidence can be mistaken for relationship flow,
or pending proposals can be mistaken for confirmed evidence.
```

