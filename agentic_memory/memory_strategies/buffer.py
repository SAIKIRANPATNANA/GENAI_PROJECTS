from langchain_classic.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage


class BufferMemoryStrategy:
    """
    Keeps EVERY message ever sent, word for word, and resends the entire
    transcript on every single turn. Perfect recall - but it never stops
    growing, so cost and size climb the longer the chat goes on.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.memory = ConversationBufferMemory(return_messages=True)

    def get_messages_for_reply(self, user_text: str):
        history = self.memory.load_memory_variables({})["history"]
        return [SystemMessage(content=self.system_prompt)] + history + [HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})
