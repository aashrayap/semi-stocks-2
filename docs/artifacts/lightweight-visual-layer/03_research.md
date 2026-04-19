---
status: complete
feature: lightweight-visual-layer
---

# Research: lightweight-visual-layer

## Flagged Items

- **Full wiki-site compiler missing from semi-stocks.** The current untracked
  repo-side code refreshes graph/map and HTML payloads, but does not regenerate
  all page HTML, `search.json`, or `previews.json`. Confidence: Medium.
- **Wikiwise still repairs repo data.** The app copies `canonical/wiki-site/`
  into a temp shell and rebuilds graph/map links from canonical markdown, so the
  app is still more than a thin reader. Confidence: High.
- **Justin's artifact schema has a small mismatch.** Built `deals.json` includes
  generated `source_category` and `target_category`, but released schema still
  describes only input deal fields with `additionalProperties: false`.
  Confidence: Medium.
- **Direction semantics in Justin's edges are not enough for semi-stocks.**
  Public docs describe `source_slug -> target_slug` as money/chips/equity flow,
  but equipment examples can read supplier-to-customer. Semi-stocks needs typed
  flows or direction notes. Confidence: Medium.
- **Current work spans two repos.** `semi-stocks-2` has untracked/modified
  wiki-site refresh artifacts; `wikiwise` has one modified app file. Confidence:
  High.
- **Decision update after research:** `canonical/site-data/` is now the chosen
  contract location, and Wikiwise is an exit target rather than a compatibility
  target. Confidence: High.

## Findings

### Codebase

#### Q1 — Current `canonical/wiki-site/` generation

**Answer:** `semi-stocks-2` now has an untracked repo-side refresh entrypoint at
`canonical/40-engine/wiki_site.py`, backed by
`canonical/40-engine/engine/wiki_site.py`. It refreshes `graph.json`,
`map.json`, and inlined graph/map payloads in `graph.html`, `map.html`, and
`map-3d.html`. It depends on the newly added `WIKI_SITE_DIR` path in
`canonical/40-engine/engine/paths.py`.

**Evidence:** `canonical/40-engine/wiki_site.py`,
`canonical/40-engine/engine/wiki_site.py`, `canonical/40-engine/engine/paths.py`.

**Confidence:** High for current refresh behavior; Medium that no full compiler
exists in this repo because this is based on repo search.

**Contract split:**

- Data-like artifacts: `previews.json`, `search.json`, `graph.json`, `map.json`.
- Presentation artifacts: page HTML, `graph.html`, `map.html`, `map-3d.html`,
  `style.css`, `app.js`, likely `search.json.js`.
- Strongest current page-data candidate: `previews.json`, because prior docs
  record `title`, `lead`, `rich`, `href`, and `type`, with `rich` carrying full
  body content.

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

#### Q3 — Wikiwise app consumption path

**Answer:** Wikiwise discovers a bundle by checking for `previews.json`,
`search.json`, `graph.json`, and `map.json`; opening the semi-stocks repo root
should resolve `<repo>/canonical/wiki-site`. It copies the whole bundle into a
temporary shell, normalizes HTML links, rebuilds graph/map from canonical
markdown, and writes generated shell HTML. The app contract therefore still
requires both the generated bundle and canonical markdown fallback.

**Evidence:** `/Users/ash/Documents/2026/wikiwise/Sources/Wikiwise/ExportBundle.swift`
discovers bundle files, builds a slug index from `10-wiki/{concepts,sources,outputs,raw}`,
copies to `wikiwise-export-shell`, rebuilds graph/map, and writes map/graph
HTML. `ContentView.swift` opens export bundles with `compiler = nil`.

**Confidence:** High.

#### Q4 — Current uncommitted changes

**Answer:**

- `semi-stocks-2`: modified agent logs/reports/predictions, modified
  `canonical/40-engine/engine/paths.py`, modified `canonical/wiki-site/graph*`
  and `map*`, untracked wiki-site refresh files, untracked compute/Wikiwise
  diagrams, untracked `canonical/.obsidian/`, and this feature artifact set.
