from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage


class SummaryBufferStrategy:
    """
    The best-of-both compromise: keeps your last few messages word-for-word
    (sharp, recent detail), but folds anything OLDER into a short recap
    instead of throwing it away. Like keeping the latest page of your
    notebook open, with a summary of earlier pages stapled to the front.
    Extra recap-writing calls only happen occasionally, when the buffer
    overflows - not on every single turn like pure Summary Memory.
    """

    def __init__(self, system_prompt: str, llm, max_token_limit: int = 120):
        self.system_prompt = system_prompt
        self.memory = ConversationSummaryBufferMemory(
            llm=llm, max_token_limit=max_token_limit, return_messages=True
        )

    def get_messages_for_reply(self, user_text: str):
        history = self.memory.load_memory_variables({})["history"]
        return [SystemMessage(content=self.system_prompt)] + history + [HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})

    def summary_text(self) -> str:
        text = getattr(self.memory, "moving_summary_buffer", None) or getattr(self.memory, "buffer", None)
        return text or "(no recap yet - buffer hasn't overflowed)"
