"""Environment and path configuration shared by all three retrieval pipelines."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project folder paths, worked out from this file's own location so they work
# no matter where the project is checked out.
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OKF_DIR = DATA_DIR / "okf"
PROCESSED_DIR = DATA_DIR / "processed"
FAISS_INDEX_PATH = PROCESSED_DIR / "faiss.index"
FAISS_META_PATH = PROCESSED_DIR / "faiss_meta.pkl"


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str
    groq_judge_api_key: str
    groq_judge_model: str
    jina_api_key: str
    jina_embedding_model: str
    jina_reranker_model: str


def get_settings() -> Settings:
    groq_api_key = os.environ.get("GROQ_API_KEY", "")
    return Settings(
        groq_api_key=groq_api_key,
        groq_model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        # A separate key/model for openevals judging: running the full eval suite on the
        # same key as generation exhausts Groq's free-tier tokens-per-minute limit, and
        # gpt-oss-120b was observed to sometimes emit reasoning text instead of the forced
        # structured-output tool call openevals relies on. gpt-oss-20b calls it reliably.
        groq_judge_api_key=os.environ.get("JUDGE_GROQ_API_KEY", "") or groq_api_key,
        groq_judge_model=os.environ.get("GROQ_JUDGE_MODEL", "openai/gpt-oss-20b"),
        jina_api_key=os.environ.get("JINA_API_KEY", ""),
        jina_embedding_model=os.environ.get("JINA_EMBEDDING_MODEL", "jina-embeddings-v3"),
        jina_reranker_model=os.environ.get("JINA_RERANKER_MODEL", "jina-reranker-v3.5"),
    )
