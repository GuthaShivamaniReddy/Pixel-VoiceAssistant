"""Normalized conversation models shared by orchestrator, API, and adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal


class Intent(StrEnum):
    cyberflorida_knowledge = "cyberflorida_knowledge"
    cybersecurity_help = "cybersecurity_help"
    scam_help = "scam_help"
    navigation = "navigation"
    clarification = "clarification"
    unsupported = "unsupported"


class InputMode(StrEnum):
    text = "text"
    voice = "voice"


class TurnStatus(StrEnum):
    created = "created"
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"


class MessageRole(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ProviderErrorCategory(StrEnum):
    timeout = "timeout"
    rate_limited = "rate_limited"
    provider_unavailable = "provider_unavailable"
    invalid_response = "invalid_response"
    cancelled = "cancelled"
    authentication_error = "authentication_error"
    unknown = "unknown"


Provenance = Literal["none", "policy", "mock", "retrieval"]
ResponseStatus = Literal["ok", "fallback", "refused"]
SafetyState = Literal["ok", "refused", "abstained", "escalated"]


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class SourceRef:
    title: str
    name: str
    url: str
    description: str
    provenance: Provenance = "policy"


@dataclass(frozen=True)
class Citation:
    url: str
    title: str = ""
    quote: str = ""


@dataclass(frozen=True)
class RecommendedAction:
    id: str
    label: str
    href: str


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    name: str
    ok: bool
    detail: str = ""
    status: str = "ok"
    error_code: str | None = None


@dataclass(frozen=True)
class Message:
    id: str
    session_id: str
    turn_id: str
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class Turn:
    id: str
    session_id: str
    input_mode: InputMode
    status: TurnStatus = TurnStatus.created
    created_at: datetime = field(default_factory=utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    generation: int = 0
    error_code: str | None = None
    timings: dict[str, int | None] = field(default_factory=dict)


@dataclass(frozen=True)
class SessionCapabilities:
    text: bool = True
    voice: bool = True


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    confidence: float
    reason: str
    requires_retrieval: bool = False
    requires_tool: bool = False
    skip_model: bool = False


@dataclass(frozen=True)
class RetrievalDecision:
    required: bool
    executed: bool = False
    available: bool = False
    reason: str = "Phase 6 retrieval is not implemented"


@dataclass(frozen=True)
class ToolDecision:
    required: bool
    executed: bool = False
    name: str | None = None
    reason: str = "not_required"


@dataclass
class AssistantResponse:
    text: str
    sources: list[SourceRef] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    actions: list[RecommendedAction] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    status: ResponseStatus = "ok"
    safety_state: SafetyState = "ok"
    intent: Intent | None = None
    policy_version: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


def source_to_dict(source: SourceRef) -> dict[str, str]:
    return {
        "title": source.title,
        "name": source.name,
        "url": source.url,
        "description": source.description,
        "provenance": source.provenance,
    }


def action_to_dict(action: RecommendedAction) -> dict[str, str]:
    return {"id": action.id, "label": action.label, "href": action.href}


def citation_to_dict(citation: Citation) -> dict[str, str]:
    return {"url": citation.url, "title": citation.title, "quote": citation.quote}
