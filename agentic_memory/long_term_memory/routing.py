"""
Memory Routing: don't query every memory store on every turn - classify
the message first, then talk to only the stores that are actually
relevant. The mental model from the notebook: an air traffic controller,
not a broadcast to every runway at once.

Hybrid classification, as the notebook recommends: fast, free keyword
rules catch the obvious cases; an LLM call only fires for messages that
don't match any rule.
"""

from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage


class Intent(Enum):
    FACT_QUERY = "FACT_QUERY"
    HISTORY_QUERY = "HISTORY_QUERY"
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    FACT_UPDATE = "FACT_UPDATE"
    CONSTRAINT_UPDATE = "CONSTRAINT_UPDATE"
    ADVICE_REQUEST = "ADVICE_REQUEST"
    EMOTIONAL_SIGNAL = "EMOTIONAL_SIGNAL"
    GENERAL_CHAT = "GENERAL_CHAT"


# Approximate tokens each store would inject if queried - used only for
# the token-savings comparison, not for real API calls.
STORE_TOKEN_COST = {
    "Entity Memory": 150,
    "Vector Store Memory": 200,
    "Episodic Memory": 250,
    "Semantic Memory": 200,
    "Procedural Memory": 150,
}

# Procedural rules should shape every response - they're always injected,
# regardless of what the router decides for everything else.
ALWAYS_INJECT = ["Procedural Memory"]

# intent -> (stores to READ from, stores to WRITE to)
ROUTING_TABLE = {
    Intent.FACT_QUERY: (["Entity Memory"], []),
    Intent.HISTORY_QUERY: (["Episodic Memory"], []),
    Intent.KNOWLEDGE_QUERY: (["Vector Store Memory"], []),
    Intent.FACT_UPDATE: (["Entity Memory"], ["Entity Memory"]),
    Intent.CONSTRAINT_UPDATE: ([], ["Procedural Memory"]),
    Intent.ADVICE_REQUEST: (["Procedural Memory", "Semantic Memory"], []),
    Intent.EMOTIONAL_SIGNAL: (["Semantic Memory"], []),
    Intent.GENERAL_CHAT: ([], []),
}

_KEYWORD_RULES = [
    (Intent.CONSTRAINT_UPDATE, ["never ", "always ", "from now on", "going forward", "don't ever"]),
    (Intent.FACT_UPDATE, ["i just ", "i changed", "i moved", "i switched", "my new "]),
    (Intent.HISTORY_QUERY, ["last time", "we discussed", "did we decide", "what happened", "previously", "last session"]),
    (Intent.EMOTIONAL_SIGNAL, ["stressed", "anxious", "worried", "frustrated", "nervous", "overwhelmed"]),
    (Intent.FACT_QUERY, ["what is my", "what's my", "do you know my", "what was my"]),
    (Intent.ADVICE_REQUEST, ["should i", "what do you recommend", "any advice", "what should i"]),
    (Intent.KNOWLEDGE_QUERY, ["how does", "what is", "explain", "how do "]),
]

CLASSIFY_SYSTEM_PROMPT = (
    "Classify the user's message into exactly ONE of these intents: FACT_QUERY, HISTORY_QUERY, "
    "KNOWLEDGE_QUERY, FACT_UPDATE, CONSTRAINT_UPDATE, ADVICE_REQUEST, EMOTIONAL_SIGNAL, "
    "GENERAL_CHAT. Reply with ONLY the intent name in capitals, nothing else."
)


def classify_rule_based(text: str) -> Intent | None:
    lowered = text.lower()
    for intent, keywords in _KEYWORD_RULES:
        if any(kw in lowered for kw in keywords):
            return intent
    return None


def classify_llm(llm, text: str) -> Intent:
    messages = [SystemMessage(content=CLASSIFY_SYSTEM_PROMPT), HumanMessage(content=text)]
    response = llm.invoke(messages)
    raw = response.content.strip().upper().replace(" ", "_")
    for intent in Intent:
        if intent.value in raw:
            return intent
    return Intent.GENERAL_CHAT


def route(llm, text: str) -> dict:
    """
    Classifies one message and returns the full routing decision, including
    a naive-vs-routed token comparison so the cost savings are concrete,
    not just asserted.
    """
    rule_intent = classify_rule_based(text)
    if rule_intent is not None:
        intent, method = rule_intent, "Rule-based (instant, free)"
    else:
        intent, method = classify_llm(llm, text), "LLM fallback (1 extra API call)"

    read_stores, write_stores = ROUTING_TABLE.get(intent, ([], []))
    read_stores = sorted(set(read_stores) | set(ALWAYS_INJECT))

    naive_tokens = sum(STORE_TOKEN_COST.values())
    routed_tokens = sum(STORE_TOKEN_COST.get(s, 0) for s in read_stores)
    savings_pct = round(100 * (1 - routed_tokens / naive_tokens), 1) if naive_tokens else 0.0

    return {
        "message": text,
        "intent": intent.value,
        "method": method,
        "read_stores": read_stores,
        "write_stores": write_stores,
        "naive_tokens": naive_tokens,
        "routed_tokens": routed_tokens,
        "savings_pct": savings_pct,
    }
