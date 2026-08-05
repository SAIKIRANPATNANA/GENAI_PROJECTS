"""GLiNER2 metadata extraction at document, page, and chunk levels."""

import asyncio
from typing import Any

try:
    from gliner import GLiNER as GLiNER2
except ImportError:
    class GLiNER2:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()
        def extract_entities(self, *args, **kwargs):
            return {}
        def predict_entities(self, text, labels, *args, **kwargs):
            return []

from .config import settings
from .logging import get_logger
from .models import DocumentMetadata, ChunkMetadata, ProcessedDocument

logger = get_logger("gliner_metadata")

# Global extractor instance (lazy-loaded)
_extractor: GLiNER2 | None = None


def _get_extractor() -> GLiNER2:
    global _extractor
    if _extractor is None:
        _extractor = GLiNER2.from_pretrained(settings.gliner_metadata_model)
    return _extractor


# --- Document-level schema (entity extraction) ---
DOC_SCHEMA = {
    "company": "Organization or business names",
    "industry": "Business sector or industry domain",
}
DOC_CLASSIFICATIONS = {
    "domain": ["finance", "healthcare", "legal", "technology", "manufacturing"],
    "language": ["en", "fr", "de", "es", "it", "pt", "nl"],
    "confidentiality": ["public", "internal", "confidential", "restricted"],
    "document_type": ["research_paper", "report", "manual", "contract", "invoice", "white_paper", "technical_spec"],
}

# --- Chunk-level schema ---
CHUNK_SCHEMA = {
    "product": "Products, services, or offerings mentioned",
    "technology": "Technologies, frameworks, or tools",
    "person": "Names of people referenced",
    "organization": "Organizations mentioned",
    "location": "Geographic locations",
    "date": "Dates, timelines, or temporal references",
    "metric": "Numerical metrics, KPIs, or measurements",
}
CHUNK_CLASSIFICATIONS = {
    "chunk_topic": ["overview", "technical_spec", "procedure", "analysis", "conclusion"],
}


async def extract_document_metadata(text: str) -> DocumentMetadata:
    """Extract document-level metadata from first N pages of text."""
    extractor = _get_extractor()

    def _extract() -> dict[str, Any]:
        # Entities
        entities = extractor.extract_entities(text, DOC_SCHEMA, include_confidence=True)
        # Classifications
        results = {"entities": entities.get("entities", {})}
        for field, labels in DOC_CLASSIFICATIONS.items():
            cls_result = extractor.classify_text(text, {field: labels}, include_confidence=True)
            results[field] = cls_result.get(field, {})
        return results

    logger.info("Extracting document metadata")
    result = await asyncio.to_thread(_extract)

    meta = DocumentMetadata()
    entities = result.get("entities", {})
    meta.companies = [e["text"] if isinstance(e, dict) else e for e in entities.get("company", [])]

    def _first_entity_text(field: str) -> str | None:
        items = entities.get(field, [])
        val = items[0] if items else None
        if isinstance(val, dict):
            return val.get("text")
        return val

    meta.industry = _first_entity_text("industry")

    def _cls_label(key: str) -> str | None:
        val = result.get(key)
        return val.get("label") if isinstance(val, dict) else None

    meta.document_type = _cls_label("document_type")
    meta.domain = _cls_label("domain")
    meta.language = _cls_label("language")
    meta.confidentiality = _cls_label("confidentiality")

    logger.info("Document metadata extracted", domain=meta.domain, industry=meta.industry, document_type=meta.document_type)
    return meta


async def extract_chunk_metadata(text: str) -> ChunkMetadata:
    """Extract chunk-level metadata for a single chunk."""
    extractor = _get_extractor()

    def _extract() -> dict[str, Any]:
        entities = extractor.extract_entities(text, CHUNK_SCHEMA, include_confidence=True)
        results = {"entities": entities.get("entities", {})}
        for field, labels in CHUNK_CLASSIFICATIONS.items():
            cls_result = extractor.classify_text(text, {field: labels}, include_confidence=True)
            results[field] = cls_result.get(field, {})
        return results

    result = await asyncio.to_thread(_extract)

    meta = ChunkMetadata()
    entities = result.get("entities", {})

    # Map GLiNER entity fields to ChunkMetadata attributes
    field_map = {
        "product": "products",
        "technology": "technologies",
        "organization": "organizations",
        "location": "locations",
        "date": "dates",
        "metric": "metrics",
    }
    for gliner_field, model_attr in field_map.items():
        values = entities.get(gliner_field, [])
        parsed = [v["text"] if isinstance(v, dict) else v for v in values]
        setattr(meta, model_attr, parsed)

    topic_result = result.get("chunk_topic", {})
    meta.chunk_topic = topic_result.get("label") if isinstance(topic_result, dict) else None

    return meta


async def enrich_document_metadata(doc: ProcessedDocument) -> None:
    """Enrich a ProcessedDocument with GLiNER2 metadata."""
    # Combine first few chunks for document-level analysis
    sample_text = " ".join([c.chunk_text or "" for c in doc.chunks[:5]])
    if sample_text.strip():
        doc.metadata = await extract_document_metadata(sample_text)

    # Enrich each chunk
    for chunk in doc.chunks:
        if chunk.chunk_text:
            chunk.metadata = await extract_chunk_metadata(chunk.chunk_text)
