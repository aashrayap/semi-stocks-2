"""Shared runtime path helpers for agent scripts."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    return REPO_ROOT


def _stage_root(base: Path, stage: str, legacy: str) -> Path:
    base = base.resolve()
    canonical = base / "canonical" / stage
    if canonical.exists():
        return canonical
    return base / legacy


def wiki_root(base: Path = REPO_ROOT) -> Path:
    return _stage_root(base, "10-wiki", "wiki")


def data_root(base: Path = REPO_ROOT) -> Path:
    return _stage_root(base, "20-data", "data")


def thesis_path(base: Path = REPO_ROOT) -> Path:
    base = base.resolve()
    canonical = base / "canonical" / "30-thesis" / "thesis.yaml"
    if canonical.exists():
        return canonical
    legacy_data = base / "data" / "thesis.yaml"
    if legacy_data.exists():
        return legacy_data
    return base / "thesis.yaml"


def engine_stage(base: Path = REPO_ROOT) -> Path:
    return _stage_root(base, "40-engine", "engine")


def reports_root(base: Path = REPO_ROOT) -> Path:
    return _stage_root(base, "50-reports", "reports")
