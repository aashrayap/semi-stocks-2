---
status: complete
feature: lightweight-visual-layer
---

# Research Questions: lightweight-visual-layer

## Codebase

1. What files and commands currently generate `canonical/site-data/`, and which
   generated artifacts are data contracts versus presentation shells?
2. Which canonical lanes currently contain company, source, claim, thesis, and
   report data that could feed a lighter visual layer?
3. What legacy `canonical/wiki-site/` references still remain in the repo, and
   which can be deleted outright?
4. What uncommitted changes already exist in `semi-stocks-2` that affect this
   migration path?

## Docs

1. What do repo docs define as the authoritative lane ownership and write
   boundaries for wiki, data, thesis, engine, reports, `site-data`, and the
   reader?
2. What does the current canonical propagation model say about the site-data
   contract, and is it still aligned with the live code?
3. What durable diagrams or idea notes already describe the compute-stack
   comparison, insertion point, migration path, and upstream evidence feed?

## Patterns

1. What validation/build pattern does Justin use for companies, deals, schemas,
   and release artifacts?
2. What object model does Justin's data repo actually encode, and which parts
   map cleanly to semi-stocks concepts?
3. What repo-local patterns already exist for deterministic Python build
   entrypoints, generated-state refreshes, and smoke checks?

## External

1. What is the public shape of `jstwng/compute-deal-map-data` as of the current
   main branch: manifests, schemas, scripts, CI, and release outputs?
2. What can be inferred safely about `compute.jstwng.com` as a reader without
   relying on private source code?

## Cross-Ref

1. Which Justin pattern should enter semi-stocks upstream as evidence import,
   and which should enter downstream as visual/export architecture?
2. What is the smallest migration slice that removes Wikiwise dependency while
   keeping current reports usable?
3. What target data contract should exist between `40-engine` and a future
   visual reader: pages, entities, edges, claims, sources, reports, thesis, or a
   different split?
4. What decision should be made now versus deferred until a prototype exists?
