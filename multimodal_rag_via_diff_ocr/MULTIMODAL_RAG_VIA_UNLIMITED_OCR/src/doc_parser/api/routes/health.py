"""GET /health and GET /collections endpoints."""
from __future__ import annotations

from loguru import logger
from fastapi import APIRouter

from doc_parser.api.dependencies import get_store
from doc_parser.api.schemas import CollectionsResponse, DeleteCollectionResponse, HealthResponse
from doc_parser.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Ping Qdrant and the configured LLM provider to verify connectivity."""
    settings = get_settings()
    store = get_store()
    reranker_backend = settings.reranker_backend

    # ── Qdrant ────────────────────────────────────────────────────────────────
    qdrant_status: str
    try:
        await store._client.get_collections()
        qdrant_status = "ok"
    except Exception as exc:
        logger.warning("Qdrant health check failed: {}", exc)
        qdrant_status = f"error: {exc}"

    # ── LLM / embedding provider ──────────────────────────────────────────────
    # For local embeddings there is no API to ping; report immediately.
    # For cloud providers (OpenAI or Groq), do a tiny embedding call.
    openai_status: str
    if settings.embedding_provider == "local":
        openai_status = f"local embeddings ({settings.embedding_model}) — ok"
    else:
        from openai import AsyncOpenAI
        if settings.groq_api_key is not None:
            provider_label = "Groq"
            llm_client = AsyncOpenAI(
                api_key=settings.groq_api_key.get_secret_value(),
                base_url=settings.groq_base_url,
            )
        else:
            provider_label = "OpenAI"
            api_key = (
                settings.openai_api_key.get_secret_value()
                if settings.openai_api_key
                else None
            )
            llm_client = AsyncOpenAI(api_key=api_key)

        try:
            await llm_client.embeddings.create(
                model=settings.embedding_model,
                input=["ping"],
                dimensions=8,
            )
            openai_status = f"{provider_label} — ok"
        except Exception as exc:
            logger.warning("{} health check failed: {}", provider_label, exc)
            openai_status = f"{provider_label} error: {exc}"

    overall = "ok" if qdrant_status == "ok" and "error" not in openai_status else "degraded"
    return HealthResponse(
        status=overall,
        qdrant=qdrant_status,
        openai=openai_status,
        reranker_backend=reranker_backend,
    )




@router.get("/collections", response_model=CollectionsResponse)
async def list_collections() -> CollectionsResponse:
    """List all Qdrant collection names."""
    store = get_store()
    response = await store._client.get_collections()
    names = [c.name for c in response.collections]
    return CollectionsResponse(collections=names)


@router.delete("/collections/{collection_name}", response_model=DeleteCollectionResponse)
async def delete_collection(collection_name: str) -> DeleteCollectionResponse:
    """Permanently delete a Qdrant collection by name.

    This is irreversible — re-ingestion is required to rebuild.
    Returns 200 with deleted=False if the collection does not exist.
    """
    store = get_store()
    deleted = await store.delete_collection(collection_name)
    return DeleteCollectionResponse(
        collection=collection_name,
        deleted=deleted,
        message="Collection deleted." if deleted else "Collection not found.",
    )
