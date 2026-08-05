"""Docling HybridChunker wrapper with image/table/formula base64 extraction."""

import asyncio
import base64
from io import BytesIO
from typing import Iterator
from uuid import UUID

from docling.chunking import HybridChunker
from docling.datamodel.document import DoclingDocument
from docling_core.types.doc.document import PictureItem, TableItem, FormulaItem

from .logging import get_logger
from .models import DocumentChunk, ChunkMetadata

logger = get_logger("chunker")

# Global chunker instance (lazy-loaded)
_chunker: HybridChunker | None = None


def _get_chunker() -> HybridChunker:
    global _chunker
    if _chunker is None:
        _chunker = HybridChunker()
    return _chunker


def _resize_to_max_dim(img, max_dim: int = 1024):
    """Resize PIL image so that neither dimension exceeds max_dim."""
    from PIL import Image

    if img is None:
        return None
    w, h = img.size
    if w <= max_dim and h <= max_dim:
        return img
    ratio = min(max_dim / w, max_dim / h)
    new_size = (int(w * ratio), int(h * ratio))
    return img.resize(new_size, Image.LANCZOS)


def _pil_to_base64_png(img) -> str | None:
    """Convert a PIL Image to base64-encoded PNG string."""
    if img is None:
        return None
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _extract_base64_from_item(item, doc: DoclingDocument) -> str | None:
    """Extract a resized base64 PNG from a Docling item (Picture/Table/Formula).

    Returns None if the item has no renderable image.
    """
    try:
        img = item.get_image(doc)
    except Exception:
        return None
    if img is None:
        return None
    resized = _resize_to_max_dim(img, max_dim=1024)
    return _pil_to_base64_png(resized)


def _item_is_visual(item) -> bool:
    """Check if a Docling item is a picture, table, or formula."""
    return isinstance(item, (PictureItem, TableItem, FormulaItem))


async def chunk_document(
    doc: DoclingDocument,
    document_id: str | UUID,
    filename: str,
) -> list[DocumentChunk]:
    """Chunk a DoclingDocument into DocumentChunks.

    For picture, table, and formula chunks, extracts a resized base64 PNG
    so the chunk can be sent to an LLM for multi-modal understanding.

    Args:
        doc: Parsed DoclingDocument.
        document_id: Parent document UUID (string or UUID).
        filename: Source filename.

    Returns:
        List of DocumentChunk objects.
    """
    chunker = _get_chunker()

    def _chunk() -> Iterator:
        return chunker.chunk(doc)

    logger.info("Chunking document", filename=filename)
    chunks = await asyncio.to_thread(_chunk)

    result: list[DocumentChunk] = []
    visual_count = 0
    for idx, chunk in enumerate(chunks):
        chunk_type = "text"
        page_number = None
        base64_str: str | None = None

        if hasattr(chunk, "meta") and chunk.meta and chunk.meta.doc_items:
            # Scan ALL doc_items in the chunk (HybridChunker may group multiple items)
            # Determine chunk type from first non-text item, or default to text
            for item in chunk.meta.doc_items:
                label = str(getattr(item, "label", "text")).lower()
                if "table" in label:
                    chunk_type = "table"
                    break
                elif "picture" in label or "chart" in label or "figure" in label:
                    chunk_type = "image"
                    break
                elif "formula" in label:
                    chunk_type = "formula"
                    break

            # Extract page number from first doc_item's provenance
            first_item = chunk.meta.doc_items[0]
            prov_list = getattr(first_item, "prov", [])
            if prov_list:
                page_number = getattr(prov_list[0], "page_no", None)

            # Try to extract base64 from ANY visual item in the chunk
            for item in chunk.meta.doc_items:
                label = str(getattr(item, "label", "text")).lower()
                if _item_is_visual(item) or "picture" in label or "chart" in label or "figure" in label:
                    b64 = _extract_base64_from_item(item, doc)
                    if b64:
                        base64_str = b64
                        visual_count += 1
                        break  # only store first visual per chunk

        result.append(DocumentChunk(
            document_id=document_id,
            chunk_index=idx,
            chunk_type=chunk_type,
            page_number=page_number,
            chunk_text=getattr(chunk, "text", None),
            chunk_base64=base64_str,
            metadata=ChunkMetadata(),
        ))

    logger.info(
        "Chunking complete",
        filename=filename,
        chunks=len(result),
        visual_chunks_with_base64=visual_count,
    )
    return result
