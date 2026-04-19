# semi-stocks-2

Use this repo as a canonical propagation system. Keep root map, skill routing, and write boundaries explicit.

## Human Response Contract

- For non-trivial work, final responses should return a concise
  human-readable packet: `This Session Focus`, `Result`, `Visual`, `Gate`,
  `Ledger`, concrete `Next Actions`, and `Details` links.
- `This Session Focus` is the first slot. Keep it to 1-2 short lines that
  remind Ash why this session started and where the work currently stands:
  first line for purpose, optional second line for current state.
- `Visual` is always a slot. For workflow, architecture, planning, review,
  decision, or multi-artifact work, link an existing diagram or create/render
  one. For narrow mechanical work, say why no visual was useful.
- Use `Ledger` when the session has multiple user requests, corrections, or
  follow-ups. Track `Captured`, `Done`, `Not Done`, and `Parked`.
- Treat chat as the receipt. Create durable artifacts only when the work must
  survive beyond chat, be linked from roadmap/PR/docs, be resumed by another
  session, or when multiple artifacts need a landing page.
- Before final response, map the latest user requests to the packet. Every
  request should be done, parked, or called out as not done.
- Keep this concise and runtime-portable.

## Runtime Preference

- Codex is Ash's strongly preferred runtime right now.
- Keep repo instructions portable across Codex and Claude, but bias day-to-day
  workflow and setup decisions toward Codex unless the user asks otherwise.

## Start Here

- Repo map: [README.md](README.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Doc contract: [docs/doc-contract.md](docs/doc-contract.md)
- Current repo/Wikiwise contract: [docs/artifacts/canonical-propagation-model/07_implementation-spec.md](docs/artifacts/canonical-propagation-model/07_implementation-spec.md)
- Wiki ingest/query/lint skill: [.claude/skills/ingest-semi/SKILL.md](.claude/skills/ingest-semi/SKILL.md)

## Authority Model

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts|outputs -> canonical/20-data/sources|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

- `canonical/10-wiki/` owns authored wiki knowledge and generated wiki metadata.
- `canonical/20-data/` owns structured evidence only.
- `canonical/30-thesis/thesis.yaml` owns the thesis control plane.
- `canonical/40-engine/` owns synthesis and render code.
- `canonical/50-reports/` owns canonical reports.
- `canonical/wiki-site/` is generated Wikiwise integration output, not a canonical stage.
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
- Wikiwise source checkout is separate: `/Users/ash/Documents/2026/wikiwise`.
- Installed Wikiwise app is `/Applications/Wikiwise.app`; it consumes `canonical/wiki-site/`.

<important if="editing wiki content">
Use the local `ingest-semi` skill. If `canonical/10-wiki/schema.md` is missing, stop and say wiki migration is not complete. Read the schema first. Never edit `canonical/10-wiki/raw/`. After wiki writes, update `canonical/10-wiki/index.md`, rebuild generated state, and append to `canonical/10-wiki/log.md`.
</important>

<important if="touching agent automation or scheduled ingest">
Read canonical lanes freely, but keep writes under `agents/` unless promoting reviewed changes intentionally.
</important>

<important if="adding or moving docs">
Root docs stay minimal. Put repo-wide process docs under `docs/process/`; keep subsystem-local docs near their owner.
</important>
