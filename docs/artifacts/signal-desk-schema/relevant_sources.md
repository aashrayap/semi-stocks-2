---
status: active
feature: signal-desk-schema
---

# Relevant Sources

This file is the durable source pointer set for Signal Desk schema and UI work.

It lives inside this artifact set instead of repo root because `docs/doc-contract.md` keeps root Markdown limited to `README.md`, `AGENTS.md`, and `CLAUDE.md`.

## Justin Wang Compute Site

### Live site

- https://compute.jstwng.com/

### UI repository

- Repo: https://github.com/jstwng/compute-site
- Inspected commit: `1f90a873c44ceea03240ccb5658e115dbc40e6c6`
- License metadata: `MIT` in `package.json`

Key source files:

- `src/App.jsx` — top-level state, toolbar wiring, graph/table/profile composition.
- `src/styles.css` — global theme variables and dark-mode palette.
- `src/app.css` — page layout, header, graph block, responsive behavior.
- `src/components/ComputeDealMap/Toolbar.jsx` — `Trace`, `Timeline`, `Cluster`, search controls.
- `src/components/ComputeDealMap/Dropdown.jsx` — compact dropdown and mobile behavior.
- `src/components/ComputeDealMap/Graph.jsx` — graph layout, focus, hover, edge/node interaction.
- `src/components/ComputeDealMap/logic.js` — filtering, trace path traversal, value-chain rank.
- `src/components/ComputeDealMap/FilterBar.jsx` — table-level deal/category filtering.
- `src/components/ComputeDealMap/ProfilePanel.jsx` — selected company/edge panel.
- `src/components/ComputeDealMap/styles.module.css` — module styles for graph, toolbar, profile panel, table.
- `scripts/vite-plugin-deal-data.mjs` — build-time fetch of release artifacts.

### Data repository

- Repo: https://github.com/jstwng/compute-deal-map-data
- Inspected commit: `e5c0e740b2f34ee56b6073e2e237b2dddc0c564d`
- Latest release inspected earlier: `2026.04.17-1`

Key source files:

- `companies.yml` — company node source.
- `deals/*.yml` — transaction edge source.
- `schema/company.schema.json` — company source schema.
- `schema/deal.schema.json` — deal source schema.
- `scripts/build.js` — emitted artifact builder.
- `scripts/validate.js` — source validation.

Observed release shape:

- 81 companies.
- 257 deals.
- Company fields: `slug`, `name`, `ticker`, `category`, `subline`, `acquired`.
- Deal fields: `id`, `source_slug/name`, `target_slug/name`, `deal_type`, `value_billions`, `value_display`, `date`, `date_display`, `description`, `source_url`.
- Company categories: `ai_lab`, `chip_designer`, `data_center`, `equipment`, `foundry`, `hyperscaler`, `investor`, `memory`, `neocloud`, `networking`, `packaging`, `power`, `server_oem`.
- Deal types: `cloud_capacity`, `custom_asic`, `equipment_supply`, `equity_investment`, `funding_round`, `gpu_purchase`, `m_and_a`, `power_ppa`.

## Semi-Stocks Canonical Contract

Core docs:

- [README.md](../../../README.md)
- [docs/architecture.md](../../architecture.md)
- [docs/doc-contract.md](../../doc-contract.md)
- [canonical propagation implementation spec](../canonical-propagation-model/07_implementation-spec.md)

Current visual-layer artifacts:

- [lightweight visual layer research](../lightweight-visual-layer/03_research.md)
- [lightweight visual layer design](../lightweight-visual-layer/04_design.md)
- [site-data contract](../lightweight-visual-layer/site-data-contract.md)

Current generated app data:

- [canonical/site-data/build.json](../../../canonical/site-data/build.json)
- [canonical/site-data/schema.json](../../../canonical/site-data/schema.json)
- [canonical/site-data/companies.json](../../../canonical/site-data/companies.json)
- [canonical/site-data/signals.json](../../../canonical/site-data/signals.json)
- [canonical/site-data/claims.json](../../../canonical/site-data/claims.json)
- [canonical/site-data/thesis.json](../../../canonical/site-data/thesis.json)
- [canonical/site-data/edges.json](../../../canonical/site-data/edges.json)
- [canonical/site-data/graph.json](../../../canonical/site-data/graph.json)

Current generator files:

- [canonical/40-engine/site_data.py](../../../canonical/40-engine/site_data.py)
- [canonical/40-engine/engine/site_data.py](../../../canonical/40-engine/engine/site_data.py)
- [canonical/40-engine/engine/paths.py](../../../canonical/40-engine/engine/paths.py)

Canonical source lanes:

- [canonical/10-wiki/schema.md](../../../canonical/10-wiki/schema.md)
- [canonical/30-thesis/thesis.yaml](../../../canonical/30-thesis/thesis.yaml)
- `canonical/20-data/companies/**`
- `canonical/20-data/sources/**`

Sidecar prediction sources:

- [agents/autoagent/program.md](../../../agents/autoagent/program.md)
- `agents/state/predictions/*.yaml`

## Local Artifact Set

- [00_summary.md](00_summary.md)
- [03_research.md](03_research.md)
- [04_design.md](04_design.md)
- [06_justin_mapping.md](06_justin_mapping.md)
- [07_ui_replication_notes.md](07_ui_replication_notes.md)
- [08_top_controls_iteration.md](08_top_controls_iteration.md)
- [09_final_spec.md](09_final_spec.md)
