"""
The shared driver behind every long-term memory page (Episodic, Semantic,
Procedural, Self-Reflection). Where common.py's run_strategy_page tests
"does this survive more turns in ONE conversation", this tests "does this
survive into a COMPLETELY FRESH conversation" - which is the actual
definition of long-term memory.

Session 1 is deliberately just Buffer Memory (Technique 2) - nothing
special happens turn by turn. The interesting part is the boundary: when
Session 1 closes, an extraction call runs, producing a small artifact.
Session 2 then starts with ZERO raw messages from Session 1 - only that
artifact, injected into the system prompt. If Session 2 still answers
correctly, the artifact - not the transcript - is doing the remembering.
"""

import streamlit as st

import common
import engine
import long_term_scenario as lts
import pricing
from components.context_inspector import render_context_inspector
from components.growth_chart import render_growth_chart
from components.metrics_bar import render_metrics_bar
from components.transformation_panel import render_transformation
from memory_strategies.buffer import BufferMemoryStrategy


def run_long_term_demo_page(
    *, page_key: str, extract_fn, artifact_panel_fn, build_session2_system_prompt_fn,
    probes=None, raw_panel_fn=None,
):
    """
    extract_fn(llm, session1_transcript) -> artifact
        session1_transcript is a list of (role, text) tuples. Runs the
        technique's extraction call(s) once, when Session 1 closes.

    artifact_panel_fn(artifact) -> (title, content)
        content is a dict (shown as JSON) or a string, for the
        transformation panel.

    build_session2_system_prompt_fn(base_prompt, artifact) -> str
        Builds the system prompt Session 2 uses. This - not the Session 1
        transcript - is the only thing Session 2 has to go on.

    probes: optional list[long_term_memory.probes.Probe], graded against
        Session 2 replies by turn index.

    raw_panel_fn: optional (session1_transcript, artifact) -> (title, list[str])
        overrides what the LEFT side of the transformation panel shows.
        Most techniques distill directly from the Session 1 transcript, so
        the default (just show the transcript) is right. Semantic Memory
        is the exception - it distills from episode SUMMARIES, not raw
        messages - so it supplies its own raw_panel_fn.

    Returns (artifact, session2_results) so the page can render extra,
    technique-specific visuals underneath.
    """
    common.require_api_key()
    model = common.get_model()
    llm, tracker = common.get_llm_and_tracker(page_key)
    probes_by_turn = {p.turn: p for p in (probes or [])}

    def k(name: str) -> str:
        return f"{page_key}_{name}"

    st.session_state.setdefault(k("s1_strategy"), BufferMemoryStrategy(lts.NOVA_SYSTEM_PROMPT))
    st.session_state.setdefault(k("s1_transcript"), [])
    st.session_state.setdefault(k("s1_turn"), 0)
    st.session_state.setdefault(k("closed"), False)
    st.session_state.setdefault(k("artifact"), None)
    st.session_state.setdefault(k("s2_strategy"), None)
    st.session_state.setdefault(k("s2_transcript"), [])
    st.session_state.setdefault(k("s2_turn"), 0)
    st.session_state.setdefault(k("s2_results"), [])
    st.session_state.setdefault(k("stats"), {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0})
    st.session_state.setdefault(k("history"), [])
    st.session_state.setdefault(k("step"), 0)
    st.session_state.setdefault(k("last_messages"), [])

    if st.button("Reset this demo", key=k("reset")):
        for name in (
            "s1_strategy", "s1_transcript", "s1_turn", "closed", "artifact", "s2_strategy",
            "s2_transcript", "s2_turn", "s2_results", "stats", "history", "step", "last_messages",
        ):
            st.session_state.pop(k(name), None)
        st.rerun()

    def _record(result: dict):
        stats = st.session_state[k("stats")]
        stats["requests"] += result["turn_requests"]
        stats["input_tokens"] += result["turn_input_tokens"]
        stats["output_tokens"] += result["turn_output_tokens"]
        stats["cost"] += result["turn_cost"]
        st.session_state[k("step")] += 1
        st.session_state[k("history")].append({
            "turn": st.session_state[k("step")],
            "input_tokens": stats["input_tokens"],
            "output_tokens": stats["output_tokens"],
            "cost": stats["cost"],
        })
        st.session_state[k("last_messages")] = result["messages_sent"]

    # ---------------- SESSION 1 ----------------
    st.header("Session 1 (today)")
    st.caption("A normal conversation happens - this is plain Buffer Memory, same mechanics as Technique 2.")

    s1_turn = st.session_state[k("s1_turn")]
    s1_done = s1_turn >= len(lts.SESSION_1)

    if not st.session_state[k("closed")]:
        if not s1_done:
            if st.button(f'Next turn -> "{lts.SESSION_1[s1_turn]}"', key=k("s1_next"), type="primary"):
                user_text = lts.SESSION_1[s1_turn]
                with st.spinner("Nova is thinking..."):
                    result = engine.run_turn(st.session_state[k("s1_strategy")], llm, tracker, model, user_text)
                _record(result)
                st.session_state[k("s1_transcript")].append(("user", user_text))
                st.session_state[k("s1_transcript")].append(("assistant", result["reply"]))
                st.session_state[k("s1_turn")] += 1
                st.rerun()
        else:
            st.success("Session 1 finished.")
            if st.button("Close Session 1 & Extract", key=k("close"), type="primary"):
                with st.spinner("Running the extraction call(s)..."):
                    before = tracker.snapshot()
                    artifact = extract_fn(llm, st.session_state[k("s1_transcript")])
                    after = tracker.snapshot()
                stats = st.session_state[k("stats")]
                extra_in = after["input_tokens"] - before["input_tokens"]
                extra_out = after["output_tokens"] - before["output_tokens"]
                stats["requests"] += after["requests"] - before["requests"]
                stats["input_tokens"] += extra_in
                stats["output_tokens"] += extra_out
                stats["cost"] += pricing.estimate_cost(model, extra_in, extra_out)

                st.session_state[k("artifact")] = artifact
                st.session_state[k("closed")] = True
                session2_prompt = build_session2_system_prompt_fn(lts.NOVA_SYSTEM_PROMPT, artifact)
                st.session_state[k("s2_strategy")] = BufferMemoryStrategy(session2_prompt)
                st.rerun()

    for role, content in st.session_state[k("s1_transcript")]:
        with st.chat_message(role):
            st.write(content)

    if not st.session_state[k("closed")]:
        return None, None

    # ---------------- TRANSFORMATION ----------------
    st.divider()
    artifact = st.session_state[k("artifact")]
    title, content = artifact_panel_fn(artifact)
    if raw_panel_fn is not None:
        raw_title, raw_items = raw_panel_fn(st.session_state[k("s1_transcript")], artifact)
    else:
        raw_title = "Session 1 - raw transcript"
        raw_items = [f"{role}: {text}" for role, text in st.session_state[k("s1_transcript")]]
    render_transformation(
        raw_title=raw_title,
        raw_items=raw_items,
        artifact_title=title,
        artifact=content,
    )

    # ---------------- SESSION 2 ----------------
    st.divider()
    st.header("Session 2 (later - a fresh conversation)")
    st.caption(
        "Nova has ZERO raw messages from Session 1 now. Everything she \"remembers\" has to come "
        "from the artifact above, injected into her system prompt."
    )

    s2_turn = st.session_state[k("s2_turn")]
    s2_done = s2_turn >= len(lts.SESSION_2)

    if not s2_done:
        probe = probes_by_turn.get(s2_turn)
        if probe:
            st.info(f"🧪 **Memory test coming up** - {probe.question}")
        if st.button(f'Next turn -> "{lts.SESSION_2[s2_turn]}"', key=k("s2_next"), type="primary"):
            user_text = lts.SESSION_2[s2_turn]
            with st.spinner("Nova is thinking..."):
                result = engine.run_turn(st.session_state[k("s2_strategy")], llm, tracker, model, user_text)
            _record(result)
            st.session_state[k("s2_transcript")].append(("user", user_text))
            st.session_state[k("s2_transcript")].append(("assistant", result["reply"]))
            if probe:
                passed = probe.check(result["reply"])
                st.session_state[k("s2_results")].append(
                    {"question": probe.question, "passed": passed, "reply": result["reply"]}
                )
            st.session_state[k("s2_turn")] += 1
            st.rerun()

    for role, content in st.session_state[k("s2_transcript")]:
        with st.chat_message(role):
            st.write(content)

    for r in st.session_state[k("s2_results")]:
        if r["passed"]:
            st.success(f"Passed: {r['question']}")
        else:
            st.error(f"Failed: {r['question']}")

    st.divider()
    stats = st.session_state[k("stats")]
    st.subheader("Live cost meter (Session 1 + extraction + Session 2, combined)")
    render_metrics_bar(stats["requests"], stats["input_tokens"], stats["output_tokens"], stats["cost"])
    render_growth_chart(st.session_state[k("history")])
    render_context_inspector(
        st.session_state[k("last_messages")], title="See exactly what Nova reads for the last reply"
    )

    return artifact, st.session_state[k("s2_results")]
