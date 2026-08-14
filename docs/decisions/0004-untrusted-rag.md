# ADR-0004: Untrusted RAG and retrieval-required org facts

- Status: Accepted
- Date: 2026-08-14
- Deciders: engineering + security (reviewer UNASSIGNED)

## Context

Web and PDF text can contain prompt-injection. Model memory will hallucinate Cyber Florida facts. The specification requires grounded answers and treats retrieved content as untrusted.

## Decision

- Organization-specific claims require retrieval (or a tiny curated facts table).
- Retrieved chunks are passed as delimited **data**, never as system/developer instructions.
- Retrieval cannot add tools or change `docs/policies.md`.
- Weak/missing evidence → abstain (FR-27).
- Public vs internal corpora stay separated; MVP indexes public sources only.

## Consequences

Some questions will correctly refuse. Ingestion quality becomes a product dependency. Prompt assembly must be tested against injection fixtures.

## Alternatives considered

- Fine-tune or prompt-only Cyber Florida knowledge: rejected (stale + hallucinated facts).
- Trusting retrieved text as instructions: rejected (OWASP LLM01).
