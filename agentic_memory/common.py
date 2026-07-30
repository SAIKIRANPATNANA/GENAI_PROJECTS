"""
Shared plumbing used by every memory-technique page: checking for the API
key, building a per-page LLM + usage tracker, and the full "run this demo"
UI loop (chat log, Next turn button, live cost meter, growth chart, context
inspector). Keeping this in one place means every technique is shown with
the exact same UI, so the only thing that changes page to page is the
memory strategy itself.
"""

import warnings

import streamlit as st
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_groq import ChatGroq

import engine
import pricing
import scenario
from components.context_inspector import render_context_inspector
from components.growth_chart import render_growth_chart
from components.metrics_bar import render_metrics_bar
from embeddings import get_embedder
from tracking import UsageTracker

# This app deliberately uses langchain_classic's "named" memory classes
# (ConversationBufferMemory, ConversationSummaryMemory, ...) because their
# class names map 1:1 onto the concepts being taught - see README for the
# full rationale. LangChain warns on every use, steering production code
# toward LangGraph checkpointers instead. That warning is expected here,
# not a bug, so it's silenced rather than acted on - only this specific
# warning class, so other deprecation warnings still surface normally.
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)


def require_api_key():
    """Every page calls this first. If there's no key yet, stop and say so."""
    if not st.session_state.get("groq_api_key"):
        st.warning("Enter your Groq API key on the **Home** page first (see the sidebar there).")
        st.stop()


def get_model() -> str:
    return st.session_state.get("groq_model", pricing.DEFAULT_MODEL)


def get_llm_and_tracker(page_key: str):
    """
    Every page gets its own ChatGroq instance + UsageTracker, cached in
    st.session_state (not st.cache_resource) on purpose: this app is meant
    to be deployed once on Streamlit Community Cloud and used by a whole
    class of students at the same time. st.cache_resource objects are
    shared by EVERY visitor to the app - caching a Groq client there would
    mean one student's API key and running cost total could leak into
    another student's browser tab. st.session_state is private per browser
    session, which is what we actually want here.

    Storing it in session_state (instead of rebuilding it on every button
    click) is still a form of caching - it just needs to be the per-user
    kind. Recreated automatically if the model is changed on the Home page.
    """
    model = get_model()
    model_cache_key = f"{page_key}_llm_model"
    llm_key = f"{page_key}_llm"
    tracker_key = f"{page_key}_tracker"

    if st.session_state.get(model_cache_key) != model or llm_key not in st.session_state:
        tracker = UsageTracker()
        llm = ChatGroq(
            model=model,
            api_key=st.session_state["groq_api_key"],
            temperature=0.7,
            callbacks=[tracker],
        )
        st.session_state[llm_key] = llm
        st.session_state[tracker_key] = tracker
        st.session_state[model_cache_key] = model

    return st.session_state[llm_key], st.session_state[tracker_key]


