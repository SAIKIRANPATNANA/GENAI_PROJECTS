import streamlit as st

import common_ltm
import long_term_scenario as lts
from components.verdict import render_verdict
from long_term_memory import semantic

st.set_page_config(page_title="Semantic Memory", page_icon="🧭", layout="wide")
st.title("🧭 Long-Term Technique 2: Semantic Memory")
st.markdown(
    """
**The idea:** Instead of storing what happened in ONE session, distil the general pattern that
holds true ACROSS many sessions. Episodic memory is the diary; semantic memory is the
encyclopedia entry it eventually produces.

**This page makes an extra call, on top of Episodic Memory's one call:** first it summarises
today's Session 1 (same extraction as the Episodic page), then it reads that summary together
with 3 made-up past sessions and asks "what's generally true about this user?" Watch the "API
requests made" number - it starts one call higher than Episodic Memory's.
"""
)

st.info(
    "👤 **Human parallel:** think about how you get to know a close friend. After enough hangouts "
    "you just KNOW \"she's always the first to leave a party\" or \"he gets weirdly competitive "
    "about board games\" - but you couldn't tell me which specific evening taught you that. The "
    "individual episodes blurred away and only the general pattern survived. That's semantic "
    "memory: Nova is building the same kind of mental picture of you, distilled from many "
    "separate sessions, with the specific dates and conversations stripped off."
)

probes = [p for p in lts.SESSION_2_PROBES if p.turn in (0, 1, 3)]

artifact, results = common_ltm.run_long_term_demo_page(
    page_key="semantic",
    extract_fn=semantic.extract,
    artifact_panel_fn=semantic.artifact_panel,
    build_session2_system_prompt_fn=semantic.build_session2_system_prompt,
    probes=probes,
    raw_panel_fn=semantic.raw_panel,
)

render_verdict(
    best="The most compact long-term memory - a handful of general facts covers weeks of sessions.",
    worst="Needs several sessions before patterns are reliable - one weird session can skew it.",
    example="After 4 sessions of exam stress, it learns 'gets anxious under pressure' - true forever, not just today.",
)
