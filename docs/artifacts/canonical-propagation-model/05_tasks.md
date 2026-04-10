---
status: completed
feature: canonical-propagation-model
updated: 2026-04-10
---

# Tasks: canonical-propagation-model

## Autonomous Execution Policy

- Treat this file and `06_handoff.md` as the execution source of truth.
- Keep `/Users/ash/Documents/2026/semi-stocks` read-only. Migration work happens in `semi-stocks-2`.
- Use `uv` for Python environment management and command execution.
- Prefer additive copy and regeneration over destructive moves until the final audit wave.
- Continue wave-by-wave without pausing when verify commands pass.
- If the repo already contains partial migration edits, reconcile them to the locked map instead of recreating work or inferring architecture from drift.
- If a destination contains non-scaffold content that conflicts with the locked map, stop the active wave and record the blocker in `06_handoff.md`.

## Execution Waves

1. Wave 1: lock the root map, install repo-local ingest skills, rewrite root docs, scaffold the canonical lanes, and remove the obsolete scaffold.
2. Wave 2: migrate the wiki lane and verify ingest/query/lint behavior.
3. Wave 3: migrate structured evidence, separate thesis, and relocate cross-lane process docs.
4. Wave 4: migrate canonical engine code into a package-safe `canonical/40-engine/engine/` layout and restore report generation.
5. Wave 5: migrate sidecar agents and scheduled ingest around the new canonical paths.
6. Wave 6: remove shims, audit the repo, and refresh the handoff.

## Execution Update

Executed on 2026-04-10:

- Waves 1 through 5 are complete in the live repo.
- The canonical shell exists and contains migrated wiki, structured data, thesis state, engine code, and reports.
- Runtime and verification now use `uv`.
- Canonical and agent reports both rebuild successfully from the canonical paths.
- Repo-local Codex and Claude ingest skills now target `canonical/10-wiki/`.

Remaining follow-up items are optional hardening, not migration blockers:

- run the live networked fetch path in `agents/src/transcript_fetcher.py`
- run a human-in-the-loop interactive scoring pass through `agents/src/post_earnings_scorer.py`
- continue future repo iteration from the canonical structure instead of reopening flat-root compatibility work

## Task List

### T01 - Lock the final root map

**Files to modify**
- `docs/artifacts/canonical-propagation-model/04_design.md`
- `docs/artifacts/canonical-propagation-model/05_tasks.md`
- `docs/artifacts/canonical-propagation-model/06_handoff.md`

**Depends on**
- none

**Acceptance criteria**
- The root map is explicit and no structural decisions remain open for wave 1.
- The locked root structure is:
  - `docs/`
  - `canonical/`
  - `agents/`
  - `tmp/`
- The locked canonical stage structure is:
  - `canonical/10-wiki/`
  - `canonical/20-data/`
  - `canonical/30-thesis/`
  - `canonical/40-engine/`
  - `canonical/50-reports/`
- The destination for cross-lane process docs is explicit: `docs/process/`.

**Verify**
- `sed -n '1,280p' docs/artifacts/canonical-propagation-model/04_design.md`
- `sed -n '1,320p' docs/artifacts/canonical-propagation-model/06_handoff.md`

**Parallel-safe**
- none

**Out of scope**
- modifying runtime files outside the planning artifacts

### T02 - Install repo-local Codex ingest skill

**Files to create or modify**
- `.codex/skills/ingest-semi/SKILL.md`

**Depends on**
- `T01`

**Acceptance criteria**
- The skill pins `/Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki` as the only wiki root.
- The skill reads `canonical/10-wiki/schema.md` first.
- The skill preserves semi-stocks-specific ingest behavior:
  - never edit `canonical/10-wiki/raw/`
  - prefer updating existing `sources/` and `concepts/` pages
  - preserve `Forward Claims`, `Thesis Signal`, and `Semi-stocks data` sections where relevant
  - propose thesis patches against `canonical/30-thesis/thesis.yaml`
- After every wiki write, the skill updates `canonical/10-wiki/index.md`, rebuilds generated state, and appends to `canonical/10-wiki/log.md`.

**Verify**
- `sed -n '1,260p' .codex/skills/ingest-semi/SKILL.md`

**Parallel-safe**
- can run in parallel with `T03` and `T05`

**Out of scope**
- migrating wiki content

### T03 - Install repo-local Claude ingest skill

**Files to create or modify**
- `.claude/skills/ingest-semi/SKILL.md`

**Depends on**
- `T01`

**Acceptance criteria**
- Claude has a repo-local ingest entrypoint for this repo.
- The skill pins the same canonical wiki and thesis paths as the Codex skill.
- The skill stays deterministic and minimal rather than reintroducing generic wiki discovery.

**Verify**
- `sed -n '1,260p' .claude/skills/ingest-semi/SKILL.md`

**Parallel-safe**
- can run in parallel with `T02` and `T05`

**Out of scope**
- broader Claude repo guidance beyond ingest routing

### T04 - Rewrite root docs and agent routers

