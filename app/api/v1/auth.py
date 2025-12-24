from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dep
from app.schemas.auth import LoginRequest, TokenResponse,RefreshTokenRequest
from app.schemas.common import ResponseSchema
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=ResponseSchema[TokenResponse])
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(db_session_dep),
):
    service = AuthService(session)
    tokens = await service.login(payload.email, payload.password)

    return ResponseSchema(
        success=True,
        data=TokenResponse(**tokens),
        error=None,
    )

@router.post(
    "/auth/refresh",
    response_model=ResponseSchema[dict],
)
async def refresh_token(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(db_session_dep),
):
    service = AuthService(session)
    token_data = await service.refresh_access_token(payload.refresh_token)

    return ResponseSchema(
        success=True,
        data=token_data,
        error=None,
    )
