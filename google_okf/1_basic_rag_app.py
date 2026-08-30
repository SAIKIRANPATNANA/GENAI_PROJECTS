"""Streamlit demo: Basic RAG (vector search + Jina rerank) over raw curriculum documents."""
import streamlit as st

from src.graphs.basic_rag_graph import build_graph

st.set_page_config(page_title="Basic RAG", page_icon="📄")
st.title("📄 Basic RAG")
st.caption(
    "FAISS vector search over raw curriculum documents, reranked with Jina, answered by Groq via LangGraph."
)


# @st.cache_resource means this only actually runs once per distinct top_k value picked
# on the slider below - Streamlit reruns this whole script on every interaction, so without
# caching we'd reload the FAISS index and reconnect to the models on every click.
@st.cache_resource(show_spinner="Loading FAISS index and models...")
def get_app(k: int):
    return build_graph(top_k=k)


question = st.text_input(
    "Ask a curriculum question", placeholder="What is the path from Python to Computer Vision?"
)
top_k = st.slider("Chunks to keep after reranking (top-k)", min_value=1, max_value=8, value=4)

if st.button("Run", type="primary") and question:
    try:
        app = get_app(top_k)
    except (ValueError, FileNotFoundError) as exc:
        st.error(f"{exc}\n\nIf this is a missing index, run `python build_index.py` first.")
        st.stop()

    with st.spinner("Retrieving, reranking, and generating..."):
        result = app.invoke({"question": question, "chunks": [], "answer": ""})

    st.subheader("Retrieved chunks (after rerank)")
    if not result["chunks"]:
        st.write("Nothing retrieved.")
    for chunk in result["chunks"]:
        with st.expander(
            f"{chunk['source']}  ·  vector {chunk['vector_score']:.3f}  ·  rerank {chunk['rerank_score']:.3f}"
        ):
            st.write(chunk["text"])

    st.subheader("Answer")
    st.write(result["answer"])

    st.divider()
    st.caption(
        "Note: reranking only reorders whatever the vector search retrieved. On multi-hop questions "
        "(e.g. 'path from Python to Computer Vision'), the facts are scattered across separate "
        "documents that individually look dissimilar to the query — so they may never even enter the "
        "candidate pool, and no amount of reranking can recover a chunk that was never retrieved."
    )
