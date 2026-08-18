import logging

from pixel.security.filenames import safe_basename
from pixel.security.kill_switch import KillSwitch
from pixel.security.limits import InProcessRateLimiter, client_ip
from pixel.security.redact import RedactingFilter, redact


def test_redact_synthetic_secrets() -> None:
    raw = (
        "password=TEST_PASSWORD_123 Authorization: Bearer test-token-value "
        "OPENAI_API_KEY=sk-test-not-real otp 123456 "
        "postgresql://pixel:secret@localhost:5432/pixel"
    )
    cleaned = redact(raw)
    assert "TEST_PASSWORD_123" not in cleaned
    assert "test-token-value" not in cleaned
    assert "sk-test-not-real" not in cleaned
    assert "123456" not in cleaned
    assert "postgresql://pixel:secret" not in cleaned
    assert "[REDACTED]" in cleaned or "[REDACTED_KEY]" in cleaned


def test_redacting_filter_strips_log_args() -> None:
    record = logging.LogRecord(
        name="pixel.api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="auth %s",
        args=("Bearer test-token-value",),
        exc_info=None,
    )
    assert RedactingFilter().filter(record) is True
    formatted = record.getMessage()
    assert "test-token-value" not in formatted


def test_in_process_limiter_allows_then_blocks() -> None:
    limiter = InProcessRateLimiter()
    assert limiter.check("k", limit=2)[0] is True
    assert limiter.check("k", limit=2)[0] is True
    allowed, retry_after = limiter.check("k", limit=2)
    assert allowed is False
    assert retry_after >= 1


def test_client_ip_ignores_forwarded_without_trust() -> None:
    assert (
        client_ip("127.0.0.1", forwarded="203.0.113.9, 10.0.0.1", trust_proxy=False) == "127.0.0.1"
    )
    assert client_ip("127.0.0.1", forwarded="203.0.113.9", trust_proxy=True) == "203.0.113.9"


def test_path_traversal_filenames_rejected() -> None:
    for name in ("../../secret.txt", "../config.env", r"..\..\windows-file", "a/b.txt"):
        try:
            safe_basename(name)
        except ValueError as exc:
            assert "invalid_filename" in str(exc)
        else:
            raise AssertionError(name)


def test_safe_basename_accepts_plain_name() -> None:
    assert safe_basename("policy.pdf") == "policy.pdf"


def test_kill_switch_blocks_named_and_side_effecting_tools() -> None:
    switch = KillSwitch(disabled_tools=frozenset({"navigate_to_url"}))
    assert switch.tool_allowed("find_program", side_effect_level="none") is True
    assert switch.tool_allowed("navigate_to_url", side_effect_level="navigation") is False
    blocked = KillSwitch(side_effecting_tools_enabled=False)
    assert blocked.tool_allowed("navigate_to_url", side_effect_level="navigation") is False
    assert blocked.tool_allowed("find_program", side_effect_level="none") is True
    off = KillSwitch(tools_enabled=False)
    assert off.tool_allowed("find_program", side_effect_level="none") is False
