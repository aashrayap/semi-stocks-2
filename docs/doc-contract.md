# Doc Contract

## Root Docs

Allowed at repo root:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`

These files have narrow jobs:

- `README.md` explains what the repo is and how the top-level lanes fit together.
- `AGENTS.md` gives always-on routing and repo-behavior rules for agents.
- `CLAUDE.md` gives the equivalent thin router for Claude-style workflows.

Root docs should stay short. They are not the place for long-form thesis writing, backlog tracking, migration notes, or detailed process documentation.

## `docs/`

Use `docs/` for durable, repo-wide documentation such as:

- architecture and lane ownership
- documentation contracts
- migration planning
- operating principles that are broader than one subsystem

Initial global docs:

- `docs/architecture.md`
- `docs/doc-contract.md`

## Subsystem-Local Docs

A document can live near its subsystem instead of under `docs/` when it is tightly coupled to that subsystem's internal rules or generated state.

Examples from the legacy repo pattern:

- wiki schema docs near the wiki
- research-pipeline docs near research data

The rule is simple: global docs go in `docs/`; subsystem-internal docs stay local.

## Explicitly Not Root Docs

Do not add these at repo root:

- backlog or session-state files like `TODO.md`
- long-form thesis or source explainers
- architecture deep-dives
- migration plans
- generated reports

## Current Migration Stance

This contract is established before broader file migration. Docs may be rewritten or migrated into `docs/` earlier than code and research content because the doc boundary is part of the structure itself.
