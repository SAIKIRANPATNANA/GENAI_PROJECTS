"""
Semantic Memory: distil GENERAL, reusable facts about the user from
several past episode summaries - not from any one session's raw messages.

The mental model from the notebook: a distillery. Episodic memory is the
raw ingredients (every session, in full). Semantic memory is the
concentrated essence - patterns that hold true across many sessions.

This is why the extraction step here reuses Episodic Memory's extractor:
semantic memory doesn't work on raw messages, it works on episode
summaries. Today's session becomes one more summary, joining three
made-up past sessions, and ONE extra LLM call asks "what's generally true
across ALL of these?"
"""

from langchain_core.messages import HumanMessage, SystemMessage

from long_term_memory import episodic
from long_term_memory.json_utils import parse_json_response

# Three made-up prior sessions, standing in for weeks of real history a
# student obviously can't play out live in class. This is exactly what a
# real semantic-memory pipeline would have accumulated by now.
CANNED_PAST_EPISODES = [
    "Session A (3 weeks ago): Maya asked about study techniques before an exam and seemed "
    "anxious about running out of time.",
    "Session B (2 weeks ago): Maya mentioned she double-checks everything before submitting it, "
    "calling herself a perfectionist.",
    "Session C (1 week ago): Maya asked Nova to keep explanations brief because long answers "
    "feel overwhelming when she's stressed.",
]

DISTILLATION_SYSTEM_PROMPT = (
    "You read several session summaries about the same user and extract GENERAL, reusable facts "
    "about them - patterns that hold across sessions, not one-off details from a single day. "
    "Return ONLY valid JSON with exactly this shape:\n"
    '{"facts": [{"fact": "a general statement about the user", '
    '"category": "behavioural | preference | academic", "confidence": 0.0}]}\n'
    "confidence should be higher when a pattern is confirmed by more than one session."
)


def extract(llm, session1_transcript: list[tuple[str, str]]) -> dict:
    today_episode = episodic.extract(llm, session1_transcript)
    today_summary = f"Session 1 (today): {today_episode.get('summary', '')}"
    all_summaries = CANNED_PAST_EPISODES + [today_summary]

    episodes_text = "\n".join(f"- {s}" for s in all_summaries)
    messages = [
        SystemMessage(content=DISTILLATION_SYSTEM_PROMPT),
        HumanMessage(content=f"PAST SESSION SUMMARIES:\n{episodes_text}"),
    ]
    response = llm.invoke(messages)
    result = parse_json_response(response.content)
    result.setdefault("facts", [])
    result["_source_summaries"] = all_summaries
    return result


def raw_panel(session1_transcript, result: dict):
    return "Inputs to distillation (3 past sessions + today)", result.get("_source_summaries", [])


def artifact_panel(result: dict):
    facts = result.get("facts", [])
    return "Distilled semantic facts (JSON)", {"facts": facts}


def build_session2_system_prompt(base_prompt: str, result: dict) -> str:
    facts = result.get("facts", [])
    relevant = [f for f in facts if isinstance(f, dict) and f.get("confidence", 0) >= 0.5]
    if not relevant:
        return base_prompt
    lines = [base_prompt, "", "General things you know about this user (patterns across sessions):"]
    for f in relevant:
        lines.append(f"- {f.get('fact', '')}")
    return "\n".join(lines)
