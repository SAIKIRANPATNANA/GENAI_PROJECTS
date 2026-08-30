"""One-off script: chunk the raw corpus, embed with Jina, and persist a FAISS index.

Run with:  python build_index.py
Requires JINA_API_KEY in .env.
"""
from __future__ import annotations

from src.config import FAISS_INDEX_PATH, FAISS_META_PATH, RAW_DIR, get_settings
from src.faiss_store import FaissStore
from src.ingestion import build_chunks
from src.jina_embeddings import JinaEmbeddings


def main() -> None:
    settings = get_settings()
    embedder = JinaEmbeddings(api_key=settings.jina_api_key, model=settings.jina_embedding_model)

    chunks = build_chunks(RAW_DIR)
    print(f"Loaded {len(chunks)} chunks from {RAW_DIR}")

    texts = [c.text for c in chunks]
    # Send texts to Jina in small batches rather than all at once, in case there
    # end up being a lot of chunks - keeps each request a reasonable size.
    batch_size = 16
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        vectors.extend(embedder.embed_documents(batch))
        print(f"Embedded {min(start + batch_size, len(texts))}/{len(texts)}")

    store = FaissStore(dim=len(vectors[0]))
    metadata = [{"text": c.text, "source": c.source, "chunk_id": c.chunk_id} for c in chunks]
    store.add(vectors, metadata)
    store.save(FAISS_INDEX_PATH, FAISS_META_PATH)
    print(f"Saved FAISS index to {FAISS_INDEX_PATH}")


if __name__ == "__main__":
    main()
