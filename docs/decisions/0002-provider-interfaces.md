# ADR-0002: Provider interfaces

- Status: Accepted (interfaces in `packages/pixel`; mock and OpenAI adapters implemented)
- Date: 2026-08-14
- Deciders: engineering

## Context

Pixel must replace LLM, realtime, STT, TTS, embedding, and rerank vendors without rewriting business logic. SDKs in the UI or orchestrator would lock the product.

## Decision

Core code depends only on:

- `LLMProvider`
- `SpeechToTextProvider`
- `TextToSpeechProvider`
- `EmbeddingProvider`
- `VectorStoreProvider`

Optional later: `RerankProvider`. Vendor SDKs live only in adapters. Local default is mocks (ADR-0007).

## Consequences

Slightly more plumbing. Enables CI without paid APIs and future procurement changes.

## Alternatives considered

- Direct OpenAI (or other) SDK in the orchestrator: rejected (vendor lock-in).
