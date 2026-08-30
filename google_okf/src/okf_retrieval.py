"""Shared OKF concept-match + graph-traversal helpers used by both the OKF-only and Hybrid pipelines."""
from __future__ import annotations

from src.okf_graph import OkfGraph
from src.okf_search import search_concepts


def mentioned_concepts(question: str, okf_graph: OkfGraph) -> list[str]:
    """Concept ids whose title literally appears in the question, ordered by position in the text."""
    q_lower = question.lower()
    mentioned = []
    for concept_id, concept in okf_graph.concepts.items():
        if concept.type != "Concept":
            continue
        if concept.title.lower() in q_lower:
            mentioned.append((q_lower.index(concept.title.lower()), concept_id))
    mentioned.sort(key=lambda item: item[0])
    return [concept_id for _, concept_id in mentioned]


def match_concepts(question: str, okf_graph: OkfGraph) -> list[str]:
    """Find the concept(s) the question is about: direct title mentions first, else keyword search."""
    mentioned = mentioned_concepts(question, okf_graph)
    if mentioned:
        return [mentioned[0], mentioned[-1]] if len(mentioned) >= 2 else [mentioned[0]]
    scored = search_concepts(question, okf_graph.concepts, top_k=1)
    return [concept_id for concept_id, _ in scored]


def traverse(matched_concepts: list[str], okf_graph: OkfGraph, max_hops: int = 3) -> dict:
    """Follow 'requires' edges from the matched concept(s) and collect related context."""
    if not matched_concepts:
        return {"path": [], "concepts_context": []}

    if len(matched_concepts) == 2:
        # Question named two concepts (e.g. "path from Python to Computer Vision") -
        # find the study-order path connecting them, trying both directions.
        start, end = matched_concepts
        path = okf_graph.study_path(start, end) or okf_graph.study_path(end, start) or matched_concepts
    else:
        # Question named (or matched to) just one concept - walk outward from it
        # to find everything that leads up to it.
        path = okf_graph.prerequisite_chain(matched_concepts[0], max_hops=max_hops)

    related_ids: set[str] = set()
    for concept_id in path:
        related_ids.update(okf_graph.related(concept_id))
    all_ids = list(dict.fromkeys(path + list(related_ids)))

    concepts_context = [
        {
            "id": concept_id,
            "title": okf_graph.concepts[concept_id].title,
            "description": okf_graph.concepts[concept_id].description,
            "source": okf_graph.concepts[concept_id].source,
            "body": okf_graph.concepts[concept_id].body,
        }
        for concept_id in all_ids
        if concept_id in okf_graph.concepts
    ]
    return {"path": path, "concepts_context": concepts_context}
