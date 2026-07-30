"""
Episodic Memory: store a complete session as one timestamped, structured
"episode" - not the raw transcript, a compressed record of what happened.

The mental model from the notebook: a diary. Every session becomes one
diary entry with a date, a summary, and what was decided.
"""

from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from long_term_memory.json_utils import parse_json_response

EXTRACTION_SYSTEM_PROMPT = (
    "You summarise a chat session into a structured JSON \"episode\" record. "
    "Return ONLY valid JSON, no other text, with exactly these keys:\n"
    '{"topics": ["short topic labels mentioned in the session"], '
    '"decision": "any decision the user made, or null if none", '
    '"summary": "a 2-3 sentence summary of the whole session", '
    '"emotional_tone": "one short phrase describing the user\'s mood"}'
)


def extract(llm, session1_transcript: list[tuple[str, str]]) -> dict:
    """
    The moment "messages become memory". One LLM call reads the whole
    Session 1 transcript and compresses it into a small structured
    record - this is exactly what a real episodic memory system does the
    instant a session ends.
    """
    transcript_text = "\n".join(f"{role}: {text}" for role, text in session1_transcript)
    messages = [
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessage(content=f"SESSION TRANSCRIPT:\n{transcript_text}"),
    ]
    response = llm.invoke(messages)
    episode = parse_json_response(response.content)
    episode["session_id"] = "session_1"
    episode["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return episode


def artifact_panel(episode: dict):
    return "Episode record (this is what got stored)", episode


def build_session2_system_prompt(base_prompt: str, episode: dict) -> str:
    summary = episode.get("summary", "")
    topics = ", ".join(episode.get("topics") or [])
    decision = episode.get("decision")

    lines = [base_prompt, "", "You are recalling a past session with this user. Here is what happened:"]
    if summary:
        lines.append(f"- Summary: {summary}")
    if topics:
        lines.append(f"- Topics discussed: {topics}")
    if decision:
        lines.append(f"- Decision made: {decision}")
    return "\n".join(lines)