**Files to modify**
- `README.md`
- `docs/architecture.md`
- `docs/doc-contract.md`
- `AGENTS.md`
- `CLAUDE.md`

**Depends on**
- `T01`
- `T02`
- `T03`

**Acceptance criteria**
- Root docs describe the final `docs/ + canonical/ + agents/ + tmp/` model, not the obsolete scaffold.
- `AGENTS.md` and `CLAUDE.md` route wiki ingest work to the repo-local `ingest-semi` skill.
- Root docs keep cross-lane docs under `docs/` and identify `canonical/` as the source-of-truth lane.
- Agent docs preserve the sidecar rule: agents may read canonical lanes broadly but write sidecar state under `agents/`.

**Verify**
- `sed -n '1,220p' README.md`
- `sed -n '1,260p' docs/architecture.md`
- `sed -n '1,260p' docs/doc-contract.md`
- `rg -n "canonical/|10-wiki|20-data|30-thesis|40-engine|50-reports|agents/|ingest-semi" README.md docs AGENTS.md CLAUDE.md -S`

**Parallel-safe**
- may run in parallel with `T05` once `T02` and `T03` are done

**Out of scope**
- copying legacy content

### T05 - Scaffold the target lanes and remove the obsolete scaffold

**Files or folders to create**
- `docs/process/`
- `canonical/`
- `canonical/10-wiki/raw/`
- `canonical/10-wiki/sources/`
- `canonical/10-wiki/concepts/`
- `canonical/10-wiki/outputs/`
- `canonical/20-data/sources/`
- `canonical/20-data/companies/`
- `canonical/30-thesis/`
- `canonical/40-engine/`
- `canonical/50-reports/`

**Files or folders to remove**
- `research/`
- `app/`
- `outputs/`

**Depends on**
- `T01`

**Acceptance criteria**
- The canonical stage lanes exist in the filesystem.
- `agents/` and `tmp/` remain in place.
- Obsolete scaffold directories are removed once the replacements exist.
- The repo root visibly matches the final map from `04_design.md`.

**Verify**
- `find . -maxdepth 3 -type d | sort`
- `test -d canonical/10-wiki`
- `test -d canonical/20-data`
- `test -d canonical/30-thesis`
- `test -d canonical/40-engine`
- `test -d canonical/50-reports`
- `test ! -d research`
- `test ! -d app`
- `test ! -d outputs`

**Parallel-safe**
- can run in parallel with `T02` and `T03`

**Out of scope**
- moving legacy files into the new lanes

### T06 - Migrate the wiki lane

**Source paths**
- `/Users/ash/Documents/2026/semi-stocks/wiki/**`

**Target files or folders**
- `canonical/10-wiki/schema.md`
- `canonical/10-wiki/index.md`
- `canonical/10-wiki/log.md`
- `canonical/10-wiki/raw/`
- `canonical/10-wiki/sources/`
- `canonical/10-wiki/concepts/`
- `canonical/10-wiki/outputs/`
- generated state rebuilt into:
  - `canonical/10-wiki/_index.json`
  - `canonical/10-wiki/_backlinks.json`
  - `canonical/10-wiki/_lint.json`

**Depends on**
- `T04`
- `T05`

**Acceptance criteria**
- Authored wiki content is migrated into `semi-stocks-2/canonical/10-wiki`.
- `canonical/10-wiki/schema.md` points to `../30-thesis/thesis.yaml` and `../20-data/sources/`.
- Generated state is rebuilt in the new repo instead of copied blindly.
- Repo-local `ingest-semi` targets the migrated wiki successfully.

**Verify**
- `uv run python ~/.dot-agent/skills/wiki/scripts/rebuild_index.py /Users/ash/Documents/2026/semi-stocks-2/canonical/10-wiki`
- `rg -n "thesis_link|data_sources|sources/|concepts/|outputs/" canonical/10-wiki/schema.md -S`

**Parallel-safe**
- none

**Out of scope**
- canonical code-path migration

### T07 - Migrate structured evidence

**Source paths**
- `/Users/ash/Documents/2026/semi-stocks/data/sources/**`
- `/Users/ash/Documents/2026/semi-stocks/data/companies/**`

**Target files or folders**
- `canonical/20-data/sources/`
- `canonical/20-data/companies/`

**Depends on**
- `T05`
- `T06`

**Acceptance criteria**
- Structured source snapshots and company YAMLs are migrated under `canonical/20-data/`.
- `canonical/20-data/` contains structured evidence only, not thesis or process-doc spillover.
- Wiki source pages can still point to the structured evidence layer cleanly.

**Verify**
- `find canonical/20-data -maxdepth 3 -type f | sort | sed -n '1,160p'`
- `rg -n "20-data/sources|20-data/companies" canonical/10-wiki canonical/20-data -S`

**Parallel-safe**
- can run in parallel with `T09` after `T05`

**Out of scope**
- thesis promotion and code-path updates

### T08 - Separate and migrate the thesis control plane

