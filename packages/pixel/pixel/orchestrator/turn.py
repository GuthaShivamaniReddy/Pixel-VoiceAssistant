from __future__ import annotations

from dataclasses import dataclass, field


class TurnError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class StageTimings:
    time_to_transcript_ms: int | None = None
    model_latency_ms: int | None = None
    tts_latency_ms: int | None = None
    time_to_first_audio_ms: int | None = None
    total_turn_latency_ms: int | None = None
    retrieval_latency_ms: int | None = None


@dataclass
class TurnResult:
    transcript: str
    reply_text: str
    wav_bytes: bytes | None
    sources: list[dict[str, str]] = field(default_factory=list)
    actions: list[dict[str, str]] = field(default_factory=list)
    citations: list[dict[str, str]] = field(default_factory=list)
    timings: StageTimings = field(default_factory=StageTimings)
    error_code: str | None = None
    error_message: str | None = None
    intent: str | None = None
    policy_version: str = ""
    status: str = "ok"
