# Agent Instructions

## Human Response Contract

- For non-trivial work, final responses should return a concise human-readable packet: `This Session Focus`, `Result`, `Visual`, `Gate`, `Ledger`, one or more concrete `Next Actions`, and `Details` links.
- `This Session Focus` is the first slot. Keep it to 1-2 short lines that remind Ash why this session started and where the work currently stands: first line for purpose, optional second line for current state.
- `Visual` is always a slot. For workflow, architecture, planning, review, decision, or multi-artifact work, link an existing diagram or create/render one. For narrow mechanical work, say why no visual was useful.
- Use `Ledger` when the session has multiple user requests, corrections, or follow-ups. Track `Captured`, `Done`, `Not Done`, and `Parked` so nothing disappears into chat.
- Treat chat as the receipt; create durable artifacts only when the work must survive beyond chat, be linked from roadmap/PR/docs, be resumed by another session, or when multiple artifacts need a landing page.
- Before final response, map the latest user requests to the packet. Every request should be done, parked, or called out as not done.
- Keep this concise and runtime-portable.

`semi-stocks-2` is a canonical propagation repo. Keep the root map, skill routing, and write boundaries explicit.

## Start Here

- Read [README.md](README.md) for the repo map.
- Read [docs/architecture.md](docs/architecture.md) for canonical lane ownership.
- Read [docs/doc-contract.md](docs/doc-contract.md) before adding docs.

## Authority Model

Canonical flow:

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts|outputs -> canonical/20-data/sources|thesis-proposals|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

Write ownership:

- `canonical/10-wiki/` owns authored wiki knowledge and generated wiki metadata.
- `canonical/20-data/` owns structured evidence, authored thesis proposals, and generated post-gate company dossiers.
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

## Progressive Disclosure

- Shared language: read `docs/UBIQUITOUS_LANGUAGE.md` when planning, implementing, or reviewing domain terminology.
