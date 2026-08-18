"""In-process sliding-window rate limiter. Not shared across processes or replicas."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class InProcessRateLimiter:
    """Process-local limiter. Horizontal replicas each have their own counters."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, *, limit: int, window_seconds: float = 60.0) -> tuple[bool, int]:
        if limit <= 0:
            return True, 0
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = int(window_seconds - (now - bucket[0])) + 1
                return False, max(1, retry_after)
            bucket.append(now)
            return True, 0


def client_ip(host: str | None, *, forwarded: str | None, trust_proxy: bool) -> str:
    if trust_proxy and forwarded:
        first = forwarded.split(",")[0].strip()
        if first and len(first) <= 64:
            return first
    if host:
        return host[:64]
    return "unknown"
