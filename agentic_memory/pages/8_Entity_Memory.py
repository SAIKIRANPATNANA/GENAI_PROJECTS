import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.entity import EntityMemoryStrategy

st.set_page_config(page_title="Entity Memory", page_icon="🪪", layout="wide")
st.title("🪪 Technique 8: Entity Memory")
st.markdown(
    """
**The idea:** Instead of remembering the whole conversation, Nova keeps a tiny profile card:
just a few labeled facts about the people and things you mention, like a contact card. She
automatically decides what counts as an "entity" worth tracking.

**Under the hood this is really two hidden jobs, not one:**
1. **Extraction** - "which names or things did the user just mention?" (e.g. `Maya`, `Whiskers`)
2. **Summarization** - for *each* name found, a separate call asks "given what I already know
   about this one, plus what was just said, what's the updated one-line summary?"

That means the number of hidden calls isn't fixed - it scales with how many things you mention
in a turn. Watch the "API requests made" number jump by different amounts turn to turn.
"""
)

strategy, last = common.run_strategy_page(
    page_key="entity",
    make_strategy=lambda llm, embedder: EntityMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT, llm),
)

st.divider()
st.subheader("Step 1: what did the extraction step notice just now?")
detected = strategy.last_detected_entities()
if detected:
    st.success("Detected this turn: " + ", ".join(f"`{name}`" for name in detected))
    st.caption(
        f"That's {len(detected)} entity{'y' if len(detected) == 1 else 'ies'} spotted -> "
        f"{len(detected)} separate summarization call{'s' if len(detected) != 1 else ''} will "
        "run during save(), one per name, to update each one's profile line."
    )
else:
    st.caption("Nothing new detected this turn - no summarization calls were needed.")

st.divider()
st.subheader("Step 2: the profile card built from those summarization calls")
entities = strategy.known_entities()
if entities:
    st.table({"Entity": list(entities.keys()), "What Nova knows": list(entities.values())})
    st.caption(
        "Each row here exists because the extraction step (above) noticed that name at some "
        "point, then a summarization call wrote (or rewrote) this line for it."
    )
else:
    st.caption("No entities identified yet - play a few turns first.")

render_verdict(
    best="Keeps a tiny, tidy profile of facts that never grows huge, no matter how long you chat.",
    worst="Only remembers things shaped like 'facts about a name' - it's bad at free-flowing stories.",
    example="It knows 'Whiskers = Maya's cat' forever, but can't tell you what you two joked about.",
)
