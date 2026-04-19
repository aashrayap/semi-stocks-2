---
status: ready-for-e2e-data-slice
feature: lightweight-visual-layer
updated: 2026-04-19
---

# Lightweight Visual Layer

## Result

This artifact set frames the move from bulky Wikiwise integration to a
schema-first output machine for semi-stocks.

Core conclusion: use Justin's compute stack in two separate ways:

1. Upstream evidence: selected compute deals/companies can inform raw sources,
   wiki synthesis, structured evidence, and thesis proposals.
2. Downstream architecture: schema-first JSON artifacts under
   `canonical/site-data/` become the reader contract after `40-engine`.

Decision update: Wikiwise should be removed from the semi-stocks visual layer.
`50-reports` should not be removed in the first slice; it remains the canonical
published report artifact until the new reader can reproduce the report view.

Target split: `40-engine` emits validated `canonical/site-data/` artifacts from
`10-wiki`, `20-data`, `30-thesis`, and synthesis/report metadata. A replaceable
React/Vite-style static reader, patterned after Justin's reader stack, consumes
only those artifacts.

## Visual

Read existing diagrams in this order:

1. `docs/diagrams/compute-vs-wide-narrow-pipeline.png`
2. `docs/diagrams/compute-stack-insertion-point.png`
3. `docs/diagrams/compute-stack-migration-path.png`
4. `docs/diagrams/compute-data-feed-vs-stack-copy.png`

## Gate

Ready for the first e2e data slice.

Not ready for full reader replacement yet. The first slice should stop before
frontend polish and prove this chain:

`10-wiki + 20-data + 30-thesis -> 40-engine/site_data.py -> canonical/site-data/*.json -> validation`

Reader path chosen: use a Justin-style React/Vite static reader after the data
contract passes.

First parity core: companies and signals. The reader should prove it can show
company exposure, source-backed signals, thesis impact, and report sections
before broader graph polish.

## Next Actions

1. Freeze current Wikiwise changes as a checkpoint, stash, or discard.
2. Add `SITE_DATA_DIR` and first `canonical/site-data/` artifacts.
3. Implement `canonical/40-engine/site_data.py` with validation.
4. Smoke the generated data without Wikiwise.
5. Prototype a React/Vite static reader after the data contract passes.
6. Stop generating `canonical/wiki-site/` only after reader parity passes.

## Details

- `01_spec.md` — goal, scope, boundaries.
- `02_questions.md` — approved research questions.
- `03_research.md` — repo/app/Justin research findings.
- `04_design.md` — draft decisions.
- `05_tasks.md` — execution-shaped task list.
- `site-data-contract.md` — first e2e artifact contract.
