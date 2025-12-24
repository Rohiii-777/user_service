from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
     decode_token,
       create_access_token
)
from app.repositories.user_repository import UserRepository
from app.services.errors import InvalidCredentials, InactiveUser,UserNotFound


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def login(self, email: str, password: str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user:
            raise InvalidCredentials()

        if not user.is_active:
            raise InactiveUser()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        user_id = decode_token(refresh_token, expected_type="refresh")

        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        if not user.is_active:
            raise InactiveUser()

        return {
            "access_token": create_access_token(user.id),
        }
