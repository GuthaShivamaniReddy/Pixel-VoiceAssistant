# Pixel — Data Flow

**Document status:** Phase 0 (Architecture / Planning)  
**Code status:** Not implemented. Flows describe the intended production path.

State names match `ARCHITECTURE.md` §9. Security wrapping matches `SECURITY.md`.

---

## 1. Voice conversation

```
Microphone
  → Audio frames
  → VAD / push-to-talk boundary
  → STT
  → Transcript
  → AI (conversation manager → orchestrator → safety)
  → RAG / Tools (when allowed)
  → Grounded response
  → Response validation
  → TTS
  → Playback
```

### 1.1 Step-by-step

| Step | State | Data in motion | Trust |
|---|---|---|---|
| 1. User grants mic and starts listen | IDLE → LISTENING | MediaStream in the browser only | User-initiated |
| 2. Client captures PCM/Opus frames | LISTENING | Audio chunks over `WS /v1/realtime` with `conversation_id` + `message_id` | Authenticated by session token; TLS |
| 3. VAD or PTT release ends the user turn | LISTENING → TRANSCRIBING | `endTurn` event; client stops sending | — |
| 4. `SpeechToTextProvider.transcribe` | TRANSCRIBING | Audio → partial/final text. **Audio discarded after STT** (PRIV-01) | STT output is untrusted user text |
| 5. Conversation manager stores user `messages.content` | THINKING | Bounded transcript, `input_mode=voice` | Size-limited; no raw audio column |
| 6. Safety / policy on user text | THINKING | Jailbreak, secret-solicitation, harmful-cyber checks | User text untrusted |
| 7. Orchestrator routes intent | THINKING or RETRIEVING | Enum: knowledge, cyber help, scam help, navigation, clarification, unsupported | Server-side |
| 8. RAG and/or tools | RETRIEVING | See §3 and §5 | Retrieved text **untrusted**; tools allowlisted |
| 9. `LLMProvider.generate` | THINKING | System policy + history + **evidence bundle as data** | Model untrusted until validated |
| 10. Response validation | THINKING | Citations, leakage, policy, tool echo | Fail closed → fallback utterance |
| 11. Persist assistant message + `source_refs` | THINKING → SPEAKING | Text, timings, provider versions | — |
| 12. `TextToSpeechProvider.synthesize` | SPEAKING | Validated text → audio chunks to client | Do not persist TTS audio |
| 13. Client playback queue | SPEAKING | Speakers + transcript + source cards | XSS: treat text as text, not HTML |
| 14. Playback complete | SPEAKING → IDLE | — | — |

### 1.2 Barge-in

```
SPEAKING | THINKING | RETRIEVING | TRANSCRIBING
  → user stop / new speech
  → INTERRUPTED
  → cancel TTS playback
  → cancel in-flight LLM/STT
  → mark message status=cancelled
  → LISTENING or THINKING (if text queued) or IDLE
```

Cancellation must be honored by provider adapters (`CancellationToken`). Orphan audio chunks are dropped.

### 1.3 Partial transcripts

Partials may render in the UI and are not durable until `final`. Only the final transcript is stored on `messages`.

---

## 2. Text conversation

```
Text
  → API (POST /v1/messages or WS text event)
  → Conversation manager
  → Safety / policy
  → AI orchestrator
  → RAG / Tools
  → LLM
  → Response validation
  → Streamed text to UI
  → optional TTS
  → Playback (if speak-enabled)
```

| Difference vs voice | Rule |
|---|---|
| No mic, VAD, STT | `IDLE` → `THINKING` |
| Same orchestrator | Do not maintain a second “chat” pipeline |
| TTS optional | User may mute Pixel; transcript still required (FR-30) |
| Same RAG trust rules | Identical evidence wrapping |

---

## 3. Knowledge ingestion

```
Source (allowlisted URL or uploaded approved file)
  → Extract
  → Clean
  → Chunk
  → Metadata
  → Embedding
  → Vector store
  → Retrieval
```

### 3.1 Ingestion pipeline

