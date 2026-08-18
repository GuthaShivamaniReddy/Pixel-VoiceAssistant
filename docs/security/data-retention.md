# Data retention and privacy (Phase 8)

**Status:** Engineering description of the current implementation. Institutional retention periods are **UNASSIGNED** unless a Cyber Florida/USF privacy owner approves them. Do not invent legal wording.

Privacy/AI notice text for production is **stakeholder-owned** (Phase 13). The application currently discloses that Pixel is an AI, that voice/text go to the Pixel API, and that provider keys stay on the server.

---

## RAW AUDIO

PURPOSE: Speech-to-text for the current turn.

STORED: NO (not in the database or disk by Pixel). A bounded PCM buffer exists in memory for the active turn (`MAX_AUDIO_BYTES`).

LOCATION: `ConversationSession.active.pcm` until the turn is taken.

RETENTION: Discarded when the turn ends, is cancelled, or the session expires/clears.

ACCESS: API process memory only.

DELETION / EXPIRATION: Drop buffer; session TTL 1800s default.

Provider role: if `STT_PROVIDER=openai`, audio is sent to that vendor for transcription. Pixel does not archive a second copy. Vendor retention is outside this repo.

---

## TRANSCRIPTS

PURPOSE: Conversation context (max 8 messages) and UI display.

STORED: YES — in-memory session only at HTTP runtime. Not written to Postgres by `VoiceRuntime`.

LOCATION: `ConversationSession.messages`.

RETENTION: Until Clear Conversation, TTL, or process restart.

ACCESS: Holder of `session_id`.

DELETION / EXPIRATION: `POST /v1/sessions/{id}/clear`; TTL prune.

Standard logs do not include full transcripts.

---

## CONVERSATION STATE

PURPOSE: Follow-ups, last intent, last approved offers.

STORED: YES — in-memory.

LOCATION: `SessionStore`.

RETENTION: TTL / clear / restart.

ACCESS: Session ID.

DELETION / EXPIRATION: Same as transcripts.

---

## FEEDBACK

PURPOSE: FR-20 feedback table is planned for Phase 10.

STORED: NO. There is no `/v1/feedback` endpoint.

LOCATION: N/A.

RETENTION: N/A.

ACCESS: N/A.

DELETION / EXPIRATION: N/A.

---

## SECURITY EVENTS

PURPOSE: Authorization failures, rate limits, injection classification, admin attempts, tool denials.

STORED: YES — application logs (process stdout / future aggregator).

LOCATION: `pixel.security` / `pixel.api` / `pixel.tools` loggers.

RETENTION: **UNASSIGNED** (ops platform).

ACCESS: Deployment owner.

DELETION / EXPIRATION: **UNASSIGNED**.

Do not put secrets, passwords, or raw audio in these events.

---

## APPLICATION LOGS

PURPOSE: Turn completion metadata (session, turn, intent, status, correlation_id).

STORED: YES — logs.

LOCATION: Process logs.

RETENTION: **UNASSIGNED**.

ACCESS: Deployment owner.

DELETION / EXPIRATION: **UNASSIGNED**.

Redaction: `pixel.security.redact`.

---

## AUDIT LOGS

PURPOSE: Privileged `/admin/*` attempts (actor, timestamp, action, target, result, correlation_id).

STORED: YES — same log pipeline. Not a separate immutable store yet.

LOCATION: `record_admin_event`.

RETENTION: **UNASSIGNED**. Should be longer than application debug logs once an aggregator exists.

ACCESS: Security incident owner / deployment owner.

DELETION / EXPIRATION: **UNASSIGNED**.

---

## RAG SOURCES

PURPOSE: Grounded public Cyber Florida answers.

STORED: YES — in-memory fixture index at runtime; Postgres/pgvector when `KNOWLEDGE_STORE=postgres` and a worker/API is wired to it. HTTP `VoiceRuntime` currently uses the fixture retriever.

LOCATION: `InMemoryKnowledgeStore` / `PostgresKnowledgeStore`.

RETENTION: Until deactivated or reindexed.

ACCESS: Public retrieval is `access_class=public` only.

DELETION / EXPIRATION: `deactivate_source` removes from retrieval; chunks set inactive.

---

## Data minimization

Pixel does not persist raw audio, full model prompts, or retrieved passages in logs. Sessions keep short transcripts for follow-up quality. Do not add long-term personal memory.

## Microphone / AI communication (required themes, not legal text)

The product must eventually tell users, in Cyber Florida/USF-approved language, that:

- Pixel is an AI, not staff.
- Microphone audio is processed to produce a transcript (and may be sent to a configured STT vendor).
- Transcripts are used to answer the current conversation.
- Retention follows the approved policy (currently short-lived in-memory sessions).

Mark any public-facing wording as requiring approval before production.
