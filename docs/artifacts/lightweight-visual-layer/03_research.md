---
status: complete
feature: lightweight-visual-layer
---

# Research: lightweight-visual-layer

## Flagged Items

- **Legacy wiki-site bundle exists only as removable output.** The active
  builder is `canonical/40-engine/site_data.py`; the old generated bundle is not
  part of the target contract. Confidence: High.
- **Justin's artifact schema has a small mismatch.** Built `deals.json` includes
  generated `source_category` and `target_category`, but released schema still
  describes only input deal fields with `additionalProperties: false`.
  Confidence: Medium.
- **Direction semantics in Justin's edges are not enough for semi-stocks.**
  Public docs describe `source_slug -> target_slug` as money/chips/equity flow,
  but equipment examples can read supplier-to-customer. Semi-stocks needs typed
  flows or direction notes. Confidence: Medium.
- **Current work spans multiple worktrees.** `semi-stocks-2` carries the active
  site-data contract and removal work. Confidence: High.
- **Decision update after research:** `canonical/site-data/` is the chosen
  contract location, and Wikiwise is an exit target. Confidence: High.

## Findings

### Codebase

#### Q1 — Current `canonical/site-data/` generation

**Answer:** `semi-stocks-2` now has the active repo-side builder at
`canonical/40-engine/site_data.py`, backed by
`canonical/40-engine/engine/site_data.py`. It writes the schema-first
`canonical/site-data/*.json` contract from the canonical lanes and validates it
on request.

**Evidence:** `canonical/40-engine/site_data.py`,
`canonical/40-engine/engine/site_data.py`, `canonical/40-engine/engine/paths.py`.

**Confidence:** High.

**Contract split:**

- Data-like artifacts: `build.json`, `schema.json`, `pages.json`,
  `companies.json`, `signals.json`, `entities.json`, `edges.json`,
  `claims.json`, `thesis.json`, `reports.json`, `search.json`, `graph.json`.
- Presentation work now belongs in `canonical/site-reader/`, not in generated
  repo-owned HTML.

#### Q2 — Canonical lanes that can feed a lighter visual layer

**Answer:** The visual layer should derive from several lanes, but own none of
them:

- `canonical/10-wiki/`: raw/source/concept/output pages plus generated wiki
  metadata.
- `canonical/20-data/companies/`: company packets, claims, financials,
  guidance, thesis signals, and positioning.
- `canonical/20-data/sources/`: structured source snapshots and positions.
- `canonical/20-data/thesis-proposals/`: pending structured evidence changes.
- `canonical/30-thesis/thesis.yaml`: cascade, status, cycle phase, ticker map.
- `canonical/40-engine/`: synthesis functions already derive agreement maps,
  dashboards, claims, and signals.
- `canonical/50-reports/`: published report output.

**Evidence:** `canonical/10-wiki/schema.md`, `canonical/20-data/companies/*`,
`canonical/20-data/sources/*`, `canonical/30-thesis/thesis.yaml`,
`canonical/40-engine/engine/synthesis.py`, `canonical/50-reports/latest.html`.

**Confidence:** High.

#### Q3 — Legacy wiki-site removal path

**Answer:** No active Wikiwise consumption path is required for the semi-stocks
reader now. Legacy `canonical/wiki-site/` files can be removed without changing
the site-data contract.

**Evidence:** repo search plus the active `canonical/site-data/` builder and
`canonical/site-reader/` worktree.

**Confidence:** High.

#### Q4 — Current uncommitted changes

**Answer:** The active work in `semi-stocks-2` is the site-data contract and
removal of the legacy `canonical/wiki-site/` bundle. No `wikiwise` worktree
dependency is required for this branch.

**Evidence:** `git status --short` in the repo worktree.

**Confidence:** High.

### Docs

#### Q5 — Authority and write boundaries

**Answer:** Repo docs should define five canonical stages plus one generated
reader contract:

