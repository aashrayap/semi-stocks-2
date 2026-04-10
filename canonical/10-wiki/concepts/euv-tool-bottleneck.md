---
title: EUV Tool Bottleneck
tags: [euv, asml, lithography, bottleneck, tools]
sources: [../../30-thesis/thesis.yaml, ../../20-data/sources/semianalysis/signals.yaml, raw/dwarkesh-dylan-ai-infrastructure-bottlenecks.md]
created: 2026-04-08
updated: 2026-04-08
---

# EUV Tool Bottleneck

EUV lithography is the deepest upstream choke point in AI semiconductors. Once power, land, and near-term cleanroom constraints are partially worked around, the limiting factor becomes how many advanced wafers the industry can expose through ASML tools and the tiny supplier chain behind them.

## Why It Matters

- ASML remains the only EUV supplier.
- One gigawatt of Rubin-class capacity was framed as requiring about `2 million` EUV passes and roughly `3.5` EUV tools.
- ASML output was framed as roughly `70` tools in 2026, `80` in 2027, and only a bit above `100` by 2030 even under aggressive expansion.
- A cumulative installed base near `700` EUV tools by 2030 implies only about `200 GW` of annual AI-chip output if those tools were fully AI-allocated.
- EUV also matters for memory, not just logic, so AI accelerators and DRAM compete for overlapping lithography capacity.

## Why It Expands Slowly

- The bottleneck is not just ASML final assembly. It includes Zeiss optics, Cymer source power, reticle and wafer stages, metrology, and a highly specialized supplier web.
- Fabs and cleanrooms take years to build, but tool-chain expansion also takes years because each supplier is capacity-constrained and talent-constrained.
- There is no clean substitution path. Power can route around bottlenecks through many technologies; EUV cannot.

## Bottleneck Rotation

- `2026-2027`: fab shells and cleanrooms are the first near-term physical bottleneck.
- `2028-2030`: tool throughput becomes the harder ceiling.
- Beyond that point, ASML and its supplier chain govern how fast TSMC, memory vendors, and everyone downstream can grow.

## Ticker Read-Through

| Ticker | Role | Read-through |
|---|---|---|
| ASML | EUV monopoly | Direct owner of the tooling ceiling |
| TSM | Largest advanced-logic deployer | Can only ship what its tool receipts allow |
| NVDA | Strongest AI-demand signal | Forces earlier reservations upstream |
| MU | Memory-side beneficiary | DRAM scaling also consumes advanced tooling |

## Why This Favors Semi Stocks Over Power Stocks

The key distinction is substitution. A data center can switch among many power sources and deployment patterns. A leading-edge fab cannot switch away from EUV once it hits that part of the process flow. That makes the tooling layer structurally scarcer than the power layer.

## See Also

- [[concepts/bottleneck-cascade]]
- [[concepts/memory-supercycle]]
- [[concepts/n3-wafer-crunch]]
- [[sources/dwarkesh-dylan-ai-infrastructure-bottlenecks]]
- [[sources/semianalysis-signals]]
