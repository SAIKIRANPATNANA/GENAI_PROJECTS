"""Metric-based comparison of Basic RAG, OKF Retrieval, and Hybrid RAG using openevals.

Runs the same fixed question set (tests/evaluation_questions.json) through all three
LangGraph pipelines and scores each answer with LLM-as-judge evaluators for helpfulness,
groundedness (is the answer supported by what was retrieved), retrieval relevance, and
correctness against a reference answer. The judge is our own Groq model (passed in via
openevals' `judge=` parameter), so no OpenAI key is required.

The question set is designed so the underlying facts are genuinely scattered across
separate source documents (see data/raw/) - low scores on the multi-hop questions reflect
a real retrieval-coverage gap in Basic RAG, not an artificially broken pipeline.
"""
from __future__ import annotations

import json
import statistics
import time

from groq import APIStatusError as GroqAPIStatusError
from groq import RateLimitError as GroqRateLimitError

from openevals.llm import create_llm_as_judge
from openevals.prompts import (
    CORRECTNESS_PROMPT,
    RAG_GROUNDEDNESS_PROMPT,
    RAG_HELPFULNESS_PROMPT,
    RAG_RETRIEVAL_RELEVANCE_PROMPT,
)

from src.config import ROOT_DIR
from src.graphs.basic_rag_graph import build_graph as build_basic_graph
from src.graphs.hybrid_rag_graph import build_graph as build_hybrid_graph
from src.graphs.okf_rag_graph import build_graph as build_okf_graph
from src.llm import get_judge_llm

QUESTIONS_PATH = ROOT_DIR / "tests" / "evaluation_questions.json"
RESULTS_PATH = ROOT_DIR / "tests" / "eval_results.json"

METRICS = ["helpfulness", "groundedness", "retrieval_relevance", "correctness"]


# Runs one question through the Basic RAG pipeline and returns the answer plus the
# retrieved text as a single string, so the judge evaluators below have something to check the answer against.
def _basic_run(app, question: str) -> dict:
    start = time.perf_counter()
    result = app.invoke({"question": question, "chunks": [], "answer": ""})
    latency = time.perf_counter() - start
    context = "\n\n".join(c["text"] for c in result["chunks"])
    return {"answer": result["answer"], "context": context, "latency": latency}


# Same idea as _basic_run, but the "context" is the matched concepts' text instead of chunks.
def _okf_run(app, question: str) -> dict:
    start = time.perf_counter()
    result = app.invoke(
        {"question": question, "matched_concepts": [], "path": [], "concepts_context": [], "answer": ""}
    )
    latency = time.perf_counter() - start
    context = "\n\n".join(f"{c['title']}: {c['description']}\n{c['body']}" for c in result["concepts_context"])
    return {"answer": result["answer"], "context": context, "latency": latency}


# Same idea again, but the "context" is both the raw chunks and the OKF concepts combined.
def _hybrid_run(app, question: str) -> dict:
    start = time.perf_counter()
    result = app.invoke(
        {
            "question": question,
            "chunks": [],
            "matched_concepts": [],
            "path": [],
            "concepts_context": [],
            "answer": "",
        }
    )
    latency = time.perf_counter() - start
    raw_context = "\n\n".join(c["text"] for c in result["chunks"])
    okf_context = "\n\n".join(f"{c['title']}: {c['description']}" for c in result["concepts_context"])
    return {"answer": result["answer"], "context": f"{raw_context}\n\n{okf_context}", "latency": latency}


# Maps a pipeline's name to the function that builds it and the function that runs
# one question through it. run_evaluation() below loops over this dict.
PIPELINES = {
    "basic_rag": (build_basic_graph, _basic_run),
    "okf": (build_okf_graph, _okf_run),
    "hybrid": (build_hybrid_graph, _hybrid_run),
}


def _safe_score(evaluator, retries: int = 4, **kwargs) -> float | None:
    """Groq's forced structured-output tool calling is occasionally flaky (the judge model
    sometimes emits a malformed tool call), and the judge key can hit its tokens-per-minute
    rate limit during a full run. Retry a few times - with a longer backoff specifically for
    rate limits - before giving up and recording the score as missing rather than crashing
    the whole evaluation run.
    """
    for attempt in range(retries):
        try:
            return evaluator(**kwargs)["score"]
        except GroqRateLimitError as exc:
            if attempt == retries - 1:
                print(f"  (judge call failed after {retries} attempts: {exc})")
                return None
            time.sleep(10)
        except GroqAPIStatusError as exc:
            if attempt == retries - 1:
                print(f"  (judge call failed after {retries} attempts: {exc})")
                return None
            time.sleep(1.5)
    return None


