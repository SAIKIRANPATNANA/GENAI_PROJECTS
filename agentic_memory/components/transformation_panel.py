import streamlit as st


def render_transformation(raw_title: str, raw_items: list[str], artifact_title: str, artifact):
    """
    The single most important visual on every long-term memory page: raw
    conversation turns on the left, the structured thing an LLM call turned
    them into on the right. This is the moment "messages become memory" -
    everything else on the page is just proving the artifact on the right
    is what actually gets used later, not the transcript on the left.

    artifact: a dict (rendered as JSON) or a plain string.
    """
    st.subheader("How the conversion happened")
    col_raw, col_arrow, col_artifact = st.columns([5, 1, 5])

    with col_raw:
        st.markdown(f"**{raw_title}**")
        with st.container(border=True, height=260):
            for item in raw_items:
                st.caption(item)

    with col_arrow:
        st.markdown(
            "<div style='text-align:center; font-size:2rem; padding-top:6rem;'>&rarr;</div>",
            unsafe_allow_html=True,
        )

    with col_artifact:
        st.markdown(f"**{artifact_title}**")
        with st.container(border=True, height=260):
            if isinstance(artifact, dict):
                st.json(artifact)
            else:
                st.write(artifact)
