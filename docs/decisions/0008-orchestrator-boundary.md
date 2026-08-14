# ADR-0008: Central orchestrator boundary

- Status: Accepted
- Date: 2026-08-14
- Deciders: engineering

## Context

Phase 4 called the LLM from `run_text_turn` / `run_voice_turn` with a hardcoded prompt. Phase 5 requires one controlled intelligence path for text and voice, with policy, intent, validation, and provider errors in one place.

## Decision

`process_turn` in `packages/pixel/pixel/orchestrator/process.py` is the only application entry that may request model output. Adapters under `pixel.providers` may talk to vendors. API routes only validate transport, sessions, and cancellation. Policy is versioned server-side (`pixel-behavior` `1.2.0`). Provider failures are `ProviderError` categories, then mapped to user-facing codes.

## Consequences

Text and voice share follow-up context, refusals, and fallbacks. Adding RAG or tools later plugs into retrieval/tool decisions without new LLM call sites.

## Alternatives considered

- Separate voice and text brains: rejected (drift).
- LLM calls in FastAPI handlers: rejected (scattered policy).
