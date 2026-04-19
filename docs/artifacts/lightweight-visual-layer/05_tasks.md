---
status: ready-for-e2e-data-slice
feature: lightweight-visual-layer
---

# Tasks: lightweight-visual-layer

## Execution Order

1. Freeze current Wikiwise changes so they do not keep expanding.
2. Define `canonical/site-data/` artifact contract.
3. Add the site-data path contract.
4. Build deterministic site-data generator from earlier canonical lanes.
5. Validate generated JSON.
6. Smoke the data output without Wikiwise.
7. Prototype Justin-style React/Vite reader over `canonical/site-data/` only.
8. Replace report/wiki visual use with the new reader.
9. Remove Wikiwise integration surfaces.

## Task List

### T1 — Freeze Current Wikiwise Slice

**Files:**

- `canonical/40-engine/wiki_site.py`
- `canonical/40-engine/engine/wiki_site.py`
- `canonical/40-engine/engine/paths.py`
- `canonical/wiki-site/graph.json`
- `canonical/wiki-site/map.json`
- `canonical/wiki-site/graph.html`
- `canonical/wiki-site/map.html`
- `canonical/wiki-site/map-3d.html`
- `/Users/ash/Documents/2026/wikiwise/Sources/Wikiwise/ExportBundle.swift`

**Work:**

- Decide whether to commit the current e2e compatibility fix as a checkpoint or
  discard it after the new reader path exists.
- Default decision: freeze current Wikiwise changes in place and ignore them
  during site-data e2e.
- Stop adding new semi-stocks behavior to Wikiwise.
- Keep unrelated agent logs/reports out of this feature branch.

**Acceptance:**

- One explicit decision exists: commit checkpoint, stash, or discard.
- No further task depends on Wikiwise behavior.

**Verify:**

```bash
git status --short
git -C /Users/ash/Documents/2026/wikiwise status --short
```

**Estimate:** 0.5-1 hour.

### T2 — Define `canonical/site-data/` Contract

**Files:**

- `docs/artifacts/lightweight-visual-layer/04_design.md`
- `docs/artifacts/lightweight-visual-layer/site-data-contract.md`

**Work:**

- Lock `canonical/site-data/` as generated contract location.
- Introduce first artifact set:
  `build.json`, `pages.json`, `companies.json`, `signals.json`,
  `entities.json`, `edges.json`, `claims.json`, `thesis.json`,
  `reports.json`, `search.json`, `graph.json`, `schema.json`.
- Generated `canonical/site-data/*.json` should be checked in at first, matching
  the repo-owned generated-output pattern used by `canonical/wiki-site/`.
- State that `50-reports` remains a published artifact; report sections enter
  site-data through engine synthesis/report metadata, not HTML scraping.
- State that the reader consumes only `canonical/site-data/`.

**Acceptance:**

- `canonical/site-data/` artifact names and ownership are documented.
- Artifact schema plan separates source facts from derived display fields.
- E2e data slice has a defined stop point before reader work.

**Verify:** documentation review only.

**Estimate:** 0.5-1 hour.

### T3 — Add Site-Data Path Contract

**Files:**

- `canonical/40-engine/engine/paths.py`

**Work:**

- Add `SITE_DATA_DIR = CANONICAL_ROOT / "site-data"`.
- Keep `WIKI_SITE_DIR` only as legacy compatibility.
- Do not remove `REPORTS_DIR`.

**Acceptance:**

- Engine modules have one canonical path for the new generated contract.

**Verify:**

```bash
uv run python - <<'PY'
from engine.paths import SITE_DATA_DIR, REPORTS_DIR
print(SITE_DATA_DIR)
print(REPORTS_DIR)
PY
```

**Estimate:** 0.25 hour.

### T4 — Add First Site-Data Builder From Early Lanes

**Files:**

- `canonical/40-engine/site_data.py`
- `canonical/40-engine/engine/site_data.py`
- `canonical/40-engine/engine/paths.py`
- `canonical/site-data/*.json`

**Work:**

- Emit first JSON artifacts from current canonical state.
- Start with deterministic, low-risk payloads:
  `build.json`, `pages.json`, `companies.json`, `signals.json`,
  `entities.json`, `edges.json`, `claims.json`, `thesis.json`,
  `reports.json`, `search.json`, `graph.json`.
- Reuse current wiki-site graph/link extraction where sensible.
- Read `10-wiki`, `20-data`, `30-thesis`, and report metadata; do not scrape
  final report HTML as the primary data source.
- Represent `20-data` company/source records and `30-thesis` controls
  directly. Do not force them through wiki pages.
- Keep `50-reports/latest.html` as a report artifact reference only.
- Populate `reports.json` with metadata and key sections first, not full HTML
  parity.
- Do not import Justin data in this task.

**Acceptance:**

- Builder can delete/regenerate its own output directory.
- Output order is deterministic.
- No writes to `canonical/10-wiki/raw/`.

**Verify:**

