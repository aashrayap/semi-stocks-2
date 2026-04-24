---
status: draft
feature: proposal-gated-data-pipeline
---

# Feature Spec: proposal-gated-data-pipeline

## Goal

Make Signal Desk approval-rooted instead of source-rooted.

Only accepted proposal-derived companies and evidence should enter the main
reader feed, even when broad candidate data exists in wiki, fund, earnings, or
SemiAnalysis inputs.

## Users and Workflows

- Ash ingests raw material into the wiki and structured source lanes.
- Candidate evidence accumulates broadly under canonical lanes without implying
  reader admission.
- Thesis-affecting changes create or update proposal files under
  `canonical/20-data/thesis-proposals/`.
- Human gate decides whether a company or thesis addition is admitted.
- Engine emits Signal Desk only from the admitted universe.
- Reader stays a consumer of already gated data.

## Acceptance Criteria

- Candidate-only source population emits zero reader-visible companies, rows,
  source documents, graph nodes, and graph edges.
- Pending or rejected proposals do not enter the main Signal Desk feed.
- Accepted proposal state is the sole admission authority for reader inclusion.
- Source mention, fund position, SemiAnalysis mention, company packet presence,
  role mapping, and `thesis.yaml.ticker_map` do not independently admit a
  company.
- Every emitted company, row, source document, search facet, count, and graph
  artifact is reachable from accepted proposal ancestry.
- Repo-local `ingest-semi` keeps working with the new shape by writing
  thesis-affecting changes into `canonical/20-data/thesis-proposals/`.

## Boundaries

- No staleness, TTL, archive, or supersession lifecycle in this phase.
- No graph database adoption.
- No reader-side approval logic.
- No broad product redesign for Signal Desk.
- No decision yet on an internal review surface for pending proposals unless it
  becomes necessary to keep the main feed clean.

## Human Direction

- Current recommendation: two physical layers plus one admission authority.
- Candidate evidence should remain broad and useful for research.
- Main reader should consume only after gate.
- Proposal decision state should become the admission authority.
- Use `admitted universe` as the term for the accepted proposal-derived set of
  companies, evidence, rows, source documents, counts, search facets, and graph
  artifacts that the engine is allowed to emit.
- Resolved: accepted proposals stay internal and only authorize downstream
  admitted evidence.
- Resolved: post-gate company dossiers should be generated/mirrored from
  accepted proposals in v1, not authored as a second manual truth surface.
- Resolved: generated company dossiers should be persisted under
  `canonical/20-data/companies/_generated/`.
- Resolved: repo state should use `proposed | accepted | rejected` only in this
  phase. `accepted` is the gate; no separate `applied` state yet.
- Resolved: Signal Desk row and source-document emission should be strict to
  accepted proposal `evidence_refs[].source_document_id`.
- Resolved: reader-consumed site-data artifacts should use the same gate, not
  only `signal_desk.json`.

## Risks and Dependencies

- Current engine still unions tickers from ungated inputs, so late filtering is
  not enough.
- Current Signal Desk contract still models `proposal` rows and a
  `pending-proposals` source channel.
- Current tests encode source-emitted position parity, which conflicts with a
  hard gate.
- Full negative fixture coverage is still needed before real company
  repopulation.
