# Generative AI Projects

This repository groups together my Generative AI projects in one place for cleaner portfolio management and easier exploration.

Recent additions in this repository also include content-focused, safety-focused, evaluation-focused, and agent-engineering GenAI systems:

- `blog-generation-agenticai` for AI-assisted long-form blog drafting and content generation workflows.
- `ainews-generation-agenticai` for AI-driven news generation, summarization, and topic-oriented publishing ideas.
- `blood-report-parsing-iisc` for AI-assisted blood report parsing, abnormality detection, and healthcare-oriented structured extraction.
- `ai_guardrails` for NeMo Guardrails, Colang flows, input/output rails, and safer LLM behavior design.
- `agentic_memory` for AI Memory Lab, a Streamlit/Groq demo suite covering short-term memory, long-term memory, vector-store memory, entity memory, episodic/semantic/procedural memory, self-reflection, routing, cost tracking, and architecture diagrams.
- `advanced_prod_rag` for production-ready enterprise RAG with OpenAI/Anthropic routing through Portkey, Jina embeddings/reranking, Qdrant retrieval, Prometheus metrics, auth, rate limiting, Neon/Upstash integrations, tests, and AWS deployment scripts.
- `loop_engineering_demo` for a TestSprite loop-engineering demo showing build -> verify -> inspect failure bundle -> fix -> deploy -> rerun around an intentional checkout regression.
- `harness_engineering_demo` for a LangGraph multi-agent support harness with guardrail, router, specialist agents, and reviewer agent patterns.
- `google_okf` for comparing Basic RAG, Google Open Knowledge Format retrieval, and Hybrid RAG with LangGraph, FAISS, Jina reranking, Groq, openevals, and LangSmith experiments.
- `rag_evaluation` for RAGAS-based evaluation of retrieval and generation quality in a product-catalog RAG app.
- `llm_gateways` for production LLM gateway concepts including Portkey routing, retries, fallbacks, observability, caching, rate limits, load balancing, and streaming.
- `multimodal_rag_via_diff_ocr` for comparing Docling, Unlimited-OCR/PaddleOCR, and GLM-OCR layout strategies inside a multimodal RAG pipeline with Qdrant hybrid search, RRF fusion, reranking, Groq generation, FastAPI, and Streamlit BYOK workbenches.

## Included Projects

- `ainews-generation-agenticai`
- `ai_guardrails`
- `agentic_memory`
- `advanced_rag`
- `advanced_prod_rag`
- `ats-using-gemini`
- `blog-generation-agenticai`
- `blood-report-parsing-iisc`
- `calorie-calc-using-gpv`
- `disease-diagnosis-dhanvantari`
- `google_okf`
- `harassment-bot`
- `harness_engineering_demo`
- `hybd_cmr_edtech`
- `loop_engineering_demo`
- `med-triage-agenticai`
- `llm_gateways`
- `multimodal_rag_via_diff_ocr`
- `pskgpt-via-transformers`
- `rag_evaluation`
- `sadhana-gen-ai-project`
- `stance-detection`
- `whatsapp-chat-analyser`

## Notes

- Nested Git repositories, FAISS index files, and local generated artifacts are removed so this repo can be pushed cleanly as a single grouped repository.
- Secrets and hardcoded API keys should always be replaced with environment variable usage before pushing.
- Project folders may continue to be refined over time with better documentation, screenshots, and deployment notes.
