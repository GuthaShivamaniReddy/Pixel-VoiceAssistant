# Pixel — Conversation UX

**Status:** Phase 3 UI, Phase 4 voice loop, Phase 5 server orchestrator.  
**Voice details:** `docs/voice.md`. **Orchestrator:** `docs/orchestrator.md`.

User-visible states follow `product.md` §20. Finer architecture states (`TRANSCRIBING`, `THINKING`, `RETRIEVING`) map to **PROCESSING**.

---

## State model

```text
IDLE → LISTENING → PROCESSING → SPEAKING → IDLE
IDLE → PROCESSING              (text submit)
LISTENING → IDLE               (cancel)
PROCESSING → IDLE              (cancel)
SPEAKING → IDLE                (stop / mute-skip / finish)
* → ERROR / PERMISSION_DENIED
ERROR → IDLE
PERMISSION_DENIED → IDLE or PROCESSING (text still works)
```

Pixel never shows listening, processing, and speaking at the same time.

`CANCELLED` is a short status announcement, then IDLE. It is not a lingering mode.

---

## Mock conversation

The live app uses `POST /v1/turns` and the server orchestrator. `apps/web/src/conversation/mock-provider.ts` remains for frontend unit tests only.

Deterministic phrases (case-insensitive):

| User says | Behavior |
|---|---|
| What is Cyber Florida? | Short identity + **mock** about-page source card |
| What cybersecurity programs are available? | High-level public programs + mock sources/actions |
| Explain phishing. | Beginner defensive definition (no org RAG required) |
| I clicked a suspicious link. | Containment steps; escalate to work IT |
| Show me the source. | Repeat last mock sources or say none |
| Tell me more. | Expand last topic, still 1–4 spoken sentences |
| simulate network error | ERROR (network) |
| simulate response failure | ERROR (response) |
| simulate timeout | ERROR (timeout) |
| simulate empty | ERROR (empty) |

Unknown questions get a bounded, non-invented reply (Pixel does not fabricate Cyber Florida facts).

Listening captures real PCM (push-to-talk). Stopping listen sends audio to `WS /v1/realtime` for STT. Empty/silent audio returns to IDLE without an LLM call.

---

## Microphone

Permission: unknown → granted | denied | unavailable.

Audio tracks are captured in the browser and streamed as PCM to the Pixel API. They are stopped on cancel/stop/unmount.

Denied: app stays usable via text. Mic is not re-requested in a loop.

---

## Mute / Stop / Cancel / Clear

| Control | Phase 3 meaning |
|---|---|
| Stop (listening) | End listen; send captured audio for STT |
| Stop (speaking) | Stop playback; keep transcript; IDLE |
| Mute | Skip/stop audible playback; transcript still shown |
| Cancel | Abort listen/processing/playback; ignore late turn results; IDLE |
| Clear | Confirm, drop visible transcript and server short-term context (`POST /v1/sessions/{id}/clear`), IDLE |

---

## How to try it

```bash
npm install
npm run web:dev
```

Open http://localhost:3000. The banner states that the conversation is mocked.

```bash
npm run web:test
npm run web:e2e
npm run web:build
```

---

## Phase 4 notes

See `docs/voice.md`. Text fallback still uses `POST /v1/turns`. Barge-in from speaking/processing starts a new listen after cancelling playback and the active turn id.
