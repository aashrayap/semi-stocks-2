---
status: completed
feature: canonical-propagation-model
updated: 2026-04-10
---

# Design: canonical-propagation-model

## Relevant Principles

- Model the repo as a propagation system, not a generic project tree.
- The top-level authority boundary is `canonical/` versus `agents/`, not a flat pile of implementation folders.
- Preserve working terminology where it carries real behavior or tooling contracts. `wiki` is one of those terms.
- Split overloaded buckets when they hide multiple propagation stages. `data` needs narrowing; `thesis` needs separation.
- Keep source state, control-plane state, render code, and published outputs visibly distinct.
- Let repo-local skills absorb path-compatibility work so the root map can reflect the real authority model.
- Keep the stage map visually explicit without choosing Python-import-hostile package names.

## Decisions

- **Decision: use `docs/ + canonical/ + agents/ + tmp/` as the root map.**
  - Options considered:
    - Flat root lanes such as `wiki/`, `data/`, `thesis.yaml`, `engine/`, `reports/`.
    - A generic wrapper such as `project/`.
    - A canonical-versus-sidecar split at root.
  - Rationale:
    - The strongest architectural boundary in the repo is canonical source-of-truth versus sidecar automation.
    - A `canonical/` wrapper makes that boundary explicit and prevents the root from collapsing back into a generic project tree.
    - `project/` and similar wrappers say nothing about authority or flow.
  - Affected files or areas:
    - root docs
    - lane scaffolding
    - all migration target paths
  - Risks still open:
    - none that outweigh the clarity gain

- **Decision: use numbered stage lanes inside `canonical/`.**
  - Options considered:
    - Unprefixed canonical subfolders.
    - Numeric stage prefixes across the canonical pipeline.
  - Rationale:
    - Inside `canonical/`, lexical sort should reinforce the propagation order.
    - Prefixes are useful here because they visualize the funnel while staying scoped to the canonical lane instead of cluttering the repo root.
    - Using `10`, `20`, `30` leaves room for future insertions without renaming every stage.
  - Locked stage map:
    - `canonical/10-wiki/`
    - `canonical/20-data/`
    - `canonical/30-thesis/`
    - `canonical/40-engine/`
    - `canonical/50-reports/`
  - Risks still open:
    - none material; the repo-local ingest skill removes the main path-compatibility concern

- **Decision: preserve `wiki` as the knowledge-workspace stage name.**
  - Options considered:
    - Rename the wiki stage to a more abstract name such as `knowledge/`.
    - Keep `wiki` as the visible stage term.
  - Rationale:
    - `wiki` is a live workflow contract in both tooling and repo conventions.
    - The wiki shape already has stable semantics: `raw/`, `sources/`, `concepts/`, `outputs/`, plus schema/index/log.
    - Preserving `wiki` keeps terminology close to `semi-stocks` while still improving the higher-level authority model.
  - Affected files or areas:
    - repo-local ingest skills
    - wiki schema and rebuild flow
    - migrated wiki content
  - Risks still open:
    - none beyond normal migration rewrites

- **Decision: keep `data`, but narrow it to structured evidence only.**
  - Options considered:
    - Rename the stage entirely.
    - Keep `data` as a catch-all bucket.
    - Keep `data` but restrict it to structured evidence.
  - Locked contents:
    - `canonical/20-data/sources/`
    - `canonical/20-data/companies/`
  - Explicit exclusions:
    - thesis state
    - cross-lane process docs
    - generic update buckets
    - reports
  - Rationale:
    - `data` is the least clean term in the legacy repo, but the useful semantics inside it are still `sources` and `companies`.
    - Narrowing the stage keeps familiar terminology without preserving the old overlap.
    - The actual fix is to move thesis and process docs out, not to rename everything by force.
  - Risks still open:
    - the term remains broad, so docs and verify checks must enforce scope

- **Decision: create an explicit thesis stage at `canonical/30-thesis/thesis.yaml`.**
  - Options considered:
    - Keep `data/thesis.yaml`.
    - Promote `thesis.yaml` to repo root.
    - Create a dedicated thesis stage under `canonical/`.
  - Rationale:
    - Thesis is the narrowest canonical control plane and deserves its own propagation stage.
    - Putting thesis under `canonical/30-thesis/` preserves the canonical authority boundary while making the thesis stage explicit.
    - Keeping `thesis.yaml` inside that stage preserves current runtime semantics and leaves room for future thesis-local docs or schema files.
  - Affected files or areas:
    - wiki schema thesis links
    - canonical synthesis code
    - sidecar scheduling and prediction code
  - Risks still open:
    - none that justify collapsing thesis back into `data`

