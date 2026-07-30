import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

_ROLE_LABELS = {SystemMessage: "SYSTEM", HumanMessage: "USER", AIMessage: "NOVA"}


def render_context_inspector(messages, title: str = "See exactly what Nova reads for this reply"):
    """
    The single most important panel on each page: it shows the EXACT text
    sent to the model for the last turn. Compare this box across pages to
    see how each memory technique shrinks, compresses, or filters the
    conversation differently.
    """
    with st.expander(f"{title} ({len(messages)} messages)"):
        if not messages:
            st.caption("Nothing sent yet.")
            return
        for m in messages:
            label = _ROLE_LABELS.get(type(m), type(m).__name__)
            st.markdown(f"**{label}:** {m.content}")
