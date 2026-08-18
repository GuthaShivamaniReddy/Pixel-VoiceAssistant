from pixel.shared.cancellation import CancellationFlag
from pixel.tools.handlers import navigate_to_url
from pixel.tools.registry import ToolRegistry, production_registry
from pixel.tools.runner import execute_tool
from pixel.tools.types import AuthContext, ConfirmationState, ToolDefinition


def test_navigate_approved_source_id() -> None:
    result = navigate_to_url({"source_id": "cf-firstline"})
    assert result.ok is True
    assert result.actions[0].href.startswith("https://cyberflorida.org/firstline")


def test_navigate_attacker_denied() -> None:
    result = navigate_to_url({"url": "https://attacker.example/"})
    assert result.ok is False
    assert result.status == "invalid_destination"
    assert result.actions == ()


def test_unknown_tool_name() -> None:
    for name in ("run_shell_command", "delete_database", "http_request", "admin_override"):
        result = execute_tool(
            name,
            {},
            registry=production_registry(),
            auth=AuthContext(),
            confirmation=ConfirmationState(),
            cancellation=CancellationFlag(),
            timeout_seconds=1,
        )
        assert result.status == "unknown_tool"
        assert result.ok is False


def test_privileged_tool_denied_for_public() -> None:
    registry = ToolRegistry()

    def _boom(**_: object) -> None:
        raise AssertionError("must not run")

    registry.register(
        ToolDefinition(
            name="admin_reindex",
            description="privileged",
            version="1.0.0",
            permission="privileged",
            confirmation_policy="explicit",
            side_effect_level="write",
            timeout_seconds=1,
            input_fields={},
            required_fields=(),
            allowed_domains=(),
            audit=True,
            handler=_boom,
        )
    )
    result = execute_tool(
        "admin_reindex",
        {},
        registry=registry,
        auth=AuthContext(permission="public"),
        confirmation=ConfirmationState(
            required=True, confirmed=True, confirmed_tool="admin_reindex"
        ),
        cancellation=CancellationFlag(),
        timeout_seconds=1,
    )
    assert result.status == "unauthorized"


def test_explicit_confirmation_required_and_bound_to_tool() -> None:
    registry = ToolRegistry()
    ran = {"value": False}

    def _run(arguments: dict[str, str], **_: object) -> object:
        from pixel.tools.types import NormalizedToolResult

        ran["value"] = True
        return NormalizedToolResult(
            name="side_effect_demo",
            ok=True,
            status="ok",
            user_message="done",
        )

    registry.register(
        ToolDefinition(
            name="side_effect_demo",
            description="test only",
            version="1.0.0",
            permission="public",
            confirmation_policy="explicit",
            side_effect_level="write",
            timeout_seconds=1,
            input_fields={},
            required_fields=(),
            allowed_domains=(),
            audit=True,
            handler=_run,
        )
    )
    denied = execute_tool(
        "side_effect_demo",
        {},
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(required=True, confirmed=False),
        cancellation=CancellationFlag(),
        timeout_seconds=1,
    )
    assert denied.status == "confirmation_required"
    assert ran["value"] is False
    wrong = execute_tool(
        "side_effect_demo",
        {},
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(
            required=True, confirmed=True, confirmed_tool="navigate_to_url"
        ),
        cancellation=CancellationFlag(),
        timeout_seconds=1,
    )
    assert wrong.status == "confirmation_required"
    allowed = execute_tool(
        "side_effect_demo",
        {},
        registry=registry,
        auth=AuthContext(),
        confirmation=ConfirmationState(
            required=True, confirmed=True, confirmed_tool="side_effect_demo"
        ),
        cancellation=CancellationFlag(),
        timeout_seconds=1,
    )
    assert allowed.ok is True
    assert ran["value"] is True
