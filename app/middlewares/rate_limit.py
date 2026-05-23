import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


# Simple in-process sliding-window counter.
# For multi-worker deployments swap this for Redis.
_request_log: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT_REQUESTS = 60    # max requests …
RATE_LIMIT_WINDOW   = 60    # … per N seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP rate limiter.
    Skips /api/v1/ health probe and static routes.
    """

    async def dispatch(self, request: Request, call_next):
        # Only limit API calls
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = (
            request.headers.get("X-Forwarded-For", "")
            .split(",")[0]
            .strip()
            or (request.client.host if request.client else "unknown")
        )

        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW

        # Prune old timestamps
        _request_log[client_ip] = [
            t for t in _request_log[client_ip]
            if t > window_start
        ]

        if len(_request_log[client_ip]) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down."
            )

        _request_log[client_ip].append(now)
        return await call_next(request)
