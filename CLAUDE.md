# semi-stocks-2

Use this repo as a canonical propagation system for semi-stocks. Codex will review your output once you are done.

## Routing

- Repo map: [README.md](README.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Root-doc policy: [docs/doc-contract.md](docs/doc-contract.md)
- Wiki ingest/query/lint: [.claude/skills/ingest-semi/SKILL.md](.claude/skills/ingest-semi/SKILL.md)

## Canonical Flow

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts -> canonical/20-data/sources|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

## Working Rules

- `canonical/10-wiki/` and `canonical/20-data/` are the canonical research lanes.
- `canonical/30-thesis/thesis.yaml` is the control plane.
- `canonical/40-engine/` and `canonical/50-reports/` stay separate.
- `canonical/wiki-site/` is a generated integration/export bundle for the external Wikiwise app shell, not a canonical stage.
- `agents/` is sidecar-only by default.
- Durable cross-lane process docs live under `docs/process/`.
- Use `uv run ...` for Python execution.

<important if="editing wiki content">
Use the local `ingest-semi` skill. If `canonical/10-wiki/schema.md` is missing, stop and say wiki migration is not complete. Never edit `canonical/10-wiki/raw/`. After wiki writes, update `canonical/10-wiki/index.md` and `canonical/10-wiki/log.md`.
</important>

<important if="touching agent automation or scheduled ingest">
Read canonical lanes freely, but keep writes under `agents/` unless promoting reviewed changes intentionally.
</important>

<important if="continuing the repo/app rollout">
Use `docs/artifacts/canonical-propagation-model/07_implementation-spec.md` as the live implementation contract. Use `04_design.md` for canonical lane ownership. Treat `05_tasks.md` and `06_handoff.md` as historical migration records.
</important>
