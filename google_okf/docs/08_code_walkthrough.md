# 08. Code Walkthrough

This doc goes file by file through `src/`. If doc 07 was the map, this is the tour.

## 8.1 The modules

### `config.py`
Loads `.env`, defines all paths (`RAW_DIR`, `OKF_DIR`, `FAISS_INDEX_PATH`, ...) and a `Settings`
dataclass with every model name/API key, each with a sane default. Nothing else in the codebase
reads an environment variable directly - it all goes through `get_settings()`.

### `jina_embeddings.py`
A ~40-line direct client for `POST https://api.jina.ai/v1/embeddings`. Two methods:
`embed_documents()` (used when building the index, `task=retrieval.passage`) and `embed_query()`
(used at question time, `task=retrieval.query`). These are deliberately different API calls, not
the same embedding reused twice - see doc 07 for why that matters.

### `jina_reranker.py`
Same pattern, for `POST https://api.jina.ai/v1/rerank`. Takes a question and a list of candidate
texts, returns them reordered with a `relevance_score`. Used by both Basic RAG and Hybrid RAG's
vector-retrieval step, never by OKF retrieval (there's nothing to rerank - a graph traversal
either finds a path or it doesn't).

### `faiss_store.py`
A minimal wrapper around `faiss.IndexFlatIP` (inner product on L2-normalized vectors = cosine
similarity). `add()`, `search()`, `save()`/`load()` to/from disk (an index file + a pickled
metadata list, since `IndexFlatIP` has no idea what a "document" is - we keep the text/source
alongside it ourselves).

### `llm.py`
Two tiny factory functions: `get_llm()` (the generation model, `GROQ_MODEL`) and `get_judge_llm()`
(a separate model/key, `GROQ_JUDGE_MODEL`/`JUDGE_GROQ_API_KEY`, used only by the evaluators in
doc 09).

### `ingestion.py`
Loads every `.md` file in `data/raw/`, splits on blank lines into paragraphs, and greedily packs
paragraphs into ~600-character chunks (splitting only if a single paragraph is longer than that).
Simple on purpose - the point of this project isn't chunking strategy, and a naive paragraph
packer is transparent enough that "why did this chunk get retrieved" stays easy to answer.

### `okf_loader.py`
Parses the OKF bundle: splits YAML frontmatter from the Markdown body, and walks the body line by
line tracking the current `##` heading, tagging every Markdown link it finds with an edge type
based on that heading (`Prerequisites` -> `requires`, everything else -> `related`). See doc 04 for
a full example.

### `okf_graph.py`
Wraps the parsed concepts/edges in a `networkx.DiGraph` and exposes the operations retrieval
needs: `prerequisite_chain` (BFS outward along `requires` edges), `study_path` (the full
chronological order between two named concepts), `related`, `backlinks`, and `render_html` (a
PyVis interactive graph for the Streamlit app).

### `okf_search.py`
A transparent keyword scorer: `5*title_match + 3*tag_match + 2*description_match + 1*body_match`.
Used as the fallback when a question doesn't literally name a concept (see `okf_retrieval.py`
below).

### `okf_retrieval.py`
Shared logic used by *both* the OKF-only and Hybrid pipelines, so the matching/traversal behavior
never drifts between them: `match_concepts()` (find concept(s) named in the question, or fall back
to keyword search) and `traverse()` (walk the graph from the matched concept(s)).

### `evaluation.py` / `langsmith_eval.py`
See doc 09 in full - the metric-comparison harness, in a local-only version and a LangSmith
Dataset+Experiments version.

## 8.2 The two bugs we actually hit

Worth documenting honestly, because both taught something real about graph modeling and about
working with fast-inference LLM APIs.

### Bug 1: shortest path skipped a real intermediate concept

`study_path()` originally used `networkx.shortest_path()` to find the study order between two
named concepts. First test: `study_path('python', 'computer-vision')` returned
`[python, machine-learning, deep-learning, computer-vision]` - **missing Statistics.**

The cause: `machine-learning.md` legitimately lists **two** direct prerequisites - Statistics
*and* Python (matching the raw document, which says "requires Statistics and Python"). That means
the graph has a direct `python -> requires -> machine-learning` edge *in addition to*
`python -> requires -> statistics -> requires -> machine-learning`. Both are true facts. But
"shortest path" by hop-count will always prefer the direct 3-hop route over the fuller 4-hop one -
even though the fuller one is the more complete study order.

Fix: use the **longest** simple path between the two concepts instead
(`nx.all_simple_paths(...)`, `max(paths, key=len)`), on the reasoning that for this specific
teaching use case, we want the fullest justified chain, not merely *a* valid one. This is a small
but genuine lesson in graph modeling: shortest-path algorithms optimize for hop count, and a
richly-connected prerequisite graph (where an advanced concept can name a "shortcut" prerequisite
that's technically also reachable the long way) will surface exactly this kind of surprise.

### Bug 2: the judge model's forced tool call kept failing

Running `openevals`' evaluators through `openai/gpt-oss-120b` (our generation model) on Groq
intermittently failed with `Tool choice is required, but model did not call a tool` or
`missing properties: 'score'`. `openevals` scores answers by forcing the judge model into a
structured-output tool call; `gpt-oss-120b` would sometimes write out its full reasoning as plain
text instead of - or in addition to, malformed - the required tool call, and Groq rejects that.

Fix: use a **separate, smaller judge model** (`openai/gpt-oss-20b`), which called the tool
correctly and consistently in testing, on its own API key so a full eval run doesn't compete with
generation for the same rate limit. Even so, judge calls occasionally hit Groq's per-minute or
per-day token limits during a long run, so `evaluation.py::_safe_score()` retries each judge call
up to 4 times (with a longer backoff specifically for rate-limit errors) before recording the
score as missing rather than crashing the whole comparison. Full story in doc 09.

## 8.3 Entry-point scripts

| Script | What it does |
|---|---|
| `build_index.py` | Chunks `data/raw/`, embeds every chunk via Jina, writes the FAISS index + metadata to `data/processed/` |
| `run_evaluation.py` | Runs all 3 pipelines against the 7 fixed questions, scores each with 4 `openevals` metrics, prints a comparison table, writes `tests/eval_results.json` |
| `run_langsmith_eval.py` | Same comparison, but uploads the questions as a LangSmith Dataset and runs each pipeline as its own LangSmith Experiment |
| `1_basic_rag_app.py` / `2_okf_rag_app.py` / `3_hybrid_rag_app.py` | Streamlit apps - one per pipeline, each showing the retrieved evidence *before* the answer, never just the final text |
