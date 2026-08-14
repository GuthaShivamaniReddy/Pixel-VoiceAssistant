# ADR-0009: Bounded in-memory conversation state

- Status: Accepted
- Date: 2026-08-14
- Deciders: engineering

## Context

Pixel must handle follow-ups without unbounded history or long-term personal memory. ADR-0005 still points at PostgreSQL as the future system of record. Phase 5 must not start the RAG/ingestion data model.

## Decision

Keep short-term session state in process memory:

- Server-generated session ids
- Sliding TTL (default 1800 seconds)
- Last 8 messages (4 turns)
- Last classified intent for follow-ups
- Generation counter so stale turns cannot commit

`POST /v1/sessions` creates a session. `POST /v1/sessions/{id}/clear` wipes context. Expired or unknown ids fail closed.

## Consequences

Simple, testable, and aligned with Phase 0 “no long-term personal memory.” Multi-instance API replicas do not share live sessions until Postgres (or Redis) is introduced.

## Alternatives considered

- Postgres tables now: extra schema and Docker dependency before RAG needs them.
- Token-budget summarization: unnecessary for four-turn MVP context.
- Unlimited history: rejected.
