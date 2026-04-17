---
name: ingest-semi
description: Ingest, query, or lint only the semi-stocks-2 canonical wiki at /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki.
---

# ingest-semi

Repo-local skill for `semi-stocks-2` wiki work. Do not fall back to any other wiki checkout.

## Composes With

- Parent: user asks to ingest, query, lint, or update semi-stocks wiki knowledge.
- Reads from: `canonical/10-wiki/`, `canonical/20-data/`, `canonical/30-thesis/thesis.yaml`, and repo docs.
- Writes to: `canonical/10-wiki/sources/`, `canonical/10-wiki/concepts/`, `canonical/10-wiki/outputs/`, generated wiki state, and explicit proposal files under `canonical/20-data/thesis-proposals/` when needed.
- Never writes to: `canonical/10-wiki/raw/`.
- Hands off through: updated wiki pages, regenerated metadata, `index.md`, `log.md`, and explicit thesis/data proposals.

## Fixed Targets

- Repo root: `/Users/ash/Documents/2026/semi-stocks-2`
- Wiki root: `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`
- Schema: `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/schema.md`
- Raw sources: `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki/raw`
- Thesis: `/Users/ash/Documents/2026/semi-stocks-2/canonical/30-thesis/thesis.yaml`
- Rebuild: `uv run python ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`

## Required Flow

1. Stop if `canonical/10-wiki/schema.md` is missing.
2. Read `canonical/10-wiki/schema.md` before wiki edits or lint decisions.
3. Treat `canonical/10-wiki/` as the only wiki root.
4. If the user names a relative file or folder, resolve it under `canonical/10-wiki/raw/` first.
5. Prefer updating existing `sources/`, `concepts/`, or `outputs/` pages over creating duplicates.
6. Preserve semi-stocks sections when applicable: `## Forward Claims`, `## Thesis Signal`, `## Semi-stocks data`, `## See Also`.
7. If a source changes thesis, bottleneck status, or company signals, create or update a structured proposal under `canonical/20-data/thesis-proposals/`; do not silently edit thesis state.
8. After every wiki write, update `index.md`, run the rebuild command, and append to `log.md`.

## Query Mode

- Start at `canonical/10-wiki/index.md`.
- Follow wikilinks through `concepts/`, `sources/`, and `outputs/`.
- Use `canonical/20-data/` only when structured evidence is needed.
- Use `canonical/30-thesis/thesis.yaml` only for control-plane conclusions.

## Lint Mode

- Run the rebuild command before judging generated metadata.
- Treat `_index.json`, `_backlinks.json`, and `_lint.json` as generated state.
- Fix dead links by updating wiki links or pages, not by editing generated JSON directly.