def run_strategy_page(*, page_key: str, make_strategy, extra_controls=None):
    """
    The shared engine behind every memory-technique page.

    make_strategy: a function (llm, embedder) -> strategy object. Called
    once per session (or after Reset) to build a fresh strategy.

    extra_controls: an optional function (strategy) -> None, called right
    after the strategy exists but before the Next-turn button. Use this
    for page-specific live controls, like the Sliding Window page's window
    size slider, that need to be visible before the student decides what
    to click next.

    Returns (strategy, last_result) so the calling page can render extra,
    technique-specific visuals (like a growing summary or a profile card)
    underneath the shared UI this function already draws.
    """
    require_api_key()
    model = get_model()
    llm, tracker = get_llm_and_tracker(page_key)
    embedder = get_embedder()

    strategy_key = f"{page_key}_strategy"
    transcript_key = f"{page_key}_transcript"
    history_key = f"{page_key}_history"
    turn_key = f"{page_key}_turn_index"
    step_key = f"{page_key}_step"
    stats_key = f"{page_key}_stats"
    last_key = f"{page_key}_last_result"

    if strategy_key not in st.session_state:
        st.session_state[strategy_key] = make_strategy(llm, embedder)
    strategy = st.session_state[strategy_key]

    st.session_state.setdefault(transcript_key, [])
    st.session_state.setdefault(history_key, [])
    st.session_state.setdefault(turn_key, 0)
    st.session_state.setdefault(step_key, 0)
    st.session_state.setdefault(stats_key, {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0})
    st.session_state.setdefault(last_key, None)

    if extra_controls is not None:
        extra_controls(strategy)
        st.divider()

    def _record_turn(user_text: str, result: dict, probe_fact=None):
        """Shared bookkeeping for both scripted turns and free-form questions."""
        stats = st.session_state[stats_key]
        stats["requests"] += result["turn_requests"]
        stats["input_tokens"] += result["turn_input_tokens"]
        stats["output_tokens"] += result["turn_output_tokens"]
        stats["cost"] += result["turn_cost"]

        st.session_state[transcript_key].append(("user", user_text))
        st.session_state[transcript_key].append(("assistant", result["reply"]))

        st.session_state[step_key] += 1
        st.session_state[history_key].append({
            "turn": st.session_state[step_key],
            "input_tokens": stats["input_tokens"],
            "output_tokens": stats["output_tokens"],
            "cost": stats["cost"],
            "requests": stats["requests"],
        })

        passed = scenario.check_probe(probe_fact, result["reply"]) if probe_fact else None
        st.session_state[last_key] = {**result, "probe_fact": probe_fact, "passed": passed}

    turn_index = st.session_state[turn_key]
    script_done = turn_index >= len(scenario.SCRIPT)
    upcoming_probe = None if script_done else scenario.PROBE_TURNS.get(turn_index)

    if upcoming_probe is not None:
        distance = scenario.probe_distance(turn_index)
        plural = "s" if distance != 1 else ""
        st.info(
            f"🧪 **Memory test coming up** - this question checks whether Nova still "
            f"remembers something said **{distance} turn{plural} ago**."
        )

    col_a, col_b = st.columns([3, 1])
    with col_a:
        if script_done:
            next_label = "Script finished - all turns played"
        elif upcoming_probe is not None:
            next_label = f'🧪 Ask the test question -> "{scenario.SCRIPT[turn_index]}"'
        else:
            next_label = f'Next turn -> "{scenario.SCRIPT[turn_index]}"'
        go = st.button(next_label, disabled=script_done, key=f"{page_key}_next", type="primary")
    with col_b:
        reset = st.button("Reset this demo", key=f"{page_key}_reset")

    if reset:
        for key in (strategy_key, transcript_key, history_key, turn_key, step_key, stats_key, last_key):
            st.session_state.pop(key, None)
        st.rerun()

    if go and not script_done:
        user_text = scenario.SCRIPT[turn_index]
        with st.spinner("Nova is thinking..."):
            result = engine.run_turn(strategy, llm, tracker, model, user_text)
        _record_turn(user_text, result, probe_fact=upcoming_probe)
        st.session_state[turn_key] += 1
        st.rerun()

    last = st.session_state[last_key]
    if last and last["probe_fact"] is not None:
        question = scenario.probe_question_text(last["probe_fact"])
        if last["passed"]:
            st.success(f"Nova remembered! (\"{question}\")")
        else:
            st.error(f"Nova forgot! (\"{question}\")")

    st.divider()
    st.subheader("Ask Nova something extra")
    st.caption(
        "This doesn't advance the scripted conversation above - use it to test any question "
        "on demand, e.g. re-asking something that just failed after you change a setting."
    )
    free_col1, free_col2 = st.columns([4, 1])
    with free_col1:
        free_text = st.text_input(
            "Your question", key=f"{page_key}_free_text",
            label_visibility="collapsed", placeholder='e.g. "What\'s my cat\'s name?"',
        )
    with free_col2:
        ask = st.button("Ask", key=f"{page_key}_free_ask")

    if ask and free_text.strip():
        with st.spinner("Nova is thinking..."):
            result = engine.run_turn(strategy, llm, tracker, model, free_text.strip())
        _record_turn(free_text.strip(), result, probe_fact=None)
        st.rerun()

    st.divider()
    st.subheader("Conversation so far")
    if not st.session_state[transcript_key]:
        st.caption("No messages yet - click **Next turn** above to start the conversation.")
    for role, content in st.session_state[transcript_key]:
        with st.chat_message(role):
            st.write(content)

    st.divider()
    stats = st.session_state[stats_key]
    st.subheader("Live cost meter")
    render_metrics_bar(stats["requests"], stats["input_tokens"], stats["output_tokens"], stats["cost"])
    render_growth_chart(st.session_state[history_key])

    if last:
        render_context_inspector(last["messages_sent"])
        if last["turn_requests"] > 1:
            st.info(
                f"This turn made **{last['turn_requests']} API calls**, not just 1 - "
                "this technique did some extra work behind the scenes."
            )

    return strategy, last
