"""Small in-memory request protections for the single-process MVP."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request

from app.config import (
    AI_EXPLANATION_RATE_LIMIT_MAX_REQUESTS,
    AI_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS,
    RATE_LIMIT_MAX_REQUESTS,
    RATE_LIMIT_WINDOW_SECONDS,
)


class RequestRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        now = monotonic() if now is None else now
        with self.lock:
            timestamps = self.requests[key]
            cutoff = now - self.window_seconds
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.max_requests:
                return False
            timestamps.append(now)
            return True


rate_limiter = RequestRateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
ai_explanation_limiter = RequestRateLimiter(
    AI_EXPLANATION_RATE_LIMIT_MAX_REQUESTS,
    AI_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS,
)


def enforce_request_rate_limit(request: Request) -> None:
    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)
    client_host = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(f"{client_host}:{route_path}"):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again shortly.",
            headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
        )


def enforce_ai_explanation_rate_limit(request: Request) -> None:
    """Apply a stricter limit before a request can incur AI API cost."""
    client_host = request.client.host if request.client else "unknown"
    if not ai_explanation_limiter.allow(f"{client_host}:ai_explanation"):
        raise HTTPException(
            status_code=429,
            detail="AI explanations are limited to two per hour. Please try again later.",
            headers={"Retry-After": str(AI_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS)},
        )
