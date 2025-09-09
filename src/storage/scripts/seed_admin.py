import asyncio
from sqlalchemy import select
from storage.core.db import async_session_maker
from storage.core.security import get_password_hash
from storage.db.models.user import User, UserRole


async def main():
    async with async_session_maker() as session:
        q = await session.execute(select(User).where(User.email == "admin@example.com"))
        user = q.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash("admin123")
            user.role = UserRole.ADMIN
            user.is_active = True
        else:
            user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(user)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
