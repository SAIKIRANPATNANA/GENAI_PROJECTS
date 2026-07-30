import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.no_memory import NoMemoryStrategy

st.set_page_config(page_title="No Memory", page_icon="🚫", layout="wide")
st.title("🚫 Technique 1: No Memory (the baseline)")
st.markdown(
    """
**The idea:** Nova gets *only* your very last message. Nothing before it exists to her, like
talking to someone with amnesia after every single sentence.

Watch turn 2: we tell Nova our name on turn 1, then immediately ask for it back on turn 2.
Even one turn later, it's already gone - this technique fails the fastest of all eight.
"""
)

common.run_strategy_page(
    page_key="no_memory",
    make_strategy=lambda llm, embedder: NoMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT),
)

render_verdict(
    best="It's free and instant - there's no memory to store, manage, or pay for.",
    worst="It forgets everything the moment you say it, even one message later.",
    example="Tell it your name, then ask again on the very next message - it has no idea.",
)