# Builds one LLM-as-judge scoring function per metric (see docs/09 for what each one checks).
def build_evaluators(judge) -> dict:
    return {
        "helpfulness": create_llm_as_judge(
            prompt=RAG_HELPFULNESS_PROMPT, feedback_key="helpfulness", judge=judge, continuous=True
        ),
        "groundedness": create_llm_as_judge(
            prompt=RAG_GROUNDEDNESS_PROMPT, feedback_key="groundedness", judge=judge, continuous=True
        ),
        "retrieval_relevance": create_llm_as_judge(
            prompt=RAG_RETRIEVAL_RELEVANCE_PROMPT, feedback_key="retrieval_relevance", judge=judge, continuous=True
        ),
        "correctness": create_llm_as_judge(
            prompt=CORRECTNESS_PROMPT, feedback_key="correctness", judge=judge, continuous=True
        ),
    }


def run_evaluation() -> list[dict]:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    judge = get_judge_llm()
    evaluators = build_evaluators(judge)

    rows: list[dict] = []
    for pipeline_name, (builder, runner) in PIPELINES.items():
        app = builder()
        for q in questions:
            run = runner(app, q["question"])
            scores = {
                "helpfulness": _safe_score(
                    evaluators["helpfulness"], inputs=q["question"], outputs=run["answer"]
                ),
                "groundedness": _safe_score(
                    evaluators["groundedness"], context=run["context"], outputs=run["answer"]
                ),
                "retrieval_relevance": _safe_score(
                    evaluators["retrieval_relevance"], inputs=q["question"], context=run["context"]
                ),
                "correctness": _safe_score(
                    evaluators["correctness"],
                    inputs=q["question"],
                    outputs=run["answer"],
                    reference_outputs=q.get("reference_answer", ""),
                ),
            }

            row = {
                "pipeline": pipeline_name,
                "question_id": q["id"],
                "type": q["type"],
                "question": q["question"],
                "answer": run["answer"],
                "latency_sec": round(run["latency"], 2),
                **scores,
            }
            rows.append(row)

            def _fmt(x: float | None) -> str:
                return f"{x:.2f}" if x is not None else "N/A"

            print(
                f"[{pipeline_name:9s}] {q['id']}  "
                f"help={_fmt(scores['helpfulness'])} ground={_fmt(scores['groundedness'])} "
                f"retr={_fmt(scores['retrieval_relevance'])} correct={_fmt(scores['correctness'])} "
                f"({row['latency_sec']}s)"
            )

    RESULTS_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nSaved detailed results to {RESULTS_PATH}")
    return rows


def _mean(values) -> str:
    clean = [v for v in values if v is not None]
    return f"{statistics.mean(clean):.2f}" if clean else "N/A"


# Prints two markdown tables: average score per pipeline across all questions, and
# again restricted to just the multi-hop questions (the headline comparison - see docs/10).
def summarize(rows: list[dict]) -> None:
    pipelines = sorted({r["pipeline"] for r in rows})

    print("\nOverall averages (all questions):")
    header = "| Metric | " + " | ".join(pipelines) + " |"
    print(header)
    print("|---" * (len(pipelines) + 1) + "|")
    for metric in [*METRICS, "latency_sec"]:
        cells = [_mean(r[metric] for r in rows if r["pipeline"] == p) for p in pipelines]
        print(f"| {metric} | " + " | ".join(cells) + " |")

    print("\nMulti-hop questions only (q2, q4 - the deliberately scattered facts):")
    hop_rows = [r for r in rows if r["type"] == "multi-hop"]
    print(header)
    print("|---" * (len(pipelines) + 1) + "|")
    for metric in METRICS:
        cells = [_mean(r[metric] for r in hop_rows if r["pipeline"] == p) for p in pipelines]
        print(f"| {metric} | " + " | ".join(cells) + " |")
