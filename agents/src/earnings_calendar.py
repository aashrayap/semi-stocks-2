#!/usr/bin/env python3
"""Earnings calendar agent.

Scans the canonical semi-stocks repo for upcoming earnings, pending forward
claims, and bottleneck context, then outputs a structured alert to agents/reports/.

Usage:
    python agents/src/earnings_calendar.py
    python agents/src/earnings_calendar.py --days 21   # lookahead window
    python agents/src/earnings_calendar.py --dry-run    # print to stdout, don't write files
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from runtime_paths import data_root, engine_stage, repo_root, thesis_path, wiki_root


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent          # agents/src/
AGENTS_DIR = SCRIPT_DIR.parent                        # agents/
REPO_ROOT = repo_root()                               # semi-stocks/
ENGINE_STAGE = engine_stage(REPO_ROOT)

if str(ENGINE_STAGE) not in sys.path:
    sys.path.insert(0, str(ENGINE_STAGE))

from engine.company_data import claim_matches_quarter, claim_window_label, next_quarter_label  # noqa: E402

THESIS_PATH = thesis_path(REPO_ROOT)
DATA_ROOT = data_root(REPO_ROOT)
WIKI_ROOT = wiki_root(REPO_ROOT)
COMPANIES_DIR = DATA_ROOT / "companies"
WIKI_SOURCES_DIR = WIKI_ROOT / "sources"
WIKI_CONCEPTS_DIR = WIKI_ROOT / "concepts"
MAIN_CONFIG_PATH = REPO_ROOT / "config.yaml"
AGENT_CONFIG_PATH = AGENTS_DIR / "config.yaml"
REPORTS_DIR = AGENTS_DIR / "reports"
LOGS_DIR = AGENTS_DIR / "logs"


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict | list | None:
    """Load a YAML file, returning None if it doesn't exist."""
    if not path.exists():
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------

def get_agent_config() -> dict:
    """Load agent fleet config."""
    cfg = load_yaml(AGENT_CONFIG_PATH)
    return cfg if cfg else {}


def get_deep_dive_tickers() -> list[str]:
    """Get deep-dive ticker list from agent config, falling back to main config."""
    agent_cfg = get_agent_config()
    deep_dive = agent_cfg.get("deep_dive", [])
    if deep_dive:
        return deep_dive

    # Fallback: read main config.yaml
    main_cfg = load_yaml(MAIN_CONFIG_PATH)
    if main_cfg and "companies" in main_cfg:
        return [c["ticker"] for c in main_cfg["companies"].get("deep_dive", [])]
    return []


def get_ticker_map() -> dict[str, dict]:
    """Load ticker_map from the canonical thesis file."""
    thesis = load_yaml(THESIS_PATH)
    if not thesis:
        return {}
    return thesis.get("ticker_map", {})


def get_cascade() -> list[dict]:
    """Load cascade stages from the canonical thesis file."""
    thesis = load_yaml(THESIS_PATH)
    if not thesis:
        return []
    return thesis.get("cascade", [])


def get_company_data(ticker: str) -> list[dict]:
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


def get_latest_company_data(ticker: str) -> dict | None:
    quarters = get_company_data(ticker)
    if not quarters:
        return None
    return quarters[-1]


def get_forward_claims(ticker: str) -> list[dict]:
    """Extract all forward_claims from a company's quarterly files."""
    claims = []
    for quarter_data in get_company_data(ticker):
        quarter_label = quarter_data.get("quarter", "unknown")
        source_file = quarter_data.get("_file", "")
        for claim in quarter_data.get("forward_claims", []):
            claims.append({
                "ticker": ticker,
                "quarter": quarter_label,
                "source_file": source_file,
                **claim,
            })
    return claims


