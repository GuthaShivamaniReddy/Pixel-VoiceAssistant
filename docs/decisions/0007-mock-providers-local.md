# ADR-0007: Mock providers by default locally

- Status: Accepted (planned; not implemented)
- Date: 2026-08-14
- Deciders: engineering

## Context

Tests and onboarding must not require paid vendor keys or a microphone. Fake “live AI” with hidden hardcoded answers in production is forbidden; labeled mocks in development are required.

## Decision

Local/default configuration uses mock `LLMProvider`, `SpeechToTextProvider`, `TextToSpeechProvider`, and `EmbeddingProvider`. CI uses mocks. Real adapters are opt-in via environment variables that are never committed.

UI and API must label mock mode so it is not mistaken for production intelligence.

## Consequences

Developers can clone and run. Demo risk if mock mode is enabled in production — production config must forbid mocks except an explicit, logged override.

## Alternatives considered

- Live APIs required for all tests: rejected (secrets, flakiness, cost).
