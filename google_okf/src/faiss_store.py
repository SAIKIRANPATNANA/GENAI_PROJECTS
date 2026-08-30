"""Minimal direct FAISS wrapper.

We deliberately avoid langchain_community's FAISS vectorstore: that package
was archived/sunset in June 2026. Talking to faiss directly is a handful of
lines and keeps this project on packages that are still maintained.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import faiss
import numpy as np


class FaissStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.metadata: list[dict] = []

    # Scales every vector to length 1. Combined with FAISS's "inner product" index below,
    # this turns a plain dot-product search into a cosine-similarity search.
    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        return vectors / norms

    def add(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        arr = self._normalize(np.array(vectors, dtype="float32"))
        self.index.add(arr)
        self.metadata.extend(metadata)

    def search(self, query_vector: list[float], k: int = 4) -> list[dict]:
        if not self.metadata:
            return []
        arr = self._normalize(np.array([query_vector], dtype="float32"))
        scores, indices = self.index.search(arr, min(k, len(self.metadata)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            # FAISS fills unused slots with -1 when there are fewer stored vectors than k.
            if idx == -1:
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)
        return results

    def save(self, index_path: Path, meta_path: Path) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        with open(meta_path, "wb") as f:
            pickle.dump({"dim": self.dim, "metadata": self.metadata}, f)

    @classmethod
    def load(cls, index_path: Path, meta_path: Path) -> "FaissStore":
        with open(meta_path, "rb") as f:
            payload = pickle.load(f)
        store = cls(dim=payload["dim"])
        store.index = faiss.read_index(str(index_path))
        store.metadata = payload["metadata"]
        return store
