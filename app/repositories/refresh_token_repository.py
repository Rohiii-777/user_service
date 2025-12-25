from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def revoke(self, token: RefreshToken) -> None:
        token.is_revoked = True
        await self.session.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()