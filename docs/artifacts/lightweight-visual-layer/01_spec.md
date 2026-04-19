---
status: ready-for-e2e-data-slice
feature: lightweight-visual-layer
---

# Feature Spec: lightweight-visual-layer

## Goal

Replace the semi-stocks Wikiwise visual integration with a lighter,
schema-first output machine inspired by Justin's compute deal map, while
preserving the repo's wide-to-narrow canonical research flow.

The feature should clarify and eventually enable two distinct moves:

1. Use compute-style data as upstream evidence inside raw sources, wiki
   synthesis, and structured evidence.
2. Replace the bulky Wikiwise reader/export path with an explicit
   `canonical/site-data/` contract and a focused visual reader for thesis,
   reports, companies, claims, and source-backed edges.

The first e2e slice is data-only: build and validate `canonical/site-data/`
from existing canonical lanes. The reader comes after the contract passes.
`50-reports` remains as the canonical published report artifact until the new
reader can reproduce the report view.

The first reader parity target is category/company/signal centered, not
whole-wiki parity: thesis categories, companies, source-backed signals, thesis
impact, and report metadata/key sections should work before broader graph
polish.

## Users and Workflows

- Research owner: starts with broad AI infrastructure sources, narrows them
  into wiki synthesis, structured evidence, thesis controls, and reports.
- Reader/reviewer: needs to browse thesis/report/company/source relationships
  quickly without thinking about the underlying canonical lanes.
- Decision loop: needs visual graph/table/detail surfaces that reveal company
  exposure, claim support, bottlenecks, catalysts, and source provenance.
- Maintenance loop: needs deterministic build and validation so visual output is
  trusted as a product of canonical state, not app-side repair glue.

## Acceptance Criteria

- The current semi-stocks visual/export architecture is documented clearly
  enough to remove Wikiwise from the target visual layer.
- Justin's compute stack is understood separately as data production, release
  contract, and reader UI, without flattening it into "just an app."
- The design distinguishes upstream evidence import from downstream visual
  export.
- The proposed target shape preserves canonical ownership:
  `10-wiki`, `20-data`, `30-thesis`, `40-engine`, and `50-reports`.
- The first implementation slice is executable end to end:
  `10-wiki + 20-data + 30-thesis -> 40-engine/site_data.py -> canonical/site-data/*.json -> validation`.
- `20-data` and `30-thesis` are represented directly in site-data; they are not
  forced through wiki pages or scraped from final report HTML.
- Companies and signals are first-class reader artifacts, not only generic graph
  nodes.
- Categories are provisional reader groupings over thesis stages, company
  exposure, signal flow, review rows, and prediction rows.
- `50-reports` is represented in site-data as report metadata/sections while
  remaining a separate published artifact for now.
- Wikiwise is not a required runtime or delivery path for semi-stocks.

## Boundaries

- Do not expand Wikiwise integration during planning.
- Do not collapse narrative wiki pages into only row/edge records.
- Do not move project-specific semantics into baseline harness config.
- Do not modify `canonical/10-wiki/raw/`.
- Do not delete `canonical/50-reports/` in the first e2e slice.
- Do not scrape `canonical/50-reports/latest.html` as the primary data source.
- Do not treat Justin's public site bundle as the authoritative source when the
  public data repo provides the cleaner contract.
- Do not make the reader parse `10-wiki`, `20-data`, or `30-thesis` directly.
- Use a Justin-style React/Vite static reader for the first real reader slice,
  but do not start reader work until the data contract validates.

## Risks and Dependencies

- Risk: copying the visible site shape could flatten semi-stocks' richer
  thesis/evidence workflow.
- Risk: keeping legacy wiki-site output around too long could preserve duplicate
  contracts and stale repair behavior.
- Risk: removing `50-reports` before report-view parity could destroy the only
  current published artifact.
- Risk: moving too much into generated JSON could hide source provenance from
  the research loop.
- Dependency: Justin's public data repo and live site are separate surfaces and
  must be analyzed separately.
- Dependency: current semi-stocks export and reader changes may be uncommitted
  across multiple worktrees.
- Dependency: any durable wiki writes must follow `canonical/10-wiki/schema.md`
  and update wiki index/generated state/log.
