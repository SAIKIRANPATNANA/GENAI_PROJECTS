"""Prefect async flows for document ingestion."""

import asyncio
from pathlib import Path

from prefect import flow

from .config import settings
from .logging import get_logger
from .models import ProcessedDocument, QdrantPayload, DocumentChunk
from .s3_client import download_s3_document
from .docling_processor import convert_document
from .chunker import chunk_document
from .gliner_metadata import enrich_document_metadata
from .gliner_pii import redact_document_chunks
from .embedder import embed_text
from .sparse_embedder import embed_text as embed_sparse
from .qdrant_store import upsert_chunks
from .neondb_client import insert_document, insert_chunks, update_document_status
from .arxiv_downloader import download_arxiv_paper
from .s3_client import S3Client

logger = get_logger("flows")


async def _process_single_document(s3_key: str, batch_id: str) -> str:
    """Process a single document end-to-end (internal, not a Prefect task).

    All work happens in one async call to avoid serializing complex objects
    (Docling ConversionResult) between Prefect tasks.
    """
    logger.info("Processing document", s3_key=s3_key, batch_id=batch_id)

    # Step 1: Download + Docling convert
    file_bytes = await download_s3_document(s3_key)
    filename = Path(s3_key).name
    # Capture size before Docling consumes the BytesIO
    size_bytes = len(file_bytes.getvalue())
    doc_result = await convert_document(file_bytes, filename)

    # Extract document type
    ext = Path(filename).suffix.lower().lstrip(".")
    doc_type = ext if ext else "unknown"

    doc = ProcessedDocument(
        s3_key=s3_key,
        filename=filename,
        document_type=doc_type,
    )
    doc.size_bytes = size_bytes
    doc.page_count = len(doc_result.document.pages)
    doc.status = "processing"

    # Step 2: Chunk + metadata + PII
    doc.chunks = await chunk_document(doc_result.document, str(doc.id), filename)
    doc.chunk_count = len(doc.chunks)

    await enrich_document_metadata(doc)
    await redact_document_chunks(doc)

    # Step 3: Embed + Qdrant upsert
    text_chunks: list[DocumentChunk] = []
    for chunk in doc.chunks:
        if chunk.chunk_text and chunk.chunk_type != "image":
            text_chunks.append(chunk)

    dense_embeddings = None
    sparse_embeddings = None
    if text_chunks:
        texts = [c.chunk_text for c in text_chunks]
        dense_embeddings, sparse_embeddings = await asyncio.gather(
            embed_text(texts),
            embed_sparse(texts),
        )

    payloads = []
    all_embeddings_dense = []
    all_embeddings_sparse = []

    for chunk in doc.chunks:
        if chunk.chunk_type == "image" or not chunk.chunk_text:
            continue

        try:
            idx = text_chunks.index(chunk)
        except ValueError:
            continue

        if dense_embeddings is not None and idx < len(dense_embeddings):
            all_embeddings_dense.append(dense_embeddings[idx])
            all_embeddings_sparse.append(sparse_embeddings[idx])

        payload = QdrantPayload(
            source_s3_key=doc.s3_key,
            document_type=doc.document_type,
            chunk_type=chunk.chunk_type,
            chunk_text=chunk.chunk_text,
            chunk_base64=chunk.chunk_base64,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            total_chunks=doc.chunk_count,
            embedding_modality="text",
            meta_domain=doc.metadata.domain,
            meta_industry=doc.metadata.industry,
            meta_companies=doc.metadata.companies,
            meta_document_type=doc.metadata.document_type,
            meta_confidentiality=doc.metadata.confidentiality,
            meta_language=doc.metadata.language,
            meta_chunk_topic=chunk.metadata.chunk_topic,
            meta_products=chunk.metadata.products,
            meta_technologies=chunk.metadata.technologies,
            meta_organizations=chunk.metadata.organizations,
            meta_locations=chunk.metadata.locations,
            meta_dates=chunk.metadata.dates,
            meta_metrics=chunk.metadata.metrics,
            pii_detected=chunk.pii_audit.pii_detected,
            pii_types=chunk.pii_audit.pii_types,
            redaction_verified=chunk.pii_audit.redaction_verified,
        )
        payloads.append(payload)

    point_ids: list[str] = []
    if all_embeddings_dense:
        point_ids = await upsert_chunks(
            dense_embeddings=all_embeddings_dense,
            sparse_embeddings=all_embeddings_sparse,
            payloads=payloads,
        )

    # Step 4: NeonDB persistence
    await insert_document(doc)
    await insert_chunks(doc.id, doc.chunks, point_ids)

    doc.status = "completed"
    await update_document_status(doc.id, "completed")

    logger.info("Document processed successfully", document_id=str(doc.id), s3_key=s3_key)
    return str(doc.id)


