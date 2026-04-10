"""Filesystem paths for the canonical engine package."""

from pathlib import Path

ENGINE_PACKAGE_DIR = Path(__file__).resolve().parent
ENGINE_STAGE_DIR = ENGINE_PACKAGE_DIR.parent
CANONICAL_ROOT = ENGINE_STAGE_DIR.parent
REPO_ROOT = CANONICAL_ROOT.parent

WIKI_DIR = CANONICAL_ROOT / "10-wiki"
DATA_DIR = CANONICAL_ROOT / "20-data"
THESIS_PATH = CANONICAL_ROOT / "30-thesis" / "thesis.yaml"
REPORTS_DIR = CANONICAL_ROOT / "50-reports"
