from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str | None = None
    department_id: int | None = None
    is_active: bool

    class Config:
        from_attributes = True
