import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from memory_strategies.summary import SummaryMemoryStrategy

st.set_page_config(page_title="Summary Memory", page_icon="📝", layout="wide")
st.title("📝 Technique 4: Summary Memory")
st.markdown(
    """
**The idea:** Instead of keeping the raw transcript, Nova keeps ONE running recap of everything
said so far, like a friend who takes notes in a meeting and gives you the highlights.

**The catch:** rewriting that recap takes a SECOND, hidden AI call, on *every single turn*.
Watch the "API requests made" number below - it will climb twice as fast as on the Buffer
Memory page.

Watch the very last memory test (turn 24, asking your name again from 23 turns back)
especially closely: by then the recap has been rewritten over 20 times. It usually survives,
but keep an eye on the "running recap" box below - each rewrite is a fresh chance for a small
detail to get compressed away or blurred.
"""
)

strategy, last = common.run_strategy_page(
    page_key="summary",
    make_strategy=lambda llm, embedder: SummaryMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT, llm),
)

st.divider()
st.subheader("Nova's running recap")
st.info(strategy.summary_text())

render_verdict(
    best="Can hold the gist of a very long conversation in just a few sentences.",
    worst="Costs 2 API calls every single turn, and details can blur after enough rewrites.",
    example="After 20 rewrites of the recap, a small detail like a middle name quietly disappears.",
)
