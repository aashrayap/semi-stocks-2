#!/usr/bin/env python3
"""Canonical site-data entrypoint for the stage-ordered engine lane."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parent
if str(STAGE_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE_DIR))

from engine.site_data import build_site_data  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build canonical/site-data artifacts.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated artifacts after writing them.",
    )
    args = parser.parse_args()

    stats = build_site_data(validate=args.validate)
    print(
        "Site-data built: "
        f"{stats['pages']} pages, "
        f"{stats['companies']} companies, "
        f"{stats['signals']} signals, "
        f"{stats['claims']} claims, "
        f"{stats['edges']} edges"
    )


if __name__ == "__main__":
    main()
