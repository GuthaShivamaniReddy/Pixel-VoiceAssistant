from pixel.tools.registry import ToolRegistry, ToolRegistryError, production_registry
from pixel.tools.types import ToolDefinition


def _definition(name: str) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description="test",
        version="1.0.0",
        permission="public",
        confirmation_policy="none",
        side_effect_level="none",
        timeout_seconds=1,
        input_fields={},
        required_fields=(),
        allowed_domains=("cyberflorida.org",),
        audit=True,
        handler=lambda **_: None,
    )


def test_production_registry_has_approved_tools() -> None:
    names = production_registry().names()
    assert names == {
        "find_program",
        "find_resource",
        "search_approved_content",
        "navigate_to_url",
    }
    for name in names:
        item = production_registry().require(name)
        assert item.input_fields is not None
        assert item.permission == "public"


def test_duplicate_registration_rejected() -> None:
    registry = ToolRegistry()
    registry.register(_definition("find_program"))
    try:
        registry.register(_definition("find_program"))
    except ToolRegistryError as exc:
        assert exc.code == "duplicate_tool"
    else:
        raise AssertionError("expected duplicate")


def test_unknown_tool_rejected() -> None:
    try:
        production_registry().require("run_shell_command")
    except ToolRegistryError as exc:
        assert exc.code == "unknown_tool"
    else:
        raise AssertionError("expected unknown")
