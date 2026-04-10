#!/usr/bin/env python3
"""Pre-earnings prediction generator.

Reads the entire semi-stocks knowledge graph and generates testable,
deterministic predictions for upcoming earnings. Predictions are
template-based (no LLM) — the script assembles structure and fills in
evidence from data sources. A human or agent refines afterward.

Usage:
    python agents/src/pre_earnings_predictor.py --ticker TSM --quarter Q1_2026
    python agents/src/pre_earnings_predictor.py --all-upcoming
    python agents/src/pre_earnings_predictor.py --ticker TSM --quarter Q1_2026 --dry-run
"""

from __future__ import annotations

import argparse
import os
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

def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser().resolve() if raw else default.resolve()


SCRIPT_DIR = Path(__file__).resolve().parent          # agents/src/
AGENTS_DIR = SCRIPT_DIR.parent                        # agents/
REPO_ROOT = repo_root()                               # semi-stocks/
READ_ROOT = _env_path("SEMI_STOCKS_READ_ROOT", REPO_ROOT)
STATE_ROOT = _env_path("SEMI_STOCKS_STATE_ROOT", AGENTS_DIR)
ENGINE_STAGE = engine_stage(REPO_ROOT)
DATA_ROOT = data_root(READ_ROOT)
WIKI_ROOT = wiki_root(READ_ROOT)

if str(ENGINE_STAGE) not in sys.path:
    sys.path.insert(0, str(ENGINE_STAGE))

from engine.company_data import (  # noqa: E402
    claim_matches_quarter,
    current_quarter_financials,
    next_quarter_label,
    normalize_quarter_label,
)

THESIS_PATH = thesis_path(READ_ROOT)
COMPANIES_DIR = DATA_ROOT / "companies"
LEOPOLD_DIR = DATA_ROOT / "sources" / "leopold"
BAKER_DIR = DATA_ROOT / "sources" / "baker"
SEMIANALYSIS_DIR = DATA_ROOT / "sources" / "semianalysis"
WIKI_CONCEPTS_DIR = WIKI_ROOT / "concepts"
WIKI_SOURCES_DIR = WIKI_ROOT / "sources"
AGENT_CONFIG_PATH = AGENTS_DIR / "config.yaml"
PREDICTIONS_DIR = STATE_ROOT / "state" / "predictions"
LOGS_DIR = STATE_ROOT / "logs"

RUNTIME_AS_OF_DATE: date | None = None


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


def parse_iso_date(value: Any) -> date | None:
    """Parse YYYY-MM-DD-ish values, returning None for non-date strings."""
    if value in (None, ""):
        return None
    text = str(value).strip()
    if len(text) >= 10:
        text = text[:10]
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def is_visible_on_or_before(as_of: date | None, visible_date: date | None) -> bool:
    """Whether a public data point is visible on a given as-of date."""
    if as_of is None or visible_date is None:
        return True
    return visible_date <= as_of


def is_reported_before(as_of: date | None, report_date: date | None) -> bool:
    """Whether reported results existed before the simulated prediction date."""
    if as_of is None or report_date is None:
        return True
    return report_date < as_of


def display_path(path: Path) -> str:
    """Render a path relative to the active read/state roots when possible."""
    resolved = path.resolve()
    for base in (STATE_ROOT, READ_ROOT, REPO_ROOT):
        try:
            return str(resolved.relative_to(base.resolve()))
        except ValueError:
            continue
    return str(resolved)


# ---------------------------------------------------------------------------
# Data readers
# ---------------------------------------------------------------------------

def get_agent_config() -> dict:
    cfg = load_yaml(AGENT_CONFIG_PATH)
    return cfg if cfg else {}


def get_thesis() -> dict:
    thesis = load_yaml(THESIS_PATH)
    return thesis if thesis else {}


def get_ticker_map() -> dict[str, dict]:
    return get_thesis().get("ticker_map", {})


def get_cascade() -> list[dict]:
    return get_thesis().get("cascade", [])


def get_cascade_for_bottleneck(bottleneck: str) -> dict | None:
    """Find the cascade stage matching a bottleneck key."""
    name_map = {
        "pluggable_optics": "Pluggable optics (scale-out)",
        "copper_signal_integrity": "Co-packaged optics / CPO (scale-up)",
        "memory": "Memory supercycle",
        "n3_logic": "N3 logic wafers",
        "gpu_cloud": "Power / DC buildout",
        "power": "Power / DC buildout",
        "euv": "EUV tools",
        "cpo_next": "Co-packaged optics / CPO (scale-up)",
        "foundry": "N3 logic wafers",
    }
    target = name_map.get(bottleneck)
    if not target:
        return None
    for stage in get_cascade():
        if stage.get("name", "").lower() == target.lower():
            return stage
    return None


