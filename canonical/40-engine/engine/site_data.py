"""Build the schema-first site-data contract for the semi-stocks reader."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
from datetime import date, datetime, timezone
from itertools import combinations
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
SIGNAL_DESK_VERSION = "signal-desk-v0.2"
SIGNAL_DESK_GENERATOR_VERSION = "site-data-v0.2"
COMPANY_ROLES_PATH = DATA_DIR / "company_roles.yaml"
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
        "signal_desk",
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
        "signal_desk_rows": len(artifacts["signal_desk"].get("rows", [])),
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
        "signal_desk",
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

    validate_signal_desk(artifacts["signal_desk"])


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
    signal_desk = _build_signal_desk(
        page_index=page_index,
        thesis=thesis,
        thesis_payload=thesis_payload,
        companies=companies,
        signals=signals,
        claims=claims,
        company_packets=company_packets,
        thesis_proposals=thesis_proposals,
    )
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
        "signal_desk": signal_desk,
    }


def validate_signal_desk(signal_desk: dict[str, Any]) -> None:
    """Validate the Signal Desk payload's referential and semantic contract."""
    required = {
        "version",
        "build",
        "features",
        "defaults",
        "quality",
        "facets",
        "source_documents",
        "companies",
        "rows",
        "graph",
        "indexes",
        "tables",
    }
    missing = required - set(signal_desk)
    if missing:
        raise ValueError(f"Signal Desk missing keys: {', '.join(sorted(missing))}")
    if signal_desk.get("version") != SIGNAL_DESK_VERSION:
        raise ValueError(f"Unexpected Signal Desk version: {signal_desk.get('version')}")
    if signal_desk.get("features", {}).get("trace", {}).get("visible") is not False:
        raise ValueError("Signal Desk MVP requires features.trace.visible=false")
    if signal_desk.get("quality", {}).get("trace_ready") is not False:
        raise ValueError("Signal Desk MVP requires quality.trace_ready=false")
    if signal_desk.get("graph", {}).get("mode") != "contextual_evidence":
        raise ValueError("Signal Desk graph mode must be contextual_evidence")

    facets = signal_desk["facets"]
    role_ids = {item["id"] for item in facets.get("company_roles", [])}
    source_channel_ids = {item["id"] for item in facets.get("source_channels", [])}
    thesis_theme_ids = {item["id"] for item in facets.get("thesis_themes", [])}
    support_families = set(facets.get("graph_support_families", []))
    if support_families != {"co_position", "shared_signal"}:
        raise ValueError(f"Signal Desk MVP graph support families must be co_position/shared_signal: {support_families}")

    source_documents = signal_desk["source_documents"]
    companies = signal_desk["companies"]
    rows = signal_desk["rows"]
    graph = signal_desk["graph"]

    _ensure_unique_ids(source_documents, "signal_desk.source_documents")
    _ensure_unique_ids(companies, "signal_desk.companies")
    _ensure_unique_ids(rows, "signal_desk.rows")

    source_document_ids = {item["id"] for item in source_documents}
    company_ids = {item["id"] for item in companies}
    row_ids = {item["id"] for item in rows}

    for source_document in source_documents:
        if source_document.get("source_channel_id") not in source_channel_ids:
            raise ValueError(f"Unknown source channel in source document {source_document.get('id')}")
        _require_period(source_document.get("period"), source_document.get("id"))
        _require_timeline(source_document.get("timeline"), source_document.get("id"))
        for company_id in source_document.get("company_ids", []):
            if company_id not in company_ids:
                raise ValueError(f"Unknown company {company_id} in source document {source_document['id']}")

    for company in companies:
        role_id = company.get("primary_role_id")
        if role_id not in role_ids:
            raise ValueError(f"Unknown primary role {role_id!r} in {company.get('id')}")
        for role_id in company.get("secondary_role_ids", []):
            if role_id not in role_ids:
                raise ValueError(f"Unknown secondary role {role_id!r} in {company.get('id')}")
        for theme_id in company.get("thesis_theme_ids", []):
            if theme_id not in thesis_theme_ids:
                raise ValueError(f"Unknown thesis theme {theme_id!r} in {company.get('id')}")
        for doc_id in company.get("source_document_ids", []):
            if doc_id not in source_document_ids:
                raise ValueError(f"Unknown source document {doc_id!r} in {company.get('id')}")

    for row in rows:
        row_id = row.get("id")
        if row.get("source_channel_id") not in source_channel_ids:
            raise ValueError(f"Unknown source channel in row {row_id}")
        if not row.get("company_ids"):
            raise ValueError(f"Row missing company_ids: {row_id}")
        if not row.get("source_document_ids"):
            raise ValueError(f"Row missing source_document_ids: {row_id}")
        if not row.get("source_paths"):
            raise ValueError(f"Row missing source_paths: {row_id}")
        for company_id in row.get("company_ids", []):
            if company_id not in company_ids:
                raise ValueError(f"Unknown company {company_id} in row {row_id}")
        primary_company_id = row.get("primary_company_id")
        if primary_company_id is not None and primary_company_id not in row.get("company_ids", []):
            raise ValueError(f"primary_company_id not in company_ids for row {row_id}")
        for doc_id in row.get("source_document_ids", []):
            if doc_id not in source_document_ids:
                raise ValueError(f"Unknown source document {doc_id} in row {row_id}")
        for theme_id in row.get("thesis_theme_ids", []):
            if theme_id not in thesis_theme_ids:
                raise ValueError(f"Unknown thesis theme {theme_id} in row {row_id}")
        _require_period(row.get("period"), row_id)
        _require_timeline(row.get("timeline"), row_id)
        graph_eligibility = row.get("graph_eligibility", {})
        if row.get("row_type") in {"claim", "proposal"} and graph_eligibility.get("eligible"):
            raise ValueError(f"{row.get('row_type')} rows cannot be graph eligible in MVP: {row_id}")
        family = graph_eligibility.get("family")
        if graph_eligibility.get("eligible") and family not in support_families:
            raise ValueError(f"Unsupported graph family {family!r} in row {row_id}")

    graph_node_ids = {node.get("id") for node in graph.get("nodes", [])}
    if graph.get("mode") != "contextual_evidence":
        raise ValueError("Signal Desk graph mode must be contextual_evidence")
    for node in graph.get("nodes", []):
        if node.get("company_id") not in company_ids:
            raise ValueError(f"Graph node missing company: {node}")
    for edge in graph.get("edges", []):
        edge_company_ids = edge.get("company_ids", [])
        if len(edge_company_ids) != 2:
            raise ValueError(f"Graph edge must have two company IDs: {edge.get('id')}")
        if edge_company_ids != sorted(edge_company_ids):
            raise ValueError(f"Graph edge company IDs must be sorted: {edge.get('id')}")
        for company_id in edge_company_ids:
            if company_id not in graph_node_ids:
                raise ValueError(f"Graph edge endpoint missing graph node: {edge.get('id')} {company_id}")
        if edge.get("trace_eligible") is not False:
            raise ValueError(f"Graph edge cannot be trace eligible in MVP: {edge.get('id')}")
        for support in edge.get("support", []):
            family = support.get("family")
            if family not in support_families:
                raise ValueError(f"Unsupported graph support family {family!r} in {edge.get('id')}")
            for row_id in support.get("row_ids", []):
                if row_id not in row_ids:
                    raise ValueError(f"Unknown support row {row_id} in graph edge {edge.get('id')}")

    position_counts = signal_desk.get("quality", {}).get("position_leg_counts", {})
    for source_name in ("baker", "leopold"):
        counts = position_counts.get(source_name, {})
        if counts.get("source") != counts.get("emitted"):
            raise ValueError(f"{source_name} source/emitted position counts differ: {counts}")


