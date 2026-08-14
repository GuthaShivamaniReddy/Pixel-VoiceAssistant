"""Normalized provider failures. Adapters raise this; orchestrator maps it for users."""

from __future__ import annotations

from pixel.domain import ProviderErrorCategory


class ProviderError(Exception):
    def __init__(
        self,
        category: ProviderErrorCategory | str,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        if isinstance(category, ProviderErrorCategory):
            self.category = category
        else:
            self.category = ProviderErrorCategory(category)
        self.message = message
        self.retryable = retryable


USER_ERROR_CODE = {
    ProviderErrorCategory.timeout: "timeout",
    ProviderErrorCategory.rate_limited: "timeout",
    ProviderErrorCategory.provider_unavailable: "network",
    ProviderErrorCategory.invalid_response: "response_failure",
    ProviderErrorCategory.authentication_error: "response_failure",
    ProviderErrorCategory.unknown: "response_failure",
    ProviderErrorCategory.cancelled: "cancelled",
}

USER_ERROR_MESSAGE = {
    "timeout": "That is taking too long. Try again, or use a shorter question.",
    "network": "I could not reach the assistant service. Try again or use text.",
    "response_failure": "I could not complete that reply. Try again, or ask another way.",
    "cancelled": "Turn cancelled.",
}


def user_facing(error: ProviderError) -> tuple[str, str]:
    code = USER_ERROR_CODE.get(error.category, "response_failure")
    return code, USER_ERROR_MESSAGE.get(code, USER_ERROR_MESSAGE["response_failure"])
