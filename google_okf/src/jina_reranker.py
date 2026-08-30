"""Thin direct client for the Jina AI Reranker API.

Used deliberately to show that reranking alone does not fix multi-hop or
relationship questions: a reranker can only reorder the candidate chunks
it is handed. It cannot pull in a chunk that vector search never retrieved,
and it cannot chain facts that are scattered across separate documents the
way OKF's graph traversal can.
"""
from __future__ import annotations

import requests

JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"


class JinaReranker:
    def __init__(self, api_key: str, model: str = "jina-reranker-v3.5", timeout: int = 60):
        if not api_key:
            raise ValueError("JINA_API_KEY is not set. Copy .env.example to .env and fill it in.")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    # Takes the candidate texts already found by vector search and returns them reordered,
    # best match first, as {"index": position in the original list, "relevance_score": ...}.
    def rerank(self, query: str, documents: list[str], top_n: int | None = None) -> list[dict]:
        if not documents:
            return []
        response = requests.post(
            JINA_RERANK_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json={
                "model": self.model,
                "query": query,
                "documents": documents,
                "top_n": top_n or len(documents),
                "return_documents": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            {"index": item["index"], "relevance_score": item["relevance_score"]}
            for item in payload["results"]
        ]
