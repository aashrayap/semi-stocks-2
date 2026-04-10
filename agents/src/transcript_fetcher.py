#!/usr/bin/env python3
"""Transcript fetcher agent.

Fetches earnings call transcripts for tracked companies using a tiered
strategy: q4cdn PDF (Tier 1) -> IR page scrape (Tier 2) -> Motley Fool
fallback (Tier 3).

CODE fetches the data (cheap, repeatable). An agent or human does the
analysis (expensive, smart).

Usage:
    python agents/src/transcript_fetcher.py --ticker TSM --quarter Q1_2026
    python agents/src/transcript_fetcher.py --ticker TSM --quarter Q1_2026 --source motley_fool
    python agents/src/transcript_fetcher.py --all-due
    python agents/src/transcript_fetcher.py --all-due --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, quote

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Optional dependencies — graceful degradation
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from runtime_paths import repo_root, thesis_path


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent          # agents/src/
AGENTS_DIR = SCRIPT_DIR.parent                        # agents/
REPO_ROOT = repo_root()                               # semi-stocks/

THESIS_PATH = thesis_path(REPO_ROOT)
AGENT_CONFIG_PATH = AGENTS_DIR / "config.yaml"
DRAFTS_EARNINGS_DIR = AGENTS_DIR / "drafts" / "earnings"
STATE_DIR = AGENTS_DIR / "state"
LOGS_DIR = AGENTS_DIR / "logs"

STATE_FILE = STATE_DIR / "transcripts.yaml"

USER_AGENT = "semi-stocks-transcript-fetcher/1.0 (research tool; contact: github.com/ashdasher777)"
REQUEST_DELAY = 1.0  # seconds between HTTP requests
MOTLEY_FOOL_LISTING_URL = "https://www.fool.com/earnings-call-transcripts/"


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logging to both file and stderr."""
    logger = logging.getLogger("transcript_fetcher")
    logger.setLevel(logging.DEBUG)

    # File handler — monthly log file
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"transcript-fetcher-{date.today().strftime('%Y-%m')}.log"
    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)

    # Stderr handler — INFO and above
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(sh)

    return logger


log = setup_logging()


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict | list | None:
    """Load a YAML file, returning None if it doesn't exist or is empty."""
    if not path.exists():
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_yaml(path: Path, data: Any) -> None:
    """Write data to a YAML file, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def get_agent_config() -> dict:
    """Load agent fleet config."""
    cfg = load_yaml(AGENT_CONFIG_PATH)
    return cfg if cfg else {}


def get_transcript_sources() -> dict:
    """Load transcript_sources from agent config."""
    cfg = get_agent_config()
    return cfg.get("transcript_sources", {})


def get_deep_dive_tickers() -> list[str]:
    """Get deep-dive ticker list from agent config."""
    cfg = get_agent_config()
    return cfg.get("deep_dive", [])


def get_ticker_map() -> dict[str, dict]:
    """Load ticker_map from the canonical thesis file."""
    thesis = load_yaml(THESIS_PATH)
    if not thesis:
        return {}
    return thesis.get("ticker_map", {})


def get_transcript_state() -> dict:
    """Load the current transcript tracking state."""
    state = load_yaml(STATE_FILE)
    return state if state else {}


def save_transcript_state(state: dict) -> None:
    """Persist the transcript tracking state."""
    save_yaml(STATE_FILE, state)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_last_request_time: float = 0.0


def _rate_limit() -> None:
    """Enforce minimum delay between HTTP requests."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - elapsed)
    _last_request_time = time.time()


def _create_ssl_context() -> ssl.SSLContext:
    """Create an SSL context that works on macOS."""
    ctx = ssl.create_default_context()
    return ctx


