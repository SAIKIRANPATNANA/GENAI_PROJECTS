from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.messages import SystemMessage, HumanMessage


class SlidingWindowStrategy:
    """
    Like a small whiteboard that only has room for your last few exchanges.
    Older turns quietly fall off the edge to make room for new ones - gone
    from what Nova sees, even though you can still see them in the chat log.
    """

    def __init__(self, system_prompt: str, window_turns: int = 2):
        self.system_prompt = system_prompt
        self.window_turns = window_turns
        self.memory = ConversationBufferWindowMemory(k=window_turns, return_messages=True)

    def set_window_turns(self, window_turns: int):
        """
        Widen or shrink the window LIVE, mid-conversation. The full history
        is still sitting in self.memory.chat_memory - only how much of it
        gets shown to Nova changes. This is how the page can demonstrate
        "fixing" a forgotten fact without restarting the whole demo.
        """
        self.window_turns = window_turns
        self.memory.k = window_turns

    def get_messages_for_reply(self, user_text: str):
        history = self.memory.load_memory_variables({})["history"]
        return [SystemMessage(content=self.system_prompt)] + history + [HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})

    def dropped_count(self) -> int:
        """How many messages have fallen out of the window so far (for display only)."""
        full = len(self.memory.chat_memory.messages)
        windowed = len(self.memory.load_memory_variables({})["history"])
        return max(0, full - windowed)
