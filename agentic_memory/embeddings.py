"""
Turns text into a "meaning fingerprint" - a list of numbers (a vector) that
captures what the text is about. Similar sentences end up with similar
fingerprints. This runs entirely on your own laptop: no API key, no cost,
no internet needed once the small model is downloaded the first time.
"""

import streamlit as st
from langchain_core.embeddings import Embeddings
from fastembed import TextEmbedding


class LocalFastEmbeddings(Embeddings):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.embed([text]))).tolist()


@st.cache_resource(show_spinner="Loading the local embedding model (only happens once)...")
def get_embedder() -> LocalFastEmbeddings:
    """
    st.cache_resource keeps ONE copy of this model loaded in memory for the
    whole running app, shared by every visitor. On Streamlit Community
    Cloud that means the ~100MB model downloads and loads only once per
    deployment, not once per student who opens the app - every session
    after the first one reuses the same cached object instantly.

    This is safe to share across everyone because the model itself holds
    no per-user data - it's a pure text-to-vector function. Contrast this
    with the Groq client in common.py, which is deliberately kept in
    st.session_state instead, because it's tied to one student's API key
    and conversation.
    """
    return LocalFastEmbeddings()
