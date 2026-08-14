# ADR-0001: Modular monolith — Next.js, FastAPI, PostgreSQL/pgvector

- Status: Accepted (foundation implemented)
- Date: 2026-08-14
- Deciders: engineering (repository owners UNASSIGNED)

## Context

The repository is empty. The specification prefers a TypeScript React/Next.js client, Python FastAPI backend, and PostgreSQL + pgvector, with containerized environments. Premature microservices would add operational cost before a voice loop exists.

## Decision

Implement Pixel as a modular monolith:

- `apps/web` — Next.js + React + TypeScript
- `apps/api` — FastAPI (HTTP + WebSocket)
- `apps/worker` — ingestion jobs sharing API packages
- PostgreSQL 16 + pgvector as the system of record and vector store

Module boundaries inside the API still follow gateway, orchestrator, knowledge, tools, security, and observability.

## Consequences

One deployable API process is easier to test and run locally. Splitting services later is allowed only with measured need. The team must maintain two languages (TypeScript + Python).

## Alternatives considered

- Node-only backend: valid per spec, weaker Python AI/RAG ecosystem for this team posture.
- Separate knowledge/tool microservices on day one: rejected as unnecessary infrastructure.
