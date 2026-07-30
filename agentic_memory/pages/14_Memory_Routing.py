import pandas as pd
import streamlit as st

import common
from components.verdict import render_verdict
from long_term_memory import routing

st.set_page_config(page_title="Memory Routing", page_icon="🚦", layout="wide")
st.title("🚦 Long-Term Technique 5: Memory Routing")
st.markdown(
    """
**The idea:** With five memory stores built (Entity, Vector, Episodic, Semantic, Procedural),
querying ALL of them on every single turn is wasteful and noisy. A router looks at what you
just said, decides which store(s) actually matter, and only talks to those - like an air
traffic controller sending each plane to one runway, not all of them.

Type any message below (or click a preset) and watch it get classified and routed live.
"""
)

st.info(
    "👤 **Human parallel:** you do this instantly and unconsciously, every conversation. If a "
    "friend asks \"what's your phone number\", you don't rummage through your whole life story - "
    "you go straight to the one fact. If they ask \"remind me what we talked about last time\", "
    "you switch to a completely different kind of memory search - not facts, but a specific past "
    "moment. You never consciously think \"which part of my brain should I check\" - you just "
    "route the question correctly, every time, without noticing you're doing it. This page makes "
    "that invisible routing step visible."
)

common.require_api_key()
model = common.get_model()
llm, tracker = common.get_llm_and_tracker("routing")

PRESETS = [
    "What is my current salary?",
    "What did we decide last time about my exams?",
    "How does compound interest work?",
    "I just adopted a new puppy!",
    "Please always keep your answers short from now on.",
    "I'm really anxious about my exam results.",
    "lol what a nice day",
]

st.session_state.setdefault("routing_log", [])

st.subheader("Try a message")
preset_choice = st.selectbox("Pick a preset (or type your own below)", ["(type my own)"] + PRESETS)
default_text = "" if preset_choice == "(type my own)" else preset_choice
text = st.text_input("Message to route", value=default_text, key="routing_text_input")

if st.button("Route this message", type="primary", disabled=not text.strip()):
    before = tracker.snapshot()
    with st.spinner("Classifying..."):
        result = routing.route(llm, text.strip())
    after = tracker.snapshot()
    result["extra_calls"] = after["requests"] - before["requests"]
    st.session_state["routing_log"].append(result)
    st.rerun()

if st.session_state["routing_log"]:
    last = st.session_state["routing_log"][-1]
    st.divider()
    st.subheader("Routing decision")
    st.write(f"**Message:** {last['message']}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Classified intent", last["intent"])
    c2.metric("Classification method", "Rule-based" if "Rule" in last["method"] else "LLM fallback")
    c3.metric("Extra API calls used", last["extra_calls"])
    st.caption(last["method"])

    st.write(f"**Stores read:** {', '.join(last['read_stores']) or '(none)'}")
    if last["write_stores"]:
        st.write(f"**Stores written:** {', '.join(last['write_stores'])}")

    st.subheader("Token cost: routed vs querying everything")
    cost_df = pd.DataFrame({
        "Approach": ["Query every store", "Routed (this message)"],
        "Tokens injected": [last["naive_tokens"], last["routed_tokens"]],
    }).set_index("Approach")
    st.bar_chart(cost_df)
    st.success(f"Routing saved {last['savings_pct']}% of the tokens this turn would have cost otherwise.")

    st.divider()
    st.subheader("Everything routed so far this session")
    log_df = pd.DataFrame([
        {
            "Message": r["message"],
            "Intent": r["intent"],
            "Method": "Rule" if "Rule" in r["method"] else "LLM",
            "Stores read": ", ".join(r["read_stores"]),
            "Savings": f"{r['savings_pct']}%",
        }
        for r in st.session_state["routing_log"]
    ])
    st.dataframe(log_df, width="stretch", hide_index=True)

    if st.button("Clear log"):
        st.session_state["routing_log"] = []
        st.rerun()
else:
    st.info("Route a message above to see the decision.")

render_verdict(
    best="Big token savings at scale - only pay for the stores that actually matter to this message.",
    worst="A misclassified message silently queries the wrong store - and you might not notice.",
    example="'How does a SIP work?' skips Entity and Episodic stores entirely - only Vector Store gets queried.",
)
