---
title: Bottleneck Cascade
tags: [thesis, bottleneck, supply-chain, rotation]
sources: [../../30-thesis/thesis.yaml, raw/dwarkesh-dylan-ai-infrastructure-bottlenecks.md, raw/jstwng-nvidia-margin-illusion.md]
created: 2026-04-07
updated: 2026-04-13
---

# Bottleneck Cascade

The core thesis: AI compute demand is chronically underestimated. Every supplier builds "X minus 1" of what's needed. Bottlenecks shift in sequence — the trade is identifying the next binding constraint before consensus.

## Confirmed Sequence

| Stage | Period | Status | Key Tickers |
|-------|--------|--------|-------------|
| CoWoS packaging | 2023 | Played out | ASX, AMAT |
| Power / DC buildout | 2024 | Played out | VST, CEG, TLN, VRT |
| [[concepts/memory-supercycle]] | 2025-2026 | Active | MU, SNDK |
| [[concepts/n3-wafer-crunch]] | 2025-2027 | Active | TSM, NVDA, AVGO, INTC |
| [[concepts/pluggable-optics]] | 2025-2027 | Active | COHR, LITE, CIEN |
| [[concepts/co-packaged-optics]] | 2028-2030 | Next | COHR, LITE, CIEN, ALAB, SMTC |
| [[concepts/euv-tool-bottleneck]] | 2028-2030 | Next | ASML |

The hierarchy is getting clearer: power and data-center buildout remain difficult, but they are substitution-rich. Semiconductor constraints are substitution-poor, which is why the bottleneck keeps rotating upstream from deployment into memory, wafers, fabs, and eventually tools.

## Meta-Principle

Buy the next bottleneck before it becomes consensus, sell the current one as it becomes consensus.

## Source Divergence

Leopold and Baker agree on the cascade's existence but disagree on which stage is currently binding:
- **Leopold:** Power is still THE bottleneck (exited NVDA, loaded power/miners)
- **Baker:** Semiconductor supply chain is binding (massive NVDA long, optical, memory)
- **Overlap:** Only COHR, LITE, INTC shared — optical interconnect is the consensus zone

Originally these were expected to be sequential. SemiAnalysis data shows memory, N3, and optics are all binding simultaneously. The newer read-through is that power scarcity still matters tactically, but the terminal bottleneck is more likely to sit in the semiconductor tool chain than in electricity generation.

## Value Capture vs. Supply Constraint

The cascade tracks which bottleneck is binding. A complementary lens (see [[concepts/nvda-margin-residual]]) tracks who captures the surplus at each node. Wang's substitutability ranking inverts the market's valuation multiples:

1. **CoWoS packaging** — zero alternatives at scale, 113% demand CAGR. Trade (ASX/AMAT) played out, but the constraint now manifests as TSMC pricing power.
2. **HBM memory** — 3-player oligopoly, sold out through 2027, long-term contracts replacing spot.
3. **N3 logic** — TSMC 92% sub-5nm share, but expandable on 18-24 month timelines.
4. **GPU/accelerator design** — most substitutable. Custom silicon provides credible BATNA.

The most supply-constrained layers trade at the lowest multiples (TSM ~25x, memory 5-12x) while the most substitutable (NVDA 37x) trades at the highest. The implication: physical infrastructure layers are structurally underweight in market pricing.

## Direct Earnings Proof

- **GPU cloud demand:** CoreWeave Q4 2025 reached $5.13B full-year revenue, backlog expanded to $66.8B, and management said it was still unable to catch up with demand signals.
- **Memory:** Micron Q2 FY2026 printed $23.86B revenue, 74.9% non-GAAP gross margin, and guided Q3 to ~$33.5B revenue / ~81% gross margin.
- **N3 logic:** TSMC Q4 2025 printed $33.73B revenue with 3nm at 28% of wafer revenue, while Intel said demand was supply constrained and would have produced more revenue with more available supply.
- **Pluggable optics:** Coherent's datacenter and communications segment was 72% of revenue ($1.208B), and Lumentum's Q2 FY2026 revenue grew 65.5% YoY with OCS backlog above $400M.
- **CPO:** Coherent and Lumentum now have real CPO demos and orders, but the timing still points to 2027+ and not the current bottleneck.

See also: [[concepts/nvda-margin-residual]], [[sources/baker-q4-2025]], [[sources/cohr-q2-fy2026]], [[sources/crwv-q4-2025]], [[sources/dwarkesh-dylan-ai-infrastructure-bottlenecks]], [[sources/jstwng-nvidia-margin-illusion]], [[sources/leopold-q4-2025]], [[sources/lite-q2-fy2026]], [[sources/mu-q2-fy2026]], [[sources/semianalysis-signals]], [[sources/tsm-q4-2025]], [[concepts/euv-tool-bottleneck]], [[concepts/token-economics]]
