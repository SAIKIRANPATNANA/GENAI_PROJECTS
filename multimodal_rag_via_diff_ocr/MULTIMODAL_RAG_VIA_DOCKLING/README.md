<div align="center">

# 🧠 MultiModal RAG Pipeline (v2)

### High-Fidelity PDF Parsing (Docling) → Hybrid Vector Retrieval (BGE + SPLADE via Qdrant) → RAG Generation (Groq Llama-3.3-70b)

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Docling](https://img.shields.io/badge/Parser-Docling_IBM-FF6F61?style=flat-square)](https://github.com/DS4SD/docling)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud_%2F_Local-DC244C?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Groq](https://img.shields.io/badge/LLM-Groq_Llama--3.3--70b-f55036?style=flat-square)](https://groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat-square)](https://github.com/astral-sh/uv)

</div>

> [!NOTE]
> **Parsing Architecture (End-to-End Multimodal Parsing vs Legacy Pipelined OCR)**:
> Unlike `multi-modal-rag-master` which relied on a multi-step **Pipelined OCR approach** (chaining PP-DocLayout box detection, PyMuPDF cropping, and GLM-OCR), **v2** upgrades to **IBM Docling** for **End-to-End Multimodal Parsing**. Docling parses PDF layouts, tables, and math expressions in a single unified pass. Document parsing and embedding are offloaded to **Google Colab (`notebooks/02_colab_ingestion.ipynb`)** to prevent local memory/OOM limits while indexing directly into Qdrant Cloud.

---

## 🌟 Overview & Architecture

**MultiModal RAG Pipeline (v2)** is a lightweight, portable, and production-grade Retrieval-Augmented Generation framework built specifically for complex, highly structured documents (e.g., AI research papers, technical reports, financial statements).

Unlike standard text-only RAG pipelines, this system extracts, embeds, and reasons across **tables, mathematical formulas, structural figures, and textual content**.

```
📄 Complex Document (PDF)
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1 · Parsing (Docling / Google Colab)                  │
│  - High-fidelity PDF structure extraction                   │
│  - Multi-modal chunking (Tables, Formulas, Figures, Text)   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2 · Dense + Sparse Hybrid Embedding                   │
│  - Dense: BAAI/bge-small-en-v1.5 (384-dim semantic)         │
│  - Sparse: SPLADE / Feature-hashed BM25 (Keyword exact)     │
│  - Vector Database: Qdrant (Cloud / Local)                  │
│  - Fusion Strategy: Reciprocal Rank Fusion (RRF)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3 · FastAPI Server & Groq Generation                 │
│  - Reranking: BGE Cross-Encoder / OpenAI                    │
│  - Generation: Groq Llama-3.3-70b-versatile                 │
│  - Endpoints: POST /search, POST /generate                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment

Ensure Python 3.12+ and `uv` package manager are installed:

```bash
# Clone repository
cd multimodal_rag_v2

# Create & activate virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies in editable mode
uv pip install -e .
```

### 2. Environment Configuration (`.env`)

Create a `.env` file in the root directory:

```ini
# Qdrant Vector Database
QDRANT_COLLECTION_NAME=multimodal_rag_docs
QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Document Parser Backend
PARSER_BACKEND=docling

# Local Embedding Configuration
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=384

# Groq API for LLM Generation (Get free key at console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_TEXT_MODEL=llama-3.3-70b-versatile

# Reranker Backend
RERANKER_BACKEND=bge
```

---

## 📓 Google Colab Ingestion Workflow

To ingest heavy PDF documents without exhausting local memory or requiring high-end GPUs:

1. Open **`notebooks/02_colab_ingestion.ipynb`** in **Google Colab**.
2. Add your `GROQ_API_KEY`, `QDRANT_URL`, and `QDRANT_API_KEY` into Colab Secrets (or set them in the environment block).
3. Run all cells to:
   - Parse PDFs using **Docling**.
   - Embed chunks with **BGE-small** (dense) and **SPLADE** (sparse).
   - Push populated collections directly into **Qdrant Cloud** (`multimodal_rag_docs`).
   - Run the automated 15-query multimodal test suite.

---

## ⚡ FastAPI Server Usage

Launch the local REST API server:

```bash
uvicorn doc_parser.api.app:app --reload --port 8000
```

Interactive API documentation will be available at: **`http://localhost:8000/docs`**

### REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck for Qdrant and LLM connections |
| `POST` | `/ingest` | Server-side PDF ingestion into Qdrant |
| `POST` | `/search` | Hybrid search (Dense + Sparse RRF) |
| `POST` | `/generate` | Full RAG pipeline (Retrieval + Rerank + Groq Generation) |

---

## 🎨 Streamlit Web Application (`app.py`)

Launch the interactive dark-mode web workbench featuring **Bring Your Own Key (BYOK)**:

```bash
uv run streamlit run app.py
```

### Features:
* **🔑 BYOK Credentials**: Enter your `Groq API Key`, `Qdrant URL`, and `Qdrant API Key` directly in the sidebar UI without touching system config.
* **🤖 1-Click RAG Generation**: Test preset benchmark queries from *"Attention Is All You Need"* with customizable system prompts and model sliders.
* **🔍 Hybrid Search & Filters**: Search dense + sparse vector space with modality filters (`table`, `formula`, `image`, `text`).
* **📊 Benchmark Reference**: Built-in ground-truth matrix for easy verification.

---

## 🧪 Multimodal Evaluation Test Suite

To verify performance across different document element modalities (specifically tested on *"Attention Is All You Need"*):

### Sample `curl` Request

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the BLEU scores for Transformer (big) on the WMT 2014 English-to-German and English-to-French translation tasks?",
    "top_k": 20,
    "top_n": 3,
    "filter_modality": null,
    "rerank": true,
    "system_prompt": "You are a scientific assistant. Answer the query only from the provided context otherwise reply answer is not found in given context",
    "max_tokens": 1024
  }'
