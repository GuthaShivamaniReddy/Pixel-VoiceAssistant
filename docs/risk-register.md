# Pixel — Risk Register (Phase 0)

**Status:** Discovery register. Not a residual-risk sign-off.  
**Owners:** UNASSIGNED (see `product.md` §2).  
**Specification:** `Pixel_CyberFlorida_AI_Voice_Assistant_Project_Guide.pdf` v1.0.

Severity: **Critical / High / Medium / Low**. Likelihood: **High / Medium / Low** until measured.

---

## 1. Spec alignment (do not silently pick a side)

The PDF is the primary specification. Existing `docs/` and later engineering prompts must not drop PDF requirements. Where texts differ, the conflict is recorded here.

| ID | Topic | Project guide (PDF) | Existing docs / later prompt | Classification | Phase 0 handling |
|---|---|---|---|---|---|
| C-01 | Conversation entities | `sessions`, `turns`, plus `sources` / `documents` / `chunks` / `feedback` / `audit_events` | Architecture uses `conversations` / `messages`; `ingestion_jobs` / `tool_executions` extra | **Conflict (naming)** | Do not rewrite code (none exists). Implementation phases must map to PDF entities or record an ADR that supersedes names. Recommendation: use PDF names (`sessions`, `turns`) when schema is created. **Not decided by code.** |
| C-02 | Feedback timing | Feedback is **MVP** | Architecture §11.7 schedules `feedback` table in Phase 10 | **Conflict (timing)** | Product MVP **includes feedback** (`product.md`). Schema may be added when FR-20 is built, which must be **before production**, not treated as optional. Phase 10 remains when ops review UI is polished — the capability itself is MVP. |
| C-03 | UI states | Idle, listening, processing, speaking, error | Architecture: IDLE, LISTENING, TRANSCRIBING, THINKING, RETRIEVING, SPEAKING, INTERRUPTED, ERROR, OFFLINE. Master prompt also lists CONNECTING, PERMISSION_REQUIRED, CANCELLED, NETWORK_ERROR, VOICE_ERROR | **Compatible if mapped** | Required **user-visible** states: IDLE, LISTENING, PROCESSING, SPEAKING, ERROR. Finer states are internal/telemetry. See `product.md` §20. |
| C-04 | Provider interface names | LLM / STT / TTS adapters | Docs: `SpeechToTextProvider`; master prompt: `STTProvider`, plus `RealtimeProvider`, `RerankingProvider` | **Naming only** | Same adapters; aliases allowed. Rerank adapter only after baseline retrieval (PDF). |
| C-05 | Voice transport | WebRTC when low-latency bidirectional audio needs it; **WebSocket acceptable** for simpler streaming/control | ADR-0003: WebSocket + PTT first | **Not a conflict** | Allowed by PDF. WebRTC remains a later option if latency requires it. |
| C-06 | Redis | May hold short-lived session state **when needed** | ADR-0005: PostgreSQL first | **Not a conflict** | Redis deferred until measured (multi-instance cancel/cache). |
| C-07 | `policies.md` completeness | Phase 1 asks 50–100 example conversations and split safety docs | Phase 1 delivered `policies.md` v1.1.0, `conversation-examples.md` (102), `safety-rules.md`, `escalation-matrix.md`, `tool-confirmation-policy.md` | **Resolved in Phase 1** | Keep split files; `policies.md` remains the central contract. |

No PDF MVP requirement was removed because it was hard.

---

## 2. Product and adoption risks

| ID | Risk | Sev | Likely | Mitigation | Residual |
|---|---|---|---|---|---|
| R-01 | Hallucinated Cyber Florida facts | Critical | High without RAG | Retrieval required for org facts; abstain if weak; eval set | Until RAG+evals exist, any “answer” is unsafe to present as official |
| R-02 | Stale events/deadlines/eligibility | High | High | Freshness jobs; date-sensitive intents abstain; content owner | Candidate sources not signed |
| R-03 | Users over-trust Pixel | High | High | AI disclosure; sources; uncertainty language; no fake certainty on scams | Policy not in running code |
| R-04 | Scope creep (avatars, mobile, open web) | High | Medium | Locked MVP in `product.md` | Pressure to demo |
| R-05 | Unassigned owners | High | Certain | Roles listed; no official production claim; admin fail-closed | Cannot complete PDF “stakeholder agreement” literally |
| R-06 | Content allowlist not approved | High | Certain | Candidate URLs only; no production ingest | Same |

---

## 3. Security and safety risks

