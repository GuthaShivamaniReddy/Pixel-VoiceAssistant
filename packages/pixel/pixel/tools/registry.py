"""Central registry. Unknown names never execute."""

from __future__ import annotations

from pixel.tools.types import ToolDefinition


class ToolRegistryError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ToolRegistryError("duplicate_tool", f"Tool already registered: {definition.name}")
        if not definition.name or not definition.name.replace("_", "").isalnum():
            raise ToolRegistryError("invalid_tool", "Tool name is invalid")
        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def require(self, name: str) -> ToolDefinition:
        item = self.get(name)
        if item is None:
            raise ToolRegistryError("unknown_tool", "That tool is not approved.")
        return item

    def names(self) -> frozenset[str]:
        return frozenset(self._tools)

    def definitions(self) -> tuple[ToolDefinition, ...]:
        return tuple(self._tools.values())


_PRODUCTION: ToolRegistry | None = None


def production_registry() -> ToolRegistry:
    global _PRODUCTION
    if _PRODUCTION is None:
        from pixel.tools.handlers import register_production_tools

        registry = ToolRegistry()
        register_production_tools(registry)
        _PRODUCTION = registry
    return _PRODUCTION
