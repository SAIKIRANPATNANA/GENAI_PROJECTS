"""Async arXiv paper downloader with metadata extraction."""

import asyncio
import re
from xml.etree import ElementTree
from typing import NamedTuple

import aiohttp

from .config import settings
from .logging import get_logger

logger = get_logger("arxiv_downloader")

# ArXiv API endpoints
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}.pdf"
ARXIV_ATOM_URL = "http://export.arxiv.org/api/query?search_query=id:{arxiv_id}&start=0&max_results=1"

# arXiv ID regex: matches 2401.12345, arxiv:2401.12345, https://arxiv.org/abs/2401.12345, etc.
_ARXIV_ID_RE = re.compile(
    r"(?:https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/)?"
    r"(?:arxiv:)?"
    r"(\d{4}\.\d{4,5})"  # e.g. 1706.03762
)


class ArxivMetadata(NamedTuple):
    """ArXiv paper metadata."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: str  # ISO 8601 date


class ArxivResult(NamedTuple):
    """Result of downloading an arXiv paper."""

    arxiv_id: str
    pdf_bytes: bytes
    metadata: ArxivMetadata
    s3_key: str


def normalize_arxiv_id(raw: str) -> str | None:
    """Normalize an arXiv identifier from various formats.

    Supports:
        - Bare ID: 1706.03762
        - Prefixed: arxiv:1706.03762
        - URL: https://arxiv.org/abs/1706.03762
        - PDF URL: https://arxiv.org/pdf/1706.03762.pdf
    """
    raw = raw.strip().lower()
    match = _ARXIV_ID_RE.search(raw)
    return match.group(1) if match else None


async def _fetch_pdf(session: aiohttp.ClientSession, arxiv_id: str) -> bytes:
    """Download PDF from arXiv with retries."""
    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)
    for attempt in range(1, 4):
        try:
            logger.info("Downloading arXiv PDF", arxiv_id=arxiv_id, attempt=attempt)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 404:
                    raise ValueError(f"arXiv paper not found: {arxiv_id}")
                resp.raise_for_status()
                data = await resp.read()
                if len(data) < 1000:
                    # arXiv sometimes returns a small HTML redirect page
                    raise ValueError(f"arXiv returned invalid PDF for {arxiv_id} (size={len(data)})")
                logger.info("Downloaded arXiv PDF", arxiv_id=arxiv_id, size=len(data))
                return data
        except aiohttp.ClientError as e:
            logger.warning("arXiv PDF download failed, retrying", arxiv_id=arxiv_id, error=str(e), attempt=attempt)
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to download arXiv PDF {arxiv_id} after 3 attempts")


async def _fetch_metadata(session: aiohttp.ClientSession, arxiv_id: str) -> ArxivMetadata:
    """Fetch metadata from arXiv Atom API."""
    url = ARXIV_ATOM_URL.format(arxiv_id=arxiv_id)
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        resp.raise_for_status()
        text = await resp.text()

    # Parse Atom XML
    root = ElementTree.fromstring(text)

    # Atom namespace
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    entry = root.find("atom:entry", ns)
    if entry is None:
        raise ValueError(f"No arXiv entry found for {arxiv_id}")

    title_elem = entry.find("atom:title", ns)
    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

    abstract_elem = entry.find("atom:summary", ns)
    abstract = abstract_elem.text.strip() if abstract_elem is not None and abstract_elem.text else ""

    authors = [
        author.find("atom:name", ns).text.strip()
        for author in entry.findall("atom:author", ns)
        if author.find("atom:name", ns) is not None and author.find("atom:name", ns).text
    ]

    categories = [cat.get("term", "") for cat in entry.findall("atom:category", ns) if cat.get("term")]

    published_elem = entry.find("atom:published", ns)
    published = published_elem.text.strip() if published_elem is not None and published_elem.text else ""

    return ArxivMetadata(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
        categories=categories,
        published=published,
    )


async def download_arxiv_paper(raw_id: str) -> ArxivResult:
    """Download an arXiv paper by ID and return PDF bytes + metadata.

    Args:
        raw_id: ArXiv identifier in any supported format.

    Returns:
        ArxivResult with PDF bytes, metadata, and the target S3 key.
    """
    arxiv_id = normalize_arxiv_id(raw_id)
    if arxiv_id is None:
        raise ValueError(f"Invalid arXiv identifier: {raw_id}")

    s3_key = f"{settings.arxiv_s3_prefix}{arxiv_id}.pdf"

    async with aiohttp.ClientSession() as session:
        pdf_bytes, metadata = await asyncio.gather(
            _fetch_pdf(session, arxiv_id),
            _fetch_metadata(session, arxiv_id),
        )

    return ArxivResult(
        arxiv_id=arxiv_id,
        pdf_bytes=pdf_bytes,
        metadata=metadata,
        s3_key=s3_key,
    )
