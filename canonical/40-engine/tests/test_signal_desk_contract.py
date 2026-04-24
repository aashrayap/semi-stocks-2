#!/usr/bin/env python3
"""Contract checks for generated Signal Desk data."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

STAGE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = STAGE_DIR.parents[1]
if str(STAGE_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE_DIR))

from engine.site_data import (  # noqa: E402
    _filter_claims_for_site_data_gate,
    _filter_rows_for_emitted_closure,
    _filter_signals_for_site_data_gate,
    _filter_source_documents_for_evidence_refs,
    build_site_data,
    validate_reader_site_data_gate,
)


class SignalDeskContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build_site_data(validate=True)
        site_data_dir = REPO_ROOT / "canonical" / "site-data"
        cls.signal_desk = json.loads((site_data_dir / "signal_desk.json").read_text(encoding="utf-8"))
        cls.site_data = {
            name: json.loads((site_data_dir / f"{name}.json").read_text(encoding="utf-8"))
            for name in ("companies", "signals", "claims", "entities", "search", "graph", "reports", "thesis", "signal_desk")
        }

    def test_trace_is_parked(self) -> None:
        desk = self.signal_desk
        self.assertEqual(desk["features"]["trace"]["status"], "parked")
        self.assertFalse(desk["features"]["trace"]["visible"])
        self.assertFalse(desk["quality"]["trace_ready"])
        self.assertEqual(desk["graph"]["mode"], "contextual_evidence")

    def test_graph_support_families_are_mvp_only(self) -> None:
        desk = self.signal_desk
        self.assertEqual(
            set(desk["facets"]["graph_support_families"]),
            {"co_position", "shared_signal"},
        )
        for edge in desk["graph"]["edges"]:
            self.assertFalse(edge["trace_eligible"])
            self.assertEqual(edge["company_ids"], sorted(edge["company_ids"]))
            for support in edge["support"]:
                self.assertIn(support["family"], {"co_position", "shared_signal"})

    def test_admitted_universe_is_reader_gate(self) -> None:
        desk = self.signal_desk
        admitted_company_ids = set(desk["quality"]["admitted_universe"]["company_ids"])
        company_ids = {company["id"] for company in desk["companies"]}
        self.assertEqual(company_ids, admitted_company_ids)
        for row in desk["rows"]:
            self.assertTrue(set(row["company_ids"]) <= admitted_company_ids, row["id"])
        for source_document in desk["source_documents"]:
            self.assertTrue(set(source_document["company_ids"]) <= admitted_company_ids, source_document["id"])
        for node in desk["graph"]["nodes"]:
            self.assertIn(node["company_id"], admitted_company_ids, node["id"])
        for edge in desk["graph"]["edges"]:
            self.assertTrue(set(edge["company_ids"]) <= admitted_company_ids, edge["id"])

    def test_position_leg_counts_are_gate_filtered(self) -> None:
        counts = self.signal_desk["quality"]["position_leg_counts"]
        for source_name in ("baker", "leopold"):
            self.assertLessEqual(counts[source_name]["emitted"], counts[source_name]["source"])
        positions = [row for row in self.signal_desk["rows"] if row["row_type"] == "position"]
        by_fund = {}
        for row in positions:
            by_fund[row["fund_id"]] = by_fund.get(row["fund_id"], 0) + 1
        self.assertEqual(by_fund.get("baker", 0), counts["baker"]["emitted"])
        self.assertEqual(by_fund.get("leopold", 0), counts["leopold"]["emitted"])

    def test_rows_have_source_documents_and_timeline(self) -> None:
        source_doc_ids = {doc["id"] for doc in self.signal_desk["source_documents"]}
        company_ids = {company["id"] for company in self.signal_desk["companies"]}
        for row in self.signal_desk["rows"]:
            self.assertTrue(row["source_document_ids"], row["id"])
            self.assertTrue(row["source_paths"], row["id"])
            self.assertTrue(row["company_ids"], row["id"])
            self.assertIn("timeline", row, row["id"])
            for doc_id in row["source_document_ids"]:
                self.assertIn(doc_id, source_doc_ids, row["id"])
            for company_id in row["company_ids"]:
                self.assertIn(company_id, company_ids, row["id"])

    def test_claims_do_not_create_graph_edges(self) -> None:
        for row in self.signal_desk["rows"]:
            if row["row_type"] == "claim":
                self.assertFalse(row["graph_eligibility"]["eligible"], row["id"])
                self.assertIsNone(row["graph_eligibility"]["family"], row["id"])

    def test_proposals_do_not_appear_in_main_feed(self) -> None:
        self.assertNotIn("proposal", self.signal_desk["facets"]["row_types"])
        self.assertNotIn(
            "source-channel:pending-proposals",
            {channel["id"] for channel in self.signal_desk["facets"]["source_channels"]},
        )
        self.assertNotIn("proposals", self.signal_desk["tables"]["view_order"])
        self.assertNotIn("proposals", self.signal_desk["tables"]["views"])
        for row in self.signal_desk["rows"]:
            self.assertNotEqual(row["row_type"], "proposal", row["id"])
        for source_document in self.signal_desk["source_documents"]:
            self.assertNotEqual(source_document["document_kind"], "thesis_proposal", source_document["id"])

    def test_source_documents_are_filtered_to_evidence_refs(self) -> None:
        source_documents = [
            {"id": "source-doc:accepted"},
            {"id": "source-doc:candidate-only"},
        ]
        admitted_universe = {
            "accepted_proposal_ids": ["proposal:accepted"],
            "evidence_source_document_ids": ["source-doc:accepted"],
        }
        self.assertEqual(
            _filter_source_documents_for_evidence_refs(source_documents, admitted_universe),
            [{"id": "source-doc:accepted"}],
        )

    def test_rows_are_filtered_to_emitted_company_and_evidence_closure(self) -> None:
        rows = [
            {"id": "row:accepted", "company_ids": ["company:accepted"], "source_document_ids": ["source-doc:accepted"]},
            {"id": "row:wrong-doc", "company_ids": ["company:accepted"], "source_document_ids": ["source-doc:candidate-only"]},
            {"id": "row:wrong-company", "company_ids": ["company:candidate-only"], "source_document_ids": ["source-doc:accepted"]},
        ]
        self.assertEqual(
            _filter_rows_for_emitted_closure(
                rows=rows,
                company_ids={"company:accepted"},
                source_document_ids={"source-doc:accepted"},
            ),
            [{"id": "row:accepted", "company_ids": ["company:accepted"], "source_document_ids": ["source-doc:accepted"]}],
        )

    def test_top_level_site_data_uses_same_gate(self) -> None:
        validate_reader_site_data_gate(self.site_data)
        admitted_company_ids = set(self.signal_desk["quality"]["admitted_universe"]["company_ids"])
        self.assertEqual({company["id"] for company in self.site_data["companies"]}, admitted_company_ids)
        self.assertNotIn("proposals", self.site_data["thesis"])
        for row in self.site_data["search"]:
            self.assertFalse(row["type"].startswith("page:"), row["id"])
        for ticker, meta in self.site_data["thesis"].get("ticker_map", {}).items():
            self.assertIn(meta.get("company_id"), admitted_company_ids, ticker)

    def test_top_level_claim_and_signal_filters_use_evidence_refs(self) -> None:
        admitted_universe = {
            "company_ids": ["company:ACPT"],
            "evidence_source_document_ids": ["source-doc:company:acpt:q4-2026", "source-doc:semianalysis:signals"],
        }
        claims = [
            {"id": "claim:accepted", "company_id": "company:ACPT", "ticker": "ACPT", "quarter": "Q4 2026"},
            {"id": "claim:wrong-doc", "company_id": "company:ACPT", "ticker": "ACPT", "quarter": "Q3 2026"},
            {"id": "claim:wrong-company", "company_id": "company:candidate", "ticker": "CAND", "quarter": "Q4 2026"},
        ]
        signals = [
            {"id": "signal:accepted", "kind": "company_thesis_signal", "ticker": "ACPT", "quarter": "Q4 2026"},
            {"id": "signal:wrong-doc", "kind": "company_thesis_signal", "ticker": "ACPT", "quarter": "Q3 2026"},
            {"id": "signal:mixed", "kind": "semianalysis_signal", "tickers": ["ACPT", "CAND"]},
        ]
        self.assertEqual(
            [claim["id"] for claim in _filter_claims_for_site_data_gate(claims, admitted_universe)],
            ["claim:accepted"],
        )
        self.assertEqual(
            _filter_signals_for_site_data_gate(signals, admitted_universe),
            [
                {"id": "signal:accepted", "kind": "company_thesis_signal", "ticker": "ACPT", "quarter": "Q4 2026"},
                {"id": "signal:mixed", "kind": "semianalysis_signal", "tickers": ["ACPT"]},
            ],
        )

    def test_table_views_reference_ids_only(self) -> None:
        views = self.signal_desk["tables"]["views"]
        for view in views.values():
            self.assertIn("columns", view)
            self.assertIn("default_sort", view)
            self.assertNotIn("rows", view)
            self.assertNotIn("documents", view)
        self.assertEqual(self.signal_desk["tables"]["default_view_id"], "signals")


if __name__ == "__main__":
    unittest.main()
