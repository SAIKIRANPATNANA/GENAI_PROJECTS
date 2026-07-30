"""
A tiny shared vocabulary for grading Session 2 replies in the long-term
memory demos. Two grading styles are enough for everything we test:

  KEYWORD     - did a specific word show up in the reply? (fact recall)
  SHORT_REPLY - is the reply short? (behavioural rule compliance)
"""

from dataclasses import dataclass
from enum import Enum


class ProbeType(Enum):
    KEYWORD = "keyword"
    SHORT_REPLY = "short_reply"


@dataclass
class Probe:
    turn: int
    kind: ProbeType
    keyword: str | None
    question: str
    max_words: int = 40

    def check(self, reply_text: str) -> bool:
        if self.kind is ProbeType.KEYWORD:
            return self.keyword in reply_text.lower()
        if self.kind is ProbeType.SHORT_REPLY:
            return len(reply_text.split()) <= self.max_words
        raise ValueError(f"Unknown probe kind: {self.kind}")
