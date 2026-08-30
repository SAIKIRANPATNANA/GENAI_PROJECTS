"""Build a navigable graph from parsed OKF concepts/edges and provide traversal helpers."""
from __future__ import annotations

from pathlib import Path

import networkx as nx
from pyvis.network import Network

from src.okf_loader import Concept, Edge, load_okf_bundle


class OkfGraph:
    def __init__(self, concepts: dict[str, Concept], edges: list[Edge]):
        self.concepts = concepts
        self.graph = nx.DiGraph()
        for concept_id, concept in concepts.items():
            self.graph.add_node(concept_id, title=concept.title, type=concept.type)
        for edge in edges:
            if edge.target in concepts:
                self.graph.add_edge(edge.source, edge.target, type=edge.type)

    @classmethod
    def from_bundle(cls, bundle_root: Path) -> "OkfGraph":
        concepts, edges = load_okf_bundle(bundle_root)
        return cls(concepts, edges)

    def prerequisite_chain(self, concept_id: str, max_hops: int = 3) -> list[str]:
        """BFS along 'requires' edges: what should I study before `concept_id`."""
        if concept_id not in self.graph:
            return []
        visited = [concept_id]
        frontier = [concept_id]
        for _ in range(max_hops):
            next_frontier = []
            for node in frontier:
                for _, target, data in self.graph.out_edges(node, data=True):
                    if data.get("type") == "requires" and target not in visited:
                        visited.append(target)
                        next_frontier.append(target)
            frontier = next_frontier
            if not frontier:
                break
        return visited

    def study_path(self, start_id: str, end_id: str) -> list[str] | None:
        """Chronological study order from `start_id` to `end_id`, following requires-edges in reverse.

        Uses the longest simple path rather than the shortest: some concepts (e.g. Machine
        Learning) list more than one direct prerequisite, which creates hop-count shortcuts
        that skip a real intermediate concept (e.g. Python -> ML directly, bypassing
        Statistics). The longest simple path returns the fullest justified chain instead.
        """
        requires_graph = nx.DiGraph(
            (u, v) for u, v, d in self.graph.edges(data=True) if d.get("type") == "requires"
        )
        reverse_graph = requires_graph.reverse()
        if start_id not in reverse_graph or end_id not in reverse_graph:
            return None
        paths = list(nx.all_simple_paths(reverse_graph, start_id, end_id))
        if not paths:
            return None
        return max(paths, key=len)

    def related(self, concept_id: str) -> list[str]:
        if concept_id not in self.graph:
            return []
        return [t for _, t, d in self.graph.out_edges(concept_id, data=True) if d.get("type") == "related"]

    def backlinks(self, concept_id: str) -> list[str]:
        if concept_id not in self.graph:
            return []
        return list(self.graph.predecessors(concept_id))

    def render_html(self, output_path: Path) -> Path:
        net = Network(height="600px", width="100%", directed=True, notebook=False, cdn_resources="in_line")
        for node_id, data in self.graph.nodes(data=True):
            net.add_node(node_id, label=data.get("title", node_id), title=data.get("type", ""))
        for source, target, data in self.graph.edges(data=True):
            net.add_edge(source, target, label=data.get("type", ""))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        net.write_html(str(output_path), notebook=False)
        return output_path