def get_company_quarters(ticker: str) -> list[dict]:
    """Load all quarterly YAML files for a company."""
    company_dir = COMPANIES_DIR / ticker
    if not company_dir.is_dir():
        return []
    results: list[tuple[date, str, dict]] = []
    for f in sorted(company_dir.glob("*.yaml")):
        data = load_yaml(f)
        if data:
            report_date = (parse_iso_date(data.get("earnings_date"))
                           or parse_iso_date(data.get("period")))
            if not is_reported_before(RUNTIME_AS_OF_DATE, report_date):
                continue
            data["_file"] = display_path(f)
            sort_key = report_date or date.min
            results.append((sort_key, f.name, data))
    results.sort(key=lambda item: (item[0], item[1]))
    return [data for _, _, data in results]


def get_latest_company_data(ticker: str) -> dict | None:
    """Get the most recent quarter data for a company."""
    quarters = get_company_quarters(ticker)
    if not quarters:
        return None
    return quarters[-1]


def get_forward_claims(ticker: str) -> list[dict]:
    """Extract all forward_claims from a company's quarterly files."""
    claims = []
    for quarter_data in get_company_quarters(ticker):
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


def get_fund_positions(fund_dir: Path) -> list[dict]:
    """Load the latest fund positioning file."""
    if not fund_dir.is_dir():
        return []
    files = sorted(fund_dir.glob("*.yaml"), key=lambda p: p.name, reverse=True)
    for f in files:
        data = load_yaml(f)
        if not data:
            continue
        filed_date = (parse_iso_date(data.get("filed"))
                      or parse_iso_date(data.get("period")))
        if is_visible_on_or_before(RUNTIME_AS_OF_DATE, filed_date):
            return data.get("positions", [])
    return []


def get_fund_position_for_ticker(fund_dir: Path, ticker: str) -> list[dict]:
    """Get all positions for a ticker from a fund (may have multiple: common + calls + puts)."""
    positions = get_fund_positions(fund_dir)
    return [p for p in positions if p.get("ticker") == ticker]


def get_fund_exits(fund_dir: Path) -> list[dict]:
    """Get exits from latest fund filing."""
    if not fund_dir.is_dir():
        return []
    files = sorted(fund_dir.glob("*.yaml"), key=lambda p: p.name, reverse=True)
    for f in files:
        data = load_yaml(f)
        if not data:
            continue
        filed_date = (parse_iso_date(data.get("filed"))
                      or parse_iso_date(data.get("period")))
        if is_visible_on_or_before(RUNTIME_AS_OF_DATE, filed_date):
            return data.get("exits", [])
    return []


def get_semianalysis_signals() -> dict:
    """Load SemiAnalysis signals."""
    data = load_yaml(SEMIANALYSIS_DIR / "signals.yaml")
    if not data:
        return {}

    if RUNTIME_AS_OF_DATE is None:
        return data

    filtered = dict(data)
    for key in ("signals", "media", "market_data"):
        entries = data.get(key)
        if not isinstance(entries, list):
            continue
        filtered[key] = [
            entry for entry in entries
            if is_visible_on_or_before(RUNTIME_AS_OF_DATE, parse_iso_date(entry.get("date")))
        ]
    return filtered


def get_semianalysis_for_ticker(ticker: str) -> list[dict]:
    """Get SemiAnalysis signals mentioning a ticker."""
    sa = get_semianalysis_signals()
    matching = []
    for signal in sa.get("signals", []):
        if ticker in signal.get("tickers", []):
            matching.append(signal)
    return matching


def get_semianalysis_for_bottleneck(bottleneck: str) -> list[dict]:
    """Get SemiAnalysis signals for a bottleneck."""
    sa = get_semianalysis_signals()
    matching = []
    for signal in sa.get("signals", []):
        if signal.get("bottleneck") == bottleneck:
            matching.append(signal)
        # Also match optical -> pluggable_optics / cpo_next
        if bottleneck in ("pluggable_optics", "cpo_next") and signal.get("bottleneck") == "optical":
            matching.append(signal)
    return matching


def get_wiki_concept_for_bottleneck(bottleneck: str) -> str | None:
    """Find the wiki concept page path for a bottleneck."""
    slug_map = {
        "pluggable_optics": "pluggable-optics",
        "copper_signal_integrity": "pluggable-optics",
        "memory": "memory-supercycle",
        "n3_logic": "n3-wafer-crunch",
        "gpu_cloud": "bottleneck-cascade",
        "power": "bottleneck-cascade",
        "cpo_next": "co-packaged-optics",
        "euv": "bottleneck-cascade",
        "foundry": "bottleneck-cascade",
    }
    slug = slug_map.get(bottleneck)
    if not slug:
        return None
    concept_path = WIKI_CONCEPTS_DIR / f"{slug}.md"
    if concept_path.exists():
        return display_path(concept_path)
    return None


