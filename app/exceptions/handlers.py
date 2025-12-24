from fastapi import Request
from fastapi.responses import JSONResponse

from app.schemas.common import ResponseSchema, ErrorSchema
from app.services.errors import ServiceError
from app.core.security import TokenPayloadError



def service_error_handler(_: Request, exc: ServiceError):
    return JSONResponse(
        status_code=400,
        content=ResponseSchema(
            success=False,
            data=None,
            error=ErrorSchema(
                code=exc.code,
                message=exc.message,
            ),
        ).model_dump(),
    )

def token_error_handler(_: Request, exc: TokenPayloadError):
    return JSONResponse(
        status_code=401,
        content=ResponseSchema(
            success=False,
            data=None,
            error=ErrorSchema(
                code="INVALID_TOKEN",
                message=str(exc),
            ),
        ).model_dump(),
    )

def permission_error_handler(_, exc: PermissionError):
    return JSONResponse(
        status_code=403,
        content=ResponseSchema(
            success=False,
            data=None,
            error=ErrorSchema(
                code="FORBIDDEN",
                message=str(exc),
            ),
        ).model_dump(),
    )
