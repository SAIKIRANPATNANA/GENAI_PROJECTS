"""Pydantic settings for pipeline configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # S3
    s3_bucket: str = ""
    s3_prefix: str = "documents/"
    aws_region: str = "us-east-1"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "rag_documents"

    # NeonDB / PostgreSQL
    neon_database_url: str = "postgresql://localhost:5432/rag_pipeline"

    # Embedding models
    dense_model: str = "jinaai/jina-embeddings-v5-omni-nano"
    sparse_model: str = "prithivida/Splade_PP_en_v1"

    # GLiNER2 models
    gliner_metadata_model: str = "fastino/gliner2-base-v1"
    gliner_pii_model: str = "fastino/gliner2-privacy-filter-PII-multi"

    # HuggingFace
    hf_token: str = ""

    # arXiv
    arxiv_s3_prefix: str = "arxiv/"

    # Prefect
    prefect_api_url: str = ""
    prefect_api_key: str = ""

    # Pipeline
    concurrency_limit: int = 5
    embedding_batch_size: int = 32
    qdrant_batch_size: int = 100


settings = Settings()

# Export HF_TOKEN to environment for transformers/huggingface_hub
if settings.hf_token:
    import os

    os.environ["HF_TOKEN"] = settings.hf_token
