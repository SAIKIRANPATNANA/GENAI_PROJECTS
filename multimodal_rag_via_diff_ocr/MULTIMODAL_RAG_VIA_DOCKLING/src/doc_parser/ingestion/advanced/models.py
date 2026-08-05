"""Pydantic models for documents, chunks, and metadata."""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Document-level GLiNER2 metadata."""

    domain: str | None = None
    industry: str | None = None
    companies: list[str] = Field(default_factory=list)
    document_type: str | None = None
    confidentiality: str | None = None
    language: str | None = None


class ChunkMetadata(BaseModel):
    """Chunk-level GLiNER2 metadata."""

    chunk_topic: str | None = None
    products: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)


class PiiAudit(BaseModel):
    """PII detection audit trail."""

    pii_detected: bool = False
    pii_types: list[str] = Field(default_factory=list)
    redaction_verified: bool = False


class DocumentChunk(BaseModel):
    """A single chunk of a document ready for embedding."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chunk_index: int
    chunk_type: str  # text, table, formula, image
    page_number: int | None = None
    chunk_text: str | None = None
    chunk_image: bytes | None = None
    chunk_base64: str | None = None  # base64 PNG for image/table/formula chunks
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata)
    pii_audit: PiiAudit = Field(default_factory=PiiAudit)


class ProcessedDocument(BaseModel):
    """A fully processed document with all chunks."""

    id: UUID = Field(default_factory=uuid4)
    s3_key: str
    filename: str
    document_type: str
    size_bytes: int | None = None
    page_count: int | None = None
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    pii_audit: PiiAudit = Field(default_factory=PiiAudit)
    chunk_count: int = 0
    status: str = "pending"
    error_message: str | None = None
    chunks: list[DocumentChunk] = Field(default_factory=list)


class QdrantPayload(BaseModel):
    """Payload stored with each Qdrant point."""

    source_s3_key: str
    document_type: str
    chunk_type: str
    chunk_text: str | None = None
    page_number: int | None = None
    chunk_index: int
    total_chunks: int
    embedding_modality: str  # text or image

    # Document-level metadata
    meta_domain: str | None = None
    meta_industry: str | None = None
    meta_companies: list[str] = Field(default_factory=list)
    meta_document_type: str | None = None
    meta_confidentiality: str | None = None
    meta_language: str | None = None

    # Chunk-level metadata
    meta_chunk_topic: str | None = None
    meta_products: list[str] = Field(default_factory=list)
    meta_technologies: list[str] = Field(default_factory=list)
    meta_organizations: list[str] = Field(default_factory=list)
    meta_locations: list[str] = Field(default_factory=list)
    meta_dates: list[str] = Field(default_factory=list)
    meta_metrics: list[str] = Field(default_factory=list)

    # Base64 image (for image/table/formula chunks sent to LLM)
    chunk_base64: str | None = None

    # Audit
    pii_detected: bool = False
    pii_types: list[str] = Field(default_factory=list)
    redaction_verified: bool = False
