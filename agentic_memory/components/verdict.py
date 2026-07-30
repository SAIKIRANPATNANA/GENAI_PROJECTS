import streamlit as st


def render_verdict(best: str, worst: str, example: str):
    """A short, plain-language wrap-up shown at the bottom of every technique page."""
    st.divider()
    st.subheader("The verdict")
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**Best thing:** {best}")
    with col2:
        st.error(f"**Worst thing:** {worst}")
    st.caption(f"**Example:** {example}")
