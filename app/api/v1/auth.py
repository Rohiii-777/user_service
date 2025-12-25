from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dep
from app.schemas.auth import LoginRequest, TokenResponse,RefreshTokenRequest,LogoutRequest,ForgotPasswordRequest,ForgotPasswordResponse,ResetPasswordRequest
from app.schemas.common import ResponseSchema
from app.services.auth_service import AuthService
from app.services.errors import (
    InvalidCredentials,
    Unauthorized,
    InactiveUser,
    UserNotFound,
)

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
    try:
        token_data = await service.refresh_access_token(payload.refresh_token)
        return ResponseSchema(
            success=True,
            data=token_data,
            error=None,
        )

    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        )

@router.post(
    "/auth/logout",
    response_model=ResponseSchema[None],
)
async def logout(
    payload: LogoutRequest,
    session: AsyncSession = Depends(db_session_dep),
):
    service = AuthService(session)
    try:
        await service.logout(payload.refresh_token)
        return ResponseSchema(
            success=True,
            data=None,
            error=None,
        )

    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        )

@router.post(
    "/auth/forgot-password",
    response_model=ResponseSchema[ForgotPasswordResponse],
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    session: AsyncSession = Depends(db_session_dep),
):
    service = AuthService(session)
    token = await service.forgot_password(payload.email)

    return ResponseSchema(
        success=True,
        data=ForgotPasswordResponse(reset_token=token),
        error=None,
    )


@router.post(
    "/auth/reset-password",
    response_model=ResponseSchema[None],
)
async def reset_password(
    payload: ResetPasswordRequest,
    session: AsyncSession = Depends(db_session_dep),
):
    service = AuthService(session)
    try:
        await service.reset_password(
            payload.reset_token,
            payload.new_password,
        )
        return ResponseSchema(
            success=True,
            data=None,
            error=None,
        )

    except Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        )