def fetch_url(url: str, timeout: int = 30) -> bytes:
    """Fetch a URL with rate limiting and polite user-agent.

    Returns raw bytes. Raises on HTTP/network errors.
    """
    _rate_limit()
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/pdf,*/*",
    })
    log.debug(f"Fetching: {url}")
    ctx = _create_ssl_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()


def fetch_url_text(url: str, timeout: int = 30, encoding: str = "utf-8") -> str:
    """Fetch a URL and return decoded text."""
    raw = fetch_url(url, timeout=timeout)
    return raw.decode(encoding, errors="replace")


# ---------------------------------------------------------------------------
# HTML parsing (stdlib fallback)
# ---------------------------------------------------------------------------

class LinkExtractor(HTMLParser):
    """Extract all <a> tags with href attributes."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []  # {"href": ..., "text": ...}
        self._current_link: dict[str, str] | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            attr_dict = dict(attrs)
            href = attr_dict.get("href", "")
            if href:
                self._current_link = {"href": href, "text": ""}
                self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_link is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current_link is not None:
            self._current_link["text"] = " ".join(self._current_text).strip()
            self.links.append(self._current_link)
            self._current_link = None
            self._current_text = []


class ArticleTextExtractor(HTMLParser):
    """Extract text content from an HTML article.

    Designed for Motley Fool transcript pages where transcript content
    lives inside the article body. Strips tags, preserves paragraph breaks.
    """

    # Tags whose content we skip entirely
    SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth: int = 0
        self._in_article: bool = False
        self._article_depth: int = 0
        self._tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)

        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return

        if self._skip_depth > 0:
            return

        # Track article entry
        if tag == "article":
            self._in_article = True
            self._article_depth += 1

        # For Motley Fool, also look for content divs
        classes = (attr_dict.get("class") or "").lower()
        if tag == "div" and any(c in classes for c in [
            "article-body", "article-content", "transcript-content",
            "tailwind-article-body",
        ]):
            self._in_article = True
            self._article_depth += 1

        self._tag_stack.append(tag)

        # Add paragraph breaks
        if tag in ("p", "br", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return

        if tag in ("article",) or (tag == "div" and self._article_depth > 0):
            if self._in_article:
                self._article_depth = max(0, self._article_depth - 1)
                if self._article_depth == 0:
                    self._in_article = False

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_article:
            self.parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self.parts)
        # Collapse whitespace within lines, preserve paragraph breaks
        paragraphs = re.split(r"\n\s*\n", raw)
        cleaned = []
        for p in paragraphs:
            line = " ".join(p.split()).strip()
            if line:
                cleaned.append(line)
        return "\n\n".join(cleaned)


def extract_links(html: str, base_url: str = "") -> list[dict[str, str]]:
    """Extract links from HTML. Returns list of {"href": ..., "text": ...}."""
    parser = LinkExtractor()
    parser.feed(html)
    if base_url:
        for link in parser.links:
            if link["href"] and not link["href"].startswith(("http://", "https://")):
                link["href"] = urljoin(base_url, link["href"])
    return parser.links


def extract_article_text(html: str) -> str:
    """Extract clean article text from HTML page."""
    if HAS_BS4:
        return _extract_article_text_bs4(html)
    return _extract_article_text_stdlib(html)


def _extract_article_text_bs4(html: str) -> str:
    """Extract article text using BeautifulSoup (higher fidelity)."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()

    # Try specific content containers first (Motley Fool patterns)
    content = None
    for selector in [
        {"class": re.compile(r"tailwind-article-body|article-body|article-content|transcript-content")},
        "article",
    ]:
        if isinstance(selector, dict):
            content = soup.find("div", selector)
        else:
            content = soup.find(selector)
        if content:
            break

    if not content:
        content = soup.find("body") or soup

    text = content.get_text(separator="\n")
    # Clean up
    paragraphs = re.split(r"\n\s*\n", text)
    cleaned = []
    for p in paragraphs:
        line = " ".join(p.split()).strip()
        if line:
            cleaned.append(line)
    return "\n\n".join(cleaned)


def _extract_article_text_stdlib(html: str) -> str:
    """Extract article text using stdlib html.parser."""
    parser = ArticleTextExtractor()
    parser.feed(html)
    text = parser.get_text()

    # If article extraction found nothing, fall back to full page body extraction
    if len(text.strip()) < 200:
        log.debug("Article extraction yielded little text, falling back to full body")
        return _extract_full_body_text(html)

    return text


def _extract_full_body_text(html: str) -> str:
    """Last-resort extraction: strip all tags, keep text."""

    class BodyExtractor(HTMLParser):
        SKIP = {"script", "style", "nav", "header", "footer", "aside", "noscript", "svg"}

        def __init__(self):
            super().__init__()
            self.parts: list[str] = []
            self._skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in self.SKIP:
                self._skip += 1
            if tag in ("p", "br", "h1", "h2", "h3", "h4", "h5", "h6", "div"):
                self.parts.append("\n\n")

        def handle_endtag(self, tag):
            if tag in self.SKIP:
                self._skip = max(0, self._skip - 1)

        def handle_data(self, data):
            if self._skip == 0:
                self.parts.append(data)

        def get_text(self):
            raw = "".join(self.parts)
            paragraphs = re.split(r"\n\s*\n", raw)
            cleaned = [" ".join(p.split()).strip() for p in paragraphs if p.strip()]
            return "\n\n".join(cleaned)

    parser = BodyExtractor()
    parser.feed(html)
    return parser.get_text()


# ---------------------------------------------------------------------------
# PDF handling
# ---------------------------------------------------------------------------

def pdf_to_text(pdf_bytes: bytes, ticker: str, quarter: str) -> tuple[str, str]:
    """Convert PDF bytes to text.

    Returns (text, fidelity) where fidelity is "full_transcript" if pdfplumber
    worked, or "pdf_saved_raw" if we just saved the file for manual conversion.
    """
    if HAS_PDFPLUMBER:
        try:
            import io
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                if pages:
                    return "\n\n".join(pages), "full_transcript"
                else:
                    log.warning("pdfplumber extracted no text from PDF")
        except Exception as e:
            log.warning(f"pdfplumber failed: {e}")

    # Fallback: save the raw PDF and note it needs manual conversion
    pdf_path = DRAFTS_EARNINGS_DIR / f"{ticker}-{quarter}-transcript.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.write_bytes(pdf_bytes)
    log.info(f"Saved raw PDF to {pdf_path.relative_to(REPO_ROOT)} (needs manual text extraction)")
    return (
        f"[PDF saved to {pdf_path.relative_to(REPO_ROOT)}. "
        f"Install pdfplumber (`pip install pdfplumber`) for automatic text extraction.]",
        "pdf_saved_raw",
    )


# ---------------------------------------------------------------------------
# Tier 1: q4cdn PDF fetch
# ---------------------------------------------------------------------------

def fetch_q4cdn(ticker: str, quarter: str, config: dict) -> dict | None:
    """Fetch transcript from q4cdn (Tier 1).

    Strategy: fetch the events/IR page, scan for PDF links containing
    "transcript" keywords, download the matching PDF, convert to text.

    Args:
        ticker: e.g. "NVDA"
        quarter: e.g. "Q1_2026"
        config: q4cdn config for this ticker (cdn_id, events_page)

    Returns:
        dict with keys: text, source, source_url, fidelity
        or None if fetch failed.
    """
    events_url = config.get("events_page")
    cdn_id = config.get("cdn_id", "")
    if not events_url:
        log.debug(f"[{ticker}] No events_page configured for q4cdn")
        return None

    log.info(f"[{ticker}] Tier 1: Fetching q4cdn events page: {events_url}")

    try:
        html = fetch_url_text(events_url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        log.warning(f"[{ticker}] Failed to fetch q4cdn events page: {e}")
        return None

    # Parse quarter string like "Q1_2026" -> ("Q1", "2026", 1)
    q_label, q_year = _parse_quarter(quarter)
    if not q_label:
        log.warning(f"[{ticker}] Could not parse quarter: {quarter}")
        return None

    # Extract all links and find transcript PDFs
    links = extract_links(html, base_url=events_url)
    transcript_links = _find_transcript_links(links, ticker, q_label, q_year, cdn_id)

    if not transcript_links:
        log.info(f"[{ticker}] No transcript PDF found on q4cdn events page for {quarter}")
        return None

    # Try the best-scoring link
    for link in transcript_links:
        pdf_url = link["href"]
        log.info(f"[{ticker}] Downloading PDF: {pdf_url}")
        try:
            pdf_bytes = fetch_url(pdf_url, timeout=60)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            log.warning(f"[{ticker}] Failed to download PDF: {e}")
            continue

        text, fidelity = pdf_to_text(pdf_bytes, ticker, quarter)
        return {
            "text": text,
            "source": "q4cdn",
            "source_url": pdf_url,
            "fidelity": fidelity,
        }

    return None


# ---------------------------------------------------------------------------
# Tier 2: IR page scrape
# ---------------------------------------------------------------------------

def fetch_ir_scrape(ticker: str, quarter: str, config: dict) -> dict | None:
    """Fetch transcript from company IR page (Tier 2).

    Strategy: fetch the transcript/events page, scan for PDF links containing
    "transcript" keywords, download the matching PDF, convert to text.

    Args:
        ticker: e.g. "TSM"
        quarter: e.g. "Q1_2026"
        config: ir_scrape config for this ticker

    Returns:
        dict with keys: text, source, source_url, fidelity
        or None if fetch failed.
    """
    # Try transcript_page first, then events_page
    page_url = config.get("transcript_page") or config.get("events_page")
    if not page_url:
        log.debug(f"[{ticker}] No page URL configured for ir_scrape")
        return None

    log.info(f"[{ticker}] Tier 2: Fetching IR page: {page_url}")

    try:
        html = fetch_url_text(page_url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        log.warning(f"[{ticker}] Failed to fetch IR page: {e}")
        return None

    q_label, q_year = _parse_quarter(quarter)
    if not q_label:
        log.warning(f"[{ticker}] Could not parse quarter: {quarter}")
        return None

    links = extract_links(html, base_url=page_url)
    transcript_links = _find_transcript_links(links, ticker, q_label, q_year)

    if not transcript_links:
        log.info(f"[{ticker}] No transcript link found on IR page for {quarter}")
        return None

    for link in transcript_links:
        link_url = link["href"]

        # If it's a PDF, download directly
        if link_url.lower().endswith(".pdf") or "pdf" in link_url.lower():
            log.info(f"[{ticker}] Downloading PDF: {link_url}")
            try:
                pdf_bytes = fetch_url(link_url, timeout=60)
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                log.warning(f"[{ticker}] Failed to download PDF: {e}")
                continue

            text, fidelity = pdf_to_text(pdf_bytes, ticker, quarter)
            return {
                "text": text,
                "source": "ir_scrape",
                "source_url": link_url,
                "fidelity": fidelity,
            }

        # If it's an HTML page, try to extract text from it
        log.info(f"[{ticker}] Fetching transcript page: {link_url}")
        try:
            transcript_html = fetch_url_text(link_url)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            log.warning(f"[{ticker}] Failed to fetch transcript page: {e}")
            continue

        text = extract_article_text(transcript_html)
        if len(text.strip()) > 500:  # Sanity check — transcripts are long
            return {
                "text": text,
                "source": "ir_scrape",
                "source_url": link_url,
                "fidelity": "full_transcript",
            }
        else:
            log.debug(f"[{ticker}] Extracted text too short ({len(text)} chars), skipping")

    return None


# ---------------------------------------------------------------------------
# Tier 3: Motley Fool fallback
# ---------------------------------------------------------------------------

def fetch_motley_fool(ticker: str, quarter: str, fool_config: dict) -> dict | None:
    """Fetch transcript from Motley Fool (Tier 3).

    Strategy: Construct the expected URL pattern, or search the earnings
    call transcripts section. Extract the article text.

    Args:
        ticker: e.g. "TSM"
        quarter: e.g. "Q1_2026"
        fool_config: motley_fool config section

    Returns:
        dict with keys: text, source, source_url, fidelity
        or None if fetch failed.
    """
    base_url = fool_config.get("base_url", "https://www.fool.com/earnings/call-transcripts/")
    slugs = fool_config.get("slugs", {})
    slug = slugs.get(ticker)

    if not slug:
        log.info(f"[{ticker}] No Motley Fool slug configured")
        return None

    q_label, q_year = _parse_quarter(quarter)
    if not q_label:
        log.warning(f"[{ticker}] Could not parse quarter: {quarter}")
        return None

    q_num = q_label.replace("Q", "")

    # Strategy 1: scan recent pages from the real earnings transcript listing.
    # Motley Fool does not expose per-ticker transcript pages at ?ticker=...
    # and recent transcripts usually remain visible in the paginated index.
    log.info(f"[{ticker}] Tier 3: Searching Motley Fool for {ticker} {quarter} transcript")
    transcript_url = None

    try:
        transcript_url = _find_motley_fool_listing_url(ticker, q_num, q_year, slug)
        if transcript_url:
            log.info(f"[{ticker}] Found transcript link in Motley Fool index: {transcript_url}")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        log.warning(f"[{ticker}] Failed to scan Motley Fool listing pages: {e}")

    # Strategy 2: If listing search failed, try a direct URL construction
    # Pattern: /earnings/call-transcripts/YYYY/MM/DD/{slug}-{ticker}-q{N}-{year}-earnings-call-transcript/
    # We don't know the exact date, but we can try common patterns
    if not transcript_url:
        log.debug(f"[{ticker}] Listing search failed, trying URL construction")
        transcript_url = _guess_fool_url(base_url, slug, ticker, q_num, q_year)

    if not transcript_url:
        log.info(f"[{ticker}] Could not find Motley Fool transcript for {quarter}")
        return None

    # Fetch the transcript page
    log.info(f"[{ticker}] Fetching transcript: {transcript_url}")
    try:
        html = fetch_url_text(transcript_url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            log.info(f"[{ticker}] Motley Fool transcript page not found (404): {transcript_url}")
        else:
            log.warning(f"[{ticker}] HTTP error fetching transcript: {e}")
        return None
    except (urllib.error.URLError, OSError) as e:
        log.warning(f"[{ticker}] Failed to fetch transcript: {e}")
        return None

    # Extract text
    text = extract_article_text(html)

    if len(text.strip()) < 500:
        log.warning(f"[{ticker}] Extracted text suspiciously short ({len(text)} chars)")
        # Still return it — might be a partial transcript
        fidelity = "partial"
    else:
        # Check for Q&A section as a quality signal
        has_qa = any(marker in text.lower() for marker in [
            "question-and-answer", "questions and answers", "q&a session",
            "q & a", "operator", "your next question",
        ])
        fidelity = "full_transcript" if has_qa else "prepared_remarks_only"

    return {
        "text": text,
        "source": "motley_fool",
        "source_url": transcript_url,
        "fidelity": fidelity,
    }


def _guess_fool_url(
    base_url: str,
    slug: str,
    ticker: str,
    q_num: str,
    q_year: str,
) -> str | None:
    """Try to construct a Motley Fool transcript URL by guessing the date.

    Earnings are typically within a few weeks of quarter end.
    First prefer the current thesis next-earnings date when it corresponds to
    the requested quarter. Otherwise fall back to a generic post-quarter window
    so historical quarter fetches can still work.
    """
    earnings_date = _candidate_earnings_date(ticker, q_num, q_year)
    if earnings_date is None:
        return None

    ticker_lower = ticker.lower()

    # Try dates in a short window around the likely transcript publication date.
    for offset in range(0, 21):
        try_date = earnings_date + timedelta(days=offset)
        date_path = try_date.strftime("%Y/%m/%d")

        # Try common URL patterns
        url_patterns = [
            f"{base_url}{date_path}/{slug}-{ticker_lower}-q{q_num}-{q_year}-earnings-call-transcript/",
            f"{base_url}{date_path}/{slug}-nasdaq-{ticker_lower}-q{q_num}-{q_year}-earnings-call-transcript/",
            f"{base_url}{date_path}/{slug}-nyse-{ticker_lower}-q{q_num}-{q_year}-earnings-call-transcript/",
        ]

        for url in url_patterns:
            try:
                # HEAD request to check if page exists without downloading full content
                req = urllib.request.Request(url, method="HEAD", headers={
                    "User-Agent": USER_AGENT,
                })
                _rate_limit()
                ctx = _create_ssl_context()
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    if resp.status == 200:
                        log.info(f"[{ticker}] Found transcript via URL guess: {url}")
                        return url
            except (urllib.error.HTTPError, urllib.error.URLError, OSError):
                continue

    return None


def _find_motley_fool_listing_url(
    ticker: str,
    q_num: str,
    q_year: str,
    slug: str,
    max_pages: int = 8,
) -> str | None:
    """Scan recent Motley Fool transcript listing pages for a matching article."""
    for page_num in range(1, max_pages + 1):
        if page_num == 1:
            listing_url = MOTLEY_FOOL_LISTING_URL
        else:
            listing_url = f"{MOTLEY_FOOL_LISTING_URL}page/{page_num}/"

        html = fetch_url_text(listing_url)
        links = extract_links(html, base_url=listing_url)
        candidates = _find_motley_fool_links(links, ticker, q_num, q_year, slug)
        if candidates:
            return candidates[0]["href"]

    return None


def _find_motley_fool_links(
    links: list[dict[str, str]],
    ticker: str,
    q_num: str,
    q_year: str,
    slug: str,
) -> list[dict[str, str]]:
    """Find Motley Fool article links that match the requested ticker + quarter."""
    scored: list[tuple[int, dict[str, str]]] = []
    ticker_lower = ticker.lower()
    slug_terms = [part for part in slug.lower().split("-") if part]

    for link in links:
        href = link["href"].lower()
        text = link["text"].lower()
        combined = f"{href} {text}"

        if "/earnings/call-transcripts/" not in href:
            continue
        if "transcript" not in combined:
            continue
        if f"q{q_num}" not in combined or q_year not in combined:
            continue

        score = 0
        if ticker_lower in combined:
            score += 6
        if slug and slug in combined:
            score += 5
        matched_slug_terms = sum(1 for term in slug_terms if term in combined)
        score += matched_slug_terms
        if "earnings-call-transcript" in href:
            score += 3
        if "motley fool transcribing" in text:
            score += 1

        required_slug_matches = 1 if len(slug_terms) <= 1 else 2
        has_identity_signal = (
            ticker_lower in combined
            or (slug and slug in combined)
            or matched_slug_terms >= required_slug_matches
        )

        if has_identity_signal and score > 0:
            scored.append((score, link))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [link for _, link in scored]


def _candidate_earnings_date(ticker: str, q_num: str, q_year: str) -> date | None:
    """Estimate the earnings date for the requested quarter."""
    requested_quarter = f"Q{q_num}_{q_year}"
    ticker_map = get_ticker_map()
    info = ticker_map.get(ticker, {})
    earnings_str = info.get("next_earnings")

    if earnings_str:
        try:
            next_earnings = datetime.strptime(earnings_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            next_earnings = None
        else:
            if infer_quarter_from_earnings_date(earnings_str) == requested_quarter:
                return next_earnings

    quarter_end = _quarter_end_date(q_num, q_year)
    if quarter_end is None:
        return None

    # Most earnings calls land ~2-8 weeks after quarter end.
    return quarter_end + timedelta(days=14)


def _quarter_end_date(q_num: str, q_year: str) -> date | None:
    """Map a calendar quarter label to an approximate quarter-end date."""
    try:
        year = int(q_year)
        quarter = int(q_num)
    except ValueError:
        return None

    quarter_ends = {
        1: (3, 31),
        2: (6, 30),
        3: (9, 30),
        4: (12, 31),
    }
    month_day = quarter_ends.get(quarter)
    if month_day is None:
        return None
    month, day = month_day
    return date(year, month, day)


# ---------------------------------------------------------------------------
# Link matching helpers
# ---------------------------------------------------------------------------

def _parse_quarter(quarter: str) -> tuple[str, str]:
    """Parse 'Q1_2026' or 'Q1 2026' into ('Q1', '2026').

    Returns ('', '') on failure.
    """
    match = re.match(r"(Q[1-4])[_\s](\d{4})", quarter, re.IGNORECASE)
    if match:
        return match.group(1).upper(), match.group(2)
    return "", ""


def _find_transcript_links(
    links: list[dict[str, str]],
    ticker: str,
    q_label: str,
    q_year: str,
    cdn_domain: str = "",
) -> list[dict[str, str]]:
    """Score and filter links that look like earnings transcript PDFs/pages.

    Returns links sorted by relevance score (highest first).
    """
    transcript_keywords = [
        "transcript", "earnings call", "earnings-call",
        "corrected transcript", "corrected-transcript",
    ]
    q_num = q_label.replace("Q", "")
    scored: list[tuple[int, dict[str, str]]] = []

    for link in links:
        href = link["href"].lower()
        text = link["text"].lower()
        combined = href + " " + text
        score = 0

        # Must have some transcript signal
        has_transcript_signal = any(kw in combined for kw in transcript_keywords)
        if not has_transcript_signal:
            continue

        # Score components
        if "transcript" in combined:
            score += 10
        if ".pdf" in href:
            score += 5
        if "corrected" in combined:
            score += 3
        if ticker.lower() in combined:
            score += 5
        if f"q{q_num}" in combined:
            score += 5
        if q_year in combined:
            score += 5
        if cdn_domain and cdn_domain.split(".")[0] in href:
            score += 3

        # For NVDA, fiscal year mapping: calendar Q1 2026 = Q2 FY2027
        # This is complex, so we boost if the year is anywhere nearby
        yr_int = int(q_year)
        for check_yr in [str(yr_int), str(yr_int + 1), str(yr_int - 1)]:
            if check_yr in combined:
                score += 2
                break

        if score > 10:  # Minimum threshold
            scored.append((score, link))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [link for _, link in scored]


# ---------------------------------------------------------------------------
# Quarter inference for --all-due
# ---------------------------------------------------------------------------

def infer_quarter_from_earnings_date(earnings_date_str: str) -> str:
    """Infer the reporting quarter from the next_earnings date.

    Heuristic: earnings in Jan-Mar report Q4 of prior year,
    Apr-Jun report Q1, Jul-Sep report Q2, Oct-Dec report Q3.
    (Most companies report ~1 month after quarter end.)
    """
    try:
        d = datetime.strptime(earnings_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return ""

    month = d.month
    year = d.year

    if month <= 3:
        return f"Q4_{year - 1}"
    elif month <= 6:
        return f"Q1_{year}"
    elif month <= 9:
        return f"Q2_{year}"
    else:
        return f"Q3_{year}"


# ---------------------------------------------------------------------------
# Core fetch orchestrator
# ---------------------------------------------------------------------------

def fetch_transcript(
    ticker: str,
    quarter: str,
    source_override: str | None = None,
    dry_run: bool = False,
) -> dict | None:
    """Fetch a transcript using the tiered strategy.

    Args:
        ticker: Stock ticker (e.g. "TSM")
        quarter: Quarter string (e.g. "Q1_2026")
        source_override: Force a specific source ("q4cdn", "ir_scrape", "motley_fool")
        dry_run: If True, don't write files

    Returns:
        dict with result metadata, or None on total failure
    """
    sources = get_transcript_sources()
    q4cdn_config = sources.get("q4cdn", {})
    ir_config = sources.get("ir_scrape", {})
    fool_config = sources.get("motley_fool", {})

    result = None

    if source_override:
        # Use only the specified source
        if source_override == "q4cdn" and ticker in q4cdn_config:
            result = fetch_q4cdn(ticker, quarter, q4cdn_config[ticker])
        elif source_override == "ir_scrape" and ticker in ir_config:
            result = fetch_ir_scrape(ticker, quarter, ir_config[ticker])
        elif source_override == "motley_fool":
            result = fetch_motley_fool(ticker, quarter, fool_config)
        else:
            log.error(f"[{ticker}] Source '{source_override}' not available for this ticker")
            return None
    else:
        # Tiered strategy
        # Tier 1: q4cdn
        if ticker in q4cdn_config:
            log.info(f"[{ticker}] Trying Tier 1 (q4cdn)")
            result = fetch_q4cdn(ticker, quarter, q4cdn_config[ticker])

        # Tier 2: IR scrape
        if result is None and ticker in ir_config:
            log.info(f"[{ticker}] Trying Tier 2 (IR scrape)")
            result = fetch_ir_scrape(ticker, quarter, ir_config[ticker])

        # Tier 3: Motley Fool
        if result is None:
            log.info(f"[{ticker}] Trying Tier 3 (Motley Fool)")
            result = fetch_motley_fool(ticker, quarter, fool_config)

    if result is None:
        log.warning(f"[{ticker}] All sources exhausted for {quarter}")
        return None

    # Write the transcript file
    if not dry_run:
        output_path = _write_transcript(ticker, quarter, result)
        _update_state(ticker, quarter, result, output_path)
        log.info(f"[{ticker}] Transcript saved: {output_path.relative_to(REPO_ROOT)}")
        result["output_path"] = str(output_path.relative_to(REPO_ROOT))
    else:
        log.info(f"[{ticker}] DRY RUN — would save transcript ({result['fidelity']})")
        result["output_path"] = None

    return result


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def _write_transcript(ticker: str, quarter: str, result: dict) -> Path:
    """Write transcript to drafts/earnings/ with frontmatter."""
    DRAFTS_EARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DRAFTS_EARNINGS_DIR / f"{ticker}-{quarter}-transcript.md"

    q_label, q_year = _parse_quarter(quarter)
    quarter_display = f"{q_label} {q_year}" if q_label else quarter

    today_str = date.today().isoformat()
    source_url = result.get("source_url", "")
    fidelity = result.get("fidelity", "unknown")
    source = result.get("source", "unknown")
    text = result.get("text", "")

    frontmatter = (
        f"---\n"
        f"ticker: {ticker}\n"
        f"quarter: \"{quarter_display}\"\n"
        f"fetched_at: \"{today_str}\"\n"
        f"source: {source}\n"
        f"source_url: \"{source_url}\"\n"
        f"fidelity: {fidelity}\n"
        f"needs_review: true\n"
        f"---\n"
    )

    content = (
        f"{frontmatter}\n"
        f"# {ticker} {quarter_display} Earnings Call Transcript\n\n"
        f"{text}\n"
    )

    output_path.write_text(content, encoding="utf-8")
    return output_path


def _update_state(ticker: str, quarter: str, result: dict, output_path: Path) -> None:
    """Update transcripts.yaml state tracking file."""
    state = get_transcript_state()

    if ticker not in state:
        state[ticker] = {}

    state[ticker][quarter] = {
        "fetched_at": date.today().isoformat(),
        "source": result.get("source", "unknown"),
        "source_url": result.get("source_url", ""),
        "path": str(output_path.relative_to(REPO_ROOT)),
        "fidelity": result.get("fidelity", "unknown"),
    }

    save_transcript_state(state)


# ---------------------------------------------------------------------------
# --all-due mode
# ---------------------------------------------------------------------------

def fetch_all_due(dry_run: bool = False) -> list[dict]:
    """Fetch transcripts for all tickers whose earnings have passed but
    have no transcript on file.

    Returns list of result dicts for successful fetches.
    """
    today = date.today()
    ticker_map = get_ticker_map()
    deep_dive = set(get_deep_dive_tickers())
    state = get_transcript_state()
    results = []

    due_tickers: list[tuple[str, str, str]] = []  # (ticker, quarter, earnings_date)

    for ticker, info in ticker_map.items():
        # Only process deep-dive tickers
        if ticker not in deep_dive:
            continue

        earnings_str = info.get("next_earnings")
        if not earnings_str:
            continue

        try:
            earnings_date = datetime.strptime(earnings_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        # Only fetch if earnings date has passed
        if earnings_date >= today:
            continue

        # Infer the quarter being reported
        quarter = infer_quarter_from_earnings_date(earnings_str)
        if not quarter:
            continue

        # Check if we already have this transcript
        ticker_state = state.get(ticker, {})
        if quarter in ticker_state:
            log.debug(f"[{ticker}] Already have transcript for {quarter}, skipping")
            continue

        due_tickers.append((ticker, quarter, earnings_str))

    if not due_tickers:
        log.info("No due transcripts to fetch")
        return results

    log.info(f"Found {len(due_tickers)} due transcript(s): "
             f"{', '.join(f'{t}({q})' for t, q, _ in due_tickers)}")

    for ticker, quarter, earnings_str in due_tickers:
        log.info(f"[{ticker}] Fetching transcript for {quarter} (earnings was {earnings_str})")
        try:
            result = fetch_transcript(ticker, quarter, dry_run=dry_run)
            if result:
                result["ticker"] = ticker
                result["quarter"] = quarter
                results.append(result)
            else:
                log.warning(f"[{ticker}] Could not fetch transcript for {quarter}")
        except Exception as e:
            log.error(f"[{ticker}] Unexpected error: {e}", exc_info=True)

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch earnings call transcripts for tracked companies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python agents/src/transcript_fetcher.py --ticker TSM --quarter Q1_2026\n"
            "  python agents/src/transcript_fetcher.py --ticker NVDA --quarter Q1_2026 --source q4cdn\n"
            "  python agents/src/transcript_fetcher.py --all-due\n"
            "  python agents/src/transcript_fetcher.py --all-due --dry-run\n"
        ),
    )

    # Mutually exclusive: single ticker vs all-due
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ticker", type=str, help="Ticker to fetch (e.g. TSM)")
    group.add_argument("--all-due", action="store_true",
                       help="Fetch for all tickers whose earnings date has passed but no transcript exists")

    parser.add_argument("--quarter", type=str,
                        help="Quarter to fetch (e.g. Q1_2026). Required with --ticker.")
    parser.add_argument("--source", type=str, choices=["q4cdn", "ir_scrape", "motley_fool"],
                        help="Force a specific source (default: auto-select by tier)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be fetched without writing files")

    args = parser.parse_args()

    # Validate args
    if args.ticker and not args.quarter:
        parser.error("--quarter is required when using --ticker")

    log.info("=" * 60)
    log.info(f"transcript_fetcher started at {datetime.now().isoformat(timespec='seconds')}")

    if args.all_due:
        log.info("Mode: --all-due")
        results = fetch_all_due(dry_run=args.dry_run)

        if results:
            print(f"\nFetched {len(results)} transcript(s):")
            for r in results:
                path_str = r.get("output_path", "(dry run)")
                print(f"  {r['ticker']} {r['quarter']}: {r['source']} [{r['fidelity']}] -> {path_str}")
        else:
            print("\nNo transcripts to fetch (all up to date or no earnings have passed).")

    else:
        ticker = args.ticker.upper()
        quarter = args.quarter.upper().replace(" ", "_")
        log.info(f"Mode: single ticker={ticker} quarter={quarter} source={args.source or 'auto'}")

        result = fetch_transcript(ticker, quarter, source_override=args.source, dry_run=args.dry_run)

        if result:
            path_str = result.get("output_path", "(dry run)")
            print(f"\nSuccess: {ticker} {quarter}")
            print(f"  Source: {result['source']}")
            print(f"  Fidelity: {result['fidelity']}")
            print(f"  URL: {result.get('source_url', 'N/A')}")
            print(f"  Output: {path_str}")
        else:
            print(f"\nFailed: Could not fetch transcript for {ticker} {quarter}")
            print("Check logs for details:", LOGS_DIR / f"transcript-fetcher-{date.today().strftime('%Y-%m')}.log")
            sys.exit(1)

    log.info(f"transcript_fetcher finished at {datetime.now().isoformat(timespec='seconds')}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
