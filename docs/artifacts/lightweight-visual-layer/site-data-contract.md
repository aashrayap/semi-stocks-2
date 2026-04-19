---
status: ready-for-e2e-data-slice
feature: lightweight-visual-layer
---

# Site Data Contract

## Purpose

`canonical/site-data/` is the generated reader contract for the new visual
layer. It replaces `canonical/wiki-site/` as the semi-stocks visual boundary.

The reader consumes `canonical/site-data/` only. It must not parse
`canonical/10-wiki`, `canonical/20-data`, `canonical/30-thesis`, or
`canonical/50-reports` directly.

## Ownership

- Source authority remains in `10-wiki`, `20-data`, `30-thesis`, and
  `50-reports`.
- Build ownership lives in `40-engine`.
- `site-data` is generated output and may be deleted/rebuilt.
- Generated `site-data` artifacts should be checked in for the first migration
  phase so reader diffs and contract drift are reviewable.
- Wikiwise is not part of the target architecture.

## First E2E Artifact Set

- `build.json` — build timestamp, source counts, generator version, warnings.
- `schema.json` — JSON Schema bundle for emitted artifacts.
- `pages.json` — wiki/report/narrative pages with body, title, type, backlinks.
- `companies.json` — first-class company/ticker records derived from `20-data`
  and thesis ticker mappings.
- `signals.json` — company/source/thesis signals used by the decision loop.
- `entities.json` — companies, tickers, sources, bottlenecks, concepts, reports.
- `edges.json` — typed relationships across pages, entities, claims, reports.
- `claims.json` — source-backed claims and status/lifecycle where available.
- `thesis.json` — promoted thesis controls from `30-thesis/thesis.yaml`.
- `reports.json` — report metadata/sections generated from engine state.
- `search.json` — compact reader search index.
- `graph.json` — graph projection optimized for the first reader.

## First Parity Core

The first reader parity target is **categories + companies + signals**:

- thesis categories that reviews and predictions move through
- company exposure and ticker mapping
- source-backed signal rows
- thesis impact or stage mapping
- report metadata and key sections
- links back to wiki/source pages

This is intentionally narrower than whole-wiki parity and more useful than
report-HTML parity. Category taxonomy is provisional until the thesis review and
prediction flow settles.

## Source Inputs

- `canonical/10-wiki/**/*.md`
- `canonical/20-data/**/*.yaml`
- `canonical/30-thesis/thesis.yaml`
- `canonical/40-engine/engine/synthesis.py` outputs
- `canonical/50-reports/latest.html` as an optional published artifact
  reference, not as the primary source of data

## Edge Types

Initial edge types:

- `links_to`
- `mentions_ticker`
- `derived_from_source`
- `supports_claim`
- `contradicts_claim`
- `exposes_company_to`
- `belongs_to_bottleneck`
- `updates_thesis_stage`
- `published_in_report`

## First Slice Stop Point

The first e2e slice is complete when this works without Wikiwise:

```bash
rm -rf canonical/site-data
uv run python canonical/40-engine/site_data.py --validate
python3 -m json.tool canonical/site-data/build.json >/dev/null
python3 -m json.tool canonical/site-data/schema.json >/dev/null
```

Reader implementation starts after this gate passes.
