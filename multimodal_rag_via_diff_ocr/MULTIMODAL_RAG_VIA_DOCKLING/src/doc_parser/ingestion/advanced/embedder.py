"""Dense embedding generator using jina-omni-nano via sentence-transformers."""

import asyncio

import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

from .config import settings
from .logging import get_logger

logger = get_logger("embedder")

# Global model instance (lazy-loaded)
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading dense embedding model", model=settings.dense_model)
        _model = SentenceTransformer(
            settings.dense_model,
            trust_remote_code=True,
            model_kwargs={"default_task": "retrieval"},
        )
        logger.info("Dense embedding model loaded")
    return _model


async def embed_text(texts: list[str]) -> np.ndarray:
    """Embed text chunks using jina-omni-nano.

    Returns:
        numpy array of shape (len(texts), 768).
    """
    model = _get_model()

    def _encode() -> np.ndarray:
        return model.encode_document(texts)

    logger.info("Embedding text chunks", count=len(texts))
    embeddings = await asyncio.to_thread(_encode)
    logger.info("Text chunks embedded", count=len(texts), shape=embeddings.shape)
    return embeddings


async def embed_image(images: list[Image.Image]) -> np.ndarray:
    """Embed image chunks using jina-omni-nano.

    Returns:
        numpy array of shape (len(images), 768).
    """
    model = _get_model()

    def _encode() -> np.ndarray:
        return model.encode_document(images)

    logger.info("Embedding image chunks", count=len(images))
    embeddings = await asyncio.to_thread(_encode)
    logger.info("Image chunks embedded", count=len(images), shape=embeddings.shape)
    return embeddings


async def embed_query(text: str) -> np.ndarray:
    """Embed a query text for retrieval.

    Returns:
        numpy array of shape (768,).
    """
    model = _get_model()

    def _encode() -> np.ndarray:
        return model.encode_query(text)

    embedding = await asyncio.to_thread(_encode)
    return embedding
