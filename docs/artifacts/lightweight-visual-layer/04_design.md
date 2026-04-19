---
status: ready-for-e2e-data-slice
feature: lightweight-visual-layer
---

# Design: lightweight-visual-layer

## Relevant Principles

- Canonical flow stays:
  `10-wiki -> 20-data -> 30-thesis -> 40-engine -> 50-reports`.
- `canonical/wiki-site/` is legacy generated integration output for Wikiwise,
  not the future visual layer.
- `canonical/site-data/` is the chosen generated data contract for the new
  output machine.
- App/reader shells render `canonical/site-data/` only; they must not read
  canonical markdown/YAML directly.
- `50-reports` remains as a published report artifact until the site-data
  reader reproduces report-view parity.
- Generated Wikiwise HTML is removed from the active repo contract.
- Upstream evidence import and downstream visual export are separate moves.

## Decisions

### D1 — Borrow Justin's stack shape without flattening the data model

**Decision:** Borrow Justin's data-contract pattern and React/Vite-style static
reader shape, but do not copy his company/deal data model wholesale.

**Options considered:**

- Copy compute map wholesale, including its company/deal-only model.
- Keep Wikiwise and only polish it.
- Use compute-style schema/data contract and reader stack while preserving
  semi-stocks' richer canonical lanes and domain objects.

**Rationale:** Justin's stack is attractive because the contract and reader are
small and purpose-built. Justin's repo has one dominant model: company nodes
and deal edges. semi-stocks needs a wider model: raw source, wiki synthesis,
structured evidence, thesis, reports, companies, signals, claims, and reader
output. The reader stack can match Justin's direction; the data model should
not be compressed into only deals.

**Affected areas:** `canonical/40-engine/`, generated reader artifacts,
future visual reader.

### D2 — Put build ownership in `40-engine`, but read earlier lanes

**Decision:** The site-data builder belongs under `canonical/40-engine/`, but
it should read earlier canonical lanes directly: wiki pages, structured data,
thesis YAML, and report metadata. The renderer should consume only the emitted
`canonical/site-data/` artifacts.

**Options considered:**

- Reader renders only final report HTML.
- Reader reads markdown/YAML directly.
- Engine emits explicit site-data artifacts from upstream canonical lanes,
  consumed by any reader.

**Rationale:** Taking only final report/engine output is too late; it loses
source provenance, claim shape, company structure, and thesis-stage metadata.
Letting the renderer read early lanes is too loose; it recreates Wikiwise-style
app coupling. The right split is: engine reads early, renderer reads data.

**Affected areas:** `canonical/40-engine/engine/`, `canonical/site-data/`.

### D3 — Keep `50-reports` for now, but stop making it the visual bottleneck

**Decision:** Keep `canonical/50-reports/latest.html` as the published report
artifact in the first migration slice. Expose report metadata and sections
through `canonical/site-data/reports.json`, but do not build site-data by
scraping final report HTML.

**Options considered:**

- Delete reports immediately and let the new reader own all output.
- Build site-data by parsing `50-reports/latest.html`.
- Keep reports as one generated publication view while site-data becomes the
  machine-readable reader contract.

**Rationale:** Reports are still the only canonical published output. Deleting
them before reader parity creates avoidable loss. Parsing final HTML is too
late and loses structured evidence. The engine should build both report output
and site-data from the same upstream synthesis functions.

**Affected areas:** `canonical/40-engine/engine/report.py`,
`canonical/40-engine/engine/site_data.py`, `canonical/50-reports/`,
`canonical/site-data/reports.json`.

### D4 — Make categories, companies, and signals the first parity core

**Decision:** The first reader parity target is category/company/signal
centered. Emit first-class `companies.json` and `signals.json` artifacts, then
derive provisional reader categories from thesis stages, company exposure,
signal flow, review rows, and prediction rows.

**Options considered:**

- Start with whole-wiki page parity.
- Start with report page parity.
- Start with category/company/signal parity and add page/report/graph views
  around it.

**Rationale:** The actual decision loop needs to see the categories that thesis
reviews and general predictions move through, then the companies and signals in
those categories. Whole-wiki parity would recreate Wikiwise. Report-only parity
would be too late in the pipeline. Category/company/signal parity proves the new
output machine is using `20-data` and `30-thesis` directly.

**Affected areas:** `canonical/site-data/companies.json`,
`canonical/site-data/signals.json`, `canonical/site-data/entities.json`,
`canonical/site-data/edges.json`, future reader table/detail views.

### D5 — Keep upstream compute data import separate

**Decision:** Imported compute-deal-map data should enter as evidence input,
not as the visual contract itself.

**Options considered:**

- Treat Justin's `companies.json` and `deals.json` as the reader backend.
- Import selected deals into raw/wiki/data lanes as source-backed evidence.
- Defer import entirely and use Justin only as architecture reference.

**Rationale:** Justin's data can inform decisions, especially deal/company
relationships, but it cannot replace semi-stocks provenance, confidence,
conflict handling, thesis proposals, or claim lifecycle.

**Affected areas:** likely future importer, `canonical/10-wiki/sources` or
`outputs`, `canonical/20-data/`, maybe `thesis-proposals`.

