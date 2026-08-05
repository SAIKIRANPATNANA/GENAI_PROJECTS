"""Streamlit Web Application for MultiModal RAG Pipeline with BYOK (Bring Your Own Key)."""
from __future__ import annotations

import time
import httpx
import streamlit as st

# ── Page Configuration & Rich CSS Aesthetics ──────────────────────────────────
st.set_page_config(
    page_title="MultiModal RAG Workbench",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern Dark Glassmorphism Styling
st.markdown(
    """
    <style>
    /* Main App Styling */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Headers & Text */
    h1, h2, h3 {
        color: #f0f6fc !important;
        font-weight: 700;
    }
    .main-title {
        background: linear-gradient(135deg, #7928CA 0%, #FF0080 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #8b949e;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 12px;
        margin-right: 6px;
    }
    .badge-table { background-color: #1f6feb; color: #ffffff; }
    .badge-formula { background-color: #8957e5; color: #ffffff; }
    .badge-image { background-color: #da3633; color: #ffffff; }
    .badge-text { background-color: #238636; color: #ffffff; }

    /* Chunk Cards */
    .chunk-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .chunk-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        border-bottom: 1px solid #21262d;
        padding-bottom: 6px;
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar: BYOK (Bring Your Own Key) & System Settings ─────────────────────
st.sidebar.markdown("## 🔑 BYOK Credentials")
st.sidebar.caption("Enter your API keys below to connect directly.")

# Pre-populate keys from st.secrets or .env fallback if available
byok_groq_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    help="Get a free key at console.groq.com",
    key="groq_key",
)

byok_qdrant_url = st.sidebar.text_input(
    "Qdrant Cluster URL",
    value="https://491a2582-7d00-4644-9809-a3faab7fab8a.eu-west-2-0.aws.cloud.qdrant.io",
    help="Your Qdrant Cloud or Local URL (e.g. http://localhost:6333)",
    key="qdrant_url",
)

byok_qdrant_key = st.sidebar.text_input(
    "Qdrant API Key",
    type="password",
    help="API key for Qdrant Cloud cluster",
    key="qdrant_key",
)

byok_collection = st.sidebar.text_input(
    "Collection Name",
    value="multimodal_rag_v3_docs",
    key="qdrant_coll",
)

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Backend API Endpoint")
api_base_url = st.sidebar.text_input(
    "FastAPI Base URL",
    value="http://127.0.0.1:8000",
    help="Target FastAPI server endpoint",
)

st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by Baidu Unlimited-OCR & PP-Structure, Qdrant Hybrid RRF, BGE & Groq Llama-3.3-70b")

# ── Header Section ────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🧠 MultiModal RAG Workbench</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Extract, retrieve, and reason across Tables 📊, Formulas 🧮, Figures 🖼️, and Text 📝</div>',
    unsafe_allow_html=True,
)

# ── Pre-set Evaluation Queries ────────────────────────────────────────────────
PRESET_QUERIES = {
    "📊 Table: BLEU Scores (WMT 2014)": "What are the BLEU scores for Transformer (big) on the WMT 2014 English-to-German and English-to-French translation tasks?",
    "🧮 Formula: Scaled Dot-Product Attention": "What is the mathematical formula for Scaled Dot-Product Attention, including the scaling factor sqrt(d_k)?",
    "🖼️ Diagram: Model Architecture (Fig 1)": "Describe the visual architecture of the Transformer model from Figure 1, detailing the Encoder and Decoder sub-layers.",
    "🔀 Reasoning: Softmax Variance Scaling": "Why is Scaled Dot-Product Attention divided by sqrt(d_k) when d_k is large?",
    "⚙️ Params: Adam Optimizer & Warmup": "What hyperparameters were used for learning rate warmup steps and optimizer parameters?",
}

# ── Navigation Tabs ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🤖 RAG Generation", "🔍 Hybrid Search", "📊 Benchmark Ground Truths"])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1: RAG GENERATION
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🤖 Answer Generation (Full RAG)")
    
    col_preset, col_clear = st.columns([4, 1])
    with col_preset:
        selected_preset = st.selectbox(
            "⚡ Quick Preset Queries (Attention Is All You Need)",
            options=["-- Select a test query --"] + list(PRESET_QUERIES.keys()),
        )
    
    default_query = (
        PRESET_QUERIES[selected_preset]
        if selected_preset != "-- Select a test query --"
        else ""
    )
    
    user_query = st.text_area(
        "Enter your query:",
        value=default_query,
        placeholder="e.g. What are the BLEU scores for Transformer (big)?",
        height=90,
    )
    
    with st.expander("⚙️ Generation Parameters & System Prompt", expanded=False):
        sys_prompt = st.text_area(
            "System Prompt:",
            value="You are a scientific assistant. Answer the query only from the provided context otherwise reply answer is not found in given context",
            height=80,
        )
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            top_k_gen = st.slider("Retrieval Top-K", min_value=5, max_value=50, value=20, key="topk_gen")
        with col_p2:
            top_n_gen = st.slider("Rerank Top-N", min_value=1, max_value=10, value=3, key="topn_gen")
        with col_p3:
            max_tokens = st.number_input("Max Output Tokens", min_value=256, max_value=2048, value=1024)

    if st.button("🚀 Run RAG Generation", type="primary", use_container_width=True):
        if not user_query.strip():
            st.warning("Please enter a query or select a preset.")
        else:
            with st.spinner("Retrieving hybrid vectors, reranking, and generating with Groq..."):
                payload = {
                    "query": user_query,
                    "top_k": top_k_gen,
                    "top_n": top_n_gen,
                    "filter_modality": None,
                    "rerank": True,
                    "system_prompt": sys_prompt,
                    "max_tokens": max_tokens,
                }
                
                # Pass BYOK headers if provided
                headers = {"Content-Type": "application/json"}
                if byok_groq_key and byok_groq_key.strip():
                    headers["X-Groq-Api-Key"] = byok_groq_key.strip()
                if byok_qdrant_url and byok_qdrant_url.strip():
                    is_cloud = "qdrant.io" in byok_qdrant_url.lower() or "cloud" in byok_qdrant_url.lower()
                    if not is_cloud or (byok_qdrant_key and byok_qdrant_key.strip()):
                        headers["X-Qdrant-Url"] = byok_qdrant_url.strip()
                if byok_qdrant_key and byok_qdrant_key.strip():
                    headers["X-Qdrant-Api-Key"] = byok_qdrant_key.strip()

                try:
                    t0 = time.perf_counter()
                    resp = httpx.post(f"{api_base_url}/generate", json=payload, headers=headers, timeout=120.0)
                    elapsed_ms = (time.perf_counter() - t0) * 1000

                    if resp.status_code == 200:
                        data = resp.json()
                        st.markdown("### 💡 Answer")
                        st.info(data.get("answer", "No answer generated."))

                        # Metrics
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Latency", f"{data.get('latency_ms', elapsed_ms):.0f} ms")
                        m2.metric("Candidates Retrieved", data.get("total_candidates", 0))
                        m3.metric("Sources Used", len(data.get("sources", [])))

                        # Sources Breakdown
                        st.markdown("### 📚 Source Chunks Used in Context")
                        for idx, source in enumerate(data.get("sources", []), 1):
                            modality = source.get("modality", "text")
                            badge_cls = f"badge-{modality}" if modality in ["table", "formula", "image", "text"] else "badge-text"
                            score = source.get("rerank_score")
                            score_str = f" | Rerank Score: {score:.4f}" if score is not None else ""
                            
                            page_num = source.get("page") or source.get("page_number", "?")
                            with st.expander(f"Source #{idx} — Page {page_num} [{modality.upper()}]{score_str}"):
                                st.markdown(f'<span class="badge {badge_cls}">{modality.upper()}</span> Page {page_num}', unsafe_allow_html=True)
                                st.text(source.get("text", ""))
                                if source.get("caption"):
                                    st.caption(f"Caption: {source.get('caption')}")
                    else:
                        st.error(f"API Error ({resp.status_code}): {resp.text}")
                except Exception as exc:
                    st.error(f"Failed to connect to FastAPI server at {api_base_url}: {exc}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: HYBRID SEARCH
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 Hybrid Dense + Sparse Vector Search")
    
    search_query = st.text_input(
        "Search Query:",
        placeholder="e.g. WMT 2014 English-to-German BLEU score",
        key="search_input",
    )
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        search_top_k = st.slider("Retrieval Top-K", min_value=5, max_value=50, value=20, key="search_topk")
    with col_s2:
        search_top_n = st.slider("Rerank Top-N", min_value=1, max_value=10, value=5, key="search_topn")
    with col_s3:
        filter_modality = st.selectbox(
            "Filter Modality",
            options=["All", "table", "formula", "image", "text"],
        )

    enable_rerank = st.checkbox("Enable Re-ranking (BGE / Cross-Encoder)", value=True)

    if st.button("🔍 Perform Search", type="primary", use_container_width=True):
        if not search_query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner("Searching vectors in Qdrant..."):
                payload = {
                    "query": search_query,
                    "top_k": search_top_k,
                    "top_n": search_top_n,
                    "filter_modality": None if filter_modality == "All" else filter_modality,
                    "rerank": enable_rerank,
                }

                headers = {"Content-Type": "application/json"}
                if byok_qdrant_url and byok_qdrant_url.strip():
                    is_cloud = "qdrant.io" in byok_qdrant_url.lower() or "cloud" in byok_qdrant_url.lower()
                    if not is_cloud or (byok_qdrant_key and byok_qdrant_key.strip()):
                        headers["X-Qdrant-Url"] = byok_qdrant_url.strip()
                if byok_qdrant_key and byok_qdrant_key.strip():
                    headers["X-Qdrant-Api-Key"] = byok_qdrant_key.strip()

                try:
                    resp = httpx.post(f"{api_base_url}/search", json=payload, headers=headers, timeout=120.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        chunks = data.get("results", []) if isinstance(data, dict) else data
                        latency = data.get("latency_ms", 0) if isinstance(data, dict) else 0
                        st.success(f"Found {len(chunks)} matching chunks (Latency: {latency:.0f} ms)")
                        
                        for idx, chunk in enumerate(chunks, 1):
                            modality = chunk.get("modality", "text")
                            badge_cls = f"badge-{modality}" if modality in ["table", "formula", "image", "text"] else "badge-text"
                            score = chunk.get("rerank_score")
                            score_str = f"Score: {score:.4f}" if score is not None else ""

                            st.markdown(
                                f"""
                                <div class="chunk-card">
                                    <div class="chunk-header">
                                        <div>
                                            <span class="badge {badge_cls}">{modality.upper()}</span>
                                            <strong>Page {chunk.get('page') or chunk.get('page_number', '?')}</strong> — {chunk.get('source_file', '')}
                                        </div>
                                        <div style="color: #58a6ff; font-weight: 600;">{score_str}</div>
                                    </div>
                                    <div style="font-family: monospace; white-space: pre-wrap; font-size: 0.9rem;">{chunk.get('text', '')[:1000]}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.error(f"Search failed ({resp.status_code}): {resp.text}")
                except Exception as exc:
                    st.error(f"Could not connect to FastAPI server at {api_base_url}: {exc}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3: BENCHMARK GROUND TRUTHS
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📊 Benchmark Ground Truth Reference (Vaswani et al., 2017)")
    st.caption("Compare RAG generated answers against the exact published numbers from 'Attention Is All You Need'.")
    
    st.markdown(
        r"""
        | Category | Question | Published Ground Truth | Reference |
        |---|---|---|---|
        | 📊 **Table** | BLEU scores for Transformer (big)? | **English-to-German**: 28.4 BLEU \| **English-to-French**: 41.0 BLEU | Table 2 (Page 8) |
        | ⚙️ **Params** | Learning rate warmup & Adam params? | **Warmup**: 4,000 steps \| **Adam**: $\beta_1=0.9, \beta_2=0.98, \epsilon=10^{-9}$ | Sec 5.3 & 5.4 |
        | 🧮 **Formula** | Scaled Dot-Product Attention formula? | $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$ | Eq 1 (Page 4) |
        | 🧮 **Formula** | Positional Encoding formulas? | $PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$, $PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$ | Sec 3.5 (Page 6) |
        | 🖼️ **Diagram** | Transformer Encoder vs Decoder sub-layers? | **Encoder**: 2 sub-layers (Self-Attn + FFN) \| **Decoder**: 3 sub-layers (Masked Self-Attn + Cross-Attn + FFN) | Figure 1 (Page 3) |
        | 🔀 **Reasoning**| Why divide dot product by $\sqrt{d_k}$? | Prevents large dot products from pushing softmax into regions with vanishing gradients. | Footnote 4 (Page 4) |
        """
    )
