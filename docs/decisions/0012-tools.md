# ADR-0012: Server-side tool registry, no model execution

- Status: Accepted
- Date: 2026-08-17
- Deciders: engineering (Phase 7)

## Context

Phase 7 needs program discovery and approved navigation without giving the model unrestricted tools.

## Decision

1. The orchestrator selects tools deterministically (`select_tool_calls`). The LLM is not given a tool-calling API.
2. Only names in `production_registry()` can run.
3. Navigation accepts only registered canonical HTTPS Cyber Florida URLs.
4. Lookup tools reuse the Phase 6 registry/retriever. No second search index.
5. The UI Open link is the navigation confirmation (`ui_click`). Pixel does not implement `/open?url=`.

## Consequences

- Prompt injection cannot invent `run_shell_command` or attacker URLs that become actions.
- Follow-up “open that” depends on bounded `last_offers`, cleared with the conversation.
