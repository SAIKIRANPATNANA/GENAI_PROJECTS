"""Hybrid RAG: fan-out into vector retrieval (+ rerank) and OKF retrieval, fuse, then generate."""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.config import FAISS_INDEX_PATH, FAISS_META_PATH, OKF_DIR, get_settings
from src.faiss_store import FaissStore
from src.jina_embeddings import JinaEmbeddings
from src.jina_reranker import JinaReranker
from src.llm import get_llm
from src.okf_graph import OkfGraph
from src.okf_retrieval import match_concepts
from src.okf_retrieval import traverse as traverse_concepts

SYSTEM_PROMPT = """You are a university curriculum assistant. Answer using BOTH evidence types below.
Prefer the raw document evidence for detailed factual claims and citations.
Use the OKF relationship path for questions about order, prerequisites, or how concepts connect.
Do not invent relationships that are not present in the evidence. Cite source documents when used."""


class HybridRagState(TypedDict):
    question: str
    chunks: list[dict]
    matched_concepts: list[str]
    path: list[str]
    concepts_context: list[dict]
    answer: str


def build_graph(top_k: int = 4, candidate_k: int = 10, max_hops: int = 3):
    settings = get_settings()
    embedder = JinaEmbeddings(api_key=settings.jina_api_key, model=settings.jina_embedding_model)
    reranker = JinaReranker(api_key=settings.jina_api_key, model=settings.jina_reranker_model)
    vector_store = FaissStore.load(FAISS_INDEX_PATH, FAISS_META_PATH)
    okf_graph = OkfGraph.from_bundle(OKF_DIR)
    llm = get_llm()

    # Same vector-search-then-rerank step as Basic RAG. Runs in parallel with
    # okf_retrieve below - see the two edges from START near the bottom of this file.
    def vector_retrieve(state: HybridRagState) -> dict:
        query_vector = embedder.embed_query(state["question"])
        candidates = vector_store.search(query_vector, k=candidate_k)
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

    # Same match-then-traverse step as OKF Retrieval, done here as one node
    # since Hybrid doesn't need to show the two steps separately in the UI.
    def okf_retrieve(state: HybridRagState) -> dict:
        matched = match_concepts(state["question"], okf_graph)
        result = traverse_concepts(matched, okf_graph, max_hops=max_hops)
        return {"matched_concepts": matched, **result}

    # Combines both kinds of evidence into one clearly-labeled prompt and generates the answer.
    def fuse_and_generate(state: HybridRagState) -> dict:
        raw_evidence = "\n\n".join(f"[source: {c['source']}]\n{c['text']}" for c in state["chunks"])
        path_str = " -> ".join(state["path"]) if state["path"] else "no path found"
        concept_block = "\n".join(f"- {c['title']}: {c['description']}" for c in state["concepts_context"])
        prompt = (
            f"{SYSTEM_PROMPT}\n\n=== RAW DOCUMENT EVIDENCE ===\n{raw_evidence}"
            f"\n\n=== OKF RELATIONSHIP PATH ===\n{path_str}"
            f"\n\n=== OKF CONCEPT EVIDENCE ===\n{concept_block}"
            f"\n\n=== QUESTION ===\n{state['question']}"
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}

    graph = StateGraph(HybridRagState)
    graph.add_node("vector_retrieve", vector_retrieve)
    graph.add_node("okf_retrieve", okf_retrieve)
    graph.add_node("fuse_and_generate", fuse_and_generate)
    # Both of these start from START, so LangGraph runs them at the same time
    # rather than one after the other.
    graph.add_edge(START, "vector_retrieve")
    graph.add_edge(START, "okf_retrieve")
    graph.add_edge("vector_retrieve", "fuse_and_generate")
    graph.add_edge("okf_retrieve", "fuse_and_generate")
    graph.add_edge("fuse_and_generate", END)
    return graph.compile()
