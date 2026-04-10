# Wiki Log — semi-stocks

Append-only record of wiki activity. Each entry starts with `## [date] action | description`.

---

## [2026-04-08] ingest | Dwarkesh x Dylan Patel — AI Infrastructure Bottlenecks

Added a non-earnings source centered on compute bottlenecks and supply-chain hierarchy:
- **Raw:** `raw/dwarkesh-dylan-ai-infrastructure-bottlenecks.md` (captured claims register from the user-provided transcript)
- **Source:** `sources/dwarkesh-dylan-ai-infrastructure-bottlenecks.md` (synthesized takeaways, tracking claims, ticker read-through)
- **Concepts:** created `concepts/euv-tool-bottleneck.md`; updated `concepts/bottleneck-cascade.md`, `concepts/memory-supercycle.md`, `concepts/n3-wafer-crunch.md`, and `sources/semianalysis-signals.md`

Key addition: the wiki now has a dedicated EUV tooling node, which sharpens the distinction between substitution-rich power bottlenecks and substitution-poor semiconductor bottlenecks.

## [2026-04-07] update | Report restructure + cycle risk integration

Restructured report from 9 sections → 5 (3 main + summary + collapsed drift):
1. Summary (+ cycle risk sentence, Baker hedge ratio)
2. Cascade + Cycle Risk (merged cascade, explainers→one-liners, cycle phase/action/flags)
3. Positions + Signals (merged agreement map + divergences inline)
4. Earnings Dashboard (merged forward claims + thesis signals + SemiAnalysis per ticker)
5. Drift (collapsed `<details>`, count badge only)

Added to `../../30-thesis/thesis.yaml`: `cycle_phase`, `cycle_signal`, `cycle_risk_flags` per cascade stage. `baker_hedge_ratio` as tracked metric (0.70, trend: increasing).

Added to `synthesis.py`: `cycle_assessment()`, `baker_hedge_ratio()`, `earnings_dashboard()`, `BOTTLENECK_ONE_LINERS`.

Updated `README.md` actionable framework: two dimensions (which bottleneck + when in cycle).

---

## [2026-04-07] query → output | Baker's cyclicality thesis — "every shortage followed by a glut"

Filed to `outputs/baker-cyclicality-thesis.md`. Research dispatched across 7 parallel subagents covering: Memory (MU), Foundry (TSM), Equipment (ASML/LRCX/AMAT), Broadcom (AVGO), Auto/Analog (TXN/ON/NXPI/ADI), GPU (NVDA/AMD), and Baker's public commentary. Synthesized evidence matrix, P/E compression data, lead time signals, and counter-arguments. Key finding: Baker's framework confirmed across all subsectors except AVGO (partial exception due to software mix and supply discipline). TXN is the single strongest proof point — P/E 16x at peak earnings, 38x at trough, stock higher during glut.

---

## [2026-04-07] query → output | NVDA pre-earnings swing trade thesis

Filed `outputs/nvda-swing-trade-thesis.md`. Query synthesized wiki sources (NVDA Q4 FY2026 earnings, Baker/Leopold positioning, SemiAnalysis signals, bottleneck cascade, token economics) with live market research (price history, technicals, options data, analyst consensus).

Key findings: $170 support confirmed (3 tests), $185-190 resistance confirmed (death cross). Forward P/E 21x on 73% growth = fundamental floor. Iron condor ($170/$190 short strikes, May 16 expiry) + directional swing trade ($171 entry, $183-185 target, $165 stop). Hard exit by May 20 before earnings.

Also added `next_earnings` field to all tickers in `../../30-thesis/thesis.yaml` and an Earnings column to the report source agreement map (color-coded: red <=7d, orange <=21d).

---

## [2026-04-07] update | Concept pages updated with earnings confirmation

Updated 3 concept pages to reflect CRWV Q4 2025 and NVDA Q4 FY2026 earnings signals:
- `concepts/memory-supercycle.md` — added NVIDIA $21.4B HBM inventory signal, earnings confirmation section
- `concepts/n3-wafer-crunch.md` — added NVIDIA supply commitments doubling, Vera Rubin production signal, earnings confirmation section
- `concepts/pluggable-optics.md` — added NVIDIA $11B networking revenue signal, earnings confirmation section

