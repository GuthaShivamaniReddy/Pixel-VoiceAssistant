"""Approved tools. Implementations belong to Phase 7 — not here.

Phase 5 records a ToolDecision on the orchestrator. Nothing is executed.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPermission:
    name: str
    allowed: bool = False


__all__ = ["ToolPermission"]
