"""
A tiny "spy" that watches an LLM and counts every call it makes.

Why this matters: some memory techniques secretly make EXTRA calls behind
the scenes (like Summary Memory rewriting its recap every turn). If we only
counted the call we made on purpose, we'd miss that hidden cost completely.
Attaching this tracker directly to the LLM catches everything, including
calls made deep inside a memory class we didn't write ourselves.
"""

from langchain_core.callbacks import BaseCallbackHandler


class UsageTracker(BaseCallbackHandler):
    def __init__(self):
        self.requests = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response, **kwargs):
        self.requests += 1
        usage = None
        try:
            usage = response.generations[0][0].message.usage_metadata
        except (AttributeError, IndexError):
            usage = None
        if usage:
            self.input_tokens += usage.get("input_tokens", 0) or 0
            self.output_tokens += usage.get("output_tokens", 0) or 0

    def snapshot(self) -> dict:
        return {
            "requests": self.requests,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }
