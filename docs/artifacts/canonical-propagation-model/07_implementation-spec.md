---
status: draft
feature: canonical-propagation-model
updated: 2026-04-15
---

# Implementation Spec: canonical-propagation-model

## Purpose

This artifact governs the next implementation pass after the April 10, 2026 canonical migration.

The migration package in `01_spec.md` through `06_handoff.md` locked the canonical repo shape and documented the completed move into `canonical/`. It did not fully specify how repo-side work in `semi-stocks-2` should coordinate with app-side work in the Wikiwise source checkout.

This file closes that gap.

For the repo/app rollout described here:

- `01_spec.md` and `04_design.md` remain the architectural baseline for canonical lane ownership.
- `05_tasks.md` and `06_handoff.md` remain historical migration records.
- this file is the working handoff and implementation contract for the parallel repo-side and app-side execution tracks

## Goal

Execute the next phase in three tracks:

1. **Repo-side track**: align `semi-stocks-2` naming, docs, path ownership, and export surfaces with the live canonical structure.
2. **App-side track**: implement the workflow shell in the Wikiwise source checkout without moving canonical ownership into the app.
3. **Integration track**: reconcile the two tracks into one explicit repo/app contract and close out ambiguous surfaces.

The primary goal is to let both tracks move in parallel without creating split authority over content, metadata, or UI artifacts.

## Locked Approach

- `semi-stocks-2` remains the source of truth for canonical research content and structured state.
- The Wikiwise checkout owns the workflow shell and app behavior, not the canonical source material.
- `canonical/10-wiki/`, `canonical/20-data/`, `canonical/30-thesis/`, `canonical/40-engine/`, and `canonical/50-reports/` remain the only canonical propagation stages.
- `canonical/wiki-site/` is **not** a sixth canonical stage. It is a generated integration/export surface derived from canonical wiki state.
- App-side code must not write into `semi-stocks-2` canonical lanes.
- Repo-side work must not absorb the external app shell into this repo.

## Recommended End State

The preferred steady state is:

- `semi-stocks-2` owns markdown content, structured metadata, thesis/data links, and generated wiki export data.
- the Wikiwise checkout owns layout, routing, search UX, graph/map UX, page chrome, and any shell-specific client logic
- `canonical/wiki-site/` either:
  - remains as a generated export fixture consumed by the app, or
  - is slimmed to the minimum generated payload the app needs

The repo should not be the long-term home of a second manually maintained UI shell.

## Track Matrix

| Track | Primary write scope | Read scope | Outputs | Parallel rule |
|---|---|---|---|---|
| Repo-side | `semi-stocks-2` docs, path contracts, export bundle, repo-side generators | canonical lanes, existing generated wiki site, current docs | aligned docs, stable export surface, explicit ownership notes | may run immediately |
| App-side | external Wikiwise checkout only | repo export bundle, canonical sample content, this spec | workflow shell, routing, visual integration, app-side build/test notes | may run immediately after checkout is pinned |
| Integration | minimal glue in both repos plus close-out docs | outputs from both tracks | one reconciled contract, verified end-to-end behavior, final ownership decision on `canonical/wiki-site/` | starts once repo export and app shell both exist |

## Authority Rules

### Canonical authority

- `canonical/10-wiki/` owns authored wiki content, schema, generated wiki metadata, and the canonical wiki index/log surfaces.
- `canonical/20-data/` owns structured evidence only.
- `canonical/30-thesis/thesis.yaml` owns the narrow thesis control plane.
- `canonical/40-engine/` owns canonical synthesis/report code.
- `canonical/50-reports/` owns canonical published report artifacts.

### App authority

- The Wikiwise checkout owns workflow-shell behavior only.
- It may render canonical data and generated export assets.
- It may not redefine canonical research structure or mutate canonical state.

### Sidecar authority

- `agents/` remains sidecar-only.
- Nothing in this rollout changes the rule that agents may read canonical state broadly and write sidecar state only under `agents/` unless a human explicitly promotes changes.

## Integration Contract

### Contract table

| Artifact | Path | Owner | Produced by | Consumed by | Notes |
|---|---|---|---|---|---|
| Authored page content | `canonical/10-wiki/sources/**/*.md`, `canonical/10-wiki/concepts/**/*.md`, `canonical/10-wiki/outputs/**/*.md` | repo-side | repo-side wiki workflow | repo-side generators, app-side shell | source of truth; app treats as read-only |
| Wiki schema and generated wiki state | `canonical/10-wiki/schema.md`, `_index.json`, `_backlinks.json`, `_lint.json`, `index.md`, `log.md` | repo-side | repo-side wiki workflow | repo-side generators, integration checks | canonical metadata; app does not author this |
| Structured evidence cross-links | `canonical/20-data/**`, `canonical/30-thesis/thesis.yaml` | repo-side | repo-side | repo-side generators, app deep links where needed | app may link or display derived state, never write it |
| Generated Wikiwise export bundle | `canonical/wiki-site/` | repo-side | repo-side export build | app-side shell | read-only fixture/export surface; not a canonical stage |
| App shell | `<WIKIWISE_CHECKOUT>/**` | app-side | app-side | end users | layout, routing, presentation, interactions |

