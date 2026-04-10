---
feature: canonical-propagation-model
status: completed
updated: 2026-04-10
---

# semi-stocks-2 Vision Handoff

## Why this repo exists

`semi-stocks-2` should not become a mechanical copy of `semi-stocks`.

The goal is to rebuild the repo around the real operating model already present in the legacy system:

- wide to narrow research propagation
- explicit canonical versus sidecar authority
- clean separation between knowledge capture, structured evidence, thesis state, render code, and published outputs
- support for both manual wiki-centric research and scheduled automation without creating a second source of truth

In short:

`semi-stocks-2` should make the propagation system obvious in the filesystem instead of hiding it behind historical wrapper names.

## Current state of `semi-stocks-2`

The migration has been executed and the canonical structure is live.

- The old scaffold root map (`research/`, `app/`, `outputs/`) is obsolete.
- The canonical filesystem and runtime are now in place under `canonical/`.
- Python runtime is now managed with `uv`.
- The migrated repo data from `semi-stocks` now lands in the canonical lanes instead of the earlier flat-root staging layout.
- The remaining gaps are verification depth on a few non-core agent flows, not structural migration work.

The canonical propagation artifacts now record what was decided and executed:

- `01_spec.md` defines the redesign goal and scope
- `02_questions.md` captures the research questions
- `03_research.md` records the findings from the legacy repo and wiki tooling
- `04_design.md` locks the final root map and stage boundaries
- `05_tasks.md` defines the phased execution plan, verify commands, and execution update

## Locked root map

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
  50-reports/
agents/
tmp/
```

Supporting compatibility decision:

- Keep `config.yaml` at repo root during migration because existing agent code already expects it there.
- Use `uv` as the Python runtime entrypoint for verification and scripted execution.

Explicit non-goals for the root map:

- no flat root `wiki/`, `data/`, `engine/`, `reports/` architecture
- no generic `project/` wrapper
- no broad `research/` or `app/` root lanes
- no thesis state inside `20-data/`
- no merge of engine and reports

## Why this is the right revision

This lock set reflects the earlier reasoning that was easy to lose once the flat-root compromise entered the thread.

- The most important top-level boundary is `canonical/` versus `agents/`.
- `wiki` should be preserved as a real workflow and tooling concept, but it does not need to sit at repo root once repo-local ingest skills exist.
- `data` should survive only as a narrowed structured-evidence stage, not as a broad catch-all.
- Thesis is distinct enough to deserve its own canonical stage.
- `engine` and `reports` should remain separate because one is source logic and the other is downstream output.
- Numeric ordering is useful inside `canonical/`, where it reinforces the pipeline instead of cluttering the entire repo root.
- `canonical/40-engine/` should be treated as a stage directory that contains a package-safe `engine/` module root.

## Desired behavior

1. Manual research lands in `canonical/10-wiki/raw/`.
2. Durable learnings live in `canonical/10-wiki/sources/` and `canonical/10-wiki/concepts/`.
3. Structured numeric and verifiable company/source state lives in `canonical/20-data/`.
4. Only thesis-level conclusions reach `canonical/30-thesis/thesis.yaml`.
5. `canonical/40-engine/` reads canonical state and renders outputs.
6. Canonical published outputs live in `canonical/50-reports/`.
7. Scheduled jobs and agents write to sidecar state under `agents/` first, then promote reviewed changes back into canonical stages.

That behavior is now implemented for the core repo paths.

## Manual ingest versus scheduled ingest

Manual research path:

- external evidence
- `canonical/10-wiki/raw/`
- `canonical/10-wiki/sources/` and `canonical/10-wiki/concepts/`
- `canonical/20-data/sources/` and `canonical/20-data/companies/`
- `canonical/30-thesis/thesis.yaml`
- `canonical/40-engine/`
- `canonical/50-reports/`

Scheduled ingest path:

- feed polling, calendars, URL fetches, and draft automation under `agents/`
- sidecar drafts and state remain under `agents/`
- human review decides whether to promote changes into canonical wiki or structured-evidence stages
- thesis is updated only when evidence changes the actual control-plane state

Key boundary:

- reusable learnings and narrative synthesis belong in `canonical/10-wiki/concepts/`
- exact machine-readable company or source facts belong in `canonical/20-data/companies/` and `canonical/20-data/sources/`

## Decisions made so far

- Use `docs/ + canonical/ + agents/ + tmp/` at repo root.
- Use numbered canonical stages:
  - `10-wiki`
  - `20-data`
  - `30-thesis`
  - `40-engine`
  - `50-reports`
- Preserve `wiki` as the knowledge-workspace stage.
- Keep `data`, but narrow it to structured evidence only.
- Move thesis into `canonical/30-thesis/thesis.yaml`.
- Rename `src/` to `canonical/40-engine/`.
- Keep `canonical/40-engine/` separate from `canonical/50-reports/`.
- Create repo-local `ingest-semi` skills for both Codex and Claude.
- Move cross-lane process docs under `docs/process/`.
- Preserve the agent-side rule: read all canonical state, write only under `agents/`, promote only through human review.

## Migration truths learned from the legacy repo

From `semi-stocks`, the stable semantics are:

- `wiki/raw/ -> wiki/sources/ -> data/companies/ or data/sources/ -> data/thesis.yaml -> src/synthesis.py -> report`
- `agents/` is already a sidecar lane with the correct authority boundary
- `thesis.yaml` already behaves as the control plane
- `wiki/schema.md` and the wiki skill make `wiki` a real operating concept

The biggest migration risks are:

- hard-coded path assumptions in canonical and agent code
- the legacy ingest skill's fixed wiki and thesis targets
- `data/` currently mixing structured state, process docs, updates, and thesis
- confusing wiki query artifacts with canonical published reports

## Execution Result

Executed successfully:

- canonical filesystem moved under `canonical/10-wiki`, `20-data`, `30-thesis`, `40-engine`, and `50-reports`
- package-safe engine layout implemented under `canonical/40-engine/engine/`
- root docs, agent routers, and repo-local ingest skills repointed to canonical paths
- wiki generated state rebuilt against `canonical/10-wiki`
- canonical report rebuilt at `canonical/50-reports/latest.html`
- agent report rebuilt at `agents/reports/latest.html`
- earnings-calendar and pre-earnings prediction flows executed successfully under `uv`
- historical autoagent backtests now replay successfully against the legacy-shaped snapshots
- transcript fetch dry run and post-earnings scorer dry run both execute successfully

## Verified Commands

- `uv run python ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`
- `uv run python -m py_compile canonical/40-engine/engine/*.py canonical/40-engine/engine/sources/*.py canonical/40-engine/report.py agents/src/*.py agents/autoagent/backtest.py`
- `uv run python canonical/40-engine/report.py`
- `uv run python agents/src/report.py`
- `uv run python agents/src/earnings_calendar.py --days 14`
- `uv run python agents/src/pre_earnings_predictor.py --all-upcoming`

## Residual Risk

- `agents/src/transcript_fetcher.py` has not been run through a live network fetch in this migration pass.
- `agents/src/post_earnings_scorer.py` has not been exercised through a human-driven interactive scoring flow in this migration pass.
- These are test gaps, not structural blockers.

## Suggested Next Session

Continue from the live canonical repo, not from the old migration plan.

Good next-session targets:

- deeper validation of `transcript_fetcher.py`
- deeper validation of `post_earnings_scorer.py`
- ongoing thesis/content iteration inside the canonical lanes
- future research and agent work using `docs/ash.md`, `README.md`, and the repo-local `ingest-semi` skills as the primary operator map
