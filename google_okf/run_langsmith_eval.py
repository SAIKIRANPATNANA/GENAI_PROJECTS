"""Run the LangSmith Dataset + Experiment version of the eval comparison, so Basic RAG /
OKF Retrieval / Hybrid RAG are directly comparable in the LangSmith dashboard.

Usage: python run_langsmith_eval.py
"""
from src.langsmith_eval import run_langsmith_eval

if __name__ == "__main__":
    run_langsmith_eval()