`canonical/10-wiki -> canonical/20-data -> canonical/30-thesis -> canonical/40-engine -> canonical/50-reports`

`canonical/site-data/` is generated reader input, and `canonical/site-reader/`
is the local presentation layer.

**Evidence:** `AGENTS.md`, `README.md`, `docs/architecture.md`,
`docs/doc-contract.md`, and
`docs/artifacts/canonical-propagation-model/07_implementation-spec.md`.

**Confidence:** High.

#### Q6 — Current propagation model alignment

**Answer:** The current model should be treated as historical migration
context. The active contract is now `canonical/site-data/` plus the reader.

**Evidence:** repo docs and the active site-data artifact set.

**Confidence:** High.

#### Q7 — Existing diagrams / idea notes

**Answer:** Existing diagrams cover four useful distinctions:

- `compute-vs-wide-narrow-pipeline.png`: Justin graph-record pipeline versus
  semi-stocks wide-to-narrow research funnel.
- `compute-stack-insertion-point.png`: compute-style contract belongs after
  `40-engine`, not inside canonical thinking loop.
- `compute-stack-migration-path.png`: migration path from the old integration
  surface to the lighter contract/reader.
- `compute-data-feed-vs-stack-copy.png`: separate upstream evidence import from
  downstream architecture borrowing.

**Evidence:** `docs/diagrams/compute-*.png`.

**Confidence:** High.

### Patterns

#### Q8 — Justin validation/build pattern

**Answer:** Justin uses a small Node 20 ESM data repo:

`companies.yml + deals/*.yml -> JSON Schema + AJV/js-yaml validation -> build.js -> dist/{companies,deals,schema}.json -> GitHub Release`

Validation checks schema shape, filename equals id, duplicate deal IDs,
foreign-key slugs, cached source/target names, date format, and HTTPS source
URLs.

**Evidence:** `package.json`, `schema/*.schema.json`, `scripts/validate.js`,
`scripts/build.js`, `.github/workflows/*.yml`.

**Confidence:** High.

#### Q9 — Justin object model

**Answer:** Justin models companies as nodes and deals as directed edges:

- Company: `slug`, `name`, `ticker`, `category`, `subline`, optional
  `acquired`.
- Deal: `id`, `source_slug/name`, `target_slug/name`, `deal_type`,
  optional value, date, description, one primary `source_url`.
- Build adds `source_category` and `target_category`.

This maps cleanly to semi-stocks for simple relationship graphing, but not for
claim/evidence provenance, multi-role companies, or thesis support/conflict.

**Evidence:** `companies.yml`, `deals/*.yml`, `schema/company.schema.json`,
`schema/deal.schema.json`.

**Confidence:** High.

#### Q10 — Existing repo build/verify patterns

**Answer:** semi-stocks already prefers deterministic `uv run python ...`
entrypoints under `canonical/40-engine/`. Report generation writes
`canonical/50-reports/latest.html`; site-data generation writes the new reader
contract. Existing task docs use `py_compile`, generator commands, and
file-shape smoke checks.

**Evidence:** `canonical/40-engine/report.py`,
`canonical/40-engine/site_data.py`, `docs/artifacts/canonical-propagation-model/05_tasks.md`,
`06_handoff.md`, `07_implementation-spec.md`.

**Confidence:** High.

### External

#### Q11 — Public compute data repo shape

**Answer:** Latest public data repo inspected at release `2026.04.17-1`, commit
`e5c0e74`, has 81 companies and 257 deals. `npm ci`, `npm run validate`,
`npm test`, and `npm run build` passed in a temp clone; Node's test runner
reported 11 passing tests.

**Evidence:** `/tmp/compute-deal-map-data-spec`, public GitHub release
`2026.04.17-1`, local verification output.

**Confidence:** High.

#### Q12 — Public site inference

