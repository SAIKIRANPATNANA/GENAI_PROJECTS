<div align="center">

# 🧠 MultiModal RAG Pipeline (v3)

### Baidu PaddleOCR & PP-DocLayout-V3 → Qdrant Hybrid RRF Search → BGE Reranker → Groq Llama-3.3-70b

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Baidu PaddleOCR](https://img.shields.io/badge/OCR-Baidu_PaddleOCR-2932E1?style=flat-square)](https://github.com/PaddlePaddle/PaddleOCR)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud_%2F_Local-DC244C?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Groq](https://img.shields.io/badge/LLM-Groq_Llama--3.3--70b-f55036?style=flat-square)](https://groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-BYOK_UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)

</div>

---

> **Parsing Architecture & OCR Approach**:
> **MultiModal RAG v3** leverages a **hybrid OCR architecture**, primarily powered by **End-to-End Vision-Language Models (Baidu Unlimited-OCR / GLM-OCR)** with fallback support for **Pipelined Multi-Stage OCR (PP-Structure / PaddleOCR)**. Document ingestion is offloaded to **Google Colab (`notebooks/03_colab_paddle_ocr_ingestion.ipynb`)** for GPU-accelerated processing and direct indexing into Qdrant Cloud.

---

## 🔬 OCR Architecture Breakdown: End-to-End vs. Pipelined

This repository supports both **End-to-End VLM-based OCR** and **Pipelined Multi-Stage OCR** approaches for document intelligence and structured PDF extraction:

### 1. End-to-End VLM Approach (Primary)
* **Models**: `baidu/Unlimited-OCR` ([arXiv:2606.23050](https://arxiv.org/abs/2606.23050)) & `GLM-OCR` (Z.AI MaaS / local).
* **Architecture**: Unified **Vision-Language Model (VLM)** / Transformer Encoder-Decoder.
* **Mechanism**: Accepts full document page images directly and produces structured Markdown, inline layout detection markers (`&lt;\|det\|&gt;category [bbox]&lt;\|/det\|&gt;`), LaTeX equations, and HTML tables in a **single unified forward pass**.
* **Key Advantages**:
  * **Zero Cascade Error Propagation**: Eliminates cascading errors between separate layout detection and OCR stages.
  * **Native Table & Formula Parsing**: Synthesizes complex HTML tables and LaTeX math natively without dedicated sub-models.
  * **Contextual Reading Order**: Naturally respects multi-column layouts and visual hierarchy.

### 2. Pipelined Multi-Stage Approach (Fallback / Modular)
* **Models**: `PaddleOCR` / `PP-Structure` (v2/v3), DBNet, SVTR/CRNN, PyMuPDF.
* **Architecture**: Sequential **Multi-Module Pipeline**.
* **Mechanism**:
  1. **Layout Detection**: Identifies element bounding boxes via layout models (e.g., PP-DocLayout-V3 / YOLOX).
  2. **Text Region OCR**: Runs text detection (DBNet) and character recognition (SVTR/CRNN) cropped region by cropped region.
  3. **Table Extraction**: Uses dedicated table structure recognition (SLANet) to rebuild cell grids into HTML.
  4. **Assembly**: Sorts reading order and stitches elements into markdown.
* **Key Advantages**:
  * **Lightweight CPU Execution**: Runs efficiently without heavy VLM GPU VRAM requirements.
  * **Explicit Bounding Box Tracking**: Provides precise coordinate metrics per recognized word or line.

### 📊 Comparison Summary

| Feature | End-to-End Approach (`baidu/Unlimited-OCR`, `GLM-OCR`) | Pipelined Approach (`PP-Structure`, `PaddleOCR`) |
| :--- | :--- | :--- |
| **Model Type** | Unified Vision-Language Transformer | Multi-stage pipeline (Layout + OCR + Table sub-models) |
| **Execution Pass** | **Single pass** (One-Shot Image → Markdown) | **Multi-stage** (Layout → OCR → Table → Assembly) |
| **Formula & Tables** | Native LaTeX & HTML generation | Requires specialized sub-models (SLANet) |
| **Error Cascade** | Low (No inter-module error accumulation) | Higher (Layout misclassification affects text extraction) |
| **Hardware Requirement** | GPU Recommended (`bfloat16` / CUDA) | CPU Friendly / Low VRAM |

---

## 🌟 Overview & Architecture

```
📄 Complex Document (PDF)
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1 · Baidu PaddleOCR / PP-DocLayout-V3 Engine          │
│  - Unlimited high-accuracy OCR (English & Multilingual)     │
│  - Layout classification & HTML table structure extraction  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2 · Dense + Sparse Hybrid Vector Search              │
│  - Dense: BAAI/bge-small-en-v1.5 (384-dim semantic)         │
│  - Sparse: SPLADE / Feature-Hashed BM25                     │
│  - Vector Store: Qdrant Cloud (`multimodal_rag_v3_docs`)    │
│  - Fusion Strategy: Reciprocal Rank Fusion (RRF)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3 · Serving, Re-Ranking & RAG Generation             │
│  - Re-ranker: BAAI BGE Cross-Encoder                        │
│  - Generation: Groq Llama-3.3-70b-versatile                 │
│  - Web Interface: Streamlit (`app.py`) with BYOK Keys       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites & Virtual Environment

```bash
cd multimodal_rag_v3

# Create & activate virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install package in editable mode
uv pip install -e .
```

### 2. Streamlit Web App with BYOK (Bring Your Own Key)

```bash
uv run streamlit run app.py
```

Features:
* 🔑 **BYOK Credentials**: Enter `Groq API Key`, `Qdrant URL`, and `Qdrant API Key` directly in the sidebar.
* 🤖 **1-Click Presets**: Test queries from *Attention Is All You Need*.
* 🔍 **Modality Filters**: Filter search across `table`, `formula`, `image`, and `text`.

### 3. FastAPI REST Server

```bash
uvicorn doc_parser.api.app:app --reload --port 8000
```

---

## 📁 Repository Structure

```
multimodal_rag_v3/
├── .env.example                 # Environment variable template
├── pyproject.toml               # Package dependencies & build configuration
├── app.py                       # Streamlit Web App with BYOK credentials
├── notebooks/
│   └── 03_colab_paddle_ocr_ingestion.ipynb # Baidu PaddleOCR Colab ingestion
├── src/
│   └── doc_parser/
│       ├── config.py            # Pydantic settings & validation
│       ├── chunker.py           # Structure-aware document chunker
│       ├── api/                 # FastAPI REST routes (/search, /generate)
│       ├── ingestion/           # PaddleOCR engine, Embedder, & Qdrant store
│       └── retrieval/           # BGE Cross-Encoder re-ranker
└── tests/                       # Unit and integration test suite
```
