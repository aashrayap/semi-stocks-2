---
name: ingest-semi
description: "Ingest, query, or lint the semi-stocks-2 wiki at /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki without falling back to any other 2026 wiki."
argument-hint: "[source-or-task]"
disable-model-invocation: true
---

Use this skill when the task should operate on the semi-stocks-2 wiki and must not touch `/Users/ash/Documents/2026/wiki` or `/Users/ash/Documents/2026/semi-stocks/wiki`.

## Fixed targets

- Repo root: `/Users/ash/Documents/2026/semi-stocks-2`
- Wiki root: `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`
- Schema: `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/schema.md`
- Raw sources: `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/raw`
- Thesis: `/Users/ash/Documents/2026/semi-stocks-2/canonical/30-thesis/thesis.yaml`
- Rebuild command: `uv run python ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`

## Workflow

1. If `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/schema.md` does not exist, stop and say wiki migration is not complete in `semi-stocks-2`.
2. Read `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/schema.md` before doing anything else.
3. Treat `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki` as the only wiki root for this skill. Do not use generic wiki discovery.
4. If `$ARGUMENTS` is empty, inspect `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/raw` for recently modified sources and suggest the best candidates.
5. If `$ARGUMENTS` names a file or folder without an absolute path, resolve it relative to `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/raw` first.
6. Follow the local schema and semi-stocks-specific ingest rules when they differ from generic wiki defaults.

## Ingest rules

- Never modify anything under `raw/`.
- Prefer updating existing pages in `sources/` and `concepts/` over creating duplicates.
- Preserve semi-stocks-specific sections such as `## Forward Claims`, `## Thesis Signal`, and `## Semi-stocks data` when they apply.
- When a source changes the thesis, bottleneck state, or tracked company signals, propose the corresponding patch to `canonical/30-thesis/thesis.yaml` and related `canonical/20-data/` artifacts explicitly.

## After every write

1. Update `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/index.md`.
2. Run `uv run python ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`.
3. Append the operation to `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/log.md`.

ARGUMENTS: $ARGUMENTS
