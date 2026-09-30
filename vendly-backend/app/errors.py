"""
Implements the shared error shape from Backend Spec section 5:
  {"error": {"code": "...", "message": "...", "fields": {...}}}
Register install_error_handlers(app) once in main.py.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    code = "INTERNAL"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str, fields: dict | None = None):
        self.message = message
        self.fields = fields
        super().__init__(message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = status.HTTP_409_CONFLICT


class WhatsAppSendFailedError(AppError):
    code = "WHATSAPP_SEND_FAILED"
    status_code = status.HTTP_502_BAD_GATEWAY


class PaymentFailedError(AppError):
    code = "PAYMENT_FAILED"
    status_code = status.HTTP_502_BAD_GATEWAY


def _error_body(code: str, message: str, fields: dict | None = None) -> dict:
    body: dict[str, object] = {"code": code, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.fields),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        fields = {}
        for err in exc.errors():
            # ('body', 'vendors', 2, 'phone') -> "vendors.2.phone"
            loc = [str(p) for p in err["loc"] if p != "body"]
            fields[".".join(loc)] = err["msg"]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("VALIDATION_ERROR", "Check the highlighted fields", fields),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("INTERNAL", "Something went wrong"),
        )
