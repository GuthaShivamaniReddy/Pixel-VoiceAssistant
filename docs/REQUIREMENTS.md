# Pixel — Requirements

**Document status:** Phase 0 (Architecture / Planning)  
**Product:** Pixel — Cyber Florida AI Voice Assistant  
**Requirement IDs** are stable. Later phases must map implementation, tests, and release gates to these IDs.

Pixel is a specialized Cyber Florida assistant, not a generic chatbot with a microphone. Organization-specific claims must be grounded in approved sources. Pixel must identify itself as an AI assistant when relevant and must never imply it is a human Cyber Florida employee.

---

## 1. Scope

### 1.1 In scope for MVP

- Voice input and text input.
- Speech-to-text, multi-turn conversation, text-to-speech.
- Cyber Florida knowledge via RAG with visible sources.
- Cybersecurity education and phishing/scam defensive guidance.
- Approved tools/actions (navigation and lookup first).
- User interruption (barge-in) while Pixel is speaking.
- Accessible, responsive web interface.
- Safety/policy controls, basic analytics, knowledge admin workflow.

### 1.2 Out of scope for MVP

- General-purpose smart-home or device control.
- Unrestricted web browsing or arbitrary tool execution.
- Autonomous high-impact security actions.
- Unrestricted access to internal Cyber Florida systems.
- Long-term memory of sensitive user information.
- Mobile-native apps, kiosk hardware, multilingual production support.
- User profiles / personalization beyond the current session (Release 2+).

### 1.3 Target users

General public, students, educators, veterans / first responders / public servants, cybersecurity professionals, public-sector organizations, businesses, and Cyber Florida staff (for public-information and approved admin workflows).

---

## 2. Functional requirements

### 2.1 Voice and text interaction

| ID | Capability | Requirement |
|---|---|---|
| FR-01 | Voice capture | Capture microphone audio only after explicit user initiation (push-to-talk) or an approved listening mode. Microphone state must never be ambiguous. The user must be able to stop listening immediately. |
| FR-02 | Voice activity detection | Detect speech start/end (or honor explicit PTT boundaries) to reduce unnecessary audio transmission and support turn-taking. |
| FR-03 | Speech-to-text | Convert speech to text with accuracy sufficient for cybersecurity terminology and common Cyber Florida proper nouns. |
| FR-04 | Text input | Keyboard/text input is a complete fallback. Development and degraded operation must never depend on working audio. |
| FR-05 | Streaming response | Begin producing the response before the full answer is generated when the selected architecture supports streaming. |
| FR-06 | Text-to-speech | Speak Pixel responses with natural pacing and clear pronunciation. Keep spoken answers typically 1–4 sentences; put detail on screen. |
| FR-07 | Interruption (barge-in) | Allow the user to interrupt Pixel while it is speaking; stop playback, cancel in-flight generation/TTS, and process the new request. |
| FR-08 | Multi-turn context | Retain bounded recent-turn context so follow-ups such as “that program” or “what about eligibility?” resolve. |
| FR-19 | Error recovery | Handle microphone, network, retrieval, model, speech synthesis, and tool errors with clear recovery options. Voice failures must degrade to usable text. |
| FR-24 | Session controls | Allow the user to clear the current conversation/session context. |
| FR-26 | Assistant states | Surface IDLE, LISTENING, TRANSCRIBING, THINKING, RETRIEVING, SPEAKING, INTERRUPTED, ERROR, and OFFLINE as distinct, truthful UI states. |

### 2.2 AI conversation and knowledge

| ID | Capability | Requirement |
|---|---|---|
| FR-09 | Intent routing | Classify requests into Cyber Florida knowledge, general cybersecurity guidance, scam/phishing help, navigation/action, clarification, or unsupported. |
| FR-10 | Cyber Florida RAG | Retrieve relevant approved Cyber Florida content before answering organization-specific questions. Do not answer org-specific facts from model memory. |
| FR-11 | Source attribution | Associate answers with source URL/document and expose sources in the UI when useful. |
| FR-12 | Freshness | Treat dates, deadlines, events, leadership, and availability as data that must be refreshed or verified. Abstain if evidence is stale or missing. |
| FR-13 | Program discovery | Ask concise questions and recommend relevant programs/resources using verified content. |
| FR-14 | Cybersecurity education | Explain defensive cybersecurity concepts at beginner, intermediate, or advanced depth on request. |
| FR-15 | Incident guidance | Provide prioritized **defensive** steps for common user incidents (phishing click, credential exposure, suspicious messages). Escalate when investigation/authority is required. |
| FR-16 | Scam analysis | Identify warning signs in user-provided message content without claiming certainty beyond available evidence. Never request passwords, OTPs, or full account credentials. |
| FR-27 | Grounded generation | If retrieval evidence is missing or weak for an org-specific claim, Pixel must say it cannot verify rather than invent details. |
| FR-28 | Disclosure | Identify as an AI assistant when relevant. Never impersonate Cyber Florida staff. |

