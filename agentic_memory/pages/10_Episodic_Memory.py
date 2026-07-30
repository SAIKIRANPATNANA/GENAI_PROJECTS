import streamlit as st

import common_ltm
import long_term_scenario as lts
from components.verdict import render_verdict
from long_term_memory import episodic

st.set_page_config(page_title="Episodic Memory", page_icon="📔", layout="wide")
st.title("📔 Long-Term Technique 1: Episodic Memory")
st.markdown(
    """
**The idea:** At the end of a session, compress the whole thing into one timestamped "episode" -
like a diary entry. Next time, Nova doesn't replay the conversation, she reads the diary entry.

Play through **Session 1** below (a normal chat). Click **Close Session 1 & Extract** and watch
the raw transcript turn into a small JSON record. Then start **Session 2** - a brand new
conversation with zero raw history - and see if Nova can still answer using only that record.
"""
)

st.info(
    "👤 **Human parallel:** you don't remember your life as a flat list of random facts - you "
    "remember it as *episodes*. \"The trip where the flight got delayed and we ended up talking "
    "all night at the airport\" is one memory with a beginning, middle, and end - not fifty "
    "separate facts. Months later, you don't replay the whole night in your head, you just recall "
    "the episode's gist. That's exactly what's about to happen below: Session 1 becomes one "
    "diary-entry-shaped memory, and that's all Session 2 gets to work with."
)

probes = [p for p in lts.SESSION_2_PROBES if p.turn in (0, 1, 3)]  # skip the procedural-rule probe here

artifact, results = common_ltm.run_long_term_demo_page(
    page_key="episodic",
    extract_fn=episodic.extract,
    artifact_panel_fn=episodic.artifact_panel,
    build_session2_system_prompt_fn=episodic.build_session2_system_prompt,
    probes=probes,
)

render_verdict(
    best="Captures a whole session as one coherent story - great for 'what happened last time' questions.",
    worst="Only generated once, at session end - and a bad summary loses details for good.",
    example="Ask 'what did we decide last time?' months later and it answers from one diary entry, not 50 messages.",
)
