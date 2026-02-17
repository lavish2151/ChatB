from __future__ import annotations

import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class GDoc:
    url: str
    title: str
    text: str


def _guess_title(url: str, soup: BeautifulSoup) -> str:
    if soup.title and soup.title.text:
        return soup.title.text.strip()
    # Fallback: last path segment-ish
    return url.strip().rstrip("/").split("/")[-1]


_PUBLISHED_RE = re.compile(r"https?://docs\.google\.com/document/d/e/[^/]+/")
_DOC_ID_RE = re.compile(r"https?://docs\.google\.com/document/d/([^/]+)/")


def _to_export_url(url: str) -> str:
    """
    Accepts common Google Docs "edit" URLs and converts them to an export URL that
    can be fetched by the server, IF the doc is publicly readable.

    Example:
      https://docs.google.com/document/d/<docId>/edit?...  ->  .../export?format=html
    """
    # Already a published-to-web URL; fetch as-is.
    if _PUBLISHED_RE.search(url):
        return url

    m = _DOC_ID_RE.search(url)
    if not m:
        return url
    doc_id = m.group(1)
    if doc_id == "e":
        # Safety: don't generate a broken export URL.
        return url
    return f"https://docs.google.com/document/d/{doc_id}/export?format=html"


def fetch_published_doc(url: str, *, timeout_s: int = 20) -> GDoc:
    """
    Fetch a Google Doc that has been "Published to the web".
    Works well for URLs like:
    - https://docs.google.com/document/d/e/<id>/pub?embedded=true
    """
    # If user pasted an /edit link, try fetching the export HTML instead.
    fetch_url = _to_export_url(url)

    resp = requests.get(fetch_url, timeout=timeout_s)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    title = _guess_title(url, soup)

    # Extract visible text
    text = soup.get_text(separator="\n", strip=True)
    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return GDoc(url=url, title=title, text=text)

