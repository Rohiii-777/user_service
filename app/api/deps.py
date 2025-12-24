from typing import AsyncGenerator

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, TokenPayloadError
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.errors import UserNotFound, InactiveUser
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def db_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session),
):
    token = credentials.credentials  # <-- raw JWT

    user_id = decode_token(token, expected_type="access")

    # # repo = UserRepository(session)
    # # user = await repo.get_by_id(user_id)

    # if not user:
    #     raise UserNotFound()

    # if not user.is_active:
    #     raise InactiveUser()

    # return user
    return user_id

async def require_admin(
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_dep),
):
    repo = UserRepository(session)
    user = await repo.get_by_id(current_user_id)

    if not user or not user.is_active:
        raise InactiveUser()

    if not user.is_admin:
        raise PermissionError("Admin access required")

    return user