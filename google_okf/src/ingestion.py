"""Load and chunk the raw source documents used by Basic RAG."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: str


def load_raw_documents(raw_dir: Path) -> list[tuple[str, str]]:
    return [(path.name, path.read_text(encoding="utf-8")) for path in sorted(raw_dir.glob("*.md"))]


# Splits one document into chunks small enough to embed and retrieve individually.
# Strategy: greedily pack whole paragraphs together up to max_chars, so related
# sentences stay in the same chunk. A single paragraph longer than max_chars gets
# sliced into overlapping pieces instead, so no chunk ever exceeds the limit.
def chunk_text(text: str, source: str, max_chars: int = 600, overlap: int = 80) -> list[Chunk]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    raw_chunks: list[str] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if len(candidate) <= max_chars:
            # Still fits - add this paragraph to the chunk being built.
            buffer = candidate
            continue
        if buffer:
            raw_chunks.append(buffer)
        if len(paragraph) <= max_chars:
            buffer = paragraph
        else:
            # This one paragraph alone is too big - cut it into overlapping pieces
            # so no sentence is left stranded exactly on a cut boundary.
            for start in range(0, len(paragraph), max_chars - overlap):
                raw_chunks.append(paragraph[start : start + max_chars])
            buffer = ""
    if buffer:
        raw_chunks.append(buffer)

    return [Chunk(text=t, source=source, chunk_id=f"{source}::{i}") for i, t in enumerate(raw_chunks)]


def build_chunks(raw_dir: Path) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for source, text in load_raw_documents(raw_dir):
        all_chunks.extend(chunk_text(text, source))
    return all_chunks
