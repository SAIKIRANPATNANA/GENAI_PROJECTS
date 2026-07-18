"""
Guardrails binary evaluation.
Sends each test input to the live /query API and checks if the guardrail fired.
Classifies each result as TP / TN / FP / FN and computes precision + recall.
"""

import copy
import time

import logfire
import requests

API_URL = "http://localhost:8000/query"
MAX_RETRIES = 3
RATE_LIMIT_BACKOFF = 65  # seconds — clears the backend's 60s limiter window
DELAY_BETWEEN_TESTS = 5
REQUEST_TIMEOUT = 120


def _is_blocked(response_json: dict) -> bool:
    tp = response_json.get("thought_process") or []
    return any("guardrails fired" in step.lower() for step in tp)


def _post_guardrail_query(input_text: str, thread_id: str) -> requests.Response:
    """POST /query with retry on 429 so guardrail metrics are not skewed."""
    for attempt in range(1, MAX_RETRIES + 1):
        resp = requests.post(
            API_URL,
            json={"q": input_text, "thread_id": thread_id},
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code != 429:
            return resp

        if attempt == MAX_RETRIES:
            resp.raise_for_status()

        logfire.warning(
            "⏳ Guardrails eval hit API rate limit; backing off before retry.",
            attempt=attempt,
            thread_id=thread_id,
            backoff_seconds=RATE_LIMIT_BACKOFF,
        )
        time.sleep(RATE_LIMIT_BACKOFF)

    raise RuntimeError("Rate-limit retry loop exited unexpectedly")


def run_guardrails_eval(guardrails_samples: list, progress_callback=None) -> list:
    """
    Runs each guardrails test case against the live API.
    Adds actual_blocked and result (TP/TN/FP/FN/ERROR) to each sample in place.
    Returns the enriched list.
    """
    samples = copy.deepcopy(guardrails_samples)
    n = len(samples)

    with logfire.span("🛡️ Eval — Guardrails Tests", total=n):
        for i, sample in enumerate(samples):
            if progress_callback:
                progress_callback(i, n, sample["input"])

            with logfire.span(
                f"🛡️ Test {sample['id']}",
                input_text=sample["input"][:80],
                expected_blocked=sample["expected_blocked"],
            ):
                error_message = None
                try:
                    resp = _post_guardrail_query(sample["input"], thread_id=f"guardrail_eval_{i}")
                    resp.raise_for_status()
                    blocked = _is_blocked(resp.json())

                except requests.exceptions.ConnectionError:
                    error_message = "Cannot reach FastAPI — is the app running on :8000?"
                    logfire.error(f"❌ {error_message}")
                    blocked = False

                except Exception as e:
                    error_message = str(e)
                    logfire.error(f"❌ Guardrails test error: {e}")
                    blocked = False

                expected = sample["expected_blocked"]
                sample["actual_blocked"] = blocked
                sample["error"] = error_message

                if error_message:
                    sample["result"] = "ERROR"
                elif expected and blocked:
                    sample["result"] = "TP"
                elif expected and not blocked:
                    sample["result"] = "FN"
                elif not expected and not blocked:
                    sample["result"] = "TN"
                else:
                    sample["result"] = "FP"

                logfire.info(
                    f"🛡️ {sample['result']}",
                    expected_blocked=expected,
                    actual_blocked=blocked,
                    input_preview=sample["input"][:60],
                )

            time.sleep(DELAY_BETWEEN_TESTS)

    return samples


def compute_guardrails_metrics(results: list) -> dict:
    scored = [r for r in results if r["result"] != "ERROR"]
    tp = sum(1 for r in scored if r["result"] == "TP")
    tn = sum(1 for r in scored if r["result"] == "TN")
    fp = sum(1 for r in scored if r["result"] == "FP")
    fn = sum(1 for r in scored if r["result"] == "FN")
    errors = sum(1 for r in results if r["result"] == "ERROR")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    accuracy = (tp + tn) / len(scored) if scored else 0.0

    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "errors": errors,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "accuracy": round(accuracy, 3),
        "total": len(results),
        "scored_total": len(scored),
        "correct": tp + tn,
    }
