"""Sparse embedding generator using SPLADE v3 via FastEmbed."""

import asyncio

from fastembed import SparseTextEmbedding, SparseEmbedding

from .config import settings
from .logging import get_logger

logger = get_logger("sparse_embedder")

# Global model instance (lazy-loaded)
_model: SparseTextEmbedding | None = None


def _get_model() -> SparseTextEmbedding:
    global _model
    if _model is None:
        logger.info("Loading sparse embedding model", model=settings.sparse_model)
        _model = SparseTextEmbedding(model_name=settings.sparse_model)
        logger.info("Sparse embedding model loaded")
    return _model


async def embed_text(texts: list[str]) -> list[SparseEmbedding]:
    """Embed text chunks using SPLADE v3.

    Returns:
        List of SparseEmbedding objects (indices + values).
    """
    model = _get_model()

    def _encode() -> list[SparseEmbedding]:
        return list(model.embed(texts))

    logger.info("Generating sparse embeddings", count=len(texts))
    embeddings = await asyncio.to_thread(_encode)
    logger.info("Sparse embeddings generated", count=len(embeddings))
    return embeddings