| ID | Risk | Sev | Likely | Mitigation | Residual |
|---|---|---|---|---|---|
| S-01 | Prompt injection via user or retrieved pages | Critical | High | Untrusted evidence channel; tools not granted by documents; red-team later | Unimplemented |
| S-02 | Secrets in browser or git | Critical | Medium if rushed | Server-only keys; `.env.example` names only; no `NEXT_PUBLIC_` vendor keys | No app yet (vacuously OK) |
| S-03 | Open admin ingestion | Critical | High if built early | Fail closed without SSO/authz | Must not ship open `/admin` |
| S-04 | Arbitrary tools / URLs | Critical | High if model-driven | Allowlist, schema, server authz, confirmation | Unimplemented |
| S-05 | Offensive cyber assistance | High | Medium | Policy refuse; safety evals | Unimplemented |
| S-06 | XSS from model/RAG HTML | High | Medium | Encode as text | Unimplemented |
| S-07 | Session guessing / abuse | High | High (public) | Unguessable IDs; in-process rate limits | Mitigated for single-process; not cluster-wide |
| S-08 | Dependency / supply chain | Medium | Medium | Lockfiles + CI SCA in foundation phase | No lockfiles yet |

---

## 4. Privacy risks

| ID | Risk | Sev | Mitigation |
|---|---|---|---|
| P-01 | Raw audio retained without notice | High | Default transient STT; exceptions need written policy |
| P-02 | Transcripts/logs contain secrets | High | Do not solicit passwords/OTPs; redact; minimize production transcript logs |
| P-03 | Retention duration undefined | Medium | Documented as TTL + user clear; **numeric TTL is an unresolved decision** (do not invent days) |
| P-04 | Feedback comments with PII | Medium | Warn users; access control; retention |

---

## 5. Engineering and delivery risks

| ID | Risk | Sev | Mitigation |
|---|---|---|---|
| E-01 | Building RAG/UI before the voice loop | High | Vertical slice: mic → STT → answer → TTS → barge-in |
| E-02 | Fake barge-in (UI state only) | High | Must stop playback and cancel generation; test on running app |
| E-03 | Vendor lock-in | Medium | Provider interfaces (ADR-0002) |
| E-04 | Two-language monorepo cost | Medium | Shared OpenAPI contracts; CI for both |
| E-05 | WebSocket latency vs conversational feel | Medium | Instrument stage latency; WebRTC later if needed |
| E-06 | Empty retrieval treated as a good answer | High | Abstain policy FR-27 |
| E-07 | Tests that need live paid APIs | Medium | Mocks default locally and in CI |
| E-08 | Workspace path with spaces (`PIXEl VA`) | Low | Quote paths in scripts |
| E-09 | No git repository | Medium | Initialize in foundation phase; no history/backup yet |
| E-10 | Claiming docs = product | High | README and architecture state unimplemented |

---

## 6. Assumptions (Phase 0)

1. Public anonymous Q&A is desired for general Cyber Florida information.
2. MVP knowledge is **public** `cyberflorida.org` content only.
3. English-only MVP.
4. Web client first; no native apps in MVP.
5. USF/Cyber Florida will name owners and approve sources before production.
6. Production hosting, DNS, SSO, and paid AI vendors are **not** chosen in this repo.
7. PDF allows WebSocket for simpler voice transport; that is the planned first path.
8. Numeric session TTL and feedback retention days require privacy-owner input.

---

## 7. Unresolved decisions (need stakeholder input — do not invent)

| Decision | Options (illustrative) | Recommendation | Wait? |
|---|---|---|---|
| Named owners | Assign Cyber Florida/USF people | Cannot invent names | **Yes** |
| Authoritative source approval | Candidate list in `product.md` §11 | Ingest only after content owner signs | **Yes** before production RAG |
| Production LLM / STT / TTS vendor | OpenAI, Azure, others | Adapters; local mocks | **Yes** before paid prod |
| Institutional SSO | OIDC / SAML / USF-approved | Fail closed until chosen | **Yes** before admin |
| Production hosting | UNASSIGNED | Container-ready | **Yes** before Phase 13 |
| Retention durations (days) | Transient audio; TTL TBD | Do not pick a number here | **Yes** |
| WebRTC in MVP vs later | Now vs after PTT+WS measured | After voice-loop metrics (ADR-0003) | No for Phase 0; revisit after Phase 4 |
| Schema names sessions vs conversations | PDF vs current architecture draft | Prefer PDF `sessions`/`turns` at implementation | Confirm at Phase 2/5 |

---

## 8. Phase 0 residual

Documentation can proceed. **Official Cyber Florida production** cannot. Admin ingestion cannot be enabled. Live org-specific answers cannot be trusted until RAG + signed sources + evals exist.
