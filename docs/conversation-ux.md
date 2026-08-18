# Pixel — Conversation UX

**Status:** Phase 9 product polish on the Phase 3–7 conversation, voice, orchestrator, RAG, and tool UI.  
**Voice details:** `docs/voice.md`. **Orchestrator:** `docs/orchestrator.md`.

User-visible states follow `product.md` §20. Finer architecture states (`TRANSCRIBING`, `THINKING`, `RETRIEVING`) map to **PROCESSING**. Searching animation is shown only when the client has a live retrieval-started signal.

---

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

## Mascot (presentation only)

`PixelMascot` renders an original 64×96 shaded SVG Pixel (`PixelCharacter.tsx`) on a small digital stage (`PixelStage.tsx`). Motion is CSS on independently grouped body parts. The supplied reference photo is inspiration only and is not loaded. The mascot must not change voice, RAG, or tool behavior.

Phase 9 keeps Pixel as a central product element: Cyber Florida greens, a restrained digital stage, compact mascot once conversation starts, and text labels for every state. Searching, speaking, and tool poses stay tied to real events. Mic level and TTS mouth motion write CSS variables instead of React state on every animation frame.

Live mapping today:

| Assistant | Mascot |
|---|---|
| idle | idle (greeting run-in once on empty page) |
| listening | listening |
| processing | thinking |
| speaking | speaking / reading if sources / toolAction if actions — only while TTS audio is playing |
| error + network | offline |
| error / permission denied | error |
| retry from error | recovering (short cue, then idle) |
| muted + idle | muted |
| clear conversation | clearing (feedback only; data clears immediately) |

`searching` is implemented in the mapper but stays unused until the client receives a live retrieval-started signal. Do not show searching during generic processing.

Assets: original character in `apps/web/src/mascot/PixelCharacter.tsx`. The supplied PNG is reference-only and is not loaded by the UI.

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

## Welcome, empty state, and transcript

The first screen shows Meet Pixel, Cyber Florida's AI Assistant, voice and text, and that Pixel is not listening until you start. An empty transcript offers four approved starter questions from `product.md`. After the first turn, the hero compactifies and Pixel shrinks so conversation, sources, actions, and controls stay first.

Transcript turns distinguish You vs Pixel. Pixel replies may show **Sources** and **Next step**. Security-sensitive replies use a calm warning kicker (warning signs, not a verdict). Unverified replies use a separate uncertainty treatment, not the error panel. The transcript auto-scrolls when the user is near the bottom and offers Jump to latest otherwise.

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

Open http://localhost:3000. Pixel is not listening until you start. Starter questions and text both use the live Pixel API.

```bash
npm run web:test
npm run web:e2e
npm run web:build
```

---

## Phase 4 notes

See `docs/voice.md`. Text fallback still uses `POST /v1/turns`. Barge-in from speaking/processing starts a new listen after cancelling playback and the active turn id.
