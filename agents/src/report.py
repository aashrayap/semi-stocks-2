#!/usr/bin/env python3
"""Agent fleet report generator.

Builds an HTML report from agent-generated data: predictions, scorecards,
earnings alerts, and draft analysis. Mirrors the visual style of the
canonical report stage while sourcing exclusively from agents/ and reading
canonical repo data for context.

Usage:
    python agents/src/report.py
    python agents/src/report.py --date 2026-04-07
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
import re
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from runtime_paths import data_root, repo_root, thesis_path


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = SCRIPT_DIR.parent
REPO_ROOT = repo_root()

PREDICTIONS_DIR = AGENTS_DIR / "state" / "predictions"
REPORTS_DIR = AGENTS_DIR / "reports"
DRAFTS_DIR = AGENTS_DIR / "drafts"
LOGS_DIR = AGENTS_DIR / "logs"
THESIS_PATH = thesis_path(REPO_ROOT)
COMPANIES_DIR = data_root(REPO_ROOT) / "companies"
AGENT_CONFIG_PATH = AGENTS_DIR / "config.yaml"


# ---------------------------------------------------------------------------
# YAML / data loading
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def load_all_predictions() -> list[dict]:
    """Load all prediction YAMLs."""
    preds = []
    if not PREDICTIONS_DIR.exists():
        return preds
    for f in sorted(PREDICTIONS_DIR.glob("*.yaml")):
        data = load_yaml(f)
        if data and "predictions" in data:
            data["_file"] = f.name
            preds.append(data)
    return preds


def load_thesis() -> dict:
    return load_yaml(THESIS_PATH) or {}


def load_agent_config() -> dict:
    return load_yaml(AGENT_CONFIG_PATH) or {}


def load_company_data(ticker: str) -> list[dict]:
    """Load all quarter YAMLs for a ticker."""
    ticker_dir = COMPANIES_DIR / ticker
    if not ticker_dir.exists():
        return []
    results = []
    for f in sorted(ticker_dir.glob("q*.yaml")):
        data = load_yaml(f)
        if data:
            results.append(data)
    return results


def count_drafts() -> dict:
    """Count files in each drafts subdirectory."""
    counts = {}
    for sub in ["13f", "earnings", "signals"]:
        d = DRAFTS_DIR / sub
        if d.exists():
            counts[sub] = len([f for f in d.iterdir() if f.name != ".gitkeep"])
        else:
            counts[sub] = 0
    return counts


TIMESTAMP_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\]")


def _parse_log_timestamp(line: str) -> datetime | None:
    match = TIMESTAMP_RE.match(line)
    if not match:
        return None
    try:
        return datetime.fromisoformat(match.group(1))
    except ValueError:
        return None


def _flush_log_entry(entries: list[tuple[datetime, str]], timestamp: datetime | None, lines: list[str]) -> None:
    if not timestamp or not lines:
        return
    text = " | ".join(line.strip() for line in lines if line.strip())
    if not text:
        return
    if " DEBUG " in text or text.endswith("=" * 60):
        return
    entries.append((timestamp, text))


def recent_logs(n: int = 10) -> list[str]:
    """Get the most recent meaningful log entries across all log files."""
    entries: list[tuple[datetime, str]] = []
    if not LOGS_DIR.exists():
        return []

    for f in LOGS_DIR.glob("*.log"):
        current_ts: datetime | None = None
        current_lines: list[str] = []

        with open(f) as fh:
            for raw_line in fh:
                line = raw_line.rstrip("\n")
                ts = _parse_log_timestamp(line)

                if ts is not None:
                    _flush_log_entry(entries, current_ts, current_lines)
                    current_ts = ts
                    current_lines = [line]
                    continue

                if not line.strip():
                    _flush_log_entry(entries, current_ts, current_lines)
                    current_ts = None
                    current_lines = []
                    continue

                if current_lines:
                    current_lines.append(line)

        _flush_log_entry(entries, current_ts, current_lines)

    entries.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in entries[:n]]


# ---------------------------------------------------------------------------
# Formatting helpers (match main report style)
# ---------------------------------------------------------------------------

def _fmt_value(val: int | float | None) -> str:
    if val is None or val == 0:
        return "—"
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.0f}M"
    return f"${val:,.0f}"


def _status_icon(status: str) -> str:
    return {
        "played_out": "&#9989;",
        "active": "&#128308;",
        "active_emerging": "&#128992;",
        "emerging": "&#128993;",
        "next": "&#11093;",
    }.get(status, "&#9675;")


def _confidence_badge(conf: str) -> str:
    colors = {
        "high": ("#238636", "#fff"),
        "medium": ("#9e6a03", "#fff"),
        "low": ("#21262d", "#8b949e"),
    }
    bg, fg = colors.get(conf, ("#21262d", "#8b949e"))
    return f'<span class="badge" style="background:{bg};color:{fg}">{conf}</span>'


def _status_badge(status: str) -> str:
    colors = {
        "pending": ("#21262d", "#8b949e"),
        "confirmed": ("#238636", "#fff"),
        "missed": ("#da3633", "#fff"),
        "partial": ("#9e6a03", "#fff"),
        "revised": ("#6e7681", "#fff"),
    }
    bg, fg = colors.get(status, ("#21262d", "#8b949e"))
    return f'<span class="badge" style="background:{bg};color:{fg}">{status.upper()}</span>'


def _category_icon(cat: str) -> str:
    return {
        "capacity": "&#9881;",
        "pricing": "&#128176;",
        "demand": "&#128200;",
        "margins": "&#128202;",
        "guidance": "&#128227;",
        "positioning": "&#127919;",
    }.get(cat, "&#9679;")


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def build_summary(predictions: list[dict], thesis: dict, today_dt: date) -> str:
    """Build the summary box."""
    total_preds = sum(len(p.get("predictions", [])) for p in predictions)
    pending = sum(
        1 for p in predictions
        for pr in p.get("predictions", [])
        if pr.get("status") == "pending"
    )
    confirmed = sum(
        1 for p in predictions
        for pr in p.get("predictions", [])
        if pr.get("status") == "confirmed"
    )
    missed = sum(
        1 for p in predictions
        for pr in p.get("predictions", [])
        if pr.get("status") == "missed"
    )
    partial = sum(
        1 for p in predictions
        for pr in p.get("predictions", [])
        if pr.get("status") == "partial"
    )
    scored = confirmed + missed + partial
    accuracy = ((confirmed + 0.5 * partial) / scored * 100) if scored > 0 else None

    tickers_covered = sorted(set(p["ticker"] for p in predictions))

    # Next earnings
    ticker_map = thesis.get("ticker_map", {})
    upcoming = []
    for ticker, meta in ticker_map.items():
        ne = meta.get("next_earnings")
        if ne:
            try:
                ne_dt = datetime.strptime(ne, "%Y-%m-%d").date()
                days = (ne_dt - today_dt).days
                if 0 < days <= 14:
                    upcoming.append((ticker, ne_dt, days))
            except ValueError:
                pass
    upcoming.sort(key=lambda x: x[2])

    html = (
        f"<strong>Agent Fleet Status:</strong> Tracking "
        f"<strong>{total_preds} predictions</strong> across "
        f"{len(tickers_covered)} ticker{'s' if len(tickers_covered) != 1 else ''}"
        f" ({', '.join(tickers_covered) if tickers_covered else 'none yet'})."
    )

    if scored > 0:
        html += (
            f" Scored: <strong>{scored}</strong> "
            f"(<span style='color:#238636'>{confirmed} confirmed</span>"
            f", <span style='color:#da3633'>{missed} missed</span>"
            f"{f', {partial} partial' if partial else ''}"
            f"). Accuracy: <strong>{accuracy:.0f}%</strong>."
        )
    else:
        html += f" <em>{pending} predictions pending — waiting for earnings.</em>"

    if upcoming:
        next_list = ", ".join(
            f"<strong>{t}</strong> ({d}d)" for t, _, d in upcoming[:5]
        )
        html += f"<br><br><strong>Next earnings:</strong> {next_list}"

    return html


def build_predictions_table(predictions: list[dict], today_dt: date) -> str:
    """Build the predictions overview table."""
    rows = ""
    for pred_file in predictions:
        ticker = pred_file.get("ticker", "?")
        quarter = pred_file.get("quarter", "?")
        bottleneck = pred_file.get("bottleneck", "?")
        bn_status = pred_file.get("bottleneck_status", "?")
        earnings_date = pred_file.get("earnings_date", "")
        preds = pred_file.get("predictions", [])

        # Days to earnings
        days_cell = "—"
        if earnings_date:
            try:
                ed = datetime.strptime(earnings_date, "%Y-%m-%d").date()
                days = (ed - today_dt).days
                if days > 0:
                    color = "#da3633" if days <= 7 else "#f0883e" if days <= 14 else "#8b949e"
                    days_cell = f'<span style="color:{color};font-weight:600">{days}d</span>'
                else:
                    days_cell = '<span style="color:#238636">REPORTED</span>'
            except ValueError:
                pass

        # Count by status
        statuses = {}
        for p in preds:
            s = p.get("status", "pending")
            statuses[s] = statuses.get(s, 0) + 1

        status_parts = []
        for s in ["confirmed", "partial", "missed", "pending"]:
            if statuses.get(s, 0) > 0:
                status_parts.append(f"{_status_badge(s)} {statuses[s]}")
        status_cell = " ".join(status_parts)

        # Confidence breakdown
        confs = {}
        for p in preds:
            c = p.get("confidence", "?")
            confs[c] = confs.get(c, 0) + 1
        conf_cell = " ".join(
            f"{_confidence_badge(c)} {n}" for c, n in
            sorted(confs.items(), key=lambda x: ["high", "medium", "low"].index(x[0])
                   if x[0] in ["high", "medium", "low"] else 99)
        )

        icon = _status_icon(bn_status)
        rows += f"""
        <tr>
            <td><strong>{ticker}</strong></td>
            <td>{quarter}</td>
            <td>{icon} {bottleneck}</td>
            <td>{days_cell}</td>
            <td>{len(preds)}</td>
            <td>{conf_cell}</td>
            <td>{status_cell}</td>
        </tr>"""

    return rows


def build_predictions_detail(predictions: list[dict]) -> str:
    """Build detailed per-ticker prediction cards."""
    html = ""
    for pred_file in predictions:
        ticker = pred_file.get("ticker", "?")
        quarter = pred_file.get("quarter", "?")
        preds = pred_file.get("predictions", [])
        pos = pred_file.get("positioning_context", {})
        track = pred_file.get("track_record", {})

        # Track record bar
        total = track.get("total_predictions", 0)
        acc = track.get("accuracy")
        track_html = ""
        if total > 0 and acc is not None:
            pct = int(acc * 100)
            color = "#238636" if pct >= 70 else "#9e6a03" if pct >= 50 else "#da3633"
            track_html = (
                f'<span class="small" style="color:{color}">'
                f'Track record: {pct}% ({track.get("confirmed", 0)}/{total})</span>'
            )

        # Positioning context
        pos_html = ""
        if pos:
            parts = []
            if pos.get("leopold"):
                parts.append(f"<strong>Leopold:</strong> {pos['leopold']}")
            if pos.get("baker"):
                parts.append(f"<strong>Baker:</strong> {pos['baker']}")
            if pos.get("implied_signal"):
                parts.append(f"<em>{pos['implied_signal']}</em>")
            pos_html = "<br>".join(parts)

        # Individual predictions
        pred_rows = ""
        for p in preds:
            cat = p.get("category", "?")
            icon = _category_icon(cat)
            claim = p.get("claim", "")
            conf = p.get("confidence", "?")
            status = p.get("status", "pending")
            basis = p.get("basis", [])

            basis_html = ""
            for b in basis[:3]:
                src = b.get("source", "")
                det = b.get("detail", "")
                basis_html += f"<br>&nbsp;&nbsp;&#8226; <code>{src}</code>: {det[:80]}"
            if len(basis) > 3:
                basis_html += f"<br>&nbsp;&nbsp;<span class='small'>+{len(basis)-3} more</span>"

            pred_rows += f"""
            <tr>
                <td>{icon} {cat}</td>
                <td>{claim}</td>
                <td>{_confidence_badge(conf)}</td>
                <td>{_status_badge(status)}</td>
                <td class="small">{basis_html}</td>
            </tr>"""

        html += f"""
        <div class="ticker-card">
            <div class="ticker-header">
                <strong>{ticker}</strong> — {quarter}
                {track_html}
            </div>
            {"" if not pos_html else f'<div class="small" style="margin-bottom:10px">{pos_html}</div>'}
            <table>
                <tr><th>Category</th><th>Prediction</th><th>Confidence</th><th>Status</th><th>Basis</th></tr>
                {pred_rows}
            </table>
        </div>"""

    return html


def build_upcoming_earnings(thesis: dict, today_dt: date) -> str:
    """Build the upcoming earnings table from the canonical thesis file."""
    ticker_map = thesis.get("ticker_map", {})
    config = load_agent_config()
    deep_dive = config.get("deep_dive", [])

    upcoming = []
    for ticker, meta in ticker_map.items():
        ne = meta.get("next_earnings")
        if not ne:
            continue
        try:
            ne_dt = datetime.strptime(ne, "%Y-%m-%d").date()
            days = (ne_dt - today_dt).days
            if 0 < days <= 30:
                upcoming.append({
                    "ticker": ticker,
                    "date": ne_dt,
                    "days": days,
                    "bottleneck": meta.get("bottleneck", ""),
                    "status": meta.get("status", ""),
                    "deep_dive": ticker in deep_dive,
                })
        except ValueError:
            pass

    upcoming.sort(key=lambda x: x["days"])

    rows = ""
    for u in upcoming:
        color = "#da3633" if u["days"] <= 7 else "#f0883e" if u["days"] <= 14 else "#c9d1d9"
        dd_badge = '<span class="badge full">DEEP DIVE</span>' if u["deep_dive"] else '<span class="badge single">watchlist</span>'
        icon = _status_icon(u["status"])

        # Check if prediction exists
        has_pred = any(
            (PREDICTIONS_DIR / f"{u['ticker']}-Q{((u['date'].month - 1) // 3) + 1}_{u['date'].year}.yaml").exists()
            for _ in [None]  # hack to check without separate variable
        ) or (PREDICTIONS_DIR / f"{u['ticker']}-Q1_{u['date'].year}.yaml").exists()
        pred_cell = "&#9989;" if has_pred else '<span style="color:#f0883e">missing</span>'

        rows += f"""
        <tr>
            <td><strong>{u['ticker']}</strong></td>
            <td style="color:{color};font-weight:600">{u['date'].strftime('%b %d')} ({u['days']}d)</td>
            <td>{icon} {u['bottleneck']}</td>
            <td>{dd_badge}</td>
            <td>{pred_cell}</td>
        </tr>"""

    return rows


def build_drafts_status() -> str:
    """Show what's in the drafts pipeline."""
    counts = count_drafts()
    rows = ""
    for category, count in counts.items():
        icon = "&#128196;" if count > 0 else "&#9675;"
        badge = f'<span class="badge full">{count} pending</span>' if count > 0 else '<span class="badge single">empty</span>'
        rows += f"""
        <tr>
            <td>{icon} agents/drafts/{category}/</td>
            <td>{badge}</td>
        </tr>"""
    return rows


