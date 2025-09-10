import asyncio
from sqlalchemy import select
from storage.core.config import settings
from storage.core.db import async_session_maker
from storage.core.security import get_password_hash
from storage.db.models.user import User, UserRole


async def main():
    email = settings.ADMIN_EMAIL
    password = settings.ADMIN_PASSWORD
    department_id = (
        int(settings.ADMIN_DEPARTMENT_ID) if settings.ADMIN_DEPARTMENT_ID else None
    )

    async with async_session_maker() as session:
        q = await session.execute(select(User).where(User.email == email))
        user = q.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash(password)
            user.role = UserRole.ADMIN
            user.department_id = department_id
            user.is_active = True
        else:
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN,
                department_id=department_id,
                is_active=True,
            )
            session.add(user)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