def get_wiki_sources_for_ticker(ticker: str) -> list[str]:
    """Find wiki source pages for a ticker."""
    ticker_lower = ticker.lower()
    paths = sorted(WIKI_SOURCES_DIR.glob(f"{ticker_lower}-*.md"))
    return [display_path(p) for p in paths]


def get_prior_predictions(ticker: str) -> list[dict]:
    """Load all prior prediction files for a ticker."""
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    preds = []
    for f in sorted(PREDICTIONS_DIR.glob(f"{ticker}-*.yaml")):
        data = load_yaml(f)
        if data:
            predicted_at = parse_iso_date(data.get("predicted_at"))
            if RUNTIME_AS_OF_DATE is not None and predicted_at is not None and predicted_at >= RUNTIME_AS_OF_DATE:
                continue
            data["_file"] = display_path(f)
            preds.append(data)
    return preds


# ---------------------------------------------------------------------------
# Track record calculation
# ---------------------------------------------------------------------------

def calculate_track_record(ticker: str) -> dict:
    """Calculate prediction accuracy from prior prediction files."""
    priors = get_prior_predictions(ticker)
    total = 0
    confirmed = 0
    missed = 0
    partial = 0
    revised = 0
    by_category: dict[str, dict] = {}

    for pred_file in priors:
        for pred in pred_file.get("predictions", []):
            status = pred.get("status", "pending")
            if status == "pending":
                continue
            cat = pred.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = {"total": 0, "confirmed": 0, "missed": 0, "partial": 0}

            total += 1
            by_category[cat]["total"] += 1

            if status == "confirmed":
                confirmed += 1
                by_category[cat]["confirmed"] += 1
            elif status == "missed":
                missed += 1
                by_category[cat]["missed"] += 1
            elif status == "partial":
                partial += 1
                by_category[cat]["partial"] += 1
            elif status == "revised":
                revised += 1

    accuracy = round(confirmed / total, 3) if total > 0 else None
    return {
        "total_predictions": total,
        "confirmed": confirmed,
        "missed": missed,
        "partial": partial,
        "revised": revised,
        "accuracy": accuracy,
        "by_category": by_category if by_category else None,
    }


# ---------------------------------------------------------------------------
# Prediction templates per bottleneck category
# ---------------------------------------------------------------------------

# Each template is a function that returns a list of prediction dicts.
# Templates scan available data and fill in what they can.

def _make_prediction(claim: str, category: str, basis: list[dict],
                     confidence: str, verify_at: str) -> dict:
    """Helper to create a prediction dict."""
    return {
        "claim": claim,
        "category": category,
        "basis": basis,
        "confidence": confidence,
        "verify_at": verify_at,
        "status": "pending",
    }


def _gather_basis_from_cascade(bottleneck: str) -> list[dict]:
    """Gather basis entries from cascade signals."""
    stage = get_cascade_for_bottleneck(bottleneck)
    if not stage:
        return []
    basis = []
    for signal in stage.get("signals", [])[:3]:  # top 3 signals
        basis.append({
            "source": "canonical/30-thesis/thesis.yaml",
            "detail": signal,
        })
    return basis


def _gather_basis_from_semianalysis(ticker: str, bottleneck: str) -> list[dict]:
    """Gather basis entries from SemiAnalysis signals."""
    basis = []
    # By ticker
    for signal in get_semianalysis_for_ticker(ticker):
        for dp in signal.get("data_points", [])[:2]:  # top 2 per signal
            basis.append({
                "source": "canonical/20-data/sources/semianalysis/signals.yaml",
                "detail": dp,
            })
    # By bottleneck (avoid duplicates)
    seen_details = {b["detail"] for b in basis}
    for signal in get_semianalysis_for_bottleneck(bottleneck):
        for dp in signal.get("data_points", [])[:2]:
            if dp not in seen_details:
                basis.append({
                    "source": "canonical/20-data/sources/semianalysis/signals.yaml",
                    "detail": dp,
                })
                seen_details.add(dp)
    return basis[:5]  # cap at 5


def _gather_basis_from_company(ticker: str) -> list[dict]:
    """Gather basis entries from company data (thesis_relevance + thesis_signals)."""
    basis = []
    latest = get_latest_company_data(ticker)
    if not latest:
        return []
    source_file = latest.get("_file", f"canonical/20-data/companies/{ticker}/")
    thesis_relevance = latest.get("thesis_relevance", {})
    if thesis_relevance.get("bottleneck_role"):
        basis.append({
            "source": source_file,
            "detail": thesis_relevance["bottleneck_role"][:200],
        })
    if thesis_relevance.get("why_now"):
        basis.append({
            "source": source_file,
            "detail": thesis_relevance["why_now"][:200],
        })
    for signal in latest.get("thesis_signals", []):
        evidence = signal.get("evidence", "").strip()
        if evidence:
            basis.append({
                "source": source_file,
                "detail": evidence[:200],
            })
    return basis[:4]


