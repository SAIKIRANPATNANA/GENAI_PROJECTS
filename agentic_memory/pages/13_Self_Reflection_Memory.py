import streamlit as st

import common_ltm
import long_term_scenario as lts
from components.verdict import render_verdict
from long_term_memory import self_reflection

st.set_page_config(page_title="Self-Reflection Memory", page_icon="🪞", layout="wide")
st.title("🪞 Long-Term Technique 4: Self-Reflection Memory")
st.markdown(
    """
**The idea:** After a session, the agent critiques its OWN performance - not facts about the
user, not rules to follow, but "did I mess up, and what should I learn from it." Nova checks
whether *she* honoured the "keep answers short" request Maya made partway through Session 1.

**The safety rule this page actually enforces:** a self-critique with no quoted evidence from
the transcript is discarded automatically - in code, not just by asking nicely in the prompt.
This is the #1 failure mode from the research: agents hallucinating mistakes they never made.
"""
)

st.info(
    "👤 **Human parallel:** this is the voice in your head on the walk home after an awkward "
    "conversation - \"did I say the wrong thing there?\" - or after a presentation - \"I should "
    "have explained that slide better.\" You're not just remembering what happened, you're "
    "judging your OWN performance against how you meant to come across, and filing away a note "
    "for next time. Nova does the same thing here, one level removed - and just like you'd "
    "distrust a friend who invents fake mistakes to seem humble, Nova's self-critique only counts "
    "if she can point to the actual moment it happened."
)

probes = [p for p in lts.SESSION_2_PROBES if p.turn == 2]

artifact, results = common_ltm.run_long_term_demo_page(
    page_key="self_reflection",
    extract_fn=self_reflection.extract,
    artifact_panel_fn=self_reflection.artifact_panel,
    build_session2_system_prompt_fn=self_reflection.build_session2_system_prompt,
    probes=probes,
)

if artifact is not None:
    st.divider()
    st.subheader("Compliance audit view")
    if artifact.get("violation_found"):
        st.error("Violation found and evidence-backed - this note carries into Session 2.")
        st.write(f"**Evidence:** \"{artifact.get('evidence_quote', '')}\"")
        st.write(f"**Lesson:** {artifact.get('lesson', '')}")
    elif artifact.get("discarded_reason"):
        st.warning(f"A violation was claimed but discarded: {artifact['discarded_reason']}")
    else:
        st.success("No compliance issue found - nothing gets injected into Session 2.")

render_verdict(
    best="Catches the agent's own mistakes and fixes them without any retraining.",
    worst="Risk of hallucinated self-critique - the evidence rule above exists specifically to guard against this.",
    example="It notices it gave a long answer right after being asked for short ones, and self-corrects next time.",
)
