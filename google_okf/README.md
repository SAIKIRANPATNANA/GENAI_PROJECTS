# OKF + RAG: Basic RAG vs OKF Retrieval vs Hybrid RAG

A runnable demo built for a webinar on Google's **Open Knowledge Format (OKF)**. It answers one
question with real code and measured results, not slides:

> When does organizing knowledge as a **graph of linked concepts** beat plain **vector search over
> documents** - and when doesn't it?

We built a small university-curriculum knowledge base and answered the same 7 questions three
ways - **Basic RAG** (vector search over raw documents), **OKF Retrieval** (walking a hand-curated
concept graph), and **Hybrid RAG** (both, fused) - then scored every answer with an independent
LLM judge (`openevals`).

## Headline result

On questions that require chaining facts across multiple documents (e.g. *"What is the path from
Python to Computer Vision?"*, where the answer is scattered across 5 separate files), Basic RAG
answered fluently and confidently - and got it **wrong**:

| Metric (multi-hop questions only) | Basic RAG | OKF | Hybrid |
|---|---|---|---|
| Helpfulness (sounds right) | 0.95 | 0.90 | 0.90 |
| **Correctness (is right)** | **0.15** | **1.00** | **1.00** |

Full explanation and every other metric: [`docs/10_results_and_findings.md`](docs/10_results_and_findings.md).

## Read the docs

Start here: **[`docs/00_INDEX.md`](docs/00_INDEX.md)** - 11 short docs, in reading order, that
explain everything from first principles: what OKF actually is, where the whole idea came from
(Andrej Karpathy's "LLM Wiki"), why plain RAG struggles on certain questions (with a real captured
failure, not a hypothetical), the full architecture, and every evaluation metric explained on its
own with worked examples.

## What's in here

Three [LangGraph](https://langchain-ai.github.io/langgraph/) pipelines over the same knowledge:

```text
data/raw/*.md  (10 documents) ---> Basic RAG   (FAISS + Jina rerank)
data/okf/**/*.md (concept graph) -> OKF Retrieval (graph traversal, no vector search)
both -----------------------------> Hybrid RAG  (fused)
```

Each has its own Streamlit app, and each shows the retrieved evidence *before* the answer - this
is a teaching tool, not a chatbot.

| Stack piece | Choice |
|---|---|
| Knowledge format | Google Open Knowledge Format (OKF) v0.2 |
| Embeddings / reranker | Jina `jina-embeddings-v3` / `jina-reranker-v3.5` |
| Vector store | FAISS (direct) |
| Orchestration | LangGraph `StateGraph` |
| LLM | Groq `openai/gpt-oss-120b` |
| Evaluation | `openevals` (LLM-as-judge) + LangSmith Datasets/Experiments |

## Quickstart

```bash
# 1. Configure keys
cp .env.example .env   # fill in GROQ_API_KEY and JINA_API_KEY at minimum

# 2. Install
uv pip install -r requirements.txt

# 3. Build the vector index (needs JINA_API_KEY)
python build_index.py

# 4. Try each system live
streamlit run 1_basic_rag_app.py
streamlit run 2_okf_rag_app.py
streamlit run 3_hybrid_rag_app.py

# 5. Reproduce the metric comparison
python run_evaluation.py        # local run -> tests/eval_results.json
python run_langsmith_eval.py    # same comparison as 3 LangSmith Experiments on 1 Dataset
```

## Repo map

```text
data/raw/          10 source documents (deliberately scattered facts - see docs/06)
data/okf/           the same knowledge, curated as an OKF bundle - see docs/04
src/                all pipeline/retrieval/eval code - see docs/08 for a full walkthrough
tests/               the fixed 7-question eval set
docs/                start at docs/00_INDEX.md
1_basic_rag_app.py, 2_okf_rag_app.py, 3_hybrid_rag_app.py   Streamlit demos
build_index.py, run_evaluation.py, run_langsmith_eval.py    entry-point scripts
```

Full breakdown with a diagram: [`docs/01_project_overview.md`](docs/01_project_overview.md).
