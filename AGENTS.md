# Agent Instructions

semi-stocks-2 is organized around a canonical propagation model.

## Start Here

- Read [README.md](README.md) for the repo map.
- Read [docs/architecture.md](docs/architecture.md) for lane ownership and propagation order.
- Read [docs/doc-contract.md](docs/doc-contract.md) before adding or expanding docs.
- For wiki ingest, query, or lint work, use the repo-local `ingest-semi` skill at [.codex/skills/ingest-semi/SKILL.md](.codex/skills/ingest-semi/SKILL.md).

## Canonical Flow

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts -> canonical/20-data/sources|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

`agents/` may read canonical state broadly but should write sidecar state only under `agents/` unless the user explicitly asks for promotion.

## Lane Rules

- `canonical/10-wiki/` is the canonical knowledge workspace and ingest landing zone.
- `canonical/20-data/` is structured evidence only. Do not reintroduce thesis or process-doc sprawl there.
- `canonical/30-thesis/thesis.yaml` is the narrow control plane.
- `canonical/40-engine/` contains canonical synthesis and render code.
- `canonical/50-reports/` is for canonical published artifacts and stays separate from `canonical/10-wiki/outputs/`.
- `canonical/wiki-site/` is a generated integration/export bundle for the external Wikiwise app shell, not a sixth canonical stage.
- `agents/` is sidecar-only by default.
- `tmp/` is scratch only.

## Wiki Rules

- If `canonical/10-wiki/schema.md` is missing, stop and say wiki migration is not complete instead of inventing placeholder wiki state.
- Read `canonical/10-wiki/schema.md` before any wiki edit once it exists.
- Never modify `canonical/10-wiki/raw/`.
- After any wiki write, update `canonical/10-wiki/index.md` and `canonical/10-wiki/log.md`.

## Runtime Rules

- Use `uv run ...` for Python execution.
- The engine stage is `canonical/40-engine/`, with the package-safe Python module root under `canonical/40-engine/engine/`.
- Keep `config.yaml` at repo root unless the user explicitly asks to relocate runtime config.

## Documentation Rules

- Keep root docs minimal: `README.md`, `AGENTS.md`, `CLAUDE.md`.
- Put cross-lane operational docs under `docs/process/`.
- Keep subsystem-local docs near their owner when they are tightly coupled to that subsystem.

## Current State

- Use [docs/artifacts/canonical-propagation-model/07_implementation-spec.md](docs/artifacts/canonical-propagation-model/07_implementation-spec.md) as the working repo/app rollout contract.
- Use [docs/artifacts/canonical-propagation-model/04_design.md](docs/artifacts/canonical-propagation-model/04_design.md) as the canonical lane baseline.
- Treat [docs/artifacts/canonical-propagation-model/05_tasks.md](docs/artifacts/canonical-propagation-model/05_tasks.md) and [docs/artifacts/canonical-propagation-model/06_handoff.md](docs/artifacts/canonical-propagation-model/06_handoff.md) as historical migration records.
- The earlier scaffold and flat-root lane layouts are obsolete.
