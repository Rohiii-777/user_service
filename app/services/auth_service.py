from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from uuid import uuid4
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
     decode_token,
       create_access_token,
       hash_refresh_token,hash_password
)
from app.repositories.user_repository import UserRepository
from app.services.errors import InvalidCredentials, InactiveUser,UserNotFound,Unauthorized
from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.core.config import get_settings
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.models.password_reset_token import PasswordResetToken


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def login(self, email: str, password: str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise InactiveUser()

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        settings = get_settings()
        seconds = settings.REFRESH_TOKEN_EXPIRE_SECONDS

        # ---- persist refresh token ----
        repo = RefreshTokenRepository(self.session)

        token_hash = hash_refresh_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(
            seconds=seconds
        )

        token_record = RefreshToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        await repo.create(token_record)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


    async def refresh_access_token(self, refresh_token: str) -> dict:
        # 1. decode + validate token type
        user_id = decode_token(refresh_token, expected_type="refresh")

        # 2. lookup refresh token in DB
        token_hash = hash_refresh_token(refresh_token)
        repo = RefreshTokenRepository(self.session)

        token_record = await repo.get_by_hash(token_hash)

        if not token_record:
            raise Unauthorized("Invalid refresh token")

        if token_record.is_revoked:
            raise Unauthorized("Refresh token revoked")

        if token_record.expires_at < datetime.utcnow():
            raise Unauthorized("Refresh token expired")

        # 3. ensure user still valid
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        if not user.is_active:
            raise InactiveUser()

        # 4. issue new access token
        return {
            "access_token": create_access_token(user.id),
        }



    async def logout(self, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        repo = RefreshTokenRepository(self.session)

        token_record = await repo.get_by_hash(token_hash)

        if not token_record:
            raise Unauthorized("Invalid refresh token")

        if token_record.is_revoked:
            return  # idempotent logout

        token_record.is_revoked = True
        await self.session.commit()

    async def forgot_password(self, email: str) -> str | None:
        user = await self.repo.get_by_email(email)

        # Always return success to avoid user enumeration
        if not user or not user.is_active:
            return None

        repo = PasswordResetTokenRepository(self.session)
        settings = get_settings()
        seconds = settings.REFRESH_TOKEN_EXPIRE_SECONDS
        raw_token = str(uuid4())
        token_hash = hash_refresh_token(raw_token)

        expires_at = datetime.utcnow() + timedelta(
            seconds=seconds
        )

        token_record = PasswordResetToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        await repo.create(token_record)
        return raw_token

    async def reset_password(self, reset_token: str, new_password: str) -> None:
        token_hash = hash_refresh_token(reset_token)
        reset_repo = PasswordResetTokenRepository(self.session)

        token_record = await reset_repo.get_by_hash(token_hash)

        if not token_record:
            raise Unauthorized("Invalid reset token")

        if token_record.used:
            raise Unauthorized("Reset token already used")

        if token_record.expires_at < datetime.utcnow():
            raise Unauthorized("Reset token expired")

        # load user
        user = await self.repo.get_by_id(token_record.user_id)
        if not user:
            raise Unauthorized("Invalid reset token")

        # update password
        user.hashed_password = hash_password(new_password)

        # invalidate all refresh tokens
        refresh_repo = RefreshTokenRepository(self.session)
        await refresh_repo.revoke_all_for_user(user.id)

        # mark reset token used
        token_record.used = True

        await self.session.commit()