**Source files**
- `/Users/ash/Documents/2026/semi-stocks/data/thesis.yaml`

**Target files**
- `canonical/30-thesis/thesis.yaml`

**Files to modify**
- `canonical/10-wiki/schema.md`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- canonical and sidecar code paths that still reference `data/thesis.yaml`

**Depends on**
- `T07`

**Acceptance criteria**
- Thesis exists at one canonical path: `canonical/30-thesis/thesis.yaml`.
- No canonical docs or runtime code still depend on `data/thesis.yaml`.
- Thesis remains a narrow control plane rather than moving into `20-data/` or `50-reports/`.

**Verify**
- `uv run python - <<'PY'\nfrom pathlib import Path\nimport yaml\npath = Path('canonical/30-thesis/thesis.yaml')\nprint(path.exists())\nprint(sorted(yaml.safe_load(path.read_text()).keys())[:8])\nPY`
- `rg -n "data/thesis.yaml|canonical/30-thesis/thesis.yaml" . -S`

**Parallel-safe**
- none

**Out of scope**
- engine rename or full report-path migration

### T09 - Relocate cross-lane process docs

**Source files**
- `/Users/ash/Documents/2026/semi-stocks/data/research/earnings-pipeline.md`
- `/Users/ash/Documents/2026/semi-stocks/data/research/13f-pipeline-design.md`

**Target files**
- `docs/process/earnings-pipeline.md`
- `docs/process/13f-pipeline-design.md`

**Files to modify**
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- any migrated docs that still point at `data/research/`

**Depends on**
- `T05`

**Acceptance criteria**
- Durable process docs no longer live inside structured evidence lanes.
- Root docs point to `docs/process/` for cross-lane operational guidance.
- No active docs still tell agents to read `data/research/...`.

**Verify**
- `find docs/process -maxdepth 2 -type f | sort`
- `rg -n "data/research|docs/process" README.md docs AGENTS.md CLAUDE.md -S`

**Parallel-safe**
- can run in parallel with `T07`

**Out of scope**
- subsystem-local docs that truly belong near their owning stage

### T10 - Migrate the canonical engine and report path

**Source paths**
- `/Users/ash/Documents/2026/semi-stocks/src/**`
- `/Users/ash/Documents/2026/semi-stocks/reports/**`

**Target files or folders**
- `canonical/40-engine/`
- `canonical/40-engine/engine/`
- `canonical/50-reports/`

**Depends on**
- `T08`
- `T09`

**Acceptance criteria**
- Canonical code lives under `canonical/40-engine/engine/` with package-safe imports.
- Canonical code reads `canonical/10-wiki/`, `canonical/20-data/`, and `canonical/30-thesis/thesis.yaml`.
- Report generation succeeds in `semi-stocks-2`.
- Generated reports land in `canonical/50-reports/`, not under `40-engine/` or `10-wiki/outputs/`.

**Verify**
- `uv run python -m py_compile canonical/40-engine/engine/*.py canonical/40-engine/report.py`
- `uv run python canonical/40-engine/report.py`
- `find canonical/50-reports -maxdepth 2 -type f | sort | sed -n '1,120p'`

**Parallel-safe**
- none

**Out of scope**
- agent-side scheduled automation

### T11 - Migrate agents and scheduled ingest

**Source paths**
- `/Users/ash/Documents/2026/semi-stocks/agents/**`

**Target files or folders**
- `agents/`
- any scheduler entrypoints or configs required by the repo-local ingest flow

**Depends on**
- `T10`

**Acceptance criteria**
- Agent-side code reads only the new canonical paths.
- Agent-side writes remain under `agents/`.
- Scheduled ingest lands in sidecar state first and promotes only through explicit review.
- No agent code still assumes `research/`, `app/`, `outputs/`, flat `wiki/`, flat `data/`, root `thesis.yaml`, or `src/`.

**Verify**
- `uv run python -m py_compile agents/src/*.py`
- `uv run python agents/src/earnings_calendar.py --days 14`
- `rg -n "research/|app/|outputs/|data/thesis.yaml|src/|wiki/|data/|thesis.yaml|reports/" agents -S`

**Parallel-safe**
- none

**Out of scope**
- deleting the legacy repo

### T12 - Remove temporary shims and complete the migration audit

**Files to modify**
- any temporary compatibility shims, copy manifests, or transitional docs created during `T02` to `T11`
- `docs/artifacts/canonical-propagation-model/06_handoff.md`

**Depends on**
- `T11`

**Acceptance criteria**
- `semi-stocks-2` works without relying on live paths inside the legacy repo.
- Obsolete scaffold names are gone from the active repo.
- Any temporary adapters are either deleted or explicitly documented as intentional.
- `06_handoff.md` records the completed waves, residual gaps, and next checkpoint.

**Verify**
- `rg -n "/Users/ash/Documents/2026/semi-stocks|legacy|compat|research/|app/|outputs/" . -S`
- `git status --short`

**Parallel-safe**
- none

**Out of scope**
- future thesis evolution beyond the current control-plane split
