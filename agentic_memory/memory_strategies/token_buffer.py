from langchain_classic.memory import ConversationTokenBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage


class TokenBufferStrategy:
    """
    Like a backpack with a strict weight limit, measured in tokens instead
    of number of turns. Once it's full, the oldest messages get tossed out
    to make room - no summarizing, no extra AI calls. The cheapest and
    most predictable of all these techniques: exactly 1 API call, every
    single turn, always.
    """

    def __init__(self, system_prompt: str, llm, max_token_limit: int = 150):
        self.system_prompt = system_prompt
        self.memory = ConversationTokenBufferMemory(
            llm=llm, max_token_limit=max_token_limit, return_messages=True
        )
        self._total_messages_added = 0

    def get_messages_for_reply(self, user_text: str):
        history = self.memory.load_memory_variables({})["history"]
        return [SystemMessage(content=self.system_prompt)] + history + [HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})
        self._total_messages_added += 2

    def set_max_token_limit(self, max_token_limit: int):
        """Widen or shrink the backpack live - takes effect on the very next turn."""
        self.memory.max_token_limit = max_token_limit

    def current_tokens(self) -> int:
        """
        How many tokens are sitting in the buffer right now, counted the
        exact same way ConversationTokenBufferMemory counts them internally
        before deciding whether to evict anything.
        """
        return self.memory.llm.get_num_tokens_from_messages(self.memory.chat_memory.messages)

    def dropped_count(self) -> int:
        """How many messages have been evicted so far (for display only)."""
        return max(0, self._total_messages_added - len(self.memory.chat_memory.messages))
