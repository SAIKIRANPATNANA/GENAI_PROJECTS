import streamlit as st

import pricing

st.set_page_config(page_title="AI Memory Lab", page_icon="🧠", layout="wide")

st.title("🧠 AI Memory Lab")
st.markdown(
    """
Welcome! This is a hands-on playground for one big question:

> **When a chatbot "remembers" something you said earlier, how does that actually work,
> and what does it cost?**

Every page in the sidebar is a different way of giving a chatbot a memory. They all chat with
the same character, **Nova**, and they all go through the same scripted conversation, so you
can compare them fairly.

### The trick we use to test "memory"
Early in the conversation, we tell Nova a few facts about ourselves: our name, our pet's name,
our favorite food, and a dream trip. Then we bury those facts under a pile of unrelated small
talk. Near the end, we ask Nova about those facts again.

- If she remembers, the memory technique worked.
- If she's forgotten, we just watched a memory technique fail, live.

At the same time, every page shows a **live cost meter**: how many API requests were made, how
many tokens were sent and received, and how much real money it cost, using Groq's actual
pricing. Some techniques are cheap but forgetful. Some remember everything but get expensive.
That trade-off *is* the lesson.
"""
)

st.divider()

with st.sidebar:
    st.header("Your Groq API key")
    st.caption(
        "Get a free key at console.groq.com/keys. It's only kept in this browser "
        "session's memory, never written to disk."
    )
    api_key = st.text_input(
        "Groq API key", type="password", value=st.session_state.get("groq_api_key", "")
    )
    if api_key:
        st.session_state["groq_api_key"] = api_key

    st.header("Choose a model")
    model_names = list(pricing.GROQ_PRICING.keys())
    labels = [pricing.GROQ_PRICING[m]["label"] for m in model_names]
    default_index = model_names.index(pricing.DEFAULT_MODEL)
    choice = st.selectbox(
        "Groq model",
        options=range(len(model_names)),
        format_func=lambda i: labels[i],
        index=default_index,
    )
    st.session_state["groq_model"] = model_names[choice]

    if st.session_state.get("groq_api_key"):
        st.success("Key saved for this session. Pick a page below!")
    else:
        st.warning("Paste your Groq API key above to unlock the demo pages.")

st.subheader("Part 1 - Short-term memory (within one conversation)")
st.markdown(
    """
1. **No Memory** - the baseline. Nothing is remembered at all.
2. **Buffer Memory** - remembers everything, cost grows forever.
3. **Sliding Window Memory** - keeps only the last few turns.
4. **Summary Memory** - keeps one running recap, rewritten every turn.
5. **Summary Buffer Memory** - recent turns exact, older turns summarized.
6. **Token Buffer Memory** - a strict token "backpack", no extra AI calls.
7. **Vector Store Memory** - searches for the most *relevant* memories, not just the most recent.
8. **Entity Memory** - keeps a tiny profile card of facts about you.
9. **Comparison** - runs all of them side by side and shows one big scoreboard.

These all answer: *does a fact survive more turns in the SAME conversation?* Open them in order -
each one fixes a problem the previous one had, and creates a new trade-off of its own.
"""
)

st.divider()
st.subheader("Part 2 - Long-term memory (across separate conversations)")
st.markdown(
    """
Short-term memory answers "does it survive more turns today?" Long-term memory answers a
different question: **when today's conversation ends and a brand new one starts days later,
what - if anything - carries over?** Every page below runs the SAME two-session experiment:
a Session 1 happens, gets compressed into something small at "Close Session 1 & Extract", and
then a completely fresh Session 2 starts with **zero raw messages** - only that small artifact.
You watch the raw transcript get converted into structured memory, live, on every page.

10. **Episodic Memory** - one session becomes one timestamped "diary entry".
11. **Semantic Memory** - many sessions get distilled into a few general, reusable facts.
12. **Procedural Memory** - a stated preference becomes a standing behavioural rule.
13. **Self-Reflection Memory** - the agent critiques its own performance and learns from it.
14. **Memory Routing** - classifies each message and queries only the relevant store(s).

Techniques 10-13 need Techniques 1-9's building blocks conceptually but don't require visiting
them first. Routing is an interactive, no-conversation demo - jump to it any time.
"""
)
