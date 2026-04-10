---
title: "SemiAnalysis Signals"
tags: [semianalysis, supply-chain, dylan-patel, signals]
sources: [../../20-data/sources/semianalysis/signals.yaml]
created: 2026-04-07
updated: 2026-04-08
---

# SemiAnalysis Signals

Dylan Patel's SemiAnalysis. Proprietary supply chain data — tracks every data center, fab, tool order, wafer allocation globally. The only source with bottom-up models for TSMC wafer allocation, ASML tool shipments, HBM capacity by vendor, and hyperscaler CapEx breakdown.

## Track Record

- Memory crunch call: Sep 2024, 12 months early
- CoWoS bottleneck: 2023 (correct)
- Power crisis: 2024 (correct)

## Current Key Signals

### Memory
- 30% of Big Tech's $600B+ CapEx goes to memory
- Smartphone volumes dropping from 1.4B to 500-600M units (DRAM demand destruction)

### N3 Wafers
- N3 utilization at 100%+ in H2 2026
- AI = 60% of N3 output (2026), projected 86% by 2027

### EUV / Fab Capacity
- ASML EUV ceiling: ~100 tools/yr by 2030
- 3.5 EUV tools per gigawatt of fab capacity
- Cleanroom/fab space is the current physical bottleneck (2yr build time)
- Installed base could approach ~700 EUV tools by 2030, implying ~200 GW of AI-chip output if fully AI-allocated

## Constraint Hierarchy

- Power is difficult but substitution-rich: turbines, engines, fuel cells, batteries, and grid workarounds all matter.
- Semiconductors are substitution-poor: memory, N3, fabs, and EUV are the harder long-run ceilings.
- Translation for the thesis: power can still make tactical winners, but the more durable choke points sit upstream.

## Role in Thesis

SemiAnalysis is the independent data layer. Leopold and Baker are positioned investors with biases. SemiAnalysis provides the supply chain ground truth that either confirms or contradicts their positioning.

Jensen Huang cited SemiAnalysis at GTC26 as doing analysis "right" — normalizing everything by tokens/second/watt.

## Key Tickers Flagged

COHR, LITE, CIEN (optics), MU, SNDK (memory), TSM, NVDA (N3), ASML (EUV)

See also: [[concepts/bottleneck-cascade]], [[concepts/euv-tool-bottleneck]], [[concepts/memory-supercycle]], [[concepts/n3-wafer-crunch]], [[sources/dwarkesh-dylan-ai-infrastructure-bottlenecks]]