def _gather_basis_from_wiki(bottleneck: str) -> list[dict]:
    """Gather basis from wiki concept page."""
    wiki_path = get_wiki_concept_for_bottleneck(bottleneck)
    if not wiki_path:
        return []
    return [{
        "source": wiki_path,
        "detail": f"See {wiki_path} for compiled bottleneck analysis",
    }]


def generate_capacity_predictions(ticker: str, bottleneck: str, quarter: str,
                                  ticker_info: dict) -> list[dict]:
    """Generate capacity-related predictions."""
    predictions = []
    status = ticker_info.get("status", "unknown")
    cascade = get_cascade_for_bottleneck(bottleneck)

    # Combine basis from multiple sources
    basis = _gather_basis_from_cascade(bottleneck)
    basis.extend(_gather_basis_from_semianalysis(ticker, bottleneck))
    basis.extend(_gather_basis_from_wiki(bottleneck))

    bn_display = bottleneck.replace("_", " ")

    if status == "active":
        predictions.append(_make_prediction(
            claim=f"{bn_display.title()} utilization remains at or near capacity in {quarter}",
            category="capacity",
            basis=basis[:4] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"{bottleneck} marked as active in cascade"}],
            confidence="high" if len(basis) >= 3 else "medium",
            verify_at=f"{quarter} earnings",
        ))

        # Check if company data mentions capacity expansion
        latest = get_latest_company_data(ticker)
        if latest:
            guidance = latest.get("guidance", {})
            if guidance:
                predictions.append(_make_prediction(
                    claim=f"Management provides update on {bn_display} capacity expansion or timeline",
                    category="capacity",
                    basis=[{"source": latest.get("_file", ""),
                            "detail": "Prior quarter guidance exists — check for capacity expansion updates"}],
                    confidence="medium",
                    verify_at=f"{quarter} earnings",
                ))
    elif status == "next":
        predictions.append(_make_prediction(
            claim=f"{bn_display.title()} begins showing early constraint signals in {quarter}",
            category="capacity",
            basis=basis[:3] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"{bottleneck} marked as next-in-line in cascade"}],
            confidence="low",
            verify_at=f"{quarter} earnings",
        ))
    elif status == "played_out":
        predictions.append(_make_prediction(
            claim=f"{bn_display.title()} capacity is no longer binding — management confirms resolution",
            category="capacity",
            basis=basis[:3] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"{bottleneck} marked as played_out in cascade"}],
            confidence="high",
            verify_at=f"{quarter} earnings",
        ))

    return predictions


def generate_pricing_predictions(ticker: str, bottleneck: str, quarter: str,
                                 ticker_info: dict) -> list[dict]:
    """Generate pricing/margin predictions."""
    predictions = []
    status = ticker_info.get("status", "unknown")
    basis = _gather_basis_from_company(ticker)
    basis.extend(_gather_basis_from_semianalysis(ticker, bottleneck))
    bn_display = bottleneck.replace("_", " ")

    if status == "active":
        predictions.append(_make_prediction(
            claim=f"ASPs/margins remain strong or expand due to {bn_display} constraints",
            category="pricing",
            basis=basis[:4] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"Active bottleneck implies pricing power"}],
            confidence="high" if status == "active" and len(basis) >= 2 else "medium",
            verify_at=f"{quarter} earnings",
        ))
    elif status == "played_out":
        predictions.append(_make_prediction(
            claim=f"Pricing power in {bn_display} segment begins normalizing",
            category="pricing",
            basis=basis[:3] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"Played-out bottleneck implies pricing normalization"}],
            confidence="medium",
            verify_at=f"{quarter} earnings",
        ))

    # Check for margin guidance in company data
    latest = get_latest_company_data(ticker)
    if latest:
        guidance = latest.get("guidance", {})
        forward_claims = latest.get("forward_claims", [])
        margin_claims = [c for c in forward_claims
                         if c.get("status") == "pending"
                         and claim_matches_quarter(c, quarter)
                         and any(kw in c.get("claim", "").lower()
                                 for kw in ("margin", "asp", "pricing", "gross"))]
        for mc in margin_claims[:1]:
            predictions.append(_make_prediction(
                claim=f"Verify prior claim: \"{mc['claim'][:120]}\"",
                category="pricing",
                basis=[{"source": latest.get("_file", ""),
                        "detail": f"Prior forward claim from {mc.get('speaker', 'management')}"}],
                confidence="medium",
                verify_at=f"{quarter} earnings",
            ))

    return predictions


