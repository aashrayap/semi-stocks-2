# agents/ — Agent Fleet Workspace

You are an automated agent operating in the semi-stocks research repo.

## Boundary Rules

- **FULL READ access** to canonical state under `canonical/`, root `config.yaml`, and repo docs
- **WRITE ONLY to agents/** — do not create or modify files outside this directory

## Key Files to Read

| File | Why |
|---|---|
| `canonical/30-thesis/thesis.yaml` | Bottleneck cascade status, ticker map, next_earnings dates, signals |
| `docs/process/earnings-pipeline.md` | Full earnings + 13F ingestion process |
| `docs/process/13f-pipeline-design.md` | 13F automation design |
| `config.yaml` | Source URLs, CIKs, deep_dive ticker list |
| `canonical/20-data/companies/<TICKER>/` | Quarterly earnings YAML with forward_claims, thesis_signals, positioning |
| `canonical/20-data/sources/` | Structured source snapshots |
| `canonical/10-wiki/schema.md` | Wiki conventions — read before wiki reads |
| `canonical/10-wiki/index.md` | Wiki page catalog |
| `canonical/10-wiki/sources/` | Synthesized earnings and 13F pages |
| `canonical/10-wiki/concepts/` | Compiled knowledge articles |
| `canonical/40-engine/engine/synthesis.py` | Agreement map, divergences, cascade logic |
| `canonical/40-engine/report.py` | Canonical HTML report entrypoint |

## Operating Rules

1. Drafts are proposals. A human reviews and decides whether to promote content back to canonical lanes.
2. Reports run parallel. Agent reports do not replace canonical reports.
3. Always log runs under `agents/logs/`.
4. Use `uv run python ...` for execution.
5. Respect the funnel: `canonical/10-wiki/` -> `canonical/20-data/` -> `canonical/30-thesis/`.
