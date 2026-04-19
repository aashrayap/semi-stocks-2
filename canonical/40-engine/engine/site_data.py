"""Build the schema-first site-data contract for the semi-stocks reader."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from engine.paths import DATA_DIR, REPO_ROOT, REPORTS_DIR, SITE_DATA_DIR, THESIS_PATH, WIKI_DIR
from engine.synthesis import (
    agreement_map,
    baker_hedge_ratio,
    cascade_status,
    concept_drift,
    cycle_assessment,
    divergences,
    earnings_dashboard,
    forward_claims_due,
    generate_summary,
    get_sources,
    load_thesis,
)

GENERATOR_VERSION = "site-data-v0.1"
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
TICKER_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")
EDGE_TYPES = {
    "links_to",
    "mentions_ticker",
    "derived_from_source",
    "supports_claim",
    "contradicts_claim",
    "exposes_company_to",
    "belongs_to_bottleneck",
    "updates_thesis_stage",
    "published_in_report",
}


def build_site_data(validate: bool = False) -> dict[str, int]:
    """Build canonical/site-data and optionally validate the generated contract."""
    artifacts = _collect_artifacts()
    if SITE_DATA_DIR.exists():
        shutil.rmtree(SITE_DATA_DIR)
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name in (
        "build",
        "schema",
        "pages",
        "companies",
        "signals",
        "entities",
        "edges",
        "claims",
        "thesis",
        "reports",
        "search",
        "graph",
    ):
        _write_json(SITE_DATA_DIR / f"{name}.json", artifacts[name])

    if validate:
        validate_site_data(artifacts)

    return {
        "pages": len(artifacts["pages"]),
        "companies": len(artifacts["companies"]),
        "signals": len(artifacts["signals"]),
        "claims": len(artifacts["claims"]),
        "edges": len(artifacts["edges"]),
    }


def validate_site_data(artifacts: dict[str, Any]) -> None:
    """Validate generated artifacts without requiring a third-party schema package."""
    required = {
        "build",
        "schema",
        "pages",
        "companies",
        "signals",
        "entities",
        "edges",
        "claims",
        "thesis",
        "reports",
        "search",
        "graph",
    }
    missing = required - set(artifacts)
    if missing:
        raise ValueError(f"Missing artifacts: {', '.join(sorted(missing))}")

    id_sets = {
        "pages": _ids_for(artifacts["pages"], "pages"),
        "companies": _ids_for(artifacts["companies"], "companies"),
        "signals": _ids_for(artifacts["signals"], "signals"),
        "entities": _ids_for(artifacts["entities"], "entities"),
        "claims": _ids_for(artifacts["claims"], "claims"),
        "reports": _ids_for(artifacts["reports"], "reports"),
    }
    thesis_stage_ids = {
        stage["id"] for stage in artifacts["thesis"].get("cascade", []) if stage.get("id")
    }
    known_ids = set().union(*id_sets.values(), thesis_stage_ids, {"thesis:current"})

    for edge in artifacts["edges"]:
        edge_id = edge.get("id")
        source = edge.get("source")
        target = edge.get("target")
        edge_type = edge.get("type")
        if not edge_id or not source or not target:
            raise ValueError(f"Malformed edge: {edge}")
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"Unknown edge type {edge_type!r} in {edge_id}")
        if source not in known_ids:
            raise ValueError(f"Unknown edge source {source!r} in {edge_id}")
        if target not in known_ids:
            raise ValueError(f"Unknown edge target {target!r} in {edge_id}")

    required_nonempty = (
        ("pages", artifacts["pages"]),
        ("companies", artifacts["companies"]),
        ("signals", artifacts["signals"]),
        ("entities", artifacts["entities"]),
        ("edges", artifacts["edges"]),
        ("claims", artifacts["claims"]),
        ("reports", artifacts["reports"]),
        ("search", artifacts["search"]),
        ("graph.nodes", artifacts["graph"].get("nodes", [])),
        ("graph.links", artifacts["graph"].get("links", [])),
    )
    empty = [name for name, value in required_nonempty if not value]
    if empty:
        raise ValueError(f"Expected non-empty artifacts: {', '.join(empty)}")

    edge_ids = [edge["id"] for edge in artifacts["edges"]]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("Duplicate edge IDs")

    for company in artifacts["companies"]:
        if not company.get("ticker") or not company.get("name"):
            raise ValueError(f"Company missing ticker/name: {company.get('id')}")

    for signal in artifacts["signals"]:
        if not signal.get("kind") or not signal.get("evidence"):
            raise ValueError(f"Signal missing kind/evidence: {signal.get('id')}")

    graph_node_ids = {node.get("id") for node in artifacts["graph"].get("nodes", [])}
    for link in artifacts["graph"].get("links", []):
        if link.get("source") not in graph_node_ids or link.get("target") not in graph_node_ids:
            raise ValueError(f"Graph link endpoint missing from graph nodes: {link}")


def _collect_artifacts() -> dict[str, Any]:
    thesis = load_thesis()
    page_index = _build_pages()
    company_packets = _load_company_packets()
    thesis_proposals = _load_thesis_proposals()

    companies = _build_companies(thesis, company_packets)
    claims = _build_claims(company_packets)
    signals = _build_signals(thesis, company_packets, thesis_proposals)
    reports = _build_reports()
    entities = _build_entities(page_index["pages"], companies, reports, thesis, signals)
    edges = _build_edges(page_index, companies, signals, claims, reports, thesis, entities)
    thesis_payload = _build_thesis(thesis, thesis_proposals)
    search = _build_search(page_index["pages"], companies, signals, claims, reports, thesis_payload)
    graph = _build_graph(page_index["pages"], entities, edges)
    schema = _schema()
    build = _build_manifest(
        page_index["pages"],
        companies,
        signals,
        claims,
        entities,
        edges,
        reports,
        thesis_payload,
    )

    return {
        "build": build,
        "schema": schema,
        "pages": page_index["pages"],
        "companies": companies,
        "signals": signals,
        "entities": entities,
        "edges": edges,
        "claims": claims,
        "thesis": thesis_payload,
        "reports": reports,
        "search": search,
        "graph": graph,
    }


def _build_pages() -> dict[str, Any]:
    by_slug: dict[str, Path] = {}
    roots = (
        WIKI_DIR / "concepts",
        WIKI_DIR / "sources",
        WIKI_DIR / "outputs",
        WIKI_DIR,
        WIKI_DIR / "raw",
    )
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            if any(part.startswith(".") for part in path.parts):
                continue
            slug = _slugify(path.stem)
            by_slug.setdefault(slug, path)

    pages: list[dict[str, Any]] = []
    for slug, path in sorted(by_slug.items(), key=lambda item: _path_sort_key(item[1])):
        source = path.read_text(encoding="utf-8")
        frontmatter, markdown = _split_frontmatter(source)
        title = str(frontmatter.get("title") or _extract_h1(markdown) or _titleize(slug))
        body = _strip_leading_h1(markdown).strip()
        plain = _plain_text(markdown)
        page_type = _page_type(path)
        out_slugs = [
            target for target in _extract_outgoing_slugs(body) if target in by_slug and target != slug
        ]
        pages.append({
            "id": _page_id(slug),
            "slug": slug,
            "title": title,
            "type": page_type,
            "path": _rel(path),
            "href": f"{slug}.html",
            "tags": sorted(str(tag) for tag in frontmatter.get("tags", []) or []),
            "sources": [str(item) for item in frontmatter.get("sources", []) or []],
            "created": _string_or_none(frontmatter.get("created")),
            "updated": _string_or_none(frontmatter.get("updated")),
            "summary": _clip(plain, 360),
            "body_markdown": body,
            "word_count": len(plain.split()),
            "outlinks": [_page_id(target) for target in out_slugs],
            "backlinks": [],
        })

    page_by_id = {page["id"]: page for page in pages}
    for page in pages:
        for target_id in page["outlinks"]:
            if target_id in page_by_id:
                page_by_id[target_id]["backlinks"].append(page["id"])
    for page in pages:
        page["backlinks"] = sorted(set(page["backlinks"]))

    return {"pages": pages, "slug_to_id": {page["slug"]: page["id"] for page in pages}}


def _build_companies(thesis: dict[str, Any], company_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    leopold, baker, semi = get_sources()
    ticker_map = thesis.get("ticker_map", {}) or {}
    dashboard_by_ticker = {row["ticker"]: row for row in earnings_dashboard()}
    packets_by_ticker: dict[str, list[dict[str, Any]]] = {}
    for packet in company_packets:
        ticker = str(packet.get("ticker", "")).upper()
        if ticker:
            packets_by_ticker.setdefault(ticker, []).append(packet)

    tickers = set(ticker_map)
    tickers.update(packets_by_ticker)
    tickers.update(leopold.tickers())
    tickers.update(baker.tickers())
    tickers.update(semi.tickers())

    companies: list[dict[str, Any]] = []
    for ticker in sorted(tickers):
        packets = sorted(packets_by_ticker.get(ticker, []), key=lambda p: str(p.get("_file", "")))
        latest_packet = packets[-1] if packets else {}
        positions = []
        for source in (leopold, baker):
            position = source.lookup(ticker)
            if position:
                positions.append({
                    "source": source.name(),
                    "value": position.get("value"),
                    "pct_portfolio": position.get("pct_portfolio"),
                    "type": position.get("type"),
                    "change_vs_prior": position.get("change_vs_prior"),
                    "notes": position.get("notes", ""),
                })
        meta = ticker_map.get(ticker, {}) or {}
        dashboard = dashboard_by_ticker.get(ticker, {})
        source_page = latest_packet.get("source_page") or dashboard.get("source_page")
        companies.append({
            "id": _company_id(ticker),
            "ticker": ticker,
            "name": (
                latest_packet.get("company")
                or _first_position_company(ticker, leopold, baker)
                or ticker
            ),
            "bottleneck": meta.get("bottleneck") or dashboard.get("bottleneck"),
            "status": meta.get("status") or dashboard.get("bottleneck_status"),
            "also": meta.get("also"),
            "next_earnings": meta.get("next_earnings") or dashboard.get("next_earnings"),
            "source_page": _source_page_slug(source_page),
            "latest_packet": _rel_from_string(latest_packet.get("_file")),
            "quarters": [
                {
                    "quarter": packet.get("quarter"),
                    "period": _string_or_none(packet.get("period")),
                    "path": _rel_from_string(packet.get("_file")),
                }
                for packet in packets
            ],
            "positions": positions,
            "signal_counts": {
                "confirms": dashboard.get("signals_confirms", 0),
                "contradicts": dashboard.get("signals_contradicts", 0),
                "semi": len((semi.lookup(ticker) or {}).get("signals", [])),
            },
            "claim_counts": {
                "pending": dashboard.get("claims_pending", 0),
                "confirmed": dashboard.get("claims_confirmed", 0),
                "missed": dashboard.get("claims_missed", 0),
                "due_next": dashboard.get("claims_due_next", 0),
            },
            "metrics": {
                "quarter": dashboard.get("quarter"),
                "revenue_label": dashboard.get("revenue_label"),
                "revenue_value": dashboard.get("revenue_value"),
                "margin_label": dashboard.get("margin_label"),
                "margin_value": dashboard.get("margin_value"),
                "guidance_period": dashboard.get("guidance_period"),
                "guidance": dashboard.get("guidance"),
            },
            "thesis": {
                "bottleneck_role": dashboard.get("bottleneck_role") or latest_packet.get("thesis_relevance", {}).get("bottleneck_role", ""),
                "why_now": dashboard.get("why_now") or latest_packet.get("thesis_relevance", {}).get("why_now", ""),
                "confirms_next": dashboard.get("confirms_next", []),
                "break_conditions": dashboard.get("break_conditions", []),
            },
        })
    return companies


def _build_claims(company_packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for packet in sorted(company_packets, key=lambda p: str(p.get("_file", ""))):
        ticker = str(packet.get("ticker", "")).upper()
        quarter = str(packet.get("quarter", "unknown"))
        source_page = _source_page_slug(packet.get("source_page"))
        for index, claim in enumerate(packet.get("forward_claims", []) or [], start=1):
            claim_id = f"claim:{ticker}:{_slugify(quarter)}:{index:02d}"
            claims.append({
                "id": claim_id,
                "ticker": ticker,
                "company_id": _company_id(ticker),
                "quarter": quarter,
                "claim": str(claim.get("claim", "")).strip(),
                "speaker": claim.get("speaker", ""),
                "source": claim.get("source", ""),
                "source_ref": claim.get("source_ref", ""),
                "source_page": source_page,
                "verify_at": claim.get("verify_at", ""),
                "verify_window": claim.get("verify_window", {}),
                "status": claim.get("status", "pending"),
                "notes": claim.get("notes", ""),
            })
    return claims


def _build_signals(
    thesis: dict[str, Any],
    company_packets: list[dict[str, Any]],
    thesis_proposals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []

    for packet in sorted(company_packets, key=lambda p: str(p.get("_file", ""))):
        ticker = str(packet.get("ticker", "")).upper()
        quarter = str(packet.get("quarter", "unknown"))
        source_page = _source_page_slug(packet.get("source_page"))
        for index, signal in enumerate(packet.get("thesis_signals", []) or [], start=1):
            bottleneck = signal.get("bottleneck", "")
            signals.append({
                "id": f"signal:company:{ticker}:{_slugify(quarter)}:{index:02d}",
                "kind": "company_thesis_signal",
                "ticker": ticker,
                "company_id": _company_id(ticker),
                "quarter": quarter,
                "bottleneck": bottleneck,
                "bottleneck_id": _bottleneck_id(bottleneck),
                "direction": signal.get("direction", ""),
                "evidence": _clean(signal.get("evidence", "")),
                "source_ref": signal.get("source_ref", ""),
                "source_page": source_page,
                "source_path": _rel_from_string(packet.get("_file")),
            })

    semi_path = DATA_DIR / "sources" / "semianalysis" / "signals.yaml"
    semi_data = _read_yaml(semi_path)
    for index, signal in enumerate(semi_data.get("signals", []) or [], start=1):
        signal_id = f"signal:semianalysis:{_slugify(signal.get('date', 'undated'))}:{index:02d}"
        data_points = [str(item) for item in signal.get("data_points", []) or []]
        signals.append({
            "id": signal_id,
            "kind": "semianalysis_signal",
            "date": _string_or_none(signal.get("date")),
            "title": signal.get("title", ""),
            "tickers": [str(t).upper() for t in signal.get("tickers", []) or []],
            "bottleneck": signal.get("bottleneck", ""),
            "bottleneck_id": _bottleneck_id(signal.get("bottleneck", "")),
            "direction": "signal",
            "evidence": "; ".join(data_points),
            "data_points": data_points,
            "source": semi_data.get("entity", "SemiAnalysis"),
            "source_path": _rel(semi_path),
        })

    for stage_index, stage in enumerate(thesis.get("cascade", []) or [], start=1):
        stage_id = _thesis_stage_id(stage.get("name", f"stage-{stage_index}"))
        for signal_index, text in enumerate(stage.get("signals", []) or [], start=1):
            signals.append({
                "id": f"signal:thesis:{_slugify(stage.get('name', 'stage'))}:{signal_index:02d}",
                "kind": "thesis_stage_signal",
                "stage_id": stage_id,
                "bottleneck": stage.get("name", ""),
                "bottleneck_id": _bottleneck_id(stage.get("name", "")),
                "direction": "supports",
                "evidence": _clean(text),
                "source_path": _rel(THESIS_PATH),
            })

    for proposal in thesis_proposals:
        evidence = proposal.get("evidence", []) or []
        if not evidence:
            continue
        for index, item in enumerate(evidence, start=1):
            signals.append({
                "id": f"signal:proposal:{proposal['_slug']}:{index:02d}",
                "kind": "thesis_proposal_signal",
                "proposal_id": f"proposal:{proposal['_slug']}",
                "status": proposal.get("status", "pending"),
                "direction": "proposed",
                "evidence": _clean(item.get("signal", "")),
                "source": item.get("source", ""),
                "date": _string_or_none(item.get("date")),
                "source_path": proposal["_file"],
            })

    return sorted(signals, key=lambda item: item["id"])


def _build_thesis(thesis: dict[str, Any], thesis_proposals: list[dict[str, Any]]) -> dict[str, Any]:
    cycle_by_name = {row["name"]: row for row in cycle_assessment()}
    cascade = []
    for stage in thesis.get("cascade", []) or []:
        name = stage.get("name", "")
        cycle = cycle_by_name.get(name, {})
        cascade.append({
            "id": _thesis_stage_id(name),
            "name": name,
            "status": stage.get("status"),
            "period": stage.get("period"),
            "cycle_phase": stage.get("cycle_phase"),
            "cycle_action": cycle.get("cycle_action"),
            "cycle_risk": cycle.get("cycle_risk"),
            "cycle_signal": stage.get("cycle_signal", ""),
            "cycle_risk_flags": stage.get("cycle_risk_flags", []),
            "tickers": [str(t).upper() for t in stage.get("tickers", []) or []],
            "company_ids": [_company_id(str(t).upper()) for t in stage.get("tickers", []) or []],
            "signals": stage.get("signals", []),
            "notes": stage.get("notes", ""),
        })

    return {
        "id": "thesis:current",
        "updated": _string_or_none(thesis.get("updated")),
        "path": _rel(THESIS_PATH),
        "baker_hedge_ratio": baker_hedge_ratio(),
        "cascade": cascade,
        "ticker_map": {
            ticker: {
                **(meta or {}),
                "company_id": _company_id(ticker),
            }
            for ticker, meta in sorted((thesis.get("ticker_map", {}) or {}).items())
        },
        "proposals": [
            {
                "id": f"proposal:{proposal['_slug']}",
                "status": proposal.get("status"),
                "created": _string_or_none(proposal.get("created")),
                "updated": _string_or_none(proposal.get("updated")),
                "proposal": _clean(proposal.get("proposal", "")),
                "target_sections": proposal.get("target_sections", []),
                "path": proposal["_file"],
            }
            for proposal in thesis_proposals
        ],
    }


def _build_reports() -> list[dict[str, Any]]:
    cascade = cascade_status()
    agreements = agreement_map()
    divs = divergences()
    dashboard = earnings_dashboard()
    drift = concept_drift()
    latest = REPORTS_DIR / "latest.html"
    sections = [
        {
            "id": "report-section:latest:summary",
            "title": "Summary",
            "kind": "summary",
            "body_html": generate_summary(cascade, agreements, divs),
        },
        {
            "id": "report-section:latest:cascade-cycle-risk",
            "title": "Cascade + Cycle Risk",
            "kind": "table",
            "rows": cycle_assessment(),
        },
        {
            "id": "report-section:latest:positions-signals",
            "title": "Positions + Signals",
            "kind": "table",
            "rows": agreements,
        },
        {
            "id": "report-section:latest:earnings-proof-gates",
            "title": "Earnings + Proof Gates",
            "kind": "table",
            "rows": dashboard,
        },
        {
            "id": "report-section:latest:drift",
            "title": "Drift Warnings",
            "kind": "table",
            "rows": drift,
        },
    ]
    return [{
        "id": "report:latest",
        "title": "semi-stocks latest report",
        "path": _rel(latest),
        "exists": latest.exists(),
        "size_bytes": latest.stat().st_size if latest.exists() else 0,
        "source": "canonical/40-engine/engine/report.py",
        "sections": sections,
    }]


def _build_entities(
    pages: list[dict[str, Any]],
    companies: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    thesis: dict[str, Any],
    signals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    entities: dict[str, dict[str, Any]] = {}

    def put(entity: dict[str, Any]) -> None:
        entities.setdefault(entity["id"], entity)

    for page in pages:
        if page["type"] in {"concept", "source", "output"}:
            put({
                "id": _entity_id(page["type"], page["slug"]),
                "type": page["type"],
                "label": page["title"],
                "page_id": page["id"],
                "slug": page["slug"],
            })

    for company in companies:
        put({
            "id": company["id"],
            "type": "company",
            "label": company["name"],
            "ticker": company["ticker"],
            "bottleneck": company.get("bottleneck"),
            "status": company.get("status"),
        })

    for report in reports:
        put({
            "id": report["id"],
            "type": "report",
            "label": report["title"],
            "path": report["path"],
        })

    put({"id": "thesis:current", "type": "thesis", "label": "Current thesis"})
    for stage in thesis.get("cascade", []) or []:
        put({
            "id": _thesis_stage_id(stage.get("name", "")),
            "type": "thesis_stage",
            "label": stage.get("name", ""),
            "status": stage.get("status"),
        })
        put({
            "id": _bottleneck_id(stage.get("name", "")),
            "type": "bottleneck",
            "label": stage.get("name", ""),
            "status": stage.get("status"),
        })

    for meta in (thesis.get("ticker_map", {}) or {}).values():
        for key in ("bottleneck", "also"):
            value = meta.get(key)
            if value:
                put({
                    "id": _bottleneck_id(value),
                    "type": "bottleneck",
                    "label": _titleize(str(value)),
                })

    for signal in signals:
        bottleneck_id = signal.get("bottleneck_id")
        if bottleneck_id:
            put({
                "id": bottleneck_id,
                "type": "bottleneck",
                "label": _titleize(str(signal.get("bottleneck", "") or bottleneck_id.split(":", 1)[1])),
            })
        source = signal.get("source")
        if source:
            put({
                "id": _entity_id("source", str(source)),
                "type": "source",
                "label": str(source),
            })

    for source_file in sorted((DATA_DIR / "sources").rglob("*.yaml")):
        data = _read_yaml(source_file)
        label = data.get("entity") or source_file.parent.name
        put({
            "id": _entity_id("source", label),
            "type": "source",
            "label": label,
            "path": _rel(source_file),
        })

    return sorted(entities.values(), key=lambda item: (item["type"], item["id"]))


def _build_edges(
    page_index: dict[str, Any],
    companies: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    thesis: dict[str, Any],
    entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pages = page_index["pages"]
    slug_to_id = page_index["slug_to_id"]
    entity_ids = {entity["id"] for entity in entities}
    company_ids = {company["id"] for company in companies}
    signal_ids = {signal["id"] for signal in signals}
    claim_ids = {claim["id"] for claim in claims}
    report_ids = {report["id"] for report in reports}
    stage_ids = {_thesis_stage_id(stage.get("name", "")) for stage in thesis.get("cascade", []) or []}
    known_ids = (
        {page["id"] for page in pages}
        | entity_ids
        | company_ids
        | signal_ids
        | claim_ids
        | report_ids
        | stage_ids
        | {"thesis:current"}
    )
    company_by_ticker = {company["ticker"]: company for company in companies}

    edges: dict[str, dict[str, Any]] = {}

    def add(edge_type: str, source: str, target: str, **meta: Any) -> None:
        if source not in known_ids or target not in known_ids:
            return
        key = f"{edge_type}:{source}->{target}"
        edges.setdefault(key, {
            "id": f"edge:{len(edges) + 1:05d}",
            "type": edge_type,
            "source": source,
            "target": target,
            **{k: v for k, v in meta.items() if v not in (None, "", [])},
        })

    for page in pages:
        for target in page.get("outlinks", []):
            add("links_to", page["id"], target)
        tickers = sorted(set(TICKER_RE.findall(page.get("body_markdown", ""))))
        for ticker in tickers:
            company = company_by_ticker.get(ticker)
            if company:
                add("mentions_ticker", page["id"], company["id"], ticker=ticker)

    for company in companies:
        bottleneck = company.get("bottleneck")
        if bottleneck:
            add("exposes_company_to", company["id"], _bottleneck_id(bottleneck), ticker=company["ticker"])
        source_slug = company.get("source_page")
        if source_slug:
            add("derived_from_source", company["id"], _page_id(source_slug), ticker=company["ticker"])
        add("published_in_report", company["id"], "report:latest", ticker=company["ticker"])

    stage_by_bottleneck = {
        stage.get("name"): _thesis_stage_id(stage.get("name", ""))
        for stage in thesis.get("cascade", []) or []
    }
    stage_by_ticker = {}
    for stage in thesis.get("cascade", []) or []:
        stage_id = _thesis_stage_id(stage.get("name", ""))
        for ticker in stage.get("tickers", []) or []:
            stage_by_ticker[str(ticker).upper()] = stage_id
        add("belongs_to_bottleneck", stage_id, _bottleneck_id(stage.get("name", "")))

    for signal in signals:
        signal_id = signal["id"]
        for ticker in signal.get("tickers", []) or []:
            company = company_by_ticker.get(str(ticker).upper())
            if company:
                add("supports_claim", signal_id, company["id"], ticker=company["ticker"])
                if company.get("bottleneck"):
                    add("exposes_company_to", company["id"], _bottleneck_id(company["bottleneck"]))
        ticker = signal.get("ticker")
        if ticker and ticker in company_by_ticker:
            company = company_by_ticker[ticker]
            add("supports_claim", signal_id, company["id"], ticker=ticker)
            if signal.get("direction") == "contradicts":
                add("contradicts_claim", signal_id, company["id"], ticker=ticker)
            source_page = signal.get("source_page")
            if source_page:
                add("derived_from_source", signal_id, _page_id(source_page))
        bottleneck_id = signal.get("bottleneck_id")
        if bottleneck_id:
            add("updates_thesis_stage", signal_id, bottleneck_id)
        stage_id = signal.get("stage_id") or stage_by_ticker.get(str(ticker or "").upper())
        if stage_id:
            add("updates_thesis_stage", signal_id, stage_id)
        source = signal.get("source")
        if source:
            add("derived_from_source", signal_id, _entity_id("source", str(source)))

    for claim in claims:
        claim_id = claim["id"]
        company_id = claim.get("company_id")
        if company_id:
            add("supports_claim", company_id, claim_id, ticker=claim.get("ticker"))
        source_page = claim.get("source_page")
        if source_page:
            add("derived_from_source", claim_id, _page_id(source_page))

    for report in reports:
        add("published_in_report", "thesis:current", report["id"])
        for section in report.get("sections", []):
            if section.get("title") == "Positions + Signals":
                for row in section.get("rows", []):
                    ticker = row.get("ticker")
                    company = company_by_ticker.get(str(ticker or "").upper())
                    if company:
                        add("published_in_report", company["id"], report["id"], ticker=company["ticker"])

    return sorted(edges.values(), key=lambda edge: edge["id"])


def _build_search(
    pages: list[dict[str, Any]],
    companies: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    thesis: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for page in pages:
        rows.append({
            "id": page["id"],
            "type": f"page:{page['type']}",
            "title": page["title"],
            "text": _clip(f"{page['summary']} {page.get('body_markdown', '')}", 900),
            "href": page["href"],
        })
    for company in companies:
        rows.append({
            "id": company["id"],
            "type": "company",
            "title": f"{company['ticker']} - {company['name']}",
            "text": _clip(" ".join([
                str(company.get("bottleneck") or ""),
                str(company.get("status") or ""),
                company.get("thesis", {}).get("why_now", ""),
            ]), 900),
            "href": company.get("source_page"),
        })
    for signal in signals:
        rows.append({
            "id": signal["id"],
            "type": "signal",
            "title": signal.get("title") or signal.get("ticker") or signal.get("kind"),
            "text": _clip(signal.get("evidence", ""), 900),
            "href": signal.get("source_page"),
        })
    for claim in claims:
        rows.append({
            "id": claim["id"],
            "type": "claim",
            "title": f"{claim.get('ticker')} claim",
            "text": _clip(f"{claim.get('claim', '')} {claim.get('notes', '')}", 900),
            "href": claim.get("source_page"),
        })
    for report in reports:
        rows.append({
            "id": report["id"],
            "type": "report",
            "title": report["title"],
            "text": " ".join(section["title"] for section in report.get("sections", [])),
            "href": report["path"],
        })
    for stage in thesis.get("cascade", []):
        rows.append({
            "id": stage["id"],
            "type": "thesis_stage",
            "title": stage["name"],
            "text": _clip(" ".join(stage.get("signals", [])) + " " + stage.get("cycle_signal", ""), 900),
            "href": "",
        })
    return sorted(rows, key=lambda row: (row["type"], row["title"], row["id"]))


def _build_graph(
    pages: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    for page in pages:
        nodes[page["id"]] = {
            "id": page["id"],
            "label": page["title"],
            "type": f"page:{page['type']}",
            "href": page["href"],
        }
    for entity in entities:
        nodes.setdefault(entity["id"], {
            "id": entity["id"],
            "label": entity.get("label", entity["id"]),
            "type": entity.get("type", "entity"),
        })

    links = [
        {
            "source": edge["source"],
            "target": edge["target"],
            "type": edge["type"],
        }
        for edge in edges
        if edge["source"] in nodes and edge["target"] in nodes
    ]

    degree: dict[str, int] = {}
    for link in links:
        degree[link["source"]] = degree.get(link["source"], 0) + 1
        degree[link["target"]] = degree.get(link["target"], 0) + 1
    for node in nodes.values():
        node["val"] = 1 + degree.get(node["id"], 0)

    return {
        "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
        "links": sorted(links, key=lambda link: (link["source"], link["target"], link["type"])),
    }


def _build_manifest(
    pages: list[dict[str, Any]],
    companies: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    entities: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    thesis: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": "build:site-data",
        "generator": GENERATOR_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_hash": _source_hash(),
        "source_counts": {
            "wiki_markdown": len(list(WIKI_DIR.rglob("*.md"))),
            "data_yaml": len(list(DATA_DIR.rglob("*.yaml"))),
            "reports": len(list(REPORTS_DIR.glob("*"))),
        },
        "artifact_counts": {
            "pages": len(pages),
            "companies": len(companies),
            "signals": len(signals),
            "claims": len(claims),
            "entities": len(entities),
            "edges": len(edges),
            "reports": len(reports),
            "thesis_stages": len(thesis.get("cascade", [])),
        },
        "warnings": [],
    }


def _schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "semi-stocks site-data contract",
        "version": GENERATOR_VERSION,
        "artifacts": {
            name: {"type": kind}
            for name, kind in {
                "build.json": "object",
                "schema.json": "object",
                "pages.json": "array",
                "companies.json": "array",
                "signals.json": "array",
                "entities.json": "array",
                "edges.json": "array",
                "claims.json": "array",
                "thesis.json": "object",
                "reports.json": "array",
                "search.json": "array",
                "graph.json": "object",
            }.items()
        },
        "edge_types": sorted(EDGE_TYPES),
        "required_record_fields": {
            "page": ["id", "slug", "title", "type", "path"],
            "company": ["id", "ticker", "name"],
            "signal": ["id", "kind", "evidence"],
            "edge": ["id", "type", "source", "target"],
            "claim": ["id", "ticker", "claim", "status"],
            "report": ["id", "title", "path", "sections"],
        },
    }


def _ids_for(rows: list[dict[str, Any]], label: str) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not row_id:
            raise ValueError(f"Missing ID in {label}: {row}")
        if row_id in seen:
            raise ValueError(f"Duplicate ID in {label}: {row_id}")
        seen.add(row_id)
    return seen


def _load_company_packets() -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    companies_dir = DATA_DIR / "companies"
    if not companies_dir.exists():
        return packets
    for path in sorted(companies_dir.glob("*/*.yaml")):
        data = _read_yaml(path)
        if data:
            data["_file"] = _rel(path)
            packets.append(data)
    return packets


def _load_thesis_proposals() -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    root = DATA_DIR / "thesis-proposals"
    if not root.exists():
        return proposals
    for path in sorted(root.glob("*.yaml")):
        data = _read_yaml(path)
        data["_file"] = _rel(path)
        data["_slug"] = _slugify(path.stem)
        proposals.append(data)
    return proposals


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(_jsonable(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return _rel(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _split_frontmatter(source: str) -> tuple[dict[str, Any], str]:
    if not source.startswith("---\n"):
        return {}, source
    _, marker, remainder = source.partition("\n---\n")
    if not marker:
        return {}, source
    raw = source[4: source.index("\n---\n")]
    return yaml.safe_load(raw) or {}, remainder


def _extract_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _strip_leading_h1(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).lstrip()
    return markdown


def _extract_outgoing_slugs(markdown: str) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for match in WIKILINK_RE.finditer(markdown):
        target = match.group(1).strip().split("/")[-1]
        slug = _slugify(target)
        if slug and slug not in seen:
            result.append(slug)
            seen.add(slug)
    return result


def _plain_text(markdown: str) -> str:
    text = re.sub(r"`{1,3}[^`]*`{1,3}", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#>*_\-|]+", " ", text)
    return _clean(text)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _clip(value: Any, limit: int) -> str:
    text = _clean(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _slugify(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "unknown"


def _titleize(value: Any) -> str:
    return str(value or "").replace("_", " ").replace("-", " ").title()


def _page_id(slug: str) -> str:
    return f"page:{_slugify(slug)}"


def _company_id(ticker: str) -> str:
    return f"company:{str(ticker).upper()}"


def _entity_id(entity_type: str, value: Any) -> str:
    return f"{entity_type}:{_slugify(value)}"


def _bottleneck_id(value: Any) -> str:
    return _entity_id("bottleneck", value)


def _thesis_stage_id(value: Any) -> str:
    return _entity_id("thesis-stage", value)


def _page_type(path: Path) -> str:
    rel = path.relative_to(WIKI_DIR)
    if rel.parts[0] == "concepts":
        return "concept"
    if rel.parts[0] == "sources":
        return "source"
    if rel.parts[0] == "outputs":
        return "output"
    if rel.parts[0] == "raw":
        return "raw"
    return "meta"


def _path_sort_key(path: Path) -> tuple[int, str]:
    priority = {"concept": 0, "source": 1, "output": 2, "meta": 3, "raw": 4}
    return priority.get(_page_type(path), 9), _rel(path)


def _source_page_slug(value: Any) -> str | None:
    if not value:
        return None
    return _slugify(Path(str(value)).stem)


def _first_position_company(ticker: str, *sources: Any) -> str | None:
    for source in sources:
        position = source.lookup(ticker)
        if position and position.get("company"):
            return position["company"]
    return None


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _rel_from_string(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)
    if text.startswith(str(REPO_ROOT)):
        return _rel(Path(text))
    return text


def _source_hash() -> str:
    digest = hashlib.sha256()
    paths = []
    paths.extend(WIKI_DIR.rglob("*.md"))
    paths.extend(DATA_DIR.rglob("*.yaml"))
    if THESIS_PATH.exists():
        paths.append(THESIS_PATH)
    latest = REPORTS_DIR / "latest.html"
    if latest.exists():
        paths.append(latest)
    for path in sorted(set(paths), key=lambda item: _rel(item)):
        digest.update(_rel(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