@flow(name="process_document", log_prints=True)
async def process_document(s3_key: str, batch_id: str) -> str:
    """Process a single document end-to-end.

    Args:
        s3_key: S3 key of the document.
        batch_id: Batch identifier for correlation.

    Returns:
        Document ID as string.
    """
    try:
        return await _process_single_document(s3_key, batch_id)
    except Exception as e:
        logger.error("Document processing failed", s3_key=s3_key, error=str(e))
        error_doc = ProcessedDocument(
            s3_key=s3_key,
            filename=Path(s3_key).name,
            document_type="unknown",
        )
        error_doc.status = "failed"
        error_doc.error_message = str(e)
        try:
            await insert_document(error_doc)
            await update_document_status(error_doc.id, "failed", str(e))
        except Exception as db_err:
            logger.error("Failed to log error to NeonDB", error=str(db_err))
        raise


@flow(name="ingest_batch", log_prints=True)
async def ingest_batch(s3_keys: list[str], batch_id: str) -> list[str]:
    """Ingest a batch of documents from S3.

    Args:
        s3_keys: List of S3 keys to process.
        batch_id: Batch identifier.

    Returns:
        List of processed document IDs.
    """
    logger.info("Starting batch ingestion", batch_id=batch_id, count=len(s3_keys))

    semaphore = asyncio.Semaphore(settings.concurrency_limit)

    async def _process_one(key: str) -> str:
        async with semaphore:
            return await process_document(key, batch_id=batch_id)

    results = await asyncio.gather(
        *[_process_one(k) for k in s3_keys],
        return_exceptions=True,
    )

    doc_ids = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    logger.info(
        "Batch ingestion complete",
        batch_id=batch_id,
        success=len(doc_ids),
        failed=len(failed),
    )
    return doc_ids


async def _download_and_upload_arxiv(raw_id: str) -> str:
    """Download arXiv paper and upload to S3. Returns S3 key."""
    result = await download_arxiv_paper(raw_id)
    s3_client = S3Client()
    await s3_client.upload_bytes(result.pdf_bytes, result.s3_key)
    logger.info(
        "arXiv paper uploaded to S3",
        arxiv_id=result.arxiv_id,
        s3_key=result.s3_key,
        title=result.metadata.title,
    )
    return result.s3_key


@flow(name="ingest_arxiv", log_prints=True)
async def ingest_arxiv(raw_ids: list[str], batch_id: str) -> list[str]:
    """Ingest arXiv papers: download PDF, upload to S3, then process.

    Args:
        raw_ids: List of arXiv identifiers (bare ID, arxiv: prefix, or URL).
        batch_id: Batch identifier.

    Returns:
        List of processed document IDs.
    """
    logger.info("Starting arXiv ingestion", batch_id=batch_id, count=len(raw_ids))

    semaphore = asyncio.Semaphore(settings.concurrency_limit)

    async def _process_one(raw_id: str) -> str:
        async with semaphore:
            s3_key = await _download_and_upload_arxiv(raw_id)
            return await process_document(s3_key, batch_id=batch_id)

    results = await asyncio.gather(
        *[_process_one(rid) for rid in raw_ids],
        return_exceptions=True,
    )

    doc_ids = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    logger.info(
        "arXiv ingestion complete",
        batch_id=batch_id,
        success=len(doc_ids),
        failed=len(failed),
    )
    return doc_ids
