---
status: final-mvp-spec-ready
feature: signal-desk-schema
updated: 2026-04-19
---

# Signal Desk Schema

## Purpose

Define the minimum app schema for the Signal Desk surface, with emphasis on keeping the UI simple while aligning the app-facing contract with the repo's wide-to-narrow canonical pipeline.

## Current State

Research, UI-control iteration, original final spec, readiness challenge, Justin
surface comparison, Research Pro handoffs, Research Pro decision merge, and
final MVP spec are complete. No implementation has been executed.

## Artifacts

- [01_spec.md](01_spec.md)
- [02_questions.md](02_questions.md)
- [03_research.md](03_research.md)
- [04_design.md](04_design.md)
- [05_tasks.md](05_tasks.md)
- [06_justin_mapping.md](06_justin_mapping.md)
- [07_ui_replication_notes.md](07_ui_replication_notes.md)
- [08_top_controls_iteration.md](08_top_controls_iteration.md)
- [09_final_spec.md](09_final_spec.md)
- [10_readiness_challenge.md](10_readiness_challenge.md)
- [11_justin_surface_compare.md](11_justin_surface_compare.md)
- [12_research_pro_brief.md](12_research_pro_brief.md)
- [13_research_pro_decisions.md](13_research_pro_decisions.md)
- [14_final_spec_v0_2.md](14_final_spec_v0_2.md)
- [15_research_pro_finalization_prompt.md](15_research_pro_finalization_prompt.md)
- [16_research_pro_final_decisions.md](16_research_pro_final_decisions.md)
- [17_final_mvp_spec.md](17_final_mvp_spec.md)
- [18_current_app_state_readup.md](18_current_app_state_readup.md)
- [relevant_sources.md](relevant_sources.md)
- [Signal Desk readiness shifts](../../diagrams/signal-desk-readiness-shifts.png)
- [Signal Desk final build shape](../../diagrams/signal-desk-final-spec-flow.png)
- [Signal Desk minimum schema diagram](../../diagrams/signal-desk-schema-minimum.png)

## Initial Framing

- The first design target should be a Signal Desk app view model generated from `canonical/site-data/`, not a new canonical stage.
- "Review" is not a first-class source entity today. Treat it as UI/review state or a derived count over already-curated signals.
- "Prediction" is overloaded. In canonical `site-data`, the real object is a forward `claim` / proof gate. In `agents/`, prediction YAMLs are sidecar pre-earnings forecasts.

## Locked Recommendation

Build the final MVP data contract first. The repo is ready for
`canonical/site-data/signal_desk.json`, not ready for UI-first implementation.

Implementation target: [17_final_mvp_spec.md](17_final_mvp_spec.md).

Final MVP corrections now accepted:

- `Signal Cluster` -> `Source Channel`
- `Company Category` -> `Company Role`
- add first-class `source_documents`
- use one unified `rows` collection with row variants
- use `tables.views.*` as row-ID indexes, not duplicated payloads
- first graph is contextual, undirected, and evidence-backed
- emitted graph support families are only `co_position` and `shared_signal`
- MVP is a web-only reader, similar to Justin's web app
- mobile is out of MVP scope
- add explicit `canonical/20-data/company_roles.yaml`
- include non-core source-fidelity roles for raw 13F preservation (`software-services`, `market-basket`)
- Trace is parked until a separate typed value-chain relationship dataset exists

Trace remains parked until a separate typed `relationship_edges` dataset exists.
