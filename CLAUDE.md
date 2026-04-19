# semi-stocks-2

Use this repo as a canonical propagation system. Keep root map, skill routing, and write boundaries explicit.

## Start Here

- Repo map: [README.md](README.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Doc contract: [docs/doc-contract.md](docs/doc-contract.md)
- Active site-data/site-reader contract: [docs/artifacts/lightweight-visual-layer/site-data-contract.md](docs/artifacts/lightweight-visual-layer/site-data-contract.md)
- Wiki ingest/query/lint skill: [.claude/skills/ingest-semi/SKILL.md](.claude/skills/ingest-semi/SKILL.md)

## Authority Model

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts|outputs -> canonical/20-data/sources|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

- `canonical/10-wiki/` owns authored wiki knowledge and generated wiki metadata.
- `canonical/20-data/` owns structured evidence only.
- `canonical/30-thesis/thesis.yaml` owns the thesis control plane.
- `canonical/40-engine/` owns synthesis and render code.
- `canonical/50-reports/` owns canonical reports.
- `canonical/site-data/` is generated reader input, not a canonical stage.
- `canonical/site-reader/` is the local presentation layer for that input.
- `agents/` is sidecar-only unless the user explicitly asks for promotion.
- `tmp/` is scratch only.

## Skill Composition

- Use repo-local `ingest-semi` for wiki ingest, query, or lint work.
- Use the Excalidraw diagram workflow for durable diagrams; store `.excalidraw` and `.png` under `docs/diagrams/` unless told otherwise.
- Use review/spec workflows only when named or when the user asks for them.
- Prefer the smallest applicable skill. Stack skills only when each one owns a distinct part of the task.
- Repo-local skills should state fixed targets, read/write boundaries, runtime commands, verification, and handoff output.

## Runtime

- Use `uv run ...` for Python.
- Canonical report command: `uv run python canonical/40-engine/report.py`.
- Engine module root: `canonical/40-engine/engine/`.
- Keep `config.yaml` at repo root unless explicitly asked to move it.

<important if="editing wiki content">
Use the local `ingest-semi` skill. If `canonical/10-wiki/schema.md` is missing, stop and say wiki migration is not complete. Read the schema first. Never edit `canonical/10-wiki/raw/`. After wiki writes, update `canonical/10-wiki/index.md`, rebuild generated state, and append to `canonical/10-wiki/log.md`.
</important>

<important if="touching agent automation or scheduled ingest">
Read canonical lanes freely, but keep writes under `agents/` unless promoting reviewed changes intentionally.
</important>

<important if="adding or moving docs">
Root docs stay minimal. Put repo-wide process docs under `docs/process/`; keep subsystem-local docs near their owner.
</important>
