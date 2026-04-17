# semi-stocks-2

Second-iteration semi-stocks workspace organized as a canonical propagation system.

Start here:
- Read [docs/architecture.md](docs/architecture.md) for lane ownership and propagation order.
- Read [docs/doc-contract.md](docs/doc-contract.md) for root-doc and subsystem-doc boundaries.
- Read [docs/ash.md](docs/ash.md) for a visual explainer of the repository.
- Use [AGENTS.md](AGENTS.md) or [CLAUDE.md](CLAUDE.md) for agent routing.
- For the current repo/app rollout, use [docs/artifacts/canonical-propagation-model/07_implementation-spec.md](docs/artifacts/canonical-propagation-model/07_implementation-spec.md).

High-level diagrams:
- [Current architecture + workflow](docs/diagrams/current-architecture-workflow.png)
- [Repo structure map](docs/diagrams/repo-structure-map.png)

## Top-Level Map

- `canonical/` — source-of-truth propagation lanes
- `agents/` — sidecar automation, drafts, logs, and scheduler state
- `docs/` — durable repo docs and process docs
- `tmp/` — scratch space
- `config.yaml` — shared runtime config kept at root during migration
- `pyproject.toml` / `uv.lock` — Python runtime managed with `uv`

## Canonical Stages

- `canonical/10-wiki/` — canonical knowledge workspace and ingest landing zone
- `canonical/20-data/` — structured evidence only (`sources/`, `companies/`)
- `canonical/30-thesis/thesis.yaml` — narrow control plane
- `canonical/40-engine/` — engine stage wrapper and package-safe Python module root
- `canonical/50-reports/` — canonical published artifacts

## Generated Integration Surface

- `canonical/wiki-site/` — generated Wikiwise export bundle consumed by the external app shell; not a sixth canonical stage

Use `uv run ...` for Python commands. Wiki ingest, query, and lint work should route through the repo-local `ingest-semi` skill rather than generic wiki discovery.
