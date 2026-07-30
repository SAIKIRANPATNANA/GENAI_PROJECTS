"""
The shared two-session script used by the long-term memory pages
(Episodic, Semantic, Procedural, Self-Reflection).

Short-term memory techniques are tested WITHIN one conversation: does a
fact survive N more turns? Long-term memory techniques are tested ACROSS
conversations: Session 1 happens, ends, and gets distilled into something
small. Then Session 2 starts completely fresh - zero raw messages carried
over - and we check whether the DISTILLED thing is enough to answer
correctly. That's the entire point of long-term memory: you don't keep the
transcript, you keep what you learned from it.

Session 1 deliberately plants four different kinds of things to extract:
  - a plain fact ("Whiskers")
  - an emotional/situational signal (exam stress)
  - a decision (study plan)
  - a stated behavioural rule ("keep answers short") - and turn 3 is asked
    BEFORE that rule exists, so it's naturally verbose. That gives Session 2
    something real to contrast against later, no staging required.
"""

from long_term_memory.probes import ProbeType, Probe  # noqa: F401  (re-exported for convenience)

NOVA_SYSTEM_PROMPT = (
    "You are Nova, a warm and cheerful AI buddy chatting with a new friend. "
    "Reply naturally and helpfully."
)

SESSION_1 = [
    "Hi Nova! I'm Maya.",
    "I have a cat named Whiskers.",
    "Can you explain how compound interest works? I'd like a proper, detailed explanation.",
    "Honestly, I'm super stressed about my exams next week.",
    "I've decided I'm going to study 2 hours every night this week to prepare.",
    "By the way, going forward, please keep your answers short - a sentence or two max.",
    "What's a good way to stay focused while studying?",
    "Thanks Nova, that's it for today!",
]

SESSION_2 = [
    "Hey Nova, it's me again! What's been stressing me out lately?",
    "What did I decide to do about it?",
    "Can you explain how the stock market works?",
    "What's my cat's name again?",
]

# Index into SESSION_1 where the "keep answers short" rule was stated.
# Everything at or before this index happened WITHOUT the rule active.
RULE_STATED_AT = 5

# Index into SESSION_1 that is a good example of a verbose reply given
# BEFORE the user asked for short answers - useful evidence for
# self-reflection ("I gave a long answer when I later learned this user
# wants brevity").
VERBOSE_EXAMPLE_TURN = 2

SESSION_2_PROBES = [
    Probe(
        turn=0,
        kind=ProbeType.KEYWORD,
        keyword="exam",
        question="Does Nova recall what was stressing Maya out?",
    ),
    Probe(
        turn=1,
        kind=ProbeType.KEYWORD,
        keyword="stud",  # matches "study" / "studying"
        question="Does Nova recall the decision Maya made?",
    ),
    Probe(
        turn=2,
        kind=ProbeType.SHORT_REPLY,
        keyword=None,
        question="Is Nova's reply short now, honouring the rule Maya stated?",
        max_words=40,
    ),
    Probe(
        turn=3,
        kind=ProbeType.KEYWORD,
        keyword="whiskers",
        question="Does Nova recall Maya's cat's name?",
    ),
]
