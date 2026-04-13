#!/usr/bin/env python3
"""Run the unattended daily agent sidecar flow."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: uv sync", file=sys.stderr)
    sys.exit(1)

from runtime_paths import repo_root


SCRIPT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = SCRIPT_DIR.parent
REPO_ROOT = repo_root().resolve()
LOGS_DIR = AGENTS_DIR / "logs"
AGENT_CONFIG_PATH = AGENTS_DIR / "config.yaml"


def load_yaml(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_agent_config() -> dict:
    cfg = load_yaml(AGENT_CONFIG_PATH)
    return cfg if cfg else {}


def get_windows() -> tuple[int, int]:
    cfg = load_agent_config()
    alerts = cfg.get("alerts", {})
    predictions = cfg.get("predictions", {})
    earnings_days = int(alerts.get("earnings_days_out", 14))
    prediction_days = int(predictions.get("auto_generate_days_before", 7))
    return earnings_days, prediction_days


def setup_logging(run_day: date) -> logging.Logger:
    logger = logging.getLogger("daily_runner")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"daily-runner-{run_day.strftime('%Y-%m')}.log"
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger


def script_cmd(script_name: str, *args: str) -> list[str]:
    return [sys.executable, str(SCRIPT_DIR / script_name), *args]


def run_step(logger: logging.Logger, label: str, command: list[str]) -> int:
    pretty = " ".join(command[1:])
    logger.info("Starting %s: %s", label, pretty)
    proc = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    if proc.stdout.strip():
        for line in proc.stdout.strip().splitlines():
            logger.info("[%s stdout] %s", label, line)
    if proc.stderr.strip():
        for line in proc.stderr.strip().splitlines():
            logger.warning("[%s stderr] %s", label, line)

    logger.info("Finished %s with exit code %s", label, proc.returncode)
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the daily unattended agent sidecar flow")
    parser.add_argument("--date", help="Override date for scripts that support YYYY-MM-DD")
    args = parser.parse_args()

    run_day = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    logger = setup_logging(run_day)
    earnings_days, prediction_days = get_windows()

    logger.info("=" * 60)
    logger.info("daily_runner started")
    logger.info("Repo root: %s", REPO_ROOT)
    logger.info("Earnings window: %sd | Prediction window: %sd", earnings_days, prediction_days)

    date_args = ["--date", args.date] if args.date else []
    failures: list[str] = []

    steps = [
        (
            "earnings_calendar",
            script_cmd("earnings_calendar.py", "--days", str(earnings_days), *date_args),
        ),
        (
            "pre_earnings_predictor",
            script_cmd(
                "pre_earnings_predictor.py",
                "--all-upcoming",
                "--days",
                str(prediction_days),
                *date_args,
            ),
        ),
        (
            "transcript_fetcher",
            script_cmd("transcript_fetcher.py", "--all-due"),
        ),
    ]

    for label, command in steps:
        if run_step(logger, label, command) != 0:
            failures.append(label)

    report_rc = run_step(logger, "agent_report", script_cmd("report.py", *date_args))
    if report_rc != 0:
        failures.append("agent_report")

    if failures:
        logger.error("daily_runner finished with failures: %s", ", ".join(failures))
        logger.info("=" * 60)
        sys.exit(1)

    logger.info("daily_runner finished successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
