"""Flush pipeline — clear all data from NeonDB and Qdrant (keeps S3 intact)."""

from qdrant_client import AsyncQdrantClient

from .config import settings
from .logging import get_logger

logger = get_logger("flush")

# Qdrant client (lazy-loaded, same pattern as qdrant_store)
_qdrant_client: AsyncQdrantClient | None = None


def _get_qdrant_client() -> AsyncQdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
    return _qdrant_client


async def flush_qdrant() -> int:
    """Delete all points from the Qdrant collection. Returns count deleted."""
    client = _get_qdrant_client()
    collection = settings.qdrant_collection

    # Check if collection exists
    collections = await client.get_collections()
    names = [c.name for c in collections.collections]

    if collection not in names:
        logger.info("Qdrant collection does not exist, nothing to flush", collection=collection)
        return 0

    # Get current count before deletion
    info = await client.get_collection(collection)
    before_count = info.points_count

    if before_count == 0:
        logger.info("Qdrant collection already empty", collection=collection)
        return 0

    # Delete all points — empty Filter() matches everything
    from qdrant_client.models import Filter
    await client.delete(
        collection_name=collection,
        points_selector=Filter()
    )

    logger.info("Qdrant flushed", collection=collection, deleted=before_count)
    return before_count


async def flush_neondb() -> dict[str, int]:
    """Truncate all rows from NeonDB chunks and documents tables.

    Returns {"chunks": N, "documents": M}.
    """
    import asyncpg

    conn = await asyncpg.connect(settings.neon_database_url, timeout=15)
    try:
        # Count before delete for reporting
        chunks_before = await conn.fetchval("SELECT COUNT(*) FROM chunks")
        docs_before = await conn.fetchval("SELECT COUNT(*) FROM documents")

        # Delete chunks first (FK constraint), then documents
        await conn.execute("DELETE FROM chunks")
        await conn.execute("DELETE FROM documents")

        logger.info("NeonDB flushed", chunks_deleted=chunks_before, documents_deleted=docs_before)
        return {"chunks": chunks_before, "documents": docs_before}
    finally:
        await conn.close()


async def flush_all() -> dict[str, any]:
    """Flush Qdrant and NeonDB. S3 data is preserved.

    Returns a summary dict for CLI reporting.
    """
    logger.warning("FLUSH started — deleting all Qdrant points and NeonDB records. S3 data is preserved.")

    qdrant_deleted = await flush_qdrant()
    neondb_deleted = await flush_neondb()

    result = {
        "qdrant_points_deleted": qdrant_deleted,
        "neondb_chunks_deleted": neondb_deleted["chunks"],
        "neondb_documents_deleted": neondb_deleted["documents"],
    }

    logger.warning("FLUSH complete", **result)
    return result
