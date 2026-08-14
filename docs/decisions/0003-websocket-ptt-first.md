# ADR-0003: WebSocket and push-to-talk before WebRTC

- Status: Accepted (implemented in Phase 4: `WS /v1/realtime` + PTT)
- Date: 2026-08-14
- Deciders: engineering

## Context

The specification allows WebRTC for low-latency bidirectional audio and WebSocket for simpler streaming/control. The first vertical slice must prove mic → STT → answer → TTS → barge-in.

## Decision

MVP realtime path: HTTPS REST + WebSocket audio/control frames, with explicit push-to-talk (and later optional VAD). Isolate the client behind `VoiceSession`. Add WebRTC only if measured latency requires it.

## Consequences

Faster path to a working loop; possibly higher latency than WebRTC for always-on conversation. Migration is confined to the voice transport adapter.

## Alternatives considered

- WebRTC-first (LiveKit/Pipecat): more moving parts before PTT works.
- Full-turn MediaRecorder upload: simpler but weaker streaming/barge-in.
