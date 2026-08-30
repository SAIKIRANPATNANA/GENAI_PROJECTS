"""Upload the fixed question set as a LangSmith Dataset, then run each pipeline as its own
LangSmith Experiment against it (openevals evaluators attached as LangSmith evaluators), so
Basic RAG / OKF Retrieval / Hybrid RAG show up side-by-side in the LangSmith Experiments
comparison view on the dashboard - not just as loose traces.

Usage: python run_langsmith_eval.py
Requires LANGSMITH_API_KEY (and LANGSMITH_TRACING=true) in .env, on top of the Groq/Jina keys.
"""
from __future__ import annotations

import json

from langsmith import Client
from langsmith.evaluation import evaluate

from src.config import ROOT_DIR
from src.evaluation import PIPELINES, _safe_score, build_evaluators
from src.llm import get_judge_llm

QUESTIONS_PATH = ROOT_DIR / "tests" / "evaluation_questions.json"
DATASET_NAME = "okf-rag-webinar-questions"


# Reuses the dataset on LangSmith if it's already there (from a previous run),
# otherwise uploads the questions as a brand new one.
def get_or_create_dataset(client: Client):
    if client.has_dataset(dataset_name=DATASET_NAME):
        return client.read_dataset(dataset_name=DATASET_NAME)

    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="OKF+RAG webinar: fixed question set comparing Basic RAG / OKF retrieval / Hybrid RAG.",
    )
    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"question": q["question"]},
                "outputs": {"reference_answer": q["reference_answer"]},
                "metadata": {"id": q["id"], "type": q["type"]},
            }
            for q in questions
        ],
    )
    return dataset


def make_target(builder, runner):
    """Build the pipeline once, return a LangSmith target function that runs it per example."""
    app = builder()

    def target(inputs: dict) -> dict:
        run = runner(app, inputs["question"])
        return {"answer": run["answer"], "context": run["context"], "latency_sec": round(run["latency"], 2)}

    return target


def make_ls_evaluators(evaluators: dict) -> list:
    """Adapt openevals' (inputs, outputs, reference_outputs, context) evaluators to
    LangSmith's (run, example) evaluator signature."""

    def helpfulness(run, example):
        score = _safe_score(
            evaluators["helpfulness"], inputs=example.inputs["question"], outputs=run.outputs["answer"]
        )
        return {"key": "helpfulness", "score": score}

    def groundedness(run, example):
        score = _safe_score(
            evaluators["groundedness"], context=run.outputs["context"], outputs=run.outputs["answer"]
        )
        return {"key": "groundedness", "score": score}

    def retrieval_relevance(run, example):
        score = _safe_score(
            evaluators["retrieval_relevance"], inputs=example.inputs["question"], context=run.outputs["context"]
        )
        return {"key": "retrieval_relevance", "score": score}

    def correctness(run, example):
        reference = (example.outputs or {}).get("reference_answer", "")
        score = _safe_score(
            evaluators["correctness"],
            inputs=example.inputs["question"],
            outputs=run.outputs["answer"],
            reference_outputs=reference,
        )
        return {"key": "correctness", "score": score}

    return [helpfulness, groundedness, retrieval_relevance, correctness]


def run_langsmith_eval() -> None:
    client = Client()
    dataset = get_or_create_dataset(client)
    print(f"Dataset: {dataset.name} ({dataset.id})")

    judge = get_judge_llm()
    ls_evaluators = make_ls_evaluators(build_evaluators(judge))

    for pipeline_name, (builder, runner) in PIPELINES.items():
        target = make_target(builder, runner)
        print(f"\nRunning experiment: {pipeline_name}")
        results = evaluate(
            target,
            data=dataset.name,
            evaluators=ls_evaluators,
            experiment_prefix=pipeline_name,
            max_concurrency=1,
            metadata={"pipeline": pipeline_name},
        )
        print(f"  {results.experiment_name}")
        print(f"  {results.url}")


if __name__ == "__main__":
    run_langsmith_eval()
