import time

from pixel.shared.cancellation import CancellationFlag
from pixel.tools.registry import ToolRegistry
from pixel.tools.runner import execute_tool
from pixel.tools.types import AuthContext, ConfirmationState, NormalizedToolResult, ToolDefinition


def test_cancelled_turn_does_not_return_tool_result() -> None:
    registry = ToolRegistry()

    def _run(**_: object) -> NormalizedToolResult:
        return NormalizedToolResult(name="find_program", ok=True, status="ok", user_message="late")

    registry.register(
        ToolDefinition(
            name="find_program",
            description="t",
            version="1.0.0",
            permission="public",
            confirmation_policy="none",
            side_effect_level="none",
            timeout_seconds=1,
            input_fields={},
            required_fields=(),
            allowed_domains=(),
            audit=True,
            handler=_run,
        )
    )
    flag = CancellationFlag()
    flag.cancel()
    try:
        execute_tool(
            "find_program",
            {},
            registry=registry,
            auth=AuthContext(),
            confirmation=ConfirmationState(),
            cancellation=flag,
            timeout_seconds=1,
        )
    except Exception as exc:
        assert exc.__class__.__name__ == "CancelledError"
    else:
        raise AssertionError("expected cancel")


def test_tool_timeout_does_not_hang() -> None:
    registry = ToolRegistry()

    def _slow(arguments: dict[str, str], **_: object) -> NormalizedToolResult:
        time.sleep(2)
        return NormalizedToolResult(name="find_program", ok=True, status="ok", user_message="late")

    registry.register(
        ToolDefinition(
            name="find_program",
            description="t",
            version="1.0.0",
            permission="public",
            confirmation_policy="none",
            side_effect_level="none",
            timeout_seconds=0.2,
            input_fields={},
            required_fields=(),
            allowed_domains=(),
            audit=True,
            handler=_slow,
        )
    )
    result = execute_tool(
        "find_program",
        {},
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(),
        cancellation=CancellationFlag(),
        timeout_seconds=0.2,
    )
    assert result.status == "timeout"
    assert result.ok is False
