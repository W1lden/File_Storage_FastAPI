from pydantic import BaseModel, EmailStr

from storage.core.constants import TOKEN_TYPE


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = TOKEN_TYPE
