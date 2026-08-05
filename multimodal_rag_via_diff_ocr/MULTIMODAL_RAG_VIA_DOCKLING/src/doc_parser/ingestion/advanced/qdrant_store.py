"""Qdrant vector store for dense + sparse hybrid vectors."""

from typing import Any
from uuid import uuid4

import numpy as np
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseVector,
    VectorParams,
    SparseVectorParams,
    Prefetch,
    FusionQuery,
    Fusion,
)

from .config import settings
from .logging import get_logger
from .models import QdrantPayload

logger = get_logger("qdrant_store")

# Global client instance (lazy-loaded)
_client: AsyncQdrantClient | None = None


def _get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
    return _client


async def ensure_collection() -> None:
    """Create Qdrant collection if it doesn't exist."""
    client = _get_client()
    collections = await client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if settings.qdrant_collection not in collection_names:
        logger.info("Creating Qdrant collection", collection=settings.qdrant_collection)
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config={
                "dense": VectorParams(size=768, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(),
            },
        )
        logger.info("Qdrant collection created")


async def upsert_chunks(
    dense_embeddings: np.ndarray,
    sparse_embeddings: list[Any],
    payloads: list[QdrantPayload],
) -> list[str]:
    """Upsert chunks with dense + sparse vectors to Qdrant.

    Args:
        dense_embeddings: numpy array of shape (N, 768).
        sparse_embeddings: list of SparseEmbedding objects.
        payloads: list of QdrantPayload objects.

    Returns:
        List of point IDs (UUIDs).
    """
    client = _get_client()
    await ensure_collection()

    point_ids = [str(uuid4()) for _ in range(len(payloads))]

    points = []
    for i, (point_id, dense_emb, sparse_emb, payload) in enumerate(
        zip(point_ids, dense_embeddings, sparse_embeddings, payloads)
    ):
        # Convert sparse embedding to Qdrant SparseVector
        sparse_vector = SparseVector(
            indices=sparse_emb.indices.tolist(),
            values=sparse_emb.values.tolist(),
        )

        points.append(PointStruct(
            id=point_id,
            vector={
                "dense": dense_emb.tolist(),
                "sparse": sparse_vector,
            },
            payload=payload.model_dump(),
        ))

    logger.info("Upserting to Qdrant", count=len(points))
    await client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )
    logger.info("Upserted to Qdrant", count=len(points))
    return point_ids


async def hybrid_search(
    dense_query: np.ndarray,
    sparse_query: Any,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Perform hybrid search using Qdrant native RRF.

    Args:
        dense_query: Dense query embedding (768,).
        sparse_query: Sparse query embedding.
        limit: Number of results.

    Returns:
        List of search results with payload.
    """
    client = _get_client()

    sparse_vector = SparseVector(
        indices=sparse_query.indices.tolist(),
        values=sparse_query.values.tolist(),
    )

    response = await client.query_points(
        collection_name=settings.qdrant_collection,
        prefetch=[
            Prefetch(query=dense_query.tolist(), using="dense", limit=limit * 2),
            Prefetch(query=sparse_vector, using="sparse", limit=limit * 2),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=limit,
        with_payload=True,
    )

    results = []
    for point in response.points:
        results.append({
            "id": point.id,
            "score": point.score,
            "payload": point.payload,
        })
    return results
