import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.buffer import BufferMemoryStrategy

st.set_page_config(page_title="Buffer Memory", page_icon="📚", layout="wide")
st.title("📚 Technique 2: Conversational Buffer Memory")
st.markdown(
    """
**The idea:** Keep *everything*, word for word, and resend the whole transcript every turn.

Nova will never forget a thing, but watch the **cost meter** below. Every turn, she has to
re-read the entire conversation from scratch, so the tokens (and the bill) keep climbing.
"""
)

common.run_strategy_page(
    page_key="buffer",
    make_strategy=lambda llm, embedder: BufferMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT),
)

render_verdict(
    best="Never forgets anything - perfect recall, every single time.",
    worst="Gets slower and more expensive the longer the conversation runs.",
    example="A 500-message chat means resending all 500 messages, on every single turn.",
)
