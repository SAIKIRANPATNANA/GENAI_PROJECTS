import streamlit as st
import pandas as pd


def render_growth_chart(history: list, columns=("input_tokens", "cost"), title: str = "How this grows, turn by turn"):
    """
    history: list of dicts like {"turn": 1, "input_tokens": 120, "cost": 0.00002, ...}
    The SHAPE of this line is the whole lesson: flat vs climbing vs stepped.
    """
    st.caption(title)
    if not history:
        st.info("No turns yet - click **Next turn** below to begin.")
        return
    df = pd.DataFrame(history).set_index("turn")
    st.line_chart(df[list(columns)])
