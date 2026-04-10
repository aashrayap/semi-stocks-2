"""Base interface for curated data sources."""

from abc import ABC, abstractmethod

from engine.paths import DATA_DIR


class Source(ABC):
    """A hand-picked source of investment research data.

    Each source reads from structured YAML files in canonical/20-data/sources/<name>/
    and provides methods to query positions, signals, and diffs.
    """

    @abstractmethod
    def name(self) -> str:
        """Short identifier (e.g. 'leopold', 'baker', 'semianalysis')."""
        ...

    @abstractmethod
    def latest(self) -> dict:
        """Return the most recent data snapshot for this source."""
        ...

    @abstractmethod
    def tickers(self) -> list[str]:
        """Return all tickers this source currently has exposure to."""
        ...

    @abstractmethod
    def lookup(self, ticker: str) -> dict | None:
        """Look up a specific ticker in this source. Returns None if not held."""
        ...