def generate_demand_predictions(ticker: str, bottleneck: str, quarter: str,
                                ticker_info: dict) -> list[dict]:
    """Generate demand-related predictions."""
    predictions = []
    status = ticker_info.get("status", "unknown")
    basis = _gather_basis_from_semianalysis(ticker, bottleneck)
    basis.extend(_gather_basis_from_cascade(bottleneck))
    bn_display = bottleneck.replace("_", " ")

    if status == "active":
        predictions.append(_make_prediction(
            claim=f"Customer demand for {bn_display} products remains elevated or accelerating",
            category="demand",
            basis=basis[:4] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"Active bottleneck implies strong demand"}],
            confidence="high" if len(basis) >= 3 else "medium",
            verify_at=f"{quarter} earnings",
        ))

    # Check for customer concentration or new customer signals
    latest = get_latest_company_data(ticker)
    if latest:
        customers = latest.get("financials", {}).get("customers", {}) or latest.get("customers", {})
        backlog = latest.get("financials", {}).get("backlog", {}) or {}
        if customers or backlog:
            predictions.append(_make_prediction(
                claim=f"Customer concentration or new customer additions provide demand visibility update",
                category="demand",
                basis=[{"source": latest.get("_file", ""),
                        "detail": "Prior quarter had customer/backlog data — watch for changes"}],
                confidence="medium",
                verify_at=f"{quarter} earnings",
            ))

    return predictions


def generate_guidance_predictions(ticker: str, bottleneck: str, quarter: str,
                                  ticker_info: dict) -> list[dict]:
    """Generate guidance-related predictions."""
    predictions = []
    status = ticker_info.get("status", "unknown")
    basis = _gather_basis_from_company(ticker)
    bn_display = bottleneck.replace("_", " ")

    latest = get_latest_company_data(ticker)

    if status == "active":
        confidence = "medium"
        if latest and latest.get("guidance"):
            confidence = "high"
            # Look for specific revenue guidance
            guidance = latest.get("guidance", {})
            for key, val in guidance.items():
                if isinstance(val, dict) and "revenue" in val:
                    rev = val.get("revenue")
                    if rev:
                        predictions.append(_make_prediction(
                            claim=f"Management raises or maintains forward revenue guidance (prior: {key})",
                            category="guidance",
                            basis=[{"source": latest.get("_file", ""),
                                    "detail": f"Prior guidance for {key}: revenue {rev}"}],
                            confidence="high",
                            verify_at=f"{quarter} earnings",
                        ))
                        break

        predictions.append(_make_prediction(
            claim=f"Management provides update on {bn_display} timeline or capacity plans",
            category="guidance",
            basis=basis[:3] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"Active bottleneck — watch for forward commentary"}],
            confidence=confidence,
            verify_at=f"{quarter} earnings",
        ))
    elif status == "next":
        predictions.append(_make_prediction(
            claim=f"Management acknowledges {bn_display} as emerging constraint or investment area",
            category="guidance",
            basis=basis[:3] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"Next-in-line bottleneck — watch for early signals"}],
            confidence="low",
            verify_at=f"{quarter} earnings",
        ))
    else:
        predictions.append(_make_prediction(
            claim=f"Management guides flat or focuses on different growth areas beyond {bn_display}",
            category="guidance",
            basis=basis[:3] if basis else [{"source": "canonical/30-thesis/thesis.yaml",
                                            "detail": f"Played-out bottleneck — expect pivot in narrative"}],
            confidence="medium",
            verify_at=f"{quarter} earnings",
        ))

    # Check for pending forward claims that should be verified this quarter
    forward_claims = get_forward_claims(ticker)
    pending = [
        c for c in forward_claims
        if c.get("status") == "pending" and claim_matches_quarter(c, quarter)
    ]
    for claim in pending[:2]:
        predictions.append(_make_prediction(
            claim=f"Verify forward claim: \"{claim['claim'][:120]}\"",
            category="guidance",
            basis=[{"source": claim.get("source_file", ""),
                    "detail": f"Claim from {claim.get('quarter', 'prior quarter')}: "
                              f"{claim.get('speaker', 'management')}"}],
            confidence="high",
            verify_at=f"{quarter} earnings",
        ))

    return predictions


