from langchain_core.messages import SystemMessage, HumanMessage


class NoMemoryStrategy:
    """
    The baseline. Nova is handed ONLY the system prompt and your latest
    message - nothing you said before this turn exists to her. Like
    talking to someone with total amnesia after every single sentence.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def get_messages_for_reply(self, user_text: str):
        return [SystemMessage(content=self.system_prompt), HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        pass  # there is nothing to save - that's the whole point
