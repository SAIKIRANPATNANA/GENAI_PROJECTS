import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.token_buffer import TokenBufferStrategy

st.set_page_config(page_title="Token Buffer", page_icon="⚖️", layout="wide")
st.title("⚖️ Technique 6: Token Buffer Memory")
st.markdown(
    """
**The idea:** Like a backpack with a strict *weight limit*, measured in tokens instead of
number of turns. Once it's full, the oldest messages get tossed out to make room. No
summarizing, no extra AI calls - this is the cheapest and most predictable technique here:
exactly 1 API call, every turn, always.
"""
)


def _controls(strategy):
    st.subheader("Token budget")
    max_tokens = st.slider(
        "How many tokens can Nova's buffer hold?",
        min_value=30, max_value=1000, value=strategy.memory.max_token_limit, step=10,
        key="token_buffer_limit_slider",
    )
    if max_tokens != strategy.memory.max_token_limit:
        strategy.set_max_token_limit(max_tokens)

    used = strategy.current_tokens()
    st.progress(min(1.0, used / max_tokens), text=f"{used} / {max_tokens} tokens currently in the buffer")
    st.caption(
        f"The moment this would go over **{max_tokens} tokens**, the oldest messages get dropped "
        "to make room - watch the bar fill up, then reset back down as old turns get evicted. "
        "Drag the slider to see exactly how many tokens back Nova can remember."
    )


strategy, last = common.run_strategy_page(
    page_key="token_buffer",
    make_strategy=lambda llm, embedder: TokenBufferStrategy(
        scenario.NOVA_SYSTEM_PROMPT, llm, max_token_limit=150
    ),
    extra_controls=_controls,
)

st.divider()
st.subheader("What's fallen out of the buffer")
st.metric("Messages evicted so far", strategy.dropped_count())
st.caption("These messages still happened, but Nova can no longer see them - they were the oldest ones over budget.")

render_verdict(
    best="Totally predictable - you always know the exact cost ceiling per turn.",
    worst="Still forgets older messages once the token budget fills up, just like a window.",
    example="Set a 150-token limit, and the oldest messages get dropped the moment you cross it.",
)
