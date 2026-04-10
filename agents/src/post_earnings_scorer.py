#!/usr/bin/env python3
"""Post-earnings prediction scorer.

Scores pre-earnings predictions against actual earnings results.
Supports interactive (human-assisted) scoring and template generation
for later manual review.

Usage:
    python agents/src/post_earnings_scorer.py --ticker TSM --quarter Q1_2026 --interactive
    python agents/src/post_earnings_scorer.py --ticker TSM --quarter Q1_2026
    python agents/src/post_earnings_scorer.py --ticker TSM --quarter Q1_2026 --dry-run
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from runtime_paths import data_root, repo_root


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent          # agents/src/
AGENTS_DIR = SCRIPT_DIR.parent                        # agents/
REPO_ROOT = repo_root()                               # semi-stocks/

COMPANIES_DIR = data_root(REPO_ROOT) / "companies"
PREDICTIONS_DIR = AGENTS_DIR / "state" / "predictions"
REPORTS_DIR = AGENTS_DIR / "reports"
DRAFTS_EARNINGS_DIR = AGENTS_DIR / "drafts" / "earnings"
LOGS_DIR = AGENTS_DIR / "logs"


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict | list | None:
    """Load a YAML file, returning None if it doesn't exist."""
    if not path.exists():
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def dump_yaml(data: dict, path: Path) -> None:
    """Write data to a YAML file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True, width=120)


# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------

def load_predictions(ticker: str, quarter: str) -> dict | None:
    """Load the predictions file for a ticker + quarter."""
    pred_path = PREDICTIONS_DIR / f"{ticker}-{quarter}.yaml"
    return load_yaml(pred_path)


def get_predictions_path(ticker: str, quarter: str) -> Path:
    """Get the path for a predictions file."""
    return PREDICTIONS_DIR / f"{ticker}-{quarter}.yaml"


def load_company_data(ticker: str) -> list[dict]:
    """Load all quarterly YAML files for a company."""
    company_dir = COMPANIES_DIR / ticker
    if not company_dir.is_dir():
        return []
    results = []
    for f in sorted(company_dir.glob("*.yaml")):
        data = load_yaml(f)
        if data:
            data["_file"] = str(f.relative_to(REPO_ROOT))
            results.append(data)
    return results


def find_earnings_draft(ticker: str, quarter: str) -> Path | None:
    """Find an earnings draft for a ticker + quarter."""
    DRAFTS_EARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    ticker_lower = ticker.lower()
    quarter_lower = quarter.lower().replace("_", "-").replace(" ", "-")
    candidates = sorted(DRAFTS_EARNINGS_DIR.glob(f"{ticker_lower}-{quarter_lower}*"))
    if candidates:
        return candidates[-1]
    # Also try without underscore
    candidates = sorted(DRAFTS_EARNINGS_DIR.glob(f"{ticker_lower}-*"))
    for c in candidates:
        if quarter_lower.replace("-", "") in c.name.lower().replace("-", ""):
            return c
    return None


def load_all_predictions_for_ticker(ticker: str) -> list[dict]:
    """Load all prediction files for a ticker (for track record)."""
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for f in sorted(PREDICTIONS_DIR.glob(f"{ticker}-*.yaml")):
        data = load_yaml(f)
        if data:
            results.append(data)
    return results


# ---------------------------------------------------------------------------
# Track record calculation
# ---------------------------------------------------------------------------

def calculate_track_record(ticker: str) -> dict:
    """Calculate prediction accuracy from all prediction files for a ticker."""
    all_preds = load_all_predictions_for_ticker(ticker)
    total = 0
    confirmed = 0
    missed = 0
    partial = 0
    revised = 0
    by_category: dict[str, dict] = {}
    by_source: dict[str, dict] = {}
    history: list[dict] = []

    for pred_file in all_preds:
        quarter = pred_file.get("quarter", "unknown")
        quarter_total = 0
        quarter_confirmed = 0

        for pred in pred_file.get("predictions", []):
            status = pred.get("status", "pending")
            if status == "pending":
                continue

            cat = pred.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = {"total": 0, "confirmed": 0, "missed": 0, "partial": 0}

            total += 1
            quarter_total += 1
            by_category[cat]["total"] += 1

            if status == "confirmed":
                confirmed += 1
                quarter_confirmed += 1
                by_category[cat]["confirmed"] += 1
            elif status == "missed":
                missed += 1
                by_category[cat]["missed"] += 1
            elif status == "partial":
                partial += 1
                by_category[cat]["partial"] += 1
            elif status == "revised":
                revised += 1

            # Track which basis sources led to correct vs incorrect predictions
            for basis_entry in pred.get("basis", []):
                source = basis_entry.get("source", "unknown")
                # Normalize source to category
                if "30-thesis/thesis.yaml" in source or source.endswith("thesis.yaml"):
                    source_key = "thesis.yaml"
                elif "semianalysis" in source:
                    source_key = "semianalysis"
                elif "leopold" in source:
                    source_key = "leopold"
                elif "baker" in source:
                    source_key = "baker"
                elif "10-wiki/concepts" in source or "wiki/concepts" in source:
                    source_key = "wiki_concepts"
                elif "20-data/companies" in source or "data/companies" in source:
                    source_key = "company_data"
                else:
                    source_key = source

                if source_key not in by_source:
                    by_source[source_key] = {"used_in": 0, "confirmed": 0, "missed": 0}
                by_source[source_key]["used_in"] += 1
                if status == "confirmed":
                    by_source[source_key]["confirmed"] += 1
                elif status == "missed":
                    by_source[source_key]["missed"] += 1

        if quarter_total > 0:
            history.append({
                "quarter": quarter,
                "total": quarter_total,
                "confirmed": quarter_confirmed,
                "accuracy": round(quarter_confirmed / quarter_total, 3),
            })

    accuracy = round(confirmed / total, 3) if total > 0 else None

    return {
        "total_predictions": total,
        "confirmed": confirmed,
        "missed": missed,
        "partial": partial,
        "revised": revised,
        "accuracy": accuracy,
        "by_category": by_category if by_category else None,
        "by_source": by_source if by_source else None,
        "history": history if history else None,
    }


# ---------------------------------------------------------------------------
# Interactive scoring
# ---------------------------------------------------------------------------

VALID_STATUSES = {"confirmed", "missed", "partial", "revised", "pending"}


def interactive_score(predictions: dict) -> dict:
    """Interactively score each prediction, prompting the user."""
    ticker = predictions.get("ticker", "???")
    quarter = predictions.get("quarter", "???")
    print(f"\n{'='*70}")
    print(f"  Scoring predictions for {ticker} — {quarter}")
    print(f"{'='*70}")
    print()
    print("For each prediction, enter a status:")
    print("  c = confirmed   m = missed   p = partial   r = revised   s = skip (keep pending)")
    print("  You can also add a note after the status, e.g.: c Revenue beat by 5%")
    print()

    preds = predictions.get("predictions", [])
    scored_count = 0

    for i, pred in enumerate(preds):
        if pred.get("status") != "pending":
            print(f"[{i+1}/{len(preds)}] Already scored: {pred.get('status')} — skipping")
            print(f"  Claim: {pred['claim']}")
            print()
            continue

        print(f"[{i+1}/{len(preds)}] {pred.get('category', '?').upper()}")
        print(f"  Claim: {pred['claim']}")
        print(f"  Confidence: {pred.get('confidence', '?')}")
        if pred.get("basis"):
            print(f"  Basis:")
            for b in pred["basis"][:2]:
                print(f"    - {b.get('source', '?')}: {b.get('detail', '?')[:80]}")
        print()

        while True:
            try:
                raw = input("  Status> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nScoring interrupted. Saving progress...")
                return predictions

            if not raw:
                print("  (skipped)")
                break

            parts = raw.split(None, 1)
            code = parts[0].lower()
            note = parts[1] if len(parts) > 1 else None

            status_map = {
                "c": "confirmed",
                "confirmed": "confirmed",
                "m": "missed",
                "missed": "missed",
                "p": "partial",
                "partial": "partial",
                "r": "revised",
                "revised": "revised",
                "s": None,  # skip
                "skip": None,
            }

            if code not in status_map:
                print(f"  Invalid. Use: c/m/p/r/s")
                continue

            new_status = status_map[code]
            if new_status is None:
                print("  (skipped)")
                break

            pred["status"] = new_status
            pred["scored_at"] = date.today().isoformat()
            if note:
                pred["actual"] = note
            scored_count += 1
            print(f"  -> {new_status}" + (f" ({note})" if note else ""))
            break

        print()

    print(f"Scored {scored_count} prediction(s).")
    return predictions


# ---------------------------------------------------------------------------
# Scorecard generation
# ---------------------------------------------------------------------------

def generate_scorecard(predictions: dict, track_record: dict, today: date) -> str:
    """Generate a Markdown scorecard from scored predictions."""
    ticker = predictions.get("ticker", "???")
    quarter = predictions.get("quarter", "???")
    bottleneck = predictions.get("bottleneck", "unknown")
    bn_status = predictions.get("bottleneck_status", "unknown")
    preds = predictions.get("predictions", [])

    lines: list[str] = []

    lines.append(f"# Prediction Scorecard: {ticker} — {quarter}")
    lines.append("")
    lines.append(f"Generated: {today.isoformat()}")
    lines.append(f"Earnings date: {predictions.get('earnings_date', 'unknown')}")
    lines.append(f"Predicted at: {predictions.get('predicted_at', 'unknown')}")
    lines.append(f"Bottleneck: {bottleneck.replace('_', ' ')} [{bn_status}]")
    lines.append("")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    scored = [p for p in preds if p.get("status") != "pending"]
    pending = [p for p in preds if p.get("status") == "pending"]
    confirmed = [p for p in preds if p.get("status") == "confirmed"]
    missed_list = [p for p in preds if p.get("status") == "missed"]
    partial_list = [p for p in preds if p.get("status") == "partial"]
    revised_list = [p for p in preds if p.get("status") == "revised"]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total predictions: {len(preds)}")
    lines.append(f"- Scored: {len(scored)}")
    lines.append(f"- Pending: {len(pending)}")
    if scored:
        accuracy = len(confirmed) / len(scored) if scored else 0
        lines.append(f"- **Confirmed: {len(confirmed)}**")
        lines.append(f"- Missed: {len(missed_list)}")
        lines.append(f"- Partial: {len(partial_list)}")
        lines.append(f"- Revised: {len(revised_list)}")
        lines.append(f"- **Accuracy: {accuracy:.0%}**")
    lines.append("")

    # -----------------------------------------------------------------------
    # Prediction details
    # -----------------------------------------------------------------------
    lines.append("## Predictions vs. Actuals")
    lines.append("")

    for i, pred in enumerate(preds):
        status = pred.get("status", "pending")
        status_icon = {
            "confirmed": "[CONFIRMED]",
            "missed": "[MISSED]",
            "partial": "[PARTIAL]",
            "revised": "[REVISED]",
            "pending": "[PENDING]",
        }.get(status, "[???]")

        lines.append(f"### {i+1}. {status_icon} {pred.get('category', '?').title()}")
        lines.append("")
        lines.append(f"**Prediction:** {pred['claim']}")
        lines.append(f"**Confidence:** {pred.get('confidence', '?')}")
        lines.append(f"**Status:** {status}")

        if pred.get("actual"):
            lines.append(f"**Actual:** {pred['actual']}")

        if pred.get("basis"):
            lines.append("**Basis:**")
            for b in pred["basis"]:
                lines.append(f"  - `{b.get('source', '?')}`: {b.get('detail', '?')}")

        lines.append("")

    # -----------------------------------------------------------------------
    # Category breakdown
    # -----------------------------------------------------------------------
    lines.append("## Accuracy by Category")
    lines.append("")
    lines.append("| Category | Total | Confirmed | Missed | Partial | Accuracy |")
    lines.append("|----------|-------|-----------|--------|---------|----------|")

    cat_stats: dict[str, dict] = {}
    for pred in preds:
        cat = pred.get("category", "unknown")
        status = pred.get("status", "pending")
        if status == "pending":
            continue
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "confirmed": 0, "missed": 0, "partial": 0}
        cat_stats[cat]["total"] += 1
        if status == "confirmed":
            cat_stats[cat]["confirmed"] += 1
        elif status == "missed":
            cat_stats[cat]["missed"] += 1
        elif status == "partial":
            cat_stats[cat]["partial"] += 1

    for cat, stats in sorted(cat_stats.items()):
        acc = stats["confirmed"] / stats["total"] if stats["total"] > 0 else 0
        lines.append(f"| {cat} | {stats['total']} | {stats['confirmed']} | "
                     f"{stats['missed']} | {stats['partial']} | {acc:.0%} |")
    if not cat_stats:
        lines.append("| (no scored predictions) | — | — | — | — | — |")
    lines.append("")

    # -----------------------------------------------------------------------
    # Source accuracy
    # -----------------------------------------------------------------------
    if track_record.get("by_source"):
        lines.append("## Basis Source Accuracy")
        lines.append("")
        lines.append("Which data sources led to correct vs. incorrect predictions:")
        lines.append("")
        lines.append("| Source | Used In | Confirmed | Missed | Hit Rate |")
        lines.append("|--------|---------|-----------|--------|----------|")
        for source, stats in sorted(track_record["by_source"].items()):
            hit_rate = (stats["confirmed"] / stats["used_in"]
                        if stats["used_in"] > 0 else 0)
            lines.append(f"| {source} | {stats['used_in']} | "
                         f"{stats['confirmed']} | {stats['missed']} | {hit_rate:.0%} |")
        lines.append("")

    # -----------------------------------------------------------------------
    # Historical accuracy trend
    # -----------------------------------------------------------------------
    if track_record.get("history"):
        lines.append("## Historical Accuracy Trend")
        lines.append("")
        lines.append("| Quarter | Total | Confirmed | Accuracy |")
        lines.append("|---------|-------|-----------|----------|")
        for h in track_record["history"]:
            lines.append(f"| {h['quarter']} | {h['total']} | "
                         f"{h['confirmed']} | {h['accuracy']:.0%} |")
        lines.append("")

        overall = track_record.get("accuracy")
        if overall is not None:
            lines.append(f"**Overall accuracy: {overall:.0%}** "
                         f"({track_record['confirmed']}/{track_record['total_predictions']})")
            lines.append("")

    # -----------------------------------------------------------------------
    # Positioning context
    # -----------------------------------------------------------------------
    pos = predictions.get("positioning_context", {})
    if pos:
        lines.append("## Positioning Context")
        lines.append("")
        if pos.get("leopold"):
            lines.append(f"- **Leopold:** {pos['leopold']}")
        if pos.get("baker"):
            lines.append(f"- **Baker:** {pos['baker']}")
        if pos.get("implied_signal"):
            lines.append(f"- **Implied signal:** {pos['implied_signal']}")
        if pos.get("divergence_detail"):
            lines.append(f"- **Divergence:** {pos['divergence_detail']}")
        lines.append("")

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `agents/src/post_earnings_scorer.py`. "
                 "This is an automated agent scorecard for tracking prediction accuracy.*")

    return "\n".join(lines)


def generate_template_scorecard(predictions: dict, today: date) -> str:
    """Generate a template scorecard with status fields to fill in manually."""
    ticker = predictions.get("ticker", "???")
    quarter = predictions.get("quarter", "???")
    preds = predictions.get("predictions", [])

    lines: list[str] = []

    lines.append(f"# Prediction Scorecard (TEMPLATE): {ticker} — {quarter}")
    lines.append("")
    lines.append(f"Generated: {today.isoformat()}")
    lines.append(f"Earnings date: {predictions.get('earnings_date', 'unknown')}")
    lines.append("")
    lines.append("Instructions: For each prediction, fill in the STATUS and ACTUAL fields.")
    lines.append("Valid statuses: confirmed | missed | partial | revised")
    lines.append("Then re-run the scorer to compute final stats.")
    lines.append("")

    for i, pred in enumerate(preds):
        status = pred.get("status", "pending")
        lines.append(f"## {i+1}. [{pred.get('category', '?').upper()}] "
                     f"(confidence: {pred.get('confidence', '?')})")
        lines.append("")
        lines.append(f"**Prediction:** {pred['claim']}")
        lines.append("")
        if pred.get("basis"):
            lines.append("**Basis:**")
            for b in pred["basis"]:
                lines.append(f"  - `{b.get('source', '?')}`: {b.get('detail', '?')}")
            lines.append("")
        lines.append(f"**STATUS:** {status}  <!-- change to: confirmed | missed | partial | revised -->")
        lines.append(f"**ACTUAL:** <!-- describe what actually happened -->")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Template generated by `agents/src/post_earnings_scorer.py`.*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def write_log(today: date, ticker: str, quarter: str,
              action: str, files_written: list[str],
              error: str | None = None) -> None:
    """Append a run entry to agents/logs/."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"post-earnings-scorer-{today.strftime('%Y-%m')}.log"

    timestamp = datetime.now().isoformat(timespec="seconds")
    entry_lines = [
        f"[{timestamp}] post_earnings_scorer",
        f"  ticker: {ticker}",
        f"  quarter: {quarter}",
        f"  action: {action}",
        f"  files_written: {', '.join(files_written) if files_written else 'none'}",
    ]
    if error:
        entry_lines.append(f"  error: {error}")
    entry_lines.append("")

    with open(log_file, "a") as f:
        f.write("\n".join(entry_lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post-earnings prediction scorer. Grades predictions against "
                    "actual earnings results and generates scorecards.")
    parser.add_argument("--ticker", type=str, required=True,
                        help="Ticker symbol (e.g. TSM)")
    parser.add_argument("--quarter", type=str, required=True,
                        help="Quarter label (e.g. Q1_2026)")
    parser.add_argument("--interactive", action="store_true",
                        help="Interactively score each prediction via prompts")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print output without writing files")
    parser.add_argument("--date", type=str, default=None,
                        help="Override today's date (YYYY-MM-DD) for testing")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    quarter = args.quarter

    if args.date:
        today = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        today = date.today()

    # Load predictions
    predictions = load_predictions(ticker, quarter)
    if not predictions:
        pred_path = get_predictions_path(ticker, quarter)
        print(f"ERROR: No predictions file found at {pred_path.relative_to(REPO_ROOT)}",
              file=sys.stderr)
        print(f"Run pre_earnings_predictor.py first to generate predictions.",
              file=sys.stderr)
        write_log(today, ticker, quarter, "error", [],
                  error=f"Predictions file not found: {pred_path}")
        sys.exit(1)

    preds_list = predictions.get("predictions", [])
    pending_count = sum(1 for p in preds_list if p.get("status") == "pending")
    scored_count = sum(1 for p in preds_list if p.get("status") != "pending")

    print(f"Loaded predictions for {ticker} — {predictions.get('quarter', quarter)}")
    print(f"  Total predictions: {len(preds_list)}")
    print(f"  Pending: {pending_count}")
    print(f"  Already scored: {scored_count}")

    # Check for supporting data
    earnings_draft = find_earnings_draft(ticker, quarter)
    if earnings_draft:
        print(f"  Earnings draft found: {earnings_draft.relative_to(REPO_ROOT)}")
    company_data = load_company_data(ticker)
    if company_data:
        print(f"  Company data: {len(company_data)} quarter(s) in canonical/20-data/companies/{ticker}/")

    files_written: list[str] = []

    if args.interactive:
        # Interactive scoring
        if pending_count == 0:
            print("\nAll predictions already scored. Generating scorecard...")
        else:
            print()
            predictions = interactive_score(predictions)

            # Save updated predictions
            if not args.dry_run:
                pred_path = get_predictions_path(ticker, quarter)

                # Update track record in predictions file
                track_record = calculate_track_record(ticker)
                predictions["track_record"] = track_record

                dump_yaml(predictions, pred_path)
                rel_path = str(pred_path.relative_to(REPO_ROOT))
                files_written.append(rel_path)
                print(f"\nPredictions updated: {rel_path}")

        # Generate scorecard
        track_record = calculate_track_record(ticker)
        scorecard = generate_scorecard(predictions, track_record, today)

        if args.dry_run:
            print("\n" + scorecard)
        else:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            scorecard_path = REPORTS_DIR / f"scorecard-{ticker}-{quarter}.md"
            scorecard_path.write_text(scorecard)
            rel_path = str(scorecard_path.relative_to(REPO_ROOT))
            files_written.append(rel_path)
            print(f"Scorecard written: {rel_path}")

        write_log(today, ticker, quarter, "interactive_score", files_written)

    else:
        # Non-interactive: generate template scorecard
        if pending_count > 0:
            print(f"\n{pending_count} prediction(s) still pending.")
            print("Generating template scorecard for manual review...")
            template = generate_template_scorecard(predictions, today)

            if args.dry_run:
                print("\n" + template)
            else:
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                scorecard_path = REPORTS_DIR / f"scorecard-{ticker}-{quarter}.md"
                scorecard_path.write_text(template)
                rel_path = str(scorecard_path.relative_to(REPO_ROOT))
                files_written.append(rel_path)
                print(f"Template scorecard written: {rel_path}")
                print("\nNext steps:")
                print(f"  1. Review predictions in the template scorecard")
                print(f"  2. Run with --interactive to score interactively, OR")
                print(f"  3. Edit the predictions YAML directly and re-run to generate final scorecard")

            write_log(today, ticker, quarter, "template_scorecard", files_written)
        else:
            # All scored — generate final scorecard
            print("\nAll predictions already scored. Generating final scorecard...")
            track_record = calculate_track_record(ticker)
            scorecard = generate_scorecard(predictions, track_record, today)

            if args.dry_run:
                print("\n" + scorecard)
            else:
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                scorecard_path = REPORTS_DIR / f"scorecard-{ticker}-{quarter}.md"
                scorecard_path.write_text(scorecard)
                rel_path = str(scorecard_path.relative_to(REPO_ROOT))
                files_written.append(rel_path)
                print(f"Scorecard written: {rel_path}")

            write_log(today, ticker, quarter, "final_scorecard", files_written)

    if files_written:
        print(f"\nDone. {len(files_written)} file(s) written.")


if __name__ == "__main__":
    main()