### D6 — Create an artifact schema, not only input schemas

**Decision:** Define `schema.json` for emitted reader artifacts, including
derived/enriched fields.

**Options considered:**

- No schema; trust builder output.
- Schema only for manually edited inputs.
- Separate source/input schemas from artifact/output schemas.

**Rationale:** Justin's release schema gap shows the issue: if build adds
fields, the distributed artifact schema must describe them. The visual layer
should validate what readers actually consume.

**Affected areas:** new `schema.json`, validation script/command.

### D7 — Use typed domain edges, not one generic wikilink edge

**Decision:** Keep wikilinks for navigation, but add typed relationships for
visual reasoning.

**Candidate edge types:**

- `links_to`
- `supports_claim`
- `contradicts_claim`
- `derived_from_source`
- `exposes_company_to`
- `belongs_to_bottleneck`
- `mentions_ticker`
- `updates_thesis_stage`
- `published_in_report`

**Rationale:** The current graph has page nodes and wikilink edges. That is
good for browsing, weak for decisions. The reader needs to answer: what claim,
which company, which evidence, which bottleneck, what report/thesis impact?

**Affected areas:** `edges.json`, `claims.json`, `entities.json`, builder
logic.

### D8 — Eliminate Wikiwise from semi-stocks visual layer

**Decision:** Remove Wikiwise from the target architecture. No compatibility
bridge remains in the semi-stocks contract.

**Options considered:**

- Delete legacy Wikiwise integration immediately.
- Keep Wikiwise as permanent local authoring/browsing.
- Build `canonical/site-data/` and a static reader, then stop generating and
  depending on `canonical/wiki-site/`.

**Rationale:** Wikiwise remains too bulky for the actual semi-stocks need. The
target is an output machine: canonical state in, validated JSON artifacts out,
static reader over those artifacts. Wikiwise can remain a separate app, but not
as semi-stocks' visual contract.

**Affected areas:** `canonical/wiki-site/`, `canonical/site-data/`, future
reader.

### D9 — Build the reader after `site-data`, not before

**Decision:** Build a purpose-specific React/Vite static reader after
`canonical/site-data` exists. Do not extend the old Wikiwise app.

**Options considered:**

- Extend Wikiwise with workflow controls.
- Build a React/Vite reader like Justin's compute site.
- Build a vanilla static reader over JSON.

**Rationale:** The current problem is contract shape, not UI polish. Once JSON
is stable, a purpose-built static reader can be small and replaceable. The
chosen reader path should resemble Justin's stack because graph/table/detail
state will matter and because the goal is a focused data product, not another
generic wiki shell.

**Affected areas:** future `canonical/site-reader/` or `canonical/site/`; not
Wikiwise.

## Open Risks

- The repo does not yet have a tracked compiler for legacy wiki-site files,
  and may not need one now that `canonical/wiki-site/` is retired.
- Current `previews.json` may be good enough to formalize, but its name implies
  teaser data rather than full pages.
- Claim data exists unevenly across company/source/thesis structures.
- A data-only reader may lose narrative feel if `pages.json` does not preserve
  rich page bodies and report sections.
- A React/Vite reader can become another bulky app if contract discipline is
  weak.
- Compute import could pollute canonical lanes if imported too aggressively
  without source/provenance mapping.

## File Map

### Current Inputs

- `canonical/10-wiki/**/*.md`
- `canonical/20-data/**/*.yaml`
- `canonical/30-thesis/thesis.yaml`
- synthesis outputs currently used by `canonical/40-engine/engine/report.py`
- `canonical/50-reports/latest.html` as optional report artifact metadata, not
  as the primary source of reader data

### Removed Legacy Export

- `canonical/wiki-site/` has no tracked active files in this target.
- Historical docs and diagrams may still mention the old export surface as
  migration context.

### New Contract Candidate

Chosen path:

- `canonical/site-data/schema.json`
- `canonical/site-data/pages.json`
- `canonical/site-data/companies.json`
- `canonical/site-data/signals.json`
- `canonical/site-data/entities.json`
- `canonical/site-data/edges.json`
- `canonical/site-data/claims.json`
- `canonical/site-data/reports.json`
- `canonical/site-data/thesis.json`
- `canonical/site-data/search.json`
- `canonical/site-data/graph.json`
- `canonical/site-data/build.json`

### Builder / Verify Candidate

- `canonical/40-engine/site_data.py`
- `canonical/40-engine/engine/site_data.py`
- `canonical/40-engine/engine/site_data_schema.py` or JSON Schema assets
- optional `canonical/40-engine/validate_site_data.py`

### Reader Candidate

Deferred until contract exists. Possible locations:

- `canonical/site-reader/` for repo-local static prototype.
- `canonical/site/` if reader output should be checked in as generated static
  site.
- separate reader repo if it becomes a real app.

### Wikiwise Removal Candidate

- Stop treating `/Users/ash/Documents/2026/wikiwise` as part of semi-stocks
  delivery.
- Do not regenerate `canonical/wiki-site/` now that `canonical/site-data/` +
  reader own the contract.
- Remove or archive Wikiwise-specific docs when they describe an active runtime
  dependency rather than migration history.
