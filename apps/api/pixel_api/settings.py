from collections.abc import Sequence
from typing import Literal, Self

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from pixel.security.kill_switch import KillSwitch, parse_disabled_tools


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    pixel_env: Literal["local", "development", "staging", "production"] = "local"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_url: str | None = None
    admin_enabled: bool = False
    admin_token: str = ""
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
    openai_tts_voice: str = Field(
        default="nova",
        validation_alias=AliasChoices("PIXEL_TTS_VOICE", "OPENAI_TTS_VOICE", "openai_tts_voice"),
    )
    stt_timeout_seconds: float = 20
    llm_timeout_seconds: float = 25
    tts_timeout_seconds: float = 20
    session_ttl_seconds: float = 1800
    llm_max_attempts: int = 2
    llm_retry_backoff_seconds: float = 0.2
    tool_timeout_seconds: float = 5
    max_tool_calls_per_turn: int = 2
    max_user_chars: int = 4000
    max_request_bytes: int = 65536
    max_ws_control_bytes: int = 8192
    rate_limit_enabled: bool = True
    rate_limit_session_per_minute: int = 30
    rate_limit_turn_per_minute: int = 120
    rate_limit_turn_per_session_per_minute: int = 60
    rate_limit_ws_per_minute: int = 30
    rate_limit_admin_per_minute: int = 20
    trust_proxy: bool = False
    hsts_enabled: bool | None = None
    tools_enabled: bool = True
    disabled_tools: str = ""
    side_effecting_tools_enabled: bool = True
    llm_enabled: bool = True
    stt_enabled: bool = True
    tts_enabled: bool = True
    knowledge_enabled: bool = True

    @field_validator("openai_tts_voice")
    @classmethod
    def tts_voice_must_be_approved(cls, value: str) -> str:
        allowed = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
        cleaned = value.strip().lower() or "nova"
        if cleaned not in allowed:
            return "nova"
        return cleaned

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
        if self.admin_enabled and len(self.admin_token.strip()) < 32:
            raise ValueError(
                "ADMIN_TOKEN must be at least 32 characters when ADMIN_ENABLED in production"
            )
        return self

    def cors_origin_list(self) -> Sequence[str]:
        return tuple(origin.strip() for origin in self.cors_origins.split(",") if origin.strip())

    def allow_mock_providers(self) -> bool:
        return self.pixel_env != "production"

    def use_hsts(self) -> bool:
        if self.hsts_enabled is not None:
            return self.hsts_enabled
        return self.pixel_env == "production"

    def kill_switch(self) -> KillSwitch:
        return KillSwitch(
            tools_enabled=self.tools_enabled,
            disabled_tools=parse_disabled_tools(self.disabled_tools),
            side_effecting_tools_enabled=self.side_effecting_tools_enabled,
            llm_enabled=self.llm_enabled,
            stt_enabled=self.stt_enabled,
            tts_enabled=self.tts_enabled,
            knowledge_enabled=self.knowledge_enabled,
        )


def get_settings() -> Settings:
    return Settings()
