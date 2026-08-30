"""Streamlit demo: Hybrid RAG - vector retrieval (+ rerank) fused with OKF concept-graph traversal."""
import streamlit as st

from src.graphs.hybrid_rag_graph import build_graph

st.set_page_config(page_title="Hybrid RAG", page_icon="🔀")
st.title("🔀 Hybrid RAG")
st.caption(
    "Runs FAISS+rerank vector retrieval and OKF concept-graph traversal in parallel, fuses both, then answers via Groq/LangGraph."
)


# Cached per (top_k, hops) combination - see the comment in 1_basic_rag_app.py for why this matters.
@st.cache_resource(show_spinner="Loading FAISS index, OKF bundle, and models...")
def get_app(k: int, hops: int):
    return build_graph(top_k=k, max_hops=hops)


question = st.text_input(
    "Ask a curriculum question", placeholder="Why is Deep Learning relevant to Computer Vision?"
)
col1, col2 = st.columns(2)
with col1:
    top_k = st.slider("Chunks to keep after reranking (top-k)", min_value=1, max_value=8, value=4)
with col2:
    max_hops = st.slider("Traversal hops", min_value=1, max_value=4, value=3)

if st.button("Run", type="primary") and question:
    try:
        app = get_app(top_k, max_hops)
    except (ValueError, FileNotFoundError) as exc:
        st.error(f"{exc}\n\nIf this is a missing index, run `python build_index.py` first.")
        st.stop()

    with st.spinner("Running vector + OKF retrieval in parallel and fusing context..."):
        result = app.invoke(
            {
                "question": question,
                "chunks": [],
                "matched_concepts": [],
                "path": [],
                "concepts_context": [],
                "answer": "",
            }
        )

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Vector evidence")
        if not result["chunks"]:
            st.write("Nothing retrieved.")
        for chunk in result["chunks"]:
            with st.expander(f"{chunk['source']}  ·  rerank {chunk['rerank_score']:.3f}"):
                st.write(chunk["text"])

    with col_b:
        st.subheader("OKF evidence")
        titles = {c["id"]: c["title"] for c in result["concepts_context"]}
        st.write("**Path:** " + (" → ".join(titles.get(cid, cid) for cid in result["path"]) or "none"))
        for concept in result["concepts_context"]:
            with st.expander(concept["title"]):
                st.write(concept["description"])
                if concept.get("source"):
                    st.caption(f"Source: {concept['source']}")

    st.subheader("Answer")
    st.write(result["answer"])