### Bundle expectations for `canonical/wiki-site/`

The export bundle must be stable enough that the app shell can consume it without scraping or guessing.

At minimum, the bundle must expose:

- page-level outputs for the current wiki corpus
- a search corpus
- a preview corpus
- a graph payload
- stable slugs/hrefs for sample pages used during integration

Today, the live repo already contains the following integration-relevant files:

- `canonical/wiki-site/search.json`
- `canonical/wiki-site/previews.json`
- `canonical/wiki-site/graph.json`
- `canonical/wiki-site/index.html`
- `canonical/wiki-site/map.html`
- `canonical/wiki-site/graph.html`
- per-page HTML outputs under `canonical/wiki-site/*.html`

Short-term contract:

- app-side may consume the generated bundle as read-only fixture input
- repo-side owns regeneration and any contract-preserving format changes

Long-term contract:

- the app should not depend on repo-owned presentational HTML if the shell can consume lower-level page/export data directly
- if the app no longer needs repo-owned HTML pages, integration should reduce `canonical/wiki-site/` to the minimum export payload required

## Parallel Execution Plan

### Repo-side track

#### R1 — Align naming, docs, and path ownership

Update repo-side docs so they describe the live canonical structure and the new app integration surface consistently.

Required outcomes:

- `canonical/wiki-site/` is explicitly described as generated integration/export output, not as a sixth canonical stage
- docs consistently describe `canonical/10-wiki/` through `canonical/50-reports/` as the only canonical stages
- `canonical/20-data/thesis-proposals/`, if retained, is documented as structured evidence staging rather than thesis control-plane state
- repo docs stop implying that migration artifacts are the current implementation handoff for this app rollout

Likely files:

- `README.md`
- `docs/architecture.md`
- `docs/doc-contract.md`
- `AGENTS.md`
- `CLAUDE.md`
- relevant artifact docs if cross-references need to be corrected

Done when:

- a new reader can tell what is canonical, what is generated, and what is external app code without inferring from drift

Verify:

- `rg -n "canonical/wiki-site|10-wiki|20-data|30-thesis|40-engine|50-reports|thesis-proposals" README.md docs AGENTS.md CLAUDE.md -S`

#### R2 — Stabilize the repo-owned export surface

Treat `canonical/wiki-site/` as a reproducible export bundle, not as hand-edited source.

Required outcomes:

- the repo-side export bundle is safe to delete and regenerate
- app-side can depend on a small, explicit set of bundle files and slugs
- no app-side behavior requires undocumented scraping of canonical markdown or HTML

Minimum sample set to preserve during integration:

- one concept page
- one source page
- one output page
- one search result path
- one graph/map path

Recommended fixture pages from the current repo:

- `canonical/10-wiki/concepts/n3-wafer-crunch.md`
- `canonical/10-wiki/sources/nvda-q4-fy2026.md`
- `canonical/10-wiki/outputs/long-term-value-chain-thesis.md`

Done when:

- app-side can build against a fixed export contract instead of repo internals

Verify:

- `find canonical/wiki-site -maxdepth 1 -type f | sort`
- `test -f canonical/wiki-site/search.json`
- `test -f canonical/wiki-site/previews.json`
- `test -f canonical/wiki-site/graph.json`

#### R3 — Keep repo-side writes inside repo-owned boundaries

Repo-side may improve generators, docs, and export data, but must not absorb the app shell.

Required outcomes:

- no shell-specific source code is added under canonical lanes as if it were source of truth
- any repo-owned HTML under `canonical/wiki-site/` is treated as generated fixture output only
- accidental local/editor state remains out of the contract

Known non-contract surfaces already visible in the worktree:

- `canonical/.obsidian/`
- `__pycache__/`
- agent logs and ad hoc reports under `agents/`

Done when:

- repo-side changes are clearly content/export work, not UI shell work

Verify:

- `git status --short`

### App-side track

#### A1 — Pin the Wikiwise checkout and native commands

Before app code changes begin, pin the external checkout path and native run/build/test commands.

Required outcomes:

- define `WIKIWISE_CHECKOUT=<absolute path to the external app repo>`
- record the app repo branch used for this work
- record the app-native install, dev, build, and test commands

