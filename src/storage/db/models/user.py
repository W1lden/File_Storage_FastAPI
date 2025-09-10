import enum
from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from storage.core.db import Base
from storage.core.constants import EMAIL_MAX_LENGTH, PASSWORD_HASH_MAX_LENGTH


class UserRole(str, enum.Enum):
    """Роли пользователей в системе."""

    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class User(Base):
    """Модель пользователя.

    Содержит данные об учётной записи, включая email,
    пароль (хэш), роль, принадлежность к отделу и статус активности.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LENGTH))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