def _build_signal_desk(
    page_index: dict[str, Any],
    thesis: dict[str, Any],
    thesis_payload: dict[str, Any],
    companies: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    company_packets: list[dict[str, Any]],
    thesis_proposals: list[dict[str, Any]],
) -> dict[str, Any]:
    role_config = _load_company_role_config()
    pages_by_slug = {page["slug"]: page for page in page_index["pages"]}
    companies_by_id = {company["id"]: company for company in companies}
    companies_by_ticker = {company["ticker"]: company for company in companies}
    thesis_theme_ids_by_company = _thesis_theme_ids_by_company(thesis_payload)
    thesis_theme_ids_by_name = {
        stage["name"]: _thesis_theme_id_from_stage_id(stage["id"])
        for stage in thesis_payload.get("cascade", [])
    }
    thesis_theme_ids_by_bottleneck = _thesis_theme_ids_by_bottleneck(thesis_payload)

    source_channels = _source_channel_facets()
    source_documents = _build_signal_desk_source_documents(
        pages_by_slug=pages_by_slug,
        thesis=thesis,
        thesis_payload=thesis_payload,
        companies_by_id=companies_by_id,
        company_packets=company_packets,
        thesis_proposals=thesis_proposals,
        thesis_theme_ids_by_company=thesis_theme_ids_by_company,
        thesis_theme_ids_by_name=thesis_theme_ids_by_name,
    )
    source_documents_by_id = {doc["id"]: doc for doc in source_documents}

    rows = _build_signal_desk_rows(
        signals=signals,
        claims=claims,
        thesis_proposals=thesis_proposals,
        companies_by_id=companies_by_id,
        companies_by_ticker=companies_by_ticker,
        source_documents_by_id=source_documents_by_id,
        thesis_theme_ids_by_company=thesis_theme_ids_by_company,
        thesis_theme_ids_by_bottleneck=thesis_theme_ids_by_bottleneck,
        thesis_theme_ids_by_name=thesis_theme_ids_by_name,
    )
    companies_payload = _build_signal_desk_companies(
        companies=companies,
        rows=rows,
        source_documents=source_documents,
        role_config=role_config,
        thesis_theme_ids_by_company=thesis_theme_ids_by_company,
    )
    company_ids = {company["id"] for company in companies_payload}
    source_documents = _filter_source_documents_for_companies(source_documents, company_ids)
    rows = [row for row in rows if set(row.get("company_ids", [])) <= company_ids]

    source_channels = _with_source_channel_counts(source_channels, rows, source_documents, companies_payload)
    company_roles = _company_role_facets(role_config, companies_payload, rows)
    thesis_themes = _thesis_theme_facets(thesis_payload, companies_payload, rows)
    indexes = _build_signal_desk_indexes(rows, companies_payload, source_documents)
    tables = _build_signal_desk_tables(rows, source_documents)
    graph = _build_signal_desk_graph(companies_payload, rows)
    quality = _build_signal_desk_quality(rows, graph)
    facets = {
        "source_channels": source_channels,
        "company_roles": company_roles,
        "thesis_themes": thesis_themes,
        "row_types": ["position", "signal", "claim", "proposal"],
        "graph_support_families": ["co_position", "shared_signal"],
    }
    build_payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generator": SIGNAL_DESK_GENERATOR_VERSION,
        "source_hash": _source_hash(),
        "collection_hashes": {},
    }
    payload = {
        "version": SIGNAL_DESK_VERSION,
        "build": build_payload,
        "features": {
            "search": True,
            "timeline": True,
            "trace": {
                "status": "parked",
                "visible": False,
                "reason": "requires a separate typed relationship_edges dataset",
            },
        },
        "defaults": {
            "filters": {
                "search": "",
                "source_channel_ids": [],
                "company_role_ids": [],
                "thesis_theme_ids": [],
                "timeline": {"from": None, "to": None},
                "include_undated": True,
            },
        },
        "quality": quality,
        "facets": facets,
        "source_documents": source_documents,
        "companies": companies_payload,
        "rows": rows,
        "graph": graph,
        "indexes": indexes,
        "tables": tables,
    }
    for name in ("facets", "source_documents", "companies", "rows", "graph", "indexes", "tables"):
        payload["build"]["collection_hashes"][name] = _collection_hash(payload[name])
    return payload


def _source_channel_facets() -> list[dict[str, Any]]:
    channels = [
        ("source-channel:baker", "Baker", "fund_positioning", ["atreides", "gavin-baker"], "Baker / Atreides fund-positioning evidence."),
        ("source-channel:leopold", "Leopold", "fund_positioning", ["situational-awareness", "situational awareness"], "Leopold / Situational Awareness fund-positioning evidence."),
        ("source-channel:semianalysis", "SemiAnalysis", "supply_chain_research", ["sem", "semi-analysis", "sa", "dylan-patel"], "SemiAnalysis supply-chain research evidence."),
        ("source-channel:company-earnings", "Company earnings", "company_reported", [], "Company-reported earnings packets, signals, and proof gates."),
        ("source-channel:thesis-stage", "Thesis stage", "thesis_control", [], "Current thesis cascade control-plane signals."),
        ("source-channel:pending-proposals", "Pending proposals", "thesis_proposal", [], "Pending or recently applied thesis proposal rows."),
    ]
    return [
        {
            "id": channel_id,
            "label": label,
            "channel_kind": channel_kind,
            "aliases": aliases,
            "description": description,
            "counts": {"companies": 0, "rows": 0, "source_documents": 0},
            "search_text": _search_text(channel_id, label, channel_kind, aliases, description),
        }
        for channel_id, label, channel_kind, aliases, description in channels
    ]


