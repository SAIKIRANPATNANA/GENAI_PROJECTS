"""Parse an OKF bundle (YAML-frontmatter Markdown files) into concepts + typed edges."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$")

# Which "## Heading" a link sits under determines the edge's semantic type.
EDGE_SECTION_MAP = {
    "prerequisites": "requires",
    "related concepts": "related",
}


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    tags: list[str]
    source: str | None
    body: str
    path: Path


@dataclass
class Edge:
    source: str
    target: str
    type: str


# Every OKF file starts with a YAML block between two "---" lines, followed by the
# Markdown content. This pulls those two parts apart.
def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    frontmatter = yaml.safe_load(parts[1]) or {}
    return frontmatter, parts[2].strip()


# Turns a link like "./machine-learning.md" (relative to the file it's written in)
# into a concept id like "concepts/machine-learning" (relative to the bundle root),
# so the same concept is always referred to by the same id no matter which file links to it.
def _resolve_link(current_path: Path, bundle_root: Path, link_target: str) -> str:
    resolved = (current_path.parent / link_target).resolve()
    rel = resolved.relative_to(bundle_root.resolve())
    return rel.with_suffix("").as_posix()


def _extract_edges(body: str, current_id: str, current_path: Path, bundle_root: Path) -> list[Edge]:
    edges: list[Edge] = []
    current_section = "body"
    for line in body.splitlines():
        # Remember the most recent "## Heading" seen so far, so any link found below
        # it can be tagged with the right edge type (see EDGE_SECTION_MAP above).
        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            current_section = heading_match.group(1).strip().lower()
            continue
        for _, target in LINK_RE.findall(line):
            target_id = _resolve_link(current_path, bundle_root, target)
            edges.append(Edge(source=current_id, target=target_id, type=EDGE_SECTION_MAP.get(current_section, "related")))
    return edges


def load_okf_bundle(bundle_root: Path) -> tuple[dict[str, Concept], list[Edge]]:
    concepts: dict[str, Concept] = {}
    edges: list[Edge] = []

    for path in sorted(bundle_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter, body = _split_frontmatter(text)
        concept_id = path.relative_to(bundle_root).with_suffix("").as_posix()

        concepts[concept_id] = Concept(
            id=concept_id,
            type=frontmatter.get("type", "Concept"),
            title=frontmatter.get("title", path.stem),
            description=frontmatter.get("description", ""),
            tags=frontmatter.get("tags", []) or [],
            source=frontmatter.get("source"),
            body=body,
            path=path,
        )
        edges.extend(_extract_edges(body, concept_id, path, bundle_root))

    return concepts, edges
