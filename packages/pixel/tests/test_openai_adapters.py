import httpx

from pixel.providers.openai import OpenAILLM, OpenAISpeechToText, OpenAITextToSpeech
from pixel.shared.cancellation import CancellationFlag
from pixel.voice import AudioBuffer
from pixel.voice.audio import sine_pcm16


def test_openai_stt_normalizes_transcript() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "Authorization" in request.headers
        assert request.headers["Authorization"].startswith("Bearer ")
        return httpx.Response(200, json={"text": "  Hello Pixel  "})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAISpeechToText("sk-test", client=client)
    events = list(
        provider.transcribe(
            AudioBuffer(pcm16le=sine_pcm16(200), sample_rate=16000),
            language="en",
            cancellation=CancellationFlag(),
        )
    )
    assert events[0].text == "Hello Pixel"
    assert events[0].is_final is True


def test_openai_llm_normalizes_completion() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Short answer."}}]},
        )

    from pixel.ai import ChatMessage, LlmRequest

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAILLM("sk-test", client=client)
    events = list(
        provider.generate(
            LlmRequest(system="sys", messages=(ChatMessage(role="user", content="Hi"),)),
            cancellation=CancellationFlag(),
        )
    )
    assert events[0].text == "Short answer."
    assert events[0].done is True


def test_openai_llm_rate_limit_is_retryable_provider_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "rate"}})

    from pixel.ai import ChatMessage, LlmRequest
    from pixel.providers.errors import ProviderError

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAILLM("sk-test", client=client)
    try:
        list(
            provider.generate(
                LlmRequest(system="sys", messages=(ChatMessage(role="user", content="Hi"),)),
                cancellation=CancellationFlag(),
            )
        )
    except ProviderError as exc:
        assert exc.category.value == "rate_limited"
        assert exc.retryable is True
    else:
        raise AssertionError("expected ProviderError")


def test_openai_tts_returns_wav_bytes() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"RIFF....WAVE")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAITextToSpeech("sk-test", client=client)
    chunks = list(provider.synthesize("Hello", voice_id="alloy", cancellation=CancellationFlag()))
    assert chunks[0].wav_bytes.startswith(b"RIFF")
    assert chunks[0].is_final is True
