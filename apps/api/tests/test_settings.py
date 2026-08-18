import pytest
from pydantic import ValidationError

from pixel_api.settings import Settings


def test_wildcard_cors_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins="*")


def test_production_admin_requires_long_token() -> None:
    with pytest.raises(ValidationError):
        Settings(
            pixel_env="production",
            llm_provider="openai",
            stt_provider="openai",
            tts_provider="openai",
            embedding_provider="openai",
            admin_enabled=True,
            admin_token="short",
        )


def test_mock_providers_blocked_in_production() -> None:
    with pytest.raises(ValidationError):
        Settings(pixel_env="production")
    settings = Settings(
        pixel_env="production",
        llm_provider="openai",
        stt_provider="openai",
        tts_provider="openai",
        embedding_provider="openai",
    )
    assert settings.allow_mock_providers() is False


def test_default_pixel_voice_is_nova() -> None:
    settings = Settings(pixel_env="local")
    assert settings.openai_tts_voice == "nova"


def test_unknown_tts_voice_falls_back_to_nova() -> None:
    settings = Settings(openai_tts_voice="cartoon-robot")
    assert settings.openai_tts_voice == "nova"
