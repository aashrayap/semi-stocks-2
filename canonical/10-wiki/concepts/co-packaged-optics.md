---
title: Co-Packaged Optics (CPO)
tags: [optics, cpo, networking, bottleneck, next]
sources: [../../30-thesis/thesis.yaml]
created: 2026-04-07
updated: 2026-04-21
---

# Co-Packaged Optics (CPO)

As AI clusters scale to tens of thousands of GPUs, copper cables between racks can't keep up — too slow, too much heat. CPO replaces copper with laser light by integrating optical engines directly onto the chip package.

## Why It's Next (Not Now)

- CPO market projected at $20B by 2036, 37% CAGR
- Lumentum disclosed an incremental multi-hundred-million-dollar CPO order for 1H 2027 delivery
- Coherent's March 2026 NVIDIA partnership added multibillion-dollar purchase commitments, future capacity rights, and a $2B investment
- Coherent's OFC 2026 demos included 6.4T silicon-photonics CPO, VCSEL socketed CPO, and a 400G-per-lane InP-on-silicon path
- Rubin Ultra NVL576: CPO between racks — explicitly low volume / test only
- Feynman NVL1152: CPO between racks, copper within rack (base case)
- 448G SerDes challenges (shoreline, reach, power) favor CPO over copper at next speed step

## Timeline (from GTC26)

| Generation | Scale-Up | Scale-Out |
|------------|----------|-----------|
| NVL72 (Blackwell) | Copper | Pluggable |
| NVL144 (Rubin Ultra) | Copper OR Copper+CPO | Pluggable |
| NVL1152 (Feynman) | All CPO | CPO |

## Key Nuance

Volume CPO is a Feynman story (2028+), NOT Rubin Ultra. Inside every rack through NVL1152 remains copper. This keeps ALAB relevant as the retained copper signal-integrity expression after the sub-$10B roster prune.

Early orders and demos matter because they make the roadmap more credible. They do not move this stage into the current bottleneck bucket yet.

## Source Positioning

| Ticker | Role | Leopold | Baker |
|--------|------|---------|-------|
| COHR | Optical engines | $89M | ~$394M incl. calls |
| LITE | Optical engines | $479M | $141M |
| ALAB | Retimers/signal integrity (copper persistence) | — | $268M |

CPO winners will be whoever integrates optical engines on-package — COHR and LITE are best positioned but volume revenue is years away.

See also: [[concepts/pluggable-optics]], [[concepts/bottleneck-cascade]], [[sources/cohr-q2-fy2026]], [[sources/lite-q2-fy2026]]
