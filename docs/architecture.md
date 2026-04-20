# Architecture

## Goal

`semi-stocks-2` should make the propagation system explicit:

`canonical/10-wiki/raw -> canonical/10-wiki/sources|concepts -> canonical/20-data/sources|companies -> canonical/30-thesis/thesis.yaml -> canonical/40-engine -> canonical/50-reports`

`agents/` reads canonical state in parallel but writes sidecar state only under `agents/`.

## Root Lanes

### `canonical/`

Canonical source-of-truth lane.

- `canonical/10-wiki/` — immutable raw inputs plus LLM-owned knowledge pages and query outputs
- `canonical/20-data/` — structured evidence only
- `canonical/30-thesis/` — narrow control plane
- `canonical/40-engine/` — engine stage
- `canonical/50-reports/` — published outputs
- `canonical/site-data/` — generated data contract for repo-owned web readers; not a canonical propagation stage
- `canonical/site-reader/` — repo-owned web reader source consuming generated site data; not a canonical propagation stage

### `agents/`

Sidecar automation, drafts, logs, reports, experiments, and scheduler state. This lane may read canonical state broadly but should not become a second source of truth.

### `docs/`

Durable human-facing docs about repo-wide architecture, contracts, and operating process.

- `docs/process/` — cross-lane operational docs such as ingest and filing pipelines
- `docs/artifacts/` — planning artifacts and restart packages

### `tmp/`

Scratch space for local working files and transient migration artifacts.

## Canonical Stage Notes

### `canonical/10-wiki/`

Knowledge lane and ingest landing zone.

- `raw/` — immutable source material
- `sources/` — source-backed synthesis pages
- `concepts/` — durable concept pages
- `outputs/` — filed query and analysis outputs for the wiki workflow

### `canonical/20-data/`

Structured evidence lane.

- `sources/` — structured source snapshots and position data
- `companies/` — structured company-level models and claim-tracking state
- `thesis-proposals/` — structured evidence staging for pending thesis patches before promotion to `30-thesis/thesis.yaml`. One YAML file per proposed change. Evidence from multiple sources accretes into each proposal. Status: `pending` → `applied` | `rejected`.

`canonical/20-data/` does not own thesis or cross-lane process docs.

### `canonical/30-thesis/thesis.yaml`

The narrow canonical control plane. Only conclusions that have cleared the evidence funnel should land here.

### `canonical/40-engine/`

Canonical synthesis and rendering stage. The stage contains a package-safe `engine/` Python package plus the `canonical/40-engine/report.py` entrypoint.

### `canonical/50-reports/`

Canonical published artifacts rendered from `canonical/40-engine/`. These are downstream outputs and stay separate from `canonical/10-wiki/outputs/`.

### `canonical/site-data/`

Generated JSON data contracts derived from canonical wiki, data, thesis, and report state. This is the preferred repo-owned app boundary for new web reader surfaces such as Signal Desk. It may be deleted and rebuilt from `canonical/40-engine/`.

### `canonical/site-reader/`

Repo-owned web reader source that consumes `canonical/site-data/` only. It is presentation/source code for a reader, not canonical research content and not a propagation stage.

## Principles

- Manual research lands in `canonical/10-wiki/` first.
- Structured numeric and verifiable state lives in `canonical/20-data/`.
- `canonical/30-thesis/thesis.yaml` stays narrow and machine-readable.
- `canonical/40-engine/` and `canonical/50-reports/` remain separate authority layers.
- Generated app surfaces (`site-data`, `site-reader`) must not become new sources of truth.
- Sidecar automation reads canonical lanes but writes under `agents/`.
- Root should show authority, not legacy implementation history.

## Runtime

- Python runtime is managed with `uv`.
- Use `uv run python canonical/40-engine/report.py` for canonical report generation.
- Use `uv run python ...` for agent scripts and verify commands.
