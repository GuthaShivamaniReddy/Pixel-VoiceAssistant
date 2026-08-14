# ADR-0006: Public anonymous sessions; admin fail-closed

- Status: Accepted
- Date: 2026-08-14
- Deciders: engineering + security

## Context

MVP serves the public without login. Knowledge administration is privileged. Open admin routes would be a critical vulnerability.

## Decision

- Public Q&A uses unguessable server-side session identifiers; `conversations.subject` is nullable.
- Admin ingestion/reindex requires real authentication/authorization. If SSO/token config is absent, routes return disabled/403 (fail closed).
- No homemade production password table if the organization standard is OIDC/SAML. Local-dev exception must be explicit and non-default in production.

## Consequences

Public abuse must be handled with rate limits. Admin work is blocked until identity is integrated — that is acceptable.

## Alternatives considered

- Force login for all questions: higher friction than the public-information use case.
- Ship admin with a shared password in env: rejected for production.