def generate_margin_predictions(ticker: str, bottleneck: str, quarter: str,
                                ticker_info: dict) -> list[dict]:
    """Generate margin-specific predictions."""
    predictions = []
    latest = get_latest_company_data(ticker)
    if not latest:
        return predictions

    _, q_data = current_quarter_financials(latest)

    # Look for gross margin data
    gm = q_data.get("gross_margin_gaap") or q_data.get("gross_margin_non_gaap")
    ebitda_margin = q_data.get("adjusted_ebitda_margin")

    if gm:
        gm_pct = f"{gm * 100:.1f}%" if isinstance(gm, float) and gm < 1 else str(gm)
        predictions.append(_make_prediction(
            claim=f"Gross margins remain at or above {gm_pct} level from prior quarter",
            category="margins",
            basis=[{"source": latest.get("_file", ""),
                    "detail": f"Prior quarter gross margin: {gm_pct}"}],
            confidence="medium",
            verify_at=f"{quarter} earnings",
        ))
    elif ebitda_margin:
        em_pct = f"{ebitda_margin * 100:.1f}%" if isinstance(ebitda_margin, float) and ebitda_margin < 1 else str(ebitda_margin)
        predictions.append(_make_prediction(
            claim=f"EBITDA margins remain at or above {em_pct} level from prior quarter",
            category="margins",
            basis=[{"source": latest.get("_file", ""),
                    "detail": f"Prior quarter EBITDA margin: {em_pct}"}],
            confidence="medium",
            verify_at=f"{quarter} earnings",
        ))

    # Check for margin-related forward claims
    forward_claims = latest.get("forward_claims", [])
    margin_claims = [c for c in forward_claims
                     if c.get("status") == "pending"
                     and claim_matches_quarter(c, quarter)
                     and any(kw in c.get("claim", "").lower()
                             for kw in ("margin", "ebitda", "operating income", "profitability"))]
    for mc in margin_claims[:1]:
        predictions.append(_make_prediction(
            claim=f"Verify margin claim: \"{mc['claim'][:120]}\"",
            category="margins",
            basis=[{"source": latest.get("_file", ""),
                    "detail": f"Forward claim from {mc.get('speaker', 'management')}"}],
            confidence="medium",
            verify_at=f"{quarter} earnings",
        ))

    return predictions


def generate_positioning_predictions(ticker: str, bottleneck: str, quarter: str,
                                     ticker_info: dict) -> list[dict]:
    """Generate positioning-related predictions."""
    predictions = []

    leopold_pos = get_fund_position_for_ticker(LEOPOLD_DIR, ticker)
    baker_pos = get_fund_position_for_ticker(BAKER_DIR, ticker)
    leopold_exits = get_fund_exits(LEOPOLD_DIR)
    baker_exits = get_fund_exits(BAKER_DIR)

    leopold_exited = any(e.get("ticker") == ticker for e in leopold_exits)
    baker_exited = any(e.get("ticker") == ticker for e in baker_exits)

    basis = []
    if leopold_pos:
        for p in leopold_pos:
            basis.append({
                "source": "canonical/20-data/sources/leopold/",
                "detail": f"Leopold: {p.get('type', 'common')} ${p.get('value', 0):,} "
                          f"({p.get('pct_portfolio', 0)*100:.1f}% of portfolio)",
            })
    elif leopold_exited:
        basis.append({
            "source": "canonical/20-data/sources/leopold/",
            "detail": f"Leopold exited {ticker}",
        })

    if baker_pos:
        for p in baker_pos:
            basis.append({
                "source": "canonical/20-data/sources/baker/",
                "detail": f"Baker: {p.get('type', 'common')} ${p.get('value', 0):,} "
                          f"({p.get('pct_portfolio', 0)*100:.1f}% of portfolio)",
            })
    elif baker_exited:
        basis.append({
            "source": "canonical/20-data/sources/baker/",
            "detail": f"Baker exited {ticker}",
        })

    if basis:
        predictions.append(_make_prediction(
            claim=f"Earnings result reinforces (or challenges) current fund positioning thesis for {ticker}",
            category="positioning",
            basis=basis,
            confidence="medium",
            verify_at=f"{quarter} earnings + next 13F filing",
        ))

    return predictions


# ---------------------------------------------------------------------------
# Positioning context builder
# ---------------------------------------------------------------------------

def build_positioning_context(ticker: str) -> dict:
    """Build the positioning_context section."""
    context: dict[str, Any] = {}

    leopold_pos = get_fund_position_for_ticker(LEOPOLD_DIR, ticker)
    baker_pos = get_fund_position_for_ticker(BAKER_DIR, ticker)
    leopold_exits = get_fund_exits(LEOPOLD_DIR)
    baker_exits = get_fund_exits(BAKER_DIR)
    leopold_exited = any(e.get("ticker") == ticker for e in leopold_exits)
    baker_exited = any(e.get("ticker") == ticker for e in baker_exits)

    # Leopold summary
    if leopold_pos:
        parts = []
        for p in leopold_pos:
            parts.append(f"{p.get('type', 'common')} ${p.get('value', 0):,} "
                         f"({p.get('change_vs_prior', 'n/a')} QoQ)")
        context["leopold"] = f"Holds {ticker}: " + "; ".join(parts)
    elif leopold_exited:
        exit_info = next((e for e in leopold_exits if e.get("ticker") == ticker), {})
        context["leopold"] = (f"Exited {ticker} (prior: {exit_info.get('type', 'unknown')} "
                              f"${exit_info.get('prior_value', 0):,})")
    else:
        context["leopold"] = f"No position in {ticker}"

    # Baker summary
    if baker_pos:
        parts = []
        for p in baker_pos:
            parts.append(f"{p.get('type', 'common')} ${p.get('value', 0):,} "
                         f"({p.get('change_vs_prior', 'n/a')} QoQ)")
        context["baker"] = f"Holds {ticker}: " + "; ".join(parts)
    elif baker_exited:
        exit_info = next((e for e in baker_exits if e.get("ticker") == ticker), {})
        context["baker"] = (f"Exited {ticker} (prior: {exit_info.get('type', 'unknown')} "
                            f"${exit_info.get('prior_value', 0):,})")
    else:
        context["baker"] = f"No position in {ticker}"

    # Implied signal
    both_long = bool(leopold_pos) and bool(baker_pos)
    divergence = bool(leopold_pos) != bool(baker_pos)
    if both_long:
        context["implied_signal"] = f"Both funds positioned in {ticker} — consensus long"
    elif divergence:
        long_fund = "Leopold" if leopold_pos else "Baker"
        absent_fund = "Baker" if leopold_pos else "Leopold"
        context["implied_signal"] = (f"{long_fund} is positioned, {absent_fund} is not "
                                     f"— thesis divergence on {ticker}")
    elif leopold_exited and baker_exited:
        context["implied_signal"] = f"Both funds exited {ticker}"
    else:
        context["implied_signal"] = f"Neither fund has a significant {ticker} position"

    # Check company data for detailed divergence text
    latest = get_latest_company_data(ticker)
    if latest and latest.get("positioning", {}).get("divergence"):
        context["divergence_detail"] = latest["positioning"]["divergence"].strip()

    return context


