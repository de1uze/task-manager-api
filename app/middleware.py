import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging_setup import request_id_ctx

logger = logging.getLogger("task-manager.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID and log one structured line per request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        token = request_id_ctx.set(rid)
        start = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception(
                    "request failed method=%s path=%s",
                    request.method,
                    request.url.path,
                )
                raise
            elapsed_ms = (time.perf_counter() - start) * 1000
            response.headers["x-request-id"] = rid
            logger.info(
                "%s %s -> %d in %.1fms",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
            return response
        finally:
            request_id_ctx.reset(token)
