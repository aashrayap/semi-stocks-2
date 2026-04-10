# Agent Instructions

semi-stocks v2 is organized by lane, not by legacy implementation details.

## Start Here

- Read [README.md](README.md) for the repo map.
- Read [docs/architecture.md](docs/architecture.md) for folder ownership.
- Read [docs/doc-contract.md](docs/doc-contract.md) before adding or expanding root docs.

## Repo Contract

- `research/` is the canonical knowledge lane.
- `app/` contains runtime and synthesis code.
- `agents/` is sidecar-only and non-canonical by default.
- `outputs/` holds generated artifacts, not source-of-truth inputs.
- `tmp/` is scratch space.

## Documentation Rules

- Keep root docs minimal: `README.md`, `AGENTS.md`, `CLAUDE.md`.
- Put durable architecture and process docs under `docs/` unless they are tightly coupled to a subsystem.
- Do not recreate root clutter by adding backlog or long-form thesis docs at repo root.

## Current State

- This repo is a clean v2 scaffold.
- Legacy-content migration is intentionally not part of the current setup pass.

