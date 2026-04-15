---
title: NVDA Margin as Residual
tags: [nvda, margin, bilateral-monopoly, value-chain, pricing-power, thesis]
sources: [raw/jstwng-nvidia-margin-illusion.md]
created: 2026-04-13
updated: 2026-04-13
---

# NVDA Margin as Residual

NVIDIA's gross margin is not a moat — it is a residual. The surplus left over after paying two supply-constrained monopolists (TSMC for fabrication + packaging, the HBM oligopoly for memory) and before selling to four hyperscalers who are building their own alternatives. The margin compresses from both directions simultaneously.

## The Framework

NVIDIA captures ~75% of the GPU selling price while contributing ~14% of the physical BoM. The gap is its vulnerability:

```
GPU selling price ($30-40K)
  minus TSMC fab + CoWoS (~$877-922, 3-4% of ASP)
  minus HBM ($2,900, 45% of BoM)
  minus packaging yield + substrate + interposer
  = NVIDIA's residual margin
```

Both the numerator (ASP) and denominator (costs) are controlled by concentrated counterparties with independent pricing power:

- **Suppliers** (TSMC, SK Hynix, Samsung, Micron) are monopolists/oligopolists charging below their theoretical maximums, anchored to pre-AI pricing norms
- **Customers** (MSFT, GOOGL, AMZN, META) form an oligopsony paying above long-run willingness, sustained by a CapEx race no one can exit first

## The Vise Mechanism

NVIDIA cannot pass supplier cost increases through to customers because the customer base has growing alternatives. This creates a structural vise:

**From below (suppliers tightening):**
- TSMC: 5-10% annual sub-5nm price hikes, CoWoS packaging monopoly (zero alternatives at scale, 113% demand CAGR)
- HBM vendors: ~20% price increases on HBM3E contracts for 2026, long-term contracts replacing spot
- Each supplier layer reprices independently; the increases compound against NVIDIA's margin

**From above (customer alternatives growing):**
- Google TPU v7: 4,614 FP8 TFLOPS, matching B200 (4,500) on compute density
- Amazon Trainium2: ~$1/hr vs $3/hr for H100, Trainium3 at 4x
- AMD MI355X: cost-per-token below GB300 NVL72 at high concurrency (SemiAnalysis InferenceX)
- Microsoft Maia 200 deploying in Azure
- Broadcom: $53B custom ASIC backlog from hyperscalers

Custom ASICs do not need to win market share to compress NVIDIA's margin. They only need to exist as a credible BATNA (Nash/Rubinstein bargaining theory). The threat disciplines pricing even if ASIC share plateaus at 20-25%.

## Evidence of Compression

NVIDIA GAAP gross margin: 75.0% (FY2025) → 71.1% (FY2026). Management guided "mid-70s" going forward. Street consensus models 74% → 71% over 5 years, which likely understates the bilateral pressure magnitude.

The compression compounds:
- TSMC + HBM vendors raise input costs → NVIDIA can absorb (margin compression) or pass through (demand destruction / ASIC acceleration)
- Hyperscaler BATNA improves each year → NVIDIA's pass-through ability declines
- The prisoner's dilemma CapEx race temporarily sustains NVIDIA's ASP, but when spending rationalizes, the highest-margin supplier is first to be renegotiated

## Inverted Multiples

The market prices the stack inversely to structural positioning:

| Layer | Substitutability | Constraint Duration | Multiple |
|-------|-----------------|--------------------|-----------|
| CoWoS packaging | None at scale | 2+ years to expand | Buried in TSM (~25x fwd) |
| HBM memory | 3-player oligopoly | Sold out through 2027 | 5-12x fwd P/E |
| N3 logic fabrication | TSM 92% share | 18-24 month expandable | TSM ~25x fwd P/E |
| GPU/accelerator design | Growing alternatives | Credible BATNA exists | NVDA 37x trailing |

The most competitively exposed layer commands the highest multiple. The most structurally entrenched layers trade at the deepest discounts.

## Relationship to Bottleneck Cascade

This concept complements the [[concepts/bottleneck-cascade]] by adding a *value capture* dimension to the *supply constraint* dimension. The cascade tracks which bottleneck is binding; this concept tracks who captures the surplus generated at each node.

Key insight: the CoWoS bottleneck was marked "played_out" as a trade (ASX/AMAT), but CoWoS remains the mechanism through which TSMC's pricing power compounds. The beneficiary rotated from equipment suppliers to TSMC itself.

## Counter-Arguments

- **CUDA moat is real:** Software ecosystem switching costs remain high for training workloads. NVIDIA may retain pricing power longer than the bilateral monopoly model predicts.
- **Revenue growth may offset margin compression:** If NVIDIA grows data center revenue from $115B to $200B+, EPS can grow even as margins compress.
- **Hyperscaler CapEx race may persist:** As long as no individual player can afford to pull back, NVIDIA's ASP stays elevated regardless of theoretical alternatives.
- **ASIC track record is mixed:** Amazon swapped ASIC partners (Marvell → Alchip), Maia is late, MTIA is nascent. Rapid model architecture shifts (dense → MoE, test-time compute) undermine ASIC design cycles.

## See also

[[concepts/bottleneck-cascade]], [[concepts/memory-supercycle]], [[concepts/n3-wafer-crunch]], [[concepts/euv-tool-bottleneck]], [[sources/jstwng-nvidia-margin-illusion]], [[sources/nvda-q4-fy2026]], [[outputs/baker-cyclicality-thesis]]
