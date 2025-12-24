from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dep
from app.schemas.user import UserCreate, UserRead,UserUpdate, ChangePasswordRequest
from app.schemas.common import ResponseSchema
from app.services.user_service import UserService
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.errors import UserNotFound

router = APIRouter(tags=["users"])


@router.post(
    "/users",
    response_model=ResponseSchema[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: UserCreate,
    session: AsyncSession = Depends(db_session_dep),
):
    service = UserService(session)
    user = await service.register_user(
        email=payload.email,
        username=payload.username,
        password=payload.password,
    )

    return ResponseSchema(
        success=True,
        data=UserRead.model_validate(user),
        error=None,
    )

@router.get(
    "/users/me",
    response_model=ResponseSchema[UserRead],
)
async def get_me(
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_dep),
):
    service = UserService(session)
    user = await service.get_user(current_user_id)

    return ResponseSchema(
        success=True,
        data=UserRead.model_validate(user),
        error=None,
    )


@router.patch(
    "/users/me",
    response_model=ResponseSchema[UserRead],
)
async def update_me(
    payload: UserUpdate,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_dep),
):
    service = UserService(session)
    user = await service.update_profile(
        user_id=current_user,
        username=payload.username,
    )

    return ResponseSchema(
        success=True,
        data=UserRead.model_validate(user),
        error=None,
    )

@router.post(
    "/users/me/change-password",
    response_model=ResponseSchema[None],
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_dep),
):
    service = UserService(session)
    await service.change_password(
        user_id=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )

    return ResponseSchema(
        success=True,
        data=None,
        error=None,
    )

@router.get(
    "/admin/users",
    response_model=ResponseSchema[list[UserRead]],
)
async def list_users(
    limit: int = 50,
    offset: int = 0,
    admin_user=Depends(require_admin),
    session: AsyncSession = Depends(db_session_dep),
):
    repo = UserRepository(session)
    users = await repo.list_users(limit=limit, offset=offset)

    return ResponseSchema(
        success=True,
        data=[UserRead.model_validate(u) for u in users],
        error=None,
    )

@router.patch(
    "/admin/users/{user_id}/deactivate",
    response_model=ResponseSchema[None],
)
async def deactivate_user(
    user_id: str,
    admin_user=Depends(require_admin),
    session: AsyncSession = Depends(db_session_dep),
):
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise UserNotFound()

    user.is_active = False
    await repo.update(user)

    return ResponseSchema(success=True, data=None, error=None)

@router.patch(
    "/admin/users/{user_id}/deactivate",
    response_model=ResponseSchema[None],
)
async def deactivate_user(
    user_id: str,
    admin_user=Depends(require_admin),
    session: AsyncSession = Depends(db_session_dep),
):
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise UserNotFound()

    user.is_active = False
    await repo.update(user)

    return ResponseSchema(success=True, data=None, error=None)
