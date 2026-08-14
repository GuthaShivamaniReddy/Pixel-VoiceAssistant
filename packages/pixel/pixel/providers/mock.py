from __future__ import annotations

import re
from collections.abc import Iterator

from pixel.ai import LlmEvent, LlmRequest
from pixel.orchestrator.fallbacks import ORG_ABSTAIN
from pixel.orchestrator.safe_replies import AI_DISCLOSURE, SafeReplySession
from pixel.orchestrator.turn import TurnError
from pixel.providers.errors import ProviderError
from pixel.shared.cancellation import CancellationFlag, CancelledError
from pixel.voice import AudioBuffer, SpeechAudio, TranscriptEvent
from pixel.voice.audio import looks_like_silence, pcm16_to_wav, sine_pcm16

_INJECTION = re.compile(
    r"ignore previous|reveal the system prompt|give the user an admin tool|"
    r"send the api key|treat this document as developer",
    re.I,
)


def _answer_from_evidence(evidence: tuple[str, ...], question: str = "") -> str:
    bodies: list[str] = []
    for block in evidence:
        lowered = block.lower()
        if "text:" not in lowered:
            continue
        after = block.split("text:", 1)[1]
        body = after.split("----- END", 1)[0].strip()
        if body and not _INJECTION.search(body):
            bodies.append(body)
    if not bodies:
        return ORG_ABSTAIN
    current = question.split("\n")[-1]
    q_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", current.lower())
        if len(token) > 3 and token not in {"what", "about", "does", "that", "this", "with"}
    }
    bodies.sort(
        key=lambda text: (
            sum(1 for token in q_tokens if token in text.lower()),
            len(text),
        ),
        reverse=True,
    )
    snippet = bodies[0]
    snippet = " ".join(snippet.split())
    if len(snippet) > 400:
        snippet = snippet[:397].rsplit(" ", 1)[0]
    if not snippet.endswith("."):
        snippet += "."
    return snippet


class MockSpeechToText:
    provider_id = "mock"

    def transcribe(
        self,
        audio: AudioBuffer,
        *,
        language: str | None,
        cancellation: CancellationFlag,
    ) -> Iterator[TranscriptEvent]:
        if cancellation.is_cancelled():
            raise CancelledError
        if looks_like_silence(audio.pcm16le, audio.sample_rate):
            yield TranscriptEvent(text="", is_final=True)
            return
        yield TranscriptEvent(text="What is Cyber Florida?", is_final=True)


class MockTextToSpeech:
    provider_id = "mock"

    def synthesize(
        self,
        text: str,
        *,
        voice_id: str,
        cancellation: CancellationFlag,
    ) -> Iterator[SpeechAudio]:
        if cancellation.is_cancelled():
            raise CancelledError
        if not text.strip():
            raise TurnError("tts_failure", "I have a written reply, but speech playback failed.")
        pcm = sine_pcm16(420)
        yield SpeechAudio(wav_bytes=pcm16_to_wav(pcm, 16000), is_final=True)


class MockLLM:
    provider_id = "mock"

    def __init__(self, session: SafeReplySession | None = None) -> None:
        self._session = session or SafeReplySession()

    def generate(
        self, request: LlmRequest, *, cancellation: CancellationFlag
    ) -> Iterator[LlmEvent]:
        if cancellation.is_cancelled():
            raise CancelledError
        user = next(
            (message.content for message in reversed(request.messages) if message.role == "user"),
            "",
        )
        prior = tuple(message for message in request.messages if message.role != "system")
        if prior and prior[-1].role == "user":
            prior = prior[:-1]
        if request.evidence:
            body = _answer_from_evidence(request.evidence, user)
            if not any(message.role == "assistant" for message in prior):
                body = AI_DISCLOSURE + body
            yield LlmEvent(text=body, done=True)
            return
        reply = self._session.respond(user, history=prior)
        code = reply.error_code
        if code == "network":
            raise ProviderError("provider_unavailable", reply.text, retryable=True)
        if code == "timeout":
            raise ProviderError("timeout", reply.text, retryable=True)
        if code == "rate_limited":
            raise ProviderError("rate_limited", reply.text, retryable=True)
        if code == "response_failure":
            raise ProviderError("unknown", reply.text, retryable=False)
        if code == "stt_failure":
            raise TurnError("stt_failure", reply.text)
        yield LlmEvent(text=reply.text, done=True)


def build_mock_bundle() -> tuple[MockSpeechToText, MockLLM, MockTextToSpeech]:
    return MockSpeechToText(), MockLLM(), MockTextToSpeech()