def _with_source_channel_counts(
    source_channels: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    source_documents: list[dict[str, Any]],
    companies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    channel_to_companies: dict[str, set[str]] = {channel["id"]: set() for channel in source_channels}
    channel_to_rows: dict[str, int] = {channel["id"]: 0 for channel in source_channels}
    channel_to_docs: dict[str, int] = {channel["id"]: 0 for channel in source_channels}
    for row in rows:
        channel_id = row.get("source_channel_id")
        if channel_id in channel_to_rows:
            channel_to_rows[channel_id] += 1
            channel_to_companies[channel_id].update(row.get("company_ids", []))
    for doc in source_documents:
        channel_id = doc.get("source_channel_id")
        if channel_id in channel_to_docs:
            channel_to_docs[channel_id] += 1
            channel_to_companies[channel_id].update(doc.get("company_ids", []))
    visible_companies = {company["id"] for company in companies}
    result = []
    for channel in source_channels:
        item = {**channel}
        item["counts"] = {
            "companies": len(channel_to_companies[item["id"]] & visible_companies),
            "rows": channel_to_rows[item["id"]],
            "source_documents": channel_to_docs[item["id"]],
        }
        result.append(item)
    return sorted(result, key=lambda item: item["id"])


def _load_company_role_config() -> dict[str, Any]:
    data = _read_yaml(COMPANY_ROLES_PATH)
    if not data.get("roles") or not data.get("companies"):
        raise ValueError(f"Missing role map data in {_rel(COMPANY_ROLES_PATH)}")
    return data


def _company_role_facets(
    role_config: dict[str, Any],
    companies: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    role_rows: dict[str, set[str]] = {}
    company_roles: dict[str, set[str]] = {}
    company_by_id = {company["id"]: company for company in companies}
    for company in companies:
        roles = [company["primary_role_id"], *company.get("secondary_role_ids", [])]
        for role_id in roles:
            company_roles.setdefault(role_id, set()).add(company["id"])
    for row in rows:
        for company_id in row.get("company_ids", []):
            company = company_by_id.get(company_id)
            if not company:
                continue
            roles = [company["primary_role_id"], *company.get("secondary_role_ids", [])]
            for role_id in roles:
                role_rows.setdefault(role_id, set()).add(row["id"])

    facets = []
    for role in (role_config.get("roles") or {}).values():
        role_id = role["id"]
        facets.append({
            "id": role_id,
            "label": role.get("label", _titleize(role_id.split(":", 1)[1])),
            "rank": role.get("rank"),
            "aliases": role.get("aliases", []) or [],
            "description": role.get("description", ""),
            "counts": {
                "companies": len(company_roles.get(role_id, set())),
                "rows": len(role_rows.get(role_id, set())),
            },
            "search_text": _search_text(role_id, role.get("label"), role.get("aliases", []), role.get("description"), role.get("search_text")),
        })
    return sorted(facets, key=lambda item: (999 if item.get("rank") is None else item["rank"], item["id"]))


def _thesis_theme_facets(
    thesis_payload: dict[str, Any],
    companies: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    company_counts: dict[str, set[str]] = {}
    row_counts: dict[str, set[str]] = {}
    for company in companies:
        for theme_id in company.get("thesis_theme_ids", []):
            company_counts.setdefault(theme_id, set()).add(company["id"])
    for row in rows:
        for theme_id in row.get("thesis_theme_ids", []):
            row_counts.setdefault(theme_id, set()).add(row["id"])

    facets = []
    for stage in thesis_payload.get("cascade", []):
        theme_id = _thesis_theme_id_from_stage_id(stage["id"])
        facets.append({
            "id": theme_id,
            "slug": theme_id.split(":", 1)[1],
            "label": stage.get("name", ""),
            "status": _theme_status(stage.get("status")),
            "period": _period_from_label(stage.get("period")),
            "parent_bucket": None,
            "cycle_phase": stage.get("cycle_phase"),
            "counts": {
                "companies": len(company_counts.get(theme_id, set())),
                "rows": len(row_counts.get(theme_id, set())),
            },
            "search_text": _search_text(theme_id, stage.get("name"), stage.get("status"), stage.get("period"), stage.get("cycle_phase"), stage.get("signals", [])),
        })
    return sorted(facets, key=lambda item: item["id"])


def _build_signal_desk_source_documents(
    pages_by_slug: dict[str, dict[str, Any]],
    thesis: dict[str, Any],
    thesis_payload: dict[str, Any],
    companies_by_id: dict[str, dict[str, Any]],
    company_packets: list[dict[str, Any]],
    thesis_proposals: list[dict[str, Any]],
    thesis_theme_ids_by_company: dict[str, list[str]],
    thesis_theme_ids_by_name: dict[str, str],
) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for fund_name in ("baker", "leopold"):
        path = _latest_source_file(fund_name)
        data = _read_yaml(path)
        quarter_label = str(data.get("quarter", "Q4 2025"))
        period_end = _string_or_none(data.get("period"))
        filed = _string_or_none(data.get("filed"))
        company_ids = sorted({
            _company_id(str(position.get("ticker", "")).upper())
            for position in data.get("positions", []) or []
            if position.get("ticker") and _company_id(str(position.get("ticker", "")).upper()) in companies_by_id
        })
        related_path, wiki_slug = _wiki_source_for_slug(pages_by_slug, f"{fund_name}-{_slugify(quarter_label)}")
        docs.append({
            "id": _source_doc_id(fund_name, _slugify(quarter_label)),
            "source_channel_id": f"source-channel:{fund_name}",
            "document_kind": "13f_filing",
            "title": f"{data.get('entity', fund_name.title())} {quarter_label} 13F",
            "canonical_path": _rel(path),
            "related_paths": [related_path] if related_path else [],
            "wiki_page_slug": wiki_slug,
            "external_url": None,
            "company_ids": company_ids,
            "thesis_theme_ids": _unique_sorted(theme for company_id in company_ids for theme in thesis_theme_ids_by_company.get(company_id, [])),
            "period": _period_from_quarter(quarter_label, period_end),
            "timeline": _timeline(filed, f"Filed {_display_date(filed)}" if filed else f"{quarter_label} filing", "filed_date"),
            "search_text": _search_text(fund_name, data.get("entity"), quarter_label, "13F", company_ids),
        })

    semi_path = DATA_DIR / "sources" / "semianalysis" / "signals.yaml"
    semi_data = _read_yaml(semi_path)
    company_ids = sorted({
        _company_id(str(ticker).upper())
        for signal in semi_data.get("signals", []) or []
        for ticker in signal.get("tickers", []) or []
        if _company_id(str(ticker).upper()) in companies_by_id
    })
    related_path, wiki_slug = _wiki_source_for_slug(pages_by_slug, "semianalysis-signals")
    updated = _string_or_none(semi_data.get("updated"))
    docs.append({
        "id": "source-doc:semianalysis:signals",
        "source_channel_id": "source-channel:semianalysis",
        "document_kind": "supply_chain_research",
        "title": semi_data.get("entity", "SemiAnalysis Signals"),
        "canonical_path": _rel(semi_path),
        "related_paths": [related_path] if related_path else [],
        "wiki_page_slug": wiki_slug,
        "external_url": None,
        "company_ids": company_ids,
        "thesis_theme_ids": _unique_sorted(theme for company_id in company_ids for theme in thesis_theme_ids_by_company.get(company_id, [])),
        "period": _period_from_label("ongoing"),
        "timeline": _timeline(updated, f"Updated {_display_date(updated)}" if updated else "Ongoing", "published_date"),
        "search_text": _search_text("semianalysis", semi_data.get("entity"), "supply chain research", company_ids),
    })

    for packet in sorted(company_packets, key=lambda item: str(item.get("_file", ""))):
        ticker = str(packet.get("ticker", "")).upper()
        company_id = _company_id(ticker)
        if company_id not in companies_by_id:
            continue
        quarter = str(packet.get("quarter", "unknown"))
        source_page = _source_page_slug(packet.get("source_page"))
        related_path, wiki_slug = _wiki_source_for_slug(pages_by_slug, source_page)
        docs.append({
            "id": _company_source_doc_id(ticker, quarter),
            "source_channel_id": "source-channel:company-earnings",
            "document_kind": "company_packet",
            "title": f"{packet.get('company', ticker)} {quarter}",
            "canonical_path": _rel_from_string(packet.get("_file")),
            "related_paths": [related_path] if related_path else [],
            "wiki_page_slug": wiki_slug,
            "external_url": None,
            "company_ids": [company_id],
            "thesis_theme_ids": thesis_theme_ids_by_company.get(company_id, []),
            "period": _period_from_quarter(quarter, _string_or_none(packet.get("period"))),
            "timeline": _timeline(_string_or_none(packet.get("period")), quarter, "period_end", precision="quarter"),
            "search_text": _search_text(ticker, packet.get("company"), quarter, packet.get("_file")),
        })

    thesis_company_ids = _unique_sorted(
        company_id
        for stage in thesis_payload.get("cascade", [])
        for company_id in stage.get("company_ids", [])
        if company_id in companies_by_id
    )
    docs.append({
        "id": "source-doc:thesis:current",
        "source_channel_id": "source-channel:thesis-stage",
        "document_kind": "thesis_control",
        "title": "Current thesis control plane",
        "canonical_path": _rel(THESIS_PATH),
        "related_paths": [],
        "wiki_page_slug": None,
        "external_url": None,
        "company_ids": thesis_company_ids,
        "thesis_theme_ids": [theme["id"] for theme in _thesis_theme_facets(thesis_payload, [], [])],
        "period": _period_from_label("current"),
        "timeline": _timeline(_string_or_none(thesis.get("updated")), f"Updated {thesis.get('updated')}", "thesis_updated"),
        "search_text": _search_text("thesis", "current thesis", THESIS_PATH),
    })

    for proposal in thesis_proposals:
        slug = proposal["_slug"]
        company_ids = _proposal_company_ids(proposal, thesis_payload, companies_by_id)
        theme_ids = _proposal_theme_ids(proposal, thesis_theme_ids_by_name)
        docs.append({
            "id": _proposal_source_doc_id(slug),
            "source_channel_id": "source-channel:pending-proposals",
            "document_kind": "thesis_proposal",
            "title": _clip(proposal.get("proposal", slug), 120),
            "canonical_path": proposal["_file"],
            "related_paths": [],
            "wiki_page_slug": None,
            "external_url": None,
            "company_ids": company_ids,
            "thesis_theme_ids": theme_ids,
            "period": _period_from_label("proposal"),
            "timeline": _timeline(_string_or_none(proposal.get("updated") or proposal.get("created")), f"Updated {proposal.get('updated') or proposal.get('created')}", "proposal_updated"),
            "search_text": _search_text(slug, proposal.get("proposal"), proposal.get("status"), proposal.get("target_sections", [])),
        })

    return sorted(docs, key=lambda item: item["id"])


def _build_signal_desk_rows(
    signals: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    thesis_proposals: list[dict[str, Any]],
    companies_by_id: dict[str, dict[str, Any]],
    companies_by_ticker: dict[str, dict[str, Any]],
    source_documents_by_id: dict[str, dict[str, Any]],
    thesis_theme_ids_by_company: dict[str, list[str]],
    thesis_theme_ids_by_bottleneck: dict[str, list[str]],
    thesis_theme_ids_by_name: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_build_position_rows(companies_by_id, source_documents_by_id, thesis_theme_ids_by_company))
    rows.extend(_build_signal_rows(signals, companies_by_id, companies_by_ticker, source_documents_by_id, thesis_theme_ids_by_company, thesis_theme_ids_by_bottleneck))
    rows.extend(_build_claim_rows(claims, companies_by_id, source_documents_by_id, thesis_theme_ids_by_company))
    rows.extend(_build_proposal_rows(thesis_proposals, companies_by_id, source_documents_by_id, thesis_theme_ids_by_name))
    return sorted(rows, key=lambda item: item["id"])


def _build_position_rows(
    companies_by_id: dict[str, dict[str, Any]],
    source_documents_by_id: dict[str, dict[str, Any]],
    thesis_theme_ids_by_company: dict[str, list[str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fund_name in ("baker", "leopold"):
        path = _latest_source_file(fund_name)
        data = _read_yaml(path)
        quarter = str(data.get("quarter", "unknown"))
        period_end = _string_or_none(data.get("period"))
        filed = _string_or_none(data.get("filed"))
        source_document_id = _source_doc_id(fund_name, _slugify(quarter))
        source_document = source_documents_by_id.get(source_document_id, {})
        seen_by_key: dict[str, int] = {}
        for position in data.get("positions", []) or []:
            ticker = str(position.get("ticker", "")).upper()
            company_id = _company_id(ticker)
            if company_id not in companies_by_id:
                continue
            position_type = _position_type(position.get("type"))
            base_key = f"{fund_name}:{ticker}:{_slugify(quarter)}:{position_type}"
            seen_by_key[base_key] = seen_by_key.get(base_key, 0) + 1
            position_leg_id = f"{base_key}:{seen_by_key[base_key]:02d}"
            row_id = f"row:position:{position_leg_id}"
            value = position.get("value")
            pct = position.get("pct_portfolio")
            title = f"{fund_name.title()} {ticker} {position_type} position"
            summary = _clip(position.get("notes") or f"{ticker} {position_type} position in {quarter}", 240)
            rows.append({
                **_base_row(
                    row_id=row_id,
                    row_type="position",
                    title=title,
                    summary=summary,
                    company_ids=[company_id],
                    primary_company_id=company_id,
                    source_channel_id=f"source-channel:{fund_name}",
                    source_document_ids=[source_document_id],
                    source_paths=[_rel(path)],
                    thesis_theme_ids=thesis_theme_ids_by_company.get(company_id, []),
                    period=_period_from_quarter(quarter, period_end),
                    timeline=_timeline(filed, f"Filed {_display_date(filed)}" if filed else f"{quarter} filing", "filed_date"),
                    graph_eligibility={
                        "eligible": True,
                        "family": "co_position",
                        "reason": "fund position row can support co-position contextual graph edges",
                    },
                    lifecycle_state="reported",
                    ui_badges=[fund_name.title(), position_type],
                    search_parts=[fund_name, ticker, position.get("company"), position_type, value, pct, position.get("notes"), source_document.get("title")],
                ),
                "fund_id": fund_name,
                "position_leg_id": position_leg_id,
                "position_type": position_type,
                "filed_date": filed,
                "shares": position.get("shares"),
                "value": value,
                "pct_portfolio": pct,
                "change_vs_prior": _change_vs_prior(position.get("change_vs_prior")),
                "underlier_ticker": ticker if position_type in {"call", "put"} else None,
            })
    return rows


def _build_signal_rows(
    signals: list[dict[str, Any]],
    companies_by_id: dict[str, dict[str, Any]],
    companies_by_ticker: dict[str, dict[str, Any]],
    source_documents_by_id: dict[str, dict[str, Any]],
    thesis_theme_ids_by_company: dict[str, list[str]],
    thesis_theme_ids_by_bottleneck: dict[str, list[str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signal in signals:
        kind = signal.get("kind")
        if kind == "thesis_proposal_signal":
            continue
        row_id = f"row:{signal['id']}"
        company_ids: list[str] = []
        source_channel_id = "source-channel:thesis-stage"
        source_document_ids = ["source-doc:thesis:current"]
        title = signal.get("title") or signal.get("ticker") or signal.get("bottleneck") or kind
        timeline = _timeline(None, "Undated thesis signal", "label")
        period = _period_from_label(signal.get("quarter") or signal.get("date") or "signal")
        graph_eligible = False
        graph_family = None
        graph_reason = "single-company or thesis-stage signal is table/profile context only"

        if kind == "company_thesis_signal":
            ticker = str(signal.get("ticker", "")).upper()
            company_id = _company_id(ticker)
            if company_id not in companies_by_id:
                continue
            company_ids = [company_id]
            source_channel_id = "source-channel:company-earnings"
            source_document_ids = [_company_source_doc_id(ticker, signal.get("quarter", "unknown"))]
            timeline = _timeline(None, str(signal.get("quarter") or "Company signal"), "label")
            period = _period_from_quarter(signal.get("quarter"), None)
        elif kind == "semianalysis_signal":
            company_ids = [
                _company_id(str(ticker).upper())
                for ticker in signal.get("tickers", []) or []
                if _company_id(str(ticker).upper()) in companies_by_id
            ]
            if not company_ids:
                continue
            source_channel_id = "source-channel:semianalysis"
            source_document_ids = ["source-doc:semianalysis:signals"]
            timeline = _timeline(signal.get("date"), _display_date(signal.get("date")) or "SemiAnalysis signal", "published_date")
            period = _period_from_label(signal.get("date"))
            graph_eligible = len(company_ids) >= 2
            graph_family = "shared_signal" if graph_eligible else None
            graph_reason = "multi-company SemiAnalysis signal supports contextual shared-signal edges" if graph_eligible else "single-company signal"
        elif kind == "thesis_stage_signal":
            stage_id = signal.get("stage_id")
            # Thesis stage signals are profile/table context, not graph support in the MVP.
            company_ids = [
                company_id
                for company_id, theme_ids in thesis_theme_ids_by_company.items()
                if stage_id and _thesis_theme_id_from_stage_id(stage_id) in theme_ids
            ]
            if not company_ids:
                continue
            source_channel_id = "source-channel:thesis-stage"
            source_document_ids = ["source-doc:thesis:current"]

        source_document_ids = [doc_id for doc_id in source_document_ids if doc_id in source_documents_by_id]
        if not source_document_ids:
            continue
        thesis_theme_ids = _unique_sorted(
            [
                *[theme for company_id in company_ids for theme in thesis_theme_ids_by_company.get(company_id, [])],
                *thesis_theme_ids_by_bottleneck.get(str(signal.get("bottleneck") or ""), []),
            ]
        )
        source_paths = _unique_sorted(
            signal.get("source_path"),
            *[source_documents_by_id[doc_id].get("canonical_path") for doc_id in source_document_ids],
        )
        rows.append({
            **_base_row(
                row_id=row_id,
                row_type="signal",
                title=str(title or kind),
                summary=_clip(signal.get("evidence", ""), 260),
                company_ids=sorted(company_ids),
                primary_company_id=company_ids[0] if len(company_ids) == 1 else None,
                source_channel_id=source_channel_id,
                source_document_ids=source_document_ids,
                source_paths=source_paths,
                thesis_theme_ids=thesis_theme_ids,
                period=period,
                timeline=timeline,
                graph_eligibility={"eligible": graph_eligible, "family": graph_family, "reason": graph_reason},
                lifecycle_state="curated",
                ui_badges=[_titleize(kind)],
                search_parts=[title, kind, signal.get("direction"), signal.get("evidence"), signal.get("data_points"), signal.get("source")],
            ),
            "signal_kind": kind,
            "impact_direction": _impact_direction(signal.get("direction")),
            "excerpt_locator": signal.get("source_ref"),
        })
    return rows


def _build_claim_rows(
    claims: list[dict[str, Any]],
    companies_by_id: dict[str, dict[str, Any]],
    source_documents_by_id: dict[str, dict[str, Any]],
    thesis_theme_ids_by_company: dict[str, list[str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for claim in claims:
        ticker = str(claim.get("ticker", "")).upper()
        company_id = _company_id(ticker)
        if company_id not in companies_by_id:
            continue
        source_document_id = _company_source_doc_id(ticker, claim.get("quarter", "unknown"))
        if source_document_id not in source_documents_by_id:
            continue
        row_id = f"row:{claim['id']}"
        title = _clip(claim.get("claim", ""), 120)
        verify_at = claim.get("verify_at") or claim.get("verify_window", {}).get("kind")
        rows.append({
            **_base_row(
                row_id=row_id,
                row_type="claim",
                title=title,
                summary=_clip(claim.get("claim", ""), 260),
                company_ids=[company_id],
                primary_company_id=company_id,
                source_channel_id="source-channel:company-earnings",
                source_document_ids=[source_document_id],
                source_paths=[source_documents_by_id[source_document_id]["canonical_path"]],
                thesis_theme_ids=thesis_theme_ids_by_company.get(company_id, []),
                period=_period_from_quarter(claim.get("quarter"), None),
                timeline=_timeline(None, str(verify_at or "Verification window"), "verify_window"),
                graph_eligibility={"eligible": False, "family": None, "reason": "claims do not create graph edges in MVP"},
                lifecycle_state=_claim_lifecycle_state(claim.get("status")),
                ui_badges=["Claim", _titleize(claim.get("status", "pending"))],
                search_parts=[claim.get("claim"), claim.get("speaker"), claim.get("source"), verify_at, claim.get("notes")],
            ),
            "claim_type": "earnings_claim",
            "claim_text": claim.get("claim", ""),
            "verification_target": verify_at,
            "verification_window_label": verify_at,
            "rationale": claim.get("notes", ""),
            "staleness_policy": "stale after verification window if unresolved",
        })
    return rows


def _build_proposal_rows(
    thesis_proposals: list[dict[str, Any]],
    companies_by_id: dict[str, dict[str, Any]],
    source_documents_by_id: dict[str, dict[str, Any]],
    thesis_theme_ids_by_name: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for proposal in thesis_proposals:
        slug = proposal["_slug"]
        source_document_id = _proposal_source_doc_id(slug)
        if source_document_id not in source_documents_by_id:
            continue
        company_ids = _proposal_company_ids(proposal, {"cascade": []}, companies_by_id)
        theme_ids = _proposal_theme_ids(proposal, thesis_theme_ids_by_name)
        # If proposal company scope cannot be inferred from direct tickers, use
        # the companies carried by its source document.
        if not company_ids:
            company_ids = source_documents_by_id[source_document_id].get("company_ids", [])
        if not company_ids:
            continue
        row_id = f"row:proposal:{slug}"
        title = _clip(proposal.get("proposal", slug), 120)
        updated = _string_or_none(proposal.get("updated") or proposal.get("created"))
        rows.append({
            **_base_row(
                row_id=row_id,
                row_type="proposal",
                title=title,
                summary=_clip(proposal.get("proposal", ""), 260),
                company_ids=company_ids,
                primary_company_id=company_ids[0] if len(company_ids) == 1 else None,
                source_channel_id="source-channel:pending-proposals",
                source_document_ids=[source_document_id],
                source_paths=[source_documents_by_id[source_document_id]["canonical_path"]],
                thesis_theme_ids=theme_ids,
                period=_period_from_label("proposal"),
                timeline=_timeline(updated, f"Updated {_display_date(updated)}" if updated else "Proposal update", "proposal_updated"),
                graph_eligibility={"eligible": False, "family": None, "reason": "proposals do not create graph edges in MVP"},
                lifecycle_state=str(proposal.get("status") or "pending"),
                ui_badges=["Proposal", _titleize(proposal.get("status", "pending"))],
                search_parts=[slug, proposal.get("proposal"), proposal.get("status"), proposal.get("target_sections", []), proposal.get("evidence", [])],
            ),
            "proposal_type": "thesis_patch",
            "affected_company_ids": company_ids,
            "affected_thesis_theme_ids": theme_ids,
        })
    return rows


def _build_signal_desk_companies(
    companies: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    source_documents: list[dict[str, Any]],
    role_config: dict[str, Any],
    thesis_theme_ids_by_company: dict[str, list[str]],
) -> list[dict[str, Any]]:
    role_map = role_config.get("companies", {}) or {}
    role_ids = {role["id"] for role in (role_config.get("roles") or {}).values()}
    rows_by_company: dict[str, list[dict[str, Any]]] = {}
    docs_by_company: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for company_id in row.get("company_ids", []):
            rows_by_company.setdefault(company_id, []).append(row)
    for doc in source_documents:
        for company_id in doc.get("company_ids", []):
            docs_by_company.setdefault(company_id, []).append(doc)

    payload: list[dict[str, Any]] = []
    for company in companies:
        ticker = company["ticker"]
        mapping = role_map.get(ticker)
        if not mapping:
            raise ValueError(f"Missing company role mapping for {ticker}")
        primary_role_id = mapping.get("primary_role_id")
        secondary_role_ids = mapping.get("secondary_role_ids", []) or []
        if primary_role_id not in role_ids:
            raise ValueError(f"Unknown primary role {primary_role_id} for {ticker}")
        unknown_secondary = [role_id for role_id in secondary_role_ids if role_id not in role_ids]
        if unknown_secondary:
            raise ValueError(f"Unknown secondary roles for {ticker}: {unknown_secondary}")

        company_id = company["id"]
        company_rows = rows_by_company.get(company_id, [])
        company_docs = docs_by_company.get(company_id, [])
        if not company_rows and not company_docs:
            continue
        counts = {
            "positions": sum(1 for row in company_rows if row["row_type"] == "position"),
            "signals": sum(1 for row in company_rows if row["row_type"] == "signal"),
            "claims": sum(1 for row in company_rows if row["row_type"] == "claim"),
            "proposals": sum(1 for row in company_rows if row["row_type"] == "proposal"),
            "source_documents": len({doc["id"] for doc in company_docs}),
        }
        theme_ids = _unique_sorted(
            *thesis_theme_ids_by_company.get(company_id, []),
            *[theme_id for row in company_rows for theme_id in row.get("thesis_theme_ids", [])],
        )
        source_channel_ids = _unique_sorted(
            *[row.get("source_channel_id") for row in company_rows],
            *[doc.get("source_channel_id") for doc in company_docs],
        )
        source_document_ids = _unique_sorted(
            *[doc["id"] for doc in company_docs],
            *[doc_id for row in company_rows for doc_id in row.get("source_document_ids", [])],
        )
        payload.append({
            "id": company_id,
            "ticker": ticker,
            "name": company["name"],
            "primary_role_id": primary_role_id,
            "secondary_role_ids": secondary_role_ids,
            "display_tags": mapping.get("display_tags", []) or [],
            "thesis_theme_ids": theme_ids,
            "source_channel_ids": source_channel_ids,
            "source_document_ids": source_document_ids,
            "counts": counts,
            "search_text": _search_text(ticker, company["name"], primary_role_id, secondary_role_ids, mapping.get("display_tags", []), company.get("bottleneck"), company.get("status")),
        })
    return sorted(payload, key=lambda item: item["id"])


def _filter_source_documents_for_companies(
    source_documents: list[dict[str, Any]],
    company_ids: set[str],
) -> list[dict[str, Any]]:
    filtered = []
    for doc in source_documents:
        item = {**doc}
        item["company_ids"] = [company_id for company_id in doc.get("company_ids", []) if company_id in company_ids]
        filtered.append(item)
    return sorted(filtered, key=lambda item: item["id"])


def _build_signal_desk_indexes(
    rows: list[dict[str, Any]],
    companies: list[dict[str, Any]],
    source_documents: list[dict[str, Any]],
) -> dict[str, Any]:
    row_ids_by_type: dict[str, list[str]] = {}
    row_ids_by_company: dict[str, list[str]] = {}
    row_ids_by_source_channel: dict[str, list[str]] = {}
    row_ids_by_thesis_theme: dict[str, list[str]] = {}
    company_ids_by_role: dict[str, list[str]] = {}
    company_ids_by_thesis_theme: dict[str, list[str]] = {}
    source_document_ids_by_source_channel: dict[str, list[str]] = {}
    for row in rows:
        row_ids_by_type.setdefault(row["row_type"], []).append(row["id"])
        row_ids_by_source_channel.setdefault(row["source_channel_id"], []).append(row["id"])
        for company_id in row.get("company_ids", []):
            row_ids_by_company.setdefault(company_id, []).append(row["id"])
        for theme_id in row.get("thesis_theme_ids", []):
            row_ids_by_thesis_theme.setdefault(theme_id, []).append(row["id"])
    for company in companies:
        for role_id in [company["primary_role_id"], *company.get("secondary_role_ids", [])]:
            company_ids_by_role.setdefault(role_id, []).append(company["id"])
        for theme_id in company.get("thesis_theme_ids", []):
            company_ids_by_thesis_theme.setdefault(theme_id, []).append(company["id"])
    for doc in source_documents:
        source_document_ids_by_source_channel.setdefault(doc["source_channel_id"], []).append(doc["id"])
    return {
        "row_ids_by_type": _sort_index(row_ids_by_type),
        "row_ids_by_company": _sort_index(row_ids_by_company),
        "row_ids_by_source_channel": _sort_index(row_ids_by_source_channel),
        "row_ids_by_thesis_theme": _sort_index(row_ids_by_thesis_theme),
        "company_ids_by_role": _sort_index(company_ids_by_role),
        "company_ids_by_thesis_theme": _sort_index(company_ids_by_thesis_theme),
        "source_document_ids_by_source_channel": _sort_index(source_document_ids_by_source_channel),
    }


def _build_signal_desk_tables(rows: list[dict[str, Any]], source_documents: list[dict[str, Any]]) -> dict[str, Any]:
    row_ids_by_type: dict[str, list[str]] = {}
    for row in rows:
        row_ids_by_type.setdefault(row["row_type"], []).append(row["id"])
    views = {
        "signals": _row_table_view("signals", "Signals", "signal", row_ids_by_type.get("signal", []), [
            ("timeline", "Date"),
            ("title", "Signal"),
            ("company_ids", "Companies"),
            ("source_channel_id", "Source Channel"),
            ("thesis_theme_ids", "Thesis Themes"),
            ("impact_direction", "Impact"),
        ]),
        "claims": _row_table_view("claims", "Claims", "claim", row_ids_by_type.get("claim", []), [
            ("timeline", "Date/Window"),
            ("claim_text", "Claim"),
            ("company_ids", "Company"),
            ("source_channel_id", "Source Channel"),
            ("lifecycle_state", "Lifecycle State"),
        ]),
        "positions": _row_table_view("positions", "Positions", "position", row_ids_by_type.get("position", []), [
            ("timeline", "Filed"),
            ("fund_id", "Fund"),
            ("company_ids", "Company"),
            ("position_type", "Position Type"),
            ("value", "Value"),
            ("pct_portfolio", "% Portfolio"),
            ("change_vs_prior", "Change"),
        ]),
        "proposals": _row_table_view("proposals", "Proposals", "proposal", row_ids_by_type.get("proposal", []), [
            ("timeline", "Updated"),
            ("title", "Proposal"),
            ("affected_company_ids", "Companies"),
            ("affected_thesis_theme_ids", "Thesis Themes"),
            ("lifecycle_state", "Lifecycle State"),
        ]),
        "sources": {
            "id": "sources",
            "label": "Sources",
            "entity_type": "source_document",
            "row_type": None,
            "row_ids": [],
            "source_document_ids": sorted(doc["id"] for doc in source_documents),
            "columns": _columns([
                ("timeline", "Date"),
                ("title", "Source"),
                ("source_channel_id", "Source Channel"),
                ("document_kind", "Kind"),
                ("canonical_path", "Canonical Path"),
            ]),
            "default_sort": {"key": "timeline.sort_date", "direction": "desc", "nulls": "last"},
        },
    }
    return {
        "default_view_id": "signals",
        "view_order": ["signals", "claims", "positions", "proposals", "sources"],
        "views": views,
    }


def _build_signal_desk_graph(
    companies: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    company_ids = {company["id"] for company in companies}
    nodes = [
        {
            "id": company["id"],
            "company_id": company["id"],
            "primary_role_id": company["primary_role_id"],
            "thesis_theme_ids": company.get("thesis_theme_ids", []),
            "source_channel_ids": company.get("source_channel_ids", []),
        }
        for company in companies
    ]
    supports: dict[tuple[str, str], list[dict[str, Any]]] = {}

    position_rows = [row for row in rows if row.get("row_type") == "position" and row.get("graph_eligibility", {}).get("family") == "co_position"]
    positions_by_channel: dict[str, list[dict[str, Any]]] = {}
    for row in position_rows:
        positions_by_channel.setdefault(row["source_channel_id"], []).append(row)
    for channel_id, channel_rows in positions_by_channel.items():
        for left, right in combinations(channel_rows, 2):
            left_company = left["company_ids"][0]
            right_company = right["company_ids"][0]
            if left_company == right_company:
                continue
            pair = tuple(sorted((left_company, right_company)))
            if pair[0] not in company_ids or pair[1] not in company_ids:
                continue
            pct_left = left.get("pct_portfolio")
            pct_right = right.get("pct_portfolio")
            if pct_left is None or pct_right is None:
                score = 0.0
            else:
                score = min(1.0, math.sqrt(float(pct_left) * float(pct_right)) / 0.10)
            supports.setdefault(pair, []).append({
                "family": "co_position",
                "source_channel_id": channel_id,
                "score": round(score, 6),
                "row_ids": sorted([left["id"], right["id"]]),
            })

    signal_rows = [row for row in rows if row.get("row_type") == "signal" and row.get("graph_eligibility", {}).get("family") == "shared_signal"]
    signal_rows_by_key: dict[tuple[tuple[str, str], str], list[str]] = {}
    for row in signal_rows:
        for left, right in combinations(sorted(set(row.get("company_ids", []))), 2):
            if left not in company_ids or right not in company_ids:
                continue
            pair = tuple(sorted((left, right)))
            key = (pair, row["source_channel_id"])
            signal_rows_by_key.setdefault(key, []).append(row["id"])
    for (pair, channel_id), row_ids in signal_rows_by_key.items():
        score = min(1.0, len(row_ids) / 3)
        supports.setdefault(pair, []).append({
            "family": "shared_signal",
            "source_channel_id": channel_id,
            "score": round(score, 6),
            "row_ids": sorted(row_ids),
        })

    edges = []
    for pair, support in sorted(supports.items()):
        support = sorted(support, key=lambda item: (item["family"], item["source_channel_id"], item["row_ids"]))
        visual_weight = round(sum(item.get("score", 0) for item in support), 6)
        edges.append({
            "id": f"edge:{pair[0]}__{pair[1]}",
            "company_ids": list(pair),
            "trace_eligible": False,
            "semantic_label": "shared_evidence",
            "support": support,
            "visual_weight": visual_weight,
        })
    return {
        "mode": "contextual_evidence",
        "default_enabled_support_families": ["co_position", "shared_signal"],
        "nodes": sorted(nodes, key=lambda item: item["id"]),
        "edges": edges,
    }


def _build_signal_desk_quality(rows: list[dict[str, Any]], graph: dict[str, Any]) -> dict[str, Any]:
    baker_source = len((_read_yaml(_latest_source_file("baker")).get("positions", []) or []))
    leopold_source = len((_read_yaml(_latest_source_file("leopold")).get("positions", []) or []))
    baker_emitted = sum(1 for row in rows if row.get("row_type") == "position" and row.get("fund_id") == "baker")
    leopold_emitted = sum(1 for row in rows if row.get("row_type") == "position" and row.get("fund_id") == "leopold")
    return {
        "ui_ready": True,
        "trace_ready": False,
        "rows_without_source_document": sum(1 for row in rows if not row.get("source_document_ids")),
        "rows_without_sort_date": sum(1 for row in rows if not row.get("timeline", {}).get("sort_date")),
        "rows_with_label_only_timeline": sum(1 for row in rows if row.get("timeline", {}).get("precision") == "label"),
        "graph_edges_contextual_only": graph.get("mode") == "contextual_evidence",
        "position_leg_counts": {
            "baker": {"source": baker_source, "emitted": baker_emitted},
            "leopold": {"source": leopold_source, "emitted": leopold_emitted},
        },
        "trace_blockers": [
            "no relationship_edges dataset",
            "no typed directional value-chain edges",
            "graph is contextual evidence only",
        ],
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
                "signal_desk.json": "object",
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


def _collection_hash(value: Any) -> str:
    payload = json.dumps(_jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _ensure_unique_ids(rows: list[dict[str, Any]], label: str) -> None:
    seen: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not row_id:
            raise ValueError(f"Missing id in {label}: {row}")
        if row_id in seen:
            raise ValueError(f"Duplicate id in {label}: {row_id}")
        seen.add(row_id)


def _require_period(period: Any, label: Any) -> None:
    if not isinstance(period, dict):
        raise ValueError(f"Missing period object for {label}")
    for key in ("system", "start_date", "end_date", "year", "quarter", "fiscal_year", "fiscal_quarter", "label"):
        if key not in period:
            raise ValueError(f"Period missing {key} for {label}")
    for key in ("start_date", "end_date"):
        if period.get(key):
            _require_iso_date(period[key], f"{label}.{key}")


def _require_timeline(timeline: Any, label: Any) -> None:
    if not isinstance(timeline, dict):
        raise ValueError(f"Missing timeline object for {label}")
    for key in ("sort_date", "end_date", "precision", "label", "kind", "include_in_range"):
        if key not in timeline:
            raise ValueError(f"Timeline missing {key} for {label}")
    if not timeline.get("label"):
        raise ValueError(f"Timeline label required for {label}")
    for key in ("sort_date", "end_date"):
        if timeline.get(key):
            _require_iso_date(timeline[key], f"{label}.{key}")


def _require_iso_date(value: Any, label: str) -> None:
    try:
        date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"Invalid date {value!r} for {label}") from exc


def _search_text(*values: Any) -> str:
    parts: list[str] = []

    def add(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                add(key)
                add(item)
            return
        if isinstance(value, (list, tuple, set)) or (
            not isinstance(value, (str, bytes, dict)) and hasattr(value, "__iter__")
        ):
            for item in value:
                add(item)
            return
        text = _clean(value).lower()
        if text:
            parts.append(text)

    for value in values:
        add(value)
    return " ".join(dict.fromkeys(" ".join(parts).split()))


def _unique_sorted(*values: Any) -> list[str]:
    out: set[str] = set()

    def add(value: Any) -> None:
        if value is None or value == "":
            return
        if isinstance(value, (list, tuple, set)) or (
            not isinstance(value, (str, bytes, dict)) and hasattr(value, "__iter__")
        ):
            for item in value:
                add(item)
            return
        out.add(str(value))

    for value in values:
        add(value)
    return sorted(out)


def _latest_source_file(source_name: str) -> Path:
    root = DATA_DIR / "sources" / source_name
    files = sorted(root.glob("q*.yaml"), reverse=True)
    if not files:
        raise ValueError(f"No source filings found for {source_name}")
    return files[0]


def _source_doc_id(*parts: Any) -> str:
    return "source-doc:" + ":".join(_slugify(part) for part in parts if str(part or ""))


def _company_source_doc_id(ticker: Any, quarter: Any) -> str:
    return _source_doc_id("company", str(ticker).upper(), _slugify(quarter))


def _proposal_source_doc_id(slug: str) -> str:
    return _source_doc_id("proposal", slug)


def _wiki_source_for_slug(pages_by_slug: dict[str, dict[str, Any]], slug: str | None) -> tuple[str | None, str | None]:
    if not slug:
        return None, None
    page = pages_by_slug.get(_slugify(slug))
    if not page:
        return None, None
    return page.get("path"), page.get("slug")


def _period_from_quarter(label: Any, end_date: str | None = None) -> dict[str, Any]:
    text = str(label or "").strip()
    fiscal = re.match(r"Q([1-4])\s+FY(\d{4})", text, re.IGNORECASE)
    if fiscal:
        return _period(
            "fiscal_quarter",
            fiscal_year=int(fiscal.group(2)),
            fiscal_quarter=int(fiscal.group(1)),
            end_date=end_date,
            label=text,
        )
    calendar = re.match(r"Q([1-4])\s+(\d{4})", text, re.IGNORECASE)
    if calendar:
        return _period(
            "calendar_quarter",
            year=int(calendar.group(2)),
            quarter=int(calendar.group(1)),
            end_date=end_date,
            label=text,
        )
    if text and text != "unknown":
        return _period_from_label(text)
    return _period("none")


def _period_from_label(label: Any) -> dict[str, Any]:
    text = _clean(label)
    if not text:
        return _period("none")
    parsed = _period_from_quarter(text, None) if re.match(r"Q[1-4]\s+(FY)?\d{4}", text, re.IGNORECASE) else None
    if parsed and parsed["system"] != "none":
        return parsed
    return _period("label", label=text)


def _period(system: str, **values: Any) -> dict[str, Any]:
    return {
        "system": system,
        "start_date": values.get("start_date"),
        "end_date": values.get("end_date"),
        "year": values.get("year"),
        "quarter": values.get("quarter"),
        "fiscal_year": values.get("fiscal_year"),
        "fiscal_quarter": values.get("fiscal_quarter"),
        "label": values.get("label"),
    }


def _timeline(
    sort_date: Any,
    label: Any,
    kind: str,
    *,
    precision: str | None = None,
    end_date: Any = None,
) -> dict[str, Any]:
    sort_date_text = _string_or_none(sort_date)
    end_date_text = _string_or_none(end_date)
    if sort_date_text and not _is_iso_date(sort_date_text):
        sort_date_text = None
    if end_date_text and not _is_iso_date(end_date_text):
        end_date_text = None
    return {
        "sort_date": sort_date_text,
        "end_date": end_date_text,
        "precision": precision or ("day" if sort_date_text else "label"),
        "label": str(label or (_display_date(sort_date_text) if sort_date_text else "Undated")),
        "kind": kind,
        "include_in_range": bool(sort_date_text),
    }


def _is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _display_date(value: Any) -> str:
    if not value:
        return ""
    text = str(value)
    try:
        parsed = date.fromisoformat(text)
        return f"{parsed.strftime('%b')} {parsed.day} {parsed.year}"
    except ValueError:
        return text


def _thesis_theme_id_from_stage_id(stage_id: str) -> str:
    return "thesis-theme:" + stage_id.split(":", 1)[1]


def _thesis_theme_ids_by_company(thesis_payload: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, set[str]] = {}
    for stage in thesis_payload.get("cascade", []):
        theme_id = _thesis_theme_id_from_stage_id(stage["id"])
        for company_id in stage.get("company_ids", []):
            result.setdefault(company_id, set()).add(theme_id)
    return {company_id: sorted(theme_ids) for company_id, theme_ids in result.items()}


def _thesis_theme_ids_by_bottleneck(thesis_payload: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, set[str]] = {}
    for stage in thesis_payload.get("cascade", []):
        theme_id = _thesis_theme_id_from_stage_id(stage["id"])
        name = stage.get("name", "")
        for key in {_slugify(name), name, name.lower().replace(" ", "_")}:
            result.setdefault(str(key), set()).add(theme_id)
    aliases = {
        "memory": "memory-supercycle",
        "n3_logic": "n3-logic-wafers",
        "optical": "pluggable-optics-scale-out",
        "pluggable_optics": "pluggable-optics-scale-out",
        "cpo_next": "co-packaged-optics-cpo-scale-up",
        "copper_signal_integrity": "co-packaged-optics-cpo-scale-up",
        "euv": "euv-tools",
        "power": "power-dc-buildout",
        "gpu_cloud": "power-dc-buildout",
        "foundry": "n3-logic-wafers",
    }
    for alias, target_slug in aliases.items():
        theme_id = f"thesis-theme:{target_slug}"
        result.setdefault(alias, set()).add(theme_id)
    return {key: sorted(value) for key, value in result.items()}


def _theme_status(value: Any) -> str:
    text = str(value or "").lower()
    if text == "active":
        return "active"
    if text in {"next", "watch"}:
        return "watch"
    return "inactive"


def _proposal_theme_ids(proposal: dict[str, Any], thesis_theme_ids_by_name: dict[str, str]) -> list[str]:
    text = _search_text(proposal.get("target_sections", []), proposal.get("proposal", ""))
    result: set[str] = set()
    for name, theme_id in thesis_theme_ids_by_name.items():
        if _slugify(name).replace("-", " ") in text or name.lower() in text:
            result.add(theme_id)
    return sorted(result)


def _proposal_company_ids(
    proposal: dict[str, Any],
    thesis_payload: dict[str, Any],
    companies_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    text = _search_text(proposal)
    result: set[str] = set()
    ticker_to_company = {
        company.get("ticker"): company_id
        for company_id, company in companies_by_id.items()
        if company.get("ticker")
    }
    for ticker in TICKER_RE.findall(text.upper()):
        company_id = ticker_to_company.get(ticker)
        if company_id:
            result.add(company_id)
    for stage in thesis_payload.get("cascade", []):
        if stage.get("name", "").lower() in text or _slugify(stage.get("name", "")).replace("-", " ") in text:
            for company_id in stage.get("company_ids", []):
                if company_id in companies_by_id:
                    result.add(company_id)
    return sorted(result)


def _base_row(
    *,
    row_id: str,
    row_type: str,
    title: str,
    summary: str,
    company_ids: list[str],
    primary_company_id: str | None,
    source_channel_id: str,
    source_document_ids: list[str],
    source_paths: list[str],
    thesis_theme_ids: list[str],
    period: dict[str, Any],
    timeline: dict[str, Any],
    graph_eligibility: dict[str, Any],
    lifecycle_state: str,
    ui_badges: list[str],
    search_parts: list[Any],
) -> dict[str, Any]:
    return {
        "id": row_id,
        "row_type": row_type,
        "title": title,
        "summary": summary,
        "company_ids": sorted(company_ids),
        "primary_company_id": primary_company_id,
        "source_channel_id": source_channel_id,
        "source_document_ids": sorted(source_document_ids),
        "source_paths": sorted(source_paths),
        "thesis_theme_ids": sorted(thesis_theme_ids),
        "search_text": _search_text(row_id, row_type, title, summary, company_ids, source_channel_id, source_paths, thesis_theme_ids, search_parts),
        "period": period,
        "timeline": timeline,
        "graph_eligibility": graph_eligibility,
        "lifecycle_state": lifecycle_state,
        "ui_badges": ui_badges,
    }


def _position_type(value: Any) -> str:
    text = str(value or "equity").lower()
    if text in {"common", "equity", "shares"}:
        return "equity"
    if text in {"call", "put"}:
        return text
    return "other"


def _change_vs_prior(value: Any) -> str:
    text = str(value or "").lower()
    if text == "new":
        return "new"
    if text in {"unchanged", "flat"}:
        return "unchanged"
    if text.startswith("+"):
        return "increased"
    if text.startswith("-"):
        return "decreased"
    return "unknown"


def _impact_direction(value: Any) -> str:
    text = str(value or "").lower()
    if text in {"confirms", "supports", "supported"}:
        return "supports"
    if text in {"contradicts", "contradict"}:
        return "contradicts"
    if text in {"mixed"}:
        return "mixed"
    if text in {"proposed"}:
        return "proposed"
    return "signal"


def _claim_lifecycle_state(value: Any) -> str:
    text = str(value or "pending").lower()
    if text in {"confirmed", "verified"}:
        return "verified"
    if text in {"missed", "disconfirmed"}:
        return "disconfirmed"
    if text == "stale":
        return "stale"
    return "pending_verification"


def _sort_index(index: dict[str, list[str]]) -> dict[str, list[str]]:
    return {key: sorted(set(values)) for key, values in sorted(index.items())}


def _columns(items: list[tuple[str, str]]) -> list[dict[str, Any]]:
    return [
        {"key": key, "label": label, "sortable": True, "visible_by_default": True}
        for key, label in items
    ]


def _row_table_view(view_id: str, label: str, row_type: str, row_ids: list[str], columns: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "id": view_id,
        "label": label,
        "entity_type": "row",
        "row_type": row_type,
        "row_ids": sorted(row_ids),
        "source_document_ids": [],
        "columns": _columns(columns),
        "default_sort": {"key": "timeline.sort_date", "direction": "desc", "nulls": "last"},
    }
