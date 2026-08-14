# Evaluations

**Current scores:** knowledge eval is scored against the fixture corpus (`evals/knowledge`). Policy/safety fixtures remain unscored against a live vendor model.

Phase 1 fixtures (unscored against a live model):

- [`evals/policy/cases.jsonl`](../evals/policy/cases.jsonl) — 83 policy cases
- [`evals/safety/cases.jsonl`](../evals/safety/cases.jsonl) — 19 safety cases
- Dialogues: [`docs/conversation-examples.md`](conversation-examples.md)

## Knowledge / RAG

See [`evals/knowledge/README.md`](../evals/knowledge/README.md) and `docs/knowledge.md`.

- Retrieval hit rate (expected source in top-k)
- Context precision
- Groundedness of org-specific claims
- Citation correctness
- Abstention when evidence is missing
- Freshness for dates/events

Do not score “correctness” from model memory.

## Safety (future)

- Prompt injection (user and retrieved HTML)
- System prompt / secret extraction
- Tool abuse / arbitrary URL
- Harmful cyber requests
- Password/OTP solicitation

## Voice (future)

- Time to transcript, time to first audio, barge-in cancel time
- Domain-term recognition samples
- Silence and permission-denied paths

## Rule

Every production bug in routing, knowledge, tools, or safety should add a regression case here. Do not ship evals that require production user transcripts.
