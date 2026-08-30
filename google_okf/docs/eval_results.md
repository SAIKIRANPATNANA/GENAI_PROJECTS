# OKF + RAG Eval Results (reference run)

Run date: 2026-08-24
Judge model: `openai/gpt-oss-20b` (Groq), continuous 0-1 scores via `openevals`
Generation model: `openai/gpt-oss-120b` (Groq)
Embeddings: `jina-embeddings-v3` (task-specific `retrieval.query` / `retrieval.passage`)
Reranker: `jina-reranker-v3.5` (Basic RAG and Hybrid RAG only)
Dataset: `tests/evaluation_questions.json` (7 fixed questions, also uploaded to LangSmith as `okf-rag-webinar-questions` with 3 experiments: `basic_rag`, `okf`, `hybrid`)

This is a snapshot from one run (`tests/eval_results.json`) kept for reference. Scores are LLM-judge estimates, not ground truth - treat the deltas as directional, not exact.

## Overall averages (all 7 questions)

| Metric | basic_rag | okf | hybrid |
|---|---|---|---|
| helpfulness | 0.78 | 0.79 | 0.94 |
| groundedness | 0.86 | 1.00 | 0.76 |
| retrieval_relevance | 0.89 | 0.76 | 0.95 |
| correctness | 0.75 | 0.82 | 0.99 |
| latency (sec) | 2.21 | 1.00 | 2.74 |

## Multi-hop questions only (q2, q4 - the deliberately scattered facts)

This is the headline comparison: q2 ("What is the path from Python to Computer Vision?") and q4 ("What should a student study before Computer Vision?") both require chaining facts that live in five separate documents (`python_prerequisites.md`, `statistics_prerequisites.md`, `machine_learning.md`, `deep_learning.md`, `computer_vision.md`).

| Metric | basic_rag | okf | hybrid |
|---|---|---|---|
| helpfulness | 0.95 | 0.90 | 0.90 |
| groundedness | 0.55 | 1.00 | 0.55 |
| retrieval_relevance | 0.90 | 1.00 | 0.90 |
| **correctness** | **0.15** | **1.00** | **1.00** |

**Reading this**: Basic RAG sounds confident (helpfulness 0.95 - it writes a fluent, well-cited answer) but is factually wrong (correctness 0.15) - it retrieved the two endpoints (`python_prerequisites.md`, `computer_vision.md`) and one adjacent doc, but never retrieved `statistics_prerequisites.md` or `machine_learning.md`, so it produced `Python -> Deep Learning -> Computer Vision`, silently skipping Statistics and Machine Learning. Reranking (Jina `jina-reranker-v3.5`, top 4 of 10 candidates) does not fix this - it can only reorder chunks that were retrieved, and the missing chunks never entered the candidate pool because they aren't lexically/semantically similar to a "path from X to Y" query. OKF traversal returns the exact 5-node chain every time (correctness 1.00, groundedness 1.00) because it isn't doing similarity search at all - it's walking explicit `requires` edges in the concept graph. Hybrid inherits OKF's correct path (correctness 1.00) while also attaching raw source passages, though its groundedness dips (0.55) because the raw evidence it attaches doesn't itself mention Statistics/Machine Learning even though the OKF path does - the judge penalizes claims in the answer that aren't backed by the *raw document* half of the context.

## Noise-question check (q7 - attendance policy, not in the OKF bundle)

`curriculum_rules.md` (administrative policy) is part of the raw corpus but was deliberately **not** curated into the OKF bundle, to test that OKF retrieval doesn't hallucinate coverage it doesn't have.

- **basic_rag**: answers correctly (75% attendance), all metrics 0.85-1.00.
- **hybrid**: answers correctly via its vector-retrieval half, all metrics 1.00.
- **okf**: correctly says the information isn't covered by the concept knowledge (helpfulness/retrieval_relevance/correctness all scored 0 by the judge since it declines to answer - groundedness scores 1.00 since "I don't know" is trivially grounded in empty context). This is expected/correct behavior, not a bug - OKF-only should not fabricate an answer from a concept graph that doesn't contain the fact.

## Per-question scores (all 21 runs)