# ---------------------------------------------------------------------------
# Core prediction assembly
# ---------------------------------------------------------------------------

CATEGORY_GENERATORS = {
    "capacity": generate_capacity_predictions,
    "pricing": generate_pricing_predictions,
    "demand": generate_demand_predictions,
    "margins": generate_margin_predictions,
    "guidance": generate_guidance_predictions,
    "positioning": generate_positioning_predictions,
}


def generate_predictions(ticker: str, quarter: str, today: date) -> dict:
    """Generate the full predictions document for a ticker + quarter."""
    ticker_map = get_ticker_map()
    ticker_info = ticker_map.get(ticker, {})
    bottleneck = ticker_info.get("bottleneck", "unknown")
    bn_status = ticker_info.get("status", "unknown")
    earnings_date = ticker_info.get("next_earnings", "unknown")

    # Assemble predictions from all category generators
    all_predictions = []
    config = get_agent_config()
    categories = config.get("predictions", {}).get("categories",
                    ["capacity", "pricing", "demand", "margins", "guidance", "positioning"])

    for category in categories:
        generator = CATEGORY_GENERATORS.get(category)
        if generator:
            preds = generator(ticker, bottleneck, quarter, ticker_info)
            all_predictions.extend(preds)

    # Build positioning context
    positioning_context = build_positioning_context(ticker)

    # Calculate track record
    track_record = calculate_track_record(ticker)

    # Assemble the full document
    quarter_display = quarter.replace("_", " ")
    doc = {
        "ticker": ticker,
        "quarter": quarter_display,
        "predicted_at": today.isoformat(),
        "earnings_date": str(earnings_date),
        "bottleneck": bottleneck,
        "bottleneck_status": bn_status,
        "predictions": all_predictions,
        "positioning_context": positioning_context,
        "track_record": track_record,
    }

    return doc


# ---------------------------------------------------------------------------
# Upcoming earnings scanner
# ---------------------------------------------------------------------------

