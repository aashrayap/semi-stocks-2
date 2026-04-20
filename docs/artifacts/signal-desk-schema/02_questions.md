---
status: approved
feature: signal-desk-schema
---

# Research Questions: signal-desk-schema

## Codebase

1. Which files currently generate or serve the Signal Desk data shown in the screenshot, and what entity names and fields do they emit?
2. Where are `reviews` and `predictions` counted today, and are those counts sourced from authored canonical files, generated YAML/JSON, agent state, or derived UI aggregation?
3. What current code paths connect `canonical/10-wiki`, `canonical/20-data`, `canonical/30-thesis`, `canonical/40-engine`, `canonical/50-reports`, and `canonical/wiki-site` into the app-facing surface?
4. Which schema fields are required by the current UI interactions: category tab, companies tab, signals tab, search, category filter, signal filter, direction filter, selected company panel, positions, and signal list?
5. Which current files look like app view models rather than canonical source-of-truth data?
6. Which local changes under `canonical/40-engine`, `canonical/site-data`, `canonical/wiki-site`, and `agents/state/predictions` are relevant to this schema discussion?

## Docs

1. What does `README.md` say about the repo map and intended canonical pipeline?
2. What does `docs/architecture.md` define as lane ownership and propagation boundaries?
3. What does `docs/doc-contract.md` require for adding schema or process docs?
4. What does `docs/artifacts/canonical-propagation-model/07_implementation-spec.md` define as the current repo/Wikiwise contract?
5. Do existing artifacts such as `lightweight-visual-layer` or `semi-stocks-v2-layout` already define a Signal Desk schema or UI contract?

## Patterns

1. What naming pattern does the repo use for canonical entities versus generated integration outputs?
2. How does the repo currently represent evidence lineage from raw/source material into concepts, companies, thesis, reports, and site data?
3. What is the narrowest existing object that can represent a user-visible "signal" without duplicating wiki/source content?
4. What pattern should separate stable IDs, display labels, counts, tags, and narrative snippets?
5. What existing validation or lint pattern should apply to app schema output if schema changes later become executable?

## External

1. In Justin's Wikiwise repo at `/Users/ash/Documents/2026/wikiwise`, what data contract does the installed app expect for `canonical/wiki-site/` or equivalent site data?
2. Which Wikiwise files or docs define accepted graph/map/site-data field names, indexes, and generated asset boundaries?
3. Are there external package or runtime constraints that affect schema format, such as JSON-only, YAML support, static-file names, or app bundle paths?

## Cross-Ref

1. Do repo docs and current generated data agree on whether `canonical/wiki-site/` is only integration output, or has it started acting like a schema source?
2. Do Justin's Wikiwise data expectations match the current `canonical/site-data` and `canonical/wiki-site` shape?
3. Can `reviews` be modeled as evidence assessments attached to company-signal-category edges, or does current data require a separate review entity?
4. Can `predictions` be modeled as forward-looking claims attached to company-signal-category edges, or does current data require a separate prediction entity?
5. What minimum schema supports the current UI without losing traceability back to canonical source material?
6. Which fields are necessary now, which can be derived, and which should be parked until a richer UI exists?
