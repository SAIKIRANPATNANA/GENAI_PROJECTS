import pandas as pd
import streamlit as st
from langchain_groq import ChatGroq

import common
import engine
import scenario
from embeddings import get_embedder
from memory_strategies.buffer import BufferMemoryStrategy
from memory_strategies.entity import EntityMemoryStrategy
from memory_strategies.no_memory import NoMemoryStrategy
from memory_strategies.sliding_window import SlidingWindowStrategy
from memory_strategies.summary import SummaryMemoryStrategy
from memory_strategies.summary_buffer import SummaryBufferStrategy
from memory_strategies.token_buffer import TokenBufferStrategy
from memory_strategies.vector_store import VectorStoreMemoryStrategy
from tracking import UsageTracker

st.set_page_config(page_title="Comparison", page_icon="📊", layout="wide")
st.title("📊 The Grand Comparison")
st.markdown(
    """
This runs the **exact same 24-message conversation** through all 8 memory techniques, back to
back, and lines up the results side by side. This is the slide that would normally take a whole
slide deck, except every number here is real and live, from your own Groq account.

⚠️ This makes well over 100 real API calls and can take a couple of minutes. Groq's free tier is
generous, but don't mash this button repeatedly.
"""
)

common.require_api_key()
model = common.get_model()

STRATEGY_BUILDERS = {
    "No Memory": lambda llm, embedder: NoMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT),
    "Buffer": lambda llm, embedder: BufferMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT),
    "Sliding Window": lambda llm, embedder: SlidingWindowStrategy(scenario.NOVA_SYSTEM_PROMPT, window_turns=3),
    "Summary": lambda llm, embedder: SummaryMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT, llm),
    "Summary Buffer": lambda llm, embedder: SummaryBufferStrategy(scenario.NOVA_SYSTEM_PROMPT, llm, max_token_limit=120),
    "Token Buffer": lambda llm, embedder: TokenBufferStrategy(scenario.NOVA_SYSTEM_PROMPT, llm, max_token_limit=150),
    "Vector Store": lambda llm, embedder: VectorStoreMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT, embedder, top_k=3),
    "Entity": lambda llm, embedder: EntityMemoryStrategy(scenario.NOVA_SYSTEM_PROMPT, llm),
}

if st.button("Run full comparison now", type="primary"):
    embedder = get_embedder()
    results = []
    total_steps = len(STRATEGY_BUILDERS) * len(scenario.SCRIPT)
    step = 0
    progress = st.progress(0.0, text="Starting...")

    for name, builder in STRATEGY_BUILDERS.items():
        tracker = UsageTracker()
        llm = ChatGroq(model=model, api_key=st.session_state["groq_api_key"], temperature=0.7, callbacks=[tracker])
        strategy = builder(llm, embedder)

        stats = {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        probes_passed = 0
        probes_total = 0

        for i, user_text in enumerate(scenario.SCRIPT):
            progress.progress(step / total_steps, text=f"Running {name}... turn {i + 1}/{len(scenario.SCRIPT)}")
            step += 1
            result = engine.run_turn(strategy, llm, tracker, model, user_text)
            stats["requests"] += result["turn_requests"]
            stats["input_tokens"] += result["turn_input_tokens"]
            stats["output_tokens"] += result["turn_output_tokens"]
            stats["cost"] += result["turn_cost"]

            fact = scenario.PROBE_TURNS.get(i)
            if fact is not None:
                probes_total += 1
                if scenario.check_probe(fact, result["reply"]):
                    probes_passed += 1

        results.append({
            "Technique": name,
            "API requests": stats["requests"],
            "Tokens in": stats["input_tokens"],
            "Tokens out": stats["output_tokens"],
            "Cost ($)": round(stats["cost"], 5),
            "Facts remembered": f"{probes_passed}/{probes_total}",
        })

    progress.progress(1.0, text="Done!")
    st.session_state["comparison_results"] = results

if "comparison_results" in st.session_state:
    df = pd.DataFrame(st.session_state["comparison_results"]).set_index("Technique")

    st.subheader("Results")
    st.dataframe(df, width="stretch")

    st.subheader("Total cost per technique")
    st.bar_chart(df["Cost ($)"])

    st.subheader("Total API requests per technique")
    st.bar_chart(df["API requests"])
