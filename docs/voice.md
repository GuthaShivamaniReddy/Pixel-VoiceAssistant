# Pixel — Voice loop (Phase 4)

**Status:** Implemented. This describes the running path, not a future design.

## Transport

HTTPS REST + WebSocket, push-to-talk (ADR-0003). WebRTC is not used.

| Path | Role |
|---|---|
| `POST /v1/turns` | Text turn → orchestrator → optional TTS WAV |
| `POST /v1/sessions` | Create short-lived conversation session |
| `POST /v1/sessions/{id}/clear` | Clear short-term context |
| `WS /v1/realtime` | PTT audio PCM → STT → same orchestrator → TTS WAV bytes |

The browser never receives `OPENAI_API_KEY`. Long-lived provider credentials stay on the API.

## Turn detection

Explicit push-to-talk: **Start listening** opens the microphone; **Stop** ends the turn and sends PCM. Listening is not shown unless capture actually started.

Silence (short/quiet audio) does not call the LLM.

## Providers

Core code depends on `SpeechToTextProvider`, `LLMProvider`, and `TextToSpeechProvider` in `packages/pixel`.

| `STT_PROVIDER` / `LLM_PROVIDER` / `TTS_PROVIDER` | Adapter |
|---|---|
| `openai` | Whisper, Chat Completions, TTS (`tts-1`) via server-side httpx |
| `mock` | Local fixture STT/LLM/TTS for development and CI (forbidden in production) |

Mock STT does **not** decode speech. If enough audio is captured it returns a fixture transcript (`What is Cyber Florida?`) so the loop can be tested without a paid key. Set `STT_PROVIDER=openai` and `OPENAI_API_KEY` for real transcription.

Mock TTS returns a short generated WAV so playback, barge-in, and Stop are real audio operations.

## Barge-in and cancellation

While Pixel is speaking or processing, **Start listening** stops playback, clears the queue, cancels the active turn id, and starts a new capture.

Late WebSocket/HTTP results for a cancelled `turn_id` are ignored.

Stop during speaking stops playback immediately. Cancel aborts listen/processing/speaking.

## Mute

Mute skips audible playback. The transcript still appears. If mute is turned on while speaking, playback stops and Pixel returns to idle. TTS may still be generated for unmuted text turns (`speak: false` when already muted).

## Latency

Each turn records `time_to_transcript_ms`, `model_latency_ms`, `tts_latency_ms`, `time_to_first_audio_ms`, and `total_turn_latency_ms` (plus `session_id` / `turn_id` / `correlation_id` on REST). Pixel turns show a “Turn timing” disclosure.

## Privacy

- Raw microphone PCM is sent to the Pixel API over the local WebSocket, then to the configured STT provider.
- Pixel does not persist raw audio or transcripts to disk in Phase 4 (in-memory session history only, bounded).
- Logs include session/turn ids and error codes, not audio bytes or API keys.

## Limitations

- No VAD / hands-free end-of-speech.
- RAG uses the approved fixture index (see `docs/knowledge.md`). Live vendor embeddings are optional.
- OpenAI adapters do not abort an in-flight HTTP call; Pixel stops consuming the result after cancel.
- Browser WebSocket origin must match `CORS_ORIGINS`.
