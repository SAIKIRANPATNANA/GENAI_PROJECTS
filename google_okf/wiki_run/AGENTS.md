# AGENTS.md — AI/Cybersecurity Curriculum Wiki Schema

This file is the governing schema for the LLM-maintained wiki.
Read it at the start of every session before touching any wiki files.

---

## Directory Layout

```
stuff/
├── AGENTS.md            ← this file (schema)
├── llm-wiki.md          ← the original pattern description (read-only reference)
├── data/
│   └── raw/             ← IMMUTABLE source documents. Never edit files here.
└── wiki/
    ├── index.md         ← master catalog (update on every ingest)
    ├── log.md           ← append-only activity log
    ├── courses/         ← one page per academic course
    ├── prerequisites/   ← one page per prerequisite/foundation subject
    ├── admin/           ← administrative & policy documents
    └── concepts/        ← synthesized cross-cutting concept pages
```

---

## Page Frontmatter Convention

Every wiki page **must** begin with YAML frontmatter:

```yaml
---
title: "Human-readable title"
category: course | prerequisite | admin | concept
tags: [tag1, tag2]
source_files: [raw/filename.md]   # list of raw files that contributed
last_updated: YYYY-MM-DD
---
```

---

## Ingest Workflow

When adding a new raw source:

1. Read the source file — do **not** modify it.
2. Determine its category: `course`, `prerequisite`, `admin`, or `concept`.
3. Create or update the relevant page in the appropriate `wiki/` subdirectory.
4. Update `wiki/index.md` — add/revise the entry for that page.
5. Update any **cross-reference links** in related pages (e.g., a course page links to its prerequisite pages).
6. Append an entry to `wiki/log.md` using the format:
   `## [YYYY-MM-DD] ingest | <Source File Name>`

---

## Query Workflow

When answering a question:

1. Read `wiki/index.md` first to identify relevant pages.
2. Read those specific pages.
3. Synthesise an answer with inline wiki links as citations.
4. If the answer represents reusable knowledge (a comparison, synthesis, analysis), **file it back** as a new page in `wiki/concepts/`.
5. Append a `query` entry to `wiki/log.md`.

---

## Lint Workflow

Periodically run a health check:
- Orphan pages (no inbound links from any other page or index)
- Missing cross-references (a page mentions a course/concept but doesn't link to it)
- Contradictions between pages
- Stale claims superseded by newer sources
- Important concepts mentioned but lacking their own page

Append a `lint` entry to `wiki/log.md` after each pass.

---

## Category Definitions

| Category       | Description                                                  | Directory           |
|----------------|--------------------------------------------------------------|---------------------|
| `course`       | A taught academic course with code, outcomes, prerequisites  | `wiki/courses/`     |
| `prerequisite` | A foundational subject (coding, stats) required by courses  | `wiki/prerequisites/`|
| `admin`        | Policy, grading, deadlines — no subject-matter content      | `wiki/admin/`       |
| `concept`      | LLM-synthesised cross-cutting topic pages (not raw sources) | `wiki/concepts/`    |

---

## Linking Convention

- Use standard markdown relative links: `[Machine Learning](../courses/machine_learning.md)`
- Always link course pages to their prerequisite pages and vice versa.
- The index lists every page; every page links back to the index.

---

## Immutability Rule

**Never edit files under `data/raw/`.** They are the immutable source of truth.
All LLM-generated content lives exclusively under `wiki/`.
