---
title: "NVDA Pre-Earnings Swing Trade & Iron Condor Thesis"
tags: [nvda, swing-trade, iron-condor, options, trade-plan]
sources: [sources/nvda-q4-fy2026, sources/baker-q4-2025, sources/leopold-q4-2025, sources/semianalysis-signals, concepts/bottleneck-cascade, concepts/n3-wafer-crunch]
created: 2026-04-07
updated: 2026-04-07
---

# NVDA Pre-Earnings Swing Trade & Iron Condor Thesis

Query: Can we exploit the $170-$190 range in NVDA before earnings, via a swing trade and/or an iron condor?

**Verdict: Yes — the range is technically confirmed and fundamentally supported, but the window closes at earnings (~May 28).**

## Thesis Summary

NVDA is trading at ~$177.64, pinned between incredible fundamentals (21x forward P/E, 73% YoY revenue growth, $97B FCF) and macro headwinds (25% semiconductor tariffs, FTC antitrust probe, China competition). This tug-of-war creates a defined trading range.

- **$170 is confirmed support** — tested 3x in Q1 2026, bounced each time
- **$185-190 is confirmed resistance** — 50-day MA ($182.8) and 200-day MA ($184) form a ceiling; death cross in place
- **Baker holds $1B+** including $902M in new call options — a whale buyer defending dips
- **Leopold exited entirely** — rotated into CRWV, LITE, power names

## Current NVDA Snapshot (April 7, 2026)

| Metric | Value |
|--------|-------|
| Price | $177.64 |
| 52-week range | $94.46 – $212.19 |
| Forward P/E | ~21x (5yr avg ~70x) |
| PEG ratio | 0.56 |
| Trailing P/E | ~35x |
| FY2026 revenue | $215.9B (+65% YoY) |
| Q1 FY2027 guide | $78B (vs consensus $72.6B) |
| Gross margin | 75.2% (non-GAAP) |
| FCF | $97B (FY2026) |
| Supply commitments | $95.2B (doubled QoQ) |
| Next earnings | ~May 28, 2026 |
| IV rank | 12.10 (low) |

## Earnings History Pattern

NVDA has beaten on both revenue and EPS for 8 consecutive quarters. But 4 of 8 post-earnings reactions were negative despite beating — short-term traders sell the event, institutions accumulate on dips.

| Quarter | Revenue | Beat | Post-Earnings Move |
|---------|---------|------|--------------------|
| Q1 FY25 | $26.0B | +$1.4B | +9.3% |
| Q2 FY25 | $30.0B | +$1.3B | -6.4% |
| Q3 FY25 | $35.1B | +$1.9B | +0.5% |
| Q4 FY25 | $39.3B | +$1.0B | -8.5% |
| Q1 FY26 | $44.1B | +$0.9B | +6% (AH) |
| Q2 FY26 | $46.7B | +$0.7B | -3% |
| Q3 FY26 | $57.0B | +$1.8B | +2.9% |
| Q4 FY26 | $68.1B | +$1.9B | -5.5% |

Revenue growth re-accelerated on the Blackwell ramp: QoQ from +6% (Q2 FY26) to +20-22% (Q3/Q4 FY26).

## Fund Positioning (Q4 2025 13F)

| | Baker | Leopold |
|---|---|---|
| Position | $1B+ (common + $902M new calls) | **Exited** |
| Thesis | Chip supply = bottleneck, NVDA = pricing power | Downstream deployment is where value accrues |
| Conviction | Very high | Negative (rotated into CRWV, LITE, power) |

This is the clearest thesis disagreement. Both can be right on different time horizons, but Baker's massive position provides a floor — he's accumulating on any weakness.

## Swing Trade: Hard Rules

### Entry

| Condition | Action |
|-----------|--------|
| NVDA touches $170-172 | **BUY** (primary entry, limit at $171) |
| NVDA drops 3%+ intraday from above $175, driven by broad market/macro | **BUY** (secondary entry) |
| NVDA drops 3%+ on NVDA-specific bad news (antitrust action, export ban) | **WAIT** |
| VIX > 30 | Wait for 2 consecutive green days on SPY before entering |
| NVDA weak but SMH holds | Caution — weakness is NVDA-specific, not sector |

### Exit

