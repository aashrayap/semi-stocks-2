# Ubiquitous Language

## Purpose

Keep humans, agents, docs, and implementation aligned on the semi-stocks-2
canonical pipeline, proposal gate, and reader surface terms.

## Terms

| Term | Definition | Use When | Compress / Aliases | Avoid | Evidence |
|------|------------|----------|--------------------|-------|----------|
| Canonical propagation repo | Repo organized as staged source-of-truth lanes that flow from wiki inputs through data, thesis, engine, reports, and reader data. | Describing the whole repo shape. | canonical pipeline, propagation system | app repo, random workspace | `AGENTS.md` Authority Model; `README.md` Current State |
| Canonical lane | A filesystem ownership lane with a clear authority boundary. | Talking about `canonical/10-wiki/`, `canonical/20-data/`, `canonical/30-thesis/`, `canonical/40-engine/`, or `canonical/50-reports/`. | stage, authority layer | folder, bucket | `docs/architecture.md` Root Lanes |
| Wiki lane | `canonical/10-wiki/`; owns raw source material, source-backed synthesis, concepts, outputs, index, and wiki metadata. | Discussing ingest, query, wiki pages, or source-backed synthesis. | canonical wiki | data layer | `AGENTS.md` Wiki Writes; `canonical/10-wiki/schema.md` |
| Candidate evidence | Broad pre-gate structured evidence that may mention many companies but does not imply reader admission. | Describing `canonical/20-data/sources/**` or source-derived signals before human decision. | source evidence, candidate data | approved data, reader data | `docs/artifacts/proposal-gated-data-pipeline/04_design.md` |
| Thesis proposal | Authored decision record under `canonical/20-data/thesis-proposals/` with `proposed`, `accepted`, or `rejected` state. | Capturing a thesis/company admission decision for Codex/human review. | proposal record, decision record | pending patch, applied patch | `canonical/20-data/thesis-proposals/README.md`; `docs/artifacts/proposal-gated-data-pipeline/04_design.md` |
| Human gate | The human/Codex decision step that changes a thesis proposal state. | Explaining how candidate evidence becomes eligible for the reader. | approval gate, decision gate | automatic promotion | `README.md` Human Loop; `docs/artifacts/proposal-gated-data-pipeline/01_spec.md` |
| Admission authority | The sole source that can make a company or evidence reader-visible. In this phase, accepted thesis proposal state. | Reviewing leakage risk or reader inclusion rules. | gate authority | ticker map, role map, source mention | `docs/artifacts/proposal-gated-data-pipeline/04_design.md` |
| Accepted proposal ancestry | The trace from an emitted reader artifact back to at least one accepted thesis proposal. | Validating a company, row, source document, count, search facet, or graph artifact. | accepted ancestry, proposal ancestry | loose provenance | `docs/artifacts/proposal-gated-data-pipeline/05_tasks.md` |
| Admitted universe | The accepted proposal-derived closure of companies, evidence, rows, source documents, counts, search facets, and graph artifacts the engine may emit. | Naming the reader-visible set built before Signal Desk emission. | accepted closure, reader universe | acceptable universe, all source tickers | `docs/artifacts/proposal-gated-data-pipeline/01_spec.md`; `docs/artifacts/proposal-gated-data-pipeline/04_design.md` |
| Company dossier | Company-level structured model. In v1 of the gate work, generated/mirrored from accepted proposals and persisted under `canonical/20-data/companies/_generated/` instead of authored as a second manual truth surface. | Discussing post-gate company data after admission. | approved company model | candidate company, source-mentioned company | `docs/artifacts/proposal-gated-data-pipeline/04_design.md` |
| Thesis control plane | `canonical/30-thesis/thesis.yaml`; narrow machine-readable thesis state, not a company admission plane. | Discussing cascade status, ticker metadata, or report synthesis control. | thesis.yaml | admission map | `docs/architecture.md` Canonical Stage Notes |
| Signal Desk | Main generated reader contract and UI surface for evidence, companies, filters, graph, and tables. | Discussing `canonical/site-data/signal_desk.json` or the reader surface. | reader feed, main reader | proposal review queue | `README.md` Signal Desk Surface |
| Reader | `canonical/site-reader/`; repo-owned web reader that consumes generated site data and must not become source truth. | Discussing UI behavior or app consumption boundaries. | web reader, reader surface | canonical data | `README.md` Generated App Surfaces |
| Generated app data | `canonical/site-data/**`; generated JSON contracts derived by the engine for readers and review surfaces. | Discussing rebuildable data outputs. | site data, generated JSON | canonical source, authored data | `docs/architecture.md` canonical/site-data |
| Source channel | Provenance facet for emitted evidence, such as Baker, Leopold, SemiAnalysis, company earnings, or thesis stage. | Filtering or explaining where a reader row/source document came from. | provenance channel | admission channel | `README.md` Control Guide |
| Contextual evidence graph | Signal Desk graph whose edges mean shared evidence only, not causality or value-chain flow. | Explaining graph semantics. | Signal Desk graph | Trace, supplier graph, money flow | `README.md` Parked |
| Trace | Parked future typed relationship feature requiring explicit directional relationship edges. | Explaining what graph lines do not mean today. | typed relationship path | current graph edge | `README.md` Parked |
| Sidecar automation | `agents/`; automation that may read canonical state but writes only sidecar state unless promoted. | Discussing schedulers, generated reports, logs, or experiments under `agents/`. | sidecar lane | canonical source | `AGENTS.md` Authority Model; `docs/architecture.md` agents |

## Open Language Questions

| Question | Why It Matters | Evidence Needed |
|----------|----------------|-----------------|
| Should an internal proposal review payload get a named surface later? | If pending proposals need a UI, it must stay separate from main Signal Desk. | Future product decision after main gate lands. |

## Refresh Notes

- Generated by: `ubiquitous-language`
- Last refreshed: 2026-04-24
- Default artifact path: `docs/UBIQUITOUS_LANGUAGE.md`
- Source inventory: `/Users/ash/.codex/skills/ubiquitous-language/scripts/ubiquitous-language.py inventory --repo /Users/ash/Documents/2026/semi-stocks-2`
- Repo root at generation: `/Users/ash/Documents/2026/semi-stocks-2`
