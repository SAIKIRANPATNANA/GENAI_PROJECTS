import numpy as np
import pandas as pd
import streamlit as st

import common
import scenario
from components.verdict import render_verdict
from embeddings import get_embedder
from memory_strategies.vector_store import VectorStoreMemoryStrategy

st.set_page_config(page_title="Vector Store Memory", page_icon="🔍", layout="wide")
st.title("🔍 Technique 7: Vector Store Memory")
st.markdown(
    """
**The idea:** Nova files away every message as a "meaning fingerprint" (an embedding), stored
in a searchable vector database (FAISS, running locally on this computer - free, no API key
needed).

When you ask something, instead of rereading the whole conversation, she acts like a librarian:
she searches for just the **3 most relevant** memories and only looks at those. Cost barely
grows even after hundreds of turns.
"""
)

# ---------------------------------------------------------------------------
# NUTSHELL DEMO: storage + retrieval, stripped down to the bare mechanism,
# with no LLM involved at all - just embeddings and a similarity score.
# This is what VectorStoreMemoryStrategy below is doing under the hood,
# every single turn.
# ---------------------------------------------------------------------------
st.header("🔬 Nutshell demo: how storage and retrieval actually work")
st.markdown(
    "Forget Nova for a second. Here are 6 unrelated sentences, already turned into vectors "
    "and \"stored\". Type a question and watch which ones get pulled out - purely based on "
    "**meaning**, not matching words."
)

NUTSHELL_SENTENCES = [
    "Whiskers is Maya's fluffy pet cat.",
    "Maya's favorite dessert is mango ice cream.",
    "The Eiffel Tower is located in Paris, France.",
    "Maya dreams of visiting Japan one day.",
    "Cheetahs are the fastest land animals.",
    "Python is a popular first programming language for beginners.",
]


@st.cache_resource(show_spinner=False)
def _nutshell_vectors():
    embedder = get_embedder()
    return np.array(embedder.embed_documents(NUTSHELL_SENTENCES))


def _cosine_similarity(query_vector, stored_vectors):
    query_norm = query_vector / np.linalg.norm(query_vector)
    stored_norms = stored_vectors / np.linalg.norm(stored_vectors, axis=1, keepdims=True)
    return stored_norms @ query_norm


with st.expander("See the 6 stored sentences"):
    for sentence in NUTSHELL_SENTENCES:
        st.write("-", sentence)

query = st.text_input("Try a question", value="What pet does Maya have?", key="vector_nutshell_query")
if query.strip():
    embedder = get_embedder()
    query_vector = np.array(embedder.embed_query(query))
    similarities = _cosine_similarity(query_vector, _nutshell_vectors())
    order = np.argsort(-similarities)

    df = pd.DataFrame({
        "Sentence": [NUTSHELL_SENTENCES[i] for i in order],
        "Similarity score": [round(float(similarities[i]), 3) for i in order],
        "Retrieved?": ["Yes - top 2" if rank < 2 else "" for rank in range(len(order))],
    })
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption(
        "Higher score = closer in meaning. The top 2 rows are what would actually get sent "
        "to the model as \"relevant memories\" - notice this has nothing to do with word "
        "overlap, only meaning. Try asking about France, or speed, or coding, to see the "
        "top match change."
    )

st.divider()

# ---------------------------------------------------------------------------
# THE REAL DEMO: the same mechanism, but running live against the scripted
# Nova conversation, with real memories accumulating turn by turn.
# ---------------------------------------------------------------------------
st.header("🧠 Now watch it work inside a real conversation")

strategy, last = common.run_strategy_page(
    page_key="vector_store",
    make_strategy=lambda llm, embedder: VectorStoreMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT, embedder, top_k=3),
)

st.divider()
st.subheader("What's stored in the memory library")
st.metric("Memories stored", strategy.stored_count())

vectors, texts = strategy.all_vectors_and_texts()
if len(vectors) >= 2:
    st.caption("Each dot below is one stored memory, laid out so similar memories sit close together.")
    centered = vectors - vectors.mean(axis=0)
    U, S, _ = np.linalg.svd(centered, full_matrices=False)
    coords = U[:, :2] * S[:2]
    df = pd.DataFrame(coords, columns=["x", "y"])
    df["memory"] = texts
    st.scatter_chart(df, x="x", y="y")
    with st.expander("See the raw memory text"):
        for t in texts:
            st.write("- " + t)
else:
    st.caption("Play a few turns above to see stored memories show up here.")

render_verdict(
    best="Finds the right memory no matter how long ago it was said - no distance limit at all.",
    worst="Only retrieves what SOUNDS relevant, so it can miss context that matters but is worded differently.",
    example="Ask 'what's my pet's name' 200 messages later and it still finds it instantly.",
)
