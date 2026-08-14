from collections.abc import Sequence
from typing import Literal, Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    pixel_env: Literal["local", "development", "staging", "production"] = "local"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_url: str | None = None
    admin_enabled: bool = False
    llm_provider: str = "mock"
    stt_provider: str = "mock"
    tts_provider: str = "mock"
    embedding_provider: str = "mock"
    embedding_model: str = "hash-bow-v1"
    embedding_dimensions: int = 1536
    knowledge_store: str = "memory"
    retrieval_top_k: int = 5
    retrieval_min_score: float = 0.08
    openai_api_key: str = ""
    openai_stt_model: str = "whisper-1"
    openai_llm_model: str = "gpt-4o-mini"
    openai_tts_model: str = "tts-1"
    openai_tts_voice: str = "alloy"
    stt_timeout_seconds: float = 20
    llm_timeout_seconds: float = 25
    tts_timeout_seconds: float = 20
    session_ttl_seconds: float = 1800
    llm_max_attempts: int = 2
    llm_retry_backoff_seconds: float = 0.2

    @field_validator("cors_origins")
    @classmethod
    def cors_must_not_be_wildcard_with_intent(cls, value: str) -> str:
        stripped = value.strip()
        if stripped == "*":
            raise ValueError("CORS origins must be an explicit allowlist, not *")
        return stripped

    @model_validator(mode="after")
    def reject_mock_providers_in_production(self) -> Self:
        if self.pixel_env != "production":
            return self
        providers = {
            "llm_provider": self.llm_provider,
            "stt_provider": self.stt_provider,
            "tts_provider": self.tts_provider,
            "embedding_provider": self.embedding_provider,
        }
        mocked = [name for name, value in providers.items() if value.strip().lower() == "mock"]
        if mocked:
            raise ValueError("Mock providers are forbidden in production: " + ", ".join(mocked))
        return self

    def cors_origin_list(self) -> Sequence[str]:
        return tuple(origin.strip() for origin in self.cors_origins.split(",") if origin.strip())

    def allow_mock_providers(self) -> bool:
        return self.pixel_env != "production"


def get_settings() -> Settings:
    return Settings()
