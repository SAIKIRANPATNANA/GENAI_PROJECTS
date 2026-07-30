"""
The shared turn-runner used by every memory technique. This is the one
piece of code that actually talks to Groq - every page just plugs in a
different "strategy" object and this function drives it the same way.
"""

import pricing


def run_turn(strategy, llm, tracker, model: str, user_text: str) -> dict:
    """
    Runs one full turn through a memory strategy:
      1. Ask the strategy what messages to send. This is where each memory
         technique's whole personality shows up - full history? a window?
         a summary? retrieved memories? a profile card?
      2. Send those messages to Groq and get Nova's reply.
      3. Let the strategy save this turn. Some strategies quietly make
         EXTRA calls here (summarizing, extracting facts) - the tracker
         attached to the LLM catches those automatically.
    """
    before = tracker.snapshot()

    messages = strategy.get_messages_for_reply(user_text)
    ai_message = llm.invoke(messages)
    reply_text = ai_message.content

    strategy.save(user_text, reply_text)

    after = tracker.snapshot()
    turn_requests = after["requests"] - before["requests"]
    turn_input_tokens = after["input_tokens"] - before["input_tokens"]
    turn_output_tokens = after["output_tokens"] - before["output_tokens"]
    turn_cost = pricing.estimate_cost(model, turn_input_tokens, turn_output_tokens)

    return {
        "reply": reply_text,
        "messages_sent": messages,
        "turn_requests": turn_requests,
        "turn_input_tokens": turn_input_tokens,
        "turn_output_tokens": turn_output_tokens,
        "turn_cost": turn_cost,
    }