```bash
uv run python canonical/40-engine/site_data.py
python3 -m json.tool canonical/site-data/pages.json >/dev/null
python3 -m json.tool canonical/site-data/companies.json >/dev/null
python3 -m json.tool canonical/site-data/signals.json >/dev/null
python3 -m json.tool canonical/site-data/entities.json >/dev/null
python3 -m json.tool canonical/site-data/edges.json >/dev/null
python3 -m json.tool canonical/site-data/claims.json >/dev/null
python3 -m json.tool canonical/site-data/thesis.json >/dev/null
python3 -m json.tool canonical/site-data/reports.json >/dev/null
python3 -m json.tool canonical/site-data/search.json >/dev/null
python3 -m json.tool canonical/site-data/graph.json >/dev/null
```

**Estimate:** 3-5 hours.

### T5 — Add Artifact Schema + Validation

**Files:**

- `canonical/site-data/schema.json`
- `canonical/40-engine/engine/site_data.py`
- optional `canonical/40-engine/validate_site_data.py`

**Work:**

- Define schema for emitted artifacts, including generated/enriched fields.
- Validate generated JSON after build.
- Separate input facts from derived display/cache fields.

**Acceptance:**

- Validation fails on missing required fields, unknown entity IDs, duplicate
  IDs, and malformed edge types.
- Schema describes what the reader consumes, not only source inputs.

**Verify:**

```bash
uv run python canonical/40-engine/site_data.py --validate
```

**Estimate:** 2-4 hours.

### T6 — Data-Only E2E Smoke

**Depends on:** T2-T5.

**Files:**

- generated `canonical/site-data/*.json`
- no reader files yet

**Work:**

- Run the site-data builder from a clean output directory.
- Validate every generated JSON file.
- Check that the output includes at least:
  one wiki page, one company entity, one source entity, one thesis node, one
  report record, one company record, one signal record, one typed edge, and one
  search record.
- Confirm no Wikiwise command or app path is needed for the smoke.

**Acceptance:**

- Data e2e succeeds without `/Users/ash/Documents/2026/wikiwise`.
- `50-reports/latest.html` still exists or is referenced only as a report
  artifact, not parsed as the source of truth.
- The generated contract is ready for a reader prototype.

**Verify:**

```bash
rm -rf canonical/site-data
uv run python canonical/40-engine/site_data.py --validate
python3 -m json.tool canonical/site-data/build.json >/dev/null
python3 -m json.tool canonical/site-data/schema.json >/dev/null
```

**Estimate:** 0.5-1 hour after T4/T5.

### T7 — Prototype Justin-Style React/Vite Reader

**Depends on:** T6.

**Files:**

- `canonical/site-reader/package.json`
- `canonical/site-reader/index.html`
- `canonical/site-reader/src/*`
- `canonical/site-reader/vite.config.*`

**Work:**

- Build a minimal React/Vite reader over JSON only, patterned after Justin's
  graph/table/detail shape.
- First screen should expose companies and signals as the baseline product
  surface, with graph/table/detail available immediately.
- Include thesis/report/company/source/signal filters.
- Keep it static and replaceable.

**Acceptance:**

- Reader runs without Wikiwise.
- Reader does not parse canonical markdown/YAML directly.
- Reader can show at least one company, one signal, one thesis stage, one report
  section, one source page, and one typed relationship.

**Verify:**

```bash
cd canonical/site-reader
npm install
npm run build
npm run dev
```

**Estimate:** 1-2 days for a usable prototype.

### T8 — Optional Compute Data Import

**Depends on:** T6, unless only prototyping in scratch.

**Files:**

- future importer under `canonical/40-engine/` or sidecar staging under `tmp/`
- possible structured evidence outputs under `canonical/20-data/`

**Work:**

- Pull latest `deals.json` and `companies.json` from Justin's release.
- Map a small subset of deals into semi-stocks source/evidence concepts.
- Preserve original source URL, release tag, imported timestamp, and mapping
  confidence.

**Acceptance:**

- Imported records are visibly evidence inputs, not canonical conclusions.
- Direction semantics are represented explicitly.
- No raw wiki files are modified automatically.

**Verify:** importer-specific validation plus diff review.

**Estimate:** 3-6 hours for a small proof.

### T9 — Remove Wikiwise Integration

**Depends on:** T7.

**Files:**

- docs that still describe Wikiwise as active semi-stocks visual layer
- `canonical/wiki-site/` generation path, once replacement parity passes
- possible Wikiwise checkout changes, if no longer needed

**Work:**

- Remove or archive Wikiwise-specific integration docs.
- Stop generating `canonical/wiki-site/` if `canonical/site-data/` + reader
  replaces it.
- Decide whether current Wikiwise checkout changes should be reverted, kept in
  that repo, or ignored as unrelated app work.

**Acceptance:**

- No semi-stocks command or doc points to Wikiwise as required visual layer.
- Replacement reader has smoke coverage for pages, thesis, reports, entities,
  and typed graph edges.

**Verify:** documentation grep plus reader smoke matrix.

**Estimate:** 1-3 hours after T5.
