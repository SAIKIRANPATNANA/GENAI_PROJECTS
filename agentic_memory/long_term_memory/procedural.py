"""
Procedural Memory: don't store facts about the user, store RULES for how
the agent should behave - and inject them as directives, not context.

The mental model from the notebook: a skill manual the agent writes for
itself. "Always keep answers short for this user" is not something Nova
knows ABOUT the user - it's an instruction for Nova's OWN behaviour.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from long_term_memory.json_utils import parse_json_response

EXTRACTION_SYSTEM_PROMPT = (
    "You read a chat transcript and look for RULES the user stated about HOW the assistant "
    "should behave going forward - instructions about behaviour, not facts about the user. "
    "Examples: 'keep answers short', 'always give an example', 'never use jargon'. "
    "Return ONLY valid JSON: "
    '{"rules": [{"rule": "a short imperative instruction, e.g. \'Keep replies to 1-2 sentences\'", '
    '"confidence": 0.0}]}\n'
    'If no such rule was stated, return {"rules": []}.'
)


def extract(llm, session1_transcript: list[tuple[str, str]]) -> dict:
    transcript_text = "\n".join(f"{role}: {text}" for role, text in session1_transcript)
    messages = [
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessage(content=f"SESSION TRANSCRIPT:\n{transcript_text}"),
    ]
    response = llm.invoke(messages)
    result = parse_json_response(response.content)
    result.setdefault("rules", [])
    return result


def artifact_panel(artifact: dict):
    return "Extracted operating rules (JSON)", artifact


def build_session2_system_prompt(base_prompt: str, artifact: dict, min_confidence: float = 0.4) -> str:
    """
    Rules are injected as DIRECTIVES, not as background information - a
    deliberately different framing from Episodic/Semantic Memory's "here's
    what you know" phrasing. Same mechanism (system prompt text), different
    instruction the model is meant to take from it.

    The phrasing here is deliberately forceful ("override your normal
    style", "a failure if broken"). Soft phrasing like "try to keep things
    short" is easy for a fast, small model to quietly ignore when it also
    wants to be "helpful" - a stronger, consequence-framed instruction
    measurably improves compliance.
    """
    rules = artifact.get("rules", [])
    active = [r for r in rules if isinstance(r, dict) and r.get("confidence", 0) >= min_confidence]
    if not active:
        return base_prompt
    lines = [
        base_prompt,
        "",
        "CRITICAL OPERATING RULES - these override your normal reply style. Follow them on "
        "EVERY reply below, with no exceptions, even if a longer answer would otherwise be more complete:",
    ]
    for r in active:
        lines.append(f"- {r.get('rule', '')}")
    lines.append("Breaking one of the rules above is a failure, regardless of how good the rest of the answer is.")
    return "\n".join(lines)


def rule_status(artifact: dict, min_confidence: float = 0.4) -> list[dict]:
    """
    For the page to show WHY a rule did or didn't make it into Session 2.
    A confidence score below the threshold is the most common SILENT
    failure point - the rule gets extracted correctly but never injected,
    and nothing on screen explains why unless we show this explicitly.
    """
    rules = artifact.get("rules", [])
    status = []
    for r in rules:
        if not isinstance(r, dict):
            continue
        confidence = r.get("confidence", 0)
        status.append({
            "rule": r.get("rule", ""),
            "confidence": confidence,
            "applied": confidence >= min_confidence,
        })
    return status
