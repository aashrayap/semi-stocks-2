#!/usr/bin/env python3
"""Canonical report entrypoint for the stage-ordered engine lane."""

import sys
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parent
if str(STAGE_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE_DIR))

from engine.report import build_report  # noqa: E402


if __name__ == "__main__":
    path = build_report()
    print(f"Report written to {path}")
