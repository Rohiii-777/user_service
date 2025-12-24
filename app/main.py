from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.exceptions.handlers import service_error_handler,token_error_handler,permission_error_handler
from app.services.errors import ServiceError
from app.api.v1 import auth, users
from app.core.security import TokenPayloadError


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.debug)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(TokenPayloadError, token_error_handler)
    app.add_exception_handler(PermissionError, permission_error_handler)

    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(users.router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
