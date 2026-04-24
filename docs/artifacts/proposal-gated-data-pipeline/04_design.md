---
status: ready-for-tasking
feature: proposal-gated-data-pipeline
---

# Design: proposal-gated-data-pipeline

## Chosen Direction

Make Signal Desk approval-rooted. The engine computes the `admitted universe`
first, then emits reader artifacts only from that accepted proposal-derived
closure.

```text
candidate evidence
  -> proposed | accepted | rejected proposal
  -> accepted proposal ancestry
  -> admitted universe
  -> generated company dossiers + admitted evidence
  -> signal_desk.json
  -> reader
```

## Relevant Principles

- Reader consumes generated site data only.
- Canonical lanes keep authority explicit.
- Proposal state aligns with wiki ingest handoff.
- Source presence is evidence, not admission.

## Decisions

### Admission Authority

- Decision: accepted proposal state is the only reader admission authority.
- Options considered: source-rooted company discovery, role-map admission,
  ticker-map admission, accepted proposal admission.
- Rationale: source-rooted discovery already leaks too many possible companies
  into the app shape.
- Affected areas: `canonical/40-engine/engine/site_data.py`,
  `canonical/40-engine/tests/test_signal_desk_contract.py`,
  `docs/architecture.md`.
- Risk: accepted proposal schema must carry stable enough IDs to generate the
  admitted universe.

### State Model

- Decision: use `proposed | accepted | rejected` in this phase.
- Options considered: `accepted` as gate, or `accepted` plus `applied`.
- Rationale: no separate materialization workflow exists yet, so `applied`
  creates process state without behavior.
- Affected areas: `canonical/20-data/thesis-proposals/`, `docs/architecture.md`,
  proposal validation in `canonical/40-engine/engine/site_data.py`.
- Risk: if a later workflow needs an implementation queue, add `applied` then.

### Proposal Visibility

- Decision: proposals stay internal. They authorize admitted companies and
  admitted evidence but do not appear as main Signal Desk rows, source docs,
  source channels, or table views.
- Options considered: visible accepted proposals, visible pending proposals,
  internal-only proposals.
- Rationale: main reader should be a published surface, not a review queue.
- Affected areas: `_source_channel_facets()`,
  `_build_signal_desk_source_documents()`, `_build_signal_desk_rows()`,
  `_build_signal_desk_tables()`, `_build_thesis()` in
  `canonical/40-engine/engine/site_data.py`.
- Risk: if a review UI is needed later, emit a separate internal-review payload.

### Company Dossiers

- Decision: V1 company dossiers are generated/mirrored from accepted proposals.
- Decision: generated company dossiers persist under
  `canonical/20-data/companies/_generated/`.
- Options considered: authored post-gate dossiers, generated-first dossiers.
- Rationale: one authored admission surface during reset reduces drift.
- Affected areas: `canonical/20-data/companies/`,
  `canonical/40-engine/engine/site_data.py`.
- Risk: proposal records may grow until company-specific data deserves an
  authored dossier lane.

### Admitted Universe Closure

- Decision: every emitted company, row, source document, count, search facet,
  graph node, and graph edge must be reachable from accepted proposal ancestry.
- Decision: in this phase, row and source-document emission is strict to
  accepted proposal `evidence_refs[].source_document_id`.
- Decision: top-level reader-consumed site-data artifacts must reconcile to the
  same admitted universe as Signal Desk.
- Options considered: late filtering, per-section filtering, top-level closure.
- Rationale: one root closure is easier to validate than scattered filters.
- Affected areas: `validate_signal_desk()`, row/source/graph builders, contract
  tests.
- Risk: existing source-emitted parity tests must invert because candidate-only
  source data should emit nothing.

## File Map

- `canonical/20-data/thesis-proposals/`: authored proposal decision records.
- `canonical/20-data/companies/_generated/`: persisted generated V1 company dossiers.
- `canonical/40-engine/engine/site_data.py`: admission root, Signal Desk
  projection, validation.
- `canonical/40-engine/engine/synthesis.py`: ticker-map consumer audit; must not
  become reader admission authority.
- `canonical/40-engine/engine/report.py`: ticker-map consumer audit; must not
  become reader admission authority.
- `canonical/40-engine/tests/test_signal_desk_contract.py`: gate contract tests.
- `docs/architecture.md`: canonical lane contract and state names.
- `README.md`: human loop and reader-source-channel wording.

## Open Risks

- Proposal schema must be strict enough for stable IDs without making first-pass
  authoring heavy.
- Existing generated `canonical/site-data/*.json` may change shape once source
  parity is inverted.
