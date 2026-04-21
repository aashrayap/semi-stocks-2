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

from engine.site_data import build_site_data  # noqa: E402


class SignalDeskContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build_site_data(validate=True)
        path = REPO_ROOT / "canonical" / "site-data" / "signal_desk.json"
        cls.signal_desk = json.loads(path.read_text(encoding="utf-8"))

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

    def test_position_leg_counts_match_source(self) -> None:
        counts = self.signal_desk["quality"]["position_leg_counts"]
        self.assertEqual(counts["baker"], {"source": 18, "emitted": 18})
        self.assertEqual(counts["leopold"], {"source": 10, "emitted": 10})
        positions = [row for row in self.signal_desk["rows"] if row["row_type"] == "position"]
        by_fund = {}
        for row in positions:
            by_fund[row["fund_id"]] = by_fund.get(row["fund_id"], 0) + 1
        self.assertEqual(by_fund["baker"], 18)
        self.assertEqual(by_fund["leopold"], 10)

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

    def test_claims_and_proposals_do_not_create_graph_edges(self) -> None:
        for row in self.signal_desk["rows"]:
            if row["row_type"] in {"claim", "proposal"}:
                self.assertFalse(row["graph_eligibility"]["eligible"], row["id"])
                self.assertIsNone(row["graph_eligibility"]["family"], row["id"])

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
