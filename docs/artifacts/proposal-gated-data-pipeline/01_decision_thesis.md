# Proposal-Gated Data Pipeline: Human Decision Thesis

## Purpose

This document explains the proposed data-pipeline change for a human final
decision. It answers one question:

```text
Should Signal Desk become approval-rooted, where only accepted proposal-derived
companies and evidence can enter the reader?
```

Short answer:

```text
Yes. Keep broad evidence capture, but make accepted proposal state the only
reader admission authority.
```

## Current Decision

Recommended decision:

```text
Adopt a two-physical-layer data model:

1. Candidate evidence layer:
   canonical/20-data/sources/**
   Broad, source-backed, pre-gate, not reader-visible.

2. Approved company/data layer:
   canonical/20-data/companies/**
   Narrow, post-gate, accepted proposal-derived, reader-visible.

Decision authority:
   canonical/20-data/thesis-proposals/**
   Proposal records with proposed / accepted / rejected state.
```

Reader rule:

```text
Signal Desk reads only the accepted proposal-derived universe.
```

Non-rule:

```text
Ticker presence, role mapping, source mention, and thesis ticker_map do not
admit a company into the reader.
```

## How This Fits The Current Wiki Skill

The repo-local wiki skill already supports the proposed gate shape.

Current wiki skill facts:

```text
Skill name:
  ingest-semi

Fixed wiki root:
  canonical/10-wiki

Reads from:
  canonical/10-wiki
  canonical/20-data
  canonical/30-thesis/thesis.yaml
  repo docs

Writes to:
  canonical/10-wiki/sources
  canonical/10-wiki/concepts
  canonical/10-wiki/outputs
  generated wiki state
  explicit proposal files under canonical/20-data/thesis-proposals when needed

Never writes to:
  canonical/10-wiki/raw
```

Most important existing rule:

```text
If a source changes thesis, bottleneck status, or company signals, create or
update a structured proposal under canonical/20-data/thesis-proposals; do not
silently edit thesis state.
```

Current query mode:

```text
Start at canonical/10-wiki/index.md.
Follow wikilinks through concepts, sources, and outputs.
Use canonical/20-data only when structured evidence is needed.
Use canonical/30-thesis/thesis.yaml only for control-plane conclusions.
```

Fit verdict:

```text
The proposal-gated architecture does not fight the wiki skill.
It formalizes the skill's existing proposal step into the admission gate.
```

What changes:

```text
Before:
  A proposal file is a patch suggestion.

After:
  A proposal file is the decision authority for reader admission.
```

What does not change:

```text
Raw sources remain immutable.
Wiki source/concept pages remain the synthesis and query layer.
20-data remains the structured evidence layer.
30-thesis remains the narrow thesis control plane.
site-data remains generated.
site-reader remains a consumer only.
```

## Layer 1: Explain Like I Am Five

Signal Desk is like a clean display shelf.

Sources are like a big messy table full of parts. The table can have many
companies, notes, and clues. That is good. Research needs mess.

But not every thing on the messy table belongs on the display shelf.

Today the app can be tempted to put things on the shelf just because they were
found on the table. That is the pollution risk.

The new rule is simple:

```text
Nothing goes on the shelf until Ash says yes through a proposal.
```

Picture:

```text
Messy table
  many companies
  many notes
  many clues
      |
      v
Ask Ash:
  "Should this company enter Signal Desk?"
      |
      v
Yes only
      |
      v
Clean display shelf
  approved companies only
```

Example:

```text
Baker filing mentions NVDA, AMD, INTC, MU.

Before:
  All four can start showing up in app shape.

After:
  All four can stay in research notes.
  Only the accepted proposal company shows in Signal Desk.
```

Human meaning:

```text
The app stops showing "things we saw."
The app starts showing "things we decided belong here."
```

## Layer 2: Explain Like A Software Engineer

The current risk is a source-rooted build.

```text
source tickers
  -> build company set
  -> build rows/docs/search/graph
  -> filter late
  -> reader
```

That shape is fragile because many inputs can imply a company:

```text
Baker ticker
Leopold ticker
SemiAnalysis ticker
earnings packet ticker
thesis ticker_map entry
role map entry
proposal row
```

The proposed shape is approval-rooted.

