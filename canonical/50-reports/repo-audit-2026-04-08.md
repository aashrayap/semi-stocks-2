# Repository Audit — 2026-04-08

## Snapshot

| Lens | Scope | Current State | Verdict |
|---|---|---:|---|
| Raw | `wiki/raw/` | 2 files | Provenance too loose |
| Research | `wiki/sources/`, `wiki/concepts/`, `data/sources/`, `data/companies/`, `data/research/` | 5 source pages, 6 concept pages, 2 company YAMLs | High signal, thin coverage |
| Thesis | `data/thesis.yaml`, `src/synthesis.py` | 1 narrative control plane | Useful, but semantically loose |
| Report | `src/report.py`, `reports/`, `wiki/outputs/`, `agents/reports/` | 3 output surfaces | Good monitor, weak trade packet |

```text
Truth Path
external source
  -> raw
  -> research
  -> thesis
  -> report
  -> trade

Seam Grade
raw      -> research   RED
research -> thesis     RED
thesis   -> report     YELLOW
report   -> trade      RED
```

## Coverage

| Item | Intended | Actual | Gap |
|---|---:|---:|---:|
| Deep-dive company coverage | 7 | 2 | 5 |
| Coverage ratio | 100% | 28.6% | -71.4 pts |
| Raw earnings/filing captures | ~20 companies target | 2 | large |
| Wiki output trade notes | n/a | 2 | underused in final report |

Deep-dive names configured: `CRWV`, `NVDA`, `MU`, `COHR`, `INTC`, `TSM`, `LITE`  
Structured company coverage today: `CRWV`, `NVDA`

## Core Findings

### Raw
- `wiki/raw/` is treated as immutable ingest, but “raw” is not consistently primary-source. `wiki/raw/nvda-q4-fy2026-transcript.md` is already a compiled artifact from multiple secondary sites.
- The layer has no enforced provenance contract: no canonical source URL standard, no checksum, no primary/secondary marker, no trace-back fields.
- Raw does not make money directly. Its job is preserving exact evidence so later claims can be trusted.

### Research
- This is the strongest layer conceptually. Leopold, Baker, SemiAnalysis, and earnings all exist in both readable and structured form.
- The weakness is penetration, not idea quality. Only 2 of 7 intended deep-dive names have `data/companies/*` depth, so most thesis claims still depend on manual reconstruction.
- Queryability is convention-driven. A human can traverse it; the codebase does not really execute the documented wiki-first query model.

### Thesis
- `data/thesis.yaml` is the real control plane, but it mixes stage state, narrative commentary, cycle logic, and ticker routing in one hand-edited blob.
- Taxonomy drifts across layers. Cascade stages are human names; ticker routing uses tags like `gpu_cloud`, `foundry`, and `copper_signal_integrity` that do not map cleanly back to cascade stages.
- Thesis is good at saying what is true. It is weak at encoding what to trade, when, and with what invalidation.

### Report
- The canonical report is a bottleneck dashboard, not a trading report.
- `wiki/outputs/*` contains the most trade-shaped work, but those outputs are not first-class inputs to `src/report.py`.
- `agents/reports/daily-2026-04-07.md` is tactically useful, but it can drift from canonical truth because it is not automatically promoted back into `wiki/` or `data/`.

## Source Feed Assessment

| Source | Current Role | Strength | Limitation |
|---|---|---|---|
| Leopold 13F | Bottleneck-through-positioning signal | High conviction, concentrated | 45-day lag, thesis bias |
| Baker 13F | Cycle + supply-chain positioning signal | Deep semi fluency | 45-day lag, options/hedges need leg-aware handling |
| SemiAnalysis | Supply-chain ground truth proxy | Earliest bottom-up bottleneck data | Needs explicit credibility weighting |
| Earnings | Direct operating confirmation | Most falsifiable source | Coverage still narrow |

## What Actually Makes Money

- Raw: exact evidence, not insight.
- Research: cross-source compression into comparable, falsifiable claims.
- Thesis: ranking bottlenecks, conflicts, catalysts, and timing.
- Report: emitting a trade packet with trigger, horizon, invalidation, hedge, and review date.

Right now the repo is strongest at `research -> thesis narrative`, and weakest at `thesis -> report -> trade`.

## Hard Findings

- Multi-leg 13F rows were being collapsed to the first matching leg in the source adapter, which understated Baker exposure in the report and cascade tables.
- The report summary language implied the only full overlap was optical interconnect, while the implementation’s “full agreement” logic also surfaced `CRWV` and `INTC`.
- The earnings dashboard was rendering raw SemiAnalysis dict objects instead of readable signal summaries.
- TODO/process tracking is stale relative to the repo state: NVDA is already ingested, but `TODO.md` still lists it as remaining work.

## Changes Made During Audit

- Added a concise four-lens audit mapping to `README.md`.
- Fixed multi-leg 13F aggregation in `src/sources/fund_13f.py`.
- Updated summary wording in `src/synthesis.py` so optical overlap is described more accurately.
- Fixed SemiAnalysis rendering in `src/report.py` so dashboard rows show human-readable signal summaries.
- Updated `TODO.md` so remaining deep-dive work matches actual repo state.
- Regenerated the canonical HTML report after the source aggregation fix.

## Post-Fix Impact

| Item | Before | After |
|---|---:|---:|
| Baker NVDA shown in report | $653M | $1.01B |
| Baker MU shown in report | $211M | $411M |
| Baker COHR shown in report | $228M | $394M |
| Baker N3 stage exposure | $671M | $1.03B |
| Baker memory stage exposure | $211M | $411M |
| Baker pluggable optics stage exposure | $703M | $869M |

## Priority Backlog

### P0
- Define a strict raw provenance contract.
- Complete the remaining 5 deep-dive company YAMLs.
- Add evidence fields to research artifacts: `claim_id`, `source_ref`, `confidence`, `last_verified`, `why_it_matters`.
- Add a canonical trade packet layer between thesis and report.

### P1
- Make wiki querying real, not just documented.
- Add source weighting by freshness, bias, and historical hit rate.
- Promote `wiki/outputs/*` into the report build path.

### P2
- Unify thesis taxonomy with stable stage ids.
- Add performance feedback from predictions and thesis calls back into the canonical report.

## Bottom Line

The repository already has the right lane structure. The main gap is not conceptual architecture. It is evidence discipline at the left edge, coverage in the middle, and trade packet generation at the right edge.