This repo does not currently contain the external Wikiwise source checkout, so this pinning step is mandatory before app implementation begins.

Done when:

- another operator can enter the app checkout and run its native verification commands without discovery work

Verify:

- `git -C <WIKIWISE_CHECKOUT> status --short`
- `<app-native install command>`
- `<app-native build command>`
- `<app-native test command>`

#### A2 — Implement the workflow shell in the app checkout

The app-side task is to build the shell, not to relocate canonical content ownership.

Required outcomes:

- app-side routing for page, index, search, and graph/map surfaces
- a reusable page chrome and navigation model
- responsive behavior for desktop and mobile
- shell behavior that consumes repo-side fixture/export data rather than rewriting canonical content

The app-side shell may borrow structure from the current generated outputs, but it should own its own routing, layout, and interactions.

Done when:

- the shell can render the agreed sample pages and shared bundle data without repo-side manual intervention

Verify:

- app-native page route smoke test
- app-native search smoke test
- app-native graph/map smoke test

#### A3 — Keep app-side transformations honest

If the app needs a transform layer between repo export data and rendered UI, that transform must be explicit and documented.

Required outcomes:

- app code does not silently depend on undocumented repo file naming quirks
- any transform between repo bundle shape and app view model is checked into the app repo and named
- if app-side needs new repo-side fields, those become repo contract changes, not ad hoc hacks

Done when:

- integration issues show up as contract diffs, not hidden app-only assumptions

### Integration track

#### I1 — Reconcile the contract

Once repo-side export work and app-side shell work both exist, reconcile the two into one explicit contract.

Required outcomes:

- confirm the app only reads the agreed bundle and canonical deep-link surfaces
- confirm the repo only owns content/export data and not shell-specific logic
- decide whether repo-owned HTML under `canonical/wiki-site/` remains necessary

Preferred decision:

- keep repo-owned export data
- move shell ownership fully to the app checkout
- retain repo-owned HTML only if it is still needed as a generated compatibility fixture

Done when:

- both tracks can be described cleanly in one paragraph without caveats

#### I2 — Run the end-to-end smoke matrix

The rollout is not complete until the same sample set works through the full path.

Smoke matrix:

| Check | Expectation |
|---|---|
| Repo export build | bundle exists and contains the required files |
| Sample concept page | renders in app shell |
| Sample source page | renders in app shell |
| Sample output page | renders in app shell |
| Search | returns at least one known page from the sample set |
| Graph/map | loads from shared graph payload |
| Canonical links | app can deep-link to source/thesis/data surfaces without writing them |
| Write boundaries | no app-side writes land in canonical lanes |

Recommended sample set:

- concept: `n3-wafer-crunch`
- source: `nvda-q4-fy2026`
- output: `long-term-value-chain-thesis`

Done when:

- all rows pass on the same contract version

#### I3 — Close out the rollout

Close-out work should update the handoff state after the contract is proven, not before.

Required outcomes:

- update the relevant repo-side docs to point at the final contract
- update the app-side docs/readme if needed
- record the final status of `canonical/wiki-site/`: retained as generated fixture or reduced to data-only export

Done when:

- a new operator can understand the repo/app split from current docs alone

## Gating Assumptions

- The external Wikiwise checkout path is currently unknown inside this repo and must be pinned during `A1`.
- App-native toolchain commands are not yet recorded here because the checkout is external to this repo.
- The current repo already contains a generated `canonical/wiki-site/` bundle; this spec assumes it can be treated as the initial fixture/export surface for app-side work.
- If repo-side discovers that the current bundle is not reproducible, that becomes the top repo-side blocker before deeper integration proceeds.

## Non-Goals

- redefining the canonical stage map away from `10-wiki` through `50-reports`
- moving app source code into `semi-stocks-2`
- allowing app-side writes to canonical lanes
- treating repo-owned HTML under `canonical/wiki-site/` as source of truth
- reopening the completed April 10 migration as if canonical lane creation were still the active project

## Open Decisions To Resolve During Execution

- Does the final app consume repo-owned HTML pages, or only lower-level exported data?
- Should `canonical/wiki-site/` remain a broad static export bundle, or be reduced to the minimum contract payload after the shell lands?
- Which exact docs should replace the April 10 migration handoff as the live entrypoint for future repo/app work?

## Definition Of Done

This rollout is done when all of the following are true:

- repo docs clearly distinguish canonical stages from generated integration surfaces
- the external Wikiwise checkout is pinned and has native verification commands recorded
- the app shell renders the agreed sample pages from repo-owned export data
- search and graph/map surfaces work against the same export contract
- no shell-specific code or ownership has leaked back into the canonical lanes
- the final ownership decision for `canonical/wiki-site/` is documented
