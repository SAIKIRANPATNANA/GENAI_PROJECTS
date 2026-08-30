"""Groq LLM factory. Isolated so the rest of the app never touches the provider directly."""
from __future__ import annotations

from langchain_groq import ChatGroq

from src.config import get_settings


def get_llm(temperature: float = 0.1) -> ChatGroq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Copy .env.example to .env and fill it in.")
    return ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=temperature)


def get_judge_llm(temperature: float = 0.0) -> ChatGroq:
    """A separate model (and, if configured, a separate API key) for openevals judging,
    kept distinct from the generation model so a full eval run doesn't share/exhaust the
    same Groq rate limit as generation."""
    settings = get_settings()
    if not settings.groq_judge_api_key:
        raise ValueError("GROQ_API_KEY is not set. Copy .env.example to .env and fill it in.")
    return ChatGroq(model=settings.groq_judge_model, api_key=settings.groq_judge_api_key, temperature=temperature)
