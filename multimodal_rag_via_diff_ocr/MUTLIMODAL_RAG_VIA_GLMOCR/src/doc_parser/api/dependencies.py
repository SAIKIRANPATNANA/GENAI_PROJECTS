"""Shared FastAPI dependency providers."""
from __future__ import annotations

from functools import lru_cache

from openai import AsyncOpenAI

from doc_parser.config import Settings, get_settings
from doc_parser.ingestion.embedder import BaseEmbedder, get_embedder
from doc_parser.ingestion.vector_store import QdrantDocumentStore
from doc_parser.retrieval.reranker import BaseReranker, get_reranker


@lru_cache
def get_llm_client() -> AsyncOpenAI:
    """Return a cached LLM client — Groq if GROQ_API_KEY is set, else OpenAI."""
    settings = get_settings()
    if settings.groq_api_key is not None:
        return AsyncOpenAI(
            api_key=settings.groq_api_key.get_secret_value(),
            base_url=settings.groq_base_url,
        )
    api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
    return AsyncOpenAI(api_key=api_key)


# Backward-compat alias used by health.py and any external callers
get_openai_client = get_llm_client


@lru_cache
def get_store() -> QdrantDocumentStore:
    """Return a cached QdrantDocumentStore."""
    return QdrantDocumentStore(get_settings())


@lru_cache
def get_reranker_dep() -> BaseReranker:
    """Return a cached BaseReranker for the configured backend."""
    return get_reranker(get_settings())


@lru_cache
def get_embedder_dep() -> BaseEmbedder:
    """Return a cached BaseEmbedder for the configured provider."""
    return get_embedder(get_settings())
