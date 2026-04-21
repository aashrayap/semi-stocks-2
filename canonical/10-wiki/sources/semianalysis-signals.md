---
title: "SemiAnalysis Signals"
tags: [semianalysis, supply-chain, dylan-patel, signals]
sources: [../../20-data/sources/semianalysis/signals.yaml]
created: 2026-04-07
updated: 2026-04-21
---

# SemiAnalysis Signals

SemiAnalysis is the external supply-chain signal layer in this reduced pipeline.

## Active Signal Scope

- `NVDA`, `CRWV`, `TSM`: near-term GPU and N3 tightness.
- `GOOGL`, `AMZN`: hyperscaler capex pull-through into accelerator demand.

## Why It Stays

- It provides directional operating context for Leopold and Baker positions.
- It connects demand (GOOGL/AMZN/CRWV) to supply constraint nodes (NVDA/TSM).

## Semi-stocks Data

- Structured signal set: `canonical/20-data/sources/semianalysis/signals.yaml`
- Thesis control plane: `canonical/30-thesis/thesis.yaml`

See also: [[concepts/bottleneck-cascade]], [[concepts/n3-wafer-crunch]], [[concepts/euv-tool-bottleneck]]