| Stage | Input | Output | Notes |
|---|---|---|---|
| Register | Admin request | `knowledge_documents` row + `ingestion_jobs` | Authz required; allowlist only |
| Fetch | `source_url` | Raw bytes/HTML | Server-side fetch; timeout; no user-supplied SSRF targets outside allowlist |
| Extract | HTML/PDF/DOCX/text | Title, main text, headings, canonical URL, dates | Strip nav/boilerplate; keep meaning |
| Clean | Extracted text | Normalized text | Do not execute scripts; strip injected “system: ignore previous” is **not** sufficient alone — trust is enforced at prompt assembly |
| Hash | Normalized document | `content_hash` | Skip re-embed if unchanged |
| Chunk | Clean text + headings | Chunks with `section`, `ordinal` | Semantic / heading-aware; stable `chunk_id` where possible |
| Metadata | Document + chunk | See §3.2 | All required RAG fields |
| Embed | Chunk text | Vector | `EmbeddingProvider`; model id stored with index generation |
| Upsert | Chunks + vectors | `knowledge_chunks` | `VectorStoreProvider.upsert_chunks` |
| Activate | Successful job | `status=active`, `indexed_at` | Previous chunks for that document deactivated/deleted first |

Failed jobs leave the previous **active** index in place (no half-cutover).

### 3.2 Metadata written per chunk

Required: `document_id`, `chunk_id`, `title`, `source_url`, `section`, `content_type`, `published_at`, `updated_at`, `indexed_at`, `content_hash`.

### 3.3 Retrieval-time flow (subset of voice/text)

```
User question + resolving context
  → query rewrite (optional, server-side)
  → embed query
  → vector search + metadata filters (active, access_class)
  → scored chunks
  → optional rerank (after baseline)
  → evidence bundle (untrusted)
  → LLM
  → citations in UI (`source_url`, `title`, `section`)
```

If top results are below a relevance threshold or empty: orchestrator instructs abstention for org-specific facts (FR-27).

### 3.4 Delete / stale

```
Source marked inactive or removed
  → ingestion job type=delete
  → chunks is_active=false or deleted
  → they must not be retrieved
```

---

## 4. Safety and policy data path

```
User text (and later, model output)
  → input size limit + charset normalization
  → prompt-injection / jailbreak heuristics + policy
  → orchestrator
  → (RAG text isolated in evidence tags)
  → LLM
  → output validation
  → user
```

Retrieved chunk **content** is placed in a clearly delimited untrusted channel, for example:

- System: Pixel policy (versioned, from server files, not from DB content).
- Developer: tool schemas Pixel already authorized.
- Untrusted evidence: titles, URLs, chunk text.
- User: current transcript.

No pipeline may “promote” a chunk into the system channel.

---

## 5. Tool / action flow

```
Orchestrator proposes tool name + arguments
  → schema validate
  → authorization + allowlist
  → confirmation if side-effecting (FR-18)
  → execute on server
  → tool_executions row
  → sanitized result back to orchestrator
  → never raw privileged payloads to the model or browser
```

Phase 7 tools: `navigate_to_url` (registered canonical HTTPS URLs only), `find_program`, `find_resource`, `search_approved_content`. No generic HTTP, shell, or database tool.

---

## 6. Error and offline flows

| Failure | User-visible path | Data |
|---|---|---|
| Mic denied | Stay IDLE; offer text | No audio sent |
| Silence | TRANSCRIBING → IDLE | No empty user message persisted (or persist nothing useful) |
| STT error | ERROR → text retry | `messages.status=error`, `error_code` |
| LLM timeout | Fallback sentence; ERROR or SPEAKING of fallback | timings recorded |
| Retrieval empty | Abstain if org-specific | no fake sources |
| TTS error | Show text; optional ERROR | assistant text already stored |
| Network drop | OFFLINE | stop sending audio |
| Tool denied | Conversational refusal | `tool_executions.permission=denied` |

---

## 7. Observability data path

```
Client creates message_id
  → sent with every WS/REST event
  → API binds conversation_id + message_id
  → adapters record stage duration
  → logs/metrics/traces with ids, not default body content
```

Analytics (FR-23) use counters and timings. They do not require a second copy of conversations.

---

## 8. What must not flow

| Data | Must not go to |
|---|---|
| Provider API keys | Browser, logs, `messages` |
| Raw microphone audio | Database (default), analytics, LLM |
| Retrieved text | System prompt channel, tool permission grants |
| Passwords / OTPs | Any store, log, or prompt (user asked not to send; redact if seen) |
| Internal knowledge chunks | Anonymous public sessions |
| Stack traces | Client error payloads |
