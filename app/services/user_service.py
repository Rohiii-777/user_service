import ulid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password,verify_password
from app.services.errors import UserAlreadyExists, UserNotFound,InvalidCredentials



class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
    ) -> User:
        if await self.repo.get_by_email(email):
            raise UserAlreadyExists("Email already registered")

        if await self.repo.get_by_username(username):
            raise UserAlreadyExists("Username already taken")

        user = User(
            id=str(ulid.ULID()),   # ✅ CORRECT
            email=email,
            username=username,
            hashed_password=hash_password(password),
        )

        return await self.repo.create(user)

    async def get_user(self, user_id: str) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        return user

    async def update(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_profile(
        self,
        user_id: str,
        username: str | None,
    ) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        if username:
            if await self.repo.get_by_username(username):
                raise UserAlreadyExists("Username already taken")

            user.username = username

        return await self.repo.update(user)



    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        if not verify_password(current_password, user.hashed_password):
            raise InvalidCredentials("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self.repo.update(user)


