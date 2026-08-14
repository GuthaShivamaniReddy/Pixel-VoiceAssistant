# Policy evaluation fixtures (Phase 1)

`cases.jsonl` — one JSON object per line. **Not executed against a live model in this phase.**

| Field | Meaning |
|---|---|
| `id` | Matches `docs/conversation-examples.md` |
| `labels` | `ALLOW` `ANSWER_DEFENSIVELY` `REQUIRE_SOURCE` `ASK_CLARIFICATION` `ABSTAIN` `ESCALATE` `DENY_UNSAFE_ACTION` `REQUIRE_CONFIRMATION` |
| `policy_version` | `pixel-behavior-1.1.0` |

Full dialogues live in the markdown corpus. Later orchestrator tests should load this file rather than inventing a second set of cases.

Safety/adversarial subset: `../safety/cases.jsonl`.