| Pipeline | Question (type) | Help | Ground | Retr | Correct | Latency |
|---|---|---|---|---|---|---|
| basic_rag | q1 (direct) | 0.30 | 1.00 | 1.00 | 1.00 | 1.91s |
| basic_rag | q2 (multi-hop) | 0.95 | 0.50 | 0.80 | 0.20 | 2.32s |
| basic_rag | q3 (relationship) | 0.60 | 0.95 | 0.60 | 0.95 | 2.74s |
| basic_rag | q4 (multi-hop) | 0.95 | 0.60 | 1.00 | 0.10 | 2.23s |
| basic_rag | q5 (synthesis) | 0.90 | 1.00 | 0.90 | 1.00 | 2.03s |
| basic_rag | q6 (relationship) | 0.90 | 1.00 | 0.95 | 1.00 | 2.13s |
| basic_rag | q7 (direct-noise) | 0.85 | 1.00 | 1.00 | 1.00 | 2.09s |
| okf | q1 (direct) | 0.90 | 1.00 | 0.95 | 0.75 | 1.17s |
| okf | q2 (multi-hop) | 0.95 | 1.00 | 1.00 | 1.00 | 1.12s |
| okf | q3 (relationship) | 0.95 | 1.00 | 0.80 | 1.00 | 1.04s |
| okf | q4 (multi-hop) | 0.85 | 1.00 | 1.00 | 1.00 | 1.09s |
| okf | q5 (synthesis) | 0.95 | 1.00 | 0.60 | 1.00 | 0.96s |
| okf | q6 (relationship) | 0.90 | 1.00 | 0.95 | 1.00 | 0.94s |
| okf | q7 (direct-noise) | 0.00 | 1.00 | 0.00 | 0.00 | 0.71s |
| hybrid | q1 (direct) | 0.95 | 0.85 | 0.95 | 1.00 | 2.74s |
| hybrid | q2 (multi-hop) | 0.95 | 0.40 | 0.80 | 1.00 | 2.56s |
| hybrid | q3 (relationship) | 0.90 | 0.75 | 0.90 | 1.00 | 3.40s |
| hybrid | q4 (multi-hop) | 0.85 | 0.70 | 1.00 | 1.00 | 3.21s |
| hybrid | q5 (synthesis) | 0.95 | 0.80 | 1.00 | 1.00 | 2.75s |
| hybrid | q6 (relationship) | 0.95 | 0.85 | 1.00 | 0.95 | 2.61s |
| hybrid | q7 (direct-noise) | 1.00 | 1.00 | 1.00 | 1.00 | 1.94s |

Full answer text for every row is in `tests/eval_results.json`.

## Question set

| id | question | type |
|---|---|---|
| q1 | What are the prerequisites for Machine Learning? | direct |
| q2 | What is the path from Python to Computer Vision? | multi-hop |
| q3 | What concepts connect Machine Learning and Computer Vision? | relationship |
| q4 | What should a student study before Computer Vision? | multi-hop |
| q5 | Why is Deep Learning relevant to Computer Vision? | synthesis |
| q6 | How is Data Science related to Machine Learning? | relationship |
| q7 | What is the minimum attendance required to sit final examinations? | direct-noise |

## Notes on the judge

- `openai/gpt-oss-120b` (the generation model) was unreliable as a judge - Groq occasionally rejected its forced structured-output tool call ("Tool choice is required, but model did not call a tool" / malformed tool arguments). `openai/gpt-oss-20b` was reliably well-behaved instead, so it's used as a dedicated judge model (`src/llm.py::get_judge_llm`), on its own API key (`JUDGE_GROQ_API_KEY`) to avoid sharing the generation key's tokens-per-minute limit.
- `src/evaluation.py::_safe_score` retries a judge call up to 4 times (longer backoff specifically on rate limits) before recording a score as missing, rather than crashing the whole run.

## Reproducing

```bash
python build_index.py          # build the FAISS index (Jina embeddings)
python run_evaluation.py       # local run -> tests/eval_results.json + console summary
python run_langsmith_eval.py   # same comparison as 3 LangSmith Experiments on 1 Dataset
```
