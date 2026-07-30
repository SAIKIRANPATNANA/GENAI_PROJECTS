"""
What Groq actually charges, per model, so the "cost" numbers on every page
are real dollars, not guesses. Prices are $ per 1 million tokens, pulled
from Groq's public pricing page. Groq changes prices sometimes - if a
number here looks off, double check at https://groq.com/pricing
"""

GROQ_PRICING = {
    "llama-3.1-8b-instant": {
        "input": 0.05,
        "output": 0.08,
        "label": "Llama 3.1 8B Instant - fastest & cheapest (recommended for this demo)",
    },
    "openai/gpt-oss-20b": {
        "input": 0.075,
        "output": 0.30,
        "label": "GPT-OSS 20B - very fast, slightly pricier",
    },
    "llama-3.3-70b-versatile": {
        "input": 0.59,
        "output": 0.79,
        "label": "Llama 3.3 70B Versatile - smarter, most expensive",
    },
}

DEFAULT_MODEL = "llama-3.1-8b-instant"


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    prices = GROQ_PRICING.get(model, GROQ_PRICING[DEFAULT_MODEL])
    return (input_tokens / 1_000_000) * prices["input"] + (output_tokens / 1_000_000) * prices["output"]