- **Decision: rename `src/` to `canonical/40-engine/`.**
  - Options considered:
    - Preserve `src/`.
    - Rename to `engine/`.
  - Rationale:
    - `src/` is a generic implementation wrapper.
    - `engine/` states the stage's actual job: read canonical state and render outputs.
    - Under `canonical/`, `40-engine/` makes the downstream flow obvious.
    - The stage directory should contain a package-safe `engine/` Python package so imports remain valid while the stage name stays ordered in the filesystem.
  - Affected files or areas:
    - canonical code paths
    - docs and verify commands
    - agent references to canonical code
  - Risks still open:
    - direct script entrypoints and `sys.path` setup need careful migration

- **Decision: keep `canonical/40-engine/` and `canonical/50-reports/` separate.**
  - Options considered:
    - Consolidate render code and rendered reports.
    - Keep them as distinct stages.
  - Rationale:
    - `40-engine/` is canonical source code.
    - `50-reports/` is downstream published output.
    - Merging them would blur source versus artifact boundaries and weaken the propagation model.
  - Affected files or areas:
    - report-generation commands
    - docs about published outputs
    - future publishing jobs
  - Risks still open:
    - none that justify a merge

- **Decision: create repo-local `ingest-semi` skills for Codex and Claude.**
  - Options considered:
    - Keep relying on user-level generic wiki discovery.
    - Install repo-local skills pinned to this repo's canonical wiki path.
  - Rationale:
    - This removes the main reason to force a top-level `wiki/`.
    - The legacy repo already has a working local Codex ingest skill worth adapting.
    - Repo-local skills let the canonical path contract drive the layout instead of the other way around.
  - Affected files or areas:
    - `.codex/skills/ingest-semi/SKILL.md`
    - `.claude/skills/ingest-semi/SKILL.md`
    - `AGENTS.md`
    - `CLAUDE.md`
  - Risks still open:
    - keep the local skills tight and repo-specific so they do not become a second generic wiki framework

- **Decision: put cross-lane process docs under `docs/process/`.**
  - Options considered:
    - Keep pipeline/process docs under `data/`.
    - Move them into `canonical/10-wiki/`.
    - Keep cross-lane docs under `docs/process/`.
  - Rationale:
    - Process docs are durable human guidance, not structured evidence.
    - Keeping them under `docs/` prevents `20-data/` from becoming a catch-all again.
    - Stage-local docs can still live beside their owning stage when truly subsystem-specific.
  - Affected files or areas:
    - migrated `data/research/*.md`
    - root docs and agent routing docs
  - Risks still open:
    - some legacy docs may still need later pruning or reclassification

- **Decision: remove the obsolete scaffold lanes once the canonical map is in place.**
  - Options considered:
    - Leave `research/`, `app/`, and `outputs/` around as historical scaffolding.
    - Remove them after replacement lanes exist.
  - Rationale:
    - Leaving both the old scaffold and the new canonical map at once would keep the root ambiguous.
    - The old scaffold directories are not the architecture being preserved.
  - Affected files or areas:
    - root tree
    - root docs
  - Risks still open:
    - stop if any obsolete scaffold lane contains real user content that should be preserved

## Open Risks

- Canonical and agent code both assume legacy flat paths, so waves that migrate `thesis`, `engine`, and report paths need disciplined path rewrites.
- `canonical/10-wiki/outputs/` and `canonical/50-reports/` must stay explicitly distinguished so query artifacts do not get mistaken for published outputs.
- The repo worktree may already contain partial wave-one edits; execution should reconcile them to this locked map rather than infer design from drift.
- `config.yaml` still needs a longer-term home. Keep it at repo root during migration until engine and agent path updates settle.

## Final Root Map

```text
docs/
  artifacts/
  process/
canonical/
  10-wiki/
    raw/
    sources/
    concepts/
    outputs/
  20-data/
    sources/
    companies/
  30-thesis/
    thesis.yaml
  40-engine/
    engine/
  50-reports/
agents/
tmp/
```

Operational compatibility note:

- Keep `config.yaml` at repo root during migration because existing agent code already expects it there.

## Working Interpretation

- `canonical/10-wiki/`: knowledge workspace, ingest landing zone, and query surface
- `canonical/20-data/`: structured evidence only
- `canonical/30-thesis/`: narrow control plane
- `canonical/40-engine/`: canonical synthesis and rendering code
- `canonical/40-engine/engine/`: package-safe Python module root for canonical synthesis code
- `canonical/50-reports/`: canonical published artifacts
- `agents/`: sidecar automation, drafts, logs, scheduler state, and experiments
- `tmp/`: scratch and migration quarantine space
