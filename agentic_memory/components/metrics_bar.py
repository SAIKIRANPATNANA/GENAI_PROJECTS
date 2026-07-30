import streamlit as st


def render_metrics_bar(requests: int, input_tokens: int, output_tokens: int, cost: float):
    """Four big numbers, updated live after every turn, so the class can watch them move."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API requests made", requests)
    c2.metric("Tokens sent (in)", f"{input_tokens:,}")
    c3.metric("Tokens received (out)", f"{output_tokens:,}")
    c4.metric("Cost so far", f"${cost:.5f}")