### 2.3 Tools, admin, and product operations

| ID | Capability | Requirement |
|---|---|---|
| FR-17 | Approved navigation | Open or navigate only to allowlisted Cyber Florida pages. |
| FR-18 | Tool confirmation | Actions with meaningful side effects require a confirmation boundary unless inherently safe and reversible. |
| FR-20 | Feedback | Allow users to rate or flag answers and optionally provide a reason. |
| FR-21 | Admin ingestion | Authorized staff can add/update/remove approved knowledge sources and trigger re-indexing. |
| FR-22 | Content lifecycle | Track source, version/fetch time, last updated time, content hash, and document status. |
| FR-23 | Analytics | Measure turns, completion, latency by stage, retrieval success, errors, and feedback without storing unnecessary sensitive content. |

### 2.4 Accessibility and responsive interface

| ID | Capability | Requirement |
|---|---|---|
| FR-25 | Accessibility | Captions/transcripts, keyboard navigation, visible focus, accessible names, and non-audio alternatives for every voice action. Target WCAG 2.2 AA. |
| FR-29 | Responsive UI | Core flows usable on mobile, tablet, and desktop. No core flow may depend only on color, sound, or pointer interaction. |
| FR-30 | Transcript | Show a live or post-turn transcript so speech is never the only channel. |

---

## 3. Non-functional requirements

| ID | Area | Requirement |
|---|---|---|
| NFR-01 | Performance / latency | Optimize for conversational responsiveness. Instrument independently: time-to-transcript, retrieval, model first token/audio, TTS start, barge-in cancel, total turn. Measure after the voice loop exists; then set numeric p95 targets. |
| NFR-02 | Availability | The public experience should degrade gracefully when a dependency is unavailable. Text mode and basic navigation remain usable where possible. |
| NFR-03 | Scalability | Application services are stateless and horizontally scalable. Session state lives in PostgreSQL first; Redis only if measured need. |
| NFR-04 | Security | Least privilege, encrypted transport, secret management, input validation, dependency scanning, logging controls, and separation of public vs privileged actions. Detailed controls: SEC-* and `SECURITY.md`. |
| NFR-05 | Privacy | Minimize audio/text retention, avoid sensitive data in logs, document retention, and user notice. Detailed controls: PRIV-* and `SECURITY.md`. |
| NFR-06 | Accessibility | WCAG 2.2 AA for the web interface. Voice functions have equivalent visual/text controls. |
| NFR-07 | Maintainability | Providers behind interfaces. Isolate speech, LLM, retrieval, tools, and storage. Document contracts. Prefer one orchestrator boundary. |
| NFR-08 | Observability | Structured logs, metrics, traces, correlation IDs per turn. Dashboards for latency, errors, retrieval no-result rate, tool failures. A failed turn must be diagnosable without reading sensitive raw content. |
| NFR-09 | Testability | Orchestration, routing, tools, chunking, and policy must be testable without a microphone or live AI provider (mocks/fixtures). |
| NFR-10 | Auditability | Record privileged tool calls and administrative content changes with actor, timestamp, target, result, and correlation ID. |
| NFR-11 | Resilience / reliability | Timeouts, bounded retries, circuit-breaker behavior where appropriate, provider kill switches, and explicit fallbacks if STT/TTS/LLM/RAG fail. |
| NFR-12 | Portability | No hard-coded single vendor in domain logic. Adapters + configuration. |

---

## 4. Security requirements

