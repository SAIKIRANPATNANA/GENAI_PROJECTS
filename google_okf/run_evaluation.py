"""Run the openevals metric comparison across Basic RAG / OKF Retrieval / Hybrid RAG.

Usage:  python run_evaluation.py
Requires GROQ_API_KEY and JINA_API_KEY in .env, and a built FAISS index (build_index.py).
"""
from src.evaluation import run_evaluation, summarize

if __name__ == "__main__":
    rows = run_evaluation()
    summarize(rows)
