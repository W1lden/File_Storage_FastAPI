from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    department_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
