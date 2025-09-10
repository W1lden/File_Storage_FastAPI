from pydantic import BaseModel, EmailStr
from storage.db.models.user import UserRole


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str | None = None
    department_id: int | None = None
    is_active: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole | None = UserRole.USER
    department_id: int | None = None
    is_active: bool = True


class UpdateUserRole(BaseModel):
    role: UserRole
