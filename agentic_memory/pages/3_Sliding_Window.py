import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.sliding_window import SlidingWindowStrategy

st.set_page_config(page_title="Sliding Window", page_icon="🪟", layout="wide")
st.title("🪟 Technique 3: Sliding Window Memory")
st.markdown(
    """
**The idea:** Only keep the last couple of exchanges, like a small whiteboard that only fits so
much. Cost stays nice and flat, but older facts silently fall off the edge.

Watch the **memory test** callouts as you click through: an immediate follow-up question
succeeds, but ask again just a few turns later and Nova has already forgotten - the fact
scrolled out of the window.
"""
)


def _controls(strategy):
    st.subheader("Window size")
    window_turns = st.slider(
        "How many turns back can Nova see?",
        min_value=1, max_value=10, value=strategy.window_turns,
        key="sliding_window_size_slider",
    )
    if window_turns != strategy.window_turns:
        strategy.set_window_turns(window_turns)
    plural = "s" if window_turns != 1 else ""
    st.caption(
        f"Right now Nova can only see the last **{window_turns}** exchange{plural}. "
        "**Try this:** after a memory test below fails, drag this slider up, then ask the "
        "same question again in the \"Ask Nova something extra\" box - no reset needed. "
        "That's the fix in action."
    )


strategy, last = common.run_strategy_page(
    page_key="sliding_window",
    make_strategy=lambda llm, embedder: SlidingWindowStrategy(scenario.NOVA_SYSTEM_PROMPT, window_turns=2),
    extra_controls=_controls,
)

st.divider()
st.subheader("What's fallen out of the window")
st.metric("Messages evicted so far", strategy.dropped_count())
st.caption("These messages still happened, but Nova can no longer see them - they're outside her window.")

render_verdict(
    best="Cheap and fast - the cost never grows, no matter how long the chat runs.",
    worst="Anything older than the window is gone completely, even if it still matters.",
    example="Mention your allergy on turn 1, and by turn 10 it's already forgotten.",
)
