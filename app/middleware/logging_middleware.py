import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import (
    HEADER_REQUEST_ID,
    HEADER_TRACE_ID,
    LOG_REQUEST_COMPLETED,
    NS_PER_MS,
)

logger = structlog.stdlib.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        structlog.contextvars.clear_contextvars()

        trace_id = request.headers.get(HEADER_REQUEST_ID, str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            method=request.method,
            path=str(request.url.path),
        )

        start = time.perf_counter_ns()
        response = await call_next(request)
        duration_ms = (time.perf_counter_ns() - start) / NS_PER_MS

        logger.info(
            LOG_REQUEST_COMPLETED,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        response.headers[HEADER_TRACE_ID] = trace_id
        return response
