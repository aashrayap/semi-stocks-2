"""13F fund source — reads quarterly YAML filings for Leopold and Baker."""

from pathlib import Path

import yaml

from engine.sources.base import DATA_DIR, Source


class Fund13FSource(Source):
    """Reads 13F position data from canonical/20-data/sources/<fund_name>/."""

    def __init__(self, fund_name: str):
        self._name = fund_name
        self._dir = DATA_DIR / "sources" / fund_name
        self._data: dict | None = None

    def name(self) -> str:
        return self._name

    def _load_latest(self) -> dict:
        """Find and load the most recent quarterly YAML file."""
        if self._data is not None:
            return self._data

        files = sorted(self._dir.glob("q*.yaml"), reverse=True)
        if not files:
            return {}

        with open(files[0]) as f:
            self._data = yaml.safe_load(f)
        return self._data

    def latest(self) -> dict:
        return self._load_latest()

    def all_quarters(self) -> list[dict]:
        """Load all quarterly filings, newest first."""
        results = []
        for f in sorted(self._dir.glob("q*.yaml"), reverse=True):
            with open(f) as fh:
                results.append(yaml.safe_load(fh))
        return results

    def tickers(self) -> list[str]:
        data = self._load_latest()
        seen = []
        for position in data.get("positions", []):
            ticker = position["ticker"]
            if ticker not in seen:
                seen.append(ticker)
        return seen

    def positions_for_ticker(self, ticker: str) -> list[dict]:
        """Return all legs for a ticker in the latest filing."""
        data = self._load_latest()
        return [p for p in data.get("positions", []) if p["ticker"] == ticker]

    def lookup(self, ticker: str) -> dict | None:
        positions = self.positions_for_ticker(ticker)
        if not positions:
            return None
        if len(positions) == 1:
            return positions[0]

        combined = positions[0].copy()
        combined["value"] = sum(p.get("value", 0) for p in positions)
        combined["pct_portfolio"] = sum(p.get("pct_portfolio", 0) for p in positions)
        combined["types"] = [p.get("type", "common") for p in positions]
        combined["type"] = "+".join(combined["types"])
        combined["legs"] = positions

        notes = []
        for position in positions:
            note = position.get("notes")
            if note and note not in notes:
                notes.append(note)
        if notes:
            combined["notes"] = " | ".join(notes)

        return combined

    def exits(self) -> list[dict]:
        """Return positions exited in the most recent quarter."""
        data = self._load_latest()
        return data.get("exits", [])

    def by_bottleneck(self, bottleneck: str) -> list[dict]:
        """Return all positions mapped to a specific bottleneck."""
        data = self._load_latest()
        return [p for p in data.get("positions", []) if p.get("bottleneck") == bottleneck]

    def summary(self) -> dict:
        """Return fund-level metadata."""
        data = self._load_latest()
        return {
            "entity": data.get("entity"),
            "quarter": data.get("quarter"),
            "filed": data.get("filed"),
            "aum": data.get("aum"),
            "positions_count": data.get("positions_count"),
            "top5_concentration": data.get("top5_concentration"),
        }
