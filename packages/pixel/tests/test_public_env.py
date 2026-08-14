from pixel.shared import FORBIDDEN_PUBLIC_SUBSTRINGS, PUBLIC_ENV_PREFIX


def public_env_key_is_safe(name: str) -> bool:
    if not name.startswith(PUBLIC_ENV_PREFIX):
        return True
    upper = name.upper()
    return not any(part in upper for part in FORBIDDEN_PUBLIC_SUBSTRINGS)


def test_public_api_base_is_safe() -> None:
    assert public_env_key_is_safe("NEXT_PUBLIC_API_BASE_URL")


def test_secret_shaped_public_keys_are_rejected() -> None:
    assert not public_env_key_is_safe("NEXT_PUBLIC_OPENAI_API_KEY")
    assert not public_env_key_is_safe("NEXT_PUBLIC_PROVIDER_TOKEN")
