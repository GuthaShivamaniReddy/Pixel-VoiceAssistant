def admin_is_enabled(flag: bool) -> bool:
    """Admin APIs fail closed unless an explicit authenticated flag is true."""
    return bool(flag)


def mock_providers_allowed(pixel_env: str) -> bool:
    """Production must not use mock LLM/STT/TTS providers (ADR-0007)."""
    return pixel_env != "production"
