"""Async NeonDB/PostgreSQL client for document and chunk registry."""

import json

import asyncpg
from uuid import UUID

from .config import settings
from .logging import get_logger
from .models import ProcessedDocument, DocumentChunk

logger = get_logger("neondb_client")

# Global pool instance (lazy-loaded)
_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Register jsonb codec for automatic Python dict/list serialization."""
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.neon_database_url,
            min_size=2,
            max_size=10,
            init=_init_connection,
        )
    return _pool


def _to_jsonb(value):
    """Serialize Python lists/dicts to JSON string for jsonb columns."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


async def insert_document(doc: ProcessedDocument) -> None:
    """Insert a document record into NeonDB.

    On conflict (same s3_key), updates all fields and preserves the existing
    document id so that downstream chunk inserts maintain FK integrity.
    """
    pool = await _get_pool()
    async with pool.acquire() as conn:
        # Upsert document, preserving existing id
        row = await conn.fetchrow(
            """
            INSERT INTO documents (
                id, s3_key, filename, document_type, size_bytes, page_count,
                meta_domain, meta_industry, meta_companies, meta_document_type,
                meta_confidentiality, meta_language,
                pii_detected, pii_types, pii_redaction_verified,
                chunk_count, status, error_message
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10, $11, $12, $13, $14::jsonb, $15, $16, $17, $18)
            ON CONFLICT (s3_key) DO UPDATE SET
                filename = EXCLUDED.filename,
                document_type = EXCLUDED.document_type,
                size_bytes = EXCLUDED.size_bytes,
                page_count = EXCLUDED.page_count,
                meta_domain = EXCLUDED.meta_domain,
                meta_industry = EXCLUDED.meta_industry,
                meta_companies = EXCLUDED.meta_companies,
                meta_document_type = EXCLUDED.meta_document_type,
                meta_confidentiality = EXCLUDED.meta_confidentiality,
                meta_language = EXCLUDED.meta_language,
                pii_detected = EXCLUDED.pii_detected,
                pii_types = EXCLUDED.pii_types,
                pii_redaction_verified = EXCLUDED.pii_redaction_verified,
                chunk_count = EXCLUDED.chunk_count,
                status = EXCLUDED.status,
                error_message = EXCLUDED.error_message,
                updated_at = NOW()
            RETURNING id
            """,
            doc.id,
            doc.s3_key,
            doc.filename,
            doc.document_type,
            doc.size_bytes,
            doc.page_count,
            doc.metadata.domain,
            doc.metadata.industry,
            _to_jsonb(doc.metadata.companies),
            doc.metadata.document_type,
            doc.metadata.confidentiality,
            doc.metadata.language,
            doc.pii_audit.pii_detected,
            _to_jsonb(doc.pii_audit.pii_types),
            doc.pii_audit.redaction_verified,
            doc.chunk_count,
            doc.status,
            doc.error_message,
        )
        # Synchronize the document id so chunks reference the correct PK
        if row:
            doc.id = row["id"]
        logger.info("Document inserted/updated", document_id=str(doc.id), filename=doc.filename)


async def insert_chunks(doc_id: UUID, chunks: list[DocumentChunk], qdrant_point_ids: list[str]) -> None:
    """Insert chunk records into NeonDB with Qdrant point IDs.

    On re-ingestion, deletes existing chunks for the document first so that
    old chunk indices that no longer exist are removed.
    """
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM chunks WHERE document_id = $1",
            doc_id,
        )
        for chunk, point_id in zip(chunks, qdrant_point_ids):
            await conn.execute(
                """
                INSERT INTO chunks (
                    id, document_id, chunk_index, chunk_type, page_number,
                    chunk_text, chunk_base64,
                    meta_chunk_topic, meta_products, meta_technologies,
                    meta_organizations, meta_locations, meta_dates, meta_metrics,
                    qdrant_point_id, qdrant_collection,
                    pii_detected, pii_types
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7,
                    $8,
                    $9::jsonb, $10::jsonb, $11::jsonb, $12::jsonb, $13::jsonb, $14::jsonb,
                    $15, $16,
                    $17, $18::jsonb
                )
                ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                    chunk_text = EXCLUDED.chunk_text,
                    chunk_base64 = EXCLUDED.chunk_base64,
                    qdrant_point_id = EXCLUDED.qdrant_point_id,
                    updated_at = NOW()
                """,
                chunk.id,
                doc_id,
                chunk.chunk_index,
                chunk.chunk_type,
                chunk.page_number,
                chunk.chunk_text,
                chunk.chunk_base64,
                chunk.metadata.chunk_topic,
                _to_jsonb(chunk.metadata.products),
                _to_jsonb(chunk.metadata.technologies),
                _to_jsonb(chunk.metadata.organizations),
                _to_jsonb(chunk.metadata.locations),
                _to_jsonb(chunk.metadata.dates),
                _to_jsonb(chunk.metadata.metrics),
                point_id,
                settings.qdrant_collection,
                chunk.pii_audit.pii_detected,
                _to_jsonb(chunk.pii_audit.pii_types),
            )
        logger.info("Chunks inserted", document_id=str(doc_id), count=len(chunks))


async def update_document_status(doc_id: UUID, status: str, error_message: str | None = None) -> None:
    """Update document processing status."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE documents SET status = $1, error_message = $2, updated_at = NOW() WHERE id = $3",
            status,
            error_message,
            doc_id,
        )
        logger.info("Document status updated", document_id=str(doc_id), status=status)
