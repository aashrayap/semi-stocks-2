---
title: Memory Supercycle
tags: [memory, hbm, dram, bottleneck]
sources: [../../30-thesis/thesis.yaml, ../../20-data/sources/semianalysis/signals.yaml]
created: 2026-04-07
updated: 2026-04-08
---

# Memory Supercycle

Every AI chip needs memory (DRAM/HBM) to hold the data it's processing. HBM (High Bandwidth Memory) is special memory stacked in layers and bonded directly to the GPU — it's 85% less dense than regular DRAM and much harder to make.

## Why It's a Bottleneck

AI is consuming so much memory that there isn't enough left for phones, PCs, and other devices. The result:
- DRAM contract prices surged +90-95% in a single quarter (Q1 2026, TrendForce)
- DDR4 spot price ($2.10/Gbit) now exceeds HBM3e ($1.70/Gbit) — unprecedented inversion
- Micron Q2 FY2026 printed $23.86B revenue with 74.9% non-GAAP gross margin
- Micron guided Q3 FY2026 to ~$33.5B revenue and ~81% gross margin
- Micron said data-center DRAM and NAND bit TAM should exceed 50% of industry TAM in 2026
- Micron says DRAM and NAND remain supply constrained beyond calendar 2026
- Micron has already begun HBM4 volume shipments for NVIDIA Vera Rubin
- Micron FY2026 capex is now above $25B
- 30% of Big Tech's $650B CapEx goes to memory
- NVIDIA carries $21.4B inventory including significant HBM stockpile (Q4 FY2026)

## Why Commodity DRAM Does Not Fix It

- HBM4 delivers bandwidth on the order of terabytes per second per stack; DDR-class memory delivers only a small fraction of that over similar chip-edge real estate.
- The constraint is not just bits per wafer. It is bandwidth per chip edge, memory locality, and how much compute gets stranded while waiting on data.
- AI can tolerate some slower inference tiers, but the highest-value workloads still prefer speed, so the market keeps bidding for HBM instead of switching cleanly to commodity DRAM.

## Source Positioning

- **Baker:** Long MU ($411M) + put hedge. Believes memory is binding.
- **Leopold:** Exited MU puts in Q4 2025. Not actively positioned in memory.
- **SemiAnalysis:** Flagged memory crunch Sep 2024, 12 months early.

## Key Tickers

| Ticker | Role | Held By |
|--------|------|---------|
| MU | DRAM/HBM manufacturer | Baker |
| SNDK | Storage/NAND | Leopold (+816% QoQ) |

## Earnings Confirmation

- **MU Q2 FY2026:** Direct shortage proof. $23.86B revenue, 74.9% non-GAAP gross margin, Q3 guide of ~$33.5B revenue / ~81% gross margin, data-center bit TAM above 50% of industry TAM in 2026, HBM4 volume shipments for Vera Rubin, and FY2026 capex above $25B.
- **CRWV Q4 2025:** Every GPU CRWV deploys needs HBM. $30-35B capex = substantial HBM demand pull-through.
- **NVDA Q4 FY2026:** $21.4B inventory (HBM stockpile). Every GPU shipped needs HBM — NVIDIA GPU volumes are the primary demand driver.

See also: [[concepts/bottleneck-cascade]], [[concepts/euv-tool-bottleneck]], [[concepts/n3-wafer-crunch]], [[sources/crwv-q4-2025]], [[sources/dwarkesh-dylan-ai-infrastructure-bottlenecks]], [[sources/mu-q2-fy2026]], [[sources/nvda-q4-fy2026]]