def build_log_activity() -> str:
    """Show recent agent activity."""
    lines = recent_logs(8)
    if not lines:
        return '<tr><td class="small">No agent activity logged yet.</td></tr>'
    rows = ""
    for line in lines:
        rows += f'<tr><td class="small">{escape(line[:220])}</td></tr>'
    return rows


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(today_dt: date | None = None) -> str:
    today_dt = today_dt or date.today()
    today_str = today_dt.strftime("%B %d, %Y")

    thesis = load_thesis()
    predictions = load_all_predictions()

    summary_html = build_summary(predictions, thesis, today_dt)
    predictions_rows = build_predictions_table(predictions, today_dt)
    predictions_detail = build_predictions_detail(predictions)
    upcoming_rows = build_upcoming_earnings(thesis, today_dt)
    drafts_status = build_drafts_status()
    log_activity = build_log_activity()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>semi-stocks agents | {today_str}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, 'SF Mono', monospace; background: #0d1117; color: #c9d1d9; padding: 24px; }}
    h1 {{ color: #58a6ff; font-size: 20px; margin-bottom: 4px; }}
    h2 {{ color: #8b949e; font-size: 14px; margin-bottom: 20px; font-weight: normal; }}
    h3 {{ color: #f0f6fc; font-size: 15px; margin: 28px 0 12px 0; padding-bottom: 6px; border-bottom: 1px solid #21262d; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }}
    th {{ text-align: left; padding: 8px 10px; background: #161b22; color: #8b949e; font-weight: 600; border-bottom: 1px solid #21262d; }}
    td {{ padding: 6px 10px; border-bottom: 1px solid #21262d; vertical-align: top; }}
    tr:hover {{ background: #161b22; }}
    .badge {{ padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }}
    .badge.full {{ background: #238636; color: #fff; }}
    .badge.partial {{ background: #9e6a03; color: #fff; }}
    .badge.single {{ background: #21262d; color: #8b949e; }}
    .badge.missed {{ background: #da3633; color: #fff; }}
    .meta {{ display: flex; gap: 32px; margin-bottom: 20px; font-size: 13px; color: #8b949e; }}
    .meta strong {{ color: #c9d1d9; }}
    .small {{ font-size: 11px; color: #8b949e; line-height: 1.5; }}
    .section {{ margin-bottom: 32px; }}
    .summary {{ background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 16px 20px; margin-bottom: 28px; font-size: 13px; line-height: 1.7; }}
    .summary strong {{ color: #58a6ff; }}
    .summary em {{ color: #f0883e; font-style: normal; }}
    .ticker-card {{ background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; }}
    .ticker-header {{ font-size: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
    details {{ margin-bottom: 20px; }}
    details summary {{ cursor: pointer; color: #8b949e; font-size: 13px; padding: 8px 0; }}
    details summary:hover {{ color: #c9d1d9; }}
    code {{ background: #21262d; padding: 1px 5px; border-radius: 3px; font-size: 11px; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
</style>
</head>
<body>

<h1>semi-stocks <span style="color:#8b949e;font-weight:normal">agents</span></h1>
<h2>Agent fleet report | {today_str}</h2>

<div class="summary">
{summary_html}
</div>

<div class="section">
<h3>PREDICTION OVERVIEW</h3>
{"<table><tr><th>Ticker</th><th>Quarter</th><th>Bottleneck</th><th>Earnings</th><th>Claims</th><th>Confidence</th><th>Status</th></tr>" + predictions_rows + "</table>" if predictions_rows else '<p class="small">No predictions generated yet. Run: <code>python3 agents/src/pre_earnings_predictor.py --all-upcoming</code></p>'}
</div>

<div class="section">
<h3>PREDICTION DETAIL</h3>
{predictions_detail if predictions_detail else '<p class="small">No prediction detail available.</p>'}
</div>

<div class="section">
<h3>UPCOMING EARNINGS</h3>
{"<table><tr><th>Ticker</th><th>Date</th><th>Bottleneck</th><th>Coverage</th><th>Prediction</th></tr>" + upcoming_rows + "</table>" if upcoming_rows else '<p class="small">No earnings in the next 30 days.</p>'}
</div>

<div class="two-col">
<div class="section">
<h3>DRAFTS PIPELINE</h3>
<table>
    <tr><th>Directory</th><th>Status</th></tr>
    {drafts_status}
</table>
</div>

<div class="section">
<h3>RECENT AGENT ACTIVITY</h3>
<table>
    {log_activity}
</table>
</div>
</div>

<div class="small" style="margin-top: 20px; color: #484f58;">
    Generated by <code>agents/src/report.py</code> | Agent fleet report — parallel to main <code>canonical/50-reports/latest.html</code>
</div>

</body>
</html>"""

    return html


def build_report(today_dt: date | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    html = generate_html(today_dt)
    out = REPORTS_DIR / "latest.html"
    out.write_text(html)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate agent fleet HTML report")
    parser.add_argument("--date", help="Override today (YYYY-MM-DD)")
    args = parser.parse_args()

    dt = None
    if args.date:
        dt = datetime.strptime(args.date, "%Y-%m-%d").date()

    path = build_report(dt)
    print(f"Agent report written to {path}")
