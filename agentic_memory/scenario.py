"""
The SAME fake conversation is replayed on every memory-technique page, so
comparing techniques is a fair test - like giving every technique the exact
same exam.

The design is a "recall distance ladder": we plant a fact, then ask about
it again after 1 turn, then plant another and ask after 3 turns, then 6,
then 8, then finally re-ask about the very first fact after all 23 turns.

Why a ladder instead of one big pile of questions at the end: different
memory techniques break at different distances. No Memory fails at
distance 1 (it forgets instantly). A small Sliding Window survives
distance 1 but fails by distance 3 (the fact scrolled out). Buffer,
Summary, Vector Store, and Entity memory are being tested on whether they
can survive all the way out to distance 23. Watching WHERE on the ladder a
technique starts failing is the whole lesson - it's not "does it remember,"
it's "how far back can it remember, and why."
"""

NOVA_SYSTEM_PROMPT = (
    "You are Nova, a warm and cheerful AI buddy chatting with a new friend. "
    "Reply in 1-2 short, friendly sentences. Do not repeat the user's message back to them."
)

SCRIPT = [
    "Hi! I'm Maya, nice to meet you.",                                  # 0   PLANT: name
    "Quick check, what's my name?",                                     # 1   PROBE: name (1 turn back)
    "I have a pet cat named Whiskers, she's super fluffy.",             # 2   PLANT: pet
    "What's a fun fact about octopuses?",                               # 3   filler
    "What's the tallest mountain in the world?",                        # 4   filler
    "Okay, what's my cat's name?",                                      # 5   PROBE: pet (3 turns back)
    "My favorite food is mango ice cream, I could eat it every day.",   # 6   PLANT: food
    "Can you tell me a short joke?",                                    # 7   filler
    "What's 15 times 23?",                                              # 8   filler
    "How many continents are there on Earth?",                         # 9   filler
    "Do you know any fun riddles?",                                     # 10  filler
    "What's the capital of France?",                                    # 11  filler
    "What's my favorite food again?",                                   # 12  PROBE: food (6 turns back)
    "I've always dreamed of visiting Japan someday.",                   # 13  PLANT: dream_trip
    "Explain what a rainbow is in one sentence.",                       # 14  filler
    "What's a good name for a new puppy?",                              # 15  filler
    "Tell me something interesting about outer space.",                 # 16  filler
    "What's the fastest animal on land?",                               # 17  filler
    "Give me a short motivational quote.",                              # 18  filler
    "What's a healthy breakfast idea?",                                 # 19  filler
    "How do bees make honey?",                                          # 20  filler
    "Where did I say I want to travel?",                                # 21  PROBE: dream_trip (8 turns back)
    "What's a good first programming language to learn?",              # 22  filler
    "One last check, what's my name again?",                           # 23  PROBE: name (23 turns back)
]

# fact key -> a lowercase keyword we look for in Nova's reply to grade pass/fail
PLANTED_FACTS = {
    "name": "maya",
    "pet": "whiskers",
    "food": "mango",
    "dream_trip": "japan",
}

# fact key -> SCRIPT index where that fact was first mentioned
PLANT_TURNS = {
    "name": 0,
    "pet": 2,
    "food": 6,
    "dream_trip": 13,
}

# SCRIPT index -> which fact that turn is probing for
PROBE_TURNS = {
    1: "name",
    5: "pet",
    12: "food",
    21: "dream_trip",
    23: "name",
}

_PROBE_LABELS = {
    "name": "What's the user's name?",
    "pet": "What's the user's pet's name?",
    "food": "What's the user's favorite food?",
    "dream_trip": "Where does the user want to travel?",
}


def check_probe(fact_key: str, reply_text: str) -> bool:
    """Very simple pass/fail check: did the keyword show up in Nova's answer?"""
    return PLANTED_FACTS[fact_key] in reply_text.lower()


def probe_question_text(fact_key: str) -> str:
    return _PROBE_LABELS[fact_key]


def probe_distance(turn_index: int) -> int:
    """How many turns back the fact being probed at this turn was planted."""
    fact_key = PROBE_TURNS[turn_index]
    return turn_index - PLANT_TURNS[fact_key]
