"""Shared company-packet helpers for quarters, claims, and financial snapshots."""

from __future__ import annotations

import re
from typing import Any

QUARTER_RE = re.compile(r"\bQ([1-4])(?:\s*(FY))?\s*([0-9]{4})\b", re.IGNORECASE)
QUARTER_RANGE_RE = re.compile(r"\bQ([1-4])\s*-\s*Q([1-4])(?:\s*(FY))?\s*([0-9]{4})\b", re.IGNORECASE)
FISCAL_YEAR_RE = re.compile(r"\bFY\s*([0-9]{4})\b", re.IGNORECASE)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("_", " ").strip())


def parse_quarter_label(value: Any) -> tuple[int, int, bool] | None:
    """Parse quarter labels like Q1 2026, Q1_2026, or Q1 FY2027."""
    text = _clean_text(value)
    if not text:
        return None
    match = QUARTER_RE.search(text.upper())
    if not match:
        return None
    quarter = int(match.group(1))
    fiscal = bool(match.group(2))
    year = int(match.group(3))
    return quarter, year, fiscal


def canonical_quarter_label(quarter: int, year: int, fiscal: bool = False) -> str:
    return f"Q{quarter} FY{year}" if fiscal else f"Q{quarter} {year}"


def normalize_quarter_label(value: Any) -> str:
    parsed = parse_quarter_label(value)
    if not parsed:
        return _clean_text(value)
    quarter, year, fiscal = parsed
    return canonical_quarter_label(quarter, year, fiscal)


def quarter_aliases(value: Any) -> set[str]:
    """Return loose quarter aliases for matching legacy and normalized labels."""
    text = _clean_text(value)
    aliases = {text, text.upper(), text.lower()}
    parsed = parse_quarter_label(text)
    if not parsed:
        return {a for a in aliases if a}

    quarter, year, fiscal = parsed
    aliases.update({
        canonical_quarter_label(quarter, year, fiscal),
        canonical_quarter_label(quarter, year, True),
        canonical_quarter_label(quarter, year, False),
        f"Q{quarter}_{year}",
        f"Q{quarter} {year}",
        f"Q{quarter} FY{year}",
    })
    return {a for a in aliases if a}


def next_quarter_label(value: Any) -> str | None:
    """Increment a quarter label while preserving fiscal/calendar notation."""
    parsed = parse_quarter_label(value)
    if not parsed:
        return None
    quarter, year, fiscal = parsed
    quarter += 1
    if quarter == 5:
        quarter = 1
        year += 1
    return canonical_quarter_label(quarter, year, fiscal)


def quarter_key_from_label(value: Any) -> str | None:
    parsed = parse_quarter_label(value)
    if not parsed:
        return None
    quarter, _, _ = parsed
    return f"q{quarter}"


def current_quarter_financials(company: dict) -> tuple[str | None, dict]:
    """Return the normalized latest-quarter financial block from a company packet."""
    financials = company.get("financials", {}) or {}
    preferred = quarter_key_from_label(company.get("quarter"))
    if preferred and isinstance(financials.get(preferred), dict):
        return preferred, financials[preferred]

    for key in ("q1", "q2", "q3", "q4"):
        block = financials.get(key)
        if isinstance(block, dict):
            return key, block
    return None, {}


def pick_revenue_metric(snapshot: dict) -> tuple[str | None, Any]:
    candidates = [
        ("revenue", "Revenue"),
        ("revenue_usd", "Revenue"),
        ("revenue_ntd", "Revenue"),
        ("data_center_revenue", "Data Center"),
        ("products_revenue", "Products"),
    ]
    for key, label in candidates:
        if key in snapshot:
            return label, snapshot[key]
    return None, None


def pick_margin_metric(snapshot: dict) -> tuple[str | None, Any]:
    candidates = [
        ("gross_margin_non_gaap", "Gross Margin"),
        ("gross_margin_gaap", "Gross Margin"),
        ("operating_margin_non_gaap", "Operating Margin"),
        ("operating_margin_gaap", "Operating Margin"),
        ("adjusted_ebitda_margin", "Adj EBITDA Margin"),
        ("net_profit_margin", "Net Margin"),
    ]
    for key, label in candidates:
        if key in snapshot:
            return label, snapshot[key]
    return None, None


def pick_primary_guidance(company: dict) -> tuple[str | None, dict]:
    """Return the first guidance block that looks like an actionable next checkpoint."""
    guidance = company.get("guidance", {}) or {}
    interesting = (
        "revenue",
        "revenue_usd",
        "gross_margin_gaap",
        "gross_margin_non_gaap",
        "operating_margin_gaap",
        "operating_margin_non_gaap",
        "eps_gaap",
        "eps_non_gaap",
    )
    for key, block in guidance.items():
        if isinstance(block, dict) and any(metric in block for metric in interesting):
            return key, block
    for key, block in guidance.items():
        if isinstance(block, dict):
            return key, block
    return None, {}


def format_period_key(key: str | None) -> str:
    if not key:
        return "—"
    return key.replace("_", " ").upper()


def infer_verify_window(verify_at: Any) -> dict:
    """Infer a structured claim window from legacy verify_at prose."""
    label = _clean_text(verify_at)
    lower = label.lower()
    if not label:
        return {}
    if lower == "ongoing":
        return {"kind": "ongoing", "label": label}

    range_match = QUARTER_RANGE_RE.search(label.upper())
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        fiscal = bool(range_match.group(3))
        year = int(range_match.group(4))
        targets = [canonical_quarter_label(q, year, fiscal) for q in range(start, end + 1)]
        return {"kind": "earnings", "targets": targets, "label": label}

    quarter_matches = list(QUARTER_RE.finditer(label.upper()))
    if quarter_matches:
        targets = [
            canonical_quarter_label(int(match.group(1)), int(match.group(3)), bool(match.group(2)))
            for match in quarter_matches
        ]
        return {"kind": "earnings", "targets": targets, "label": label}

    fy_match = FISCAL_YEAR_RE.search(label.upper())
    if fy_match and "quarterly results" in lower:
        year = int(fy_match.group(1))
        return {
            "kind": "earnings",
            "targets": [canonical_quarter_label(q, year, True) for q in range(1, 5)],
            "label": label,
        }

    if fy_match and "results" in lower:
        year = int(fy_match.group(1))
        return {
            "kind": "earnings",
            "targets": [canonical_quarter_label(4, year, True)],
            "label": label,
        }

    if re.search(r"\b(?:h1|h2|calendar|20\d{2})\b", lower):
        return {"kind": "commentary", "targets": [label], "label": label}

    return {"kind": "commentary", "targets": [label], "label": label}


def claim_verify_window(claim: dict) -> dict:
    window = dict(claim.get("verify_window") or {})
    if not window:
        window = infer_verify_window(claim.get("verify_at", ""))
    if "label" not in window:
        window["label"] = _clean_text(claim.get("verify_at", "")) or "—"
    return window


def claim_window_label(claim: dict) -> str:
    return claim_verify_window(claim).get("label", "—")


def claim_matches_quarter(claim: dict, quarter: str) -> bool:
    window = claim_verify_window(claim)
    if window.get("kind") != "earnings":
        return False
    requested = quarter_aliases(quarter)
    for target in window.get("targets", []):
        if requested & quarter_aliases(target):
            return True
    return False
