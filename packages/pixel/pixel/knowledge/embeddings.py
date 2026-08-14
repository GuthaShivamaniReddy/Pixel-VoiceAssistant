"""Embedding adapters. Vendor HTTP stays here, not in ingestion."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence

import httpx

from pixel.providers.errors import ProviderError

_TOKEN = re.compile(r"[a-z0-9]+")
TOKEN = _TOKEN
OPENAI_API = "https://api.openai.com/v1"
DEFAULT_DIMENSIONS = 1536


def _normalize(vector: list[float]) -> tuple[float, ...]:
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return tuple(value / norm for value in vector)


class HashEmbeddingProvider:
    """Deterministic lexical embedding for tests and local mock mode."""

    provider_id = "mock"
    model_id = "hash-bow-v1"
    dimensions = DEFAULT_DIMENSIONS

    def embed_documents(self, texts: Sequence[str]) -> Sequence[tuple[float, ...]]:
        return tuple(self.embed_query(text) for text in texts)

    def embed_query(self, text: str) -> tuple[float, ...]:
        vector = [0.0] * self.dimensions
        tokens = _TOKEN.findall(text.lower())
        if not tokens:
            raise ProviderError("invalid_response", "Cannot embed empty text.")
        for token in tokens:
            bucket = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % self.dimensions
            vector[bucket] += 1.0
        return _normalize(vector)


class OpenAIEmbeddingProvider:
    provider_id = "openai"
    model_id = "text-embedding-3-small"
    dimensions = DEFAULT_DIMENSIONS

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "text-embedding-3-small",
        dimensions: int = DEFAULT_DIMENSIONS,
        timeout_seconds: float = 20,
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self.model_id = model
        self.dimensions = dimensions
        self._timeout = timeout_seconds
        self._client = client

    def embed_documents(self, texts: Sequence[str]) -> Sequence[tuple[float, ...]]:
        if not texts:
            return ()
        return self._embed(list(texts))

    def embed_query(self, text: str) -> tuple[float, ...]:
        return self._embed([text])[0]

    def _embed(self, texts: list[str]) -> tuple[tuple[float, ...], ...]:
        if any(not item.strip() for item in texts):
            raise ProviderError("invalid_response", "Cannot embed empty text.")
        if not self._api_key:
            raise ProviderError("authentication_error", "Embeddings are not configured.")
        client = self._client or httpx.Client(timeout=self._timeout)
        close = self._client is None
        try:
            response = client.post(
                f"{OPENAI_API}/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self.model_id, "input": texts, "dimensions": self.dimensions},
            )
        except httpx.TimeoutException as exc:
            raise ProviderError("timeout", "Embedding timed out.", retryable=True) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(
                "provider_unavailable", "Embedding failed.", retryable=True
            ) from exc
        finally:
            if close:
                client.close()
        if response.status_code in {401, 403}:
            raise ProviderError("authentication_error", "Embedding failed.")
        if response.status_code >= 400:
            raise ProviderError("unknown", "Embedding failed.")
        try:
            payload = response.json()
            items = sorted(payload["data"], key=lambda row: int(row["index"]))
            vectors = []
            for item in items:
                raw = [float(value) for value in item["embedding"]]
                if len(raw) != self.dimensions:
                    raise ProviderError("invalid_response", "Embedding failed.")
                vectors.append(_normalize(raw))
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderError("invalid_response", "Embedding failed.") from exc
        return tuple(vectors)


def cosine(left: Sequence[float], right: Sequence[float]) -> float:
    return float(sum(a * b for a, b in zip(left, right, strict=True)))