```text
accepted proposals
  -> admitted company IDs
  -> admitted evidence refs
  -> emitted rows/docs/search/graph
  -> reader
```

The engine should compute an admitted universe first:

```text
admitted_universe = closure(
  accepted proposal IDs
  -> approved company IDs
  -> evidence refs
  -> source document refs
)
```

Then every emitted artifact must be inside that closure.

Required invariant:

```text
for artifact in signal_desk.json:
  assert artifact is reachable from accepted proposal ancestry
```

This applies to:

```text
companies
rows
source_documents
search entries
facets
counts
graph nodes
graph edges
```

Data layout:

```text
canonical/10-wiki/raw/**
  Immutable source material.

canonical/10-wiki/sources|concepts|outputs/**
  Wiki synthesis and query output.

canonical/20-data/sources/**
  Candidate structured evidence.
  Broad.
  Pre-gate.
  Not reader-visible by default.

canonical/20-data/thesis-proposals/**
  Human decision records.
  proposed / accepted / rejected.
  Sole admission authority.

canonical/20-data/companies/**
  Generated/mirrored V1 company dossiers.
  Derived from accepted proposal ancestry.

canonical/30-thesis/thesis.yaml
  Thesis control plane.
  Not a company admission plane.

canonical/40-engine/**
  Builds admitted closure and generated reader data.

canonical/site-data/**
  Generated JSON.

canonical/site-reader/**
  Web reader.
  Consumes generated JSON only.
```

Minimal proposal record:

```yaml
kind: thesis_proposal
schema_version: 1
id: proposal:nvidia-memory-pressure-2026-q2
status: proposed
title: NVIDIA memory pressure should enter the gated thesis universe
decision_question: Should company:nvda enter the current Signal Desk universe?
thesis_theme_ids:
  - thesis-theme:ai-accelerator-demand
companies:
  - company_id: company:nvda
    ticker: NVDA
    name: NVIDIA
    role_id: company-role:chip_designer
    inclusion_reason: Primary company under review.
evidence_refs:
  - candidate_record_id: candidate:semianalysis:2026-04-21:01
    source_document_id: source-document:semianalysis:2026-04-21
    supports_company_ids:
      - company:nvda
    summary: AI accelerator demand is tightening HBM and packaging capacity.
decision:
  decided_by: null
  decided_at: null
  notes: ""
lineage:
  wiki_page_ids:
    - wiki:example-source-page
```

When accepted:

```yaml
status: accepted
decision:
  decided_by: ash
  decided_at: "2026-04-23"
  notes: "Admit NVDA for current memory-pressure thesis tracking."
```

Minimal approved company record:

```yaml
kind: approved_company
schema_version: 1
id: company:nvda
ticker: NVDA
name: NVIDIA
primary_role_id: company-role:chip_designer
secondary_role_ids: []
display_tags: []
thesis_theme_ids:
  - thesis-theme:ai-accelerator-demand
admission:
  primary_proposal_id: proposal:nvidia-memory-pressure-2026-q2
  inclusion_summary: Primary company under current memory-pressure thesis.
```

No authored `reader_eligible` field:

```text
reader eligibility = derived(status == accepted and lineage valid)
```

Main test idea:

```text
Candidate-only source data emits nothing.
Pending proposal emits nothing.
Accepted proposal emits exactly its admitted company/evidence closure.
```

## Layer 3: Expert Explanation

This architecture changes the reader boundary from source-additive to
decision-closed.

The current canonical pipeline already has the right lanes:

```text
10-wiki -> 20-data -> 30-thesis -> 40-engine -> site-data -> site-reader
```

The missing rule is not another lane. The missing rule is admission authority.

Without that rule, the pipeline has ambiguous company ontology:

```text
A company can appear because a source mentioned it.
A company can appear because a structured packet used its ticker.
A company can appear because thesis.yaml named it.
A company can appear because a role map classified it.
A company can appear because a proposal discussed it.
```

Those are different meanings:

```text
mentioned
structured
classified
proposed
accepted
active in reader
```

The proposal formalizes these meanings:

```text
mentioned/source-backed:
  Candidate evidence. No reader authority.

proposed:
  Human decision pending. No main reader authority.

accepted:
  Admission authority. Reader universe may include this closure.

rejected:
  Preserved decision history. No reader authority.
```

