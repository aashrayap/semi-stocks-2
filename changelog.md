# Changelog

## 2026-04-24 - Proposal-Gated Reader Data Pipeline

### Context

Signal Desk needed a hard admission gate so broad source capture could continue
without polluting the reader with companies or evidence that had not cleared a
human/Codex proposal decision.

### Decisions

- Use accepted thesis proposal state as the only reader admission authority.
- Keep proposal records internal; proposals do not appear as reader rows, source
  documents, source channels, or table views.
- Use `proposed | accepted | rejected`; do not add `applied` until there is a
  real separate materialization workflow.
- Persist generated post-gate company dossiers under
  `canonical/20-data/companies/_generated/`.
- Enforce strict `evidence_refs[].source_document_id` closure for emitted reader
  rows and source documents.
- Apply the hard gate to reader-consumed `canonical/site-data/*.json`, not only
  `signal_desk.json`.

### Changed

- Added shared ubiquitous language for admitted universe, admission authority,
  accepted proposal ancestry, candidate evidence, company dossiers, and Signal
  Desk.
- Added `canonical/20-data/thesis-proposals/` as the authored proposal decision
  lane.
- Added `canonical/20-data/companies/_generated/` for generated approved-company
  dossiers.
- Updated `canonical/40-engine/engine/site_data.py` so reader-facing generated
  data reconciles to accepted proposal ancestry and accepted evidence refs.
- Removed proposal rows, proposal source docs, pending proposal source channel,
  and proposal table view from the main Signal Desk feed.
- Updated contract tests to check proposal feed removal, evidence-ref closure,
  and top-level site-data gate parity.
- Updated repo docs and `ingest-semi` routing so wiki/query flows know to check
  thesis proposals for admission state.

### Current Baseline

The clean reset currently emits zero companies, rows, source documents, graph
company nodes, and generated company dossiers because no accepted proposals exist
yet.

### Verification

- `uv run python canonical/40-engine/site_data.py --validate`
- `uv run python canonical/40-engine/tests/test_signal_desk_contract.py`
- `python3 -m json.tool canonical/site-data/signal_desk.json`
- `git diff --check`
- `/Users/ash/.codex/skills/ubiquitous-language/scripts/ubiquitous-language.py lint --repo /Users/ash/Documents/2026/semi-stocks-2`

### Parked

- Direct `canonical/50-reports/latest.html` generation is left in place for now.
  It may become obsolete, but it was not deleted in this pass.
- Staleness, archive, supersession lifecycle, and internal proposal review UI
  remain future work.

### Post-PR Follow-Up

- After this branch merges to main, start a new session to add the first real
  accepted proposal fixture and confirm it emits exactly one company, one
  generated dossier, and only the referenced evidence docs and rows.
