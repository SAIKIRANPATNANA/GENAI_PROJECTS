"""Shared helper for the four extraction-based long-term techniques."""

import json
import re


def parse_json_response(text: str) -> dict:
    """
    LLMs often wrap JSON in markdown code fences or add stray text around
    it. This strips that noise and parses what's left. Falls back to a
    single-field dict if parsing still fails, so a bad response never
    crashes the demo mid-class.
    """
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"raw_text": text.strip(), "parse_error": True}
