from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pixel.shared.cancellation import CancellationFlag

CancellationToken = CancellationFlag


@dataclass(frozen=True)
class AudioBuffer:
    pcm16le: bytes
    sample_rate: int


@dataclass(frozen=True)
class TranscriptEvent:
    text: str
    is_final: bool


@dataclass(frozen=True)
class SpeechAudio:
    wav_bytes: bytes
    is_final: bool


@runtime_checkable
class SpeechToTextProvider(Protocol):
    provider_id: str

    def transcribe(
        self,
        audio: AudioBuffer,
        *,
        language: str | None,
        cancellation: CancellationFlag,
    ) -> Iterator[TranscriptEvent]: ...


@runtime_checkable
class TextToSpeechProvider(Protocol):
    provider_id: str

    def synthesize(
        self,
        text: str,
        *,
        voice_id: str,
        cancellation: CancellationFlag,
    ) -> Iterator[SpeechAudio]: ...


__all__ = [
    "AudioBuffer",
    "CancellationFlag",
    "CancellationToken",
    "SpeechAudio",
    "SpeechToTextProvider",
    "TextToSpeechProvider",
    "TranscriptEvent",
]
