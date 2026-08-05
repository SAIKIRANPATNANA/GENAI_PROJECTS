"""Streamlit App: MultiModal RAG Frontend Studio.

Architecture:
- ⚡ Frontend: Streamlit UI
- 🚀 Backend: FastAPI server (http://localhost:8000)

Workflow:
1. Start backend server first:
   uv run uvicorn doc_parser.api.app:app --port 8000 --reload
2. Start Streamlit frontend:
   uv run streamlit run app.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import httpx
import streamlit as st

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MultiModal RAG Studio (FastAPI + Streamlit)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODALITY_BADGES = {
    "text": "🟢 Text",
    "image": "🖼️ Image",
    "table": "📊 Table",
    "formula": "🧪 Formula",
    "algorithm": "⚡ Algorithm",
}

DEFAULT_SAMPLE_QUERIES = [
    "--- Select a sample query or type your own below ---",
    "What is the main contribution of the Transformer architecture?",
    "How does scaled dot-product attention work and what is the scaling factor?",
    "What are the BLEU scores achieved by the Transformer on WMT 2014 English-to-German?",
    "What is the mathematical equation for Positional Encoding using sine and cosine functions?",
    "Describe the encoder-decoder architecture diagram and its multi-head attention layers.",
    "What learning rate schedule, warmup steps, and Adam optimizer hyperparameters were used during training?",
    "Why are self-attention layers faster than recurrent layers for long sequences?",
]


# ── Helper Functions & Backend Connectivity ──────────────────────────────────

def check_backend_health(backend_url: str) -> dict | None:
    """Check if FastAPI backend server is online."""
    try:
        url = f"{backend_url.rstrip('/')}/health"
        res = httpx.get(url, timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


def apply_byok_keys():
    """Apply BYOK keys stored in session_state to process environment."""
    groq_key = st.session_state.get("byok_groq", "")
    if groq_key and str(groq_key).strip():
        os.environ["GROQ_API_KEY"] = str(groq_key).strip()

    qdrant_url = st.session_state.get("byok_qdrant_url", "http://localhost:6333")
    if qdrant_url:
        os.environ["QDRANT_URL"] = str(qdrant_url).strip()

    qdrant_col = st.session_state.get("byok_qdrant_col", "documents")
    if qdrant_col and str(qdrant_col).strip():
        os.environ["QDRANT_COLLECTION_NAME"] = str(qdrant_col).strip()


def execute_search_api(
    backend_url: str,
    query: str,
    top_k: int,
    top_n: int,
    filter_modality: str | None,
    rerank: bool,
) -> dict:
    apply_byok_keys()
    url = f"{backend_url.rstrip('/')}/search"
    payload = {
        "query": query,
        "top_k": top_k,
        "top_n": top_n,
        "filter_modality": filter_modality if filter_modality != "All" else None,
        "rerank": rerank,
    }
    res = httpx.post(url, json=payload, timeout=60.0)
    if res.status_code != 200:
        raise RuntimeError(f"Backend API error ({res.status_code}): {res.text}")
    return res.json()


def execute_generate_api(
    backend_url: str,
    query: str,
    system_prompt: str,
    max_tokens: int,
    top_k: int,
    top_n: int,
    filter_modality: str | None,
    rerank: bool,
) -> dict:
    apply_byok_keys()
    url = f"{backend_url.rstrip('/')}/generate"
    payload = {
        "query": query,
        "system_prompt": system_prompt,
        "max_tokens": max_tokens,
        "top_k": top_k,
        "top_n": top_n,
        "filter_modality": filter_modality if filter_modality != "All" else None,
        "rerank": rerank,
    }
    res = httpx.post(url, json=payload, timeout=120.0)
    if res.status_code != 200:
        raise RuntimeError(f"Backend API error ({res.status_code}): {res.text}")
    return res.json()


# ── UI Layout ─────────────────────────────────────────────────────────────────

st.title("⚡ MultiModal RAG Studio (Client-Server)")
st.caption("Streamlit Frontend $\\rightarrow$ FastAPI Backend $\\rightarrow$ Qdrant & Groq")

# ── Sidebar: Backend & Credentials Config ────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Server & Credentials")

    backend_url = st.text_input(
        "FastAPI Backend URL",
        value=os.environ.get("BACKEND_URL", "http://localhost:8000"),
        help="Target FastAPI server address",
    )

    st.session_state.byok_groq = st.text_input(
        "Groq API Key (Free)",
        value=os.environ.get("GROQ_API_KEY", ""),
        type="password",
        help="Get a free key instantly at https://console.groq.com",
    )

    st.session_state.byok_qdrant_url = st.text_input(
        "Qdrant Server URL",
        value=os.environ.get("QDRANT_URL", "http://localhost:6333"),
        help="Local URL (http://localhost:6333) or Qdrant Cloud URL",
    )

    st.session_state.byok_qdrant_col = st.text_input(
        "Qdrant Collection Name",
        value=os.environ.get("QDRANT_COLLECTION_NAME", "documents"),
        help="Default Qdrant collection name",
    )

    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        apply_byok_keys()
        st.toast("Settings updated!", icon="✅")

    # Backend Connection Status Check
    st.divider()
    health_data = check_backend_health(backend_url)
    backend_online = health_data is not None

    st.markdown("**System Health Status:**")
    st.markdown(f"- **FastAPI Backend**: {'🟢 Online (`' + backend_url + '`)' if backend_online else '🔴 Offline'}")
    if health_data:
        st.markdown(f"- **Qdrant Vector DB**: `{health_data.get('qdrant', 'unknown')}`")
        st.markdown(f"- **LLM / Embedding**: `{health_data.get('openai', 'unknown')}`")
        st.markdown(f"- **Re-Ranker**: `{health_data.get('reranker_backend', 'bge')}`")

# ── Top Warning if Backend is Offline ─────────────────────────────────────────
if not backend_online:
    st.error(
        "⚠️ **FastAPI Backend Server is Offline!**\n\n"
        "Please start the backend server in your terminal before using the app:\n\n"
        "```bash\n"
        "uv run uvicorn doc_parser.api.app:app --port 8000 --reload\n"
        "```"
    )

# ── Main Tabs Interface ───────────────────────────────────────────────────────
tab_search, tab_generate = st.tabs([
    "🔍 Hybrid Search",
    "🤖 RAG Answer Generation",
])

# ==============================================================================
# TAB 1: HYBRID SEARCH & RE-RANKING
# ==============================================================================
with tab_search:
    st.subheader("🔍 Hybrid Vector Retrieval & Re-Ranking")
    st.caption("Combines Dense Semantic Search + BM25 Sparse Feature Hashing with Reciprocal Rank Fusion (RRF)")

    # Sample Query Picker for Tab 1
    selected_sample_search = st.selectbox(
        "💡 Quick Sample Queries",
        DEFAULT_SAMPLE_QUERIES,
        key="sample_search_picker",
    )

    initial_search_val = (
        selected_sample_search
        if selected_sample_search != DEFAULT_SAMPLE_QUERIES[0]
        else ""
    )

    col_q1, col_q2 = st.columns([3, 1])
    with col_q1:
        search_query = st.text_input(
            "Search Query",
            value=initial_search_val,
            placeholder="e.g. What is the transformer attention mechanism?",
            key="search_query_input",
        )
    with col_q2:
        modality_filter = st.selectbox("Modality Filter", ["All", "text", "image", "table", "formula", "algorithm"])

    with st.expander("⚙️ Search Parameters", expanded=False):
        c_k, c_n, c_rerank = st.columns(3)
        with c_k:
            top_k = st.slider("Candidates (top_k)", min_value=5, max_value=50, value=20)
        with c_n:
            top_n = st.slider("Final Results (top_n)", min_value=1, max_value=15, value=5)
        with c_rerank:
            do_rerank = st.checkbox("Enable Re-Ranking", value=True)

    if st.button("🚀 Run Hybrid Search via FastAPI", type="primary", key="btn_search", disabled=not backend_online):
        if not search_query.strip():
            st.warning("Please enter or select a search query.")
        else:
            with st.spinner("Calling FastAPI `/search` endpoint..."):
                try:
                    res_data = execute_search_api(
                        backend_url=backend_url,
                        query=search_query,
                        top_k=top_k,
                        top_n=top_n,
                        filter_modality=modality_filter,
                        rerank=do_rerank,
                    )

                    candidates = res_data.get("results", [])
                    total_candidates = res_data.get("total_candidates", len(candidates))
                    latency_ms = res_data.get("latency_ms", 0.0)

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Retrieved Candidates", total_candidates)
                    m2.metric("Final Results", len(candidates))
                    m3.metric("Backend Latency", f"{latency_ms} ms")

                    st.divider()

                    if not candidates:
                        st.info("No matching chunks found in Qdrant collection.")
                    else:
                        for i, c in enumerate(candidates, 1):
                            modality = c.get("modality", "text")
                            badge = MODALITY_BADGES.get(modality, "📄 Text")
                            score = c.get("rerank_score")
                            score_str = f" | Score: {score:.4f}" if score is not None else ""
                            page = c.get("page", "?")
                            source_file = c.get("source_file", "unknown")

                            with st.expander(f"[{i}] {badge} — {source_file} (Page {page}){score_str}"):
                                st.markdown(f"**Source File:** `{source_file}` | **Page:** `{page}` | **Modality:** `{modality}`")

                                text_content = c.get("text", "")
                                caption_content = c.get("caption")

                                if caption_content:
                                    st.markdown("**LLM Caption / Summary:**")
                                    st.info(caption_content)

                                if text_content:
                                    st.markdown("**Chunk Content:**")
                                    st.code(text_content, language="markdown")

                                if c.get("bbox"):
                                    st.caption(f"Bounding Box: {c.get('bbox')}")
                except Exception as exc:
                    st.error(f"Search failed: {exc}")

# ==============================================================================
# TAB 2: RAG ANSWER GENERATION
# ==============================================================================
with tab_generate:
    st.subheader("🤖 End-to-End Multimodal RAG Generation")
    st.caption("Calls FastAPI `/generate` endpoint to retrieve grounding context and generate cited responses")

    # Sample Query Picker for Tab 2
    selected_sample_gen = st.selectbox(
        "💡 Quick Sample Questions",
        DEFAULT_SAMPLE_QUERIES,
        key="sample_gen_picker",
    )

    initial_gen_val = (
        selected_sample_gen
        if selected_sample_gen != DEFAULT_SAMPLE_QUERIES[0]
        else ""
    )

    rag_query = st.text_area(
        "User Question",
        value=initial_gen_val,
        placeholder="e.g. Summarize the key results and performance metrics reported in the paper.",
        height=80,
        key="rag_query_input",
    )

    with st.expander("⚙️ RAG Prompt & Parameters", expanded=False):
        sys_prompt = st.text_area(
            "System Prompt",
            value=(
                "You are a precise document assistant. Answer the question using ONLY the provided context. "
                "If the answer is not in the context, say 'I don't have enough information to answer this.' "
                "Cite page numbers when referring to facts."
            ),
            height=100,
        )
        col_m2, col_m3 = st.columns(2)
        with col_m2:
            max_tokens = st.slider("Max Output Tokens", 128, 4096, 1024, 128)
        with col_m3:
            gen_rerank = st.checkbox("Enable Re-Ranking for Context", value=True, key="gen_rerank_cb")

        g_k, g_n = st.columns(2)
        with g_k:
            g_top_k = st.number_input("Top K Candidates", value=20)
        with g_n:
            g_top_n = st.number_input("Top N Re-ranked Context", value=5)

    if st.button("✨ Generate RAG Response via FastAPI", type="primary", key="btn_generate", disabled=not backend_online):
        if not rag_query.strip():
            st.warning("Please enter or select a question.")
        else:
            with st.spinner("Calling FastAPI `/generate` endpoint..."):
                try:
                    res_data = execute_generate_api(
                        backend_url=backend_url,
                        query=rag_query,
                        system_prompt=sys_prompt,
                        max_tokens=max_tokens,
                        top_k=int(g_top_k),
                        top_n=int(g_top_n),
                        filter_modality=None,
                        rerank=gen_rerank,
                    )

                    answer = res_data.get("answer", "")
                    sources = res_data.get("sources", [])
                    total_latency = res_data.get("latency_ms", 0.0)

                    st.markdown("### 💬 Generated Answer")
                    st.markdown(answer)
                    st.caption(f"⚡ End-to-end Latency: {total_latency} ms")

                    st.divider()
                    st.markdown("### 📚 Grounding Context Sources")
                    for idx, src in enumerate(sources, 1):
                        modality = src.get("modality", "text")
                        badge = MODALITY_BADGES.get(modality, "📄 Text")
                        page = src.get("page", "?")
                        source_file = src.get("source_file", "doc")
                        with st.expander(f"[{idx}] {badge} — {source_file} (Page {page})"):
                            st.write(src.get("text") or src.get("caption") or "")

                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
