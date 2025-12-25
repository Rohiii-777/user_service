from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create(self, token: PasswordResetToken) -> PasswordResetToken:
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def mark_used(self, token: PasswordResetToken) -> None:
        token.used = True
        await self.session.commit()
