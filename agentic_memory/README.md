# AI Memory Lab

A hands-on Streamlit app for teaching LLM "memory" techniques - short-term AND
long-term - live, with a real Groq model, a real cost meter, and scripted
demos designed to make each technique's trade-off obvious on stage.

**Architecture diagrams for every technique live outside the app now**, as plain
Mermaid diagrams in two companion files (GitHub renders these natively - no browser
JS involved, so nothing to break):
- [SHORT_TERM_MEMORY.md](SHORT_TERM_MEMORY.md) - diagrams for techniques 1-8
- [LONG_TERM_MEMORY.md](LONG_TERM_MEMORY.md) - diagrams for techniques 10-14

## Part 1 - Short-term memory (pages 1-9)

Every page chats with the same character, **Nova**, through the same 24-message
script. Facts get planted early (name, pet, favorite food, dream trip), buried
under small talk, then probed for at increasing distances (1, 3, 6, 8, 23
turns) - so you can literally watch a memory technique remember or forget,
live, in front of the class.

| Page | Technique | What it teaches |
|---|---|---|
| 1 | No Memory | The baseline - forgets everything instantly |
| 2 | Buffer Memory | Remembers everything, cost grows forever |
| 3 | Sliding Window Memory | Fixed-size window, old facts fall out (live-resizable) |
| 4 | Summary Memory | One running recap, rewritten every turn (2x calls) |
| 5 | Summary Buffer Memory | Recent turns exact, older turns summarized |
| 6 | Token Buffer Memory | Hard token cap, zero extra API calls (live-resizable) |
| 7 | Vector Store Memory | Retrieves only the most relevant past memories |
| 8 | Entity Memory | Tracks a small profile card of facts, not raw text |
| 9 | Comparison | Runs all 8 back-to-back, one scoreboard |

## Part 2 - Long-term memory (pages 10-14)

Short-term memory tests survival *within* one conversation. Long-term memory
tests survival *across* separate conversations - which requires showing a
different thing: not "did it forget", but "what got extracted before the
session ended, and is that small extracted thing enough on its own."

Every page here runs the same **two-session experiment**: Session 1 happens,
gets compressed at "Close Session 1 & Extract" (with the raw-transcript-to-
artifact conversion shown on screen), then a completely fresh Session 2 starts
with **zero raw messages** - only the extracted artifact. If Session 2 still
answers correctly, the artifact - not the transcript - is doing the work.

| Page | Technique | What it teaches |
|---|---|---|
| 10 | Episodic Memory | One session -> one timestamped "diary entry" (JSON) |
| 11 | Semantic Memory | Many episode summaries distilled into general, reusable facts |
| 12 | Procedural Memory | A stated preference becomes a standing behavioural rule (system-prompt directive, not context) |
| 13 | Self-Reflection Memory | The agent critiques its own performance - evidence-grounded, or discarded |
| 14 | Memory Routing | Classifies each message, queries only the relevant store(s) - interactive, no session needed |

## Tech stack

- **Streamlit** for the app/UI
- **LangChain** (`langchain`, `langchain-classic`, `langchain-groq`) for the
  chat model and the actual memory classes (`ConversationBufferMemory`,
  `ConversationSummaryMemory`, etc.) - these are LangChain's "classic" memory
  APIs, kept around specifically because their names map 1:1 onto the
  concepts being taught, even though LangChain's own docs now point new
  production apps toward LangGraph checkpointers instead.
- **Groq** (BYOK - bring your own API key) as the LLM provider, for its speed
  and generous free tier
- **fastembed** for local, free, no-API-key embeddings (`BAAI/bge-small-en-v1.5`)
- **FAISS** for the local vector store (Technique 7)

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (macOS/Linux)
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get a free Groq API key at https://console.groq.com/keys

## Running it

```
streamlit run app.py
```

This opens the **Home** page in your browser. Paste your Groq API key into the
sidebar, pick a model (Llama 3.1 8B Instant is the fastest/cheapest and is the
default), then open any page from the sidebar.

The first time you visit a page that uses embeddings (Technique 7, or the
Comparison page), fastembed will download its small model - this needs
internet access once, then works offline.

## Project layout

```
app.py                     Home page: API key entry, model picker, overview
common.py                  Shared short-term page driver: chat loop, metrics, charts
common_ltm.py              Shared long-term page driver: two-session flow, extraction, injection
engine.py                  Runs one conversation turn through a short-term strategy
tracking.py                Counts every API call made (incl. hidden ones)
pricing.py                 Groq's real per-model $/token pricing
embeddings.py              Local embedding model wrapper (fastembed)
scenario.py                Shared short-term scripted conversation + planted facts
long_term_scenario.py      Shared long-term two-session script + probes
memory_strategies/         One file per short-term technique, wrapping LangChain's memory classes
long_term_memory/          One file per long-term technique (hand-rolled - LangChain has no
                            built-in classes for episodic/semantic/procedural/reflection/
                            routing, so these implement the extraction + injection logic
                            directly, guided by the reference notebooks)
components/                Shared UI: metrics bar, growth chart, context inspector,
                            transformation panel (raw -> extracted artifact), verdict box
pages/                     14 Streamlit pages: 1-9 short-term (+ comparison), 10-14 long-term
SHORT_TERM_MEMORY.md       Architecture diagrams (Mermaid) for techniques 1-8
LONG_TERM_MEMORY.md        Architecture diagrams (Mermaid) for techniques 10-14
```

Each short-term technique lives in its own file under `memory_strategies/`,
all implementing the same two-method interface (`get_messages_for_reply`,
`save`), so `engine.py` and `common.py` don't need to know which technique
they're driving.

Each long-term technique lives in its own file under `long_term_memory/`,
exposing three functions: `extract(llm, session1_transcript) -> artifact`,
`artifact_panel(artifact) -> (title, content)`, and
`build_session2_system_prompt(base_prompt, artifact) -> str`. `common_ltm.py`
drives all four session-based pages (Episodic, Semantic, Procedural,
Self-Reflection) through this same interface. Routing is an interactive,
non-session demo and doesn't use `common_ltm.py`.

## Notes for the live demo

- Each page has its own **Reset this demo** button, so a mid-class mistake
  doesn't cost you time - it wipes just that page's conversation and stats.
- The **Comparison** page makes 100+ real API calls in one go (it replays the
  full script through all 8 short-term techniques). It takes a couple of
  minutes - don't run it repeatedly back-to-back.
- The long-term pages (10, 11, 13) each make 1-2 extra extraction calls when
  you click "Close Session 1 & Extract" - visible in the live cost meter,
  same as the short-term pages' hidden summarization calls.
- Groq pricing can change - if the numbers in the cost meter look off, check
  https://groq.com/pricing and update `pricing.py`.
