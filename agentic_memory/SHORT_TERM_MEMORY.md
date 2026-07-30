# Short-Term Memory — Architecture Diagrams

Companion reference for pages 1-8 of AI Memory Lab. Each technique answers the same
question — **does a fact survive more turns in the SAME conversation?** — with a different
trade-off between recall, cost, and complexity. GitHub renders the Mermaid diagrams below
natively, so this is the "How It Works" view for each technique.

---

## 1. No Memory (the baseline)

```mermaid
flowchart LR
    A[User message] --> B[System prompt + this message only]
    B --> C[Send to Nova]
    C --> D[Reply]
    D --> E[Nothing saved]
    E -. next turn starts over .-> A
```

**Best:** it's free and instant — there's no memory to store, manage, or pay for.
**Worst:** it forgets everything the moment you say it, even one message later.
**Example:** tell it your name, then ask again on the very next message — it has no idea.

---

## 2. Buffer Memory

```mermaid
flowchart LR
    A[New message] --> B[Append to full history]
    B --> C[Send entire history plus new message]
    C --> D[Reply]
    D --> E[Append reply to history too]
    E -. history keeps growing .-> B
```

**Best:** never forgets anything — perfect recall, every single time.
**Worst:** gets slower and more expensive the longer the conversation runs.
**Example:** a 500-message chat means resending all 500 messages, on every single turn.

---

## 3. Sliding Window Memory

```mermaid
flowchart LR
    A[New message] --> B[Add to window]
    B --> C{Window over k turns?}
    C -->|yes| D[Drop the oldest turn]
    C -->|no| E[Keep as is]
    D --> F[Send only what is in the window]
    E --> F
    F --> G[Reply]
    G --> H[Add reply to window too]
```

**Best:** cheap and fast — the cost never grows, no matter how long the chat runs.
**Worst:** anything older than the window is gone completely, even if it still matters.
**Example:** mention your allergy on turn 1, and by turn 10 it's already forgotten.

---

## 4. Summary Memory

```mermaid
flowchart LR
    A[New message] --> B[Send running summary plus new message]
    B --> C[Reply]
    C --> D[Summarization call]
    D --> E[New running summary replaces the old one]
    E -. used again next turn .-> B
```

**Best:** can hold the gist of a very long conversation in just a few sentences.
**Worst:** costs 2 API calls every single turn, and details can blur after enough rewrites.
**Example:** after 20 rewrites of the recap, a small detail like a middle name quietly disappears.

---

## 5. Summary Buffer Memory

```mermaid
flowchart LR
    A[New message] --> B[Add to recent buffer]
    B --> C{Buffer over token limit?}
    C -->|yes| D[Summarize the overflow]
    D --> E[Fold into running summary]
    C -->|no| F[Send summary plus recent buffer]
    E --> F
    F --> G[Reply]
```

**Best:** balances both worlds — sharp on recent details, still keeps the gist of the old stuff.
**Worst:** more moving parts than either technique alone, so it's harder to predict and tune.
**Example:** it nails what you said 2 turns ago, and roughly recalls what you said 20 turns ago.

---

## 6. Token Buffer Memory

```mermaid
flowchart LR
    A[New message] --> B[Add to buffer]
    B --> C{Buffer over token limit?}
    C -->|yes| D[Evict oldest messages, no LLM call]
    C -->|no| E[Keep as is]
    D --> F[Send buffer, within budget]
    E --> F
    F --> G[Reply]
```

**Best:** totally predictable — you always know the exact cost ceiling per turn.
**Worst:** still forgets older messages once the token budget fills up, just like a window.
**Example:** set a 150-token limit, and the oldest messages get dropped the moment you cross it.

---

## 7. Vector Store Memory

```mermaid
flowchart LR
    A[New message] --> B[Embed the message]
    B --> C[Search FAISS for the top-k similar memories]
    C --> D[Inject retrieved memories into system prompt]
    D --> E[Send system prompt plus new message]
    E --> F[Reply]
    F --> G[Embed and store this turn as a new memory]
```

**Best:** finds the right memory no matter how long ago it was said — no distance limit at all.
**Worst:** only retrieves what SOUNDS relevant, so it can miss context that matters but is worded differently.
**Example:** ask "what's my pet's name" 200 messages later and it still finds it instantly.

---

## 8. Entity Memory

```mermaid
flowchart LR
    A[New message] --> B[Extraction call: which entities were mentioned]
    B --> C[Look up known facts about those entities]
    C --> D[Inject entity facts into system prompt]
    D --> E[Send system prompt plus new message]
    E --> F[Reply]
    F --> G[Summarization call per entity: update each profile line]
```

**Best:** keeps a tiny, tidy profile of facts that never grows huge, no matter how long you chat.
**Worst:** only remembers things shaped like "facts about a name" — it's bad at free-flowing stories.
**Example:** it knows "Whiskers = Maya's cat" forever, but can't tell you what you two joked about.

---

See [LONG_TERM_MEMORY.md](LONG_TERM_MEMORY.md) for the techniques that survive *across*
separate conversations, not just within one. See [README.md](README.md) for setup and how
to run the app itself.