| ID | Area | Requirement |
|---|---|---|
| SEC-01 | Prompt injection | User input and **retrieved documents are untrusted**. Retrieved text must never override system/developer instructions, grant tools, or change policy. See `SECURITY.md`. |
| SEC-02 | Input validation | Validate and size-limit all API inputs, tool arguments, and upload/import payloads server-side. |
| SEC-03 | Tool permissions | Tools exist only via server-side allowlists, schemas, authorization, and confirmation policy. The model cannot create tools. |
| SEC-04 | Rate limiting | Rate-limit public endpoints; apply body/request size limits and abuse controls. |
| SEC-05 | Secrets | Never expose API keys or long-lived credentials to the browser. Never commit secrets. Use env/secrets manager. Client may receive only short-lived delegated session material when explicitly designed. |
| SEC-06 | Authentication readiness | Public anonymous mode for general information. Architecture must allow OIDC/SAML (or org-approved SSO) for staff/admin without redesigning the API. Do not ship open admin endpoints. |
| SEC-07 | Authorization readiness | Enforce authorization on the server for every protected action. UI visibility is not an authorization control. Separate public vs privileged knowledge indexes when internal content exists. |
| SEC-08 | XSS | Treat transcripts, model output, and retrieved titles/snippets as untrusted in the UI. Default React encoding; never `dangerouslySetInnerHTML` for model/RAG text. |
| SEC-09 | CSRF | Cookie-based session (if used) requires CSRF protection. Prefer Authorization bearer/session tokens that are not automatically attached cross-site, plus SameSite cookies if cookies are used. |
| SEC-10 | CORS | Explicit allowlist of frontend origins. No `*` with credentials. |
| SEC-11 | API security | TLS in transit; authenticated admin routes; security headers; no stack traces to clients; health endpoints without secrets. |
| SEC-12 | Least privilege | Service identities and DB roles limited to needed operations. |
| SEC-13 | Dependency security | SCA/dependency scanning in CI; patch critical issues through a defined process. |
| SEC-14 | Harmful cyber requests | Refuse offensive hacking, exploit, malware, or unauthorized-access assistance. Defensive education and awareness only. |
| SEC-15 | Output validation | Check responses for policy violations, secret leakage patterns, invalid tool calls, and unsupported org facts before TTS/UI commit. |

---

## 5. Privacy requirements

| ID | Area | Requirement |
|---|---|---|
| PRIV-01 | Audio handling | **Default: audio is transient.** Process for STT and discard. Do not persist raw audio unless a later approved policy explicitly requires it, with notice and retention limits. |
| PRIV-02 | Conversation retention | Store only bounded session messages needed for multi-turn context. Sessions expire. User can clear the current conversation. No long-term personal memory in MVP. |
| PRIV-03 | Sensitive data | Do not solicit passwords, OTPs, SSNs, full financial account numbers, or authentication tokens. Detect/redact high-risk values from logs where feasible. |
| PRIV-04 | Logging | Structured operational logs. Do not log raw audio, secrets, or unnecessary transcript bodies in production by default. Correlation IDs instead of content dumps. |
| PRIV-05 | User privacy | Provide user-facing notice that Pixel is an AI assistant that processes voice/text to answer questions. Document retention. Minimize PII. Feedback is optional and should warn against including sensitive data. |
| PRIV-06 | Analytics minimization | Aggregate metrics preferred. Feedback comments stored with retention and access control. |
| PRIV-07 | Admin access | Knowledge and conversation-admin access is privileged; audit it. |

---

## 6. UX and voice behavior (normative)

- Display listening, processing, speaking, and error states truthfully.
- Visible Stop / Mute / Cancel while Pixel is speaking or listening.
- Short spoken answers; screen for links, sources, and multi-step instructions.
- Explicit wording when Pixel is uncertain or cannot verify a fact.
- Source links and next actions prominent after relevant answers.

---

## 7. MVP acceptance (product-level)

| Category | Criterion |
|---|---|
| Conversation | User can speak a question, receive a spoken answer, ask a follow-up, and interrupt the assistant. Text fallback works. |
| Knowledge | Approved Cyber Florida evaluation questions meet the grounded-answer target and surface correct sources. |
| Safety | Pixel does not expose secrets/system instructions in standard red-team tests and does not execute unauthorized tools. |
| Reliability | Voice, text, retrieval, and error fallbacks work in staging under expected load. |
| Accessibility | Core flows pass keyboard testing and automated/manual accessibility checks. |
| Operations | Teams can monitor errors/latency, update knowledge, review feedback, and roll back a release. |

These criteria are **not met** in Phase 0. No runtime exists.

---

## 8. Requirement ownership in later phases

| Cluster | Primary later phase |
|---|---|
| Identity, tone, safety wording | Phase 1 |
| Repo, CI, env, containers | Phase 2 |
| UI states, text fallback, a11y shell | Phase 3 |
| STT/TTS/barge-in | Phase 4 |
| Orchestrator, context, routing | Phase 5 |
| RAG / ingestion | Phase 6 |
| Tools | Phase 7 |
| Hardening | Phase 8 |
| Visual polish | Phase 9 |
| Observability, feedback (FR-20), dashboards | Phase 10 |
| Eval / UAT | Phases 11–12 |
| Production | Phase 13 |
