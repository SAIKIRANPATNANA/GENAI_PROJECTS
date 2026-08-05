"""Configuration management using pydantic-settings."""
from __future__ import annotations

import logging
from pathlib import Path

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    """Return the repository root, independent of the current working directory."""
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Parser backend
    parser_backend: str = "docling"  # "cloud" | "ollama" | "docling"
    z_ai_api_key: SecretStr | None = None
    log_level: str = "INFO"
    output_dir: str = "./output"
    config_yaml_path: str = "config.yaml"

    # OpenAI (optional when using Groq)
    openai_api_key: SecretStr | None = None
    openai_llm_model: str = "gpt-4o"

    # Groq (free-tier alternative to OpenAI)
    # Sign up at https://console.groq.com — no credit card needed
    # Vision model  : qwen/qwen3.6-27b   (image captioning)
    # Text LLM model: meta/llama-3.3-70b-versatile  (table/formula/algorithm captions)
    groq_api_key: SecretStr | None = None
    groq_vision_model: str = "qwen/qwen3.6-27b"
    groq_text_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Embedding (provider-agnostic)
    embedding_provider: str = "openai"  # "openai" | "gemini"
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072
    gemini_api_key: SecretStr | None = None

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None
    qdrant_collection_name: str = "multimodal_rag_v3_docs"

    # Reranker
    reranker_backend: str = "openai"  # "jina" | "openai" | "bge" | "qwen"
    reranker_top_n: int = 5
    jina_api_key: SecretStr | None = None

    # Feature flags
    image_caption_enabled: bool = True

    # Captioning tuning
    table_max_tokens: int = 2000
    table_max_input_chars: int = 12_000
    image_max_tokens: int = 800
    table_use_vision: bool = False

    # API server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1

    # Logging
    log_json: bool = False

    @model_validator(mode="after")
    def _validate_backend(self) -> Settings:
        """Enforce backend-specific constraints and auto-set config path."""
        # ── Parser backend ────────────────────────────────────────────────────
        if self.parser_backend == "cloud":
            if self.z_ai_api_key is None:
                raise ValueError(
                    "Z_AI_API_KEY is required when PARSER_BACKEND=cloud"
                )
        elif self.parser_backend in ("ollama", "docling"):
            if self.config_yaml_path == "config.yaml":
                object.__setattr__(self, "config_yaml_path", "ollama/config.yaml")
        else:
            raise ValueError(
                f"PARSER_BACKEND must be 'cloud', 'ollama', or 'docling', got: {self.parser_backend!r}"
            )

        config_path = Path(self.config_yaml_path).expanduser()
        if not config_path.is_absolute():
            config_path = _project_root() / config_path
        object.__setattr__(self, "config_yaml_path", str(config_path))

        # ── LLM / captioning key ──────────────────────────────────────────────
        # Require at least one of: OpenAI or Groq key (unless captioning is disabled)
        if self.image_caption_enabled:
            has_openai = self.openai_api_key is not None
            has_groq = self.groq_api_key is not None
            # Local-only embedding providers also don't need an LLM key for embeddings,
            # but captioning still needs one.  Warn rather than hard-fail so users can
            # set IMAGE_CAPTION_ENABLED=false to skip captioning entirely.
            if not has_openai and not has_groq:
                import warnings
                warnings.warn(
                    "Neither OPENAI_API_KEY nor GROQ_API_KEY is set. "
                    "Image captioning will be disabled automatically. "
                    "Set IMAGE_CAPTION_ENABLED=false to silence this warning.",
                    stacklevel=2,
                )
                object.__setattr__(self, "image_caption_enabled", False)

        return self


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with the given level."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
