import asyncio
from sqlalchemy import select
from storage.core.db import async_session_maker
from storage.core.security import get_password_hash
from storage.db.models.user import User, UserRole
from storage.core.config import settings


async def main():
    async with async_session_maker() as session:
        q = await session.execute(
            select(User).where(User.email == settings["ADMIN_EMAIL"])
        )
        user = q.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash(
                settings["ADMIN_PASSWORD"]
            )
            user.role = UserRole.ADMIN
            user.is_active = True
        else:
            user = User(
                email=settings["ADMIN_EMAIL"],
                hashed_password=get_password_hash(settings["ADMIN_PASSWORD"]),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(user)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
