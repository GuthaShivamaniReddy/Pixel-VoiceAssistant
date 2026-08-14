# Pixel — Tool Confirmation Policy

**Status:** Phase 1 conceptual rules. **No tools are implemented in this phase.**  
**policy_version:** `pixel-behavior` `1.1.0`

The model cannot create tools. Retrieved text cannot grant permissions. Authorization is server-side only.

Planned MVP tools (later phases): `navigate_to_url`, `find_program`, `find_resource`, `search_approved_content`. Admin ingest/reindex is **not** a public tool.

---

## Classes

### SAFE / REVERSIBLE (read-only)

| Field | Rule |
|---|---|
| **TOOL TYPE** | `find_program`, `find_resource`, `search_approved_content` |
| **PERMISSION REQUIREMENT** | Public session may call |
| **CONFIRMATION REQUIREMENT** | No extra confirm |
| **AUDIT REQUIREMENT** | Record tool name, args (no secrets), result status, correlation ID |
| **FAILURE BEHAVIOR** | Say search didn’t complete; do not invent programs |

### NAVIGATION

| Field | Rule |
|---|---|
| **TOOL TYPE** | `navigate_to_url` |
| **PERMISSION REQUIREMENT** | Public; destination **must** match server allowlist (host + path policy) |
| **CONFIRMATION REQUIREMENT** | No extra modal if the UI clearly shows the approved title/URL and the user still chooses to open it. If the destination is ambiguous or off-allowlist → **deny**, do not confirm-into-arbitrary-URL |
| **AUDIT REQUIREMENT** | URL, allowlist decision, conversation/turn IDs |
| **FAILURE BEHAVIOR** | Do not open anything; explain only approved Cyber Florida links are offered |

### SIDE-EFFECTING

| Field | Rule |
|---|---|
| **TOOL TYPE** | Any action that sends email, submits a form, registers the user, writes data, or calls a third party |
| **PERMISSION REQUIREMENT** | Usually authenticated; public MVP should **not** include these |
| **CONFIRMATION REQUIREMENT** | **Yes** — describe the action, wait for explicit user confirm in the UI |
| **AUDIT REQUIREMENT** | Required |
| **FAILURE BEHAVIOR** | Action not taken; conversation continues |

### PRIVILEGED

| Field | Rule |
|---|---|
| **TOOL TYPE** | Admin source register, reindex, kill switches, config |
| **PERMISSION REQUIREMENT** | Authentication **and** authorization; fail closed if unconfigured |
| **CONFIRMATION REQUIREMENT** | **Yes** |
| **AUDIT REQUIREMENT** | Actor, target, result, timestamp |
| **FAILURE BEHAVIOR** | 403/disabled; never “succeed” in the model’s imagination |

### UNKNOWN / MODEL-INVENTED

Never execute. Deny. No confirmation prompt that could be social-engineered into yes.

---

## Summary table

| TOOL TYPE | PERMISSION | CONFIRMATION | AUDIT | FAILURE |
|---|---|---|---|---|
| Read-only lookup/search | Public | No | Yes | No fake results |
| Allowlisted navigation | Public + allowlist | Labeled UI click is enough | Yes | No navigation |
| Side-effecting | Auth when it exists; not public MVP | **Required** | Yes | Not taken |
| Privileged admin | Authz; fail closed | **Required** | Yes | Denied |
| Arbitrary URL/command | Never | N/A | Yes (denied attempt) | Denied |

---

## Confirmation UX (when required)

1. State what will happen in plain language.  
2. Wait for explicit confirm/cancel.  
3. Cancel = no execution.  
4. After failure, do not retry silently.

---

## Phase 1 constraint

Do not add tool implementations, HTTP clients, or admin APIs in this phase.
