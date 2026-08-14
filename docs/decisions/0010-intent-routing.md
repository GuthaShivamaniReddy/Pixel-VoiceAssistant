# ADR-0010: Deterministic intent taxonomy

- Status: Accepted
- Date: 2026-08-14
- Deciders: engineering

## Context

The orchestrator must route Cyber Florida questions, defensive help, scams, navigation, clarification, and unsupported requests in a testable way. An extra classifier model call would add latency and a second failure mode.

## Decision

Use a small typed taxonomy and deterministic rules (`pixel.orchestrator.intents.classify_intent`). Follow-ups inherit `last_intent` when present. Prompt-injection and offensive patterns skip the model and return canned Phase 1 refusals. Structured `IntentResult` is validated for allowed enum values.

Retrieval and tools are flags only in Phase 5 (`requires_retrieval`, `requires_tool`). They do not execute.

## Consequences

Routing is predictable in CI without a paid LLM. Ambiguous phrasing can be misclassified; that is accepted until a later hybrid classifier is justified.

## Alternatives considered

- LLM JSON classification every turn: extra latency and invalid-JSON handling.
- Dozens of fine-grained intents: harder to test, overlaps Phase 7 tools.
