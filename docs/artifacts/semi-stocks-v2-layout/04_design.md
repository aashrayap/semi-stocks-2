---
status: completed
feature: semi-stocks-v2-layout
---

# Design: semi-stocks-v2-layout

## Decision 1

**Decision**
Use explicit top-level lanes in `semi-stocks-2`:
- `research/`
- `app/`
- `agents/`
- `outputs/`
- `docs/`
- `tmp/`

**Options considered**
- Keep legacy top-level names: `wiki/`, `data/`, `src/`, `reports/`, `agents/`
- Wrap everything canonical under a single `research/` parent and normalize application/output names

**Rationale**
The current repo already has distinct concerns, but they are represented as a mix of content types and implementation details. A `research/` parent makes the canonical lane legible at a glance and lets `wiki/` and `data/` remain internal sublayers rather than competing top-level brands. `app/` and `outputs/` are clearer than `src/` and `reports/` for repo-level orientation.

**Affected files or areas**
- Repo root folder structure
- `docs/architecture.md`
- Root docs that reference folder paths

**Risks still open**
- This changes path names relative to the current repo, so later migration work will need an explicit mapping.

## Decision 2

**Decision**
Inside `research/`, preserve the existing wide-to-narrow model:
- `research/wiki/`
- `research/data/`

**Options considered**
- Collapse everything into one research tree with no distinction between authored wiki pages and structured data
- Keep `wiki/` and `data/` as separate top-level folders

**Rationale**
The current system clearly distinguishes authored synthesis from structured control-plane and company/source data. Preserving that distinction keeps the funnel intelligible while still reducing root clutter.

**Affected files or areas**
- `docs/architecture.md`
- Future migration mapping

**Risks still open**
- Some process docs currently living under `data/research/` may eventually fit better under root `docs/`; this pass only establishes the contract, not the full migration.

## Decision 3

**Decision**
Keep root markdown minimal: `README.md`, `AGENTS.md`, and `CLAUDE.md` only.

**Options considered**
- Keep `TODO.md` at root
- Allow additional root docs such as `ARCHITECTURE.md` or `MIGRATION.md`

**Rationale**
Root should answer three questions only: what this repo is, how agents should route themselves, and where deeper docs live. Architecture, process, migration, and backlog material should not compete with startup docs.

**Affected files or areas**
- Repo root
- `docs/doc-contract.md`

**Risks still open**
- If day-to-day backlog management still needs a home, it should be handled outside the root-doc contract.

## Decision 4

**Decision**
Move durable explanatory material into `docs/`, starting with:
- `docs/architecture.md`
- `docs/doc-contract.md`

**Options considered**
- Keep architecture explanation in `README.md`
- Scatter process docs across subsystem folders without a shared documentation contract

**Rationale**
The current repo stores important process and architecture material inside content folders (`data/research/`, `wiki/schema.md`) and root docs. A dedicated `docs/` home gives the repo one place for durable human-facing documentation while letting subsystem-local docs remain local when they are tightly coupled to a subsystem.

**Affected files or areas**
- `docs/`
- Root `README.md`, `AGENTS.md`, `CLAUDE.md`

**Risks still open**
- Some subsystem docs will still live near their subsystem for practical reasons; the contract needs to distinguish “global docs” from “local subsystem docs.”

## Decision 5

**Decision**
Treat `tmp/` as explicitly local scratch and non-authoritative; keep it present in the map but lightweight.

**Options considered**
- Omit `tmp/` from the high-level map
- Fold scratch work into `agents/` or `outputs/`

**Rationale**
The current repo already uses `tmp/` for transient deep-dive artifacts. Naming it explicitly reduces ambiguity and keeps scratch work from leaking into canonical or generated lanes.

**Affected files or areas**
- `docs/architecture.md`
- `.gitignore` in later execution, if needed

**Risks still open**
- Whether `tmp/` should be committed at all can be deferred.

## Repo Principles

- Control plane remains structured data, not prose.
- Canonical research and sidecar automation stay physically separated.
- Generated outputs do not live inside canonical source folders unless they are part of a subsystem’s documented generated state.
- Root docs route; deeper docs explain.
- High-level structure should be understandable without reading legacy history.