- `wikiwise`: modified `Sources/Wikiwise/ExportBundle.swift` only. Relevant
  changes prefer authored wiki pages before raw files and inline map/previews/
  graph JSON into generated `map.html`.

**Evidence:** `git status --short` in both worktrees.

**Confidence:** High.

### Docs

#### Q5 — Authority and write boundaries

**Answer:** Repo docs consistently define five canonical stages plus one
generated app surface:

`canonical/10-wiki -> canonical/20-data -> canonical/30-thesis -> canonical/40-engine -> canonical/50-reports`

`canonical/wiki-site/` is generated integration/export output for the external
Wikiwise app, not a sixth canonical stage.

**Evidence:** `AGENTS.md`, `README.md`, `docs/architecture.md`,
`docs/doc-contract.md`, and
`docs/artifacts/canonical-propagation-model/07_implementation-spec.md`.

**Confidence:** High.

#### Q6 — Current propagation model alignment

**Answer:** The current model already points toward a data-only future. It says
Wikiwise may consume the generated bundle short-term, but long-term should not
depend on repo-owned presentational HTML if lower-level page/export data is
available. It also explicitly flags `previews.json` as closer to a page-data
contract than its name suggests.

**Evidence:** `docs/artifacts/canonical-propagation-model/07_implementation-spec.md`.

**Confidence:** High.

#### Q7 — Existing diagrams / idea notes

**Answer:** Existing diagrams cover four useful distinctions:

- `compute-vs-wide-narrow-pipeline.png`: Justin graph-record pipeline versus
  semi-stocks wide-to-narrow research funnel.
- `compute-stack-insertion-point.png`: compute-style contract belongs after
  `40-engine`, not inside canonical thinking loop.
- `compute-stack-migration-path.png`: keep Wikiwise alive while building the
  lighter contract/reader.
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
`canonical/50-reports/latest.html`; wiki-site refresh prints graph/map counts.
Existing task docs use `py_compile`, generator commands, and file-shape smoke
checks.

**Evidence:** `canonical/40-engine/report.py`,
`canonical/40-engine/wiki_site.py`, `docs/artifacts/canonical-propagation-model/05_tasks.md`,
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

**Answer:** First slice should freeze current Wikiwise work, then formalize
`canonical/site-data/`, generate it deterministically from current canonical
state, and validate its schema. Wikiwise should not receive new semi-stocks
behavior.

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
- Wikiwise is removed from the target architecture after reader parity.
- Justin's public data is an optional evidence input, not a new authority layer.
- Visual layer is derived from canonical lanes after `40-engine`.
- Reader path is a Justin-style React/Vite static app after the data contract
  validates.
- First parity core is companies and signals, with report metadata/key sections
  before full report HTML parity.

**Defer:**

- Exact timing for stopping `canonical/wiki-site/` generation.
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
- `previews.json` is already an accidental page-data contract; formalizing or
  replacing it is lower risk than inventing everything from scratch.
- Wikiwise app-side graph repair is useful as a bridge, but bad as a permanent
  contract.

## Core Docs Summary

- `README.md` and `docs/architecture.md`: five canonical stages plus generated
  `wiki-site`.
- `AGENTS.md`: write ownership and wiki write rules.
- `docs/doc-contract.md`: root docs stay minimal; generated bundle is
  repo-owned export output.
- `07_implementation-spec.md`: current app/repo handoff; already recommends
  reducing dependence on repo-owned HTML once lower-level page data is stable.
- `canonical/10-wiki/schema.md`: wiki edits require schema/index/generated
  state/log discipline.

## Open Questions

- How fast should `canonical/wiki-site/` be retired after `canonical/site-data/`
  exists?
- Should first execution formalize current `previews.json` or introduce
  `pages.json` and leave `previews.json` only as legacy bundle data?
- Should compute-deal-map-data be ingested now, or only used as design
  reference until the reader contract exists?
- What minimum claim schema exists today, given claims are present in company
  YAML but not yet normalized across all lanes?
