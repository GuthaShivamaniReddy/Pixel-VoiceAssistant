"""Bounded retries for transient provider failures only."""

from __future__ import annotations

from collections.abc import Callable
from time import sleep

from pixel.providers.errors import ProviderError
from pixel.shared.cancellation import CancellationFlag, CancelledError

DEFAULT_MAX_ATTEMPTS = 2
DEFAULT_BACKOFF_SECONDS = 0.2


def call_with_retry(
    operation: Callable[[], str],
    *,
    cancellation: CancellationFlag,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
) -> str:
    attempts = max(1, max_attempts)
    last_error: ProviderError | None = None
    for index in range(attempts):
        if cancellation.is_cancelled():
            raise CancelledError
        try:
            return operation()
        except ProviderError as exc:
            last_error = exc
            if cancellation.is_cancelled():
                raise CancelledError from exc
            retryable = exc.retryable and index < attempts - 1
            if not retryable:
                raise
            sleep(backoff_seconds * (2**index))
    assert last_error is not None
    raise last_error
