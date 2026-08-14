"""Bounded in-memory conversation sessions. Not long-term memory."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from pixel.ai import ChatMessage
from pixel.domain import (
    InputMode,
    Intent,
    Message,
    MessageRole,
    SessionCapabilities,
    Turn,
    TurnStatus,
    utcnow,
)
from pixel.orchestrator.policy import POLICY_VERSION
from pixel.shared.cancellation import CancellationFlag

MAX_MESSAGES = 8
MAX_SESSIONS = 500
DEFAULT_TTL_SECONDS = 1800


class SessionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class ActiveTurn:
    turn_id: str
    generation: int
    cancellation: CancellationFlag
    input_mode: InputMode = InputMode.text
    pcm: bytearray = field(default_factory=bytearray)
    sample_rate: int = 16000


@dataclass
class ConversationSession:
    id: str
    created_at: datetime
    expires_at: datetime
    ttl: timedelta
    capabilities: SessionCapabilities = field(default_factory=SessionCapabilities)
    messages: list[Message] = field(default_factory=list)
    last_intent: Intent | None = None
    generation: int = 0
    active: ActiveTurn | None = None
    policy_version: str = POLICY_VERSION

    def is_expired(self, now: datetime | None = None) -> bool:
        moment = now or utcnow()
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=UTC)
        return moment >= self.expires_at

    def touch(self) -> None:
        self.expires_at = utcnow() + self.ttl

    def history_tuple(self) -> tuple[ChatMessage, ...]:
        return tuple(
            ChatMessage(role=message.role.value, content=message.content)
            for message in self.messages
            if message.role in {MessageRole.user, MessageRole.assistant}
        )

    def clear_context(self) -> None:
        self.messages.clear()
        self.last_intent = None
        self.touch()

    def commit_turn(
        self,
        *,
        generation: int,
        turn_id: str,
        user_text: str,
        assistant_text: str,
        intent: Intent | None,
    ) -> bool:
        if generation != self.generation:
            return False
        if self.active is not None and self.active.turn_id != turn_id:
            return False
        self.messages.append(
            Message(
                id=str(uuid4()),
                session_id=self.id,
                turn_id=turn_id,
                role=MessageRole.user,
                content=user_text,
            )
        )
        self.messages.append(
            Message(
                id=str(uuid4()),
                session_id=self.id,
                turn_id=turn_id,
                role=MessageRole.assistant,
                content=assistant_text,
            )
        )
        if len(self.messages) > MAX_MESSAGES:
            self.messages = self.messages[-MAX_MESSAGES:]
        self.last_intent = intent
        self.touch()
        return True


class SessionStore:
    def __init__(self, *, ttl_seconds: float = DEFAULT_TTL_SECONDS) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self._sessions: dict[str, ConversationSession] = {}

    def create(self) -> ConversationSession:
        self.prune()
        if len(self._sessions) >= MAX_SESSIONS:
            self.prune(force=True)
        session = ConversationSession(
            id=str(uuid4()),
            created_at=utcnow(),
            expires_at=utcnow() + self.ttl,
            ttl=self.ttl,
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> ConversationSession:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionError("unknown_session", "That conversation was not found. Start again.")
        if session.is_expired():
            self._sessions.pop(session_id, None)
            raise SessionError("session_expired", "That conversation expired. Start again.")
        return session

    def get_or_create(self, session_id: str | None) -> ConversationSession:
        if not session_id:
            return self.create()
        return self.get(session_id)

    def clear(self, session_id: str) -> ConversationSession:
        session = self.get(session_id)
        if session.active is not None:
            session.active.cancellation.cancel()
            session.active = None
        session.generation += 1
        session.clear_context()
        return session

    def prune(self, *, force: bool = False) -> None:
        expired = [key for key, session in self._sessions.items() if session.is_expired()]
        for key in expired:
            self._sessions.pop(key, None)
        if force and len(self._sessions) >= MAX_SESSIONS:
            oldest = sorted(self._sessions.values(), key=lambda item: item.expires_at)
            for session in oldest[: max(1, len(oldest) // 5)]:
                self._sessions.pop(session.id, None)

    def begin_turn(
        self,
        session: ConversationSession,
        turn_id: str,
        *,
        input_mode: InputMode,
        sample_rate: int = 16000,
    ) -> ActiveTurn:
        if session.active is not None and session.active.turn_id != turn_id:
            session.active.cancellation.cancel()
        session.generation += 1
        active = ActiveTurn(
            turn_id=turn_id,
            generation=session.generation,
            cancellation=CancellationFlag(),
            input_mode=input_mode,
            sample_rate=sample_rate if sample_rate > 0 else 16000,
        )
        session.active = active
        session.touch()
        return active

    def cancel_turn(self, session: ConversationSession, turn_id: str) -> None:
        active = session.active
        if active is None or active.turn_id != turn_id:
            return
        active.cancellation.cancel()
        session.active = None

    def take_turn(self, session: ConversationSession, turn_id: str) -> ActiveTurn | None:
        active = session.active
        if active is None or active.turn_id != turn_id:
            return None
        session.active = None
        return active


def new_turn(session: ConversationSession, turn_id: str, input_mode: InputMode) -> Turn:
    return Turn(
        id=turn_id,
        session_id=session.id,
        input_mode=input_mode,
        status=TurnStatus.processing,
        started_at=utcnow(),
        generation=session.generation,
    )
