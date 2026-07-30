from langchain_classic.memory import ConversationSummaryMemory
from langchain_core.messages import SystemMessage, HumanMessage


class SummaryMemoryStrategy:
    """
    Instead of remembering word-for-word, Nova keeps ONE running recap of
    the whole conversation - like a friend who takes notes in a meeting
    and gives you the highlights instead of replaying the whole recording.
    The catch: rewriting that recap takes a SECOND, hidden AI call, on
    every single turn.
    """

    def __init__(self, system_prompt: str, llm):
        self.system_prompt = system_prompt
        self.memory = ConversationSummaryMemory(llm=llm, return_messages=False)

    def get_messages_for_reply(self, user_text: str):
        summary = self.memory.load_memory_variables({})["history"]
        system_content = self.system_prompt
        if summary:
            system_content += f"\n\nHere is a recap of the conversation so far:\n{summary}"
        return [SystemMessage(content=system_content), HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})

    def summary_text(self) -> str:
        text = getattr(self.memory, "buffer", None)
        return text or "(no recap yet)"
