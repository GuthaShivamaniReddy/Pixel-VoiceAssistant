from pixel.orchestrator.retry import call_with_retry
from pixel.providers.errors import ProviderError
from pixel.shared.cancellation import CancellationFlag, CancelledError


def test_retries_retryable_then_succeeds() -> None:
    calls = {"n": 0}

    def operation() -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            raise ProviderError("timeout", "temp", retryable=True)
        return "ok"

    assert (
        call_with_retry(
            operation, cancellation=CancellationFlag(), max_attempts=2, backoff_seconds=0
        )
        == "ok"
    )
    assert calls["n"] == 2


def test_does_not_retry_auth_failure() -> None:
    calls = {"n": 0}

    def operation() -> str:
        calls["n"] += 1
        raise ProviderError("authentication_error", "nope", retryable=False)

    try:
        call_with_retry(
            operation, cancellation=CancellationFlag(), max_attempts=3, backoff_seconds=0
        )
    except ProviderError as exc:
        assert exc.category.value == "authentication_error"
    else:
        raise AssertionError("expected ProviderError")
    assert calls["n"] == 1


def test_cancel_skips_retry() -> None:
    flag = CancellationFlag()
    flag.cancel()

    def operation() -> str:
        raise ProviderError("timeout", "temp", retryable=True)

    try:
        call_with_retry(operation, cancellation=flag, max_attempts=3, backoff_seconds=0)
    except CancelledError:
        return
    raise AssertionError("expected CancelledError")
