"""Server-side kill switches. UI hiding is not a control."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KillSwitch:
    tools_enabled: bool = True
    disabled_tools: frozenset[str] = frozenset()
    side_effecting_tools_enabled: bool = True
    llm_enabled: bool = True
    stt_enabled: bool = True
    tts_enabled: bool = True
    knowledge_enabled: bool = True

    def tool_allowed(self, name: str, *, side_effect_level: str) -> bool:
        if not self.tools_enabled:
            return False
        if name in self.disabled_tools:
            return False
        if not self.side_effecting_tools_enabled and side_effect_level != "none":
            return False
        return True


def parse_disabled_tools(raw: str) -> frozenset[str]:
    return frozenset(part.strip() for part in raw.split(",") if part.strip())
