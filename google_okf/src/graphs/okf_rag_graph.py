"""OKF concept-graph retrieval as a LangGraph StateGraph: match_concept -> traverse -> generate."""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.config import OKF_DIR
from src.llm import get_llm
from src.okf_graph import OkfGraph
from src.okf_retrieval import match_concepts
from src.okf_retrieval import traverse as traverse_concepts

SYSTEM_PROMPT = """You are a university curriculum assistant. Answer the question using ONLY the
concept knowledge and relationship path below, drawn from the curriculum's OKF knowledge bundle.
Explain the relationship path explicitly when one is given. If the knowledge below does not
cover the question, say so plainly instead of guessing."""


class OkfRagState(TypedDict):
    question: str
    matched_concepts: list[str]
    path: list[str]
    concepts_context: list[dict]
    answer: str


def build_graph(max_hops: int = 3):
    okf_graph = OkfGraph.from_bundle(OKF_DIR)
    llm = get_llm()

    # Step 1: work out which concept(s) the question is about.
    def match_concept(state: OkfRagState) -> dict:
        return {"matched_concepts": match_concepts(state["question"], okf_graph)}

    # Step 2: walk the concept graph from there to build the path/context.
    def traverse(state: OkfRagState) -> dict:
        return traverse_concepts(state["matched_concepts"], okf_graph, max_hops=max_hops)

    # Step 3: ask the LLM to answer using the path and concepts traverse() found.
    def generate(state: OkfRagState) -> dict:
        path_str = " -> ".join(state["path"]) if state["path"] else "no path found"
        concept_block = "\n\n".join(
            f"Concept: {c['title']}\nDescription: {c['description']}\n{c['body']}" for c in state["concepts_context"]
        )
        prompt = (
            f"{SYSTEM_PROMPT}\n\n=== RELATIONSHIP PATH ===\n{path_str}"
            f"\n\n=== CONCEPT KNOWLEDGE ===\n{concept_block}"
            f"\n\n=== QUESTION ===\n{state['question']}"
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}

    graph = StateGraph(OkfRagState)
    graph.add_node("match_concept", match_concept)
    graph.add_node("traverse", traverse)
    graph.add_node("generate", generate)
    graph.add_edge(START, "match_concept")
    graph.add_edge("match_concept", "traverse")
    graph.add_edge("traverse", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