def find_upcoming_tickers(days: int, today: date) -> list[dict]:
    """Find tickers with earnings within N days."""
    ticker_map = get_ticker_map()
    upcoming = []
    cutoff = today + timedelta(days=days)

    for ticker, info in ticker_map.items():
        earnings_str = info.get("next_earnings")
        if not earnings_str:
            continue
        try:
            earnings_date = datetime.strptime(str(earnings_str), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if today <= earnings_date <= cutoff:
            upcoming.append({
                "ticker": ticker,
                "earnings_date": earnings_date,
                "days_until": (earnings_date - today).days,
            })

    upcoming.sort(key=lambda x: (x["earnings_date"], x["ticker"]))
    return upcoming


def quarter_from_date(earnings_date: date) -> str:
    """Infer quarter label from an earnings date.

    Earnings typically report the prior quarter, so:
    - Jan-Mar earnings -> Q4 of prior year or Q1 current
    - Apr-Jun earnings -> Q1 current year
    - Jul-Sep earnings -> Q2 current year
    - Oct-Dec earnings -> Q3 current year

    This is approximate — the actual quarter depends on the company's fiscal year.
    We use a simple mapping and the user can override with --quarter.
    """
    month = earnings_date.month
    year = earnings_date.year
    if month <= 3:
        return f"Q4 {year - 1}"
    elif month <= 6:
        return f"Q1 {year}"
    elif month <= 9:
        return f"Q2 {year}"
    else:
        return f"Q3 {year}"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def write_log(today: date, tickers_processed: list[str],
              files_written: list[str], error: str | None = None) -> None:
    """Append a run entry to agents/logs/."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"pre-earnings-predictor-{today.strftime('%Y-%m')}.log"

    timestamp = datetime.now().isoformat(timespec="seconds")
    entry_lines = [
        f"[{timestamp}] pre_earnings_predictor",
        f"  tickers: {', '.join(tickers_processed) if tickers_processed else 'none'}",
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
    global RUNTIME_AS_OF_DATE

    parser = argparse.ArgumentParser(
        description="Pre-earnings prediction generator. Reads the knowledge graph "
                    "and generates testable predictions for upcoming earnings.")
    parser.add_argument("--ticker", type=str, help="Ticker symbol (e.g. TSM)")
    parser.add_argument("--quarter", type=str,
                        help="Quarter label (e.g. Q1_2026). Auto-inferred if omitted.")
    parser.add_argument("--all-upcoming", action="store_true",
                        help="Generate predictions for all tickers with earnings in the next 7 days")
    parser.add_argument("--days", type=int, default=7,
                        help="Lookahead window for --all-upcoming (default: 7)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print YAML to stdout without writing files")
    parser.add_argument("--date", type=str, default=None,
                        help="Override today's date (YYYY-MM-DD) and filter dated inputs as-of that day")
    args = parser.parse_args()

    if not args.ticker and not args.all_upcoming:
        parser.error("Provide --ticker or --all-upcoming")

    # Determine today
    if args.date:
        today = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        today = date.today()
    RUNTIME_AS_OF_DATE = today

    # Validate the canonical thesis file is loadable
    thesis = get_thesis()
    if not thesis:
        print("ERROR: Could not load canonical/30-thesis/thesis.yaml", file=sys.stderr)
        write_log(today, [], [], error="canonical thesis not found or empty")
        sys.exit(1)

    # Determine which tickers to process
    targets: list[tuple[str, str]] = []  # (ticker, quarter)

    if args.all_upcoming:
        upcoming = find_upcoming_tickers(args.days, today)
        if not upcoming:
            print(f"No tickers with earnings in the next {args.days} days.", file=sys.stderr)
            write_log(today, [], [], error=f"No upcoming earnings within {args.days} days")
            sys.exit(0)
        for entry in upcoming:
            latest = get_latest_company_data(entry["ticker"])
            quarter = next_quarter_label((latest or {}).get("quarter")) or quarter_from_date(entry["earnings_date"])
            targets.append((entry["ticker"], quarter))
        print(f"Found {len(targets)} ticker(s) with earnings in next {args.days} days: "
              f"{', '.join(t[0] for t in targets)}")
    else:
        ticker = args.ticker.upper()
        ticker_map = get_ticker_map()
        if ticker not in ticker_map:
            print(f"WARNING: {ticker} not found in canonical thesis ticker_map. "
                  f"Generating with limited data.", file=sys.stderr)

        if args.quarter:
            quarter = normalize_quarter_label(args.quarter)
        else:
            # Infer quarter from next_earnings date
            latest = get_latest_company_data(ticker)
            quarter = next_quarter_label((latest or {}).get("quarter"))
            if not quarter:
                info = ticker_map.get(ticker, {})
                earnings_str = info.get("next_earnings")
                if earnings_str:
                    try:
                        ed = datetime.strptime(str(earnings_str), "%Y-%m-%d").date()
                        quarter = quarter_from_date(ed)
                    except (ValueError, TypeError):
                        quarter = f"Q1 {today.year}"
                else:
                    quarter = f"Q1 {today.year}"
        targets.append((ticker, quarter))

    # Generate predictions
    tickers_processed = []
    files_written = []

    for ticker, quarter in targets:
        print(f"\nGenerating predictions for {ticker} ({quarter.replace('_', ' ')})...")

        doc = generate_predictions(ticker, quarter, today)

        if args.dry_run:
            print("---")
            print(yaml.dump(doc, default_flow_style=False, sort_keys=False,
                            allow_unicode=True, width=120))
        else:
            PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
            quarter_slug = quarter.replace(" ", "_")
            out_path = PREDICTIONS_DIR / f"{ticker}-{quarter_slug}.yaml"
            dump_yaml(doc, out_path)
            rel_path = display_path(out_path)
            files_written.append(rel_path)
            print(f"  Written to {rel_path}")

            pred_count = len(doc.get("predictions", []))
            print(f"  Predictions: {pred_count}")
            for p in doc.get("predictions", []):
                conf = p.get("confidence", "?")
                cat = p.get("category", "?")
                print(f"    [{conf:>6}] [{cat}] {p['claim'][:80]}")

        tickers_processed.append(ticker)

    write_log(today, tickers_processed, files_written)

    if not args.dry_run and files_written:
        print(f"\nDone. {len(files_written)} prediction file(s) written.")
        print("Next step: review and refine predictions before earnings.")


if __name__ == "__main__":
    main()
