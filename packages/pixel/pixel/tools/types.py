"""Typed tool contracts. The model cannot invent or execute these."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Literal

from pixel.domain import Citation, RecommendedAction, SourceRef

Permission = Literal["public", "authenticated", "privileged"]
ConfirmationPolicy = Literal["none", "ui_click", "explicit"]
SideEffectLevel = Literal["none", "navigation", "write"]
ToolStatus = Literal[
    "ok",
    "invalid_input",
    "not_found",
    "unauthorized",
    "confirmation_required",
    "timeout",
    "unavailable",
    "invalid_destination",
    "cancelled",
    "unknown_tool",
    "internal_error",
]


@dataclass(frozen=True)
class SourceOffer:
    source_id: str
    title: str
    url: str


@dataclass(frozen=True)
class AuthContext:
    permission: Permission = "public"
    session_id: str = ""
    turn_id: str = ""
    correlation_id: str = ""


@dataclass(frozen=True)
class ConfirmationState:
    required: bool = False
    confirmed: bool = False
    confirmed_tool: str | None = None


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    version: str
    permission: Permission
    confirmation_policy: ConfirmationPolicy
    side_effect_level: SideEffectLevel
    timeout_seconds: float
    input_fields: Mapping[str, str]
    required_fields: tuple[str, ...]
    allowed_domains: tuple[str, ...]
    audit: bool
    handler: Callable[..., object]


@dataclass(frozen=True)
class NormalizedToolResult:
    name: str
    ok: bool
    status: ToolStatus
    user_message: str
    detail: str = ""
    error_code: str | None = None
    sources: tuple[SourceRef, ...] = ()
    actions: tuple[RecommendedAction, ...] = ()
    citations: tuple[Citation, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