| Condition | Action |
|-----------|--------|
| NVDA reaches $183-185 | **SELL half** (approaching 50/200 DMA resistance) |
| NVDA reaches $185+ | **SELL remaining** (or trail stop at $180) |
| NVDA closes below $165 | **STOP OUT** ($170 support broken, next level $155-160) |
| May 20 (any price) | **EXIT ALL** (hard time stop, 1 week before earnings) |

### Position Sizing

- Risk no more than 5% of trading capital
- Entry at $172, stop at $165 = $7 downside/share
- Target at $183 = $11 upside/share (1.6:1 reward/risk)

## Iron Condor: Range-Bound Options Play

The thesis "NVDA stays between $170 and $190" maps to an **iron condor** — selling volatility within a defined range.

### Structure

| Leg | Strike | Action |
|-----|--------|--------|
| Long put (protection) | $160 | Buy |
| Short put (floor) | $170 | Sell |
| Short call (ceiling) | $190 | Sell |
| Long call (protection) | $200 | Buy |
| **Expiration** | **May 16, 2026** | **Before earnings** |

### Risk/Reward

| Metric | Value |
|--------|-------|
| Estimated net credit | ~$2.40 – $3.00 ($240-300/contract) |
| Max loss | ~$7.00 – $7.60 ($700-760/contract) |
| Lower break-even | ~$167.30 |
| Upper break-even | ~$192.70 |
| Probability of profit | ~55-65% |
| Capital at risk | ~$730/contract |

### Management Rules

- Close at 50% of max profit (~$135) to improve win rate
- Close if loss reaches 2x credit (~$540) — don't ride to max loss
- Need ~3 wins to offset 1 max loss at full width

### Why May 16 Expiration

- 39 DTE = sweet spot for theta decay
- **Expires before earnings (~May 28)** — avoids the 8-12% binary move
- Monthly expiration = best liquidity, tightest bid-ask spreads
- IV rank is low (12.10) so premium isn't huge, but the range is tight enough to work

## Alternative Options Strategies

| Strategy | When to Use | Credit | Max Loss |
|----------|-------------|--------|----------|
| **Put credit spread** ($170/$160) | Bullish — "won't drop below $170" but might rally above $190 | ~$1.50 | ~$8.50 |
| **Cash-secured put** at $170 | Want to own NVDA at ~$167 effective cost | ~$2.30 | Stock goes to $0 |
| **Covered call** at $190 (if you own shares) | Generate income, cap upside at $190 | ~$2.00 | Full downside exposure |
| **Short strangle** ($170/$190) | Same range thesis, more credit, unlimited risk | ~$4.30 | Unlimited (upside) |

## What Breaks the Range

**Upward (above $190):**
- Q1 FY2027 earnings beat + guidance raise (late May)
- Rubin production ahead of schedule
- Major new AI customer announcement
- Tariff reduction / trade deal

**Downward (below $170):**
- New tariff escalation (50%+ or full China ban)
- FTC antitrust enforcement action (not just investigation)
- Hyperscaler capex cut announcement
- Broader market crash (SPY -10%+)

## Thesis-Level Grounding

From [[concepts/bottleneck-cascade]]: NVDA sits at the intersection of three active bottlenecks — [[concepts/n3-wafer-crunch]], [[concepts/memory-supercycle]], and [[concepts/pluggable-optics]]. The [[concepts/token-economics]] framework ("compute = revenue") means GPU demand compounds indefinitely. At 21x forward P/E with $500B revenue visibility and $95.2B in supply commitments, the fundamental floor is real. The stock is compressed by temporary headwinds (tariffs, sentiment), not structural deterioration.

[[sources/semianalysis-signals]]: N3 utilization 100%+ in H2 2026, AI = 60% of output (86% by 2027). NVDA has the strongest demand curve against constrained supply.

The swing and the iron condor are complementary. The swing captures directional upside ($170 → $185 = ~8%). The iron condor captures time decay within the range. Both close before earnings.

## See Also

- [[concepts/bottleneck-cascade]]
- [[concepts/n3-wafer-crunch]]
- [[concepts/token-economics]]
- [[sources/nvda-q4-fy2026]]
- [[sources/baker-q4-2025]]
- [[sources/leopold-q4-2025]]
- [[sources/semianalysis-signals]]
