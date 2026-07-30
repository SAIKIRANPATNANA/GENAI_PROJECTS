import streamlit as st

import common_ltm
import long_term_scenario as lts
from components.verdict import render_verdict
from long_term_memory import procedural

st.set_page_config(page_title="Procedural Memory", page_icon="📐", layout="wide")
st.title("📐 Long-Term Technique 3: Procedural Memory")
st.markdown(
    """
**The idea:** Don't remember facts ABOUT the user - remember RULES for how to BEHAVE with them.
In Session 1, turn 6, Maya asks Nova to "keep answers short". Watch turn 3 (asked BEFORE that
rule existed) come back long and detailed - then watch the equivalent question in Session 2
come back short, because the rule is now a standing instruction in the system prompt.
"""
)

st.info(
    "👤 **Human parallel:** you do this automatically with everyone you know well. Once you learn "
    "a friend takes their tea with no sugar, you just... stop offering sugar. You never re-ask, "
    "and you never consciously think \"I am now applying the no-sugar rule\" - it's baked into how "
    "you behave around them. You've turned one remembered fact into a standing habit. That's "
    "procedural memory: not \"I know a fact about you\", but \"I now act differently because of it\"."
)

probes = [p for p in lts.SESSION_2_PROBES if p.turn == 2]  # only the short-reply rule-compliance probe

artifact, results = common_ltm.run_long_term_demo_page(
    page_key="procedural",
    extract_fn=procedural.extract,
    artifact_panel_fn=procedural.artifact_panel,
    build_session2_system_prompt_fn=procedural.build_session2_system_prompt,
    probes=probes,
)

if artifact is not None:
    st.divider()
    st.subheader("Did the rule actually reach Session 2?")
    st.caption(
        "The most common silent failure here isn't a bug - it's a confidence score that landed "
        "below the 0.4 injection threshold, so the rule was extracted but never applied. Or the "
        "rule was applied and the model just didn't fully comply - smaller, faster models follow "
        "in-context instructions less reliably than bigger ones. Both are worth seeing explicitly:"
    )
    status_rows = procedural.rule_status(artifact)
    if not status_rows:
        st.warning("No rule was extracted from Session 1 at all - nothing to check.")
    else:
        for row in status_rows:
            label = "Applied to Session 2" if row["applied"] else "NOT applied (confidence too low)"
            icon = "✅" if row["applied"] else "❌"
            st.write(f"{icon} *{row['rule']}* - confidence **{row['confidence']:.2f}** - {label}")
    if results and any(not r["passed"] for r in results):
        st.warning(
            "If the rule shows as applied above but Session 2's reply still came back long, that's "
            "not a bug in this app - it's a real, honest limitation: prompt-based rules shape "
            "behaviour probabilistically, they don't guarantee it the way code-level limits (like "
            "Token Buffer's hard eviction) do. Try switching to a bigger model (Llama 3.3 70B) in "
            "the Home page sidebar and re-running - compliance usually improves with model size."
        )

if artifact and artifact.get("rules"):
    st.divider()
    st.subheader("Outcome feedback - the self-improvement loop")
    st.caption(
        "In production, a rule that keeps working gets reinforced; a rule that backfires gets "
        "weakened and eventually stops being injected. Try it:"
    )
    rule = artifact["rules"][0]
    fb_key = "procedural_feedback_confidence"
    if fb_key not in st.session_state:
        st.session_state[fb_key] = float(rule.get("confidence", 0.5))

    st.write(f"Rule: *{rule.get('rule', '')}*")
    st.progress(st.session_state[fb_key], text=f"Confidence: {st.session_state[fb_key]:.2f}")

    c1, c2 = st.columns(2)
    if c1.button("It worked - reinforce it", key="procedural_reinforce"):
        st.session_state[fb_key] = min(1.0, st.session_state[fb_key] + 0.15)
        st.rerun()
    if c2.button("It didn't help - weaken it", key="procedural_weaken"):
        st.session_state[fb_key] = max(0.0, st.session_state[fb_key] - 0.15)
        st.rerun()

    if st.session_state[fb_key] < 0.4:
        st.warning("Confidence has dropped below the injection threshold (0.4) - this rule would stop being applied.")

render_verdict(
    best="Shapes HOW the agent behaves, not just what it knows - personalises style, not just facts.",
    worst="A bad rule that gets reinforced by mistake causes the same wrong behaviour every time.",
    example="Tell it once to keep answers short, and every future answer is short - no re-asking required.",
)