def get_wiki_source_summary(ticker: str) -> str | None:
    """Read the most recent wiki source page for a ticker and extract
    a brief summary (first non-frontmatter paragraph)."""
    # Wiki source files follow the pattern: <ticker>-<quarter>.md (lowercase)
    ticker_lower = ticker.lower()
    candidates = sorted(
        WIKI_SOURCES_DIR.glob(f"{ticker_lower}-*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None

    text = candidates[0].read_text()
    # Skip YAML frontmatter
    lines = text.split("\n")
    in_frontmatter = False
    body_lines = []
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            body_lines.append(line)

    # Find first non-empty, non-heading paragraph
    body = "\n".join(body_lines).strip()
    for paragraph in body.split("\n\n"):
        stripped = paragraph.strip()
        if stripped and not stripped.startswith("#"):
            # Limit to ~200 chars
            if len(stripped) > 200:
                return stripped[:200] + "..."
            return stripped
    return None


def get_wiki_concept_context(bottleneck: str) -> str | None:
    """Try to find a wiki concept page matching a bottleneck name."""
    # Map bottleneck keys to likely concept page names
    name_map = {
        "pluggable_optics": "pluggable-optics",
        "copper_signal_integrity": "pluggable-optics",  # related
        "memory": "memory-supercycle",
        "n3_logic": "n3-wafer-crunch",
        "gpu_cloud": "bottleneck-cascade",
        "power": "bottleneck-cascade",
        "cpo_next": "co-packaged-optics",
        "euv": "bottleneck-cascade",
        "foundry": "bottleneck-cascade",
    }
    slug = name_map.get(bottleneck)
    if not slug:
        return None

    concept_path = WIKI_CONCEPTS_DIR / f"{slug}.md"
    if not concept_path.exists():
        return None

    text = concept_path.read_text()
    # Extract first paragraph after frontmatter
    lines = text.split("\n")
    in_frontmatter = False
    body_lines = []
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    for paragraph in body.split("\n\n"):
        stripped = paragraph.strip()
        if stripped and not stripped.startswith("#"):
            if len(stripped) > 300:
                return stripped[:300] + "..."
            return stripped
    return None


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def find_upcoming_earnings(
    ticker_map: dict[str, dict],
    today: date,
    days_out: int,
) -> list[dict]:
    """Find tickers with earnings within the lookahead window."""
    upcoming = []
    cutoff = today + timedelta(days=days_out)

    for ticker, info in ticker_map.items():
        earnings_str = info.get("next_earnings")
        if not earnings_str:
            continue
        try:
            earnings_date = datetime.strptime(earnings_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        if today <= earnings_date <= cutoff:
            days_until = (earnings_date - today).days
            upcoming.append({
                "ticker": ticker,
                "earnings_date": earnings_date,
                "days_until": days_until,
                "bottleneck": info.get("bottleneck", "unknown"),
                "status": info.get("status", "unknown"),
                "also": info.get("also"),
            })

    # Sort by date, then ticker
    upcoming.sort(key=lambda x: (x["earnings_date"], x["ticker"]))
    return upcoming


def find_claims_coming_due(
    tickers: list[str],
    today: date,
    days_out: int,
) -> list[dict]:
    """Find pending forward claims that line up with the next reported quarter."""
    due = []
    for ticker in tickers:
        latest = get_latest_company_data(ticker)
        next_quarter = next_quarter_label((latest or {}).get("quarter"))
        if not next_quarter:
            continue
        for claim in get_forward_claims(ticker):
            if claim.get("status") != "pending":
                continue
            if claim_matches_quarter(claim, next_quarter):
                due.append({
                    **claim,
                    "verify_at": claim_window_label(claim),
                    "due_for_quarter": next_quarter,
                })
    return due


def get_cascade_context(bottleneck: str, cascade: list[dict]) -> dict | None:
    """Find the cascade stage for a bottleneck."""
    # Map ticker_map bottleneck keys to cascade stage names
    name_map = {
        "pluggable_optics": "Pluggable optics",
        "copper_signal_integrity": "Pluggable optics",
        "memory": "Memory supercycle",
        "n3_logic": "N3 logic wafers",
        "gpu_cloud": "Power / DC buildout",  # closest mapping
        "power": "Power / DC buildout",
        "euv": "EUV tools",
        "cpo_next": "Co-packaged optics",
        "foundry": "N3 logic wafers",
    }
    target = name_map.get(bottleneck)
    if not target:
        return None
    for stage in cascade:
        if stage.get("name", "").lower() == target.lower():
            return stage
    return None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    today: date,
    days_out: int,
    upcoming: list[dict],
    deep_dive: list[str],
    cascade: list[dict],
) -> str:
    """Generate the Markdown earnings alert report."""
    lines: list[str] = []

    lines.append(f"# Earnings Alert -- {today.isoformat()}")
    lines.append("")
    lines.append(f"Generated: {today.isoformat()} | Lookahead: {days_out} days | "
                 f"Window: {today.isoformat()} to {(today + timedelta(days=days_out)).isoformat()}")
    lines.append("")

    if not upcoming:
        lines.append("No tickers reporting within the lookahead window.")
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Section 1: Which tickers report
    # -----------------------------------------------------------------------
    this_week = [t for t in upcoming if t["days_until"] <= 7]
    next_week = [t for t in upcoming if 7 < t["days_until"] <= 14]
    later = [t for t in upcoming if t["days_until"] > 14]

    deep_dive_set = set(deep_dive)

    lines.append("## Upcoming Earnings")
    lines.append("")

    def _ticker_line(entry: dict) -> str:
        ticker = entry["ticker"]
        label = "DEEP DIVE" if ticker in deep_dive_set else "watchlist"
        date_str = entry["earnings_date"].strftime("%a %b %d")
        days = entry["days_until"]
        return (f"- **{ticker}** -- {date_str} ({days}d) | "
                f"{entry['bottleneck'].replace('_', ' ')} [{entry['status']}] | {label}")

    if this_week:
        lines.append("### This Week (0-7 days)")
        lines.append("")
        for e in this_week:
            lines.append(_ticker_line(e))
        lines.append("")

    if next_week:
        lines.append("### Next Week (8-14 days)")
        lines.append("")
        for e in next_week:
            lines.append(_ticker_line(e))
        lines.append("")

    if later:
        lines.append("### Later (15+ days)")
        lines.append("")
        for e in later:
            lines.append(_ticker_line(e))
        lines.append("")

    # -----------------------------------------------------------------------
    # Section 2: Deep-dive vs watchlist summary
    # -----------------------------------------------------------------------
    deep_upcoming = [t for t in upcoming if t["ticker"] in deep_dive_set]
    watch_upcoming = [t for t in upcoming if t["ticker"] not in deep_dive_set]

    lines.append("## Coverage Summary")
    lines.append("")
    lines.append(f"- Deep-dive names reporting: {len(deep_upcoming)} "
                 f"({', '.join(t['ticker'] for t in deep_upcoming) or 'none'})")
    lines.append(f"- Watchlist names reporting: {len(watch_upcoming)} "
                 f"({', '.join(t['ticker'] for t in watch_upcoming) or 'none'})")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 3: Pending forward claims coming due
    # -----------------------------------------------------------------------
    reporting_tickers = [t["ticker"] for t in upcoming]
    claims = find_claims_coming_due(reporting_tickers, today, days_out)

    if claims:
        lines.append("## Forward Claims Coming Due")
        lines.append("")
        lines.append("These pending claims can be verified at upcoming earnings:")
        lines.append("")
        for c in claims:
            lines.append(f"### {c['ticker']} -- {c['quarter']}")
            lines.append("")
            lines.append(f"- **Claim:** {c['claim']}")
            if c.get("speaker"):
                lines.append(f"- **Speaker:** {c['speaker']}")
            if c.get("due_for_quarter"):
                lines.append(f"- **Due for:** {c['due_for_quarter']}")
            lines.append(f"- **Verify at:** {c['verify_at']}")
            if c.get("notes"):
                lines.append(f"- **Notes:** {c['notes']}")
            lines.append(f"- **Source file:** `{c.get('source_file', 'unknown')}`")
            lines.append("")
    else:
        lines.append("## Forward Claims Coming Due")
        lines.append("")
        lines.append("No pending forward claims for reporting tickers (or no company data files yet).")
        lines.append("")

    # -----------------------------------------------------------------------
    # Section 4: Bottleneck context from the canonical thesis file
    # -----------------------------------------------------------------------
    lines.append("## Bottleneck Context")
    lines.append("")

    # Group by bottleneck
    bottlenecks_seen: dict[str, list[dict]] = {}
    for entry in upcoming:
        bn = entry["bottleneck"]
        bottlenecks_seen.setdefault(bn, []).append(entry)

    for bn, entries in bottlenecks_seen.items():
        stage = get_cascade_context(bn, cascade)
        tickers_str = ", ".join(e["ticker"] for e in entries)
        lines.append(f"### {bn.replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"Reporting tickers: {tickers_str}")
        if stage:
            lines.append(f"Cascade status: {stage.get('status', 'unknown')}")
            lines.append(f"Period: {stage.get('period', 'unknown')}")
            signals = stage.get("signals", [])
            if signals:
                lines.append("Key signals:")
                for s in signals[:4]:
                    lines.append(f"  - {s}")
            notes = stage.get("notes", "")
            if notes:
                lines.append(f"Notes: {notes.strip()}")
        else:
            lines.append(f"(No cascade stage mapped for '{bn}')")

        # Wiki concept context
        concept_ctx = get_wiki_concept_context(bn)
        if concept_ctx:
            lines.append(f"Wiki context: {concept_ctx}")
        lines.append("")

    # -----------------------------------------------------------------------
    # Section 5: What to watch for
    # -----------------------------------------------------------------------
    lines.append("## What to Watch For")
    lines.append("")

    for entry in upcoming:
        ticker = entry["ticker"]
        lines.append(f"### {ticker}")
        lines.append("")
        lines.append(f"- Earnings: {entry['earnings_date'].strftime('%a %b %d')} "
                     f"({entry['days_until']}d)")
        lines.append(f"- Bottleneck: {entry['bottleneck'].replace('_', ' ')} "
                     f"[{entry['status']}]")
        if entry.get("also"):
            lines.append(f"- Also linked to: {entry['also']}")
        is_deep = ticker in deep_dive_set
        lines.append(f"- Coverage: {'DEEP DIVE' if is_deep else 'watchlist'}")

        # Wiki source summary
        wiki_summary = get_wiki_source_summary(ticker)
        if wiki_summary:
            lines.append(f"- Recent wiki context: {wiki_summary}")

        # Pending claims for this ticker
        ticker_claims = [c for c in claims if c["ticker"] == ticker]
        if ticker_claims:
            lines.append(f"- Pending claims to verify: {len(ticker_claims)}")
            for c in ticker_claims:
                lines.append(f"  - \"{c['claim'][:100]}{'...' if len(c['claim']) > 100 else ''}\"")

        if is_deep:
            lines.append("- Action: Full earnings pipeline treatment. "
                         "Score prior forward_claims. Update canonical/10-wiki/sources/ and canonical/20-data/companies/.")
        else:
            lines.append("- Action: Monitor for thesis signals. "
                         "Update canonical/10-wiki/sources/ if material.")
        lines.append("")

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `agents/src/earnings_calendar.py`. "
                 "This is an automated agent report for comparison against human-curated research.*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def write_log(today: date, upcoming: list[dict], report_path: Path | None, error: str | None = None) -> None:
    """Append a run entry to agents/logs/."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"earnings-calendar-{today.strftime('%Y-%m')}.log"

    tickers = [t["ticker"] for t in upcoming]
    timestamp = datetime.now().isoformat(timespec="seconds")

    entry_lines = [
        f"[{timestamp}] earnings_calendar",
        f"  lookahead_tickers: {', '.join(tickers) if tickers else 'none'}",
        f"  report: {report_path.relative_to(REPO_ROOT) if report_path else 'none (dry-run)'}",
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
    parser = argparse.ArgumentParser(description="Earnings calendar alert agent")
    parser.add_argument("--days", type=int, default=14, help="Lookahead window in days (default: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Print report to stdout without writing files")
    parser.add_argument("--date", type=str, default=None, help="Override today's date (YYYY-MM-DD) for testing")
    args = parser.parse_args()

    # Determine today
    if args.date:
        today = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        today = date.today()

    # Load data
    ticker_map = get_ticker_map()
    if not ticker_map:
        print("ERROR: Could not load ticker_map from canonical/30-thesis/thesis.yaml", file=sys.stderr)
        write_log(today, [], None, error="canonical thesis not found or empty")
        sys.exit(1)

    deep_dive = get_deep_dive_tickers()
    cascade = get_cascade()

    # Find upcoming earnings
    upcoming = find_upcoming_earnings(ticker_map, today, args.days)

    # Generate report
    report = generate_report(today, args.days, upcoming, deep_dive, cascade)

    if args.dry_run:
        print(report)
        write_log(today, upcoming, None)
    else:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"earnings-alert-{today.isoformat()}.md"
        report_path.write_text(report)
        write_log(today, upcoming, report_path)
        print(f"Report written to {report_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
