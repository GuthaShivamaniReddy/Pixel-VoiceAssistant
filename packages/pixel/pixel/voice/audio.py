from __future__ import annotations

import array
import math
import struct

PCM16_MAX = 32767


def pcm16_to_wav(pcm16le: bytes, sample_rate: int) -> bytes:
    data_size = len(pcm16le)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        sample_rate,
        sample_rate * 2,
        2,
        16,
        b"data",
        data_size,
    )
    return header + pcm16le


def wav_duration_ms(pcm16le: bytes, sample_rate: int) -> int:
    if sample_rate <= 0:
        return 0
    samples = len(pcm16le) // 2
    return int(round(samples / sample_rate * 1000))


def pcm16_rms(pcm16le: bytes) -> float:
    usable = pcm16le[: len(pcm16le) // 2 * 2]
    if not usable:
        return 0.0
    samples = array.array("h")
    samples.frombytes(usable)
    total = sum(int(sample) * int(sample) for sample in samples)
    return math.sqrt(total / len(samples))


def sine_pcm16(duration_ms: int, sample_rate: int = 16000, hz: float = 440.0) -> bytes:
    n = max(1, int(sample_rate * duration_ms / 1000))
    samples = array.array("h")
    for index in range(n):
        value = int(0.18 * PCM16_MAX * math.sin(2 * math.pi * hz * index / sample_rate))
        samples.append(value)
    return samples.tobytes()


def speechish_pcm16(text: str, sample_rate: int = 16000, hz: float = 196.0) -> bytes:
    """Audible mock speech with short pauses so the mascot mouth can close."""
    words = max(1, len((text or "ok").split()))
    duration_ms = min(5500, max(900, words * 70))
    n = max(1, int(sample_rate * duration_ms / 1000))
    cycle = max(1, int(sample_rate * 0.42))
    pause = max(1, int(sample_rate * 0.07))
    samples = array.array("h")
    for index in range(n):
        pos = index % cycle
        if pos > cycle - pause:
            envelope = 0.0
        elif pos > cycle - pause * 2:
            envelope = 0.05
        else:
            envelope = 0.16
        value = int(envelope * PCM16_MAX * math.sin(2 * math.pi * hz * index / sample_rate))
        samples.append(value)
    return samples.tobytes()


def looks_like_silence(pcm16le: bytes, sample_rate: int, min_ms: int = 180) -> bool:
    if wav_duration_ms(pcm16le, sample_rate) < min_ms:
        return True
    return pcm16_rms(pcm16le) < 120.0
