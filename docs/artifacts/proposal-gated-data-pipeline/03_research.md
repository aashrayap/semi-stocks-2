---
status: draft
feature: proposal-gated-data-pipeline
---

# Research: proposal-gated-data-pipeline

## Flagged Items

- Current build is still source-additive, not approval-rooted.
- `thesis.yaml.ticker_map` still acts as an admission input in synthesis and
  reporting paths.
- Signal Desk still emits proposal rows and a `pending-proposals` source
  channel.
- Current contract tests enforce full source-to-emitted fund-position parity.
- Repo docs and the repo-local wiki skill already support proposal files as the
  intended thesis-affecting handoff.

## Findings

### Codebase

#### Question

Which current engine paths admit companies from ungated inputs before any
proposal gate is applied?

#### Answer

The current company universe is built from a union of thesis tickers, company
packets, Baker positions, Leopold positions, and SemiAnalysis tickers.

#### Evidence

- `canonical/40-engine/engine/site_data.py` `_build_companies()` unions tickers
  from `ticker_map`, company packets, `leopold.tickers()`, `baker.tickers()`,
  and `semi.tickers()`.
- `canonical/40-engine/engine/synthesis.py` `agreement_map()` and
  `divergences()` iterate `thesis.get("ticker_map", {})`.
- `canonical/40-engine/engine/report.py` iterates `thesis.get("ticker_map", {})`
  for report shaping.

#### Confidence

High

#### Question

Which Signal Desk payload sections currently emit pending proposal data into the
main reader contract?

#### Answer

Signal Desk currently has first-class proposal emission in facets, source
documents, rows, tables, and thesis payload metadata.

#### Evidence

- `canonical/40-engine/engine/site_data.py` `_source_channel_facets()` defines
  `source-channel:pending-proposals`.
- `_build_signal_desk_source_documents()` emits thesis proposals as
  `document_kind: thesis_proposal`.
- `_build_signal_desk_rows()` includes `_build_proposal_rows()`.
- `_build_signal_desk_tables()` defines a `proposals` table view and includes it
  in view order.
- `_build_thesis()` serializes proposal metadata into the emitted thesis
  payload.

#### Confidence

High

#### Question

Do current contract tests encode source-rooted emission assumptions that must be
inverted?

#### Answer

Yes. The current contract tests require source and emitted position-leg counts
to match for Baker and Leopold, and they explicitly preserve `proposal` rows as
part of the contract.

#### Evidence

- `canonical/40-engine/tests/test_signal_desk_contract.py`
  `test_position_leg_counts_match_source()` asserts Baker and Leopold source
  counts equal emitted counts.
- `test_claims_and_proposals_do_not_create_graph_edges()` assumes proposal rows
  are present and only constrains their graph eligibility.

#### Confidence

High

### Docs

#### Question

What do current repo docs already say about `canonical/20-data/thesis-proposals/`
and the human approval loop?

#### Answer

Repo docs already describe `thesis-proposals` as a structured staging area and
the README human loop already places human approval before Signal Desk.

#### Evidence

- `docs/architecture.md` describes
  `canonical/20-data/thesis-proposals/` as pending thesis patch staging.
- `README.md` defines the human loop as
  `raw source -> wiki ingest/query -> human approval -> canonical data/thesis -> signal_desk.json -> web reader`.

#### Confidence

High

#### Question

Does the repo-local `ingest-semi` skill already route thesis-affecting source
changes into proposal files instead of direct thesis edits?

#### Answer

Yes. The repo-local wiki skill already instructs thesis-affecting ingest work to
create or update explicit proposal files under `canonical/20-data/thesis-proposals/`.

#### Evidence

- `.codex/skills/ingest-semi/SKILL.md` rule 7:
  thesis, bottleneck, or company-signal changes should create/update a
  structured proposal and should not silently edit thesis state.

#### Confidence

High

### Cross-Ref

#### Question

How do the Research Pro review findings compare with current local engine and
contract reality?

#### Answer

The strongest external review findings are confirmed locally. The main blocker
is real: the engine is source-additive today, and proposal visibility is
currently part of the emitted reader contract.

#### Evidence

- Research Pro review called out source-rooted company discovery and proposal
  leakage.
- Local inspection confirms source-union company building and proposal emission
  in Signal Desk.

#### Confidence

High

## Patterns Found

- Safe path now: make proposal acceptance the admission root, then derive every
  emitted artifact from that closure.
- Unsafe path now: keep broad source-rooted emission and rely on later filters.
- Wiki skill already matches proposal-gated flow; engine and tests are the parts
  that still need inversion.

## Core Docs Summary

- `README.md` already frames Signal Desk as downstream of human approval.
- `docs/architecture.md` already reserves `canonical/20-data/thesis-proposals/`
  as a staging lane.
- `ingest-semi` already writes thesis-affecting findings into proposal files.
- Current implementation lags the documented intent.

## Direction Options

### Option A

Two physical layers plus one admission authority.

- Candidate evidence stays broad under source lanes.
- Proposal files hold decision state.
- Approved company dossiers exist post-gate.
- Engine emits only accepted-proposal-derived closure.

Assessment: safest fit for current reset stage.

### Option B

Single physical lane with strict status fields and hard validation.

- Fewer directories.
- Higher risk of drift because the current implementation already has multiple
  admission paths and proposal-visible reader semantics.

Assessment: possible later, weaker now.

## Resolved Human Direction

- Accepted proposals stay internal and do not appear as main Signal Desk rows
  or source documents.
- V1 company dossiers are generated/mirrored from accepted proposals. They are
  part of the admitted universe, not an independently authored admission
  surface.
- Proposal state is `proposed | accepted | rejected` for this phase. `accepted`
  is the gate; `applied` stays out until there is a real separate
  materialization workflow.

## Open Questions

- None for design tasking.
