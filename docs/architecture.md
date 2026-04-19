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
- `canonical/site-data/` — generated reader contract; not a canonical propagation stage
- `canonical/site-reader/` — local static reader over `canonical/site-data/`

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

Generated JSON contract derived from canonical wiki, structured data, thesis, and engine synthesis state. This surface is repo-owned reader input, not a sixth canonical stage or a hand-maintained source lane.

### `canonical/site-reader/`

Local static reader for `canonical/site-data/`. The reader is presentation only and must not parse canonical markdown or YAML directly.

## Principles

- Manual research lands in `canonical/10-wiki/` first.
- Structured numeric and verifiable state lives in `canonical/20-data/`.
- `canonical/30-thesis/thesis.yaml` stays narrow and machine-readable.
- `canonical/40-engine/` and `canonical/50-reports/` remain separate authority layers.
- `canonical/site-data/` and `canonical/site-reader/` remain replaceable generated/presentation surfaces.
- Sidecar automation reads canonical lanes but writes under `agents/`.
- Root should show authority, not legacy implementation history.

## Runtime

- Python runtime is managed with `uv`.
- Use `uv run python canonical/40-engine/report.py` for canonical report generation.
- Use `uv run python ...` for agent scripts and verify commands.
