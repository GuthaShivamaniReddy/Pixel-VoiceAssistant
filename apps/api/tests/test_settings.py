import pytest
from pydantic import ValidationError

from pixel_api.settings import Settings


def test_wildcard_cors_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins="*")


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
