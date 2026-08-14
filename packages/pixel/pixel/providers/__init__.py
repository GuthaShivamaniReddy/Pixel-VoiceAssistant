from dataclasses import dataclass

from pixel.ai import LLMProvider
from pixel.voice import SpeechToTextProvider, TextToSpeechProvider


class ProviderConfigError(ValueError):
    pass


@dataclass
class ProviderBundle:
    stt: SpeechToTextProvider
    llm: LLMProvider
    tts: TextToSpeechProvider


def build_providers(
    *,
    llm_provider: str,
    stt_provider: str,
    tts_provider: str,
    openai_api_key: str = "",
    allow_mock: bool = True,
    stt_timeout_seconds: float = 20,
    llm_timeout_seconds: float = 25,
    tts_timeout_seconds: float = 20,
    openai_stt_model: str = "whisper-1",
    openai_llm_model: str = "gpt-4o-mini",
    openai_tts_model: str = "tts-1",
) -> ProviderBundle:
    return ProviderBundle(
        stt=_build_stt(
            stt_provider,
            api_key=openai_api_key,
            allow_mock=allow_mock,
            timeout_seconds=stt_timeout_seconds,
            model=openai_stt_model,
        ),
        llm=_build_llm(
            llm_provider,
            api_key=openai_api_key,
            allow_mock=allow_mock,
            timeout_seconds=llm_timeout_seconds,
            model=openai_llm_model,
        ),
        tts=_build_tts(
            tts_provider,
            api_key=openai_api_key,
            allow_mock=allow_mock,
            timeout_seconds=tts_timeout_seconds,
            model=openai_tts_model,
        ),
    )


def _require_key(name: str, api_key: str) -> str:
    if not api_key.strip():
        raise ProviderConfigError(f"{name} requires OPENAI_API_KEY on the server")
    return api_key.strip()


def _build_stt(
    name: str,
    *,
    api_key: str,
    allow_mock: bool,
    timeout_seconds: float,
    model: str,
) -> SpeechToTextProvider:
    key = name.strip().lower()
    if key == "mock":
        if not allow_mock:
            raise ProviderConfigError("Mock STT is forbidden in this environment")
        from pixel.providers.mock import MockSpeechToText

        return MockSpeechToText()
    if key == "openai":
        from pixel.providers.openai import OpenAISpeechToText

        return OpenAISpeechToText(
            _require_key("STT", api_key),
            model=model,
            timeout_seconds=timeout_seconds,
        )
    raise ProviderConfigError(f"Unknown STT provider: {name}")


def _build_llm(
    name: str,
    *,
    api_key: str,
    allow_mock: bool,
    timeout_seconds: float,
    model: str,
) -> LLMProvider:
    key = name.strip().lower()
    if key == "mock":
        if not allow_mock:
            raise ProviderConfigError("Mock LLM is forbidden in this environment")
        from pixel.providers.mock import MockLLM

        return MockLLM()
    if key == "openai":
        from pixel.providers.openai import OpenAILLM

        return OpenAILLM(
            _require_key("LLM", api_key),
            model=model,
            timeout_seconds=timeout_seconds,
        )
    raise ProviderConfigError(f"Unknown LLM provider: {name}")


def _build_tts(
    name: str,
    *,
    api_key: str,
    allow_mock: bool,
    timeout_seconds: float,
    model: str,
) -> TextToSpeechProvider:
    key = name.strip().lower()
    if key == "mock":
        if not allow_mock:
            raise ProviderConfigError("Mock TTS is forbidden in this environment")
        from pixel.providers.mock import MockTextToSpeech

        return MockTextToSpeech()
    if key == "openai":
        from pixel.providers.openai import OpenAITextToSpeech

        return OpenAITextToSpeech(
            _require_key("TTS", api_key),
            model=model,
            timeout_seconds=timeout_seconds,
        )
    raise ProviderConfigError(f"Unknown TTS provider: {name}")
