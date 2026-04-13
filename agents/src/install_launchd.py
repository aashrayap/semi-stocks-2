#!/usr/bin/env python3
"""Install or update the local launchd job for the daily agent runner."""

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_paths import repo_root


LABEL = "com.ash.semi-stocks-agents.daily"
DEFAULT_HOUR = 6
DEFAULT_MINUTE = 5

REPO_ROOT = repo_root().resolve()
AGENTS_DIR = REPO_ROOT / "agents"
LOGS_DIR = AGENTS_DIR / "logs"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_PATH = LAUNCH_AGENTS_DIR / f"{LABEL}.plist"
RUNNER_PATH = REPO_ROOT / "agents" / "src" / "daily_runner.py"


def find_uv() -> Path:
    uv_path = shutil.which("uv")
    if not uv_path:
        print("ERROR: Could not find `uv` on PATH.", file=sys.stderr)
        sys.exit(1)
    return Path(uv_path).resolve()


def build_plist(uv_path: Path, hour: int, minute: int) -> dict:
    stdout_path = LOGS_DIR / "launchd-daily.stdout.log"
    stderr_path = LOGS_DIR / "launchd-daily.stderr.log"
    return {
        "Label": LABEL,
        "ProgramArguments": [
            str(uv_path),
            "run",
            "python",
            str(RUNNER_PATH),
        ],
        "WorkingDirectory": str(REPO_ROOT),
        "StartCalendarInterval": {
            "Hour": hour,
            "Minute": minute,
        },
        "StandardOutPath": str(stdout_path),
        "StandardErrorPath": str(stderr_path),
        "ProcessType": "Background",
    }


def install_plist(hour: int, minute: int) -> Path:
    uv_path = find_uv()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    plist = build_plist(uv_path, hour, minute)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f, sort_keys=False)
    return PLIST_PATH


def run_launchctl(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["launchctl", *args],
        capture_output=True,
        text=True,
    )
    if check and proc.returncode != 0:
        print(proc.stderr.strip() or proc.stdout.strip(), file=sys.stderr)
        sys.exit(proc.returncode)
    return proc


def load_plist() -> None:
    domain = f"gui/{os.getuid()}"
    run_launchctl("bootout", domain, str(PLIST_PATH), check=False)
    run_launchctl("bootstrap", domain, str(PLIST_PATH))


def run_now() -> None:
    domain = f"gui/{os.getuid()}/{LABEL}"
    run_launchctl("kickstart", "-k", domain)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install the semi-stocks daily launchd job")
    parser.add_argument("--hour", type=int, default=DEFAULT_HOUR, help="Local hour for the daily run")
    parser.add_argument("--minute", type=int, default=DEFAULT_MINUTE, help="Local minute for the daily run")
    parser.add_argument("--load", action="store_true", help="Load the job into launchd after writing it")
    parser.add_argument("--run-now", action="store_true", help="Kick off the job immediately after loading it")
    args = parser.parse_args()

    if not (0 <= args.hour <= 23):
        parser.error("--hour must be between 0 and 23")
    if not (0 <= args.minute <= 59):
        parser.error("--minute must be between 0 and 59")
    if args.run_now and not args.load:
        parser.error("--run-now requires --load")

    path = install_plist(args.hour, args.minute)
    print(f"Wrote launchd plist to {path}")
    print(f"Schedule: daily at {args.hour:02d}:{args.minute:02d} local time")

    if args.load:
        load_plist()
        print(f"Loaded {LABEL}")

    if args.run_now:
        run_now()
        print(f"Started {LABEL}")


if __name__ == "__main__":
    main()
