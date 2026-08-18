# Pixel — Tools (Phase 7)

**Status:** Implemented. Server-side only. The model cannot execute tools.

Approved tools: `find_program`, `find_resource`, `search_approved_content`, `navigate_to_url`.

```
USER → orchestrator → intent → select_tool_calls → registry → permission →
confirmation → input validation → handler → normalized result → UI action
```

Unknown names are rejected. Retrieved documents cannot grant tools. Authorization is `AuthContext` from the API, never from model output.

## Registry

`pixel.tools.registry.production_registry()` is the only production set. Duplicate names are rejected at register time.

## Shared rules

| Field | Value |
|---|---|
| Permission | `public` |
| Timeouts | `TOOL_TIMEOUT_SECONDS` (default 5), capped by the tool definition |
| Loop limit | `MAX_TOOL_CALLS_PER_TURN` (default 2) |
| Audit | `tool_audit` log: name, status, authorized, confirmed, duration, session, turn, correlation. Arguments are not logged. |
| HTTP/shell/SQL | None. Tools do not fetch URLs, spawn processes, or run SQL. |

Navigation destinations must be **registered canonical HTTPS URLs** on `cyberflorida.org` / `www.cyberflorida.org`. Host substring matching is not used. `javascript:`, `data:`, `file:`, `http:`, localhost, and private IPs are denied.

## find_program

| | |
|---|---|
| **PURPOSE** | List approved Cyber Florida programs from the Phase 6 source registry |
| **INPUTS** | `audience` (enum), `topic`, `keywords` — all optional |
| **OUTPUTS** | Sources, Open actions, short user message |
| **PERMISSIONS** | public |
| **CONFIRMATION** | none |
| **FAILURE** | `not_found` / `invalid_input` — no invented programs |

## find_resource

Same as find_program over all approved public sources (not programs-only).

## search_approved_content

Wraps the Phase 6 retriever. Inactive/non-public chunks are skipped. Does not search the open web.

## navigate_to_url

| | |
|---|---|
| **PURPOSE** | Resolve an approved page for the user to open |
| **INPUTS** | `source_id` and/or `url` |
| **OUTPUTS** | One Open action with the canonical URL |
| **PERMISSIONS** | public |
| **CONFIRMATION** | `ui_click` — the labeled link is the confirmation; Pixel does not auto-redirect |
| **FAILURE** | `invalid_destination` — no action chip |

The browser is never sent an unapproved href from this tool.

## Side-effecting tools

Not implemented. Confirmation engine exists and is tested with a non-production definition. Stronger idempotency is deferred until write tools exist.

## Voice

Voice and text share `process_turn`. Follow-up “open that program” uses `session.last_offers`. Empty later turns do not wipe stored offers. “Tell me more about the first one” is a follow-up that retrieves the resolved program.
