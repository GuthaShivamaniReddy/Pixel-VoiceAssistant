"""Execute only registered tools after server-side checks."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from time import perf_counter

from pixel.knowledge import Retriever
from pixel.security.kill_switch import KillSwitch
from pixel.shared.cancellation import CancellationFlag, CancelledError
from pixel.tools.policy import confirmation_satisfied, permission_allows
from pixel.tools.registry import ToolRegistry, ToolRegistryError
from pixel.tools.types import (
    AuthContext,
    ConfirmationState,
    NormalizedToolResult,
    SourceOffer,
)
from pixel.tools.validate import validate_arguments

log = logging.getLogger("pixel.tools")


def execute_tool(
    name: str,
    arguments: Mapping[str, object],
    *,
    registry: ToolRegistry,
    auth: AuthContext,
    confirmation: ConfirmationState,
    cancellation: CancellationFlag,
    timeout_seconds: float,
    retriever: Retriever | None = None,
    last_offers: tuple[SourceOffer, ...] = (),
    kill_switch: KillSwitch | None = None,
) -> NormalizedToolResult:
    started = perf_counter()
    if cancellation.is_cancelled():
        raise CancelledError
    try:
        definition = registry.require(name)
    except ToolRegistryError:
        _audit(name, auth, "unknown_tool", started, authorized=False, confirmed=False)
        return NormalizedToolResult(
            name=name,
            ok=False,
            status="unknown_tool",
            user_message="That action is not available.",
            error_code="unknown_tool",
        )
    switch = kill_switch or KillSwitch()
    if not switch.tool_allowed(definition.name, side_effect_level=definition.side_effect_level):
        _audit(definition.name, auth, "unavailable", started, authorized=False, confirmed=False)
        return NormalizedToolResult(
            name=definition.name,
            ok=False,
            status="unavailable",
            user_message="That action is temporarily disabled.",
            error_code="unavailable",
        )
    if not permission_allows(auth, definition.permission):
        _audit(definition.name, auth, "unauthorized", started, authorized=False, confirmed=False)
        return NormalizedToolResult(
            name=definition.name,
            ok=False,
            status="unauthorized",
            user_message="You are not allowed to use that action.",
            error_code="unauthorized",
        )
    if not confirmation_satisfied(definition, confirmation):
        _audit(
            definition.name,
            auth,
            "confirmation_required",
            started,
            authorized=True,
            confirmed=False,
        )
        return NormalizedToolResult(
            name=definition.name,
            ok=False,
            status="confirmation_required",
            user_message="I need you to confirm that action before I continue.",
            error_code="confirmation_required",
        )
    try:
        cleaned = validate_arguments(
            arguments,
            allowed=definition.input_fields,
            required=definition.required_fields,
        )
    except ValueError:
        _audit(definition.name, auth, "invalid_input", started, authorized=True, confirmed=True)
        return NormalizedToolResult(
            name=definition.name,
            ok=False,
            status="invalid_input",
            user_message="That request was not valid, so I did not run it.",
            error_code="invalid_input",
        )
    timeout = min(timeout_seconds, definition.timeout_seconds)

    def _call() -> NormalizedToolResult:
        result = definition.handler(
            cleaned,
            retriever=retriever,
            last_offers=last_offers,
            auth=auth,
        )
        if not isinstance(result, NormalizedToolResult):
            return NormalizedToolResult(
                name=definition.name,
                ok=False,
                status="internal_error",
                user_message="That action could not be completed.",
                error_code="internal_error",
            )
        return result

    pool = ThreadPoolExecutor(max_workers=1)
    try:
        future = pool.submit(_call)
        result = future.result(timeout=timeout)
    except FuturesTimeout:
        _audit(definition.name, auth, "timeout", started, authorized=True, confirmed=True)
        return NormalizedToolResult(
            name=definition.name,
            ok=False,
            status="timeout",
            user_message="That lookup took too long. Please try again.",
            error_code="timeout",
        )
    except CancelledError:
        raise
    except Exception:
        log.exception("tool_internal tool=%s", definition.name)
        _audit(definition.name, auth, "internal_error", started, authorized=True, confirmed=True)
        return NormalizedToolResult(
            name=definition.name,
            ok=False,
            status="internal_error",
            user_message="That action could not be completed.",
            error_code="internal_error",
        )
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    if cancellation.is_cancelled():
        raise CancelledError
    duration_ms = int((perf_counter() - started) * 1000)
    _audit(
        definition.name,
        auth,
        result.status,
        started,
        authorized=True,
        confirmed=True,
        duration_ms=duration_ms,
    )
    return result


def _audit(
    name: str,
    auth: AuthContext,
    status: str,
    started: float,
    *,
    authorized: bool,
    confirmed: bool,
    duration_ms: int | None = None,
) -> None:
    elapsed = duration_ms if duration_ms is not None else int((perf_counter() - started) * 1000)
    log.info(
        "tool_audit tool=%s status=%s authorized=%s confirmed=%s "
        "duration_ms=%s session=%s turn=%s correlation=%s",
        name,
        status,
        authorized,
        confirmed,
        elapsed,
        auth.session_id,
        auth.turn_id,
        auth.correlation_id,
    )
