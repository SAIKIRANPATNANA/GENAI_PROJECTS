import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.summary_buffer import SummaryBufferStrategy

st.set_page_config(page_title="Summary Buffer", page_icon="🎒", layout="wide")
st.title("🎒 Technique 5: Summary Buffer Memory")
st.markdown(
    """
**The idea:** A hybrid. Nova keeps your last couple of messages word-for-word (sharp, recent
detail), and only folds OLDER messages into a short recap once they overflow a small budget.

Extra "recap" calls only happen occasionally, not every turn like pure Summary Memory, but more
often than never, like Buffer Memory. Watch the requests counter to see the difference.
"""
)

strategy, last = common.run_strategy_page(
    page_key="summary_buffer",
    make_strategy=lambda llm, embedder: SummaryBufferStrategy(
        scenario.NOVA_SYSTEM_PROMPT, llm, max_token_limit=120
    ),
)

st.divider()
st.subheader("Recap of older messages")
st.info(strategy.summary_text())

render_verdict(
    best="Balances both worlds - sharp on recent details, still keeps the gist of the old stuff.",
    worst="More moving parts than either technique alone, so it's harder to predict and tune.",
    example="It nails what you said 2 turns ago, and roughly recalls what you said 20 turns ago.",
)
