"""Basic RAG as a LangGraph StateGraph: retrieve (vector search + rerank) -> generate."""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.config import FAISS_INDEX_PATH, FAISS_META_PATH, get_settings
from src.faiss_store import FaissStore
from src.jina_embeddings import JinaEmbeddings
from src.jina_reranker import JinaReranker
from src.llm import get_llm

SYSTEM_PROMPT = """You are a university curriculum assistant. Answer the question using ONLY the
retrieved chunks below. Cite the source document for each fact you use, like [source: file.md].
If the chunks don't fully answer the question, say plainly what is missing instead of guessing."""


class BasicRagState(TypedDict):
    question: str
    chunks: list[dict]
    answer: str


def build_graph(top_k: int = 4, candidate_k: int = 10):
    settings = get_settings()
    embedder = JinaEmbeddings(api_key=settings.jina_api_key, model=settings.jina_embedding_model)
    reranker = JinaReranker(api_key=settings.jina_api_key, model=settings.jina_reranker_model)
    store = FaissStore.load(FAISS_INDEX_PATH, FAISS_META_PATH)
    llm = get_llm()

    # Step 1: embed the question, find the closest chunks in FAISS, then rerank
    # the top candidates so the most relevant ones end up first.
    def retrieve(state: BasicRagState) -> dict:
        query_vector = embedder.embed_query(state["question"])
        candidates = store.search(query_vector, k=candidate_k)
        if not candidates:
            return {"chunks": []}

        rerank_results = reranker.rerank(state["question"], [c["text"] for c in candidates], top_n=top_k)
        chunks = []
        for r in rerank_results:
            chunk = dict(candidates[r["index"]])
            chunk["vector_score"] = chunk.pop("score")
            chunk["rerank_score"] = r["relevance_score"]
            chunks.append(chunk)
        return {"chunks": chunks}

    # Step 2: ask the LLM to answer using only the chunks retrieve() found.
    def generate(state: BasicRagState) -> dict:
        evidence = "\n\n".join(f"[source: {c['source']}]\n{c['text']}" for c in state["chunks"])
        prompt = f"{SYSTEM_PROMPT}\n\n=== RETRIEVED CHUNKS ===\n{evidence}\n\n=== QUESTION ===\n{state['question']}"
        response = llm.invoke(prompt)
        return {"answer": response.content}

    graph = StateGraph(BasicRagState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
