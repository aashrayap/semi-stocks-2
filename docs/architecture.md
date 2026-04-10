# Architecture

## Goal

`semi-stocks-2` is the second-iteration repo shape for semi-stocks. The point of this layout is to make authority boundaries obvious at root.

## Lanes

### `research/`

Canonical knowledge lane.

- `research/wiki/` — authored synthesis, raw-source handling, and related wiki state
- `research/data/` — structured thesis/control-plane data and other canonical structured artifacts

This lane replaces the old pattern where `wiki/` and `data/` competed as separate top-level concerns.

### `app/`

Runtime code for synthesis, reports, and other canonical application behavior.

This is the future home for code that previously lived under `src/`.

### `agents/`

Sidecar automation, experiments, drafts, logs, and other non-canonical agent outputs.

This lane may read canonical artifacts but should not become a second source of truth.

### `outputs/`

Generated artifacts intended for consumption, review, or export.

This is the future home for top-level generated reports and similar outputs that should stay separate from authored source material.

### `docs/`

Durable human-facing docs about repo-wide architecture, contracts, and future migration notes.

Global docs belong here unless they are tightly coupled to a specific subsystem.

### `tmp/`

Scratch space for local working files and transient artifacts.

## Principles

- Control-plane state should live in structured data, not prose.
- Canonical research and sidecar automation should be physically separate.
- Generated artifacts should not be mistaken for canonical inputs.
- Root should show lanes, not history.

## Non-Goals For This Pass

- No detailed migration of legacy research, code, or reports
- No deep subfolder design beyond what is needed to make the lane model clear
- No attempt to preserve every old top-level name in v2

