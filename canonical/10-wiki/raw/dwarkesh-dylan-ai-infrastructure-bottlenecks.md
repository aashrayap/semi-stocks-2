# Dwarkesh x Dylan Patel — AI Infrastructure Bottlenecks

Date captured: 2026-04-08
Source type: User-provided podcast transcript
Speakers: Dwarkesh Patel, Dylan Patel

## Context

Long-form discussion on hyperscaler CapEx, AI-lab compute procurement, memory and N3 shortages, ASML/EUV ceilings, power buildout, China catch-up, and space data centers.

## Captured Claims

- Big Tech hyperscaler CapEx is running at roughly `$600B` in 2026, with broader supply-chain spend near `$1T`.
- The US is adding roughly `20 GW` of critical IT capacity in 2026, but a meaningful share of 2026 CapEx prepays 2027-2029 turbines, land, power agreements, and data-center construction.
- Anthropic and OpenAI were described as being around `2-2.5 GW` currently and potentially reaching roughly `5-6 GW` by year-end, with OpenAI ahead because it signed more aggressive long-dated compute deals.
- Late compute procurement is still possible, but at worse economics: shorter Hopper contracts were described as clearing as high as `$2.40/hr` for `2-3 year` terms.
- Roughly `30%` of Big Tech CapEx was framed as memory spend; consumer phones and PCs are the demand-destruction release valve.
- Commodity DRAM is not a clean HBM substitute because bandwidth per chip edge is the real constraint, not just raw bits per wafer.
- Nvidia signaled demand to the semiconductor supply chain earlier than Google or Amazon and locked more leading-edge logic and memory capacity.
- The near-term chip bottleneck is fab and cleanroom capacity; the later bottleneck is tool throughput, especially ASML EUV.
- One gigawatt of Rubin-class compute was estimated to need roughly `55,000` 3nm wafers, `6,000` 5nm wafers, `170,000` DRAM wafers, roughly `2 million` EUV passes, and about `3.5` EUV tools.
- Installed EUV base could reach roughly `700` tools by 2030; if fully AI-allocated that implies on the order of `200 GW` of annual AI-chip output.
- Power was argued to be hard but substitution-rich: combined-cycle turbines, aeroderivatives, reciprocating engines, ship engines, fuel cells, batteries, and grid peak-shaving can all expand supply.
- Space data centers were argued to be unattractive this decade because chips, deployment delay, networking, and failure handling dominate the energy advantage.
- China likely indigenizes DUV by 2030 and may have working EUV, but not yet mass-manufactured EUV at ASML-like scale.

## Tickers and Entities

ASML, TSMC, Nvidia, Micron, Amazon, Google, Microsoft, Anthropic, OpenAI, CoreWeave, Oracle, Apple, Huawei

## Notes

- This source reinforces the existing memory and N3 thesis nodes.
- The main genuinely new wiki node is the tooling-layer bottleneck: `[[concepts/euv-tool-bottleneck]]`.