**Answer:** The live site is a static SPA hosted on Netlify. HTML mounts
`#root` and loads a hashed JS/CSS bundle. The public JS bundle contains React
18.3.1 and appears to embed data at build time rather than fetch
`deals.json`/`companies.json` at runtime. The graph looks custom React/SVG from
public assets; Vite is likely but not proven.

**Evidence:** `https://compute.jstwng.com/`, public asset
`/assets/index-DmhPwKym.js`.

**Confidence:** High for static SPA/React/embedded data; Medium for Vite/custom
graph internals due to minified public assets.

### Cross-Ref

#### Q13 — Upstream versus downstream use of Justin's pattern

**Answer:** Use Justin's data as upstream evidence only when it is treated as
source-backed observations entering the research funnel. Use Justin's stack as
downstream architecture when defining a schema-first reader/export contract.
Keep those moves separate:

- Upstream: imported deal/company/source signals can become raw/source notes,
  wiki clusters, structured evidence, or thesis proposals.
- Downstream: semi-stocks emits reader artifacts derived from canonical lanes.

**Confidence:** High.

#### Q14 — Smallest migration slice

**Answer:** First slice should delete the legacy wiki-site bundle, then
formalize `canonical/site-data/`, generate it deterministically from current
canonical state, and validate its schema. Wikiwise should not receive new
semi-stocks behavior.

**Confidence:** High.

#### Q15 — Target reader data contract

**Answer:** The likely split is:

- `pages.json`: wiki/report pages with title, kind, body/summary, href, source
  path, lane.
- `entities.json`: companies, tickers, bottlenecks, sources, thesis stages.
- `edges.json`: typed relationships with provenance and flow/direction
  semantics.
- `claims.json`: claim/evidence/confidence/status records where available.
- `reports.json`: published report metadata and sections.
- `thesis.json`: derived view of `thesis.yaml`.
- `search.json` and `graph.json`: derived indexes/caches.
- `schema.json`: artifact schema, not just input schema.

**Confidence:** Medium; needs design approval.

#### Q16 — Decide now versus defer

**Decide now:**

- JSON artifacts become the reader contract.
- Wikiwise is removed from the target architecture.
- Justin's public data is an optional evidence input, not a new authority layer.
- Visual layer is derived from canonical lanes after `40-engine`.
- Reader path is a Justin-style React/Vite static app after the data contract
  validates.
- First parity core is companies and signals, with report metadata/key sections
  before full report HTML parity.

**Defer:**

- Whether compute data gets a dedicated importer in the first implementation
  slice.
- Final public/private distribution mechanism.

**Confidence:** High for now/defer split.

## Patterns Found

- Schema-first data artifacts make the UI replaceable.
- One-record-per-file improves reviewability for graph edges.
- Generated enriched fields should have artifact schemas, not only input
  schemas.
- Semi-stocks needs richer relationships than Justin's single directed edge:
  `flow_type`, `supports_claim`, `contradicts_claim`, `exposes_company_to`,
  `belongs_to_bottleneck`, and `derived_from_source`.
- `pages.json` is the new page-data contract; keep it explicit rather than
  implicit.
- Wikiwise app-side graph repair is no longer part of the semi-stocks
  contract.

## Core Docs Summary

- `README.md` and `docs/architecture.md`: five canonical stages plus generated
  reader contract.
- `AGENTS.md`: write ownership and wiki write rules.
- `docs/doc-contract.md`: root docs stay minimal; generated reader input is
  repo-owned output.
- `07_implementation-spec.md`: current app/repo handoff; already recommends
  reducing dependence on repo-owned HTML once lower-level page data is stable.
- `canonical/10-wiki/schema.md`: wiki edits require schema/index/generated
  state/log discipline.

## Open Questions

- Which legacy `canonical/wiki-site/` files, if any, should be archived before
  deletion?
- Should compute-deal-map-data be ingested now, or only used as design
  reference until the reader contract exists?
- What minimum claim schema exists today, given claims are present in company
  YAML but not yet normalized across all lanes?
