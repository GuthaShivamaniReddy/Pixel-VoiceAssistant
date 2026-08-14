from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from pixel.shared.cancellation import CancellationFlag

CancellationToken = CancellationFlag


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LlmRequest:
    system: str
    messages: tuple[ChatMessage, ...]
    policy_version: str = ""
    response_constraints: str = ""
    metadata: tuple[tuple[str, str], ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class LlmEvent:
    text: str
    done: bool


@runtime_checkable
class LLMProvider(Protocol):
    provider_id: str

    def generate(
        self, request: LlmRequest, *, cancellation: CancellationFlag
    ) -> Iterator[LlmEvent]: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    provider_id: str
    model_id: str
    dimensions: int

    def embed_documents(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...

    def embed_query(self, text: str) -> Sequence[float]: ...


__all__ = [
    "CancellationFlag",
    "CancellationToken",
    "ChatMessage",
    "EmbeddingProvider",
    "LLMProvider",
    "LlmEvent",
    "LlmRequest",
]