The engine should therefore stop asking:

```text
Which companies can I discover?
```

It should ask:

```text
Which accepted proposal decisions define the admitted universe?
```

Then it computes the closure:

```text
accepted proposal
  -> admitted company IDs
  -> generated company dossier
  -> evidence refs
  -> source document refs
  -> emitted reader rows
  -> emitted reader facets/counts/search
  -> graph nodes/edges from emitted rows only
```

That closure is the app boundary.

This also clarifies the wiki skill's role. The wiki remains the synthesis and
query substrate, not the admission plane. During ingest, the wiki skill can
summarize a source, cross-link concepts, and create structured proposal files.
But it should not silently mutate thesis state or app visibility.

The proposal record becomes the bridge between:

```text
LLM-readable synthesis
  and
machine-validated app admission
```

This is why stable IDs matter. Free text can explain; IDs govern.

Required ID classes:

```text
proposal ID
company ID
role ID
thesis theme ID
candidate evidence ID
source document ID
wiki page ID
row ID
```

The reader does not need a graph database. It needs referential closure:

```text
Every emitted reader object must prove ancestry to an accepted proposal.
```

Graph semantics stay intentionally narrow:

```text
Graph edge = shared emitted evidence under current filters.
Graph edge != supplier relationship.
Graph edge != causality.
Graph edge != money flow.
Graph edge != Trace.
```

The graph must be built after gate closure, not before. Otherwise an ungated
company can distort co-position or shared-signal support even if it is filtered
out visually later.

The design also preserves future staleness work without implementing it now:

```text
Use status-derived eligibility.
Keep accepted proposal ancestry.
Keep decision timestamps.
Keep stable IDs.
Do not hard-code permanent visibility with reader_eligible.
```

Later, states like `archived`, `superseded`, or `inactive` can be added without
rewriting the core gate concept.

## Before And After

Before:

```text
sources
  -> discovered tickers
  -> company set
  -> rows/docs/graph/search
  -> late filtering
  -> reader
```

Risk:

```text
"We saw this company" can become "this company is in the app."
```

After:

```text
sources
  -> candidate evidence
  -> proposal
  -> accepted decision
  -> admitted universe
  -> rows/docs/graph/search
  -> reader
```

Rule:

```text
"We accepted this proposal" becomes "this company is in the app."
```

## Decision Criteria

Approve this proposal if the desired Signal Desk meaning is:

```text
Signal Desk shows the companies Ash has admitted into the current research
universe, backed by source lineage.
```

Reject or defer this proposal if the desired Signal Desk meaning is:

```text
Signal Desk is a broad exploratory search surface over every source-mentioned
semi company.
```

The current user intent matches the first meaning.

## Recommended Final Decision

Adopt this architecture:

```text
Two physical layers.
One admission authority.
Approval-rooted engine.
Accepted-only main reader feed.
Wiki skill creates proposals, not direct app visibility.
```

Adopt these states now:

```text
proposed
accepted
rejected
```

Do not adopt yet:

```text
reader_eligible
applied
stale
archived
superseded
```

Parked for later:

```text
staleness review
archive UX
supersession links
internal pending-proposal review surface
Trace / typed relationship edges
```

## Acceptance Tests Before Real Repopulation

Minimum tests:

```text
1. Clean reset emits zero companies and remains valid.
2. Candidate-only sources emit zero companies.
3. Pending proposal emits zero companies to main reader.
4. Accepted proposal emits exactly admitted company closure.
5. Mixed source document does not leak non-admitted neighbor companies.
6. Role mapping without accepted proposal emits nothing.
7. thesis.yaml ticker_map without accepted proposal emits nothing or fails.
8. Graph edges use emitted rows only.
9. Source-channel counts reconcile to emitted rows/docs only.
10. Search entries reconcile to emitted companies/rows/docs only.
```

## Human Final Decision Prompt

Choose one:

```text
1. Approve proposal-gated architecture.
   Proceed to docs/schema/tests/engine implementation.

2. Approve concept, but require pending proposals visible in a separate review
   payload before implementation.

3. Defer and keep source-rooted reader population for now.
```

Recommended choice:

```text
1
```
