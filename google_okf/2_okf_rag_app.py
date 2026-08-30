"""Streamlit demo: OKF concept-graph retrieval over the curriculum's OKF bundle."""
import streamlit as st

from src.config import OKF_DIR, PROCESSED_DIR
from src.graphs.okf_rag_graph import build_graph
from src.okf_graph import OkfGraph

st.set_page_config(page_title="OKF Retrieval", page_icon="🕸️")
st.title("🕸️ OKF Retrieval")
st.caption(
    "Concept matching + prerequisite-graph traversal over the curriculum's OKF bundle, answered by Groq via LangGraph."
)


# Cached per hops value - see the comment in 1_basic_rag_app.py for why this matters.
@st.cache_resource(show_spinner="Loading OKF bundle and model...")
def get_app(hops: int):
    return build_graph(max_hops=hops)


question = st.text_input(
    "Ask a curriculum question", placeholder="What should I study before Computer Vision?"
)
max_hops = st.slider("Traversal hops", min_value=1, max_value=4, value=3)

if st.button("Run", type="primary") and question:
    try:
        app = get_app(max_hops)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    with st.spinner("Matching concept, traversing the graph, and generating..."):
        result = app.invoke(
            {"question": question, "matched_concepts": [], "path": [], "concepts_context": [], "answer": ""}
        )

    titles = {c["id"]: c["title"] for c in result["concepts_context"]}

    st.subheader("Matched concept(s)")
    st.write(", ".join(titles.get(cid, cid) for cid in result["matched_concepts"]) or "none found")

    st.subheader("Traversed path")
    st.write(" → ".join(titles.get(cid, cid) for cid in result["path"]) if result["path"] else "No path found.")

    st.subheader("Concept evidence")
    if not result["concepts_context"]:
        st.write("No matching concepts in the OKF bundle for this question.")
    for concept in result["concepts_context"]:
        with st.expander(concept["title"]):
            st.write(concept["description"])
            if concept.get("source"):
                st.caption(f"Source: {concept['source']}")

    st.subheader("Answer")
    st.write(result["answer"])

st.divider()
if st.checkbox("Show full concept graph"):
    okf_graph = OkfGraph.from_bundle(OKF_DIR)
    html_path = okf_graph.render_html(PROCESSED_DIR / "okf_graph.html")
    st.components.v1.html(html_path.read_text(encoding="utf-8"), height=620, scrolling=True)
