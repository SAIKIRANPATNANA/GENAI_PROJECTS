# Documentation Index

This folder explains the whole project end to end, in plain language, for anyone opening this
repo for the first time. Read the docs in this order - each one builds on the last.

| # | Doc | What it covers |
|---|---|---|
| 01 | [Project Overview](./01_project_overview.md) | What this project is, why it was built, the repo map, how to run it. |
| 02 | [History: LLM Wiki -> OKF](./02_history_llm_wiki_to_okf.md) | Where this whole idea comes from - Andrej Karpathy's "LLM Wiki", explained from first principles, and how Google turned it into a format. |
| 03 | [LLM Wiki vs Knowledge Graph vs GraphRAG vs OKF](./03_llm_wiki_vs_knowledge_graph_vs_graphrag_vs_okf.md) | Four terms people mix up, told apart with one running example. |
| 04 | [What is OKF?](./04_what_is_okf.md) | The Open Knowledge Format itself, dissected line by line, using our own concept files. |
| 05 | [Problems with Traditional RAG](./05_problems_with_traditional_rag.md) | Why plain vector search genuinely struggles on some questions - shown with a real failure we captured, not a hypothetical. |
| 06 | [The Dataset](./06_the_dataset.md) | The 10 source documents, why they're "messy" on purpose, and exactly which facts live where. |
| 07 | [Project Architecture](./07_project_architecture.md) | The full system: 3 pipelines, LangGraph, Jina, Groq, FAISS, Streamlit - with diagrams. |
| 08 | [Code Walkthrough](./08_code_walkthrough.md) | Every file in `src/`, what it does, and the two trickiest bugs we hit while building it. |
| 09 | [Evaluation Methodology](./09_evaluation_methodology.md) | `openevals` + LangSmith, and each of the 4 metrics (helpfulness, groundedness, retrieval relevance, correctness) explained on their own. |
| 10 | [Results & Findings](./10_results_and_findings.md) | The actual numbers, what they mean, and the teaching takeaway. |

Appendix: [`eval_results.md`](./eval_results.md) - raw per-question scores and full answer text from one reference run.

## The one-paragraph version

We built a small university-curriculum knowledge base and answered the same 7 questions three
ways: **Basic RAG** (vector search over raw documents), **OKF Retrieval** (walking a hand-curated
concept graph), and **Hybrid RAG** (both, fused). The dataset was designed so that some questions
force you to chain facts spread across five separate documents. On those questions, Basic RAG
answered fluently and confidently - and got the answer **wrong** (measured correctness: 0.15/1.00).
OKF and Hybrid got it right every time (1.00/1.00), because a concept graph doesn't need the facts
to be *textually similar* to the question - it just walks the edges. That's the whole point of this
repo, demonstrated with a real, runnable, measured system instead of a slide.
