---
status: draft
feature: proposal-gated-data-pipeline
---

# Tasks: proposal-gated-data-pipeline

## Execution Order

0. PGDP-00: Create shared ubiquitous language.
1. PGDP-01: Update docs and proposal state language.
2. PGDP-02: Add minimal proposal fixtures/schema expectations.
3. PGDP-03: Add admitted-universe builder and validation.
4. PGDP-04: Remove proposal emission from main Signal Desk feed.
5. PGDP-05: Generate/mirror V1 company dossiers from accepted proposals.
6. PGDP-06: Invert contract tests from source parity to gate parity.
7. PGDP-07: Audit ticker-map consumers and final verification.

## Task List

### PGDP-00 - Create Shared Ubiquitous Language

- Status: done.
- Files:
  - `docs/UBIQUITOUS_LANGUAGE.md`
  - `AGENTS.md`
- Work:
  - Add repo-level terminology contract.
  - Add AGENTS pointer for planning, implementation, and review.
- Acceptance:
  - Language doc defines `admitted universe`, `admission authority`,
    `accepted proposal ancestry`, `candidate evidence`, and `Signal Desk`.
- Verify:
  - `/Users/ash/.codex/skills/ubiquitous-language/scripts/ubiquitous-language.py lint --repo /Users/ash/Documents/2026/semi-stocks-2`

### PGDP-01 - Update Canonical Lane Contract

- Status: done.
- Files:
  - `docs/architecture.md`
  - `README.md`
  - `docs/artifacts/proposal-gated-data-pipeline/01_spec.md`
  - `docs/artifacts/proposal-gated-data-pipeline/04_design.md`
- Work:
  - Replace old `pending -> applied | rejected` proposal language with
    `proposed | accepted | rejected`.
  - Define `admitted universe`.
  - State that `canonical/20-data/companies/` is generated/mirrored in v1.
  - Remove "pending proposals" from main reader/source-channel framing.
- Acceptance:
  - Docs say accepted proposal state is sole admission authority.
  - Docs say `applied` is parked.
- Verify:
  - `git diff --check`

### PGDP-02 - Add Minimal Proposal Input Shape

- Status: done.
- Files:
  - `canonical/20-data/thesis-proposals/README.md`
  - `canonical/40-engine/engine/site_data.py`
- Work:
  - Create proposal lane if missing.
  - Define required fields for v1: `kind`, `schema_version`, `id`, `status`,
    company refs, evidence refs, decision metadata for accepted proposals.
  - Enforce statuses: `proposed | accepted | rejected`.
  - Reject `accepted` records without stable company ID and source/evidence
    lineage.
- Acceptance:
  - Candidate-only reset with no proposals is valid and emits no companies.
  - Invalid status fails validation.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`

### PGDP-03 - Build Admitted Universe First

- Status: done.
- Files:
  - `canonical/40-engine/engine/site_data.py`
- Work:
  - Add an admitted-universe helper rooted in accepted proposals.
  - Compute admitted company IDs, evidence/source refs, and thesis theme refs
    before building Signal Desk payload sections.
  - Change `_build_companies()` or its caller so source tickers, company packets,
    role config, and `thesis.yaml.ticker_map` cannot mint reader-visible
    companies.
  - Treat ticker/source mentions outside the admitted universe as candidate
    evidence only.
- Acceptance:
  - Every emitted company is reachable from an accepted proposal.
  - Candidate-only Baker, Leopold, SemiAnalysis, and earnings data emits zero
    companies.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`

### PGDP-04 - Remove Proposal Rows From Main Reader

- Status: done.
- Files:
  - `canonical/40-engine/engine/site_data.py`
  - `canonical/40-engine/tests/test_signal_desk_contract.py`
- Work:
  - Remove `source-channel:pending-proposals` from `_source_channel_facets()`.
  - Stop emitting proposal source docs in `_build_signal_desk_source_documents()`.
  - Stop adding `_build_proposal_rows()` to `_build_signal_desk_rows()`.
  - Remove the `proposals` table from `_build_signal_desk_tables()`.
  - Remove proposal metadata from public thesis payload if it is consumed by the
    reader.
- Acceptance:
  - Main `signal_desk.json` has no proposal rows, proposal source docs,
    proposal source channel, or proposal table view.
  - Accepted proposals still authorize admitted universe internally.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`

### PGDP-05 - Generate V1 Company Dossiers From Accepted Proposals

- Status: done.
- Files:
  - `canonical/40-engine/engine/site_data.py`
  - `canonical/20-data/companies/`
- Work:
  - Generate/mirror approved company dossier shape from accepted proposal data.
  - Persist generated dossiers under `canonical/20-data/companies/_generated/`.
  - Keep generated dossiers subordinate to accepted proposal ancestry.
  - Preserve role lookup through `canonical/20-data/company_roles.yaml` without
    letting role mapping admit companies.
- Acceptance:
  - A company dossier without accepted proposal ancestry does not emit.
  - An accepted proposal can generate the minimum company payload needed by the
    reader.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`

### PGDP-06 - Invert Contract Tests To Gate Parity

- Status: done.
- Files:
  - `canonical/40-engine/tests/test_signal_desk_contract.py`
  - `canonical/40-engine/engine/site_data.py`
- Work:
  - Replace source-position parity expectations with admitted-universe
    invariants.
  - Enforce row/source-document emission through accepted proposal
    `evidence_refs[].source_document_id`.
  - Add tests for:
    - clean reset emits zero companies/rows/graph nodes
    - candidate-only sources emit nothing
    - proposed proposal emits nothing
    - rejected proposal emits nothing
    - accepted proposal emits only admitted company closure
    - mixed source document does not leak non-admitted companies
    - role mapping and ticker_map without accepted proposal do not admit
    - graph/search/counts reconcile to emitted artifacts only
- Acceptance:
  - Tests prove no emitted artifact exists outside accepted proposal ancestry.
- Verify:
  - `uv run python canonical/40-engine/tests/test_signal_desk_contract.py`

### PGDP-07 - Audit Ticker-Map Consumers And Final Verification

- Status: done.
- Files:
  - `canonical/40-engine/engine/synthesis.py`
  - `canonical/40-engine/engine/report.py`
  - `canonical/40-engine/engine/site_data.py`
  - `canonical/site-data/*.json`
- Work:
  - Confirm `ticker_map` still serves thesis/report control-plane needs only.
  - Ensure no reader-visible Signal Desk section uses `ticker_map` as admission.
  - Ensure top-level reader-consumed site-data artifacts reconcile to accepted
    proposal ancestry.
  - Regenerate site data after all gate changes.
- Acceptance:
  - `ticker_map` without accepted proposal ancestry cannot create a reader
    company, row, source doc, graph node, search entry, or count.
  - Generated `signal_desk.json` validates.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`
  - `uv run python canonical/40-engine/tests/test_signal_desk_contract.py`
  - `python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null`
