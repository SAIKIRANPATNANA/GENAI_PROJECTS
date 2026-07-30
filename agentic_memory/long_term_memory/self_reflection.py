"""
Self-Reflection Memory: after a session, the agent critiques its OWN
performance - not facts about the user, not rules to follow, but "did I
mess up, and what should I learn from it."

The mental model from the notebook: a doctor's post-consultation debrief.
The critical safety rule from the notebook carries over directly: a
reflection with no quoted evidence from the transcript is a hallucinated
self-critique and must be discarded, not injected.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from long_term_memory.json_utils import parse_json_response

REFLECTION_SYSTEM_PROMPT = (
    "You are Nova, reviewing your OWN performance in the session transcript below. At some "
    "point the user asked you to keep answers short (a sentence or two). Check whether YOUR "
    "replies AFTER that request honoured it. Return ONLY valid JSON:\n"
    '{"violation_found": true or false, '
    '"evidence_quote": "the exact reply text that shows the issue, or null if none", '
    '"lesson": "a short instruction for next time, or null if nothing to fix"}\n'
    "If you cannot quote a specific one of your own replies as evidence, set violation_found to "
    "false. Do not invent a problem that is not clearly shown in the transcript."
)


def extract(llm, session1_transcript: list[tuple[str, str]]) -> dict:
    transcript_text = "\n".join(f"{role}: {text}" for role, text in session1_transcript)
    messages = [
        SystemMessage(content=REFLECTION_SYSTEM_PROMPT),
        HumanMessage(content=f"YOUR SESSION TRANSCRIPT:\n{transcript_text}"),
    ]
    response = llm.invoke(messages)
    reflection = parse_json_response(response.content)
    reflection.setdefault("violation_found", False)

    # The evidence rule, enforced in code, not just asked for in the prompt:
    # a violation claim with no quoted evidence does not survive.
    if reflection.get("violation_found") and not reflection.get("evidence_quote"):
        reflection["violation_found"] = False
        reflection["discarded_reason"] = "No quoted evidence was provided, so this reflection was discarded."

    return reflection


def artifact_panel(reflection: dict):
    return "Self-reflection note (JSON)", reflection


def build_session2_system_prompt(base_prompt: str, reflection: dict) -> str:
    if not reflection.get("violation_found"):
        return base_prompt
    lesson = reflection.get("lesson") or "Review your last session for missed instructions."
    lines = [base_prompt, "", "SELF-NOTE FROM LAST SESSION (learn from this):", f"- {lesson}"]
    if reflection.get("evidence_quote"):
        lines.append(f'  (Evidence: you previously replied "{reflection["evidence_quote"]}" - too long.)')
    return "\n".join(lines)
