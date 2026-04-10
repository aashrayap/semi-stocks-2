---
title: "NVIDIA — Q4 FY2026 Earnings"
tags: [earnings, nvda, n3-logic, memory, pluggable-optics, ai-infrastructure]
sources: [raw/nvda-q4-fy2026-transcript.md]
created: 2026-04-07
updated: 2026-04-07
---

# NVIDIA — Q4 FY2026 Earnings

Record quarter: $68.1B revenue (+73% YoY), beat guidance by ~$3B. Guided Q1 to $78B vs Street's $72.6B. Stock rose on the beat. Data Center = 91% of revenue.

## Key Metrics

| Metric | Q4 FY2026 | FY2026 | QoQ | YoY |
|---|---|---|---|---|
| Revenue | $68.1B | $215.9B | +20% | +73% |
| Data Center | $62.3B | $193.7B | +22% | +75% |
| Networking | $11B | $31B | — | +3.5x |
| Gaming | $3.7B | $16.0B | -13% | +47% |
| Gross Margin (non-GAAP) | 75.2% | 71.3% | +180bps | — |
| Net Income | $43.0B | $120.1B | +35% | +94% |
| FCF | $35B | $97B | — | — |
| EPS (GAAP) | $1.76 | $4.90 | — | — |

Grace Blackwell systems = ~two-thirds of Data Center revenue. Top 5 cloud providers = ~50% of DC revenue. Supply commitments nearly doubled: $50.3B → $95.2B.

## Guidance

- **Q1 FY2027 revenue:** $78B ±2% (Street expected $72.6B — massive beat)
- **Q1 gross margin:** 75% non-GAAP ±50bps
- **FY2027 tax rate:** 17-19%
- **China Data Center excluded** from Q1 outlook
- **Mid-70s gross margins** described as sustainable through FY2027

## Forward Claims

Verifiable statements management made. These get tracked in `canonical/20-data/companies/NVDA/q4_fy2026.yaml`.

1. **Q1 revenue $78B ±2%** — massive guide-up vs consensus $72.6B (verify: Q1 FY2027 earnings, ~late May 2026)
2. **Mid-70s gross margins sustainable through FY2027** — Kress: generational perf leads sustain margins (verify: FY2027 quarterly results)
3. **Rubin production shipments H2 2026** — Vera Rubin samples already shipped, production targeted H2 (verify: Q3 FY2027, ~late Nov 2026)
4. **Rubin: 1/4 GPUs for MoE training, 10x lower inference cost vs Blackwell** — Jensen (verify: Rubin benchmarks, H2 2026)
5. **$500B revenue visibility through end of CY2026** — Kress (verify: ongoing through FY2027)
6. **$3-4T annual AI infrastructure investment by 2029-2030** — Jensen, secular demand thesis (verify: long-term)
7. **China competitors could "disrupt the structure of the global AI industry"** — Kress warning (verify: ongoing)

## Notable Quotes

**On compute = revenue (Jensen):**
> "In this new world of AI, compute is revenues. Without compute, there's no way to generate tokens. Without tokens, there's no way to grow revenues."

**On demand (Jensen):**
> "Computing demand is growing exponentially. Enterprise adoption of agents is skyrocketing. Our customers are racing to invest in AI compute — the factories powering the AI industrial revolution."

**On margin sustainability (Kress):**
> "The single most important lever of our gross margins is actually delivering generational leads" through superior performance per watt and per dollar.

**On Spectrum-X (Jensen):**
> Spectrum-X Ethernet: "a home run."

**On rack-scale (Jensen):**
> "We don't ship nodes of computers, we ship racks of computers."

**On Meta ROI (Jensen):**
> Meta's GEM model drove "3.5x increase in ad clicks" on Facebook and "more than 1%" conversation gains on Instagram.

## Product & Partnership Announcements

- **OpenAI:** GPT-5.3 Codex training/inference on Grace Blackwell / NVLink 72
- **Anthropic:** $10B NVIDIA strategic investment
- **Meta:** deploying "millions" of Blackwell and Rubin GPUs
- **Groq:** non-exclusive licensing for low-latency inference technology
- **GB300 NVL72:** 50x perf/watt, 35x lower cost/token vs Hopper
- **CUDA optimization:** 5x better performance on GB200 NVL72 in 4 months
- **Vera CPU:** fundamentally different architecture (LPDDR5, single-port), "off the charts" single-thread perf vs Grace
- **Vera Rubin samples already shipped** — production H2 2026

## Thesis Signal

NVIDIA is thesis-central — it sits at the intersection of multiple active bottlenecks:

**[[concepts/n3-wafer-crunch]] (primary):** Rubin moves to N3, competing with all other AI accelerators (TPU v7/v8, Trainium3, MI350X) for TSMC capacity. $95.2B in supply commitments = enormous wafer demand. Vera Rubin production H2 2026 adds more N3 pressure.

**[[concepts/memory-supercycle]]:** Every GPU needs HBM. $21.4B inventory. NVIDIA's GPU shipments are a primary demand driver for the [[concepts/memory-supercycle|memory supercycle]]. CRWV's $30-35B capex flows through NVIDIA into memory.

**[[concepts/pluggable-optics]]:** $11B networking quarter (+3.5x YoY). Every NVL72 rack needs OSFP pluggable transceivers. Spectrum-X "home run" validates COHR/LITE revenue stream. "We ship racks of computers" = optics in every rack.

**GPU cloud demand validation:** Supply commitments nearly doubled ($50.3B → $95.2B). $500B revenue visibility. Validates [[sources/crwv-q4-2025|CRWV]]'s "insatiable demand" thesis.

## Baker vs Leopold on NVDA

| | Baker | Leopold |
|---|---|---|
| Position | $1B+ (massive long) | **Exited** |
| Type | Common stock | — |
| Conviction | Very high | Negative / rotated out |

**Key divergence.** Baker bets the semiconductor supply chain is the bottleneck — NVDA is the picks-and-shovels play. Leopold exited NVDA and concentrated into GPU cloud (CRWV #1) and power/optics — he bets the downstream deployment layer is where the bottleneck value accrues. Both can be right (different time horizons), but this is the clearest thesis disagreement.

## Semi-stocks Data

- Structured financials and verifiable claims: `canonical/20-data/companies/NVDA/q4_fy2026.yaml`
- Leopold positioning: [[sources/leopold-q4-2025]] (exited NVDA)
- Baker positioning: [[sources/baker-q4-2025]] (NVDA = top position, $1B+)
- Thesis cascade: `canonical/30-thesis/thesis.yaml` (NVDA tagged as n3_logic: active)

## See Also

- [[concepts/n3-wafer-crunch]] — TSMC N3 at 100%+ utilization
- [[concepts/memory-supercycle]] — HBM demand driven by GPU shipments
- [[concepts/pluggable-optics]] — $11B networking = optics revenue
- [[concepts/token-economics]] — Jensen's "compute = revenue" framework
- [[concepts/bottleneck-cascade]] — where NVDA sits in the cascade
- [[sources/crwv-q4-2025]] — CRWV as NVDA's largest GPU cloud customer