Drift warnings reduced from 11 → 1 (remaining: no dedicated gpu_cloud concept page).

---

## [2026-04-07] ingest | NVIDIA Q4 FY2026 Earnings

Second earnings pipeline run. Full three-layer funnel:
- **Raw:** `raw/nvda-q4-fy2026-transcript.md` (compiled from NVIDIA Newsroom, Motley Fool, Yahoo Finance, Fortune, Ticker Report)
- **Source:** `sources/nvda-q4-fy2026.md` (synthesized: metrics, quotes, guidance, 7 forward claims, bottleneck mapping, Baker/Leopold divergence)
- **Structure:** `../../20-data/companies/NVDA/q4_fy2026.yaml` (7 forward_claims with verify_at dates, thesis signals across 4 bottlenecks, product highlights, partnership announcements)

Key thesis signals: $95.2B supply commitments (doubled QoQ), $11B networking quarter validates optics, Rubin production H2 2026 adds N3 pressure. Baker/Leopold NVDA divergence is the clearest thesis disagreement — Baker $1B+ long, Leopold exited.

---

## [2026-04-07] ingest | CoreWeave Q4 2025 Earnings — first earnings pipeline run

First use of the earnings pipeline. Three-layer funnel:
- **Raw:** `raw/crwv-q4-2025-transcript.md` (full earnings call transcript, FactSet/CallStreet corrected)
- **Source:** `sources/crwv-q4-2025.md` (synthesized: metrics, quotes, guidance claims, bottleneck mapping, Leopold/Baker divergence)
- **Structure:** `../../20-data/companies/CRWV/q4_2025.yaml` (9 forward_claims with verify_at dates, thesis signals across 5 bottlenecks)

Moved from `../../10-wiki` to `canonical/10-wiki` (correct location per architecture).

## [2026-04-07] init | Semi-stocks wiki scaffolded

Created wiki structure inside semi-stocks-2 canonical lane. Thesis-linked to `../../30-thesis/thesis.yaml`.

Seed content migrated from existing README.md narrative, `../../30-thesis/thesis.yaml` signals, and synthesis.py BOTTLENECK_EXPLAINERS.

**Concept pages created:** bottleneck-cascade, memory-supercycle, n3-wafer-crunch, pluggable-optics, co-packaged-optics, token-economics
**Source pages created:** leopold-q4-2025, baker-q4-2025, semianalysis-signals

## [2026-04-09] rebuild-index | 20 pages indexed, 115 local links, 2 orphan pages, 0 dead links

## [2026-04-09] rebuild-index | 20 pages indexed, 115 local links, 0 orphan pages, 0 dead links

## [2026-04-10] rebuild-index | 20 pages indexed, 115 local links, 0 orphan pages, 0 dead links

## [2026-04-10] path-cleanup | canonical wiki paths normalized

Normalized the checked-in wiki metadata and generated state to the canonical lane layout:
- updated `schema.md` to describe `canonical/10-wiki/` and canonical thesis/data links
- updated `index.md` and this log to reference `../../30-thesis/thesis.yaml` and `../../20-data/`
- normalized source and concept page references to canonical path strings
- rebuilt `_index.json`, `_backlinks.json`, and `_lint.json` against the canonical wiki root

## [2026-04-10] schema update | canonical wiki root contract refreshed

Updated `schema.md` to describe the canonical `canonical/10-wiki/` root, canonical thesis/data cross-lane links, and `uv run` rebuild command. Rebuilt `_index.json`, `_backlinks.json`, and `_lint.json` against the updated wiki root.

## [2026-04-10] root-path correction | wiki root references fixed

Corrected the wiki-root references in `schema.md` and `index.md` so the wiki root now points to `../30-thesis/thesis.yaml` and `../20-data/sources/` from `canonical/10-wiki/`.
