# Doc Contract

## Root Docs

Allowed root docs:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`

These files have narrow jobs:

- `README.md` explains the repo and the canonical root map.
- `AGENTS.md` gives always-on routing and repo-behavior rules for Codex-style agents.
- `CLAUDE.md` gives the equivalent thin router for Claude-style workflows.

Root docs stay short. They are not the place for long-form thesis writing, backlog tracking, migration plans, or deep operational process notes.

## Canonical Root Entries

The canonical non-doc root entries are:

- `canonical/`
- `agents/`
- `docs/`
- `tmp/`
- `config.yaml`
- `pyproject.toml`
- `uv.lock`

These are filesystem lanes, runtime config, or tool metadata, not narrative documentation.

## `docs/`

Use `docs/` for durable, repo-wide documentation such as:

- architecture and lane ownership
- documentation contracts
- migration artifacts and restart packages
- cross-lane process docs under `docs/process/`

## Subsystem-Local Docs

A document should live near its subsystem when it is tightly coupled to that subsystem's rules or generated state.

Examples:

- `canonical/10-wiki/schema.md` stays under the wiki lane
- agent-only operational notes may live under `agents/`
- engine-internal notes may live under `canonical/40-engine/`

The rule is simple: repo-wide docs go in `docs/`; subsystem-internal docs stay local.

## Explicitly Not Root Docs

Do not add these at repo root:

- backlog or session-state files like `TODO.md`
- long-form thesis prose or source explainers
- architecture deep-dives
- process docs that belong in `docs/process/`
- migration plans outside `docs/`
- generated reports

## Migration Note

This contract replaces the obsolete `research/` + `app/` + `outputs/` scaffold and the intermediate flat-root `wiki/` + `data/` layout. Active docs should point at the canonical stage lanes.