```

### Multimodal Test Queries & Expected Ground Truth

#### 📊 1. Table & Quantitative Queries
* **Query**: `"What are the BLEU scores for Transformer (big) on the WMT 2014 English-to-German and English-to-French translation tasks?"`
  * **Expected Answer**: `28.4` BLEU for English-to-German, `41.0` BLEU for English-to-French (Table 2, Page 8).
* **Query**: `"What hyperparameters were used for learning rate warmup steps and optimizer parameters?"`
  * **Expected Answer**: 4,000 warmup steps; Adam optimizer ($\beta_1=0.9, \beta_2=0.98, \epsilon=10^{-9}$).

#### 🧮 2. Mathematical & Formula Queries
* **Query**: `"What is the mathematical formula for Scaled Dot-Product Attention, including the scaling factor sqrt(d_k)?"`
  * **Expected Answer**: $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$ (Section 3.2.1, Page 4).
* **Query**: `"Write the formulas used to calculate Positional Encodings using sine and cosine functions."`
  * **Expected Answer**: $PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$, $PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$.

#### 🖼️ 3. Visual & Diagrammatic Queries
* **Query**: `"Describe the visual architecture of the Transformer model from Figure 1, detailing the Encoder and Decoder sub-layers."`
  * **Expected Answer**: Encoder has 2 sub-layers (Self-Attention + FFN); Decoder has 3 sub-layers (Masked Self-Attention + Cross-Attention + FFN) (Figure 1, Page 3).

#### 🔀 4. Hybrid / Cross-Modal Reasoning
* **Query**: `"Why is Scaled Dot-Product Attention divided by sqrt(d_k) when d_k is large?"`
  * **Expected Answer**: For large $d_k$, dot products grow large, pushing softmax into regions with vanishing gradients. Scaling brings variance back to 1.

---

## 📁 Repository Structure

```
multimodal_rag_v2/
├── .env                         # Local environment variables & API keys
├── pyproject.toml               # Python dependencies and build config
├── notebooks/
│   └── 02_colab_ingestion.ipynb # Portable Colab ingestion & test suite
├── src/
│   └── doc_parser/
│       ├── config.py            # Pydantic settings & validation
│       ├── chunker.py           # Structure-aware document chunking
│       ├── post_processor.py    # Markdown & structure formatting
│       ├── api/                 # FastAPI REST server & routes
│       ├── ingestion/           # Embedders (Dense/Sparse) & Qdrant store
│       └── retrieval/           # Re-ranker backends (BGE, OpenAI, Jina)
└── tests/                       # Unit and integration test suite
```

---

<div align="center">
<b>Multimodal RAG Pipeline v2</b> — Engineered for Precision & Scale.
</div>
