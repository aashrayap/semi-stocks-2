"""SemiAnalysis source — reads curated signals from YAML."""

from pathlib import Path

import yaml

from engine.sources.base import DATA_DIR, Source


class SemiAnalysisSource(Source):
    """Reads SemiAnalysis signal data from canonical/20-data/sources/semianalysis/signals.yaml."""

    def __init__(self):
        self._path = DATA_DIR / "sources" / "semianalysis" / "signals.yaml"
        self._data: dict | None = None

    def name(self) -> str:
        return "semianalysis"

    def _load(self) -> dict:
        if self._data is not None:
            return self._data

        if not self._path.exists():
            return {}

        with open(self._path) as f:
            self._data = yaml.safe_load(f)
        return self._data

    def latest(self) -> dict:
        return self._load()

    def tickers(self) -> list[str]:
        """Return all tickers mentioned across signals."""
        data = self._load()
        seen = []
        for signal in data.get("signals", []):
            for t in signal.get("tickers", []):
                if t not in seen:
                    seen.append(t)
        return seen

    def lookup(self, ticker: str) -> dict | None:
        """Return all signals mentioning a specific ticker."""
        data = self._load()
        relevant = [s for s in data.get("signals", []) if ticker in s.get("tickers", [])]
        if not relevant:
            return None
        return {"ticker": ticker, "signals": relevant}

    def signals(self, bottleneck: str | None = None) -> list[dict]:
        """Return signals, optionally filtered by bottleneck."""
        data = self._load()
        all_signals = data.get("signals", [])
        if bottleneck is None:
            return all_signals
        return [s for s in all_signals if s.get("bottleneck") == bottleneck]

    def recent(self, n: int = 5) -> list[dict]:
        """Return the N most recent signals."""
        data = self._load()
        signals = data.get("signals", [])
        return sorted(signals, key=lambda s: s.get("date", ""), reverse=True)[:n]

    def media(self) -> list[dict]:
        """Return media appearance claims."""
        data = self._load()
        return data.get("media", [])
