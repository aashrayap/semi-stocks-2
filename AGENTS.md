# Agent Instructions

`semi-stocks-2` is a canonical propagation repo. Keep the root map, skill routing, and write boundaries explicit.

## Start Here

- Read [README.md](README.md) for the repo map.
- Read [docs/architecture.md](docs/architecture.md) for canonical lane ownership.
- Read [docs/doc-contract.md](docs/doc-contract.md) before adding docs.

## Authority Model

Canonical flow:

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts|outputs -> canonical/20-data/sources|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

Write ownership:

- `canonical/10-wiki/` owns authored wiki knowledge and generated wiki metadata.
- `canonical/20-data/` owns structured evidence only.
- `canonical/30-thesis/thesis.yaml` owns the narrow thesis control plane.
- `canonical/40-engine/` owns synthesis and render code.
- `canonical/50-reports/` owns canonical published reports.
- `canonical/site-data/` is generated app data for repo-owned web readers, not a canonical stage.
- `canonical/site-reader/` is repo-owned web reader source that consumes generated site data, not a canonical stage.
- `agents/` is sidecar-only unless the user explicitly asks to promote changes.
- `tmp/` is scratch only.

## Skill Composition

- Use repo-local `ingest-semi` for wiki ingest, query, or lint work: [.codex/skills/ingest-semi/SKILL.md](.codex/skills/ingest-semi/SKILL.md).
- Use the Excalidraw diagram skill for durable diagrams. Store editable `.excalidraw` and rendered `.png` under `docs/diagrams/` unless told otherwise.
- Use review/spec skills only when named or when the user asks for that workflow.
- Prefer the smallest applicable skill. Do not stack skills unless each one owns a distinct part of the task.
- A repo-local skill must state fixed targets, read/write boundaries, runtime commands, verification, and handoff output.

## Runtime

- Use `uv run ...` for Python.
- Use `uv run python canonical/40-engine/report.py` for canonical report generation.
- The package-safe engine module root is `canonical/40-engine/engine/`.
- Keep `config.yaml` at repo root unless the user explicitly asks to move it.

## Wiki Writes

- Stop if `canonical/10-wiki/schema.md` is missing.
- Read `canonical/10-wiki/schema.md` before editing wiki pages.
- Never modify `canonical/10-wiki/raw/`.
- After wiki writes, update `canonical/10-wiki/index.md`, rebuild generated state, and append to `canonical/10-wiki/log.md`.

## Documentation

- Root docs stay minimal: `README.md`, `AGENTS.md`, `CLAUDE.md`.
- Repo-wide process docs live under `docs/process/`.
- Subsystem-local docs stay near their owner.
- Historical migration docs remain under `docs/artifacts/`; do not use them as current runtime authority unless current root docs point there.
