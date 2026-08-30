"""Simple, transparent keyword scoring over OKF concepts (title/tags/description/body)."""
from __future__ import annotations

import re

from src.okf_loader import Concept

# How much each kind of match is worth when scoring a concept against a question.
# A word matching the title counts for more than the same word matching the body text.
WEIGHTS = {"title": 5, "tag": 3, "description": 2, "body": 1}


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_concept(query_tokens: set[str], concept: Concept) -> int:
    score = 0
    if query_tokens & _tokenize(concept.title):
        score += WEIGHTS["title"]
    if query_tokens & {t.lower() for t in concept.tags}:
        score += WEIGHTS["tag"]
    if query_tokens & _tokenize(concept.description):
        score += WEIGHTS["description"]
    if query_tokens & _tokenize(concept.body):
        score += WEIGHTS["body"]
    return score


def search_concepts(question: str, concepts: dict[str, Concept], top_k: int = 3) -> list[tuple[str, int]]:
    query_tokens = _tokenize(question)
    scored = [
        (concept_id, score_concept(query_tokens, concept))
        for concept_id, concept in concepts.items()
        if concept.type == "Concept"
    ]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]
