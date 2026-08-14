# ADR-0005: PostgreSQL for sessions; Redis later if measured

- Status: Accepted (Postgres/pgvector in Compose; conversation tables not created yet)
- Date: 2026-08-14
- Deciders: engineering

## Context

The specification allows Redis for short-lived distributed session state. Extra infrastructure is unjustified before horizontal multi-instance cancellation is needed.

## Decision

Store conversations/messages in PostgreSQL with TTL. Use in-process cancellation tokens in a single API instance. Introduce Redis (or equivalent) only if multiple API replicas must share live barge-in cancel or hot session cache.

## Consequences

Simpler local Compose. Multi-instance barge-in may be weaker until a shared bus exists.

## Alternatives considered

- Redis from day one: extra service without measured need.
