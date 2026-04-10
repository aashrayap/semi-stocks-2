#!/usr/bin/env python3
"""AutoAgent backtest runner.

Runs the pre-earnings predictor against historical earnings with known outcomes
and scores the results. Used by the meta-agent to optimize prediction templates.

Usage:
    python agents/autoagent/backtest.py --task CRWV-Q4-2025
    python agents/autoagent/backtest.py --task NVDA-Q4-FY2026 --verbose
    python agents/autoagent/backtest.py --all
    python agents/autoagent/backtest.py --all --verbose
    python agents/autoagent/backtest.py --all --label "increased SA weight"
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent                # agents/autoagent/
AGENTS_DIR = SCRIPT_DIR.parent                              # agents/
REPO_ROOT = AGENTS_DIR.parent                               # semi-stocks/
TASKS_DIR = SCRIPT_DIR / "tasks"
EXPERIMENTS_DIR = SCRIPT_DIR / "experiments"
PREDICTOR_SCRIPT = AGENTS_DIR / "src" / "pre_earnings_predictor.py"


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
# Task discovery
# ---------------------------------------------------------------------------

def discover_tasks() -> list[str]:
    """Find all task directories under tasks/."""
    if not TASKS_DIR.is_dir():
        return []
    tasks = []
    for d in sorted(TASKS_DIR.iterdir()):
        if d.is_dir() and (d / "task.yaml").exists() and (d / "known_outcomes.yaml").exists():
            tasks.append(d.name)
    return tasks


def load_task(task_id: str) -> tuple[dict, dict]:
    """Load task.yaml and known_outcomes.yaml for a task."""
    task_dir = TASKS_DIR / task_id
    task_meta = load_yaml(task_dir / "task.yaml")
    known_outcomes = load_yaml(task_dir / "known_outcomes.yaml")
    if not task_meta:
        raise FileNotFoundError(f"task.yaml not found in {task_dir}")
    if not known_outcomes:
        raise FileNotFoundError(f"known_outcomes.yaml not found in {task_dir}")
    return task_meta, known_outcomes


# ---------------------------------------------------------------------------
# Predictor invocation
# ---------------------------------------------------------------------------

def run_predictor(ticker: str, quarter: str, pre_date: str,
                  read_root: Path) -> tuple[dict | None, str]:
    """Run the pre-earnings predictor and capture its YAML output.

    Uses --dry-run so the predictor prints to stdout without writing files.
    Uses --date to simulate the pre-earnings knowledge state.
    """
    cmd = [
        sys.executable, str(PREDICTOR_SCRIPT),
        "--ticker", ticker,
        "--quarter", quarter,
        "--date", pre_date,
        "--dry-run",
    ]

    with tempfile.TemporaryDirectory(prefix=f"autoagent-{ticker.lower()}-") as temp_dir:
        env = os.environ.copy()
        env["SEMI_STOCKS_READ_ROOT"] = str(read_root)
        env["SEMI_STOCKS_STATE_ROOT"] = str(Path(temp_dir) / "agents")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(REPO_ROOT),
                env=env,
            )
        except subprocess.TimeoutExpired:
            print(f"  ERROR: Predictor timed out for {ticker} {quarter}", file=sys.stderr)
            return None, "timeout"

    if result.returncode != 0:
        print(f"  ERROR: Predictor failed for {ticker} {quarter}", file=sys.stderr)
        print(f"  stderr: {result.stderr.strip()}", file=sys.stderr)
        return None, "error"

    # The predictor prints some status lines then a YAML document after "---"
    stdout = result.stdout
    yaml_start = stdout.find("\n---\n")
    if yaml_start == -1:
        # Try finding just "---" at start of a line
        yaml_start = stdout.find("---\n")
        if yaml_start == -1:
            print(f"  ERROR: No YAML output found in predictor stdout", file=sys.stderr)
            if stdout.strip():
                print(f"  stdout: {stdout[:500]}", file=sys.stderr)
            return None, "error"

    yaml_text = stdout[yaml_start:]
    # Strip the leading "---" line
    if yaml_text.startswith("---\n"):
        yaml_text = yaml_text[4:]
    elif yaml_text.startswith("\n---\n"):
        yaml_text = yaml_text[5:]

    try:
        doc = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        print(f"  ERROR: Failed to parse predictor YAML output: {e}", file=sys.stderr)
        return None, "error"

    return doc, "ok"


def get_task_snapshot_root(task_id: str) -> Path | None:
    """Return the frozen input snapshot for a task, if present."""
    snapshot_root = TASKS_DIR / task_id / "snapshot"
    if snapshot_root.is_dir():
        return snapshot_root
    return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize text for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def match_prediction_to_outcome(prediction: dict, outcomes_for_category: list[dict]) -> dict | None:
    """Match a prediction to the best-fitting known outcome.

    Uses fuzzy matching on claim text vs outcome claim_pattern.
    Returns the matched outcome dict or None.
    """
    claim = normalize_text(prediction.get("claim", ""))

    best_match = None
    best_score = 0.0

    for outcome in outcomes_for_category:
        pattern = normalize_text(outcome.get("claim_pattern", ""))
        if not pattern:
            continue

        # Check if the pattern words appear in the claim
        pattern_words = pattern.split()
        if not pattern_words:
            continue

        matches = sum(1 for w in pattern_words if w in claim)
        score = matches / len(pattern_words)

        if score > best_score:
            best_score = score
            best_match = outcome

    # Require at least 40% word overlap to count as a match
    if best_score >= 0.4 and best_match is not None:
        return best_match

    return None


def score_predictions(predictions_doc: dict, known_outcomes: dict,
                      verbose: bool = False) -> dict:
    """Score predictions against known outcomes.

    Returns a result dict with:
    - total: number of predictions scored
    - confirmed: count
    - partial: count
    - missed: count
    - unmatched: predictions that didn't match any outcome
    - score: 0.0-1.0
    - by_category: breakdown per category
    - details: list of per-prediction results (if verbose)
    """
    outcomes_map = known_outcomes.get("outcomes", {})
    predictions = predictions_doc.get("predictions", [])

    total = 0
    confirmed = 0
    partial = 0
    missed = 0
    unmatched = 0
    details: list[dict] = []
    by_category: dict[str, dict] = {}

    for pred in predictions:
        category = pred.get("category", "unknown")
        claim = pred.get("claim", "")
        confidence = pred.get("confidence", "unknown")

        # Initialize category tracker
        if category not in by_category:
            by_category[category] = {
                "total": 0, "confirmed": 0, "partial": 0,
                "missed": 0, "unmatched": 0,
            }

        # Find matching outcomes for this category
        category_outcomes = outcomes_map.get(category, [])

        if not category_outcomes:
            # No known outcomes for this category — count as unmatched
            unmatched += 1
            by_category[category]["unmatched"] += 1
            if verbose:
                details.append({
                    "claim": claim,
                    "category": category,
                    "confidence": confidence,
                    "result": "unmatched",
                    "reason": f"No known outcomes for category '{category}'",
                })
            continue

        # Try to match this prediction to an outcome
        matched_outcome = match_prediction_to_outcome(pred, category_outcomes)

        if matched_outcome is None:
            # Could not match — use the first outcome for the category as fallback
            # This handles generic predictions like "management provides update"
            # which should match any outcome in that category
            matched_outcome = category_outcomes[0]

        status = matched_outcome.get("status", "missed")
        evidence = matched_outcome.get("evidence", "").strip()

        total += 1
        by_category[category]["total"] += 1

        if status == "confirmed":
            confirmed += 1
            by_category[category]["confirmed"] += 1
        elif status == "partial":
            partial += 1
            by_category[category]["partial"] += 1
        else:
            missed += 1
            by_category[category]["missed"] += 1

        if verbose:
            details.append({
                "claim": claim,
                "category": category,
                "confidence": confidence,
                "result": status,
                "matched_pattern": matched_outcome.get("claim_pattern", ""),
                "evidence": evidence[:200] if evidence else "",
            })

    # Calculate score: (confirmed + 0.5 * partial) / total
    score = (confirmed + 0.5 * partial) / total if total > 0 else 0.0
    score = round(score, 4)

    result = {
        "total": total,
        "confirmed": confirmed,
        "partial": partial,
        "missed": missed,
        "unmatched": unmatched,
        "score": score,
        "by_category": by_category,
    }

    if verbose:
        result["details"] = details

    return result


# ---------------------------------------------------------------------------
# Experiment logging
# ---------------------------------------------------------------------------

def log_experiment(task_results: dict[str, dict], label: str | None = None) -> Path:
    """Log experiment results to experiments/ directory."""
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"experiment-{timestamp}.yaml"
    log_path = EXPERIMENTS_DIR / filename

    # Compute aggregate score
    total_score = 0.0
    total_tasks = 0
    for task_id, result in task_results.items():
        if result.get("score") is not None:
            total_score += result["score"]
            total_tasks += 1

    aggregate_score = round(total_score / total_tasks, 4) if total_tasks > 0 else 0.0

    log_data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "label": label or "unlabeled",
        "aggregate_score": aggregate_score,
        "task_count": total_tasks,
        "tasks": {},
    }

    for task_id, result in task_results.items():
        # Strip verbose details from log to keep it compact
        task_log = {k: v for k, v in result.items() if k != "details"}
        log_data["tasks"][task_id] = task_log

    dump_yaml(log_data, log_path)
    return log_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_task(task_id: str, verbose: bool = False) -> dict:
    """Run a single backtest task and return the scoring result."""
    print(f"\n{'='*60}")
    print(f"  Task: {task_id}")
    print(f"{'='*60}")

    # Load task metadata and known outcomes
    try:
        task_meta, known_outcomes = load_task(task_id)
    except FileNotFoundError as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {"error": str(e), "score": None}

    ticker = task_meta["ticker"]
    quarter = task_meta["quarter"]
    pre_date = task_meta.get("pre_earnings_date", "")
    bottleneck = task_meta.get("bottleneck", "unknown")
    earnings_date = task_meta.get("earnings_date", "unknown")
    snapshot_root = get_task_snapshot_root(task_id)
    input_mode = "snapshot" if snapshot_root else "live"
    read_root = snapshot_root if snapshot_root else REPO_ROOT

    print(f"  Ticker: {ticker}")
    print(f"  Quarter: {quarter}")
    print(f"  Earnings date: {earnings_date}")
    print(f"  Bottleneck: {bottleneck}")
    print(f"  Simulated date: {pre_date}")
    print(f"  Input mode: {input_mode}")
    if snapshot_root:
        print(f"  Snapshot root: {snapshot_root.relative_to(REPO_ROOT)}")
    else:
        print(f"  WARNING: No task snapshot found. Live undated inputs may still leak hindsight.")

    # The predictor expects quarter in the format used by the CLI (e.g., Q4_2025
    # or Q4_FY2026). Normalize: replace spaces with underscores.
    quarter_cli = quarter.replace(" ", "_")

    # Run the predictor
    print(f"\n  Running predictor (--ticker {ticker} --quarter {quarter_cli} --date {pre_date})...")
    predictions_doc, predictor_status = run_predictor(ticker, quarter_cli, pre_date, read_root)

    if predictions_doc is None:
        print(f"  FAILED: Predictor returned no output", file=sys.stderr)
        return {
            "error": "predictor_failed",
            "predictor_status": predictor_status,
            "input_mode": input_mode,
            "score": None,
        }

    pred_count = len(predictions_doc.get("predictions", []))
    print(f"  Predictor generated {pred_count} prediction(s)")

    if verbose:
        for p in predictions_doc.get("predictions", []):
            conf = p.get("confidence", "?")
            cat = p.get("category", "?")
            print(f"    [{conf:>6}] [{cat}] {p['claim'][:75]}")

    # Score predictions against known outcomes
    print(f"\n  Scoring against known outcomes...")
    result = score_predictions(predictions_doc, known_outcomes, verbose=verbose)
    result["input_mode"] = input_mode

    # Print results
    print(f"\n  Results:")
    print(f"    Total scored:  {result['total']}")
    print(f"    Confirmed:     {result['confirmed']}")
    print(f"    Partial:       {result['partial']}")
    print(f"    Missed:        {result['missed']}")
    print(f"    Unmatched:     {result['unmatched']}")
    print(f"    SCORE:         {result['score']:.4f}")

    # Category breakdown
    print(f"\n  By category:")
    for cat, stats in sorted(result.get("by_category", {}).items()):
        cat_score = ((stats["confirmed"] + 0.5 * stats["partial"]) / stats["total"]
                     if stats["total"] > 0 else 0.0)
        print(f"    {cat:>12}: {stats['total']} predictions, "
              f"{stats['confirmed']}C/{stats['partial']}P/{stats['missed']}M "
              f"(score: {cat_score:.2f})")

    # Verbose: per-prediction details
    if verbose and result.get("details"):
        print(f"\n  Prediction details:")
        for d in result["details"]:
            status_icon = {
                "confirmed": "+",
                "partial": "~",
                "missed": "-",
                "unmatched": "?",
            }.get(d["result"], "?")
            print(f"    [{status_icon}] [{d['category']}] {d['claim'][:70]}")
            if d.get("matched_pattern"):
                print(f"        matched: '{d['matched_pattern']}'")
            if d.get("evidence"):
                print(f"        evidence: {d['evidence'][:120]}")
            if d.get("reason"):
                print(f"        reason: {d['reason']}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AutoAgent backtest runner. Tests the pre-earnings predictor "
                    "against historical earnings with known outcomes.")
    parser.add_argument("--task", type=str,
                        help="Task ID to run (e.g., CRWV-Q4-2025)")
    parser.add_argument("--all", action="store_true",
                        help="Run all available tasks")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed per-prediction scoring")
    parser.add_argument("--label", type=str, default=None,
                        help="Label for this experiment (logged with results)")
    parser.add_argument("--list", action="store_true",
                        help="List available tasks and exit")
    args = parser.parse_args()

    if args.list:
        tasks = discover_tasks()
        if not tasks:
            print("No tasks found in agents/autoagent/tasks/")
        else:
            print(f"Available tasks ({len(tasks)}):")
            for t in tasks:
                meta = load_yaml(TASKS_DIR / t / "task.yaml")
                if meta:
                    print(f"  {t}: {meta.get('ticker', '?')} {meta.get('quarter', '?')} "
                          f"({meta.get('bottleneck', '?')}, "
                          f"{'snapshot' if get_task_snapshot_root(t) else 'live'})")
                else:
                    print(f"  {t}")
        return

    if not args.task and not args.all:
        parser.error("Provide --task TASK_ID or --all")

    # Determine which tasks to run
    if args.all:
        task_ids = discover_tasks()
        if not task_ids:
            print("No tasks found in agents/autoagent/tasks/", file=sys.stderr)
            sys.exit(1)
        print(f"Running {len(task_ids)} task(s): {', '.join(task_ids)}")
    else:
        task_ids = [args.task]

    # Run tasks
    task_results: dict[str, dict] = {}
    for task_id in task_ids:
        result = run_task(task_id, verbose=args.verbose)
        task_results[task_id] = result

    # Aggregate results
    scored_tasks = {k: v for k, v in task_results.items() if v.get("score") is not None}
    failed_tasks = {k: v for k, v in task_results.items() if v.get("score") is None}

    print(f"\n{'='*60}")
    print(f"  AGGREGATE RESULTS")
    print(f"{'='*60}")

    if scored_tasks:
        scores = [v["score"] for v in scored_tasks.values()]
        aggregate = sum(scores) / len(scores)
        print(f"\n  Tasks scored: {len(scored_tasks)}")
        for task_id, result in sorted(scored_tasks.items()):
            print(f"    {task_id}: {result['score']:.4f} "
                  f"({result['confirmed']}C/{result['partial']}P/{result['missed']}M)")
        print(f"\n  AGGREGATE SCORE: {aggregate:.4f}")
    else:
        print(f"\n  No tasks completed successfully.")

    if failed_tasks:
        print(f"\n  Failed tasks: {len(failed_tasks)}")
        for task_id, result in sorted(failed_tasks.items()):
            print(f"    {task_id}: {result.get('error', 'unknown error')}")

    # Log experiment
    log_path = log_experiment(task_results, label=args.label)
    print(f"\n  Experiment logged: {log_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
