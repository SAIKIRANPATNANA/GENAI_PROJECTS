<div align="center">

# 🧠 MultiModal RAG via Diverse OCR & Document Parsing Strategies

### Comprehensive Benchmarking & Architectural Suite for Document Intelligence

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Qdrant](https://img.shields.io/badge/Qdrant-Cloud_%2F_Local-DC244C?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Groq](https://img.shields.io/badge/LLM-Groq_Llama--3.3--70b-f55036?style=flat-square)](https://groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-BYOK_UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat-square)](https://github.com/astral-sh/uv)

</div>

---

## 📌 Executive Summary

**MultiModal RAG via Diverse OCR Strategies** is a production-grade research and engineering framework designed to ingest, parse, chunk, index, and retrieve complex structured documents (e.g., scientific research papers, financial reports, technical documentation).

Standard text-based RAG systems fail when processing documents containing multi-column layouts, complex HTML/LaTeX tables, mathematical formulas, embedded diagrams, and visual charts. This monorepo implements and compares **three distinct, state-of-the-art OCR and document parsing paradigms**:

1. 📄 **IBM Docling Strategy** (`MULTIMODAL_RAG_VIA_DOCKLING`): End-to-End Multimodal Unified Parsing.
2. ⚡ **Baidu Unlimited-OCR & PaddleOCR Strategy** (`MULTIMODAL_RAG_VIA_UNLIMITED_OCR`): One-Shot Vision-Language Model (VLM) & Multi-Stage Layout OCR.
3. 🔬 **GLM-OCR + PP-DocLayout-V3 Strategy** (`MUTLIMODAL_RAG_VIA_GLMOCR`): Pipelined Object Detection (23 Categories), Bounding-Box Cropping, and Multi-Modal Vision LLM Captioning.

All strategies share a unified **Hybrid Vector Retrieval pipeline (Dense + BM25 Sparse with RRF score fusion)**, **BGE Cross-Encoder Re-Ranking**, **Groq Llama-3.3-70b LLM Generation**, and interactive **Streamlit dark-mode workbenches with Bring-Your-Own-Key (BYOK) credential management**.

---

## 🏛️ End-to-End System Architecture

```
                               📄 Input Complex Document (PDF / Image)
                                                 │
            ┌────────────────────────────────────┼────────────────────────────────────┐
            ▼                                    ▼                                    ▼
┌───────────────────────┐            ┌───────────────────────┐            ┌───────────────────────┐
│ Strategy 1: Docling   │            │ Strategy 2: Unlimited │            │ Strategy 3: GLM-OCR   │
│ (IBM End-to-End)      │            │ (Baidu VLM & Paddle)  │            │ (PP-DocLayout-V3)     │
│ • Unified Layout &    │            │ • Single-Pass VLM     │            │ • 23 Category Object  │
│   Structure Parsing   │            │ • Inline Markdown &   │            │   Detection BBoxes    │
│ • Unified Table/Math  │            │   HTML/LaTeX Output   │            │ • PyMuPDF Crop & VLM  │
└───────────┬───────────┘            └───────────┬───────────┘            └───────────┬───────────┘
            │                                    │                                    │
            └────────────────────────────────────┼────────────────────────────────────┘
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Structure & Modality-Aware Chunking   │
                             │ (Tables, Formulas, Text, Images)      │
                             └───────────────────┬───────────────────┘
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Hybrid Vector Embedding Generation    │
                             │ • Dense: BGE / MiniLM (Semantic)      │
                             │ • Sparse: BM25 (131k Feature Hashing) │
                             └───────────────────┬───────────────────┘
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Qdrant Vector Store Indexing          │
                             │ Dual Vectors + RRF Score Fusion       │
                             └───────────────────┬───────────────────┘
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Cross-Encoder Re-Ranking              │
                             │ BGE / Qwen VL / Jina / OpenAI         │
                             └───────────────────┬───────────────────┘
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Serving & User Interfaces             │
                             │ • Streamlit Workbench (BYOK Key UI)   │
                             │ • FastAPI REST API (/search,/generate)│
                             └───────────────────────────────────────┘
```

---

## 🔬 In-Depth Explanation of OCR Strategies

### 1️⃣ Strategy 1: IBM Docling (End-to-End Multimodal Parsing)
📁 **Directory**: [`MULTIMODAL_RAG_VIA_DOCKLING`](./MULTIMODAL_RAG_VIA_DOCKLING)

* **Overview**: Utilizes IBM's open-source **Docling** library to perform document parsing, layout recognition, table structure extraction, and formula reading in a single integrated pass.
* **Core Components**:
  * **Unified Model Pass**: Directly parses native PDF vector geometries alongside bitmap elements without splitting into disjoint pipeline stages.
  * **Docling Document Format (DoclingDocument)**: Maintains a hierarchical tree structure of headings, paragraphs, lists, tables, and code snippets.
* **Chunking Approach**:
  * Structure-aware chunking that preserves document hierarchy.
  * Ensures tables and formulas are retained as atomic chunks to prevent contextual loss.
* **Best Used For**:
  * Clean or native digital PDFs (e.g., arXiv research papers, financial prospectuses).
  * High-speed batch processing in memory-constrained or serverless environments.

---

### 2️⃣ Strategy 2: Baidu Unlimited-OCR & PaddleOCR (Vision-Language & Hybrid OCR)
📁 **Directory**: [`MULTIMODAL_RAG_VIA_UNLIMITED_OCR`](./MULTIMODAL_RAG_VIA_UNLIMITED_OCR)

* **Overview**: Incorporates **Baidu Unlimited-OCR** ([arXiv:2606.23050](https://arxiv.org/abs/2606.23050)), a state-of-the-art Vision-Language Model (VLM) paired with **PaddleOCR / PP-Structure** for long-horizon, high-density document parsing.
* **Core Components**:
  * **One-Shot VLM Inference**: Processes whole-page images through a unified Transformer Encoder-Decoder, directly emitting structured Markdown with embedded LaTeX math (`$$...$$`), HTML table cells, and spatial layout tokens (`<|det|>category [bbox]<|/det|>`).
  * **Fallback Pipelined Engine**: Offers PP-Structure (DBNet text detection + SVTR/CRNN text recognition + SLANet table structure) for lightweight local CPU execution.
* **Chunking Approach**:
  * Modality-specific tagging (`table`, `formula`, `text`, `image`).
  * Dedicated Colab ingestion workflow (`notebooks/03_colab_paddle_ocr_ingestion.ipynb`) for GPU acceleration.
* **Best Used For**:
  * Complex multi-column documents with heavy mathematical equations and complex nested tables.
  * Multilingual and CJK (Chinese, Japanese, Korean) + English document processing.

---

### 3️⃣ Strategy 3: GLM-OCR + PP-DocLayout-V3 (Pipelined Multi-Stage & Vision Enrichment)
📁 **Directory**: [`MUTLIMODAL_RAG_VIA_GLMOCR`](./MUTLIMODAL_RAG_VIA_GLMOCR)

* **Overview**: Implements a granular **Multi-Stage Pipelined Architecture** combining layout detection object models (**PP-DocLayout-V3**), spatial bounding-box cropping (**PyMuPDF**), OCR model inference (**GLM-OCR 0.9B**), and Vision LLM image captioning (**Qwen 3.6 27B / GPT-4o**).
* **Core Components**:
  * **23-Category Layout Detection**: Classifies document regions into 23 precise structural classes (`document_title`, `paragraph_title`, `abstract`, `paragraph`, `table`, `formula`, `figure`, `algorithm`, `footnote`, `reference`, etc.).
  * **Bounding-Box Normalization**: Coordinates are tracked on a normalized scale (`[0, 1000]`).
  * **Multimodal Figure Captioning**: Figures, charts, and diagrams are cropped using PyMuPDF and dispatched to Groq/OpenAI Vision models with surrounding text context, producing rich text summaries that enable keyword and semantic indexing for visual elements.
* **Chunking Approach**:
  * **Title Forwarding**: Binds heading elements to subsequent body text elements to eliminate orphan titles across page boundaries.
  * **Atomic Preservation**: Guarantees tables, formulas, and visual figures are never fragmented mid-element.
* **Best Used For**:
  * High-precision document intelligence requiring pixel-accurate bounding box visualizations.
  * Indexing image-heavy documents (diagrams, architecture charts, workflow plots).

---

## 📊 Comprehensive OCR Strategy Comparison Matrix

| Feature / Dimension | Strategy 1: IBM Docling (`MULTIMODAL_RAG_VIA_DOCKLING`) | Strategy 2: Unlimited-OCR (`MULTIMODAL_RAG_VIA_UNLIMITED_OCR`) | Strategy 3: GLM-OCR + Layout (`MUTLIMODAL_RAG_VIA_GLMOCR`) |
| :--- | :--- | :--- | :--- |
| **Parsing Paradigm** | End-to-End Structural Parser | One-Shot Vision-Language Model (VLM) | Multi-Stage Pipelined Layout OCR |
| **Primary Engine / Model** | IBM Docling Engine | Baidu Unlimited-OCR / PaddleOCR | PP-DocLayout-V3 + GLM-OCR 0.9B |
| **Layout Detection** | Native Docling Unified Layout Model | VLM Inline Detection Tokens | YOLOX / PP-DocLayout-V3 (23 Categories) |
| **Execution Steps** | 1-Pass Structural Parsing | 1-Pass (VLM) or Multi-Stage (Paddle) | Multi-Stage (Layout → Crop → OCR → Caption) |
| **Table Extraction** | Markdown & Struct HTML Tables | Native HTML Table Synthesis | Specialized SLANet & Markdown Tables |
| **Formula Extraction** | Inline / Block LaTeX | Native VLM LaTeX Synthesis | LaTeX Math via GLM-OCR |
| **Image & Chart Handling** | Extracted as Image Elements | Inline Bounding Boxes | PyMuPDF Crop + Vision LLM Captioning |
| **Error Propagation Risk**| Low | Minimal (Zero Cascade Error) | Moderate (Layout errors cascade to OCR) |
| **Hardware Requirement** | Low-Medium (CPU Friendly) | High for VLM (GPU), Low for Paddle | Medium (Local GPU / Ollama or Cloud API) |
| **Title Forwarding Chunking**| Standard Hierarchical | Modality-Tagged | Advanced (Prevents Orphan Headings) |
| **Spatial BBox Tracking** | Structural Relative Bounds | Normalized VLM Coordinates | Pixel-Accurate `0-1000` Bounding Boxes |
| **Cloud / Local Modes** | Local / Cloud Portable | Colab GPU / Cloud / Local | Dual Mode (Cloud Z.AI & Local Ollama) |

---

## ⚡ Shared RAG Pipeline Capabilities

Across all three OCR strategies, the framework provides identical, standardized retrieval and generation capabilities:

### 1. Hybrid Vector Search (Dense + BM25 Sparse)
* **Dense Semantic Embeddings**: Uses models like `BAAI/bge-small-en-v1.5` (384d), `all-MiniLM-L6-v2`, or `OpenAI text-embedding-3-large` (3072d).
* **Sparse Keyword Embeddings (BM25)**: Employs a **$2^{17} = 131,072$-bucket zero-vocabulary Feature-Hashing Trick**. Hashes n-gram terms with term-frequency (TF) weights to guarantee exact matching for technical terms, formulas, model names, and IDs without static vocabulary limits.
* **Reciprocal Rank Fusion (RRF)**: Executes parallel dense and sparse prefetch queries inside Qdrant and merges rankings via RRF:
  $$\text{RRF Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)} \quad (k=60)$$

### 2. Cross-Encoder Re-Ranking
Supports pluggable second-stage re-ranker backends to refine candidate precision:
* **BAAI BGE Cross-Encoder** (`bge-reranker-v2-minicpm` / `bge-reranker-large`)
* **Qwen3-VL-Reranker-2B** (Vision-aware re-ranking)
* **Jina Reranker M0** & **OpenAI GPT-4o-mini**

### 3. Serving & User Interfaces
* **FastAPI REST API**: Production-grade async endpoints (`POST /search`, `POST /generate`, `POST /ingest`, `GET /health`).
* **Streamlit Dark-Mode Workbench**:
  * **Bring-Your-Own-Key (BYOK)**: Input Groq API Key, Qdrant URL, and Qdrant API Key directly in the UI without modifying system files.
  * **Modality Filtering**: Filter search targets by `table`, `formula`, `image`, or `text`.
  * **Ground-Truth Benchmarking**: Built-in 15-query test suite for *"Attention Is All You Need"*.

---

## 🗂️ Code & Directory Structure

```
MULTIMODAL_RAG_VIA_DIFF_OCR_STRATEGIES/
├── 📄 README.md                             # Monorepo master documentation
├── 📄 readme.md                             # Master documentation (symlink/copy)
├── 📄 LICENSE                               # MIT License
│
├── 📁 MULTIMODAL_RAG_VIA_DOCKLING/          # Strategy 1: IBM Docling Engine
│   ├── 📄 pyproject.toml                    # UV build config & dependencies
│   ├── 📄 app.py                            # Streamlit Web App with BYOK
│   ├── 📄 README.md                         # Docling-specific detailed guide
│   ├── 📁 notebooks/
│   │   └── 02_colab_ingestion.ipynb         # Portable Colab ingestion notebook
│   └── 📁 src/doc_parser/
│       ├── config.py                        # Pydantic settings & validation
│       ├── chunker.py                       # Hierarchical structure chunker
│       ├── api/                             # FastAPI REST endpoints
│       ├── ingestion/                       # Embedders & Qdrant vector store
│       └── retrieval/                       # Cross-encoder re-rankers
│
├── 📁 MULTIMODAL_RAG_VIA_UNLIMITED_OCR/     # Strategy 2: Baidu Unlimited-OCR & Paddle
│   ├── 📄 pyproject.toml                    # UV build config
│   ├── 📄 app.py                            # Streamlit Web App with BYOK
│   ├── 📄 README.md                         # Unlimited-OCR detailed guide
│   ├── 📁 notebooks/
│   │   └── 03_colab_paddle_ocr_ingestion.ipynb # Baidu Colab ingestion notebook
│   └── 📁 src/doc_parser/
│       ├── config.py                        # System settings
│       ├── chunker.py                       # Modality-aware chunker
│       ├── api/                             # FastAPI server
│       ├── ingestion/                       # PaddleOCR & VLM embedders
│       └── retrieval/                       # BGE re-ranker backend
│
└── 📁 MUTLIMODAL_RAG_VIA_GLMOCR/            # Strategy 3: GLM-OCR + PP-DocLayout-V3
    ├── 📄 pyproject.toml                    # UV build config & dev dependencies
    ├── 📄 config.yaml                       # Z.AI MaaS / GLM-OCR SDK config
    ├── 📄 app.py                            # Streamlit Bounding Box Visualizer
    ├── 📄 README.md                         # GLM-OCR detailed guide
    ├── 📁 notebooks/
    │   └── 02_colab_ingestion.ipynb         # Colab ingestion workflow
    ├── 📁 ollama/                           # 100% Local offline setup
    │   ├── visualize.py                     # Streamlit local bounding box inspector
    │   └── config.yaml                      # Ollama local config
    ├── 📁 scripts/                          # CLI utilities (parse, ingest, search, serve)
    ├── 📁 src/doc_parser/
    │   ├── pipeline.py                      # PP-DocLayout-V3 & GLM-OCR wrapper
    │   ├── post_processor.py                # BBox normalization & Markdown builder
    │   ├── chunker.py                       # Structure-aware & Title-Forwarding chunker
    │   ├── ingestion/                       # Embedders & Image Vision Captioner
    │   ├── retrieval/                       # Cross-encoder re-rankers
    │   └── api/                             # Async FastAPI server
    └── 📁 workflows/                        # Architecture & design documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

Ensure you have **Python 3.12+** and the **`uv`** package manager installed:

```bash
# Install uv package manager (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Choose and Setup Your Desired OCR Strategy

#### Option A: Running Strategy 1 (Docling)

```bash
cd MULTIMODAL_RAG_VIA_DOCKLING

# Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies in editable mode
uv pip install -e .

# Launch Streamlit Workbench
uv run streamlit run app.py
```

#### Option B: Running Strategy 2 (Baidu Unlimited-OCR / PaddleOCR)

```bash
cd MULTIMODAL_RAG_VIA_UNLIMITED_OCR

# Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Launch Streamlit Workbench
uv run streamlit run app.py
```

#### Option C: Running Strategy 3 (GLM-OCR + PP-DocLayout-V3)

```bash
cd MUTLIMODAL_RAG_VIA_GLMOCR

# Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies with layout extra
uv pip install -e ".[layout]"

# Launch CLI parser
python scripts/parse.py path/to/document.pdf --chunks

# Launch Streamlit visualizer
uv run streamlit run app.py
```

---

## 🧪 Benchmark Test Matrix (*Attention Is All You Need*)

To evaluate and compare performance across the three strategies, test queries targeting different document modalities are provided:

| Query Type | Sample Test Query | Expected Ground Truth Content |
| :--- | :--- | :--- |
| 📊 **Table & Quantitative** | *"What are the BLEU scores for Transformer (big) on the WMT 2014 English-to-German and English-to-French translation tasks?"* | **28.4 BLEU** (EN-DE), **41.0 BLEU** (EN-FR) (Table 2, Page 8) |
| 🧮 **Mathematical Formula** | *"What is the mathematical formula for Scaled Dot-Product Attention, including the scaling factor sqrt(d_k)?"* | $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$ (Sec 3.2.1, Page 4) |
| 🧮 **Formula & Parameters** | *"Write the formulas used to calculate Positional Encodings using sine and cosine functions."* | $PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{model}})$, $PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{model}})$ |
| 🖼️ **Visual Architecture** | *"Describe the visual architecture of the Transformer model from Figure 1, detailing the Encoder and Decoder sub-layers."* | Encoder: 2 sub-layers (Self-Attn + FFN); Decoder: 3 sub-layers (Masked Attn + Cross Attn + FFN) |
| 🔀 **Cross-Modal Reasoning** | *"Why is Scaled Dot-Product Attention divided by sqrt(d_k) when d_k is large?"* | Prevents dot products from growing large and pushing softmax into regions with vanishing gradients. |

---

## 🎯 Strategy Decision Guide: Which OCR Engine to Choose?

* Choose **IBM Docling Strategy** if you need a lightweight, fast, pure-Python solution for standard digital PDFs without complex image captioning requirements.
* Choose **Baidu Unlimited-OCR Strategy** if your documents contain heavy mathematical formulas, multi-lingual text (CJK/English), or dense structured tables, and you have access to GPU acceleration.
* Choose **GLM-OCR + Layout Strategy** if you require pixel-accurate spatial bounding boxes, visual layout classification across 23 element categories, or rich Vision LLM captioning of embedded diagrams and figures.

---

<div align="center">

**MultiModal RAG via Diverse OCR Strategies** — Built for Precision Document Intelligence.

</div>
