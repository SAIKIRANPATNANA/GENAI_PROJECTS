"""Thin direct client for the Jina AI embeddings API.

We call the REST API directly instead of using langchain_community's
JinaEmbeddings wrapper: langchain_community was archived in June 2026, and
even before that its Jina wrapper only supported the older v2 model with no
support for v3's task-specific LoRA adapters (retrieval.query vs
retrieval.passage), which this project relies on for asymmetric search.
"""
from __future__ import annotations

import requests

JINA_EMBEDDINGS_URL = "https://api.jina.ai/v1/embeddings"


class JinaEmbeddings:
    def __init__(self, api_key: str, model: str = "jina-embeddings-v3", timeout: int = 60):
        if not api_key:
            raise ValueError("JINA_API_KEY is not set. Copy .env.example to .env and fill it in.")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def _embed(self, texts: list[str], task: str) -> list[list[float]]:
        if not texts:
            return []
        response = requests.post(
            JINA_EMBEDDINGS_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json={"model": self.model, "task": task, "input": texts},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        # The API doesn't guarantee results come back in the same order we sent them,
        # so line them back up by their original position before returning.
        ordered = sorted(payload["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in ordered]

    # Used when building the index: embeds the documents/chunks that will be searched.
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, task="retrieval.passage")

    # Used at question time: embeds the user's question with a different task setting,
    # so the model encodes "a search query" rather than "a passage" (see module docstring).
    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], task="retrieval.query")[0]
