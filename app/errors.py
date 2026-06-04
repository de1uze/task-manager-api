import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging_setup import request_id_ctx

logger = logging.getLogger("task-manager.errors")


def _envelope(status_code: int, message: str, details: object | None = None) -> dict:
    body: dict = {
        "error": {
            "code": status_code,
            "message": message,
            "request_id": request_id_ctx.get(),
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.status_code, str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_envelope(422, "validation failed", exc.errors()),
        )

    @app.exception_handler(Exception)
    async def _unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content=_envelope(500, "internal server error"),
        )
