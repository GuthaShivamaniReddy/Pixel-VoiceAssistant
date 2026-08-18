# Safety evaluation fixtures

`cases.jsonl` covers prompt injection, secret extraction, unsafe cyber assistance, arbitrary tools/URLs, retrieved-document injection, and emergency escalation.

`redteam.jsonl` expands Phase 8 categories: system-prompt extraction, secret extraction, role override, tool abuse, SSRF/malicious URLs, and RAG poisoning prompts.

`poison.html` is a retrieved-document injection fixture (untrusted data). In-memory tests ingest a related HTML fixture via `include_injection=True`.

These cases **must fail closed**. They are not scored for live-vendor helpfulness.

Automated runner: `packages/pixel/tests/test_safety_eval.py`.

See `docs/safety-rules.md` and `docs/conversation-examples.md`.
