# AutoAgent: Prediction Optimization Program

You are a meta-agent whose goal is to improve the accuracy of `agents/src/pre_earnings_predictor.py` by backtesting against historical earnings with known outcomes.

## The System

The semi-stocks agent fleet runs a prediction-evaluation loop:

1. **Pre-earnings (7 days before):** `pre_earnings_predictor.py` reads canonical/30-thesis/thesis.yaml, company data, fund positioning (Leopold/Baker 13F), SemiAnalysis supply chain signals, and wiki concept pages. It generates template-based, deterministic predictions. Output: `agents/state/predictions/<TICKER>-<quarter>.yaml`.

2. **Post-earnings:** `post_earnings_scorer.py` grades each prediction against actual results. Statuses: `confirmed`, `missed`, `partial`, `revised`.

3. **This meta-agent:** Modifies the predictor, runs backtests against known earnings, measures accuracy, and iterates.

## What the Predictor Does

The predictor generates predictions across six categories:

| Category | What it predicts |
|---|---|
| **capacity** | Whether a bottleneck's utilization remains constrained, expanding, or resolving |
| **pricing** | ASP/margin strength or normalization based on bottleneck status |
| **demand** | Customer demand trajectory, new customer signals, backlog changes |
| **margins** | Gross/EBITDA/operating margin levels relative to prior quarter |
| **guidance** | Forward revenue/capacity guidance, pending forward claim verification |
| **positioning** | Whether earnings reinforce or challenge Leopold/Baker fund positioning |

For each prediction, it produces:
- **claim**: A testable statement
- **category**: One of the six above
- **basis**: List of source/detail pairs (where the evidence came from)
- **confidence**: high / medium / low
- **verify_at**: When this claim can be checked
- **status**: Always starts as "pending"

Basis sources include:
- `canonical/30-thesis/thesis.yaml` (cascade signals)
- `canonical/20-data/sources/semianalysis/signals.yaml` (supply chain data)
- `canonical/20-data/companies/<TICKER>/` (prior earnings, forward claims, thesis signals)
- `canonical/20-data/sources/leopold/` and `canonical/20-data/sources/baker/` (fund positioning)
- `canonical/10-wiki/concepts/` (compiled bottleneck analysis)

## Scoring

The backtest score formula is:

```
score = (confirmed + 0.5 * partial) / total_predictions
```

A score of 1.0 means every prediction was confirmed. A score of 0.5 means half were confirmed. Partial credit counts as 0.5.

## Levers You Can Pull

### 1. Prediction Template Text
The predictor uses template strings (e.g., `"{bn_display} utilization remains at or near capacity"`). You can:
- Make claims more specific and testable
- Make claims broader to increase confirmation rate (but reduce signal value)
- Split vague claims into multiple precise sub-claims
- **Trade-off:** Specificity improves signal but risks more misses

### 2. Confidence Calibration
The predictor assigns confidence based on heuristics (e.g., `len(basis) >= 3` -> high). You can:
- Adjust thresholds for high/medium/low
- Weight certain source types more heavily in confidence assignment
- Add rules like "if both funds positioned, confidence += 1 tier"
- **Trade-off:** Better calibration improves decision-making even if accuracy stays flat

### 3. Source Weighting
Different basis sources have different predictive value. You can:
- Increase weight for sources that correlate with confirmed predictions
- Decrease weight for sources that correlate with misses
- Cap the number of basis entries from low-accuracy sources
- **Goal:** If SemiAnalysis signals predict capacity correctly 90% of the time but wiki concepts only 50%, weight accordingly

### 4. Category Selection
Not all categories are equally predictable per bottleneck type. You can:
- Skip categories that consistently miss for certain bottleneck types
- Add more predictions in high-accuracy categories
- Map which categories work for which bottleneck statuses (active/next/played_out)
- **Goal:** If guidance predictions always miss for `gpu_cloud` tickers, stop generating them

### 5. Evidence Scanning Patterns
The predictor scans canonical/30-thesis/thesis.yaml signals, company forward_claims, and SemiAnalysis data_points. You can:
- Change how many signals to pull per source (currently top 3 from cascade, top 2 per SA signal)
- Filter signals by recency or relevance keywords
- Add new scanning logic (e.g., check for backlog data, customer concentration flags)
- **Goal:** Better evidence extraction leads to more accurate claims

## What NOT to Change

- **Output YAML schema**: The structure of prediction files must stay the same (ticker, quarter, predictions list with claim/category/basis/confidence/verify_at/status, positioning_context, track_record)
- **File paths**: Predictions go to `agents/state/predictions/<TICKER>-<quarter>.yaml`
- **CLI interface**: `--ticker`, `--quarter`, `--date`, `--dry-run`, `--all-upcoming` must keep working
- **Category names**: capacity, pricing, demand, margins, guidance, positioning
- **Status values**: confirmed, missed, partial, revised, pending

## How to Run an Experiment

1. **Baseline**: Run `python agents/autoagent/backtest.py --all --verbose` to get the current score
2. **Modify**: Edit `agents/src/pre_earnings_predictor.py` (the levers above)
3. **Test**: Run `python agents/autoagent/backtest.py --all --verbose` again
4. **Compare**: Check `agents/autoagent/experiments/` for logged results
5. **Iterate**: Keep the change if score improved, revert if not

Each experiment is logged with a timestamp, the score, and a description of what changed.

## Available Backtest Tasks

| Task ID | Ticker | Quarter | Earnings Date | Bottleneck |
|---|---|---|---|---|
| CRWV-Q4-2025 | CRWV | Q4 2025 | 2026-02-26 | gpu_cloud (active) |
| NVDA-Q4-FY2026 | NVDA | Q4 FY2026 | 2026-02-26 | n3_logic (active) |

Task directories live at `agents/autoagent/tasks/<TASK_ID>/` and contain:
- `task.yaml` — metadata (ticker, quarter, earnings date, bottleneck, pre-earnings date)
- `known_outcomes.yaml` — actual results by category with status and evidence
- `snapshot/` — frozen pre-earnings input tree used to replay the predictor without head-state leakage

## Success Criteria

- Score > 0.75 across all tasks is a strong predictor
- Score > 0.85 means the template is well-calibrated for these bottleneck types
- Score < 0.50 means significant template or weighting issues
- Category-level breakdown reveals where the predictor is strongest/weakest
- Source-level breakdown reveals which data sources are most predictive
