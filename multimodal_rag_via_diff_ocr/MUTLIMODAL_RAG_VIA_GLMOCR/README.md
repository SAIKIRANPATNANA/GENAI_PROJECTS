<div align="center">

# 🧠 MultiModal RAG Pipeline

### Production-Grade Document Intelligence · Layout Analysis · Hybrid Search · Re-Ranking

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C?style=flat-square)](https://qdrant.tech)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat-square)](https://github.com/astral-sh/uv)

</div>

> [!NOTE]
> **Parsing Architecture (Pipelined OCR Approach)**:
> This repository follows a **Pipelined OCR Strategy** — combining object detection (**PP-DocLayout-V3**), bounding box image cropping (**PyMuPDF**), and separate OCR / Vision models (**GLM-OCR 0.9B** / **qwen3.6-27b**). Portable ingestion is supported via Google Colab (`02_colab_ingestion.ipynb`).

```

**MultiModal RAG** is an end-to-end local-first document intelligence pipeline. It converts complex PDF documents and images into structured Markdown, extracts tables/formulas/figures with bounding box spatial awareness, computes hybrid vector representations (Dense + BM25 Sparse), and re-ranks retrieval candidates for downstream LLM generation.

It natively supports both **Cloud Mode** (Z.AI MaaS + OpenAI / Groq / Gemini) and **Fully Local Mode** (Ollama + sentence-transformers + BGE / Qwen VL rerankers).

```
📄 Input PDF / Image
      │
      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Document Parsing & Layout Detection (PP-DocLayout-V3 + GLM-OCR)      │
│    • Identifies 23 element categories (headings, formulas, tables, etc)│
│    • Extracts normalized bounding boxes [y_min, x_min, y_max, x_max]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Structure-Aware & Document-Aware Chunking                           │
│    • Atomic preserving: Tables, formulas, figures & algorithms         │
│    • Title forwarding: Prevents orphan headings across pages            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Multimodal Enrichment & Captioning (Groq / OpenAI Vision)           │
│    • Bounding box PDF cropping → Vision LLM caption generation        │
│    • Converts raw figures & charts into searchable visual descriptions │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Hybrid Embedding (Dense Semantic + Sparse BM25 Feature-Hashing)      │
│    • Dense: OpenAI (3072d), Gemini (3072d), or Local MiniLM (384d)     │
│    • Sparse: 131,072-bucket TF feature hashing (no static vocab needed) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. Qdrant Hybrid Storage & Reciprocal Rank Fusion (RRF)                │
│    • Dual vector collection (text_dense + bm25_sparse)                 │
│    • Prefetch candidate retrieval + RRF score fusion                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 6. Cross-Encoder Re-Ranking                                            │
│    • Pluggable backends: BGE (local fast), Qwen VL, Jina M0, OpenAI    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 7. Serving Layer (FastAPI REST API & Streamlit BBox Visualizer)        │
│    • Async REST API (/ingest, /search, /health, /collections)          │
│    • Streamlit layout & polygon bounding box visualizer                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Detailed Architecture & How It Works

### Phase 1: Parsing & Layout Analysis
* **PP-DocLayout-V3**: Performs object detection on document pages to classify regions into **23 distinct element categories** (e.g., `document_title`, `paragraph_title`, `abstract`, `paragraph`, `table`, `formula`, `figure`, `algorithm`, `reference`, `footnote`).
* **GLM-OCR 0.9B**: Recognizes textual content, generates HTML representation for tables, LaTeX math expressions for block formulas, and outputs spatial bounding boxes normalized to `0-1000`.

### Phase 2: Structure-Aware & Document-Aware Chunking
* **Atomic Elements**: Elements tagged as `table`, `formula`, `image`, `figure`, or `algorithm` are treated as atomic units. They are never split mid-element or merged with plain text.
* **Title Forwarding**: Heading elements (`document_title`, `paragraph_title`) automatically bind to subsequent body text elements to prevent orphan section titles.
* **Token Boundaries**: Text blocks accumulate until reaching `max_chunk_tokens` (default: 512). Oversized text is split cleanly on whitespace boundaries.

### Phase 3: Multimodal Enrichment & Image Captioning
* **Crop & Base64 Encoding**: When an image or figure element is encountered, PyMuPDF crops the exact bounding box from the rendering canvas and encodes it as a high-resolution base64 PNG.
* **Contextual Prompting**: Surrounding textual context (preceding/succeeding chunks) and the PDF crop are fed to a Vision Model (Groq `qwen/qwen3.6-27b` or OpenAI `gpt-4o`).
* **Structured Output**: Generates concise summaries, visual details, structural diagrams, and captions, allowing non-text content to be indexed by text embedding models.

### Phase 4: Hybrid Embeddings (Dense + BM25 Sparse)
* **Dense Vectors**: Captures high-level semantic meaning using sentence-transformers (`all-MiniLM-L6-v2`, 384d), OpenAI (`text-embedding-3-large`, 3072d), or Gemini.
* **Sparse Vectors (BM25)**: Applies a zero-vocabulary **Feature-Hashing Trick** that hashes token n-grams into $2^{17} = 131,072$ hash buckets with term-frequency (TF) weights. This ensures exact keyword matching for model names, mathematical symbols, and IDs without maintaining a huge static vocabulary.

### Phase 5: Qdrant Hybrid Storage & Reciprocal Rank Fusion (RRF)
* **Dual Indexing**: Stores points with dual named vectors (`text_dense` with Cosine distance and `bm25_sparse`).
* **Reciprocal Rank Fusion (RRF)**: At query time, Qdrant executes parallel prefetch queries for dense semantic search and BM25 sparse search. Results are combined using RRF scoring:
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  where $k = 60$ and $r_m(d)$ is the rank of document $d$ in retrieval method $m$.

### Phase 6: Cross-Encoder Re-Ranking
Top candidate chunks retrieved from Qdrant pass through a second-stage cross-encoder re-ranker:
* **BAAI/bge-reranker-v2-minicpm** (Local, CPU/GPU, ultra-fast 50ms)
* **Qwen3-VL-Reranker-2B** (Local VLM, vision-capable)
* **Jina Reranker M0** (Cloud API)
* **OpenAI GPT-4o-mini** (Cloud LLM cross-encoder)

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [CLI Reference](#-cli-reference)
- [REST API Reference](#-rest-api-reference)
- [Configuration Reference](#-configuration-reference)
- [Local Mode (Ollama)](#-local-mode-ollama)
- [Visual Inspector (Streamlit)](#-visual-inspector-streamlit)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)

---

## 🛠️ Prerequisites

| Requirement | Version | Description |
| :--- | :--- | :--- |
| **Python** | `3.12+` | Runtime environment |
| **uv** | Latest | Fast Python package installer and virtualenv manager |
| **Qdrant** | `v1.13+` | Vector DB (running locally as binary or via Qdrant Cloud) |
| **Z.AI API Key** | — | Optional: Required for Cloud parsing (`PARSER_BACKEND=cloud`) |
| **OpenAI / Groq Key** | — | Required for image captioning, embeddings, or cloud re-ranking |

### Installing `uv`

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## ⚡ Quick Start

```bash
# 1. Navigate to the project directory
cd multi-modal-rag-master

# 2. Create and activate Python virtual environment
uv venv --python 3.12
source .venv/bin/activate

# 3. Install project package and dependencies
uv pip install -e ".[dev]"

# 4. Configure environment variables
cp .env.example .env
# Edit .env to add your API keys (or set PARSER_BACKEND=ollama for local mode)

# 5. Start Qdrant locally (or set QDRANT_URL in .env to Qdrant Cloud)
qdrant

# 6. Parse a document to Markdown and JSON
python scripts/parse.py data/raw/sample.pdf --chunks

# 7. Ingest document into Qdrant vector store
python scripts/ingest.py data/raw/sample.pdf

# 8. Run hybrid search with cross-encoder re-ranking
python scripts/search.py "What is the primary contribution of this work?"

# 9. (Optional) Start the FastAPI REST API server
python scripts/serve.py --reload
```

---

## 🖥️ CLI Reference

### 1. `scripts/parse.py` — PDF & Image Parser
Parses documents into clean Markdown, element JSON, and RAG chunks.

```bash
python scripts/parse.py <input-path> [options]
```

| Option | Default | Description |
| :--- | :--- | :--- |
| `input` | *(Required)* | File path or directory containing PDFs/images |
| `--output` | `./output/` | Output directory for `.md` and `.json` files |
| `--format` | `both` | Output format: `markdown`, `json`, or `both` |
| `--chunks` | Off | Generate RAG chunk file (`*_chunks.json`) |
| `--log-level` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`) |

**Examples:**
```bash
python scripts/parse.py data/raw/sample.pdf --chunks
python scripts/parse.py ./docs_folder/ --output ./parsed_output/ --format markdown
```

---

### 2. `scripts/ingest.py` — Embedding & Vector Indexing
Parses, enriches non-text chunks, computes embeddings, and upserts points to Qdrant.

```bash
python scripts/ingest.py <input-path> [options]
```

| Option | Default | Description |
| :--- | :--- | :--- |
| `input` | *(Required)* | File path or directory to ingest |
| `--no-caption` | Off | Skip vision LLM image/figure captioning |
| `--collection` | `.env` default | Target Qdrant collection name |
| `--overwrite` | Off | Re-create collection from scratch before upserting |
| `--max-chunk-tokens`| `512` | Token limit for text chunks |

**Examples:**
```bash
python scripts/ingest.py data/raw/sample.pdf
python scripts/ingest.py data/raw/sample.pdf --overwrite --collection my_docs
```

---

### 3. `scripts/search.py` — Hybrid Search & Re-Ranking
Queries Qdrant using hybrid retrieval (Dense + BM25 Sparse) and re-ranks top candidates.

```bash
python scripts/search.py "<query>" [options]
```

| Option | Default | Description |
| :--- | :--- | :--- |
| `query` | *(Required)* | Search query string |
| `--top-k` | `20` | Candidate count retrieved from vector store |
| `--top-n` | `.env` default | Final result count returned after re-ranking |
| `--backend` | `.env` default | Re-ranker backend: `openai`, `jina`, `bge`, `qwen` |
| `--filter-modality`| All | Filter by chunk modality: `text`, `image`, `table`, `formula` |
| `--no-rerank` | Off | Skip second-stage re-ranking |

**Examples:**
```bash
python scripts/search.py "transformer attention mechanism"
python scripts/search.py "performance benchmark" --filter-modality table --backend bge
```

---

### 4. `scripts/serve.py` — FastAPI REST Server
Launches the production-ready FastAPI backend server.

```bash
python scripts/serve.py --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 REST API Reference

Interactive API documentation is available at **`http://localhost:8000/docs`** (Swagger UI) or **`http://localhost:8000/redoc`**.

### Core Endpoints

| Method | Path | Summary | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health Check | Verifies connectivity to Qdrant & LLM APIs |
| `GET` | `/collections` | List Collections | Lists available Qdrant vector collections |
| `POST` | `/ingest` | Ingest by Path | Ingests a document using a server-side file path |
| `POST` | `/ingest/file` | Multipart Upload | Uploads and ingests a document directly |
| `POST` | `/search` | Search & Re-rank | Runs hybrid search and cross-encoder re-ranking |

#### `POST /search` Payload & Curl Example:

```json
{
  "query": "transformer multi-head attention",
  "top_k": 20,
  "top_n": 5,
  "filter_modality": null,
  "rerank": true
}
```

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer multi-head attention", "top_k": 10, "top_n": 3}'
```

---

## ⚙️ Configuration Reference

All settings are managed via `.env` and validated automatically at startup using `pydantic-settings`.

```dotenv
# ─── PARSER CONFIGURATION ───────────────────────────────────────────────────
PARSER_BACKEND=cloud               # "cloud" (Z.AI MaaS API) or "ollama" (local)
Z_AI_API_KEY=your_z_ai_key         # Required when PARSER_BACKEND=cloud

# ─── LLM / VISION ENRICHMENT ────────────────────────────────────────────────
GROQ_API_KEY=gsk_your_groq_key     # Groq Free Tier (takes priority if set)
GROQ_VISION_MODEL=qwen/qwen3.6-27b # Vision model for figure captioning
GROQ_TEXT_MODEL=meta/llama-3.3-70b-versatile
OPENAI_API_KEY=sk-your_openai_key  # Fallback for OpenAI LLM & Vision

# ─── EMBEDDINGS ─────────────────────────────────────────────────────────────
EMBEDDING_PROVIDER=local           # "local" (sentence-transformers), "openai", "gemini"
EMBEDDING_MODEL=all-MiniLM-L6-v2   # Model name
EMBEDDING_DIMENSIONS=384           # 384 for local, 3072 for OpenAI text-embedding-3-large

# ─── QDRANT VECTOR STORE ───────────────────────────────────────────────────
QDRANT_URL=http://localhost:6333   # Local binary URL or Qdrant Cloud URL
QDRANT_API_KEY=                    # Blank for local; set for Qdrant Cloud
QDRANT_COLLECTION_NAME=documents

# ─── RE-RANKER CONFIGURATION ─────────────────────────────────────────────────
RERANKER_BACKEND=bge               # "bge" (local fast), "qwen", "jina", "openai"
RERANKER_TOP_N=5                   # Number of final results after re-ranking
```

---

## 🦙 Local Mode (Ollama)

Run the entire pipeline 100% locally with zero external API calls:

```bash
# 1. Install & start Ollama
ollama serve

# 2. Pull GLM-OCR model
ollama pull glm-ocr:latest

# 3. Install local layout dependencies
uv pip install -e ".[layout]"

# 4. Set PARSER_BACKEND=ollama in .env
```

---

## 🎨 Visual Inspector (Streamlit)

Visualize bounding boxes, document element classifications, and page polygons:

```bash
# Cloud API visualizer
uv run streamlit run app.py

# Ollama local visualizer
uv run streamlit run ollama/visualize.py
```

---

## 🗂️ Project Structure

```
multi-modal-rag-master/
├── 📄 pyproject.toml              # Project configuration & dependencies
├── 📄 config.yaml                 # GLM-OCR cloud SDK configuration
├── 📄 .env.example                # Environment variables template
│
├── src/doc_parser/
│   ├── config.py                  # Pydantic settings singleton
│   ├── pipeline.py                # DocumentParser wrapper for GLM-OCR
│   ├── post_processor.py          # Markdown assembly & element conversion
│   ├── chunker.py                 # Structure-aware & title-forwarding chunker
│   ├── logging_config.py          # Loguru logging setup
│   │
│   ├── ingestion/
│   │   ├── embedder.py            # Dense (Local/OpenAI/Gemini) & Sparse BM25
│   │   ├── image_captioner.py     # Groq/OpenAI vision model captioning
│   │   └── vector_store.py        # Qdrant hybrid vector store wrapper
│   │
│   ├── retrieval/
│   │   └── reranker.py            # Cross-encoder re-rankers (BGE/Qwen/Jina/OpenAI)
│   │
│   └── api/
│       ├── app.py                 # FastAPI application factory
│       ├── dependencies.py        # Dependency injection singletons
│       ├── middleware.py          # Request ID correlation middleware
│       ├── schemas.py             # Pydantic API schemas
│       └── routes/
│           ├── health.py          # GET /health, GET /collections
│           ├── ingest.py          # POST /ingest, POST /ingest/file
│           └── search.py          # POST /search
│
├── 🎨 app.py                      # Streamlit cloud inspector
│
├── 🦙 ollama/
│   ├── config.yaml                # Ollama-specific GLM-OCR config
│   ├── test_parse.py              # CLI local parser test
│   └── visualize.py               # Streamlit local inspector
│
├── 📜 scripts/
│   ├── parse.py                   # PDF → Markdown + JSON CLI
│   ├── ingest.py                  # Document ingestion CLI
│   ├── search.py                  # Search & re-ranking CLI
│   └── serve.py                   # FastAPI server launcher
│
└── 📖 workflows/                  # Architecture & design documentation
```

---

## 🔍 Troubleshooting

<details>
<summary><strong>Qdrant connection refused</strong></summary>

Ensure your local Qdrant process is running:
```bash
qdrant
```
Or check that `QDRANT_URL` in `.env` points to your active Qdrant Cloud cluster.
</details>

<details>
<summary><strong>Missing Z_AI_API_KEY error</strong></summary>

If you want to run completely locally without an API key, update `.env`:
```dotenv
PARSER_BACKEND=ollama
```
</details>

<details>
<summary><strong>Dimension mismatch on Qdrant vector store</strong></summary>

If you change `EMBEDDING_DIMENSIONS` in `.env`, run ingestion with `--overwrite` to recreate the collection:
```bash
python scripts/ingest.py data/raw/sample.pdf --overwrite
```
</details>

---

<div align="center">

**Built with Python 3.12 · uv · FastAPI · Qdrant · Streamlit**

</div>
