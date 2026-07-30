from langchain_classic.memory import ConversationEntityMemory
from langchain_core.messages import SystemMessage, HumanMessage


class EntityMemoryStrategy:
    """
    Instead of remembering the whole conversation, Nova keeps a tiny
    profile card: just a few labeled facts about the people and things you
    mention (like a contact card). She automatically decides what counts
    as an "entity" worth tracking - watch the profile fill in as you go.

    Under the hood this is actually TWO separate hidden AI jobs, not one:
      1. Extraction - "which names/things were just mentioned?" (runs
         inside get_messages_for_reply, via entity_cache below)
      2. Summarization - "given what's already known about each of those
         names, and what was just said, what's the updated summary?"
         (runs once PER detected entity, inside save())
    """

    def __init__(self, system_prompt: str, llm):
        self.system_prompt = system_prompt
        self.memory = ConversationEntityMemory(llm=llm, return_messages=True)

    def get_messages_for_reply(self, user_text: str):
        variables = self.memory.load_memory_variables({"input": user_text})
        history = variables["history"]
        entities = variables.get("entities", {})
        system_content = self.system_prompt
        known = ", ".join(f"{name}: {summary}" for name, summary in entities.items() if summary)
        if known:
            system_content += f"\n\nWhat you know about the people/things mentioned: {known}"
        return [SystemMessage(content=system_content)] + history + [HumanMessage(content=user_text)]

    def save(self, user_text: str, reply_text: str):
        self.memory.save_context({"input": user_text}, {"output": reply_text})

    def known_entities(self) -> dict:
        """The full profile card built up so far: every entity ever detected."""
        return dict(self.memory.entity_store.store)

    def last_detected_entities(self) -> list[str]:
        """
        Whichever names/things the extraction step just noticed in the most
        recent turn - this is exactly what triggers the summarization calls
        in save(). Empty list means nothing new was detected this turn.
        """
        return list(self.memory.entity_cache)
